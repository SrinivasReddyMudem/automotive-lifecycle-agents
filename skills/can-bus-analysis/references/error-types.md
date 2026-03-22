# CAN Error Types — Complete Reference

All 5 CAN error types with detection mechanism, TEC/REC impact, and root cause.

---

## 1. Bit Error

**Definition:** A transmitting node monitors the bus while transmitting.
If the bit it samples differs from the bit it transmitted, it detects a bit error.

**How detected:** Transmitting node compares transmitted bit to sampled bus level.
**Which node detects it:** The transmitting node only.
**Exception:** During arbitration or ACK field, no bit error is generated for recessive
bits being overwritten by dominant bits (this is normal arbitration / ACK behaviour).

**TEC/REC impact:** TEC +8 on the transmitting node.

**Typical root causes in automotive ECUs:**
- Bus termination fault: incorrect impedance causes reflections
- Short circuit on CAN_H or CAN_L to power or ground
- Open circuit breaks differential signalling
- EMC interference from adjacent harness
- CAN transceiver damage (often from reverse voltage or static)

---

## 2. Stuff Error

**Definition:** CAN uses bit stuffing: after 5 consecutive bits of the same polarity,
the transmitter inserts one bit of opposite polarity. A stuff error occurs when
a 6th consecutive bit of the same polarity is detected between SOF and CRC.

**How detected:** Any node monitoring the bus (CAN controller hardware).
**Which node detects it:** Any node — both transmitting and receiving nodes.

**TEC/REC impact:** TEC +8 transmitting node; REC +1 all other nodes.

**Typical root causes in automotive ECUs:**
- Oscillator frequency mismatch between nodes (bit timing mismatch)
- Noise injection corrupting the stuff bit
- Damaged or incompatible CAN controller silicon
- Bit timing configuration error (wrong sample point, wrong Tq count)
- Bus load so high that stuff bits accumulate and corrupt other frames

---

## 3. CRC Error

**Definition:** The receiver calculates a 15-bit CRC over the received frame.
If the calculated CRC differs from the CRC field in the frame, a CRC error is raised.

**How detected:** Receiving nodes compute CRC independently and compare.
**Which node detects it:** Receiving nodes (not the transmitting node).

**TEC/REC impact:** REC +1 on all receiving nodes that detect the mismatch.

**Typical root causes in automotive ECUs:**
- Single-bit noise during data transmission
- EMC interference on CAN bus harness
- CAN bus star topology without proper termination (signal reflection)
- Very long stubs on a CAN network (impedance mismatch)
- Faulty CAN transceiver with unstable output

---

## 4. Form Error

**Definition:** Certain fields in a CAN frame have a fixed format (always recessive
or always dominant). If a node receives a bit in these fields that has the wrong
polarity, a form error is detected. Affected fields: CRC delimiter, ACK delimiter, EOF.

**How detected:** Any node monitoring the bus.
**Which node detects it:** Any node — can be transmitting or receiving.

**TEC/REC impact:** TEC +8 transmitting node; REC +1 receiving nodes.

**Typical root causes in automotive ECUs:**
- Another node transmitting when it should be silent (babbling idiot)
- CAN controller in error passive state corrupting ACK delimiter
- Hardware fault causing a node to drive dominant in fixed-recessive fields
- Ground loop creating dominant-level offset on the bus

---

## 5. ACK Error

**Definition:** The transmitting node requires at least one receiver to send a
dominant bit in the ACK slot. If the ACK slot remains recessive after transmission,
the transmitting node detects an ACK error.

**How detected:** Only the transmitting node monitors the ACK slot for response.
**Which node detects it:** Transmitting node only.

**TEC/REC impact:** TEC +8 on the transmitting node.

**Typical root causes in automotive ECUs:**
- No other node is present on the bus (ECU powered alone on bench without terminator + load)
- All other nodes are in bus-off state
- Bus-off ECU is the only receiver of this specific message
- Missing bus termination resistors
- CAN baud rate mismatch: receivers not sampling the correct bits
- Physical bus disconnect (open circuit, unplugged connector)

---

## Error counter summary table

| Event                                 | TEC Change | REC Change |
|---------------------------------------|------------|------------|
| Transmit error detected               | +8         | 0          |
| Receive error detected                | 0          | +1         |
| Successful transmission               | -1         | 0          |
| Successful reception                  | 0          | -1 (min 0) |
| ACK error                             | +8         | 0          |
| Bit error in active error flag        | +8         | —          |
| Overload frame detected               | 0          | 0          |
