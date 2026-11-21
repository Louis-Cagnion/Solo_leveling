'use strict';

/*
 * Maquette « Système » : ondes de courant des secteurs de la roue.
 *
 * Dans chaque secteur de rang D ou plus, une onde part du centre vers le bord : un front
 * net, suivi d'une traîne de courant qui s'estompe derrière lui. Elle revient d'autant
 * plus souvent que le rang est haut ; au rang Nation, la puissance est sous contrôle et
 * un train régulier d'ondes se suit. Le rang E et les secteurs sans rang restent fixes.
 * Un domaine dont toutes les notions sont au moins rouges est couronné : un courant
 * rouge fait le tour de son insigne de rang et le relie à ses voisins couronnés.
 * Les calques sont décoratifs, rognés au secteur, et ne captent aucun clic ; rien ne
 * bouge sous prefers-reduced-motion (wheel-fx.css). Chargé après dom.js et model.js.
 */

/* Période (ms) de l'onde d'un secteur par rang ; en Nation, NATION_WAVES ondes se suivent. */
const WAVE_MS = {D: 4160, C: 3680, B: 3200, A: 2720, S: 1600, Nation: 2400};
const NATION_WAVES = 3;
/* Profondeur de la traîne derrière le front, en unités de la roue. */
const WAVE_TRAIL = 110;

/**
 * Pose les ondes du secteur sector, s'il porte un rang D ou plus.
 *
 * @param {SVGAElement} sector secteur de buildSector (data-start, data-end, data-rank)
 * @param {number} index rang du secteur dans la roue, pour des identifiants uniques
 */
function waveSector(sector, index) {
  const start = Number(sector.dataset.start);
  const end = Number(sector.dataset.end);
  const nation = sector.dataset.rank === 'Nation';
  const period = WAVE_MS[sector.dataset.rank];
  const outer = WHEEL.sectorOuter;
  if (!period) return;
  const waves = Array.from({length: nation ? NATION_WAVES : 1}, (unused, turn) => {
    const wave = svgEl(
      'g',
      {class: 'sector-wave'},
      svgEl('path', {
        class: 'wave-trail',
        d: ringPath(outer - WAVE_TRAIL, outer, start, end),
        fill: `url(#wave-trail-${index})`,
      }),
      svgEl('path', {class: 'wave-front', d: ringPath(outer, outer, start, end)}),
    );
    wave.style.setProperty('--period', `${Math.round(period)}ms`);
    wave.style.setProperty('--delay', `${Math.round((-period * turn) / NATION_WAVES)}ms`);
    return wave;
  });
  sector.append(svgEl(
    'g',
    {class: 'sector-waves', 'aria-hidden': 'true', 'clip-path': `url(#wave-clip-${index})`},
    svgEl(
      'clipPath',
      {id: `wave-clip-${index}`},
      svgEl('path', {d: ringPath(WHEEL.sectorInner, outer, start, end)}),
    ),
    svgEl(
      'radialGradient',
      {id: `wave-trail-${index}`, gradientUnits: 'userSpaceOnUse', cx: 0, cy: 0, r: outer},
      svgEl('stop', {class: 'wave-stop-far', offset: (outer - WAVE_TRAIL) / outer}),
      svgEl('stop', {class: 'wave-stop-near', offset: 1}),
    ),
    waves,
  ));
}

/**
 * Suites de secteurs voisins couronnés, la roue étant fermée sur elle-même.
 *
 * crownRuns([true, false, true, true]) -> [[2, 4]]
 *
 * @param {boolean[]} crowned un drapeau par secteur, dans l'ordre de la roue
 * @returns {number[][]} [premier secteur, longueur] de chaque suite ; une seule suite de
 *   la longueur de crowned si tous le sont
 */
function crownRuns(crowned) {
  const count = crowned.length;
  if (crowned.every(Boolean)) return count ? [[0, count]] : [];
  return crowned.flatMap((flag, first) => {
    if (!flag || crowned[(first - 1 + count) % count]) return [];
    let length = 1;
    while (crowned[(first + length) % count]) length += 1;
    return [[first, length]];
  });
}

/**
 * Couronne des domaines dont toutes les notions sont au moins rouges, portée par leurs
 * insignes de rang : un hexagone de courant autour de chacun, et un arc de courant
 * d'insigne à insigne entre domaines voisins couronnés. Un domaine isolé n'a que son
 * hexagone ; la roue entière couronnée ferme l'anneau.
 *
 * @param {SVGSVGElement} svg roue de renderWheel
 */
function crownWheel(svg) {
  const sectors = [...svg.querySelectorAll('.sector')];
  const slot = 360 / sectors.length;
  const radius = WHEEL.rankRadius;
  const runs = crownRuns(sectors.map(sector => sector.dataset.crowned === 'yes'));
  if (!runs.length) return;
  const arcs = runs.filter(([, length]) => length > 1).flatMap(([first, length]) => {
    const from = -90 + (first + 0.5) * slot;
    const [tag, attrs] = length === sectors.length
      ? ['circle', {r: radius}]
      : ['path', {d: ringPath(radius, radius, from, from + (length - 1) * slot)}];
    return ['crown-line', 'crown-pulse'].map(name => svgEl(tag, {class: name, ...attrs}));
  });
  sectors[0].before(svgEl('g', {class: 'wheel-crown', 'aria-hidden': 'true'}, arcs));
  for (const badge of svg.querySelectorAll('[data-crowned="yes"] .sector-rank')) {
    badge.append(svgEl('polygon', {
      class: 'crown-hex',
      points: HEXAGON,
      pathLength: 100,
      'aria-hidden': 'true',
    }));
  }
}

/** Anime la roue svg, secteurs déjà construits par renderWheel. */
function animateWheel(svg) {
  svg.querySelectorAll('.sector').forEach(waveSector);
  crownWheel(svg);
}
