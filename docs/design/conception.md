# Conception (P2)

Ce document est la conception de la V1, tirée du rapport de P2.1 (11/11/2026) et des décisions de P1 (`docs/plan.md`). Un script Python lit `/professor` et l'API 42, applique des règles configurables, et écrit un fichier de données que la page affiche. La principale limite tient aux données : `/professor` ne permet aujourd'hui de calculer que les rangs E et D. Les rangs suivants demandent un fait « niveau validé » que `/professor` n'enregistre pas encore.

## Modèle de données

### Valeur statuée

Toute valeur prend la forme `{valeur, statut, sources[], raison}` :
- **`observe`** : la valeur est lue telle quelle dans une source.
- **`estime`** : la valeur sort d'une règle qui contient une hypothèse (interpolation, table tierce, équivalence, taux de l'IA, calibration, règle du rang B).
- **`insuffisant`** : une entrée manque ou est invalide, ou les seuils de prudence ne sont pas atteints (`metriques.md:65`). La valeur vaut alors `null` et `raison` est obligatoire.

### Fichier produit : `data/etat.js`

Le fichier contient `window.SYSTEME = {...}`, du JSON validé, pour que la page s'ouvre en `file://` sans serveur.

| Entité | Contenu |
|---|---|
| `meta` | version du schéma, date de génération, empreinte des règles |
| `sources[]` | état de chaque source (ok, cache, indisponible), lignes lues et rejetées |
| `niveau42` | niveau (observé), XP (estimée), projets 42 validés et leur XP de base |
| `systeme` | XP, niveau, détail par origine, calibration |
| `trajectoire[]` | une ligne par synchronisation : date, niveau 42, niveau Système |
| `cartes[]` | paliers, notions, certifications, rang, manques pour le rang suivant |
| `notions{}` | état, objectif, carte et palier, dernière pratique |
| `relations[]` | liens de `relations.csv` ; la dernière ligne d'un triplet fait foi |
| `projets[]` | projets perso et pro, équivalent 42, facteur de l'IA, XP |
| `titres[]` | titres du Système et achievements 42, obtenus ou non, avec leur progression |
| `anomalies[]` | lignes rejetées ou suspectes, avec `fichier:ligne` |

Trois règles s'appliquent à l'export :
- de `/v2/me`, seuls le niveau, les projets et les achievements sont exportés (liste blanche) ;
- la colonne « Solidité » de `notions.md`, en texte libre, n'est pas exportée ;
- les tableaux Markdown se lisent par nom de colonne et se découpent sur les `|` non échappés.

### Règles configurables : `config/regles.toml`

Le fichier est versionné et commenté. On y trouve l'ordre des états, les conditions des rangs, les taux de la part de l'IA (`louis` 1,0, `mixte` 0,5, `ia` 0,0, `lecture` ignorée), la table XP épinglée (URL et sha256), les paramètres de calibration et les titres. Les types de rang et de titre sont des données, sans `if` par instance. Les chemins et les secrets vont dans `.env`, ignoré par Git.

## Règles de calcul

### Rang d'un domaine

| Rang | Condition | Statut |
|---|---|---|
| E | au moins une notion de la carte suivie (« déclarée » exclue) | observé |
| D | fait `niveau = débutant`, sinon toutes les notions débutantes au moins « comprises » (`methode.md:262`) | observé ou estimé |
| C | fait `niveau = intermédiaire` (banc sans IA, `methode.md:263-274`) | observé |
| B | C, plus la moitié des notions avancées au moins « appliquées » | estimé |
| A, S | fait `niveau = avancé` ou `niveau = transcendée` | observé |
| Nation | S, et chaque certification retenue de la carte obtenue, ou aucune certification retenue | observé |

Le rang affiché est le plus haut dont toutes les conditions précédentes sont remplies. Une carte sans notion suivie n'a « aucun rang », ce qui n'est pas « insuffisant ». Un niveau validé ne retombe jamais (`methode.md:253`).

Sur les données du 11/11/2026, 10 cartes sont au rang E et 6 n'ont aucun rang. Aucune carte n'atteint D : SQL a 5 notions débutantes sur 8 au moins « comprises », Docker 4 sur 8.

### XP et niveau 42

- Le niveau `cursus_users[21].level` de l'API est observé.
- L'XP est estimée par interpolation linéaire dans la table de 42calculator : 12,44 donne 133 834 XP.
- L'XP d'un projet est l'XP de base (`difficulty`) lue par l'API. L'écart avec l'XP déduite du niveau, dû à la note et aux bonus, s'affiche comme « écart non expliqué ».

### XP et niveau « Système »

- XP_sys = XP_42 + la somme, pour chaque projet perso ou pro livré, de l'XP de base de son équivalent 42 multipliée par le facteur de l'IA.
- Le facteur de l'IA d'un projet est la moyenne des taux de ses lignes d'`historique-ia.csv`. Un projet sans aucune ligne a un facteur insuffisant et ne compte pas.
- Un projet perso qui reprend un projet 42 est rejeté, pour éviter un double comptage.
- **Calibration** : une courbe par morceaux, continue et croissante. Elle part d'un point (date, XP_sys, niveau affiché, XP_42) et vise T(25) = 777 756. Si le rythme r (XP perso par XP de 42) se maintient, les deux jauges atteignent 25 ensemble. r s'estime à partir de 3 projets et de 90 jours ; avant ce seuil, la calibration est « provisoire ». Recalibrer change la pente de la courbe, jamais la valeur affichée.

