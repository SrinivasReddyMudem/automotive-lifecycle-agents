# MISRA C:2012 Deviation Request Template

Use this template whenever a required or mandatory MISRA rule cannot be
satisfied. Advisory rule deviations do not require formal documentation
but should be noted in code review.

---

## MISRA Deviation Request

**Deviation ID:** DEV-MISRA-[PROJECT]-[NNN]
**Date:** [YYYY-MM-DD]
**Author:** [Name / Role]
**Reviewer:** [Name / Role]
**Approver (Safety Engineer):** [Name / Role]

---

### 1. Identification

| Field                  | Value                                           |
|------------------------|-------------------------------------------------|
| MISRA C:2012 Rule      | Rule [X.Y] — [rule short title]                |
| Rule Category          | [Mandatory / Required / Advisory]               |
| Source File            | [filename.c]                                   |
| Line Number(s)         | [line range]                                   |
| Static Analysis Tool   | [Polyspace / QAC / PC-lint / Coverity]         |
| Tool Finding ID        | [tool-specific finding reference]              |
| ASIL Level             | [QM / ASIL-A / ASIL-B / ASIL-C / ASIL-D]      |

---

### 2. Violation Description

**Code excerpt (synthetic pattern):**
```c
/* Describe the pattern that triggers the rule violation */
/* Use synthetic / anonymised code — no real IP here    */
```

**Explanation of violation:**
[Describe precisely why this code triggers the named rule.]

---

### 3. Justification

**Reason compliance is not achievable or appropriate:**
[Explain the technical or architectural constraint that prevents compliance.
Examples: legacy interface requires void* pass-through; hardware register
layout requires pointer cast; third-party library API is fixed.]

**Alternatives considered and rejected:**
1. [Alternative 1] — rejected because [reason]
2. [Alternative 2] — rejected because [reason]

---

### 4. Risk Assessment

**Potential risk introduced by the deviation:**
[Describe the specific risk. Be honest — if the risk is low, say why.]

**Risk level:** [Low / Medium / High]

**Risk mitigation measures:**
- [Mitigation 1 — e.g., encapsulated in a single function with comment]
- [Mitigation 2 — e.g., reviewed by safety engineer at each release]
- [Mitigation 3 — e.g., covered by unit test checking boundary conditions]

**Impact on safety goal [SG-ID if applicable]:**
[State explicitly whether this deviation could affect a safety goal,
and if so, what additional measures are in place.]

---

### 5. Review and Approval

| Role                   | Name         | Signature | Date       |
|------------------------|--------------|-----------|------------|
| Software Developer     |              |           |            |
| Software Lead          |              |           |            |
| Functional Safety Eng. |              |           |            |
| Quality Assurance      |              |           |            |

---

### 6. Deviation Register Entry

This deviation must be entered in the project deviation register with:
- Deviation ID (from this document)
- Rule ID
- File and line reference
- ASIL level
- Risk level
- Approval date and approver name

---

## Example Completed Deviation (Synthetic)

**Deviation ID:** DEV-MISRA-PROJ-A-007
**MISRA Rule:** 11.5 — Advisory
**File:** nvm_access.c, line 42
**ASIL:** ASIL B

**Violation:** `NvM_ReadBlock()` returns a `void *` pointer to the block
data buffer. The code casts this to `uint8_t *` for byte-level access.

**Justification:** The NvM module API is defined by AUTOSAR R4.x specification.
The `void *` return type is normative. Changing the NvM API is not possible
without violating AUTOSAR conformance.

**Risk:** Low. The target buffer is always a `uint8_t` array of fixed size.
The cast is encapsulated in a single wrapper function `Nvm_ReadByteBuffer()`.

**Mitigation:** The wrapper is unit tested with boundary value inputs.
A static comment above the cast references this deviation ID.

**Approved by:** Safety Engineer — [date]
