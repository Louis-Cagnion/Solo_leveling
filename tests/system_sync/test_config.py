"""Tests de `system_sync.config` (T1, cas N1 à N7 et L1 à L12).

Contrat que le builder de T1.b suit, import `from system_sync import config` :
- `ConfigError(Exception)` : message en français avec fichier, ligne, clé et
  valeur reçue ; jamais la valeur d'un secret.
- `load_rules(path) -> dict` : valide `rules.toml` (familles states, ranks,
  ia, xp_table, calibration, titles). `states.order` sans doublon ; taux
  `ia.louis`, `ia.mixte` et `ia.ia` présents, dans [0, 1].
- `rules_fingerprint(path) -> str` : sha256 hexadécimal du fichier.
- `load_env(path) -> dict[str, str]` : commentaires, lignes vides, guillemets.
  Erreur si absent (liste les 5 variables), sans `=` ou en doublon.
- `check_env(env) -> dict` : valeurs converties, clés = noms des variables,
  port en `int` dans 1024-65535, chemins en `pathlib.Path`. Seuls les deux
  chemins sont obligatoires ; PROFESSOR_SUIVI_DIR existe et est un dossier.
"""

import hashlib
import re
import tempfile
import tomllib
import unittest
from pathlib import Path

try:
    from system_sync import config
except ImportError:
    config = None  # chaque test échoue séparément tant que le module manque

ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURES = ROOT / "tests" / "fixtures" / "config"
REAL_RULES = ROOT / "config" / "rules.toml"
VARIABLES = (
    "PROFESSOR_SUIVI_DIR",
    "IA_HISTORY_CSV",
    "API42_CLIENT_ID",
    "API42_CLIENT_SECRET",
    "API42_CALLBACK_PORT",
)
FAMILIES = ["calibration", "ia", "ranks", "states", "titles", "xp_table"]
PIN_COMMIT = "520b8e938ac8f685a4bc647bba45d0b409282714"


class TempDirCase(unittest.TestCase):
    def setUp(self):
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        self.tmp = Path(holder.name)


class RealRulesTest(unittest.TestCase):
    def test_T1_N1_real_rules_load_with_six_families(self):
        rules = config.load_rules(REAL_RULES)
        self.assertEqual(sorted(rules), FAMILIES)

    def test_T1_N2_ia_rates_and_lecture_absent(self):
        rules = config.load_rules(REAL_RULES)
        self.assertEqual(rules["ia"], {"louis": 1.0, "mixte": 0.5, "ia": 0.0})

    def test_T1_N3_xp_table_pinned(self):
        table = config.load_rules(REAL_RULES)["xp_table"]
        self.assertIn(PIN_COMMIT, table["url"])
        self.assertRegex(table["sha256"], r"^[0-9a-f]{64}$")

    def test_T1_N4_calibration_parameters(self):
        calibration = config.load_rules(REAL_RULES)["calibration"]
        self.assertEqual(calibration["r_initial"], 0)
        for expected in (25, 3, 90):
            self.assertIn(expected, calibration.values())

    def test_T1_N5_fingerprint_is_file_sha256(self):
        expected = hashlib.sha256(REAL_RULES.read_bytes()).hexdigest()
        self.assertEqual(config.rules_fingerprint(REAL_RULES), expected)

    def test_T1_N6_env_example_has_five_empty_keys(self):
        text = (ROOT / ".env.example").read_text(encoding="utf-8")
        pairs = {}
        for line in text.splitlines():
            if line.strip() and not line.startswith("#"):
                key, _, value = line.partition("=")
                pairs[key] = value
        self.assertEqual(pairs, {name: "" for name in VARIABLES})

    def test_T1_criterion3_real_rules_families_with_tomllib(self):
        with open(REAL_RULES, "rb") as handle:
            self.assertEqual(sorted(tomllib.load(handle)), FAMILIES)

    def test_T1_criterion5_xp_sha256_pinned_once(self):
        pin = "7b98ff202015868ed400f339589e6ca00dc009d436a599c3f2272b5c0e258771"
        text = REAL_RULES.read_text(encoding="utf-8")
        self.assertEqual(text.count(pin), 1)

    def test_T1_criterion7_no_secret_in_env_example(self):
        text = (ROOT / ".env.example").read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"^API42_CLIENT_SECRET=.+", text, re.M))


