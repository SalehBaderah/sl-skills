# Evaluation cases

Automated checks validate packaging and the deterministic logo helper. Visual cases validate the prompt/workflow on representative targets; they are not a guarantee of every tool, file format, or future generation.

## Automated

From the package root:

```bash
python scripts/validate_skill.py
python -m unittest discover -s tests -v
```

Verify front matter, links, all eight colors across JSON/CSS/CSV/GPL/SVG/PNG, original source-PDF colors/CMYK labels, source-PDF hash, seven original SVG paths, all four transparent logo variants, actual PNG colors, and runnable scripts. Exercise light/dark selection, alpha, clear-space/protected-region guards, surface-relative size, undersized/out-of-bounds placement, low contrast, no overwrite, deliberate footer resizing, and refusal of silent animation/CMYK flattening. A saved-file test does not verify user-visible display.

## Visual cases and acceptance criteria

| Case | Required preservation | AIP result and logo |
| --- | --- | --- |
| Plush mascot, shirt requested | Same face, expression, cream fur, pose, proportions | Purple T-shirt with a conspicuous white emblem printed on its chest; actual final preview must show it; no footer |
| Cat using a laptop | Same illustration, laptop geometry, surrounding objects/copy | Emblem appears as a print on the lid, with contrast and no clipping; no standalone substitute |
| Clay icon sheet | Same 15 subjects, layout, perspective, soft matte depth, bell badge 1 | Navy/purple surfaces, pale accents; one exact emblem in an inspected margin |
| Cat meme | Same cat/pose, desk/chair geometry, natural fur, exact LOCKED IN headline | Designed surfaces/background themed; emblem clear of cat and headline |
| Coffee/laptop pixel character | Happy eyes, steam, mug handle, feet, laptop angle, pixel steps, intentional source shading | AIP colors and same medium; requested logo uses a suitable object surface; strict-flat variants must also have discrete fills with no gradients/blur |
| Flat SVG | Original paths, viewBox, semantic holes, transparency, native editability | Exact palette fills; supplied emblem placed as vector, not raster |
| Arabic/English poster | Exact words, Arabic shaping/RTL, hierarchy, dimensions | Usable contrast; exact emblem in an empty margin; actual fonts disclosed |
| Chart/slide | Same data, scales, labels, order, page count | Distinguishable series; preserved semantic states; logo outside plot/text |
| Transparent icon | Alpha, silhouette, small-size legibility | Correct variant for intended background or logo omitted under auto |
| Dense fixed canvas | Every meaningful element and required dimensions | Logo omitted under auto with explanation; required mode flags constraints |
| Animated input | Timing, motion, frame count | Native frame-aware workflow or honest unsupported-export explanation |

For each actual run, inspect the output and record what was checked. Do not mark unexecuted cases as passed. If a generation adds gradients to pixel art or changes text/identity, correct it or report that specific limitation.
