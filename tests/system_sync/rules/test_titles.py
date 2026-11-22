"""Tests de `system_sync.rules.titles` (T8, cas N1 à N12 et L1 à L9 ; A7, A17, A18, A19, A23).

Contrat de T8.b (`from system_sync.rules import titles`, aucune fonction publique ne lève,
appel par mot-clé compris, aucune lecture de source ni de fichier : les fonctions reçoivent
les données déjà lues, l'état précédent compris, que T10 lira dans `data/historique/`) :
- `school_titles(level, card_ranks, facts, rules) -> tuple[dict]` : un élément par titre
  de `rules["titles"]` dont le type n'est pas `school_achievements`, dans l'ordre de la
  configuration (les types sont des données : `level_at_least` avec `value`,
  `rank_on_all_cards` avec `rank`). Clés : `id` (clé de la configuration), `type`,
  `obtained` (`StatedValue`) et `progress` (`{"current", "target", "percent"}`, `percent`
  arrondi à 2 décimales et plafonné à 100, ou `None` sans mesure). Un élément qui porte un
  `name` ne contient jamais « (42) » (A23).
  - `level` : `StatedValue` du niveau (`Api42Result.level`) ou `None`. `obtained` vaut
    observé vrai ou faux, avec les sources du niveau ; progression = niveau sur seuil.
    Niveau `None`, non mesurable, négatif ou non fini : `unmeasurable` (valeur `None`) ;
    `None` ou un niveau `unmeasurable` rend le code du niveau (`cursus_absent`...) ou
    `api_unavailable`, un nombre invalide rend `level_invalid`. Un niveau énorme (1e9)
    dépasse le seuil : obtenu.
  - `card_ranks` : dict nom de carte vers `StatedValue` de `ranks.rank_card`. Progression =
    cartes au moins au rang requis (ordre de `rules["ranks"]`, Nation vaut au moins S) sur
    cartes. Un rang `none` ne compte pas et le titre reste « non obtenu » (observé faux,
    A19). Une carte dont le rang est `insufficient` ou `unmeasurable` rend le titre
    `insufficient` (raison `card_rank_missing`) ; aucune carte (`{}` ou `None`) rend
    `insufficient` (raison `no_cards`), jamais vrai par vacuité.
  - `facts` : `read_events(...).facts` ou `None` (A7). Un titre dont l'identifiant (clé de
    `rules["titles"]`) est la `value` d'un fait `titre` est `obtained` observé vrai, sources
    contenant `events`, même si ses conditions ne sont plus remplies (`c:142`), pour tout
    titre configuré. Sans fait, calcul par les conditions. Un fait `titre` inutilisable
    (identifiant inconnu, valeur vide ou non texte) est ignoré, comme une autre métrique.
  - `rules` : le dictionnaire de `config.load_rules`. Inutilisable : `()`.
- `title_anomalies(facts, rules) -> tuple[Anomaly]` : pour chaque fait `titre`, fichier
  `evenements.csv` et ligne du fait : `unknown_title` (identifiant absent de la
  configuration) ou `unusable_title_fact` (valeur vide ou non texte).
- `achievements_entity(achievements, complete) -> dict` (A23) : `achievements` est
  `Api42Result.achievements` (dicts `id`, `name`, `description`, `obtained` statuée,
  `obtained_on`, `title`), `complete` la valeur statuée de `Api42Result.complete`.
  Retour : `complete` (la valeur reçue, `unmeasurable` si elle est inutilisable), `items`
  (tuple de dicts aux six clés, dans l'ordre reçu, sans élément sans `id` ni `name` ni
  doublon d'`id`), `notice_code` (`None`, `full_list_unavailable` quand `complete` est
  `unmeasurable`, sinon `no_achievements` quand `items` est vide) et `notice` (phrase
  française de ce code, ou `None`).
- `achievement_anomalies(achievements, complete, catalogue_ids=None) -> tuple[Anomaly]` :
  `malformed_achievement` (sans `id` ou sans `name`) et `duplicate_achievement` (même
  `id`), `line` valant la position 1 de la liste ; si `complete` est observé et que
  `catalogue_ids` (identifiants de la liste complète) est donné, `unlisted_achievement`
  pour un élément obtenu absent de cette liste (L9, il reste dans `items`).
Codes à ajouter à `model.REASON_CODES` : `card_rank_missing`, `no_cards`,
`no_achievements` (`api_unavailable`, `level_invalid`, `cursus_absent` et
`full_list_unavailable` existent déjà).
"""

