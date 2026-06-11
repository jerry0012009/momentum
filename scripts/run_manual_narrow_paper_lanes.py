#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SCRIPTS_DIR = ROOT / "scripts"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import build_volume_supportflip_higherlow_first_verdict as rank2_mod  # noqa: E402
import build_rank32_ema_slope_clean_replication as rank32_base_mod  # noqa: E402
from momentum.analytics.multi_tf_momentum_backtest import (  # noqa: E402
    MultiTfMomentumBacktestConfig,
    evaluate_multi_tf_momentum_reversal,
)
from momentum.signals.pullback_recovery_confirmation import (  # noqa: E402
    PullbackRecoveryConfirmationConfig,
    compute_pullback_recovery_confirmation_signals,
)
from momentum.signals.trendline_breakout_navigator import (  # noqa: E402
    TrendlineBreakoutNavigatorConfig,
    compute_trendline_breakout_navigator,
)

ART_DIR = ROOT / "reports" / "artifacts" / "manual_narrow_paper_lanes"
LEDGER_PATH = ART_DIR / "manual_narrow_paper_closed_trades.csv"
STATUS_PATH = ART_DIR / "manual_narrow_paper_status.csv"
OPEN_POSITIONS_PATH = ART_DIR / "manual_narrow_paper_open_positions.csv"
STATE_PATH = ART_DIR / "manual_narrow_paper_state.json"
RUN_SUMMARY_PATH = ART_DIR / "manual_narrow_paper_last_run_summary.json"
RANK29_SHADOW_TRADE_VIEW_PATH = ART_DIR / "rank29_shadow_trade_view.csv"
RANK29_GATE_THRESHOLD_PATH = ROOT / "reports" / "artifacts" / "rank29_regime_gate_backtest" / "thresholds.json"
RANK29_SHADOW_BAD_WEIGHT = 0.25
DEFAULT_RANK29_GATE_THRESHOLDS = {
    "trend_low_q33": 0.10078188159206895,
    "noise_high_q67": 0.8197288074726972,
}

ASSET_TO_BINANCE = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}

RANK29_EXEC_NOTIONAL_USD = 500.0
RANK29_TAKER_FEE_BPS = 4.5
RANK29_EXEC_DEPTH_LIMIT = 100
RANK29_EXEC_VENUE_MODE = "paper_binance_futures_orderbook_proxy"
RANK29_EXEC_SOURCE = "binance_futures_500u_depth"
RANK29_EXEC_FRICTION_MODEL = "500u_live_depth_proxy_plus_4p5bps_taker"
RANK29_SIGNAL_PREFIXES = ["tbn_short", "tbn_medium", "tbn_long"]
RANK29_DEFAULT_HOLD_BARS = 8
RANK29_CAUSAL_REPLAY_CONTEXT_BARS = 960


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_z(ts) -> str:
    return pd.to_datetime(ts, utc=True).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_csv_or_empty(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {}
    return json.loads(STATE_PATH.read_text())


def save_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True))


def load_rank29_gate_thresholds() -> dict[str, float]:
    if RANK29_GATE_THRESHOLD_PATH.exists():
        data = json.loads(RANK29_GATE_THRESHOLD_PATH.read_text())
        return {
            "trend_low_q33": float(data.get("trend_low_q33", DEFAULT_RANK29_GATE_THRESHOLDS["trend_low_q33"])),
            "noise_high_q67": float(data.get("noise_high_q67", DEFAULT_RANK29_GATE_THRESHOLDS["noise_high_q67"])),
        }
    return DEFAULT_RANK29_GATE_THRESHOLDS.copy()


def compute_rank29_gate_daily_flags(bars_cache: dict[str, pd.DataFrame], thresholds: dict[str, float]) -> pd.DataFrame:
    daily_frames: list[pd.DataFrame] = []
    for asset, raw_bars in bars_cache.items():
        daily = (
            raw_bars.set_index("timestamp")
            .resample("1D")
            .agg(open=("open", "first"), high=("high", "max"), low=("low", "min"), close=("close", "last"), volume=("volume", "sum"))
            .dropna()
            .reset_index()
        )
        daily["asset"] = asset
        daily["ret_1d"] = daily["close"].pct_change()
        daily["trend_strength_20d"] = daily["close"].pct_change(20).abs()
        abs_20d_move = daily["close"].pct_change(20).abs()
        abs_sum_20 = daily["ret_1d"].abs().rolling(20).sum()
        daily["noise_ratio_20d"] = 1.0 - (abs_20d_move / abs_sum_20.where(abs_sum_20 != 0))
        daily_frames.append(daily[["timestamp", "asset", "trend_strength_20d", "noise_ratio_20d"]])

    if not daily_frames:
        return pd.DataFrame(
            columns=[
                "timestamp",
                "month",
                "gate_trend_strength_20d_mean_day",
                "gate_noise_ratio_20d_mean_day",
                "gate_trend_strength_20d_mtd_mean",
                "gate_noise_ratio_20d_mtd_mean",
                "gate_low_trend_high_noise",
                "effective_for_trade_day",
            ]
        )

    daily_all = pd.concat(daily_frames, ignore_index=True)
    gate_daily = (
        daily_all.groupby("timestamp", as_index=False)
        .agg(
            gate_trend_strength_20d_mean_day=("trend_strength_20d", "mean"),
            gate_noise_ratio_20d_mean_day=("noise_ratio_20d", "mean"),
        )
        .sort_values("timestamp")
        .reset_index(drop=True)
    )
    gate_daily["month"] = gate_daily["timestamp"].dt.strftime("%Y-%m")
    gate_daily["gate_trend_strength_20d_mtd_mean"] = (
        gate_daily.groupby("month")["gate_trend_strength_20d_mean_day"].expanding().mean().reset_index(level=0, drop=True)
    )
    gate_daily["gate_noise_ratio_20d_mtd_mean"] = (
        gate_daily.groupby("month")["gate_noise_ratio_20d_mean_day"].expanding().mean().reset_index(level=0, drop=True)
    )
    gate_daily["gate_low_trend_high_noise"] = (
        (gate_daily["gate_trend_strength_20d_mtd_mean"] <= float(thresholds["trend_low_q33"]))
        & (gate_daily["gate_noise_ratio_20d_mtd_mean"] >= float(thresholds["noise_high_q67"]))
    ).fillna(False).astype(int)
    gate_daily["effective_for_trade_day"] = gate_daily["timestamp"] + pd.Timedelta(days=1)
    return gate_daily


