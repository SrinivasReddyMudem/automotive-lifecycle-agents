---
name: iso21434-tara
description: |
  Load automatically when any of these appear:
  cybersecurity, TARA, CAL, CAL-1, CAL-2, CAL-3,
  CAL-4, cyber attack, threat, vulnerability,
  attack feasibility, impact, cybersecurity goal,
  security control, OTA, over-the-air update,
  remote access, CAN injection, replay attack,
  man in the middle, ECU hacking, ISO 21434,
  UNECE R155, UNECE R156, penetration test,
  cybersecurity case, asset, damage scenario,
  attack path, threat scenario, security testing,
  secure boot, PKI, certificate, key management,
  intrusion detection, IDS, firewall, HSM,
  hardware security module, cybersecurity plan,
  cybersecurity assessment, cybersecurity manager,
  spoofing, tampering, repudiation, information
  disclosure, denial of service, elevation of
  privilege, STRIDE, attack tree, attack vector,
  authentication, authorisation, encryption,
  message authentication code, MAC, digital
  signature, security update, vulnerability
  disclosure, incident response, monitoring.
---

## TARA method overview

Asset identification
→ Damage scenarios
→ Threat scenarios
→ Impact assessment
→ Attack feasibility
→ CAL assignment
→ Cybersecurity goals
→ Security controls

---

## Impact categories (ISO 21434 Clause 15)

| Category   | Description                                          |
|------------|------------------------------------------------------|
| Safety     | Physical harm or death to persons                    |
| Financial  | Monetary loss to user, OEM, or supplier              |
| Operational| Loss or degradation of vehicle function              |
| Privacy    | Exposure of personal or confidential data            |

**Impact severity levels:**
- I1 — Negligible: no significant impact
- I2 — Moderate: limited or reversible impact
- I3 — Major: significant impact, difficult to reverse
- I4 — Severe: critical harm, safety risk or major financial loss

---

## Attack feasibility factors

Attack feasibility is evaluated using these factors:

| Factor                   | Levels                                    |
|--------------------------|-------------------------------------------|
| Elapsed time             | < 1 week / 1 week–1 month / 1–6 months / >6 months |
| Expertise                | Layman / Proficient / Expert / Multiple experts |
| Knowledge of item        | Public / Restricted / Confidential / Strictly confidential |
| Window of opportunity    | Unlimited / Easy / Moderate / Difficult   |
| Equipment                | Standard / Specialised / Bespoke / Multiple bespoke |

**Feasibility levels:**
- AF1 — Very low: requires significant resources and expertise
- AF2 — Low: requires expertise and specialised access
- AF3 — Medium: moderate resources needed
- AF4 — High: easily performed with common tools

---

## CAL assignment table

[reference: references/cal-table.md]

Full Impact × Attack Feasibility matrix for CAL1 through CAL4.

---

## Cybersecurity goal format

"The [asset] shall be protected against [threat scenario]
to avoid [damage scenario] [CAL-level requirement]."

**Example:**
"The OTA software update mechanism shall be protected against
malicious firmware injection to avoid deployment of unauthorized
software that could impair vehicle safety functions. CAL-4 requirements apply."

---

## Key rules for TARA output

- Identify all assets: primary (data) and secondary (systems)
- Threat scenarios must name the attacker profile
- Impact must cover all four categories where applicable
- Worst-case impact drives the CAL (not average)
- Attack feasibility uses the easiest known attack path
- Cybersecurity goals are technology-independent
- All TARA output ends with:
  "This analysis requires review and approval by a qualified
  cybersecurity engineer before use in any project."

[reference: references/tara-template.md]
