"""Tests de `system_sync.rules.network` (T9, cas de la fiche portés par A25).

A25 retire l'entité `network` : restent le contrôle des relations et le repérage des
prérequis fragiles. Cas de la fiche écartés (nœuds, arêtes d'appartenance, comptes de
nœuds) : N1, N2, N7, N8, N9, L5 (notion dans deux paliers) et L7 (carte sans notion), ainsi
que la partie « 8 états » de N4. Gardés : N3, N5, N6, L1 à L4, L6 et L8.

Contrat de T9.b (`from system_sync.rules import network`, aucune fonction publique ne lève,
aucune lecture de source : les fonctions reçoivent les données déjà lues, aucune récursion
sur les chaînes de prérequis) :
- `relations` : enregistrements de `read_relations(...).records` (clés `source`, `relation`,
  `target`, `status`, `line`...) ; `notions` : ceux de `read_notions(...).records` (clés
  `id`, `state`, `line`) ; `cards` : ceux de `read_cards(...).records` (clé `ids`) ; `rules` :
  le dictionnaire de `config.load_rules`. `None` vaut une liste vide ; un enregistrement
  inutilisable (pas un dict, clé manquante) est ignoré. Un identifiant est connu s'il est
  celui d'une notion suivie ou figure dans `cards[].ids`.
- `control_relations(relations, notions, cards) -> (kept, anomalies)` : `kept` est le tuple
  des relations gardées, mêmes dictionnaires, ordre d'entrée ; `anomalies` est un tuple de
  `model.Anomaly` (fichier `relations.csv`, ligne de la relation, détail qui nomme les
  identifiants) triées par ligne. Natures :
  - `unknown_endpoint` : une anomalie par extrémité inconnue ; la relation est GARDÉE (A13).
  - `self_relation` : source égale cible ; relation rejetée.
  - `duplicate_relation` : même triplet `source`, `relation`, `target` qu'une relation
    précédente ; la première est gardée, la suivante rejetée, l'anomalie porte sa ligne.
  - `unknown_status` : statut hors `theorique`, `reconnue`, `demontree` ; relation rejetée.
  - `prerequisite_cycle` : une anomalie par ensemble d'au moins deux notions qui se
    précèdent en cercle par des relations `prerequis` (auto-relations exclues) ; relations
    gardées ; ligne = la plus petite ligne des relations du cycle ; le détail nomme toutes
    les notions du cycle. Seul le type `prerequis` forme un cycle.
- `fragile_prerequisites(relations, notions, cards, rules) -> tuple[Anomaly]` : une anomalie
  `fragile_prerequisite` par relation `prerequis` dont la source est sous « comprise » et la
  cible au moins « comprise » (ordre `states.order`). Une source « déclarée » (état non
  prouvé) est sous « comprise » : fragile ; une cible « déclarée » n'est jamais fragile.
  Une notion connue mais non suivie vaut « non rencontrée ». Une relation à extrémité
  inconnue n'est jamais fragile. Fichier `relations.csv`, ligne de la relation, détail qui
  nomme les deux identifiants et leurs deux états.
- `network_anomalies(relations, notions, cards, rules) -> tuple[Anomaly]` : les anomalies de
  `control_relations`, puis celles de `fragile_prerequisites`.
Aucun code à ajouter à `model.REASON_CODES` (ces fonctions ne produisent aucune valeur
statuée).
"""

import copy
import json
import re
import time
import unittest
from collections import Counter
from pathlib import Path

from system_sync import config, model

try:
    from system_sync.rules import network
except ImportError:
    network = None  # chaque test échoue séparément tant que le module manque

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "tests" / "fixtures" / "network"
RULES = ROOT / "tests" / "fixtures" / "ranks" / "rules_demo.toml"
RULES_DIR = ROOT / "source" / "system_sync" / "rules"
KINDS = {
    "unknown_endpoint",
    "self_relation",
    "duplicate_relation",
    "unknown_status",
    "prerequisite_cycle",
    "fragile_prerequisite",
}
STATES = (
    "non rencontrée",
    "découverte",
    "en cours",
    "comprise",
    "appliquée",
    "retenue",
    "transférée",
    "transcendée",
)


def load_json(name):
    """Lit une fixture JSON de `tests/fixtures/network/`."""
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def relation(source, target, line, kind="prerequis", status="theorique"):
    """Construit une relation au format de `read_relations(...).records`."""
    return {
        "date": "2026-10-15",
        "source": source,
        "relation": kind,
        "target": target,
        "status": status,
        "limit": "",
        "proof": "",
        "line": line,
    }


