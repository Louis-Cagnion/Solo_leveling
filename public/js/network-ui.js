'use strict';

/*
 * Maquette « Système » : page du réseau des notions, autour de la scène 3D.
 *
 * Premier écran : le réseau seul, en arbre autour de sa notion racine. À gauche, le choix
 * de la disposition et la légende des types et des statuts de lien ; cliquer un type
 * filtre le réseau. À droite, la liste des connexions, un groupe repliable par type,
 * fermé par défaut. Le détail ne s'ouvre qu'au clic sur une connexion (liste ou lien de
 * la scène) ; cliquer une notion met ses liens en avant, réduit la liste à ceux-ci et
 * permet de centrer l'arbre sur elle. Le choix vit dans le fragment d'adresse (layout,
 * root, kind, node, link).
 */

const PROOF_TIP = 'Référence de la preuve dans le suivi : session, notion, puis mesure.';
const LIMIT_TIP = 'Ce qui empêche de transposer telle quelle une notion vers l’autre.';

/**
 * Choix lu dans le fragment d'adresse, valeurs absentes à null ; une disposition
 * inconnue vaut la première de LAYOUT_MODES.
 *
 * @param {string} hash fragment, avec ou sans « # »
 * @returns {{layout: string, root: ?string, kind: ?string, node: ?string, link: ?number}}
 */
