"""Tests de `system_sync.sources.professor` (T3, cas N1 à N16 et L1 à L17).

Contrat de T3.b (`from system_sync.sources import professor`, aucune fonction ne lève) :
- `read_cards(dir)`, `read_notions`, `read_relations`, `read_events`, `read_history` et
  `read_projects` (`path`) : un `SourceResult` chacune.
- `read_professor(suivi_dir, history_csv) -> dict` : les six résultats, clés `cards`,
  `notions`, `relations`, `events`, `history`, `projects` (fichiers sous `suivi_dir`).
- `SourceResult` (dataclass figée) : `name`, `path`, `status` (`ok`, `unavailable`, ou
  `absent` pour `projets.csv` seul), `error` (`None` si `ok`, sinon le chemin et un mot
  `absent`, `vide`, `dossier` ou `aucune carte`, ou l'offset d'un octet non UTF-8),
  `records` (dicts de `RECORD_KEYS`, `line` physique), `facts` (événements `niveau`,
  `certification`, `titre`), `anomalies` (`model.Anomaly`, `kind` de `ANOMALY_KINDS`),
  `read` (lignes de données ou cartes), `rejected` (hors dates suspectes) ; 0 et 0 si
  indisponible. Dates en AAAA-MM-JJ, `None` si texte libre ; en-tête seul : `ok`, vide.
- `cards[].certifications` (A21) : id vers texte brut, espaces retirés, de la cellule
  « Certifications » ; cellules vides ou « tiret cadratin » ignorées, `{}` sans colonne ou
  sans cellule remplie. `cards[].has_certifications` (booléen) : vrai si la carte a une colonne
  « Certifications », même sans cellule remplie.
"""

import hashlib
import shutil
import tempfile
import unittest
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

from system_sync import model

try:
    from system_sync.sources import professor
except ImportError:
    professor = None  # chaque test échoue séparément tant que le module manque

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "tests" / "fixtures" / "professor"
SUIVI = FIXTURES / "suivi"
HISTORY = FIXTURES / "historique-ia.csv"
BAD = FIXTURES / "mal_forme"

# Clés de chaque enregistrement ; `section` est le titre `##` de `notions.md`.
RECORD_KEYS = {
    "cards": {
        "name",
        "tiers",
        "ids",
        "declared",
        "declared_followed",
        "certifications",
        "has_certifications",
    },
    "notions": {
        "id",
        "title",
        "section",
        "objective",
        "state",
        "last_practice",
        "interval",
        "next_review",
        "last_m1",
        "relapses",
        "line",
    },
    "relations": {"date", "source", "relation", "target", "status", "limit", "proof", "line"},
    "events": {
        "date",
        "session",
        "domain",
        "notion",
        "metric",
        "value",
        "context",
        "visual_form",
        "proof",
        "line",
    },
    "history": {
        "date",
        "suspect",
        "project",
        "mode",
        "domain",
        "notions",
        "author",
        "proof",
        "line",
    },
}
# Natures d'anomalie : rejet de ligne ou de carte, sauf `suspect_date` (ligne gardée).
ANOMALY_KINDS = {
    "field_count",
    "invalid_date",
    "suspect_date",
    "unknown_author",
    "unknown_status",
    "unknown_state",
    "unknown_level",
    "duplicate_id",
    "missing_title",
    "unknown_tier",
    "missing_tier",
    "bad_encoding",
}
TIERS = ("Débutant", "Intermédiaire", "Avancé", "Transcendée")
ALPHA_IDS = [
    "alpha-loop",
    "alpha-array",
    "alpha-tree",
    "alpha-graph",
    "alpha-heap",
    "alpha-sort",
    "alpha-proof",
    "alpha-bound",
]
REL_HEAD = "date,source,relation,cible,statut,limite,preuve"
EVT_HEAD = "date,session,domaine,notion,metrique,valeur,contexte,forme_visuelle,preuve"
HIS_HEAD = "date,projet,mode,domaine,notions,auteur,preuve"
NOTION_HEAD = (
    "| Id | Notion | Objectif | État | Dernière pratique | Intervalle | Prochain rappel"
    " | Dernier M1 | Rechutes | Solidité |"
)
NOTION_SEP = "|" + "---|" * 10
# Lecteur, fichier, en-tête, modèle de ligne valide (`{}` = date) et nombre de champs.
SOURCES = {
    "relations": (
        "read_relations",
        "relations.csv",
        REL_HEAD,
        "{},alpha-loop,prerequis,alpha-array,theorique,,",
        7,
    ),
    "events": (
        "read_events",
        "evenements.csv",
        EVT_HEAD,
        "{},1,Alpha,alpha-loop,etat,découverte,,,",
        9,
    ),
    "history": (
        "read_history",
        "historique-ia.csv",
        HIS_HEAD,
        "{},demo-sort,professor,Alpha,,ia,",
        7,
    ),
}
COUNTS = {
    "cards": (2, 0),
    "notions": (6, 0),
    "relations": (5, 1),
    "events": (8, 0),
    "history": (8, 1),
}
PARTS = {
    "cards": Path("suivi") / "cartes",
    "notions": Path("suivi") / "notions.md",
    "relations": Path("suivi") / "relations.csv",
    "events": Path("suivi") / "evenements.csv",
    "history": Path("historique-ia.csv"),
}


