'use strict';

/*
 * Maquette « Système » : calculs purs sur l'objet window.SYSTEME, sans DOM.
 *
 * Valeur statuée : {value, status, reason}, status parmi observed, estimated,
 * insufficient (des conditions existent et ne sont pas remplies) et unmeasurable (aucune
 * mesure pour comparer). Une notion est allumée si son état atteint, dans data.proofOrder,
 * le seuil data.rankDThreshold : « déclarée » et « non rencontrée » n'y figurent pas et
 * restent éteintes. Porte aussi les rendus et les tons d'état, l'échelle des rangs, les
 * rangs des cartes de niveau, l'état des certifications et la géométrie de la roue.
 * Exporté pour Node par module.exports ; dans la page, fonctions globales du script
 * classique.
 */

const STATUSES = ['observed', 'estimated', 'insufficient', 'unmeasurable'];
const SOURCE_STATES = {ok: 'lue', unavailable: 'indisponible'};
const NO_REASON = 'raison non fournie';

/** true si la valeur statuée value n'a pas de valeur (null ou absente). */
function isMissing(value) {
  return value?.value === null || value?.value === undefined;
}

/**
 * Statut de la valeur statuée value. Un statut inconnu, ou « insufficient » sans valeur,
 * vaut « unmeasurable » : rien n'a été mesuré, aucune condition n'a donc échoué.
 */
function statusOf(value) {
  const status = STATUSES.includes(value?.status) ? value.status : 'unmeasurable';
  return status === 'insufficient' && isMissing(value) ? 'unmeasurable' : status;
}

/** true si la valeur statuée value repose sur une mesure (observée ou estimée). */
function isMeasured(value) {
  return ['observed', 'estimated'].includes(statusOf(value));
}

/** Statut d'un niveau : une valeur absente est toujours non mesurable. */
function levelStatus(level) {
  return isMissing(level) ? 'unmeasurable' : statusOf(level);
}

/** Statut d'un rang : absent et observé vaut « aucun rang », absent sinon non mesurable. */
function rankStatus(rank) {
  const status = statusOf(rank);
  return isMissing(rank) && status !== 'observed' ? 'unmeasurable' : status;
}

/** true si le seuil d'allumage figure dans l'ordre de preuve de data. */
function hasThreshold(data) {
  return Array.isArray(data.proofOrder) && data.proofOrder.includes(data.rankDThreshold);
}

/**
 * Indique si une notion est allumée : son état est au moins au seuil du rang D.
 *
 * @param {Object} data objet window.SYSTEME (proofOrder, rankDThreshold, notions)
 * @param {string} id identifiant de notion
 * @returns {boolean} false aussi si le seuil ou la notion manque
 */
function isLit(data, id) {
  if (!hasThreshold(data)) return false;
  const order = data.proofOrder;
  return order.indexOf(data.notions?.[id]?.state) >= order.indexOf(data.rankDThreshold);
}

/** État exigé des notions d'une certification : data.certThreshold, sinon celui du rang D. */
function certThreshold(data) {
  return data.certThreshold || data.rankDThreshold;
}

/**
 * Compte, parmi les notions ids, celles dont l'état atteint threshold dans
 * data.proofOrder.
 *
 * @param {Object} data objet window.SYSTEME (proofOrder, notions)
 * @param {string[]} ids identifiants de notion
 * @param {string} threshold libellé d'état ; hors de l'ordre de preuve, aucune ne compte
 * @returns {{lit: number, total: number}}
 */
function thresholdProgress(data, ids, threshold) {
  const order = Array.isArray(data.proofOrder) ? data.proofOrder : [];
  const floor = order.indexOf(threshold);
  const reached = id => floor >= 0 && order.indexOf(data.notions?.[id]?.state) >= floor;
  return {lit: ids.filter(reached).length, total: ids.length};
}

/** Cartes de domaine de data, ou tableau vide si elles manquent. */
function dataCards(data) {
  return Array.isArray(data.cards) ? data.cards : [];
}

/** Paliers d'une carte, ou tableau vide s'ils manquent. */
function cardTiers(card) {
  return Array.isArray(card?.tiers) ? card.tiers : [];
}

/** Identifiants des notions d'un palier, ou tableau vide s'ils manquent. */
function tierNotions(tier) {
  return Array.isArray(tier?.notions) ? tier.notions : [];
}

