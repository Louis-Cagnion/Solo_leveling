"""Modèle de données de `sync` : valeur statuée et anomalie (T2, amendements A17 et A18).

Une valeur statuée porte sa valeur, son statut, ses sources et, quand il le faut, une
raison en français avec son code traduisible. Ses invariants sont vérifiés à la création,
et `output.py` réutilise la même règle (`stated_problems`) pour valider un état.
"""

from dataclasses import dataclass

STATUSES = ("observed", "estimated", "insufficient", "unmeasurable")

# Statuts qui exigent une raison non vide (A17).
REASON_REQUIRED = ("insufficient", "unmeasurable")

# Vocabulaire fermé des codes de raison (A18) ; la page les traduit (A27).
REASON_CODES = frozenset(
    {
        "api_unavailable",
        "xp_interpolated",
        "third_party_table",
        "ia_rate",
        "below_threshold",
        "certification_list_unreadable",
        "no_certification_notion",
        "full_list_unavailable",
        "no_personal_project",
        "card_unmeasurable",
    }
)


class ModelError(ValueError):
    """Invariant de valeur statuée violé ; le message nomme le champ et la valeur."""


def is_blank(text):
    """Dit si une raison est inutilisable.

    Args:
        text: valeur de `reason`, de n'importe quel type.

    Returns:
        True si `text` n'est pas une chaîne ou ne contient que des espaces.
    """
    return not isinstance(text, str) or not text.strip()


def stated_problems(value, status, sources, reason, reason_code):
    """Liste les violations des invariants d'une valeur statuée.

    Args:
        value: valeur portée, de n'importe quel type JSON.
        status: statut annoncé, attendu parmi `STATUSES`.
        sources: noms des sources, liste ou tuple de chaînes (éventuellement vide).
        reason: phrase française de repli, chaîne ou `None`.
        reason_code: code de `REASON_CODES` ou `None`.

    Returns:
        Liste de couples (champ fautif, cause avec la valeur reçue), vide si valide.
    """
    if status not in STATUSES:
        return [("status", f"statut {status!r} hors de {STATUSES}")]
    found = []
    if status == "observed" and value is None:
        found.append(("value", "valeur null pour un statut observed"))
    if status == "observed" and not sources:
        found.append(("sources", f"sources {sources!r} vides pour un statut observed"))
    if status == "unmeasurable" and value is not None:
        found.append(("value", f"valeur {value!r} pour un statut unmeasurable"))
    if status in REASON_REQUIRED and is_blank(reason):
        found.append(("reason", f"raison {reason!r} vide pour un statut {status}"))
    if reason_code is not None and reason_code not in REASON_CODES:
        found.append(("reason_code", f"code {reason_code!r} hors du vocabulaire"))
    if reason_code is None and not is_blank(reason):
        found.append(("reason_code", f"code manquant pour la raison {reason!r}"))
    return found


@dataclass(frozen=True)
class StatedValue:
    """Valeur statuée `{value, status, sources, reason, reason_code}`.

    Args:
        value: valeur JSON, `None` pour `unmeasurable`, jamais `None` pour `observed`.
        status: un des quatre `STATUSES`.
        sources: noms des sources, au moins une pour `observed`.
        reason: phrase française, obligatoire pour `insufficient` et `unmeasurable`.
        reason_code: code de `REASON_CODES`, obligatoire dès qu'il y a une raison.
    """

    value: object
    status: str
    sources: tuple = ()
    reason: object = None
    reason_code: object = None

    def __post_init__(self):
        """Refuse la création si un invariant est violé (`ModelError`)."""
        problems = stated_problems(
            self.value,
            self.status,
            self.sources,
            self.reason,
            self.reason_code,
        )
        if problems:
            field, cause = problems[0]
            raise ModelError(f"{field} : {cause}")
        object.__setattr__(self, "sources", tuple(self.sources or ()))

    def to_dict(self):
        """Renvoie la forme JSON de l'état, sources en liste."""
        return {
            "value": self.value,
            "status": self.status,
            "sources": list(self.sources),
            "reason": self.reason,
            "reason_code": self.reason_code,
        }


def observed(value, sources):
    """Crée une valeur lue telle quelle dans une source.

    Args:
        value: valeur non nulle.
        sources: noms des sources, au moins un.

    Returns:
        La `StatedValue` de statut `observed`.
    """
    return StatedValue(value, "observed", tuple(sources))


def estimated(value, sources, reason=None, reason_code=None):
    """Crée une valeur issue d'une règle à hypothèse.

    Args:
        value: valeur estimée.
        sources: noms des sources.
        reason: phrase française facultative, qui impose alors `reason_code`.
        reason_code: code de `REASON_CODES` ou `None`.

    Returns:
        La `StatedValue` de statut `estimated`.
    """
    return StatedValue(value, "estimated", tuple(sources), reason, reason_code)


def insufficient(reason, reason_code, value=None):
    """Crée une valeur dont les conditions ne sont pas remplies.

    Args:
        reason: phrase française non vide.
        reason_code: code de `REASON_CODES`.
        value: valeur provisoire facultative.

    Returns:
        La `StatedValue` de statut `insufficient`.
    """
    return StatedValue(value, "insufficient", (), reason, reason_code)


def unmeasurable(reason, reason_code):
    """Crée une valeur qu'aucune mesure ne permet d'obtenir (valeur `None`).

    Args:
        reason: phrase française non vide.
        reason_code: code de `REASON_CODES`.

    Returns:
        La `StatedValue` de statut `unmeasurable`.
    """
    return StatedValue(None, "unmeasurable", (), reason, reason_code)


@dataclass(frozen=True)
class Anomaly:
    """Ligne rejetée ou suspecte d'une source.

    Args:
        file: nom du fichier source.
        line: numéro de ligne, entier à partir de 1.
        kind: nature de l'anomalie, texte court.
        detail: précision, texte.
    """

    file: str
    line: int
    kind: str
    detail: str

    def __str__(self):
        """Rend `fichier:ligne : nature : détail`."""
        return f"{self.file}:{self.line} : {self.kind} : {self.detail}"

    def to_dict(self):
        """Renvoie les quatre champs sous forme JSON."""
        return {
            "file": self.file,
            "line": self.line,
            "kind": self.kind,
            "detail": self.detail,
        }
