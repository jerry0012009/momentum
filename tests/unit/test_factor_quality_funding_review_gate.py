import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from build_factor_quality_scorecard import classify_review_and_ml_gate


def _base_kwargs(**overrides):
    values = {
        "metadata_quality": "COMPLETE",
        "quality_class": "PROMISING_BUT_INCONSISTENT",
        "coverage": 0.95,
        "rankic_mean": 0.03,
        "ls_ann_return": 0.10,
        "comp_score": 90,
        "quantile_shape": "NEAR_MONOTONIC",
        "strongest_redundancy_level": "LOW_REDUNDANCY",
        "rankic_robust_class": "ROBUST_SIGNIFICANT_POSITIVE",
        "ls_robust_class": "RETURN_ROBUST_POSITIVE",
        "cost_status": "COST_SURVIVED",
    }
    values.update(overrides)
    return values


def test_funding_edge_flip_gets_specific_review_status():
    gate = classify_review_and_ml_gate(**_base_kwargs(
        funding_adjusted_edge_flip=True,
        after_funding_ls_spread=-0.01,
        after_funding_coverage_rate=0.90,
    ))

    assert gate["review_substatus"] == "REVIEW_FUNDING_ADJUSTED_ECONOMICS"
    assert "funding_adjusted_edge_flip" in gate["ml_gate_risk_flags"]
    assert "funding_adjusted_edge_nonpositive" in gate["ml_gate_risk_flags"]


def test_low_funding_coverage_gets_specific_risk_flag():
    gate = classify_review_and_ml_gate(**_base_kwargs(
        after_funding_ls_spread=0.01,
        after_funding_coverage_rate=0.50,
    ))

    assert gate["review_substatus"] == "REVIEW_FUNDING_ADJUSTED_ECONOMICS"
    assert "funding_coverage_insufficient" in gate["ml_gate_risk_flags"]


def test_bucket_tail_reason_gets_tail_review_status():
    gate = classify_review_and_ml_gate(**_base_kwargs(
        rankic_mean=0.03,
        ls_ann_return=0.10,
        workflow_review_bucket="TAIL_OR_MONOTONICITY_REVIEW_REQUIRED",
        workflow_review_reasons="tail_concentrated_negative_mean",
        bucket_tail_diagnosis="TAIL_CONCENTRATED_NEGATIVE_MEAN",
    ))

    assert gate["review_substatus"] == "REVIEW_BUCKET_TAIL"
    assert "tail_concentrated" in gate["ml_gate_risk_flags"]
