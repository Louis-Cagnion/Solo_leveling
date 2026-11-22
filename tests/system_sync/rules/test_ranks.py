"""Tests de `system_sync.rules.ranks` (T6, cas N1 à N15 et L1 à L12 ; A17 à A21).

Contrat de T6.b (`from system_sync.rules import ranks`, aucune fonction publique ne lève,
aucune lecture de source : les fonctions reçoivent les données déjà lues) :
- `card`, `cards` : enregistrements de `read_cards(...).records` (clés `name`, `tiers`,
  `ids`, `certifications`, `has_certifications`...) ; `tiers` associe « Débutant »,
  « Intermédiaire », « Avancé » et « Transcendée » à des listes d'identifiants.
- `notions` : enregistrements de `read_notions(...).records` (clés `id`, `state`, `line`).
- `facts` : `read_events(...).facts` (clés `date` ISO ou `None`, `domain`, `metric`,
  `value`, `line`) ; `None` vaut une liste vide. Le fait `niveau` d'une carte porte son
  nom dans `domain`. Un fait `certification` porte son code dans `value` ; il vaut pour
  chaque carte qui cite ce code (A2), quel que soit son `domain`.
- `rules` : le dictionnaire de `config.load_rules`. Les paliers des règles sont en
  minuscules (`avancé`), les clés de `tiers` ont leur majuscule (`Avancé`).
- `rank_card(card, notions, facts, rules) -> StatedValue` : rang de la carte parmi
  `E, D, C, B, A, S, Nation` ou `"none"` (A19). Statuts : `observed` (E, C, A, S, Nation, D
  d'après un fait, « none »), `estimated` (D d'après les notions : raison `tier_fallback` ;
  B : raison `half_tier_rule`), `unmeasurable` (valeur `None`) pour une carte `None`, des
  données ou des règles inutilisables. `sources` : `events` si un fait compte, `notions`
  pour tout rang tiré des notions (« none » compris). Une carte dont la liste de
  certifications est illisible (aucune colonne) reste à S : Nation n'est jamais « non
  mesurable » comme rang. Un fait `niveau` vaut pour les rangs inférieurs (A9) et un
  niveau validé ne retombe pas.
- `next_rank(card, notions, facts, rules) -> dict | None` (A20) : `None` à Nation ou pour
  une carte inutilisable, sinon `rank` (le rang suivant), `condition` (texte tiré des
  règles, qui nomme leur état ou leur niveau), `progress` (valeur statuée), `total`
  (entier ou `None`) et `missing` (liste de `{id, state}`).
  - E : `total` 1, `progress` observé (nombre de notions suivies), `missing` = les notions
    de la carte non suivies (état « non rencontrée » ou « déclarée »).
  - D (sans fait) et B : `progress` observé = notions du palier au moins à l'état exigé,
    `total` = notions distinctes du palier pour D (la moitié par excès pour B), `missing`
    = notions du palier sous l'état exigé, avec leur état. Palier vide : `progress`
    insufficient (raison `empty_tier`), `total` 0, `missing` vide.
  - C, A, S (fait `niveau`) : `progress` insufficient (raison `level_fact_missing`),
    `total` `None`, `missing` vide.
  - Nation : `progress` observé = certifications obtenues, `total` = certifications
    retenues, `missing` = les codes non obtenus (`id` = code). Carte sans colonne
    « Certifications » : `progress` unmeasurable (raison `certification_list_unreadable`).
- `card_certifications(card, cards, notions, facts, rules) -> tuple[dict]` (A21) : une
  entrée par code cité dans les cellules de `card.certifications` (ordre de première
  apparition), plus une par fait `certification` de la carte dont le code n'est cité
  par aucune cellule ; un code est un mot de majuscules, chiffres et tirets qui commence
  par une majuscule (« ALPHA-1 et ALPHA-2 (fictives) » cite ALPHA-1 et ALPHA-2). Clés :
  `code`, `detail` (texte ou `None`), `notions` (identifiants, toutes cartes confondues),
  `conditions` (`None`), `obtained` (observé, vrai si un fait porte le code, faux sinon),
  `obtained_on` (date du fait ou `None`) et `accessible` (`estimated` : toutes les
  notions au moins à `states.cert_ready_at_least`, « déclarée » exclue ; `unmeasurable`
  sans notion, raison `no_certification_notion`, ou sans colonne, raison
  `certification_list_unreadable`).
- `rank_anomalies(cards, notions, facts, rules) -> tuple[Anomaly]` : une anomalie par
  état de notion inconnu (`unknown_state`, `notions.md`, ligne de la notion), par fait
  `niveau` de valeur inconnue (`unknown_level`), par fait dont `domain` n'est aucune
  carte (`unknown_card`) et par fait `certification` dont le code n'est cité par aucune
  carte (`unknown_certification`) ; les faits portent le fichier `evenements.csv` et leur
  ligne, le détail nomme l'identifiant, le domaine ou le code reçu.
Codes à ajouter à `model.REASON_CODES` : `tier_fallback`, `half_tier_rule`, `empty_tier`,
`level_fact_missing` (`card_unmeasurable`, `certification_list_unreadable` et
`no_certification_notion` existent déjà).
"""

