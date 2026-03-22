# ISO 26262 Hardware Metrics and Software Requirements

## Hardware Metrics Target Values (ISO 26262-5)

### Single Point Fault Metric (SPFM)

| ASIL | Target |
|------|--------|
| QM   | N/A    |
| A    | >= 90% |
| B    | >= 90% |
| C    | >= 97% |
| D    | >= 99% |

**Formula**: SPFM = 1 - (Sum of lambda_SPF / Sum of lambda)

Where lambda_SPF = failure rate of single-point faults (no safety mechanism covers them).

### Latent Fault Metric (LFM)

| ASIL | Target |
|------|--------|
| QM   | N/A    |
| A    | >= 60% |
| B    | >= 60% |
| C    | >= 80% |
| D    | >= 90% |

**Formula**: LFM = 1 - (Sum of lambda_latent / Sum of lambda_multi-point)

### Probabilistic Metric for Hardware Failures (PMHF)

| ASIL | Target (per hour) | Target (FIT) |
|------|-------------------|--------------|
| QM   | N/A               | N/A          |
| A    | < 10^-7           | < 100        |
| B    | < 10^-7           | < 100        |
| C    | < 10^-8           | < 10         |
| D    | < 10^-8           | < 10         |

FIT = Failures In Time (failures per 10^9 hours)

---

## Code Coverage Requirements (ISO 26262-6 Table 13)

| ASIL | Statement | Branch | MC/DC |
|------|-----------|--------|-------|
| A    | ++        | +      | o     |
| B    | ++        | ++     | o     |
| C    | ++        | ++     | +     |
| D    | ++        | ++     | ++    |

Legend:
- ++ Highly recommended
- + Recommended
- o For consideration

**MC/DC**: Modified Condition/Decision Coverage — every condition in a decision
independently affects the outcome. Required at ASIL D.

---

## Software Development Methods by ASIL (ISO 26262-6)

### Coding Guidelines per ASIL

| ASIL | Requirements |
|------|--------------|
| A    | MISRA C compliance |
| B    | MISRA C compliance |
| C    | MISRA C + static analysis |
| D    | MISRA C + static analysis + defensive programming + walkthrough |

### Software Architecture Methods (ISO 26262-6 Table 5)

| Method | ASIL A | ASIL B | ASIL C | ASIL D |
|--------|--------|--------|--------|--------|
| Hierarchical structure | ++ | ++ | ++ | ++ |
| Restricted size and complexity | + | ++ | ++ | ++ |
| Low coupling between components | + | + | ++ | ++ |
| Appropriate scheduling sequence | + | ++ | ++ | ++ |
| Information hiding/encapsulation | + | + | ++ | ++ |
| Defensive programming | + | ++ | ++ | ++ |

### Review Requirements by ASIL

| ASIL | Design Review | Code Review | Independence |
|------|--------------|-------------|--------------|
| A    | Peer         | Peer        | Not required |
| B    | Peer         | Peer        | Not required |
| C    | Independent  | Independent | Required     |
| D    | Independent + walkthrough | Independent + walkthrough | Required |

---

## Safety Mechanism Catalog

### Detection Mechanisms

| Mechanism | Purpose | Typical Diagnostic Coverage |
|-----------|---------|------------------------------|
| Range check | Detect sensor out-of-range values | 60-90% |
| Plausibility check | Cross-check redundant sensors | 70-95% |
| Watchdog (windowed) | Detect SW hang or incorrect timing | 90-99% |
| CRC / Checksum | Detect data corruption in memory or comm | 90-99.9% |
| Dual-channel comparison | Detect computation error | 90-99% |
| RAM test (march test) | Detect RAM cell faults | 80-95% |
| Flash CRC | Detect code memory corruption | 95-99% |
| Alive counter | Detect stale data from sender | 95% |
| End-to-end protection (E2E) | Detect comm errors (AUTOSAR E2E) | 99.9% |

### Control Mechanisms