def download_binance_bars(symbol: str, *, interval: str = "15m", days: int = 150) -> pd.DataFrame:
    end_ms = int(pd.Timestamp.now("UTC").timestamp() * 1000)
    start_ms = end_ms - days * 24 * 60 * 60 * 1000
    url = "https://api.binance.com/api/v3/klines"
    rows: list[list] = []
    current = start_ms

    while current < end_ms:
        qs = urlencode(
            {
                "symbol": symbol,
                "interval": interval,
                "startTime": current,
                "endTime": end_ms,
                "limit": 1000,
            }
        )
        with urlopen(f"{url}?{qs}", timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if not data:
            break
        rows.extend(data)
        last_close_time = int(data[-1][6])
        current = last_close_time + 1
        if len(data) < 1000:
            break

    if not rows:
        raise ValueError(f"No Binance data for {symbol}")

    df = pd.DataFrame(
        rows,
        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "number_of_trades",
            "taker_buy_base_asset_volume",
            "taker_buy_quote_asset_volume",
            "ignore",
        ],
    )
    out = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(df["open_time"], unit="ms", utc=True),
            "close_ts": pd.to_datetime(df["close_time"], unit="ms", utc=True),
            "open": pd.to_numeric(df["open"], errors="coerce"),
            "high": pd.to_numeric(df["high"], errors="coerce"),
            "low": pd.to_numeric(df["low"], errors="coerce"),
            "close": pd.to_numeric(df["close"], errors="coerce"),
            "volume": pd.to_numeric(df["volume"], errors="coerce"),
        }
    )
    out = out.dropna().sort_values("timestamp").reset_index(drop=True)
    now_ts = pd.Timestamp.now("UTC")
    out = out[out["close_ts"] < now_ts].copy()
    return out.reset_index(drop=True)


def download_binance_futures_depth(symbol: str, *, limit: int = RANK29_EXEC_DEPTH_LIMIT) -> dict:
    qs = urlencode({"symbol": symbol, "limit": limit})
    with urlopen(f"https://fapi.binance.com/fapi/v1/depth?{qs}", timeout=30) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    snapshot_ts = utc_now()
    bids = [(float(px), float(qty)) for px, qty in payload.get("bids", [])]
    asks = [(float(px), float(qty)) for px, qty in payload.get("asks", [])]
    if not bids or not asks:
        raise ValueError(f"Empty futures depth for {symbol}")
    best_bid = bids[0][0]
    best_ask = asks[0][0]
    mid = (best_bid + best_ask) / 2.0
    return {
        "symbol": symbol,
        "snapshot_ts_utc": iso_z(snapshot_ts),
        "best_bid": best_bid,
        "best_ask": best_ask,
        "mid": mid,
        "bids": bids,
        "asks": asks,
    }


def simulate_orderbook_slippage_bps(depth: dict, side: str, target_notional_usd: float) -> tuple[float, float]:
    target_notional_usd = max(float(target_notional_usd), 1.0)
    levels = depth["asks"] if side == "buy" else depth["bids"]
    remaining = target_notional_usd
    filled_qty = 0.0
    filled_notional = 0.0
    for price, qty in levels:
        level_notional = price * qty
        take_notional = min(remaining, level_notional)
        if take_notional <= 0:
            continue
        take_qty = take_notional / price
        filled_qty += take_qty
        filled_notional += take_notional
        remaining -= take_notional
        if remaining <= 1e-9:
            break
    if remaining > 1e-6 or filled_qty <= 0:
        raise ValueError(f"Insufficient depth for {depth['symbol']} side={side} target={target_notional_usd}")
    avg_px = filled_notional / filled_qty
    mid = float(depth["mid"])
    if side == "buy":
        slippage_bps = (avg_px / mid - 1.0) * 10000.0
    else:
        slippage_bps = (mid / avg_px - 1.0) * 10000.0
    return float(slippage_bps), float(avg_px)


def apply_rank29_live_execution_model(
    trades: pd.DataFrame,
    depth: dict,
    *,
    exposure_col: str | None = None,
    base_notional_usd: float = RANK29_EXEC_NOTIONAL_USD,
) -> pd.DataFrame:
    if trades.empty:
        return trades.copy()
    out = trades.copy()
    out["net_ret_legacy_6bps"] = out["net_ret"]
    out["gross_ret_legacy_bar"] = out["gross_ret"]
    out["execution_notional_usd"] = base_notional_usd
    out["entry_slippage_bps_500u"] = 0.0
    out["exit_slippage_bps_500u"] = 0.0
    out["entry_exec_price"] = out["entry_price"].astype(float)
    out["exit_exec_price"] = out["exit_price"].astype(float)
    out["book_snapshot_asof_utc"] = depth["snapshot_ts_utc"]
    out["execution_depth_mid"] = float(depth["mid"])
    out["fee_bps_per_side"] = RANK29_TAKER_FEE_BPS
    out["friction_model"] = RANK29_EXEC_FRICTION_MODEL
    fee_rate = RANK29_TAKER_FEE_BPS / 10000.0
    slip_cache: dict[tuple[str, float], tuple[float, float]] = {}

    def get_slippage(side: str, target_notional: float) -> tuple[float, float]:
        key = (side, round(float(target_notional), 6))
        if key not in slip_cache:
            slip_cache[key] = simulate_orderbook_slippage_bps(depth, side, target_notional)
        return slip_cache[key]

    gross_vals: list[float] = []
    net_vals: list[float] = []
    for idx, row in out.iterrows():
        exposure = 1.0
        if exposure_col and exposure_col in out.columns:
            exposure = float(row.get(exposure_col, 1.0) or 1.0)
        target_notional = max(base_notional_usd * exposure, 1.0)
        if str(row["direction"]) == "long":
            entry_slip_bps, _ = get_slippage("buy", target_notional)
            exit_slip_bps, _ = get_slippage("sell", target_notional)
            entry_exec = float(row["entry_price"]) * (1.0 + entry_slip_bps / 10000.0)
            exit_exec = float(row["exit_price"]) * (1.0 - exit_slip_bps / 10000.0)
            gross = exit_exec / entry_exec - 1.0
        else:
            entry_slip_bps, _ = get_slippage("sell", target_notional)
            exit_slip_bps, _ = get_slippage("buy", target_notional)
            entry_exec = float(row["entry_price"]) * (1.0 - entry_slip_bps / 10000.0)
            exit_exec = float(row["exit_price"]) * (1.0 + exit_slip_bps / 10000.0)
            gross = entry_exec / exit_exec - 1.0
        net = (1.0 + gross) * (1.0 - fee_rate) * (1.0 - fee_rate) - 1.0
        out.at[idx, "execution_notional_usd"] = target_notional
        out.at[idx, "entry_slippage_bps_500u"] = entry_slip_bps
        out.at[idx, "exit_slippage_bps_500u"] = exit_slip_bps
        out.at[idx, "entry_exec_price"] = entry_exec
        out.at[idx, "exit_exec_price"] = exit_exec
        gross_vals.append(float(gross))
        net_vals.append(float(net))
    out["gross_ret"] = gross_vals
    out["net_ret"] = net_vals
    return out


