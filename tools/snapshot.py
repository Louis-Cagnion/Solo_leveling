#!/usr/bin/env python3
"""Génère l'instantané `public/data.js` de la vitrine, depuis le suivi de /professor.

Lit en lecture seule cartes/*.md, notions.md et relations.csv du suivi, puis écrit
public/data.js sous la forme window.SYSTEME = {...}, sans aucun chemin absolu.

Usage : python3 -I tools/snapshot.py [--suivi DOSSIER] [--output FICHIER]
        [--mask FICHIER]
Masque : --mask, sinon tools/snapshot-mask.txt (local, ignoré par Git, facultatif) ; une
chaîne par ligne, remplacée par [masqué] dans la sortie ; # et lignes vides ignorés.
Suivi : --suivi, sinon PROFESSOR_SUIVI_DIR, sinon le suivi du dépôt des commandes.
Sortie : code 0 et comptes sur stdout ; code 1 et message sur stderr (cause et
chemin) si une source est illisible ou la sortie non inscriptible, l'ancien
fichier de sortie restant intact.
"""
import argparse
import csv
import io
import json
import os
import re
import sys
import tempfile
import unicodedata
from datetime import datetime
from pathlib import Path

# Sous `python3 -I`, le dossier du script n'est pas dans sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from snapshot_mask import DEFAULT_MASK, MaskError, mask_payload, read_mask  # noqa: E402

DEFAULT_SUIVI = Path.home() / "claude_custom_commands" / "references" / "professor" / "suivi"
ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "public" / "data.js"

# Ordre de preuve de methode.md (« États d'une notion ») ; « déclarée » ne prouve rien.
STATES = (
    ("découverte", "discovered"),
    ("en cours", "in-progress"),
    ("comprise", "understood"),
    ("appliquée", "applied"),
    ("retenue", "retained"),
    ("transférée", "transferred"),
    ("transcendée", "transcended"),
    ("déclarée", "declared"),
)
UNMET = ("non rencontrée", "unmet")
DECLARED = "déclarée"
PROOF_ORDER = [label for label, _ in STATES if label != DECLARED]
RANK_D_THRESHOLD = "comprise"
# État exigé de chaque notion d'une certification (« Certification prête », /professor).
CERT_THRESHOLD = "retenue"

TIERS = (
    ("Débutant", "beginner"),
    ("Intermédiaire", "intermediate"),
    ("Avancé", "advanced"),
    ("Transcendée", "transcended"),
)

RELATION_COLUMNS = ("date", "source", "relation", "cible", "statut", "limite", "preuve")
LINK_STATUSES = (
    ("demontree", "demonstrated", "démontrée"),
    ("reconnue", "recognized", "reconnue"),
    ("theorique", "theoretical", "théorique"),
)
# Lecture d'un lien depuis sa source (outgoing) et depuis sa cible (incoming).
LINK_KINDS = {
    "prerequis": {
        "label": "prérequis",
        "outgoing": "prérequis de",
        "incoming": "a pour prérequis",
    },
    "transfert": {
        "label": "transfert",
        "outgoing": "se transfère vers",
        "incoming": "reçoit un transfert de",
    },
    "complementaire": {
        "label": "complémentaire",
        "outgoing": "complémentaire de",
        "incoming": "complémentaire de",
    },
    "instance_de": {
        "label": "instance de",
        "outgoing": "instance de",
        "incoming": "a pour instance",
    },
    "analogue": {
        "label": "analogue",
        "outgoing": "analogue à",
        "incoming": "analogue à",
    },
}

