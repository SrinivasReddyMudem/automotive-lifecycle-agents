"""
Standalone routing test — no Streamlit import needed.
Run: python sdk_agents/test_routing.py
"""
import re as _re

# ── Routing tables (must stay in sync with app.py) ─────────────────────────────
_NORMALIZATIONS = [
    (r"\bbus\s*off\b", "bus-off"), (r"\bcanbus\b", "can bus"),
    (r"\bcan[\s_-]fd\b", "can-fd"), (r"\bcandump\b", "candump"),
    (r"\bbabl(ing)?\b", "babbling"), (r"\bbit[\s_]tim(ing)?\b", "bit timing"),
    (r"\berror[\s_]counter\b", "error counter"), (r"\btec[\s_]counter\b", "tec counter"),
    (r"\brec[\s_]counter\b", "rec counter"),
    (r"\basil[\s_]([a-dA-D])\b", r"asil-\1"),
    (r"\bswe[\s_]?([1-6])\b", r"swe.\1"),
    (r"\bservice[\s_]?0?x?([0-9a-fA-F]{2})\b", r"service 0x\1"),
    (r"\bnrc[\s_]?0?x?([0-9a-fA-F]{2})\b", r"nrc"),
    (r"\bhard[\s_]fault\b", "hard fault"), (r"\bhardfault\b", "hard fault"),
    (r"\bstack[\s_]overflow\b", "stack overflow"),
    (r"\bmisra[\s_]c\b", "misra"), (r"\bmisra[\s]?c:?2012\b", "misra"),
    (r"\bautosar[\s_]classic\b", "autosar classic"),
    (r"\bp[\s_]port\b", "p-port"), (r"\br[\s_]port\b", "r-port"),
    (r"\bsender[\s_]receiver\b", "sender-receiver"), (r"\bclient[\s_]server\b", "client-server"),
    (r"\brte[\s_]generation[\s_]?(fail|error|issue)\b", "rte generation fail"),
    (r"\bport[\s_]not[\s_]connected\b", "port not connected"),
    (r"\bd[\s_]?space\b", "dspace"),
    (r"\bhardware[\s_]in[\s_]the[\s_]loop\b", "hardware in the loop"),
    (r"\bsoftware[\s_]in[\s_]the[\s_]loop\b", "software in the loop"),
    (r"\btest[\s_]bench\b", "test bench"),
    (r"\bunit[\s_]test(ing|s)?\b", "unit test"), (r"\bmc[\s_/]?dc\b", "mc/dc"),
    (r"\bboundary[\s_]value\b", "boundary value analysis"),
    (r"\bequivalence[\s_]part\w*\b", "equivalence partition"),
    (r"\bchange[\s_]request\b", "change request"), (r"\bschedule[\s_]impact\b", "schedule impact"),
    (r"\brisk[\s_]register\b", "risk register"), (r"\biso[\s_]?26262\b", "iso 26262"),
    (r"\biso[\s_]?21434\b", "iso 21434"), (r"\bsafety[\s_]goal\b", "safety goal"),
    (r"\bhazardous[\s_]event\b", "hazardous event"),
    (r"\bgap[\s_]analysis\b", "gap analysis"), (r"\bprocess[\s_]area\b", "process area"),
    (r"\bwork[\s_]product\b", "work product"), (r"\btest[\s_]delta\b", "test delta"),
    (r"\bbaseline[\s_]comp\w*\b", "baseline comparison"), (r"\bpass[\s_]rate\b", "pass rate"),
    (r"\bflaky[\s_]test\b", "flaky test"), (r"\bgate[\s_]review\b", "gate review"),
    (r"\bgo[\s_/]no[\s_/]go\b", "go/no-go"), (r"\bsop[\s_]readiness\b", "sop readiness"),
    (r"\bdiagnostic[\s_]trouble[\s_]code\b", "dtc"),
    (r"\bnegative[\s_]response\b", "negative response"),
    (r"\bfreeze[\s_]frame\b", "freeze frame"),
    (r"\bfailures\b", "failure"), (r"\btests\b", "test"), (r"\bhazards\b", "hazard"),
]

