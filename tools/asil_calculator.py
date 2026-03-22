#!/usr/bin/env python3
"""
ASIL Calculator — ISO 26262-3 Table 4 lookup tool.

Author: Srinivas Reddy M
Project: Automotive Lifecycle Agents


Determines ASIL level from Severity, Exposure, and Controllability ratings.
Uses direct table lookup — no interpolation. All 64 S/E/C combinations
are explicitly defined matching ISO 26262-3 Table 4.

Usage:
    python tools/asil_calculator.py --severity S3 --exposure E4 --controllability C2
    python tools/asil_calculator.py --interactive
    python tools/asil_calculator.py --list-all

DISCLAIMER: Results require review by a qualified functional safety engineer.
"""

import argparse
import sys

# ---------------------------------------------------------------------------
# ISO 26262-3 Table 4 — Complete ASIL lookup table
# Key: (severity, exposure, controllability)  Value: ASIL result string
# ---------------------------------------------------------------------------
ASIL_TABLE = {
    # S0 — no injuries: always QM regardless of E and C
    ("S0", "E0", "C0"): "QM", ("S0", "E0", "C1"): "QM", ("S0", "E0", "C2"): "QM",
    ("S0", "E0", "C3"): "QM", ("S0", "E1", "C0"): "QM", ("S0", "E1", "C1"): "QM",
    ("S0", "E1", "C2"): "QM", ("S0", "E1", "C3"): "QM", ("S0", "E2", "C0"): "QM",
    ("S0", "E2", "C1"): "QM", ("S0", "E2", "C2"): "QM", ("S0", "E2", "C3"): "QM",
    ("S0", "E3", "C0"): "QM", ("S0", "E3", "C1"): "QM", ("S0", "E3", "C2"): "QM",
    ("S0", "E3", "C3"): "QM", ("S0", "E4", "C0"): "QM", ("S0", "E4", "C1"): "QM",
    ("S0", "E4", "C2"): "QM", ("S0", "E4", "C3"): "QM",

    # S1 — light to moderate injuries
    ("S1", "E1", "C1"): "QM",    ("S1", "E1", "C2"): "QM",    ("S1", "E1", "C3"): "QM",
    ("S1", "E2", "C1"): "QM",    ("S1", "E2", "C2"): "QM",    ("S1", "E2", "C3"): "QM",
    ("S1", "E3", "C1"): "QM",    ("S1", "E3", "C2"): "QM",    ("S1", "E3", "C3"): "ASIL A",
    ("S1", "E4", "C1"): "QM",    ("S1", "E4", "C2"): "ASIL A", ("S1", "E4", "C3"): "ASIL B",

    # S2 — severe and life-threatening, survival probable
    ("S2", "E1", "C1"): "QM",    ("S2", "E1", "C2"): "QM",    ("S2", "E1", "C3"): "QM",
    ("S2", "E2", "C1"): "QM",    ("S2", "E2", "C2"): "QM",    ("S2", "E2", "C3"): "ASIL A",
    ("S2", "E3", "C1"): "QM",    ("S2", "E3", "C2"): "ASIL A", ("S2", "E3", "C3"): "ASIL B",
    ("S2", "E4", "C1"): "ASIL A", ("S2", "E4", "C2"): "ASIL B", ("S2", "E4", "C3"): "ASIL C",

    # S3 — life-threatening, survival uncertain or fatal
    ("S3", "E1", "C1"): "QM",    ("S3", "E1", "C2"): "QM",    ("S3", "E1", "C3"): "ASIL A",
    ("S3", "E2", "C1"): "QM",    ("S3", "E2", "C2"): "ASIL A", ("S3", "E2", "C3"): "ASIL B",
    ("S3", "E3", "C1"): "ASIL A", ("S3", "E3", "C2"): "ASIL B", ("S3", "E3", "C3"): "ASIL C",
    ("S3", "E4", "C1"): "ASIL B", ("S3", "E4", "C2"): "ASIL C", ("S3", "E4", "C3"): "ASIL D",
}

SEVERITY_DESC = {
    "S0": "No injuries",
    "S1": "Light to moderate injuries",
    "S2": "Severe and life-threatening injuries, survival probable",
    "S3": "Life-threatening injuries, survival uncertain, or fatal",
}

EXPOSURE_DESC = {
    "E0": "Incredible / not relevant",
    "E1": "Very low probability",
    "E2": "Low probability",
    "E3": "Medium probability",
    "E4": "High probability (occurs in most driving situations)",
}

CONTROLLABILITY_DESC = {
    "C0": "Controllable in general",
    "C1": "Simply controllable (>99% of drivers)",
    "C2": "Normally controllable (>90% of drivers)",
    "C3": "Difficult to control or uncontrollable (<90% of drivers)",
}

