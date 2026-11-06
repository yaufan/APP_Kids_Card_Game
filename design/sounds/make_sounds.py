"""小卡認天下 (picture cards): every sound in the app, made here from sine
waves and noise, so every one is ours: nothing recorded, nothing downloaded,
and both tunes written for this app.

- Music (WAV, 16,000 Hz): a light tune for playing with the cards (kalimba,
  celesta, a soft marimba) and a slow lullaby for the rest screen (a music
  box over a felt piano). Each tune is as long as its bars, and what still
  rings at the end is carried round to the start, so it loops without a seam.
- Short sounds and each card's own sound, `say_<card id>` (WAV, 22,050 Hz).
- For children from 2: calm, warm and soft. No buzzers, nothing sudden; the
  animals are cute rather than real (the lion's roar is a friendly "rawr").
- Animal voices are a buzz through formant filters, as in 畫畫小鎮, 字母寵物
  and 動物小餐廳; horns, sirens and engines are tones and noise.
- Every random choice uses a fixed seed, so each run writes the same files.
- Every short sound is set to the same loudness as heard by the ear through
  a phone speaker (A-weighting, and nothing under 250 Hz), plus or minus a
  few dB where it should sit softer, with its peak at most 0.72. Low sounds
  (a cow, a boat's horn, a rocket) get a little of their own overtones added
  (`carry`), so a phone, which hardly plays anything low, still carries them.

The helpers (t_of, env, sweep, decay, lowpass, bandpass, norm, partial,
bell, marimba, place, tune_loop, resonator, voice, ease, glide, bubble,
above, spans, melody, root_of, third_of, kalimba, pluck_bass,
metal, woodblock, shaker, noise_through, tidy, write, report, read, preview)
come from 動物小餐廳's design/sounds/make_sounds.py; music_box_note,
soft_piano and harp from 字母寵物's. The animal calls, sirens, the horns,
the jet, the helicopter, Für Elise (Beethoven, 1810: the garbage truck's
tune) and the excavator are adapted from 畫畫小鎮's
docs/design/sounds/make_sounds.py. The celesta, the warm chime, carry,
round_off, highpass, the loudness balancing and the other sounds are new.

    python3 design/sounds/make_sounds.py                  # writes app/assets/sounds/*.wav
    python3 design/sounds/make_sounds.py preview OUT.m4a  # and a listening preview
"""
import json
import pathlib
import subprocess
import sys
import wave

import numpy as np
from scipy.signal import lfilter, resample_poly

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "app" / "assets" / "sounds"
CARDS = ROOT / "design" / "cards.json"
SR = 22050       # short sounds and the cards' sounds
LOOP_SR = 16000  # music
LIMIT = 4_000_000  # bytes, the whole folder

# Notes (Hz), with flats as well as sharps.
NOTE = {f"{n}{o}": 440 * 2 ** ((k - 9) / 12 + o - 4)
        for o in range(1, 9) for k, n in enumerate("C C# D D# E F F# G G# A A# B".split())}
for _o in range(1, 9):
    for _flat, _sharp in (("Db", "C#"), ("Eb", "D#"), ("Gb", "F#"), ("Ab", "G#"), ("Bb", "A#")):
        NOTE[f"{_flat}{_o}"] = NOTE[f"{_sharp}{_o}"]


# ---------------------------------------------------------------- helpers (from 動物小餐廳 and 字母寵物)


def t_of(dur, sr=SR):
    return np.arange(int(dur * sr)) / sr


def env(n, attack=0.005, release=0.05, sr=SR):
    """Up quickly, down smoothly: no clicks at either end."""
    e = np.ones(n)
    a, r = max(1, min(n, int(attack * sr))), max(1, min(n, int(release * sr)))
    e[:a] = np.linspace(0, 1, a) ** 2
    e[-r:] *= np.linspace(1, 0, r) ** 2
    return e


def sweep(f, sr=SR):
    """A sine whose frequency follows the array [f] (Hz per sample)."""
    return np.sin(2 * np.pi * np.cumsum(f) / sr)


def decay(n, tau, sr=SR):
    return np.exp(-np.arange(n) / (tau * sr))


def lowpass(x, cutoff, sr=SR):
    spec = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(len(x), 1 / sr)
    spec *= 1 / (1 + (freqs / cutoff) ** 4)
    return np.fft.irfft(spec, len(x))


def bandpass(x, lo, hi, sr=SR):
    spec = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(len(x), 1 / sr)
    spec *= 1 / (1 + (lo / np.maximum(freqs, 1)) ** 4) / (1 + (freqs / hi) ** 4)
    return np.fft.irfft(spec, len(x))


def norm(x):
    return x / max(1e-9, np.abs(x).max())


def partial(freq, t, sr):
    """A sine at [freq], or silence if it is too high for [sr] (it would fold
    back down as a wrong note)."""
    return np.sin(2 * np.pi * freq * t) if freq < 0.45 * sr else np.zeros_like(t)


def bell(freq, dur=0.5, sr=SR, bright=1.0):
    """A soft glockenspiel note: a few partials, the high ones dying first."""
    t = t_of(dur, sr)
    x = (partial(freq, t, sr) * np.exp(-t / (dur * 0.35))
         + 0.35 * bright * partial(freq * 2.76, t, sr) * np.exp(-t / (dur * 0.12))
         + 0.15 * bright * partial(freq * 5.4, t, sr) * np.exp(-t / (dur * 0.06)))
    return x * env(len(t), 0.002, 0.03, sr)


def marimba(freq, dur=0.5, sr=SR):
    t = t_of(dur, sr)
    x = partial(freq, t, sr) * np.exp(-t / (dur * 0.3)) + 0.2 * partial(freq * 4, t, sr) * np.exp(-t / (dur * 0.05))
    return x * env(len(t), 0.003, 0.03, sr)


def place(total, parts, sr=SR):
    """[parts]: (start seconds, signal) mixed into [total] seconds."""
    out = np.zeros(int(total * sr))
    for start, sig in parts:
        i = int(start * sr)
        j = min(len(out), i + len(sig))
        out[i:j] += sig[: j - i]
    return out


def tune_loop(seconds, notes, sr=LOOP_SR):
    """[notes]: (start seconds, signal); what rings past [seconds] wraps to the start."""
    n = int(round(seconds * sr))
    tail = max(len(sig) + int(start * sr) for start, sig in notes) - n
    out = np.zeros(n + max(0, tail))
    for start, sig in notes:
        i = int(start * sr)
        out[i:i + len(sig)] += sig
    loop = out[:n].copy()
    if tail > 0:
        loop[:tail] += out[n:]
    return loop


def resonator(x, freq, bw, sr=SR, block=64):
    """A two-pole resonance at [freq] Hz (a number, or one per sample, for a
    sound that changes) of bandwidth [bw] Hz."""
    freq = np.broadcast_to(np.asarray(freq, dtype=float), x.shape)
    y, zi = np.zeros_like(x), np.zeros(2)
    r = np.exp(-np.pi * bw / sr)
    for i in range(0, len(x), block):
        th = 2 * np.pi * freq[i] / sr
        y[i:i + block], zi = lfilter([1 - r], [1, -2 * r * np.cos(th), r * r], x[i:i + block], zi=zi)
    return y


def voice(f0, formants, rng, breath=0.03, rough=0.0, sr=SR):
    """A voice at pitch [f0] (Hz per sample) through [formants]: (Hz or Hz
    per sample, bandwidth, gain). [rough] jitters the pitch, for a growl."""
    n = len(f0)
    if rough:
        f0 = f0 * (1 + rough * lowpass(rng.standard_normal(n), 60, sr) * 3)
    buzz = 2 * (np.cumsum(f0) / sr % 1) - 1 + breath * rng.standard_normal(n)
    out = np.zeros(n)
    for f, bw, gain in formants:
        y = resonator(buzz, f, bw, sr)
        out += gain * y / max(1e-9, np.abs(y).max())
    return lowpass(out, 3800, sr)  # soft, not a kazoo


def ease(u):
    """0 to 1, smoothly, over u in 0..1."""
    u = np.clip(u, 0, 1)
    return u * u * (3 - 2 * u)


def glide(t, *points):
    """A value that moves smoothly between (time, value) [points]."""
    ts, vs = zip(*points)
    out = np.interp(t, ts, vs)
    return lowpass(out - out.mean(), 25) + out.mean() if len(t) > 64 else out


def bubble(rng, sr=SR, low=(300, 550), rise=(2.2, 3.2), dur=(0.04, 0.08)):
    """One little bubble: a quick rising blip that starts and ends at zero."""
    d = rng.uniform(*dur)
    t = t_of(d, sr)
    f0 = rng.uniform(*low)
    f = np.geomspace(f0, f0 * rng.uniform(*rise), len(t))
    return sweep(f, sr) * np.sin(np.pi * t / d)


