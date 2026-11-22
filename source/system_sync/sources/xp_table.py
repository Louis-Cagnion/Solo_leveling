"""Table XP de 42calculator (T5) : lecture épinglée, cache et interpolation (A17, A18, A22).

La table `{meta, levels: [{level, experience}]}` est téléchargée sans suivre de redirection,
avec un délai et un plafond de taille. Son sha256, calculé sur les octets bruts, doit égaler
l'épingle de `config/rules.toml` ; sa forme est validée sans nombre magique. Après un
succès, les octets reçus sont écrits atomiquement dans le cache ; après un échec, le cache
est relu avec les mêmes contrôles. Aucune fonction publique ne lève. Contrat :
`tests/system_sync/sources/test_xp_table.py` ; dépendance décrite dans `EXTERNAL.md`.
"""

import hashlib
import http.client
import json
import logging
import math
import os
import ssl
import stat
from dataclasses import dataclass
from fractions import Fraction
from urllib.error import HTTPError, URLError
from urllib.request import HTTPSHandler, Request, build_opener

from system_sync import model
from system_sync.interpolation import interpolate
from system_sync.sources.api42 import NoRedirect, digits, http_error
from system_sync.sources.api42_profile import is_integer, is_number, preview
from system_sync.sources.atomic_file import write_atomic

__all__ = [
    "XpTable",
    "XpTableResult",
    "level_for_xp",
    "load_xp_table",
    "xp_for_level",
]

DEFAULT_TIMEOUT = 10.0
DEFAULT_MAX_BYTES = 1_048_576
MIN_LEVELS = 2
HALF = Fraction(1, 2)
LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class XpTable:
    """Table XP validée.

    Args:
        levels: tuple de couples (niveau, XP) entiers, strictement croissants.
        url: URL épinglée d'où vient la table, texte.
        commit: commit épinglé de 42calculator, texte.
        sha256: empreinte hexadécimale des octets bruts, texte.
    """

    levels: tuple
    url: str
    commit: str
    sha256: str


@dataclass(frozen=True)
class XpTableResult:
    """Résultat de chargement de la table XP.

    Args:
        status: `ok` (réseau), `cache` (cache relu) ou `unavailable`.
        error: `None`, ou la cause avec l'URL, les deux hashes ou le chemin du cache.
        table: `XpTable`, ou `None` si `unavailable`.
    """

    status: str
    error: str | None = None
    table: XpTable | None = None


class _TableError(Exception):
    """Téléchargement, cache ou table refusés ; le message nomme l'élément et la cause."""


def _read_body(response, url, max_bytes):
    """Lit le corps d'une réponse en refusant toute taille au-delà du plafond.

    Args:
        response: réponse HTTP ouverte.
        url: URL lue, texte, pour les messages.
        max_bytes: entier, octets au plus.

    Returns:
        Les octets bruts reçus.

    Raises:
        _TableError: corps annoncé ou reçu au-delà de `max_bytes`.
    """
    declared = digits(response.headers.get("Content-Length"))
    if declared is not None and declared > max_bytes:
        raise _TableError(f"{url} : corps annoncé de {declared} octets, plafond {max_bytes}")
    body = response.read(max_bytes + 1)
    if len(body) > max_bytes:
        raise _TableError(f"{url} : corps de plus de {max_bytes} octets")
    return body


def _download(url, timeout, max_bytes):
    """Télécharge `url` en GET, TLS vérifié, sans suivre aucune redirection.

    Args:
        url: URL de la table, texte.
        timeout: secondes de délai de chaque opération du socket.
        max_bytes: entier, octets au plus.

    Returns:
        Les octets bruts reçus.

    Raises:
        _TableError: statut HTTP d'échec, réseau coupé, délai dépassé ou corps trop gros.
    """
    opener = build_opener(HTTPSHandler(context=ssl.create_default_context()), NoRedirect)
    try:
        with opener.open(Request(url), timeout=timeout) as response:
            return _read_body(response, url, max_bytes)
    except HTTPError as error:
        error.close()
        raise _TableError(http_error(url, error.code)) from None
    except URLError as error:
        if isinstance(error.reason, TimeoutError):
            cause = f"aucune réponse en {timeout} s"
        else:
            cause = f"connexion impossible ({error.reason})"
    except TimeoutError:
        cause = f"réponse non terminée en {timeout} s"
    except (OSError, http.client.HTTPException) as error:
        cause = f"réponse interrompue ({type(error).__name__})"
    except (ValueError, TypeError) as error:
        cause = f"URL {preview(url)} inutilisable ({type(error).__name__})"
    raise _TableError(f"{url} : {cause}")


