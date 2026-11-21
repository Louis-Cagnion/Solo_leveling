"""Tests de `tools/snapshot.py` (cas N1 à N4, L1, L2 et Q1 de la fiche W1)."""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = ROOT / "tools" / "snapshot.py"
FIXTURE = ROOT / "tests" / "fixtures" / "snapshot"
PREFIX = "window.SYSTEME = "
MAX_LINE = 95
MAX_LINES = 750
TIMEOUT = 60


def run_snapshot(suivi, output):
    """Lance `python3 -I tools/snapshot.py --suivi <suivi> --output <output>`."""
    return subprocess.run(
        [sys.executable, "-I", str(SCRIPT), "--suivi", str(suivi), "--output", str(output)],
        capture_output=True,
        text=True,
        timeout=TIMEOUT,
    )


def load_output(path):
    """Renvoie le JSON de `window.SYSTEME` écrit dans ce fichier."""
    text = Path(path).read_text(encoding="utf-8")
    assert text.startswith(PREFIX), f"préfixe attendu {PREFIX!r}"
    return json.loads(text[len(PREFIX):].strip().removesuffix(";"))


def sha256(path):
    """Empreinte sha256 d'un fichier."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class SnapshotTest(unittest.TestCase):
    """Génération de l'instantané depuis le suivi fictif."""

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.tmp = Path(directory.name)
        self.output = self.tmp / "out" / "data.js"
        self.output.parent.mkdir()

    def generate(self, output=None):
        """Génère sur la fixture et exige le code 0."""
        result = run_snapshot(FIXTURE, output or self.output)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def test_N1(self):
        self.generate()
        data = load_output(self.output)
        self.assertEqual(data["counts"]["cards"], 2)

    def test_N2(self):
        self.generate()
        text = self.output.read_text(encoding="utf-8")
        for path in (FIXTURE, FIXTURE.resolve()):
            self.assertNotIn(str(path), text)

    def test_N3(self):
        second = self.tmp / "out" / "second.js"
        self.generate()
        self.generate(second)
        first_data = load_output(self.output)
        second_data = load_output(second)
        for data in (first_data, second_data):
            self.assertIn("generatedAt", data["meta"])
            del data["meta"]["generatedAt"]
        self.assertEqual(first_data, second_data)

    def test_N4(self):
        self.generate()
        data = load_output(self.output)
        self.assertEqual(data["counts"]["relationsRejected"], 1)
        rejected = [item for item in data["anomalies"] if item["rejected"]]
        self.assertTrue(any(item["file"] == "relations.csv" for item in rejected))

    def test_L1(self):
        missing = self.tmp / "suivi-absent"
        self.output.write_text("ancien contenu\n", encoding="utf-8")
        before = sha256(self.output)
        result = run_snapshot(missing, self.output)
        self.assertEqual(result.returncode, 1)
        self.assertIn(str(missing), result.stderr)
        self.assertEqual(sha256(self.output), before)

    @unittest.skipIf(os.geteuid() == 0, "root ignore les droits d'écriture")
    def test_L2(self):
        locked = self.tmp / "verrouille"
        locked.mkdir()
        locked.chmod(0o500)
        self.addCleanup(locked.chmod, 0o700)
        result = run_snapshot(FIXTURE, locked / "data.js")
        self.assertEqual(result.returncode, 1)
        self.assertTrue(result.stderr.strip(), "message attendu sur stderr")
        self.assertNotIn("Traceback", result.stderr)

    def test_Q1(self):
        self.assertTrue(SCRIPT.is_file(), f"fichier absent : {SCRIPT}")
        lines = SCRIPT.read_text(encoding="utf-8").split("\n")
        too_long = [
            number
            for number, line in enumerate(lines, start=1)
            if len(line) > MAX_LINE
        ]
        self.assertEqual(too_long, [])
        self.assertLessEqual(len(SCRIPT.read_text(encoding="utf-8").splitlines()), MAX_LINES)


if __name__ == "__main__":
    unittest.main()