import copy
import json
import math
import re
import unittest
from pathlib import Path

from system_sync import config, model

try:
    from system_sync.rules import titles
except ImportError:
    titles = None  # chaque test échoue séparément tant que le module manque

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "tests" / "fixtures" / "titles"
RULES = FIXTURES / "rules_demo.toml"
RULES_DIR = ROOT / "source" / "system_sync" / "rules"
ITEM_KEYS = {"id", "name", "description", "obtained", "obtained_on", "title"}
ENTITY_KEYS = {"complete", "items", "notice_code", "notice"}
PROGRESS_KEYS = {"current", "target", "percent"}
FULL_LIST_DOWN = model.unmeasurable(
    "Liste complète indisponible : test",
    "full_list_unavailable",
)
DEFAULT = object()
GARBAGE = (None, 3, "x", [None, 3, {}], {"a": 1}, [{"id": 1}], float("nan"))


def stated(data):
    """Reconstruit une valeur statuée depuis sa forme JSON de fixture."""
    return model.StatedValue(
        data["value"],
        data["status"],
        tuple(data["sources"]),
        data["reason"],
        data["reason_code"],
    )


def load_json(name):
    """Lit une fixture JSON de `tests/fixtures/titles/`."""
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def load_ranks():
    """Rangs de la fixture `three_cards_ranks.json` : S, S et A."""
    return {name: stated(data) for name, data in load_json("three_cards_ranks.json").items()}


def load_items(name):
    """Achievements d'une fixture, `obtained` en valeur statuée."""
    return [{**item, "obtained": stated(item["obtained"])} for item in load_json(name)]


def level_of(number):
    """Niveau observé de l'API 42."""
    return model.observed(number, ("api42",))


def fact(metric, value, line, domain=""):
    """Fait au format de `read_events(...).facts`."""
    return {
        "date": "2026-11-20",
        "session": "3",
        "domain": domain,
        "notion": "",
        "metric": metric,
        "value": value,
        "context": "",
        "visual_form": "",
        "proof": "tests/banc-fictif",
        "line": line,
    }


def ranks_with(**changes):
    """Rangs de base où `changes` (nom vers valeur statuée) remplace ou ajoute une carte."""
    return {**load_ranks(), **changes}


def rank_of(value, status="observed"):
    """Rang d'une carte : valeur statuée ou, hors `observed`, manque de mesure."""
    if status == "observed":
        return model.observed(value, ("notions",))
    if status == "insufficient":
        return model.insufficient("rang insuffisant", "card_unmeasurable")
    return model.unmeasurable("rang non mesurable", "card_unmeasurable")


