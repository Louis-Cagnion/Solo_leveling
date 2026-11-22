# Plan d'implémentation de la V1 (P3)

Ce plan détaille les sous-tâches T1 à T12 de `docs/design/conception.md`. Pour chacune, il donne les entrées, la sortie, les fichiers, des critères vérifiables (avec leur commande exacte) et les cas de test que l'étape 4 écrit avant le code. Les fiches viennent de la feuille P3.1 (11/11/2026) ; les arbitrages du moniteur sur les ambiguïtés relevées précèdent les fiches et l'emportent sur elles en cas d'écart. Le plan doit être validé par Louis avant toute ligne de code.

## Noms en anglais

Tous les identifiants, noms de fichiers, de dossiers, de fixtures, d'options en ligne de commande et de variables s'écrivent en anglais (règle « Langue du code » de `/best-practice`). Les textes de l'interface restent en français. Les noms de modules ci-dessous sont transposés dans les fiches. Les autres noms français qui restent dans les fiches (fixtures, options, variables) sont indicatifs : l'agent qui crée un fichier le nomme en anglais.

| Conception | Nom retenu |
|---|---|
| `synchro` | `system_sync` (`python3 -m system_sync sync`) |
| `regles/`, `rangs`, `titres`, `reseau` | `rules/`, `ranks`, `titles`, `network` |
| `modele.py`, `sortie.py`, `table_xp.py` | `model.py`, `output.py`, `xp_table.py` |
| `config/regles.toml` | `config/rules.toml` |
| `data/etat.js`, `window.SYSTEME` | `data/state.js`, `window.SYSTEM_STATE` |
| `{valeur, statut, sources[], raison}` | `{value, status, sources[], reason}` |
| `observe`, `estime`, `insuffisant` | `observed`, `estimated`, `insufficient` |

Les noms qui viennent de `/professor` (`cartes/`, `notions.md`, `relations.csv`, `evenements.csv`, `projets.csv`, les colonnes et leurs valeurs) restent tels quels : ce sont des données externes.

## Arbitrages sur les ambiguïtés

- **A1, faits ajoutés à `/professor`** (formats de T0) :
  - `niveau` : `metrique` = `niveau`, `domaine` = nom de la carte (titre `# Carte : <Nom>`), `notion` vide, `valeur` parmi `débutant`, `intermédiaire`, `avancé`, `transcendée`, `preuve` = chemin du banc ;
  - `certification` : même forme, avec `valeur` = code de la certification ;
  - `titre` : `valeur` = identifiant du titre, pour qu'un titre acquis ne se perde jamais (voir A7).
- **A2, Nation** : tant que S n'est pas atteint, Nation est « non atteint » (observé). La valeur ne passe à « insuffisant » que si S est atteint et que la liste des certifications de la carte est illisible. Une certification partagée entre plusieurs cartes compte pour chacune d'elles.
- **A3, API** : on lit l'entrée de `cursus_users` dont `cursus.id` vaut 21, jamais l'élément d'index 21.
- **A4, XP de base des projets** : elle vient de `projects_21.json` de 42calculator, lu à distance et épinglé (commit et sha256), avec le même mécanisme que la table XP de T5. Valeur estimée, source tierce.
- **A5, `projets.csv`** :
  - `cadre` : `perso` ou `pro` ;
  - `statut` : `en cours`, `livré` ou `abandonné` ;
  - `id` : comparé sans tenir compte de la casse à la colonne `projet` d'`historique-ia.csv` ;
  - une clé est ambiguë quand plusieurs graphies d'`historique-ia.csv` désignent un même `id` ; elle se signale en anomalie et se corrige en T0 ;
  - fichier absent : statut « absent », distinct d'un échec de lecture, et XP Système égale à l'XP 42.
- **A6, calibration** :
  - un seul segment, du dernier point d'ancrage jusqu'au niveau 25 ;
  - r = XP perso et pro livrée depuis le premier point, divisée par l'XP 42 gagnée sur la même période ;
  - r ne s'estime qu'avec au moins 3 projets livrés ET au moins 90 jours depuis le premier point ;
  - XP arrondie à l'entier ;
  - sans `projets.csv`, le niveau Système est estimé (la table est tierce) avec la raison « aucun projet perso ou pro enregistré ».
- **A7, état persistant** :
  - un titre acquis s'enregistre comme fait `titre` dans `/professor` (T0) : il ne dépend jamais de `data/`, qui est ignoré par Git ;
  - les points d'ancrage de la calibration sont des données versionnées de `config/rules.toml` ;
  - la trajectoire (`data/history/`, une ligne par synchronisation) reste locale, et sa perte est acceptée ;
  - la reconstitution par `marked_at` est hors V1.
- **A8, état « déclarée »** : il est exclu de toutes les comparaisons « au moins X », pour les rangs comme pour les prérequis fragiles.
- **A9, rangs** :
  - « la moitié » vaut ⌈n/2⌉ ;
  - un palier vide ne remplit jamais une condition « toutes les notions » ;
  - un fait `niveau` vaut aussi pour les paliers précédents (`methode.md:262` : un niveau ne se valide qu'après le précédent).
- **A10, schéma** :
  - une 12e entité `network` (`nodes`, `edges`, `highlights`) ;
  - `notions{}` contient les 682 notions de carte et les notions suivies hors carte, avec l'état « non rencontrée » pour celles que le suivi ne contient pas ;
  - un champ simple (`card` d'une notion hors carte) peut valoir `null` sans statut ; seules les valeurs statuées suivent la règle de la raison ;
  - une valeur observée a au moins une source ;
  - T9 dépend aussi de T6 pour les manques.
- **A11, fichiers manquants à l'arborescence** : `config.py`, `__main__.py` et les `__init__.py` sont créés par T1 ; la commande `verifier` (contrôle du format des sources) est rattachée à T10 ; `EXTERNAL.md` est écrit par T4 et complété par T5.
- **A12, noms** : en anglais, voir ci-dessus.
- **A13, événements et relations** :
  - la V1 ne lit dans `evenements.csv` que les faits `niveau`, `certification` et `titre` ; les autres lignes sont comptées comme lues, sans autre traitement ;
  - T3 ne rejette que les lignes mal formées ;
  - une relation vers un identifiant inconnu est gardée, avec un nœud « inconnu » signalé suspect en T9.
- **A14, tests de la page** : `node --test` sert de coureur pour les fonctions JS pures, sans aucun paquet npm. Le comportement de la page se vérifie dans Chrome par le moniteur.
- **A15, OAuth** :
  - l'URI de redirection et l'écoute utilisent toutes deux `127.0.0.1` ;
  - chaque synchronisation redemande le consentement dans le navigateur (pas de jeton de rafraîchissement en V1) ;
  - le cache de l'API s'affiche « observé au <date> », sans limite d'âge en V1.
- **A16, API de `config.py`** (moniteur, 11/11/2026) : `ConfigError`, `load_rules(path)`, `rules_fingerprint(path)`, `load_env(path)` et `check_env(env)` ; contrat détaillé dans la docstring de `tests/system_sync/test_config.py`, écrite en T1.a.

## Amendements du 15/11/2026 (après la maquette)

La maquette `mockups/system/`, validée par Louis le 15/11/2026, lit des données que le plan du 11/11 ne prévoyait pas (rapport de la feuille P5.0, écarts E1 à E17). Ces amendements l'emportent sur les arbitrages A1 à A16 et sur les fiches. Validés par Louis le 15/11/2026.

- **A17, quatre statuts** (choix de Louis, `PRODUCT.md`) : `observed`, `estimated`, `insufficient`, `unmeasurable`.
  - `unmeasurable` : aucune mesure n'est possible (source absente, API sans consentement, table indisponible, projet sans ligne d'historique, carte sans colonne « Certifications ») ; valeur `null` et raison obligatoires.
  - `insufficient` : des conditions existent et ne sont pas remplies (seuils de prudence, calibration « provisoire ») ; raison obligatoire, valeur facultative.
  - Partout où une fiche écrit « insuffisant » pour une donnée absente, lire `unmeasurable` (T4, T5, T7 L1, L2 et L4, T8 N6 et L1, T10 L2 à L4, A2, A6).
- **A18, raison traduisible** : toute raison porte `reason_code` (vocabulaire fermé, en anglais, déclaré dans `model.py`) en plus de `reason` (phrase française de repli) ; la page traduit le code (voir A27).
- **A19, « aucun rang »** : valeur observée `"none"` ; `rank.value` appartient à `E`, `D`, `C`, `B`, `A`, `S`, `Nation`, `none`.
- **A20, rang suivant** : `cards[].gaps` devient `next_rank`, objet ou `null` au rang maximal : `rank`, `condition` (texte tiré des règles), `progress` (valeur statuée), `total` (entier ou `null`), `missing` (`[{id, state}]`).
- **A21, certifications** : `cards[].certifications[]` = `code`, `detail` (texte ou `null`), `notions` (identifiants des notions dont la colonne « Certifications » des cartes cite ce code, toutes cartes confondues, liste éventuellement vide), `conditions` (`null` en V1), `obtained` (valeur statuée), `obtained_on` (date ISO ou `null`, date du fait `certification`), `accessible` (valeur statuée, calculée par T6 : toutes ses notions au moins au seuil `cert_ready_at_least` ; `unmeasurable` sans `notions`). `tier` est retiré. La ligne `Codes` de A2 et de `c:91` est remplacée par la colonne « Certifications » des cartes (6 cartes sur 19 au 15/11/2026).
- **A22, cibles et règles exportées** : `level42.target_xp` (valeur statuée, estimée d'après la table XP) ; entité `rules` : `proof_order` (ordre des états sans les exclus ni « non rencontrée »), `excluded_states`, `rank_d_threshold`, `cert_threshold`, `target_level`. `config/rules.toml` gagne `[states] cert_ready_at_least = "retenue"`, contrôlée par `config.py`.
- **A23, achievements de 42** : entité `achievements` à part : `complete` (valeur statuée booléenne, `unmeasurable` avec le code `full_list_unavailable`), `items[]` = `id`, `name`, `description`, `obtained` (statuée), `obtained_on`, `title` (les trois derniers nullables). `titles[]` ne garde que les deux « I AM THE ANSWER », sans « (42) » dans `name`.
- **A24, notions, relations, sources** : `notions{}.section` (titre `## <domaine>` de `notions.md`, ou `null`) ; relations en `source`, `target` et statut brut de `/professor` (`theorique`, `reconnue`, `demontree`) ; `sources[].observed_at` (date ISO ou `null`, pour A15).
- **A25, entité `network` retirée** (E16) : la page construit le réseau depuis `relations[]` et `notions{}`. T9 se réduit au contrôle des relations (extrémité inconnue, auto-relation, doublon, cycle de prérequis signalé) et au repérage des prérequis fragiles (prérequis sous « comprise » alors que sa cible est au moins « comprise »). Louis, le 15/11/2026 : un prérequis connu ne devrait pas être fragile ; s'il l'est, le suivi est à revérifier pour que les mesures soient fiables. Un prérequis fragile n'est donc pas affiché comme une information : `sync` le range dans `anomalies[]` (nature `fragile_prerequisite`, les deux notions et leurs états), à corriger dans une session `/professor`. `anomalies[]` et `trajectory[]` restent produites ; leur affichage va au pré-mortem.
- **A26, calculs de la page** : `public/` garde des fonctions pures d'affichage, testées par `node --test` : rang du bloc « Niveau 42 » (7 tranches d'XP égales de 0 à `target_xp`), rang du bloc « Niveau Système » (moyenne des rangs des domaines, `none` et `unmeasurable` comptés 0), tons de rareté, comparaison de deux visites (boîte « Événements », `localStorage`). Le niveau Système affiché reste celui de la calibration (A6) : la moyenne ne donne que le rang du bloc (E17, confirmé par Louis).
- **A27, deux langues** (consigne de Louis du 15/11/2026) : la page s'affiche en français ou en anglais. Tous ses textes (libellés, infobulles, raisons par `reason_code`, annonces, page de repli) vivent dans un fichier par langue, `public/js/strings-fr.js` et `strings-en.js`. Un test prouve que les deux ont les mêmes clés, toutes non vides, et qu'aucun texte français ne reste en dur dans `public/` hors de `strings-fr.js`. Les noms de notions, de domaines, de paliers et de certifications viennent de `/professor`, en français : leur traduction vit dans une table versionnée du projet, `config/names-en.toml` (identifiant vers libellé anglais), jamais dans les fiches du skill (choix de Louis du 15/11/2026). `sync` l'exporte dans une entité `names` (`en` : identifiant vers libellé) et signale en anomalie, code `missing_translation`, tout identifiant de `/professor` absent de la table ; la page affiche alors le libellé français. Feuille T14 : remplir la table (682 notions de carte, notions hors carte, domaines, certifications au 15/11/2026) et tester qu'aucun identifiant du jour ne manque.
- **A28, page (T11)** : deux pages, `public/index.html` et `public/network.html` ; copie tierce `public/vendor/` (three.js 0.147.0 et `OrbitControls.js`, MIT, jamais reformatés), exemptée des critères 2 et 4 et du plafond de 750 lignes, comme les licences des polices et l'espace de noms SVG ; `css/views.css` (756 lignes) à scinder ; `js/demo.js` non porté ; contrôle de `schema_version` ajouté ; un module adaptateur lit `window.SYSTEM_STATE` (la maquette lit `window.SYSTEME`, d'une autre forme). Sons : `public/js/sound-data.js` est généré par `tools/sound_partials.py`, versionné avec lui ; `sound effects/` reste hors de Git. N8 passe à quatre statuts.
- **A29, synchronisation depuis `/professor`** (consigne de Louis du 15/11/2026) : aucune copie statique du suivi ; `sync` lit les fichiers de `/professor` et régénère `data/state.js`. Feuille T13, après T10 : la clôture d'une session `/professor` lance `sync` sans l'API 42 (cache relu), par une règle du dépôt des commandes ; T0 (faits `niveau`, `certification`, `titre`, `projets.csv`) se fait dans la même feuille, les formats étant ceux de A1, A5 et A21.
- **A30, comptes** : les comptes réels des fiches datent du 11/11/2026 (16 cartes ; 19 au 15/11). Chaque testeur les remesure au lancement de sa feuille et épingle les empreintes du jour. Les comptes de tests par fiche et le total « ≥ 269 » sont des planchers à recalculer en T12 ; le critère 4 de T2 attend 14 entités (`rules`, `achievements`, `names` ajoutées, `network` retirée) ; le critère 3 de T12 lit `d['cards']`.

