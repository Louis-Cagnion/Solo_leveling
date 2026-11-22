"""Rangs réels des règles de T6 (critère 2, comptes remesurés le 22/11/2026, A30).

Le test s'ignore sans `PROFESSOR_SUIVI_DIR` et `IA_HISTORY_CSV`, et quand une source a une
empreinte différente de celle épinglée ci-dessous. Aucun contenu réel n'est copié : seuls
des comptes, des noms de cartes (déjà publics dans `docs/` et `public/`) et des empreintes
figurent ici. Interface de `system_sync.rules.ranks` : voir `test_ranks`.

Écarts avec la fiche de T6 (comptes du 11/11/2026, 16 cartes) : 19 cartes au lieu de 16,
11 cartes au rang E au lieu de 10 (Python s'ajoute), 8 sans rang au lieu de 6 (les cartes
Développement web, JavaScript et Mathématiques pour l'IA s'ajoutent, Python part), toujours
aucune carte D, SQL à 5 notions débutantes sur 8 et Docker à 4 sur 8 comme annoncé.
"""

import hashlib
import os
import unittest
from collections import Counter
from pathlib import Path

from system_sync import config

try:
    from system_sync.rules import ranks
    from system_sync.sources import professor
except ImportError:
    ranks = professor = None  # chaque test échoue séparément tant que les modules manquent

ROOT = Path(__file__).resolve().parents[3]
PIN_DATE = "22/11/2026"
# Seize premiers caractères du sha256 de chaque source (`cartes` : `cat cartes/*.md`).
FINGERPRINTS = {
    "notions.md": "ab75f23e1984c6b6",
    "relations.csv": "3008d013b365b0b1",
    "evenements.csv": "4db54cc48bb53098",
    "historique-ia.csv": "efa24512fe5569ee",
    "cartes": "a62f62746ba6d141",
}
CARDS = 19
RANK_COUNTS = {"E": 11, "none": 8}
RANK_E_CARDS = {
    "Algorithmique",
    "C",
    "C++",
    "Docker",
    "Infographie 3D",
    "Linux (système)",
    "Noyau et assembleur",
    "Python",
    "Réseau",
    "Shell",
    "SQL",
}
NO_RANK_CARDS = {
    "Apprentissage automatique",
    "Développement web (serveur)",
    "JavaScript et TypeScript",
    "LLM",
    "Mathématiques pour l'IA",
    "PHP",
    "Programmation fonctionnelle",
    "Sécurité binaire",
}
# Carte : (notions débutantes au moins « comprises », notions débutantes, manques pour D).
BEGINNER_PROGRESS = {"SQL": (5, 8, 3), "Docker": (4, 8, 4)}
CERTIFICATIONS_PER_CARD = {
    "C": 3,
    "C++": 2,
    "Développement web (serveur)": 2,
    "JavaScript et TypeScript": 2,
    "Linux (système)": 3,
    "Python": 4,
}
CERTIFICATION_ENTRIES = 16
CERTIFICATION_CODES = 15
CARDS_WITHOUT_CERTIFICATION_COLUMN = 12


def short_digest(data):
    """Seize premiers caractères du sha256 de `data`."""
    return hashlib.sha256(data).hexdigest()[:16]


def fingerprints(suivi, history):
    """Empreintes courtes des cinq sources, sous les clés de `FINGERPRINTS`."""
    cards = b"".join(path.read_bytes() for path in sorted((suivi / "cartes").glob("*.md")))
    return {
        "notions.md": short_digest((suivi / "notions.md").read_bytes()),
        "relations.csv": short_digest((suivi / "relations.csv").read_bytes()),
        "evenements.csv": short_digest((suivi / "evenements.csv").read_bytes()),
        "historique-ia.csv": short_digest(history.read_bytes()),
        "cartes": short_digest(cards),
    }


def full_digests(suivi, history):
    """sha256 complet de chaque fichier du suivi et de l'historique."""
    paths = [path for path in sorted(suivi.rglob("*")) if path.is_file()]
    return {
        str(path): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in [*paths, history]
    }


class RealRanksTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        suivi = os.environ.get("PROFESSOR_SUIVI_DIR")
        history = os.environ.get("IA_HISTORY_CSV")
        if not suivi or not history:
            raise unittest.SkipTest("PROFESSOR_SUIVI_DIR et IA_HISTORY_CSV non définies")
        cls.suivi, cls.history = Path(suivi), Path(history)
        try:
            found = fingerprints(cls.suivi, cls.history)
        except OSError as error:
            raise unittest.SkipTest(f"sources illisibles : {error}") from error
        changed = sorted(name for name, value in found.items() if value != FINGERPRINTS[name])
        if changed:
            raise unittest.SkipTest(f"sources modifiées depuis le {PIN_DATE} : {changed}")

    def setUp(self):
        self.assertIsNotNone(ranks, "module system_sync.rules.ranks absent")
        self.assertIsNotNone(professor, "module system_sync.sources.professor absent")
        self.rules = config.load_rules(ROOT / "config" / "rules.toml")
        results = professor.read_professor(self.suivi, self.history)
        self.cards = list(results["cards"].records)
        self.notions = list(results["notions"].records)
        self.facts = list(results["events"].facts)
        self.by_name = {card["name"]: card for card in self.cards}

    def rank_of(self, card):
        """Rang d'une carte réelle."""
        return ranks.rank_card(card, self.notions, self.facts, self.rules)

    def test_real_rank_counts_without_any_fact(self):
        self.assertEqual((len(self.cards), len(self.facts)), (CARDS, 0))
        found = [self.rank_of(card) for card in self.cards]
        self.assertEqual(Counter(rank.value for rank in found), Counter(RANK_COUNTS))
        self.assertEqual({rank.status for rank in found}, {"observed"})
        self.assertTrue(all(rank.sources for rank in found))

    def test_real_rank_e_and_no_rank_cards_are_the_expected_ones(self):
        by_rank = {}
        for card in self.cards:
            by_rank.setdefault(self.rank_of(card).value, set()).add(card["name"])
        self.assertEqual(by_rank["E"], RANK_E_CARDS)
        self.assertEqual(by_rank["none"], NO_RANK_CARDS)
        self.assertNotIn("D", by_rank)

    def test_real_sql_and_docker_miss_beginner_notions_for_d(self):
        for name, (done, total, missing) in BEGINNER_PROGRESS.items():
            with self.subTest(card=name):
                found = ranks.next_rank(
                    self.by_name[name],
                    self.notions,
                    self.facts,
                    self.rules,
                )
                self.assertEqual(found["rank"], "D")
                self.assertEqual((found["progress"].value, found["total"]), (done, total))
                self.assertEqual(len(found["missing"]), missing)
                self.assertEqual(done + missing, total)

    def test_real_certification_entries_none_accessible_none_obtained(self):
        everything = list(self.cards)
        entries = {
            card["name"]: ranks.card_certifications(
                card,
                everything,
                self.notions,
                self.facts,
                self.rules,
            )
            for card in self.cards
        }
        counts = {name: len(found) for name, found in entries.items() if found}
        self.assertEqual(counts, CERTIFICATIONS_PER_CARD)
        flat = [entry for found in entries.values() for entry in found]
        self.assertEqual(len(flat), CERTIFICATION_ENTRIES)
        self.assertEqual(len({entry["code"] for entry in flat}), CERTIFICATION_CODES)
        self.assertEqual({entry["accessible"].status for entry in flat}, {"estimated"})
        self.assertEqual([e["accessible"].value for e in flat if e["accessible"].value], [])
        self.assertEqual([e for e in flat if e["obtained"].value], [])
        self.assertTrue(all(entry["notions"] for entry in flat))

    def test_real_cards_without_certification_column_are_twelve(self):
        without = [card for card in self.cards if not card["has_certifications"]]
        self.assertEqual(len(without), CARDS_WITHOUT_CERTIFICATION_COLUMN)

    def test_real_data_gives_no_rank_anomaly(self):
        found = ranks.rank_anomalies(self.cards, self.notions, self.facts, self.rules)
        self.assertEqual(tuple(found), ())

    def test_real_sources_are_unchanged_after_ranking(self):
        before = full_digests(self.suivi, self.history)
        for card in self.cards:
            self.rank_of(card)
            ranks.next_rank(card, self.notions, self.facts, self.rules)
        self.assertEqual(full_digests(self.suivi, self.history), before)
        self.assertGreater(len(before), 5)


if __name__ == "__main__":
    unittest.main()
