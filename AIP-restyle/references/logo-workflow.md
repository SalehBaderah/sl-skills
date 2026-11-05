# Integrated-logo workflow · v2.1

## Actual bundled assets

The user's supplied white emblem matches the original standalone emblem on guideline page 6. Its seven filled vector paths were extracted without tracing or generative reconstruction. The screenshot was a visual reference, not a downloadable original file; do not claim the bundle contains its original upload bytes. The dark background is presentation background, not part of the emblem.

See [asset index](../assets/logos/README.md). White, purple, dark-purple, and navy variants are provided as native SVG and 2048px-wide transparent PNG, with identical geometry/alpha. The [manifest](../assets/logos/manifest.json) records the source hash, page, geometry hash, and variants. White/purple are evidenced in the guide; dark-purple/navy are user-authorized palette recolors. This is the emblem, not an invented bilingual wordmark.

## Where the logo belongs

If the user specifies a shirt, put it on that shirt. If they specify a laptop, put it on its lid. For unspecified placement, choose a suitable existing designed surface: clothing, a bag, packaging, a device, or the native branding area of a layout. A footer or a loose logo beside the character does not satisfy an on-object request. No footer, banner, margin extension, or new logo container unless requested.

`logo: auto` integrates it where suitable. `logo: required` includes explicit logo/location requests and cannot be silently dropped. `logo: none` suppresses new branding. Keep existing copy; replacing a decorative mark requires authorization from the requested edit/context. A tiny functional icon may need omission under auto rather than an illegible logo.

## Choose the output workflow first

### A. Exact native or composited master

Use the supplied SVG in native layouts/mockups, preserving paths, proportions, and orientation. For a simple front-facing raster surface, the helper places the exact PNG without changing pixels elsewhere. For a complex curved surface, use a suitable native texture/mockup workflow if available; do not claim a flat stamp simulates folds or UVs.

An image tool may prepare a clean surface internally, but a blank-shirt/laptop intermediate is not the final deliverable. Complete exact placement and deliver the actual branded master using the host's supported file/image mechanism. Do not assume the earlier generated-image card updated itself when a different local file was saved.

### B. Reference-guided raster mockup

For an image-tool mockup, provide the target and bundled emblem as explicitly labeled references through the tool's supported controls. Request a clearly visible print on the chosen surface in the generated image itself. Preserve the seven-shape arrangement and compare against the source. Do not prompt for a blank shirt when that generated image will be the only visible final result.

If local vs recent-image controls cannot be mixed, follow the active schema. Never combine mutually exclusive controls or substitute an old target. Use an exact composited master as the input to a final render when possible. Generative rendering may vary curves/pixels and cannot guarantee native logo geometry: preserve the exact master separately where exact fidelity is required, and describe the visible mockup accurately.

## Visibility, material, and color

- Start with white on purple/navy; use navy/dark-purple on pale fabric/panels. Purple is also bundled. The user authorized AIP-palette recolors for visibility. Do not alter geometry or substitute a different symbol.
- Scale against the usable surface, not the whole canvas. For a central chest print, about 40–55% of usable panel width is an application starting point, subject to clear space and actual cloth geometry. Check the whole image at normal viewing size; a logo visible only in a zoomed crop is insufficient.
- A real print should sit within the surface and follow believable material/light/perspective. Avoid badge borders, floating marks, excessive glow, fading, or arbitrary distortion. Natural material shading is not a reason to make the logo illegible.
- Inspect guideline page 7 for clear space. Helper defaults are application spacing choices (0.5× emblem height on surfaces, 0.65× in layouts), not official numeric requirements. The helper enforces its configured spacing but cannot certify the official layout visually.
- The 3:1 contrast guard over 95% of opaque pixels is an engineering threshold, not an official brand or WCAG-logo mandate. Check visually too.

## Surface helper

Choose a blank, inspected, front-facing usable panel that includes room for the print and clear space. Coordinates below are illustrative.

```bash
python scripts/brand_image.py shirt.png shirt-aip.png \
  --mode surface --region 300 790 410 310 --variant white
```

Surface mode targets 55% of region width, reduces it only to fit its spacing, preserves dimensions/alpha, and prints a JSON report. If the usable panel is too small, reframe or choose an appropriate authorized workflow; do not silently deliver an invisible mark. Use `--logo-width` for an explicit size; impossible requests fail instead of covering content.

For an existing layout branding area, use `--mode overlay --region X Y W H`. `--avoid X Y W H` protects text/subject rectangles, including clear-space overlap. Automatic color selection compares all four bundled variants. `--variant navy`, `dark-purple`, `purple`, or `white` chooses explicitly.

Footer mode exists only for an explicit footer/canvas-extension request. It changes aspect ratio and must never be an automatic fallback for a shirt/object request.

For transparent regions, `--background '#020624'` supplies the intended viewing background for contrast checking only; it does not fill alpha. Check the intended viewing background and preserve transparency. The helper handles static sRGB previews and PNG output, not animation/CMYK/curved-surface rendering. It never overwrites input or existing output.

## Required final handoff

Follow [final-delivery.md](final-delivery.md). A successful helper report proves a file was written, not that the user saw it. Display the actual branded output, inspect the full image and logo location, and provide the real file when supported. Do not finish by showing only the source, a blank-shirt generation, or the standalone emblem.