AGENT_SCORES = {
    "can-bus-analyst": {
        "bus-off":4,"babbling idiot":4,"candump":4,"error counter":4,"tec counter":4,
        "rec counter":4,"bit stuffing":4,"error passive":4,"error active":4,
        "oscilloscope can":4,"can-fd":3,"error frame":3,"bit timing":3,"can trace":3,
        "120 ohm":3,"can matrix":3,"dbc file":3,"canalyzer":3,"canoe":2,"can node":2,
        "baud rate":2,"termination":2,"transceiver":2,"can bus":2,"bus load":2,
        "can high":2,"can low":2,"tec":1,"rec":1,"can":1,
    },
    "field-debug-fae": {
        "nrc":4,"negative response code":4,"conditionsnotcorrect":4,"securityaccessdenied":4,
        "requestoutofrange":4,"freeze frame":4,"dtc status byte":4,"seed key":4,
        "service 0x27":4,"service 0x22":4,"customer says":4,"customer reports":4,
        "service 0x10":3,"service 0x19":3,"security access":3,"programming session":3,
        "extended session":3,"flash programming":3,"uds session":3,"ecu not responding":3,
        "negative response":3,"workshop":3,"vehicle complaint":3,"field return":3,
        "field failure":3,"won't start":3,"warning light":2,
        "tester present":2,"dtc":2,"fault code":2,"diagnostic session":2,
        "field issue":2,"customer complaint":2,"0x22":2,"0x31":2,"diagnostic":1,
    },
    "sw-integrator": {
        "port not connected":4,"rte generation fail":4,"rte generation error":4,
        "linker error":4,"memory map conflict":4,"bsw wiring":4,
        "port prototype mismatch":4,"arxml error":4,"composition error":4,
        "rte inconsistency":4,"integration issue":3,"build error":3,
        "integration plan":3,"sw baseline":3,"delivery package":3,
        "bsw module version":3,"undefined reference":3,"integration test":2,"build system":2,
        "cmake":2,"makefile":2,"integration":1,
    },
    "autosar-bsw-developer": {
        "arxml":4,"p-port":4,"r-port":4,"rte api":4,"rte_read":4,"rte_write":4,
        "rte_call":4,"davinci":4,"eb tresos":4,"runnable entity":4,
        "sender-receiver":4,"client-server":4,"bsw configuration":4,
        "software component type":4,"autosar classic":3,"bsw module":3,"swc design":3,
        "composition swc":3,"port interface":3,"data element":3,
        "autosar r4":3,"autosar r22":3,"swc port":3,
        "autosar":2,"swc":2,"runnable":2,"bsw":2,"rte":1,
    },
    "embedded-c-developer": {
        "cfsr":4,"hard fault":4,"stack overflow":4,"mpu fault":4,"hardfault":4,
        "nvic":4,"memory barrier":4,"cortex-m":4,"cortex-r":4,"bare metal":4,
        "isr":3,"watchdog reset":3,"dma transfer":3,"volatile":3,"freertos":3,
        "context switch":3,"linker script":3,"startup code":3,"stack depth":3,
        "interrupt priority":3,"mutex":2,"semaphore":2,"rtos":2,"watchdog":2,
        "interrupt":2,"embedded c":2,"microcontroller":2,"cortex":2,"embedded":1,
    },
    "misra-reviewer": {
        "misra":4,"misra c":4,"misra c:2012":4,"polyspace":4,"qac":4,"pc-lint":4,
        "coverity":4,"deviation justification":4,"compliant rewrite":4,
        "mandatory rule":4,"required rule":4,"advisory rule":4,
        "rule violation":3,"static analysis finding":3,"deviation request":3,
        "coding standard":3,"dead code":2,"undefined behaviour":2,
        "implicit cast":2,"static analysis":2,"deviation":1,
    },
    "aspice-process-coach": {
        "aspice":4,"automotive spice":4,"swe.1":4,"swe.2":4,"swe.3":4,
        "swe.4":4,"swe.5":4,"swe.6":4,"pa 2.1":4,"pa 2.2":4,
        "capability level":4,"process area":4,"gap analysis":3,
        "work product missing":3,"base practice":3,"major finding":3,
        "minor finding":3,"assessment":3,"aspice level":3,
        "process attribute":3,"traceability matrix":3,
        "review record":2,"baseline freeze":2,"work product":2,
        "process compliance":2,"audit":2,
    },
    "gate-review-approver": {
        "gate review":4,"go/no-go":4,"sop readiness":4,"sor readiness":4,
        "release gate":4,"formal release approval":4,"gate decision":4,
        "gate criteria":3,"release approval":3,"milestone gate":3,
        "release readiness":3,"gate":2,
    },
    "safety-and-cyber-lead": {
        "hara":4,"hazardous event":4,"tara":4,"iso 26262":4,"iso 21434":4,
        "asil-d":4,"asil-c":4,"cybersecurity goal":4,"attack feasibility":4,
        "ftti":4,"damage scenario":4,"safety goal":3,"threat scenario":3,
        "controllability":3,"severity":3,"exposure":3,"unece r155":3,"cal-":3,
        "asil-b":2,"asil-a":2,"asil":2,"functional safety":2,"safe state":2,
        "safety mechanism":2,"hazard":2,"cybersecurity":2,"safety":1,
    },
    "sw-project-lead": {
        "change request":4,"cr impact":4,"schedule impact":4,
        "ota update requirement":4,"scope change":4,"statement of work":4,
        "risk register":3,"milestone delay":3,"resource plan":3,
        "schedule delta":3,"feasibility study":3,"project risk":3,
        "stakeholder":2,"milestone":2,"project plan":2,"nre":2,
        "schedule":1,"project":1,
    },
    "regression-analyst": {
        "regression analysis":4,"test delta":4,"baseline comparison":4,
        "new test failures":4,"pass rate dropped":4,"pass rate change":4,
        "flaky test":4,"test comparison":4,"test instability":3,
        "coverage decreased":3,"test history":3,"failed tests after change":3,
        "new failures":3,"tests failed":2,"test report":2,
        "regression":2,"test failures":2,"test failure":3,"baseline":2,
    },
    "sil-hil-test-planner": {
        "hardware in the loop":4,"software in the loop":4,"dspace":4,
        "scalexio":4,"microautobox":4,"hil rack":4,"test bench setup":4,
        "fault injection test":4,"plant model":4,"canoe capl":3,
        "hil test":3,"sil test":3,"test environment":3,
        "ni teststand":3,"automation framework":3,"test bench":3,
        "hil":2,"sil":2,"test plan":2,
    },
    "sw-unit-tester": {
        "mc/dc":4,"mcdc":4,"modified condition decision":4,
        "equivalence partition":4,"boundary value analysis":4,
        "googletest":4,"unity test":4,"vectorcast":4,"ldra":4,"cpputest":4,
        "test case design":4,"stub function":4,"independence pair":4,
        "unit test":3,"branch coverage":3,"statement coverage":3,
        "function under test":3,"test harness":3,"mock":2,
        "test coverage":2,"unit tester":2,"stub":2,
    },
}
_MIN_ROUTE_SCORE = 3


