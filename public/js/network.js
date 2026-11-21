'use strict';

/*
 * Réseau des notions : calculs purs sur window.SYSTEME, sans DOM ni three.js.
 *
 * Construit le graphe des notions reliées par data.relations : une notion absente de
 * data.notions reste un nœud « inconnu », signalé suspect (arbitrage A13). Les nœuds se
 * groupent en amas par carte, ou par section pour une notion hors carte ; les amas se
 * posent sur un anneau, comme les domaines de la roue, et leurs nœuds sur une petite
 * sphère. La couleur d'un lien dit son type, son épaisseur et son trait son statut.
 * stateGroup et dataCards viennent de model.js, chargé avant ce script. Exporté pour
 * Node par module.exports ; dans la page, fonctions globales.
 */

const TRANSFER_KIND = 'transfert';
const UNKNOWN_CLUSTER = 'unknown';
const CLUSTER_GAP = 7;
const GOLDEN_ANGLE = Math.PI * (3 - Math.sqrt(5));
const TREE_SHELL = 12;
const TREE_GAP = 8;

/* Dispositions proposées du réseau, la première par défaut. */
const LAYOUT_MODES = [
  {
    code: 'clusters',
    label: 'Amas',
    meaning: 'les notions regroupées par domaine, sans racine',
  },
  {
    code: 'tree',
    label: 'Arbre',
    meaning: 'la notion racine au centre, ses connexions en branches autour d’elle ; '
      + 'chaque domaine nommé une fois, sur son plus grand groupe de notions reliées',
  },
];

/* Type de lien : jeton CSS de sa couleur et sens (cartographie.md de /professor). */
const KIND_STYLES = {
  transfert: {
    token: '--kind-transfer',
    meaning: 'la première notion a été réutilisée dans le contexte de la seconde',
  },
  prerequis: {
    token: '--kind-prerequisite',
    meaning: 'la première notion est nécessaire pour comprendre la seconde',
  },
  instance_de: {
    token: '--kind-instance',
    meaning: 'la première notion illustre le principe qu’est la seconde',
  },
  complementaire: {
    token: '--kind-complement',
    meaning: 'les deux notions se combinent, avec une valeur ajoutée',
  },
  analogue: {
    token: '--kind-analog',
    meaning: 'les deux notions ont la même structure ; la limite dit ce qui empêche de '
      + 'transposer',
  },
};
const DEFAULT_KIND_STYLE = {token: '--text-faint', meaning: 'type de lien inconnu du suivi'};

/* Rendu d'un statut : rayon du tube, motif du trait, opacité et définition. */
const STATUS_STYLES = {
  demonstrated: {
    radius: 0.4,
    pattern: 'solid',
    opacity: 0.95,
    meaning: 'lien utilisé avec succès dans un exercice ou un projet, preuve citée',
  },
  recognized: {
    radius: 0.24,
    pattern: 'dash',
    opacity: 0.85,
    meaning: 'lien énoncé par Louis lui-même',
  },
  theoretical: {
    radius: 0.12,
    pattern: 'dot',
    opacity: 0.7,
    meaning: 'lien proposé par Claude, pas encore constaté',
  },
};
const DEFAULT_STATUS_STYLE = {
  radius: 0.1,
  pattern: 'dot',
  opacity: 0.5,
  meaning: 'statut inconnu du suivi',
};

/**
 * Type de lien lu dans data.linkKinds : libellé et sens ; un type absent garde son code.
 *
 * @param {Object} data objet window.SYSTEME
 * @param {string} code code du type (prerequis, transfert...)
 * @returns {{code: string, label: string, outgoing: string, incoming: string,
 *   known: boolean, directed: boolean, style: Object}}
 */
function kindInfo(data, code) {
  const kind = data.linkKinds?.[code];
  return {
    code,
    label: kind?.label || code,
    outgoing: kind?.outgoing || 'lié à',
    incoming: kind?.incoming || 'lié à',
    known: Boolean(kind),
    directed: Boolean(kind) && kind.outgoing !== kind.incoming,
    style: KIND_STYLES[code] || DEFAULT_KIND_STYLE,
  };
}

