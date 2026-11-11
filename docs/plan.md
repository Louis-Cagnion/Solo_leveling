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
- Le lieu d'exécution : le code est versionné dans le dépôt privé `Louis-Cagnion/Solo_leveling`. J'en déduis une interface locale, mais le déploiement n'est pas tranché.

### Questions à trancher en P1 (§12, points tranchés 9/9)

1. Pertinence et valeur ajoutée pour l'apprentissage.
2. Fonctionnalités prioritaires et superflues.
3. Données de `/professor` à exploiter et améliorations nécessaires.
4. Critères d'évaluation des compétences et des projets.
5. Fonctionnement de l'expérience, des niveaux et des rangs.
6. Calibration par rapport au cursus de 42.
7. Conditions de déblocage de « I AM THE ANSWER » et des autres titres.
8. Architecture technique et modalités d'intégration (local ou déployé, pile, lecture des données).
9. Modalités de la maquette (Opus `xhigh`, `impeccable`).

### Décisions de P1

- **Point 1, rôle de l'interface** (Louis, 11/11/2026) : un tableau de bord gamifié dans l'esprit de *Solo Leveling*, pour voir où en est la progression. C'est un affichage des compétences, pas un outil de recommandation.
- **Point 2, contenu de la V1** (Louis, 11/11/2026) : XP, rangs, titres et trajectoire vers le niveau 25, ainsi que le réseau de compétences. Ce réseau s'appuie sur les paliers des cartes (débutant, intermédiaire, avancé, transcendée) et sur leurs certifications associées. Les statistiques détaillées du §2 et les recommandations du §5 sont hors de la V1.
- **Point 3, sources de l'XP** (Louis, 11/11/2026) : l'XP, le niveau et les projets de 42 viennent de l'API de l'intranet, et les projets perso et pro de `/professor`. Si l'API est trop limitée, les règles de calcul et les données générales de 42 (table XP, XP par projet) servent à recalculer. Les achievements du profil 42, obtenus et non obtenus, s'intègrent s'il est possible de les lire (feuille P0.4).
- **Point 6, niveau affiché** (Louis, 11/11/2026) : deux jauges. Le niveau 42 officiel s'affiche tel quel. Le niveau « Système » compte toutes les sources, et sa courbe est calée pour atteindre 25 en même temps que le niveau 42.
- **Point 5, rangs d'un domaine** (Louis, 11/11/2026, tableau confirmé) : le rang se lit sur la carte du domaine.

  | Rang | Condition |
  |---|---|
  | E | une notion de la carte commencée |
  | D | palier débutant validé |
  | C | palier intermédiaire validé |
  | B | moitié du palier avancé validée |
  | A | palier avancé validé |
  | S | palier transcendée validé |
  | Nation | certifications de la carte obtenues ; S suffit si la carte n'en a aucune |
- **Point 4, XP d'un projet perso ou pro** (Louis, 11/11/2026) : le projet rapporte l'XP du projet 42 de taille et de difficulté proches. Cette XP baisse avec la part de l'IA, d'après la colonne `auteur` de `historique-ia.csv` (par exemple 100 % pour `louis`, 50 % pour `mixte`, 0 % pour `ia`, taux à fixer en P2).
- **Point 7, « I AM THE ANSWER »** (Louis, 11/11/2026) : deux titres distincts. La version 42 se débloque au niveau 42 officiel 25 ; c'est un écart assumé au §7.2, qui voulait des preuves en plus du seuil. La version « Système » se débloque avec le rang S sur toutes les cartes, quel que soit leur nombre.
- **Point 8, architecture** (Louis, 11/11/2026) : l'interface tourne en local, sur la machine de Louis. C'est une page en HTML, CSS et JS sans framework, alimentée par un script de synchronisation qui lit `/professor` et l'API 42 et produit le fichier de données affiché. Le secret OAuth reste hors de Git.
- **Point 9, maquette** (Louis, 11/11/2026) : un agent Opus en effort `xhigh` la construit avec le skill `impeccable`, puis le moniteur la montre dans Chrome.
- **Données réelles** (Louis, 11/11/2026) : la lecture seule du suivi de `/professor` est autorisée pour les maquettes et les tests sur données réelles de P5 ; l'API 42 attend son consentement.

## Arbre (phases closes 4/6)

Statuts : [ ] à faire, [~] en cours, [x] faite, [v] validée, [!] bloquée
Prochaine feuille prête : P4.5 (ordre de Louis du 11/11/2026 : P4.4, P4.5, P4.6, puis P5 sans attendre son avis sur les maquettes, montrées dans Chrome à son retour)
Moniteur : opus 5.5/high, réévalué à la clôture de P1

- P2 [nœud] : conception, sans code ; point de contrôle : le document de conception couvre les six critères du brief de P2.1
  - [v] P2.1 analyst : modèle de données, règles de calcul, architecture, découpage ; fait par : opus/high, deux affirmations relues par le moniteur
  - [v] P2.2 moniteur : `docs/design/conception.md`