def _normalize(text: str) -> str:
    s = text.lower()
    for pattern, replacement in _NORMALIZATIONS:
        s = _re.sub(pattern, replacement, s)
    return s


def detect_agents(text: str) -> list:
    """
    Return ranked list of relevant agents.
    Primary:     highest scorer above _MIN_ROUTE_SCORE.
    Secondaries: score >= 60% of primary AND >= _MIN_ROUTE_SCORE.
    """
    normalized = _normalize(text)
    scores = {}
    for agent, kw_map in AGENT_SCORES.items():
        total = sum(w for kw, w in kw_map.items() if kw in normalized)
        if total > 0:
            scores[agent] = total
    if not scores:
        return []
    best = max(scores.values())
    if best < _MIN_ROUTE_SCORE:
        return []
    top = [a for a, s in scores.items() if s == best]
    primary = max(top, key=lambda a: max(AGENT_SCORES[a].values()))
    secondary_floor = max(_MIN_ROUTE_SCORE, min(best * 0.4, 7))
    secondaries = [
        a for a, s in sorted(scores.items(), key=lambda x: -x[1])
        if a != primary and s >= secondary_floor
    ]
    return [primary] + secondaries


def auto_detect_agent(text: str):
    agents = detect_agents(text)
    return agents[0] if agents else None


