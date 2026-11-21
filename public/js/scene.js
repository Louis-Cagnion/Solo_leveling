'use strict';

/*
 * Réseau des notions : scène three.js r147 (vendor/), rendu, survol
 * et sélection. Textures et décor : scene-kit.js, chargé avant ce script.
 *
 * Nœuds en sprites face à la caméra, comme les signes d'état de la roue : losange
 * lumineux ou disque à la couleur de rareté de l'état, cercle pointillé (déclarée), petit
 * cercle (non rencontrée), cercle pointillé orange (absente du suivi). Liens en tubes :
 * la couleur dit le type, l'épaisseur et le trait le statut, une flèche le sens ; les
 * branches d'un arbre sont presque droites, les autres liens en arc.
 * Un signal parcourt chaque transfert. Décor : champ d'étoiles, halo par amas et anneaux
 * d'un socle holographique. Sous prefers-reduced-motion: reduce, ni rotation automatique,
 * ni inertie, ni signal : rendu à la demande. La boucle s'arrête quand la page est
 * masquée. Étiquettes en DOM, posées sur la projection.
 */

/* Rendu des nœuds : échelle du sprite et rayon visible, par rendu d'état. */
const NODE_LOOKS = {
  high: {scale: 4.6, radius: 1},
  low: {scale: 3.4, radius: 0.85},
  declared: {scale: 2.8, radius: 1.05},
  unmet: {scale: 2.2, radius: 0.9},
  unknown: {scale: 2.8, radius: 1.05},
};
const PICK_RADIUS = 0.8;
const MIN_CLUSTER_LABEL = 3;
const FRAME_FILL = 0.74;
/* Marge du cadrage de layout.span : rayon d'un nœud. */
const NODE_ROOM = 3;
/* Délai avant que la rotation reprenne après un déplacement ou un zoom. */
const SPIN_RESUME_MS = 500;
const TREE_BEND = 0.05;
const CROSS_BEND = 0.22;
const CROSS_DIM = 0.4;
const GLOWING_LOOKS = ['high', 'low'];
const NOTHING = {node: null, link: null};
const round = value => Math.round(value * 100) / 100;
const DASH_PERIODS = {dash: 2.4, dot: 1.3};
const DIM_NODE = 0.2;
const DIM_LINK = 0.08;
const PULSE_MS = 2400;
const CLICK_SLOP = 5;
const AUTO_ROTATE_SPEED = 0.5;
const motionQuery = matchMedia('(prefers-reduced-motion: reduce)');

/** Clé de NODE_LOOKS et de texture d'un nœud : son rendu d'état, sinon unknown. */
function nodeLook(node) {
  return NODE_LOOKS[node.group] ? node.group : 'unknown';
}

/**
 * Demi-largeur (px), autour du centre de stage, que laissent libre les panneaux posés
 * sur lui ; toute sa demi-largeur si aucun ne le recouvre.
 */
function clearHalfWidth(stage) {
  const box = stage.getBoundingClientRect();
  const middle = (box.left + box.right) / 2;
  let half = box.width / 2;
  for (const panel of stage.parentElement.querySelectorAll('.panel')) {
    const rect = panel.getBoundingClientRect();
    if (rect.bottom <= box.top || rect.top >= box.bottom) continue;
    const gap = rect.right <= middle ? middle - rect.right : rect.left - middle;
    if (gap > 0) half = Math.min(half, gap);
  }
  return half;
}

/**
 * Pointe de flèche posée au bout de curve, juste avant le bord du nœud cible.
 *
 * @param {THREE.Curve} curve courbe du lien
 * @param {number} radius rayon du tube
 * @param {number} gap rayon visible du nœud cible
 * @param {THREE.Material} material matière de la pointe
 * @returns {THREE.Mesh}
 */
function arrowHead(curve, radius, gap, material) {
  const height = Math.max(1.2, radius * 6);
  const tipAt = Math.max(0, 1 - gap / curve.getLength());
  const tangent = curve.getTangentAt(tipAt);
  const cone = new THREE.Mesh(
    new THREE.ConeGeometry(Math.max(0.45, radius * 2.6), height, 12),
    material,
  );
  cone.position.copy(curve.getPointAt(tipAt)).addScaledVector(tangent, -height / 2);
  cone.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), tangent);
  return cone;
}