/** Libellé d'un statut de lien lu dans data.linkStatuses, sinon « statut inconnu ». */
function statusLabel(data, code) {
  const statuses = Array.isArray(data.linkStatuses) ? data.linkStatuses : [];
  return statuses.find(status => status?.code === code)?.label || `statut inconnu (${code})`;
}

/** Rendu du statut de lien code : motif et opacité. */
function statusStyle(code) {
  return STATUS_STYLES[code] || DEFAULT_STATUS_STYLE;
}

/**
 * Amas d'une notion : sa carte, sinon sa section (« hors carte »), sinon l'amas des
 * notions inconnues.
 *
 * @param {Object} data objet window.SYSTEME
 * @param {string} id identifiant de notion
 * @returns {{key: string, name: string, card: string|null, section: string|null}}
 */
function clusterOf(data, id) {
  const notion = data.notions?.[id];
  if (!notion) {
    const name = 'Notions absentes du suivi';
    return {key: UNKNOWN_CLUSTER, name, card: null, section: null};
  }
  if (notion.card) {
    const card = dataCards(data).find(entry => entry?.id === notion.card);
    const name = card ? card.name || card.id : `${notion.card} (carte absente du suivi)`;
    return {key: `card:${notion.card}`, name, card: notion.card, section: null};
  }
  const section = notion.section || 'Sans section';
  return {key: `section:${section}`, name: `${section}, hors carte`, card: null, section};
}

/**
 * Clé de tri d'un amas : les cartes dans l'ordre de data.cards, chacune suivie de sa
 * section hors carte de même nom, puis les autres sections, puis les notions inconnues.
 */
function clusterRank(data, cluster) {
  const cards = dataCards(data);
  const byCard = cards.findIndex(card => card?.id === cluster.card);
  if (byCard >= 0) return [byCard, 0];
  const byName = cards.findIndex(card => cluster.section && card?.name === cluster.section);
  if (byName >= 0) return [byName, 1];
  return [cards.length + (cluster.key === UNKNOWN_CLUSTER ? 1 : 0), 2];
}

/** Compare deux amas par clusterRank, puis par nom. */
function compareClusters(data, left, right) {
  const [a, b] = [clusterRank(data, left), clusterRank(data, right)];
  return a[0] - b[0] || a[1] - b[1] || left.name.localeCompare(right.name, 'fr');
}

/** Nœud d'une notion : libellé, état, allumage et amas ; un id inconnu reste un nœud. */
function makeNode(data, id) {
  const notion = data.notions?.[id];
  return {
    id,
    label: notion?.label || id,
    known: Boolean(notion),
    state: notion?.state || null,
    group: notion ? stateGroup(data, notion.state) : 'unknown',
    level: notion ? stateLevel(data, notion.state) : 0,
    cluster: clusterOf(data, id).key,
  };
}

/**
 * Graphe des notions reliées. Une relation sans source ou cible textuelle est comptée
 * dans unreadable et ignorée.
 *
 * @param {Object} data objet window.SYSTEME
 * @returns {{nodes: Object[], byId: Map<string, Object>, links: Object[],
 *   clusters: Object[], unreadable: number, hasRelations: boolean}} clusters :
 *   {key, name, nodeIds} triés ; links : {index, source, target, kind, status, limit,
 *   proof}
 */
function buildNetwork(data) {
  const relations = Array.isArray(data.relations) ? data.relations : [];
  const readable = relations.filter(relation => (
    typeof relation?.source === 'string' && typeof relation?.target === 'string'
  ));
  const links = readable.map((relation, index) => ({
    index,
    source: relation.source,
    target: relation.target,
    kind: String(relation.kind),
    status: String(relation.status),
    limit: relation.limit || null,
    proof: relation.proof || null,
  }));
  const byId = new Map();
  const clusters = new Map();
  for (const id of links.flatMap(link => [link.source, link.target])) {
    if (byId.has(id)) continue;
    byId.set(id, makeNode(data, id));
    const cluster = clusterOf(data, id);
    if (!clusters.has(cluster.key)) clusters.set(cluster.key, {...cluster, nodeIds: []});
    clusters.get(cluster.key).nodeIds.push(id);
  }
  const sorted = [...clusters.values()].sort((left, right) => (
    compareClusters(data, left, right)
  ));
  for (const cluster of sorted) {
    cluster.nodeIds.sort((left, right) => (
      byId.get(left).label.localeCompare(byId.get(right).label, 'fr')
    ));
  }
  return {
    nodes: sorted.flatMap(cluster => cluster.nodeIds.map(id => byId.get(id))),
    byId,
    links,
    clusters: sorted,
    unreadable: relations.length - readable.length,
    hasRelations: Array.isArray(data.relations),
  };
}

