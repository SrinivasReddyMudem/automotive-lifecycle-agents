# HARA Template — Brake-by-Wire Example (Synthetic Data)

This is a fully worked example using synthetic data only.
It demonstrates the required HARA output format.

---

## 1. Item Definition

**Item name:** Brake-by-Wire (BbW) System
**Item description:** The BbW system replaces the hydraulic brake circuit
with electronic actuation. The driver's brake pedal input is sensed by
a pedal travel sensor, processed by the BbW ECU, and the deceleration
demand is sent via CAN to electromechanical actuators on each wheel.
**Item boundary:** Pedal sensor (input) → BbW ECU → CAN → wheel actuators (output).
Excludes: ABS/ESC function (separate item), park brake (separate item).
**Key functions:**
- F1: Convert pedal travel to deceleration demand
- F2: Distribute braking force across four wheels
- F3: Apply emergency braking on loss of control signal
- F4: Detect and manage actuator failures

---

## 2. Operational Situations

| OS-ID | Description                            | Estimated Exposure |
|-------|----------------------------------------|--------------------|
| OS-1  | Normal city driving, speed 0–50 km/h  | E4 (daily)         |
| OS-2  | Highway driving, speed 80–130 km/h    | E4 (daily)         |
| OS-3  | Emergency braking from high speed      | E2 (rare event)    |
| OS-4  | Low-speed manoeuvring in parking lot   | E4 (frequent)      |

---

## 3. Hazardous Events and ASIL Determination

### HE-001: No braking response when driver presses brake pedal

**Malfunctioning behavior:** BbW ECU fails to generate deceleration demand
**Operational situation:** OS-2 (highway driving 80–130 km/h)

| Parameter       | Rating | Justification                                                           |
|-----------------|--------|-------------------------------------------------------------------------|
| Severity        | S3     | Collision with preceding vehicle at high speed likely fatal             |
| Exposure        | E4     | Highway driving is a daily operational situation for most drivers       |
| Controllability | C3     | Driver has no redundant braking; cannot control the vehicle effectively |

**ASIL Result: ASIL D**

**Safety Goal SG-001:**
"The BbW system shall not fail to provide braking deceleration when
the driver commands braking, in all operational situations."
ASIL D | Safe state: controlled deceleration to standstill

---

### HE-002: Unintended braking during normal forward driving

**Malfunctioning behavior:** BbW ECU applies brakes without driver input
**Operational situation:** OS-2 (highway driving 80–130 km/h)

| Parameter       | Rating | Justification                                                               |
|-----------------|--------|-----------------------------------------------------------------------------|
| Severity        | S3     | Rear-end collision from following vehicle at highway speed is potentially fatal |
| Exposure        | E4     | Failure can occur during any driving phase on highway                       |
| Controllability | C2     | Driver can react by steering around, but only if warning is timely          |

**ASIL Result: ASIL C**

**Safety Goal SG-002:**
"The BbW system shall not apply braking force greater than 0.1 g
without a valid driver pedal demand in any operational situation."
ASIL C | Safe state: release all braking, alert driver

---

### HE-003: Asymmetric braking causing vehicle yaw

**Malfunctioning behavior:** Left wheels apply 100% braking, right wheels 0%
**Operational situation:** OS-2 (highway driving 80–130 km/h)

| Parameter       | Rating | Justification                                                              |
|-----------------|--------|----------------------------------------------------------------------------|
| Severity        | S3     | Vehicle yaw at highway speed can cause loss of control and fatal collision |
| Exposure        | E4     | Failure can occur during any braking event on highway                      |
| Controllability | C3     | Sudden yaw at high speed is uncontrollable for most drivers                |

**ASIL Result: ASIL D**

**Safety Goal SG-003:**
"The BbW system shall distribute braking force symmetrically between
left and right sides within a tolerance of ±15% at all times."
ASIL D | Safe state: equal distribution or no braking

---

## 4. Safety Goal Summary

| SG-ID  | Safety Goal Description                          | ASIL   | Safe State                              |
|--------|--------------------------------------------------|--------|-----------------------------------------|
| SG-001 | Shall not fail to provide braking on command     | ASIL D | Controlled decel to standstill          |
| SG-002 | Shall not apply braking without driver demand    | ASIL C | Release braking, alert driver           |
| SG-003 | Shall distribute braking force symmetrically     | ASIL D | Equal distribution or no braking        |

---

## 5. Review Note

This analysis requires review and approval by a qualified functional
safety engineer before use in any project. All data in this example
is synthetic and for demonstration purposes only.
