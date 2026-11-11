"""Tests de `system_sync.output` (T2, cas N5 à N12 et L1 à L14).

Contrat de T2.b, import `from system_sync import output` :
- `OutputError(Exception)` : une ligne `chemin : cause` par problème, ou `strerror` + chemin.
- `validate(state) -> list[tuple[str, str]]` : couples (chemin du champ fautif, cause),
  `[]` si valide, sans lever. Chemin pointé (`level42.email`, `cards[1].id`, `$` racine) ;
  cause = valeur reçue ou type.
- `write(state, path) -> None` : valide d'abord (`OutputError`, rien d'écrit), crée le
  dossier, temporaire voisin puis `os.replace`, `allow_nan=False`, contenu
  `window.SYSTEM_STATE = ` + JSON + `;` + saut de ligne. Échec : ancien fichier intact.
- Schéma de `tests/fixtures/state/state_complete.js` : 12 entités, objets fermés, clés et
  types requis. Dict `value`, `status`, `sources`, `reason` = valeur statuée (`model`).
  `schema_version` 1, `generated_at` `AAAA-MM-JJThh:mm:ssZ`, niveaux et XP finis >= 0.
  `setting` : perso|pro ; projet `status` : en cours|livré|abandonné ; `scope` : 42|Système.
"""

import copy
import errno
import hashlib
import json
import os
import stat
import tempfile
import unittest
from pathlib import Path

try:
    from system_sync import output
except ImportError:
    output = None  # chaque test échoue séparément tant que le module manque

ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURES = ROOT / "tests" / "fixtures" / "state"
SOURCE = ROOT / "source" / "system_sync"
PREFIX = "window.SYSTEM_STATE = "
ENTITIES = {
    "meta",
    "sources",
    "level42",
    "system",
    "trajectory",
    "cards",
    "notions",
    "relations",
    "projects",
    "titles",
    "anomalies",
    "network",
}


def load_state(name):
    """Lit une fixture `state_<name>.js` et renvoie l'objet JSON qu'elle porte."""
    text = (FIXTURES / f"state_{name}.js").read_text(encoding="utf-8")
    assert text.startswith(PREFIX) and text.endswith(";\n"), name
    return json.loads(text[len(PREFIX) : -2])


def set_at(state, path, value):
    """Remplace la valeur au chemin donné (clés séparées par `.`, entiers en index)."""
    keys = [int(k) if k.isdigit() else k for k in path.split(".")]
    holder = state
    for key in keys[:-1]:
        holder = holder[key]
    assert keys[-1] in holder if isinstance(holder, dict) else keys[-1] < len(holder)
    holder[keys[-1]] = value


def paths_of(state):
    return [path for path, _ in output.validate(state)]


def cause_at(state, path):
    causes = [cause for found, cause in output.validate(state) if found == path]
    assert causes, f"{path} absent de {output.validate(state)}"
    return causes[0]


class TempDirCase(unittest.TestCase):
    def setUp(self):
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        self.tmp = Path(holder.name)
        self.target = self.tmp / "data" / "state.js"


class ValidStatesTest(unittest.TestCase):
    def test_T2_N5_minimal_state_is_valid(self):
        self.assertEqual(output.validate(load_state("minimal")), [])

    def test_T2_N6_complete_state_is_valid(self):
        self.assertEqual(output.validate(load_state("complete")), [])

    def test_T2_N6_partial_and_trap_fixtures_are_valid(self):
        for name in ("partial", "trap"):
            self.assertEqual(output.validate(load_state(name)), [], name)


