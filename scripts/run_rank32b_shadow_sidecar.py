#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.domain.canary32b_models import EventRecord, EventType, StrategyStatusSnapshot  # noqa: E402
from momentum.execution.canary32b.event_bus import JsonlEventBus  # noqa: E402
from momentum.execution.canary32b.signal_adapter import Rank32BPerpSignalAdapter  # noqa: E402

ART_DIR = ROOT / "reports" / "artifacts" / "rank32b_shadow_beat"
EVENTS_PATH = ART_DIR / "shadow_events.jsonl"
STATE_PATH = ART_DIR / "shadow_state.json"
STATUS_PATH = ART_DIR / "shadow_status.json"
RUN_SUMMARY_PATH = ART_DIR / "shadow_last_run_summary.json"
SIGNALS_PATH = ART_DIR / "shadow_recent_signals.json"
REJECTIONS_PATH = ART_DIR / "shadow_recent_rejections.json"
WARNINGS_PATH = ART_DIR / "shadow_warnings.json"
PAPER_SUMMARY_PATH = ART_DIR / "paper_summary.json"
PAPER_TRADES_PATH = ART_DIR / "paper_trades.json"
PAPER_CLOSED_PATH = ART_DIR / "paper_closed_trades.json"
PAPER_OPEN_PATH = ART_DIR / "paper_open_positions.json"
PAPER_SKIPPED_PATH = ART_DIR / "paper_skipped_signals.json"
CONFIG_PATH = ROOT / "config" / "execution" / "rank32b_canary.yaml"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


phase6lib = load_module(ROOT / "scripts" / "run_rank32b_canary_phase6.py", "rank32b_phase6_shadow_lib")
exec_mod = load_module(ROOT / "scripts" / "build_rank32b_execution_probe.py", "rank32b_exec_mod_alt_shadow")
depth_v2_mod = load_module(ROOT / "scripts" / "rank32b_depth_v2_paper.py", "rank32b_depth_v2_alt_shadow")


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_shadow_cfg(cfg: dict[str, Any]) -> dict[str, Any]:
    phase6 = cfg.get("phase6", {}) if isinstance(cfg.get("phase6"), dict) else {}
    shadow_cfg = phase6.get("shadow", {}) if isinstance(phase6.get("shadow"), dict) else {}
    asset_to_symbol = shadow_cfg.get("asset_to_symbol") if isinstance(shadow_cfg.get("asset_to_symbol"), dict) else {"BEAT-USD": "BEATUSDT"}
    paper_cfg = shadow_cfg.get("paper") if isinstance(shadow_cfg.get("paper"), dict) else {}
    return {
        "enabled": bool(shadow_cfg.get("enabled", True)),
        "name": str(shadow_cfg.get("name", "Alt shadow sidecar")),
        "bucket": str(shadow_cfg.get("bucket", "alt") or "alt"),
        "asset_to_symbol": {str(asset): str(symbol).upper() for asset, symbol in asset_to_symbol.items()},
        "recent_hours": int(shadow_cfg.get("recent_hours", 240)),
        "tail_signals": int(shadow_cfg.get("tail_signals", 500)),
        "apply_smallcap_activity_filter": bool(shadow_cfg.get("apply_smallcap_activity_filter", True)),
        "paper": {
            "enabled": bool(paper_cfg.get("enabled", True)),
            "entry_style": str(paper_cfg.get("entry_style", "taker") or "taker"),
            "entry_ttl_5m_bars": int(paper_cfg.get("entry_ttl_5m_bars", exec_mod.ENTRY_TTL_5M_BARS)),
            "market_cost_bps": float(paper_cfg.get("market_cost_bps", exec_mod.TAKER_FEE_BPS)),
            "tp_atr_mult": float(paper_cfg.get("tp_atr_mult", 1.25)),
            "sl_atr_mult": float(paper_cfg.get("sl_atr_mult", 1.0)),
            "timeout_15m": int(paper_cfg.get("timeout_15m", 8)),
            "max_concurrent_positions": int(paper_cfg.get("max_concurrent_positions", 1)),
            "fallback_tp_bps": float(paper_cfg.get("fallback_tp_bps", 40.0)),
            "fallback_sl_bps": float(paper_cfg.get("fallback_sl_bps", 40.0)),
            "depth_v2": {
                "enabled": bool((paper_cfg.get("depth_v2") or {}).get("enabled", False)) if isinstance(paper_cfg.get("depth_v2"), dict) else False,
                "order_notional_usdt": float((paper_cfg.get("depth_v2") or {}).get("order_notional_usdt", 500.0)) if isinstance(paper_cfg.get("depth_v2"), dict) else 500.0,
                "depth_limit": int((paper_cfg.get("depth_v2") or {}).get("depth_limit", 20)) if isinstance(paper_cfg.get("depth_v2"), dict) else 20,
                "reject_if_insufficient_depth": bool((paper_cfg.get("depth_v2") or {}).get("reject_if_insufficient_depth", True)) if isinstance(paper_cfg.get("depth_v2"), dict) else True,
                "min_depth_fill_ratio": float((paper_cfg.get("depth_v2") or {}).get("min_depth_fill_ratio", 0.98)) if isinstance(paper_cfg.get("depth_v2"), dict) else 0.98,
                "entry_fee_bps": float((paper_cfg.get("depth_v2") or {}).get("entry_fee_bps", paper_cfg.get("market_cost_bps", exec_mod.TAKER_FEE_BPS))) if isinstance(paper_cfg.get("depth_v2"), dict) else float(paper_cfg.get("market_cost_bps", exec_mod.TAKER_FEE_BPS)),
                "exit_fee_bps": float((paper_cfg.get("depth_v2") or {}).get("exit_fee_bps", paper_cfg.get("market_cost_bps", exec_mod.TAKER_FEE_BPS))) if isinstance(paper_cfg.get("depth_v2"), dict) else float(paper_cfg.get("market_cost_bps", exec_mod.TAKER_FEE_BPS)),
            },
        },
    }