def build_rank2_prepared_bars(asset: str, raw_bars: pd.DataFrame) -> pd.DataFrame:
    bars = raw_bars.copy()
    bars["asset"] = asset
    bars["ema_fast"] = bars["close"].ewm(span=rank2_mod.EMA_FAST, adjust=False).mean()
    bars["ema_slow"] = bars["close"].ewm(span=rank2_mod.EMA_SLOW, adjust=False).mean()
    bars["long_bias"] = (bars["ema_fast"] > bars["ema_slow"]).astype(int)
    bars["short_bias"] = (bars["ema_fast"] < bars["ema_slow"]).astype(int)
    bars["donchian_upper"] = bars["high"].shift(1).rolling(rank2_mod.DONCHIAN_LOOKBACK, min_periods=rank2_mod.DONCHIAN_LOOKBACK).max()
    bars["donchian_lower"] = bars["low"].shift(1).rolling(rank2_mod.DONCHIAN_LOOKBACK, min_periods=rank2_mod.DONCHIAN_LOOKBACK).min()
    bars["atr"] = rank2_mod.compute_atr(bars, rank2_mod.ATR_PERIOD)
    bars["volume_median20"] = bars["volume"].rolling(rank2_mod.VOLUME_MEDIAN_LOOKBACK, min_periods=rank2_mod.VOLUME_MEDIAN_LOOKBACK).median()
    bars["threshold_upper"] = bars["donchian_upper"] + rank2_mod.TAU_ATR * bars["atr"]
    bars["threshold_lower"] = bars["donchian_lower"] - rank2_mod.TAU_ATR * bars["atr"]
    bars["raw_long_breakout"] = ((bars["long_bias"] == 1) & (bars["close"] > bars["threshold_upper"])).fillna(False)
    bars["raw_short_breakout"] = ((bars["short_bias"] == 1) & (bars["close"] < bars["threshold_lower"])).fillna(False)
    bars["raw_long_transition"] = (bars["raw_long_breakout"] & (~bars["raw_long_breakout"].shift(1).fillna(False))).astype(int)
    bars["raw_short_transition"] = (bars["raw_short_breakout"] & (~bars["raw_short_breakout"].shift(1).fillna(False))).astype(int)
    return bars


def compute_rank2_lane(asset: str, raw_bars: pd.DataFrame) -> tuple[pd.DataFrame, dict, dict | None]:
    prepared = build_rank2_prepared_bars(asset, raw_bars)
    symbol = ASSET_TO_BINANCE[asset]
    events = rank2_mod.build_event_frame(asset, symbol, prepared)
    variant_events = rank2_mod.filtered_events_for_variant(events, "combo_all")
    trades, _ = rank2_mod.simulate_variant_events(prepared, variant_events, "combo_all", cost_bps_per_side=6.0)
    if trades.empty:
        status = {
            "candidate_id": "rank2_combo_all",
            "candidate_rank": 2,
            "stage": "P3_narrow_paper_pilot",
            "asset": asset,
            "scope_tag": "narrow_paper_pilot_approved",
            "venue_mode": "paper_binance_spot",
            "signal_family": "volume_supportflip_higherlow_combo_all",
            "sample_end_utc": iso_z(prepared["timestamp"].iloc[-1]),
            "latest_closed_exit_ts_utc": None,
            "lifetime_total_return_6bps": 0.0,
            "new_trades_appended": 0,
            "open_position": "none",
            "open_entry_ts_utc": None,
            "open_side": None,
        }
        return pd.DataFrame(), status, None

    trades = trades.copy()
    for col in ["breakout_ts", "signal_ts", "entry_ts", "exit_ts"]:
        trades[col] = pd.to_datetime(trades[col], utc=True)
    trades["candidate_id"] = "rank2_combo_all"
    trades["candidate_rank"] = 2
    trades["stage"] = "P3_narrow_paper_pilot"
    trades["scope_tag"] = "narrow_paper_pilot_approved"
    trades["venue_mode"] = "paper_binance_spot"
    trades["signal_family"] = "volume_supportflip_higherlow_combo_all"
    trades["source"] = "binance_spot_15m"
    trades["complete_trade"] = ~((trades["exit_reason"] == "time_stop") & (trades["hold_bars"] < rank2_mod.TIME_STOP_BARS))

    closed = trades[trades["complete_trade"]].copy().reset_index(drop=True)
    open_trade = trades[~trades["complete_trade"]].copy().sort_values("entry_ts").tail(1)
    open_row = None if open_trade.empty else open_trade.iloc[0].to_dict()

    if not closed.empty:
        latest_closed = closed.iloc[-1]
        lifetime = float((1.0 + closed["net_ret"]).prod() - 1.0)
        latest_closed_ts = iso_z(latest_closed["exit_ts"])
    else:
        lifetime = 0.0
        latest_closed_ts = None

    status = {
        "candidate_id": "rank2_combo_all",
        "candidate_rank": 2,
        "stage": "P3_narrow_paper_pilot",
        "asset": asset,
        "scope_tag": "narrow_paper_pilot_approved",
        "venue_mode": "paper_binance_spot",
        "signal_family": "volume_supportflip_higherlow_combo_all",
        "sample_end_utc": iso_z(prepared["timestamp"].iloc[-1]),
        "latest_closed_exit_ts_utc": latest_closed_ts,
        "lifetime_total_return_6bps": lifetime,
        "new_trades_appended": 0,
        "open_position": "open" if open_row else "none",
        "open_entry_ts_utc": iso_z(open_row["entry_ts"]) if open_row else None,
        "open_side": open_row.get("side") if open_row else None,
    }
    return closed, status, open_row


def build_rank17_signals(bars: pd.DataFrame) -> pd.DataFrame:
    sig = compute_pullback_recovery_confirmation_signals(
        bars,
        config=PullbackRecoveryConfirmationConfig(
            window_5m=6,
            window_15m=6,
            threshold_5m=0.003,
            threshold_15m=0.006,
            resample_rule_15m="15min",
            vol_window=20,
            pullback_lookback=2,
            pullback_vol_z_max=0.0,
            vol_recover_th=1.0,
            breakout_lookback=1,
        ),
    )
    sig["timestamp"] = pd.to_datetime(sig["timestamp"], utc=True)
    return sig