# Valeurs de 42 hors /professor tant que l'API n'est pas branchée (docs/research/42-api.md).
LEVEL_42 = 12.44
LEVEL_42_REASON = "déclaré par Louis le 11/11/2026, API 42 non branchée"
XP_TABLE = ((12, 124_446), (13, 145_782))
XP_TABLE_SOURCE = "table data/experience_21.json de 42calculator"
LEVEL_TARGET = 25
# XP du niveau LEVEL_TARGET dans la table de 42calculator (docs/research/42-api.md).
XP_TARGET = 777756
ACHIEVEMENTS_REASON = "liste indisponible : API 42 non branchée"
NO_LEVEL_FACT = "aucun fait « niveau validé » enregistré dans /professor"

CARD_TITLE = re.compile(r"^# Carte : (?P<name>.+?)\s*$")
DECLARED_COUNT = re.compile(r"^- \*\*Notions\*\* : (?P<count>\d+)\b")
CERT_HEADER = re.compile(r"^- \*\*Certifications\*\*(?P<rest>.*)$")
CERT_ITEM = re.compile(r"^\s+- (?P<text>.+?)\s*$")
CERT_LABEL_END = re.compile(r", | : ")
UNESCAPED_PIPE = re.compile(r"(?<!\\)\|")
TABLE_RULE = re.compile(r"^\|(?:\s*:?-+:?\s*\|)+\s*$")
NOTION_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DATE = re.compile(r"^\d{2}/\d{2}/\d{4}$")


class DataError(Exception):
    """Source illisible ou sans contenu utile : la génération s'arrête."""


def statused(value, status, reason=None):
    """Construit une valeur statuée de docs/design/conception.md.

    Args:
        value: valeur affichable, None si status vaut "insufficient".
        status: "observed", "estimated" ou "insufficient".
        reason: texte français, obligatoire pour "insufficient".

    Returns:
        Dictionnaire {value, status, reason}.
    """
    if status == "insufficient" and (value is not None or not reason):
        raise ValueError(f"valeur insuffisante mal formée : {value!r}, raison {reason!r}")
    return {"value": value, "status": status, "reason": reason}


def anomaly(anomalies, file, line, reason, rejected=False):
    """Ajoute une anomalie {file, line, reason, rejected} à la liste anomalies."""
    anomalies.append({"file": file, "line": line, "reason": reason, "rejected": rejected})


def read_text(path):
    """Lit un fichier ordinaire en UTF-8 strict.

    Args:
        path: Path du fichier.

    Returns:
        Contenu du fichier.
    """
    if not path.exists():
        raise DataError(f"{path} : fichier absent")
    if not path.is_file():
        raise DataError(f"{path} : dossier ou fichier spécial, fichier ordinaire attendu")
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise DataError(f"{path} : encodage UTF-8 invalide ({error.reason})") from error
    except OSError as error:
        raise DataError(f"{path} : lecture impossible ({error.strerror})") from error


def split_row(line):
    """Découpe une ligne de tableau Markdown sur les | non échappés.

    Args:
        line: ligne qui commence et finit par |.

    Returns:
        Liste des cellules, espaces retirés et \\| rendus en |.
    """
    cells = UNESCAPED_PIPE.split(line.strip())[1:-1]
    return [cell.strip().replace("\\|", "|") for cell in cells]


def read_tables(lines, file, anomalies):
    """Lit les tableaux Markdown d'un fichier, par nom de colonne.

    Args:
        lines: lignes du fichier, sans fin de ligne.
        file: nom relatif du fichier, pour les anomalies.
        anomalies: liste complétée par les lignes rejetées.

    Returns:
        Liste de (titre de niveau 2 ou None, numéro de ligne, dict colonne -> cellule).
    """
    rows = []
    heading = None
    header = None
    for number, line in enumerate(lines, start=1):
        if line.startswith("## "):
            heading = line[3:].strip()
        if not line.startswith("|"):
            header = None
            continue
        if header is None:
            header = split_row(line)
            continue
        if TABLE_RULE.match(line):
            continue
        cells = split_row(line)
        if len(cells) != len(header):
            reason = f"{len(cells)} cellules au lieu de {len(header)}, ligne rejetée"
            anomaly(anomalies, file, number, reason, rejected=True)
            continue
        rows.append((heading, number, dict(zip(header, cells))))
    return rows