def load_state() -> dict[str, Any]:
    raw = phase6lib.load_json(STATE_PATH, {})
    if not isinstance(raw, dict):
        raw = {}
    return {
        "seen_signal_ids": list(raw.get("seen_signal_ids", [])),
        "last_run_utc": raw.get("last_run_utc"),
    }


def save_state(state: dict[str, Any], *, now_iso: str) -> None:
    payload = {
        "seen_signal_ids": list(state.get("seen_signal_ids", []))[-5000:],
        "last_run_utc": now_iso,
    }
    phase6lib.save_json(STATE_PATH, payload)


def parse_ts(value: Any) -> pd.Timestamp | None:
    if value is None:
        return None
    try:
        ts = pd.to_datetime(value, utc=True)
    except Exception:
        return None
    if pd.isna(ts):
        return None
    return ts


def iso(ts: pd.Timestamp | None) -> str | None:
    if ts is None or pd.isna(ts):
        return None
    return pd.Timestamp(ts).tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def get_signal_entry_ts(row: dict[str, Any]) -> pd.Timestamp | None:
    return parse_ts(row.get("signal_confirmed_at")) or parse_ts(row.get("timestamp"))


def get_signal_atr(row: dict[str, Any]) -> float | None:
    meta = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
    atr = meta.get("atr14")
    try:
        value = float(atr)
    except Exception:
        return None
    if value <= 0:
        return None
    return value


def get_signal_direction_sign(row: dict[str, Any]) -> int:
    return 1 if str(row.get("side") or "").lower() == "long" else -1


def get_symbol_bars(symbol: str, *, days: int, now_ts: pd.Timestamp, cache: dict[str, pd.DataFrame]) -> pd.DataFrame:
    if symbol in cache:
        return cache[symbol]
    df = exec_mod.load_or_fetch_perp_5m(symbol, days=days, refresh=False)
    last_ts = parse_ts(df["timestamp"].max()) if not df.empty else None
    if last_ts is None or last_ts < (now_ts.floor("5min") - pd.Timedelta(minutes=10)):
        df = exec_mod.load_or_fetch_perp_5m(symbol, days=days, refresh=True)
    df = df.sort_values("timestamp").reset_index(drop=True)
    cache[symbol] = df
    return df


