#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from momentum.signals.trendline_breakout_navigator import (  # noqa: E402
    TrendlineBreakoutNavigatorConfig,
    compute_trendline_breakout_navigator,
)
from run_manual_narrow_paper_lanes import (  # noqa: E402
    ASSET_TO_BINANCE,
    build_rank29_trades_causal,
    build_rank29_trades_confirmed_lines,
    compute_rank29_gate_daily_flags,
    download_binance_bars,
    load_rank29_gate_thresholds,
)

SITE_DIR = ROOT / "reports" / "site" / "factors" / "rank29_monitoring_hub"
OUT_PATH = SITE_DIR / "report.html"

ART_DIR = ROOT / "reports" / "artifacts" / "manual_narrow_paper_lanes"
LIVE_DIR = ROOT / "reports" / "artifacts" / "rank29_gate_live"
ORD_DIR = ROOT / "reports" / "artifacts" / "rank29_orderbook_shadow"

SHADOW_VIEW_PATH = ART_DIR / "rank29_shadow_trade_view.csv"
ACTUAL_LEDGER_PATH = ART_DIR / "manual_narrow_paper_closed_trades.csv"
STATUS_CSV_PATH = ART_DIR / "manual_narrow_paper_status.csv"
RUN_SUMMARY_PATH = ART_DIR / "manual_narrow_paper_last_run_summary.json"

LIVE_STATE_PATH = LIVE_DIR / "rank29_gate_live_state.json"
LIVE_STATUS_PATH = LIVE_DIR / "rank29_gate_live_status.json"
LIVE_COMPARE_PATH = LIVE_DIR / "rank29_gate_live_vs_shadow.csv"
LIVE_REJECTIONS_PATH = LIVE_DIR / "rank29_gate_live_recent_rejections.json"
LIVE_WARNINGS_PATH = LIVE_DIR / "rank29_gate_live_warnings.json"
LIVE_ORDERS_PATH = LIVE_DIR / "rank29_gate_live_recent_orders.json"

ORDERBOOK_STATUS_PATH = ORD_DIR / "shadow_status.csv"

BASELINE_ID = "rank29_trendline_breakout_navigator"
GATE_ID = "rank29_trendline_breakout_gate_shadow"
EXAMPLE_ASSET = "SOL-USD"
EXAMPLE_SIGNAL_TS = pd.Timestamp("2026-04-02T16:30:00Z")
EXAMPLE_CONFIG = TrendlineBreakoutNavigatorConfig()
SIGNAL_AUDIT_DAYS = 7


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


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def fmt_ts(v: Any) -> str:
    if v is None or v == "" or pd.isna(v):
        return "-"
    try:
        return pd.to_datetime(v, utc=True).strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return str(v)


def money(v: Any, digits: int = 3) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f} USDT"


def pct(v: Any, digits: int = 1) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def num(v: Any, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f}"


def safe_num(series: pd.Series | Any) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def summarize(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {"trades": 0, "wins": 0, "losses": 0, "win_rate": None, "cum_pnl": 0.0}
    pnl = safe_num(df["pnl_usdt"]).fillna(0.0)
    trades = len(df)
    wins = int((pnl > 0).sum())
    losses = int((pnl < 0).sum())
    return {
        "trades": trades,
        "wins": wins,
        "losses": losses,
        "win_rate": (wins / trades) if trades else None,
        "cum_pnl": float(pnl.sum()),
    }


def prep_rank29_shadow_view() -> tuple[pd.DataFrame, pd.DataFrame]:
    df = read_csv(SHADOW_VIEW_PATH)
    empty = pd.DataFrame(columns=["ts", "symbol", "side", "pnl_usdt", "exit_reason"])
    if df.empty:
        return empty, empty
    if "candidate_id" not in df.columns:
        return empty, empty
    df = df.copy()
    df["ts"] = pd.to_datetime(df.get("exit_ts"), utc=True, errors="coerce")
    df["pnl_usdt"] = safe_num(df.get("net_ret", 0.0)).fillna(0.0) * 100.0
    symbol_series = df["symbol"] if "symbol" in df.columns else pd.Series([None] * len(df), index=df.index)
    asset_series = df["asset"] if "asset" in df.columns else pd.Series([None] * len(df), index=df.index)
    side_series = df["direction"] if "direction" in df.columns else pd.Series([None] * len(df), index=df.index)
    exit_reason_series = df["exit_reason"] if "exit_reason" in df.columns else pd.Series([None] * len(df), index=df.index)
    df["symbol"] = symbol_series.fillna(asset_series).astype(str)
    df["side"] = side_series.fillna("").astype(str)
    df["exit_reason"] = exit_reason_series.fillna("shadow_close").astype(str)
    df = df[df["ts"].notna()].sort_values("ts").reset_index(drop=True)
    keep = ["ts", "symbol", "side", "pnl_usdt", "exit_reason"]
    baseline = df[df["candidate_id"] == BASELINE_ID][keep].reset_index(drop=True)
    gate = df[df["candidate_id"] == GATE_ID][keep].reset_index(drop=True)
    return baseline, gate


def prep_live_trades() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any], dict[str, Any]]:
    state = read_json(LIVE_STATE_PATH, {}) or {}
    status = read_json(LIVE_STATUS_PATH, {}) or {}
    rows = state.get("closed_trades", []) or []
    if not rows:
        live_df = pd.DataFrame(columns=["ts", "symbol", "side", "pnl_usdt", "exit_reason", "entry_time", "exit_time"])
    else:
        live_df = pd.DataFrame(rows).copy()
        live_df["ts"] = pd.to_datetime(live_df.get("exit_time"), utc=True, errors="coerce")
        live_df["pnl_usdt"] = safe_num(live_df.get("net_pnl", 0.0)).fillna(safe_num(live_df.get("gross_pnl", 0.0))).fillna(0.0)
        live_df["symbol"] = live_df.get("symbol", "").astype(str)
        live_df["side"] = live_df.get("side", "").astype(str)
        live_df["exit_reason"] = live_df.get("exit_reason", "").astype(str)
        live_df = live_df[live_df["ts"].notna()].sort_values("ts").reset_index(drop=True)
    open_df = pd.DataFrame(state.get("live_positions", []) or [])
    return live_df, open_df, state, status


def line_chart_svg(series_list: list[dict[str, Any]], *, width: int = 980, height: int = 280) -> str:
    valid = [s for s in series_list if s.get("values")]
    if not valid:
        return '<div class="empty">暂无可绘制的累计收益曲线。</div>'
    max_len = max(len(s["values"]) for s in valid)
    all_y = [0.0]
    for s in valid:
        all_y.extend(float(v) for v in s["values"])
    ymin, ymax = min(all_y), max(all_y)
    span = max(ymax - ymin, 1e-9)
    ymin -= span * 0.12 + 1e-9
    ymax += span * 0.12 + 1e-9
    plot_x, plot_y, plot_w, plot_h = 56, 18, width - 76, height - 52

    def xy(idx: int, total: int, val: float) -> tuple[float, float]:
        x = plot_x + (plot_w / 2 if total <= 1 else (idx / (total - 1)) * plot_w)
        y = plot_y + plot_h - ((val - ymin) / (ymax - ymin)) * plot_h
        return x, y

    zero_y = xy(0, 1, 0.0)[1]
    parts = [
        f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" role="img">',
        f'<line x1="{plot_x}" y1="{zero_y:.2f}" x2="{plot_x + plot_w}" y2="{zero_y:.2f}" stroke="#334155" stroke-dasharray="4 4" />',
        f'<rect x="{plot_x}" y="{plot_y}" width="{plot_w}" height="{plot_h}" rx="12" fill="none" stroke="#1f2937" />',
    ]
    legend_x = plot_x
    for s in valid:
        pts = [xy(i, len(s["values"]), float(v)) for i, v in enumerate(s["values"])]
        path = " ".join(("M" if i == 0 else "L") + f" {x:.2f} {y:.2f}" for i, (x, y) in enumerate(pts))
        parts.append(f'<path d="{path}" fill="none" stroke="{s["color"]}" stroke-width="2.5" />')
        last_x, last_y = pts[-1]
        parts.append(f'<circle cx="{last_x:.2f}" cy="{last_y:.2f}" r="3.6" fill="{s["color"]}" />')
        parts.append(f'<rect x="{legend_x}" y="{height - 18}" width="11" height="11" rx="3" fill="{s["color"]}" />')
        parts.append(f'<text x="{legend_x + 17}" y="{height - 8}" fill="#cbd5e1" font-size="12">{escape(str(s["label"]))}</text>')
        legend_x += 150
    parts.append(f'<text x="8" y="{plot_y + 10}" fill="#94a3b8" font-size="11">{money(ymax, 1)}</text>')
    parts.append(f'<text x="8" y="{zero_y - 4:.2f}" fill="#64748b" font-size="11">0</text>')
    parts.append(f'<text x="8" y="{plot_y + plot_h}" fill="#94a3b8" font-size="11">{money(ymin, 1)}</text>')
    parts.append("</svg>")
    return "".join(parts)


def strip_chart_svg(df: pd.DataFrame, title: str, *, width: int = 980, height: int = 120) -> str:
    if df.empty:
        return f'<div class="empty">{escape(title)}：暂无数据。</div>'
    pnl = safe_num(df["pnl_usdt"]).fillna(0.0).tolist()
    max_abs = max(max(abs(v) for v in pnl), 1e-9)
    plot_x, plot_y, plot_w, plot_h = 34, 10, width - 46, height - 22
    center_y = plot_y + plot_h / 2
    parts = [
        f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" role="img">',
        f'<line x1="{plot_x}" y1="{center_y:.2f}" x2="{plot_x + plot_w}" y2="{center_y:.2f}" stroke="#334155" stroke-dasharray="4 4" />',
    ]
    total = len(pnl)
    for i, value in enumerate(pnl):
        x = plot_x + (plot_w / max(total - 1, 1)) * i if total > 1 else plot_x + plot_w / 2
        y = center_y - (value / max_abs) * (plot_h * 0.38)
        color = "#22c55e" if value > 0 else ("#ef4444" if value < 0 else "#94a3b8")
        parts.append(f'<line x1="{x:.2f}" y1="{center_y:.2f}" x2="{x:.2f}" y2="{y:.2f}" stroke="{color}" stroke-width="2.2" />')
        parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3" fill="{color}" />')
    parts.append(f'<text x="4" y="14" fill="#94a3b8" font-size="11">win</text>')
    parts.append(f'<text x="4" y="{center_y + 4:.2f}" fill="#64748b" font-size="11">0</text>')
    parts.append(f'<text x="4" y="{height - 6}" fill="#94a3b8" font-size="11">loss</text>')
    parts.append("</svg>")
    return "".join(parts)


def curve_spec(df: pd.DataFrame, label: str, color: str) -> dict[str, Any]:
    if df.empty:
        return {"label": label, "color": color, "values": []}
    work = df.sort_values("ts").copy().reset_index(drop=True)
    work["cum_pnl"] = safe_num(work["pnl_usdt"]).fillna(0.0).cumsum()
    return {"label": label, "color": color, "values": work["cum_pnl"].tolist()}


