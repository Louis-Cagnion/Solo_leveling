'use strict';

/*
 * Maquette « Système » : niveau 2 (un domaine et ses quatre paliers) et niveau 3 (le
 * détail des notions d'un palier).
 *
 * Niveau 2 : chaque notion est un signe d'état, à la couleur de rareté de son état,
 * suivi de son titre seul ; le libellé complet et l'état s'ouvrent au survol.
 * Niveau 3 : tableau du libellé complet, de l'état, de l'objectif et de la dernière
 * pratique. Un palier prend le ton de l'état le plus bas de ses notions (tierTone). Les
 * définitions des infobulles viennent de la méthode de /professor (tableau des états,
 * « Classe d'une notion »). Les certifications du domaine sont dans certs.js.
 */

const STATE_PROOFS = {
  'découverte': 'rencontrée en session',
  'en cours': 'travaillée, sans preuve de compréhension pour l’instant',
  'comprise': 'restituée avec ses propres mots, note d’au moins 4 sur 5',
  'appliquée': 'utilisée presque sans aide dans une tâche, un exercice ou un projet',
  'retenue': 'deux rappels différés réussis, dont un à 21 jours ou plus',
  'transférée': 'exercice réussi hors du contexte d’apprentissage',
  'transcendée': 'restitution parfaite et rappel réussi à 60 jours ou plus',
  'déclarée': 'maîtrise affirmée par Louis, sans preuve, à vérifier au premier rappel',
  'non rencontrée': 'jamais rencontrée en session',
};
const OBJECTIVE_TIP = [
  'Place de la notion dans le suivi.',
  '« socle » : notion générale, révisée selon le calendrier complet.',
  '« projet (nom) » : sert ce projet, révisée avant ses évaluations.',
  '« hors objectif » : détail expliqué une fois, sans rappel.',
  '« déclarée » : maîtrise affirmée, pas encore vérifiée.',
  '« non suivie » : la notion n’est pas encore entrée dans le suivi.',
].join('\n');
const PRACTICE_TIP = 'Date de la dernière session où la notion a été travaillée.';

/** État d'une notion en toutes lettres ; « non rencontrée » si la notion manque. */
function notionState(notion) {
  return notion?.state || 'non rencontrée';
}

/** Signe d'état de l'état state : forme de son rendu, couleur de son niveau de rareté. */
function glyphOf(data, state) {
  return stateGlyph(stateGroup(data, state), stateLevel(data, state));
}

/** Légende des états, du plus rare au plus commun : signe, nom et preuve en infobulle. */
function stateLegend(data) {
  const order = Array.isArray(data.proofOrder) ? data.proofOrder : [];
  const others = (Array.isArray(data.states) ? data.states : [])
    .map(entry => entry?.label)
    .filter(label => typeof label === 'string' && !order.includes(label));
  return el(
    'ul',
    {className: 'state-legend', attrs: {'aria-label': 'États des notions'}},
    [...order].reverse().concat(others).map(state => el(
      'li',
      {},
      glyphOf(data, state),
      el('span', {text: capitalizeFirst(state)}),
      STATE_PROOFS[state] && info(`« ${state} » : ${STATE_PROOFS[state]}.`),
    )),
  );
}

