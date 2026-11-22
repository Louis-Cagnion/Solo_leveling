"""Lecteurs des sources de `/professor` (T3.b) : cartes, notions, relations, événements,
historique et projets.

Lecture seule, sans réseau. Aucune fonction publique ne lève : une source illisible
devient un `SourceResult` indisponible, une ligne ou une carte rejetée devient une
`model.Anomaly`. Contrat détaillé dans `tests/system_sync/sources/test_professor.py`.
"""

import csv
import io
import os
import re
import stat
from dataclasses import dataclass
from datetime import date
from functools import partial
from pathlib import Path

from system_sync.model import Anomaly

TIERS = ("Débutant", "Intermédiaire", "Avancé", "Transcendée")
# États valides figés ici : le plan n'injecte pas `config/rules.toml` dans T3.
NOTION_STATES = frozenset(
    {
        "non rencontrée",
        "découverte",
        "en cours",
        "comprise",
        "appliquée",
        "retenue",
        "transférée",
        "transcendée",
        "déclarée",
    }
)
AUTHORS = frozenset({"ia", "louis", "mixte", "lecture"})
RELATION_STATUSES = frozenset({"theorique", "reconnue", "demontree"})
FACT_LEVELS = frozenset({"débutant", "intermédiaire", "avancé", "transcendée"})
FACT_METRICS = frozenset({"niveau", "certification", "titre"})
# Colonne de `notions.md` vers clé d'enregistrement ; « Solidité » n'est jamais exportée.
NOTION_COLUMNS = {
    "Id": "id",
    "Notion": "title",
    "Objectif": "objective",
    "État": "state",
    "Dernière pratique": "last_practice",
    "Intervalle": "interval",
    "Prochain rappel": "next_review",
    "Dernier M1": "last_m1",
    "Rechutes": "relapses",
}
NOTION_DATE_KEYS = ("last_practice", "next_review")
DATE_MIN = date(2020, 1, 1)

DATE_PATTERN = re.compile(r"(?:([0-9]{2})/)?([0-9]{2})/([0-9]{4})")
UNESCAPED_BAR = re.compile(r"(?<!\\)\|")
SEPARATOR_CELL = re.compile(r":?-+:?")
CARD_TITLE = re.compile(r"# Carte : (.+)")
CARD_DECLARED = re.compile(r"- \*\*Notions\*\* : ([0-9]+)(?:, dont ([0-9]+) déjà)?")
# Échecs de lecture d'une carte rangés en anomalie ; tout autre échec rend la source
# indisponible.
CARD_FAILURES = {"encoding": "bad_encoding", "empty": "missing_title"}


class SourceError(Exception):
    """Échec de lecture d'une source, avec un code court et un message complet.

    Args:
        code: `absent`, `empty`, `encoding`, `csv`, `header` ou `os`.
        message: texte qui nomme le chemin, la ligne ou l'offset et la cause.
    """

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


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


@dataclass(frozen=True)
class Check:
    """Contrôle d'une valeur de champ contre un ensemble d'entrées permises.

    Args:
        key: clé de l'enregistrement contrôlée.
        label: mot qui désigne le champ dans le message.
        allowed: ensemble de textes permis.
        kind: nature d'anomalie produite en cas d'écart.
        only_if: couple (clé, valeur) qui limite le contrôle, ou tuple vide.
    """

    key: str
    label: str
    allowed: frozenset
    kind: str
    only_if: tuple = ()

    def problem(self, record):
        """Décrit l'écart de `record` à ce contrôle.

        Args:
            record: dict dont les clés incluent `key` et celle de `only_if`.

        Returns:
            Le texte du détail, ou `None` si la valeur est permise ou hors champ.
        """
        if self.only_if and record[self.only_if[0]] != self.only_if[1]:
            return None
        value = record[self.key]
        if value in self.allowed:
            return None
        expected = ", ".join(sorted(self.allowed))
        return f"{self.label} {value!r} inconnu, attendu parmi {expected}"


