# Automotive Lifecycle Agents

[![Tests](https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents/actions/workflows/tests.yml/badge.svg)](https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents/actions/workflows/tests.yml)
[![Agents](https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents/actions/workflows/validate-agents.yml/badge.svg)](https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents/actions/workflows/validate-agents.yml)
[![SDK](https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents/actions/workflows/validate-sdk.yml/badge.svg)](https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents/actions/workflows/validate-sdk.yml)
[![Skills](https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents/actions/workflows/validate-skills.yml/badge.svg)](https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents/actions/workflows/validate-skills.yml)
[![Lint](https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents/actions/workflows/lint.yml/badge.svg)](https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents/actions/workflows/lint.yml)
[![Agents](https://img.shields.io/badge/md__agents-12-7C3AED)]()
[![SDK](https://img.shields.io/badge/sdk__agents-1%20(expanding)-blue)]()
[![Skills](https://img.shields.io/badge/Skills-8-orange)]()
[![Standards](https://img.shields.io/badge/Standards-ISO%2026262%20%7C%20ASPICE%20%7C%20MISRA%20%7C%20ISO%2021434-green)]()

> **12 AI agents purpose-built for automotive software engineering — in two implementations.**
> `md_agents`: prompt-engineered Claude Code agents.
> `sdk_agents`: schema-enforced Python SDK agents with guaranteed structured output.

---

## Two implementations — one engineering purpose

This project explores two approaches to the same problem: getting an LLM to produce
accurate, structured, actionable output for automotive SW engineering roles.

| | `md_agents` | `sdk_agents` |
|---|---|---|
| Technology | Claude Code `.md` agent files | Python SDK + Streamlit (Groq / Llama 3.3) |
| Output enforcement | Prompt instructions (best effort) | JSON Schema via `response_schema` (guaranteed) |
| Interface | Claude Code chat tab | Browser app — `streamlit run sdk_agents/app.py` |
| API cost | Covered by Claude subscription | Free — Groq free tier (no credit card) |
| Agents | 12 roles, fully built | 1 built (expanding), same domain knowledge |
| Lesson learned | Prompt enforcement is unreliable at scale | Schema enforcement is the right architectural choice |

**Shared foundation:** both implementations load from the same `skills/` folder —
8 domain knowledge bases covering CAN bus, MISRA C, ASPICE, ISO 26262, AUTOSAR,
UDS diagnostics, ISO 21434, and embedded patterns.

---

## CI quality checks

Every push to this repository runs 5 automated checks:

| Badge | What it validates |
|---|---|
| **Tests** | 78 pytest cases verify all 4 Python tools produce correct outputs |
| **Agents** | All 12 `md_agents` files are structurally valid with correct frontmatter |
| **SDK** | `sdk_agents` schema validation, imports, skill loader, 15+ unit tests — no API key needed |
| **Skills** | All 8 skill files present and correctly formatted |
| **Lint** | Python code passes flake8 across tools and sdk_agents |

If any check fails, the corresponding badge turns red and the cause is visible in the Actions tab.

---

## What this is

Automotive software development follows strict international standards —
ISO 26262 for functional safety, ASPICE for process quality, MISRA C for
coding safety, ISO 21434 for cybersecurity. A generic AI assistant knows
*about* these standards. These agents work *within* them.

Each agent covers one engineering role in the automotive development lifecycle.
Describe your problem in plain English. The agent classifies it, applies the
right standard, and produces structured output a real engineer can act on.

**Built from:** hands-on experience across developer, tester, integrator,
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
> in your diagnostic tool and see if the
> problem correlates with any specific event..."

</td>
<td>

```
BUS ANALYSIS REPORT
Protocol: CAN 500 kbit/s
OSI Layer: L1 Physical (confirmed by pattern)
TEC climb rate: ~1.4 TEC/s net
Time to bus-off: 180 s → matches 3 min exactly

Probable Causes (ranked):
1. [HIGH] Alternator AC ripple on transceiver Vcc
   after engine reaches steady state (~60 s warmup)
   Test: oscilloscope Vcc pin, AC-coupled
   Fail: ripple > 100 mV or dip below 4.5 V

2. [HIGH] Ground potential shift under load
   Test: DMM — ECU chassis GND to battery (−)
   Fail: > 200 mV DC while engine running

3. [MEDIUM] EMC from ignition/inverter switching
   Test: scope CANH/CANL individually — look for
   common-mode burst at ignition firing frequency
```

</td>
</tr>
</table>

The agent classifies the fault by OSI layer before diagnosing. It calculates
the TEC climb rate from the symptom. It gives three ranked causes each with
a specific measurement, a tool, and a pass/fail threshold. No guessing.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    You describe the problem                      │
│          "bus-off after 3 min" / "ASIL-D PMHF too high"        │
│          "ASPICE assessment in 3 weeks" / "MISRA Rule 21.3"     │
└──────────────────────────┬──────────────────────────────────────┘
                           │  Claude Code reads your words
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Agent auto-routing                            │
│  Keywords in your message → right agent activates automatically │
│  No need to name standards. No need to pick an agent manually.  │
└──────┬────────────┬──────────────┬────────────────┬────────────┘
       │            │              │                │
       ▼            ▼              ▼                ▼
  Developer     Tester        Integrator       Project Lead
  agents (3)    agents (3)    agents (3)       agents (3)
       │            │              │                │
       └────────────┴──────────────┴────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Skills layer (8 skills)                       │
│  Agents load reference tables on demand — ASIL tables, MISRA    │
│  rule index, ASPICE BP checklists, attack feasibility scores,   │
│  AUTOSAR OS API, UDS service IDs, CAN error type reference      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 12 Agents — what each one produces

### Developer (3 agents)

| Agent | Activates when you mention | Produces |
|---|---|---|
| **embedded-c-developer** | embedded C, RTOS, watchdog, ISR, stack, DMA, ring buffer, Tricore, Cortex | MISRA-compliant code with per-rule annotation, worst-case stack depth calculation, windowed WDT kick window formula, TC3xx dual-core cache coherency pattern, TRACE32 MCU execution layer debug reference (Trace/Task/Register/Memory windows, CFSR register decode) |
| **autosar-bsw-developer** | AUTOSAR, SWC, BSW, RTE, ARXML, runnable, port, NvM, COM, CanIf | Full SWC design with exact RTE API names, port/interface definition, ASIL-B FFI partitioning note, DaVinci configuration parameter paths |
| **misra-reviewer** | MISRA, rule violation, static analysis, Polyspace, deviation, QAC | Prioritised violation report (mandatory → required → advisory), compliant rewrite per rule, root cause cluster analysis with developer-intent interpretation, sprint effort estimate per cluster, deviation justification template |

### Tester (3 agents)

| Agent | Activates when you mention | Produces |
|---|---|---|
| **sw-unit-tester** | unit test, MC/DC, coverage, Unity, stub, ASIL test | Test plan with truth table, MC/DC independence pairs per ISO 26262-6 Table 13, actual Unity test code with assertions, coverage summary |
| **sil-hil-test-planner** | SIL, HIL, dSPACE, CANoe, fault injection, SWE.5, SWE.6 | Full test plan with SIL vs HIL allocation, fault injection parameters (voltage ramp rates, sensor open/short), regression strategy by change type |
| **regression-analyst** | regression, new failures, pass rate dropped, test delta | Failure clusters ranked by ASIL risk, quantified ASIL-D/B/QM failure count per summary, commit-level change impact traceability, baseline HOLD/PROCEED recommendation with justification, ASPICE SWE.4/5 impact |

### Integrator (3 agents)

| Agent | Activates when you mention | Produces |
|---|---|---|
| **can-bus-analyst** | CAN, bus-off, Ethernet, I2C, SPI, UART, SOME/IP, oscilloscope, TEC, NACK | AUTOSAR/OSI/debug layer master table (7 layers, tool per layer), quantified TEC climb rate with time-to-bus-off arithmetic, TSN bandwidth budget and latency reference, per-protocol debug tool selection guide, SOME/IP-SD timing diagnosis |
| **sw-integrator** | integration error, RTE error, linker error, ARXML, memory map | AUTOSAR integration fault classification table (RTE/BSW/Linker/Build layer), tool-specific debug reference (DaVinci port view, GCC linker map, TRACE32 stack canary), root cause ranked diagnosis, release candidate baseline checklist |
| **field-debug-fae** | DTC, NRC, UDS session, flash failure, ECU not responding | Customer complaint → AUTOSAR/OSI layer translation (STEP 0 mandatory), fault triage with tool-specific expected outputs (CANoe trace, DLT Viewer, TRACE32, Saleae, Wireshark), DTC status byte 8-bit decode, NRC root cause analysis, UDS session reconstruction |

### Project Lead (3 agents + 1 gated)

| Agent | Activates when you mention | Produces |
|---|---|---|
| **safety-and-cyber-lead** | HARA, ASIL, safety goal, TARA, FMEA, FTA, PMHF, cybersecurity | HARA with S/E/C justifications, ASIL determination, AIAG-VDA DFMEA 7-step, FTA with minimal cut sets, TARA with 5-factor attack feasibility, PMHF contributor breakdown |
| **aspice-process-coach** | ASPICE assessment, gap analysis, work product, SWE.x, finding | RAG status table per process area with BP1–BP6 individual status, PA 2.2 hidden trap check (review record + approval record + CM baseline verified separately), assessor finding prediction by BP number, formal finding response template (3-part) |
| **sw-project-lead** | project plan, change request, risk, OEM request, milestone, release | Quantified risk register (probability × impact score), CR record with working-day schedule delta, OEM escalation response draft |
| **gate-review-approver** | `/gate-review` command only | Structured gate review report — never auto-triggers |

---

## 8 Skills — reference knowledge that loads automatically

| Skill | Loads when you mention | Contains |
|---|---|---|
| **iso26262-hara** | ASIL, HARA, safety goal, hazard | Full ASIL determination table, SPFM/LFM/PMHF targets per ASIL, safety mechanism catalog |
| **aspice-process** | ASPICE, assessment, SWE.x, gap | BP1–BP6 checklists for SWE.1–SWE.6, traceability matrix formats, work product naming |
| **misra-c-2012** | MISRA, rule violation, static analysis | Top 15 violated rules with compliant rewrites, deviation template |
| **iso21434-tara** | cybersecurity, TARA, CAL, OTA attack | 5-factor feasibility scoring table, STRIDE catalog, UN R155 threat list |
| **autosar-classic** | AUTOSAR, SWC, BSW, RTE | Full OS/COM/NvM API reference, OIL configuration examples, SWC patterns |
| **uds-diagnostics** | UDS, DTC, NRC, flash, diagnostic | All service IDs with session requirements, complete NRC table, flash sequence |
| **can-bus-analysis** | CAN, bus-off, error frame, TEC | All 5 CAN error types, fault pattern table, TEC/REC rules |
| **embedded-patterns** | embedded, RTOS, watchdog, ISR, stack | 5 RTOS patterns, interrupt handling, watchdog service pattern |

---

## Quick start

### md_agents — Claude Code (no cost, 12 agents)
```bash
# Global install — agents available in all your Claude Code projects
git clone https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents ~/.claude

# Restart Claude Code (VS Code extension or claude CLI)
# Agents activate automatically — no configuration needed
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
# Edit .env and add your GROQ_API_KEY

streamlit run app.py
# Opens http://localhost:8501 in browser
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

## Standards this project covers

| Standard | Area | Depth |
|---|---|---|
| **ISO 26262** | Functional Safety (automotive E/E systems) | HARA, ASIL, safety goals, DFMEA, FTA, FMEDA, PMHF, hardware metrics |
| **ISO 21434** | Cybersecurity Engineering | TARA, attack feasibility, CAL, cybersecurity goals, UN R155 |
| **ASPICE v3.1** | Software Process Assessment | SWE.1–SWE.6 base practices, PA 2.1/2.2, gap analysis, work products |
| **MISRA C:2012** | Embedded C Coding Standard | Mandatory/required/advisory rules, deviations, static analysis review |
| **AUTOSAR Classic** | ECU Software Architecture | SWC, BSW, RTE, COM, NvM, CanIf, OS API, OIL configuration |
| **ISO 14229 (UDS)** | Unified Diagnostic Services | All service IDs, NRC codes, flash sequence, session management |
| **ISO 11898** | CAN Bus | Error types, TEC/REC rules, bus-off recovery, bit timing |
| **IEEE 802.3bw** | 100BASE-T1 Automotive Ethernet | PHY thresholds, SOME/IP, DoIP, TSN |

---

## Notes

- All scenarios use synthetic data — no real company code or proprietary information
- Safety and cybersecurity outputs require review and approval by a qualified engineer before use in any project
- This is a personal project demonstrating AI agent accuracy for automotive SW engineering roles
