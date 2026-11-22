"""Tests du renvoi des écrans tactiles vers `unsupported.html` (cas G1 à G4)."""

import json
import shutil
import subprocess
import unittest
from pathlib import Path

from tests.public.test_site_static import PUBLIC, parse_page, read

GATE = PUBLIC / "js" / "device-gate.js"
GATED_PAGES = ("index.html", "network.html")
SITE_ADDRESS = "louis-cagnion.github.io/Solo_leveling/"
DEVICES = {
    "phone": {"pointer": "coarse", "hover": "none", "redirected": True},
    "tablet": {"pointer": "coarse", "hover": "none", "redirected": True},
    "desktop": {"pointer": "fine", "hover": "hover", "redirected": False},
    "touch laptop": {"pointer": "fine", "hover": "hover", "redirected": False},
    "hybrid with a mouse": {"pointer": "coarse", "hover": "hover", "redirected": False},
}
# Joue le script en contexte isolé ; `matchMedia` y évalue des clauses `(trait: valeur)`.
HARNESS = """
const fs = require('fs');
const vm = require('vm');
const source = fs.readFileSync(process.argv[1], 'utf8');
const cases = JSON.parse(process.argv[2]);

function run(device) {
  const replaced = [];
  const window = {location: {replace: url => replaced.push(url)}};
  if (device) {
    window.matchMedia = query => ({
      matches: query.split(' and ').every(clause => {
        const [feature, value] = clause.replace(/[()]/g, '').split(':').map(s => s.trim());
        return device[feature] === value;
      }),
    });
  }
  vm.runInNewContext(source, {window});
  return replaced;
}

const result = {};
for (const [name, device] of Object.entries(cases)) result[name] = run(device);
result['no matchMedia'] = run(null);
console.log(JSON.stringify(result));
"""


def play_gate():
    """Redirections demandées par le script pour chaque appareil, plus un navigateur sans
    `matchMedia` ; échoue si le script est absent ou plante."""
    if not GATE.is_file():
        raise AssertionError(f"fichier absent : {GATE}")
    cases = {name: {k: v for k, v in device.items() if k != "redirected"}
             for name, device in DEVICES.items()}
    done = subprocess.run(
        ["node", "-e", HARNESS, str(GATE), json.dumps(cases)],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if done.returncode != 0:
        raise AssertionError(f"le script plante : {done.stderr.strip()}")
    return json.loads(done.stdout)


class DeviceGateTest(unittest.TestCase):
    """Constats sur `js/device-gate.js`, `unsupported.html` et leur câblage."""

    def test_G1_pages_load_the_gate_first(self):
        for name in GATED_PAGES:
            with self.subTest(page=name):
                scripts = [
                    attrs
                    for tag, attrs in parse_page(name).tags
                    if tag == "script" and "src" in attrs
                ]
                self.assertEqual(scripts[0].get("src"), "js/device-gate.js")
                self.assertIn("defer", scripts[0])

    @unittest.skipUnless(shutil.which("node"), "node absent : cas G2 non joué")
    def test_G2_touch_only_screens_are_redirected(self):
        result = play_gate()
        for name, device in DEVICES.items():
            with self.subTest(device=name):
                expected = ["unsupported.html"] if device["redirected"] else []
                self.assertEqual(result[name], expected)

    @unittest.skipUnless(shutil.which("node"), "node absent : cas G3 non joué")
    def test_G3_browser_without_match_media_is_left_alone(self):
        self.assertEqual(play_gate()["no matchMedia"], [])

    def test_G4_unsupported_page_says_computer_only(self):
        page = parse_page("unsupported.html")
        self.assertIn("ordinateur", read("unsupported.html"))
        self.assertTrue(page.title.strip())
        names = [tag for tag, _ in page.tags]
        self.assertNotIn("script", names)
        self.assertEqual(names.count("h1"), 1)

    def test_G5_unsupported_page_names_the_accessible_address(self):
        self.assertIn(SITE_ADDRESS, read("unsupported.html").replace("<wbr>", ""))


if __name__ == "__main__":
    unittest.main()
