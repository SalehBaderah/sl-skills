# Website Walkthrough

Create cinematic website demos from an uploaded recording or a live site. The skill guides capture, camera movement, framing, sound, and final MP4 verification.

- Smooth camera moves and gentle perspective motion.
- Rounded framing, soft shadows, or edge-to-edge output.
- Cropping and canvas controls that preserve aspect ratio.
- Subtle UI sounds with stereo source audio preserved.
- Preview frames and H.264 MP4 export.

## Installation

### 1. Add the skill

With Node.js and npm installed, run from your project directory:

```bash
npx skills add https://github.com/Sl-15-dev/sl-skills/tree/main --skill website-walkthrough --agent codex
```

Add `--global` for use across projects, `--yes` for noninteractive installation, or omit `--agent codex` to select another supported agent. Reload skills or start a new agent session afterward.

For a manual Codex installation, copy the complete `website-walkthrough` folder into `~/.codex/skills/`. Back up any existing installation before replacing it.

### 2. Install rendering dependencies

Use **Python 3.10+**, **FFmpeg with libx264 and FFV1**, and **FFprobe**. Install FFmpeg with your OS package manager, such as `brew install ffmpeg` on macOS or `sudo apt-get install ffmpeg` on Debian/Ubuntu.

From the installed `website-walkthrough` directory, run:

```bash
python3 -m venv work/venv
work/venv/bin/python -m pip install -r requirements.txt
ffmpeg -version
ffprobe -version
```

For repository development, use `website-walkthrough/` as that directory. All commands below run there too. On Windows, use `py -m venv work/venv` and replace `work/venv/bin/python` with `work\venv\Scripts\python.exe`.

### 3. Enable live capture (optional)

Skip this step when editing an existing recording.

```bash
work/venv/bin/python -m pip install -r requirements-capture.txt
work/venv/bin/python -m playwright install chromium ffmpeg
```

On Linux, missing browser libraries may also require `work/venv/bin/python -m playwright install-deps chromium` with administrator permission. Browser downloads and the target site must be reachable. See the [live capture guide](references/live-capture.md) for browser selection and troubleshooting.

## Use with an agent

**Record a website**

```text
Use $website-walkthrough to record https://example.com.
Create a 30-second demo: introduce the site, show one key feature,
and finish on its contact section. Use gentle motion and subtle click sounds.
```

**Edit an uploaded recording**

```text
Use $website-walkthrough to edit the attached recording.
Add a rounded frame and smooth focus moves. Keep the UI readable,
preserve the original stereo audio, and add no music.
```

You can specify duration, desktop or mobile layout, aspect ratio, framing, motion, and audio preferences. If you do not choose an input mode, the agent asks whether to edit a recording or capture a site.

## Run the tools directly

### Render a recording

Save your video as `work/input.mp4` and create `work/plan.json` using the [edit-plan schema](references/edit-plan.md). The [camera](examples/plan.json) and [motion](examples/motion-plan.json) examples are starting points; adapt their timestamps and coordinates to your footage.

Preview a few frames, choosing times within your clip:

```bash
work/venv/bin/python scripts/render_walkthrough.py work/input.mp4 --plan work/plan.json --output work/previews --preview-times 0 2 5
```

Export the video:

```bash
work/venv/bin/python scripts/render_walkthrough.py work/input.mp4 --plan work/plan.json --output output/walkthrough.mp4
```

### Capture a website

Create `work/capture.json` for your site using the [capture example](examples/capture.json) and [capture guide](references/live-capture.md), then record:

```bash
work/venv/bin/python scripts/record_walkthrough.py --script work/capture.json --output-dir work/capture
```

Review `work/capture/source.mkv` and adjust the generated `plan.json` before rendering:

```bash
work/venv/bin/python scripts/render_walkthrough.py work/capture/source.mkv --plan work/capture/plan.json --output output/walkthrough.mp4
```

Use a new output directory for each capture. Keep enough disk space for the FFV1 working video, which can be much larger than the final MP4. Store private footage, plans, and session files under `work/`; keep them out of commits.

## What to expect

The renderer moves and tilts a **2D video plane**. It does not create a physical 3D device, add narration or captions, remove a baked-in cursor, or trim and retime footage. Prepare those edits separately and match the plan to the edited source.

The bundled Playwright recorder typically captures at **25 fps without website or system audio**. Exporting at 60 fps does not create native 60 fps motion. Uploaded recordings retain their source audio by default; UI sounds can be added separately.

See the [quality guide](references/cinematic-quality.md) for capture, composition, and final review, and the [edit-plan schema](references/edit-plan.md) for motion, cropping, cursor, and audio options.

## Development

Run the test suite after installing rendering dependencies:

```bash
work/venv/bin/python -m unittest discover -s tests -v
```

With capture dependencies and browsers installed, include the browser integration test:

```bash
RUN_BROWSER_TESTS=1 work/venv/bin/python -m unittest discover -s tests -v
```

For a compatible system Chromium, set `TEST_CHROMIUM_EXECUTABLE` to its executable path. Tests cover local capture fixtures, rendering, motion, and audio; review the actual video for visual quality and sound.

## License

[MIT](LICENSE). Third-party tools and services have their own terms.
