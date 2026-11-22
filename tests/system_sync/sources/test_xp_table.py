"""Tests de `system_sync.sources.xp_table` (T5, cas N1 à N10 et L1 à L12 ; A17, A18, A22).

Contrat de T5.b (`from system_sync.sources import xp_table`, aucune fonction publique ne
lève) :
- `load_xp_table(url, commit, sha256, cache_path, *, timeout=10.0, max_bytes=1048576)
  -> XpTableResult` : télécharge `url` (aucune redirection suivie, `timeout` secondes par
  appel, `max_bytes` octets au plus), compare le sha256 des octets bruts à `sha256`
  (hexadécimal), valide la forme `{meta, levels: [{level, experience, ...}]}` (au moins
  deux niveaux entiers et des XP entières, les deux strictement croissants), puis écrit
  le cache atomiquement en 0600 dans `cache_path` (dossier créé) avec les octets reçus.
  Sur un échec, relit le cache en le revérifiant de la même façon (hash épinglé compris).
- `XpTableResult(status, error, table)` : `status` vaut `ok` (réseau), `cache` (cache
  relu) ou `unavailable` ; `error` est `None` ou un texte qui nomme la cause (code HTTP,
  deux hashes, champ fautif, taille limite, chemin du cache) ; `table` est un `XpTable` ou
  `None` si `unavailable`. Un échec ne laisse aucun cache écrit.
- `XpTable(levels, url, commit, sha256)` : `levels` est le tuple de couples (niveau, XP),
  dans l'ordre croissant.
- `xp_for_level(result, level) -> StatedValue` : XP entière du niveau (int ou float
  fini), par interpolation linéaire entre les deux niveaux voisins, arrondie à la moitié
  vers le haut. `estimated` avec des sources qui citent l'URL et le commit. Table
  `unavailable` : `unmeasurable`, code `xp_table_unavailable`. Niveau absent, texte,
  NaN ou infini : `unmeasurable`, code `level_invalid`. Niveau hors de la table : valeur
  `None`, `insufficient`, code `level_out_of_table`, sans extrapolation.
- `level_for_xp(result, xp) -> StatedValue` : niveau décimal (float) d'une XP, fonction
  inverse de la précédente, mêmes statuts. XP absente, texte, NaN ou infinie :
  `unmeasurable`, code `xp_invalid`. XP hors de la table : `insufficient`, code
  `xp_out_of_table`.
Codes à ajouter à `model.REASON_CODES` : `xp_table_unavailable`, `level_out_of_table`,
`xp_out_of_table`, `xp_invalid` (`level_invalid` et `xp_interpolated` existent déjà).
Pendant tout le module, `socket` refuse tout hôte hors de 127.0.0.1, les variables de
proxy sont retirées, et chaque serveur écoute sur un port libre choisi par le système.
"""

import ast
import hashlib
import json
import math
import os
import stat
import tempfile
import time
import unittest
from pathlib import Path

from system_sync import model
from tests.system_sync.sources.fake_server import (
    HOST,
    FakeServer,
    NetworkGuard,
    Reply,
    free_port,
)

try:
    from system_sync.sources import xp_table
except ImportError:
    xp_table = None  # chaque test échoue dans `setUp` tant que le module manque

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "xp_table"
COMMIT = "0123456789abcdef0123456789abcdef01234567"
PATH = f"/fictional/{COMMIT}/data/experience.json"
VALID_LEVELS = ((0, 0), (1, 100), (2, 300), (3, 600), (4, 1000), (5, 1500))
JSON_TYPE = (("Content-Type", "application/json"),)
NETWORK_CALLS = {"urlopen", "HTTPConnection", "HTTPSConnection", "create_connection"}
NOT_A_LEVEL = ("12,44", float("nan"), float("inf"), float("-inf"))
GUARD = NetworkGuard()


def setUpModule():
    """Garde le réseau pendant tout le module."""
    GUARD.start()


