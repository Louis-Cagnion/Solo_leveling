"""Réseau de notions (T9, A13, A25) : contrôle des relations et prérequis fragiles.

Fonctions pures, sans lecture de source : elles reçoivent les enregistrements déjà lus de
`relations.csv`, `notions.md` et des cartes. Aucune fonction publique ne lève : une entrée
inutilisable est ignorée, et des règles inutilisables donnent `()`. Aucune récursion sur les
chaînes de prérequis : le repérage des cycles parcourt le graphe en boucle.
"""

from system_sync.model import Anomaly
from system_sync.rules.guard import empty, never_raises

RELATIONS_FILE = "relations.csv"
PREREQUISITE = "prerequis"
RELATION_STATUSES = ("theorique", "reconnue", "demontree")
# État sous lequel un prérequis est fragile, et état au moins requis de sa cible.
FRAGILE_BELOW = "comprise"
# Champs d'une relation de `read_relations(...).records` et type attendu.
RELATION_FIELDS = {
    "source": str,
    "relation": str,
    "target": str,
    "status": str,
    "line": int,
}


def _is_self(relation, seen):
    """Dit si la relation relie une notion à elle-même."""
    return relation["source"] == relation["target"]


def _has_unknown_status(relation, seen):
    """Dit si le statut de la relation est hors de `RELATION_STATUSES`."""
    return relation["status"] not in RELATION_STATUSES


def _is_duplicate(relation, seen):
    """Dit si une relation gardée a déjà le même triplet source, relation, cible."""
    return _triplet(relation) in seen


# Causes de rejet, dans l'ordre : nature, test et message (champs de la relation, `allowed`).
REJECTIONS = (
    (
        "self_relation",
        _is_self,
        "relation {relation!r} de la notion {source!r} vers elle-même",
    ),
    (
        "unknown_status",
        _has_unknown_status,
        "relation {source!r} {relation!r} {target!r} : statut {status!r} inconnu, "
        "attendu {allowed}",
    ),
    (
        "duplicate_relation",
        _is_duplicate,
        "relation {source!r} {relation!r} {target!r} déjà lue plus haut",
    ),
)


def _nothing(error):
    """Valeur de repli de `control_relations` : aucune relation, aucune anomalie."""
    return ((), ())


def _dicts(items):
    """Garde les dictionnaires d'une liste ou d'un tuple, sinon renvoie une liste vide."""
    if not isinstance(items, (list, tuple)):
        return []
    return [item for item in items if isinstance(item, dict)]


def _usable(relations):
    """Garde les relations dont chaque champ de `RELATION_FIELDS` a le type attendu."""
    return [
        relation
        for relation in _dicts(relations)
        if all(isinstance(relation.get(key), kind) for key, kind in RELATION_FIELDS.items())
    ]


def _triplet(relation):
    """Renvoie le triplet qui identifie une relation : source, type et cible."""
    return (relation["source"], relation["relation"], relation["target"])


def _known_ids(notions, cards):
    """Renvoie les identifiants connus : notions suivies et identifiants des cartes."""
    found = {note.get("id") for note in _dicts(notions)}
    for card in _dicts(cards):
        ids = card.get("ids")
        found.update(ids if isinstance(ids, (list, tuple)) else ())
    return found


def _rejection_anomalies(relation, seen):
    """Renvoie les anomalies de rejet d'une relation, vide si elle est gardée."""
    allowed = ", ".join(RELATION_STATUSES)
    return [
        Anomaly(
            RELATIONS_FILE,
            relation["line"],
            kind,
            message.format(allowed=allowed, **relation),
        )
        for kind, test, message in REJECTIONS
        if test(relation, seen)
    ]


def _endpoint_anomalies(relation, known):
    """Renvoie une anomalie `unknown_endpoint` par extrémité absente de `known`."""
    return [
        Anomaly(
            RELATIONS_FILE,
            relation["line"],
            "unknown_endpoint",
            f"notion {relation[role]!r} inconnue ({role} de {relation['relation']!r})",
        )
        for role in ("source", "target")
        if relation[role] not in known
    ]