class WriteTest(TempDirCase):
    def test_T2_N7_output_starts_and_ends_as_specified(self):
        output.write(load_state("complete"), self.target)
        text = self.target.read_text(encoding="utf-8")
        self.assertTrue(text.startswith(PREFIX))
        self.assertTrue(text.endswith(";\n"))
        self.assertFalse(text.endswith(";\n\n"))

    def test_T2_N8_json_round_trip_is_identical(self):
        for name in ("complete", "trap", "minimal"):
            state = load_state(name)
            output.write(state, self.target)
            text = self.target.read_text(encoding="utf-8")
            self.assertEqual(json.loads(text[len(PREFIX) : -2]), state, name)

    def test_T2_N9_missing_data_directory_is_created(self):
        self.assertFalse(self.target.parent.exists())
        output.write(load_state("minimal"), self.target)
        self.assertTrue(self.target.is_file())

    def test_T2_N10_no_temporary_file_remains(self):
        output.write(load_state("complete"), self.target)
        output.write(load_state("minimal"), self.target)
        self.assertEqual(os.listdir(self.target.parent), ["state.js"])

    def test_T2_N10_no_temporary_file_after_a_refusal(self):
        state = load_state("complete")
        set_at(state, "level42.level.status", "bizarre")
        with self.assertRaises(output.OutputError):
            output.write(state, self.target)
        self.assertEqual([p for p in self.tmp.rglob("*") if p.is_file()], [])
        self.assertFalse(self.target.exists())

    def test_T2_L12_failed_validation_keeps_the_old_file(self):
        output.write(load_state("complete"), self.target)
        before = hashlib.sha256(self.target.read_bytes()).hexdigest()
        state = load_state("complete")
        set_at(state, "level42.level.status", "bizarre")
        with self.assertRaises(output.OutputError) as ctx:
            output.write(state, self.target)
        self.assertIn("level42.level.status", str(ctx.exception))
        after = hashlib.sha256(self.target.read_bytes()).hexdigest()
        self.assertEqual(before, after)
        self.assertEqual(os.listdir(self.target.parent), ["state.js"])

    def test_T2_L12_nan_is_refused_before_any_write(self):
        state = load_state("complete")
        set_at(state, "level42.xp.value", float("nan"))
        with self.assertRaises(output.OutputError) as ctx:
            output.write(state, self.target)
        self.assertIn("level42.xp.value", str(ctx.exception))
        self.assertFalse(self.target.exists())

    @unittest.skipIf(os.geteuid() == 0, "root ignore les droits du dossier")
    def test_T2_L13_read_only_directory_keeps_old_file_and_cites_strerror(self):
        output.write(load_state("minimal"), self.target)
        before = self.target.read_bytes()
        self.target.parent.chmod(stat.S_IRUSR | stat.S_IXUSR)
        self.addCleanup(self.target.parent.chmod, stat.S_IRWXU)
        with self.assertRaises(output.OutputError) as ctx:
            output.write(load_state("complete"), self.target)
        self.assertIn(os.strerror(errno.EACCES), str(ctx.exception))
        self.assertIn(str(self.target), str(ctx.exception))
        self.assertEqual(self.target.read_bytes(), before)
        self.assertEqual(os.listdir(self.target.parent), ["state.js"])


