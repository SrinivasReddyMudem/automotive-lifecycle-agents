# Architecture Reference — Automotive Lifecycle Agents

**Author: Srinivas Reddy Mudem**
Complete guide to every layer, what it contains, how layers connect,
what to modify when adding or changing something, and what to run.

---

## Table of contents

1. [System overview — two implementations](#1-system-overview)
2. [Shared foundation](#2-shared-foundation)
3. [md_agents layer map](#3-md_agents-layer-map)
4. [sdk_agents layer map](#4-sdk_agents-layer-map)
5. [Skills layer (shared)](#5-skills-layer)
6. [md_agents — agents in depth](#6-md_agents-agents)
7. [sdk_agents — core in depth](#7-sdk_agents-core)
8. [sdk_agents — 3-layer quality system](#8-3-layer-quality)
9. [sdk_agents — routing system](#9-routing-system)
10. [Python tools](#10-python-tools)
11. [Tests and CI/CD](#11-tests-and-cicd)
12. [Modification guide](#12-modification-guide)
13. [Commands reference](#13-commands-reference)

---

## 1. System overview

This project implements 13 automotive engineering AI agents in two ways.
Both read from the same 8 skills. Same domain knowledge — two enforcement mechanisms.

```
User describes an engineering problem in plain English
          │
          ├── md_agents path (Claude Code)
          │     Claude reads agent descriptions → picks best match →
          │     agent loads skills → produces structured response via prompt
          │
          └── sdk_agents path (Streamlit browser app)
                Weighted keyword scoring → routes to agent class →
                Groq API call with JSON Schema → Pydantic validation →
                semantic validators → structured UI output
```

**Key architectural difference:**
- `md_agents`: format enforcement via prompt instructions (model tries to comply)
- `sdk_agents`: format enforcement via `json_schema` API parameter (schema is contractual)

---

## 2. Shared foundation

```
automotive-lifecycle-agents/
│
├── skills/                     ← SHARED: 8 domain knowledge packs
│   ├── iso26262-hara/
│   ├── aspice-process/
│   ├── misra-c-2012/
│   ├── iso21434-tara/
│   ├── autosar-classic/
│   ├── uds-diagnostics/
│   ├── can-bus-analysis/
│   └── embedded-patterns/
│
├── tools/                      ← SHARED: Python CLI calculators (ASIL, CAL, ASPICE, Gate)
│
├── tests/                      ← Tests for Python tools (pytest, no API key)
│
├── md_agents/                  ← Implementation 1: Claude Code agents
│   ├── developer/
│   ├── tester/
│   ├── integrator/
│   └── project-lead/
│
├── sdk_agents/                 ← Implementation 2: Python SDK + Streamlit
│   ├── core/
│   ├── integrator/
│   ├── developer/
│   ├── tester/
│   └── project_lead/
│
└── .github/workflows/          ← 5 CI workflows (one badge per check type)
```

Skills are written once. `md_agents` loads them via Claude Code's `skills:` frontmatter
directive. `sdk_agents` loads them via `skill_loader.py` which reads the same files from
disk into the Groq system prompt. One source of truth — two consumers.

---

## 3. md_agents layer map

```
CLAUDE.md                       ← Global rules (always loaded first)
│  - 7 rules applying to every agent response
│  - Skill auto-loading table (documentation)
│  - /gate-review explicit-trigger requirement
│
skills/<name>/SKILL.md          ← Domain knowledge trigger + method overview
│  description: (keyword list)  ← Auto-routing trigger
│  references/                  ← Deep tables loaded when skill is active
│
md_agents/<role>/<name>.md      ← Agent behaviour
│  ---YAML frontmatter---
│  name:          unique id
│  description:   80+ word trigger (this IS the routing signal)
│  tools:         Claude Code permissions
│  skills:        reference packs this agent always loads
│  maxTurns:      5–15 based on task complexity
│  ---Markdown body---
│  ## Role
│  ## Response rules
│  ## Output format
│  ## Synthetic example
│
Interface: Claude Code chat tab (VS Code extension or CLI)
```

**How auto-routing works:**
When a user types a message, Claude Code reads ALL agent descriptions and picks the best
semantic match. The description IS the routing signal — a vague description means no routing.
Skills also auto-load when their trigger keywords appear, even without the agent listing them.

**gate-review-approver special rule:**
Has `disable-model-invocation: true` in frontmatter. Only activates on explicit `/gate-review`
command. Never auto-triggers. The CI `validate-agents` job checks this flag is always present.

---

## 4. sdk_agents layer map

```
sdk_agents/
│
├── core/
│   ├── base_agent.py           ← BaseAgent class
│   │     Groq API call with json_schema enforcement
│   │     _inline_schema(): resolves $ref → flat schema (required by Groq strict mode)
│   │     MAX_RETRIES = 2: retry on ValidationError or DomainCheckError
│   │     domain_feedback: on DomainCheckError, feeds failure reason back to model
│   │     Returns BaseModel or AgentError — never raises
│   │
│   ├── skill_loader.py         ← load_skill("name") → reads skills/ folder → string
│   │
│   ├── registry.py             ← Agent name + aliases → agent class (lazy imports)
│   │
│   ├── renderer.py             ← Pydantic model → Streamlit UI (safe_render wrapper)
│   │
│   └── logger.py               ← Raw API response logging to sdk_agents/logs/
│
├── <role>/<agent_name>/
│   ├── __init__.py             ← AgentClass(BaseAgent): get_schema(), get_prompt(), _validate_domain()
│   ├── prompt.py               ← AGENT_KNOWLEDGE string + load_skill() → get_system_prompt()
│   ├── schema.py               ← Pydantic v2 output model (all required fields)
│   └── validators.py           ← validate(output): domain-specific semantic checks
│
├── app.py                      ← Streamlit UI + AGENT_SCORES + RENDER_MAP
│   │   _NORMALIZATIONS (56 regex rules)
│   │   detect_agents() → weighted scoring → primary + secondaries
│
├── run.py                      ← CLI: python run.py --agent X --prompt "..."
│
└── test_routing.py             ← 40 single-agent + 7 multi-agent routing cases
```

**Interface:** Browser at `http://localhost:8501` after `streamlit run sdk_agents/app.py`

**Model:** `meta-llama/llama-4-scout-17b-16e-instruct` via Groq free tier

---

## 5. Skills layer

Each skill folder has two parts:

```
skills/<skill-name>/
├── SKILL.md              ← Frontmatter (name, description/trigger keywords) + content
└── references/           ← Deep reference files (tables, templates, worked examples)
    ├── <table>.md
    └── <template>.md
```

| Skill | Trigger keywords | Reference content |
|---|---|---|
| iso26262-hara | ASIL, HARA, safety goal, hazard | 64-entry S×E×C table, HARA template, safety goal format |
| aspice-process | ASPICE, assessment, SWE.x, gap | BP checklists SWE.1–6, assessor questions, gap template |
| misra-c-2012 | MISRA, rule violation, static analysis | Top 15 rules with compliant rewrites, deviation template |
| iso21434-tara | cybersecurity, TARA, CAL, OTA attack | CAL table, TARA template, STRIDE catalog, UN R155 |
| autosar-classic | AUTOSAR, SWC, BSW, RTE, ARXML | BSW module APIs, SWC patterns, composition ARXML |
| uds-diagnostics | UDS, DTC, NRC, flash, diagnostic | All service IDs 0x10–0x3E, NRC codes, flash sequence |
| can-bus-analysis | CAN, bus-off, error frame, TEC | Error type TEC/REC table, fault pattern table |
| embedded-patterns | embedded, RTOS, ISR, watchdog | RTOS patterns, interrupt handling, watchdog pattern |

**md_agents loads skills via:** `skills:` frontmatter list (Claude Code resolves at runtime)
**sdk_agents loads skills via:** `load_skill("name")` in prompt.py (reads files into string)

---

## 6. md_agents — agents in depth

### The 13 agents by role

```
md_agents/
├── developer/
│   ├── autosar-bsw-developer.md     maxTurns: 15  (design tasks)
│   ├── embedded-c-developer.md      maxTurns: 15
│   └── misra-reviewer.md            maxTurns: 6   (read-only)
│
├── tester/
│   ├── sw-unit-tester.md            maxTurns: 12
│   ├── sil-hil-test-planner.md      maxTurns: 10
│   └── regression-analyst.md        maxTurns: 6   (read-only)
│
├── integrator/
│   ├── can-bus-analyst.md           maxTurns: 6   (read-only)
│   ├── field-debug-fae.md           maxTurns: 8
│   └── sw-integrator.md             maxTurns: 12
│
└── project-lead/
    ├── safety-and-cyber-lead.md     maxTurns: 10  (read-only)
    ├── aspice-process-coach.md      maxTurns: 10  (read-only)
    ├── sw-project-lead.md           maxTurns: 12
    └── gate-review-approver.md      maxTurns: 5   (manual trigger only)
```

### YAML frontmatter rules

1. `name:` — unique, must match filename without `.md`
2. `description:` — 80+ words, keyword-rich — this IS the routing signal
3. `tools:` — minimum needed (misra-reviewer and can-bus-analyst are read-only)
4. `skills:` — skills this agent always loads (others may auto-load from keywords)
5. `maxTurns:` — 5–6 for read-only analysis, 12–15 for design/implementation
6. **Never add `model:` field** — hardcodes a version, breaks future updates
7. `gate-review-approver` must always have `disable-model-invocation: true`

---

## 7. sdk_agents — core in depth

### base_agent.py — the orchestrator

```python
class BaseAgent:
    def run(self, user_message: str) -> BaseModel | AgentError:
        # Loop MAX_RETRIES + 1 times
        for attempt in range(MAX_RETRIES + 1):
            try:
                raw = self._call_api(user_message, domain_feedback)
                parsed = self._parse(raw)          # Pydantic validation
                self._validate_domain(parsed)       # semantic checks
                return parsed                       # success
            except ValidationError:
                # retry (no feedback — likely transient)
            except DomainCheckError as e:
                # retry WITH feedback: model knows what to fix
                domain_feedback = f"Quality check failed: {e}. Fix this specific issue."
            except Exception:
                return AgentError(...)              # API error — return immediately

    def _inline_schema(self, schema):
        # Resolve all $ref to inline — required for Groq strict mode
        # Strip $defs, title, minItems, maxItems
        # Add "additionalProperties": false to every object

    def _call_api(self, user_message, domain_feedback=None):
        # Build messages: [system, user] + [domain_feedback if retry]
        # Call Groq with response_format: {type: json_schema, strict: True}
```

### _inline_schema — why it exists

Pydantic generates schemas with `$ref` references. Groq strict mode requires fully inlined
schemas (no `$ref` allowed). The method recursively substitutes every `$ref` with the full
definition from `$defs`, then removes `$defs`. Without this, every API call fails with
a schema error before any content is generated.

### registry.py — lazy imports

All 13 agent classes are imported inside `_get_registry()` (not at module level). This
means importing the registry module does not load any agents. Agents load only when
`get_agent("name")` is called. This keeps startup fast and avoids loading all 13 skill
files when only one agent will be used.

---

## 8. sdk_agents — 3-layer quality system

Every agent response passes through three validation layers before reaching the user:

```
Layer 1: API Schema Enforcement
  Groq json_schema strict=True
  ├── All required fields present?
  ├── Field types correct?
  └── No extra fields?
  → Fails → retry (ValidationError)

Layer 2: Pydantic Validation
  schema.model_validate_json(raw)
  ├── Literal constraints satisfied?    e.g. rank must be "HIGH"|"MEDIUM"|"LOW"
  ├── Type coercion issues?
  └── Nested model constraints?
  → Fails → retry (ValidationError)

Layer 3: Semantic Domain Validation
  validators.validate(parsed)
  ├── Content specificity checks        e.g. tec_math has ≥ 3 numbers
  ├── Domain value checks               e.g. autosar_layer is a known value
  ├── Length/completeness checks        e.g. test description ≥ 25 chars
  └── Self-evaluation evidence checks   e.g. PASS items have ≥ 15 char evidence
  → Fails → DomainCheckError
  → Retry with specific failure message fed back to model
```

The retry with feedback is the key innovation:
- `ValidationError` retry: clean attempt (transient schema issue)
- `DomainCheckError` retry: appends the failure reason to the messages array
  so the model knows exactly which field to fix and why

---

## 9. sdk_agents — routing system

### Step 1 — Normalization (56 regex rules)

```python
_NORMALIZATIONS = [
    (r"\bbus[\s_-]?off\b",      "bus-off"),          # "busoff", "bus_off", "bus off" → "bus-off"
    (r"\bhard[\s_]?fault\b",    "hard fault"),        # "hardfault", "hard_fault" → "hard fault"
    (r"\bunit[\s_]test(ing)?\b","unit test"),          # "unit testing" → "unit test"
    ...56 total rules...
]
```

### Step 2 — Weighted scoring

```python
AGENT_SCORES = {
    "can-bus-analyst": {
        "bus-off": 4,     # uniquely identifies this agent
        "error frame": 3, # strong signal
        "canoe": 2,       # shared signal
        "can": 1,         # weak corroborating evidence
    },
    ...
}
```

### Step 3 — Primary + secondary detection

```python
_MIN_ROUTE_SCORE = 3

def detect_agents(text):
    # Score all agents against normalized text
    # Pick primary = highest scorer above threshold
    # Secondary floor = max(3, min(best * 0.4, 7))
    # Return [primary] + [secondaries above floor]
```

The secondary floor cap at 7 prevents high-scoring primaries (score 20) from
requiring secondaries to also score 8+. This ensures genuinely overlapping
domains (ASPICE gap + MISRA violation, CAN bus-off + UDS session) are detected.

### What triggers multi-agent notification

The app shows "Multi-skill query detected. Also relevant: [agent names]" when
secondaries are detected. The user can switch agents in the sidebar to get each
perspective. Secondary agents are not run automatically — only the primary runs.

---

## 10. Python tools

Four standalone CLI calculators. No agent, no API key, no Claude needed.

| Tool | Standard | Inputs | Output |
|---|---|---|---|
| asil_calculator.py | ISO 26262-3 Table 4 | --severity S0-S3, --exposure E0-E4, --controllability C0-C3 | ASIL level |
| aspice_checker.py | ASPICE v3.1 | --phase SWE1-SWE6, --have "work_product_list" | Gap report with assessor risk |
| cal_calculator.py | ISO 21434 | --impact I1-I4, --feasibility AF1-AF4 | CAL level |
| gate_review_scorer.py | Project governance | --phase SOR/SOP, --criteria "key:status,..." | RAG score with blockers |

Tools implement the same tables as the skills reference files:

```
skills/iso26262-hara/references/asil-table.md  ←→  tools/asil_calculator.py (ASIL_TABLE dict)
skills/iso21434-tara/references/cal-table.md   ←→  tools/cal_calculator.py (CAL_TABLE dict)
```

**Rule:** If you update a table value in a reference file, update the tool lookup dict too.
The tests verify both are consistent.

---

## 11. Tests and CI/CD

### 5 CI workflows — one badge each

| Badge | Workflow | What it validates |
|---|---|---|
| Tests | tests.yml | 78 pytest cases for Python tools (asil, aspice, cal, gate) |
| Agents | validate-agents.yml | All 13 md_agents files: frontmatter, description length, gate-review flag |
| SDK | validate-sdk.yml | All 13 sdk agent imports, schemas, skill loader, routing (47 cases), unit tests, lint |
| Skills | validate-skills.yml | All 8 skill files present and correctly formatted |
| Lint | lint.yml | flake8 on tools/ and tests/ (root level) |

### validate-sdk.yml steps (no API key needed)

1. Import all 13 agent classes — catches structural/wiring errors
2. Validate all 13 Pydantic schemas — checks required fields present
3. Validate skill loader — all 8 skills load successfully with content > 100 chars
4. Run routing tests — 40 single-agent + 7 multi-agent routing cases
5. Run unit tests — pytest sdk_agents/tests/ (all API calls mocked)
6. Lint — flake8 with E501, E231 suppressed (intentional compact dict style)

### Test structure

```
tests/                           ← Python tool tests (root-level pytest)
│   test_asil_calculator.py      ← 20+ cases: all ASIL levels, invalid input
│   test_aspice_checker.py       ← gap detection, phase validation
│   └── test_cal_calculator.py   ← all CAL levels, table completeness

sdk_agents/tests/                ← sdk_agents unit tests (mocked)
└── integrator/
    └── test_can_bus_analyst.py  ← Schema (6), Validators (4), Skill loader (3), Agent (7)
```

---

## 12. Modification guide

### Add a new agent to sdk_agents

1. Create `sdk_agents/<role>/<agent_name>/` with 4 files: `__init__.py`, `prompt.py`, `schema.py`, `validators.py`
2. Schema: Pydantic v2 model, all fields required, include `self_evaluation: list[SelfEvaluationLine]`
3. Prompt: `AGENT_KNOWLEDGE` string + `get_system_prompt()` that calls `load_skill()`
4. Validators: `validate(output)` that raises `DomainCheckError` for weak content
5. `__init__.py`: class inheriting `BaseAgent`, override `get_schema()`, `get_prompt()`, `_validate_domain()`
6. Add to `core/registry.py`: canonical name + snake_case alias + short alias
7. Add to `AGENT_DISPLAY_NAMES` in registry.py
8. Add `render_<agent_name>()` to `core/renderer.py`
9. Add to `RENDER_MAP` in `app.py`
10. Add keyword scores to `AGENT_SCORES` in `app.py`
11. Add tests in `sdk_agents/tests/<role>/test_<agent_name>.py`
12. Add to schema validation list in `.github/workflows/validate-sdk.yml`

### Add a new agent to md_agents

1. Create `md_agents/<role>/<agent-name>.md`
2. YAML frontmatter: `name`, `description` (80+ words, keyword-rich), `tools`, `skills`, `maxTurns`
3. Agent body: Role, Response rules, Output format, Synthetic example
4. CI validate-agents checks the file automatically on push — no CI change needed

### Add a new skill

1. Create `skills/<skill-name>/SKILL.md` with frontmatter and content
2. Create `skills/<skill-name>/references/` with at least 2 reference files
3. Update `CLAUDE.md` routing table (md_agents documentation)
4. Update any agents that should auto-load this skill

### Modify the ASIL or CAL table

Three files must stay in sync:
1. `skills/<standard>/references/<table>.md` (human-readable reference)
2. `tools/<calculator>.py` — update the Python dict
3. `tests/test_<calculator>.py` — update expected values

Run `pytest tests/ -v` to verify all three are consistent.

---

## 13. Commands reference

### md_agents setup

```bash
# Install globally (agents available in all Claude Code sessions)
git clone https://github.com/SrinivasReddyMudem/automotive-lifecycle-agents ~/.claude

# Update
git -C ~/.claude pull
```

### sdk_agents setup

```bash
cd sdk_agents
pip install -r requirements.txt
cp .env.example .env
# Edit .env: GROQ_API_KEY=your-key  (free at console.groq.com, no credit card)

# Run Streamlit UI
streamlit run sdk_agents/app.py    # opens http://localhost:8501

# Run CLI
python run.py --agent can-bus-analyst --prompt "CAN node goes bus-off after 3 minutes"
```

### Python tools

```bash
python tools/asil_calculator.py --severity S3 --exposure E4 --controllability C2
python tools/aspice_checker.py --phase SWE4 --have "unit_test_spec,test_results"
python tools/cal_calculator.py --impact I3 --feasibility AF2
python tools/gate_review_scorer.py --phase SOP --criteria "test_complete:pass,traceability:partial"
```

### Testing

```bash
# All tests
pytest tests/ sdk_agents/tests/ -v

# Python tools only
pytest tests/ -v

# sdk_agents unit tests (no API key)
pytest sdk_agents/tests/ -v

# Routing test
python sdk_agents/test_routing.py

# Lint
flake8 sdk_agents/ --max-line-length 100 --extend-ignore=E501,E231 \
  --exclude=sdk_agents/logs,sdk_agents/.venv
flake8 tools/ tests/ --max-line-length 88
```