/**
 * Objets d'un lien : tube courbe (arc alterné vers le haut ou le bas), pointe pour un
 * type orienté, et tube invisible plus large qui reçoit le clic.
 *
 * @param {Object} context {data, layout, network, dashes, palette}
 * @param {Object} link lien de buildNetwork
 * @returns {Object|null} {link, group, pick, curve, materials, opacity}, null pour une
 *   auto-relation, sans longueur à tracer
 */
function buildLink(context, link) {
  const kind = kindInfo(context.data, link.kind);
  const status = statusStyle(link.status);
  const from = new THREE.Vector3(...context.layout.positions.get(link.source));
  const to = new THREE.Vector3(...context.layout.positions.get(link.target));
  const length = from.distanceTo(to);
  if (length < 1e-6) return null;
  const control = from.clone().add(to).multiplyScalar(0.5);
  const branch = context.layout.treeLinks.has(link.index);
  const bend = branch ? TREE_BEND : CROSS_BEND;
  /* Dans un arbre, les liens hors branches s'effacent pour laisser lire la structure. */
  const opacity = status.opacity * (branch || !context.layout.root ? 1 : CROSS_DIM);
  control.y += length * bend * (link.index % 2 ? 1 : -1);
  const curve = new THREE.QuadraticBezierCurve3(from, control, to);
  const material = () => new THREE.MeshBasicMaterial({
    color: context.palette[kind.style.token],
    transparent: true,
    opacity,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
  });
  const tube = material();
  if (status.pattern !== 'solid') {
    tube.alphaMap = context.dashes[status.pattern].clone();
    tube.alphaMap.repeat.set(curve.getLength() / DASH_PERIODS[status.pattern], 1);
    tube.alphaMap.needsUpdate = true;
  }
  const mark = material();
  const group = new THREE.Group();
  group.add(new THREE.Mesh(new THREE.TubeGeometry(curve, 48, status.radius, 8), tube));
  const target = context.network.byId.get(link.target);
  const gap = NODE_LOOKS[nodeLook(target)].radius + 0.2;
  if (kind.directed) group.add(arrowHead(curve, status.radius, gap, mark));
  const pick = new THREE.Mesh(
    new THREE.TubeGeometry(curve, 16, PICK_RADIUS, 5),
    new THREE.MeshBasicMaterial({visible: false}),
  );
  pick.userData.link = link.index;
  group.add(pick);
  return {link, group, pick, curve, materials: [tube, mark], opacity};
}

/** Sprites des nœuds de network posés selon layout dans scene ; renvoie {node, sprite}. */
function buildNodes(scene, network, layout, textures) {
  return network.nodes.map(node => {
    const look = nodeLook(node);
    const sprite = new THREE.Sprite(new THREE.SpriteMaterial({
      map: textures[look] || textures.colored(look, node.level),
      transparent: true,
      depthWrite: false,
      blending: GLOWING_LOOKS.includes(look)
        ? THREE.AdditiveBlending
        : THREE.NormalBlending,
    }));
    sprite.position.set(...layout.positions.get(node.id));
    sprite.scale.setScalar(NODE_LOOKS[look].scale);
    sprite.userData.radius = NODE_LOOKS[look].radius;
    sprite.userData.id = node.id;
    scene.add(sprite);
    return {node, sprite};
  });
}

/** Sprite toujours dessiné par-dessus (halo, signal), masqué jusqu'à son placement. */
function overlaySprite(scene, texture, color, onTop) {
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({
    map: texture,
    color,
    transparent: true,
    depthTest: !onTop,
    depthWrite: false,
  }));
  sprite.renderOrder = onTop ? 10 : 0;
  sprite.visible = false;
  scene.add(sprite);
  return sprite;
}

/** Vrai si les rectangles a et b, élargis de gap pixels, se recouvrent. */
function overlaps(a, b, gap = 4) {
  return a.left < b.right + gap && b.left < a.right + gap
    && a.top < b.bottom + gap && b.top < a.bottom + gap;
}