def parse_certifications(lines):
    """Extrait les certifications du texte libre de l'en-tête d'une carte.

    Args:
        lines: lignes de l'en-tête (avant le premier titre de niveau 2).

    Returns:
        (liste de {label, detail}, note de la ligne « Certifications » ou None si absente).
    """
    certifications = []
    note = None
    inside = False
    for line in lines:
        header = CERT_HEADER.match(line)
        if header:
            inside = True
            note = header.group("rest").strip(" ,:")
            continue
        item = CERT_ITEM.match(line)
        if not inside or not item:
            inside = inside and bool(item)
            continue
        text = item.group("text")
        if "non retenue" in text:
            continue
        label = CERT_LABEL_END.split(text, maxsplit=1)[0]
        certifications.append({"label": label, "detail": text})
    return certifications, note


def parse_card(path, anomalies):
    """Lit une carte de domaine : titre, paliers, notions et certifications.

    Args:
        path: Path de cartes/<id>.md.
        anomalies: liste complétée par les écarts de format.

    Returns:
        Dictionnaire {id, name, tiers, certifications, certificationNote, labels}.
    """
    file = f"cartes/{path.name}"
    lines = read_text(path).splitlines()
    title = CARD_TITLE.match(lines[0]) if lines else None
    if not title:
        raise DataError(f"{path} : ligne 1, titre « # Carte : <nom> » attendu")
    first_heading = next(
        (index for index, line in enumerate(lines) if line.startswith("## ")),
        len(lines),
    )
    certifications, note = parse_certifications(lines[:first_heading])
    if note is None:
        anomaly(anomalies, file, None, "ligne « Certifications » absente de l'en-tête")
    tier_codes = dict(TIERS)
    tiers = {code: [] for _, code in TIERS}
    labels = {}
    for heading, number, row in read_tables(lines, file, anomalies):
        notion_id = row.get("Id", "")
        if heading not in tier_codes:
            reason = f"notion hors palier connu (titre {heading!r}), ligne rejetée"
            anomaly(anomalies, file, number, reason, rejected=True)
            continue
        if not NOTION_ID.match(notion_id) or not row.get("Notion"):
            reason = f"identifiant ou nom invalide : {notion_id!r}, ligne rejetée"
            anomaly(anomalies, file, number, reason, rejected=True)
            continue
        tiers[tier_codes[heading]].append(notion_id)
        labels[notion_id] = row["Notion"]
    declared = next(
        (DECLARED_COUNT.match(line) for line in lines if DECLARED_COUNT.match(line)),
        None,
    )
    if declared and int(declared.group("count")) != len(labels):
        reason = f"en-tête : {declared.group('count')} notions annoncées, {len(labels)} lues"
        anomaly(anomalies, file, None, reason)
    return {
        "id": path.stem,
        "name": title.group("name"),
        "tiers": [
            {"code": code, "label": label, "notions": tiers[code]}
            for label, code in TIERS
        ],
        "certifications": certifications,
        "certificationNote": note,
        "labels": labels,
    }


def parse_notions(path, anomalies):
    """Lit les notions suivies de notions.md, par nom de colonne.

    Args:
        path: Path de notions.md.
        anomalies: liste complétée par les lignes rejetées.

    Returns:
        Dictionnaire id -> {label, state, objective, lastPractice, section}.
    """
    known_states = {label for label, _ in STATES}
    notions = {}
    lines = read_text(path).splitlines()
    for section, number, row in read_tables(lines, path.name, anomalies):
        notion_id = row.get("Id", "")
        state = row.get("État", "")
        if not NOTION_ID.match(notion_id) or not row.get("Notion"):
            reason = f"identifiant ou nom invalide : {notion_id!r}, ligne rejetée"
            anomaly(anomalies, path.name, number, reason, rejected=True)
            continue
        if state not in known_states:
            reason = f"état inconnu : {state!r}, ligne rejetée"
            anomaly(anomalies, path.name, number, reason, rejected=True)
            continue
        if notion_id in notions:
            reason = f"{notion_id} en double, cette ligne fait foi"
            anomaly(anomalies, path.name, number, reason)
        notions[notion_id] = {
            "label": row["Notion"],
            "state": state,
            "objective": row.get("Objectif") or None,
            "lastPractice": row.get("Dernière pratique") or None,
            "section": section,
        }
    if not notions:
        raise DataError(f"{path} : aucune notion lue")
    return notions


