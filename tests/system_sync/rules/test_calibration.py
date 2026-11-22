"""Tests de `system_sync.rules.calibration` (T7, cas N11 à N17, L1 et L9 à L11 ; A6, A7, A17).

Contrat de T7.b (`from system_sync.rules import calibration`, aucune fonction publique ne
lève, appel par mot-clé compris, aucune lecture de source ni de fichier) :
- Point d'ancrage (A7 : donnée versionnée de `config/rules.toml`, `anchors` du plus ancien au
  plus récent) : dict `date` ISO, `xp_system`, `level` (niveau Système affiché), `xp_42`
  (`c:69`) et `r` facultatif, rythme du segment qui en part (`r_initial` à défaut, `c:149`).
- `levels` : couples (niveau, XP) de `XpTableResult.table.levels`, ou `None` ; T et T⁻¹ sont
  leurs interpolations linéaires exactes, sans arrondi. N = `calibration.target_level`.
- Courbe (A6, un seul segment du dernier point au niveau N) : pour un point a de rythme r,
  X_fin = a.xp_system + (1 + r) × (T(N) − a.xp_42), XP Système atteinte quand XP_42 vaut
  T(N) à rythme constant ; Y = T(a.level) + (X − a.xp_system) × (T(N) − T(a.level)) /
  (X_fin − a.xp_system), niveau = T⁻¹(min(Y, T(N))) : tout X ≥ X_fin donne N (au-delà :
  pré-mortem). Sans projet (r = 0 et XP Système = XP_42 au point), il suit le niveau 42.
- `level_at(anchor, xp_system, levels, rules) -> StatedValue` : niveau en `xp_system`,
  `estimated`, code `third_party_table`. X < a.xp_system : `insufficient`, valeur `None`,
  code `xp_below_anchor`, raison qui cite les deux XP. a.level ≥ N ou X_fin ≤ a.xp_system :
  `insufficient`, code `anchor_at_target`, jamais de division par zéro. `levels` `None` :
  `unmeasurable`, `xp_table_unavailable` ; point inutilisable : `unmeasurable`, `no_anchor`.
- `recalibrate(anchor, xp_system, xp_42, r, day, levels, rules) -> dict` : nouveau point
  `{date: day.isoformat(), xp_system, level, xp_42, r}` où `level` = `level_at(anchor,
  xp_system)` : la valeur affichée ne change pas, seule la pente change. `r` négatif, non
  fini ou non numérique, ou niveau non `estimated` : `anchor` rendu tel quel.
- `calibrate(xp_system, xp_42, entries, anchors, levels, rules, today) -> dict` : clés
  `level` et `calibration`. `xp_system` et `xp_42` sont les `StatedValue` de `xp.system_xp`
  et `xp.level42_entity`, `entries` celles de `xp.project_entries` (`None` : `projets.csv`
  absent). Projets livrés depuis le premier point : `status` `livré`, `xp` `estimated`, date
  au moins `anchors[0]["date"]`. r = leur XP / (XP_42 − `anchors[0]["xp_42"]`), estimé
  seulement avec `min_projects` projets ET `min_days` jours depuis `anchors[0]["date"]` (A6).
  Sinon `calibration` est `insufficient`, code `calibration_provisional`, r du dernier point.
  r négatif ou non fini : `insufficient`, code `pace_invalid`, dernier point inchangé. r
  estimé : `estimated` sans raison ; s'il diffère du r du dernier point, `recalibrate` à
  `today`. Valeur de
  `calibration` : `{r, target_level, anchor, recalibrated}`, `anchor` étant le point en
  usage, `r` compris, à reporter dans `config/rules.toml` si `recalibrated` est vrai.
  `level` = `level_at(point en usage, xp_system)`, code `no_personal_project` sans
  `projets.csv` (A6). XP non mesurée : `level` `unmeasurable` avec son code ; `anchors` vide
  ou inutilisable : `level` et `calibration` `unmeasurable`, code `no_anchor`.
- `extend_trajectory(previous, day, level42, system_level) -> tuple[dict]` : lignes reçues
  (`{date, level42, system_level}`, `None` vaut aucune) plus une ligne par appel, même deux
  fois le même jour ; aucune ligne si un niveau n'est ni `observed` ni `estimated` (jamais
  0 à la place, `contexte.md:65`).
Codes à ajouter à `model.REASON_CODES` : `xp_below_anchor`, `anchor_at_target`,
`calibration_provisional`, `pace_invalid`, `no_anchor` (`third_party_table`,
`xp_table_unavailable`, `no_personal_project` et `api_unavailable` existent déjà).
"""

