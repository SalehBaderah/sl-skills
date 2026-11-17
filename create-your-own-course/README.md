# Create Your Own Course

A reusable, agent-neutral skill for designing, building, and working through a personalized course on any subject.

Use it for English, writing, design, programming, science, professional skills, or another subject. The agent acts as your curriculum designer, content creator, tutor, and feedback partner. It first plans with you, then creates the course incrementally and adapts it as you progress.

This repository contains the reusable instructions and optional templates. Your course is created later through collaboration.

## Installation

With Node.js and npm installed, run from your project directory:

```bash
npx skills add https://github.com/SalehBaderah/sl-skills/tree/main --skill create-your-own-course --agent codex
```

Add `--global` to install across projects, or omit `--agent codex` to choose another supported agent. Reload skills or start a new agent session after installation.

## Quick start with any agent

### An agent that can read local files

1. Extract this repository and open the folder in your agent's workspace.
2. Send:

   > Read SKILL.md and use it to help me create my own course on [subject]. Start by understanding my goals and planning the roadmap with me. Do not create course files until we agree on the plan.

3. Answer the planning questions, refine the roadmap, and approve it when ready.
4. The agent creates the approved overview and first module, then helps you practice, review, and continue.

By default, courses created in this repository go under `courses/<course-slug>/`. You can choose another location. The reusable skill and repository README stay intact.

### A chat agent without file access

1. Open [PROMPT.md](PROMPT.md).
2. Paste its contents into the chat, or attach the file if the agent can read attachments.
3. Add your request, such as: "I want a course on writing short stories. I have two hours per week. Start by planning with me."

The agent can create the outline, lessons, activities, feedback, and progress summaries in chat. You can save them yourself. File creation, browsing, media review, and persistent memory depend on the agent's capabilities.

No special commands, APIs, plugins, code execution, or dependencies are required to use the instructions. Automatic skill discovery depends on the host agent; explicit file reading or pasting is the portable fallback.

## Optional: install as an agent skill

`SKILL.md` has a standard name/description frontmatter header. For agents that support this skill format, copy the entire `create-your-own-course` folder, including `templates/`, into the location specified by your agent.

For example, a Codex repository-local layout is:

```text
your-repo/
└── .agents/
    └── skills/
        └── create-your-own-course/
            ├── SKILL.md
            └── templates/
                └── ...
```

In Codex, you can then request:

```text
Use $create-your-own-course to help me build a course on [subject].
Plan the roadmap with me before creating materials.
```

Other agents may use different installation directories or invocation syntax. Follow their documentation, or use the universal quick start above. The included `AGENTS.md` helps agents that recognize that filename find the skill; it is not required.

## How it works

1. **Understand:** identify the subject, learner, starting level, goals, and constraints.
2. **Assess:** use a short diagnostic when helpful.
3. **Plan together:** agree on outcomes, modules, practice, effort, and completion criteria.
4. **Create:** build the overview and next module in a suitable format.
5. **Teach and practice:** work through explanations, examples, and activities.
6. **Review and adapt:** give feedback, address gaps, and adjust the next step.
7. **Record:** keep track of created materials, completed activities, and demonstrated abilities separately.

The same workflow supports creating a course for other learners. Say who the audience is; the agent can include instructor notes, rubrics, and answer keys.

## Repository contents

```text
create-your-own-course/
├── README.md
├── SKILL.md                 # Canonical instructions, usable on their own
├── PROMPT.md                # Same instructions without metadata, ready to paste
├── AGENTS.md                # Entry point for agents that read this filename
├── .gitignore
├── examples/
│   └── course-requests.md   # Requests across subjects and learner levels
└── templates/
    ├── course-overview.md
    ├── module.md
    ├── learner-profile.md
    └── progress.md
```

Templates are optional and should be adapted. No course-specific materials are generated until you agree on a plan.

## Start a new Git repository

The ZIP contains repository-ready source files; it does not contain Git history or a remote connection.

After extraction, from the `create-your-own-course` folder:

```sh
git init
git add .
git commit -m "Add Create Your Own Course skill"
```

Then create an empty repository with your preferred Git hosting provider and follow its instructions to add a remote and push. Alternatively, copy the package into an existing repository and commit it there. Include hidden files when copying.

## Customize and maintain

Edit `SKILL.md` to change the behavior. Keep `PROMPT.md` synchronized with everything after the frontmatter in `SKILL.md`; it is a plain Markdown copy for chat-only use.

Adjust or remove the optional templates to suit your workflow. To update an installed copy, replace the skill package while preserving learner-created course files. To uninstall it, remove the installed skill folder.

Before sharing a repository containing your courses, review learner profiles, submissions, and progress notes for information you want to keep private.
