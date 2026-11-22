"""Tests de la revue de T3.b (T3.d) : cinq défauts importants de `professor.py`.

Contrat tranché par le moniteur (interface imposée au builder) :
- I1 : une cellule « Certifications » égale à un tiret cadratin est ignorée ; une
  ligne de carte qui a moins de cellules que l'en-tête garde son id et donne une anomalie
  `field_count` (fichier `cartes/<fichier>`, ligne physique) ; chaque carte gagne
  `has_certifications`.
- I2 : une carte dont un tableau de palier n'a pas de colonne « Id » est rejetée avec
  `missing_header` ; dans `notions.md`, un tableau sans « Id » donne `missing_header` (ligne
  de son en-tête) et un fichier non vide sans enregistrement est `unavailable` ; un compte
  « Notions : N » différent du nombre d'ids lus donne `declared_mismatch` (carte gardée).
- I3 : une date de `notions.md` faite de chiffres et de séparateurs, mais pas jj/mm/aaaa
  valide, vaut `None` avec `invalid_date` ; valide mais hors de 2020-01-01 à aujourd'hui,
  elle reste ISO avec `suspect_date` ; un texte libre reste `None` sans anomalie.
- I4 : `projets.csv` se lit par nom de colonne (`id,cadre,statut,date,equivalent_42,
  justification`, ordre libre) ; clés `id`, `frame`, `status`, `date`, `equivalent_42`,
  `justification`, `line` ; `cadre` hors `perso`, `pro` : `unknown_frame` ; `statut` hors
  `en cours`, `livré`, `abandonné` : `unknown_status`.
- I5 : la première ligne de `relations.csv`, `evenements.csv`, `historique-ia.csv` et
  `projets.csv` est lue comme en-tête ; sans en-tête, permutée ou renommée, la source est
  `unavailable` et le message nomme la ligne 1, la colonne attendue et la valeur reçue.
"""

import tomllib
import unittest

from tests.system_sync.sources.test_professor import (
    ROOT,
    SOURCES,
    SUIVI,
    ProfessorCase,
    card_text,
    dated_row,
    four_tiers,
    kinds,
    lines_of,
    notion_row,
    notions_text,
    professor,
    put,
)

DASH = "\u2014"
PROJECT_HEAD = "id,cadre,statut,date,equivalent_42,justification"
PROJECT_ROWS = [
    "demo-sort,perso,livré,15/10/2026,300,Projet fictif",
    "demo-parser,pro,en cours,01/11/2026,120,Autre projet fictif",
]
PROJECT_KEYS = {"id", "frame", "status", "date", "equivalent_42", "justification", "line"}


