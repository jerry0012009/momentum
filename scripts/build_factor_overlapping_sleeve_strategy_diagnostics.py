#!/usr/bin/env python3
"""PM-59A: Overlapping Sleeve Strategy Diagnostics.

Computes per-factor hourly strategy return series using overlapping sleeves.
Each factor's derived strategy direction and horizon determine ranking and holding.
At every hour, a new sleeve is formed (long top quantile, short bottom quantile),
and the sleeve contributes realized 1h returns for h hours.

NOT a backtest. NOT a trading strategy. Research diagnostics only.

Usage:
    python scripts/build_factor_overlapping_sleeve_strategy_diagnostics.py --dry-run
    python scripts/build_factor_overlapping_sleeve_strategy_diagnostics.py --max-factors 2 --overwrite
    python scripts/build_factor_overlapping_sleeve_strategy_diagnostics.py --only-missing
    python scripts/build_factor_overlapping_sleeve_strategy_diagnostics.py --factor-ids mom_20h,reversal_5h
"""

from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

# ── Constants ────────────────────────────────────────────────────────────────
WORKSPACE = Path(__file__).resolve().parent.parent
DATASET_ID = "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1"
FEATURES_DIR = WORKSPACE / "data" / "features" / DATASET_ID
BARS_PATH = WORKSPACE / "data" / "cache" / DATASET_ID / "bars_1h.parquet"
UNIVERSE_PATH = (
    WORKSPACE
    / "data"
    / "universe"
    / "crypto_usdt_perp_monthly_volume_top50_current_listed_v1"
    / "universe_snapshots.parquet"
)
STATE_PATH = (
    WORKSPACE
    / "research"
    / "factor_runs"
    / "crypto_top50_factor_library"
    / "factor_library_state.json"
)
COVERAGE_PATH = (
    WORKSPACE
    / "research"
    / "factor_runs"
    / "crypto_top50_factor_library"
    / "factor_level_evaluation"
    / "factor_level_coverage_summary.csv"
)
DIAG_SUMMARY_PATH = (
    WORKSPACE
    / "research"
    / "factor_runs"
    / "crypto_top50_factor_library"
    / "factor_diagnostics"
    / "factor_diagnostics_summary.csv"
)
RANKIC_SUMMARY_PATH = (
    WORKSPACE
    / "research"
    / "factor_runs"
    / "crypto_top50_factor_library"
    / "factor_level_evaluation"
    / "factor_level_rankic_summary.csv"
)
LS_SUMMARY_PATH = (
    WORKSPACE
    / "research"
    / "factor_runs"
    / "crypto_top50_factor_library"
    / "factor_level_evaluation"
    / "factor_level_long_short_summary.csv"
)
DIAG_DIR = (
    WORKSPACE
    / "research"
    / "factor_runs"
    / "crypto_top50_factor_library"
    / "factor_diagnostics"
)
RETURNS_DIR = DIAG_DIR / "overlapping_sleeve_strategy_returns"
SUMMARY_CSV = DIAG_DIR / "factor_overlapping_sleeve_strategy_summary.csv"
SUMMARY_JSON = DIAG_DIR / "factor_overlapping_sleeve_strategy_summary.json"
MANIFEST_JSON = DIAG_DIR / "factor_overlapping_sleeve_strategy_manifest.json"

LONG_QUANTILE = 0.80
SHORT_QUANTILE = 0.20
MIN_SYMBOLS_PER_TS = 10
HORIZON_MAP = {"1h": 1, "4h": 4, "24h": 24, "72h": 72}
VALID_HORIZONS = list(HORIZON_MAP.keys())


# ── Helpers ──────────────────────────────────────────────────────────────────

def _r4(x: float) -> float | None:
    return round(float(x), 4) if x is not None and np.isfinite(x) else None


def _safe_float(x) -> float | None:
    if x is None:
        return None
    try:
        v = float(x)
        return v if np.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def _sanitize_for_json(obj):
    """Recursively replace NaN/inf with None for JSON serialization."""
    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize_for_json(v) for v in obj]
    if isinstance(obj, float):
        return _safe_float(obj)
    return obj


# ── Data Loading ─────────────────────────────────────────────────────────────

def load_direction_map() -> dict[str, str]:
    """Load expected_direction for every registered factor from registry."""
    scripts_dir = Path(__file__).resolve().parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from factor_formula_registry import REGISTRY
    return {spec.factor_id: spec.expected_direction for spec in REGISTRY}


def load_rankic_data() -> pd.DataFrame:
    """Load RankIC summary for empirical direction derivation."""
    if RANKIC_SUMMARY_PATH.exists():
        return pd.read_csv(RANKIC_SUMMARY_PATH)
    return pd.DataFrame()


def load_ls_data() -> pd.DataFrame:
    """Load LS summary for empirical direction/horizon derivation."""
    if LS_SUMMARY_PATH.exists():
        return pd.read_csv(LS_SUMMARY_PATH)
    return pd.DataFrame()


def load_coverage_data() -> pd.DataFrame:
    """Load coverage summary."""
    if COVERAGE_PATH.exists():
        return pd.read_csv(COVERAGE_PATH)
    return pd.DataFrame()


def load_diag_data() -> pd.DataFrame:
    """Load diagnostics summary."""
    if DIAG_SUMMARY_PATH.exists():
        return pd.read_csv(DIAG_SUMMARY_PATH)
    return pd.DataFrame()


# ── Direction Derivation ─────────────────────────────────────────────────────

