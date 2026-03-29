# Automotive Lifecycle Agents

[![Tests](https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents/actions/workflows/tests.yml/badge.svg)](https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents/actions/workflows/tests.yml)
[![Agents](https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents/actions/workflows/validate-agents.yml/badge.svg)](https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents/actions/workflows/validate-agents.yml)
[![SDK](https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents/actions/workflows/validate-sdk.yml/badge.svg)](https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents/actions/workflows/validate-sdk.yml)
[![Skills](https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents/actions/workflows/validate-skills.yml/badge.svg)](https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents/actions/workflows/validate-skills.yml)
[![Lint](https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents/actions/workflows/lint.yml/badge.svg)](https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents/actions/workflows/lint.yml)

> **13 AI agents purpose-built for automotive software engineering.**
> Available as Claude Code agents and as a Streamlit browser app — no credit card required.

---

## What this is

> Most AI tools respond to engineering questions with broad suggestions. This project
> demonstrates what changes when an LLM is constrained by domain schemas, engineering
> guardrails, and structured validation — producing outputs that are **precise, verifiable,
> and ready for real engineering use**.

After years across ECU development, integration, testing, and project roles, the same
pattern kept appearing — **complex issues taking days to diagnose** when a structured,
experience-driven approach could narrow them down in under an hour.

This gap has real impact:

- Unstable baselines during integration
- Repeated test failures and re-validation cycles
- Rework during safety reviews
- Late-stage change requests that should have been caught earlier

This project constrains an LLM using **domain knowledge, structured schemas, and engineering
guardrails** — so outputs reflect how an experienced automotive engineer reasons, not how
a generic assistant guesses.

**Goal:** Make expert-level reasoning accessible, consistent, and scalable across the
development lifecycle.

---

## Gap in existing AI tools

- Generate broad suggestions — no OSI/AUTOSAR classification
- No calculations shown (TEC math, ASIL determination, risk scoring)
- No traceability — conclusions without reasoning chains
- No standards alignment — ISO 26262, ASPICE, MISRA, UDS ignored
- Cannot distinguish stated facts from inferred assumptions

---

## Core approach

**Input Analysis** — every response separates what the engineer stated from what was
inferred or assumed. Nothing is silently assumed.

**Data Sufficiency** — before diagnosis, data completeness is rated: `SUFFICIENT` /
`PARTIAL` / `INSUFFICIENT`. Missing critical inputs are listed explicitly so the engineer
knows exactly what would sharpen the result.

**Structured Validation** — every output passes a multi-layer domain check before being
returned. Risk scores verified against P × I, feasibility factors reconciled against
system totals, schedule impacts numerically quantified. Any response that fails is
**rejected and retried**.

---

## The difference — one question, two responses

**Question asked:** *"CAN node goes bus-off after 3 minutes, only when engine running."*

<table>
<tr>
<th width="50%">Generic AI response</th>
<th width="50%">This agent's response</th>
</tr>
<tr>
<td>

> "There could be several reasons for bus-off.
> Check your CAN bus wiring and termination.
> Verify the baud rate settings are consistent
> across all nodes. Look at the error counters
> in your diagnostic tool..."

</td>
<td>

```
Protocol:   CAN | HIGH confidence
Data:       PARTIAL — oscilloscope trace required
            to confirm ripple vs GND offset

Facts:      bus-off after 3 min, engine-running dependency

Assumptions:
            ~1 msg/s TX rate (not provided)
            single node affected (not confirmed)

Basis:
  bus-off after 3 min
  → TEC accumulation, intermittent errors
  only when engine running
  → engine-coupled noise source

OSI Layer:     L1 Physical
AUTOSAR Layer: MCAL (CanDrv)

Tool:
  Oscilloscope
  - Diff probe on CAN_H/CAN_L (signal integrity)
  - Single-ended probe on Vcc (ripple check)

TEC Math:
  Net climb = 256 / 180s
              = 1.41 TEC/s
  Bus-off: ~181s — 3 min ✓

Ruled Out:
  Software issue — engine-dependent symptom
                   contradicts SW fault
  Bus overload   — does not match gradual
                   TEC-driven failure pattern

Causes:
  [HIGH]   Alternator ripple (most likely)
           Engine-running maps to supply noise
           Vcc AC-coupled
           Pass < 200mV / Fail > 500mV

  [MEDIUM] GND offset
           Condition-dependent noise possible
           but less consistent
           Pass < 50mV / Fail > 200mV

Next Action:
  Measure Vcc ripple at transceiver pin
  with engine at 2000 RPM

Contradictions:
  None — inputs consistent with
  TEC-driven bus-off behaviour
```

