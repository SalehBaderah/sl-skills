# SL Skills

Reusable agent skills by [Saleh Baderah](https://github.com/SalehBaderah).

## Skills

| Skill | Purpose | Documentation |
| --- | --- | --- |
| [`website-walkthrough`](website-walkthrough/) | Turn a screen recording or live website into a polished demo video. | [README](website-walkthrough/README.md) |
| [`create-your-own-course`](create-your-own-course/) | Design, build, teach, and improve a personalized course on any subject. | [README](create-your-own-course/README.md) |

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

## Create Your Own Course

Design, build, teach, and improve a personalized course on any subject. The skill helps define practical outcomes, assess the learner's starting point, plan a roadmap, create modules incrementally, and track demonstrated progress.

### Install

With Node.js and npm installed, run from your project directory:

```bash
npx skills add https://github.com/SalehBaderah/sl-skills/tree/main --skill create-your-own-course --agent codex
```

Add `--global` to install across projects. Reload skills or start a new agent session after installation.

### Try it

```text
Use $create-your-own-course to help me learn [subject].
Start by understanding my goals and planning the roadmap with me.
Do not create course files until we agree on the plan.
```

[Setup & usage](create-your-own-course/README.md) · [Examples](create-your-own-course/examples) · [Templates](create-your-own-course/templates)

