"""Tests de `system_sync.rules.xp` (T7, cas N1 à N11, L1 à L8 et L12 ; A4 à A6, A17, A18).

Contrat de T7.b (`from system_sync.rules import xp`, aucune fonction publique ne lève, appel
par mot-clé compris, aucune lecture de source ni de fichier : les données arrivent lues).
Entrées communes :
- `projects` : `read_projects(...).records` (clés `id`, `frame`, `status`, `date` ISO ou
  `None`, `equivalent_42`, `justification`, `line`) ; `None` si `projets.csv` est absent.
- `history` : `read_history(...).records` (clés `project`, `author`, `line`...) ou `None`.
- `catalogue` : projets 42 de 42calculator (A4), liste de `{slug, name, difficulty}`, ou
  `None` ; `validated` : `Api42Result.projects` (`{id, slug, name, final_mark}`) ou `None`.
- `rules` : dict de `config.load_rules`, dont seuls `ia` et `calibration` sont lus ; `today` :
  `datetime.date` de la synchronisation.
Fonctions :
- `project_entries(projects, history, catalogue, validated, rules, today) -> tuple[dict]` :
  une entrée par projet dans l'ordre reçu, sans enregistrement mal formé ni doublon d'`id`
  (casse ignorée, le premier gardé). Clés de `output._PROJECT` : `id`, `setting` (`frame`),
  `name` (l'`id` : `projets.csv` n'a pas de nom), `status`, `date`, `equivalent_42`,
  `ia_factor` et `xp`.
  - `ia_factor` : moyenne non arrondie des taux `rules["ia"]` des lignes dont `project` égale
    l'`id` sans tenir compte de la casse (A5), `lecture` et auteurs inconnus exclus (`c:148`) ;
    `estimated`, sources contenant `history`, code `ia_rate`. Aucune ligne, `history` vide ou
    `None` : `unmeasurable`, code `ia_history_missing` (A17). Seulement des lignes exclues :
    `insufficient`, code `ia_no_rated_line`. Plusieurs graphies de `project` pour un même
    `id` (`RNCP6` et `rncp6`) : `insufficient`, code `ambiguous_project_key` (`c:94`).
  - `xp` : `difficulty` de l'équivalent × facteur, non arrondie, `estimated`. Refus, dans cet
    ordre : projet `perso` dont `equivalent_42` est le `slug` d'un projet validé,
    `insufficient`, code `duplicates_42_project` (`c:68` ; un projet `pro` ne l'est jamais,
    `c:141`) ; équivalent absent du catalogue, `unmeasurable`, `equivalent_unknown` ;
    `difficulty` négative, non numérique ou non finie, `unmeasurable`, `base_xp_invalid` ;
    facteur non estimé, même statut et même code que le facteur ; date `None`, avant
    2020-01-01 ou après `today`, `insufficient`, `suspect_date` (valeur facultative).
  - Un projet compte dans l'XP Système si et seulement si `status` vaut `livré` et `xp` est
    `estimated` : un facteur 0 compte pour 0.
- `project_anomalies(mêmes paramètres) -> tuple[Anomaly]` : fichier `projets.csv` pour
  `malformed_project` (`id` vide ou non texte, `frame` hors `perso` et `pro`, `status` hors
  des trois de A5, `equivalent_42` absent) et `duplicate_project` (`id` déjà lu) ; fichier
  `historique-ia.csv` pour `unknown_author` (ni dans `rules["ia"]` ni `lecture`) et
  `ambiguous_project_key` (une par `id`) ; ligne de l'enregistrement, détail qui nomme la
  valeur reçue. Une date suspecte n'en ajoute pas (`read_projects` l'a déjà signalée).
- `level42_entity(level, xp, target_xp, validated, catalogue) -> dict` : clés `level`, `xp`,
  `target_xp`, `projects`, `unexplained_gap`. `level` est `Api42Result.level` (`None` :
  `unmeasurable`, code `api_unavailable`) ; `xp` et `target_xp` sont les `StatedValue` de
  `xp_table.xp_for_level` (niveau, puis `calibration.target_level`), rendues telles quelles
  (`None` : `unmeasurable`, `xp_table_unavailable`). Niveau non mesuré : `xp` et l'écart
  `unmeasurable` avec le code du niveau. `projects` : un `{id: slug, name, base_xp}` par
  projet validé, `base_xp` = `difficulty` sans facteur d'IA (`c:147`), `estimated` ; absent
  du catalogue ou invalide : `unmeasurable`, mêmes codes que `xp`. `unexplained_gap` = `xp`
  moins la somme des `base_xp`, `estimated`, `unmeasurable` si un terme manque (`c:62`).
- `system_xp(xp_42, entries) -> dict` : clés `xp` et `origins`. `xp_42` est le `xp` de
  `level42_entity`, `entries` le résultat de `project_entries` (`None` : `projets.csv`
  absent). `xp` = XP_42 + somme des projets comptés, arrondie à l'entier, moitié vers le
  haut (A6), `int`, `estimated`. `origins` : trois `{origin, xp}` dans l'ordre `42`, `perso`,
  `pro`, sommes non arrondies, `estimated`. Sans `projets.csv` : `xp` = XP_42, `estimated`,
  code `no_personal_project`, `perso` et `pro` `unmeasurable` du même code (A5, A6). XP_42
  non mesurée : `xp` et l'origine `42` `unmeasurable` avec son code (`api_unavailable` pour
  `None`), jamais 0.
- Entrée inutilisable : `()` pour les tuples, dict aux mêmes clés de valeurs `unmeasurable`.
Codes à ajouter à `model.REASON_CODES` : `ia_history_missing`, `ia_no_rated_line`,
`ambiguous_project_key`, `duplicates_42_project`, `equivalent_unknown`, `base_xp_invalid`,
`suspect_date` (`ia_rate`, `no_personal_project`, `api_unavailable`, `cursus_absent` et
`xp_table_unavailable` existent déjà).
Écart à trancher : `output.SCHEMA` n'a pas de clé `level42.unexplained_gap` (fiche T7).
"""

