# Agent Guide

Detailed reference for all 12 agents — what they do, when they activate,
and what output to expect.

---

## Developer Agents

### autosar-bsw-developer

**When it activates:** AUTOSAR, SWC, BSW, RTE, ARXML, port, runnable,
sender-receiver, client-server, DaVinci, EB tresos, BSW configuration,
AUTOSAR Classic, AUTOSAR Adaptive, ara::com, SOME/IP

**What it produces:**
- SWC type selection and port design with AUTOSAR naming
- Interface definitions with data types and update policy
- Runnable design with trigger and API calls
- BSW module configuration parameters with typical values
- ASIL impact notes for safety-relevant designs
- MISRA considerations for implementation

**Skills loaded automatically:** autosar-classic, misra-c-2012

**Example:** "Design a sender-receiver SWC for battery state of charge,
provider BMS ECU, consumer cluster ECU, 100ms cycle, ASIL-A"

---

### embedded-c-developer

**When it activates:** embedded C, RTOS, interrupt, ISR, watchdog, ring buffer,
state machine, volatile, FreeRTOS, DMA, stack, bare metal, peripheral driver,
CAN driver, Ethernet driver, 100BASE-T1

**What it produces:**
- Synthetic C code patterns with MISRA compliance notes
- RTOS task design with FreeRTOS API references
- ISR-to-task communication patterns
- Automotive Ethernet driver patterns with DMA
- Stack sizing guidance
- Unit test considerations per function
- TRACE32 MCU execution layer debug reference (Trace, Task, Register, Memory windows)
- CFSR register bit-level decode for crash analysis (STKERR, IACCVIOL, DACCVIOL)

**Expert approach:** Physical layer first → RTOS second → application third.
Never jumps to application logic before ruling out hardware or RTOS root causes.

**Skills loaded automatically:** misra-c-2012, embedded-patterns

**Example:** "Implement a watchdog service pattern for a FreeRTOS ECU with
3 safety-critical tasks, ASIL-B"

---

### misra-reviewer

**When it activates:** MISRA review, code review, rule violation, static analysis
finding, which MISRA rule, compliant rewrite, deviation justification, Polyspace,
QAC, PC-lint

**What it produces:**
- Exact rule ID with mandatory/required/advisory category
- Violation explanation with synthetic code pattern
- Compliant rewrite with explanation
- Root cause cluster analysis: groups violations by underlying developer habit
- Developer-intent interpretation per violation
- Sprint effort estimate per cluster with recommended deadline per priority level
- Deviation request template when compliant rewrite is not feasible

**Note:** Read-only agent. Does not write files.

**Skills loaded automatically:** misra-c-2012

---

## Tester Agents

### sw-unit-tester

**When it activates:** unit test, test case design, coverage, MC/DC, branch coverage,
equivalence partition, boundary value, SWE.4, test framework, pass criteria

**What it produces:**
- Test case table: TC-ID, objective, preconditions, inputs, expected result, ASIL note
- Boundary value analysis (min-1, min, min+1, max-1, max, max+1)
- MC/DC condition mapping for ASIL-C/D functions
- Branch coverage analysis
- Stub requirements and design traceability

**Skills loaded automatically:** aspice-process, misra-c-2012

---

### sil-hil-test-planner

**When it activates:** SIL test, HIL test, hardware in the loop, SWQT, test bench,
dSPACE, CANoe, integration test, SWE.5, SWE.6, qualification test

**What it produces:**
- Test plan with SIL vs HIL allocation table
- Requirements-based test cases per SWE.5/6
- Test environment description
- Regression test strategy with impact-based selection

**Skills loaded automatically:** aspice-process

---

### regression-analyst

**When it activates:** regression analysis, test delta, new test failures, pass rate
change, coverage change, which tests changed, test comparison

**What it produces:**
- Summary delta with quantified ASIL risk: ASIL-D affected / ASIL-B affected / QM count
- Failure clusters ranked by ASIL risk — never lists without grouping
- Probable cause linked to specific code change per cluster
- Coverage delta: specific module and function, not just percentage
- Flaky test identification with root cause
- HOLD / PROCEED WITH EXCEPTIONS / PROCEED recommendation with justification
- ASPICE SWE.4/5 impact: explicitly states if failures block a planned baseline

**Expert approach:** Clusters before diagnosing. Traces every cluster to its commit.

**Note:** Read-only analysis agent.

---

## Integrator / FAE Agents

### field-debug-fae

**When it activates:** DTC, fault code, field issue, customer complaint, bus-off,
UDS session failure, NRC, freeze frame, ECU not responding, OBD fault, battery fault,
DoIP session, DLT log

**What it produces:**
- STEP 0 — SYMPTOM TRANSLATION: translates customer complaint to AUTOSAR/OSI layer,
  primary debug tool, and probable domain before any diagnosis begins
- STEP 1 — Fault triage with ranked causes and tool-specific expected outputs
  (what you see in CANoe trace, DLT Viewer, TRACE32, Saleae, Wireshark)
- STEP 2 — Prioritised debug steps with tool + expected output per step
- DTC status byte 8-bit decode, NRC root cause analysis, UDS session reconstruction
- Safety consideration flag if fault is safety-relevant
- Escalation brief template for engineering escalation

