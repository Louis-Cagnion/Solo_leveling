"""Tests du workflow de déploiement `pages.yml` (cas W1 à W5 de la fiche W1)."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
WORKFLOW = ROOT / ".github" / "workflows" / "pages.yml"
PINNED_USES = re.compile(r"^[^\s@]+@[0-9a-f]{40}\s+#\s*\S+")
EXPECTED_PERMISSIONS = {"contents": "read", "pages": "write", "id-token": "write"}


def workflow_text():
    """Lit `pages.yml` ; échoue s'il est absent."""
    if not WORKFLOW.is_file():
        raise AssertionError(f"fichier absent : {WORKFLOW}")
    return WORKFLOW.read_text(encoding="utf-8")


def block_after(lines, header, indent):
    """Lignes indentées sous la première ligne `header` (clé de YAML) ; échoue sinon."""
    for index, line in enumerate(lines):
        if line.rstrip() == header or line.startswith(header + " "):
            block = []
            for following in lines[index + 1:]:
                if following.strip() and len(following) - len(following.lstrip()) <= indent:
                    break
                block.append(following)
            return block
    raise AssertionError(f"clé absente : {header!r}")


def key_values(block):
    """Paires `clé: valeur` des lignes d'un bloc, commentaires retirés."""
    pairs = {}
    for line in block:
        content = line.split(" #")[0].strip()
        if ":" in content and not content.startswith("-"):
            key, _, value = content.partition(":")
            pairs[key.strip()] = value.strip()
    return pairs


class WorkflowTest(unittest.TestCase):
    """Constats sur le texte de `.github/workflows/pages.yml`."""

    def test_W1(self):
        uses = [
            line.split("uses:", 1)[1].strip()
            for line in workflow_text().splitlines()
            if re.match(r"^\s*(-\s+)?uses:", line)
        ]
        self.assertTrue(uses, "aucune ligne uses:")
        for value in uses:
            with self.subTest(uses=value):
                self.assertRegex(value, PINNED_USES)

    def test_W2(self):
        lines = workflow_text().splitlines()
        permissions = key_values(block_after(lines, "permissions:", 0))
        self.assertEqual(permissions, EXPECTED_PERMISSIONS)

    def test_W3(self):
        lines = workflow_text().splitlines()
        triggers = block_after(lines, "on:", 0)
        keys = key_values(triggers)
        self.assertIn("workflow_dispatch", keys)
        self.assertIn("push", keys)
        push = block_after(triggers, "  push:", 2)
        self.assertRegex("\n".join(push), r"branches:\s*\[\s*main\s*\]|-\s+main\b")
        paths = block_after(push, "    paths:", 4)
        listed = [line.strip().removeprefix("- ").strip("'\"") for line in paths]
        listed = [item for item in listed if item]
        self.assertEqual(
            sorted(listed),
            [".github/workflows/pages.yml", "public/**"],
        )

    def test_W4(self):
        text = workflow_text()
        self.assertRegex(text, r"upload-pages-artifact@")
        self.assertRegex(text, r"(?m)^\s*path:\s*['\"]?public['\"]?\s*$")

    def test_W5(self):
        self.assertRegex(workflow_text(), r"(?m)^\s*timeout-minutes:\s*\d+\s*$")


if __name__ == "__main__":
    unittest.main()
