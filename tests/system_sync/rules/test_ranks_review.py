"""Tests de la revue de T6.d : défauts I2 et I4 de `system_sync.rules.ranks`.

Contrat imposé au builder (les fixtures et helpers sont ceux de `test_ranks`) :
- I2 : une cellule de certifications au texte non vide, ni tiret cadratin ni « aucune »
  (casse ignorée), sans code extrait par `CODE_PATTERN`, rend la liste illisible. Le rang
  reste `S` ; `next_rank` vers Nation porte `progress` `unmeasurable` (raison
  `certification_list_unreadable`) ; `card_certifications` ne rend aucune certification
  accessible ; `rank_anomalies` rend une anomalie `unreadable_certification` pour la
  carte, dont le détail nomme la carte et le texte de la cellule.
- I4 : `rank_card`, `next_rank`, `card_certifications` et `rank_anomalies` acceptent les
  mots-clés `card`, `cards`, `notions`, `facts`, `rules` et rendent le même résultat qu'en
  appel positionnel ; un mot-clé inconnu ne lève pas (`unmeasurable`, `None`, `()`).
"""

import copy
import unittest

from system_sync.rules import ranks
from tests.system_sync.rules.test_ranks import RankCase, fact, level

UNREADABLE_TEXT = "Docker Certified Associate"
EM_DASH = chr(0x2014)


class UnreadableCellTest(RankCase):
    def with_cell(self, text):
        """Copie d'Alpha dont l'unique cellule de certifications vaut `text`."""
        card = copy.deepcopy(self.cards["Alpha"])
        card["certifications"] = {"alpha-d1": text}
        return card

    def test_I2_cell_without_code_keeps_rank_s(self):
        card = self.with_cell(UNREADABLE_TEXT)
        found = self.rank("Alpha", facts=[level("transcendée")], card=card)
        self.assertEqual((found.value, found.status), ("S", "observed"))

    def test_I2_cell_without_code_makes_next_rank_unmeasurable(self):
        card = self.with_cell(UNREADABLE_TEXT)
        found = ranks.next_rank(card, self.notions, [level("transcendée")], self.rules)
        self.assertEqual(found["rank"], "Nation")
        self.assertEqual(found["progress"].status, "unmeasurable")
        self.assertEqual(found["progress"].reason_code, "certification_list_unreadable")

    def test_I2_cell_without_code_gives_no_accessible_certification(self):
        card = self.with_cell(UNREADABLE_TEXT)
        found = ranks.card_certifications(
            card,
            [card],
            self.notions,
            [level("transcendée")],
            self.rules,
        )
        for entry in found:
            with self.subTest(code=entry["code"]):
                self.assertEqual(entry["accessible"].status, "unmeasurable")
                self.assertEqual(
                    entry["accessible"].reason_code,
                    "certification_list_unreadable",
                )

    def test_I2_cell_without_code_is_reported_once(self):
        card = self.with_cell(UNREADABLE_TEXT)
        found = ranks.rank_anomalies(
            [card],
            self.notions,
            [level("transcendée")],
            self.rules,
        )
        found = [a for a in found if a.kind == "unreadable_certification"]
        self.assertEqual(len(found), 1)
        self.assertIn("Alpha", found[0].detail)
        self.assertIn(UNREADABLE_TEXT, found[0].detail)

    def test_I2_guard_empty_cells_keep_nation_reachable(self):
        for text in ("aucune", "Aucune", EM_DASH):
            with self.subTest(text=text):
                card = self.with_cell(text)
                found = self.rank("Alpha", facts=[level("transcendée")], card=card)
                self.assertEqual((found.value, found.status), ("Nation", "observed"))
                anomalies = ranks.rank_anomalies([card], self.notions, [], self.rules)
                self.assertEqual(
                    [a for a in anomalies if a.kind == "unreadable_certification"],
                    [],
                )

    def test_I2_guard_valid_code_cell_is_unchanged(self):
        card = self.with_cell("ALPHA-1")
        facts = [level("transcendée")]
        found = self.rank("Alpha", facts=facts, card=card)
        self.assertEqual((found.value, found.status), ("S", "observed"))
        following = ranks.next_rank(card, self.notions, facts, self.rules)
        self.assertEqual(following["progress"].status, "observed")
        self.assertEqual(following["total"], 1)
        anomalies = ranks.rank_anomalies([card], self.notions, facts, self.rules)
        self.assertEqual(
            [a for a in anomalies if a.kind == "unreadable_certification"],
            [],
        )


class KeywordCallTest(RankCase):
    def setUp(self):
        super().setUp()
        self.card = self.cards["Alpha"]
        self.all_cards = list(self.cards.values())
        self.some_facts = [level("avancé"), fact("Alpha", "certification", "ALPHA-1")]

    def test_I4_rank_card_by_keyword_equals_positional(self):
        by_keyword = ranks.rank_card(
            card=self.card,
            notions=self.notions,
            facts=self.some_facts,
            rules=self.rules,
        )
        positional = ranks.rank_card(self.card, self.notions, self.some_facts, self.rules)
        self.assertEqual(by_keyword, positional)
        self.assertNotEqual(by_keyword.status, "unmeasurable")

    def test_I4_next_rank_by_keyword_equals_positional(self):
        by_keyword = ranks.next_rank(
            card=self.card,
            notions=self.notions,
            facts=self.some_facts,
            rules=self.rules,
        )
        positional = ranks.next_rank(self.card, self.notions, self.some_facts, self.rules)
        self.assertIsNotNone(by_keyword)
        self.assertEqual(by_keyword, positional)

    def test_I4_card_certifications_by_keyword_equals_positional(self):
        by_keyword = ranks.card_certifications(
            card=self.card,
            cards=self.all_cards,
            notions=self.notions,
            facts=self.some_facts,
            rules=self.rules,
        )
        positional = ranks.card_certifications(
            self.card,
            self.all_cards,
            self.notions,
            self.some_facts,
            self.rules,
        )
        self.assertTrue(by_keyword)
        self.assertEqual(by_keyword, positional)

    def test_I4_rank_anomalies_by_keyword_equals_positional(self):
        facts = [*self.some_facts, fact("Alpha", "niveau", "expert", line=8)]
        by_keyword = ranks.rank_anomalies(
            cards=self.all_cards,
            notions=self.notions,
            facts=facts,
            rules=self.rules,
        )
        positional = ranks.rank_anomalies(self.all_cards, self.notions, facts, self.rules)
        self.assertTrue(by_keyword)
        self.assertEqual(by_keyword, positional)

    def test_I4_unknown_keyword_never_raises(self):
        found = ranks.rank_card(
            card=self.card,
            notions=self.notions,
            facts=[],
            rules=self.rules,
            unknown=1,
        )
        self.assertEqual(found.status, "unmeasurable")
        self.assertIsNone(found.value)
        self.assertIsNone(
            ranks.next_rank(
                card=self.card,
                notions=self.notions,
                facts=[],
                rules=self.rules,
                unknown=1,
            )
        )
        self.assertEqual(
            ranks.card_certifications(
                card=self.card,
                cards=self.all_cards,
                notions=self.notions,
                facts=[],
                rules=self.rules,
                unknown=1,
            ),
            (),
        )
        self.assertEqual(
            ranks.rank_anomalies(
                cards=self.all_cards,
                notions=self.notions,
                facts=[],
                rules=self.rules,
                unknown=1,
            ),
            (),
        )


if __name__ == "__main__":
    unittest.main()
