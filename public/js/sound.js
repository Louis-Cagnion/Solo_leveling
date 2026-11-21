'use strict';

/*
 * Maquette « Système » : sons de l'interface, synthétisés par l'API Web Audio.
 *
 * Aucun enregistrement n'est joué. Les sons d'ouverture, de fermeture, de clic, d'annonce
 * et de rangement sont resynthétisés d'après SOUND_PARTIALS (sound-data.js) : la mesure
 * des bruits d'origine fournis par Louis, réduite à des sinusoïdes et à des bandes de
 * bruit filtré, donc proches des originaux sans leur être identiques. Le survol garde un
 * tic synthétique. Rien ne joue avant le premier geste du visiteur (règle des
 * navigateurs) ni quand le son est coupé ; le réglage se garde dans localStorage. Chargé
 * après dom.js et sound-data.js.
 */

const SOUND_KEY = 'system-sound';
const SOUND_TARGETS = '.button, .sector, .hub, .domain-row, .tier-open, .connection, '
  + '.legend-kind, .layout-mode, .connection-group summary, .projects summary, '
  + '.proof summary, .detail-close';
const MASTER_GAIN = 0.5;
const ECHO_DELAY = 0.12;
const ECHO_FEEDBACK = 0.34;
const ECHO_LEVEL = 0.3;

/* Voix du survol, seul son sans bruit d'origine : onde, fréquences (Hz), durées (s). */
const SOUND_VOICES = {
  hover: [
    {wave: 'sine', from: 1077, to: 1280, delay: 0, length: 0.06, gain: 0.05},
  ],
};
const SHARP_ATTACK = 0.008;
/* Durée (s) du bruit blanc mis en boucle derrière les bandes de bruit. */
const NOISE_SECONDS = 2;
const noiseBuffers = new WeakMap();

const soundState = {context: null, master: null, dry: null, muted: false, hovered: null};

/** true si le visiteur a déjà agi sur la page : avant, le navigateur refuse tout son. */
function hasUserGesture() {
  return navigator.userActivation ? navigator.userActivation.hasBeenActive : true;
}

/** Contexte audio, créé au premier besoin ; null si l'API manque ou échoue. */
function audioContext() {
  if (soundState.context) return soundState.context;
  const AudioApi = window.AudioContext || window.webkitAudioContext;
  if (!AudioApi) return null;
  try {
    soundState.context = new AudioApi();
  } catch {
    return null;
  }
  const {context} = soundState;
  soundState.master = context.createGain();
  soundState.master.gain.value = MASTER_GAIN;
  soundState.master.connect(context.destination);
  soundState.dry = context.createGain();
  soundState.dry.gain.value = MASTER_GAIN;
  soundState.dry.connect(context.destination);
  /* Écho court et réinjecté : la traîne cristalline d'une fenêtre holographique. */
  const echo = context.createDelay(0.5);
  const feedback = context.createGain();
  const wet = context.createGain();
  echo.delayTime.value = ECHO_DELAY;
  feedback.gain.value = ECHO_FEEDBACK;
  wet.gain.value = ECHO_LEVEL;
  soundState.master.connect(echo);
  echo.connect(feedback).connect(echo);
  echo.connect(wet).connect(context.destination);
  return context;
}

/** Joue une voix : un oscillateur, son attaque puis sa chute exponentielle. */
function playVoice(context, voice) {
  const start = context.currentTime + voice.delay;
  const end = start + voice.length;
  const oscillator = context.createOscillator();
  const envelope = context.createGain();
  oscillator.type = voice.wave;
  oscillator.frequency.setValueAtTime(voice.from, start);
  oscillator.frequency.exponentialRampToValueAtTime(voice.to, end);
  envelope.gain.setValueAtTime(0.0001, start);
  const peak = start + (voice.attack || SHARP_ATTACK);
  envelope.gain.exponentialRampToValueAtTime(voice.gain, peak);
  envelope.gain.exponentialRampToValueAtTime(0.0001, end);
  oscillator.connect(envelope).connect(soundState.master);
  oscillator.start(start);
  oscillator.stop(end + 0.02);
}

/** Bruit blanc uniforme du contexte context, créé une fois puis partagé. */
function noiseBuffer(context) {
  if (!noiseBuffers.has(context)) {
    const rate = context.sampleRate;
    const buffer = context.createBuffer(1, rate * NOISE_SECONDS, rate);
    const samples = buffer.getChannelData(0);
    for (let index = 0; index < samples.length; index += 1) {
      samples[index] = Math.random() * 2 - 1;
    }
    noiseBuffers.set(context, buffer);
  }
  return noiseBuffers.get(context);
}

/**
 * Programme sur param l'enveloppe points, à partir de l'instant start.
 *
 * @param {AudioParam} param gain à piloter
 * @param {number[]} points [temps (s), niveau, ...], temps croissants
 * @param {number} start instant du contexte où le son commence
 * @returns {number[]} instants de début et de fin de l'enveloppe
 */