### Titres

- **« I AM THE ANSWER » (42)** : niveau 42 au moins égal à 25.
- **« I AM THE ANSWER » (Système)** : rang S sur toutes les cartes. Si une carte est au rang insuffisant, le titre est « insuffisant », et non « non obtenu ».
- **Achievements 42** : les obtenus viennent de `/v2/me`. La liste complète passe par `/v2/achievements`, qui n'est pas confirmé ; à défaut, la page indique « liste complète indisponible ».

### Réseau de compétences

- **Nœuds** : 682 notions de carte, 42 notions suivies hors carte, les cartes, les paliers et les certifications.
- **Arêtes** : l'appartenance d'une notion à un palier et d'un palier à une carte, plus les liens de `relations.csv`, de statut théorique, reconnu ou démontré.
- **États** : les 8 états de `/professor` tels quels, plus « non rencontrée » pour une notion de carte que le suivi ne contient pas.
- **Points mis en évidence** : un prérequis fragile (prérequis sous « comprise » alors que sa cible est au moins « comprise ») et les manques pour le rang suivant.

## Données à ajouter dans `/professor`

Ce dépôt ne crée aucun suivi propre (§9). Ces ajouts se font dans une session `/professor` (T0).

| Besoin | Format proposé | Sans cette donnée |
|---|---|---|
| Niveaux validés | fait `niveau` dans `evenements.csv` | D estimé ; C, A, S jamais attribués |
| Certifications retenues, par palier | ligne `- **Codes** : CLA (intermédiaire), CLP (avancé)` en tête de carte | Nation insuffisant partout |
| Certifications obtenues | fait `certification` | Nation insuffisant |
| Projets perso et pro | `suivi/projets.csv` : `id,cadre,statut,date,equivalent_42,justification` | Système = 42 seul |
| Clés de projet stables | une seule graphie par projet dans `historique-ia.csv` | facteur insuffisant pour les clés ambiguës |
| Lignes invalides | `relations.csv:40`, `historique-ia.csv:14-17,19,21,45` | lignes rejetées et listées en anomalies |

## Architecture

```
config/regles.toml     règles (versionné)
.env.example           chemins et identifiants OAuth à remplir (versionné)
source/synchro/        package Python 3.12, bibliothèque standard seulement
  sources/             professor.py, api42.py, table_xp.py
  modele.py            valeur statuée, anomalies
  regles/              rangs, xp, calibration, titres, reseau (fonctions pures)
  sortie.py            validation du schéma, écriture atomique
public/                index.html, css/, js/ : rendu seul, textContent, aucune ressource externe
data/                  généré, ignoré par Git (etat.js, historique/, cache/)
tests/                 fixtures fictives, en miroir de source/
```

- **Dépendances** : sources, puis modèle, puis règles, puis sortie. Les règles n'importent aucune source : elles se testent sur des fixtures.
- **Python plutôt que Node** : la bibliothèque standard suffit (`csv`, `tomllib`, `http.server`, `urllib`), c'est le langage des outils de `/professor`, et Louis le connaît mieux.
- **OAuth** : flux authorization code avec `state`, serveur de retour borné sur 127.0.0.1, jeton gardé en mémoire, secret dans `.env`.
- **Table XP** : lue à distance, épinglée sur un commit avec son sha256, puis mise en cache. Rien n'est redistribué et aucun code sous GPL n'est repris.

## Découpage de la V1

| # | Sous-tâche | Dépend de |
|---|---|---|
| T0 | Formats de `/professor` (session `/professor`, hors dépôt) | - |
| T1 | Squelette, `.gitignore` (`.env`, `data/`), `.env.example`, `regles.toml` | P2 |
| T2 | Modèle, schéma de sortie et validateur | T1 |
| T3 | Lecteurs de `/professor` | T2 |
| T4 | Client de l'API 42 (OAuth, cache, 2 requêtes par seconde) | T2 |
| T5 | Table XP et interpolation | T2 |
| T6 | Rangs | T3 |
| T7 | XP Système et calibration | T3, T4, T5 |
| T8 | Titres | T4, T6 |
| T9 | Réseau | T3 |
| T10 | Commande `sync` | T6 à T9 |
| T11 | Page, d'après la maquette retenue | T2, P4 |
| T12 | Vérification de bout en bout | T10, T11 |

Hors V1 : statistiques M1 à M11, recommandations, techniques, transfert par notion, historique recalculé des rangs, formule de note des projets 42, jeton de rafraîchissement, déploiement.

## Risques

- **Motivation** : pendant longtemps, la V1 affichera surtout le rang E et « aucun rang ». C'est honnête, mais peu gratifiant tant que les bancs de `/professor` ne sont pas enregistrés.
- **Table XP tierce** : T(25) vient d'une source non confirmée.
- **Champs de l'API** : ils viennent d'une copie de 2021 et restent à confirmer avec le jeton de Louis. Sans `marked_at`, la trajectoire démarre à la première synchronisation.
- **Ordre des états** : dans `/professor`, « transférée » passe au-dessus de « retenue » alors que leurs preuves sont indépendantes (`methode.md:156`).
- **Cartes récentes** : toutes datées du 11/11/2026, leur format peut encore changer ; la commande `verifier` doit le détecter.
