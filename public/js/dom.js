'use strict';

/*
 * Maquette « Système » : primitives DOM, composants partagés et infobulle.
 *
 * Tout texte passe par textContent. Une valeur statuée montre toujours son statut en
 * toutes lettres ; sa raison s'ouvre en infobulle au survol et au focus (attribut
 * data-tip). L'infobulle est unique, rendue sur le body et bornée à l'écran. Chargé
 * après model.js, avant les vues.
 */

const SVG_NS = 'http://www.w3.org/2000/svg';
const STATUS_LABELS = {
  observed: 'observé',
  estimated: 'estimé',
  insufficient: 'insuffisant',
  unmeasurable: 'non mesurable',
};
const ICON_PATHS = {
  back: 'M10 3.5L5.5 8L10 12.5M5.5 8H14',
  chevron: 'M6 3.5L10.5 8L6 12.5',
  info: 'M8 7.2V11.6M8 4.4V4.5M8 1.5A6.5 6.5 0 1 0 8 14.5A6.5 6.5 0 1 0 8 1.5',
  network: 'M3.5 4.5L8 8L12.5 3.5M8 8V13M3.5 4.5V4.6M12.5 3.5V3.6M8 13V13.1',
  close: 'M4 4L12 12M12 4L4 12',
};
const GLYPH_SHAPES = {
  high: ['path', {d: 'M7 0.5L13.5 7L7 13.5L0.5 7Z'}],
  low: ['circle', {cx: 7, cy: 7, r: 4.2}],
  declared: ['circle', {cx: 7, cy: 7, r: 5.2}],
  unmet: ['circle', {cx: 7, cy: 7, r: 3.6}],
};
const TIP_GAP = 10;
const TIP_EDGE = 8;
const numberFormats = new Map();

const byId = id => document.getElementById(id);

/** Nombre au format français, avec digits décimales exactement. */
function formatNumber(value, digits = 0) {
  if (!numberFormats.has(digits)) {
    numberFormats.set(digits, new Intl.NumberFormat('fr-FR', {
      minimumFractionDigits: digits,
      maximumFractionDigits: digits,
    }));
  }
  return numberFormats.get(digits).format(value);
}

/** Texte text aux guillemets, deux-points et points-virgules insécables. */
function frenchSpacing(text) {
  return String(text)
    .replaceAll('« ', '« ')
    .replaceAll(' »', ' »')
    .replaceAll(' :', ' :')
    .replaceAll(' ;', ' ;');
}

/** Texte text avec sa première lettre en capitale. */
function capitalizeFirst(text) {
  return text.charAt(0).toUpperCase() + text.slice(1);
}

/** Pose sur element les attributs attrs, valeurs nulles ou fausses omises. */
function setAttributes(element, attrs = {}) {
  for (const [name, value] of Object.entries(attrs)) {
    if (value !== null && value !== undefined && value !== false) {
      element.setAttribute(name, String(value));
    }
  }
}

/**
 * Crée un élément HTML.
 *
 * el('p', {className: 'empty', text: 'Aucune donnée'}) -> <p class="empty">
 *
 * @param {string} tag nom de balise
 * @param {{className?: string, text?: string, attrs?: Object}} options
 * @param {...(Node|string|null|false|undefined)} children enfants, valeurs fausses omises
 * @returns {HTMLElement}
 */
function el(tag, options = {}, ...children) {
  const element = document.createElement(tag);
  if (options.className) element.className = options.className;
  if (options.text !== undefined) element.textContent = frenchSpacing(options.text);
  setAttributes(element, options.attrs);
  element.append(...children.flat().filter(Boolean));
  return element;
}

/** Crée un élément SVG tag avec ses attributs attrs et ses enfants. */
function svgEl(tag, attrs = {}, ...children) {
  const element = document.createElementNS(SVG_NS, tag);
  setAttributes(element, attrs);
  element.append(...children.flat().filter(Boolean));
  return element;
}

/** Pictogramme name d'ICON_PATHS, décoratif (masqué aux lecteurs d'écran). */
function icon(name) {
  return svgEl(
    'svg',
    {class: 'icon', viewBox: '0 0 16 16', 'aria-hidden': 'true'},
    svgEl('path', {d: ICON_PATHS[name]}),
  );
}

/**
 * Nœuds d'un libellé : les passages entre accents graves deviennent des <code>.
 *
 * @param {string} label texte, avec ou sans `code`
 * @returns {Array<Node|string>}
 */
function richText(label) {
  return frenchSpacing(label)
    .split('`')
    .map((part, index) => (index % 2 ? el('code', {text: part}) : part))
    .filter(Boolean);
}

/** Attributs qui rendent un élément porteur de l'infobulle text, au survol et au focus. */
function tipAttrs(text) {
  return {'data-tip': text, tabindex: '0'};
}

/**
 * Pictogramme ⓘ porteur de l'infobulle text, précédé d'une espace insécable pour ne
 * jamais passer seul à la ligne.
 *
 * @param {string} text contenu de l'infobulle
 * @returns {Array<Node|string>} à placer juste après le dernier mot du libellé
 */
function info(text) {
  const mark = el(
    'span',
    {className: 'info', attrs: {...tipAttrs(text), role: 'img', 'aria-label': text}},
    icon('info'),
  );
  return [' ', mark];
}

/**
 * Étiquette du statut d'une valeur statuée, en toutes lettres, avec sa raison en
 * infobulle.
 *
 * @param {{status?: string, reason?: string}|undefined} value valeur statuée
 * @param {string} [status] statut à afficher, par défaut celui de value
 * @returns {HTMLElement}
 */
