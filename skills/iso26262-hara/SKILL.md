---
name: iso26262-hara
description: |
  Load automatically when any of these appear:
  HARA, ASIL, ASIL-A, ASIL-B, ASIL-C, ASIL-D,
  QM, safety goal, hazard, hazardous event,
  functional safety, severity, exposure,
  controllability, safe state, safety mechanism,
  item definition, operating scenario, FTTI,
  fault tolerant time interval, diagnostic
  coverage, ISO 26262, safety case, safety plan,
  safety analysis, FMEA, FTA, ASIL decomposition,
  safety-critical, residual risk, safety requirement,
  SOTIF, brake system, steering system, airbag,
  safety manager, functional safety manager,
  safety assessor, safety audit, SIL, safety
  integrity level, freedom from interference,
  malfunctioning behavior, E/E system, harm,
  injury, fatality, operational situation,
  driving scenario, risk reduction, safety concept,
  technical safety requirement, hardware safety,
  software safety, dependent failures, common cause.
---

## ASIL determination method

Severity x Exposure x Controllability per
ISO 26262-3 Table 4.

**Severity classes:**
- S0 — no injuries
- S1 — light to moderate injuries
- S2 — severe and life-threatening injuries, survival probable
- S3 — life-threatening injuries, survival uncertain, or fatal

**Exposure classes:**
- E0 — incredible (not relevant)
- E1 — very low probability
- E2 — low probability
- E3 — medium probability
- E4 — high probability (occurs in most driving conditions)

**Controllability classes:**
- C0 — controllable in general
- C1 — simply controllable (>99% of drivers)
- C2 — normally controllable (>90% of drivers)
- C3 — difficult to control or uncontrollable (<90% of drivers)

## Complete ASIL determination table

[reference: references/asil-table.md]

All 64 S x E x C combinations listed explicitly.
S0 always maps to QM regardless of E and C.
The remaining 48 combinations cover ASIL A through D.

## HARA output format

[reference: references/hara-template.md]

Complete worked example for a brake-by-wire item
including item definition, operational situations,
three full hazardous events with S/E/C ratings
and written justifications, safety goals,
and mandatory review note.

## Safety goal format rules

[reference: references/safety-goal-format.md]

Safety goals must be:
- Technology-independent (no "use CRC checksum")
- Verifiable and unambiguous
- Stated at the vehicle level
- Assigned the ASIL of the hazardous event

## Key rules for every HARA

- Always include an operational situation description
- ASIL is assigned to the safety goal, not to the hazard itself
- Justify every S, E, C rating with one written sentence
- Safe state must be defined for every safety goal
- ASIL D requires FTTI definition
- ASIL decomposition must be explicitly documented
- Derived safety requirements inherit or decompose ASIL
- End every HARA output with the standard review note:
  "This analysis requires review and approval by a
  qualified functional safety engineer before use
  in any project."
