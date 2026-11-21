"""Tests du workflow de déploiement `pages.yml` (cas W1 à W5 de la fiche W1, W6 de W9)."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
WORKFLOW = ROOT / ".github" / "workflows" / "pages.yml"
PINNED_USES = re.compile(r"^[^\s@]+@[0-9a-f]{40}\s+#\s*\S+")
FIXTURES = ROOT / "tests" / "fixtures" / "workflow"
EXPECTED_PERMISSIONS = {"contents": "read", "pages": "write", "id-token": "write"}
EXPECTED_TRIGGERS = {"push", "workflow_dispatch"}
FORBIDDEN_IN_CODE = re.compile(r"\bsecrets\.|\$\{\{\s*github\.event")
RUN_STEP = re.compile(r"^\s*(-\s+)?run:")
INDENTED_PERMISSIONS = re.compile(r"^\s+permissions:")


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


def permission_problems(text):
    """Problèmes de droits : `permissions:` indenté, ou bloc racine différent."""
    lines = text.splitlines()
    problems = [
        f"permissions indenté : {line.strip()}"
        for line in lines
        if INDENTED_PERMISSIONS.match(line)
    ]
    try:
        found = key_values(block_after(lines, "permissions:", 0))
    except AssertionError as error:
        return problems + [str(error)]
    if found != EXPECTED_PERMISSIONS:
        problems.append(f"permissions racine inattendues : {found}")
    return problems


def trigger_problems(text):
    """Problèmes de déclencheurs : clés de `on:` autres que `push`, `workflow_dispatch`."""
    try:
        block = block_after(text.splitlines(), "on:", 0)
    except AssertionError as error:
        return [str(error)]
    keys = set()
    for line in block:
        content = line.split(" #")[0].rstrip()
        if content.strip() and not content.lstrip().startswith("#"):
            if len(content) - len(content.lstrip()) == 2 and ":" in content:
                keys.add(content.strip().partition(":")[0])
    if keys != EXPECTED_TRIGGERS:
        return [f"déclencheurs inattendus : {sorted(keys)}"]
    return []


def injection_problems(text):
    """Problèmes d'injection : `run:`, `secrets.` ou `github.event` hors commentaire."""
    problems = []
    for number, line in enumerate(text.splitlines(), start=1):
        code = "" if line.lstrip().startswith("#") else line.split(" #")[0]
        if RUN_STEP.match(code):
            problems.append(f"ligne {number} : étape run:")
        if FORBIDDEN_IN_CODE.search(code):
            problems.append(f"ligne {number} : secrets. ou github.event")
    return problems


CHECKS = {
    "permissions_tache.yml": permission_problems,
    "declencheur_pr_target.yml": trigger_problems,
    "injection_run.yml": injection_problems,
}


class WorkflowTest(unittest.TestCase):
    """Constats sur le texte de `.github/workflows/pages.yml`."""

    def test_W1(self):
        uses = [
            line.split("uses:", 1)[1].strip()
            for line in workflow_text().splitlines()
            if re.match(r"^\s*(-\s+)?uses:", line)
        ]
        self.assertTrue(uses, "aucune ligne uses:")
        self.assertEqual(injection_problems(workflow_text()), [])
        for value in uses:
            with self.subTest(uses=value):
                self.assertRegex(value, PINNED_USES)

    def test_W2(self):
        lines = workflow_text().splitlines()
        permissions = key_values(block_after(lines, "permissions:", 0))
        self.assertEqual(permissions, EXPECTED_PERMISSIONS)
        self.assertEqual(permission_problems(workflow_text()), [])

    def test_W3(self):
        lines = workflow_text().splitlines()
        triggers = block_after(lines, "on:", 0)
        keys = key_values(triggers)
        self.assertIn("workflow_dispatch", keys)
        self.assertIn("push", keys)
        self.assertEqual(trigger_problems(workflow_text()), [])
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

    def test_W6(self):
        conforme = (FIXTURES / "conforme.yml").read_text(encoding="utf-8")
        for check in (permission_problems, trigger_problems, injection_problems):
            with self.subTest(conforme=check.__name__):
                self.assertEqual(check(conforme), [])
        for name, check in CHECKS.items():
            text = (FIXTURES / name).read_text(encoding="utf-8")
            with self.subTest(fautif=name):
                self.assertTrue(check(text), f"{name} : rien vu par {check.__name__}")


if __name__ == "__main__":
    unittest.main()