def above(name, low):
    """The note called [name] (no octave) at or just above the note [low]."""
    for o in range(1, 9):
        if NOTE[f"{name}{o}"] >= NOTE[low] * 0.999:
            return f"{name}{o}"
    raise ValueError(name)


def spans(bars, beats_per_bar):
    """Bars like "F" or "Gm-C" (two chords, half a bar each) -> (beat, length in beats, chord)."""
    out = []
    for i, bar in enumerate(bars):
        parts = bar.split("-")
        each = beats_per_bar / len(parts)
        out += [(i * beats_per_bar + k * each, each, c) for k, c in enumerate(parts)]
    return out


def melody(tune, beat, start=0.0, swing=0.0, bars=None, beats_per_bar=4):
    """[tune]: (note or None for a rest, beats) one after another ->
    (seconds, note, seconds long). [swing] (in beats) delays each note that
    falls halfway through a beat, for a lilt. [bars]: check the tune fills them."""
    if bars is not None:
        assert abs(sum(b for _, b in tune) - bars * beats_per_bar) < 1e-9, tune
    out, b = [], 0.0
    for name, beats in tune:
        if name:
            late = swing if abs(b % 1 - 0.5) < 1e-6 else 0.0
            out.append((start + (b + late) * beat, name, (beats - late) * beat))
        b += beats
    return out


def root_of(chord):
    return chord[:2] if len(chord) > 1 and chord[1] in "#b" else chord[0]


def third_of(chord):
    """Semitones from the root to the third: 3 for a minor chord, else 4."""
    rest = chord[len(root_of(chord)):]
    return 3 if rest.startswith("m") and not rest.startswith("maj") else 4


def kalimba(freq, dur=1.8, sr=LOOP_SR):
    """A thumb piano's tine: a round note and a quick metal tick high above it
    (a tine's second mode is about 6.3 times the first)."""
    t = t_of(dur, sr)
    x = (partial(freq, t, sr) * np.exp(-t / (dur * 0.3))
         + 0.28 * partial(freq * 6.27, t, sr) * np.exp(-t / 0.025)
         + 0.08 * partial(freq * 2, t, sr) * np.exp(-t / (dur * 0.08)))
    return x * env(len(t), 0.001, 0.08, sr)


def pluck_bass(freq, dur=1.0, sr=LOOP_SR):
    """A plucked double bass: round, short, warm."""
    t = t_of(dur, sr)
    x = (partial(freq, t, sr) * np.exp(-t / (dur * 0.35))
         + 0.45 * partial(freq * 2, t, sr) * np.exp(-t / (dur * 0.15))
         + 0.15 * partial(freq * 3, t, sr) * np.exp(-t / (dur * 0.08)))
    return x * env(len(t), 0.006, 0.08, sr)


def metal(freq, dur, sr=SR, ratios=(1, 1.59, 2.14, 2.65, 3.15), amps=(1, .6, .45, .3, .2), taus=(.5, .3, .2, .15, .1)):
    """A small metal ting (a bell, a coin): partials that are not
    whole-number multiples; [taus] are fractions of [dur]."""
    t = t_of(dur, sr)
    x = sum(a * partial(freq * r, t, sr) * np.exp(-t / (dur * k)) for r, a, k in zip(ratios, amps, taus))
    return x * env(len(t), 0.0008, 0.03, sr)


def woodblock(freq, sr=LOOP_SR, dur=0.09):
    t = t_of(dur, sr)
    x = partial(freq, t, sr) * np.exp(-t / 0.018) + 0.45 * partial(freq * 2.3, t, sr) * np.exp(-t / 0.007)
    return x * env(len(t), 0.0008, 0.02, sr)


def shaker(rng, sr=LOOP_SR, dur=0.06):
    n = int(dur * sr)
    return norm(bandpass(rng.standard_normal(n), 3000, 7000, sr)) * env(n, 0.006, dur * 0.8, sr)


def noise_through(rng, centre, bw, n):
    """Noise through a resonance that can move: the voice of air and water."""
    return norm(resonator(rng.standard_normal(n), centre, bw))


def music_box_note(freq, dur, sr=LOOP_SR, bright=1.0):
    """A music box's comb: bright at first, then a long soft ring."""
    t = t_of(dur, sr)
    x = (partial(freq, t, sr) * np.exp(-t / 0.9)
         + 0.4 * bright * partial(freq * 3.0, t, sr) * np.exp(-t / 0.18)
         + 0.18 * bright * partial(freq * 5.2, t, sr) * np.exp(-t / 0.06))
    return x * env(len(t), 0.002, 0.08, sr)


def soft_piano(freq, dur=2.5, sr=LOOP_SR):
    """A felt piano: a marimba's warm knock and a bell's soft ring, blended,
    over a plain tone that rings a little longer."""
    t = t_of(dur, sr)
    body = (partial(freq, t, sr) * np.exp(-t / (dur * 0.32))
            + 0.25 * partial(freq * 2, t, sr) * np.exp(-t / (dur * 0.12)))
    x = 0.45 * marimba(freq, dur, sr) + 0.3 * bell(freq, dur, sr, bright=0.25) + 0.5 * body
    return x * env(len(t), 0.006, 0.08, sr)


def harp(freq, dur=1.6, sr=LOOP_SR, bright=1.0):
    """A plucked harp string: whole-number harmonics, the high ones fading first."""
    t = t_of(dur, sr)
    x = np.zeros_like(t)
    for k, a in ((1, 1.0), (2, 0.5), (3, 0.22), (4, 0.1), (5, 0.05)):
        x += (a if k == 1 else a * bright) * partial(freq * k, t, sr) * np.exp(-t / (dur * 0.36 / k ** 0.8))
    return x * env(len(t), 0.004, 0.06, sr)


def triangle(freq, dur, sr=SR):
    t = t_of(dur, sr)
    return 2 / np.pi * np.arcsin(np.sin(2 * np.pi * freq * t))


# ---------------------------------------------------------------- new helpers


def highpass(x, cutoff, sr=SR):
    spec = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(len(x), 1 / sr)
    spec *= 1 / (1 + (cutoff / np.maximum(freqs, 1e-3)) ** 4)
    return np.fft.irfft(spec, len(x))


def carry(x, amount=0.3, lo=500, hi=3000, drive=2.5, sr=SR):
    """Phone speakers hardly play anything under about 300 Hz. For a low
    sound, add its own overtones (a soft saturation of it, kept to [lo]..[hi]
    Hz): a phone plays those, and the ear still hears the low note."""
    peak = max(1e-9, np.abs(x).max())
    over = bandpass(np.tanh(drive * x / peak), lo, hi, sr)
    return x + amount * peak * norm(over)


def round_off(x, drive=2.0):
    """Round off the tallest peaks (a soft saturation), so a sound made of
    quick hits can be as loud as the others without going over the peak."""
    return np.tanh(drive * norm(x)) / np.tanh(drive)


def celesta(freq, dur=1.0, sr=LOOP_SR):
    """A celesta: a felt hammer on a small steel bar over a wooden box. A
    sweet, round tone with a little of its octave, and a soft tick."""
    t = t_of(dur, sr)
    x = (partial(freq, t, sr) * np.exp(-t / (dur * 0.3))
         + 0.25 * partial(freq * 2, t, sr) * np.exp(-t / (dur * 0.12))
         + 0.06 * partial(freq * 4.1, t, sr) * np.exp(-t / 0.02))
    return x * env(len(t), 0.0015, 0.05, sr)


def chime(freq, dur, sr=SR):
    """A soft, warm bell: whole-number partials (no glockenspiel clang), two
    tones a hair apart so it shimmers as it rings."""
    t = t_of(dur, sr)
    x = ((partial(freq, t, sr) + 0.5 * partial(freq * 1.003, t, sr)) * np.exp(-t / (dur * 0.38))
         + 0.28 * partial(freq * 2.0, t, sr) * np.exp(-t / (dur * 0.16))
         + 0.1 * partial(freq * 3.01, t, sr) * np.exp(-t / (dur * 0.07)))
    return x * env(len(t), 0.003, 0.08, sr)


def a_weight(x, sr):
    """[x] as the ear hears it out of a phone: A-weighting (the ear is less
    sensitive to low and very high sounds) and nothing under about 250 Hz."""
    spec = np.fft.rfft(x)
    f2 = np.fft.rfftfreq(len(x), 1 / sr) ** 2
    ra = 12194 ** 2 * f2 ** 2 / ((f2 + 20.6 ** 2) * np.sqrt((f2 + 107.7 ** 2) * (f2 + 737.9 ** 2)) * (f2 + 12194 ** 2))
    phone = 1 / (1 + (250 ** 2 / np.maximum(f2, 1e-6)) ** 2)
    return np.fft.irfft(spec * ra * 1.2589 * phone, len(x))


