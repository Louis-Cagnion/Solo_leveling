"""Tests rouges de T10 : commande `sync` (`source/system_sync/sync.py`, pas encore écrit).

Contrat testé (fiche `docs/design/implementation.md:596-633`, arbitrages A1 à A31) :
- `sync.run_sync(argv, *, open_browser=None, api_base=None, rules_path=None,
  xp_loader=None) -> int` reçoit les options APRÈS `sync` (`--env CHEMIN`,
  `--sortie CHEMIN`) et rend le code de sortie : 0, 1 (échec de configuration, de règles ou
  d'écriture), 2 (option invalide). Les paramètres nommés ne servent qu'aux tests
  (`None` : `webbrowser.open`, `API_BASE`, `config/rules.toml` du dépôt, trouvé depuis le
  fichier du module, non le dossier courant ;
  `xp_loader` : appelable de la signature de `load_xp_table`, `None` pour le vrai).
- `python3 -m system_sync` sans sous-commande ou avec une inconnue : usage, code 2.
- Sortie par défaut `<dépôt>/data/state.js` ; le cache (`cache/api42.json`,
  `cache/xp_table.json`) et la trajectoire (`history/`, une ligne par synchronisation)
  vivent dans le dossier de la sortie.
- Le journal (`AAAA-MM-JJ HH:MM:SS ... NIVEAU ...`) va sur l'erreur standard, avec un
  gestionnaire créé à chaque appel ; l'entité `names` écrite vaut `{"en": {}}`.
Aucun test ne touche le réseau réel, `data/` ni le vrai suivi de `/professor`.
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest import mock

from system_sync import output
from system_sync.sources.xp_table import (
    DEFAULT_MAX_BYTES,
    DEFAULT_TIMEOUT,
    XpTable,
    XpTableResult,
)
from tests.system_sync.sources.fake_server import (
    Browser,
    Capture,
    FakeServer,
    NetworkGuard,
    free_port,
    json_reply,
    load,
)

try:
    from system_sync import sync
except ImportError:
    sync = None  # chaque test échoue dans `setUp` tant que le module manque

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures"
SYNC_FIXTURES = FIXTURES / "sync"
XP_TABLE = FIXTURES / "xp_table" / "valid.json"
REAL_RULES = ROOT / "config" / "rules.toml"
COMMIT = "0123456789abcdef0123456789abcdef01234567"
XP_URL = f"https://example.invalid/42calculator/{COMMIT}/xp.json"
SECRET = "secret-fictif-sync-0123456789"
CODE = "fake-authorization-code-0123"
PREFIX = "window.SYSTEM_STATE = "
ENTITIES = {
    "meta", "sources", "level42", "system", "trajectory", "cards", "notions",
    "relations", "projects", "titles", "anomalies", "rules", "achievements", "names",
}
PROFESSOR_SOURCES = ("cards", "notions", "relations", "events", "history", "projects")
NOTION_IDS = {
    "alpha-loop", "alpha-array", "alpha-tree", "alpha-graph", "alpha-heap",
    "alpha-sort", "alpha-proof", "alpha-bound", "beta-one", "beta-two", "beta-three",
    "beta-four", "principes-revue",
}
JOURNAL_LINE = re.compile(r"^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\b.*\b(INFO|WARNING|ERROR)\b")
GUARD = NetworkGuard()


def setUpModule():
    GUARD.start()


def tearDownModule():
    GUARD.stop()


def read_state(path):
    """Lit `window.SYSTEM_STATE = {...};` et rend l'objet JSON."""
    text = Path(path).read_text(encoding="utf-8")
    assert text.startswith(PREFIX), text[:40]
    return json.loads(text[len(PREFIX):].rstrip().removesuffix(";"))


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def big_table(path):
    """Écrit une table XP fictive de 0 à 30 (XP = 100 n²), qui couvre le niveau 12,44."""
    levels = [
        {"level": n, "experience": 100 * n * n, "label": f"fictional level {n}"}
        for n in range(31)
    ]
    body = json.dumps({"meta": {"source": "fictional"}, "levels": levels}).encode()
    Path(path).write_bytes(body)


