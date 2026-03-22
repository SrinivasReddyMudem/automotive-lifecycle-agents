#!/usr/bin/env python3
"""
Gate Review Scorer — SOR and SOP readiness assessment tool.

Author: Srinivas Reddy M
Project: Automotive Lifecycle Agents


Scores release gate criteria and produces a RAG readiness status.
Supports SOR (Start of Release) and SOP (Start of Production) phases.

Usage:
    python tools/gate_review_scorer.py \\
        --phase SOP \\
        --criteria "test_complete:pass,traceability:partial,safety_plan:pass,\\
        cm_baselines:fail,open_issues:partial"
    python tools/gate_review_scorer.py --phase SOR --interactive
    python tools/gate_review_scorer.py --list-criteria SOP

Status values: pass | partial | fail
"""

import argparse
import sys

# ---------------------------------------------------------------------------
# Gate criteria definitions per phase
# Each entry: (criterion_id, display_name, weight, description)
# Weight: critical=3, important=2, advisory=1
# ---------------------------------------------------------------------------
GATE_CRITERIA = {
    "SOR": [
        ("requirements_freeze", "SW Requirements Freeze", 3,
         "SRS approved and change freeze in effect"),
        ("safety_plan_signed", "Safety Plan Signed", 3,
         "Functional safety plan reviewed and signed by safety manager"),
        ("aspice_swe1_swe3", "ASPICE SWE.1-3 Work Products", 2,
         "SRS, SAD, detailed design present and under CM"),
        ("architecture_approved", "Architecture (SAD) Approved", 2,
         "SAD reviewed, approved, and baselined"),
        ("integration_plan", "Integration Plan Available", 2,
         "SWE.5 integration plan documented"),
        ("resource_commitment", "Resource Commitment Confirmed", 1,
         "Development team allocation confirmed for project schedule"),
    ],
    "SOP": [
        ("test_complete", "All Tests Completed and Signed Off", 3,
         "SWQT results approved; zero P1 open failures"),
        ("traceability", "Traceability Complete", 3,
         "Full SRS-to-test coverage documented and reviewed"),
        ("safety_plan", "Safety Plan/Case Closed", 3,
         "Safety case complete; all safety goals verified"),
        ("cm_baselines", "CM Baselines Recorded", 3,
         "Release candidate SW baselined in CM system"),
        ("aspice_evidence", "ASPICE Evidence Complete", 2,
         "All SWE.1-6 work products present and approved"),
        ("open_issues", "Open Issues Classified", 2,
         "All open findings classified with risk assessment"),
        ("cybersecurity_plan", "Cybersecurity Plan Complete", 2,
         "Cybersecurity activities complete per project plan"),
        ("customer_signoff", "Customer Sign-off Received", 1,
         "OEM or internal customer review complete"),
    ],
}

STATUS_SCORE = {
    "pass": 1.0,
    "partial": 0.5,
    "fail": 0.0,
}

STATUS_SYMBOL = {
    "pass": "PASS    ",
    "partial": "PARTIAL ",
    "fail": "FAIL    ",
}


def score_criteria(phase: str, criteria_input: dict) -> dict:
    """
    Score criteria for a phase against provided statuses.
    Returns dict with score details.
    """
    phase_key = phase.upper()
    if phase_key not in GATE_CRITERIA:
        raise ValueError(
            f"Unknown phase '{phase}'. Valid phases: {sorted(GATE_CRITERIA.keys())}"
        )

    criteria_defs = GATE_CRITERIA[phase_key]
    results = []
    total_weighted_score = 0.0
    total_weight = 0
    critical_fails = []

    for crit_id, name, weight, desc in criteria_defs:
        raw_status = criteria_input.get(crit_id, "").lower().strip()

        if raw_status not in STATUS_SCORE:
            if raw_status == "":
                status = "fail"
                was_provided = False
            else:
                raise ValueError(
                    f"Invalid status '{raw_status}' for criterion '{crit_id}'. "
                    f"Valid values: pass, partial, fail"
                )
        else:
            status = raw_status
            was_provided = True

        score = STATUS_SCORE[status]
        weighted = score * weight
        total_weighted_score += weighted
        total_weight += weight

        if status == "fail" and weight == 3:
            critical_fails.append(name)

        results.append({
            "id": crit_id,
            "name": name,
            "weight": weight,
            "status": status,
            "score": score,
            "weighted": weighted,
            "provided": was_provided,
        })

    overall_pct = (total_weighted_score / total_weight * 100) if total_weight > 0 else 0.0

    if overall_pct >= 85 and not critical_fails:
        rag = "GREEN"
        recommendation = "Proceed to gate review meeting with documented evidence."
    elif overall_pct >= 60 or (critical_fails and len(critical_fails) <= 1):
        rag = "AMBER"
        recommendation = "Address critical findings before gate review meeting."
    else:
        rag = "RED"
        recommendation = "Gate review should not proceed. Address all critical failures first."

    return {
        "phase": phase_key,
        "results": results,
        "overall_pct": overall_pct,
        "rag": rag,
        "critical_fails": critical_fails,
        "recommendation": recommendation,
    }


