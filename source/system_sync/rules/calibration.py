"""Calibration du niveau Système (T7, A6, A7, A17) : fonctions pures, sans source.

La courbe n'a qu'un segment, du dernier point d'ancrage au niveau cible N (A6). Partie du
point a de rythme r, elle atteint N quand l'XP 42 atteint T(N) à rythme constant :
X_fin = a.xp_system + (1 + r) × (T(N) − a.xp_42), et le niveau en X vaut T⁻¹ de
T(a.level) + (X − a.xp_system) × (T(N) − T(a.level)) / (X_fin − a.xp_system), plafonné à
T(N). Un recalibrage crée un point à l'XP courante et au niveau affiché : la valeur ne
change jamais, seule la pente change (`c:69`). Les points viennent de `config/rules.toml`
(A7) et la trajectoire est rendue, jamais écrite ici. Aucune fonction publique ne lève.
Contrat : `tests/system_sync/rules/test_calibration.py`.
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import NamedTuple

from system_sync.interpolation import interpolate
from system_sync.model import estimated, insufficient, unmeasurable
from system_sync.rules.guard import never_raises
from system_sync.rules.xp import (
    API_SOURCE,
    ESTIMATED,
    NO_PROJECT,
    NO_PROJECT_CODE,
    PROJECTS_SOURCE,
    THIRD_PARTY_CODE,
    XP_INVALID_CODE,
    is_counted,
    is_nonnegative,
    is_number,
    missing_measure,
)

TABLE_SOURCE = "xp_table"
# Nombres obligatoires d'un point d'ancrage, tous finis et positifs ou nuls.
ANCHOR_NUMBERS = ("xp_system", "level", "xp_42")
NO_ANCHOR_CODE = "no_anchor"
AT_TARGET_CODE = "anchor_at_target"


class _Segment(NamedTuple):
    """Segment de courbe d'un point d'ancrage.

    Args:
        x_start: XP Système du point.
        x_end: XP Système X_fin où la courbe atteint le niveau cible.
        y_start: T(niveau du point), XP de la table.
        y_end: T(niveau cible), XP de la table.
    """

    x_start: object
    x_end: object
    y_start: object
    y_end: object


@dataclass(frozen=True)
class _Sync:
    """Mesures et règles d'une synchronisation, déjà validées.

    Args:
        xp_system: XP Système, nombre fini.
        xp_42: XP 42, nombre fini.
        entries: tuple de `xp.project_entries`, ou `None` si `projets.csv` est absent.
        levels: couples (niveau, XP) de la table XP.
        rules: dict de `config.load_rules`.
        today: `datetime.date` de la synchronisation.
    """

    xp_system: object
    xp_42: object
    entries: object
    levels: object
    rules: dict
    today: date


def _day(text):
    """Lit une date ISO `AAAA-MM-JJ` ; `None` si elle est absente ou illisible."""
    try:
        return date.fromisoformat(text)
    except (TypeError, ValueError):
        return None


def _is_day(value):
    """Dit si `value` est une `datetime.date` sans heure."""
    return (
        isinstance(value, date)
        and not isinstance(value, datetime)
    )


def _anchor(point, rules):
    """Valide un point d'ancrage et complète son rythme par `r_initial` (`c:149`).

    Args:
        point: dict `date` ISO, `xp_system`, `level`, `xp_42` et `r` facultatif.
        rules: dict de `config.load_rules`, dont `calibration.r_initial` est lu.

    Returns:
        Une copie du point avec `r`, ou `None` si sa date est illisible ou si un de ses
        nombres est négatif, non fini ou absent.
    """
    if not isinstance(point, dict):
        return None
    pace = point.get("r", rules["calibration"]["r_initial"])
    numbers = [*(point.get(key) for key in ANCHOR_NUMBERS), pace]
    if not all(is_nonnegative(number) for number in numbers):
        return None
    if _day(point.get("date")) is None:
        return None
    return {**point, "r": pace}


def _segment(point, levels, target):
    """Construit le segment d'un point, du niveau du point au niveau cible.

    Args:
        point: point d'ancrage validé par `_anchor`.
        levels: couples (niveau, XP) de la table XP.
        target: niveau cible N.

    Returns:
        Le couple (`_Segment`, `None`), ou (`None`, valeur `insufficient`) si le point est
        déjà à la cible, hors de la table ou si le segment est de longueur nulle.
    """
    if point["level"] >= target:
        reason = f"niveau du point d'ancrage {point['level']} déjà au niveau cible {target}"
        return None, insufficient(reason, AT_TARGET_CODE)
    y_start, y_end = interpolate(levels, point["level"]), interpolate(levels, target)
    if y_start is None or y_end is None:
        reason = f"niveau du point {point['level']} ou cible {target} hors de la table XP"
        return None, insufficient(reason, "level_out_of_table")
    x_start = point["xp_system"]
    x_end = x_start + (1 + point["r"]) * (y_end - point["xp_42"])
    if x_end <= x_start:
        reason = (
            f"XP 42 du point ({point['xp_42']}) déjà à T({target}) = {y_end} : "
            "segment de longueur nulle"
        )
        return None, insufficient(reason, AT_TARGET_CODE)
    return _Segment(x_start, x_end, y_start, y_end), None


def _curve_level(point, xp_system, levels, target):
    """Lit le niveau de la courbe d'un point validé en `xp_system`.

    Args:
        point: point d'ancrage validé par `_anchor`.
        xp_system: XP Système, nombre fini.
        levels: couples (niveau, XP) de la table XP.
        target: niveau cible N.

    Returns:
        La valeur `estimated` du niveau, ou `insufficient` (`xp_below_anchor`,
        `anchor_at_target`, `level_out_of_table`).
    """
    if xp_system < point["xp_system"]:
        reason = (
            f"XP Système {xp_system} inférieure à celle du point d'ancrage "
            f"({point['xp_system']}) : aucun niveau n'est inventé"
        )
        return insufficient(reason, "xp_below_anchor")
    segment, problem = _segment(point, levels, target)
    if problem is not None:
        return problem
    progress = (xp_system - segment.x_start) / (segment.x_end - segment.x_start)
    curve = segment.y_start + progress * (segment.y_end - segment.y_start)
    inverse = tuple((xp_value, level) for level, xp_value in levels)
    level = interpolate(inverse, min(curve, segment.y_end))
    reason = "niveau Système lu sur la table XP tierce, le long de la courbe calibrée"
    return estimated(float(level), (TABLE_SOURCE,), reason, THIRD_PARTY_CODE)


def _no_level(error):
    """Niveau de repli : calibration inutilisable."""
    return unmeasurable(f"calibration inutilisable : {error}", NO_ANCHOR_CODE)


@never_raises(_no_level)
def level_at(anchor, xp_system, levels, rules):
    """Niveau Système de la courbe partie d'un point d'ancrage, en `xp_system`.

    Args:
        anchor: point d'ancrage (dict `date`, `xp_system`, `level`, `xp_42`, `r`).
        xp_system: XP Système, nombre fini.
        levels: couples (niveau, XP) de `XpTableResult.table.levels`, ou `None`.
        rules: dict de `config.load_rules`, dont `calibration` est lu.

    Returns:
        La valeur `estimated` (code `third_party_table`) ; `insufficient` sous le point ou
        si le point est à la cible ; `unmeasurable` sans table (`xp_table_unavailable`),
        point inutilisable (`no_anchor`) ou XP invalide (`xp_invalid`).
    """
    target = rules["calibration"]["target_level"]
    if levels is None:
        reason = "table XP indisponible : niveau Système non calculable"
        return unmeasurable(reason, "xp_table_unavailable")
    point = _anchor(anchor, rules)
    if point is None:
        return unmeasurable(f"point d'ancrage {anchor!r} inutilisable", NO_ANCHOR_CODE)
    if not is_number(xp_system):
        reason = f"XP Système {xp_system!r} : nombre fini attendu"
        return unmeasurable(reason, XP_INVALID_CODE)
    return _curve_level(point, xp_system, levels, target)


def _refused(error):
    """Repli d'un recalibrage impossible : aucun nouveau point."""
    return None


