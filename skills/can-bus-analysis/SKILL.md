---
name: can-bus-analysis
description: |
  Load automatically when any of these appear:
  CAN, CAN-FD, bus-off, error frame, error
  counter, TEC, REC, transmit error counter,
  receive error counter, passive error state,
  warning limit, active error state, dominant,
  recessive, bit stuffing, arbitration, CAN ID,
  extended ID, DBC file, database, signal,
  message, LIN, FlexRay, SOME/IP, automotive
  Ethernet, missing ACK, babbling idiot,
  bus load, CAN statistics, candump, Vector
  CANalyzer, CANoe, PCAN, Peak, bit timing,
  baudrate, sample point, CAN trace, CAN log,
  network management, NM, CanNm, CAN matrix,
  oscilloscope, bit error, form error, CRC error,
  acknowledgement error, stuffing error, error
  passive, error active, error warning, bus
  termination, short circuit, open circuit,
  differential voltage, recessive bus idle,
  CAN high, CAN low, twisted pair, 120 ohm.
---

## CAN frame structure

```
SOF | Arbitration (11 or 29 bit ID) | RTR | Control (DLC) |
Data (0–8 bytes) | CRC (15 bit) | ACK | EOF | IFS
```

CAN-FD adds: BRS (bit rate switch) and ESI bit; data up to 64 bytes.

---

## Error types and counters

| Error Type    | What triggers it                         | Which node detects it     |
|---------------|------------------------------------------|---------------------------|
| Bit error     | Node transmits and samples wrong bit     | Transmitting node         |
| Stuff error   | 6+ consecutive bits of same polarity     | Any node monitoring       |
| CRC error     | CRC calculated ≠ CRC received            | Receiving node            |
| Form error    | Fixed-form field has wrong format        | Any node monitoring       |
| ACK error     | No dominant bit during ACK slot          | Transmitting node only    |

**Error counter rules:**
- TEC (Transmit Error Counter) increments +8 on transmit error
- TEC decrements -1 on successful transmission
- REC (Receive Error Counter) increments +1 on receive error
- REC decrements -1 on successful reception

**Error state transitions:**
- Active (TEC/REC < 96): sends active error frames
- Warning (TEC/REC ≥ 96): node still active but flagged
- Passive (TEC/REC ≥ 128): sends passive error frames (recessive)
- Bus-off (TEC ≥ 256): node stops all transmission

---

## Bus-off recovery

Node enters bus-off: ceases all transmission.

**Auto-recovery (if configured):**
128 × 11 recessive bits must be observed on the bus.
This takes approximately 1.1 ms at 1 Mbit/s.
After recovery, TEC and REC reset to 0.

**Manual recovery:**
Requires ECU reset or explicit software re-enable.
Configuration determines which mode is used.
AUTOSAR CanSM controls bus-off handling for BSW stack.

---

## Common fault patterns

[reference: references/fault-patterns.md]

Symptom → probable cause → debug steps table.
Covers: bus-off, missing ACK, high error rate,
signal out of range, node not responding.

## All error types with root cause

[reference: references/error-types.md]

All 5 error types with detection mechanism and TEC/REC impact.
