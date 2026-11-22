"""Tests de `system_sync.output` (T2, cas N5 à N12 et L1 à L14, amendements A17 à A27).

Contrat de T2.b, import `from system_sync import output` :
- `OutputError(Exception)` : une ligne `chemin : cause` par problème, ou `strerror` + chemin.
- `validate(state) -> list[tuple[str, str]]` : couples (chemin du champ fautif, cause),
  `[]` si valide, sans lever. Chemin pointé (`level42.email`, `cards[1].id`, `$` racine) ;
  cause = valeur reçue ou type.
- `write(state, path) -> None` : valide d'abord (`OutputError`, rien d'écrit), crée le
  dossier, temporaire voisin puis `os.replace`, `allow_nan=False`, contenu
  `window.SYSTEM_STATE = ` + JSON + `;` + saut de ligne. Échec : ancien fichier intact.
- Schéma de `tests/fixtures/state/state_complete.js` : 14 entités (A30), objets fermés,
  clés et types requis ; `network` est refusée (A25). `schema_version` 1, `generated_at`
  `AAAA-MM-JJThh:mm:ssZ`, dates simples `AAAA-MM-JJ`, niveaux et XP finis >= 0.
- Valeur statuée : `value`, `status`, `sources`, `reason`, `reason_code` (cinq clés).
  `status` parmi quatre (A17). `observed` : valeur non nulle, une source. `unmeasurable` :
  valeur `null`, raison. `insufficient` : raison, valeur facultative. Chemin du défaut :
  `.value`, `.sources` ou `.reason`. `reason_code` (A18) : code de `model.REASON_CODES` ou
  `null` ; une raison non vide sans code est refusée au chemin `.reason_code` ; un code
  sans raison n'est refusé qu'au chemin `.reason` quand le statut l'exige.
- `cards[].rank.value` : E, D, C, B, A, S, Nation ou none (A19). `cards[].next_rank`
  (A20) : `null` ou `rank`, `condition`, `progress` (statuée), `total` (entier ou
  `null`), `missing` (`id`, `state`). Certification (A21) : `code`, `detail`, `notions`,
  `conditions` (`null`), `obtained`, `obtained_on`, `accessible`. `level42.target_xp`
  statuée ; `rules` : `proof_order`, `excluded_states`, `rank_d_threshold`,
  `cert_threshold`, `target_level` (A22). `achievements` : `complete` (statuée, valeur
  booléenne) et `items[]` de `id`, `name`, `description`, `obtained` (statuée),
  `obtained_on`, `title` (A23). `notions{}.section`, relation `source`, `target`,
  `sources[].observed_at` (A24). `names` : `en`, identifiant vers libellé (A27).
"""

import copy
import errno
import hashlib
import json
import os
import re
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
    "rules",
    "achievements",
    "names",
}
STATED_VALUES = (
    "level42.level",
    "level42.xp",
    "level42.target_xp",
    "system.calibration",
    "cards.0.rank",
    "cards.0.next_rank.progress",
    "cards.0.certifications.0.obtained",
    "cards.1.certifications.0.accessible",
    "achievements.complete",
    "achievements.items.0.obtained",
)
RANKS = ("E", "D", "C", "B", "A", "S", "Nation", "none")
BAD_DATES = ("hier", "2026-13-45", "2026-11-11T10:00:00Z", "", 20261111)


def load_state(name):
    """Lit une fixture `state_<name>.js` et renvoie l'objet JSON qu'elle porte."""
    text = (FIXTURES / f"state_{name}.js").read_text(encoding="utf-8")
    assert text.startswith(PREFIX) and text.endswith(";\n"), name
    return json.loads(text[len(PREFIX) : -2])


def holder_at(state, dotted):
    """Renvoie l'objet au chemin donné (clés séparées par `.`, entiers en index)."""
    holder = state
    for key in dotted.split("."):
        holder = holder[int(key) if key.isdigit() else key]
    return holder


def set_at(state, path, value):
    """Remplace la valeur au chemin donné (clés séparées par `.`, entiers en index)."""
    parent, _, last = path.rpartition(".")
    holder = holder_at(state, parent) if parent else state
    key = int(last) if last.isdigit() else last
    assert key in holder if isinstance(holder, dict) else key < len(holder), path
    holder[key] = value


def vpath(dotted):
    """Convertit `cards.0.rank` en chemin du validateur `cards[0].rank`."""
    return re.sub(r"\.(\d+)(?=\.|$)", r"[\1]", dotted)