def print_score_report(report: dict) -> None:
    """Print formatted gate review score report."""
    sep = "─" * 55

    print(f"\nGATE REVIEW SCORER — {report['phase']}")
    print(sep)

    for item in report["results"]:
        bar_filled = int(item["score"] * 10)
        bar = "█" * bar_filled + "░" * (10 - bar_filled)
        pct = int(item["score"] * 100)
        weight_str = f"[W:{item['weight']}]"
        status_str = STATUS_SYMBOL.get(item["status"], item["status"])
        print(
            f"  {item['name']:<35} {status_str} {bar} {pct:3d}% {weight_str}"
        )

    print(sep)
    print(f"  Overall score: {report['overall_pct']:.0f}%   Status: {report['rag']}")
    print(sep)

    if report["critical_fails"]:
        print()
        print("  Critical findings (weight=3 failures):")
        for fail in report["critical_fails"]:
            print(f"    FAIL  {fail}")

    print()
    print(f"  Recommendation: {report['recommendation']}")
    print()
    print("  NOTE: This tool does not constitute a formal release approval.")
    print("  Final gate decision requires sign-off by SW Project Lead,")
    print("  Quality Manager, and Functional Safety Manager per project procedure.")
    print(sep)


def interactive_mode(phase: str) -> None:
    """Prompt user for criterion status values interactively."""
    phase_key = phase.upper()
    if phase_key not in GATE_CRITERIA:
        raise ValueError(f"Unknown phase '{phase}'.")

    print(f"Gate Review Scorer — {phase_key} Interactive Mode")
    print("─" * 45)
    print("Enter status for each criterion: pass / partial / fail")
    print()

    criteria_input = {}
    for crit_id, name, weight, desc in GATE_CRITERIA[phase_key]:
        print(f"  {name}")
        print(f"  ({desc})")
        status = input("  Status [pass/partial/fail]: ").strip().lower()
        criteria_input[crit_id] = status
        print()

    report = score_criteria(phase_key, criteria_input)
    print_score_report(report)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Gate Review Scorer — SOR/SOP readiness assessment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python tools/gate_review_scorer.py --phase SOP \\\n"
            '    --criteria "test_complete:pass,traceability:partial,'
            'safety_plan:pass,cm_baselines:fail,open_issues:partial"\n'
            "  python tools/gate_review_scorer.py --phase SOR --interactive\n"
            "  python tools/gate_review_scorer.py --list-criteria SOP\n"
        ),
    )
    parser.add_argument("--phase", "-p", help="Gate phase: SOR or SOP")
    parser.add_argument(
        "--criteria", "-c",
        help="Comma-separated criterion:status pairs (status: pass/partial/fail)",
    )
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="Interactive mode — prompts for each criterion")
    parser.add_argument("--list-criteria", metavar="PHASE",
                        help="List criteria IDs and descriptions for a phase")

    args = parser.parse_args()

    if args.list_criteria:
        phase_key = args.list_criteria.upper()
        if phase_key not in GATE_CRITERIA:
            print(f"Error: Unknown phase '{args.list_criteria}'.", file=sys.stderr)
            return 1
        print(f"\nGate criteria for {phase_key}:")
        print(f"{'ID':<25} {'Weight':<8} Description")
        print("─" * 65)
        for crit_id, name, weight, desc in GATE_CRITERIA[phase_key]:
            wt_label = {3: "critical", 2: "important", 1: "advisory"}.get(weight, str(weight))
            print(f"  {crit_id:<23} {wt_label:<8} {name}")
        print()
        return 0

    if not args.phase:
        parser.print_help()
        print("\nError: --phase is required.")
        return 1

    if args.interactive:
        try:
            interactive_mode(args.phase)
            return 0
        except ValueError as err:
            print(f"Error: {err}", file=sys.stderr)
            return 1

    if not args.criteria:
        parser.print_help()
        print("\nError: --criteria is required (or use --interactive).")
        return 1

    try:
        criteria_input = {}
        for pair in args.criteria.split(","):
            pair = pair.strip()
            if ":" in pair:
                key, value = pair.split(":", 1)
                criteria_input[key.strip()] = value.strip()

        report = score_criteria(args.phase, criteria_input)
        print_score_report(report)
        return 0

    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
