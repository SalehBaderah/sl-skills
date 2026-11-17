"""Soft, natural UI sounds generated locally; no downloaded samples.

Clicks are short filtered-noise transients with a small low "body" (like a
real trackpad or key), not sine beeps. Each hit gets slight, deterministic
pitch/gain variation so repeated clicks and typing never sound identical.
"""
import math
import wave

import numpy as np

SAMPLE_RATE = 48000
EFFECTS = {"click", "open", "close", "touch", "toggle", "type", "success"}
DEFAULT_VOLUME = .25
LENGTHS = {"click": .06, "open": .22, "close": .2, "touch": .09,
           "toggle": .12, "type": .04, "success": .55}


def number(value, label, low, high):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f"{label} must be a finite number in {low}..{high}")
    return value


def cues(plan, duration):
    """Return sorted (time, effect, gain, pan) cues; validate even disabled cues."""
    config = plan.get("sound_effects", {})
    if not isinstance(config, dict):
        raise ValueError("sound_effects must be an object")
    enabled = config.get("enabled", False)
    if not isinstance(enabled, bool):
        raise ValueError("sound_effects.enabled must be true or false")
    volume = number(config.get("volume", DEFAULT_VOLUME), "sound_effects.volume", 0, 1)
    stereo = config.get("stereo", True)
    if not isinstance(stereo, bool):
        raise ValueError("sound_effects.stereo must be true or false")
    result = []
    for event in plan.get("events", []):
        effect = event.get("sound", "click")
        if not isinstance(effect, str) or effect not in EFFECTS | {"none"}:
            raise ValueError(f"Unknown event sound: {effect}")
        if effect != "none":
            pan = (event.get("x", .5)-.5)*.6 if stereo else 0
            result.append((event["time"], effect, volume, pan))
    extra = plan.get("sounds", [])
    if not isinstance(extra, list):
        raise ValueError("sounds must be a list")
    for cue in extra:
        if not isinstance(cue, dict) or cue.get("effect") not in EFFECTS:
            raise ValueError("Each sounds cue needs a supported effect")
        start = number(cue.get("time"), "Sound time", 0, duration)
        gain = number(cue.get("volume", 1), "Sound volume", 0, 1)
        result.append((start, cue["effect"], gain*volume, 0))
    if not enabled or plan.get("audio", "preserve") == "mute":
        return []
    return sorted(c for c in result if c[0] < duration and c[2] > 0)


def _bandpass(x, low, high):
    """Zero-phase FFT band-pass; fine for these tiny buffers."""
    spectrum = np.fft.rfft(x, n=len(x)*2)
    f = np.fft.rfftfreq(len(x)*2, 1/SAMPLE_RATE)
    shape = 1/(1+(low/np.maximum(f, 1))**4) / (1+(f/high)**4)
    return np.fft.irfft(spectrum*shape)[:len(x)]


def _tone(t, freq, decay, partials=((1, 1), (2.76, .25), (5.4, .08))):
    """Mallet-like tone: inharmonic partials that decay faster when higher."""
    return sum(g*np.sin(2*np.pi*freq*m*t)*np.exp(-t*decay*m**.5) for m, g in partials)


def synthesize(effect, variant=0):
    """Return a mono float waveform. `variant` gives subtle per-hit variation."""
    rng = np.random.default_rng(1009*variant + sorted(EFFECTS).index(effect))
    detune = 1 + (rng.uniform(-.06, .06) if variant else 0)
    length = LENGTHS[effect]
    t = np.arange(round(length*SAMPLE_RATE)) / SAMPLE_RATE
    noise = rng.standard_normal(len(t))
    if effect in ("click", "type", "touch"):
        centre = {"click": 3200, "type": 4200, "touch": 1800}[effect]*detune
        decay = {"click": 380, "type": 520, "touch": 220}[effect]
        snap = _bandpass(noise, centre*.55, centre*1.6) * np.exp(-t*decay)
        body_f = {"click": 190, "type": 260, "touch": 150}[effect]*detune
        body = np.sin(2*np.pi*body_f*t) * np.exp(-t*90)
        signal = .9*snap/max(np.max(np.abs(snap)), 1e-9) + {"click": .35, "type": .18, "touch": .5}[effect]*body
        signal *= {"click": .55, "type": .32, "touch": .45}[effect]
    elif effect == "toggle":
        # Two soft ticks, second slightly higher: continuous phase, no pops.
        tick = lambda t0, f: np.where(t >= t0, 1, 0) * _bandpass(noise, f*.6, f*1.5) * np.exp(-np.maximum(t-t0, 0)*400)
        signal = tick(0, 2600*detune) + .8*tick(.045, 3400*detune)
        signal = .45*signal/max(np.max(np.abs(signal)), 1e-9)
    elif effect in ("open", "close"):
        # A soft "whoosh": band-passed noise with a gentle swell, plus a muted tone.
        env = np.sin(np.pi*t/length)**2 if effect == "open" else np.exp(-t*14)*(1-np.exp(-t*400))
        air = _bandpass(noise, 700, 3500) * env
        air /= max(np.max(np.abs(air)), 1e-9)
        f = (520 if effect == "open" else 440)*detune
        signal = .18*air + .22*_tone(t, f, 18)*(1-np.exp(-t*300))
    else:  # success: two gentle marimba notes (major third), not a game chime
        second = np.where(t >= .09, 1, 0)*_tone(np.maximum(t-.09, 0), 784*detune, 9)
        signal = .22*(_tone(t, 622*detune, 9) + second)
    fade = np.minimum(1, t/.0015) * np.minimum(1, (length-t)/.012)
    fade[0] = 0
    return (signal*fade).astype(np.float32)


def write_effects(path, sound_cues, duration):
    """Write a stereo WAV, streaming bounded blocks rather than the whole timeline."""
    pending = []
    for i, cue in enumerate(sound_cues):
        t, effect, gain = cue[:3]
        pan = cue[3] if len(cue) > 3 else 0
        mono = synthesize(effect, i+1)*gain
        angle = (pan+1)*math.pi/4  # constant-power pan
        pending.append((round(t*SAMPLE_RATE), np.stack([mono*math.cos(angle), mono*math.sin(angle)], 1)*math.sqrt(2)))
    total = round(duration*SAMPLE_RATE)
    with wave.open(str(path), "wb") as out:
        out.setnchannels(2)
        out.setsampwidth(2)
        out.setframerate(SAMPLE_RATE)
        for start in range(0, total, SAMPLE_RATE):
            end = min(start+SAMPLE_RATE, total)
            block = np.zeros((end-start, 2), np.float32)
            for offset, samples in pending:
                lo, hi = max(start, offset), min(end, offset+len(samples))
                if lo < hi:
                    block[lo-start:hi-start] += samples[lo-offset:hi-offset]
            pending = [(o, s) for o, s in pending if o+len(s) > end]
            out.writeframes((np.clip(np.tanh(block*1.1)/math.tanh(1.1), -1, 1)*32767).astype("<i2").tobytes())
