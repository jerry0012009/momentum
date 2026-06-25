#!/usr/bin/env python3
"""PM-59A: Overlapping Sleeve Strategy Diagnostics.

Computes per-factor hourly strategy return series using overlapping sleeves.
Each factor's canonical best_horizon determines the holding period.
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


def load_best_horizon_map() -> dict[str, str]:
    """Load best_adj_ic_horizon from coverage summary, fallback to diagnostics."""
    hz_map: dict[str, str] = {}

    # Primary: coverage summary
    if COVERAGE_PATH.exists():
        cov = pd.read_csv(COVERAGE_PATH)
        for _, row in cov.iterrows():
            hz = row.get("best_adj_ic_horizon")
            if pd.notna(hz) and str(hz) in HORIZON_MAP:
                hz_map[row["factor_name"]] = str(hz)

    # Fallback: diagnostics summary
    if DIAG_SUMMARY_PATH.exists():
        diag = pd.read_csv(DIAG_SUMMARY_PATH)
        for _, row in diag.iterrows():
            fid = row.get("factor_id")
            hz = row.get("best_horizon")
            if fid and pd.notna(hz) and fid not in hz_map:
                hz_str = str(hz).strip()
                if hz_str in HORIZON_MAP:
                    hz_map[fid] = hz_str

    return hz_map


def load_universe_eligible_set() -> pd.DataFrame:
    """Load universe snapshots, return DataFrame with (asof_month, symbol) → eligible."""
    univ = pd.read_parquet(UNIVERSE_PATH, columns=["asof_time", "symbol", "eligible"])
    univ = univ[univ["eligible"] == True].copy()
    # Parse asof_time to month period for joining
    univ["asof_time"] = pd.to_datetime(univ["asof_time"], utc=True)
    univ["universe_month"] = univ["asof_time"].dt.to_period("M")
    return univ[["universe_month", "symbol"]].drop_duplicates()


def load_realized_1h_returns() -> pd.DataFrame:
    """Load bars and compute realized 1h returns.

    realized_1h_return[ts, sym] = close[ts+1h, sym] / close[ts, sym] - 1

    This means: at timestamp t, the return for "the next hour" is stored
    with return_start_ts = t. When a sleeve enters at entry_ts, its first
    hour's return uses return_start_ts = entry_ts, second hour uses
    return_start_ts = entry_ts + 1h, etc.
    """
    bars = pd.read_parquet(BARS_PATH, columns=["timestamp", "symbol", "close"])
    bars = bars.sort_values(["symbol", "timestamp"]).reset_index(drop=True)

    # Compute per-symbol hourly return
    bars["realized_1h_return"] = bars.groupby("symbol")["close"].pct_change()

    # Shift: realized_1h_return at ts means "return from ts to ts+1h"
    # We want: at return_start_ts = t, return = close[t+1]/close[t] - 1
    # pct_change already gives close[t]/close[t-1] - 1, so we need to shift forward
    # Actually: pct_change() at row t gives (close[t] - close[t-1]) / close[t-1]
    # We want: return_start_ts=t → close[t+1]/close[t] - 1
    # So we need to shift the result backward by 1 within each group
    bars["realized_1h_return"] = bars.groupby("symbol")["realized_1h_return"].shift(-1)

    # Drop NaN returns (first row per symbol has no prior, last row has no next)
    bars = bars.dropna(subset=["realized_1h_return"])

    result = bars[["timestamp", "symbol", "realized_1h_return"]].copy()
    result = result.rename(columns={"timestamp": "return_start_ts"})
    # Ensure return_start_ts is timezone-aware UTC for consistent merging
    if result["return_start_ts"].dt.tz is None:
        result["return_start_ts"] = result["return_start_ts"].dt.tz_localize("UTC")
    return result


def discover_eligible_factors(
    direction_map: dict[str, str],
    hz_map: dict[str, str],
) -> tuple[list[dict], list[tuple[str, str]]]:
    """Discover eligible factors from canonical workflow artifacts.

    Returns list of dicts: {factor_id, expected_direction, best_horizon, ...}
    """
    state = json.loads(STATE_PATH.read_text())
    registered_ids = set(state.get("registered_factor_ids", []))

    eligible = []
    skipped = []

    for fid in sorted(registered_ids):
        # Check factor_values exists
        fv_path = FEATURES_DIR / fid / "factor_values.parquet"
        if not fv_path.exists():
            skipped.append((fid, "MISSING_FACTOR_VALUES"))
            continue

        # Check direction
        direction = direction_map.get(fid)
        if direction is None:
            skipped.append((fid, "MISSING_DIRECTION"))
            continue
        if direction == "conditional":
            skipped.append((fid, "SKIPPED_CONDITIONAL_DIRECTION"))
            continue
        if direction not in ("positive", "negative"):
            skipped.append((fid, f"INVALID_DIRECTION:{direction}"))
            continue

        # Check best_horizon
        hz = hz_map.get(fid)
        if hz is None:
            skipped.append((fid, "MISSING_BEST_HORIZON"))
            continue

        holding_hours = HORIZON_MAP.get(hz)
        if holding_hours is None:
            skipped.append((fid, f"INVALID_HORIZON:{hz}"))
            continue

        eligible.append({
            "factor_id": fid,
            "expected_direction": direction,
            "best_horizon": hz,
            "holding_hours": holding_hours,
            "factor_values_path": str(fv_path),
        })

    return eligible, skipped


def get_existing_complete_outputs() -> set[tuple[str, str]]:
    """Scan existing outputs, return set of (factor_id, horizon) that are complete."""
    complete = set()
    if not SUMMARY_CSV.exists():
        return complete
    try:
        df = pd.read_csv(SUMMARY_CSV)
        for _, row in df.iterrows():
            if row.get("status") == "OK":
                fid = row.get("factor_id")
                hz = row.get("horizon")
                if fid and hz:
                    complete.add((str(fid), str(hz)))
    except Exception:
        pass
    return complete


# ── Core Computation ─────────────────────────────────────────────────────────

def compute_sleeve_strategy_returns(
    factor_id: str,
    expected_direction: str,
    holding_hours: int,
    factor_values_path: str,
    returns_panel: pd.DataFrame,
    universe_set: pd.DataFrame,
    overwrite: bool = False,
) -> dict:
    """Compute overlapping sleeve strategy returns for one factor.

    Returns summary dict with metrics.
    """
    t0 = time.time()
    result = {
        "factor_id": factor_id,
        "horizon": f"{holding_hours}h",
        "expected_direction": expected_direction,
        "holding_hours": holding_hours,
        "status": "OK",
        "skip_reason": None,
        "warning": None,
    }

    # Determine direction handling
    if expected_direction == "positive":
        direction_handling = "positive_aligned"
    elif expected_direction == "negative":
        direction_handling = "negative_flipped"
    else:
        direction_handling = "raw_order_conditional"

    result["direction_handling"] = direction_handling
    result["strategy_return_convention"] = "long_mean_minus_short_mean_spread"
    result["return_timestamp_convention"] = (
        "realized_1h_return[return_start_ts, symbol] = close[return_start_ts+1h] / close[return_start_ts] - 1"
    )
    result["eligible_source"] = "factor_library_state.json + factor_values.parquet + coverage_summary"
    result["best_horizon_source"] = "factor_level_coverage_summary.csv (primary) / factor_diagnostics_summary.csv (fallback)"
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

    # Drop NaN factor values
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
    # For positive: high factor_value = high rank → long top
    # For negative: low factor_value = high rank (flip) → long top after flip
    if expected_direction == "negative":
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

    # Create holding offsets
    offsets = np.arange(1, h + 1)  # [1, 2, ..., h]

    # Repeat each signal row h times
    entry_ts_repeated = np.repeat(signals["entry_ts"].values, h)
    symbol_repeated = np.repeat(signals["symbol"].values, h)
    basket_repeated = np.repeat(signals["basket"].values, h)
    offset_tiled = np.tile(offsets, n_signals)

    # Compute return_start_ts for each row
    # return_start_ts = entry_ts + (offset - 1) hours
    # offset=1 → return_start_ts = entry_ts (first hour return)
    # offset=2 → return_start_ts = entry_ts + 1h (second hour return)
    return_start_ts = entry_ts_repeated + pd.to_timedelta(offset_tiled - 1, unit="h")

    expanded = pd.DataFrame({
        "entry_ts": entry_ts_repeated,
        "return_start_ts": return_start_ts,
        "symbol": symbol_repeated,
        "basket": basket_repeated,
        "holding_offset": offset_tiled,
    })

    # Merge with realized 1h returns
    # returns_panel has columns: return_start_ts, symbol, realized_1h_return
    # Ensure both sides have consistent timezone awareness
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

    # Fill missing returns with 0 (conservative: no return if data missing)
    expanded["realized_1h_return"] = expanded["realized_1h_return"].fillna(0.0)

    # Compute sleeve-level hourly return: mean(long) - mean(short)
    # Group by (entry_ts, return_start_ts) → get long_mean and short_mean
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
    # A sleeve is "active" at return_start_ts if entry_ts <= return_start_ts < entry_ts + h hours
    # By construction, each row in sleeve_returns IS an active contribution
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

    # Gross total return (compounded)
    gross_total = np.prod(1 + hourly_rets) - 1
    result["gross_total_return"] = _r4(gross_total)

    # Arithmetic annualized return
    mean_hourly = np.mean(hourly_rets)
    result["gross_annualized_return"] = _r4(mean_hourly * 8760)

    # Annualized vol
    std_hourly = np.std(hourly_rets, ddof=1) if len(hourly_rets) > 1 else 0.0
    result["gross_annualized_vol"] = _r4(std_hourly * np.sqrt(8760))

    # Sharpe
    if std_hourly > 0:
        result["gross_sharpe"] = _r4(mean_hourly / std_hourly * np.sqrt(8760))
    else:
        result["gross_sharpe"] = None

    # Max drawdown
    cum_returns = np.cumprod(1 + hourly_rets)
    running_max = np.maximum.accumulate(cum_returns)
    drawdowns = cum_returns / running_max - 1
    max_dd = np.min(drawdowns)
    result["max_drawdown"] = _r4(max_dd)

    # Hourly win rate
    valid_rets = hourly_rets[np.isfinite(hourly_rets)]
    if len(valid_rets) > 0:
        result["hourly_win_rate"] = _r4(np.sum(valid_rets > 0) / len(valid_rets))
    else:
        result["hourly_win_rate"] = None

    # Mean / std hourly return
    result["mean_hourly_return"] = _r4(mean_hourly)
    result["std_hourly_return"] = _r4(std_hourly)

    # Active sleeve count stats
    result["active_sleeve_count_mean"] = _r4(float(np.mean(active_counts)))
    result["active_sleeve_count_median"] = _r4(float(np.median(active_counts)))
    result["active_sleeve_count_min"] = int(np.min(active_counts))
    result["active_sleeve_count_max"] = int(np.max(active_counts))

    # Missing return rate
    result["missing_return_hour_rate"] = _r4(missing_rate)

    # Warm-up warning
    if holding_hours > 1:
        warmup = strategy.head(holding_hours)
        warmup_max = warmup["active_sleeve_count"].max() if len(warmup) > 0 else 0
        if warmup_max < holding_hours:
            result["warning"] = (result["warning"] or "") + (
                f"warmup_period: first {holding_hours} hours have "
                f"active_sleeve_count_max={warmup_max} < {holding_hours}; "
            )

    # Annualization warning
    if len(strategy) < 8760:
        result["warning"] = (result["warning"] or "") + (
            f"sample_less_than_1_year: {len(strategy)} hours < 8760; "
            f"arithmetic_annualization_may_exaggerate; "
        )

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
            # Remove rows that are being re-processed
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

    # CSV
    summary_df.to_csv(SUMMARY_CSV, index=False)

    # JSON (sanitize NaN/inf)
    summary_records = summary_df.replace({np.nan: None, np.inf: None, -np.inf: None})
    summary_json = summary_records.to_dict(orient="records")
    SUMMARY_JSON.write_text(json.dumps(summary_json, indent=2, default=str, ensure_ascii=False))

    # Manifest
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
    hz_map = load_best_horizon_map()
    print(f"  direction_map: {len(direction_map)} factors")
    print(f"  best_horizon_map: {len(hz_map)} factors")

    # ── Discover eligible factors ────────────────────────────────────────
    print("\n[2/5] Discovering eligible factors...")
    all_eligible, all_skipped = discover_eligible_factors(direction_map, hz_map)

    state = json.loads(STATE_PATH.read_text())
    n_registered = len(state.get("registered_factor_ids", []))
    n_computed = len(state.get("computed_factor_ids", []))

    print(f"  Registered: {n_registered}")
    print(f"  Computed: {n_computed}")
    print(f"  Eligible: {len(all_eligible)}")
    print(f"  Skipped: {len(all_skipped)}")

    if all_skipped:
        print("\n  Skipped factors:")
        skip_reasons = {}
        for fid, reason in all_skipped:
            skip_reasons[reason] = skip_reasons.get(reason, 0) + 1
            if reason in ("SKIPPED_CONDITIONAL_DIRECTION", "MISSING_BEST_HORIZON"):
                print(f"    {fid}: {reason}")
        print(f"\n  Skip reason distribution:")
        for reason, count in sorted(skip_reasons.items()):
            print(f"    {reason}: {count}")

    # ── Apply filters ────────────────────────────────────────────────────
    to_process = all_eligible[:]

    # --factor-ids filter
    if args.factor_ids:
        target_ids = set(fid.strip() for fid in args.factor_ids.split(","))
        to_process = [f for f in to_process if f["factor_id"] in target_ids]
        invalid = target_ids - {f["factor_id"] for f in to_process}
        if invalid:
            print(f"\n  WARNING: requested factor_ids not eligible: {sorted(invalid)}")

    # --only-missing filter
    if args.only_missing:
        existing = get_existing_complete_outputs()
        before = len(to_process)
        to_process = [
            f for f in to_process
            if (f["factor_id"], f["best_horizon"]) not in existing
        ]
        print(f"\n  --only-missing: {before} → {len(to_process)} factors to process")

    # --max-factors limit
    if args.max_factors is not None:
        to_process = to_process[:args.max_factors]
        print(f"  --max-factors: limited to {len(to_process)} factors")

    print(f"\n  Final: {len(to_process)} factor-horizon pairs to process")

    if not to_process:
        print("\n  Nothing to process. Exiting.")
        return 0

    # Print plan
    for f in to_process:
        print(f"    {f['factor_id']} → {f['best_horizon']} ({f['expected_direction']})")

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
        direction = finfo["expected_direction"]
        h = finfo["holding_hours"]
        fv_path = finfo["factor_values_path"]

        print(f"\n  [{i+1}/{len(to_process)}] {fid} (horizon={hz}, direction={direction}, h={h})")
        t0 = time.time()

        summary_row = compute_sleeve_strategy_returns(
            factor_id=fid,
            expected_direction=direction,
            holding_hours=h,
            factor_values_path=fv_path,
            returns_panel=returns_panel,
            universe_set=universe_set,
            overwrite=args.overwrite,
        )
        results.append(summary_row)

        elapsed = time.time() - t0
        status = summary_row["status"]
        print(f"    → status={status}, runtime={elapsed:.1f}s", end="")
        if status == "OK":
            print(f", n_return_hours={summary_row.get('n_return_hours', 0)}", end="")
            sharpe = summary_row.get("gross_sharpe")
            if sharpe is not None:
                print(f", sharpe={sharpe}", end="")
        print()

        # Free memory
        gc.collect()

    # ── Write outputs ────────────────────────────────────────────────────
    print("\n[5/5] Writing outputs...")

    # Merge with existing summary
    summary_df = merge_summary(results)

    # Build manifest
    elapsed_total = time.time() - t_start
    n_processed = sum(1 for r in results if r["status"] == "OK")
    n_skipped = sum(1 for r in results if r["status"] != "OK")
    skipped_by_reason = {}
    for r in results:
        if r["status"] != "OK":
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
        "n_eligible": len(all_eligible),
        "n_processed": n_processed,
        "n_skipped": n_skipped,
        "skipped_by_reason": skipped_by_reason,
        "return_convention": "long_mean_minus_short_mean_spread",
        "timestamp_convention": "realized_1h_return[return_start_ts] = close[return_start_ts+1h]/close[return_start_ts]-1",
        "universe_convention": "monthly volume top50 from universe_snapshots.parquet",
        "annualization_method": "arithmetic_mean_hourly_x_8760",
        "quantile_method": "cross-sectional_rank_pct",
        "eligible_source": "factor_library_state.json + factor_values.parquet + coverage_summary + factor_formula_registry",
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

    # Print summary table
    ok_results = [r for r in results if r["status"] == "OK"]
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


if __name__ == "__main__":
    sys.exit(main())