def loudness(x, sr):
    """How loud [x] sounds, roughly, in dB: the weighted power in 200 ms
    windows (the ear adds up about that long, so a click sounds softer than
    a note as loud), over the windows within 20 dB of the loudest one."""
    y = a_weight(np.asarray(x, dtype=np.float64), sr) ** 2
    w, hop = int(0.2 * sr), int(0.025 * sr)
    y = np.concatenate([y, np.zeros(max(0, w - len(y)))])
    c = np.concatenate([[0], np.cumsum(y)])
    e = (c[w::hop] - c[:len(c) - w:hop]) / w
    return 10 * np.log10(max(1e-12, np.mean(e[e >= e.max() * 0.01])))


# ---------------------------------------------------------------- music


def music_play():
    """Playing with the cards: light and gentle, in F. A kalimba sings the
    tune; in the second half a celesta sings along an octave up. A soft
    marimba walks through each chord, a plucked bass holds it, a shaker and a
    wood click tick along very softly. A little celesta run at the end of each
    half: up, then down to the start."""
    beat = 0.58
    bars = ["F", "Dm", "Bb", "C", "F", "Am", "Bb-C", "F"]
    tune = [("C5", .5), ("F5", .5), ("A5", 1), ("G5", .5), ("F5", .5), ("A5", 1),
            ("D5", 1), ("F5", 1), ("A5", 2),
            ("Bb5", 1), ("A5", .5), ("G5", .5), ("F5", 1), ("D5", 1),
            ("E5", 1), ("C5", 1), ("G5", 2),
            ("C5", .5), ("F5", .5), ("A5", 1), ("G5", .5), ("F5", .5), ("C6", 1),
            ("C6", 1), ("A5", 1), ("E5", 2),
            ("D5", 1), ("F5", 1), ("E5", 1), ("G5", 1),
            ("F5", 3), (None, 1)]
    notes = []
    for at, n, d in melody(tune, beat, bars=8):
        notes.append((at, 0.6 * kalimba(NOTE[n], max(1.4, d + 0.8))))
        if at >= 16 * beat - 1e-9:  # the second half: the celesta sings along
            notes.append((at, 0.16 * celesta(NOTE[n] * 2, 0.9)))
    for b, n in ((14.5, "C6"), (15, "E6"), (15.5, "G6"), (30, "C7"), (30.5, "A6"), (31, "F6"), (31.5, "C6")):
        notes.append((b * beat, 0.2 * celesta(NOTE[n], 1.0)))
    for b, length, chord in spans(bars, 4):
        r = NOTE[above(root_of(chord), "G3")]
        steps = [0, 7, 12 + third_of(chord), 7][:int(length)]
        for k, s in enumerate(steps):
            notes.append(((b + k) * beat, (0.2 if k == 0 else 0.14) * marimba(r * 2 ** (s / 12), 0.55, LOOP_SR)))
        bass = NOTE[above(root_of(chord), "E2")]
        notes.append((b * beat, 0.24 * pluck_bass(bass, 1.1)))
        if length == 4:
            fifth = bass * 2 ** (7 / 12)
            notes.append(((b + 2) * beat, 0.17 * pluck_bass(fifth / 2 if fifth > NOTE["D3"] else fifth, 0.9)))
    rng = np.random.default_rng(101)
    beats = len(bars) * 4
    for b in range(beats):
        notes.append(((b + 0.5) * beat, 0.035 * shaker(rng)))
        if b % 2:
            notes.append((b * beat, 0.05 * woodblock(1300)))
    x = tune_loop(beats * beat, notes)
    return lowpass(x, 4500, LOOP_SR)


def music_rest():
    """The rest screen: a slow lullaby in G, three beats a bar. A music box
    sings; a felt piano rocks up and down under it; a plucked bass and a
    warm hum hold each chord."""
    beat = 0.75
    bars = ["G", "Em", "C", "D", "G", "Em", "C-D", "G"]
    tune = [("B5", 2), ("A5", 1),
            ("G5", 2), ("E5", 1),
            ("E5", 1), ("G5", 1), ("C6", 1),
            ("A5", 3),
            ("B5", 2), ("D6", 1),
            ("B5", 2), ("G5", 1),
            ("A5", 1), ("G5", 1), ("F#5", 1),
            ("G5", 3)]
    notes = [(at, 0.7 * music_box_note(NOTE[n], 2.6, bright=0.45)) for at, n, _ in melody(tune, beat, bars=8, beats_per_bar=3)]
    for b, length, chord in spans(bars, 3):
        root = root_of(chord)
        r = NOTE[above(root, "G3")]
        t3 = 12 + third_of(chord)
        for k, s in enumerate([0, 7, 12, t3, 12, 7][:int(round(length * 2))]):
            notes.append(((b + k / 2) * beat, (0.2 if k == 0 else 0.12) * soft_piano(r * 2 ** (s / 12), 1.6)))
        notes.append((b * beat, 0.2 * pluck_bass(NOTE[above(root, "E2")], 2.0)))
        # the hum: the chord held, swelling in and out, two tones a hair apart
        d = length * beat + 1.0
        t = t_of(d, LOOP_SR)
        swell = np.sin(np.pi * t / d) ** 2
        tones = [r, r * 2 ** (third_of(chord) / 12), r * 2 ** (7 / 12)]
        hum = sum(np.sin(2 * np.pi * f * t) + np.sin(2 * np.pi * f * 1.002 * t) for f in tones)
        notes.append((b * beat, 0.03 * hum * swell))
    x = tune_loop(len(bars) * 3 * beat, notes)
    return lowpass(x, 2800, LOOP_SR)


MUSIC = {
    "music_play": (music_play, 0.21),
    "music_rest": (music_rest, 0.19),
}


# ---------------------------------------------------------------- the app's own sounds


def flip():
    """A card turning over: a soft papery whoosh, and a tiny flap as it lands."""
    rng = np.random.default_rng(201)
    dur = 0.28
    t = t_of(dur)
    n = len(t)
    shape = np.interp(t, [0, 0.13, dur], [0, 1, 0]) ** 1.6
    paper = norm(bandpass(rng.standard_normal(n), 900, 6000)) * (1 + 0.4 * norm(lowpass(rng.standard_normal(n), 40)))
    swoosh = noise_through(rng, np.interp(t, [0, 0.13, dur], [1100, 2500, 1400]), 900, n)
    t2 = t_of(0.06)
    flap = (0.6 * norm(lowpass(rng.standard_normal(len(t2)), 1200)) * np.exp(-t2 / 0.012)
            + 0.4 * partial(430, t2, SR) * np.exp(-t2 / 0.015)) * env(len(t2), 0.001, 0.02)
    return place(0.36, [(0, (0.55 * paper + 0.45 * swoosh) * shape), (0.25, 0.4 * flap)])


def tap():
    """A button: a soft wooden tok."""
    t = t_of(0.07)
    x = (partial(980, t, SR) * np.exp(-t / 0.014) + 0.35 * partial(2350, t, SR) * np.exp(-t / 0.005)
         + 0.15 * partial(3900, t, SR) * np.exp(-t / 0.002))
    return x * env(len(t), 0.0008, 0.02)


def right():
    """A right answer: a warm, happy chime. A marimba goes up C-E-G with a
    kalimba, and lands on a kalimba C with a soft harp chord and a bell."""
    parts = []
    for k, n in enumerate(["C5", "E5", "G5"]):
        parts += [(0.085 * k, 0.5 * marimba(NOTE[n], 0.4)), (0.085 * k, 0.3 * kalimba(NOTE[n], 0.5, SR))]
    land = 0.27
    parts += [(land, 0.6 * kalimba(NOTE["C6"], 1.1, SR)), (land, 0.35 * marimba(NOTE["C6"], 0.8)),
              (land, 0.18 * bell(NOTE["E6"] * 2, 0.6, bright=0.3))]
    parts += [(land + 0.012 * k, 0.22 * harp(NOTE[n], 1.0, SR, bright=0.5)) for k, n in enumerate(["C4", "E4", "G4", "C5"])]
    return lowpass(place(1.3, parts), 6500)


def try_again():
    """Not that one: a very soft, friendly "hm-hm?". Two round notes going
    up, the second lifting a little at the end like a question. Never a
    buzzer, never down."""
    def note(f0, f1, dur):
        t = t_of(dur)
        f = np.interp(t, [0, dur * 0.55, dur], [f0, f0, f1])
        ph = 2 * np.pi * np.cumsum(f) / SR
        return (np.sin(ph) + 0.12 * np.sin(2 * ph) + 0.03 * np.sin(3 * ph)) * env(len(t), 0.03, dur * 0.45)
    x = place(0.58, [(0, 0.85 * note(NOTE["E5"], NOTE["E5"], 0.15)), (0.19, note(NOTE["G5"], NOTE["A5"], 0.34))])
    return lowpass(x, 2200)


