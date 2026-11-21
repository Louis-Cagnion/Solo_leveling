'use strict';

/*
 * Maquette « Système » : certifications.
 *
 * Section « Certification(s) » d'un domaine (une carte par certification), bloc « Titres »
 * de la fenêtre de statut (« Obtenues », de la plus proche à la plus lointaine, « Non
 * mesurables ») et carte au premier plan d'une certification : prérequis par palier,
 * dépliables en notions, flèches (ou touches gauche et droite) vers la précédente et la
 * suivante. La couleur suit l'état (CERT_STATES de model.js). La carte s'ouvre sur la vue
 * d'où elle est appelée et vit dans l'adresse : « #/status/<certification> » ou
 * « #/c/<carte>/cert/<rang> ». Une notion compte à partir de l'état certThreshold (règle
 * « Certification prête » de /professor). Chargé après section.js (notionRow).
 */

const CERT_TIPS = {
  unmeasurable: 'Les notions de cette certification ne sont pas dans les données : le '
    + 'Système ne peut pas dire si elle est accessible.',
  locked: 'Les compétences connues ne couvrent pas encore la certification : chacune de '
    + 'ses notions doit atteindre l’état exigé.',
  accessible: 'Les compétences connues couvrent la certification.\nAvant de la passer : '
    + 'un examen blanc réussi au seuil officiel (méthode de /professor).',
  obtained: 'Certification obtenue.\nRouge : le domaine n’a pas encore les conditions du '
    + 'rang S, certification exclue.',
  crowned: 'Certification obtenue.\nViolet : le domaine a les conditions du rang Nation.',
};
const CERT_NOTES = {
  obtained: 'domaine sous le rang S',
  crowned: 'conditions du rang Nation remplies',
};
const OBTAINED_TIP = 'De la plus récente à la plus ancienne.\nRouge : obtenue, le domaine '
  + 'n’a pas encore les conditions du rang S.\nViolet : obtenue, le domaine a les '
  + 'conditions du rang Nation.';
const DOMAIN_SCOPE_NOTE = 'Les notions propres à cette certification ne sont pas dans les '
  + 'données : avancement du domaine à la place, sans le détail de ses notions.';

/** Adresse de la carte au premier plan de la certification id, sur la vue de statut. */
function certHref(id) {
  return `#/status/${encodeURIComponent(id)}`;
}

/**
 * Contexte de la carte au premier plan sur la vue de statut : toutes les certifications.
 *
 * @param {Object} data objet window.SYSTEME
 * @returns {{entries: Object[], base: string, hrefOf: function(string): string,
 *   link: function(Object): {href: string, label: string}}} base : adresse de la vue
 *   sans carte ; link : lien de sortie affiché dans la carte
 */
function statusCertContext(data) {
  return {
    entries: rankedCertifications(data),
    base: '#/status',
    hrefOf: certHref,
    link: entry => ({
      href: `#/c/${encodeURIComponent(entry.card.id)}`,
      label: `Ouvrir le domaine ${entry.card.name || entry.card.id}`,
    }),
  };
}

/** Contexte de la carte au premier plan sur la vue du domaine card : ses certifications. */
function sectionCertContext(data, card) {
  const base = `#/c/${encodeURIComponent(card.id)}`;
  return {
    entries: rankedCertifications(data).filter(entry => entry.card === card),
    base,
    hrefOf: id => `${base}/cert/${id.slice(card.id.length + 1)}`,
    link: entry => ({href: certHref(entry.id), label: 'Voir parmi les titres'}),
  };
}

/** État d'une certification en toutes lettres, avec sa date d'obtention si elle l'est. */
function certStateText(entry) {
  const obtained = entry.cert.obtained?.value === true;
  const date = entry.cert.obtainedOn ? `le ${entry.cert.obtainedOn}` : 'date inconnue';
  const label = CERT_STATES[entry.state].label;
  return capitalizeFirst(obtained ? `${label} ${date}` : label);
}

/** Ligne d'état d'une certification : état, précision de couleur, explication. */
function certStateLine(entry) {
  const note = CERT_NOTES[entry.state];
  return el(
    'p',
    {className: 'cert-state'},
    el('span', {text: certStateText(entry)}),
    note && el('span', {className: 'cert-note', text: note}),
    info(CERT_TIPS[entry.state]),
  );
}

/** Texte « n / N notions au moins « seuil » » d'un avancement. */
function litText(data, progress) {
  return `${progress.lit} / ${progress.total} notions au moins « ${certThreshold(data)} »`;
}

/** Jauge et compte de l'avancement d'une certification, ou le texte qui dit qu'il manque. */
function certGauge(data, entry) {
  const {progress} = entry;
  if (!progress) {
    return el('p', {
      className: 'empty',
      text: 'Avancement non mesurable : aucune notion du domaine n’est suivie.',
    });
  }
  const scope = progress.scope === 'domain' ? ' dans le domaine' : '';
  return el(
    'div',
    {className: 'cert-gauge'},
    el('p', {text: `${litText(data, progress)}${scope}`}),
    bar(progress.ratio, CERT_STATES[entry.state].tone),
  );
}

