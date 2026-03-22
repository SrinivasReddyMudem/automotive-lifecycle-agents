# Safety Goal Format — ISO 26262

## Required elements in every safety goal

A well-formed safety goal must include all of these:
1. The item or system being constrained
2. The malfunctioning behavior being prevented
3. The operating condition or scope (if not universal)
4. A measurable or verifiable criterion where possible
5. The ASIL level assigned to the goal
6. The safe state that must be reached or maintained

## Format template

"The [item/system] shall [not / ensure] [behavior] [condition/scope]."
Assigned ASIL: [ASIL A/B/C/D]
Safe state: [description of the safe state]

## Three worked examples

---

### Example 1 — Electric Power Steering (ASIL D)

**Safety Goal SG-EPS-001:**
"The Electric Power Steering system shall not apply steering torque
in a direction opposing the driver's intent in any operational situation."

- Assigned ASIL: D
- Safe state: Remove steering assist; driver retains full manual steering
- Justification: Unintended steering torque against driver at highway speed
  is S3/E4/C3 because driver cannot overcome motor torque at speed

**Why this is well-formed:**
- Names the item (Electric Power Steering system)
- States what is prevented (torque opposing driver intent)
- Scope is clear (any operational situation)
- Safe state is defined (remove assist, manual fallback remains)
- Technology-independent (does not say "use torque sensor")

---

### Example 2 — Battery Management System (ASIL C)

**Safety Goal SG-BMS-001:**
"The Battery Management System shall prevent battery cell voltage
from exceeding maximum cell voltage limits during any charging operation."

- Assigned ASIL: C
- Safe state: Terminate charging; disconnect battery from charger
- Justification: Overvoltage causes thermal runaway risk; S2/E3/C2
  because charging is a regular operation and driver may not notice warning

**Why this is well-formed:**
- Names the item (Battery Management System)
- Defines the constraint precisely (maximum cell voltage limits)
- Condition scoped (during any charging operation)
- Safe state is actionable (terminate charging, disconnect)
- Does not reference implementation technology

---

### Example 3 — Electronic Throttle Control (ASIL D)

**Safety Goal SG-ETC-001:**
"The Electronic Throttle Control system shall not command engine
torque exceeding the driver's requested torque by more than [X]%
during normal driving operations."

- Assigned ASIL: D
- Safe state: Reduce engine torque to idle; alert driver
- Justification: Unintended acceleration S3/E4/C3 for vehicles
  above 60 km/h where driver cannot override engine torque quickly

**Why this is well-formed:**
- Item named (Electronic Throttle Control system)
- Quantifiable criterion ([X]% tolerance — specific value from system eng)
- Scope defined (normal driving operations)
- Safe state defined (idle, driver alert)
- No implementation detail mentioned

---

## Common mistakes to avoid

| Mistake                                | Problem                                | Correction                                |
|----------------------------------------|----------------------------------------|-------------------------------------------|
| "The CRC check shall detect errors"    | Technology-specific                    | "The system shall detect data corruption" |
| "The ECU shall not crash"              | Vague, not verifiable                  | Define specific failure mode              |
| No safe state defined                  | Safety case cannot be closed           | Always define safe state                  |
| ASIL assigned to the hazard not goal  | Incorrect allocation                   | ASIL belongs to the safety goal           |
| "Should" instead of "shall"            | Weaker normative strength              | Always use "shall" for safety goals       |