def next_card():
    """The next card: a gentle slide across, a soft whoosh with a little
    tone gliding up inside it."""
    rng = np.random.default_rng(204)
    dur = 0.32
    t = t_of(dur)
    n = len(t)
    shape = np.sin(np.pi * t / dur) ** 2
    swish = noise_through(rng, np.interp(t, [0, dur], [700, 2300]), 700, n) * shape
    tone = sweep(np.geomspace(NOTE["G5"], NOTE["D6"], n)) * shape
    return lowpass(place(0.34, [(0, 0.8 * swish + 0.16 * tone)]), 6000)


def switch():
    """Real picture or cartoon: a tiny sparkle, three quick little bells."""
    run = [("A6", 0.5), ("C#7", 0.42), ("E7", 0.36), ("A7", 0.18)]
    return place(0.45, [(0.045 * k, a * bell(NOTE[n], 0.3, bright=0.4)) for k, (n, a) in enumerate(run)])


def star():
    """A star: a twinkle running up the glockenspiel, then a shimmer."""
    run = ["E6", "G#6", "B6", "E7"]
    parts = [(i * 0.055, (0.5 + 0.1 * i) * bell(NOTE[n], 0.5, bright=0.6)) for i, n in enumerate(run)]
    parts += [(0.26 + k * 0.06, 0.32 * 0.8 ** k * bell(NOTE["B6" if k % 2 else "E7"], 0.3, bright=0.3)) for k in range(8)]
    return place(0.95, parts)


def rest_bell():
    """Time for a rest: one soft, warm bell, and a quieter one above it,
    ringing out slowly."""
    return place(1.5, [(0, chime(NOTE["C5"], 1.5)), (0.4, 0.45 * chime(NOTE["G5"], 1.1))])


# ---------------------------------------------------------------- animals


def woof(rng, high=1.0, times=2):
    """A dog: woof woof (畫畫小鎮)."""
    def one():
        dur = 0.16 / high ** 0.3
        t = t_of(dur)
        f0 = glide(t, (0, 330), (0.04, 380), (dur, 220)) * high
        x = voice(f0, [(520 * high ** 0.5, 160, 1.0), (1350 * high ** 0.4, 220, 0.5), (2600, 300, 0.1)], rng, breath=0.3, rough=0.05)
        return x * env(len(t), 0.004, 0.06) * decay(len(t), 0.09)
    return place(0.23 * times + 0.1, [(0.23 * i, one()) for i in range(times)])


def say_dog():
    """汪汪: a friendly young dog, woof woof."""
    return woof(np.random.default_rng(301), high=1.2)


def say_cat():
    """喵喵: a cute mi-aa-ow (畫畫小鎮's meow, a little higher)."""
    rng = np.random.default_rng(302)
    dur = 0.72
    t = t_of(dur)
    f0 = glide(t, (0, 520), (0.27, 760), (dur, 480)) * 1.1
    f1 = glide(t, (0, 320), (0.24, 900), (dur, 450))
    f2 = glide(t, (0, 2300), (0.29, 1500), (dur, 950))
    return voice(f0, [(f1, 120, 1.0), (f2, 180, 0.6), (3000, 300, 0.1)], rng, breath=0.05) * env(len(t), 0.05, 0.2)


def say_rabbit():
    """A rabbit: its nose twitching, sniff-sniff-sniff, then two tiny squeaks."""
    rng = np.random.default_rng(303)

    def sniff(amp):
        m = int(0.035 * SR)
        return amp * norm(bandpass(rng.standard_normal(m), 2200, 6500)) * np.hanning(m)

    def squeak(dur, f):
        t = t_of(dur)
        fr = np.interp(t, [0, 0.4 * dur, dur], [f, f * 1.35, f * 1.1])
        return (sweep(fr) + 0.15 * sweep(2 * fr)) * np.sin(np.pi * t / dur) ** 1.2
    return place(0.56, [(0, sniff(0.4)), (0.065, sniff(0.32)), (0.13, sniff(0.4)),
                        (0.26, 0.5 * squeak(0.09, 1500)), (0.4, 0.45 * squeak(0.11, 1650))])


def say_cow():
    """哞～: mmm-ooo, rising then sinking, a little higher than a real cow."""
    rng = np.random.default_rng(304)
    low, dur = 1.15, 1.1
    t = t_of(dur)
    f0 = glide(t, (0, 105), (0.25 * dur, 150), (0.7 * dur, 140), (dur, 96)) * low * (1 + 0.012 * np.sin(2 * np.pi * 5 * t))
    opening = ease((t - 0.08) / 0.25)  # the mouth opens from "m" to "oo-oh"
    x = voice(f0, [(250 + 380 * opening * low, 90, 1.0), (600 + 350 * opening * low, 120, 0.45), (2400, 250, 0.06)], rng, breath=0.04)
    return carry(x * env(len(t), 0.1, 0.3), 0.3)


def say_pig():
    """齁齁: two snorty little oinks."""
    rng = np.random.default_rng(305)

    def one(dur):
        t = t_of(dur)
        f0 = glide(t, (0, 165), (0.4 * dur, 250), (dur, 185))
        x = voice(f0, [(420, 180, 1.0), (1300, 300, 0.45), (2400, 300, 0.1)], rng, breath=0.55, rough=0.1)
        return x * env(len(t), 0.01, 0.06) * np.sin(np.pi * t / dur) ** 0.5
    return carry(place(0.5, [(0, one(0.17)), (0.24, 0.9 * one(0.2))]), 0.2)


def say_sheep():
    """咩～: b-aa-aa, a lamb's bleat."""
    rng = np.random.default_rng(306)
    high, dur, shake = 1.12, 0.85, 7.0
    t = t_of(dur)
    bleat = 1 + 0.05 * np.sin(2 * np.pi * shake * t) * ease(t / 0.2)
    f0 = glide(t, (0, 250), (0.12, 300), (dur, 255)) * high * bleat
    opening = ease(t / 0.06)
    x = voice(f0, [(350 + 450 * opening, 110, 1.0), (1150 + 150 * high, 150, 0.6), (2600, 250, 0.12)], rng, breath=0.05)
    return x * env(len(t), 0.01, 0.25) * (0.75 + 0.25 * np.sin(2 * np.pi * shake * t))


def clop(rng, f):
    """A hoof on the road: a hollow, woody clop."""
    t = t_of(0.08)
    x = (partial(f, t, SR) * np.exp(-t / 0.012) + 0.5 * partial(f * 2.4, t, SR) * np.exp(-t / 0.006)
         + 0.6 * sweep(np.geomspace(f * 0.4, f * 0.3, len(t))) * np.exp(-t / 0.02))
    click = 0.3 * norm(bandpass(rng.standard_normal(len(t)), 1500, 6000)) * np.exp(-t / 0.002)
    return (x + click) * env(len(t), 0.0008, 0.02)


def say_horse():
    """A horse: neigh-h-h, falling and trembling, then clip-clop, clip-clop."""
    rng = np.random.default_rng(307)
    dur = 0.8
    t = t_of(dur)
    shake = 1 + 0.08 * np.sin(2 * np.pi * 12 * t) * ease(t / 0.4)
    f0 = glide(t, (0, 820), (0.13, 920), (dur, 430)) * shake
    f1 = glide(t, (0, 400), (0.25, 750), (dur, 700))
    neigh = voice(f0, [(f1, 150, 1.0), (glide(t, (0, 2200), (dur, 1250)), 200, 0.6)], rng, breath=0.12)
    parts = [(0, neigh * env(len(t), 0.02, 0.25))]
    parts += [(at, a * clop(rng, f)) for at, f, a in ((0.86, 900, 0.5), (0.98, 700, 0.42), (1.18, 900, 0.5), (1.3, 700, 0.42))]
    return place(1.45, parts)


def say_chicken():
    """咕咕: a hen, bok, bok, bok, b-gawk!"""
    rng = np.random.default_rng(308)

    def bok(dur=0.07, f=380):
        t = t_of(dur)
        x = voice(np.full(len(t), float(f)), [(650, 140, 1.0), (1500, 200, 0.4)], rng, breath=0.2)
        return x * env(len(t), 0.003, 0.04) * decay(len(t), 0.04)
    t = t_of(0.34)
    f0 = glide(t, (0, 480), (0.08, 650), (0.34, 470))
    gawk = voice(f0, [(glide(t, (0, 450), (0.1, 750), (0.34, 650)), 140, 1.0), (1200, 200, 0.5)], rng, breath=0.15)
    return place(0.82, [(0, bok()), (0.13, bok(f=400)), (0.26, bok(f=370)), (0.44, gawk * env(len(t), 0.01, 0.12))])