def tearDownModule():
    GUARD.stop()


def fixture(name):
    """Octets bruts de la fixture `tests/fixtures/xp_table/<name>`."""
    return (FIXTURES / name).read_bytes()


def table_bytes(xps, padding=0):
    """Octets JSON d'une table fictive : niveau i porte l'XP `xps[i]`.

    Args:
        xps: liste des XP, un niveau par élément à partir de 0.
        padding: nombre de caractères de remplissage ajoutés à `meta`.
    """
    data = {
        "meta": {"source": "fictional", "padding": "x" * padding},
        "levels": [{"level": index, "experience": xp} for index, xp in enumerate(xps)],
    }
    return json.dumps(data).encode("utf-8")


def pin(body):
    """Sha256 hexadécimal des octets bruts `body`."""
    return hashlib.sha256(body).hexdigest()


def reply(body, **kwargs):
    """`Reply` 200 JSON portant `body`."""
    return Reply(status=200, body=body, headers=JSON_TYPE, **kwargs)


class Guarded(unittest.TestCase):
    """Base : module présent, cache temporaire, aucune connexion hors 127.0.0.1."""

    def setUp(self):
        if xp_table is None:
            self.fail("module system_sync.sources.xp_table absent")
        GUARD.outside.clear()
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.cache = Path(folder.name) / "cache" / "xp_table.json"
        self.dead_url = f"http://{HOST}:{free_port()}{PATH}"

    def tearDown(self):
        self.assertEqual(GUARD.outside, [], "connexion tentée hors de 127.0.0.1")

    def serve(self, *replies):
        """Serveur factice qui rend `replies` sur `PATH`, fermé en fin de test."""
        server = FakeServer()
        self.addCleanup(server.close)
        server.route(PATH, *replies)
        return server

    def fetch(self, url, body, **kwargs):
        """Charge `url` en épinglant le hash de `body` ; `timeout` vaut 2 s par défaut."""
        kwargs.setdefault("timeout", 2.0)
        return xp_table.load_xp_table(url, COMMIT, pin(body), self.cache, **kwargs)

    def loaded(self, body=None):
        """Résultat `ok` d'une table servie par un serveur factice (fixture valide)."""
        body = fixture("valid.json") if body is None else body
        server = self.serve(reply(body))
        result = self.fetch(server.url + PATH, body)
        self.assertEqual(result.status, "ok", result.error)
        return result

    def assert_unavailable(self, result):
        """Vérifie un échec : `unavailable`, cause nommée, rien en cache, pas de table."""
        self.assertEqual(result.status, "unavailable")
        self.assertIsNone(result.table)
        self.assertIsInstance(result.error, str)
        self.assertTrue(result.error.strip())
        self.assertFalse(self.cache.exists(), "cache écrit malgré l'échec")

    def assert_estimated(self, stated, value):
        """Vérifie une valeur estimée de `value`, avec l'URL et le commit en sources."""
        self.assertIsInstance(stated, model.StatedValue)
        self.assertEqual(stated.status, "estimated", stated)
        self.assertEqual(stated.value, value)
        self.assertTrue(any(COMMIT in name for name in stated.sources), stated.sources)
        self.assertTrue(any(PATH in name for name in stated.sources), stated.sources)

    def assert_refused(self, stated, status, code):
        """Vérifie une valeur sans mesure : statut, code, raison, valeur `None`."""
        self.assertIsInstance(stated, model.StatedValue)
        self.assertEqual((stated.status, stated.reason_code), (status, code), stated)
        self.assertIsNone(stated.value)
        self.assertTrue(stated.reason.strip())