/** Rayon de la sphère d'un amas de count nœuds ; 0 pour un nœud seul. */
function clusterRadius(count) {
  return count > 1 ? 2.5 + 2.4 * Math.sqrt(count) : 0;
}

/** Point index sur count répartis sur la sphère unité (spirale de Fibonacci). */
function fibonacciPoint(index, count) {
  const y = 1 - (2 * (index + 0.5)) / count;
  const ring = Math.sqrt(1 - y * y);
  const angle = index * GOLDEN_ANGLE;
  return [ring * Math.cos(angle), y, ring * Math.sin(angle)];
}

/**
 * Disposition 3D déterministe : amas sur un anneau horizontal (arc proportionnel à leur
 * diamètre, hauteur alternée), nœuds sur la sphère de leur amas.
 *
 * @param {{clusters: Object[]}} network résultat de buildNetwork
 * @returns {{positions: Map<string, number[]>, centers: Map<string, {center: number[],
 *   radius: number, name: string, ids: string[]}>, extent: number}} centers : sphère, nom
 *   et notions de chaque amas ; extent : plus grande distance d'un nœud à l'origine
 */
function layoutNetwork(network) {
  const radii = network.clusters.map(cluster => clusterRadius(cluster.nodeIds.length));
  const spans = radii.map(radius => 2 * radius + CLUSTER_GAP);
  const circumference = spans.reduce((sum, span) => sum + span, 0);
  const ring = network.clusters.length > 1 ? circumference / (2 * Math.PI) : 0;
  const positions = new Map();
  const centers = new Map();
  let along = 0;
  network.clusters.forEach((cluster, index) => {
    const angle = ((along + spans[index] / 2) / circumference) * 2 * Math.PI;
    along += spans[index];
    const lift = (index % 2 ? 1 : -1) * ring * 0.12;
    const center = [ring * Math.cos(angle), lift, ring * Math.sin(angle)];
    centers.set(cluster.key, {
      center,
      radius: radii[index],
      name: cluster.name,
      ids: cluster.nodeIds,
    });
    cluster.nodeIds.forEach((id, rank) => {
      const unit = fibonacciPoint(rank, cluster.nodeIds.length);
      positions.set(id, center.map((value, axis) => value + unit[axis] * radii[index]));
    });
  });
  const extent = Math.max(0, ...[...positions.values()].map(point => Math.hypot(...point)));
  return {positions, centers, extent};
}

/**
 * Voisinage de chaque notion, sans sens : les liens se parcourent dans les deux directions.
 *
 * @param {{nodes: Object[], links: Object[]}} network résultat de buildNetwork
 * @returns {Map<string, {id: string, link: number}[]>} voisins et indice du lien
 */
function neighborMap(network) {
  const neighbors = new Map(network.nodes.map(node => [node.id, []]));
  for (const link of network.links) {
    if (link.source === link.target) continue;
    neighbors.get(link.source).push({id: link.target, link: link.index});
    neighbors.get(link.target).push({id: link.source, link: link.index});
  }
  return neighbors;
}

/** Groupes de notions reliées entre elles, du plus grand au plus petit. */
function connectedGroups(network, neighbors) {
  const seen = new Set();
  const groups = [];
  for (const node of network.nodes) {
    if (seen.has(node.id)) continue;
    const group = [];
    const queue = [node.id];
    seen.add(node.id);
    while (queue.length) {
      const id = queue.shift();
      group.push(id);
      for (const next of neighbors.get(id)) {
        if (seen.has(next.id)) continue;
        seen.add(next.id);
        queue.push(next.id);
      }
    }
    groups.push(group);
  }
  return groups.sort((left, right) => right.length - left.length);
}

/** Notion la plus reliée de ids, la première en cas d'égalité : racine par défaut. */
function mostLinked(ids, neighbors) {
  return ids.reduce((best, id) => (
    neighbors.get(id).length > neighbors.get(best).length ? id : best
  ));
}

