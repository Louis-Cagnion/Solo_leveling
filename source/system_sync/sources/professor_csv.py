"""Moteur de lecture des CSV de `/professor` (T3.d) : en-têtes, dates, enregistrements.

Lecture seule, sans réseau. Le moteur ne lève que `SourceError`, que
`professor.guarded` rend en `SourceResult` indisponible. Les lecteurs publics et le
tableau des sources vivent dans `professor.py`.
"""

import csv
import io
import re
from dataclasses import dataclass
from datetime import date
from operator import attrgetter

from system_sync.model import Anomaly

DATE_MIN = date(2020, 1, 1)
DATE_PATTERN = re.compile(r"(?:([0-9]{2})/)?([0-9]{2})/([0-9]{4})")


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
    """Description d'un CSV à en-tête dont une colonne `date` est lue en jj/mm/aaaa.

    Args:
        name: nom du résultat.
        columns: dict nom de colonne du fichier vers clé d'enregistrement, dans l'ordre
            des colonnes attendues.
        checks: tuple de `Check` appliqués après la date.
        unique: clés dont le triplet garde la dernière ligne, ou tuple vide.
        flag_suspect: `True` pour ajouter la clé `suspect` aux enregistrements.
        fact_metrics: valeurs de `metric` exposées en faits.
        optional: `True` si l'absence du fichier est un statut `absent`.
        ordered: `True` si les colonnes doivent suivre l'ordre de `columns`.
    """

    name: str
    columns: dict
    checks: tuple = ()
    unique: tuple = ()
    flag_suspect: bool = False
    fact_metrics: frozenset = frozenset()
    optional: bool = False
    ordered: bool = True


def parse_date(text, allow_month=True, latest=None):
    """Convertit `jj/mm/aaaa` en AAAA-MM-JJ et juge la date.

    Args:
        text: texte brut de la cellule, `jj/mm/aaaa` ou `mm/aaaa` attendu.
        allow_month: `False` pour refuser `mm/aaaa` (verdict `invalid`).
        latest: `date` de la borne haute permise, `None` pour aujourd'hui.

    Returns:
        Couple (date ISO ou `None`, verdict `ok`, `suspect` ou `invalid`) : `suspect`
        pour un mois sans jour ou une date hors de 2020-01-01 à `latest`.
    """
    match = DATE_PATTERN.fullmatch(text)
    if not match or (match[1] is None and not allow_month):
        return None, "invalid"
    day, month, year = match.groups()
    try:
        parsed = date(int(year), int(month), int(day or 1))
    except ValueError:
        return None, "invalid"
    if day is None:
        return None, "suspect"
    in_range = DATE_MIN <= parsed <= (latest or date.today())
    return parsed.isoformat(), "ok" if in_range else "suspect"


def tally(label, items, extra=()):
    """Sépare les enregistrements gardés des anomalies et compte lus et rejetés.

    Args:
        label: nom de fichier porté par les anomalies, texte.
        items: liste de triplets (ligne, enregistrement ou `None`, notes), où `notes`
            est une liste de couples (nature, détail).
        extra: `model.Anomaly` hors des lignes lues, qui ne comptent ni lues ni rejetées.

    Returns:
        Dict des champs `records`, `anomalies` (triées par ligne), `read` et `rejected`.
    """
    records = tuple(record for _, record, _ in items if record is not None)
    anomalies = [
        Anomaly(label, line, kind, detail)
        for line, _, notes in items
        for kind, detail in notes
    ]
    return {
        "records": records,
        "anomalies": tuple(sorted([*anomalies, *extra], key=attrgetter("line"))),
        "read": len(items),
        "rejected": len(items) - len(records),
    }


def csv_rows(path, text):
    """Découpe un CSV en lignes avec leur numéro de ligne physique.

    Args:
        path: `Path` du fichier, nommé dans le message d'erreur.
        text: contenu du CSV, en-tête compris.

    Returns:
        Liste de couples (numéro de la première ligne, liste de champs), lignes vides
        exclues.

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
    return rows


def header_problem(spec, header):
    """Compare l'en-tête d'un CSV aux colonnes attendues.

    Args:
        spec: `CsvSpec` de la source.
        header: liste des noms de la première ligne du fichier.

    Returns:
        Le texte de la première différence, ou `None` si l'en-tête est conforme.
    """
    names = list(spec.columns)
    for number, got in enumerate(header, 1):
        if spec.ordered:
            allowed = names[number - 1 : number]
        else:
            allowed = [name for name in names if name not in header[: number - 1]]
        if got not in allowed:
            expected = ", ".join(allowed) or "aucune colonne"
            return f"colonne {number} reçue {got!r}, attendue : {expected}"
    absent = [name for name in names if name not in header]
    if absent:
        return f"colonne {absent[0]!r} attendue, absente de l'en-tête"
    return None


def make_record(spec, keys, row, line):
    """Construit l'enregistrement d'une ligne de CSV ou la rejette.

    Args:
        spec: `CsvSpec` de la source.
        keys: clés d'enregistrement, dans l'ordre des colonnes du fichier.
        row: liste de champs de la ligne.
        line: numéro de la ligne physique, entier à partir de 1.

    Returns:
        Couple (enregistrement ou `None` si rejetée, liste de couples (nature, détail)).
    """
    if len(row) != len(keys):
        detail = f"{len(row)} champs reçus, {len(keys)} attendus"
        return None, [("field_count", detail)]
    record = dict(zip(keys, row))
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
    """Lit un CSV à en-tête : enregistrements, faits, anomalies et compteurs.

    Args:
        spec: `CsvSpec` de la source.
        path: `Path` du fichier.
        text: contenu du fichier.

    Returns:
        Dict des champs de `SourceResult`, la dernière ligne d'un triplet `unique`
        remplaçant les précédentes.

    Raises:
        SourceError: CSV illisible, sans ligne, ou dont l'en-tête n'est pas celui attendu.
    """
    rows = csv_rows(path, text)
    if not rows:
        raise SourceError("header", f"{path} : aucune ligne, en-tête absent")
    (head_line, header), data = rows[0], rows[1:]
    problem = header_problem(spec, header)
    if problem:
        raise SourceError("header", f"{path}:{head_line} : en-tête illisible, {problem}")
    keys = [spec.columns[name] for name in header]
    items = [(line, *make_record(spec, keys, row, line)) for line, row in data]
    parsed = tally(path.name, items)
    records = parsed["records"]
    if spec.unique:
        latest = {tuple(r[key] for key in spec.unique): r for r in records}
        records = tuple(latest.values())
    facts = tuple(r for r in records if r.get("metric") in spec.fact_metrics)
    return {**parsed, "records": records, "facts": facts}