def block(tier, header, rows):
    """Palier de carte : titre, tableau d'en-tête `header` et lignes `rows` (textes)."""
    lines = [f"## {tier}", "", "| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    return lines + rows + [""]


def build_card(title, blocks, declared):
    """Carte de titre `title` qui déclare `declared` notions, de paliers `blocks`."""
    head = [f"# Carte : {title}", "", f"- **Notions** : {declared}, aucune déjà suivie.", ""]
    return "\n".join(head + [line for part in blocks for line in part])


def certification_card(first_rows, declared=4):
    """Carte à quatre paliers de colonnes Id, Notion, Certifications ; `first_rows` va au
    premier palier, les trois autres ont chacun une ligne sans certification."""
    header = ["Id", "Notion", "Certifications"]
    tiers = ["Débutant", "Intermédiaire", "Avancé", "Transcendée"]
    blocks = [block(tiers[0], header, first_rows)]
    for number, tier in enumerate(tiers[1:], 1):
        blocks.append(block(tier, header, [f"| c-fill{number} | Remplissage | |"]))
    return build_card("Cert", blocks, declared)


def dated_notion(last, following):
    """Ligne de `notions.md` (10 cellules) de dernière pratique et prochain rappel donnés."""
    cells = ["alpha-loop", "Boucle", "socle", "en cours", last, "21", following, "2", "0", "x"]
    return "| " + " | ".join(cells) + " |"


def read_notions_dates(case, last, following):
    """Écrit un `notions.md` d'une ligne datée (ligne 7) et le lit."""
    text = notions_text(dated_notion(last, following))
    return professor.read_notions(put(case.tmp / "notions.md", text))


class CertificationTest(ProfessorCase):
    def test_I1_dash_certification_cell_is_not_a_certification(self):
        rows = ["| c-a | A | CERT-1 |", f"| c-b | B | {DASH} |", "| c-c | C |  |"]
        text = certification_card(rows, declared=6)
        card = professor.read_cards(self.cards_dir(cert=text)).records[0]
        self.assertEqual(dict(card["certifications"]), {"c-a": "CERT-1"})
        expected = ["c-a", "c-b", "c-c", "c-fill1", "c-fill2", "c-fill3"]
        self.assertEqual(list(card["ids"]), expected)

    def test_I1_card_with_only_dash_cells_has_the_column_and_no_certification(self):
        text = certification_card([f"| c-a | A | {DASH} |"])
        card = professor.read_cards(self.cards_dir(cert=text)).records[0]
        self.assertEqual(dict(card["certifications"]), {})
        self.assertIs(card["has_certifications"], True)

    def test_I1_short_card_row_keeps_its_id_and_reports_field_count(self):
        rows = ["| c-a | A | CERT-1 |", "| c-b | B |"]
        text = certification_card(rows, declared=5)
        result = professor.read_cards(self.cards_dir(cert=text))
        self.assertEqual((result.read, result.rejected), (1, 0))
        card = result.records[0]
        self.assertIn("c-b", card["ids"])
        self.assertEqual(dict(card["certifications"]), {"c-a": "CERT-1"})
        (anomaly,) = result.anomalies
        self.assertEqual((anomaly.kind, anomaly.file), ("field_count", "cartes/cert.md"))
        self.assertEqual(anomaly.line, lines_of(text, "| c-b | B |")[0])
        self.assertRegex(anomaly.detail, r"\b2\b")
        self.assertRegex(anomaly.detail, r"\b3\b")

    def test_I1_has_certifications_is_a_boolean_on_every_card(self):
        records = professor.read_cards(SUIVI / "cartes").records
        flags = {card["name"]: card["has_certifications"] for card in records}
        self.assertEqual(flags, {"Alpha": True, "Beta": False})


class HeaderDriftTest(ProfessorCase):
    def test_I2_card_tier_table_without_id_column_rejects_the_card(self):
        alpha = (SUIVI / "cartes" / "alpha.md").read_text(encoding="utf-8")
        for name in ("ID", "Identifiant"):
            with self.subTest(column=name):
                tiers = ["Débutant", "Intermédiaire", "Avancé", "Transcendée"]
                blocks = [
                    block(tier, ["Id", "Notion"], [f"| t{n} | T |"])
                    for n, tier in enumerate(tiers)
                ]
                blocks[1] = block(tiers[1], [name, "Notion"], ["| t9 | T |"])
                bad = build_card("Bad", blocks, 4)
                cards = self.cards_dir(alpha=alpha, bad=bad)
                result = professor.read_cards(cards)
                self.assertEqual((result.read, result.rejected), (2, 1))
                self.assertEqual([card["name"] for card in result.records], ["Alpha"])
                (anomaly,) = result.anomalies
                found = (anomaly.kind, anomaly.file)
                self.assertEqual(found, ("missing_header", "cartes/bad.md"))

    def test_I2_notions_table_without_id_column_is_reported_on_its_header_line(self):
        extra = "\n## Beta\n\n| ID | Notion |\n|---|---|\n| b-1 | Un |\n"
        text = notions_text(notion_row("alpha-loop")) + extra
        result = professor.read_notions(put(self.tmp / "notions.md", text))
        self.assertEqual(result.status, "ok")
        self.assertEqual([record["id"] for record in result.records], ["alpha-loop"])
        (anomaly,) = result.anomalies
        self.assertEqual((anomaly.kind, anomaly.file), ("missing_header", "notions.md"))
        self.assertEqual(anomaly.line, lines_of(text, "| ID |")[0])

    def test_I2_non_empty_notions_file_without_any_record_is_unavailable(self):
        bad_table = "## Beta\n\n| ID | Notion |\n|---|---|\n| b-1 | Un |\n"
        for label, text in (("table sans Id", bad_table), ("prose", "# Notions\n\nrien\n")):
            with self.subTest(content=label):
                path = put(self.tmp / label / "notions.md", text)
                result = professor.read_notions(path)
                self.assertEqual(result.status, "unavailable")
                self.assertIn(str(path), result.error)
                self.assertNotIn("vide", result.error)
                self.assertNotIn("absent", result.error)
                self.assertEqual((result.read, result.rejected), (0, 0))

    def test_I2_declared_count_different_from_the_ids_read_is_reported(self):
        ids = ["g-a", "g-b", "g-c", "g-d"]
        text = card_text("Gamma", four_tiers(ids), declared=7)
        result = professor.read_cards(self.cards_dir(gamma=text))
        self.assertEqual((result.read, result.rejected), (1, 0))
        self.assertEqual(list(result.records[0]["ids"]), ids)
        (anomaly,) = result.anomalies
        found = (anomaly.kind, anomaly.file)
        self.assertEqual(found, ("declared_mismatch", "cartes/gamma.md"))
        self.assertRegex(anomaly.detail, r"\b7\b")
        self.assertRegex(anomaly.detail, r"\b4\b")

    def test_I2_card_with_id_header_and_the_right_count_has_no_anomaly(self):
        result = professor.read_cards(SUIVI / "cartes")
        self.assertEqual(result.status, "ok")
        self.assertEqual(list(result.anomalies), [])
        text = card_text("Gamma", four_tiers(["g-a", "g-b", "g-c", "g-d"]))
        self.assertEqual(list(professor.read_cards(self.cards_dir(g=text)).anomalies), [])


class NotionDatesTest(ProfessorCase):
    def test_I3_date_shaped_but_invalid_cell_is_none_with_invalid_date(self):
        for value in ("31/02/2026", "9/11/2026", "2026-11-30", "10/2026"):
            for key in ("last_practice", "next_review"):
                with self.subTest(value=value, column=key):
                    pair = {"last_practice": "09/11/2026", "next_review": "10/11/2026"}
                    pair[key] = value
                    result = read_notions_dates(
                        self,
                        pair["last_practice"],
                        pair["next_review"],
                    )
                    (record,) = result.records
                    self.assertIsNone(record[key])
                    (anomaly,) = result.anomalies
                    found = (anomaly.kind, anomaly.file)
                    self.assertEqual(found, ("invalid_date", "notions.md"))
                    self.assertEqual(anomaly.line, 7)
                    self.assertIn(value, anomaly.detail)

    def test_I3_valid_date_out_of_range_is_kept_in_iso_with_suspect_date(self):
        cases = (
            ("01/01/1999", "last_practice", "1999-01-01"),
            ("01/01/1999", "next_review", "1999-01-01"),
            ("01/01/2999", "last_practice", "2999-01-01"),
        )
        for value, key, iso in cases:
            with self.subTest(value=value, column=key):
                pair = {"last_practice": "09/11/2026", "next_review": "10/11/2026"}
                pair[key] = value
                result = read_notions_dates(self, pair["last_practice"], pair["next_review"])
                (record,) = result.records
                self.assertEqual(record[key], iso)
                (anomaly,) = result.anomalies
                self.assertEqual((anomaly.kind, anomaly.file), ("suspect_date", "notions.md"))
                self.assertEqual(anomaly.line, 7)
                self.assertIn(value, anomaly.detail)

    def test_I3_free_text_stays_none_without_anomaly(self):
        for value in ("à fixer", "sortie", "à la reprise du projet"):
            with self.subTest(value=value):
                result = read_notions_dates(self, value, value)
                (record,) = result.records
                self.assertIsNone(record["last_practice"])
                self.assertIsNone(record["next_review"])
                self.assertEqual(list(result.anomalies), [])

    def test_I3_valid_past_date_stays_iso_without_anomaly(self):
        result = read_notions_dates(self, "09/11/2026", "10/11/2026")
        (record,) = result.records
        found = (record["last_practice"], record["next_review"])
        self.assertEqual(found, ("2026-11-09", "2026-11-10"))
        self.assertEqual(list(result.anomalies), [])


class ProjectsTest(ProfessorCase):
    def read_projects(self, head, rows, name="projets.csv"):
        """Écrit un `projets.csv` (en-tête `head`, lignes `rows`) et le lit."""
        path = put(self.tmp / name, "\n".join([head, *rows]) + "\n")
        return professor.read_projects(path)

    def test_I4_conforming_projects_file_is_read_by_column_name(self):
        result = self.read_projects(PROJECT_HEAD, PROJECT_ROWS)
        self.assertEqual((result.status, result.read, result.rejected), ("ok", 2, 0))
        first, second = result.records
        self.assertEqual(set(first), PROJECT_KEYS)
        found = (first["id"], first["frame"], first["status"])
        self.assertEqual(found, ("demo-sort", "perso", "livré"))
        self.assertEqual((first["date"], first["line"]), ("2026-10-15", 2))
        self.assertEqual(str(first["equivalent_42"]), "300")
        self.assertEqual(first["justification"], "Projet fictif")
        found = (second["id"], second["frame"], second["status"])
        self.assertEqual(found, ("demo-parser", "pro", "en cours"))
        self.assertEqual((second["date"], second["line"]), ("2026-11-01", 3))
        self.assertEqual(list(result.anomalies), [])

    def test_I4_column_order_is_free(self):
        head = "date,id,statut,cadre,justification,equivalent_42"
        rows = ["15/10/2026,demo-sort,livré,perso,Projet fictif,300"]
        result = self.read_projects(head, rows)
        self.assertEqual((result.status, result.read, result.rejected), ("ok", 1, 0))
        (record,) = result.records
        found = (record["id"], record["frame"], record["status"])
        self.assertEqual(found, ("demo-sort", "perso", "livré"))
        self.assertEqual(record["date"], "2026-10-15")
        self.assertEqual(record["justification"], "Projet fictif")
        self.assertEqual(str(record["equivalent_42"]), "300")

    def test_I4_unknown_frame_rejects_the_row(self):
        bad = "demo-x,mixte,livré,15/10/2026,10,Hors liste"
        result = self.read_projects(PROJECT_HEAD, [bad, PROJECT_ROWS[0]])
        self.assertEqual((result.read, result.rejected), (2, 1))
        self.assertEqual([record["id"] for record in result.records], ["demo-sort"])
        (anomaly,) = result.anomalies
        self.assertEqual((anomaly.kind, anomaly.line), ("unknown_frame", 2))
        self.assertIn("mixte", anomaly.detail)

    def test_I4_unknown_status_rejects_the_row_and_abandoned_is_accepted(self):
        bad = "demo-x,perso,terminé,15/10/2026,10,Hors liste"
        good = "demo-y,pro,abandonné,16/10/2026,0,Laissé"
        result = self.read_projects(PROJECT_HEAD, [bad, good])
        self.assertEqual((result.read, result.rejected), (2, 1))
        self.assertEqual([record["status"] for record in result.records], ["abandonné"])
        (anomaly,) = result.anomalies
        self.assertEqual((anomaly.kind, anomaly.line), ("unknown_status", 2))
        self.assertIn("terminé", anomaly.detail)


class CsvHeaderTest(ProfessorCase):
    def check_unavailable(self, reader, path, expected, received):
        """Vérifie une source indisponible dont le message nomme ligne 1, attendu, reçu."""
        result = getattr(professor, reader)(path)
        self.assertEqual(result.status, "unavailable")
        self.assertEqual((result.read, result.rejected, list(result.records)), (0, 0, []))
        message = result.error.replace(str(path), "")
        self.assertRegex(message, r"\b1\b")
        self.assertIn(expected, message)
        if received:
            self.assertIn(received, message)

    def test_I5_file_without_header_is_unavailable(self):
        for kind, (reader, name, header, _, _) in SOURCES.items():
            with self.subTest(source=kind):
                row = dated_row(kind, "15/10/2026")
                path = put(self.tmp / kind / name, row + "\n" + row + "\n")
                self.check_unavailable(reader, path, header.split(",")[0], "15/10/2026")

    def test_I5_permuted_columns_are_unavailable(self):
        for kind, (reader, name, header, _, _) in SOURCES.items():
            with self.subTest(source=kind):
                names = header.split(",")
                names[0], names[1] = names[1], names[0]
                text = ",".join(names) + "\n" + dated_row(kind, "15/10/2026") + "\n"
                path = put(self.tmp / kind / name, text)
                self.check_unavailable(reader, path, header.split(",")[0], names[0])

    def test_I5_renamed_column_is_unavailable(self):
        for kind, (reader, name, header, _, _) in SOURCES.items():
            with self.subTest(source=kind):
                names = header.split(",")
                expected = names[3]
                names[3] = "zzz"
                text = ",".join(names) + "\n" + dated_row(kind, "15/10/2026") + "\n"
                path = put(self.tmp / kind / name, text)
                self.check_unavailable(reader, path, expected, "zzz")

    def test_I5_projects_without_header_or_with_a_renamed_column_are_unavailable(self):
        no_header = put(self.tmp / "a" / "projets.csv", "\n".join(PROJECT_ROWS) + "\n")
        self.check_unavailable("read_projects", no_header, "id", "demo-sort")
        renamed = PROJECT_HEAD.replace("cadre", "frame")
        text = "\n".join([renamed, *PROJECT_ROWS]) + "\n"
        path = put(self.tmp / "b" / "projets.csv", text)
        self.check_unavailable("read_projects", path, "cadre", "frame")


class StatesTest(unittest.TestCase):
    def test_I6_notion_states_equal_the_rules_states_order(self):
        self.assertIsNotNone(professor, "module system_sync.sources.professor absent")
        with (ROOT / "config" / "rules.toml").open("rb") as handle:
            order = tomllib.load(handle)["states"]["order"]
        self.assertEqual(len(order), len(set(order)))
        self.assertEqual(set(order), set(professor.NOTION_STATES))


if __name__ == "__main__":
    unittest.main()