function readChoice(hash) {
  const params = new URLSearchParams(hash.replace(/^#/, ''));
  const link = Number.parseInt(params.get('link'), 10);
  const layout = params.get('layout');
  return {
    layout: LAYOUT_MODES.some(mode => mode.code === layout) ? layout : LAYOUT_MODES[0].code,
    root: params.get('root'),
    kind: params.get('kind'),
    node: params.get('node'),
    link: Number.isInteger(link) ? link : null,
  };
}

/** Fragment d'adresse du choix choice, clés nulles et disposition par défaut omises. */
function choiceHash(choice) {
  const params = new URLSearchParams();
  for (const key of ['layout', 'root', 'kind', 'node', 'link']) {
    const value = choice[key];
    const implied = key === 'layout' && value === LAYOUT_MODES[0].code;
    if (value !== null && value !== undefined && !implied) params.set(key, value);
  }
  return `#${params}`;
}

/** Boutons du choix de disposition, celui de current enfoncé, définition en infobulle. */
function layoutSwitch(current) {
  return el('ul', {className: 'layout-modes'}, LAYOUT_MODES.map(mode => el(
    'li',
    {},
    el('button', {
      className: 'layout-mode',
      text: mode.label,
      attrs: {
        type: 'button',
        'data-layout': mode.code,
        'aria-pressed': String(mode.code === current),
        'data-tip': `« ${mode.label} » : ${mode.meaning}.`,
      },
    }),
  )));
}

/**
 * Vue du réseau pour un choix : ce que la scène affiche, met en avant et étiquette, et
 * les liens de la liste.
 *
 * @param {Object} network résultat de buildNetwork
 * @param {{kind: ?string, node: ?string, link: ?number}} choice choix courant
 * @param {?string} root racine de la disposition, toujours étiquetée si elle est affichée
 * @returns {{nodes: Set, links: Set, focus: ?Set, focusLinks: ?Set, labels: string[],
 *   selected: ?string, listed: Object[], link: ?Object}} link : lien choisi s'il est
 *   affiché ; listed : liens de la liste
 */
function buildView(network, choice, root) {
  const shown = network.links.filter(link => !choice.kind || link.kind === choice.kind);
  const nodes = linkedIds(shown);
  const selected = nodes.has(choice.node) ? choice.node : null;
  const touching = selected
    ? shown.filter(entry => entry.source === selected || entry.target === selected)
    : null;
  const link = (touching || shown).find(entry => entry.index === choice.link) || null;
  const focused = link ? [link] : touching;
  return {
    nodes,
    links: new Set(shown.map(entry => entry.index)),
    focus: focused ? linkedIds(focused) : null,
    focusLinks: focused ? new Set(focused.map(entry => entry.index)) : null,
    labels: [...new Set([...(link ? [link.source, link.target] : [selected]), root])]
      .filter(Boolean),
    selected,
    listed: touching || shown,
    link,
  };
}

/** Trait d'exemple d'un lien : couleur du type, épaisseur et motif du statut. */
function linkSwatch(kind, status) {
  const swatch = el('span', {
    className: 'swatch',
    attrs: {'data-pattern': status.pattern, 'aria-hidden': 'true'},
  });
  swatch.style.setProperty('--swatch-color', `var(${kind.style.token})`);
  const width = Math.max(2, Math.round(status.radius * 12));
  swatch.style.setProperty('--swatch-width', `${width}px`);
  return swatch;
}

/** Pictogramme entre les deux notions d'un lien : flèche si le type est orienté. */
function linkArrow(kind) {
  const path = kind.directed ? 'M2 8H13M9.5 4.5L13 8L9.5 11.5' : 'M2 6H14M2 10H14';
  return svgEl(
    'svg',
    {class: 'icon link-arrow', viewBox: '0 0 16 16', 'aria-hidden': 'true'},
    svgEl('path', {d: path}),
  );
}

/** Texte lu d'un lien : « A, prérequis de, B ». */
function linkSentence(data, network, link) {
  const kind = kindInfo(data, link.kind);
  const name = id => shortLabel(network.byId.get(id).label);
  return `${name(link.source)}, ${kind.outgoing}, ${name(link.target)}`;
}

/** Bouton d'une connexion de la liste : trait, « A → B » en titres courts. */
function connectionButton(data, network, link, pressed) {
  const kind = kindInfo(data, link.kind);
  const name = id => shortLabel(network.byId.get(id).label);
  return el(
    'button',
    {
      className: 'connection',
      attrs: {
        type: 'button',
        'data-link': link.index,
        'aria-pressed': String(pressed),
        'aria-label': linkSentence(data, network, link),
      },
    },
    linkSwatch(kind, statusStyle(link.status)),
    el(
      'span',
      {className: 'connection-text'},
      name(link.source),
      linkArrow(kind),
      name(link.target),
    ),
  );
}

/**
 * Liste des connexions de view : un groupe repliable par type, ou le texte qui dit qu'il
 * n'y en a pas. Un groupe est ouvert s'il est seul, s'il contient le lien choisi ou si
 * son type figure dans opened ; fermé sinon.
 *
 * @param {Object} data objet window.SYSTEME
 * @param {Object} network résultat de buildNetwork
 * @param {Object} view résultat de buildView
 * @param {Set<string>} opened codes des types ouverts à la main
 * @returns {HTMLElement[]}
 */
function connectionList(data, network, view, opened) {
  if (!view.listed.length) {
    return [el('p', {className: 'empty', text: 'Aucune connexion à afficher.'})];
  }
  const kinds = kindSummary(data, view.listed);
  return kinds.map(kind => {
    const open = kinds.length === 1 || view.link?.kind === kind.code || opened.has(kind.code);
    return el(
      'details',
      {className: 'connection-group', attrs: {'data-kind': kind.code, open: open && ''}},
      el(
        'summary',
        {},
        linkSwatch(kind, statusStyle('demonstrated')),
        el('span', {text: capitalizeFirst(kind.label)}),
        el('span', {className: 'legend-count', text: String(kind.count)}),
        icon('chevron'),
      ),
      el('ul', {}, view.listed.filter(link => link.kind === kind.code).map(link => el(
        'li',
        {},
        connectionButton(data, network, link, view.link?.index === link.index),
      ))),
    );
  });
}

/** Légende des types : un bouton filtre par type, sa définition en infobulle. */
function kindLegend(data, network, choice) {
  const kinds = kindSummary(data, network.links);
  if (!kinds.length) return el('p', {className: 'empty', text: 'Aucun type de lien.'});
  return el('ul', {className: 'legend-list'}, kinds.map(kind => el(
    'li',
    {},
    el(
      'button',
      {
        className: 'legend-kind',
        attrs: {
          type: 'button',
          'data-kind': kind.code,
          'aria-pressed': String(choice.kind === kind.code),
        },
      },
      linkSwatch(kind, statusStyle('demonstrated')),
      el('span', {text: capitalizeFirst(kind.label)}),
      el('span', {className: 'legend-count', text: String(kind.count)}),
    ),
    info(`« ${kind.label} » : ${kind.style.meaning}.`),
  )));
}

/** Légende des statuts : épaisseur et trait de chacun, sa définition en infobulle. */
function statusLegend(data, network) {
  const neutral = {style: {token: '--text'}};
  const statuses = statusSummary(data, network.links);
  if (!statuses.length) return el('p', {className: 'empty', text: 'Aucun statut de lien.'});
  return el('ul', {className: 'legend-list'}, statuses.map(status => el(
    'li',
    {className: 'legend-status'},
    linkSwatch(neutral, status.style),
    el('span', {text: capitalizeFirst(status.label)}),
    el('span', {className: 'legend-count', text: String(status.count)}),
    info(`« ${status.label} » : ${status.style.meaning}.`),
  )));
}

/** Notion d'un bout de lien : titre court, libellé complet en infobulle. */
function endpoint(network, id) {
  const label = network.byId.get(id).label;
  return el('span', {
    className: 'detail-end',
    text: shortLabel(label),
    attrs: tipAttrs(frenchSpacing(label.replace(/`/g, ''))),
  });
}

/** Limite et preuve d'un lien, repliées derrière « Voir la preuve », ou le texte d'absence. */
function proofBlock(link) {
  if (!link.limit && !link.proof) {
    return el('p', {className: 'empty', text: 'Aucune preuve enregistrée pour ce lien.'});
  }
  const line = (term, value, tip) => value && [
    el('dt', {}, term, info(tip)),
    el('dd', {}, richText(value)),
  ];
  return el(
    'details',
    {className: 'proof'},
    el('summary', {text: 'Voir la preuve'}),
    el(
      'dl',
      {},
      line('Preuve', link.proof, PROOF_TIP),
      line('Limite', link.limit, LIMIT_TIP),
    ),
  );
}

/** Fenêtre de détail d'un lien : A, sens du lien, B, type, statut, preuve repliée. */
function detailWindow(data, network, link) {
  const kind = kindInfo(data, link.kind);
  const status = statusStyle(link.status);
  const close = el(
    'button',
    {className: 'detail-close', attrs: {type: 'button', 'aria-label': 'Fermer la connexion'}},
    icon('close'),
  );
  return systemWindow(
    {title: 'Connexion', className: 'detail-window'},
    close,
    el(
      'p',
      {className: 'detail-pair'},
      endpoint(network, link.source),
      el('span', {className: 'detail-phrase', text: kind.outgoing}),
      endpoint(network, link.target),
    ),
    el(
      'p',
      {className: 'detail-meta'},
      linkSwatch(kind, status),
      el('span', {text: `Type : ${kind.label}`}),
      info(`« ${kind.label} » : ${kind.style.meaning}.`),
      el('span', {text: `Statut : ${statusLabel(data, link.status)}`}),
      info(`« ${statusLabel(data, link.status)} » : ${status.meaning}.`),
    ),
    proofBlock(link),
  );
}

/** Phrase de portée de la liste : nombre de connexions, filtre et notion choisie. */
function scopeText(data, network, choice, view) {
  const total = network.links.length;
  const count = `${view.listed.length} ${view.listed.length > 1 ? 'connexions' : 'connexion'}`;
  if (view.selected) {
    return `${count} de « ${shortLabel(network.byId.get(view.selected).label)} »`;
  }
  if (choice.kind) {
    return `${count} de type « ${kindInfo(data, choice.kind).label} » sur ${total}`;
  }
  return count;
}

/** Démarre la page du réseau : données, scène, panneaux et écouteurs. */
function startNetwork() {
  const data = window.SYSTEME;
  const tip = byId('tip');
  const tips = initTips(tip);
  const page = byId('view');
  initSound(byId('sound-toggle'));
  if (!isDataObject(data)) {
    page.replaceChildren(dataFailureWindow());
    return;
  }
  const network = buildNetwork(data);
  const inbox = initInbox(
    {
      button: byId('inbox-toggle'),
      count: byId('inbox-count'),
      panel: byId('inbox'),
      layer: byId('unlocks'),
    },
    snapshotOf(data),
    visitStore(VISIT_KEY),
  );
  const parts = {
    kinds: byId('kinds'),
    statuses: byId('statuses'),
    scope: byId('scope'),
    list: byId('connections'),
    detail: byId('detail'),
    showAll: byId('show-all'),
    stage: byId('stage'),
    layouts: byId('layouts'),
    rootLine: byId('root-line'),
    center: byId('center-node'),
  };
  const opened = new Set();
  let shownLink = null;
  const go = changes => {
    location.hash = choiceHash({...readChoice(location.hash), ...changes});
  };
  const mounted = {scene: null, key: null, root: null};
  const handlers = {
    onPick: ({node, link}) => go({node, link}),
    onHover: (id, rect) => {
      tip.hidden = !id;
      if (!id) return;
      const node = network.byId.get(id);
      const state = node.state || 'absente du suivi';
      tip.textContent = frenchSpacing(`${shortLabel(node.label)}. État : ${state}.`);
      placeTip(tip, {getBoundingClientRect: () => rect});
    },
    onFailure: message => showStageMessage(parts.stage, message),
  };

  /** Monte la scène de la disposition et de la racine de choice, si elles ont changé. */
  const mount = choice => {
    const key = `${choice.layout}|${choice.root}`;
    if (key === mounted.key) return;
    mounted.key = key;
    mounted.scene?.dispose();
    mounted.scene = null;
    const layout = layoutFor(network, choice.layout, choice.root);
    mounted.root = layout.root;
    if (!network.links.length) {
      showStageMessage(parts.stage, 'Aucune relation entre notions dans le suivi.');
      return;
    }
    parts.stage.querySelector('.stage-message')?.remove();
    try {
      mounted.scene = createScene(parts.stage, data, network, layout, handlers);
    } catch (error) {
      showStageMessage(parts.stage, error.message);
    }
  };
  parts.statuses.replaceChildren(statusLegend(data, network));

  const show = () => {
    const choice = readChoice(location.hash);
    mount(choice);
    const view = buildView(network, choice, mounted.root);
    tips.hide();
    parts.layouts.replaceChildren(layoutSwitch(choice.layout));
    parts.rootLine.textContent = mounted.root
      ? frenchSpacing(`Racine : ${shortLabel(network.byId.get(mounted.root).label)}`)
      : 'Sans racine : notions groupées par domaine.';
    parts.center.hidden = !view.selected || !mounted.root || view.selected === mounted.root;
    parts.kinds.replaceChildren(kindLegend(data, network, choice));
    parts.scope.textContent = frenchSpacing(scopeText(data, network, choice, view));
    parts.list.replaceChildren(...connectionList(data, network, view, opened));
    const detail = view.link ? [detailWindow(data, network, view.link)] : [];
    parts.detail.replaceChildren(...detail);
    parts.showAll.hidden = !choice.kind && !view.selected && !view.link;
    const linkIndex = view.link ? view.link.index : null;
    if (linkIndex !== shownLink) playSound(view.link ? 'open' : 'close');
    shownLink = linkIndex;
    mounted.scene?.applyView(view);
  };
  parts.layouts.addEventListener('click', event => {
    const button = event.target.closest('[data-layout]');
    if (button) go({layout: button.dataset.layout});
  });
  parts.center.addEventListener('click', () => {
    go({root: readChoice(location.hash).node});
  });
  parts.kinds.addEventListener('click', event => {
    const button = event.target.closest('[data-kind]');
    if (!button) return;
    const kind = button.dataset.kind;
    go({kind: readChoice(location.hash).kind === kind ? null : kind, node: null, link: null});
  });
  parts.list.addEventListener('click', event => {
    const button = event.target.closest('[data-link]');
    if (!button) return;
    const link = Number(button.dataset.link);
    go({link: readChoice(location.hash).link === link ? null : link});
  });
  parts.list.addEventListener('toggle', event => {
    const kind = event.target.dataset?.kind;
    if (!kind) return;
    if (event.target.open) opened.add(kind);
    else opened.delete(kind);
  }, true);
  parts.detail.addEventListener('click', event => {
    if (event.target.closest('.detail-close')) go({link: null});
  });
  parts.showAll.addEventListener('click', () => go({kind: null, node: null, link: null}));
  byId('reset-view').addEventListener('click', () => mounted.scene?.resetView());
  document.addEventListener('keydown', event => {
    if (event.key !== 'Escape') return;
    const choice = readChoice(location.hash);
    if (inbox.isOpen() || inbox.dismiss()) return;
    if (tips.isOpen()) tips.hide();
    else if (choice.link !== null) go({link: null});
    else if (choice.node) go({node: null});
    else if (choice.kind) go({kind: null, node: null, link: null});
  });
  addEventListener('hashchange', show);
  show();
}

/**
 * Affiche dans stage un message stylé quand le rendu 3D est impossible ou vide ; la
 * couche des étiquettes reste en place pour une scène montée plus tard.
 */
function showStageMessage(stage, message) {
  stage.querySelector('.stage-message')?.remove();
  stage.querySelector('canvas')?.remove();
  stage.append(el('p', {
    className: 'stage-message',
    text: `Vue 3D indisponible : ${message} La liste « Connexions » reste utilisable.`,
  }));
}

document.addEventListener('DOMContentLoaded', startNetwork);
