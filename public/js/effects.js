'use strict';

/*
 * Maquette « Système » : insigne et éclairs de rang, dépassement du niveau maximal.
 *
 * rankBadge crée l'insigne et l'électrise ; chargeWindow électrise les filets d'une
 * fenêtre qui porte un rang. Les éclairs se tracent dans un calque SVG décoratif puis
 * s'éteignent : nombre, taille et fréquence montent du rang D au rang S, le rang E n'en
 * a aucun. Un courant fait le tour de l'insigne et du cadre (effects.css) : chaque salve
 * le coupe, et il tient de plus en plus longtemps de D à S. Au rang Nation, la puissance
 * est sous contrôle : il est continu, et des éclairs rapides le suivent sans s'éteindre.
 * crownBadge couronne l'insigne d'un domaine aux notions toutes au moins rouges ;
 * breakLimit rompt le cadre d'une fenêtre de niveau au-delà de sa cible. Les calques
 * passent sous le texte et ne captent aucun clic ; rien ne se trace sous
 * prefers-reduced-motion ni hors de la page. Chargé après model.js et dom.js.
 */

/*
 * Puissance par rang : éclairs par salve, pause entre salves (ms), portée et trait (px) ;
 * stable : part du temps où le courant tient entre deux salves. La pause se resserre
 * jusqu'à la durée d'un éclair (FLASH_MS) : au rang S, les salves s'enchaînent presque
 * sans répit, à l'approche des éclairs continus du rang Nation.
 */
const RANK_POWER = {
  D: {bolts: 1, pause: 1500, reach: 13, width: 1.2, stable: 0.15},
  C: {bolts: 1, pause: 1100, reach: 16, width: 1.3, stable: 0.3},
  B: {bolts: 2, pause: 800, reach: 19, width: 1.5, stable: 0.5},
  A: {bolts: 3, pause: 550, reach: 23, width: 1.7, stable: 0.7},
  S: {bolts: 4, pause: 340, reach: 30, width: 2.1, stable: 0.85},
};
/* Écart (px) entre un insigne et son hexagone de courant. */
const ORBIT_GAP = 5;
/* Éclairs continus du rang Nation : brisures, écart au contour et trait (px), rythme (ms). */
const RIDER = {steps: 12, drift: 5, width: 1.6, shakeMs: 70};
const BOLT_STEPS = 6;
const FLASH_MS = 260;
/* Biais d'un éclair de filet (radians) : assez pour se détacher du filet qu'il quitte. */
const RAIL_TILT = [0.3, 0.7];
const RAIL_STRETCH = 2.6;
const HEXAGON_RING = '50,2 96,26 96,74 50,98 4,74 4,26';
/* Cadre rompu : largeur (px) de l'ouverture laissée par un éclat sur chaque côté. */
const FRACTURE_GAP = 44;

/** Nombre aléatoire entre min et max. */
function between(min, max) {
  return min + Math.random() * (max - min);
}

/**
 * Tracé brisé d'un éclair.
 *
 * @param {number} x abscisse de départ
 * @param {number} y ordonnée de départ
 * @param {number} angle direction en radians
 * @param {number} length longueur totale
 * @returns {string} attribut points d'un <polyline>
 */
function boltPoints(x, y, angle, length) {
  const step = length / BOLT_STEPS;
  const points = [[x, y]];
  for (let index = 1; index <= BOLT_STEPS; index += 1) {
    const drift = between(-0.45, 0.45) * step;
    points.push([
      x + Math.cos(angle) * step * index - Math.sin(angle) * drift,
      y + Math.sin(angle) * step * index + Math.cos(angle) * drift,
    ]);
  }
  return points.map(point => point.map(value => value.toFixed(1)).join(',')).join(' ');
}

/** Départ, direction et longueur d'un éclair autour d'un insigne de width × height. */
function badgeBolt(width, height, power) {
  const angle = between(0, Math.PI * 2);
  const radius = Math.min(width, height) / 2;
  return [
    width / 2 + Math.cos(angle) * radius,
    height / 2 + Math.sin(angle) * radius,
    angle + between(-0.5, 0.5),
    power.reach,
  ];
}

