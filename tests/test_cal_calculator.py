"""
Tests for tools/cal_calculator.py

Verifies:
- CAL 1 output: I1/AF1
- CAL 4 output: I4/AF4
- I3/AF2 → CAL 2 explicitly
- I3/AF3 → CAL 3 explicitly
- I4/AF2 → CAL 3 explicitly
- Invalid impact → ValueError with helpful message
- Invalid feasibility → ValueError with helpful message
- All CAL levels are reachable
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.cal_calculator import lookup_cal, print_result, print_all_combinations, CAL_TABLE  # noqa: E402


class TestCalLookup:
    """Tests for direct CAL table lookup."""

    def test_i1_af1_returns_cal1(self):
        """I1/AF1 → CAL 1 (lowest impact, lowest feasibility)."""
        result = lookup_cal("I1", "AF1")
        assert result == "CAL 1"

    def test_i4_af4_returns_cal4(self):
        """I4/AF4 → CAL 4 (severe impact, highly feasible)."""
        result = lookup_cal("I4", "AF4")
        assert result == "CAL 4"

    def test_i3_af2_returns_cal2(self):
        """I3/AF2 → CAL 2 explicitly as per specification."""
        result = lookup_cal("I3", "AF2")
        assert result == "CAL 2"

    def test_i3_af3_returns_cal3(self):
        """I3/AF3 → CAL 3."""
        result = lookup_cal("I3", "AF3")
        assert result == "CAL 3"

    def test_i4_af2_returns_cal3(self):
        """I4/AF2 → CAL 3."""
        result = lookup_cal("I4", "AF2")
        assert result == "CAL 3"

    def test_i4_af1_returns_cal2(self):
        """I4/AF1 — severe impact but very low feasibility → CAL 2."""
        result = lookup_cal("I4", "AF1")
        assert result == "CAL 2"

    def test_i2_af3_returns_cal2(self):
        """I2/AF3 → CAL 2."""
        result = lookup_cal("I2", "AF3")
        assert result == "CAL 2"

    def test_i1_af4_returns_cal1(self):
        """I1/AF4 — negligible impact even at high feasibility → CAL 1."""
        result = lookup_cal("I1", "AF4")
        assert result == "CAL 1"

    def test_i2_af1_returns_cal1(self):
        """I2/AF1 → CAL 1."""
        result = lookup_cal("I2", "AF1")
        assert result == "CAL 1"

    def test_all_cal_levels_reachable(self):
        """All four CAL levels must be reachable from the table."""
        results = set(CAL_TABLE.values())
        assert "CAL 1" in results
        assert "CAL 2" in results
        assert "CAL 3" in results
        assert "CAL 4" in results

    def test_cal4_only_i4_af4(self):
        """CAL 4 should only result from I4/AF4."""
        cal4_entries = [k for k, v in CAL_TABLE.items() if v == "CAL 4"]
        assert len(cal4_entries) == 1
        assert cal4_entries[0] == ("I4", "AF4")


class TestCalInputValidation:
    """Tests for invalid input rejection."""

    def test_invalid_impact_raises_value_error(self):
        """Invalid impact value → ValueError with description."""
        with pytest.raises(ValueError) as exc_info:
            lookup_cal("I5", "AF2")
        assert "I5" in str(exc_info.value)

    def test_invalid_feasibility_raises_value_error(self):
        """Invalid feasibility value → ValueError."""
        with pytest.raises(ValueError) as exc_info:
            lookup_cal("I3", "AF9")
        assert "AF9" in str(exc_info.value)

    def test_empty_impact_raises_value_error(self):
        """Empty impact string → ValueError."""
        with pytest.raises(ValueError):
            lookup_cal("", "AF2")

    def test_empty_feasibility_raises_value_error(self):
        """Empty feasibility string → ValueError."""
        with pytest.raises(ValueError):
            lookup_cal("I3", "")

    def test_lowercase_input_accepted(self):
        """Lowercase inputs should be normalised."""
        result = lookup_cal("i4", "af4")
        assert result == "CAL 4"

    def test_mixed_case_accepted(self):
        """Mixed case normalised."""
        result = lookup_cal("I3", "af2")
        assert result == "CAL 2"

    def test_invalid_format_raises_value_error(self):
        """Completely wrong format raises ValueError."""
        with pytest.raises(ValueError):
            lookup_cal("HIGH", "LOW")


class TestCalTableCompleteness:
    """Tests for table completeness."""

    def test_table_has_sixteen_entries(self):
        """4 impact levels × 4 feasibility levels = 16 entries."""
        assert len(CAL_TABLE) == 16

    def test_all_impact_levels_covered(self):
        """All 4 impact levels are in the table."""
        impact_levels = {k[0] for k in CAL_TABLE.keys()}
        assert "I1" in impact_levels
        assert "I2" in impact_levels
        assert "I3" in impact_levels
        assert "I4" in impact_levels

    def test_all_feasibility_levels_covered(self):
        """All 4 feasibility levels are in the table."""
        feas_levels = {k[1] for k in CAL_TABLE.keys()}
        assert "AF1" in feas_levels
        assert "AF2" in feas_levels
        assert "AF3" in feas_levels
        assert "AF4" in feas_levels


class TestCalOutput:
    """Tests for output functions."""

    def test_print_result_cal4(self, capsys):
        """print_result for CAL 4 should include CAL 4 and disclaimer."""
        print_result("I4", "AF4")
        captured = capsys.readouterr()
        assert "CAL 4" in captured.out
        assert "DISCLAIMER" in captured.out or "review" in captured.out.lower()

    def test_print_result_cal1(self, capsys):
        """print_result for CAL 1 should include CAL 1."""
        print_result("I1", "AF1")
        captured = capsys.readouterr()
        assert "CAL 1" in captured.out

    def test_print_all_combinations_runs(self, capsys):
        """print_all_combinations should run without error."""
        print_all_combinations()
        captured = capsys.readouterr()
        assert "CAL 4" in captured.out
        assert "I4" in captured.out
        assert "AF4" in captured.out

    def test_print_result_includes_impact_description(self, capsys):
        """print_result should show impact description."""
        print_result("I3", "AF2")
        captured = capsys.readouterr()
        assert "I3" in captured.out
        assert "AF2" in captured.out
