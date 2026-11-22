"""Tests de `system_sync.sources.atomic_file` (correction T5.d, défaut I2).

Contrat : `write_atomic(path, data) -> str | None`. `path` est un `str` ou un `Path`,
`data` des octets. Crée le dossier parent, écrit dans un temporaire du même dossier en
0600, `fsync`, puis `os.replace`. Rend `None` en cas de succès, sinon un texte qui nomme
le chemin et la cause (`strerror`). Ne lève jamais, ne laisse aucun temporaire, laisse
l'ancien fichier intact si l'écriture échoue, remplace un lien symbolique sans toucher à
sa cible.
"""

import errno
import os
import stat
import tempfile
import unittest
from pathlib import Path

try:
    from system_sync.sources import atomic_file
except ImportError:
    atomic_file = None  # chaque test échoue dans `setUp` tant que le module manque


class WriteAtomic(unittest.TestCase):
    def setUp(self):
        if atomic_file is None:
            self.fail("module system_sync.sources.atomic_file absent")
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        self.target = self.root / "out" / "file.json"

    def names(self, folder):
        return sorted(item.name for item in folder.iterdir())

    def test_success_creates_folder_and_writes_bytes(self):
        self.assertIsNone(atomic_file.write_atomic(self.target, b"abc"))
        self.assertEqual(self.target.read_bytes(), b"abc")
        self.assertEqual(self.names(self.target.parent), ["file.json"])

    def test_accepts_a_str_path(self):
        self.assertIsNone(atomic_file.write_atomic(str(self.target), b"x"))
        self.assertEqual(self.target.read_bytes(), b"x")

    def test_file_mode_is_0600(self):
        atomic_file.write_atomic(self.target, b"x")
        self.assertEqual(stat.S_IMODE(self.target.stat().st_mode), 0o600)

    def test_replaces_an_existing_file(self):
        atomic_file.write_atomic(self.target, b"old")
        self.assertIsNone(atomic_file.write_atomic(self.target, b"new"))
        self.assertEqual(self.target.read_bytes(), b"new")
        self.assertEqual(self.names(self.target.parent), ["file.json"])

    def test_symlink_target_is_replaced_and_its_destination_untouched(self):
        elsewhere = self.root / "elsewhere.txt"
        elsewhere.write_bytes(b"keep")
        self.target.parent.mkdir()
        self.target.symlink_to(elsewhere)
        self.assertIsNone(atomic_file.write_atomic(self.target, b"new"))
        self.assertFalse(self.target.is_symlink())
        self.assertEqual(self.target.read_bytes(), b"new")
        self.assertEqual(elsewhere.read_bytes(), b"keep")

    def test_invalid_paths_do_not_raise(self):
        for bad in (None, "a\0b", 42):
            with self.subTest(path=repr(bad)):
                result = atomic_file.write_atomic(bad, b"x")
                self.assertIsInstance(result, str)
                self.assertTrue(result)

    def test_data_that_is_not_bytes_returns_text_and_keeps_old_file(self):
        atomic_file.write_atomic(self.target, b"old")
        result = atomic_file.write_atomic(self.target, "text")
        self.assertIsInstance(result, str)
        self.assertEqual(self.target.read_bytes(), b"old")
        self.assertEqual(self.names(self.target.parent), ["file.json"])

    def test_target_that_is_a_folder_names_path_and_cause(self):
        self.target.mkdir(parents=True)
        result = atomic_file.write_atomic(self.target, b"x")
        self.assertIsInstance(result, str)
        self.assertIn(str(self.target), result)
        self.assertIn(os.strerror(errno.EISDIR), result)
        self.assertTrue(self.target.is_dir())
        self.assertEqual(self.names(self.target.parent), ["file.json"])

    def test_unwritable_folder_names_path_and_cause_and_leaves_nothing(self):
        if os.geteuid() == 0:
            self.skipTest("root écrit dans un dossier en lecture seule")
        folder = self.root / "locked"
        folder.mkdir()
        target = folder / "file.json"
        target.write_bytes(b"old")
        folder.chmod(0o500)
        self.addCleanup(folder.chmod, 0o700)
        result = atomic_file.write_atomic(target, b"new")
        self.assertIsInstance(result, str)
        self.assertIn(str(target), result)
        self.assertIn(os.strerror(errno.EACCES), result)
        self.assertEqual(target.read_bytes(), b"old")
        self.assertEqual(self.names(folder), ["file.json"])


if __name__ == "__main__":
    unittest.main()