def derive_strategy_direction(
    factor_id: str,
    registry_direction: str,
    horizon: str,
    rankic_df: pd.DataFrame,
    ls_df: pd.DataFrame,
) -> dict:
    """Derive PM-59A strategy direction for a factor.

    For positive/negative registry directions, use directly.
    For conditional, derive from empirical evidence (RankIC or LS).
    """
    result = {
        "registry_expected_direction": registry_direction,
        "strategy_direction": None,
        "direction_source": None,
        "direction_confidence": None,
        "direction_warning": None,
    }

    if registry_direction == "positive":
        result["strategy_direction"] = "positive"
        result["direction_source"] = "registry_expected_direction"
        result["direction_confidence"] = "high"
        return result

    if registry_direction == "negative":
        result["strategy_direction"] = "negative"
        result["direction_source"] = "registry_expected_direction"
        result["direction_confidence"] = "high"
        return result

    # ── conditional: derive from empirical evidence ──────────────────────
    # Try RankIC first at the selected horizon
    raw_ic = None
    if len(rankic_df) > 0:
        mask = (rankic_df["factor_name"] == factor_id) & (rankic_df["horizon"] == horizon)
        rows = rankic_df[mask]
        if len(rows) > 0:
            raw_ic = rows.iloc[0].get("raw_mean_rank_ic")
            if pd.isna(raw_ic):
                raw_ic = rows.iloc[0].get("direction_adjusted_mean_rank_ic")

    if raw_ic is not None and not pd.isna(raw_ic):
        result["strategy_direction"] = "positive" if raw_ic > 0 else "negative"
        result["direction_source"] = "empirical_rankic_at_selected_horizon"
        result["direction_confidence"] = "high" if abs(raw_ic) >= 0.005 else "low"
        if abs(raw_ic) < 0.005:
            result["direction_warning"] = "weak_empirical_direction; abs(raw_ic) < 0.005; "
        result["direction_warning"] = (result["direction_warning"] or "") + (
            "This does not modify registry expected_direction. "
            "This is PM-59A diagnostic-only direction. "
        )
        return result

    # Try LS spread at the selected horizon
    ls_spread = None
    if len(ls_df) > 0:
        mask = (ls_df["factor_name"] == factor_id) & (ls_df["horizon"] == horizon)
        rows = ls_df[mask]
        if len(rows) > 0:
            ls_spread = rows.iloc[0].get("long_short_spread_mean")

    if ls_spread is not None and not pd.isna(ls_spread):
        result["strategy_direction"] = "positive" if ls_spread > 0 else "negative"
        result["direction_source"] = "empirical_ls_at_selected_horizon"
        result["direction_confidence"] = "medium" if abs(ls_spread) > 0.0001 else "low"
        if abs(ls_spread) <= 0.0001:
            result["direction_warning"] = "weak_empirical_direction; abs(ls_spread) <= 0.0001; "
        result["direction_warning"] = (result["direction_warning"] or "") + (
            "This does not modify registry expected_direction. "
            "This is PM-59A diagnostic-only direction. "
        )
        return result

    # Both missing or zero: default to positive
    result["strategy_direction"] = "positive"
    result["direction_source"] = "default_positive_for_diagnostic_coverage"
    result["direction_confidence"] = "low"
    result["direction_warning"] = (
        "conditional direction had insufficient evidence; "
        "default positive used for diagnostic coverage only; "
        "This does not modify registry expected_direction. "
    )
    return result


# ── Horizon Derivation ───────────────────────────────────────────────────────

