# Edit plan schema

The JSON plan contains only recording-specific editing data. Coordinates are normalized to the full, correctly oriented source frame, not the visible browser content area or framed output.

| Field | Meaning |
| --- | --- |
| frame | true (default) for rounded screen and subdued backdrop; false for edge-to-edge |
| audio | "preserve" (default) or "mute"; mute silences original audio and added effects; no music is generated |
| crf | Integer 0–28; new cinematic plans use 14; renderer default remains 16 for older plans; lower values increase file size |
| click_highlights | true (default) for a subtle visual pulse at each event |
| events | Objects with time in seconds, x, y, optional zoom (default 1.5), sound (default "click"), and highlight (default true) |
| sound_effects | Object with enabled (boolean, default false for older plans) and volume (0–1, default 0.35); new skill plans should explicitly enable it unless declined |
| sounds | Optional list of {time, effect, volume}; volume is a 0–1 multiplier of sound_effects.volume, default 1; no visual highlight or camera movement |
| camera | [time, zoom, center_x, center_y] keyframes; use for cinematic edits; overrides automatic event zooms |
| source_cursor_visible | Defaults true; must explicitly be false before drawing a replacement cursor |
| cursor | Optional [time, hotspot_x, hotspot_y] keyframes; only for a verified cursor-free source |

Times must increase strictly inside each keyframe list. Coordinates must be 0–1, zoom 1–3, and times within the actual clip. The camera clamps crops to source bounds, so edge controls will remain near an edge even when zoomed. This avoids inventing pixels outside the recorded viewport.

Use [cinematic quality](cinematic-quality.md) to direct the camera. Choose focus centers for complete headings, cards, and visible results, independently of click locations. Keep a wide, steady camera through navigation and scrolls, then focus after the destination settles. Start around 1.10–1.35×, vary readable holds with the selected pace, and inspect the largest crop at full resolution. `examples/plan.json` illustrates two navigation events in a clip at least 18 seconds long: the camera stays wide until illustrative settled times of 4.2 and 10.2 seconds, then focuses. Replace all events, settled times, and keys with observations from your own source. Generated capture plans start with a fixed wide camera, so they need this editorial review before final rendering.

The renderer preserves source dimensions and frame rate. It does not implement a high-density capture mode, aspect-ratio conversion, time editing, 3D tilt, or native 60 fps generation. `frame` supplies the built-in rounded surface/backdrop only. Prepare other compositions in an appropriate tool, then match plan coordinates and times to that prepared source. The capture helper supplies an FFV1 `source.mkv`; ordinary uploaded MP4s remain supported.

Supported sounds are `click`, `open`, `close`, `touch`, `toggle`, `type`, and `success`. An event may use `sound: "none"`; independent sound cues need a supported effect. All effects are synthesized locally. Enabling effects works even on silent footage. Source audio is mixed with the effects and a peak limiter; speech is retained but the mix may change peaks. Lower effects volume under narration. `audio: "mute"` removes every audio stream; `sound_effects: {"enabled": false}` preserves source audio alone. A cue at the clip's exact end is omitted and effects extending past the end are truncated. Do not add an independent cue at the same time as an event cue unless both are intentional.

```json
{
  "audio": "preserve",
  "sound_effects": {"enabled": true, "volume": 0.35},
  "events": [
    {"time": 1.2, "x": 0.6, "y": 0.3, "sound": "click"},
    {"time": 3.0, "x": 0.8, "y": 0.2, "sound": "none"}
  ],
  "sounds": [{"time": 3.15, "effect": "open", "volume": 0.7}]
}
```

Automatic mode eases into an event beginning 0.55 seconds before its timestamp, holds focus until 0.6 seconds afterward, then releases over 0.8 seconds. Nearby events blend their focus points. Use explicit camera keys when this blend would center on irrelevant content, or when a response appears far from its triggering control.

For explicit keyframes, each transition uses quintic easing. Include intermediate keys for a sustained scrolling move; two distant keys with easing can cause noticeable speed changes. Add equal-position keys at both ends of a pause. Camera keys control zoom/focus; event timestamps still control click highlights. A cursor keyframe is a pointer hotspot, not the center of its bitmap.

Do not substitute example timestamps for analysis. For a source with no reliable clicks, a deliberate camera-keyframe edit is valid; omit invented events and label the result accordingly.
