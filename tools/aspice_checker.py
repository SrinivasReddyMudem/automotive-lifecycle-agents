#!/usr/bin/env python3
"""
ASPICE Checker — Work product gap analysis for Automotive SPICE SWE.1–SWE.6.

Author: Srinivas Reddy M
Project: Automotive Lifecycle Agents


Compares work products present against requirements for each SWE process area
and outputs a gap report with risk classification per missing item.

Usage:
    python tools/aspice_checker.py --phase SWE4 \
        --have "unit_test_spec,test_results,coverage_report"
    python tools/aspice_checker.py --phase all \
        --have "srs,sad,unit_test_spec,test_results"
    python tools/aspice_checker.py --list-phases

DISCLAIMER: Gap analysis is advisory. Assessment findings depend on evidence quality.
"""

import argparse
import sys

# ---------------------------------------------------------------------------
# Work product definitions per SWE phase
# Each entry: (work_product_id, display_name, risk_if_missing, assessor_note)
# ---------------------------------------------------------------------------
SWE_WORK_PRODUCTS = {
    "SWE1": [
        ("srs", "SW Requirements Spec (SRS)", "HIGH",
         "Assessor will ask: Show me your SRS. Who approved it and when?"),
        ("interface_req", "Interface requirements", "MEDIUM",
         "Assessor will ask: How are system-level interfaces defined?"),
        ("traceability_sw_sys", "Traceability SW req ↔ System req", "HIGH",
         "Assessor will ask: Show me bidirectional traceability to system requirements."),
        ("change_requests_swe1", "Change request records", "MEDIUM",
         "Assessor will ask: How do system requirement changes flow into SW requirements?"),
        ("requirements_review_record", "Requirements review record", "HIGH",
         "Assessor will ask (PA 2.2): Show me the review record with sign-off."),
    ],
    "SWE2": [
        ("sad", "SW Architectural Design (SAD)", "HIGH",
         "Assessor will ask: Is your SAD approved? Show me the approval."),
        ("interface_desc", "Interface descriptions", "MEDIUM",
         "Assessor will ask: How are SW component interfaces specified?"),
        ("dynamic_behaviour", "Dynamic behaviour description", "MEDIUM",
         "Assessor will ask: Show me state diagrams or sequence diagrams."),
        ("traceability_sad_srs", "Traceability SAD ↔ SRS", "HIGH",
         "Assessor will ask: How does your architecture address every SW requirement?"),
        ("sad_review_record", "SAD review record", "HIGH",
         "Assessor will ask (PA 2.2): Show me the SAD review with sign-off."),
    ],
    "SWE3": [
        ("detailed_design", "SW detailed design documents", "HIGH",
         "Assessor will ask: Is your detailed design separate from source code?"),
        ("unit_implementation", "Unit implementation (under CM)", "MEDIUM",
         "Assessor will ask: Is source code baselined in your CM system?"),
        ("misra_evidence", "MISRA compliance evidence", "HIGH",
         "Assessor will ask: Show me your static analysis tool report and qualification."),
        ("deviation_register", "Deviation register", "MEDIUM",
         "Assessor will ask: Are all MISRA deviations formally approved?"),
        ("traceability_design_sad", "Traceability detailed design ↔ SAD", "HIGH",
         "Assessor will ask: How does detailed design trace to architecture?"),
    ],
    "SWE4": [
        ("unit_test_spec", "Unit test specification", "HIGH",
         "Assessor will ask: Show a test case traced to detailed design."),
        ("unit_test_results", "Unit test results", "HIGH",
         "Assessor will ask: Are results linked to the baselined SW version?"),
        ("coverage_evidence", "Coverage evidence (branch/MC/DC)", "HIGH",
         "Assessor will ask: Show your coverage report from a qualified tool."),
        ("static_analysis_results", "Static analysis results", "HIGH",
         "Assessor will ask: Show your static analysis tool and how findings were addressed."),
        ("test_design_traceability", "Test ↔ design traceability", "MEDIUM",
         "Assessor will ask: How do you know your tests cover the detailed design?"),
    ],
    "SWE5": [
        ("integration_plan", "SW integration plan", "MEDIUM",
         "Assessor will ask: Show me your integration strategy and build order."),
        ("integration_test_spec", "Integration test specification", "HIGH",
         "Assessor will ask: How are integration tests different from unit tests?"),
        ("integration_test_results", "Integration test results", "HIGH",
         "Assessor will ask: Are integration test results linked to a build?"),
        ("build_log", "Build logs", "MEDIUM",
         "Assessor will ask: Show me the build log for your release candidate."),
        ("integration_traceability", "Integration tests ↔ SAD traceability", "MEDIUM",
         "Assessor will ask: How do integration tests cover architectural interfaces?"),
    ],
    "SWE6": [
        ("swqt_spec", "SWQT specification", "HIGH",
         "Assessor will ask: Is there a test case for every SW requirement?"),
        ("swqt_results", "SWQT results", "HIGH",
         "Assessor will ask: Was the final release candidate the SW that was tested?"),
        ("test_environment_desc", "Test environment description", "MEDIUM",
         "Assessor will ask: What hardware and tools were used for qualification tests?"),
        ("regression_results", "Regression test results", "MEDIUM",
         "Assessor will ask: What regression tests were run after the last change?"),
        ("swqt_srs_traceability", "SWQT ↔ SRS traceability", "HIGH",
         "Assessor will ask: Show 100% coverage of SW requirements by SWQT."),
    ],
}

