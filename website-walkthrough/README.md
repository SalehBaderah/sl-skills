# Website Walkthrough

An agent skill for cinematic, mockup-style website demo videos. Start with an uploaded recording or let the agent open and record a site. The workflow combines readable framing, gentle floating perspective, deliberate camera moves, eased scrolling, cursor handling, and subtle UI sounds, then verifies and delivers an MP4.

## Installation

### 1. Add the skill to your agent

With Node.js and npm installed, use the [Skills CLI](https://skills.sh/docs/cli):

```bash
npx skills add https://github.com/Sl-15-dev/sl-skills/tree/main --skill website-walkthrough --agent codex
```

This installs for Codex in the current project from the `main` branch. Add `--global` for a personal installation across projects, or omit `--agent codex` to choose another supported agent. Add `--yes` to skip confirmation prompts when automating installation. Reload skills or start a new agent session afterward. To upgrade a CLI-managed installation, run `npx skills update`; back up local edits and work first. The CLI installs skill files; Python, FFmpeg, and optional browser dependencies are separate steps below.

**Manual alternative:** download a branch or release containing this folder, or extract the skill ZIP. Keep the entire `website-walkthrough` folder together, including scripts, examples, and references.

For Codex, copy it into your personal skills directory. Run these commands from the directory containing `website-walkthrough/` (the repository root for a GitHub download):

```bash
mkdir -p ~/.codex/skills
cp -R website-walkthrough ~/.codex/skills/
```

If upgrading manually, back up your existing skill folder and local work before replacing it. Reload skills or start a new agent session. For other agents, use their documented skill directory or load `SKILL.md` through their supported mechanism. Installing a skill does not add capabilities the host agent lacks.

### 2. Install rendering dependencies

Requirements: **Python 3.10+**, **FFmpeg with libx264 and FFV1**, and **FFprobe** on PATH. Install FFmpeg using your OS package manager (for example, `brew install ffmpeg` on macOS or `sudo apt-get install ffmpeg` on Debian/Ubuntu), or an official linked build from [ffmpeg.org](https://ffmpeg.org/download.html).

From the installed skill directory (use the location reported by the CLI, or your manual installation path):

```bash
python3 -m venv work/venv
work/venv/bin/python -m pip install -r requirements.txt
ffmpeg -version
ffprobe -version
```

On Windows, use your installed skill directory, `py -m venv work/venv`, and `work\venv\Scripts\python.exe` in place of `work/venv/bin/python` throughout the commands below. The Python scripts are portable; shell examples use POSIX syntax.

### 3. Enable live-site capture (optional)

For the included Playwright recorder:

```bash
work/venv/bin/python -m pip install -r requirements-capture.txt
work/venv/bin/python -m playwright install chromium ffmpeg
```

On a supported Linux host missing browser libraries, `work/venv/bin/python -m playwright install-deps chromium` may also be needed with administrator permission. Keep network proxy, CA trust, and TLS verification intact. Browser downloads and the target site must be allowed by the host environment. See [live capture](references/live-capture.md) for browser selection and troubleshooting.

A host-provided recorder may be used instead when it supports video export. Prefer a recorder that genuinely supports high-density capture and native 60 fps for premium motion. The bundled Playwright recorder is a portable fallback, usually **25 fps**, with **no website/system audio**. It does not become a 60 fps recorder by changing the export rate.

## Use with an agent

Invoke the skill:

> Use $website-walkthrough to make a cinematic product demo.

The agent first asks whether to edit an uploaded video or open and record a site. If your request explicitly chooses a mode, it proceeds without repeating the question.

**Upload mode:**

> Use $website-walkthrough to edit the attached recording. Make it feel like a premium product mockup: readable UI, gentle floating perspective, smooth focus moves, subtle framing, and click sounds. Settle the stage during interactions. Preserve the original speech and stereo audio; add no music.

**Record mode:**

> Use $website-walkthrough. Open and record https://example.com. Create a brisk 30-second cinematic walkthrough: introduce the site, open one featured project, show its strongest result, and finish on the real contact invitation. Keep headings and cards complete, let navigation settle before zooming, and add subtle interaction sounds. Deliver an MP4.

You can specify the feature route, duration, desktop/mobile layout, target aspect ratio, whether to frame the website, motion or a static stage, and audio preference. The agent inspects the source/site and chooses practical defaults for anything unspecified. Examples use placeholder sites and illustrative timestamps; they are not reusable routes for arbitrary websites.

## What the cinematic workflow does

- Tests capture quality before a full live tour; uses real source detail and the available recorder's native frame rate.
- Makes the product prominent with a slim rounded frame, shadow, and subdued backdrop, or edge-to-edge output.
- Adds gentle floating translation and perspective to framed plans, with neutral holds during interactions and page changes; respects requests for no motion.
- Can crop inspected recording controls and fit the remaining viewport to a chosen canvas without stretching it.
- Plans one featured project/workflow, focused supporting beats, and a real contact invitation or next step for the ending.
- Varies reading holds to match the requested pace. Short showcases start around 25–35 seconds; detailed tours can run longer.
- Frames complete sections and waits for navigation to settle before zooming.
- Keeps one cursor and supports click, open, close, touch, toggle, type, and success sounds.
- Preserves stereo source audio with effects and can target identified 50/60 Hz hum without blanket muting.
- Uses a lossless working intermediate and one final H.264 delivery encode after capture.
- Reviews readability, motion, framing, sound, decoding, and file access before delivery.

The supplied renderer supports camera movement and perspective transforms of a **2D video plane**. It does not generate a physical 3D device model, reflections, or depth of field; recover lost detail; remove baked-in cursors automatically; discover click events in an upload; add narration/captions; or edit time. Those tasks need appropriate source preparation or other tools. Read the [cinematic quality standard](references/cinematic-quality.md) for direction and quality gates.

## Run the tools manually

From the skill directory after installation:

1. Save your source as `work/input.mp4` and create `work/plan.json` using the [edit-plan schema](references/edit-plan.md). Adapt [the camera example](examples/plan.json) or [the motion example](examples/motion-plan.json) to the actual clip before running it. The motion example needs at least 12 seconds of footage; its crop, events, and holds are illustrative.
2. Inspect previews at timestamps that exist in your clip:

   ```bash
   work/venv/bin/python scripts/render_walkthrough.py work/input.mp4 --plan work/plan.json --output work/previews --preview-times 0 2 5
   ```

3. Export:

   ```bash
   work/venv/bin/python scripts/render_walkthrough.py work/input.mp4 --plan work/plan.json --output output/walkthrough.mp4
   ```

For live capture, first inspect the site and create `work/capture.json`; `examples/capture.json` demonstrates a read-only route:

```bash
work/venv/bin/python scripts/record_walkthrough.py --script work/capture.json --output-dir work/capture
work/venv/bin/python scripts/render_walkthrough.py work/capture/source.mkv --plan work/capture/plan.json --output output/walkthrough.mp4
```

Before that final render, review the captured video and edit its starter `plan.json` into the intended camera sequence. New capture plans enable gentle stage motion and start with a fixed wide camera so clicks do not drag the focus toward navigation. Keep the camera wide and the stage neutral during navigation; focus only after the destination has settled. Capture pauses provide editing headroom; shorten idle time and match the camera/events to the prepared timeline when making a brisk cut. Each capture attempt needs a new output directory. FFV1 intermediates are large; keep adequate disk space. Original uploads and previously captured MP4 files remain supported.

Set `frame: false` for edge-to-edge output, omit/disable `motion` for a static stage, disable `sound_effects` for source audio without added cues, or set `audio: "mute"` for complete silence. Use `audio_cleanup` only after identifying hum. New plans use CRF 14; older plans retain the renderer's CRF 16 default when omitted.

`crop` selects normalized bounds from the full source; `canvas` sets even output dimensions and fits the viewport without distortion. All camera, event, and cursor coordinates still use the full original source frame. The default canvas and rate follow the source; changing canvas adds no detail. `--fps` can deliberately normalize a known nominal-60 source with a fractional intermediate tag, but converting a 25 fps recording does not make it native 60 fps. Verify the actual export rate. Trimming or retiming requires preparation in another editing tool and a plan matched to that prepared timeline.

The scripts write local files. Your agent's attachment or an authorized file host is required to share a video; a workspace path is not a public download link. Keep session state, private footage, capture plans, and credentials out of shared packages and commits.

## Development

With rendering dependencies installed:

```bash
work/venv/bin/python -m unittest discover -s tests -v
```

The browser integration test is optional. Install capture dependencies and browsers, then run:

```bash
RUN_BROWSER_TESTS=1 work/venv/bin/python -m unittest discover -s tests -v
```

For a compatible system Chromium, set `TEST_CHROMIUM_EXECUTABLE` to its executable path. These tests exercise local fixtures and encoding behavior; visual direction and listening still need review of the actual output.

## License

MIT; see [LICENSE](LICENSE). Browser, FFmpeg, Python dependency, and hosting-service terms apply separately.
