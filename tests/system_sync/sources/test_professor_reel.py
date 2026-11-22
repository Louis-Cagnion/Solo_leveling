"""Comptes réels des lecteurs de `/professor` (T3, critère 2, comptes remesurés le 22/11/2026).

Le test s'ignore sans `PROFESSOR_SUIVI_DIR` et `IA_HISTORY_CSV`, et quand une source a une
empreinte différente de celle épinglée ci-dessous. Aucun contenu réel n'est copié ni cité :
seuls des comptes et des empreintes figurent ici. Interface : voir `test_professor`.
"""

import hashlib
import os
import unittest
from collections import Counter
from pathlib import Path

try:
    from system_sync.sources import professor
except ImportError:
    professor = None  # chaque test échoue séparément tant que le module manque

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
CARD_NOTIONS = 822
CARDS_WITH_CERTIFICATIONS = 7
CARDS_WITH_CERTIFICATION_COLUMN = 7
CARDS_WITHOUT_CERTIFICATION_COLUMN = 12
CERTIFICATION_CELLS = 192
SHORT_CARD_ROWS = ("cartes/linux-systeme.md", range(82, 92))
FOLLOWED = 179
FOLLOWED_ON_CARD = 124
FOLLOWED_OFF_CARD = 55
STATES = {
    "en cours": 77,
    "découverte": 51,
    "comprise": 21,
    "appliquée": 18,
    "transférée": 11,
    "déclarée": 1,
}
RELATIONS = 95
RELATION_STATUSES = {"theorique": 68, "demontree": 16, "reconnue": 11}
RELATION_TYPES = {
    "prerequis": 51,
    "complementaire": 24,
    "instance_de": 13,
    "analogue": 4,
    "transfert": 3,
}
EVENTS = 1214
PASS_LEVELS_EVENTS = 24
HISTORY = 279
HISTORY_SUSPECT_LINES = [45]
AUTHORS = {"ia": 148, "lecture": 68, "louis": 47, "mixte": 16}
PROJECTS = 31
ANOMALIES = [
    *[("cartes/linux-systeme.md", line, "field_count") for line in SHORT_CARD_ROWS[1]],
    ("historique-ia.csv", 45, "suspect_date"),
]


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


class RealCountsTest(unittest.TestCase):
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
        self.assertIsNotNone(professor, "module system_sync.sources.professor absent")
        self.results = professor.read_professor(self.suivi, self.history)

    def test_real_cards_and_card_notions(self):
        cards = self.results["cards"]
        self.assertEqual(cards.status, "ok")
        self.assertEqual((cards.read, cards.rejected, len(cards.records)), (CARDS, 0, CARDS))
        self.assertEqual(sum(len(card["ids"]) for card in cards.records), CARD_NOTIONS)
        self.assertEqual(sum(card["declared"] for card in cards.records), CARD_NOTIONS)
        found = [(a.file, a.line, a.kind) for a in cards.anomalies]
        self.assertEqual(found, ANOMALIES[:-1])

    def test_real_card_certification_cells(self):
        certifications = [card["certifications"] for card in self.results["cards"].records]
        filled = [found for found in certifications if found]
        self.assertEqual(len(filled), CARDS_WITH_CERTIFICATIONS)
        self.assertEqual(sum(len(found) for found in certifications), CERTIFICATION_CELLS)
        texts = [text for found in filled for text in found.values()]
        self.assertEqual([text for text in texts if not text or text != text.strip()], [])
        self.assertNotIn("\u2014", texts)

    def test_real_card_certification_column_flag(self):
        flags = [card["has_certifications"] for card in self.results["cards"].records]
        self.assertEqual(flags.count(True), CARDS_WITH_CERTIFICATION_COLUMN)
        self.assertEqual(flags.count(False), CARDS_WITHOUT_CERTIFICATION_COLUMN)

    def test_real_followed_notions_on_and_off_card(self):
        notions = self.results["notions"]
        counts = (notions.read, notions.rejected, len(notions.records))
        self.assertEqual(counts, (FOLLOWED, 0, FOLLOWED))
        on_card = {note for card in self.results["cards"].records for note in card["ids"]}
        found = [record["id"] in on_card for record in notions.records]
        split = (found.count(True), found.count(False))
        self.assertEqual(split, (FOLLOWED_ON_CARD, FOLLOWED_OFF_CARD))
        self.assertEqual(len(notions.anomalies), 0)

    def test_real_followed_notion_states(self):
        states = Counter(record["state"] for record in self.results["notions"].records)
        self.assertEqual(states, Counter(STATES))

    def test_real_relations_read_kept_rejected_statuses_and_types(self):
        relations = self.results["relations"]
        counts = (relations.read, relations.rejected, len(relations.records))
        self.assertEqual(counts, (RELATIONS, 0, RELATIONS))
        statuses = Counter(record["status"] for record in relations.records)
        types = Counter(record["relation"] for record in relations.records)
        self.assertEqual(statuses, Counter(RELATION_STATUSES))
        self.assertEqual(types, Counter(RELATION_TYPES))
        self.assertEqual(len(relations.anomalies), 0)

    def test_real_events_and_facts(self):
        events = self.results["events"]
        counts = (events.read, events.rejected, len(events.records))
        self.assertEqual(counts, (EVENTS, 0, EVENTS))
        self.assertEqual(len(events.facts), 0)
        sessions = Counter(record["session"] for record in events.records)
        self.assertEqual(sessions["passe-niveaux"], PASS_LEVELS_EVENTS)
        self.assertEqual(len(events.anomalies), 0)

    def test_real_history_read_kept_rejected_suspect(self):
        history = self.results["history"]
        counts = (history.read, history.rejected, len(history.records))
        self.assertEqual(counts, (HISTORY, 0, HISTORY))
        suspect = [record["line"] for record in history.records if record["suspect"]]
        self.assertEqual(suspect, HISTORY_SUSPECT_LINES)

    def test_real_history_authors_and_projects(self):
        records = self.results["history"].records
        self.assertEqual(Counter(record["author"] for record in records), Counter(AUTHORS))
        self.assertEqual(len({record["project"] for record in records}), PROJECTS)

    def test_real_anomalies_total(self):
        found = [
            (anomaly.file, anomaly.line, anomaly.kind)
            for result in self.results.values()
            for anomaly in result.anomalies
        ]
        self.assertEqual(found, ANOMALIES)

    def test_real_projects_file_is_absent(self):
        projects = self.results["projects"]
        self.assertEqual(projects.status, "absent")
        counts = (projects.read, projects.rejected, list(projects.records))
        self.assertEqual(counts, (0, 0, []))

    def test_real_sources_are_unchanged_after_reading(self):
        before = full_digests(self.suivi, self.history)
        professor.read_professor(self.suivi, self.history)
        self.assertEqual(full_digests(self.suivi, self.history), before)
        self.assertGreater(len(before), 5)


if __name__ == "__main__":
    unittest.main()