def put(path, text):
    """Écrit `text` en UTF-8 dans `path` (dossiers créés) et renvoie `path`."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def lines_of(text, needle):
    """Numéros (à partir de 1) des lignes de `text` qui contiennent `needle`."""
    return [n for n, line in enumerate(text.splitlines(), 1) if needle in line]


def card_text(title, tiers, declared=None):
    """Fabrique une carte : `tiers` est une liste de couples (palier, identifiants).

    `declared` est le compte « Notions : N » ; par défaut, le nombre d'identifiants distincts.
    """
    if declared is None:
        declared = len({note_id for _, ids in tiers for note_id in ids})
    lines = [f"# Carte : {title}", "", f"- **Notions** : {declared}, aucune déjà suivie.", ""]
    for tier, ids in tiers:
        lines += [f"## {tier}", "", "| Id | Notion |", "|---|---|"]
        lines += [f"| {note_id} | Notion {note_id} |" for note_id in ids]
        lines.append("")
    return "\n".join(lines)


def four_tiers(ids):
    """Quatre paliers de `TIERS` portant chacun l'identifiant de même rang dans `ids`."""
    return [(tier, [note_id]) for tier, note_id in zip(TIERS, ids)]


def notion_row(note_id, state="en cours", title="Titre"):
    """Ligne de `notions.md` à 10 cellules."""
    cells = [note_id, title, "socle", state, "09/11/2026", "21", "30/11/2026", "2", "0", "x"]
    return "| " + " | ".join(cells) + " |"


def notions_text(*rows):
    """Fabrique un `notions.md` d'une section `Alpha` ; les lignes sont à partir de la 7e."""
    head = ["# État des notions", "", "## Alpha", "", NOTION_HEAD, NOTION_SEP]
    return "\n".join(head + list(rows)) + "\n"


def read_source(tmp, kind, rows):
    """Écrit une source CSV sous `tmp` (en-tête puis `rows`) et la lit."""
    reader, name, header, _, _ = SOURCES[kind]
    path = put(tmp / name, "\n".join([header, *rows]) + "\n")
    return getattr(professor, reader)(path)


def dated_row(kind, text):
    """Ligne valide de la source `kind` portant la date `text`."""
    return SOURCES[kind][3].format(text)


def kinds(result):
    """Natures des anomalies d'un résultat, dans l'ordre."""
    return [anomaly.kind for anomaly in result.anomalies]


def digest(root):
    """Empreinte sha256 de chaque fichier sous `root` ; les dossiers sont listés."""
    found = {}
    for path in sorted(Path(root).rglob("*")):
        key = str(path.relative_to(root))
        found[key] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "dir"
    return found


