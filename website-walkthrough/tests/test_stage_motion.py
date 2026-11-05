import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from stage_motion import MotionStage, homography, layout, pose, validate_composition


def run(*command, input=None):
    result = subprocess.run([str(item) for item in command], input=input,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        raise RuntimeError(result.stderr.decode(errors="replace"))
    return result.stdout


class MotionCompositionTests(unittest.TestCase):
    def test_invalid_compositions_fail_before_rendering(self):
        invalid = [
            {"crop": [0, 0, 1]}, {"crop": [0, 0, float("nan"), 1]},
            {"crop": [True, 0, 1, 1]}, {"crop": [.5, 0, .4, 1]},
            {"crop": [0, 0, 1, 1.01]}, {"canvas": [321, 240]},
            {"canvas": [320, True]}, {"canvas": [320, 0]},
            {"canvas": [320, 7682]}, {"motion": True},
            {"motion": {"enabled": "yes"}},
            {"frame": False, "motion": {"enabled": True}},
            {"motion": {"keyframes": [[0, 0, 0, 0, 0]]}},
            {"motion": {"keyframes": [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]}},
            {"motion": {"keyframes": [[2.01, 0, 0, 0, 0, 0]]}},
            {"motion": {"keyframes": [[0, .021, 0, 0, 0, 0]]}},
            {"motion": {"keyframes": [[0, 0, -.021, 0, 0, 0]]}},
            {"motion": {"keyframes": [[0, 0, 0, 3.01, 0, 0]]}},
            {"motion": {"keyframes": [[0, 0, 0, 0, -3.01, 0]]}},
            {"motion": {"keyframes": [[0, 0, 0, 0, 0, 1.01]]}},
            {"motion": {"keyframes": [[0, 0, 0, 0, float("inf"), 0]]}},
            {"motion": {"settle": [[1, .5]]}},
            {"motion": {"settle": [[0, 2.01]]}},
            {"motion": {"settle": [[False, 1]]}},
        ]
        for plan in invalid:
            with self.subTest(plan=plan), self.assertRaises(ValueError):
                validate_composition(plan, 2)
        validate_composition({"motion": {"enabled": True,
            "keyframes": [[0, -.02, .02, -3, 3, -1], [2, .02, -.02, 3, -3, 1]],
            "settle": [[.5, 1]]}}, 2)

    def test_layout_preserves_cropped_source_aspect_and_centers_it(self):
        for canvas in ([320, 240], [240, 400], [400, 240]):
            plan = {"canvas": canvas, "crop": [.1, .2, .9, .8]}
            size, crop, bounds = layout(plan, 450, 300)
            self.assertEqual(size, tuple(canvas))
            self.assertEqual(crop, (45, 60, 405, 240))
            x, y, width, height = bounds
            # A source circle must keep its shape after fitting; only integer
            # pixel rounding may alter the 2:1 crop's displayed proportions.
            self.assertLessEqual(abs(width - 2 * height), 1)
            self.assertLessEqual(abs(2 * x + width - canvas[0]), 1)
            self.assertLessEqual(abs(2 * y + height - canvas[1]), 1)
            self.assertGreater(x, 0)
            self.assertGreater(y, 0)
        with self.assertRaises(ValueError):
            layout({"crop": [0, 0, .001, 1]}, 320, 240)

    def test_entire_plane_stays_visible_between_keyframes(self):
        for canvas in ([640, 360], [360, 640], [240, 240], [160, 640]):
            for source in ((1920, 1080), (1080, 1920)):
                plan = {"canvas": canvas, "motion": {"enabled": True, "settle": [],
                    "keyframes": [[0, -.02, .02, 3, -3, 1],
                                  [1, .02, -.02, -3, 3, -1],
                                  [2, -.02, .02, 3, -3, 1]]}}
                size, _, bounds = layout(plan, *source)
                x, y, w, h = bounds
                corners = np.array([[[x, y], [x+w, y], [x+w, y+h], [x, y+h]]], np.float32)
                for time in np.linspace(0, 2, 41):
                    with self.subTest(canvas=canvas, source=source, time=time):
                        projected = cv2.perspectiveTransform(corners,
                            homography(plan, time, 2, size, bounds))[0]
                        self.assertTrue(np.isfinite(projected).all())
                        self.assertGreaterEqual(float(projected.min()), -.001)
                        self.assertLessEqual(float(projected[:, 0].max()), size[0] + .001)
                        self.assertLessEqual(float(projected[:, 1].max()), size[1] + .001)

    def test_settle_freezes_interactions_and_eases_at_both_boundaries(self):
        fixed = [0.01, -.006, 2, -2, .5]
        plan = {"events": [{"time": 2, "x": .5, "y": .5}],
                "motion": {"enabled": True, "keyframes": [[0, *fixed], [4, *fixed]]}}
        for time in (1.55, 1.7, 2, 2.6, 2.75):
            np.testing.assert_array_equal(pose(plan, time, 4), np.zeros(5))
        np.testing.assert_allclose(pose(plan, 1, 4), fixed)
        np.testing.assert_allclose(pose(plan, 3.2, 4), fixed)
        # Small changes at either end of the ramp must be much smaller than
        # changes halfway along it, so entering or leaving the hold cannot jerk.
        for a, b in ((1.25, 1.55), (2.75, 3.05)):
            step = .001
            near_start = np.linalg.norm(pose(plan, a+step, 4)-pose(plan, a, 4))
            near_end = np.linalg.norm(pose(plan, b, 4)-pose(plan, b-step, 4))
            midpoint = (a+b)/2
            middle = np.linalg.norm(pose(plan, midpoint+step, 4)-pose(plan, midpoint, 4))
            self.assertGreater(middle, 0)
            self.assertLess(near_start, middle * .001)
            self.assertLess(near_end, middle * .001)
        plan["motion"]["settle"] = []
        np.testing.assert_allclose(pose(plan, 2, 4), fixed)
        plan["motion"]["settle"] = [[.3, .6]]
        np.testing.assert_array_equal(pose(plan, .45, 4), np.zeros(5))
        np.testing.assert_allclose(pose(plan, 2, 4), fixed)

    def test_keyframes_ease_and_legacy_plans_stay_still(self):
        plan = {"motion": {"enabled": True, "settle": [],
            "keyframes": [[0, 0, 0, 0, 0, 0], [2, .01, .01, 2, 2, .5]]}}
        values = np.array([pose(plan, time, 2) for time in np.linspace(0, 2, 41)])
        self.assertTrue((np.diff(values, axis=0) >= 0).all())
        self.assertLess(np.linalg.norm(values[1]-values[0]),
                        np.linalg.norm(values[20]-values[19]) * .05)
        self.assertLess(np.linalg.norm(values[-1]-values[-2]),
                        np.linalg.norm(values[20]-values[19]) * .05)
        for legacy in ({}, {"motion": {"enabled": False}}):
            for time in (0, .4, 1, 2):
                np.testing.assert_array_equal(pose(legacy, time, 2), np.zeros(5))
        floating = {"motion": {"enabled": True, "settle": []}}
        self.assertGreater(np.linalg.norm(pose(floating, .5, 2)), .1)

    def test_motion_keeps_backdrop_fixed_and_avoids_dark_edge_ringing(self):
        ow, oh = 360, 240
        x, y = np.meshgrid(np.arange(ow), np.arange(oh))
        backdrop = np.stack([70+x*.1, 90+y*.1, 110+(x+y)*.05], axis=2).astype(np.uint8)
        mask = Image.new("L", (240, 120))
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, 239, 119), radius=8, fill=255)
        alpha = np.asarray(mask, dtype=np.float32)[..., None]/255
        plan = {"motion": {"enabled": True, "settle": [],
            "keyframes": [[0, 0, 0, 0, 0, 0], [2, .02, -.02, 3, -3, 1]]}}
        stage = MotionStage(backdrop, alpha, (60, 60, 240, 120), 8, plan, 2)
        screen = np.full((120, 240, 3), (210, 225, 240), np.uint8)
        frames = [stage.render(screen, time) for time in (0, .5, 1, 1.5, 2)]
        self.assertGreater(np.count_nonzero(frames[0] != frames[-1]), 1000)
        for frame in frames:
            np.testing.assert_array_equal(frame[:20], backdrop[:20])
            np.testing.assert_array_equal(frame[:, :20], backdrop[:, :20])
            # The foreground is brighter than the backdrop. A 145/255 black
            # shadow is the darkest valid contribution; interpolation must not
            # create a darker black fringe around the moving rounded edge.
            lower_bound = np.floor(backdrop.astype(float) * (1-145/255)) - 1
            self.assertTrue((frame >= lower_bound).all(), "Moving edge has an unexpected dark halo")
            self.assertGreaterEqual(int(frame[100:140, 100:260].min()), 208)


class MotionRendererIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.work = Path(cls.temp.name)
        cls.source = cls.work / "marked-source.mkv"
        frame = np.full((240, 400, 3), (180, 210, 220), np.uint8)
        # Magenta strips simulate unwanted recording chrome. They surround a
        # 320x192 crop, while the marker uses ORIGINAL full-source coordinates.
        frame[:24] = frame[216:] = (255, 0, 255)
        frame[:, :40] = frame[:, 360:] = (255, 0, 255)
        cv2.circle(frame, (280, 96), 12, (230, 120, 25), -1)
        cv2.circle(frame, (120, 168), 10, (30, 190, 70), -1)
        run("ffmpeg", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgr24",
            "-s", "400x240", "-r", "8", "-i", "-", "-c:v", "ffv1", cls.source,
            input=frame.tobytes() * 16)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_real_crop_canvas_motion_encode_and_original_event_coordinates(self):
        plan = {"canvas": [320, 240], "crop": [.1, .1, .9, .9],
            "camera": [[0, 1, .5, .5], [2, 1, .5, .5]],
            "motion": {"enabled": True},
            "events": [{"time": .2, "x": .7, "y": .4}], "audio": "mute"}
        plan_path, output = self.work / "plan.json", self.work / "motion.mp4"
        plan_path.write_text(json.dumps(plan))
        run(sys.executable, ROOT / "scripts/render_walkthrough.py", self.source,
            "--plan", plan_path, "--output", output)
        run("ffmpeg", "-v", "error", "-i", output, "-f", "null", "-")
        metadata = json.loads(run("ffprobe", "-v", "error", "-show_streams",
            "-show_format", "-of", "json", output))
        video = next(s for s in metadata["streams"] if s["codec_type"] == "video")
        self.assertEqual((video["width"], video["height"]), (320, 240))
        self.assertEqual(video["codec_name"], "h264")
        self.assertAlmostEqual(float(metadata["format"]["duration"]), 2, delta=.13)
        decoded = np.frombuffer(run("ffmpeg", "-v", "error", "-i", output,
            "-f", "rawvideo", "-pix_fmt", "bgr24", "-"), np.uint8).reshape(-1, 240, 320, 3)
        self.assertEqual(len(decoded), 16)
        # Only excluded strips are magenta, and they must be absent throughout.
        magenta = (decoded[..., 0] > 200) & (decoded[..., 1] < 65) & (decoded[..., 2] > 200)
        self.assertLess(int(magenta.sum()), 5)
        self.assertGreater(float(np.abs(decoded[0].astype(float)-decoded[12]).mean()), .5)

        # Lossless preview comparison makes the original-source click location
        # observable independently of video compression and the camera motion.
        preview = self.work / "preview"
        run(sys.executable, ROOT / "scripts/render_walkthrough.py", self.source,
            "--plan", plan_path, "--output", preview, "--preview-times", ".35")
        highlighted = cv2.imread(str(preview / "00000.350.png"))
        plan["click_highlights"] = False
        plan_path.write_text(json.dumps(plan))
        plain_preview = self.work / "plain-preview"
        run(sys.executable, ROOT / "scripts/render_walkthrough.py", self.source,
            "--plan", plan_path, "--output", plain_preview, "--preview-times", ".35")
        plain = cv2.imread(str(plain_preview / "00000.350.png"))
        difference = np.any(highlighted != plain, axis=2)
        rows, cols = np.nonzero(difference)
        self.assertGreater(len(cols), 10)
        blue_marker = (plain[..., 0] > 210) & (plain[..., 1] < 150) & (plain[..., 2] < 60)
        marker_rows, marker_cols = np.nonzero(blue_marker)
        self.assertGreater(len(marker_cols), 100)
        self.assertAlmostEqual(float(cols.mean()), float(marker_cols.mean()), delta=1.5)
        self.assertAlmostEqual(float(rows.mean()), float(marker_rows.mean()), delta=1.5)
        # The encoded crop keeps the two source circles circular rather than
        # stretching the source to fill the differently shaped output canvas.
        self.assertLessEqual(abs(np.ptp(marker_cols)-np.ptp(marker_rows)), 2)


if __name__ == "__main__":
    unittest.main()
