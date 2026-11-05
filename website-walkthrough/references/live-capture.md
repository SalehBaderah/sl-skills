# Open a site and record it

Use this path only after the user's input-mode choice. The agent can explore a URL, inspect its accessible controls, plan a route, execute it in a browser, record real behavior, and edit that recording. A URL by itself is not a prerecorded video. Browser access, video capture, site reachability, and any authorized login are required. Do not substitute a slideshow or fabricated UI when capture is unavailable.

## Choose a recorder

Prefer a host browser tool if it supports **actual video recording/export** plus interaction metadata. A browsing tool that supplies only screenshots does not establish that it can record video. Otherwise use the included Playwright helper. Follow the host's browser rules and networking policy. Do not bypass a mandated browser tool with a different browser. If neither route is supported, ask for uploaded footage.

The helper records a single Chromium viewport. It does not capture browser chrome, microphone/system/site audio, new tabs, native dialogs, or full desktop apps. Iframe and keyboard actions can appear in the video but their pointer metadata may be incomplete. Inspect those manually. It records at the browser encoder's actual rate (commonly 25 fps), not an assumed 60 fps. It does not promise lossless capture. Larger viewports cost more time and storage; start at 1440×900, or use an even-sized mobile viewport when requested. A mobile viewport and tap support alone do not emulate an entire mobile device.

## Install (only for browser capture)

From the skill directory with Python 3.10+ and FFmpeg/FFprobe on PATH:

```bash
python -m venv work/venv
work/venv/bin/python -m pip install -r requirements-capture.txt
work/venv/bin/python -m playwright install chromium ffmpeg
```

On a supported Linux host missing native browser libraries, Playwright's documented `install-deps chromium` command may be needed with host authorization. Respect the host's configured proxy and CA trust. Do not disable TLS verification. The normal Playwright installer may need `cdn.playwright.dev` and `playwright.download.prss.microsoft.com`; diagnose the actual failed destination before requesting a policy change. For an already installed compatible Chromium, pass `--browser-path /path/to/chromium`; Playwright's video encoder still needs installation. Retained dependencies survive as files; browser processes must start for each capture.

## Inspect and write a capture script

Visit the site using the permitted browser tools first. Discover current roles, accessible names, text, or test IDs; do not invent selectors or replay coordinates from another site. Use authorized, reversible demo interactions. Choose a short route that shows the user's requested features. Dismiss cookies/popups only as authorized and keep the chosen consent consistent. Do not modify the website's behavior or suppress meaningful loading/error states to fake performance.

Write `work/capture.json` based on that inspection. `examples/capture.json` is a runnable, read-only example, not a generic route for other websites. For a site with an inspected menu button, a step might be:

```json
{"action": "click", "target": {"role": "button", "name": "Menu"}, "sound": "open", "pause": 1.0}
```

Each target selects exactly one kind: `{role, name}`, `{text}`, `{test_id}`, or `{css}`. Matching is exact for names/text; ambiguous matches fail instead of clicking the first one. Actions:

| Action | Parameters |
| --- | --- |
| click / tap / hover | target; optional sound and pause |
| fill | target and either value (non-sensitive demo data) or value_env (an already authorized runtime variable name); never save credentials in a script |
| press | target and key, e.g. "ArrowDown"; avoid triggering unauthorized submissions |
| wait_for | target; waits until visible |
| scroll | dy (default 500 pixels), optional dx and pause; smooth wheel sequence |
| wait | seconds (default 1, at most 60) |
| goto | url; use only within the authorized route |

`pause` defaults to 0.65 seconds after each action other than wait/wait_for. Top-level `settle` (default 1 second) allows the initial page to settle before recording the tour; `initial_hold` (0.6) and `end_hold` (1.2) add readable pauses. These waits do not replace checking actual loaded state. `site_draws_cursor: true` disables the replacement cursor for sites that already draw one. Pointer-down events default to `sound: "click"`; use `open`, `close`, `touch`, `toggle`, `success`, or `none` only when accurate. Hover/scroll/fill/keyboard actions do not automatically produce sound cues. Add manually verified independent sounds in the edit plan if needed.

Use only provided or already authorized login sessions. The helper accepts `--storage-state work/session.json` for sensitive, authorized Playwright session state, and `--headed` for hosts with a display. Never package, commit, print, or deliver session files, tokens, passwords, or private capture plans. If interactive login, MFA, CAPTCHA, or site policy prevents capture, pause for authorized user assistance or use uploaded footage. No stealth or access-control bypass is part of this skill.

## Record, review, render

```bash
work/venv/bin/python scripts/record_walkthrough.py --script work/capture.json --output-dir work/capture
work/venv/bin/python scripts/render_walkthrough.py work/capture/source.mp4 --plan work/capture/plan.json --output output/walkthrough.mp4
```

Choose a fresh output directory for each attempt. The helper retains raw browser footage under `raw/`, trims a temporary two-color synchronization slate, and writes `source.mp4`, `plan.json`, and `capture-info.json`. It logs observed main-frame pointer events without page text or typed values. Do not deliver raw footage, which can contain initial private UI and the slate. This helper does not collect or save authentication state.

The slate aligns the event clock to the saved video; asynchronous screencasting can still introduce a few frames of latency. Review source frames against the plan and correct any offsets. Recorded pointer events indicate input, not proof that a menu opened or a transaction succeeded. Check the visible outcome before selecting an open/success effect. Revisit zooms to include both targets and resulting content, merge repetitive interactions, and verify custom cursors before drawing an overlay. Inspect any CSS hover effects affected by pointer/touch support.

Run the standard skill verification on the final MP4, including full decode and audio checks. Disclose missing site audio. Do not claim recording was tested on the user's site until it was actually run there.