## Amendement du 21/11/2026 (publication)

- **A31, vitrine puis V1** (Louis, 21/11/2026) : la phase W (`docs/design/vitrine.md`) publie d'abord la maquette sur GitHub Pages dans `public/`, avec un instantané `public/data.js` (`window.SYSTEME`) produit par `tools/snapshot.py`. A29 (« aucune copie statique du suivi ») est suspendu pour cet instantané seulement, jusqu'à T15. `js/demo.js` est porté et gardé (Louis, 21/11/2026), contrairement à A28. Conséquences sur la V1 :
  - T11 part du `public/` de la vitrine (aucun nouveau portage depuis `mockups/system/`) : adaptateur vers `window.SYSTEM_STATE`, deux langues (A27), contrôle de `schema_version` ; le critère 2 de T11 exclut `public/vendor/` et les licences `.txt` ; les tests S1 à S15 de `tests/public/test_site_static.py` restent verts.
  - T15, après T12 : la page publiée lit l'état produit par `sync`, copié dans `public/` sans les champs internes (anomalies, chemins des sources) ; `tools/snapshot.py` et `public/data.js` sont retirés ; la procédure « Rafraîchir la vitrine » devient celle de la publication de la V1. T13 ne pousse jamais seul : publier reste une action demandée par Louis, sauf décision contraire de sa part à T13.

## Ordre d'exécution

Un seul agent à la fois (consigne de Louis du 11/11/2026), donc sans worktree. Chaque sous-tâche passe par l'étape 4 (un `tester` écrit ses tests, rouges), puis l'étape 5 (un `builder` les fait passer au vert), puis la revue de l'étape 6 et la correction de l'étape 7.

Ordre (A31) : la vitrine (W0 à W13), puis T1, T2, T3, T4, T5, T6, T9, T7, T8, T10, T11, T12 (`checker`), T15, puis le pré-mortem. T0 se fait en session `/professor`, à n'importe quel moment : la V1 fonctionne sans T0, avec des valeurs « insuffisant ».

## 0. Conventions communes

**Citations.** `c:N` renvoie à la ligne N de `docs/design/conception.md`, `p:N` à `docs/plan.md`, `bp:N` à `~/.claude/commands/best-practice.md`, `m:N` à `methode.md`, `rc:N` à `regles-communes.md`.

**Test.** Chaque module `source/system_sync/X.py` a son miroir `tests/system_sync/test_X.py`, et `sources/` et `rules/` ont le leur. Un `__init__.py` est requis dans chaque dossier de `tests/` pour la forme pointée.
- Un module : `PYTHONPATH=source python3 -m unittest tests.system_sync.sources.test_professor -v`
- Suite complète : `PYTHONPATH=source python3 -m unittest discover -s tests -t . -v`

**Identifiants de cas.** `Tn-Nk` désigne un cas nominal, `Tn-Lk` un cas limite (absent, vide, mal formé, hors plage, doublon), `Tn-Pk` un cas de pré-mortem. L'étape 4 nomme chaque test par son identifiant. Les pré-mortem ne sont pas dans les comptes de tests.

**Compte global.** La suite complète donne « Ran ≥ 269 tests, OK (skipped=3) ». Les 3 ignorés sont les tests sur données réelles ou réseau, sans leurs variables d'environnement. Détail par tâche (T1 à T12) : 25, 26, 33, 30, 23, 28, 29, 21, 17, 18, 10, 9.

**Qualité du code.** Elle suit la PARTIE B, donc les règles communes (`rc:13`) :
- 95 caractères par ligne au plus ;
- un argument par ligne dans un appel enveloppé ;
- aucun « — » ;
- 750 lignes de code au plus par fichier ;
- une erreur par cause, qui nomme `fichier:ligne`, le champ et la valeur reçue (`bp:185-186`) ;
- journal avec niveau et horodatage pour tout script sans supervision (`bp:196`) ;
- aucun accès réseau sans délai borné (`bp:190`).

**Données réelles.** Les comptes ci-dessous sont un instantané du 11/11/2026. `/professor` change tous les jours. Chaque test réel calcule d'abord les empreintes sha256 (16 premiers caractères) et s'ignore, avec un message, si elles diffèrent :
- `notions.md` : `67275067762f23fe`
- `relations.csv` : `d873f1cf85d191c0`
- `evenements.csv` : `e408fe6877d7de86`
- `historique-ia.csv` : `cb3bd9843714290e`
- `cat cartes/*.md` (ordre alphabétique) : `3ddf648fe1b702dd`

**Variables d'environnement proposées pour T1** (la conception ne les nomme pas, `c:39`) : `PROFESSOR_SUIVI_DIR`, `IA_HISTORY_CSV`, `API42_CLIENT_ID`, `API42_CLIENT_SECRET`, `API42_CALLBACK_PORT`.


---

## 1. Fiches T1 à T12

### T1 : squelette, `.gitignore`, `.env.example`, `rules.toml`

