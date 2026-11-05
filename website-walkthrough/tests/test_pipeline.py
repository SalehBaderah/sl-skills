import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def run(*command):
    try:
        return subprocess.check_output([str(x) for x in command], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(exc.output.decode(errors="replace")) from exc


def probe(path):
    return json.loads(run("ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path))


def audio_samples(path):
    return np.frombuffer(run("ffmpeg", "-v", "error", "-i", path, "-map", "0:a:0", "-f", "f32le", "-ac", "1", "-ar", "48000", "-"), dtype="<f4")


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.work = Path(cls.temp.name)
        cls.silent = cls.work/"silent.mp4"
        cls.source_audio = cls.work/"source-audio.mp4"
        run("ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc2=size=320x240:rate=12:duration=2", "-c:v", "libx264", "-pix_fmt", "yuv420p", cls.silent)
        run("ffmpeg", "-v", "error", "-i", cls.silent, "-f", "lavfi", "-i", "sine=frequency=330:sample_rate=48000:duration=2", "-c:v", "copy", "-c:a", "aac", "-shortest", cls.source_audio)

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def render(self, name, plan, source=None):
        path, output = self.work/f"{name}.json", self.work/f"{name}.mp4"
        path.write_text(json.dumps(plan))
        run(sys.executable, ROOT/"scripts/render_walkthrough.py", source or self.silent, "--plan", path, "--output", output)
        run("ffmpeg", "-v", "error", "-i", output, "-f", "null", "-")
        data = probe(output)
        video = next(s for s in data["streams"] if s["codec_type"] == "video")
        self.assertEqual((video["width"], video["height"]), (320, 240))
        self.assertLess(abs(float(data["format"]["duration"])-2), .12)
        return output, data

    def test_silent_source_gets_timed_effects(self):
        output, data = self.render("effects", {"sound_effects": {"enabled": True}, "events": [{"time": .6, "x": .5, "y": .5, "sound": "open"}]})
        self.assertTrue(any(s["codec_type"] == "audio" for s in data["streams"]))
        samples = audio_samples(output)
        self.assertLess(float(np.max(np.abs(samples[:24000]))), .0001)
        self.assertGreater(float(np.max(np.abs(samples[28800:38000]))), .02)
        self.assertLess(float(np.max(np.abs(samples[48000:]))), .0001)

    def test_source_audio_is_retained_in_mix(self):
        output, _ = self.render("mix", {"sound_effects": {"enabled": True}, "sounds": [{"time": .7, "effect": "touch"}]}, self.source_audio)
        samples = audio_samples(output)
        # The original source tone remains before and after the effect.
        for start in (.15, 1.2):
            segment = samples[int(start*48000):int((start+.2)*48000)]
            peak = np.argmax(np.abs(np.fft.rfft(segment)))*48000/len(segment)
            self.assertAlmostEqual(peak, 330, delta=6)
        self.assertLessEqual(float(np.max(np.abs(samples))), 1)

    def test_mute_removes_all_audio(self):
        _, data = self.render("mute", {"audio": "mute", "sound_effects": {"enabled": True}, "sounds": [{"time": .5, "effect": "click"}]}, self.source_audio)
        self.assertFalse(any(s["codec_type"] == "audio" for s in data["streams"]))

    def test_old_plan_remains_silent_on_silent_source(self):
        _, data = self.render("legacy", {"events": [{"time": .5, "x": .5, "y": .5}]})
        self.assertFalse(any(s["codec_type"] == "audio" for s in data["streams"]))

    def test_disabled_effects_keep_original_audio(self):
        output, _ = self.render("disabled", {"sound_effects": {"enabled": False}, "sounds": [{"time": .5, "effect": "success"}]}, self.source_audio)
        samples = audio_samples(output)
        source = audio_samples(self.source_audio)
        n = min(len(samples), len(source))
        self.assertGreater(float(np.corrcoef(samples[:n], source[:n])[0, 1]), .99)


if __name__ == "__main__": unittest.main()
