# Getting Started

## What this project is

Automotive Lifecycle Agents is a set of Claude Code agent definitions and skills
for automotive software engineering roles. It covers the full SW development
lifecycle — from requirements and architecture through testing, integration, and
release — across four engineering roles:

- **Developer** — AUTOSAR, embedded C, MISRA C compliance
- **Tester** — unit testing, SIL/HIL planning, regression analysis
- **Integrator / FAE** — CAN bus analysis, field fault triage, SW integration
- **Project Lead** — ASPICE process, safety/cybersecurity lead, gate review

The agents use domain-specific skills that load automatically based on
keywords in your request. You never need to name a standard explicitly.

---

## Installation

### Option 1 — Project-specific install (recommended for trying it out)

```bash
cd your-project-directory
git clone https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents .claude
```

Restart Claude Code. The agents are now available for this project.

### Option 2 — Global install (available in all projects)

```bash
git clone https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents ~/.claude
```

Restart Claude Code.

### Option 3 — Using setup.sh

```bash
git clone https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents
cd automotive-lifecycle-agents

./setup.sh --project    # install into current project
./setup.sh --global     # install globally
./setup.sh --remove     # remove from current project
```

### Update

```bash
git -C .claude pull
# or
git -C ~/.claude pull
```

---

## First steps

Once installed, open Claude Code and try these examples.

**No need to specify the agent — just describe the problem:**

```
"I need a CAN sender-receiver SWC for vehicle speed, ASIL-B, 10ms cycle"
```
→ autosar-bsw-developer activates, autosar-classic and misra-c-2012 load

```
"My CAN node goes bus-off after 3 minutes, only when engine running"
```
→ can-bus-analyst and field-debug-fae activate, can-bus-analysis skill loads

```
"Generate unit tests for a saturating adder uint16, ASIL-B"
```
→ sw-unit-tester activates, aspice-process and misra-c-2012 load

```
"ASPICE assessment in 3 weeks, SAD not approved, no traceability matrix"
```
→ aspice-process-coach activates, gap analysis and assessor questions load

---

## Python tools

The tools work standalone — no Claude Code required:

```bash
# Determine ASIL level
python tools/asil_calculator.py --severity S3 --exposure E4 --controllability C2

# Check ASPICE work product gaps
python tools/aspice_checker.py --phase SWE4 \
  --have "unit_test_spec,test_results,coverage_evidence"

# Determine CAL level
python tools/cal_calculator.py --impact I3 --feasibility AF2

# Score gate review readiness
python tools/gate_review_scorer.py --phase SOP \
  --criteria "test_complete:pass,traceability:partial,safety_plan:pass,cm_baselines:fail"
```

Run tests:
```bash
pytest tests/ -v
```

---

## Important notes

1. All examples use synthetic data — never input real company code or proprietary data
2. Safety-critical outputs require review by a qualified engineer
3. The gate-review-approver agent only activates on explicit `/gate-review` command
4. Agents provide analysis and guidance — final decisions always rest with the engineer

---

## Folder structure

```
automotive-lifecycle-md_agents/
├── CLAUDE.md               — global rules loaded by Claude Code
├── md_agents/                 — 12 agent definitions (4 roles)
│   ├── developer/          — autosar-bsw-developer, embedded-c-developer, misra-reviewer
│   ├── tester/             — sw-unit-tester, sil-hil-test-planner, regression-analyst
│   ├── integrator/         — field-debug-fae, sw-integrator, can-bus-analyst
│   └── project-lead/       — sw-project-lead, safety-and-cyber-lead, aspice-process-coach, gate-review-approver
├── skills/                 — 8 domain skills with reference files
├── tools/                  — 4 Python CLI tools
├── tests/                  — pytest test suite
└── docs/                   — this documentation
```