class LoadRulesTest(TempDirCase):
    def test_T1_N1_valid_fixture_loads(self):
        rules = config.load_rules(FIXTURES / "rules_valid.toml")
        self.assertEqual(sorted(rules), FAMILIES)

    def test_T1_L1_missing_file_names_path(self):
        path = self.tmp / "absent.toml"
        with self.assertRaises(config.ConfigError) as ctx:
            config.load_rules(path)
        self.assertIn(str(path), str(ctx.exception))

    def test_T1_L2_empty_file_says_empty(self):
        path = FIXTURES / "rules_empty.toml"
        with self.assertRaises(config.ConfigError) as ctx:
            config.load_rules(path)
        self.assertIn("vide", str(ctx.exception))
        self.assertIn("rules_empty.toml", str(ctx.exception))

    def test_T1_L3_malformed_toml_names_line(self):
        with self.assertRaises(config.ConfigError) as ctx:
            config.load_rules(FIXTURES / "rules_malformed.toml")
        self.assertIn("rules_malformed.toml", str(ctx.exception))
        self.assertRegex(str(ctx.exception), r"\b3\b")

    def test_T1_L4_rate_above_one_names_key_and_value(self):
        with self.assertRaises(config.ConfigError) as ctx:
            config.load_rules(FIXTURES / "rules_rate_out_of_range.toml")
        self.assertIn("mixte", str(ctx.exception))
        self.assertIn("1.5", str(ctx.exception))

    def test_T1_L4_negative_rate_names_key_and_value(self):
        text = (FIXTURES / "rules_valid.toml").read_text(encoding="utf-8")
        path = self.tmp / "negative.toml"
        path.write_text(text.replace("mixte = 0.5", "mixte = -0.1"), encoding="utf-8")
        with self.assertRaises(config.ConfigError) as ctx:
            config.load_rules(path)
        self.assertIn("mixte", str(ctx.exception))
        self.assertIn("-0.1", str(ctx.exception))

    def test_T1_L5_missing_mixte_names_key(self):
        text = (FIXTURES / "rules_valid.toml").read_text(encoding="utf-8")
        path = self.tmp / "no_mixte.toml"
        path.write_text(text.replace("mixte = 0.5\n", ""), encoding="utf-8")
        with self.assertRaises(config.ConfigError) as ctx:
            config.load_rules(path)
        self.assertIn("mixte", str(ctx.exception))

    def test_T1_L6_duplicate_state_names_value(self):
        text = (FIXTURES / "rules_valid.toml").read_text(encoding="utf-8")
        doubled = text.replace('"comprise"', '"comprise", "comprise"')
        path = self.tmp / "dup_states.toml"
        path.write_text(doubled, encoding="utf-8")
        with self.assertRaises(config.ConfigError) as ctx:
            config.load_rules(path)
        self.assertIn("comprise", str(ctx.exception))


class LoadEnvTest(TempDirCase):
    def test_T1_N7_env_accepts_comments_blanks_and_quotes(self):
        env = config.load_env(FIXTURES / "valid.env")
        self.assertEqual(
            env,
            {
                "PROFESSOR_SUIVI_DIR": "/tmp/fictif/suivi",
                "IA_HISTORY_CSV": "/tmp/fictif/historique.csv",
                "API42_CLIENT_ID": "id-fictif",
                "API42_CLIENT_SECRET": "",
                "API42_CALLBACK_PORT": "5610",
            },
        )

    def test_T1_N7_env_reads_non_empty_secret_from_temp_file(self):
        path = self.tmp / "secret.env"
        path.write_text(
            "# fictif\n\nAPI42_CLIENT_SECRET=\"secret-fictif\"\n",
            encoding="utf-8",
        )
        env = config.load_env(path)
        self.assertEqual(env["API42_CLIENT_SECRET"], "secret-fictif")

    def test_T1_L7_missing_env_lists_five_variables(self):
        path = self.tmp / "absent.env"
        with self.assertRaises(config.ConfigError) as ctx:
            config.load_env(path)
        message = str(ctx.exception)
        self.assertIn(str(path), message)
        for name in VARIABLES:
            self.assertIn(name, message)

    def test_T1_L9_line_without_equals_names_line_number(self):
        with self.assertRaises(config.ConfigError) as ctx:
            config.load_env(FIXTURES / "no_equals.env")
        self.assertIn("no_equals.env", str(ctx.exception))
        self.assertRegex(str(ctx.exception), r"\b3\b")

    def test_T1_L10_duplicate_key_names_key(self):
        with self.assertRaises(config.ConfigError) as ctx:
            config.load_env(FIXTURES / "duplicate.env")
        self.assertIn("duplicate.env", str(ctx.exception))
        self.assertIn("PROFESSOR_SUIVI_DIR", str(ctx.exception))


