# Données de `/professor` (P0.1)

Ce document fait l'inventaire du suivi de `/professor` au 11/11/2026 et de ce qu'il couvre de la spécification. Il prépare le point 3 de P1. Les mesures sont riches, mais récentes : 27 jours de données, dont près de la moitié dans un seul domaine (Linux). Les projets, l'XP et la part de l'IA par notion n'ont aucune donnée structurée.

Sources lues (dépôt `claude_custom_commands`, `references/`) : `professor/suivi/` (`evenements.csv`, `relations.csv`, `notions.md`, `techniques.md`, `sessions.md`, `a-venir.md`, `cartes/`), les règles de `professor/` (`methode.md`, `metriques.md`, `cartographie.md`, `outils.md`), ainsi que `best-practice/historique-ia.csv` et `objectifs-louis.md`.

## Volumes

| Fichier | Contenu | Volume |
|---|---|---|
| `evenements.csv` | Journal des mesures (`date,session,domaine,notion,metrique,valeur,contexte,forme_visuelle,preuve`) | 730 lignes, 153 notions, 15/10 au 11/11/2026 |
| `relations.csv` | Liens entre nœuds, de statut théorique, reconnu ou démontré | 77 liens |
| `notions.md` | Vue courante des notions, une section par domaine | 108 notions |
| `techniques.md` | Outils et techniques (VS Code, Git, shell, débogage) | 45 techniques, aucune « maîtrisée » |
| `cartes/*.md` | Périmètre de 16 domaines, en 4 paliers | 682 notions, dont 66 suivies ; 6 cartes sans aucune notion suivie |
| `historique-ia.csv` | Auteur du code par projet et par session (`ia`, `louis`, `mixte`, `lecture`) | 165 lignes, 24 projets |
| `sessions.md` | Journal narratif | 1 043 lignes, sans schéma stable : à ne pas parser |

## Couverture de la spécification

| Besoin | Couverture | Source |
|---|---|---|
| §2 Autonomie, rétention, évolution temporelle | couvert | M2, M1 et M4 de `evenements.csv` ; calendrier de rappels de `notions.md` |
| §2 Maîtrise, qualité du code, transfert, efficacité | partiel | M3 (21 mesures), M5 (10, en 6 formats), M6 (11), M7 (1) |
| §3 États | partiel | 8 états de `/professor` (`methode.md:158-167`) pour 5 dans la spécification ; « retenue » n'a encore aucune occurrence |
| §3 Prérequis, relations, transfert démontré | couvert | `relations.csv`, colonne `statut` |
| §3 Lacunes | partiel | Écart entre les cartes (682) et les notions suivies (66) |
| §4 Outils | partiel | `techniques.md` ; rien sur les outils de l'alternance |
| §5 Recommandations | partiel | Rappels dus et règles d'ordre (`methode.md:21-26`) ; aucune notion de valeur future |
| §6.1 Sources d'expérience | absent | Seules les XP prévues du cursus 42 figurent dans `objectifs-louis.md` |
| §8 Évaluation des projets | absent | Ni grille, ni note, ni difficulté par projet |
| §8 Part de l'IA | partiel | `historique-ia.csv`, au niveau projet ; les notions y sont en texte libre |
| Observé, estimé, insuffisant (§2) | règle seulement | Défini par `metriques.md:14` et `:65` (moins de 5 mesures ou de 3 sessions), porté par aucun champ : à calculer |

## Règles de calcul réutilisables

- Échelles M1 à M7, seuil « comprise » à M3 ≥ 4/5 (`metriques.md:20-45`).
- Intervalles de rappel J+1 à J+120 (`methode.md:180`) et planchers de durée avant « retenue » et « transcendée » (`metriques.md:77`).
- Niveaux de domaine : seuils de 80, 90 et 100 % (`methode.md:265-274`).
- Technique maîtrisée : 3 semaines et 3 observations (`outils.md:33`).

## Améliorations à décider côté `/professor` (point 3 de P1)

Ces points sont hors du périmètre de ce projet : ils se corrigent dans une session `/professor`, du plus bloquant au moins bloquant.

1. Un fichier de projets (difficulté, validation, note, part de l'IA), nécessaire aux §6.1 et §8.
2. Des identifiants de notions dans `historique-ia.csv`, pour rattacher l'autonomie aux notions.
3. Une correspondance entre les 5 états de la spécification et les 8 de `/professor`.
4. Des lignes CSV invalides à corriger : `relations.csv:40`, `historique-ia.csv:14-17,19,21` (virgules hors guillemets) et `:45` (date incomplète). Il y a aussi des `|` qui cassent les tableaux, à `notions.md:84` et `techniques.md:14,30,43,55,58`.
5. Des valeurs à normaliser : M2 (7 valeurs sans `N`), M5 (6 formats), M6 (dans `valeur` ou dans `contexte`). Deux libellés existent pour le domaine Linux.
6. Cinq identifiants d'événements absents de `notions.md`, plus une notion vide (`evenements.csv:491`).
