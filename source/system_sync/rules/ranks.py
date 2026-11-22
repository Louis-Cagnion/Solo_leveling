"""Rangs des cartes (T6, A2, A8, A9, A17 à A21) : fonctions pures, sans lecture de source.

Les rangs et leurs conditions viennent de `rules["ranks"]` : l'ordre des tables est l'ordre
des rangs, et chaque table porte un `type` qui désigne une règle de `_EVALUATORS` (rang
atteint) et de `_PROGRESS` (rang suivant). Aucune fonction publique ne lève : une carte, des
données ou des règles inutilisables donnent une valeur `unmeasurable`, `None` ou `()`.
"""

import re
from dataclasses import dataclass
from typing import NamedTuple

from system_sync.model import Anomaly, estimated, insufficient, observed, unmeasurable
from system_sync.rules.guard import empty, never_raises

EVENTS = "events"
NOTIONS = "notions"
EVENTS_FILE = "evenements.csv"
NOTIONS_FILE = "notions.md"
LEVEL_METRIC = "niveau"
CERT_METRIC = "certification"
NOT_OBTAINED = "non obtenue"
CARDS_LABEL = "cartes"
# Cellules « Certifications » sans certification, comparées sans casse ni espaces de bord.
NO_CERTIFICATION = frozenset({"", "aucune", "\N{EM DASH}"})
# Un code de certification : mot de majuscules, chiffres et tirets, qui débute par une lettre.
CODE_PATTERN = re.compile(r"(?<!\w)[A-Z][A-Z0-9-]*(?!\w)")
# Champs d'une carte de `read_cards(...).records` et type attendu.
CARD_FIELDS = {
    "name": str,
    "tiers": dict,
    "ids": (list, tuple),
    "certifications": dict,
    "has_certifications": bool,
}


class _Unusable(ValueError):
    """Carte, règle ou donnée inutilisable ; le message nomme l'élément et la valeur."""


class _Verdict(NamedTuple):
    """Résultat de l'évaluation d'une condition de rang.

    Args:
        met: True si la condition est remplie.
        status: `observed` ou `estimated`.
        sources: noms des sources qui comptent.
        reason: phrase française pour un statut `estimated`, sinon `None`.
        code: code de raison de `REASON_CODES`, sinon `None`.
    """

    met: bool
    status: str
    sources: tuple
    reason: object
    code: object


@dataclass(frozen=True)
class _Rules:
    """Règles lues et validées de `rules.toml`.

    Args:
        ranks: tables `[ranks.*]`, dans l'ordre des rangs.
        order: états des notions, du plus bas au plus haut.
        excluded: états ignorés des comparaisons « au moins X » (A8).
        ready: état exigé pour qu'une certification soit accessible, ou `None`.
        levels: valeurs de `niveau` dans l'ordre des rangs (clé `level` des tables).
    """

    ranks: dict
    order: list
    excluded: frozenset
    ready: object
    levels: list


@dataclass(frozen=True)
class _Context:
    """Données d'une carte prêtes à l'évaluation.

    Args:
        card: enregistrement de carte validé.
        rules: règles validées.
        states: état courant de chaque identifiant de notion.
        facts: faits (dict) reçus.
        level_index: plus haut niveau valide d'un fait de la carte, ou -1.
        obtained: faits `certification` regroupés par code.
    """

    card: dict
    rules: _Rules
    states: dict
    facts: list
    level_index: int
    obtained: dict

    def position(self, state):
        """Renvoie le rang d'un état dans `states.order` ; refuse un état inconnu."""
        if state not in self.rules.order:
            raise _Unusable(f"état {state!r} absent de states.order")
        return self.rules.order.index(state)

    def at_least(self, note_id, state):
        """Dit si la notion est au moins à `state`, un état exclu ne comptant jamais."""
        found = self.states.get(note_id)
        if found not in self.rules.order or found in self.rules.excluded:
            return False
        return self.position(found) >= self.position(state)

    def followed(self, note_id):
        """Dit si la notion est suivie : un état connu, ni exclu ni le plus bas."""
        found = self.states.get(note_id)
        return (
            found in self.rules.order
            and found not in self.rules.excluded
            and found != self.rules.order[0]
        )

    def tier(self, key):
        """Renvoie les identifiants distincts d'un palier (clé en minuscules des règles)."""
        return list(dict.fromkeys(self.card["tiers"].get(key.capitalize(), ())))

    def count_at_least(self, ids, state):
        """Compte les notions de `ids` au moins à `state`."""
        return sum(self.at_least(note_id, state) for note_id in ids)

    def items(self, ids):
        """Renvoie `{id, state}` pour chaque identifiant, `states.order[0]` si absent."""
        lowest = self.rules.order[0]
        return [{"id": note_id, "state": self.states.get(note_id, lowest)} for note_id in ids]


