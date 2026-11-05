# AI Pioneers Restyler v2.1

An updated skill for adapting designs to the AIP identity while preserving their original medium and meaning.

## What's included

- Exact team emblem: original vector curves extracted from the bundled guideline, matching the supplied logo; white, purple, dark-purple, and navy SVG/transparent PNG variants. See the [logo asset index](assets/logos/README.md).
- Integrated logo placement on clothing, laptop lids, packaging, and suitable native branding areas. Explicit on-object requests must not turn into footers or standalone marks. A surface-aware helper sizes against the usable panel.
- All eight AIP colors in [JSON](assets/palette.json), [CSS](assets/palette.css), [CSV](assets/palette.csv), [GIMP swatches](assets/palette.gpl), [SVG](assets/palette.svg), and [PNG](assets/palette.png), including resolved HEX/RGB and transcribed guide CMYK labels.
- Final-delivery checks that distinguish a saved composite from the image the host actually displays, plus integrated shirt/laptop examples.
- Recipes for pixel art, photos/memes, flat/vector art, 3D, posters, slides, charts, packaging, transparent assets, mixed media, and UI.
- AIP palette tokens, source guideline, visual references, package validation, and logo-placement tests.

The logo PNGs/SVGs are extracted assets, not the original screenshot's bytes. See [logo provenance and placement](references/logo-workflow.md).

## Complete palette

| Color | Digital HEX |
| --- | --- |
| Midnight navy | `#020624` |
| Deep navy | `#0F1543` |
| Dark purple | `#2F2447` |
| Mid purple | `#4A3B68` |
| Muted blue | `#58709C` |
| Pale blue | `#B7CDDD` |
| Pale lavender | `#D4DAFA` |
| Cool off-white | `#F6F9FC` |

White `#FFFFFF` is included for reversed logos in addition to the eight palette colors. The guide repeats an incorrect purple HEX on the muted-blue swatch and reverses the first navy's printed RGB; bundled digital values are verified against original PDF vectors. CMYK source labels are included as guide data, not a new profile-managed print specification. Available palette colors do not require every design to use all eight.

## Use

Keep the `restyle-ai-pioneers` folder intact in a skill-capable host. Import/install the folder or ZIP using that host's skill workflow; this archive does not itself install or activate a skill.

Example requests:

- “Use $restyle-ai-pioneers on this image.”
- “Apply AIP colors, preserve the pixel-art grid, logo required.”
- “Apply AIP style and print the white team emblem on its purple T-shirt.”
- “Restyle this photo subtly; keep natural skin tones.”
- “Adapt this chart to AIP without changing labels/data; logo none.”
- “Update this editable SVG in AIP colors and keep it editable.”

Defaults are balanced strength, source light/dark theme, preserved dimensions/medium, and integrated logo auto. An explicit logo/location request implies required placement. No footer unless requested. Use explicit instructions to override defaults.

## Helper setup

Raster restyling requires the host's image-editing tool. Exact-logo compositing requires Python 3.10+ and Pillow:

```bash
python -m pip install -r requirements.txt
python scripts/brand_image.py --help
python scripts/validate_skill.py
python -m unittest discover -s tests -v
```

Asset regeneration uses `python scripts/prepare_assets.py` (development requirements) and `python scripts/prepare_palette.py` (Pillow). Bundled assets are already built; regeneration is optional. PDF source-verification tests need the optional development dependency PyMuPDF; they report a skip when unavailable. Do not install dependencies again when available.

## Practical limits

The skill adapts many design types, but actual editing/export depends on host tools. Generative raster edits do not guarantee exact pixel grids, copy, color hex values, or identity. Native edits and exact-logo composition improve fidelity. Fonts are referenced, not distributed. The helper supports static sRGB previews and PNG output; it is not a CMYK, animation, or curved-surface mockup engine. Visual inspection is required after each transformation.

See [evaluation cases](references/evaluation.md). Do not describe an unrun case as tested or an image preview as an editable native document.

See [validation report](references/validation-report.md) for the checks actually run on this release, including the strict pixel-art generation limitation found during testing.
