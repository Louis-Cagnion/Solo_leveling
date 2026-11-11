"""Tests d'architecture de T1 (cas N8 à N13 et critères 2 et 9)."""

import ast
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGE = ROOT / "source" / "system_sync"
MAX_LINE = 95
MAX_LINES = 750
LOCAL_ROOTS = {"system_sync", "tests"}
EM_DASH = chr(0x2014)


def require_package():
    """Échoue si `source/system_sync/` est absent (jamais de succès vide)."""
    if not PACKAGE.is_dir():
        raise AssertionError(f"dossier absent : {PACKAGE}")


def python_files(*bases):
    """Renvoie les fichiers `.py` sous les dossiers donnés, triés."""
    found = []
    for base in bases:
        found.extend((ROOT / base).rglob("*.py"))
    return sorted(found)


def imported_modules(path):
    """Renvoie les (module, niveau relatif) importés par un fichier."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.extend((alias.name, 0) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            found.append((node.module or "", node.level))
    return found


class ArchitectureTest(unittest.TestCase):
    def test_T1_N8_stdlib_imports_only(self):
        require_package()
        files = python_files("source", "tests")
        self.assertGreater(len(files), 3)
        foreign = []
        for path in files:
            for module, level in imported_modules(path):
                top = module.split(".")[0]
                if level == 0 and top not in sys.stdlib_module_names | LOCAL_ROOTS:
                    foreign.append(f"{path.relative_to(ROOT)}: {module}")
        self.assertEqual(foreign, [])

    def test_T1_N9_rules_never_import_sources(self):
        require_package()
        rules_dir = PACKAGE / "rules"
        self.assertTrue(rules_dir.is_dir(), f"dossier absent : {rules_dir}")
        offenders = []
        for path in sorted(rules_dir.rglob("*.py")):
            for module, level in imported_modules(path):
                if re.search(r"(^|\.)sources(\.|$)", module):
                    offenders.append(f"{path.name}: {module}")
        self.assertEqual(offenders, [])

    def test_T1_N10_no_line_over_95_characters(self):
        require_package()
        checked = 0
        long_lines = []
        for base in ("source", "tests", "config"):
            for suffix in ("*.py", "*.toml"):
                for path in (ROOT / base).rglob(suffix):
                    checked += 1
                    text = path.read_text(encoding="utf-8")
                    for number, line in enumerate(text.splitlines(), 1):
                        if len(line) > MAX_LINE:
                            long_lines.append(f"{path}:{number}")
        self.assertGreater(checked, 3)
        self.assertEqual(long_lines, [])

    def test_T1_N11_no_file_over_750_lines(self):
        require_package()
        files = python_files("source", "tests")
        self.assertGreater(len(files), 3)
        big = []
        for path in files:
            count = len(path.read_text(encoding="utf-8").splitlines())
            if count > MAX_LINES:
                big.append(f"{path}: {count}")
        self.assertEqual(big, [])

    def test_T1_N12_no_em_dash(self):
        require_package()
        targets = [ROOT / "source", ROOT / "tests", ROOT / "config"]
        files = [ROOT / "README.md", ROOT / ".env.example"]
        for base in targets:
            files.extend(p for p in base.rglob("*") if p.is_file())
        found = []
        for path in files:
            if path.suffix == ".pyc":
                continue
            text = path.read_text(encoding="utf-8")
            if EM_DASH in text:
                found.append(str(path))
        self.assertEqual(found, [])

    def test_T1_N13_gitignore_conforms(self):
        lines = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        for required in (".env", "data/", "__pycache__/"):
            self.assertIn(required, lines)
        self.assertEqual([ln for ln in lines if re.match(r"^/?tests", ln)], [])

    def test_T1_criterion2_packages_importable(self):
        require_package()
        env = dict(os.environ, PYTHONPATH=str(ROOT / "source"))
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import system_sync, system_sync.sources, system_sync.rules",
            ],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_T1_criterion9_readme_up_to_date(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertNotIn("aucune maquette ni ligne de code", text)


if __name__ == "__main__":
    unittest.main()