@never_raises(_refused)
def _moved_anchor(anchor, xp_system, xp_42, r, day, levels, rules):
    """Construit le nouveau point d'un recalibrage, ou `None` s'il est refusé."""
    shown = level_at(anchor, xp_system, levels, rules)
    if shown.status != ESTIMATED:
        return None
    candidate = {
        "date": day.isoformat(),
        "xp_system": xp_system,
        "level": shown.value,
        "xp_42": xp_42,
        "r": r,
    }
    return _anchor(candidate, rules)


def recalibrate(anchor, xp_system, xp_42, r, day, levels, rules):
    """Recalibre la courbe : nouveau point à l'XP courante, au niveau affiché (`c:69`).

    Args:
        anchor: point d'ancrage en usage.
        xp_system: XP Système courante, nombre fini.
        xp_42: XP 42 courante, nombre fini.
        r: nouveau rythme, nombre fini positif ou nul.
        day: `datetime.date` du recalibrage.
        levels: couples (niveau, XP) de la table XP, ou `None`.
        rules: dict de `config.load_rules`.

    Returns:
        Le point `{date, xp_system, level, xp_42, r}` ; `anchor` tel quel si `r` ou une
        autre entrée est inutilisable, ou si le niveau affiché n'est pas estimé.
    """
    moved = _moved_anchor(anchor, xp_system, xp_42, r, day, levels, rules)
    return anchor if moved is None else moved


