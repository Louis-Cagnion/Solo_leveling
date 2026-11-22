# Solo_leveling

Tableau de bord personnel de progression en programmation, dans l'esprit de *Solo Leveling* et de l'école 42 : niveaux, rangs et titres. Il s'appuie sur les données de suivi de `/professor` et sur l'API 42. Il distingue ce qui est observé, ce qui est estimé et ce qui reste insuffisant pour conclure. Une vitrine en ligne, sur GitHub Pages, en montre déjà la roue des domaines, les paliers, le statut et le réseau 3D des notions.

## Sommaire

- [État actuel](#état-actuel)
- [Fonctionnement](#fonctionnement)
- [Structure](#structure)
- [Configuration](#configuration)
- [Publication](#publication)
- [Tests](#tests)
- [Usage de l'IA](#usage-de-lia)
- [Contributeurs](#contributeurs)

## État actuel

- La vitrine est en ligne sur https://louis-cagnion.github.io/Solo_leveling/ : pour Louis seul, sur ordinateur, en français ; un téléphone ou une tablette est renvoyé vers `public/unsupported.html`, qui donne l'adresse à ouvrir sur ordinateur. Elle affiche un instantané des données de `/professor` (`public/data.js`), rafraîchi à la demande ; l'adresse `?demo` montre des données fictives pour juger les effets.
- Les maquettes de référence sont dans `mockups/`, non versionnées.
- Le paquet `system_sync` lit les sources : le suivi de `/professor` (cartes, notions, relations, événements, historique, en lecture seule) et l'API 42 (niveau, projets, achievements, par OAuth sur 127.0.0.1), avec le modèle de données et le validateur du fichier de sortie.
- Les règles de calcul, la commande `sync` et la page qu'elle alimente restent à écrire.

## Fonctionnement

Un script Python lit le suivi de `/professor` et l'API 42, applique les règles de `config/rules.toml`, puis écrit `data/state.js`, que la page affiche en local.

- **Sources** : cartes, notions, relations et événements du suivi, historique d'usage de l'IA, profil et projets de l'API 42, table XP épinglée.
- **Valeurs** : chacune est observée (lue telle quelle), estimée (issue d'une hypothèse) ou insuffisante (donnée manquante ou seuil de prudence non atteint), avec ses sources et sa raison.
- **Rangs et niveaux** : un rang par domaine (E à S, puis Nation), un niveau 42 et un niveau Système calibré sur le niveau 25.

Le détail se trouve dans `docs/design/conception.md`.

## Structure

```
config/rules.toml      règles : états, rangs, taux d'IA, table XP épinglée, titres
.env.example           variables à renseigner dans `.env` (ignoré par Git)
EXTERNAL.md            dépendance externe : API 42 (connexion, variables, requêtes, quotas)
source/system_sync/    paquet Python 3.12, bibliothèque standard seulement
  config.py            chargement et contrôle de `rules.toml` et de `.env`
  model.py, output.py  valeur statuée, anomalie ; schéma fermé et écriture atomique de `data/state.js`
  sources/             lecture des sources : professor*.py (suivi de `/professor`), api42*.py (API 42)
  rules/               règles de calcul, sans accès aux sources
public/                site publié tel quel par GitHub Pages : index.html, network.html,
                       404.html, favicon.svg, css/, js/, fonts/, vendor/, data.js (instantané)
tools/snapshot.py      génère public/data.js depuis le suivi de /professor (lecture seule)
tools/snapshot_mask.py masque des chaînes listées dans l'instantané
tools/sound_partials.py  génère public/js/sound-data.js depuis des enregistrements locaux
.github/workflows/pages.yml  déploie public/ à chaque push sur main qui le touche
tests/                 tests et fixtures fictives (system_sync en miroir de `source/`, public, tools)
docs/                  specification.md, plan.md, design/ (conception, implémentation, vitrine)
mockups/               maquettes de référence, non versionnées
```

## Configuration

Copier `.env.example` en `.env`, puis renseigner le dossier du suivi de `/professor` et le fichier `historique-ia.csv`. L'identifiant, le secret OAuth et le port de retour de l'API 42 sont facultatifs tant que l'API n'est pas utilisée.

- Le dossier du suivi doit exister.
- Le port, s'il est renseigné, est un entier de 1024 à 65535.
- Chaque ligne est `CLE=valeur` : une variable inconnue est refusée, et une valeur garde tout ce qui suit `=`, `#` compris.
- Le fichier `.env` ne doit jamais être versionné ; `chmod 600 .env` est conseillé.

## Publication

GitHub Actions déploie `public/` à chaque push sur `main` qui le touche (source de Pages : « GitHub Actions »). Le suivi de `/professor` change presque chaque jour : l'instantané se rafraîchit à la demande, jamais de lui-même.

1. `python3 -I tools/snapshot.py` : code 0, comptes affichés et « Masqué : N occurrence(s) » avec N au moins égal à 1. Le fichier local `tools/snapshot-mask.txt` (une chaîne par ligne, ignoré par Git) doit exister : sans lui, l'identifiant 42 de Louis serait publié.
2. `grep -rnE '/home/|@[a-z0-9-]+\.[a-z]{2,}' public --exclude-dir=vendor` sans ligne, puis `sh ~/claude_custom_commands/tools/verifier-confidentiel.sh public/data.js` sans sortie, puis `PYTHONPATH=source python3 -m unittest tests.public.test_site_static -v` vert.
3. Commit de `public/data.js` seul (« Vitrine : instantané des données du JJ/MM/AAAA »), puis push.
4. État du déploiement : `curl -s 'https://api.github.com/repos/Louis-Cagnion/Solo_leveling/actions/runs?per_page=1'` doit donner `completed` et `success` ; le cache de GitHub Pages peut garder l'ancienne version jusqu'à 10 minutes.

## Tests

Le paquet n'utilise que la bibliothèque standard de Python 3.12.

```
PYTHONPATH=source python3 -m unittest discover -s tests -t . -v
```

Les tests de la vitrine (`tests.public`, `tests.tools`) et ceux du squelette (`tests.test_architecture`, `tests.system_sync.test_config`) passent ; les tests de `tests/system_sync/` consacrés au modèle de données sont écrits d'avance et restent rouges jusqu'à leur implémentation.

## Usage de l'IA

Le cadrage, le plan, les recherches et le code sont produits avec Claude Code (mode `/best-practice`), sous la validation de Louis.

## Contributeurs

- Louis Cagnion