PHASE_DISPLAY = {
    "SWE1": "SWE.1 — Software Requirements Analysis",
    "SWE2": "SWE.2 — Software Architectural Design",
    "SWE3": "SWE.3 — Detailed Design and Unit Construction",
    "SWE4": "SWE.4 — Software Unit Verification",
    "SWE5": "SWE.5 — Software Integration and Integration Test",
    "SWE6": "SWE.6 — Software Qualification Test",
}


def check_phase(phase: str, have_set: set) -> tuple:
    """
    Check work products for a single phase.
    Returns (total, present_count, gap_list).
    """
    phase_key = phase.upper()
    if phase_key not in SWE_WORK_PRODUCTS:
        raise ValueError(
            f"Unknown phase '{phase}'. Valid phases: {sorted(SWE_WORK_PRODUCTS.keys())}"
        )

    work_products = SWE_WORK_PRODUCTS[phase_key]
    gaps = []
    present_count = 0

    for wp_id, name, risk, assessor_note in work_products:
        if wp_id in have_set:
            present_count += 1
        else:
            gaps.append((name, risk, assessor_note))

    return len(work_products), present_count, gaps


def print_phase_report(phase: str, have_set: set) -> int:
    """Print gap report for one phase. Returns number of gaps."""
    phase_key = phase.upper()
    total, present, gaps = check_phase(phase_key, have_set)

    sep = "─" * 55
    print(sep)
    print(f"  {PHASE_DISPLAY[phase_key]}")
    print(sep)

    work_products = SWE_WORK_PRODUCTS[phase_key]
    for wp_id, name, risk, _ in work_products:
        status = "PRESENT" if wp_id in have_set else f"MISSING  [{risk} RISK]"
        print(f"  {name:<40} {status}")

    print(sep)
    gap_count = len(gaps)
    print(f"  {present}/{total} work products present. {gap_count} gap(s) found.")

    if gaps:
        print()
        print("  Assessor focus areas for missing work products:")
        for name, risk, note in gaps:
            print(f"  [{risk}] {note}")

    print(sep)
    print()
    return gap_count


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="ASPICE Checker — work product gap analysis for SWE.1-SWE.6",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python tools/aspice_checker.py --phase SWE4 "
            '--have "unit_test_spec,test_results,coverage_report"\n'
            "  python tools/aspice_checker.py --phase all "
            '--have "srs,sad,unit_test_spec,test_results"\n'
            "  python tools/aspice_checker.py --list-phases\n"
        ),
    )
    parser.add_argument(
        "--phase", "-p",
        help="Phase to check: SWE1, SWE2, SWE3, SWE4, SWE5, SWE6, or 'all'",
    )
    parser.add_argument(
        "--have",
        help="Comma-separated list of work product IDs you have",
    )
    parser.add_argument(
        "--list-phases", action="store_true",
        help="List all phases and their work product IDs",
    )

    args = parser.parse_args()

    if args.list_phases:
        for phase_key, display in PHASE_DISPLAY.items():
            print(f"\n{display}")
            for wp_id, name, risk, _ in SWE_WORK_PRODUCTS[phase_key]:
                print(f"  {wp_id:<35} [{risk} if missing]")
        return 0

    if not args.phase or not args.have:
        parser.print_help()
        print("\nError: --phase and --have are required.")
        return 1

    have_set = {wp.strip().lower() for wp in args.have.split(",") if wp.strip()}
    total_gaps = 0

    try:
        if args.phase.upper() == "ALL":
            print("ASPICE Gap Analysis — All SWE Process Areas")
            print()
            for phase_key in ["SWE1", "SWE2", "SWE3", "SWE4", "SWE5", "SWE6"]:
                total_gaps += print_phase_report(phase_key, have_set)
            print(f"TOTAL GAPS ACROSS ALL PHASES: {total_gaps}")
        else:
            total_gaps = print_phase_report(args.phase, have_set)

        print()
        print("DISCLAIMER: Gap analysis is advisory only. Assessment findings")
        print("depend on evidence quality and assessor interpretation.")
        return 0

    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