def _anchors(anchors, rules):
    """Valide tous les points d'ancrage ; `None` si la liste est vide ou un point est faux."""
    if not isinstance(anchors, (list, tuple)):
        return None
    points = [_anchor(point, rules) for point in anchors]
    if not points or None in points:
        return None
    return points


def _on_or_after(text, since):
    """Dit si une date ISO de projet est lisible et au moins égale à `since`."""
    day = _day(text)
    return day is not None and day >= since


def _delivered_since(entries, since):
    """Renvoie les projets comptés dans l'XP Système et livrés depuis `since`."""
    if entries is None:
        return []
    return [
        entry
        for entry in entries
        if is_counted(entry)
        if _on_or_after(entry["date"], since)
    ]


def _pace(total, gain):
    """Calcule r = XP perso et pro livrée / XP 42 gagnée depuis le premier point (A6).

    Args:
        total: XP des projets livrés depuis le premier point, nombre fini.
        gain: XP 42 gagnée sur la même période, nombre fini.

    Returns:
        Le couple (r, `None`), ou (`None`, raison) si l'XP 42 n'a pas augmenté ou si r
        est négatif ou non fini.
    """
    if not gain > 0:
        return None, f"XP 42 gagnée depuis le premier point : {gain}, positive attendue"
    pace = total / gain
    if not is_nonnegative(pace):
        return None, f"rythme r = {pace} négatif ou non fini"
    return pace, None


def _value(point, pace, settings, recalibrated):
    """Valeur `{r, target_level, anchor, recalibrated}` de l'état de calibration."""
    return {
        "r": pace,
        "target_level": settings["target_level"],
        "anchor": point,
        "recalibrated": recalibrated,
    }


def _unchanged(reason, code, last, settings):
    """Calibration `insufficient` qui garde le dernier point et son rythme.

    Args:
        reason: phrase française non vide.
        code: `calibration_provisional` ou `pace_invalid`.
        last: dernier point d'ancrage validé.
        settings: table `rules["calibration"]`.

    Returns:
        Le couple (valeur statuée, point en usage).
    """
    value = _value(last, last["r"], settings, False)
    return insufficient(reason, code, value), last


def _calibration(sync, points):
    """Estime r et recalibre si besoin.

    Args:
        sync: mesures et règles validées de la synchronisation.
        points: points d'ancrage validés, du plus ancien au plus récent.

    Returns:
        Le couple (valeur statuée de la calibration, point en usage).
    """
    settings = sync.rules["calibration"]
    first, last = points[0], points[-1]
    since = _day(first["date"])
    delivered = _delivered_since(sync.entries, since)
    elapsed = (sync.today - since).days
    if (
        len(delivered) < settings["min_projects"]
        or elapsed < settings["min_days"]
    ):
        reason = (
            f"calibration provisoire : {len(delivered)} projets livrés (au moins "
            f"{settings['min_projects']}) et {elapsed} jours depuis le premier point "
            f"(au moins {settings['min_days']})"
        )
        return _unchanged(reason, "calibration_provisional", last, settings)
    total = sum(entry["xp"].value for entry in delivered)
    pace, problem = _pace(total, sync.xp_42 - first["xp_42"])
    if problem is not None:
        reason = f"{problem} : point d'ancrage inchangé"
        return _unchanged(reason, "pace_invalid", last, settings)
    point = last
    if pace != last["r"]:
        point = recalibrate(
            last,
            sync.xp_system,
            sync.xp_42,
            pace,
            sync.today,
            sync.levels,
            sync.rules,
        )
    value = _value(point, pace, settings, point is not last)
    return estimated(value, (PROJECTS_SOURCE, API_SOURCE)), point


