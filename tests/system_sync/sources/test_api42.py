"""Tests de `system_sync.sources.api42` (T4, cas N1 à N13 et L1 à L17 ; A15, A17, A23).

Contrat de T4.b (`from system_sync.sources import api42`, aucune fonction publique ne lève) :
- `API_BASE = "https://api.intra.42.fr"`.
- `authorization_url(client_id, port) -> (url, state)`.
- `CallbackServer(port, state, timeout)` : `start() -> str | None`, `address`, `wait()`.
- `RateLimiter(rate=2.0, clock=time.monotonic, sleep=time.sleep)` : `wait() -> None`.
- `Api42Client(api_base, *, timeout, limiter, sleep, max_retries, max_retry_after,
  max_pages, max_bytes)` : `exchange_code(client_id, client_secret, code, redirect_uri)
  -> str | None`, `fetch_me() -> Fetch`, `fetch_achievements() -> Fetch`.
- `read_api42(env, cache_path, *, open_browser, api_base, consent_timeout,
  request_timeout, clock, sleep) -> Api42Result`.
Détail dans la docstring de chaque classe de test. Pendant tout le module, `socket`
refuse tout hôte hors de 127.0.0.1 et les variables de proxy sont retirées.
"""

import ast
import dataclasses
import json
import math
import re
import socket
import tempfile
import time
import unittest
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from tests.system_sync.sources.fake_server import (
    FIXTURES,
    HOST,
    Browser,
    Capture,
    FakeClock,
    FakeServer,
    NetworkGuard,
    Reply,
    callback_url,
    free_port,
    get_status,
    in_thread,
    json_reply,
    load,
)

try:
    from system_sync.sources import api42
except ImportError:
    api42 = None  # chaque test échoue dans `setUp` tant que le module manque

TOKEN_PATH = "/oauth/token"
ME_PATH = "/v2/me"
ACHIEVEMENTS_PATH = "/v2/achievements"
CLIENT_ID = "fake-client-id"
CLIENT_SECRET = "fake-client-secret-0123456789"
CODE = "fake-authorization-code-0123"
TOKEN = load("token.json")["access_token"]
SECRETS = (CLIENT_SECRET, CODE, TOKEN)
VARIABLES = ("API42_CLIENT_ID", "API42_CLIENT_SECRET", "API42_CALLBACK_PORT")
PROJECT_KEYS = {"id", "slug", "name", "final_mark"}
ITEM_KEYS = {"id", "name", "description", "obtained", "obtained_on", "title"}
OBTAINED_IDS = {1, 2, 101}
VALIDATED_IDS = {1314, 1327}
# Valeurs de `me_personal_fields.json` qui ne doivent sortir nulle part (N7).
PERSONAL_MARKERS = (
    "personal-email@example.invalid",
    "personal-login",
    "PersonalFirstName",
    "PersonalLastName",
    "PersonalFullName",
    "PersonalDisplayName",
    "personal-phone-0000",
    "personal-location-host",
    "personal-pool-month",
    "personal-image.example.invalid",
    "999000111",
    "424242",
)
# Appels réseau qui doivent porter `timeout=` (N13) ; `open` compte sur un nom `*opener*`.
NETWORK_CALLS = {"urlopen", "HTTPConnection", "HTTPSConnection", "create_connection"}
TLS_BYPASS = re.compile(r"_create_unverified_context|CERT_NONE|check_hostname *= *False")
GUARD = NetworkGuard()


def setUpModule():
    """Garde le réseau pendant tout le module."""
    GUARD.start()


def tearDownModule():
    GUARD.stop()


def page(number):
    """Réponse JSON de la page `number` des achievements."""
    return json_reply(load(f"achievements_page{number}.json"))


def entropy_bits(state):
    """Entropie maximale d'un jeton URL-safe : longueur × log2 de l'alphabet."""
    if not re.fullmatch(r"[A-Za-z0-9_-]+", state):
        return 0
    alphabet = 16 if re.fullmatch(r"[0-9a-f]+", state) else 64
    return len(state) * math.log2(alphabet)


def written_text(root):
    """Concatène le texte de tous les fichiers sous `root`."""
    files = sorted(path for path in Path(root).rglob("*") if path.is_file())
    return "\n".join(path.read_bytes().decode("utf-8", "replace") for path in files)


