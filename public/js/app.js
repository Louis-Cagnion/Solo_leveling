'use strict';

/*
 * Maquette « Système » : routage par l'adresse et page de repli.
 *
 * L'état vit dans le fragment d'adresse : « #/ » la roue, « #/c/<carte> » un domaine,
 * « #/c/<carte>/<palier> » un palier, « #/status » la fenêtre de statut. Recharger,
 * partager ou revenir en arrière rend le même écran. Échap ferme l'infobulle ouverte,
 * sinon remonte d'un niveau. Descendre d'un niveau joue le son d'ouverture, remonter
 * celui de fermeture (sound.js). « #/status/<certification> » et
 * « #/c/<carte>/cert/<rang> » ouvrent la carte d'une certification au premier plan.
 * « ?demo » dans l'adresse charge les données fictives de demo.js, signalées dans la
 * barre du haut : « ?demo=over » y ajoute un niveau 42 au-delà de sa cible, « ?demo=red »
 * et « ?demo=red-all » des domaines aux notions toutes au moins rouges, « ?demo=events »
 * une visite précédente fictive qui déclenche l'annonce (inbox.js).
 */

const PAGE_TITLE = 'Système de progression';
const ROUTE_DEPTHS = {wheel: 0, status: 1, section: 1, tier: 2, cert: 2};

/**
 * Route décrite par un fragment d'adresse.
 *
 * parseRoute('#/c/linux/beginner') -> {name: 'tier', card: 'linux', tier: 'beginner'}
 *
 * @param {string} hash fragment, avec ou sans « # »
 * @returns {{name: string, card?: string, tier?: string}} name : wheel, section, tier
 *   ou status ; un fragment inconnu renvoie la roue
 */
function parseRoute(hash) {
  const parts = hash.replace(/^#\/?/, '').split('/').filter(Boolean).map(part => {
    try {
      return decodeURIComponent(part);
    } catch {
      return part;
    }
  });
  if (parts[0] === 'status') return {name: 'status', cert: parts[1]};
  if (parts[0] === 'c' && parts[2] === 'cert' && parts[3]) {
    return {name: 'section', card: parts[1], cert: `${parts[1]}.${parts[3]}`};
  }
  if (parts[0] === 'c' && parts[2]) return {name: 'tier', card: parts[1], tier: parts[2]};
  if (parts[0] === 'c' && parts[1]) return {name: 'section', card: parts[1]};
  return {name: 'wheel'};
}

/** Fragment du niveau au-dessus de route, ou null depuis la roue. */
function parentHash(route) {
  if (route.name === 'tier') return `#/c/${encodeURIComponent(route.card)}`;
  return route.name === 'wheel' ? null : '#/';
}

/** Affiche la vue de la route courante dans root ; renvoie le titre de l'onglet. */
function renderRoute(root, data, route, session) {
  const card = dataCards(data).find(entry => entry?.id === route.card);
  const tier = cardTiers(card).find(entry => entry?.code === route.tier);
  const origin = session.origin;
  session.origin = null;
  if (route.name === 'status') {
    renderStatus(root, data, route.cert);
    return 'Statut';
  }
  if (route.name === 'wheel') {
    renderWheel(root, data, {
      intro: !session.introPlayed,
      onOrigin: point => {
        session.origin = point;
      },
    });
    session.introPlayed = true;
    return null;
  }
  if (!card || (route.name === 'tier' && !tier)) {
    const missing = card ? `le palier « ${route.tier} »` : `le domaine « ${route.card} »`;
    root.replaceChildren(systemWindow(
      {title: 'Introuvable', className: 'fatal'},
      el('p', {text: `Le suivi ne contient pas ${missing}.`}),
      el('a', {className: 'button', text: 'Revenir à la roue', attrs: {href: '#/'}}),
    ));
    return 'Introuvable';
  }
  if (route.name === 'tier') {
    renderTier(root, data, card, tier);
    return `${card.name}, palier ${tier.label}`;
  }
  renderSection(root, data, card, origin, route.cert);
  return card.name;
}

/** Signale les données fictives dans la barre du haut, avec le lien qui rend les vraies. */
function showDemoNotice() {
  document.querySelector('.topnav').prepend(el('a', {
    className: 'button',
    text: 'Données fictives : revenir aux données réelles',
    attrs: {href: 'index.html'},
  }));
}

/**
 * Mémoire de visite selon le mode de « ?demo » : la vraie hors démonstration, une à part
 * sous « ?demo », et une visite précédente fictive, jamais conservée, sous « ?demo=events ».
 *
 * @param {string|null} mode valeur de « ?demo », null hors démonstration
 * @param {Object} snapshot résultat de snapshotOf pour la visite courante
 * @returns {Object} résultat de visitStore ou de memoryStore
 */
function visitStoreFor(mode, snapshot) {
  if (mode === 'events') {
    return memoryStore({snapshot: demoPastVisit(snapshot), events: [], unread: 0});
  }
  return visitStore(mode === null ? VISIT_KEY : `${VISIT_KEY}:demo`);
}

/** Démarre la page : données, infobulle, boîte d'événements, routage et touche Échap. */
function startApp() {
  const root = byId('view');
  const source = window.SYSTEME;
  const tips = initTips(byId('tip'));
  if (!isDataObject(source)) {
    root.replaceChildren(dataFailureWindow());
    return;
  }
  const params = new URLSearchParams(location.search);
  const demo = params.has('demo');
  const data = demo ? withDemoData(source, params.get('demo')) : source;
  if (demo) showDemoNotice();
  initSound(byId('sound-toggle'));
  const snapshot = snapshotOf(data);
  const inbox = initInbox(
    {
      button: byId('inbox-toggle'),
      count: byId('inbox-count'),
      panel: byId('inbox'),
      layer: byId('unlocks'),
    },
    snapshot,
    visitStoreFor(params.get('demo'), snapshot),
  );
  const session = {origin: null, introPlayed: false, started: false, depth: 0, view: null};
  const statusLink = byId('nav-status');
  const show = () => {
    const route = parseRoute(location.hash);
    tips.hide();
    const title = renderRoute(root, data, route, session);
    document.title = title ? `${title}, ${PAGE_TITLE}` : PAGE_TITLE;
    if (route.name === 'status') statusLink.setAttribute('aria-current', 'page');
    else statusLink.removeAttribute('aria-current');
    const view = `${route.name} ${route.card || ''} ${route.tier || ''}`;
    if (view !== session.view) scrollTo(0, 0);
    session.view = view;
    const depth = ROUTE_DEPTHS[route.cert ? 'cert' : route.name];
    if (session.started) {
      root.focus({preventScroll: true});
      playSound(depth > session.depth ? 'open' : 'close');
    }
    session.depth = depth;
    session.started = true;
  };
  addEventListener('hashchange', show);
  document.addEventListener('keydown', event => {
    if (event.key !== 'Escape' || document.querySelector('dialog[open]')) return;
    if (tips.isOpen()) {
      tips.hide();
      return;
    }
    if (inbox.isOpen() || inbox.dismiss()) return;
    const parent = parentHash(parseRoute(location.hash));
    if (parent) location.hash = parent;
  });
  show();
}

document.addEventListener('DOMContentLoaded', startApp);