def derive_strategy_horizon(
    factor_id: str,
    coverage_df: pd.DataFrame,
    diagnostics_df: pd.DataFrame,
    rankic_df: pd.DataFrame,
    ls_df: pd.DataFrame,
) -> dict:
    """Derive PM-59A strategy horizon for a factor.

    Priority: coverage > diagnostics > rankic abs max > ls abs max > default 72h
    """
    result = {
        "horizon": None,
        "holding_hours": None,
        "best_horizon_source": None,
        "horizon_confidence": None,
        "horizon_warning": None,
    }

    # 1. Coverage summary best_adj_ic_horizon
    if len(coverage_df) > 0:
        row = coverage_df[coverage_df["factor_name"] == factor_id]
        if len(row) > 0:
            hz = row.iloc[0].get("best_adj_ic_horizon")
            if pd.notna(hz) and str(hz) in HORIZON_MAP:
                result["horizon"] = str(hz)
                result["holding_hours"] = HORIZON_MAP[str(hz)]
                result["best_horizon_source"] = "coverage_best_adj_ic_horizon"
                result["horizon_confidence"] = "high"
                return result

    # 2. Diagnostics summary best_horizon
    if len(diagnostics_df) > 0:
        row = diagnostics_df[diagnostics_df["factor_id"] == factor_id]
        if len(row) > 0:
            hz = row.iloc[0].get("best_horizon")
            if pd.notna(hz) and str(hz) in HORIZON_MAP:
                result["horizon"] = str(hz)
                result["holding_hours"] = HORIZON_MAP[str(hz)]
                result["best_horizon_source"] = "diagnostics_summary_best_horizon"
                result["horizon_confidence"] = "high"
                return result

    # 3. Derive from RankIC: pick horizon with max abs(raw_mean_rank_ic)
    if len(rankic_df) > 0:
        rows = rankic_df[rankic_df["factor_name"] == factor_id]
        if len(rows) > 0:
            ic_col = "raw_mean_rank_ic"
            if ic_col not in rows.columns:
                ic_col = "direction_adjusted_mean_rank_ic"
            if ic_col in rows.columns:
                valid = rows[rows[ic_col].notna()].copy()
                if len(valid) > 0:
                    valid["abs_ic"] = valid[ic_col].abs()
                    best_row = valid.loc[valid["abs_ic"].idxmax()]
                    hz = str(best_row.get("horizon", ""))
                    if hz in HORIZON_MAP:
                        result["horizon"] = hz
                        result["holding_hours"] = HORIZON_MAP[hz]
                        result["best_horizon_source"] = "derived_from_abs_rankic"
                        result["horizon_confidence"] = "medium"
                        result["horizon_warning"] = "horizon derived from max abs RankIC; not canonical; "
                        return result

    # 4. Derive from LS: pick horizon with max abs(long_short_spread_mean)
    if len(ls_df) > 0:
        rows = ls_df[ls_df["factor_name"] == factor_id]
        if len(rows) > 0:
            valid = rows[rows["long_short_spread_mean"].notna()].copy()
            if len(valid) > 0:
                valid["abs_spread"] = valid["long_short_spread_mean"].abs()
                best_row = valid.loc[valid["abs_spread"].idxmax()]
                hz = str(best_row.get("horizon", ""))
                if hz in HORIZON_MAP:
                    result["horizon"] = hz
                    result["holding_hours"] = HORIZON_MAP[hz]
                    result["best_horizon_source"] = "derived_from_abs_ls_spread"
                    result["horizon_confidence"] = "medium"
                    result["horizon_warning"] = "horizon derived from max abs LS spread; not canonical; "
                    return result

    # 5. Default 72h
    result["horizon"] = "72h"
    result["holding_hours"] = 72
    result["best_horizon_source"] = "default_72h_for_diagnostic_coverage"
    result["horizon_confidence"] = "low"
    result["horizon_warning"] = (
        "missing best_horizon; default 72h used for PM-59A diagnostic coverage only; "
    )
    return result


# ── Factor Discovery ─────────────────────────────────────────────────────────

def discover_target_factors(
    direction_map: dict[str, str],
    rankic_df: pd.DataFrame,
    ls_df: pd.DataFrame,
    coverage_df: pd.DataFrame,
    diagnostics_df: pd.DataFrame,
) -> tuple[list[dict], list[tuple[str, str]]]:
    """Discover all target factors from computed_factor_ids.

    Only skip if factor_values.parquet doesn't exist or is empty.
    Conditional direction and missing best_horizon are derived, not skipped.
    """
    state = json.loads(STATE_PATH.read_text())
    computed_ids = set(state.get("computed_factor_ids", []))

    targets = []
    skipped = []

    for fid in sorted(computed_ids):
        fv_path = FEATURES_DIR / fid / "factor_values.parquet"
        if not fv_path.exists():
            skipped.append((fid, "MISSING_FACTOR_VALUES"))
            continue

        # Get registry direction
        registry_dir = direction_map.get(fid)
        if registry_dir is None:
            skipped.append((fid, "MISSING_DIRECTION"))
            continue

        # Derive strategy direction
        dir_info = derive_strategy_direction(
            fid, registry_dir, "72h", rankic_df, ls_df
        )

        # Derive strategy horizon (we need horizon first to finalize direction)
        hz_info = derive_strategy_horizon(
            fid, coverage_df, diagnostics_df, rankic_df, ls_df
        )

        # Re-derive direction at the actual horizon (not placeholder 72h)
        dir_info = derive_strategy_direction(
            fid, registry_dir, hz_info["horizon"], rankic_df, ls_df
        )

        targets.append({
            "factor_id": fid,
            "registry_expected_direction": registry_dir,
            "strategy_direction": dir_info["strategy_direction"],
            "direction_source": dir_info["direction_source"],
            "direction_confidence": dir_info["direction_confidence"],
            "direction_warning": dir_info.get("direction_warning"),
            "best_horizon": hz_info["horizon"],
            "holding_hours": hz_info["holding_hours"],
            "best_horizon_source": hz_info["best_horizon_source"],
            "horizon_confidence": hz_info["horizon_confidence"],
            "horizon_warning": hz_info.get("horizon_warning"),
            "factor_values_path": str(fv_path),
        })

    return targets, skipped


def get_existing_complete_outputs() -> set[tuple[str, str]]:
    """Scan existing outputs, return set of (factor_id, horizon) that are complete."""
    complete = set()
    if not SUMMARY_CSV.exists():
        return complete
    try:
        df = pd.read_csv(SUMMARY_CSV)
        for _, row in df.iterrows():
            fid = row.get("factor_id")
            hz = row.get("horizon")
            status = row.get("status")
            n_hours = row.get("n_return_hours", 0)
            out_path = row.get("output_path", "")

            if not (fid and hz):
                continue

            # Check completeness
            is_complete = (
                status in ("OK", "OK_WITH_WARNING")
                and isinstance(out_path, str) and len(out_path) > 0
                and Path(out_path).exists()
                and pd.notna(n_hours) and n_hours > 0
            )
            if is_complete:
                # Verify parquet has data
                try:
                    pf = pd.read_parquet(out_path)
                    if len(pf) > 0:
                        complete.add((str(fid), str(hz)))
                except Exception:
                    pass
    except Exception:
        pass
    return complete


# ── Core Computation ─────────────────────────────────────────────────────────