/** Carte d'une certification dans la section de son domaine ; href ouvre ses prérequis. */
function certCard(data, entry, href, order) {
  const {cert} = entry;
  const ids = Array.isArray(cert.notions) ? cert.notions : [];
  const titles = ids.map(id => shortLabel(data.notions?.[id]?.label || id));
  return systemWindow(
    {
      title: cert.label,
      level: 'h4',
      className: 'cert-window',
      order,
      tone: CERT_STATES[entry.state].tone,
    },
    certStateLine(entry),
    entry.state === 'accessible' && cert.conditions && el('p', {
      className: 'cert-conditions',
      text: `Conditions de passage : ${cert.conditions}`,
    }),
    entry.state === 'accessible' && titles.length > 0 && el('p', {
      className: 'cert-conditions',
      text: `Notions abordées : ${titles.join(', ')}.`,
    }),
    certGauge(data, entry),
    el(
      'p',
      {className: 'cert-links'},
      el('a', {className: 'button', attrs: {href}}, 'Prérequis'),
      cert.detail && info(cert.detail),
    ),
  );
}

/** Section « Certification(s) » d'une carte, ou la note qui dit qu'elle n'en a aucune. */
function certificationSection(data, card) {
  const context = sectionCertContext(data, card);
  if (!context.entries.length) {
    return el('p', {className: 'section-certs', text: 'Aucune certification reconnue.'});
  }
  return el(
    'section',
    {className: 'section-certs'},
    el('h3', {
      className: 'group-title',
      text: context.entries.length > 1 ? 'Certifications' : 'Certification',
    }),
    el(
      'div',
      {className: 'cert-cards'},
      context.entries.map((entry, index) => (
        certCard(data, entry, context.hrefOf(entry.id), index)
      )),
    ),
  );
}

/** Cellule cliquable d'une certification dans le bloc « Titres ». */
function certCell(entry) {
  const tone = CERT_STATES[entry.state].tone;
  return el(
    'li',
    {},
    el(
      'a',
      {className: 'cert', attrs: {href: certHref(entry.id), 'data-tone': tone || null}},
      el('span', {className: 'cert-name', text: entry.cert.label}),
      el('span', {className: 'cert-card', text: entry.card.name || entry.card.id}),
      el('span', {className: 'cert-label', text: certStateText(entry)}),
      CERT_NOTES[entry.state] && el('span', {
        className: 'cert-card',
        text: capitalizeFirst(CERT_NOTES[entry.state]),
      }),
      entry.progress && bar(entry.progress.ratio, tone),
    ),
  );
}

/** Bloc « Titres » : obtenues, puis classées par avancement, puis « Non mesurables ». */
function titlesWindow(data) {
  const entries = rankedCertifications(data);
  const obtained = entries.filter(entry => entry.cert.obtained?.value === true);
  const open = entries.filter(entry => !obtained.includes(entry));
  const group = (title, tip, list) => list.length > 0 && el(
    'div',
    {className: 'cert-group'},
    el('h3', {className: 'group-title'}, title, info(tip)),
    el('ul', {className: 'certs'}, list.map(certCell)),
  );
  return systemWindow(
    {title: 'Titres', className: 'titles-window', order: 4},
    entries.length
      ? [
        group('Obtenues', OBTAINED_TIP, obtained),
        group(
          'De la plus proche à la plus lointaine',
          'Classement automatique sur l’avancement chiffré : part des notions au moins '
            + `« ${certThreshold(data)} » de la certification, sinon de son domaine.`,
          open.filter(entry => entry.progress),
        ),
        group(
          'Non mesurables',
          'Aucune notion du domaine n’est suivie : rien ne permet de les classer.',
          open.filter(entry => !entry.progress),
        ),
      ]
      : el('p', {className: 'empty', text: 'Aucune certification reconnue par les cartes.'}),
  );
}

/**
 * Notions d'une certification rangées par palier de son domaine, paliers vides omis ;
 * celles d'un autre domaine forment le dernier groupe.
 *
 * @param {Object} card carte de la certification
 * @param {string[]} ids notions de la certification
 * @returns {Array<{label: string, notions: string[]}>} un groupe par palier
 */
function certTiers(card, ids) {
  const groups = cardTiers(card).map(tier => ({
    label: tier.label || tier.code,
    notions: tierNotions(tier).filter(id => ids.includes(id)),
  }));
  const placed = groups.flatMap(group => group.notions);
  groups.push({label: 'Autres domaines', notions: ids.filter(id => !placed.includes(id))});
  return groups.filter(group => group.notions.length);
}

/** En-tête d'un palier de prérequis : nom, « n / N » au seuil des certifications, jauge. */
function certTierHead(data, group) {
  const progress = thresholdProgress(data, group.notions, certThreshold(data));
  return [
    el('span', {text: group.label}),
    el('span', {className: 'readout-count', text: `${progress.lit} / ${progress.total}`}),
    bar(progress.total ? progress.lit / progress.total : 0, tierTone(data, group)),
  ];
}

