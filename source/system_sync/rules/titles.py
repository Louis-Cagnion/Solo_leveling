"""Titres et achievements (T8, A7, A8, A17, A18, A19, A23) : fonctions pures, sans source.

Les titres, leurs types et leurs seuils viennent de `rules["titles"]` : chaque type désigne
un évaluateur de `TITLE_TYPES`, et un titre de plus dans la configuration apparaît sans
changer le code. Un titre acquis est un fait `titre` reçu en paramètre (A7), jamais un
fichier lu ici. Aucune fonction publique ne lève : une donnée inutilisable donne une valeur
`unmeasurable`, `insufficient`, `()` ou une entité vide.
"""

import math
import re
from dataclasses import dataclass

from system_sync.model import (
    REASON_CODES,
    Anomaly,
    StatedValue,
    insufficient,
    observed,
    unmeasurable,
)
from system_sync.rules.guard import empty, never_raises
from system_sync.rules.ranks import EVENTS, EVENTS_FILE, NOTIONS

TITLE_METRIC = "titre"
API_SOURCE = "api42"
ACHIEVEMENTS_FILE = "api42:achievements"
# Statuts d'une valeur qui porte une mesure exploitable.
USABLE_STATUSES = ("observed", "estimated")
NO_RANK = "none"
# Mention « (42) » retirée du nom d'un titre (A23), espace qui la précède comprise.
SUFFIX_42 = re.compile(r"\s*\(42\)")
# Phrase française de repli de chaque code de mention d'une entité `achievements`.
NOTICES = {
    "full_list_unavailable": "Liste complète indisponible : seuls les achievements obtenus "
    "sont affichés.",
    "no_achievements": "Aucun achievement à afficher.",
}


@dataclass(frozen=True)
class _Inputs:
    """Données communes aux évaluateurs de titre.

    Args:
        level: valeur statuée du niveau 42, ou toute autre valeur reçue.
        card_ranks: dict nom de carte vers valeur statuée du rang, ou toute autre valeur.
        order: noms des rangs, du plus bas au plus haut (ordre de `rules["ranks"]`).
    """

    level: object
    card_ranks: object
    order: list


def _progress(current, target):
    """Progression `{current, target, percent}` ; le pourcentage est plafonné à 100.

    Args:
        current: nombre courant, fini et non négatif.
        target: nombre cible, strictement positif.

    Returns:
        Le dictionnaire de progression, `percent` arrondi à 2 décimales.
    """
    if not target > 0:
        raise ValueError(f"cible {target!r} : un nombre strictement positif est attendu")
    percent = round(min(current, target) / target * 100, 2)
    return {"current": current, "target": target, "percent": percent}


def _level_problem(level):
    """Renvoie la valeur statuée `unmeasurable` d'un niveau inutilisable, ou `None`."""
    if not isinstance(level, StatedValue):
        reason = f"niveau 42 reçu {level!r} : aucune valeur statuée, API 42 indisponible"
        return unmeasurable(reason, "api_unavailable")
    if level.status not in USABLE_STATUSES:
        code = level.reason_code if level.reason_code in REASON_CODES else "api_unavailable"
        return unmeasurable(level.reason or f"niveau 42 {level.status}", code)
    value = level.value
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value < 0
    ):
        reason = f"niveau 42 {value!r} invalide : un nombre fini non négatif est attendu"
        return unmeasurable(reason, "level_invalid")
    return None


def _level_title(spec, inputs):
    """Évalue un titre `level_at_least` : niveau 42 au moins égal à `spec["value"]`.

    Args:
        spec: table de la configuration, avec `value` (seuil numérique).
        inputs: données communes des évaluateurs.

    Returns:
        Le couple (valeur statuée `obtained`, progression ou `None` sans mesure).
    """
    problem = _level_problem(inputs.level)
    if problem is not None:
        return problem, None
    level, target = inputs.level.value, spec["value"]
    sources = inputs.level.sources or (API_SOURCE,)
    return observed(level >= target, sources), _progress(level, target)