def _screen(relations, notions, cards):
    """Écarte les relations rejetées et signale les extrémités inconnues des gardées.

    Args:
        relations: enregistrements de `read_relations(...).records`.
        notions: enregistrements de `read_notions(...).records`.
        cards: enregistrements de `read_cards(...).records`.

    Returns:
        Couple (liste des relations gardées dans l'ordre d'entrée, liste d'anomalies).
    """
    known = _known_ids(notions, cards)
    kept, seen, found = [], set(), []
    for relation in _usable(relations):
        rejected = _rejection_anomalies(relation, seen)
        found.extend(rejected or _endpoint_anomalies(relation, known))
        if not rejected:
            kept.append(relation)
            seen.add(_triplet(relation))
    return kept, found


class _Walker:
    """Parcours itératif de Tarjan : regroupe les nœuds en composantes fortement connexes.

    Args:
        graph: dictionnaire nœud vers liste des nœuds suivants.
    """

    def __init__(self, graph):
        self.graph = graph
        self.index = {}
        self.low = {}
        self.stack = []
        self.on_stack = set()
        self.components = []

    def _open(self, node):
        """Numérote un nœud, l'empile et renvoie son entrée de pile de travail."""
        self.index[node] = self.low[node] = len(self.index)
        self.stack.append(node)
        self.on_stack.add(node)
        return (node, iter(self.graph.get(node, ())))

    def _close(self, node):
        """Dépile la composante dont `node` est la racine, si c'en est une."""
        if self.low[node] != self.index[node]:
            return
        component = []
        while not component or component[-1] != node:
            component.append(self.stack.pop())
            self.on_stack.discard(component[-1])
        self.components.append(component)

    def _advance(self, work):
        """Avance d'un pas le dernier nœud de la pile de travail."""
        node, children = work[-1]
        for child in children:
            if child not in self.index:
                work.append(self._open(child))
                return
            if child in self.on_stack:
                self.low[node] = min(self.low[node], self.index[child])
        work.pop()
        if work:
            parent = work[-1][0]
            self.low[parent] = min(self.low[parent], self.low[node])
        self._close(node)

    def run(self):
        """Parcourt tout le graphe et renvoie la liste des composantes (listes de nœuds)."""
        for root in self.graph:
            if root in self.index:
                continue
            work = [self._open(root)]
            while work:
                self._advance(work)
        return self.components


def _cycle_anomalies(kept):
    """Renvoie une anomalie `prerequisite_cycle` par ensemble de notions en cercle.

    Args:
        kept: relations gardées ; seules celles de type `prerequis` forment un cycle.

    Returns:
        Liste d'`Anomaly` à la plus petite ligne des relations du cycle.
    """
    graph = {}
    prerequisites = [item for item in kept if item["relation"] == PREREQUISITE]
    for item in prerequisites:
        graph.setdefault(item["source"], []).append(item["target"])
    cycles = [part for part in _Walker(graph).run() if len(part) > 1]
    owner = {note_id: number for number, part in enumerate(cycles) for note_id in part}
    lines = {}
    for item in prerequisites:
        number = owner.get(item["source"])
        if number is not None and number == owner.get(item["target"]):
            lines[number] = min(item["line"], lines.get(number, item["line"]))
    return [
        Anomaly(
            RELATIONS_FILE,
            lines[number],
            "prerequisite_cycle",
            f"notions en cercle par {PREREQUISITE} : {', '.join(sorted(part))}",
        )
        for number, part in enumerate(cycles)
    ]


def _read_order(rules):
    """Renvoie (états du plus bas au plus haut, états exclus) de `rules["states"]`.

    Args:
        rules: dictionnaire de `config.load_rules`, de n'importe quel type.

    Returns:
        Le couple ; lève `ValueError` si `states.order` manque ou n'a pas `FRAGILE_BELOW`.
    """
    states = rules.get("states") if isinstance(rules, dict) else None
    order = states.get("order") if isinstance(states, dict) else None
    if not isinstance(order, list) or FRAGILE_BELOW not in order:
        raise ValueError(f"[states] sans liste `order` avec {FRAGILE_BELOW!r} : {states!r}")
    return order, frozenset(states.get("excluded", ()))