/**
 * Arbre couvrant en largeur depuis root : chaque notion s'accroche à la notion la plus
 * proche de la racine qui la touche.
 *
 * @param {string} root identifiant de la racine
 * @param {Map} neighbors résultat de neighborMap
 * @returns {{order: string[], depth: Map<string, number>, children: Map<string,
 *   string[]>, links: number[]}} order : notions de la racine vers les feuilles ; links :
 *   indices des liens qui forment l'arbre
 */
function spanningTree(root, neighbors) {
  const depth = new Map([[root, 0]]);
  const children = new Map([[root, []]]);
  const links = [];
  const order = [root];
  for (let cursor = 0; cursor < order.length; cursor += 1) {
    const id = order[cursor];
    for (const next of neighbors.get(id)) {
      if (depth.has(next.id)) continue;
      depth.set(next.id, depth.get(id) + 1);
      children.set(next.id, []);
      children.get(id).push(next.id);
      links.push(next.link);
      order.push(next.id);
    }
  }
  return {order, depth, children, links};
}

/** Vecteur [x, y, z] ramené à la longueur 1 ; [0, 1, 0] pour un vecteur nul. */
function unitVector([x, y, z]) {
  const length = Math.hypot(x, y, z);
  return length < 1e-9 ? [0, 1, 0] : [x / length, y / length, z / length];
}

/** Directions de count branches en cône d'angle spread (radians) autour de axis. */
function coneDirections(axis, count, spread, turn) {
  if (count === 1) return [axis];
  const helper = Math.abs(axis[1]) < 0.9 ? [0, 1, 0] : [1, 0, 0];
  const side = unitVector([
    axis[1] * helper[2] - axis[2] * helper[1],
    axis[2] * helper[0] - axis[0] * helper[2],
    axis[0] * helper[1] - axis[1] * helper[0],
  ]);
  const up = [
    axis[1] * side[2] - axis[2] * side[1],
    axis[2] * side[0] - axis[0] * side[2],
    axis[0] * side[1] - axis[1] * side[0],
  ];
  return Array.from({length: count}, (unused, index) => {
    const angle = turn + (index / count) * 2 * Math.PI;
    return unitVector(axis.map((value, part) => (
      value * Math.cos(spread)
        + (side[part] * Math.cos(angle) + up[part] * Math.sin(angle)) * Math.sin(spread)
    )));
  });
}

/**
 * Arbre rayonnant : la racine au centre, chaque génération sur une sphère plus grande,
 * les branches d'une notion ouvertes en cône dans sa direction.
 *
 * @param {Object} tree résultat de spanningTree
 * @returns {Map<string, number[]>} position [x, y, z] de chaque notion, racine en 0
 */
function radialPositions(tree) {
  const [root] = tree.order;
  const positions = new Map([[root, [0, 0, 0]]]);
  const directions = new Map();
  const first = tree.children.get(root);
  first.forEach((id, index) => {
    directions.set(id, first.length === 1 ? [0, 1, 0] : fibonacciPoint(index, first.length));
  });
  for (const id of tree.order.slice(1)) {
    const direction = directions.get(id);
    const depth = tree.depth.get(id);
    positions.set(id, direction.map(value => value * depth * TREE_SHELL));
    const branches = tree.children.get(id);
    const spread = Math.min(0.95, 0.3 + 0.1 * branches.length) / Math.sqrt(depth);
    coneDirections(direction, branches.length, spread, depth * GOLDEN_ANGLE)
      .forEach((branch, index) => directions.set(branches[index], branch));
  }
  return positions;
}

/**
 * Titres de domaine d'un arbre : un par amas, posé au centre de son plus grand groupe de
 * notions reliées entre elles par des branches, donc jamais en double.
 *
 * @param {Object} network résultat de buildNetwork
 * @param {Map<string, number[]>} positions position de chaque notion
 * @param {Set<number>} treeLinks indices des liens qui forment les arbres
 * @returns {Map<string, Object>} forme des centers de layoutNetwork, sans sphère (rayon
 *   nul), plus named : true, le titre s'affiche quelle que soit la taille du groupe
 */