import copy
import json
import unittest
from datetime import date
from pathlib import Path

from system_sync import model
from system_sync.sources import professor, xp_table

try:
    from system_sync.rules import xp
except ImportError:
    xp = None  # chaque test échoue séparément tant que le module manque

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "tests" / "fixtures" / "xp"
TABLE_FIXTURE = ROOT / "tests" / "fixtures" / "xp_table" / "valid.json"
TODAY = date(2026, 11, 22)
RULES = {
    "ia": {"louis": 1.0, "mixte": 0.5, "ia": 0.0},
    "calibration": {
        "target_level": 5,
        "r_initial": 0,
        "min_projects": 3,
        "min_days": 90,
    },
}
PROJECT_KEYS = {
    "id",
    "setting",
    "name",
    "status",
    "date",
    "equivalent_42",
    "ia_factor",
    "xp",
}
LEVEL42_KEYS = {"level", "xp", "target_xp", "projects", "unexplained_gap"}
SYSTEM_KEYS = {"xp", "origins"}
DEFAULT = object()
GARBAGE = (None, 3, "x", [None, 3, {}], {"a": 1}, [{"id": 1}], float("nan"))
# XP de la fixture : 450 (niveau 2,5) + 400 × 2/3 (demo-perso-a) + 0 (demo-pro-b).
DEMO_SYSTEM_XP = 717


def load_levels():
    """Couples (niveau, XP) de la table fictive de T5 : de 0 à 5, T(5) = 1 500."""
    data = json.loads(TABLE_FIXTURE.read_text(encoding="utf-8"))
    return tuple((entry["level"], entry["experience"]) for entry in data["levels"])


LEVELS = load_levels()


def table_result():
    """`XpTableResult` de la table fictive, comme le rend `load_xp_table`."""
    table = xp_table.XpTable(
        LEVELS,
        "https://example.invalid/fictional/experience.json",
        "0123456789abcdef0123456789abcdef01234567",
        "0" * 64,
    )
    return xp_table.XpTableResult("ok", None, table)


def level_of(number):
    """Niveau observé de l'API 42."""
    return model.observed(number, ("api42",))


def xp_42_of(level=2.5):
    """XP estimée d'un niveau par la table fictive (2,5 donne 450)."""
    return xp_table.xp_for_level(table_result(), level)