def _normalize_rank29_trade_frame(df: pd.DataFrame, *, asset: str | None = None) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["asset", "event_ts", "entry_ts", "exit_ts", "direction", "trigger_tf", "signal_key"])
    out = df.copy()
    if asset is not None:
        out["asset"] = asset
    elif "asset" not in out.columns:
        out["asset"] = ""
    for col in ["event_ts", "entry_ts", "exit_ts"]:
        if col in out.columns:
            out[col] = pd.to_datetime(out[col], utc=True, errors="coerce")
    out = out[out.get("event_ts", pd.Series(dtype="datetime64[ns, UTC]")).notna()].copy()
    direction_series = out["direction"] if "direction" in out.columns else pd.Series([""] * len(out), index=out.index)
    trigger_series = out["trigger_tf"] if "trigger_tf" in out.columns else pd.Series([""] * len(out), index=out.index)
    out["direction"] = direction_series.fillna("").astype(str)
    out["trigger_tf"] = trigger_series.fillna("").astype(str)
    out["signal_key"] = (
        out["asset"].astype(str)
        + "|"
        + out["event_ts"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        + "|"
        + out["direction"]
        + "|"
        + out["trigger_tf"]
    )
    return out


def _split_rank29_signal_sets(confirmed_df: pd.DataFrame, causal_df: pd.DataFrame, *, asset: str) -> dict[str, pd.DataFrame]:
    confirmed = _normalize_rank29_trade_frame(confirmed_df, asset=asset)
    causal = _normalize_rank29_trade_frame(causal_df, asset=asset)
    causal_keys = set(causal["signal_key"]) if not causal.empty else set()
    confirmed_keys = set(confirmed["signal_key"]) if not confirmed.empty else set()
    overlap = confirmed[confirmed["signal_key"].isin(causal_keys)].copy()
    hindsight_only = confirmed[~confirmed["signal_key"].isin(causal_keys)].copy()
    causal_only = causal[~causal["signal_key"].isin(confirmed_keys)].copy()
    return {
        "confirmed": confirmed,
        "causal": causal,
        "overlap": overlap,
        "hindsight_only": hindsight_only,
        "causal_only": causal_only,
    }


def build_recent_signal_honesty_audit(*, days: int = SIGNAL_AUDIT_DAYS) -> dict[str, Any]:
    asset_rows: list[dict[str, Any]] = []
    detail_frames: list[pd.DataFrame] = []
    total_confirmed = 0
    total_causal = 0
    total_hindsight_only = 0
    for asset, symbol in ASSET_TO_BINANCE.items():
        bars = download_binance_bars(symbol, interval="15m", days=days)
        if bars.empty:
            continue
        confirmed = build_rank29_trades_confirmed_lines(asset, bars)
        causal = build_rank29_trades_causal(asset, bars)
        split = _split_rank29_signal_sets(confirmed, causal, asset=asset)
        confirmed_n = split["confirmed"]
        causal_n = split["causal"]
        hindsight_only = split["hindsight_only"]
        total_confirmed += len(confirmed_n)
        total_causal += len(causal_n)
        total_hindsight_only += len(hindsight_only)
        latest_hindsight_ts = hindsight_only["event_ts"].max() if not hindsight_only.empty else pd.NaT
        asset_rows.append(
            {
                "asset": asset,
                "hindsight_signals": len(confirmed_n),
                "causal_signals": len(causal_n),
                "hindsight_only": len(hindsight_only),
                "misleading_pct": (len(hindsight_only) / len(confirmed_n)) if len(confirmed_n) else pd.NA,
                "latest_hindsight_only": latest_hindsight_ts,
            }
        )
        if not hindsight_only.empty:
            detail = hindsight_only[[c for c in ["asset", "event_ts", "direction", "trigger_tf", "entry_ts"] if c in hindsight_only.columns]].copy()
            detail_frames.append(detail)
    per_asset_df = pd.DataFrame(asset_rows)
    if not per_asset_df.empty and "latest_hindsight_only" in per_asset_df.columns:
        per_asset_df["latest_hindsight_only"] = pd.to_datetime(per_asset_df["latest_hindsight_only"], utc=True, errors="coerce")
    detail_df = pd.concat(detail_frames, ignore_index=True) if detail_frames else pd.DataFrame(columns=["asset", "event_ts", "direction", "trigger_tf", "entry_ts"])
    misleading_pct = (total_hindsight_only / total_confirmed) if total_confirmed else None
    return {
        "days": days,
        "confirmed_signals": total_confirmed,
        "causal_signals": total_causal,
        "hindsight_only_signals": total_hindsight_only,
        "misleading_pct": misleading_pct,
        "causal_kept_pct": ((total_confirmed - total_hindsight_only) / total_confirmed) if total_confirmed else None,
        "per_asset_df": per_asset_df,
        "detail_df": detail_df,
    }


def build_signal_example() -> dict[str, Any]:
    symbol = ASSET_TO_BINANCE[EXAMPLE_ASSET]
    bars = download_binance_bars(symbol, interval="15m", days=7)
    if bars.empty:
        return {}
    bars = bars.copy()
    bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True, errors="coerce")
    nav = compute_trendline_breakout_navigator(
        bars[["timestamp", "high", "low", "close"]].copy(),
        config=EXAMPLE_CONFIG,
    )
    nav["timestamp"] = pd.to_datetime(nav["timestamp"], utc=True, errors="coerce")
    full = bars.merge(nav.drop(columns=["high", "low", "close"], errors="ignore"), on="timestamp", how="left")
    full = full.reset_index(drop=True)
    full["bar_index"] = full.index

    confirmed_trades = build_rank29_trades_confirmed_lines(EXAMPLE_ASSET, bars)
    causal_trades = build_rank29_trades_causal(EXAMPLE_ASSET, bars)
    split = _split_rank29_signal_sets(confirmed_trades, causal_trades, asset=EXAMPLE_ASSET)
    confirmed_trades = split["confirmed"]
    causal_trades = split["causal"]
    hindsight_only_trades = split["hindsight_only"]

    selected_trade = pd.DataFrame()
    example_kind = ""
    if not causal_trades.empty:
        exact = causal_trades[causal_trades["event_ts"] == EXAMPLE_SIGNAL_TS].copy()
        selected_trade = exact if not exact.empty else causal_trades.sort_values("event_ts").tail(1).copy()
        example_kind = "causal"
    elif not hindsight_only_trades.empty:
        exact = hindsight_only_trades[hindsight_only_trades["event_ts"] == EXAMPLE_SIGNAL_TS].copy()
        selected_trade = exact if not exact.empty else hindsight_only_trades.sort_values("event_ts").tail(1).copy()
        example_kind = "hindsight_only"
    elif not confirmed_trades.empty:
        selected_trade = confirmed_trades.sort_values("event_ts").tail(1).copy()
        example_kind = "confirmed_only"
    if selected_trade.empty:
        return {}

    for col in ["event_ts", "entry_ts", "exit_ts"]:
        if col in selected_trade.columns:
            selected_trade[col] = pd.to_datetime(selected_trade[col], utc=True, errors="coerce")
    trade_row = selected_trade.iloc[0].to_dict()
    signal_ts = pd.Timestamp(trade_row["event_ts"])

    window = full[(full["timestamp"] >= signal_ts - pd.Timedelta(hours=4)) & (full["timestamp"] <= signal_ts + pd.Timedelta(hours=3))].copy().reset_index(drop=True)
    overview_window = full[(full["timestamp"] >= signal_ts - pd.Timedelta(hours=36)) & (full["timestamp"] <= signal_ts + pd.Timedelta(hours=28))].copy().reset_index(drop=True)

    bars_cache = {asset: download_binance_bars(sym, interval="15m", days=60) for asset, sym in ASSET_TO_BINANCE.items()}
    thresholds = load_rank29_gate_thresholds()
    gate = compute_rank29_gate_daily_flags(bars_cache, thresholds)
    if not gate.empty:
        for col in ["timestamp", "effective_for_trade_day"]:
            if col in gate.columns:
                gate[col] = pd.to_datetime(gate[col], utc=True, errors="coerce")
        trade_day = pd.Timestamp(trade_row["entry_ts"]).floor("D") if pd.notna(trade_row.get("entry_ts")) else pd.NaT
        gate_row = gate[gate["effective_for_trade_day"] == trade_day].head(1) if pd.notna(trade_day) else pd.DataFrame()
        gate_info = gate_row.iloc[0].to_dict() if not gate_row.empty else {}
    else:
        gate_info = {}

    trigger_row_df = full[full["timestamp"] == signal_ts].head(1)
    hindsight_trigger_row = trigger_row_df.iloc[0].to_dict() if not trigger_row_df.empty else {}

    causal_prefix_bars = bars[bars["timestamp"] <= signal_ts].copy().reset_index(drop=True)
    causal_nav = compute_trendline_breakout_navigator(
        causal_prefix_bars[["timestamp", "high", "low", "close"]].copy(),
        config=EXAMPLE_CONFIG,
    )
    causal_nav["timestamp"] = pd.to_datetime(causal_nav["timestamp"], utc=True, errors="coerce")
    causal_full = causal_prefix_bars.merge(causal_nav.drop(columns=["high", "low", "close"], errors="ignore"), on="timestamp", how="left")
    causal_full = causal_full.reset_index(drop=True)
    causal_full["bar_index"] = causal_full.index
    causal_trigger_df = causal_full[causal_full["timestamp"] == signal_ts].tail(1)
    causal_trigger_row = causal_trigger_df.iloc[0].to_dict() if not causal_trigger_df.empty else {}

    def _idx_to_ts(frame: pd.DataFrame, idx_val: Any) -> str:
        try:
            idx_int = int(idx_val)
        except Exception:
            return "-"
        if idx_int < 0 or idx_int >= len(frame):
            return "-"
        return fmt_ts(frame.iloc[idx_int]["timestamp"])

    def _formula_from_row(row: dict[str, Any], frame: pd.DataFrame) -> dict[str, Any]:
        medium_anchor_origin = row.get("tbn_medium_anchor_origin", -1)
        medium_pivot_origin = row.get("tbn_medium_active_pivot_origin", -1)
        signal_idx = frame.index[frame["timestamp"] == signal_ts].tolist()
        signal_bar_index = signal_idx[0] if signal_idx else None
        signal_close = safe_num(pd.Series([row.get("close")])).iloc[0]
        line_value = safe_num(pd.Series([row.get("tbn_medium_line_value")])).iloc[0]
        return {
            "short_trend": int(row.get("tbn_short_trend", 0) or 0),
            "medium_trend": int(row.get("tbn_medium_trend", 0) or 0),
            "long_trend": int(row.get("tbn_long_trend", 0) or 0),
            "composite_trend": int(row.get("tbn_composite_trend", 0) or 0),
            "medium_anchor_origin": int(medium_anchor_origin) if pd.notna(medium_anchor_origin) else -1,
            "medium_anchor_price": safe_num(pd.Series([row.get("tbn_medium_anchor_price")])).iloc[0],
            "medium_pivot_origin": int(medium_pivot_origin) if pd.notna(medium_pivot_origin) else -1,
            "medium_pivot_price": safe_num(pd.Series([row.get("tbn_medium_active_pivot_price")])).iloc[0],
            "medium_line_slope": safe_num(pd.Series([row.get("tbn_medium_line_slope")])).iloc[0],
            "medium_line_value": line_value,
            "medium_anchor_ts": _idx_to_ts(frame, medium_anchor_origin),
            "medium_pivot_ts": _idx_to_ts(frame, medium_pivot_origin),
            "signal_bar_index": signal_bar_index,
            "signal_close": signal_close,
            "signal_open": safe_num(pd.Series([row.get("open")])).iloc[0],
            "signal_high": safe_num(pd.Series([row.get("high")])).iloc[0],
            "signal_low": safe_num(pd.Series([row.get("low")])).iloc[0],
            "close_minus_line": signal_close - line_value if pd.notna(signal_close) and pd.notna(line_value) else pd.NA,
        }

    hindsight_formula = _formula_from_row(hindsight_trigger_row, full) if hindsight_trigger_row else {}
    causal_formula = _formula_from_row(causal_trigger_row, causal_full) if causal_trigger_row else {}
    selected_formula = causal_formula if example_kind == "causal" else hindsight_formula
    selected_trigger_row = causal_trigger_row if example_kind == "causal" else hindsight_trigger_row

    breakout_rows: list[dict[str, Any]] = []
    for _, row in overview_window.iterrows():
        comp = int(row.get("tbn_composite_trend", 0) or 0)
        chosen_side = None
        chosen_tf = None
        for prefix in ["short", "medium", "long"]:
            if int(row.get(f"tbn_{prefix}_line_is_provisional", 0) or 0) == 1:
                continue
            if int(row.get(f"tbn_{prefix}_breakout_bull", 0) or 0) == 1 and comp >= 2:
                chosen_side = "long"
                chosen_tf = prefix
                break
            if int(row.get(f"tbn_{prefix}_breakout_bear", 0) or 0) == 1 and comp <= -2:
                chosen_side = "short"
                chosen_tf = prefix
                break
        if chosen_side is not None and chosen_tf is not None:
            breakout_rows.append(
                {
                    "timestamp": row.get("timestamp"),
                    "timeframe": chosen_tf,
                    "side": chosen_side,
                    "close": row.get("close"),
                    "trend_score": comp,
                    "line_value": row.get(f"tbn_{chosen_tf}_line_value"),
                    "line_is_provisional": row.get(f"tbn_{chosen_tf}_line_is_provisional"),
                }
            )
    overview_breakouts_df = pd.DataFrame(breakout_rows)

    overview_start = overview_window["timestamp"].min() if not overview_window.empty else pd.NaT
    overview_end = overview_window["timestamp"].max() if not overview_window.empty else pd.NaT
    overview_causal_signals_df = causal_trades[(causal_trades["event_ts"] >= overview_start) & (causal_trades["event_ts"] <= overview_end)].copy() if pd.notna(overview_start) else pd.DataFrame()
    overview_hindsight_only_df = hindsight_only_trades[(hindsight_only_trades["event_ts"] >= overview_start) & (hindsight_only_trades["event_ts"] <= overview_end)].copy() if pd.notna(overview_start) else pd.DataFrame()
    if not overview_causal_signals_df.empty:
        overview_causal_signals_df = overview_causal_signals_df.rename(columns={"event_ts": "timestamp", "trigger_tf": "timeframe", "direction": "side"})
        overview_causal_signals_df["signal_kind"] = "causal"
    if not overview_hindsight_only_df.empty:
        overview_hindsight_only_df = overview_hindsight_only_df.rename(columns={"event_ts": "timestamp", "trigger_tf": "timeframe", "direction": "side"})
        overview_hindsight_only_df["signal_kind"] = "hindsight_only"

    seg_rows: list[dict[str, Any]] = []

    def _origin_to_ts(origin: Any) -> str:
        try:
            oi = int(origin)
        except Exception:
            return "-"
        hit = full[full["bar_index"] == oi]
        if hit.empty:
            return "-"
        return fmt_ts(hit.iloc[0]["timestamp"])

    def _append_segment(seg: pd.DataFrame, tf: str, *, end_reason: str) -> None:
        if len(seg) < 2:
            return
        first = seg.iloc[0]
        seg_rows.append(
            {
                "timeframe": tf,
                "segment_start": seg.iloc[0]["timestamp"],
                "segment_end": seg.iloc[-1]["timestamp"],
                "duration_bars": len(seg),
                "trend": int(first.get(f"tbn_{tf}_trend", 0) or 0),
                "line_is_provisional": int(first.get(f"tbn_{tf}_line_is_provisional", 0) or 0),
                "anchor_origin": first.get(f"tbn_{tf}_anchor_origin"),
                "anchor_price": first.get(f"tbn_{tf}_anchor_price"),
                "pivot_origin": first.get(f"tbn_{tf}_active_pivot_origin"),
                "pivot_price": first.get(f"tbn_{tf}_active_pivot_price"),
                "anchor_ts": _origin_to_ts(first.get(f"tbn_{tf}_anchor_origin")),
                "pivot_ts": _origin_to_ts(first.get(f"tbn_{tf}_active_pivot_origin")),
                "line_slope": first.get(f"tbn_{tf}_line_slope"),
                "end_reason": end_reason,
            }
        )

    for tf in ["short", "medium", "long"]:
        line_col = f"tbn_{tf}_line_value"
        key_cols = [
            f"tbn_{tf}_anchor_origin",
            f"tbn_{tf}_active_pivot_origin",
            f"tbn_{tf}_line_slope",
            f"tbn_{tf}_trend",
            f"tbn_{tf}_line_is_provisional",
        ]
        start_idx = None
        prev_key = None
        for i, row in overview_window.iterrows():
            line_val = row.get(line_col)
            key = tuple(row.get(k) for k in key_cols)
            if pd.isna(line_val):
                if start_idx is not None:
                    _append_segment(overview_window.iloc[start_idx:i], tf, end_reason="line_missing")
                start_idx = None
                prev_key = None
                continue
            if start_idx is None:
                start_idx = i
                prev_key = key
                continue
            if key != prev_key:
                _append_segment(overview_window.iloc[start_idx:i], tf, end_reason="lifecycle_change")
                start_idx = i
                prev_key = key
        if start_idx is not None:
            _append_segment(overview_window.iloc[start_idx:], tf, end_reason="window_end")
    overview_segments_df = pd.DataFrame(seg_rows)

    return {
        "asset": EXAMPLE_ASSET,
        "symbol": symbol,
        "trade": trade_row,
        "trade_kind": example_kind,
        "gate": gate_info,
        "trigger": selected_trigger_row,
        "window": window,
        "overview_window": overview_window,
        "overview_breakouts_df": overview_breakouts_df,
        "overview_causal_signals_df": overview_causal_signals_df,
        "overview_hindsight_only_df": overview_hindsight_only_df,
        "overview_segments_df": overview_segments_df,
        "formula": selected_formula,
        "formula_causal": causal_formula,
        "formula_hindsight": hindsight_formula,
        "config": EXAMPLE_CONFIG,
    }