# ── Test cases ─────────────────────────────────────────────────────────────────
CASES = [
    # Clean professional inputs
    ("CAN node goes bus-off after 3 minutes only when engine running",    "can-bus-analyst"),
    ("ECU returns NRC 0x22 on service 0x27 in extended session only",     "field-debug-fae"),
    ("RTE generation fails port not connected after adding SWC",          "sw-integrator"),
    ("Write unit tests for saturating adder ASIL-B MC/DC coverage",       "sw-unit-tester"),
    ("Polyspace flagged MISRA Rule 11.3 cast pointer in CAN driver",      "misra-reviewer"),
    ("ASPICE assessment in 3 weeks SWE.4 unit test work product gaps",    "aspice-process-coach"),
    ("HARA for emergency braking loss of braking ASIL-D safety goal",     "safety-and-cyber-lead"),
    ("Customer OTA update requirement schedule impact change request",     "sw-project-lead"),
    ("Hard fault on Cortex-M4 CFSR 0x00000400 after 2 hours runtime",    "embedded-c-developer"),
    ("Design sender-receiver SWC AUTOSAR Classic ARXML port interface",   "autosar-bsw-developer"),
    ("After SW baseline 2.4 regression 14 test failures ASIL-D",         "regression-analyst"),
    ("Plan SIL HIL test using dSPACE SCALEXIO for ASIL-B function",      "sil-hil-test-planner"),
    ("Gate review go/no-go SOP readiness software release decision",      "gate-review-approver"),
    # Typos and natural language variants
    ("can busoff happening every 3 minutes node only",                    "can-bus-analyst"),
    ("ecu giving nrc22 on service27 security access rejected",            "field-debug-fae"),
    ("rte generation error port not conected after adding vehicle speed",  "sw-integrator"),
    ("unit testing with mcdc and boundary value for adder function",      "sw-unit-tester"),
    ("polyspace misra c2012 rule violation rule 11.3 pointer cast",       "misra-reviewer"),
    ("aspice asessment swe4 gaps process area work product missing",      "aspice-process-coach"),
    ("ASIL D safety goal hazardous event braking loss highway speed",     "safety-and-cyber-lead"),
    ("change request at milestone 3 schedule impacted OTA feature added", "sw-project-lead"),
    ("hardfault cortex m4 cfsr register dump after runtime",              "embedded-c-developer"),
    ("sender receiver arxml autosar classic runnable design",             "autosar-bsw-developer"),
    ("regression analysis test failures after baseline comparison",       "regression-analyst"),
    ("HIL test dspace hardware in the loop test bench setup",             "sil-hil-test-planner"),
    # Ambiguous / weak signals — should still route correctly via accumulated score
    ("TEC counter climbing every time engine runs CAN trace shows errors", "can-bus-analyst"),
    ("NRC 0x31 requestOutOfRange on flash routine control",               "field-debug-fae"),
    ("linker error undefined reference BSW module missing",               "sw-integrator"),
    ("branch coverage ASIL-B function stub needed for RTE call",         "sw-unit-tester"),
    ("MISRA deviation request for Rule 14.3 dead code in timer ISR",     "misra-reviewer"),
    ("major finding gap analysis capability level 2 ASPICE audit",       "aspice-process-coach"),
    ("ISO 26262 ASIL-C severity controllability hazard analysis",         "safety-and-cyber-lead"),
    ("project risk register resource plan milestone delay stakeholder",   "sw-project-lead"),
    ("stack overflow on FreeRTOS task after DMA transfer callback",       "embedded-c-developer"),
    ("RTE_Read RTE_Write ARXML port interface BSW configuration",         "autosar-bsw-developer"),
    ("pass rate dropped after merge flaky test in test report",           "regression-analyst"),
    ("fault injection test dSPACE plant model HIL environment",          "sil-hil-test-planner"),
    # Customer complaint language — plain English, no engineering terms
    ("Customer says door not unlocking. Car is at the workshop now.",    "field-debug-fae"),
    ("Customer reports warning light on dashboard, vehicle at workshop", "field-debug-fae"),
    ("customer says car won't start, field return from customer site",   "field-debug-fae"),
]