def _records(items):
    """Garde les dictionnaires d'une liste ou d'un tuple, sinon renvoie une liste vide."""
    if not isinstance(items, (list, tuple)):
        return []
    return [item for item in items if isinstance(item, dict)]


def _read_rules(rules):
    """Valide `rules` et en tire les tables de rang, les états et les niveaux.

    Args:
        rules: dictionnaire de `config.load_rules`, de n'importe quel type.

    Returns:
        Les `_Rules` ; lève `_Unusable` si une partie manque ou si un `type` est inconnu.
    """
    if not isinstance(rules, dict):
        raise _Unusable(f"règles de type {type(rules).__name__}, dict attendu")
    ranks, states = rules.get("ranks"), rules.get("states")
    if (
        not isinstance(ranks, dict)
        or not ranks
    ):
        raise _Unusable(f"[ranks] absent ou vide : {ranks!r}")
    if (
        not isinstance(states, dict)
        or not isinstance(states.get("order"), list)
    ):
        raise _Unusable(f"[states] sans liste `order` : {states!r}")
    for name, rule in ranks.items():
        kind = rule.get("type") if isinstance(rule, dict) else None
        if kind not in _EVALUATORS:
            raise _Unusable(f"[ranks.{name}] : type {kind!r} inconnu")
    return _Rules(
        ranks=ranks,
        order=states["order"],
        excluded=frozenset(states.get("excluded", ())),
        ready=states.get("cert_ready_at_least"),
        levels=[rule["level"] for rule in ranks.values() if "level" in rule],
    )


def _read_card(card):
    """Valide la forme d'une carte et la renvoie ; lève `_Unusable` sinon."""
    if not isinstance(card, dict):
        raise _Unusable(f"carte de type {type(card).__name__}, dict attendu")
    for key, kind in CARD_FIELDS.items():
        if not isinstance(card.get(key), kind):
            found = card.get(key)
            raise _Unusable(f"carte {card.get('name')!r} : champ {key!r} reçu {found!r}")
    return card


def _level_index(card, facts, levels):
    """Renvoie le plus haut niveau valide d'un fait `niveau` de la carte, ou -1."""
    found = [
        levels.index(fact["value"])
        for fact in facts
        if fact.get("metric") == LEVEL_METRIC
        if fact.get("domain") == card["name"]
        if fact.get("value") in levels
    ]
    return max(found, default=-1)


def _group_certifications(facts):
    """Regroupe les faits `certification` par code, quel que soit leur domaine (A2)."""
    grouped = {}
    for fact in facts:
        if fact.get("metric") == CERT_METRIC:
            grouped.setdefault(fact.get("value"), []).append(fact)
    return grouped


def _build(card, notions, facts, rules):
    """Prépare le contexte d'évaluation ; lève `_Unusable` si carte ou règles sont fautives."""
    parsed = _read_rules(rules)
    card = _read_card(card)
    records = _records(facts)
    return _Context(
        card=card,
        rules=parsed,
        states={note.get("id"): note.get("state") for note in _records(notions)},
        facts=records,
        level_index=_level_index(card, records, parsed.levels),
        obtained=_group_certifications(records),
    )


def _card_codes(card):
    """Renvoie les codes cités par les cellules `certifications` de la carte, sans doublon."""
    cells = card.get("certifications")
    if not isinstance(cells, dict):
        return []
    found = [code for text in cells.values() for code in CODE_PATTERN.findall(text)]
    return list(dict.fromkeys(found))


def _unreadable_texts(card):
    """Renvoie les cellules `certifications` non vides dont aucun code ne s'extrait."""
    cells = card.get("certifications")
    if not isinstance(cells, dict):
        return []
    return [
        text
        for text in cells.values()
        if text.strip().casefold() not in NO_CERTIFICATION
        if not CODE_PATTERN.search(text)
    ]


def _list_problem(card):
    """Renvoie la raison pour laquelle la liste des certifications est illisible, ou `None`."""
    if not card["has_certifications"]:
        return f"la carte {card['name']!r} n'a pas de colonne « Certifications »"
    texts = _unreadable_texts(card)
    if texts:
        shown = "; ".join(texts)
        return f"carte {card['name']!r} : cellule « Certifications » illisible « {shown} »"
    return None