class Guarded(unittest.TestCase):
    """Base : module présent, et aucune connexion hors 127.0.0.1 pendant le test."""

    def setUp(self):
        if api42 is None:
            self.fail("module system_sync.sources.api42 absent")
        GUARD.outside.clear()

    def tearDown(self):
        self.assertEqual(GUARD.outside, [], "connexion tentée hors de 127.0.0.1")


class AuthorizationUrlTest(Guarded):
    """`authorization_url(client_id, port) -> (url, state)`.

    `url` = `API_BASE + "/oauth/authorize?"` avec `client_id`, `redirect_uri`
    (`http://127.0.0.1:<port>/callback`, A15), `response_type=code` et `state` ; `state`
    vient de `secrets`, URL-safe, au moins 128 bits, nouveau à chaque appel.
    """

    def test_N1_url_parameters_and_fresh_state(self):
        url, state = api42.authorization_url(CLIENT_ID, 5615)
        parts = urlsplit(url)
        query = parse_qs(parts.query)
        self.assertEqual(api42.API_BASE, "https://api.intra.42.fr")
        self.assertEqual(
            f"{parts.scheme}://{parts.netloc}{parts.path}",
            api42.API_BASE + "/oauth/authorize",
        )
        self.assertEqual(query["client_id"], [CLIENT_ID])
        self.assertEqual(query["redirect_uri"], [f"http://{HOST}:5615/callback"])
        self.assertEqual(query["response_type"], ["code"])
        self.assertEqual(query["state"], [state])
        self.assertGreaterEqual(entropy_bits(state), 128, state)
        states = {api42.authorization_url(CLIENT_ID, 5615)[1] for _ in range(20)}
        self.assertEqual(len(states), 20)


class CallbackServerTest(Guarded):
    """`CallbackServer(port, state, timeout)`, journal de `http.server` coupé.

    `start() -> str | None` : lie 127.0.0.1:`port` ; erreur qui nomme le port s'il est
    pris, sans toucher à l'occupant. `address` : `getsockname()` après `start`.
    `wait() -> Callback` : sert jusqu'au premier retour `/callback` dont `state` est égal
    (comparé par `compare_digest`), ou jusqu'à `timeout` secondes réelles, puis ferme le
    port dans tous les cas. Un retour sans `state` ou avec un autre reçoit 400 et l'attente
    continue. Retour valide : 200. `Callback` (figé) : `code` (`str` ou `None`), `error`
    (`None` si `code`, sinon la cause : délai écoulé, ou l'`error` reçue, `access_denied`).
    """

    def serve(self, state, timeout, requests):
        """Sert `requests` depuis un fil ; rend (callback, statuts, durée de `wait`, port)."""
        port = free_port()
        server = api42.CallbackServer(port, state, timeout)
        self.assertIsNone(server.start())
        statuses = []
        thread = in_thread(
            lambda: statuses.extend(get_status(callback_url(port, **p)) for p in requests)
        )
        begin = time.monotonic()
        callback = server.wait()
        elapsed = time.monotonic() - begin
        thread.join(timeout=2)
        return callback, statuses, elapsed, port

    def test_N2_server_binds_loopback_on_given_port(self):
        port = free_port()
        server = api42.CallbackServer(port, "s" * 32, 0.2)
        self.assertIsNone(server.start())
        self.assertEqual(server.address, (HOST, port))
        self.assertIsNone(server.wait().code)

    def test_N11_server_closed_and_port_free_after_callback(self):
        state = "a" * 32
        callback, statuses, _, port = self.serve(state, 2.0, [{"code": CODE, "state": state}])
        self.assertEqual(callback.code, CODE)
        self.assertIsNone(callback.error)
        self.assertEqual(statuses, [200])
        with self.assertRaises(ConnectionRefusedError):
            socket.create_connection((HOST, port), timeout=0.2).close()
        with socket.socket() as probe:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            probe.bind((HOST, port))

    def test_L3_missing_or_wrong_state_gets_400(self):
        state = "b" * 32
        requests = [{"code": CODE, "state": "c" * 32}, {"code": CODE}]
        callback, statuses, _, _ = self.serve(state, 0.5, requests)
        self.assertEqual(statuses, [400, 400])
        self.assertIsNone(callback.code)
        self.assertTrue(callback.error)

    def test_L5_access_denied_ends_wait_without_code(self):
        state = "e" * 32
        requests = [{"error": "access_denied", "state": state}]
        callback, _, elapsed, _ = self.serve(state, 2.0, requests)
        self.assertIsNone(callback.code)
        self.assertIn("access_denied", callback.error)
        self.assertLess(elapsed, 1.5)

    def test_L16_busy_port_named_and_occupant_untouched(self):
        occupant = socket.socket()
        self.addCleanup(occupant.close)
        occupant.bind((HOST, 0))
        occupant.listen()
        port = occupant.getsockname()[1]
        error = api42.CallbackServer(port, "d" * 32, 0.2).start()
        self.assertIsNotNone(error)
        self.assertIn(str(port), error)
        self.assertEqual(occupant.getsockname(), (HOST, port))
        socket.create_connection((HOST, port), timeout=0.5).close()