/**
 * Progression d'un palier : notions allumées sur notions du palier.
 *
 * @param {Object} data objet window.SYSTEME
 * @param {{notions: string[]}} tier palier de carte
 * @returns {{lit: number, total: number}}
 */
function tierProgress(data, tier) {
  const ids = tierNotions(tier);
  return {lit: ids.filter(id => isLit(data, id)).length, total: ids.length};
}

/** Texte « n notions / N » d'une progression, au singulier pour 0 ou 1 notion. */
function progressText(progress) {
  const noun = progress.lit > 1 ? 'notions' : 'notion';
  return `${progress.lit} ${noun} / ${progress.total}`;
}

/**
 * Compte des titres : obtenus (obtained.value === true) sur le total, plus le nombre
 * de titres dont l'obtention n'est pas connue (valeur non booléenne).
 *
 * @param {Object[]|undefined} titles data.titles
 * @returns {{obtained: number, total: number, unknown: number}}
 */
function titleCount(titles) {
  const list = Array.isArray(titles) ? titles : [];
  return {
    obtained: list.filter(title => title?.obtained?.value === true).length,
    total: list.length,
    unknown: list.filter(title => typeof title?.obtained?.value !== 'boolean').length,
  };
}

/** Texte de la colonne « Objectif » d'une notion : sa valeur, sinon « non suivie ». */
function objectiveText(notion) {
  return notion?.objective || 'non suivie';
}

/** Titre d'identifiant id dans data.titles, ou undefined s'il manque. */
function findTitle(titles, id) {
  return Array.isArray(titles) ? titles.find(title => title?.id === id) : undefined;
}

/** Raison d'une valeur statuée, sinon « raison non fournie ». */
function reasonText(value) {
  return value?.reason || NO_REASON;
}

/**
 * Raison de l'état d'une source de data.sources : son champ reason, sinon son libellé et
 * son état connu ; « raison non fournie » si la source ou son état manque.
 *
 * @param {Object[]|undefined} sources data.sources ({label, status, reason?})
 * @param {string} label libellé exact de la source
 * @returns {string}
 */
function sourceReason(sources, label) {
  const source = Array.isArray(sources)
    ? sources.find(entry => entry?.label === label)
    : undefined;
  if (source?.reason) return source.reason;
  const state = SOURCE_STATES[source?.status];
  return state ? `source « ${label} » ${state}` : NO_REASON;
}

/**
 * Progression chiffrée d'un titre : progress.value sur target, ratio borné à [0, 1].
 *
 * @param {{progress?: {value?: number}, target?: number}|undefined} title titre
 * @returns {{value: number, target: number, ratio: number}|null} null sans valeur
 *   numérique mesurée ou sans cible positive
 */
function titleProgress(title) {
  const value = title?.progress?.value;
  const target = title?.target;
  if (!Number.isFinite(value) || !isMeasured(title.progress)) return null;
  if (!Number.isFinite(target) || target <= 0) return null;
  return {value, target, ratio: Math.min(1, Math.max(0, value / target))};
}

/** Obtention d'un titre en toutes lettres, ou null si elle n'est pas connue. */
function obtainedWords(obtained) {
  if (typeof obtained?.value !== 'boolean') return null;
  return obtained.value ? 'obtenu' : 'non obtenu';
}

/* Les quatre rendus d'état d'une notion, du plus rare au plus commun. */
const STATE_GROUPS = ['high', 'low', 'declared', 'unmet'];

/* Nombre de couleurs de l'échelle de rareté (jetons --rarity-1 à --rarity-7). */
const RARITY_LEVELS = 7;

/* Ton de rareté de chaque rang : A en or et S en rouge (échange choisi par Louis). */
const RANK_TONES = {E: 1, D: 2, C: 3, B: 4, A: 6, S: 5, Nation: 7};

/* Ton rouge de l'échelle de rareté (jeton --rarity-5). */
const RED_TONE = 5;

/* Tons échangés entre états : « retenue » en or, « transférée » en rouge (même choix). */
const STATE_TONE_SWAP = {5: 6, 6: 5};

/* États d'une certification : libellé affiché et ton de rareté (0 : couleur par défaut). */
const CERT_STATES = {
  unmeasurable: {label: 'accessibilité non mesurable', tone: 0},
  locked: {label: 'non accessible', tone: 0},
  accessible: {label: 'accessible', tone: 2},
  obtained: {label: 'obtenue', tone: 5},
  crowned: {label: 'obtenue', tone: 7},
};

