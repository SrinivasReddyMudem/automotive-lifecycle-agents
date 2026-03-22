---
name: autosar-classic
description: |
  Load automatically when any of these appear:
  AUTOSAR, BSW, SWC, RTE, ARXML, ComStack,
  NvM, Dcm, Dem, Com, PduR, CanIf, CanSM,
  CanNm, FrIf, LinIf, EthIf, runnable, port,
  R-Port, P-Port, interface, sender-receiver,
  client-server, AUTOSAR Classic, software
  component, basic software, runtime environment,
  memory mapping, OS task, alarm, schedule table,
  AUTOSAR Adaptive, ara::com, execution manifest,
  service instance, method, event, field, DDS,
  SOME/IP, service oriented, adaptive platform,
  BSW configuration, DaVinci, EB tresos, ETAS,
  Vector, communication matrix, system description,
  SWC description, composition, port prototype,
  AUTOSAR R4, AUTOSAR R22, AUTOSAR naming,
  software component type, atomic SWC, composition
  SWC, service SWC, sensor actuator SWC, parameter
  SWC, SWC connector, AUTOSAR interface, data
  element, operation, implementation data type,
  application data type, base type, category.
---

## SWC types (AUTOSAR Classic)

| SWC Type             | Purpose                                        |
|----------------------|------------------------------------------------|
| Application SWC      | Implements application logic, no direct HW     |
| Sensor-Actuator SWC  | Direct hardware access (sensors, actuators)    |
| Parameter SWC        | Provides calibration and configuration data    |
| ECU Abstraction SWC  | Abstracts ECU hardware for application SWCs    |
| Service SWC          | Provides OS/BSW services to application layer  |
| Composition SWC      | Groups other SWCs, defines internal interfaces |

---

## Port and interface types

| Port/Interface Type | Description                                          |
|---------------------|------------------------------------------------------|
| R-Port (Required)   | Consumes a service or data from another SWC          |
| P-Port (Provided)   | Offers a service or data to other SWCs               |
| Sender-Receiver     | Asynchronous data flow between SWCs                  |
| Client-Server       | Synchronous service call with request/response       |
| NvData Interface    | Non-volatile data read/write access                  |
| Parameter Interface | Read-only access to calibration parameters           |
| Trigger Interface   | Signals an event trigger to a receiving SWC          |
| Mode Switch         | Communicates mode changes between SWCs               |

---

## AUTOSAR naming conventions (R4.x)

**Data type naming:**
- Base type: `uint8`, `sint16`, `float32`
- Implementation type: `VehicleSpeed_T`, `EngineRpm_T`
- Application type: `VehicleSpeed_At`, `EngineRpm_At`

**Interface naming:**
- Sender-Receiver: `SR_VehicleSpeed_I`, `SR_EngineRpm_I`
- Client-Server: `CS_DiagnosticService_I`

**SWC naming:**
- SWC type: `VehicleSpeedProvider_SWCType`
- Instance: `VehicleSpeedProvider_SWC`

**Port naming:**
- Provided: `VehicleSpeed_PP`
- Required: `VehicleSpeed_RP`

**Runnable naming:**
- Init runnable: `VehicleSpeedProvider_Init`
- Cyclic runnable: `VehicleSpeedProvider_MainFunction`
- Event runnable: `VehicleSpeedProvider_OnSpeedChange`

---

## Key BSW modules

[reference: references/bsw-modules.md]

Com, PduR, CanIf, CanSM, NvM, Dcm, Dem, Os, RTE —
each with purpose, key APIs, and common issues.

## Common SWC patterns

[reference: references/swc-patterns.md]

Five patterns with ARXML element names and runnable design.
