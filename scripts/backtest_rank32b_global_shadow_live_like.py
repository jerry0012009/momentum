#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from copy import deepcopy
from datetime import timedelta
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.execution.canary32b.signal_adapter import Rank32BPerpSignalAdapter  # noqa: E402
from momentum.domain.canary32b_models import AlphaSignal, Side  # noqa: E402

CONFIG_PATH = ROOT / "config" / "execution" / "rank32b_canary.yaml"
OUT_DIR = ROOT / "reports" / "artifacts" / "rank32b_shadow_global_live_like_backtest"
DAY_1M_CACHE_DIR = OUT_DIR / "day_1m_cache"
LEDGER_DIR = OUT_DIR / "trade_ledgers"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


phase6lib = load_module(ROOT / "scripts" / "run_rank32b_canary_phase6.py", "rank32b_live_like_bt_phase6")
shadow_mod = load_module(ROOT / "scripts" / "run_rank32b_global_selector_shadow.py", "rank32b_live_like_bt_shadow")
depth_v2_mod = load_module(ROOT / "scripts" / "rank32b_depth_v2_paper.py", "rank32b_live_like_bt_depth")
preview_mod = load_module(ROOT / "scripts" / "build_rank32b_unclosed15m_preview_backtest.py", "rank32b_live_like_preview")


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_cfg(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_live_like_notional(cfg: dict[str, Any], asset_to_symbol: dict[str, str]) -> tuple[float, dict[str, float]]:
    phase6 = cfg.get("phase6", {}) if isinstance(cfg.get("phase6"), dict) else {}
    global_live = phase6.get("global_live", {}) if isinstance(phase6.get("global_live"), dict) else {}
    base_sizing = phase6.get("sizing", {}) if isinstance(phase6.get("sizing"), dict) else {}
    default_notional = float(global_live.get("desired_notional_usdt", base_sizing.get("desired_notional_usdt", 100.0)))
    by_symbol = {str(symbol).upper(): default_notional for symbol in asset_to_symbol.values()}
    overrides = global_live.get("desired_notional_usdt_by_symbol") if isinstance(global_live.get("desired_notional_usdt_by_symbol"), dict) else {}
    for key, value in overrides.items():
        try:
            num = float(value)
        except Exception:
            continue
        if math.isfinite(num) and num > 0:
            by_symbol[str(key).upper()] = num
    return default_notional, by_symbol


def normalize_selected_rows(signals: list[Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for sig in signals:
        row = sig.to_dict() if hasattr(sig, "to_dict") else dict(sig)
        metadata = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
        row["signal_confirmed_at"] = phase6lib.signal_confirmed_at(str(row.get("timestamp") or ""), metadata)
        rows.append(row)
    rows.sort(key=lambda row: (str(row.get("signal_confirmed_at") or row.get("timestamp") or ""), str(row.get("symbol") or "")))
    return rows


def trade_ts(row: dict[str, Any]) -> pd.Timestamp:
    for key in ("exit_ts", "mark_ts", "signal_confirmed_at", "signal_ts", "timestamp"):
        ts = shadow_mod.parse_ts(row.get(key))
        if ts is not None:
            return ts
    return pd.Timestamp.min.tz_localize("UTC")


def compute_metrics(trades: list[dict[str, Any]], *, default_notional: float, notional_by_symbol: dict[str, float]) -> dict[str, Any]:
    effective = [row for row in trades if row.get("paper_trade_state") in {"open", "closed"}]
    effective.sort(key=trade_ts)
    equity = 1.0
    peak = 1.0
    max_dd = 0.0
    usdt_pnl = 0.0
    closed_usdt_pnl = 0.0
    for row in effective:
        ret = float(row.get("paper_effective_net_ret") or 0.0)
        symbol = str(row.get("symbol") or "").upper()
        notional = float(notional_by_symbol.get(symbol, default_notional))
        usdt_pnl += notional * ret
        if row.get("paper_trade_state") == "closed":
            closed_usdt_pnl += notional * ret
        equity *= 1.0 + ret
        peak = max(peak, equity)
        max_dd = max(max_dd, 0.0 if peak <= 0 else (peak - equity) / peak)
    closed = [row for row in effective if row.get("paper_trade_state") == "closed"]
    closed_rets = [float(row.get("net_ret") or 0.0) for row in closed if row.get("net_ret") is not None]
    return {
        "usdt_pnl_live_like": usdt_pnl,
        "closed_usdt_pnl_live_like": closed_usdt_pnl,
        "max_drawdown": max_dd,
        "effective_trade_count": len(effective),
        "closed_trade_count": len(closed),
        "closed_win_rate": float(sum(1 for x in closed_rets if x > 0) / len(closed_rets)) if closed_rets else None,
        "avg_closed_net_ret": float(sum(closed_rets) / len(closed_rets)) if closed_rets else None,
    }


def day_cache_paths(symbol: str, day_start: pd.Timestamp) -> tuple[Path, Path]:
    ensure_dir(DAY_1M_CACHE_DIR)
    tag = day_start.strftime("%Y-%m-%d")
    return DAY_1M_CACHE_DIR / f"{symbol.upper()}__{tag}__1m.csv", DAY_1M_CACHE_DIR / f"{symbol.upper()}__{tag}__1m.meta.json"


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def fetch_symbol_day_1m(symbol: str, day_start: pd.Timestamp, cache_cfg: dict[str, Any]) -> pd.DataFrame:
    csv_path, meta_path = day_cache_paths(symbol, day_start)
    if csv_path.exists() and csv_path.stat().st_size > 0:
        try:
            df = pd.read_csv(csv_path)
            return depth_v2_mod.normalize_1m_frame(df)
        except Exception:
            pass
    day_end = day_start + pd.Timedelta(days=1) - pd.Timedelta(milliseconds=1)
    try:
        df = depth_v2_mod.fetch_klines_1m(
            symbol,
            int(day_start.timestamp() * 1000),
            int(day_end.timestamp() * 1000),
            cache_cfg=cache_cfg,
        )
        depth_v2_mod.save_minute_cache_frame(csv_path, df)
        meta_path.write_text(
            json.dumps(
                {
                    "symbol": symbol.upper(),
                    "day_start_utc": day_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "day_end_utc": day_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "row_count": int(len(df)),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return df
    except Exception as exc:
        meta_path.write_text(
            json.dumps(
                {
                    "symbol": symbol.upper(),
                    "day_start_utc": day_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "error": str(exc),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        raise


def get_trade_minute_window(
    symbol: str,
    *,
    entry_ts: pd.Timestamp,
    timeout_minutes: int,
    cache_cfg: dict[str, Any],
    day_cache: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    monitor_start = entry_ts.floor("1min") + pd.Timedelta(minutes=1)
    monitor_end = (entry_ts + pd.Timedelta(minutes=int(timeout_minutes))).ceil("1min")
    day_start = monitor_start.floor("1D")
    frames: list[pd.DataFrame] = []
    while day_start <= monitor_end.floor("1D"):
        key = f"{symbol.upper()}|{day_start.strftime('%Y-%m-%d')}"
        if key not in day_cache:
            day_cache[key] = fetch_symbol_day_1m(symbol, day_start, cache_cfg)
        frames.append(day_cache[key])
        day_start = day_start + pd.Timedelta(days=1)
    if not frames:
        return pd.DataFrame(columns=["open_ts", "close_ts", "open", "high", "low", "close", "volume"])
    df = depth_v2_mod.normalize_1m_frame(pd.concat(frames, ignore_index=True))
    return df[(df["open_ts"] >= monitor_start) & (df["open_ts"] <= monitor_end)].reset_index(drop=True)


def get_symbol_bars_local_first(symbol: str, *, days: int, cache: dict[str, pd.DataFrame]) -> pd.DataFrame:
    if symbol in cache:
        return cache[symbol]
    try:
        df = shadow_mod.exec_mod.load_or_fetch_perp_5m(symbol, days=days, refresh=False)
    except Exception:
        df = pd.DataFrame()
    if df.empty:
        # Only fetch remotely when there is no local cache at all.
        df = shadow_mod.exec_mod.load_or_fetch_perp_5m(symbol, days=days, refresh=True)
    df = df.sort_values("timestamp").reset_index(drop=True)
    cache[symbol] = df
    return df


def get_signal_minute_history(
    symbol: str,
    *,
    start_ts: pd.Timestamp,
    end_ts: pd.Timestamp,
    cache_cfg: dict[str, Any],
    day_cache: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    fetch_start = pd.to_datetime(start_ts, utc=True).floor("1min")
    fetch_end = pd.to_datetime(end_ts, utc=True).ceil("1min")
    frames: list[pd.DataFrame] = []
    day_start = fetch_start.floor("1D")
    while day_start <= fetch_end.floor("1D"):
        key = f"signal|{symbol.upper()}|{day_start.strftime('%Y-%m-%d')}"
        if key not in day_cache:
            day_cache[key] = fetch_symbol_day_1m(symbol, day_start, cache_cfg)
        frames.append(day_cache[key])
        day_start = day_start + pd.Timedelta(days=1)
    if not frames:
        return pd.DataFrame(columns=["open_ts", "close_ts", "open", "high", "low", "close", "volume"])
    df = depth_v2_mod.normalize_1m_frame(pd.concat(frames, ignore_index=True))
    return df[(df["close_ts"] >= fetch_start) & (df["open_ts"] <= fetch_end)].reset_index(drop=True)


def load_signal_snapshot(
    cfg: dict[str, Any],
    *,
    horizon_days: int,
    now_ts: pd.Timestamp,
    cache_cfg: dict[str, Any],
    day_cache: dict[str, pd.DataFrame],
):
    shadow_cfg = shadow_mod.load_shadow_cfg(cfg)
    asset_to_symbol = shadow_cfg["asset_to_symbol"]
    signal_cfg = cfg.get("signal_adapter", {}) if isinstance(cfg.get("signal_adapter"), dict) else {}
    signal_lookback_days = max(0, int(signal_cfg.get("lookback_days", horizon_days)))
    signal_fetch_days = int(horizon_days) + signal_lookback_days
    preview_enabled = bool(signal_cfg.get("preview_unclosed_15m", False))
    adapter = Rank32BPerpSignalAdapter(
        asset_to_symbol=asset_to_symbol,
        days=signal_fetch_days,
        recent_hours=int(horizon_days * 24),
        variant=str(signal_cfg.get("variant", "ema_cross_plus_slope_floor")),
        refresh_bars=False,
        refresh_tail_days=(int(signal_cfg["refresh_tail_days"]) if signal_cfg.get("refresh_tail_days") is not None else None),
        preview_unclosed_15m=preview_enabled,
        preview_fetch_limit=int(signal_cfg.get("preview_fetch_limit", 30)),
        entry_delay_minutes=int(signal_cfg.get("entry_delay_minutes", 0)),
        official_signal_ttl_minutes=None,
    )
    cutoff = now_ts - pd.Timedelta(hours=int(horizon_days * 24))
    refresh_tail_days = max(0, int(signal_cfg.get("refresh_tail_days", 2) or 2))
    # Warmup should only add the indicator/history buffer once. The previous version
    # accidentally used horizon+lookback again here, expanding the effective fetch
    # window to roughly 2*horizon+lookback and contaminating the intended time scope.
    warmup_days = max(signal_lookback_days, refresh_tail_days)
    warmup_start = cutoff - pd.Timedelta(days=warmup_days)
    signals: list[AlphaSignal] = []
    latest_bar: pd.Timestamp | None = None
    latest_observed_signal: pd.Timestamp | None = None

    for asset, symbol in asset_to_symbol.items():
        minute_df = get_signal_minute_history(
            symbol,
            start_ts=warmup_start,
            end_ts=now_ts,
            cache_cfg=cache_cfg,
            day_cache=day_cache,
        )
        if minute_df.empty:
            continue
        minute_df = minute_df.sort_values("open_ts").reset_index(drop=True)
        latest_bar = pd.to_datetime(minute_df.iloc[-1]["open_ts"], utc=True) if latest_bar is None else max(latest_bar, pd.to_datetime(minute_df.iloc[-1]["open_ts"], utc=True))

        hour_df = preview_mod.build_completed_hours(minute_df)
        bars15 = preview_mod.build_completed_15m(minute_df, hour_df)
        if not bars15.empty:
            official_df = preview_mod.official_signal_rows(asset, symbol, bars15)
            if not official_df.empty:
                official_df = official_df[(official_df["signal_ts"] >= cutoff) & (official_df["signal_confirmed_at"] <= now_ts)].copy()
                for _, row in official_df.iterrows():
                    ts = pd.to_datetime(row["signal_ts"], utc=True)
                    ready_at = pd.to_datetime(row["signal_confirmed_at"], utc=True)
                    side = Side.LONG if int(row["direction"]) > 0 else Side.SHORT
                    atr_val = row["atr14"]
                    atr_ready = pd.notna(atr_val) and float(atr_val) > 0
                    signals.append(
                        AlphaSignal(
                            signal_id=adapter._signal_id(symbol=symbol, ts=ts, side=side, mode="official"),
                            timestamp=ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                            symbol=symbol,
                            side=side,
                            signal_price=float(row["signal_price"]),
                            alpha_name="rank32b_slope_floor_continuation",
                            alpha_version="canary_phase1_v1",
                            metadata={
                                "asset": asset,
                                "variant": str(signal_cfg.get("variant", "ema_cross_plus_slope_floor")),
                                "signal_mode": "official_close",
                                "bucket_start": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                "bucket_close_at": ready_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                "first_seen_at": ready_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                "expired_at": None,
                                "confirmed_at_close": True,
                                "official_confirmed_at": ready_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                "entry_reference": "immediate_market",
                                "signal_confirmed_at_override": ready_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                "entry_delay_minutes": 0,
                                "fast_slope": float(row["fast_slope"]) if pd.notna(row["fast_slope"]) else None,
                                "slow_slope": float(row["slow_slope"]) if pd.notna(row["slow_slope"]) else None,
                                "spread_mid": None,
                                "slope_strength": float(row["slope_strength"]) if pd.notna(row["slope_strength"]) else None,
                                "atr_ready": bool(atr_ready),
                                "atr14": float(atr_val) if atr_ready else None,
                                "bar_close_price": float(row["signal_price"]),
                            },
                        )
                    )
                    latest_observed_signal = ts if latest_observed_signal is None else max(latest_observed_signal, ts)

        if preview_enabled and not bars15.empty:
            preview_df = preview_mod.build_preview_minutes(minute_df, hour_df, bars15)
            preview_first_df = preview_mod.first_preview_rows(asset, symbol, preview_df)
            if not preview_first_df.empty:
                preview_first_df = preview_first_df[(preview_first_df["preview_ts"] >= cutoff) & (preview_first_df["preview_ts"] <= now_ts)].copy()
                for _, row in preview_first_df.iterrows():
                    preview_ts = pd.to_datetime(row["preview_ts"], utc=True)
                    bucket_start = pd.to_datetime(row["bucket_start"], utc=True)
                    side = Side.LONG if int(row["preview_dir"]) > 0 else Side.SHORT
                    atr_val = row["preview_atr14"]
                    atr_ready = pd.notna(atr_val) and float(atr_val) > 0
                    signals.append(
                        AlphaSignal(
                            signal_id=adapter._signal_id(symbol=symbol, ts=preview_ts, side=side, mode="preview"),
                            timestamp=preview_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                            symbol=symbol,
                            side=side,
                            signal_price=float(row["preview_price"]),
                            alpha_name="rank32b_slope_floor_continuation",
                            alpha_version="canary_preview_v2",
                            metadata={
                                "asset": asset,
                                "variant": str(signal_cfg.get("variant", "ema_cross_plus_slope_floor")),
                                "signal_mode": "preview_unclosed15m",
                                "bucket_start": bucket_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                "bucket_close_at": (bucket_start + pd.Timedelta(minutes=15)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                "first_seen_at": preview_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                "expired_at": None,
                                "confirmed_at_close": None,
                                "official_confirmed_at": None,
                                "entry_reference": "immediate_market",
                                "signal_confirmed_at_override": preview_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                "entry_delay_minutes": 0,
                                "fast_slope": float(row["preview_fast_slope"]) if pd.notna(row["preview_fast_slope"]) else None,
                                "slow_slope": float(row["preview_slow_slope"]) if pd.notna(row["preview_slow_slope"]) else None,
                                "spread_mid": None,
                                "slope_strength": float(row["preview_slope_strength"]) if pd.notna(row["preview_slope_strength"]) else None,
                                "atr_ready": bool(atr_ready),
                                "atr14": float(atr_val) if atr_ready else None,
                                "bar_close_price": float(row["preview_price"]),
                            },
                        )
                    )
                    latest_observed_signal = preview_ts if latest_observed_signal is None else max(latest_observed_signal, preview_ts)

    signals.sort(key=lambda sig: (sig.timestamp, sig.symbol))
    latest_signal_utc = signals[-1].timestamp if signals else None
    latest_bar_utc = latest_bar.strftime("%Y-%m-%dT%H:%M:%SZ") if latest_bar is not None else None
    latest_observed_signal_utc = latest_observed_signal.strftime("%Y-%m-%dT%H:%M:%SZ") if latest_observed_signal is not None else None
    snapshot = type("SignalSnapshotCompat", (), {
        "signals": signals,
        "latest_bar_utc": latest_bar_utc,
        "latest_signal_utc": latest_signal_utc,
        "latest_observed_signal_utc": latest_observed_signal_utc,
    })()
    return snapshot, shadow_cfg, preview_enabled


def simulate_horizon(cfg: dict[str, Any], *, horizon_days: int, now_ts: pd.Timestamp) -> dict[str, Any]:
    paper_cfg = deepcopy(shadow_mod.load_shadow_cfg(cfg).get("paper", {}))
    if isinstance(paper_cfg.get("depth_v2"), dict):
        paper_cfg["depth_v2"]["enabled"] = False
    live_parity_cfg = depth_v2_mod.build_live_parity_cfg(paper_cfg)
    cache_cfg = live_parity_cfg.get("kline_1m_cache", {})
    bars_cache: dict[str, pd.DataFrame] = {}
    day_cache: dict[str, pd.DataFrame] = {}
    snapshot, shadow_cfg, preview_enabled = load_signal_snapshot(
        cfg,
        horizon_days=horizon_days,
        now_ts=now_ts,
        cache_cfg=cache_cfg,
        day_cache=day_cache,
    )
    signal_cfg = cfg.get("signal_adapter", {}) if isinstance(cfg.get("signal_adapter"), dict) else {}
    signal_lookback_days = max(0, int(signal_cfg.get("lookback_days", horizon_days)))
    signal_fetch_days = int(horizon_days) + signal_lookback_days
    refresh_tail_days = max(0, int(signal_cfg.get("refresh_tail_days", 2) or 2))
    warmup_days = max(signal_lookback_days, refresh_tail_days)
    asset_to_symbol = shadow_cfg["asset_to_symbol"]
    selection_phase6 = {
        "selection": shadow_cfg.get("selection", {}),
        "smallcap": {"enabled": False, "symbols": []},
        "max_new_signals_per_run": 0,
    }
    selected_signals, skipped_weaker_signals = phase6lib.select_signals_for_execution(snapshot.signals, selection_phase6)
    selected_rows = normalize_selected_rows(selected_signals)

    usable_rows = [row for row in selected_rows if shadow_mod.get_signal_entry_ts(row) is not None]
    usable_rows.sort(key=lambda row: (shadow_mod.get_signal_entry_ts(row), str(row.get("symbol") or "")))
    oldest_ts = min(shadow_mod.get_signal_entry_ts(row) for row in usable_rows if shadow_mod.get_signal_entry_ts(row) is not None)
    days_5m = max(3, int(math.ceil((now_ts - oldest_ts) / pd.Timedelta(days=1))) + 2) if usable_rows else max(3, horizon_days + 2)

    consumed: set[str] = set()
    active_positions: list[dict[str, Any]] = []
    paper_trades: list[dict[str, Any]] = []
    skipped_signals: list[dict[str, Any]] = []

    timeout_minutes = int(paper_cfg.get("timeout_15m", 8)) * 15

    for row in usable_rows:
        entry_ts = shadow_mod.get_signal_entry_ts(row)
        symbol = str(row.get("symbol") or "").upper()
        side = str(row.get("side") or "").lower()
        direction_sign = shadow_mod.get_signal_direction_sign(row)
        bar_key = str(row.get("bar_key") or depth_v2_mod.signal_bar_key(symbol, row.get("timestamp") or row.get("signal_confirmed_at"), int(live_parity_cfg.get("same_bar_minutes", 15))))

        active_positions = [pos for pos in active_positions if pos.get("active_until") and pos["active_until"] > entry_ts]

        if live_parity_cfg.get("same_bar_once", True) and bar_key in consumed:
            skipped_signals.append({
                "timestamp": row.get("timestamp"),
                "signal_confirmed_at": row.get("signal_confirmed_at"),
                "signal_id": row.get("signal_id"),
                "symbol": symbol,
                "side": side,
                "bar_key": bar_key,
                "reason": "same_bar_signal_already_consumed",
            })
            continue

        if live_parity_cfg.get("same_symbol_single_position", True) and any(str(pos.get("symbol") or "").upper() == symbol for pos in active_positions):
            skipped_signals.append({
                "timestamp": row.get("timestamp"),
                "signal_confirmed_at": row.get("signal_confirmed_at"),
                "signal_id": row.get("signal_id"),
                "symbol": symbol,
                "side": side,
                "bar_key": bar_key,
                "reason": "live_position_exists_for_symbol",
            })
            consumed.add(bar_key)
            continue

        if len(active_positions) >= int(paper_cfg.get("max_concurrent_positions", 1)):
            skipped_signals.append({
                "timestamp": row.get("timestamp"),
                "signal_confirmed_at": row.get("signal_confirmed_at"),
                "signal_id": row.get("signal_id"),
                "symbol": symbol,
                "side": side,
                "bar_key": bar_key,
                "reason": "paper_rejected_by_max_concurrent",
                "paper_active_positions": len(active_positions),
                "paper_max_concurrent_positions": int(paper_cfg.get("max_concurrent_positions", 1)),
            })
            consumed.add(bar_key)
            continue

        sub_df = get_symbol_bars_local_first(symbol, days=days_5m, cache=bars_cache)
        ts_array = sub_df["timestamp"].to_numpy(dtype="datetime64[ns]") if not sub_df.empty else []
        entry_res = shadow_mod.exec_mod.simulate_entry(
            sub_df,
            ts_array,
            entry_ts,
            direction_sign,
            entry_style=str(paper_cfg.get("entry_style", "taker")),
            entry_offset_bps=0.0,
            ttl_bars=int(paper_cfg.get("entry_ttl_5m_bars", shadow_mod.exec_mod.ENTRY_TTL_5M_BARS)),
        ) if not sub_df.empty else None

        if entry_res is None:
            paper_trades.append(
                {
                    "signal_id": row.get("signal_id"),
                    "symbol": symbol,
                    "side": row.get("side"),
                    "mode": ((row.get("metadata") if isinstance(row.get("metadata"), dict) else {}) or {}).get("signal_mode"),
                    "signal_ts": row.get("timestamp"),
                    "signal_confirmed_at": row.get("signal_confirmed_at"),
                    "bar_key": bar_key,
                    "status": "entry_pending",
                    "paper_trade_state": "entry_pending",
                    "paper_effective_net_ret": 0.0,
                    "paper_effective_gross_ret": 0.0,
                }
            )
            consumed.add(bar_key)
            continue

        fill_ts = shadow_mod.parse_ts(entry_res.get("fill_ts")) or entry_ts
        minute_df = get_trade_minute_window(symbol, entry_ts=fill_ts, timeout_minutes=timeout_minutes, cache_cfg=cache_cfg, day_cache=day_cache)
        if minute_df.empty:
            exit_res = shadow_mod.simulate_exit_5m_fallback(sub_df, int(entry_res["fill_idx"]), float(entry_res["fill_px"]), direction_sign, shadow_mod.get_signal_atr(row), paper_cfg)
        else:
            exit_res = depth_v2_mod.simulate_exit_on_minute_bars(
                minute_df,
                entry_ts=fill_ts,
                entry_price=float(entry_res.get("fill_px")),
                position_side=side,
                atr_value=shadow_mod.get_signal_atr(row),
                paper_cfg=paper_cfg,
                now_ts=fill_ts + pd.Timedelta(minutes=timeout_minutes + 1),
                entry_fee_bps=float(shadow_mod.exec_mod.TAKER_FEE_BPS),
                exit_fee_bps=float(shadow_mod.exec_mod.TAKER_FEE_BPS),
            )

        trade_row = {
            "signal_id": row.get("signal_id"),
            "symbol": symbol,
            "side": row.get("side"),
            "mode": ((row.get("metadata") if isinstance(row.get("metadata"), dict) else {}) or {}).get("signal_mode"),
            "signal_ts": row.get("timestamp"),
            "signal_confirmed_at": row.get("signal_confirmed_at"),
            "bar_key": bar_key,
            "entry_ts": shadow_mod.iso(fill_ts),
            "entry_price": float(entry_res.get("fill_px")),
            "entry_fee_bps": float(entry_res.get("entry_fee_bps", shadow_mod.exec_mod.TAKER_FEE_BPS)),
            "entry_maker": int(entry_res.get("entry_maker", 0)),
            "paper_trade_state": str(exit_res.get("status") or "unknown"),
            "status": str(exit_res.get("mark_status") or exit_res.get("status") or "unknown"),
            "exit_ts": shadow_mod.iso(exit_res.get("exit_ts")),
            "exit_price": exit_res.get("exit_price"),
            "exit_reason": exit_res.get("exit_reason"),
            "mark_ts": shadow_mod.iso(exit_res.get("mark_ts")),
            "mark_price": exit_res.get("mark_price"),
            "gross_ret": exit_res.get("gross_ret"),
            "net_ret": exit_res.get("net_ret"),
            "mark_gross_ret": exit_res.get("mark_gross_ret"),
            "mark_net_ret": exit_res.get("mark_net_ret"),
            "paper_effective_gross_ret": exit_res.get("gross_ret") if exit_res.get("status") == "closed" else exit_res.get("mark_gross_ret", 0.0),
            "paper_effective_net_ret": exit_res.get("net_ret") if exit_res.get("status") == "closed" else exit_res.get("mark_net_ret", 0.0),
            "hold_minutes": int(exit_res.get("hold_minutes", 0)),
            "target_hit": int(exit_res.get("target_hit", 0)),
            "stop_hit": int(exit_res.get("stop_hit", 0)),
            "timeout_hit": int(exit_res.get("timeout_hit", 0)),
            "same_bar_conflict": int(exit_res.get("same_bar_conflict", 0)),
            "barrier_type": exit_res.get("barrier_type"),
            "atr14": shadow_mod.get_signal_atr(row),
            "tp_atr_mult": float(paper_cfg.get("tp_atr_mult", 1.75)),
            "sl_atr_mult": float(paper_cfg.get("sl_atr_mult", 1.0)),
            "timeout_15m": int(paper_cfg.get("timeout_15m", 8)),
            "max_concurrent_positions": int(paper_cfg.get("max_concurrent_positions", 1)),
            "exit_monitor_interval_minutes": int(live_parity_cfg.get("exit_check_interval_minutes", 1)),
        }
        paper_trades.append(trade_row)
        trade_end_ts = shadow_mod.parse_ts(trade_row.get("exit_ts")) or shadow_mod.parse_ts(trade_row.get("mark_ts")) or fill_ts
        active_positions.append({"symbol": symbol, "active_until": trade_end_ts})
        active_positions.sort(key=lambda pos: (pos.get("active_until") or fill_ts, pos.get("symbol") or ""))
        consumed.add(bar_key)

    closed_trades = [row for row in paper_trades if row.get("paper_trade_state") == "closed"]
    open_positions = [row for row in paper_trades if row.get("paper_trade_state") == "open"]
    realized_rets = [float(row.get("net_ret", 0.0)) for row in closed_trades if row.get("net_ret") is not None]
    effective_rets = [float(row.get("paper_effective_net_ret", 0.0)) for row in paper_trades if row.get("paper_effective_net_ret") is not None]

    def total_return(vals: list[float]) -> float:
        acc = 1.0
        for val in vals:
            acc *= 1.0 + float(val)
        return acc - 1.0

    default_notional, notional_by_symbol = load_live_like_notional(cfg, asset_to_symbol)
    metrics = compute_metrics(paper_trades, default_notional=default_notional, notional_by_symbol=notional_by_symbol)

    return {
        "horizon_days": horizon_days,
        "signal_generation_mode": "preview_live_like" if preview_enabled else "official_close_only",
        "signal_lookback_days": signal_lookback_days,
        "signal_fetch_days": signal_fetch_days,
        "warmup_history_days": warmup_days,
        "warmup_audit_status": "fixed_2026-04-07",
        "tp_atr_mult": float(paper_cfg.get("tp_atr_mult", 1.75)),
        "sl_atr_mult": float(paper_cfg.get("sl_atr_mult", 1.0)),
        "timeout_15m": int(paper_cfg.get("timeout_15m", 8)),
        "latest_bar_utc": snapshot.latest_bar_utc,
        "latest_signal_utc": snapshot.latest_signal_utc,
        "latest_observed_signal_utc": snapshot.latest_observed_signal_utc,
        "signals_total": len(snapshot.signals),
        "selected_winners": len(selected_rows),
        "skipped_weaker_signals": len(skipped_weaker_signals),
        "paper_summary": {
            "paper_trades": len(paper_trades),
            "paper_closed_trades": len(closed_trades),
            "paper_open_positions": len(open_positions),
            "paper_skipped_by_max_concurrent": len([row for row in skipped_signals if row.get("reason") == "paper_rejected_by_max_concurrent"]),
            "paper_rejected_same_symbol_open": len([row for row in skipped_signals if row.get("reason") == "live_position_exists_for_symbol"]),
            "paper_rejected_same_bar_consumed": len([row for row in skipped_signals if row.get("reason") == "same_bar_signal_already_consumed"]),
            "paper_realized_total_return": total_return(realized_rets),
            "paper_marked_total_return": total_return(effective_rets),
        },
        "metrics": metrics,
        "paper_trades": paper_trades,
        "notional_by_symbol": notional_by_symbol,
        "default_notional_usdt": default_notional,
        "used_now_utc": now_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def build_trade_frame(trades: list[dict[str, Any]], *, default_notional: float, notional_by_symbol: dict[str, float]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for row in trades:
        state = str(row.get("paper_trade_state") or "")
        if state not in {"open", "closed"}:
            continue
        symbol = str(row.get("symbol") or "").upper()
        effective_ret = float(row.get("paper_effective_net_ret") or 0.0)
        trade_time = trade_ts(row)
        rows.append(
            {
                **row,
                "symbol": symbol,
                "trade_ts": trade_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "notional_usdt": float(notional_by_symbol.get(symbol, default_notional)),
                "live_like_pnl_usdt": float(notional_by_symbol.get(symbol, default_notional)) * effective_ret,
                "effective_net_ret": effective_ret,
                "month": trade_time.tz_convert(None).to_period("M").strftime("%Y-%m"),
            }
        )
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values(["trade_ts", "symbol"]).reset_index(drop=True)


def trade_sharpe(values: list[float]) -> float | None:
    vals = [float(v) for v in values if v is not None and math.isfinite(float(v))]
    if len(vals) < 5:
        return None
    mean = sum(vals) / len(vals)
    var = sum((x - mean) ** 2 for x in vals) / len(vals)
    std = math.sqrt(var)
    if std <= 0:
        return None
    return float((mean / std) * math.sqrt(len(vals)))


def build_monthly_summary(df: pd.DataFrame) -> list[dict[str, Any]]:
    if df.empty:
        return []
    out: list[dict[str, Any]] = []
    cum = 0.0
    for month, grp in df.groupby("month", sort=True):
        pnl = float(grp["live_like_pnl_usdt"].sum())
        cum += pnl
        rets = [float(x) for x in grp["effective_net_ret"].tolist()]
        out.append(
            {
                "month": str(month),
                "trade_count": int(len(grp)),
                "pnl_usdt": pnl,
                "cum_pnl_usdt": cum,
                "win_rate": float((grp["effective_net_ret"] > 0).mean()) if len(grp) else None,
                "avg_net_ret": float(grp["effective_net_ret"].mean()) if len(grp) else None,
                "trade_sharpe": trade_sharpe(rets),
            }
        )
    return out


def save_trade_ledgers(result: dict[str, Any]) -> None:
    ensure_dir(LEDGER_DIR)
    days = int(result["horizon_days"])
    json_path = LEDGER_DIR / f"paper_trades_{days}d.json"
    csv_path = LEDGER_DIR / f"paper_trades_{days}d.csv"
    monthly_json_path = LEDGER_DIR / f"monthly_summary_{days}d.json"
    monthly_csv_path = LEDGER_DIR / f"monthly_summary_{days}d.csv"
    trades = result.get("paper_trades") or []
    json_path.write_text(json.dumps(trades, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    trade_df = build_trade_frame(
        trades,
        default_notional=float(result.get("default_notional_usdt") or 100.0),
        notional_by_symbol=result.get("notional_by_symbol") or {},
    )
    if trade_df.empty:
        pd.DataFrame().to_csv(csv_path, index=False)
        pd.DataFrame().to_csv(monthly_csv_path, index=False)
        monthly_json_path.write_text("[]\n", encoding="utf-8")
        return
    trade_df.to_csv(csv_path, index=False)
    monthly = build_monthly_summary(trade_df)
    pd.DataFrame(monthly).to_csv(monthly_csv_path, index=False)
    monthly_json_path.write_text(json.dumps(monthly, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def render_markdown(results: list[dict[str, Any]]) -> str:
    lines = [
        "# rank32b global shadow live-like backtest",
        "",
        "口径：global strongest-only；入场按历史 5m bar simulate_entry，出场按 1m K 线逐分钟回放；USDT PnL 用 live-like 100U/40U 仓位换算。",
        "",
    ]
    for item in results:
        s = item["paper_summary"]
        m = item["metrics"]
        lines.extend(
            [
                f"## Horizon: {item['horizon_days']} days",
                f"- signal_generation_mode: {item.get('signal_generation_mode', 'unknown')}",
                f"- exit_params: TP {float(item.get('tp_atr_mult', 1.75)):.2f} ATR | SL {float(item.get('sl_atr_mult', 1.0)):.2f} ATR | timeout {int(item.get('timeout_15m', 8)) * 15}m",
                f"- selected_winners: {item['selected_winners']}",
                f"- paper_trades: {s['paper_trades']} | closed: {s['paper_closed_trades']} | open: {s['paper_open_positions']}",
                f"- skipped_by_max_concurrent: {s['paper_skipped_by_max_concurrent']} | skipped_same_symbol: {s['paper_rejected_same_symbol_open']} | skipped_same_bar: {s['paper_rejected_same_bar_consumed']}",
                f"- realized_return: {s['paper_realized_total_return']:.4f} | marked_return: {s['paper_marked_total_return']:.4f}",
                f"- live_like_pnl: {m['usdt_pnl_live_like']:.2f} | closed_pnl: {m['closed_usdt_pnl_live_like']:.2f} | mdd: {m['max_drawdown']:.4f}",
                f"- closed_win_rate: {m['closed_win_rate']:.4f}" if m.get("closed_win_rate") is not None else "- closed_win_rate: n/a",
                "",
            ]
        )
    return "\n".join(lines) + "\n"


def write_payload(path_json: Path, path_md: Path, *, cfg_path: Path, results: list[dict[str, Any]]) -> None:
    compact_results: list[dict[str, Any]] = []
    for item in results:
        compact_results.append({k: v for k, v in item.items() if k not in {"paper_trades", "notional_by_symbol", "default_notional_usdt"}})
    payload = {
        "generated_at_utc": pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ"),
        "config_path": str(cfg_path),
        "results": compact_results,
    }
    path_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    path_md.write_text(render_markdown(compact_results), encoding="utf-8")


def main() -> int:
    global OUT_DIR, DAY_1M_CACHE_DIR, LEDGER_DIR
    ap = argparse.ArgumentParser(description="Historical live-like backtest for rank32b global shadow")
    ap.add_argument("--config", default=str(CONFIG_PATH))
    ap.add_argument("--horizon-days", nargs="*", type=int, default=[10, 30, 60, 180, 365, 720])
    ap.add_argument("--out-dir", default=str(OUT_DIR))
    ap.add_argument("--tp-atr-mult", type=float, default=None)
    ap.add_argument("--sl-atr-mult", type=float, default=None)
    args = ap.parse_args()

    cfg_path = Path(args.config)
    cfg = load_cfg(cfg_path)
    out_dir = Path(args.out_dir)
    OUT_DIR = out_dir
    DAY_1M_CACHE_DIR = OUT_DIR / "day_1m_cache"
    LEDGER_DIR = OUT_DIR / "trade_ledgers"
    phase6 = cfg.setdefault("phase6", {})
    shadow_global = phase6.setdefault("shadow_global", {})
    paper_cfg = shadow_global.setdefault("paper", {})
    if args.tp_atr_mult is not None:
        paper_cfg["tp_atr_mult"] = float(args.tp_atr_mult)
    if args.sl_atr_mult is not None:
        paper_cfg["sl_atr_mult"] = float(args.sl_atr_mult)
    now_ts = pd.Timestamp.now(tz="UTC")
    ensure_dir(OUT_DIR)
    ensure_dir(DAY_1M_CACHE_DIR)
    ensure_dir(LEDGER_DIR)

    results: list[dict[str, Any]] = []
    json_path = OUT_DIR / "backtest_windows.json"
    md_path = OUT_DIR / "backtest_windows.md"
    for days in args.horizon_days:
        result = simulate_horizon(cfg, horizon_days=int(days), now_ts=now_ts)
        results.append(result)
        save_trade_ledgers(result)
        write_payload(json_path, md_path, cfg_path=cfg_path, results=results)
        print(json.dumps({"completed_horizon_days": int(days), "paper_trades": result.get("paper_summary", {}).get("paper_trades"), "live_like_pnl": result.get("metrics", {}).get("usdt_pnl_live_like")}, ensure_ascii=False), flush=True)

    payload = {
        "generated_at_utc": pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ"),
        "config_path": str(cfg_path),
        "results": [{k: v for k, v in item.items() if k not in {"paper_trades", "notional_by_symbol", "default_notional_usdt"}} for item in results],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
