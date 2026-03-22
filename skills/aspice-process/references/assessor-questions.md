# ASPICE Assessor Questions — SWE.1 through SWE.6

Five realistic assessor questions per process area with evidence guidance.
Based on common assessment patterns — not verbatim from any assessment.

---

## SWE.1 — Software Requirements Analysis

**Q1: Show me your software requirements specification. Who approved it and when?**
Evidence needed: SRS document with approval signature, version, and date.
If reviewed but not approved — this is a PA 2.2 finding.

**Q2: How do you ensure every SW requirement is traceable to a system requirement?**
Evidence needed: Bidirectional traceability matrix. Assessor will check random
rows to verify the link exists and is correct.
If traceability only exists from system → SW but not SW → system, expect a finding.

**Q3: When a system requirement changes, how does that flow into your SW requirements?**
Evidence needed: Change request record showing impact analysis on SRS.
Show one real example of a CR that changed the SRS and the SRS revision.

**Q4: How do you handle ambiguous or infeasible requirements from the customer?**
Evidence needed: Requirements review records, customer negotiation log, or
SRS change history showing requirement was clarified or rejected with reason.

**Q5: Are your non-functional requirements documented — timing, memory, interfaces?**
Evidence needed: SRS sections covering: timing requirements, memory budget,
interface signal definitions, error handling requirements.
A purely functional SRS with no non-functional content is a common gap.

---

## SWE.2 — Software Architectural Design

**Q1: Show me your software architectural design. Does it describe all components?**
Evidence needed: SAD document with component diagrams showing all major SW units,
their responsibilities, and static relationships.
Block diagrams alone without interface specifications are insufficient.

**Q2: How does your architecture handle safety-relevant failures — what are your safe states?**
Evidence needed: SAD section on error handling, safe state transitions,
or FMEA/FMEDA at architecture level if ASIL applies.

**Q3: Show me how you trace from your design back to the software requirements.**
Evidence needed: Traceability matrix SAD components ↔ SRS requirements.
Assessor will check that every SRS requirement has at least one design element.

**Q4: How do you describe the dynamic behaviour of your system?**
Evidence needed: State machine diagrams, sequence diagrams, activity diagrams
for key use cases. A purely static architecture is a common gap.

**Q5: Was this design reviewed? Show me the review record.**
Evidence needed: Review meeting record with reviewers, date, findings raised,
findings closed. Tool-based review evidence (e.g., Gerrit/JIRA) is acceptable
if it shows reviewers and resolution of each comment.

---

## SWE.3 — Software Detailed Design and Unit Construction

**Q1: Is your detailed design documented separately from source code?**
Evidence needed: Low-level design documents (flowcharts, pseudo-code, Nassi-
Shneiderman diagrams) that exist before or alongside code — not generated from it.
Source code alone as detailed design is a typical finding.

**Q2: Show me your MISRA compliance status and how you handle deviations.**
Evidence needed: Static analysis tool report, deviation register with approved
deviations, tool qualification record.
If violations are suppressed in the tool without a signed deviation, expect a finding.

**Q3: How do you know your code matches the detailed design?**
Evidence needed: Traceability from code units / modules to detailed design elements.
Code review records referencing design document sections.

**Q4: Is your source code under configuration management? Show me the baseline.**
Evidence needed: CM tool (Git, ClearCase, PVCS) with baseline tag, history log,
and evidence that tagged version matches what was tested.

**Q5: What coding standards do you apply and how do you enforce them?**
Evidence needed: Coding guidelines document (MISRA, AUTOSAR C++14, project rules),
enforcement mechanism (CI check, tool, code review checklist).
Saying "we follow MISRA" without evidence of enforcement is insufficient.

---

## SWE.4 — Software Unit Verification

**Q1: Show me a unit test specification. How are test cases derived from design?**
Evidence needed: Unit test spec with test cases traceable to detailed design
requirements. Random spot check: pick one function, show its design and
the test cases that verify it.

**Q2: What is your test coverage and how was it measured?**
Evidence needed: Coverage report from tool (VectorCAST, LDRA, Testwell CTC++).
For ASIL C/D: MC/DC required. For ASIL B: branch coverage required.
Coverage achieved but not measured with a qualified tool is not sufficient.

**Q3: What static analysis results do you have and what did you do with findings?**
Evidence needed: Full tool report showing findings addressed. Each suppression
must have a comment or link to approved deviation. Zero-finding report is ideal.
A report with 200 open findings and no response is a major finding.

**Q4: Are unit test results linked to a specific software version?**
Evidence needed: Test results with: test date, tester, SW version, tool version.
Assessor checks that results correspond to the baselined SW — not a later version.

**Q5: Show me how you trace unit tests back to detailed design.**
Evidence needed: Traceability matrix: test case IDs ↔ detailed design elements.
Tests with no design traceability cannot be assessed for completeness.

---

## SWE.5 — Software Integration and Integration Test

**Q1: Show me your integration plan. What is the integration strategy?**
Evidence needed: Integration plan document defining: build order, interface-level
test approach, environment, acceptance criteria.
Incremental integration (bottom-up or top-down) preferred over big-bang.

**Q2: How are integration tests different from your unit tests?**
Evidence needed: Integration tests verify interfaces between components —
not just single-function behaviour. Assessor checks for tests at interface
boundaries (e.g., CAN signal passing through two components).

**Q3: Show me a build log for your release candidate.**
Evidence needed: Build output log with: timestamp, toolchain version, build flags,
warnings/errors addressed, resulting artefact checksum or version.
Manual builds without logs are a gap.

**Q4: Show me the traceability from integration tests to your architecture.**
Evidence needed: Matrix: integration test cases ↔ SAD interfaces/components.
Testing that cannot be linked to an architectural element cannot be assessed.

**Q5: What happens when an integration test fails? Show me an example.**
Evidence needed: Defect report or CR raised, linked to failing test, root cause
recorded, fix applied, retest result. Demonstrates the feedback loop is closed.

---

## SWE.6 — Software Qualification Test

**Q1: Show me that you have a test case for every software requirement.**
Evidence needed: SWQT ↔ SRS traceability matrix with 100% SRS coverage.
Missing coverage for non-functional requirements is the most common gap.

**Q2: Were the SWQT tests performed on the final release candidate?**
Evidence needed: Test results showing the exact SW build version tested matches
the release candidate. Version mismatch is an immediate finding.

**Q3: Show me your test environment description.**
Evidence needed: Document or configuration record specifying: hardware (ECU
type and version), test tools (CANoe version, dSPACE model), test bench setup,
calibration records for measurement equipment.

**Q4: What regression testing did you perform after the last change?**
Evidence needed: Regression test selection rationale (impact analysis of change),
subset of SWQT cases re-run, pass/fail results retained.
Full re-run of all tests after every change is ideal but impact-based is acceptable.

**Q5: Are your SWQT results formally reviewed and signed off?**
Evidence needed: Test report with review record, test manager sign-off,
open failures classified with risk assessment.
Results in a spreadsheet with no review is a PA 2.2 gap.
