"""Relations réelles des règles de T9 (comptes remesurés le 22/11/2026, A30).

Le test s'ignore sans `PROFESSOR_SUIVI_DIR` et `IA_HISTORY_CSV`, et quand une source a une
empreinte différente de celle épinglée ci-dessous. Aucun contenu réel n'est copié : seuls
des comptes, des numéros de ligne et des empreintes figurent ici. Interface de
`system_sync.rules.network` : voir `test_network`.

Écarts avec la fiche de T9 (comptes du 11/11/2026) : 95 relations lues, comme annoncé ; une
seule extrémité inconnue (`relations.csv:32`, cible), comme annoncé ; aucune auto-relation,
aucun doublon, aucun cycle ni statut inconnu ; 10 prérequis fragiles au lieu de 8, tous à
source suivie sous « comprise » (8 « en cours » et 2 « découverte »), la règle d'A25 étant
appliquée à la lettre. Les comptes de
nœuds et d'arêtes d'appartenance de la fiche tombent avec l'entité `network` (A25).
"""

import hashlib
import os
import unittest
from collections import Counter
from pathlib import Path

from system_sync import config

try:
    from system_sync.rules import network
    from system_sync.sources import professor
except ImportError:
    network = professor = None  # chaque test échoue séparément tant que les modules manquent

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
RELATIONS = 95
UNKNOWN_ENDPOINT_LINES = [32]
FRAGILE_LINES = [6, 7, 26, 29, 35, 36, 39, 40, 51, 74]
FRAGILE_STATE_PAIRS = {
    ("en cours", "appliquée"): 3,
    ("en cours", "comprise"): 2,
    ("en cours", "transférée"): 3,
    ("découverte", "comprise"): 1,
    ("découverte", "transférée"): 1,
}


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


class RealNetworkTest(unittest.TestCase):
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
        self.assertIsNotNone(network, "module system_sync.rules.network absent")
        self.assertIsNotNone(professor, "module system_sync.sources.professor absent")
        self.rules = config.load_rules(ROOT / "config" / "rules.toml")
        results = professor.read_professor(self.suivi, self.history)
        self.relations = list(results["relations"].records)
        self.notions = list(results["notions"].records)
        self.cards = list(results["cards"].records)

    def control(self):
        """Contrôle des relations réelles."""
        return network.control_relations(self.relations, self.notions, self.cards)

    def test_real_relations_are_read_and_all_kept(self):
        self.assertEqual(len(self.relations), RELATIONS)
        kept, _ = self.control()
        self.assertEqual(len(kept), RELATIONS)

    def test_real_unknown_endpoint_is_kept_and_flagged(self):
        kept, found = self.control()
        flagged = [item for item in found if item.kind == "unknown_endpoint"]
        self.assertEqual([item.line for item in flagged], UNKNOWN_ENDPOINT_LINES)
        self.assertIn("minishell-environnement", flagged[0].detail)
        self.assertEqual({item.file for item in flagged}, {"relations.csv"})
        self.assertIn(UNKNOWN_ENDPOINT_LINES[0], [item["line"] for item in kept])

    def test_real_data_has_no_other_control_anomaly(self):
        _, found = self.control()
        self.assertEqual(Counter(item.kind for item in found), {"unknown_endpoint": 1})

    def test_real_fragile_prerequisites_are_ten(self):
        found = network.fragile_prerequisites(
            self.relations,
            self.notions,
            self.cards,
            self.rules,
        )
        self.assertEqual([item.line for item in found], FRAGILE_LINES)
        self.assertEqual({item.kind for item in found}, {"fragile_prerequisite"})
        by_line = {item["line"]: item for item in self.relations}
        states = {item["id"]: item["state"] for item in self.notions}
        pairs = Counter(
            (states[by_line[item.line]["source"]], states[by_line[item.line]["target"]])
            for item in found
        )
        self.assertEqual(pairs, Counter(FRAGILE_STATE_PAIRS))

    def test_real_network_anomalies_total_eleven(self):
        found = network.network_anomalies(
            self.relations,
            self.notions,
            self.cards,
            self.rules,
        )
        self.assertEqual(len(found), 1 + len(FRAGILE_LINES))

    def test_real_sources_are_unchanged_after_control(self):
        before = full_digests(self.suivi, self.history)
        network.network_anomalies(self.relations, self.notions, self.cards, self.rules)
        self.assertEqual(full_digests(self.suivi, self.history), before)
        self.assertGreater(len(before), 5)


if __name__ == "__main__":
    unittest.main()
