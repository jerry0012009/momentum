#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.execution.canary32b.frmonitor_bridge import load_frmonitor_bridge  # noqa: E402
from run_manual_narrow_paper_lanes import (  # noqa: E402
    ASSET_TO_BINANCE,
    build_rank29_trades,
    build_rank29_trades_causal,
    build_rank29_trades_confirmed_lines,
    compute_rank29_gate_daily_flags,
    download_binance_bars,
    iso_z,
    load_rank29_gate_thresholds,
)

DEFAULT_CONFIG_PATH = ROOT / "config" / "execution" / "rank29_gate_live.yaml"
DEFAULT_ART_DIR = ROOT / "reports" / "artifacts" / "rank29_gate_live"
DEFAULT_SHADOW_VIEW_PATH = ROOT / "reports" / "artifacts" / "manual_narrow_paper_lanes" / "rank29_shadow_trade_view.csv"
DEFAULT_CORE3_STATE_PATH = ROOT / "reports" / "artifacts" / "rank32b_canary" / "phase6_state.json"

STATE_FILENAME = "rank29_gate_live_state.json"
STATUS_FILENAME = "rank29_gate_live_status.json"
ORDERS_FILENAME = "rank29_gate_live_recent_orders.json"
REJECTIONS_FILENAME = "rank29_gate_live_recent_rejections.json"
WARNINGS_FILENAME = "rank29_gate_live_warnings.json"
COMPARE_FILENAME = "rank29_gate_live_vs_shadow.csv"
HTML_FILENAME = "rank29_gate_live_report.html"

DEFAULT_WEEKLY_LOSS_LIMIT_USDT = 10.0
DEFAULT_SIGNAL_AGE_MINUTES = 4
DEFAULT_RECENT_SIGNAL_WINDOW_MINUTES = 60
DEFAULT_DESIRED_NOTIONAL_USDT = 100.0
DEFAULT_BAD_REGIME_WEIGHT = 0.25
DEFAULT_TAKER_FEE_BPS_PER_SIDE = 4.5
DEFAULT_HISTORY_DAYS = 150
DEFAULT_HOLD_BARS = 8
DEFAULT_BAR_MINUTES = 15
DEFAULT_DEFAULT_LEVERAGE = 1
RECENT_LIMIT = 80
STATE_MAX_SEEN = 4000
STATE_MAX_REJECTIONS = 400
STATE_MAX_WARNINGS = 400
STATE_MAX_ORDERS = 400
STATE_MAX_CLOSED = 400
STATE_MAX_LIVE = 50
UTC = timezone.utc


@dataclass(slots=True)
class SignalCandidate:
    signal_id: str
    asset: str
    symbol: str
    side: str
    entry_ts: datetime
    planned_exit_ts: datetime
    event_ts: datetime
    gate_low_trend_high_noise: bool
    exposure_weight: float
    trigger_tf: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "signal_id": self.signal_id,
            "asset": self.asset,
            "symbol": self.symbol,
            "side": self.side,
            "entry_ts": iso_dt(self.entry_ts),
            "planned_exit_ts": iso_dt(self.planned_exit_ts),
            "event_ts": iso_dt(self.event_ts),
            "gate_low_trend_high_noise": bool(self.gate_low_trend_high_noise),
            "exposure_weight": float(self.exposure_weight),
            "trigger_tf": self.trigger_tf,
        }


def utc_now() -> datetime:
    return datetime.now(UTC)