/** Départ, direction et longueur d'un éclair qui part en biais d'un filet de fenêtre. */
function railBolt(width, height, power) {
  const along = Math.random() < 0.5 ? 0 : Math.PI;
  const side = Math.random() < 0.5 ? 1 : -1;
  return [
    between(0.08, 0.92) * width,
    Math.random() < 0.5 ? 0 : height,
    along + side * between(...RAIL_TILT),
    power.reach * RAIL_STRETCH,
  ];
}

/** Calque SVG décoratif de classe className, étiré sur son hôte, qui contient shapes. */
function overlay(className, ...shapes) {
  return svgEl(
    'svg',
    {
      class: className,
      viewBox: '0 0 100 100',
      preserveAspectRatio: 'none',
      'aria-hidden': 'true',
    },
    ...shapes,
  );
}

/**
 * Impulsion de courant : sa longueur vaut la part stable de length, sur un pas de period.
 *
 * @param {string} tag « polygon » ou « rect »
 * @param {Object} attrs attributs de la forme parcourue
 * @param {number} stable part du temps où le courant tient (0 à 1)
 * @param {number[]} dash [length, period] à pleine stabilité
 * @returns {SVGElement}
 */
function flowPulse(tag, attrs, stable, [length, period]) {
  const pulse = svgEl(tag, {class: 'flow-pulse', ...attrs});
  pulse.style.strokeDasharray = `${length * stable} ${period - length * stable}`;
  return pulse;
}

/** Courant autour d'un insigne : hexagone continu et ses impulsions (périmètre 100). */
function hexFlow(stable) {
  const ring = {points: HEXAGON_RING};
  return overlay(
    'flow flow-hex',
    svgEl('polygon', {class: 'flow-line', ...ring}),
    flowPulse('polygon', {...ring, pathLength: 100}, stable, [16, 50]),
  );
}

/** Courant autour d'une fenêtre : impulsions qui longent le cadre (longueurs en px). */
function frameFlow(stable) {
  return overlay(
    'flow flow-frame',
    flowPulse('rect', {width: 100, height: 100}, stable, [46, 76]),
  );
}

/** Sommets (px) du cadre d'une fenêtre de width × height, dans le sens du courant. */
function frameOutline(width, height) {
  return [[0, 0], [width, 0], [width, height], [0, height]];
}

/** Sommets (px) de l'hexagone de courant d'un insigne de width × height, même sens. */
function hexOutline(width, height) {
  return HEXAGON_RING.split(' ').map(point => {
    const [x, y] = point.split(',').map(Number);
    return [
      (x / 100) * (width + 2 * ORBIT_GAP) - ORBIT_GAP,
      (y / 100) * (height + 2 * ORBIT_GAP) - ORBIT_GAP,
    ];
  });
}

/**
 * Parcours fermé qui relie les sommets vertices.
 *
 * @param {number[][]} vertices sommets [x, y], au moins deux
 * @returns {{total: number, at: function(number): number[]}} total : périmètre ; at : point
 *   [x, y] et normale unitaire [nx, ny] à la distance donnée, ramenée dans le périmètre
 */
function closedPath(vertices) {
  const sides = vertices.map(([x, y], index) => {
    const [nextX, nextY] = vertices[(index + 1) % vertices.length];
    return {x, y, dx: nextX - x, dy: nextY - y, length: Math.hypot(nextX - x, nextY - y)};
  });
  const total = sides.reduce((sum, side) => sum + side.length, 0);
  return {
    total,
    at(distance) {
      let rest = ((distance % total) + total) % total;
      const side = sides.find(entry => {
        if (rest <= entry.length) return true;
        rest -= entry.length;
        return false;
      }) || sides[0];
      const share = side.length ? rest / side.length : 0;
      const unit = side.length || 1;
      return [
        side.x + side.dx * share,
        side.y + side.dy * share,
        side.dy / unit,
        -side.dx / unit,
      ];
    },
  };
}

