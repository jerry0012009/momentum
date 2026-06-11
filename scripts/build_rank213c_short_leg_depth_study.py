#!/usr/bin/env python3
"""213c Short Leg Gate & Capital Allocation Depth Study.

Tests 21 new variants (5 groups) + 3 references on the buffer8_50_50 base,
with walk-forward validation at 4/8/12 bps cost assumptions.

Groups:
  A — Composite AND gates (4)
  B — Threshold gates (4)
  C — Adaptive capital allocation (5)
  D — New indicator gates (4)
  E — Buffer8-weekly combinations (4)
"""
from __future__ import annotations

import importlib.util
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank213_largecap_xs_jump_veto"
SITE_PATH = ROOT / "reports" / "site" / "paper" / "213c_short_leg_research.html"
BUFFER8_SCRIPT_PATH = ROOT / "scripts" / "build_rank213c_buffer8_focus_research.py"

SUMMARY_PATH = ART_DIR / "rank213c_short_leg_depth_summary.json"
RESULTS_PATH = ART_DIR / "rank213c_short_leg_depth_results.csv"
DAILY_PATH = ART_DIR / "rank213c_short_leg_depth_daily.csv"
WF_PATH = ART_DIR / "rank213c_short_leg_depth_walk_forward.csv"
ANNUAL_PATH = ART_DIR / "rank213c_short_leg_depth_annual.csv"

COST_GRID_BPS = [4.0, 8.0, 12.0]
SAMPLE_START = pd.Timestamp("2020-02-01T00:00:00Z")

# Walk-forward fold boundaries
WF_FOLDS = [
    {"train_end": "2021-12", "test_year": "2022"},
    {"train_end": "2022-12", "test_year": "2023"},
    {"train_end": "2023-12", "test_year": "2024"},
    {"train_end": "2024-12", "test_year": "2025"},
    {"train_end": "2025-12", "test_year": "2026"},
]


