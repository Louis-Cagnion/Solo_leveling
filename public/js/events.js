'use strict';

/*
 * Maquette « Système » : événements débloqués entre deux visites, calculs purs sans DOM.
 *
 * snapshotOf réduit window.SYSTEME à l'état mesurable d'une visite (niveaux, rangs,
 * paliers, états atteints, certifications, titres) ; detectEvents compare deux états et
 * liste ce qui a progressé. Une valeur qui baisse ou disparaît n'est jamais annoncée.
 * Chaque événement porte sa famille, son texte, un ton de rareté et l'adresse où le
 * voir. Chargé après model.js ; exporté pour Node par module.exports.
 */

const SNAPSHOT_VERSION = 1;
/* Familles d'événements, dans l'ordre d'annonce. */
const EVENT_FAMILIES = {
  levels: 'Niveaux',
  ranks: 'Rangs',
  tiers: 'Paliers',
  notions: 'Notions',
  certifications: 'Certifications',
  titles: 'Titres',
};
const NOTION_CAPS = [10, 50, 100];
const S_DOMAIN_CAPS = [3, 10];
const NATION_SHARES = [0.5, 1];
const ANSWER_SHARES = [0.25, 0.5, 0.75];
const SHARE_WORDS = {0.25: 'un quart', 0.5: 'la moitié', 0.75: 'les trois quarts'};
const OBTAINED_STATES = ['obtained', 'crowned'];
const STATUS_HREF = '#/status';

/** Place du rang rank dans RANK_LADDER, -1 pour un rang absent ou inconnu. */
function rankIndex(rank) {
  return RANK_LADDER.findIndex(step => step.rank === rank);
}

/** Plus haut palier de steps franchi en passant de before à after, ou null. */
function crossed(before, after, steps) {
  return steps.filter(step => before < step && after >= step).pop() ?? null;
}

/** Adresse de la vue du domaine id. */
function cardHref(id) {
  return `#/c/${encodeURIComponent(id)}`;
}

/** Événement : family clé d'EVENT_FAMILIES, tone ton de rareté (0 : aucun) ou « gold ». */
function unlockEvent(family, text, tone, href) {
  return {family, text, tone: tone || 0, href};
}

/** État d'une carte dans snapshotOf : rang, notions commencées, paliers, certifications. */
function cardSnapshot(data, card, order) {
  const stateIndex = id => order.indexOf(data.notions?.[id]?.state);
  const tiers = cardTiers(card).filter(tier => tier?.code);
  return {
    name: card.name || card.id,
    rank: isMissing(card.rank) ? null : String(card.rank.value),
    crowned: cardReaches(data, card, RED_TONE),
    started: tiers.flatMap(tierNotions).filter(id => stateIndex(id) >= 0).length,
    tiers: Object.fromEntries(tiers.map(tier => {
      const ids = tierNotions(tier);
      return [tier.code, {
        label: tier.label || tier.code,
        ...tierProgress(data, tier),
        floor: ids.length ? Math.min(...ids.map(stateIndex)) : -1,
      }];
    })),
    certs: (Array.isArray(card.certifications) ? card.certifications : []).map(cert => ({
      name: cert?.label || 'certification sans nom',
      state: certState(data, card, cert),
    })),
  };
}

/**
 * État mesurable d'une visite, sérialisable en JSON.
 *
 * @param {Object} data objet window.SYSTEME
 * @returns {Object} reached : nombre de notions au moins à chaque état de order ; crowned
 *   d'une carte : toutes ses notions au moins rouges (cardReaches) ; floor
 *   d'un palier : place dans order de son état le plus bas, -1 s'il est vide ou si une
 *   notion est hors de order
 */
