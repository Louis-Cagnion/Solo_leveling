"""Titres réels des règles de T8 (critère 3, comptes remesurés le 22/11/2026, A30).

Le test s'ignore sans `PROFESSOR_SUIVI_DIR` et `IA_HISTORY_CSV`, et quand une source a une
empreinte différente de celle épinglée ci-dessous. Aucun contenu réel n'est copié : seuls
des comptes, des empreintes et le niveau de 12,44 (donné en paramètre : le niveau réel vient
de l'API 42, que le test n'appelle pas) figurent ici. Interface de `system_sync.rules.titles` :
voir `test_titles`.

Écarts avec la fiche de T8 (comptes du 11/11/2026, 16 cartes) : 19 cartes au lieu de 16,
toujours 0 carte au rang S, aucune carte au rang insuffisant ; le titre 42 vaut toujours
12,44 sur 25, soit 49,76 %, non obtenu, observé (niveau passé par le test).
"""

import hashlib
import os
import unittest
from pathlib import Path

from system_sync import config, model

try:
    from system_sync.rules import ranks, titles
    from system_sync.sources import professor
except ImportError:
    ranks = titles = professor = None  # chaque test échoue tant que les modules manquent

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
CARDS_AT_S = 0
LEVEL = 12.44
TARGET_LEVEL = 25
LEVEL_PERCENT = 49.76


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


class RealTitlesTest(unittest.TestCase):
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
        self.assertIsNotNone(titles, "module system_sync.rules.titles absent")
        self.assertIsNotNone(ranks, "module system_sync.rules.ranks absent")
        self.assertIsNotNone(professor, "module system_sync.sources.professor absent")
        self.rules = config.load_rules(ROOT / "config" / "rules.toml")
        results = professor.read_professor(self.suivi, self.history)
        self.cards = list(results["cards"].records)
        notions = list(results["notions"].records)
        self.facts = list(results["events"].facts)
        facts = self.facts
        self.card_ranks = {
            card["name"]: ranks.rank_card(card, notions, facts, self.rules)
            for card in self.cards
        }

    def real_titles(self):
        """Titres réels indexés par `id`, le niveau étant donné en paramètre."""
        found = titles.school_titles(
            level=model.observed(LEVEL, ("api42",)),
            card_ranks=self.card_ranks,
            facts=self.facts,
            rules=self.rules,
        )
        return {entry["id"]: entry for entry in found}

    def test_real_system_title_is_not_obtained_with_no_card_at_s(self):
        self.assertEqual(len(self.card_ranks), CARDS)
        entry = self.real_titles()["answer_system"]
        obtained = entry["obtained"]
        self.assertEqual((obtained.value, obtained.status), (False, "observed"))
        self.assertTrue(entry["obtained"].sources)
        self.assertEqual(entry["progress"]["current"], CARDS_AT_S)
        self.assertEqual(entry["progress"]["target"], CARDS)

    def test_real_no_card_has_an_unusable_rank(self):
        statuses = {state.status for state in self.card_ranks.values()}
        self.assertEqual(statuses, {"observed"})
        entry = self.real_titles()["answer_system"]
        self.assertNotEqual(entry["obtained"].status, "insufficient")

    def test_real_42_title_is_at_49_76_percent_not_obtained_and_observed(self):
        entry = self.real_titles()["answer_42"]
        obtained = entry["obtained"]
        self.assertEqual((obtained.value, obtained.status), (False, "observed"))
        self.assertEqual(entry["progress"]["current"], LEVEL)
        self.assertEqual(entry["progress"]["target"], TARGET_LEVEL)
        self.assertAlmostEqual(entry["progress"]["percent"], LEVEL_PERCENT, places=2)

    def test_real_only_the_two_answer_titles_are_listed(self):
        self.assertEqual(list(self.real_titles()), ["answer_42", "answer_system"])
        found = titles.title_anomalies(facts=self.facts, rules=self.rules)
        self.assertEqual((found, len(self.facts)), ((), 0))

    def test_real_sources_are_unchanged_after_the_titles(self):
        before = full_digests(self.suivi, self.history)
        self.real_titles()
        self.assertEqual(full_digests(self.suivi, self.history), before)
        self.assertGreater(len(before), 5)


if __name__ == "__main__":
    unittest.main()
