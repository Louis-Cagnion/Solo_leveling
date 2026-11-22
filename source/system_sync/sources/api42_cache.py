"""Cache de l'API 42 (T4) : écriture atomique après une lecture `ok`, relecture en repli.

Le cache ne porte que le résultat en liste blanche, jamais de jeton ni de secret. Aucune
fonction publique ne lève : un cache absent, vide ou corrompu donne `unavailable`.
"""

import contextlib
import json
import logging
import os
import tempfile
from datetime import date

from system_sync import model
from system_sync.sources.api42_profile import (
    ITEM_KEYS,
    PROJECT_KEYS,
    Api42Result,
    preview,
)
from system_sync.sources.professor import SourceError, load_text

CACHE_VERSION = 1
UNAVAILABLE_REASON = "API 42 indisponible et aucun cache lisible"
LOGGER = logging.getLogger(__name__)


def cache_payload(result):
    """Rend la forme JSON du cache d'un résultat, sans anomalie ni compte.

    Args:
        result: `Api42Result` de statut `ok`.

    Returns:
        Dict JSON de version `CACHE_VERSION`, valeurs statuées en dict.
    """
    return {
        "version": CACHE_VERSION,
        "observed_at": result.observed_at,
        "level": result.level.to_dict(),
        "complete": result.complete.to_dict(),
        "projects": list(result.projects),
        "achievements": [
            {**item, "obtained": item["obtained"].to_dict()}
            for item in result.achievements
        ],
    }


def write_cache(path, payload):
    """Écrit le cache atomiquement (fichier temporaire 0600 puis `os.replace`).

    Args:
        path: `Path` du cache ; son dossier est créé au besoin.
        payload: dict JSON du cache, nombres finis seulement.

    Returns:
        `None` si écrit, sinon l'erreur qui nomme le chemin et la cause.
    """
    text = json.dumps(payload, ensure_ascii=False, allow_nan=False)
    temporary = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except OSError as error:
        if temporary is not None:
            with contextlib.suppress(OSError):
                os.unlink(temporary)
        return f"cache {path} non écrit : {error.strerror or error}"
    return None


class _CacheError(Exception):
    """Cache absent, vide, illisible ou de forme inattendue ; le message nomme le chemin."""


def _exact_keys(record, keys):
    """Vérifie qu'un élément du cache a exactement les clés attendues.

    Args:
        record: valeur lue dans le cache.
        keys: tuple des clés attendues.

    Returns:
        Une copie du dict.

    Raises:
        ValueError: autre chose qu'un dict, ou clés différentes.
    """
    if not isinstance(record, dict) or set(record) != set(keys):
        raise ValueError(f"élément {preview(record)} : clés {keys} attendues")
    return dict(record)


def _stated(data):
    """Reconstruit une `StatedValue` depuis sa forme JSON (invariants contrôlés).

    Args:
        data: dict de clés `value`, `status`, `sources`, `reason`, `reason_code`.

    Returns:
        La `StatedValue`.

    Raises:
        TypeError: autre chose qu'un dict de ces clés.
        model.ModelError: invariant violé.
    """
    if not isinstance(data, dict):
        raise TypeError(f"valeur statuée {preview(data)} : objet attendu")
    return model.StatedValue(**data)


def _load_cache(path):
    """Relit le cache écrit par `write_cache`.

    Args:
        path: `Path` du cache.

    Returns:
        Dict des champs de `Api42Result` qu'il porte.

    Raises:
        _CacheError: absent, vide, non UTF-8, JSON invalide ou de forme inattendue.
    """
    try:
        payload = json.loads(load_text(path))
    except SourceError as error:
        raise _CacheError(f"cache {error}") from None
    except json.JSONDecodeError as error:
        place = f"ligne {error.lineno}, colonne {error.colno}"
        raise _CacheError(f"cache {path} corrompu : JSON invalide ({place})") from None
    except (ValueError, RecursionError) as error:
        raise _CacheError(f"cache {path} inexploitable ({type(error).__name__})") from None
    if not isinstance(payload, dict) or payload.get("version") != CACHE_VERSION:
        raise _CacheError(f"cache {path} : objet de version {CACHE_VERSION} attendu")
    try:
        return {
            "observed_at": date.fromisoformat(payload["observed_at"]).isoformat(),
            "level": _stated(payload["level"]),
            "complete": _stated(payload["complete"]),
            "projects": tuple(_exact_keys(item, PROJECT_KEYS) for item in payload["projects"]),
            "achievements": tuple(
                {**_exact_keys(item, ITEM_KEYS), "obtained": _stated(item["obtained"])}
                for item in payload["achievements"]
            ),
        }
    except (KeyError, TypeError, ValueError) as error:
        cause = f"{type(error).__name__} {error}"
        raise _CacheError(f"cache {path} de forme inattendue : {cause}") from None


def fall_back(cache_path, cause):
    """Rend le cache relu après un échec, ou le résultat `unavailable`.

    Args:
        cache_path: `Path` du cache, jamais réécrit ici.
        cause: texte de l'échec, sans aucun secret.

    Returns:
        `Api42Result` `cache` ou `unavailable` ; `error` dit la cause puis l'issue du cache.
    """
    LOGGER.warning("API 42 : %s", cause)
    try:
        cached = _load_cache(cache_path)
    except _CacheError as error:
        LOGGER.warning("API 42 : %s", error)
        return Api42Result(
            status="unavailable",
            error=f"{cause} ; {error}",
            level=model.unmeasurable(UNAVAILABLE_REASON, "api_unavailable"),
            complete=model.unmeasurable(UNAVAILABLE_REASON, "api_unavailable"),
        )
    LOGGER.info("API 42 : cache du %s relu", cached["observed_at"])
    error = f"{cause} ; cache du {cached['observed_at']} relu"
    return Api42Result(status="cache", error=error, **cached)
