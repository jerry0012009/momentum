import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from build_factor_ml_signal_prototype import (  # noqa: E402
    FeatureSelectionConfig,
    build_ls_utility_after_funding_targets,
    build_feature_matrix,
    eval_label_cols_for_mode,
    label_cols_for_mode,
    select_core_features,
    walk_forward_months,
)


def _scorecard(n: int = 140) -> pd.DataFrame:
    rows = []
    for i in range(n):
        hold = i % 17 == 0
        rows.append({
            "factor_id": f"factor_{i:03d}",
            "ml_gate_status": "ML_HOLD" if hold else "ML_READY_WITH_CAUTION",
            "review_substatus": "REVIEW_METADATA_ONLY" if i % 3 else "REVIEW_DIRECTION_SEMANTICS",
            "final_quality_score": 80 - (i % 30),
            "coverage_rate": 0.99 - (i % 5) * 0.01,
            "rankic_mean": 0.05 - (i % 7) * 0.002,
            "long_short_sharpe": 1.2 - (i % 4) * 0.1,
            "monthly_ic_positive_rate": 0.7,
            "strongest_redundancy_level": "HIGH_REDUNDANCY" if i % 11 == 0 else "LOW_REDUNDANCY",
            "redundancy_cluster_id": i // 4,
            "ml_gate_risk_flags": "metadata_needs_review" if i % 2 else "",
            "after_funding_best_horizon": "72h",
            "after_funding_long_short_spread": 0.002 if i % 5 else -0.001,
            "after_funding_coverage_rate": 1.0,
            "after_funding_bucket_tail_diagnosis": "DIRECTIONALLY_CLEAN_THIN_EDGE",
            "funding_adjusted_edge_flip": False,
        })
    return pd.DataFrame(rows)


def test_select_core_features_excludes_hold_and_targets_range():
    selected, summary = select_core_features(
        _scorecard(160),
        FeatureSelectionConfig(target_features=100, min_features=80, max_features=120, cluster_cap=3),
    )
    assert 80 <= len(selected) <= 120
    assert summary["eligible_factors"] < 160
    assert not (selected["ml_gate_status"] == "ML_HOLD").any()
    assert selected["factor_id"].is_unique


def test_ls_ic_aligned_policy_prefers_tradeable_direction_rows():
    df = _scorecard(80)
    df.loc[:9, "long_short_sharpe"] = 1.0
    df.loc[:9, "rankic_mean"] = 0.04
    df.loc[:9, "ml_gate_risk_flags"] = ""
    df.loc[:9, "strongest_redundancy_level"] = "LOW_REDUNDANCY"
    df.loc[10:19, "ml_gate_risk_flags"] = "rankic_ls_direction_conflict"
    df.loc[20:29, "ml_gate_risk_flags"] = "ls_not_robust"
    df.loc[30:39, "long_short_sharpe"] = -0.5

    selected, summary = select_core_features(
        df,
        FeatureSelectionConfig(
            target_features=10,
            min_features=5,
            max_features=12,
            cluster_cap=3,
            selection_policy="ls_ic_aligned",
        ),
    )

    flags = selected["ml_gate_risk_flags"].fillna("")
    assert len(selected) == 10
    assert summary["selection_policy"] == "ls_ic_aligned"
    assert summary["strict_ls_ic_aligned_factors"] >= 10
    assert summary["selected_strict_ls_ic_aligned"] == 10
    assert not flags.str.contains("rankic_ls_direction_conflict", regex=False).any()
    assert not (selected["long_short_sharpe"] <= 0).any()