def _half(count):
    """Renvoie la moitié par excès de `count` (A9)."""
    return (count + 1) // 2


def _whole(count):
    """Renvoie `count` : la part exigée quand toutes les notions comptent."""
    return count


# Part exigée d'un palier : texte de la condition et nombre de notions à atteindre.
SCOPES = {
    "all": ("toutes les notions", _whole),
    "half": ("la moitié des notions", _half),
}


def _eval_any_notion(ctx, rule):
    """Condition `any_notion` : au moins une notion suivie."""
    met = any(ctx.followed(note_id) for note_id in ctx.card["ids"])
    return _Verdict(met, "observed", (NOTIONS,), None, None)


def _eval_fact_level(ctx, rule):
    """Condition `fact_level` : fait `niveau`, ou repli sur un palier de notions."""
    if ctx.level_index >= ctx.rules.levels.index(rule["level"]):
        return _Verdict(True, "observed", (EVENTS,), None, None)
    if "fallback_tier" not in rule:
        return _Verdict(False, "observed", (EVENTS,), None, None)
    ids = ctx.tier(rule["fallback_tier"])
    met = (
        bool(ids)
        and ctx.count_at_least(ids, rule["fallback_at_least"]) == len(ids)
    )
    reason = f"palier {rule['fallback_tier']} estimé d'après les notions, sans fait niveau"
    return _Verdict(met, "estimated", (NOTIONS,), reason, "tier_fallback")


def _eval_half_tier(ctx, rule):
    """Condition `half_tier_at_least` : la moitié par excès d'un palier, jamais vide."""
    ids = ctx.tier(rule["tier"])
    half = _half(len(ids))
    met = 0 < half <= ctx.count_at_least(ids, rule["at_least"])
    reason = f"moitié du palier {rule['tier']} estimée d'après les notions"
    return _Verdict(met, "estimated", (EVENTS, NOTIONS), reason, "half_tier_rule")


def _eval_certifications(ctx, rule):
    """Condition `certifications` : colonne lisible et tous les codes obtenus (A2)."""
    missing = [code for code in _card_codes(ctx.card) if code not in ctx.obtained]
    met = _list_problem(ctx.card) is None and not missing
    return _Verdict(met, "observed", (EVENTS,), None, None)


_EVALUATORS = {
    "any_notion": _eval_any_notion,
    "fact_level": _eval_fact_level,
    "half_tier_at_least": _eval_half_tier,
    "certifications": _eval_certifications,
}


def _reached(ctx):
    """Renvoie (position du plus haut rang atteint ou -1, son verdict).

    Args:
        ctx: contexte d'évaluation d'une carte.

    Returns:
        Le couple ; l'évaluation s'arrête à la première condition non remplie.
    """
    found = (-1, None)
    for position, rule in enumerate(ctx.rules.ranks.values()):
        verdict = _EVALUATORS[rule["type"]](ctx, rule)
        if not verdict.met:
            break
        found = (position, verdict)
    return found


def _progress(condition, progress, total, missing):
    """Assemble les quatre champs de `next_rank` qui varient d'un type de condition."""
    return {
        "condition": condition,
        "progress": progress,
        "total": total,
        "missing": missing,
    }


def _tier_progress(ctx, key, state, scope):
    """Progression vers une condition de palier ; palier vide : `insufficient`."""
    text, needed = SCOPES[scope]
    condition = f"{text} du palier {key} au moins à l'état « {state} »"
    ids = ctx.tier(key)
    if not ids:
        reason = f"le palier {key} de la carte est vide"
        return _progress(condition, insufficient(reason, "empty_tier"), 0, [])
    done = [note_id for note_id in ids if ctx.at_least(note_id, state)]
    return _progress(
        condition,
        observed(len(done), (NOTIONS,)),
        needed(len(ids)),
        ctx.items([note_id for note_id in ids if note_id not in done]),
    )


def _progress_any_notion(ctx, rule):
    """Progression vers `any_notion` : notions suivies sur 1, manquantes listées."""
    ids = list(dict.fromkeys(ctx.card["ids"]))
    missing = [note_id for note_id in ids if not ctx.followed(note_id)]
    return _progress(
        "au moins une notion suivie (hors « déclarée »)",
        observed(len(ids) - len(missing), (NOTIONS,)),
        1,
        ctx.items(missing),
    )