/* Échelle des rangs et condition de chacun (docs/plan.md, décision du point 5 de P1). */
const RANK_LADDER = [
  {rank: 'E', condition: 'une notion de la carte commencée'},
  {rank: 'D', condition: 'palier débutant validé'},
  {rank: 'C', condition: 'palier intermédiaire validé'},
  {rank: 'B', condition: 'moitié du palier avancé validée'},
  {rank: 'A', condition: 'palier avancé validé'},
  {rank: 'S', condition: 'palier transcendée validé'},
  {
    rank: 'Nation',
    condition: 'certifications de la carte obtenues ; S suffit si la carte n’en a aucune',
  },
];

/**
 * Rendu d'un état de notion : « high » au seuil du rang D et au-dessus, « low » en
 * dessous, « declared » pour l'état déclaré, « unmet » sinon (état inconnu compris).
 *
 * @param {Object} data objet window.SYSTEME (states, proofOrder, rankDThreshold)
 * @param {string|null|undefined} state libellé d'état de la notion
 * @returns {string} un code de STATE_GROUPS
 */
function stateGroup(data, state) {
  const order = Array.isArray(data.proofOrder) ? data.proofOrder : [];
  const position = order.indexOf(state);
  if (position >= 0) {
    const threshold = order.indexOf(data.rankDThreshold);
    return threshold >= 0 && position >= threshold ? 'high' : 'low';
  }
  const states = Array.isArray(data.states) ? data.states : [];
  const code = states.find(entry => entry?.label === state)?.code;
  return code === 'declared' ? 'declared' : 'unmet';
}

/**
 * Ton de rareté d'un état, de 1 à RARITY_LEVELS : le dernier état de data.proofOrder
 * vaut le sommet, le précédent un de moins, sans descendre sous 1, puis STATE_TONE_SWAP.
 *
 * @param {Object} data objet window.SYSTEME (proofOrder)
 * @param {string|null|undefined} state libellé d'état de la notion
 * @returns {number} 0 pour un état hors de l'ordre de preuve (déclarée, non rencontrée)
 */
function stateLevel(data, state) {
  const order = Array.isArray(data.proofOrder) ? data.proofOrder : [];
  const position = order.indexOf(state);
  if (position < 0) return 0;
  const level = Math.max(1, RARITY_LEVELS - (order.length - 1 - position));
  return STATE_TONE_SWAP[level] || level;
}

/** Ton de rareté du rang rank, 0 pour un rang absent ou inconnu. */
function rankTone(rank) {
  return RANK_TONES[rank] || 0;
}

/**
 * Ton d'un palier : celui de l'état le plus bas parmi toutes ses notions, à partir du
 * deuxième état de data.proofOrder.
 *
 * @param {Object} data objet window.SYSTEME (proofOrder, notions)
 * @param {{notions: string[]}} tier palier de carte
 * @returns {number} 0 si le palier est vide ou si une notion est sous ce deuxième état
 */
function tierTone(data, tier) {
  const order = Array.isArray(data.proofOrder) ? data.proofOrder : [];
  const ids = tierNotions(tier);
  const lowest = Math.min(...ids.map(id => order.indexOf(data.notions?.[id]?.state)));
  return ids.length && lowest >= 1 ? stateLevel(data, order[lowest]) : 0;
}

/**
 * Indique si toutes les notions des paliers de card sont au moins à l'état de ton tone.
 *
 * @param {Object} data objet window.SYSTEME (proofOrder, notions)
 * @param {Object} card carte de data.cards
 * @param {number} tone ton de rareté d'un état (stateLevel), RED_TONE pour le rouge
 * @returns {boolean} false sans notion ou si aucun état ne porte ce ton
 */
function cardReaches(data, card, tone) {
  const order = Array.isArray(data.proofOrder) ? data.proofOrder : [];
  const floor = order.findIndex(state => stateLevel(data, state) === tone);
  const ids = cardTiers(card).flatMap(tierNotions);
  return floor >= 0
    && ids.length > 0
    && ids.every(id => order.indexOf(data.notions?.[id]?.state) >= floor);
}

/**
 * Rang atteint par un rapport découpé en tranches égales, une par rang de RANK_LADDER.
 *
 * ratioRank(0.2) -> 'D'
 *
 * @param {number} ratio avancement, 1 ou plus pour la cible atteinte
 * @returns {string|null} null si ratio n'est pas un nombre positif ou nul
 */
