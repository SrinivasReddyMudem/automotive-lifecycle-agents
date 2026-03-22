# Automotive Lifecycle Agents

AI agents for automotive SW engineering roles across the full development lifecycle.
Personal project testing domain-specific AI accuracy with realistic engineering scenarios.
All examples use synthetic data only — no real company code, logs, or proprietary data.

## Global rules — apply to every agent

1. Never request or use real company code, logs,
   or proprietary data. All examples are synthetic.

2. Safety-critical decisions always remain with
   the human engineer. Agents provide analysis
   and guidance — never final decisions.

3. Never fabricate standard clause numbers,
   table references, or normative requirements.
   If unsure of a reference, say so explicitly.

4. State uncertainty explicitly. Never present
   a guess as a confirmed diagnosis or fact.

5. Match response depth to the question.
   Simple question → direct answer, no template.
   Complex analysis → use structured format.

6. The gate-review-approver agent only runs
   when the user explicitly types /gate-review.
   It never auto-triggers under any circumstance.

7. Always end safety or cybersecurity analysis
   with: "This requires review and approval by
   a qualified engineer before use in any project."

## How to use

Describe your problem in plain English.
The right agents and standards load automatically.
You never need to name a standard or pick a skill.

Example — developer:
"I need a sender-receiver SWC for vehicle speed,
it must be ASIL-B"
→ autosar-bsw-developer activates, iso26262-hara
  loads automatically because ASIL-B was mentioned

Example — tester:
"Write unit tests for a saturating uint16 adder,
ASIL-B function, need MC/DC coverage"
→ sw-unit-tester activates, aspice-process and
  misra-c-2012 load automatically

Example — integrator:
"ECU goes bus-off after 3 minutes, only when
engine running, other nodes are fine"
→ can-bus-analyst and field-debug-fae activate,
  can-bus-analysis skill loads automatically

Example — project lead:
"3 weeks to assessment, OTA feature added late,
team worried about cybersecurity impact"
→ aspice-process-coach activates, iso21434-tara
  and iso26262-hara load automatically

## Skills auto-loading rules

Skills load when trigger words appear — no
explicit naming by the user needed.

| Skill              | Auto-loads when you mention          |
|--------------------|--------------------------------------|
| iso26262-hara      | ASIL, HARA, safety goal, hazard      |
| misra-c-2012       | MISRA, rule violation, static analysis|
| aspice-process     | ASPICE, assessment, SWE.x, gap       |
| iso21434-tara      | cybersecurity, TARA, CAL, OTA attack |
| autosar-classic    | AUTOSAR, SWC, BSW, RTE, ARXML        |
| uds-diagnostics    | UDS, DTC, NRC, flash, diagnostic     |
| can-bus-analysis   | CAN, bus-off, error frame, DBC       |
| embedded-patterns  | embedded, RTOS, ISR, watchdog, mutex |