import copy
import json
import random
import re
import unittest
from datetime import timedelta
from pathlib import Path

from system_sync import model
from tests.system_sync.rules.test_xp import FIXTURES, GARBAGE, LEVELS, ROOT, RULES, TODAY

try:
    from system_sync.rules import calibration
except ImportError:
    calibration = None  # chaque test échoue séparément tant que le module manque

RULES_DIR = ROOT / "source" / "system_sync" / "rules"
TARGET = 5
TARGET_XP = 1500
SEED = 20261122
GRID = 1000
TOLERANCE = 1e-9
CALIBRATE_KEYS = {"level", "calibration"}
CALIBRATION_KEYS = {"r", "target_level", "anchor", "recalibrated"}
TRAJECTORY_KEYS = {"date", "level42", "system_level"}
DEFAULT = object()


def t_of(level):
    """XP exacte d'un niveau dans la table fictive (interpolation linéaire)."""
    for (x0, y0), (x1, y1) in zip(LEVELS, LEVELS[1:]):
        if x0 <= level <= x1:
            return y0 + (level - x0) * (y1 - y0) / (x1 - x0)
    raise ValueError(f"niveau {level} hors de la table fictive")


def anchor(day, xp_system, level, xp_42, r=None):
    """Point d'ancrage ; `r` absent vaut `r_initial`."""
    point = {"date": day, "xp_system": xp_system, "level": level, "xp_42": xp_42}
    return point if r is None else {**point, "r": r}


def demo_anchors():
    """Deux points : 2026-01-01 sans `r`, puis 2026-06-01 (450 XP, niveau 2,5, r = 0,5)."""
    return json.loads((FIXTURES / "demo_anchors.json").read_text(encoding="utf-8"))


def estimated(value):
    """Valeur estimée de test."""
    return model.estimated(value, ("test",))


def entry(project_id, xp_value, day, setting="perso", status="livré"):
    """Entrée de `xp.project_entries` ; `xp_value` `None` donne une XP non mesurable.

    Les codes de repli existent déjà : `calibrate` ne lit que le statut de `xp`.
    """
    if xp_value is None:
        xp_state = model.unmeasurable("projet sans mesure", "xp_table_unavailable")
    else:
        xp_state = estimated(xp_value)
    return {
        "id": project_id,
        "setting": setting,
        "name": project_id,
        "status": status,
        "date": day,
        "equivalent_42": "demo-minishell",
        "ia_factor": estimated(1.0),
        "xp": xp_state,
    }


def demo_entries():
    """Entrées des quatre projets de démonstration : deux comptés (266,67 et 0)."""
    rejected = entry("demo-perso-d", None, "2026-06-01")
    rejected["xp"] = model.insufficient("reprise d'un projet 42", "below_threshold")
    return (
        entry("demo-perso-a", 400 * 2 / 3, "2026-03-15"),
        entry("demo-pro-b", 0.0, "2026-04-20", setting="pro"),
        entry("demo-perso-c", None, "2026-05-10"),
        rejected,
    )


def three_projects():
    """Trois projets livrés dix jours avant `TODAY`, 850 XP en tout."""
    day = (TODAY - timedelta(days=10)).isoformat()
    return tuple(
        entry(f"demo-perso-{index}", value, day)
        for index, value in enumerate((200.0, 150.0, 500.0))
    )


def days_ago(count):
    """Date ISO `count` jours avant `TODAY`."""
    return (TODAY - timedelta(days=count)).isoformat()


def random_anchors(count):
    """Points tirés avec une graine fixe, dans la table et sous la cible."""
    rng = random.Random(SEED)
    return [
        anchor(
            "2026-06-01",
            rng.uniform(100, 1400),
            rng.uniform(0.5, 4.5),
            rng.uniform(0, 1200),
            rng.uniform(0, 3),
        )
        for _ in range(count)
    ]


def end_of(point):
    """X_fin d'un point : XP Système atteinte quand XP_42 vaut T(N) à rythme constant."""
    return point["xp_system"] + (1 + point.get("r", 0)) * (TARGET_XP - point["xp_42"])