def paths_of(state):
    return [path for path, _ in output.validate(state)]


def cause_at(state, path):
    causes = [cause for found, cause in output.validate(state) if found == path]
    assert causes, f"{path} absent de {output.validate(state)}"
    return causes[0]


class StateCase(unittest.TestCase):
    """Aides communes : modifier une fixture puis lire le verdict du validateur."""

    def refused(self, dotted, value, name="complete", cause=None):
        state = load_state(name)
        set_at(state, dotted, value)
        self.assertIn(vpath(dotted), paths_of(state), repr(value))
        if cause is not None:
            self.assertIn(cause, cause_at(state, vpath(dotted)), repr(value))

    def accepted(self, dotted, value, name="complete"):
        state = load_state(name)
        set_at(state, dotted, value)
        self.assertEqual(output.validate(state), [], f"{dotted} = {value!r}")

    def required(self, container, fields, name="complete"):
        for field in fields:
            state = load_state(name)
            holder = holder_at(state, container)
            self.assertIn(field, holder)
            del holder[field]
            self.assertIn(vpath(f"{container}.{field}"), paths_of(state), field)

    def unknown_key(self, container, key, name="complete"):
        state = load_state(name)
        holder_at(state, container)[key] = "intrus"
        self.assertEqual(paths_of(state), [vpath(f"{container}.{key}")])


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

    def test_A30_complete_and_minimal_fixtures_carry_the_fourteen_entities(self):
        self.assertEqual(len(ENTITIES), 14)
        for name in ("complete", "minimal"):
            state = load_state(name)
            self.assertEqual(set(state), ENTITIES, name)
            self.assertEqual(output.validate(state), [], name)


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


class SchemaRefusalTest(StateCase):
    def test_T2_N11_unknown_key_is_refused_with_its_path(self):
        found = output.validate(load_state("unknown_key"))
        self.assertEqual([path for path, _ in found], ["level42.email"])

    def test_T2_N12_solidity_column_is_refused_in_notions(self):
        self.unknown_key("notions.notion_a", "solidity")

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
        self.refused("level42.level.status", "bizarre", cause="bizarre")

    def test_T2_L4_french_status_names_are_refused(self):
        for status in ("observe", "estime", "insuffisant", "non mesurable"):
            self.refused("level42.level.status", status, cause=status)

    def test_T2_L5_observed_with_null_value(self):
        self.refused("level42.level.value", None)

    def test_T2_L6_unmeasurable_with_value(self):
        self.refused("level42.level.value", 5, name="partial", cause="5")

    def test_T2_L7_unmeasurable_without_reason_fixture(self):
        found = output.validate(load_state("insufficient_without_reason"))
        self.assertEqual([path for path, _ in found], ["level42.level.reason"])

    def test_T2_L7_blank_reasons_are_refused(self):
        for reason in (None, "", "   ", "\t\n "):
            self.refused("level42.level.reason", reason, name="partial")
            self.refused("system.calibration.reason", reason)

    def test_T2_L8_unknown_schema_version_cites_the_value(self):
        found = output.validate(load_state("unknown_schema"))
        self.assertEqual([path for path, _ in found], ["meta.schema_version"])
        self.assertIn("99", found[0][1])

    def test_T2_L9_negative_level_and_xp(self):
        paths = (
            "level42.level.value",
            "level42.xp.value",
            "level42.target_xp.value",
            "system.xp.value",
        )
        for path in paths:
            self.refused(path, -5, cause="-5")

    def test_T2_L9_malformed_generation_date(self):
        for date in ("hier", "2026-13-45T10:00:00Z", "2026-11-11", "", 20261111):
            self.refused("meta.generated_at", date)

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
            self.refused("level42.xp.value", number)

    def test_T2_L14_observed_without_source(self):
        self.refused("level42.level.sources", [])


