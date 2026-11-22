"""Lecture des tableaux Markdown de `/professor` (T3.d) : cartes et `notions.md`.

Lecture seule, sans réseau. Le module ne lève que `SourceError`, que
`professor.guarded` rend en `SourceResult` indisponible. Les lecteurs publics vivent
dans `professor.py`.
"""

import re
from datetime import date

from system_sync.model import Anomaly
from system_sync.sources.professor_csv import SourceError, parse_date, tally

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
# Colonne de date vers (clé, borne haute) : un rappel futur n'est jamais suspect.
NOTION_DATES = {
    "Dernière pratique": ("last_practice", None),
    "Prochain rappel": ("next_review", date.max),
}
DATE_NOTES = {
    "invalid": "{column} : date {raw!r} illisible, jj/mm/aaaa attendu",
    "suspect": "{column} : date {raw!r} hors de la plage permise",
}
# Cellules « Certifications » sans certification : vide ou tiret cadratin.
NO_CERTIFICATION = frozenset({"", "\N{EM DASH}"})

DATE_SHAPED = re.compile(r"[0-9]+(?:[/.\-][0-9]+)*")
UNESCAPED_BAR = re.compile(r"(?<!\\)\|")
SEPARATOR_CELL = re.compile(r":?-+:?")
CARD_TITLE = re.compile(r"# Carte : (.+)")
CARD_DECLARED = re.compile(r"- \*\*Notions\*\* : ([0-9]+)(?:, dont ([0-9]+) déjà)?")


def split_cells(line):
    """Découpe une ligne de tableau Markdown sur les `|` non échappés.

    Args:
        line: ligne de texte.

    Returns:
        La liste des cellules sans espaces de bord, ou `None` si la ligne n'est pas
        une ligne de tableau.
    """
    if not line.startswith("|"):
        return None
    return [cell.strip() for cell in UNESCAPED_BAR.split(line.strip())[1:-1]]


def is_separator(cells):
    """Dit si des cellules forment la ligne de tirets sous l'en-tête d'un tableau.

    Args:
        cells: liste de cellules de `split_cells`, ou `None`.

    Returns:
        `True` si la liste n'est pas vide et ne contient que des tirets.
    """
    return bool(cells) and all(SEPARATOR_CELL.fullmatch(cell) for cell in cells)


def markdown_rows(lines):
    """Parcourt les en-têtes et les lignes de données des tableaux d'un document.

    Args:
        lines: liste des lignes du document, sans fin de ligne.

    Returns:
        Générateur de quadruplets (numéro de ligne, titre `##` courant ou `None`,
        cellules de l'en-tête, cellules de la ligne). Une ligne d'en-tête (suivie de
        sa ligne de tirets) donne `None` pour les cellules de la ligne ; les lignes d'un
        tableau sans colonne `Id` et les blocs de code sont ignorés.
    """
    heading = header = None
    fenced = False
    for index, line in enumerate(lines):
        if line.startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        if line.startswith("## "):
            heading, header = line[3:].strip(), None
            continue
        cells = split_cells(line)
        if cells is None or is_separator(cells):
            continue
        following = lines[index + 1] if index + 1 < len(lines) else ""
        if is_separator(split_cells(following)):
            header = cells if "Id" in cells else None
            yield index + 1, heading, cells, None
        elif header:
            yield index + 1, heading, header, cells


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


def notion_dates(record):
    """Convertit en ISO les cellules de date d'un enregistrement de `notions.md`.

    Args:
        record: dict de `NOTION_COLUMNS`, modifié ici : une date devient ISO, `None` si
            invalide ou si le texte est libre (sans anomalie).

    Returns:
        Liste de couples (nature, détail) : `invalid_date` pour un texte de chiffres
        et de séparateurs qui n'est pas un jj/mm/aaaa valide, `suspect_date` pour une
        date hors de la plage permise.
    """
    notes = []
    for column, (key, latest) in NOTION_DATES.items():
        raw = record[key]
        iso, verdict = None, "free"
        if DATE_SHAPED.fullmatch(raw):
            iso, verdict = parse_date(raw, allow_month=False, latest=latest)
        record[key] = iso
        if verdict in DATE_NOTES:
            detail = DATE_NOTES[verdict].format(column=column, raw=raw)
            notes.append((f"{verdict}_date", detail))
    return notes


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
    notes = notion_dates(record)
    record.update(section=section, line=number)
    return record, notes


def parse_notions(path, text):
    """Lit `notions.md` par nom de colonne.

    Args:
        path: `Path` du fichier.
        text: contenu du fichier.

    Returns:
        Dict des champs de `SourceResult`. Un tableau sans colonne `Id` donne une
        anomalie `missing_header` à la ligne de son en-tête, sans compter de ligne lue.

    Raises:
        SourceError: un tableau à `Id` n'a pas l'une des colonnes de `NOTION_COLUMNS`,
            ou le fichier n'a aucun tableau à colonne `Id`.
    """
    seen, items, stray, tables = set(), [], [], 0
    for number, section, header, cells in markdown_rows(text.split("\n")):
        if cells is not None:
            items.append((number, *notion_record(header, cells, number, section, seen)))
        elif "Id" not in header:
            detail = f"colonne 'Id' absente de l'en-tête {header!r}"
            stray.append(Anomaly(path.name, number, "missing_header", detail))
        else:
            missing = [name for name in NOTION_COLUMNS if name not in header]
            if missing:
                message = f"{path}:{number} : colonne {missing[0]!r} absente de l'en-tête"
                raise SourceError("header", message)
            tables += 1
    if not tables:
        raise SourceError("header", f"{path} : aucun tableau à colonne 'Id' lisible")
    return tally(path.name, items, stray)


