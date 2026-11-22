"""Tests de `system_sync.config` (T1, cas N1 à N14 et L1 à L20).

Contrat de T1.b, import `from system_sync import config` :
- `ConfigError(Exception)` : message français avec fichier, ligne, clé et valeur
  reçue ; jamais la valeur d'un secret.
- `load_rules(path) -> dict` : valide les six familles de `rules.toml`.
- `rules_fingerprint(path) -> str` : sha256 hexadécimal du fichier.
- `load_env(path) -> dict[str, str]` : commentaires, lignes vides, guillemets ;
  erreur si absent, sans `=`, en doublon ou variable inconnue.
- `check_env(env) -> dict` : chemins en `Path`, port `int` de 1024 à 65535 ou
  `None` s'il est vide ; seuls les deux chemins sont obligatoires ; il ne
  laisse sortir que des `ConfigError`. Un chemin relatif se résout depuis le
  dossier courant et se cite en absolu dans les messages.
"""

import hashlib
import os
import re
import stat
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
SENTINEL = "SENTINELLE42"
COMMIT = "0123456789abcdef0123456789abcdef01234567"
STATES = [
    "non rencontrée",
    "découverte",
    "en cours",
    "comprise",
    "appliquée",
    "retenue",
    "transférée",
    "transcendée",
    "déclarée",
]
RANK_TYPES = {
    "E": "any_notion",
    "D": "fact_level",
    "C": "fact_level",
    "B": "half_tier_at_least",
    "A": "fact_level",
    "S": "fact_level",
    "Nation": "certifications",
}
CALIBRATION = {"target_level": 25, "r_initial": 0, "min_projects": 3, "min_days": 90}
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
        expected = {
            "target_level": 25,
            "r_initial": 0,
            "min_projects": 3,
            "min_days": 90,
        }
        for key, value in expected.items():
            self.assertEqual(calibration[key], value, key)

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

    def test_T1_N14_real_rules_content(self):
        rules = config.load_rules(REAL_RULES)
        self.assertEqual(rules["states"]["order"], STATES)
        self.assertEqual(rules["states"]["excluded"], ["déclarée"])
        self.assertEqual(list(rules["ranks"]), list(RANK_TYPES))
        for name, kind in RANK_TYPES.items():
            self.assertEqual(rules["ranks"][name]["type"], kind, name)
        titles = rules["titles"]
        self.assertEqual(
            titles["answer_42"],
            {"type": "level_at_least", "value": 25},
        )
        self.assertEqual(
            titles["answer_system"],
            {"type": "rank_on_all_cards", "rank": "S"},
        )
        self.assertEqual(titles["achievements_42"], {"type": "school_achievements"})
        calibration = rules["calibration"]
        for key, value in CALIBRATION.items():
            self.assertEqual(calibration[key], value, key)

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
        message = str(ctx.exception)
        self.assertIn("rules_malformed.toml:3", message)
        self.assertNotRegex(message, r"at line|column|Expected|Invalid")

    def test_T1_L4_rate_above_one_names_key_and_value(self):
        with self.assertRaises(config.ConfigError) as ctx:
            config.load_rules(FIXTURES / "rules_rate_out_of_range.toml")
        self.assertIn("mixte", str(ctx.exception))
        self.assertIn("1.5", str(ctx.exception))

    def test_T1_L4_negative_rate_names_key_and_value(self):
        text = (FIXTURES / "rules_valid.toml").read_text(encoding="utf-8")
        path = self.tmp / "negative.toml"
        self.assertIn("mixte = 0.5", text)
        path.write_text(text.replace("mixte = 0.5", "mixte = -0.1"), encoding="utf-8")
        with self.assertRaises(config.ConfigError) as ctx:
            config.load_rules(path)
        self.assertIn("mixte", str(ctx.exception))
        self.assertIn("-0.1", str(ctx.exception))

    def test_T1_L5_missing_mixte_names_key(self):
        text = (FIXTURES / "rules_valid.toml").read_text(encoding="utf-8")
        path = self.tmp / "no_mixte.toml"
        self.assertIn("mixte = 0.5\n", text)
        path.write_text(text.replace("mixte = 0.5\n", ""), encoding="utf-8")
        with self.assertRaises(config.ConfigError) as ctx:
            config.load_rules(path)
        self.assertIn("mixte", str(ctx.exception))

    def test_T1_L6_duplicate_state_names_value(self):
        text = (FIXTURES / "rules_valid.toml").read_text(encoding="utf-8")
        self.assertIn('"comprise"', text)
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
        self.assertIn("no_equals.env:3", str(ctx.exception))

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
        self.assertIsNone(values["API42_CALLBACK_PORT"])

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