def _shown_level(point, sync):
    """Niveau affiché sur la courbe du point en usage (A6).

    Args:
        point: point d'ancrage en usage.
        sync: mesures et règles validées de la synchronisation.

    Returns:
        La valeur statuée de `level_at`, de code `no_personal_project` si elle est estimée
        sans `projets.csv`.
    """
    level = level_at(point, sync.xp_system, sync.levels, sync.rules)
    if sync.entries is not None or level.status != ESTIMATED:
        return level
    return estimated(level.value, level.sources, NO_PROJECT, NO_PROJECT_CODE)


def _both(state):
    """Résultat de `calibrate` dont le niveau et la calibration valent `state`."""
    return {"level": state, "calibration": state}


def _no_calibration(error):
    """Résultat de repli de `calibrate` : niveau et calibration `unmeasurable`."""
    return _both(_no_level(error))


@never_raises(_no_calibration)
def calibrate(xp_system, xp_42, entries, anchors, levels, rules, today):
    """Calcule le niveau Système affiché et l'état de la calibration (A6).

    Args:
        xp_system: valeur `xp` de `xp.system_xp`.
        xp_42: valeur `xp` de `xp.level42_entity`.
        entries: tuple de `xp.project_entries`, ou `None` si `projets.csv` est absent.
        anchors: points d'ancrage de `config/rules.toml`, du plus ancien au plus récent.
        levels: couples (niveau, XP) de la table XP, ou `None`.
        rules: dict de `config.load_rules`, dont `calibration` est lu.
        today: `datetime.date` de la synchronisation.

    Returns:
        Le dict `level` et `calibration` (valeur `{r, target_level, anchor,
        recalibrated}`) ; tous deux `unmeasurable` sans point utilisable (`no_anchor`) ou
        sans XP mesurée (code de l'XP).
    """
    points = _anchors(anchors, rules)
    if points is None:
        reason = f"aucun point d'ancrage utilisable parmi {anchors!r}"
        return _both(unmeasurable(reason, NO_ANCHOR_CODE))
    for state, noun in ((xp_system, "XP Système"), (xp_42, "XP 42")):
        missing = missing_measure(state, noun, XP_INVALID_CODE)
        if missing is not None:
            return _both(missing)
    sync = _Sync(xp_system.value, xp_42.value, entries, levels, rules, today)
    state, point = _calibration(sync, points)
    return {"level": _shown_level(point, sync), "calibration": state}


def _is_measured_level(state):
    """Dit si un niveau est observé ou estimé, de nombre fini."""
    return missing_measure(state, "niveau", "level_invalid") is None


def extend_trajectory(previous, day, level42, system_level):
    """Ajoute la ligne de trajectoire d'une synchronisation (A7, cas N17).

    Args:
        previous: lignes `{date, level42, system_level}` déjà connues, ou `None`.
        day: `datetime.date` de la synchronisation.
        level42: valeur statuée du niveau 42.
        system_level: valeur `level` de `calibrate`.

    Returns:
        Le tuple des lignes reçues, plus une ligne si les deux niveaux sont mesurés et
        `day` est une date (jamais 0 à la place d'un niveau, `contexte.md:65`).
    """
    lines = tuple(previous) if isinstance(previous, (list, tuple)) else ()
    measured = all(_is_measured_level(state) for state in (level42, system_level))
    if (
        not measured
        or not _is_day(day)
    ):
        return lines
    line = {
        "date": day.isoformat(),
        "level42": level42.value,
        "system_level": system_level.value,
    }
    return (*lines, line)