def simulate_exit(sub_df: pd.DataFrame, fill_idx: int, fill_px: float, direction_sign: int, atr_value: float | None, paper_cfg: dict[str, Any]) -> dict[str, Any]:
    timeout_5m_bars = int(max(1, int(paper_cfg.get("timeout_15m", 8)) * 3))
    last_idx = len(sub_df) - 1
    end_idx = min(last_idx, fill_idx + timeout_5m_bars - 1)
    if atr_value is not None and atr_value > 0:
        target_px = float(fill_px + direction_sign * float(paper_cfg.get("tp_atr_mult", 1.25)) * atr_value)
        stop_px = float(fill_px - direction_sign * float(paper_cfg.get("sl_atr_mult", 1.0)) * atr_value)
        barrier_label = "atr"
    else:
        tp_bps = float(paper_cfg.get("fallback_tp_bps", 40.0)) / 10000.0
        sl_bps = float(paper_cfg.get("fallback_sl_bps", 40.0)) / 10000.0
        target_px = float(fill_px * (1.0 + direction_sign * tp_bps))
        stop_px = float(fill_px * (1.0 - direction_sign * sl_bps))
        barrier_label = "fallback_bps"

    for idx in range(fill_idx, end_idx + 1):
        bar = sub_df.iloc[idx]
        high = float(bar["high"])
        low = float(bar["low"])
        if direction_sign > 0:
            hit_tp = high >= target_px
            hit_sl = low <= stop_px
        else:
            hit_tp = low <= target_px
            hit_sl = high >= stop_px
        if hit_tp and hit_sl:
            exit_px = stop_px
            gross_ret = exec_mod.gross_return(fill_px, exit_px, direction_sign)
            net_ret = exec_mod.apply_fees(gross_ret, exec_mod.TAKER_FEE_BPS, exec_mod.TAKER_FEE_BPS)
            return {"status": "closed", "mark_status": "realized", "exit_ts": parse_ts(bar["timestamp"]), "exit_price": exit_px, "exit_reason": "conflict_stop_first", "gross_ret": gross_ret, "net_ret": net_ret, "hold_minutes": int((idx - fill_idx + 1) * 5), "barrier_type": barrier_label}
        if hit_tp:
            exit_px = target_px
            gross_ret = exec_mod.gross_return(fill_px, exit_px, direction_sign)
            net_ret = exec_mod.apply_fees(gross_ret, exec_mod.TAKER_FEE_BPS, exec_mod.MAKER_FEE_BPS)
            return {"status": "closed", "mark_status": "realized", "exit_ts": parse_ts(bar["timestamp"]), "exit_price": exit_px, "exit_reason": "target_limit", "gross_ret": gross_ret, "net_ret": net_ret, "hold_minutes": int((idx - fill_idx + 1) * 5), "barrier_type": barrier_label}
        if hit_sl:
            exit_px = stop_px
            gross_ret = exec_mod.gross_return(fill_px, exit_px, direction_sign)
            net_ret = exec_mod.apply_fees(gross_ret, exec_mod.TAKER_FEE_BPS, exec_mod.TAKER_FEE_BPS)
            return {"status": "closed", "mark_status": "realized", "exit_ts": parse_ts(bar["timestamp"]), "exit_price": exit_px, "exit_reason": "stop_loss", "gross_ret": gross_ret, "net_ret": net_ret, "hold_minutes": int((idx - fill_idx + 1) * 5), "barrier_type": barrier_label}

    if end_idx >= fill_idx + timeout_5m_bars - 1:
        bar = sub_df.iloc[end_idx]
        exit_px = float(bar["close"])
        gross_ret = exec_mod.gross_return(fill_px, exit_px, direction_sign)
        net_ret = exec_mod.apply_fees(gross_ret, exec_mod.TAKER_FEE_BPS, exec_mod.TAKER_FEE_BPS)
        return {"status": "closed", "mark_status": "realized", "exit_ts": parse_ts(bar["timestamp"]), "exit_price": exit_px, "exit_reason": "timeout_close", "gross_ret": gross_ret, "net_ret": net_ret, "hold_minutes": int((end_idx - fill_idx + 1) * 5), "barrier_type": barrier_label}

    bar = sub_df.iloc[last_idx]
    mark_px = float(bar["close"])
    gross_ret = exec_mod.gross_return(fill_px, mark_px, direction_sign)
    net_ret = exec_mod.apply_fees(gross_ret, exec_mod.TAKER_FEE_BPS, exec_mod.TAKER_FEE_BPS)
    return {"status": "open", "mark_status": "marked_to_market", "mark_ts": parse_ts(bar["timestamp"]), "mark_price": mark_px, "mark_gross_ret": gross_ret, "mark_net_ret": net_ret, "hold_minutes": int((last_idx - fill_idx + 1) * 5), "barrier_type": barrier_label}