def _fragile_anomalies(kept, notions, cards, rules):
    """Renvoie une anomalie `fragile_prerequisite` par prérequis fragile (A25).

    Args:
        kept: relations gardées par `_screen`.
        notions: enregistrements de `read_notions(...).records`.
        cards: enregistrements de `read_cards(...).records`.
        rules: dictionnaire de `config.load_rules`.

    Returns:
        Liste d'`Anomaly` ; la source est sous `FRAGILE_BELOW` (un état exclu y est sous) et
        la cible au moins à `FRAGILE_BELOW` (un état exclu ne l'est jamais).
    """
    order, excluded = _read_order(rules)
    threshold = order.index(FRAGILE_BELOW)
    states = {note.get("id"): note.get("state") for note in _dicts(notions)}
    known = _known_ids(notions, cards)
    found = []
    for item in kept:
        ends = (item["source"], item["target"])
        if item["relation"] != PREREQUISITE or not known.issuperset(ends):
            continue
        source, target = (states.get(note_id, order[0]) for note_id in ends)
        if source not in order or target not in order:
            continue
        low = source in excluded or order.index(source) < threshold
        high = target not in excluded and order.index(target) >= threshold
        if low and high:
            found.append(
                Anomaly(
                    RELATIONS_FILE,
                    item["line"],
                    "fragile_prerequisite",
                    f"prérequis {ends[0]!r} à l'état « {source} » "
                    f"de {ends[1]!r} à l'état « {target} »",
                )
            )
    return found


def _by_line(anomalies):
    """Renvoie les anomalies en tuple, triées par ligne (tri stable)."""
    return tuple(sorted(anomalies, key=lambda item: item.line))


@never_raises(_nothing)
def control_relations(relations, notions, cards):
    """Contrôle les relations : extrémité inconnue, auto-relation, doublon, statut, cycle.

    Args:
        relations: enregistrements de `read_relations(...).records`, ou `None`.
        notions: enregistrements de `read_notions(...).records`, ou `None`.
        cards: enregistrements de `read_cards(...).records`, ou `None`.

    Returns:
        Couple (tuple des relations gardées dans l'ordre d'entrée, tuple d'`Anomaly` triées
        par ligne) ; une extrémité inconnue et un cycle n'écartent pas la relation.
    """
    kept, found = _screen(relations, notions, cards)
    return tuple(kept), _by_line([*found, *_cycle_anomalies(kept)])


@never_raises(empty)
def fragile_prerequisites(relations, notions, cards, rules):
    """Repère les prérequis fragiles parmi les relations gardées (A25).

    Args:
        relations: enregistrements de `read_relations(...).records`, ou `None`.
        notions: enregistrements de `read_notions(...).records`, ou `None`.
        cards: enregistrements de `read_cards(...).records`, ou `None`.
        rules: dictionnaire de `config.load_rules`.

    Returns:
        Tuple d'`Anomaly` `fragile_prerequisite` triées par ligne ; `()` si les règles
        sont inutilisables.
    """
    kept, _ = _screen(relations, notions, cards)
    return _by_line(_fragile_anomalies(kept, notions, cards, rules))


@never_raises(empty)
def network_anomalies(relations, notions, cards, rules):
    """Rassemble les anomalies du contrôle, puis celles des prérequis fragiles.

    Args:
        relations: enregistrements de `read_relations(...).records`, ou `None`.
        notions: enregistrements de `read_notions(...).records`, ou `None`.
        cards: enregistrements de `read_cards(...).records`, ou `None`.
        rules: dictionnaire de `config.load_rules`.

    Returns:
        Tuple d'`Anomaly` : celles de `control_relations`, puis celles de
        `fragile_prerequisites`.
    """
    _, found = control_relations(relations, notions, cards)
    return found + fragile_prerequisites(relations, notions, cards, rules)
