# TARA Template — OTA Update System Example (Synthetic Data)

This is a fully worked TARA example using synthetic data only.
It demonstrates the required output format for ISO 21434 analysis.

---

## 1. Item Boundary Definition

**Item:** Over-the-Air (OTA) Software Update System
**Description (synthetic):** The OTA system receives software update packages
from a cloud backend via the vehicle's telematics unit (TCU). Updates are
validated and distributed to target ECUs via the internal vehicle network.

**Item boundary:**
- In scope: TCU OTA client, update validation module, CAN/Ethernet distribution,
  target ECU flash programming interface
- Out of scope: Cloud backend server, mobile phone app, PKI infrastructure
  (covered in separate TARA)

---

## 2. Asset Identification

| Asset ID | Asset Name                   | Asset Type | Description                                        |
|----------|------------------------------|------------|----------------------------------------------------|
| A-001    | Firmware update package      | Data       | SW binary transmitted to ECU for programming       |
| A-002    | Code signing key (public)    | Crypto     | Used to verify firmware authenticity               |
| A-003    | TCU authentication token     | Data       | Credential for cloud server authentication         |
| A-004    | ECU flash write interface    | Function   | Ability to reprogram any connected ECU             |
| A-005    | Update session control       | Function   | Ability to authorise and trigger update execution  |

---

## 3. Damage Scenarios

| DS-ID | Asset  | Damage Scenario                                            | Impact Categories  | Worst Impact |
|-------|--------|------------------------------------------------------------|--------------------|--------------|
| DS-01 | A-001  | Malicious firmware deployed to safety-critical ECU         | Safety, Operational| I4 (Severe)  |
| DS-02 | A-001  | Firmware with privacy data exfiltration deployed           | Privacy, Financial | I3 (Major)   |
| DS-03 | A-003  | Authentication token stolen → attacker gains cloud access  | Financial, Privacy | I3 (Major)   |
| DS-04 | A-004  | Attacker bricks all ECUs in a fleet                        | Financial, Op.     | I3 (Major)   |
| DS-05 | A-005  | Attacker triggers update during vehicle operation          | Safety, Op.        | I4 (Severe)  |

---

## 4. Threat Scenarios

| TS-ID | Damage | Threat Actor      | Attack Vector  | Threat Scenario Description                            |
|-------|--------|-------------------|----------------|--------------------------------------------------------|
| TS-01 | DS-01  | Remote attacker   | Cellular/Wi-Fi | Attacker intercepts update channel, replaces firmware  |
| TS-02 | DS-01  | Insider threat    | Physical CAN   | Service technician injects unsigned update via OBD     |
| TS-03 | DS-03  | Remote attacker   | Cellular       | Token harvested from TCU memory via buffer overflow    |
| TS-04 | DS-04  | Remote attacker   | Fleet backend  | Mass deployment of corrupt firmware to all fleet ECUs  |
| TS-05 | DS-05  | Remote attacker   | Remote API     | Attacker triggers update while vehicle is in motion    |

---

## 5. Attack Feasibility Assessment

| TS-ID | Elapsed Time | Expertise    | Knowledge    | Window        | Equipment    | Feasibility |
|-------|--------------|--------------|--------------|---------------|--------------|-------------|
| TS-01 | 1–6 months   | Expert       | Confidential | Moderate       | Specialised  | AF2 (Low)   |
| TS-02 | < 1 week     | Proficient   | Restricted   | Easy           | Standard     | AF3 (Medium)|
| TS-03 | 1–6 months   | Expert       | Confidential | Difficult      | Specialised  | AF2 (Low)   |
| TS-04 | > 6 months   | Multi-expert | Restricted   | Moderate       | Bespoke      | AF1 (V.Low) |
| TS-05 | 1–6 months   | Expert       | Confidential | Moderate       | Specialised  | AF2 (Low)   |

---

## 6. CAL Assignment

| TS-ID | Worst Impact | Feasibility | CAL Result |
|-------|--------------|-------------|------------|
| TS-01 | I4           | AF2         | CAL 3      |
| TS-02 | I4           | AF3         | CAL 3      |
| TS-03 | I3           | AF2         | CAL 2      |
| TS-04 | I3           | AF1         | CAL 1      |
| TS-05 | I4           | AF2         | CAL 3      |

---

## 7. Cybersecurity Goals

**CG-001 (CAL 3):**
"The OTA update system shall authenticate every firmware package using a
cryptographic signature to prevent deployment of unauthorised software."

**CG-002 (CAL 3):**
"The OTA update client shall verify that an update session is not initiated
while the vehicle is in a moving operational state."

**CG-003 (CAL 2):**
"The TCU authentication token shall be stored in hardware-protected memory
and shall not be accessible via software interfaces."

---

## 8. Review Note

This analysis requires review and approval by a qualified cybersecurity
engineer before use in any project. All data in this example is synthetic
and for demonstration purposes only.
