# ISO 21434 — CAL Assignment Table

## Impact × Attack Feasibility → CAL

Cybersecurity Assurance Level (CAL) is assigned based on the
combination of impact severity and attack feasibility.
Higher impact or easier attacks result in higher CAL.

| Impact \ Feasibility | AF1 (Very Low) | AF2 (Low) | AF3 (Medium) | AF4 (High) |
|----------------------|----------------|-----------|--------------|------------|
| I1 (Negligible)      | CAL 1          | CAL 1     | CAL 1        | CAL 1      |
| I2 (Moderate)        | CAL 1          | CAL 1     | CAL 2        | CAL 2      |
| I3 (Major)           | CAL 1          | CAL 2     | CAL 3        | CAL 3      |
| I4 (Severe)          | CAL 2          | CAL 3     | CAL 3        | CAL 4      |

---

## CAL requirements summary

**CAL 1 — Low assurance requirement**
- Basic security measures required
- Cybersecurity plan with basic controls
- Validation: informal review

**CAL 2 — Medium-low assurance requirement**
- Structured threat mitigation
- Security testing required
- Validation: structured review + testing

**CAL 3 — Medium-high assurance requirement**
- Rigorous security design and testing
- Penetration testing recommended
- Validation: security expert review + pen test

**CAL 4 — Highest assurance requirement**
- Full security lifecycle controls
- Mandatory penetration testing
- Formal security case required
- Validation: independent security assessment

---

## When CAL 4 applies

CAL 4 = I4 impact with AF4 (high) feasibility.
Examples of CAL 4 scenarios:
- Remote code execution on safety-critical ECU via telematics
- OTA update system compromise allowing any firmware deployment
- Steering or braking control accessible via external network attack
- Key extraction from immobiliser allowing vehicle theft at scale

---

## Relationship to ISO 26262 ASIL

CAL and ASIL are separate and parallel:
- ASIL addresses random hardware failures and SW systematic faults
- CAL addresses intentional adversarial attacks
- An item can have both ASIL D and CAL 4 requirements simultaneously
- Security controls required by CAL shall not compromise safety mechanisms

When safety and cybersecurity interact (e.g., OTA update to safety-critical ECU),
co-engineering between safety and cybersecurity teams is required.
