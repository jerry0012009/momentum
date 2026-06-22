#!/usr/bin/env python3
"""
PM-26: Quantile Shape and Rolling Stability Diagnostics

Builds quantile shape diagnostics (monotonicity, tail concentration, slope)
and rolling stability diagnostics (IC/LS rolling windows, deterioration detection)
for all registered factors across 4 horizons.

Outputs (7 files):
  - factor_quantile_shape_summary.csv + .json
  - factor_rolling_stability_summary.csv + .json
  - factor_shape_stability_timeseries.csv
  - factor_shape_stability_payload.json
  - factor_shape_stability_manifest.json
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as sp_stats

# ── Paths ──────────────────────────────────────────────────────────────────
BASE = Path("research/factor_runs/crypto_top50_factor_library")
DIAG = BASE / "factor_diagnostics"
EVAL = BASE / "factor_level_evaluation"
STATE_FILE = BASE / "factor_library_state.json"

QR_FILE = EVAL / "factor_level_period_quantile_return_summary.csv"
LS_PERIOD_FILE = EVAL / "factor_level_period_long_short_summary.csv"
IC_FILE = DIAG / "factor_monthly_ic_series.csv"
LS_FILE = DIAG / "factor_monthly_long_short_series.csv"
DIAG_SUMMARY = DIAG / "factor_diagnostics_summary.csv"


# ── Monotonicity / shape helpers ───────────────────────────────────────────
def _monotonicity_score(values: list[float], expected_direction: str) -> float:
    """Share of adjacent steps going in the expected direction."""
    if len(values) < 2:
        return 0.0
    sign = 1.0 if expected_direction == "positive" else -1.0
    good = sum(
        1 for i in range(len(values) - 1) if (values[i + 1] - values[i]) * sign >= 0
    )
    return good / (len(values) - 1)


def _classify_monotonicity(score: float, n_buckets: int, n_months: int) -> str:
    if n_months < 6 or n_buckets < 3:
        return "INSUFFICIENT_DATA"
    if score >= 0.9:
        return "MONOTONIC_STRONG"
    if score >= 0.7:
        return "MONOTONIC_WEAK"
    # Check for U-shape or reversal: endpoints worse than middle
    return "FLAT_NO_SHAPE"


def _tail_concentration(values: list[float]) -> tuple[float, str]:
    """How much return is concentrated in tail buckets vs middle."""
    if len(values) < 3:
        return 0.0, "INSUFFICIENT_DATA"
    arr = np.array(values)
    tail = abs(arr[0] - arr[-1])
    mid_range = np.ptp(arr)
    if mid_range == 0:
        return 0.0, "FLAT_NO_SHAPE"
    # Tail share: spread vs total range
    score = tail / mid_range if mid_range > 0 else 0.0
    if score > 0.8:
        return score, "TAIL_DOMINANT"
    if score > 0.5:
        return score, "TAIL_HEAVY"
    return score, "BALANCED"


def _detect_u_shape_or_reversal(values: list[float], expected_direction: str) -> bool:
    """Returns True if the shape is U-shaped or has a reversal pattern."""
    if len(values) < 4:
        return False
    arr = np.array(values)
    sign = 1 if expected_direction == "positive" else -1
    # Check if middle buckets have higher returns than endpoints (reversal)
    mid_mean = np.mean(arr[1:-1])
    endpoint_mean = (arr[0] + arr[-1]) / 2
    # U-shape: endpoints better than middle (opposite of monotonic)
    if (endpoint_mean - mid_mean) * sign > 0:
        return True
    # Check for sign reversals in adjacent steps
    diffs = np.diff(arr) * sign
    neg_steps = np.sum(diffs < 0)
    if neg_steps > len(diffs) * 0.6:
        return True
    return False


def _quantile_shape_class(mono_class: str, mono_score: float, spearman: float) -> str:
    if mono_class == "INSUFFICIENT_DATA":
        return "INSUFFICIENT_DATA"
    if mono_class == "MONOTONIC_STRONG" and abs(spearman) > 0.85:
        return "EXCELLENT_MONOTONIC"
    if mono_class == "MONOTONIC_STRONG":
        return "STRONG_MONOTONIC"
    if mono_class == "MONOTONIC_WEAK" or abs(spearman) > 0.6:
        return "WEAK_MONOTONIC"
    if abs(spearman) > 0.4:
        return "MIXED_SHAPE"
    return "NO_CLEAR_SHAPE"


def _shape_notes_zh(mono_class: str, qclass: str, slope: float, spread: float) -> str:
    if mono_class == "INSUFFICIENT_DATA":
        return "数据不足，无法判断分位数形状"
    if qclass in ("EXCELLENT_MONOTONIC", "STRONG_MONOTONIC"):
        d = "正向" if slope > 0 else "反向"
        return f"分位数回报呈{d}单调排列，因子分层能力优秀"
    if qclass == "WEAK_MONOTONIC":
        return "分位数回报大体呈单调趋势，但存在波动"
    if qclass == "MIXED_SHAPE":
        return "分位数回报模式混合，分层信号不够清晰"
    return "分位数回报无明显规律，因子分层能力弱"


def _shape_notes_en(mono_class: str, qclass: str, slope: float, spread: float) -> str:
    if mono_class == "INSUFFICIENT_DATA":
        return "Insufficient data to assess quantile shape"
    if qclass in ("EXCELLENT_MONOTONIC", "STRONG_MONOTONIC"):
        d = "positive" if slope > 0 else "negative"
        return f"Quantile returns show {d} monotonic pattern — strong factor separation"
    if qclass == "WEAK_MONOTONIC":
        return "Quantile returns show generally monotonic trend with some noise"
    if qclass == "MIXED_SHAPE":
        return "Mixed quantile return pattern — factor signal is inconsistent"
    return "No clear quantile return pattern — weak factor separation"


# ── Rolling stability helpers ──────────────────────────────────────────────
def _stability_score(
    ic_pos_rate: float,
    ls_pos_rate: float,
    recent_ic_delta: float,
    recent_ls_delta: float,
    rolling_ic_min: float,
    n_months: int,
) -> float:
    """Composite 0-100 stability score."""
    if n_months < 6:
        return 0.0
    s = 0.0
    # IC consistency (30 pts)
    s += min(ic_pos_rate * 30, 30)
    # LS consistency (20 pts)
    s += min(ls_pos_rate * 20, 20)
    # No deterioration (25 pts): penalize if recent < full
    det_penalty = max(0, -recent_ic_delta * 500)  # scale
    s += max(0, 25 - det_penalty)
    # Rolling IC never deeply negative (15 pts)
    if rolling_ic_min > -0.05:
        s += 15
    elif rolling_ic_min > -0.1:
        s += 10
    elif rolling_ic_min > -0.2:
        s += 5
    # Duration bonus (10 pts)
    s += min(n_months / 24 * 10, 10)
    return round(min(s, 100), 1)


def _classify_stability(score, ic_pos_rate, ls_pos_rate, recent_ic_delta, n_months):
    if n_months < 6:
        return "INSUFFICIENT_HISTORY"
    if score >= 70 and ic_pos_rate >= 0.7 and recent_ic_delta >= -0.02:
        return "STABLE_POSITIVE"
    if score >= 50 and ic_pos_rate >= 0.5:
        return "STABLE_WEAK"
    if recent_ic_delta < -0.05 or (recent_ic_delta < -0.03 and ic_pos_rate < 0.5):
        return "RECENT_DETERIORATION"
    # Check for sign flips
    if ic_pos_rate < 0.4 and ls_pos_rate < 0.4:
        return "UNSTABLE_SIGN_FLIP"
    if 0.4 <= ic_pos_rate <= 0.6:
        return "REGIME_OR_PERIOD_DEPENDENT"
    return "STABLE_WEAK"


def _stability_notes_zh(cls: str) -> str:
    notes = {
        "STABLE_POSITIVE": "因子近期表现稳定且方向一致，适合作为组合因子之一",
        "STABLE_WEAK": "因子表现基本稳定但信号偏弱，可作为辅助因子",
        "RECENT_DETERIORATION": "因子近期信号明显恶化，需关注是否为结构性变化",
        "REGIME_OR_PERIOD_DEPENDENT": "因子表现依赖市场环境，建议结合市场状态使用",
        "UNSTABLE_SIGN_FLIP": "因子信号方向不稳定，不建议单独使用",
        "INSUFFICIENT_HISTORY": "历史数据不足，暂无法评估稳定性",
    }
    return notes.get(cls, "")


def _stability_notes_en(cls: str) -> str:
    notes = {
        "STABLE_POSITIVE": "Factor shows stable positive performance — suitable for portfolio inclusion",
        "STABLE_WEAK": "Factor is stable but weak — consider as auxiliary signal",
        "RECENT_DETERIORATION": "Recent performance deterioration detected — monitor for structural change",
        "REGIME_OR_PERIOD_DEPENDENT": "Factor performance is regime-dependent — use with market state overlay",
        "UNSTABLE_SIGN_FLIP": "Factor signal direction is unstable — not recommended standalone",
        "INSUFFICIENT_HISTORY": "Insufficient history to assess stability",
    }
    return notes.get(cls, "")


# ── Main computation ───────────────────────────────────────────────────────
def build_quantile_shape(qr_df: pd.DataFrame, diag_df: pd.DataFrame) -> pd.DataFrame:
    """Build quantile shape diagnostics per factor_id, horizon."""
    rows = []
    # Get expected_direction from diagnostics summary
    direction_map = dict(zip(diag_df["factor_id"], diag_df["expected_direction"]))

    for (fid, hz), grp in qr_df.groupby(["factor_id", "horizon"]):
        months = sorted(grp["period"].unique())
        n_months = len(months)
        buckets = sorted(grp["bucket"].unique())
        n_buckets = len(buckets)
        expected_dir = direction_map.get(fid, "positive")

        # Aggregate mean return per bucket across all months
        bucket_means = []
        monthly_spreads = []
        for b in buckets:
            bm = grp[grp["bucket"] == b]["mean_forward_return"].mean()
            bucket_means.append(bm)

        # Monthly spreads (high - low bucket per month)
        for m in months:
            mgrp = grp[grp["period"] == m].sort_values("bucket")
            if len(mgrp) >= 2:
                mvals = mgrp["mean_forward_return"].values
                spread = mvals[-1] - mvals[0]
                monthly_spreads.append(spread)

        q_low = bucket_means[0] if bucket_means else np.nan
        q_high = bucket_means[-1] if bucket_means else np.nan
        q_spread = q_high - q_low if bucket_means else np.nan

        # Linear slope across ordered buckets
        if n_buckets >= 2:
            slope, _, _, _, _ = sp_stats.linregress(range(n_buckets), bucket_means)
        else:
            slope = np.nan

        # Spearman correlation: bucket index vs mean return
        if n_buckets >= 3:
            spearman_corr, _ = sp_stats.spearmanr(range(n_buckets), bucket_means)
        else:
            spearman_corr = np.nan

        # Monotonicity
        mono_score = _monotonicity_score(bucket_means, expected_dir)
        mono_class = _classify_monotonicity(mono_score, n_buckets, n_months)

        # U-shape detection
        if mono_class not in ("INSUFFICIENT_DATA",) and _detect_u_shape_or_reversal(
            bucket_means, expected_dir
        ):
            mono_class = "U_SHAPED_OR_REVERSAL"

        # Tail concentration
        tail_score, tail_class = _tail_concentration(bucket_means)

        # Check if tail dominates (tail buckets have much more return than middle)
        if n_buckets >= 4:
            arr = np.array(bucket_means)
            tail_ret = abs(arr[0]) + abs(arr[-1])
            mid_ret = np.sum(np.abs(arr[1:-1]))
            if mid_ret > 0 and tail_ret / mid_ret > 1.5:
                tail_class = "TAIL_DEPENDENT"
                if mono_class in ("FLAT_NO_SHAPE", "MONOTONIC_WEAK"):
                    mono_class = "TAIL_DEPENDENT"

        # Positive spread month rate
        pos_spread_rate = (
            sum(1 for s in monthly_spreads if s > 0) / len(monthly_spreads)
            if monthly_spreads
            else 0.0
        )
        # Adjust for expected direction: if negative, negative spread is "positive"
        if expected_dir == "negative":
            neg_spreads = [s for s in monthly_spreads if s < 0]
            pos_spread_rate = len(neg_spreads) / len(monthly_spreads) if monthly_spreads else 0.0

        qclass = _quantile_shape_class(mono_class, mono_score, spearman_corr)
        note_zh = _shape_notes_zh(mono_class, qclass, slope, q_spread)
        note_en = _shape_notes_en(mono_class, qclass, slope, q_spread)

        rows.append(
            {
                "factor_id": fid,
                "horizon": hz,
                "n_months": n_months,
                "n_quantile_buckets": n_buckets,
                "q_low_return": round(q_low, 8) if not np.isnan(q_low) else None,
                "q_high_return": round(q_high, 8) if not np.isnan(q_high) else None,
                "q_spread_return": round(q_spread, 8) if not np.isnan(q_spread) else None,
                "q_return_slope": round(slope, 10) if not np.isnan(slope) else None,
                "q_spearman_corr": round(spearman_corr, 4) if not np.isnan(spearman_corr) else None,
                "monotonicity_score": round(mono_score, 4),
                "monotonicity_class": mono_class,
                "tail_concentration_score": round(tail_score, 4),
                "tail_concentration_class": tail_class,
                "positive_spread_month_rate": round(pos_spread_rate, 4),
                "quantile_shape_class": qclass,
                "main_shape_note_zh": note_zh,
                "main_shape_note_en": note_en,
            }
        )

    return pd.DataFrame(rows)


def build_rolling_stability(
    ic_df: pd.DataFrame, ls_df: pd.DataFrame, rolling_windows: list[int]
) -> pd.DataFrame:
    """Build rolling stability diagnostics per factor_id, horizon."""
    rows = []

    for (fid, hz), ic_grp in ic_df.groupby(["factor_id", "horizon"]):
        ic_grp = ic_grp.sort_values("month").reset_index(drop=True)
        ls_grp = ls_df[(ls_df["factor_id"] == fid) & (ls_df["horizon"] == hz)]
        ls_grp = ls_grp.sort_values("month").reset_index(drop=True)

        n_months = len(ic_grp)
        ic_vals = ic_grp["rank_ic"].values
        ls_vals = ls_grp["long_short_return"].values if len(ls_grp) > 0 else np.array([])

        # Rolling IC stats
        def rolling_mean_latest(arr, w):
            if len(arr) < w:
                return np.nan
            return float(np.mean(arr[-w:]))

        def rolling_min(arr, w):
            if len(arr) < w:
                return np.nan
            return float(
                min(np.mean(arr[i : i + w]) for i in range(len(arr) - w + 1))
            )

        def rolling_max(arr, w):
            if len(arr) < w:
                return np.nan
            return float(
                max(np.mean(arr[i : i + w]) for i in range(len(arr) - w + 1))
            )

        w3, w6 = rolling_windows[0], rolling_windows[1]

        row = {
            "factor_id": fid,
            "horizon": hz,
            "n_months": n_months,
        }

        for w in rolling_windows:
            prefix = f"rolling_ic_{w}m"
            row[f"{prefix}_mean_latest"] = round(rolling_mean_latest(ic_vals, w), 6) if n_months >= w else None
            row[f"{prefix}_min"] = round(rolling_min(ic_vals, w), 6) if n_months >= w else None
            row[f"{prefix}_max"] = round(rolling_max(ic_vals, w), 6) if n_months >= w else None

            if len(ls_vals) >= w:
                row[f"rolling_ls_{w}m_mean_latest"] = round(rolling_mean_latest(ls_vals, w), 8)
            else:
                row[f"rolling_ls_{w}m_mean_latest"] = None

        # Positive month rates
        ic_pos_rate = float(np.mean(ic_vals > 0)) if n_months > 0 else 0.0
        ls_pos_rate = float(np.mean(ls_vals > 0)) if len(ls_vals) > 0 else 0.0
        row["ic_positive_month_rate"] = round(ic_pos_rate, 4)
        row["ls_positive_month_rate"] = round(ls_pos_rate, 4)

        # Recent 6m vs full period
        recent_n = min(6, n_months)
        recent_ic = float(np.mean(ic_vals[-recent_n:])) if n_months > 0 else np.nan
        full_ic = float(np.mean(ic_vals)) if n_months > 0 else np.nan
        row["recent_6m_ic_mean"] = round(recent_ic, 6) if not np.isnan(recent_ic) else None
        row["full_period_ic_mean"] = round(full_ic, 6) if not np.isnan(full_ic) else None
        row["recent_vs_full_ic_delta"] = (
            round(recent_ic - full_ic, 6) if not (np.isnan(recent_ic) or np.isnan(full_ic)) else None
        )

        recent_ls = float(np.mean(ls_vals[-recent_n:])) if len(ls_vals) > 0 else np.nan
        full_ls = float(np.mean(ls_vals)) if len(ls_vals) > 0 else np.nan
        row["recent_6m_ls_mean"] = round(recent_ls, 8) if not np.isnan(recent_ls) else None
        row["full_period_ls_mean"] = round(full_ls, 8) if not np.isnan(full_ls) else None
        row["recent_vs_full_ls_delta"] = (
            round(recent_ls - full_ls, 8) if not (np.isnan(recent_ls) or np.isnan(full_ls)) else None
        )

        # Stability score & class
        r_ic_delta = row.get("recent_vs_full_ic_delta") or 0
        r_ls_delta = row.get("recent_vs_full_ls_delta") or 0
        r_ic_min = row.get(f"rolling_ic_{w3}m_min") or 0

        s_score = _stability_score(ic_pos_rate, ls_pos_rate, r_ic_delta, r_ls_delta, r_ic_min, n_months)
        s_class = _classify_stability(s_score, ic_pos_rate, ls_pos_rate, r_ic_delta, n_months)
        row["stability_score"] = s_score
        row["stability_class"] = s_class
        row["main_stability_note_zh"] = _stability_notes_zh(s_class)
        row["main_stability_note_en"] = _stability_notes_en(s_class)

        rows.append(row)

    return pd.DataFrame(rows)


def build_timeseries(ic_df: pd.DataFrame, ls_df: pd.DataFrame) -> pd.DataFrame:
    """Compact timeseries: per factor/horizon/month, rolling IC and LS."""
    rows = []
    for (fid, hz), ic_grp in ic_df.groupby(["factor_id", "horizon"]):
        ic_grp = ic_grp.sort_values("month").reset_index(drop=True)
        ls_grp = ls_df[(ls_df["factor_id"] == fid) & (ls_df["horizon"] == hz)]
        ls_grp = ls_grp.sort_values("month").reset_index(drop=True)

        ic_vals = ic_grp["rank_ic"].values
        months = ic_grp["month"].values
        ls_map = dict(zip(ls_grp["month"], ls_grp["long_short_return"]))

        for i, m in enumerate(months):
            ic_3m = float(np.mean(ic_vals[max(0, i - 2) : i + 1]))
            ic_6m = float(np.mean(ic_vals[max(0, i - 5) : i + 1]))
            ls_val = ls_map.get(m)
            ls_3m_arr = [
                ls_map.get(months[j])
                for j in range(max(0, i - 2), i + 1)
                if j < len(months) and ls_map.get(months[j]) is not None
            ]
            ls_6m_arr = [
                ls_map.get(months[j])
                for j in range(max(0, i - 5), i + 1)
                if j < len(months) and ls_map.get(months[j]) is not None
            ]
            rows.append(
                {
                    "factor_id": fid,
                    "horizon": hz,
                    "month": m,
                    "rank_ic": round(float(ic_vals[i]), 6),
                    "rolling_ic_3m": round(ic_3m, 6),
                    "rolling_ic_6m": round(ic_6m, 6),
                    "long_short_return": round(float(ls_val), 8) if ls_val is not None else None,
                    "rolling_ls_3m": round(float(np.mean(ls_3m_arr)), 8) if ls_3m_arr else None,
                    "rolling_ls_6m": round(float(np.mean(ls_6m_arr)), 8) if ls_6m_arr else None,
                }
            )
    return pd.DataFrame(rows)


def build_payload(shape_df: pd.DataFrame, stab_df: pd.DataFrame) -> dict:
    """Compact JSON payload for page integration."""
    factors = []
    for fid in sorted(shape_df["factor_id"].unique()):
        s_rows = shape_df[shape_df["factor_id"] == fid]
        st_rows = stab_df[stab_df["factor_id"] == fid]
        horizons = {}
        for hz in sorted(s_rows["horizon"].unique()):
            sr = s_rows[s_rows["horizon"] == hz].iloc[0].to_dict()
            st = st_rows[st_rows["horizon"] == hz].iloc[0].to_dict() if len(st_rows[st_rows["horizon"] == hz]) > 0 else {}
            horizons[hz] = {
                "shape": {
                    "quantile_shape_class": sr.get("quantile_shape_class"),
                    "monotonicity_class": sr.get("monotonicity_class"),
                    "monotonicity_score": sr.get("monotonicity_score"),
                    "q_spread_return": sr.get("q_spread_return"),
                    "q_spearman_corr": sr.get("q_spearman_corr"),
                    "positive_spread_month_rate": sr.get("positive_spread_month_rate"),
                    "note_zh": sr.get("main_shape_note_zh"),
                    "note_en": sr.get("main_shape_note_en"),
                },
                "stability": {
                    "stability_class": st.get("stability_class"),
                    "stability_score": st.get("stability_score"),
                    "ic_positive_month_rate": st.get("ic_positive_month_rate"),
                    "recent_vs_full_ic_delta": st.get("recent_vs_full_ic_delta"),
                    "recent_vs_full_ls_delta": st.get("recent_vs_full_ls_delta"),
                    "note_zh": st.get("main_stability_note_zh"),
                    "note_en": st.get("main_stability_note_en"),
                },
            }
        factors.append({"factor_id": fid, "horizons": horizons})
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "n_factors": len(factors),
        "factors": factors,
    }


def main():
    parser = argparse.ArgumentParser(description="PM-26: Quantile Shape & Rolling Stability Diagnostics")
    parser.add_argument("--min-months", type=int, default=6, help="Minimum months for classification")
    parser.add_argument("--rolling-windows", type=str, default="3,6", help="Comma-separated rolling windows")
    args = parser.parse_args()

    rolling_windows = [int(x) for x in args.rolling_windows.split(",")]
    min_months = args.min_months

    print("Loading data...")
    qr_df = pd.read_csv(QR_FILE)
    ls_period_df = pd.read_csv(LS_PERIOD_FILE)
    ic_df = pd.read_csv(IC_FILE)
    ls_df = pd.read_csv(LS_FILE)
    diag_df = pd.read_csv(DIAG_SUMMARY)

    # Standardize column name: quantile file uses 'factor_name', we need 'factor_id'
    if "factor_name" in qr_df.columns and "factor_id" not in qr_df.columns:
        qr_df = qr_df.rename(columns={"factor_name": "factor_id"})

    print(f"  Quantile data: {len(qr_df)} rows, {qr_df['factor_id'].nunique()} factors")
    print(f"  IC series: {len(ic_df)} rows, {ic_df['factor_id'].nunique()} factors")
    print(f"  LS series: {len(ls_df)} rows, {ls_df['factor_id'].nunique()} factors")

    # Load state
    with open(STATE_FILE) as f:
        state = json.load(f)
    n_registered = state.get("registered_factors", 71)

    # ── Build quantile shape ───────────────────────────────────────────
    print("Building quantile shape diagnostics...")
    shape_df = build_quantile_shape(qr_df, diag_df)
    print(f"  → {len(shape_df)} rows ({shape_df['factor_id'].nunique()} factors × {shape_df['horizon'].nunique()} horizons)")

    # ── Build rolling stability ────────────────────────────────────────
    print("Building rolling stability diagnostics...")
    stab_df = build_rolling_stability(ic_df, ls_df, rolling_windows)
    print(f"  → {len(stab_df)} rows ({stab_df['factor_id'].nunique()} factors × {stab_df['horizon'].nunique()} horizons)")

    # ── Build timeseries ───────────────────────────────────────────────
    print("Building timeseries...")
    ts_df = build_timeseries(ic_df, ls_df)
    print(f"  → {len(ts_df)} rows ({ts_df['factor_id'].nunique()} factors)")

    # ── Build payload ──────────────────────────────────────────────────
    print("Building payload...")
    payload = build_payload(shape_df, stab_df)
    print(f"  → {payload['n_factors']} factors in payload")

    # ── Write outputs ──────────────────────────────────────────────────
    DIAG.mkdir(parents=True, exist_ok=True)

    shape_csv = DIAG / "factor_quantile_shape_summary.csv"
    shape_json = DIAG / "factor_quantile_shape_summary.json"
    stab_csv = DIAG / "factor_rolling_stability_summary.csv"
    stab_json = DIAG / "factor_rolling_stability_summary.json"
    ts_csv = DIAG / "factor_shape_stability_timeseries.csv"
    payload_json = DIAG / "factor_shape_stability_payload.json"
    manifest_json = DIAG / "factor_shape_stability_manifest.json"

    shape_df.to_csv(shape_csv, index=False)
    shape_df.to_json(shape_json, orient="records", indent=2)
    stab_df.to_csv(stab_csv, index=False)
    stab_df.to_json(stab_json, orient="records", indent=2)
    ts_df.to_csv(ts_csv, index=False)
    with open(payload_json, "w") as f:
        json.dump(payload, f, indent=2, default=str)

    # Manifest
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pm_ticket": "PM-26",
        "description": "Quantile shape and rolling stability diagnostics for factor library",
        "n_registered_factors": n_registered,
        "n_shape_factors": int(shape_df["factor_id"].nunique()),
        "n_stability_factors": int(stab_df["factor_id"].nunique()),
        "n_timeseries_rows": len(ts_df),
        "horizons": sorted(shape_df["horizon"].unique().tolist()),
        "rolling_windows": rolling_windows,
        "min_months": min_months,
        "payload_bytes": len(json.dumps(payload, default=str)),
        "outputs": [
            str(shape_csv),
            str(shape_json),
            str(stab_csv),
            str(stab_json),
            str(ts_csv),
            str(payload_json),
            str(manifest_json),
        ],
        "shape_class_distribution": shape_df["quantile_shape_class"].value_counts().to_dict(),
        "stability_class_distribution": stab_df["stability_class"].value_counts().to_dict(),
    }
    with open(manifest_json, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"\n✅ All outputs written to {DIAG}/")
    print(f"   Shape classes: {shape_df['quantile_shape_class'].value_counts().to_dict()}")
    print(f"   Stability classes: {stab_df['stability_class'].value_counts().to_dict()}")


if __name__ == "__main__":
    main()