def _progress_fact_level(ctx, rule):
    """Progression vers `fact_level` : palier de repli, sinon fait `niveau` à attendre."""
    if "fallback_tier" in rule:
        return _tier_progress(ctx, rule["fallback_tier"], rule["fallback_at_least"], "all")
    reason = f"aucun fait niveau « {rule['level']} » dans les événements"
    return _progress(
        f"fait niveau « {rule['level']} »",
        insufficient(reason, "level_fact_missing"),
        None,
        [],
    )


def _progress_half_tier(ctx, rule):
    """Progression vers `half_tier_at_least` : la moitié du palier."""
    return _tier_progress(ctx, rule["tier"], rule["at_least"], "half")


def _progress_certifications(ctx, rule):
    """Progression vers `certifications` : codes obtenus sur codes retenus."""
    condition = "toutes les certifications retenues obtenues"
    problem = _list_problem(ctx.card)
    if problem:
        return _progress(
            condition,
            unmeasurable(problem, "certification_list_unreadable"),
            None,
            [],
        )
    codes = _card_codes(ctx.card)
    missing = [code for code in codes if code not in ctx.obtained]
    return _progress(
        condition,
        observed(len(codes) - len(missing), (EVENTS,)),
        len(codes),
        [{"id": code, "state": NOT_OBTAINED} for code in missing],
    )


_PROGRESS = {
    "any_notion": _progress_any_notion,
    "fact_level": _progress_fact_level,
    "half_tier_at_least": _progress_half_tier,
    "certifications": _progress_certifications,
}


def _unusable_rank(error):
    """Valeur de `rank_card` quand la carte, les données ou les règles sont inutilisables."""
    reason = f"carte, données ou règles inutilisables ({type(error).__name__} : {error})"
    return unmeasurable(reason, "card_unmeasurable")


def _none(error):
    """Valeur de repli `None`."""
    return None


@never_raises(_unusable_rank)
def rank_card(card, notions, facts, rules):
    """Calcule le rang d'une carte : le plus haut dont toutes les conditions sont remplies.

    Args:
        card: enregistrement de `read_cards(...).records`.
        notions: enregistrements de `read_notions(...).records` (`id`, `state`, `line`).
        facts: `read_events(...).facts`, ou `None`.
        rules: dictionnaire de `config.load_rules`.

    Returns:
        `StatedValue` du rang (clé de `ranks` ou `"none"`) : `observed`, `estimated` si
        un palier de notions le décide, `unmeasurable` pour une entrée inutilisable.
    """
    ctx = _build(card, notions, facts, rules)
    position, verdict = _reached(ctx)
    if verdict is None:
        return observed("none", (NOTIONS,))
    name = list(ctx.rules.ranks)[position]
    if verdict.status == "estimated":
        return estimated(name, verdict.sources, verdict.reason, verdict.code)
    return observed(name, verdict.sources)


@never_raises(_none)
def next_rank(card, notions, facts, rules):
    """Décrit le rang suivant d'une carte (A20).

    Args:
        card: enregistrement de `read_cards(...).records`.
        notions: enregistrements de `read_notions(...).records`.
        facts: `read_events(...).facts`, ou `None`.
        rules: dictionnaire de `config.load_rules`.

    Returns:
        Dictionnaire `rank`, `condition`, `progress` (`StatedValue`), `total` et `missing`
        (liste de `{id, state}`) ; `None` au rang maximal ou pour une entrée inutilisable.
    """
    ctx = _build(card, notions, facts, rules)
    names = list(ctx.rules.ranks)
    position = _reached(ctx)[0] + 1
    if position >= len(names):
        return None
    rule = ctx.rules.ranks[names[position]]
    return {"rank": names[position], **_PROGRESS[rule["type"]](ctx, rule)}


def _citing_notions(cards, code):
    """Renvoie les identifiants des notions dont une cellule cite `code`, toutes cartes."""
    found = [
        note_id
        for record in _records(cards)
        if isinstance(record.get("certifications"), dict)
        for note_id, text in record["certifications"].items()
        if code in CODE_PATTERN.findall(text)
    ]
    return list(dict.fromkeys(found))


def _accessible(ctx, ids):
    """Dit si une certification est accessible : toutes ses notions au seuil `ready`."""
    problem = _list_problem(ctx.card)
    if problem:
        return unmeasurable(problem, "certification_list_unreadable")
    if not ids:
        return unmeasurable("aucune notion ne cite ce code", "no_certification_notion")
    ready = all(ctx.at_least(note_id, ctx.rules.ready) for note_id in ids)
    return estimated(ready, (NOTIONS,))


