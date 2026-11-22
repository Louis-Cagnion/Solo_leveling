"""Test de la table XP réelle épinglée (T5, critère 2), sur le réseau.

Ignoré sans `SYNC_TEST_NETWORK=1`. Il télécharge le fichier de `config/rules.toml` et
ne le recopie nulle part : le cache va dans un dossier temporaire supprimé ensuite. Il
utilise l'interface décrite dans l'en-tête de `test_xp_table.py`.
"""

import os
import tempfile
import unittest
from pathlib import Path

from system_sync import config

try:
    from system_sync.sources import xp_table
except ImportError:
    xp_table = None  # le test échoue tant que le module manque

RULES = Path(__file__).resolve().parents[3] / "config" / "rules.toml"


@unittest.skipUnless(os.environ.get("SYNC_TEST_NETWORK") == "1", "SYNC_TEST_NETWORK absent")
class RealTableTest(unittest.TestCase):
    """Table réelle de 42calculator, épinglée par URL, commit et sha256."""

    def test_pinned_real_table(self):
        if xp_table is None:
            self.fail("module system_sync.sources.xp_table absent")
        pinned = config.load_rules(RULES)["xp_table"]
        with tempfile.TemporaryDirectory() as folder:
            result = xp_table.load_xp_table(
                pinned["url"],
                pinned["commit"],
                pinned["sha256"],
                Path(folder) / "cache" / "xp_table.json",
                timeout=20.0,
            )
        self.assertEqual(result.status, "ok", result.error)
        self.assertEqual(result.table.sha256, pinned["sha256"])
        self.assertEqual(len(result.table.levels), 31)
        self.assertEqual(xp_table.xp_for_level(result, 12).value, 124446)
        self.assertEqual(xp_table.xp_for_level(result, 25).value, 777756)
        interpolated = xp_table.xp_for_level(result, 12.44)
        self.assertEqual(interpolated.status, "estimated")
        self.assertEqual(interpolated.value, 133834)


if __name__ == "__main__":
    unittest.main()
