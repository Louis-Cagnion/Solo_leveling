"""Tests de la revue du client de l'API 42 (T4.d) : trois défauts, tests rouges d'abord.

- I1 : `CallbackServer` sert plusieurs connexions à la fois (une connexion muette ou un
  client goutte-à-goutte ne bloque pas le vrai retour) et son délai total reste borné.
- I2 : `read_api42` ne lève jamais sur un surrogate isolé venu de l'API : l'élément est
  écarté (`malformed_achievement` ou `malformed_project`), le cache est écrit sans lui et
  aucun fichier temporaire `.api42.json.*` ne reste dans son dossier.
- S : les analyses statiques portent sur TOUS les `api42*.py` (propriété du code).
Pendant tout le module, `socket` refuse tout hôte hors de 127.0.0.1.
"""

import ast
import json
import re
import socket
import tempfile
import time
import unittest
from collections import Counter
from pathlib import Path

from tests.system_sync.sources.fake_server import (
    HOST,
    Browser,
    Capture,
    FakeClock,
    FakeServer,
    callback_url,
    dribble,
    free_port,
    get_status,
    in_thread,
    json_reply,
    load,
    silent_connection,
)
from tests.system_sync.sources.test_api42 import (
    ACHIEVEMENTS_PATH,
    CLIENT_ID,
    CLIENT_SECRET,
    CODE,
    GUARD,
    ME_PATH,
    TOKEN_PATH,
    Guarded,
    api42,
    page,
)

REQUEST_LINE = b"GET /favicon.ico HTTP/1.0\r\n"
STATE_NAME = re.compile(r"(?<![a-z])state(?![a-z])")
COMPARISON = re.compile(r"==|!=")


def setUpModule():
    """Garde le réseau pendant tout le module."""
    GUARD.start()


def tearDownModule():
    GUARD.stop()


class CallbackConcurrencyTest(Guarded):
    """I1 : le serveur de retour reste disponible et son délai total borné.

    Une préconnexion muette (Chrome en ouvre) ne doit pas empêcher de servir le vrai
    retour ; un client qui envoie 1 octet toutes les 0,25 s ne doit pas prolonger `wait()`
    au-delà de environ le délai demandé (au plus 2 fois ce délai plus 1 s).
    """

    def start(self, timeout):
        """Démarre un `CallbackServer` ; rend (serveur, port, state)."""
        port = free_port()
        _, state = api42.authorization_url(CLIENT_ID, port)
        server = api42.CallbackServer(port, state, timeout)
        self.assertIsNone(server.start())
        return server, port, state

    def test_I1_silent_connection_does_not_block_real_callback(self):
        server, port, state = self.start(1.5)
        silent = silent_connection(port)
        self.addCleanup(silent.close)
        statuses = []

        def real_return():
            time.sleep(0.1)
            statuses.append(get_status(callback_url(port, code=CODE, state=state)))

        thread = in_thread(real_return)
        callback = server.wait()
        thread.join(timeout=3)
        self.assertEqual((callback.code, statuses), (CODE, [200]), callback.error)

    def test_I1_slow_client_cannot_extend_total_delay(self):
        timeout = 0.6
        server, port, _ = self.start(timeout)
        thread = in_thread(lambda: dribble(port, REQUEST_LINE, 0.25, 3.0))
        begin = time.monotonic()
        callback = server.wait()
        elapsed = time.monotonic() - begin
        thread.join(timeout=3)
        self.assertLessEqual(elapsed, 2 * timeout + 1.0, "wait() rendu bien après le délai")
        self.assertIsNone(callback.code)
        self.assertTrue(callback.error)
        with self.assertRaises(ConnectionRefusedError):
            socket.create_connection((HOST, port), timeout=0.2).close()