class SchemaFieldsTest(StateCase):
    """Champs par famille : absence et mauvais type, avec le chemin fautif."""

    def test_T2_N13_notion_label_is_required_and_text(self):
        self.required("notions.notion_a", ["label"])
        self.refused("notions.notion_a.label", 5)

    def test_T2_N14_relation_fields_are_required(self):
        self.required("relations.0", ["kind", "limit", "proof"])

    def test_T2_N14_relation_types(self):
        for field in ("kind", "limit", "proof"):
            self.refused(f"relations.0.{field}", 5)

    def test_T2_N14_relation_limit_and_proof_accept_text_or_null(self):
        for value in ("texte", None):
            state = load_state("complete")
            set_at(state, "relations.0.limit", value)
            set_at(state, "relations.0.proof", value)
            self.assertEqual(output.validate(state), [], repr(value))

    def test_T2_N16_project_fields_are_required(self):
        fields = ["setting", "name", "status", "date", "equivalent_42"]
        self.required("projects.0", fields)

    def test_T2_N16_framework_key_is_refused(self):
        self.unknown_key("projects.0", "framework")

    def test_T2_N16_project_setting_and_status_values(self):
        self.refused("projects.0.setting", "autre", cause="autre")
        self.refused("projects.0.status", "terminé", cause="terminé")
        for status in ("en cours", "livré", "abandonné"):
            self.accepted("projects.0.status", status)

    def test_T2_N17_title_fields_are_required(self):
        self.required("titles.0", ["scope", "condition", "progress", "target"])

    def test_T2_N17_title_types_and_scope(self):
        for field, value in (("scope", "autre"), ("condition", 5), ("target", "vingt")):
            self.refused(f"titles.0.{field}", value)

    def test_T2_N17_title_progress_is_a_stated_value(self):
        self.refused("titles.0.progress", 12.44)
        self.refused("titles.0.progress.status", "bizarre")

    def test_T2_N17_title_target_may_be_null(self):
        self.accepted("titles.0.target", None)


class StatusTest(StateCase):
    """A17 et A18 : quatre statuts et raison traduisible, sur chaque valeur statuée."""

    def test_A17_partial_fixture_carries_unmeasurable_values(self):
        state = load_state("partial")
        self.assertEqual(state["level42"]["level"]["status"], "unmeasurable")
        self.assertEqual(output.validate(state), [])

    def test_A17_unmeasurable_status_is_accepted_everywhere(self):
        unmeasurable = {
            "value": None,
            "status": "unmeasurable",
            "sources": [],
            "reason": "source absente",
            "reason_code": "api_unavailable",
        }
        for dotted in STATED_VALUES:
            self.accepted(dotted, dict(unmeasurable))

    def test_A17_unmeasurable_with_value_is_refused_everywhere(self):
        for dotted in STATED_VALUES:
            state = load_state("complete")
            holder_at(state, dotted).update(
                value=5,
                status="unmeasurable",
                reason="manque",
                reason_code="api_unavailable",
            )
            self.assertIn(vpath(f"{dotted}.value"), paths_of(state), dotted)

    def test_A17_unmeasurable_without_reason_is_refused(self):
        self.refused("level42.level.reason", None, name="partial")

    def test_A17_insufficient_keeps_an_optional_value(self):
        stated = load_state("complete")["system"]["calibration"]
        self.assertEqual(stated["status"], "insufficient")
        self.assertIsNotNone(stated["value"])
        self.accepted("system.calibration.value", None)

    def test_A17_insufficient_without_reason_is_refused(self):
        self.refused("system.calibration.reason", None)

    def test_A18_every_stated_value_has_the_five_keys(self):
        for dotted in STATED_VALUES:
            state = load_state("complete")
            del holder_at(state, dotted)["reason_code"]
            self.assertIn(vpath(f"{dotted}.reason_code"), paths_of(state), dotted)

    def test_A18_code_outside_the_vocabulary_is_refused_and_cited(self):
        for dotted in STATED_VALUES:
            self.refused(f"{dotted}.reason_code", "code_invente", cause="code_invente")

    def test_A18_french_code_is_refused(self):
        self.refused("level42.level.reason_code", "api_indisponible", name="partial")

    def test_A18_reason_without_code_is_refused(self):
        self.refused("level42.xp.reason_code", None)
        self.refused("level42.level.reason_code", None, name="partial")

    def test_A18_code_is_null_without_reason_on_an_observed_value(self):
        state = load_state("complete")
        stated = state["level42"]["level"]
        self.assertEqual((stated["reason"], stated["reason_code"]), (None, None))
        self.assertEqual(output.validate(state), [])