/** Palier de prérequis dépliable : avancement en tête, notions exigées au dépliage. */
function certTierDetails(data, group) {
  return el(
    'details',
    {className: 'cert-tier', attrs: {name: 'cert-tier'}},
    el('summary', {}, icon('chevron'), certTierHead(data, group)),
    el('ul', {className: 'notions'}, group.notions.map(id => notionRow(data, id))),
  );
}

/** Prérequis d'une certification et leur avancement, selon ce que les données mesurent. */
function certPrerequisites(data, entry) {
  const {progress, cert, card} = entry;
  if (!progress) return certGauge(data, entry);
  if (progress.scope === 'certification') {
    return [
      certGauge(data, entry),
      el(
        'div',
        {className: 'cert-tiers'},
        certTiers(card, cert.notions).map(group => certTierDetails(data, group)),
      ),
    ];
  }
  return [
    el('p', {className: 'cert-conditions', text: DOMAIN_SCOPE_NOTE}),
    el(
      'ul',
      {className: 'readout-tiers'},
      cardTiers(card).map(tier => el(
        'li',
        {className: 'readout-tier'},
        certTierHead(data, {label: tier.label || tier.code, notions: tierNotions(tier)}),
      )),
    ),
  ];
}

/** Flèche nav (« prev » ou « next ») vers target, ou sa forme inactive en bout de liste. */
function certArrow(context, target, nav) {
  const className = `button cert-arrow${nav === 'prev' ? ' is-flipped' : ''}`;
  if (!target) {
    return el('span', {className, attrs: {'aria-disabled': 'true'}}, icon('chevron'));
  }
  const label = nav === 'prev' ? 'Certification précédente' : 'Certification suivante';
  return el(
    'a',
    {
      className,
      attrs: {
        href: context.hrefOf(target.id),
        'aria-label': `${label} : ${target.cert.label}`,
        'data-nav': nav,
      },
    },
    icon('chevron'),
  );
}

/** Contenu de la carte au premier plan pour l'entrée de rang index de context.entries. */
function certDialogBody(data, context, index) {
  const {entries} = context;
  const entry = entries[index];
  const link = context.link(entry);
  return systemWindow(
    {
      title: entry.cert.label,
      level: 'h3',
      className: 'cert-dialog-window',
      tone: CERT_STATES[entry.state].tone,
    },
    certStateLine(entry),
    el('h4', {className: 'group-title', text: 'Prérequis'}),
    certPrerequisites(data, entry),
    el(
      'p',
      {className: 'cert-links'},
      el(
        'a',
        {className: 'button', attrs: {href: link.href}},
        el('span', {text: link.label}),
        icon('chevron'),
      ),
      entry.cert.detail && info(entry.cert.detail),
    ),
    el(
      'nav',
      {className: 'cert-nav', attrs: {'aria-label': 'Certifications'}},
      certArrow(context, entries[index - 1], 'prev'),
      el('span', {text: `${index + 1} / ${entries.length}`}),
      certArrow(context, entries[index + 1], 'next'),
      el(
        'a',
        {className: 'button', attrs: {href: context.base, 'data-nav': 'close'}},
        icon('close'),
        'Fermer',
      ),
    ),
  );
}

/**
 * Ouvre, met à jour ou ferme la carte au premier plan selon l'adresse.
 *
 * @param {HTMLElement} root conteneur de la vue, qui porte la carte (certDialog)
 * @param {Object} data objet window.SYSTEME
 * @param {Object} context résultat de statusCertContext ou de sectionCertContext
 * @param {string|undefined} id identifiant de certification de la route, absent ou
 *   inconnu pour fermer
 */
function syncCertDialog(root, data, context, id) {
  const dialog = root.querySelector('.cert-dialog');
  const index = context.entries.findIndex(entry => entry.id === id);
  if (!dialog) return;
  dialog.dataset.base = context.base;
  if (index < 0) {
    if (dialog.open) dialog.close();
    return;
  }
  const used = document.activeElement?.dataset?.nav;
  dialog.setAttribute('aria-label', context.entries[index].cert.label);
  dialog.replaceChildren(certDialogBody(data, context, index));
  if (!dialog.open) dialog.showModal();
  const target = dialog.querySelector(`[data-nav="${used}"]`)
    || dialog.querySelector('[data-nav="close"]');
  target.focus();
}

/** Carte au premier plan, vide : Échap et un clic sur le fond rendent la vue seule. */
function certDialog() {
  const dialog = el('dialog', {className: 'cert-dialog'});
  const leave = () => {
    if (parseRoute(location.hash).cert) location.hash = dialog.dataset.base;
  };
  dialog.addEventListener('close', leave);
  dialog.addEventListener('click', event => {
    if (event.target === dialog) leave();
  });
  dialog.addEventListener('keydown', event => {
    const nav = {ArrowLeft: 'prev', ArrowRight: 'next'}[event.key];
    if (nav) dialog.querySelector(`[data-nav="${nav}"]`)?.click();
  });
  return dialog;
}
