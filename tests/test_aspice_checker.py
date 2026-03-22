"""
Tests for tools/aspice_checker.py

Verifies:
- SWE4 with all work products present → zero gaps
- SWE4 with missing static_analysis_results → gap with HIGH risk
- --phase all with minimal have list → gaps across multiple phases
- Invalid phase name → ValueError
- Work product status detection
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.aspice_checker import check_phase, print_phase_report, SWE_WORK_PRODUCTS  # noqa: E402


class TestSwe4Complete:
    """Tests for SWE.4 with all work products present."""

    def test_swe4_all_present_zero_gaps(self):
        """SWE4 with all required work products → zero gaps."""
        all_swe4_ids = {wp[0] for wp in SWE_WORK_PRODUCTS["SWE4"]}
        total, present, gaps = check_phase("SWE4", all_swe4_ids)
        assert len(gaps) == 0
        assert present == total

    def test_swe4_all_present_present_count_equals_total(self):
        """All present: present_count must equal total."""
        all_swe4_ids = {wp[0] for wp in SWE_WORK_PRODUCTS["SWE4"]}
        total, present, gaps = check_phase("SWE4", all_swe4_ids)
        assert present == total

    def test_swe4_five_work_products_defined(self):
        """SWE.4 should define exactly 5 work products."""
        assert len(SWE_WORK_PRODUCTS["SWE4"]) == 5


class TestSwe4Gaps:
    """Tests for SWE.4 with specific gaps."""

    def test_swe4_missing_static_analysis_creates_gap(self):
        """Missing static_analysis_results should create a gap."""
        have = {
            "unit_test_spec",
            "unit_test_results",
            "coverage_evidence",
            "test_design_traceability",
            # static_analysis_results intentionally omitted
        }
        total, present, gaps = check_phase("SWE4", have)
        gap_names = [g[0] for g in gaps]
        assert any("static" in name.lower() or "analysis" in name.lower()
                   for name in gap_names)

    def test_swe4_missing_static_analysis_is_high_risk(self):
        """Missing static_analysis_results should have HIGH risk."""
        have = {"unit_test_spec", "unit_test_results", "coverage_evidence",
                "test_design_traceability"}
        _total, _present, gaps = check_phase("SWE4", have)
        high_risk_gaps = [g for g in gaps if g[1] == "HIGH"]
        assert len(high_risk_gaps) >= 1

    def test_swe4_empty_have_all_gaps(self):
        """Empty have set → all SWE4 work products are missing."""
        total, present, gaps = check_phase("SWE4", set())
        assert present == 0
        assert len(gaps) == total

    def test_swe4_missing_test_spec_gap_detected(self):
        """Missing unit_test_spec should appear as a gap."""
        have = {"unit_test_results", "coverage_evidence",
                "static_analysis_results", "test_design_traceability"}
        _total, _present, gaps = check_phase("SWE4", have)
        gap_ids_raw = [g[0] for g in gaps]
        # gaps return (name, risk, note) — check name contains "spec" or "specification"
        assert any("spec" in name.lower() or "test" in name.lower() for name in gap_ids_raw)


class TestAllPhases:
    """Tests for all phases at once."""

    def test_all_phases_minimal_have_finds_multiple_gaps(self):
        """With only SRS present, all other phases should have gaps."""
        minimal_have = {"srs"}
        total_gaps = 0
        for phase_key in ["SWE1", "SWE2", "SWE3", "SWE4", "SWE5", "SWE6"]:
            _total, _present, gaps = check_phase(phase_key, minimal_have)
            total_gaps += len(gaps)
        assert total_gaps > 10  # expecting many gaps across all phases

    def test_all_phases_full_have_zero_gaps(self):
        """With all work products present, all phases should have zero gaps."""
        all_ids = set()
        for phase_key, work_products in SWE_WORK_PRODUCTS.items():
            for wp_id, _name, _risk, _note in work_products:
                all_ids.add(wp_id)

        total_gaps = 0
        for phase_key in ["SWE1", "SWE2", "SWE3", "SWE4", "SWE5", "SWE6"]:
            _total, _present, gaps = check_phase(phase_key, all_ids)
            total_gaps += len(gaps)
        assert total_gaps == 0


class TestPhaseValidation:
    """Tests for invalid phase input."""

    def test_invalid_phase_raises_value_error(self):
        """Unknown phase name should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            check_phase("SWE99", {"srs"})
        assert "SWE99" in str(exc_info.value)

    def test_invalid_phase_lowercase_raises_value_error(self):
        """Phase names are case-normalised — completely invalid names raise."""
        with pytest.raises(ValueError):
            check_phase("INVALID_PHASE", set())

    def test_valid_phase_lowercase_accepted(self):
        """Lowercase phase name should be normalised and accepted."""
        total, present, gaps = check_phase("swe4", {"unit_test_spec"})
        assert total > 0


class TestPrintPhaseReport:
    """Tests for print output."""

    def test_print_phase_report_runs(self, capsys):
        """print_phase_report should produce output without error."""
        have = {"unit_test_spec", "unit_test_results"}
        print_phase_report("SWE4", have)
        captured = capsys.readouterr()
        assert "SWE.4" in captured.out
        assert "PRESENT" in captured.out
        assert "MISSING" in captured.out

    def test_print_phase_report_no_gaps_message(self, capsys):
        """With all work products, gap count should be 0."""
        all_swe4_ids = {wp[0] for wp in SWE_WORK_PRODUCTS["SWE4"]}
        gaps = print_phase_report("SWE4", all_swe4_ids)
        assert gaps == 0


class TestWorkProductStructure:
    """Tests for data structure integrity."""

    def test_all_six_phases_present(self):
        """All SWE.1 through SWE.6 must be defined."""
        for phase in ["SWE1", "SWE2", "SWE3", "SWE4", "SWE5", "SWE6"]:
            assert phase in SWE_WORK_PRODUCTS

    def test_each_phase_has_at_least_four_work_products(self):
        """Each phase should have at least 4 work products."""
        for phase_key, wps in SWE_WORK_PRODUCTS.items():
            assert len(wps) >= 4, f"{phase_key} has fewer than 4 work products"

    def test_work_product_entries_have_four_fields(self):
        """Each work product tuple must have 4 fields: id, name, risk, note."""
        for phase_key, wps in SWE_WORK_PRODUCTS.items():
            for wp in wps:
                assert len(wp) == 4, f"Work product in {phase_key} missing fields: {wp}"

    def test_risk_levels_are_valid(self):
        """Risk levels must be HIGH, MEDIUM, or LOW."""
        valid_risks = {"HIGH", "MEDIUM", "LOW"}
        for phase_key, wps in SWE_WORK_PRODUCTS.items():
            for wp_id, name, risk, note in wps:
                assert risk in valid_risks, (
                    f"Invalid risk '{risk}' for {wp_id} in {phase_key}"
                )
