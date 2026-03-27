# Architecture Reference — Automotive Lifecycle Agents

**Author: Srinivas Reddy M**
Complete guide to every layer, what it contains, how layers connect,
what to modify when adding or changing something, and what to run.

---

## Table of contents

1. [System overview](#1-system-overview)
2. [Layer map](#2-layer-map)
3. [Layer 1 — CLAUDE.md (global rules)](#3-layer-1--claudemd-global-rules)
4. [Layer 2 — Skills (domain knowledge)](#4-layer-2--skills-domain-knowledge)
5. [Layer 3 — Agents (role behaviour)](#5-layer-3--agents-role-behaviour)
6. [Layer 4 — Python tools (standalone calculators)](#6-layer-4--python-tools-standalone-calculators)
7. [Layer 5 — Tests (quality gate)](#7-layer-5--tests-quality-gate)
8. [Layer 6 — CI/CD (automated validation)](#8-layer-6--cicd-automated-validation)
9. [How the layers connect](#9-how-the-layers-connect)
10. [Modification guide — what to change for each scenario](#10-modification-guide)
11. [Commands reference](#11-commands-reference)
12. [File naming rules](#12-file-naming-rules)

---

## 1. System overview

This project works as a Claude Code extension. When installed into `.claude/`,
Claude Code reads the agents and skills and uses them to respond to user prompts
with automotive domain expertise.

```
User types a prompt in plain English
        ↓
Claude Code reads CLAUDE.md global rules
        ↓
Description keywords in agents match the prompt → correct agent activates
        ↓
Agent loads its skills → skills load their reference files
        ↓
Agent + skill content shapes the response
        ↓
Python tools run independently from the command line (no Claude needed)
```

**The user never names a standard, an agent, or a skill.
Everything routes automatically from keywords in the prompt.**

---

## 2. Layer map

```
automotive-lifecycle-md_agents/
│
├── CLAUDE.md                    ← LAYER 1: Global rules (always loaded)
│
├── skills/                      ← LAYER 2: Domain knowledge
│   ├── iso26262-hara/
│   │   ├── SKILL.md             ← Trigger keywords + method overview
│   │   └── references/          ← Deep reference content (tables, templates)
│   ├── misra-c-2012/
│   ├── aspice-process/
│   ├── iso21434-tara/
│   ├── autosar-classic/
│   ├── uds-diagnostics/
│   ├── can-bus-analysis/
│   └── embedded-patterns/
│
├── md_agents/                      ← LAYER 3: Role behaviour
│   ├── developer/               ← 3 agents
│   ├── tester/                  ← 3 agents
│   ├── integrator/              ← 3 agents
│   └── project-lead/            ← 4 agents
│
├── tools/                       ← LAYER 4: Python CLI tools
│   ├── asil_calculator.py
│   ├── aspice_checker.py
│   ├── cal_calculator.py
│   └── gate_review_scorer.py
│
├── tests/                       ← LAYER 5: Automated tests
│   ├── test_asil_calculator.py
│   ├── test_aspice_checker.py
│   └── test_cal_calculator.py
│
├── .github/workflows/           ← LAYER 6: CI/CD
│   └── validate.yml
│
└── docs/                        ← Documentation (not a runtime layer)
```

---

## 3. Layer 1 — CLAUDE.md (global rules)

### What it contains
- Rules that apply to every agent and every response
- The auto-routing skill table (which keywords trigger which skill)
- Four worked examples showing prompt → agent activation

### How it connects to other layers
- Claude Code loads `CLAUDE.md` first, before any agent activates
- Rules in CLAUDE.md override any agent-level behaviour
- The skill auto-loading table in CLAUDE.md is documentation only —
  the real trigger mechanism is in each skill's `description:` field

### When to modify CLAUDE.md
- Adding a new global rule that applies to all agents
- Adding a new skill to the routing table (after adding the skill to `skills/`)
- Changing the synthetic data or safety disclaimer policy

### What to run after modifying
```bash
# No test needed — restart Claude Code to reload CLAUDE.md
# Verify by typing a prompt that should trigger the new rule
```

---

## 4. Layer 2 — Skills (domain knowledge)

### What it contains

Each skill folder has two parts:

```
skills/<skill-name>/
├── SKILL.md          ← Frontmatter (name, description/trigger keywords)
│                        + method overview + links to references
└── references/       ← Detailed content files
    ├── <table>.md    ← Complete tables, worked examples, templates
    └── <template>.md
```

### The trigger mechanism (most important concept)

The `description:` field in `SKILL.md` frontmatter is the **auto-routing trigger**.
Claude reads it and loads the skill when any keyword in the description appears in
the user's prompt. This is why descriptions must be long and keyword-rich.

```yaml
---
name: iso26262-hara
description: |
  Load automatically when any of these appear:
  HARA, ASIL, ASIL-A, ASIL-B, ASIL-C, ASIL-D,
  safety goal, hazard, ...
---
```

### How skills connect to agents

Agents declare which skills they always need in their frontmatter:

```yaml
skills:
  - iso26262-hara
  - misra-c-2012
```

When the agent activates, those skills load with it. Skills can also load
independently when keywords appear — without the agent explicitly listing them.

### How reference files connect to SKILL.md

SKILL.md contains pointers to reference files using this pattern:

```markdown
[reference: references/asil-table.md]
All 64 S x E x C combinations listed explicitly.
```

Claude reads the reference file content when the skill is active.

### 8 skills and what each reference contains

| Skill | Reference files | What they contain |
|-------|----------------|-------------------|
| iso26262-hara | asil-table.md | All 64 S×E×C → ASIL combinations |
| | hara-template.md | Full worked HARA example (brake-by-wire) |
| | safety-goal-format.md | Format rules + 3 worked safety goals |
| misra-c-2012 | top-rules.md | 15 rules: violation code + compliant rewrite |
| | deviation-template.md | Formal deviation request template |
| aspice-process | swe-work-products.md | All work products per SWE.1-6 with gaps |
| | assessor-questions.md | 5 real questions per SWE area + evidence |
| | gap-analysis-template.md | RAG gap report template |
| iso21434-tara | cal-table.md | Impact × Feasibility → CAL table |
| | tara-template.md | Full TARA example (OTA update system) |
| autosar-classic | bsw-modules.md | 15 BSW modules with APIs and issues |
| | swc-patterns.md | 5 SWC design patterns with ARXML names |
| uds-diagnostics | service-ids.md | All UDS services 0x10-0x3E |
| | nrc-codes.md | All NRC codes with root causes |
| can-bus-analysis | error-types.md | All 5 CAN error types with TEC/REC impact |
| | fault-patterns.md | Symptom → cause → debug step table |
| embedded-patterns | rtos-patterns.md | 5 RTOS patterns with safety notes |
| | interrupt-patterns.md | ISR design + Automotive Ethernet DMA |

### When to modify skills

| Scenario | What to change |
|----------|---------------|
| Standard table is incomplete | Edit the relevant reference file |
| Skill not triggering on a keyword | Add keyword to `description:` in SKILL.md |
| Add a new reference topic | Add new file in `references/`, add pointer in SKILL.md |
| Add a brand new skill | Create new `skills/<name>/` folder with SKILL.md + references/ |

---

## 5. Layer 3 — Agents (role behaviour)

### What it contains

Each agent is a single `.md` file with two parts:

```markdown
---                          ← YAML frontmatter (machine-readable config)
name: autosar-bsw-developer
description: |               ← Auto-routing trigger (keyword-rich)
  AUTOSAR, BSW, SWC, RTE...
tools:                       ← Which Claude tools the agent can use
  - Read
  - Write
skills:                      ← Which skills always load with this agent
  - autosar-classic
  - misra-c-2012
maxTurns: 15                 ← Max conversation turns before agent stops
---

## Role                      ← Markdown body (human-readable instructions)
...
## Response rules
...
## Output format
...
## Synthetic example
...
```

### The 4 agent frontmatter rules (never break these)

1. `name:` must be unique across all agents
2. `description:` must be 80+ words and keyword-rich — this is the trigger
3. **Never add `model:` field** — hardcoding a model breaks future updates
4. `gate-review-approver` must have `disable-model-invocation: true`

### Agent folder structure

```
md_agents/
├── developer/          ← Software construction role
│   ├── autosar-bsw-developer.md     maxTurns: 15 (complex design tasks)
│   ├── embedded-c-developer.md      maxTurns: 15
│   └── misra-reviewer.md            maxTurns: 6  (read-only, focused)
├── tester/             ← Verification and validation role
│   ├── sw-unit-tester.md            maxTurns: 12
│   ├── sil-hil-test-planner.md      maxTurns: 10
│   └── regression-analyst.md        maxTurns: 6  (read-only, analysis)
├── integrator/         ← Integration and field support role
│   ├── field-debug-fae.md           maxTurns: 8
│   ├── sw-integrator.md             maxTurns: 12
│   └── can-bus-analyst.md           maxTurns: 6  (read-only, analysis)
└── project-lead/       ← Project management and standards role
    ├── sw-project-lead.md           maxTurns: 12
    ├── safety-and-cyber-lead.md     maxTurns: 10 (read-only)
    ├── aspice-process-coach.md      maxTurns: 10 (read-only)
    └── gate-review-approver.md      maxTurns: 5  (manual trigger only)
```

### maxTurns logic

| maxTurns | Used for |
|----------|----------|
| 5–6 | Read-only analysis agents; short focused answers |
| 8–10 | Medium complexity agents; structured output |
| 12–15 | Full design and implementation agents |

### How agents connect to skills

```
Agent frontmatter                    Skill SKILL.md
─────────────────                    ──────────────
skills:               → loads →      name: iso26262-hara
  - iso26262-hara                    description: (trigger keywords)
  - misra-c-2012                     references/asil-table.md
                                     references/hara-template.md
```

### When to modify agents

| Scenario | What to change |
|----------|---------------|
| Agent not activating on your keywords | Add keywords to `description:` |
| Agent response format not right | Edit the `## Output format` section |
| Agent needs a new skill | Add skill name to `skills:` list |
| Agent writes files it shouldn't | Remove `Write` and `Edit` from `tools:` |
| Add a new agent | Create new `.md` in the appropriate role folder |
| New engineering role | Create new subfolder in `md_agents/` |

---

## 6. Layer 4 — Python tools (standalone calculators)

### What it contains

Four independent CLI tools. They run from the command line with no Claude
needed and no external pip dependencies.

| Tool | Standard | Input | Output |
|------|----------|-------|--------|
| asil_calculator.py | ISO 26262-3 Table 4 | S, E, C ratings | ASIL level |
| aspice_checker.py | Automotive SPICE | Phase + work products you have | Gap report |
| cal_calculator.py | ISO 21434 | Impact + Feasibility | CAL level |
| gate_review_scorer.py | Project gate | Phase + criterion statuses | RAG score |

### How tools connect to skills

Tools are **standalone** — they do not call skills or agents. However they
implement the same tables that the skills reference:

```
skills/iso26262-hara/references/asil-table.md  ←→  tools/asil_calculator.py
skills/iso21434-tara/references/cal-table.md   ←→  tools/cal_calculator.py
skills/aspice-process/references/swe-work-products.md ←→ tools/aspice_checker.py
```

**Rule:** If you update a table in a reference file, update the corresponding
tool's lookup table to keep them consistent.

### Tool structure pattern (same for all 4)

```python
# 1. Lookup table (dictionary) — the data
ASIL_TABLE = { ("S3","E4","C3"): "ASIL D", ... }

# 2. Core function — pure logic, testable
def lookup_asil(severity, exposure, controllability):
    ...

# 3. Print function — formatted output with disclaimer
def print_result(severity, exposure, controllability):
    ...

# 4. CLI entry point — argparse
def main():
    parser = argparse.ArgumentParser(...)
    ...
```

### When to modify tools

| Scenario | What to change |
|----------|---------------|
| Add a new S/E/C combination | Edit `ASIL_TABLE` dict in asil_calculator.py |
| Add a new ASPICE work product | Edit `SWE_WORK_PRODUCTS` dict in aspice_checker.py |
| Add new gate criterion | Edit `GATE_CRITERIA` dict in gate_review_scorer.py |
| Change output format | Edit the `print_result()` function |
| Add new CLI flag | Add `parser.add_argument()` and handle in `main()` |

**After any tool change — always run tests:**
```bash
pytest tests/ -v
```

---

## 7. Layer 5 — Tests (quality gate)

### What it contains

Three pytest files — one per tool (gate_review_scorer has no dedicated test file
but is covered through integration in the other tests).

```
tests/
├── test_asil_calculator.py    ← 20+ tests: all ASIL levels, invalid input
├── test_aspice_checker.py     ← gap detection, structure validation, all phases
└── test_cal_calculator.py     ← all CAL levels, table completeness, validation
```

### How tests connect to tools

Tests import directly from `tools/`:

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.asil_calculator import lookup_asil, print_result
```

### Test coverage targets

| Tool | Key assertions tested |
|------|-----------------------|
| asil_calculator | S3/E4/C3=ASIL D, only one ASIL D exists, all 5 ASIL levels reachable, invalid inputs raise ValueError |
| aspice_checker | All WPs present = 0 gaps, missing static analysis = HIGH risk gap, invalid phase = ValueError |
| cal_calculator | I4/AF4=CAL 4 only, I3/AF2=CAL 2, 16 entries in table, all CAL levels reachable |

### When to modify tests

| Scenario | What to change |
|----------|---------------|
| Added new lookup combination to a tool | Add test asserting the new combination |
| Changed risk level of an ASPICE work product | Update the corresponding risk assertion |
| Added new CLI flag | Add test calling the flag |
| Changed ASIL/CAL table values | Update expected values in tests |

### What to run

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=tools --cov-report=term-missing

# Run a single test file
pytest tests/test_asil_calculator.py -v

# Run a single test
pytest tests/test_asil_calculator.py::TestAsilLookup::test_s3_e4_c3_returns_asil_d -v
```

---

## 8. Layer 6 — CI/CD (automated validation)

### What it contains

One GitHub Actions workflow file: `.github/workflows/validate.yml`

It runs 4 jobs on every push and pull request to `main`:

| Job | What it checks |
|-----|---------------|
| test | pytest + coverage on all 3 test files |
| validate-agents | Frontmatter fields, no model: field, gate-review-approver rule, description length |
| validate-skills | SKILL.md present in every skill folder, name + description fields |
| lint | flake8 on tools/ and tests/ (max line length 88) |

### How CI connects to other layers

```
Push to GitHub
     ↓
validate-agents → reads md_agents/**/*.md → checks Layer 3
validate-skills → reads skills/*/SKILL.md → checks Layer 2
test            → imports tools/*.py → runs Layer 5 against Layer 4
lint            → checks tools/ and tests/ code style
```

### When to modify CI

| Scenario | What to change |
|----------|---------------|
| Add a new required frontmatter field | Add to the field check list in validate-agents job |
| Change Python version | Edit `python-version:` in setup-python step |
| Add a new test file | No change needed — `pytest tests/` picks it up automatically |
| Change max line length | Edit `--max-line-length` in lint job |

---

## 9. How the layers connect

### Full connection diagram

```
LAYER 1: CLAUDE.md
  │  global rules → applied to every response
  │  skill routing table → documentation reference
  ↓
LAYER 2: skills/<name>/SKILL.md
  │  description: keywords → auto-routing trigger
  │  references/ → deep content loaded when skill is active
  ↓
LAYER 3: md_agents/<role>/<name>.md
  │  description: keywords → agent auto-routing trigger
  │  skills: list → pulls in Layer 2 content
  │  tools: list → grants Claude Code tool permissions
  │  body (Role/Rules/Format/Example) → shapes response
  ↓
LAYER 4: tools/*.py              ← independent, run from terminal
  ↓
LAYER 5: tests/*.py              ← validates Layer 4 logic
  ↓
LAYER 6: .github/workflows/      ← validates Layer 2, 3, 4, 5 on push
```

### Key data flows

**Flow 1 — User prompt triggers an agent:**
```
User: "ASIL-B SWC for vehicle speed"
  → ASIL-B keyword → iso26262-hara skill loads
  → AUTOSAR/SWC keyword → autosar-bsw-developer agent activates
  → Agent body shapes the response format
  → iso26262-hara reference files provide ASIL context
  → autosar-classic skill provides SWC design patterns
```

**Flow 2 — Table in skill and table in tool must stay in sync:**
```
skills/iso26262-hara/references/asil-table.md  (human-readable table)
                ↕  must match
tools/asil_calculator.py  ASIL_TABLE dict  (machine-executable table)
```

**Flow 3 — Agent description drives CI validation:**
```
md_agents/developer/autosar-bsw-developer.md
  → description: field
  → CI validate-agents job checks word count ≥ 80
  → If too short → CI fails → push blocked
```

---

## 10. Modification guide

### Add a new agent

1. Decide the role folder: `developer/`, `tester/`, `integrator/`, or `project-lead/`
2. Create `md_agents/<role>/<new-agent-name>.md`
3. Write YAML frontmatter:
   - `name:` unique, lowercase-hyphen
   - `description:` 80+ words with all trigger keywords
   - `tools:` minimum needed
   - `skills:` skills this agent always needs
   - `maxTurns:` 5–15 based on complexity
   - **No `model:` field**
4. Write agent body: Role, What you work with, Response rules, Output format, Synthetic example
5. Update `CLAUDE.md` routing table if it's a new keyword domain
6. Update `docs/agent-guide.md` with the new agent entry
7. Run: `pytest tests/ -v` — no test change needed for agent files
8. Push: CI validate-agents job will check frontmatter automatically

### Add a new skill

1. Create folder: `skills/<new-skill-name>/`
2. Create `skills/<new-skill-name>/SKILL.md` with frontmatter + content
3. Create `skills/<new-skill-name>/references/` with at least 2 reference files
4. Reference files must have real content — no placeholder text
5. Update `CLAUDE.md` routing table to include the new skill
6. Update any agents that should auto-load this skill (add to their `skills:` list)
7. Run: no test needed — CI validate-skills job checks presence automatically
8. Update `docs/agent-guide.md` if the skill changes agent behaviour

### Expand an existing reference file

1. Open the reference file in `skills/<name>/references/`
2. Add the new content (table row, new section, worked example)
3. If the content is also in a Python tool lookup table: update the tool too
4. Run: `pytest tests/ -v` to confirm tool tests still pass

### Add a new Python tool

1. Create `tools/<new_tool>.py` following the 4-part structure:
   - Lookup table / data dict
   - Core logic function (pure, testable)
   - Print/output function
   - `main()` with argparse
2. Add author header: `Author: Srinivas Reddy M`
3. Create `tests/test_<new_tool>.py` with:
   - At least one test per major output value
   - Invalid input raises ValueError tests
   - Output function runs without error
4. Run: `pytest tests/ -v` — all tests must pass
5. CI will pick up the new test file automatically

### Modify the ASIL table

If you need to correct an ASIL value:
1. Edit `skills/iso26262-hara/references/asil-table.md` — update the table row
2. Edit `tools/asil_calculator.py` — update the `ASIL_TABLE` dict entry
3. Edit `tests/test_asil_calculator.py` — update the expected value in the test
4. Run: `pytest tests/test_asil_calculator.py -v`

### Modify the CAL table

Same pattern as ASIL:
1. Edit `skills/iso21434-tara/references/cal-table.md`
2. Edit `tools/cal_calculator.py` — update `CAL_TABLE` dict
3. Edit `tests/test_cal_calculator.py` — update expected value
4. Run: `pytest tests/test_cal_calculator.py -v`

---

## 11. Commands reference

### Install and setup
```bash
# Clone for current project
git clone https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents .claude

# Clone globally
git clone https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents ~/.claude

# Using setup.sh
./setup.sh --project     # current project
./setup.sh --global      # global
./setup.sh --remove      # remove from current project

# Update
git -C .claude pull
```

### Python tools
```bash
# ASIL calculator
python tools/asil_calculator.py --severity S3 --exposure E4 --controllability C2
python tools/asil_calculator.py --interactive
python tools/asil_calculator.py --list-all

# ASPICE checker
python tools/aspice_checker.py --phase SWE4 --have "unit_test_spec,test_results"
python tools/aspice_checker.py --phase all --have "srs,sad"
python tools/aspice_checker.py --list-phases

# CAL calculator
python tools/cal_calculator.py --impact I3 --feasibility AF2
python tools/cal_calculator.py --interactive
python tools/cal_calculator.py --list-all

# Gate review scorer
python tools/gate_review_scorer.py --phase SOP \
  --criteria "test_complete:pass,traceability:partial,cm_baselines:fail"
python tools/gate_review_scorer.py --phase SOR --interactive
python tools/gate_review_scorer.py --list-criteria SOP
```

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=tools --cov-report=term-missing

# Single file
pytest tests/test_asil_calculator.py -v

# Single test
pytest tests/test_asil_calculator.py::TestAsilLookup::test_s3_e4_c3_returns_asil_d
```

### Linting
```bash
pip install flake8
flake8 tools/ tests/ --max-line-length 88
```

### Git (first time)
```bash
cd "c:/SrinivasReddy/Projects/automotive-lifecycle-agents"
git init
git remote add origin https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents.git
```

---

## 12. File naming rules

| Layer | Convention | Example |
|-------|-----------|---------|
| Agents | lowercase-hyphen.md | `autosar-bsw-developer.md` |
| Skills folder | lowercase-hyphen | `iso26262-hara/` |
| SKILL.md | always `SKILL.md` | `SKILL.md` |
| Reference files | lowercase-hyphen.md | `asil-table.md` |
| Python tools | lowercase_underscore.py | `asil_calculator.py` |
| Test files | `test_` + tool name | `test_asil_calculator.py` |
| Agent `name:` field | matches filename without .md | `autosar-bsw-developer` |
| Skill `name:` field | matches folder name | `iso26262-hara` |

**Breaking these naming rules will cause CI validation to fail or skills/agents
to not load correctly in Claude Code.**