function statusTag(value, status = statusOf(value)) {
  const reason = value?.reason;
  const attrs = {'data-status': status};
  if (reason || status !== 'observed') {
    Object.assign(attrs, tipAttrs(frenchSpacing(reasonText(value))));
  }
  return el('span', {className: 'tag', text: STATUS_LABELS[status], attrs});
}

/** Jauge remplie à ratio (0 à 1), décorative ; tone : ton de rareté (1 à 7) ou « gold ». */
function bar(ratio, tone = null) {
  const track = el(
    'span',
    {className: 'bar', attrs: {'data-tone': tone || null, 'aria-hidden': 'true'}},
    el('span', {className: 'bar-fill'}),
  );
  track.style.setProperty('--ratio', String(ratio));
  track.style.display = 'block';
  return track;
}

/**
 * Signe d'état d'une notion, décoratif : forme du rendu group de STATE_GROUPS, couleur
 * du niveau de rareté level (0 : sans couleur propre).
 *
 * @param {string} group code de STATE_GROUPS
 * @param {number} [level] résultat de stateLevel
 * @returns {SVGSVGElement}
 */
function stateGlyph(group, level = 0) {
  const [tag, attrs] = GLYPH_SHAPES[group] || GLYPH_SHAPES.unmet;
  return svgEl(
    'svg',
    {
      class: 'glyph',
      viewBox: '0 0 14 14',
      'data-group': group,
      'data-level': level || null,
      'aria-hidden': 'true',
    },
    svgEl(tag, attrs),
  );
}

/**
 * Fenêtre du Système : cadre, titre en en-tête et contenu.
 *
 * @param {{title: string, level?: string, className?: string, order?: number,
 *   tone?: number, attrs?: Object}} options level : balise du titre (h2 par défaut) ;
 *   order : rang dans le dépliage en cascade ; tone : ton de rareté du cadre (1 à 7)
 * @param {...(Node|string|null|false)} body contenu de la fenêtre
 * @returns {HTMLElement}
 */
function systemWindow(options, ...body) {
  const head = el(
    'header',
    {className: 'window-head'},
    el(options.level || 'h2', {className: 'window-title', text: options.title}),
  );
  const frame = el(
    'section',
    {className: `window unfold ${options.className || ''}`.trim(), attrs: options.attrs},
    head,
    ...body,
  );
  frame.style.setProperty('--order', String(options.order || 0));
  if (options.tone) frame.dataset.tone = String(options.tone);
  return frame;
}

/** Lien de retour vers href, avec le rappel de la touche Échap. */
function backLink(href, label) {
  return el(
    'p',
    {className: 'back'},
    el('a', {className: 'button', attrs: {href}}, icon('back'), el('span', {text: label})),
    el('kbd', {className: 'key', text: 'Échap'}),
  );
}

/**
 * Fenêtre de repli quand window.SYSTEME est absent ou illisible : la cause (le fichier de
 * données du site) et un bouton « Réessayer » qui recharge la page.
 *
 * @returns {HTMLElement}
 */
function dataFailureWindow() {
  const retry = el('button', {
    className: 'button',
    text: 'Réessayer',
    attrs: {type: 'button'},
  });
  retry.addEventListener('click', () => location.reload());
  return systemWindow(
    {title: 'Chargement impossible', className: 'fatal'},
    el('p', {
      text: 'Le fichier de données du site est absent ou illisible, la page ne peut '
        + 'pas s’afficher. « Réessayer » recharge la page.',
    }),
    retry,
  );
}

/** true si data est l'objet de données attendu (ni absent, ni tableau, ni primitive). */
function isDataObject(data) {
  return Boolean(data) && typeof data === 'object' && !Array.isArray(data);
}

/** Place l'infobulle tip au-dessus de target, en dessous si la place manque. */
function placeTip(tip, target) {
  const box = target.getBoundingClientRect();
  const {offsetWidth: width, offsetHeight: height} = tip;
  const above = box.top - TIP_GAP - height;
  const top = above >= TIP_EDGE ? above : box.bottom + TIP_GAP;
  const centered = box.left + box.width / 2 - width / 2;
  const left = Math.min(Math.max(TIP_EDGE, centered), innerWidth - width - TIP_EDGE);
  tip.style.translate = `${Math.round(left)}px ${Math.round(top)}px`;
}

/**
 * Branche l'infobulle unique tip sur tout élément [data-tip] du document : ouverte au
 * survol et au focus, fermée à la sortie, au défilement et au redimensionnement. Avec
 * l'attribut popover, elle passe au-dessus d'une carte ouverte au premier plan.
 *
 * @param {HTMLElement} tip élément role="tooltip" de la page
 * @returns {{hide: function(), isOpen: function(): boolean}} pour la touche Échap
 */
function initTips(tip) {
  let owner = null;
  const hide = () => {
    if (!owner) return;
    owner.removeAttribute('aria-describedby');
    owner = null;
    tip.hidden = true;
    if (tip.matches(':popover-open')) tip.hidePopover();
  };
  const show = event => {
    const target = event.target.closest?.('[data-tip]');
    if (!target || target === owner) return;
    hide();
    owner = target;
    tip.textContent = target.getAttribute('data-tip');
    tip.hidden = false;
    if (tip.popover) tip.showPopover();
    owner.setAttribute('aria-describedby', tip.id);
    placeTip(tip, target);
  };
  const leave = event => {
    if (owner && !owner.contains(event.relatedTarget)) hide();
  };
  document.addEventListener('pointerover', show);
  document.addEventListener('focusin', show);
  document.addEventListener('pointerout', leave);
  document.addEventListener('focusout', leave);
  document.addEventListener('scroll', hide, {capture: true, passive: true});
  addEventListener('resize', hide);
  return {hide, isOpen: () => Boolean(owner)};
}
