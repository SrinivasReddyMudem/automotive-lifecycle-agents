---
name: aspice-process
description: |
  Load automatically when any of these appear:
  ASPICE, assessment, process area, work product,
  SWE.1, SWE.2, SWE.3, SWE.4, SWE.5, SWE.6,
  SUP.1, SUP.8, SUP.10, MAN.3, base practice,
  maturity level, capability level, Level 1,
  Level 2, Level 3, gap analysis, audit, evidence,
  traceability, traceability matrix, SRS, SAD,
  software requirements specification, software
  architectural design, unit test, integration
  test, qualification test, configuration
  management, change request, quality assurance,
  process compliance, work product checklist,
  assessor, assessment preparation, SPICE,
  automotive SPICE, process improvement,
  process capability, process attribute, PA 1.1,
  PA 2.1, PA 2.2, process performance, work
  product management, Capability Maturity,
  assessment findings, minor finding, major finding,
  evidence of review, baseline, release record,
  test specification approved, review record,
  configuration item, change control board.
---

## SWE process areas — purpose and key work products

### SWE.1 — Software Requirements Analysis
**Purpose:** Establish and analyse SW requirements derived from system requirements.
**Key work products:**
- Software Requirements Specification (SRS) — approved
- System/HW interface requirements
- Traceability: SW requirements ↔ system requirements
- Change request records for requirements changes

### SWE.2 — Software Architectural Design
**Purpose:** Establish the SW architecture and detailed design of SW components.
**Key work products:**
- Software Architectural Design (SAD) — reviewed and approved
- SW interface descriptions
- Dynamic behaviour description (state machines, sequences)
- Traceability: SAD ↔ SRS

### SWE.3 — Software Detailed Design and Unit Construction
**Purpose:** Provide detailed design for SW units and implement them.
**Key work products:**
- SW detailed design document per unit/module
- Unit source code (implementation)
- MISRA compliance evidence or deviation records
- Traceability: detailed design ↔ SAD

### SWE.4 — Software Unit Verification
**Purpose:** Verify that SW units satisfy their design and coding requirements.
**Key work products:**
- Unit test specification (per unit, per design)
- Unit test results (pass/fail with date and version)
- Coverage evidence: statement, branch, MC/DC where required
- Static analysis results (tool + qualification record)
- Traceability: unit tests ↔ detailed design

### SWE.5 — Software Integration and Integration Test
**Purpose:** Integrate SW units into a software item and verify integration.
**Key work products:**
- SW integration plan
- SW integration test specification
- SW integration test results
- Build log / integration record
- Traceability: integration tests ↔ SAD

### SWE.6 — Software Qualification Test
**Purpose:** Ensure that the integrated SW item meets its SW requirements.
**Key work products:**
- SW qualification test specification (SWQT spec)
- SW qualification test results (SWQT results)
- Test environment description
- Regression test results
- Traceability: SWQT ↔ SRS

---

## Capability level requirements

**Level 1 (Performed):** Work products exist and base practices executed.
PA 1.1 — process is performed and produces work products.

**Level 2 (Managed):** Work products are managed; reviews and baselines recorded.
PA 2.1 — performance management (planning, monitoring, adjustment)
PA 2.2 — work product management (documented, reviewed, baselined)

**Level 3 (Established):** Process uses an organisation-defined standard process.
PA 3.1 — process definition
PA 3.2 — process deployment

---

[reference: references/swe-work-products.md]
[reference: references/assessor-questions.md]
[reference: references/gap-analysis-template.md]
