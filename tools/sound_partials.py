"""Tire des bruits d'origine les partiels des sons de la maquette « Système ».

Chaque enregistrement de « sound effects/ » est analysé (spectre à court terme, suivi des
partiels les plus forts), puis réduit à des sinusoïdes (fréquence, enveloppe en peu de
points) et, pour ce qu'elles ne rendent pas (souffles, chocs), à des bandes de bruit
filtré avec leur enveloppe, mesurées sur une fenêtre courte pour garder les attaques. Le
résultat, écrit dans public/js/sound-data.js, ne contient aucun échantillon : la
page resynthétise un son proche de l'original, jamais identique. Avec un chemin en
argument, le script y écrit aussi les niveaux par bande de chaque extrait d'origine, à
deux finesses (REFERENCE_FRAMES), pour contrôler le rendu de la page.

Usage, depuis la racine du dépôt : python3 -I tools/sound_partials.py [reference.json]
"""

import array
import cmath
import functools
import json
import math
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT / 'sound effects'
OUTPUT = ROOT / 'public' / 'js' / 'sound-data.js'
RATE = 44100
# Fenêtre et pas (échantillons) du suivi des partiels.
TONAL_SIZE = 2048
TONAL_HOP = 256
# Étages de bruit (fenêtre, pas, de, à (Hz), bandes) : le grave demande une fenêtre longue,
# le reste une fenêtre courte qui garde les attaques.
NOISE_TIERS = [(2048, 256, 80, 160, 3), (512, 128, 160, 14000, 16)]
# Finesses (fenêtre, pas) des niveaux de contrôle : spectre d'abord, attaques ensuite.
REFERENCE_FRAMES = {'coarse': (2048, 512), 'fine': (512, 128)}
PEAKS_PER_FRAME = 40
PEAK_FLOOR_DB = -48
MATCH_RATIO = 0.025
MAX_GAP_SECONDS = 0.025
MIN_TRACK_SECONDS = 0.07
TRACKS_KEPT = 24
# Filtres passe-bande en série par bande de bruit, repris par sound.js.
NOISE_STAGES = 2
# Part de la largeur d'une bande gardée par chaque filtre de la série.
STAGE_WIDTH = 0.644
NOISE_FLOOR_DB = -50
FIT_ROUNDS = 40
TRIM_STEP = 512
ENVELOPE_TOLERANCE = 0.05
TRIM_START_DB = -38
TRIM_END_DB = -44
TARGET_LEVEL = 0.5
FADE_IN = 0.006
FADE_OUT = 0.05
BANDS = 28
# Fenêtre et pas (échantillons) du retrait d'un bruit de fond, et part retirée de son profil.
SUBTRACT_SIZE = 1024
SUBTRACT_HOP = 256
OVER_SUBTRACT = 6.0
FFMPEG_TIMEOUT = 60

# Son de la maquette : fichier d'origine, début et fin (s, après rognage du silence ;
# None : jusqu'au bout) et niveau relatif.
SOUNDS = {
    'unlock': ('solo_leveling_level_up_once.mp3', 0.0, None, 1.0),
    'select': ('solo_leveling_level_up_once.mp3', 0.12, 0.42, 0.45),
    'open': ('window_open_and_text_update.mp3', 0.0, None, 1.0),
    'close': ('solo_leveling_menu_pop.mp3', 0.24, 0.8, 0.7),
    'notify': ('System-Notifikason-Solo-Leveling.mp3', 0.0, 2.2, 1.0),
    'store': ('System-Notifikason-Solo-Leveling.mp3', 1.1, 1.9, 0.6),
}
# Fichier dont un bruit de fond se retire : début et fin (s, après rognage du silence) de
# la section où ce bruit est seul ; ce qui la précède est gardé, débarrassé de ce bruit.
BACKGROUNDS = {
    'window_open_and_text_update.mp3': (0.9, 2.1),
}


@functools.lru_cache(maxsize=None)
def window(size):
    """Fenêtre de Hann de size points."""
    return [0.5 - 0.5 * math.cos(2 * math.pi * index / size) for index in range(size)]