@dataclass(frozen=True)
class CsvSpec:
    """Description d'un CSV positionnel dont la première colonne est la date.

    Args:
        name: nom du résultat.
        keys: clés d'enregistrement, dans l'ordre des colonnes.
        checks: tuple de `Check` appliqués après la date.
        unique: clés dont le triplet garde la dernière ligne, ou tuple vide.
        flag_suspect: `True` pour ajouter la clé `suspect` aux enregistrements.
        fact_metrics: valeurs de `metric` exposées en faits.
        optional: `True` si l'absence du fichier est un statut `absent`.
    """

    name: str
    keys: tuple
    checks: tuple = ()
    unique: tuple = ()
    flag_suspect: bool = False
    fact_metrics: frozenset = frozenset()
    optional: bool = False


CSV_SPECS = {
    "relations": CsvSpec(
        name="relations",
        keys=("date", "source", "relation", "target", "status", "limit", "proof"),
        checks=(Check("status", "statut", RELATION_STATUSES, "unknown_status"),),
        unique=("source", "relation", "target"),
    ),
    "events": CsvSpec(
        name="events",
        keys=(
            "date",
            "session",
            "domain",
            "notion",
            "metric",
            "value",
            "context",
            "visual_form",
            "proof",
        ),
        checks=(
            Check("value", "niveau", FACT_LEVELS, "unknown_level", ("metric", "niveau")),
        ),
        fact_metrics=FACT_METRICS,
    ),
    "history": CsvSpec(
        name="history",
        keys=("date", "project", "mode", "domain", "notions", "author", "proof"),
        checks=(Check("author", "auteur", AUTHORS, "unknown_author"),),
        flag_suspect=True,
    ),
    "projects": CsvSpec(
        name="projects",
        keys=("date", "id", "frame", "status", "equivalent_42", "justification"),
        optional=True,
    ),
}


def parse_date(text):
    """Convertit `jj/mm/aaaa` en AAAA-MM-JJ et juge la date.

    Args:
        text: texte brut de la cellule, `jj/mm/aaaa` ou `mm/aaaa` attendu.

    Returns:
        Couple (date ISO ou `None`, verdict `ok`, `suspect` ou `invalid`) : `suspect`
        pour un mois sans jour ou une date hors de 2020-01-01 à aujourd'hui.
    """
    match = DATE_PATTERN.fullmatch(text)
    if not match:
        return None, "invalid"
    day, month, year = match.groups()
    try:
        parsed = date(int(year), int(month), int(day or 1))
    except ValueError:
        return None, "invalid"
    if day is None:
        return None, "suspect"
    in_range = DATE_MIN <= parsed <= date.today()
    return parsed.isoformat(), "ok" if in_range else "suspect"


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
        return SourceResult(name, path, status, str(error))
    return SourceResult(name, path, "ok", None, **parsed)


def tally(label, items):
    """Sépare les enregistrements gardés des anomalies et compte lus et rejetés.

    Args:
        label: nom de fichier porté par les anomalies, texte.
        items: liste de triplets (ligne, enregistrement ou `None`, notes), où `notes`
            est une liste de couples (nature, détail).

    Returns:
        Dict des champs `records`, `anomalies`, `read` et `rejected`.
    """
    records = tuple(record for _, record, _ in items if record is not None)
    anomalies = tuple(
        Anomaly(label, line, kind, detail)
        for line, _, notes in items
        for kind, detail in notes
    )
    return {
        "records": records,
        "anomalies": anomalies,
        "read": len(items),
        "rejected": len(items) - len(records),
    }


def csv_rows(path, text):
    """Découpe un CSV en lignes de données avec leur numéro de ligne physique.

    Args:
        path: `Path` du fichier, nommé dans le message d'erreur.
        text: contenu du CSV, en-tête compris.

    Returns:
        Liste de couples (numéro de la première ligne, liste de champs), en-tête et
        lignes vides exclus.

    Raises:
        SourceError: le CSV est illisible (champ trop grand par exemple).
    """
    reader = csv.reader(io.StringIO(text, newline=""))
    rows, start = [], 1
    try:
        for fields in reader:
            if fields:
                rows.append((start, fields))
            start = reader.line_num + 1
    except csv.Error as error:
        message = f"{path}:{start} : CSV illisible : {error}"
        raise SourceError("csv", message) from error
    return rows[1:]