def compute_sleeve_strategy_returns(
    factor_id: str,
    strategy_direction: str,
    holding_hours: int,
    factor_values_path: str,
    returns_panel: pd.DataFrame,
    universe_set: pd.DataFrame,
    dir_info: dict,
    hz_info: dict,
    overwrite: bool = False,
) -> dict:
    """Compute overlapping sleeve strategy returns for one factor."""
    t0 = time.time()
    result = {
        "factor_id": factor_id,
        "horizon": f"{holding_hours}h",
        "holding_hours": holding_hours,
        "status": "OK",
        "skip_reason": None,
        "warning": None,
    }

    # Direction fields
    result["registry_expected_direction"] = dir_info["registry_expected_direction"]
    result["strategy_direction"] = strategy_direction
    result["direction_source"] = dir_info["direction_source"]
    result["direction_confidence"] = dir_info["direction_confidence"]
    result["direction_warning"] = dir_info.get("direction_warning")

    # Legacy field for backward compat
    result["expected_direction"] = strategy_direction
    result["direction_handling"] = (
        "positive_aligned" if strategy_direction == "positive"
        else "negative_flipped"
    )

    # Horizon fields
    result["horizon_source"] = hz_info["best_horizon_source"]
    result["horizon_confidence"] = hz_info["horizon_confidence"]
    result["horizon_warning"] = hz_info.get("horizon_warning")

    # Coverage mode
    is_conditional = dir_info["registry_expected_direction"] == "conditional"
    is_default_hz = hz_info["best_horizon_source"] in (
        "default_72h_for_diagnostic_coverage", "derived_from_abs_rankic",
        "derived_from_abs_ls_spread"
    )
    coverage_parts = []
    if is_conditional:
        coverage_parts.append("empirical_direction")
    if is_default_hz:
        coverage_parts.append("derived_horizon")
    result["coverage_mode"] = "standard" if not coverage_parts else "+".join(coverage_parts)

    # Conventions
    result["strategy_return_convention"] = "long_mean_minus_short_mean_spread"
    result["return_timestamp_convention"] = (
        "realized_1h_return[return_start_ts, symbol] = close[return_start_ts+1h] / close[return_start_ts] - 1"
    )
    result["eligible_source"] = "factor_library_state.json (computed_factor_ids)"
    result["best_horizon_source"] = hz_info["best_horizon_source"]
    result["universe_source"] = "universe_snapshots.parquet (monthly volume top50)"
    result["quantile_method"] = "cross-sectional_rank_pct"
    result["long_quantile"] = LONG_QUANTILE
    result["short_quantile"] = SHORT_QUANTILE
    result["memory_mode"] = "factor_by_factor_streaming"

    # Output path
    out_name = f"{factor_id}__{holding_hours}h.parquet"
    out_path = RETURNS_DIR / out_name
    result["output_path"] = str(out_path)

    # Check if already complete
    if not overwrite and out_path.exists():
        try:
            existing = pd.read_parquet(out_path)
            if len(existing) > 0:
                result["status"] = "SKIPPED_ALREADY_EXISTS"
                result["skip_reason"] = "output already exists and --overwrite not set"
                result["runtime_seconds"] = round(time.time() - t0, 2)
                return result
        except Exception:
            pass

    # Load factor values
    fv = pd.read_parquet(factor_values_path, columns=["timestamp", "symbol", "factor_value"])
    result["n_input_rows"] = len(fv)

    fv = fv.dropna(subset=["factor_value"])
    if len(fv) == 0:
        result["status"] = "EMPTY_FACTOR_VALUES"
        result["skip_reason"] = "all factor_values are NaN"
        result["runtime_seconds"] = round(time.time() - t0, 2)
        return result

    # Parse timestamps
    fv["timestamp"] = pd.to_datetime(fv["timestamp"], utc=True)
    fv["universe_month"] = fv["timestamp"].dt.to_period("M")

    # Join with universe to filter eligible symbols
    fv = fv.merge(universe_set, on=["universe_month", "symbol"], how="inner")
    fv = fv.drop(columns=["universe_month"])

    if len(fv) == 0:
        result["status"] = "NO_UNIVERSE_MATCH"
        result["skip_reason"] = "no factor_values match universe eligibility"
        result["runtime_seconds"] = round(time.time() - t0, 2)
        return result

    # Direction-adjusted ranking
    if strategy_direction == "negative":
        fv["factor_value"] = -fv["factor_value"]

    # Cross-sectional rank per timestamp
    fv["rank_pct"] = fv.groupby("timestamp")["factor_value"].rank(pct=True, method="first")

    # Assign baskets
    fv["basket"] = np.where(
        fv["rank_pct"] >= LONG_QUANTILE, "long",
        np.where(fv["rank_pct"] <= SHORT_QUANTILE, "short", None)
    )

    signals = fv[fv["basket"].notna()][["timestamp", "symbol", "basket"]].copy()
    signals = signals.rename(columns={"timestamp": "entry_ts"})

    n_signal_timestamps = signals["entry_ts"].nunique()
    result["n_signal_timestamps"] = int(n_signal_timestamps)

    if len(signals) == 0:
        result["status"] = "NO_SIGNALS"
        result["skip_reason"] = "no symbols passed quantile thresholds"
        result["runtime_seconds"] = round(time.time() - t0, 2)
        return result

    # Check minimum symbols per timestamp
    ts_counts = signals.groupby("entry_ts").size()
    if ts_counts.min() < 2:
        result["warning"] = (result["warning"] or "") + f"min_symbols_per_ts={ts_counts.min()}; "

    # Expand sleeves: each signal generates h rows (holding_offsets 1..h)
    n_signals = len(signals)
    h = holding_hours

    offsets = np.arange(1, h + 1)

    entry_ts_repeated = np.repeat(signals["entry_ts"].values, h)
    symbol_repeated = np.repeat(signals["symbol"].values, h)
    basket_repeated = np.repeat(signals["basket"].values, h)
    offset_tiled = np.tile(offsets, n_signals)

    # return_start_ts = entry_ts + (offset - 1) hours
    return_start_ts = entry_ts_repeated + pd.to_timedelta(offset_tiled - 1, unit="h")

    expanded = pd.DataFrame({
        "entry_ts": entry_ts_repeated,
        "return_start_ts": return_start_ts,
        "symbol": symbol_repeated,
        "basket": basket_repeated,
        "holding_offset": offset_tiled,
    })

    # Ensure consistent timezone
    if expanded["return_start_ts"].dt.tz is not None and returns_panel["return_start_ts"].dt.tz is None:
        returns_panel = returns_panel.copy()
        returns_panel["return_start_ts"] = returns_panel["return_start_ts"].dt.tz_localize("UTC")
    elif expanded["return_start_ts"].dt.tz is None and returns_panel["return_start_ts"].dt.tz is not None:
        expanded["return_start_ts"] = expanded["return_start_ts"].dt.tz_localize("UTC")

    expanded = expanded.merge(
        returns_panel,
        on=["return_start_ts", "symbol"],
        how="left",
    )

    n_missing_returns = expanded["realized_1h_return"].isna().sum()
    n_total = len(expanded)
    missing_rate = n_missing_returns / n_total if n_total > 0 else 0.0

    expanded["realized_1h_return"] = expanded["realized_1h_return"].fillna(0.0)

    # Compute sleeve-level hourly return: mean(long) - mean(short)
    sleeve_groups = expanded.groupby(["entry_ts", "return_start_ts", "basket"])["realized_1h_return"].mean()
    sleeve_groups = sleeve_groups.unstack("basket")

    if "long" in sleeve_groups.columns and "short" in sleeve_groups.columns:
        sleeve_groups["sleeve_hourly_return"] = (
            sleeve_groups["long"].fillna(0) - sleeve_groups["short"].fillna(0)
        )
    elif "long" in sleeve_groups.columns:
        sleeve_groups["sleeve_hourly_return"] = sleeve_groups["long"].fillna(0)
        result["warning"] = (result["warning"] or "") + "no_short_leg; "
    elif "short" in sleeve_groups.columns:
        sleeve_groups["sleeve_hourly_return"] = -sleeve_groups["short"].fillna(0)
        result["warning"] = (result["warning"] or "") + "no_long_leg; "
    else:
        result["status"] = "NO_BASKET_RETURNS"
        result["skip_reason"] = "neither long nor short basket has returns"
        result["runtime_seconds"] = round(time.time() - t0, 2)
        return result

    sleeve_returns = sleeve_groups[["sleeve_hourly_return"]].reset_index()

    # Aggregate: for each return_start_ts, average all active sleeves
    strategy = sleeve_returns.groupby("return_start_ts").agg(
        strategy_hourly_return=("sleeve_hourly_return", "mean"),
        active_sleeve_count=("sleeve_hourly_return", "count"),
    ).reset_index()

    strategy = strategy.sort_values("return_start_ts").reset_index(drop=True)

    result["n_return_hours"] = len(strategy)
    result["first_return_ts"] = str(strategy["return_start_ts"].iloc[0]) if len(strategy) > 0 else None
    result["last_return_ts"] = str(strategy["return_start_ts"].iloc[-1]) if len(strategy) > 0 else None

    # Compute metrics
    hourly_rets = strategy["strategy_hourly_return"].values
    active_counts = strategy["active_sleeve_count"].values

    if len(hourly_rets) == 0:
        result["status"] = "EMPTY_STRATEGY_RETURNS"
        result["skip_reason"] = "no strategy returns computed"
        result["runtime_seconds"] = round(time.time() - t0, 2)
        return result

    gross_total = np.prod(1 + hourly_rets) - 1
    result["gross_total_return"] = _r4(gross_total)

    mean_hourly = np.mean(hourly_rets)
    result["gross_annualized_return"] = _r4(mean_hourly * 8760)

    std_hourly = np.std(hourly_rets, ddof=1) if len(hourly_rets) > 1 else 0.0
    result["gross_annualized_vol"] = _r4(std_hourly * np.sqrt(8760))

    if std_hourly > 0:
        result["gross_sharpe"] = _r4(mean_hourly / std_hourly * np.sqrt(8760))
    else:
        result["gross_sharpe"] = None

    cum_returns = np.cumprod(1 + hourly_rets)
    running_max = np.maximum.accumulate(cum_returns)
    drawdowns = cum_returns / running_max - 1
    max_dd = np.min(drawdowns)
    result["max_drawdown"] = _r4(max_dd)

    valid_rets = hourly_rets[np.isfinite(hourly_rets)]
    if len(valid_rets) > 0:
        result["hourly_win_rate"] = _r4(np.sum(valid_rets > 0) / len(valid_rets))
    else:
        result["hourly_win_rate"] = None

    result["mean_hourly_return"] = _r4(mean_hourly)
    result["std_hourly_return"] = _r4(std_hourly)

    result["active_sleeve_count_mean"] = _r4(float(np.mean(active_counts)))
    result["active_sleeve_count_median"] = _r4(float(np.median(active_counts)))
    result["active_sleeve_count_min"] = int(np.min(active_counts))
    result["active_sleeve_count_max"] = int(np.max(active_counts))

    result["missing_return_hour_rate"] = _r4(missing_rate)

    # Warnings
    if holding_hours > 1:
        warmup = strategy.head(holding_hours)
        warmup_max = warmup["active_sleeve_count"].max() if len(warmup) > 0 else 0
        if warmup_max < holding_hours:
            result["warning"] = (result["warning"] or "") + (
                f"warmup_period: first {holding_hours} hours have "
                f"active_sleeve_count_max={warmup_max} < {holding_hours}; "
            )

    if len(strategy) < 8760:
        result["warning"] = (result["warning"] or "") + (
            f"sample_less_than_1_year: {len(strategy)} hours < 8760; "
            f"arithmetic_annualization_may_exaggerate; "
        )

    if result.get("direction_warning"):
        result["warning"] = (result["warning"] or "") + result["direction_warning"]
    if result.get("horizon_warning"):
        result["warning"] = (result["warning"] or "") + result["horizon_warning"]

    # Upgrade status if warnings present
    if result.get("warning"):
        result["status"] = "OK_WITH_WARNING"

    # Write per-factor parquet
    out_df = pd.DataFrame({
        "timestamp": strategy["return_start_ts"],
        "strategy_hourly_return": strategy["strategy_hourly_return"],
        "active_sleeve_count": strategy["active_sleeve_count"],
        "cumulative_gross_return": cum_returns,
        "drawdown": drawdowns,
    })
    RETURNS_DIR.mkdir(parents=True, exist_ok=True)
    out_df.to_parquet(out_path, index=False)

    result["runtime_seconds"] = round(time.time() - t0, 2)
    return result