/** Rectangle écran de l'étiquette en (x, y), taille mesurée une fois et gardée. */
function labelRect(label, x, y) {
  const {element} = label;
  if (!label.size && element.offsetWidth) {
    label.size = {width: element.offsetWidth, height: element.offsetHeight};
  }
  const {width, height} = label.size || {width: 0, height: 0};
  return {
    left: x - width / 2,
    right: x + width / 2,
    top: y - height - label.lift,
    bottom: y - label.lift,
  };
}

/**
 * Étiquettes DOM des amas d'au moins MIN_CLUSTER_LABEL notions, ou marqués named,
 * au-dessus de leur sphère.
 */
function clusterLabels(layer, layout) {
  const named = [...layout.centers.values()].filter(cluster => (
    cluster.named || cluster.ids.length >= MIN_CLUSTER_LABEL
  ));
  return named.map(({center, radius, name, ids}) => {
    const element = el('span', {className: 'scene-label is-cluster', text: name});
    layer.append(element);
    const position = new THREE.Vector3(center[0], center[1] + radius + 3.4, center[2]);
    return {ids, element, position, lift: 0};
  });
}

/**
 * Crée la scène dans stage et renvoie de quoi la piloter. Lève une Error dont le message
 * dit la cause si three.js, ses contrôles, WebGL ou la charte manquent.
 *
 * @param {HTMLElement} stage conteneur du canevas et de #labels
 * @param {Object} data objet window.SYSTEME
 * @param {Object} network résultat de buildNetwork
 * @param {Object} layout résultat de layoutNetwork
 * @param {{onPick: function({node: ?string, link: ?number}), onHover: function(?string,
 *   ?Object), onFailure: function(string)}} handlers rappels : nœud ou lien cliqué (les
 *   deux nuls dans le vide), nœud survolé et son rectangle à l'écran, perte du contexte
 * @returns {{applyView: function(Object), resetView: function(), dispose: function()}}
 *   dispose retire la scène de la page avant d'en créer une autre
 */