class RankTest(StateCase):
    """A19 et A20 : rang `none` et objet `next_rank`."""

    def test_A19_every_rank_value_is_accepted(self):
        for rank in RANKS:
            self.accepted("cards.0.rank.value", rank)

    def test_A19_none_is_an_observed_rank_in_the_fixture(self):
        state = load_state("complete")
        rank = state["cards"][2]["rank"]
        self.assertEqual((rank["value"], rank["status"]), ("none", "observed"))
        self.assertEqual(output.validate(state), [])

    def test_A19_rank_outside_the_closed_list_is_refused(self):
        for rank in ("Z", "", "e", "aucun", "nation", 5):
            self.refused("cards.0.rank.value", rank, cause=str(rank))

    def test_A20_next_rank_is_null_at_the_maximal_rank(self):
        self.accepted("cards.0.next_rank", None)

    def test_A20_gaps_is_replaced_by_next_rank(self):
        state = load_state("complete")
        self.assertNotIn("gaps", state["cards"][0])
        state["cards"][0]["gaps"] = ["notion_b : comprise requise"]
        self.assertEqual(paths_of(state), ["cards[0].gaps"])

    def test_A20_next_rank_fields_are_required(self):
        fields = ["rank", "condition", "progress", "total", "missing"]
        self.required("cards.0.next_rank", fields)

    def test_A20_next_rank_unknown_key_is_refused(self):
        self.unknown_key("cards.0.next_rank", "email")

    def test_A20_next_rank_types(self):
        self.refused("cards.0.next_rank.condition", 5)
        self.refused("cards.0.next_rank.progress", 1)
        self.refused("cards.0.next_rank.total", "deux")
        self.refused("cards.0.next_rank.missing", "notion_b")

    def test_A20_next_rank_total_may_be_null(self):
        self.assertIsNone(load_state("complete")["cards"][2]["next_rank"]["total"])
        self.accepted("cards.0.next_rank.total", None)

    def test_A20_missing_entries_have_id_and_state(self):
        self.required("cards.0.next_rank.missing.0", ["id", "state"])
        self.refused("cards.0.next_rank.missing.0.id", 5)
        self.unknown_key("cards.0.next_rank.missing.0", "email")

    def test_A20_missing_may_be_empty(self):
        self.accepted("cards.0.next_rank.missing", [])


class CertificationTest(StateCase):
    """A21 : certifications de carte."""

    BASE = "cards.0.certifications.0"

    def test_A21_certification_fields_are_required(self):
        fields = ["code", "detail", "notions", "conditions", "obtained"]
        fields += ["obtained_on", "accessible"]
        self.required(self.BASE, fields)

    def test_A21_tier_is_removed(self):
        self.unknown_key(self.BASE, "tier")

    def test_A21_detail_is_text_or_null(self):
        self.accepted(f"{self.BASE}.detail", "Détail")
        self.accepted(f"{self.BASE}.detail", None)
        self.refused(f"{self.BASE}.detail", 5)

    def test_A21_notions_is_a_list_of_identifiers(self):
        self.accepted(f"{self.BASE}.notions", [])
        self.refused(f"{self.BASE}.notions", "notion_a")
        self.refused(f"{self.BASE}.notions.0", 5)

    def test_A21_conditions_is_null_in_v1(self):
        self.accepted(f"{self.BASE}.conditions", None)
        self.refused(f"{self.BASE}.conditions", "texte")

    def test_A21_obtained_and_accessible_are_stated_values(self):
        self.refused(f"{self.BASE}.obtained", False)
        self.refused(f"{self.BASE}.accessible", False)

    def test_A21_accessible_is_unmeasurable_without_notions(self):
        state = load_state("complete")
        cert = state["cards"][1]["certifications"][0]
        self.assertEqual(cert["notions"], [])
        self.assertEqual(cert["accessible"]["status"], "unmeasurable")
        self.assertEqual(output.validate(state), [])

    def test_A21_obtained_on_is_a_date_or_null(self):
        self.accepted(f"{self.BASE}.obtained_on", "2026-10-20")
        self.accepted(f"{self.BASE}.obtained_on", None)
        for date in BAD_DATES:
            self.refused(f"{self.BASE}.obtained_on", date)


class RulesTest(StateCase):
    """A22 : `level42.target_xp` et entité `rules`."""

    def test_A22_target_xp_is_required_and_stated(self):
        self.required("level42", ["target_xp"])
        self.refused("level42.target_xp", 1000000)

    def test_A22_rules_fields_are_required(self):
        fields = ["proof_order", "excluded_states", "rank_d_threshold"]
        fields += ["cert_threshold", "target_level"]
        self.required("rules", fields)

    def test_A22_rules_unknown_key_is_refused(self):
        self.unknown_key("rules", "secret")

    def test_A22_rules_types(self):
        self.refused("rules.proof_order", "comprise")
        self.refused("rules.proof_order.0", 1)
        self.refused("rules.excluded_states", "déclarée")
        self.refused("rules.excluded_states.0", 1)
        self.refused("rules.rank_d_threshold", 5)
        self.refused("rules.cert_threshold", 5)
        self.refused("rules.target_level", "vingt")

    def test_A22_rules_missing_entity(self):
        state = load_state("complete")
        del state["rules"]
        self.assertEqual(paths_of(state), ["rules"])


