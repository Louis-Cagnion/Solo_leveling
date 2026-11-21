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
| W Vitrine | Maquette publiée sur GitHub Pages avec un instantané des données (`docs/design/vitrine.md`), avant la V1 | 4 à 8 | oui, rendu visuel |
| P5 V1 puis pré-mortem | Tests, réalisation, revue, correction, finalisation, publication | 4 à 8 | tests sur les données |

## Cadrage (étape 1)

### Risques

- **Doublon avec `/professor`** (§9) : l'interface lit les données de `/professor`, elle n'en collecte aucune de son côté. Tout manque se corrige dans `/professor`.
- **Niveaux arbitraires** (§2) : sans preuve suffisante, un score ment. Chaque valeur affichée porte un statut : observé, estimé ou insuffisant.
- **Calibration sur 42 non vérifiée** (§7.1) : la formule d'XP, la courbe des niveaux et la place du niveau 25 dans le cursus restent à établir sur des sources officielles.
- **Double comptage** (§6.1) : un même projet ou une même compétence ne doit pas rapporter deux fois de l'XP sans justification.
- **Autonomie surestimée** (§8) : ce qui a été réalisé avec l'IA n'est pas une preuve d'autonomie. `historique-ia.csv` distingue déjà `louis`, `mixte`, `ia` et `lecture`.
- **Gadget plutôt qu'outil** (§12.1) : un tableau de bord motivant, mais qui n'aide à aucune décision d'apprentissage, ne justifie pas le projet.
- **Propriété intellectuelle** : on s'inspire des mécaniques et de l'ambiance (fenêtres « Système », rangs E à S, titres), sans reprendre de logo, d'illustration, de police ni de visuel officiel de *Solo Leveling*.
- **Confidentialité** : le suivi mentionne des projets professionnels anonymisés, et le site publié est public. Les données publiées passent le contrôle de confidentialité du dépôt des commandes avant chaque push (ligne 2 de « Restrictions et secours », `docs/design/vitrine.md`).
- **AI Act** : il s'agit d'une auto-évaluation personnelle, sans décision sur un tiers, donc d'un risque minimal. Le niveau serait à revoir si les scores servaient un jour à un recrutement.

### Informations manquantes

- La table officielle de l'XP par niveau et l'XP par projet : seule l'API de l'intranet les donne, avec l'accès de Louis (`docs/research/42-system.md`).
- Le lieu d'exécution : tranché au point 8 (synchronisation locale, site publié sur GitHub Pages).

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
- **Point 8 amendé, publication** (Louis, 21/11/2026) : le site est publié sur GitHub Pages depuis ce dépôt, rendu public le 20/11/2026, pour Louis seul et sur ordinateur ; vitrine d'abord avec un instantané des données, puis la V1, puis le pré-mortem (A31 de `docs/design/implementation.md`, décisions détaillées dans `docs/design/vitrine.md`).
- **Point 9, maquette** (Louis, 11/11/2026) : un agent Opus en effort `xhigh` la construit avec le skill `impeccable`, puis le moniteur la montre dans Chrome.
- **Données réelles** (Louis, 11/11/2026) : la lecture seule du suivi de `/professor` est autorisée pour les maquettes et les tests sur données réelles de P5 ; l'API 42 attend son consentement.

## Arbre (phases closes 5/7)

Statuts : [ ] à faire, [~] en cours, [x] faite, [v] validée, [!] bloquée
Reprise (moniteur Sonnet/high au moins, jamais Fable ; consigne de Louis du 15/11/2026) : activer `/best-practice`, lire `todo.md` puis cet arbre, et reprendre à « Prochaine feuille prête ». Feuilles à garder en Opus/high, revue comprise : T4 (OAuth), T7 (calibration), T11 (page), W8 (revue de la vitrine).
Ordre (Louis, 21/11/2026) : W (vitrine), puis P5 à partir de T2.a2, puis PM (pré-mortem).
Prochaine feuille prête : W0 (Louis, demandée au début de la phase) et W1
Moniteur : opus 5.5/high jusqu'à P3 ; depuis P4.7 : fable 5.2, effort par défaut de la session (aucun réglage pour ce modèle dans `settings.json`), session choisie par Louis ; plan de la vitrine : opus 5.5/high ; à partir de W1 : sonnet 5.5/high recommandé ; agents en sonnet ou opus seulement

