# ISO/SAE 21434 Attack Feasibility and Security Reference

## Attack Feasibility Scoring (ISO 21434 Annex B)

### Feasibility Factor Scores

| Factor | Score | Rating |
|--------|-------|--------|
| **Elapsed Time to attack** | | |
| <= 1 day | 3 | Very High |
| <= 1 week | 4 | High |
| <= 1 month | 7 | Medium |
| <= 6 months | 10 | Low |
| > 6 months | 11 | Very Low |
| **Expertise required** | | |
| Layman (no automotive knowledge) | 0 | Very High |
| Proficient (automotive domain knowledge) | 3 | High |
| Expert (cryptography, protocol internals) | 6 | Medium |
| Multiple experts (cross-domain team) | 8 | Low |
| **Knowledge of item required** | | |
| Public (datasheet, open standard) | 0 | Very High |
| Restricted (internal documentation) | 3 | High |
| Confidential (OEM proprietary) | 7 | Medium |
| Strictly confidential (HSM keys, OEM PKI) | 11 | Low |
| **Window of Opportunity** | | |
| Unlimited (remote, no physical access) | 0 | Very High |
| Easy (OBD-II port, 5 min physical access) | 1 | High |
| Moderate (workshop access, teardown required) | 4 | Medium |
| Difficult (specialized lab, ECU extraction) | 10 | Low |
| **Equipment required** | | |
| Standard (laptop, CAN adapter, free tools) | 0 | Very High |
| Specialized (oscilloscope, JTAG debugger) | 4 | High |
| Bespoke (custom firmware, fault injection HW) | 7 | Medium |
| Multiple bespoke (lab-grade equipment set) | 9 | Low |

**Total Feasibility Score** = Sum of scores across all 5 factors

| Total Score | Feasibility Rating |
|-------------|-------------------|
| 0-9 | Very High (AF4) |
| 10-16 | High (AF3) |
| 17-23 | Medium (AF2) |
| 24-33 | Low (AF1) |
| >= 34 | Very Low (AF0, negligible) |

---

## Impact Rating Criteria (ISO 21434 Clause 9.5)

| Rating | Safety Impact | Financial Impact | Operational Impact | Privacy Impact |
|--------|--------------|------------------|--------------------|----------------|
| **Severe** | Death or serious injury to multiple persons | > 1,000,000 EUR | Complete system failure | Mass breach > 10,000 users |
| **Major** | Light to moderate injury | 100,000 - 1,000,000 EUR | Major function degradation | PII exposure 100-10,000 users |
| **Moderate** | Possible minor injury | 10,000 - 100,000 EUR | Minor function degradation | Limited < 100 users |
| **Negligible** | No injury expected | < 10,000 EUR | Inconvenience only | Minimal or no privacy impact |

---

## Risk Determination Matrix

| Impact / Feasibility | Very High | High | Medium | Low | Very Low |
|----------------------|-----------|------|--------|-----|----------|
| **Severe** | Unacceptable | Unacceptable | High | Medium | Low |
| **Major** | Unacceptable | High | High | Medium | Low |
| **Moderate** | High | Medium | Medium | Low | Very Low |
| **Negligible** | Medium | Low | Low | Very Low | Very Low |

**Risk Treatment**:
- Unacceptable: Must be reduced — risk avoidance or mandatory mitigation
- High: Should be reduced; requires strong justification to accept
- Medium: May be accepted with management approval and documented rationale
- Low/Very Low: Can be accepted with documented justification

---

## STRIDE Attack Catalog for Automotive

| Attack Type | Vector | Automotive Example | Mitigation |
|-------------|--------|-------------------|------------|
| **Spoofing** | CAN injection | Fake brake pedal signal from compromised ECU | SecOC message authentication |
| **Tampering** | Firmware modification | Reflash ECU via unsecured diagnostic port | Secure boot, signed firmware |
| **Repudiation** | Log deletion | Attacker clears evidence after intrusion | Write-once logging, remote log forward |
| **Information Disclosure** | CAN eavesdropping | Passive monitoring of unencrypted CAN | SecOC confidentiality mode |
| **Denial of Service** | CAN bus flooding | Send max-rate frames to saturate bus | IDS with rate limiting |
| **Elevation of Privilege** | Diagnostic exploit | Exploit UDS service to gain programming access | Seed-key auth, session control |

---

## UN R155 Annex 5 Threat Catalog (Key Entries)

| Threat ID | Description | Target Asset | Typical Mitigation |
|-----------|-------------|--------------|-------------------|
| 1.1.1 | Back-end server attack | Cloud services | TLS, WAF, authentication |
| 1.2.1 | Update procedure attack | OTA update mechanism | Signed updates, secure transport |
| 1.3.1 | Vehicle communication channel attack | Telematics unit | Encrypted channels, firewall |
| 2.1.1 | External connectivity attack | TCU, gateway | Authentication, IDS |
| 2.2.1 | Wireless communication attack | V2X, WiFi, Bluetooth | WPA3, encryption |
| 3.1.1 | Wired communication attack | OBD-II, Ethernet port | Physical access control, auth |
| 4.1.1 | Vehicle data or code attack | Flash memory, RAM | Secure boot, encrypted storage |

---

## Security Controls Checklist

### Vehicle-Level Controls

- [ ] Gateway Firewall: CAN-Ethernet gateway with packet filtering rules
- [ ] Network Segmentation: Critical domains isolated from infotainment domain
- [ ] Intrusion Detection System (IDS): Monitor CAN/Ethernet for anomalies
- [ ] Secure Gateway: Authenticated inter-domain communication
- [ ] Diagnostic Access Control: UDS seed-key for Level 2+ services
- [ ] Physical Security: Tamper detection on safety-critical ECUs
- [ ] Secure Debug Port: JTAG/SWD disabled or authenticated in production