class CalibrationCase(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(calibration, "module system_sync.rules.calibration absent")
        self.rules = copy.deepcopy(RULES)
        self.anchors = demo_anchors()

    def level(self, point, xp_system, rules=None):
        """`level_at` sur la table fictive."""
        found = calibration.level_at(
            anchor=point,
            xp_system=xp_system,
            levels=LEVELS,
            rules=self.rules if rules is None else rules,
        )
        self.assertIsInstance(found, model.StatedValue)
        return found

    def value(self, point, xp_system):
        """Niveau estimé de la courbe en `xp_system`."""
        found = self.level(point, xp_system)
        self.assertEqual(found.status, "estimated", found.reason)
        return found.value

    def calibrate(self, xp_system, xp_42=450, entries=DEFAULT, anchors=None):
        """`calibrate` au jour `TODAY` ; les nombres deviennent des valeurs estimées."""
        found = calibration.calibrate(
            xp_system=estimated(xp_system) if isinstance(xp_system, int) else xp_system,
            xp_42=estimated(xp_42) if isinstance(xp_42, int) else xp_42,
            entries=demo_entries() if entries is DEFAULT else entries,
            anchors=self.anchors if anchors is None else anchors,
            levels=LEVELS,
            rules=self.rules,
            today=TODAY,
        )
        self.assertEqual(set(found), CALIBRATE_KEYS)
        return found

    def check_missing(self, result, status, code):
        """Vérifie une valeur sans mesure : valeur `None`, statut et code attendus."""
        self.assertIsInstance(result, model.StatedValue)
        self.assertEqual((result.value, result.status), (None, status))
        self.assertEqual(result.reason_code, code)
        self.assertTrue(result.reason.strip())

    def check_state(self, found, status, code, r):
        """Vérifie le statut, le code et le rythme de la valeur `calibration`."""
        state = found["calibration"]
        self.assertEqual((state.status, state.reason_code), (status, code))
        self.assertEqual(set(state.value), CALIBRATION_KEYS)
        self.assertAlmostEqual(state.value["r"], r, places=9)
        self.assertEqual(state.value["target_level"], TARGET)
        return state.value


class NominalTest(CalibrationCase):
    def test_N11_without_projects_csv_the_system_level_follows_level_42(self):
        xp_system = model.estimated(450, ("test",), "aucun projet", "no_personal_project")
        found = self.calibrate(xp_system, entries=None, anchors=self.anchors[:1])
        self.assertEqual(found["level"].status, "estimated")
        self.assertEqual(found["level"].reason_code, "no_personal_project")
        self.assertAlmostEqual(found["level"].value, 2.5, delta=TOLERANCE)
        self.check_state(found, "insufficient", "calibration_provisional", 0)
        self.assertAlmostEqual(self.value(self.anchors[0], 1000), 4.0, delta=TOLERANCE)

    def test_N12_the_curve_goes_through_the_anchor(self):
        self.assertAlmostEqual(self.value(self.anchors[1], 450), 2.5, delta=TOLERANCE)
        self.assertAlmostEqual(self.value(self.anchors[0], 300), 2.0, delta=TOLERANCE)
        for point in random_anchors(20):
            self.assertAlmostEqual(
                self.value(point, point["xp_system"]),
                point["level"],
                delta=TOLERANCE,
            )

    def test_N12_the_displayed_level_starts_from_the_last_anchor(self):
        found = self.calibrate(717)
        self.assertAlmostEqual(
            found["level"].value,
            self.value(self.anchors[1], 717),
            delta=TOLERANCE,
        )
        self.assertNotAlmostEqual(found["level"].value, self.value(self.anchors[0], 717))

    def test_N13_the_curve_is_continuous_and_strictly_increasing(self):
        step = 1e-6
        for point in [self.anchors[1], *random_anchors(5)]:
            start, end = point["xp_system"], end_of(point)
            grid = [start + (end - start) * index / (GRID - 1) for index in range(GRID)]
            levels = [self.value(point, x) for x in grid]
            mean_step = (TARGET - point["level"]) / (GRID - 1)
            for before, after in zip(levels, levels[1:]):
                self.assertGreater(after, before)
                self.assertLess(after - before, 10 * mean_step)
            span = (end - start) / (TARGET_XP - t_of(point["level"]))
            knots = [
                start + (xp_value - t_of(point["level"])) * span
                for level, xp_value in LEVELS
                if point["level"] < level < TARGET
            ]
            for x in [*grid[1:-1], *knots]:
                jump = self.value(point, x + step) - self.value(point, x - step)
                self.assertLess(abs(jump), 1e-6)

    def test_N14_at_constant_pace_the_target_is_reached_with_xp_42(self):
        for point in [self.anchors[1], *random_anchors(5)]:
            pace = point.get("r", 0)
            previous = None
            for index in range(GRID):
                xp_42 = point["xp_42"] + (TARGET_XP - point["xp_42"]) * index / (GRID - 1)
                xp_system = point["xp_system"] + (1 + pace) * (xp_42 - point["xp_42"])
                found = self.value(point, xp_system)
                if index < GRID - 1:
                    self.assertLess(found, TARGET)
                if previous is not None:
                    self.assertGreater(found, previous)
                previous = found
            self.assertAlmostEqual(previous, TARGET, delta=TOLERANCE)
        self.assertAlmostEqual(self.value(self.anchors[1], 2100), TARGET, delta=TOLERANCE)

    def test_N15_a_recalibration_never_changes_the_displayed_value(self):
        rng = random.Random(SEED)
        points = random_anchors(100)
        for point in points:
            xp_system = rng.uniform(point["xp_system"], end_of(point))
            xp_42 = rng.uniform(point["xp_42"], TARGET_XP - 1)
            pace = rng.uniform(0, 3)
            shown = self.value(point, xp_system)
            moved = calibration.recalibrate(
                anchor=point,
                xp_system=xp_system,
                xp_42=xp_42,
                r=pace,
                day=TODAY,
                levels=LEVELS,
                rules=self.rules,
            )
            self.assertEqual(moved["date"], TODAY.isoformat())
            self.assertEqual((moved["xp_system"], moved["xp_42"]), (xp_system, xp_42))
            self.assertEqual(moved["r"], pace)
            self.assertAlmostEqual(moved["level"], shown, delta=TOLERANCE)
            self.assertAlmostEqual(self.value(moved, xp_system), shown, delta=TOLERANCE)
            self.assertAlmostEqual(self.value(moved, end_of(moved)), TARGET, delta=TOLERANCE)
            self.assertLess(self.value(moved, end_of(moved) - 1), TARGET)

    def test_N15_calibrate_recalibrates_without_moving_the_displayed_value(self):
        first = anchor(days_ago(90), 300, 2.0, 300)
        found = self.calibrate(1300, entries=three_projects(), anchors=[first])
        self.assertEqual(found["level"].status, "estimated")
        self.assertAlmostEqual(found["level"].value, self.value(first, 1300), delta=TOLERANCE)
        self.assertAlmostEqual(found["level"].value, 4.6, delta=TOLERANCE)
        state = self.check_state(found, "estimated", None, 850 / 150)
        self.assertTrue(state["recalibrated"])
        moved = state["anchor"]
        self.assertEqual((moved["date"], moved["xp_system"]), (TODAY.isoformat(), 1300))
        self.assertEqual(moved["xp_42"], 450)
        self.assertAlmostEqual(moved["r"], 850 / 150, places=9)

    def test_N16_calibration_is_provisional_below_three_projects_or_90_days(self):
        found = self.calibrate(717)
        state = self.check_state(found, "insufficient", "calibration_provisional", 0.5)
        self.assertFalse(state["recalibrated"])
        self.assertEqual(state["anchor"]["date"], "2026-06-01")
        self.assertEqual(found["level"].status, "estimated")
        first = anchor(days_ago(89), 300, 2.0, 300)
        found = self.calibrate(1300, entries=three_projects(), anchors=[first])
        state = self.check_state(found, "insufficient", "calibration_provisional", 0)
        self.assertFalse(state["recalibrated"])
        self.assertEqual(state["anchor"]["date"], first["date"])
        first = anchor(days_ago(90), 300, 2.0, 300)
        found = self.calibrate(1300, entries=three_projects()[:2], anchors=[first])
        self.check_state(found, "insufficient", "calibration_provisional", 0)

    def test_N17_one_trajectory_line_per_synchronisation(self):
        line = calibration.extend_trajectory(
            previous=None,
            day=TODAY,
            level42=model.observed(2.5, ("api42",)),
            system_level=estimated(3.05),
        )
        self.assertEqual(line, ({"date": "2026-11-22", "level42": 2.5, "system_level": 3.05},))
        lines = calibration.extend_trajectory(
            previous=line,
            day=TODAY,
            level42=model.observed(2.6, ("api42",)),
            system_level=estimated(3.1),
        )
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0], line[0])
        self.assertEqual(lines[1]["level42"], 2.6)
        self.assertTrue(all(set(item) == TRAJECTORY_KEYS for item in lines))