class ClientTest(Guarded):
    """`Api42Client(api_base, *, timeout, limiter, sleep, max_retries, max_retry_after,
    max_pages, max_bytes)`, toutes les options ayant une valeur par défaut.

    `exchange_code(...) -> str | None` : POST de formulaire sur `/oauth/token` (rien dans
    l'URL) ; garde le jeton en mémoire et renvoie l'erreur, ou `None`. `fetch_me()` et
    `fetch_achievements()` (`?per_page=100&page=N` depuis 1, arrêt à la première page
    incomplète, au plus `max_pages` pages) renvoient `Fetch` (figé) : `data` (JSON décodé ;
    pages fusionnées en liste) ou `None`, `error` (`None`, ou la cause avec le chemin et le
    code HTTP). Chaque requête passe par `limiter.wait()` et porte `timeout` ; corps de plus
    de `max_bytes` refusé ; 429 et 5xx repris au plus `max_retries` fois, attente
    `Retry-After` plafonnée à `max_retry_after` par `sleep` ; 401, 403, 404 jamais repris.
    """

    REDIRECT = f"http://{HOST}:5615/callback"

    def setUp(self):
        super().setUp()
        self.clock = FakeClock()
        self.server = FakeServer(clock=self.clock.now)
        self.addCleanup(self.server.close)
        self.server.route(TOKEN_PATH, json_reply(load("token.json")))

    def client(self, **options):
        """Client branché sur le serveur factice, jeton déjà obtenu."""
        settings = {
            "timeout": 1.0,
            "limiter": api42.RateLimiter(clock=self.clock.now, sleep=self.clock.sleep),
            "sleep": self.clock.sleep,
            "max_retries": 2,
            "max_retry_after": 5.0,
        }
        settings.update(options)
        client = api42.Api42Client(self.server.url, **settings)
        self.assertIsNone(client.exchange_code(CLIENT_ID, CLIENT_SECRET, CODE, self.REDIRECT))
        return client

    def me_requests(self):
        return self.server.requests(ME_PATH)

    def test_N8_achievement_pages_merged(self):
        self.server.route(ACHIEVEMENTS_PATH, page(1), page(2))
        fetch = self.client().fetch_achievements()
        self.assertIsNone(fetch.error)
        self.assertEqual([item["id"] for item in fetch.data], list(range(1, 104)))
        queries = [request.query for request in self.server.requests(ACHIEVEMENTS_PATH)]
        self.assertEqual([query.get("page") for query in queries], [["1"], ["2"]])
        self.assertEqual([query.get("per_page") for query in queries], [["100"]] * 2)

    def test_N9_api_requests_half_a_second_apart(self):
        self.server.route(ME_PATH, json_reply(load("me_valid.json")))
        self.server.route(ACHIEVEMENTS_PATH, page(1), page(2))
        client = self.client()
        client.fetch_me()
        client.fetch_achievements()
        times = [
            request.at
            for request in self.server.requests()
            if request.path != TOKEN_PATH
        ]
        self.assertEqual(len(times), 3)
        gaps = [later - earlier for earlier, later in zip(times, times[1:])]
        self.assertTrue(all(gap >= 0.5 - 1e-9 for gap in gaps), gaps)

    def test_L9_html_or_truncated_body_rejected(self):
        client = self.client()
        replies = {
            "html": Reply(
                body=b"<html><body>Maintenance</body></html>",
                headers=(("Content-Type", "text/html"),),
            ),
            "truncated": Reply(
                body=b'{"cursus_users": [{"level": 12.',
                headers=(("Content-Type", "application/json"),),
            ),
        }
        for name, reply in replies.items():
            with self.subTest(name):
                self.server.route(ME_PATH, reply)
                fetch = client.fetch_me()
                self.assertIsNone(fetch.data)
                self.assertIn(ME_PATH, fetch.error)

    def test_L10_one_message_per_http_status(self):
        client = self.client()
        errors = {}
        for status in (401, 403, 404, 429, 500):
            with self.subTest(status=status):
                headers = (("Retry-After", "1"),) if status == 429 else ()
                self.server.route(ME_PATH, json_reply({"error": "x"}, status, headers))
                fetch = client.fetch_me()
                self.assertIsNone(fetch.data)
                self.assertIn(str(status), fetch.error)
                errors[status] = fetch.error
        self.assertEqual(len(set(errors.values())), 5, errors)

    def test_L10_retries_bounded_on_429_and_5xx_only(self):
        client = self.client(max_retries=2)
        expected = {401: 1, 403: 1, 404: 1, 429: 3, 500: 3, 503: 3}
        for status, count in expected.items():
            with self.subTest(status=status):
                headers = (("Retry-After", "1"),) if status == 429 else ()
                self.server.route(ME_PATH, json_reply({}, status, headers))
                before = len(self.me_requests())
                client.fetch_me()
                self.assertEqual(len(self.me_requests()) - before, count)

    def test_L10_retry_after_honoured_and_capped(self):
        client = self.client(max_retries=2, max_retry_after=5.0)
        self.server.route(
            ME_PATH,
            json_reply({}, 429, (("Retry-After", "1"),)),
            json_reply({}, 500),
            json_reply(load("me_valid.json")),
        )
        fetch = client.fetch_me()
        self.assertIsNone(fetch.error)
        self.assertEqual(fetch.data["cursus_users"][1]["level"], 12.44)
        first, second, _ = [request.at for request in self.me_requests()]
        self.assertGreaterEqual(second - first, 1.0)
        self.server.route(ME_PATH, json_reply({}, 429, (("Retry-After", "3600"),)))
        before = len(self.me_requests())
        self.clock.sleeps.clear()
        fetch = client.fetch_me()
        self.assertIn("429", fetch.error)
        self.assertLessEqual(len(self.me_requests()) - before, 3)
        self.assertTrue(all(pause <= 5.0 for pause in self.clock.sleeps), self.clock.sleeps)

    def test_L11_slow_server_hits_timeout(self):
        client = self.client(timeout=0.2)
        self.server.route(ME_PATH, Reply(body=b"{}", delay=0.6))
        begin = time.monotonic()
        fetch = client.fetch_me()
        self.assertLess(time.monotonic() - begin, 2.0)
        self.assertIsNone(fetch.data)
        self.assertIn(ME_PATH, fetch.error)

    def test_L13_endless_pagination_capped(self):
        self.server.route(ACHIEVEMENTS_PATH, page(1))
        fetch = self.client(max_pages=3).fetch_achievements()
        self.assertIsNone(fetch.data)
        self.assertIn(ACHIEVEMENTS_PATH, fetch.error)
        self.assertEqual(len(self.server.requests(ACHIEVEMENTS_PATH)), 3)

    def test_L14_body_over_cap_rejected(self):
        body = json.dumps({"cursus_users": [{"level": 1.0, "pad": "x" * 80}] * 60}).encode()
        for length in (True, False):
            with self.subTest(content_length=length):
                self.server.route(
                    ME_PATH,
                    Reply(
                        body=body,
                        headers=(("Content-Type", "application/json"),),
                        length=length,
                    ),
                )
                fetch = self.client(max_bytes=2048).fetch_me()
                self.assertIsNone(fetch.data)
                self.assertIn(ME_PATH, fetch.error)


