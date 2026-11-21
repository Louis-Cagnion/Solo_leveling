"""Masquage de chaînes dans la sortie de `tools/snapshot.py`.

Fichier de masquage : une chaîne par ligne, lignes vides et lignes en # ignorées,
correspondance exacte et sensible à la casse. Chaque occurrence devient [masqué].
"""
import json
import re
from pathlib import Path

DEFAULT_MASK = Path(__file__).resolve().parent / "snapshot-mask.txt"
MASKED = "[masqué]"


class MaskError(Exception):
    """Fichier de masquage illisible ou mal formé, ou sortie masquée invalide."""


def read_mask(path, required):
    """Lit les chaînes à masquer, une par ligne (# et lignes vides ignorés).

    Args:
        path: Path du fichier de masquage.
        required: True si le fichier est donné par --mask, False pour le défaut.

    Returns:
        Liste des chaînes, vide si le fichier par défaut est absent.
    """
    if not required and not path.exists():
        return []
    if not path.is_file():
        raise MaskError(f"{path} : absent, dossier ou fichier spécial")
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError as error:
        raise MaskError(f"{path} : encodage UTF-8 invalide ({error.reason})") from error
    except OSError as error:
        raise MaskError(f"{path} : lecture impossible ({error.strerror})") from error
    strings = []
    for number, line in enumerate(lines, start=1):
        if '"' in line or "\\" in line:
            raise MaskError(f"{path} : ligne {number}, guillemet ou barre oblique inverse")
        if line and not line.startswith("#"):
            strings.append(line)
    return strings


def mask_payload(payload, strings):
    """Remplace chaque occurrence des chaînes par [masqué] et revérifie le JSON.

    Args:
        payload: texte JSON de sortie.
        strings: chaînes à masquer, sans guillemet ni barre oblique inverse.

    Returns:
        (texte masqué, nombre d'occurrences masquées).
    """
    if not strings:
        return payload, 0
    pattern = "|".join(re.escape(text) for text in sorted(strings, key=len, reverse=True))
    masked, count = re.subn(pattern, MASKED, payload)
    try:
        json.loads(masked)
    except ValueError as error:
        raise MaskError(f"masquage : JSON illisible après masquage : {error}") from error
    return masked, count