def parse_relations(path, anomalies):
    """Lit relations.csv par nom de colonne ; la dernière ligne d'un triplet fait foi.

    Args:
        path: Path de relations.csv.
        anomalies: liste complétée par les lignes rejetées.

    Returns:
        (liste des relations retenues, nombre de lignes lues, nombre de lignes rejetées).
    """
    reader = csv.reader(io.StringIO(read_text(path), newline=""))
    header = next(reader, None)
    if header is None:
        raise DataError(f"{path} : fichier vide, en-tête attendu")
    missing = [column for column in RELATION_COLUMNS if column not in header]
    if missing:
        raise DataError(f"{path} : ligne 1, colonnes absentes : {', '.join(missing)}")
    statuses = {source: code for source, code, _ in LINK_STATUSES}
    kept = {}
    read = 0
    rejected = 0
    for row in reader:
        if not row:
            continue
        read += 1
        line = reader.line_num
        if len(row) != len(header):
            reason = f"{len(row)} champs au lieu de {len(header)}, ligne rejetée"
            anomaly(anomalies, path.name, line, reason, rejected=True)
            rejected += 1
            continue
        fields = dict(zip(header, row))
        if fields["statut"] not in statuses:
            reason = f"statut inconnu : {fields['statut']!r}, ligne rejetée"
            anomaly(anomalies, path.name, line, reason, rejected=True)
            rejected += 1
            continue
        if not fields["source"] or not fields["cible"]:
            reason = "source ou cible vide, ligne rejetée"
            anomaly(anomalies, path.name, line, reason, rejected=True)
            rejected += 1
            continue
        if fields["relation"] not in LINK_KINDS:
            reason = f"type de lien inconnu : {fields['relation']!r}"
            anomaly(anomalies, path.name, line, reason)
        if not DATE.match(fields["date"]):
            anomaly(anomalies, path.name, line, f"date mal formée : {fields['date']!r}")
        key = (fields["source"], fields["relation"], fields["cible"])
        kept.pop(key, None)
        kept[key] = {
            "source": fields["source"],
            "target": fields["cible"],
            "kind": fields["relation"],
            "status": statuses[fields["statut"]],
            "date": fields["date"],
            "limit": fields["limite"] or None,
            "proof": fields["preuve"] or None,
            "line": line,
        }
    return list(kept.values()), read, rejected


def proof_index(state):
    """Rang d'un état dans l'ordre de preuve, -1 pour « déclarée » ou un état absent."""
    return PROOF_ORDER.index(state) if state in PROOF_ORDER else -1


