# ASPICE Gap Analysis Template

Use this template to assess readiness before an ASPICE assessment.
RAG rating: GREEN = present and complete / AMBER = partial / RED = missing.

---

## Project Context (fill in before analysis)

- Project name: [synthetic / your project]
- Target capability level: [ Level 1 / Level 2 / Level 3 ]
- Assessment date: [scheduled date]
- Software lifecycle phase: [concept / design / testing / release]
- ECU / item under assessment: [e.g., Camera ECU, BMS ECU]

---

## Work Product Status Table

### SWE.1 — Software Requirements Analysis

| Work Product                        | Status   | RAG    | Risk Level | Notes                        |
|-------------------------------------|----------|--------|------------|------------------------------|
| SW Requirements Spec (SRS)          | [status] | [RAG]  | [risk]     |                              |
| Interface requirements              | [status] | [RAG]  | [risk]     |                              |
| SRS ↔ SysRS traceability matrix     | [status] | [RAG]  | [risk]     |                              |
| Change request records              | [status] | [RAG]  | [risk]     |                              |
| Requirements review records         | [status] | [RAG]  | [risk]     |                              |

### SWE.2 — Software Architectural Design

| Work Product                        | Status   | RAG    | Risk Level | Notes                        |
|-------------------------------------|----------|--------|------------|------------------------------|
| SW Architectural Design (SAD)       | [status] | [RAG]  | [risk]     |                              |
| Interface descriptions              | [status] | [RAG]  | [risk]     |                              |
| Dynamic behaviour descriptions      | [status] | [RAG]  | [risk]     |                              |
| SAD ↔ SRS traceability              | [status] | [RAG]  | [risk]     |                              |
| Design review record                | [status] | [RAG]  | [risk]     |                              |

### SWE.3 — Detailed Design and Unit Construction

| Work Product                        | Status   | RAG    | Risk Level | Notes                        |
|-------------------------------------|----------|--------|------------|------------------------------|
| SW detailed design documents        | [status] | [RAG]  | [risk]     |                              |
| Unit implementation (under CM)      | [status] | [RAG]  | [risk]     |                              |
| MISRA compliance evidence           | [status] | [RAG]  | [risk]     |                              |
| Deviation register                  | [status] | [RAG]  | [risk]     |                              |
| Traceability design ↔ SAD           | [status] | [RAG]  | [risk]     |                              |

### SWE.4 — Software Unit Verification

| Work Product                        | Status   | RAG    | Risk Level | Notes                        |
|-------------------------------------|----------|--------|------------|------------------------------|
| Unit test specification             | [status] | [RAG]  | [risk]     |                              |
| Unit test results                   | [status] | [RAG]  | [risk]     |                              |
| Coverage evidence (branch/MC/DC)    | [status] | [RAG]  | [risk]     |                              |
| Static analysis results             | [status] | [RAG]  | [risk]     |                              |
| Test ↔ design traceability          | [status] | [RAG]  | [risk]     |                              |

### SWE.5 — Software Integration

| Work Product                        | Status   | RAG    | Risk Level | Notes                        |
|-------------------------------------|----------|--------|------------|------------------------------|
| SW integration plan                 | [status] | [RAG]  | [risk]     |                              |
| Integration test specification      | [status] | [RAG]  | [risk]     |                              |
| Integration test results            | [status] | [RAG]  | [risk]     |                              |
| Build logs                          | [status] | [RAG]  | [risk]     |                              |
| Integration ↔ SAD traceability      | [status] | [RAG]  | [risk]     |                              |

### SWE.6 — Software Qualification Test

| Work Product                        | Status   | RAG    | Risk Level | Notes                        |
|-------------------------------------|----------|--------|------------|------------------------------|
| SWQT specification                  | [status] | [RAG]  | [risk]     |                              |
| SWQT results                        | [status] | [RAG]  | [risk]     |                              |
| Test environment description        | [status] | [RAG]  | [risk]     |                              |
| Regression test results             | [status] | [RAG]  | [risk]     |                              |
| SWQT ↔ SRS traceability             | [status] | [RAG]  | [risk]     |                              |

---

## Top 3 Actions (prioritised by risk)

| # | Action                                       | Owner  | Effort Est. | Due Date  |
|---|----------------------------------------------|--------|-------------|-----------|
| 1 |                                              |        |             |           |
| 2 |                                              |        |             |           |
| 3 |                                              |        |             |           |

---

## Assessor Finding Prediction Per Gap

| Gap Description                     | Finding Likely?  | Finding Type       | Predicted Severity |
|-------------------------------------|------------------|--------------------|--------------------|
| SRS not approved                    | Yes              | PA 2.2 finding     | Major              |
| No traceability matrix              | Yes              | BP 1.4 finding     | Major              |
| Detailed design = source code only  | Yes              | BP 3.1 finding     | Major              |
| MC/DC coverage missing for ASIL C   | Yes              | BP 4.2 finding     | Major              |
| Static analysis not run             | Yes              | BP 4.3 finding     | Major              |
| Integration tests not separated     | Yes              | BP 5.3 finding     | Minor              |
| Build logs missing                  | Yes              | PA 2.2 finding     | Minor              |
| Regression results informal         | Yes              | PA 2.2 finding     | Minor              |

---

## Overall Readiness Assessment

| Capability Level Target | GREEN work products | AMBER | RED | Readiness |
|-------------------------|---------------------|-------|-----|-----------|
| Level 1                 | [count]             | [n]   | [n] | [RAG]     |
| Level 2 (add PA 2.x)    | [count]             | [n]   | [n] | [RAG]     |

**Summary note:**
[Write 2-3 sentences describing the overall readiness and the single most
important gap to address before the assessment date.]
