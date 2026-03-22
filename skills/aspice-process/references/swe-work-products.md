# ASPICE SWE Work Products — Complete Reference

All evidence descriptions are generic patterns. No real project data.

## SWE.1 — Software Requirements Analysis

| Work Product               | Typical Evidence                                    | Common Gaps                                          |
|----------------------------|-----------------------------------------------------|------------------------------------------------------|
| SW Requirements Spec (SRS) | Approved document with version and date             | Not approved; missing non-functional requirements    |
| Interface requirements     | List of system-level interfaces with signals/data   | Vague interface descriptions; missing data types     |
| Req. traceability matrix   | Bidirectional table: SRS ID ↔ SysRS ID             | One-way only; gaps in coverage; outdated              |
| Change request records     | CR system with impact analysis per change           | Changes made without formal CR; no impact documented |
| Review records             | Meeting minutes or tool-based review with sign-off  | Review performed but not documented or not signed    |

## SWE.2 — Software Architectural Design

| Work Product              | Typical Evidence                                    | Common Gaps                                          |
|---------------------------|-----------------------------------------------------|------------------------------------------------------|
| SW Architectural Design   | Block diagrams, interface tables, approved doc      | Reviewed but not approved; only block diagrams       |
| Interface descriptions    | API specifications, signal definitions              | Internal interfaces documented but not external      |
| Dynamic behaviour desc.   | State diagrams, sequence diagrams per component     | Static design only; no dynamic behaviour evidence    |
| SAD ↔ SRS traceability    | Matrix mapping design components to requirements    | Missing or generated last-minute before assessment   |
| Review record             | Signed-off review with action items closed          | Review done informally; no signed evidence           |

## SWE.3 — Software Detailed Design and Unit Construction

| Work Product              | Typical Evidence                                    | Common Gaps                                          |
|---------------------------|-----------------------------------------------------|------------------------------------------------------|
| SW detailed design        | Low-level design per module (flowcharts, pseudo)   | Only source code as design — not acceptable          |
| Unit implementation       | Source code under CM with version history           | Code not baselined; version not traceable to design  |
| MISRA compliance evidence | Static analysis report from Polyspace/QAC/PC-lint  | Tool not qualified; no suppression records           |
| Deviation register        | Approved deviations with risk and sign-off          | Deviations suppressed in tool but not documented     |
| Traceability detail ↔ SAD | Matrix: detailed design elements ↔ SAD components  | Traceability ends at SAD; detailed level missing     |

## SWE.4 — Software Unit Verification

| Work Product              | Typical Evidence                                    | Common Gaps                                          |
|---------------------------|-----------------------------------------------------|------------------------------------------------------|
| Unit test specification   | Test cases per function with inputs/expected output | Only test results; no specification traceable to req |
| Unit test results         | Pass/fail per test case with tool, version, date   | Results exist but not linked to specific SW version  |
| Coverage evidence         | Coverage report: statement/branch/MC/DC             | Statement only; MC/DC missing for ASIL C/D           |
| Static analysis results   | Tool report with all findings addressed             | Tool run but findings not reviewed or suppressed     |
| Test ↔ design traceability| Matrix: test cases ↔ detailed design elements      | Tests exist but not traced to design requirements    |

## SWE.5 — Software Integration and Integration Test

| Work Product              | Typical Evidence                                    | Common Gaps                                          |
|---------------------------|-----------------------------------------------------|------------------------------------------------------|
| SW integration plan       | Documented build order, test levels, environment   | Plan exists as word of mouth; not documented         |
| Integration test spec     | Test cases for component interactions and interfaces| Unit tests reused as integration tests — not same    |
| Integration test results  | Results per test case with pass/fail and build ref | Integration tests pass but results not retained      |
| Build log                 | Build record: toolchain version, build date, flags | Manual builds without retained logs                  |
| Integration traceability  | Tests ↔ SAD (interface and component level)        | Traceability to SRS only; architecture level missing |

## SWE.6 — Software Qualification Test

| Work Product              | Typical Evidence                                    | Common Gaps                                          |
|---------------------------|-----------------------------------------------------|------------------------------------------------------|
| SWQT specification        | Requirements-based test cases (one per SW req)     | Tests cover features but not all requirements        |
| SWQT results              | Results per SWQT case with verdict and date        | Results in spreadsheet not linked to test spec ID    |
| Test environment desc.    | HW platform, tools, setup procedures               | Environment not documented; changes not tracked      |
| Regression test results   | Subset re-run after change, results retained       | Regression run but not formally recorded             |
| SWQT ↔ SRS traceability   | Every SRS requirement has at least one SWQT case  | Coverage gaps: non-functional reqs often not tested  |
