"""Schéma de `data/state.js`, validateur et écriture atomique (T2, amendements A17 à A27).

Le schéma est une structure de données (`SCHEMA`) parcourue par un seul validateur, sans
bibliothèque. Un objet y est fermé : toute clé absente du schéma est refusée, ce qui
tient lieu de liste blanche (aucun champ personnel de l'API 42, aucune « Solidité »).
"""

import contextlib
import json
import math
import os
import re
import tempfile
from datetime import datetime

from . import model

PREFIX = "window.SYSTEM_STATE = "
RANKS = ("E", "D", "C", "B", "A", "S", "Nation", "none")
RELATION_STATUSES = ("theorique", "reconnue", "demontree")
PROJECT_SETTINGS = ("perso", "pro")
PROJECT_STATUSES = ("en cours", "livré", "abandonné")
TITLE_SCOPES = ("42", "Système")
SCHEMA_VERSIONS = (1,)

# Forme textuelle puis format de lecture de chaque famille de date.
TIME_FORMATS = {
    "date": (r"\d{4}-\d\d-\d\d", "%Y-%m-%d"),
    "datetime": (r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", "%Y-%m-%dT%H:%M:%SZ"),
}


class OutputError(Exception):
    """Écriture refusée ; une ligne `chemin : cause` par problème, ou chemin et `strerror`."""


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_time(value, kind):
    """Dit si `value` est une chaîne de la famille `kind` de `TIME_FORMATS` et réelle."""
    shape, pattern = TIME_FORMATS[kind]
    if not isinstance(value, str) or not re.fullmatch(shape, value):
        return False
    try:
        datetime.strptime(value, pattern)
    except ValueError:
        return False
    return True


# Types feuilles : nom -> (prédicat, description de la valeur attendue).
LEAVES = {
    "text": (lambda value: isinstance(value, str), "texte"),
    "bool": (lambda value: isinstance(value, bool), "booléen"),
    "null": (lambda value: value is None, "null"),
    "count": (lambda value: _is_int(value) and value >= 0, "entier positif ou nul"),
    "nonneg": (
        lambda value: _is_number(value) and math.isfinite(value) and value >= 0,
        "nombre fini positif ou nul",
    ),
    "json": (
        lambda value: not isinstance(value, float) or math.isfinite(value),
        "valeur JSON finie",
    ),
    "date": (lambda value: _is_time(value, "date"), "date AAAA-MM-JJ"),
    "datetime": (
        lambda value: _is_time(value, "datetime"),
        "date AAAA-MM-JJThh:mm:ssZ",
    ),
}


def _obj(**fields):
    return ("object", fields)


def _list(item, unique=None):
    return ("list", item, unique)


def _map(item):
    return ("map", item)


def _enum(*values):
    return ("enum", values)


def _nullable(node):
    return ("nullable", node)


def _stated(value_node="json"):
    return ("stated", value_node)


_CERTIFICATION = _obj(
    code="text",
    detail=_nullable("text"),
    notions=_list("text"),
    conditions="null",
    obtained=_stated("bool"),
    obtained_on=_nullable("date"),
    accessible=_stated("bool"),
)
_NEXT_RANK = _obj(
    rank="text",
    condition="text",
    progress=_stated(),
    total=_nullable("count"),
    missing=_list(_obj(id="text", state="text")),
)
_SOURCE = _obj(
    name="text",
    status="text",
    lines_read="count",
    lines_rejected="count",
    observed_at=_nullable("date"),
)
_CARD = _obj(
    id="text",
    name="text",
    rank=_stated(_enum(*RANKS)),
    next_rank=_nullable(_NEXT_RANK),
    tiers=_list(_obj(name="text", notions=_list("text"))),
    certifications=_list(_CERTIFICATION),
)
_NOTION = _obj(
    label="text",
    section=_nullable("text"),
    state=_stated("text"),
    goal=_nullable("text"),
    card=_nullable("text"),
    tier=_nullable("text"),
    last_practice=_nullable("text"),
)
_RELATION = _obj(
    source="text",
    target="text",
    kind="text",
    status=_enum(*RELATION_STATUSES),
    limit=_nullable("text"),
    proof=_nullable("text"),
)
_PROJECT = _obj(
    id="text",
    setting=_enum(*PROJECT_SETTINGS),
    name="text",
    status=_enum(*PROJECT_STATUSES),
    date="text",
    equivalent_42="text",
    ia_factor=_stated("nonneg"),
    xp=_stated("nonneg"),
)
_TITLE = _obj(
    id="text",
    name="text",
    scope=_enum(*TITLE_SCOPES),
    condition="text",
    obtained=_stated("bool"),
    progress=_stated(),
    target=_nullable("count"),
)
_ACHIEVEMENT = _obj(
    id="text",
    name="text",
    description="text",
    obtained=_stated("bool"),
    obtained_on=_nullable("date"),
    title=_nullable("text"),
)

# Schéma fermé des 14 entités de l'état (A30).
SCHEMA = _obj(
    meta=_obj(
        schema_version=_enum(*SCHEMA_VERSIONS),
        generated_at="datetime",
        rules_fingerprint="text",
    ),
    sources=_list(_SOURCE, unique="name"),
    level42=_obj(
        level=_stated("nonneg"),
        xp=_stated("nonneg"),
        target_xp=_stated("nonneg"),
        projects=_list(_obj(id="text", name="text", base_xp=_stated("nonneg"))),
    ),
    system=_obj(
        xp=_stated("nonneg"),
        level=_stated("nonneg"),
        origins=_list(_obj(origin="text", xp=_stated("nonneg"))),
        calibration=_stated(),
    ),
    trajectory=_list(_obj(date="date", level42="nonneg", system_level="nonneg")),
    cards=_list(_CARD, unique="id"),
    notions=_map(_NOTION),
    relations=_list(_RELATION),
    projects=_list(_PROJECT),
    titles=_list(_TITLE),
    anomalies=_list(_obj(file="text", line="count", kind="text", detail="text")),
    rules=_obj(
        proof_order=_list("text"),
        excluded_states=_list("text"),
        rank_d_threshold="text",
        cert_threshold="text",
        target_level="nonneg",
    ),
    achievements=_obj(
        complete=_stated("bool"),
        items=_list(_ACHIEVEMENT, unique="id"),
    ),
    names=_obj(en=_map("text")),
)


def _child(path, key):
    return f"{path}.{key}" if path else str(key)


def _type_problem(path, value, expected):
    cause = f"type {type(value).__name__}, attendu {expected}"
    return (path or "$", cause)


def _check_leaf(path, value, node, problems):
    predicate, expected = LEAVES[node]
    if not predicate(value):
        cause = f"valeur {value!r} de type {type(value).__name__}, attendu {expected}"
        problems.append((path or "$", cause))


def _check_object(path, value, node, problems):
    fields = node[1]
    if not isinstance(value, dict):
        problems.append(_type_problem(path, value, "objet"))
        return
    for key, sub_node in fields.items():
        if key in value:
            _check(_child(path, key), value[key], sub_node, problems)
        else:
            problems.append((_child(path, key), "champ manquant"))
    for key in value:
        if key not in fields:
            problems.append((_child(path, key), f"clé inconnue {key!r}"))


def _check_list(path, value, node, problems):
    _, item_node, unique = node
    if not isinstance(value, list):
        problems.append(_type_problem(path, value, "liste"))
        return
    seen = set()
    for index, item in enumerate(value):
        _check(f"{path}[{index}]", item, item_node, problems)
        key = item.get(unique) if unique and isinstance(item, dict) else None
        if isinstance(key, str) and key in seen:
            problems.append((f"{path}[{index}].{unique}", f"doublon {key!r}"))
        seen.add(key)


def _check_map(path, value, node, problems):
    if not isinstance(value, dict):
        problems.append(_type_problem(path, value, "objet"))
        return
    for key, item in value.items():
        if isinstance(key, str):
            _check(_child(path, key), item, node[1], problems)
        else:
            problems.append((path, f"clé {key!r} qui n'est pas du texte"))


def _check_enum(path, value, node, problems):
    allowed = node[1]
    if not any(type(value) is type(item) and value == item for item in allowed):
        problems.append((path, f"valeur {value!r} hors de {allowed}"))


def _check_nullable(path, value, node, problems):
    if value is not None:
        _check(path, value, node[1], problems)


def _check_stated(path, value, node, problems):
    """Vérifie les cinq clés d'une valeur statuée puis ses invariants (`model`)."""
    fields = {
        "value": _nullable(node[1]),
        "status": "text",
        "sources": _list("text"),
        "reason": _nullable("text"),
        "reason_code": _nullable("text"),
    }
    before = len(problems)
    _check_object(path, value, _obj(**fields), problems)
    if len(problems) > before:
        return
    for field, cause in model.stated_problems(
        value["value"],
        value["status"],
        value["sources"],
        value["reason"],
        value["reason_code"],
    ):
        problems.append((_child(path, field), cause))


# Vérificateur de chaque genre de nœud du schéma.
CHECKERS = {
    "object": _check_object,
    "list": _check_list,
    "map": _check_map,
    "enum": _check_enum,
    "nullable": _check_nullable,
    "stated": _check_stated,
}


def _check(path, value, node, problems):
    if isinstance(node, str):
        _check_leaf(path, value, node, problems)
    else:
        CHECKERS[node[0]](path, value, node, problems)


def validate(state):
    """Valide un état contre le schéma fermé, sans lever.

    Args:
        state: objet JSON de l'état complet (14 entités), de n'importe quel type.

    Returns:
        Liste de couples (chemin pointé du champ fautif, cause avec la valeur reçue),
        `$` pour la racine ; liste vide si l'état est valide.
    """
    problems = []
    _check("", state, SCHEMA, problems)
    return problems


def _render(state, path):
    """Sérialise l'état en octets UTF-8, ou lève `OutputError` nommant `path`."""
    try:
        body = json.dumps(state, indent=2, ensure_ascii=False, allow_nan=False)
        return f"{PREFIX}{body};\n".encode("utf-8")
    except (TypeError, ValueError) as error:
        raise OutputError(f"{path} : sérialisation impossible : {error}") from error


def write(state, path):
    """Écrit `window.SYSTEM_STATE = {...};` de façon atomique, après validation.

    Le fichier est préparé dans un temporaire voisin puis installé par `os.replace` :
    sur toute erreur, l'ancien fichier reste intact et aucun temporaire ne subsiste.

    Args:
        state: objet JSON de l'état complet, valide selon `SCHEMA`.
        path: chemin du fichier à produire (chaîne ou `Path`) ; son dossier est créé.

    Raises:
        OutputError: état invalide (un problème par ligne) ou échec du système de
            fichiers (chemin et `strerror`).
    """
    problems = validate(state)
    if problems:
        raise OutputError("\n".join(f"{where} : {cause}" for where, cause in problems))
    path = os.fspath(path)
    data = _render(state, path)
    directory = os.path.dirname(path) or "."
    temporary = None
    try:
        os.makedirs(directory, exist_ok=True)
        descriptor, temporary = tempfile.mkstemp(dir=directory, suffix=".tmp")
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
        os.replace(temporary, path)
    except OSError as error:
        raise OutputError(f"{path} : {error.strerror or error}") from error
    finally:
        if temporary is not None:
            with contextlib.suppress(FileNotFoundError):
                os.unlink(temporary)
