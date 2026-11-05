import sys
import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"scripts"))
from sound_effects import EFFECTS, SAMPLE_RATE, cues, synthesize, write_effects
from render_walkthrough import validate


class SoundTests(unittest.TestCase):
    def test_effects_are_finite_distinct_and_faded(self):
        signals = [synthesize(effect) for effect in sorted(EFFECTS)]
        for signal in signals:
            self.assertTrue(np.isfinite(signal).all())
            self.assertGreater(float(np.max(np.abs(signal))), .05)
            self.assertLessEqual(float(np.max(np.abs(signal))), 1)
            self.assertEqual(float(signal[0]), 0)
            self.assertLess(abs(float(signal[-1])), .01)
        self.assertEqual(len({s.tobytes() for s in signals}), len(EFFECTS))

    def test_timeline_silence_gain_and_tail(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/"effects.wav"
            write_effects(path, [(.25, "touch", .3), (.98, "open", .3)], 1)
            with wave.open(str(path)) as w:
                self.assertEqual(w.getnframes(), SAMPLE_RATE)
                samples = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2")
            self.assertFalse(np.any(samples[:12000]))
            self.assertGreater(int(np.max(np.abs(samples[12000:16000]))), 100)
            self.assertFalse(np.any(samples[20000:46000]))
            self.assertGreater(int(np.max(np.abs(samples[47100:]))), 0)

    def test_compatibility_disable_and_mute(self):
        event = {"time": .5, "x": .5, "y": .5}
        plan = {"events": [event]}
        self.assertEqual(cues(plan, 1), [])
        plan["sound_effects"] = {"enabled": True}
        self.assertEqual(cues(plan, 1), [(.5, "click", .35)])
        plan["audio"] = "mute"
        self.assertEqual(cues(plan, 1), [])
        plan["audio"] = "preserve"
        event["sound"] = "none"
        self.assertEqual(cues(plan, 1), [])

    def test_invalid_plans_fail(self):
        cases = [
            {"sounds": [{"time": -1, "effect": "click"}]},
            {"sounds": [{"time": .5, "effect": "unknown"}]},
            {"sound_effects": {"volume": float("nan")}},
            {"sound_effects": {"volume": 2}},
            {"sound_effects": {"enabled": "false"}},
            {"events": [{"time": .5, "x": .5, "y": .5, "sound": "music"}]},
            {"cursor": [[0, .5, .5]]},
        ]
        for plan in cases:
            with self.subTest(plan=plan), self.assertRaises(ValueError): validate(plan, 1)


if __name__ == "__main__": unittest.main()