def compute_rank17_lane(asset: str, raw_bars: pd.DataFrame) -> tuple[pd.DataFrame, dict, dict | None]:
    bars = raw_bars.copy()
    bars["symbol"] = asset
    sig = build_rank17_signals(bars)
    bt = evaluate_multi_tf_momentum_reversal(
        sig,
        config=MultiTfMomentumBacktestConfig(
            fee_bps_per_side=6.0,
            slippage_bps_per_side=0.0,
            flip_on_reverse_signal=True,
        ),
    )
    trades = bt.trades.copy()
    if trades.empty:
        status = {
            "candidate_id": "rank17_pullback_ethsol_narrow_pilot",
            "candidate_rank": 17,
            "stage": "P3_narrow_paper_pilot",
            "asset": asset,
            "scope_tag": "narrow_paper_pilot_eth_sol_only",
            "venue_mode": "paper_binance_spot",
            "signal_family": "pullback_recovery_confirmation",
            "sample_end_utc": iso_z(bars["timestamp"].iloc[-1]),
            "latest_closed_exit_ts_utc": None,
            "lifetime_total_return_6bps": 0.0,
            "new_trades_appended": 0,
            "open_position": "none",
            "open_entry_ts_utc": None,
            "open_side": None,
        }
        return pd.DataFrame(), status, None

    for col in ["signal_ts", "entry_ts", "exit_ts"]:
        trades[col] = pd.to_datetime(trades[col], utc=True)
    trades["asset"] = asset
    trades["variant"] = "pullback2_vol1.0_break1"
    trades["cost_bps_per_side"] = 6.0
    trades["candidate_id"] = "rank17_pullback_ethsol_narrow_pilot"
    trades["candidate_rank"] = 17
    trades["stage"] = "P3_narrow_paper_pilot"
    trades["scope_tag"] = "narrow_paper_pilot_eth_sol_only"
    trades["venue_mode"] = "paper_binance_spot"
    trades["signal_family"] = "pullback_recovery_confirmation"
    trades["source"] = "binance_spot_15m"
    trades["complete_trade"] = trades["exit_reason"] != "force_close_final_bar"

    closed = trades[trades["complete_trade"]].copy().reset_index(drop=True)
    open_trade = trades[~trades["complete_trade"]].copy().sort_values("entry_ts").tail(1)
    open_row = None if open_trade.empty else open_trade.iloc[0].to_dict()

    if not closed.empty:
        latest_closed = closed.iloc[-1]
        lifetime = float((1.0 + closed["net_ret"]).prod() - 1.0)
        latest_closed_ts = iso_z(latest_closed["exit_ts"])
    else:
        lifetime = 0.0
        latest_closed_ts = None

    status = {
        "candidate_id": "rank17_pullback_ethsol_narrow_pilot",
        "candidate_rank": 17,
        "stage": "P3_narrow_paper_pilot",
        "asset": asset,
        "scope_tag": "narrow_paper_pilot_eth_sol_only",
        "venue_mode": "paper_binance_spot",
        "signal_family": "pullback_recovery_confirmation",
        "sample_end_utc": iso_z(bars["timestamp"].iloc[-1]),
        "latest_closed_exit_ts_utc": latest_closed_ts,
        "lifetime_total_return_6bps": lifetime,
        "new_trades_appended": 0,
        "open_position": "open" if open_row else "none",
        "open_entry_ts_utc": iso_z(open_row["entry_ts"]) if open_row else None,
        "open_side": open_row.get("side") if open_row else None,
    }
    return closed, status, open_row


def _rank29_direction_from_row(row: pd.Series, *, allow_provisional: bool = True) -> tuple[int, str]:
    for prefix in RANK29_SIGNAL_PREFIXES:
        if not allow_provisional and int(row.get(f"{prefix}_line_is_provisional", 0) or 0) == 1:
            continue
        if row.get(f"{prefix}_breakout_bull") == 1 and row.get("tbn_composite_trend", 0) >= 2:
            return 1, prefix.replace("tbn_", "")
        if row.get(f"{prefix}_breakout_bear") == 1 and row.get("tbn_composite_trend", 0) <= -2:
            return -1, prefix.replace("tbn_", "")
    return 0, ""


def _rank29_trade_row_from_full(asset: str, full: pd.DataFrame, event_idx: int, direction: int, trigger_tf: str, *, hold_bars_target: int = RANK29_DEFAULT_HOLD_BARS) -> dict[str, object] | None:
    entry_idx = event_idx + 1
    exit_idx = min(event_idx + hold_bars_target, len(full) - 1)
    if entry_idx >= len(full):
        return None
    entry = float(full.iloc[entry_idx]["open"])
    exit_ = float(full.iloc[exit_idx]["close"])
    cost_rate = 6.0 / 10000.0
    gross = (exit_ / entry - 1.0) * direction
    net = (1.0 + gross) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
    actual_hold_bars = int(exit_idx - entry_idx + 1)
    return {
        "asset": asset,
        "variant": "breakout_align_ge2",
        "mode": "no_overlap_guard",
        "signal_engine": "hindsight_replay",
        "cost_bps_per_side": 6.0,
        "event_idx": int(event_idx),
        "event_ts": full.iloc[event_idx]["timestamp"],
        "entry_ts": full.iloc[entry_idx]["timestamp"],
        "exit_ts": full.iloc[exit_idx]["timestamp"],
        "direction": "long" if direction > 0 else "short",
        "trigger_tf": trigger_tf,
        "entry_price": entry,
        "exit_price": exit_,
        "gross_ret": gross,
        "net_ret": net,
        "hold_bars": actual_hold_bars,
        "complete_trade": actual_hold_bars == hold_bars_target,
    }


def _build_rank29_nav_frame(raw_bars: pd.DataFrame, *, backfill_history: bool) -> pd.DataFrame:
    nav = compute_trendline_breakout_navigator(
        raw_bars[["timestamp", "high", "low", "close"]].copy(),
        config=TrendlineBreakoutNavigatorConfig(backfill_history=backfill_history),
    )
    return pd.concat(
        [
            raw_bars.reset_index(drop=True),
            nav.drop(columns=["timestamp", "high", "low", "close"], errors="ignore").reset_index(drop=True),
        ],
        axis=1,
    )