def card_rank(card, tracked):
    """Calcule le rang d'une carte et ce qui manque pour le suivant (conception, « Rang »).

    Args:
        card: carte de parse_card.
        tracked: notions suivies de parse_notions.

    Returns:
        (valeur statuée du rang, dictionnaire du rang suivant).
    """
    all_ids = [nid for tier in card["tiers"] for nid in tier["notions"]]
    proven = [nid for nid in all_ids if proof_index(tracked.get(nid, {}).get("state")) >= 0]
    if not proven:
        reason = "aucune notion de la carte suivie (« déclarée » exclue)"
        rank = statused(None, "observed", reason)
        upcoming = {
            "rank": "E",
            "condition": "au moins une notion de la carte suivie (« déclarée » exclue)",
            "progress": statused(0, "observed"),
            "total": None,
            "missing": [],
        }
        return rank, upcoming
    beginner = card["tiers"][0]["notions"]
    threshold = proof_index(RANK_D_THRESHOLD)
    missing = [
        nid
        for nid in beginner
        if proof_index(tracked.get(nid, {}).get("state")) < threshold
    ]
    if beginner and not missing:
        reason = f"notions débutantes au moins « {RANK_D_THRESHOLD} », {NO_LEVEL_FACT}"
        upcoming = {
            "rank": "C",
            "condition": "fait « niveau = intermédiaire » (banc sans IA)",
            "progress": statused(None, "insufficient", NO_LEVEL_FACT),
            "total": None,
            "missing": [],
        }
        return statused("D", "estimated", reason), upcoming
    reason = f"{len(proven)} notions de la carte suivies (« déclarée » exclue)"
    upcoming = {
        "rank": "D",
        "condition": f"notions débutantes au moins « {RANK_D_THRESHOLD} », {NO_LEVEL_FACT}",
        "progress": statused(len(beginner) - len(missing), "estimated"),
        "total": len(beginner),
        "missing": missing,
    }
    return statused("E", "observed", reason), upcoming


def level_values(suivi):
    """Niveau 42, XP 42 et niveau Système, avec leurs statuts.

    Args:
        suivi: Path du dossier de suivi (présence de projets.csv).

    Returns:
        Dictionnaire {level42, xp42, systemLevel, levelTarget, xpTarget}.
    """
    (low_level, low_xp), (high_level, high_xp) = XP_TABLE
    if low_level <= LEVEL_42 <= high_level:
        xp = round(low_xp + (LEVEL_42 - low_level) * (high_xp - low_xp))
        reason = (
            f"interpolation linéaire dans la {XP_TABLE_SOURCE}, entre le niveau "
            f"{low_level} ({low_xp} XP) et le niveau {high_level} ({high_xp} XP)"
        )
        xp42 = statused(xp, "estimated", reason)
    else:
        xp42 = statused(None, "insufficient", "niveau hors de la table XP de la maquette")
    if (suivi / "projets.csv").exists():
        system = statused(None, "insufficient", "projets.csv présent : calcul hors maquette")
    else:
        system = statused(LEVEL_42, "estimated", "aucun projet perso ou pro enregistré")
    return {
        "level42": statused(LEVEL_42, "observed", LEVEL_42_REASON),
        "xp42": xp42,
        "systemLevel": system,
        "levelTarget": LEVEL_TARGET,
        "xpTarget": XP_TARGET,
    }


def titles(cards):
    """Titres du Système et achievements 42 (conception, « Titres »).

    Args:
        cards: cartes exportées, chacune avec sa valeur statuée « rank ».

    Returns:
        Liste de {id, name, scope, condition, progress, target, obtained}.
    """
    if any(card["rank"]["status"] == "insufficient" for card in cards):
        reason = "rang insuffisant sur au moins une carte"
        s_count = statused(None, "insufficient", reason)
        s_obtained = statused(None, "insufficient", reason)
    else:
        s_count = statused(sum(card["rank"]["value"] == "S" for card in cards), "observed")
        s_obtained = statused(s_count["value"] == len(cards), "observed")
    return [
        {
            "id": "answer-42",
            "name": "I AM THE ANSWER",
            "scope": "42",
            "condition": f"niveau 42 officiel au moins égal à {LEVEL_TARGET}",
            "progress": statused(LEVEL_42, "observed", LEVEL_42_REASON),
            "target": LEVEL_TARGET,
            "obtained": statused(LEVEL_42 >= LEVEL_TARGET, "observed"),
        },
        {
            "id": "answer-system",
            "name": "I AM THE ANSWER",
            "scope": "Système",
            "condition": "rang S sur toutes les cartes",
            "progress": s_count,
            "target": len(cards),
            "obtained": s_obtained,
        },
        {
            "id": "achievements-42",
            "name": "Achievements",
            "scope": "42",
            "condition": "obtenus et non obtenus, lus dans l'API de l'intranet",
            "progress": statused(None, "insufficient", ACHIEVEMENTS_REASON),
            "target": None,
            "obtained": statused(None, "insufficient", ACHIEVEMENTS_REASON),
        },
    ]


