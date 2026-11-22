"""Tests de la correction T5.d (revue de `xp_table`, défauts I1 et I2).

I1 : aucune fonction publique ne lève sur un chemin de cache `None` ou à octet NUL, ni
sur un niveau ou une XP entière trop grande pour un float.
I2 : l'écriture atomique vit dans `atomic_file` seul, plus de `mkstemp(` ni de
`os.replace(` dans `xp_table*.py` ni dans `api42_cache.py`.
"""

import tempfile
import unittest
from pathlib import Path

from system_sync.sources import api42_profile
from tests.system_sync.sources.fake_server import (
    HOST,
    FakeServer,
    NetworkGuard,
    Reply,
    free_port,
)
from tests.system_sync.sources.test_xp_table import (
    COMMIT,
    PATH,
    fixture,
    pin,
)

try:
    from system_sync.sources import xp_table
except ImportError:
    xp_table = None

SOURCES = Path(__file__).resolve().parents[3] / "source" / "system_sync" / "sources"
HUGE = 10**400
GUARD = NetworkGuard()


def setUpModule():
    GUARD.start()


def tearDownModule():
    GUARD.stop()


class HugeNumbers(unittest.TestCase):
    def test_is_number_rejects_an_int_too_big_for_a_float(self):
        self.assertFalse(api42_profile.is_number(HUGE))
        self.assertFalse(api42_profile.is_number(-HUGE))

    def test_is_number_guards_stay_as_they_were(self):
        self.assertTrue(api42_profile.is_number(10**308))
        self.assertFalse(api42_profile.is_number(True))

    def loaded(self):
        body = fixture("valid.json")
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        server = FakeServer()
        self.addCleanup(server.close)
        server.route(PATH, Reply(body=body))
        return xp_table.load_xp_table(
            server.url + PATH,
            COMMIT,
            pin(body),
            Path(folder.name) / "c.json",
            timeout=2.0,
        )

    def test_xp_for_level_with_a_huge_level_is_unmeasurable(self):
        result = self.loaded()
        for level in (HUGE, -HUGE):
            with self.subTest(level=level > 0):
                value = xp_table.xp_for_level(result, level)
                self.assertEqual(value.status, "unmeasurable")
                self.assertEqual(value.reason_code, "level_invalid")

    def test_level_for_xp_with_a_huge_xp_is_unmeasurable(self):
        value = xp_table.level_for_xp(self.loaded(), HUGE)
        self.assertEqual(value.status, "unmeasurable")
        self.assertEqual(value.reason_code, "xp_invalid")


class BadCachePath(unittest.TestCase):
    def setUp(self):
        GUARD.outside.clear()
        self.body = fixture("valid.json")

    def tearDown(self):
        self.assertEqual(GUARD.outside, [])

    def test_cache_path_none_gives_unavailable_naming_the_cache(self):
        dead = f"http://{HOST}:{free_port()}{PATH}"
        result = xp_table.load_xp_table(dead, COMMIT, pin(self.body), None, timeout=2.0)
        self.assertEqual(result.status, "unavailable")
        self.assertIn("cache", result.error.lower())

    def test_cache_path_with_nul_and_network_ok_gives_ok_naming_the_cache(self):
        server = FakeServer()
        self.addCleanup(server.close)
        server.route(PATH, Reply(body=self.body))
        result = xp_table.load_xp_table(
            server.url + PATH,
            COMMIT,
            pin(self.body),
            "a\0b",
            timeout=2.0,
        )
        self.assertEqual(result.status, "ok")
        self.assertIn("cache", result.error.lower())

    def test_cache_path_with_nul_and_network_cut_gives_unavailable(self):
        dead = f"http://{HOST}:{free_port()}{PATH}"
        result = xp_table.load_xp_table(
            dead,
            COMMIT,
            pin(self.body),
            "a\0b",
            timeout=2.0,
        )
        self.assertEqual(result.status, "unavailable")
        self.assertTrue(result.error)


class SharedAtomicWrite(unittest.TestCase):
    def test_only_atomic_file_holds_mkstemp_and_replace(self):
        files = sorted(SOURCES.glob("xp_table*.py")) + [SOURCES / "api42_cache.py"]
        self.assertTrue(all(path.exists() for path in files))
        for path in files:
            text = path.read_text(encoding="utf-8")
            for needle in ("mkstemp(", "os.replace("):
                with self.subTest(file=path.name, needle=needle):
                    self.assertNotIn(needle, text)
        shared = SOURCES / "atomic_file.py"
        self.assertTrue(shared.exists(), "atomic_file.py absent")
        text = shared.read_text(encoding="utf-8")
        self.assertIn("mkstemp(", text)
        self.assertIn("os.replace(", text)


if __name__ == "__main__":
    unittest.main()
