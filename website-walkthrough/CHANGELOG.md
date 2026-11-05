# Changelog

## 2.3

- Added reusable floating translation and video-plane perspective, with bounded keyframes and smooth neutral holds around interactions.
- Made gentle motion the default direction for new framed plans while preserving static behavior for existing plans and honoring no-motion requests.
- Added source cropping and an explicit output canvas, retaining full-source coordinates and undistorted viewport fitting.
- Added optional targeted mains-hum cleanup and preserved stereo source audio when mixing effects.
- Added a motion-plan example, motion/readability checks, frame-rate normalization guidance, and installation through the Skills CLI alongside manual installation.

## 2.2

- Added a featured project/workflow with a visible outcome and an intentional identity/contact closing shot.
- Added complete-section framing and settled navigation before camera zooms.
- Made pacing responsive to feedback: brisk showcases start around 25–35 seconds, with varied holds and longer detailed tours when appropriate.
- Clarified capture headroom, safe timeline retiming, and final checks for storytelling and shot boundaries.
- Extended the browser integration check to cover a featured project's detail page, its visible result, and a contact closing shot.

## 2.1

- Added cinematic mockup direction, a capture pilot, readability and motion quality gates, and content-led camera choreography.
- Added eased scrolling and longer default holds; starter capture plans now hold a stable wide view for editorial planning.
- Replaced the lossy H.264 preparation encode with an FFV1 working file, followed by one final delivery encode; new plans use CRF 14.
- Documented native capture limits, high-density/60 fps recorder selection, installation, usage, and file delivery.
- Removed environment-specific validation notes and unimplemented feature suggestions from the public guide.

## 2.0

- Added required input-mode selection, with explicit choices in a user's request respected.
- Added live-site capture instructions and an optional Playwright recorder with pointer metadata and timeline alignment.
- Added locally generated UI sound effects, per-event/independent cues, gain control, source-audio mixing, and full mute.
- Retained older edit plans' audio behavior and original camera/cursor workflow.
- Added capture/edit examples, integration checks, and documentation of limits.
