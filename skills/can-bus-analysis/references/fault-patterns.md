# CAN Bus Fault Patterns — Symptom to Cause Table

## 1. Bus-Off

**Symptom:** Node stops transmitting; DTC set; ECU not responding to diagnostic requests.

| Probability | Probable Cause                                       | Debug Step                                                  |
|-------------|------------------------------------------------------|-------------------------------------------------------------|
| High        | Physical layer short or open circuit                 | Check CAN_H/CAN_L voltage (should be ~2.5V differential)   |
| High        | Babbling idiot — another node drives bus constantly  | Disconnect nodes one at a time; observe when bus-off clears |
| Medium      | Baud rate mismatch with another node                 | Confirm baud rate config on all nodes                       |
| Medium      | EMC burst causing rapid error accumulation           | Check oscilloscope trace for noise bursts; check ground     |
| Low         | CAN transceiver hardware damage                      | Replace transceiver IC; check supply voltage                |

**Key check:** After bus-off, TEC resets to 0 on recovery.
If bus-off recurs immediately → physical problem, not software.

---

## 2. Missing ACK

**Symptom:** Transmitting ECU shows ACK errors; TEC climbs; frames not received by others.

| Probability | Probable Cause                                       | Debug Step                                                  |
|-------------|------------------------------------------------------|-------------------------------------------------------------|
| High        | No other node present on bus                         | Check if at least one other node is powered and connected   |
| High        | Baud rate mismatch — receivers not sampling frame    | Verify baud rate matches across all nodes                   |
| High        | Missing termination resistor (open bus)              | Measure bus with oscilloscope: wave should be clean square  |
| Medium      | All other nodes are in bus-off state                 | Check TEC/REC via diagnostics on all nodes                  |
| Low         | Very long cable stub causing late sampling           | Check network topology; stubs > 30cm on 500kbit/s are risky |

**Key check:** ACK error only seen on bench (single ECU) is expected — not a bug.

---

## 3. High Error Rate (Intermittent Errors)

**Symptom:** Error frames visible in trace; TEC/REC fluctuating but not reaching bus-off;
occasional message retransmissions.

| Probability | Probable Cause                                       | Debug Step                                                  |
|-------------|------------------------------------------------------|-------------------------------------------------------------|
| High        | Electrical noise from ignition, inverter, or motor   | Check error timing vs ignition events; add shielding        |
| High        | Loose CAN connector or damaged twisted pair          | Inspect harness; measure differential voltage at nodes      |
| Medium      | Poor termination (wrong resistor value)              | Measure resistance across bus (should be ~60 ohm)           |
| Medium      | Bit timing mismatch (sample point too tight)         | Adjust sample point; use oscilloscope to verify bit quality |
| Low         | Ground potential difference between nodes            | Measure ground difference; ECUs should share common ground  |

---

## 4. Signal Out of Range

**Symptom:** DTC for sensor signal out of range; value in trace shows max or min.

| Probability | Probable Cause                                       | Debug Step                                                  |
|-------------|------------------------------------------------------|-------------------------------------------------------------|
| High        | Sender ECU sending default/error value intentionally | Check DTC on sender; sender may be in error state           |
| High        | Scaling mismatch — factor/offset wrong in receiver   | Compare DBC signal definition vs actual encoded value       |
| Medium      | Sender ECU not initialised yet (startup phase)       | Capture trace from ignition-on; compare timing              |
| Medium      | Wrong byte order (little vs big endian)              | Check DBC endianness setting; compare raw bytes             |
| Low         | CAN ID collision — different signal on same ID       | Check for ID conflicts in DBC; check network management     |

---

## 5. Node Not Responding to Diagnostic Requests

**Symptom:** No response to 0x22 ReadDID or TesterPresent; session times out.

| Probability | Probable Cause                                       | Debug Step                                                  |
|-------------|------------------------------------------------------|-------------------------------------------------------------|
| High        | ECU not powered or not booted                        | Confirm power supply; measure Vcc on ECU                    |
| High        | Wrong CAN channel or baud rate on tester             | Confirm tester channel, baud rate, and bus connection       |
| High        | ECU in bus-off state                                 | Check TEC; power cycle ECU to recover                       |
| Medium      | Functional addressing used — ECU ignores             | Switch to physical addressing (ECU's specific ID)           |
| Medium      | Gateway blocking diagnostic routing                  | Check gateway routing table; confirm physical address       |
| Low         | Wrong CAN database loaded in CANoe/CANalyzer         | Reload correct DBC; check physical vs functional addresses  |