class AchievementsTest(StateCase):
    """A23 : entité `achievements`."""

    def test_A23_fields_are_required(self):
        self.required("achievements", ["complete", "items"])
        fields = ["id", "name", "description", "obtained", "obtained_on", "title"]
        self.required("achievements.items.0", fields)

    def test_A23_unknown_keys_are_refused(self):
        self.unknown_key("achievements", "email")
        self.unknown_key("achievements.items.0", "icon")

    def test_A23_complete_is_a_stated_value(self):
        self.refused("achievements.complete", True)
        self.refused("achievements.complete.value", "oui")

    def test_A23_complete_is_unmeasurable_with_its_code_in_the_partial_fixture(self):
        stated = load_state("partial")["achievements"]["complete"]
        self.assertEqual(stated["status"], "unmeasurable")
        self.assertEqual(stated["reason_code"], "full_list_unavailable")
        self.assertEqual(output.validate(load_state("partial")), [])

    def test_A23_item_obtained_is_a_stated_value(self):
        self.refused("achievements.items.0.obtained", True)

    def test_A23_item_obtained_on_and_title_are_nullable(self):
        self.accepted("achievements.items.0.obtained_on", None)
        self.accepted("achievements.items.0.title", None)
        self.accepted("achievements.items.1.title", "answer_42")
        self.accepted("achievements.items.1.obtained_on", "2026-11-01")

    def test_A23_item_types(self):
        for date in BAD_DATES:
            self.refused("achievements.items.0.obtained_on", date)
        self.refused("achievements.items.0.title", 5)
        self.refused("achievements.items.0.name", 5)
        self.refused("achievements.items.0.description", 5)

    def test_A23_two_items_with_the_same_id(self):
        state = load_state("complete")
        items = state["achievements"]["items"]
        items.append(copy.deepcopy(items[0]))
        path = f"achievements.items[{len(items) - 1}].id"
        self.assertIn("achievement_first", cause_at(state, path))


class LinkFieldsTest(StateCase):
    """A24 : `section`, relations `source` et `target`, `observed_at` des sources."""

    def test_A24_notion_section_is_required_text_or_null(self):
        self.required("notions.notion_a", ["section"])
        self.accepted("notions.notion_a.section", None)
        self.accepted("notions.notion_a.section", "Alpha")
        self.refused("notions.notion_a.section", 5)

    def test_A24_relation_source_and_target_are_required_text(self):
        self.required("relations.0", ["source", "target"])
        self.refused("relations.0.source", 5)
        self.refused("relations.0.target", 5)

    def test_A24_relation_old_names_are_refused(self):
        self.unknown_key("relations.0", "source_id")
        self.unknown_key("relations.0", "target_id")

    def test_A24_relation_status_is_the_raw_professor_value(self):
        for status in ("theorique", "reconnue", "demontree"):
            self.accepted("relations.0.status", status)

    def test_A24_source_observed_at_is_required(self):
        self.required("sources.0", ["observed_at"])

    def test_A24_source_observed_at_is_a_date_or_null(self):
        self.accepted("sources.0.observed_at", "2026-11-11")
        self.accepted("sources.0.observed_at", None)
        for date in BAD_DATES:
            self.refused("sources.0.observed_at", date)


class EntitiesTest(StateCase):
    """A25 et A27 : `network` retirée, `names` ajoutée."""

    def test_A25_network_entity_is_refused(self):
        state = load_state("complete")
        state["network"] = {"nodes": [], "edges": [], "highlights": []}
        self.assertEqual(paths_of(state), ["network"])

    def test_A25_network_is_not_among_the_missing_entities(self):
        found = {path for path, _ in output.validate(load_state("empty"))}
        self.assertNotIn("network", found)

    def test_A27_names_fields_are_required(self):
        self.required("names", ["en"])

    def test_A27_names_unknown_language_is_refused(self):
        self.unknown_key("names", "fr")

    def test_A27_names_en_maps_identifiers_to_text(self):
        self.accepted("names.en", {})
        self.refused("names.en.notion_a", 5)
        self.refused("names.en", ["Notion A"])

    def test_A27_names_missing_entity(self):
        state = load_state("complete")
        del state["names"]
        self.assertEqual(paths_of(state), ["names"])


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
