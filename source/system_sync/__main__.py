"""Point d'entrée `python3 -m system_sync <commande>` : aiguille vers la commande."""

import sys

from system_sync import sync

COMMANDS = {"sync": sync.run_sync}
USAGE = "utilisation : python3 -m system_sync sync [--env CHEMIN] [--sortie CHEMIN]"


def main(argv):
    """Lance la commande nommée par `argv[0]` ; usage sur l'erreur standard sinon.

    Args:
        argv: arguments après le nom du module, liste de textes.

    Returns:
        Le code de sortie de la commande, ou 2 sans commande ou avec une inconnue.
    """
    if not argv or argv[0] not in COMMANDS:
        known = f" (reçue : {argv[0]!r})" if argv else ""
        print(f"commande absente ou inconnue{known}\n{USAGE}", file=sys.stderr)
        return 2
    return COMMANDS[argv[0]](argv[1:])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