function treeCenters(network, positions, treeLinks) {
  const clusterOf = new Map();
  for (const cluster of network.clusters) {
    for (const id of cluster.nodeIds) clusterOf.set(id, cluster);
  }
  const head = new Map([...clusterOf.keys()].map(id => [id, id]));
  const find = id => (head.get(id) === id ? id : find(head.get(id)));
  for (const link of network.links) {
    const joined = treeLinks.has(link.index)
      && clusterOf.get(link.source) === clusterOf.get(link.target);
    if (joined) head.set(find(link.source), find(link.target));
  }
  const groups = new Map();
  for (const id of clusterOf.keys()) {
    const key = find(id);
    groups.set(key, [...(groups.get(key) || []), id]);
  }
  const centers = new Map();
  const largest = new Map();
  for (const ids of groups.values()) {
    const cluster = clusterOf.get(ids[0]);
    if (ids.length > (largest.get(cluster)?.length || 0)) largest.set(cluster, ids);
  }
  for (const [key, ids] of groups) {
    if (largest.get(clusterOf.get(key)) !== ids) continue;
    const points = ids.map(id => positions.get(id));
    const center = [0, 1, 2].map(axis => (
      points.reduce((sum, point) => sum + point[axis], 0) / points.length
    ));
    centers.set(key, {center, radius: 0, name: clusterOf.get(key).name, ids, named: true});
  }
  return centers;
}

/**
 * Disposition 3D en arbres : le groupe de la racine au centre, les autres groupes de
 * notions reliées autour, chacun déployé depuis sa notion la plus reliée.
 *
 * @param {Object} network résultat de buildNetwork
 * @param {string|null} rootId racine voulue ; absente du réseau ou nulle : la notion la
 *   plus reliée du plus grand groupe
 * @returns {{positions: Map<string, number[]>, centers: Map, extent: number, frame:
 *   number, span: null, root: string|null, treeLinks: Set<number>}} centers : résultat
 *   de treeCenters ; frame : rayon de l'arbre central, que la vue cadre ; span nul : rien
 *   à montrer en entier
 */
function layoutTrees(network, rootId) {
  const neighbors = neighborMap(network);
  const groups = connectedGroups(network, neighbors);
  const positions = new Map();
  const treeLinks = new Set();
  if (!groups.length) {
    return {
      positions,
      centers: new Map(),
      extent: 0,
      frame: 0,
      span: null,
      root: null,
      treeLinks,
    };
  }
  const chosen = groups.findIndex(group => group.includes(rootId));
  if (chosen > 0) groups.unshift(...groups.splice(chosen, 1));
  const blocks = groups.map((ids, index) => {
    const root = index === 0 && chosen >= 0 ? rootId : mostLinked(ids, neighbors);
    const tree = spanningTree(root, neighbors);
    tree.links.forEach(link => treeLinks.add(link));
    const local = radialPositions(tree);
    const reach = Math.max(0, ...[...local.values()].map(point => Math.hypot(...point)));
    return {root, local, reach};
  });
  const [main, ...others] = blocks;
  const span = others.reduce((sum, block) => sum + 2 * block.reach + TREE_GAP, 0);
  const ring = Math.max(main.reach + TREE_GAP, span / (2 * Math.PI));
  let along = 0;
  blocks.forEach((block, index) => {
    let center = [0, 0, 0];
    if (index > 0) {
      const share = 2 * block.reach + TREE_GAP;
      const angle = ((along + share / 2) / span) * 2 * Math.PI;
      along += share;
      const distance = ring + block.reach;
      center = [distance * Math.cos(angle), 0, distance * Math.sin(angle)];
    }
    for (const [id, point] of block.local) {
      positions.set(id, point.map((value, axis) => value + center[axis]));
    }
  });
  const extent = Math.max(0, ...[...positions.values()].map(point => Math.hypot(...point)));
  return {
    positions,
    centers: treeCenters(network, positions, treeLinks),
    extent,
    frame: main.reach,
    span: null,
    root: main.root,
    treeLinks,
  };
}

/**
 * Disposition 3D du mode mode : « clusters » (amas par domaine) ou « tree » (arbre).
 *
 * @param {Object} network résultat de buildNetwork
 * @param {string} mode code de LAYOUT_MODES
 * @param {string|null} rootId racine voulue des dispositions en arbre
 * @returns {Object} forme de layoutTrees ; pour les amas, root nul, treeLinks vide et
 *   span : demi-largeur de l'anneau des amas, que la vue montre en entier
 */
