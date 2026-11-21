'use strict';

/*
 * Maquette « Système » : boîte d'événements de la barre du haut et annonce au retour.
 *
 * À chaque visite, l'état mesurable (events.js) se compare à celui de la visite
 * précédente, gardé dans le stockage du navigateur. Ce qui a progressé s'annonce dans une
 * fenêtre qui se replie vers le bouton « Événements », puis reste dans sa boîte, dont une
 * pastille rouge compte les nouveautés jusqu'à sa fermeture. Première visite : aucun
 * événement. Stockage indisponible : la boîte le dit, la page fonctionne. Un événement
 * déjà dans la boîte n'est jamais annoncé deux fois. L'annonce joue un son (sound.js) à
 * l'ouverture ou au premier geste du visiteur : celui d'un niveau gagné si elle en
 * compte un, celui d'une notification sinon. Chargé après dom.js, sound.js et events.js.
 */

const VISIT_KEY = 'progression-system:visit';
const INBOX_LIMIT = 100;
const ANNOUNCE_LINES = 5;
const ANNOUNCE_BASE_MS = 3500;
const ANNOUNCE_LINE_MS = 900;
const FOLD_MS = 460;
/* Plusieurs niveaux gagnés : le son de niveau frappe une seconde fois après ce délai. */
const UNLOCK_ECHO_MS = 500;
const COUNT_CAP = 99;
const ALERT_PATH = 'M8 1.5L13.6 4.75V11.25L8 14.5L2.4 11.25V4.75ZM8 5V8.8M8 10.9V11';
const eventDate = new Intl.DateTimeFormat('fr-FR', {dateStyle: 'short', timeStyle: 'short'});

/**
 * Mémoire de la dernière visite dans localStorage, sous key.
 *
 * @param {string} key clé de stockage
 * @returns {{read: function(): {available: boolean, state: ?Object}, write:
 *   function(Object): boolean}} read : available faux si le stockage est refusé, state
 *   nul s'il est vide ou illisible ; write : faux si l'écriture échoue
 */
function visitStore(key) {
  return {
    read() {
      try {
        const raw = localStorage.getItem(key);
        try {
          return {available: true, state: raw ? JSON.parse(raw) : null};
        } catch {
          return {available: true, state: null};
        }
      } catch {
        return {available: false, state: null};
      }
    },
    write(state) {
      try {
        localStorage.setItem(key, JSON.stringify(state));
        return true;
      } catch {
        return false;
      }
    },
  };
}

/** Mémoire de visite non conservée, de même forme que visitStore, partie de state. */
function memoryStore(state) {
  let kept = state;
  return {
    read: () => ({available: true, state: kept}),
    write(next) {
      kept = next;
      return true;
    },
  };
}

/** true si event est un événement affichable : famille connue, texte, adresse interne. */
function isStoredEvent(event) {
  return Boolean(event)
    && Object.hasOwn(EVENT_FAMILIES, event.family)
    && typeof event.text === 'string'
    && typeof event.href === 'string'
    && event.href.startsWith('#/');
}

/**
 * Compare la visite courante à la précédente et enregistre la courante.
 *
 * @param {Object} store résultat de visitStore ou de memoryStore
 * @param {Object} snapshot résultat de snapshotOf pour la visite courante
 * @returns {{available: boolean, fresh: Object[], events: Object[], unread: number}}
 *   fresh : événements de cette visite ; events : toute la boîte, les plus récents
 *   d'abord ; available : faux si rien ne peut être gardé d'une visite à l'autre
 */
function recordVisit(store, snapshot) {
  const {available, state} = store.read();
  const known = isSnapshot(state?.snapshot);
  const past = known && Array.isArray(state.events) ? state.events.filter(isStoredEvent) : [];
  const told = new Set(past.map(event => event.text));
  const at = Date.now();
  const fresh = (known ? detectEvents(state.snapshot, snapshot) : [])
    .filter(event => !told.has(event.text))
    .map(event => ({...event, at}));
  const events = [...fresh, ...past].slice(0, INBOX_LIMIT);
  const unread = Math.min(
    events.length,
    fresh.length + (known && Number.isInteger(state.unread) ? Math.max(0, state.unread) : 0),
  );
  const saved = available && store.write({snapshot, events, unread});
  return {available: saved, fresh, events, unread};
}

/** Pictogramme d'alerte du Système : un point d'exclamation dans un hexagone. */
function alertIcon() {
  return svgEl(
    'svg',
    {class: 'icon', viewBox: '0 0 16 16', 'aria-hidden': 'true'},
    svgEl('path', {d: ALERT_PATH}),
  );
}

/** Ligne de la boîte : famille, texte et date de l'événement, lien vers sa vue. */
function inboxRow(event, isNew) {
  const date = Number.isFinite(event.at) ? new Date(event.at) : null;
  return el(
    'li',
    {attrs: {'data-tone': event.tone || null}},
    el(
      'a',
      {className: 'inbox-event', attrs: {href: event.href}},
      el(
        'span',
        {className: 'inbox-family'},
        EVENT_FAMILIES[event.family],
        isNew && el('span', {className: 'inbox-new', text: 'nouveau'}),
      ),
      el('span', {className: 'inbox-text', text: event.text}),
      date && el('time', {
        className: 'inbox-date',
        text: eventDate.format(date),
        attrs: {datetime: date.toISOString()},
      }),
    ),
  );
}