class LimitTest(CalibrationCase):
    def test_L1_unmeasured_xp_gives_no_level_and_no_trajectory_line(self):
        down = model.unmeasurable("API 42 indisponible", "api_unavailable")
        found = self.calibrate(down, xp_42=down)
        self.check_missing(found["level"], "unmeasurable", "api_unavailable")
        previous = ({"date": "2026-11-21", "level42": 2.5, "system_level": 3.05},)
        lines = calibration.extend_trajectory(
            previous=previous,
            day=TODAY,
            level42=down,
            system_level=found["level"],
        )
        self.assertEqual(lines, previous)

    def test_L9_negative_or_infinite_pace_is_refused_and_the_anchor_kept(self):
        flat = anchor(days_ago(120), 450, 2.5, 450)
        fallen = anchor(days_ago(120), 600, 3.0, 600)
        for point in (flat, fallen):
            with self.subTest(point=point):
                found = self.calibrate(1300, entries=three_projects(), anchors=[point])
                state = self.check_state(found, "insufficient", "pace_invalid", 0)
                self.assertFalse(state["recalibrated"])
                self.assertEqual(state["anchor"]["date"], point["date"])
                self.assertEqual(state["anchor"]["xp_system"], point["xp_system"])
                expected = self.value(point, 1300)
                self.assertAlmostEqual(found["level"].value, expected, delta=TOLERANCE)
        for pace in (-1, float("inf"), float("nan"), "x", None):
            with self.subTest(pace=pace):
                moved = calibration.recalibrate(
                    anchor=self.anchors[1],
                    xp_system=717,
                    xp_42=450,
                    r=pace,
                    day=TODAY,
                    levels=LEVELS,
                    rules=self.rules,
                )
                self.assertEqual(moved, self.anchors[1])

    def test_L10_system_xp_below_the_anchor_gives_no_invented_level(self):
        found = self.level(self.anchors[1], 400)
        self.check_missing(found, "insufficient", "xp_below_anchor")
        self.assertIn("400", found.reason)
        self.assertIn("450", found.reason)
        found = self.calibrate(400)
        self.check_missing(found["level"], "insufficient", "xp_below_anchor")

    def test_L11_target_not_above_the_anchor_level_never_divides_by_zero(self):
        at_target = anchor("2026-06-01", 1500, 5.0, 1500)
        flat_end = anchor("2026-06-01", 1000, 4.0, 1500)
        for point in (at_target, flat_end):
            with self.subTest(point=point):
                found = self.level(point, 1600)
                self.check_missing(found, "insufficient", "anchor_at_target")
        low = copy.deepcopy(self.rules)
        low["calibration"]["target_level"] = 2
        found = self.level(self.anchors[1], 717, rules=low)
        self.check_missing(found, "insufficient", "anchor_at_target")