def demo_projects():
    """Les quatre projets de `demo_projects.csv`, lus par `read_projects`."""
    return list(professor.read_projects(FIXTURES / "demo_projects.csv").records)


def demo_history():
    """Les sept lignes de `demo_history.csv`, lues par `read_history`."""
    return list(professor.read_history(FIXTURES / "demo_history.csv").records)


def demo_42():
    """Catalogue fictif des projets 42 et projets validés (`demo-libft`, `demo-alternance`)."""
    return json.loads((FIXTURES / "demo_projects_42.json").read_text(encoding="utf-8"))


def project(
    project_id,
    frame="perso",
    status="livré",
    day="2026-07-01",
    equivalent="demo-minishell",
    line=10,
):
    """Enregistrement au format de `read_projects(...).records`."""
    return {
        "id": project_id,
        "frame": frame,
        "status": status,
        "date": day,
        "equivalent_42": equivalent,
        "justification": "projet fictif",
        "line": line,
    }


def history_line(project_id, author, line=20):
    """Ligne au format de `read_history(...).records`."""
    return {
        "date": "2026-07-01",
        "project": project_id,
        "mode": "professor",
        "domain": "Alpha",
        "notions": "",
        "author": author,
        "proof": "session fictive",
        "line": line,
        "suspect": False,
    }


