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

## Pre-change validation — mandatory before every commit

Before touching any file, automatically run all of these. No exceptions.

### 1. Identify dependencies first
- `grep -rn "from.*<module>" sdk_agents/` — find every file that imports what you are changing
- For `renderer.py` changes: affects all 13 agents — check every render function
- For `validators.py` changes: grep other agents for the same validator pattern
- For `schema.py` changes: verify renderer fields match new schema fields exactly
- For `prompt.py` changes: verify prompt examples meet the validator minimums for that agent

### 2. Mandatory checks before commit

```bash
# 1. All tests pass
python -m pytest sdk_agents/tests/ -q

# 2. All imports load cleanly
python -c "from sdk_agents.core.renderer import render_safe; print('renderer OK')"
python -c "from sdk_agents.core.base_agent import BaseAgent; print('base_agent OK')"

# 3. Prompt length within safe bounds (warn if > 20000 chars)
python -c "
from sdk_agents.<group>.<agent>.prompt import get_system_prompt
p = get_system_prompt()
print(f'{len(p)} chars / ~{len(p)//4} tokens')
assert len(p) < 25000, 'PROMPT TOO LONG — model may fail to produce valid JSON'
"

# 4. Renderer field alignment — for any agent touched
# Check every field accessed in render_<agent>() exists in <Agent>Output schema
# Fields must use getattr(output, 'field', None) — never output.field directly
```

### 3. Renderer rules — enforced on every renderer change
- Every `render_<agent>` function MUST start with AgentError guard via `type(output).__name__`
- Every field access MUST use `getattr(output, 'field', None)` — never `output.field` directly
- No field access is unconditional — always guard with `if value:` before rendering

### 4. Validator-prompt alignment — enforced on every prompt or validator change
- Every example in the prompt must meet the minimum length set in the validator
- If validator sets `MIN_CRITERIA_LENGTH = 12`, every example in the prompt must be ≥ 12 chars
- Run: `grep "MIN_\|minimum" sdk_agents/<group>/<agent>/validators.py` and verify against prompt examples

### 5. Cross-agent impact
- `shared_schema.py` changes: all agents using shared fields must be re-verified
- `renderer.py` changes: run full pytest + check render functions for all agents in the changed section
- `base_agent.py` changes: all agents affected — run full test suite + import check for every agent

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
