# Automotive Lifecycle Agents

[![Tests](https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents/actions/workflows/tests.yml/badge.svg)](https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents/actions/workflows/tests.yml)
[![Agents](https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents/actions/workflows/validate-agents.yml/badge.svg)](https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents/actions/workflows/validate-agents.yml)
[![SDK](https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents/actions/workflows/validate-sdk.yml/badge.svg)](https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents/actions/workflows/validate-sdk.yml)
[![Skills](https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents/actions/workflows/validate-skills.yml/badge.svg)](https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents/actions/workflows/validate-skills.yml)
[![Lint](https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents/actions/workflows/lint.yml/badge.svg)](https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents/actions/workflows/lint.yml)

> **13 AI agents purpose-built for automotive software engineering.**
> Available as Claude Code agents and as a Streamlit browser app — no credit card required.

---

## CI quality checks

Every push runs 5 automated checks:

| Badge | What it validates |
|---|---|
| **Tests** | 78 pytest cases — all 4 Python tools produce correct outputs |
| **Agents** | All 13 Claude Code agent files are structurally valid with correct frontmatter |
| **SDK** | All 13 Python agent schemas, imports, routing (47 cases), unit tests — no API key needed |
| **Skills** | All 8 skill reference files present and correctly formatted |
| **Lint** | Python code passes flake8 |

---

## What this is

Automotive software development follows strict international standards —
ISO 26262 for functional safety, ASPICE for process quality, MISRA C for
coding safety, ISO 21434 for cybersecurity. A generic AI assistant knows
*about* these standards. These agents work *within* them.

Each agent covers one engineering role in the automotive development lifecycle.
Describe your problem in plain English. The agent classifies it, applies the
right standard, and produces structured output a real engineer can act on.

**Built from:** 11 years of hands-on experience across developer, tester, integrator,
and SW project lead roles in automotive ECU development.
All examples use synthetic data only.

---

## The difference — one question, two responses

**Question asked:** *"CAN node goes bus-off after 3 minutes, only when engine running. Other nodes fine."*

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
BUS ANALYSIS REPORT
OSI Layer: L1 Physical (confirmed by 3-min gradual onset)
AUTOSAR: MCAL (CanDrv) — not CanSM/CanIf
Tool: Oscilloscope + DMM

TEC math:
  TX rate: 10 msg/s → 1800 tx in 180s
  Errors needed for bus-off: 256/8 = 32
  Min error rate: 32/1800 = 1.8%
  Net TEC climb: 1.4 TEC/s → 180s to bus-off ✓

Probable Causes (ranked):
1. [HIGH] Alternator AC ripple on transceiver Vcc
   Test: oscilloscope Vcc pin AC-coupled, 2000 RPM
   Pass: ripple < 200 mV peak-to-peak
   Fail: ripple > 500 mV or dips below 4.5 V

2. [HIGH] Ground potential shift under engine load
   Test: DMM ECU chassis GND to battery negative
   Pass: offset < 50 mV
   Fail: offset > 200 mV — replace corroded GND strap

3. [MEDIUM] Thermal drift of CAN transceiver
   Test: heat gun at PCB, 3 min, engine off, CANoe active
   Pass: no bus-off from heat alone
   Fail: bus-off triggered by heat — replace transceiver
```

</td>
</tr>
</table>

The agent classifies the fault by OSI layer and AUTOSAR layer before diagnosing.
It calculates the exact TEC climb rate from the 3-minute symptom. Each cause has
a specific tool, probe point, and numeric pass/fail threshold. No guessing.

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
pytest sdk_agents/tests/ -v          # 20 unit tests, all mocked
python sdk_agents/test_routing.py    # 40 single-agent + 7 multi-agent routing cases
```

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
| **IEEE 802.3bw** | 100BASE-T1 Automotive Ethernet | PHY, SOME/IP, DoIP |

---

## Notes

- All scenarios use synthetic data — no real company code or proprietary information
- Safety and cybersecurity outputs require review and approval by a qualified engineer before use in any project
- This is a personal project demonstrating AI agent accuracy for automotive SW engineering roles
- Built by Srinivas Reddy Mudem — 11 years automotive ECU experience (Marquardt, AUTOSAR/CAN/diagnostics)
