# ISO 26262-3 Table 4 — Complete ASIL Determination Table

All 64 S x E x C combinations. This table is the authoritative lookup
used by the asil_calculator.py tool and the iso26262-hara skill.

S0 (no injuries): all combinations map to QM — excluded from table below.

## Complete Table — S1 through S3

| Severity | Exposure | Controllability | ASIL Result |
|----------|----------|-----------------|-------------|
| S1       | E1       | C1              | QM          |
| S1       | E1       | C2              | QM          |
| S1       | E1       | C3              | QM          |
| S1       | E2       | C1              | QM          |
| S1       | E2       | C2              | QM          |
| S1       | E2       | C3              | QM          |
| S1       | E3       | C1              | QM          |
| S1       | E3       | C2              | QM          |
| S1       | E3       | C3              | ASIL A      |
| S1       | E4       | C1              | QM          |
| S1       | E4       | C2              | ASIL A      |
| S1       | E4       | C3              | ASIL B      |
| S2       | E1       | C1              | QM          |
| S2       | E1       | C2              | QM          |
| S2       | E1       | C3              | QM          |
| S2       | E2       | C1              | QM          |
| S2       | E2       | C2              | QM          |
| S2       | E2       | C3              | ASIL A      |
| S2       | E3       | C1              | QM          |
| S2       | E3       | C2              | ASIL A      |
| S2       | E3       | C3              | ASIL B      |
| S2       | E4       | C1              | ASIL A      |
| S2       | E4       | C2              | ASIL B      |
| S2       | E4       | C3              | ASIL C      |
| S3       | E1       | C1              | QM          |
| S3       | E1       | C2              | QM          |
| S3       | E1       | C3              | ASIL A      |
| S3       | E2       | C1              | QM          |
| S3       | E2       | C2              | ASIL A      |
| S3       | E2       | C3              | ASIL B      |
| S3       | E3       | C1              | ASIL A      |
| S3       | E3       | C2              | ASIL B      |
| S3       | E3       | C3              | ASIL C      |
| S3       | E4       | C1              | ASIL B      |
| S3       | E4       | C2              | ASIL C      |
| S3       | E4       | C3              | ASIL D      |

## Summary: When ASIL D occurs

ASIL D results only from S3/E4/C3:
- Severity S3: fatal or survival uncertain
- Exposure E4: high probability (most driving situations)
- Controllability C3: difficult or uncontrollable

Example: Loss of electric power steering on a highway
at 120 km/h — driver cannot maintain lane without
steering assist → S3 / E4 / C3 → ASIL D.

## ASIL decomposition reference

ASIL D can decompose to:
- ASIL D(D) = ASIL B(D) + ASIL B(D)
- ASIL D(D) = ASIL C(D) + ASIL A(D)
- ASIL D(D) = ASIL D + QM (not recommended, rarely used)

Parentheses notation: ASIL X(Y) means a component
with ASIL X derived by decomposition from ASIL Y.

## Rating guidance notes

**Severity S3 examples:**
- Loss of braking at highway speed
- Unintended steering toward oncoming traffic
- Airbag non-deployment in high-speed crash
- Unintended acceleration in traffic

**Exposure E4 examples:**
- Normal driving on public roads
- Any function active during regular commuting
- Vehicle speed above 0 km/h

**Exposure E1 examples:**
- Driving in a tunnel (rare for most drivers)
- Driving on a track day (very rare)

**Controllability C3 examples:**
- Sudden loss of braking with no warning
- Sudden full-lock steering deflection
- Sudden unintended acceleration above 50 km/h