function createScene(stage, data, network, layout, handlers) {
  if (typeof THREE === 'undefined') {
    throw new Error('La bibliothèque three.js n’a pas été chargée : '
      + 'vendor/three.min.js est absent ou illisible.');
  }
  if (typeof THREE.OrbitControls !== 'function') {
    throw new Error('Les contrôles de caméra n’ont pas été chargés : '
      + 'vendor/OrbitControls.js est absent ou illisible.');
  }
  const palette = cssPalette();
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({antialias: true, alpha: true});
  } catch (error) {
    throw new Error(`WebGL est indisponible dans ce navigateur (${error.message}).`);
  }
  const canvas = renderer.domElement;
  canvas.className = 'scene-canvas';
  canvas.setAttribute('role', 'img');
  canvas.setAttribute(
    'aria-label',
    'Vue 3D du réseau ; la liste « Connexions » donne le même contenu au clavier.',
  );
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 1000);
  scene.fog = new THREE.Fog(palette['--void'], 1, 2);
  const controls = new THREE.OrbitControls(camera, canvas);
  const textures = spriteTextures(palette);
  const context = {data, layout, network, dashes: dashTextures(), palette};
  const state = {
    motion: !motionQuery.matches,
    spin: true,
    selected: false,
    resume: 0,
    hovered: null,
    framed: false,
    lost: false,
    radius: Math.max(layout.frame, 8) + 6,
  };
  const loop = {handle: 0};
  const labels = {
    layer: byId('labels'),
    clusters: clusterLabels(byId('labels'), layout),
    nodes: [],
  };
  const raycaster = new THREE.Raycaster();
  const pointer = new THREE.Vector2();
  const startTime = performance.now();

  const extent = Math.max(layout.frame, 8);
  const haloTexture = glowTexture([
    [0, withAlpha(palette['--flux'], 0.38)],
    [0.3, withAlpha(palette['--flux'], 0.12)],
    [0.5, withAlpha(palette['--flux'], 0.03)],
    [0.62, withAlpha(palette['--flux'], 0)],
  ], 2 * TEXTURE_SIZE);
  scene.add(
    buildStars(Math.max(layout.extent, 8), palette['--rail']),
    buildPlatform(extent, palette['--flux']),
    ...buildClusterHalos(layout, haloTexture),
  );
  const nodes = buildNodes(scene, network, layout, textures);
  const spriteById = new Map(nodes.map(entry => [entry.node.id, entry.sprite]));
  const links = network.links.map(link => buildLink(context, link)).filter(Boolean);
  for (const entry of links) {
    scene.add(entry.group);
    if (entry.link.kind !== TRANSFER_KIND) continue;
    entry.pulse = overlaySprite(scene, textures.pulse, '#ffffff', false);
    entry.pulse.scale.setScalar(1.9);
  }
  const rootHalo = overlaySprite(scene, textures.halo, palette['--flux'], true);
  const selectHalo = overlaySprite(scene, textures.halo, palette['--rail'], true);
  const hoverHalo = overlaySprite(scene, textures.halo, palette['--flux'], true);

  /** Pose halo sur le nœud id, ou le masque si id est nul ou masqué. */
  const placeHalo = (halo, id) => {
    const sprite = id && spriteById.get(id);
    halo.visible = Boolean(sprite?.visible);
    if (!halo.visible) return;
    halo.position.copy(sprite.position);
    halo.scale.setScalar((sprite.userData.radius + 0.7) * 2.3);
  };

  /**
   * Projette les étiquettes sur le canevas ; masquées derrière la caméra, hors cadre. Les
   * étiquettes de notion gardent leur place ; celles d'amas, de la plus proche de la
   * caméra à la plus lointaine, sont masquées tant qu'elles en recouvriraient une autre.
   */
  const placeLabels = () => {
    const {clientWidth: width, clientHeight: height} = canvas;
    const shown = [];
    for (const label of [...labels.clusters, ...labels.nodes]) {
      if (label.element.hidden) continue;
      const point = label.position.clone().project(camera);
      const outside = point.z > 1 || Math.abs(point.x) > 1.1 || Math.abs(point.y) > 1.1;
      label.element.style.visibility = outside ? 'hidden' : '';
      if (outside) continue;
      const x = round(((point.x + 1) / 2) * width);
      const y = round(((1 - point.y) / 2) * height);
      label.element.style.transform = `translate(${x}px, ${y}px)`;
      shown.push({label, depth: point.z, rect: labelRect(label, x, y)});
    }
    const taken = shown.filter(entry => !entry.label.ids).map(entry => entry.rect);
    const clusters = shown.filter(entry => entry.label.ids);
    for (const {label, rect} of clusters.sort((a, b) => a.depth - b.depth)) {
      const clash = taken.some(other => overlaps(rect, other));
      label.element.style.visibility = clash ? 'hidden' : '';
      if (!clash) taken.push(rect);
    }
  };

  /** Fait avancer chaque signal de transfert le long de sa courbe. */
  const movePulses = now => {
    const phase = ((now - startTime) % PULSE_MS) / PULSE_MS;
    for (const entry of links) {
      if (entry.pulse) entry.pulse.position.copy(entry.curve.getPointAt(phase));
    }
  };

  /**
   * Une image : contrôles, brouillard calé sur la distance de la caméra (l'arrière du
   * réseau s'assombrit à tout zoom), signaux, rendu, étiquettes ; relance si l'animation
   * court.
   */
  const drawFrame = now => {
    loop.handle = 0;
    if (!state.framed) return;
    controls.update();
    const distance = camera.position.distanceTo(controls.target);
    scene.fog.near = Math.max(0, distance - state.radius * 0.4);
    scene.fog.far = distance + state.radius * 2.2;
    if (state.motion) movePulses(now);
    renderer.render(scene, camera);
    placeLabels();
    if (state.motion) scheduleFrame();
  };

  /** Demande une image, sauf si une est prévue, la page masquée ou le contexte perdu. */
  const scheduleFrame = () => {
    if (loop.handle || document.hidden || state.lost) return;
    loop.handle = requestAnimationFrame(drawFrame);
  };

  /** Applique le réglage de mouvement : rotation, inertie et signaux. */
  const applyMotion = () => {
    state.motion = !motionQuery.matches;
    controls.enableDamping = state.motion;
    controls.autoRotate = state.motion && state.spin && !state.hovered;
    for (const entry of links) {
      if (!entry.pulse) continue;
      entry.pulse.visible = state.motion && entry.group.visible && entry.focused;
    }
    scheduleFrame();
  };

  /**
   * Cadre le réseau entre les panneaux, vu de biais et d'en haut, et relance la rotation
   * automatique ; la demi-largeur layout.span tient en entier, le reste déborde un peu.
   */
  const resetView = () => {
    state.spin = true;
    const radius = state.radius;
    const vertical = THREE.MathUtils.degToRad(camera.fov / 2);
    const clear = clearHalfWidth(stage);
    const angleOf = pixels => (
      Math.atan((Math.tan(vertical) * 2 * pixels) / stage.clientHeight)
    );
    const fill = radius * FRAME_FILL;
    const wide = layout.span === null ? fill : layout.span + NODE_ROOM;
    const distance = Math.max(
      wide / Math.sin(angleOf(clear)),
      fill / Math.sin(vertical),
    );
    camera.position.set(0, 0.55, 1).normalize().multiplyScalar(distance);
    camera.near = distance / 100;
    camera.far = distance * 5;
    camera.updateProjectionMatrix();
    controls.target.set(0, 0, 0);
    controls.minDistance = radius * 0.12;
    controls.maxDistance = distance * 2.5;
    controls.update();
    state.framed = true;
    applyMotion();
  };

  /** Adapte le canevas au conteneur, cadre la vue à la première taille connue. */
  const resize = () => {
    const {clientWidth: width, clientHeight: height} = stage;
    if (!width || !height) return;
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    if (!state.framed) resetView();
    scheduleFrame();
  };

  /**
   * Ce qui est visible sous le pointeur : {node} pour le nœud dont le disque contient le
   * point (sinon le plus proche du rayon), à défaut {link} pour le lien le plus proche ;
   * les deux nuls dans le vide.
   */
  const pickAt = event => {
    const box = canvas.getBoundingClientRect();
    pointer.set(
      ((event.clientX - box.left) / box.width) * 2 - 1,
      1 - ((event.clientY - box.top) / box.height) * 2,
    );
    raycaster.setFromCamera(pointer, camera);
    const visible = nodes.map(entry => entry.sprite).filter(sprite => sprite.visible);
    const hits = raycaster.intersectObjects(visible, false);
    const offset = ({point, object}) => (
      point.distanceTo(object.position) / object.userData.radius
    );
    const hit = hits.find(entry => offset(entry) <= 1.2)
      || hits.sort((left, right) => offset(left) - offset(right))[0];
    if (hit) return {node: hit.object.userData.id, link: null};
    const tubes = links.filter(entry => entry.group.visible).map(entry => entry.pick);
    const tube = raycaster.intersectObjects(tubes, false)[0];
    return {node: null, link: tube ? tube.object.userData.link : null};
  };

  /** Rectangle à l'écran du nœud id, pour l'infobulle. */
  const screenRect = id => {
    const sprite = spriteById.get(id);
    const box = canvas.getBoundingClientRect();
    const point = sprite.position.clone().project(camera);
    const x = box.left + ((point.x + 1) / 2) * box.width;
    const y = box.top + ((1 - point.y) / 2) * box.height;
    const size = 12;
    return {
      left: x - size,
      top: y - size,
      width: 2 * size,
      height: 2 * size,
      right: x + size,
      bottom: y + size,
    };
  };

  /**
   * Survol de target ({node, link}) : halo et infobulle du nœud, curseur de clic sur un
   * nœud ou un lien, pause de la rotation au-dessus d'un nœud.
   */
  const hover = target => {
    canvas.classList.toggle('is-pointing', Boolean(target.node) || target.link !== null);
    if (target.node === state.hovered) return;
    state.hovered = target.node;
    placeHalo(hoverHalo, target.node);
    handlers.onHover(target.node, target.node ? screenRect(target.node) : null);
    applyMotion();
  };

  /**
   * Met la scène à jour pour view : nœuds et liens affichés, nœuds de view.focus et liens
   * de view.focusLinks mis en avant, les autres estompés ; étiquette des seuls nœuds de
   * view.labels (le choix ou les deux bouts du lien choisi).
   */
  const applyView = view => {
    state.selected = Boolean(view.selected);
    state.spin = !state.selected;
    for (const {node, sprite} of nodes) {
      sprite.visible = view.nodes.has(node.id);
      sprite.material.opacity = view.focus && !view.focus.has(node.id) ? DIM_NODE : 1;
    }
    for (const entry of links) {
      entry.group.visible = view.links.has(entry.link.index);
      entry.focused = !view.focusLinks || view.focusLinks.has(entry.link.index);
      const opacity = entry.opacity * (entry.focused ? 1 : DIM_LINK);
      for (const material of entry.materials) material.opacity = opacity;
    }
    placeHalo(selectHalo, view.selected);
    placeHalo(rootHalo, layout.root);
    rootHalo.scale.multiplyScalar(1.5);
    if (state.hovered && !view.nodes.has(state.hovered)) hover(NOTHING);
    for (const label of labels.clusters) {
      label.element.hidden = !label.ids.some(id => view.nodes.has(id));
      label.element.classList.toggle(
        'is-dim',
        Boolean(view.focus) && !label.ids.some(id => view.focus.has(id)),
      );
    }
    for (const label of labels.nodes) label.element.remove();
    labels.nodes = view.labels.filter(id => view.nodes.has(id)).map(id => {
      const sprite = spriteById.get(id);
      const element = el('span', {
        className: 'scene-label is-node',
        text: shortLabel(network.byId.get(id).label),
      });
      labels.layer.append(element);
      const position = sprite.position.clone();
      position.y += sprite.userData.radius + 0.6;
      return {element, position, lift: 4};
    });
    applyMotion();
  };

  controls.autoRotateSpeed = AUTO_ROTATE_SPEED;
  controls.addEventListener('change', scheduleFrame);
  controls.addEventListener('start', () => {
    clearTimeout(state.resume);
    state.spin = false;
    applyMotion();
  });
  controls.addEventListener('end', () => {
    clearTimeout(state.resume);
    state.resume = setTimeout(() => {
      state.spin = !state.selected;
      applyMotion();
    }, SPIN_RESUME_MS);
  });
  let press = null;
  canvas.addEventListener('pointerdown', event => {
    press = event.button === 0 ? {x: event.clientX, y: event.clientY} : null;
  });
  canvas.addEventListener('pointerup', event => {
    const moved = press && Math.hypot(event.clientX - press.x, event.clientY - press.y);
    if (press && moved <= CLICK_SLOP) handlers.onPick(pickAt(event));
    press = null;
  });
  canvas.addEventListener('pointermove', event => {
    if (!event.buttons) hover(pickAt(event));
  });
  canvas.addEventListener('pointerleave', () => hover(NOTHING));
  canvas.addEventListener('webglcontextlost', event => {
    event.preventDefault();
    if (state.lost) return;
    state.lost = true;
    cancelAnimationFrame(loop.handle);
    loop.handle = 0;
    handlers.onFailure('Le contexte WebGL a été perdu (pilote graphique réinitialisé ou '
      + 'mémoire graphique saturée).');
  });
  const onVisibility = () => {
    if (!document.hidden) {
      scheduleFrame();
      return;
    }
    cancelAnimationFrame(loop.handle);
    loop.handle = 0;
  };
  document.addEventListener('visibilitychange', onVisibility);
  motionQuery.addEventListener('change', applyMotion);
  stage.prepend(canvas);
  const observer = new ResizeObserver(resize);
  observer.observe(stage);
  resize();

  /** Arrête la scène et libère ce qu'elle tient : boucle, écouteurs, canevas, GPU. */
  const dispose = () => {
    state.lost = true;
    clearTimeout(state.resume);
    cancelAnimationFrame(loop.handle);
    observer.disconnect();
    document.removeEventListener('visibilitychange', onVisibility);
    motionQuery.removeEventListener('change', applyMotion);
    controls.dispose();
    scene.traverse(object => {
      object.geometry?.dispose();
      for (const material of [object.material].flat().filter(Boolean)) {
        material.map?.dispose();
        material.alphaMap?.dispose();
        material.dispose();
      }
    });
    renderer.dispose();
    canvas.remove();
    labels.layer.replaceChildren();
  };
  return {applyView, resetView, dispose};
}
