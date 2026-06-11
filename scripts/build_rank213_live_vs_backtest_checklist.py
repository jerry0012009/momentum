#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
LIVE_ART_DIR = ROOT / "reports" / "artifacts" / "rank213_age90_live_canary_shell"
PAPER_ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank213_age90_live"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "rank213_live_vs_backtest_checklist"
OUT_JSON = LIVE_ART_DIR / "live_vs_backtest_checklist.json"
OUT_HTML = SITE_DIR / "report.html"
CLOSEOUT_PAGE_PATH = ROOT / "reports" / "site" / "paper" / "rank213_archive_closeout.html"
CLOSEOUT_RECEIPT_PATH = LIVE_ART_DIR / "rank213_archive_closeout_receipt.json"

LIVE_STATE_PATH = LIVE_ART_DIR / "live_state.json"
LIVE_STATUS_PATH = LIVE_ART_DIR / "live_status.json"
LIVE_COMPARE_PATH = LIVE_ART_DIR / "live_vs_shadow_summary.json"
LIVE_POSITIONS_PATH = LIVE_ART_DIR / "live_exchange_positions.json"
LIVE_ORDERS_PATH = LIVE_ART_DIR / "live_recent_orders.json"
SHADOW_DECISION_PATH = PAPER_ART_DIR / "rank213_age90_shadow_current_decision.json"
SHADOW_STATUS_PATH = PAPER_ART_DIR / "rank213_age90_shadow_status.json"
PAPER_REFERENCE_CLOSED_PATH = PAPER_ART_DIR / "rank213_age90_paper_reference_closed.csv"
PAPER_REFERENCE_OPEN_PATH = PAPER_ART_DIR / "rank213_age90_paper_reference_open.csv"
PAPER_REFERENCE_STATUS_PATH = PAPER_ART_DIR / "rank213_age90_paper_reference_status.json"
PAPER_REFERENCE_CURVE_PATH = PAPER_ART_DIR / "rank213_age90_paper_reference_curve.csv"
DRIFT_ATTRIBUTION_PATH = LIVE_ART_DIR / "live_vs_backtest_drift_attribution.csv"
DRIFT_SUMMARY_PATH = LIVE_ART_DIR / "live_vs_backtest_drift_summary.json"

BASKET_NOTIONAL_USDT = 120.0
HOLD_HOURS = 3
DEFAULT_ENTRY_FEE_BPS_MAKER = 2.0
DEFAULT_ENTRY_FEE_BPS_TAKER = 5.0
DEFAULT_EXIT_FEE_BPS_TAKER = 5.0


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


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def safe_float(series: Any) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def safe_bool_series(series: Any) -> pd.Series:
    if isinstance(series, pd.Series):
        source = series
    elif series is None:
        source = pd.Series(dtype="object")
    else:
        source = pd.Series(series)

    def coerce(value: Any) -> bool:
        if isinstance(value, (list, tuple, set, dict)):
            return False
        if value is None or value == "" or pd.isna(value):
            return False
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"true", "1", "yes", "y", "on"}:
                return True
            if lowered in {"false", "0", "no", "n", "off", "nan", "none", "[]", "{}"}:
                return False
        return bool(value)

    return source.map(coerce)


def as_ts(series: Any) -> pd.Series:
    return pd.to_datetime(series, utc=True, errors="coerce")


def fmt_ts(v: Any) -> str:
    if v is None or v == "" or pd.isna(v):
        return "-"
    try:
        return pd.to_datetime(v, utc=True).strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        text = str(v)
        return "-" if text in {"nan", "None"} else text


def money(v: Any, digits: int = 3) -> str:
    if v is None or v == "" or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f} USDT"


def num(v: Any, digits: int = 2) -> str:
    if v is None or v == "" or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f}"


def bps(v: Any, digits: int = 1) -> str:
    if v is None or v == "" or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f} bps"


def pct(v: Any, digits: int = 2) -> str:
    if v is None or v == "" or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def classify_metric_kind(v: Any) -> str:
    if v is None or v == "" or pd.isna(v):
        return ""
    val = float(v)
    return "pos" if val > 0 else ("neg" if val < 0 else "flat")


def compute_loss_streak(live_closed: pd.DataFrame) -> dict[str, Any]:
    if live_closed.empty or "basket_net_pnl" not in live_closed.columns:
        return {
            "wins": 0,
            "losses": 0,
            "mean_basket_pnl": None,
            "last3_all_negative": False,
            "last5_all_negative": False,
            "recent_basket_pnls": [],
            "sustained_loss": False,
        }
    work = live_closed.copy()
    work["basket_net_pnl"] = safe_float(work["basket_net_pnl"])
    work["decision_ts"] = as_ts(work.get("decision_ts"))
    work = work[work["basket_net_pnl"].notna()].sort_values("decision_ts").reset_index(drop=True)
    pnls = [float(v) for v in work["basket_net_pnl"].tolist()]
    wins = sum(1 for v in pnls if v > 0)
    losses = sum(1 for v in pnls if v < 0)
    last3 = pnls[-3:]
    last5 = pnls[-5:]
    last3_all_negative = len(last3) >= 3 and all(v < 0 for v in last3)
    last5_all_negative = len(last5) >= 5 and all(v < 0 for v in last5)
    return {
        "wins": wins,
        "losses": losses,
        "mean_basket_pnl": (sum(pnls) / len(pnls)) if pnls else None,
        "last3_all_negative": last3_all_negative,
        "last5_all_negative": last5_all_negative,
        "recent_basket_pnls": pnls[-6:],
        "sustained_loss": losses >= 3 and (last3_all_negative or last5_all_negative),
    }


def fee_bps_to_rate(v: Any, default_bps: float) -> float:
    try:
        return float(v) / 10000.0
    except Exception:
        return default_bps / 10000.0