def rejected_rows(anomalies, prefix):
    """Nombre de lignes rejetées dans les fichiers dont le nom commence par prefix."""
    return sum(item["rejected"] for item in anomalies if item["file"].startswith(prefix))


def sort_key(name):
    """Clé de tri alphabétique française : accents ignorés, casse ignorée."""
    decomposed = unicodedata.normalize("NFD", name)
    return "".join(char for char in decomposed if not unicodedata.combining(char)).casefold()


def build(suivi):
    """Lit le suivi et assemble l'objet window.SYSTEME de la vitrine.

    Args:
        suivi: Path du dossier references/professor/suivi.

    Returns:
        (objet exporté, dictionnaire des comptes affichés sur stdout).
    """
    anomalies = []
    if not suivi.is_dir():
        raise DataError(f"{suivi} : dossier de suivi absent")
    if not (suivi / "cartes").is_dir():
        raise DataError(f"{suivi / 'cartes'} : dossier absent")
    card_paths = sorted((suivi / "cartes").glob("*.md"))
    if not card_paths:
        raise DataError(f"{suivi / 'cartes'} : aucune carte *.md")
    cards = sorted(
        (parse_card(path, anomalies) for path in card_paths),
        key=lambda card: sort_key(card["name"]),
    )
    tracked = parse_notions(suivi / "notions.md", anomalies)
    relations, relations_read, relations_rejected = parse_relations(
        suivi / "relations.csv",
        anomalies,
    )
    notions = {}
    for card in cards:
        for tier in card["tiers"]:
            for nid in tier["notions"]:
                if nid in notions:
                    file = f"cartes/{card['id']}.md"
                    anomaly(anomalies, file, None, f"{nid} déjà rangée sur une carte")
                    continue
                entry = tracked.get(nid, {})
                notions[nid] = {
                    "label": card["labels"][nid],
                    "card": card["id"],
                    "tier": tier["code"],
                    "state": entry.get("state", UNMET[0]),
                    "objective": entry.get("objective"),
                    "lastPractice": entry.get("lastPractice"),
                    "section": entry.get("section"),
                }
    card_names = {card["name"]: card["id"] for card in cards}
    for nid, entry in tracked.items():
        if nid not in notions:
            notions[nid] = {**entry, "card": None, "tier": None}
    for relation in relations:
        for end in ("source", "target"):
            if relation[end] not in notions:
                reason = f"{relation[end]} absent des cartes et de notions.md"
                anomaly(anomalies, "relations.csv", relation["line"], reason)
    exported_cards = []
    for card in cards:
        rank, upcoming = card_rank(card, tracked)
        all_ids = [nid for tier in card["tiers"] for nid in tier["notions"]]
        off_card = [
            nid
            for nid, entry in notions.items()
            if entry["card"] is None and card_names.get(entry["section"]) == card["id"]
        ]
        exported_cards.append({
            "id": card["id"],
            "name": card["name"],
            "tiers": card["tiers"],
            "certifications": [
                {
                    **certification,
                    "obtained": statused(
                        None,
                        "insufficient",
                        "aucun fait « certification » dans /professor",
                    ),
                }
                for certification in card["certifications"]
            ],
            "certificationNote": card["certificationNote"],
            "rank": rank,
            "nextRank": upcoming,
            "trackedCount": sum(nid in tracked for nid in all_ids),
            "offCard": off_card,
        })
    on_cards = sum(entry["card"] is not None for entry in notions.values())
    tracked_on_cards = sum(notions[nid]["card"] is not None for nid in tracked)
    counts = {
        "cards": len(exported_cards),
        "cardNotions": on_cards,
        "tracked": len(tracked),
        "trackedOnCards": tracked_on_cards,
        "trackedOffCards": len(tracked) - tracked_on_cards,
        "relationsRead": relations_read,
        "relationsRejected": relations_rejected,
        "relationsKept": len(relations),
    }
    data = {
        "meta": {
            "schema": "maquette-constellation-1",
            "generatedAt": datetime.now().astimezone().isoformat(timespec="minutes"),
        },
        "counts": counts,
        "sources": [
            {
                "label": "cartes/*.md",
                "status": "ok",
                "read": len(cards),
                "rejected": rejected_rows(anomalies, "cartes/"),
            },
            {
                "label": "notions.md",
                "status": "ok",
                "read": len(tracked),
                "rejected": rejected_rows(anomalies, "notions.md"),
            },
            {
                "label": "relations.csv",
                "status": "ok",
                "read": relations_read,
                "rejected": relations_rejected,
            },
            {"label": "API de l'intranet 42", "status": "unavailable", "read": None},
        ],
        "states": [{"label": label, "code": code} for label, code in (*STATES, UNMET)],
        "proofOrder": PROOF_ORDER,
        "rankDThreshold": RANK_D_THRESHOLD,
        "certThreshold": CERT_THRESHOLD,
        "linkStatuses": [{"code": code, "label": label} for _, code, label in LINK_STATUSES],
        "linkKinds": LINK_KINDS,
        "levels": level_values(suivi),
        "cards": exported_cards,
        "notions": notions,
        "relations": relations,
        "titles": titles(exported_cards),
        "anomalies": anomalies,
    }
    return data, counts


