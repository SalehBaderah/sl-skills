# Course-building entry point

This repository contains the reusable Create Your Own Course skill.

When the user asks to design, create, teach, review, or continue a course:
- Read `SKILL.md` and follow its workflow within your available capabilities.
- Use the conversation and existing course records before asking questions.
- Plan with the user before creating course materials, unless already authorized.
- After agreement, create courses under `courses/<course-slug>/` unless the user chooses another location.
- Preserve this repository's reusable instructions, templates, and root README.
- Use only the optional templates relevant to the current task.

For maintenance of this repository, follow the requested maintenance task. Do not start a learner intake questionnaire. Keep `PROMPT.md` synchronized with the instructions in `SKILL.md` after its YAML frontmatter.

Agents that do not automatically read `AGENTS.md` can follow an explicit request to read `SKILL.md`, or use the contents of `PROMPT.md` directly.