### ECU-Level Controls

- [ ] Secure Boot: RSA/ECDSA firmware signature verification at startup
- [ ] Code Signing: All application software signed by OEM key
- [ ] Runtime Integrity: Periodic CRC/hash checks of code in RAM
- [ ] Memory Protection: MPU configured to prevent code injection
- [ ] Stack Protection: Stack canaries enabled
- [ ] Watchdog: Independent watchdog to detect lockup or tampering
- [ ] Secure Storage: HSM or secure element for private keys
- [ ] Anti-Rollback: Version enforcement to block firmware downgrade

### Communication Security

- [ ] SecOC: Message authentication on critical CAN/FlexRay messages
- [ ] TLS 1.3: For Ethernet-based protocols (DoIP, SOME/IP)
- [ ] IPsec/MACsec: Layer 3/2 encryption for zonal Ethernet
- [ ] Freshness Values: Counter or timestamp to prevent replay attacks
- [ ] Rate Limiting: Prevent DoS on communication channels
- [ ] Certificate Management: X.509 lifecycle (issue, renew, revoke)

### Backend/Cloud Security

- [ ] OTA Update Security: Signature verification + encrypted transport
- [ ] Backend Authentication: Mutual TLS between vehicle and cloud
- [ ] API Security: OAuth2/JWT for REST APIs
- [ ] Secure Logging: Tamper-evident logs for forensic analysis
- [ ] Incident Response: SOC monitoring, vulnerability disclosure process

---

## Cryptographic Algorithm Selection (2026+ Recommendations)

### Recommended Algorithms

| Use Case | Algorithm | Key/Hash Size | Notes |
|----------|-----------|---------------|-------|
| Symmetric Encryption | AES-GCM | 256-bit | Authenticated encryption |
| Symmetric Encryption | ChaCha20-Poly1305 | 256-bit | For constrained embedded |
| Asymmetric Encryption | RSA | 3072-bit minimum | Use OAEP padding |
| Key Exchange | ECDH | P-256 or higher | Faster than RSA on MCU |
| Digital Signature | ECDSA | P-256 or higher | Recommended for ECU |
| Digital Signature | EdDSA (Ed25519) | 256-bit | Recommended new designs |
| Hash Function | SHA-256 | 256-bit | General purpose |
| Message Authentication | HMAC-SHA256 | 256-bit | For non-AEAD |
| Message Authentication | CMAC-AES | 128/256-bit | AUTOSAR SecOC |
| Key Derivation | HKDF | - | For key expansion |

### Deprecated Algorithms — Do Not Use

| Algorithm | Status | Reason |
|-----------|--------|--------|
| DES, 3DES | Prohibited | Key size too small (56/112-bit) |
| MD5 | Prohibited | Collision attacks demonstrated |
| SHA-1 | Prohibited | Collision attacks demonstrated |
| RSA 1024-bit | Prohibited | Insufficient key length |
| RC4 | Prohibited | Statistical biases known |
| AES-ECB mode | Prohibited | Does not hide data patterns |

---

## ISO 21434 Compliance Checklist

- [ ] Clause 5: Organizational cybersecurity management
  - [ ] 5.4.2: Cybersecurity policy defined
  - [ ] 5.4.3: Roles and responsibilities assigned
- [ ] Clause 8: Continuous cybersecurity activities
  - [ ] 8.3: Cybersecurity monitoring established
  - [ ] 8.4: Cybersecurity event assessment process
- [ ] Clause 9: Concept phase
  - [ ] 9.3: TARA performed and documented
  - [ ] 9.4: Cybersecurity goals defined with CAL
  - [ ] 9.5: Cybersecurity concept created
- [ ] Clause 10: Product development
  - [ ] 10.4: Cybersecurity requirements specification
  - [ ] 10.5: Architectural design with security controls
  - [ ] 10.7: Integration and verification of security controls
- [ ] Clause 11: Cybersecurity validation
  - [ ] 11.4: Validation plan approved
  - [ ] 11.5: Penetration testing executed and documented
- [ ] Clause 13: Operations and maintenance
  - [ ] 13.4: Vulnerability management process active
  - [ ] 13.5: Incident response procedure established
  - [ ] 13.6: Security update process defined

---

## UN R155 CSMS Required Documentation

1. Cybersecurity Policy (ISO 21434 Clause 5.4.2)
2. TARA Methodology description (Clause 9.3)
3. Risk Treatment Plan (Clause 9.4)
4. Cybersecurity Validation Report — penetration test results (Clause 11)
5. Production Control Plan (Clause 12)
6. Vulnerability Management Process (Clause 15.3)
7. Incident Response Procedure (Clause 15.5)
8. Security Update Process description (Clause 15.6)

---

## Key Management Lifecycle Reference

### Certificate Validity Periods

| Certificate Type | Validity | Renewal Trigger |
|-----------------|----------|-----------------|
| Root CA | 20 years | N/A (kept offline) |
| Intermediate CA (OEM) | 10 years | 1 year before expiry |
| ECU Certificate | 15 years (vehicle life) | Hardware-bound, non-renewable |
| TLS Server Certificate | 1 year | Auto-renew at 30 days remaining |
| V2X Certificate | 3 years | Auto-renew at 90 days remaining |

---

*This requires review and approval by a qualified engineer before use in any project.*