import copy
import json
import re
import unittest
from pathlib import Path

from system_sync import config, model

try:
    from system_sync.rules import ranks
except ImportError:
    ranks = None  # chaque test échoue séparément tant que le module manque

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "tests" / "fixtures" / "ranks"
RULES = FIXTURES / "rules_demo.toml"
STRICT_B = FIXTURES / "rules_strict_b.toml"
RULES_DIR = ROOT / "source" / "system_sync" / "rules"
RANK_VALUES = {"E", "D", "C", "B", "A", "S", "Nation", "none"}
NEXT_RANK_KEYS = {"rank", "condition", "progress", "total", "missing"}
CERTIFICATION_KEYS = {
    "code",
    "detail",
    "notions",
    "conditions",
    "obtained",
    "obtained_on",
    "accessible",
}
# Palier débutant en dessous de « comprise », avancées sous la moitié de « appliquée ».
WEAK_BEGINNER = {"alpha-d1": "en cours", "alpha-d2": "découverte"}
WEAK_ADVANCED = {"alpha-a1": "en cours", "alpha-a2": "en cours"}


def load_json(name):
    """Lit une fixture JSON de `tests/fixtures/ranks/`."""
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def fact(domain, metric, value, line=50, date="2026-11-01"):
    """Construit un fait au format de `read_events(...).facts`."""
    return {
        "date": date,
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


def level(value, line=50, date="2026-11-01"):
    """Fait `niveau` de la carte Alpha."""
    return fact("Alpha", "niveau", value, line, date)


def patched(notions, changes):
    """Copie des notions où `changes` (identifiant vers état) remplace ou ajoute."""
    found = {record["id"]: dict(record) for record in notions}
    for note_id, state in changes.items():
        record = found.setdefault(
            note_id,
            {**notions[0], "id": note_id, "line": 100 + len(found)},
        )
        record["state"] = state
    return list(found.values())


class RankCase(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(ranks, "module system_sync.rules.ranks absent")
        self.rules = config.load_rules(RULES)
        self.cards = {card["name"]: card for card in load_json("demo_cards.json")}
        self.notions = load_json("demo_notions.json")
        self.facts = load_json("demo_facts.json")

    def rank(self, name, notions=None, facts=None, rules=None, card=None):
        """Rang de la carte `name`, avec les données de base pour ce qui manque."""
        return ranks.rank_card(
            card or self.cards[name],
            self.notions if notions is None else notions,
            self.facts if facts is None else facts,
            self.rules if rules is None else rules,
        )

    def next_rank(self, name, notions=None, facts=None, rules=None):
        """Rang suivant de la carte `name`, avec les données de base par défaut."""
        return ranks.next_rank(
            self.cards[name],
            self.notions if notions is None else notions,
            self.facts if facts is None else facts,
            self.rules if rules is None else rules,
        )

    def certs(self, name, notions=None, facts=None, rules=None):
        """Certifications de la carte `name`, indexées par code."""
        found = ranks.card_certifications(
            self.cards[name],
            list(self.cards.values()),
            self.notions if notions is None else notions,
            self.facts if facts is None else facts,
            self.rules if rules is None else rules,
        )
        return {entry["code"]: entry for entry in found}

    def anomalies(self, notions=None, facts=None):
        """Anomalies de règles sur les trois cartes de la fixture."""
        return ranks.rank_anomalies(
            list(self.cards.values()),
            self.notions if notions is None else notions,
            self.facts if facts is None else facts,
            self.rules,
        )

    def check(self, result, value, status):
        """Vérifie la valeur et le statut d'une valeur statuée."""
        self.assertIsInstance(result, model.StatedValue)
        self.assertEqual((result.value, result.status), (value, status))


class NominalTest(RankCase):
    def test_N1_card_without_followed_notion_has_no_rank(self):
        self.check(self.rank("Gamma"), "none", "observed")

    def test_N2_one_discovered_notion_gives_rank_e(self):
        self.check(self.rank("Beta"), "E", "observed")

    def test_N3_declared_notions_only_give_no_rank(self):
        notions = patched(self.notions, {"beta-d1": "déclarée"})
        self.check(self.rank("Beta", notions), "none", "observed")

    def test_N4_rank_d_is_estimated_when_every_beginner_notion_is_understood(self):
        result = self.rank("Alpha", facts=[])
        self.check(result, "D", "estimated")
        self.assertEqual(result.reason_code, "tier_fallback")

    def test_N5_rank_d_is_observed_with_the_beginner_level_fact(self):
        notions = patched(self.notions, WEAK_BEGINNER)
        result = self.rank("Alpha", notions, [level("débutant")])
        self.check(result, "D", "observed")
        self.assertIn("events", result.sources)

    def test_N6_rank_c_is_observed_with_the_intermediate_level_fact(self):
        notions = patched(self.notions, WEAK_ADVANCED)
        result = self.rank("Alpha", notions, [level("intermédiaire")])
        self.check(result, "C", "observed")
        self.assertIn("events", result.sources)

    def test_N7_rank_b_is_estimated_with_half_of_the_advanced_notions_applied(self):
        result = self.rank("Alpha")
        self.check(result, "B", "estimated")
        self.assertEqual(result.reason_code, "half_tier_rule")
        self.assertLessEqual({"events", "notions"}, set(result.sources))

    def test_N8_rank_a_and_rank_s_are_observed_with_their_level_facts(self):
        for fact_value, expected in (("avancé", "A"), ("transcendée", "S")):
            with self.subTest(fact=fact_value):
                result = self.rank("Alpha", facts=[level(fact_value)])
                self.check(result, expected, "observed")
                self.assertIn("events", result.sources)

    def test_N9_nation_when_s_and_every_retained_certification_are_obtained(self):
        facts = [
            level("transcendée"),
            fact("Alpha", "certification", "ALPHA-1"),
            fact("Alpha", "certification", "ALPHA-2"),
        ]
        self.check(self.rank("Alpha", facts=facts), "Nation", "observed")

    def test_N10_nation_when_s_and_no_retained_certification(self):
        card = copy.deepcopy(self.cards["Alpha"])
        card["certifications"] = {}
        result = self.rank("Alpha", facts=[level("transcendée")], card=card)
        self.check(result, "Nation", "observed")

    def test_N11_displayed_rank_is_the_highest_one_with_all_previous_conditions(self):
        # B a sa condition de notions, mais sans fait C le rang reste D (A9).
        self.check(self.rank("Alpha", facts=[]), "D", "estimated")
        self.check(self.rank("Alpha", facts=[level("intermédiaire")]), "B", "estimated")

    def test_N12_a_validated_level_never_falls_back(self):
        notions = patched(self.notions, {i: "découverte" for i in self.cards["Alpha"]["ids"]})
        result = self.rank("Alpha", notions, [level("intermédiaire")])
        self.check(result, "C", "observed")

    def test_N13_missing_notions_for_the_next_rank_are_listed_with_their_state(self):
        notions = patched(self.notions, {"alpha-d3": "en cours"})
        self.check(self.rank("Alpha", notions, []), "E", "observed")
        found = self.next_rank("Alpha", notions, [])
        self.assertEqual(found["rank"], "D")
        self.assertEqual((found["progress"].value, found["total"]), (3, 4))
        self.assertEqual(found["missing"], [{"id": "alpha-d3", "state": "en cours"}])
        first = self.next_rank("Gamma")
        self.assertEqual(first["rank"], "E")
        ids = [item["id"] for item in first["missing"]]
        self.assertTrue(ids)
        self.assertLessEqual(set(ids), set(self.cards["Gamma"]["ids"]))

    def test_N14_every_rank_carries_status_sources_and_reason(self):
        weak = patched(self.notions, WEAK_BEGINNER)
        scenarios = (
            ("Gamma", None, None),
            ("Beta", None, None),
            ("Alpha", None, []),
            ("Alpha", weak, [level("débutant")]),
            ("Alpha", None, None),
            ("Alpha", None, [level("avancé")]),
        )
        for name, notions, facts in scenarios:
            with self.subTest(card=name, facts=facts):
                result = self.rank(name, notions, facts)
                self.assertIn(result.status, model.STATUSES)
                self.assertTrue(result.sources)
                self.assertTrue(all(isinstance(s, str) and s for s in result.sources))
                if result.status == "observed":
                    self.assertIsNone(result.reason)
                else:
                    self.assertFalse(model.is_blank(result.reason))
                    self.assertIn(result.reason_code, model.REASON_CODES)

    def test_N15_a_changed_threshold_changes_the_result_without_code_change(self):
        facts = [level("intermédiaire")]
        self.check(self.rank("Alpha", facts=facts), "B", "estimated")
        strict = config.load_rules(STRICT_B)
        self.check(self.rank("Alpha", facts=facts, rules=strict), "C", "observed")


class LimitTest(RankCase):
    def test_L1_none_card_is_unmeasurable_and_an_empty_list_gives_nothing(self):
        result = ranks.rank_card(None, self.notions, self.facts, self.rules)
        self.check(result, None, "unmeasurable")
        self.assertEqual(result.reason_code, "card_unmeasurable")
        self.assertFalse(model.is_blank(result.reason))
        self.assertIsNone(ranks.next_rank(None, self.notions, self.facts, self.rules))
        found = ranks.card_certifications(None, [], self.notions, self.facts, self.rules)
        self.assertEqual(tuple(found), ())
        self.assertEqual(tuple(ranks.rank_anomalies([], [], [], self.rules)), ())

    def test_L2_no_event_and_no_fact_still_gives_the_rank_of_the_notions(self):
        for facts in ([], None):
            with self.subTest(facts=facts):
                result = ranks.rank_card(
                    self.cards["Alpha"],
                    self.notions,
                    facts,
                    self.rules,
                )
                self.check(result, "D", "estimated")
        self.check(self.rank("Alpha", [], []), "none", "observed")

    def test_L3_empty_beginner_tier_never_gives_d_by_vacuity(self):
        notions = patched(self.notions, {"gamma-i1": "comprise"})
        self.check(self.rank("Gamma", notions, []), "E", "observed")
        found = self.next_rank("Gamma", notions, [])
        self.assertEqual(found["rank"], "D")
        self.assertEqual(found["progress"].status, "insufficient")
        self.assertEqual(found["progress"].reason_code, "empty_tier")
        self.assertEqual((found["total"], found["missing"]), (0, []))

    def test_L4_empty_advanced_tier_never_gives_b(self):
        notions = patched(self.notions, {"gamma-i1": "comprise"})
        facts = [fact("Gamma", "niveau", "intermédiaire")]
        self.check(self.rank("Gamma", notions, facts), "C", "observed")
        found = self.next_rank("Gamma", notions, facts)
        self.assertEqual(found["rank"], "B")
        self.assertEqual(found["progress"].status, "insufficient")
        self.assertEqual(found["progress"].reason_code, "empty_tier")

    def test_L5_unknown_notion_state_is_reported_and_never_raises_the_rank(self):
        notions = patched(self.notions, {"beta-d1": "bizarre"})
        self.check(self.rank("Beta", notions), "none", "observed")
        found = [a for a in self.anomalies(notions) if a.kind == "unknown_state"]
        self.assertEqual(len(found), 1)
        record = next(r for r in notions if r["id"] == "beta-d1")
        self.assertEqual((found[0].file, found[0].line), ("notions.md", record["line"]))
        self.assertIn("beta-d1", found[0].detail)
        notions = patched(self.notions, {"alpha-d1": "bizarre"})
        self.check(self.rank("Alpha", notions, []), "E", "observed")

    def test_L6_unknown_level_fact_is_ignored_and_reported(self):
        facts = [level("maître", line=7)]
        self.assertEqual(
            self.rank("Alpha", facts=facts).value,
            self.rank("Alpha", facts=[]).value,
        )
        found = [a for a in self.anomalies(facts=facts) if a.kind == "unknown_level"]
        self.assertEqual([(a.file, a.line) for a in found], [("evenements.csv", 7)])
        self.assertIn("maître", found[0].detail)

    def test_L7_fact_of_an_unknown_card_is_reported_and_never_attributed(self):
        stray = fact("Linux et noyau", "niveau", "intermédiaire", line=9)
        for name in self.cards:
            with self.subTest(card=name):
                self.assertEqual(
                    self.rank(name, facts=[stray]),
                    self.rank(name, facts=[]),
                )
        found = [a for a in self.anomalies(facts=[stray]) if a.kind == "unknown_card"]
        self.assertEqual([(a.file, a.line) for a in found], [("evenements.csv", 9)])
        self.assertIn("Linux et noyau", found[0].detail)

    def test_L8_duplicate_facts_count_once_and_the_highest_level_stays(self):
        notions = patched(self.notions, {**WEAK_BEGINNER, **WEAK_ADVANCED})
        twice = [level("débutant", line=2), level("débutant", line=3)]
        self.check(self.rank("Alpha", notions, twice), "D", "observed")
        older = level("intermédiaire", line=2, date="2026-10-01")
        newer = level("débutant", line=3, date="2026-10-05")
        for facts in ([older, newer], [newer, older]):
            with self.subTest(order=[f["value"] for f in facts]):
                self.check(self.rank("Alpha", notions, facts), "C", "observed")

    def test_L9_obtained_certification_unknown_to_the_card_is_reported(self):
        stray = fact("Alpha", "certification", "ZZ-9", line=8)
        facts = [level("transcendée"), stray]
        self.check(self.rank("Alpha", facts=facts), "S", "observed")
        found = [a for a in self.anomalies(facts=facts) if a.kind == "unknown_certification"]
        self.assertEqual([(a.file, a.line) for a in found], [("evenements.csv", 8)])
        self.assertIn("ZZ-9", found[0].detail)

    def test_L10_nation_depends_on_the_list_only_once_s_is_reached(self):
        beginner = {"beta-d1": "comprise", "beta-d2": "comprise", "beta-d3": "comprise"}
        advanced = {"beta-a1": "appliquée", "beta-a2": "appliquée"}
        notions = patched(self.notions, beginner)
        facts = [fact("Beta", "niveau", "intermédiaire")]
        self.check(self.rank("Beta", notions, facts), "C", "observed")
        notions = patched(self.notions, {**beginner, **advanced})
        facts = [fact("Beta", "niveau", "transcendée")]
        self.check(self.rank("Beta", notions, facts), "S", "observed")
        found = self.next_rank("Beta", notions, facts)
        self.assertEqual(found["rank"], "Nation")
        self.assertEqual(found["progress"].status, "unmeasurable")
        self.assertEqual(found["progress"].reason_code, "certification_list_unreadable")

    def test_L11_exact_half_of_the_advanced_notions_gives_b(self):
        for applied, expected in ((2, "B"), (1, "C")):
            states = ["appliquée"] * applied + ["en cours"] * (4 - applied)
            changes = dict(zip(self.cards["Alpha"]["tiers"]["Avancé"], states))
            with self.subTest(applied=applied):
                result = self.rank(
                    "Alpha",
                    patched(self.notions, changes),
                    [level("intermédiaire")],
                )
                self.assertEqual(result.value, expected)

    def test_L12_duplicate_notion_in_a_card_is_counted_once(self):
        card = copy.deepcopy(self.cards["Beta"])
        card["tiers"]["Débutant"] = ["beta-d1", "beta-d1", "beta-d2", "beta-d3"]
        states = {"beta-d1": "comprise", "beta-d2": "comprise", "beta-d3": "en cours"}
        notions = patched(self.notions, states)
        found = ranks.next_rank(card, notions, [], self.rules)
        self.assertEqual(found["rank"], "D")
        self.assertEqual((found["progress"].value, found["total"]), (2, 3))
        self.assertEqual([item["id"] for item in found["missing"]], ["beta-d3"])


class AmendmentTest(RankCase):
    def test_A19_rank_values_are_closed_and_none_is_a_string(self):
        for name in self.cards:
            result = self.rank(name)
            self.assertIn(result.value, RANK_VALUES, name)
        self.assertEqual(self.rank("Gamma").value, "none")
        self.assertIsNot(self.rank("Gamma").value, None)

    def test_A20_next_rank_has_the_closed_shape(self):
        notions = patched(self.notions, {"alpha-d3": "en cours"})
        found = self.next_rank("Alpha", notions, [])
        self.assertEqual(set(found), NEXT_RANK_KEYS)
        self.assertIsInstance(found["progress"], model.StatedValue)
        self.assertIsInstance(found["condition"], str)
        self.assertTrue(found["condition"].strip())
        self.assertIsInstance(found["total"], int)
        for item in found["missing"]:
            self.assertEqual(set(item), {"id", "state"})

    def test_A20_next_rank_is_none_at_the_maximum_rank(self):
        facts = [
            level("transcendée"),
            fact("Alpha", "certification", "ALPHA-1"),
            fact("Alpha", "certification", "ALPHA-2"),
        ]
        self.assertIsNone(self.next_rank("Alpha", facts=facts))

    def test_A20_condition_text_comes_from_the_rules(self):
        notions = patched(self.notions, {"alpha-a1": "appliquée", "alpha-a2": "en cours"})
        facts = [level("intermédiaire")]
        found = self.next_rank("Alpha", notions, facts)
        self.assertEqual(found["rank"], "B")
        self.assertIn("appliquée", found["condition"])
        strict = config.load_rules(STRICT_B)
        found = self.next_rank("Alpha", notions, facts, strict)
        self.assertEqual(found["rank"], "B")
        self.assertIn("transférée", found["condition"])

    def test_A20_next_rank_of_a_level_fact_is_insufficient_without_total(self):
        found = self.next_rank("Alpha", facts=[level("avancé")])
        self.assertEqual(found["rank"], "S")
        self.assertIn("transcendée", found["condition"])
        self.assertEqual(found["progress"].status, "insufficient")
        self.assertEqual(found["progress"].reason_code, "level_fact_missing")
        self.assertEqual((found["total"], found["missing"]), (None, []))

    def test_A20_next_rank_of_nation_counts_the_obtained_certifications(self):
        facts = [level("transcendée"), fact("Alpha", "certification", "ALPHA-1")]
        found = self.next_rank("Alpha", facts=facts)
        self.assertEqual(found["rank"], "Nation")
        self.assertEqual((found["progress"].value, found["total"]), (1, 2))
        self.assertEqual([item["id"] for item in found["missing"]], ["ALPHA-2"])

    def test_A21_certification_entries_have_the_closed_shape(self):
        found = self.certs("Alpha")
        self.assertEqual(set(found), {"ALPHA-1", "ALPHA-2"})
        for entry in found.values():
            self.assertEqual(set(entry), CERTIFICATION_KEYS)
            self.assertIsNone(entry["conditions"])
            self.assertTrue(entry["detail"] is None or isinstance(entry["detail"], str))
            self.assertIsInstance(entry["obtained"], model.StatedValue)
            self.assertIsInstance(entry["accessible"], model.StatedValue)

    def test_A21_notions_cover_every_card_that_cites_the_code(self):
        expected = {
            "ALPHA-1": {"alpha-d1", "alpha-a1", "gamma-i1"},
            "ALPHA-2": {"alpha-a1"},
        }
        alpha = {code: set(e["notions"]) for code, e in self.certs("Alpha").items()}
        self.assertEqual(alpha, expected)
        gamma = {code: set(e["notions"]) for code, e in self.certs("Gamma").items()}
        self.assertEqual(gamma, {"ALPHA-1": expected["ALPHA-1"]})

    def test_A21_obtained_and_date_come_from_the_certification_fact(self):
        found = self.certs("Alpha")
        self.assertEqual(found["ALPHA-1"]["obtained"].value, True)
        self.assertEqual(found["ALPHA-1"]["obtained"].status, "observed")
        self.assertEqual(found["ALPHA-1"]["obtained_on"], "2026-10-20")
        self.assertEqual(found["ALPHA-2"]["obtained"].value, False)
        self.assertEqual(found["ALPHA-2"]["obtained"].status, "observed")
        self.assertIsNone(found["ALPHA-2"]["obtained_on"])
        # Un code partagé entre deux cartes compte pour chacune d'elles (A2).
        self.assertEqual(self.certs("Gamma")["ALPHA-1"]["obtained"].value, True)

    def test_A21_accessible_needs_every_notion_at_the_ready_state(self):
        cases = (
            ("transférée", True),
            ("retenue", True),
            ("appliquée", False),
            ("déclarée", False),
        )
        for state, expected in cases:
            notions = patched(self.notions, {"alpha-a1": state})
            with self.subTest(state=state):
                accessible = self.certs("Alpha", notions)["ALPHA-2"]["accessible"]
                self.assertEqual(accessible.value, expected)
                self.assertEqual(accessible.status, "estimated")
        notions = patched(self.notions, {"alpha-a1": "retenue"})
        self.assertEqual(self.certs("Alpha", notions)["ALPHA-1"]["accessible"].value, False)

    def test_A21_ready_state_is_read_from_the_rules(self):
        rules = copy.deepcopy(self.rules)
        rules["states"]["cert_ready_at_least"] = "comprise"
        accessible = self.certs("Alpha", rules=rules)["ALPHA-2"]["accessible"]
        self.assertEqual((accessible.value, accessible.status), (True, "estimated"))

    def test_A21_card_without_column_has_no_entry_and_an_unmeasurable_orphan(self):
        self.assertEqual(self.certs("Beta"), {})
        facts = [fact("Beta", "certification", "ZZ-9")]
        accessible = self.certs("Beta", facts=facts)["ZZ-9"]["accessible"]
        self.assertEqual((accessible.value, accessible.status), (None, "unmeasurable"))
        self.assertEqual(accessible.reason_code, "certification_list_unreadable")

    def test_A21_code_without_notion_is_unmeasurable(self):
        facts = [fact("Alpha", "certification", "ZZ-9")]
        entry = self.certs("Alpha", facts=facts)["ZZ-9"]
        self.assertEqual(list(entry["notions"]), [])
        self.assertEqual(entry["accessible"].status, "unmeasurable")
        self.assertIsNone(entry["accessible"].value)
        self.assertEqual(entry["accessible"].reason_code, "no_certification_notion")


class ContractTest(RankCase):
    def test_contract_no_public_function_raises_on_garbage(self):
        card = self.cards["Alpha"]
        garbage = (None, 3, "x", [None, 3, {}], {"a": 1}, [{"id": 1, "state": None}])
        for junk in garbage:
            with self.subTest(junk=junk):
                self.assertIsInstance(
                    ranks.rank_card(card, junk, junk, self.rules),
                    model.StatedValue,
                )
                ranks.next_rank(card, junk, junk, self.rules)
                self.assertIsInstance(
                    ranks.card_certifications(card, junk, junk, junk, self.rules),
                    tuple,
                )
                self.assertIsInstance(
                    ranks.rank_anomalies(junk, junk, junk, self.rules),
                    tuple,
                )
        for rules in (None, {}, {"ranks": 3}, {"states": {}, "ranks": {}}):
            with self.subTest(rules=rules):
                result = ranks.rank_card(card, self.notions, self.facts, rules)
                self.check(result, None, "unmeasurable")
                ranks.next_rank(card, self.notions, self.facts, rules)
                ranks.card_certifications(card, [card], self.notions, self.facts, rules)
                ranks.rank_anomalies([card], self.notions, self.facts, rules)


class ArchitectureTest(unittest.TestCase):
    def ranks_source(self):
        path = RULES_DIR / "ranks.py"
        self.assertTrue(path.is_file(), "module system_sync.rules.ranks absent")
        return path.read_text(encoding="utf-8")

    def test_criterion_3_rules_never_import_sources(self):
        self.ranks_source()
        pattern = re.compile(r"^(from|import) .*sources", re.MULTILINE)
        found = [
            path.name
            for path in sorted(RULES_DIR.glob("*.py"))
            if pattern.search(path.read_text(encoding="utf-8"))
        ]
        self.assertEqual(found, [])

    def test_criterion_4_no_rank_is_hard_coded(self):
        text = self.ranks_source()
        pattern = re.compile(r"(==|in) *['\"](E|D|C|B|A|S|Nation)['\"]")
        found = [
            f"{number}: {line.strip()}"
            for number, line in enumerate(text.splitlines(), 1)
            if pattern.search(line)
        ]
        self.assertEqual(found, [])


if __name__ == "__main__":
    unittest.main()