</td>
</tr>
</table>

The agent declares protocol confidence, separates stated facts from assumptions, shows
the reasoning basis before the conclusion, calculates TEC math from the symptom, and
actively rules out hypotheses. Each cause has a specific tool, probe point, and numeric
pass/fail threshold. No guessing.

---

## What engineers get

- **Classified before diagnosed** — every problem placed in context (OSI layer, AUTOSAR
  layer, ASPICE process area, or ASIL level) before analysis begins
- **Transparent calculations** — TEC accumulation, ASIL determination, risk scoring,
  and boundary conditions shown step-by-step
- **Concrete, testable outputs** — tool selection, exact probe points, and pass/fail
  thresholds for immediate validation
- **Standards-aligned reasoning** — outputs consistent with ISO 26262, ASPICE, MISRA C:2012,
  AUTOSAR, ISO 21434, and UDS

---

## How output quality is ensured

Each response follows a **structured engineering reasoning path** — starting from stated
facts, declaring assumptions, and narrowing causes based on evidence.

The output is not just a conclusion — it is **a clear reasoning path**: what was considered,
what was ruled out, and why a specific cause ranks higher than others.

Behind every output is a **multi-layer validation framework** enforcing domain-specific
rules — including risk scores automatically checked against P × I, feasibility factors
reconciling against system-level totals, and schedule impacts numerically quantified.
Any response that fails these checks is **rejected and retried** before the engineer
sees it. This validation ensures **internal consistency and prevents invalid engineering
conclusions**.

---

## Architecture — two layers working together

```
┌──────────────────────────────────────────────────────────────────┐
│                   User types plain English                        │
│  "bus-off after 3 min"  /  "ASIL-D safety goal"  /              │
│  "Customer says door not unlocking"  /  "MISRA Rule 21.3"       │
└───────────────────────────┬──────────────────────────────────────┘
                            │
          ┌─────────────────▼──────────────────┐
          │        Auto-routing engine          │
          │  Weighted keyword scoring (0–20+)   │
          │  Typo normalization (56 rules)      │
          │  Multi-agent detection (overlapping │
          │  domains activate secondary agents) │
          └─────────────────┬──────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
   Developer (3)       Tester (3)         Integrator (3)
   AUTOSAR / MISRA /   Unit test /        CAN / FAE /
   Embedded C          SIL-HIL /          SW Integrator
                       Regression
                            │
                   Project Lead (4)
                   ASPICE / Safety+Cyber /
                   SW Lead / Gate Review
                            │
        ┌───────────────────▼───────────────────┐
        │           Skills layer (8 skills)      │
        │  ISO 26262 HARA + ASIL tables          │
        │  ASPICE BP checklists (SWE + SUP + MAN)│
        │  MISRA C:2012 top rules + deviations   │
        │  ISO 21434 TARA + feasibility tables   │
        │  AUTOSAR Classic BSW/RTE/COM APIs      │
        │  UDS service IDs + NRC codes           │
        │  CAN error types + fault patterns      │
        │  Embedded RTOS + ISR patterns          │
        └───────────────────┬───────────────────┘
                            │
        ┌───────────────────▼───────────────────┐
        │       3-layer output quality           │
        │  1. JSON Schema enforcement (API)      │
        │  2. Semantic validators (Python)       │
        │  3. Retry with feedback on failure     │
        └───────────────────────────────────────┘
```

---

## 13 Agents — what each one produces

### Developer (3 agents)

| Agent | Activates when you mention | Produces |
|---|---|---|
| **embedded-c-developer** | embedded C, RTOS, ISR, watchdog, stack, DMA, Cortex, TC3xx | CFSR register decode, Cortex-M/R fault analysis, FreeRTOS stack overflow diagnosis, DMA transfer timing, MISRA-compliant code with per-rule annotation |
| **autosar-bsw-developer** | AUTOSAR, SWC, BSW, RTE, ARXML, runnable, port, NvM, COM | Full SWC design with exact RTE API names, port/interface ARXML, ASIL-B FFI partitioning, DaVinci config paths |
| **misra-reviewer** | MISRA, rule violation, static analysis, Polyspace, QAC | Violation report (mandatory → required → advisory), compliant C rewrite per rule, root cause clusters, deviation template, effort estimate |

