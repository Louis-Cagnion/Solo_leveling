# Plan : interface de progression

Plan du projet décrit dans `docs/specification.md`, en suivant la chaîne en 8 étapes de `/best-practice`. Conformément au §12 de la spécification, aucune maquette ni implémentation ne démarre avant la validation des neuf points de la phase P1.

## Phases

| Phase | Contenu | Étape de la chaîne | Validation de Louis |
|---|---|---|---|
| P0 Recherche | Données `/professor`, système officiel de 42, mécaniques transposables | 1 | non |
| P1 Décisions | Les neuf points du §12, un par un | 1 | oui, point par point |
| P2 Conception | Modèle de données, règles de calcul, architecture | 2 | non |
| P3 Plan d'implémentation | Sous-tâches, fichiers, critères de réussite | 3 | oui |
| P4 Maquette | Opus `xhigh`, skill `impeccable`, rendu montré dans Chrome (§11) | avant 4 | oui, rendu visuel |
| P5 V1 puis pré-mortem | Tests, réalisation, revue, correction, finalisation | 4 à 8 | tests sur les données |

## Cadrage (étape 1)

### Risques

- **Doublon avec `/professor`** (§9) : l'interface lit les données de `/professor`, elle n'en collecte aucune de son côté. Tout manque se corrige dans `/professor`.
- **Niveaux arbitraires** (§2) : sans preuve suffisante, un score ment. Chaque valeur affichée porte un statut : observé, estimé ou insuffisant.
- **Calibration sur 42 non vérifiée** (§7.1) : la formule d'XP, la courbe des niveaux et la place du niveau 25 dans le cursus restent à établir sur des sources officielles.
- **Double comptage** (§6.1) : un même projet ou une même compétence ne doit pas rapporter deux fois de l'XP sans justification.
- **Autonomie surestimée** (§8) : ce qui a été réalisé avec l'IA n'est pas une preuve d'autonomie. `historique-ia.csv` distingue déjà `louis`, `mixte`, `ia` et `lecture`.
- **Gadget plutôt qu'outil** (§12.1) : un tableau de bord motivant, mais qui n'aide à aucune décision d'apprentissage, ne justifie pas le projet.
- **Propriété intellectuelle** : on s'inspire des mécaniques et de l'ambiance (fenêtres « Système », rangs E à S, titres), sans reprendre de logo, d'illustration, de police ni de visuel officiel de *Solo Leveling*.
- **Confidentialité** : le suivi mentionne des projets professionnels anonymisés. Si l'interface est un jour publiée, elle ne doit rien exposer de plus que ce qui est versionné.
- **AI Act** : il s'agit d'une auto-évaluation personnelle, sans décision sur un tiers, donc d'un risque minimal. Le niveau serait à revoir si les scores servaient un jour à un recrutement.

### Informations manquantes

- La table officielle de l'XP par niveau et l'XP par projet : seule l'API de l'intranet les donne, avec l'accès de Louis (`docs/research/42-system.md`).
- L'usage visé : interface locale seulement, ou déployée.

### Questions à trancher en P1 (§12)

1. Pertinence et valeur ajoutée pour l'apprentissage.
2. Fonctionnalités prioritaires et superflues.
3. Données de `/professor` à exploiter et améliorations nécessaires.
4. Critères d'évaluation des compétences et des projets.
5. Fonctionnement de l'expérience, des niveaux et des rangs.
6. Calibration par rapport au cursus de 42.
7. Conditions de déblocage de « I AM THE ANSWER » et des autres titres.
8. Architecture technique et modalités d'intégration (local ou déployé, pile, lecture des données).
9. Modalités de la maquette (Opus `xhigh`, `impeccable`).

## Arbre : P0 Recherche (feuilles validées 3/3)

Statuts : [ ] à faire, [~] en cours, [x] faite, [v] validée, [!] bloquée
Prochaine feuille prête : P1, point 1
Moniteur : opus 5.5/high, réévalué au point de contrôle P0

- P0 [nœud] : réunir les faits nécessaires aux décisions de P1 ; point de contrôle : chaque question de P1 dispose de ses faits ou d'un manque nommé (validé par le moniteur ; pas de `checker`, faute de code ou de test à jouer)
  - [v] P0.1 analyst (`docs/research/professor-data.md`) : inventaire des données de `/professor` ; fait par : sonnet/medium, chiffres vérifiés par sondage, un compte corrigé (6 cartes sans notion suivie, et non 7)
  - [v] P0.2 general-purpose (`docs/research/42-system.md`) : niveaux officiels de 42 ; fait par : sonnet/medium, une source relue par le moniteur
  - [v] P0.3 moniteur (`docs/research/mechanics.md`) : mécaniques transposables

P1 se déroule avec Louis, point par point. Les phases P2 à P5 se détaillent en feuilles une fois P1 close.

## Faits pour la suite

- Seules les métriques M1, M2 et M4 ont assez de mesures. Les autres seraient aujourd'hui affichées comme « insuffisant » (`docs/research/professor-data.md`).
- Projets, XP et part de l'IA par notion n'existent pas dans `/professor` : ils conditionnent l'XP personnelle, les rangs et les titres.
- Le niveau 25 n'est pas un jalon officiel de 42 : le titre reste un objectif personnel, à calibrer sur la table XP de l'API de l'intranet.
