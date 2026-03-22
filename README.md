# Automotive Lifecycle Agents

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Built for Claude Code](https://img.shields.io/badge/Built%20for-Claude%20Code-7C3AED)](https://claude.ai/claude-code)
[![Agents](https://img.shields.io/badge/Agents-12-green)]()
[![Skills](https://img.shields.io/badge/Skills-8-orange)]()
[![CI](https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents/actions/workflows/validate.yml/badge.svg)](../../actions)

**AI agents for automotive SW engineering roles — developer, tester, integrator, project lead.**

A personal project testing how accurately AI agents perform when given proper
automotive domain context across the full software development lifecycle.
Background: SW developer, tester, integrator, and SW project lead experience.
All examples use synthetic data only.

---

## The key promise

Describe your problem in plain English.
The right standards load automatically.
**You never need to name ISO 26262, ASPICE, or MISRA. The agents detect what is needed from your words.**

```
You type:    "My CAN node goes bus-off after exactly 3 minutes, only when engine running"
You get:     Structured fault triage with ranked probable causes, TEC/REC analysis,
             oscilloscope debug steps, and Automotive Ethernet context
```

---

## Quick install

```bash
# Install for a specific project
git clone https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents .claude

# Install globally for all Claude Code projects
git clone https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents ~/.claude

# Restart Claude Code — agents load automatically
```

Update anytime:
```bash
git -C .claude pull
```

Remove anytime:
```bash
rm -rf .claude
```

---

## Four role examples

### Developer
```
You type:   "Design a sender-receiver SWC for vehicle speed, ASIL-B required"

You get:    AUTOSAR SWC design with port types, interface definition,
            ARXML element names, runnable trigger config at 10ms,
            ASIL-B freedom-from-interference note, MISRA compliance
            considerations for the implementation
```

### Tester
```
You type:   "Generate unit tests for a saturating uint16 adder, ASIL-B, MC/DC"

You get:    8 test cases covering all boundary values and branches,
            branch coverage analysis, MC/DC mapping, stub requirements,
            traceability to design reference, ASPICE SWE.4 note
```

### Integrator (FAE)
```
You type:   "Customer BMS fault P0A0F-00, -8C overnight, first occurrence"

You get:    Structured triage report with 4 ranked probable causes,
            physical inspection steps, freeze frame interpretation,
            safety relevance note, escalation brief template
```

### Project Lead
```
You type:   "3 weeks to ASPICE assessment, SAD reviewed but not approved,
            no traceability matrix, OTA feature added last week"

You get:    Gap analysis with RAG status per SWE process area,
            top 3 priority actions with effort estimate,
            assessor finding prediction per gap, cybersecurity
            impact note for the OTA feature addition
```

---

## Python tools

```bash
# ASIL level calculator
python tools/asil_calculator.py --severity S3 --exposure E4 --controllability C2
# Output: ASIL C

# ASPICE gap checker
python tools/aspice_checker.py --phase SWE4 \
  --have "unit_test_spec,test_results,coverage_evidence"
# Output: Gap report with risk levels and assessor questions

# CAL level calculator
python tools/cal_calculator.py --impact I3 --feasibility AF2
# Output: CAL 2

# Gate review scorer
python tools/gate_review_scorer.py --phase SOP \
  --criteria "test_complete:pass,traceability:partial,safety_plan:pass,\
  cm_baselines:fail,open_issues:partial"
# Output: Scored readiness with RAG status
```

---

## What is inside

| Component          | Count | What it covers                                          |
|--------------------|-------|---------------------------------------------------------|
| Agents             | 12    | Developer (3), Tester (3), Integrator (3), Lead (4)    |
| Skills             | 8     | ISO 26262, ASPICE, MISRA, ISO 21434, AUTOSAR, UDS, CAN, Embedded |
| Python tools       | 4     | ASIL calc, ASPICE checker, CAL calc, Gate scorer        |
| Tests              | 3     | Full pytest coverage of all 4 tools                     |
| Reference files    | 16    | Tables, templates, worked examples                      |

**Standards covered:** ISO 26262 · ISO 21434 · AUTOSAR Classic/Adaptive ·
ASPICE v3.1 · MISRA C:2012 · ISO 14229 (UDS) · CAN/CAN-FD · Automotive Ethernet

---

## Notes

- All scenarios use synthetic data — no real company code or proprietary information
- Safety-critical decisions always require review by a qualified engineer
- This is a personal demonstration project, not a production safety tool
