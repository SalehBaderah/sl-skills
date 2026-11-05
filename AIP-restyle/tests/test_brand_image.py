"""Behavioral checks for exact-logo placement; no image service/network needed."""

import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from brand_image import brand_image


class LogoPlacementTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.input = self.root / "input.png"
        self.output = self.root / "output.png"

    def make(self, color, size=(400, 400)):
        image = Image.new("RGBA", size, color)
        ImageDraw.Draw(image).rectangle((30, 40, 110, 200), fill="#58709C")
        image.save(self.input)
        return image

    def test_light_canvas_picks_navy_and_preserves_source_outside_mark(self):
        before = self.make("#F6F9FC")
        original_bytes = self.input.read_bytes()
        result = brand_image(self.input, self.output, region=(220, 220, 180, 180),
                             logo_width=64, avoid=[(30, 40, 81, 161)])
        self.assertEqual(result["variant"], "navy")
        self.assertEqual(self.input.read_bytes(), original_bytes)
        with Image.open(self.output) as after:
            self.assertEqual(after.size, before.size)
            delta = ImageChops.difference(before, after).convert("RGB")
            bbox = delta.getbbox()
            self.assertIsNotNone(bbox)
            x, y, w, h = result["logo_bounds_xywh"]
            self.assertGreaterEqual(bbox[0], x)
            self.assertGreaterEqual(bbox[1], y)
            self.assertLessEqual(bbox[2], x+w)
            self.assertLessEqual(bbox[3], y+h)
            self.assertEqual(after.crop((0, 0, 220, 220)).tobytes(), before.crop((0, 0, 220, 220)).tobytes())

    def test_dark_canvas_picks_white(self):
        self.make("#020624")
        result = brand_image(self.input, self.output, region=(220, 220, 180, 180), logo_width=64)
        self.assertEqual(result["variant"], "white")
        self.assertGreaterEqual(result["contrast_5th_percentile"], 3)

    def test_transparency_preserved_with_explicit_viewing_background(self):
        before = self.make((0, 0, 0, 0))
        result = brand_image(self.input, self.output, region=(220, 220, 180, 180),
                             variant="white", background="#020624")
        self.assertEqual(result["variant"], "white")
        with Image.open(self.output) as after:
            self.assertEqual(after.getpixel((0, 0)), before.getpixel((0, 0)))
            self.assertEqual(after.getpixel((0, 0))[3], 0)
            self.assertEqual(after.size, before.size)

    def test_unknown_transparent_background_refused(self):
        self.make((0, 0, 0, 0))
        with self.assertRaisesRegex(ValueError, "transparent"):
            brand_image(self.input, self.output, region=(220, 220, 180, 180))
        self.assertFalse(self.output.exists())

    def test_protected_content_including_clear_space_refused(self):
        self.make("#F6F9FC")
        with self.assertRaisesRegex(ValueError, "protected"):
            brand_image(self.input, self.output, region=(220, 220, 180, 180), avoid=[(220, 220, 180, 180)])
        self.assertFalse(self.output.exists())

    def test_insufficient_contrast_refused(self):
        self.make("#F6F9FC")
        with self.assertRaisesRegex(ValueError, "contrast"):
            brand_image(self.input, self.output, region=(220, 220, 180, 180), variant="white")

    def test_region_constraints_refused(self):
        self.make("#F6F9FC")
        for region in [(-1, 0, 50, 50), (380, 380, 100, 100), (250, 250, 10, 10), (0, 0, 0, 200)]:
            with self.subTest(region=region), self.assertRaises(ValueError):
                brand_image(self.input, self.output, region=region)
        with self.assertRaisesRegex(ValueError, "requires"):
            brand_image(self.input, self.output)
        with self.assertRaisesRegex(ValueError, "do not fit"):
            brand_image(self.input, self.output, region=(250, 250, 100, 100), logo_width=90)

    def test_never_overwrites_source_or_existing_output(self):
        self.make("#F6F9FC")
        original_bytes = self.input.read_bytes()
        with self.assertRaisesRegex(ValueError, "overwrite"):
            brand_image(self.input, self.input, region=(220, 220, 180, 180))
        self.output.write_bytes(b"keep this existing file")
        with self.assertRaisesRegex(ValueError, "overwrite"):
            brand_image(self.input, self.output, region=(220, 220, 180, 180))
        self.assertEqual(self.input.read_bytes(), original_bytes)
        self.assertEqual(self.output.read_bytes(), b"keep this existing file")

    def test_footer_preserves_all_original_pixels(self):
        before = self.make("#F6F9FC")
        result = brand_image(self.input, self.output, mode="footer", logo_width=64)
        with Image.open(self.output) as after:
            self.assertEqual(after.width, before.width)
            self.assertGreater(after.height, before.height)
            self.assertEqual(after.crop((0, 0, *before.size)).tobytes(), before.tobytes())
        self.assertEqual(result["original_size"], [400, 400])

    def test_transparent_footer_preserves_original_alpha(self):
        before = self.make((0, 0, 0, 0))
        brand_image(self.input, self.output, mode="footer", footer_color="transparent",
                    variant="white", background="#020624")
        with Image.open(self.output) as after:
            self.assertEqual(after.crop((0, 0, *before.size)).tobytes(), before.tobytes())
            self.assertEqual(after.getpixel((0, after.height-1))[3], 0)

    def test_animated_input_not_silently_flattened(self):
        gif = self.root / "animated.gif"
        Image.new("RGB", (100, 100), "red").save(gif, save_all=True,
            append_images=[Image.new("RGB", (100, 100), "blue")], duration=100, loop=0)
        with self.assertRaisesRegex(ValueError, "Animated"):
            brand_image(gif, self.output, mode="footer")

    def test_cmyk_not_silently_converted(self):
        cmyk = self.root / "print.jpg"
        Image.new("CMYK", (100, 100)).save(cmyk)
        with self.assertRaisesRegex(ValueError, "CMYK"):
            brand_image(cmyk, self.output, mode="footer")

    def test_lossy_or_non_alpha_output_refused(self):
        self.make("#F6F9FC")
        with self.assertRaisesRegex(ValueError, "PNG"):
            brand_image(self.input, self.root / "output.jpg", mode="footer")

    def test_surface_size_uses_panel_not_whole_canvas(self):
        before = self.make("#2F2447", size=(1200, 1600))
        result = brand_image(self.input, self.output, mode="surface", region=(200, 500, 400, 500))
        x, y, w, h = result["logo_bounds_xywh"]
        self.assertEqual(w, 220)
        self.assertEqual(result["logo_fraction_of_region_width"], 0.55)
        self.assertEqual(result["variant"], "white")
        self.assertEqual(result["output_size"], list(before.size))
        with Image.open(self.output) as after:
            diff = ImageChops.difference(before, after).convert("RGB").getbbox()
            self.assertGreaterEqual(diff[0], x)
            self.assertGreaterEqual(diff[1], y)
            self.assertLessEqual(diff[2], x+w)
            self.assertLessEqual(diff[3], y+h)

    def test_palette_logo_variants_render_correct_ink(self):
        self.make("#F6F9FC")
        for variant, fill in [("navy", (2, 6, 36)), ("dark-purple", (47, 36, 71))]:
            with self.subTest(variant=variant):
                path = self.root / f"{variant}.png"
                result = brand_image(self.input, path, mode="surface", region=(220, 220, 180, 180), variant=variant)
                self.assertEqual(result["variant"], variant)
                with Image.open(path) as output:
                    self.assertIn(fill, {color for count, color in output.convert("RGB").getcolors(400*400)})

    def test_saved_file_does_not_claim_host_display_was_verified(self):
        self.make("#2F2447")
        result = brand_image(self.input, self.output, mode="surface", region=(220, 220, 180, 180))
        self.assertTrue(self.output.is_file())
        self.assertIs(result["display_verified"], False)
        self.assertEqual(result["placement"], "integrated surface print")


if __name__ == "__main__":
    unittest.main()
