# Contributing to Automotive Lifecycle Agents

Thank you for your interest. This is a personal project but contributions
from automotive engineers, safety experts, and AI practitioners are welcome.

---

## What contributions are welcome

- New agent files for automotive engineering roles not yet covered
- New skill files for automotive standards and domains
- Improvements to reference files (better examples, more complete tables)
- Bug fixes in Python tools
- Additional test coverage
- Documentation improvements

---

## Before contributing

1. Read CLAUDE.md — understand the global rules that apply to all content
2. All examples must use synthetic data — no real company data or proprietary content
3. Safety and cybersecurity analysis outputs must include the mandatory review note
4. Agent descriptions must be trigger-rich for accurate auto-routing (80+ words minimum)

---

## How to add a new agent

1. Create the file in the appropriate `md_agents/<role>/` folder
2. Use YAML frontmatter with these required fields:
   - `name:` — unique identifier, lowercase with hyphens
   - `description:` — rich keyword list for auto-routing (80+ words)
   - `tools:` — minimum necessary tools list
   - `maxTurns:` — appropriate for task complexity
   - Do NOT add `model:` field
3. Agent body must include:
   - Role description
   - What the agent works with
   - Response rules
   - Output format
   - Synthetic example with realistic input and response structure
4. Test the agent with at least 3 different inputs before submitting

## How to add a new skill

1. Create folder `skills/<skill-name>/`
2. Create `SKILL.md` with YAML frontmatter:
   - `name:` and `description:` (80+ words, keyword-rich)
3. Create `references/` folder with reference files
4. Reference files must have real content — no "see standard for details" placeholders

## Python tool requirements

- Full CLI with argparse
- Input validation with helpful error messages
- No external dependencies beyond Python stdlib
- All logic paths covered by tests
- Output includes disclaimer text for safety/cybersecurity tools

## Commit message format

```
<type>: <short description>

type: feat | fix | docs | test | refactor | ci
```

Example: `feat: add calibration-engineer agent with ECU calibration workflow`

## Pull request process

1. Fork and create a feature branch
2. Ensure all tests pass: `pytest tests/ -v`
3. Ensure lint passes: `flake8 tools/ tests/ --max-line-length 88`
4. Describe what the PR adds and why in the PR description
5. Reference any relevant automotive standard if applicable

---

## Questions

Open an issue with the label `question` for discussion before
starting a large contribution.
