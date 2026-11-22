"""Lecteurs des sources de `/professor` (T3.b) : cartes, notions, relations, événements,
historique et projets.

Lecture seule, sans réseau. Aucune fonction publique ne lève : une source illisible
devient un `SourceResult` indisponible, une ligne ou une carte rejetée devient une
`model.Anomaly`. Le moteur CSV vit dans `professor_csv.py`, les tableaux Markdown dans
`professor_markdown.py`. Contrat détaillé dans `tests/system_sync/sources/test_professor.py`.
"""

import os
import stat
from dataclasses import dataclass
from functools import partial
from pathlib import Path

from system_sync.model import Anomaly
from system_sync.sources.professor_csv import (
    Check,
    CsvSpec,
    SourceError,
    parse_csv,
)
from system_sync.sources.professor_markdown import (
    NOTION_STATES,
    parse_card,
    parse_notions,
)

__all__ = [
    "NOTION_STATES",
    "SourceError",
    "SourceResult",
    "read_cards",
    "read_events",
    "read_history",
    "read_notions",
    "read_professor",
    "read_projects",
    "read_relations",
]

AUTHORS = frozenset({"ia", "louis", "mixte", "lecture"})
RELATION_STATUSES = frozenset({"theorique", "reconnue", "demontree"})
FACT_LEVELS = frozenset({"débutant", "intermédiaire", "avancé", "transcendée"})
FACT_METRICS = frozenset({"niveau", "certification", "titre"})
PROJECT_FRAMES = frozenset({"perso", "pro"})
PROJECT_STATUSES = frozenset({"en cours", "livré", "abandonné"})
# Échecs de lecture d'une carte rangés en anomalie ; tout autre échec rend la source
# indisponible.
CARD_FAILURES = {"encoding": "bad_encoding", "empty": "missing_title"}


@dataclass(frozen=True)
class SourceResult:
    """Résultat de lecture d'une source.

    Args:
        name: `cards`, `notions`, `relations`, `events`, `history` ou `projects`.
        path: `Path` du fichier ou du dossier lu.
        status: `ok`, `unavailable`, ou `absent` pour `projets.csv` seul.
        error: `None` si `ok`, sinon texte avec le chemin et la cause.
        records: tuple de dicts, un par ligne ou carte gardée.
        facts: tuple des événements `niveau`, `certification` et `titre`.
        anomalies: tuple de `model.Anomaly`.
        read: nombre de lignes de données ou de cartes lues.
        rejected: nombre de lignes ou cartes rejetées, hors dates suspectes.
    """

    name: str
    path: Path
    status: str
    error: str | None = None
    records: tuple = ()
    facts: tuple = ()
    anomalies: tuple = ()
    read: int = 0
    rejected: int = 0


CSV_SPECS = {
    "relations": CsvSpec(
        name="relations",
        columns={
            "date": "date",
            "source": "source",
            "relation": "relation",
            "cible": "target",
            "statut": "status",
            "limite": "limit",
            "preuve": "proof",
        },
        checks=(Check("status", "statut", RELATION_STATUSES, "unknown_status"),),
        unique=("source", "relation", "target"),
    ),
    "events": CsvSpec(
        name="events",
        columns={
            "date": "date",
            "session": "session",
            "domaine": "domain",
            "notion": "notion",
            "metrique": "metric",
            "valeur": "value",
            "contexte": "context",
            "forme_visuelle": "visual_form",
            "preuve": "proof",
        },
        checks=(
            Check("value", "niveau", FACT_LEVELS, "unknown_level", ("metric", "niveau")),
        ),
        fact_metrics=FACT_METRICS,
    ),
    "history": CsvSpec(
        name="history",
        columns={
            "date": "date",
            "projet": "project",
            "mode": "mode",
            "domaine": "domain",
            "notions": "notions",
            "auteur": "author",
            "preuve": "proof",
        },
        checks=(Check("author", "auteur", AUTHORS, "unknown_author"),),
        flag_suspect=True,
    ),
    "projects": CsvSpec(
        name="projects",
        columns={
            "id": "id",
            "cadre": "frame",
            "statut": "status",
            "date": "date",
            "equivalent_42": "equivalent_42",
            "justification": "justification",
        },
        checks=(
            Check("frame", "cadre", PROJECT_FRAMES, "unknown_frame"),
            Check("status", "statut", PROJECT_STATUSES, "unknown_status"),
        ),
        optional=True,
        ordered=False,
    ),
}


def load_text(path):
    """Lit un fichier ordinaire en UTF-8, sans jamais bloquer sur une FIFO.

    Args:
        path: `Path` attendu vers un fichier ordinaire non vide.

    Returns:
        Le texte, sans BOM initial.

    Raises:
        SourceError: fichier absent, dossier, non ordinaire, illisible, vide ou
            non UTF-8 (l'offset du premier octet fautif est nommé).
    """
    try:
        mode = os.stat(path).st_mode
        if stat.S_ISDIR(mode):
            raise SourceError("os", f"{path} : dossier au lieu d'un fichier")
        if not stat.S_ISREG(mode):
            raise SourceError("os", f"{path} : ni fichier ordinaire ni dossier")
        with os.fdopen(os.open(path, os.O_RDONLY | os.O_NONBLOCK), "rb") as handle:
            data = handle.read()
    except FileNotFoundError as error:
        raise SourceError("absent", f"{path} : absent") from error
    except OSError as error:
        raise SourceError("os", f"{path} : {error.strerror}") from error
    if not data:
        raise SourceError("empty", f"{path} : vide")
    try:
        return data.decode("utf-8").removeprefix("﻿")
    except UnicodeDecodeError as error:
        raise SourceError(
            "encoding",
            f"{path} : octet non UTF-8 à l'offset {error.start}",
        ) from error