class NominalTest(Guarded):
    """Chargement, hash, interpolation et inverse sur la table fictive de 0 à 5."""

    def test_N1_fictional_table_loaded(self):
        result = self.loaded()
        self.assertIsNone(result.error)
        self.assertEqual(tuple(map(tuple, result.table.levels)), VALID_LEVELS)
        self.assertEqual(result.table.commit, COMMIT)

    def test_N2_pinned_hash_checked_on_raw_bytes(self):
        body = fixture("valid.json")
        server = self.serve(reply(body))
        result = self.fetch(server.url + PATH, body)
        self.assertEqual(result.status, "ok", result.error)
        self.assertEqual(result.table.sha256, pin(body))
        self.assertEqual(len(server.requests(PATH)), 1)
        self.assertEqual(server.requests(PATH)[0].method, "GET")

    def test_N3_exact_xp_at_integer_levels(self):
        result = self.loaded()
        for level, xp in VALID_LEVELS:
            for given in (level, float(level)):
                with self.subTest(level=given):
                    self.assert_estimated(xp_table.xp_for_level(result, given), xp)

    def test_N4_level_two_and_a_half_gives_450(self):
        stated = xp_table.xp_for_level(self.loaded(), 2.5)
        self.assert_estimated(stated, 450)
        self.assertIs(type(stated.value), int)

    def test_N5_continuity_at_integer_bounds(self):
        result = self.loaded()
        epsilon = 2**-20
        for level, xp in VALID_LEVELS[1:-1]:
            for given in (level - epsilon, level, level + epsilon):
                with self.subTest(level=given):
                    self.assertEqual(xp_table.xp_for_level(result, given).value, xp)

    def test_N6_strictly_increasing_on_a_fine_grid(self):
        result = self.loaded()
        values = [xp_table.xp_for_level(result, step / 20).value for step in range(101)]
        self.assertNotIn(None, values)
        for before, after in zip(values, values[1:]):
            self.assertLess(before, after)

    def test_N7_round_trip_xp_and_level(self):
        result = self.loaded()
        for step in range(21):
            level = step / 4
            xp = xp_table.xp_for_level(result, level).value
            with self.subTest(level=level, xp=xp):
                back = xp_table.level_for_xp(result, xp)
                self.assertEqual(back.status, "estimated", back)
                self.assertAlmostEqual(back.value, level, delta=1e-9)
        self.assertAlmostEqual(xp_table.level_for_xp(result, 450).value, 2.5, delta=1e-9)

    def test_N8_estimated_with_url_and_commit_sources(self):
        result = self.loaded()
        for level in (0, 2.5, 5):
            with self.subTest(level=level):
                stated = xp_table.xp_for_level(result, level)
                self.assertEqual(stated.status, "estimated")
                self.assertTrue(any(PATH in name for name in stated.sources))
                self.assertTrue(any(COMMIT in name for name in stated.sources))
        inverse = xp_table.level_for_xp(result, 450)
        self.assertEqual(inverse.status, "estimated")
        self.assertTrue(any(COMMIT in name for name in inverse.sources))

    def test_N9_cache_written_then_read_when_network_is_cut(self):
        first = self.loaded()
        mode = stat.S_IMODE(os.stat(self.cache).st_mode)
        self.assertEqual(mode, 0o600)
        files = [path.name for path in self.cache.parent.iterdir()]
        self.assertEqual(files, [self.cache.name])
        again = self.fetch(self.dead_url, fixture("valid.json"))
        self.assertEqual(again.status, "cache", again.error)
        self.assertIsInstance(again.error, str)
        self.assertEqual(again.table.levels, first.table.levels)
        self.assert_estimated(xp_table.xp_for_level(again, 2.5), 450)

    def test_N10_timeout_on_every_call(self):
        body = fixture("valid.json")
        server = self.serve(reply(body, delay=1.0))
        begin = time.monotonic()
        result = self.fetch(server.url + PATH, body, timeout=0.2)
        self.assertLess(time.monotonic() - begin, 0.8)
        self.assert_unavailable(result)
        source = Path(xp_table.__file__).read_text(encoding="utf-8")
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Call):
                func = node.func
                name = getattr(func, "id", None) or getattr(func, "attr", None)
                receiver = ast.unparse(func.value) if isinstance(func, ast.Attribute) else ""
                if name in NETWORK_CALLS or (name == "open" and "opener" in receiver.lower()):
                    keywords = {keyword.arg for keyword in node.keywords}
                    self.assertIn("timeout", keywords, ast.unparse(node))