class ProfessorCase(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(professor, "module system_sync.sources.professor absent")
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        self.tmp = Path(holder.name)

    def copy_suivi(self, base):
        """Copie les fixtures sous `base` ; renvoie le dossier du suivi et l'historique."""
        shutil.copytree(SUIVI, base / "suivi")
        shutil.copy(HISTORY, base / "historique-ia.csv")
        return base / "suivi", base / "historique-ia.csv"

    def cards_dir(self, **texts):
        """Dossier `cartes/` temporaire : un fichier `<clé>.md` par texte reçu."""
        for name, text in texts.items():
            put(self.tmp / "cartes" / f"{name}.md", text)
        return self.tmp / "cartes"


class NominalTest(ProfessorCase):
    def test_N1_card_name_four_tiers_ordered_ids(self):
        result = professor.read_cards(SUIVI / "cartes")
        self.assertEqual(result.status, "ok")
        self.assertEqual([card["name"] for card in result.records], ["Alpha", "Beta"])
        alpha = result.records[0]
        self.assertEqual(set(alpha), RECORD_KEYS["cards"])
        self.assertEqual(list(alpha["tiers"]), list(TIERS))
        self.assertEqual(list(alpha["tiers"]["Avancé"]), ["alpha-heap", "alpha-sort"])
        self.assertEqual(list(alpha["ids"]), ALPHA_IDS)

    def test_N2_declared_count_is_read(self):
        records = professor.read_cards(SUIVI / "cartes").records
        counts = {c["name"]: (c["declared"], c["declared_followed"]) for c in records}
        self.assertEqual(counts, {"Alpha": (8, 2), "Beta": (4, 0)})

    def test_N16_card_certification_cells_by_notion(self):
        cards = {c["name"]: c for c in professor.read_cards(SUIVI / "cartes").records}
        expected = {"alpha-array": "ALPHA-1", "alpha-heap": "ALPHA-1 et ALPHA-2 (fictives)"}
        self.assertEqual(dict(cards["Alpha"]["certifications"]), expected)
        self.assertIs(cards["Alpha"]["has_certifications"], True)

    def test_N16_card_without_certification_column_gives_an_empty_dict(self):
        cards = {c["name"]: c for c in professor.read_cards(SUIVI / "cartes").records}
        self.assertEqual(dict(cards["Beta"]["certifications"]), {})
        self.assertIs(cards["Beta"]["has_certifications"], False)
        self.assertEqual(len(cards["Beta"]["ids"]), 4)

    def test_N16_card_with_the_column_but_no_filled_cell_gives_an_empty_dict(self):
        text = (SUIVI / "cartes" / "alpha.md").read_text(encoding="utf-8")
        for code in ("ALPHA-1 et ALPHA-2 (fictives)", "ALPHA-1"):
            text = text.replace(f"| {code} |", "| |").replace(f"|  {code}  |", "| |")
        card = professor.read_cards(self.cards_dir(alpha=text)).records[0]
        self.assertEqual(dict(card["certifications"]), {})
        self.assertIs(card["has_certifications"], True)
        self.assertEqual(list(card["ids"]), ALPHA_IDS)

    def test_N3_notions_ten_named_columns(self):
        result = professor.read_notions(SUIVI / "notions.md")
        self.assertEqual(result.status, "ok")
        by_id = {record["id"]: record for record in result.records}
        self.assertEqual(len(by_id), 6)
        loop = by_id["alpha-loop"]
        self.assertEqual(set(loop), RECORD_KEYS["notions"])
        expected = {
            "title": "Boucle",
            "section": "Alpha",
            "objective": "socle",
            "state": "en cours",
            "last_practice": "2026-11-09",
            "interval": "21",
            "next_review": "2026-11-30",
            "last_m1": "2",
            "relapses": "0",
        }
        for key, value in expected.items():
            self.assertEqual(loop[key], value, key)
        self.assertEqual(by_id["principes-revue"]["section"], "Principes")
        self.assertEqual(by_id["alpha-tree"]["state"], "déclarée")
        self.assertIsNone(by_id["alpha-array"]["last_practice"])
        self.assertIsNone(by_id["alpha-array"]["next_review"])

    def test_N4_escaped_bar_stays_in_the_cell(self):
        records = professor.read_notions(SUIVI / "notions.md").records
        array = {record["id"]: record for record in records}["alpha-array"]
        self.assertEqual(array["title"].replace("\\|", "|"), "Tableau (`a | b`, indices)")
        self.assertEqual(array["objective"], "socle")
        self.assertEqual(array["state"], "découverte")
        self.assertEqual(array["relapses"], "0")

    def test_N5_solidity_is_not_in_the_output(self):
        records = professor.read_notions(SUIVI / "notions.md").records
        self.assertEqual(len(records), 6)
        for record in records:
            self.assertNotIn("SOLIDITE", repr(record))
            self.assertFalse(any("solid" in key.lower() for key in record), record)

    def test_N6_relations_seven_fields_read_as_is(self):
        result = professor.read_relations(SUIVI / "relations.csv")
        by_source = {record["source"]: record for record in result.records}
        record = by_source["alpha-array"]
        self.assertEqual(set(record), RECORD_KEYS["relations"])
        self.assertEqual(record["date"], "2026-10-16")
        self.assertEqual(record["relation"], "complementaire")
        self.assertEqual(record["target"], "alpha-tree")
        self.assertEqual(record["status"], "reconnue")
        self.assertEqual((record["limit"], record["proof"]), ("", ""))
        tree = by_source["alpha-tree"]
        self.assertEqual((tree["relation"], tree["status"]), ("instance_de", "demontree"))
        self.assertEqual((tree["limit"], tree["proof"]), ("aucune limite", "S2/alpha-tree/M2"))

    def test_N7_repeated_triplet_last_line_wins(self):
        result = professor.read_relations(SUIVI / "relations.csv")
        triplet = [record for record in result.records if record["source"] == "alpha-loop"]
        self.assertEqual(len(triplet), 1)
        self.assertEqual(len(result.records), 3)
        self.assertEqual(triplet[0]["status"], "demontree")
        self.assertEqual(triplet[0]["date"], "2026-10-20")
        self.assertEqual(triplet[0]["proof"], "S1/alpha-loop/M2")
        self.assertEqual(triplet[0]["line"], 5)

    def test_N8_events_keep_the_quoted_comma(self):
        result = professor.read_events(SUIVI / "evenements.csv")
        self.assertEqual(len(result.records), 8)
        quoted = [record for record in result.records if record["notion"] == "alpha-tree"]
        self.assertEqual(set(quoted[0]), RECORD_KEYS["events"])
        self.assertEqual(quoted[0]["context"], "contexte, avec virgule")
        self.assertEqual(quoted[0]["date"], "2026-10-17")
        self.assertEqual(quoted[0]["line"], 4)

    def test_N9_pass_levels_session_is_accepted(self):
        result = professor.read_events(SUIVI / "evenements.csv")
        sessions = {record["notion"]: record["session"] for record in result.records}
        self.assertEqual(sessions["alpha-array"], "passe-niveaux")
        self.assertEqual(sessions["alpha-tree"], "hors-session")
        self.assertEqual(result.rejected, 0)

    def test_N10_history_authors(self):
        result = professor.read_history(HISTORY)
        self.assertEqual(len(result.records), 7)
        self.assertEqual(set(result.records[0]), RECORD_KEYS["history"])
        authors = Counter(record["author"] for record in result.records)
        self.assertEqual(authors, Counter({"ia": 2, "louis": 3, "mixte": 1, "lecture": 1}))
        projects = {record["project"] for record in result.records}
        self.assertEqual(projects, {"demo-sort", "demo-parser"})
        self.assertEqual(result.records[0]["date"], "2026-10-15")

    def test_N11_counters_per_source(self):
        results = professor.read_professor(SUIVI, HISTORY)
        self.assertEqual(sorted(results), sorted([*COUNTS, "projects"]))
        for name, counts in COUNTS.items():
            with self.subTest(source=name):
                self.assertEqual(results[name].name, name)
                self.assertEqual(results[name].status, "ok")
                self.assertIsNone(results[name].error)
                self.assertEqual((results[name].read, results[name].rejected), counts)

    def test_N12_rejected_line_gives_an_anomaly_and_the_rest_is_read(self):
        result = professor.read_relations(SUIVI / "relations.csv")
        (anomaly,) = result.anomalies
        self.assertIsInstance(anomaly, model.Anomaly)
        self.assertEqual((anomaly.file, anomaly.line), ("relations.csv", 4))
        self.assertEqual(anomaly.kind, "field_count")
        self.assertTrue(str(anomaly).startswith("relations.csv:4 : field_count : "))
        self.assertEqual({record["line"] for record in result.records}, {3, 5, 6})
        history = professor.read_history(HISTORY)
        self.assertLessEqual(set(kinds(history)), ANOMALY_KINDS)
        self.assertEqual({a.line for a in history.anomalies if a.kind == "field_count"}, {7})
        self.assertIn(9, {record["line"] for record in history.records})

    def test_N13_level_and_certification_facts_are_exposed_raw(self):
        result = professor.read_events(SUIVI / "evenements.csv")
        facts = list(result.facts)
        metrics = [fact["metric"] for fact in facts]
        self.assertEqual(metrics, ["niveau", "certification", "titre"])
        level, certification, title = facts
        self.assertEqual(level["domain"], "Alpha")
        self.assertEqual((level["notion"], level["value"]), ("", "intermédiaire"))
        self.assertEqual(level["proof"], "tests/banc-alpha")
        self.assertEqual(certification["domain"], "Alpha")
        self.assertEqual(certification["value"], "ALPHA-1")
        self.assertEqual((title["domain"], title["value"]), ("Système", "titre-demo"))
        self.assertEqual(len(result.records), 8)

    def test_N14_missing_projects_file_is_absent_not_unavailable(self):
        absent = professor.read_projects(self.tmp / "projets.csv")
        self.assertEqual(absent.status, "absent")
        self.assertEqual((absent.read, absent.rejected, list(absent.records)), (0, 0, []))
        (self.tmp / "folder" / "projets.csv").mkdir(parents=True)
        broken = professor.read_projects(self.tmp / "folder" / "projets.csv")
        self.assertEqual(broken.status, "unavailable")
        self.assertEqual(professor.read_professor(SUIVI, HISTORY)["projects"].status, "absent")

    def test_N15_sources_are_unchanged_after_reading(self):
        before = digest(FIXTURES)
        professor.read_professor(SUIVI, HISTORY)
        professor.read_cards(SUIVI / "cartes")
        self.assertEqual(digest(FIXTURES), before)
        self.assertGreater(len(before), 10)


class LimitTest(ProfessorCase):
    def test_L1_each_missing_source_is_unavailable_and_the_others_are_read(self):
        for name, part in PARTS.items():
            with self.subTest(missing=name):
                base = self.tmp / name
                suivi, history = self.copy_suivi(base)
                target = base / part
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
                results = professor.read_professor(suivi, history)
                self.assertEqual(results[name].status, "unavailable")
                self.assertIn(str(target), results[name].error)
                self.assertIn("absent", results[name].error)
                self.assertEqual((results[name].read, results[name].rejected), (0, 0))
                for other in COUNTS:
                    if other != name:
                        self.assertEqual(results[other].status, "ok", other)
                        self.assertEqual(results[other].read, COUNTS[other][0], other)

    def test_L2_directory_in_place_of_a_file(self):
        for kind, (reader, name, _, _, _) in SOURCES.items():
            with self.subTest(source=kind):
                path = self.tmp / kind / name
                path.mkdir(parents=True)
                result = getattr(professor, reader)(path)
                self.assertEqual(result.status, "unavailable")
                self.assertIn(str(path), result.error)
                self.assertIn("dossier", result.error)
        notions = self.tmp / "notions" / "notions.md"
        notions.mkdir(parents=True)
        self.assertIn("dossier", professor.read_notions(notions).error)
        cards = put(self.tmp / "file" / "cartes", "pas un dossier\n")
        self.assertEqual(professor.read_cards(cards).status, "unavailable")
        self.assertIn(str(cards), professor.read_cards(cards).error)

    def test_L3_empty_file_has_its_own_message(self):
        readers = {"notions": ("read_notions", "notions.md")}
        readers.update({kind: (spec[0], spec[1]) for kind, spec in SOURCES.items()})
        for kind, (reader, name) in readers.items():
            with self.subTest(source=kind):
                path = put(self.tmp / kind / name, "")
                result = getattr(professor, reader)(path)
                self.assertEqual(result.status, "unavailable")
                self.assertIn(str(path), result.error)
                self.assertIn("vide", result.error)
                self.assertNotIn("absent", result.error)
        fixture = professor.read_relations(BAD / "relations_vide.csv")
        self.assertEqual(fixture.status, "unavailable")
        self.assertIn("vide", fixture.error)

    def test_L4_header_only_is_ok_and_empty(self):
        results = {
            "events": professor.read_events(BAD / "evenements_entete_seul.csv"),
            "relations": read_source(self.tmp, "relations", []),
            "history": read_source(self.tmp, "history", []),
            "notions": professor.read_notions(put(self.tmp / "n.md", notions_text())),
        }
        for kind, result in results.items():
            with self.subTest(source=kind):
                self.assertEqual(result.status, "ok")
                self.assertIsNone(result.error)
                self.assertEqual(list(result.records), [])
                self.assertEqual(list(result.anomalies), [])
                self.assertEqual((result.read, result.rejected), (0, 0))

    def test_L5_cards_directory_without_markdown_is_unavailable(self):
        put(self.tmp / "cartes" / "notes.txt", "pas une carte\n")
        result = professor.read_cards(self.tmp / "cartes")
        self.assertEqual(result.status, "unavailable")
        self.assertIn(str(self.tmp / "cartes"), result.error)
        self.assertIn("aucune carte", result.error)
        self.assertEqual((result.read, result.rejected), (0, 0))

    def test_L6_wrong_field_count_names_received_and_expected(self):
        for kind, (_, _, _, _, width) in SOURCES.items():
            row = dated_row(kind, "15/10/2026")
            wrong = {width + 1: row + ",extra", width - 1: row.rsplit(",", 1)[0]}
            for received, text in wrong.items():
                with self.subTest(source=kind, received=received):
                    result = read_source(self.tmp, kind, [text, row])
                    self.assertEqual((result.read, result.rejected), (2, 1))
                    (anomaly,) = result.anomalies
                    self.assertEqual((anomaly.kind, anomaly.line), ("field_count", 2))
                    self.assertRegex(anomaly.detail, rf"\b{received}\b")
                    self.assertRegex(anomaly.detail, rf"\b{width}\b")

    def test_L7_month_only_date_is_kept_and_marked_suspect(self):
        result = professor.read_history(HISTORY)
        by_line = {record["line"]: record for record in result.records}
        self.assertIsNone(by_line[8]["date"])
        self.assertIs(by_line[8]["suspect"], True)
        self.assertEqual({line for line, record in by_line.items() if record["suspect"]}, {8})
        (suspect,) = [a for a in result.anomalies if a.kind == "suspect_date"]
        self.assertEqual((suspect.file, suspect.line), ("historique-ia.csv", 8))
        self.assertIn("10/2026", suspect.detail)
        self.assertEqual(result.rejected, 1)

    def test_L8_impossible_date_is_rejected(self):
        for kind in SOURCES:
            with self.subTest(source=kind):
                result = read_source(self.tmp, kind, [dated_row(kind, "31/02/2026")])
                self.assertEqual((result.read, result.rejected), (1, 1))
                self.assertEqual(list(result.records), [])
                (anomaly,) = result.anomalies
                self.assertEqual((anomaly.kind, anomaly.line), ("invalid_date", 2))
                self.assertIn("31/02/2026", anomaly.detail)

    def test_L9_out_of_range_date_is_suspect_and_kept(self):
        today = date.today()
        cases = {
            "31/12/2019": True,
            "01/01/2020": False,
            (today - timedelta(days=1)).strftime("%d/%m/%Y"): False,
            (today + timedelta(days=2)).strftime("%d/%m/%Y"): True,
        }
        for text, suspect in cases.items():
            with self.subTest(date=text):
                result = read_source(self.tmp, "history", [dated_row("history", text)])
                self.assertEqual((result.read, result.rejected), (1, 0))
                self.assertEqual(len(result.records), 1)
                self.assertIs(result.records[0]["suspect"], suspect)
                self.assertEqual(kinds(result), ["suspect_date"] if suspect else [])

    def test_L10_unknown_author_or_relation_status_is_rejected_with_the_value(self):
        author = read_source(
            self.tmp,
            "history",
            [
                "15/10/2026,demo-sort,professor,Alpha,,robot,",
                dated_row("history", "16/10/2026"),
            ],
        )
        self.assertEqual((author.read, author.rejected, len(author.records)), (2, 1, 1))
        self.assertEqual(kinds(author), ["unknown_author"])
        self.assertEqual(author.anomalies[0].line, 2)
        self.assertIn("robot", author.anomalies[0].detail)
        status = read_source(
            self.tmp,
            "relations",
            [
                "15/10/2026,alpha-loop,prerequis,alpha-array,probable,,",
                dated_row("relations", "16/10/2026"),
            ],
        )
        self.assertEqual((status.read, status.rejected, len(status.records)), (2, 1, 1))
        self.assertEqual(kinds(status), ["unknown_status"])
        self.assertEqual(status.anomalies[0].line, 2)
        self.assertIn("probable", status.anomalies[0].detail)

    def test_L11_notions_row_with_9_or_11_columns_is_rejected_never_shifted(self):
        text = (BAD / "notions_9_colonnes.md").read_text(encoding="utf-8")
        eleven = notions_text(
            notion_row("alpha-loop"),
            notion_row("alpha-array", title="a | b"),
            notion_row("alpha-sort", "appliquée"),
        )
        for received, content in ((9, text), (11, eleven)):
            with self.subTest(columns=received):
                result = professor.read_notions(put(self.tmp / f"n{received}.md", content))
                self.assertEqual((result.read, result.rejected), (3, 1))
                (anomaly,) = result.anomalies
                self.assertEqual(anomaly.kind, "field_count")
                self.assertEqual(anomaly.line, lines_of(content, "alpha-array")[0])
                self.assertRegex(anomaly.detail, rf"\b{received}\b")
                self.assertRegex(anomaly.detail, r"\b10\b")
                by_id = {record["id"]: record for record in result.records}
                self.assertEqual(sorted(by_id), ["alpha-loop", "alpha-sort"])
                self.assertEqual(by_id["alpha-sort"]["state"], "appliquée")
                self.assertEqual(by_id["alpha-sort"]["relapses"], "0")

    def test_L12_unknown_notion_state_is_rejected(self):
        text = notions_text(
            notion_row("alpha-loop"),
            notion_row("alpha-array", "expert"),
            notion_row("alpha-sort", "appliquée"),
        )
        result = professor.read_notions(put(self.tmp / "notions.md", text))
        self.assertEqual((result.read, result.rejected), (3, 1))
        (anomaly,) = result.anomalies
        self.assertEqual((anomaly.kind, anomaly.line), ("unknown_state", 8))
        self.assertIn("expert", anomaly.detail)
        ids = [record["id"] for record in result.records]
        self.assertEqual(ids, ["alpha-loop", "alpha-sort"])

    def test_L13_card_without_title_is_rejected(self):
        cards = self.cards_dir(alpha=(SUIVI / "cartes" / "alpha.md").read_text("utf-8"))
        shutil.copy(BAD / "carte_sans_titre.md", cards / "carte_sans_titre.md")
        result = professor.read_cards(cards)
        self.assertEqual((result.read, result.rejected), (2, 1))
        self.assertEqual([card["name"] for card in result.records], ["Alpha"])
        (anomaly,) = result.anomalies
        self.assertEqual(anomaly.kind, "missing_title")
        self.assertEqual((anomaly.file, anomaly.line), ("cartes/carte_sans_titre.md", 1))

    def test_L14_unknown_tier_bonus_and_missing_tier_reject_the_card(self):
        bonus = (BAD / "carte_palier_bonus.md").read_text(encoding="utf-8")
        three = [
            (tier, [f"delta-{n}"])
            for n, tier in enumerate(TIERS)
            if tier != "Avancé"
        ]
        missing = card_text("Delta", three)
        cards = self.cards_dir(alpha=(SUIVI / "cartes" / "alpha.md").read_text("utf-8"))
        put(cards / "carte_palier_bonus.md", bonus)
        put(cards / "delta.md", missing)
        result = professor.read_cards(cards)
        self.assertEqual((result.read, result.rejected), (3, 2))
        self.assertEqual([card["name"] for card in result.records], ["Alpha"])
        by_file = {anomaly.file: anomaly for anomaly in result.anomalies}
        unknown = by_file["cartes/carte_palier_bonus.md"]
        self.assertEqual(unknown.kind, "unknown_tier")
        self.assertEqual(unknown.line, lines_of(bonus, "## Bonus")[0])
        self.assertIn("Bonus", unknown.detail)
        absent = by_file["cartes/delta.md"]
        self.assertEqual((absent.kind, absent.line), ("missing_tier", 1))
        self.assertIn("Avancé", absent.detail)

    def test_L15_duplicate_id_inside_a_card_is_dropped_and_reported(self):
        tiers = [("Débutant", ["dup-a", "dup-b"]), ("Intermédiaire", ["dup-c", "dup-a"])]
        tiers += [("Avancé", ["dup-d"]), ("Transcendée", ["dup-e"])]
        text = card_text("Dup", tiers)
        result = professor.read_cards(self.cards_dir(dup=text))
        self.assertEqual((result.read, result.rejected), (1, 0))
        expected = ["dup-a", "dup-b", "dup-c", "dup-d", "dup-e"]
        self.assertEqual(list(result.records[0]["ids"]), expected)
        (anomaly,) = result.anomalies
        self.assertEqual((anomaly.kind, anomaly.file), ("duplicate_id", "cartes/dup.md"))
        self.assertEqual(anomaly.line, lines_of(text, "| dup-a |")[1])
        self.assertIn("dup-a", anomaly.detail)

    def test_L15_duplicate_id_between_cards_keeps_the_first_card(self):
        alpha = (SUIVI / "cartes" / "alpha.md").read_text(encoding="utf-8")
        ids = ["alpha-loop", "delta-b", "delta-c", "delta-d"]
        other = card_text("Delta", four_tiers(ids), declared=3)
        result = professor.read_cards(self.cards_dir(alpha=alpha, delta=other))
        cards = {card["name"]: card for card in result.records}
        self.assertEqual(list(cards["Alpha"]["ids"]), ALPHA_IDS)
        self.assertEqual(list(cards["Delta"]["ids"]), ["delta-b", "delta-c", "delta-d"])
        (anomaly,) = result.anomalies
        self.assertEqual((anomaly.kind, anomaly.file), ("duplicate_id", "cartes/delta.md"))
        self.assertEqual(anomaly.line, lines_of(other, "alpha-loop")[0])
        self.assertIn("alpha-loop", anomaly.detail)

    def test_L15_duplicate_id_in_notions_rejects_the_second_row(self):
        text = notions_text(
            notion_row("alpha-loop"),
            notion_row("alpha-loop", "appliquée"),
            notion_row("alpha-sort"),
        )
        result = professor.read_notions(put(self.tmp / "notions.md", text))
        self.assertEqual((result.read, result.rejected), (3, 1))
        (anomaly,) = result.anomalies
        self.assertEqual((anomaly.kind, anomaly.line), ("duplicate_id", 8))
        self.assertIn("alpha-loop", anomaly.detail)
        by_id = {record["id"]: record for record in result.records}
        self.assertEqual(sorted(by_id), ["alpha-loop", "alpha-sort"])
        self.assertEqual(by_id["alpha-loop"]["state"], "en cours")

    def test_L16_unknown_level_fact_is_rejected_and_known_levels_pass(self):
        template = "19/10/2026,3,Alpha,,niveau,{},,,tests/banc-alpha"
        known = ["débutant", "intermédiaire", "avancé", "transcendée"]
        good = read_source(self.tmp, "events", [template.format(level) for level in known])
        self.assertEqual((good.read, good.rejected, len(good.facts)), (4, 0, 4))
        self.assertEqual([fact["value"] for fact in good.facts], known)
        rows = [template.format("expert"), template.format("avancé")]
        bad = read_source(self.tmp, "events", rows)
        self.assertEqual((bad.read, bad.rejected, len(bad.facts)), (2, 1, 1))
        (anomaly,) = bad.anomalies
        self.assertEqual((anomaly.kind, anomaly.line), ("unknown_level", 2))
        self.assertIn("expert", anomaly.detail)

    def test_L17_latin1_bytes_name_the_offset(self):
        valid = {
            "notions": (notions_text(notion_row("alpha-loop")), "notions.md", "read_notions"),
        }
        for kind, (reader, name, header, _, _) in SOURCES.items():
            text = "\n".join([header, dated_row(kind, "15/10/2026")]) + "\n"
            valid[kind] = (text, name, reader)
        for kind, (text, name, reader) in valid.items():
            with self.subTest(source=kind):
                data = text.encode("utf-8") + b"caf\xe9\n"
                path = self.tmp / kind / name
                path.parent.mkdir()
                path.write_bytes(data)
                result = getattr(professor, reader)(path)
                self.assertEqual(result.status, "unavailable")
                message = result.error.replace(str(path), "")
                self.assertRegex(message, rf"\b{len(text.encode('utf-8')) + 3}\b")

    def test_L17_latin1_card_is_rejected_with_the_offset(self):
        cards = self.cards_dir(alpha=(SUIVI / "cartes" / "alpha.md").read_text("utf-8"))
        data = card_text("Latin", four_tiers(["l-a", "l-b", "l-c", "l-d"])).encode("utf-8")
        (cards / "latin.md").write_bytes(data + b"caf\xe9\n")
        result = professor.read_cards(cards)
        self.assertEqual((result.status, result.read, result.rejected), ("ok", 2, 1))
        self.assertEqual([card["name"] for card in result.records], ["Alpha"])
        (anomaly,) = result.anomalies
        self.assertEqual((anomaly.kind, anomaly.file), ("bad_encoding", "cartes/latin.md"))
        self.assertRegex(anomaly.detail, rf"\b{len(data) + 3}\b")


if __name__ == "__main__":
    unittest.main()