def _standing(state, order, required):
    """Dit si le rang d'une carte atteint `required` : True, False, ou `None` sans mesure.

    Args:
        state: valeur statuée du rang d'une carte, ou toute autre valeur reçue.
        order: noms des rangs, du plus bas au plus haut.
        required: position du rang requis dans `order`.

    Returns:
        `None` si le rang est inutilisable, sinon un booléen ; `none` ne l'atteint jamais.
    """
    if (
        not isinstance(state, StatedValue)
        or state.status not in USABLE_STATUSES
    ):
        return None
    if state.value == NO_RANK:
        return False
    if state.value not in order:
        return None
    return order.index(state.value) >= required


def _rank_title(spec, inputs):
    """Évalue un titre `rank_on_all_cards` : toutes les cartes au moins au rang `spec["rank"]`.

    Args:
        spec: table de la configuration, avec `rank` (nom d'un rang de `rules["ranks"]`).
        inputs: données communes des évaluateurs.

    Returns:
        Le couple (valeur statuée `obtained`, progression ou `None` sans mesure) ;
        `insufficient` sans carte ou si le rang d'une carte est inutilisable.
    """
    cards = inputs.card_ranks
    if not isinstance(cards, dict) or not cards:
        reason = f"aucune carte reçue ({cards!r}) : le titre ne peut pas être jugé"
        return insufficient(reason, "no_cards"), None
    required = inputs.order.index(spec["rank"])
    standings = {name: _standing(state, inputs.order, required) for name, state in cards.items()}
    lacking = [f"{name!r} ({cards[name]!r})" for name, found in standings.items() if found is None]
    if lacking:
        reason = f"rang inutilisable pour les cartes : {', '.join(lacking)}"
        return insufficient(reason, "card_rank_missing"), None
    sources = {source for state in cards.values() for source in state.sources}
    reached = sum(standings.values())
    obtained = observed(reached == len(cards), tuple(sorted(sources)) or (NOTIONS,))
    return obtained, _progress(reached, len(cards))


# Un évaluateur par type de titre : un type de plus se déclare ici, sans `if` par titre.
TITLE_TYPES = {
    "level_at_least": _level_title,
    "rank_on_all_cards": _rank_title,
}


def _title_facts(facts):
    """Garde les faits `titre` (dict) d'une liste ou d'un tuple, sinon renvoie `[]`."""
    if not isinstance(facts, (list, tuple)):
        return []
    return [
        fact
        for fact in facts
        if isinstance(fact, dict)
        if fact.get("metric") == TITLE_METRIC
    ]


def _usable_id(value):
    """Dit si la valeur d'un fait `titre` est un identifiant : texte non vide."""
    return isinstance(value, str) and bool(value.strip())


def _acquired(facts, configured):
    """Renvoie les identifiants de titres configurés que des faits `titre` déclarent acquis."""
    return {
        fact["value"]
        for fact in _title_facts(facts)
        if _usable_id(fact.get("value"))
        if fact["value"] in configured
    }


def _entry(title_id, spec, inputs, acquired):
    """Assemble l'élément de `school_titles` d'un titre configuré.

    Args:
        title_id: clé du titre dans `rules["titles"]`.
        spec: table du titre, avec un `type` de `TITLE_TYPES`.
        inputs: données communes des évaluateurs.
        acquired: identifiants de titres acquis d'après les faits `titre`.

    Returns:
        Le dictionnaire `id`, `type`, `obtained`, `progress` (et `name` si configuré) ;
        un titre acquis est observé vrai avec la source `events` (A7).
    """
    obtained, progress = TITLE_TYPES[spec["type"]](spec, inputs)
    if title_id in acquired:
        obtained = observed(True, (EVENTS,))
    entry = {"id": title_id, "type": spec["type"], "obtained": obtained, "progress": progress}
    if isinstance(spec.get("name"), str):
        entry["name"] = SUFFIX_42.sub("", spec["name"])
    return entry


