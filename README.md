# Solo_leveling

Tableau de bord personnel de progression en programmation, dans l'esprit de *Solo Leveling* et de l'école 42 : niveaux, rangs et titres. Il s'appuie sur les données de suivi de `/professor` et sur l'API 42. Il distingue ce qui est observé, ce qui est estimé et ce qui reste insuffisant pour conclure.

## Sommaire

- [État actuel](#état-actuel)
- [Structure](#structure)
- [Configuration](#configuration)
- [Tests](#tests)
- [Usage de l'IA](#usage-de-lia)
- [Contributeurs](#contributeurs)

## État actuel

- Les maquettes de la page sont réalisées dans `mockups/`, non versionnées.
- Le squelette Python est posé : le paquet `system_sync` se charge, avec le chargeur de `config/rules.toml` et de `.env`.
- La synchronisation (lecture de `/professor`, de l'API 42 et des règles de calcul) et la page restent à écrire.

## Structure

```
config/rules.toml      règles : états, rangs, taux d'IA, table XP épinglée, titres
.env.example           variables à renseigner dans `.env` (ignoré par Git)
source/system_sync/    paquet Python 3.12, bibliothèque standard seulement
  config.py            chargement et contrôle de `rules.toml` et de `.env`
  sources/             lecture des sources de données
  rules/               règles de calcul, sans accès aux sources
tests/                 tests et fixtures fictives, en miroir de `source/`
docs/                  spécification, plan, conception et plan d'implémentation
mockups/               maquettes de la page
```

## Configuration

Copier `.env.example` en `.env`, puis renseigner le dossier du suivi de `/professor` et le fichier `historique-ia.csv`. L'identifiant, le secret OAuth et le port de retour de l'API 42 sont facultatifs tant que l'API n'est pas utilisée. Le fichier `.env` ne doit jamais être versionné.

## Tests

Le paquet n'utilise que la bibliothèque standard de Python 3.12.

```
PYTHONPATH=source python3 -m unittest discover -s tests -t . -v
```

## Usage de l'IA

Le cadrage, le plan, les recherches et le code sont produits avec Claude Code (mode `/best-practice`), sous la validation de Louis.

## Contributeurs

- Louis Cagnion
