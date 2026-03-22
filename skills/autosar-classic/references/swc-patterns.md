# AUTOSAR Classic SWC Design Patterns

Five common patterns with ARXML element names and runnable design.
All names and signal definitions are synthetic examples.

---

## Pattern 1 — Cyclic Sender (Provider SWC)

**Use case:** Publish a vehicle signal at a fixed rate to other SWCs.
**Example:** Vehicle speed provider running at 10 ms cycle.

**ARXML elements:**
```
SWC Type:          VehicleSpeedProvider_SWCType
Port:              VehicleSpeed_PP  (P-Port)
Interface:         SR_VehicleSpeed_I  (Sender-Receiver)
Data element:      VehicleSpeed_DE  (type: uint16, range 0–30000 in 0.01 km/h)
Internal behavior: VehicleSpeedProvider_IB
Runnable:          VehicleSpeedProvider_MainFunction
Runnable trigger:  TimingEvent, period 10ms
```

**Runnable design:**
1. Read raw ADC or CAN signal value
2. Apply scaling and range check
3. Write scaled value to R-Port data element via Rte_Write
4. Set error flag if out-of-range via Dem_ReportErrorStatus

---

## Pattern 2 — Cyclic Receiver (Consumer SWC)

**Use case:** Consume a signal and use it in control logic.
**Example:** Torque request consumer at 10 ms cycle.

**ARXML elements:**
```
SWC Type:          TorqueController_SWCType
Port:              VehicleSpeed_RP  (R-Port, Sender-Receiver)
Port:              TorqueRequest_RP  (R-Port, Sender-Receiver)
Port:              TorqueOutput_PP  (P-Port, Sender-Receiver)
Internal behavior: TorqueController_IB
Runnable:          TorqueController_MainFunction
Runnable trigger:  TimingEvent, period 10ms
```

**Runnable design:**
1. Rte_Read on both input ports
2. Check port read return status (E_OK check)
3. Execute control algorithm
4. Rte_Write result to P-Port
5. If input invalid: set safe output (e.g., zero torque)

---

## Pattern 3 — Client-Server Request Handler (Server SWC)

**Use case:** Provide a service that other SWCs can call synchronously.
**Example:** NvM block read service.

**ARXML elements:**
```
SWC Type:          NvmReadService_SWCType
Port:              ReadCalibration_PP  (P-Port, Client-Server)
Interface:         CS_ReadCalibration_I
Operation:         ReadCalibration_Op  (in: blockId uint8; out: data uint8[32]; return Std_ReturnType)
Internal behavior: NvmReadService_IB
Runnable:          ReadCalibration_Run
Runnable trigger:  OperationInvokedEvent on ReadCalibration_Op
```

**Runnable design:**
1. Receive blockId from caller
2. Call NvM_ReadBlock synchronously or via polling
3. Copy block data to output buffer
4. Return E_OK on success, E_NOT_OK on failure

---

## Pattern 4 — Mode-Dependent SWC

**Use case:** SWC changes behaviour based on ECU mode (normal / diagnostic / sleep).
**Example:** Diagnostic data logger that only runs in extended diagnostic session.

**ARXML elements:**
```
SWC Type:          DiagLogger_SWCType
Port:              EcuMode_RP  (R-Port, Mode Switch Interface)
Interface:         MSI_EcuMode_I  (Mode Switch Interface)
Modes:             NORMAL, DIAGNOSTIC, SLEEP
Internal behavior: DiagLogger_IB
Runnable:          DiagLogger_NormalMode  (active in NORMAL)
Runnable:          DiagLogger_DiagMode    (active in DIAGNOSTIC)
```

**Runnable design:**
- In NORMAL mode: minimal logging, reduce CPU load
- In DIAGNOSTIC mode: full signal capture, DTC snapshot storage
- Mode activation/deactivation events drive runnable enable/disable

---

## Pattern 5 — ASIL-Partitioned SWC Pair (ASIL Decomposition)

**Use case:** ASIL D function decomposed into two independent SWCs for independence.
**Example:** Brake command splitter: ASIL B + ASIL B = ASIL D.

**ARXML elements:**
```
SWC Type A:        BrakeCmd_Primary_SWCType     (ASIL B, derived)
SWC Type B:        BrakeCmd_Monitor_SWCType     (ASIL B, derived)
Composition:       BrakeCmd_ASILD_Composition
Ports on A:        BrakeRequest_RP (R), BrakeCmd_PP (P)
Ports on B:        BrakeRequest_RP (R), BrakeMonitor_PP (P)
Arbiter SWC:       BrakeCmd_Arbiter_SWCType
```

**Runnable design:**
- Primary SWC: computes brake command from driver request
- Monitor SWC: independently verifies plausibility of brake command
- Arbiter SWC: compares outputs; applies safe state if discrepancy detected
- Freedom from interference: SWCs must be mapped to separate OS partitions
- No shared writable memory between Primary and Monitor
