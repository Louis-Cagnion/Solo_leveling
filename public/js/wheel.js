'use strict';

/*
 * Maquette « Système » : niveau 1, la roue des domaines.
 *
 * Chaque carte est un secteur cliquable : son titre à l'intérieur, son rang à
 * l'extérieur, et sur le bord quatre arcs, un par palier, remplis selon ses notions
 * allumées. Au centre, les deux niveaux ouvrent la fenêtre de statut. Le survol ou le
 * focus d'un secteur ouvre son résumé à côté de la roue quand la place existe. Une liste
 * des mêmes liens remplace la roue sur un écran trop petit (wheel.css).
 */

const WHEEL = {
  box: 500,
  sectorInner: 186,
  sectorOuter: 396,
  tierRadius: 408,
  rankRadius: 456,
  nameRadius: 291,
  sectorGap: 1.4,
  tierGap: 1,
  gauges: [168, 176],
  lineHeight: 27,
  sideRoom: 300,
};
const HEXAGON = [-90, -30, 30, 90, 150, 210]
  .map(angle => polar(25, angle).join(','))
  .join(' ');

/** Phrase du rang d'une carte : « rang E, observé » ou « aucun rang ». */
function rankPhrase(card) {
  const status = STATUS_LABELS[rankStatus(card.rank)];
  if (isMissing(card.rank)) return status === 'observé' ? 'aucun rang' : `rang ${status}`;
  return `rang ${card.rank.value}, ${status}`;
}

/** Arcs des paliers d'un secteur entre start et end : une piste et son remplissage chacun. */
function tierArcs(data, card, start, end) {
  const tiers = cardTiers(card);
  const span = (end - start - WHEEL.tierGap * (tiers.length - 1)) / (tiers.length || 1);
  return tiers.flatMap((tier, index) => {
    const from = start + index * (span + WHEEL.tierGap);
    const progress = tierProgress(data, tier);
    const lit = progress.total ? (progress.lit / progress.total) * span : 0;
    const arc = to => ringPath(WHEEL.tierRadius, WHEEL.tierRadius, from, to);
    return [
      svgEl('path', {class: 'tier-track', d: arc(from + span)}),
      lit > 0 && svgEl('path', {class: 'tier-fill', d: arc(from + lit)}),
    ];
  });
}

/** Titre d'une carte, écrit le long du rayon d'angle middle, retourné à gauche. */
function sectorName(card, middle) {
  const lines = splitName(card.name || card.id);
  const flipped = Math.cos((middle * Math.PI) / 180) < 0;
  const first = -((lines.length - 1) * WHEEL.lineHeight) / 2;
  const turn = `rotate(${middle}) translate(${WHEEL.nameRadius} 0)`
    + (flipped ? ' rotate(180)' : '');
  return svgEl(
    'text',
    {class: 'sector-name', transform: turn},
    lines.map((line, index) => {
      const tspan = svgEl('tspan', {x: 0, y: first + index * WHEEL.lineHeight});
      tspan.textContent = line;
      return tspan;
    }),
  );
}

/** Insigne de rang d'une carte, posé à l'extérieur de la roue à l'angle middle. */
function sectorRank(card, middle) {
  const [x, y] = polar(WHEEL.rankRadius, middle);
  const rank = isMissing(card.rank) ? null : String(card.rank.value);
  const letter = svgEl('text', {class: 'rank-letter'});
  letter.textContent = rank ? rank.charAt(0) : '–';
  return svgEl(
    'g',
    {class: 'sector-rank', transform: `translate(${x} ${y})`, 'data-rank': rank || 'none'},
    svgEl('polygon', {points: HEXAGON}),
    letter,
  );
}

/**
 * Secteur cliquable d'une carte.
 *
 * @param {Object} data objet window.SYSTEME
 * @param {Object} card carte de data.cards
 * @param {number} index rang de la carte dans la roue
 * @param {number} count nombre de cartes
 * @returns {SVGAElement} lien vers la section de la carte
 */