class RoundingTest(Guarded):
    """Arrondi de l'XP à l'entier : la moitié monte, jamais au pair (`round` de Python)."""

    def test_R1_half_rounds_up_not_to_even(self):
        result = self.loaded(table_bytes([0, 1, 4]))
        cases = ((0.5, 1), (1.5, 3), (0.25, 0), (0.75, 1), (1.25, 2), (1.75, 3))
        for level, expected in cases:
            with self.subTest(level=level):
                self.assert_estimated(xp_table.xp_for_level(result, level), expected)

    def test_R2_just_around_the_half(self):
        result = self.loaded(table_bytes([0, 1, 4]))
        epsilon = 1 / 1024
        for level, expected in ((0.5 - epsilon, 0), (0.5 + epsilon, 1)):
            with self.subTest(level=level):
                self.assert_estimated(xp_table.xp_for_level(result, level), expected)


class LimitTest(Guarded):
    """Entrées invalides, bornes, tables et réponses refusées."""

    def test_L1_absent_level(self):
        result = self.loaded()
        stated = xp_table.xp_for_level(result, None)
        self.assert_refused(stated, "unmeasurable", "level_invalid")
        inverse = xp_table.level_for_xp(result, None)
        self.assert_refused(inverse, "unmeasurable", "xp_invalid")

    def test_L2_text_nan_and_infinite_levels(self):
        result = self.loaded()
        for given in NOT_A_LEVEL:
            with self.subTest(given=given):
                stated = xp_table.xp_for_level(result, given)
                self.assert_refused(stated, "unmeasurable", "level_invalid")
                inverse = xp_table.level_for_xp(result, given)
                self.assert_refused(inverse, "unmeasurable", "xp_invalid")

    def test_L3_outside_the_table_without_extrapolation(self):
        result = self.loaded()
        for given in (-1, -0.001, 5.001, 6, 1e9):
            with self.subTest(level=given):
                stated = xp_table.xp_for_level(result, given)
                self.assert_refused(stated, "insufficient", "level_out_of_table")
        for given in (-1, -0.001, 1500.001, 1501, 1e12):
            with self.subTest(xp=given):
                stated = xp_table.level_for_xp(result, given)
                self.assert_refused(stated, "insufficient", "xp_out_of_table")

    def test_L4_exact_bounds_zero_and_maximum(self):
        result = self.loaded()
        self.assert_estimated(xp_table.xp_for_level(result, 0), 0)
        self.assert_estimated(xp_table.xp_for_level(result, 5), 1500)
        for xp, level in ((0, 0), (1500, 5)):
            with self.subTest(xp=xp):
                inverse = xp_table.level_for_xp(result, xp)
                self.assertEqual(inverse.status, "estimated", inverse)
                self.assertAlmostEqual(inverse.value, level, delta=1e-9)

    def test_L5_different_hash_with_both_hashes_and_no_cache(self):
        body = fixture("valid.json")
        server = self.serve(reply(body))
        wrong = "0" * 64
        result = xp_table.load_xp_table(
            server.url + PATH,
            COMMIT,
            wrong,
            self.cache,
            timeout=2.0,
        )
        self.assert_unavailable(result)
        self.assertIn(wrong, result.error)
        self.assertIn(pin(body), result.error)

    def test_L5_different_hash_leaves_an_existing_cache_untouched(self):
        self.loaded()
        before = self.cache.read_bytes()
        other = fixture("not_increasing.json")
        server = self.serve(reply(other))
        self.fetch(server.url + PATH, fixture("valid.json"))
        self.assertEqual(self.cache.read_bytes(), before)

    def test_L6_empty_table_without_levels_or_with_a_missing_field(self):
        cases = (
            (fixture("empty.json"), "levels"),
            (json.dumps({"meta": {}}).encode("utf-8"), "levels"),
            (fixture("missing_field.json"), "experience"),
        )
        for body, named in cases:
            with self.subTest(named=named, size=len(body)):
                server = self.serve(reply(body))
                result = self.fetch(server.url + PATH, body)
                self.assert_unavailable(result)
                self.assertIn(named, result.error)
                stated = xp_table.xp_for_level(result, 2.5)
                self.assert_refused(stated, "unmeasurable", "xp_table_unavailable")

    def test_L7_duplicate_levels_or_non_increasing_xp(self):
        duplicate = json.dumps(
            {
                "meta": {},
                "levels": [
                    {"level": 0, "experience": 0},
                    {"level": 1, "experience": 100},
                    {"level": 1, "experience": 200},
                ],
            },
        ).encode("utf-8")
        for body in (fixture("not_increasing.json"), duplicate, table_bytes([0, 100, 100])):
            with self.subTest(size=len(body)):
                server = self.serve(reply(body))
                self.assert_unavailable(self.fetch(server.url + PATH, body))

    def test_L8_single_level_table(self):
        body = table_bytes([0])
        server = self.serve(reply(body))
        self.assert_unavailable(self.fetch(server.url + PATH, body))

    def test_L9_network_cut_without_cache(self):
        result = self.fetch(self.dead_url, fixture("valid.json"))
        self.assert_unavailable(result)
        stated = xp_table.xp_for_level(result, 2.5)
        self.assert_refused(stated, "unmeasurable", "xp_table_unavailable")
        inverse = xp_table.level_for_xp(result, 450)
        self.assert_refused(inverse, "unmeasurable", "xp_table_unavailable")

    def test_L10_http_404_and_redirect_to_another_host(self):
        body = fixture("valid.json")
        server = self.serve(Reply(status=404, body=b"not found"))
        missing = self.fetch(server.url + PATH, body)
        self.assert_unavailable(missing)
        self.assertIn("404", missing.error)
        elsewhere = FakeServer()
        self.addCleanup(elsewhere.close)
        elsewhere.route(PATH, reply(body))
        location = (("Location", elsewhere.url + PATH),)
        server.route(PATH, Reply(status=302, headers=location))
        moved = self.fetch(server.url + PATH, body)
        self.assert_unavailable(moved)
        self.assertIn("302", moved.error)
        self.assertEqual(elsewhere.requests(), [])

    def test_L11_corrupted_cache_or_cache_of_another_hash(self):
        self.loaded()
        other = fixture("not_increasing.json")
        for content in (b"", b"{not json", other):
            with self.subTest(size=len(content)):
                self.cache.write_bytes(content)
                result = self.fetch(self.dead_url, fixture("valid.json"))
                self.assertEqual(result.status, "unavailable", result.error)
                self.assertIsNone(result.table)
                self.assertIn(str(self.cache), result.error)
        self.loaded()
        different_pin = self.fetch(self.dead_url, other)
        self.assertEqual(different_pin.status, "unavailable", different_pin.error)

    def test_L12_response_too_large(self):
        body = table_bytes([0, 100, 300], padding=5000)
        limit = 2000
        for length in (True, False):
            with self.subTest(length=length):
                server = self.serve(reply(body, length=length))
                result = self.fetch(server.url + PATH, body, max_bytes=limit)
                self.assert_unavailable(result)
                self.assertIn(str(limit), result.error)
        server = self.serve(reply(body))
        self.assertEqual(self.fetch(server.url + PATH, body, max_bytes=20000).status, "ok")


if __name__ == "__main__":
    unittest.main()