def decode(path):
    """Échantillons mono de path (flottants à RATE Hz), décodés par ffmpeg."""
    if not path.is_file():
        raise SystemExit(f'Son d\'origine introuvable : {path}')
    command = [
        'ffmpeg', '-v', 'error', '-i', str(path), '-ac', '1', '-ar', str(RATE),
        '-f', 'f32le', '-',
    ]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            timeout=FFMPEG_TIMEOUT,
            check=False,
        )
    except FileNotFoundError:
        raise SystemExit('ffmpeg est introuvable : installez-le puis relancez.') from None
    except subprocess.TimeoutExpired:
        message = f'ffmpeg n\'a pas fini en {FFMPEG_TIMEOUT} s sur {path.name}.'
        raise SystemExit(message) from None
    if result.returncode != 0 or not result.stdout:
        raise SystemExit(f'ffmpeg a échoué sur {path.name} : {result.stderr.decode().strip()}')
    samples = array.array('f')
    samples.frombytes(result.stdout[:len(result.stdout) // 4 * 4])
    return samples


def fft(values):
    """Transformée de Fourier rapide de values, dont la longueur est une puissance de 2."""
    count = len(values)
    if count == 1:
        return values
    even = fft(values[0::2])
    odd = fft(values[1::2])
    out = [0] * count
    for index in range(count // 2):
        turn = cmath.exp(-2j * math.pi * index / count) * odd[index]
        out[index] = even[index] + turn
        out[index + count // 2] = even[index] - turn
    return out


def spectra(samples, size, hop):
    """Modules du spectre des trames de samples, la trame n centrée sur l'échantillon n × hop.

    Returns:
        Une liste de size // 2 modules par trame, fenêtre de Hann de size points.
    """
    padded = [0.0] * (size // 2) + list(samples) + [0.0] * size
    weights = window(size)
    frames = []
    for start in range(0, len(samples) + 1, hop):
        chunk = padded[start:start + size]
        spectrum = fft([value * weight for value, weight in zip(chunk, weights)])
        frames.append([abs(value) for value in spectrum[:size // 2]])
    return frames


def trimmed(samples):
    """samples sans son silence de tête ni de queue, d'après son niveau par tranche."""
    step = TRIM_STEP
    peak = max((abs(value) for value in samples), default=0.0)
    if peak <= 0:
        raise SystemExit('Son d\'origine vide ou silencieux.')
    levels = []
    for start in range(0, len(samples), step):
        chunk = samples[start:start + step]
        rms = math.sqrt(sum(value * value for value in chunk) / len(chunk))
        levels.append(20 * math.log10(rms / peak + 1e-9))
    first = next(index for index, level in enumerate(levels) if level > TRIM_START_DB)
    last = max(index for index, level in enumerate(levels) if level > TRIM_END_DB)
    return samples[max(0, first - 1) * step:(last + 2) * step]


def decay_rate(powers, times):
    """Pente (par seconde, jamais positive) du logarithme de l'énergie totale des trames."""
    logs = [math.log(sum(row) + 1e-30) for row in powers]
    mean_time = sum(times) / len(times)
    mean_log = sum(logs) / len(logs)
    spread = sum((time - mean_time) ** 2 for time in times)
    slope = sum(
        (time - mean_time) * (level - mean_log)
        for time, level in zip(times, logs)
    ) / spread
    return min(slope, 0.0)


def without_background(samples, start, end):
    """Début de samples débarrassé du bruit de fond qui joue seul de start à end.

    Soustraction spectrale : le spectre moyen du bruit seul, prolongé vers l'arrière selon
    sa décroissance, est retiré OVER_SUBTRACT fois de chaque trame d'avant start.

    Args:
        samples: échantillons de l'enregistrement, silence de tête rogné.
        start: début (s) de la section où le bruit de fond est seul.
        end: fin (s) de cette section.

    Returns:
        Les échantillons d'avant start, sans le bruit de fond.
    """
    size, hop = SUBTRACT_SIZE, SUBTRACT_HOP
    half = size // 2
    weights = window(size)
    padded = [0.0] * size + list(samples[:int(end * RATE)]) + [0.0] * size
    frames = [
        fft([value * weight for value, weight in zip(padded[begin:begin + size], weights)])
        for begin in range(0, len(padded) - size, hop)
    ]
    times = [(number * hop - half) / RATE for number in range(len(frames))]
    alone = [number for number, time in enumerate(times) if start <= time <= end]
    if len(alone) < 2:
        raise SystemExit(f'Section de bruit seul trop courte : de {start} à {end} s.')
    powers = [[abs(value) ** 2 for value in frame[:half + 1]] for frame in frames]
    slope = decay_rate(
        [powers[number] for number in alone],
        [times[number] for number in alone],
    )
    profile = [
        sum(powers[number][index] * math.exp(-slope * times[number]) for number in alone)
        / len(alone)
        for index in range(half + 1)
    ]
    out = [0.0] * len(padded)
    for number, frame in enumerate(frames):
        if times[number] >= start:
            break
        level = OVER_SUBTRACT * math.exp(slope * times[number])
        for index in range(half + 1):
            power = powers[number][index]
            kept = max(power - level * profile[index], 0.0)
            scale = math.sqrt(kept / power) if power else 0.0
            frame[index] *= scale
            if 0 < index < half:
                frame[size - index] *= scale
        restored = fft([value.conjugate() for value in frame])
        for index, value in enumerate(restored):
            out[number * hop + index] += value.real / size / 2
    return out[size:size + int(start * RATE)]


def frame_peaks(spectrum, floor):
    """Pics (fréquence en Hz, amplitude) d'une trame de TONAL_SIZE, les plus forts d'abord."""
    peaks = []
    for index in range(3, len(spectrum) - 1):
        here = spectrum[index]
        if here < floor or here <= spectrum[index - 1] or here < spectrum[index + 1]:
            continue
        left, right = spectrum[index - 1], spectrum[index + 1]
        bend = left - 2 * here + right
        shift = 0.5 * (left - right) / bend if bend else 0.0
        peaks.append(((index + shift) * RATE / TONAL_SIZE, 4 * here / TONAL_SIZE))
    peaks.sort(key=lambda peak: -peak[1])
    return peaks[:PEAKS_PER_FRAME]


def track_partials(frames):
    """Partiels suivis d'une trame à l'autre : listes de (trame, fréquence, amplitude)."""
    floor = max(max(frame) for frame in frames) * 10 ** (PEAK_FLOOR_DB / 20)
    max_gap = MAX_GAP_SECONDS * RATE / TONAL_HOP
    min_frames = MIN_TRACK_SECONDS * RATE / TONAL_HOP
    open_tracks, closed = [], []
    for number, spectrum in enumerate(frames):
        free = list(open_tracks)
        for freq, amp in frame_peaks(spectrum, floor):
            near = [
                track for track in free
                if abs(track[-1][1] - freq) / track[-1][1] < MATCH_RATIO
            ]
            if near:
                track = min(near, key=lambda item: abs(item[-1][1] - freq))
                free.remove(track)
                track.append((number, freq, amp))
            else:
                open_tracks.append([(number, freq, amp)])
        for track in free:
            if number - track[-1][0] > max_gap:
                open_tracks.remove(track)
                closed.append(track)
    closed.extend(open_tracks)
    kept = [track for track in closed if len(track) >= min_frames]
    kept.sort(key=lambda track: -sum(point[2] ** 2 for point in track))
    return kept[:TRACKS_KEPT]


def simplify(points, tolerance):
    """Points (temps, niveau) réduits à ceux écartés de la droite de plus de tolerance."""
    if len(points) < 3:
        return points
    (start_time, start_level), (end_time, end_level) = points[0], points[-1]
    span = (end_time - start_time) or 1e-9
    worst, where = 0.0, 0
    for index in range(1, len(points) - 1):
        time, level = points[index]
        line = start_level + (end_level - start_level) * (time - start_time) / span
        if abs(level - line) > worst:
            worst, where = abs(level - line), index
    if worst <= tolerance:
        return [points[0], points[-1]]
    return simplify(points[:where + 1], tolerance)[:-1] + simplify(points[where:], tolerance)


def describe(track, length):
    """Partiel réduit à [fréquence de départ, d'arrivée, [temps, niveau, ...]]."""
    third = max(1, len(track) // 3)
    median = lambda values: sorted(values)[len(values) // 2]
    start_freq = median([point[1] for point in track[:third]])
    end_freq = median([point[1] for point in track[-third:]])
    frame = TONAL_HOP / RATE
    points = [(max(0.0, track[0][0] * frame - frame), 0.0)]
    measured = track[1:] if track[0][0] == 0 else track
    points += [(number * frame, amp) for number, _, amp in measured]
    points.append((min(length, track[-1][0] * frame + 2 * frame), 0.0))
    top = max(amp for _, _, amp in track)
    return [start_freq, end_freq, simplify(points, ENVELOPE_TOLERANCE * top)]


def faded(points, length):
    """Points d'enveloppe atténués par un fondu d'entrée et de sortie du son."""
    def weight(time):
        """Facteur de fondu (0 à 1) appliqué à l'instant time."""
        return min(1.0, time / FADE_IN if FADE_IN else 1.0, (length - time) / FADE_OUT)

    return [(time, level * max(0.0, weight(time))) for time, level in points]


def level_at(points, time):
    """Niveau d'une enveloppe en points (temps, niveau) à l'instant time."""
    if time <= points[0][0] or time >= points[-1][0]:
        return 0.0
    for (left_time, left), (right_time, right) in zip(points, points[1:]):
        if left_time <= time <= right_time:
            share = (time - left_time) / ((right_time - left_time) or 1e-9)
            return left + (right - left) * share
    return 0.0


def synthesize(partials, length):
    """Échantillons resynthétisés des partiels, pour le contrôle de la sortie."""
    count = int(length * RATE)
    out = [0.0] * count
    for start_freq, end_freq, points in partials:
        first = max(0, int(points[0][0] * RATE))
        last = min(count, int(points[-1][0] * RATE) + 1)
        phase, cursor = 0.0, 0
        for index in range(first, last):
            time = index / RATE
            while cursor < len(points) - 2 and points[cursor + 1][0] < time:
                cursor += 1
            (left_time, left), (right_time, right) = points[cursor], points[cursor + 1]
            share = (time - left_time) / ((right_time - left_time) or 1e-9)
            level = left + (right - left) * min(1.0, max(0.0, share))
            span = (points[-1][0] - points[0][0]) or 1e-9
            glide = (time - points[0][0]) / span
            freq = start_freq + (end_freq - start_freq) * glide
            phase += 2 * math.pi * freq / RATE
            out[index] += level * math.sin(phase)
    return out


def band_edges(count, low=80, high=14000):
    """Bornes (Hz) de count bandes logarithmiques de low à high."""
    return [low * (high / low) ** (index / count) for index in range(count + 1)]


def band_bins(edges, size):
    """Indices (premier, après le dernier) des raies de chaque bande, une raie au moins."""
    bins = [int(edge * size / RATE) for edge in edges]
    return [(low, max(high, low + 1)) for low, high in zip(bins, bins[1:])]


def band_energies(frames, edges, size):
    """Énergie de chaque trame (fenêtre size) dans les bandes edges (somme des modules²)."""
    ranges = band_bins(edges, size)
    return [
        [sum(value * value for value in spectrum[low:high]) for low, high in ranges]
        for spectrum in frames
    ]


def band_levels(samples, size, hop):
    """Niveau en dB, 0 au plus fort et -60 au plancher, de chaque trame dans BANDS bandes."""
    rows = [
        [10 * math.log10(energy + 1e-12) for energy in row]
        for row in band_energies(spectra(samples, size, hop), band_edges(BANDS), size)
    ]
    top = max(max(row) for row in rows)
    return [[max(value - top, -60.0) for value in row] for row in rows]


def filter_power(centre, quality, freq):
    """Gain en puissance, à freq Hz, de NOISE_STAGES passe-bande de Web Audio en série."""
    turn = 2 * math.pi * centre / RATE
    alpha = math.sin(turn) / (2 * quality)
    back = cmath.exp(-2j * math.pi * freq / RATE)
    response = alpha * (1 - back * back) / (
        1 + alpha - 2 * math.cos(turn) * back + (1 - alpha) * back * back
    )
    return abs(response) ** (2 * NOISE_STAGES)


def leak_matrix(filters, edges, size):
    """Énergie qu'un bruit blanc uniforme de gain 1 laisse dans chaque bande, par filtre.

    Args:
        filters: liste de (fréquence centrale, facteur Q) des bandes de bruit.
        edges: bornes (Hz) des bandes d'analyse.
        size: nombre de points de la fenêtre d'analyse.

    Returns:
        Une ligne par bande d'analyse, une colonne par filtre.
    """
    per_bin = (1 / 3) * (3 / 8) * size
    return [
        [
            per_bin * sum(
                filter_power(centre, quality, index * RATE / size)
                for index in range(low, high)
            )
            for centre, quality in filters
        ]
        for low, high in band_bins(edges, size)
    ]


def fit_powers(target, leak, reach):
    """Puissances positives des filtres dont la somme des fuites approche target.

    Args:
        target: énergie à rendre dans chaque bande d'analyse.
        leak: matrice de leak_matrix.
        reach: somme de chaque colonne de leak.

    Returns:
        Une puissance par filtre, par mises à jour multiplicatives (divergence de
        Kullback-Leibler).
    """
    count = len(target)
    powers = [target[index] / leak[index][index] for index in range(count)]
    for _ in range(FIT_ROUNDS):
        ratios = [
            target[row] / (sum(leak[row][col] * powers[col] for col in range(count)) + 1e-30)
            for row in range(count)
        ]
        pulls = [
            sum(leak[row][col] * ratios[row] for row in range(count))
            for col in range(count)
        ]
        powers = [power * pull / total for power, pull, total in zip(powers, pulls, reach)]
    return powers


def noise_bands(samples, tonal, tier):
    """Bandes de bruit d'un étage, qui rendent ce que les partiels ne rendent pas.

    Args:
        samples: échantillons de l'extrait d'origine.
        tonal: échantillons de la resynthèse des seuls partiels.
        tier: entrée de NOISE_TIERS.

    Returns:
        Liste de [fréquence centrale (Hz), facteur Q, points (temps, niveau)], le niveau
        étant le gain d'un bruit blanc uniforme passé dans NOISE_STAGES filtres passe-bande.
    """
    size, hop, low_edge, high_edge, count = tier
    edges = band_edges(count, low_edge, high_edge)
    full = band_energies(spectra(samples, size, hop), edges, size)
    covered = band_energies(spectra(tonal, size, hop), edges, size)
    filters = [
        (math.sqrt(low * high), math.sqrt(low * high) / ((high - low) * STAGE_WIDTH))
        for low, high in zip(edges, edges[1:])
    ]
    leak = leak_matrix(filters, edges, size)
    reach = [sum(row[col] for row in leak) for col in range(count)]
    floor = max(max(row) for row in full) * 10 ** (NOISE_FLOOR_DB / 10)
    frame = hop / RATE
    levels = []
    for number, row in enumerate(full):
        rest = [
            max(energy - covered[number][index], 0.0)
            for index, energy in enumerate(row)
        ]
        rest = [energy if energy > floor else 0.0 for energy in rest]
        powers = fit_powers(rest, leak, reach) if any(rest) else [0.0] * count
        levels.append([math.sqrt(power) for power in powers])
    bands = []
    for index, (centre, quality) in enumerate(filters):
        points = [(number * frame, row[index]) for number, row in enumerate(levels)]
        top = max(level for _, level in points)
        if top <= 0:
            continue
        points = [(0.0, 0.0)] + points[1:] + [(points[-1][0] + frame, 0.0)]
        bands.append([centre, quality, simplify(points, ENVELOPE_TOLERANCE * top)])
    return bands


def flat(points, scale):
    """Points (temps, niveau) mis à plat [temps, niveau, ...], niveaux multipliés par scale."""
    return [
        value for time, level in points
        for value in (round(time, 3), round(level * scale, 4))
    ]


def build(name, source, start, end, gain):
    """Description du son name et niveaux par bande de son extrait d'origine.

    Returns:
        (description, niveaux) : description porte la durée, les partiels et les bandes
        de bruit, normalisés sur le pic de l'extrait puis multipliés par gain ; niveaux
        porte, par finesse de REFERENCE_FRAMES, les niveaux par bande de l'extrait.
    """
    whole = source
    stop = len(whole) if end is None else min(len(whole), int(end * RATE))
    samples = whole[int(start * RATE):stop]
    if len(samples) < TONAL_SIZE:
        raise SystemExit(f'Extrait trop court pour « {name} » : {len(samples)} échantillons.')
    length = len(samples) / RATE
    tracks = track_partials(spectra(samples, TONAL_SIZE, TONAL_HOP))
    partials = [describe(track, length) for track in tracks]
    if not partials:
        raise SystemExit(f'Aucun partiel trouvé pour « {name} ».')
    partials = [[low, high, faded(points, length)] for low, high, points in partials]
    tonal = synthesize(partials, length)
    noise = [
        [centre, quality, faded(points, length)]
        for tier in NOISE_TIERS
        for centre, quality, points in noise_bands(samples, tonal, tier)
    ]
    peak = max(abs(value) for value in samples)
    scale = TARGET_LEVEL * gain / peak
    count = sum(len(entry[2]) for entry in partials + noise)
    print(f'{name:7} {length:5.2f} s, {len(partials):2} partiels, {len(noise):2} bandes de '
          f'bruit, {count:4} points')
    description = {
        'length': round(length, 3),
        'partials': [
            [round(low, 1), round(high, 1), flat(points, scale)]
            for low, high, points in partials
        ],
        'noise': [
            [round(centre, 1), round(quality, 2), flat(points, scale)]
            for centre, quality, points in noise
        ],
    }
    levels = {
        label: band_levels(samples, size, hop)
        for label, (size, hop) in REFERENCE_FRAMES.items()
    }
    return description, levels


def main():
    """Écrit OUTPUT d'après SOURCE_DIR, et les niveaux d'origine si un chemin est donné."""
    sources = {}
    sounds = {}
    reference = {}
    for name, (file_name, start, end, gain) in SOUNDS.items():
        if file_name not in sources:
            sources[file_name] = trimmed(decode(SOURCE_DIR / file_name))
            if file_name in BACKGROUNDS:
                section = BACKGROUNDS[file_name]
                sources[file_name] = without_background(sources[file_name], *section)
        sounds[name], reference[name] = build(name, sources[file_name], start, end, gain)
    header = (
        "'use strict';\n\n"
        "/*\n"
        " * Maquette « Système » : partiels et bandes de bruit des sons de l'interface,\n"
        " * générés par tools/sound_partials.py d'après la mesure des bruits d'origine.\n"
        " * Ne pas modifier à la main. Par son : durée (s), partiels [fréquence de départ,\n"
        " * d'arrivée (Hz), [temps (s), niveau, ...]] et bandes de bruit [fréquence centrale\n"
        " * (Hz), Q, [temps, niveau, ...]], chaque bande passant par SOUND_NOISE_STAGES\n"
        " * filtres en série. Aucun échantillon enregistré : sound.js resynthétise.\n"
        " */\n\n"
        f"const SOUND_NOISE_STAGES = {NOISE_STAGES};\n"
    )
    body = json.dumps(sounds, separators=(',', ':'))
    OUTPUT.write_text(f'{header}const SOUND_PARTIALS = {body};\n', encoding='utf-8')
    print(f'Écrit : {OUTPUT.relative_to(ROOT)} ({OUTPUT.stat().st_size} octets)')
    if len(sys.argv) > 1:
        rounded = {
            name: {
                label: [[round(value, 1) for value in row] for row in rows]
                for label, rows in levels.items()
            }
            for name, levels in reference.items()
        }
        text = json.dumps(rounded, separators=(',', ':'))
        Path(sys.argv[1]).write_text(text, encoding='utf-8')
        print(f'Écrit : {sys.argv[1]}')


if __name__ == '__main__':
    sys.setrecursionlimit(10000)
    main()
