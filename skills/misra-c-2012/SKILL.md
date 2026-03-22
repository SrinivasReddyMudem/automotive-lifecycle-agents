---
name: misra-c-2012
description: |
  Load automatically when any of these appear:
  MISRA, MISRA C, MISRA C++, rule violation,
  coding standard, static analysis, deviation,
  deviation request, deviation justification,
  compliant rewrite, MISRA compliant, pointer
  arithmetic, cast, implicit conversion, goto,
  recursion, dynamic memory, malloc, free,
  heap, union, bitfield, undefined behaviour,
  MISRA rule, safety coding, code review,
  Polyspace, QAC, PC-lint, Coverity, MISRA
  checker, rule 15, rule 17, rule 18, rule 11,
  rule 14, MISRA violation, mandatory rule,
  required rule, advisory rule, C90, C99,
  AUTOSAR MISRA, ASIL coding requirement,
  static analysis finding, dead code, unreachable,
  return value ignored, array bounds, type mismatch,
  implicit cast, essential type, side effect,
  operator precedence, composite expression,
  memory allocation, function pointer, void pointer.
---

## The 15 most violated MISRA C:2012 rules
in automotive embedded development

[reference: references/top-rules.md — full detail with code examples]

Quick reference:

| Rule   | Category  | Summary                                                    |
|--------|-----------|------------------------------------------------------------|
| 1.3    | Required  | No undefined or critical unspecified behaviour             |
| 2.2    | Required  | No dead code                                               |
| 8.4    | Required  | Compatible declaration for function with external linkage  |
| 10.1   | Required  | Operands shall not be inappropriate essential type         |
| 10.3   | Required  | Value shall not be assigned to variable of different type  |
| 11.3   | Required  | No cast between pointer to object types                    |
| 11.5   | Advisory  | No cast from void pointer to object pointer                |
| 12.1   | Advisory  | Precedence of operators shall not be relied upon           |
| 13.5   | Required  | No persistent side effects on right side of && or \|\|     |
| 14.4   | Required  | Controlling expression of if/while shall be Boolean        |
| 15.5   | Advisory  | Function shall have single point of exit                   |
| 17.7   | Required  | Return value of non-void function shall be used            |
| 18.6   | Required  | Address of auto storage shall not outlive the object       |
| 18.8   | Required  | No variable length array types                             |
| 21.3   | Required  | Memory allocation functions not used                       |

## Rule categories

- **Mandatory** — must never be violated; no deviation permitted
- **Required** — must comply; deviation requires formal justification
- **Advisory** — should comply; violation noted but not blocking

## MISRA and ASIL

For ASIL C and D, all mandatory and required rules must be satisfied.
For ASIL A and B, mandatory rules must be satisfied and required rules
should be satisfied. Advisory rules should be reviewed regardless of ASIL.

## Deviation process

When a required rule cannot be satisfied:
1. Identify the rule ID and violation location
2. Document the technical reason compliance is not achievable
3. Perform risk assessment of the deviation
4. Obtain approval from safety engineer and software lead
5. Record in deviation register

[reference: references/deviation-template.md]