def _build_rank29_trades_from_frame(asset: str, full: pd.DataFrame, *, allow_provisional: bool, signal_engine: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    last_exit = -1
    for i, row in full.iterrows():
        direction, trigger_tf = _rank29_direction_from_row(row, allow_provisional=allow_provisional)
        if direction == 0:
            continue
        if i <= last_exit:
            continue
        trade_row = _rank29_trade_row_from_full(asset, full, i, direction, trigger_tf)
        if trade_row is None:
            continue
        trade_row["signal_engine"] = signal_engine
        rows.append(trade_row)
        last_exit = min(i + RANK29_DEFAULT_HOLD_BARS, len(full) - 1)
    return pd.DataFrame(rows)


def build_rank29_trades_hindsight(asset: str, raw_bars: pd.DataFrame) -> pd.DataFrame:
    full = _build_rank29_nav_frame(raw_bars, backfill_history=True)
    return _build_rank29_trades_from_frame(asset, full, allow_provisional=True, signal_engine="hindsight_replay")


def build_rank29_trades_confirmed_lines(asset: str, raw_bars: pd.DataFrame) -> pd.DataFrame:
    full = _build_rank29_nav_frame(raw_bars, backfill_history=True)
    return _build_rank29_trades_from_frame(asset, full, allow_provisional=False, signal_engine="confirmed_line_only")


def build_rank29_trades_causal(asset: str, raw_bars: pd.DataFrame, *, replay_context_bars: int = RANK29_CAUSAL_REPLAY_CONTEXT_BARS) -> pd.DataFrame:
    del replay_context_bars
    full = _build_rank29_nav_frame(raw_bars, backfill_history=False)
    return _build_rank29_trades_from_frame(asset, full, allow_provisional=False, signal_engine="causal_replay")


def build_rank29_trades_baseline(asset: str, raw_bars: pd.DataFrame, *, replay_context_bars: int = RANK29_CAUSAL_REPLAY_CONTEXT_BARS) -> pd.DataFrame:
    return build_rank29_trades_causal(asset, raw_bars, replay_context_bars=replay_context_bars)


def build_rank29_trades(asset: str, raw_bars: pd.DataFrame) -> pd.DataFrame:
    return build_rank29_trades_hindsight(asset, raw_bars)


def compute_rank29_lane(asset: str, raw_bars: pd.DataFrame, exec_depth: dict) -> tuple[pd.DataFrame, dict, dict | None]:
    trades = build_rank29_trades_baseline(asset, raw_bars)
    if trades.empty:
        status = {
            "candidate_id": "rank29_trendline_breakout_navigator",
            "candidate_rank": 29,
            "stage": "P3_narrow_paper_pilot",
            "asset": asset,
            "scope_tag": "narrow_paper_pilot_rank29_breakout_align_ge2_no_overlap",
            "venue_mode": RANK29_EXEC_VENUE_MODE,
            "signal_family": "trendline_breakout_navigator",
            "sample_end_utc": iso_z(raw_bars["timestamp"].iloc[-1]),
            "latest_closed_exit_ts_utc": None,
            "lifetime_total_return_6bps": 0.0,
            "lifetime_total_return_livefriction": 0.0,
            "new_trades_appended": 0,
            "open_position": "none",
            "open_entry_ts_utc": None,
            "open_side": None,
            "fee_bps_per_side": RANK29_TAKER_FEE_BPS,
            "execution_notional_usd": RANK29_EXEC_NOTIONAL_USD,
            "friction_model": RANK29_EXEC_FRICTION_MODEL,
            "book_snapshot_asof_utc": exec_depth["snapshot_ts_utc"],
        }
        return pd.DataFrame(), status, None

    trades = trades.copy()
    for col in ["event_ts", "entry_ts", "exit_ts"]:
        trades[col] = pd.to_datetime(trades[col], utc=True)
    trades["candidate_id"] = "rank29_trendline_breakout_navigator"
    trades["candidate_rank"] = 29
    trades["stage"] = "P3_narrow_paper_pilot"
    trades["scope_tag"] = "narrow_paper_pilot_rank29_breakout_align_ge2_no_overlap"
    trades["venue_mode"] = RANK29_EXEC_VENUE_MODE
    trades["signal_family"] = "trendline_breakout_navigator"
    trades["source"] = RANK29_EXEC_SOURCE
    trades = apply_rank29_live_execution_model(trades, exec_depth)

    closed = trades[trades["complete_trade"]].copy().reset_index(drop=True)
    open_trade = trades[~trades["complete_trade"]].copy().sort_values("entry_ts").tail(1)
    open_row = None if open_trade.empty else open_trade.iloc[0].to_dict()

    if not closed.empty:
        latest_closed = closed.iloc[-1]
        lifetime_live = float((1.0 + closed["net_ret"]).prod() - 1.0)
        lifetime_legacy = float((1.0 + closed["net_ret_legacy_6bps"]).prod() - 1.0)
        latest_closed_ts = iso_z(latest_closed["exit_ts"])
        mean_entry_slip = float(closed["entry_slippage_bps_500u"].mean())
        mean_exit_slip = float(closed["exit_slippage_bps_500u"].mean())
    else:
        lifetime_live = 0.0
        lifetime_legacy = 0.0
        latest_closed_ts = None
        mean_entry_slip = 0.0
        mean_exit_slip = 0.0

    status = {
        "candidate_id": "rank29_trendline_breakout_navigator",
        "candidate_rank": 29,
        "stage": "P3_narrow_paper_pilot",
        "asset": asset,
        "scope_tag": "narrow_paper_pilot_rank29_breakout_align_ge2_no_overlap",
        "venue_mode": RANK29_EXEC_VENUE_MODE,
        "signal_family": "trendline_breakout_navigator",
        "sample_end_utc": iso_z(raw_bars["timestamp"].iloc[-1]),
        "latest_closed_exit_ts_utc": latest_closed_ts,
        "lifetime_total_return_6bps": lifetime_legacy,
        "lifetime_total_return_livefriction": lifetime_live,
        "new_trades_appended": 0,
        "open_position": "open" if open_row else "none",
        "open_entry_ts_utc": iso_z(open_row["entry_ts"]) if open_row else None,
        "open_side": open_row.get("direction") if open_row else None,
        "fee_bps_per_side": RANK29_TAKER_FEE_BPS,
        "execution_notional_usd": RANK29_EXEC_NOTIONAL_USD,
        "friction_model": RANK29_EXEC_FRICTION_MODEL,
        "book_snapshot_asof_utc": exec_depth["snapshot_ts_utc"],
        "mean_entry_slippage_bps_500u": mean_entry_slip,
        "mean_exit_slippage_bps_500u": mean_exit_slip,
    }
    return closed, status, open_row


def compute_rank29_gate_shadow_lane(
    asset: str,
    raw_bars: pd.DataFrame,
    gate_daily_flags: pd.DataFrame,
    exec_depth: dict,
    *,
    shadow_bad_weight: float = RANK29_SHADOW_BAD_WEIGHT,
) -> tuple[pd.DataFrame, dict, dict | None]:
    trades = build_rank29_trades_baseline(asset, raw_bars)
    if trades.empty:
        status = {
            "candidate_id": "rank29_trendline_breakout_gate_shadow",
            "candidate_rank": 29,
            "stage": "P3_narrow_paper_shadow",
            "asset": asset,
            "scope_tag": "narrow_paper_pilot_rank29_low_trend_high_noise_w25_shadow",
            "venue_mode": RANK29_EXEC_VENUE_MODE,
            "signal_family": "trendline_breakout_navigator_regime_gate_shadow",
            "sample_end_utc": iso_z(raw_bars["timestamp"].iloc[-1]),
            "latest_closed_exit_ts_utc": None,
            "lifetime_total_return_6bps": 0.0,
            "lifetime_total_return_livefriction": 0.0,
            "new_trades_appended": 0,
            "open_position": "none",
            "open_entry_ts_utc": None,
            "open_side": None,
            "shadow_bad_regime_weight": shadow_bad_weight,
            "gate_hit_trades": 0,
            "mean_exposure_weight": 1.0,
            "fee_bps_per_side": RANK29_TAKER_FEE_BPS,
            "execution_notional_usd": RANK29_EXEC_NOTIONAL_USD,
            "friction_model": RANK29_EXEC_FRICTION_MODEL,
            "book_snapshot_asof_utc": exec_depth["snapshot_ts_utc"],
        }
        return pd.DataFrame(), status, None

    trades = trades.copy()
    for col in ["event_ts", "entry_ts", "exit_ts"]:
        trades[col] = pd.to_datetime(trades[col], utc=True)

    trades["trade_day_utc"] = trades["entry_ts"].dt.floor("D")
    gate = gate_daily_flags.copy()
    if not gate.empty:
        gate["effective_for_trade_day"] = pd.to_datetime(gate["effective_for_trade_day"], utc=True)
        trades = trades.merge(
            gate[
                [
                    "effective_for_trade_day",
                    "gate_trend_strength_20d_mtd_mean",
                    "gate_noise_ratio_20d_mtd_mean",
                    "gate_low_trend_high_noise",
                ]
            ],
            left_on="trade_day_utc",
            right_on="effective_for_trade_day",
            how="left",
        )
    else:
        trades["gate_trend_strength_20d_mtd_mean"] = pd.NA
        trades["gate_noise_ratio_20d_mtd_mean"] = pd.NA
        trades["gate_low_trend_high_noise"] = 0
        trades["effective_for_trade_day"] = pd.NaT

    trades["gate_low_trend_high_noise"] = trades["gate_low_trend_high_noise"].fillna(0).astype(int)
    trades["exposure_weight"] = trades["gate_low_trend_high_noise"].map({1: shadow_bad_weight, 0: 1.0}).astype(float)
    trades["candidate_id"] = "rank29_trendline_breakout_gate_shadow"
    trades["candidate_rank"] = 29
    trades["stage"] = "P3_narrow_paper_shadow"
    trades["scope_tag"] = "narrow_paper_pilot_rank29_low_trend_high_noise_w25_shadow"
    trades["venue_mode"] = RANK29_EXEC_VENUE_MODE
    trades["signal_family"] = "trendline_breakout_navigator_regime_gate_shadow"
    trades["source"] = RANK29_EXEC_SOURCE
    trades["gate_variant"] = "low_trend_high_noise_w25"
    trades["shadow_bad_regime_weight"] = shadow_bad_weight
    trades = apply_rank29_live_execution_model(trades, exec_depth, exposure_col="exposure_weight")
    trades["baseline_net_ret_livefriction"] = trades["net_ret"]
    trades["baseline_net_ret"] = trades["net_ret_legacy_6bps"]
    trades["net_ret_legacy_shadow"] = trades["baseline_net_ret"] * trades["exposure_weight"]
    trades["net_ret"] = trades["baseline_net_ret_livefriction"] * trades["exposure_weight"]

    closed = trades[trades["complete_trade"]].copy().reset_index(drop=True)
    open_trade = trades[~trades["complete_trade"]].copy().sort_values("entry_ts").tail(1)
    open_row = None if open_trade.empty else open_trade.iloc[0].to_dict()

    if not closed.empty:
        latest_closed = closed.iloc[-1]
        lifetime_live = float((1.0 + closed["net_ret"]).prod() - 1.0)
        lifetime_legacy = float((1.0 + closed["net_ret_legacy_shadow"]).prod() - 1.0)
        latest_closed_ts = iso_z(latest_closed["exit_ts"])
        gate_hit_trades = int(closed["gate_low_trend_high_noise"].sum())
        mean_exposure_weight = float(closed["exposure_weight"].mean())
        mean_entry_slip = float(closed["entry_slippage_bps_500u"].mean())
        mean_exit_slip = float(closed["exit_slippage_bps_500u"].mean())
    else:
        lifetime_live = 0.0
        lifetime_legacy = 0.0
        latest_closed_ts = None
        gate_hit_trades = 0
        mean_exposure_weight = 1.0
        mean_entry_slip = 0.0
        mean_exit_slip = 0.0

    status = {
        "candidate_id": "rank29_trendline_breakout_gate_shadow",
        "candidate_rank": 29,
        "stage": "P3_narrow_paper_shadow",
        "asset": asset,
        "scope_tag": "narrow_paper_pilot_rank29_low_trend_high_noise_w25_shadow",
        "venue_mode": RANK29_EXEC_VENUE_MODE,
        "signal_family": "trendline_breakout_navigator_regime_gate_shadow",
        "sample_end_utc": iso_z(raw_bars["timestamp"].iloc[-1]),
        "latest_closed_exit_ts_utc": latest_closed_ts,
        "lifetime_total_return_6bps": lifetime_legacy,
        "lifetime_total_return_livefriction": lifetime_live,
        "new_trades_appended": 0,
        "open_position": "open" if open_row else "none",
        "open_entry_ts_utc": iso_z(open_row["entry_ts"]) if open_row else None,
        "open_side": open_row.get("direction") if open_row else None,
        "shadow_bad_regime_weight": shadow_bad_weight,
        "gate_hit_trades": gate_hit_trades,
        "mean_exposure_weight": mean_exposure_weight,
        "gate_snapshot_asof_utc": iso_z(gate["timestamp"].max()) if not gate.empty else None,
        "fee_bps_per_side": RANK29_TAKER_FEE_BPS,
        "execution_notional_usd": RANK29_EXEC_NOTIONAL_USD,
        "friction_model": RANK29_EXEC_FRICTION_MODEL,
        "book_snapshot_asof_utc": exec_depth["snapshot_ts_utc"],
        "mean_entry_slippage_bps_500u": mean_entry_slip,
        "mean_exit_slippage_bps_500u": mean_exit_slip,
    }
    return closed, status, open_row


def build_rank32b_frame(asset: str, raw_bars: pd.DataFrame) -> pd.DataFrame:
    bars = raw_bars.copy()
    bars["asset"] = asset
    market = bars[["timestamp", "close"]].copy().rename(columns={"close": "close_1h_src"}).set_index("timestamp")
    market_1h = market.resample("1h").last().dropna().reset_index()
    market_1h["ema_fast_1h"] = market_1h["close_1h_src"].ewm(span=rank32_base_mod.EMA_FAST_1H, adjust=False).mean()
    market_1h["ema_slow_1h"] = market_1h["close_1h_src"].ewm(span=rank32_base_mod.EMA_SLOW_1H, adjust=False).mean()
    market_1h["fast_slope"] = market_1h["ema_fast_1h"].pct_change()
    market_1h["slow_slope"] = market_1h["ema_slow_1h"].pct_change()

    frame = pd.merge_asof(
        bars.sort_values("timestamp"),
        market_1h.sort_values("timestamp"),
        on="timestamp",
        direction="backward",
    )
    frame["spread_mid"] = (frame["ema_fast_1h"] + frame["ema_slow_1h"]) / 2.0
    frame["long_structure"] = (frame["ema_fast_1h"] > frame["ema_slow_1h"]).fillna(False).astype(int)
    frame["short_structure"] = (frame["ema_fast_1h"] < frame["ema_slow_1h"]).fillna(False).astype(int)
    frame["slope_floor_long"] = ((frame["fast_slope"] > rank32_base_mod.SLOPE_FLOOR) & (frame["slow_slope"] > 0)).fillna(False).astype(int)
    frame["slope_floor_short"] = ((frame["fast_slope"] < -rank32_base_mod.SLOPE_FLOOR) & (frame["slow_slope"] < 0)).fillna(False).astype(int)
    frame["slope_strength"] = frame["fast_slope"].abs().fillna(0.0) + frame["slow_slope"].abs().fillna(0.0)

    prev_close = frame["close"].shift(1)
    prev_fast = frame["ema_fast_1h"].shift(1)
    prev_mid = frame["spread_mid"].shift(1)
    recent_low = frame["low"].shift(1).rolling(rank32_base_mod.RECLAIM_LOOKBACK, min_periods=rank32_base_mod.RECLAIM_LOOKBACK).min()
    recent_high = frame["high"].shift(1).rolling(rank32_base_mod.RECLAIM_LOOKBACK, min_periods=rank32_base_mod.RECLAIM_LOOKBACK).max()

    frame["cross_only_long"] = ((frame["long_structure"] == 1) & (prev_close <= prev_fast) & (frame["close"] > frame["ema_fast_1h"])).fillna(False).astype(int)
    frame["cross_only_short"] = ((frame["short_structure"] == 1) & (prev_close >= prev_fast) & (frame["close"] < frame["ema_fast_1h"])).fillna(False).astype(int)
    frame["slope_floor_long_signal"] = ((frame["cross_only_long"] == 1) & (frame["slope_floor_long"] == 1)).astype(int)
    frame["slope_floor_short_signal"] = ((frame["cross_only_short"] == 1) & (frame["slope_floor_short"] == 1)).astype(int)
    frame["reclaim_long_signal"] = ((frame["long_structure"] == 1) & (frame["slope_floor_long"] == 1) & (recent_low <= prev_mid) & (frame["close"] > frame["ema_fast_1h"]) & (frame["close"] > frame["spread_mid"]) & (prev_close <= prev_mid)).fillna(False).astype(int)
    frame["reclaim_short_signal"] = ((frame["short_structure"] == 1) & (frame["slope_floor_short"] == 1) & (recent_high >= prev_mid) & (frame["close"] < frame["ema_fast_1h"]) & (frame["close"] < frame["spread_mid"]) & (prev_close >= prev_mid)).fillna(False).astype(int)
    return frame


def compute_rank32b_lane(asset: str, raw_bars: pd.DataFrame) -> tuple[pd.DataFrame, dict, dict | None]:
    frame = build_rank32b_frame(asset, raw_bars)
    trades, _, _ = rank32_base_mod.build_trades(frame, asset, "ema_cross_plus_slope_floor", 6.0)
    if trades.empty:
        status = {
            "candidate_id": "rank32b_slope_floor_continuation",
            "candidate_rank": 32,
            "stage": "P3_narrow_paper_pilot",
            "asset": asset,
            "scope_tag": "narrow_paper_pilot_rank32b_full_scope",
            "venue_mode": "paper_binance_spot",
            "signal_family": "ema_slope_floor_continuation",
            "sample_end_utc": iso_z(frame["timestamp"].iloc[-1]),
            "latest_closed_exit_ts_utc": None,
            "lifetime_total_return_6bps": 0.0,
            "new_trades_appended": 0,
            "open_position": "none",
            "open_entry_ts_utc": None,
            "open_side": None,
        }
        return pd.DataFrame(), status, None

    trades = trades.copy()
    for col in ["event_ts", "entry_ts", "exit_ts"]:
        trades[col] = pd.to_datetime(trades[col], utc=True)
    trades["candidate_id"] = "rank32b_slope_floor_continuation"
    trades["candidate_rank"] = 32
    trades["stage"] = "P3_narrow_paper_pilot"
    trades["scope_tag"] = "narrow_paper_pilot_rank32b_full_scope"
    trades["venue_mode"] = "paper_binance_spot"
    trades["signal_family"] = "ema_slope_floor_continuation"
    trades["source"] = "binance_spot_15m"
    trades["complete_trade"] = trades["hold_bars"] >= rank32_base_mod.HOLD_BARS

    closed = trades[trades["complete_trade"]].copy().reset_index(drop=True)
    open_trade = trades[~trades["complete_trade"]].copy().sort_values("entry_ts").tail(1)
    open_row = None if open_trade.empty else open_trade.iloc[0].to_dict()

    if not closed.empty:
        latest_closed = closed.iloc[-1]
        lifetime = float((1.0 + closed["net_ret"]).prod() - 1.0)
        latest_closed_ts = iso_z(latest_closed["exit_ts"])
    else:
        lifetime = 0.0
        latest_closed_ts = None

    status = {
        "candidate_id": "rank32b_slope_floor_continuation",
        "candidate_rank": 32,
        "stage": "P3_narrow_paper_pilot",
        "asset": asset,
        "scope_tag": "narrow_paper_pilot_rank32b_full_scope",
        "venue_mode": "paper_binance_spot",
        "signal_family": "ema_slope_floor_continuation",
        "sample_end_utc": iso_z(frame["timestamp"].iloc[-1]),
        "latest_closed_exit_ts_utc": latest_closed_ts,
        "lifetime_total_return_6bps": lifetime,
        "new_trades_appended": 0,
        "open_position": "open" if open_row else "none",
        "open_entry_ts_utc": iso_z(open_row["entry_ts"]) if open_row else None,
        "open_side": open_row.get("direction") if open_row else None,
    }
    return closed, status, open_row


def lane_key(candidate_id: str, asset: str) -> str:
    return f"{candidate_id}::{asset}"


def append_new_rows(state: dict, closed_df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    if closed_df.empty:
        return pd.DataFrame(), {}
    watermarks = state.setdefault("watermarks", {})
    out_rows: list[pd.DataFrame] = []
    counts: dict[str, int] = {}
    for (candidate_id, asset), sub in closed_df.groupby(["candidate_id", "asset"], sort=False):
        key = lane_key(str(candidate_id), str(asset))
        watermark = watermarks.get(key)
        sub = sub.sort_values("exit_ts").copy()
        if watermark:
            sub = sub[sub["exit_ts"] > pd.to_datetime(watermark, utc=True)].copy()
            if sub.empty:
                continue
            out_rows.append(sub)
            watermarks[key] = iso_z(sub["exit_ts"].max())
            counts[key] = counts.get(key, 0) + len(sub)
        else:
            # New lane added after initial rollout: start tracking from the current latest closed watermark,
            # but do not backfill the entire historical sample into the ongoing ledger.
            watermarks[key] = iso_z(sub["exit_ts"].max())
    if not out_rows:
        return pd.DataFrame(), counts
    appended = pd.concat(out_rows, ignore_index=True)
    return appended, counts


def initialize_watermarks(state: dict, closed_df: pd.DataFrame) -> None:
    watermarks = state.setdefault("watermarks", {})
    if closed_df.empty:
        return
    for (candidate_id, asset), sub in closed_df.groupby(["candidate_id", "asset"], sort=False):
        sub = sub.sort_values("exit_ts")
        watermarks[lane_key(str(candidate_id), str(asset))] = iso_z(sub["exit_ts"].iloc[-1])


def build_open_positions_frame(open_rows: list[dict | None]) -> pd.DataFrame:
    rows = []
    for item in open_rows:
        if not item:
            continue
        rows.append(
            {
                "candidate_id": item.get("candidate_id"),
                "candidate_rank": item.get("candidate_rank"),
                "asset": item.get("asset"),
                "entry_ts_utc": iso_z(item.get("entry_ts")),
                "exit_ts_marked_utc": iso_z(item.get("exit_ts")),
                "side": item.get("side") or item.get("direction"),
                "signal_family": item.get("signal_family"),
                "note": "open paper position inferred from incomplete final sample; wait for next manual refresh to confirm close",
            }
        )
    return pd.DataFrame(rows)


def normalize_for_csv(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[col]):
            out[col] = out[col].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Manual kickoff/refresh for Rank 2 / 17 / 29 baseline+gate-shadow / 32b narrow paper lanes using Binance 15m spot data.")
    parser.add_argument("--init-from-now", action="store_true", help="Initialize watermarks from current closed trades and start manual paper tracking from now.")
    parser.add_argument("--refresh", action="store_true", help="Refresh from Binance and append new closed trades since initialization.")
    parser.add_argument("--days", type=int, default=150, help="Historical Binance window to recompute each lane.")
    parser.add_argument("--force-reinit", action="store_true", help="Allow reinitializing even if state already exists.")
    args = parser.parse_args()

    if not args.init_from_now and not args.refresh:
        parser.error("choose one of --init-from-now or --refresh")

    ensure_dir(ART_DIR)
    state = load_state()
    if args.init_from_now and state and not args.force_reinit:
        parser.error(f"state already exists at {STATE_PATH}; use --force-reinit to reset")
    if args.refresh and not state:
        parser.error(f"missing state at {STATE_PATH}; run --init-from-now first")

    bars_cache = {asset: download_binance_bars(symbol, interval="15m", days=args.days) for asset, symbol in ASSET_TO_BINANCE.items()}
    rank29_exec_depth = {asset: download_binance_futures_depth(symbol, limit=RANK29_EXEC_DEPTH_LIMIT) for asset, symbol in ASSET_TO_BINANCE.items()}
    rank29_gate_thresholds = load_rank29_gate_thresholds()
    rank29_gate_daily_flags = compute_rank29_gate_daily_flags(bars_cache, rank29_gate_thresholds)

    closed_frames: list[pd.DataFrame] = []
    status_rows: list[dict] = []
    open_rows: list[dict | None] = []

    for asset in ["BTC-USD", "ETH-USD", "SOL-USD"]:
        closed, status, open_row = compute_rank2_lane(asset, bars_cache[asset])
        closed_frames.append(closed)
        status_rows.append(status)
        open_rows.append(open_row)

    for asset in ["ETH-USD", "SOL-USD"]:
        closed, status, open_row = compute_rank17_lane(asset, bars_cache[asset])
        closed_frames.append(closed)
        status_rows.append(status)
        open_rows.append(open_row)

    for asset in ["BTC-USD", "ETH-USD", "SOL-USD"]:
        closed, status, open_row = compute_rank29_lane(asset, bars_cache[asset], rank29_exec_depth[asset])
        closed_frames.append(closed)
        status_rows.append(status)
        open_rows.append(open_row)

    for asset in ["BTC-USD", "ETH-USD", "SOL-USD"]:
        closed, status, open_row = compute_rank29_gate_shadow_lane(asset, bars_cache[asset], rank29_gate_daily_flags, rank29_exec_depth[asset])
        closed_frames.append(closed)
        status_rows.append(status)
        open_rows.append(open_row)

    for asset in ["BTC-USD", "ETH-USD", "SOL-USD"]:
        closed, status, open_row = compute_rank32b_lane(asset, bars_cache[asset])
        closed_frames.append(closed)
        status_rows.append(status)
        open_rows.append(open_row)

    all_closed = pd.concat([df for df in closed_frames if not df.empty], ignore_index=True) if any(not df.empty for df in closed_frames) else pd.DataFrame()
    rank29_shadow_trade_view = (
        all_closed[all_closed["candidate_id"].isin(["rank29_trendline_breakout_navigator", "rank29_trendline_breakout_gate_shadow"])].copy()
        if not all_closed.empty
        else pd.DataFrame()
    )

    if args.init_from_now:
        state = {
            "initialized_at_utc": iso_z(utc_now()),
            "mode": "manual_follow_up",
            "source": "binance_spot_15m",
            "notes": "Kickoff from current closed-trade watermark; later manual refresh appends only trades closed after init.",
            "watermarks": {},
        }
        initialize_watermarks(state, all_closed)
        save_state(state)
        if LEDGER_PATH.exists():
            LEDGER_PATH.unlink()
        appended = pd.DataFrame()
        append_counts = {}
    else:
        appended, append_counts = append_new_rows(state, all_closed)
        save_state(state)
        if not appended.empty:
            prior = read_csv_or_empty(LEDGER_PATH)
            combined = pd.concat([prior, normalize_for_csv(appended)], ignore_index=True) if not prior.empty else normalize_for_csv(appended)
            combined.to_csv(LEDGER_PATH, index=False)

    for row in status_rows:
        key = lane_key(row["candidate_id"], row["asset"])
        row["new_trades_appended"] = int(append_counts.get(key, 0)) if args.refresh else 0
        row["watermark_exit_ts_utc"] = state.get("watermarks", {}).get(key)

    status_df = pd.DataFrame(status_rows).sort_values(["candidate_rank", "candidate_id", "asset"]).reset_index(drop=True)
    normalize_for_csv(status_df).to_csv(STATUS_PATH, index=False)

    if rank29_shadow_trade_view.empty:
        RANK29_SHADOW_TRADE_VIEW_PATH.write_text(
            "candidate_id,asset,entry_ts,exit_ts,net_ret,gate_low_trend_high_noise,baseline_net_ret,exposure_weight\n"
        )
    else:
        normalize_for_csv(rank29_shadow_trade_view.sort_values(["candidate_id", "asset", "entry_ts", "exit_ts"]).reset_index(drop=True)).to_csv(
            RANK29_SHADOW_TRADE_VIEW_PATH, index=False
        )

    open_df = build_open_positions_frame(open_rows)
    if open_df.empty:
        OPEN_POSITIONS_PATH.write_text("candidate_id,candidate_rank,asset,entry_ts_utc,exit_ts_marked_utc,side,signal_family,note\n")
    else:
        normalize_for_csv(open_df).to_csv(OPEN_POSITIONS_PATH, index=False)

    summary = {
        "run_at_utc": iso_z(utc_now()),
        "mode": "init_from_now" if args.init_from_now else "refresh",
        "source": "binance_spot_15m",
        "rank29_execution_proxy": {
            "venue_mode": RANK29_EXEC_VENUE_MODE,
            "friction_model": RANK29_EXEC_FRICTION_MODEL,
            "fee_bps_per_side": RANK29_TAKER_FEE_BPS,
            "notional_usd": RANK29_EXEC_NOTIONAL_USD,
            "book_snapshots": {asset: depth["snapshot_ts_utc"] for asset, depth in rank29_exec_depth.items()},
        },
        "days": int(args.days),
        "lanes_initialized": int(len(status_rows)),
        "new_closed_trades_appended": int(len(appended)) if args.refresh else 0,
        "status_path": str(STATUS_PATH.relative_to(ROOT)),
        "open_positions_path": str(OPEN_POSITIONS_PATH.relative_to(ROOT)),
        "ledger_path": str(LEDGER_PATH.relative_to(ROOT)),
        "rank29_shadow_trade_view_path": str(RANK29_SHADOW_TRADE_VIEW_PATH.relative_to(ROOT)),
        "state_path": str(STATE_PATH.relative_to(ROOT)),
    }
    RUN_SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))

    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