class SchemaRefusalTest(unittest.TestCase):
    def test_T2_N11_unknown_key_is_refused_with_its_path(self):
        found = output.validate(load_state("unknown_key"))
        self.assertEqual([path for path, _ in found], ["level42.email"])

    def test_T2_N12_solidity_column_is_refused_in_notions(self):
        state = load_state("complete")
        state["notions"]["notion_a"]["solidity"] = "texte libre"
        self.assertEqual(paths_of(state), ["notions.notion_a.solidity"])

    def test_T2_L1_missing_meta(self):
        state = load_state("complete")
        self.assertIn("meta", state)
        del state["meta"]
        self.assertEqual(paths_of(state), ["meta"])

    def test_T2_L2_empty_object_lists_every_missing_entity(self):
        found = output.validate(load_state("empty"))
        self.assertEqual(len(found), len(ENTITIES))
        self.assertEqual({path for path, _ in found}, ENTITIES)

    def test_T2_L3_state_that_is_not_an_object(self):
        for state in ([], ["meta"], "texte", 12, None):
            found = output.validate(state)
            self.assertEqual([path for path, _ in found], ["$"], repr(state))
            self.assertIn(type(state).__name__, found[0][1])

    def test_T2_L4_unknown_status_cites_the_value(self):
        state = load_state("complete")
        set_at(state, "level42.level.status", "bizarre")
        self.assertIn("bizarre", cause_at(state, "level42.level.status"))

    def test_T2_L5_observed_with_null_value(self):
        state = load_state("complete")
        set_at(state, "level42.level.value", None)
        self.assertIn("level42.level.value", paths_of(state))

    def test_T2_L6_insufficient_with_value(self):
        state = load_state("partial")
        set_at(state, "level42.level.value", 5)
        self.assertIn("5", cause_at(state, "level42.level.value"))

    def test_T2_L7_insufficient_without_reason_fixture(self):
        found = output.validate(load_state("insufficient_without_reason"))
        self.assertEqual([path for path, _ in found], ["level42.level.reason"])

    def test_T2_L7_blank_reasons_are_refused(self):
        for reason in (None, "", "   ", "\t\n "):
            state = load_state("partial")
            set_at(state, "level42.level.reason", reason)
            self.assertIn("level42.level.reason", paths_of(state), repr(reason))

    def test_T2_L8_unknown_schema_version_cites_the_value(self):
        found = output.validate(load_state("unknown_schema"))
        self.assertEqual([path for path, _ in found], ["meta.schema_version"])
        self.assertIn("99", found[0][1])

    def test_T2_L9_negative_level_and_xp(self):
        for path in ("level42.level.value", "level42.xp.value", "system.xp.value"):
            state = load_state("complete")
            set_at(state, path, -5)
            self.assertIn("-5", cause_at(state, path), path)

    def test_T2_L9_malformed_generation_date(self):
        for date in ("hier", "2026-13-45T10:00:00Z", "2026-11-11", "", 20261111):
            state = load_state("complete")
            set_at(state, "meta.generated_at", date)
            self.assertIn("meta.generated_at", paths_of(state), repr(date))

    def test_T2_L10_two_cards_with_the_same_id(self):
        state = load_state("complete")
        state["cards"].append(copy.deepcopy(state["cards"][0]))
        path = f"cards[{len(state['cards']) - 1}].id"
        self.assertIn("card_alpha", cause_at(state, path))

    def test_T2_L10_two_sources_with_the_same_name(self):
        state = load_state("complete")
        state["sources"].append(copy.deepcopy(state["sources"][0]))
        path = f"sources[{len(state['sources']) - 1}].name"
        self.assertIn("professor", cause_at(state, path))

    def test_T2_L11_nan_and_infinity_are_refused_with_their_path(self):
        for number in (float("nan"), float("inf"), float("-inf")):
            state = load_state("complete")
            set_at(state, "level42.xp.value", number)
            self.assertIn("level42.xp.value", paths_of(state), repr(number))

    def test_T2_L14_observed_without_source(self):
        state = load_state("complete")
        set_at(state, "level42.level.sources", [])
        self.assertIn("level42.level.sources", paths_of(state))