# ── Summary Merge ────────────────────────────────────────────────────────────

def merge_summary(new_rows: list[dict]) -> pd.DataFrame:
    """Merge new rows into existing summary, preserving non-target rows."""
    new_df = pd.DataFrame(new_rows)
    target_keys = set(zip(new_df["factor_id"], new_df["horizon"]))

    if SUMMARY_CSV.exists():
        try:
            old = pd.read_csv(SUMMARY_CSV)
            mask = ~old.apply(lambda r: (r["factor_id"], r["horizon"]) in target_keys, axis=1)
            old = old[mask]
            merged = pd.concat([old, new_df], ignore_index=True)
        except Exception:
            merged = new_df
    else:
        merged = new_df

    return merged


def write_summary_and_manifest(
    summary_df: pd.DataFrame,
    manifest: dict,
) -> None:
    """Write summary CSV/JSON and manifest JSON."""
    DIAG_DIR.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(SUMMARY_CSV, index=False)

    summary_records = summary_df.replace({np.nan: None, np.inf: None, -np.inf: None})
    summary_json = summary_records.to_dict(orient="records")
    SUMMARY_JSON.write_text(json.dumps(summary_json, indent=2, default=str, ensure_ascii=False))

    MANIFEST_JSON.write_text(json.dumps(_sanitize_for_json(manifest), indent=2, default=str, ensure_ascii=False))


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="PM-59A: Overlapping Sleeve Strategy Diagnostics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--factor-ids", type=str, default=None,
                        help="Comma-separated factor IDs to process (subset mode).")
    parser.add_argument("--only-missing", action="store_true", default=False,
                        help="Only process factors with missing/incomplete outputs.")
    parser.add_argument("--max-factors", type=int, default=None,
                        help="Maximum number of factors to process (debug/testing).")
    parser.add_argument("--dry-run", action="store_true", default=False,
                        help="Print plan without executing.")
    parser.add_argument("--overwrite", action="store_true", default=False,
                        help="Overwrite existing per-factor outputs.")
    args = parser.parse_args()

    t_start = time.time()
    print("=" * 70)
    print("PM-59A: Overlapping Sleeve Strategy Diagnostics")
    print("=" * 70)

    # ── Load metadata ────────────────────────────────────────────────────
    print("\n[1/5] Loading metadata...")
    direction_map = load_direction_map()
    rankic_df = load_rankic_data()
    ls_df = load_ls_data()
    coverage_df = load_coverage_data()
    diagnostics_df = load_diag_data()
    print(f"  direction_map: {len(direction_map)} factors")
    print(f"  rankic_df: {len(rankic_df)} rows")
    print(f"  ls_df: {len(ls_df)} rows")
    print(f"  coverage_df: {len(coverage_df)} rows")
    print(f"  diagnostics_df: {len(diagnostics_df)} rows")

    # ── Discover target factors ──────────────────────────────────────────
    print("\n[2/5] Discovering target factors...")
    all_targets, all_skipped = discover_target_factors(
        direction_map, rankic_df, ls_df, coverage_df, diagnostics_df
    )

    state = json.loads(STATE_PATH.read_text())
    n_registered = len(state.get("registered_factor_ids", []))
    n_computed = len(state.get("computed_factor_ids", []))

    print(f"  Registered: {n_registered}")
    print(f"  Computed: {n_computed}")
    print(f"  Target factors: {len(all_targets)}")
    print(f"  Skipped: {len(all_skipped)}")

    # Count empirical/default directions
    n_empirical_dir = sum(
        1 for t in all_targets
        if t["direction_source"] in ("empirical_rankic_at_selected_horizon", "empirical_ls_at_selected_horizon")
    )
    n_default_dir = sum(
        1 for t in all_targets
        if t["direction_source"] == "default_positive_for_diagnostic_coverage"
    )
    n_derived_hz = sum(
        1 for t in all_targets
        if t["best_horizon_source"] in ("derived_from_abs_rankic", "derived_from_abs_ls_spread")
    )
    n_default_hz = sum(
        1 for t in all_targets
        if t["best_horizon_source"] == "default_72h_for_diagnostic_coverage"
    )

    if n_empirical_dir > 0:
        print(f"  Empirical direction: {n_empirical_dir} factors")
    if n_default_dir > 0:
        print(f"  Default direction: {n_default_dir} factors")
    if n_derived_hz > 0:
        print(f"  Derived horizon: {n_derived_hz} factors")
    if n_default_hz > 0:
        print(f"  Default horizon (72h): {n_default_hz} factors")

    if all_skipped:
        print("\n  Skipped factors:")
        skip_reasons = {}
        for fid, reason in all_skipped:
            skip_reasons[reason] = skip_reasons.get(reason, 0) + 1
            print(f"    {fid}: {reason}")
        print(f"\n  Skip reason distribution:")
        for reason, count in sorted(skip_reasons.items()):
            print(f"    {reason}: {count}")

    # ── Apply filters ────────────────────────────────────────────────────
    to_process = all_targets[:]

    if args.factor_ids:
        target_ids = set(fid.strip() for fid in args.factor_ids.split(","))
        to_process = [f for f in to_process if f["factor_id"] in target_ids]
        invalid = target_ids - {f["factor_id"] for f in to_process}
        if invalid:
            print(f"\n  WARNING: requested factor_ids not found or skipped: {sorted(invalid)}")

    if args.only_missing:
        existing = get_existing_complete_outputs()
        before = len(to_process)
        to_process = [
            f for f in to_process
            if (f["factor_id"], f["best_horizon"]) not in existing
        ]
        print(f"\n  --only-missing: {before} → {len(to_process)} factors to process")

    if args.max_factors is not None:
        to_process = to_process[:args.max_factors]
        print(f"  --max-factors: limited to {len(to_process)} factors")

    print(f"\n  Final: {len(to_process)} factor-horizon pairs to process")

    if not to_process:
        print("\n  Nothing to process. Exiting.")
        return 0

    for f in to_process:
        dir_tag = f"dir={f['strategy_direction']}" if f["registry_expected_direction"] == "conditional" else f["strategy_direction"]
        print(f"    {f['factor_id']} → {f['best_horizon']} ({dir_tag})")

    if args.dry_run:
        print("\n  DRY RUN — not executing.")
        return 0

    # ── Load shared data ─────────────────────────────────────────────────
    print("\n[3/5] Loading shared data (universe + returns panel)...")
    universe_set = load_universe_eligible_set()
    print(f"  Universe eligible pairs: {len(universe_set)}")

    returns_panel = load_realized_1h_returns()
    print(f"  Realized 1h returns: {len(returns_panel)} rows")
    print(f"  Return ts range: {returns_panel['return_start_ts'].min()} to {returns_panel['return_start_ts'].max()}")

    # ── Process each factor ──────────────────────────────────────────────
    print("\n[4/5] Processing factors...")
    RETURNS_DIR.mkdir(parents=True, exist_ok=True)
    results = []

    for i, finfo in enumerate(to_process):
        fid = finfo["factor_id"]
        hz = finfo["best_horizon"]
        strategy_dir = finfo["strategy_direction"]
        h = finfo["holding_hours"]
        fv_path = finfo["factor_values_path"]

        dir_label = strategy_dir
        if finfo["registry_expected_direction"] == "conditional":
            dir_label = f"conditional→{strategy_dir}"

        print(f"\n  [{i+1}/{len(to_process)}] {fid} (horizon={hz}, direction={dir_label}, h={h})")
        t0 = time.time()

        summary_row = compute_sleeve_strategy_returns(
            factor_id=fid,
            strategy_direction=strategy_dir,
            holding_hours=h,
            factor_values_path=fv_path,
            returns_panel=returns_panel,
            universe_set=universe_set,
            dir_info={
                "registry_expected_direction": finfo["registry_expected_direction"],
                "direction_source": finfo["direction_source"],
                "direction_confidence": finfo["direction_confidence"],
                "direction_warning": finfo.get("direction_warning"),
            },
            hz_info={
                "best_horizon_source": finfo["best_horizon_source"],
                "horizon_confidence": finfo["horizon_confidence"],
                "horizon_warning": finfo.get("horizon_warning"),
            },
            overwrite=args.overwrite,
        )
        results.append(summary_row)

        elapsed = time.time() - t0
        status = summary_row["status"]
        print(f"    → status={status}, runtime={elapsed:.1f}s", end="")
        if status in ("OK", "OK_WITH_WARNING"):
            print(f", n_return_hours={summary_row.get('n_return_hours', 0)}", end="")
            sharpe = summary_row.get("gross_sharpe")
            if sharpe is not None:
                print(f", sharpe={sharpe}", end="")
        print()

        gc.collect()

    # ── Write outputs ────────────────────────────────────────────────────
    print("\n[5/5] Writing outputs...")

    summary_df = merge_summary(results)

    elapsed_total = time.time() - t_start
    n_processed = sum(1 for r in results if r["status"] in ("OK", "OK_WITH_WARNING"))
    n_skipped = sum(1 for r in results if r["status"] not in ("OK", "OK_WITH_WARNING"))
    skipped_by_reason = {}
    for r in results:
        if r["status"] not in ("OK", "OK_WITH_WARNING"):
            reason = r.get("skip_reason") or r["status"]
            skipped_by_reason[reason] = skipped_by_reason.get(reason, 0) + 1

    warnings = []
    for r in results:
        if r.get("warning"):
            warnings.append(f"{r['factor_id']}: {r['warning']}")

    manifest = {
        "pm_id": "PM-59A",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "command": " ".join(sys.argv),
        "input_files": {
            "state": str(STATE_PATH),
            "coverage": str(COVERAGE_PATH),
            "universe": str(UNIVERSE_PATH),
            "bars_1h": str(BARS_PATH),
        },
        "output_files": {
            "summary_csv": str(SUMMARY_CSV),
            "summary_json": str(SUMMARY_JSON),
            "manifest_json": str(MANIFEST_JSON),
            "returns_dir": str(RETURNS_DIR),
        },
        "n_registered": n_registered,
        "n_computed": n_computed,
        "n_target_factors": len(all_targets),
        "n_processed_ok": n_processed,
        "n_processed_with_warning": sum(1 for r in results if r["status"] == "OK_WITH_WARNING"),
        "n_skipped": n_skipped,
        "skipped_by_reason": skipped_by_reason,
        "n_empirical_direction": n_empirical_dir,
        "n_default_direction": n_default_dir,
        "n_derived_horizon": n_derived_hz,
        "n_default_horizon": n_default_hz,
        "return_convention": "long_mean_minus_short_mean_spread",
        "timestamp_convention": "realized_1h_return[return_start_ts] = close[return_start_ts+1h]/close[return_start_ts]-1",
        "universe_convention": "monthly volume top50 from universe_snapshots.parquet",
        "annualization_method": "arithmetic_mean_hourly_x_8760",
        "quantile_method": "cross-sectional_rank_pct",
        "eligible_source": "factor_library_state.json (computed_factor_ids) + factor_values.parquet",
        "direction_source_policy": "registry_positive/negative → direct; conditional → empirical RankIC/LS or default",
        "horizon_source_policy": "coverage > diagnostics > abs_rankic > abs_ls > default_72h",
        "long_quantile": LONG_QUANTILE,
        "short_quantile": SHORT_QUANTILE,
        "warnings": warnings,
        "total_runtime_seconds": round(elapsed_total, 1),
    }

    write_summary_and_manifest(summary_df, manifest)

    print(f"\n  Summary CSV: {SUMMARY_CSV}")
    print(f"  Summary JSON: {SUMMARY_JSON}")
    print(f"  Manifest: {MANIFEST_JSON}")
    print(f"  Per-factor returns: {RETURNS_DIR}/")
    print(f"\n  Processed: {n_processed}/{len(to_process)}")
    print(f"  Skipped: {n_skipped}/{len(to_process)}")
    print(f"  Total runtime: {elapsed_total:.1f}s")

    ok_results = [r for r in results if r["status"] in ("OK", "OK_WITH_WARNING")]
    if ok_results:
        print(f"\n  {'Factor':<45} {'Hz':>4} {'Sharpe':>8} {'MaxDD':>8} {'WinRate':>8} {'AnnVol':>8}")
        print(f"  {'-'*45} {'-'*4} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")
        for r in ok_results:
            print(f"  {r['factor_id']:<45} {r['horizon']:>4} "
                  f"{str(r.get('gross_sharpe', 'N/A')):>8} "
                  f"{str(r.get('max_drawdown', 'N/A')):>8} "
                  f"{str(r.get('hourly_win_rate', 'N/A')):>8} "
                  f"{str(r.get('gross_annualized_vol', 'N/A')):>8}")

    return 0