def signal_example_svg(example: dict[str, Any], *, width: int = 1180, height: int = 420) -> str:
    window = example.get("window")
    trade = example.get("trade") or {}
    if window is None or getattr(window, "empty", True):
        return '<div class="empty">示意图暂时不可用。</div>'
    work = window.copy().reset_index(drop=True)
    lows = safe_num(work["low"]).fillna(safe_num(work["close"])).fillna(0.0)
    highs = safe_num(work["high"]).fillna(safe_num(work["close"])).fillna(0.0)
    opens = safe_num(work["open"]).fillna(safe_num(work["close"])).fillna(0.0)
    closes = safe_num(work["close"]).fillna(0.0)
    formula = example.get("formula") or {}
    anchor_origin = formula.get("medium_anchor_origin", -1)
    slope = safe_num(pd.Series([formula.get("medium_line_slope")])).iloc[0]
    anchor_price = safe_num(pd.Series([formula.get("medium_anchor_price")])).iloc[0]
    fixed_line = pd.Series([pd.NA] * len(work), index=work.index, dtype="object")
    if pd.notna(anchor_price) and pd.notna(slope) and "bar_index" in work.columns:
        fixed_vals = anchor_price + slope * (safe_num(work["bar_index"]).fillna(0.0) - float(anchor_origin))
        fixed_line = fixed_vals
    active_line = safe_num(work.get("tbn_medium_line_value", pd.Series(dtype=float))).fillna(pd.NA)
    line_min = safe_num(pd.concat([safe_num(active_line).dropna(), safe_num(pd.Series(fixed_line)).dropna()], ignore_index=True)).dropna()
    ymin = float(min(lows.min(), line_min.min() if not line_min.empty else lows.min()))
    ymax = float(max(highs.max(), line_min.max() if not line_min.empty else highs.max()))
    span = max(ymax - ymin, 1e-9)
    ymin -= span * 0.08
    ymax += span * 0.14
    plot_x, plot_y, plot_w, plot_h = 60, 18, width - 84, height - 92
    step = plot_w / max(len(work), 1)

    def y(val: float) -> float:
        return plot_y + plot_h - ((val - ymin) / (ymax - ymin)) * plot_h

    parts = [
        f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" role="img">',
        f'<rect x="{plot_x}" y="{plot_y}" width="{plot_w}" height="{plot_h}" rx="12" fill="none" stroke="#1f2937" />',
    ]

    signal_ts = pd.Timestamp(trade.get("event_ts")) if trade.get("event_ts") is not None else None
    entry_ts = pd.Timestamp(trade.get("entry_ts")) if trade.get("entry_ts") is not None else None
    exit_ts = pd.Timestamp(trade.get("exit_ts")) if trade.get("exit_ts") is not None else None
    anchor_ts = pd.Timestamp(formula.get("medium_anchor_ts")) if formula.get("medium_anchor_ts") not in (None, "-") else None
    pivot_ts = pd.Timestamp(formula.get("medium_pivot_ts")) if formula.get("medium_pivot_ts") not in (None, "-") else None

    fixed_points = [(i, float(v)) for i, v in enumerate(fixed_line) if pd.notna(v)]
    if fixed_points:
        pts = [(plot_x + step * i + step / 2, y(val)) for i, val in fixed_points]
        path = " ".join(("M" if j == 0 else "L") + f" {px:.2f} {py:.2f}" for j, (px, py) in enumerate(pts))
        parts.append(f'<path d="{path}" fill="none" stroke="#f59e0b" stroke-width="2.8" />')

    active_points = [(i, float(v)) for i, v in enumerate(active_line) if pd.notna(v)]
    if active_points:
        pts = [(plot_x + step * i + step / 2, y(val)) for i, val in active_points]
        path = " ".join(("M" if j == 0 else "L") + f" {px:.2f} {py:.2f}" for j, (px, py) in enumerate(pts))
        parts.append(f'<path d="{path}" fill="none" stroke="#94a3b8" stroke-width="1.4" stroke-dasharray="4 4" opacity="0.7" />')

    for i, row in work.iterrows():
        ts = pd.Timestamp(row["timestamp"])
        x = plot_x + step * i + step / 2
        if signal_ts is not None and ts == signal_ts:
            parts.append(f'<rect x="{x - step/2 + 1:.2f}" y="{plot_y}" width="{max(step - 2, 4):.2f}" height="{plot_h}" fill="rgba(59,130,246,0.10)" />')
        if entry_ts is not None and ts == entry_ts:
            parts.append(f'<rect x="{x - step/2 + 1:.2f}" y="{plot_y}" width="{max(step - 2, 4):.2f}" height="{plot_h}" fill="rgba(34,197,94,0.10)" />')
        if exit_ts is not None and ts == exit_ts:
            parts.append(f'<rect x="{x - step/2 + 1:.2f}" y="{plot_y}" width="{max(step - 2, 4):.2f}" height="{plot_h}" fill="rgba(239,68,68,0.08)" />')
        color = "#22c55e" if closes.iloc[i] >= opens.iloc[i] else "#ef4444"
        parts.append(f'<line x1="{x:.2f}" y1="{y(float(highs.iloc[i])):.2f}" x2="{x:.2f}" y2="{y(float(lows.iloc[i])):.2f}" stroke="{color}" stroke-width="1.5" />')
        body_top = y(max(float(opens.iloc[i]), float(closes.iloc[i])))
        body_bottom = y(min(float(opens.iloc[i]), float(closes.iloc[i])))
        body_h = max(body_bottom - body_top, 2.0)
        parts.append(f'<rect x="{x - step*0.22:.2f}" y="{body_top:.2f}" width="{max(step*0.44, 4):.2f}" height="{body_h:.2f}" rx="2" fill="{color}" />')
        if i % 3 == 0:
            parts.append(f'<text x="{x - 16:.2f}" y="{height - 42}" fill="#64748b" font-size="10">{escape(ts.strftime("%m-%d %H:%M"))}</text>')

    for label, ts, color in [("signal", signal_ts, "#60a5fa"), ("entry", entry_ts, "#22c55e"), ("exit", exit_ts, "#ef4444"), ("anchor", anchor_ts, "#f59e0b"), ("pivot", pivot_ts, "#fbbf24")]:
        if ts is None:
            continue
        idxs = work.index[work["timestamp"] == ts].tolist()
        if not idxs:
            continue
        x = plot_x + step * idxs[0] + step / 2
        parts.append(f'<line x1="{x:.2f}" y1="{plot_y}" x2="{x:.2f}" y2="{plot_y + plot_h}" stroke="{color}" stroke-dasharray="4 4" />')
        parts.append(f'<text x="{x + 4:.2f}" y="{plot_y + 14}" fill="{color}" font-size="11">{escape(label)}</text>')

    legend = [
        ("#f59e0b", "signal-time confirmed line"),
        ("#94a3b8", "active line path (for reference)"),
        ("#60a5fa", "signal bar"),
        ("#22c55e", "entry bar"),
        ("#ef4444", "exit bar"),
    ]
    lx = plot_x
    for color, label in legend:
        parts.append(f'<rect x="{lx}" y="{height - 24}" width="12" height="12" rx="3" fill="{color}" />')
        parts.append(f'<text x="{lx + 18}" y="{height - 14}" fill="#cbd5e1" font-size="12">{escape(label)}</text>')
        lx += 180

    parts.append(f'<text x="8" y="{plot_y + 10}" fill="#94a3b8" font-size="11">{num(ymax, 2)}</text>')
    parts.append(f'<text x="8" y="{plot_y + plot_h}" fill="#94a3b8" font-size="11">{num(ymin, 2)}</text>')
    parts.append("</svg>")
    return "".join(parts)