def _parse_entry(index, entry):
    """Valide un élément de `levels`.

    Args:
        index: position de l'élément, entier.
        entry: valeur lue, de n'importe quel type.

    Returns:
        Le couple (niveau, XP).

    Raises:
        _TableError: autre chose qu'un objet, `level` ou `experience` absent ou non entier.
    """
    if not isinstance(entry, dict):
        raise _TableError(f"levels[{index}] : objet attendu, reçu {preview(entry)}")
    for key in ("level", "experience"):
        if not is_integer(entry.get(key)):
            received = preview(entry.get(key))
            raise _TableError(f"levels[{index}].{key} : entier attendu, reçu {received}")
    return entry["level"], entry["experience"]


def _parse_levels(data):
    """Valide la forme d'une table décodée.

    Args:
        data: JSON décodé, de n'importe quel type.

    Returns:
        Le tuple des couples (niveau, XP), strictement croissants dans les deux colonnes.

    Raises:
        _TableError: `levels` absent, trop court, mal formé ou non strictement croissant.
    """
    entries = data.get("levels") if isinstance(data, dict) else None
    if not isinstance(entries, list):
        raise _TableError(f"levels : liste attendue, reçu {preview(entries)}")
    if len(entries) < MIN_LEVELS:
        raise _TableError(f"levels : {MIN_LEVELS} niveaux au moins, {len(entries)} reçu(s)")
    pairs = tuple(_parse_entry(index, entry) for index, entry in enumerate(entries))
    for index, (before, after) in enumerate(zip(pairs, pairs[1:]), start=1):
        for column, key in enumerate(("level", "experience")):
            if after[column] <= before[column]:
                cause = f"{after[column]} après {before[column]}"
                raise _TableError(f"levels[{index}].{key} : non croissant ({cause})")
    return pairs


def _parse_table(body, url, commit, pinned):
    """Vérifie le hash des octets bruts puis la forme de la table.

    Args:
        body: octets bruts de la table.
        url: URL épinglée, texte.
        commit: commit épinglé, texte.
        pinned: sha256 hexadécimal épinglé, texte.

    Returns:
        La `XpTable`.

    Raises:
        _TableError: hash différent (les deux sont nommés), JSON invalide ou forme refusée.
    """
    digest = hashlib.sha256(body).hexdigest()
    if digest != pinned:
        raise _TableError(f"sha256 reçu {digest}, épinglé {pinned}")
    try:
        data = json.loads(body)
    except json.JSONDecodeError as error:
        place = f"ligne {error.lineno}, colonne {error.colno}"
        raise _TableError(f"JSON invalide ({place} : {error.msg})") from None
    except (ValueError, RecursionError) as error:
        raise _TableError(f"JSON inexploitable ({type(error).__name__})") from None
    return XpTable(_parse_levels(data), url, commit, digest)


def _read_cache(path, max_bytes):
    """Lit les octets bruts du cache sans bloquer sur un fichier non ordinaire.

    `load_text` décode et retire le BOM : il fausserait le hash, d'où cette lecture brute.

    Args:
        path: `Path` ou texte du cache.
        max_bytes: entier, octets au plus.

    Returns:
        Les octets bruts.

    Raises:
        _TableError: absent, non ordinaire, illisible, vide ou trop gros.
    """
    try:
        if not stat.S_ISREG(os.stat(path).st_mode):
            raise _TableError("ni fichier ordinaire ni lisible")
        with os.fdopen(os.open(path, os.O_RDONLY | os.O_NONBLOCK), "rb") as handle:
            data = handle.read(max_bytes + 1)
    except FileNotFoundError:
        raise _TableError("absent") from None
    except (TypeError, ValueError) as error:
        raise _TableError(f"chemin invalide ({type(error).__name__})") from None
    except OSError as error:
        raise _TableError(f"illisible ({error.strerror})") from None
    if not data:
        raise _TableError("vide")
    if len(data) > max_bytes:
        raise _TableError(f"plus de {max_bytes} octets")
    return data


def _write_cache(path, body):
    """Écrit les octets reçus atomiquement (voir `write_atomic`).

    Args:
        path: `Path` ou texte du cache ; son dossier est créé au besoin.
        body: octets bruts de la table.

    Returns:
        `None` si écrit, sinon l'erreur qui nomme le chemin et la cause.
    """
    error = write_atomic(path, body)
    return None if error is None else f"cache {error}"


def _fall_back(cause, cache_path, url, commit, pinned, max_bytes):
    """Relit le cache après un échec, en le revérifiant comme une réponse du réseau.

    Args:
        cause: texte de l'échec, avec l'URL ou les deux hashes.
        cache_path: `Path` ou texte du cache, jamais réécrit ici.
        url: URL épinglée, texte.
        commit: commit épinglé, texte.
        pinned: sha256 hexadécimal épinglé, texte.
        max_bytes: entier, octets au plus.

    Returns:
        `XpTableResult` `cache` ou `unavailable` ; `error` dit la cause puis l'issue du cache.
    """
    LOGGER.warning("table XP : %s", cause)
    try:
        table = _parse_table(_read_cache(cache_path, max_bytes), url, commit, pinned)
    except _TableError as error:
        return XpTableResult("unavailable", f"{cause} ; cache {cache_path} : {error}")
    return XpTableResult("cache", f"{cause} ; cache {cache_path} relu", table)