class EnvEdgeCasesTest(TempDirCase):
    def write_env(self, content, name="edge.env"):
        path = self.tmp / name
        path.write_bytes(content.encode("utf-8"))
        return path

    def error_of(self, line, name="edge.env"):
        path = self.write_env(f"# fictif\n\n{line}\n", name)
        with self.assertRaises(config.ConfigError) as ctx:
            config.load_env(path)
        return str(ctx.exception)

    def test_T1_L13_secret_never_quoted_in_env_errors(self):
        lines = (
            f"API42_CLIENT_SECRET {SENTINEL}",
            f"={SENTINEL}",
            f'API42_CLIENT_SECRET="{SENTINEL}',
            f"API42_CLIENT_SECRT={SENTINEL}",
        )
        for line in lines:
            message = self.error_of(line)
            self.assertNotIn(SENTINEL, message, line)
            self.assertIn("edge.env:3", message, line)

    def test_T1_L14_three_causes_have_three_messages(self):
        messages = {
            self.error_of(f"API42_CLIENT_SECRET {SENTINEL}"),
            self.error_of(f"={SENTINEL}"),
            self.error_of(f'API42_CLIENT_SECRET="{SENTINEL}'),
        }
        self.assertEqual(len(messages), 3)

    def test_T1_L15_unknown_variable_is_rejected(self):
        message = self.error_of("VARIABLE_FICTIVE=valeur")
        self.assertIn("VARIABLE_FICTIVE", message)
        self.assertIn("edge.env:3", message)

    def test_T1_L16_crlf_bom_equals_and_comment_in_value(self):
        content = (
            "\ufeff# fictif\r\n"
            "API42_CLIENT_ID=ab=cd\r\n"
            "IA_HISTORY_CSV=/tmp/x # note\r\n"
            "API42_CALLBACK_PORT=5610\r\n"
        )
        env = config.load_env(self.write_env(content))
        self.assertEqual(
            env,
            {
                "API42_CLIENT_ID": "ab=cd",
                "IA_HISTORY_CSV": "/tmp/x # note",
                "API42_CALLBACK_PORT": "5610",
            },
        )

    def test_T1_L17_line_separator_stays_inside_one_value(self):
        path = self.write_env("API42_CLIENT_ID=ab\u2028cd\n")
        self.assertEqual(config.load_env(path), {"API42_CLIENT_ID": "ab\u2028cd"})