def test_after_funding_policy_uses_net_return_evidence():
    df = _scorecard(80)
    df["after_funding_long_short_spread"] = -0.001
    df["funding_adjusted_edge_flip"] = False
    df.loc[:14, "after_funding_long_short_spread"] = 0.003
    df.loc[:14, "ml_gate_risk_flags"] = ""
    df.loc[:14, "strongest_redundancy_level"] = "LOW_REDUNDANCY"
    df.loc[15:25, "after_funding_long_short_spread"] = 0.002
    df.loc[15:25, "funding_adjusted_edge_flip"] = True

    selected, summary = select_core_features(
        df,
        FeatureSelectionConfig(
            target_features=12,
            min_features=8,
            max_features=15,
            cluster_cap=3,
            selection_policy="after_funding_ls",
        ),
    )

    assert summary["selection_policy"] == "after_funding_ls"
    assert summary["selected_strict_ls_ic_aligned"] >= 8
    assert (selected["after_funding_long_short_spread"] > 0).all()
    assert not selected["funding_adjusted_edge_flip"].map(lambda x: str(x).lower() == "true").any()


def test_label_cols_for_mode():
    assert label_cols_for_mode("price")["24h"] == "ret_fwd_24h"
    assert label_cols_for_mode("after_funding")["24h"] == "ret_fwd_24h_after_funding"
    assert label_cols_for_mode("ls_utility_after_funding")["24h"] == "ls_utility_24h_after_funding"
    assert eval_label_cols_for_mode("ls_utility_after_funding")["24h"] == "ret_fwd_24h_after_funding"


def test_build_ls_utility_after_funding_targets_assigns_cross_section_tails():
    labels = pd.DataFrame({
        "timestamp": pd.to_datetime(["2026-01-01 00:00Z"] * 5 + ["2026-01-01 01:00Z"] * 5),
        "symbol": ["A", "B", "C", "D", "E"] * 2,
        "ret_fwd_1h_after_funding": [-0.04, -0.01, 0.0, 0.01, 0.04, 0.05, 0.02, 0.0, -0.02, -0.05],
    })

    out, manifest = build_ls_utility_after_funding_targets(labels, ["1h"], tail_fraction=0.20)

    assert manifest["status"] == "LS_UTILITY_AFTER_FUNDING_LABELS_COMPUTED"
    assert out["ls_utility_1h_after_funding"].tolist() == [-1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, -1.0]
    cov = manifest["coverage_by_horizon"][0]
    assert cov["long_rows"] == 2
    assert cov["short_rows"] == 2
    assert cov["middle_rows"] == 6


def test_walk_forward_months_has_no_lookahead():
    months = np.array([f"2025-{m:02d}" for m in range(1, 13)] + [f"2026-{m:02d}" for m in range(1, 7)])
    splits = walk_forward_months(months, min_train_months=12, max_splits=3)
    assert len(splits) == 3
    for train_months, test_month in splits:
        assert train_months[-1] < test_month
        assert test_month not in set(train_months)


def test_build_feature_matrix_schema_and_duplicate_policy(tmp_path):
    features_dir = tmp_path / "features"
    labels = pd.DataFrame({
        "timestamp": pd.to_datetime(["2026-01-01 00:00Z", "2026-01-01 00:00Z", "2026-01-01 01:00Z", "2026-01-01 01:00Z"]),
        "symbol": ["A", "B", "A", "B"],
        "ret_fwd_1h": [0.1, -0.1, 0.2, -0.2],
    })
    for fid, offset in [("factor_a", 0.0), ("factor_b", 1.0)]:
        d = features_dir / fid
        d.mkdir(parents=True)
        base = labels[["timestamp", "symbol"]].copy()
        first = base.assign(factor_value=[1 + offset, 2 + offset, 3 + offset, 4 + offset])
        second = base.assign(factor_value=[2 + offset, 3 + offset, 4 + offset, 5 + offset])
        pd.concat([first, second], ignore_index=True).to_parquet(d / "factor_values.parquet", index=False)

    x, valid_count, meta = build_feature_matrix(["factor_a", "factor_b"], features_dir, labels)
    assert x.shape == (4, 2)
    assert valid_count.tolist() == [2, 2, 2, 2]
    assert {m["duplicate_policy"] for m in meta} == {"last_of_2_aligned_blocks"}
    assert np.isfinite(x).all()


def test_script_manifest_disclaimer_constant():
    script = (SCRIPTS / "build_factor_ml_signal_prototype.py").read_text()
    assert "Research prototype only" in script
    assert "Not a trading signal" in script
    assert "ML_HOLD" in script
