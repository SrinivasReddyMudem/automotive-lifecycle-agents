# UDS Negative Response Codes — ISO 14229

All NRC codes with hex value, name, meaning, and most common root cause.
NRC 0x78 is the only "positive" NRC — it means response pending, not failure.

| NRC  | Name                                    | Meaning                                        | Most Common Root Cause in Automotive ECUs              |
|------|-----------------------------------------|------------------------------------------------|--------------------------------------------------------|
| 0x10 | generalReject                           | Request rejected — no specific reason          | Catch-all; check service ID and subfunction            |
| 0x11 | serviceNotSupported                     | Service ID not supported by ECU                | Wrong SID; service disabled in current build variant   |
| 0x12 | subFunctionNotSupported                 | SubFunction value not recognised               | Wrong subfunction byte; check service spec             |
| 0x13 | incorrectMessageLengthOrInvalidFormat   | Wrong data length for this service             | Missing or extra bytes in request; check byte counts   |
| 0x14 | responseTooLong                         | Response data exceeds buffer or frame size     | DID response larger than configured buffer             |
| 0x21 | busyRepeatRequest                       | Server busy — repeat later                     | ECU in middle of previous operation; retry after 100ms |
| 0x22 | conditionsNotCorrect                    | Preconditions not met                          | Wrong session, engine not running, speed not zero      |
| 0x24 | requestSequenceError                    | Services called in wrong order                 | Forgot seed-key before write; missed step in sequence  |
| 0x25 | noResponseFromSubnetComponent           | Subnet node not responding                     | Gateway routing issue; check CAN/LIN connectivity      |
| 0x26 | failurePreventsExecutionOfRequestedAction | Internal failure blocks execution            | HW fault in ECU; cannot execute even if request valid  |
| 0x31 | requestOutOfRange                       | Parameter or ID outside valid range            | DID not defined, address out of range, invalid mode    |
| 0x33 | securityAccessDenied                    | Security level not sufficient                  | Did not complete 0x27 seed-key; wrong security level   |
| 0x35 | invalidKey                              | Seed-key calculation returned wrong result     | Key algorithm mismatch; seed already used (replay)     |
| 0x36 | exceededNumberOfAttempts                | Too many failed key attempts                   | Repeated wrong key — ECU locked for time delay         |
| 0x37 | requiredTimeDelayNotExpired             | Must wait before retrying security access      | Back-off timer after exceededNumberOfAttempts          |
| 0x70 | uploadDownloadNotAccepted               | Download/upload not accepted in current state  | Not in programming session or wrong memory state       |
| 0x71 | transferDataSuspended                   | Data transfer was interrupted                  | CAN bus error during block transfer; restart download  |
| 0x72 | generalProgrammingFailure               | Flash write or erase operation failed          | Flash controller error; voltage too low during flash   |
| 0x73 | wrongBlockSequenceCounter               | Block counter does not match expected value    | Missed a block; retransmit from last accepted block    |
| 0x78 | requestCorrectlyReceivedResponsePending | Request received; processing in progress       | NOT an error — wait for final response (up to P2* ms)  |
| 0x7E | subFunctionNotSupportedInActiveSession  | SubFunction valid but not in current session   | Trying to use extended session function in default     |
| 0x7F | serviceNotSupportedInActiveSession      | Service valid but not in current session       | Must enter extended or programming session first       |

---

## How to read a negative response frame

```
Frame: 7F [SID] [NRC]
 7F = Negative Response Service ID (always 0x7F)
 SID = The service ID that was rejected (echo of request SID)
 NRC = The specific negative response code
```

**Example:** `7F 22 31`
- `7F` — negative response
- `22` — ReadDataByIdentifier was the requested service
- `31` — requestOutOfRange — the DID is not defined in this ECU

---

## FAE quick triage guide

| Symptom                          | Most likely NRC | First action                               |
|----------------------------------|-----------------|--------------------------------------------|
| Nothing works in default session | 0x7F            | Enter extended session first (0x10 0x03)  |
| Write rejected                   | 0x33            | Complete security access (0x27)           |
| Flash rejected at start          | 0x22            | Check session, speed=0, ignition state    |
| Flash rejected mid-transfer      | 0x73            | Check block counter; restart from 0x34   |
| Session drops during flash       | timeout / 0x78  | Keep sending TesterPresent (0x3E)         |
| Key rejected on first try        | 0x35            | Check seed-key algorithm; re-request seed |
| Key rejected after 3 tries       | 0x36            | Wait for ECU delay timer (often 10 sec)   |