### Tester (3 agents)

| Agent | Activates when you mention | Produces |
|---|---|---|
| **sw-unit-tester** | unit test, MC/DC, coverage, boundary value, stub, ASIL | Test plan with truth table, MC/DC independence pairs, boundary/equivalence cases, Unity test code, coverage summary |
| **sil-hil-test-planner** | SIL, HIL, dSPACE, CANoe, fault injection, SWE.5/6 | SIL vs HIL test allocation, fault injection parameters, regression strategy by change type, ASPICE evidence checklist |
| **regression-analyst** | regression, new failures, pass rate dropped, test delta | ASIL-D/B/QM failure clusters, flaky vs real regression assessment, HOLD/PROCEED recommendation, ASPICE SWE.4/5 impact |

### Integrator (3 agents)

| Agent | Activates when you mention | Produces |
|---|---|---|
| **can-bus-analyst** | CAN, bus-off, TEC, error frame, bit timing, candump | OSI + AUTOSAR layer classification, TEC math with time-to-bus-off calculation, 3 ranked probable causes with numeric thresholds |
| **sw-integrator** | integration error, RTE error, linker error, ARXML, memory map | AUTOSAR fault classification (RTE/BSW/Linker layer), tool-specific debug reference, root cause diagnosis, release baseline checklist |
| **field-debug-fae** | DTC, NRC, UDS session, ECU not responding, customer complaint | Customer symptom → AUTOSAR/OSI translation, DTC status byte 8-bit decode, NRC root cause analysis, UDS session reconstruction, lab-vs-field assessment |

### Project Lead (4 agents)

| Agent | Activates when you mention | Produces |
|---|---|---|
| **safety-and-cyber-lead** | HARA, ASIL, safety goal, TARA, hazard, cybersecurity | HARA with S/E/C justifications per event, ASIL determination table, TARA with 5-factor attack feasibility, co-engineering interface assessment |
| **aspice-process-coach** | ASPICE, assessment, SWE.x, gap analysis, work product | RAG status per process area (SWE + SUP.8 + SUP.10 + MAN.3), PA 2.2 3-condition check, finding prediction by BP number, formal finding response (3-part) |
| **sw-project-lead** | change request, schedule impact, project risk, milestone | Quantified risk register, CR record with schedule delta, OEM escalation response, resource plan |
| **gate-review-approver** | `/gate-review` command only | SOR/SOP gate report with per-criterion PASS/AMBER/FAIL — never auto-triggers |

---

## 8 Skills — reference knowledge that loads automatically

| Skill | Loads when you mention | Contains |
|---|---|---|
| **iso26262-hara** | ASIL, HARA, safety goal, hazard | Full ASIL table (all 64 S×E×C), SPFM/LFM/PMHF targets, safety mechanism catalog |
| **aspice-process** | ASPICE, assessment, SWE.x, gap | BP1–BP6 checklists for SWE.1–6, SUP.8/10, MAN.3, traceability formats, work product naming |
| **misra-c-2012** | MISRA, rule violation, static analysis | Top 15 violated rules with compliant rewrites, deviation template |
| **iso21434-tara** | cybersecurity, TARA, CAL, OTA attack | 5-factor feasibility scoring, STRIDE catalog, UN R155 threat list |
| **autosar-classic** | AUTOSAR, SWC, BSW, RTE | Full OS/COM/NvM API reference, OIL config, SWC patterns |
| **uds-diagnostics** | UDS, DTC, NRC, flash, diagnostic | All service IDs with session requirements, complete NRC table, flash sequence |
| **can-bus-analysis** | CAN, bus-off, error frame, TEC | All 5 CAN error types, fault pattern table, TEC/REC rules |
| **embedded-patterns** | embedded, RTOS, watchdog, ISR, stack | RTOS patterns, interrupt handling, watchdog service pattern |

---

## Quick start

