#!/usr/bin/env python3
"""Check (or with --write, regenerate) PROMPT.md from SKILL.md minus its frontmatter."""
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
skill = (root/"SKILL.md").read_text(encoding="utf-8").replace("\r\n", "\n")
if not skill.startswith("---\n"):
    sys.exit("SKILL.md must start with YAML frontmatter")
body = skill.split("\n---\n", 1)[1].lstrip("\n")
prompt_path = root/"PROMPT.md"
if "--write" in sys.argv:
    prompt_path.write_text(body, encoding="utf-8", newline="\n")
    print("PROMPT.md regenerated")
elif prompt_path.read_text(encoding="utf-8").replace("\r\n", "\n").rstrip() != body.rstrip():
    sys.exit("PROMPT.md is out of sync with SKILL.md; run with --write")
else:
    print("PROMPT.md is in sync")