class CheckEnvEdgeCasesTest(TempDirCase):
    def setUp(self):
        super().setUp()
        self.csv = self.tmp / "historique.csv"
        self.csv.write_text("a,b\n", encoding="utf-8")
        self.locked = None

    def tearDown(self):
        if self.locked is not None:
            self.locked.chmod(stat.S_IRWXU)

    def failure(self, **overrides):
        env = {
            "PROFESSOR_SUIVI_DIR": str(self.tmp),
            "IA_HISTORY_CSV": str(self.csv),
            "API42_CLIENT_ID": "id-fictif",
            "API42_CLIENT_SECRET": "SENTINEL-SECRET",
            "API42_CALLBACK_PORT": "5610",
        }
        env.update(overrides)
        with self.assertRaises(config.ConfigError) as ctx:
            config.check_env(env)
        self.assertNotIn("SENTINEL-SECRET", str(ctx.exception))
        return str(ctx.exception)

    def test_T1_L18_unknown_user_home_is_a_config_error(self):
        value = "~utilisateurinexistant42/x"
        message = self.failure(PROFESSOR_SUIVI_DIR=value)
        self.assertIn(value, message)

    def test_T1_L18_component_of_300_characters(self):
        value = str(self.tmp / ("a" * 300))
        self.assertIn(value, self.failure(PROFESSOR_SUIVI_DIR=value))

    @unittest.skipIf(os.geteuid() == 0, "root ignore les droits du dossier")
    def test_T1_L18_parent_without_permission(self):
        self.locked = self.tmp / "verrou"
        (self.locked / "suivi").mkdir(parents=True)
        self.locked.chmod(0)
        value = str(self.locked / "suivi")
        self.assertIn(value, self.failure(PROFESSOR_SUIVI_DIR=value))

    def test_T1_L18_port_of_5000_digits(self):
        value = "1" * 5000
        self.assertIn(value, self.failure(API42_CALLBACK_PORT=value))

    def test_T1_L19_relative_path_is_cited_as_absolute(self):
        message = self.failure(PROFESSOR_SUIVI_DIR="dossier_inexistant_42")
        self.assertIn(str(Path.cwd() / "dossier_inexistant_42"), message)


class RulesValidationTest(TempDirCase):
    def failure(self, old, new, name="modified.toml"):
        text = (FIXTURES / "rules_valid.toml").read_text(encoding="utf-8")
        self.assertIn(old, text)
        path = self.tmp / name
        path.write_text(text.replace(old, new), encoding="utf-8")
        with self.assertRaises(config.ConfigError) as ctx:
            config.load_rules(path)
        return str(ctx.exception)

    def test_T1_L20_excluded_as_text_then_as_integer(self):
        old = 'order = ["non rencontrée"'
        as_text = self.failure(old, 'excluded = "déclarée"\n' + old)
        as_integer = self.failure(old, "excluded = 7\n" + old)
        self.assertIn("states.excluded", as_text)
        self.assertIn("déclarée", as_text)
        self.assertIn("states.excluded", as_integer)
        self.assertRegex(as_integer, r"reçue\s*:\s*7\b")
        self.assertNotEqual(as_text, as_integer)

    def test_T1_L21_empty_order(self):
        message = self.failure(
            'order = ["non rencontrée", "déclarée", "comprise", "appliquée"]',
            "order = []",
        )
        self.assertIn("states.order", message)

    def test_T1_L22_order_absent_and_mistyped_differ(self):
        old = 'order = ["non rencontrée", "déclarée", "comprise", "appliquée"]'
        absent = self.failure(old, "")
        mistyped = self.failure(old, "order = 12")
        self.assertIn("order", absent)
        self.assertIn("order", mistyped)
        self.assertRegex(mistyped, r"reçue\s*:\s*12\b")
        self.assertNotEqual(absent, mistyped)

    def test_T1_L23_r_initial_not_finite(self):
        for value in ("nan", "inf"):
            message = self.failure("r_initial = 0", f"r_initial = {value}")
            self.assertIn("calibration.r_initial", message, value)
            self.assertIn(value, message, value)

    def test_T1_L24_xp_url_must_be_https(self):
        old = f"https://example.invalid/raw/{COMMIT}/experience.json"
        messages = []
        for url in (f"http://example.invalid/{COMMIT}/x", f"file:///{COMMIT}/x"):
            message = self.failure(old, url)
            self.assertIn("xp_table.url", message)
            self.assertIn(url, message)
            self.assertIn("https://", message)
            messages.append(message)
        self.assertNotEqual(messages[0], messages[1])

    def test_T1_L25_commit_must_be_40_hexadecimals(self):
        for commit in ("abc123", "g" * 40):
            message = self.failure(COMMIT, commit)
            self.assertIn("xp_table.commit", message, commit)
            self.assertIn(commit, message, commit)

    def test_T1_L26_answer_system_rank_must_exist(self):
        old = 'value = 25\n'
        extra = old + '\n[titles.answer_system]\ntype = "rank_on_all_cards"\nrank = "Z"\n'
        message = self.failure(old, extra)
        self.assertIn("titles.answer_system.rank", message)
        self.assertIn("Z", message)

    def test_T1_L27_rank_entry_must_be_a_table(self):
        message = self.failure('[ranks.E]\ntype = "any_notion"', "[ranks]\nE = 5")
        self.assertIn("ranks.E", message)
        self.assertRegex(message, r"reçue\s*:\s*5\b")