/** Ligne d'une notion au niveau 2 : signe d'état et titre seul, détail en infobulle. */
function notionRow(data, id) {
  const notion = data.notions?.[id];
  const label = notion?.label || id;
  const state = notionState(notion);
  const group = stateGroup(data, state);
  return el(
    'li',
    {
      className: 'notion',
      attrs: {
        'data-group': group,
        'data-tip': frenchSpacing(`${label.replace(/`/g, '')}.\nÉtat : ${state}.`),
      },
    },
    stateGlyph(group, stateLevel(data, state)),
    el('span', {className: 'notion-title', text: shortLabel(label)}),
    el('span', {className: 'visually-hidden', text: `, ${state}`}),
  );
}

/** Fenêtre d'un palier au niveau 2 : progression, lien vers le détail, notions. */
function tierWindow(data, card, tier, order) {
  const progress = tierProgress(data, tier);
  const ids = tierNotions(tier);
  const tone = tierTone(data, tier);
  const href = `#/c/${encodeURIComponent(card.id)}/${encodeURIComponent(tier.code)}`;
  const open = el(
    'a',
    {className: 'tier-open', attrs: {href}},
    el('span', {className: 'tier-count', text: progressText(progress)}),
    el('span', {className: 'tier-more'}, el('span', {text: 'Détail'}), icon('chevron')),
    bar(progress.total ? progress.lit / progress.total : 0, tone),
  );
  const body = ids.length
    ? el('ul', {className: 'notions'}, ids.map(id => notionRow(data, id)))
    : el('p', {className: 'empty', text: 'Aucune notion dans ce palier.'});
  return systemWindow(
    {title: tier.label || tier.code, level: 'h3', className: 'tier-window', order, tone},
    ids.length ? open : null,
    body,
  );
}

/** Phrase du prochain rang d'une carte, avec sa condition en infobulle, ou null. */
function nextRankLine(card) {
  const next = card.nextRank;
  if (!next?.rank) return null;
  const done = Number.isFinite(next.progress?.value) ? next.progress.value : 0;
  return el(
    'p',
    {className: 'section-next'},
    el('span', {text: `Prochain rang : ${next.rank}, ${done} / ${next.total} notions`}),
    next.condition && info(`Condition : ${next.condition}.`),
  );
}

/**
 * Affiche le niveau 2 : le domaine card et ses paliers.
 *
 * @param {HTMLElement} root conteneur de la vue
 * @param {Object} data objet window.SYSTEME
 * @param {Object} card carte de data.cards
 * @param {{x: number, y: number}|null} origin centre à l'écran du secteur d'où la vue
 *   s'ouvre, null pour une ouverture sans roue
 * @param {string} [certId] certification dont la carte s'ouvre au premier plan ; un
 *   domaine déjà affiché ne met à jour que cette carte
 */
function renderSection(root, data, card, origin, certId) {
  const context = sectionCertContext(data, card);
  if (root.querySelector('.section-view')?.dataset.card === card.id) {
    syncCertDialog(root, data, context, certId);
    return;
  }
  const rank = isMissing(card.rank) ? null : String(card.rank.value);
  const tiers = cardTiers(card);
  const badge = rankBadge(rank);
  if (cardReaches(data, card, RED_TONE)) crownBadge(badge);
  const head = el(
    'header',
    {className: 'section-head'},
    badge,
    el(
      'div',
      {className: 'section-titles'},
      el('h2', {className: 'section-name', text: card.name || card.id}),
      el(
        'p',
        {className: 'section-rank'},
        el('span', {text: rank ? `Rang ${rank}` : 'Aucun rang'}),
        statusTag(card.rank, rankStatus(card.rank)),
      ),
    ),
    nextRankLine(card),
  );
  const body = tiers.length
    ? el('div', {className: 'tiers'}, tiers.map((tier, index) => (
      tierWindow(data, card, tier, index)
    )))
    : el('p', {className: 'empty', text: 'Aucun palier disponible pour ce domaine.'});
  const view = el(
    'div',
    {className: `section-view${origin ? ' from-sector' : ''}`},
    backLink('#/', 'Retour à la roue'),
    head,
    tiers.length ? stateLegend(data) : null,
    body,
    certificationSection(data, card),
    certDialog(),
  );
  view.dataset.card = card.id;
  root.replaceChildren(view);
  syncCertDialog(root, data, context, certId);
  if (origin) {
    const box = view.getBoundingClientRect();
    view.style.setProperty('--ox', `${Math.round(origin.x - box.left)}px`);
    view.style.setProperty('--oy', `${Math.round(origin.y - box.top)}px`);
  }
}

/** Cellule d'état du niveau 3 : signe, état en toutes lettres et sa preuve en infobulle. */
function stateCell(data, notion) {
  const state = notionState(notion);
  const proof = STATE_PROOFS[state];
  return el(
    'td',
    {},
    el(
      'span',
      {className: 'state', attrs: proof ? tipAttrs(`« ${state} » : ${proof}.`) : {}},
      glyphOf(data, state),
      el('span', {text: state}),
    ),
  );
}

/** Ligne du tableau du niveau 3 pour la notion id. */
function notionDetailRow(data, id) {
  const notion = data.notions?.[id];
  const state = notionState(notion);
  return el(
    'tr',
    {
      attrs: {
        'data-group': stateGroup(data, state),
        'data-tone': stateLevel(data, state) || null,
      },
    },
    el('th', {attrs: {scope: 'row'}}, richText(notion?.label || id)),
    stateCell(data, notion),
    el('td', {text: objectiveText(notion)}),
    el('td', {text: notion?.lastPractice || 'jamais'}),
  );
}

/**
 * Affiche le niveau 3 : le détail des notions du palier tier de la carte card.
 *
 * @param {HTMLElement} root conteneur de la vue
 * @param {Object} data objet window.SYSTEME
 * @param {Object} card carte de data.cards
 * @param {Object} tier palier de la carte
 */
function renderTier(root, data, card, tier) {
  const progress = tierProgress(data, tier);
  const ids = tierNotions(tier);
  const tone = tierTone(data, tier);
  const name = card.name || card.id;
  const column = (label, tip) => el('th', {attrs: {scope: 'col'}}, label, tip && info(tip));
  const table = el(
    'table',
    {className: 'notion-table'},
    el('thead', {}, el(
      'tr',
      {},
      column('Notion'),
      column('État'),
      column('Objectif', OBJECTIVE_TIP),
      column('Dernière pratique', PRACTICE_TIP),
    )),
    el('tbody', {}, ids.map(id => notionDetailRow(data, id))),
  );
  root.replaceChildren(el(
    'div',
    {className: 'tier-view'},
    backLink(`#/c/${encodeURIComponent(card.id)}`, `Retour à ${name}`),
    el(
      'header',
      {className: 'tier-head'},
      el('h2', {
        className: 'section-name',
        text: `${name}, palier ${tier.label || tier.code}`,
      }),
      el('p', {className: 'tier-count', text: progressText(progress)}),
      bar(progress.total ? progress.lit / progress.total : 0, tone),
    ),
    systemWindow(
      {title: 'Notions du palier', level: 'h3', className: 'table-window', tone},
      ids.length
        ? table
        : el('p', {className: 'empty', text: 'Aucune notion dans ce palier.'}),
    ),
  ));
}
