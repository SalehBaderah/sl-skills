# AI Pioneers identity reference

## Source and interpretation

Use `ai-pioneers-guidelines-v2.pdf`, copied unchanged from the user's `AIPioneers Guideline V2 (1).pdf`, as the authority. It has 31 pages and is dated June 2026; page footers say Brand Guidelines V2.0 while the cover says Version 0.2. Preserve that provenance rather than inventing a reconciled version number.

The brand is AI Pioneers / Artificial Intelligence Pioneers / رواد الذكاء الاصطناعي. Its stated logo idea is connectivity and continuous growth, with a community shaping the future through knowledge and technology (page 5). The guide asks for creative flexibility alongside consistent recognition (page 3).

Treat items marked **application default** as useful treatments inferred from the shown examples, not additional official mandates.

## Digital palette (page 11)

| Descriptive role | Use hex | RGB | Evidence |
| --- | --- | --- | --- |
| Midnight navy | `#020624` | 2, 6, 36 | Printed hex and vector swatch agree; RGB label conflicts. |
| Deep navy | `#0F1543` | 15, 21, 67 | Printed hex/RGB and vector swatch agree. |
| Core dark purple | `#2F2447` | 47, 36, 71 | Printed hex/RGB and vector swatch agree. |
| Mid purple | `#4A3B68` | 74, 59, 104 | Printed hex/RGB and vector swatch agree. |
| Muted blue | `#58709C` | 88, 112, 156 | Hex derived from printed RGB; verified against PDF vector fill. |
| Pale blue | `#B7CDDD` | 183, 205, 221 | Printed hex/RGB and vector swatch agree. |
| Pale lavender | `#D4DAFA` | 212, 218, 250 | Printed hex/RGB and vector swatch agree. |
| Cool off-white | `#F6F9FC` | 246, 249, 252 | Printed hex/RGB and vector swatch agree. |

Account for two labeling conflicts:

- The first navy's printed RGB is `36, 6, 2`, but its printed hex and original vector fill are `#020624` / `2, 6, 36`. Use the latter for digital work.
- The muted blue repeats the purple hex `#4a3b68`. Its printed RGB and original vector fill are `88, 112, 156`, which convert to `#58709C`. This is a documented resolution from source evidence, not a newly approved brand color.

Do not use screenshot sampling to override these values: PDF color management can change displayed pixels. For print work, consult the original CMYK labels and production requirements rather than assuming RGB conversion is approved. Pure white also appears in reversed logos/text. Treat the role names as descriptive: the guide gives no percentages or numeric primary/secondary allocation.

**Application default:** Give navy and purple the largest role in a dark treatment, with pale blue/lavender accents and white/off-white contrast. For a light treatment, use off-white or transparency with navy/purple foregrounds. Use subtle navy-to-purple gradients where helpful; the cover and social examples support them. Keep bright neon, rainbow gradients, heavy glow, and busy technological clichés out of the default treatment.

## Typography (page 12)

| Language | Family | Shown weights |
| --- | --- | --- |
| English | Gilroy | Regular, ExtraBold |
| Arabic | Droid Arabic Naskh | Regular, Bold |

Use the actual families when font files are available. The PDF is a reference, not an included complete font distribution. Do not claim the correct font was used when substituting. For editable production work requiring exact type, obtain authorized fonts if unavailable; for a preview, name a substitute briefly. Preserve Arabic shaping, right-to-left order, punctuation, and exact copy. Do not translate/transliterate unless requested.

**Application default:** Use clear hierarchy, generous spacing, and confident headings. Apply typography only when the requested asset contains text; do not add text to an icon merely to use the fonts.

## Shape and pattern language (pages 5, 13)

The emblem and supporting pattern use circular endpoints and fluid, rounded connecting forms. Page 13 explicitly shows FILL and OUTLINE treatments, in sparse and dense horizontal arrangements. The pattern supports the design with depth and character.

**Application default:** Use smooth organic connectors, rounded terminals, repeated rhythms, and ample negative space. Borrow this vocabulary selectively when restyling an object. Use subdued pattern fragments at edges or in open background areas. Use the exact original pattern when a production application calls for it; a new illustrative shape inspired by this language is not the official emblem.

Keep pattern and logo rules distinct: outline pattern artwork is allowed on page 13, while outline-only treatment of the identifying logo is prohibited on page 9. A decorative low-contrast motif is not permission to lower the identifying logo's opacity.

## Logo rules (pages 6-10)

The standalone emblem supplied by the user is bundled as exact extracted SVG paths and transparent PNGs in `assets/logos/`, with provenance in `manifest.json`. White/purple match the guide; dark-purple/navy are user-authorized AIP-palette recolors. The v2.1 default integrates it into a suitable designed surface or native branding area (`logo: auto`); an explicit logo/location request implies `required`, and `none` suppresses it. A footer is not a substitute for a requested shirt/object print. These are user-requested workflow choices, not newly discovered official brand rules. See [logo-workflow.md](logo-workflow.md). Do not invent a replacement logo or wordmark; distinguish exact native masters from reference-guided generative mockups.

- Page 6 permits emblem and wordmark together or independently, depending on application.
- Preserve official geometry, proportions, orientation, and wordmark. Use exact source artwork or faithful extraction; do not redraw from memory or synthesize the brand name inside the logo.
- Follow page 7's illustrated clear-space proportions around the entire logo and keep the region empty. No textual numeric multiplier is specified; do not present a guessed measurement as official.
- Page 8 requires sufficient background contrast. Use the appropriate approved light/dark variant; avoid dark purple on a similarly dark background.
- Page 9 prohibits outline-only logo, rotation, stretching/squeezing, horizontal flipping, adding containers, and reducing logo opacity.
- Page 10 requires preserved proportions, colors, and clear space in co-branding. Do not alter partner logos or imply a partnership the user did not request.

The bundled full-page images are visual references, not standalone transparent logo assets. Render/extract original vector artwork from the PDF when suitable. Verify that page backgrounds, labels, and guide marks were not included. If exact reuse is impossible, ask for an original SVG/PNG logo when essential.

## Application examples and dimensions

| PDF page | Reference use |
| --- | --- |
| 1-2 | Navy/purple gradients, generous negative space, enlarged outline motif. |
| 15-18 | Social layouts, pale/dark contrast, subtle pattern placement. |
| 19 | Light stationery with purple identity elements. |
| 20-23 | Tote, mug, bottle, lanyard and badge: realistic materials and brand-colored surfaces. |
| 24-25 | Banners and flags: readable hierarchy at larger scale. |
| 26-28 | Pins/stickers: diverse subjects unified by palette and visual treatment. |
| 29-30 | Booths and spatial applications: rounded forms, purple/white surfaces, larger motifs. |

**Application default:** Follow the example relevant to the requested medium. Do not force glossy 3D onto a flat icon or turn a realistic portrait into a sticker unless asked. Sticker borders are an option for requested stickers, not a mandatory border around every asset.

Preserve requested output dimensions or source aspect ratio by default. The social dimensions on pages 15-18 are examples from the June 2026 guide, not current platform requirements. Consult them when relevant; verify current external specifications if specifically requested.