VALID_SEVERITY = {"S0", "S1", "S2", "S3"}
VALID_EXPOSURE = {"E0", "E1", "E2", "E3", "E4"}
VALID_CONTROLLABILITY = {"C0", "C1", "C2", "C3"}


def lookup_asil(severity: str, exposure: str, controllability: str) -> str:
    """Return ASIL level for given S/E/C combination."""
    s = severity.upper()
    e = exposure.upper()
    c = controllability.upper()

    if s not in VALID_SEVERITY:
        raise ValueError(
            f"Invalid severity '{severity}'. Valid values: {sorted(VALID_SEVERITY)}"
        )
    if e not in VALID_EXPOSURE:
        raise ValueError(
            f"Invalid exposure '{exposure}'. Valid values: {sorted(VALID_EXPOSURE)}"
        )
    if c not in VALID_CONTROLLABILITY:
        raise ValueError(
            f"Invalid controllability '{controllability}'. "
            f"Valid values: {sorted(VALID_CONTROLLABILITY)}"
        )

    key = (s, e, c)
    if key not in ASIL_TABLE:
        raise ValueError(f"Combination {key} not found in ASIL table.")

    return ASIL_TABLE[key]


def print_result(severity: str, exposure: str, controllability: str) -> None:
    """Print formatted ASIL result with context."""
    s = severity.upper()
    e = exposure.upper()
    c = controllability.upper()

    result = lookup_asil(s, e, c)

    sep = "─" * 45
    print(sep)
    print(f"  Severity:        {s} — {SEVERITY_DESC.get(s, '')}")
    print(f"  Exposure:        {e} — {EXPOSURE_DESC.get(e, '')}")
    print(f"  Controllability: {c} — {CONTROLLABILITY_DESC.get(c, '')}")
    print(sep)
    print(f"  ASIL Result:     {result}")
    print(sep)
    print()
    print("  DISCLAIMER: This result requires review and approval by a")
    print("  qualified functional safety engineer before use in any project.")
    print(sep)


def print_all_combinations() -> None:
    """Print all 64 S/E/C combinations as a formatted table."""
    print(f"{'Severity':<10} {'Exposure':<10} {'Controllability':<16} {'ASIL':<10}")
    print("─" * 50)
    for s in ["S0", "S1", "S2", "S3"]:
        for e in ["E0", "E1", "E2", "E3", "E4"]:
            for c in ["C0", "C1", "C2", "C3"]:
                key = (s, e, c)
                result = ASIL_TABLE.get(key, "N/A")
                print(f"{s:<10} {e:<10} {c:<16} {result:<10}")
    print()
    print("Total combinations: 64 (including S0=QM and E0=QM for all)")


def interactive_mode() -> None:
    """Prompt user step-by-step for S, E, C values."""
    print("ASIL Calculator — Interactive Mode")
    print("─" * 45)
    print()
    print("Step 1: Severity — How severe is the potential harm?")
    for k, v in SEVERITY_DESC.items():
        print(f"  {k}: {v}")
    severity = input("Enter severity [S0/S1/S2/S3]: ").strip().upper()

    print()
    print("Step 2: Exposure — How often is the vehicle in this operational situation?")
    for k, v in EXPOSURE_DESC.items():
        print(f"  {k}: {v}")
    exposure = input("Enter exposure [E0/E1/E2/E3/E4]: ").strip().upper()

    print()
    print("Step 3: Controllability — Can the driver control the vehicle?")
    for k, v in CONTROLLABILITY_DESC.items():
        print(f"  {k}: {v}")
    controllability = input("Enter controllability [C0/C1/C2/C3]: ").strip().upper()

    print()
    print_result(severity, exposure, controllability)


def main() -> int:
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="ASIL Calculator — ISO 26262-3 Table 4 lookup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python tools/asil_calculator.py --severity S3 --exposure E4 "
            "--controllability C2\n"
            "  python tools/asil_calculator.py --interactive\n"
            "  python tools/asil_calculator.py --list-all\n"
        ),
    )
    parser.add_argument("--severity", "-s", help="Severity class: S0, S1, S2, S3")
    parser.add_argument("--exposure", "-e", help="Exposure class: E0, E1, E2, E3, E4")
    parser.add_argument(
        "--controllability", "-c", help="Controllability class: C0, C1, C2, C3"
    )
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Interactive step-by-step mode"
    )
    parser.add_argument(
        "--list-all", action="store_true", help="Print all 64 S/E/C combinations"
    )

    args = parser.parse_args()

    if args.list_all:
        print_all_combinations()
        return 0

    if args.interactive:
        interactive_mode()
        return 0

    if not all([args.severity, args.exposure, args.controllability]):
        parser.print_help()
        print("\nError: --severity, --exposure, and --controllability are all required.")
        print("Or use --interactive or --list-all.")
        return 1

    try:
        print_result(args.severity, args.exposure, args.controllability)
        return 0
    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
