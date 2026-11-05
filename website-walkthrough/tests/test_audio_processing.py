"""Exercise the emitted filters through real encoding and audio decoding."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audio_processing import audio_options, validate_audio_processing


RATE = 48000
DURATION = 2


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg is required")
class AudioProcessingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.times = np.arange(RATE * DURATION) / RATE
        self.effects = np.zeros(len(self.times))
        mask = (self.times >= .6) & (self.times < .8)
        self.effects[mask] = .1 * np.sin(2 * np.pi * 3000 * self.times[mask])
        self.write_wav(self.root / "effects.wav", self.effects)

    def write_wav(self, path, samples):
        channels = 1 if samples.ndim == 1 else samples.shape[1]
        with wave.open(str(path), "wb") as audio:
            audio.setnchannels(channels)
            audio.setsampwidth(2)
            audio.setframerate(RATE)
            audio.writeframes((np.clip(samples, -1, 1) * 32767).astype("<i2").tobytes())

    def render(self, samples, plan, effects=False, stream=None):
        source = self.root / "source.wav"
        self.write_wav(source, samples if samples is not None else np.zeros(len(self.times)))
        if samples is not None and stream is None:
            channels = 1 if samples.ndim == 1 else samples.shape[1]
            stream = {"channels": channels}
        output = self.root / "output.mp4"
        command = [
            "ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
            "color=c=black:s=160x120:r=10:d=2", "-i", str(source),
        ]
        if effects:
            command += ["-i", str(self.root / "effects.wav")]
        command += ["-map", "0:v:0", "-c:v", "libx264", "-preset", "ultrafast"]
        command += audio_options(plan, stream, effects)
        command += ["-t", str(DURATION), str(output)]
        subprocess.run(command, check=True, capture_output=True)
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(output)],
            check=True, capture_output=True, text=True,
        )
        streams = json.loads(probe.stdout)["streams"]
        audio = next((s for s in streams if s["codec_type"] == "audio"), None)
        if audio is None:
            return None, None
        decoded = subprocess.run(
            ["ffmpeg", "-v", "error", "-i", str(output), "-map", "0:a:0",
             "-f", "f32le", "-ar", str(RATE), "-"],
            check=True, capture_output=True,
        )
        return audio, np.frombuffer(decoded.stdout, dtype="<f4").reshape(-1, audio["channels"])

    def amplitude(self, samples, frequency, start=.3, end=1.3):
        window = samples[int(start * RATE):int(end * RATE)]
        phase = np.arange(len(window)) / RATE
        return abs(np.sum(window * np.exp(-2j * np.pi * frequency * phase))) * 2 / len(window)

    def test_stereo_tones_stay_isolated_when_mixing_mono_effect(self):
        source = np.column_stack((
            .1 * np.sin(2 * np.pi * 330 * self.times),
            .1 * np.sin(2 * np.pi * 660 * self.times),
        ))
        stream, result = self.render(source, {}, effects=True)
        self.assertEqual(stream["channels"], 2)
        self.assertEqual(stream["channel_layout"], "stereo")
        for channel, own, other in [(0, 330, 660), (1, 660, 330)]:
            amplitude = self.amplitude(result[:, channel], own)
            self.assertGreater(amplitude, .08)
            self.assertLess(self.amplitude(result[:, channel], other), amplitude * .03)
            self.assertGreater(self.amplitude(result[:, channel], 3000, .62, .78), .04)

    def test_hum_harmonics_drop_while_speech_frequency_is_preserved(self):
        source = sum(a * np.sin(2 * np.pi * f * self.times)
                     for f, a in [(60, .15), (120, .04), (180, .02), (330, .07)])
        _, result = self.render(source, {"audio_cleanup": {"hum_hz": 60}})
        result = result[:, 0]
        for frequency, original in [(60, .15), (120, .04), (180, .02)]:
            self.assertLess(self.amplitude(result, frequency, .8, 1.8), original * .05)
        self.assertAlmostEqual(self.amplitude(result, 330, .8, 1.8), .07, delta=.008)

    def test_disabled_cleanup_preserves_hum_and_mono(self):
        source = .15 * np.sin(2 * np.pi * 60 * self.times)
        stream, result = self.render(source, {"audio_cleanup": {"enabled": False}})
        self.assertEqual(stream["channels"], 1)
        self.assertAlmostEqual(self.amplitude(result[:, 0], 60), .15, delta=.012)

    def test_mute_has_no_audio_even_with_effects_and_cleanup(self):
        stream, result = self.render(np.zeros(len(self.times)), {
            "audio": "mute", "audio_cleanup": {"hum_hz": 50},
        }, effects=True)
        self.assertIsNone(stream)
        self.assertIsNone(result)

    def test_no_source_keeps_effects_and_ignores_source_cleanup(self):
        stream, result = self.render(None, {"audio_cleanup": {"hum_hz": 60}}, effects=True)
        self.assertEqual(stream["channels"], 1)
        self.assertLess(float(np.max(np.abs(result[:int(.4 * RATE)]))), .001)
        self.assertGreater(self.amplitude(result[:, 0], 3000, .62, .78), .08)

    def test_no_source_and_no_effects_has_no_audio(self):
        stream, _ = self.render(None, {})
        self.assertIsNone(stream)

    def test_declared_surround_layout_is_retained(self):
        source = np.column_stack([
            .04 * np.sin(2 * np.pi * frequency * self.times)
            for frequency in [330, 440, 550, 80, 660, 770]
        ])
        stream, result = self.render(source, {}, effects=True,
                                     stream={"channels": 6, "channel_layout": "5.1"})
        self.assertEqual(stream["channels"], 6)
        self.assertEqual(stream["channel_layout"], "5.1")
        self.assertGreater(self.amplitude(result[:, 0], 330), .025)
        self.assertLess(self.amplitude(result[:, 0], 440), .002)


class AudioValidationTests(unittest.TestCase):
    def test_invalid_cleanup_fails_before_encoding(self):
        cases = [
            {"audio": "drop"}, {"audio_cleanup": None}, {"audio_cleanup": {}},
            {"audio_cleanup": {"enabled": "false"}},
            {"audio_cleanup": {"hum_hz": 55}}, {"audio_cleanup": {"hum_hz": True}},
            {"audio_cleanup": {"hum_hz": 60, "harmonics": 0}},
            {"audio_cleanup": {"hum_hz": 50, "harmonics": 5}},
            {"audio_cleanup": {"hum_hz": 60, "harmonics": 2.5}},
            {"audio_cleanup": {"hum_hz": 60, "harmonics": True}},
        ]
        for plan in cases:
            with self.subTest(plan=plan), self.assertRaises(ValueError):
                validate_audio_processing(plan)

    def test_unsupported_or_ambiguous_layouts_are_rejected(self):
        for stream in [
            {"channels": 6}, {"channels": 6, "channel_layout": "unknown"},
            {"channels": 2, "channel_layout": "mono"},
            {"channels": 6, "channel_layout": "custom"}, {"channels": True},
        ]:
            with self.subTest(stream=stream), self.assertRaises(ValueError):
                audio_options({}, stream, True)


if __name__ == "__main__":
    unittest.main()