def say_duck():
    """呱呱: two nasal little quacks."""
    def one(dur):
        t = t_of(dur)
        f = np.linspace(560, 380, len(t))
        buzz = 2 * (np.cumsum(f) / SR % 1) - 1  # a sawtooth, nasal once filtered
        x = bandpass(buzz, 700, 2600) + 0.3 * bandpass(buzz, 2600, 4200)
        return x * env(len(t), 0.008, 0.05) * (0.6 + 0.4 * np.sin(np.pi * t / dur))
    return lowpass(place(0.42, [(0, one(0.15)), (0.2, 0.85 * one(0.17))]), 3500)


def say_fish():
    """A fish: blub, blub, blub, and little bubbles going up."""
    rng = np.random.default_rng(310)

    def blub(f0, f1, dur):
        t = t_of(dur)
        f = np.geomspace(f0, f1, len(t))
        return (sweep(f) + 0.3 * sweep(2 * f)) * env(len(t), 0.004, 0.04) * decay(len(t), dur * 0.5)
    parts = [(0, blub(300, 850, 0.1)), (0.14, blub(360, 950, 0.09)), (0.27, blub(280, 780, 0.11))]
    parts += [(rng.uniform(0.05, 0.48), rng.uniform(0.15, 0.3) * bubble(rng, SR, (700, 1200), (1.8, 2.4), (0.02, 0.035)))
              for _ in range(6)]
    return place(0.6, parts)


def say_bird():
    """啾啾: a little bird, tweet-tweet and a tiny trill."""
    def chirp(dur, lo, hi):
        t = t_of(dur)
        f = np.interp(t, [0, 0.35 * dur, dur], [lo, hi, lo * 1.15])
        return sweep(f) * np.sin(np.pi * t / dur) ** 1.5
    parts = [(0, chirp(0.09, 2700, 4300)), (0.15, chirp(0.1, 2800, 4400))]
    parts += [(0.36 + 0.045 * k, 0.5 * chirp(0.035, 3300 + 200 * (k % 2), 3900)) for k in range(4)]
    return place(0.58, parts)


def say_mouse():
    """吱吱: two tiny squeaks, higher than the rabbit's."""
    def squeak(dur, f):
        t = t_of(dur)
        fr = np.interp(t, [0, 0.5 * dur, dur], [f, f * 1.4, f * 1.15])
        return (sweep(fr) + 0.12 * sweep(2 * fr)) * np.sin(np.pi * t / dur)
    return place(0.36, [(0, squeak(0.085, 2100)), (0.15, squeak(0.12, 2250))])


def say_elephant():
    """An elephant: a soft, brassy toot that slides up and wavers, like a toy trumpet."""
    rng = np.random.default_rng(313)
    dur = 0.85
    t = t_of(dur)
    f0 = glide(t, (0, 380), (0.12, 600), (0.7, 640), (dur, 560)) * (1 + 0.025 * np.sin(2 * np.pi * 6 * t))
    x = voice(f0, [(900, 250, 1.0), (2000, 300, 0.7), (3300, 400, 0.25)], rng, breath=0.08, rough=0.03)
    return lowpass(x * env(len(t), 0.05, 0.2), 3200)


def say_lion():
    """吼～: a soft, friendly "rawr", higher and smoother than a real roar."""
    rng = np.random.default_rng(314)
    low, dur = 1.45, 0.75
    t = t_of(dur)
    f0 = glide(t, (0, 120), (0.2 * dur, 175), (0.6 * dur, 150), (dur, 100)) * low
    growl = 1 - 0.2 * (0.5 + 0.5 * np.sin(2 * np.pi * 26 * t))
    x = voice(f0, [(720 * low ** 0.4, 160, 1.0), (1150 * low ** 0.4, 200, 0.7), (2500, 300, 0.15)], rng, breath=0.35, rough=0.1)
    return x * growl * env(len(t), 0.08, 0.28)


def say_giraffe():
    """A giraffe: pulling leaves off a branch (a soft rustle), then munch, munch, munch."""
    rng = np.random.default_rng(315)

    def rustle(dur, count):
        n = int(dur * SR)
        grains = np.zeros(n)
        for i in rng.integers(0, n - 200, count):
            m = int(rng.uniform(0.002, 0.006) * SR)
            grains[i:i + m] += rng.standard_normal(m) * np.exp(-np.arange(m) / (m / 4)) * rng.uniform(0.3, 1.0)
        return norm(bandpass(grains, 1800, 7000)) * np.sin(np.pi * np.arange(n) / n)

    def nom(f):
        dur = 0.15
        t = t_of(dur)
        f0 = glide(t, (0, f), (dur, f * 0.87))
        f1 = glide(t, (0, 280), (0.055, 580), (dur, 300))
        return voice(f0, [(f1, 100, 1.0), (1100, 200, 0.3), (2400, 300, 0.08)], rng, breath=0.08) * env(len(t), 0.012, 0.05)
    parts = [(0, 0.5 * rustle(0.28, 45))]
    for k, at in enumerate((0.34, 0.58, 0.82)):
        parts += [(at, 0.6 * nom(230 - 8 * k)), (at - 0.02, 0.22 * rustle(0.07, 10))]
    return place(1.02, parts)


def say_zebra():
    """A zebra: a quick, bouncy little whinny, hee-hee-heee (higher and
    shorter than the horse, and no hooves)."""
    rng = np.random.default_rng(316)
    parts = []
    for k, (high, dur) in enumerate([(1.12, 0.16), (1.06, 0.16), (1.0, 0.27)]):
        t = t_of(dur)
        shake = 1 + 0.07 * np.sin(2 * np.pi * 16 * t)
        f0 = np.interp(t, [0, 0.25 * dur, dur], [760 * high, 860 * high, 580 * high]) * shake
        f1 = np.interp(t, [0, 0.3 * dur, dur], [450, 800, 700])
        f2 = np.interp(t, [0, dur], [2100, 1500])
        x = voice(f0, [(f1, 150, 1.0), (f2, 200, 0.6)], rng, breath=0.15)
        parts.append((k * 0.21, x * env(len(t), 0.012, 0.06)))
    return place(0.72, parts)


def say_monkey():
    """A monkey: ooh ooh aah aah!"""
    rng = np.random.default_rng(317)

    def one(f, vowel, dur=0.14):
        t = t_of(dur)
        f0 = glide(t, (0, f * 0.9), (dur, f * 1.1))
        f1, f2 = (380, 800) if vowel == "oo" else (850, 1350)
        return voice(f0, [(f1, 130, 1.0), (f2, 180, 0.5), (2600, 300, 0.08)], rng, breath=0.08) * env(len(t), 0.01, 0.05)
    return place(0.82, [(0, one(480, "oo")), (0.17, one(560, "oo")), (0.36, one(720, "aa", 0.17)), (0.58, one(820, "aa", 0.2))])


def say_bear():
    """A bear: a soft, warm growl-hum, mmmm, and a happy little "hm!"."""
    rng = np.random.default_rng(318)
    d = 0.6
    t = t_of(d)
    growl = 1 - 0.22 * (0.5 + 0.5 * np.sin(2 * np.pi * 22 * t))
    hmm = voice(glide(t, (0, 115), (0.2, 135), (d, 110)), [(420, 110, 1.0), (850, 150, 0.5), (2300, 250, 0.08)], rng,
                breath=0.25, rough=0.08) * growl * env(len(t), 0.08, 0.2)
    d2 = 0.3
    t2 = t_of(d2)
    hm = voice(glide(t2, (0, 135), (0.12, 150), (d2, 175)), [(300, 70, 1.0), (1000, 150, 0.3), (2300, 250, 0.08)], rng,
               breath=0.05) * env(len(t2), 0.03, 0.1)
    return carry(place(0.98, [(0, hmm), (0.66, 0.9 * hm)]), 0.35)


def say_turtle():
    """A turtle: slow, round bubbles, bloop... bloop... bloop."""
    rng = np.random.default_rng(319)

    def blub(f0, f1, dur):
        t = t_of(dur)
        f = np.geomspace(f0, f1, len(t))
        return (0.7 * sweep(f) + 0.5 * sweep(2 * f) + 0.18 * sweep(3 * f)) * env(len(t), 0.006, 0.05) * decay(len(t), dur * 0.6)
    dur = 1.15
    t = t_of(dur)
    hush = 0.05 * norm(lowpass(rng.standard_normal(len(t)), 500)) * np.sin(np.pi * t / dur)
    x = place(dur, [(0.02, blub(170, 420, 0.17)), (0.44, 0.9 * blub(150, 380, 0.2)), (0.88, 0.85 * blub(190, 460, 0.16))]) + hush
    return carry(x, 0.3)


