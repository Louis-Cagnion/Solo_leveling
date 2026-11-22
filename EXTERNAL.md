# Dépendances externes

`sync` lit le niveau, les projets et les achievements de l'utilisateur dans l'API de l'intranet 42. Ce fichier décrit la connexion, les requêtes envoyées et leurs limites. Aucune valeur réelle n'y figure : les identifiants vivent dans `.env`, ignoré par Git.

## API de l'intranet 42

### Connexion

- Flux OAuth 2 « authorization code » : chaque synchronisation ouvre la page de consentement dans le navigateur, puis un serveur local reçoit le code et l'échange contre un jeton.
- Application à créer sur l'intranet 42, avec l'URI de redirection `http://127.0.0.1:<port>/callback` (127.0.0.1, jamais `localhost`), où `<port>` est la valeur de `API42_CALLBACK_PORT`.
- Le serveur de retour n'écoute que sur 127.0.0.1 et accepte un seul retour dont le `state` est égal. Il sert chaque connexion dans son propre fil, avec un délai de 5 s par opération du socket : une préconnexion muette du navigateur ne bloque pas le vrai retour. Il attend 120 s au total, qu'aucune connexion lente ne prolonge, puis ferme le port et coupe les connexions encore ouvertes.
- Le jeton (valable 2 h) reste en mémoire : il n'est jamais écrit, ni journalisé, ni réutilisé d'une synchronisation à l'autre.

### Variables d'environnement

| Variable | Contenu |
|---|---|
| `API42_CLIENT_ID` | identifiant (UID) de l'application 42 |
| `API42_CLIENT_SECRET` | secret de l'application 42, jamais journalisé |
| `API42_CALLBACK_PORT` | port local du serveur de retour, de 1024 à 65535 |

Les trois sont facultatives : si l'une manque, `sync` relit le cache, sinon la source passe `unavailable` avec un message qui nomme chaque variable en cause.

### Requêtes types

| Requête | Contenu | Usage |
|---|---|---|
| `GET /oauth/authorize?client_id&redirect_uri&response_type=code&state` | ouverte dans le navigateur | consentement |
| `POST /oauth/token` | formulaire `grant_type=authorization_code`, `client_id`, `client_secret`, `code`, `redirect_uri` | jeton |
| `GET /v2/me` | en-tête `Authorization: Bearer <jeton>` | niveau du cursus 21, `projects_users`, `achievements` obtenus |
| `GET /v2/achievements?per_page=100&page=N` | idem, de la page 1 à la première incomplète | liste complète des achievements |

Base : `https://api.intra.42.fr`, TLS vérifié par le magasin de certificats du système ; aucune redirection n'est suivie.

### Limites et repli

- Débit : 2 requêtes par seconde au plus (limiteur), pour un quota observé de 1 200 par heure ; une synchronisation en envoie au moins 3 (jeton, profil, puis une page par centaine d'achievements).
- Chaque requête : délai de 10 s sur chaque opération du socket (connexion, puis chaque lecture), qui ne borne donc pas la durée totale d'une réponse lente ; corps de 5 Mo au plus ; liste complète lue sur 20 pages au plus ; 429 et 5xx repris 2 fois, après `Retry-After` plafonné à 10 s ; 401, 403 et 404 jamais repris.
- Seuls le niveau, les projets validés (`id`, `slug`, `name`, `final_mark`) et les achievements (`id`, `name`, `description`, obtenu ou non) sont gardés ; aucun champ personnel de `/v2/me`.
- Après une lecture réussie, le résultat est écrit atomiquement dans le cache JSON passé en `cache_path` (le dossier `data/` est ignoré par Git). En cas d'échec, le cache est relu (statut `cache`), sinon la source est `unavailable`.
- `/v2/achievements` refusé : seuls les achievements obtenus restent, avec la raison `full_list_unavailable` (« liste complète indisponible »).

### Code concerné

- `source/system_sync/sources/api42.py` : `authorization_url`, `RateLimiter`, `Api42Client`, `read_api42`.
- `source/system_sync/sources/api42_server.py` : `CallbackServer`, serveur de retour OAuth.
- `source/system_sync/sources/api42_profile.py` : extraction en liste blanche de `/v2/me` et de la liste complète (`Api42Result`).
- `source/system_sync/sources/api42_cache.py` : écriture et relecture du cache.

## Table XP de 42calculator

### Source

La table XP (niveau vers XP) vient du dépôt GPL-3.0 `lucas-ht/42calculator`, lue à distance et jamais copiée dans le dépôt. L'hôte est `raw.githubusercontent.com`, en HTTPS vérifié par le magasin de certificats du système, sans identifiant ni jeton.

L'adresse, le commit et le sha256 sont épinglés dans la section `[xp_table]` de `config/rules.toml` (`url`, `commit`, `sha256`) : changer de version de la table se fait en changeant ces trois valeurs ensemble.

### Requête type

| Requête | Contenu | Usage |
|---|---|---|
| `GET /lucas-ht/42calculator/<commit>/data/experience_21.json` | aucun en-tête particulier | table `{meta, levels: [{level, experience}]}` |

### Limites et repli

- Aucune redirection n'est suivie : toute réponse 3xx est un échec.
- Chaque requête : délai de 10 s sur chaque opération du socket (connexion, puis chaque lecture), qui ne borne donc pas la durée totale d'une réponse lente ; corps de 1 Mio au plus, refusé dès l'annonce de `Content-Length` ou à la lecture.
- Le sha256 des octets bruts reçus doit égaler l'épingle, puis la forme est validée : au moins 2 niveaux entiers, niveaux et XP strictement croissants.
- Après un succès, les octets reçus sont écrits atomiquement en 0600 dans le cache passé en `cache_path` (dossier `data/`, ignoré par Git). Après un échec (réseau, HTTP, taille, hash différent, forme), le cache est relu avec les mêmes contrôles, hash épinglé compris : statut `cache`, et `error` nomme la cause. Un hash différent ne réécrit jamais le cache.
- Sans cache valide, la source est `unavailable` et l'XP cible reste `unmeasurable` (code `xp_table_unavailable`).

### Code concerné

- `source/system_sync/sources/xp_table.py` : `load_xp_table`, `XpTable`, `XpTableResult`, `xp_for_level`, `level_for_xp`.
