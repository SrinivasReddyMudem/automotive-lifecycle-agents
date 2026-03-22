# ASPICE Base Practice Checklists and Work Product Templates

## SWE.1 Assessment Checklist

### BP1: Specify software requirements

- [ ] Requirements documented in Software Requirements Specification (SRS)
- [ ] Each requirement has a unique ID (e.g., SWE-REQ-001)
- [ ] Functional and non-functional requirements specified
- [ ] Interface requirements specified (CAN signals, function calls, timing)
- [ ] Safety requirements with ASIL assignment specified
- [ ] Requirements use "shall" language (not "should", "may", "will")
- [ ] Requirements are unambiguous — single interpretation possible

### BP2: Analyze software requirements

- [ ] Requirements reviewed for correctness against system specification
- [ ] Requirements reviewed for completeness (no missing functions)
- [ ] Requirements reviewed for consistency (no contradictions)
- [ ] Requirements reviewed for testability (verifiable in test)
- [ ] Analysis findings documented
- [ ] Defects tracked and resolved before baseline

### BP5: Bidirectional traceability

- [ ] Traceability matrix exists (system req -> software req)
- [ ] All system requirements traced to at least one software requirement
- [ ] All software requirements traced to a system requirement (no orphans)
- [ ] Orphan requirements justified if present
- [ ] Traceability maintained in tool or controlled document

### BP6: Communicate and approve requirements

- [ ] SRS reviewed and approved with sign-off
- [ ] SRS distributed to all stakeholders (architect, tester, safety)
- [ ] Changes to requirements go through change control

**Evidence for SWE.1**:
- 17-11: Software requirements specification (SRS)
- 13-19: Verification criteria
- 13-22: Traceability record
- 13-16: Review records (sign-offs)

---

## SWE.2 Assessment Checklist

### BP1: Develop software architectural design

- [ ] Architecture document exists and is approved
- [ ] Components identified with responsibilities defined
- [ ] Component boundaries and interfaces specified
- [ ] Architecture reviewed by independent reviewer (ASIL C/D)

### BP2: Allocate requirements to components

- [ ] All software requirements allocated to components
- [ ] Allocation documented in traceability matrix
- [ ] No single component overloaded (complexity managed)

### BP3: Define interfaces between components

- [ ] All interfaces documented (function signatures, data structures, timing)
- [ ] Interface timing and periodicity specified
- [ ] Error handling at interfaces specified

### BP4: Describe dynamic behavior

- [ ] State machines documented for stateful components
- [ ] Sequence diagrams for key interactions
- [ ] Task/interrupt scheduling described

**Evidence for SWE.2**:
- 17-01: Software architectural design specification
- 17-02: Software interface specification
- 13-22: Traceability record (req -> component)

---

## SWE.3 Assessment Checklist

### BP1: Develop detailed design

- [ ] Detailed design document exists per software unit
- [ ] Algorithms described (not just code)
- [ ] Data flow diagrams or pseudocode provided

### BP2: Describe dynamic behavior at unit level

- [ ] State machines for complex units
- [ ] Error handling within unit described

### BP5: Traceability to architecture

- [ ] Each software unit traceable to architecture component
- [ ] Each architecture component has at least one software unit

**Evidence for SWE.3**:
- 17-03: Software detailed design specification
- 17-04: Software unit (source code with review)
- 13-22: Traceability record

---

## SWE.4 Assessment Checklist (Unit Testing)

### BP1: Develop unit test specification

- [ ] Unit test specification exists per software unit
- [ ] Test cases cover all requirements allocated to unit
- [ ] Test cases cover boundary conditions and equivalence classes
- [ ] MC/DC test cases designed for ASIL C/D

### BP2: Select and apply test techniques

- [ ] Equivalence class partitioning applied
- [ ] Boundary value analysis applied
- [ ] For ASIL C/D: MC/DC explicitly designed and recorded

### BP4: Achieve coverage targets

- [ ] Statement coverage measured and documented
- [ ] Branch coverage measured and documented
- [ ] MC/DC coverage measured for ASIL D
- [ ] Coverage gaps analyzed and justified or addressed

### BP5: Traceability

- [ ] Each test case traced to a software requirement
- [ ] Each software requirement has at least one test case

**Coverage targets**:

| ASIL | Statement | Branch | MC/DC |
|------|-----------|--------|-------|
| A    | 100%      | Target | N/A   |
| B    | 100%      | 100%   | N/A   |
| C    | 100%      | 100%   | Target|
| D    | 100%      | 100%   | 100%  |

**Evidence for SWE.4**:
- 17-12: Software unit test strategy
- 17-13: Software unit test specification
- 17-14: Software unit test report (with coverage metrics)

---

## SWE.5 Assessment Checklist (Integration Testing)

### BP1: Integration test specification

- [ ] Integration test specification exists
- [ ] Test cases verify interface behavior between components
- [ ] Test cases cover error injection across interfaces

### BP3: Achieve coverage

- [ ] Interface coverage (all interfaces exercised)
- [ ] Structural coverage at integration level

**Evidence for SWE.5**:
- 17-06: Software integration test strategy
- 17-07: Software integration test specification
- 17-08: Software integration test report

---

## SWE.6 Assessment Checklist (Qualification Testing)

### BP1: Qualification test specification

- [ ] Qualification test specification exists
- [ ] Test cases verify all software requirements end-to-end
- [ ] Pass/fail criteria defined for all test cases

### BP3: Complete traceability

- [ ] All software requirements covered by at least one qualification test
- [ ] All qualification tests traced to requirements

**Evidence for SWE.6**:
- 17-09: Qualification test strategy
- 17-10: Qualification test specification
- 17-15: Qualification test report

---

## Generic Practice GP 2.1 Checklist (Performance Management)

