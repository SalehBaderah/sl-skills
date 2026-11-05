"""Verify digital colors and CMYK labels against the original PDF, not a screenshot."""

import json
import unittest
from pathlib import Path

try:
    import fitz
except ImportError:
    fitz = None

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipIf(fitz is None, "PDF source verification needs optional development dependency PyMuPDF")
class PaletteSourceTests(unittest.TestCase):
    def test_all_eight_digital_colors_exist_as_original_vector_fills(self):
        palette = json.loads((ROOT / "assets/palette.json").read_text())
        with fitz.open(ROOT / "references/ai-pioneers-guidelines-v2.pdf") as document:
            fills = {tuple(round(c*255) for c in drawing["fill"])
                     for drawing in document[10].get_drawings() if drawing.get("fill") and len(drawing["fill"]) == 3}
        self.assertEqual(len(palette["colors"]), 8)
        for value in palette["colors"].values():
            with self.subTest(hex=value):
                self.assertIn(tuple(bytes.fromhex(value[1:])), fills)
        self.assertEqual(palette["colors"]["midnight_navy"], "#020624")
        self.assertEqual(palette["colors"]["muted_blue"], "#58709C")

    def test_cmyk_labels_are_transcribed_from_the_guide(self):
        palette = json.loads((ROOT / "assets/palette.json").read_text())
        with fitz.open(ROOT / "references/ai-pioneers-guidelines-v2.pdf") as document:
            text = "".join(document[10].get_text().split())
        for swatch in palette["swatches"]:
            label = "CMYK" + ",".join(map(str, swatch["cmyk_source_label"]))
            with self.subTest(color=swatch["id"]):
                self.assertIn(label, text)


if __name__ == "__main__":
    unittest.main()