def build_closeout_basket_df(*, live_state: dict[str, Any], closeout_receipt: dict[str, Any], exec_cfg: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    if not closeout_receipt or str(closeout_receipt.get("mode") or "") != "execute":
        return pd.DataFrame(), pd.DataFrame(), {}
    flatten_orders = [row for row in safe_list(closeout_receipt.get("flatten_orders")) if isinstance(row, dict)]
    if not flatten_orders:
        return pd.DataFrame(), pd.DataFrame(), {}

    live_positions = {
        str(row.get("symbol") or "").upper(): row
        for row in safe_list(live_state.get("live_positions"))
        if isinstance(row, dict) and str(row.get("symbol") or "")
    }
    entry_fee_maker = fee_bps_to_rate(exec_cfg.get("entry_fee_bps_maker"), DEFAULT_ENTRY_FEE_BPS_MAKER)
    entry_fee_taker = fee_bps_to_rate(exec_cfg.get("entry_fee_bps_taker"), DEFAULT_ENTRY_FEE_BPS_TAKER)
    exit_fee_taker = fee_bps_to_rate(exec_cfg.get("exit_fee_bps_taker"), DEFAULT_EXIT_FEE_BPS_TAKER)

    leg_rows: list[dict[str, Any]] = []
    for row in flatten_orders:
        symbol = str(row.get("symbol") or "").upper()
        pos = safe_dict(live_positions.get(symbol))
        result = safe_dict(row.get("result"))
        qty = float(safe_float(pd.Series([result.get("executed_qty") or row.get("current_exchange_qty") or row.get("qty")])).fillna(0.0).iloc[0])
        entry_price = float(safe_float(pd.Series([pos.get("entry_price") or row.get("entry_price")])).fillna(0.0).iloc[0])
        exit_price = float(safe_float(pd.Series([result.get("avg_price") or row.get("avg_price")])).fillna(0.0).iloc[0])
        side = str(pos.get("side") or row.get("side") or "").lower()
        if not symbol or side not in {"long", "short"} or qty <= 0 or entry_price <= 0 or exit_price <= 0:
            continue
        gross = (exit_price - entry_price) * qty if side == "long" else (entry_price - exit_price) * qty
        entry_notional = float(safe_float(pd.Series([pos.get("entry_notional") or entry_price * qty])).fillna(entry_price * qty).iloc[0])
        exit_notional = exit_price * qty
        entry_used_taker = bool(pos.get("entry_fallback_used")) or str(pos.get("final_entry_status") or "") == "fallback_filled"
        entry_fee = entry_notional * (entry_fee_taker if entry_used_taker else entry_fee_maker)
        exit_fee = exit_notional * exit_fee_taker
        total_fee = entry_fee + exit_fee
        net = gross - total_fee
        basket_id = str(pos.get("basket_id") or (safe_list(row.get("basket_ids"))[0] if safe_list(row.get("basket_ids")) else "rank213-closeout"))
        decision_ts = pos.get("signal_timestamp") or pos.get("planned_exit_ts") or pos.get("entry_time")
        leg_rows.append({
            "basket_id": basket_id,
            "decision_ts": decision_ts,
            "exit_ts": closeout_receipt.get("flatten_submitted_at_utc"),
            "symbol": symbol,
            "side": side,
            "gross_pnl": gross,
            "fee": total_fee,
            "net_pnl": net,
            "entry_notional": entry_notional,
            "entry_fee": entry_fee,
            "exit_fee": exit_fee,
            "entry_fee_mode": "taker" if entry_used_taker else "maker",
            "exit_fee_mode": "taker_closeout",
            "exit_reason": "archive_closeout_market",
        })

    if not leg_rows:
        return pd.DataFrame(), pd.DataFrame(), {}
    legs_df = pd.DataFrame(leg_rows)
    legs_df["decision_ts"] = as_ts(legs_df["decision_ts"])
    legs_df["exit_ts"] = as_ts(legs_df["exit_ts"])
    basket_df = (
        legs_df.groupby("basket_id", as_index=False)
        .agg(
            decision_ts=("decision_ts", "min"),
            exit_ts=("exit_ts", "max"),
            leg_count=("symbol", "count"),
            basket_gross_pnl=("gross_pnl", "sum"),
            basket_fee=("fee", "sum"),
            basket_net_pnl=("net_pnl", "sum"),
            entry_notional=("entry_notional", "sum"),
            symbols=("symbol", lambda s: ", ".join(sorted({str(v) for v in s if str(v)}))),
            exit_reasons=("exit_reason", lambda s: ", ".join(sorted({str(v) for v in s if str(v)}))),
        )
        .sort_values("decision_ts")
        .reset_index(drop=True)
    )
    basket_df["basket_net_bps"] = basket_df.apply(lambda r: (float(r["basket_net_pnl"]) / float(r["entry_notional"]) * 10000.0) if float(r["entry_notional"] or 0.0) else None, axis=1)
    basket_df["status"] = "closed_archive_closeout"
    summary = {
        "basket_count": int(len(basket_df)),
        "leg_count": int(len(legs_df)),
        "gross_pnl": float(legs_df["gross_pnl"].sum()),
        "fee": float(legs_df["fee"].sum()),
        "net_pnl": float(legs_df["net_pnl"].sum()),
    }
    return basket_df, legs_df, summary


def metric_card(title: str, value: str, sub: str) -> str:
    return f"<div class='metric'><div class='k'>{escape(title)}</div><div class='v'>{escape(value)}</div><div class='s'>{sub}</div></div>"


def table_html(df: pd.DataFrame) -> str:
    if df.empty:
        return '<p class="empty">暂无数据。</p>'
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows: list[str] = []
    for _, row in df.iterrows():
        row_class = ""
        pnl_val = None
        for col in ["live_net_pnl", "paper_pnl_usdt", "delta_vs_paper", "unrealized_pnl", "net_pnl", "basket_net_pnl"]:
            if col in df.columns:
                try:
                    pnl_val = float(row.get(col))
                    break
                except Exception:
                    pass
        if pnl_val is not None:
            row_class = "pos" if pnl_val > 0 else ("neg" if pnl_val < 0 else "flat")
        cells: list[str] = []
        for col in df.columns:
            value = row[col]
            if col.endswith("_ts") or col.endswith("_time") or col in {"ts", "decision_ts", "entry_ts", "exit_ts", "planned_exit_ts", "updated_at_utc", "last_run_utc"}:
                text = fmt_ts(value)
            elif any(token in col for token in ["pnl", "fee", "mtm"]) and col not in {"pnl_style"}:
                text = money(value, 3)
            elif col.endswith("_bps") or col == "delta_bps":
                text = bps(value, 1)
            else:
                text = "-" if value is None or str(value) in {"nan", "None"} else str(value)
            cells.append(f"<td>{escape(text)}</td>")
        rows.append(f"<tr class='{row_class}'>{''.join(cells)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def line_chart_svg(series_list: list[dict[str, Any] | None], *, width: int = 760, height: int = 220) -> str:
    valid = [s for s in series_list if s and s.get("points")]
    if not valid:
        return '<div class="empty">当前时间窗口内暂无可绘制的曲线。</div>'

    all_y = [0.0]
    all_t: list[pd.Timestamp] = []
    normalized: list[dict[str, Any]] = []
    for s in valid:
        pts: list[tuple[pd.Timestamp, float]] = []
        for p in s.get("points", []):
            ts = pd.to_datetime(p.get("ts"), utc=True, errors="coerce")
            val = p.get("value")
            if pd.isna(ts) or val is None:
                continue
            pts.append((ts, float(val)))
            all_t.append(ts)
            all_y.append(float(val))
        if pts:
            normalized.append({**s, "points_norm": pts})
    if not normalized or not all_t:
        return '<div class="empty">当前时间窗口内暂无可绘制的曲线。</div>'

    ymin, ymax = min(all_y), max(all_y)
    span = max(ymax - ymin, 1e-9)
    ymin -= span * 0.12 + 1e-9
    ymax += span * 0.12 + 1e-9
    plot_x, plot_y, plot_w, plot_h = 44, 16, width - 56, height - 38
    tmin, tmax = min(all_t), max(all_t)
    trange = max((tmax - tmin).total_seconds(), 1.0)

    def xy(ts: pd.Timestamp, val: float) -> tuple[float, float]:
        if trange <= 1.0:
            x = plot_x + plot_w / 2
        else:
            x = plot_x + (((ts - tmin).total_seconds()) / trange) * plot_w
        y = plot_y + plot_h - ((val - ymin) / (ymax - ymin)) * plot_h
        return x, y

    zero_y = xy(tmin, 0.0)[1]
    parts = [
        f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" role="img">',
        f'<line x1="{plot_x}" y1="{zero_y:.2f}" x2="{plot_x + plot_w}" y2="{zero_y:.2f}" stroke="#334155" stroke-dasharray="4 4" />',
        f'<rect x="{plot_x}" y="{plot_y}" width="{plot_w}" height="{plot_h}" rx="10" fill="none" stroke="#1f2937" />',
    ]
    legend_x = plot_x
    for s in normalized:
        pts = [xy(ts, val) for ts, val in s["points_norm"]]
        if len(pts) == 1:
            x, y = pts[0]
            parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4.2" fill="{s["color"]}" />')
        else:
            path = " ".join(("M" if i == 0 else "L") + f" {x:.2f} {y:.2f}" for i, (x, y) in enumerate(pts))
            parts.append(f'<path d="{path}" fill="none" stroke="{s["color"]}" stroke-width="2.4" />')
            for x, y in pts:
                parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="2.6" fill="{s["color"]}" />')
        lx, ly = pts[-1]
        parts.append(f'<circle cx="{lx:.2f}" cy="{ly:.2f}" r="3.4" fill="{s["color"]}" />')
        parts.append(f'<rect x="{legend_x}" y="{height - 16}" width="10" height="10" rx="3" fill="{s["color"]}" />')
        parts.append(f'<text x="{legend_x + 16}" y="{height - 7}" fill="#cbd5e1" font-size="12">{escape(str(s["label"]))}</text>')
        legend_x += 186
    parts.append(f'<text x="6" y="{plot_y + 10}" fill="#94a3b8" font-size="11">{money(ymax, 1)}</text>')
    parts.append(f'<text x="6" y="{zero_y - 4:.2f}" fill="#64748b" font-size="11">0</text>')
    parts.append(f'<text x="6" y="{plot_y + plot_h}" fill="#94a3b8" font-size="11">{money(ymin, 1)}</text>')
    parts.append(f'<text x="{plot_x}" y="{height - 24}" fill="#64748b" font-size="11">{escape(tmin.strftime("%m-%d %H:%M"))}</text>')
    parts.append(f'<text x="{plot_x + plot_w - 74}" y="{height - 24}" fill="#64748b" font-size="11">{escape(tmax.strftime("%m-%d %H:%M"))}</text>')
    parts.append("</svg>")
    return "".join(parts)


def bar_chart_svg(df: pd.DataFrame, value_col: str, label_col: str, *, width: int = 760, height: int = 220) -> str:
    if df.empty or value_col not in df.columns or label_col not in df.columns:
        return '<div class="empty">当前时间窗口内暂无可绘制的柱状对比。</div>'
    vals = safe_float(df[value_col]).fillna(0.0).tolist()
    labels = [str(v) for v in df[label_col].tolist()]
    if not vals:
        return '<div class="empty">当前时间窗口内暂无可绘制的柱状对比。</div>'
    max_abs = max(max(abs(v) for v in vals), 1e-9)
    plot_x, plot_y, plot_w, plot_h = 40, 16, width - 52, height - 46
    center_y = plot_y + plot_h / 2
    bar_w = max(min(plot_w / max(len(vals), 1) * 0.62, 28), 6)
    gap = plot_w / max(len(vals), 1)
    parts = [
        f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" role="img">',
        f'<line x1="{plot_x}" y1="{center_y:.2f}" x2="{plot_x + plot_w}" y2="{center_y:.2f}" stroke="#334155" stroke-dasharray="4 4" />',
    ]
    for i, value in enumerate(vals):
        x = plot_x + gap * i + (gap - bar_w) / 2
        h = abs(value) / max_abs * (plot_h * 0.42)
        y = center_y - h if value >= 0 else center_y
        color = "#22c55e" if value > 0 else ("#ef4444" if value < 0 else "#94a3b8")
        parts.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_w:.2f}" height="{max(h,1.5):.2f}" rx="3" fill="{color}" />')
        if len(vals) <= 16 or i % max(len(vals) // 8, 1) == 0 or i == len(vals) - 1:
            parts.append(f'<text x="{x + bar_w / 2:.2f}" y="{height - 12}" text-anchor="middle" fill="#64748b" font-size="11">{escape(labels[i])}</text>')
    parts.append(f'<text x="4" y="{plot_y + 10}" fill="#94a3b8" font-size="11">{money(max_abs, 1)}</text>')
    parts.append(f'<text x="4" y="{center_y + 4:.2f}" fill="#64748b" font-size="11">0</text>')
    parts.append(f'<text x="4" y="{plot_y + plot_h}" fill="#94a3b8" font-size="11">-{money(max_abs, 1)}</text>')
    parts.append("</svg>")
    return "".join(parts)


def timeline_band_svg(df: pd.DataFrame, *, width: int = 760, height: int = 108) -> str:
    if df.empty or "timeline_status" not in df.columns:
        return '<div class="empty">当前时间窗口内暂无可绘制的时间带。</div>'
    work = df.copy()
    work["decision_ts"] = as_ts(work.get("decision_ts"))
    work = work[work["decision_ts"].notna()].sort_values("decision_ts").reset_index(drop=True)
    if work.empty:
        return '<div class="empty">当前时间窗口内暂无可绘制的时间带。</div>'

    color_map = {
        "exact_match": "#22c55e",
        "symbol_mismatch": "#facc15",
        "economic_drift": "#ef4444",
        "open_snapshot": "#60a5fa",
        "missing_coverage": "#94a3b8",
    }
    label_map = {
        "exact_match": "exact match",
        "symbol_mismatch": "symbol mismatch",
        "economic_drift": "economic drift",
        "open_snapshot": "open snapshot",
        "missing_coverage": "missing coverage",
    }

    plot_x, plot_y, plot_w, band_h = 24, 22, width - 36, 26
    n = max(len(work), 1)
    gap = plot_w / n
    cell_w = max(min(gap * 0.84, 28), 6)
    parts = [
        f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" role="img">',
        f'<rect x="{plot_x}" y="{plot_y}" width="{plot_w}" height="{band_h}" rx="10" fill="none" stroke="#1f2937" />',
    ]
    for i, row in work.iterrows():
        x = plot_x + gap * i + (gap - cell_w) / 2
        status = str(row.get("timeline_status") or "missing_coverage")
        color = color_map.get(status, "#94a3b8")
        parts.append(f'<rect x="{x:.2f}" y="{plot_y + 4:.2f}" width="{cell_w:.2f}" height="{band_h - 8:.2f}" rx="4" fill="{color}" />')
        if len(work) <= 16 or i % max(len(work) // 8, 1) == 0 or i == len(work) - 1:
            label = pd.to_datetime(row.get("decision_ts"), utc=True).strftime("%m-%d %H:%M")
            parts.append(f'<text x="{x + cell_w / 2:.2f}" y="{plot_y + band_h + 18:.2f}" text-anchor="middle" fill="#64748b" font-size="11">{escape(label)}</text>')

    legend_x = plot_x
    legend_y = height - 12
    for key in ["exact_match", "symbol_mismatch", "economic_drift", "open_snapshot", "missing_coverage"]:
        parts.append(f'<rect x="{legend_x}" y="{legend_y - 9}" width="10" height="10" rx="3" fill="{color_map[key]}" />')
        parts.append(f'<text x="{legend_x + 15}" y="{legend_y}" fill="#cbd5e1" font-size="12">{escape(label_map[key])}</text>')
        legend_x += 120
    parts.append("</svg>")
    return "".join(parts)


def curve_series(df: pd.DataFrame, *, ts_col: str, value_col: str, label: str, color: str, cumulative: bool = True) -> dict[str, Any] | None:
    if df.empty or ts_col not in df.columns or value_col not in df.columns:
        return None
    work = df.copy()
    work[ts_col] = as_ts(work[ts_col])
    work[value_col] = safe_float(work[value_col]).fillna(0.0)
    work = work[work[ts_col].notna()].sort_values(ts_col).reset_index(drop=True)
    if work.empty:
        return None
    if cumulative:
        work["chart_value"] = work[value_col].cumsum()
    else:
        work["chart_value"] = work[value_col]
    return {
        "label": label,
        "color": color,
        "points": [{"ts": ts.isoformat(), "value": float(val)} for ts, val in zip(work[ts_col], work["chart_value"], strict=False)],
    }


def load_live_closed_baskets(live_state: dict[str, Any]) -> pd.DataFrame:
    rows = live_state.get("closed_trades", []) or []
    if not rows:
        return pd.DataFrame(columns=["basket_id", "decision_ts", "exit_ts", "leg_count", "basket_net_pnl", "basket_fee", "basket_gross_pnl", "entry_notional", "basket_net_bps", "symbols", "exit_reasons", "status"])
    df = pd.DataFrame(rows).copy()
    df["decision_ts"] = as_ts(df.get("signal_timestamp"))
    df["exit_ts"] = as_ts(df.get("exit_time"))
    df["gross_pnl"] = safe_float(df.get("gross_pnl")).fillna(0.0)
    df["net_pnl"] = safe_float(df.get("net_pnl")).fillna(0.0)
    df["fee"] = safe_float(df.get("fee")).fillna(0.0)
    df["entry_notional_leg"] = safe_float(df.get("qty")).fillna(0.0) * safe_float(df.get("entry_price")).fillna(0.0)
    basket_ids = df.get("basket_id")
    if basket_ids is None:
        df["basket_id"] = ""
    else:
        df["basket_id"] = basket_ids.where(basket_ids.notna(), "")
    df["basket_id"] = df["basket_id"].astype(str)
    df["symbol"] = df.get("symbol", "").astype(str)
    df["exit_reason"] = df.get("exit_reason", "").astype(str)
    df = df[~df["basket_id"].isin(["", "nan", "None"])].copy()
    if df.empty:
        return pd.DataFrame(columns=["basket_id", "decision_ts", "exit_ts", "leg_count", "basket_net_pnl", "basket_fee", "basket_gross_pnl", "entry_notional", "basket_net_bps", "symbols", "exit_reasons", "status"])

    def join_unique(series: pd.Series) -> str:
        vals = sorted({str(v) for v in series if str(v)})
        return ", ".join(vals)

    out = (
        df.groupby("basket_id", as_index=False)
        .agg(
            decision_ts=("decision_ts", "min"),
            exit_ts=("exit_ts", "max"),
            leg_count=("symbol", "count"),
            basket_gross_pnl=("gross_pnl", "sum"),
            basket_fee=("fee", "sum"),
            basket_net_pnl=("net_pnl", "sum"),
            entry_notional=("entry_notional_leg", "sum"),
            symbols=("symbol", join_unique),
            exit_reasons=("exit_reason", join_unique),
        )
        .sort_values("decision_ts")
        .reset_index(drop=True)
    )
    out["basket_net_bps"] = out.apply(lambda r: (float(r["basket_net_pnl"]) / float(r["entry_notional"]) * 10000.0) if float(r["entry_notional"] or 0.0) else None, axis=1)
    out["status"] = "closed"
    return out


def load_live_orphan_closed_adjustment(live_state: dict[str, Any]) -> pd.DataFrame:
    rows = live_state.get("closed_trades", []) or []
    if not rows:
        return pd.DataFrame(columns=["basket_id", "decision_ts", "exit_ts", "leg_count", "basket_net_pnl", "basket_fee", "basket_gross_pnl", "entry_notional", "basket_net_bps", "symbols", "exit_reasons", "status"])
    df = pd.DataFrame(rows).copy()
    basket_ids = df.get("basket_id")
    if basket_ids is None:
        mask = pd.Series([True] * len(df))
    else:
        basket_text = basket_ids.astype(str)
        mask = basket_ids.isna() | basket_text.isin(["", "None", "nan"])
    df = df[mask].copy()
    if df.empty:
        return pd.DataFrame(columns=["basket_id", "decision_ts", "exit_ts", "leg_count", "basket_net_pnl", "basket_fee", "basket_gross_pnl", "entry_notional", "basket_net_bps", "symbols", "exit_reasons", "status"])
    df["decision_ts"] = as_ts(df.get("signal_timestamp"))
    df["exit_ts"] = as_ts(df.get("exit_time"))
    df["gross_pnl"] = safe_float(df.get("gross_pnl")).fillna(0.0)
    df["net_pnl"] = safe_float(df.get("net_pnl")).fillna(0.0)
    df["fee"] = safe_float(df.get("fee")).fillna(0.0)
    df["entry_notional_leg"] = safe_float(df.get("qty")).fillna(0.0) * safe_float(df.get("entry_price")).fillna(0.0)
    symbols = ", ".join(sorted({str(v) for v in df.get("symbol", []) if str(v)}))
    reasons = ", ".join(sorted({str(v) for v in df.get("exit_reason", []) if str(v)}))
    out = pd.DataFrame([{
        "basket_id": "rank213-unbucketed-closed-adjustment",
        "decision_ts": df["decision_ts"].min(),
        "exit_ts": df["exit_ts"].max(),
        "leg_count": int(len(df)),
        "basket_gross_pnl": float(df["gross_pnl"].sum()),
        "basket_fee": float(df["fee"].sum()),
        "basket_net_pnl": float(df["net_pnl"].sum()),
        "entry_notional": float(df["entry_notional_leg"].sum()),
        "symbols": symbols,
        "exit_reasons": reasons,
        "status": "closed_unbucketed_adjustment",
    }])
    out["basket_net_bps"] = out.apply(lambda r: (float(r["basket_net_pnl"]) / float(r["entry_notional"]) * 10000.0) if float(r["entry_notional"] or 0.0) else None, axis=1)
    return out


def load_live_open_legs(exchange_positions: list[dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for pos in exchange_positions:
        if not bool(pos.get("rank213_owned")):
            continue
        claims = pos.get("matched_local_claims", []) or []
        live_claims = [claim for claim in claims if str(claim.get("local_status") or "") == "live_open" and str(claim.get("basket_id") or "")]
        claim = live_claims[0] if live_claims else {}
        matched_basket_ids = [str(v) for v in (pos.get("matched_basket_ids") or []) if str(v)]
        basket_id = str(claim.get("basket_id") or "") or (matched_basket_ids[0] if matched_basket_ids else "")
        if not basket_id:
            basket_id = f"rank213-residual-{str(pos.get('symbol') or '').lower()}-{str(pos.get('side') or '').lower()}"
        if not live_claims and not matched_basket_ids and str(pos.get("reconciliation_classification") or "") != "residual_open_on_exchange":
            continue
        rows.append(
            {
                "basket_id": basket_id,
                "decision_ts": claim.get("signal_timestamp") or (basket_id.split("rank213-", 1)[1] if basket_id.startswith("rank213-") and "T" in basket_id else None),
                "planned_exit_ts": claim.get("planned_exit_ts"),
                "symbol": str(pos.get("symbol") or ""),
                "side": str(pos.get("side") or claim.get("side") or ""),
                "basket_role": str(claim.get("basket_role") or "residual"),
                "entry_time": claim.get("entry_time"),
                "entry_price": safe_float(pd.Series([claim.get("entry_price") if claim else pos.get("entry_price")])).iloc[0],
                "qty": safe_float(pd.Series([pos.get("qty")])).iloc[0],
                "unrealized_pnl": safe_float(pd.Series([pos.get("unrealized_pnl")])).fillna(0.0).iloc[0],
                "submit_outcome": str(claim.get("submit_outcome") or ("residual_open_on_exchange" if not live_claims else "")),
                "fallback_reason": str(claim.get("fallback_reason") or ""),
            }
        )
    if not rows:
        return pd.DataFrame(columns=["basket_id", "decision_ts", "planned_exit_ts", "symbol", "side", "basket_role", "entry_time", "entry_price", "qty", "unrealized_pnl", "submit_outcome", "fallback_reason"])
    df = pd.DataFrame(rows)
    df["decision_ts"] = as_ts(df["decision_ts"])
    df["planned_exit_ts"] = as_ts(df["planned_exit_ts"])
    df["entry_time"] = as_ts(df["entry_time"])
    return df.sort_values(["decision_ts", "basket_role", "symbol"], na_position="last").reset_index(drop=True)


def load_live_open_baskets(open_legs: pd.DataFrame) -> pd.DataFrame:
    if open_legs.empty:
        return pd.DataFrame(columns=["basket_id", "decision_ts", "planned_exit_ts", "leg_count", "basket_net_pnl", "symbols", "submit_outcomes", "status"])

    def join_unique(series: pd.Series) -> str:
        vals = sorted({str(v) for v in series if str(v)})
        return ", ".join(vals)

    out = (
        open_legs.groupby("basket_id", as_index=False)
        .agg(
            decision_ts=("decision_ts", "min"),
            planned_exit_ts=("planned_exit_ts", "max"),
            leg_count=("symbol", "count"),
            basket_net_pnl=("unrealized_pnl", "sum"),
            symbols=("symbol", join_unique),
            submit_outcomes=("submit_outcome", join_unique),
        )
        .sort_values("decision_ts")
        .reset_index(drop=True)
    )
    out["status"] = "open_mtm"
    return out


def load_paper_closed_reference() -> pd.DataFrame:
    keep = [
        "decision_ts", "actual_exit_ts", "paper_pnl_usdt", "paper_net_bps", "paper_mode", "reference_status",
        "longs", "shorts", "gate_on", "veto_count", "paper_price_ret", "paper_funding_ret", "paper_net_ret",
        "paper_turnover_x", "funding_events",
    ]
    closed = read_csv(PAPER_REFERENCE_CLOSED_PATH)
    if closed.empty:
        return pd.DataFrame(columns=keep)
    closed = closed.copy()
    closed["decision_ts"] = as_ts(closed.get("decision_ts"))
    closed["actual_exit_ts"] = as_ts(closed.get("actual_exit_ts"))
    for col in ["paper_pnl_usdt", "paper_net_bps", "paper_price_ret", "paper_funding_ret", "paper_net_ret", "paper_turnover_x"]:
        closed[col] = safe_float(closed.get(col))
    for col in ["veto_count", "funding_events"]:
        closed[col] = safe_float(closed.get(col))
    closed["gate_on"] = safe_bool_series(closed.get("gate_on"))
    closed_out = closed[keep].copy()
    return closed_out[closed_out["decision_ts"].notna()].sort_values("decision_ts").reset_index(drop=True)


def load_paper_open_reference() -> pd.DataFrame:
    keep = [
        "decision_ts", "planned_exit_ts", "mark_ts", "paper_pnl_usdt", "paper_net_bps", "paper_mode", "reference_status",
        "longs", "shorts", "gate_on", "veto_count", "paper_price_ret", "paper_funding_ret", "paper_net_ret",
        "paper_turnover_x", "funding_events",
    ]
    open_df = read_csv(PAPER_REFERENCE_OPEN_PATH)
    if open_df.empty:
        return pd.DataFrame(columns=keep)
    open_df = open_df.copy()
    open_df["decision_ts"] = as_ts(open_df.get("decision_ts"))
    open_df["planned_exit_ts"] = as_ts(open_df.get("planned_exit_ts"))
    open_df["mark_ts"] = as_ts(open_df.get("mark_ts"))
    for col in ["paper_pnl_usdt", "paper_net_bps", "paper_price_ret", "paper_funding_ret", "paper_net_ret", "paper_turnover_x"]:
        open_df[col] = safe_float(open_df.get(col))
    for col in ["veto_count", "funding_events"]:
        open_df[col] = safe_float(open_df.get(col))
    open_df["gate_on"] = safe_bool_series(open_df.get("gate_on"))
    out = open_df[keep].copy()
    return out[out["decision_ts"].notna()].sort_values("decision_ts").reset_index(drop=True)


def load_paper_reference_status() -> dict[str, Any]:
    return read_json(PAPER_REFERENCE_STATUS_PATH, {}) or {}


def filter_since(df: pd.DataFrame, ts_col: str, since_ts: pd.Timestamp | None) -> pd.DataFrame:
    if df.empty or since_ts is None or ts_col not in df.columns:
        return df.copy().reset_index(drop=True)
    work = df.copy()
    work[ts_col] = as_ts(work[ts_col])
    work = work[work[ts_col].isna() | (work[ts_col] >= since_ts)]
    return work.reset_index(drop=True)


def earliest_compare_ts(live_closed: pd.DataFrame, live_open: pd.DataFrame) -> pd.Timestamp | None:
    candidates: list[pd.Timestamp] = []
    if not live_closed.empty and "decision_ts" in live_closed.columns:
        vals = as_ts(live_closed["decision_ts"]).dropna()
        if not vals.empty:
            candidates.append(vals.min())
    if not live_open.empty and "decision_ts" in live_open.columns:
        vals = as_ts(live_open["decision_ts"]).dropna()
        if not vals.empty:
            candidates.append(vals.min())
    return min(candidates) if candidates else None


def build_match_table(live_closed: pd.DataFrame, live_open: pd.DataFrame, paper_closed: pd.DataFrame, paper_open: pd.DataFrame) -> pd.DataFrame:
    live_columns = ["basket_id", "decision_ts", "exit_ts", "leg_count", "basket_net_pnl", "basket_net_bps", "symbols", "status"]
    live_parts: list[pd.DataFrame] = []
    if not live_closed.empty:
        live_parts.append(live_closed[live_columns].copy())
    if not live_open.empty:
        open_df = live_open[["basket_id", "decision_ts", "planned_exit_ts", "leg_count", "basket_net_pnl", "symbols", "status"]].copy()
        open_df["exit_ts"] = open_df.get("planned_exit_ts")
        open_df["basket_net_bps"] = None
        live_parts.append(open_df[live_columns])
    if not live_parts:
        return pd.DataFrame(columns=["decision_ts", "basket_id", "status", "comparison_status", "paper_coverage", "live_net_pnl", "paper_pnl_usdt", "delta_vs_paper", "live_leg_count", "paper_net_bps", "live_symbols", "paper_longs", "paper_shorts"])
    nonempty_live_parts = [part.reindex(columns=live_columns) for part in live_parts if not part.empty]
    if not nonempty_live_parts:
        live_all = pd.DataFrame(columns=live_columns)
    else:
        live_records: list[dict[str, Any]] = []
        for part in nonempty_live_parts:
            live_records.extend(part.to_dict("records"))
        live_all = pd.DataFrame.from_records(live_records, columns=live_columns)
    live_all["decision_key"] = live_all["decision_ts"].map(lambda v: pd.to_datetime(v, utc=True, errors="coerce").isoformat() if not pd.isna(pd.to_datetime(v, utc=True, errors="coerce")) else "")

    paper_cols = [
        "decision_ts", "paper_pnl_usdt", "paper_net_bps", "longs", "shorts", "gate_on", "veto_count",
        "paper_price_ret", "paper_funding_ret", "paper_net_ret", "paper_turnover_x", "funding_events",
    ]
    paper_closed_work = paper_closed.copy()
    if paper_closed_work.empty:
        paper_closed_work = pd.DataFrame(columns=paper_cols)
    paper_closed_work["decision_key"] = paper_closed_work["decision_ts"].map(lambda v: pd.to_datetime(v, utc=True, errors="coerce").isoformat() if not pd.isna(pd.to_datetime(v, utc=True, errors="coerce")) else "")

    paper_open_work = paper_open.copy()
    if paper_open_work.empty:
        paper_open_work = pd.DataFrame(columns=paper_cols + ["mark_ts"])
    paper_open_work["decision_key"] = paper_open_work["decision_ts"].map(lambda v: pd.to_datetime(v, utc=True, errors="coerce").isoformat() if not pd.isna(pd.to_datetime(v, utc=True, errors="coerce")) else "")

    paper_closed_work = paper_closed_work.rename(columns={
        "paper_pnl_usdt": "paper_closed_pnl_usdt", "paper_net_bps": "paper_closed_net_bps", "longs": "paper_closed_longs", "shorts": "paper_closed_shorts",
        "gate_on": "paper_closed_gate_on", "veto_count": "paper_closed_veto_count", "paper_price_ret": "paper_closed_price_ret",
        "paper_funding_ret": "paper_closed_funding_ret", "paper_net_ret": "paper_closed_ret", "paper_turnover_x": "paper_closed_turnover_x", "funding_events": "paper_closed_funding_events",
    })
    paper_open_work = paper_open_work.rename(columns={
        "paper_pnl_usdt": "paper_open_pnl_usdt", "paper_net_bps": "paper_open_net_bps", "longs": "paper_open_longs", "shorts": "paper_open_shorts",
        "gate_on": "paper_open_gate_on", "veto_count": "paper_open_veto_count", "paper_price_ret": "paper_open_price_ret",
        "paper_funding_ret": "paper_open_funding_ret", "paper_net_ret": "paper_open_ret", "paper_turnover_x": "paper_open_turnover_x", "funding_events": "paper_open_funding_events",
    })

    merged = live_all.merge(
        paper_closed_work[["decision_key", "paper_closed_pnl_usdt", "paper_closed_net_bps", "paper_closed_longs", "paper_closed_shorts", "paper_closed_gate_on", "paper_closed_veto_count", "paper_closed_price_ret", "paper_closed_funding_ret", "paper_closed_ret", "paper_closed_turnover_x", "paper_closed_funding_events"]],
        on="decision_key",
        how="left",
    )
    merged = merged.merge(
        paper_open_work[["decision_key", "paper_open_pnl_usdt", "paper_open_net_bps", "paper_open_longs", "paper_open_shorts", "paper_open_gate_on", "paper_open_veto_count", "paper_open_price_ret", "paper_open_funding_ret", "paper_open_ret", "paper_open_turnover_x", "paper_open_funding_events", "mark_ts"]],
        on="decision_key",
        how="left",
    )
    is_open_live = merged.get("status").astype(str) == "open_mtm"
    merged["paper_pnl_usdt"] = safe_float(merged.get("paper_closed_pnl_usdt"))
    merged.loc[is_open_live, "paper_pnl_usdt"] = safe_float(merged.loc[is_open_live, "paper_open_pnl_usdt"])
    merged["paper_net_bps"] = safe_float(merged.get("paper_closed_net_bps"))
    merged.loc[is_open_live, "paper_net_bps"] = safe_float(merged.loc[is_open_live, "paper_open_net_bps"])
    merged["paper_longs"] = merged.get("paper_closed_longs")
    merged.loc[is_open_live, "paper_longs"] = merged.loc[is_open_live, "paper_open_longs"]
    merged["paper_shorts"] = merged.get("paper_closed_shorts")
    merged.loc[is_open_live, "paper_shorts"] = merged.loc[is_open_live, "paper_open_shorts"]
    paper_closed_gate = safe_bool_series(merged.get("paper_closed_gate_on"))
    paper_open_gate = safe_bool_series(merged.get("paper_open_gate_on"))
    merged["paper_gate_on"] = paper_closed_gate.where(~is_open_live, paper_open_gate)
    merged["paper_veto_count"] = safe_float(merged.get("paper_closed_veto_count"))
    merged.loc[is_open_live, "paper_veto_count"] = safe_float(merged.loc[is_open_live, "paper_open_veto_count"])
    merged["paper_price_ret"] = safe_float(merged.get("paper_closed_price_ret"))
    merged.loc[is_open_live, "paper_price_ret"] = safe_float(merged.loc[is_open_live, "paper_open_price_ret"])
    merged["paper_funding_ret"] = safe_float(merged.get("paper_closed_funding_ret"))
    merged.loc[is_open_live, "paper_funding_ret"] = safe_float(merged.loc[is_open_live, "paper_open_funding_ret"])
    merged["paper_net_ret"] = safe_float(merged.get("paper_closed_ret"))
    merged.loc[is_open_live, "paper_net_ret"] = safe_float(merged.loc[is_open_live, "paper_open_ret"])
    merged["paper_turnover_x"] = safe_float(merged.get("paper_closed_turnover_x"))
    merged.loc[is_open_live, "paper_turnover_x"] = safe_float(merged.loc[is_open_live, "paper_open_turnover_x"])
    merged["paper_funding_events"] = safe_float(merged.get("paper_closed_funding_events"))
    merged.loc[is_open_live, "paper_funding_events"] = safe_float(merged.loc[is_open_live, "paper_open_funding_events"])
    paper_pnl = safe_float(merged.get("paper_pnl_usdt"))
    merged["paper_coverage"] = paper_pnl.notna()
    merged["delta_vs_paper"] = safe_float(merged.get("basket_net_pnl")).fillna(0.0) - paper_pnl.fillna(0.0)
    merged.loc[~merged["paper_coverage"], "delta_vs_paper"] = None
    merged["delta_vs_paper_bps"] = (safe_float(merged.get("delta_vs_paper")) / BASKET_NOTIONAL_USDT) * 10000.0
    merged.loc[~merged["paper_coverage"], "delta_vs_paper_bps"] = None
    merged["live_leg_count"] = safe_float(merged.get("leg_count")).fillna(0).astype(int)
    merged["comparison_status"] = merged.apply(
        lambda row: (
            "missing_paper_reference"
            if not bool(row.get("paper_coverage"))
            else ("matched_open_snapshot" if str(row.get("status") or "") == "open_mtm" else "matched_closed")
        ),
        axis=1,
    )

    merged["live_symbols_list"] = merged.get("symbols").map(parse_symbol_text)
    merged["paper_longs_list"] = merged.get("paper_longs").map(parse_symbol_text)
    merged["paper_shorts_list"] = merged.get("paper_shorts").map(parse_symbol_text)
    merged["paper_all_symbols_list"] = merged.apply(lambda row: row["paper_longs_list"] + row["paper_shorts_list"], axis=1)
    merged["basket_exact_match"] = merged.apply(
        lambda row: bool(row.get("paper_coverage")) and format_symbol_list(set(row["live_symbols_list"])) == format_symbol_list(set(row["paper_all_symbols_list"])),
        axis=1,
    )
    merged["long_overlap_rate"] = merged.apply(lambda row: overlap_rate(row["live_symbols_list"], row["paper_longs_list"]), axis=1)
    merged["short_overlap_rate"] = merged.apply(lambda row: overlap_rate(row["live_symbols_list"], row["paper_shorts_list"]), axis=1)
    merged["live_only_symbols"] = merged.apply(lambda row: format_symbol_list(set(row["live_symbols_list"]) - set(row["paper_all_symbols_list"])), axis=1)
    merged["paper_only_symbols"] = merged.apply(lambda row: format_symbol_list(set(row["paper_all_symbols_list"]) - set(row["live_symbols_list"])), axis=1)
    merged["gate_match"] = safe_bool_series(merged.get("paper_gate_on"))
    merged["gate_mismatch"] = False
    merged["veto_count_match"] = True
    merged["veto_mismatch"] = False
    merged["mechanism_mismatch_class"] = merged.apply(
        lambda row: (
            "missing_paper_reference"
            if not bool(row.get("paper_coverage"))
            else ("open_snapshot_only" if str(row.get("status") or "") == "open_mtm"
            else ("exact_match" if bool(row.get("basket_exact_match")) else "basket_symbols_only"))
        ),
        axis=1,
    )
    def build_attribution_notes(row: pd.Series) -> str:
        notes: list[str] = []
        if str(row.get("status") or "") == "open_mtm":
            notes.append("open snapshot compare")
        if str(row.get("live_only_symbols") or ""):
            notes.append(f"live_only={row.get('live_only_symbols')}")
        if str(row.get("paper_only_symbols") or ""):
            notes.append(f"paper_only={row.get('paper_only_symbols')}")
        funding_events = float(row.get("paper_funding_events") or 0)
        if bool(row.get("paper_coverage")) and funding_events > 0:
            notes.append(f"paper_funding_events={int(funding_events)}")
        return "; ".join(notes)

    merged["attribution_notes"] = merged.apply(build_attribution_notes, axis=1)
    merged = merged.rename(columns={"basket_net_pnl": "live_net_pnl", "symbols": "live_symbols"})
    merged = merged[[
        "decision_ts", "basket_id", "status", "comparison_status", "paper_coverage", "live_net_pnl", "paper_pnl_usdt", "delta_vs_paper", "delta_vs_paper_bps",
        "live_leg_count", "paper_net_bps", "live_symbols", "paper_longs", "paper_shorts", "paper_gate_on", "paper_veto_count", "paper_price_ret",
        "paper_funding_ret", "paper_net_ret", "paper_turnover_x", "paper_funding_events", "basket_exact_match", "long_overlap_rate", "short_overlap_rate",
        "live_only_symbols", "paper_only_symbols", "gate_match", "gate_mismatch", "veto_count_match", "veto_mismatch", "mechanism_mismatch_class", "attribution_notes",
    ]]
    return merged.sort_values("decision_ts", ascending=False).reset_index(drop=True)


def build_matched_pnl_curves(match_table: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    empty = pd.DataFrame(columns=["ts", "pnl_usdt"])
    if match_table.empty or "paper_coverage" not in match_table.columns:
        return empty, empty, empty

    work = match_table[match_table["paper_coverage"].fillna(False)].copy()
    if work.empty:
        return empty, empty, empty

    work["ts"] = as_ts(work.get("decision_ts"))
    work["live_pnl_usdt"] = safe_float(work.get("live_net_pnl")).fillna(0.0)
    work["paper_pnl_usdt"] = safe_float(work.get("paper_pnl_usdt")).fillna(0.0)
    work = work[work["ts"].notna()].sort_values("ts").reset_index(drop=True)
    if work.empty:
        return empty, empty, empty

    live_curve = work[["ts", "live_pnl_usdt"]].copy().rename(columns={"live_pnl_usdt": "pnl_usdt"})
    live_curve["pnl_usdt"] = live_curve["pnl_usdt"].cumsum()

    paper_curve = work[["ts", "paper_pnl_usdt"]].copy().rename(columns={"paper_pnl_usdt": "pnl_usdt"})
    paper_curve["pnl_usdt"] = paper_curve["pnl_usdt"].cumsum()

    delta_curve = work[["ts"]].copy()
    delta_curve["pnl_usdt"] = (work["live_pnl_usdt"] - work["paper_pnl_usdt"]).cumsum()
    return live_curve, paper_curve, delta_curve


def build_compare_timeline(match_table: pd.DataFrame, drift_attribution: pd.DataFrame) -> pd.DataFrame:
    if match_table.empty:
        return pd.DataFrame(columns=["decision_ts", "decision_label", "timeline_status", "timeline_label", "delta_vs_paper", "status", "comparison_status", "mechanism_mismatch_class", "attribution_notes", "paper_coverage"])

    work = match_table.copy()
    drift_cols = [c for c in ["decision_ts", "composition_class", "fallback_taker_count", "residual_flatten_hit", "non_horizon_exit_leg_count"] if c in drift_attribution.columns]
    if drift_cols:
        work = work.merge(drift_attribution[drift_cols], on="decision_ts", how="left")

    def classify(row: pd.Series) -> str:
        if not bool(row.get("paper_coverage")):
            return "missing_coverage"
        if str(row.get("status") or "") == "open_mtm":
            return "open_snapshot"
        if str(row.get("mechanism_mismatch_class") or "") == "basket_symbols_only" or not bool(row.get("basket_exact_match")):
            return "symbol_mismatch"
        delta_bps = abs(float(safe_float(pd.Series([row.get("delta_vs_paper_bps")])).fillna(0.0).iloc[0]))
        if delta_bps >= 75.0 or bool(row.get("fallback_taker_count")) or bool(row.get("residual_flatten_hit")) or float(safe_float(pd.Series([row.get("non_horizon_exit_leg_count")])).fillna(0.0).iloc[0]) > 0:
            return "economic_drift"
        return "exact_match"

    label_map = {
        "exact_match": "exact match",
        "symbol_mismatch": "symbol mismatch",
        "economic_drift": "economic drift",
        "open_snapshot": "open snapshot",
        "missing_coverage": "missing coverage",
    }
    work["decision_ts"] = as_ts(work.get("decision_ts"))
    work = work[work["decision_ts"].notna()].sort_values("decision_ts", ascending=False).reset_index(drop=True)
    work["timeline_status"] = work.apply(classify, axis=1)
    work["timeline_label"] = work["timeline_status"].map(label_map)
    work["decision_label"] = work["decision_ts"].map(lambda v: pd.to_datetime(v, utc=True).strftime("%m-%d %H:%M"))
    keep = [
        "decision_ts", "decision_label", "timeline_status", "timeline_label", "delta_vs_paper", "status",
        "comparison_status", "mechanism_mismatch_class", "attribution_notes", "paper_coverage",
    ]
    return work[keep]


def build_order_lineage_table(live_orders: list[dict[str, Any]], basket_id: str | None) -> pd.DataFrame:
    if not basket_id:
        return pd.DataFrame(columns=["timestamp", "symbol", "order_role", "status", "price", "qty", "lineage"])
    rows = [row for row in live_orders if str(row.get("basket_id") or "") == basket_id]
    if not rows:
        return pd.DataFrame(columns=["timestamp", "symbol", "order_role", "status", "price", "qty", "lineage"])
    df = pd.DataFrame(rows).copy()
    df["timestamp"] = as_ts(df.get("timestamp"))
    keep = [c for c in ["timestamp", "symbol", "order_role", "status", "price", "qty", "lineage"] if c in df.columns]
    return df[keep].sort_values("timestamp", ascending=False).reset_index(drop=True)


def build_open_leg_table(open_legs: pd.DataFrame) -> pd.DataFrame:
    if open_legs.empty:
        return pd.DataFrame(columns=["symbol", "side", "basket_role", "entry_time", "planned_exit_ts", "unrealized_pnl", "submit_outcome", "fallback_reason"])
    df = open_legs.copy()
    keep = [c for c in ["symbol", "side", "basket_role", "entry_time", "planned_exit_ts", "unrealized_pnl", "submit_outcome", "fallback_reason"] if c in df.columns]
    return df[keep].sort_values(["basket_role", "symbol"]).reset_index(drop=True)


def parse_symbol_text(text: Any) -> list[str]:
    return [x.strip() for x in str(text or "").split(",") if x and x.strip()]


def format_symbol_list(values: set[str] | list[str]) -> str:
    if not values:
        return ""
    return ",".join(sorted({str(v) for v in values if str(v)}))


def overlap_rate(a: list[str], b: list[str]) -> float:
    sa = {str(v) for v in a if str(v)}
    sb = {str(v) for v in b if str(v)}
    denom = max(len(sa | sb), 1)
    return len(sa & sb) / denom


def safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def safe_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def join_symbols(symbols: list[str]) -> str:
    return ", ".join(sorted({str(s) for s in symbols if str(s)}))


def basket_id_from_decision_ts(decision_ts: Any) -> str | None:
    ts = pd.to_datetime(decision_ts, utc=True, errors="coerce")
    if pd.isna(ts):
        return None
    return f"rank213-{ts.strftime('%Y-%m-%dT%H:%M:%SZ')}"


def extract_basket_source(live_compare: dict[str, Any], basket_id: str | None) -> dict[str, Any]:
    if not basket_id:
        return {}
    tracked = safe_dict(live_compare.get("tracked_basket_outcome"))
    if str(tracked.get("basket_id") or "") == basket_id:
        return tracked
    current = safe_dict(live_compare.get("current_basket_parity"))
    if str(safe_dict(current.get("intended_basket")).get("basket_id") or "") == basket_id:
        return {"basket_id": basket_id, "basket_parity": current}
    basket_parity = safe_dict(live_compare.get("basket_parity"))
    if str(safe_dict(basket_parity.get("intended_basket")).get("basket_id") or "") == basket_id:
        return {"basket_id": basket_id, "basket_parity": basket_parity}
    return {}


def extract_residual_history_for_basket(live_status: dict[str, Any], basket_id: str | None) -> list[dict[str, Any]]:
    if not basket_id:
        return []
    hits: list[dict[str, Any]] = []
    for item in safe_list(live_status.get("residual_flatten_history")):
        source_positions = safe_list(safe_dict(item).get("source_positions"))
        matched = False
        for pos in source_positions:
            matched_ids = {str(v) for v in safe_list(safe_dict(pos).get("matched_basket_ids")) if str(v)}
            if basket_id in matched_ids:
                matched = True
                break
        if matched:
            hits.append(safe_dict(item))
    return hits


def mean_of_list(values: list[float]) -> float | None:
    vals = [float(v) for v in values if v is not None and not pd.isna(v)]
    return (sum(vals) / len(vals)) if vals else None


def build_drift_attribution(match_table: pd.DataFrame, live_compare: dict[str, Any], live_status: dict[str, Any]) -> tuple[pd.DataFrame, dict[str, Any]]:
    if match_table.empty:
        summary = {
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "matched_baskets": 0,
            "top_gap_baskets": [],
            "repeated_mechanism_mismatches": {},
            "operator_stance": {
                "recommended_stage": "audit_observation_only",
                "scale_recommendation": "hold_size_constant",
                "reasoning": [
                    "No matched baskets are available yet, so the honest next step is observation rather than scaling.",
                ],
            },
        }
        return pd.DataFrame(), summary

    matched = match_table[match_table.get("paper_coverage").fillna(False)].copy()
    if matched.empty:
        summary = {
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "matched_baskets": 0,
            "top_gap_baskets": [],
            "repeated_mechanism_mismatches": {},
            "operator_stance": {
                "recommended_stage": "audit_observation_only",
                "scale_recommendation": "hold_size_constant",
                "reasoning": [
                    "No matched live-vs-paper baskets are available in the current age90 artifact set.",
                    "This page still shows truthful live PnL, shadow timestamps, and archive/closeout status without fabricating paper parity.",
                ],
            },
        }
        return pd.DataFrame(), summary
    rows: list[dict[str, Any]] = []
    for _, row in matched.iterrows():
        basket_id = str(row.get("basket_id") or "") or basket_id_from_decision_ts(row.get("decision_ts")) or ""
        basket_source = extract_basket_source(live_compare, basket_id)
        basket_parity = safe_dict(basket_source.get("basket_parity"))
        intended = safe_dict(basket_parity.get("intended_basket"))
        submitted = safe_dict(basket_parity.get("submitted_basket"))
        realized = safe_dict(basket_parity.get("realized_basket"))
        basket_safety = safe_dict(basket_parity.get("basket_safety"))
        lifecycle = safe_list(realized.get("lifecycle"))

        paper_symbols = parse_symbol_text(row.get("paper_longs")) + parse_symbol_text(row.get("paper_shorts"))
        intended_symbols = [str(s) for s in safe_list(intended.get("long_symbols")) + safe_list(intended.get("short_symbols")) if str(s)]
        submitted_symbols = [str(s) for s in safe_list(submitted.get("symbols")) if str(s)]
        realized_symbols = [str(s) for s in safe_list(realized.get("closed_symbols")) + safe_list(realized.get("live_symbols")) if str(s)]
        live_symbols = parse_symbol_text(row.get("live_symbols"))
        compare_symbols = realized_symbols or live_symbols

        paper_set = set(paper_symbols)
        compare_set = set(compare_symbols)
        missing_vs_paper = sorted(paper_set - compare_set)
        extra_vs_paper = sorted(compare_set - paper_set)
        overlap_ratio = (len(paper_set & compare_set) / len(paper_set)) if paper_set else None

        safe_to_compare = bool(basket_safety.get("safe_to_compare_economics", True))
        submit_failed_count = int(submitted.get("legs_submit_failed") or 0)
        partial_submit_count = int(submitted.get("partial_submit_count") or 0)
        if not safe_to_compare:
            composition_class = "unsafe_to_compare"
        elif missing_vs_paper or extra_vs_paper:
            composition_class = "symbol_mismatch"
        elif submit_failed_count > 0 or partial_submit_count > 0:
            composition_class = "partial_submit"
        else:
            composition_class = "exact_match"

        entry_slippages = [safe_float(pd.Series([safe_dict(leg).get("entry_slippage_bps")])).iloc[0] for leg in lifecycle if safe_dict(leg).get("entry_slippage_bps") is not None]
        exit_deltas = [safe_float(pd.Series([safe_dict(leg).get("exit_policy_delta_bps")])).iloc[0] for leg in lifecycle if safe_dict(leg).get("exit_policy_delta_bps") is not None]
        exit_reasons = sorted({str(safe_dict(leg).get("exit_reason") or "") for leg in lifecycle if str(safe_dict(leg).get("exit_reason") or "")})
        non_horizon_exit_leg_count = sum(1 for leg in lifecycle if str(safe_dict(leg).get("exit_reason") or "") not in {"", "horizon_market_filled"})
        late_exit_leg_count = sum(1 for leg in lifecycle if abs(float(safe_float(pd.Series([safe_dict(leg).get("exit_policy_delta_bps")])).fillna(0.0).iloc[0])) >= 1.0)

        residual_hits = extract_residual_history_for_basket(live_status, basket_id)
        residual_symbols = sorted({str(sym) for hit in residual_hits for sym in safe_list(safe_dict(hit).get("symbols")) if str(sym)})

        delta_vs_paper = safe_float(pd.Series([row.get("delta_vs_paper")])).iloc[0]
        entry_mean = mean_of_list(entry_slippages)
        exit_mean = mean_of_list(exit_deltas)
        explained_abs_usdt = 0.0
        if entry_mean is not None:
            explained_abs_usdt += abs(entry_mean) / 10000.0 * BASKET_NOTIONAL_USDT
        if exit_mean is not None:
            explained_abs_usdt += abs(exit_mean) / 10000.0 * BASKET_NOTIONAL_USDT
        unexplained_gap_usdt = None if pd.isna(delta_vs_paper) else float(delta_vs_paper) - (float(explained_abs_usdt) if explained_abs_usdt else 0.0)

        rows.append({
            "decision_ts": row.get("decision_ts"),
            "basket_id": basket_id,
            "status": row.get("status"),
            "live_net_pnl": row.get("live_net_pnl"),
            "paper_pnl_usdt": row.get("paper_pnl_usdt"),
            "delta_vs_paper": delta_vs_paper,
            "delta_vs_paper_bps": row.get("delta_vs_paper_bps"),
            "mechanism_mismatch_class": row.get("mechanism_mismatch_class"),
            "attribution_notes": row.get("attribution_notes"),
            "composition_class": composition_class,
            "paper_symbol_count": len(paper_set),
            "intended_symbol_count": len(set(intended_symbols)) or None,
            "submitted_symbol_count": len(set(submitted_symbols)) or None,
            "realized_symbol_count": len(compare_set),
            "missing_symbols_vs_paper": join_symbols(missing_vs_paper),
            "extra_symbols_vs_paper": join_symbols(extra_vs_paper),
            "symbol_overlap_ratio": overlap_ratio,
            "maker_reject_count": int(submitted.get("maker_reject_count") or 0),
            "fallback_taker_count": int(submitted.get("fallback_taker_count") or 0),
            "submit_failed_count": submit_failed_count,
            "execution_regime": submitted.get("execution_regime"),
            "avg_entry_slippage_bps": entry_mean,
            "sum_entry_slippage_bps": sum(float(v) for v in entry_slippages) if entry_slippages else None,
            "execution_drift_flag": bool((submitted.get("maker_reject_count") or 0) or (submitted.get("fallback_taker_count") or 0) or submit_failed_count),
            "avg_exit_policy_delta_bps": exit_mean,
            "sum_exit_policy_delta_bps": sum(float(v) for v in exit_deltas) if exit_deltas else None,
            "late_exit_leg_count": late_exit_leg_count,
            "non_horizon_exit_leg_count": non_horizon_exit_leg_count,
            "exit_reason_set": ", ".join(exit_reasons),
            "exit_drift_flag": bool(late_exit_leg_count or non_horizon_exit_leg_count),
            "residual_flatten_hit": bool(residual_hits),
            "residual_flatten_count": len(residual_hits),
            "residual_symbols": join_symbols(residual_symbols),
            "accounting_drift_flag": bool(residual_hits),
            "unexplained_gap_usdt": unexplained_gap_usdt,
            "safe_to_compare_economics": safe_to_compare,
            "paper_gate_on": row.get("paper_gate_on"),
            "paper_veto_count": row.get("paper_veto_count"),
            "paper_price_ret": row.get("paper_price_ret"),
            "paper_funding_ret": row.get("paper_funding_ret"),
            "paper_net_ret": row.get("paper_net_ret"),
            "paper_turnover_x": row.get("paper_turnover_x"),
            "paper_funding_events": row.get("paper_funding_events"),
        })

    attribution = pd.DataFrame(rows).sort_values("decision_ts", ascending=False).reset_index(drop=True)
    if attribution.empty:
        return attribution, {
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "matched_baskets": 0,
            "top_gap_baskets": [],
            "repeated_mechanism_mismatches": {},
            "operator_stance": {
                "recommended_stage": "audit_observation_only",
                "scale_recommendation": "hold_size_constant",
                "reasoning": ["No attribution rows were built."],
            },
        }

    work = attribution.copy()
    work["abs_gap_usdt"] = safe_float(work.get("delta_vs_paper")).abs()
    top_gap_cols = [
        "decision_ts", "basket_id", "status", "delta_vs_paper", "composition_class", "fallback_taker_count",
        "submit_failed_count", "avg_entry_slippage_bps", "avg_exit_policy_delta_bps", "residual_flatten_hit",
    ]
    top_gap = work.sort_values("abs_gap_usdt", ascending=False).head(5)[top_gap_cols].copy()

    repeated: dict[str, Any] = {}
    buckets = {
        "fallback_taker_baskets": work[safe_float(work.get("fallback_taker_count")).fillna(0) > 0],
        "partial_submit_baskets": work[work.get("composition_class").astype(str) == "partial_submit"],
        "symbol_mismatch_baskets": work[(work.get("mechanism_mismatch_class").astype(str) == "basket_symbols_only") | (work.get("composition_class").astype(str) == "symbol_mismatch")],
        "open_snapshot_baskets": work[work.get("mechanism_mismatch_class").astype(str) == "open_snapshot_only"],
        "non_horizon_exit_baskets": work[safe_float(work.get("non_horizon_exit_leg_count")).fillna(0) > 0],
        "residual_affected_baskets": work[work.get("residual_flatten_hit").fillna(False)],
    }
    for key, df in buckets.items():
        repeated[key] = {
            "count": int(len(df)),
            "affected_decision_ts": [pd.to_datetime(v, utc=True).strftime("%Y-%m-%dT%H:%M:%SZ") for v in df.get("decision_ts", pd.Series(dtype=object)).dropna().tolist()],
            "total_gap_usdt": float(safe_float(df.get("delta_vs_paper")).fillna(0.0).sum()) if not df.empty else 0.0,
            "mean_gap_usdt": float(safe_float(df.get("delta_vs_paper")).fillna(0.0).mean()) if not df.empty else 0.0,
        }

    operator_stance = {
        "recommended_stage": "audit_observation_only",
        "scale_recommendation": "hold_size_constant",
        "reasoning": [
            "Paper coverage is now full_compare, so the honest next step is to explain drift rather than scale size.",
            "Matched baskets still show non-trivial live-vs-paper gap, so execution and basket-level mismatches should be audited before increasing notional.",
            "There is still no independent live funding ledger or full account NAV history, so unresolved accounting drift should remain visible instead of being waved away.",
        ],
    }

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "matched_baskets": int(len(attribution)),
        "top_gap_baskets": [] if top_gap.empty else json.loads(top_gap.to_json(orient="records", date_format="iso")),
        "repeated_mechanism_mismatches": repeated,
        "operator_stance": operator_stance,
    }
    return attribution, summary


def build_repeated_mismatch_table(repeated: dict[str, Any]) -> pd.DataFrame:
    if not repeated:
        return pd.DataFrame(columns=["mechanism", "count", "total_gap_usdt", "mean_gap_usdt", "affected_decision_ts"])
    label_map = {
        "fallback_taker_baskets": "fallback taker baskets",
        "partial_submit_baskets": "partial submit baskets",
        "symbol_mismatch_baskets": "symbol mismatch baskets",
        "non_horizon_exit_baskets": "non-horizon exit baskets",
        "residual_affected_baskets": "residual affected baskets",
    }
    rows: list[dict[str, Any]] = []
    for key, item in repeated.items():
        data = safe_dict(item)
        rows.append({
            "mechanism": label_map.get(key, key),
            "count": data.get("count"),
            "total_gap_usdt": data.get("total_gap_usdt"),
            "mean_gap_usdt": data.get("mean_gap_usdt"),
            "affected_decision_ts": ", ".join(str(v) for v in safe_list(data.get("affected_decision_ts"))),
        })
    return pd.DataFrame(rows).sort_values(["count", "total_gap_usdt"], ascending=[False, False]).reset_index(drop=True)


def render_artifact_links() -> str:
    links = [
        ("live_state.json", LIVE_STATE_PATH),
        ("live_exchange_positions.json", LIVE_POSITIONS_PATH),
        ("live_recent_orders.json", LIVE_ORDERS_PATH),
        ("live_vs_shadow_summary.json", LIVE_COMPARE_PATH),
        ("live_status.json", LIVE_STATUS_PATH),
        ("rank213_age90_shadow_current_decision.json", SHADOW_DECISION_PATH),
        ("rank213_age90_shadow_status.json", SHADOW_STATUS_PATH),
        ("live_vs_backtest_drift_attribution.csv", DRIFT_ATTRIBUTION_PATH),
        ("live_vs_backtest_drift_summary.json", DRIFT_SUMMARY_PATH),
        ("live_vs_backtest_checklist.json", OUT_JSON),
        ("rank213_archive_closeout_receipt.json", CLOSEOUT_RECEIPT_PATH),
    ]
    optional_links = [
        ("rank213_age90_paper_reference_closed.csv", PAPER_REFERENCE_CLOSED_PATH),
        ("rank213_age90_paper_reference_open.csv", PAPER_REFERENCE_OPEN_PATH),
        ("rank213_age90_paper_reference_status.json", PAPER_REFERENCE_STATUS_PATH),
        ("rank213_age90_paper_reference_curve.csv", PAPER_REFERENCE_CURVE_PATH),
    ]
    items = []
    for label, path in links:
        if not path.exists():
            continue
        rel = path.relative_to(ROOT / "reports")
        href = "../../../" + str(rel).replace("\\", "/")
        items.append(f"<li><a href='{escape(href)}'>{escape(label)}</a></li>")
    for label, path in optional_links:
        if not path.exists():
            continue
        rel = path.relative_to(ROOT / "reports")
        href = "../../../" + str(rel).replace("\\", "/")
        items.append(f"<li><a href='{escape(href)}'>{escape(label)}</a></li>")
    return "<ul>" + "".join(items) + "</ul>"


def render_html(payload: dict[str, Any]) -> str:
    metrics = payload["metrics"]
    closeout_receipt = payload.get("closeout_receipt", {}) or {}
    drift_summary = payload.get("drift_summary", {}) or {}
    operator_stance = drift_summary.get("operator_stance", {}) if isinstance(drift_summary, dict) else {}
    repeated = drift_summary.get("repeated_mechanism_mismatches", {}) if isinstance(drift_summary, dict) else {}
    final_realized_curve_svg = line_chart_svg([
        payload.get("final_realized_curve_series"),
    ])
    curve_svg = line_chart_svg([
        payload.get("matched_live_pnl_curve_series"),
        payload.get("matched_paper_pnl_curve_series"),
        payload.get("matched_delta_curve_series"),
    ])
    timeline_svg = timeline_band_svg(payload.get("compare_timeline_band", pd.DataFrame()))
    delta_svg = bar_chart_svg(payload.get("compare_timeline_bar", pd.DataFrame()), "delta_vs_paper", "decision_label")
    matched_table = table_html(payload.get("match_table_display", pd.DataFrame()))
    timeline_table = table_html(payload.get("compare_timeline_display", pd.DataFrame()))
    drift_top_table = table_html(payload.get("drift_top_display", pd.DataFrame()))
    drift_repeat_table = table_html(payload.get("drift_repeat_display", pd.DataFrame()))
    drift_detail_table = table_html(payload.get("drift_detail_display", pd.DataFrame()))
    open_legs_table = table_html(payload.get("open_legs_display", pd.DataFrame()))
    lineage_table = table_html(payload.get("order_lineage_display", pd.DataFrame()))
    artifact_links = render_artifact_links()
    highlights = payload.get("highlights", [])
    limitations = payload.get("limitations", [])
    highlights_html = "<ul>" + "".join(f"<li>{escape(str(item))}</li>" for item in highlights) + "</ul>"
    limitations_html = "<ul>" + "".join(f"<li>{escape(str(item))}</li>" for item in limitations) + "</ul>"
    operator_reasoning = "<ul>" + "".join(f"<li>{escape(str(item))}</li>" for item in safe_list(operator_stance.get("reasoning"))) + "</ul>"
    closeout_link = "../paper/rank213_archive_closeout.html"
    if closeout_receipt:
        archive_notice_html = (
            "<div class='panel archive-note archive-stop'>"
            "<h2>Archive Status</h2>"
            f"<p><b>rank213 age90 live canary 已进入收口。</b> "
            f"平仓回执时间：{escape(fmt_ts(closeout_receipt.get('flatten_submitted_at_utc')))}；"
            f"策略停止时间：{escape(fmt_ts(closeout_receipt.get('timers_disabled_at_utc')))}。</p>"
            f"<p class='muted'>pre-close snapshot total={escape(money((closeout_receipt.get('pre_close_metrics') or {}).get('snapshot_total_pnl')))} · "
            f"remaining positions after flatten={escape(str(closeout_receipt.get('remaining_position_count_after_flatten') or 0))} · "
            f"timers stopped={escape(str(closeout_receipt.get('timers_disable_status') or '-'))}。</p>"
            f"<p><a href='{closeout_link}'>查看 rank213 收口报告</a></p>"
            "</div>"
        )
    elif metrics.get("sustained_loss_verdict"):
        archive_notice_html = (
            "<div class='panel archive-note archive-warn'>"
            "<h2>Loss Alert</h2>"
            f"<p><b>当前已满足持续亏损告警。</b> "
            f"closed baskets={int(metrics.get('live_closed_baskets', 0))}，"
            f"loss baskets={int(metrics.get('loss_basket_count', 0))}，"
            f"last3 all negative={escape(str(bool(metrics.get('last3_all_negative'))))}，"
            f"last5 all negative={escape(str(bool(metrics.get('last5_all_negative'))))}。</p>"
            "<p class='muted'>若已执行收口，这里会显示 flatten / stop receipt；否则这页会继续保留当前实盘快照以便审计。</p>"
            "</div>"
        )
    else:
        archive_notice_html = ""
    final_curve_title = "Final realized PnL to stop time" if closeout_receipt else "Live realized PnL curve"
    final_curve_desc = (
        "这条蓝线展示从第一笔 closed basket 到最后一次 stop-time flatten 的累计已实现盈亏。最后一个点已经把 2026-05-13 的 6 条真实平仓成交并入，不再停留在 flatten 前的 open MTM snapshot。"
        if closeout_receipt
        else "这条蓝线展示当前 artifacts 中可见的累计已实现盈亏。"
    )
    cards = "".join(
        [
            metric_card("strategy state", escape(str(metrics.get("strategy_state") or "-")), f"sustained_loss={escape(str(bool(metrics.get('sustained_loss_verdict'))))} · closeout_receipt={escape(str(bool(closeout_receipt)))}"),
            metric_card("closed basket W/L", f"{int(metrics.get('win_basket_count', 0))}/{int(metrics.get('loss_basket_count', 0))}", f"mean basket pnl={money(metrics.get('mean_basket_pnl'))}"),
            metric_card("loss streak", escape(str(metrics.get("loss_streak_label") or "-")), f"last3 all negative={escape(str(bool(metrics.get('last3_all_negative'))))} · last5 all negative={escape(str(bool(metrics.get('last5_all_negative'))))}"),
            metric_card("compare start", fmt_ts(metrics.get("compare_start_ts")), "从第一笔 live basket 决策开始建立近端对照窗口。"),
            metric_card("final realized pnl", money(metrics.get("live_realized_pnl")), f"closed baskets={int(metrics.get('live_closed_baskets', 0))} · estimated fees={money(metrics.get('live_realized_fee'))}"),
            metric_card("pre-close snapshot", money(metrics.get("pre_close_snapshot_total")), f"pre-close realized={money(metrics.get('pre_close_realized_pnl'))} · open mtm={money(metrics.get('pre_close_open_mtm'))}"),
            metric_card("closeout basket", money(metrics.get("terminal_closeout_net_pnl")), f"legs={int(metrics.get('terminal_closeout_leg_count') or 0)} · fees={money(metrics.get('terminal_closeout_fee'))}"),
            metric_card("paper reference pnl", money(metrics.get("paper_reference_pnl")), (f"matched only · closed matches={int(metrics.get('paper_closed_matches', 0))} · open matches={int(metrics.get('paper_open_matches', 0))}" if metrics.get("paper_reference_ready") else "paper compare window missing / stale")),
            metric_card("live minus paper", money(metrics.get("live_vs_paper_gap")), (f"matched live={money(metrics.get('live_matched_pnl'))} · coverage={escape(str(metrics.get('paper_coverage_status') or '-'))}" if metrics.get("paper_reference_ready") else "delta hidden until paper coverage exists")),
            metric_card("matched compare basis", escape(str(metrics.get("paper_coverage_status") or "-")), f"closed={int(metrics.get('paper_closed_matches', 0))}/{int(metrics.get('live_closed_baskets', 0))} · open={int(metrics.get('paper_open_matches', 0))}/{int(metrics.get('live_open_baskets', 0))} · latest decision={escape(fmt_ts(metrics.get('paper_latest_decision_ts')))} · latest mark={escape(fmt_ts(metrics.get('paper_latest_mark_ts')))}"),
            metric_card("current shadow bar", escape(str(metrics.get("latest_shadow_bar_key") or "-")), f"gate_on={metrics.get('shadow_gate_on')} · latest shadow={escape(fmt_ts(metrics.get('latest_shadow_decision_ts')))}"),
            metric_card("last live refresh", fmt_ts(metrics.get("last_run_utc")), f"snapshot={escape(str(metrics.get('live_snapshot_status') or '-'))} · age={num(metrics.get('last_live_refresh_age_minutes'), 1)} min · tracked regime={escape(str(metrics.get('tracked_execution_regime') or '-'))}"),
            metric_card("true NAV coverage", "No", "主图已切到 matched basket pnl compare；但当前仍无账户级 equity history、无独立 live funding ledger。"),
        ]
    )
    drift_cards = "".join(
        [
            metric_card("matched baskets", str(int(drift_summary.get("matched_baskets") or 0)), "exact decision_ts join 后可做 honest attribution 的 live baskets。"),
            metric_card("top abs gap", money(metrics.get("top_gap_abs_usdt")), f"basket={escape(str(metrics.get('top_gap_basket_id') or '-'))}"),
            metric_card("fallback baskets", str(int(metrics.get("fallback_affected_baskets") or 0)), "maker reject / taker fallback 重复出现的篮子数。"),
            metric_card("composition mismatch", str(int(metrics.get("composition_mismatch_baskets") or 0)), "live 实际篮子与 paper target 不完全同腿。"),
            metric_card("residual affected", str(int(metrics.get("residual_affected_baskets") or 0)), "出现 residual flatten / reconciliation 痕迹的篮子数。"),
            metric_card("recommended stage", escape(str(operator_stance.get("recommended_stage") or "-")), f"scale={escape(str(operator_stance.get('scale_recommendation') or '-'))}"),
        ]
    )
    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>rank213 live pnl vs paper reference</title>
  <style>
    body {{ font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; background: #0b1220; color: #e5e7eb; }}
    .wrap {{ max-width: 1500px; margin: 0 auto; padding: 32px 20px 72px; }}
    .hero, .panel, .metric {{ background: #111827; border: 1px solid #1f2937; border-radius: 16px; }}
    .hero {{ padding: 22px; background: linear-gradient(180deg, #111827 0%, #0f172a 100%); }}
    .panel {{ padding: 18px; margin-top: 18px; }}
    .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-top: 16px; }}
    .metric {{ padding: 16px; }}
    .viz-grid {{ display: grid; grid-template-columns: 1.35fr 1fr; gap: 14px; margin-top: 16px; }}
    .dual-grid {{ display: grid; grid-template-columns: 1.2fr 1fr; gap: 16px; margin-top: 16px; }}
    .triple-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 14px; margin-top: 16px; }}
    h1, h2, h3 {{ margin: 0 0 12px; }}
    p, li {{ line-height: 1.65; }}
    .k {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: .05em; }}
    .v {{ margin-top: 10px; font-size: 22px; font-weight: 800; }}
    .s {{ margin-top: 10px; color: #cbd5e1; font-size: 13px; line-height: 1.6; }}
    .muted {{ color: #94a3b8; }}
    .pill {{ display: inline-flex; padding: 6px 10px; border-radius: 999px; background: rgba(96,165,250,.14); color: #bfdbfe; border: 1px solid rgba(96,165,250,.25); font-size: 12px; }}
    .archive-note {{ margin-bottom: 18px; }}
    .archive-stop {{ border-color: rgba(248,113,113,.35); background: rgba(127,29,29,.16); }}
    .archive-warn {{ border-color: rgba(245,158,11,.35); background: rgba(120,53,15,.16); }}
    table {{ width: 100%; border-collapse: collapse; border: 1px solid #1f2937; border-radius: 14px; overflow: hidden; background: #111827; }}
    th, td {{ text-align: left; vertical-align: top; padding: 12px; border-bottom: 1px solid #1f2937; font-size: 13px; line-height: 1.6; }}
    th {{ background: #0f172a; color: #cbd5e1; }}
    tr:last-child td {{ border-bottom: none; }}
    tr.pos td {{ color: #86efac; }}
    tr.neg td {{ color: #fca5a5; }}
    tr.flat td {{ color: #cbd5e1; }}
    .empty {{ color: #94a3b8; padding: 12px 0; }}
    a {{ color: #60a5fa; }}
    code {{ background: #0f172a; color: #cbd5e1; padding: 2px 6px; border-radius: 6px; }}
    @media (max-width: 980px) {{ .viz-grid, .dual-grid {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <div class='wrap'>
    <p class='muted'>Generated: {escape(fmt_ts(payload.get('generated_at_utc')))}</p>
    {archive_notice_html}
    <div class='hero'>
      <h1>rank213 age90 live pnl transparency</h1>
      <p>这页主图现在展示的是 <b>matched basket PnL compare</b>：只用 exact matched baskets 的 <code>live_net_pnl</code> 与 <code>paper_pnl_usdt</code> 做累计对比，直接回答 <b>实盘盈亏和 paper 盈亏是否保持一致</b>。</p>
      <p class='muted'>主图不再混用 sparse live realized path、单个当前 MTM snapshot、以及 continuous paper reference curve；统一改成按 <code>decision_ts</code> 对齐的 matched basket cumulative PnL basis。</p>
      <p class='muted'>这仍然不是真实账户 NAV history：当前没有历史 equity curve，也没有独立 live funding ledger。若最新一篮仍是 <code>open_mtm</code>，最后一点本质上仍是 snapshot compare，而不是完整 path replay。</p>
      <p class='muted'>当前 paper reference 仅来自历史 15m K 线 + funding + rank213 as-of/formal-gate 语义重建；它不读取 live trades、live signals、live orders 或任何 live execution artifacts。</p>
    </div>

    <div class='metric-grid'>{cards}</div>

    <div class='panel'>
      <h2>{escape(final_curve_title)}</h2>
      <p class='muted'>{escape(final_curve_desc)}</p>
      {final_realized_curve_svg}
    </div>

    <div class='viz-grid'>
      <div class='panel'>
        <h2>Matched live vs paper cumulative PnL</h2>
        <p class='muted'>深蓝 = matched live cumulative pnl；绿色 = matched paper cumulative pnl；红色 = cumulative live-minus-paper delta。三条线都只来自 <code>paper_coverage=true</code> 的 exact matched baskets，并统一使用 <code>decision_ts</code> 作为 x 轴。若最后一笔是 <code>open_mtm</code>，其经济含义仍是 open snapshot compare，不是账户级真实 NAV 曲线。</p>
        {curve_svg}
      </div>
      <div class='panel'>
        <h2>Match / mismatch timeline</h2>
        <p class='muted'>这条时间带直接回答过去一段时间里哪些 decision timestamps 是 exact match，哪些是 symbol mismatch、economic drift、open snapshot 或 missing coverage。先看这里的颜色分布，再回头看上面的 cumulative 曲线，就能判断偏离是零星事件还是连续一段时间在扩大。</p>
        {timeline_svg}
      </div>
    </div>

    <div class='dual-grid'>
      <div class='panel'>
        <h2>Basket delta vs paper over time</h2>
        <p class='muted'>每根柱子对应一笔 decision timestamp 的 <code>delta_vs_paper</code>。时间带回答“什么时候 match / mismatch”，这张图回答“那次偏离到底有多大”。</p>
        {delta_svg}
      </div>
      <div class='panel'>
        <h2>Recent compare timeline</h2>
        <p class='muted'>按时间顺序列出最近一段时间的 compare 状态，方便把颜色带和具体机制一一对应起来。</p>
        {timeline_table}
      </div>
    </div>

    <div class='triple-grid'>
      <div class='panel'>
        <h3>What this page can answer</h3>
        {highlights_html}
      </div>
      <div class='panel'>
        <h3>What this page is not</h3>
        {limitations_html}
      </div>
      <div class='panel'>
        <h3>Method</h3>
        <ul>
          <li>主图直接来自 <code>build_match_table(...)</code> 的 matched rows，而不是 mixed-frequency 的 realized curve / MTM marker / continuous paper path 拼接。</li>
          <li>只有 <code>paper_coverage=true</code> 的 exact matched baskets 会进入主图；每个点都使用同一个 <code>decision_ts</code>。</li>
          <li>live 主线累计的是 matched baskets 的 <code>live_net_pnl</code>；paper 主线累计的是同篮 <code>paper_pnl_usdt</code>；delta 线累计的是 <code>live - paper</code>。</li>
          <li>时间带视图同样按 <code>decision_ts</code> 展开，并把每一篮压缩成 <code>exact_match / symbol_mismatch / economic_drift / open_snapshot / missing_coverage</code> 五类状态。</li>
          <li>若 matched row 的 <code>status=open_mtm</code>，该点仍然只是 open snapshot compare，不是 closed realized replay。</li>
          <li>逐篮对照表仍按 <code>live decision_ts == paper decision_ts</code> 的 exact timestamp join 口径工作；若无覆盖，则明确显示 coverage 缺失而不是伪造对照。</li>
        </ul>
      </div>
    </div>

    <div class='panel'>
      <h2>Drift attribution summary</h2>
      <p class='muted'>这一层不是伪装成精确 NAV 拆账，而是基于当前可观测 runtime/parity 字段，诚实回答 gap 主要来自哪几类机制、哪些是重复出现的问题，以及当前为什么仍应停留在小额观察阶段。</p>
      <div class='metric-grid'>{drift_cards}</div>
    </div>

    <div class='dual-grid'>
      <div class='panel'>
        <h2>Top gap baskets</h2>
        <p class='muted'>优先看绝对 gap 最大的几笔，同时附 composition / fallback / exit / residual 标签，避免只盯总 gap 却不知道 gap 来自哪里。</p>
        {drift_top_table}
      </div>
      <div class='panel'>
        <h2>Repeated mechanism mismatches</h2>
        <p class='muted'>这里汇总真正重复出现的机制差，而不是单次偶然盈亏。应该优先修复这些反复出现的 drift 源。</p>
        {drift_repeat_table}
      </div>
    </div>

    <div class='panel'>
      <h2>Operator stance</h2>
      <p class='muted'>这是展示层 recommendation，不会修改任何 live execution config，也不会自动调大仓位。</p>
      <p><span class='pill'>{escape(str(operator_stance.get('recommended_stage') or '-'))}</span> <span class='pill'>{escape(str(operator_stance.get('scale_recommendation') or '-'))}</span></p>
      {operator_reasoning}
    </div>

    <div class='panel'>
      <h2>Drift attribution detail</h2>
      <p class='muted'>逐篮展开 composition / execution / exit / residual 归因字段。没有独立 funding ledger 或无法精确拆到腿的部分，会保留在 unexplained bucket，而不是硬凑解释。</p>
      {drift_detail_table}
    </div>

    <div class='dual-grid'>
      <div class='panel'>
        <h2>Recent basket comparison</h2>
        <p class='muted'>上表把 recent live baskets 分成 matched closed / matched open snapshot / missing paper reference 三类，直接回答每一篮当前到底是否可比、差值是多少、缺的又是什么。</p>
        {matched_table}
      </div>
      <div class='panel'>
        <h2>Current open basket legs</h2>
        <p class='muted'>这里直接展示当前 rank213 实盘 open legs 的 MTM、planned exit、以及 maker/fallback 语义。</p>
        {open_legs_table}
      </div>
    </div>

    <div class='panel'>
      <h2>Current active basket order lineage</h2>
      <p class='muted'>用最近 order history 直接解释当前活跃篮子从 intended → submitted / rejected_post_only / entry_fallback / filled 的执行轨迹。</p>
      {lineage_table}
    </div>

    <div class='panel'>
      <h2>Artifacts</h2>
      <p class='muted'>这页直接消费的核心输入与输出如下。</p>
      {artifact_links}
    </div>
  </div>
</body>
</html>
"""


def main() -> int:
    ensure_dir(LIVE_ART_DIR)
    ensure_dir(SITE_DIR)

    live_state = read_json(LIVE_STATE_PATH, {}) or {}
    live_status = read_json(LIVE_STATUS_PATH, {}) or {}
    live_compare = read_json(LIVE_COMPARE_PATH, {}) or {}
    live_positions = read_json(LIVE_POSITIONS_PATH, []) or []
    live_orders = read_json(LIVE_ORDERS_PATH, []) or []
    shadow_decision = read_json(SHADOW_DECISION_PATH, {}) or {}
    shadow_status = read_json(SHADOW_STATUS_PATH, {}) or {}
    closeout_receipt = read_json(CLOSEOUT_RECEIPT_PATH, {}) or {}
    closeout_executed = bool(closeout_receipt) and str(closeout_receipt.get("mode") or "") == "execute"

    live_closed = load_live_closed_baskets(live_state)
    orphan_closed_adjustment_df = load_live_orphan_closed_adjustment(live_state)
    open_legs = load_live_open_legs(live_positions)
    live_open = load_live_open_baskets(open_legs)
    paper_closed = load_paper_closed_reference()
    paper_open = load_paper_open_reference()
    paper_status = load_paper_reference_status()
    exec_cfg = safe_dict(load_yaml(ROOT / "config" / "execution" / "rank213_age90_live_canary.yaml").get("execution"))
    closeout_basket_df, closeout_leg_df, closeout_curve_summary = build_closeout_basket_df(
        live_state=live_state,
        closeout_receipt=closeout_receipt,
        exec_cfg=exec_cfg if isinstance(exec_cfg, dict) else {},
    )

    compare_start = earliest_compare_ts(live_closed, live_open)
    live_closed = filter_since(live_closed, "decision_ts", compare_start)
    live_open = filter_since(live_open, "decision_ts", compare_start)
    open_legs = filter_since(open_legs, "decision_ts", compare_start)
    closeout_basket_df = filter_since(closeout_basket_df, "decision_ts", compare_start)
    orphan_closed_adjustment_df = filter_since(orphan_closed_adjustment_df, "decision_ts", compare_start)
    paper_closed = filter_since(paper_closed, "decision_ts", compare_start)
    paper_open = filter_since(paper_open, "decision_ts", compare_start)
    if not orphan_closed_adjustment_df.empty:
        live_closed = pd.concat([live_closed, orphan_closed_adjustment_df], ignore_index=True).sort_values("decision_ts").reset_index(drop=True)
    if closeout_executed and int(closeout_receipt.get("remaining_position_count_after_flatten") or 0) == 0 and not closeout_basket_df.empty:
        live_closed = pd.concat([live_closed, closeout_basket_df], ignore_index=True).sort_values("decision_ts").reset_index(drop=True)
        live_open = pd.DataFrame(columns=live_open.columns)
        open_legs = pd.DataFrame(columns=open_legs.columns)

    match_table = build_match_table(live_closed, live_open, paper_closed, paper_open)
    drift_attribution, drift_summary = build_drift_attribution(match_table, live_compare, live_status)
    repeated = drift_summary.get("repeated_mechanism_mismatches", {}) if isinstance(drift_summary, dict) else {}
    top_gap_rows = safe_list(drift_summary.get("top_gap_baskets")) if isinstance(drift_summary, dict) else []
    top_gap_first = safe_dict(top_gap_rows[0]) if top_gap_rows else {}
    matched_live_curve_df, matched_paper_curve_df, matched_delta_curve_df = build_matched_pnl_curves(match_table)
    realized_curve_df = pd.DataFrame(columns=["ts", "basket_net_pnl"])
    if not live_closed.empty:
        realized_curve_df = live_closed[["exit_ts", "basket_net_pnl", "basket_id", "status"]].copy()
        realized_curve_df["ts"] = as_ts(realized_curve_df["exit_ts"])
        realized_curve_df["basket_net_pnl"] = safe_float(realized_curve_df["basket_net_pnl"]).fillna(0.0)
        realized_curve_df = realized_curve_df[realized_curve_df["ts"].notna()].sort_values("ts").reset_index(drop=True)

    active_basket_id = None
    if closeout_executed and not closeout_basket_df.empty:
        active_basket_id = str(closeout_basket_df.sort_values("decision_ts").iloc[-1]["basket_id"])
    elif not live_open.empty:
        live_open_with_ts = live_open[live_open["decision_ts"].notna()] if "decision_ts" in live_open.columns else pd.DataFrame()
        active_source = live_open_with_ts if not live_open_with_ts.empty else live_open
        active_basket_id = str(active_source.sort_values("decision_ts", na_position="first").iloc[-1]["basket_id"])
    elif isinstance(live_state.get("current_basket"), dict):
        active_basket_id = str(live_state.get("current_basket", {}).get("basket_id") or "") or None

    order_lineage = build_order_lineage_table(live_orders, active_basket_id)
    open_legs_display = build_open_leg_table(open_legs)
    if closeout_executed and int(closeout_receipt.get("remaining_position_count_after_flatten") or 0) == 0:
        open_legs_display = pd.DataFrame(columns=["symbol", "side", "basket_role", "entry_time", "planned_exit_ts", "unrealized_pnl", "submit_outcome", "fallback_reason"])

    compare_timeline = build_compare_timeline(match_table, drift_attribution)

    compare_timeline_bar = compare_timeline.copy().sort_values("decision_ts").reset_index(drop=True) if not compare_timeline.empty else pd.DataFrame()
    compare_timeline_display = compare_timeline.copy().head(16)
    if not compare_timeline_display.empty:
        compare_timeline_display = compare_timeline_display[[
            "decision_ts",
            "timeline_label",
            "delta_vs_paper",
            "status",
            "comparison_status",
            "mechanism_mismatch_class",
            "attribution_notes",
        ]]

    match_display = match_table.copy().head(12)
    if not match_display.empty:
        match_display = match_display[[
            "decision_ts",
            "basket_id",
            "status",
            "comparison_status",
            "paper_coverage",
            "live_net_pnl",
            "paper_pnl_usdt",
            "delta_vs_paper",
            "delta_vs_paper_bps",
            "mechanism_mismatch_class",
            "live_leg_count",
            "paper_net_bps",
            "paper_price_ret",
            "paper_funding_ret",
            "paper_turnover_x",
            "paper_funding_events",
            "live_symbols",
            "paper_longs",
            "paper_shorts",
            "attribution_notes",
        ]]

    drift_top_display = drift_attribution.copy().sort_values("delta_vs_paper", key=lambda s: safe_float(s).abs(), ascending=False).head(5) if not drift_attribution.empty else pd.DataFrame()
    if not drift_top_display.empty:
        drift_top_display = drift_top_display[[
            "decision_ts",
            "basket_id",
            "status",
            "delta_vs_paper",
            "delta_vs_paper_bps",
            "mechanism_mismatch_class",
            "composition_class",
            "paper_price_ret",
            "paper_funding_ret",
            "paper_turnover_x",
            "fallback_taker_count",
            "avg_entry_slippage_bps",
            "avg_exit_policy_delta_bps",
            "residual_flatten_hit",
            "unexplained_gap_usdt",
        ]]

    drift_repeat_display = build_repeated_mismatch_table(repeated) if repeated else pd.DataFrame()

    drift_detail_display = drift_attribution.copy().head(12)
    if not drift_detail_display.empty:
        drift_detail_display = drift_detail_display[[
            "decision_ts",
            "basket_id",
            "status",
            "delta_vs_paper",
            "delta_vs_paper_bps",
            "mechanism_mismatch_class",
            "composition_class",
            "missing_symbols_vs_paper",
            "extra_symbols_vs_paper",
            "paper_gate_on",
            "paper_veto_count",
            "paper_price_ret",
            "paper_funding_ret",
            "paper_turnover_x",
            "fallback_taker_count",
            "avg_entry_slippage_bps",
            "avg_exit_policy_delta_bps",
            "non_horizon_exit_leg_count",
            "residual_flatten_hit",
            "attribution_notes",
            "unexplained_gap_usdt",
        ]]

    if not open_legs_display.empty:
        open_legs_display = open_legs_display[[
            "symbol",
            "side",
            "basket_role",
            "entry_time",
            "planned_exit_ts",
            "unrealized_pnl",
            "submit_outcome",
            "fallback_reason",
        ]]

    if not order_lineage.empty:
        order_lineage = order_lineage.head(18)

    countable_live_closed = live_closed.copy()
    if not countable_live_closed.empty and "status" in countable_live_closed.columns:
        countable_live_closed = countable_live_closed[countable_live_closed["status"].astype(str) != "closed_unbucketed_adjustment"].reset_index(drop=True)
    live_realized_pnl = float(safe_float(live_closed.get("basket_net_pnl")).fillna(0.0).sum()) if not live_closed.empty else 0.0
    live_realized_fee = float(safe_float(live_closed.get("basket_fee")).fillna(0.0).sum()) if not live_closed.empty else 0.0
    live_open_mtm = float(safe_float(live_open.get("basket_net_pnl")).fillna(0.0).sum()) if not live_open.empty else 0.0
    loss_summary = compute_loss_streak(countable_live_closed)
    pre_close_metrics = safe_dict(closeout_receipt.get("pre_close_metrics")) if closeout_executed else {}
    pre_close_realized_pnl = float(safe_float(pd.Series([pre_close_metrics.get("realized_net_pnl")])).fillna(live_realized_pnl).iloc[0]) if closeout_executed else live_realized_pnl
    pre_close_open_mtm = float(safe_float(pd.Series([pre_close_metrics.get("open_unrealized_pnl")])).fillna(live_open_mtm).iloc[0]) if closeout_executed else live_open_mtm
    pre_close_snapshot_total = pre_close_realized_pnl + pre_close_open_mtm
    paper_closed_pnl_total = float(safe_float(paper_closed.get("paper_pnl_usdt")).fillna(0.0).sum()) if not paper_closed.empty else 0.0
    paper_open_pnl_total = float(safe_float(paper_open.get("paper_pnl_usdt")).fillna(0.0).sum()) if not paper_open.empty else 0.0
    matched_baskets = int(match_table["paper_coverage"].fillna(False).sum()) if not match_table.empty and "paper_coverage" in match_table.columns else 0
    paper_closed_matches = int(((match_table.get("status").astype(str) != "open_mtm") & match_table.get("paper_coverage").fillna(False)).sum()) if not match_table.empty else 0
    paper_open_matches = int(((match_table.get("status").astype(str) == "open_mtm") & match_table.get("paper_coverage").fillna(False)).sum()) if not match_table.empty else 0
    matched_paper = match_table[match_table["paper_coverage"].fillna(False)].copy() if not match_table.empty else pd.DataFrame()
    matched_live_pnl = float(safe_float(matched_paper.get("live_net_pnl")).fillna(0.0).sum()) if not matched_paper.empty else 0.0
    paper_closed_pnl = float(safe_float(matched_paper.loc[matched_paper.get("status").astype(str) != "open_mtm", "paper_pnl_usdt"]).fillna(0.0).sum()) if not matched_paper.empty else 0.0
    paper_open_pnl = float(safe_float(matched_paper.loc[matched_paper.get("status").astype(str) == "open_mtm", "paper_pnl_usdt"]).fillna(0.0).sum()) if not matched_paper.empty else 0.0
    paper_reference_pnl = paper_closed_pnl + paper_open_pnl
    live_compare_baskets = int(len(match_table))
    paper_reference_ready = matched_baskets > 0
    paper_latest_decision_ts = paper_status.get("latest_decision_ts")
    paper_coverage_status = (
        "live_only"
        if live_compare_baskets <= 0 or matched_baskets <= 0
        else ("full_compare" if matched_baskets == live_compare_baskets else "partial_compare")
    )
    if not paper_latest_decision_ts:
        paper_decisions = pd.concat([as_ts(paper_closed.get("decision_ts")), as_ts(paper_open.get("decision_ts"))], ignore_index=True).dropna() if (not paper_closed.empty or not paper_open.empty) else pd.Series(dtype="datetime64[ns, UTC]")
        if not paper_decisions.empty:
            paper_latest_decision_ts = paper_decisions.max().isoformat()
    paper_latest_mark_ts = paper_status.get("latest_mark_ts")
    shadow_latest_decision_ts = shadow_decision.get("decision_ts")
    if paper_latest_decision_ts and shadow_latest_decision_ts:
        try:
            if pd.to_datetime(paper_latest_decision_ts, utc=True) < pd.to_datetime(shadow_latest_decision_ts, utc=True):
                paper_coverage_status = "stale_partial_compare" if matched_baskets > 0 else "stale_live_only"
        except Exception:
            pass

    current_basket = live_state.get("current_basket") or {}
    current_basket_status = "open_mtm" if not live_open.empty else current_basket.get("basket_status")
    if closeout_executed:
        current_basket_status = "archived_flattened"

    generated_at_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    live_last_run_utc = live_status.get("last_run_at_utc") or live_status.get("last_run_utc")
    last_live_refresh_age_minutes = None
    live_snapshot_status = "unknown"
    if live_last_run_utc:
        try:
            age_seconds = max((datetime.now(timezone.utc) - pd.to_datetime(live_last_run_utc, utc=True).to_pydatetime()).total_seconds(), 0.0)
            last_live_refresh_age_minutes = age_seconds / 60.0
            live_snapshot_status = "fresh" if age_seconds <= 20 * 60 else ("aging" if age_seconds <= 60 * 60 else "stale")
        except Exception:
            live_snapshot_status = "unknown"

    metrics = {
        "strategy_state": "archived" if closeout_executed else ("running" if (len(live_open) > 0 or active_basket_id) else "idle"),
        "compare_start_ts": compare_start.isoformat() if compare_start is not None else None,
        "live_closed_baskets": len(countable_live_closed),
        "live_closed_legs": int(safe_float(live_closed.get("leg_count")).fillna(0).sum()) if not live_closed.empty else 0,
        "live_closed_curve_segments": len(live_closed),
        "live_realized_pnl": live_realized_pnl,
        "live_realized_fee": live_realized_fee,
        "live_open_baskets": len(live_open),
        "live_open_mtm": live_open_mtm,
        "live_total_mtm": live_realized_pnl + live_open_mtm,
        "pre_close_realized_pnl": pre_close_realized_pnl,
        "pre_close_open_mtm": pre_close_open_mtm,
        "pre_close_snapshot_total": pre_close_snapshot_total,
        "terminal_closeout_net_pnl": closeout_curve_summary.get("net_pnl"),
        "terminal_closeout_fee": closeout_curve_summary.get("fee"),
        "terminal_closeout_gross_pnl": closeout_curve_summary.get("gross_pnl"),
        "terminal_closeout_leg_count": closeout_curve_summary.get("leg_count"),
        "paper_reference_baskets": len(paper_closed) + len(paper_open),
        "paper_closed_reference_baskets": len(paper_closed),
        "paper_open_reference_baskets": len(paper_open),
        "paper_reference_pnl": paper_reference_pnl,
        "paper_closed_reference_pnl": paper_closed_pnl,
        "paper_open_reference_pnl": paper_open_pnl,
        "paper_reference_total_window_pnl": paper_closed_pnl_total + paper_open_pnl_total,
        "live_matched_pnl": matched_live_pnl,
        "live_vs_paper_gap": matched_live_pnl - paper_reference_pnl if paper_reference_ready else None,
        "matched_baskets": matched_baskets,
        "paper_closed_matches": paper_closed_matches,
        "paper_open_matches": paper_open_matches,
        "live_compare_baskets": live_compare_baskets,
        "paper_coverage_status": paper_coverage_status,
        "paper_latest_decision_ts": paper_latest_decision_ts,
        "paper_latest_mark_ts": paper_latest_mark_ts,
        "active_basket_id": active_basket_id,
        "current_basket_status": current_basket_status,
        "latest_shadow_bar_key": shadow_decision.get("bar_key"),
        "latest_shadow_decision_ts": shadow_decision.get("decision_ts"),
        "shadow_gate_on": shadow_decision.get("gate_on"),
        "last_run_utc": live_last_run_utc,
        "last_live_refresh_age_minutes": last_live_refresh_age_minutes,
        "live_snapshot_status": live_snapshot_status,
        "tracked_execution_regime": (((live_compare.get("tracked_basket_outcome") or {}).get("basket_parity") or {}).get("submitted_basket") or {}).get("execution_regime"),
        "paper_reference_ready": paper_reference_ready,
        "top_gap_basket_id": top_gap_first.get("basket_id"),
        "top_gap_abs_usdt": abs(float(safe_float(pd.Series([top_gap_first.get("delta_vs_paper")])).fillna(0.0).iloc[0])) if top_gap_first else None,
        "fallback_affected_baskets": safe_dict(repeated.get("fallback_taker_baskets")).get("count", 0),
        "composition_mismatch_baskets": safe_dict(repeated.get("symbol_mismatch_baskets")).get("count", 0),
        "residual_affected_baskets": safe_dict(repeated.get("residual_affected_baskets")).get("count", 0),
        "win_basket_count": loss_summary["wins"],
        "loss_basket_count": loss_summary["losses"],
        "mean_basket_pnl": loss_summary["mean_basket_pnl"],
        "last3_all_negative": loss_summary["last3_all_negative"],
        "last5_all_negative": loss_summary["last5_all_negative"],
        "sustained_loss_verdict": loss_summary["sustained_loss"],
        "loss_streak_label": f"{loss_summary['losses']} losing baskets" if loss_summary["losses"] else "0 losing baskets",
    }

    paper_highlight = (
        f"matched cumulative basis 下，paper = {money(paper_reference_pnl)}（closed={money(paper_closed_pnl)} · open snapshot={money(paper_open_pnl)}），live minus paper = {money(metrics['live_vs_paper_gap'])}。"
        if paper_reference_ready
        else "当前 artifacts 中没有覆盖 compare window 的 independent backtest-only paper reference，因此主图不会伪造 matched compare。"
    )
    timeline_counts = compare_timeline["timeline_status"].value_counts().to_dict() if not compare_timeline.empty else {}
    highlights = [
        f"最终停止后 terminal realized pnl = {money(live_realized_pnl)}；其中最后一次 closeout basket = {money(closeout_curve_summary.get('net_pnl')) if closeout_curve_summary else '-'}。",
        f"历史上有 1 个 unbucketed closed-trade adjustment（{money(float(safe_float(orphan_closed_adjustment_df.get('basket_net_pnl')).fillna(0.0).sum()) if not orphan_closed_adjustment_df.empty else 0.0)}），已并入最终 realized curve，但不计入正式 basket 胜负统计。",
        f"closed basket 胜负分布：wins={int(loss_summary['wins'])} · losses={int(loss_summary['losses'])} · sustained_loss={bool(loss_summary['sustained_loss'])}。",
        f"目前累计纳入最终 realized curve 的段数 = {len(live_closed)}（其中正式 baskets={len(countable_live_closed)}），当前 open baskets = {len(live_open)}。",
        f"顶部 live realized pnl = {money(live_realized_pnl)}，snapshot total = {money(live_realized_pnl + live_open_mtm)}；但主图不再使用这条 mixed-frequency 口径。",
        f"主图当前只累计 matched baskets：matched live = {money(matched_live_pnl)}，matched paper = {money(paper_reference_pnl)}。",
        f"timeline 统计：exact match={int(timeline_counts.get('exact_match', 0))} · symbol mismatch={int(timeline_counts.get('symbol_mismatch', 0))} · economic drift={int(timeline_counts.get('economic_drift', 0))} · open snapshot={int(timeline_counts.get('open_snapshot', 0))} · missing coverage={int(timeline_counts.get('missing_coverage', 0))}。",
        paper_highlight,
        f"当前 active basket = {active_basket_id or '-'}，current basket status = {current_basket_status or '-'}，shadow 最新官方 bar = {shadow_decision.get('bar_key') or '-'}，paper latest decision = {paper_latest_decision_ts or '-'}。",
        f"tracked execution regime = {metrics.get('tracked_execution_regime') or '-'}。",
    ]
    if closeout_receipt:
        highlights.insert(
            0,
            f"收口回执：flatten submitted at {fmt_ts(closeout_receipt.get('flatten_submitted_at_utc'))}，timers disabled at {fmt_ts(closeout_receipt.get('timers_disabled_at_utc'))}，remaining positions={closeout_receipt.get('remaining_position_count_after_flatten', 0)}，pre-close snapshot={money(pre_close_snapshot_total)}。",
        )
    limitations = [
        "主图更公平，但仍不是账户级真实 NAV；当前没有独立 live funding ledger，也没有 historical equity curve。",
        "live fees 来自 closed_trades 中的 estimated fee；当前没有独立 live funding ledger。",
        "停止后的 terminal realized curve 会把最后一次 flatten 成交并入，但 open legs 的 entry/exit fee 仍按 config bps 做估算，而不是交易所逐笔 fee ledger 回放。",
        "paper PnL 仍按 120 USDT gross basket notional 等值，不代表真实账户规模回放。",
        "当前 open basket 只能与同 decision timestamp 的 paper open snapshot 做静态对照，还不是完整 path-by-path fill replay。",
        "drift attribution 是基于 basket parity / lifecycle / residual history 的审计拆账，不代表已精确还原账户级 NAV。",
        "若缺少独立 funding ledger 或无法把 residual/reconciliation 精确拆到腿，页面会保留 unexplained gap，而不是伪装成 fully explained。",
    ]
    if not paper_reference_ready:
        limitations.append("paper artifacts 目前没有覆盖到当前 live compare window，所以 paper 对照区会暂时留空，直到独立 historical K-line/funding reference 刷新到相同时间段。")
    elif str(paper_coverage_status).startswith("stale_"):
        limitations.append("当前 independent paper reference 已部分覆盖 compare window，但最新 paper decision 仍落后于最新 shadow/live 窗口，因此 coverage 仍是 stale partial，不应把缺口误读成完整 parity。")

    payload = {
        "generated_at_utc": generated_at_utc,
        "strategy_id": "rank213_age90_14d_skip1d_voladj_top50_4x4",
        "page_type": "live_vs_backtest_report",
        "metrics": metrics,
        "highlights": highlights,
        "limitations": limitations,
        "live_closed_baskets": [] if live_closed.empty else json.loads(live_closed.to_json(orient="records", date_format="iso")),
        "live_open_baskets": [] if live_open.empty else json.loads(live_open.to_json(orient="records", date_format="iso")),
        "closeout_legs": [] if closeout_leg_df.empty else json.loads(closeout_leg_df.to_json(orient="records", date_format="iso")),
        "basket_matches": [] if match_table.empty else json.loads(match_table.to_json(orient="records", date_format="iso")),
        "compare_timeline": [] if compare_timeline.empty else json.loads(compare_timeline.to_json(orient="records", date_format="iso")),
        "drift_summary": drift_summary,
        "drift_attribution": [] if drift_attribution.empty else json.loads(drift_attribution.to_json(orient="records", date_format="iso")),
        "paper_reference_status": paper_status,
        "closeout_receipt": closeout_receipt,
    }

    html_payload = {
        **payload,
        "compare_timeline_band": compare_timeline,
        "compare_timeline_bar": compare_timeline_bar,
        "compare_timeline_display": compare_timeline_display,
        "match_table_display": match_display,
        "drift_top_display": drift_top_display,
        "drift_repeat_display": drift_repeat_display,
        "drift_detail_display": drift_detail_display,
        "open_legs_display": open_legs_display,
        "order_lineage_display": order_lineage,
        "final_realized_curve_series": curve_series(realized_curve_df, ts_col="ts", value_col="basket_net_pnl", label="cumulative realized pnl", color="#60a5fa", cumulative=True),
        "matched_live_pnl_curve_series": curve_series(matched_live_curve_df, ts_col="ts", value_col="pnl_usdt", label="matched live cumulative pnl", color="#2563eb", cumulative=False),
        "matched_paper_pnl_curve_series": curve_series(matched_paper_curve_df, ts_col="ts", value_col="pnl_usdt", label="matched paper cumulative pnl", color="#22c55e", cumulative=False),
        "matched_delta_curve_series": curve_series(matched_delta_curve_df, ts_col="ts", value_col="pnl_usdt", label="cumulative live minus paper", color="#ef4444", cumulative=False),
    }

    if drift_attribution.empty:
        DRIFT_ATTRIBUTION_PATH.write_text("", encoding="utf-8")
    else:
        drift_attribution.to_csv(DRIFT_ATTRIBUTION_PATH, index=False)
    DRIFT_SUMMARY_PATH.write_text(json.dumps(drift_summary, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_HTML.write_text(render_html(html_payload), encoding="utf-8")
    print(OUT_JSON)
    print(OUT_HTML)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