- **Entrées** : `c:99-110` (arborescence), `c:39` (contenu de `rules.toml`), `c:113` (Python 3.12, bibliothèque standard seulement), `c:143` (tests versionnés), `p:49-67` (décisions P1 : rangs, taux d'IA, titres). `.gitignore` existant : il contient déjà `.env` et `data/`, mais pas `__pycache__/`. `README.md` existant : il dit « aucune ligne de code n'existe encore ».
- **Faits à intégrer** : la table XP est épinglée sur le commit `520b8e938ac8f685a4bc647bba45d0b409282714` (dernier commit touchant `data/experience_21.json`, 14/05/2024). Son sha256 est `7b98ff202015868ed400f339589e6ca00dc009d436a599c3f2272b5c0e258771`, identique à celui de `main` au 11/11/2026. URL brute : `https://raw.githubusercontent.com/lucas-ht/42calculator/520b8e938ac8f685a4bc647bba45d0b409282714/data/experience_21.json`.
- **Sortie** : arborescence importable, règles chargeables, variables documentées.
- **Fichiers**
  - Créés : `config/rules.toml`, `.env.example`, `source/system_sync/__init__.py`, `source/system_sync/sources/__init__.py`, `source/system_sync/rules/__init__.py`, `source/system_sync/config.py` (chargeur de `rules.toml` et de `.env`, ajout non listé, voir A11), `tests/__init__.py`, `tests/system_sync/__init__.py`, `tests/test_architecture.py`, `tests/system_sync/test_config.py`.
  - Créés (fixtures) : `tests/fixtures/config/rules_valid.toml`, `rules_rate_out_of_range.toml`, `rules_empty.toml`, `rules_malformed.toml`, `valid.env`, `no_equals.env`, `duplicate.env`. Le motif `.env` du `.gitignore` attrape tout fichier nommé exactement `.env`, d'où les noms `valid.env`.
  - Modifiés : `.gitignore` (ajout de `__pycache__/`), `README.md` (état et structure actuels, `bp:284-286`).
- **`rules.toml` (types de rang et de titre en données, `c:39`)** : tables proposées `states` (ordre), `ranks` (une entrée par rang avec son `type` et ses paramètres), `ia` (louis 1.0, mixte 0.5, ia 0.0, `lecture` ignorée), `xp_table` (url, commit, sha256), `calibration` (niveau cible 25, `r_initial` 0, seuils 3 projets et 90 jours), `titles`. Commentaires de 3 lignes au plus.

| # | Critère | Commande exacte | Résultat attendu | Source |
|---|---|---|---|---|
| 1 | Tests T1 | `PYTHONPATH=source python3 -m unittest tests.test_architecture tests.system_sync.test_config -v` | `Ran` ≥ 25, `OK` | c:122 |
| 2 | Paquet importable | `PYTHONPATH=source python3 -c "import system_sync, system_sync.sources, system_sync.rules"` | code 0, aucune sortie | c:99-110 |
| 3 | Familles de règles | `python3 -c "import tomllib; print(sorted(tomllib.load(open('config/rules.toml','rb'))))"` | `['calibration', 'ia', 'ranks', 'states', 'titles', 'xp_table']` (ordre trié par la commande) | c:39 |
| 4 | Taux d'IA | `python3 -c "import tomllib; print(tomllib.load(open('config/rules.toml','rb'))['ia'])"` | `{'louis': 1.0, 'mixte': 0.5, 'ia': 0.0}` | c:39 |
| 5 | Épingle de la table XP | `grep -c "7b98ff202015868ed400f339589e6ca00dc009d436a599c3f2272b5c0e258771" config/rules.toml` | `1` | c:115, c:150 |
| 6 | Git | `grep -cE '^(\.env\|data/\|__pycache__/)$' .gitignore` puis `grep -cE '^/?tests' .gitignore` | `3` puis `0` (tests versionnés, décision de Louis qui prime sur `bp:228`) | c:143 |
| 7 | Aucun secret | `grep -nE '^API42_CLIENT_SECRET=.+' .env.example` | aucune ligne (code 1) | c:39 |
| 8 | Forme | `grep -rnE '.{96,}' source tests config --include='*.py' --include='*.toml'` ; `grep -rn '—' source tests config README.md .env.example` | aucune ligne, code 1 pour les deux | rc:13 |
| 9 | README à jour | `grep -c "aucune maquette ni ligne de code" README.md` | `0` | bp:284 |

- **Cas nominaux**
  - N1 : `rules.toml` réel se charge avec les 6 familles.
  - N2 : taux d'IA corrects, `lecture` absent.
  - N3 : table XP avec URL contenant le commit et un sha256 de 64 hexadécimaux.
  - N4 : calibration (cible 25, `r_initial` 0, seuils 3 et 90).
  - N5 : l'empreinte des règles égale le sha256 du fichier.
  - N6 : `.env.example` contient les 5 clés, toutes vides.
  - N7 : le chargeur de `.env` accepte commentaires, lignes vides et guillemets.
  - N8 : imports de la bibliothèque standard seulement, dans `source/` et `tests/` (`c:102, c:113`).
  - N9 : aucun module de `rules/` n'importe `sources/` (`c:112`).
  - N10 : aucune ligne de plus de 95 caractères.
  - N11 : aucun fichier de code de plus de 750 lignes.
  - N12 : aucun « — ».
  - N13 : `.gitignore` conforme (critère 6).
- **Cas limites**
  - L1 : `rules.toml` absent, message avec le chemin.
  - L2 : fichier de 0 octet, message « vide ».
  - L3 : TOML mal formé, message avec la ligne.
  - L4 : taux de 1,5 ou de -0,1, message avec clé et valeur.
  - L5 : taux `mixte` absent, message avec la clé.
  - L6 : états en doublon dans l'ordre.
  - L7 : `.env` absent, message qui liste les 5 variables.
  - L8 : variable obligatoire vide, message avec le nom et jamais la valeur.
  - L9 : ligne sans `=`, message avec le numéro de ligne.
  - L10 : clé en doublon dans `.env`.
  - L11 : chemin `PROFESSOR_SUIVI_DIR` inexistant, puis fichier au lieu de dossier (deux messages distincts).
  - L12 : port non numérique ou hors 1024-65535, message avec la valeur.
- **Pré-mortem** : `.env` en CRLF ou avec BOM ; valeur contenant `=`, `#` ou des espaces ; `~` et chemins relatifs ; `rules.toml` avec BOM ; locale non UTF-8 (`LANG=C`) ; `.env` lisible par tous (avertir si le mode dépasse 600, documenté en V1 par `chmod 600` dans le README) ; empreinte qui change avec les fins de ligne ; caractère de contrôle (NUL, BEL) dans une valeur du `.env`.
- **Niveau** : tester sonnet/low ; builder sonnet/medium. Structure et configuration, le point délicat est le contenu de `rules.toml`.

### T2 : modèle, schéma de sortie, validateur

- **Entrées** : T1, `c:9-12` (valeur statuée, `null` et raison obligatoire si insuffisant), `c:14-30` (11 entités), `c:32-35` (liste blanche, « Solidité » non exportée), `c:107` (`output.py`).
- **Sortie**
  - `model.py` : valeur statuée `{value, status, sources[], reason}` avec ses invariants, et anomalie `(fichier, ligne, nature, détail)`.
  - `output.py` : schéma fermé des entités, `valider` (liste de chemins et de causes), `écrire` atomique (validation d'abord, temporaire dans le même dossier, `os.replace`, `allow_nan=False`) qui produit `window.SYSTEM_STATE = {...};`.
- **Fichiers**
  - Créés : `source/system_sync/model.py`, `source/system_sync/output.py`, `tests/system_sync/test_model.py`, `tests/system_sync/test_output.py`.
  - Créés (fixtures, partagées avec T11 et T12) : `tests/fixtures/state/state_minimal.js`, `state_complet.js`, `state_vide.js`, `state_partiel.js`, `state_schema_inconnu.js`, `state_piege.js`, `state_insuffisant_sans_raison.js`, `state_cle_inconnue.js`. Valeurs fictives ; `state_piege.js` porte une chaîne `<img src=x onerror=alert(1)>` et `</script>`.

| # | Critère | Commande exacte | Résultat attendu | Source |
|---|---|---|---|---|
| 1 | Tests | `PYTHONPATH=source python3 -m unittest tests.system_sync.test_model tests.system_sync.test_output -v` | `Ran` ≥ 26, `OK` | c:123 |
| 2 | Pas de NaN | `grep -c "allow_nan=False" source/system_sync/output.py` | `1` | c:16 |
| 3 | Remplacement atomique | `grep -c "os.replace" source/system_sync/output.py` | ≥ `1` | c:107 |
| 4 | Fichier chargeable par un navigateur | `node -e "global.window={};require('./tests/fixtures/state/state_complet.js');console.log(Object.keys(window.SYSTEM_STATE).length)"` | `11` (ou 12 selon A10) | c:16, c:18-30 |
| 5 | Taille | `wc -l source/system_sync/model.py source/system_sync/output.py` | chacun ≤ 750 | bp:226 |

- **Cas nominaux**
  - N1, N2, N3 : valeur observe, estime, insuffisant (null et raison).
  - N4 : anomalie rendue `fichier:ligne`.
  - N5 : état minimal valide.
  - N6 : état complet valide.
  - N7 : sortie commençant par `window.SYSTEM_STATE = ` et finissant par `;\n`.
  - N8 : aller-retour JSON identique.
  - N9 : création de `data/` si absent.
  - N10 : aucun `.tmp` restant.
  - N11 : clé inconnue refusée (`level42.email`), message avec le chemin (`c:33`).
  - N12 : colonne « Solidité » refusée dans `notions{}` (`c:34`).
- **Cas limites**
  - L1 : entité `meta` absente.
  - L2 : `{}` donne la liste des entités manquantes.
  - L3 : état qui n'est pas un objet.
  - L4 : statut inconnu, message avec la valeur.
  - L5 : observe avec valeur null.
  - L6 : insuffisant avec valeur non null.
  - L7 : insuffisant sans raison, ou raison vide ou faite d'espaces (`c:12`).
  - L8 : version de schéma inconnue, message avec la valeur reçue.
  - L9 : niveau ou XP négatifs, date de génération mal formée.
  - L10 : doublon (deux `cards[]` de même id, deux sources de même nom).
  - L11 : NaN ou Infinity refusés avec leur chemin.
  - L12 : échec de validation, l'ancien `state.js` reste identique octet pour octet (sha256 égal).
  - L13 : dossier non inscriptible, message avec `strerror`, ancien fichier intact.
  - L14 : observe sans source (déduit de `c:10`, voir A10).
- **Pré-mortem** : `</script>` et U+2028 dans les chaînes ; `OSError` injecté après écriture partielle (temporaire supprimé) ; deux écritures simultanées ; lien symbolique `state.js` ; état de 10 Mo ; substitut Unicode isolé ; booléen pris pour entier ; clé non chaîne.
- **Niveau** : tester sonnet/medium ; builder sonnet/high. C'est le contrat de toute la chaîne, et le validateur s'écrit à la main sans bibliothèque.

### T3 : lecteurs de `/professor`

- **Entrées** : T2 (anomalies, `sources[]`) ; les 5 sources en lecture seule ; `c:35` (colonnes par nom, découpe sur `|` non échappé), `c:30` (anomalies avec `fichier:ligne`), `c:88-95`.
- **Formats constatés** :
  - **Carte** : titre `# Carte : <Nom>`, ligne `- **Notions** : 42, dont 5 déjà suivies.`, 4 sections `## Débutant|Intermédiaire|Avancé|Transcendée`, tableaux `| Id | Notion |`. Les certifications sont du texte libre ; il n'existe aucune ligne `Codes`.
  - **`notions.md`** : une section `## <domaine>` par carte (plus « Principes »), tableaux à 10 colonnes (Id, Notion, Objectif, État, Dernière pratique, Intervalle, Prochain rappel, Dernier M1, Rechutes, Solidité). `\|` est échappé. Les dates peuvent valoir « à fixer ».
  - **`relations.csv`** : 7 colonnes `date,source,relation,cible,statut,limite,preuve`. Statuts sans accent : `theorique`, `reconnue`, `demontree`. Types : `prerequis`, `complementaire`, `instance_de`, `analogue`, `transfert`.
  - **`evenements.csv`** : 9 colonnes. `session` vaut « passe-niveaux » aux lignes 708-731 (24 lignes) ; `notion` est vide à la ligne 491 (cadrage).
  - **`historique-ia.csv`** : 7 colonnes, `auteur` ∈ {ia, louis, mixte, lecture}.
- **Sortie** : cartes (nom, paliers, ids dans l'ordre, compte déclaré), notions suivies (sans « Solidité »), relations (dernière ligne d'un triplet), événements, lignes d'historique, `projets.csv` facultatif (A5), faits `niveau` et `certification` bruts (A1), anomalies, compteurs lues et rejetées par source.
- **Fichiers**
  - Créés : `source/system_sync/sources/professor.py`, `tests/system_sync/sources/__init__.py`, `tests/system_sync/sources/test_professor.py`, `tests/system_sync/sources/test_professor_reel.py`.
  - Créés (fixtures, `tests/fixtures/professor/`) :
    - `suivi/cartes/alpha.md` (4 paliers de 2 notions, une ligne certification).
    - `suivi/cartes/beta.md` (aucune notion suivie).
    - `suivi/notions.md` (sections « Alpha » et « Principes », 6 lignes dont une avec `\|`, une hors carte, une « déclarée »).
    - `suivi/relations.csv` (5 lignes, un triplet répété, une ligne à 8 champs).
    - `suivi/evenements.csv` (8 lignes : session non numérique, notion vide, un fait `niveau`, une virgule entre guillemets).
    - `historique-ia.csv` (8 lignes dont une à 9 champs et une datée `10/2026`).
    - `mal_forme/` : `carte_sans_titre.md`, `carte_palier_bonus.md`, `notions_9_colonnes.md`, `relations_vide.csv` (0 octet), `evenements_entete_seul.csv`.
    - Les fichiers binaires (Latin-1, BOM, FIFO, droits) sont générés par le test dans un dossier temporaire.

| # | Critère | Commande exacte | Résultat attendu | Source |
|---|---|---|---|---|
| 1 | Tests fictifs | `PYTHONPATH=source python3 -m unittest tests.system_sync.sources.test_professor -v` | `Ran` ≥ 32, `OK` | c:124 |
| 2 | Comptes réels | `PROFESSOR_SUIVI_DIR=/home/sung-jinwoo/claude_custom_commands/references/professor/suivi IA_HISTORY_CSV=/home/sung-jinwoo/claude_custom_commands/references/best-practice/historique-ia.csv PYTHONPATH=source python3 -m unittest tests.system_sync.sources.test_professor_reel -v` | `OK`, non ignoré, avec les comptes ci-dessous | c:56, p:73 |
| 3 | Lecture seule, sans réseau | `grep -nE "open\([^)]*['\"][wax+]\|urlopen\|socket" source/system_sync/sources/professor.py` | aucune ligne (code 1) | bp:190 |

- **Comptes réels attendus (critère 2)** :
  - 16 cartes ; 682 notions de carte ; 108 notions suivies, dont 66 sur une carte et 42 hors carte.
  - États des 108 : découverte 48, en cours 29, transférée 11, appliquée 9, déclarée 6, comprise 5.
  - 77 relations lues, 76 gardées, 1 rejetée (`relations.csv:40`, 8 champs au lieu de 7). Statuts des 76 : theorique 55, demontree 11, reconnue 10. Types : prerequis 41, complementaire 15, instance_de 13, analogue 4, transfert 3.
  - 730 événements, 0 rejeté.
  - 165 lignes d'historique, 159 gardées, 6 rejetées (`historique-ia.csv:14,15,16,17,19,21`), 1 suspecte (`:45`, date `10/2026`). Auteurs des 159 : ia 70, lecture 40, louis 37, mixte 12 ; 24 projets.
  - 8 anomalies de format au total (1 + 6 + 1).
  - 0 fait `niveau` et 0 fait `certification`.
- **Cas nominaux**
  - N1 : carte, nom, 4 paliers, ids ordonnés.
  - N2 : compte déclaré (« Notions : 8, dont 2 déjà suivies ») lu.
  - N3 : `notions.md`, 10 colonnes nommées.
  - N4 : `\|` reste dans la cellule.
  - N5 : « Solidité » absente de la sortie (`c:34`).
  - N6 : relations, 7 champs lus tels quels.
  - N7 : triplet répété, la dernière ligne fait foi (`c:27`).
  - N8 : événements, virgule entre guillemets conservée.
  - N9 : session « passe-niveaux » acceptée.
  - N10 : historique, auteurs.
  - N11 : compteurs par source.
  - N12 : une ligne rejetée donne une anomalie `fichier:ligne` avec sa cause, et les suivantes sont lues.
  - N13 : faits `niveau` et `certification` exposés bruts (format hypothétique, A1).
  - N14 : `projets.csv` absent est un statut « absent » distinct d'« indisponible » (A5).
  - N15 : sources inchangées après lecture (sha256).
- **Cas limites**
  - L1 : chacune des 5 sources absente, source indisponible avec le chemin, les autres lues.
  - L2 : dossier à la place d'un fichier.
  - L3 : fichier de 0 octet, message distinct d'« absent ».
  - L4 : en-tête seul.
  - L5 : `cartes/` sans `.md`.
  - L6 : nombre de champs différent (reçu et attendu nommés).
  - L7 : date `10/2026`, ligne gardée et marquée suspecte (`:45`).
  - L8 : date impossible `31/02/2026`, rejet.
  - L9 : date hors plage (avant 2020 ou future), suspecte.
  - L10 : auteur inconnu ou statut de relation inconnu, rejet avec la valeur reçue.
  - L11 : ligne de `notions.md` à 9 ou 11 colonnes rejetée, jamais décalée.
  - L12 : état de notion inconnu (« expert »).
  - L13 : carte sans titre.
  - L14 : palier « Bonus » inconnu, et palier manquant.
  - L15 : doublon d'Id dans une carte, entre cartes, dans `notions.md`.
  - L16 : fait `niveau` de valeur inconnue.
  - L17 : octets Latin-1, message avec l'offset.
- **Pré-mortem** : BOM ; CRLF ; accents en NFD ; FIFO et lien symbolique (tester `S_ISREG` avant ouverture, pas de blocage) ; guillemet CSV ouvert qui avale le fichier (numéro de ligne de départ) ; cellule multiligne ; ligne de 10 Mo ; colonnes réordonnées, ajoutées ou renommées (lecture par nom, `c:35`) ; ligne `Codes` ajoutée en tête de carte (`c:160`) ; `|` dans un `` `code` `` non échappé ; fichier modifié pendant la lecture ; lecture incohérente entre fichiers pendant une session `/professor` ; chemin avec espaces ; droits 000 ; volume ×10 pour vérifier que le temps reste linéaire (`bp:191`) ; `auteur` écrit « Louis » ; « à fixer » dans `Intervalle`.
- **Niveau** : tester sonnet/high ; builder sonnet/high. Cinq formats, rejets chiffrés, beaucoup de cas limites.

### T4 : client de l'API 42

- **Entrées** : T2, T1 (`.env`), `42-api.md:7-12` (flux, endpoints, 2 requêtes par seconde, 1 200 par heure, jeton de 2 h, pages de 100), `c:22, c:33, c:75, c:114, c:125, c:158`.
- **Sortie** :
  - Flux authorization code avec `state` aléatoire (`secrets`) comparé en temps constant.
  - Serveur de retour sur 127.0.0.1 seulement, un seul callback, délai total borné, fermé ensuite, journal du serveur HTTP désactivé.
  - Jeton gardé en mémoire.
  - `GET /v2/me` (niveau du cursus 21, projets, achievements : liste blanche, `c:33`), puis `GET /v2/achievements?per_page=100` paginé avec plafond de pages et de taille.
  - Limiteur de 2 requêtes par seconde (horloge injectable).
  - Délais bornés et reprise bornée sur 429 et 5xx (`Retry-After`).
  - Cache `data/cache/` écrit atomiquement ; statuts de source `ok`, `cache`, `indisponible`.
- **Fichiers**
  - Créés : `source/system_sync/sources/api42.py`, `tests/system_sync/sources/test_api42.py`, `tests/system_sync/sources/serveur_factice.py` (assistant de test, `http.server` sur 127.0.0.1 port 0), `EXTERNAL.md` (`bp:294`, valeurs par variable d'environnement, jamais en dur).
  - Créés (fixtures, `tests/fixtures/api42/`) : `me_valide.json`, `me_champs_personnels.json` (champs génériques non identifiants), `me_vide.json`, `achievements_page1.json`, `achievements_page2.json`, `token.json`.

| # | Critère | Commande exacte | Résultat attendu | Source |
|---|---|---|---|---|
| 1 | Tests | `PYTHONPATH=source python3 -m unittest tests.system_sync.sources.test_api42 -v` | `Ran` ≥ 30, `OK`, aucune connexion hors 127.0.0.1 | c:125 |
| 2 | Délai sur chaque appel | `grep -nE "urlopen\(\|HTTPS?Connection\(" source/system_sync/sources/api42.py` | chaque ligne contient `timeout` (le test statique le compte) | bp:190 |
| 3 | TLS non contourné | `grep -nE "_create_unverified_context\|CERT_NONE\|check_hostname *= *False" source/system_sync/sources/api42.py` | aucune ligne (code 1) | bp:180 |
| 4 | Liaison locale | test N2 : `getsockname()[0] == "127.0.0.1"` | `OK` | c:114 |
| 5 | Secrets absents | test N12 : le secret fictif ne figure ni dans le journal capturé ni dans `data/cache/` | `OK` | c:114 |
| 6 | Réel (consentement dans le navigateur) | non vérifiable par un agent (clic de Louis, jeton de Louis) | à faire au P5 par Louis et le moniteur : `sources[]` api42 = `ok`, niveau 12,44 | c:158 |

- **Cas nominaux**
  - N1 : URL d'autorisation avec `client_id`, `redirect_uri`, `response_type=code` et un `state` de 128 bits au moins, différent à chaque appel.
  - N2 : serveur lié à 127.0.0.1 et au port du `.env`.
  - N3 : callback valide, échange du code contre le jeton, jeton en mémoire seulement.
  - N4 : niveau du cursus 21 lu (12,44, observé).
  - N5 : projets validés extraits.
  - N6 : achievements obtenus extraits.
  - N7 : champs personnels de la fixture absents de la sortie et du cache.
  - N8 : `/v2/achievements` sur 2 pages fusionnées.
  - N9 : écart d'au moins 0,5 s entre deux requêtes.
  - N10 : cache écrit puis relu si l'API échoue, statut `cache`.
  - N11 : serveur fermé et port libre après le callback.
  - N12 : secret, code et jeton absents du journal et du cache.
  - N13 : tous les appels réseau ont un délai (analyse statique).
- **Cas limites**
  - L1 : identifiants absents du `.env`, message qui nomme les variables, aucun appel réseau.
  - L2 : consentement non donné, fin au délai, repli sur le cache.
  - L3 : `state` absent ou différent, HTTP 400, aucun échange.
  - L4 : callback rejoué.
  - L5 : `error=access_denied`.
  - L6 : `/v2/me` vide.
  - L7 : cursus 21 absent.
  - L8 : niveau « abc », « 12,44 », null, NaN, infini, négatif.
  - L9 : corps HTML ou JSON tronqué.
  - L10 : 401, 403, 404, 429 (`Retry-After` borné), 500, un message par cause.
  - L11 : serveur plus lent que le délai.
  - L12 : doublons de projets et d'achievements.
  - L13 : pagination sans fin.
  - L14 : réponse au-dessus du plafond.
  - L15 : cache absent, vide ou corrompu.
  - L16 : port occupé, le message nomme le port et aucun processus n'est arrêté (`rc:11`).
  - L17 : `/v2/achievements` refusé, obtenus seuls et mention « liste complète indisponible » (`c:75`).
- **Pré-mortem** : `localhost` résolu en `::1` alors que le serveur n'écoute qu'en 127.0.0.1 ; redirection 3xx vers un autre hôte (ne pas la suivre) ; `Retry-After` au format date HTTP ; BOM dans le JSON ; jeton expiré en cours de synchronisation (2 h) ; navigateur introuvable (afficher l'URL à copier) ; variables `HTTP_PROXY` ; magasin de certificats absent (échec explicite) ; cache d'un autre compte ; le journal par défaut de `http.server` écrit la ligne de requête, donc `code` et `state` ; traceback d'`urllib` qui contient l'URL avec `code=` ; quota de 1 200 par heure ; navigateur qui rejoue le callback (favicon, double onglet).
- **Niveau** : tester opus/medium ; builder opus/high. OAuth, serveur local et secrets (sécurité), réseau borné.

### T5 : table XP et interpolation

- **Entrées** : T2, T1 (`xp_table` épinglée), `42-api.md:14-28`, `c:61, c:115, c:150`.
- **Faits constatés (11/11/2026)** : le JSON a la forme `{meta, levels:[{level, experience,...}]}`, avec 31 niveaux de 0 à 30, strictement croissants. 12 → 124 446 ; 13 → 145 782 ; 17 → 263 508 ; 21 → 457 632 ; 25 → 777 756 ; 30 → 1 484 070. 124 446 + 0,44 × (145 782 − 124 446) = 133 833,84, soit environ 133 834 (`c:61`).
- **Sortie** : téléchargement avec délai borné, sha256 sur les octets bruts comparé à l'épingle (refus si différent), validation de forme générique (≥ 2 niveaux, niveaux et XP strictement croissants, pas de nombre magique), cache `data/cache/`. XP d'un niveau décimal par interpolation linéaire (statut estime, sources avec URL et commit, `insufficient` hors table). Fonction inverse XP vers niveau (utile à T7, voir A6).
- **Fichiers**
  - Créés : `source/system_sync/sources/xp_table.py`, `tests/system_sync/sources/test_xp_table.py`, `tests/system_sync/sources/test_table_xp_reseau.py`.
  - Créés (fixtures, `tests/fixtures/xp_table/`) : `experience_valide.json` (niveaux 0 à 5, XP 0, 100, 300, 600, 1000, 1500), `experience_non_croissante.json`, `experience_vide.json`, `experience_champ_manquant.json`.
  - Modifié : `EXTERNAL.md` (ajout de la dépendance, fichier partagé avec T4).
  - Le fichier réel n'est pas versionné ni recopié (`c:115`).

| # | Critère | Commande exacte | Résultat attendu | Source |
|---|---|---|---|---|
| 1 | Tests | `PYTHONPATH=source python3 -m unittest tests.system_sync.sources.test_xp_table -v` | `Ran` ≥ 22, `OK` | c:126 |
| 2 | Table réelle épinglée | `SYNCHRO_TEST_RESEAU=1 PYTHONPATH=source python3 -m unittest tests.system_sync.sources.test_table_xp_reseau -v` | `Ran 1`, `OK`, non ignoré : sha256 conforme, 31 niveaux, XP(12) = 124 446, XP(25) = 777 756, XP(12,44) = 133 833,84, arrondi 133 834 | c:61, c:69 |
| 3 | Délais | `grep -nE "urlopen\(" source/system_sync/sources/xp_table.py` | chaque ligne contient `timeout` | bp:190 |

- **Cas nominaux**
  - N1 : table fictive chargée.
  - N2 : hash épinglé vérifié.
  - N3 : XP exacte à tous les niveaux entiers.
  - N4 : niveau 2,5 donne 450.
  - N5 : continuité aux bornes entières.
  - N6 : croissance stricte sur une grille fine.
  - N7 : aller-retour XP, niveau.
  - N8 : statut `estimated` avec sources.
  - N9 : cache écrit puis relu quand le réseau est coupé (source `cache`).
  - N10 : délai sur chaque appel.
- **Cas limites**
  - L1 : niveau absent (None).
  - L2 : niveau « 12,44 », NaN, infini.
  - L3 : niveau négatif ou au-dessus du maximum, insuffisant sans extrapolation.
  - L4 : bornes exactes 0 et maximum.
  - L5 : hash différent, message avec les deux hashes, cache non écrit.
  - L6 : table vide, sans `levels`, champ manquant.
  - L7 : niveaux en doublon, ou XP non croissante.
  - L8 : table d'un seul niveau.
  - L9 : réseau coupé sans cache.
  - L10 : HTTP 404 et redirection vers un autre hôte.
  - L11 : cache corrompu ou de hash différent.
  - L12 : réponse trop grande.
- **Pré-mortem** : arrondi à .5 (le `round` de Python arrondit au pair) ; représentation binaire de 12,44 ; hash sur octets bruts contre texte (CRLF) ; limite de débit de `raw.githubusercontent.com` ; commit supprimé ; `levels` désordonné ; niveaux écrits en chaînes ; BOM ; `data/cache/` jamais suivi par Git.
- **Niveau** : tester sonnet/medium ; builder sonnet/medium. Petit module, hash et interpolation.

### T6 : rangs

- **Entrées** : T3 (cartes, notions suivies, événements), T1 (conditions de rang en données), `c:43-56, c:88-92, c:146, c:150-152`, `m:156-167` (états), `m:262-274` (niveaux), `m:253` (un niveau validé ne retombe pas).
- **Sortie** : pour chaque carte, un rang (E, D, C, B, A, S, Nation, « aucun rang », insuffisant) avec statut, sources, raison, et la liste des manques pour le rang suivant (ids et état courant). Les rangs sont des types de condition paramétrés dans `rules.toml`, sans `if` par rang (`c:39`).
- **Fichiers**
  - Créés : `source/system_sync/rules/ranks.py`, `tests/system_sync/rules/__init__.py`, `tests/system_sync/rules/test_ranks.py`, `tests/system_sync/rules/test_rangs_reel.py`.
  - Créés (fixtures, `tests/fixtures/ranks/`) : `cartes_demo.json` (3 cartes fictives), `notions_demo.json`, `faits_demo.json` (faits `niveau` et `certification` dans le format hypothétique de A1).

| # | Critère | Commande exacte | Résultat attendu | Source |
|---|---|---|---|---|
| 1 | Tests | `PYTHONPATH=source python3 -m unittest tests.system_sync.rules.test_ranks -v` | `Ran` ≥ 27, `OK` | c:127 |
| 2 | Rangs réels | `PROFESSOR_SUIVI_DIR=/home/sung-jinwoo/claude_custom_commands/references/professor/suivi IA_HISTORY_CSV=/home/sung-jinwoo/claude_custom_commands/references/best-practice/historique-ia.csv PYTHONPATH=source python3 -m unittest tests.system_sync.rules.test_rangs_reel -v` | `OK`, non ignoré : 10 cartes rang E, 6 « aucun rang », 0 carte D | c:56 |
| 3 | Règles sans source | `grep -rnE "^(from\|import) .*sources" source/system_sync/rules` | aucune ligne (code 1) | c:112 |
| 4 | Pas de rang en dur | `grep -nE "(==\|in) *['\"](E\|D\|C\|B\|A\|S\|Nation)['\"]" source/system_sync/rules/ranks.py` | aucune ligne (code 1) | c:39 |

- **Valeurs réelles à contrôler dans le test 2** :
  - Aucune carte à D.
  - SQL : 5 notions débutantes sur 8 au moins « comprises », donc 3 manques pour D.
  - Docker : 4 sur 8, donc 4 manques.
  - Les 10 cartes E (Algorithmique, C, C++, Docker, Infographie 3D, Linux (système), Noyau et assembleur, Réseau, Shell, SQL) ont chacune au moins une notion suivie non « déclarée » (C : 3 sur 5, Infographie 3D : 4 sur 8).
  - Les 6 sans rang : Apprentissage automatique, LLM, PHP, Programmation fonctionnelle, Python, Sécurité binaire.
- **Cas nominaux**
  - N1 : carte sans notion suivie, « aucun rang » (jamais « insuffisant », `c:54`).
  - N2 : une notion « découverte » donne E observé.
  - N3 : notions seulement « déclarées », aucun rang (`c:151`).
  - N4 : D estimé quand toutes les débutantes sont au moins « comprises » (« appliquée » et « transférée » comptent).
  - N5 : D observé si fait `niveau = débutant`, même avec des notions sous « comprise ».
  - N6 : C observé (fait `intermédiaire`).
  - N7 : B estimé (C, plus la moitié des avancées au moins « appliquées », `c:50`).
  - N8 : A observé (fait `avancé`), S observé (fait `transcendée`).
  - N9 : Nation quand S et toutes les certifications retenues sont obtenues.
  - N10 : Nation quand S et aucune certification retenue.
  - N11 : rang affiché = plus haut rang dont toutes les conditions précédentes sont remplies.
  - N12 : niveau validé qui ne retombe pas (fait présent, notions redescendues).
  - N13 : manques listés (notions débutantes sous « comprise » ; pour une carte sans rang, « une notion suivie »).
  - N14 : statut, sources et raison présents sur chaque rang.
  - N15 : changer le seuil de B dans la configuration change le résultat sans toucher au code.
- **Cas limites**
  - L1 : carte None ou liste vide.
  - L2 : aucun événement ni fait.
  - L3 : palier débutant vide, D refusé (jamais vrai par vacuité), insuffisant avec raison.
  - L4 : palier avancé vide, B refusé.
  - L5 : état de notion inconnu, anomalie sans surévaluer le rang.
  - L6 : fait `niveau` de valeur inconnue, ignoré avec anomalie.
  - L7 : fait pour une carte inconnue ou à l'ancien libellé (« Linux et noyau »), anomalie, jamais attribué en silence.
  - L8 : faits en doublon, puis `intermédiaire` suivi de `débutant` (le rang maximal reste).
  - L9 : certification obtenue inconnue de la carte.
  - L10 : Nation sans ligne `Codes`, insuffisant ; S non atteint, Nation « non atteint » (A2).
  - L11 : égalité exacte de la moitié (2 sur 4 donne B, 1 sur 4 non).
  - L12 : notion en doublon dans une carte, comptée une fois.
- **Pré-mortem** : C sans D (A9) ; moitié d'un nombre impair de notions (A9) ; carte d'une seule notion ; l'état « retenue » n'a aucune occurrence réelle, donc le chemin n'est jamais exercé par les données ; ordre « transférée » au-dessus de « retenue » (`c:159`) ; faits contradictoires entre sessions ; carte renommée ; règle de configuration invalide.
- **Niveau** : tester sonnet/high ; builder sonnet/high. Fonctions pures, mais plusieurs ambiguïtés à arbitrer (A8, A9).

### T7 : XP Système et calibration

- **Entrées** : T3 (historique, `projets.csv`), T4 (niveau 42, projets 42 validés), T5 (XP du niveau, inverse), `c:58-69, c:93-95, c:141, c:147-149`, `p:64`.
- **Sortie** : `level42` (niveau observé, XP estimée, écart non expliqué = XP déduite du niveau moins somme des `difficulty` des projets validés) ; `system` (XP, niveau, détail par origine, calibration) ; `projects[]` ; une ligne de trajectoire par synchronisation ; facteur d'IA par projet.
- **Fichiers**
  - Créés : `source/system_sync/rules/xp.py`, `source/system_sync/rules/calibration.py`, `tests/system_sync/rules/test_xp.py`, `tests/system_sync/rules/test_calibration.py`.
  - Créés (fixtures, `tests/fixtures/xp/`) : `projets_demo.csv` (`demo-perso-a` base 400 avec lignes louis, mixte, mixte, lecture ; `demo-pro-b` base 1000 avec lignes ia seulement ; `demo-perso-c` sans ligne ; `demo-perso-d` dont l'équivalent 42 est validé), `historique_demo.csv`, `projets_42_demo.json`, `ancrage_demo.json`. Table fictive de T5, cible de calibration réduite à 5.
- **Exemple chiffré fixé** : `demo-perso-a` a un facteur de (1 + 0,5 + 0,5) / 3 = 0,6667 (`lecture` exclue, `c:148`), soit 266,67 XP. `demo-pro-b` a un facteur de 0,0 : valide et compté pour 0. `demo-perso-c` est insuffisant et ne compte pas. `demo-perso-d` est rejeté. XP_sys = XP_42 + 266,67 (arrondi à fixer, A6).

| # | Critère | Commande exacte | Résultat attendu | Source |
|---|---|---|---|---|
| 1 | Tests | `PYTHONPATH=source python3 -m unittest tests.system_sync.rules.test_xp tests.system_sync.rules.test_calibration -v` | `Ran` ≥ 29, `OK` | c:128 |
| 2 | Propriétés de la courbe | inclus dans N13 à N15 (graine fixe, grille de 1 000 points ; 100 recalibrages aléatoires) | `OK` : courbe continue, strictement croissante, valeur affichée inchangée (écart < 1e-9) | c:69 |
| 3 | Règles sans source | `grep -rnE "^(from\|import) .*sources" source/system_sync/rules` | aucune ligne | c:112 |
| 4 | Réel hors API | non chiffrable sans le jeton de Louis | sans `projets.csv` : Système = 42 seul, calibration « provisoire », `r` = 0 (`c:149`) ; avec le niveau 12,44 : XP_42 = 133 834 | c:93, c:149 |

- **Cas nominaux**
  - N1 : facteur d'IA = moyenne des taux des lignes, `lecture` exclue.
  - N2 : XP d'un projet = base de l'équivalent × facteur.
  - N3 : facteur 0 valide et compté pour 0.
  - N4 : projet sans ligne, facteur insuffisant et projet non compté (`c:67`).
  - N5 : projet dont toutes les lignes sont `lecture`, insuffisant.
  - N6 : XP_sys = XP_42 + somme des projets livrés.
  - N7 : projet perso reprenant un projet 42, rejeté avec raison (`c:68`, détection A5).
  - N8 : XP de l'alternance et projet pro réalisé pendant l'alternance, additionnés (`c:141`).
  - N9 : XP des projets 42 non réduite par l'IA (`c:147`).
  - N10 : XP du niveau 42 par interpolation et écart non expliqué (`c:62`).
  - N11 : sans `projets.csv`, Système = 42 seul.
  - N12 : la courbe passe par l'ancrage.
  - N13 : courbe continue et strictement croissante.
  - N14 : si `r` est constant, la courbe atteint le niveau cible quand XP_42 atteint T(cible).
  - N15 : un recalibrage ne change jamais la valeur affichée à l'XP courante, seulement la pente.
  - N16 : « provisoire » tant que moins de 3 projets ou moins de 90 jours.
  - N17 : une ligne de trajectoire par synchronisation.
- **Cas limites**
  - L1 : niveau 42 absent (API en échec), XP et Système insuffisants avec raison.
  - L2 : `historique-ia.csv` absent ou vide, facteurs insuffisants.
  - L3 : `projets.csv` mal formé, anomalie `fichier:ligne`, autres lignes lues.
  - L4 : équivalent 42 inconnu du catalogue, projet insuffisant.
  - L5 : base d'XP négative, non numérique ou NaN.
  - L6 : auteur inconnu, ligne ignorée avec anomalie.
  - L7 : projet livré deux fois, compté une fois avec anomalie.
  - L8 : date de projet future ou antérieure à 2020, suspecte.
  - L9 : `r` négatif ou infini, refusé, ancrage inchangé.
  - L10 : XP_sys inférieure à l'ancrage, message sans valeur inventée.
  - L11 : niveau cible inférieur ou égal au niveau d'ancrage, aucune division par zéro.
  - L12 : clés d'historique de graphie différente (`RNCP6` et `rncp6`), facteur insuffisant (`c:94`).
- **Pré-mortem** : XP_42 = 0 ; arrondis cumulés ; `r` très grand ; XP_sys au-dessus de T(30) ; 90 jours calendaires contre 90 × 24 h (changement d'heure) ; date jj/mm contre mm/jj ; même équivalent 42 utilisé par plusieurs projets ; changement d'équivalence après l'ancrage ; recalibrer deux fois de suite sur les mêmes données doit donner le même ancrage ; format de l'ancrage qui change d'une version à l'autre.
- **Niveau** : tester opus/high ; builder opus/high. Mathématique de calibration à invariants, plusieurs points sous-spécifiés (A6, A7).

### T8 : titres

- **Entrées** : T4 (niveau, achievements obtenus, liste complète éventuelle), T6 (rangs), T1 (types de titre), `c:71-75, c:142`, `p:65`.
- **Sortie** : `titles[]` avec statut obtenu, non obtenu ou insuffisant, et progression. Le titre « I AM THE ANSWER » (42) est obtenu à un niveau de 25 ou plus. Le titre Système est obtenu quand toutes les cartes sont au rang S. Une carte au rang insuffisant donne le statut « insuffisant », pas « non obtenu » (`c:74`). Une fois obtenu, le titre Système reste acquis (`c:142`).
- **Fichiers**
  - Créés : `source/system_sync/rules/titles.py`, `tests/system_sync/rules/test_titles.py`.
  - Créés (fixtures, `tests/fixtures/titles/`) : `rangs_trois_cartes.json`, `achievements_obtenus.json`, `achievements_complet.json`, `state_precedent_acquis.json`, `state_precedent_corrompu.json`.

| # | Critère | Commande exacte | Résultat attendu | Source |
|---|---|---|---|---|
| 1 | Tests | `PYTHONPATH=source python3 -m unittest tests.system_sync.rules.test_titles -v` | `Ran` ≥ 21, `OK` | c:129 |
| 2 | Règles sans source | `grep -rnE "^(from\|import) .*sources" source/system_sync/rules` | aucune ligne | c:112 |
| 3 | Valeurs réelles (via T10, T12) | voir T12 | titre 42 : 12,44 sur 25, soit 49,76 %, non obtenu, observé ; titre Système : 0 carte S sur 16, non obtenu (aucune carte au rang insuffisant au 11/11/2026) | c:73-74, c:56 |

- **Cas nominaux**
  - N1 : niveau 25,0, titre 42 obtenu.
  - N2 : niveau 24,99, non obtenu, progression 99,96 %.
  - N3 : niveau 30, obtenu.
  - N4 : toutes les cartes à S, titre Système obtenu.
  - N5 : cartes S, S, A, non obtenu, progression 2 sur 3.
  - N6 : une carte au rang insuffisant, titre « insuffisant ».
  - N7 : carte « aucun rang », non obtenu (≠ insuffisant).
  - N8 : titre déjà obtenu et carte ajoutée au rang E, il reste obtenu (`c:142`).
  - N9 : achievements obtenus listés, statut observé.
  - N10 : liste complète disponible, les non obtenus sont listés.
  - N11 : liste complète indisponible, mention « liste complète indisponible » (`c:75`).
  - N12 : un titre de plus déclaré dans la configuration apparaît sans changement de code.
- **Cas limites**
  - L1 : niveau absent, insuffisant.
  - L2 : niveau négatif, NaN, 1e9.
  - L3 : aucune carte, titre Système insuffisant (jamais vrai par vacuité).
  - L4 : achievements absents ou liste vide, texte explicite (`bp:194`).
  - L5 : achievement sans id ou sans nom, anomalie.
  - L6 : achievements en doublon.
  - L7 : état précédent absent (première synchronisation).
  - L8 : état précédent corrompu, ignoré avec message.
  - L9 : achievement obtenu absent de la liste complète, ajouté avec anomalie.
- **Pré-mortem** : dossier `data/historique/` supprimé alors que le titre était acquis (A7) ; niveau API qui régresse sous 25 après avoir été obtenu (le titre 42 est-il aussi persistant ? A7) ; jeton d'un autre compte ; noms d'achievement localisés ; identifiants d'achievement qui changent.
- **Niveau** : tester sonnet/medium ; builder sonnet/medium. Règles courtes, la difficulté est la persistance (A7).

### T9 : réseau de compétences

- **Entrées** : T3, T6 (manques par carte, voir A10), `c:77-82, p:50`.
- **Sortie** : nœuds (notions de carte, notions hors carte, cartes, paliers, certifications si des codes sont lisibles), arêtes (notion vers palier, palier vers carte, relations avec type et statut), états (8 états plus « non rencontrée »), points mis en évidence (prérequis fragiles et manques pour le rang suivant).
- **Fichiers**
  - Créés : `source/system_sync/rules/network.py`, `tests/system_sync/rules/test_network.py`.
  - Créés (fixtures, `tests/fixtures/network/`) : `cartes_alpha_beta.json`, `relations_demo.json` (une relation vers un nœud inconnu, une auto-relation, un cycle de prérequis, un doublon).
- **Valeurs réelles** : 804 nœuds (682 + 42 + 16 + 64 paliers + 0 certification, faute de ligne `Codes`) ; 746 arêtes d'appartenance (682 + 64) ; relations : 822 arêtes au total si la relation vers `minishell-environnement` (`relations.csv:32`) est gardée, 821 sinon (A13) ; 616 notions « non rencontrées » (682 − 66) ; 8 prérequis fragiles (voir fait 7 pour la lecture retenue).

| # | Critère | Commande exacte | Résultat attendu | Source |
|---|---|---|---|---|
| 1 | Tests | `PYTHONPATH=source python3 -m unittest tests.system_sync.rules.test_network -v` | `Ran` ≥ 17, `OK` | c:130 |
| 2 | Règles sans source | `grep -rnE "^(from\|import) .*sources" source/system_sync/rules` | aucune ligne | c:112 |
| 3 | Valeurs réelles | portées par le test réel de T12 (`tests/test_bout_en_bout.py`, variante réelle) | 804 nœuds, 746 arêtes d'appartenance, 616 « non rencontrée », 8 prérequis fragiles | c:79-82 |

- **Cas nominaux**
  - N1 : nœuds de notion de carte, notion hors carte, carte, palier.
  - N2 : arêtes d'appartenance.
  - N3 : arêtes de relation, type et statut conservés.
  - N4 : « non rencontrée » pour une notion de carte absente du suivi, et 8 états sinon.
  - N5 : prérequis fragile (source sous « comprise », cible au moins « comprise »).
  - N6 : non fragile si la source est au moins « comprise », si la cible est sous « comprise », ou si le type n'est pas `prerequis`.
  - N7 : identifiants uniques entre espaces de noms.
  - N8 : certification en nœud quand `Codes` est présent.
  - N9 : comptes attendus sur la fixture alpha et beta.
- **Cas limites**
  - L1 : aucune relation.
  - L2 : relation vers un nœud inconnu, anomalie avec la ligne et l'id (traitement à décider, A13).
  - L3 : auto-relation, rejetée.
  - L4 : cycle de prérequis, signalé sans boucle infinie.
  - L5 : notion présente dans deux paliers.
  - L6 : relation en doublon, une seule arête.
  - L7 : carte sans notion.
  - L8 : statut de relation inconnu.
- **Pré-mortem** : chaîne de 1 000 prérequis (pas de récursion) ; identifiant de carte égal à un identifiant de notion ; caractères spéciaux dans les ids ; relation dont une extrémité est un identifiant de technique (`techniques.md` n'est pas lu en V1).
- **Niveau** : tester sonnet/medium ; builder sonnet/medium. Graphe simple, comptes exacts à tenir.

### T10 : commande `sync`

- **Entrées** : T6 à T9, T2 (écriture et validation), T1 (configuration), `c:16, c:112, c:131` ; point `verifier` non rattaché (A11).
- **Sortie** : lit les sources, applique les règles, valide, écrit `data/state.js` de façon atomique, enregistre la ligne de trajectoire dans `data/historique/` (format A7), journalise chaque étape avec niveau et horodatage (`bp:196`). Interface proposée, à valider : `PYTHONPATH=source python3 -m system_sync sync [--env CHEMIN] [--sortie CHEMIN]`.
- **Fichiers**
  - Créés : `source/system_sync/sync.py`, `source/system_sync/__main__.py` (ajouts non listés, A11), `tests/system_sync/test_sync.py`.
  - Créés (fixtures, `tests/fixtures/sync/`) : `valid.env`, `sans_api.env`, `sans_regles.env`, plus réutilisation de `tests/fixtures/professor/`, `api42/` et `xp_table/`.

| # | Critère | Commande exacte | Résultat attendu | Source |
|---|---|---|---|---|
| 1 | Tests | `PYTHONPATH=source python3 -m unittest tests.system_sync.test_sync -v` | `Ran` ≥ 18, `OK` | c:131 |
| 2 | Synchronisation sur fixtures | `PYTHONPATH=source python3 -m system_sync sync --env tests/fixtures/sync/valid.env --sortie /tmp/state_test.js` (dossier de sortie temporaire du test, jamais `data/` pendant les tests) | code 0 ; sortie qui passe `valider` sans erreur | c:16 |
| 3 | Journal | test N7 | au moins 8 lignes `AAAA-MM-JJ HH:MM:SS … INFO|WARNING|ERROR`, avec les volumes lus et rejetés par source | bp:196 |
| 4 | Secret absent | test N8 | le secret fictif n'apparaît ni dans la sortie ni dans le journal | c:114 |
| 5 | Atomicité | test N10 | sortie invalide, ancien `state.js` identique octet pour octet | c:107 |

- **Cas nominaux**
  - N1 : synchronisation complète sur fixtures, `state.js` valide, code 0.
  - N2 : toutes les entités présentes.
  - N3 : `sources[]` avec statut et compteurs.
  - N4 : anomalies de T3 reprises avec `fichier:ligne`.
  - N5 : `meta` (version de schéma, date ISO, empreinte = sha256 de `rules.toml`).
  - N6 : une ligne de trajectoire par synchronisation.
  - N7 : journal.
  - N8 : aucun secret.
  - N9 : deux synchronisations sur entrées identiques, sortie identique hors `meta.date` et trajectoire.
  - N10 : écriture seulement après validation.
- **Cas limites**
  - L1 : `.env` absent ou mal formé, message, code non nul, aucun fichier écrit.
  - L2 : chemin `/professor` absent, source indisponible, fichier écrit avec valeurs insuffisantes.
  - L3 : API indisponible avec cache (statut `cache`), puis sans cache (insuffisant).
  - L4 : table XP indisponible, XP estimée insuffisante, reste de l'état écrit.
  - L5 : `rules.toml` invalide, échec avant toute lecture.
  - L6 : dossier de sortie non inscriptible, message avec `strerror`, code non nul.
  - L7 : toutes les sources vides, état valide avec raisons, code 0.
  - L8 : sous-commande absente ou inconnue, usage affiché, code 2.
- **Pré-mortem** : deux synchronisations simultanées (verrou) ; interruption (Ctrl-C) entre le temporaire et le remplacement ; horloge ou fuseau ; `data/historique/` volumineux après des mois ; sortie sur un autre disque (`os.replace` entre systèmes de fichiers) ; synchronisation lancée depuis un autre répertoire courant (chemins relatifs).
- **Niveau** : tester sonnet/medium ; builder sonnet/high. Orchestration, échecs partiels, atomicité.

### T11 : page

- **Entrées** : T2 (schéma), P4 (maquette validée par Louis), `c:107` (`public/`, `textContent`, aucune ressource externe), `c:16` (ouverture en `file://`), `c:30, c:75, bp:193-194, bp:230`. La maquette n'est pas lue ici. Les critères visuels (palette, typographie, espacements, composition) viendront d'elle ; seuls ceux qui découlent de la conception sont fixés.
- **Sortie** : page qui lit `window.SYSTEM_STATE` chargé par un script classique `../data/state.js` (`type="module"` est bloqué en `file://` par Chrome, donc scripts classiques `defer`).
- **Fichiers**
  - Créés : `public/index.html`, `public/css/*.css`, `public/js/*.js` (noms à fixer d'après la maquette), `tests/public/__init__.py`, `tests/public/test_page_statique.py`.
  - Fixtures : `tests/fixtures/state/*.js` (T2).
- **Critères automatiques (statiques, Python)**

| # | Critère | Commande exacte | Résultat attendu | Source |
|---|---|---|---|---|
| 1 | Tests | `PYTHONPATH=source python3 -m unittest tests.public.test_page_statique -v` | `Ran` ≥ 10, `OK` | c:132 |
| 2 | Aucune ressource externe | `grep -rnE "https?://\|//[a-z0-9.-]+\.[a-z]{2,}\|@import" public` | aucune ligne (code 1) | c:107 |
| 3 | Pas d'injection HTML | `grep -rnE "innerHTML\|outerHTML\|insertAdjacentHTML\|document\.write\|eval\(\|new Function" public` | aucune ligne | c:107 |
| 4 | Ouverture en `file://` | `grep -rnE "type=\"module\"\|fetch\(\|XMLHttpRequest\|^import " public` | aucune ligne | c:16 |
| 5 | Mouvement réduit | `grep -rc "prefers-reduced-motion" public/css` | au moins 1 occurrence au total | PRODUCT.md:60 |
| 6 | Clavier (statique) | `grep -rnE "tabindex=\"[1-9]\|<(div\|span)[^>]*onclick" public` | aucune ligne | PRODUCT.md:60 |
| 7 | Structure HTML | test N1 | head, puis scripts `defer`, puis body ; aucun script inline ni dans le body | bp:230 |

- **Critères manuels, par le moniteur dans Chrome** : après copie de `public/` et de la fixture dans le scratchpad (jamais de remplacement du vrai `data/state.js`). Un agent n'a pas de navigateur. Aucun banc DOM n'existe dans le dépôt (A14).
- **Cas nominaux (automatiques)**
  - N1 : structure head, scripts, body.
  - N2 : `lang="fr"`, `<title>`, viewport.
  - N3 : `state.js` chargé en script classique.
  - N4 : aucune URL absolue.
  - N5 : aucun `innerHTML` ni équivalent.
  - N6 : `prefers-reduced-motion` présent.
  - N7 : aucun `tabindex` positif ni `onclick` sur div ou span.
  - N8 : les trois statuts connus avec libellé texte, pas la couleur seule (`c:10-12`).
  - N9 : un message de repli défini par section.
  - N10 : aucun attribut `title` natif (`bp:244`).
- **Cas limites (manuels, M1 à M9)**
  - M1 : `window.SYSTEM_STATE` absent, page de repli stylée avec « Chargement impossible » et un bouton « Réessayer » (`bp:247`).
  - M2 : version de schéma inconnue, message avec la version reçue.
  - M3 : état vide, « Aucune donnée disponible » dans chaque section au même emplacement, aucun sélecteur ni compteur vide (`bp:194`).
  - M4 : une seule section manquante, les autres s'affichent (`bp:193`).
  - M5 : valeur « insuffisant » affichée avec sa raison, jamais 0 ni vide.
  - M6 : chaîne piégée de `state_piege.js` affichée littéralement.
  - M7 : parcours complet au Tab, focus visible, Entrée et Espace activent, Échap ferme.
  - M8 : `prefers-reduced-motion: reduce` émulé, aucune animation.
  - M9 : aucune barre de défilement horizontale à aucune largeur (`bp:253`).
- **Pré-mortem** : 724 nœuds et plus de 800 arêtes en rendu (performance) ; `state.js` de plusieurs Mo ; noms très longs ; navigateur sans `matchMedia` ; fichier `state.js` périmé ; texte en NFD.
- **Niveau** : tester sonnet/medium ; builder opus/high. Fidélité à la maquette, accessibilité, repli par section ; la vérification visuelle revient au moniteur.

### T12 : vérification de bout en bout

- **Entrées** : T10, T11, `c:133, c:56`, `bp:286` (README), `bp:294` (`EXTERNAL.md`).
- **Sortie** : test de bout en bout sur fixtures, passage sur données réelles hors API, rapport de vérification ; `README.md` finalisé (résumé, sommaire, fonctionnement, architecture, lancement, usage de l'IA en avant-dernière partie, contributeurs en dernière).
- **Fichiers**
  - Créés : `tests/test_bout_en_bout.py`.
  - Modifiés : `README.md`, `EXTERNAL.md` (contrôle).
  - Aucun code de production.

| # | Critère | Commande exacte | Résultat attendu | Source |
|---|---|---|---|---|
| 1 | Suite complète | `PYTHONPATH=source python3 -m unittest discover -s tests -t . -v` | `Ran` ≥ 269, `OK (skipped=3)` | c:133 |
| 2 | Synchronisation réelle sans API (`.env` réel, sans identifiants OAuth) | `PYTHONPATH=source python3 -m system_sync sync` | `data/state.js` écrit ; api42 « indisponible » ; niveau 42 et Système « insuffisant » avec raison | c:16, c:56 |
| 3 | Comptes réels | `python3 -c "import json; t=open('data/state.js',encoding='utf-8').read(); d=json.loads(t[len('window.SYSTEM_STATE = '):].rstrip().rstrip(';')); print(len(d['cartes']), len(d['relations']), len(d['anomalies']))"` (noms de champs fixés par T2) | `16 76 8` (anomalies de T3 seules, A13) | c:56, c:30 |
| 4 | Aucun secret suivi | `grep -rlE "^API42_CLIENT_SECRET=.+" --exclude=.env .` | aucun fichier (code 1) | c:39 |
| 5 | Aucune donnée personnelle dans l'état | `grep -niE "email\|phone\|login\|image\|location\|wallet" data/state.js` | aucune ligne (code 1) | c:33 |
| 6 | Git propre | `git status --short --ignored` | `data/` listé ignoré (`!! data/`), `tests/` suivi, aucun `.env` | c:143 |
| 7 | README | `grep -n '^## ' README.md \| tail -2` | « Usage de l'IA » puis « Contributeurs » | bp:286 |
| 8 | Réel avec API | non vérifiable par un agent | par Louis et le moniteur : niveau 12,44 observé, XP 133 834 estimée, api42 `ok` | c:158 |
| 9 | Page sur données réelles | non vérifiable par un agent (Chrome) | par le moniteur : 16 cartes, 10 au rang E, 6 « aucun rang », statuts visibles (critères M1 à M9 de T11) | c:56 |

- **Cas nominaux** : N1 bout en bout sur fixtures avec comptes attendus ; N2 rangs de la fixture ; N3 titres de la fixture ; N4 `public/index.html` référence `../data/state.js` et le fichier généré existe ; N5 aucun secret ni champ personnel dans `state.js` ; N6 suite complète verte.
- **Cas limites** : L1 chacune des 5 sources absente tour à tour (5 exécutions), état valide à chaque fois ; L2 `state.js` supprimé, page de repli (manuel) ; L3 relance idempotente.
- **Pré-mortem** : ajout d'une ligne `Codes` dans une carte récente (`c:160`) ; arrivée du premier fait `niveau` réel (T0) : rang D observé, puis C, A, S ; renommage d'un domaine ; `data/` supprimé entre deux synchronisations (titre acquis perdu, A7).
- **Niveau** : checker sonnet/high. Vérification sans code de production.

---

## 2. Arborescence des fixtures

```
tests/fixtures/
  config/    regles_valide.toml, regles_taux_hors_plage.toml, regles_vide.toml,
             regles_mal_forme.toml, valide.env, sans_egal.env, doublon.env
  etat/      etat_minimal.js, etat_complet.js, etat_vide.js, etat_partiel.js,
             etat_schema_inconnu.js, etat_piege.js, etat_insuffisant_sans_raison.js,
             etat_cle_inconnue.js
  professor/ suivi/{cartes/{alpha,beta}.md, notions.md, relations.csv,
             evenements.csv}, historique-ia.csv, mal_forme/
  api42/     me_valide.json, me_champs_personnels.json, me_vide.json,
             achievements_page1.json, achievements_page2.json, token.json
  table_xp/  experience_valide.json, experience_non_croissante.json,
             experience_vide.json, experience_champ_manquant.json
  rangs/     cartes_demo.json, notions_demo.json, faits_demo.json
  xp/        projets_demo.csv, historique_demo.csv, projets_42_demo.json,
             ancrage_demo.json
  titres/    rangs_trois_cartes.json, achievements_obtenus.json,
             achievements_complet.json, etat_precedent_acquis.json,
             etat_precedent_corrompu.json
  reseau/    cartes_alpha_beta.json, relations_demo.json
  sync/      valide.env, sans_api.env, sans_regles.env
```

Toutes les valeurs sont fictives (identifiants `demo-...`, domaine « Alpha », champs personnels de l'API remplis de valeurs génériques non identifiantes). Les fichiers binaires, FIFO et droits sont fabriqués par les tests dans un dossier temporaire.

## 3. Niveaux d'agent

| Tâche | Tests (étape 4) | Code (étape 5) | Justification en une ligne |
|---|---|---|---|
| T1 | sonnet/low | sonnet/medium | Structure et configuration, contenu de `rules.toml` à soigner |
| T2 | sonnet/medium | sonnet/high | Contrat de toute la chaîne, validateur écrit à la main |
| T3 | sonnet/high | sonnet/high | Cinq formats, rejets chiffrés, nombreux cas limites |
| T4 | opus/medium | opus/high | OAuth, serveur local, secrets, réseau borné |
| T5 | sonnet/medium | sonnet/medium | Petit module, hash et interpolation |
| T6 | sonnet/high | sonnet/high | Règles pures, plusieurs ambiguïtés à tenir (A8, A9) |
| T7 | opus/high | opus/high | Calibration à invariants, sous-spécifiée (A6) |
| T8 | sonnet/medium | sonnet/medium | Règles courtes, persistance à surveiller |
| T9 | sonnet/medium | sonnet/medium | Graphe simple, comptes exacts |
| T10 | sonnet/medium | sonnet/high | Orchestration, échecs partiels, atomicité |
| T11 | sonnet/medium | opus/high | Fidélité à la maquette, accessibilité, repli par section |
| T12 | checker sonnet/high | sans objet | Vérification sans code de production |