def say_frog():
    """呱呱: a frog, ribbit, ribbit: a buzzy croak that rattles, in two parts."""
    rng = np.random.default_rng(320)

    def syllable(dur, f0, form):
        t = t_of(dur)
        x = voice(np.interp(t, [0, dur], [f0, f0 * 1.08]), [(form, 160, 1.0), (form * 1.9, 250, 0.5), (500, 120, 0.2)],
                  rng, breath=0.1)
        return x * (0.65 + 0.35 * np.sin(2 * np.pi * 38 * t)) * env(len(t), 0.006, 0.03)

    def ribbit(at):
        return [(at, syllable(0.1, 150, 950)), (at + 0.13, 0.85 * syllable(0.08, 170, 1150))]
    return round_off(place(0.75, ribbit(0) + ribbit(0.38)), 1.5)


# ---------------------------------------------------------------- vehicles


def honk(notes=(415, 523), beeps=((0, 0.13), (0.19, 0.18)), cutoff=1800, square=0.6):
    """A little horn: two notes together, soft-edged (畫畫小鎮)."""
    parts = []
    for at, dur in beeps:
        t = t_of(dur)
        x = sum(square * np.sign(np.sin(2 * np.pi * f * t)) + np.sin(2 * np.pi * f * t) for f in notes)
        parts.append((at, lowpass(x, cutoff) * env(len(t), 0.012, 0.04)))
    return place(max(a + d for a, d in beeps) + 0.02, parts)


def say_car():
    """叭叭: a little car horn, beep beep."""
    return honk()


def say_bus():
    """叭～: the bus's longer, lower horn, then its door opening, pssh."""
    rng = np.random.default_rng(322)
    horn = honk((311, 392), ((0, 0.48),), cutoff=1500)
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    hiss = norm(bandpass(rng.standard_normal(n), 2000, 7000)) * ease(t / 0.015) * np.exp(-t / 0.13)
    thunk = sweep(np.geomspace(220, 150, n)) * np.exp(-t / 0.03) + 0.5 * norm(lowpass(rng.standard_normal(n), 900)) * np.exp(-t / 0.01)
    return place(1.15, [(0, horn), (0.62, 0.45 * hiss), (0.6, 0.25 * thunk * env(n, 0.001, 0.05))])


def say_taxi():
    """A taxi pulling up for you: its turn signal ticks, then a bright bi-bip!"""
    rng = np.random.default_rng(323)

    def tick(f):
        t = t_of(0.03)
        x = partial(f, t, SR) * np.exp(-t / 0.004) + 0.4 * norm(bandpass(rng.standard_normal(len(t)), 2000, 7000)) * np.exp(-t / 0.002)
        return x * env(len(t), 0.0005, 0.01)
    parts = [(0, 0.35 * tick(2400)), (0.2, 0.3 * tick(1900)), (0.4, 0.35 * tick(2400))]
    return place(0.9, parts + [(0.6, honk((587, 740), ((0, 0.08), (0.12, 0.14)), cutoff=2400))])


def say_scooter():
    """噗噗: a scooter's little engine, putt-putt-putt, revving up, then a thin bee-beep."""
    rng = np.random.default_rng(324)
    dur = 0.85
    t = t_of(dur)
    n = len(t)
    rate = glide(t, (0, 14), (0.4, 22), (dur, 19))  # putts per second
    phase = np.cumsum(rate) / SR
    pulses = (0.5 + 0.5 * np.cos(2 * np.pi * phase)) ** 6
    body = noise_through(rng, 550, 350, n) + 0.5 * noise_through(rng, 1300, 600, n)
    tone = np.sin(2 * np.pi * np.cumsum(rate * 6) / SR)
    shape = ease(t / 0.05) * (1 - ease((t - 0.65) / 0.2))
    engine = carry((0.8 * body + 0.5 * tone) * pulses * shape, 0.3)

    def beep(dur):
        tt = t_of(dur)
        x = 0.5 * np.sign(np.sin(2 * np.pi * 740 * tt)) + np.sin(2 * np.pi * 740 * tt) + 0.6 * np.sin(2 * np.pi * 1110 * tt)
        return lowpass(x, 2800) * env(len(tt), 0.008, 0.03)
    return place(1.2, [(0, engine), (0.86, 0.35 * beep(0.08)), (0.99, 0.35 * beep(0.16))])


def say_bicycle():
    """鈴鈴: a bicycle bell, ring-ring: its little hammer striking the dome
    again and again, twice."""
    def ring(at0):
        return [(at0 + 0.04 * k, (1 - 0.15 * k) * metal(2050, 0.55, ratios=(1, 1.51, 2.27, 2.91),
                                                         amps=(1, .5, .3, .15), taus=(.6, .35, .2, .12))) for k in range(5)]
    return lowpass(place(1.05, ring(0) + ring(0.42)), 7000)


def say_train():
    """嘟嘟: a little train, chuff-chuff-chuff, and its whistle, toot-toot!"""
    rng = np.random.default_rng(326)
    parts = []
    for k in range(6):
        m = int(0.16 * SR)
        tt = np.arange(m) / SR
        chuff = norm(bandpass(rng.standard_normal(m), 500, 4000)) * ease(tt / 0.01) * np.exp(-tt / 0.045)
        parts.append((k * 0.21, (0.35 if k % 2 == 0 else 0.25) * chuff))

    def whistle(dur):
        t = t_of(dur)
        scoop = 1 - 0.03 * np.exp(-t / 0.03)
        x = sum(sweep(f * scoop) + 0.2 * sweep(2 * f * scoop) for f in (NOTE["C5"], NOTE["E5"], NOTE["G5"]))
        air = 0.4 * norm(bandpass(rng.standard_normal(len(t)), 600, 2500))
        return (x / 3 + 0.3 * air) * env(len(t), 0.03, 0.08)
    parts += [(0.22, 0.55 * whistle(0.22)), (0.55, 0.6 * whistle(0.45))]
    return place(1.3, parts)


def say_mrt():
    """The metro: a soft two-tone door chime, ding-dong (a plain falling
    third, not any real line's tune), then the gentle hum and rising whine of
    the train moving off."""
    rng = np.random.default_rng(327)
    parts = [(0, 0.5 * chime(NOTE["B5"], 0.7)), (0.3, 0.5 * chime(NOTE["G5"], 0.9))]
    dur = 0.85
    t = t_of(dur)
    n = len(t)
    shape = ease(t / 0.15) * (1 - ease((t - 0.6) / 0.25))
    whine = sweep(glide(t, (0, 320), (dur, 780))) + 0.3 * sweep(2 * glide(t, (0, 320), (dur, 780)))
    hum = carry(norm(lowpass(rng.standard_normal(n), 300)) + 0.6 * np.sin(2 * np.pi * 120 * t), 0.3)
    parts.append((0.62, (0.12 * whine + 0.35 * norm(hum)) * shape))
    return place(1.5, parts)


def say_hsr():
    """The high-speed train: whoooosh as it rushes by, its whine falling as it
    goes, and a soft ka-tan ka-tan from the rails as it passes."""
    rng = np.random.default_rng(328)
    dur = 1.3
    t = t_of(dur)
    n = len(t)
    by = np.interp(t, [0, 0.5, 0.62, 1.05, dur], [0, 0.85, 1, 0.25, 0]) ** 1.5
    air = noise_through(rng, np.interp(t, [0, 0.58, dur], [700, 2200, 900]), 1200, n)
    hiss = norm(bandpass(rng.standard_normal(n), 2500, 7000))
    rumble = norm(lowpass(rng.standard_normal(n), 400))
    whine = sweep(np.interp(t, [0, 0.52, 0.72, dur], [1250, 1220, 930, 900]))
    x = (0.7 * air + 0.25 * hiss + 0.3 * rumble + 0.2 * whine) * by
    m = int(0.03 * SR)
    tm = np.arange(m) / SR
    clicks = []
    for at in (0.4, 0.47, 0.6, 0.67):
        c = (norm(bandpass(rng.standard_normal(m), 800, 3000)) * np.exp(-tm / 0.006)
             + 0.4 * partial(1150, tm, SR) * np.exp(-tm / 0.01)) * env(m, 0.0005, 0.01)
        clicks.append((at, 0.4 * np.interp(at, t, by) * c))
    return carry(x + place(dur, clicks), 0.15, lo=400, hi=2000)


def say_airplane():
    """An airplane flying over: a soft hiss and hum that come and go, and the
    jet's whine sinking as it passes."""
    rng = np.random.default_rng(329)
    n = int(1.5 * SR)
    t = np.arange(n) / SR
    over = np.sin(np.pi * t / 1.5) ** 2
    hiss = norm(bandpass(rng.standard_normal(n), 500, 4000)) * over
    rumble = norm(lowpass(rng.standard_normal(n), 160)) * over
    whine = sweep(glide(t, (0, 1500), (0.75, 1350), (1.5, 1000))) * over
    return carry(0.6 * hiss + 0.8 * rumble + 0.22 * whine, 0.25, lo=300, hi=1500)


