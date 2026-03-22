# AUTOSAR Classic BSW Modules — Key Reference

All examples use synthetic configurations and generic descriptions.

| Module | Full Name               | Purpose                                           | Key APIs                              | Typical Issues                              |
|--------|-------------------------|---------------------------------------------------|---------------------------------------|---------------------------------------------|
| Com    | Communication           | Signal/PDU packing and routing within ECU         | Com_SendSignal, Com_ReceiveSignal     | Signal byte-order mismatch, timeout config  |
| PduR   | PDU Router              | Routes PDUs between Com and IF layers             | PduR_ComTransmit                      | Routing table misconfiguration, ID clash    |
| CanIf  | CAN Interface           | Abstracts hardware CAN controller                 | CanIf_Transmit, CanIf_RxIndication   | Hardware channel mapping errors             |
| CanSM  | CAN State Manager       | Manages CAN bus state transitions                 | CanSM_RequestComMode                  | Bus-off recovery loop, timing config        |
| CanNm  | CAN Network Management  | Coordinates network sleep/wake-up                 | CanNm_NetworkRequest                  | NM message timing, node ID collision        |
| NvM    | NvM Manager             | Non-volatile memory read/write management         | NvM_ReadBlock, NvM_WriteBlock        | Block layout change after re-flash           |
| Dcm    | Diagnostic Comm. Mgr    | Handles UDS diagnostic sessions and services      | Dcm_GetSecurityLevel                  | Session/security transition timing          |
| Dem    | Diagnostic Event Mgr    | Manages DTCs, event status, freeze frames         | Dem_ReportErrorStatus                 | DTC not stored, wrong event config          |
| Os     | Operating System        | Task scheduling, alarms, events (OSEK/AUTOSAR OS) | Os_ActivateTask, Os_SetEvent          | Stack overflow, missed deadlines            |
| RTE    | Runtime Environment     | Mediates SWC communication and scheduling         | Rte_Read_*, Rte_Write_*, Rte_Call_*  | Generated code errors on port mismatch      |
| EcuM   | ECU Manager             | Controls ECU startup, shutdown, and sleep         | EcuM_Init, EcuM_GoDown               | Wake-up source not configured               |
| BswM   | BSW Mode Manager        | Coordinates BSW mode transitions                  | BswM_RequestMode                      | Rule expression conflicts                   |
| Fee    | Flash EEPROM Emulation  | Emulates EEPROM in flash for NvM backing          | Fee_Read, Fee_Write                   | Wear-levelling exhaustion over life         |
| Wdg    | Watchdog Manager        | Services watchdog within configured window        | WdgM_MainFunction                     | Checkpoint not serviced → reset             |
| Fls    | Flash Driver            | Raw flash read/write/erase for lower layers       | Fls_Read, Fls_Write, Fls_Erase        | Erase time exceeding deadline               |

---

## Common BSW configuration parameters (selected)

### Com module
- `ComSignalEndianness` — LITTLE_ENDIAN or BIG_ENDIAN per DBC
- `ComSignalBitPosition` — starting bit position in the PDU
- `ComTimeoutFactor` — reception deadline monitoring multiplier

### CanIf module
- `CanIfCtrlId` — maps logical channel to hardware controller
- `CanIfTxPduId` — unique PDU ID for each transmitted message
- `CanIfRxPduDlc` — expected DLC for received message validation

### NvM module
- `NvMBlockUseCrc` — enables CRC for block integrity check
- `NvMWriteBlockOnce` — block can only be written once (factory data)
- `NvMResistantToChangedSw` — block survives SW update without reset

### Dcm module
- `DcmDspSessionForBoot` — sessions allowed for bootloader access
- `DcmDspSecurityLevel` — security level required per service
- `DcmTimingP2ServerMax` — maximum response time per service request

### Os module
- `OsTaskPriority` — numerical priority (higher = more urgent)
- `OsTaskActivation` — max pending activations for basic tasks
- `OsStacksize` — stack size in bytes (ensure headroom for calls)