# ── Multi-agent test cases ──────────────────────────────────────────────────────
# Each entry: (prompt, expected_primary, [expected_secondaries_subset])
# expected_secondaries_subset: every agent listed here MUST appear in the returned list.
MULTI_CASES = [
    # CAN bus-off + UDS diagnostic session simultaneously
    # NRC/UDS signals are stronger (nrc=4, service0x27=4, extended session=3) so
    # field-debug-fae is correctly primary; can-bus-analyst is the secondary concern
    (
        "CAN node goes bus-off and ECU returns NRC 0x22 on service 0x27 during extended session",
        "field-debug-fae",
        ["can-bus-analyst"],
    ),
    # ASPICE assessment gap + MISRA violations in the code under review
    (
        "ASPICE assessment SWE.4 gap — unit test work products missing and Polyspace "
        "flagging MISRA rule violations in the module under test",
        "aspice-process-coach",
        ["misra-reviewer"],
    ),
    # Safety HARA + cybersecurity TARA for OTA update
    (
        "Perform HARA and TARA for OTA update function — ASIL-D safety goal and "
        "cybersecurity CAL-3 attack feasibility needed",
        "safety-and-cyber-lead",
        [],  # single agent covers both ISO 26262 and ISO 21434
    ),
    # AUTOSAR SWC design triggers MISRA concern about generated RTE code
    (
        "Design AUTOSAR Classic sender-receiver SWC ARXML and check if RTE generated "
        "code has MISRA rule violations in the Rte_Read function",
        "autosar-bsw-developer",
        ["misra-reviewer"],
    ),
    # Regression report with ASIL-D coverage concern → regression + unit-tester both needed
    (
        "After baseline 2.4 regression 14 test failures and branch coverage dropped "
        "below MC/DC target for ASIL-D functions — should we release?",
        "regression-analyst",
        ["sw-unit-tester"],
    ),
    # SIL/HIL test plan also needs ASPICE evidence for SWE.5
    (
        "Plan HIL test using dSPACE SCALEXIO for ASIL-B function and document "
        "ASPICE SWE.5 test specification work product",
        "sil-hil-test-planner",
        ["aspice-process-coach"],
    ),
    # Hard fault in embedded code + MISRA violation in the ISR
    (
        "Hard fault on Cortex-M4 CFSR 0x00000400 in DMA ISR, same ISR flagged by "
        "Polyspace for MISRA rule violation in pointer cast",
        "embedded-c-developer",
        ["misra-reviewer"],
    ),
]


if __name__ == "__main__":
    # ── Single-agent routing test ────────────────────────────────────────────────
    print("=" * 72)
    print("SINGLE-AGENT ROUTING  (37 cases)")
    print("=" * 72)
    ok = fail = 0
    for prompt, expected in CASES:
        result = auto_detect_agent(prompt)
        if result == expected:
            ok += 1
            print(f"  OK   {result:<26} | {prompt[:60]}")
        else:
            fail += 1
            print(f"  FAIL {str(result):<26} want={expected} | {prompt[:60]}")
    print(f"\n{ok}/{len(CASES)} correct  ({fail} failed)")

    # ── Multi-agent routing test ─────────────────────────────────────────────────
    print()
    print("=" * 72)
    print("MULTI-AGENT ROUTING  (overlapping domain queries)")
    print("=" * 72)
    mok = mfail = 0
    for prompt, exp_primary, exp_secondaries in MULTI_CASES:
        detected = detect_agents(prompt)
        primary = detected[0] if detected else None
        primary_ok = primary == exp_primary
        missing = [s for s in exp_secondaries if s not in detected]
        if primary_ok and not missing:
            mok += 1
            extra = detected[1:]
            extra_str = f"  secondaries={extra}" if extra else ""
            print(f"  OK   primary={primary:<26}{extra_str} | {prompt[:55]}")
        else:
            mfail += 1
            if not primary_ok:
                print(f"  FAIL primary={str(primary):<26} want={exp_primary} | {prompt[:55]}")
            if missing:
                print(f"  FAIL secondary missing={missing} | {prompt[:55]}")
    print(f"\n{mok}/{len(MULTI_CASES)} correct  ({mfail} failed)")