def say_helicopter():
    """A helicopter: chop-chop-chop-chop and its engine's whine."""
    rng = np.random.default_rng(330)
    n = int(1.3 * SR)
    t = np.arange(n) / SR
    beats = (0.5 + 0.5 * np.cos(2 * np.pi * 11 * t)) ** 6
    thump = norm(lowpass(rng.standard_normal(n), 350)) * beats
    whup = noise_through(rng, 700, 400, n) * beats
    whine = sweep(np.full(n, 2100.0))
    return carry((0.7 * thump + 0.6 * whup + 0.04 * whine) * env(n, 0.15, 0.3), 0.3, lo=400, hi=2000)


def say_boat():
    """嗚～: a big boat's horn, low and round, over the water lapping."""
    rng = np.random.default_rng(331)
    dur = 1.05
    t = t_of(dur)
    f0 = glide(t, (0, 140), (0.12, 150), (0.85, 148), (dur, 138)) * (1 + 0.004 * np.sin(2 * np.pi * 4.5 * t))
    horn = voice(f0, [(450, 150, 1.0), (900, 200, 0.6), (1700, 300, 0.25)], rng, breath=0.05) * env(len(t), 0.12, 0.3)
    m = int(1.4 * SR)
    tm = np.arange(m) / SR
    water = norm(bandpass(rng.standard_normal(m), 200, 1500)) * (0.5 + 0.5 * np.sin(2 * np.pi * 1.4 * tm)) ** 2 * np.sin(np.pi * tm / 1.4)
    return carry(place(1.4, [(0, horn), (0, 0.12 * water)]), 0.3)