def build_paper_trades(signal_rows: list[dict[str, Any]], shadow_cfg: dict[str, Any], now_ts: pd.Timestamp) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    paper_cfg = shadow_cfg.get("paper", {}) if isinstance(shadow_cfg.get("paper"), dict) else {}
    if not paper_cfg.get("enabled", True):
        return [], [], [], {"status": "disabled", "skipped_rows": []}
    eligible_rows = [row for row in signal_rows if get_signal_entry_ts(row) is not None and not row.get("shadow_would_block_reason")]
    eligible_rows.sort(key=lambda row: (get_signal_entry_ts(row), str(row.get("symbol") or "")))
    if bool(((paper_cfg.get("depth_v2") or {}).get("enabled", False)) if isinstance(paper_cfg.get("depth_v2"), dict) else False):
        existing_trades = phase6lib.load_json(PAPER_TRADES_PATH, [])
        if not isinstance(existing_trades, list):
            existing_trades = []
        trades, closed, open_positions, summary = depth_v2_mod.build_depth_v2_paper_trades(eligible_rows, paper_cfg, now_ts, existing_trades)
        summary.setdefault("eligible_signals", len(eligible_rows))
        return trades, closed, open_positions, summary
    if not eligible_rows:
        return [], [], [], {
            "status": "ok",
            "eligible_signals": 0,
            "paper_trades": 0,
            "paper_closed_trades": 0,
            "paper_open_positions": 0,
            "paper_skipped_by_max_concurrent": 0,
            "paper_realized_total_return": 0.0,
            "paper_marked_total_return": 0.0,
            "skipped_rows": [],
        }
    oldest_ts = min(get_signal_entry_ts(row) for row in eligible_rows if get_signal_entry_ts(row) is not None)
    days = max(3, int(((now_ts - oldest_ts) / pd.Timedelta(days=1))) + 3)
    bars_cache: dict[str, pd.DataFrame] = {}
    active_until: list[pd.Timestamp] = []
    paper_trades: list[dict[str, Any]] = []
    skipped_signals: list[dict[str, Any]] = []
    for row in eligible_rows:
        entry_ts = get_signal_entry_ts(row)
        symbol = str(row.get("symbol") or "").upper()
        direction_sign = get_signal_direction_sign(row)
        active_until = [ts for ts in active_until if ts > entry_ts]
        if len(active_until) >= int(paper_cfg.get("max_concurrent_positions", 1)):
            skipped_signals.append({
                "timestamp": row.get("timestamp"),
                "signal_confirmed_at": row.get("signal_confirmed_at"),
                "signal_id": row.get("signal_id"),
                "symbol": symbol,
                "side": row.get("side"),
                "reason": "paper_rejected_by_max_concurrent",
                "paper_active_positions": len(active_until),
                "paper_max_concurrent_positions": int(paper_cfg.get("max_concurrent_positions", 1)),
            })
            continue
        sub_df = get_symbol_bars(symbol, days=days, now_ts=now_ts, cache=bars_cache)
        ts_array = sub_df["timestamp"].to_numpy(dtype="datetime64[ns]") if not sub_df.empty else []
        entry_res = exec_mod.simulate_entry(sub_df, ts_array, entry_ts, direction_sign, entry_style=str(paper_cfg.get("entry_style", "taker")), entry_offset_bps=0.0, ttl_bars=int(paper_cfg.get("entry_ttl_5m_bars", exec_mod.ENTRY_TTL_5M_BARS))) if not sub_df.empty else None
        if entry_res is None:
            paper_trades.append({"signal_id": row.get("signal_id"), "symbol": symbol, "side": row.get("side"), "mode": ((row.get("metadata") if isinstance(row.get("metadata"), dict) else {}) or {}).get("signal_mode"), "signal_ts": row.get("timestamp"), "signal_confirmed_at": row.get("signal_confirmed_at"), "status": "entry_pending", "paper_trade_state": "entry_pending", "paper_effective_net_ret": 0.0})
            continue
        exit_res = simulate_exit(sub_df, int(entry_res["fill_idx"]), float(entry_res["fill_px"]), direction_sign, get_signal_atr(row), paper_cfg)
        trade_row = {
            "signal_id": row.get("signal_id"),
            "symbol": symbol,
            "side": row.get("side"),
            "mode": ((row.get("metadata") if isinstance(row.get("metadata"), dict) else {}) or {}).get("signal_mode"),
            "signal_ts": row.get("timestamp"),
            "signal_confirmed_at": row.get("signal_confirmed_at"),
            "entry_ts": iso(parse_ts(entry_res.get("fill_ts"))),
            "entry_price": float(entry_res.get("fill_px")),
            "entry_fee_bps": float(entry_res.get("entry_fee_bps", exec_mod.TAKER_FEE_BPS)),
            "paper_trade_state": str(exit_res.get("status") or "unknown"),
            "status": str(exit_res.get("mark_status") or exit_res.get("status") or "unknown"),
            "exit_ts": iso(exit_res.get("exit_ts")),
            "exit_price": exit_res.get("exit_price"),
            "exit_reason": exit_res.get("exit_reason"),
            "mark_ts": iso(exit_res.get("mark_ts")),
            "mark_price": exit_res.get("mark_price"),
            "net_ret": exit_res.get("net_ret"),
            "mark_net_ret": exit_res.get("mark_net_ret"),
            "paper_effective_net_ret": exit_res.get("net_ret") if exit_res.get("status") == "closed" else exit_res.get("mark_net_ret", 0.0),
            "hold_minutes": int(exit_res.get("hold_minutes", 0)),
            "atr14": get_signal_atr(row),
            "tp_atr_mult": float(paper_cfg.get("tp_atr_mult", 1.25)),
            "sl_atr_mult": float(paper_cfg.get("sl_atr_mult", 1.0)),
            "timeout_15m": int(paper_cfg.get("timeout_15m", 8)),
            "max_concurrent_positions": int(paper_cfg.get("max_concurrent_positions", 1)),
        }
        paper_trades.append(trade_row)
        trade_end_ts = parse_ts(trade_row.get("exit_ts")) or parse_ts(trade_row.get("mark_ts")) or now_ts
        active_until.append(trade_end_ts)
        active_until.sort()
    closed_trades = [row for row in paper_trades if row.get("paper_trade_state") == "closed"]
    open_positions = [row for row in paper_trades if row.get("paper_trade_state") == "open"]
    realized_rets = [float(row.get("net_ret", 0.0)) for row in closed_trades if row.get("net_ret") is not None]
    effective_rets = [float(row.get("paper_effective_net_ret", 0.0)) for row in paper_trades if row.get("paper_effective_net_ret") is not None]

    def total_return(vals: list[float]) -> float:
        acc = 1.0
        for val in vals:
            acc *= 1.0 + float(val)
        return acc - 1.0

    return paper_trades, closed_trades, open_positions, {
        "status": "ok",
        "assumptions": {
            "entry_style": paper_cfg.get("entry_style"),
            "entry_ttl_5m_bars": int(paper_cfg.get("entry_ttl_5m_bars", exec_mod.ENTRY_TTL_5M_BARS)),
            "market_cost_bps": float(paper_cfg.get("market_cost_bps", exec_mod.TAKER_FEE_BPS)),
            "tp_atr_mult": float(paper_cfg.get("tp_atr_mult", 1.25)),
            "sl_atr_mult": float(paper_cfg.get("sl_atr_mult", 1.0)),
            "timeout_15m": int(paper_cfg.get("timeout_15m", 8)),
            "max_concurrent_positions": int(paper_cfg.get("max_concurrent_positions", 1)),
        },
        "eligible_signals": len(eligible_rows),
        "paper_trades": len(paper_trades),
        "paper_closed_trades": len(closed_trades),
        "paper_open_positions": len(open_positions),
        "paper_skipped_by_max_concurrent": len(skipped_signals),
        "paper_realized_total_return": total_return(realized_rets),
        "paper_marked_total_return": total_return(effective_rets),
        "paper_closed_win_rate": float(sum(1 for x in realized_rets if x > 0) / len(realized_rets)) if realized_rets else None,
        "paper_avg_closed_net_ret": float(sum(realized_rets) / len(realized_rets)) if realized_rets else None,
        "paper_last_closed_symbol": closed_trades[-1].get("symbol") if closed_trades else None,
        "paper_last_closed_exit_ts": closed_trades[-1].get("exit_ts") if closed_trades else None,
        "paper_last_mark_symbol": open_positions[-1].get("symbol") if open_positions else None,
        "paper_last_mark_ts": open_positions[-1].get("mark_ts") if open_positions else None,
        "skipped_rows": skipped_signals,
    }