@never_raises(empty)
def school_titles(level, card_ranks, facts, rules):
    """Évalue les titres de `rules["titles"]` hors `school_achievements`, dans leur ordre.

    Args:
        level: valeur statuée du niveau 42 (`Api42Result.level`) ou `None`.
        card_ranks: dict nom de carte vers valeur statuée de `ranks.rank_card`, ou `None`.
        facts: faits de `read_events(...).facts`, ou `None`.
        rules: dictionnaire de `config.load_rules`.

    Returns:
        Un tuple de dicts `id`, `type`, `obtained`, `progress` ; `()` si `rules` est inutilisable.
    """
    configured = rules["titles"]
    inputs = _Inputs(level, card_ranks, list(rules["ranks"]))
    acquired = _acquired(facts, configured)
    return tuple(
        _entry(title_id, spec, inputs, acquired)
        for title_id, spec in configured.items()
        if isinstance(spec, dict)
        if spec.get("type") in TITLE_TYPES
    )


def _fact_anomaly(fact, configured):
    """Renvoie l'anomalie d'un fait `titre`, ou `None` s'il désigne un titre configuré."""
    value, line = fact.get("value"), fact.get("line")
    if not _usable_id(value):
        detail = f"fait titre de valeur {value!r} : un identifiant non vide est attendu"
        return Anomaly(EVENTS_FILE, line, "unusable_title_fact", detail)
    if value not in configured:
        detail = f"fait titre {value!r} : identifiant absent de rules[titles]"
        return Anomaly(EVENTS_FILE, line, "unknown_title", detail)
    return None


@never_raises(empty)
def title_anomalies(facts, rules):
    """Signale les faits `titre` dont l'identifiant est inconnu ou la valeur inutilisable.

    Args:
        facts: faits de `read_events(...).facts`, ou `None`.
        rules: dictionnaire de `config.load_rules`.

    Returns:
        Un tuple d'`Anomaly` (`unknown_title`, `unusable_title_fact`), dans l'ordre des faits.
    """
    configured = rules["titles"]
    found = [_fact_anomaly(fact, configured) for fact in _title_facts(facts)]
    return tuple(anomaly for anomaly in found if anomaly is not None)


def _id_problem(item):
    """Renvoie la cause pour laquelle un achievement est inutilisable, ou `None`."""
    if not isinstance(item, dict):
        return f"élément {item!r} : un dictionnaire est attendu"
    ident, name = item.get("id"), item.get("name")
    if isinstance(ident, bool) or not isinstance(ident, (int, str)) or ident == "":
        return f"achievement sans identifiant utilisable (id reçu {ident!r})"
    if not isinstance(name, str) or not name.strip():
        return f"achievement {ident!r} sans nom utilisable (name reçu {name!r})"
    return None


def _scan(achievements):
    """Classe chaque achievement reçu : conservé, mal formé ou en doublon.

    Args:
        achievements: liste de dicts de `Api42Result.achievements`, ou toute autre valeur.

    Returns:
        Une liste de (position à partir de 1, élément, nature, cause) ; la nature est `None`
        pour un élément conservé, sinon `malformed_achievement` ou `duplicate_achievement`.
    """
    if not isinstance(achievements, (list, tuple)):
        return []
    seen, scanned = set(), []
    for position, item in enumerate(achievements, 1):
        problem = _id_problem(item)
        if problem is not None:
            scanned.append((position, item, "malformed_achievement", problem))
        elif item["id"] in seen:
            cause = f"achievement {item['id']!r} déjà lu plus haut"
            scanned.append((position, item, "duplicate_achievement", cause))
        else:
            seen.add(item["id"])
            scanned.append((position, item, None, None))
    return scanned