def load_universe_eligible_set() -> pd.DataFrame:
    """Load universe snapshots, return DataFrame with (asof_month, symbol) → eligible."""
    univ = pd.read_parquet(UNIVERSE_PATH, columns=["asof_time", "symbol", "eligible"])
    univ = univ[univ["eligible"] == True].copy()
    univ["asof_time"] = pd.to_datetime(univ["asof_time"], utc=True)
    univ["universe_month"] = univ["asof_time"].dt.to_period("M")
    return univ[["universe_month", "symbol"]].drop_duplicates()


def load_realized_1h_returns() -> pd.DataFrame:
    """Load bars and compute realized 1h returns.

    realized_1h_return[ts, sym] = close[ts+1h, sym] / close[ts, sym] - 1
    """
    bars = pd.read_parquet(BARS_PATH, columns=["timestamp", "symbol", "close"])
    bars = bars.sort_values(["symbol", "timestamp"]).reset_index(drop=True)
    bars["realized_1h_return"] = bars.groupby("symbol")["close"].pct_change()
    bars["realized_1h_return"] = bars.groupby("symbol")["realized_1h_return"].shift(-1)
    bars = bars.dropna(subset=["realized_1h_return"])

    result = bars[["timestamp", "symbol", "realized_1h_return"]].copy()
    result = result.rename(columns={"timestamp": "return_start_ts"})
    if result["return_start_ts"].dt.tz is None:
        result["return_start_ts"] = result["return_start_ts"].dt.tz_localize("UTC")
    return result


if __name__ == "__main__":
    sys.exit(main())