def signal_enrichment(signal: Any, *, cfg: dict[str, Any], shadow_cfg: dict[str, Any], run_ctx: Any) -> tuple[dict[str, Any], dict[str, Any] | None]:
    phase6 = cfg.get("phase6", {}) if isinstance(cfg.get("phase6"), dict) else {}
    signal_dict = signal.to_dict()
    metadata = signal_dict.get("metadata") if isinstance(signal_dict.get("metadata"), dict) else {}
    symbol = str(signal_dict.get("symbol") or "").upper()
    trace_id = phase6lib.make_trace_id(str(signal_dict.get("signal_id") or f"shadow-{symbol}"))
    live_universe_symbols = [str(s).upper() for s in cfg.get("universe", {}).get("symbols", [])]
    live_bucket = phase6lib.phase6_symbol_bucket(symbol, phase6)
    bar_key = phase6lib.signal_bar_key(symbol, str(signal_dict.get("timestamp") or ""))
    confirmed_at = phase6lib.signal_confirmed_at(str(signal_dict.get("timestamp") or ""), metadata)
    activity_snapshot = None
    would_block_reason = None
    if shadow_cfg.get("bucket") == "smallcap" and bool(shadow_cfg.get("apply_smallcap_activity_filter", True)):
        activity_snapshot = phase6lib.smallcap_activity_snapshot(symbol, phase6, run_ctx.now_dt)
        if not bool(activity_snapshot.get("allowed", False)):
            would_block_reason = "smallcap_activity_percentile_below_floor"
    payload = {
        **signal_dict,
        "trace_id": trace_id,
        "bar_key": bar_key,
        "signal_confirmed_at": confirmed_at,
        "shadow_name": shadow_cfg.get("name"),
        "shadow_bucket": shadow_cfg.get("bucket"),
        "shadow_live_universe_enabled": symbol in live_universe_symbols,
        "shadow_live_bucket_now": live_bucket,
        "shadow_would_block_reason": would_block_reason,
        "shadow_activity_snapshot": activity_snapshot,
        "config_version": phase6lib.config_hash(cfg),
        "code_version": phase6lib.code_version(),
    }
    reject_row = None
    if would_block_reason is not None:
        reject_row = {**payload, "risk": {"allowed": False, "reason": would_block_reason, "activity": activity_snapshot}}
    return payload, reject_row


