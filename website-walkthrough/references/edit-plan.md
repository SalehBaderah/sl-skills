# Edit plan schema

The JSON plan contains recording-specific editing data. All camera, event, and cursor coordinates are normalized to the full, correctly oriented original source frame, even when `crop` selects a smaller viewport or `canvas` changes output dimensions. They never refer to the cropped browser area or the framed output.

| Field | Meaning |
| --- | --- |
| frame | true (default) for rounded screen and subdued backdrop; false for edge-to-edge |
| crop | Optional [left, top, right, bottom] bounds, normalized to the full source; default [0, 0, 1, 1] |
| canvas | Optional [width, height] output dimensions, each an even integer from 2 to 7680; default source dimensions rounded down to even values |
| motion | Optional framed-stage translation and video-plane perspective; absent or disabled retains the static stage; see below |
| audio | "preserve" (default) or "mute"; mute silences original audio and added effects; no music is generated |
| audio_cleanup | Optional targeted hum filtering: {enabled: true, hum_hz: 50 or 60, harmonics: 1–4}; harmonics defaults to 3; enable only for identified hum |
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

## Source viewport and output canvas

`crop` bounds must satisfy `0 <= left < right <= 1` and `0 <= top < bottom <= 1`. Inspect the original before excluding recording controls or borders; never hide meaningful product errors, content, or outcomes. The selected viewport fits inside `canvas` without distortion. Output dimensions and stage space do not add captured detail. Default settings retain the full source and its dimensions. For example, a crop that removes a bottom recording bar does not change the full-source coordinate of an existing click or camera center.

The renderer keeps the source rate unless `--fps` deliberately overrides it. Normalizing a known nominal-60 source with a fractional intermediate tag is valid; verify the actual export rate and motion. Duplicating a 25 fps recording does not make it native 60 fps. Crop, canvas, and motion do not trim or retime footage. Prepare timeline edits separately, then update all plan times. The capture helper supplies an FFV1 `source.mkv`; ordinary uploaded MP4s remain supported. The renderer does not implement a high-density recorder, physical 3D device models, reflections, depth of field, or narration.

## Floating perspective

`motion` requires `frame: true`. Enable gentle motion for new framed plans unless the user prefers a static presentation. Omitting `motion`, or setting `enabled: false`, preserves the existing static stage.

```json
{
  "frame": true,
  "motion": {
    "enabled": true,
    "keyframes": [
      [0, 0, 0.003, 0.3, -0.7, -0.1],
      [3, 0.003, -0.003, -0.2, 0.6, 0.1],
      [8, -0.003, 0.002, 0.2, -0.5, -0.1]
    ],
    "settle": [[3.5, 5.2]]
  }
}
```

Each key is `[time, dx, dy, pitch, yaw, roll]`:

| Value | Units and bounds |
| --- | --- |
| time | Seconds within the source; strictly increasing |
| dx, dy | Translation as fractions of output canvas width/height; each −0.02 to 0.02 |
| pitch, yaw | Degrees; each −3 to 3 |
| roll | Degrees; −1 to 1 |

Enabled motion without keyframes generates a gentle float proportional to the clip duration. This is a perspective transform of the 2D video plane, not a physical 3D device model. The renderer scales the stage down only when needed to keep its projected corners inside the canvas, including portrait layouts. Keep poses small enough to preserve readable text, complete subjects, and breathing room for the surface and shadow. Bounds are limits, not recommended strengths; inspect the most extreme poses.

`settle` contains `[start, end]` intervals in seconds. During each interval the stage returns to its neutral pose, with smooth fades into and out of the hold. When `settle` is omitted, event-adjacent windows run from 0.45 seconds before each event to 0.75 seconds after it, clipped to the source duration. An explicit empty list, `"settle": []`, requests continuous motion. Extend neutral holds for real navigation, scrolling, layout changes, and close reading; the event default cannot infer when a page has settled. Stage settling does not stop source motion or camera zooms: plan those separately.

Use [the 12-second motion example](../examples/motion-plan.json) for a complete schematic plan with two interaction holds. Its crop, events, and camera keys need inspection and replacement for each source. [The camera example](../examples/plan.json) retains the older static-stage workflow.

## Audio

Supported sounds are `click`, `open`, `close`, `touch`, `toggle`, `type`, and `success`. An event may use `sound: "none"`; independent sound cues need a supported effect. All effects are synthesized locally. Enabling effects works even on silent footage. Source audio is mixed with effects and a peak limiter; stereo source channels are preserved. Speech is retained but the mix may change peaks. Lower effects volume under narration. `audio: "mute"` removes every audio stream; disabling `sound_effects` removes added cues while retaining the source, with optional cleanup if enabled. A cue at the clip's exact end is omitted and effects extending past the end are truncated. Do not add an independent cue at the same time as an event cue unless both are intentional.

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

If inspection identifies persistent mains hum, optionally add `"audio_cleanup": {"enabled": true, "hum_hz": 60, "harmonics": 3}`. Enabled cleanup requires an explicit 50 or 60 Hz frequency matching the observed hum; `harmonics` controls how many multiples are targeted, from 1 to 4, defaulting to 3. Omit cleanup for an unaffected source, or set `"audio_cleanup": {"enabled": false}` without a frequency. Compare the result against the original and preserve speech, music, and intended low tones. This is targeted filtering, not general noise removal or permission to blanket-mute the source. Full `audio: "mute"` takes precedence.

## Camera and pointer timing

Automatic mode eases into an event beginning 0.55 seconds before its timestamp, holds focus until 0.6 seconds afterward, then releases over 0.8 seconds. Nearby events blend their focus points. Use explicit camera keys when this blend would center on irrelevant content, or when a response appears far from its triggering control.

For explicit keyframes, each transition uses quintic easing. Include intermediate keys for a sustained scrolling move; two distant keys with easing can cause noticeable speed changes. Add equal-position keys at both ends of a pause. Camera keys control zoom/focus; event timestamps still control click highlights. A cursor keyframe is a pointer hotspot, not the center of its bitmap.

Do not substitute example timestamps for analysis. For a source with no reliable clicks, a deliberate camera-keyframe edit is valid; omit invented events and label the result accordingly.