/*
 * Par tracé : éclair des rangs D à S, courant, puis rang Nation : contour, nombre et
 * allure (longueur en px, vitesse en px/s) des éclairs continus, bien plus rapides que
 * les impulsions du courant.
 */
const CHARGES = {
  badge: {
    bolt: badgeBolt,
    flow: hexFlow,
    nation: {
      outline: hexOutline,
      count: 2,
      pace: perimeter => ({length: perimeter * 0.3, speed: perimeter / 0.55}),
    },
  },
  rails: {
    bolt: railBolt,
    flow: frameFlow,
    nation: {outline: frameOutline, count: 3, pace: () => ({length: 150, speed: 1100})},
  },
};

/**
 * Trace dans layer des éclairs continus, répartis sur le tour de host, tant qu'il est
 * dans la page.
 *
 * @param {HTMLElement} host élément dont les éclairs suivent le contour
 * @param {SVGElement} layer calque des éclairs
 * @param {{outline: function, count: number, pace: function}} ride entrée nation de
 *   CHARGES
 */
function rideLoop(host, layer, ride) {
  const {count} = ride;
  const lines = Array.from({length: count}, () => (
    svgEl('polyline', {'stroke-width': RIDER.width})
  ));
  let drifts = [];
  let shaken = -Infinity;
  const frame = now => {
    if (!host.isConnected) return;
    const {width, height} = host.getBoundingClientRect();
    const path = closedPath(ride.outline(width, height));
    const {length, speed} = ride.pace(path.total);
    const head = (now / 1000) * speed;
    if (now - shaken > RIDER.shakeMs) {
      drifts = lines.map(() => (
        Array.from({length: RIDER.steps + 1}, () => between(-RIDER.drift, RIDER.drift))
      ));
      shaken = now;
    }
    lines.forEach((line, turn) => {
      const lead = head + (turn / count) * path.total;
      line.setAttribute('points', drifts[turn].map((drift, index) => {
        const [x, y, normalX, normalY] = path.at(lead - length * (1 - index / RIDER.steps));
        return `${(x + normalX * drift).toFixed(1)},${(y + normalY * drift).toFixed(1)}`;
      }).join(' '));
    });
    requestAnimationFrame(frame);
  };
  layer.append(...lines);
  requestAnimationFrame(frame);
}

/**
 * Trace des salves d'éclairs dans layer tant que host est dans la page.
 *
 * @param {Element} host élément dont la sortie de la page arrête les salves
 * @param {SVGElement} layer calque vidé à chaque salve
 * @param {{bolts: number, pause: number, width: number}} power puissance de RANK_POWER
 * @param {function(): Array} aim départ, direction et longueur d'un éclair (boltPoints)
 * @param {function(number)} [onStrike] reçoit la pause (ms) qui suit chaque salve
 */
function strikeLoop(host, layer, power, aim, onStrike) {
  const strike = () => {
    const pause = power.pause * between(0.6, 1.4);
    if (!host.isConnected) return;
    if (!document.hidden) {
      const bolts = Array.from({length: power.bolts}, () => svgEl('polyline', {
        points: boltPoints(...aim()),
        'stroke-width': power.width,
      }));
      layer.replaceChildren(...bolts);
      setTimeout(() => layer.replaceChildren(), FLASH_MS);
      onStrike?.(pause);
    }
    setTimeout(strike, pause);
  };
  setTimeout(strike, between(200, power.pause));
}

/**
 * Électrise host selon le rang rank.
 *
 * @param {HTMLElement} host élément positionné (insigne ou fenêtre)
 * @param {string|null} rank rang de RANK_LADDER ; E ou absent : aucun effet
 * @param {string} shape clé de CHARGES
 */