function snapshotOf(data) {
  const order = Array.isArray(data.proofOrder) ? data.proofOrder : [];
  const levels = data.levels || {};
  const cards = dataCards(data).filter(card => card?.id);
  const notions = Object.values(data.notions || {});
  const measured = value => (
    isMeasured(value) && Number.isFinite(value.value) ? value.value : null
  );
  const titles = (Array.isArray(data.titles) ? data.titles : []).filter(title => title?.id);
  const achievements = Array.isArray(data.achievements) ? data.achievements : [];
  return {
    version: SNAPSHOT_VERSION,
    order,
    levelTarget: Number.isFinite(levels.levelTarget) ? levels.levelTarget : null,
    level42: measured(levels.level42),
    levelSystem: measured(levels.systemLevel),
    rank42: xpRank(levels),
    rankSystem: averageRank(cards),
    reached: order.map((state, index) => (
      notions.filter(notion => order.indexOf(notion?.state) >= index).length
    )),
    cards: Object.fromEntries(cards.map(card => [card.id, cardSnapshot(data, card, order)])),
    titles: Object.fromEntries(titles.map(title => [title.id, {
      name: `${title.name} (${title.scope})`,
      ratio: titleProgress(title)?.ratio ?? null,
      obtained: title.obtained?.value === true,
    }])),
    achievements: Object.fromEntries(achievements.filter(item => item?.name).map(item => [
      item.name,
      {obtained: Boolean(item.obtained), title: item.title || null},
    ])),
  };
}

/** true si value a la forme d'un résultat de snapshotOf de la version courante. */
function isSnapshot(value) {
  const isMap = part => Boolean(part) && typeof part === 'object' && !Array.isArray(part);
  return isMap(value)
    && value.version === SNAPSHOT_VERSION
    && Array.isArray(value.order)
    && Array.isArray(value.reached)
    && [value.cards, value.titles, value.achievements].every(isMap);
}

/** Niveaux : passage de niveau, niveau cible atteint ou dépassé, nouveau rang du bloc. */
function levelEvents(before, after) {
  const gauges = [
    ['Niveau 42', 'level42', 'rank42'],
    ['Niveau Système', 'levelSystem', 'rankSystem'],
  ];
  return gauges.flatMap(([name, level, rank]) => {
    const was = before[level];
    const now = after[level];
    const tone = rankTone(after[rank]);
    const target = after.levelTarget;
    const moved = Number.isFinite(was) && Number.isFinite(now);
    const reached = moved && Number.isFinite(target) && was < target && now >= target;
    return [
      moved && Math.floor(now) > Math.floor(was)
        && unlockEvent('levels', `${name} : niveau ${Math.floor(now)} atteint`, tone),
      reached && unlockEvent(
        'levels',
        `${name} : niveau cible ${target} ${now > target ? 'dépassé' : 'atteint'}`,
        tone,
      ),
      rankIndex(after[rank]) > rankIndex(before[rank])
        && unlockEvent('levels', `${name} : rang ${after[rank]}`, tone),
    ].filter(Boolean).map(event => ({...event, href: STATUS_HREF}));
  });
}

/** Nombre de cartes de snapshot au moins au rang rank. */
function countAtRank(snapshot, rank) {
  const floor = rankIndex(rank);
  return Object.values(snapshot.cards).filter(card => rankIndex(card?.rank) >= floor).length;
}

/** Rangs : nouveau rang d'un domaine, puis les caps de l'ensemble des domaines. */
function rankEvents(before, after) {
  const events = Object.entries(after.cards)
    .filter(([id, card]) => rankIndex(card.rank) > rankIndex(before.cards[id]?.rank))
    .map(([id, card]) => unlockEvent(
      'ranks',
      `${card.name} : rang ${card.rank}`,
      rankTone(card.rank),
      cardHref(id),
    ));
  const size = snapshot => Object.keys(snapshot.cards).length;
  const share = snapshot => countAtRank(snapshot, 'Nation') / (size(snapshot) || 1);
  const allAt = (snapshot, rank) => (
    size(snapshot) > 0 && countAtRank(snapshot, rank) === size(snapshot)
  );
  const all = RANK_LADDER.map(step => step.rank).slice(1, -1)
    .filter(rank => allAt(after, rank) && !allAt(before, rank))
    .pop();
  const wide = (text, rank) => unlockEvent('ranks', text, rankTone(rank), '#/');
  for (const rank of ['S', 'Nation']) {
    if (!countAtRank(before, rank) && countAtRank(after, rank)) {
      events.push(wide(`Premier domaine au rang ${rank}`, rank));
    }
  }
  const cap = crossed(countAtRank(before, 'S'), countAtRank(after, 'S'), S_DOMAIN_CAPS);
  if (cap) events.push(wide(`${cap} domaines au rang S ou plus`, 'S'));
  if (all) events.push(wide(`Tous les domaines au rang ${all} ou plus`, all));
  const nation = crossed(share(before), share(after), NATION_SHARES);
  if (nation) {
    const words = nation === 1 ? 'Tous les domaines' : 'La moitié des domaines';
    events.push(wide(`${words} au rang Nation`, 'Nation'));
  }
  return events;
}

