'use strict';

/*
 * Maquette « Système » : données fictives de « ?demo », pour juger les couleurs et les
 * états que les données réelles n'atteignent pas encore.
 *
 * Rangs à tour de rôle sur les cartes, premiers paliers portés à un même état,
 * certifications dans chacun de leurs états et achievements de 42 inventés ; avec
 * « ?demo=over », le niveau 42 dépasse aussi sa cible ; avec « ?demo » seul ou
 * « ?demo=red », des cartes voisines et isolées ont leurs notions au moins rouges, avec
 * « ?demo=red-all » toutes. Rien de ce fichier ne s'affiche hors de « ?demo », et la
 * barre du haut le signale (app.js).
 */

const DEMO_REASON = 'valeur fictive de la démonstration';
/*
 * Cartes au moins rouges : voisines et isolées sous ?demo et ?demo=red, toutes sous
 * ?demo=red-all.
 */
const DEMO_RED_SOME = index => [0, 1, 3].includes(index % 5);
const DEMO_RED = {'': DEMO_RED_SOME, red: DEMO_RED_SOME, 'red-all': () => true};
/* Rapport du niveau 42 fictif à sa cible sous « ?demo=over ». */
const DEMO_OVER = 1.0924;
const DEMO_CONDITIONS = 'examen en ligne surveillé, 40 questions en 65 minutes, 70 % de '
  + 'bonnes réponses (conditions fictives).';
const DEMO_ACHIEVEMENTS = [
  ['Premier projet validé', 'Valider un premier projet du cursus.', '14/03/2025'],
  ['Dix évaluations données', 'Évaluer dix projets d’autres étudiants.', '02/06/2025'],
  ['Entraide V', 'Aider cinquante étudiants.', '30/09/2025', 'Bienfaiteur'],
  ['Niveau 10', 'Atteindre le niveau 10.', '21/01/2026'],
  ['Projet validé à 125', 'Valider un projet avec tous ses bonus.', null],
  ['Cent évaluations données', 'Évaluer cent projets d’autres étudiants.', null, 'Arbitre'],
  ['Niveau 21', 'Atteindre le niveau 21.', null],
].map(([name, description, obtainedOn, title]) => ({
  name,
  description: `${description}\nAchievement fictif de la démonstration.`,
  obtained: Boolean(obtainedOn),
  obtainedOn,
  title,
}));

/** Copie de notions où chaque identifiant de ids passe à l'état state. */
function withState(notions, ids, state) {
  const changed = Object.fromEntries(ids.map(id => [id, {...notions[id], state}]));
  return {...notions, ...changed};
}

/**
 * Certification fictive selon son rang turn : ses notions sont celles du premier palier,
 * puis elle est obtenue, puis ses notions sont celles du deuxième palier, puis inchangée.
 */
function demoCertification(card, cert, turn) {
  const tiers = cardTiers(card);
  if (turn % 4 === 1) {
    return {
      ...cert,
      obtained: {value: true, status: 'observed', reason: DEMO_REASON},
      obtainedOn: `${String(10 + turn).slice(-2)}/0${1 + (turn % 9)}/2026`,
    };
  }
  if (turn % 4 === 3) return cert;
  return {
    ...cert,
    notions: tierNotions(tiers[turn % 4 === 0 ? 0 : 1]),
    conditions: DEMO_CONDITIONS,
  };
}

/**
 * Copie de notions où, dans les cartes retenues par pick (rang de la carte), chaque
 * notion d'un palier sous l'état rouge y est portée.
 */
function withRedFloor(data, notions, order, pick) {
  const floor = order.findIndex(state => stateLevel(data, state) === RED_TONE);
  const low = dataCards(data)
    .filter((card, index) => pick(index))
    .flatMap(card => cardTiers(card).flatMap(tierNotions))
    .filter(id => order.indexOf(notions[id]?.state) < floor);
  return floor < 0 ? notions : withState(notions, low, order[floor]);
}

/** Copie de levels où le niveau 42 et son XP dépassent leur cible de DEMO_OVER. */
function overLevels(levels) {
  const beyond = (target, digits) => ({
    value: Number((target * DEMO_OVER).toFixed(digits)),
    status: 'observed',
    reason: DEMO_REASON,
  });
  return {
    ...levels,
    level42: beyond(levels.levelTarget, 2),
    xp42: beyond(levels.xpTarget, 0),
  };
}

/**
 * Visite précédente fictive de « ?demo=events » : snapshot en retrait sur le niveau 42,
 * un rang sur trois, un palier sur quatre, une certification sur deux, les états atteints
 * et les titres.
 *
 * @param {Object} snapshot résultat de snapshotOf pour la visite courante
 * @returns {Object} snapshot n'est pas modifié
 */
function demoPastVisit(snapshot) {
  const past = structuredClone(snapshot);
  const ranks = RANK_LADDER.map(step => step.rank);
  const lower = rank => ranks[ranks.indexOf(rank) - 1] || null;
  if (Number.isFinite(past.level42)) past.level42 -= 1.2;
  past.rank42 = lower(past.rank42);
  past.reached = past.reached.map((count, index, all) => (
    index === all.length - 1 ? 0 : Math.max(0, count - 3)
  ));
  Object.values(past.cards).forEach((card, index) => {
    const [first] = Object.values(card.tiers);
    if (index % 3 === 0) card.rank = lower(card.rank);
    if (index % 4 === 1 && first) {
      first.lit = Math.max(0, first.lit - 1);
      first.floor = Math.max(-1, first.floor - 1);
    }
    if (index % 2 === 0) card.certs = card.certs.map(cert => ({...cert, state: 'locked'}));
  });
  for (const title of Object.values(past.titles)) if (title.ratio !== null) title.ratio /= 2;
  const [achieved] = Object.values(past.achievements).filter(item => item.obtained);
  if (achieved) achieved.obtained = false;
  return past;
}

/**
 * Copie de data aux valeurs fictives : rangs, états des premiers paliers, certifications
 * et achievements de 42.
 *
 * @param {Object} data objet window.SYSTEME
 * @param {string|null} mode valeur de « ?demo » : « over », le niveau 42 dépasse sa
 *   cible ; clé de DEMO_RED (dont « » pour « ?demo » seul), des cartes ont toutes leurs
 *   notions au moins rouges
 * @returns {Object} data n'est pas modifié
 */
function withDemoData(data, mode) {
  const order = Array.isArray(data.proofOrder) ? data.proofOrder : [];
  let notions = {...data.notions};
  let turn = 0;
  const cards = dataCards(data).map((card, index) => {
    if (!card) return card;
    const [first, second] = cardTiers(card);
    const state = order[1 + (index % (order.length - 1))];
    if (state) notions = withState(notions, tierNotions(first), state);
    if (state && index % 3 === 0) notions = withState(notions, tierNotions(second), order[1]);
    const certifications = (Array.isArray(card.certifications) ? card.certifications : [])
      .map(cert => demoCertification(card, cert, turn++));
    return {
      ...card,
      certifications,
      rank: {
        value: RANK_LADDER[index % RANK_LADDER.length].rank,
        status: 'observed',
        reason: DEMO_REASON,
      },
    };
  });
  const levels = mode === 'over' ? overLevels(data.levels || {}) : data.levels;
  if (DEMO_RED[mode]) notions = withRedFloor(data, notions, order, DEMO_RED[mode]);
  return {...data, cards, notions, levels, achievements: DEMO_ACHIEVEMENTS};
}
