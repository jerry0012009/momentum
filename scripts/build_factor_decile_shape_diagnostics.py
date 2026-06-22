#!/usr/bin/env python3
"""PM-27B: Direction-aware decile-level quantile shape diagnostics.

Reads factor_values parquet + labels parquet directly, computes 10-bucket
quantile returns per factor/horizon/month, and derives decile shape metrics.

Direction-awareness (PM-27B repair):
  - Loads expected_direction from factor_formula_registry for each factor
  - raw_decile 1..10 (D1=lowest factor value, D10=highest)
  - expected_order_decile: for positive = raw; for negative = 11 - raw;
    for conditional/missing = raw with flag
  - All shape metrics computed on expected-direction ordering
  - direction_handling: "positive_aligned" / "negative_flipped" / "raw_order_conditional"

Outputs (to factor_diagnostics/):
  - factor_decile_return_summary.csv
  - factor_decile_shape_summary.csv / .json
  - factor_decile_shape_payload.json   (compact, for PM-28 page integration)
  - factor_decile_shape_manifest.json
  - factor_decile_shape_timeseries.csv (monthly D10-D1 spread series)

Usage:
    python scripts/build_factor_decile_shape_diagnostics.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as sp_stats

# ── Constants ────────────────────────────────────────────────────────────────
WORKSPACE = Path(__file__).resolve().parent.parent
DATASET_ID = "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1"
FEATURES_DIR = WORKSPACE / "data" / "features" / DATASET_ID
LABELS_PATH = FEATURES_DIR / "labels.parquet"
STATE_PATH = (
    WORKSPACE
    / "research"
    / "factor_runs"
    / "crypto_top50_factor_library"
    / "factor_library_state.json"
)
DIAG_DIR = (
    WORKSPACE
    / "research"
    / "factor_runs"
    / "crypto_top50_factor_library"
    / "factor_diagnostics"
)
Q5_SUMMARY_PATH = DIAG_DIR / "factor_quantile_shape_summary.csv"

N_DECILES = 10
LABEL_HORIZONS = ["1h", "4h", "24h", "72h"]
LABEL_COLS = {
    "1h": "ret_fwd_1h",
    "4h": "ret_fwd_4h",
    "24h": "ret_fwd_24h",
    "72h": "ret_fwd_72h",
}
MIN_SYMBOLS = 5  # minimum symbols per timestamp to include
MIN_MONTHS = 3   # minimum months for classification


# ── Helpers ──────────────────────────────────────────────────────────────────

def _r2(x: float) -> float:
    return round(float(x), 8) if x is not None and not np.isnan(x) else None


def _r4(x: float) -> float:
    return round(float(x), 4) if x is not None and not np.isnan(x) else None


def load_direction_map() -> dict[str, str]:
    """Load expected_direction for every factor_id from the registry."""
    # Import REGISTRY from factor_formula_registry (same directory)
    scripts_dir = Path(__file__).resolve().parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from factor_formula_registry import REGISTRY

    direction_map: dict[str, str] = {}
    for spec in REGISTRY:
        direction_map[spec.factor_id] = spec.expected_direction
    return direction_map


def get_direction_handling(expected_direction: str) -> str:
    """Map expected_direction to direction_handling label."""
    if expected_direction == "positive":
        return "positive_aligned"
    elif expected_direction == "negative":
        return "negative_flipped"
    else:
        return "raw_order_conditional"


def reorder_for_direction(
    decile_returns: list[float | None],
    expected_direction: str,
) -> list[float | None]:
    """Reorder decile returns so that D1 = worst expected, D10 = best expected.

    For positive direction: D1=lowest factor → lowest expected return (raw order).
    For negative direction: D1=lowest factor → HIGHEST expected return (flip),
        so D1 becomes raw D10 and D10 becomes raw D1.
    For conditional/missing: use raw order (no flip).
    """
    if expected_direction == "negative":
        # Flip: expected_d1 = raw_d10, expected_d10 = raw_d1
        return list(reversed(decile_returns))
    else:
        # positive or conditional: raw order is fine
        return list(decile_returns)


def compute_decile_monotonicity(decile_returns: list[float | None]) -> tuple[float, str]:
    """Score 0-1 based on proportion of pairwise adjacent steps that are monotonic.

    Returns (score, class_str).
    """
    vals = [v for v in decile_returns if v is not None and not np.isnan(v)]
    if len(vals) < 3:
        return 0.0, "INSUFFICIENT"
    # Check both directions
    n_up = sum(1 for i in range(len(vals) - 1) if vals[i + 1] > vals[i])
    n_down = sum(1 for i in range(len(vals) - 1) if vals[i + 1] < vals[i])
    n_steps = len(vals) - 1
    mono_up = n_up / n_steps
    mono_down = n_down / n_steps
    score = max(mono_up, mono_down)
    if score >= 0.9:
        return score, "MONOTONIC_STRONG"
    elif score >= 0.7:
        return score, "MONOTONIC_WEAK"
    else:
        return score, "NON_MONOTONIC"


def compute_tail_concentration(decile_returns: list[float | None]) -> tuple[float, str]:
    """Measure how much of the total spread is driven by tail deciles vs middle.

    tail_concentration = |D10-D1| / (sum of all adjacent step absolute changes)
    High → tail-driven.  Returns (score, class_str).
    """
    vals = [v for v in decile_returns if v is not None and not np.isnan(v)]
    if len(vals) < 3:
        return 0.0, "INSUFFICIENT"
    spread = abs(vals[-1] - vals[0])
    total_steps = sum(abs(vals[i + 1] - vals[i]) for i in range(len(vals) - 1))
    if total_steps == 0:
        return 0.0, "FLAT"
    ratio = spread / total_steps
    # In a perfectly monotonic series, ratio ≈ 1.0 (all steps align).
    # If ratio is high, spread is mostly from the tails.
    if ratio >= 0.6:
        return ratio, "TAIL_DOMINANT"
    elif ratio >= 0.4:
        return ratio, "MODERATE"
    else:
        return ratio, "DISTRIBUTED"


def compute_middle_flatness(decile_returns: list[float | None]) -> float:
    """Mean absolute adjacent-step change for D3-D8 relative to total range.

    Low value → flat middle; high → active middle.
    Returns score 0-1 where 1 = perfectly flat middle.
    """
    vals = [v for v in decile_returns if v is not None and not np.isnan(v)]
    if len(vals) < 10:
        return np.nan
    rng = max(vals) - min(vals)
    if rng == 0:
        return 1.0
    mid_steps = [abs(vals[i + 1] - vals[i]) for i in range(2, 7)]  # D3→D4 ... D7→D8
    mid_avg = np.mean(mid_steps)
    # Normalize: if mid_avg is small relative to range, middle is flat
    flatness = 1.0 - min(mid_avg / (rng / (len(vals) - 1)), 1.0)
    return float(flatness)


def compute_u_shape_score(decile_returns: list[float | None]) -> float:
    """Measure U-shaped or inverted-U pattern.

    Compares tail returns to middle returns.  Positive → tails higher (U).
    Returns raw score (can be negative for inverted U).
    """
    vals = [v for v in decile_returns if v is not None and not np.isnan(v)]
    if len(vals) < 10:
        return np.nan
    tail_avg = (vals[0] + vals[-1]) / 2.0
    mid_avg = np.mean(vals[4:6])  # D5, D6
    return float(tail_avg - mid_avg)


def compute_nonlinearity_score(decile_returns: list[float | None]) -> float:
    """Residual std after fitting linear trend through decile returns.

    Higher → more nonlinear.  Returns residual std.
    """
    vals = [v for v in decile_returns if v is not None and not np.isnan(v)]
    if len(vals) < 4:
        return np.nan
    x = np.arange(len(vals), dtype=float)
    slope, intercept, _, _, _ = sp_stats.linregress(x, vals)
    predicted = slope * x + intercept
    resid = np.array(vals) - predicted
    return float(np.std(resid, ddof=1)) if len(resid) > 2 else np.nan


def classify_decile_shape(
    monotonicity_score: float,
    monotonicity_class: str,
    tail_concentration: float,
    tail_class: str,
    u_shape: float,
    nonlinearity: float,
    d10_minus_d1: float | None,
    n_months: int,
) -> str:
    """Assign one of the 8 decile shape classes."""
    if n_months < MIN_MONTHS:
        return "INSUFFICIENT_DATA"
    if monotonicity_class == "MONOTONIC_STRONG":
        return "DECILE_MONOTONIC_STRONG"
    if monotonicity_class == "MONOTONIC_WEAK":
        return "DECILE_MONOTONIC_WEAK"
    # Not strongly/weakly monotonic → check tail dependence
    if tail_class == "TAIL_DOMINANT":
        if not np.isnan(u_shape):
            if abs(u_shape) > 0.0 and u_shape > 0:
                return "BOTH_TAILS_U_SHAPED"
        # Check which tail dominates
        if d10_minus_d1 is not None and not np.isnan(d10_minus_d1):
            # If D1 > D10, bottom tail drives; if D10 > D1, top tail drives
            vals_abs = abs(d10_minus_d1) if d10_minus_d1 != 0 else 0
            if vals_abs > 0:
                return "TOP_TAIL_DEPENDENT"  # Could refine but this is a heuristic
        return "TOP_TAIL_DEPENDENT"
    if not np.isnan(nonlinearity) and nonlinearity > 0:
        return "NONLINEAR_MIXED"
    return "FLAT_NO_SHAPE"


def assess_consistency_with_q5(q5_class: str, decile_class: str) -> str:
    """Compare decile shape class to PM-26 Q5 shape class."""
    if decile_class == "INSUFFICIENT_DATA" or not q5_class or q5_class == "NO_CLEAR_SHAPE":
        return "INSUFFICIENT_DATA" if decile_class == "INSUFFICIENT_DATA" else "CONFLICTING"

    # Map Q5 classes to expected decile behavior
    q5_monotonic = q5_class in ("EXCELLENT_MONOTONIC", "WEAK_MONOTONIC")
    decile_monotonic = decile_class in ("DECILE_MONOTONIC_STRONG", "DECILE_MONOTONIC_WEAK")

    if q5_monotonic and decile_monotonic:
        return "CONSISTENT"
    if q5_monotonic and not decile_monotonic:
        return "DECILE_REVEALS_NONLINEARITY"
    if not q5_monotonic and decile_monotonic:
        return "DECILE_MORE_MONOTONIC"
    if "TAIL" in decile_class:
        return "DECILE_REVEALS_TAIL_DEPENDENCE"
    if "U_SHAPED" in decile_class:
        return "DECILE_REVEALS_NONLINEARITY"
    return "CONFLICTING"


def generate_notes(
    decile_class: str,
    consistency: str,
    d10_minus_d1: float | None,
    monotonicity_score: float,
    tail_class: str,
    expected_direction: str,
    direction_handling: str,
) -> tuple[str, str]:
    """Generate Chinese and English summary notes."""
    spread_sign = "正向" if d10_minus_d1 and d10_minus_d1 > 0 else "反向"
    spread_sign_en = "positive" if d10_minus_d1 and d10_minus_d1 > 0 else "negative"

    dir_note_zh = ""
    dir_note_en = ""
    if direction_handling == "negative_flipped":
        dir_note_zh = "（负向因子，已翻转十分位顺序）"
        dir_note_en = " (negative direction, decile order flipped)"
    elif direction_handling == "raw_order_conditional":
        dir_note_zh = "（条件方向，未翻转）"
        dir_note_en = " (conditional direction, raw order)"

    notes_zh = {
        "DECILE_MONOTONIC_STRONG": f"十分位回报呈{spread_sign}强单调排列，因子分层能力优秀{dir_note_zh}",
        "DECILE_MONOTONIC_WEAK": f"十分位回报大体呈{spread_sign}单调趋势，但存在波动{dir_note_zh}",
        "TOP_TAIL_DEPENDENT": f"十分位回报主要依赖顶部尾部分位，中间分位区分度低{dir_note_zh}",
        "BOTTOM_TAIL_DEPENDENT": f"十分位回报主要依赖底部尾部分位，中间分位区分度低{dir_note_zh}",
        "BOTH_TAILS_U_SHAPED": f"十分位回报呈U型分布，两端尾部回报高于中间{dir_note_zh}",
        "NONLINEAR_MIXED": f"十分位回报呈非线性混合模式，无明显单调趋势{dir_note_zh}",
        "FLAT_NO_SHAPE": f"十分位回报平坦，无明显形状特征{dir_note_zh}",
        "INSUFFICIENT_DATA": "数据不足，无法确定十分位形状",
    }

    notes_en = {
        "DECILE_MONOTONIC_STRONG": f"Decile returns show {spread_sign_en} monotonic pattern — strong factor separation{dir_note_en}",
        "DECILE_MONOTONIC_WEAK": f"Decile returns show generally {spread_sign_en} monotonic trend with some noise{dir_note_en}",
        "TOP_TAIL_DEPENDENT": f"Decile returns driven mainly by top tail; middle deciles show limited separation{dir_note_en}",
        "BOTTOM_TAIL_DEPENDENT": f"Decile returns driven mainly by bottom tail; middle deciles show limited separation{dir_note_en}",
        "BOTH_TAILS_U_SHAPED": f"Decile returns show U-shaped pattern — both tails outperform middle{dir_note_en}",
        "NONLINEAR_MIXED": f"Decile returns show nonlinear mixed pattern without clear monotonic trend{dir_note_en}",
        "FLAT_NO_SHAPE": f"Decile returns are flat — no discernible shape{dir_note_en}",
        "INSUFFICIENT_DATA": "Insufficient data to determine decile shape",
    }

    zh = notes_zh.get(decile_class, "未知形状")
    en = notes_en.get(decile_class, "Unknown shape")

    cons_zh = {
        "CONSISTENT": "与Q5分类一致",
        "DECILE_MORE_MONOTONIC": "十分位揭示了比Q5更强的单调性",
        "DECILE_REVEALS_TAIL_DEPENDENCE": "十分位揭示了尾部依赖性",
        "DECILE_REVEALS_NONLINEARITY": "十分位揭示了非线性特征",
        "CONFLICTING": "与Q5分类存在冲突",
        "INSUFFICIENT_DATA": "",
    }
    cons_en = {
        "CONSISTENT": "consistent with Q5 classification",
        "DECILE_MORE_MONOTONIC": "deciles reveal stronger monotonicity than Q5",
        "DECILE_REVEALS_TAIL_DEPENDENCE": "deciles reveal tail dependence",
        "DECILE_REVEALS_NONLINEARITY": "deciles reveal nonlinearity",
        "CONFLICTING": "conflicts with Q5 classification",
        "INSUFFICIENT_DATA": "",
    }
    c_zh = cons_zh.get(consistency, "")
    c_en = cons_en.get(consistency, "")
    if c_zh:
        zh += f"；{c_zh}"
    if c_en:
        en += f"; {c_en}"

    return zh, en


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    t_start = time.time()
    print("=" * 70)
    print("PM-27B: Direction-aware decile-level quantile shape diagnostics")
    print("=" * 70)

    # Ensure output dir
    DIAG_DIR.mkdir(parents=True, exist_ok=True)

    # Load state
    state = json.loads(STATE_PATH.read_text())
    factor_ids = state["computed_factor_ids"]
    print(f"  Factors from state: {len(factor_ids)}")

    # Load expected_direction from registry
    direction_map = load_direction_map()
    print(f"  Direction map loaded: {len(direction_map)} factors")
    dir_counts = {}
    for d in direction_map.values():
        dir_counts[d] = dir_counts.get(d, 0) + 1
    for k, v in sorted(dir_counts.items()):
        print(f"    {k}: {v}")

    # Load Q5 shape summary (PM-26)
    q5_map: dict[tuple[str, str], dict] = {}
    if Q5_SUMMARY_PATH.exists():
        q5_df = pd.read_csv(Q5_SUMMARY_PATH)
        for _, row in q5_df.iterrows():
            q5_map[(row["factor_id"], row["horizon"])] = row.to_dict()
        print(f"  PM-26 Q5 shape rows loaded: {len(q5_map)}")

    # Load labels
    print("  Loading labels...", end=" ", flush=True)
    labels = pd.read_parquet(LABELS_PATH)
    labels["timestamp"] = pd.to_datetime(labels["timestamp"], utc=True)
    labels = labels.sort_values("timestamp").reset_index(drop=True)
    print(f"done ({len(labels)} rows)")

    # Storage
    decile_return_rows: list[dict] = []
    timeseries_rows: list[dict] = []

    # Process each factor
    for fi, fid in enumerate(factor_ids):
        fv_path = FEATURES_DIR / fid / "factor_values.parquet"
        if not fv_path.exists():
            print(f"  [{fi+1}/{len(factor_ids)}] {fid}: MISSING, skip")
            continue

        # Get expected direction for this factor
        expected_dir = direction_map.get(fid, "conditional")

        fv = pd.read_parquet(fv_path, columns=["timestamp", "symbol", "factor_value"])
        fv["timestamp"] = pd.to_datetime(fv["timestamp"], utc=True)

        # Merge with labels
        merged = fv.merge(labels, on=["timestamp", "symbol"], how="inner")
        merged = merged.dropna(subset=["factor_value"])
        merged = merged.sort_values("timestamp").reset_index(drop=True)

        if len(merged) == 0:
            print(f"  [{fi+1}/{len(factor_ids)}] {fid}: empty merge, skip")
            continue

        # Add month period
        merged["_period"] = merged["timestamp"].dt.to_period("M")

        for hz in LABEL_HORIZONS:
            ret_col = LABEL_COLS[hz]
            hz_merged = merged.dropna(subset=[ret_col]).copy()
            if len(hz_merged) < MIN_SYMBOLS * N_DECILES:
                continue

            # Rank per timestamp
            hz_merged["_rank"] = hz_merged.groupby("timestamp")["factor_value"].rank(method="first")
            hz_merged["_count"] = hz_merged.groupby("timestamp")["factor_value"].transform("count")
            hz_merged["decile"] = (
                ((hz_merged["_rank"] - 1) * N_DECILES / hz_merged["_count"])
                .astype(int)
                .clip(0, N_DECILES - 1)
            )

            # Per-timestamp decile means
            decile_ts = (
                hz_merged.groupby(["timestamp", "decile"])[ret_col]
                .mean()
                .unstack(fill_value=np.nan)
            )
            decile_ts.index = pd.to_datetime(decile_ts.index, utc=True)
            decile_ts["_period"] = decile_ts.index.to_period("M")

            # Monthly aggregation
            for period_val, period_grp in decile_ts.groupby("_period"):
                period_str = str(period_val)
                for d in range(N_DECILES):
                    if d in period_grp.columns:
                        d_vals = period_grp[d].dropna()
                        if len(d_vals) > 0:
                            raw_decile = d + 1  # 1-indexed

                            # Direction-aware expected order decile
                            if expected_dir == "negative":
                                expected_order_decile = 11 - raw_decile
                            else:
                                expected_order_decile = raw_decile

                            decile_return_rows.append({
                                "factor_id": fid,
                                "horizon": hz,
                                "month": period_str,
                                "raw_decile": raw_decile,
                                "expected_order_decile": expected_order_decile,
                                "expected_direction": expected_dir,
                                "direction_handling": get_direction_handling(expected_dir),
                                "mean_return": _r2(float(d_vals.mean())),
                                "median_return": _r2(float(d_vals.median())),
                                "n_obs": int(len(d_vals)),
                            })

                # D10-D1 spread for timeseries (direction-aware)
                # For raw: D10=9, D1=0. For negative-flipped: spread is inverted.
                if 9 in period_grp.columns and 0 in period_grp.columns:
                    raw_spread = period_grp[9] - period_grp[0]
                    raw_spread = raw_spread.dropna()
                    if len(raw_spread) > 0:
                        # Direction-aware spread: for negative, flip sign
                        if expected_dir == "negative":
                            da_spread = -raw_spread
                        else:
                            da_spread = raw_spread

                        timeseries_rows.append({
                            "factor_id": fid,
                            "horizon": hz,
                            "month": period_str,
                            "expected_direction": expected_dir,
                            "direction_handling": get_direction_handling(expected_dir),
                            "d10_minus_d1_mean": _r2(float(da_spread.mean())),
                            "d10_minus_d1_median": _r2(float(da_spread.median())),
                            "n_timestamps": int(len(da_spread)),
                        })

        if (fi + 1) % 20 == 0 or fi == len(factor_ids) - 1:
            print(f"  [{fi+1}/{len(factor_ids)}] processed", flush=True)

    # Build raw return summary
    ret_df = pd.DataFrame(decile_return_rows)
    print(f"\n  Total decile return rows: {len(ret_df)}")
    print(f"  Unique factors: {ret_df['factor_id'].nunique()}")

    # Save raw return summary
    ret_csv = DIAG_DIR / "factor_decile_return_summary.csv"
    ret_df.to_csv(ret_csv, index=False)
    print(f"  Saved: {ret_csv.name}")

    # Build shape summary per factor × horizon
    shape_rows: list[dict] = []
    grouped = ret_df.groupby(["factor_id", "horizon"])

    for (fid, hz), grp in grouped:
        months = sorted(grp["month"].unique())
        n_months = len(months)

        # Get expected direction
        expected_dir = direction_map.get(fid, "conditional")
        dir_handling = get_direction_handling(expected_dir)

        # Overall decile returns (mean across months) in raw order
        raw_decile_means = []
        for d in range(1, N_DECILES + 1):
            d_data = grp[grp["raw_decile"] == d]["mean_return"]
            if len(d_data) > 0:
                raw_decile_means.append(float(d_data.mean()))
            else:
                raw_decile_means.append(None)

        # Direction-aware reorder
        expected_decile_means = reorder_for_direction(raw_decile_means, expected_dir)

        # D10-D1 spread per month (direction-aware)
        monthly_spreads = []
        for m in months:
            m_grp = grp[grp["month"] == m]
            d10 = m_grp[m_grp["raw_decile"] == 10]["mean_return"]
            d1 = m_grp[m_grp["raw_decile"] == 1]["mean_return"]
            if len(d10) > 0 and len(d1) > 0:
                raw_spread = float(d10.values[0]) - float(d1.values[0])
                if expected_dir == "negative":
                    monthly_spreads.append(-raw_spread)
                else:
                    monthly_spreads.append(raw_spread)

        d10_minus_d1_mean = float(np.mean(monthly_spreads)) if monthly_spreads else None
        d10_minus_d1_positive_rate = (
            float(np.mean([s > 0 for s in monthly_spreads])) if monthly_spreads else 0.0
        )

        # Linear slope through direction-aware decile means
        valid_deciles = [(i, v) for i, v in enumerate(expected_decile_means) if v is not None]
        if len(valid_deciles) >= 3:
            x_arr = np.array([v[0] for v in valid_deciles], dtype=float)
            y_arr = np.array([v[1] for v in valid_deciles], dtype=float)
            slope, _, r_val, _, _ = sp_stats.linregress(x_arr, y_arr)
            spearman_corr = float(sp_stats.spearmanr(x_arr, y_arr).correlation)
        else:
            slope, spearman_corr = 0.0, 0.0

        # Monotonicity (direction-aware)
        mono_score, mono_class = compute_decile_monotonicity(expected_decile_means)

        # Tail concentration (direction-aware)
        tail_score, tail_class = compute_tail_concentration(expected_decile_means)

        # Middle flatness (direction-aware)
        mid_flat = compute_middle_flatness(expected_decile_means)

        # U-shape (direction-aware)
        u_score = compute_u_shape_score(expected_decile_means)

        # Nonlinearity (direction-aware)
        nl_score = compute_nonlinearity_score(expected_decile_means)

        # Shape classification (direction-aware)
        shape_class = classify_decile_shape(
            mono_score, mono_class, tail_score, tail_class,
            u_score, nl_score, d10_minus_d1_mean, n_months,
        )

        # Q5 shape class from PM-26
        q5_info = q5_map.get((fid, hz), {})
        q5_class = q5_info.get("quantile_shape_class", "")

        # Consistency
        consistency = assess_consistency_with_q5(q5_class, shape_class)

        # Notes (direction-aware)
        note_zh, note_en = generate_notes(
            shape_class, consistency, d10_minus_d1_mean, mono_score, tail_class,
            expected_dir, dir_handling,
        )

        row = {
            "factor_id": fid,
            "horizon": hz,
            "n_months": n_months,
            "n_deciles": N_DECILES,
            "expected_direction": expected_dir,
            "direction_handling": dir_handling,
        }

        # Raw decile returns
        for d in range(1, N_DECILES + 1):
            row[f"raw_d{d}_return"] = _r2(raw_decile_means[d - 1])

        # Direction-aware (expected-order) decile returns
        for d in range(1, N_DECILES + 1):
            row[f"expected_d{d}_return"] = _r2(expected_decile_means[d - 1])

        # Direction-aware metrics
        row.update({
            "expected_d10_minus_d1_spread": _r2(d10_minus_d1_mean),
            "expected_d10_minus_d1_positive_month_rate": _r4(d10_minus_d1_positive_rate),
            "direction_aware_slope": _r2(float(slope)),
            "direction_aware_spearman_corr": _r4(spearman_corr),
            "direction_aware_monotonicity_score": _r4(mono_score),
            "direction_aware_monotonicity_class": mono_class,
            "tail_concentration_score": _r4(tail_score),
            "tail_concentration_class": tail_class,
            "middle_bucket_flatness": _r4(mid_flat) if not np.isnan(mid_flat) else None,
            "u_shape_score": _r2(u_score) if not np.isnan(u_score) else None,
            "nonlinearity_score": _r2(nl_score) if not np.isnan(nl_score) else None,
            "decile_shape_class": shape_class,
            "q5_shape_class_from_pm26": q5_class,
            "shape_consistency_with_q5": consistency,
            "main_decile_note_zh": note_zh,
            "main_decile_note_en": note_en,
        })
        shape_rows.append(row)

    shape_df = pd.DataFrame(shape_rows)

    # Save shape summary CSV
    shape_csv = DIAG_DIR / "factor_decile_shape_summary.csv"
    shape_df.to_csv(shape_csv, index=False)
    print(f"  Saved: {shape_csv.name}")

    # Save shape summary JSON
    shape_json = DIAG_DIR / "factor_decile_shape_summary.json"
    shape_json.write_text(json.dumps(shape_rows, indent=2, ensure_ascii=False, default=str))
    print(f"  Saved: {shape_json.name}")

    # Save timeseries CSV
    ts_df = pd.DataFrame(timeseries_rows)
    ts_csv = DIAG_DIR / "factor_decile_shape_timeseries.csv"
    ts_df.to_csv(ts_csv, index=False)
    print(f"  Saved: {ts_csv.name} ({len(ts_df)} rows)")

    # Build compact payload for PM-28 page integration
    payload_factors: list[dict] = []
    for fid in sorted(shape_df["factor_id"].unique()):
        f_rows = shape_df[shape_df["factor_id"] == fid]
        horizons: dict[str, dict] = {}
        for _, row in f_rows.iterrows():
            hz = row["horizon"]
            hz_data: dict = {
                "n_months": int(row["n_months"]),
                "expected_direction": row["expected_direction"],
                "direction_handling": row["direction_handling"],
                "raw_decile_returns": [
                    _r2(row.get(f"raw_d{d}_return")) for d in range(1, N_DECILES + 1)
                ],
                "expected_order_decile_returns": [
                    _r2(row.get(f"expected_d{d}_return")) for d in range(1, N_DECILES + 1)
                ],
                "expected_d10_minus_d1_spread": _r2(row["expected_d10_minus_d1_spread"]),
                "expected_d10_minus_d1_positive_month_rate": _r4(row["expected_d10_minus_d1_positive_month_rate"]),
                "direction_aware_slope": _r2(row["direction_aware_slope"]),
                "direction_aware_spearman_corr": _r4(row["direction_aware_spearman_corr"]),
                "direction_aware_monotonicity_score": _r4(row["direction_aware_monotonicity_score"]),
                "direction_aware_monotonicity_class": row["direction_aware_monotonicity_class"],
                "tail_concentration_score": _r4(row["tail_concentration_score"]),
                "tail_concentration_class": row["tail_concentration_class"],
                "decile_shape_class": row["decile_shape_class"],
                "q5_shape_class_from_pm26": row["q5_shape_class_from_pm26"],
                "shape_consistency_with_q5": row["shape_consistency_with_q5"],
                "note_zh": row["main_decile_note_zh"],
                "note_en": row["main_decile_note_en"],
            }
            horizons[hz] = hz_data
        payload_factors.append({"factor_id": fid, "horizons": horizons})

    payload = {
        "version": "pm27b_decile_v2",
        "n_deciles": N_DECILES,
        "n_factors": len(payload_factors),
        "factors": payload_factors,
    }
    payload_path = DIAG_DIR / "factor_decile_shape_payload.json"
    payload_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
    print(f"  Saved: {payload_path.name}")

    # Manifest
    manifest = {
        "version": "pm27b_decile_v2",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "dataset_id": DATASET_ID,
        "n_deciles": N_DECILES,
        "n_factors": int(shape_df["factor_id"].nunique()),
        "n_factor_horizon_pairs": len(shape_df),
        "n_return_rows": len(ret_df),
        "n_timeseries_rows": len(ts_df),
        "direction_handling_distribution": shape_df["direction_handling"].value_counts().to_dict(),
        "expected_direction_distribution": shape_df["expected_direction"].value_counts().to_dict(),
        "decile_shape_distribution": shape_df["decile_shape_class"].value_counts().to_dict(),
        "tail_concentration_distribution": shape_df["tail_concentration_class"].value_counts().to_dict(),
        "consistency_distribution": shape_df["shape_consistency_with_q5"].value_counts().to_dict(),
        "payload_size_bytes": payload_path.stat().st_size,
        "source_files": {
            "labels": str(LABELS_PATH),
            "q5_summary": str(Q5_SUMMARY_PATH),
            "state": str(STATE_PATH),
        },
        "output_files": [str(f.name) for f in DIAG_DIR.iterdir() if f.name.startswith("factor_decile")],
    }
    manifest_path = DIAG_DIR / "factor_decile_shape_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, default=str))
    print(f"  Saved: {manifest_path.name}")

    # Summary
    elapsed = time.time() - t_start
    print(f"\n{'=' * 70}")
    print(f"Done in {elapsed:.1f}s")
    print(f"  Factors: {shape_df['factor_id'].nunique()}")
    print(f"  Factor-horizon pairs: {len(shape_df)}")
    print(f"  Direction handling distribution:")
    for cls, cnt in shape_df["direction_handling"].value_counts().items():
        print(f"    {cls}: {cnt}")
    print(f"  Direction-aware decile shape classes:")
    for cls, cnt in shape_df["decile_shape_class"].value_counts().items():
        print(f"    {cls}: {cnt}")
    print(f"  Consistency with Q5:")
    for cls, cnt in shape_df["shape_consistency_with_q5"].value_counts().items():
        print(f"    {cls}: {cnt}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