- W [nœud] : vitrine sur GitHub Pages (`docs/design/vitrine.md`, fiches W0 à W13) ; point de contrôle : W12 (`checker`), 15 lignes de « Restrictions et secours » jugées ; un agent à la fois
  - [ ] W0 Louis : source de GitHub Pages sur « GitHub Actions » ; dépend de : - ; demandée au début de la phase, attendue avant W11
  - [ ] W1 tester : tests rouges du site, du déploiement et de l'instantané ; dépend de : - ; niveau pressenti : sonnet/medium
  - [ ] W2 builder : `public/` copié de la maquette, démonstration gardée (`?demo` ou `#demo` selon Louis) ; dépend de : W1 ; niveau pressenti : sonnet/medium
  - [ ] W3 builder : `tools/snapshot.py` et `public/data.js` ; dépend de : W2 ; niveau pressenti : sonnet/medium
  - [ ] W4 builder : `public/` aux conventions de la PARTIE B, rendu inchangé ; dépend de : W2 ; niveau pressenti : sonnet/high
  - [ ] W5 builder : politique de sécurité, `noindex`, icône, `404.html`, replis ; dépend de : W4 ; niveau pressenti : sonnet/high
  - [ ] W6 builder : `tools/sound_partials.py` versionné, sortie dans `public/js/` ; dépend de : W2 ; niveau pressenti : sonnet/low
  - [ ] W7 builder : `.github/workflows/pages.yml`, actions épinglées par SHA ; dépend de : W1 ; niveau pressenti : sonnet/medium
  - [ ] W8 analyst : revue indépendante, VALIDÉ ou À CORRIGER ; dépend de : W2 à W7 ; niveau pressenti : opus/high
  - [ ] W9 fixer : une feuille par problème CRITIQUE ou IMPORTANT de W8 ; dépend de : W8
  - [ ] W10 moniteur : rendu comparé à la maquette dans Chrome, validé par Louis ; dépend de : W9
  - [ ] W11 moniteur : workflow commité et poussé, site en ligne vérifié ; dépend de : W0, W10
  - [ ] W12 checker : point de contrôle ; dépend de : W11 ; niveau pressenti : sonnet/high
  - [ ] W13 moniteur : README, contexte des agents, arbre condensé, reprise sur T2.a2 ; dépend de : W12

- P2 [nœud] : conception, sans code ; point de contrôle : le document de conception couvre les six critères du brief de P2.1
  - [v] P2.1 analyst : modèle de données, règles de calcul, architecture, découpage ; fait par : opus/high, deux affirmations relues par le moniteur
  - [v] P2.2 moniteur : `docs/design/conception.md`