### md_agents — Claude Code (no cost, 13 agents)
```bash
# Install globally — agents available in all Claude Code sessions
git clone https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents ~/.claude

# Restart Claude Code (VS Code extension or claude CLI)
# Type any engineering problem — the right agent activates automatically
```

Update anytime:
```bash
git -C ~/.claude pull
```

### sdk_agents — Streamlit browser app (free, Groq API)
```bash
cd sdk_agents
pip install -r requirements.txt

# Get a free API key (no credit card) at console.groq.com
cp .env.example .env
# Edit .env and set: GROQ_API_KEY=your-key

streamlit run app.py
# Opens http://localhost:8501 in your browser
```

Run without the UI (CLI mode):
```bash
python run.py --agent can-bus-analyst --prompt "CAN node goes bus-off after 3 minutes"
```

Run tests (no API key needed):
```bash
pytest sdk_agents/tests/ -v
python sdk_agents/test_routing.py
```

---

## CI quality checks

Every push runs 5 automated checks:

| Badge | What it validates |
|---|---|
| **Tests** | 363 pytest cases — all Python agents produce correct, validated outputs |
| **Agents** | All 13 Claude Code agent files are structurally valid with correct frontmatter |
| **SDK** | All 13 Python agent schemas, imports, routing, and unit tests — no API key needed |
| **Skills** | All 8 skill reference files present and correctly formatted |
| **Lint** | Python code passes flake8 |

---

## Python tools included

```bash
# Calculate ASIL from severity, exposure, controllability
python tools/asil_calculator.py --severity S3 --exposure E4 --controllability C2
# → ASIL C

# Check ASPICE readiness for a process area
python tools/aspice_checker.py --phase SWE4 --have "unit_test_spec,test_results"
# → Gap report with assessor risk per missing item

# Calculate Cybersecurity Assurance Level
python tools/cal_calculator.py --impact I3 --feasibility AF2
# → CAL 2

# Score a gate review readiness
python tools/gate_review_scorer.py --phase SOP \
  --criteria "test_complete:pass,traceability:partial,safety_plan:pass"
# → Scored RAG status with blockers
```

---

## Standards covered

| Standard | Area | Depth |
|---|---|---|
| **ISO 26262** | Functional Safety | HARA, ASIL, safety goals, DFMEA, PMHF, hardware metrics |
| **ISO 21434** | Cybersecurity Engineering | TARA, 5-factor attack feasibility, CAL, UN R155 |
| **ASPICE v3.1** | Software Process Assessment | SWE.1–SWE.6, SUP.8/10, MAN.3, PA 2.1/2.2 |
| **MISRA C:2012** | Embedded C Coding Standard | Mandatory/required/advisory, deviations, static analysis |
| **AUTOSAR Classic** | ECU Software Architecture | SWC, BSW, RTE, COM, NvM, CanIf, OS API |
| **ISO 14229 (UDS)** | Unified Diagnostic Services | All service IDs, NRC codes, flash sequence |
| **ISO 11898** | CAN Bus | Error types, TEC/REC rules, bus-off recovery |

*Automotive Ethernet (IEEE 802.3bw) and LIN are recognised, with dedicated skill depth under active development.*

---

## Who this is relevant for

- SW Integration Engineers — CAN/UDS fault triage, baseline stability
- Safety Engineers — HARA, ASIL determination, safety review support
- Embedded Developers — MISRA compliance, AUTOSAR SWC design
- Test Engineers — SIL/HIL planning, unit test design, MC/DC coverage
- Project Leads — ASPICE readiness, risk tracking, milestone assessment
- Field Application Engineers — field fault triage, DTC analysis

---

## What's next

- Adding **structured sub-models** for richer diagnostic context (freeze frame, port connection status, damage scenario, effort estimate)
- Strengthening **validator coverage** across all 13 agents for edge cases and type safety
- Enhancing **protocol coverage** for LIN and Automotive Ethernet
- Deepening **reasoning logic** for complex multi-node and multi-layer interactions

---

## Notes

- All scenarios use synthetic data — no real company code or proprietary information
- Safety and cybersecurity outputs require review and approval by a qualified engineer before use in any project
- This is a personal project demonstrating AI agent accuracy for automotive SW engineering roles

---
*Built by Srinivas Reddy Mudem*
