"""
Tests for gate_review_scorer.py

Covers SOR/SOP phase scoring, RAG status determination,
critical failure detection, and input validation.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.gate_review_scorer import score_criteria, GATE_CRITERIA  # noqa: E402


# ---------------------------------------------------------------------------
# SOP tests
# ---------------------------------------------------------------------------

def test_sop_all_pass_returns_green():
    """All SOP criteria pass → GREEN with no critical fails."""
    criteria = {cid: "pass" for cid, _, _, _ in GATE_CRITERIA["SOP"]}
    result = score_criteria("SOP", criteria)

    assert result["rag"] == "GREEN"
    assert result["overall_pct"] == pytest.approx(100.0)
    assert result["critical_fails"] == []
    assert result["phase"] == "SOP"


def test_sop_one_critical_fail_returns_amber():
    """One weight=3 fail (cm_baselines) with all others passing → AMBER."""
    criteria = {cid: "pass" for cid, _, _, _ in GATE_CRITERIA["SOP"]}
    criteria["cm_baselines"] = "fail"

    result = score_criteria("SOP", criteria)

    assert result["rag"] == "AMBER"
    assert "CM Baselines Recorded" in result["critical_fails"]
    assert len(result["critical_fails"]) == 1


def test_sop_multiple_critical_fails_returns_red():
    """Four weight=3 criteria failing with low overall score → RED."""
    criteria = {cid: "pass" for cid, _, _, _ in GATE_CRITERIA["SOP"]}
    for crit_id in ("test_complete", "traceability", "safety_plan", "cm_baselines"):
        criteria[crit_id] = "fail"

    result = score_criteria("SOP", criteria)

    assert result["rag"] == "RED"
    assert len(result["critical_fails"]) == 4
    assert result["overall_pct"] < 60.0


def test_sop_partial_statuses_affect_score():
    """Partial status contributes 0.5 weight to the score."""
    criteria = {cid: "pass" for cid, _, _, _ in GATE_CRITERIA["SOP"]}
    criteria["test_complete"] = "partial"   # weight=3, score=0.5 → 1.5 weighted

    result = score_criteria("SOP", criteria)

    # Overall < 100% but no hard fail on a critical criterion
    assert result["overall_pct"] < 100.0
    assert result["rag"] in ("GREEN", "AMBER")
    # partial on a weight=3 item is not a critical_fail (only fail is)
    assert result["critical_fails"] == []


# ---------------------------------------------------------------------------
# SOR tests
# ---------------------------------------------------------------------------

def test_sor_all_pass_returns_green():
    """All SOR criteria pass → GREEN."""
    criteria = {cid: "pass" for cid, _, _, _ in GATE_CRITERIA["SOR"]}
    result = score_criteria("SOR", criteria)

    assert result["rag"] == "GREEN"
    assert result["overall_pct"] == pytest.approx(100.0)
    assert result["phase"] == "SOR"


def test_sor_one_critical_fail_returns_amber():
    """One weight=3 SOR criterion failing → AMBER."""
    criteria = {cid: "pass" for cid, _, _, _ in GATE_CRITERIA["SOR"]}
    criteria["requirements_freeze"] = "fail"

    result = score_criteria("SOR", criteria)

    assert result["rag"] == "AMBER"
    assert len(result["critical_fails"]) == 1


# ---------------------------------------------------------------------------
# Validation and edge-case tests
# ---------------------------------------------------------------------------

def test_invalid_phase_raises_value_error():
    """Unrecognised phase name raises ValueError."""
    with pytest.raises(ValueError, match="Unknown phase"):
        score_criteria("INVALID_PHASE", {})


def test_invalid_status_raises_value_error():
    """Unrecognised status string raises ValueError."""
    criteria = {cid: "pass" for cid, _, _, _ in GATE_CRITERIA["SOP"]}
    criteria["test_complete"] = "maybe"

    with pytest.raises(ValueError, match="Invalid status"):
        score_criteria("SOP", criteria)


def test_missing_criterion_treated_as_fail():
    """Criterion absent from input dict is scored as fail, was_provided=False."""
    result = score_criteria("SOP", {})  # provide nothing

    fail_items = [r for r in result["results"] if r["status"] == "fail"]
    assert len(fail_items) == len(GATE_CRITERIA["SOP"])

    unprovided = [r for r in result["results"] if not r["provided"]]
    assert len(unprovided) == len(GATE_CRITERIA["SOP"])


def test_phase_key_is_case_insensitive():
    """Lowercase phase string is normalised to uppercase correctly."""
    criteria = {cid: "pass" for cid, _, _, _ in GATE_CRITERIA["SOP"]}
    result = score_criteria("sop", criteria)

    assert result["phase"] == "SOP"
    assert result["rag"] == "GREEN"


def test_result_contains_all_defined_criteria():
    """Results list contains one entry per defined criterion for the phase."""
    criteria = {cid: "pass" for cid, _, _, _ in GATE_CRITERIA["SOR"]}
    result = score_criteria("SOR", criteria)

    assert len(result["results"]) == len(GATE_CRITERIA["SOR"])
    result_ids = {r["id"] for r in result["results"]}
    defined_ids = {cid for cid, _, _, _ in GATE_CRITERIA["SOR"]}
    assert result_ids == defined_ids
