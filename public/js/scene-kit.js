'use strict';

/*
 * Réseau des notions : matière première de la scène three.js, sans état.
 *
 * Couleurs lues dans base.css, textures dessinées sur canevas (nœuds par rendu d'état et
 * par niveau de rareté, halos, signal, motifs de trait) et décor (champ d'étoiles, halos
 * d'amas, socle holographique). Chargé après network.js et avant scene.js.
 */

const TEXTURE_SIZE = 128;
const STAR_COUNT = 900;
const PLATFORM_RINGS = [0.45, 0.8, 1.15, 1.5];
const PALETTE_TOKENS = [
  '--flux',
  '--rail',
  '--warn',
  '--rarity-1',
  '--rarity-2',
  '--rarity-3',
  '--rarity-4',
  '--rarity-5',
  '--rarity-6',
  '--rarity-7',
  '--void',
  '--text-faint',
  '--kind-transfer',
  '--kind-prerequisite',
  '--kind-instance',
  '--kind-complement',
  '--kind-analog',
];

/**
 * Couleurs de la charte lues dans base.css ; un jeton absent est une erreur.
 *
 * @returns {Object<string, string>} clé : nom du jeton (« --flux »...)
 */
function cssPalette() {
  const style = getComputedStyle(document.documentElement);
  const palette = {};
  for (const token of PALETTE_TOKENS) {
    const value = style.getPropertyValue(token).trim();
    if (!value) throw new Error(`Jeton CSS ${token} absent : css/base.css n’est pas chargé.`);
    palette[token] = value;
  }
  return palette;
}

/** Couleur CSS color avec l'opacité alpha, en rgba(). */
function withAlpha(color, alpha) {
  const {r, g, b} = new THREE.Color(color);
  const channels = [r, g, b].map(value => Math.round(value * 255));
  return `rgba(${channels.join(', ')}, ${alpha})`;
}

/**
 * Texture dessinée par draw sur un canevas de width × height pixels.
 *
 * @param {function(CanvasRenderingContext2D, number, number)} draw reçoit le contexte,
 *   la largeur et la hauteur
 * @param {number} [width] largeur en pixels
 * @param {number} [height] hauteur en pixels
 * @returns {THREE.CanvasTexture}
 */
function canvasTexture(draw, width = TEXTURE_SIZE, height = TEXTURE_SIZE) {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const context = canvas.getContext('2d');
  if (!context) throw new Error('Le canevas 2D est indisponible pour dessiner les nœuds.');
  draw(context, width, height);
  return new THREE.CanvasTexture(canvas);
}

/** Cercle de rayon radius × size / 2, rempli de fill puis tracé de stroke. */
function ring(context, size, radius, stroke, fill, dash = [], width = 0.07) {
  context.beginPath();
  context.arc(size / 2, size / 2, (radius * size) / 2, 0, 2 * Math.PI);
  if (fill) {
    context.fillStyle = fill;
    context.fill();
  }
  context.setLineDash(dash);
  context.lineWidth = size * width;
  context.strokeStyle = stroke;
  context.stroke();
}

/** Texture carrée d'un dégradé radial, stops : paires [position de 0 à 1, couleur CSS]. */
function glowTexture(stops, side = TEXTURE_SIZE) {
  return canvasTexture((context, size) => {
    const half = size / 2;
    const glow = context.createRadialGradient(half, half, 0, half, half, half);
    for (const [offset, color] of stops) glow.addColorStop(offset, color);
    context.fillStyle = glow;
    context.fillRect(0, 0, size, size);
  }, side, side);
}

/** Losange lumineux d'une notion acquise : halo et cœur de couleur color. */
function diamondTexture(palette, color) {
  return canvasTexture((context, size) => {
    const half = size / 2;
    const glow = context.createRadialGradient(half, half, 0, half, half, half);
    glow.addColorStop(0, withAlpha(color, 0.75));
    glow.addColorStop(1, withAlpha(color, 0));
    context.fillStyle = glow;
    context.fillRect(0, 0, size, size);
    const reach = size * 0.23;
    context.beginPath();
    context.moveTo(half, half - reach);
    context.lineTo(half + reach, half);
    context.lineTo(half, half + reach);
    context.lineTo(half - reach, half);
    context.closePath();
    context.fillStyle = color;
    context.fill();
    context.lineWidth = size * 0.03;
    context.strokeStyle = palette['--rail'];
    context.stroke();
  });
}

