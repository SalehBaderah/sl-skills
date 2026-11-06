# Skills

Reusable agent skills for creative and development workflows.

| Skill | What it does | Invoke in Codex |
| --- | --- | --- |
| [AIP Restyle](AIP-restyle/README.md) | Adapt images and designs to the AI Pioneers identity with its navy-purple palette and bundled emblem. | `$restyle-ai-pioneers` |
| [Website Walkthrough](website-walkthrough/README.md) | Create cinematic website demo videos from uploaded recordings or live browser capture. | `$website-walkthrough` |

## Install

With Node.js and npm installed, run the command for the skill you want from your project directory.

**AIP Restyle**

```bash
npx skills add https://github.com/Sl-15-dev/sl-skills/tree/main --skill restyle-ai-pioneers --agent codex
```

**Website Walkthrough**

```bash
npx skills add https://github.com/Sl-15-dev/sl-skills/tree/main --skill website-walkthrough --agent codex
```

These commands install for Codex in the current project. Add `--global` for a personal installation across projects, or omit `--agent codex` to choose another supported agent. Add `--yes` for a noninteractive installation. Reload skills or start a new agent session afterward.

The CLI installs skill instructions and bundled assets. Editing tools, Python helpers, FFmpeg, and browser dependencies depend on the workflow; follow the relevant guide below.

## Start using a skill

Attach your image or design, then ask:

```text
Use $restyle-ai-pioneers on this image. Apply the AIP palette, preserve the
subject and original text, and integrate the emblem into a suitable surface.
```

For a website video, attach a recording or specify a site to record:

```text
Use $website-walkthrough to record https://example.com and create a
30-second walkthrough with readable framing, gentle motion, and click sounds.
```

See the [AIP Restyle guide](AIP-restyle/README.md) for example prompts, logo options, palette downloads, and helper setup. See the [Website Walkthrough guide](website-walkthrough/README.md) for rendering, optional live capture, motion controls, and verification.
