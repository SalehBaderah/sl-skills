"""Small, deterministic UI sounds generated locally; no downloaded samples."""
import math
import wave

import numpy as np

SAMPLE_RATE = 48000
EFFECTS = {"click", "open", "close", "touch", "toggle", "type", "success"}


def number(value, label, low, high):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f"{label} must be a finite number in {low}..{high}")
    return value


def cues(plan, duration):
    """Validate even disabled cues, so malformed plans fail before rendering."""
    config = plan.get("sound_effects", {})
    if not isinstance(config, dict):
        raise ValueError("sound_effects must be an object")
    enabled = config.get("enabled", False)
    if not isinstance(enabled, bool):
        raise ValueError("sound_effects.enabled must be true or false")
    volume = number(config.get("volume", .35), "sound_effects.volume", 0, 1)
    result = []
    for event in plan.get("events", []):
        effect = event.get("sound", "click")
        if not isinstance(effect, str) or effect not in EFFECTS | {"none"}:
            raise ValueError(f"Unknown event sound: {effect}")
        if effect != "none":
            result.append((event["time"], effect, volume))
    extra = plan.get("sounds", [])
    if not isinstance(extra, list):
        raise ValueError("sounds must be a list")
    for cue in extra:
        if not isinstance(cue, dict) or cue.get("effect") not in EFFECTS:
            raise ValueError("Each sounds cue needs a supported effect")
        start = number(cue.get("time"), "Sound time", 0, duration)
        gain = number(cue.get("volume", 1), "Sound volume", 0, 1)
        result.append((start, cue["effect"], gain * volume))
    if not enabled or plan.get("audio", "preserve") == "mute":
        return []
    return sorted(c for c in result if c[0] < duration and c[2] > 0)


def synthesize(effect):
    """Return a mono, floating-point waveform with a short fade at both ends."""
    lengths = {"click": .045, "open": .18, "close": .16, "touch": .09,
               "toggle": .10, "type": .025, "success": .32}
    t = np.arange(round(lengths[effect] * SAMPLE_RATE)) / SAMPLE_RATE
    rng = np.random.default_rng(17)
    noise = rng.uniform(-1, 1, len(t))
    if effect in ("click", "type"):
        f = 1500 if effect == "click" else 2100
        signal = (.55 * np.sin(2*np.pi*f*t) + .25*noise) * np.exp(-t*150)
    elif effect == "touch":
        signal = .6*np.sin(2*np.pi*420*t)*np.exp(-t*45)
    elif effect in ("open", "close"):
        start, end = (550, 1050) if effect == "open" else (900, 430)
        phase = 2*np.pi*(start*t + .5*(end-start)/lengths[effect]*t*t)
        signal = .35*np.sin(phase) * np.sin(np.pi*t/lengths[effect])**2
    elif effect == "toggle":
        signal = .4*np.sin(2*np.pi*np.where(t < .05, 620, 880)*t)*np.exp(-t*20)
    else:
        signal = .25*(np.sin(2*np.pi*660*t) + np.sin(2*np.pi*990*t))*np.sin(np.pi*t/lengths[effect])**2
    fade = np.minimum(1, t/.003) * np.minimum(1, (lengths[effect]-t)/.008)
    return (signal*fade).astype(np.float32)


def write_effects(path, sound_cues, duration):
    """Stream bounded-size blocks; don't allocate a whole recording in RAM."""
    pending = [(round(t*SAMPLE_RATE), synthesize(effect)*gain) for t, effect, gain in sound_cues]
    total = round(duration*SAMPLE_RATE)
    with wave.open(str(path), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(SAMPLE_RATE)
        for start in range(0, total, SAMPLE_RATE):
            end = min(start+SAMPLE_RATE, total)
            block = np.zeros(end-start, np.float32)
            for offset, samples in pending:
                lo, hi = max(start, offset), min(end, offset+len(samples))
                if lo < hi:
                    block[lo-start:hi-start] += samples[lo-offset:hi-offset]
            pending = [(o, s) for o, s in pending if o+len(s) > end]
            out.writeframes((np.clip(block, -1, 1)*32767).astype("<i2").tobytes())