def guarded(name, path, parse, optional=False):
    """Lit `path`, applique `parse` et rend un `SourceResult` sans jamais lever.

    Args:
        name: nom du résultat.
        path: chemin du fichier, texte ou `Path`.
        parse: fonction (chemin, texte) vers un dict de champs de `SourceResult`.
        optional: `True` si l'absence du fichier donne le statut `absent`.

    Returns:
        Le résultat `ok`, ou indisponible (`absent` si facultatif et absent).
    """
    path = Path(path)
    try:
        parsed = parse(path, load_text(path))
    except SourceError as error:
        status = "absent" if optional and error.code == "absent" else "unavailable"
        return SourceResult(name=name, path=path, status=status, error=str(error))
    return SourceResult(name=name, path=path, status="ok", **parsed)


def read_csv(spec, path):
    """Lit un CSV de `/professor` décrit par `spec`.

    Args:
        spec: `CsvSpec` de la source.
        path: chemin du fichier CSV.

    Returns:
        Le `SourceResult` de la source.
    """
    return guarded(spec.name, path, partial(parse_csv, spec), spec.optional)


def read_relations(path):
    """Lit `relations.csv` (7 champs).

    Args:
        path: chemin de `relations.csv`.

    Returns:
        Le `SourceResult` `relations`.
    """
    return read_csv(CSV_SPECS["relations"], path)


def read_events(path):
    """Lit `evenements.csv` (9 champs) et en tire les faits.

    Args:
        path: chemin de `evenements.csv`.

    Returns:
        Le `SourceResult` `events`.
    """
    return read_csv(CSV_SPECS["events"], path)


def read_history(path):
    """Lit `historique-ia.csv` (7 champs).

    Args:
        path: chemin de `historique-ia.csv`.

    Returns:
        Le `SourceResult` `history`.
    """
    return read_csv(CSV_SPECS["history"], path)


def read_projects(path):
    """Lit `projets.csv` (6 champs), facultatif.

    Args:
        path: chemin de `projets.csv`.

    Returns:
        Le `SourceResult` `projects`, de statut `absent` si le fichier manque.
    """
    return read_csv(CSV_SPECS["projects"], path)


def read_notions(path):
    """Lit `notions.md`.

    Args:
        path: chemin de `notions.md`.

    Returns:
        Le `SourceResult` `notions`.
    """
    return guarded("notions", path, parse_notions)


def list_cards(directory):
    """Liste les fichiers `.md` ordinaires d'un dossier, triés par nom.

    Args:
        directory: `Path` du dossier des cartes.

    Returns:
        La liste triée des `Path`.

    Raises:
        SourceError: dossier absent, illisible, qui n'en est pas un, ou sans carte.
    """
    try:
        if not directory.is_dir() and directory.exists():
            raise SourceError("os", f"{directory} : fichier au lieu d'un dossier")
        with os.scandir(directory) as entries:
            files = sorted(
                Path(entry.path)
                for entry in entries
                if entry.name.endswith(".md") and entry.is_file()
            )
    except FileNotFoundError as error:
        raise SourceError("absent", f"{directory} : absent") from error
    except OSError as error:
        raise SourceError("os", f"{directory} : {error.strerror}") from error
    if not files:
        raise SourceError("empty", f"{directory} : aucune carte .md")
    return files


def read_cards(directory):
    """Lit toutes les cartes d'un dossier, dans l'ordre alphabétique des fichiers.

    Args:
        directory: chemin du dossier `cartes/`.

    Returns:
        Le `SourceResult` `cards` ; une carte rejetée est comptée et signalée.
    """
    directory = Path(directory)
    records, anomalies, taken = [], [], {}
    try:
        files = list_cards(directory)
        for path in files:
            label = f"{directory.name}/{path.name}"
            try:
                card, notes = parse_card(label, load_text(path), taken)
            except SourceError as error:
                if error.code not in CARD_FAILURES:
                    raise
                notes = [Anomaly(label, 1, CARD_FAILURES[error.code], str(error))]
                card = None
            anomalies.extend(notes)
            if card:
                records.append(card)
    except SourceError as error:
        return SourceResult(
            name="cards",
            path=directory,
            status="unavailable",
            error=str(error),
        )
    return SourceResult(
        name="cards",
        path=directory,
        status="ok",
        records=tuple(records),
        anomalies=tuple(anomalies),
        read=len(files),
        rejected=len(files) - len(records),
    )


def read_professor(suivi_dir, history_csv):
    """Lit les six sources de `/professor`.

    Args:
        suivi_dir: chemin du dossier du suivi (`cartes/`, `notions.md`, `relations.csv`,
            `evenements.csv`, `projets.csv` facultatif).
        history_csv: chemin de `historique-ia.csv`.

    Returns:
        Dict de six `SourceResult`, clés `cards`, `notions`, `relations`, `events`,
        `history` et `projects`.
    """
    suivi = Path(suivi_dir)
    return {
        "cards": read_cards(suivi / "cartes"),
        "notions": read_notions(suivi / "notions.md"),
        "relations": read_relations(suivi / "relations.csv"),
        "events": read_events(suivi / "evenements.csv"),
        "history": read_history(history_csv),
        "projects": read_projects(suivi / "projets.csv"),
    }