def check_structure(label, lines, rows):
    """Contrôle le titre, les paliers et les en-têtes de palier d'une carte.

    Args:
        label: nom `dossier/fichier` porté par l'anomalie.
        lines: liste des lignes de la carte.
        rows: liste des quadruplets de `markdown_rows` pour ces lignes.

    Returns:
        La `model.Anomaly` qui fait rejeter la carte, ou `None` : titre absent, palier
        inconnu ou manquant, ou tableau de palier sans colonne `Id`.
    """
    if not CARD_TITLE.match(lines[0].strip()):
        detail = "première ligne sans « # Carte : <nom> »"
        return Anomaly(label, 1, "missing_title", detail)
    headings = [
        (number, line[3:].strip())
        for number, line in enumerate(lines, 1)
        if line.startswith("## ")
    ]
    for number, name in headings:
        if name not in TIERS:
            detail = f"palier {name!r} hors de {', '.join(TIERS)}"
            return Anomaly(label, number, "unknown_tier", detail)
    absent = [tier for tier in TIERS if tier not in {name for _, name in headings}]
    if absent:
        return Anomaly(label, 1, "missing_tier", f"palier absent : {', '.join(absent)}")
    bad = [
        (number, tier, header)
        for number, tier, header, cells in rows
        if cells is None
           and tier
           and "Id" not in header
    ]
    if bad:
        number, tier, header = bad[0]
        detail = f"palier {tier!r} : colonne 'Id' absente de l'en-tête {header!r}"
        return Anomaly(label, number, "missing_header", detail)
    return None


def read_tier_rows(label, rows, taken):
    """Lit les lignes des tableaux de palier d'une carte.

    Args:
        label: nom `dossier/fichier` porté par les anomalies.
        rows: liste des quadruplets de `markdown_rows`.
        taken: dict identifiant vers carte, pour les identifiants des cartes gardées.

    Returns:
        Triplet (dict `tiers`, `certifications` et `has_certifications` de la carte,
        dict identifiant vers `label` des identifiants gardés, liste de `model.Anomaly`
        : `field_count` pour une ligne dont le nombre de cellules diffère de l'en-tête,
        `duplicate_id` pour un identifiant déjà pris).
    """
    tiers = {tier: [] for tier in TIERS}
    certifications, owners, anomalies = {}, {}, []
    has_column = False
    for number, tier, header, cells in rows:
        if tier not in tiers:
            continue
        if cells is None:
            has_column = has_column or "Certifications" in header
            continue
        if len(cells) != len(header):
            detail = f"{len(cells)} cellules reçues, {len(header)} attendues"
            anomalies.append(Anomaly(label, number, "field_count", detail))
        note_id = cell_of(header, cells, "Id")
        if not note_id:
            continue
        owner = owners.get(note_id) or taken.get(note_id)
        if owner:
            detail = f"identifiant {note_id!r} déjà pris par {owner}"
            anomalies.append(Anomaly(label, number, "duplicate_id", detail))
            continue
        owners[note_id] = label
        tiers[tier].append(note_id)
        certification = cell_of(header, cells, "Certifications")
        if certification not in NO_CERTIFICATION:
            certifications[note_id] = certification
    parts = {
        "tiers": tiers,
        "certifications": certifications,
        "has_certifications": has_column,
    }
    return parts, owners, anomalies


def declared_notions(lines):
    """Cherche la ligne `- **Notions** : N, dont M déjà suivies` d'une carte.

    Args:
        lines: liste des lignes de la carte.

    Returns:
        Triplet (numéro de ligne, compte déclaré, dont déjà suivies), ou `None`.
    """
    for number, line in enumerate(lines, 1):
        match = CARD_DECLARED.match(line.strip())
        if match:
            return number, int(match[1]), int(match[2] or 0)
    return None


def parse_card(label, text, taken):
    """Lit une carte ou la rejette en entier.

    Args:
        label: nom `dossier/fichier` porté par les anomalies.
        text: contenu de la carte.
        taken: dict identifiant vers carte, pour les identifiants des cartes gardées.

    Returns:
        Couple (carte ou `None` si rejetée, liste de `model.Anomaly`). Un identifiant
        déjà pris est écarté avec `duplicate_id`, et un compte déclaré différent du
        nombre d'identifiants lus donne `declared_mismatch`, la carte restant lue.
    """
    lines = text.split("\n")
    rows = list(markdown_rows(lines))
    rejection = check_structure(label, lines, rows)
    if rejection:
        return None, [rejection]
    parts, owners, anomalies = read_tier_rows(label, rows, taken)
    ids = [note_id for tier in TIERS for note_id in parts["tiers"][tier]]
    found = declared_notions(lines)
    number, declared, followed = found or (0, 0, 0)
    if found and declared != len(ids):
        detail = f"{declared} notions déclarées, {len(ids)} identifiants lus"
        anomalies.append(Anomaly(label, number, "declared_mismatch", detail))
    taken.update(owners)
    card = {
        "name": CARD_TITLE.match(lines[0].strip())[1].strip(),
        "ids": ids,
        "declared": declared,
        "declared_followed": followed,
        **parts,
    }
    return card, anomalies
