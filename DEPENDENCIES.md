# Dependency Map

Single source of truth for file dependencies.
When touching any file, look up its entry here — verify everything listed under **must verify**.
When adding a new agent or file, update this map before merging.

---

## Core files — highest impact

### `sdk_agents/core/base_agent.py`
**Depended on by:** every agent `__init__.py`, every `validators.py` (DomainCheckError), `renderer.py` (AgentError), `app.py`, `run.py`
**Must verify:**
- `python -m pytest sdk_agents/tests/ -q` (full suite)
- Import check: `python -c "from sdk_agents.core.base_agent import BaseAgent, AgentError; print('OK')"`
- Verify `AgentError` fields match `type(output).__name__` checks in `renderer.py`

---

### `sdk_agents/core/renderer.py`
**Depended on by:** `app.py` (imports all render functions), affects output of all 13 agents
**Must verify:**
- `python -m pytest sdk_agents/tests/ -q`
- Every `render_<agent>` function has `type(output).__name__ == "AgentError"` guard at top
- Every field access uses `getattr(output, 'field', None)` — no bare `output.field`
- Fields accessed in each render function exist in the corresponding schema:

| Render function | Schema to cross-check |
|---|---|
| `render_can_bus_analyst` | `can_bus_analyst/schema.py` — CanBusAnalystOutput |
| `render_field_debug_fae` | `field_debug_fae/schema.py` — FieldDebugFAEOutput |
| `render_sw_integrator` | `sw_integrator/schema.py` — SwIntegratorOutput |
| `render_autosar_bsw_developer` | `autosar_bsw_developer/schema.py` |
| `render_embedded_c_developer` | `embedded_c_developer/schema.py` |
| `render_misra_reviewer` | `misra_reviewer/schema.py` |
| `render_aspice_process_coach` | `aspice_process_coach/schema.py` |
| `render_safety_and_cyber_lead` | `safety_and_cyber_lead/schema.py` |
| `render_sw_project_lead` | `sw_project_lead/schema.py` — no `long_term_actions` |
| `render_regression_analyst` | `regression_analyst/schema.py` |
| `render_sil_hil_test_planner` | `sil_hil_test_planner/schema.py` |
| `render_sw_unit_tester` | `sw_unit_tester/schema.py` |
| `render_gate_review_approver` | `gate_review_approver/schema.py` |

---

### `sdk_agents/core/shared_schema.py`
**Depended on by:** all 13 agent `schema.py` files (imports ProbableCause, NarrowingQuestion, SelfEvaluationLine, ToolSelection, ProtocolDetection, DataSufficiency, InputAnalysis, DiagnosisBasisLine)
**Must verify:**
- `python -m pytest sdk_agents/tests/ -q`
- Import check for every agent schema:
  ```bash
  python -c "
  from sdk_agents.integrator.can_bus_analyst.schema import CanBusAnalystOutput
  from sdk_agents.integrator.field_debug_fae.schema import FieldDebugFAEOutput
  from sdk_agents.integrator.sw_integrator.schema import SwIntegratorOutput
  from sdk_agents.developer.autosar_bsw_developer.schema import AutosarBswDeveloperOutput
  from sdk_agents.developer.embedded_c_developer.schema import EmbeddedCDeveloperOutput
  from sdk_agents.developer.misra_reviewer.schema import MisraReviewerOutput
  from sdk_agents.project_lead.aspice_process_coach.schema import AspiceProcessCoachOutput
  from sdk_agents.project_lead.safety_and_cyber_lead.schema import SafetyAndCyberLeadOutput
  from sdk_agents.project_lead.sw_project_lead.schema import SwProjectLeadOutput
  from sdk_agents.project_lead.gate_review_approver.schema import GateReviewApproverOutput
  print('all schemas OK')
  "
  ```

---