/**
 * Paliers : palier complet, nouvelle couleur, niveau maximum, domaine au maximum. Un
 * palier qui change de couleur en se complétant n'annonce que sa couleur.
 */
function tierEvents(before, after) {
  const top = after.order.length - 1;
  const maxed = card => {
    const tiers = Object.values(card?.tiers || {});
    return top >= 1 && tiers.length > 0 && tiers.every(tier => tier.floor === top);
  };
  return Object.entries(after.cards).flatMap(([id, card]) => {
    const past = before.cards[id];
    const events = Object.entries(card.tiers).flatMap(([code, tier]) => {
      const was = past?.tiers?.[code];
      const name = `${card.name}, palier ${tier.label}`;
      const tone = stateLevel({proofOrder: after.order}, after.order[tier.floor]);
      const full = entry => Boolean(entry) && entry.total > 0 && entry.lit === entry.total;
      const raised = tier.floor >= 1 && tier.floor > (was?.floor ?? -1);
      const state = after.order[tier.floor];
      return [
        full(tier) && !full(was) && !raised
          && unlockEvent('tiers', `${name} : complet`, tone),
        raised && tier.floor < top && unlockEvent(
          'tiers',
          `${name} : nouvelle couleur, toutes ses notions au moins « ${state} »`,
          tone,
        ),
        raised && tier.floor === top && unlockEvent(
          'tiers',
          `${name} : niveau maximum, toutes ses notions « ${state} »`,
          tone,
        ),
      ];
    });
    events.push(maxed(card) && !maxed(past) && unlockEvent(
      'tiers',
      `${card.name} : tous ses paliers au niveau maximum`,
      RARITY_LEVELS,
    ));
    return events.filter(Boolean).map(event => ({...event, href: cardHref(id)}));
  });
}

/**
 * Notions : première notion d'un domaine, domaine couronné (toutes ses notions au moins
 * rouges), roue entière couronnée, premier accès à un état, caps par état.
 */
function notionEvents(before, after) {
  const proof = {proofOrder: after.order};
  const red = after.order.find(state => stateLevel(proof, state) === RED_TONE);
  const whole = snapshot => {
    const cards = Object.values(snapshot.cards);
    return cards.length > 0 && cards.every(card => card?.crowned);
  };
  const events = Object.entries(after.cards).flatMap(([id, card]) => [
    card.started > 0 && !(before.cards[id]?.started > 0)
      && unlockEvent('notions', `${card.name} : première notion commencée`, 0, cardHref(id)),
    card.crowned && !before.cards[id]?.crowned && unlockEvent(
      'notions',
      `${card.name} : domaine couronné, toutes ses notions au moins « ${red} »`,
      RED_TONE,
      cardHref(id),
    ),
  ]).filter(Boolean);
  if (whole(after) && !whole(before)) {
    const text = 'Roue couronnée : tous les domaines le sont';
    events.push(unlockEvent('notions', text, RED_TONE, '#/'));
  }
  if (after.order.join('|') !== before.order.join('|')) return events;
  after.order.forEach((state, index) => {
    const was = before.reached[index] || 0;
    const now = after.reached[index] || 0;
    const tone = stateLevel({proofOrder: after.order}, state);
    const cap = crossed(was, now, NOTION_CAPS);
    if (!was && now) {
      events.push(unlockEvent('notions', `Première notion « ${state} »`, tone, '#/'));
    }
    if (cap) {
      events.push(unlockEvent('notions', `${cap} notions au moins « ${state} »`, tone, '#/'));
    }
  });
  return events;
}

