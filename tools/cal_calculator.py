#!/usr/bin/env python3
"""
CAL Calculator — ISO 21434 Cybersecurity Assurance Level determination.

Author: Srinivas Reddy M
Project: Automotive Lifecycle Agents


Determines CAL level from Impact and Attack Feasibility ratings.
Uses direct table lookup matching ISO 21434 Annex E methodology.

Usage:
    python tools/cal_calculator.py --impact I3 --feasibility AF2
    python tools/cal_calculator.py --interactive
    python tools/cal_calculator.py --list-all

DISCLAIMER: Results require review by a qualified cybersecurity engineer.
"""

import argparse
import sys

# ---------------------------------------------------------------------------
# ISO 21434 Impact × Attack Feasibility → CAL table
# ---------------------------------------------------------------------------
CAL_TABLE = {
    # I1 — Negligible impact: CAL 1 regardless of feasibility
    ("I1", "AF1"): "CAL 1",
    ("I1", "AF2"): "CAL 1",
    ("I1", "AF3"): "CAL 1",
    ("I1", "AF4"): "CAL 1",

    # I2 — Moderate impact
    ("I2", "AF1"): "CAL 1",
    ("I2", "AF2"): "CAL 1",
    ("I2", "AF3"): "CAL 2",
    ("I2", "AF4"): "CAL 2",

    # I3 — Major impact
    ("I3", "AF1"): "CAL 1",
    ("I3", "AF2"): "CAL 2",
    ("I3", "AF3"): "CAL 3",
    ("I3", "AF4"): "CAL 3",

    # I4 — Severe impact (safety, large financial, major operational)
    ("I4", "AF1"): "CAL 2",
    ("I4", "AF2"): "CAL 3",
    ("I4", "AF3"): "CAL 3",
    ("I4", "AF4"): "CAL 4",
}

IMPACT_DESC = {
    "I1": "Negligible — no significant harm",
    "I2": "Moderate — limited or reversible impact",
    "I3": "Major — significant impact, difficult to reverse",
    "I4": "Severe — safety risk or critical financial/operational harm",
}

FEASIBILITY_DESC = {
    "AF1": "Very low — requires significant resources, multi-expert, bespoke equipment",
    "AF2": "Low — requires expertise and specialised access",
    "AF3": "Medium — moderate resources, proficient attacker",
    "AF4": "High — easily performed with common tools and standard knowledge",
}

CAL_REQUIREMENTS = {
    "CAL 1": "Basic security measures. Informal review. Cybersecurity plan with basic controls.",
    "CAL 2": "Structured threat mitigation. Security testing required. Expert review.",
    "CAL 3": "Rigorous security design and testing. Penetration testing recommended. "
             "Security expert independent review.",
    "CAL 4": "Highest assurance. Mandatory penetration testing. Formal security case. "
             "Independent security assessment required.",
}

VALID_IMPACT = {"I1", "I2", "I3", "I4"}
VALID_FEASIBILITY = {"AF1", "AF2", "AF3", "AF4"}


def lookup_cal(impact: str, feasibility: str) -> str:
    """Return CAL level for given Impact/Feasibility combination."""
    i = impact.upper()
    f = feasibility.upper()

    if i not in VALID_IMPACT:
        raise ValueError(
            f"Invalid impact '{impact}'. Valid values: {sorted(VALID_IMPACT)}\n"
            f"  I1=Negligible, I2=Moderate, I3=Major, I4=Severe"
        )
    if f not in VALID_FEASIBILITY:
        raise ValueError(
            f"Invalid feasibility '{feasibility}'. Valid values: {sorted(VALID_FEASIBILITY)}\n"
            f"  AF1=Very low, AF2=Low, AF3=Medium, AF4=High"
        )

    key = (i, f)
    if key not in CAL_TABLE:
        raise ValueError(f"Combination {key} not found in CAL table.")

    return CAL_TABLE[key]


def print_result(impact: str, feasibility: str) -> None:
    """Print formatted CAL result with context."""
    i = impact.upper()
    f = feasibility.upper()
    result = lookup_cal(i, f)

    sep = "─" * 55
    print(sep)
    print(f"  Impact:            {i} — {IMPACT_DESC.get(i, '')}")
    print(f"  Attack Feasibility:{f} — {FEASIBILITY_DESC.get(f, '')}")
    print(sep)
    print(f"  CAL Result:        {result}")
    print(sep)
    print()
    print(f"  {result} requirements: {CAL_REQUIREMENTS.get(result, '')}")
    print()
    print("  DISCLAIMER: This result requires review and approval by a")
    print("  qualified cybersecurity engineer before use in any project.")
    print(sep)


def print_all_combinations() -> None:
    """Print complete Impact × Feasibility CAL table."""
    print(f"{'Impact':<8} {'Feasibility':<8} {'CAL Result':<12}")
    print("─" * 32)
    for i in ["I1", "I2", "I3", "I4"]:
        for f in ["AF1", "AF2", "AF3", "AF4"]:
            result = CAL_TABLE.get((i, f), "N/A")
            print(f"{i:<8} {f:<8} {result:<12}")
    print()
    print("Impact:      I1=Negligible / I2=Moderate / I3=Major / I4=Severe")
    print("Feasibility: AF1=Very low / AF2=Low / AF3=Medium / AF4=High")


def interactive_mode() -> None:
    """Prompt user step-by-step for Impact and Feasibility values."""
    print("CAL Calculator — Interactive Mode")
    print("─" * 45)
    print()
    print("Step 1: Impact — What is the worst-case damage scenario impact?")
    for k, v in IMPACT_DESC.items():
        print(f"  {k}: {v}")
    impact = input("Enter impact [I1/I2/I3/I4]: ").strip().upper()

    print()
    print("Step 2: Attack Feasibility — How feasible is the attack path?")
    for k, v in FEASIBILITY_DESC.items():
        print(f"  {k}: {v}")
    feasibility = input("Enter feasibility [AF1/AF2/AF3/AF4]: ").strip().upper()

    print()
    print_result(impact, feasibility)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="CAL Calculator — ISO 21434 cybersecurity assurance level",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python tools/cal_calculator.py --impact I3 --feasibility AF2\n"
            "  python tools/cal_calculator.py --interactive\n"
            "  python tools/cal_calculator.py --list-all\n"
        ),
    )
    parser.add_argument("--impact", "-i", help="Impact: I1, I2, I3, I4")
    parser.add_argument("--feasibility", "-f", help="Attack feasibility: AF1, AF2, AF3, AF4")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--list-all", action="store_true", help="Print all combinations")

    args = parser.parse_args()

    if args.list_all:
        print_all_combinations()
        return 0

    if args.interactive:
        interactive_mode()
        return 0

    if not args.impact or not args.feasibility:
        parser.print_help()
        print("\nError: --impact and --feasibility are required.")
        print("Or use --interactive or --list-all.")
        return 1

    try:
        print_result(args.impact, args.feasibility)
        return 0
    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