def siren(kind, dur=1.4):
    """Fire engine (a slow wail), police car (a quick wee-woo), ambulance (two
    notes, high and low) (畫畫小鎮), rounder and softer."""
    t = t_of(dur)
    if kind == "fire":
        f = glide(t, (0, 520), (0.75, 1100), (dur, 620))
    elif kind == "police":
        f = 700 + 300 * (0.5 - 0.5 * np.cos(2 * np.pi * t / 0.43))
    else:
        f = np.where((t // 0.35) % 2 == 0, 960.0, 770.0)
        f = lowpass(f - 865, 60) + 865
    phase = np.cumsum(f) / SR
    x = lowpass(np.sign(np.sin(2 * np.pi * phase)) * 0.35 + np.sin(2 * np.pi * phase), 2400)
    return x * env(len(t), 0.08, 0.2)


def say_fire_truck():
    """喔咿喔咿: the fire engine's slow wail, up and down."""
    return siren("fire")


def say_ambulance():
    """The ambulance: two notes, high and low."""
    return siren("ambulance")


def say_police_car():
    """The police car: a quick wee-woo, wee-woo."""
    return siren("police", 1.3)


def say_garbage_truck():
    """The garbage truck's tune: the opening of Für Elise (Beethoven, 1810),
    from a tinny little loudspeaker, as Taiwan's garbage trucks play it."""
    tune = [("E5", 1), ("D#5", 1), ("E5", 1), ("D#5", 1), ("E5", 1), ("B4", 1), ("D5", 1), ("C5", 1), ("A4", 2)]
    beat, parts, at = 0.14, [], 0.0
    for note, beats in tune:
        dur = beat * beats
        t = t_of(dur)
        f = NOTE[note]
        x = triangle(f, dur) + 0.35 * np.sign(np.sin(2 * np.pi * f * t))
        parts.append((at, x * env(len(t), 0.008, 0.06) * (decay(len(t), 0.5) if beats > 1 else 1)))
        at += dur
    return bandpass(place(at + 0.1, parts), 450, 3800)


def say_truck():
    """A big truck: its deep air horn, baap, baaap, over the diesel rumble."""
    rng = np.random.default_rng(332)

    def blast(dur):
        t = t_of(dur)
        x = sum(2 * (np.cumsum(np.full(len(t), f)) / SR % 1) - 1 for f in (185, 233))
        return lowpass(x, 1400) * env(len(t), 0.03, 0.08)
    n = int(1.1 * SR)
    t = np.arange(n) / SR
    pulses = 0.6 + 0.4 * (0.5 + 0.5 * np.cos(2 * np.pi * 18 * t)) ** 3
    engine = carry(norm(lowpass(rng.standard_normal(n), 350)) * pulses, 0.4, lo=300, hi=1500) * env(n, 0.1, 0.25)
    return place(1.1, [(0, 0.25 * engine), (0.05, 0.5 * blast(0.3)), (0.45, 0.5 * blast(0.5))])


def say_excavator():
    """An excavator backing up: beep, beep, beep over its engine (畫畫小鎮)."""
    rng = np.random.default_rng(333)
    beeps = []
    for k in range(3):
        t = t_of(0.18)
        beeps.append((0.33 * k, (np.sin(2 * np.pi * 1050 * t) + 0.12 * np.sin(2 * np.pi * 2100 * t)) * env(len(t), 0.01, 0.03)))
    n = int(1.05 * SR)
    t = np.arange(n) / SR
    engine = norm(lowpass(rng.standard_normal(n), 180)) * (0.7 + 0.3 * np.sin(2 * np.pi * 14 * t))
    engine = carry(engine, 0.45, lo=300, hi=1500) * env(n, 0.1, 0.2)
    return place(1.05, beeps) * 0.55 + 0.45 * engine


def say_hot_air_balloon():
    """A hot-air balloon: the valve clicks and the burner goes fwoosh... fwoooosh."""
    rng = np.random.default_rng(334)
    dur = 1.25
    t = t_of(dur)
    n = len(t)
    flicker = 1 + 0.45 * norm(lowpass(rng.standard_normal(n), 30))
    flame = norm(bandpass(rng.standard_normal(n), 150, 1800)) * flicker
    roar = noise_through(rng, 650, 500, n)
    hiss = norm(bandpass(rng.standard_normal(n), 2000, 6000))
    def puff(a, b):
        return ease((t - a) / 0.08) * (1 - ease((t - b + 0.3) / 0.3))
    shape = 0.8 * puff(0.02, 0.42) + puff(0.56, dur)
    x = carry((0.7 * flame + 0.5 * roar + 0.2 * hiss) * shape, 0.25, lo=400, hi=2200)
    click = metal(2600, 0.05, ratios=(1, 2.3), amps=(1, 0.4), taus=(0.3, 0.15))
    return place(dur + 0.02, [(0, 0.3 * click), (0.54, 0.3 * click), (0.02, x)])


def say_rocket():
    """A rocket going up: a deep rumble that swells in, a roar rising as it
    climbs away, and a soft whistle going up and up."""
    rng = np.random.default_rng(335)
    dur = 1.5
    t = t_of(dur)
    n = len(t)
    shape = ease(t / 0.35) * (1 - ease((t - 0.8) / 0.7))
    rumble = norm(lowpass(rng.standard_normal(n), 220))
    roar = noise_through(rng, glide(t, (0, 350), (dur, 1500)), 500, n)
    hiss = norm(bandpass(rng.standard_normal(n), 2500, 7000)) * ease(t / 0.9)
    whistle = sweep(glide(t, (0, 450), (0.3, 500), (dur, 1700))) * ease((t - 0.2) / 0.4)
    return carry((rumble + 0.8 * roar + 0.2 * hiss + 0.25 * whistle) * shape, 0.3, lo=400, hi=2500)


def say_stroller():
    """A stroller: its wheels rolling along, and one little wheel squeaking, eek, eek, eek."""
    rng = np.random.default_rng(336)
    dur = 1.25
    t = t_of(dur)
    n = len(t)
    shape = ease(t / 0.15) * (1 - ease((t - 1.0) / 0.25))
    roll = norm(lowpass(rng.standard_normal(n), 700)) * (0.7 + 0.3 * np.abs(np.sin(2 * np.pi * 3 * t)))
    rumble = noise_through(rng, 380, 220, n)

    def eek(d=0.09):
        tt = t_of(d)
        f = np.interp(tt, [0, 0.5 * d, d], [1500, 1850, 1650])
        return (sweep(f) + 0.15 * sweep(2 * f)) * np.sin(np.pi * tt / d) ** 1.5
    x = carry((0.6 * roll + 0.4 * rumble) * shape, 0.3, lo=400, hi=2000)
    return place(dur, [(0, 0.45 * x)] + [(at, 0.4 * eek()) for at in (0.18, 0.56, 0.94)])


# ---------------------------------------------------------------- things at home


def say_clock():
    """滴答: a clock, tick-tock, tick-tock."""
    rng = np.random.default_rng(341)

    def tk(f):
        t = t_of(0.06)
        x = (partial(f, t, SR) * np.exp(-t / 0.008) + 0.5 * partial(f * 1.73, t, SR) * np.exp(-t / 0.005)
             + 0.4 * partial(f * 0.35, t, SR) * np.exp(-t / 0.015)  # the wooden case
             + 0.3 * norm(bandpass(rng.standard_normal(len(t)), 3000, 8000)) * np.exp(-t / 0.0015))
        return x * env(len(t), 0.0005, 0.015)
    return place(1.05, [(0, tk(2200)), (0.32, 0.9 * tk(1500)), (0.64, tk(2200)), (0.96, 0.9 * tk(1500))])


def say_phone():
    """鈴鈴: a phone ringing gently, li-li-li-li, li-li-li-li: two soft bells
    trilling, twice."""
    def burst(at0):
        return [(at0 + 0.055 * k, (0.8 if k % 2 == 0 else 0.65) * bell(NOTE["C6" if k % 2 == 0 else "A5"], 0.16, bright=0.3))
                for k in range(8)]
    return place(1.2, burst(0) + burst(0.65))


def say_door():
    """叩叩: knock-knock on a wooden door."""
    rng = np.random.default_rng(343)

    def knock():
        t = t_of(0.12)
        n = len(t)
        thud = sweep(np.geomspace(190, 120, n)) * np.exp(-t / 0.025)
        hit = rng.standard_normal(n) * np.exp(-t / 0.004)
        panel = (norm(resonator(hit, 520, 110)) * np.exp(-t / 0.045)  # the wooden panel rings
                 + 0.7 * norm(resonator(hit, 1150, 220)) * np.exp(-t / 0.025)
                 + 0.35 * norm(resonator(hit, 2300, 400)) * np.exp(-t / 0.01))
        click = 0.2 * norm(bandpass(rng.standard_normal(n), 2000, 6000)) * np.exp(-t / 0.0015)
        return round_off((0.35 * thud + panel + click) * env(n, 0.0005, 0.03), 3.0)
    return carry(place(0.45, [(0, knock()), (0.21, 0.9 * knock())]), 0.25)


# ---------------------------------------------------------------- the list

# name: (make, loudness in dB beside the others: below 0 sits softer).
UI = {
    "flip": (flip, -4), "tap": (tap, -4), "right": (right, 0), "try": (try_again, -5), "next": (next_card, -5),
    "switch": (switch, -5), "star": (star, -1), "rest": (rest_bell, -2),
}
SAY = {
    # animals
    "dog": (say_dog, 0), "cat": (say_cat, 0), "rabbit": (say_rabbit, -2), "cow": (say_cow, 0), "pig": (say_pig, 0),
    "sheep": (say_sheep, 0), "horse": (say_horse, 0), "chicken": (say_chicken, 0), "duck": (say_duck, 0),
    "fish": (say_fish, 0), "bird": (say_bird, -3), "mouse": (say_mouse, -4), "elephant": (say_elephant, -1),
    "lion": (say_lion, 0), "giraffe": (say_giraffe, -1), "zebra": (say_zebra, -1), "monkey": (say_monkey, 0),
    "bear": (say_bear, 0), "turtle": (say_turtle, 0), "frog": (say_frog, 0),
    # vehicles
    "car": (say_car, 0), "bus": (say_bus, 0), "taxi": (say_taxi, 0), "scooter": (say_scooter, 0),
    "bicycle": (say_bicycle, -3), "train": (say_train, 0), "mrt": (say_mrt, 0), "hsr": (say_hsr, 0),
    "airplane": (say_airplane, 0), "helicopter": (say_helicopter, 0), "boat": (say_boat, 0),
    "fire_truck": (say_fire_truck, -3), "ambulance": (say_ambulance, -3), "police_car": (say_police_car, -3),
    "garbage_truck": (say_garbage_truck, -1), "truck": (say_truck, 0), "excavator": (say_excavator, -1),
    "hot_air_balloon": (say_hot_air_balloon, 0), "rocket": (say_rocket, 0), "stroller": (say_stroller, -1),
    # things at home
    "clock": (say_clock, -2), "phone": (say_phone, -3), "door": (say_door, 0),
}
SHORT = {**UI, **{f"say_{k}": v for k, v in SAY.items()}}
TARGET = -21.0  # dB, the loudness of a short sound at 0 (about where 動物小餐廳's sit)
MAX_PEAK = 0.72


def check_cards():
    """Every animal and vehicle card has its sound, and so do the clock, the
    phone and the door; no sound is for a card that is not there."""
    decks = {d["id"]: [c["id"] for c in d["cards"]] for d in json.loads(CARDS.read_text())["decks"]}
    want = decks["animals"] + decks["vehicles"] + [c for c in ("clock", "phone", "door") if c in decks["home"]]
    assert sorted(want) == sorted(SAY), (set(want) ^ set(SAY))


# ---------------------------------------------------------------- writing and checking


def tidy(x, sr=SR):
    """A short sound: drop the silent end, then fade both ends so neither clicks."""
    x = np.asarray(x, dtype=np.float64)
    loud = np.nonzero(np.abs(x) > np.abs(x).max() * 1e-3)[0]
    x = x[: min(len(x), loud[-1] + int(0.01 * sr))]
    return x * env(len(x), 0.002, 0.012, sr)


def level(x, offset, sr=SR):
    """[x] at the loudness TARGET + [offset] dB, unless that would put its
    peak over MAX_PEAK: then at MAX_PEAK. Returns the peak."""
    x = norm(x)
    return min(MAX_PEAK, 10 ** ((TARGET + offset - loudness(x, sr)) / 20))


def write(path, x, peak, sr):
    x = np.asarray(x, dtype=np.float64)
    x = x / max(1e-9, np.abs(x).max()) * peak
    data = np.round(x * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(data.tobytes())
    return data


def report(name, data, sr, loop, want=None):
    x = data.astype(np.float64) / 32767
    peak = np.abs(x).max()
    loud = loudness(x, sr)
    clipped = int(np.sum(np.abs(data) >= 32767))
    steps = np.abs(np.diff(data.astype(np.int32)))
    if loop:  # the jump from the last sample back to the first, beside the usual step
        jump = abs(int(data[0]) - int(data[-1]))
        edge = f"seam jump {jump:4d} (usual step {np.median(steps):.0f}, 99% {np.percentile(steps, 99):.0f})"
    else:
        edge = f"ends {int(data[0]):+d} / {int(data[-1]):+d}"
    short = "" if want is None or loud > want - 0.5 else f"  ({want - loud:.1f} dB under, held by the peak)"
    print(f"  {name:22s} {len(x) / sr:5.2f} s  {len(data) * 2 + 44:9,d} bytes  peak {peak:.2f}  "
          f"loudness {loud:6.1f} dB  clipped {clipped}  {edge}{short}")


def read(path):
    with wave.open(str(path), "rb") as w:
        return np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(np.float64) / 32767, w.getframerate()


def preview(path, loop_seconds=8.0, gap=0.5):
    """A listening preview: [loop_seconds] of each tune, then every short
    sound in order, [gap] apart. Prints where each one starts."""
    path = pathlib.Path(path)
    sr, pieces, at = 22050, [], 0.0
    print(f"preview {path}:")
    for name in list(MUSIC) + list(SHORT):
        x, rate = read(OUT / f"{name}.wav")
        if rate != sr:
            x = resample_poly(x, sr, rate)
        if name in MUSIC:
            x = x[: int(loop_seconds * sr)] * env(int(loop_seconds * sr), 0.01, 0.5, sr)
        print(f"  {int(at // 60)}:{at % 60:04.1f}  {name}")
        pieces += [x, np.zeros(int((1.0 if name in MUSIC else gap) * sr))]
        at += (len(x) + len(pieces[-1])) / sr
    wav = path.with_suffix(".wav")
    write(wav, np.concatenate(pieces), np.abs(np.concatenate(pieces)).max(), sr)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-c:a", "aac", "-b:a", "96k", str(path)], check=True)
    wav.unlink()
    print(f"  total {at:.1f} s")


def main():
    check_cards()
    OUT.mkdir(parents=True, exist_ok=True)
    print("music (16,000 Hz, loops):")
    for name, (make, peak) in MUSIC.items():
        report(name, write(OUT / f"{name}.wav", make(), peak, LOOP_SR), LOOP_SR, True)
    print(f"short sounds (22,050 Hz), loudness {TARGET:.0f} dB plus or minus, peaks at most {MAX_PEAK}:")
    for name, (make, offset) in SHORT.items():
        x = tidy(highpass(make(), 70))  # nothing a phone cannot play anyway, for more room under the peak
        report(name, write(OUT / f"{name}.wav", x, level(x, offset), SR), SR, False, TARGET + offset)
    total = sum(p.stat().st_size for p in OUT.glob("*.wav"))
    print(f"{len(MUSIC) + len(SHORT)} sounds, {total:,} bytes ({total / 1024 / 1024:.2f} MiB) in {OUT}")
    assert total < LIMIT, f"the sounds must stay under {LIMIT:,} bytes"
    if len(sys.argv) == 3 and sys.argv[1] == "preview":
        preview(sys.argv[2])


if __name__ == "__main__":
    main()