def table_loader(table_path):
    """Faux `load_xp_table` : rend la table de `table_path` en résultat `ok`, sans réseau."""
    body = Path(table_path).read_bytes()
    levels = tuple((n["level"], n["experience"]) for n in json.loads(body)["levels"])

    def load_xp_table(
        url,
        commit,
        sha256,
        cache_path,
        *,
        timeout=DEFAULT_TIMEOUT,
        max_bytes=DEFAULT_MAX_BYTES,
    ):
        table = XpTable(levels, url, commit, hashlib.sha256(body).hexdigest())
        return XpTableResult("ok", None, table)

    return load_xp_table


def unavailable_loader(
    url,
    commit,
    sha256,
    cache_path,
    *,
    timeout=DEFAULT_TIMEOUT,
    max_bytes=DEFAULT_MAX_BYTES,
):
    """Faux `load_xp_table` d'une table XP indisponible (réseau et cache en échec)."""
    return XpTableResult("unavailable", f"{url} : connexion impossible ; cache absent")


class SyncCase(unittest.TestCase):
    """Dossier temporaire, serveur factice, `rules.toml` de test et lanceur de `sync`."""

    def setUp(self):
        if sync is None:
            self.fail("module system_sync.sync absent")
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.out = self.tmp / "out" / "state.js"
        self.server = FakeServer()
        self.addCleanup(self.server.close)
        self.server.route("/oauth/token", json_reply(load("token.json")))
        self.server.route("/v2/me", json_reply(load("me_valid.json")))
        self.route_achievements()
        self.set_table(XP_TABLE)
        self.journal = ""

    def route_achievements(self):
        """Rejoue les deux pages des succès depuis la première (compteur remis à 0)."""
        self.server.route(
            "/v2/achievements",
            json_reply(load("achievements_page1.json")),
            json_reply(load("achievements_page2.json")),
        )

    def set_table(self, table_path):
        """Injecte `table_path` (jamais téléchargée) et écrit `rules.toml` qui l'épingle."""
        body = Path(table_path).read_bytes()
        self.xp_loader = table_loader(table_path)
        self.write_rules(hashlib.sha256(body).hexdigest())

    def write_rules(self, digest, anchor=True):
        """`rules.toml` du dépôt, table XP https et point d'ancrage de test remplacés."""
        text = REAL_RULES.read_text(encoding="utf-8")
        head, rest = text.split("[xp_table]", 1)
        tail = rest.split("[calibration]", 1)[1]
        table = (
            f'[xp_table]\nurl = "{XP_URL}"\n'
            f'commit = "{COMMIT}"\nsha256 = "{digest}"\n\n'
        )
        text = head + table + "[calibration]" + tail
        if anchor:
            text += (
                '\n[[calibration.anchors]]\ndate = "2026-01-01"\nxp_system = 400\n'
                "level = 2.0\nxp_42 = 400\n"
            )
        self.rules = self.tmp / "rules.toml"
        self.rules.write_text(text, encoding="utf-8")

    def env(self, name="valid.env", **changes):
        """Copie de `tests/fixtures/sync/<name>` en chemins absolus et port libre."""
        text = (SYNC_FIXTURES / name).read_text(encoding="utf-8")
        text = text.replace("tests/fixtures/", f"{FIXTURES}/")
        port = f"API42_CALLBACK_PORT={free_port()}"
        text = re.sub(r"(?m)^API42_CALLBACK_PORT=5611$", port, text)
        for key, value in changes.items():
            text = re.sub(f"(?m)^{key}=.*$", f"{key}={value}", text)
        path = self.tmp / f"{name}.copy.env"
        path.write_text(text, encoding="utf-8")
        return path

    def run_sync(self, env=None, out=None, rules=None, extra=()):
        """Lance `run_sync` en capturant le journal ; rend le code de sortie."""
        browser = Browser(CODE)
        argv = [
            "--env", str(env or self.env()),
            "--sortie", str(out or self.out),
            *extra,
        ]
        with Capture() as capture:
            code = sync.run_sync(
                argv,
                open_browser=browser,
                api_base=self.server.url,
                rules_path=rules or self.rules,
                xp_loader=self.xp_loader,
            )
            browser.join()
        self.stderr = capture.err.getvalue()
        self.journal += capture.text
        return code

    def state(self):
        return read_state(self.out)

    def sync_ok(self, **kwargs):
        """Lance `run_sync`, exige le code 0 et rend l'état écrit."""
        code = self.run_sync(**kwargs)
        self.assertEqual(code, 0, self.stderr)
        return self.state()