function buildSector(data, card, index, count) {
  const span = 360 / count;
  const start = -90 + index * span + WHEEL.sectorGap / 2;
  const end = start + span - WHEEL.sectorGap;
  const middle = (start + end) / 2;
  const link = svgEl(
    'a',
    {
      class: 'sector',
      href: `#/c/${encodeURIComponent(card.id)}`,
      'aria-label': `${card.name}, ${rankPhrase(card)}`,
      'data-card': card.id,
      'data-ranked': isMissing(card.rank) ? 'no' : 'yes',
      'data-rank': isMissing(card.rank) ? null : String(card.rank.value),
      'data-start': start,
      'data-end': end,
      'data-crowned': cardReaches(data, card, RED_TONE) ? 'yes' : null,
    },
    svgEl('path', {
      class: 'sector-shape',
      d: ringPath(WHEEL.sectorInner, WHEEL.sectorOuter, start, end),
    }),
    tierArcs(data, card, start, end),
    sectorName(card, middle),
    sectorRank(card, middle),
  );
  link.style.setProperty('--i', String(index));
  return link;
}

/** Jauges circulaires des deux niveaux vers la cible, autour du centre. */
function levelGauges(data) {
  const levels = data.levels || {};
  const values = [levels.level42, levels.systemLevel];
  return values.flatMap((level, index) => {
    const radius = WHEEL.gauges[index];
    const ratio = isMissing(level) ? 0 : levelRatio(level.value, levels.levelTarget);
    const sweep = Math.min(ratio * 360, 359.9);
    return [
      svgEl('circle', {class: 'gauge-track', r: radius}),
      sweep > 0 && svgEl('path', {
        class: `gauge-fill gauge-${index ? 'system' : 'official'}`,
        d: ringPath(radius, radius, -90, -90 + sweep),
      }),
    ];
  });
}

/** Ligne d'un niveau du centre : libellé, valeur et statut en toutes lettres. */
function hubLevel(label, level, className) {
  const status = levelStatus(level);
  const value = isMissing(level) ? STATUS_LABELS[status] : formatNumber(level.value, 2);
  return el(
    'span',
    {className},
    el('span', {className: 'hub-label', text: label}),
    el('span', {className: 'hub-value', text: value}),
    !isMissing(level) && el('span', {
      className: 'tag',
      text: STATUS_LABELS[status],
      attrs: {'data-status': status},
    }),
  );
}

/** Centre de la roue : les deux niveaux, lien vers la fenêtre de statut. */
function buildHub(data) {
  const levels = data.levels || {};
  return el(
    'a',
    {className: 'hub', attrs: {href: '#/status'}},
    hubLevel('Niveau 42', levels.level42, 'hub-official'),
    hubLevel('Système', levels.systemLevel, 'hub-system'),
    el(
      'span',
      {className: 'hub-action'},
      el('span', {text: 'Ouvrir le statut'}),
      icon('chevron'),
    ),
  );
}

/** Ligne du résumé pour un palier : nom, « n / N » et jauge. */
function readoutTier(data, tier) {
  const progress = tierProgress(data, tier);
  return el(
    'li',
    {className: 'readout-tier'},
    el('span', {text: tier.label || tier.code}),
    el('span', {className: 'readout-count', text: `${progress.lit} / ${progress.total}`}),
    bar(progress.total ? progress.lit / progress.total : 0, tierTone(data, tier)),
  );
}

/** Résumé d'une carte, affiché à côté de la roue au survol ou au focus de son secteur. */
function buildReadout(data, card) {
  const next = card.nextRank;
  const rank = isMissing(card.rank) ? null : String(card.rank.value);
  const frame = systemWindow(
    {
      title: card.name || card.id,
      level: 'p',
      className: 'readout-window',
      tone: rankTone(rank),
    },
    el(
      'p',
      {className: 'readout-rank'},
      rankBadge(rank),
      el('span', {text: capitalizeFirst(rankPhrase(card))}),
    ),
    el(
      'ul',
      {className: 'readout-tiers'},
      cardTiers(card).map(tier => readoutTier(data, tier)),
    ),
    next?.rank && el('p', {
      className: 'readout-next',
      text: `Prochain rang : ${next.rank}, ${next.progress?.value ?? 0} / ${next.total} `
        + 'notions du palier',
    }),
  );
  chargeWindow(frame, rank);
  return frame;
}