def iso_dt(value: datetime | str | pd.Timestamp | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        dt = parse_dt(value)
    else:
        dt = pd.to_datetime(value, utc=True).to_pydatetime()
    if dt is None:
        return None
    return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_dt(value: Any) -> datetime | None:
    if value is None or value == "":
        return None
    try:
        return pd.to_datetime(value, utc=True).to_pydatetime()
    except Exception:
        return None


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def save_json(path: Path, payload: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def sf(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def normalize_symbol(symbol: str) -> str:
    raw = str(symbol or "").upper()
    return raw if raw.endswith("USDT") else f"{raw}USDT"


def symbol_to_asset(symbol: str) -> str:
    pair = normalize_symbol(symbol)
    for asset, mapped in ASSET_TO_BINANCE.items():
        if normalize_symbol(mapped) == pair:
            return asset
    return pair.replace("USDT", "-USD")


def side_to_order_side(side: str) -> str:
    return "BUY" if str(side).lower() == "long" else "SELL"


def exit_order_side(side: str) -> str:
    return "SELL" if str(side).lower() == "long" else "BUY"


def hedge_position_side(side: str) -> str:
    return "LONG" if str(side).lower() == "long" else "SHORT"


def signal_id_for(asset: str, entry_ts: datetime, side: str) -> str:
    symbol = ASSET_TO_BINANCE[asset]
    return f"{symbol}|{iso_dt(entry_ts)}|{side.lower()}"


def week_start_utc(now_dt: datetime) -> datetime:
    base = now_dt.astimezone(UTC)
    return (base - timedelta(days=base.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)


def trim_list(rows: list[Any], limit: int) -> list[Any]:
    if len(rows) <= limit:
        return rows
    return rows[-limit:]


class Rank29GateLiveState:
    def __init__(self, raw: dict[str, Any] | None = None) -> None:
        raw = raw or {}
        self.seen_signal_ids: list[str] = list(raw.get("seen_signal_ids", []))
        self.live_positions: list[dict[str, Any]] = list(raw.get("live_positions", []))
        self.closed_trades: list[dict[str, Any]] = list(raw.get("closed_trades", []))
        self.recent_rejections: list[dict[str, Any]] = list(raw.get("recent_rejections", []))
        self.recent_warnings: list[dict[str, Any]] = list(raw.get("recent_warnings", []))
        self.recent_orders: list[dict[str, Any]] = list(raw.get("recent_orders", []))
        self.last_run_utc: str | None = raw.get("last_run_utc")

    def to_dict(self) -> dict[str, Any]:
        return {
            "seen_signal_ids": trim_list(self.seen_signal_ids, STATE_MAX_SEEN),
            "live_positions": trim_list(self.live_positions, STATE_MAX_LIVE),
            "closed_trades": trim_list(self.closed_trades, STATE_MAX_CLOSED),
            "recent_rejections": trim_list(self.recent_rejections, STATE_MAX_REJECTIONS),
            "recent_warnings": trim_list(self.recent_warnings, STATE_MAX_WARNINGS),
            "recent_orders": trim_list(self.recent_orders, STATE_MAX_ORDERS),
            "last_run_utc": self.last_run_utc,
        }


def load_state(path: Path) -> Rank29GateLiveState:
    return Rank29GateLiveState(load_json(path, {}))


def append_warning(state: Rank29GateLiveState, *, now_iso: str, message: str, payload: dict[str, Any] | None = None) -> None:
    state.recent_warnings.append({
        "timestamp": now_iso,
        "message": message,
        "payload": payload or {},
    })


def append_rejection(
    state: Rank29GateLiveState,
    *,
    now_iso: str,
    reason: str,
    signal: SignalCandidate,
    payload: dict[str, Any] | None = None,
) -> None:
    state.recent_rejections.append({
        "timestamp": now_iso,
        "reason": reason,
        "signal_id": signal.signal_id,
        "symbol": signal.symbol,
        "side": signal.side,
        "entry_ts": iso_dt(signal.entry_ts),
        "planned_exit_ts": iso_dt(signal.planned_exit_ts),
        "gate_low_trend_high_noise": bool(signal.gate_low_trend_high_noise),
        "exposure_weight": float(signal.exposure_weight),
        "payload": payload or {},
    })


def append_order(state: Rank29GateLiveState, row: dict[str, Any]) -> None:
    state.recent_orders.append(row)


def prune_historical_signal_noise(state: Rank29GateLiveState, *, recent_cutoff_dt: datetime) -> None:
    kept_rejections: list[dict[str, Any]] = []
    for row in state.recent_rejections:
        reason = str(row.get("reason") or "")
        entry_dt = parse_dt(row.get("entry_ts"))
        if reason == "signal_expired" and entry_dt is not None and entry_dt < recent_cutoff_dt:
            continue
        kept_rejections.append(row)
    state.recent_rejections = kept_rejections


def weekly_closed_pnl_usdt(closed_trades: list[dict[str, Any]], now_dt: datetime) -> float:
    start = week_start_utc(now_dt)
    total = 0.0
    for row in closed_trades:
        exit_dt = parse_dt(row.get("exit_time"))
        if exit_dt is None or exit_dt < start:
            continue
        total += sf(row.get("net_pnl"), 0.0)
    return total


def build_signal_candidates(cfg: dict[str, Any]) -> list[SignalCandidate]:
    market_cfg = cfg.get("market", {})
    exec_cfg = cfg.get("execution", {})
    history_days = int(market_cfg.get("history_days", DEFAULT_HISTORY_DAYS))
    interval = str(market_cfg.get("interval", "15m"))
    hold_bars = int(exec_cfg.get("hold_bars", DEFAULT_HOLD_BARS))
    bar_minutes = int(market_cfg.get("bar_minutes", DEFAULT_BAR_MINUTES))
    bad_regime_weight = float(exec_cfg.get("bad_regime_weight", DEFAULT_BAD_REGIME_WEIGHT))
    signal_engine = str(exec_cfg.get("signal_engine", "hindsight_replay") or "hindsight_replay").strip().lower()
    replay_context_bars = int(exec_cfg.get("causal_replay_context_bars", 960) or 960)

    bars_cache: dict[str, pd.DataFrame] = {
        asset: download_binance_bars(symbol, interval=interval, days=history_days)
        for asset, symbol in ASSET_TO_BINANCE.items()
    }
    thresholds = load_rank29_gate_thresholds()
    gate_daily_flags = compute_rank29_gate_daily_flags(bars_cache, thresholds)
    gate_cols = [
        "effective_for_trade_day",
        "gate_low_trend_high_noise",
        "gate_trend_strength_20d_mtd_mean",
        "gate_noise_ratio_20d_mtd_mean",
    ]
    gate_daily_flags = gate_daily_flags[gate_cols].copy() if not gate_daily_flags.empty else pd.DataFrame(columns=gate_cols)

    signals: list[SignalCandidate] = []
    for asset, bars in bars_cache.items():
        if signal_engine == "causal_replay":
            trades = build_rank29_trades_causal(asset, bars, replay_context_bars=replay_context_bars)
        elif signal_engine == "confirmed_line_only":
            trades = build_rank29_trades_confirmed_lines(asset, bars)
        else:
            trades = build_rank29_trades(asset, bars)
        if trades.empty:
            continue
        trades = trades.copy()
        trades["entry_ts"] = pd.to_datetime(trades["entry_ts"], utc=True)
        trades["event_ts"] = pd.to_datetime(trades["event_ts"], utc=True)
        trades["trade_day_utc"] = trades["entry_ts"].dt.floor("D")
        if not gate_daily_flags.empty:
            trades = trades.merge(gate_daily_flags, left_on="trade_day_utc", right_on="effective_for_trade_day", how="left")
        else:
            trades["gate_low_trend_high_noise"] = 0
        trades["gate_low_trend_high_noise"] = trades["gate_low_trend_high_noise"].fillna(0).astype(int)
        trades["exposure_weight"] = trades["gate_low_trend_high_noise"].map(lambda x: bad_regime_weight if int(x) == 1 else 1.0)

        for row in trades.itertuples(index=False):
            entry_ts = pd.to_datetime(row.entry_ts, utc=True).to_pydatetime()
            signals.append(
                SignalCandidate(
                    signal_id=signal_id_for(asset, entry_ts, str(row.direction)),
                    asset=asset,
                    symbol=ASSET_TO_BINANCE[asset],
                    side=str(row.direction),
                    entry_ts=entry_ts,
                    planned_exit_ts=entry_ts + timedelta(minutes=bar_minutes * hold_bars),
                    event_ts=pd.to_datetime(row.event_ts, utc=True).to_pydatetime(),
                    gate_low_trend_high_noise=bool(int(getattr(row, "gate_low_trend_high_noise", 0) or 0)),
                    exposure_weight=float(getattr(row, "exposure_weight", 1.0) or 1.0),
                    trigger_tf=str(getattr(row, "trigger_tf", "")),
                )
            )
    signals.sort(key=lambda x: (x.entry_ts, x.symbol, x.side))
    return signals


def load_core3_busy_symbols(cfg: dict[str, Any], bridge: Any, own_live_symbols: set[str]) -> tuple[set[str], list[dict[str, Any]]]:
    conflict_cfg = cfg.get("conflict", {})
    busy: set[str] = set()
    warnings: list[dict[str, Any]] = []

    state_paths = conflict_cfg.get("higher_priority_state_paths") or [conflict_cfg.get("core3_state_path") or DEFAULT_CORE3_STATE_PATH]
    for raw_path in state_paths:
        if not raw_path:
            continue
        raw = load_json(Path(str(raw_path)), {})
        for bucket in ("pending_entries", "live_positions"):
            for row in raw.get(bucket, []) or []:
                symbol = normalize_symbol(str(row.get("symbol") or ""))
                if symbol:
                    busy.add(symbol)

    exchange_symbols = {
        normalize_symbol(s)
        for s in (
            conflict_cfg.get("higher_priority_enabled_symbols")
            or conflict_cfg.get("core3_enabled_symbols")
            or list(ASSET_TO_BINANCE.values())
        )
    }
    try:
        positions_raw = bridge.get_binance_perp_positions()
        rows = positions_raw if isinstance(positions_raw, list) else [positions_raw]
        for row in rows:
            if not isinstance(row, dict):
                continue
            symbol = normalize_symbol(str(row.get("symbol") or ""))
            if symbol not in exchange_symbols:
                continue
            amt = abs(sf(row.get("positionAmt"), 0.0))
            if amt <= 0:
                continue
            if symbol in own_live_symbols:
                continue
            busy.add(symbol)
            warnings.append(
                {
                    "message": "exchange reports external busy symbol on higher-priority universe",
                    "payload": {
                        "symbol": symbol,
                        "positionAmt": row.get("positionAmt"),
                        "entryPrice": row.get("entryPrice"),
                    },
                }
            )
    except Exception as exc:  # noqa: BLE001
        warnings.append({"message": "failed to query exchange positions for higher-priority conflict scan", "payload": {"error": str(exc)}})

    return busy, warnings


def estimate_fee_and_net(*, entry_price: float, exit_price: float, qty: float, gross_pnl: float, fee_bps_per_side: float) -> tuple[float, float]:
    avg_notional = qty * ((entry_price + exit_price) / 2.0)
    fee = avg_notional * (2.0 * fee_bps_per_side / 10000.0)
    return fee, gross_pnl - fee


def place_entry_order(
    *,
    bridge: Any,
    signal: SignalCandidate,
    desired_notional_usdt: float,
    fee_bps_per_side: float,
    default_leverage: int,
    now_iso: str,
    allow_live_orders: bool,
    state: Rank29GateLiveState,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    target_notional = desired_notional_usdt * float(signal.exposure_weight)
    try:
        bridge.set_binance_perp_leverage(signal.symbol, default_leverage)
    except Exception:
        pass

    qty_payload = bridge.derive_binance_qty_from_notional(signal.symbol, target_notional)
    client_order_id = f"r29g-{signal.symbol.lower()}-{now_iso.replace('-', '').replace(':', '').replace('T', '').replace('Z', '')}"[:36]
    preview = {
        "timestamp": now_iso,
        "order_role": "entry_preview",
        "signal_id": signal.signal_id,
        "symbol": signal.symbol,
        "side": signal.side,
        "exchange_side": side_to_order_side(signal.side),
        "desired_notional_usdt": round(target_notional, 6),
        "qty": qty_payload.get("quantity"),
        "last_price": qty_payload.get("last_price"),
        "gate_low_trend_high_noise": bool(signal.gate_low_trend_high_noise),
        "exposure_weight": float(signal.exposure_weight),
        "allow_live_orders": bool(allow_live_orders),
    }
    append_order(state, preview)
    if not allow_live_orders:
        return None, preview

    response = bridge.place_binance_perp_live_market_order(
        symbol=signal.symbol,
        side=side_to_order_side(signal.side),
        quantity=qty_payload["quantity"],
        reduce_only=None,
        position_side=hedge_position_side(signal.side),
        client_order_id=client_order_id,
    )
    avg_price = sf(response.get("avg_price") or response.get("price"), sf(qty_payload.get("last_price"), 0.0))
    executed_qty = sf(response.get("executed_qty") or response.get("quantity"), sf(qty_payload.get("quantity"), 0.0))
    live_position = {
        "signal_id": signal.signal_id,
        "asset": signal.asset,
        "symbol": signal.symbol,
        "side": signal.side,
        "entry_time": now_iso,
        "entry_signal_time": iso_dt(signal.entry_ts),
        "event_time": iso_dt(signal.event_ts),
        "planned_exit_time": iso_dt(signal.planned_exit_ts),
        "entry_price": avg_price,
        "qty": executed_qty,
        "desired_notional_usdt": round(target_notional, 6),
        "gate_low_trend_high_noise": bool(signal.gate_low_trend_high_noise),
        "exposure_weight": float(signal.exposure_weight),
        "trigger_tf": signal.trigger_tf,
        "entry_order_id": response.get("order_id"),
        "entry_client_order_id": response.get("client_order_id"),
        "fee_bps_per_side": float(fee_bps_per_side),
    }
    append_order(
        state,
        {
            "timestamp": now_iso,
            "order_role": "entry",
            "signal_id": signal.signal_id,
            "symbol": signal.symbol,
            "side": signal.side,
            "exchange_side": side_to_order_side(signal.side),
            "price": avg_price,
            "qty": executed_qty,
            "status": response.get("status"),
            "exchange_order_id": response.get("order_id"),
            "client_order_id": response.get("client_order_id"),
            "desired_notional_usdt": round(target_notional, 6),
            "gate_low_trend_high_noise": bool(signal.gate_low_trend_high_noise),
            "exposure_weight": float(signal.exposure_weight),
        },
    )
    return live_position, preview


def maybe_exit_due_positions(
    *,
    bridge: Any,
    state: Rank29GateLiveState,
    now_dt: datetime,
    now_iso: str,
    allow_live_orders: bool,
) -> None:
    keep: list[dict[str, Any]] = []
    for row in state.live_positions:
        planned_exit_dt = parse_dt(row.get("planned_exit_time"))
        if planned_exit_dt is None or now_dt < planned_exit_dt:
            keep.append(row)
            continue

        symbol = normalize_symbol(str(row.get("symbol") or ""))
        side = str(row.get("side") or "")
        qty = sf(row.get("qty"), 0.0)
        if qty <= 0:
            append_warning(state, now_iso=now_iso, message="live position missing qty; dropping from state", payload={"row": row})
            continue

        preview = {
            "timestamp": now_iso,
            "order_role": "exit_preview",
            "signal_id": row.get("signal_id"),
            "symbol": symbol,
            "side": side,
            "exchange_side": exit_order_side(side),
            "qty": qty,
            "allow_live_orders": bool(allow_live_orders),
            "exit_reason": "timeout_8bars",
        }
        append_order(state, preview)
        if not allow_live_orders:
            keep.append(row)
            continue

        try:
            response = bridge.place_binance_perp_live_market_order(
                symbol=symbol,
                side=exit_order_side(side),
                quantity=qty,
                reduce_only=None,
                position_side=hedge_position_side(side),
                client_order_id=f"r29x-{symbol.lower()}-{now_iso.replace('-', '').replace(':', '').replace('T', '').replace('Z', '')}"[:36],
            )
        except Exception as exc:  # noqa: BLE001
            append_warning(
                state,
                now_iso=now_iso,
                message="exit order failed; keeping position in state",
                payload={"signal_id": row.get("signal_id"), "symbol": symbol, "error": str(exc)},
            )
            keep.append(row)
            continue

        exit_price = sf(response.get("avg_price") or response.get("price"), 0.0)
        executed_qty = sf(response.get("executed_qty") or response.get("quantity"), qty)
        entry_price = sf(row.get("entry_price"), 0.0)
        gross_pnl = (exit_price - entry_price) * executed_qty if side.lower() == "long" else (entry_price - exit_price) * executed_qty
        fee, net_pnl = estimate_fee_and_net(
            entry_price=entry_price,
            exit_price=exit_price,
            qty=executed_qty,
            gross_pnl=gross_pnl,
            fee_bps_per_side=sf(row.get("fee_bps_per_side"), DEFAULT_TAKER_FEE_BPS_PER_SIDE),
        )
        holding_minutes = 0.0
        entry_dt = parse_dt(row.get("entry_time"))
        if entry_dt is not None:
            holding_minutes = (now_dt - entry_dt).total_seconds() / 60.0

        append_order(
            state,
            {
                "timestamp": now_iso,
                "order_role": "exit",
                "signal_id": row.get("signal_id"),
                "symbol": symbol,
                "side": side,
                "exchange_side": exit_order_side(side),
                "price": exit_price,
                "qty": executed_qty,
                "status": response.get("status"),
                "exchange_order_id": response.get("order_id"),
                "client_order_id": response.get("client_order_id"),
                "exit_reason": "timeout_8bars",
            },
        )
        state.closed_trades.append(
            {
                "signal_id": row.get("signal_id"),
                "asset": row.get("asset") or symbol_to_asset(symbol),
                "symbol": symbol,
                "side": side,
                "entry_time": row.get("entry_time"),
                "entry_signal_time": row.get("entry_signal_time"),
                "event_time": row.get("event_time"),
                "exit_time": now_iso,
                "planned_exit_time": row.get("planned_exit_time"),
                "holding_minutes": holding_minutes,
                "entry_price": entry_price,
                "exit_price": exit_price,
                "qty": executed_qty,
                "desired_notional_usdt": row.get("desired_notional_usdt"),
                "gross_pnl": gross_pnl,
                "fee": fee,
                "net_pnl": net_pnl,
                "fee_bps_per_side": row.get("fee_bps_per_side"),
                "gate_low_trend_high_noise": bool(row.get("gate_low_trend_high_noise")),
                "exposure_weight": row.get("exposure_weight"),
                "exit_reason": "timeout_8bars",
                "entry_order_id": row.get("entry_order_id"),
                "entry_client_order_id": row.get("entry_client_order_id"),
                "exit_order_id": response.get("order_id"),
                "exit_client_order_id": response.get("client_order_id"),
            }
        )
    state.live_positions = keep


def write_compare_artifacts(cfg: dict[str, Any], art_dir: Path, state: Rank29GateLiveState) -> None:
    compare_path = art_dir / COMPARE_FILENAME
    html_path = art_dir / HTML_FILENAME
    shadow_path = Path(cfg.get("artifacts", {}).get("shadow_trade_view_path") or DEFAULT_SHADOW_VIEW_PATH)

    live_rows = pd.DataFrame(state.closed_trades)
    if live_rows.empty:
        compare_path.write_text(
            "signal_id,symbol,side,live_entry_time,live_exit_time,live_net_pnl_usdt,shadow_proxy_net_pnl_usdt,delta_vs_shadow_usdt\n",
            encoding="utf-8",
        )
        html_path.write_text(
            "<html><body><h1>rank29 gate live</h1><p>No closed trades yet.</p></body></html>",
            encoding="utf-8",
        )
        return

    live_rows = live_rows.copy()
    live_rows["signal_id"] = live_rows["signal_id"].astype(str)
    live_rows["live_net_pnl_usdt"] = live_rows["net_pnl"].astype(float)
    live_rows["live_gross_pnl_usdt"] = live_rows["gross_pnl"].astype(float)
    live_rows["live_entry_time"] = live_rows["entry_time"].astype(str)
    live_rows["live_exit_time"] = live_rows["exit_time"].astype(str)

    if shadow_path.exists():
        shadow = pd.read_csv(shadow_path)
        shadow = shadow[shadow["candidate_id"] == "rank29_trendline_breakout_gate_shadow"].copy()
        if not shadow.empty:
            shadow["entry_ts"] = pd.to_datetime(shadow["entry_ts"], utc=True)
            shadow["signal_id"] = shadow.apply(
                lambda row: signal_id_for(str(row["asset"]), pd.to_datetime(row["entry_ts"], utc=True).to_pydatetime(), str(row.get("direction") or row.get("side") or "long")),
                axis=1,
            )
            desired_notional = float(cfg.get("execution", {}).get("desired_notional_usdt", DEFAULT_DESIRED_NOTIONAL_USDT))
            shadow["shadow_proxy_net_pnl_usdt"] = shadow["net_ret"].astype(float) * desired_notional
            merged = live_rows.merge(
                shadow[
                    [
                        "signal_id",
                        "entry_ts",
                        "exit_ts",
                        "net_ret",
                        "baseline_net_ret",
                        "gate_low_trend_high_noise",
                        "exposure_weight",
                        "shadow_proxy_net_pnl_usdt",
                    ]
                ],
                on="signal_id",
                how="left",
            )
        else:
            merged = live_rows.copy()
            merged["shadow_proxy_net_pnl_usdt"] = math.nan
    else:
        merged = live_rows.copy()
        merged["shadow_proxy_net_pnl_usdt"] = math.nan

    merged["delta_vs_shadow_usdt"] = merged["live_net_pnl_usdt"] - merged["shadow_proxy_net_pnl_usdt"]
    merged.sort_values(["live_exit_time", "signal_id"], inplace=True)
    merged.to_csv(compare_path, index=False)

    total_live = float(merged["live_net_pnl_usdt"].fillna(0.0).sum())
    total_shadow = float(merged["shadow_proxy_net_pnl_usdt"].fillna(0.0).sum())
    total_delta = float(merged["delta_vs_shadow_usdt"].fillna(0.0).sum())
    table_html = merged.tail(30).to_html(index=False, justify="left")
    html = f"""
<html>
  <head>
    <meta charset=\"utf-8\" />
    <title>rank29 gate live report</title>
    <style>
      body {{ font-family: sans-serif; padding: 20px; }}
      table {{ border-collapse: collapse; width: 100%; }}
      th, td {{ border: 1px solid #ddd; padding: 6px 8px; font-size: 13px; }}
      th {{ background: #f5f5f5; text-align: left; }}
      .metric {{ margin: 4px 0; }}
    </style>
  </head>
  <body>
    <h1>rank29 gate live vs shadow</h1>
    <div class=\"metric\">closed trades: {len(merged)}</div>
    <div class=\"metric\">live net pnl: {total_live:.4f} USDT</div>
    <div class=\"metric\">shadow proxy pnl: {total_shadow:.4f} USDT</div>
    <div class=\"metric\">delta vs shadow: {total_delta:.4f} USDT</div>
    {table_html}
  </body>
</html>
"""
    html_path.write_text(html, encoding="utf-8")


def refresh_local_dashboards() -> None:
    builder_paths = [
        ROOT / "scripts" / "build_rank29_gate_live_dashboard.py",
        ROOT / "scripts" / "build_rank29_monitoring_hub.py",
    ]
    for builder in builder_paths:
        try:
            subprocess.run([sys.executable, str(builder)], cwd=str(ROOT), check=True, capture_output=True, text=True)
        except Exception:
            continue


def build_status_payload(
    *,
    cfg: dict[str, Any],
    now_iso: str,
    allow_live_orders: bool,
    state: Rank29GateLiveState,
    core3_busy_symbols: set[str],
    signals: list[SignalCandidate],
    recent_signal_window_minutes: int,
    historical_backfill_skipped: int,
    fresh_signal_expired: int,
) -> dict[str, Any]:
    exec_cfg = cfg.get("execution", {})
    weekly_pnl = weekly_closed_pnl_usdt(state.closed_trades, parse_dt(now_iso) or utc_now())
    weekly_limit = float(cfg.get("risk", {}).get("weekly_loss_limit_usdt", DEFAULT_WEEKLY_LOSS_LIMIT_USDT))
    return {
        "generated_at_utc": now_iso,
        "runner": "rank29_gate_live_100u",
        "allow_live_orders": bool(allow_live_orders),
        "desired_notional_usdt": float(exec_cfg.get("desired_notional_usdt", DEFAULT_DESIRED_NOTIONAL_USDT)),
        "bad_regime_weight": float(exec_cfg.get("bad_regime_weight", DEFAULT_BAD_REGIME_WEIGHT)),
        "signal_engine": str(exec_cfg.get("signal_engine", "hindsight_replay") or "hindsight_replay"),
        "causal_replay_context_bars": int(exec_cfg.get("causal_replay_context_bars", 960) or 960),
        "weekly_closed_pnl_usdt": weekly_pnl,
        "weekly_loss_limit_usdt": weekly_limit,
        "weekly_stop_active": bool(weekly_pnl <= -abs(weekly_limit)),
        "recent_signal_window_minutes": int(recent_signal_window_minutes),
        "historical_backfill_skipped_this_run": int(historical_backfill_skipped),
        "fresh_signal_expired_this_run": int(fresh_signal_expired),
        "core3_busy_symbols": sorted(core3_busy_symbols),
        "live_symbols": sorted({normalize_symbol(str(row.get('symbol') or '')) for row in state.live_positions if row.get('symbol')}),
        "live_positions": len(state.live_positions),
        "closed_trades": len(state.closed_trades),
        "seen_signal_ids": len(state.seen_signal_ids),
        "candidate_signals_scanned": len(signals),
        "recent_orders": trim_list(state.recent_orders, 20),
        "recent_rejections": trim_list(state.recent_rejections, 20),
        "recent_warnings": trim_list(state.recent_warnings, 20),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run rank29 gate live 100u lane")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--allow-live", action="store_true", help="Actually place/cancel live orders")
    args = parser.parse_args()

    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    art_dir = ensure_dir(Path(cfg.get("artifacts", {}).get("root") or DEFAULT_ART_DIR))
    state_path = art_dir / STATE_FILENAME
    status_path = art_dir / STATUS_FILENAME
    orders_path = art_dir / ORDERS_FILENAME
    rejections_path = art_dir / REJECTIONS_FILENAME
    warnings_path = art_dir / WARNINGS_FILENAME

    now_dt = utc_now()
    now_iso = iso_dt(now_dt) or now_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    state = load_state(state_path)
    state.last_run_utc = now_iso

    phase3 = cfg.get("phase3", {})
    bridge = load_frmonitor_bridge(
        phase3["fr_monitor_root"],
        local_private_path=phase3.get("local_private_path"),
    )

    maybe_exit_due_positions(
        bridge=bridge,
        state=state,
        now_dt=now_dt,
        now_iso=now_iso,
        allow_live_orders=bool(args.allow_live),
    )

    own_live_symbols = {normalize_symbol(str(row.get("symbol") or "")) for row in state.live_positions if row.get("symbol")}
    core3_busy_symbols, conflict_warnings = load_core3_busy_symbols(cfg, bridge, own_live_symbols)
    for warning in conflict_warnings:
        append_warning(state, now_iso=now_iso, message=warning["message"], payload=warning.get("payload") or {})

    signals = build_signal_candidates(cfg)
    signal_age_minutes = int(cfg.get("execution", {}).get("max_signal_age_minutes", DEFAULT_SIGNAL_AGE_MINUTES))
    recent_signal_window_minutes = int(cfg.get("execution", {}).get("recent_signal_window_minutes", DEFAULT_RECENT_SIGNAL_WINDOW_MINUTES))
    recent_signal_window_minutes = max(signal_age_minutes + 1, recent_signal_window_minutes)
    recent_cutoff_dt = now_dt - timedelta(minutes=recent_signal_window_minutes)
    desired_notional_usdt = float(cfg.get("execution", {}).get("desired_notional_usdt", DEFAULT_DESIRED_NOTIONAL_USDT))
    default_leverage = int(cfg.get("execution", {}).get("default_leverage", DEFAULT_DEFAULT_LEVERAGE))
    fee_bps_per_side = float(cfg.get("execution", {}).get("taker_fee_bps_per_side", DEFAULT_TAKER_FEE_BPS_PER_SIDE))
    weekly_limit = float(cfg.get("risk", {}).get("weekly_loss_limit_usdt", DEFAULT_WEEKLY_LOSS_LIMIT_USDT))
    weekly_stop_active = weekly_closed_pnl_usdt(state.closed_trades, now_dt) <= -abs(weekly_limit)
    prune_historical_signal_noise(state, recent_cutoff_dt=recent_cutoff_dt)

    historical_backfill_skipped = 0
    fresh_signal_expired = 0
    seen = set(state.seen_signal_ids)
    own_live_symbols = {normalize_symbol(str(row.get("symbol") or "")) for row in state.live_positions if row.get("symbol")}
    recent_signals = [signal for signal in signals if recent_cutoff_dt <= signal.entry_ts <= now_dt]
    historical_backfill_skipped = sum(1 for signal in signals if signal.signal_id not in seen and signal.entry_ts < recent_cutoff_dt)

    for signal in recent_signals:
        if signal.signal_id in seen:
            continue
        age_minutes = (now_dt - signal.entry_ts).total_seconds() / 60.0
        if age_minutes > signal_age_minutes:
            append_rejection(
                state,
                now_iso=now_iso,
                reason="fresh_signal_expired",
                signal=signal,
                payload={"age_minutes": round(age_minutes, 3), "recent_signal_window_minutes": recent_signal_window_minutes},
            )
            fresh_signal_expired += 1
            state.seen_signal_ids.append(signal.signal_id)
            seen.add(signal.signal_id)
            continue
        if weekly_stop_active:
            append_rejection(
                state,
                now_iso=now_iso,
                reason="weekly_loss_limit_reached",
                signal=signal,
                payload={"weekly_loss_limit_usdt": weekly_limit},
            )
            state.seen_signal_ids.append(signal.signal_id)
            seen.add(signal.signal_id)
            continue
        if signal.symbol in own_live_symbols:
            append_rejection(state, now_iso=now_iso, reason="own_lane_symbol_busy", signal=signal)
            state.seen_signal_ids.append(signal.signal_id)
            seen.add(signal.signal_id)
            continue
        if signal.symbol in core3_busy_symbols:
            append_rejection(state, now_iso=now_iso, reason="core3_symbol_conflict_skip", signal=signal)
            state.seen_signal_ids.append(signal.signal_id)
            seen.add(signal.signal_id)
            continue

        try:
            live_position, _preview = place_entry_order(
                bridge=bridge,
                signal=signal,
                desired_notional_usdt=desired_notional_usdt,
                fee_bps_per_side=fee_bps_per_side,
                default_leverage=default_leverage,
                now_iso=now_iso,
                allow_live_orders=bool(args.allow_live),
                state=state,
            )
        except Exception as exc:  # noqa: BLE001
            append_warning(
                state,
                now_iso=now_iso,
                message="entry order failed; signal consumed to avoid duplicate live fill",
                payload={"signal_id": signal.signal_id, "symbol": signal.symbol, "error": str(exc)},
            )
            state.seen_signal_ids.append(signal.signal_id)
            seen.add(signal.signal_id)
            continue

        if live_position is not None:
            state.live_positions.append(live_position)
            own_live_symbols.add(signal.symbol)
            state.seen_signal_ids.append(signal.signal_id)
            seen.add(signal.signal_id)

    save_json(state_path, state.to_dict())
    save_json(orders_path, trim_list(state.recent_orders, RECENT_LIMIT))
    save_json(rejections_path, trim_list(state.recent_rejections, RECENT_LIMIT))
    save_json(warnings_path, trim_list(state.recent_warnings, RECENT_LIMIT))
    write_compare_artifacts(cfg, art_dir, state)
    save_json(
        status_path,
        build_status_payload(
            cfg=cfg,
            now_iso=now_iso,
            allow_live_orders=bool(args.allow_live),
            state=state,
            core3_busy_symbols=core3_busy_symbols,
            signals=recent_signals,
            recent_signal_window_minutes=recent_signal_window_minutes,
            historical_backfill_skipped=historical_backfill_skipped,
            fresh_signal_expired=fresh_signal_expired,
        ),
    )
    refresh_local_dashboards()

    print(
        json.dumps(
            {
                "generated_at_utc": now_iso,
                "artifacts_root": str(art_dir.relative_to(ROOT)),
                "live_positions": len(state.live_positions),
                "closed_trades": len(state.closed_trades),
                "allow_live_orders": bool(args.allow_live),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
