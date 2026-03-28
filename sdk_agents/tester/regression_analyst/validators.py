"""
Domain validators for regression_analyst output.
Catches missing HOLD/PROCEED rationale, unclustered failures, ignored ASIL-D.
"""

from sdk_agents.core.base_agent import DomainCheckError
from .schema import RegressionAnalystOutput

MIN_RATIONALE_LENGTH = 20
MIN_CLUSTER_CAUSE_LENGTH = 15


def validate(output: RegressionAnalystOutput) -> None:
    _check_summary_counts_logical(output)
    _check_asil_d_prioritised(output)
    _check_cluster_causes_specific(output)
    _check_hold_proceed_rationale(output)
    _check_coverage_blockers_identified(output)
    _check_self_evaluation_has_evidence(output)


def _check_summary_counts_logical(output: RegressionAnalystOutput) -> None:
    s = output.summary
    # new_failures cannot exceed current failing tests
    if s.new_failures > s.current_fail:
        raise DomainCheckError(
            f"summary.new_failures={s.new_failures} > current_fail={s.current_fail}. "
            f"New failures cannot exceed total current failures."
        )
    # ASIL breakdown cannot exceed new_failures total
    asil_total = s.asil_d_affected + s.asil_b_affected + s.qm_affected
    if asil_total > s.new_failures and s.new_failures > 0:
        raise DomainCheckError(
            f"ASIL breakdown (D={s.asil_d_affected} + B={s.asil_b_affected} + "
            f"QM={s.qm_affected} = {asil_total}) exceeds new_failures={s.new_failures}."
        )


def _check_asil_d_prioritised(output: RegressionAnalystOutput) -> None:
    if output.summary.asil_d_affected > 0:
        # If ASIL-D failures exist, recommendation should not be PROCEED without exceptions
        if output.hold_proceed_recommendation == "PROCEED":
            raise DomainCheckError(
                f"summary.asil_d_affected = {output.summary.asil_d_affected} but "
                f"hold_proceed_recommendation is PROCEED. ASIL-D failures must be "
                f"HOLD or at minimum PROCEED_WITH_EXCEPTIONS with justification."
            )
        # At least one cluster should be ASIL-D risk level
        asil_d_clusters = [c for c in output.failure_clusters if c.risk_level == "ASIL-D"]
        if not asil_d_clusters:
            raise DomainCheckError(
                f"{output.summary.asil_d_affected} ASIL-D failures reported but no cluster "
                f"has risk_level='ASIL-D'. ASIL-D failures must form a dedicated cluster."
            )


def _check_cluster_causes_specific(output: RegressionAnalystOutput) -> None:
    for i, cluster in enumerate(output.failure_clusters):
        if len(cluster.probable_cause.strip()) < MIN_CLUSTER_CAUSE_LENGTH:
            raise DomainCheckError(
                f"failure_clusters[{i}].probable_cause is too vague "
                f"({len(cluster.probable_cause)} chars). "
                f"Must name a specific module or change area."
            )


def _check_hold_proceed_rationale(output: RegressionAnalystOutput) -> None:
    if len(output.hold_proceed_rationale.strip()) < MIN_RATIONALE_LENGTH:
        raise DomainCheckError(
            f"hold_proceed_rationale is too short ({len(output.hold_proceed_rationale)} chars). "
            f"Must give specific justification for the {output.hold_proceed_recommendation} decision."
        )


def _check_coverage_blockers_identified(output: RegressionAnalystOutput) -> None:
    for delta in output.coverage_deltas:
        if delta.is_blocker == "YES" and not delta.lost_function.strip():
            raise DomainCheckError(
                f"CoverageDelta for module '{delta.module}' is marked as blocker "
                f"but lost_function is empty. Must identify the specific function that lost coverage."
            )


def _check_self_evaluation_has_evidence(output: RegressionAnalystOutput) -> None:
    for line in output.self_evaluation:
        if line.result == "PASS" and len(line.evidence.strip()) < 10:
            raise DomainCheckError(
                f"self_evaluation item '{line.item}' claims PASS "
                f"but evidence is empty or too short: '{line.evidence}'"
            )