/** Liste des domaines, variante de la roue pour un écran trop petit. */
function buildDomainList(cards) {
  return el('ul', {className: 'domain-list'}, cards.map(card => el(
    'li',
    {},
    el(
      'a',
      {className: 'domain-row', attrs: {href: `#/c/${encodeURIComponent(card.id)}`}},
      rankBadge(isMissing(card.rank) ? null : String(card.rank.value)),
      el('span', {className: 'domain-name', text: card.name || card.id}),
      el('span', {className: 'domain-rank', text: rankPhrase(card)}),
    ),
  )));
}

/** Texte de l'infobulle de la légende : l'échelle des rangs et leurs conditions. */
function ladderTip() {
  return RANK_LADDER.map(step => `${step.rank} : ${step.condition}.`).join('\n');
}

/**
 * Affiche la roue des domaines dans root.
 *
 * @param {HTMLElement} root conteneur de la vue
 * @param {Object} data objet window.SYSTEME
 * @param {{intro: boolean, onOrigin: function({x: number, y: number})}} options intro :
 *   joue l'allumage des secteurs ; onOrigin reçoit le centre à l'écran du secteur activé
 */
function renderWheel(root, data, options) {
  const cards = dataCards(data);
  const heading = el('h2', {className: 'visually-hidden', text: 'Roue des domaines'});
  if (!cards.length) {
    root.replaceChildren(heading, el('p', {
      className: 'empty wheel-empty',
      text: 'Aucun domaine disponible : le suivi ne contient aucune carte.',
    }));
    return;
  }
  const box = WHEEL.box;
  const svg = svgEl(
    'svg',
    {class: 'wheel-svg', viewBox: `${-box} ${-box} ${2 * box} ${2 * box}`},
    svgEl('g', {'aria-hidden': 'true'}, levelGauges(data)),
    cards.map((card, index) => buildSector(data, card, index, cards.length)),
  );
  const readout = el('aside', {className: 'readout', attrs: {'aria-hidden': 'true'}});
  const wheel = el('div', {className: 'wheel'}, svg, buildHub(data), readout);
  const stage = el(
    'div',
    {className: `wheel-stage${options.intro ? ' is-intro' : ''}`},
    wheel,
    buildDomainList(cards),
  );
  const legend = el(
    'p',
    {className: 'wheel-legend'},
    'Rangs observés, sauf mention. Bord de chaque domaine : ses quatre paliers.',
    info(ladderTip()),
  );

  const showReadout = event => {
    const sector = event.target.closest('.sector');
    const card = sector && cards.find(entry => entry.id === sector.dataset.card);
    if (!card || readout.dataset.card === card.id) return;
    readout.dataset.card = card.id;
    readout.replaceChildren(buildReadout(data, card));
  };
  const clearReadout = () => {
    delete readout.dataset.card;
    readout.replaceChildren();
  };
  svg.addEventListener('pointerover', showReadout);
  svg.addEventListener('focusin', showReadout);
  svg.addEventListener('pointerleave', clearReadout);
  svg.addEventListener('focusout', event => {
    if (!svg.contains(event.relatedTarget)) clearReadout();
  });
  svg.addEventListener('click', event => {
    const shape = event.target.closest('.sector')?.querySelector('.sector-shape');
    if (!shape) return;
    const rect = shape.getBoundingClientRect();
    options.onOrigin({x: rect.left + rect.width / 2, y: rect.top + rect.height / 2});
  });
  new ResizeObserver(() => {
    const room = (stage.clientWidth - wheel.clientWidth) / 2;
    stage.classList.toggle('has-side', room >= WHEEL.sideRoom);
  }).observe(stage);

  animateWheel(svg);
  root.replaceChildren(heading, stage, legend);
}