def load_xp_table(
    url,
    commit,
    sha256,
    cache_path,
    *,
    timeout=DEFAULT_TIMEOUT,
    max_bytes=DEFAULT_MAX_BYTES,
):
    """Charge la table XP épinglée, sinon relit le cache ; ne lève jamais.

    Args:
        url: URL de la table à l'adresse du commit épinglé, texte.
        commit: commit épinglé de 42calculator, texte.
        sha256: empreinte hexadécimale attendue des octets bruts, texte.
        cache_path: `Path` ou texte du cache, écrit en 0600 après un succès seulement.
        timeout: secondes de délai de chaque opération du socket, nombre positif.
        max_bytes: entier, octets au plus pour la réponse et pour le cache.

    Returns:
        `XpTableResult` : `ok` (cache écrit), `cache` (cache valide relu après un échec) ou
        `unavailable`.
    """
    try:
        body = _download(url, timeout, max_bytes)
    except _TableError as error:
        return _fall_back(str(error), cache_path, url, commit, sha256, max_bytes)
    try:
        table = _parse_table(body, url, commit, sha256)
    except _TableError as error:
        cause = f"table {url} : {error}"
        return _fall_back(cause, cache_path, url, commit, sha256, max_bytes)
    return XpTableResult("ok", _write_cache(cache_path, body), table)


def _refusal(result, value, code, noun):
    """Dit pourquoi une valeur ne se calcule pas, avant toute interpolation.

    Args:
        result: `XpTableResult`.
        value: niveau ou XP demandé, de n'importe quel type.
        code: code de raison d'une valeur qui n'est pas un nombre fini.
        noun: `niveau` ou `XP`, pour la raison.

    Returns:
        La `StatedValue` `unmeasurable`, ou `None` si le calcul est possible.
    """
    if result.table is None:
        reason = f"table XP indisponible : {result.error}"
        return model.unmeasurable(reason, "xp_table_unavailable")
    if not is_number(value):
        reason = f"{noun} {preview(value)} : nombre fini attendu"
        return model.unmeasurable(reason, code)
    return None


def _estimated(table, value, reason):
    """Crée une valeur estimée qui cite l'URL et le commit de la table.

    Args:
        table: `XpTable` utilisée.
        value: valeur calculée.
        reason: phrase française de l'interpolation.

    Returns:
        La `StatedValue` `estimated` de code `xp_interpolated`.
    """
    sources = (table.url, f"commit {table.commit}")
    return model.estimated(value, sources, reason, "xp_interpolated")


def xp_for_level(result, level):
    """XP d'un niveau décimal, interpolée entre les deux niveaux voisins.

    Args:
        result: `XpTableResult`.
        level: niveau, `int` ou `float` fini (tout autre type est refusé).

    Returns:
        `StatedValue` `estimated` de l'XP entière, arrondie à la moitié vers le haut ;
        `unmeasurable` (table indisponible ou niveau invalide) ; `insufficient` hors table.
    """
    refused = _refusal(result, level, "level_invalid", "niveau")
    if refused is not None:
        return refused
    found = interpolate(result.table.levels, level)
    if found is None:
        first, last = result.table.levels[0][0], result.table.levels[-1][0]
        reason = f"niveau {level} hors de la table (de {first} à {last})"
        return model.insufficient(reason, "level_out_of_table")
    reason = "XP interpolée linéairement entre deux niveaux de la table"
    return _estimated(result.table, math.floor(found + HALF), reason)


def level_for_xp(result, xp):
    """Niveau décimal d'une XP, fonction inverse de `xp_for_level`.

    Args:
        result: `XpTableResult`.
        xp: XP, `int` ou `float` fini (tout autre type est refusé).

    Returns:
        `StatedValue` `estimated` du niveau (float) ; `unmeasurable` (table indisponible ou
        XP invalide) ; `insufficient` hors table.
    """
    refused = _refusal(result, xp, "xp_invalid", "XP")
    if refused is not None:
        return refused
    points = tuple((points_xp, level) for level, points_xp in result.table.levels)
    found = interpolate(points, xp)
    if found is None:
        first, last = points[0][0], points[-1][0]
        reason = f"XP {xp} hors de la table (de {first} à {last})"
        return model.insufficient(reason, "xp_out_of_table")
    reason = "niveau interpolé linéairement entre deux niveaux de la table"
    return _estimated(result.table, float(found), reason)