class CertReadyTest(TempDirCase):
    """Clé `states.cert_ready_at_least` (T1.e, amendement A22)."""

    CURRENT = 'cert_ready_at_least = "appliquée"'

    def failure(self, old, new, name="modified.toml"):
        text = (FIXTURES / "rules_valid.toml").read_text(encoding="utf-8")
        self.assertIn(old, text)
        path = self.tmp / name
        path.write_text(text.replace(old, new), encoding="utf-8")
        with self.assertRaises(config.ConfigError) as ctx:
            config.load_rules(path)
        return str(ctx.exception)

    def test_T1e_real_rules_value_is_retenue(self):
        rules = config.load_rules(REAL_RULES)
        self.assertEqual(rules["states"]["cert_ready_at_least"], "retenue")

    def test_T1e_real_value_in_order_and_not_excluded(self):
        states = config.load_rules(REAL_RULES)["states"]
        self.assertIn(states["cert_ready_at_least"], states["order"])
        self.assertNotIn(states["cert_ready_at_least"], states["excluded"])

    def test_T1e_valid_fixture_returns_the_key(self):
        rules = config.load_rules(FIXTURES / "rules_valid.toml")
        self.assertEqual(rules["states"]["cert_ready_at_least"], "appliquée")

    def test_T1e_absent_key_names_it(self):
        message = self.failure(self.CURRENT + "\n", "")
        self.assertIn("states.cert_ready_at_least", message)

    def test_T1e_value_outside_order_names_key_value_and_allowed(self):
        message = self.failure(self.CURRENT, 'cert_ready_at_least = "expert"')
        self.assertIn("states.cert_ready_at_least", message)
        self.assertIn("expert", message)
        for state in ("non rencontrée", "déclarée", "comprise", "appliquée"):
            self.assertIn(state, message)

    def test_T1e_value_in_excluded_is_rejected(self):
        old = 'order = ["non rencontrée"'
        text = (FIXTURES / "rules_valid.toml").read_text(encoding="utf-8")
        text = text.replace(self.CURRENT, 'cert_ready_at_least = "déclarée"')
        path = self.tmp / "excluded_value.toml"
        new = 'excluded = ["déclarée"]\n' + old
        path.write_text(text.replace(old, new), encoding="utf-8")
        with self.assertRaises(config.ConfigError) as ctx:
            config.load_rules(path)
        message = str(ctx.exception)
        self.assertIn("states.cert_ready_at_least", message)
        self.assertIn("déclarée", message)
        self.assertNotIn("hors de `order`", message)

    def test_T1e_non_text_values_name_key_and_received_value(self):
        for raw, value in (("7", 7), ("[1, 2]", [1, 2]), ("true", True), ("1.5", 1.5)):
            message = self.failure(self.CURRENT, f"cert_ready_at_least = {raw}")
            self.assertIn("states.cert_ready_at_least", message, raw)
            self.assertIn("texte", message, raw)
            self.assertRegex(message, r"reçue\s*:\s*" + re.escape(repr(value)), raw)

    def test_T1e_empty_text_names_key(self):
        message = self.failure(self.CURRENT, 'cert_ready_at_least = ""')
        self.assertIn("states.cert_ready_at_least", message)
        self.assertIn("vide", message)

    def test_T1e_five_causes_have_five_messages(self):
        values = ('"expert"', '""', "7", "[1]")
        messages = {
            self.failure(self.CURRENT, f"cert_ready_at_least = {value}")
            for value in values
        }
        messages.add(self.failure(self.CURRENT + "\n", ""))
        self.assertEqual(len(messages), 5)


if __name__ == "__main__":
    unittest.main()
