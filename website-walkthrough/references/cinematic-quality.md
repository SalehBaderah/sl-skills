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
- Compose a complete subject: its heading, the full featured card or panel, and enough context to understand it. Check every edge for a clipped neighboring heading, partial card, stray tooltip, or unrelated control. Reposition the page or pull back when needed; do not cover a composition problem with extra decoration.

## Choreograph a short story

Choose one main story and only enough supporting beats to establish it. For a short showcase, start around 25–35 seconds. A practical 30-second structure is:

| Beat | Starting point |
| --- | --- |
| Establish the product | 2–3 seconds; identity and core promise |
| Explore one featured project or workflow | 8–10 seconds; enter it, show a meaningful action/detail, and hold the visible outcome |
| Demonstrate supporting features | 8–10 seconds across 1–2 focused beats |
| Show a distinctive interaction | 3–4 seconds, if it adds value |
| Finish | 2–3 seconds; actual identity and a clear contact invitation or next step |

Adapt the structure to the content and the user's pacing feedback. Allow 45–60 seconds for a detailed tour, narration, or a requested explanation. Avoid padding sparse pages or holding every section for the same duration. For uploads, preserve duration unless editing it is within the user's request.

For a portfolio, inspect a project's detail page before recording and choose a useful result, illustration, or demonstration to show. For an app, select a short workflow with a clear outcome. Keep the story inside the authorized route; an external demo or consequential action may need separate authorization. Never invent results or imply a control works when its outcome was not observed. With existing footage, choose the best available material and state any coverage limit.

Plan the closing composition in advance. Prefer the site's own name/identity and visible contact section, booking link, or next-step control. If those elements are in separate areas, use a short identity shot followed by the real CTA. Hold the final settled view for 2–3 seconds. Do not end halfway through a scroll or click, open a mail client, send a message, or add a branded end card without authorization.

Move the pointer purposefully, settle, interact, then hold the result. Start around 0.4–0.8 seconds for pointer travel, 0.6–1.2 seconds for camera transitions, and 0.8–1.5 seconds for a short eased scroll. Give simple labels roughly 1–2 seconds and the most important results 2–3 seconds; allow longer when actual reading or explanation needs it. Real loading and animation completion determine when the result can be shown. Capture longer holds for editing headroom, then shorten idle time in the final cut. Avoid pointer detours, long pauses between minor actions, uniform holds, and constant zoom-in/zoom-out cycles. Preserve speech and meaningful loading behavior when retiming.

Keep the camera wide and still during navigation, anchor scrolling, and layout changes. After the destination has visibly settled, ease into its important content. Never combine an unsettled page move with a competing camera zoom. A lead-in zoom is appropriate only for an interaction whose surrounding UI stays stable. Check this distinction in the actual encoded transition, not just the keyframe list.

Build camera keys separately from click events. Use 1.10–1.35× focus moves initially; check text at the maximum crop before increasing magnification. Use equal-position keys for holds and a wider establishing composition before large content changes. If two moves overlap, combine them into one deliberate focus instead of averaging unrelated targets.

## Preserve detail through export

Use a lossless working file when normalizing or trimming. Render final composition, cursor, and effects into one H.264 delivery generation: CRF 14, slow preset, yuv420p, AAC when audio exists, and MP4 fast-start. CRF 14 is a starting point, not a guarantee: inspect gradients, thin lines, and moving text. CRF 12–16 may be appropriate; lower values cost storage and do not repair a poor source. Use original audio where present and keep UI sounds restrained. Add music only when requested.

For the bundled capture helper, retain raw WebM and use its FFV1 source.mkv for editing. This removes an extra lossy preparation encode; the browser's initial video is still lossy and typically 25 fps. The FFV1 file can be much larger than the final MP4; check disk space. Select a different supported capture method for genuinely higher-density/60 fps requirements.

## Quality gate

Review the encoded file at the size the audience will use. Watch the transitions, not just a contact sheet.

- Can the viewer read the key heading, labels, and result without pausing or enlarging the player?
- Is the product prominent, with consistent margins and no important controls cut off?
- Are the featured heading/card/panel complete, with no distracting fragments of the next section at the edges?
- Are scrolls and pans smooth, and does every important view have time to settle?
- Does navigation finish before the camera focuses, and are idle holds short enough for the selected pace?
- Does each camera move serve the content rather than merely follow the cursor?
- Is there one memorable project detail or real outcome, with more attention than minor supporting sections?
- Are there no duplicate pointers, repair artifacts, clipping, stray synchronization slates, or unintended blank frames?
- Are sounds aligned and quiet, speech intelligible, and silence requests respected?
- Does the final settled shot show a clear identity/contact invitation or legitimate next step, without activating a consequential action?
- Does the file fully decode with the expected rate, duration, and audio?
- Can the user actually access the delivered file?

Correct failed gates and recheck affected shots. Be precise about a source or tool limit that cannot be corrected. Do not equate a successful encode with a cinematic result.