class CheckEnvTest(TempDirCase):
    def setUp(self):
        super().setUp()
        self.suivi = self.tmp / "suivi"
        self.suivi.mkdir()
        self.csv = self.tmp / "historique.csv"
        self.csv.write_text("a,b\n", encoding="utf-8")

    def make_env(self, **overrides):
        env = {
            "PROFESSOR_SUIVI_DIR": str(self.suivi),
            "IA_HISTORY_CSV": str(self.csv),
            "API42_CLIENT_ID": "id-fictif",
            "API42_CLIENT_SECRET": "SENTINEL-SECRET",
            "API42_CALLBACK_PORT": "5610",
        }
        env.update(overrides)
        return env

    def test_T1_N7_valid_env_is_converted(self):
        values = config.check_env(self.make_env())
        self.assertEqual(values["PROFESSOR_SUIVI_DIR"], self.suivi)
        self.assertEqual(values["IA_HISTORY_CSV"], self.csv)
        self.assertIsInstance(values["PROFESSOR_SUIVI_DIR"], Path)
        self.assertEqual(values["API42_CALLBACK_PORT"], 5610)
        self.assertIsInstance(values["API42_CALLBACK_PORT"], int)

    def test_T1_N7_port_bounds_are_accepted(self):
        for port in ("1024", "65535"):
            values = config.check_env(self.make_env(API42_CALLBACK_PORT=port))
            self.assertEqual(values["API42_CALLBACK_PORT"], int(port))

    def test_T1_N7_api_variables_may_stay_empty(self):
        env = self.make_env(
            API42_CLIENT_ID="",
            API42_CLIENT_SECRET="",
            API42_CALLBACK_PORT="",
        )
        values = config.check_env(env)
        self.assertEqual(values["PROFESSOR_SUIVI_DIR"], self.suivi)

    def test_T1_L8_empty_required_variable_names_it_only(self):
        for name in ("PROFESSOR_SUIVI_DIR", "IA_HISTORY_CSV"):
            with self.assertRaises(config.ConfigError) as ctx:
                config.check_env(self.make_env(**{name: ""}))
            self.assertIn(name, str(ctx.exception))
            self.assertNotIn("SENTINEL-SECRET", str(ctx.exception))

    def test_T1_L8_secret_never_in_any_message(self):
        with self.assertRaises(config.ConfigError) as ctx:
            config.check_env(self.make_env(API42_CALLBACK_PORT="abc"))
        self.assertNotIn("SENTINEL-SECRET", str(ctx.exception))

    def test_T1_L11_missing_path_and_file_messages_differ(self):
        missing = self.tmp / "inexistant"
        with self.assertRaises(config.ConfigError) as first:
            config.check_env(self.make_env(PROFESSOR_SUIVI_DIR=str(missing)))
        with self.assertRaises(config.ConfigError) as second:
            config.check_env(self.make_env(PROFESSOR_SUIVI_DIR=str(self.csv)))
        self.assertIn(str(missing), str(first.exception))
        self.assertIn(str(self.csv), str(second.exception))
        self.assertNotEqual(str(first.exception), str(second.exception))

    def test_T1_L12_invalid_port_names_value(self):
        for port in ("abc", "80", "1023", "65536", "-5", "55.5"):
            with self.assertRaises(config.ConfigError, msg=port) as ctx:
                config.check_env(self.make_env(API42_CALLBACK_PORT=port))
            self.assertIn(port, str(ctx.exception))
            self.assertIn("API42_CALLBACK_PORT", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
