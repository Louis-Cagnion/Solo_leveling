"""Garde commune des règles : aucune fonction publique ne lève sur une donnée inutilisable."""

import functools

GUARDED_ERRORS = (LookupError, TypeError, ValueError, AttributeError, OverflowError)


def never_raises(fallback):
    """Fabrique un décorateur qui remplace toute erreur de données par `fallback(erreur)`.

    Args:
        fallback: fonction à un argument (l'erreur attrapée) qui renvoie la valeur de repli.

    Returns:
        Le décorateur à poser sur une fonction publique.
    """

    def decorate(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except GUARDED_ERRORS as error:
                return fallback(error)

        return wrapper

    return decorate


def empty(error):
    """Valeur de repli `()`."""
    return ()