**Skills loaded automatically:** uds-diagnostics, can-bus-analysis

---

### sw-integrator

**When it activates:** integration issue, build error, linker error, BSW wiring,
SWC port mismatch, RTE generation error, integration plan, SWE.5, release candidate

**What it produces:**
- AUTOSAR layer classification first — every error identified by layer before diagnosis
- AUTOSAR Integration Fault Classification table (RTE/BSW/Linker/Build/OS)
- Tool-specific debug reference: DaVinci port view, GCC linker map, TRACE32 stack canary
- Ranked root cause candidates with confirming test per candidate
- Release candidate baseline checklist (7 categories, never abbreviated)
- ASPICE SWE.5 work product impact note

**Skills loaded automatically:** autosar-classic, aspice-process

---

### can-bus-analyst

**When it activates:** CAN trace, bus-off, error frame, missing ACK, TEC, REC,
DBC, CANoe, PCAN, bit timing, SOME/IP, DoIP, automotive Ethernet, 100BASE-T1

**What it produces:**
- AUTOSAR/OSI/Debug Layer master table (always included): 7 layers from
  Physical/MCAL/Oscilloscope through Application/SWC/DLT and MCU/TRACE32
- OSI-layer fault classification before any diagnosis
- Mandatory TEC analysis block: net climb rate arithmetic + time-to-bus-off calculation
- TSN bandwidth budget and latency reference for automotive Ethernet scenarios
- Ranked probable causes with specific measurement, tool, pass/fail threshold
- Concrete investigation sequence per fault pattern

**Note:** Read-only analysis agent.

---

## Project Lead Agents

### sw-project-lead

**When it activates:** project plan, milestone, change request, schedule delay,
OEM request, release plan, ASPICE, SOP readiness, risk register

**What it produces:**
- Priority action list for project situations
- Change request impact analysis (schedule + safety + ASPICE)
- OEM query response structure
- ASPICE process guidance

**Note:** Also auto-loads iso26262-hara (when safety mentioned),
iso21434-tara (when cybersecurity mentioned), autosar-classic (when AUTOSAR mentioned).

---

### safety-and-cyber-lead

**When it activates:** HARA, ASIL, safety goal, TARA, CAL, hazard, threat analysis,
ISO 26262, ISO 21434, damage scenario, attack feasibility, FMEA, FTA

**What it produces:**
- HARA with S/E/C ratings, written justifications, ASIL, safety goals
- TARA with assets, threats, CAL, cybersecurity goals
- Co-engineering notes when safety and cybersecurity interact
- Always ends with mandatory review note

**Note:** Read-only analysis agent. Every output ends with the review disclaimer.

---

### aspice-process-coach

**When it activates:** ASPICE assessment, process gap, work product missing,
SWE.1 through SWE.6, assessor, gap analysis, Level 1/2/3

**What it produces:**
- Work product status table per SWE process area with RAG rating
- BP1–BP6 individual status per process area
- PA 2.2 hidden trap check: review record, approval record, and CM baseline
  verified as three separate items
- Top 3 priority actions with effort estimate
- Assessor finding prediction per BP number with Major/Minor severity
- Formal 3-part finding response template (action / evidence / prevention)
- Overall readiness assessment

**Expert approach:** Focuses on highest-risk BPs from experience (SWE.1 BP4,
SWE.2 BP5, SWE.5 BP1). PA 2.2 is the most frequent hidden trap at Level 2.

---

### gate-review-approver

**TRIGGER: Only activates on explicit `/gate-review` command.**
Never auto-triggers from conversation context.

**What it produces:**
- Gate criteria assessment table (SOR or SOP)
- Overall RAG with score
- Critical findings with risk classification
- Always ends with mandatory sign-off note

**Output always states:** "Final release decision requires sign-off by SW Project Lead,
Quality Manager, and Functional Safety Manager per your project release procedure."

---

## Auto-routing reference

| You mention...          | Agent activates                 | Skills load                    |
|-------------------------|---------------------------------|--------------------------------|
| AUTOSAR, SWC, BSW, RTE  | autosar-bsw-developer           | autosar-classic, misra-c-2012  |
| embedded C, RTOS, ISR   | embedded-c-developer            | misra-c-2012, embedded-patterns|
| MISRA rule, violation   | misra-reviewer                  | misra-c-2012                   |
| unit test, coverage     | sw-unit-tester                  | aspice-process, misra-c-2012   |
| SIL, HIL, SWQT          | sil-hil-test-planner            | aspice-process                 |
| test regression, delta  | regression-analyst              | aspice-process                 |
| DTC, NRC, field fault   | field-debug-fae                 | uds-diagnostics, can-bus-analysis|
| RTE error, build error  | sw-integrator                   | autosar-classic, aspice-process|
| CAN trace, bus-off      | can-bus-analyst                 | can-bus-analysis               |
| project plan, milestone | sw-project-lead                 | aspice-process                 |
| HARA, ASIL, safety goal | safety-and-cyber-lead           | iso26262-hara, iso21434-tara   |
| ASPICE assessment       | aspice-process-coach            | aspice-process                 |
| /gate-review            | gate-review-approver            | aspice-process, iso26262-hara  |
