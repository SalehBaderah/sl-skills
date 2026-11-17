# Create Your Own Course

A reusable, agent-neutral skill that has your agent **write a complete, personalized course on any subject**: full theory lessons, worked examples, practical exercises, projects, and answer keys.

Use it for English, writing, design, programming, science, professional skills, or another subject. The agent acts as subject expert, course author, tutor, and feedback partner. It plans briefly with you, then writes study-ready modules one at a time, teaching both the theory (the why and how) and the practice (doing it). It adapts as you progress. You can learn from the modules directly; outside links are optional extras.

This folder contains the reusable instructions and optional templates. Your course is created later through collaboration.

## Installation

With Node.js and npm installed, run from your project directory:

```bash
npx skills add https://github.com/SalehBaderah/sl-skills/tree/main --skill create-your-own-course
```

Choose your agent when prompted (or pass `--agent <name>`, e.g. `--agent codex`). Add `--global` to install across projects. Reload skills or start a new agent session after installation.

Then ask your agent, for example:

```text
Use the create-your-own-course skill to help me learn [subject].
Start by understanding my goals and planning the roadmap with me.
Do not create course files until we agree on the plan.
```

In Codex you can also invoke it as `$create-your-own-course`.

## Use without installing

### An agent that can read local files

1. Clone this repository (or copy the `create-your-own-course` folder) and open it in your agent's workspace.
2. Send:

   > Read SKILL.md and use it to help me create my own course on [subject]. Start by understanding my goals and planning the roadmap with me. Do not create course files until we agree on the plan.

3. Answer the planning questions, refine the roadmap, and approve it when ready.
4. The agent creates the approved overview and first module, then helps you practice, review, and continue.

By default, courses are created under `courses/<course-slug>/` at your workspace root, never inside the installed skill folder. You can choose another location.

### A chat agent without file access

1. Open [PROMPT.md](PROMPT.md).
2. Paste its contents into the chat, or attach the file if the agent can read attachments.
3. Add your request, such as: "I want a course on writing short stories. I have two hours per week. Start by planning with me."

The agent can create the outline, lessons, activities, feedback, and progress summaries in chat. You can save them yourself. File creation, browsing, media review, and persistent memory depend on the agent's capabilities.

No special commands, APIs, plugins, code execution, or dependencies are required to use the instructions.

## How it works

1. **Understand:** identify the subject, learner, starting level, goals, and constraints.
2. **Assess:** use a short diagnostic when helpful.
3. **Plan together:** agree on outcomes, modules, practice, effort, and completion criteria.
4. **Create:** build the overview and next module in a suitable format.
5. **Teach and practice:** work through explanations, examples, and activities.
6. **Review and adapt:** give feedback, address gaps, and adjust the next step.
7. **Record:** keep track of created materials, completed activities, and demonstrated abilities separately.

The same workflow supports creating a course for other learners. Say who the audience is; the agent can include instructor notes, rubrics, and answer keys.

See [examples/course-requests.md](examples/course-requests.md) for requests across subjects and levels.

## Contents

```text
create-your-own-course/
├── README.md
├── SKILL.md                 # Canonical instructions, usable on their own
├── PROMPT.md                # Same instructions without metadata, ready to paste
├── CHANGELOG.md
├── examples/
│   └── course-requests.md   # Requests across subjects and learner levels
├── scripts/
│   └── check_prompt_sync.py # Verifies PROMPT.md matches SKILL.md
└── templates/
    ├── course-overview.md
    ├── module.md
    ├── learner-profile.md
    └── progress.md
```

Templates are optional and should be adapted. No course-specific materials are generated until you agree on a plan.

## Customize and maintain

Edit `SKILL.md` to change the behavior, then regenerate `PROMPT.md` (everything after the frontmatter) and verify:

```bash
python scripts/check_prompt_sync.py          # check
python scripts/check_prompt_sync.py --write  # regenerate PROMPT.md
```

To update an installed copy, replace the skill folder while preserving learner-created course files. To uninstall, remove the installed skill folder.

## Privacy

Courses can contain learner profiles, submissions, and progress notes. Before sharing or publishing a repository that contains your courses, review them, or keep `courses/` in `.gitignore`.

## License

MIT. See [LICENSE](../LICENSE).