- [ ] Process performance objectives defined (schedule, effort, quality)
- [ ] Performance monitored (actual vs planned weekly or bi-weekly)
- [ ] Status reported regularly to project lead
- [ ] Deviations from plan identified
- [ ] Corrective actions defined and tracked to closure

**Evidence for GP 2.1**:
- 15-20: Project plan (with objectives)
- 15-21: Project status reports (weekly/bi-weekly)
- 14-04: Schedule (Gantt chart or equivalent)
- Meeting minutes with action items

---

## Generic Practice GP 2.2 Checklist (Work Product Management)

- [ ] Work product requirements defined (templates, standards to follow)
- [ ] Work products reviewed before use/release
- [ ] Review criteria defined (checklists exist for each WP type)
- [ ] Review findings documented (not just "reviewed — OK")
- [ ] Work products under version control
- [ ] Baselines established at defined project milestones

**Evidence for GP 2.2**:
- Document templates (SRS, architecture, test spec)
- Review checklists per work product type
- 13-16: Review records (with names, dates, findings, dispositions)
- 15-05: Configuration management records (version history, baselines)

---

## Naming Conventions for Work Products

### Work Product Naming Pattern

| Work Product Type | Pattern | Example |
|-------------------|---------|---------|
| Requirements spec | [PROJ]-SWE-REQ-[Component]-v[X.Y].md | PROJ-ESC-SWE-REQ-Control-v1.2.md |
| Architecture spec | [PROJ]-SWE-ARCH-[Component]-v[X.Y].md | PROJ-ESC-SWE-ARCH-Control-v2.0.md |
| Detailed design   | [PROJ]-SWE-DES-[Module]-v[X.Y].md | PROJ-ESC-SWE-DES-Plausibility-v1.0.md |
| Unit test spec    | [PROJ]-SWE-TEST-UT-[Component]-v[X.Y].md | PROJ-ESC-SWE-TEST-UT-Control-v1.1.md |
| Integration test  | [PROJ]-SWE-TEST-IT-[Component]-v[X.Y].md | PROJ-ESC-SWE-TEST-IT-Control-v1.0.md |
| Test report       | [PROJ]-SWE-TESTREP-[Level]-[Component]-[Date].pdf | PROJ-ESC-TESTREP-UT-Control-20260315.pdf |

### Requirement ID Convention

```
Format: [Type]-REQ-[Component]-[Number]

Examples:
SYS-REQ-ESC-042    (System requirement for ESC, number 42)
SWE-REQ-ESC-001    (Software requirement for ESC, number 1)
HW-REQ-SENSOR-015  (Hardware requirement for sensor)

Numbering: use leading zeros (001, 002, ..., 099, 100)
```

### Test Case ID Convention

```
Format: TC-[Req]-[Level]-[Number]

Levels: UT (Unit), IT (Integration), QT (Qualification), ST (System)

Examples:
TC-SWE-001-UT-01   (Unit test 1 for SWE-REQ-001)
TC-SWE-042-IT-03   (Integration test 3 for SWE-REQ-042)
```

---

## Traceability Matrix Format

### Forward Traceability (Requirements -> Tests)

```
| Req ID  | Requirement        | ASIL | Component   | Unit      | Int Test | Status    |
|---------|--------------------|------|-------------|-----------|----------|-----------|
| SWE-001 | Wheel speed calc   | D    | WheelSpeed.c| TC-UT-01  | TC-IT-05 | Verified  |
| SWE-002 | Plausibility check | D    | Plaus.c     | TC-UT-02  | TC-IT-06 | In review |
```

### Backward Traceability (Tests -> Requirements)

```
| Test ID  | Description      | Verifies Req | Pass/Fail | Date       |
|----------|------------------|--------------|-----------|------------|
| TC-UT-01 | Nominal speed    | SWE-001      | Pass      | 2026-03-15 |
| TC-IT-05 | ESC integration  | SWE-001, 003 | Pass      | 2026-03-18 |
```

---

## Common Pitfalls Assessors Flag

### SWE.1 Pitfalls
- Requirements too high-level ("software shall provide ESC function" — not testable)
- No verification method specified per requirement
- Missing traceability to system requirements
- Requirements not reviewed or approved

### SWE.2 Pitfalls
- Architecture diagram without component descriptions
- Interfaces vaguely described ("via CAN" without signal names, timing, format)
- No allocation of requirements to components (no traceability)
- No dynamic behavior documented (no state machines, sequence diagrams)

### SWE.3 Pitfalls
- Detailed design only in code comments — not a separate controlled document
- No traceability from code unit to design document
- Algorithm not described; only implementation shown

### SWE.4 Pitfalls
- Test specification written after testing (not before execution)
- Coverage measured but below target with no deviation justification
- Test cases for MC/DC not explicitly designed — only claimed achieved
- No review record for test specification

### Generic Practice Pitfalls
- Process plan exists but not followed (plan stale, status reports missing)
- Reviews performed but not documented (no review record, no sign-off)
- Configuration management tool used but no baselines defined
- Project plan not updated after scope or schedule changes

---

## Process Performance Metrics (Level 2/3 Evidence)

| Metric | Purpose | Collection | Target |
|--------|---------|------------|--------|
| Requirements stability | Track change rate | Count changes per baseline | < 10% change after freeze |
| Defect density | Code quality indicator | Defects / KLOC | < 5 defects/KLOC |
| Review efficiency | Review effectiveness | Defects in review / total defects | > 60% found in review |
| Test coverage | Verification completeness | Coverage tool output | Per ASIL table above |
| Schedule variance | Project control | Actual vs planned % | +/- 10% |
| Effort variance | Estimation accuracy | Actual vs estimated hours | +/- 15% |
