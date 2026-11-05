# Cinematic quality standard

Aim for a premium product presentation: sharp UI, readable type, confident pacing, and a cohesive mockup stage. Technical resolution is only one part of quality. Do not accept tiny text or restless framing just because an export has large dimensions.

## Capture first

| Area | Target | Check or fallback |
| --- | --- | --- |
| Detail | High pixel density at a readable logical viewport; capture above delivery size when useful for crops | Inspect actual glyph edges and fine UI lines. Device-scale settings must produce genuine captured detail, not an enlarged low-resolution screencast. |
| Motion | Native 60 fps for scrolling and animated interfaces when supported | Inspect motion in the encoded pilot. Keep the actual 25/30 fps when that is the recorder's limit; duplicating frames is not native 60 fps. |
| Layout | A viewport that makes the site's content prominent | Desktop sites often work at 1280–1440 CSS pixels wide; test their responsive breakpoints. Increasing viewport width can shrink content relative to the frame. |
| Delivery | Prefer at least 1920×1080 for a landscape demo when source detail and composition support it; higher resolution when useful | Retain a better-fitting source aspect ratio unless another is requested. The bundled renderer keeps source dimensions; prepare the desired canvas with capture or a separate compositor. Do not pad/upscale merely to claim HD/4K. |
| Compression | Sharp master, lossless intermediates, one final delivery encode | A lossless intermediate preserves the decoded capture; it cannot undo compression in the original. Keep raw and master files. |

Record a 5–8 second pilot with a readable heading/body paragraph, pointer motion, a short scroll, and a representative click. Inspect it at intended playback size and at 100% pixels. Verify fonts and images finished loading, UI contrast is preserved, and motion is smooth. Reduce capture load, adjust viewport/density, or choose a better supported recorder before recording a full tour if the pilot fails. Preserve the host's proxy, CA trust, and browser policy.

For an uploaded source, inspect equivalent sections. Improve composition and pacing within its real limits. Request a better source only if needed; explain what setting would help.

## Compose the mockup

- Make the website surface roughly 85–95% of the stage width as a starting point, with slim margins, restrained corner radius, a soft shadow, and a quiet backdrop. Also account for whitespace **inside** the page. A large outer frame does not make a narrow content column readable.
- Respect the original palette and contrast. Avoid crushing dark UI, excessive glow, sharpening halos, fake reflections over text, or decorative motion that competes with the product.
- Keep the UI square to the viewer while it must be read or operated. If an advanced compositor is available, reserve gentle perspective for brief establishing/ending shots. The bundled renderer has no 3D or custom-background controls; do not promise those from its JSON plan.
- Prioritize the target **and the resulting content**. Navigation clicks do not need a camera move. Use focus on a project image, feature panel, menu result, or changed state when that advances the story.

## Choreograph a short story

Choose 3–5 feature beats. A useful 45–60 second structure is:

| Beat | Starting point |
| --- | --- |
| Establish the product | 3–5 seconds; stable, readable overview |
| Show the main value | 10–15 seconds; meaningful action and visible result |
| Demonstrate supporting features | 15–25 seconds across 2–3 beats |
| Show a distinctive interaction | 5–8 seconds, if relevant |
| Finish | 3–5 seconds on a complete, settled view |

Adapt the structure to the actual product and requested length; do not pad sparse pages. For uploads, preserve duration unless editing it is within the user's request.

Move the pointer purposefully, settle, interact, then hold the result. Allow roughly 0.5–1 second for pointer travel, 0.8–1.5 seconds for camera transitions, 1.2–2.5 seconds for a short eased scroll, and 3–5 seconds to read important content. Real loading and animation completion determine the actual timing. Avoid pointer detours, rapid jumps through anchor links, and constant zoom-in/zoom-out cycles.

Build camera keys separately from click events. Use 1.10–1.35× focus moves initially; check text at the maximum crop before increasing magnification. Use equal-position keys for holds and a wider establishing composition before large content changes. If two moves overlap, combine them into one deliberate focus instead of averaging unrelated targets.

## Preserve detail through export

Use a lossless working file when normalizing or trimming. Render final composition, cursor, and effects into one H.264 delivery generation: CRF 14, slow preset, yuv420p, AAC when audio exists, and MP4 fast-start. CRF 14 is a starting point, not a guarantee: inspect gradients, thin lines, and moving text. CRF 12–16 may be appropriate; lower values cost storage and do not repair a poor source. Use original audio where present and keep UI sounds restrained. Add music only when requested.

For the bundled capture helper, retain raw WebM and use its FFV1 source.mkv for editing. This removes an extra lossy preparation encode; the browser's initial video is still lossy and typically 25 fps. The FFV1 file can be much larger than the final MP4; check disk space. Select a different supported capture method for genuinely higher-density/60 fps requirements.

## Quality gate

Review the encoded file at the size the audience will use. Watch the transitions, not just a contact sheet.

- Can the viewer read the key heading, labels, and result without pausing or enlarging the player?
- Is the product prominent, with consistent margins and no important controls cut off?
- Are scrolls and pans smooth, and does every important view have time to settle?
- Does each camera move serve the content rather than merely follow the cursor?
- Are there no duplicate pointers, repair artifacts, clipping, stray synchronization slates, or unintended blank frames?
- Are sounds aligned and quiet, speech intelligible, and silence requests respected?
- Does the ending feel complete, and does the file fully decode with the expected rate, duration, and audio?
- Can the user actually access the delivered file?

Correct failed gates and recheck affected shots. Be precise about a source or tool limit that cannot be corrected. Do not equate a successful encode with a cinematic result.
