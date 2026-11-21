'use strict';

/*
 * Maquette « Système » : fenêtre de statut.
 *
 * Deux blocs de niveau (42 et Système) avec leur jauge vers la cible, leur total d'XP et
 * la liste déroulante de l'XP par projet ; le bloc « Achievements » avec les deux
 * « I AM THE ANSWER » ; le bloc « Achievements de 42 », facultatifs, sur toute la
 * largeur ; le bloc « Titres » (certs.js). Chacun des trois premiers porte un rang et sa
 * couleur : tranches d'XP égales pour le niveau 42, moyenne des rangs des domaines pour le
 * niveau Système, avancement des titres pour les achievements.
 * Une liste vide est remplacée par un texte qui dit pourquoi.
 */

const API_SOURCE = 'API de l\'intranet 42';

/** Valeur statuée value suivie de son étiquette de statut, ou l'étiquette seule. */
function statedValue(value, text) {
  return el(
    'span',
    {className: 'stated'},
    !isMissing(value) && el('span', {className: 'stated-value', text}),
    statusTag(value, levelStatus(value)),
  );
}

/**
 * Liste déroulante de l'XP par projet, ou le texte emptyReason si elle est vide.
 *
 * @param {Array<{name: string, xp: number}>|undefined} projects projets et leur XP
 * @param {string} emptyReason raison affichée quand aucun projet n'est connu
 * @returns {HTMLElement}
 */
function projectList(projects, emptyReason) {
  const list = Array.isArray(projects) ? projects : [];
  if (!list.length) {
    return el('p', {className: 'empty', text: `Aucun projet à lister : ${emptyReason}.`});
  }
  return el(
    'details',
    {className: 'projects'},
    el('summary', {text: `XP par projet (${list.length})`}),
    el('ul', {}, list.map(project => el(
      'li',
      {},
      el('span', {text: project.name}),
      el('span', {text: `${formatNumber(project.xp)} XP`}),
    ))),
  );
}

/**
 * Ligne du rang d'un bloc : insigne, rang en toutes lettres et sa règle en infobulle.
 *
 * @param {string|null} rank rang de RANK_LADDER, null s'il ne se mesure pas
 * @param {string} rule règle de calcul du rang, un sujet par ligne
 * @returns {HTMLElement}
 */
function blockRank(rank, rule) {
  return el(
    'p',
    {className: 'block-rank'},
    rankBadge(rank),
    el('span', {text: rank ? `Rang ${rank}` : 'Rang non mesurable'}),
    info(rule),
  );
}

/** Règle du rang du niveau 42 : tranches d'XP égales jusqu'à l'XP de la cible. */
function xpRankRule(levels) {
  const slice = levels.xpTarget / RANK_LADDER.length;
  if (!Number.isFinite(slice) || slice <= 0) {
    return 'L’XP du niveau cible manque dans les données : le rang ne se mesure pas.';
  }
  return `Une tranche d’XP par rang, de E à Nation : ${formatNumber(slice)} XP chacune.\n`
    + `Le niveau ${levels.levelTarget} vaut ${formatNumber(levels.xpTarget)} XP.`;
}

/**
 * Bloc d'un niveau : rang, valeur, jauge vers la cible, total d'XP, XP par projet.
 *
 * @param {{title: string, level: Object, xp: Object, target: number, projects: Array,
 *   emptyReason: string, order: number, rank: string|null, rule: string}} block level
 *   et xp : valeurs statuées ; rank et rule : arguments de blockRank
 * @returns {HTMLElement} cadre rompu si le niveau dépasse target, électrisé sinon
 */
function levelWindow(block) {
  const {level, xp, target} = block;
  const known = !isMissing(level);
  const tone = rankTone(block.rank);
  const over = known && Number.isFinite(target) && level.value > target;
  const frame = systemWindow(
    {title: block.title, className: 'level-window', order: block.order, tone},
    blockRank(block.rank, block.rule),
    el('p', {className: 'level-figure'}, statedValue(
      level,
      known ? formatNumber(level.value, 2) : '',
    )),
    known && Number.isFinite(target) && el(
      'div',
      {className: 'level-goal'},
      bar(levelRatio(level.value, target), tone),
      el(
        'p',
        {},
        `${formatNumber(level.value, 2)} / `,
        over ? brokenLimit(formatNumber(target)) : formatNumber(target),
      ),
    ),
    over && el('p', {className: 'over-label', text: 'Limite du Système dépassée'}),
    el(
      'p',
      {className: 'level-xp'},
      el('span', {text: 'Total d’XP'}),
      statedValue(xp, isMissing(xp) ? '' : `${formatNumber(xp.value)} XP`),
    ),
    projectList(block.projects, block.emptyReason),
  );
  if (over) breakLimit(frame);
  else chargeWindow(frame, block.rank);
  return frame;
}

/** Entrée d'un titre à progression chiffrée : nom, condition, jauge dorée, obtention. */
function answerEntry(title) {
  const progress = titleProgress(title);
  const digits = Number.isInteger(title.target) && Number.isInteger(progress.value) ? 0 : 2;
  const figures = `${formatNumber(progress.value, digits)} / ${formatNumber(title.target)}`;
  return el(
    'li',
    {className: 'answer'},
    el(
      'p',
      {className: 'answer-name'},
      el('span', {className: 'answer-title', text: title.name}),
      el('span', {className: 'answer-scope', text: title.scope}),
    ),
    el('p', {className: 'answer-condition', text: capitalizeFirst(`${title.condition}.`)}),
    bar(progress.ratio, 'gold'),
    el(
      'p',
      {className: 'answer-figures'},
      el('span', {text: figures}),
      el('span', {text: obtainedWords(title.obtained) || 'obtention inconnue'}),
      statusTag(title.progress),
    ),
  );
}