/**
 * Textures des nœuds, du halo et du signal ; halo en blanc. Les rendus « high » et
 * « low » ont une texture par niveau de rareté, créée à la demande par colored().
 */
function spriteTextures(palette) {
  const dots = size => [size * 0.09, size * 0.08];
  const hollow = (color, dash, width) => canvasTexture((context, size) => {
    ring(context, size, 0.8, color, palette['--void'], dash(size), width);
  });
  const byLevel = new Map();
  const colored = (look, level) => {
    const key = `${look}:${level}`;
    if (byLevel.has(key)) return byLevel.get(key);
    const color = palette[`--rarity-${level}`] || palette['--flux'];
    const texture = look === 'high'
      ? diamondTexture(palette, color)
      : glowTexture([
        [0, palette['--rail']],
        [0.4, color],
        [0.5, withAlpha(color, 0.4)],
        [1, withAlpha(color, 0)],
      ]);
    byLevel.set(key, texture);
    return texture;
  };
  return {
    colored,
    declared: hollow(palette['--rail'], dots, 0.08),
    unmet: hollow(palette['--text-faint'], () => [], 0.1),
    unknown: hollow(palette['--warn'], dots, 0.08),
    halo: canvasTexture((context, size) => ring(context, size, 0.86, '#ffffff', null)),
    pulse: glowTexture([
      [0, '#ffffff'],
      [0.3, withAlpha(palette['--rail'], 0.9)],
      [1, withAlpha(palette['--rail'], 0)],
    ]),
  };
}

/** Motifs des statuts en alphaMap : tirets et points blancs sur noir, répétés en u. */
function dashTextures() {
  const pattern = share => {
    const texture = canvasTexture((context, width, height) => {
      context.fillStyle = '#000000';
      context.fillRect(0, 0, width, height);
      context.fillStyle = '#ffffff';
      context.fillRect(0, 0, width * share, height);
    }, 64, 4);
    texture.wrapS = THREE.RepeatWrapping;
    return texture;
  };
  return {dash: pattern(0.62), dot: pattern(0.32)};
}

/** Générateur pseudo-aléatoire déterministe (suite congruente) : nombres de 0 à 1. */
function seededRandom(seed) {
  let value = seed;
  return () => {
    value = (value * 1664525 + 1013904223) % 4294967296;
    return value / 4294967296;
  };
}

/** Champ d'étoiles fixe autour du réseau, entre 2 et 4 fois son rayon radius. */
function buildStars(radius, color) {
  const random = seededRandom(42);
  const points = [];
  for (let index = 0; index < STAR_COUNT; index += 1) {
    const [x, y, z] = fibonacciPoint(index, STAR_COUNT);
    const reach = radius * (2 + 2 * random());
    points.push(x * reach, y * reach, z * reach);
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(points, 3));
  return new THREE.Points(geometry, new THREE.PointsMaterial({
    color,
    size: 1.6,
    sizeAttenuation: false,
    transparent: true,
    opacity: 0.55,
    depthWrite: false,
    fog: false,
  }));
}

/** Halo lumineux de chaque amas de plusieurs notions, derrière ses nœuds. */
function buildClusterHalos(layout, texture) {
  const clusters = [...layout.centers.values()].filter(cluster => cluster.radius > 0);
  return clusters.map(({center, radius}) => {
    const halo = new THREE.Sprite(new THREE.SpriteMaterial({
      map: texture,
      transparent: true,
      opacity: 0.9,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      fog: false,
    }));
    halo.position.set(...center);
    halo.scale.setScalar(radius * 5.5);
    halo.renderOrder = -1;
    return halo;
  });
}

/** Anneaux concentriques du socle holographique, sous le réseau de rayon radius. */
function buildPlatform(radius, color) {
  const platform = new THREE.Group();
  for (const share of PLATFORM_RINGS) {
    const points = [];
    for (let step = 0; step <= 128; step += 1) {
      const [x, z] = polar(radius * share, (step / 128) * 360);
      points.push(new THREE.Vector3(x, 0, z));
    }
    platform.add(new THREE.Line(
      new THREE.BufferGeometry().setFromPoints(points),
      new THREE.LineBasicMaterial({
        color,
        transparent: true,
        opacity: 0.22,
        depthWrite: false,
      }),
    ));
  }
  platform.position.y = -radius * 0.42;
  return platform;
}
