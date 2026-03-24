# Changelog

All notable changes to Automotive Lifecycle Agents are documented here.
Format: [version] — date — summary

---

## [1.1.0] — 2026-03-24

### Agent enhancements — expert depth and structured debug output

**embedded-c-developer:**
- Added senior expert diagnostic mental model (physical layer first → RTOS → application)
- Added TRACE32 MCU execution layer debug reference table (Trace, Task, Register, Memory
  windows, Breakpoints, Performance Analyzer)
- Added CFSR register bit-level decode for crash analysis (STKERR, IACCVIOL, DACCVIOL)

**misra-reviewer:**
- Added expert mental model showing what each violation reveals about developer practice
- Added root cause cluster recognition (type conversion, error handling, memory safety,
  code structure clusters)
- Added sprint effort estimate per cluster and developer-intent interpretation per rule

**regression-analyst:**
- Added senior analyst expert thinking section (cluster before diagnosing, trace to commit,
  HOLD/PROCEED is the deliverable)
- Added quantified ASIL risk line to summary block: ASIL-D affected / ASIL-B affected / QM

**aspice-process-coach:**
- Added senior coach expert thinking section with highest-risk BP patterns from experience
- Added PA 2.2 hidden trap explanation (review record ≠ approved review ≠ CM baseline)
- Enhanced gap analysis output to show BP1–BP6 individual status per process area

**can-bus-analyst:**
- Added Complete System View: AUTOSAR/OSI/Debug Layer master table (7 rows, tool per layer,
  from Physical/MCAL/Oscilloscope up to Application/SWC/DLT)
- Added mandatory TEC analysis block to output: net climb rate arithmetic + time-to-bus-off
- Added TSN bandwidth budget and latency reference (100BASE-T1, VLAN priority table,
  camera bandwidth formula, PTP < 1 µs, E2E latency breakdown)

**field-debug-fae:**
- Added Customer Symptom → Layer Translation section with 9-row master mapping table
  (customer complaint → function affected → AUTOSAR layer → OSI layer → primary tool)
- Added Debug Tool Output Reference showing what you actually see in: CANoe trace,
  CANoe Diagnostic Console, DLT Viewer, TRACE32, Saleae, Wireshark
- Added STEP 0 — SYMPTOM TRANSLATION as mandatory first output block before fault triage
- Added STEP 2 — PRIORITISED DEBUG STEPS with tool + expected output per step

**sw-integrator:**
- Added AUTOSAR Integration Fault Classification table (error message → layer → tool →
  root cause) for RTE, BSW, Linker, Build, OS/MCAL error types
- Added Integration Debug tool reference: DaVinci port connection view, GCC linker map
  grep commands, TRACE32 stack overflow detection

---

## [1.0.0] — 2026-03-22

### Initial release

**Agents added (12 total):**
- Developer: autosar-bsw-developer, embedded-c-developer, misra-reviewer
- Tester: sw-unit-tester, sil-hil-test-planner, regression-analyst
- Integrator: field-debug-fae, sw-integrator, can-bus-analyst
- Project Lead: sw-project-lead, safety-and-cyber-lead, aspice-process-coach,
  gate-review-approver

**Skills added (8 total):**
- iso26262-hara: complete ASIL table, HARA template, safety goal format
- misra-c-2012: top 15 rules with code examples, deviation template
- aspice-process: SWE.1-6 work products, assessor questions, gap analysis template
- iso21434-tara: CAL table, TARA worked example
- autosar-classic: BSW modules reference, SWC design patterns
- uds-diagnostics: complete service ID table, NRC code reference
- can-bus-analysis: error types, fault pattern symptom table
- embedded-patterns: RTOS patterns, interrupt patterns with Automotive Ethernet

**Python tools added (4 total):**
- asil_calculator.py: ISO 26262-3 Table 4 complete lookup, interactive mode
- aspice_checker.py: SWE.1-6 gap analysis with risk classification
- cal_calculator.py: ISO 21434 CAL determination table
- gate_review_scorer.py: SOR/SOP readiness scoring with RAG output

**Tests added (3 files):**
- test_asil_calculator.py: 20+ test cases, 100% logic coverage
- test_aspice_checker.py: gap detection, validation, structure tests
- test_cal_calculator.py: all CAL levels, input validation

**CI/CD:**
- GitHub Actions workflow: pytest + coverage, agent validation,
  skill validation, flake8 lint

---

## Planned

- Automotive Ethernet dedicated skill (SOME/IP, DoIP, TSN, IEEE 802.1Qbv)
- V2X communications agent (DSRC, C-V2X)
- OTA update workflow integration
- Additional agents: calibration engineer, HIL test specialist