| Mechanism | Purpose | Implementation |
|-----------|---------|----------------|
| Voting (2oo3) | Mask single failure | 3 sensors, select median |
| Hot standby | Fail-operational | Redundant ECU with switchover |
| Watchdog + reset | Recover from transient fault | External watchdog triggers reset |
| Graceful degradation | Maintain partial function | Limp-home mode |
| Safe state transition | Prevent hazard on failure | Controlled shutdown |

### Mitigation Mechanisms

| Mechanism | Purpose | Example |
|-----------|---------|---------|
| Torque limitation | Limit acceleration on sensor fault | Cap throttle to 30% on fault |
| Speed limitation | Reduce risk in degraded mode | Limit to 50 km/h degraded |
| Driver warning | Increase controllability | Visual/audible alert on fault |
| Driver intervention request | Transfer control to driver | "Take over immediately" |
| Emergency stop | Ultimate safe state | Controlled deceleration to standstill |

---

## Diagnostic Coverage Estimation

### Fault Injection Formula

```
DC = (N_detected / N_injected) x 100%

where:
N_detected = Faults detected by safety mechanism
N_injected = Total faults injected
```

### Combined Coverage (Multiple Mechanisms)

```
DC_total = 1 - product(1 - DC_i)

Example:
DC_watchdog = 0.95
DC_range_check = 0.80
DC_total = 1 - (1 - 0.95) x (1 - 0.80) = 1 - 0.01 = 0.99 = 99%
```

---

## Common Safety Goals by System

### Powertrain

| System | Safety Goal | Typical ASIL |
|--------|-------------|--------------|
| Engine control | Prevent unintended acceleration | D |
| Engine control | Prevent unintended engine off on highway | C |
| Transmission | Prevent unintended gear shift | C |
| Cruise control | Prevent unintended activation | B |

### Chassis

| System | Safety Goal | Typical ASIL |
|--------|-------------|--------------|
| ESC | Maintain stability control availability | D |
| ABS | Maintain braking capability | D |
| EPS | Maintain steering assistance | D |
| Brake-by-wire | Prevent unintended braking | D |
| Brake-by-wire | Shall not fail to provide braking on demand | D |

### ADAS

| System | Safety Goal | Typical ASIL |
|--------|-------------|--------------|
| AEB | Prevent collision or mitigate severity | D |
| LKA | Prevent unintended lane departure | C |
| ACC | Prevent unsafe acceleration or deceleration | C |
| Parking assist | Prevent collision during low-speed parking | B |

---

## Hardware Development Requirements by ASIL

| ASIL | Analysis | Review | Metrics | Validation |
|------|----------|--------|---------|------------|
| A    | FMEA | Peer | SPFM >= 90%, LFM >= 60% | Functional test |
| B    | FMEA + FTA | Peer | SPFM >= 90%, LFM >= 60% | Functional + stress test |
| C    | FMEA + FTA | Independent | SPFM >= 97%, LFM >= 80% | + Fault injection |
| D    | FMEA + FTA + DFA | Independent | SPFM >= 99%, LFM >= 90% | + Long-term validation |

DFA = Dependent Failure Analysis (required for ASIL decomposition)

---

## ASIL Decomposition Reference (Complete)

### Valid Decomposition Schemes

| Parent ASIL | Decomposition Options |
|-------------|----------------------|
| D | D = B(D) + B(D) |
| D | D = C(D) + A(D) |
| C | C = B(C) + A(C) |
| C | C = A(C) + A(C) |
| B | B = A(B) + A(B) |
| A | Cannot be decomposed |

**Notation**: B(D) means "ASIL B component developed to achieve ASIL D system requirement"

### Independence Requirements for Decomposition

- Sufficiently independent development processes (design, verification, validation)
- No cascading failures between decomposed elements
- No common cause failures
- Dependent Failure Analysis (DFA) required per ISO 26262-9

---

*This requires review and approval by a qualified engineer before use in any project.*
