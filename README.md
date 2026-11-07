# SL Skills

Reusable agent skills by [Saleh Baderah](https://github.com/SalehBaderah).

## Website Walkthrough

Turn a screen recording or live website into a polished demo video. Add smooth camera moves, subtle perspective, a rounded frame, and UI sounds, then export an MP4.

Useful for portfolios, landing pages, dashboards, and product demos.

### Install

With Node.js and npm installed, run from your project directory:

```bash
npx skills add https://github.com/SalehBaderah/sl-skills/tree/main --skill website-walkthrough --agent codex
```

Add `--global` to install across projects. Reload skills or start a new agent session after installation.

Rendering requires **Python 3.10+ and FFmpeg**; live capture also uses Playwright. Follow the [setup guide](website-walkthrough/README.md#installation) to install these dependencies.

### Try it

**Record a website**

```text
Use $website-walkthrough to record https://example.com.
Create a 30-second demo with gentle camera moves and subtle click sounds.
```

**Edit a recording**

Attach your video, then ask:

```text
Use $website-walkthrough to edit this recording.
Keep the UI readable, add a rounded frame, and preserve the original audio.
```

[Setup & usage](website-walkthrough/README.md) · [Example plans](website-walkthrough/examples) · [Changelog](website-walkthrough/CHANGELOG.md) · [MIT license](website-walkthrough/LICENSE)

---

