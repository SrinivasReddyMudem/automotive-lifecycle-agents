# UDS Services Reference — ISO 14229

All services listed with service ID, name, typical request, and FAE debug tips.

| SID  | Service Name                        | Session(s)         | Typical Request Content                  | Positive Response         | FAE Debug Tip                                             |
|------|-------------------------------------|--------------------|------------------------------------------|---------------------------|-----------------------------------------------------------|
| 0x10 | DiagnosticSessionControl            | All                | subFunctionByte (session type)           | 0x50 + subFunction        | If rejected: check session preconditions                  |
| 0x11 | ECUReset                            | All                | resetType (0x01=hard, 0x02=key, 0x03=soft)| 0x51 + resetType        | NRC 0x22: conditions not correct — check session first    |
| 0x14 | ClearDiagnosticInformation          | All                | groupOfDTC (0xFFFFFF = all)              | 0x54 (no data)            | NRC 0x31: DTC group not valid; use 0xFFFFFF for all       |
| 0x19 | ReadDTCInformation                  | All                | subFunction + DTC status mask            | 0x59 + DTC records        | SubFunc 0x02 = most common (DTCs by status mask)          |
| 0x22 | ReadDataByIdentifier                | All (some restrict)| DID (2 bytes, e.g., 0xF190=VIN)          | 0x62 + DID + data         | NRC 0x31: DID not supported; NRC 0x22: wrong session      |
| 0x23 | ReadMemoryByAddress                 | Extended           | addressAndLengthFormat + startAddress    | 0x63 + data               | Rarely used in production; mainly for debug               |
| 0x27 | SecurityAccess                      | Extended/Prog      | 0x01 = request seed; 0x02 = send key     | 0x67 + seed/0x00          | NRC 0x35: key wrong; NRC 0x36: attempts exceeded          |
| 0x28 | CommunicationControl                | Extended           | controlType + communicationType          | 0x68 + controlType        | Disables normal communication during diagnostics          |
| 0x2E | WriteDataByIdentifier               | Extended           | DID + data to write                      | 0x6E + DID                | Requires security access first; NRC 0x22: not in ext sess |
| 0x2F | InputOutputControlByIdentifier      | Extended           | DID + controlOptionRecord                | 0x6F + DID + status       | Used for actuator testing and parameter override          |
| 0x31 | RoutineControl                      | Extended/Prog      | 0x01=start, 0x02=stop, 0x03=result + ID  | 0x71 + status             | Flash pre-check routine: 0x31 0x01 0xFF00                 |
| 0x34 | RequestDownload                     | Programming        | dataFormatIdentifier + addressAndLength  | 0x74 + blockLengthInfo    | Rejected if not in programming session or security not OK |
| 0x35 | RequestUpload                       | Programming        | dataFormatIdentifier + addressAndLength  | 0x75 + blockLengthInfo    | Used for memory readback or data extraction               |
| 0x36 | TransferData                        | Programming        | blockSequenceCounter + transferData      | 0x76 + blockSeqCounter    | Block counter must increment each block; reset on error   |
| 0x37 | RequestTransferExit                 | Programming        | (no parameters usually)                  | 0x77 (no data)            | Flash validation happens here; NRC if CRC fails           |
| 0x38 | RequestFileTransfer                 | Programming        | modeOfOperation + filePath               | 0x78 + response           | Used in some OTA systems for file-based update            |
| 0x3D | WriteMemoryByAddress                | Extended           | addressAndLength + data                  | 0x7D                      | Restricted; rarely enabled in production ECUs             |
| 0x3E | TesterPresent                       | Extended/Prog      | subFunction 0x00 or 0x80 (no response)  | 0x7E + 0x00               | Send every 1–2 sec to prevent session timeout             |
| 0x85 | ControlDTCSetting                   | Extended           | 0x01=on, 0x02=off + DTCGroup             | 0xC5 + setting            | Disable DTC storage during calibration to avoid noise     |
| 0x86 | ResponseOnEvent                     | Extended           | eventType + eventWindowTime + service    | 0xC6 + response           | Complex service — rarely used outside EOBD systems        |

---

## Flash programming sequence (typical)

```
1. 0x10 0x02          → Enter Programming Session
2. 0x27 0x01          → Request Seed
3. 0x27 0x02 [key]    → Send Computed Key
4. 0x31 0x01 0xFF 0x00→ Start Pre-Programming Routine (erase check)
5. 0x34 [params]      → Request Download (address + size)
6. 0x36 [data blocks] → Transfer Data (loop until all blocks sent)
7. 0x37               → Request Transfer Exit (CRC validation)
8. 0x31 0x01 0xFF 0x01→ Check Programming Dependencies
9. 0x11 0x01          → ECU Reset (hard reset)
```

Any negative response at step 5–7 requires restarting from step 4 or earlier.
