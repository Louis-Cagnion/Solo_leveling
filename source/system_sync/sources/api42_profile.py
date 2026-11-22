"""Extraction de `/v2/me` et de la liste complète des achievements (T4, A23).

Liste blanche (`conception.md:33`) : seuls le niveau du cursus 21, les projets validés et
les achievements sortent ; un élément mal formé ou en double devient une `model.Anomaly`
dont `file` est le chemin d'API. Aucune fonction publique ne lève.
"""

import logging
import math
import re
from dataclasses import dataclass
from datetime import date

from system_sync import model

SOURCE = "api42"
CURSUS_ID = 21
ME_PATH = "/v2/me"
ACHIEVEMENTS_PATH = "/v2/achievements"
ME_LISTS = ("cursus_users", "projects_users", "achievements")
PROJECT_KEYS = ("id", "slug", "name", "final_mark")
ITEM_KEYS = ("id", "name", "description", "obtained", "obtained_on", "title")
PREVIEW_LENGTH = 40
MALFORMED_DETAIL = "champ absent ou de type inattendu"
# Surrogate isolé (`"\ud800"` reçu en JSON) : l'écriture UTF-8 du cache le refuserait.
SURROGATE = re.compile("[\ud800-\udfff]")
LOGGER = logging.getLogger(__name__)


def is_number(value):
    """Dit si une valeur JSON est un nombre fini, booléens exclus.

    Args:
        value: valeur de n'importe quel type.

    Returns:
        True pour un `int` ou un `float` fini qui n'est pas un `bool`.
    """
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def is_integer(value):
    """Dit si une valeur JSON est un entier, booléens exclus.

    Args:
        value: valeur de n'importe quel type.

    Returns:
        True pour un `int` qui n'est pas un `bool`.
    """
    return isinstance(value, int) and not isinstance(value, bool)


def preview(value):
    """Rend une valeur reçue sous une forme courte et sûre pour un message.

    Args:
        value: valeur de n'importe quel type.

    Returns:
        Le `repr` de la valeur, tronqué à `PREVIEW_LENGTH` caractères.
    """
    text = repr(value)
    return text if len(text) <= PREVIEW_LENGTH else text[:PREVIEW_LENGTH] + "…"


@dataclass(frozen=True)
class Api42Result:
    """Résultat de lecture de l'API 42.

    Args:
        status: `ok`, `cache` ou `unavailable`.
        error: `None` si `ok`, sinon la cause, puis l'issue du cache.
        level: `StatedValue` du niveau du cursus 21.
        complete: `StatedValue` booléenne, liste complète des achievements lue (A23).
        projects: tuple des projets validés, dicts de clés `PROJECT_KEYS`.
        achievements: tuple des achievements, dicts de clés `ITEM_KEYS` (A23).
        observed_at: date ISO de la lecture, ou `None`.
        anomalies: tuple de `model.Anomaly`, `file` étant le chemin d'API.
        read: nombre d'éléments reçus (projets, obtenus et liste complète).
        rejected: nombre d'éléments écartés (doublons, éléments mal formés).
    """

    status: str
    error: str | None
    level: model.StatedValue
    complete: model.StatedValue
    projects: tuple = ()
    achievements: tuple = ()
    observed_at: str | None = None
    anomalies: tuple = ()
    read: int = 0
    rejected: int = 0


def surrogate_problem(record, names):
    """Nomme le premier champ texte qu'UTF-8 ne peut pas encoder (surrogate isolé).

    Args:
        record: dict déjà contrôlé.
        names: tuple des noms de ses champs texte gardés.

    Returns:
        La cause qui nomme le champ et sa valeur, ou `None`.
    """
    for name in names:
        value = record.get(name)
        if isinstance(value, str) and SURROGATE.search(value):
            return f"champ {name} {preview(value)} : surrogate isolé, non encodable en UTF-8"
    return None


def project_key(entry):
    """Contrôle une entrée de `projects_users` et renvoie l'identifiant du projet.

    Args:
        entry: élément de la liste, de n'importe quel type.

    Returns:
        Couple (identifiant entier, `None`), ou (`None`, cause) si un champ gardé manque,
        a un autre type ou porte un surrogate isolé.
    """
    project = entry.get("project") if isinstance(entry, dict) else None
    if not isinstance(project, dict):
        return None, MALFORMED_DETAIL
    well_formed = (
        is_integer(project.get("id"))
        and isinstance(project.get("slug"), str)
        and isinstance(project.get("name"), str)
        and (entry.get("final_mark") is None
             or is_integer(entry.get("final_mark")))
    )
    if not well_formed:
        return None, MALFORMED_DETAIL
    problem = surrogate_problem(project, ("slug", "name"))
    return (None, problem) if problem else (project["id"], None)


def achievement_key(entry):
    """Contrôle un achievement et renvoie son identifiant.

    Args:
        entry: élément de la liste, de n'importe quel type.

    Returns:
        Couple (identifiant entier, `None`), ou (`None`, cause) si un champ gardé manque,
        a un autre type ou porte un surrogate isolé.
    """
    if not isinstance(entry, dict):
        return None, MALFORMED_DETAIL
    well_formed = (
        is_integer(entry.get("id"))
        and isinstance(entry.get("name"), str)
        and (entry.get("description") is None
             or isinstance(entry.get("description"), str))
    )
    if not well_formed:
        return None, MALFORMED_DETAIL
    problem = surrogate_problem(entry, ("name", "description"))
    return (None, problem) if problem else (entry["id"], None)