- P4 [nœud] : maquette (§11), validée par Louis le 15/11/2026 (`mockups/system/`, sons compris) ; point de contrôle : rendu montré à Louis dans Chrome, choix validé
  - [v] P4.1 moniteur et Louis : `PRODUCT.md`, direction choisie par Louis (constellation façon Holy Graph de 42, après deux tirages), contrat dans `.impeccable/surfaces/`
  - [x] P4.2 builder : maquette `mockups/constellation/`, données réelles de `/professor` ; dépend de : P4.1 ; niveau : opus/xhigh (§11) ; fait par : opus/xhigh ; avis de Louis : concept intéressant, mais trop d'informations et de clics
  - [x] P4.3 builder : variante allégée `mockups/constellation-light/` (révélation progressive, fichiers de 750 lignes au plus) ; dépend de : P4.2 ; niveau : opus/high (retouche, pas une conception) ; fait par : opus/high ; avis de Louis : mieux, mais encore trop fourni
  - [x] P4.4 builder : navigation en trois niveaux `mockups/constellation-steps/` (cercle des sections, section sur toute la page, détail d'un palier) ; fait par : opus/high, puis fixer sonnet/medium (débordement d'1 px, statut répété sous les sections, une régression) ; « type » du niveau 3 lu comme l'objectif de la notion, à confirmer par Louis ; avis de Louis : à recueillir
  - [x] P4.5 builder : fenêtre de statut détaillée, au clic sur la carte des niveaux et des titres (consigne de Louis du 11/11/2026). Elle montre : le détail des titres ; les projets qui ont donné de l'XP pour atteindre le niveau actuel, sur 42 et sur le Système ; la progression vers les deux « I AM THE ANSWER » (42 et Système) ; les achievements de l'école en détail. Dépend de : P4.4 ; fait par : opus/high dans `mockups/constellation-steps/`, alignement du tableau corrigé par haiku/low ; avis de Louis : à recueillir
  - [x] P4.6 builder : page à part, réseau de neurones 3D des liens entre notions, en particulier les transferts (proposition de Louis du 11/11/2026). 3D par une copie locale de three.js (MIT), choisie par Louis le 11/11/2026, sans aucune ressource externe. Dépend de : P4.4 ; fait par : opus/high dans `mockups/neural-network/` (three.js 0.147.0, dernière version en scripts classiques), puis fixer sonnet/medium (étiquettes superposées, jargon interne, extrémités invisibles) ; avis de Louis : à recueillir
  - [x] P4.7 moniteur : retouches d'après la relecture de Louis du 11/11/2026, faites dans la nouvelle maquette `mockups/system/` (consigne du 15/11/2026 : une maquette d'abord, style des fenêtres du Système de *Solo Leveling*, carte blanche pour le reste) ; premier avis de Louis le 15/11/2026 : très favorable, retouches faites le jour même (domaine doré au rang S et violet au rang Nation, sons, texte du centre de la roue) ; avis suivant : à recueillir.
    - Roue (niveau 1) : titre de chaque carte à l'intérieur de sa section, sections agrandies pour qu'il y tienne ; les rangs restent à l'extérieur.
    - Niveau 2 : titre seul de chaque notion, sans parenthèse ni explication (règle de coupe vérifiée sur les 682 libellés réels).
    - États des notions : quatre rendus (« comprise » et au-dessus, en dessous, « déclarée », « non rencontrée ») en rareté de couleur, animation réservée aux états hauts, coupée sous `prefers-reduced-motion` ; même code sur la page 3D.
    - Niveau 3 : infobulle sur « Objectif » (valeurs possibles, d'après `methode.md`) et sur tout intitulé ou valeur obscur ; infobulles existantes relues.
    - Fenêtre de statut : « Titres » devient la liste des certifications reconnues ; les deux « I AM THE ANSWER » passent dans « Achievements » ; « Projets qui ont donné de l'XP » devient deux blocs, 42 et Système, avec une barre de niveau, le total d'XP et une liste déroulante de l'XP par projet.
  - [x] P4.8 moniteur : refonte du réseau 3D dans `mockups/system/network.html` (avis de Louis du 11/11/2026 : trop d'informations, panneaux trop longs, termes non expliqués, palette qui ne se démarque pas ; à garder : détail d'un lien, épaisseur selon le statut, rotation et zoom) ; retouches du 15/11/2026 à la demande de Louis : décor (étoiles, halos d'amas, socle), types de connexion en listes repliées, « Recadrer la vue » relance la rotation ; puis, même jour, dispositions au choix et échelle de rareté en sept couleurs pour les rangs et les états ; avis de Louis du 15/11/2026 : amas par domaine par défaut, arbre autour d'une notion racine en second, couches retirées, rotation qui reprend 0,5 s après un déplacement ou un zoom ; avis suivant : à recueillir (sphères de domaine dans l'arbre, sons) ; plan de refonte :
    - Premier écran : le réseau complet, dominant ; aucune fiche ouverte.
    - Un côté : légende compacte des types et statuts de lien, chaque terme avec une infobulle qui le définit (« analogue », « instance de »…) ; cliquer un type filtre le réseau (remplace la case « Transferts seulement »).
    - L'autre côté : liste déroulante des connexions, groupées par type, en titres courts « A → B ».
    - Détail seulement au clic sur une connexion (liste ou arête) : A → B, type, statut ; limite et preuve repliées derrière « Voir la preuve ». Le clic sur une notion met en avant ses liens et réduit la liste à ceux-ci.
    - Identité propre : une couleur franche et contrastée par type de lien (jamais l'or, réservé aux titres), étiquettes des notions au survol seulement, moins d'étiquettes d'amas.
- P3 [nœud] : plan d'implémentation, validé par Louis ; dépend de : P2 et P4
  - [v] P3.1 analyst : fiches de T1 à T12 ; fait par : sonnet/high, 15 ambiguïtés relevées et arbitrées par le moniteur
  - [v] P3.2 moniteur : `docs/design/implementation.md`, validé par Louis le 11/11/2026 (critères visuels de T11 après la maquette)

- P5 [nœud] : V1, construite en entier sur ordre de Louis du 15/11/2026 (« avec tous les choix validés jusqu'ici, commit et push »), une sous-tâche après l'autre (`docs/design/implementation.md`, section « Ordre d'exécution ») ; point de contrôle : T12 (`checker`). Chaque Tn se déroule en a (tester, tests rouges), b (builder, tests verts), c (analyst, revue VALIDÉ ou À CORRIGER), d (fixer, si à corriger). Niveaux pressentis : section « Niveaux d'agent » du plan, réévalués au lancement.
  - [x] T1 (a faite par sonnet/low : 37 tests rouges ; b faite par sonnet/medium après une interruption par disque plein : 37 verts ; c faite par sonnet/high : À CORRIGER, 1 critique (fuite de secret), 6 importants, 12 mineurs ; d faite (tests par sonnet/low, correction par sonnet/medium) : 56 verts) ; [~] T2 (a faite par sonnet/medium : 61 tests rouges, schéma des 12 entités fixé par la fixture `state_complete.js` puis complété par le moniteur ; b arrêtée par Louis sans fichier écrit, en attente de son ordre) ; [ ] T3 ; [ ] T5 ; [ ] T4 ; [ ] T6 ; [ ] T9 ; [ ] T7 ; [ ] T8 ; [ ] T10 ; [ ] T11 (après P4) ; [ ] T12
  - [v] P5.0 analyst : écarts entre la maquette validée `mockups/system/` et le contrat de données du plan ; fait par : opus/high, 17 écarts (E1 à E17), repris par le moniteur dans les amendements A17 à A30
  - [ ] T2.a2 tester : fixtures `tests/fixtures/state/*.js` et tests `test_model.py`, `test_output.py` portés au contrat amendé (A17 à A25 et entité `names` de A27, 14 entités), toujours rouges ; niveau pressenti : sonnet/medium ; puis T2.b (sonnet/high), c, d
  - [ ] T1.e tester puis builder : `cert_ready_at_least` dans `config/rules.toml` et `config.py` (A22) ; avant T6 ; niveau pressenti : sonnet/low
  - [ ] T13 (après T10) : synchronisation lancée à la clôture d'une session `/professor` et formats de T0 (A29) ; dépôt des commandes, commit isolé ; niveau pressenti : sonnet/medium
  - [ ] T14 (après T3, avant T10) : table `config/names-en.toml` des noms de `/professor` en anglais, lue par `sync`, avec le test « aucun identifiant sans traduction » (A27) ; niveau pressenti : sonnet/medium pour le lecteur et le test, haiku/medium pour remplir la table par carte
  - T11 se découpe au lancement (A26 à A28) : adaptateur et fonctions pures avec `node --test`, page `index.html`, page `network.html`, textes en deux langues et leur test ; opus/high pour les deux pages
  - [ ] T15 (après T12) : publication de la V1 sur GitHub Pages à la place de l'instantané (A31) ; niveau pressenti : sonnet/high
  - [>] T0 : formats de `/professor`, fondue dans T13 (A29)
- PM [nœud] : pré-mortem, après T15 : une feuille en lecture seule par axe de « Phases d'un projet destiné à un public » (`~/.claude/references/best-practice/arborescence-taches.md`), ordinateur seulement, puis les constats de `todo.md` triés en arbre de correction

### P0 Recherche (feuilles validées 4/4) et P1 Décisions (points tranchés 9/9)

- P0 [nœud] : réunir les faits nécessaires aux décisions de P1 ; point de contrôle : chaque question de P1 dispose de ses faits ou d'un manque nommé (validé par le moniteur ; pas de `checker`, faute de code ou de test à jouer)
  - [v] P0.1 analyst (`docs/research/professor-data.md`) : inventaire des données de `/professor` ; fait par : sonnet/medium, chiffres vérifiés par sondage, un compte corrigé (6 cartes sans notion suivie, et non 7)
  - [v] P0.2 general-purpose (`docs/research/42-system.md`) : niveaux officiels de 42 ; fait par : sonnet/medium, une source relue par le moniteur
  - [v] P0.3 moniteur (`docs/research/mechanics.md`) : mécaniques transposables
  - [v] P0.4 general-purpose (`docs/research/42-api.md`) : API de l'intranet 42 (authentification, endpoints, achievements, quotas) et source de repli des règles de calcul (42calculator) ; fait par : sonnet/medium, table XP relue par le moniteur


## Faits pour la suite

- Seules les métriques M1, M2 et M4 ont assez de mesures. Les autres seraient aujourd'hui affichées comme « insuffisant » (`docs/research/professor-data.md`).
- Projets, XP et part de l'IA par notion n'existent pas dans `/professor` : ils conditionnent l'XP personnelle, les rangs et les titres.
- Revue de T1 (11/11/2026), pour les sous-tâches suivantes :
  - T4 : `check_env` renvoie `None` pour un port vide et `""` pour un identifiant ou un secret vides : les refuser au point d'usage avec un message dédié ; le `dict` renvoyé contient le secret en clair, à ne jamais journaliser.
  - T5 : vérifier `https://`, un délai borné puis le sha256 avant d'utiliser la table XP.
  - T6 : l'ordre des rangs est celui des tables `ranks.*` ; retirer les états de `states.excluded` avant toute comparaison « au moins X » (« déclarée » est en tête de `order`).
  - T7 : A7 place les points d'ancrage dans `config/rules.toml`, mais leur schéma (`[[calibration.anchors]]`) et son contrôle restent à ajouter.
  - T3 : `check_env` ne contrôle pas `IA_HISTORY_CSV` (existence, fichier ordinaire).
- Le niveau 25 n'est pas un jalon officiel de 42 : le titre reste un objectif personnel, à calibrer sur la table XP de l'API de l'intranet.
