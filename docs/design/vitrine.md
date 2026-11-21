# Plan de la vitrine (phase W)

La vitrine publie la maquette validée `mockups/system/` sur GitHub Pages, en vrai site : code au niveau de la PARTIE B, données réelles figées dans un instantané rafraîchi à la demande, déploiement automatique à chaque push. Elle passe avant la V1 (arbre de `docs/plan.md`) ; la V1 la reprend ensuite, sans repartir de la maquette (amendement A31 de `docs/design/implementation.md`).

## Sommaire

- [Décisions de Louis](#décisions-de-louis)
- [Architecture](#architecture)
- [Restrictions et secours](#restrictions-et-secours)
- [Fiches W0 à W13](#fiches-w0-à-w13)
- [Rafraîchir la vitrine](#rafraîchir-la-vitrine)
- [Hors vitrine](#hors-vitrine)

## Décisions de Louis

Le 21/11/2026, à ne pas redemander :

- Vitrine d'abord, faite à partir de la maquette avec un instantané de ses données, puis la V1, puis le pré-mortem.
- Public : Louis seul, en ligne, sur ordinateur. Pas de version téléphone ni de présentation du projet ; page en français (l'anglais vient avec la V1, A27).
- Hébergement : le dépôt `Louis-Cagnion/Solo_leveling`, rendu public par Louis le 20/11/2026 (vérifié le 21/11 : `"private": false`). Adresse : `https://louis-cagnion.github.io/Solo_leveling/`.
- Sons : publiés tels quels (`js/sound-data.js`), risque de droits assumé par Louis. Les bruits d'origine (`sound effects/`) restent exclus de Git.
- Démonstration gardée (`js/demo.js` porté, A28 amendé par A31) : données fictives activées par l'adresse. Louis garde `?demo` tel quel (réponse du 21/11/2026 à la question de début de phase) : `?demo`, `?demo=over#/status`, `?demo=events`, `?demo=red`, `?demo=red-all`, aucun code de routage à changer ; le `#` reste aux vues (`#/status`).
- Source de GitHub Pages : Louis charge le moniteur de la basculer sur « GitHub Actions » dans Chrome (réponse du 21/11/2026). Le Chrome de l'extension n'est pas connecté à GitHub (essai du 21/11/2026 : la page des réglages donne 404 et propose « Sign in ») : Louis s'y connecte lui-même, jamais de mot de passe saisi par le moniteur.

Décidé par le moniteur, modifiable par Louis à la validation : le site n'est pas indexé par les moteurs de recherche (`<meta name="robots" content="noindex">`), puisqu'il ne sert qu'à Louis.

## Architecture

```
public/                  site publié tel quel (artefact de GitHub Pages)
  index.html             roue, domaines, paliers, statut (copie de mockups/system/index.html)
  network.html           réseau 3D des notions
  404.html               adresse inconnue, à l'identité du site, lien vers l'accueil
  favicon.svg            icône d'onglet
  data.js                instantané window.SYSTEME, généré par tools/snapshot.py, versionné
  css/ js/ fonts/        repris de la maquette, js/demo.js compris (A31)
  vendor/                three.js 0.147.0 et OrbitControls.js, copiés octet pour octet
tools/snapshot.py        génère public/data.js depuis le suivi de /professor (lecture seule)
tools/sound_partials.py  génère public/js/sound-data.js depuis sound effects/ (local)
.github/workflows/pages.yml  déploie public/ à chaque push sur main qui le touche
```

- Scripts classiques avec `defer`, jamais `type="module"` : la page s'ouvre aussi en `file://`, ce que la V1 garde (`c:16`).
- Toute adresse est relative (pas de `/` en tête) : le site vit sous `/Solo_leveling/`.
- Politique de sécurité en balise `meta` dans chaque page HTML, mot pour mot : `default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'none'; object-src 'none'`. La maquette n'a aucun style en ligne (relevé le 21/11/2026), donc rien à assouplir.
- La maquette `mockups/system/` reste en local, non versionnée, comme référence visuelle jusqu'à la fin de T11.

## Restrictions et secours

Types retenus : interface web, script en ligne de commande. Chaque ligne : état attendu ; constat. Les lignes du catalogue sur le téléphone (320 et 390 px), le réseau coupé et le zoom à 200 % sont écartées : site personnel sur ordinateur (décision de Louis) ; elles vont au pré-mortem.

**Ne doit pas apparaître**

1. Aucune ressource externe ni injection HTML dans `public/` ; constat : tests S2 et S3 verts.
2. Aucun chemin local, adresse électronique ni terme interne dans `public/` ; constat : `grep -rnE '/home/|@[a-z0-9-]+\.[a-z]{2,}' public --exclude-dir=vendor` sans ligne, puis `sh ~/claude_custom_commands/tools/verifier-confidentiel.sh public/data.js` lancé seul, sans sortie.
3. Aucune donnée fictive hors démonstration : sans marqueur de démonstration dans l'adresse, la page montre les données de `data.js` sans l'avis de démonstration ; avec lui, l'avis est visible ; constat : test S6 vert, puis `index.html` et chaque adresse de démonstration ouvertes dans Chrome (W10).
4. Console vide en ligne, aucune violation de la politique de sécurité, aucune réponse 4xx ; constat : `index.html` puis `network.html` ouverts sur l'adresse publique dans Chrome, `read_console_messages` et `read_network_requests` : zéro erreur.
5. Aucune barre de défilement horizontale à 1280, 1536 et 1920 px ; constat : script « Largeurs » de W10, `scrollWidth` au plus égal à `clientWidth` sur les vues roue, domaine, palier, statut et réseau.
6. Aucun écart de rendu avec la maquette validée ; constat : W10, chaque vue côte à côte avec la maquette à 1536 px (palette, typographie, disposition, effets, sons), puis validation du rendu par Louis.

**Cas particuliers**

7. `data.js` absent ou illisible : fenêtre « Chargement impossible » avec « Réessayer », sans commande à taper ; constat : commande « Repli des données » de W5, au moins une ligne.
8. WebGL indisponible sur `network.html` : message à l'identité du site, barre du haut utilisable ; constat : commande « Repli WebGL » de W5, au moins une ligne.
9. Clavier seul : roue, domaine, palier, statut, réseau et boîte « Événements » au Tab, focus visible, Échap ferme ; constat : parcours de W10.
10. Lien direct vers une vue (`#/status`, domaine ouvert) : le rechargement rend le même écran ; constat : W10.
11. Adresse inconnue : page `404.html` à l'identité du site, avec un lien vers l'accueil ; constat : `curl -s -o /dev/null -w '%{http_code}' https://louis-cagnion.github.io/Solo_leveling/inconnue` donne `404`, puis la page ouverte dans Chrome.
12. Source du suivi absente ou illisible : `tools/snapshot.py` s'arrête, code 1, message qui nomme le chemin, ancien `public/data.js` intact ; constat : test L1 de `test_snapshot`.

**Secours**

13. Aucune dépendance externe au chargement (polices, three.js et données servis par le site) ; constat : `read_network_requests` sur les deux pages en ligne, toutes les requêtes vers `louis-cagnion.github.io`.
14. Web Audio indisponible ou son coupé : la page fonctionne sans son ; constat : `window.AudioContext = undefined; window.webkitAudioContext = undefined;` dans la console puis parcours de la roue au statut, zéro erreur.
15. Déploiement en échec : la version précédente reste en ligne et le moniteur le voit ; constat : après chaque push, `curl -s 'https://api.github.com/repos/Louis-Cagnion/Solo_leveling/actions/runs?per_page=1' | python3 -c "import json,sys; r=json.load(sys.stdin)['workflow_runs'][0]; print(r['status'], r['conclusion'])"` donne `completed success`.

## Fiches W0 à W13

Conventions : celles de `docs/design/implementation.md` §0 (95 caractères par ligne, 750 lignes par fichier, aucun tiret cadratin, une erreur par cause). Exemptés : `public/vendor/`, les licences des polices, les fichiers générés `public/data.js` et `public/js/sound-data.js`. Tout agent d'interface lit `~/.claude/references/best-practice/frontend.md` et `interface.md`, et le brief nomme les skills `frontend-design` et `impeccable`. Commandes lourdes (Chrome sans interface) : `systemd-run --user --scope -q -p MemoryMax=2G -p MemorySwapMax=0 -p CPUQuota=200% nice -n 19 timeout 90 …`, appelé « plafond » ci-dessous.

### W0 Louis : source de GitHub Pages

- Action du moniteur dans Chrome (onglet à lui, fermé ensuite), sur ordre de Louis : sur GitHub, « Settings », « Pages », « Build and deployment », « Source » : « GitHub Actions ». Prérequis : Louis connecté à GitHub dans ce Chrome ; l'essai du 21/11/2026 l'a trouvé déconnecté, donc W0 reste à faire.
- Constat : `https://louis-cagnion.github.io/Solo_leveling/network.html` ne sert plus le README Jekyll ; puis, après W11, ligne 15 de la liste ci-dessus ; un échec `deploy-pages` « Pages not enabled » veut dire que W0 n'est pas fait.
- Marqueur de la démonstration : tranché (`?demo`, cf. « Décisions de Louis »).

### W1 tester : tests rouges

- Fichiers autorisés : `tests/public/__init__.py`, `tests/public/test_site_static.py`, `tests/public/test_workflow.py`, `tests/tools/__init__.py`, `tests/tools/test_snapshot.py`, `tests/fixtures/snapshot/` (suivi fictif : `cartes/alpha.md`, `cartes/beta.md`, `notions.md`, `relations.csv` avec une ligne mal formée, au format des fichiers réels de `~/claude_custom_commands/references/professor/suivi/`, lus en lecture seule).
- `test_site_static.py` (bibliothèque standard, lit `public/`) :
  - S1 : `index.html`, `network.html`, `404.html` existent ; chacun a `<html lang="fr">`, un `<title>` non vide, la balise `viewport`, la politique de sécurité exacte de « Architecture », `noindex` et un lien vers `favicon.svg`.
  - S2 : aucune correspondance de `https?://|//[a-z0-9.-]+\.[a-z]{2,}|@import` dans les `.html`, `.css`, `.js` hors `vendor/`, l'espace de noms `http://www.w3.org/2000/svg` excepté.
  - S3 : aucune correspondance de `innerHTML|outerHTML|insertAdjacentHTML|document\.write|eval\(|new Function` hors `vendor/`.
  - S4 : aucune correspondance de `type="module"|fetch\(|XMLHttpRequest|^import ` hors `vendor/`.
  - S5 : chaque `src` et `href` local des pages et chaque `url(...)` des CSS est relatif et désigne un fichier qui existe sous `public/`.
  - S6 : `js/demo.js` présent, chargé par `index.html` avec `defer` avant `js/app.js` ; `data.js` ne contient aucun identifiant `demo-` ; `app.js` lit toujours `?demo` (au moins une correspondance de `params\.(has|get)\('demo'\)`).
  - S7 : au moins une occurrence de `prefers-reduced-motion` dans `public/css/`.
  - S8 : aucun `tabindex="[1-9]`.
  - S9 : aucune ligne de plus de 95 caractères (comptés en caractères, pas en octets) dans les `.html`, `.css`, `.js`, fichiers exemptés à part.
  - S10 : au plus 750 lignes par fichier `.css` et `.js`, fichiers exemptés à part.
  - S11 : aucun tiret cadratin (`chr(0x2014)`) hors `vendor/`.
  - S12 : chaque `<script src>` porte `defer` et se trouve entre `</head>` et `<body>` (règle « Structure d'un document HTML », `interface.md`).
  - S13 : `404.html` contient un lien vers `./` ou `index.html`.
  - S14 : `data.js` commence par `window.SYSTEME = `, son JSON se lit, et il ne contient ni `/home/` ni adresse électronique.
  - S15 : sha256 de `vendor/three.min.js` = `f34446bf875b5fb0dcd93819ffe1d9e182d46634ee855f5d904c6c4ac7cdbc95`, de `vendor/OrbitControls.js` = `b4c6e53f98538535b11fd6655627d47fb5877b3ad972568bff0a7026c4b6d5c4` (relevés sur la maquette le 21/11/2026) ; les deux licences des polices et `vendor/LICENSE` présentes.
- `test_workflow.py` (lit `.github/workflows/pages.yml` comme texte, sans paquet YAML) : W1 chaque `uses:` épinglé sur 40 caractères hexadécimaux suivis d'un commentaire de version ; W2 `permissions` avec `contents: read`, `pages: write`, `id-token: write` et rien d'autre ; W3 déclencheurs `workflow_dispatch` et `push` sur `main` limité à `public/**` et au fichier lui-même ; W4 `path: public` dans l'étape d'envoi ; W5 `timeout-minutes` présent.
- `test_snapshot.py` (lance `python3 -I tools/snapshot.py --suivi <dossier> --output <fichier>` en sous-processus, sortie dans un dossier temporaire) : N1 code 0 sur la fixture, JSON lu après `window.SYSTEME = `, 2 cartes ; N2 la sortie ne contient pas le chemin du dossier de la fixture ; N3 deux exécutions donnent la même sortie hors `meta.generatedAt` ; N4 la relation mal formée est comptée dans `rejected` ; L1 suivi absent : code 1, message qui nomme le chemin, fichier de sortie déjà présent identique (sha256) ; L2 dossier de sortie non inscriptible : code 1, message ; Q1 `tools/snapshot.py` a au plus 95 caractères par ligne et 750 lignes.
- Critère : `PYTHONPATH=source python3 -m unittest tests.public.test_site_static tests.public.test_workflow tests.tools.test_snapshot -v` échoue (rouge) sur chaque cas, aucune erreur d'import ; la suite T1 existante reste verte (`PYTHONPATH=source python3 -m unittest tests.test_architecture tests.system_sync.test_config -v`).
- Niveau pressenti : sonnet/medium.

### W2 builder : site porté dans `public/`

- But : copier `mockups/system/` dans `public/`, démonstration comprise, sans changement de rendu.
- Fichiers autorisés : `public/**` ; lus seulement : `mockups/system/**`.
- Contenu : copie de `index.html`, `network.html`, `css/`, `js/`, `fonts/`, `vendor/` (copie binaire, `cp -p`). Aucune ligne de démonstration ne change (`?demo` gardé). La mémoire de visite réelle (`progression-system:visit`) et celle de la démonstration (`:demo`) restent séparées.
- Critères : S5, S6, S15 verts ; `diff -rq mockups/system/vendor public/vendor` sans sortie ; servi par le moniteur, les deux pages s'affichent sans erreur de console (contrôle du moniteur à la relecture, sur `public/data.js` copié provisoirement de la maquette, jamais commité avant W3).
- Niveau pressenti : sonnet/medium.

### W3 builder : `tools/snapshot.py`

- But : générateur versionné de `public/data.js`, tiré de `tools/mockup_data.py` (local, ignoré par Git, laissé en place).
- Fichiers autorisés : `tools/snapshot.py`, `public/data.js`.
- Interface : `python3 -I tools/snapshot.py [--suivi DOSSIER] [--output FICHIER]` ; défauts : `PROFESSOR_SUIVI_DIR`, sinon `~/claude_custom_commands/references/professor/suivi` ; `public/data.js`. Écriture atomique (fichier temporaire du même dossier, puis `os.replace`) ; code 1 et message qui nomme la cause et le chemin sur toute source illisible ; aucun chemin absolu dans la sortie ; bibliothèque standard seulement.
- Critères : `python3 -m unittest tests.tools.test_snapshot -v` vert ; `python3 -I tools/snapshot.py` sur le suivi réel, code 0, comptes affichés ; S14 vert ; lignes 2 et 12 de « Restrictions et secours ».
- Niveau pressenti : sonnet/medium.

### W4 builder : conformité PARTIE B de `public/`

- But : mettre le code porté aux conventions, rendu inchangé.
- Fichiers autorisés : `public/css/**`, `public/js/**` sauf `sound-data.js`, `public/*.html` (seulement pour charger les CSS scindées).
- Contenu : scinder `css/views.css` (756 lignes) en fichiers de 750 lignes au plus, par vue ; ramener sous 95 caractères les 33 lignes relevées le 21/11/2026 (`app.js` 1, `certs.js` 2, `demo.js` 1, `dom.js` 1, `effects.js` 1, `events.js` 3, `inbox.js` 1, `model.js` 5, `network-ui.js` 1, `scene.js` 1, `wheel.js` 1, `effects.css` 2, `inbox.css` 2, `network.css` 1, `views.css` 1, `wheel.css` 2, `wheel-fx.css` 1, `window.css` 5) ; relire chaque fichier contre `~/.claude/references/best-practice/code.md` et signaler dans le rapport tout autre écart, corrigé seulement s'il ne change pas le rendu.
- Critères : S9, S10, S11 verts ; aucune règle CSS perdue (nombre total de sélecteurs avant et après égal, compté par le rapport) ; le moniteur compare les vues à la maquette avant de valider.
- Niveau pressenti : sonnet/high (régression visuelle possible sans navigateur).

### W5 builder : finitions du site

- Fichiers autorisés : `public/*.html`, `public/404.html`, `public/favicon.svg`, `public/js/dom.js`, `public/js/app.js`, `public/js/network-ui.js`, tout fichier `public/js/` qui lit `localStorage`.
- Contenu : balises de S1 dans chaque page (politique de sécurité, `noindex`, icône) ; `404.html` dans le style des fenêtres du Système, mêmes polices et CSS, lien « Retour à l'accueil » vers `./` ; `favicon.svg` repris de l'hexagone de l'icône « Événements » (`index.html`), aux couleurs de la charte ; texte de `dataFailureWindow` (`js/dom.js`) qui dit que le fichier de données du site est absent ou illisible, sans commande à taper ; chaque accès à `localStorage` dans un `try`, la page fonctionnant sans mémoire de visite.
- Critères : S1, S13 verts ; puis, au plafond :
  - « Repli des données » : `d=$(mktemp -d) && cp -r public/. "$d" && rm "$d/data.js"` puis `google-chrome --headless=new --disable-gpu --no-first-run --user-data-dir="$(mktemp -d)" --virtual-time-budget=8000 --dump-dom "file://$d/index.html" | grep -c "Chargement impossible"` : au moins 1 ;
  - « Repli WebGL » : même commande avec `--disable-webgl --disable-3d-apis` sur `file://$PWD/public/network.html`, `grep -c "WebGL"` : au moins 1.
- Niveau pressenti : sonnet/high.

### W6 builder : outil des sons versionné

- Fichiers autorisés : `tools/sound_partials.py`, `public/js/sound-data.js`.
- Contenu : `OUTPUT` vers `public/js/sound-data.js` ; mise aux conventions (95 caractères, docstrings) sans changer le calcul.
- Critères : `sha256sum public/js/sound-data.js` avant, puis `python3 -I tools/sound_partials.py`, puis même empreinte ; aucune ligne de plus de 95 caractères dans l'outil ; `sound effects/` toujours ignoré (`git check-ignore -v "sound effects/"` répond par `.git/info/exclude`).
- Niveau pressenti : sonnet/low.

### W7 builder : déploiement

- Fichiers autorisés : `.github/workflows/pages.yml`.
- Contenu : déclencheurs et droits de `test_workflow.py` ; `concurrency` de groupe `pages` sans annulation ; une tâche `deploy` sur `ubuntu-latest`, `timeout-minutes: 10`, environnement `github-pages` ; étapes `actions/checkout`, `actions/configure-pages`, `actions/upload-pages-artifact` (`path: public`), `actions/deploy-pages`. Chaque action épinglée sur le SHA de sa dernière version publiée depuis au moins deux semaines, relevé par `git ls-remote --tags https://github.com/actions/<nom>` (ligne `^{}` du tag), version en commentaire.
- Critères : `PYTHONPATH=source python3 -m unittest tests.public.test_workflow -v` vert ; rapport qui donne chaque tag, sa date et son SHA.
- Niveau pressenti : sonnet/medium.

### W8 analyst : revue indépendante (étape 6)

- Entrées : diff de W2 à W7, ce fichier, `mockups/system/` comme référence.
- Contenu : relecture contre la PARTIE B (`code.md`), `interface.md`, `frontend.md` et la liste « Restrictions et secours » : verdict par ligne jouable sans navigateur (1, 2, 3 par grep, 7, 8, 12), les autres marquées « au moniteur » ; problèmes classés CRITIQUE, IMPORTANT, MINEUR ; conclusion VALIDÉ ou À CORRIGER. Les MINEURS vont au pré-mortem (`todo.md`), sans feuille.
- Niveau pressenti : opus/high (plus haut que le moniteur, pour couvrir le risque, cf. « Niveau du moniteur », `agents.md`).

### W9 fixer : corrections

- Une feuille par problème CRITIQUE ou IMPORTANT de W8, niveau jaugé sur le problème ; puis le test ou la commande qui le constate, rejoué.

### W10 moniteur : rendu dans Chrome, validé par Louis

- Serveur : `timeout 3600 python3 -m http.server 5621 --bind 127.0.0.1` lancé à la racine du dépôt ; vitrine `http://127.0.0.1:5621/public/index.html` et `network.html`, maquette `http://127.0.0.1:5621/mockups/system/index.html` et `network.html`. Contenus différents (instantané du jour contre celui de la maquette) : seul le rendu se compare.
- Vues comparées côte à côte à 1536 px : roue, domaine, palier, carte de certification, statut, boîte « Événements », réseau « Amas » puis « Arbre ». Sons : `open` à l'ouverture de « Événements ».
- « Largeurs » : dans un onglet de la vitrine, `for (const w of [1280, 1536, 1920]) { const f = document.createElement('iframe'); f.style.width = w + 'px'; f.style.height = '900px'; f.src = location.href; document.body.append(f); }`, puis après chargement, pour chaque cadre, `f.contentDocument.documentElement.scrollWidth <= f.contentDocument.documentElement.clientWidth`.
- Démonstration : les cinq adresses de démonstration retenues (avis visible, rangs fictifs, dépassement, événements, domaines rouges), puis `index.html` sans marqueur (aucun avis).
- Lignes 3, 5, 9, 10 et 14 jouées ; puis l'onglet reste ouvert sur la roue pour Louis (une notification, une question : rendu validé ou retouches).

### W11 moniteur : mise en ligne

- Dépend de W0 et W10. Commit de `.github/workflows/pages.yml` puis push ; lignes 15, 11, 13 et 4 jouées sur l'adresse publique (`index.html`, `network.html`, `data.js` en 200).

### W12 checker : point de contrôle

- Suite complète `PYTHONPATH=source python3 -m unittest discover -s tests -t . -v` : tests de T1 et de la vitrine verts, tests rouges de T2.a déjà présents comptés à part (ils restent rouges jusqu'à T2.b) ; chaque ligne de « Restrictions et secours » reçoit un verdict avec sa preuve, celles déjà jouées par le moniteur reprises de son relevé ; compte des lignes tenues sur 15.
- Niveau pressenti : sonnet/high.

### W13 moniteur : clôture de la vitrine

- `README.md` : « État actuel », « Structure » (`public/`, `tools/`, `.github/`) et une section « Publication » qui reprend « Rafraîchir la vitrine » ; `PRODUCT.md` relu ; contexte des agents (`~/claude_custom_commands/references/projects/progression-system/contexte.md`) mis à jour, commit isolé dans le dépôt des commandes ; arbre de `docs/plan.md` condensé ; `todo.md` et sa ligne de reprise sur T2.a2.

## Rafraîchir la vitrine

Le suivi de `/professor` change presque chaque jour (commits sur les cartes ou `notions.md` 14 jours sur 15 du 07 au 21/11/2026) : l'instantané se rafraîchit à la demande de Louis, jamais de lui-même, tant que la V1 ne publie pas.

1. `python3 -I tools/snapshot.py` : code 0, comptes affichés.
2. Lignes 1 et 2 de « Restrictions et secours », puis `PYTHONPATH=source python3 -m unittest tests.public.test_site_static -v` vert.
3. Commit `Vitrine : instantané des données du JJ/MM/AAAA` de `public/data.js` seul, puis push.
4. Ligne 15, puis `index.html` en ligne (le cache de GitHub Pages peut garder l'ancienne version jusqu'à 10 minutes).

## Hors vitrine

Vont au pré-mortem (`todo.md`), jamais dans cette phase : largeurs de téléphone, zoom à 200 %, réseau coupé après chargement, `prefers-reduced-motion` émulé, contrastes mesurés paire par paire, cache de 10 minutes de GitHub Pages, rotation calée sur le temps écoulé (écran à 144 Hz), `localStorage` bloqué par le navigateur.