function electrify(host, rank, shape) {
  const charge = CHARGES[shape];
  const nation = rank === 'Nation';
  const power = RANK_POWER[rank];
  const stable = nation ? 1 : power?.stable || 0;
  const flow = stable ? charge.flow(stable) : null;
  host.dataset.charge = rank || 'none';
  if (flow) {
    flow.style.setProperty('--stable', String(stable));
    host.append(flow);
  }
  if ((!nation && !power) || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const layer = svgEl('svg', {class: 'sparks', 'aria-hidden': 'true'});
  host.append(layer);
  if (nation) {
    layer.classList.add('is-rider');
    rideLoop(host, layer, charge.nation);
    return;
  }
  const aim = () => {
    const {width, height} = host.getBoundingClientRect();
    return charge.bolt(width, height, power);
  };
  strikeLoop(host, layer, power, aim, pause => {
    flow.classList.add('is-cut');
    setTimeout(() => flow.classList.remove('is-cut'), pause * (1 - stable));
  });
}

/** Insigne hexagonal du rang rank, électrisé ; un tiret pour « aucun rang ». */
function rankBadge(rank) {
  const badge = el(
    'span',
    {className: 'rank', attrs: {'data-rank': rank || 'none', 'aria-hidden': 'true'}},
    el('span', {text: rank ? rank.charAt(0) : '–'}),
  );
  electrify(badge, rank, 'badge');
  return badge;
}

/** Électrise les filets de la fenêtre frame, qui porte le rang rank. */
function chargeWindow(frame, rank) {
  electrify(frame, rank, 'rails');
}

/** Couronne l'insigne badge d'un domaine dont toutes les notions sont au moins rouges. */
function crownBadge(badge) {
  badge.append(overlay(
    'badge-crown',
    svgEl('polygon', {points: HEXAGON_RING, pathLength: 100}),
  ));
}

/**
 * Limite d'une jauge dépassée : la valeur text se brouille en « ??? ».
 *
 * @param {string} text limite d'origine, déjà mise en forme
 * @returns {HTMLElement}
 */
function brokenLimit(text) {
  return el(
    'span',
    {
      className: 'over-limit',
      attrs: {role: 'img', 'aria-label': `limite de ${text} dépassée`},
    },
    el('span', {className: 'over-limit-was', text, attrs: {'aria-hidden': 'true'}}),
    el('span', {className: 'over-limit-now', text: '???', attrs: {'aria-hidden': 'true'}}),
  );
}

/**
 * Tracés du cadre rompu d'une fenêtre : le contour, ouvert sur chaque côté par un éclat
 * déplacé, et une fissure qui part de chaque ouverture vers l'intérieur.
 *
 * @param {number} width largeur de la fenêtre en px
 * @param {number} height hauteur de la fenêtre en px
 * @returns {{frame: string, cracks: string}} attributs d de deux <path>
 */
function fracturePaths(width, height) {
  const gap = FRACTURE_GAP;
  const top = Math.round(width * 0.32);
  const right = Math.round(height * 0.7);
  const bottom = Math.round(width * 0.64);
  const left = Math.round(height * 0.28);
  return {
    frame: `M0 0H${top}M${top + 4} -7l36 12M${top + gap} 0H${width}V${right}`
      + `M${width + 6} ${right + 4}l-10 32M${width} ${right + gap}V${height}H${bottom}`
      + `M${bottom - 4} ${height + 7}l-36 -12M${bottom - gap} ${height}H0V${left}`
      + `M-6 ${left - 4}l10 -32M0 ${left - gap}V0`,
    cracks: `M${top + 22} 0l8 18l-10 12l9 20M${width} ${right + 20}l-20 6l8 12l-24 10`
      + `M${bottom - 22} ${height}l-6 -20l10 -12l-6 -16M0 ${left - 20}l22 -6l-8 -12l24 -9`,
  };
}

/** Rompt le cadre de la fenêtre frame, dont le niveau dépasse sa cible. */
function breakLimit(frame) {
  const outline = svgEl('path', {class: 'fracture-frame'});
  const cracks = svgEl('path', {class: 'fracture-cracks'});
  frame.dataset.over = 'true';
  frame.append(svgEl('svg', {class: 'fracture', 'aria-hidden': 'true'}, outline, cracks));
  new ResizeObserver(() => {
    const paths = fracturePaths(frame.clientWidth, frame.clientHeight);
    outline.setAttribute('d', paths.frame);
    cracks.setAttribute('d', paths.cracks);
  }).observe(frame);
}