def notion(note_id, state, line=10):
    """Construit une notion au format de `read_notions(...).records`."""
    return {
        "id": note_id,
        "title": f"Notion fictive {note_id}",
        "section": "Domaine fictif",
        "objective": "objectif fictif",
        "state": state,
        "last_practice": "2026-10-15",
        "interval": "7",
        "next_review": None,
        "last_m1": "",
        "relapses": "0",
        "line": line,
    }


def kinds(anomalies):
    """Compte les anomalies par nature."""
    return Counter(item.kind for item in anomalies)


class NetworkTestCase(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(network, "module system_sync.rules.network absent")
        self.rules = config.load_rules(RULES)
        self.relations = load_json("relations_demo.json")
        self.notions = load_json("notions_demo.json")
        self.cards = load_json("cards_demo.json")

    def control(self, relations, notions=(), cards=()):
        """Appelle `control_relations` avec les mots-clés."""
        return network.control_relations(
            relations=list(relations),
            notions=list(notions),
            cards=list(cards),
        )

    def fragile(self, relations, notions, cards=()):
        """Appelle `fragile_prerequisites` avec les mots-clés."""
        return network.fragile_prerequisites(
            relations=list(relations),
            notions=list(notions),
            cards=list(cards),
            rules=self.rules,
        )

    def pair(self, source_state, target_state, kind="prerequis"):
        """Anomalies fragiles d'une relation unique entre deux notions d'états donnés."""
        return self.fragile(
            [relation("p-src", "p-dst", 2, kind)],
            [notion("p-src", source_state, 10), notion("p-dst", target_state, 11)],
        )


class ControlTest(NetworkTestCase):
    def test_no_relation_gives_nothing(self):
        for empty in ([], None):
            with self.subTest(empty=empty):
                self.assertEqual(
                    network.control_relations(empty, self.notions, self.cards),
                    ((), ()),
                )
                self.assertEqual(
                    network.fragile_prerequisites(empty, self.notions, self.cards, self.rules),
                    (),
                )

    def test_relations_keep_type_status_and_order(self):
        kept, _ = self.control(self.relations, self.notions, self.cards)
        by_line = {item["line"]: item for item in kept}
        self.assertEqual(by_line[5]["relation"], "complementaire")
        self.assertEqual(by_line[3]["status"], "reconnue")
        self.assertEqual(by_line[4]["status"], "demontree")
        self.assertEqual([item["line"] for item in kept], sorted(by_line))
        self.assertTrue(all(item in self.relations for item in kept))

    def test_unknown_endpoint_is_kept_with_an_anomaly(self):
        kept, found = self.control(self.relations, self.notions, self.cards)
        flagged = [item for item in found if item.kind == "unknown_endpoint"]
        self.assertEqual(len(flagged), 1)
        self.assertEqual((flagged[0].file, flagged[0].line), ("relations.csv", 7))
        self.assertIn("net-gone", flagged[0].detail)
        self.assertIn(7, [item["line"] for item in kept])

    def test_card_id_without_follow_up_is_known(self):
        kept, found = self.control(
            [relation("net-a", "net-u", 2)],
            [notion("net-a", "comprise")],
            self.cards,
        )
        self.assertEqual((len(kept), found), (1, ()))

    def test_both_endpoints_unknown_give_two_anomalies(self):
        kept, found = self.control([relation("ghost-1", "ghost-2", 4)])
        self.assertEqual(len(kept), 1)
        self.assertEqual(kinds(found), {"unknown_endpoint": 2})
        details = " ".join(item.detail for item in found)
        self.assertIn("ghost-1", details)
        self.assertIn("ghost-2", details)

    def test_self_relation_is_rejected_with_its_id(self):
        kept, found = self.control(self.relations, self.notions, self.cards)
        flagged = [item for item in found if item.kind == "self_relation"]
        self.assertEqual([(item.file, item.line) for item in flagged], [("relations.csv", 8)])
        self.assertIn("net-a", flagged[0].detail)
        self.assertNotIn(8, [item["line"] for item in kept])

    def test_duplicate_keeps_the_first_relation_only(self):
        kept, found = self.control(self.relations, self.notions, self.cards)
        flagged = [item for item in found if item.kind == "duplicate_relation"]
        self.assertEqual([item.line for item in flagged], [9])
        self.assertIn("net-a", flagged[0].detail)
        self.assertIn("net-c", flagged[0].detail)
        lines = [item["line"] for item in kept]
        self.assertIn(2, lines)
        self.assertNotIn(9, lines)

    def test_same_ends_with_another_type_is_not_a_duplicate(self):
        _, found = self.control(
            [relation("net-a", "net-c", 2), relation("net-a", "net-c", 3, "analogue")],
            self.notions,
            self.cards,
        )
        self.assertEqual(found, ())

    def test_unknown_status_is_rejected_with_an_anomaly(self):
        kept, found = self.control(self.relations, self.notions, self.cards)
        flagged = [item for item in found if item.kind == "unknown_status"]
        self.assertEqual([item.line for item in flagged], [13])
        self.assertIn("presque", flagged[0].detail)
        self.assertNotIn(13, [item["line"] for item in kept])

    def test_prerequisite_cycle_is_flagged_once_and_kept(self):
        kept, found = self.control(self.relations, self.notions, self.cards)
        flagged = [item for item in found if item.kind == "prerequisite_cycle"]
        self.assertEqual([(item.file, item.line) for item in flagged], [("relations.csv", 10)])
        for note_id in ("net-x", "net-y", "net-z"):
            self.assertIn(note_id, flagged[0].detail)
        self.assertTrue({10, 11, 12} <= {item["line"] for item in kept})

    def test_cycle_needs_prerequisite_relations_only(self):
        _, found = self.control(
            [
                relation("net-a", "net-b", 2, "complementaire"),
                relation("net-b", "net-a", 3, "complementaire"),
                relation("net-c", "net-d", 4, "prerequis"),
                relation("net-d", "net-c", 5, "analogue"),
            ],
            self.notions,
            self.cards,
        )
        self.assertEqual(found, ())

    def test_two_separate_cycles_give_two_anomalies(self):
        rows = [
            relation("c-1", "c-2", 2),
            relation("c-2", "c-1", 3),
            relation("c-3", "c-4", 4),
            relation("c-4", "c-5", 5),
            relation("c-5", "c-3", 6),
            relation("c-1", "c-3", 7),
        ]
        _, found = self.control(rows)
        self.assertEqual([item.line for item in found if item.kind == "prerequisite_cycle"],
                         [2, 4])

    def test_long_chain_neither_recurses_nor_cycles(self):
        size = 1000
        rows = [relation(f"chain-{i}", f"chain-{i + 1}", i + 2) for i in range(size)]
        notions = [notion(f"chain-{i}", "comprise", i + 2) for i in range(size + 1)]
        kept, found = self.control(rows, notions)
        self.assertEqual((len(kept), found), (size, ()))
        self.assertEqual(self.fragile(rows, notions), ())

    def test_long_cycle_is_flagged_without_recursion(self):
        size = 1000
        rows = [relation(f"loop-{i}", f"loop-{(i + 1) % size}", i + 2) for i in range(size)]
        notions = [notion(f"loop-{i}", "comprise", i + 2) for i in range(size)]
        kept, found = self.control(rows, notions)
        self.assertEqual((len(kept), kinds(found)), (size, {"prerequisite_cycle": 1}))

    def test_time_does_not_grow_faster_than_linear_with_the_chain(self):
        def best_time(size):
            rows = [relation(f"t-{i}", f"t-{i + 1}", i + 2) for i in range(size)]
            notions = [notion(f"t-{i}", "découverte", i + 2) for i in range(size + 1)]
            times = []
            for _ in range(3):
                start = time.perf_counter()
                network.network_anomalies(rows, notions, [], self.rules)
                times.append(time.perf_counter() - start)
            return min(times)

        small, large = best_time(20000), best_time(40000)
        self.assertLess(large, max(small, 0.01) * 3.5)

    def test_anomalies_are_model_anomalies_sorted_by_line(self):
        _, found = self.control(self.relations, self.notions, self.cards)
        self.assertTrue(all(isinstance(item, model.Anomaly) for item in found))
        self.assertEqual([item.line for item in found], sorted(item.line for item in found))
        self.assertEqual(
            kinds(found),
            {
                "unknown_endpoint": 1,
                "self_relation": 1,
                "duplicate_relation": 1,
                "unknown_status": 1,
                "prerequisite_cycle": 1,
            },
        )
        self.assertEqual({item.file for item in found}, {"relations.csv"})


class FragileTest(NetworkTestCase):
    def test_fragile_prerequisite_names_both_notions_and_states(self):
        found = self.fragile(self.relations, self.notions, self.cards)
        self.assertEqual([item.line for item in found], [3, 4, 15])
        by_line = {item.line: item for item in found}
        self.assertEqual({item.kind for item in found}, {"fragile_prerequisite"})
        self.assertEqual({item.file for item in found}, {"relations.csv"})
        for line, words in {
            3: ("net-b", "net-c", "découverte", "appliquée"),
            4: ("net-d", "net-e", "en cours", "transférée"),
            15: ("net-u", "net-a", "non rencontrée", "comprise"),
        }.items():
            for word in words:
                with self.subTest(line=line, word=word):
                    self.assertIn(word, by_line[line].detail)

    def test_fragile_rule_over_every_pair_of_states(self):
        threshold = STATES.index("comprise")
        for source in STATES:
            for target in STATES:
                with self.subTest(source=source, target=target):
                    expected = STATES.index(source) < threshold <= STATES.index(target)
                    self.assertEqual(len(self.pair(source, target)), int(expected))

    def test_boundary_is_comprise_on_both_sides(self):
        self.assertEqual(len(self.pair("en cours", "comprise")), 1)
        self.assertEqual(self.pair("comprise", "comprise"), ())
        self.assertEqual(self.pair("en cours", "en cours"), ())

    def test_other_relation_types_are_never_fragile(self):
        for kind in ("complementaire", "analogue", "instance_de", "transfert"):
            with self.subTest(kind=kind):
                self.assertEqual(self.pair("découverte", "transférée", kind), ())

    def test_declared_state_is_excluded_from_at_least(self):
        self.assertEqual(self.pair("découverte", "déclarée"), ())

    def test_N5_declared_source_is_fragile(self):
        found = self.pair("déclarée", "appliquée")
        self.assertEqual([item.kind for item in found], ["fragile_prerequisite"])
        self.assertIn("déclarée", found[0].detail)
        self.assertIn("appliquée", found[0].detail)
        self.assertEqual(self.pair("déclarée", "en cours"), ())

    def test_followed_notion_never_met_counts_as_not_met(self):
        self.assertEqual(len(self.pair("non rencontrée", "appliquée")), 1)

    def test_untracked_target_is_not_fragile(self):
        found = self.fragile(
            [relation("net-b", "net-u", 2)],
            [notion("net-b", "découverte")],
            self.cards,
        )
        self.assertEqual(found, ())

    def test_unknown_endpoint_is_never_fragile(self):
        found = self.fragile(
            [relation("net-gone", "net-a", 2), relation("net-b", "net-gone", 3)],
            self.notions,
            self.cards,
        )
        self.assertEqual(found, ())

    def test_fragile_count_on_the_demo_fixture(self):
        found = network.network_anomalies(
            self.relations,
            self.notions,
            self.cards,
            self.rules,
        )
        self.assertEqual(
            kinds(found),
            {
                "unknown_endpoint": 1,
                "self_relation": 1,
                "duplicate_relation": 1,
                "unknown_status": 1,
                "prerequisite_cycle": 1,
                "fragile_prerequisite": 3,
            },
        )
        self.assertTrue({item.kind for item in found} <= KINDS)

    def test_network_anomalies_are_control_then_fragile(self):
        _, control = self.control(self.relations, self.notions, self.cards)
        fragile = self.fragile(self.relations, self.notions, self.cards)
        found = network.network_anomalies(
            relations=self.relations,
            notions=self.notions,
            cards=self.cards,
            rules=self.rules,
        )
        self.assertEqual(found, tuple(control) + tuple(fragile))

    def test_anomaly_serializes_to_four_fields(self):
        found = self.fragile(self.relations, self.notions, self.cards)
        self.assertEqual(set(found[0].to_dict()), {"file", "line", "kind", "detail"})


class RobustnessTest(NetworkTestCase):
    def test_functions_never_raise_on_bad_inputs(self):
        junk = [None, "texte", 7, [None, 3, "x", {}, {"source": "a"}], {"source": "a"}]
        for bad in junk:
            with self.subTest(bad=bad):
                network.control_relations(bad, bad, bad)
                network.fragile_prerequisites(bad, bad, bad, bad)
                network.network_anomalies(bad, bad, bad, bad)
                network.fragile_prerequisites(bad, self.notions, self.cards, self.rules)
                network.network_anomalies(self.relations, bad, bad, self.rules)

    def test_incomplete_records_are_ignored(self):
        rows = [{"source": "net-a"}, relation("net-a", "net-c", 2), None]
        kept, found = self.control(rows, self.notions, self.cards)
        self.assertEqual(([item["line"] for item in kept], found), ([2], ()))

    def test_inputs_are_not_modified(self):
        before = copy.deepcopy((self.relations, self.notions, self.cards))
        network.network_anomalies(self.relations, self.notions, self.cards, self.rules)
        self.assertEqual((self.relations, self.notions, self.cards), before)

    def test_result_is_the_same_on_a_second_call(self):
        args = (self.relations, self.notions, self.cards, self.rules)
        self.assertEqual(network.network_anomalies(*args), network.network_anomalies(*args))


class ArchitectureTest(unittest.TestCase):
    def test_module_exists_and_reads_no_source(self):
        path = RULES_DIR / "network.py"
        self.assertTrue(path.is_file(), "source/system_sync/rules/network.py absent")
        text = path.read_text(encoding="utf-8")
        pattern = re.compile(r"^(from|import) .*sources", re.MULTILINE)
        self.assertIsNone(pattern.search(text))


if __name__ == "__main__":
    unittest.main()
