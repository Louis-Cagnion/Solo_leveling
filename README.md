# Solo_leveling

Tableau de bord personnel de progression en programmation, dans l'esprit de *Solo Leveling* et de l'école 42 : niveaux, rangs et titres. Il s'appuie sur les données de suivi de `/professor` et sur l'API 42. Il distingue ce qui est observé, ce qui est estimé et ce qui reste insuffisant pour conclure.

## Sommaire

- [État actuel](#état-actuel)
- [Fonctionnement](#fonctionnement)
- [Structure](#structure)
- [Configuration](#configuration)
- [Tests](#tests)
- [Usage de l'IA](#usage-de-lia)
- [Contributeurs](#contributeurs)

## État actuel

- Les maquettes de la page sont réalisées dans `mockups/`, non versionnées.
- Le squelette Python est posé : le paquet `system_sync` se charge, avec le chargeur de `config/rules.toml` et de `.env`.
- La synchronisation (lecture de `/professor`, de l'API 42 et des règles de calcul) et la page restent à écrire.

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
source/system_sync/    paquet Python 3.12, bibliothèque standard seulement
  config.py            chargement et contrôle de `rules.toml` et de `.env`
  sources/             lecture des sources de données
  rules/               règles de calcul, sans accès aux sources
tests/                 tests et fixtures fictives, en miroir de `source/`
docs/                  specification.md, plan.md, design/conception.md, design/implementation.md
mockups/               maquettes de la page
```

## Configuration

Copier `.env.example` en `.env`, puis renseigner le dossier du suivi de `/professor` et le fichier `historique-ia.csv`. L'identifiant, le secret OAuth et le port de retour de l'API 42 sont facultatifs tant que l'API n'est pas utilisée.

- Le dossier du suivi doit exister.
- Le port, s'il est renseigné, est un entier de 1024 à 65535.
- Chaque ligne est `CLE=valeur` : une variable inconnue est refusée, et une valeur garde tout ce qui suit `=`, `#` compris.
- Le fichier `.env` ne doit jamais être versionné ; `chmod 600 .env` est conseillé.

## Tests

Le paquet n'utilise que la bibliothèque standard de Python 3.12.

```
PYTHONPATH=source python3 -m unittest discover -s tests -t . -v
```

## Usage de l'IA

Le cadrage, le plan, les recherches et le code sont produits avec Claude Code (mode `/best-practice`), sous la validation de Louis.

## Contributeurs

- Louis Cagnion