class RateLimiterTest(Guarded):
    """`RateLimiter(rate=2.0, clock, sleep)` : `wait()` rend la main au plus `rate` fois
    par seconde de `clock`, en attendant par `sleep` le reste de l'intervalle.
    """

    def test_N9_limiter_spaces_calls_by_half_a_second(self):
        clock = FakeClock()
        limiter = api42.RateLimiter(rate=2.0, clock=clock.now, sleep=clock.sleep)
        times = []
        for _ in range(4):
            limiter.wait()
            times.append(clock.now())
        gaps = [later - earlier for earlier, later in zip(times, times[1:])]
        self.assertTrue(all(0.5 - 1e-9 <= gap <= 0.6 for gap in gaps), gaps)


class ReadApi42Test(Guarded):
    """`read_api42(env, cache_path, *, open_browser, api_base, consent_timeout,
    request_timeout, clock, sleep) -> Api42Result`, figé.

    `env` : dict de `check_env`, seules les clés `API42_*` sont lues ; identifiant ou secret
    `""` ou absent, port `None` ou absent : `unavailable`, l'erreur nomme ces variables, aucun
    appel réseau. Le serveur de retour écoute avant `open_browser(url)`. `clock` et `sleep`
    ne servent qu'au limiteur et aux reprises. Résultat : `status` (`ok`, `cache`,
    `unavailable`), `error` (`None` si `ok`), `level` (`StatedValue` du cursus 21, source
    `api42`), `projects` (validés, clés `PROJECT_KEYS`), `achievements` (A23, `ITEM_KEYS`,
    `obtained` statuée), `complete` (A23), `observed_at` (date ISO), `anomalies`
    (`duplicate_project`, `duplicate_achievement` ; `file` = chemin d'API), `read`
    (éléments reçus), `rejected` (doublons). `ok` écrit le cache `cache_path` (dossier créé) ;
    sinon le cache est relu tel quel (`cache`) ou, absent ou illisible, `unavailable` avec
    `level` `unmeasurable` (`api_unavailable`). `/v2/me` `{}` : réponse invalide.
    """

    def setUp(self):
        super().setUp()
        self.clock = FakeClock()
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.cache_path = self.tmp / "cache" / "api42.json"
        self.journal = ""
        self.port = None

    def serve(self, me=None, pages=None, token=None):
        """Serveur factice : jeton, `/v2/me` et deux pages d'achievements par défaut."""
        server = FakeServer(clock=self.clock.now)
        self.addCleanup(server.close)
        server.route(TOKEN_PATH, token or json_reply(load("token.json")))
        server.route(ME_PATH, me or json_reply(load("me_valid.json")))
        server.route(ACHIEVEMENTS_PATH, *(pages or (page(1), page(2))))
        return server

    def env(self, port=None):
        """Variables `API42_*` valides, port libre par défaut."""
        self.port = port or free_port()
        return {
            "API42_CLIENT_ID": CLIENT_ID,
            "API42_CLIENT_SECRET": CLIENT_SECRET,
            "API42_CALLBACK_PORT": self.port,
        }

    def sync(self, server, browser=None, env=None, consent_timeout=2.0):
        """Lance `read_api42` en capturant journal, sortie et erreur standard."""
        browser = browser or Browser(CODE)
        with Capture() as capture:
            result = api42.read_api42(
                self.env() if env is None else env,
                self.cache_path,
                open_browser=browser,
                api_base=server.url,
                consent_timeout=consent_timeout,
                request_timeout=1.0,
                clock=self.clock.now,
                sleep=self.clock.sleep,
            )
            browser.join()
        self.journal += capture.text
        return result

    def assert_unavailable(self, result):
        """Vérifie un résultat `unavailable` sans cache, niveau `api_unavailable`."""
        self.assertEqual(result.status, "unavailable")
        self.assertTrue(result.error)
        self.assertEqual(result.level.status, "unmeasurable")
        self.assertEqual(result.level.reason_code, "api_unavailable")
        self.assertEqual(result.complete.status, "unmeasurable")

    def test_N3_code_exchanged_and_token_kept_in_memory(self):
        server = self.serve()
        result = self.sync(server)
        self.assertEqual(result.status, "ok", result.error)
        [request] = server.requests(TOKEN_PATH)
        self.assertEqual((request.method, request.query), ("POST", {}))
        form = parse_qs(request.body.decode("utf-8"))
        expected = {
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": CODE,
            "redirect_uri": f"http://{HOST}:{self.port}/callback",
        }
        for key, value in expected.items():
            self.assertEqual(form.get(key), [value], key)
        api_requests = server.requests(ME_PATH) + server.requests(ACHIEVEMENTS_PATH)
        self.assertEqual(len(api_requests), 3)
        for api_request in api_requests:
            self.assertEqual(api_request.headers.get("authorization"), f"Bearer {TOKEN}")
        self.assertTrue(self.cache_path.is_file())
        self.assertNotIn(TOKEN, written_text(self.tmp))
        self.assertNotIn(TOKEN, repr(result))

    def test_N4_cursus_21_level_observed(self):
        result = self.sync(self.serve())
        self.assertEqual(result.status, "ok", result.error)
        self.assertIsNone(result.error)
        self.assertEqual(result.level.value, 12.44)
        self.assertEqual(result.level.status, "observed")
        self.assertEqual(result.level.sources, ("api42",))
        self.assertEqual(result.observed_at, date.today().isoformat())
        with self.assertRaises(dataclasses.FrozenInstanceError):
            result.status = "cache"

    def test_N5_validated_projects_extracted(self):
        result = self.sync(self.serve())
        self.assertEqual({project["id"] for project in result.projects}, VALIDATED_IDS)
        for project in result.projects:
            self.assertEqual(set(project), PROJECT_KEYS)
        libft = next(project for project in result.projects if project["id"] == 1314)
        self.assertEqual((libft["slug"], libft["final_mark"]), ("42cursus-libft", 125))

    def test_N6_obtained_achievements_extracted(self):
        result = self.sync(self.serve())
        self.assertEqual(len(result.achievements), 103)
        obtained = set()
        for item in result.achievements:
            self.assertEqual(set(item), ITEM_KEYS)
            self.assertEqual(item["obtained"].status, "observed")
            if item["obtained"].value is True:
                obtained.add(item["id"])
        self.assertEqual(obtained, OBTAINED_IDS)
        self.assertEqual((result.complete.value, result.complete.status), (True, "observed"))

    def test_N7_personal_fields_absent_from_output_and_cache(self):
        fixture = (FIXTURES / "me_personal_fields.json").read_text(encoding="utf-8")
        server = self.serve(me=json_reply(load("me_personal_fields.json")))
        result = self.sync(server)
        self.assertEqual(result.status, "ok", result.error)
        self.assertTrue(self.cache_path.is_file())
        cache = written_text(self.tmp)
        for marker in PERSONAL_MARKERS:
            with self.subTest(marker=marker):
                self.assertIn(marker, fixture)
                self.assertNotIn(marker, repr(result))
                self.assertNotIn(marker, cache)

    def test_N10_cache_written_then_read_when_api_fails(self):
        server = self.serve()
        first = self.sync(server)
        self.assertEqual(first.status, "ok", first.error)
        written = self.cache_path.read_bytes()
        server.route(TOKEN_PATH, json_reply({"error": "server"}, 500))
        second = self.sync(server)
        self.assertEqual(second.status, "cache")
        self.assertTrue(second.error)
        self.assertEqual(second.level, first.level)
        self.assertEqual(second.projects, first.projects)
        self.assertEqual(second.achievements, first.achievements)
        self.assertEqual(second.observed_at, first.observed_at)
        self.assertEqual(self.cache_path.read_bytes(), written)

    def test_N12_secrets_absent_from_journal_cache_and_errors(self):
        ok = self.sync(self.serve())
        self.assertEqual(ok.status, "ok", ok.error)
        echo = {"error": "invalid_grant", "error_description": f"{CODE} {CLIENT_SECRET}"}
        failed = self.sync(self.serve(token=json_reply(echo, 401)))
        self.assertEqual(failed.status, "cache")
        written = written_text(self.tmp)
        for secret in SECRETS:
            with self.subTest(secret=secret):
                self.assertNotIn(secret, self.journal)
                self.assertNotIn(secret, written)
                self.assertNotIn(secret, failed.error)
                self.assertNotIn(secret, repr(ok) + repr(failed))

    def test_L1_missing_credentials_named_without_network(self):
        complete = self.env()
        cases = {
            "absent": ({}, VARIABLES),
            "client_id": ({**complete, "API42_CLIENT_ID": ""}, VARIABLES[:1]),
            "secret": ({**complete, "API42_CLIENT_SECRET": ""}, VARIABLES[1:2]),
            "port": ({**complete, "API42_CALLBACK_PORT": None}, VARIABLES[2:]),
        }
        for name, (env, named) in cases.items():
            with self.subTest(name):
                server = self.serve()
                browser = Browser(CODE)
                result = self.sync(server, browser=browser, env=env)
                self.assertEqual(result.status, "unavailable")
                self.assertEqual(result.level.status, "unmeasurable")
                for variable in VARIABLES:
                    check = self.assertIn if variable in named else self.assertNotIn
                    check(variable, result.error)
                self.assertEqual((browser.urls, server.requests()), ([], []))

    def test_L2_no_consent_times_out_and_reads_cache(self):
        server = self.serve()
        self.assertEqual(self.sync(server).status, "ok")
        begin = time.monotonic()
        result = self.sync(server, browser=Browser(CODE, act=False), consent_timeout=0.3)
        self.assertLess(time.monotonic() - begin, 2.0)
        self.assertEqual(result.status, "cache")
        self.assertTrue(result.error)
        self.assertEqual((result.level.value, result.level.status), (12.44, "observed"))
        self.assertEqual(len(server.requests(TOKEN_PATH)), 1)

    def test_L3_bad_state_never_exchanges_code(self):
        server = self.serve()
        browser = Browser(CODE, params={"state": "wrong-state"})
        result = self.sync(server, browser=browser, consent_timeout=0.4)
        self.assert_unavailable(result)
        self.assertEqual(browser.statuses, [400])
        self.assertEqual(server.requests(TOKEN_PATH), [])

    def test_L4_replayed_callback_exchanged_once(self):
        server = self.serve()
        browser = Browser(CODE, times=2)
        result = self.sync(server, browser=browser)
        self.assertEqual(result.status, "ok", result.error)
        self.assertEqual(browser.statuses[0], 200)
        self.assertNotEqual(browser.statuses[1], 200)
        self.assertEqual(len(server.requests(TOKEN_PATH)), 1)

    def test_L5_access_denied_falls_back(self):
        server = self.serve()
        browser = Browser(CODE, params={"code": None, "error": "access_denied"})
        result = self.sync(server, browser=browser)
        self.assert_unavailable(result)
        self.assertIn("access_denied", result.error)
        self.assertEqual(server.requests(TOKEN_PATH), [])

    def test_L6_empty_me_is_invalid(self):
        result = self.sync(self.serve(me=json_reply(load("me_empty.json"))))
        self.assert_unavailable(result)
        self.assertIn(ME_PATH, result.error)
        self.assertFalse(self.cache_path.exists())

    def test_L7_cursus_21_absent_level_unmeasurable(self):
        me = load("me_valid.json")
        me["cursus_users"] = [
            entry
            for entry in me["cursus_users"]
            if entry["cursus_id"] != 21
        ]
        result = self.sync(self.serve(me=json_reply(me)))
        self.assertEqual(result.status, "ok", result.error)
        self.assertEqual((result.level.value, result.level.status), (None, "unmeasurable"))
        self.assertIn("21", result.level.reason)
        self.assertEqual({project["id"] for project in result.projects}, VALIDATED_IDS)

    def test_L8_invalid_levels_unmeasurable(self):
        for level in ("abc", "12,44", None, math.nan, math.inf, -1.0):
            with self.subTest(level=level):
                me = load("me_valid.json")
                me["cursus_users"][1]["level"] = level
                result = self.sync(self.serve(me=json_reply(me)))
                self.assertEqual(result.status, "ok", result.error)
                self.assertEqual(result.level.status, "unmeasurable")
                self.assertIsNone(result.level.value)

    def test_L12_duplicates_kept_once_and_reported(self):
        me = load("me_valid.json")
        me["projects_users"].append(me["projects_users"][0])
        me["achievements"].append(me["achievements"][0])
        last = load("achievements_page2.json") + [load("achievements_page1.json")[-1]]
        server = self.serve(me=json_reply(me), pages=(page(1), json_reply(last)))
        result = self.sync(server)
        self.assertEqual(result.status, "ok", result.error)
        project_ids = [project["id"] for project in result.projects]
        self.assertEqual(sorted(project_ids), sorted(VALIDATED_IDS))
        item_ids = [item["id"] for item in result.achievements]
        self.assertEqual(sorted(item_ids), list(range(1, 104)))
        kinds = Counter(anomaly.kind for anomaly in result.anomalies)
        self.assertEqual(kinds, Counter(duplicate_project=1, duplicate_achievement=2))
        files = {anomaly.file for anomaly in result.anomalies}
        self.assertEqual(files, {ME_PATH, ACHIEVEMENTS_PATH})
        self.assertTrue(all(anomaly.line >= 1 for anomaly in result.anomalies))
        self.assertEqual(result.rejected, 3)
        self.assertEqual(result.read, 5 + 4 + 104)

    def test_L15_absent_empty_or_corrupt_cache_unavailable(self):
        failing = json_reply({"error": "server"}, 500)
        errors = {}
        for name, content in (("absent", None), ("empty", b""), ("corrupt", b"{tron")):
            with self.subTest(name):
                if content is not None:
                    self.cache_path.parent.mkdir(exist_ok=True)
                    self.cache_path.write_bytes(content)
                result = self.sync(self.serve(token=failing))
                self.assert_unavailable(result)
                errors[name] = result.error
        self.cache_path.write_bytes(b"[]")
        self.assert_unavailable(self.sync(self.serve(token=failing)))
        self.assertEqual(len(set(errors.values())), 3, errors)

    def test_L16_busy_port_named_without_browser(self):
        occupant = socket.socket()
        self.addCleanup(occupant.close)
        occupant.bind((HOST, 0))
        occupant.listen()
        port = occupant.getsockname()[1]
        server = self.serve()
        browser = Browser(CODE)
        result = self.sync(server, browser=browser, env=self.env(port))
        self.assert_unavailable(result)
        self.assertIn(str(port), result.error)
        self.assertEqual((browser.urls, server.requests()), ([], []))
        socket.create_connection((HOST, port), timeout=0.5).close()

    def test_L17_full_list_refused_keeps_obtained(self):
        refused = json_reply({"error": "Forbidden"}, 403)
        result = self.sync(self.serve(pages=(refused,)))
        self.assertEqual(result.status, "ok", result.error)
        self.assertIsNone(result.error)
        self.assertEqual(result.complete.status, "unmeasurable")
        self.assertEqual(result.complete.reason_code, "full_list_unavailable")
        self.assertIn("liste complète indisponible", result.complete.reason.lower())
        self.assertEqual({item["id"] for item in result.achievements}, OBTAINED_IDS)
        self.assertTrue(all(item["obtained"].value is True for item in result.achievements))


class StaticTest(Guarded):
    """Analyse du source de tous les `api42*.py` : délais, TLS et `state`."""

    def source(self):
        """Texte de tous les `api42*.py` du dossier du module importé, bout à bout."""
        folder = Path(api42.__file__).parent
        return "\n".join(p.read_text("utf-8") for p in sorted(folder.glob("api42*.py")))

    def test_N13_every_network_call_has_timeout(self):
        calls = []
        for node in ast.walk(ast.parse(self.source())):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            name = getattr(func, "id", None) or getattr(func, "attr", None)
            receiver = ast.unparse(func.value) if isinstance(func, ast.Attribute) else ""
            if name in NETWORK_CALLS or (name == "open" and "opener" in receiver.lower()):
                calls.append(node)
        self.assertTrue(calls, "aucun appel réseau trouvé")
        for call in calls:
            keywords = {keyword.arg for keyword in call.keywords}
            self.assertIn("timeout", keywords, ast.unparse(call))

    def test_C3_tls_never_bypassed(self):
        self.assertEqual(TLS_BYPASS.findall(self.source()), [])

    def test_L3_state_compared_in_constant_time(self):
        self.assertRegex(self.source(), r"\bcompare_digest\(")


if __name__ == "__main__":
    unittest.main()