def summarize_recent_signals(rows: list[dict[str, Any]]) -> dict[str, Any]:
    preview = 0
    official = 0
    latest_signal_time = None
    latest_symbol = None
    for row in rows:
        mode = str(((row.get("metadata") if isinstance(row.get("metadata"), dict) else {}) or {}).get("signal_mode") or row.get("signal_mode") or "")
        if mode == "preview_unclosed15m":
            preview += 1
        elif mode == "official_close":
            official += 1
        ts = row.get("timestamp")
        if ts and (latest_signal_time is None or str(ts) > str(latest_signal_time)):
            latest_signal_time = ts
            latest_symbol = row.get("symbol")
    return {"preview_signals": preview, "official_signals": official, "total_signals": len(rows), "latest_signal_time": latest_signal_time, "latest_signal_symbol": latest_symbol}


def main() -> int:
    ap = argparse.ArgumentParser(description="Run rank32b shadow sidecar without affecting live execution.")
    ap.add_argument("--config", default=str(CONFIG_PATH))
    args = ap.parse_args()

    ensure_dir(ART_DIR)
    run_ctx = phase6lib.utcnow()
    now_ts = parse_ts(run_ctx.now_iso) or pd.Timestamp.utcnow().tz_localize("UTC")
    cfg = phase6lib.load_yaml(Path(args.config))
    shadow_cfg = load_shadow_cfg(cfg)
    if not shadow_cfg.get("enabled", True):
        phase6lib.save_json(RUN_SUMMARY_PATH, {"generated_at_utc": run_ctx.now_iso, "status": "disabled", "message": "phase6.shadow.enabled=false"})
        return 0

    state = load_state()
    seen = set(str(x) for x in state.get("seen_signal_ids", []))
    warnings: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    event_bus = JsonlEventBus(EVENTS_PATH)

    signal_cfg = cfg.get("signal_adapter", {}) if isinstance(cfg.get("signal_adapter"), dict) else {}
    safety_cfg = cfg.get("phase6", {}).get("safety", {}) if isinstance(cfg.get("phase6", {}).get("safety"), dict) else {}
    adapter = Rank32BPerpSignalAdapter(
        asset_to_symbol=shadow_cfg["asset_to_symbol"],
        days=int(signal_cfg.get("lookback_days", 30)),
        recent_hours=int(shadow_cfg.get("recent_hours", signal_cfg.get("recent_hours", 72))),
        variant=str(signal_cfg.get("variant", "ema_cross_plus_slope_floor")),
        refresh_bars=bool(signal_cfg.get("refresh_bars", True)),
        refresh_tail_days=(int(signal_cfg["refresh_tail_days"]) if signal_cfg.get("refresh_tail_days") is not None else None),
        preview_unclosed_15m=bool(signal_cfg.get("preview_unclosed_15m", False)),
        preview_fetch_limit=int(signal_cfg.get("preview_fetch_limit", 30)),
        entry_delay_minutes=int(signal_cfg.get("entry_delay_minutes", 0)),
        official_signal_ttl_minutes=int(safety_cfg.get("max_signal_age_minutes", 30)),
    )
    snapshot = adapter.load_recent_signals()

    recent_rows: list[dict[str, Any]] = []
    new_rows: list[dict[str, Any]] = []
    reject_rows: list[dict[str, Any]] = []
    new_reject_rows: list[dict[str, Any]] = []
    for signal in snapshot.signals:
        enriched, reject_row = signal_enrichment(signal, cfg=cfg, shadow_cfg=shadow_cfg, run_ctx=run_ctx)
        recent_rows.append(enriched)
        if reject_row is not None:
            reject_rows.append(reject_row)
        if signal.signal_id in seen:
            continue
        seen.add(signal.signal_id)
        new_rows.append(enriched)
        phase6lib.append_event(event_bus, events, EventRecord(timestamp=run_ctx.now_iso, event_type=EventType.SIGNAL_RECEIVED, symbol=signal.symbol, side=signal.side.value, trace_id=str(enriched.get("trace_id") or ""), message="shadow sidecar received signal", payload=enriched, level="INFO"))
        if reject_row is not None:
            new_reject_rows.append(reject_row)
            phase6lib.append_event(event_bus, events, EventRecord(timestamp=run_ctx.now_iso, event_type=EventType.RISK_REJECTED, symbol=signal.symbol, side=signal.side.value, trace_id=str(enriched.get("trace_id") or ""), message=str(reject_row.get("risk", {}).get("reason") or "shadow_reject"), payload=reject_row, level="INFO"))

    merged_signals = phase6lib.append_recent_json(SIGNALS_PATH, recent_rows, tail=int(shadow_cfg.get("tail_signals", 500)), key_fields=["signal_id"])
    merged_rejections = phase6lib.append_recent_json(REJECTIONS_PATH, reject_rows, tail=int(shadow_cfg.get("tail_signals", 500)), key_fields=["signal_id", "shadow_would_block_reason"])
    phase6lib.save_json(WARNINGS_PATH, warnings)

    paper_trades, paper_closed, paper_open, paper_summary = build_paper_trades(merged_signals if isinstance(merged_signals, list) else [], shadow_cfg, now_ts)
    paper_summary_payload = {"generated_at_utc": run_ctx.now_iso, "shadow_name": shadow_cfg.get("name"), "shadow_bucket": shadow_cfg.get("bucket"), "code_version": phase6lib.code_version(), "config_version": phase6lib.config_hash(cfg), **{k: v for k, v in paper_summary.items() if k != "skipped_rows"}}
    phase6lib.save_json(PAPER_SUMMARY_PATH, paper_summary_payload)
    phase6lib.save_json(PAPER_TRADES_PATH, paper_trades)
    phase6lib.save_json(PAPER_CLOSED_PATH, paper_closed)
    phase6lib.save_json(PAPER_OPEN_PATH, paper_open)
    phase6lib.save_json(PAPER_SKIPPED_PATH, paper_summary.get("skipped_rows", []))

    summary_bits = summarize_recent_signals(merged_signals if isinstance(merged_signals, list) else [])
    run_summary = {
        "generated_at_utc": run_ctx.now_iso,
        "status": "ok",
        "shadow_name": shadow_cfg.get("name"),
        "shadow_bucket": shadow_cfg.get("bucket"),
        "shadow_symbols": shadow_cfg.get("asset_to_symbol"),
        "paper": shadow_cfg.get("paper"),
        "code_version": phase6lib.code_version(),
        "config_version": phase6lib.config_hash(cfg),
        "signal_adapter_latest_bar_utc": snapshot.latest_bar_utc,
        "signal_adapter_latest_signal_utc": snapshot.latest_signal_utc,
        "signal_adapter_latest_observed_signal_utc": snapshot.latest_observed_signal_utc,
        "snapshot_signal_count": len(snapshot.signals),
        "new_signal_count": len(new_rows),
        "new_rejection_count": len(new_reject_rows),
        "recent_rejection_count": len(merged_rejections if isinstance(merged_rejections, list) else []),
        **summary_bits,
        "paper_closed_trades": paper_summary_payload.get("paper_closed_trades"),
        "paper_open_positions": paper_summary_payload.get("paper_open_positions"),
        "paper_realized_total_return": paper_summary_payload.get("paper_realized_total_return"),
        "paper_marked_total_return": paper_summary_payload.get("paper_marked_total_return"),
    }
    phase6lib.save_json(RUN_SUMMARY_PATH, run_summary)

    status = StrategyStatusSnapshot(
        alpha_name="rank32b_shadow_sidecar",
        version=phase6lib.code_version(),
        mode="shadow_paper",
        enabled_symbols=list(shadow_cfg.get("asset_to_symbol", {}).values()),
        current_config_hash=phase6lib.config_hash(cfg),
        last_signal_time=snapshot.latest_signal_utc,
        system_health="ok",
        last_run_utc=run_ctx.now_iso,
        trade_enabled=False,
        kill_switch=False,
        recent_signal_count=int(run_summary.get("total_signals", 0)),
        recent_intention_count=0,
        recent_reject_count=int(run_summary.get("recent_rejection_count", 0)),
        notes=[
            "Alt shadow records every eligible alt signal and also computes paper PnL.",
            "It does not use global strongest-only selection; it answers whether the alt pocket itself is tradeable.",
            "Paper portfolio uses max_concurrent_positions from phase6.shadow.paper.",
        ],
        latest_evaluated_bar_time=snapshot.latest_bar_utc,
    )
    phase6lib.save_json(STATUS_PATH, status.to_dict())

    state["seen_signal_ids"] = list(seen)[-5000:]
    save_state(state, now_iso=run_ctx.now_iso)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        now_iso = phase6lib.utcnow().now_iso
        ensure_dir(ART_DIR)
        cfg_hash = None
        code_version = None
        try:
            cfg = phase6lib.load_yaml(Path(CONFIG_PATH))
            cfg_hash = phase6lib.config_hash(cfg)
        except Exception:
            cfg = None
        try:
            code_version = phase6lib.code_version()
        except Exception:
            code_version = None
        phase6lib.save_json(
            RUN_SUMMARY_PATH,
            {
                "generated_at_utc": now_iso,
                "status": "error_degraded",
                "shadow_name": "Alt shadow sidecar",
                "code_version": code_version,
                "config_version": cfg_hash,
                "error": str(exc),
            },
        )
        phase6lib.save_json(
            STATUS_PATH,
            {
                "alpha_name": "rank32b_shadow_sidecar",
                "version": code_version,
                "mode": "shadow_paper",
                "current_config_hash": cfg_hash,
                "system_health": "degraded",
                "last_run_utc": now_iso,
                "trade_enabled": False,
                "kill_switch": False,
                "recent_signal_count": 0,
                "recent_intention_count": 0,
                "recent_reject_count": 0,
                "notes": [f"shadow runner degraded: {exc}"],
            },
        )
        print(
            {
                "level": "ERROR",
                "component": "rank32b_shadow_sidecar",
                "message": "shadow_runner_degraded_not_failing_service",
                "error": str(exc),
            },
            flush=True,
        )
        raise SystemExit(0)