def _obtained_state(item):
    """Renvoie `obtained` d'un achievement, `unmeasurable` s'il n'est pas une valeur statuée."""
    state = item.get("obtained")
    if isinstance(state, StatedValue):
        return state
    reason = f"achievement {item['id']!r} : obtained reçu {state!r}, valeur statuée attendue"
    return unmeasurable(reason, "api_unavailable")


def _item(item):
    """Renvoie un achievement aux six clés de l'entité (A23), `obtained` toujours statué."""
    return {
        "id": item["id"],
        "name": item["name"],
        "description": item.get("description"),
        "obtained": _obtained_state(item),
        "obtained_on": item.get("obtained_on"),
        "title": item.get("title"),
    }


def _usable_complete(complete):
    """Renvoie `complete` s'il est un booléen statué ou `unmeasurable`, sinon son repli."""
    if isinstance(complete, StatedValue):
        if complete.status == "unmeasurable" or isinstance(complete.value, bool):
            return complete
    reason = f"liste complète : valeur reçue {complete!r} inutilisable"
    return unmeasurable(reason, "full_list_unavailable")


def _notice_code(complete, items):
    """Renvoie le code de la mention de l'entité : liste complète absente, ou rien à lister."""
    if complete.status == "unmeasurable":
        return "full_list_unavailable"
    return None if items else "no_achievements"


def _empty_entity(error):
    """Entité `achievements` de repli : liste complète indisponible, aucun élément."""
    return _build_entity((), _usable_complete(None))


def _build_entity(items, complete):
    """Assemble les quatre clés de l'entité `achievements`.

    Args:
        items: tuple d'achievements aux six clés.
        complete: valeur statuée de la liste complète, déjà validée.

    Returns:
        Le dictionnaire `complete`, `items`, `notice_code`, `notice`.
    """
    code = _notice_code(complete, items)
    return {
        "complete": complete,
        "items": items,
        "notice_code": code,
        "notice": NOTICES.get(code),
    }


@never_raises(_empty_entity)
def achievements_entity(achievements, complete):
    """Construit l'entité `achievements` (A23) sans élément mal formé ni doublon d'`id`.

    Args:
        achievements: liste de dicts de `Api42Result.achievements`, ou `None`.
        complete: valeur statuée de `Api42Result.complete`.

    Returns:
        Le dictionnaire `complete`, `items` (tuple), `notice_code` et `notice` (français).
    """
    items = tuple(_item(item) for _, item, kind, _ in _scan(achievements) if kind is None)
    return _build_entity(items, _usable_complete(complete))


def _unlisted(item, catalogue_ids):
    """Dit si un achievement obtenu est absent des identifiants de la liste complète."""
    state = _obtained_state(item)
    return state.status == "observed" and state.value is True and item["id"] not in catalogue_ids


@never_raises(empty)
def achievement_anomalies(achievements, complete, catalogue_ids=None):
    """Signale les achievements mal formés, en doublon ou obtenus mais hors de la liste.

    Args:
        achievements: liste de dicts de `Api42Result.achievements`, ou `None`.
        complete: valeur statuée de `Api42Result.complete`.
        catalogue_ids: identifiants de la liste complète (ensemble ou liste), ou `None`.

    Returns:
        Un tuple d'`Anomaly` dont `line` est la position à partir de 1 dans `achievements`.
    """
    state = _usable_complete(complete)
    compare = (
        state.status == "observed"
        and isinstance(catalogue_ids, (set, frozenset, list, tuple))
    )
    found = []
    for position, item, kind, cause in _scan(achievements):
        if kind is None and compare and _unlisted(item, catalogue_ids):
            kind = "unlisted_achievement"
            cause = f"achievement obtenu {item['id']!r} absent de la liste complète"
        if kind is not None:
            found.append(Anomaly(ACHIEVEMENTS_FILE, position, kind, cause))
    return tuple(found)