def mtf_overview_svg(example: dict[str, Any], *, width: int = 1180, height: int = 520) -> str:
    window = example.get("overview_window")
    trade = example.get("trade") or {}
    if window is None or getattr(window, "empty", True):
        return '<div class="empty">多时间框架总览图暂时不可用。</div>'
    work = window.copy().reset_index(drop=True)
    work["timestamp"] = pd.to_datetime(work["timestamp"], utc=True, errors="coerce")
    lows = safe_num(work["low"]).fillna(safe_num(work["close"])).fillna(0.0)
    highs = safe_num(work["high"]).fillna(safe_num(work["close"])).fillna(0.0)
    opens = safe_num(work["open"]).fillna(safe_num(work["close"])).fillna(0.0)
    closes = safe_num(work["close"]).fillna(0.0)
    line_cols = {
        "short": ("tbn_short_line_value", "#38bdf8"),
        "medium": ("tbn_medium_line_value", "#f59e0b"),
        "long": ("tbn_long_line_value", "#a855f7"),
    }
    trend_cols = {
        "short": "tbn_short_trend",
        "medium": "tbn_medium_trend",
        "long": "tbn_long_trend",
        "composite": "tbn_composite_trend",
    }
    line_vals = []
    for col, _ in line_cols.values():
        if col in work.columns:
            line_vals.append(safe_num(work[col]).dropna())
    merged_line = pd.concat(line_vals, ignore_index=True) if line_vals else pd.Series(dtype=float)
    ymin = float(min(lows.min(), merged_line.min() if not merged_line.empty else lows.min()))
    ymax = float(max(highs.max(), merged_line.max() if not merged_line.empty else highs.max()))
    span = max(ymax - ymin, 1e-9)
    ymin -= span * 0.08
    ymax += span * 0.14
    plot_x, price_y, plot_w, price_h = 60, 18, width - 84, 300
    state_y = price_y + price_h + 28
    row_h = 22
    step = plot_w / max(len(work), 1)

    def x_for_idx(idx: int) -> float:
        return plot_x + step * idx + step / 2

    def y(val: float) -> float:
        return price_y + price_h - ((val - ymin) / (ymax - ymin)) * price_h

    parts = [
        f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" role="img">',
        f'<rect x="{plot_x}" y="{price_y}" width="{plot_w}" height="{price_h}" rx="12" fill="none" stroke="#1f2937" />',
    ]

    signal_ts = pd.Timestamp(trade.get("event_ts")) if trade.get("event_ts") is not None else None
    entry_ts = pd.Timestamp(trade.get("entry_ts")) if trade.get("entry_ts") is not None else None
    exit_ts = pd.Timestamp(trade.get("exit_ts")) if trade.get("exit_ts") is not None else None

    for i, row in work.iterrows():
        ts = pd.Timestamp(row["timestamp"])
        x = x_for_idx(i)
        if signal_ts is not None and ts == signal_ts:
            parts.append(f'<rect x="{x - step/2 + 1:.2f}" y="{price_y}" width="{max(step - 2, 4):.2f}" height="{price_h}" fill="rgba(59,130,246,0.10)" />')
        if entry_ts is not None and ts == entry_ts:
            parts.append(f'<rect x="{x - step/2 + 1:.2f}" y="{price_y}" width="{max(step - 2, 4):.2f}" height="{price_h}" fill="rgba(34,197,94,0.08)" />')
        if exit_ts is not None and ts == exit_ts:
            parts.append(f'<rect x="{x - step/2 + 1:.2f}" y="{price_y}" width="{max(step - 2, 4):.2f}" height="{price_h}" fill="rgba(239,68,68,0.06)" />')
        color = "#22c55e" if closes.iloc[i] >= opens.iloc[i] else "#ef4444"
        parts.append(f'<line x1="{x:.2f}" y1="{y(float(highs.iloc[i])):.2f}" x2="{x:.2f}" y2="{y(float(lows.iloc[i])):.2f}" stroke="{color}" stroke-width="1.3" />')
        body_top = y(max(float(opens.iloc[i]), float(closes.iloc[i])))
        body_bottom = y(min(float(opens.iloc[i]), float(closes.iloc[i])))
        body_h = max(body_bottom - body_top, 2.0)
        parts.append(f'<rect x="{x - step*0.2:.2f}" y="{body_top:.2f}" width="{max(step*0.4, 3):.2f}" height="{body_h:.2f}" rx="2" fill="{color}" />')
        if i % 6 == 0:
            parts.append(f'<text x="{x - 18:.2f}" y="{height - 16}" fill="#64748b" font-size="10">{escape(ts.strftime("%m-%d %H:%M"))}</text>')

    ts_to_idx = {pd.Timestamp(ts): i for i, ts in enumerate(work["timestamp"])}
    bar_index_to_idx: dict[int, int] = {}
    if "bar_index" in work.columns:
        bar_idx_series = safe_num(work["bar_index"]).dropna().astype(int)
        for i, bar_idx in zip(bar_idx_series.index.tolist(), bar_idx_series.tolist(), strict=False):
            bar_index_to_idx[int(bar_idx)] = int(i)

    breakout_df = example.get("overview_breakouts_df")
    causal_signal_df = example.get("overview_causal_signals_df")
    hindsight_signal_df = example.get("overview_hindsight_only_df")
    causal_signal_ts_set: set[pd.Timestamp] = set()
    hindsight_signal_ts_set: set[pd.Timestamp] = set()
    if isinstance(causal_signal_df, pd.DataFrame) and not causal_signal_df.empty:
        for _, r in causal_signal_df.iterrows():
            ts = pd.to_datetime(r.get("timestamp"), utc=True, errors="coerce")
            if pd.notna(ts):
                causal_signal_ts_set.add(pd.Timestamp(ts))
    if isinstance(hindsight_signal_df, pd.DataFrame) and not hindsight_signal_df.empty:
        for _, r in hindsight_signal_df.iterrows():
            ts = pd.to_datetime(r.get("timestamp"), utc=True, errors="coerce")
            if pd.notna(ts):
                hindsight_signal_ts_set.add(pd.Timestamp(ts))

    tf_color = {"short": "#38bdf8", "medium": "#f59e0b", "long": "#a855f7"}
    breakout_points_by_tf: dict[str, list[dict[str, Any]]] = {"short": [], "medium": [], "long": []}
    if isinstance(breakout_df, pd.DataFrame) and not breakout_df.empty:
        for _, r in breakout_df.iterrows():
            ts = pd.to_datetime(r.get("timestamp"), utc=True, errors="coerce")
            if pd.isna(ts) or pd.Timestamp(ts) not in ts_to_idx:
                continue
            tf = str(r.get("timeframe"))
            if tf not in breakout_points_by_tf:
                continue
            idx = ts_to_idx[pd.Timestamp(ts)]
            close_val = safe_num(pd.Series([r.get("close")])).iloc[0]
            line_val = safe_num(pd.Series([r.get("line_value")])).iloc[0]
            breakout_points_by_tf[tf].append(
                {
                    "idx": idx,
                    "ts": pd.Timestamp(ts),
                    "close": close_val,
                    "line_value": line_val,
                    "is_true": pd.Timestamp(ts) in causal_signal_ts_set,
                }
            )

    def _path_from_indexed_points(indexed_points: list[tuple[int, float, float]]) -> str:
        return " ".join(
            ("M" if p == 0 else "L") + f" {px:.2f} {py:.2f}"
            for p, (_, px, py) in enumerate(indexed_points)
        )

    for label, (col, color) in line_cols.items():
        if col not in work.columns:
            continue
        key_cols = [
            f"tbn_{label}_anchor_origin",
            f"tbn_{label}_active_pivot_origin",
            f"tbn_{label}_line_slope",
            f"tbn_{label}_trend",
            f"tbn_{label}_line_is_provisional",
        ]
        segment_start = None
        prev_key = None

        def draw_segment(start_i: int, end_i: int) -> None:
            seg = work.iloc[start_i:end_i].copy()
            if len(seg) < 2:
                return
            indexed_points = [
                (int(j), x_for_idx(int(j)), y(float(v)))
                for j, v in zip(seg.index.tolist(), seg[col].tolist(), strict=False)
                if pd.notna(v)
            ]
            if len(indexed_points) < 2:
                return
            first = seg.iloc[0]
            provisional = int(first.get(f"tbn_{label}_line_is_provisional", 0) or 0)
            matched_breakouts = [bp for bp in breakout_points_by_tf.get(label, []) if start_i <= int(bp["idx"]) <= end_i - 1]
            matched_breakouts.sort(key=lambda bp: int(bp["idx"]))
            if matched_breakouts:
                break_idx = int(matched_breakouts[0]["idx"])
                pre_points = [pt for pt in indexed_points if pt[0] < break_idx]
                ext_points = [pt for pt in indexed_points if pt[0] >= max(start_i, break_idx - 1)]
                if len(pre_points) >= 2:
                    parts.append(f'<path d="{_path_from_indexed_points(pre_points)}" fill="none" stroke="{color}" stroke-width="2.1" />')
                if len(ext_points) >= 2:
                    parts.append(f'<path d="{_path_from_indexed_points(ext_points)}" fill="none" stroke="{color}" stroke-width="2.1" stroke-dasharray="6 5" opacity="0.95" />')
                elif len(indexed_points) >= 2:
                    parts.append(f'<path d="{_path_from_indexed_points(indexed_points)}" fill="none" stroke="{color}" stroke-width="2.1" stroke-dasharray="6 5" opacity="0.95" />')
            else:
                dash = ' stroke-dasharray="5 4" opacity="0.72"' if provisional else ""
                parts.append(f'<path d="{_path_from_indexed_points(indexed_points)}" fill="none" stroke="{color}" stroke-width="2.1"{dash} />')

            anchor_origin = first.get(f"tbn_{label}_anchor_origin")
            anchor_price = safe_num(pd.Series([first.get(f"tbn_{label}_anchor_price")])).iloc[0]
            pivot_origin = first.get(f"tbn_{label}_active_pivot_origin")
            pivot_price = safe_num(pd.Series([first.get(f"tbn_{label}_active_pivot_price")])).iloc[0]

            anchor_idx = None
            pivot_idx = None
            try:
                anchor_idx = bar_index_to_idx.get(int(anchor_origin))
            except Exception:
                anchor_idx = None
            try:
                pivot_idx = bar_index_to_idx.get(int(pivot_origin))
            except Exception:
                pivot_idx = None

            if anchor_idx is not None and pd.notna(anchor_price):
                ax = x_for_idx(anchor_idx)
                ay = y(float(anchor_price))
                parts.append(f'<circle cx="{ax:.2f}" cy="{ay:.2f}" r="4.8" fill="#020617" stroke="{color}" stroke-width="2.0" />')
                parts.append(f'<text x="{ax + 6:.2f}" y="{ay - 6:.2f}" fill="{color}" font-size="10">A</text>')
            if pivot_idx is not None and pd.notna(pivot_price):
                px = x_for_idx(pivot_idx)
                py = y(float(pivot_price))
                parts.append(f'<circle cx="{px:.2f}" cy="{py:.2f}" r="4.0" fill="{color}" stroke="#e5e7eb" stroke-width="1.4" />')
                parts.append(f'<text x="{px + 6:.2f}" y="{py - 6:.2f}" fill="{color}" font-size="10">P</text>')
            elif provisional and anchor_idx is not None and pd.notna(anchor_price):
                ax = x_for_idx(anchor_idx)
                ay = y(float(anchor_price))
                parts.append(f'<text x="{ax + 14:.2f}" y="{ay + 14:.2f}" fill="#94a3b8" font-size="10">prov</text>')

            mid_idx = indexed_points[len(indexed_points) // 2][0]
            slope = safe_num(pd.Series([first.get(f"tbn_{label}_line_slope")])).iloc[0]
            mid_val = safe_num(pd.Series([work.iloc[mid_idx].get(col)])).iloc[0]
            if pd.notna(mid_val):
                tag = f"{label[0].upper()}({num(slope, 4)})" if pd.notna(slope) else label[0].upper()
                if provisional:
                    tag += " prov"
                parts.append(f'<text x="{x_for_idx(mid_idx) - 20:.2f}" y="{y(float(mid_val)) - 8:.2f}" fill="#cbd5e1" font-size="10">{escape(tag)}</text>')

        for i, row in work.iterrows():
            val = row.get(col)
            key = tuple(row.get(k) for k in key_cols)
            if pd.isna(val):
                if segment_start is not None:
                    draw_segment(segment_start, i)
                segment_start = None
                prev_key = None
                continue
            if segment_start is None:
                segment_start = i
                prev_key = key
                continue
            if key != prev_key:
                draw_segment(segment_start, i)
                segment_start = i
                prev_key = key
        if segment_start is not None:
            draw_segment(segment_start, len(work))

    if isinstance(breakout_df, pd.DataFrame) and not breakout_df.empty:
        for _, r in breakout_df.iterrows():
            ts = pd.to_datetime(r.get("timestamp"), utc=True, errors="coerce")
            if pd.isna(ts) or pd.Timestamp(ts) not in ts_to_idx:
                continue
            i = ts_to_idx[pd.Timestamp(ts)]
            x = x_for_idx(i)
            tf = str(r.get("timeframe"))
            c = tf_color.get(tf, "#f8fafc")
            line_val = safe_num(pd.Series([r.get("line_value")])).iloc[0]
            close_val = safe_num(pd.Series([r.get("close")])).iloc[0]
            event_y = y(float(line_val)) if pd.notna(line_val) else (y(float(close_val)) if pd.notna(close_val) else price_y + price_h / 2)
            close_y = y(float(close_val)) if pd.notna(close_val) else event_y
            is_true = pd.Timestamp(ts) in causal_signal_ts_set
            if abs(close_y - event_y) > 1.0:
                parts.append(f'<line x1="{x:.2f}" y1="{event_y:.2f}" x2="{x:.2f}" y2="{close_y:.2f}" stroke="{c}" stroke-width="1.5" stroke-dasharray="3 3" opacity="0.9" />')
                parts.append(f'<rect x="{x - 3.0:.2f}" y="{close_y - 3.0:.2f}" width="6.0" height="6.0" rx="1.6" fill="#020617" stroke="{c}" stroke-width="1.3" />')
            fill = c if is_true else "#0b1220"
            stroke_w = 2.4 if is_true else 2.0
            parts.append(f'<circle cx="{x:.2f}" cy="{event_y:.2f}" r="4.5" fill="{fill}" stroke="{c}" stroke-width="{stroke_w}" />')

    if isinstance(causal_signal_df, pd.DataFrame) and not causal_signal_df.empty:
        for _, r in causal_signal_df.iterrows():
            ts = pd.to_datetime(r.get("timestamp"), utc=True, errors="coerce")
            if pd.isna(ts) or pd.Timestamp(ts) not in ts_to_idx:
                continue
            i = ts_to_idx[pd.Timestamp(ts)]
            x = x_for_idx(i)
            close_hit = work.iloc[i].get("close")
            yy = y(float(close_hit)) - 10 if pd.notna(close_hit) else (price_y + 12)
            parts.append(f'<text x="{x - 4:.2f}" y="{yy:.2f}" fill="#facc15" font-size="14">★</text>')
    if isinstance(hindsight_signal_df, pd.DataFrame) and not hindsight_signal_df.empty:
        for _, r in hindsight_signal_df.iterrows():
            ts = pd.to_datetime(r.get("timestamp"), utc=True, errors="coerce")
            if pd.isna(ts) or pd.Timestamp(ts) not in ts_to_idx:
                continue
            i = ts_to_idx[pd.Timestamp(ts)]
            x = x_for_idx(i)
            close_hit = work.iloc[i].get("close")
            yy = y(float(close_hit)) - 10 if pd.notna(close_hit) else (price_y + 12)
            parts.append(f'<text x="{x - 4:.2f}" y="{yy:.2f}" fill="#fb7185" font-size="14">☆</text>')

    row_labels = [("short", "短周期趋势"), ("medium", "中周期趋势"), ("long", "长周期趋势"), ("composite", "合成分数")]
    for ridx, (key, title) in enumerate(row_labels):
        y0 = state_y + ridx * (row_h + 8)
        parts.append(f'<text x="{plot_x}" y="{y0 + 14}" fill="#cbd5e1" font-size="12">{escape(title)}</text>')
        for i, row in work.iterrows():
            x = plot_x + 96 + step * i
            w = max(step - 1, 3)
            val = row.get(trend_cols[key], 0)
            try:
                val = int(val)
            except Exception:
                val = 0
            if key == "composite":
                color = "#1d4ed8" if val >= 2 else ("#2563eb" if val == 1 else ("#475569" if val == 0 else ("#b91c1c" if val <= -2 else "#dc2626")))
            else:
                color = "#16a34a" if val > 0 else ("#475569" if val == 0 else "#dc2626")
            parts.append(f'<rect x="{x:.2f}" y="{y0:.2f}" width="{w:.2f}" height="{row_h:.2f}" rx="3" fill="{color}" opacity="0.95" />')
        parts.append(f'<text x="{plot_x + plot_w + 8}" y="{y0 + 14}" fill="#94a3b8" font-size="11">{escape(str(int(work[trend_cols[key]].iloc[-1])) if trend_cols[key] in work.columns and len(work) else '-') }</text>')

    legend_y1 = price_y + price_h + 4
    legend_y2 = price_y + price_h + 28
    lx = plot_x
    for color, label in [("#38bdf8", "short"), ("#f59e0b", "medium"), ("#a855f7", "long")]:
        parts.append(f'<rect x="{lx}" y="{legend_y1}" width="12" height="12" rx="3" fill="{color}" />')
        parts.append(f'<text x="{lx + 18}" y="{legend_y1 + 10}" fill="#cbd5e1" font-size="12">{escape(label)} line</text>')
        lx += 128
    parts.append(f'<line x1="{lx}" y1="{legend_y1 + 6}" x2="{lx + 18}" y2="{legend_y1 + 6}" stroke="#94a3b8" stroke-dasharray="5 4" opacity="0.72" />')
    parts.append(f'<text x="{lx + 24}" y="{legend_y1 + 10}" fill="#cbd5e1" font-size="12">provisional</text>')
    lx += 128
    parts.append(f'<circle cx="{lx + 6}" cy="{legend_y1 + 6}" r="4.8" fill="#020617" stroke="#e5e7eb" stroke-width="1.5" />')
    parts.append(f'<text x="{lx + 18}" y="{legend_y1 + 10}" fill="#cbd5e1" font-size="12">A = anchor</text>')
    lx += 128
    parts.append(f'<circle cx="{lx + 6}" cy="{legend_y1 + 6}" r="4.0" fill="#e5e7eb" stroke="#020617" stroke-width="1.0" />')
    parts.append(f'<text x="{lx + 18}" y="{legend_y1 + 10}" fill="#cbd5e1" font-size="12">P = pivot</text>')

    parts.append(f'<circle cx="{plot_x}" cy="{legend_y2}" r="4.5" fill="#0b1220" stroke="#f8fafc" stroke-width="2.0" />')
    parts.append(f'<text x="{plot_x + 12}" y="{legend_y2 + 4}" fill="#cbd5e1" font-size="12">breakout 在线上（line_value）</text>')
    parts.append(f'<rect x="{plot_x + 220}" y="{legend_y2 - 3}" width="6" height="6" rx="1.6" fill="#020617" stroke="#f8fafc" stroke-width="1.3" />')
    parts.append(f'<text x="{plot_x + 232}" y="{legend_y2 + 4}" fill="#cbd5e1" font-size="12">close 位置</text>')
    parts.append(f'<text x="{plot_x + 340}" y="{legend_y2 + 4}" fill="#facc15" font-size="14">★</text>')
    parts.append(f'<text x="{plot_x + 356}" y="{legend_y2 + 4}" fill="#cbd5e1" font-size="12">causal 真信号（当前基准）</text>')
    parts.append(f'<text x="{plot_x + 576}" y="{legend_y2 + 4}" fill="#fb7185" font-size="14">☆</text>')
    parts.append(f'<text x="{plot_x + 592}" y="{legend_y2 + 4}" fill="#cbd5e1" font-size="12">hindsight-only（事后长出来）</text>')

    parts.append(f'<text x="8" y="{price_y + 10}" fill="#94a3b8" font-size="11">{num(ymax, 2)}</text>')
    parts.append(f'<text x="8" y="{price_y + price_h}" fill="#94a3b8" font-size="11">{num(ymin, 2)}</text>')
    parts.append("</svg>")
    return "".join(parts)


def metric_card(title: str, value: str, sub: str) -> str:
    return f"<div class='metric'><div class='k'>{escape(title)}</div><div class='v'>{escape(value)}</div><div class='s'>{sub}</div></div>"


def table_html(df: pd.DataFrame) -> str:
    if df.empty:
        return '<p class="empty">暂无数据。</p>'
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows: list[str] = []
    for _, row in df.iterrows():
        cls = ""
        if "pnl_usdt" in df.columns:
            try:
                val = float(row.get("pnl_usdt"))
                cls = "pos" if val > 0 else ("neg" if val < 0 else "flat")
            except Exception:
                cls = ""
        tds: list[str] = []
        for col in df.columns:
            val = row[col]
            if col.endswith("time") or col in {"ts", "entry_ts", "exit_ts", "updated_at"}:
                text = fmt_ts(val)
            elif col == "pnl_usdt":
                text = money(val)
            elif col == "win_rate":
                text = pct(val)
            else:
                text = str(val)
            tds.append(f"<td>{escape(text)}</td>")
        rows.append(f"<tr class='{cls}'>{''.join(tds)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def main() -> int:
    ensure_dir(SITE_DIR)

    baseline_shadow_df, gate_shadow_df = prep_rank29_shadow_view()
    live_df, open_df, live_state, live_status = prep_live_trades()
    compare_df = read_csv(LIVE_COMPARE_PATH)
    rejections = read_json(LIVE_REJECTIONS_PATH, []) or []
    warnings = read_json(LIVE_WARNINGS_PATH, []) or []
    orders = read_json(LIVE_ORDERS_PATH, []) or []
    actual_ledger = read_csv(ACTUAL_LEDGER_PATH)
    status_csv = read_csv(STATUS_CSV_PATH)
    run_summary = read_json(RUN_SUMMARY_PATH, {}) or {}
    orderbook_status = read_csv(ORDERBOOK_STATUS_PATH)

    live_summary = summarize(live_df)
    gate_summary = summarize(gate_shadow_df)
    baseline_summary = summarize(baseline_shadow_df)
    signal_example = build_signal_example()
    honesty_audit = build_recent_signal_honesty_audit()

    compare_live = safe_num(compare_df.get("live_net_pnl_usdt", pd.Series(dtype=float))).fillna(0.0).sum() if not compare_df.empty else 0.0
    compare_shadow = safe_num(compare_df.get("shadow_proxy_net_pnl_usdt", pd.Series(dtype=float))).fillna(0.0).sum() if not compare_df.empty else 0.0
    compare_delta = safe_num(compare_df.get("delta_vs_shadow_usdt", pd.Series(dtype=float))).fillna(0.0).sum() if not compare_df.empty else 0.0

    reject_df = pd.DataFrame(rejections)
    reason_counts = (
        reject_df.get("reason", pd.Series(dtype=str)).fillna("-").value_counts().rename_axis("reason").reset_index(name="count")
        if not reject_df.empty else pd.DataFrame(columns=["reason", "count"])
    )
    higher_priority_skips = 0
    expired_skips = 0
    if not reject_df.empty and "reason" in reject_df.columns:
        higher_priority_skips = int(reject_df[reject_df["reason"].astype(str).str.contains("conflict|priority|core3", case=False, na=False)].shape[0])
        expired_skips = int(reject_df[reject_df["reason"] == "signal_expired"].shape[0])

    if not live_df.empty:
        recent_live = live_df.sort_values("ts", ascending=False).head(16).copy()
        recent_live["result"] = recent_live["pnl_usdt"].map(lambda x: "win" if x > 0 else ("loss" if x < 0 else "flat"))
        recent_live = recent_live[[c for c in ["ts", "symbol", "side", "pnl_usdt", "result", "exit_reason"] if c in recent_live.columns]]
    else:
        recent_live = pd.DataFrame()

    if not compare_df.empty:
        compare_view = compare_df.copy()
        for col in ["live_entry_time", "live_exit_time", "entry_ts", "exit_ts"]:
            if col in compare_view.columns:
                compare_view[col] = compare_view[col].map(fmt_ts)
        compare_view = compare_view[[c for c in ["symbol", "side", "live_exit_time", "live_net_pnl_usdt", "shadow_proxy_net_pnl_usdt", "delta_vs_shadow_usdt", "gate_low_trend_high_noise", "exposure_weight"] if c in compare_view.columns]].sort_values("live_exit_time", ascending=False).head(20)
    else:
        compare_view = pd.DataFrame()

    if not open_df.empty:
        open_view = open_df[[c for c in ["symbol", "side", "entry_time", "entry_price", "planned_exit_time", "desired_notional_usdt"] if c in open_df.columns]].copy()
    else:
        open_view = pd.DataFrame()

    warnings_view = pd.DataFrame(warnings)
    if not warnings_view.empty:
        warnings_view = warnings_view[[c for c in ["timestamp", "message"] if c in warnings_view.columns]].tail(10).iloc[::-1]

    orders_view = pd.DataFrame(orders)
    if not orders_view.empty:
        orders_view = orders_view[[c for c in ["timestamp", "order_role", "symbol", "side", "price", "qty", "status"] if c in orders_view.columns]].tail(10).iloc[::-1]

    actual_gate_val = "-"
    actual_gate_sub = "actual append-only gate ledger 暂无数据"
    if not actual_ledger.empty and "candidate_id" in actual_ledger.columns:
        gate_actual = actual_ledger[actual_ledger["candidate_id"] == GATE_ID].copy()
        if not gate_actual.empty:
            gate_actual["net_ret"] = safe_num(gate_actual.get("net_ret", 0.0)).fillna(0.0)
            gate_actual["exit_ts"] = pd.to_datetime(gate_actual.get("exit_ts"), utc=True, errors="coerce")
            actual_gate_val = pct((1.0 + gate_actual["net_ret"]).prod() - 1.0)
            actual_gate_sub = f"closed={len(gate_actual)} · last exit={fmt_ts(gate_actual['exit_ts'].max())}"

    runner_last = "-"
    if not status_csv.empty and "sample_end_utc" in status_csv.columns:
        sub = status_csv[status_csv.get("candidate_id", "").isin([BASELINE_ID, GATE_ID])].copy()
        if not sub.empty:
            runner_last = fmt_ts(sub["sample_end_utc"].max())

    orderbook_text = "orderbook shadow 暂无数据"
    if not orderbook_status.empty:
        row = orderbook_status.iloc[0]
        orderbook_text = f"signals={int(row.get('recent_signal_count', 0) or 0)} · rejects={int(row.get('recent_rejection_count', 0) or 0)} · updated={fmt_ts(row.get('updated_at_utc'))}"

    top_cards = "".join(
        [
            metric_card("rank29 live cumulative pnl", money(live_summary["cum_pnl"]), f"closed={live_summary['trades']} · wins={live_summary['wins']} · win rate={pct(live_summary['win_rate'])}"),
            metric_card("gate shadow reference", money(gate_summary["cum_pnl"]), f"closed={gate_summary['trades']} · win rate={pct(gate_summary['win_rate'])}"),
            metric_card("baseline shadow reference", money(baseline_summary["cum_pnl"]), f"closed={baseline_summary['trades']} · win rate={pct(baseline_summary['win_rate'])}"),
            metric_card("future-leak misleading ratio", pct(honesty_audit.get("misleading_pct")), f"recent {honesty_audit.get('days', SIGNAL_AUDIT_DAYS)}d: hindsight_only={honesty_audit.get('hindsight_only_signals', 0)} / old_signals={honesty_audit.get('confirmed_signals', 0)}"),
            metric_card("live vs gate shadow delta", money(compare_delta), f"live={money(compare_live)} · shadow={money(compare_shadow)}"),
            metric_card("priority conflict skips", str(higher_priority_skips), f"expired={expired_skips} · warnings={len(warnings)}"),
            metric_card("runner freshness", runner_last, f"weekly stop={bool(live_status.get('weekly_stop_active'))} · live open={len(open_view)}"),
        ]
    )

    archive_cards = "".join([
        metric_card("archive / research", "rank29 shadow dashboard", "真实 paper / replay / research 视角，已降级为 archive 页"),
        metric_card("debug / live detail", "rank29 gate live", "看 recent orders / rejections / raw compare 的细页"),
        metric_card("runner / watermark", "manual narrow paper lanes", "看 sample_end、水位、append-only 台账是否新鲜"),
        metric_card("execution shadow", "orderbook shadow", orderbook_text),
    ])

    signal_example_trade = signal_example.get("trade", {})
    signal_example_trigger = signal_example.get("trigger", {})
    signal_example_gate = signal_example.get("gate", {})
    signal_example_formula = signal_example.get("formula", {})
    signal_example_formula_causal = signal_example.get("formula_causal", {})
    signal_example_formula_hindsight = signal_example.get("formula_hindsight", {})
    signal_example_kind = str(signal_example.get("trade_kind", ""))
    signal_example_cfg = signal_example.get("config", EXAMPLE_CONFIG)
    honesty_asset_df = honesty_audit.get("per_asset_df", pd.DataFrame())
    honesty_detail_df = honesty_audit.get("detail_df", pd.DataFrame())
    signal_kind_text = {
        "causal": "causal 真信号",
        "hindsight_only": "hindsight-only（事后长出来）",
        "confirmed_only": "confirmed-only 旧口径示例",
    }.get(signal_example_kind, "示例")
    signal_example_cards = "".join([
        metric_card("案例类型", signal_kind_text, f"asset={signal_example.get('asset', EXAMPLE_ASSET)} · event={fmt_ts(signal_example_trade.get('event_ts'))}"),
        metric_card("趋势分数", f"causal {signal_example_formula_causal.get('composite_trend', '-')} vs hindsight {signal_example_formula_hindsight.get('composite_trend', '-')}", "同一根 bar 只要两边不一样，就说明事后重算改写了当时可见状态"),
        metric_card("进出场", f"entry {num(signal_example_trade.get('entry_price'))} → exit {num(signal_example_trade.get('exit_price'))}", f"entry={fmt_ts(signal_example_trade.get('entry_ts'))} · exit={fmt_ts(signal_example_trade.get('exit_ts'))}"),
        metric_card("gate 当日", f"low_trend_high_noise={num(signal_example_gate.get('gate_low_trend_high_noise'), 0)}", f"坏环境只缩仓：weight=25%，不是直接禁做"),
    ])
    trend_formula_html = f"""
      <div class='viz-card' style='margin-top:14px;'>
        <h3>趋势分数怎么计算</h3>
        <p class='muted'>当前页面展示的 <code>trend_score</code> 实际就是 <code>tbn_composite_trend</code>。它不是一个连续回归分数，而是三个时间框架趋势状态的整数求和：</p>
        <pre><code>tbn_composite_trend = tbn_long_trend + tbn_medium_trend + tbn_short_trend</code></pre>
        <p class='muted'>其中每个 timeframe 的 trend 只取三种值：<code>+1</code>（多头）、<code>0</code>（中性 / 尚未定向）、<code>-1</code>（空头）。本例我同时把 <b>causal</b> 和 <b>hindsight</b> 两个视角摆出来：</p>
        <pre><code>causal:
  long_trend   = {signal_example_formula_causal.get('long_trend', 0)}
  medium_trend = {signal_example_formula_causal.get('medium_trend', 0)}
  short_trend  = {signal_example_formula_causal.get('short_trend', 0)}
  => trend_score = {signal_example_formula_causal.get('composite_trend', 0)}

hindsight:
  long_trend   = {signal_example_formula_hindsight.get('long_trend', 0)}
  medium_trend = {signal_example_formula_hindsight.get('medium_trend', 0)}
  short_trend  = {signal_example_formula_hindsight.get('short_trend', 0)}
  => trend_score = {signal_example_formula_hindsight.get('composite_trend', 0)}</code></pre>
        <p class='muted'>做多准入要求：<code>trend_score ≥ 2</code>；做空准入要求：<code>trend_score ≤ -2</code>。</p>
      </div>
    """
    line_formula_html = f"""
      <div class='viz-card' style='margin-top:14px;'>
        <h3>趋势线怎么画（定量公式）</h3>
        <p class='muted'>以本例的 <b>medium</b> 线为例，配置参数是：<code>swing_medium={signal_example_cfg.swing_medium}</code>、<code>swing_right={signal_example_cfg.swing_right}</code>、<code>min_pivot_gap={signal_example_cfg.min_pivot_gap}</code>。</p>
        <p class='muted'>确认 pivot 的规则：</p>
        <pre><code>pivot high at center c:
  high[c] &gt; max(high[c-L : c-1])
  and high[c] &gt; max(high[c+1 : c+R])
  confirmed on bar c+R

pivot low at center c:
  low[c] &lt; min(low[c-L : c-1])
  and low[c] &lt; min(low[c+1 : c+R])
  confirmed on bar c+R</code></pre>
        <p class='muted'>一旦趋势建立后，线本体用两点式表示：</p>
        <pre><code>line_value(i) = anchor_price + line_slope × (i - anchor_origin)
line_slope    = (pivot_price - anchor_price) / (pivot_origin - anchor_origin)</code></pre>
        <p class='muted'>本例 medium 线的可见参数是：</p>
        <pre><code>bullish breakout condition: close[bar] &gt; line_value[bar]
bearish breakout condition: close[bar] &lt; line_value[bar]</code></pre>
        <pre><code>causal view:
  anchor_origin = {signal_example_formula_causal.get('medium_anchor_origin', '-')}
  anchor_time   = {signal_example_formula_causal.get('medium_anchor_ts', '-')}
  pivot_origin  = {signal_example_formula_causal.get('medium_pivot_origin', '-')}
  pivot_time    = {signal_example_formula_causal.get('medium_pivot_ts', '-')}
  line_slope    = {num(signal_example_formula_causal.get('medium_line_slope'), 6)}
  line_value    = {num(signal_example_formula_causal.get('medium_line_value'))}

hindsight view:
  anchor_origin = {signal_example_formula_hindsight.get('medium_anchor_origin', '-')}
  anchor_time   = {signal_example_formula_hindsight.get('medium_anchor_ts', '-')}
  pivot_origin  = {signal_example_formula_hindsight.get('medium_pivot_origin', '-')}
  pivot_time    = {signal_example_formula_hindsight.get('medium_pivot_ts', '-')}
  line_slope    = {num(signal_example_formula_hindsight.get('medium_line_slope'), 6)}
  line_value    = {num(signal_example_formula_hindsight.get('medium_line_value'))}

signal_bar_close = {num(signal_example_formula_hindsight.get('signal_close'))}
close_minus_line = {num(signal_example_formula_hindsight.get('close_minus_line'))}</code></pre>
        <p class='muted'>只有当 breakout 落在 <code>line_is_provisional = 0</code> 的 confirmed line 上时，这条信号才允许进入 rank29 live / shadow。若图里某段线只有 <code>A</code> 没有 <code>P</code>，那不是漏画，而是它还停留在 <b>provisional line</b>：第 2 个定义点尚未确认，所以只能暂时把它当成“候选结构”，不能当完整两点趋势线来读。若 <b>causal</b> 与 <b>hindsight</b> 的 pivot / slope / trend_score 不同，就说明这根 bar 被未来确认信息改写过。</p>
      </div>
    """
    signal_example_window = signal_example.get("window")
    signal_example_rows = signal_example_window.copy() if isinstance(signal_example_window, pd.DataFrame) else pd.DataFrame()
    if not signal_example_rows.empty:
        signal_example_rows = signal_example_rows[[c for c in ["timestamp", "open", "high", "low", "close", "tbn_short_trend", "tbn_medium_trend", "tbn_long_trend", "tbn_composite_trend", "tbn_medium_breakout_bull", "tbn_medium_line_is_provisional"] if c in signal_example_rows.columns]].copy()
        signal_example_rows = signal_example_rows.rename(columns={
            "timestamp": "bar_time",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "tbn_short_trend": "short_trend",
            "tbn_medium_trend": "medium_trend",
            "tbn_long_trend": "long_trend",
            "tbn_composite_trend": "trend_score",
            "tbn_medium_breakout_bull": "medium_bull_breakout",
            "tbn_medium_line_is_provisional": "medium_line_is_provisional",
        })
    signal_example_table = table_html(signal_example_rows)

    breakout_compare_df = signal_example.get("overview_breakouts_df")
    causal_signal_points_df = signal_example.get("overview_causal_signals_df")
    hindsight_signal_points_df = signal_example.get("overview_hindsight_only_df")
    if isinstance(breakout_compare_df, pd.DataFrame) and not breakout_compare_df.empty:
        breakout_compare_df = breakout_compare_df.copy()
        breakout_compare_df["timestamp"] = pd.to_datetime(breakout_compare_df["timestamp"], utc=True, errors="coerce")
        breakout_compare_df = breakout_compare_df.rename(columns={
            "timestamp": "breakout_bar",
            "timeframe": "tf",
            "side": "side",
            "trend_score": "trend_score",
            "line_is_provisional": "is_provisional",
            "line_value": "line_value",
            "close": "close",
        })
        causal_signal_set = set()
        hindsight_signal_set = set()
        if isinstance(causal_signal_points_df, pd.DataFrame) and not causal_signal_points_df.empty:
            causal_signal_set = set(pd.to_datetime(causal_signal_points_df["timestamp"], utc=True, errors="coerce"))
        if isinstance(hindsight_signal_points_df, pd.DataFrame) and not hindsight_signal_points_df.empty:
            hindsight_signal_set = set(pd.to_datetime(hindsight_signal_points_df["timestamp"], utc=True, errors="coerce"))
        breakout_compare_df["close_minus_line"] = safe_num(breakout_compare_df.get("close", pd.Series(dtype=float))).fillna(0.0) - safe_num(breakout_compare_df.get("line_value", pd.Series(dtype=float))).fillna(0.0)
        breakout_compare_df["signal_kind"] = breakout_compare_df["breakout_bar"].map(lambda ts: "causal" if ts in causal_signal_set else ("hindsight_only" if ts in hindsight_signal_set else "-"))
        breakout_compare_df = breakout_compare_df[[c for c in ["breakout_bar", "tf", "side", "trend_score", "line_value", "close", "close_minus_line", "is_provisional", "signal_kind"] if c in breakout_compare_df.columns]]
    else:
        breakout_compare_df = pd.DataFrame()
    breakout_compare_table = table_html(breakout_compare_df)

    segment_df = signal_example.get("overview_segments_df")
    if isinstance(segment_df, pd.DataFrame) and not segment_df.empty:
        segment_df = segment_df.copy()
        for c in ["segment_start", "segment_end"]:
            segment_df[c] = pd.to_datetime(segment_df[c], utc=True, errors="coerce")
        segment_df = segment_df.rename(columns={
            "timeframe": "tf",
            "segment_start": "segment_start",
            "segment_end": "segment_end",
            "duration_bars": "bars",
            "trend": "trend",
            "line_is_provisional": "is_provisional",
            "anchor_origin": "anchor_idx",
            "anchor_price": "anchor_px",
            "pivot_origin": "pivot_idx",
            "pivot_price": "pivot_px",
            "anchor_ts": "anchor_ts",
            "pivot_ts": "pivot_ts",
            "line_slope": "slope",
            "end_reason": "end_reason",
        })
        segment_df = segment_df[[c for c in ["tf", "segment_start", "segment_end", "bars", "trend", "is_provisional", "anchor_idx", "anchor_px", "pivot_idx", "pivot_px", "anchor_ts", "pivot_ts", "slope", "end_reason"] if c in segment_df.columns]]
    else:
        segment_df = pd.DataFrame()
    segment_table = table_html(segment_df)

    honesty_asset_view = honesty_asset_df.copy() if isinstance(honesty_asset_df, pd.DataFrame) else pd.DataFrame()
    if not honesty_asset_view.empty:
        honesty_asset_view = honesty_asset_view[[c for c in ["asset", "hindsight_signals", "causal_signals", "hindsight_only", "misleading_pct", "latest_hindsight_only"] if c in honesty_asset_view.columns]]
    honesty_asset_table = table_html(honesty_asset_view)

    honesty_detail_view = honesty_detail_df.copy() if isinstance(honesty_detail_df, pd.DataFrame) else pd.DataFrame()
    if not honesty_detail_view.empty:
        honesty_detail_view = honesty_detail_view[[c for c in ["asset", "event_ts", "direction", "trigger_tf", "entry_ts"] if c in honesty_detail_view.columns]].sort_values("event_ts", ascending=False).head(20)
    honesty_detail_table = table_html(honesty_detail_view)

    html = f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank29 live ops</title>
  <style>
    :root {{
      --bg:#020617; --panel:#0f172a; --panel2:#111827; --line:#1f2937; --muted:#94a3b8; --text:#e5e7eb;
    }}
    body {{ margin:0; background:var(--bg); color:var(--text); font-family:Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; }}
    .wrap {{ max-width:1320px; margin:0 auto; padding:28px 18px 80px; }}
    h1,h2,h3 {{ margin:0 0 10px; }}
    p,li {{ line-height:1.65; }}
    a {{ color:#60a5fa; }}
    .muted {{ color:var(--muted); }}
    .hero,.panel,.viz-card,.metric {{ background:var(--panel); border:1px solid var(--line); border-radius:18px; }}
    .hero {{ padding:20px 22px; margin-bottom:18px; }}
    .panel {{ padding:18px; margin-top:18px; }}
    .metric-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px; margin-top:14px; }}
    .metric {{ background:var(--panel2); padding:14px; border-radius:14px; }}
    .metric .k {{ font-size:12px; color:var(--muted); text-transform:uppercase; letter-spacing:.05em; }}
    .metric .v {{ font-size:28px; font-weight:800; margin-top:8px; }}
    .metric .s {{ margin-top:8px; color:#9ca3af; font-size:13px; }}
    .pill {{ display:inline-block; background:#0b1220; border:1px solid #334155; border-radius:999px; padding:6px 10px; font-size:12px; color:#cbd5e1; margin-top:8px; }}
    .viz-grid {{ display:grid; grid-template-columns:1.2fr 1fr; gap:14px; margin-top:16px; }}
    .dual-grid {{ display:grid; grid-template-columns:1.1fr 1fr; gap:16px; margin-top:16px; }}
    .triple-grid {{ display:grid; grid-template-columns:1.35fr 1fr; gap:16px; margin-top:16px; }}
    .rule-list li {{ margin-bottom:8px; }}
    .viz-card {{ padding:14px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:10px; background:var(--panel2); border:1px solid var(--line); border-radius:14px; overflow:hidden; }}
    th,td {{ text-align:left; padding:10px 12px; border-bottom:1px solid var(--line); font-size:13px; vertical-align:top; }}
    th {{ background:#0b1220; color:#cbd5e1; }}
    tr:last-child td {{ border-bottom:none; }}
    tr.pos td {{ background:rgba(34,197,94,0.05); }}
    tr.neg td {{ background:rgba(239,68,68,0.05); }}
    .empty {{ color:var(--muted); padding:18px 0; }}
    .archive-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:12px; margin-top:12px; }}
    .cta a {{ display:inline-block; margin-right:10px; margin-top:8px; padding:9px 12px; border-radius:10px; background:#1d4ed8; color:#fff; text-decoration:none; }}
    .cta a.secondary {{ background:#111827; border:1px solid #334155; color:#cbd5e1; }}
    @media (max-width:980px) {{ .viz-grid,.dual-grid {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body>
  <div class='wrap'>
    <div class='muted'>Generated: {escape(datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'))}</div>
    <div class='hero'>
      <p><a href='/momentum/factors/live_trading_center/report.html'>Live Trading Center</a> ｜ <a href='../index.html'>← 返回 factors 首页</a></p>
      <h1>Rank29 · archive / audit</h1>
      <p><b>Rank29 已停止实盘并降为 P0 archived。</b> 这页不再把它当“主运营页”，而是把相关证据收口成一页审计：<b>future leak 污染有多重</b>、<b>strict-causal 后为什么失效</b>、<b>旧 live / shadow 该怎么留档</b>。</p>
      <p class='muted'>页面结构已压缩：<b>shadow_dashboard</b> 保留为研究/历史口径页，<b>gate_live</b> 保留为 retired debug/raw 细页。任何旧的 Rank29 收益曲线，都只能按“历史污染样本”来读，不能再当作已验证有效的策略证据。</p>
      <div class='pill'>当前状态：P0 archived · live timer disabled · rank29 legacy live ↔ archived shadow（仅审计对照）</div>
      <div class='metric-grid'>{top_cards}</div>
      <div class='cta'>
        <a href='/momentum/factors/rank29_gate_live/report.html'>打开 live debug 细页</a>
        <a class='secondary' href='/momentum/factors/rank29_shadow_dashboard/report.html'>打开 research / archive 页</a>
        <a class='secondary' href='/momentum/factors/manual_narrow_paper_lanes/report.html'>打开 runner 状态页</a>
        <a class='secondary' href='/momentum/factors/rank29_orderbook_shadow/report.html'>打开 orderbook shadow 页</a>
      </div>
    </div>

    <section class='panel'>
      <h2>0) causal 基准下，一个信号当时是怎么通过准入的</h2>
      <p class='muted'>下面用 <b>{escape(signal_example.get('asset', EXAMPLE_ASSET))}</b> 在 <b>{fmt_ts(signal_example_trade.get('event_ts'))}</b> 的案例举例。现在这页默认把 <b>causal replay</b> 当主基准：只有当时真实可见的信息能给出信号，才算可交易；若某个标记只会在事后整段历史重算后才出现，就会被归类成 <b>hindsight-only</b>，不再当成真实可交易星号。</p>
      <div class='triple-grid'>
        <div class='viz-card'>
          <h3>单笔信号图：解释这一笔为什么触发</h3>
          <p class='muted'>这里用 <b>橙色实线</b> 画“该案例视角下真正参与判定的那条 confirmed line”，灰色虚线只保留作参考轨迹。蓝色竖线 = signal bar；绿色 = entry bar；红色 = exit bar。</p>
          {signal_example_svg(signal_example)}
        </div>
        <div>
          <div class='metric-grid'>{signal_example_cards}</div>
          {trend_formula_html}
          {line_formula_html}
          <div class='viz-card' style='margin-top:14px;'>
            <h3>什么情况下会触发 / 不会触发</h3>
            <ul class='rule-list'>
              <li><b>会触发：</b>某根 15m bar 出现 <b>confirmed line breakout</b>，同时 <b>做多时 trend_score ≥ 2 / 做空时 ≤ -2</b>。</li>
              <li><b>不会触发：</b>breakout 发生在 <b>provisional line</b> 上；这类信号最容易事后回看才出现，所以现在直接过滤。</li>
              <li><b>不会触发：</b>信号虽然成立，但已经过了 live freshness 窗口；实盘不会回头补下历史单。</li>
              <li><b>不会触发：</b>同一个 symbol 已经被更高优先级 lane 占用；三条 lane 只禁止同 symbol 重叠，不禁止不同 symbol 并发。</li>
              <li><b>gate 只调仓位，不直接否决：</b><code>low_trend_high_noise = 1</code> 时，这条线会缩到约 <b>25%</b> 仓位，而不是完全停做。</li>
            </ul>
          </div>
        </div>
      </div>
      <div class='viz-card' style='margin-top:16px;'>
        <h3>多时间框架总览：更多 K 线 + 多条趋势线 + 分数标记</h3>
        <p class='muted'>你刚才盯到的问题是对的：<b>每一条趋势线的生命周期内都应该是一条直线</b>，而 breakout 也应该和它实际突破的那条线发生可见交汇。所以这张总览图现在进一步改成：<b>同一生命周期继续画成一条直线</b>，若该段后来触发 breakout，就把通向 breakout bar 的最后一段改成<b>虚线延长</b>；同时把 <b>A=anchor</b>、<b>P=pivot</b> 两个定义点直接标出来。若只有 A 没有 P，就表示这段仍是 provisional，第二个点还没确认。</p>
        <p class='muted'><b>口径一致性：</b>图里的 breakout 圆点现在画在 <code>line_value</code> 上，方块画在当根 <code>close</code> 上，中间用竖向虚线连接；这样你能同时看到“突破发生在什么价位的线”与“收盘最终冲到了哪里”。<b>黄色实心星</b>表示 causal 真信号，<b>粉色空心星</b>表示 hindsight-only：事后回看会出现，但当时并不能诚实算出来。</p>
        {mtf_overview_svg(signal_example)}
      </div>
      <div class='dual-grid'>
        <div>
          <h3>breakout 点 vs 真正信号点（同口径对照）</h3>
          <p class='muted'>同一根 bar 里，breakout 点是“满足突破+分数”的候选；这里额外列出 <code>close_minus_line</code>，方便直接看收盘价到底越线了多少。<code>signal_kind=causal</code> 才是当前基准认可的真信号；<code>hindsight_only</code> 表示这根 bar 只有事后重算才会被打星。</p>
          {breakout_compare_table}
        </div>
        <div>
          <h3>趋势线生命周期分段明细</h3>
          <p class='muted'>每一段对应一条直线生命周期；当 anchor/pivot/slope/trend 任一变化，就结束当前段并开始下一段。现在表里也直接给出 anchor/pivot 的价格与索引；如果 <code>pivot_idx</code> 仍为空，说明这段还只是 provisional。</p>
          {segment_table}
        </div>
      </div>
      <div class='viz-card' style='margin-top:16px;'>
        <h3>示例 bar 明细</h3>
        <p class='muted'>这张表就是上面图里的原始数值：你可以直接看到哪一根 bar 的 <code>medium_bull_breakout</code> 从 0 变成 1，以及 short / medium / long 三个趋势分数是如何相加成 <code>trend_score</code> 的。</p>
        {signal_example_table}
      </div>
    </section>

    <section class='panel'>
      <h2>0.5) future leak 审计（最近 {honesty_audit.get('days', SIGNAL_AUDIT_DAYS)} 天）</h2>
      <p class='muted'>这里专门回答你刚才问的核心问题：<b>旧口径里的星号，有多少其实是被未来确认的 pivot / slope 回填误导出来的？</b> 当前统计口径是：先用 <code>confirmed_line_only</code> 扫一遍旧信号，再用 <code>causal_replay</code> 重放同一窗口；凡是旧信号里有、但 causal 重放里没有的，都记作 <b>hindsight-only</b>。</p>
      <div class='metric-grid'>
        {metric_card('旧口径信号数', str(honesty_audit.get('confirmed_signals', 0)), 'recent window · confirmed_line_only')}
        {metric_card('causal 真信号数', str(honesty_audit.get('causal_signals', 0)), 'recent window · causal_replay')}
        {metric_card('hindsight-only', str(honesty_audit.get('hindsight_only_signals', 0)), '旧口径有、causal 没有')}
        {metric_card('未来函数误导比例', pct(honesty_audit.get('misleading_pct')), 'hindsight_only / old_signals')}
      </div>
      <div class='dual-grid'>
        <div>
          <h3>按资产拆开</h3>
          <p class='muted'>如果某个资产的 <code>misleading_pct</code> 特别高，说明它在最近样本里特别依赖事后确认结构，实盘可信度就更低。</p>
          {honesty_asset_table}
        </div>
        <div>
          <h3>最近 hindsight-only 样本</h3>
          <p class='muted'>这些就是“图上会亮星，但当时其实算不出来”的代表案例。</p>
          {honesty_detail_table}
        </div>
      </div>
    </section>

    <section class='panel'>
      <h2>1) 累计收益曲线</h2>
      <p class='muted'>这里把 <b>rank29 live</b>、<b>gate shadow</b>、<b>baseline shadow</b> 放在同一张图上。看盘时先看这张：如果 live 明显开始背离 gate shadow，就说明要优先检查执行质量或优先级冲突，而不是先怀疑策略本体。</p>
      <div class='viz-card'>
        {line_chart_svg([
          curve_spec(live_df, 'rank29 live', '#38bdf8'),
          curve_spec(gate_shadow_df, 'gate shadow', '#f97316'),
          curve_spec(baseline_shadow_df, 'baseline shadow', '#22c55e'),
        ])}
      </div>
    </section>

    <section class='panel'>
      <h2>2) 逐笔赢亏</h2>
      <div class='viz-grid'>
        <div class='viz-card'>
          <h3>rank29 live 每笔已平仓</h3>
          <p class='muted'>向上 = 赢，向下 = 亏。live 如果还没成交，这里会为空。</p>
          {strip_chart_svg(live_df.tail(80), 'rank29 live')}
        </div>
        <div class='viz-card'>
          <h3>gate shadow 每笔参考</h3>
          <p class='muted'>这是 matching shadow 的逐笔参考，用来判断最近 shadow 本身是在顺风还是逆风环境。</p>
          {strip_chart_svg(gate_shadow_df.tail(80), 'gate shadow')}
        </div>
      </div>
    </section>

    <section class='panel'>
      <h2>3) 最近 live 与 shadow 对照</h2>
      <p class='muted'>这里直接看真钱 closed trades 和 gate shadow proxy 的同窗差值。当前如果还没很多真钱成交，这块会先比较稀疏，是正常的。</p>
      {table_html(compare_view)}
    </section>

    <section class='panel'>
      <h2>4) 最近真钱交易 / 当前持仓</h2>
      <div class='dual-grid'>
        <div>
          <h3>最近 live 已平仓</h3>
          {table_html(recent_live)}
        </div>
        <div>
          <h3>当前 open positions</h3>
          {table_html(open_view)}
        </div>
      </div>
    </section>

    <section class='panel'>
      <h2>5) 为什么没做单</h2>
      <div class='dual-grid'>
        <div>
          <h3>rejection reason 统计</h3>
          {table_html(reason_counts.head(12))}
        </div>
        <div>
          <h3>最近 warnings / orders</h3>
          <h4 class='muted'>warnings</h4>
          {table_html(warnings_view)}
          <h4 class='muted'>recent orders</h4>
          {table_html(orders_view)}
        </div>
      </div>
    </section>

    <section class='panel'>
      <h2>6) Archive / Debug / Research</h2>
      <p class='muted'>这些页面还保留，但默认不再是主入口。后面排障或回看研究时再点进去。</p>
      <div class='archive-grid'>{archive_cards}</div>
      <div class='dual-grid'>
        <div>
          <h3>archive 入口</h3>
          <ul>
            <li><a href='/momentum/factors/rank29_shadow_dashboard/report.html'>rank29 shadow dashboard</a>（研究 / 真实 paper / replay）</li>
            <li><a href='/momentum/factors/rank29_gate_live/report.html'>rank29 gate live</a>（debug / recent orders / rejections）</li>
            <li><a href='/momentum/factors/manual_narrow_paper_lanes/report.html'>manual narrow paper lanes</a>（runner / watermark / append-only）</li>
            <li><a href='/momentum/factors/rank29_orderbook_shadow/report.html'>rank29 orderbook shadow</a>（执行层影子）</li>
            <li><a href='/momentum/factors/scout_rank29_trendline_breakout_navigator_15m/report.html'>clean replication</a>（策略本体研究）</li>
          </ul>
        </div>
        <div>
          <h3>actual append-only snapshot</h3>
          <p class='muted'>这块只做 sanity check，不再占首页 headline。</p>
          <div class='metric-grid'>
            {metric_card('actual gate paper', actual_gate_val, actual_gate_sub)}
            {metric_card('manual runner', runner_last, f"last refresh={fmt_ts(run_summary.get('run_at_utc'))} · new appended={run_summary.get('new_closed_trades_appended', 0)}")}
          </div>
        </div>
      </div>
    </section>
  </div>
</body>
</html>
"""

    OUT_PATH.write_text(html, encoding="utf-8")
    print(OUT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