/** Certifications : accessible, obtenue, passée au violet, domaine complet, première. */
function certificationEvents(before, after) {
  const obtained = cert => OBTAINED_STATES.includes(cert?.state);
  const count = snapshot => Object.values(snapshot.cards)
    .flatMap(card => card?.certs || [])
    .filter(obtained).length;
  const complete = card => card?.certs?.length > 0 && card.certs.every(obtained);
  const events = Object.entries(after.cards).flatMap(([id, card]) => {
    const past = before.cards[id];
    const rows = card.certs.flatMap((cert, index) => {
      const was = past?.certs?.[index];
      const tone = CERT_STATES[cert.state]?.tone;
      const name = `Certification ${cert.name}`;
      return [
        cert.state === 'accessible' && was?.state !== 'accessible' && !obtained(was)
          && unlockEvent('certifications', `${name} : accessible`, tone),
        obtained(cert) && !obtained(was)
          && unlockEvent('certifications', `${name} : obtenue`, tone),
        cert.state === 'crowned' && was?.state === 'obtained'
          && unlockEvent('certifications', `${name} : passée du rouge au violet`, tone),
      ];
    });
    rows.push(complete(card) && !complete(past) && unlockEvent(
      'certifications',
      `${card.name} : toutes ses certifications obtenues`,
      CERT_STATES.crowned.tone,
    ));
    return rows.filter(Boolean).map(event => ({...event, href: cardHref(id)}));
  });
  if (!count(before) && count(after)) {
    events.push(unlockEvent(
      'certifications',
      'Première certification obtenue',
      CERT_STATES.obtained.tone,
      STATUS_HREF,
    ));
  }
  return events;
}

/**
 * Titres : avancement d'un titre chiffré, titre obtenu, achievement de 42 obtenu et titre
 * qu'il donne. Une liste d'achievements lue pour la première fois n'annonce rien.
 */
function titleEvents(before, after) {
  const events = Object.entries(after.titles).flatMap(([id, title]) => {
    const was = before.titles[id];
    const share = crossed(was?.ratio ?? 0, title.ratio ?? 0, ANSWER_SHARES);
    if (title.obtained) return was?.obtained ? [] : [`Titre obtenu : ${title.name}`];
    return share ? [`${title.name} : ${SHARE_WORDS[share]} du chemin parcouru`] : [];
  });
  const known = Object.keys(before.achievements).length > 0;
  for (const [name, item] of Object.entries(after.achievements)) {
    if (!known || !item.obtained || before.achievements[name]?.obtained) continue;
    const given = item.title ? `, titre « ${item.title} »` : '';
    events.push(`Achievement de 42 obtenu : ${name}${given}`);
  }
  return events.map(text => unlockEvent('titles', text, 'gold', STATUS_HREF));
}

/**
 * Événements débloqués entre deux visites, dans l'ordre d'EVENT_FAMILIES.
 *
 * @param {Object} before résultat de snapshotOf à la visite précédente
 * @param {Object} after résultat de snapshotOf à la visite courante
 * @returns {{family: string, text: string, tone: number|string, href: string}[]} vide si
 *   before n'est pas un état de la version courante
 */
function detectEvents(before, after) {
  if (!isSnapshot(before) || !isSnapshot(after)) return [];
  return [levelEvents, rankEvents, tierEvents, notionEvents, certificationEvents, titleEvents]
    .flatMap(detect => detect(before, after));
}

if (typeof module !== 'undefined') {
  module.exports = {SNAPSHOT_VERSION, EVENT_FAMILIES, snapshotOf, isSnapshot, detectEvents};
}