class XpCase(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(xp, "module system_sync.rules.xp absent")
        self.rules = copy.deepcopy(RULES)
        self.data42 = demo_42()

    def arguments(self, projects, history, catalogue, validated, rules):
        """Paramètres nommés communs, données de démonstration par défaut."""
        return {
            "projects": demo_projects() if projects is DEFAULT else projects,
            "history": demo_history() if history is DEFAULT else history,
            "catalogue": self.data42["catalogue"] if catalogue is DEFAULT else catalogue,
            "validated": self.data42["validated"] if validated is DEFAULT else validated,
            "rules": self.rules if rules is None else rules,
            "today": TODAY,
        }

    def entries(
        self,
        projects=DEFAULT,
        history=DEFAULT,
        catalogue=DEFAULT,
        validated=DEFAULT,
        rules=None,
    ):
        """Tuple de `project_entries`, vérifié."""
        found = xp.project_entries(
            **self.arguments(projects, history, catalogue, validated, rules),
        )
        self.assertIsInstance(found, tuple)
        return found

    def by_id(self, **changes):
        """Entrées indexées par `id`."""
        return {entry["id"]: entry for entry in self.entries(**changes)}

    def anomalies(
        self,
        projects=DEFAULT,
        history=DEFAULT,
        catalogue=DEFAULT,
        validated=DEFAULT,
        rules=None,
    ):
        """Couples (nature, fichier, ligne) de `project_anomalies`."""
        found = xp.project_anomalies(
            **self.arguments(projects, history, catalogue, validated, rules),
        )
        self.assertIsInstance(found, tuple)
        self.assertTrue(all(isinstance(item, model.Anomaly) for item in found))
        return found

    def system(self, entries=DEFAULT, xp_42=DEFAULT):
        """Résultat de `system_xp`, XP_42 de 450 et projets de démonstration par défaut."""
        found = xp.system_xp(
            xp_42=xp_42_of() if xp_42 is DEFAULT else xp_42,
            entries=self.entries() if entries is DEFAULT else entries,
        )
        self.assertEqual(set(found), SYSTEM_KEYS)
        return found

    def origins(self, found):
        """Origines de `system_xp` indexées par nom."""
        return {item["origin"]: item["xp"] for item in found["origins"]}

    def level42(self, level=DEFAULT, xp_value=DEFAULT, catalogue=DEFAULT):
        """Résultat de `level42_entity` au niveau 2,5 par défaut."""
        level = level_of(2.5) if level is DEFAULT else level
        found = xp.level42_entity(
            level=level,
            xp=xp_42_of(level.value) if xp_value is DEFAULT else xp_value,
            target_xp=xp_42_of(5),
            validated=self.data42["validated"],
            catalogue=self.data42["catalogue"] if catalogue is DEFAULT else catalogue,
        )
        self.assertEqual(set(found), LEVEL42_KEYS)
        return found

    def check(self, result, value, status):
        """Vérifie la valeur et le statut d'une valeur statuée."""
        self.assertIsInstance(result, model.StatedValue)
        self.assertEqual((result.value, result.status), (value, status))

    def check_missing(self, result, status, code):
        """Vérifie une valeur sans mesure : valeur `None`, statut et code attendus."""
        self.check(result, None, status)
        self.assertEqual(result.reason_code, code)
        self.assertTrue(result.reason.strip())

    def with_difficulty(self, slug, difficulty):
        """Catalogue de démonstration où `slug` reçoit `difficulty`."""
        catalogue = copy.deepcopy(self.data42["catalogue"])
        for item in catalogue:
            if item["slug"] == slug:
                item["difficulty"] = difficulty
        return catalogue


class NominalTest(XpCase):
    def test_N1_ia_factor_is_the_mean_of_rated_lines_without_lecture(self):
        factor = self.by_id()["demo-perso-a"]["ia_factor"]
        self.assertEqual(factor.status, "estimated")
        self.assertAlmostEqual(factor.value, (1 + 0.5 + 0.5) / 3, places=9)
        self.assertAlmostEqual(factor.value, 0.6667, places=4)
        self.assertIn("history", factor.sources)
        self.assertEqual(factor.reason_code, "ia_rate")
        self.rules["ia"]["mixte"] = 0.25
        factor = self.by_id()["demo-perso-a"]["ia_factor"]
        self.assertAlmostEqual(factor.value, 0.5, places=9)

    def test_N2_project_xp_is_the_base_of_its_equivalent_times_the_factor(self):
        entry = self.by_id()["demo-perso-a"]
        self.assertEqual(set(entry), PROJECT_KEYS)
        self.assertEqual(entry["xp"].status, "estimated")
        self.assertAlmostEqual(entry["xp"].value, 400 * 2 / 3, places=9)
        self.assertAlmostEqual(entry["xp"].value, 266.67, places=2)
        keys = ("setting", "name", "status", "date", "equivalent_42")
        expected = ("perso", "demo-perso-a", "livré", "2026-03-15", "demo-printf")
        self.assertEqual(tuple(entry[key] for key in keys), expected)

    def test_N3_a_zero_factor_is_valid_and_counts_for_zero(self):
        entry = self.by_id()["demo-pro-b"]
        self.check(entry["ia_factor"], 0.0, "estimated")
        self.check(entry["xp"], 0.0, "estimated")
        pro = self.origins(self.system())["pro"]
        self.check(pro, 0.0, "estimated")

    def test_N4_project_without_history_line_is_unmeasurable_and_not_counted(self):
        entry = self.by_id()["demo-perso-c"]
        self.check_missing(entry["ia_factor"], "unmeasurable", "ia_history_missing")
        self.assertIsNone(entry["xp"].value)
        self.assertEqual(entry["xp"].status, "unmeasurable")
        self.assertEqual(self.system()["xp"].value, DEMO_SYSTEM_XP)

    def test_N5_project_with_only_lecture_lines_is_insufficient(self):
        projects = demo_projects() + [project("demo-perso-e")]
        history = demo_history() + [
            history_line("demo-perso-e", "lecture", 30),
            history_line("demo-perso-e", "lecture", 31),
        ]
        entry = self.by_id(projects=projects, history=history)["demo-perso-e"]
        self.check_missing(entry["ia_factor"], "insufficient", "ia_no_rated_line")
        self.assertNotEqual(entry["xp"].status, "estimated")
        entries = self.entries(projects=projects, history=history)
        self.assertEqual(self.system(entries)["xp"].value, DEMO_SYSTEM_XP)

    def test_N6_system_xp_is_xp_42_plus_the_delivered_projects(self):
        found = self.system()
        self.check(found["xp"], DEMO_SYSTEM_XP, "estimated")
        self.assertIs(type(found["xp"].value), int)
        self.assertEqual([item["origin"] for item in found["origins"]], ["42", "perso", "pro"])
        origins = self.origins(found)
        self.check(origins["42"], 450, "estimated")
        self.assertAlmostEqual(origins["perso"].value, 400 * 2 / 3, places=9)
        self.assertEqual(origins["perso"].status, "estimated")

    def test_N6_a_project_in_progress_is_not_counted(self):
        projects = demo_projects() + [project("demo-perso-e", status="en cours")]
        history = demo_history() + [history_line("demo-perso-e", "louis", 30)]
        entries = self.entries(projects=projects, history=history)
        entry = {item["id"]: item for item in entries}["demo-perso-e"]
        self.check(entry["xp"], 300.0, "estimated")
        self.assertEqual(self.system(entries)["xp"].value, DEMO_SYSTEM_XP)

    def test_N7_personal_project_redoing_a_validated_42_project_is_rejected(self):
        entry = self.by_id()["demo-perso-d"]
        self.check_missing(entry["xp"], "insufficient", "duplicates_42_project")
        self.assertIn("demo-libft", entry["xp"].reason)
        self.assertEqual(self.system()["xp"].value, DEMO_SYSTEM_XP)

    def test_N8_apprenticeship_and_pro_project_during_it_add_up(self):
        projects = demo_projects() + [
            project("demo-pro-e", frame="pro", equivalent="demo-alternance"),
        ]
        history = demo_history() + [history_line("demo-pro-e", "louis", 30)]
        entries = self.entries(projects=projects, history=history)
        entry = {item["id"]: item for item in entries}["demo-pro-e"]
        self.check(entry["xp"], 200.0, "estimated")
        found = self.system(entries)
        self.assertEqual(found["xp"].value, DEMO_SYSTEM_XP + 200)
        self.check(self.origins(found)["pro"], 200.0, "estimated")

    def test_N9_42_projects_keep_their_base_xp_whatever_the_ia_share(self):
        found = self.level42()
        bases = [(item["id"], item["base_xp"].value) for item in found["projects"]]
        self.assertEqual(bases, [("demo-libft", 100), ("demo-alternance", 200)])
        statuses = {item["base_xp"].status for item in found["projects"]}
        self.assertEqual(statuses, {"estimated"})
        self.assertEqual(found["projects"][0]["name"], "Demo Libft")
        self.assertNotIn("demo-libft", self.by_id())
        self.check(self.origins(self.system())["42"], 450, "estimated")

    def test_N10_level_42_xp_is_interpolated_and_the_gap_is_shown(self):
        found = self.level42()
        self.check(found["level"], 2.5, "observed")
        self.check(found["xp"], 450, "estimated")
        self.check(found["target_xp"], 1500, "estimated")
        self.check(found["unexplained_gap"], 150, "estimated")
        found = self.level42(level_of(3))
        self.check(found["unexplained_gap"], 300, "estimated")

    def test_N11_without_projects_csv_the_system_is_42_alone(self):
        self.assertEqual(self.entries(projects=None), ())
        found = self.system(entries=None)
        self.check(found["xp"], 450, "estimated")
        self.assertEqual(found["xp"].reason_code, "no_personal_project")
        origins = self.origins(found)
        self.check(origins["42"], 450, "estimated")
        for name in ("perso", "pro"):
            self.check_missing(origins[name], "unmeasurable", "no_personal_project")


class LimitTest(XpCase):
    def test_L1_absent_level_makes_xp_and_system_unmeasurable(self):
        absent = model.unmeasurable("cursus 21 absent", "cursus_absent")
        for level, code in ((None, "api_unavailable"), (absent, "cursus_absent")):
            with self.subTest(level=level):
                found = xp.level42_entity(
                    level=level,
                    xp=None,
                    target_xp=xp_42_of(5),
                    validated=self.data42["validated"],
                    catalogue=self.data42["catalogue"],
                )
                self.check_missing(found["level"], "unmeasurable", code)
                self.check_missing(found["xp"], "unmeasurable", code)
                self.assertEqual(found["unexplained_gap"].status, "unmeasurable")
                system = self.system(xp_42=found["xp"])
                self.check_missing(system["xp"], "unmeasurable", code)
                self.check_missing(self.origins(system)["42"], "unmeasurable", code)
        system = self.system(xp_42=None)
        self.check_missing(system["xp"], "unmeasurable", "api_unavailable")

    def test_L2_absent_or_empty_history_makes_every_factor_unmeasurable(self):
        for history in (None, []):
            with self.subTest(history=history):
                entries = self.entries(history=history)
                self.assertEqual(len(entries), 4)
                for entry in entries:
                    factor = entry["ia_factor"]
                    self.check_missing(factor, "unmeasurable", "ia_history_missing")
                    self.assertNotEqual(entry["xp"].status, "estimated")
                self.check(self.system(entries)["xp"], 450, "estimated")

    def test_L3_malformed_project_records_are_reported_and_others_read(self):
        broken = [
            project("", line=6),
            project("demo-perso-e", frame="école", line=7),
            project("demo-perso-f", status="fini", line=8),
            {
                key: value
                for key, value in project("demo-perso-g", line=9).items()
                if key != "equivalent_42"
            },
        ]
        projects = demo_projects() + broken
        ids = [entry["id"] for entry in self.entries(projects=projects)]
        self.assertEqual(ids, ["demo-perso-a", "demo-pro-b", "demo-perso-c", "demo-perso-d"])
        found = self.anomalies(projects=projects)
        expected = [("malformed_project", "projets.csv", line) for line in (6, 7, 8, 9)]
        self.assertEqual([(a.kind, a.file, a.line) for a in found], expected)
        self.assertIn("école", found[1].detail)

    def test_L4_equivalent_unknown_to_the_catalogue_is_unmeasurable(self):
        projects = demo_projects() + [project("demo-perso-e", equivalent="demo-inconnu")]
        history = demo_history() + [history_line("demo-perso-e", "louis", 30)]
        entries = self.entries(projects=projects, history=history)
        entry = {item["id"]: item for item in entries}["demo-perso-e"]
        self.check_missing(entry["xp"], "unmeasurable", "equivalent_unknown")
        self.assertIn("demo-inconnu", entry["xp"].reason)
        self.assertEqual(self.system(entries)["xp"].value, DEMO_SYSTEM_XP)

    def test_L5_negative_non_numeric_or_nan_base_xp_is_refused(self):
        for difficulty in (-400, "quatre cents", float("nan"), float("inf"), None, True):
            with self.subTest(difficulty=difficulty):
                catalogue = self.with_difficulty("demo-printf", difficulty)
                entries = self.entries(catalogue=catalogue)
                entry = {item["id"]: item for item in entries}["demo-perso-a"]
                self.check_missing(entry["xp"], "unmeasurable", "base_xp_invalid")
                self.assertEqual(self.system(entries)["xp"].value, 450)
                catalogue = self.with_difficulty("demo-libft", difficulty)
                found = self.level42(catalogue=catalogue)
                base = found["projects"][0]["base_xp"]
                self.check_missing(base, "unmeasurable", "base_xp_invalid")
                self.assertEqual(found["unexplained_gap"].status, "unmeasurable")

    def test_L6_unknown_author_line_is_ignored_with_an_anomaly(self):
        history = demo_history() + [history_line("demo-perso-a", "robot", 30)]
        factor = self.by_id(history=history)["demo-perso-a"]["ia_factor"]
        self.assertAlmostEqual(factor.value, 2 / 3, places=9)
        found = self.anomalies(history=history)
        self.assertEqual(
            [(a.kind, a.file, a.line) for a in found],
            [("unknown_author", "historique-ia.csv", 30)],
        )
        self.assertIn("robot", found[0].detail)

    def test_L7_project_delivered_twice_counts_once_with_an_anomaly(self):
        again = project("demo-perso-a", equivalent="demo-printf", line=9)
        projects = demo_projects() + [again]
        entries = self.entries(projects=projects)
        self.assertEqual([entry["id"] for entry in entries].count("demo-perso-a"), 1)
        self.assertEqual(entries[0]["date"], "2026-03-15")
        self.assertEqual(self.system(entries)["xp"].value, DEMO_SYSTEM_XP)
        found = self.anomalies(projects=projects)
        self.assertEqual(
            [(a.kind, a.file, a.line) for a in found],
            [("duplicate_project", "projets.csv", 9)],
        )

    def test_L8_future_or_pre_2020_date_is_suspect_and_not_counted(self):
        for day in ("2027-01-15", "2019-06-01", None):
            with self.subTest(day=day):
                projects = demo_projects() + [project("demo-perso-e", day=day)]
                history = demo_history() + [history_line("demo-perso-e", "louis", 30)]
                entries = self.entries(projects=projects, history=history)
                entry = {item["id"]: item for item in entries}["demo-perso-e"]
                self.assertEqual(entry["xp"].status, "insufficient")
                self.assertEqual(entry["xp"].reason_code, "suspect_date")
                self.assertEqual(self.system(entries)["xp"].value, DEMO_SYSTEM_XP)

    def test_L12_history_keys_spelled_two_ways_make_the_factor_insufficient(self):
        projects = demo_projects() + [
            project("rncp6", frame="pro", equivalent="demo-webserv", line=6),
            project("rncp7", frame="pro", equivalent="demo-minishell", line=7),
        ]
        history = demo_history() + [
            history_line("RNCP6", "louis", 30),
            history_line("rncp6", "ia", 31),
            history_line("RNCP7", "louis", 32),
        ]
        found = self.by_id(projects=projects, history=history)
        factor = found["rncp6"]["ia_factor"]
        self.check_missing(factor, "insufficient", "ambiguous_project_key")
        self.assertNotEqual(found["rncp6"]["xp"].status, "estimated")
        self.check(found["rncp7"]["ia_factor"], 1.0, "estimated")
        reported = self.anomalies(projects=projects, history=history)
        self.assertEqual(
            [(a.kind, a.file) for a in reported],
            [("ambiguous_project_key", "historique-ia.csv")],
        )
        self.assertIn(reported[0].line, (30, 31))


class AmendmentTest(XpCase):
    def stated_values(self):
        """Toutes les valeurs statuées de plusieurs synchronisations, sans mesure comprise."""
        absent = model.unmeasurable("cursus 21 absent", "cursus_absent")
        level42 = self.level42(absent, None)
        measured = self.level42()
        unknown = demo_projects() + [project("demo-perso-e", equivalent="demo-inconnu")]
        entries = self.entries() + self.entries(history=None) + self.entries(projects=unknown)
        found = [entry[key] for entry in entries for key in ("ia_factor", "xp")]
        for entity in (level42, measured):
            found += [entity[key] for key in ("level", "xp", "target_xp", "unexplained_gap")]
        for system in (self.system(), self.system(None), self.system(xp_42=level42["xp"])):
            found += [system["xp"], *self.origins(system).values()]
        return found

    def test_A17_a_value_without_measure_is_never_zero_or_empty(self):
        statuses = set()
        for state in self.stated_values():
            self.assertIsInstance(state, model.StatedValue)
            statuses.add(state.status)
            if state.status == "unmeasurable" or state.value is None:
                self.assertIn(state.status, model.REASON_REQUIRED)
                self.assertIsNone(state.value)
        self.assertEqual(statuses, {"observed", "estimated", "insufficient", "unmeasurable"})

    def test_A18_every_missing_measure_carries_a_reason_with_its_code(self):
        reasons = 0
        for state in self.stated_values():
            if state.status in model.REASON_REQUIRED:
                reasons += 1
                self.assertTrue(state.reason.strip())
                self.assertIn(state.reason_code, model.REASON_CODES)
        self.assertGreaterEqual(reasons, 10)


class ContractTest(XpCase):
    def test_contract_no_public_function_raises_on_garbage(self):
        for junk in GARBAGE:
            with self.subTest(junk=junk):
                arguments = {
                    "projects": junk,
                    "history": junk,
                    "catalogue": junk,
                    "validated": junk,
                    "rules": junk,
                    "today": junk,
                }
                self.assertIsInstance(xp.project_entries(**arguments), tuple)
                self.assertIsInstance(xp.project_anomalies(**arguments), tuple)
                found = xp.level42_entity(
                    level=junk,
                    xp=junk,
                    target_xp=junk,
                    validated=junk,
                    catalogue=junk,
                )
                self.assertEqual(set(found), LEVEL42_KEYS)
                self.assertEqual(set(xp.system_xp(xp_42=junk, entries=junk)), SYSTEM_KEYS)

    def test_contract_positional_call_matches_keyword_call(self):
        arguments = self.arguments(DEFAULT, DEFAULT, DEFAULT, DEFAULT, None)
        by_keyword = xp.project_entries(**arguments)
        self.assertEqual(xp.project_entries(*arguments.values()), by_keyword)
        self.assertEqual(len(by_keyword), 4)


if __name__ == "__main__":
    unittest.main()
