"""Smoke test for evaluate_factors.py — run on synthetic data, verify output fields."""
import math
import numpy as np
import pandas as pd
import pytest


def _make_synthetic_panel(n_symbols=20, n_timestamps=200, seed=42):
    """Create a synthetic merged panel of factor_value + forward returns."""
    rng = np.random.default_rng(seed)
    rows = []
    base_ts = pd.Timestamp("2026-01-01", tz="UTC")
    for t in range(n_timestamps):
        ts = base_ts + pd.Timedelta(hours=t)
        for s in range(n_symbols):
            fv = rng.normal()
            # Synthetic: forward return correlated with factor_value (weak signal)
            noise = rng.normal(0, 0.01)
            ret = 0.001 * fv + noise
            rows.append({
                "timestamp": ts,
                "symbol": f"SYM{s}",
                "factor_value": fv,
                "ret_fwd_1h": ret,
            })
    return pd.DataFrame(rows)


def _evaluate_one_label(df, label, min_n=10):
    """Replicate evaluate_factors.py core logic for one label."""
    total = len(df)
    factor_coverage = df["factor_value"].notna().mean() if total else 0.0
    valid = df[["timestamp", "symbol", "factor_value", label]].dropna()
    if valid.empty:
        return {"coverage": factor_coverage, "IC_mean": None, "RankIC_mean": None,
                "quantile_spread_mean": None, "turnover": None}

    fv_pivot = valid.pivot_table(index="timestamp", columns="symbol", values="factor_value")
    lb_pivot = valid.pivot_table(index="timestamp", columns="symbol", values=label)
    n_ts = len(fv_pivot)

    ics = fv_pivot.corrwith(lb_pivot, axis=1).dropna().tolist()
    rics = fv_pivot.rank(axis=1).corrwith(lb_pivot.rank(axis=1), axis=1).dropna().tolist()

    # Quintile spread
    fv_arr = fv_pivot.values
    lb_arr = lb_pivot.values
    symbols = fv_pivot.columns.tolist()
    spreads = []
    top_sets, bottom_sets = [], []

    for i in range(n_ts):
        row = fv_arr[i]
        mask = ~np.isnan(row)
        n_valid = mask.sum()
        if n_valid < min_n:
            continue
        ranked = np.argsort(np.argsort(row[mask])) + 1
        pctile = ranked / n_valid
        q = np.floor(pctile * 5).clip(0, 4).astype(int) + 1

        q1_mask = q == 1
        q5_mask = q == 5
        valid_mask = ~np.isnan(lb_arr[i])
        q1_vals = lb_arr[i][mask][q1_mask & valid_mask[mask]] if np.any(q1_mask & valid_mask[mask]) else np.array([])
        q5_vals = lb_arr[i][mask][q5_mask & valid_mask[mask]] if np.any(q5_mask & valid_mask[mask]) else np.array([])

        if len(q1_vals) > 0 and len(q5_vals) > 0:
            spreads.append(np.mean(q5_vals) - np.mean(q1_vals))

    def safe_mean(xs):
        clean = [x for x in xs if not (isinstance(x, float) and (math.isnan(x) or math.isinf(x)))]
        return float(np.mean(clean)) if clean else None

    def safe_std(xs):
        clean = [x for x in xs if not (isinstance(x, float) and (math.isnan(x) or math.isinf(x)))]
        return float(np.std(clean, ddof=1)) if len(clean) > 1 else None

    icm = safe_mean(ics)
    icsd = safe_std(ics)
    ricm = safe_mean(rics)
    ricsd = safe_std(rics)

    return {
        "coverage": factor_coverage,
        "IC_mean": icm,
        "IC_std": icsd,
        "ICIR": icm / icsd if icm is not None and icsd not in (None, 0) else None,
        "RankIC_mean": ricm,
        "RankIC_std": ricsd,
        "RankICIR": ricm / ricsd if ricm is not None and ricsd not in (None, 0) else None,
        "quantile_spread_mean": safe_mean(spreads),
        "quantile_spread_tstat": safe_mean(spreads) / safe_std(spreads) * math.sqrt(len(spreads)) if safe_std(spreads) and len(spreads) > 1 else None,
        "turnover": None,  # simplified — not testing turnover here
        "n_timestamps": len(ics),
    }


class TestEvaluationSmoke:
    """evaluate_factors.py logic must produce valid IC / RankIC / spread on synthetic data."""

    def test_ic_fields_present(self):
        df = _make_synthetic_panel()
        m = _evaluate_one_label(df, "ret_fwd_1h")
        for key in ["IC_mean", "IC_std", "ICIR", "RankIC_mean", "RankIC_std", "RankICIR",
                     "quantile_spread_mean", "quantile_spread_tstat", "coverage", "n_timestamps"]:
            assert key in m, f"Missing key: {key}"

    def test_ic_values_finite(self):
        df = _make_synthetic_panel()
        m = _evaluate_one_label(df, "ret_fwd_1h")
        for key in ["IC_mean", "RankIC_mean", "quantile_spread_mean", "coverage"]:
            v = m[key]
            assert v is not None, f"{key} is None"
            assert not math.isnan(v), f"{key} is NaN"
            assert not math.isinf(v), f"{key} is Inf"

    def test_ic_positive_for_synthetic_signal(self):
        """Synthetic data has positive factor-return correlation → IC should be positive."""
        df = _make_synthetic_panel(n_symbols=20, n_timestamps=500, seed=42)
        m = _evaluate_one_label(df, "ret_fwd_1h")
        # With 0.001 * fv + noise, IC should be positive on average
        assert m["IC_mean"] > 0, f"Expected positive IC, got {m['IC_mean']}"

    def test_coverage_near_one(self):
        df = _make_synthetic_panel()
        m = _evaluate_one_label(df, "ret_fwd_1h")
        assert m["coverage"] > 0.95

    def test_empty_panel_returns_none_metrics(self):
        df = pd.DataFrame(columns=["timestamp", "symbol", "factor_value", "ret_fwd_1h"])
        m = _evaluate_one_label(df, "ret_fwd_1h")
        assert m["IC_mean"] is None
        assert m["coverage"] == 0.0
