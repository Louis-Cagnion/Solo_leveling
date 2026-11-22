"""Écriture atomique d'un fichier (T5.d) : temporaire 0600 du même dossier, puis remplacement.

Module feuille, partagé par les caches de l'API 42 et de la table XP. Aucune fonction
publique ne lève.
"""

import contextlib
import os
import tempfile
from pathlib import Path


def write_atomic(path, data):
    """Écrit des octets atomiquement, sans jamais lever ni laisser de temporaire.

    Le dossier parent est créé au besoin ; le fichier temporaire est écrit en 0600 puis
    `fsync`, et remplace la cible d'un bloc (un lien symbolique en cible est remplacé, sa
    destination reste intacte). En cas d'échec, l'ancien fichier reste intact.

    Args:
        path: `str` ou `Path` de la cible.
        data: octets à écrire.

    Returns:
        `None` si écrit, sinon un texte qui nomme le chemin et la cause.
    """
    temporary = None
    try:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary = tempfile.mkstemp(dir=target.parent, prefix=f".{target.name}.")
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
        temporary = None
    except OSError as error:
        return f"{path} non écrit : {error.strerror or error}"
    except (TypeError, ValueError) as error:
        return f"{path} non écrit : valeur invalide ({type(error).__name__} : {error})"
    finally:
        if temporary is not None:
            with contextlib.suppress(OSError):
                os.unlink(temporary)
    return None