def make_record(spec, row, line):
    """Construit l'enregistrement d'une ligne de CSV ou la rejette.

    Args:
        spec: `CsvSpec` de la source.
        row: liste de champs de la ligne.
        line: numéro de la ligne physique, entier à partir de 1.

    Returns:
        Couple (enregistrement ou `None` si rejetée, liste de couples (nature, détail)).
    """
    if len(row) != len(spec.keys):
        detail = f"{len(row)} champs reçus, {len(spec.keys)} attendus"
        return None, [("field_count", detail)]
    record = dict(zip(spec.keys, row))
    raw_date = record["date"]
    iso, verdict = parse_date(raw_date)
    if verdict == "invalid":
        return None, [("invalid_date", f"date {raw_date!r} illisible")]
    for check in spec.checks:
        problem = check.problem(record)
        if problem:
            return None, [(check.kind, problem)]
    record.update(date=iso, line=line)
    if spec.flag_suspect:
        record["suspect"] = verdict == "suspect"
    notes = []
    if verdict == "suspect":
        notes.append(("suspect_date", f"date {raw_date!r} hors plage ou sans jour"))
    return record, notes


def parse_csv(spec, path, text):
    """Lit un CSV positionnel : enregistrements, faits, anomalies et compteurs.

    Args:
        spec: `CsvSpec` de la source.
        path: `Path` du fichier.
        text: contenu du fichier.

    Returns:
        Dict des champs de `SourceResult`, la dernière ligne d'un triplet `unique`
        remplaçant les précédentes.
    """
    items = [
        (line, *make_record(spec, row, line))
        for line, row in csv_rows(path, text)
    ]
    parsed = tally(path.name, items)
    records = parsed["records"]
    if spec.unique:
        latest = {tuple(r[key] for key in spec.unique): r for r in records}
        records = tuple(latest.values())
    facts = tuple(r for r in records if r.get("metric") in spec.fact_metrics)
    return {**parsed, "records": records, "facts": facts}


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


def split_cells(line):
    """Découpe une ligne de tableau Markdown sur les `|` non échappés.

    Args:
        line: ligne de texte.

    Returns:
        La liste des cellules sans espaces de bord, ou `None` si la ligne n'est pas
        une ligne de tableau ou si elle ne sépare que des tirets.
    """
    if not line.startswith("|"):
        return None
    cells = [cell.strip() for cell in UNESCAPED_BAR.split(line.strip())[1:-1]]
    if cells and all(SEPARATOR_CELL.fullmatch(cell) for cell in cells):
        return None
    return cells


def markdown_rows(lines):
    """Parcourt les lignes de données des tableaux d'un document Markdown.

    Args:
        lines: liste des lignes du document, sans fin de ligne.

    Returns:
        Générateur de quadruplets (numéro de ligne, titre `##` courant ou `None`,
        cellules de l'en-tête du tableau, cellules de la ligne). Les blocs de code et
        les tableaux sans en-tête `Id` sont ignorés.
    """
    heading = header = None
    fenced = False
    for number, line in enumerate(lines, 1):
        if line.startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        if line.startswith("## "):
            heading, header = line[3:].strip(), None
            continue
        cells = split_cells(line)
        if cells and cells[0] == "Id":
            header = cells
        elif cells and header:
            yield number, heading, header, cells


def cell_of(header, cells, name):
    """Lit la cellule de la colonne `name`.

    Args:
        header: cellules de l'en-tête du tableau.
        cells: cellules de la ligne.
        name: nom de colonne, texte.

    Returns:
        Le texte de la cellule, ou `""` si la colonne ou la cellule manque.
    """
    if name not in header or header.index(name) >= len(cells):
        return ""
    return cells[header.index(name)]