def write_atomically(path, text):
    """Écrit text dans path par un fichier temporaire du même dossier, puis un renommage."""
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(dir=path.parent, prefix=".data-", suffix=".js")
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            stream.write(text)
        os.chmod(temporary, 0o644)
        os.replace(temporary, path)
    except OSError:
        Path(temporary).unlink(missing_ok=True)
        raise


def parse_arguments(argv):
    """Lit la ligne de commande : --suivi, --output et --mask, avec leurs défauts."""
    parser = argparse.ArgumentParser(description="Génère l'instantané de la vitrine.")
    parser.add_argument(
        "--suivi",
        type=Path,
        default=Path(os.environ.get("PROFESSOR_SUIVI_DIR") or DEFAULT_SUIVI),
        help="dossier du suivi de /professor",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT,
        help="fichier data.js écrit",
    )
    parser.add_argument(
        "--mask",
        type=Path,
        default=None,
        help="chaînes à masquer, une par ligne (défaut : tools/snapshot-mask.txt)",
    )
    return parser.parse_args(argv)


def main(argv=None):
    """Génère l'instantané et affiche les comptes ; renvoie le code de sortie."""
    arguments = parse_arguments(argv)
    try:
        strings = read_mask(arguments.mask or DEFAULT_MASK, arguments.mask is not None)
        data, counts = build(arguments.suivi)
        payload, masked = mask_payload(json.dumps(data, ensure_ascii=False, indent=1), strings)
    except (DataError, MaskError) as error:
        print(f"snapshot : {error}", file=sys.stderr)
        return 1
    try:
        write_atomically(arguments.output, f"window.SYSTEME = {payload};\n")
    except OSError as error:
        message = f"snapshot : {arguments.output} : écriture impossible ({error.strerror})"
        print(message, file=sys.stderr)
        return 1
    for name, value in counts.items():
        print(f"{name} : {value}")
    print(f"anomalies : {len(data['anomalies'])}")
    print(f"Masqué : {masked} occurrence(s)")
    print(f"Écrit : {arguments.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