/** Remplit le panneau de la boîte selon visit (résultat de recordVisit). */
function renderInbox(panel, visit) {
  const empty = visit.available
    ? 'Aucun événement : la boîte se remplit quand une valeur progresse entre deux visites.'
    : 'Le stockage du navigateur est indisponible : les événements ne peuvent pas être '
      + 'suivis d’une visite à l’autre.';
  panel.replaceChildren(
    el(
      'header',
      {className: 'window-head'},
      el('h2', {className: 'window-title', text: 'Événements'}),
    ),
    visit.events.length
      ? el(
        'ol',
        {className: 'inbox-list'},
        visit.events.map((event, index) => inboxRow(event, index < visit.unread)),
      )
      : el('p', {className: 'empty', text: empty}),
  );
}

/** Pose sur le bouton de la boîte la pastille et le nom qui comptent unread nouveautés. */
function showCount(parts, unread) {
  const noun = unread > 1 ? 'nouveaux' : 'nouveau';
  parts.count.textContent = unread > COUNT_CAP ? `${COUNT_CAP}+` : String(unread);
  parts.count.hidden = !unread;
  parts.button.setAttribute(
    'aria-label',
    unread ? `Événements, ${unread} ${noun}` : 'Événements',
  );
}

/** Replie la fenêtre d'annonce toast vers le bouton target ; résolue une fois repliée. */
function foldInto(toast, target) {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return Promise.resolve();
  const from = toast.getBoundingClientRect();
  const to = target.getBoundingClientRect();
  const shiftX = to.left + to.width / 2 - (from.left + from.width / 2);
  const shiftY = to.top + to.height / 2 - (from.top + from.height / 2);
  return toast.animate(
    [
      {transform: 'none', opacity: 1},
      {transform: `translate(${shiftX}px, ${shiftY}px) scale(0.08)`, opacity: 0},
    ],
    {duration: FOLD_MS, easing: 'cubic-bezier(0.7, 0, 0.84, 0)', fill: 'forwards'},
  ).finished;
}

/**
 * Annonce les événements fresh dans layer : les premiers un à un, le reste en un compte.
 *
 * @param {{layer: HTMLElement, button: HTMLElement, count: HTMLElement}} parts éléments
 *   de la page
 * @param {Object[]} fresh événements de cette visite, au moins un
 * @returns {function(): boolean} ferme l'annonce ; faux si elle l'était déjà
 */
function announce(parts, fresh) {
  const shown = fresh.slice(0, ANNOUNCE_LINES);
  const rest = fresh.length - shown.length;
  const close = el('button', {className: 'button', text: 'Fermer', attrs: {type: 'button'}});
  const total = fresh.length > 1 ? `${fresh.length} déblocages` : 'Un déblocage';
  const toast = systemWindow(
    {title: 'Événements débloqués', level: 'p', className: 'unlock-window'},
    el('p', {className: 'unlock-count', text: `${total} depuis votre dernière visite.`}),
    el('ol', {className: 'unlock-list'}, shown.map((event, index) => {
      const line = el('li', {text: event.text, attrs: {'data-tone': event.tone || null}});
      line.style.setProperty('--order', String(index));
      return line;
    })),
    rest > 0 && el('p', {
      className: 'unlock-more',
      text: `Et ${rest} ${rest > 1 ? 'autres' : 'autre'} dans la boîte « Événements ».`,
    }),
    close,
  );
  let timer = null;
  let open = true;
  const dismiss = () => {
    if (!open) return false;
    open = false;
    clearTimeout(timer);
    playSound('store');
    foldInto(toast, parts.button).catch(() => {}).then(() => {
      toast.remove();
      parts.count.classList.add('is-landing');
    });
    return true;
  };
  const arm = () => {
    clearTimeout(timer);
    timer = setTimeout(dismiss, ANNOUNCE_BASE_MS + shown.length * ANNOUNCE_LINE_MS);
  };
  toast.querySelector('.window-head').prepend(alertIcon());
  close.addEventListener('click', dismiss);
  for (const pause of ['pointerenter', 'focusin']) {
    toast.addEventListener(pause, () => clearTimeout(timer));
  }
  for (const resume of ['pointerleave', 'focusout']) toast.addEventListener(resume, arm);
  parts.layer.replaceChildren(toast);
  arm();
  const leveled = fresh.filter(event => event.family === 'levels').length;
  playSoundOnGesture(leveled ? 'unlock' : 'notify', () => open);
  if (leveled > 1) {
    setTimeout(() => playSoundOnGesture('unlock', () => open), UNLOCK_ECHO_MS);
  }
  return dismiss;
}

/**
 * Branche la boîte d'événements et annonce ce qui a progressé depuis la dernière visite.
 *
 * @param {{button: HTMLElement, count: HTMLElement, panel: HTMLElement, layer:
 *   HTMLElement}} parts bouton de la barre, sa pastille, son panneau (popover) et la zone
 *   d'annonce
 * @param {Object} snapshot résultat de snapshotOf pour la visite courante
 * @param {Object} store résultat de visitStore ou de memoryStore
 * @returns {{dismiss: function(): boolean, isOpen: function(): boolean}} dismiss ferme
 *   l'annonce (faux si elle l'était déjà) ; isOpen : panneau de la boîte ouvert
 */
function initInbox(parts, snapshot, store) {
  const visit = recordVisit(store, snapshot);
  let dismiss = () => false;
  renderInbox(parts.panel, visit);
  showCount(parts, visit.unread);
  parts.button.hidden = false;
  parts.panel.addEventListener('toggle', event => {
    if (event.newState !== 'closed' || !visit.unread) return;
    visit.unread = 0;
    store.write({snapshot, events: visit.events, unread: 0});
    renderInbox(parts.panel, visit);
    showCount(parts, 0);
  });
  parts.panel.addEventListener('click', event => {
    if (event.target.closest('a')) parts.panel.hidePopover();
  });
  if (visit.fresh.length) dismiss = announce(parts, visit.fresh);
  return {dismiss: () => dismiss(), isOpen: () => parts.panel.matches(':popover-open')};
}