- P4 [nœud] : maquette (§11) ; point de contrôle : rendu montré à Louis dans Chrome, choix validé
  - [v] P4.1 moniteur et Louis : `PRODUCT.md`, direction choisie par Louis (constellation façon Holy Graph de 42, après deux tirages), contrat dans `.impeccable/surfaces/`
  - [x] P4.2 builder : maquette `mockups/constellation/`, données réelles de `/professor` ; dépend de : P4.1 ; niveau : opus/xhigh (§11) ; fait par : opus/xhigh ; avis de Louis : concept intéressant, mais trop d'informations et de clics
  - [x] P4.3 builder : variante allégée `mockups/constellation-light/` (révélation progressive, fichiers de 750 lignes au plus) ; dépend de : P4.2 ; niveau : opus/high (retouche, pas une conception) ; fait par : opus/high ; avis de Louis : mieux, mais encore trop fourni
  - [x] P4.4 builder : navigation en trois niveaux `mockups/constellation-steps/` (cercle des sections, section sur toute la page, détail d'un palier) ; fait par : opus/high, puis fixer sonnet/medium (débordement d'1 px, statut répété sous les sections, une régression) ; « type » du niveau 3 lu comme l'objectif de la notion, à confirmer par Louis ; avis de Louis : à recueillir
  - [ ] P4.5 builder : fenêtre de statut détaillée, au clic sur la carte des niveaux et des titres (consigne de Louis du 11/11/2026). Elle montre : le détail des titres ; les projets qui ont donné de l'XP pour atteindre le niveau actuel, sur 42 et sur le Système ; la progression vers les deux « I AM THE ANSWER » (42 et Système) ; les achievements de l'école en détail. Dépend de : P4.4
  - [ ] P4.6 builder : page à part, réseau de neurones 3D des liens entre notions, en particulier les transferts (proposition de Louis du 11/11/2026). 3D par une copie locale de three.js (MIT), choisie par Louis le 11/11/2026, sans aucune ressource externe. Dépend de : P4.4
- P3 [nœud] : plan d'implémentation, validé par Louis ; dépend de : P2 et P4
  - [v] P3.1 analyst : fiches de T1 à T12 ; fait par : sonnet/high, 15 ambiguïtés relevées et arbitrées par le moniteur
  - [v] P3.2 moniteur : `docs/design/implementation.md`, validé par Louis le 11/11/2026 (critères visuels de T11 après la maquette)

- P5 [nœud] : V1, une sous-tâche après l'autre (`docs/design/implementation.md`, section « Ordre d'exécution ») ; point de contrôle : T12 (`checker`). Chaque Tn se déroule en a (tester, tests rouges), b (builder, tests verts), c (analyst, revue VALIDÉ ou À CORRIGER), d (fixer, si à corriger). Niveaux pressentis : section « Niveaux d'agent » du plan, réévalués au lancement.
  - [ ] T1 ; [ ] T2 ; [ ] T3 ; [ ] T5 ; [ ] T4 ; [ ] T6 ; [ ] T9 ; [ ] T7 ; [ ] T8 ; [ ] T10 ; [ ] T11 (après P4) ; [ ] T12
  - [>] T0 : formats de `/professor` (session `/professor`, hors dépôt)

### P0 Recherche (feuilles validées 4/4) et P1 Décisions (points tranchés 9/9)

- P0 [nœud] : réunir les faits nécessaires aux décisions de P1 ; point de contrôle : chaque question de P1 dispose de ses faits ou d'un manque nommé (validé par le moniteur ; pas de `checker`, faute de code ou de test à jouer)
  - [v] P0.1 analyst (`docs/research/professor-data.md`) : inventaire des données de `/professor` ; fait par : sonnet/medium, chiffres vérifiés par sondage, un compte corrigé (6 cartes sans notion suivie, et non 7)
  - [v] P0.2 general-purpose (`docs/research/42-system.md`) : niveaux officiels de 42 ; fait par : sonnet/medium, une source relue par le moniteur
  - [v] P0.3 moniteur (`docs/research/mechanics.md`) : mécaniques transposables
  - [v] P0.4 general-purpose (`docs/research/42-api.md`) : API de l'intranet 42 (authentification, endpoints, achievements, quotas) et source de repli des règles de calcul (42calculator) ; fait par : sonnet/medium, table XP relue par le moniteur


## Faits pour la suite

- Seules les métriques M1, M2 et M4 ont assez de mesures. Les autres seraient aujourd'hui affichées comme « insuffisant » (`docs/research/professor-data.md`).
- Projets, XP et part de l'IA par notion n'existent pas dans `/professor` : ils conditionnent l'XP personnelle, les rangs et les titres.
- Le niveau 25 n'est pas un jalon officiel de 42 : le titre reste un objectif personnel, à calibrer sur la table XP de l'API de l'intranet.
