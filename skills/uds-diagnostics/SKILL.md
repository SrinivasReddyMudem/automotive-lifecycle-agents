---
name: uds-diagnostics
description: |
  Load automatically when any of these appear:
  UDS, DTC, diagnostic trouble code, fault code,
  tester present, ECU reset, read data by
  identifier, write data by identifier, security
  access, seed key, routine control, flash
  programming, software download, ISO 14229,
  OBD-II, SAE J1979, PID, negative response,
  NRC, DoIP, ISO 13400, KWP2000, diagnostic
  session, extended session, programming session,
  default session, service 0x10, service 0x11,
  service 0x14, service 0x19, service 0x22,
  service 0x27, service 0x2E, service 0x31,
  service 0x34, service 0x36, service 0x37,
  service 0x3E, DTC status byte, freeze frame,
  snapshot, response on event, P2 timeout,
  communication control, input output control,
  ECU not responding, negative response code,
  requestOutOfRange, conditionsNotCorrect,
  securityAccessDenied, requestSequenceError,
  transferDataSuspended, requestTooLong.
---

## Session types

| Session ID | Name               | Typical use                                     |
|------------|--------------------|-------------------------------------------------|
| 0x01       | Default Session    | Normal operation — standard OBD and status reads|
| 0x02       | Programming Session| Flash programming — software update procedures  |
| 0x03       | Extended Session   | Advanced diagnostics — parameter write access   |

Session transitions must follow defined paths.
Most services are not available in default session.

---

## DTC format (ISO 14229)

3-byte DTC:
- Byte 1: System identifier (P=powertrain, B=body, C=chassis, U=network)
- Byte 2: Fault type (mid byte)
- Byte 3: Fault detail (LSB)

DTC status byte — 8 bits:
| Bit | Name                          | Meaning                        |
|-----|-------------------------------|--------------------------------|
| 0   | testFailed                    | Current test result            |
| 1   | testFailedThisMonitoringCycle | Failed in this cycle           |
| 2   | pendingDTC                    | Detected but not confirmed     |
| 3   | confirmedDTC                  | Confirmed fault present        |
| 4   | testNotCompletedSinceLastClear| Test not run since clear       |
| 5   | testFailedSinceLastClear      | Failed since last clear        |
| 6   | testNotCompletedThisCycle     | Test not completed this cycle  |
| 7   | warningIndicatorRequested     | MIL or warning light requested |

---

## Common UDS services

[reference: references/service-ids.md]

All services 0x10 through 0x3E with request format,
positive response, and FAE debug tips.

## Negative response codes

[reference: references/nrc-codes.md]

All NRC codes 0x10 through 0x78 with meaning and
most common root cause in automotive ECUs.

---

## Key diagnostic rules

- TesterPresent (0x3E) must be sent every ~2 seconds to keep
  extended or programming session alive
- Security access (0x27) requires seed-key exchange before
  write operations in extended or programming session
- ClearDTC (0x14) removes all DTCs in current DTC group
- Flash programming sequence: 0x10(02) → 0x27 → 0x34 → 0x36 → 0x37 → 0x11
- P2 timeout (default 50ms): server must respond within this time
- P2* timeout (default 5000ms): extended response time server can request
