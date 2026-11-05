# Changelog

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