class SurrogateTest(Guarded):
    """I2 : un surrogate isolé dans un nom venu de l'API écarte l'élément, sans lever.

    `read_api42` rend `ok` avec le reste du résultat, l'anomalie `malformed_achievement`
    (achievement absent du catalogue) ou `malformed_project` (projet validé), un cache écrit
    sans l'élément et lisible, et aucun fichier `.api42.json.*` dans le dossier du cache.
    """

    def setUp(self):
        super().setUp()
        self.clock = FakeClock()
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.cache_path = Path(tmp.name) / "cache" / "api42.json"

    def serve(self, me=None, token=None):
        """Serveur factice : jeton, `/v2/me` (corps JSON de `me`) et les deux pages."""
        server = FakeServer(clock=self.clock.now)
        self.addCleanup(server.close)
        server.route(TOKEN_PATH, token or json_reply(load("token.json")))
        server.route(ME_PATH, json_reply(me or load("me_valid.json")))
        server.route(ACHIEVEMENTS_PATH, page(1), page(2))
        return server

    def cache_files(self):
        """Noms des fichiers du dossier du cache, ou `[]` s'il n'existe pas."""
        folder = self.cache_path.parent
        return sorted(path.name for path in folder.iterdir()) if folder.is_dir() else []

    def sync(self, server):
        """Lance `read_api42` ; une exception levée fait échouer le test, cache listé."""
        browser = Browser(CODE)
        env = {
            "API42_CLIENT_ID": CLIENT_ID,
            "API42_CLIENT_SECRET": CLIENT_SECRET,
            "API42_CALLBACK_PORT": free_port(),
        }
        with Capture():
            try:
                result = api42.read_api42(
                    env,
                    self.cache_path,
                    open_browser=browser,
                    api_base=server.url,
                    consent_timeout=2.0,
                    request_timeout=1.0,
                    clock=self.clock.now,
                    sleep=self.clock.sleep,
                )
            except Exception as error:
                self.fail(
                    f"read_api42 a levé {type(error).__name__} : {error} ; "
                    f"dossier du cache : {self.cache_files()}"
                )
            finally:
                browser.join()
        return result

    def assert_dropped(self, me, kind):
        """Lit `me` : un élément écarté (`kind`), le reste normal, cache sain et lisible."""
        result = self.sync(self.serve(me))
        self.assertEqual(result.status, "ok", result.error)
        self.assertEqual(Counter(a.kind for a in result.anomalies), Counter({kind: 1}))
        self.assertEqual((result.rejected, result.level.value), (1, 12.44))
        self.assertEqual(self.cache_files(), ["api42.json"])
        failing = json_reply({"error": "server"}, 500)
        cached = self.sync(self.serve(me, token=failing))
        self.assertEqual(cached.status, "cache", cached.error)
        self.assertEqual(cached.projects, result.projects)
        self.assertEqual(len(cached.achievements), len(result.achievements))
        return result

    def test_I2_lone_surrogate_in_absent_achievement_name_is_dropped(self):
        me = load("me_valid.json")
        extra = {"id": 999, "name": "\ud800", "description": "Fictif 999", "kind": "project"}
        me["achievements"].append(extra)
        result = self.assert_dropped(me, "malformed_achievement")
        self.assertEqual(len(result.achievements), 103)
        self.assertNotIn(999, {item["id"] for item in result.achievements})

    def test_I2_lone_surrogate_in_validated_project_name_is_dropped(self):
        me = load("me_valid.json")
        me["projects_users"][0]["project"]["name"] = "\udcff"
        result = self.assert_dropped(me, "malformed_project")
        self.assertEqual({project["id"] for project in result.projects}, {1327})

    def test_I2_accented_name_still_accepted(self):
        """Garde-fou : un nom accentué ordinaire passe, sans anomalie."""
        me = load("me_valid.json")
        me["projects_users"][0]["project"]["name"] = "Élève"
        result = self.sync(self.serve(me))
        self.assertEqual(result.status, "ok", result.error)
        self.assertEqual(result.anomalies, ())
        libft = next(project for project in result.projects if project["id"] == 1314)
        self.assertEqual(libft["name"], "Élève")
        self.assertEqual(self.cache_files(), ["api42.json"])


class StaticAllModulesTest(Guarded):
    """S : les règles de code portent sur tous les `api42*.py`, pas sur un seul fichier."""

    def sources(self):
        """Arbres syntaxiques des `api42*.py` du dossier de `api42`, par nom de fichier."""
        folder = Path(api42.__file__).parent
        return {
            path.name: ast.parse(path.read_text(encoding="utf-8"))
            for path in sorted(folder.glob("api42*.py"))
        }

    def test_S_state_never_compared_with_an_operator(self):
        found = []
        for name, tree in self.sources().items():
            for node in ast.walk(tree):
                text = ast.unparse(node) if isinstance(node, ast.Compare) else ""
                if COMPARISON.search(text) and STATE_NAME.search(text):
                    found.append(f"{name}:{node.lineno} {text}")
        self.assertEqual(found, [], "`state` comparé sans compare_digest")


if __name__ == "__main__":
    unittest.main()