def select(entries, path, noun, identify):
    """Garde une fois chaque entrée bien formée, dans l'ordre reçu.

    Args:
        entries: liste reçue de l'API.
        path: chemin d'API, texte, pour les anomalies.
        noun: `project` ou `achievement`, suffixe de la nature d'anomalie.
        identify: fonction entrée vers couple (identifiant ou `None`, cause ou `None`).

    Returns:
        Couple (entrées gardées, liste de `model.Anomaly` des écartées).
    """
    kept, first_line, anomalies = [], {}, []
    for line, entry in enumerate(entries, 1):
        key, detail = identify(entry)
        if key is None:
            anomalies.append(model.Anomaly(path, line, f"malformed_{noun}", detail))
        elif key in first_line:
            detail = f"identifiant {key} déjà lu à l'entrée {first_line[key]}"
            anomalies.append(model.Anomaly(path, line, f"duplicate_{noun}", detail))
        else:
            first_line[key] = line
            kept.append(entry)
    return kept, anomalies


def project_record(entry):
    """Réduit une entrée de `projects_users` déjà contrôlée à `PROJECT_KEYS`.

    Args:
        entry: dict accepté par `project_key`.

    Returns:
        Le dict `id`, `slug`, `name`, `final_mark`.
    """
    project = entry["project"]
    return {
        "id": project["id"],
        "slug": project["slug"],
        "name": project["name"],
        "final_mark": entry.get("final_mark"),
    }


def achievement_record(entry, obtained):
    """Réduit un achievement déjà contrôlé à `ITEM_KEYS` (A23).

    Args:
        entry: dict de l'achievement.
        obtained: booléen, présent dans les achievements de `/v2/me`.

    Returns:
        Le dict, `obtained` statué `observed`, date et titre à `None`.
    """
    return {
        "id": entry["id"],
        "name": entry["name"],
        "description": entry.get("description"),
        "obtained": model.observed(obtained, (SOURCE,)),
        "obtained_on": None,
        "title": None,
    }


def read_level(cursus_users):
    """Lit le niveau du cursus 21 dans `cursus_users`.

    Args:
        cursus_users: liste reçue de `/v2/me`.

    Returns:
        `StatedValue` observée, ou `unmeasurable` (cursus absent, niveau invalide).
    """
    entry = next(
        (
            entry
            for entry in cursus_users
            if isinstance(entry, dict) and entry.get("cursus_id") == CURSUS_ID
        ),
        None,
    )
    if entry is None:
        return model.unmeasurable(f"cursus {CURSUS_ID} absent de {ME_PATH}", "cursus_absent")
    level = entry.get("level")
    if is_number(level) and level >= 0:
        return model.observed(level, (SOURCE,))
    return model.unmeasurable(
        f"niveau du cursus {CURSUS_ID} invalide ({preview(level)}) : nombre fini positif "
        "ou nul attendu",
        "level_invalid",
    )


def me_problem(me):
    """Contrôle la forme de `/v2/me`.

    Args:
        me: JSON reçu.

    Returns:
        `None` si les trois listes lues sont présentes, sinon la cause.
    """
    if not isinstance(me, dict):
        return f"{ME_PATH} : {type(me).__name__} reçu, objet JSON attendu"
    if not me:
        return f"{ME_PATH} : objet JSON vide"
    for name in ME_LISTS:
        if not isinstance(me.get(name), list):
            return f"{ME_PATH} : champ {name} absent ou autre qu'une liste"
    return None


def build_result(me, catalogue):
    """Tire de `/v2/me` et de la liste complète le résultat `ok`, en liste blanche.

    Args:
        me: dict de `/v2/me` déjà contrôlé par `me_problem`.
        catalogue: `Fetch` de `/v2/achievements`.

    Returns:
        `Api42Result` `ok` ; sans liste complète, `complete` est `unmeasurable` (L17).
    """
    projects, anomalies = select(me["projects_users"], ME_PATH, "project", project_key)
    obtained, found = select(me["achievements"], ME_PATH, "achievement", achievement_key)
    anomalies += found
    read = len(me["projects_users"]) + len(me["achievements"])
    listed = []
    if catalogue.error is None:
        listed, found = select(
            catalogue.data,
            ACHIEVEMENTS_PATH,
            "achievement",
            achievement_key,
        )
        anomalies += found
        read += len(catalogue.data)
        complete = model.observed(True, (SOURCE,))
    else:
        LOGGER.warning("API 42 : liste complète indisponible : %s", catalogue.error)
        complete = model.unmeasurable(
            f"Liste complète indisponible : {catalogue.error}",
            "full_list_unavailable",
        )
    obtained_ids = {entry["id"] for entry in obtained}
    listed_ids = {entry["id"] for entry in listed}
    entries = listed + [entry for entry in obtained if entry["id"] not in listed_ids]
    return Api42Result(
        status="ok",
        error=None,
        level=read_level(me["cursus_users"]),
        complete=complete,
        projects=tuple(
            project_record(entry)
            for entry in projects
            if entry.get("validated?") is True
        ),
        achievements=tuple(
            achievement_record(entry, entry["id"] in obtained_ids)
            for entry in entries
        ),
        observed_at=date.today().isoformat(),
        anomalies=tuple(anomalies),
        read=read,
        rejected=len(anomalies),
    )
