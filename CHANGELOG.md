# Changelog

All notable changes to Automotive Lifecycle Agents are documented here.
Format: [version] — date — summary

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