function ratioRank(ratio) {
  if (!Number.isFinite(ratio) || ratio < 0) return null;
  const slices = RANK_LADDER.length;
  return RANK_LADDER[Math.min(slices - 1, Math.floor(ratio * slices))].rank;
}

/** Rang du niveau 42 : tranche d'XP atteinte, null si l'XP ou sa cible manque. */
function xpRank(levels) {
  const xp = levels.xp42;
  if (!isMeasured(xp) || !(levels.xpTarget > 0)) return null;
  return ratioRank(xp.value / levels.xpTarget);
}

/**
 * Rang moyen des cartes : chaque rang vaut sa place dans RANK_LADDER (E = 1), une carte
 * sans rang vaut 0, et la moyenne s'arrondit au rang le plus proche.
 *
 * @param {Object[]} cards cartes de data.cards
 * @returns {string|null} null sans carte ou si la moyenne arrondie vaut 0
 */
function averageRank(cards) {
  const ranks = RANK_LADDER.map(step => step.rank);
  if (!cards.length) return null;
  const sum = cards.reduce(
    (total, card) => total + ranks.indexOf(String(card?.rank?.value)) + 1,
    0,
  );
  return ranks[Math.round(sum / cards.length) - 1] || null;
}

/** Moyenne des avancements (0 à 1) des titres à progression mesurée, null sans titre. */
function answersRatio(titles) {
  const ratios = (Array.isArray(titles) ? titles : [])
    .map(title => titleProgress(title)?.ratio)
    .filter(Number.isFinite);
  return ratios.length ? ratios.reduce((sum, ratio) => sum + ratio, 0) / ratios.length : null;
}

/**
 * Avancement vers une certification, en notions au moins à certThreshold : sur ses notions
 * si elle les liste, sinon sur celles de son domaine dès qu'une d'elles est suivie.
 *
 * @param {Object} data objet window.SYSTEME
 * @param {Object} card carte de la certification
 * @param {{notions?: string[]}} cert certification de card.certifications
 * @returns {{lit: number, total: number, ratio: number, scope: string}|null} scope :
 *   « certification » ou « domain » ; null si rien ne permet de mesurer
 */
function certProgress(data, card, cert) {
  const own = Array.isArray(cert?.notions) ? cert.notions : [];
  const ids = own.length ? own : cardTiers(card).flatMap(tierNotions);
  const order = Array.isArray(data.proofOrder) ? data.proofOrder : [];
  const tracked = ids.some(id => order.includes(data.notions?.[id]?.state));
  if (!ids.length || (!own.length && !tracked)) return null;
  const {lit} = thresholdProgress(data, ids, certThreshold(data));
  return {
    lit,
    total: ids.length,
    ratio: lit / ids.length,
    scope: own.length ? 'certification' : 'domain',
  };
}

/**
 * État d'une certification, clé de CERT_STATES : « crowned » obtenue dans un domaine au
 * rang S ou Nation, « obtained » obtenue sinon, « accessible » si toutes ses notions
 * atteignent certThreshold, « locked » sinon, « unmeasurable » si elle ne liste aucune notion.
 */
function certState(data, card, cert) {
  if (cert?.obtained?.value === true) {
    return ['S', 'Nation'].includes(card?.rank?.value) ? 'crowned' : 'obtained';
  }
  const ids = Array.isArray(cert?.notions) ? cert.notions : [];
  if (!ids.length) return 'unmeasurable';
  const {lit, total} = thresholdProgress(data, ids, certThreshold(data));
  return lit === total ? 'accessible' : 'locked';
}

/** Date « jj/mm/aaaa » en nombre aaaammjj comparable, 0 si elle manque ou est mal formée. */
function dateKey(date) {
  const parts = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec(date || '');
  return parts ? Number(`${parts[3]}${parts[2]}${parts[1]}`) : 0;
}

/**
 * Certifications de toutes les cartes : obtenues de la plus récente à la plus ancienne,
 * puis avancement décroissant, puis celles sans mesure (progress null) dans l'ordre des
 * cartes.
 *
 * @param {Object} data objet window.SYSTEME
 * @returns {Array<{id: string, card: Object, cert: Object, state: string,
 *   progress: Object|null}>} id : « <carte>.<rang dans la carte> »
 */