class SchemaFieldsTest(unittest.TestCase):
    """Champs ajoutés par famille : absence et mauvais type, avec le chemin fautif."""

    def drop_all(self, container, prefix, fields):
        for field in fields:
            state = load_state("complete")
            holder = state
            for key in container.split("."):
                holder = holder[int(key) if key.isdigit() else key]
            self.assertIn(field, holder)
            del holder[field]
            self.assertIn(f"{prefix}.{field}", paths_of(state), field)

    def test_T2_N13_notion_label_is_required_and_text(self):
        self.drop_all("notions.notion_a", "notions.notion_a", ["label"])
        state = load_state("complete")
        set_at(state, "notions.notion_a.label", 5)
        self.assertIn("notions.notion_a.label", paths_of(state))

    def test_T2_N14_relation_fields_are_required(self):
        self.drop_all("relations.0", "relations[0]", ["kind", "limit", "proof"])

    def test_T2_N14_relation_types(self):
        for field in ("kind", "limit", "proof"):
            state = load_state("complete")
            set_at(state, f"relations.0.{field}", 5)
            self.assertIn(f"relations[0].{field}", paths_of(state), field)

    def test_T2_N14_relation_limit_and_proof_accept_text_or_null(self):
        for value in ("texte", None):
            state = load_state("complete")
            set_at(state, "relations.0.limit", value)
            set_at(state, "relations.0.proof", value)
            self.assertEqual(output.validate(state), [], repr(value))

    def test_T2_N15_edge_kind_and_status_are_required_and_text(self):
        self.drop_all("network.edges.0", "network.edges[0]", ["kind", "status"])
        for field in ("kind", "status"):
            state = load_state("complete")
            set_at(state, f"network.edges.0.{field}", 5)
            self.assertIn(f"network.edges[0].{field}", paths_of(state), field)

    def test_T2_N16_project_fields_are_required(self):
        fields = ["setting", "name", "status", "date", "equivalent_42"]
        self.drop_all("projects.0", "projects[0]", fields)

    def test_T2_N16_framework_key_is_refused(self):
        state = load_state("complete")
        state["projects"][0]["framework"] = "perso"
        self.assertIn("projects[0].framework", paths_of(state))

    def test_T2_N16_project_setting_and_status_values(self):
        for field, value in (("setting", "autre"), ("status", "terminé")):
            state = load_state("complete")
            set_at(state, f"projects.0.{field}", value)
            self.assertIn(value, cause_at(state, f"projects[0].{field}"))
        for status in ("en cours", "livré", "abandonné"):
            state = load_state("complete")
            set_at(state, "projects.0.status", status)
            self.assertEqual(output.validate(state), [], status)

    def test_T2_N17_title_fields_are_required(self):
        fields = ["scope", "condition", "progress", "target"]
        self.drop_all("titles.0", "titles[0]", fields)

    def test_T2_N17_title_types_and_scope(self):
        checks = (("scope", "autre"), ("condition", 5), ("target", "vingt"))
        for field, value in checks:
            state = load_state("complete")
            set_at(state, f"titles.0.{field}", value)
            self.assertIn(f"titles[0].{field}", paths_of(state), field)

    def test_T2_N17_title_progress_is_a_stated_value(self):
        state = load_state("complete")
        set_at(state, "titles.0.progress", 12.44)
        self.assertIn("titles[0].progress", paths_of(state))
        set_at(state, "titles.0.progress", {"value": 1, "status": "bizarre"})
        self.assertIn("titles[0].progress", " ".join(paths_of(state)))

    def test_T2_N17_title_target_may_be_null(self):
        state = load_state("complete")
        set_at(state, "titles.0.target", None)
        self.assertEqual(output.validate(state), [])

    def test_T2_N18_certification_tier_is_required_and_text(self):
        prefix = "cards[0].certifications[0]"
        self.drop_all("cards.0.certifications.0", prefix, ["tier"])
        state = load_state("complete")
        set_at(state, "cards.0.certifications.0.tier", 5)
        self.assertIn(f"{prefix}.tier", paths_of(state))

    def test_T2_N18_certification_obtained_is_a_stated_value(self):
        state = load_state("complete")
        set_at(state, "cards.0.certifications.0.obtained", False)
        self.assertIn("cards[0].certifications[0].obtained", paths_of(state))

    def test_T2_N18_certification_obtained_follows_stated_rules(self):
        path = "cards.0.certifications.0.obtained"
        state = load_state("complete")
        set_at(state, path, {"value": None, "status": "insufficient"})
        self.assertIn("cards[0].certifications[0].obtained", " ".join(paths_of(state)))
        set_at(
            state,
            path,
            {"value": None, "status": "insufficient", "sources": [], "reason": "illisible"},
        )
        self.assertEqual(output.validate(state), [])


class SourceCriteriaTest(unittest.TestCase):
    def test_T2_criterion2_allow_nan_false_appears_once(self):
        text = (SOURCE / "output.py").read_text(encoding="utf-8")
        self.assertEqual(text.count("allow_nan=False"), 1)

    def test_T2_criterion3_atomic_replace_is_used(self):
        text = (SOURCE / "output.py").read_text(encoding="utf-8")
        self.assertGreaterEqual(text.count("os.replace"), 1)

    def test_T2_criterion5_files_stay_under_750_lines(self):
        for name in ("model.py", "output.py"):
            lines = (SOURCE / name).read_text(encoding="utf-8").splitlines()
            self.assertLessEqual(len(lines), 750, name)


if __name__ == "__main__":
    unittest.main()
