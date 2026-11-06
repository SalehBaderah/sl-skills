# Skills

Reusable agent skills for creative and development workflows.

| Skill | What it does | Invoke in Codex |
| --- | --- | --- |
| [Website Walkthrough](website-walkthrough/README.md) | Create cinematic website demo videos from uploaded recordings or live browser capture. | `$website-walkthrough` |

## Install

With Node.js and npm installed, run this command from your project directory:

```bash
npx skills add https://github.com/Sl-15-dev/sl-skills/tree/main --skill website-walkthrough --agent codex
```

This installs Website Walkthrough for Codex in the current project. Add `--global` for a personal installation across projects, or omit `--agent codex` to choose another supported agent. Add `--yes` for a noninteractive installation. Reload skills or start a new agent session afterward.

The CLI installs skill instructions and bundled assets. See the [setup and usage guide](website-walkthrough/README.md) for Python, FFmpeg, optional browser capture, and other dependencies.

## Start using the skill

Attach a recording or specify a site to record, then ask:

```text
Use $website-walkthrough to record https://example.com and create a
30-second walkthrough with readable framing, gentle motion, and click sounds.
```

See the [Website Walkthrough guide](website-walkthrough/README.md) for rendering, optional live capture, motion controls, and verification.

## AIP Restyle has moved

AIP Restyle is maintained in its own repository: [Sl-15-dev/aip-restyle](https://github.com/Sl-15-dev/aip-restyle). Follow its README for installation, example prompts, palette downloads, and logo helpers. Its skill identifier remains `$restyle-ai-pioneers`.