class TitleCase(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(titles, "module system_sync.rules.titles absent")
        self.rules = config.load_rules(RULES)

    def entries(self, level=DEFAULT, card_ranks=None, facts=None, rules=None):
        """Titres indexés par `id`, avec le niveau 12,44 et les rangs S, S, A par défaut."""
        found = titles.school_titles(
            level=level_of(12.44) if level is DEFAULT else level,
            card_ranks=load_ranks() if card_ranks is None else card_ranks,
            facts=facts,
            rules=self.rules if rules is None else rules,
        )
        self.assertIsInstance(found, tuple)
        return {entry["id"]: entry for entry in found}

    def check(self, result, value, status):
        """Vérifie la valeur et le statut d'une valeur statuée."""
        self.assertIsInstance(result, model.StatedValue)
        self.assertEqual((result.value, result.status), (value, status))

    def counts(self, entry):
        """Couple (courant, cible) de la progression d'un titre."""
        return entry["progress"]["current"], entry["progress"]["target"]

    def entity(self, achievements, complete=FULL_LIST_DOWN):
        """Entité `achievements` pour une liste et la valeur `complete`."""
        return titles.achievements_entity(achievements=achievements, complete=complete)

    def reported_titles(self, facts):
        """Anomalies des faits `titre`, par appel de mot-clé."""
        return titles.title_anomalies(facts=facts, rules=self.rules)

    def reported(self, achievements, complete=FULL_LIST_DOWN, catalogue_ids=None):
        """Anomalies d'achievements, par appel de mot-clé."""
        return titles.achievement_anomalies(
            achievements=achievements,
            complete=complete,
            catalogue_ids=catalogue_ids,
        )


class NominalTest(TitleCase):
    def test_N1_level_25_obtains_the_42_title(self):
        entry = self.entries(level_of(25.0))["answer_42"]
        self.check(entry["obtained"], True, "observed")
        self.assertIn("api42", entry["obtained"].sources)
        self.assertEqual(entry["progress"]["current"], 25.0)
        self.assertEqual(entry["progress"]["target"], 25)

    def test_N2_level_24_99_is_not_obtained_at_99_96_percent(self):
        entry = self.entries(level_of(24.99))["answer_42"]
        self.check(entry["obtained"], False, "observed")
        self.assertEqual(set(entry["progress"]), PROGRESS_KEYS)
        self.assertEqual(entry["progress"]["current"], 24.99)
        self.assertAlmostEqual(entry["progress"]["percent"], 99.96, places=2)

    def test_N3_level_30_obtains_the_title_and_progress_is_capped(self):
        entry = self.entries(level_of(30))["answer_42"]
        self.check(entry["obtained"], True, "observed")
        self.assertEqual(entry["progress"]["percent"], 100.0)

    def test_N4_every_card_at_s_obtains_the_system_title(self):
        card_ranks = ranks_with(Gamma=rank_of("S"))
        entry = self.entries(card_ranks=card_ranks)["answer_system"]
        self.check(entry["obtained"], True, "observed")
        self.assertTrue(entry["obtained"].sources)
        self.assertEqual(self.counts(entry), (3, 3))

    def test_N4_a_card_at_nation_counts_as_at_least_s(self):
        card_ranks = ranks_with(Gamma=rank_of("Nation"))
        entry = self.entries(card_ranks=card_ranks)["answer_system"]
        self.check(entry["obtained"], True, "observed")

    def test_N5_cards_s_s_a_are_not_obtained_at_two_out_of_three(self):
        entry = self.entries()["answer_system"]
        self.check(entry["obtained"], False, "observed")
        self.assertTrue(entry["obtained"].sources)
        self.assertEqual(self.counts(entry), (2, 3))
        self.assertAlmostEqual(entry["progress"]["percent"], 66.67, places=2)

    def test_N6_a_card_without_usable_rank_makes_the_system_title_insufficient(self):
        for status in ("insufficient", "unmeasurable"):
            with self.subTest(status=status):
                card_ranks = ranks_with(Gamma=rank_of(None, status))
                entry = self.entries(card_ranks=card_ranks)["answer_system"]
                self.assertEqual(entry["obtained"].status, "insufficient")
                self.assertIsNot(entry["obtained"].value, True)
                self.assertEqual(entry["obtained"].reason_code, "card_rank_missing")

    def test_N7_a_card_without_rank_is_not_obtained_and_not_insufficient(self):
        card_ranks = ranks_with(Gamma=rank_of("none"))
        entry = self.entries(card_ranks=card_ranks)["answer_system"]
        self.check(entry["obtained"], False, "observed")

    def test_N8_an_acquired_title_stays_obtained_when_its_conditions_fall(self):
        card_ranks = ranks_with(Gamma=rank_of("S"), Delta=rank_of("E"))
        found = self.entries(level_of(10.0), card_ranks, load_json("title_facts.json"))
        self.check(found["answer_system"]["obtained"], True, "observed")
        self.assertIn("events", found["answer_system"]["obtained"].sources)
        self.check(found["answer_42"]["obtained"], False, "observed")
        facts = [fact("titre", "answer_42", 3)]
        found = self.entries(level_of(10.0), facts=facts)
        self.check(found["answer_42"]["obtained"], True, "observed")
        self.assertIn("events", found["answer_42"]["obtained"].sources)

    def test_N9_obtained_achievements_are_listed_as_observed(self):
        found = self.entity(load_items("achievements_obtained.json"))
        self.assertEqual([item["id"] for item in found["items"]], [1, 2, 3])
        for item in found["items"]:
            self.check(item["obtained"], True, "observed")
        self.assertEqual(found["items"][0]["obtained_on"], "2025-03-14")
        self.assertEqual(found["items"][2]["title"], "Titre fictif")

    def test_N10_the_complete_list_adds_the_achievements_not_obtained(self):
        complete = model.observed(True, ("api42",))
        found = self.entity(load_items("achievements_complete.json"), complete)
        self.assertEqual([item["id"] for item in found["items"]], [1, 2, 3, 4, 5])
        self.check(found["complete"], True, "observed")
        values = [item["obtained"].value for item in found["items"]]
        self.assertEqual(values, [True, True, True, False, False])
        self.assertIsNone(found["notice_code"])

    def test_N11_without_the_complete_list_the_entity_says_so(self):
        found = self.entity(load_items("achievements_obtained.json"), FULL_LIST_DOWN)
        self.assertEqual(found["complete"].status, "unmeasurable")
        self.assertEqual(found["complete"].reason_code, "full_list_unavailable")
        self.assertEqual(found["notice_code"], "full_list_unavailable")
        self.assertIn("indisponible", found["notice"].lower())

    def test_N12_a_title_added_to_the_configuration_appears_without_code_change(self):
        rules = copy.deepcopy(self.rules)
        rules["titles"]["answer_early"] = {"type": "level_at_least", "value": 10}
        rules["titles"]["answer_system_a"] = {"type": "rank_on_all_cards", "rank": "A"}
        found = self.entries(rules=rules)
        expected = ["answer_42", "answer_system", "answer_early", "answer_system_a"]
        self.assertEqual(list(found), expected)
        self.check(found["answer_early"]["obtained"], True, "observed")
        self.assertEqual(found["answer_early"]["type"], "level_at_least")
        card_ranks = {name: rank_of("A") for name in load_ranks()}
        found = self.entries(card_ranks=card_ranks, rules=rules)
        self.check(found["answer_system_a"]["obtained"], True, "observed")
        self.check(found["answer_system"]["obtained"], False, "observed")

    def test_N12_the_level_threshold_comes_from_the_configuration(self):
        rules = copy.deepcopy(self.rules)
        rules["titles"]["answer_42"]["value"] = 30
        found = self.entries(level_of(25.0), rules=rules)["answer_42"]
        self.check(found["obtained"], False, "observed")
        self.assertEqual(found["progress"]["target"], 30)

    def test_N12_the_required_rank_comes_from_the_configuration(self):
        rules = copy.deepcopy(self.rules)
        rules["titles"]["answer_system"]["rank"] = "A"
        card_ranks = ranks_with(Alpha=rank_of("A"), Beta=rank_of("A"))
        found = self.entries(card_ranks=card_ranks, rules=rules)["answer_system"]
        self.check(found["obtained"], True, "observed")


class LimitTest(TitleCase):
    def test_L1_absent_level_is_unmeasurable_and_the_system_title_still_computed(self):
        absent = model.unmeasurable("cursus 21 absent", "cursus_absent")
        for level in (None, absent):
            with self.subTest(level=level):
                found = self.entries(level)
                self.check(found["answer_42"]["obtained"], None, "unmeasurable")
                self.assertIn(found["answer_42"]["obtained"].reason_code, model.REASON_CODES)
                self.check(found["answer_system"]["obtained"], False, "observed")
        code = self.entries(absent)["answer_42"]["obtained"].reason_code
        self.assertEqual(code, "cursus_absent")

    def test_L2_negative_or_not_finite_level_is_invalid(self):
        for number in (-1.0, float("nan"), float("inf"), -math.inf):
            with self.subTest(level=number):
                entry = self.entries(level_of(number))["answer_42"]
                self.check(entry["obtained"], None, "unmeasurable")
                self.assertEqual(entry["obtained"].reason_code, "level_invalid")
                self.assertIsNone(entry["progress"])

    def test_L2_a_huge_level_exceeds_the_threshold(self):
        entry = self.entries(level_of(1e9))["answer_42"]
        self.check(entry["obtained"], True, "observed")
        self.assertEqual(entry["progress"]["percent"], 100.0)

    def test_L3_no_card_makes_the_system_title_insufficient_never_true(self):
        for card_ranks in ({}, None):
            with self.subTest(card_ranks=card_ranks):
                found = titles.school_titles(
                    level=level_of(12.44),
                    card_ranks=card_ranks,
                    facts=None,
                    rules=self.rules,
                )
                entry = {item["id"]: item for item in found}["answer_system"]
                self.assertEqual(entry["obtained"].status, "insufficient")
                self.assertIsNot(entry["obtained"].value, True)
                self.assertEqual(entry["obtained"].reason_code, "no_cards")

    def test_L4_absent_or_empty_achievements_give_an_explicit_notice(self):
        for achievements in (None, [], ()):
            with self.subTest(achievements=achievements):
                found = self.entity(achievements)
                self.assertEqual(found["items"], ())
                self.assertEqual(found["notice_code"], "full_list_unavailable")
        found = self.entity(None, model.observed(True, ("api42",)))
        self.assertEqual(found["notice_code"], "no_achievements")
        self.assertTrue(found["notice"].strip())
        self.assertIn(found["notice_code"], model.REASON_CODES)

    def test_L5_achievement_without_id_or_name_is_reported_and_left_out(self):
        base = load_items("achievements_obtained.json")
        no_id = {key: value for key, value in base[1].items() if key != "id"}
        no_name = {key: value for key, value in base[2].items() if key != "name"}
        items = [base[0], no_id, no_name, {**base[2], "id": 9}]
        self.assertEqual([item["id"] for item in self.entity(items)["items"]], [1, 9])
        found = self.reported(items)
        expected = [("malformed_achievement", 2), ("malformed_achievement", 3)]
        self.assertEqual([(a.kind, a.line) for a in found], expected)
        self.assertTrue(all(isinstance(a, model.Anomaly) and a.file for a in found))

    def test_L6_duplicate_achievements_are_kept_once_and_reported(self):
        base = load_items("achievements_obtained.json")
        items = [base[0], {**base[0], "name": "Autre nom"}, base[1]]
        found = self.entity(items)["items"]
        kept = [(item["id"], item["name"]) for item in found]
        self.assertEqual(kept, [(1, base[0]["name"]), (2, base[1]["name"])])
        reported = [(a.kind, a.line) for a in self.reported(items)]
        self.assertEqual(reported, [("duplicate_achievement", 2)])

    def test_L7_no_title_fact_is_the_first_synchronisation(self):
        for facts in (None, [], [fact("niveau", "avancé", 2)]):
            with self.subTest(facts=facts):
                self.assertEqual(self.reported_titles(facts), ())
                entry = self.entries(facts=facts)["answer_system"]
                self.check(entry["obtained"], False, "observed")

    def test_L8_an_unusable_title_fact_is_ignored_with_an_anomaly(self):
        facts = load_json("title_facts.json")
        found = self.entries(facts=facts[:1] + facts[2:])
        self.check(found["answer_system"]["obtained"], False, "observed")
        found = self.reported_titles(facts)
        expected = [
            ("unknown_title", 8),
            ("unusable_title_fact", 9),
            ("unusable_title_fact", 10),
        ]
        self.assertEqual([(a.kind, a.line) for a in found], expected)
        self.assertTrue(all(a.file == "evenements.csv" for a in found))
        wrong = [fact("niveau", "answer_system", 5), fact("certification", "x", 6)]
        self.assertEqual(self.reported_titles(wrong), ())
        self.check(self.entries(facts=wrong)["answer_system"]["obtained"], False, "observed")

    def test_L9_an_obtained_achievement_missing_from_the_complete_list_is_added(self):
        items = load_items("achievements_complete.json")
        complete = model.observed(True, ("api42",))
        found = self.reported(items, complete, catalogue_ids={1, 2, 4, 5})
        self.assertEqual([(a.kind, a.line) for a in found], [("unlisted_achievement", 3)])
        self.assertIn(3, [item["id"] for item in self.entity(items, complete)["items"]])
        self.assertEqual(self.reported(items, FULL_LIST_DOWN, catalogue_ids=None), ())


class AmendmentTest(TitleCase):
    def scenarios(self):
        """Quatre situations qui couvrent les statuts d'un titre."""
        return (
            self.entries(level_of(30)),
            self.entries(level_of(24.0)),
            self.entries(None, card_ranks={}),
            self.entries(level_of(-3.0), ranks_with(Gamma=rank_of(None, "unmeasurable"))),
        )

    def test_A17_titles_use_the_statuses_of_the_model_with_their_conditions(self):
        seen = set()
        for found in self.scenarios():
            for entry in found.values():
                state = entry["obtained"]
                self.assertIsInstance(state, model.StatedValue)
                self.assertIn(state.status, model.STATUSES)
                self.assertNotEqual(state.status, "estimated")
                seen.add(state.status)
                if state.status == "observed":
                    self.assertIsInstance(state.value, bool)
                    self.assertTrue(state.sources)
                if state.status == "unmeasurable":
                    self.assertIsNone(state.value)
        self.assertEqual(seen, {"observed", "insufficient", "unmeasurable"})

    def test_A18_every_missing_measure_carries_a_reason_with_its_code(self):
        reasons = 0
        for found in self.scenarios():
            for entry in found.values():
                state = entry["obtained"]
                if state.status in model.REASON_REQUIRED:
                    reasons += 1
                    self.assertTrue(state.reason.strip())
                    self.assertIn(state.reason_code, model.REASON_CODES)
        self.assertGreaterEqual(reasons, 3)
        for found in (self.entity(None), self.entity(None, model.observed(True, ("api42",)))):
            self.assertIn(found["notice_code"], model.REASON_CODES)

    def test_A19_rank_none_counts_as_not_reached(self):
        card_ranks = ranks_with(Beta=rank_of("none"), Gamma=rank_of("none"))
        entry = self.entries(card_ranks=card_ranks)["answer_system"]
        self.check(entry["obtained"], False, "observed")
        self.assertEqual(self.counts(entry), (1, 3))

    def test_A23_titles_keep_only_the_two_answer_titles(self):
        found = titles.school_titles(
            level=level_of(12.44),
            card_ranks=load_ranks(),
            facts=None,
            rules=self.rules,
        )
        self.assertEqual([entry["id"] for entry in found], ["answer_42", "answer_system"])
        for entry in found:
            self.assertNotIn("(42)", entry.get("name", ""))

    def test_A23_items_keep_the_six_keys_and_the_entity_its_four(self):
        found = self.entity(load_items("achievements_complete.json"))
        self.assertEqual(set(found), ENTITY_KEYS)
        for item in found["items"]:
            self.assertEqual(set(item), ITEM_KEYS)

    def test_A23_complete_is_a_stated_boolean(self):
        found = self.entity([], model.observed(True, ("api42",)))
        self.check(found["complete"], True, "observed")
        found = self.entity(load_items("achievements_obtained.json"), FULL_LIST_DOWN)
        self.check(found["complete"], None, "unmeasurable")
        self.assertEqual(found["complete"].reason_code, "full_list_unavailable")


class ContractTest(TitleCase):
    def test_contract_no_public_function_raises_on_garbage(self):
        for junk in GARBAGE:
            with self.subTest(junk=junk):
                found = titles.school_titles(
                    level=junk,
                    card_ranks=junk,
                    facts=junk,
                    rules=self.rules,
                )
                self.assertIsInstance(found, tuple)
                self.assertIsInstance(
                    titles.title_anomalies(facts=junk, rules=self.rules),
                    tuple,
                )
                self.assertIsInstance(
                    titles.achievement_anomalies(
                        achievements=junk,
                        complete=junk,
                        catalogue_ids=junk,
                    ),
                    tuple,
                )
                entity = titles.achievements_entity(achievements=junk, complete=junk)
                self.assertEqual(set(entity), ENTITY_KEYS)
                self.assertIsInstance(entity["items"], tuple)
        for rules in (None, {}, {"titles": 3}, {"titles": {"x": 3}}, {"titles": {"x": {}}}):
            with self.subTest(rules=rules):
                found = titles.school_titles(
                    level=level_of(30),
                    card_ranks=load_ranks(),
                    facts=None,
                    rules=rules,
                )
                self.assertIsInstance(found, tuple)

    def test_contract_positional_call_matches_keyword_call(self):
        args = (level_of(30), load_ranks(), None, self.rules)
        by_keyword = titles.school_titles(
            level=args[0],
            card_ranks=args[1],
            facts=args[2],
            rules=args[3],
        )
        self.assertEqual(titles.school_titles(*args), by_keyword)


class ArchitectureTest(unittest.TestCase):
    def titles_source(self):
        path = RULES_DIR / "titles.py"
        self.assertTrue(path.is_file(), "module system_sync.rules.titles absent")
        return path.read_text(encoding="utf-8")

    def test_criterion_2_rules_never_import_sources(self):
        self.titles_source()
        pattern = re.compile(r"^(from|import) .*sources", re.MULTILINE)
        found = [
            path.name
            for path in sorted(RULES_DIR.glob("*.py"))
            if pattern.search(path.read_text(encoding="utf-8"))
        ]
        self.assertEqual(found, [])

    def test_N12_no_title_name_is_hard_coded(self):
        text = self.titles_source()
        pattern = re.compile(r"answer_42|answer_system|achievements_42")
        found = [
            f"{number}: {line.strip()}"
            for number, line in enumerate(text.splitlines(), 1)
            if pattern.search(line)
        ]
        self.assertEqual(found, [])


if __name__ == "__main__":
    unittest.main()