/** Entrée d'un titre sans progression chiffrée : nom, portée et statut avec sa raison. */
function plainTitleEntry(title) {
  return el(
    'li',
    {className: 'answer'},
    el(
      'p',
      {className: 'answer-name'},
      el('span', {className: 'answer-plain', text: `${title.name} de ${title.scope}`}),
      statusTag(title.progress),
    ),
    el('p', {
      className: 'answer-condition',
      text: capitalizeFirst(`${reasonText(title.progress)}.`),
    }),
  );
}

/** Ligne d'un achievement de 42 : nom, obtention et titre qu'il donne s'il en donne un. */
function schoolRow(item) {
  const title = item.title
    && `${item.obtained ? 'Titre obtenu' : 'Titre à la clé'} : ${item.title}`;
  return el(
    'li',
    {attrs: {'data-obtained': item.obtained ? 'yes' : 'no'}},
    el('span', {className: 'school-name', text: item.name}, info(item.description)),
    el('span', {
      className: 'school-state',
      text: item.obtained ? `obtenu le ${item.obtainedOn}` : 'non obtenu',
    }),
    title && el('span', {className: 'school-title', text: title}),
  );
}

/**
 * Bloc « Achievements de 42 » : la liste de data.achievements quand l'API la fournit,
 * sinon les titres de data.titles sans progression chiffrée, avec leur raison.
 */
function schoolWindow(data) {
  const list = Array.isArray(data.achievements) ? data.achievements : [];
  const others = (Array.isArray(data.titles) ? data.titles : [])
    .filter(title => !titleProgress(title));
  const obtained = list.filter(item => item.obtained).length;
  const body = list.length
    ? [
      el('p', {
        className: 'school-count',
        text: `${obtained} obtenus sur ${list.length}. Facultatifs : ils ne comptent `
          + 'dans aucun rang.',
      }),
      el('ul', {className: 'school'}, list.map(schoolRow)),
    ]
    : el('ul', {className: 'answers'}, others.map(plainTitleEntry));
  return systemWindow(
    {title: 'Achievements de 42', className: 'school-window', order: 3},
    list.length || others.length
      ? body
      : el('p', {className: 'empty', text: 'Aucun achievement de 42 disponible.'}),
  );
}

/** Bloc « Achievements » : les titres de data.titles à progression chiffrée. */
function achievementsWindow(data) {
  const titles = Array.isArray(data.titles) ? data.titles : [];
  const measured = titles.filter(title => titleProgress(title));
  const rank = ratioRank(answersRatio(titles) ?? NaN);
  const rule = 'Une tranche par rang sur l’avancement des « I AM THE ANSWER », à parts '
    + 'égales.\nLes achievements de 42 ne comptent pas dans ce rang.';
  const frame = systemWindow(
    {
      title: 'Achievements',
      className: 'achievements-window',
      order: 2,
      tone: rankTone(rank),
    },
    blockRank(rank, rule),
    measured.length
      ? el('ul', {className: 'answers'}, measured.map(answerEntry))
      : el('p', {className: 'empty', text: 'Aucun titre à progression chiffrée.'}),
  );
  chargeWindow(frame, rank);
  return frame;
}

/** Ligne des sources de données : libellé et état de chacune. */
function sourcesLine(data) {
  const sources = Array.isArray(data.sources) ? data.sources : [];
  if (!sources.length) return null;
  const words = source => {
    const state = SOURCE_STATES[source.status] || 'état inconnu';
    const read = Number.isFinite(source.read) ? `, ${source.read} lignes` : '';
    return `${source.label} (${state}${read})`;
  };
  return el('p', {
    className: 'sources',
    text: `Sources : ${sources.map(words).join(', ')}.`,
  });
}

/**
 * Affiche la fenêtre de statut, ou met seulement à jour la carte au premier plan si la
 * fenêtre est déjà affichée.
 *
 * @param {HTMLElement} root conteneur de la vue
 * @param {Object} data objet window.SYSTEME
 * @param {string} [certId] certification dont la carte s'ouvre au premier plan
 */
function renderStatus(root, data, certId) {
  const context = statusCertContext(data);
  if (root.querySelector('.status-view')) {
    syncCertDialog(root, data, context, certId);
    return;
  }
  const levels = data.levels || {};
  const systemXp = levels.systemXp
    || {value: null, status: 'unmeasurable', reason: levels.systemLevel?.reason};
  root.replaceChildren(el(
    'div',
    {className: 'status-view'},
    backLink('#/', 'Retour à la roue'),
    el('h2', {className: 'section-name', text: 'Statut'}),
    el(
      'div',
      {className: 'status-grid'},
      levelWindow({
        title: 'Niveau 42',
        level: levels.level42,
        xp: levels.xp42,
        target: levels.levelTarget,
        projects: levels.projects42,
        emptyReason: sourceReason(data.sources, API_SOURCE),
        order: 0,
        rank: xpRank(levels),
        rule: xpRankRule(levels),
      }),
      levelWindow({
        title: 'Niveau Système',
        level: levels.systemLevel,
        xp: systemXp,
        target: levels.levelTarget,
        projects: levels.projectsSystem,
        emptyReason: reasonText(levels.systemLevel),
        order: 1,
        rank: averageRank(dataCards(data)),
        rule: 'Moyenne des rangs des domaines de la roue, arrondie au rang le plus '
          + 'proche.\nE vaut 1, Nation vaut 7, un domaine sans rang vaut 0.',
      }),
      achievementsWindow(data),
      schoolWindow(data),
      titlesWindow(data),
    ),
    sourcesLine(data),
    certDialog(),
  ));
  syncCertDialog(root, data, context, certId);
}