def _certification_entry(ctx, cards, code):
    """Construit l'entrée de `certifications[]` d'un code (A21)."""
    ids = _citing_notions(cards, code)
    found = ctx.obtained.get(code, [])
    dates = [fact["date"] for fact in found if isinstance(fact.get("date"), str)]
    return {
        "code": code,
        "detail": None,
        "notions": ids,
        "conditions": None,
        "obtained": observed(bool(found), (EVENTS,)),
        "obtained_on": min(dates, default=None),
        "accessible": _accessible(ctx, ids),
    }


@never_raises(empty)
def card_certifications(card, cards, notions, facts, rules):
    """Liste les certifications d'une carte (A21) : codes cités, puis codes des faits.

    Args:
        card: enregistrement de `read_cards(...).records`.
        cards: toutes les cartes, pour les notions qui citent chaque code (A2).
        notions: enregistrements de `read_notions(...).records`.
        facts: `read_events(...).facts`, ou `None`.
        rules: dictionnaire de `config.load_rules`.

    Returns:
        Tuple de dictionnaires `code`, `detail`, `notions`, `conditions`, `obtained`,
        `obtained_on` et `accessible` ; `()` pour une entrée inutilisable.
    """
    ctx = _build(card, notions, facts, rules)
    own = [
        fact.get("value")
        for fact in ctx.facts
        if fact.get("metric") == CERT_METRIC
        if fact.get("domain") == ctx.card["name"]
    ]
    codes = list(dict.fromkeys([*_card_codes(ctx.card), *own]))
    return tuple(_certification_entry(ctx, cards, code) for code in codes)


def _state_anomalies(notions, order):
    """Une anomalie `unknown_state` par notion dont l'état n'est pas dans `order`."""
    return [
        Anomaly(
            NOTIONS_FILE,
            note["line"],
            "unknown_state",
            f"notion {note.get('id')!r} : état {note.get('state')!r} inconnu",
        )
        for note in _records(notions)
        if note.get("state") not in order
    ]


def _fact_problems(fact, names, codes, levels):
    """Liste les couples (nature, détail) des problèmes d'un fait `niveau` ou `certification`.

    Args:
        fact: fait de `read_events(...).facts`.
        names: noms des cartes connues.
        codes: codes de certification cités par les cartes.
        levels: valeurs de `niveau` des règles.

    Returns:
        Liste de couples, vide si le fait est valide.
    """
    metric, domain, value = fact.get("metric"), fact.get("domain"), fact.get("value")
    problems = []
    if domain not in names:
        problems.append(("unknown_card", f"carte {domain!r} inconnue (fait {metric!r})"))
    if metric == LEVEL_METRIC and value not in levels:
        problems.append(("unknown_level", f"niveau {value!r} inconnu pour {domain!r}"))
    if metric == CERT_METRIC and value not in codes:
        problems.append(("unknown_certification", f"code {value!r} cité par aucune carte"))
    return problems


def _unreadable_anomalies(cards):
    """Une anomalie `unreadable_certification` par carte à cellule illisible."""
    found = []
    for record in _records(cards):
        texts = _unreadable_texts(record)
        if texts:
            detail = f"carte {record.get('name')!r} : cellule illisible « {'; '.join(texts)} »"
            found.append(Anomaly(CARDS_LABEL, 1, "unreadable_certification", detail))
    return found


@never_raises(empty)
def rank_anomalies(cards, notions, facts, rules):
    """Signale les états, niveaux, cartes et codes inconnus (A9, A13).

    Args:
        cards: enregistrements de `read_cards(...).records`.
        notions: enregistrements de `read_notions(...).records`.
        facts: `read_events(...).facts`, ou `None`.
        rules: dictionnaire de `config.load_rules`.

    Returns:
        Tuple d'`Anomaly` `unknown_state`, `unknown_level`, `unknown_card`,
        `unknown_certification` et `unreadable_certification` (cellule sans code) ;
        `()` si les règles sont inutilisables.
    """
    parsed = _read_rules(rules)
    names = {card.get("name") for card in _records(cards)}
    codes = {code for card in _records(cards) for code in _card_codes(card)}
    found = _state_anomalies(notions, parsed.order)
    found.extend(_unreadable_anomalies(cards))
    for fact in _records(facts):
        if fact.get("metric") not in (LEVEL_METRIC, CERT_METRIC):
            continue
        found.extend(
            Anomaly(EVENTS_FILE, fact["line"], kind, detail)
            for kind, detail in _fact_problems(fact, names, codes, parsed.levels)
        )
    return tuple(found)