function rankedCertifications(data) {
  const entries = dataCards(data).flatMap(card => (
    (Array.isArray(card?.certifications) ? card.certifications : []).map((cert, index) => ({
      id: `${card.id}.${index}`,
      card,
      cert,
      state: certState(data, card, cert),
      progress: certProgress(data, card, cert),
    }))
  ));
  const obtained = entries.filter(entry => entry.cert.obtained?.value === true);
  const open = entries.filter(entry => !obtained.includes(entry));
  const measured = open.filter(entry => entry.progress);
  obtained.sort((a, b) => dateKey(b.cert.obtainedOn) - dateKey(a.cert.obtainedOn));
  measured.sort((a, b) => b.progress.ratio - a.progress.ratio);
  return obtained.concat(measured, open.filter(entry => !entry.progress));
}

/**
 * Titre seul d'une notion : le libellé avant sa première parenthèse, son premier
 * deux-points ou son premier point-virgule, sans accents graves de code.
 *
 * shortLabel('Flux (`std::cout`, `std::cin`)') -> 'Flux'
 *
 * @param {string} label libellé complet de la notion
 * @returns {string} le libellé entier si la coupe laisserait moins de 3 caractères
 */
function shortLabel(label) {
  const text = String(label).replace(/`/g, '');
  const head = text.match(/^(.*?)(?:\s\(|\s?:\s|\s;\s)/);
  return (head && head[1].length >= 3 ? head[1] : text).trim();
}

/** Nom name coupé en deux lignes équilibrées s'il dépasse limit caractères. */
function splitName(name, limit = 16) {
  const words = String(name).split(' ');
  if (name.length <= limit || words.length < 2) return [String(name)];
  let best = 1;
  for (let cut = 1; cut < words.length; cut += 1) {
    const gap = side => Math.abs(
      words.slice(0, side).join(' ').length - words.slice(side).join(' ').length,
    );
    if (gap(cut) < gap(best)) best = cut;
  }
  return [words.slice(0, best).join(' '), words.slice(best).join(' ')];
}

/** Rapport borné à [0, 1] d'un niveau sur sa cible ; 0 sans nombres valides. */
function levelRatio(level, target) {
  if (!Number.isFinite(level) || !Number.isFinite(target) || target <= 0) return 0;
  return Math.min(1, Math.max(0, level / target));
}

/** Point [x, y] à la distance radius du centre, angle en degrés (0 à droite, horaire). */
function polar(radius, degrees) {
  const angle = (degrees * Math.PI) / 180;
  const rounded = value => Math.round(value * 100) / 100;
  return [rounded(radius * Math.cos(angle)), rounded(radius * Math.sin(angle))];
}

/**
 * Tracé SVG d'un secteur d'anneau, ou d'un arc simple si inner égale outer.
 *
 * @param {number} inner rayon intérieur
 * @param {number} outer rayon extérieur
 * @param {number} start angle de départ en degrés
 * @param {number} end angle de fin en degrés, supérieur à start
 * @returns {string} attribut d d'un <path>
 */
function ringPath(inner, outer, start, end) {
  const large = end - start > 180 ? 1 : 0;
  const [ax, ay] = polar(outer, start);
  const [bx, by] = polar(outer, end);
  const arc = `M${ax} ${ay}A${outer} ${outer} 0 ${large} 1 ${bx} ${by}`;
  if (inner === outer) return arc;
  const [cx, cy] = polar(inner, end);
  const [dx, dy] = polar(inner, start);
  return `${arc}L${cx} ${cy}A${inner} ${inner} 0 ${large} 0 ${dx} ${dy}Z`;
}

if (typeof module !== 'undefined') {
  module.exports = {
    isMissing,
    statusOf,
    isMeasured,
    levelStatus,
    rankStatus,
    hasThreshold,
    isLit,
    certThreshold,
    thresholdProgress,
    dataCards,
    cardTiers,
    tierNotions,
    tierProgress,
    progressText,
    titleCount,
    objectiveText,
    findTitle,
    reasonText,
    sourceReason,
    titleProgress,
    obtainedWords,
    STATE_GROUPS,
    RARITY_LEVELS,
    RANK_TONES,
    CERT_STATES,
    stateLevel,
    rankTone,
    tierTone,
    RED_TONE,
    cardReaches,
    ratioRank,
    xpRank,
    averageRank,
    answersRatio,
    certProgress,
    certState,
    dateKey,
    rankedCertifications,
    RANK_LADDER,
    stateGroup,
    shortLabel,
    splitName,
    levelRatio,
    polar,
    ringPath,
  };
}