function shapeGain(param, points, start) {
  param.setValueAtTime(points[1], start + points[0]);
  for (let index = 2; index < points.length; index += 2) {
    param.linearRampToValueAtTime(points[index + 1], start + points[index]);
  }
  return [start + points[0], start + points[points.length - 2]];
}

/**
 * Resynthétise un son de SOUND_PARTIALS (sound-data.js) : une sinusoïde par partiel, un
 * bruit blanc passé dans SOUND_NOISE_STAGES filtres par bande de bruit, chacun avec son
 * enveloppe.
 *
 * @param {BaseAudioContext} context contexte audio
 * @param {{partials: Array, noise: Array}} sound entrée de SOUND_PARTIALS
 * @param {AudioNode} output nœud qui reçoit le son
 */
function playResynth(context, sound, output) {
  const start = context.currentTime + 0.01;
  for (const [from, to, points] of sound.partials) {
    const oscillator = context.createOscillator();
    const envelope = context.createGain();
    const [first, last] = shapeGain(envelope.gain, points, start);
    oscillator.frequency.setValueAtTime(from, first);
    oscillator.frequency.linearRampToValueAtTime(to, last);
    oscillator.connect(envelope).connect(output);
    oscillator.start(first);
    oscillator.stop(last + 0.02);
  }
  for (const [centre, quality, points] of sound.noise) {
    const source = context.createBufferSource();
    const envelope = context.createGain();
    const [first, last] = shapeGain(envelope.gain, points, start);
    let chain = source;
    source.buffer = noiseBuffer(context);
    source.loop = true;
    for (let stage = 0; stage < SOUND_NOISE_STAGES; stage += 1) {
      const filter = context.createBiquadFilter();
      filter.type = 'bandpass';
      filter.frequency.value = centre;
      filter.Q.value = quality;
      chain = chain.connect(filter);
    }
    chain.connect(envelope).connect(output);
    source.start(first, Math.random() * NOISE_SECONDS);
    source.stop(last + 0.02);
  }
}

/**
 * Joue le son name : resynthèse de SOUND_PARTIALS, sinon voix de SOUND_VOICES ; sans effet
 * si le son est coupé, si le visiteur n'a pas encore agi ou si l'audio est indisponible.
 *
 * @param {string} name clé de SOUND_PARTIALS ou de SOUND_VOICES
 */
function playSound(name) {
  const sound = Object.hasOwn(SOUND_PARTIALS, name) ? SOUND_PARTIALS[name] : null;
  const voices = SOUND_VOICES[name];
  if ((!sound && !voices) || soundState.muted || !hasUserGesture()) return;
  const context = audioContext();
  if (!context) return;
  if (context.state === 'suspended') context.resume().catch(() => {});
  if (sound) playResynth(context, sound, soundState.dry);
  else for (const voice of voices) playVoice(context, voice);
}

/**
 * Joue le son name tout de suite si le visiteur a déjà agi sur la page, sinon à son
 * premier geste, tant que wanted renvoie vrai.
 *
 * @param {string} name clé de SOUND_PARTIALS ou de SOUND_VOICES
 * @param {function(): boolean} wanted true tant que le son a encore un sens
 */
function playSoundOnGesture(name, wanted) {
  if (hasUserGesture()) {
    playSound(name);
    return;
  }
  const play = () => {
    for (const type of ['pointerdown', 'keydown']) document.removeEventListener(type, play);
    if (wanted()) playSound(name);
  };
  for (const type of ['pointerdown', 'keydown']) document.addEventListener(type, play);
}

/** Réglage « son coupé » gardé dans localStorage ; false s'il est illisible. */
function readMuted() {
  try {
    return localStorage.getItem(SOUND_KEY) === 'off';
  } catch {
    return false;
  }
}

/**
 * Branche les sons sur la page : tic au survol et tintement au clic des éléments de
 * SOUND_TARGETS, bouton toggle pour couper ou remettre le son.
 *
 * @param {HTMLButtonElement} toggle bouton « Son » de la barre du haut
 */
function initSound(toggle) {
  const label = toggle.querySelector('.sound-label');
  const refresh = () => {
    toggle.setAttribute('aria-pressed', String(!soundState.muted));
    label.textContent = soundState.muted ? 'Son coupé' : 'Son activé';
  };
  soundState.muted = readMuted();
  refresh();
  toggle.addEventListener('click', () => {
    soundState.muted = !soundState.muted;
    try {
      localStorage.setItem(SOUND_KEY, soundState.muted ? 'off' : 'on');
    } catch {
      /* Stockage refusé (navigation privée) : le réglage vaut pour la page ouverte. */
    }
    refresh();
    playSound('select');
  });
  document.addEventListener('pointerover', event => {
    const target = event.target.closest?.(SOUND_TARGETS) || null;
    if (target === soundState.hovered) return;
    soundState.hovered = target;
    if (target) playSound('hover');
  });
  document.addEventListener('click', event => {
    const target = event.target.closest?.(SOUND_TARGETS);
    if (target && target !== toggle) playSound('select');
  });
}