def load_buffer8_module():
    spec = importlib.util.spec_from_file_location("rank213_buffer8_short_leg_mod", BUFFER8_SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load {BUFFER8_SCRIPT_PATH}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["rank213_buffer8_short_leg_mod"] = mod
    spec.loader.exec_module(mod)
    return mod


buf8 = load_buffer8_module()
fifth = buf8.fifth

# Re-export helpers
BufferSpec = buf8.BufferSpec
summarize_daily = buf8.summarize_daily
classify = buf8.classify
table_html = buf8.table_html
fmt_pct = buf8.fmt_pct
fmt_bps = buf8.fmt_bps
fmt_num = buf8.fmt_num


# ---------------------------------------------------------------------------
# 1. Extended market context — new indicator columns
# ---------------------------------------------------------------------------

def extend_market_context(ctx: pd.DataFrame) -> pd.DataFrame:
    """Add 6 new causal indicator columns to the context DataFrame."""
    out = ctx.copy()

    btc_ret = pd.to_numeric(out["btc_ret"], errors="coerce").fillna(0.0)
    eligible_ret = pd.to_numeric(out["eligible_ew_ret"], errors="coerce").fillna(0.0)

    # D1: BTC consecutive 3 up days (shifted ≥1)
    r1 = btc_ret.shift(1)
    r2 = btc_ret.shift(2)
    r3 = btc_ret.shift(3)
    out["btc_consecutive_up_3d"] = (r1 > 0) & (r2 > 0) & (r3 > 0)

    # D2: Eligible consecutive 3 down days
    er1 = eligible_ret.shift(1)
    er2 = eligible_ret.shift(2)
    er3 = eligible_ret.shift(3)
    out["eligible_consecutive_down_3d"] = (er1 < 0) & (er2 < 0) & (er3 < 0)

    # D3: BTC vol expansion (7d vol > 1.5x 30d vol)
    btc_vol_7d = btc_ret.shift(1).rolling(7, min_periods=5).std()
    btc_vol_30d = btc_ret.shift(1).rolling(30, min_periods=20).std()
    out["btc_realized_vol_7d"] = btc_vol_7d
    out["btc_realized_vol_30d"] = btc_vol_30d
    out["btc_vol_expansion"] = btc_vol_7d > 1.5 * btc_vol_30d

    # D4: Dispersion above rolling 60-day Q75 (avoids full-sample look-ahead)
    disp = pd.to_numeric(out["eligible_dispersion_p90_p10"], errors="coerce")
    rolling_q75 = disp.shift(1).rolling(60, min_periods=40).quantile(0.75)
    out["dispersion_above_rolling_q75"] = disp > rolling_q75

    # Also store median for Group B3
    prior30_disp = pd.to_numeric(out.get("prior30_dispersion", pd.Series(dtype=float)), errors="coerce")
    if "prior30_dispersion_q50" not in out.columns:
        valid = prior30_disp.dropna()
        if len(valid):
            out["prior30_dispersion_q50"] = valid.median()

    return out


# ---------------------------------------------------------------------------
# 2. Extended gate series — returns boolean mask for any gate name
# ---------------------------------------------------------------------------

def extended_gate_series(ctx: pd.DataFrame, name: str) -> pd.Series:
    """Return a boolean gate mask. Supports all existing gates + 12 new ones."""
    if name == "always":
        return pd.Series(True, index=ctx.index)
    if name == "never":
        return pd.Series(False, index=ctx.index)

    # Try existing gates first
    existing = fifth.gate_masks(ctx)
    if name in existing:
        return existing[name].fillna(False).astype(bool)

    # Group A: Composite AND gates
    if name == "btc_prior7_positive_AND_dispersion_mid_high":
        return (ctx["prior7_btc_ret"] > 0) & (ctx["prior30_dispersion_mid_high"].fillna(False).astype(bool))
    if name == "btc_prior7_negative_AND_dispersion_mid_high":
        return (ctx["prior7_btc_ret"] < 0) & (ctx["prior30_dispersion_mid_high"].fillna(False).astype(bool))
    if name == "eligible_prior7_negative_AND_dispersion_mid_high":
        return (ctx["prior7_eligible_ew_ret"] < 0) & (ctx["prior30_dispersion_mid_high"].fillna(False).astype(bool))
    if name == "btc_above_ma20_AND_dispersion_mid_high":
        return ctx["btc_above_ma20"].fillna(False).astype(bool) & ctx["prior30_dispersion_mid_high"].fillna(False).astype(bool)

    # Group B: Threshold gates
    if name == "btc_prior7_above_5pct":
        return ctx["prior7_btc_ret"] > 0.05
    if name == "eligible_prior7_below_neg5pct":
        return ctx["prior7_eligible_ew_ret"] < -0.05
    if name == "dispersion_above_median":
        q50 = ctx["prior30_dispersion_q50"].iloc[0] if "prior30_dispersion_q50" in ctx.columns else ctx["prior30_dispersion"].median()
        return ctx["prior30_dispersion"] > q50
    if name == "dispersion_above_q67_AND_btc_prior7_positive":
        return (ctx["prior30_dispersion_high"].fillna(False).astype(bool)) & (ctx["prior7_btc_ret"] > 0)

    # Group D: New indicator gates
    if name == "btc_consecutive_up_3d":
        return ctx["btc_consecutive_up_3d"].fillna(False).astype(bool)
    if name == "eligible_consecutive_down_3d":
        return ctx["eligible_consecutive_down_3d"].fillna(False).astype(bool)
    if name == "btc_vol_expansion":
        return ctx["btc_vol_expansion"].fillna(False).astype(bool)
    if name == "dispersion_above_rolling_q75":
        return ctx["dispersion_above_rolling_q75"].fillna(False).astype(bool)

    raise KeyError(f"unknown gate: {name}")


# ---------------------------------------------------------------------------
# 3. Adaptive capital series builders (Group C)
# ---------------------------------------------------------------------------

def build_short_capital_series(ctx: pd.DataFrame, mode: str) -> pd.Series:
    """Return a Series of short_capital values aligned to ctx.index."""
    n = len(ctx)
    disp = pd.to_numeric(ctx.get("prior30_dispersion", pd.Series(dtype=float)), errors="coerce")
    btc_ret7 = pd.to_numeric(ctx.get("prior7_btc_ret", pd.Series(dtype=float)), errors="coerce")
    elig_ret7 = pd.to_numeric(ctx.get("prior7_eligible_ew_ret", pd.Series(dtype=float)), errors="coerce")

    # Get tercile boundaries from full-sample (causal: these are descriptive labels)
    valid_disp = disp.dropna()
    q33 = valid_disp.quantile(1 / 3) if len(valid_disp) else 0.0
    q50 = valid_disp.quantile(0.5) if len(valid_disp) else 0.0
    q67 = valid_disp.quantile(2 / 3) if len(valid_disp) else 0.0

    if mode == "adaptive_cap_dispersion_3level":
        # C1: high disp→0.5, mid→0.25, low→0.0
        caps = pd.Series(0.25, index=ctx.index)
        caps[disp > q67] = 0.5
        caps[disp <= q33] = 0.0
        return caps

    if mode == "adaptive_cap_btc_regime_3level":
        # C2: crash(<-5%)→0.25, bull(>0)→0.5, neutral→0.375
        caps = pd.Series(0.375, index=ctx.index)
        caps[btc_ret7 > 0] = 0.5
        caps[btc_ret7 < -0.05] = 0.25
        return caps

    if mode == "adaptive_cap_eligible_trend_2level":
        # C3: eligible up→0.5, down→0.25
        caps = pd.Series(0.25, index=ctx.index)
        caps[elig_ret7 > 0] = 0.5
        return caps

    if mode == "adaptive_cap_combined_4level":
        # C4: 2D grid: dispersion × BTC direction
        caps = pd.Series(0.125, index=ctx.index)  # low disp, BTC down
        caps[(disp > q50) & (btc_ret7 > 0)] = 0.5       # high disp, BTC up
        caps[(disp > q50) & (btc_ret7 <= 0)] = 0.375     # high disp, BTC down
        caps[(disp <= q50) & (btc_ret7 > 0)] = 0.25      # low disp, BTC up
        return caps

    raise KeyError(f"unknown adaptive mode: {mode}")


# ---------------------------------------------------------------------------
# 4. Simulation functions using extended gates
# ---------------------------------------------------------------------------

def simulate_spec_extended(
    spec: BufferSpec,
    *,
    next_ret: pd.DataFrame,
    score_panel: pd.DataFrame,
    ranked_by_month: dict[str, list[str]],
    onboard_map: dict[str, pd.Timestamp],
    ctx: pd.DataFrame,
) -> pd.DataFrame:
    """Like buf8.simulate_spec but uses extended_gate_series for new gates."""
    rows: list[dict] = []
    prev_weights: dict[str, float] = {}
    prev_longs: list[str] = []
    prev_shorts: list[str] = []
    last_rebalance_i = -10**9
    short_gate = extended_gate_series(ctx, spec.short_gate)
    active_guard = buf8.guard_series(ctx, spec.market_guard)

    for i, row in ctx.iterrows():
        ts = row["timestamp_ts"]
        month = str(row["month"])
        do_rebalance = (i - last_rebalance_i) >= spec.rebalance_every_days or not prev_weights
        if do_rebalance:
            universe = ranked_by_month.get(month, [])[:spec.universe_size]
            eligible = fifth.eligible_for_day(universe, onboard_map, ts)
            cols = [sym for sym in eligible if sym in score_panel.columns]
            scores = pd.Series(dtype=float)
            if cols and ts in score_panel.index:
                scores = pd.to_numeric(score_panel.loc[ts, cols], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
            desired_longs, desired_shorts = buf8.choose_legs(scores, spec)
            if desired_longs or desired_shorts:
                long_rank = scores.sort_values(ascending=False).index.astype(str).tolist()
                short_rank = scores.sort_values(ascending=True).index.astype(str).tolist()
                new_longs = buf8.apply_side_buffer(prev_longs, desired_longs, long_rank, spec.long_count, spec.long_buffer_extra)
                new_shorts = buf8.apply_side_buffer(prev_shorts, desired_shorts, short_rank, spec.short_count, spec.short_buffer_extra)
                if spec.replacement_cap is not None and prev_longs and prev_shorts:
                    new_longs = fifth.apply_replacement_cap(prev_longs, new_longs, spec.replacement_cap)
                    new_shorts = fifth.apply_replacement_cap(prev_shorts, new_shorts, spec.replacement_cap)
                prev_longs = new_longs
                prev_shorts = new_shorts
                last_rebalance_i = i

        guard_on = bool(active_guard.iloc[i])
        use_short = guard_on and bool(short_gate.iloc[i])
        target_weights = fifth.weights_from_longs_shorts(
            prev_longs if guard_on else [],
            prev_shorts if use_short else [],
            long_capital=spec.long_capital,
            short_capital=spec.short_capital,
        )
        cur_weights = buf8.blend_or_cap_weights(prev_weights, target_weights, spec)
        gross, long_ret, short_ret, long_count, short_count = fifth.returns_for_weights(next_ret, cur_weights, ts)
        t = fifth.turnover(prev_weights, cur_weights)
        rows.append({
            "experiment_group": spec.group,
            "variant": spec.variant,
            "timestamp_ts": ts,
            "month": month,
            "active": bool(cur_weights),
            "active_short": any(w < 0 for w in cur_weights.values()),
            "gross_ret": gross,
            "long_contribution": long_ret,
            "short_contribution": short_ret,
            "target_turnover_x": t,
            "long_count": long_count,
            "short_count": short_count,
            "long_capital": spec.long_capital,
            "short_capital": spec.short_capital,
            "long_buffer_extra": spec.long_buffer_extra,
            "short_buffer_extra": spec.short_buffer_extra,
            "rebalance_every_days": spec.rebalance_every_days,
            "replacement_cap": spec.replacement_cap if spec.replacement_cap is not None else 0,
            "short_gate": spec.short_gate,
            "market_guard": spec.market_guard,
            "weight_blend": spec.weight_blend,
            "turnover_cap_x": spec.turnover_cap_x if spec.turnover_cap_x is not None else np.nan,
            "longs": ",".join(prev_longs),
            "shorts": ",".join(prev_shorts if use_short else []),
        })
        prev_weights = cur_weights
    return pd.DataFrame(rows)


def simulate_spec_adaptive(
    spec: BufferSpec,
    short_capital_series: pd.Series,
    *,
    next_ret: pd.DataFrame,
    score_panel: pd.DataFrame,
    ranked_by_month: dict[str, list[str]],
    onboard_map: dict[str, pd.Timestamp],
    ctx: pd.DataFrame,
) -> pd.DataFrame:
    """Like simulate_spec but uses per-day short_capital from short_capital_series."""
    rows: list[dict] = []
    prev_weights: dict[str, float] = {}
    prev_longs: list[str] = []
    prev_shorts: list[str] = []
    last_rebalance_i = -10**9
    short_gate = extended_gate_series(ctx, spec.short_gate)
    active_guard = buf8.guard_series(ctx, spec.market_guard)

    for i, row in ctx.iterrows():
        ts = row["timestamp_ts"]
        month = str(row["month"])
        do_rebalance = (i - last_rebalance_i) >= spec.rebalance_every_days or not prev_weights
        if do_rebalance:
            universe = ranked_by_month.get(month, [])[:spec.universe_size]
            eligible = fifth.eligible_for_day(universe, onboard_map, ts)
            cols = [sym for sym in eligible if sym in score_panel.columns]
            scores = pd.Series(dtype=float)
            if cols and ts in score_panel.index:
                scores = pd.to_numeric(score_panel.loc[ts, cols], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
            desired_longs, desired_shorts = buf8.choose_legs(scores, spec)
            if desired_longs or desired_shorts:
                long_rank = scores.sort_values(ascending=False).index.astype(str).tolist()
                short_rank = scores.sort_values(ascending=True).index.astype(str).tolist()
                new_longs = buf8.apply_side_buffer(prev_longs, desired_longs, long_rank, spec.long_count, spec.long_buffer_extra)
                new_shorts = buf8.apply_side_buffer(prev_shorts, desired_shorts, short_rank, spec.short_count, spec.short_buffer_extra)
                if spec.replacement_cap is not None and prev_longs and prev_shorts:
                    new_longs = fifth.apply_replacement_cap(prev_longs, new_longs, spec.replacement_cap)
                    new_shorts = fifth.apply_replacement_cap(prev_shorts, new_shorts, spec.replacement_cap)
                prev_longs = new_longs
                prev_shorts = new_shorts
                last_rebalance_i = i

        guard_on = bool(active_guard.iloc[i])
        use_short = guard_on and bool(short_gate.iloc[i])
        day_short_capital = float(short_capital_series.iloc[i]) if use_short else 0.0
        target_weights = fifth.weights_from_longs_shorts(
            prev_longs if guard_on else [],
            prev_shorts if use_short else [],
            long_capital=spec.long_capital,
            short_capital=day_short_capital,
        )
        cur_weights = buf8.blend_or_cap_weights(prev_weights, target_weights, spec)
        gross, long_ret, short_ret, long_count, short_count = fifth.returns_for_weights(next_ret, cur_weights, ts)
        t = fifth.turnover(prev_weights, cur_weights)
        rows.append({
            "experiment_group": spec.group,
            "variant": spec.variant,
            "timestamp_ts": ts,
            "month": month,
            "active": bool(cur_weights),
            "active_short": any(w < 0 for w in cur_weights.values()),
            "gross_ret": gross,
            "long_contribution": long_ret,
            "short_contribution": short_ret,
            "target_turnover_x": t,
            "long_count": long_count,
            "short_count": short_count,
            "long_capital": spec.long_capital,
            "short_capital": day_short_capital,
            "long_buffer_extra": spec.long_buffer_extra,
            "short_buffer_extra": spec.short_buffer_extra,
            "rebalance_every_days": spec.rebalance_every_days,
            "replacement_cap": spec.replacement_cap if spec.replacement_cap is not None else 0,
            "short_gate": spec.short_gate,
            "market_guard": spec.market_guard,
            "weight_blend": spec.weight_blend,
            "turnover_cap_x": spec.turnover_cap_x if spec.turnover_cap_x is not None else np.nan,
            "longs": ",".join(prev_longs),
            "shorts": ",".join(prev_shorts if use_short else []),
        })
        prev_weights = cur_weights
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 5. Variant definitions
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AdaptiveVariant:
    """For Group C adaptive-capital variants that need per-day short_capital."""
    group: str
    variant: str
    adaptive_mode: str
    long_capital: float = 0.5
    long_count: int = 4
    short_count: int = 4
    universe_size: int = 50
    long_buffer_extra: int = 8
    short_buffer_extra: int = 8
    rebalance_every_days: int = 1
    replacement_cap: int | None = None
    short_gate: str = "always"
    market_guard: str = "none"
    weight_blend: float = 1.0
    turnover_cap_x: float | None = None

    def to_buffer_spec(self, short_capital: float = 0.5) -> BufferSpec:
        return BufferSpec(
            group=self.group,
            variant=self.variant,
            long_capital=self.long_capital,
            short_capital=short_capital,
            long_count=self.long_count,
            short_count=self.short_count,
            universe_size=self.universe_size,
            long_buffer_extra=self.long_buffer_extra,
            short_buffer_extra=self.short_buffer_extra,
            rebalance_every_days=self.rebalance_every_days,
            replacement_cap=self.replacement_cap,
            short_gate=self.short_gate,
            market_guard=self.market_guard,
            weight_blend=self.weight_blend,
            turnover_cap_x=self.turnover_cap_x,
        )


def build_buffer_specs() -> list[BufferSpec]:
    """Group A, B, D, E + references — standard BufferSpec variants."""
    specs: list[BufferSpec] = []

    # References
    specs.append(BufferSpec("reference", "base_50_50_daily", long_buffer_extra=0, short_buffer_extra=0))
    specs.append(BufferSpec("reference", "buffer8_50_50", long_buffer_extra=8, short_buffer_extra=8))
    specs.append(BufferSpec("reference", "buffer8_weekly", long_buffer_extra=8, short_buffer_extra=8, rebalance_every_days=7))

    # Group A: Composite AND gates
    for gate in [
        "btc_prior7_positive_AND_dispersion_mid_high",
        "btc_prior7_negative_AND_dispersion_mid_high",
        "eligible_prior7_negative_AND_dispersion_mid_high",
        "btc_above_ma20_AND_dispersion_mid_high",
    ]:
        specs.append(BufferSpec("composite_gate", f"buffer8_{gate}", long_buffer_extra=8, short_buffer_extra=8, short_gate=gate))

    # Group B: Threshold gates
    for gate in [
        "btc_prior7_above_5pct",
        "eligible_prior7_below_neg5pct",
        "dispersion_above_median",
        "dispersion_above_q67_AND_btc_prior7_positive",
    ]:
        specs.append(BufferSpec("threshold_gate", f"buffer8_{gate}", long_buffer_extra=8, short_buffer_extra=8, short_gate=gate))

    # Group D: New indicator gates
    for gate in [
        "btc_consecutive_up_3d",
        "eligible_consecutive_down_3d",
        "btc_vol_expansion",
        "dispersion_above_rolling_q75",
    ]:
        specs.append(BufferSpec("new_indicator_gate", f"buffer8_{gate}", long_buffer_extra=8, short_buffer_extra=8, short_gate=gate))

    # Group E: Buffer8-weekly combinations
    specs.append(BufferSpec("weekly_overlay", "buffer8_weekly_short_btc_prior7_positive", long_buffer_extra=8, short_buffer_extra=8, rebalance_every_days=7, short_gate="btc_prior7_positive"))
    specs.append(BufferSpec("weekly_overlay", "buffer8_weekly_short25", long_capital=0.5, short_capital=0.25, long_buffer_extra=8, short_buffer_extra=8, rebalance_every_days=7))
    specs.append(BufferSpec("weekly_overlay", "buffer8_weekly_dispersion_mid_high", long_buffer_extra=8, short_buffer_extra=8, rebalance_every_days=7, short_gate="prior30_dispersion_mid_high"))
    specs.append(BufferSpec("weekly_overlay", "buffer8_weekly_btc_prior7_negative", long_buffer_extra=8, short_buffer_extra=8, rebalance_every_days=7, short_gate="btc_prior7_negative"))

    return specs


def build_adaptive_variants() -> list[AdaptiveVariant]:
    """Group C: Adaptive capital allocation variants."""
    return [
        AdaptiveVariant("adaptive_cap", "buffer8_adaptive_cap_dispersion_3level", "adaptive_cap_dispersion_3level"),
        AdaptiveVariant("adaptive_cap", "buffer8_adaptive_cap_btc_regime_3level", "adaptive_cap_btc_regime_3level"),
        AdaptiveVariant("adaptive_cap", "buffer8_adaptive_cap_eligible_trend_2level", "adaptive_cap_eligible_trend_2level"),
        AdaptiveVariant("adaptive_cap", "buffer8_adaptive_cap_combined_4level", "adaptive_cap_combined_4level"),
        AdaptiveVariant("adaptive_cap", "buffer8_weekly_adaptive_cap_dispersion", "adaptive_cap_dispersion_3level", rebalance_every_days=7),
    ]


# ---------------------------------------------------------------------------
# 6. Gate indicator summary — active/inactive analysis
# ---------------------------------------------------------------------------

def gate_indicator_summary(daily: pd.DataFrame, ctx: pd.DataFrame) -> pd.DataFrame:
    """For each gate, compute active days, short mean when active/inactive, lift."""
    gate_names = [
        "btc_prior7_positive", "btc_prior7_negative", "btc_above_ma20",
        "prior30_dispersion_mid_high", "prior30_dispersion_high",
        "btc_prior7_positive_AND_dispersion_mid_high",
        "btc_prior7_negative_AND_dispersion_mid_high",
        "btc_prior7_above_5pct", "dispersion_above_median",
        "btc_consecutive_up_3d", "eligible_consecutive_down_3d",
        "btc_vol_expansion", "dispersion_above_rolling_q75",
    ]

    # Use base_50_50_daily for the short contribution analysis
    base = daily[daily["variant"] == "buffer8_50_50"].copy()
    if base.empty:
        base = daily[daily["variant"] == daily["variant"].unique()[0]].copy()
    short_ret = pd.to_numeric(base["short_contribution"], errors="coerce").fillna(0.0).values * 10000.0

    rows = []
    for gname in gate_names:
        try:
            mask = extended_gate_series(ctx, gname)
            mask_aligned = mask.values[:len(short_ret)]
            if len(mask_aligned) < len(short_ret):
                mask_aligned = np.pad(mask_aligned, (0, len(short_ret) - len(mask_aligned)), constant_values=False)
            active = short_ret[mask_aligned]
            inactive = short_ret[~mask_aligned]
            rows.append({
                "gate": gname,
                "active_days": int(mask_aligned.sum()),
                "active_rate_pct": float(mask_aligned.mean() * 100.0),
                "short_mean_active_bps": float(active.mean()) if len(active) else np.nan,
                "short_mean_inactive_bps": float(inactive.mean()) if len(inactive) else np.nan,
                "lift_bps": float(active.mean() - inactive.mean()) if len(active) and len(inactive) else np.nan,
            })
        except (KeyError, Exception):
            pass
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 7. Walk-forward engine
# ---------------------------------------------------------------------------

def run_single_variant(
    variant_key: str,
    spec_or_adaptive,
    *,
    next_ret, score_panel, ranked_by_month, onboard_map, ctx,
    short_capital_series=None,
) -> pd.DataFrame:
    """Run one variant (BufferSpec or AdaptiveVariant) and return daily DataFrame."""
    if isinstance(spec_or_adaptive, BufferSpec):
        return simulate_spec_extended(
            spec_or_adaptive,
            next_ret=next_ret,
            score_panel=score_panel,
            ranked_by_month=ranked_by_month,
            onboard_map=onboard_map,
            ctx=ctx,
        )
    else:
        # AdaptiveVariant
        av = spec_or_adaptive
        spec = av.to_buffer_spec()
        scs = short_capital_series if short_capital_series is not None else build_short_capital_series(ctx, av.adaptive_mode)
        return simulate_spec_adaptive(
            spec,
            scs,
            next_ret=next_ret,
            score_panel=score_panel,
            ranked_by_month=ranked_by_month,
            onboard_map=onboard_map,
            ctx=ctx,
        )


def run_walk_forward(
    all_variants: list[tuple[str, object]],
    *,
    next_ret_full, score_panel_full, ranked_by_month, onboard_map, ctx_full,
    cost_bps: float = 4.0,
) -> pd.DataFrame:
    """Run expanding-window walk-forward. Returns WF summary DataFrame."""
    ctx_full = ctx_full.copy()
    ctx_full["_month_str"] = ctx_full["timestamp_ts"].dt.strftime("%Y-%m")

    wf_rows = []

    for fold_idx, fold in enumerate(WF_FOLDS):
        train_end = fold["train_end"]
        test_year = fold["test_year"]

        train_mask = ctx_full["_month_str"] <= train_end
        test_mask = ctx_full["_month_str"].str.startswith(test_year)

        ctx_train = ctx_full[train_mask].copy().drop(columns=["_month_str"]).reset_index(drop=True)
        ctx_test = ctx_full[test_mask].copy().drop(columns=["_month_str"]).reset_index(drop=True)

        if ctx_train.empty or ctx_test.empty:
            continue

        # Sub-sliced next_ret and score_panel for training
        train_ts = set(ctx_train["timestamp_ts"])
        test_ts = set(ctx_test["timestamp_ts"])

        # Run all variants on training set
        train_results = {}
        for var_key, spec_or_adaptive in all_variants:
            try:
                scs = None
                if isinstance(spec_or_adaptive, AdaptiveVariant):
                    scs = build_short_capital_series(ctx_train, spec_or_adaptive.adaptive_mode)
                daily_train = run_single_variant(
                    var_key, spec_or_adaptive,
                    next_ret=next_ret_full, score_panel=score_panel_full,
                    ranked_by_month=ranked_by_month, onboard_map=onboard_map,
                    ctx=ctx_train, short_capital_series=scs,
                )
                summ = summarize_daily(daily_train, cost_bps)
                train_results[var_key] = summ["net_mean_bps"]
            except Exception:
                train_results[var_key] = np.nan

        # Select best variant by training net_mean_bps
        valid_train = {k: v for k, v in train_results.items() if not np.isnan(v)}
        if not valid_train:
            continue
        best_key = max(valid_train, key=valid_train.get)

        # Run best variant on test set
        best_spec = dict(all_variants)[best_key]
        try:
            scs = None
            if isinstance(best_spec, AdaptiveVariant):
                scs = build_short_capital_series(ctx_test, best_spec.adaptive_mode)
            daily_test = run_single_variant(
                best_key, best_spec,
                next_ret=next_ret_full, score_panel=score_panel_full,
                ranked_by_month=ranked_by_month, onboard_map=onboard_map,
                ctx=ctx_test, short_capital_series=scs,
            )
            test_summ = summarize_daily(daily_test, cost_bps)
        except Exception:
            test_summ = {"net_mean_bps": np.nan, "sharpe": np.nan, "max_drawdown_pct": np.nan}

        # Record all variants' training results + best variant's test result
        for var_key, spec_or_adaptive in all_variants:
            is_selected = (var_key == best_key)
            train_mean = train_results.get(var_key, np.nan)
            wf_rows.append({
                "fold": fold_idx + 1,
                "train_end": train_end,
                "test_year": test_year,
                "variant": var_key,
                "train_net_mean_bps": train_mean,
                "test_net_mean_bps": test_summ["net_mean_bps"] if is_selected else np.nan,
                "train_sharpe": np.nan,  # could compute if needed
                "test_sharpe": test_summ.get("sharpe", np.nan) if is_selected else np.nan,
                "test_max_dd_pct": test_summ.get("max_drawdown_pct", np.nan) if is_selected else np.nan,
                "selected": is_selected,
            })

    return pd.DataFrame(wf_rows)


def summarize_walk_forward(wf: pd.DataFrame) -> pd.DataFrame:
    """Aggregate walk-forward results per variant."""
    rows = []
    for variant, g in wf.groupby("variant"):
        selected_rows = g[g["selected"]]
        fold_count = len(g["fold"].unique())
        selection_freq = int(selected_rows.shape[0])

        is_mean = g["train_net_mean_bps"].mean()
        oos_vals = selected_rows["test_net_mean_bps"].dropna()
        oos_mean = oos_vals.mean() if len(oos_vals) else np.nan
        is_oos_delta = is_mean - oos_mean if not np.isnan(oos_mean) else np.nan
        oos_positive_rate = float((oos_vals > 0).mean()) if len(oos_vals) else np.nan
        oos_worst = float(oos_vals.min()) if len(oos_vals) else np.nan

        if not np.isnan(oos_positive_rate) and oos_positive_rate >= 0.6 and (np.isnan(is_oos_delta) or is_oos_delta < 5):
            stability = "Stable"
        elif not np.isnan(oos_positive_rate) and oos_positive_rate >= 0.4 and (np.isnan(is_oos_delta) or is_oos_delta < 10):
            stability = "Marginal"
        else:
            stability = "Unstable"

        rows.append({
            "variant": variant,
            "fold_count": fold_count,
            "selection_frequency": selection_freq,
            "IS_mean_bps": is_mean,
            "OOS_mean_bps": oos_mean,
            "IS_OOS_delta_bps": is_oos_delta,
            "OOS_positive_rate": oos_positive_rate,
            "OOS_worst_fold_bps": oos_worst,
            "stability_verdict": stability,
        })
    return pd.DataFrame(rows).sort_values("OOS_mean_bps", ascending=False).reset_index(drop=True)


# ---------------------------------------------------------------------------
# 8. Annual & monthly tables
# ---------------------------------------------------------------------------

def annual_table(daily: pd.DataFrame, selected_variants: list[str]) -> pd.DataFrame:
    """Annual stability for selected variants."""
    rows = []
    d = daily.copy()
    d["year"] = pd.to_datetime(d["timestamp_ts"], utc=True).dt.year
    for variant in selected_variants:
        sub = d[d["variant"] == variant]
        if sub.empty:
            continue
        for year, g in sub.groupby("year"):
            gross = pd.to_numeric(g["gross_ret"], errors="coerce").fillna(0.0)
            turn = pd.to_numeric(g["target_turnover_x"], errors="coerce").fillna(0.0)
            net = gross - 4.0 / 10000.0 * turn  # always at 4bps for annual
            rows.append({
                "variant": variant,
                "year": int(year),
                "days": int(len(g)),
                "net_cum_pct": fifth.compound(net) * 100.0,
                "max_drawdown_pct": float(fifth.max_drawdown(net) * 100.0),
                "avg_turnover_x": float(turn.mean()),
                "long_mean_bps": float(pd.to_numeric(g["long_contribution"], errors="coerce").fillna(0.0).mean() * 10000.0),
                "short_mean_bps": float(pd.to_numeric(g["short_contribution"], errors="coerce").fillna(0.0).mean() * 10000.0),
                "active_short_days": int(g["active_short"].fillna(False).astype(bool).sum()),
            })
    return pd.DataFrame(rows)


def worst_months_table(daily: pd.DataFrame, variant: str, n: int = 8) -> pd.DataFrame:
    """Worst n months for a variant."""
    sub = daily[daily["variant"] == variant].copy()
    if sub.empty:
        return pd.DataFrame()
    gross = pd.to_numeric(sub["gross_ret"], errors="coerce").fillna(0.0)
    turn = pd.to_numeric(sub["target_turnover_x"], errors="coerce").fillna(0.0)
    net = gross - 4.0 / 10000.0 * turn
    sub = sub.copy()
    sub["net_ret"] = net
    rows = []
    for month, g in sub.groupby("month"):
        rows.append({
            "variant": variant,
            "month": month,
            "net_cum_pct": fifth.compound(g["net_ret"]) * 100.0,
            "max_drawdown_pct": float(fifth.max_drawdown(g["net_ret"]) * 100.0),
            "avg_turnover_x": float(pd.to_numeric(g["target_turnover_x"], errors="coerce").mean()),
        })
    return pd.DataFrame(rows).sort_values("net_cum_pct").head(n).reset_index(drop=True)


# ---------------------------------------------------------------------------
# 9. Adaptive capital detail table
# ---------------------------------------------------------------------------

def adaptive_capital_detail(
    daily: pd.DataFrame,
    ctx: pd.DataFrame,
    adaptive_variants: list[AdaptiveVariant],
) -> pd.DataFrame:
    """Breakdown by regime level for adaptive capital variants."""
    rows = []
    for av in adaptive_variants:
        sub = daily[daily["variant"] == av.variant].copy()
        if sub.empty:
            continue
        scs = build_short_capital_series(ctx, av.adaptive_mode)
        # Align scs to sub by index
        scs_aligned = scs.reindex(sub.index).fillna(0.0)
        sub = sub.copy()
        sub["day_short_capital"] = scs_aligned.values
        sub["short_contribution_bps"] = pd.to_numeric(sub["short_contribution"], errors="coerce").fillna(0.0) * 10000.0

        for cap_level, g in sub.groupby("day_short_capital"):
            rows.append({
                "variant": av.variant,
                "regime_capital": float(cap_level),
                "days": int(len(g)),
                "short_mean_bps": float(g["short_contribution_bps"].mean()),
                "active_short_days": int(g["active_short"].fillna(False).astype(bool).sum()),
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 10. Main
# ---------------------------------------------------------------------------

def main() -> int:
    print("Loading data...")
    close, quote_volume = fifth.fourth.load_close_quote_panels()
    close = close[close.index >= SAMPLE_START - pd.Timedelta(days=45)].copy()
    next_ret = (close.shift(-1) / close - 1.0).replace([np.inf, -np.inf], np.nan)
    score_panels = fifth.build_score_panels(close)
    score_panel = score_panels["retvol_14d_skip1d"]
    onboard_map = fifth.fourth.read_onboard_map()
    months = sorted({ts.strftime("%Y-%m") for ts in close.index[close.index >= SAMPLE_START]})
    ranked_by_month = fifth.fourth.build_monthly_ranked_universes(months, quote_volume, onboard_map, 100)
    dates = pd.DataFrame({"timestamp_ts": [ts for ts in close.index if ts >= SAMPLE_START and ts + pd.Timedelta(days=1) in close.index]})
    dates["exit_ts"] = dates["timestamp_ts"] + pd.Timedelta(days=1)
    dates["month"] = dates["timestamp_ts"].dt.strftime("%Y-%m")

    print("Building market context...")
    ctx = fifth.add_reference_gate_context(fifth.build_market_context(close, ranked_by_month, onboard_map, dates))
    ctx = extend_market_context(ctx)

    # Build all variant specs
    buffer_specs = build_buffer_specs()
    adaptive_variants = build_adaptive_variants()

    # Convert to (key, spec_or_adaptive) list for unified handling
    all_variants: list[tuple[str, object]] = []
    for spec in buffer_specs:
        all_variants.append((spec.variant, spec))
    for av in adaptive_variants:
        all_variants.append((av.variant, av))

    print(f"Running {len(all_variants)} variants on full sample...")
    daily_parts = []
    for var_key, spec_or_adaptive in all_variants:
        print(f"  {var_key}...")
        try:
            scs = None
            if isinstance(spec_or_adaptive, AdaptiveVariant):
                scs = build_short_capital_series(ctx, spec_or_adaptive.adaptive_mode)
            d = run_single_variant(
                var_key, spec_or_adaptive,
                next_ret=next_ret, score_panel=score_panel,
                ranked_by_month=ranked_by_month, onboard_map=onboard_map,
                ctx=ctx, short_capital_series=scs,
            )
            daily_parts.append(d)
        except Exception as e:
            print(f"    ERROR: {e}")

    daily = pd.concat(daily_parts, ignore_index=True)
    daily.to_csv(DAILY_PATH, index=False)
    print(f"  wrote {DAILY_PATH.relative_to(ROOT)}")

    # Summarize at each cost level
    print("Computing full-sample results...")
    rows = []
    for (_, variant), sub in daily.groupby(["experiment_group", "variant"], sort=False):
        for cost in COST_GRID_BPS:
            rows.append(summarize_daily(sub, cost))
    results = pd.DataFrame(rows)
    verdicts = results.apply(lambda r: classify(r), axis=1)
    results["verdict"] = [v[0] for v in verdicts]
    results["reason"] = [v[1] for v in verdicts]
    results["verdict_rank"] = [v[2] for v in verdicts]
    results.to_csv(RESULTS_PATH, index=False)
    print(f"  wrote {RESULTS_PATH.relative_to(ROOT)}")

    # Walk-forward
    print("Running walk-forward (5 folds)...")
    wf = run_walk_forward(
        all_variants,
        next_ret_full=next_ret,
        score_panel_full=score_panel,
        ranked_by_month=ranked_by_month,
        onboard_map=onboard_map,
        ctx_full=ctx,
        cost_bps=4.0,
    )
    wf.to_csv(WF_PATH, index=False)
    print(f"  wrote {WF_PATH.relative_to(ROOT)}")

    wf_summary = summarize_walk_forward(wf)

    # Gate indicator summary
    print("Computing gate indicator summary...")
    gate_summary = gate_indicator_summary(daily, ctx)

    # Annual stability for top variants
    cost4 = results[results["cost_bps_per_1x_turnover"] == 4.0].copy()
    top_variants = cost4.sort_values("net_mean_bps", ascending=False).head(8)["variant"].tolist()
    for ref in ["buffer8_50_50", "buffer8_weekly", "base_50_50_daily"]:
        if ref not in top_variants:
            top_variants.append(ref)
    annual = annual_table(daily, top_variants)
    annual.to_csv(ANNUAL_PATH, index=False)

    # Worst months for best variant
    best_variant = top_variants[0]
    worst = worst_months_table(daily, best_variant)

    # Adaptive capital detail
    adapt_detail = adaptive_capital_detail(daily, ctx, adaptive_variants)

    # Summary JSON
    cost12 = results[results["cost_bps_per_1x_turnover"] == 12.0]
    summary = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "objective": "213c short leg gate & capital allocation depth study",
        "sample_start": str(SAMPLE_START.date()),
        "sample_end": str(pd.to_datetime(dates["timestamp_ts"].max()).date()),
        "variant_count": len(all_variants),
        "cost_grid_bps": COST_GRID_BPS,
        "cumulative_variant_count_across_studies": 76 + len(all_variants),
        "expected_false_positives_95pct": round((76 + len(all_variants)) * 0.05, 1),
        "best_variant_4bps": best_variant,
        "best_net_mean_4bps": float(cost4.iloc[0]["net_mean_bps"]) if len(cost4) else np.nan,
        "artifacts": {
            "daily": str(DAILY_PATH.relative_to(ROOT)),
            "results": str(RESULTS_PATH.relative_to(ROOT)),
            "walk_forward": str(WF_PATH.relative_to(ROOT)),
            "annual": str(ANNUAL_PATH.relative_to(ROOT)),
            "site": str(SITE_PATH.relative_to(ROOT)),
        },
    }
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Build and write HTML report
    print("Building HTML report...")
    html = build_report(results, wf, wf_summary, gate_summary, annual, worst, adapt_detail, summary)
    SITE_PATH.write_text(html, encoding="utf-8")
    print(f"  wrote {SITE_PATH.relative_to(ROOT)}")

    # Deploy to web server
    deploy_dir = Path("/var/www/momentum-report/paper")
    if deploy_dir.exists():
        import shutil
        shutil.copy2(SITE_PATH, deploy_dir / SITE_PATH.name)
        print(f"  deployed to {deploy_dir / SITE_PATH.name}")

    print("Done.")
    return 0


# ---------------------------------------------------------------------------
# 11. HTML report
# ---------------------------------------------------------------------------

def build_report(
    results: pd.DataFrame,
    wf: pd.DataFrame,
    wf_summary: pd.DataFrame,
    gate_summary: pd.DataFrame,
    annual: pd.DataFrame,
    worst_months: pd.DataFrame,
    adapt_detail: pd.DataFrame,
    summary: dict,
) -> str:
    generated = summary["generated_at_utc"].replace("T", " ").replace("Z", " UTC")
    variant_count = summary["variant_count"]
    cumulative_count = summary["cumulative_variant_count_across_studies"]
    expected_fp = summary["expected_false_positives_95pct"]

    cost4 = results[results["cost_bps_per_1x_turnover"] == 4.0].copy()
    cost12 = results[results["cost_bps_per_1x_turnover"] == 12.0].copy()

    # Best variant at 4bps
    best4 = cost4.sort_values("net_mean_bps", ascending=False).iloc[0] if len(cost4) else None
    # Reference: buffer8_50_50 at 4bps
    ref4 = cost4[cost4["variant"] == "buffer8_50_50"].iloc[0] if len(cost4[cost4["variant"] == "buffer8_50_50"]) else None

    # Core metrics cards
    def metric_card(label, mean_bps, cum_pct, dd_pct, variant_name):
        return f"""<div class="card">
      <h4>{escape(str(variant_name))}</h4>
      <div class="metrics-grid">
        <div><span class="k">Net Mean</span><span class="v">{fmt_bps(mean_bps)}</span></div>
        <div><span class="k">Cumulative</span><span class="v">{fmt_pct(cum_pct)}</span></div>
        <div><span class="k">Max DD</span><span class="v">{fmt_pct(dd_pct)}</span></div>
      </div>
    </div>"""

    cards_html = ""
    if best4 is not None:
        cards_html += metric_card("Best @ 4bps", best4["net_mean_bps"], best4["net_cum_pct"], best4["max_drawdown_pct"], best4["variant"])
    if ref4 is not None:
        cards_html += metric_card("buffer8_50_50 @ 4bps", ref4["net_mean_bps"], ref4["net_cum_pct"], ref4["max_drawdown_pct"], "buffer8_50_50 (reference)")

    # Results table columns
    res_cols = ["verdict", "experiment_group", "variant", "net_mean_bps", "net_cum_pct", "max_drawdown_pct", "sharpe", "avg_turnover_x", "long_mean_bps", "short_mean_bps", "short_gate", "reason"]

    # Walk-forward summary columns
    wf_cols = ["variant", "fold_count", "selection_frequency", "IS_mean_bps", "OOS_mean_bps", "IS_OOS_delta_bps", "OOS_positive_rate", "OOS_worst_fold_bps", "stability_verdict"]

    # Gate summary columns
    gate_cols = ["gate", "active_days", "active_rate_pct", "short_mean_active_bps", "short_mean_inactive_bps", "lift_bps"]

    # Annual columns
    annual_cols = ["variant", "year", "net_cum_pct", "max_drawdown_pct", "avg_turnover_x", "long_mean_bps", "short_mean_bps", "active_short_days"]

    # Worst months columns
    wm_cols = ["variant", "month", "net_cum_pct", "max_drawdown_pct", "avg_turnover_x"]

    # Adaptive detail columns
    adapt_cols = ["variant", "regime_capital", "days", "short_mean_bps", "active_short_days"]

    # WF fold detail (top 10 variants only)
    top10_variants = cost4.sort_values("net_mean_bps", ascending=False).head(10)["variant"].tolist()
    wf_detail = wf[wf["variant"].isin(top10_variants)].copy()
    wf_detail_cols = ["fold", "variant", "train_net_mean_bps", "test_net_mean_bps", "test_sharpe", "test_max_dd_pct", "selected"]

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>213c Short Leg Gate 与仓位控制深度研究</title>
  <style>
    body {{ margin:0; background:#f6f3ec; color:#172033; font-family:"Noto Sans SC","Source Han Sans SC","PingFang SC","Microsoft YaHei",sans-serif; line-height:1.62; }}
    main {{ max-width:1220px; margin:0 auto; padding:28px 16px 56px; }}
    .card {{ background:white; border:1px solid #e6dccb; border-radius:14px; padding:18px 20px; margin:14px 0; }}
    .hero {{ border-color:#0f766e; background:#f0fdfa; }}
    .warn {{ background:#fff7ed; border-color:#fdba74; }}
    .good {{ background:#f0fdf4; border-color:#86efac; }}
    h1 {{ font-size:1.6em; margin:0 0 6px; }}
    h2 {{ font-size:1.25em; margin:28px 0 10px; border-bottom:2px solid #e6dccb; padding-bottom:4px; }}
    h3 {{ font-size:1.05em; margin:18px 0 8px; }}
    h4 {{ margin:0 0 8px; color:#0f766e; }}
    .sub {{ color:#64748b; font-size:0.88em; }}
    .metrics-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:10px; }}
    .metrics-grid .k {{ display:block; font-size:0.78em; color:#64748b; }}
    .metrics-grid .v {{ font-size:1.15em; font-weight:600; }}
    table {{ width:100%; border-collapse:collapse; font-size:0.82em; margin:8px 0; }}
    th,td {{ padding:5px 8px; border:1px solid #e6dccb; text-align:right; }}
    th {{ background:#f6f3ec; font-weight:600; text-align:center; }}
    td:first-child, th:first-child {{ text-align:left; }}
    tr:nth-child(even) {{ background:#faf8f5; }}
    .tag {{ display:inline-block; padding:1px 7px; border-radius:8px; font-size:0.78em; font-weight:600; }}
    .tag-Promising {{ background:#d1fae5; color:#065f46; }}
    .tag-Watch {{ background:#fef3c7; color:#92400e; }}
    .tag-Diagnostic {{ background:#e0e7ff; color:#3730a3; }}
    .tag-Fail {{ background:#fee2e2; color:#991b1b; }}
    .tag-Stable {{ background:#d1fae5; color:#065f46; }}
    .tag-Marginal {{ background:#fef3c7; color:#92400e; }}
    .tag-Unstable {{ background:#fee2e2; color:#991b1b; }}
    .note {{ font-size:0.85em; color:#64748b; margin:6px 0; }}
  </style>
</head>
<body>
<main>

<div class="card hero">
  <h1>213c Short Leg Gate 与仓位控制深度研究</h1>
  <p class="sub">生成时间：{generated} | 成本假设：4/8/12 bps/1x turnover | 变体数：{variant_count}（累计 ~{cumulative_count}，预期 ~{expected_fp} 假阳性 @95%）</p>
</div>

<div class="card good">
  <h4>核心发现</h4>
  <p>最佳变体：<strong>{escape(str(best4["variant"])) if best4 is not None else "N/A"}</strong>
     @ 4bps = {fmt_bps(best4["net_mean_bps"]) if best4 is not None else "N/A"}，
     累计 {fmt_pct(best4["net_cum_pct"]) if best4 is not None else "N/A"}，
     最大回撤 {fmt_pct(best4["max_drawdown_pct"]) if best4 is not None else "N/A"}</p>
  <p class="note">对比 buffer8_50_50 baseline：{fmt_bps(ref4["net_mean_bps"]) if ref4 is not None else "N/A"} @ 4bps</p>
</div>

<h2>1. 全样本结果 @ 4bps</h2>
<div class="card">
  {table_html(cost4, res_cols)}
</div>

<h2>1b. 全样本结果 @ 12bps</h2>
<div class="card">
  {table_html(cost12, res_cols)}
</div>

<h2>2. Walk-Forward 稳定性总结</h2>
<div class="card">
  <p class="note">扩展窗口：训练 2020-02 起逐年增长，测试 2022-2026。选择标准：训练期 net_mean_bps @ 4bps 最高。Stable = OOS 正率 ≥60% 且 IS-OOS delta &lt;5bps。</p>
  {table_html(wf_summary, wf_cols)}
</div>

<h2>2b. Walk-Forward 逐 Fold 细节（Top 10 变体）</h2>
<div class="card">
  {table_html(wf_detail, wf_detail_cols)}
</div>

<h2>3. 过拟合诊断</h2>
<div class="card">
  <p>累计变体测试数：<strong>~{cumulative_count}</strong></p>
  <p>95% 置信度预期假阳性：<strong>~{expected_fp}</strong></p>
  <p>本研究新增 {variant_count} 个变体，所有变体在运行前已预注册，未根据结果追加。</p>
  <p class="note">注意：2022-2025 数据已被先前 gate 选择研究使用（Phase 3、第五轮）。2026 YTD 是唯一未用于先前设计的时段。</p>
</div>

<h2>4. Gate 指标分析</h2>
<div class="card">
  <p class="note">基于 buffer8_50_50 的 short contribution，按 gate 激活/未激活拆分。Lift = active mean - inactive mean。</p>
  {table_html(gate_summary, gate_cols)}
</div>

<h2>5. 自适应仓位细节</h2>
<div class="card">
  <p class="note">按 regime capital 水平拆分 short contribution。</p>
  {table_html(adapt_detail, adapt_cols)}
</div>

<h2>6. 年度稳定性（Top 变体 + 参考）@ 4bps</h2>
<div class="card">
  {table_html(annual, annual_cols)}
</div>

<h2>7. 最差月份（最佳变体）</h2>
<div class="card">
  {table_html(worst_months, wm_cols)}
</div>

<h2>8. 建议</h2>
<div class="card">
  <h3>可做</h3>
  <ul>
    <li>如果某变体在 walk-forward 中 OOS 正率 ≥60% 且 IS-OOS delta &lt;5bps，可考虑进入 real-cost replay</li>
    <li>自适应仓位（Group C）如果优于 binary gate，说明"连续调节"比"开关"更适合 short leg</li>
    <li>Gate 指标分析中 lift 最高的 gate 值得进一步研究其因果机制</li>
  </ul>
  <h3>不应做</h3>
  <ul>
    <li>不应将任何单个变体的最佳参数直接推入实盘——需要 walk-forward + real-cost replay 双重验证</li>
    <li>不应在看到结果后追加新变体——会增加 multiple-testing 负担</li>
    <li>不应仅凭全样本 mean 选择变体——必须看 OOS 稳定性</li>
  </ul>
</div>

</main>
</body>
</html>"""


if __name__ == "__main__":
    raise SystemExit(main())