class ContractTest(CalibrationCase):
    def test_contract_no_public_function_raises_on_garbage(self):
        for junk in GARBAGE:
            with self.subTest(junk=junk):
                found = calibration.level_at(
                    anchor=junk,
                    xp_system=junk,
                    levels=junk,
                    rules=junk,
                )
                self.assertIsInstance(found, model.StatedValue)
                calibration.recalibrate(
                    anchor=junk,
                    xp_system=junk,
                    xp_42=junk,
                    r=junk,
                    day=junk,
                    levels=junk,
                    rules=junk,
                )
                found = calibration.calibrate(
                    xp_system=junk,
                    xp_42=junk,
                    entries=junk,
                    anchors=junk,
                    levels=junk,
                    rules=junk,
                    today=junk,
                )
                self.assertEqual(set(found), CALIBRATE_KEYS)
                found = calibration.extend_trajectory(
                    previous=junk,
                    day=junk,
                    level42=junk,
                    system_level=junk,
                )
                self.assertIsInstance(found, tuple)

    def test_contract_no_anchor_makes_level_and_calibration_unmeasurable(self):
        for anchors in ([], [{"date": "2026-06-01"}]):
            with self.subTest(anchors=anchors):
                found = self.calibrate(717, anchors=anchors)
                self.check_missing(found["level"], "unmeasurable", "no_anchor")
                self.check_missing(found["calibration"], "unmeasurable", "no_anchor")


class ArchitectureTest(unittest.TestCase):
    def test_criterion_3_rules_never_import_sources(self):
        for name in ("xp.py", "calibration.py"):
            path = RULES_DIR / name
            self.assertTrue(path.is_file(), f"module system_sync.rules.{path.stem} absent")
        pattern = re.compile(r"^(from|import) .*sources", re.MULTILINE)
        found = [
            path.name
            for path in sorted(RULES_DIR.glob("*.py"))
            if pattern.search(path.read_text(encoding="utf-8"))
        ]
        self.assertEqual(found, [])


if __name__ == "__main__":
    unittest.main()