def notion_record(header, cells, number, section, seen):
    """Construit l'enregistrement d'une ligne de `notions.md` ou la rejette.

    Args:
        header: cellules de l'en-tête du tableau.
        cells: cellules de la ligne.
        number: numéro de la ligne, entier à partir de 1.
        section: titre `##` de la section, ou `None`.
        seen: ensemble des identifiants déjà gardés, complété ici.

    Returns:
        Couple (enregistrement ou `None` si rejetée, liste de couples (nature, détail)).
    """
    if len(cells) != len(header):
        detail = f"{len(cells)} colonnes reçues, {len(header)} attendues"
        return None, [("field_count", detail)]
    by_name = dict(zip(header, cells))
    record = {key: by_name[name] for name, key in NOTION_COLUMNS.items()}
    if record["state"] not in NOTION_STATES:
        return None, [("unknown_state", f"état {record['state']!r} inconnu")]
    if record["id"] in seen:
        return None, [("duplicate_id", f"identifiant {record['id']!r} en double")]
    seen.add(record["id"])
    for key in NOTION_DATE_KEYS:
        record[key] = parse_date(record[key])[0]
    record.update(section=section, line=number)
    return record, []


def parse_notions(path, text):
    """Lit `notions.md` par nom de colonne.

    Args:
        path: `Path` du fichier.
        text: contenu du fichier.

    Returns:
        Dict des champs de `SourceResult`.

    Raises:
        SourceError: un tableau n'a pas l'une des colonnes de `NOTION_COLUMNS`.
    """
    seen, items = set(), []
    for number, section, header, cells in markdown_rows(text.split("\n")):
        missing = [name for name in NOTION_COLUMNS if name not in header]
        if missing:
            message = f"{path}:{number} : colonne {missing[0]!r} absente de l'en-tête"
            raise SourceError("header", message)
        items.append((number, *notion_record(header, cells, number, section, seen)))
    return tally(path.name, items)


def read_notions(path):
    """Lit `notions.md`.

    Args:
        path: chemin de `notions.md`.

    Returns:
        Le `SourceResult` `notions`.
    """
    return guarded("notions", path, parse_notions)


def parse_card(label, text, taken):
    """Lit une carte ou la rejette en entier.

    Args:
        label: nom `dossier/fichier` porté par les anomalies.
        text: contenu de la carte.
        taken: dict identifiant vers carte, pour les identifiants des cartes gardées.

    Returns:
        Couple (carte ou `None` si rejetée, liste de `model.Anomaly`). Un identifiant
        déjà pris est écarté avec une anomalie `duplicate_id`, la carte restant lue.
    """
    lines = text.split("\n")
    title = CARD_TITLE.match(lines[0].strip())
    if not title:
        detail = "première ligne sans « # Carte : <nom> »"
        return None, [Anomaly(label, 1, "missing_title", detail)]
    headings = [
        (number, line[3:].strip())
        for number, line in enumerate(lines, 1)
        if line.startswith("## ")
    ]
    for number, name in headings:
        if name not in TIERS:
            detail = f"palier {name!r} hors de {', '.join(TIERS)}"
            return None, [Anomaly(label, number, "unknown_tier", detail)]
    absent = [tier for tier in TIERS if tier not in {name for _, name in headings}]
    if absent:
        detail = f"palier absent : {', '.join(absent)}"
        return None, [Anomaly(label, 1, "missing_tier", detail)]
    tiers = {tier: [] for tier in TIERS}
    certifications, owners, anomalies = {}, {}, []
    for number, tier, header, cells in markdown_rows(lines):
        note_id = cell_of(header, cells, "Id")
        if tier not in tiers or not note_id:
            continue
        owner = owners.get(note_id) or taken.get(note_id)
        if owner:
            detail = f"identifiant {note_id!r} déjà pris par {owner}"
            anomalies.append(Anomaly(label, number, "duplicate_id", detail))
            continue
        owners[note_id] = label
        tiers[tier].append(note_id)
        certification = cell_of(header, cells, "Certifications")
        if certification:
            certifications[note_id] = certification
    declared, followed = 0, 0
    for line in lines:
        match = CARD_DECLARED.match(line.strip())
        if match:
            declared, followed = int(match[1]), int(match[2] or 0)
            break
    card = {
        "name": title[1].strip(),
        "tiers": tiers,
        "ids": [note_id for tier in TIERS for note_id in tiers[tier]],
        "declared": declared,
        "declared_followed": followed,
        "certifications": certifications,
    }
    taken.update(owners)
    return card, anomalies


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
        return SourceResult("cards", directory, "unavailable", str(error))
    return SourceResult(
        "cards",
        directory,
        "ok",
        None,
        tuple(records),
        (),
        tuple(anomalies),
        len(files),
        len(files) - len(records),
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