function layoutFor(network, mode, rootId) {
  if (mode !== 'clusters') return layoutTrees(network, rootId);
  const layout = layoutNetwork(network);
  return {
    ...layout,
    frame: layout.extent,
    span: layout.extent,
    root: null,
    treeLinks: new Set(),
  };
}

/** Identifiants des notions touchées par les liens links. */
function linkedIds(links) {
  return new Set(links.flatMap(link => [link.source, link.target]));
}

/**
 * Liens d'une notion parmi links, vus depuis elle : transferts d'abord, puis dans l'ordre
 * des types de data.linkKinds et des statuts de data.linkStatuses.
 *
 * @param {Object} data objet window.SYSTEME
 * @param {Object[]} links liens de buildNetwork
 * @param {string} id identifiant de la notion
 * @returns {{link: Object, otherId: string, phrase: string, kind: Object}[]} phrase : sens
 *   du lien lu depuis la notion (« prérequis de », « a pour prérequis »...)
 */
function nodeLinks(data, links, id) {
  const kindOrder = Object.keys(data.linkKinds || {});
  const statusOrder = (data.linkStatuses || []).map(status => status?.code);
  const rank = (order, code) => (order.includes(code) ? order.indexOf(code) : order.length);
  return links
    .filter(link => link.source === id || link.target === id)
    .map(link => {
      const kind = kindInfo(data, link.kind);
      const outgoing = link.source === id;
      return {
        link,
        kind,
        otherId: outgoing ? link.target : link.source,
        phrase: outgoing ? kind.outgoing : kind.incoming,
      };
    })
    .sort((left, right) => (
      (right.link.kind === TRANSFER_KIND) - (left.link.kind === TRANSFER_KIND)
      || rank(kindOrder, left.link.kind) - rank(kindOrder, right.link.kind)
      || rank(statusOrder, left.link.status) - rank(statusOrder, right.link.status)
    ));
}

/**
 * Décompte des liens par valeur d'un champ, dans l'ordre de order puis des valeurs
 * inconnues de order.
 *
 * @param {Object[]} links liens de buildNetwork
 * @param {string} field « kind » ou « status »
 * @param {string[]} order codes connus, dans l'ordre d'affichage
 * @returns {{code: string, count: number}[]} codes sans lien omis
 */
function countBy(links, field, order) {
  const counts = new Map(order.map(code => [code, 0]));
  for (const link of links) counts.set(link[field], (counts.get(link[field]) || 0) + 1);
  return [...counts].filter(([, count]) => count > 0).map(([code, count]) => ({code, count}));
}

/** Types présents dans links, transferts d'abord, avec leur décompte et leur rendu. */
function kindSummary(data, links) {
  const order = [TRANSFER_KIND, ...Object.keys(data.linkKinds || {})];
  return countBy(links, 'kind', [...new Set(order)])
    .map(entry => ({...kindInfo(data, entry.code), count: entry.count}));
}

/** Statuts présents dans links, dans l'ordre de data.linkStatuses, avec leur décompte. */
function statusSummary(data, links) {
  const order = (Array.isArray(data.linkStatuses) ? data.linkStatuses : [])
    .map(status => status?.code);
  return countBy(links, 'status', order).map(entry => ({
    ...entry,
    label: statusLabel(data, entry.code),
    style: statusStyle(entry.code),
  }));
}

/** Texte « n mots / N », au singulier pour 0 ou 1. */
function countText(count, total, singular, plural) {
  return `${count} ${count > 1 ? plural : singular} / ${total}`;
}

if (typeof module !== 'undefined') {
  module.exports = {
    TRANSFER_KIND,
    kindInfo,
    statusLabel,
    statusStyle,
    clusterOf,
    buildNetwork,
    clusterRadius,
    fibonacciPoint,
    layoutNetwork,
    LAYOUT_MODES,
    neighborMap,
    connectedGroups,
    spanningTree,
    layoutTrees,
    layoutFor,
    linkedIds,
    nodeLinks,
    kindSummary,
    statusSummary,
    countText,
  };
}