### `sdk_agents/core/skill_loader.py`
**Depended on by:** all agent `prompt.py` files
**Must verify:**
- `python -c "from sdk_agents.core.skill_loader import load_skill, load_skills; print('OK')"`
- Import all prompts: `python -c "from sdk_agents.integrator.can_bus_analyst.prompt import get_system_prompt; print(len(get_system_prompt()))"`

---

## Per-agent files — isolated impact

For each agent, the dependency chain is:
```
schema.py → validators.py (imports schema types)
schema.py → renderer.py (field names must match)
prompt.py → validators.py (examples must meet validator minimums)
prompt.py → skill_loader.py (loads skills)
```

### When touching any agent's `schema.py`
1. Check `validators.py` still imports correctly
2. Check `renderer.py` render function — every accessed field still exists in schema
3. Run: `python -m pytest sdk_agents/tests/ -q`

### When touching any agent's `validators.py`
1. Check validator minimums against prompt examples:
   - `grep "MIN_" sdk_agents/<group>/<agent>/validators.py`
   - Verify every prompt BAD/GOOD example meets the minimum length
2. Run: `python -m pytest sdk_agents/tests/<group>/test_<agent>.py -v`

### When touching any agent's `prompt.py`
1. Check prompt length: must stay under 25,000 chars
   ```bash
   python -c "from sdk_agents.<group>.<agent>.prompt import get_system_prompt; p=get_system_prompt(); print(len(p), 'chars'); assert len(p)<25000"
   ```
2. Verify examples in prompt meet validator minimums for that agent
3. Run: `python -m pytest sdk_agents/tests/ -q`

---

## Agent registry

| Agent | Group | Schema class | Render function | Test file |
|---|---|---|---|---|
| can-bus-analyst | integrator | CanBusAnalystOutput | render_can_bus_analyst | tests/integrator/test_can_bus_analyst.py |
| field-debug-fae | integrator | FieldDebugFAEOutput | render_field_debug_fae | tests/integrator/test_field_debug_fae.py |
| sw-integrator | integrator | SwIntegratorOutput | render_sw_integrator | tests/integrator/test_sw_integrator.py |
| autosar-bsw-developer | developer | AutosarBswDeveloperOutput | render_autosar_bsw_developer | tests/developer/test_autosar_bsw_developer.py |
| embedded-c-developer | developer | EmbeddedCDeveloperOutput | render_embedded_c_developer | tests/developer/test_embedded_c_developer.py |
| misra-reviewer | developer | MisraReviewerOutput | render_misra_reviewer | tests/developer/test_misra_reviewer.py |
| aspice-process-coach | project_lead | AspiceProcessCoachOutput | render_aspice_process_coach | tests/project_lead/test_aspice_process_coach.py |
| safety-and-cyber-lead | project_lead | SafetyAndCyberLeadOutput | render_safety_and_cyber_lead | tests/project_lead/test_safety_and_cyber_lead.py |
| sw-project-lead | project_lead | SwProjectLeadOutput | render_sw_project_lead | tests/project_lead/test_sw_project_lead.py |
| regression-analyst | tester | RegressionAnalystOutput | render_regression_analyst | tests/tester/test_regression_analyst.py |
| sil-hil-test-planner | tester | SilHilTestPlannerOutput | render_sil_hil_test_planner | tests/tester/test_sil_hil_test_planner.py |
| sw-unit-tester | tester | SwUnitTesterOutput | render_sw_unit_tester | tests/tester/test_sw_unit_tester.py |
| gate-review-approver | project_lead | GateReviewApproverOutput | render_gate_review_approver | tests/project_lead/test_gate_review_approver.py |

---

## Adding a new agent — checklist

1. Create `schema.py`, `prompt.py`, `validators.py`, `__init__.py` in the correct group folder
2. Add render function to `core/renderer.py` — with AgentError guard and getattr on all fields
3. Register in `core/registry.py` and `app.py`
4. Add test file to `sdk_agents/tests/<group>/test_<agent>.py`
5. **Add entry to this DEPENDENCIES.md** — agent registry table + schema/render cross-check row
6. Run full validation: `python -m pytest sdk_agents/tests/ -q`