class NominalTest(SyncCase):
    """N1 à N10, critères 2 à 5 de la fiche."""

    def test_N1_complete_sync_writes_valid_state(self):
        state = self.sync_ok()
        self.assertEqual(output.validate(state), [])

    def test_N1_subprocess_exits_zero_without_network(self):
        guard = self.tmp / "guard"
        guard.mkdir()
        (guard / "sitecustomize.py").write_text(
            "import socket\n"
            "def refuse(*args, **kwargs):\n"
            "    raise OSError('réseau coupé par le test')\n"
            "socket.getaddrinfo = refuse\n",
            encoding="utf-8",
        )
        env = {
            **os.environ,
            "PYTHONPATH": os.pathsep.join([str(guard), str(ROOT / "source")]),
        }
        done = subprocess.run(
            [
                sys.executable, "-m", "system_sync", "sync",
                "--env", str(self.env("sans_api.env")),
                "--sortie", str(self.out),
            ],
            cwd=ROOT, env=env, capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(output.validate(self.state()), [])

    def test_N2_all_fourteen_entities_present(self):
        self.assertEqual(set(self.sync_ok()), ENTITIES)

    def test_N3_sources_carry_status_and_counters(self):
        by_name = {s["name"]: s for s in self.sync_ok()["sources"]}
        expected = {
            "cards": ("ok", 2, 0), "notions": ("ok", 6, 0), "relations": ("ok", 5, 1),
            "events": ("ok", 8, 0), "history": ("ok", 8, 1), "projects": ("absent", 0, 0),
        }
        for name, (status, read, rejected) in expected.items():
            got = by_name[name]
            self.assertEqual(
                (got["status"], got["lines_read"], got["lines_rejected"]),
                (status, read, rejected),
                name,
            )
        self.assertEqual(by_name["api42"]["status"], "ok")

    def test_N4_parser_anomalies_kept_with_file_and_line(self):
        found = {(a["file"], a["line"], a["kind"]) for a in self.sync_ok()["anomalies"]}
        for file, line, kind in (
            ("relations.csv", 4, "field_count"),
            ("historique-ia.csv", 7, "field_count"),
            ("historique-ia.csv", 8, "suspect_date"),
        ):
            self.assertIn((file, line, kind), found)

    def test_N5_meta_version_date_and_rules_fingerprint(self):
        meta = self.sync_ok()["meta"]
        self.assertEqual(meta["schema_version"], 1)
        self.assertRegex(meta["generated_at"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
        self.assertEqual(meta["rules_fingerprint"], sha256(self.rules))

    def test_N5_content_matches_the_fixtures(self):
        state = self.sync_ok()
        self.assertEqual({c["id"] for c in state["cards"]}, {"alpha", "beta"})
        self.assertEqual(set(state["notions"]), NOTION_IDS)
        states = {k: v["state"]["value"] for k, v in state["notions"].items()}
        self.assertEqual(states["alpha-loop"], "en cours")
        self.assertEqual(states["alpha-tree"], "déclarée")
        self.assertEqual(states["alpha-graph"], "non rencontrée")
        self.assertEqual(state["level42"]["level"]["value"], 12.44)
        self.assertEqual(state["level42"]["level"]["status"], "observed")
        self.assertEqual(state["names"], {"en": {}})
        self.assertEqual(state["rules"]["excluded_states"], ["déclarée"])
        self.assertEqual(state["rules"]["target_level"], 25)

    def test_N6_one_trajectory_line_per_synchronisation(self):
        big_table(self.tmp / "big.json")
        self.set_table(self.tmp / "big.json")
        for count in (1, 2):
            state = self.sync_ok()
            self.assertEqual(len(state["trajectory"]), count)
            lines = [
                line
                for path in (self.out.parent / "history").rglob("*")
                if path.is_file()
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual(len(lines), count)

    def test_N7_journal_has_timestamped_lines_and_volumes(self):
        self.sync_ok()
        lines = [x for x in self.stderr.splitlines() if JOURNAL_LINE.match(x)]
        self.assertGreaterEqual(len(lines), 8, self.stderr)
        for name in PROFESSOR_SOURCES:
            self.assertTrue(any(name in x for x in lines), name)
        self.assertTrue(any(re.search(r"\b5\b.*\b1\b", x) for x in lines if "relations" in x))

    def test_N8_no_secret_in_state_nor_journal(self):
        self.sync_ok()
        text = self.out.read_text(encoding="utf-8") + self.journal
        for secret in (SECRET, CODE, load("token.json")["access_token"]):
            self.assertNotIn(secret, text)

    def test_N9_two_runs_same_state_except_date_and_trajectory(self):
        first = self.sync_ok()
        self.route_achievements()
        second = self.sync_ok()
        for state in (first, second):
            del state["meta"]["generated_at"]
            del state["trajectory"]
        self.assertEqual(first, second)

    def test_N10_invalid_state_leaves_previous_file_byte_identical(self):
        self.sync_ok()
        before = sha256(self.out)
        with mock.patch("system_sync.output.validate", return_value=[("$", "forcé")]):
            code = self.run_sync()
        self.assertNotEqual(code, 0)
        self.assertEqual(sha256(self.out), before)
        self.assertEqual([p.name for p in self.out.parent.glob("*.tmp")], [])
        self.assertIn("forcé", self.stderr)

    def test_N10_interrupt_before_replace_keeps_previous_file(self):
        self.sync_ok()
        before = sha256(self.out)
        with mock.patch("os.replace", side_effect=KeyboardInterrupt):
            try:
                code = self.run_sync()
            except KeyboardInterrupt:
                code = None
        self.assertNotEqual(code, 0)
        self.assertEqual(sha256(self.out), before)
        self.assertEqual([p.name for p in self.out.parent.glob("*.tmp")], [])


class LimitTest(SyncCase):
    """L1 à L8 et points testables du pré-mortem."""

    def test_L1_env_missing_or_malformed_fails_without_writing(self):
        malformed = FIXTURES / "config" / "no_equals.env"
        for env in (self.tmp / "absent.env", malformed):
            with self.subTest(env=env.name):
                self.assertNotEqual(self.run_sync(env=env), 0)
                self.assertIn(env.name, self.stderr)
                self.assertFalse(self.out.parent.exists())

    def test_L2_professor_sources_unavailable_state_still_written(self):
        state = self.sync_ok(env=self.env("sans_regles.env"))
        by_name = {s["name"]: s["status"] for s in state["sources"]}
        for name in ("cards", "notions", "relations", "events", "history"):
            self.assertEqual(by_name[name], "unavailable", name)
        self.assertEqual(state["cards"], [])
        self.assertEqual(output.validate(state), [])

    def test_L3_api_down_with_cache_then_without_cache(self):
        self.sync_ok()
        cache = self.out.parent / "cache" / "api42.json"
        self.assertTrue(cache.is_file())
        cached = self.sync_ok(env=self.env("sans_api.env"))
        by_name = {s["name"]: s["status"] for s in cached["sources"]}
        self.assertEqual(by_name["api42"], "cache")
        self.assertEqual(cached["level42"]["level"]["value"], 12.44)
        self.assertNotIn(str(self.tmp), self.out.read_text(encoding="utf-8"))
        self.out = self.tmp / "other" / "state.js"
        bare = self.sync_ok(env=self.env("sans_api.env"))
        level = bare["level42"]["level"]
        self.assertEqual((level["status"], level["value"]), ("unmeasurable", None))
        self.assertTrue(level["reason"])
        self.assertNotIn(str(self.tmp), self.out.read_text(encoding="utf-8"))

    def test_L4_xp_table_unavailable_rest_of_state_written(self):
        self.xp_loader = unavailable_loader
        state = self.sync_ok()
        xp = state["level42"]["xp"]
        self.assertEqual((xp["status"], xp["value"]), ("unmeasurable", None))
        self.assertTrue(xp["reason"])
        self.assertEqual({c["id"] for c in state["cards"]}, {"alpha", "beta"})
        self.assertEqual(output.validate(state), [])

    def test_L5_invalid_rules_fail_before_any_read(self):
        bad = FIXTURES / "config" / "rules_malformed.toml"
        browser_calls = []
        with Capture() as capture:
            code = sync.run_sync(
                ["--env", str(self.env()), "--sortie", str(self.out)],
                open_browser=browser_calls.append,
                api_base=self.server.url,
                rules_path=bad,
            )
        self.assertNotEqual(code, 0)
        self.assertIn("rules_malformed.toml", capture.text)
        self.assertEqual(self.server.requests(), [])
        self.assertEqual(browser_calls, [])
        self.assertFalse(self.out.parent.exists())

    def test_L6_unwritable_output_names_the_strerror(self):
        blocker = self.tmp / "blocker"
        blocker.write_text("fichier ordinaire", encoding="utf-8")
        code = self.run_sync(out=blocker / "sub" / "state.js")
        self.assertNotEqual(code, 0)
        self.assertIn(os.strerror(20), self.stderr)
        self.assertIn("blocker", self.stderr)

    def test_L7_all_sources_empty_gives_valid_state(self):
        suivi = self.tmp / "suivi"
        (suivi / "cartes").mkdir(parents=True)
        (suivi / "notions.md").write_text("# État des notions\n", encoding="utf-8")
        for name, header in (
            ("relations.csv", "date,source,relation,cible,statut,limite,preuve"),
            (
                "evenements.csv",
                "date,session,domaine,notion,metrique,valeur,contexte,forme_visuelle,preuve",
            ),
        ):
            (suivi / name).write_text(header + "\n", encoding="utf-8")
        history = self.tmp / "history.csv"
        header = "date,projet,mode,domaine,notions,auteur,preuve\n"
        history.write_text(header, encoding="utf-8")
        env = self.env(PROFESSOR_SUIVI_DIR=suivi, IA_HISTORY_CSV=history)
        state = self.sync_ok(env=env)
        self.assertEqual(output.validate(state), [])
        self.assertEqual((state["cards"], state["notions"], state["relations"]), ([], {}, []))
        by_name = {s["name"]: s for s in state["sources"]}
        for name in ("relations", "events", "history"):
            self.assertEqual(by_name[name]["lines_read"], 0, name)

    def test_L8_missing_or_unknown_subcommand_prints_usage_code_2(self):
        env = {**os.environ, "PYTHONPATH": str(ROOT / "source")}
        for args in ([], ["inconnue"]):
            with self.subTest(args=args):
                done = subprocess.run(
                    [sys.executable, "-m", "system_sync", *args],
                    cwd=ROOT, env=env, capture_output=True, text=True, timeout=60,
                )
                self.assertEqual(done.returncode, 2)
                self.assertIn("sync", done.stderr + done.stdout)
                self.assertRegex((done.stderr + done.stdout).lower(), "usage|utilisation")

    def test_L8_unknown_option_returns_code_2(self):
        with Capture():
            self.assertEqual(sync.run_sync(["--inconnue"]), 2)

    def test_premortem_other_working_directory_relative_output(self):
        guard = self.tmp / "guard"
        guard.mkdir()
        (guard / "sitecustomize.py").write_text(
            "import socket\n"
            "def refuse(*args, **kwargs):\n"
            "    raise OSError('réseau coupé par le test')\n"
            "socket.getaddrinfo = refuse\n",
            encoding="utf-8",
        )
        elsewhere = self.tmp / "elsewhere"
        elsewhere.mkdir()
        env = {
            **os.environ,
            "PYTHONPATH": os.pathsep.join([str(guard), str(ROOT / "source")]),
        }
        done = subprocess.run(
            [
                sys.executable, "-m", "system_sync", "sync",
                "--env", str(self.env("sans_api.env")),
                "--sortie", "relative/state.js",
            ],
            cwd=elsewhere, env=env, capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(output.validate(read_state(elsewhere / "relative" / "state.js")), [])
        self.assertFalse((ROOT / "relative").exists())


class RealRulesTest(unittest.TestCase):
    """Critère 4 de T7 : `config/rules.toml` porte un premier point d'ancrage."""

    def test_real_rules_carry_a_first_anchor(self):
        rules = tomllib.loads(REAL_RULES.read_text(encoding="utf-8"))
        anchors = rules["calibration"].get("anchors", [])
        self.assertGreaterEqual(len(anchors), 1)
        for key in ("date", "xp_system", "level", "xp_42"):
            self.assertIn(key, anchors[0])


if __name__ == "__main__":
    unittest.main()
