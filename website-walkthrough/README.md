# Website Walkthrough skill

Create polished MP4 demos from **an uploaded recording** or **a live website the agent opens and records**. Includes a portable camera/cursor renderer, generated UI sounds, an optional Playwright recorder, plan references, examples, and tests. Version 2.0.

## What's new

- First-use question: **upload a video** or **let the agent open and record the site**. An explicit mode choice in the request skips a repeated question.
- Seven adjustable sound effects: click, open, close, touch, toggle, type, and success. Effects are generated locally; no downloaded sound library or music. Disable effects while preserving source audio, or mute everything.
- Browser capture with observed pointer events, smooth pointer moves, a starter edit plan, and synchronization-slate trimming.

## Install

Copy the entire `website-walkthrough` folder (the one containing SKILL.md) into your agent's skills directory. For Codex, the usual personal location is `~/.codex/skills/website-walkthrough/`. Reload skills or start a new session if needed. Installation is local; this archive does not install itself into anyone's account.

Rendering requires Python 3.10+, FFmpeg/FFprobe, and `requirements.txt`. Live capture additionally needs `requirements-capture.txt`, Chromium, and Playwright's video encoder. See [SKILL.md](SKILL.md) and [live capture](references/live-capture.md). Always follow the host's tool, network, and installation rules.

## Use

To get the opening choice:

> Use $website-walkthrough to make a product demo.

To choose directly:

> Use $website-walkthrough. I'll upload a video; edit it with subtle click sounds and smooth camera zooms. Preserve speech, add no music, and give me an MP4.

> Use $website-walkthrough. Open and record https://my-site.example, show the navigation and theme switch, then scroll through the features. Add subtle interaction sounds. Use a desktop viewport.

The agent inspects the actual source/site and adapts its plans. Example coordinates, selectors, and timestamps are illustrative, not reusable across websites. The standalone renderer does not discover clicks or remove baked-in cursors. Browser capture needs an environment that can automate and record a browser, reachable pages, and authorized access. Playwright capture omits site/system audio; use an audio-capable recorder or uploaded footage if that matters.

For edge-to-edge output set `frame` to false. Set `sound_effects.enabled` to false for original audio only, or `audio` to `"mute"` for complete silence. Older plans without sound_effects keep their original behavior. See the [edit-plan schema](references/edit-plan.md).

## Developer checks

From this directory after installing rendering dependencies:

```bash
python -m unittest discover -s tests -v
```

This runs waveform/timing, invalid-plan, FFmpeg mix, source-audio, mute, and backward-compatibility checks. Browser capture is an optional integration test. With capture dependencies and browser installed:

```bash
RUN_BROWSER_TESTS=1 python -m unittest discover -s tests -v
```

For an existing compatible system Chromium, set `TEST_CHROMIUM_EXECUTABLE` to its executable path. Browser tests use an isolated local demo, not a third-party site. They verify visible state changes against recorded events and fully decode the final render. These tests do not establish compatibility with every website or listening review of the generated sounds.

## Other useful additions

These are recommendations, **not implemented features**:

1. **Private-data masking:** blur selected fields, emails, names, and notifications with preview review.
2. **Narration and captions:** optional voice-over, transcript-based captions, and language selection; duck effects under speech.
3. **Output presets:** desktop, mobile, landscape/portrait/square framing, and platform-specific durations. Reframe instead of cropping important controls.
4. **Pacing controls:** remove approved idle sections, speed up repetitive input, and preserve meaningful loading states.
5. **Reusable tour recipes:** configurable routes for feature demos, onboarding, and release notes, with selectors validated each run.
6. **Review before final export:** a lightweight preview with a shot list and timestamped revision requests.

## License

MIT; see LICENSE. Original notice retained. Effects are synthesized by the included code. Hosting services, agent software, browsers, and dependencies have their own terms. No accounts, credentials, user footage, or private URLs are bundled.
