#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import math
import sys
from datetime import timezone, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

ART_DIR = ROOT / "reports" / "artifacts" / "rank32b_shadow_global_live_like_backtest"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "rank32b"
OUT_JSON = ART_DIR / "monthly_stability_720d.json"
OUT_MD = ART_DIR / "monthly_stability_720d.md"
OUT_HTML = SITE_DIR / "global_live_like_stability.html"
LONG_WINDOW_STATUS = "withdrawn_due_warmup_audit"
BACKTEST_JSON = ART_DIR / "backtest_windows.json"
BACKTEST_180_SNAPSHOT_JSON = ART_DIR / "backtest_windows_180d_snapshot.json"
BACKTEST_365_LOG = ART_DIR / "nohup_logs" / "backtest_365d.log"
BACKTEST_720_LOG = ART_DIR / "nohup_logs" / "backtest_720d.log"
STABILITY_180D_JSON = ART_DIR / "stability_180d.json"
LEDGER_DIR = ART_DIR / "trade_ledgers"
ATR11_ART_DIR = ROOT / "reports" / "artifacts" / "rank32b_shadow_global_live_like_backtest_atr1_1"
ATR11_BACKTEST_JSON = ATR11_ART_DIR / "backtest_windows.json"
ATR11_LEDGER_DIR = ATR11_ART_DIR / "trade_ledgers"
BT_SCRIPT = ROOT / "scripts" / "backtest_rank32b_global_shadow_live_like.py"
GLOBAL_LIVE_ART_DIR = ROOT / "reports" / "artifacts" / "rank32b_global_live"
GLOBAL_LIVE_STATE_JSON = GLOBAL_LIVE_ART_DIR / "live_state.json"
GLOBAL_LIVE_RUN_JSON = GLOBAL_LIVE_ART_DIR / "live_last_run_summary.json"
GLOBAL_LIVE_STATUS_JSON = GLOBAL_LIVE_ART_DIR / "live_status.json"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


