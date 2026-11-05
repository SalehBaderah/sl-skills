# v2.1 validation report

Validated with Python 3.12, Pillow 13.0.0, and PyMuPDF in the current environment. This reports observed checks, not universal compatibility or proof of a host's UI behavior.

## Package and palette

- All eight digital colors verified against original filled vectors on page 11 of the unchanged source PDF: `#020624`, `#0F1543`, `#2F2447`, `#4A3B68`, `#58709C`, `#B7CDDD`, `#D4DAFA`, `#F6F9FC`.
- Original CMYK labels transcribed and checked against page-11 text. RGB values match the resolved HEX values. The original navy RGB and muted-blue HEX label conflicts remain explicitly documented; no print-profile conversion is implied.
- JSON, CSS, CSV, GIMP palette, editable SVG, and PNG swatches checked for all eight colors. PNG swatch pixels checked directly; visual preview inspected.
- White, purple, dark-purple, and navy emblem variants checked for seven unchanged native paths, consistent viewBox, matching transparent PNG alpha, and correct opaque fill colors. Source-PDF and geometry hashes verified.
- Local Markdown links, skill/interface metadata, Python syntax, and actual bundled examples checked.

## Automated tests

All **18 tests passed**, with no skips in this environment. Coverage includes light/dark and explicit palette variants, source preservation, transparency, low contrast, protected regions, bounds/size errors, no overwrite, explicit footer behavior, animation/CMYK/output-format refusal, surface-relative sizing, saved-file vs display status, and palette/source-PDF agreement.

PyMuPDF is an optional development dependency for the two PDF-source tests. Hosts without it report those two as skipped, not passed. Other runtime logo checks require Pillow.

## Integrated logo examples and delivery regression

The bundled shirt example is the final reference-guided raster mockup with the large visible white emblem on the purple shirt. The laptop detail shows exact-logo compositing on the laptop lid. Both were visually inspected. The example images are appearance references, not official logo masters or new user targets; the SVG/PNG logo files are canonical assets.

Earlier saved composites contained logos while the user reported no visible logo in their output. The skill now requires selecting and displaying the actual final branded artifact, inspecting normal-scale visibility and surface placement, and avoiding a blank-shirt intermediate or unrelated old preview as the final handoff. The helper explicitly reports `display_verified: false`; it cannot certify what a host showed to the user. No automated code test is claimed to prove host-visible image delivery.

## Remaining limits

Generative raster mockups can vary logo curves, text, grids, and identity; exact native/composited masters remain necessary for deterministic fidelity. Earlier strict-flat pixel-art trials retained gradients after a targeted retry, so pixel-perfect generation is not claimed. Fonts are referenced, not bundled. Full slide decks, Arabic text-heavy layouts, production CMYK/dielines, live web/UI edits, video, and every possible format have not all been exercised end to end. The helper does not simulate curved cloth/UVs.

The ZIP is portable skill content, not an installed/activated host skill. Import using the host's skill workflow.
