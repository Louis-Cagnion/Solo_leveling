# API de l'intranet 42 et règles de calcul (P0.4)

Ce document décrit ce qu'il faut pour lire le niveau, les projets et les achievements de Louis, et la source de repli pour calculer l'XP (point 3 de P1, 11/11/2026). La documentation officielle de l'API n'est lisible qu'une fois connecté : les faits ci-dessous viennent d'une copie communautaire de 2021 et du code de 42calculator. Ils sont à confirmer avec le jeton de Louis.

## Brancher l'API (étapes de Louis)

1. Créer une application sur `profile.intra.42.fr/oauth/applications`, avec une redirection locale (`http://127.0.0.1:<port>/callback`, l'adresse exacte que le client écoute et envoie, port de `API42_CALLBACK_PORT`). Garder l'UID et le secret dans un `.env` ignoré par Git.
2. Utiliser le flux authorization code (`/oauth/authorize`, puis `/oauth/token`). Le flux client credentials n'est lié à aucun utilisateur.
3. Appeler `GET /v2/me`, qui donne `cursus_users[]` (cursus 21, `level` décimal), `projects_users[]` (`final_mark`, `validated?`, `status`) et `achievements[]` (achievements obtenus).
4. Tester `GET /v2/achievements?per_page=100` pour la liste complète, et donc les achievements non obtenus. Ni son existence ni son scope ne sont établis.

Les limites observées sont de 2 requêtes par seconde et 1 200 par heure, avec un jeton valable 2 h et des pages de 100 éléments au plus. Une synchronisation ponctuelle reste très en dessous.

## Source de repli : 42calculator

Il s'agit du dépôt `github.com/lucas-ht/42calculator`, sous licence GPL-3.0, mis à jour le 26/10/2026.

| Fichier | Contenu | Statut |
|---|---|---|
| `data/experience_21.json` | Table niveau vers XP, niveaux 0 à 30 : 12 = 124 446, 13 = 145 782, 17 = 263 508, 21 = 457 632, 25 = 777 756 | relu par le moniteur ; origine non déclarée |
| `data/projects_21.json` | 393 projets, XP de base dans `difficulty` (Libft 462, alternance RNCP6 150 000), récupérés par l'API | constaté dans le script `fetch_projects.py` ; ni bonus ni formule de note |
| `data/rncp_21.json` | Conditions RNCP 6 et 7 | revu le 26/10/2026 d'après l'intranet, non relu |

À trancher avant toute réutilisation : la GPL-3.0 impose sa licence au code qui reprend celui du dépôt. Lire les fichiers de données à distance, ou les copier avec leur source, est à décider en P2.

## Calcul de l'XP

- XP actuelle estimée, en interpolation linéaire entre deux niveaux : 12,44 donne environ 133 834 XP. La règle d'interpolation n'est pas documentée.
- La note (jusqu'à 125) et les bonus modifient l'XP réelle d'un projet, mais leur formule n'est publiée nulle part. À recouper avec les `projects_users` validés de l'API.