bt = load_module(BT_SCRIPT, "rank32b_global_live_like_bt_monthly")


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def read_json_from_log(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return default
    starts = [idx for idx, ch in enumerate(text) if ch == "{"]
    for start in reversed(starts):
        try:
            obj = json.loads(text[start:])
        except Exception:
            continue
        if isinstance(obj, dict) and obj.get("results"):
            return obj
    return default


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


def fmt_bj(ts: pd.Timestamp) -> str:
    bj = ts.tz_convert(timezone(timedelta(hours=8)))
    utc = ts.tz_convert("UTC")
    return f"{bj.strftime('%Y-%m-%d %H:%M:%S')} 北京时间 / {utc.strftime('%Y-%m-%d %H:%M:%S')} UTC"


def pct(v: float | None, digits: int = 2) -> str:
    if v is None or not math.isfinite(float(v)):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def num(v: float | None, digits: int = 2) -> str:
    if v is None or not math.isfinite(float(v)):
        return "-"
    return f"{float(v):.{digits}f}"


def sign_num(v: float | None, digits: int = 2) -> str:
    if v is None or not math.isfinite(float(v)):
        return "-"
    return f"{float(v):+,.{digits}f}"


def load_now_ts() -> pd.Timestamp:
    if BACKTEST_JSON.exists():
        payload = json.loads(BACKTEST_JSON.read_text(encoding="utf-8"))
        ts = parse_ts(payload.get("generated_at_utc"))
        if ts is not None:
            return ts
    return pd.Timestamp.now(tz="UTC")


def simulate_horizon_with_trades(cfg: dict[str, Any], *, horizon_days: int, now_ts: pd.Timestamp) -> dict[str, Any]:
    shadow_cfg = bt.shadow_mod.load_shadow_cfg(cfg)
    asset_to_symbol = shadow_cfg["asset_to_symbol"]
    signal_cfg = cfg.get("signal_adapter", {}) if isinstance(cfg.get("signal_adapter"), dict) else {}
    signal_lookback_days = int(signal_cfg.get("lookback_days", horizon_days))
    signal_fetch_days = int(horizon_days) + max(0, signal_lookback_days)
    adapter = bt.Rank32BPerpSignalAdapter(
        asset_to_symbol=asset_to_symbol,
        days=signal_fetch_days,
        recent_hours=int(horizon_days * 24),
        variant=str(signal_cfg.get("variant", "ema_cross_plus_slope_floor")),
        refresh_bars=bool(signal_cfg.get("refresh_bars", True)),
        refresh_tail_days=(int(signal_cfg["refresh_tail_days"]) if signal_cfg.get("refresh_tail_days") is not None else None),
        preview_unclosed_15m=False,
        preview_fetch_limit=int(signal_cfg.get("preview_fetch_limit", 30)),
        entry_delay_minutes=int(signal_cfg.get("entry_delay_minutes", 0)),
        official_signal_ttl_minutes=None,
    )
    snapshot = adapter.load_recent_signals()
    selection_phase6 = {
        "selection": shadow_cfg.get("selection", {}),
        "smallcap": {"enabled": False, "symbols": []},
        "max_new_signals_per_run": 0,
    }
    selected_signals, skipped_weaker_signals = bt.phase6lib.select_signals_for_execution(snapshot.signals, selection_phase6)
    selected_rows = bt.normalize_selected_rows(selected_signals)

    paper_cfg = bt.deepcopy(shadow_cfg.get("paper", {}))
    if isinstance(paper_cfg.get("depth_v2"), dict):
        paper_cfg["depth_v2"]["enabled"] = False
    live_parity_cfg = bt.depth_v2_mod.build_live_parity_cfg(paper_cfg)
    cache_cfg = live_parity_cfg.get("kline_1m_cache", {})
    bars_cache: dict[str, pd.DataFrame] = {}
    day_cache: dict[str, pd.DataFrame] = {}

    usable_rows = [row for row in selected_rows if bt.shadow_mod.get_signal_entry_ts(row) is not None]
    usable_rows.sort(key=lambda row: (bt.shadow_mod.get_signal_entry_ts(row), str(row.get("symbol") or "")))
    oldest_ts = min(bt.shadow_mod.get_signal_entry_ts(row) for row in usable_rows if bt.shadow_mod.get_signal_entry_ts(row) is not None)
    days_5m = max(3, int(math.ceil((now_ts - oldest_ts) / pd.Timedelta(days=1))) + 2) if usable_rows else max(3, horizon_days + 2)

    consumed: set[str] = set()
    active_positions: list[dict[str, Any]] = []
    paper_trades: list[dict[str, Any]] = []
    skipped_signals: list[dict[str, Any]] = []
    timeout_minutes = int(paper_cfg.get("timeout_15m", 8)) * 15

    for row in usable_rows:
        entry_ts = bt.shadow_mod.get_signal_entry_ts(row)
        symbol = str(row.get("symbol") or "").upper()
        side = str(row.get("side") or "").lower()
        direction_sign = bt.shadow_mod.get_signal_direction_sign(row)
        bar_key = str(
            row.get("bar_key")
            or bt.depth_v2_mod.signal_bar_key(symbol, row.get("timestamp") or row.get("signal_confirmed_at"), int(live_parity_cfg.get("same_bar_minutes", 15)))
        )

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

        sub_df = bt.shadow_mod.get_symbol_bars(symbol, days=days_5m, now_ts=now_ts, cache=bars_cache)
        ts_array = sub_df["timestamp"].to_numpy(dtype="datetime64[ns]") if not sub_df.empty else []
        entry_res = bt.shadow_mod.exec_mod.simulate_entry(
            sub_df,
            ts_array,
            entry_ts,
            direction_sign,
            entry_style=str(paper_cfg.get("entry_style", "taker")),
            entry_offset_bps=0.0,
            ttl_bars=int(paper_cfg.get("entry_ttl_5m_bars", bt.shadow_mod.exec_mod.ENTRY_TTL_5M_BARS)),
        ) if not sub_df.empty else None

        if entry_res is None:
            paper_trades.append({
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
            })
            consumed.add(bar_key)
            continue

        fill_ts = bt.shadow_mod.parse_ts(entry_res.get("fill_ts")) or entry_ts
        minute_df = bt.get_trade_minute_window(symbol, entry_ts=fill_ts, timeout_minutes=timeout_minutes, cache_cfg=cache_cfg, day_cache=day_cache)
        if minute_df.empty:
            exit_res = bt.shadow_mod.simulate_exit_5m_fallback(sub_df, int(entry_res["fill_idx"]), float(entry_res["fill_px"]), direction_sign, bt.shadow_mod.get_signal_atr(row), paper_cfg)
        else:
            exit_res = bt.depth_v2_mod.simulate_exit_on_minute_bars(
                minute_df,
                entry_ts=fill_ts,
                entry_price=float(entry_res.get("fill_px")),
                position_side=side,
                atr_value=bt.shadow_mod.get_signal_atr(row),
                paper_cfg=paper_cfg,
                now_ts=fill_ts + pd.Timedelta(minutes=timeout_minutes + 1),
                entry_fee_bps=float(bt.shadow_mod.exec_mod.TAKER_FEE_BPS),
                exit_fee_bps=float(bt.shadow_mod.exec_mod.TAKER_FEE_BPS),
            )

        trade_row = {
            "signal_id": row.get("signal_id"),
            "symbol": symbol,
            "side": row.get("side"),
            "mode": ((row.get("metadata") if isinstance(row.get("metadata"), dict) else {}) or {}).get("signal_mode"),
            "signal_ts": row.get("timestamp"),
            "signal_confirmed_at": row.get("signal_confirmed_at"),
            "bar_key": bar_key,
            "entry_ts": bt.shadow_mod.iso(fill_ts),
            "entry_price": float(entry_res.get("fill_px")),
            "entry_fee_bps": float(entry_res.get("entry_fee_bps", bt.shadow_mod.exec_mod.TAKER_FEE_BPS)),
            "entry_maker": int(entry_res.get("entry_maker", 0)),
            "paper_trade_state": str(exit_res.get("status") or "unknown"),
            "status": str(exit_res.get("mark_status") or exit_res.get("status") or "unknown"),
            "exit_ts": bt.shadow_mod.iso(exit_res.get("exit_ts")),
            "exit_price": exit_res.get("exit_price"),
            "exit_reason": exit_res.get("exit_reason"),
            "mark_ts": bt.shadow_mod.iso(exit_res.get("mark_ts")),
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
            "atr14": bt.shadow_mod.get_signal_atr(row),
            "tp_atr_mult": float(paper_cfg.get("tp_atr_mult", 1.75)),
            "sl_atr_mult": float(paper_cfg.get("sl_atr_mult", 1.0)),
            "timeout_15m": int(paper_cfg.get("timeout_15m", 8)),
            "max_concurrent_positions": int(paper_cfg.get("max_concurrent_positions", 1)),
            "exit_monitor_interval_minutes": int(live_parity_cfg.get("exit_check_interval_minutes", 1)),
        }
        paper_trades.append(trade_row)
        trade_end_ts = bt.shadow_mod.parse_ts(trade_row.get("exit_ts")) or bt.shadow_mod.parse_ts(trade_row.get("mark_ts")) or fill_ts
        active_positions.append({"symbol": symbol, "active_until": trade_end_ts})
        active_positions.sort(key=lambda pos: (pos.get("active_until") or fill_ts, pos.get("symbol") or ""))
        consumed.add(bar_key)

    default_notional, notional_by_symbol = bt.load_live_like_notional(cfg, asset_to_symbol)
    metrics = bt.compute_metrics(paper_trades, default_notional=default_notional, notional_by_symbol=notional_by_symbol)
    closed_trades = [row for row in paper_trades if row.get("paper_trade_state") == "closed"]
    open_positions = [row for row in paper_trades if row.get("paper_trade_state") == "open"]

    def total_return(vals: list[float]) -> float:
        acc = 1.0
        for val in vals:
            acc *= 1.0 + float(val)
        return acc - 1.0

    realized_rets = [float(row.get("net_ret", 0.0)) for row in closed_trades if row.get("net_ret") is not None]
    effective_rets = [float(row.get("paper_effective_net_ret", 0.0)) for row in paper_trades if row.get("paper_effective_net_ret") is not None]

    return {
        "horizon_days": int(horizon_days),
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
        "signal_lookback_days": signal_lookback_days,
        "signal_fetch_days": signal_fetch_days,
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
        trade_ts = bt.trade_ts(row)
        rows.append({
            **row,
            "symbol": symbol,
            "trade_ts": trade_ts,
            "entry_ts_obj": parse_ts(row.get("entry_ts")),
            "exit_ts_obj": parse_ts(row.get("exit_ts")),
            "mark_ts_obj": parse_ts(row.get("mark_ts")),
            "notional_usdt": float(notional_by_symbol.get(symbol, default_notional)),
            "live_like_pnl_usdt": float(notional_by_symbol.get(symbol, default_notional)) * effective_ret,
            "effective_net_ret": effective_ret,
            "month": trade_ts.tz_convert(None).to_period("M").strftime("%Y-%m"),
        })
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    return df.sort_values(["trade_ts", "symbol"]).reset_index(drop=True)


def build_monthly_summary(df: pd.DataFrame) -> list[dict[str, Any]]:
    if df.empty:
        return []
    out: list[dict[str, Any]] = []
    cum = 0.0
    grouped = df.groupby("month", sort=True)
    for month, grp in grouped:
        pnl = float(grp["live_like_pnl_usdt"].sum())
        cum += pnl
        rets = [float(x) for x in grp["effective_net_ret"].tolist()]
        compound = 1.0
        for r in rets:
            compound *= 1.0 + r
        compound -= 1.0
        out.append({
            "month": month,
            "trade_count": int(len(grp)),
            "pnl_usdt": pnl,
            "cum_pnl_usdt": cum,
            "win_rate": float((grp["effective_net_ret"] > 0).mean()) if len(grp) else None,
            "avg_net_ret": float(grp["effective_net_ret"].mean()) if len(grp) else None,
            "compound_trade_return": float(compound),
            "trade_sharpe": trade_sharpe(rets),
            "positive": bool(pnl > 0),
        })
    return out


def build_rolling_summary(df: pd.DataFrame, months: list[dict[str, Any]], window: int = 3) -> list[dict[str, Any]]:
    if not months:
        return []
    month_keys = [m["month"] for m in months]
    month_periods = [pd.Period(m, freq="M") for m in month_keys]
    out: list[dict[str, Any]] = []
    month_df = pd.DataFrame(months)
    for idx in range(window - 1, len(months)):
        start_p = month_periods[idx - window + 1]
        end_p = month_periods[idx]
        part = df[df["month"].isin([p.strftime("%Y-%m") for p in month_periods[idx - window + 1 : idx + 1]])].copy()
        monthly_slice = month_df.iloc[idx - window + 1 : idx + 1]
        compound = 1.0
        for r in [float(x) for x in part["effective_net_ret"].tolist()]:
            compound *= 1.0 + r
        compound -= 1.0
        out.append({
            "window_label": f"{start_p.strftime('%Y-%m')} → {end_p.strftime('%Y-%m')}",
            "end_month": end_p.strftime("%Y-%m"),
            "trade_count": int(len(part)),
            "rolling_pnl_usdt": float(part["live_like_pnl_usdt"].sum()),
            "rolling_compound_trade_return": float(compound),
            "rolling_trade_sharpe": trade_sharpe([float(x) for x in part["effective_net_ret"].tolist()]),
            "positive_months": int(sum(1 for x in monthly_slice["pnl_usdt"].tolist() if float(x) > 0)),
        })
    return out


def pnl_points(items: list[dict[str, Any]], label_key: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in items or []:
        label = row.get(label_key)
        if label is None and row.get("idx") is not None:
            label = row.get("idx")
        if label is None:
            continue
        try:
            pnl = float(row.get("pnl_usdt") or 0.0)
        except Exception:
            pnl = 0.0
        out.append({"label": label, "pnl_usdt": pnl})
    return out


def build_payload() -> dict[str, Any]:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    cfg = bt.load_cfg(bt.CONFIG_PATH)
    shadow_cfg = bt.shadow_mod.load_shadow_cfg(cfg)
    default_notional_usdt, notional_by_symbol = bt.load_live_like_notional(cfg, shadow_cfg["asset_to_symbol"])
    base_payload = json.loads(BACKTEST_JSON.read_text(encoding="utf-8")) if BACKTEST_JSON.exists() else {"results": []}
    base_results = {int(item.get("horizon_days")): item for item in base_payload.get("results", []) if item.get("horizon_days") is not None}

    snap180 = read_json(BACKTEST_180_SNAPSHOT_JSON, {}) or {}
    snap180_results = snap180.get("results") or []
    if 180 not in base_results and snap180_results:
        first180 = snap180_results[0] if isinstance(snap180_results[0], dict) else None
        if first180 and first180.get("horizon_days") == 180:
            base_results[180] = first180

    log365 = read_json_from_log(BACKTEST_365_LOG, {}) or {}
    log365_results = log365.get("results") or []
    if 365 not in base_results and log365_results:
        first365 = log365_results[0] if isinstance(log365_results[0], dict) else None
        if first365 and first365.get("horizon_days") == 365:
            base_results[365] = first365

    result_180 = base_results.get(180)
    result_365 = base_results.get(365)
    result_720 = base_results.get(720)
    horizon_720_status = "ready" if result_720 is not None else ("running" if BACKTEST_720_LOG.exists() else "missing")
    used_backtest_now_utc = (
        (result_720 or {}).get("used_now_utc")
        or (result_365 or {}).get("used_now_utc")
        or (result_180 or {}).get("used_now_utc")
        or load_now_ts().strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    monthly: list[dict[str, Any]] = []
    negative_months: list[dict[str, Any]] = []
    best_month: dict[str, Any] | None = None
    worst_month: dict[str, Any] | None = None
    older_monthly: list[dict[str, Any]] = []
    rolling_3m: list[dict[str, Any]] = []
    rolling_6m: list[dict[str, Any]] = []
    older_exact = 0.0
    recent365_exact = 0.0
    if LONG_WINDOW_STATUS != "withdrawn_due_warmup_audit" and result_720 is not None:
        trades_720 = read_json(LEDGER_DIR / "paper_trades_720d.json", []) or []
        if trades_720:
            df = build_trade_frame(
                trades_720,
                default_notional=float(default_notional_usdt),
                notional_by_symbol=notional_by_symbol,
            )
            monthly = build_monthly_summary(df)
            rolling_3m = build_rolling_summary(df, monthly, window=3)
            rolling_6m = build_rolling_summary(df, monthly, window=6)
            cutoff_365 = pd.Timestamp(used_backtest_now_utc, tz="UTC") - pd.Timedelta(days=365)
            older_df = df[df["trade_ts"] < cutoff_365].copy()
            recent365_df = df[df["trade_ts"] >= cutoff_365].copy()
            older_monthly = [m for m in monthly if m["month"] < cutoff_365.tz_convert(None).to_period("M").strftime("%Y-%m")]
            negative_months = [m for m in monthly if float(m["pnl_usdt"]) < 0]
            worst_month = min(monthly, key=lambda x: float(x["pnl_usdt"])) if monthly else None
            best_month = max(monthly, key=lambda x: float(x["pnl_usdt"])) if monthly else None
            older_exact = float(older_df["live_like_pnl_usdt"].sum()) if not older_df.empty else 0.0
            recent365_exact = float(recent365_df["live_like_pnl_usdt"].sum()) if not recent365_df.empty else 0.0
    if LONG_WINDOW_STATUS == "withdrawn_due_warmup_audit":
        result_180 = None
        result_365 = None
        result_720 = None
        horizon_720_status = LONG_WINDOW_STATUS
        monthly = []
        negative_months = []
        best_month = None
        worst_month = None
        older_monthly = []
        rolling_3m = []
        rolling_6m = []
        older_exact = 0.0
        recent365_exact = 0.0
    delta_vs_365 = None
    if LONG_WINDOW_STATUS != "withdrawn_due_warmup_audit" and result_365 is not None and result_720 is not None:
        delta_vs_365 = float((result_720.get("metrics") or {}).get("usdt_pnl_live_like") or 0.0) - float((result_365.get("metrics") or {}).get("usdt_pnl_live_like") or 0.0)
    recent180 = json.loads(STABILITY_180D_JSON.read_text(encoding="utf-8")) if STABILITY_180D_JSON.exists() else None
    live_state = read_json(GLOBAL_LIVE_STATE_JSON, {}) or {}
    live_run = read_json(GLOBAL_LIVE_RUN_JSON, {}) or {}
    live_status = read_json(GLOBAL_LIVE_STATUS_JSON, {}) or {}
    live_positions = live_state.get("live_positions", []) or []
    active_position = live_positions[0] if live_positions else None
    short_official = {days: base_results.get(days) for days in (3, 10, 30, 60)}
    atr11_payload = read_json(ATR11_BACKTEST_JSON, {}) or {}
    atr11_results = {int(item.get("horizon_days")): item for item in atr11_payload.get("results", []) if item.get("horizon_days") is not None}
    atr11_seg60 = pnl_points(read_json(ATR11_LEDGER_DIR / "ten_day_segments_60d.json", []) or [], "idx")
    atr11_mon60 = pnl_points(read_json(ATR11_LEDGER_DIR / "monthly_summary_60d.json", []) or [], "month")
    atr11_seg180 = pnl_points(read_json(ATR11_LEDGER_DIR / "ten_day_segments_180d.json", []) or [], "idx")
    atr11_mon180 = pnl_points(read_json(ATR11_LEDGER_DIR / "monthly_summary_180d.json", []) or [], "month")

    payload = {
        "generated_at_utc": pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ"),
        "used_backtest_now_utc": used_backtest_now_utc,
        "config_path": str(bt.CONFIG_PATH),
        "comparison": {
            "horizon_180": result_180,
            "horizon_365": result_365,
            "horizon_720": result_720,
            "horizon_720_status": horizon_720_status,
            "long_window_status": LONG_WINDOW_STATUS,
            "long_window_note": "Long-window live-like outputs (180d/365d/720d) were withdrawn after the 2026-04-07 warmup audit. Re-run with the fixed backtest script before restoring them.",
            "delta_720_minus_365_usdt": delta_vs_365,
            "older_than_365_exact_live_like_pnl_usdt": older_exact,
            "recent_365_exact_live_like_pnl_usdt": recent365_exact,
        },
        "monthly": {
            "months": monthly,
            "negative_months": negative_months,
            "best_month": best_month,
            "worst_month": worst_month,
            "positive_month_count": int(sum(1 for m in monthly if float(m["pnl_usdt"]) > 0)),
            "negative_month_count": int(sum(1 for m in monthly if float(m["pnl_usdt"]) < 0)),
            "older_window_months": older_monthly,
        },
        "rolling_3m": rolling_3m,
        "rolling_6m": rolling_6m,
        "recent_180d_stability": recent180,
        "official_live": {
            "closed_trades": int(len(live_state.get("closed_trades", []) or [])),
            "open_positions": int(len(live_positions)),
            "active_position": active_position,
            "last_run_utc": live_run.get("run_finished_at") or live_status.get("last_run_utc"),
            "entry_window": live_run.get("entry_window") or {},
            "warnings": int(live_run.get("warnings", 0) or 0),
            "history_reset_archive": "official_transition_20260405T101057Z",
        },
        "short_official_windows": short_official,
        "atr_1_1": {
            "results": atr11_results,
            "seg60": atr11_seg60,
            "mon60": atr11_mon60,
            "seg180": atr11_seg180,
            "mon180": atr11_mon180,
        },
    }
    return payload


def write_markdown(payload: dict[str, Any]) -> None:
    comp = payload.get("comparison", {})
    if comp.get("long_window_status") == "withdrawn_due_warmup_audit":
        lines = [
            "# rank32b global live-like monthly stability",
            "",
            f"- used_backtest_now_utc: {payload.get('used_backtest_now_utc')}",
            "- long-window status: withdrawn_due_warmup_audit",
            f"- note: {comp.get('long_window_note')}",
            "- retained on this page: short-window official-close windows + recent-180d stability visuals",
            "",
        ]
        OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return
    m365 = (((comp.get("horizon_365") or {}).get("metrics") or {}) if comp.get("horizon_365") else {})
    m720 = (((comp.get("horizon_720") or {}).get("metrics") or {}) if comp.get("horizon_720") else {})
    monthly = ((payload.get("monthly") or {}).get("months") or [])
    negative = ((payload.get("monthly") or {}).get("negative_months") or [])
    worst = (payload.get("monthly") or {}).get("worst_month") or {}
    lines = [
        "# rank32b global live-like monthly stability (720d)",
        "",
        f"- used_backtest_now_utc: {payload.get('used_backtest_now_utc')}",
        f"- 365d live-like pnl: {num(m365.get('usdt_pnl_live_like'), 2)} U",
        f"- 720d live-like pnl: {num(m720.get('usdt_pnl_live_like'), 2)} U",
        f"- delta (720-365): {sign_num(comp.get('delta_720_minus_365_usdt'), 2)} U",
        f"- older-than-365 exact contribution: {sign_num(comp.get('older_than_365_exact_live_like_pnl_usdt'), 2)} U",
        f"- monthly windows: {len(monthly)} | negative months: {len(negative)}",
        f"- worst month: {worst.get('month')} {sign_num(worst.get('pnl_usdt'), 2)} U" if worst else "- worst month: -",
        "",
        "## Negative months",
        "",
    ]
    if negative:
        for row in sorted(negative, key=lambda x: float(x.get("pnl_usdt", 0.0))):
            lines.append(f"- {row['month']}: {sign_num(row['pnl_usdt'], 2)} U | trades={row['trade_count']} | win_rate={pct(row['win_rate'])}")
    else:
        lines.append("- none")
    lines.append("")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_html(payload: dict[str, Any]) -> None:
    comp = payload.get("comparison", {})
    m180 = (((comp.get("horizon_180") or {}).get("metrics") or {}) if comp.get("horizon_180") else {})
    m365 = (((comp.get("horizon_365") or {}).get("metrics") or {}) if comp.get("horizon_365") else {})
    m720 = (((comp.get("horizon_720") or {}).get("metrics") or {}) if comp.get("horizon_720") else {})
    monthly = ((payload.get("monthly") or {}).get("months") or [])
    negative = ((payload.get("monthly") or {}).get("negative_months") or [])
    best = (payload.get("monthly") or {}).get("best_month") or {}
    worst = (payload.get("monthly") or {}).get("worst_month") or {}
    rolling_3m = payload.get("rolling_3m") or []
    recent180 = payload.get("recent_180d_stability") or {}
    recent10 = (((recent180.get("segments_10d") or {}).get("summary") or {}) if recent180 else {})
    recent30 = (((recent180.get("segments_30d") or {}).get("summary") or {}) if recent180 else {})
    recent_ready = bool(((recent180.get("segments_10d") or {}).get("segments") or []))
    if recent_ready:
        recent10_value = f"{recent10.get('positive_segments',0)}/{recent10.get('segment_count',0)}"
        recent10_sub = f"均值 {sign_num(recent10.get('mean_pnl_usdt'),2)}U · 最差 {sign_num(recent10.get('worst_pnl_usdt'),2)}U"
        recent30_value = f"{recent30.get('positive_segments',0)}/{recent30.get('segment_count',0)}"
        recent30_sub = f"均值 {sign_num(recent30.get('mean_pnl_usdt'),2)}U · 最差 {sign_num(recent30.get('worst_pnl_usdt'),2)}U"
    else:
        recent10_value = "pending"
        recent10_sub = "修正后 180d 分段仍在重算，旧结果已下线"
        recent30_value = "pending"
        recent30_sub = "修正后 180d 分段仍在重算，旧结果已下线"
    short_windows = payload.get("short_official_windows") or {}
    atr11 = payload.get("atr_1_1") or {}
    atr11_results = atr11.get("results") or {}
    cfg = bt.load_cfg(bt.CONFIG_PATH)
    signal_cfg = cfg.get("signal_adapter", {}) if isinstance(cfg.get("signal_adapter"), dict) else {}
    default_signal_lookback_days = int(signal_cfg.get("lookback_days", 0) or 0)
    live = payload.get("official_live") or {}
    active_position = live.get("active_position") or {}
    generated_at = fmt_bj(pd.Timestamp(payload["generated_at_utc"], tz="UTC"))
    used_now = fmt_bj(pd.Timestamp(payload["used_backtest_now_utc"], tz="UTC"))
    delta_720_minus_365 = comp.get("delta_720_minus_365_usdt")
    negative_month_count = int((payload.get("monthly") or {}).get("negative_month_count") or 0)
    older_exact = float(comp.get("older_than_365_exact_live_like_pnl_usdt") or 0.0)
    latest_bar_180_utc = (comp.get("horizon_180") or {}).get("latest_bar_utc")
    latest_bar_365_utc = (comp.get("horizon_365") or {}).get("latest_bar_utc")
    latest_bar_720_utc = (comp.get("horizon_720") or {}).get("latest_bar_utc")
    latest_bar_180 = fmt_bj(pd.Timestamp(latest_bar_180_utc, tz="UTC")) if latest_bar_180_utc else "-"
    latest_bar_365 = fmt_bj(pd.Timestamp(latest_bar_365_utc, tz="UTC")) if latest_bar_365_utc else "-"
    latest_bar_720 = fmt_bj(pd.Timestamp(latest_bar_720_utc, tz="UTC")) if latest_bar_720_utc else "-"
    h720_status = str(comp.get("horizon_720_status") or "missing")
    last_run_utc = parse_ts(live.get("last_run_utc"))
    last_run_text = fmt_bj(last_run_utc) if last_run_utc is not None else "-"
    entry_window = live.get("entry_window") or {}
    entry_mode = (
        f"15m cadence · trigger second = {entry_window.get('trigger_second', 5)} · freshness = "
        f"{int((entry_window.get('freshness_seconds') or 180) / 60)}m"
    )
    active_position_text = (
        f"{active_position.get('symbol','-')} {active_position.get('side','-')} · entry {active_position.get('entry_time','-')}"
        if active_position else "none"
    )
    short_cards = []
    for days in (3, 10, 30, 60):
        item = short_windows.get(days) or short_windows.get(str(days)) or {}
        metrics = (item.get("metrics") or {}) if isinstance(item, dict) else {}
        summary = (item.get("paper_summary") or {}) if isinstance(item, dict) else {}
        if not item:
            short_cards.append(
                f"<div class=\"stat\"><div class=\"k\">{days}d official-close</div><div class=\"v\">-</div><div class=\"sub\">尚未生成修正后结果</div></div>"
            )
            continue
        lookback_days = int(item.get("signal_lookback_days") or default_signal_lookback_days)
        fetch_days = int(item.get("signal_fetch_days") or (int(days) + max(0, lookback_days)))
        short_cards.append(
            f"<div class=\"stat\"><div class=\"k\">{days}d official-close</div>"
            f"<div class=\"v\">{sign_num(metrics.get('usdt_pnl_live_like'),2)}U</div>"
            f"<div class=\"sub\">closed {summary.get('paper_closed_trades','-')} · win {pct(metrics.get('closed_win_rate'))} · warmup {lookback_days}d / fetch {fetch_days}d</div></div>"
        )
    atr_cards = []
    for days in (3, 10, 30, 60, 180):
        item = atr11_results.get(days) or atr11_results.get(str(days)) or {}
        metrics = (item.get("metrics") or {}) if isinstance(item, dict) else {}
        summary = (item.get("paper_summary") or {}) if isinstance(item, dict) else {}
        if not item:
            atr_cards.append(
                f"<div class=\"stat\"><div class=\"k\">{days}d ATR 1.0 / 1.0</div><div class=\"v\">-</div><div class=\"sub\">尚未生成</div></div>"
            )
            continue
        klass = " good" if float(metrics.get("usdt_pnl_live_like") or 0.0) > 0 else ""
        atr_cards.append(
            f"<div class=\"stat\"><div class=\"k\">{days}d ATR 1.0 / 1.0</div>"
            f"<div class=\"v{klass}\">{sign_num(metrics.get('usdt_pnl_live_like'),2)}U</div>"
            f"<div class=\"sub\">closed {summary.get('paper_closed_trades','-')} · win {pct(metrics.get('closed_win_rate'))}</div></div>"
        )
    atr_row_links = {
        3: [
            ("/momentum/artifacts/rank32b_shadow_global_live_like_backtest_atr1_1/trade_ledgers/paper_trades_3d.json", "paper_trades_3d.json"),
            ("/momentum/artifacts/rank32b_shadow_global_live_like_backtest_atr1_1/trade_ledgers/monthly_summary_3d.json", "monthly_summary_3d.json"),
        ],
        10: [
            ("/momentum/artifacts/rank32b_shadow_global_live_like_backtest_atr1_1/trade_ledgers/paper_trades_10d.json", "paper_trades_10d.json"),
            ("/momentum/artifacts/rank32b_shadow_global_live_like_backtest_atr1_1/trade_ledgers/monthly_summary_10d.json", "monthly_summary_10d.json"),
        ],
        30: [
            ("/momentum/artifacts/rank32b_shadow_global_live_like_backtest_atr1_1/trade_ledgers/paper_trades_30d.json", "paper_trades_30d.json"),
            ("/momentum/artifacts/rank32b_shadow_global_live_like_backtest_atr1_1/trade_ledgers/monthly_summary_30d.json", "monthly_summary_30d.json"),
        ],
        60: [
            ("/momentum/artifacts/rank32b_shadow_global_live_like_backtest_atr1_1/trade_ledgers/paper_trades_60d.json", "paper_trades_60d.json"),
            ("/momentum/artifacts/rank32b_shadow_global_live_like_backtest_atr1_1/trade_ledgers/monthly_summary_60d.json", "monthly_summary_60d.json"),
            ("/momentum/artifacts/rank32b_shadow_global_live_like_backtest_atr1_1/trade_ledgers/ten_day_segments_60d.json", "ten_day_segments_60d.json"),
        ],
        180: [
            ("/momentum/artifacts/rank32b_shadow_global_live_like_backtest_atr1_1/trade_ledgers/paper_trades_180d.json", "paper_trades_180d.json"),
            ("/momentum/artifacts/rank32b_shadow_global_live_like_backtest_atr1_1/trade_ledgers/monthly_summary_180d.json", "monthly_summary_180d.json"),
            ("/momentum/artifacts/rank32b_shadow_global_live_like_backtest_atr1_1/trade_ledgers/ten_day_segments_180d.json", "ten_day_segments_180d.json"),
        ],
    }
    atr_rows = []
    for days in (3, 10, 30, 60, 180):
        item = atr11_results.get(days) or atr11_results.get(str(days)) or {}
        metrics = (item.get("metrics") or {}) if isinstance(item, dict) else {}
        summary = (item.get("paper_summary") or {}) if isinstance(item, dict) else {}
        links = " · ".join([f"<a href=\"{href}\">{label}</a>" for href, label in atr_row_links.get(days, [])])
        atr_rows.append(
            f"<tr><td>{days}d</td><td>{sign_num(metrics.get('usdt_pnl_live_like'),2)}U</td>"
            f"<td>{summary.get('paper_closed_trades','-')}</td><td>{pct(metrics.get('closed_win_rate'))}</td><td>{links}</td></tr>"
        )
    if delta_720_minus_365 is not None and float(delta_720_minus_365) >= 0:
        delta_sub = "说明 365d 之前那段老历史到当前口径为正贡献"
        delta_read = (
            f"这次最新复算里，<b>720d 没有低于 365d</b>。更长历史不但没有拖累，"
            f"反而额外贡献了 <span class=\"good\">{sign_num(older_exact,2)}U</span>。"
        )
        month_title = "月度亏损月份（如果有的话）"
        month_read = (
            "这次 720d 月度拆解里暂时没有出现负收益月份，说明累计差异更多来自各月正收益厚薄不同，"
            "而不是某几个大亏月把曲线砸穿。"
            if negative_month_count == 0
            else "这张表专门用来盯哪些月份是净拖累。"
        )
        how_to_read_line = "如果你想确认长窗有没有拖后腿：看 <b>365d vs 720d</b> 差值卡片，再结合月度柱状图。当前最新结果里长窗是加分项。"
    elif delta_720_minus_365 is not None:
        delta_sub = "说明 365d 之前那段老历史到当前口径为负贡献"
        delta_read = (
            "更准确地说：<b>720d 比 365d 少，不等于老历史每天都亏</b>；"
            "而是更长历史里存在一些负贡献窗口，把多出来的那段累计收益拉低了。"
        )
        month_title = "负贡献月份（最值得盯）"
        month_read = "这张表专门用来盯哪些月份是净拖累。"
        how_to_read_line = "如果你想知道为什么 720d 低于 365d：看 <b>月度 PnL 柱状图</b> 和下面这张表。"
    else:
        delta_sub = "720d 仍在运行，暂时还没有最终差值"
        delta_read = "当前 <b>180d / 365d / 720d</b> 的旧 long-window live-like 结果已因 warmup 审计撤下；在修正版 backtest 重跑完成前，页面只保留 short-window official-close 与 recent-180d 稳定性。"
        month_title = "Long-window 月度拆解（withdrawn pending rerun）"
        month_read = "720d 结果尚未最终落盘，所以月度拆解和 older-than-365 贡献暂不展示；等 720d 跑完后再自动补齐。"
        how_to_read_line = "当前先看 180d / 365d 两张长期卡片；720d 完成后再看长窗扩展有没有增益或拖累。"
    data_json = json.dumps(payload, ensure_ascii=False)
    atr11_seg60_json = json.dumps(atr11.get("seg60") or [], ensure_ascii=False)
    atr11_mon60_json = json.dumps(atr11.get("mon60") or [], ensure_ascii=False)
    atr11_seg180_json = json.dumps(atr11.get("seg180") or [], ensure_ascii=False)
    atr11_mon180_json = json.dumps(atr11.get("mon180") or [], ensure_ascii=False)

    def rows(items: list[dict[str, Any]], limit: int = 12) -> str:
        body = []
        for row in items[:limit]:
            body.append(
                f"<tr><td>{row.get('month','-')}</td><td>{sign_num(row.get('pnl_usdt'),2)}</td><td>{row.get('trade_count','-')}</td><td>{pct(row.get('win_rate'))}</td><td>{pct(row.get('compound_trade_return'))}</td><td>{num(row.get('trade_sharpe'),2)}</td></tr>"
            )
        return "".join(body) if body else "<tr><td colspan='6'>暂无</td></tr>"

    html = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>32b global live-like 稳定性拆解（short-window only）</title>
  <style>
    :root{{--bg:#0b1120;--panel:#111827;--panel2:#0f172a;--line:#24324a;--text:#e5e7eb;--muted:#94a3b8;--accent:#7dd3fc;--good:#34d399;--bad:#f87171;--warn:#f59e0b;--blue:#60a5fa}}
    *{{box-sizing:border-box}}
    body{{margin:0;background:linear-gradient(180deg,#08101f,#0f172a);color:var(--text);font:15px/1.65 -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif}}
    .wrap{{max-width:1200px;margin:0 auto;padding:28px 20px 60px}}
    .card{{background:rgba(17,24,39,.94);border:1px solid var(--line);border-radius:18px;padding:18px 20px;margin-bottom:16px;box-shadow:0 10px 28px rgba(0,0,0,.22)}}
    .hero h1,.card h2,.card h3{{margin:0 0 8px}}
    p{{margin:0 0 10px;color:var(--muted)}}
    .lead{{color:#dbeafe;font-size:17px}}
    .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}}
    .stat{{background:rgba(15,23,42,.9);border:1px solid var(--line);border-radius:16px;padding:14px 16px}}
    .k{{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}}
    .v{{font-size:26px;font-weight:800;color:#f8fafc;margin-top:2px}}
    .sub{{font-size:13px;color:var(--muted);margin-top:4px}}
    .pill{{display:inline-block;padding:3px 8px;border-radius:999px;background:#13233f;border:1px solid #28456d;color:#bfdbfe;font-size:12px;margin-right:8px}}
    .charts{{display:grid;grid-template-columns:1fr;gap:14px}}
    .chart-box{{background:linear-gradient(180deg,rgba(11,17,32,.8),rgba(15,23,42,.5));border:1px solid rgba(125,211,252,.14);border-radius:14px;padding:10px}}
    svg{{display:block;width:100%;height:auto}}
    .twocol{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}
    @media (max-width: 920px){{.twocol{{grid-template-columns:1fr}}}}
    table{{width:100%;border-collapse:collapse;margin-top:8px;font-size:14px}}
    th,td{{padding:8px 10px;border-bottom:1px solid #22304a;text-align:left}}
    th{{color:#bfdbfe;font-weight:700}}
    .good{{color:var(--good)}} .bad{{color:var(--bad)}} .warn{{color:var(--warn)}}
    a{{color:var(--accent);text-decoration:none}}
    code{{color:#bfdbfe}}
    .iframe-wrap{{margin-top:12px;border:1px solid var(--line);border-radius:16px;overflow:hidden;background:#0b1120}}
    .iframe-wrap iframe{{display:block;width:100%;height:980px;border:0;background:#0b1120}}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <div class=\"card hero\">
      <div class=\"pill\">32b</div><div class=\"pill\">official-close</div><div class=\"pill\">live vs backtest</div>
      <h1>32b global live-like 稳定性拆解（short-window only）</h1>
      <p class=\"lead\">这页现在只保留一个主口径：<b>historical official-close backtest</b> 对照 <b>current official-close live</b>。目标不是继续讨论 preview，而是把 live 和回测放在同一条定义线上，后面持续审计它们是否逐步贴合。</p>
      <p>页面生成时间：{generated_at}</p>
      <p>当前页面里的历史基准只保留 <b>short-window official-close backtest</b> 与 <b>recent-180d stability</b>；旧的 180d / 365d / 720d live-like long-window 产物已因 warmup 审计撤下。本页当前统一使用的短窗基准时点是：{used_now}。</p>
      <p>当前 live 已切到 <b>15m official-close only</b>，在每个 <code>00/15/30/45</code> 分钟的 <code>:05</code> 触发，关闭 preview；这份页面现在只展示最近几小时内生成的短窗 / recent-180d 结果，long-window 部分等修正版 backtest 重跑后再恢复。</p>
      <p><b>口径审计说明：</b>本页只采用 <b>因果版 hourly EMA</b>：每根 15m bar 只引用 <b>上一根完整 1h</b> 的 EMA 基线，再用当前 bar close 做增量更新；不再使用会把同小时后段价格回灌到前半小时的旧 merge 方式。</p>
    </div>

    <div class=\"card\">
      <h2>Current Official Live</h2>
      <div class=\"grid\">
        <div class=\"stat\"><div class=\"k\">mode</div><div class=\"v\">official</div><div class=\"sub\">{entry_mode}</div></div>
        <div class=\"stat\"><div class=\"k\">current live ledger</div><div class=\"v\">{int(live.get('closed_trades', 0) or 0)} closed</div><div class=\"sub\">旧 preview/live 账本已归档，official 版本重新开始累计</div></div>
        <div class=\"stat\"><div class=\"k\">active position</div><div class=\"v\">{int(live.get('open_positions', 0) or 0)} open</div><div class=\"sub\">{active_position_text}</div></div>
        <div class=\"stat\"><div class=\"k\">last official run</div><div class=\"v\">{last_run_text.split(' / ')[-1].replace(' UTC','') if last_run_text != '-' else '-'}</div><div class=\"sub\">warnings={int(live.get('warnings', 0) or 0)} · archive={live.get('history_reset_archive','-')}</div></div>
      </div>
      <p style=\"margin-top:10px\">当前 live 的作用不是立刻证明盈利，而是先严格使用和回测一致的 <b>official-close 信号定义</b> 重新开始记账。等这条 official live 累够样本后，再和 180d / 365d / 720d official-close 基准做一对一对照。</p>
    </div>

    <div class=\"card\">
      <h2>Official-Close Backtest 基准</h2>
      <div class=\"grid\">
        <div class=\"stat\"><div class=\"k\">180d / 365d / 720d</div><div class=\"v bad\">withdrawn</div><div class=\"sub\">warmup audit 后暂不展示旧 long-window 数值</div></div>
        <div class=\"stat\"><div class=\"k\">status</div><div class=\"v\">audit hold</div><div class=\"sub\">需要用修正后的 backtest 重新生成 canonical ledger</div></div>
        <div class=\"stat\"><div class=\"k\">raw cache</div><div class=\"v\">retained</div><div class=\"sub\">1m day cache 保留，可复用到后续重跑</div></div>
        <div class=\"stat\"><div class=\"k\">next step</div><div class=\"v\">rerun</div><div class=\"sub\">先修正 warmup，再重跑 180/365/720</div></div>
      </div>
      <p style=\"margin-top:10px\">{delta_read}</p>
    </div>

    <div class=\"card\">
      <h2>短窗 Official-Close（已按完整 Warmup 修正）</h2>
      <p>这几档现在按统一口径重算：<b>评估窗口</b> 与 <b>signal warmup</b> 分离。当前配置下 <code>lookback_days=30</code>，因此短窗会按 <code>horizon + 30d</code> 拉历史 bars，再只评估最后目标窗口，避免继续出现 live / standalone / backtest 因 warmup 不足而分叉。</p>
      <div class=\"grid\">
        {''.join(short_cards)}
      </div>
    </div>

    <div class=\"card\">
      <h2>Official-Close（TP=1.00 ATR / SL=1.00 ATR）</h2>
      <p>这组是基于当前 official-close 回测链路，唯一把 exit 改成 <code>TP 1.00 ATR / SL 1.00 ATR</code> 后得到的独立结果；其他口径保持不变，仍然是 strongest-only / same-bar / same-symbol / max-concurrent=3 / timeout=120m / warmup=30d。</p>
      <div class=\"grid\">
        {''.join(atr_cards)}
      </div>
      <p style=\"margin-top:10px\">这组参数在 <b>30d</b> 上转正，但扩大到 <b>60d / 180d</b> 后重新转负。也就是说，<code>1.00 / 1.00 ATR</code> 对短窗有改善，但从目前样本看，还不足以把中窗整体拉回稳定盈利。</p>
      <table>
        <thead><tr><th>窗口</th><th>PnL</th><th>Closed Trades</th><th>Win Rate</th><th>Artifacts</th></tr></thead>
        <tbody>
          {''.join(atr_rows)}
        </tbody>
      </table>
    </div>

    <div class=\"card\">
      <h2>ATR 1.0 / 1.0 分段 PnL 折线图</h2>
      <p>下面两组图直接把 <code>60d</code> 和 <code>180d</code> 的 <b>10 天分段 PnL</b> 与 <b>月度 PnL</b> 摊开。这样你可以直观看到，这组参数是“持续偏弱”，还是“少数坏窗口把整体拉负”。</p>
      <div class=\"twocol\">
        <div class=\"chart-box\"><div class=\"sub\" style=\"margin:0 0 6px 4px\">60d · 10-day segments</div><svg id=\"atr10-seg60\" viewBox=\"0 0 1100 320\"></svg></div>
        <div class=\"chart-box\"><div class=\"sub\" style=\"margin:0 0 6px 4px\">60d · monthly pnl</div><svg id=\"atr10-mon60\" viewBox=\"0 0 1100 320\"></svg></div>
        <div class=\"chart-box\"><div class=\"sub\" style=\"margin:0 0 6px 4px\">180d · 10-day segments</div><svg id=\"atr10-seg180\" viewBox=\"0 0 1100 320\"></svg></div>
        <div class=\"chart-box\"><div class=\"sub\" style=\"margin:0 0 6px 4px\">180d · monthly pnl</div><svg id=\"atr10-mon180\" viewBox=\"0 0 1100 320\"></svg></div>
      </div>
    </div>

    <div class=\"card\">
      <h2>当前情况与目标</h2>
      <table>
        <thead><tr><th>项</th><th>说明</th></tr></thead>
        <tbody>
          <tr><td>主比较口径</td><td><b>official-close historical backtest</b> 对照 <b>official-close live</b>。preview 只保留为归档，不再作为主版本解释 live。</td></tr>
          <tr><td>当前状态</td><td>历史基准已经按 <b>causal hourly EMA</b> 重新复算；以本页卡片与 artifacts 为准。current official live 刚刚完成切换并重置账本，所以目前还没有足够 closed trades 证明 live 已经贴近 backtest。</td></tr>
          <tr><td>后续验收</td><td>先验证 live 与回测在 <b>signal 时间、入场币种、仓位、退出原因</b> 上逐步对齐；确认“定义一致”后，再看 live 是否沿着回测的盈利形状前进。</td></tr>
          <tr><td>页面用途</td><td>这页现在主要回答两个问题：<b>short-window official-close 基准最近稳不稳</b>，以及 <b>当前 official live 离这条短窗基准还有多远</b>。旧的 180d/365d/720d long-window live-like 结果已因 warmup 审计撤下，避免误读。</td></tr>
        </tbody>
      </table>
    </div>

    <div class=\"card\">
      <h2>最近 180d：18×10d / 6×30d 稳定性</h2>
      <p>这部分仍然保留，用来看 <b>修正后的 official-close 历史基准</b> 在最近 180 天到底稳不稳。也就是说，这里不是预设“最近一定强”，而是把分段结果摊开给你直接看。</p>
      <div class=\"grid\">
        <div class=\"stat\"><div class=\"k\">18 × 10d</div><div class=\"v\">{recent10_value}</div><div class=\"sub\">{recent10_sub}</div></div>
        <div class=\"stat\"><div class=\"k\">6 × 30d</div><div class=\"v\">{recent30_value}</div><div class=\"sub\">{recent30_sub}</div></div>
      </div>
      <div class=\"iframe-wrap\"><iframe src=\"/momentum/factors/rank32b/stability_snapshot.html\" title=\"32b 180d stability snapshot\"></iframe></div>
    </div>

    <div class=\"card\">
      <h2>720d：按月拆解，确认长窗贡献来自哪里</h2>
      <div class=\"charts\">
        <div class=\"chart-box\"><svg id=\"monthly-bars\" viewBox=\"0 0 1100 340\"></svg></div>
        <div class=\"chart-box\"><svg id=\"cum-line\" viewBox=\"0 0 1100 320\"></svg></div>
      </div>
      <p style=\"margin-top:10px\">{month_read}</p>
    </div>

    <div class=\"card\">
      <h2>滚动指标（3 个月窗口）</h2>
      <p>这里的 <b>rolling return</b> 用的是 <b>按成交序列复合的 trade-return proxy</b>，不是严格 capital-normalized 资金曲线收益；<b>rolling Sharpe</b> 是按这 3 个月窗口内成交序列的 trade Sharpe 算的。作用主要是看“这条策略在不同阶段有没有明显变钝”。</p>
      <div class=\"charts\">
        <div class=\"chart-box\"><svg id=\"rolling-return\" viewBox=\"0 0 1100 320\"></svg></div>
        <div class=\"chart-box\"><svg id=\"rolling-sharpe\" viewBox=\"0 0 1100 320\"></svg></div>
      </div>
    </div>

    <div class=\"card twocol\">
      <div>
        <h3>{month_title}</h3>
        <table>
          <thead><tr><th>Month</th><th>PnL</th><th>Trades</th><th>Win rate</th><th>Compound</th><th>Trade Sharpe</th></tr></thead>
          <tbody>{rows(sorted(negative, key=lambda x: float(x.get('pnl_usdt',0.0))))}</tbody>
        </table>
      </div>
      <div>
        <h3>滚动 3m 末端窗口</h3>
        <table>
          <thead><tr><th>Window</th><th>rolling PnL</th><th>Trades</th><th>rolling return</th><th>rolling Sharpe</th><th>positive months</th></tr></thead>
          <tbody>{''.join([f"<tr><td>{r['window_label']}</td><td>{sign_num(r['rolling_pnl_usdt'],2)}</td><td>{r['trade_count']}</td><td>{pct(r['rolling_compound_trade_return'])}</td><td>{num(r['rolling_trade_sharpe'],2)}</td><td>{r['positive_months']}/3</td></tr>" for r in rolling_3m[-8:]]) or '<tr><td colspan="6">暂无</td></tr>'}</tbody>
        </table>
      </div>
    </div>

    <div class=\"card\">
      <h2>Artifacts</h2>
      <table>
        <thead><tr><th>项</th><th>链接</th></tr></thead>
        <tbody>
          <tr><td>official-close monthly json</td><td><a href=\"/momentum/artifacts/rank32b_shadow_global_live_like_backtest/monthly_stability_720d.json\">monthly_stability_720d.json</a></td></tr>
          <tr><td>official-close monthly md</td><td><a href=\"/momentum/artifacts/rank32b_shadow_global_live_like_backtest/monthly_stability_720d.md\">monthly_stability_720d.md</a></td></tr>
          <tr><td>current official live dashboard</td><td><a href=\"/momentum/factors/rank32b_global_live/report.html\">rank32b_global_live/report.html</a></td></tr>
          <tr><td>archived preview/live ledger</td><td><a href=\"/momentum/artifacts/rank32b_global_live/archive/{live.get('history_reset_archive','official_transition_20260405T101057Z')}/live_recent_closed_trades.json\">archived closed trades</a></td></tr>
        </tbody>
      </table>
    </div>

    <div class=\"card\">
      <h2>怎么读这页</h2>
      <ul>
        <li>先看 <b>Current Official Live</b>，确认现在讨论的 live 已经是 official-close 版本，而不是 preview。</li>
        <li>再看 <b>Official-Close Backtest 基准</b>，确认 365d / 720d 历史基准本身是什么形状。</li>
        <li>{how_to_read_line}</li>
        <li>如果你想判断 historical official-close 最近是否变钝，再看 <b>180d stability</b> 和 <b>rolling 3m return / Sharpe</b>；本页这些分段结果也已经切到修正后的因果口径。</li>
      </ul>
      <p>当前目标很明确：先确保 <b>live 和回测可以对照</b>，再去验证 <b>live 是否会像回测一样盈利</b>。数据源：<code>backtest_windows.json</code> + <code>stability_180d.json</code> + <code>rank32b_global_live</code> 当前 live artifacts。</p>
    </div>
  </div>

  <script>
    const payload = {data_json};
    const months = payload.monthly.months || [];
    const rolling3 = payload.rolling_3m || [];
    const atr10Seg60 = {atr11_seg60_json};
    const atr10Mon60 = {atr11_mon60_json};
    const atr10Seg180 = {atr11_seg180_json};
    const atr10Mon180 = {atr11_mon180_json};

    function axisTicks(min, max, count) {{
      if (min === max) return [min];
      const out = [];
      for (let i = 0; i <= count; i++) out.push(min + (max-min)*i/count);
      return out;
    }}

    function makeSvgEl(name, attrs = {{}}, text = null) {{
      const ns = 'http://www.w3.org/2000/svg';
      const el = document.createElementNS(ns, name);
      Object.entries(attrs).forEach(([k,v]) => el.setAttribute(k, String(v)));
      if (text != null) el.textContent = text;
      return el;
    }}

    function drawBarChart(svgId, data, valueKey, labelKey, opts = {{}}) {{
      const svg = document.getElementById(svgId); if (!svg) return;
      const W = 1100, H = 340, pad = {{l:60,r:20,t:18,b:56}};
      const innerW = W-pad.l-pad.r, innerH = H-pad.t-pad.b;
      const vals = data.map(d => Number(d[valueKey] || 0));
      const minV = Math.min(0, ...vals) * 1.15;
      const maxV = Math.max(0, ...vals) * 1.15 || 1;
      const y = v => pad.t + innerH - ((v-minV)/(maxV-minV))*innerH;
      const xStep = innerW / Math.max(1, data.length);
      const barW = Math.max(8, xStep * 0.66);
      const zeroY = y(0);
      axisTicks(minV, maxV, 4).forEach(t => {{
        const yy = y(t);
        svg.appendChild(makeSvgEl('line', {{x1:pad.l,y1:yy,x2:W-pad.r,y2:yy,stroke:'rgba(148,163,184,.16)','stroke-width':1}}));
        svg.appendChild(makeSvgEl('text', {{x:pad.l-10,y:yy+4,'text-anchor':'end',fill:'#94a3b8','font-size':12}}, `${{t.toFixed(0)}}U`));
      }});
      svg.appendChild(makeSvgEl('line', {{x1:pad.l,y1:zeroY,x2:W-pad.r,y2:zeroY,stroke:'rgba(148,163,184,.32)','stroke-width':1.2}}));
      data.forEach((d, i) => {{
        const v = Number(d[valueKey] || 0);
        const x = pad.l + i*xStep + (xStep-barW)/2;
        const yy = y(Math.max(v,0));
        const h = Math.abs(y(v)-zeroY);
        const fill = v >= 0 ? 'rgba(52,211,153,.82)' : 'rgba(248,113,113,.82)';
        const rect = makeSvgEl('rect', {{x, y: v>=0 ? yy : zeroY, width:barW, height:Math.max(1,h), rx:4, fill}});
        rect.appendChild(makeSvgEl('title', {{}}, `${{d[labelKey]}} | ${{v >= 0 ? '+' : ''}}${{v.toFixed(2)}}U`));
        svg.appendChild(rect);
        const show = data.length <= 18 || i % 2 === 0 || i === data.length-1;
        if (show) svg.appendChild(makeSvgEl('text', {{x:x+barW/2, y:H-pad.b+18, 'text-anchor':'middle', fill:'#94a3b8', 'font-size':11}}, d[labelKey]));
      }});
    }}

    function drawLineChart(svgId, data, valueKey, labelKey, color, suffix='', zeroLine=false) {{
      const svg = document.getElementById(svgId); if (!svg || !data.length) return;
      const W = 1100, H = 320, pad = {{l:60,r:20,t:18,b:50}};
      const innerW = W-pad.l-pad.r, innerH = H-pad.t-pad.b;
      const vals = data.map(d => Number(d[valueKey] ?? 0)).filter(v => Number.isFinite(v));
      let minV = Math.min(...vals), maxV = Math.max(...vals);
      if (!Number.isFinite(minV) || !Number.isFinite(maxV)) {{ minV = 0; maxV = 1; }}
      if (zeroLine) {{ minV = Math.min(minV, 0); maxV = Math.max(maxV, 0); }}
      if (minV === maxV) {{ minV -= 1; maxV += 1; }}
      minV *= (minV < 0 ? 1.15 : 0.92); maxV *= (maxV > 0 ? 1.15 : 0.92);
      const x = i => pad.l + (data.length === 1 ? innerW/2 : i * innerW / (data.length-1));
      const y = v => pad.t + innerH - ((v-minV)/(maxV-minV))*innerH;
      axisTicks(minV, maxV, 4).forEach(t => {{
        const yy = y(t);
        svg.appendChild(makeSvgEl('line', {{x1:pad.l,y1:yy,x2:W-pad.r,y2:yy,stroke:'rgba(148,163,184,.16)','stroke-width':1}}));
        svg.appendChild(makeSvgEl('text', {{x:pad.l-10,y:yy+4,'text-anchor':'end',fill:'#94a3b8','font-size':12}}, `${{t.toFixed(2)}}${{suffix}}`));
      }});
      if (zeroLine) {{
        svg.appendChild(makeSvgEl('line', {{x1:pad.l,y1:y(0),x2:W-pad.r,y2:y(0),stroke:'rgba(248,113,113,.32)','stroke-width':1.2}}));
      }}
      const pts = data.map((d,i) => `${{x(i)}},${{y(Number(d[valueKey] ?? 0))}}`).join(' ');
      svg.appendChild(makeSvgEl('polyline', {{points:pts, fill:'none', stroke:color, 'stroke-width':3, 'stroke-linecap':'round', 'stroke-linejoin':'round'}}));
      data.forEach((d,i) => {{
        const cx = x(i), cy = y(Number(d[valueKey] ?? 0));
        const c = makeSvgEl('circle', {{cx,cy,r:4.5,fill:'#0b1120',stroke:color,'stroke-width':2}});
        c.appendChild(makeSvgEl('title', {{}}, `${{d[labelKey]}} | ${{Number(d[valueKey] ?? 0).toFixed(4)}}${{suffix}}`));
        svg.appendChild(c);
        const show = data.length <= 18 || i % 2 === 0 || i === data.length-1;
        if (show) svg.appendChild(makeSvgEl('text', {{x:cx, y:H-pad.b+18, 'text-anchor':'middle', fill:'#94a3b8', 'font-size':11}}, d[labelKey]));
      }});
    }}

    drawBarChart('monthly-bars', months, 'pnl_usdt', 'month');
    drawLineChart('cum-line', months, 'cum_pnl_usdt', 'month', '#60a5fa', 'U', true);
    drawLineChart('rolling-return', rolling3.map(x => ({{...x, val:(Number(x.rolling_compound_trade_return||0)*100)}})), 'val', 'end_month', '#34d399', '%', true);
    drawLineChart('rolling-sharpe', rolling3.map(x => ({{...x, val:Number(x.rolling_trade_sharpe ?? 0)}})), 'val', 'end_month', '#f59e0b', '', true);
    drawLineChart('atr10-seg60', atr10Seg60, 'pnl_usdt', 'label', '#38bdf8', 'U', true);
    drawLineChart('atr10-mon60', atr10Mon60, 'pnl_usdt', 'label', '#34d399', 'U', true);
    drawLineChart('atr10-seg180', atr10Seg180, 'pnl_usdt', 'label', '#f59e0b', 'U', true);
    drawLineChart('atr10-mon180', atr10Mon180, 'pnl_usdt', 'label', '#f87171', 'U', true);
  </script>
</body>
</html>
"""
    OUT_HTML.write_text(html, encoding="utf-8")


def main() -> int:
    payload = build_payload()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(payload)
    write_html(payload)
    print(json.dumps({
        "json": str(OUT_JSON),
        "html": str(OUT_HTML),
        "used_backtest_now_utc": payload.get("used_backtest_now_utc"),
        "delta_720_minus_365_usdt": ((payload.get("comparison") or {}).get("delta_720_minus_365_usdt")),
        "negative_month_count": ((payload.get("monthly") or {}).get("negative_month_count")),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
