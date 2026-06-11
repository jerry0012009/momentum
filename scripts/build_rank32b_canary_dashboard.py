#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "rank32b_canary"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "rank32b_canary"
OUT_PATH = SITE_DIR / "report.html"
DOC_PATH = ROOT / "docs" / "CANARY_32B_TODO.md"
PHASE1_DOC_PATH = ROOT / "docs" / "CANARY_32B_PHASE1.md"
PHASE2_DOC_PATH = ROOT / "docs" / "CANARY_32B_PHASE2.md"
PHASE3_DOC_PATH = ROOT / "docs" / "CANARY_32B_PHASE3.md"
PHASE4_DOC_PATH = ROOT / "docs" / "CANARY_32B_PHASE4.md"
PHASE5_DOC_PATH = ROOT / "docs" / "CANARY_32B_PHASE5.md"
PHASE6_DOC_PATH = ROOT / "docs" / "CANARY_32B_PHASE6.md"

PH1_STATUS_PATH = ART_DIR / "phase1_status.json"
PH1_RUN_SUMMARY_PATH = ART_DIR / "phase1_last_run_summary.json"
PH1_INTENTIONS_PATH = ART_DIR / "phase1_recent_intentions.json"
PH1_REJECTIONS_PATH = ART_DIR / "phase1_recent_rejections.json"
PH1_SYMBOL_STATE_PATH = ART_DIR / "phase1_symbol_state.json"

PH2_STATUS_PATH = ART_DIR / "phase2_status.json"
PH2_RUN_SUMMARY_PATH = ART_DIR / "phase2_last_run_summary.json"
PH2_INTENTIONS_PATH = ART_DIR / "phase2_recent_intentions.json"
PH2_ORDERS_PATH = ART_DIR / "phase2_recent_orders.json"
PH2_REJECTIONS_PATH = ART_DIR / "phase2_recent_rejections.json"
PH2_CHAINS_PATH = ART_DIR / "phase2_receipt_chains.json"
PH2_SYMBOL_STATE_PATH = ART_DIR / "phase2_symbol_state.json"
PH2_PACKET_PATH = ART_DIR / "phase2_operator_packet.json"

PH3_STATUS_PATH = ART_DIR / "phase3_status.json"
PH3_RUN_SUMMARY_PATH = ART_DIR / "phase3_last_run_summary.json"
PH3_VENUE_HEALTH_PATH = ART_DIR / "phase3_venue_health.json"
PH3_ACCOUNT_SNAPSHOT_PATH = ART_DIR / "phase3_account_snapshot.json"
PH3_LEDGER_PATH = ART_DIR / "phase3_order_ledger.json"
PH3_PACKET_PATH = ART_DIR / "phase3_operator_packet.json"

PH4_STATUS_PATH = ART_DIR / "phase4_status.json"
PH4_RUN_SUMMARY_PATH = ART_DIR / "phase4_last_run_summary.json"
PH4_RECEIPT_PATH = ART_DIR / "phase4_execution_receipt.json"
PH4_PACKET_PATH = ART_DIR / "phase4_operator_packet.json"

PH5_STATUS_PATH = ART_DIR / "phase5_status.json"
PH5_RUN_SUMMARY_PATH = ART_DIR / "phase5_last_run_summary.json"
PH5_RECEIPT_PATH = ART_DIR / "phase5_execution_receipt.json"
PH5_PACKET_PATH = ART_DIR / "phase5_operator_packet.json"

PH6_STATUS_PATH = ART_DIR / "phase6_status.json"
PH6_RUN_SUMMARY_PATH = ART_DIR / "phase6_last_run_summary.json"
PH6_ORDERS_PATH = ART_DIR / "phase6_recent_orders.json"
PH6_POSITIONS_PATH = ART_DIR / "phase6_recent_positions.json"
PH6_CLOSED_PATH = ART_DIR / "phase6_recent_closed_trades.json"
PH6_SIGNALS_PATH = ART_DIR / "phase6_recent_signals.json"
PH6_EVENTS_PATH = ART_DIR / "phase6_events.jsonl"
PH6_REJECTIONS_PATH = ART_DIR / "phase6_recent_rejections.json"
PH6_STATE_PATH = ART_DIR / "phase6_state.json"
PH6_WARNINGS_PATH = ART_DIR / "phase6_warnings.json"
PH6_PACKET_PATH = ART_DIR / "phase6_operator_packet.json"
PH6_SMALLCAP_ACTIVITY_CACHE_PATH = ART_DIR / "phase6_smallcap_activity_cache.json"
PH6_OBSERVATION_WINDOW_PATH = ART_DIR / "phase6_observation_window.json"
SHADOW_BEAT_RUN_SUMMARY_PATH = ROOT / "reports" / "artifacts" / "rank32b_shadow_beat" / "shadow_last_run_summary.json"
SHADOW_BEAT_STATUS_PATH = ROOT / "reports" / "artifacts" / "rank32b_shadow_beat" / "shadow_status.json"
SHADOW_BEAT_PAPER_SUMMARY_PATH = ROOT / "reports" / "artifacts" / "rank32b_shadow_beat" / "paper_summary.json"
SHADOW_BEAT_PAPER_TRADES_PATH = ROOT / "reports" / "artifacts" / "rank32b_shadow_beat" / "paper_trades.json"
SHADOW_GLOBAL_RUN_SUMMARY_PATH = ROOT / "reports" / "artifacts" / "rank32b_shadow_global_winner" / "shadow_last_run_summary.json"
SHADOW_GLOBAL_STATUS_PATH = ROOT / "reports" / "artifacts" / "rank32b_shadow_global_winner" / "shadow_status.json"
SHADOW_GLOBAL_PAPER_SUMMARY_PATH = ROOT / "reports" / "artifacts" / "rank32b_shadow_global_winner" / "paper_summary.json"
SHADOW_GLOBAL_PAPER_TRADES_PATH = ROOT / "reports" / "artifacts" / "rank32b_shadow_global_winner" / "paper_trades.json"
GLOBAL_LIVE_RUN_SUMMARY_PATH = ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_last_run_summary.json"
GLOBAL_LIVE_STATUS_PATH = ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_status.json"
GLOBAL_LIVE_COMPARE_PATH = ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_vs_shadow.csv"
SNAPSHOT_SCRIPT = ROOT / "scripts" / "build_rank32b_live_email_snapshot.py"
CONFIG_PATH = ROOT / "config" / "execution" / "rank32b_canary.yaml"

EXIT_REASON_LABELS = {
    "manual_market_close": "手动平仓",
    "manual_close": "手动平仓",
    "external_flat_reconciled": "外部/对账平仓",
    "exit_attach_failed_market_close": "止损挂单失败后平仓",
    "tp_attach_failed_market_close": "止盈挂单失败后平仓",
    "attach_failed_market_close": "保护单挂单失败平仓",
    "take_profit": "止盈",
    "stop_loss": "止损",
    "timeout_market": "超时",
    "timeout_close": "超时",
}
NATURAL_EXIT_REASONS = {"take_profit", "stop_loss", "timeout_market", "timeout_close"}
SIGNAL_MODE_LABELS = {
    "preview_unclosed15m": "preview",
    "official_close": "official_close",
    "-": "历史旧样本/未标记",
    "": "历史旧样本/未标记",
}


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def load_jsonl(path: Path, default):
    if not path.exists():
        return default
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows if rows else default


def run_text_command(command: str, *, timeout: int = 20) -> str:
    try:
        out = subprocess.check_output(
            ["/bin/bash", "-lc", command],
            cwd=str(ROOT),
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
        )
        return out.strip()
    except Exception as exc:  # noqa: BLE001
        return f"命令执行失败：{exc}"


def num(v, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f}"


def fmt(v) -> str:
    if v is None or pd.isna(v):
        return "-"
    text = str(v).strip()
    if text.lower() == "nan":
        return "-"
    return text or "-"


def fmt_ts_bj(v) -> str:
    text = fmt(v)
    if text == "-":
        return "-"
    raw = text.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(raw)
    except Exception:
        return text
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    bj = dt.astimezone(timezone(timedelta(hours=8)))
    utc = dt.astimezone(timezone.utc)
    return f"{bj.strftime('%Y-%m-%d %H:%M:%S')} 北京时间 / {utc.strftime('%Y-%m-%d %H:%M:%S')} UTC"


def parse_ts(v) -> datetime | None:
    text = fmt(v)
    if text == "-":
        return None
    raw = text.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(raw)
    except Exception:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def localize_time_columns(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    for col in cols:
        if col in out.columns:
            out[col] = out[col].apply(fmt_ts_bj)
    return out


def render_table(df: pd.DataFrame, digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    digits_cols = digits_cols or {}
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = []
        for col in df.columns:
            val = row[col]
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                text = num(val, digits_cols.get(col, 2))
            else:
                text = fmt(val)
            cells.append(f"<td>{escape(text)}</td>")
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def build_equity_curve_card(df: pd.DataFrame, *, time_col: str, ret_col: str, title: str, subtitle: str, width: int = 960, height: int = 240) -> str:
    if df.empty or time_col not in df.columns or ret_col not in df.columns:
        return f"<div class='card'><h3>{escape(title)}</h3><p class='muted'>暂无可绘制曲线的数据。</p></div>"
    work = df[[time_col, ret_col]].copy()
    work[time_col] = pd.to_datetime(work[time_col], utc=True, errors='coerce')
    work[ret_col] = pd.to_numeric(work[ret_col], errors='coerce')
    work = work.dropna().sort_values(time_col)
    if work.empty:
        return f"<div class='card'><h3>{escape(title)}</h3><p class='muted'>暂无可绘制曲线的数据。</p></div>"
    equity = []
    acc = 1.0
    for value in work[ret_col].tolist():
        acc *= 1.0 + float(value)
        equity.append(acc)
    min_y = min(min(equity), 1.0)
    max_y = max(max(equity), 1.0)
    if abs(max_y - min_y) < 1e-12:
        max_y += 0.01
        min_y -= 0.01
    pad_x = 28
    pad_y = 18
    plot_w = width - pad_x * 2
    plot_h = height - pad_y * 2

    def x_at(i: int) -> float:
        return pad_x + (plot_w * i / max(len(equity) - 1, 1))

    def y_at(v: float) -> float:
        return pad_y + (max_y - v) / (max_y - min_y) * plot_h

    points = " ".join(f"{x_at(i):.2f},{y_at(v):.2f}" for i, v in enumerate(equity))
    base_y = y_at(1.0)
    stroke = "#3ddc97" if equity[-1] >= 1.0 else "#ff6b6b"
    fill = "rgba(61,220,151,0.10)" if equity[-1] >= 1.0 else "rgba(255,107,107,0.10)"
    area_points = f"{pad_x:.2f},{base_y:.2f} " + points + f" {x_at(len(equity)-1):.2f},{base_y:.2f}"
    start_ts = work[time_col].iloc[0].strftime('%Y-%m-%d %H:%M UTC')
    end_ts = work[time_col].iloc[-1].strftime('%Y-%m-%d %H:%M UTC')
    return (
        f"<div class='card'><h3>{escape(title)}</h3>"
        f"<p class='muted'>{escape(subtitle)}</p>"
        f"<svg viewBox='0 0 {width} {height}' width='100%' height='{height}' role='img' aria-label='{escape(title)}'>"
        f"<line x1='{pad_x}' y1='{base_y:.2f}' x2='{width-pad_x}' y2='{base_y:.2f}' stroke='#5b6b7b' stroke-dasharray='4 4' stroke-width='1'/>"
        f"<polygon points='{area_points}' fill='{fill}' />"
        f"<polyline points='{points}' fill='none' stroke='{stroke}' stroke-width='3' stroke-linejoin='round' stroke-linecap='round'/>"
        f"</svg>"
        f"<p class='muted'>样本 {len(equity)} 笔｜起点 1.0000 ｜终点 {equity[-1]:.4f} ｜区间 {escape(start_ts)} → {escape(end_ts)}</p>"
        f"</div>"
    )


def build_multi_strategy_equity_card(series_items: list[dict[str, object]], *, title: str, subtitle: str, width: int = 980, height: int = 300) -> str:
    prepared: list[dict[str, object]] = []
    all_ts: list[pd.Timestamp] = []
    all_eq: list[float] = [1.0]
    for item in series_items:
        df = item.get("df")
        time_col = str(item.get("time_col") or "")
        ret_col = str(item.get("ret_col") or "")
        if not isinstance(df, pd.DataFrame) or df.empty or time_col not in df.columns or ret_col not in df.columns:
            continue
        work = df[[time_col, ret_col]].copy()
        work[time_col] = pd.to_datetime(work[time_col], utc=True, errors="coerce")
        work[ret_col] = pd.to_numeric(work[ret_col], errors="coerce")
        work = work.dropna().sort_values(time_col)
        if work.empty:
            continue
        eq = []
        acc = 1.0
        for value in work[ret_col].tolist():
            acc *= 1.0 + float(value)
            eq.append(acc)
        prepared.append({
            "label": str(item.get("label") or "strategy"),
            "color": str(item.get("color") or "#60a5fa"),
            "work": work,
            "equity": eq,
        })
        all_ts.extend(work[time_col].tolist())
        all_eq.extend(eq)
    if not prepared or not all_ts:
        return f"<div class='card'><h3>{escape(title)}</h3><p class='muted'>暂无可绘制的三策略净值对照数据。</p></div>"
    min_ts = min(all_ts)
    max_ts = max(all_ts)
    min_y = min(all_eq)
    max_y = max(all_eq)
    if min_ts == max_ts:
        max_ts = min_ts + pd.Timedelta(minutes=1)
    if abs(max_y - min_y) < 1e-12:
        max_y += 0.01
        min_y -= 0.01
    pad_x = 42
    pad_y = 18
    plot_w = width - pad_x * 2
    plot_h = height - pad_y * 2

    def x_at(ts: pd.Timestamp) -> float:
        return pad_x + (plot_w * ((ts - min_ts).total_seconds() / max((max_ts - min_ts).total_seconds(), 1)))

    def y_at(v: float) -> float:
        return pad_y + (max_y - v) / (max_y - min_y) * plot_h

    base_y = y_at(1.0)
    parts = [f"<line x1='{pad_x}' y1='{base_y:.2f}' x2='{width-pad_x}' y2='{base_y:.2f}' stroke='#5b6b7b' stroke-dasharray='4 4' stroke-width='1' />"]
    legend = []
    summaries = []
    for item in prepared:
        work = item["work"]
        eq = item["equity"]
        color = item["color"]
        pts = " ".join(f"{x_at(ts):.2f},{y_at(val):.2f}" for ts, val in zip(work[work.columns[0]].tolist(), eq))
        parts.append(f"<polyline points='{pts}' fill='none' stroke='{color}' stroke-width='2.5' stroke-linejoin='round' stroke-linecap='round' />")
        for ts, val in zip(work[work.columns[0]].tolist(), eq):
            parts.append(f"<circle cx='{x_at(ts):.2f}' cy='{y_at(val):.2f}' r='2.8' fill='{color}' />")
        legend.append(f"<span style='display:inline-flex;align-items:center;gap:6px;margin-right:14px;'><span style='width:10px;height:10px;border-radius:999px;background:{color};display:inline-block;'></span>{escape(str(item['label']))}</span>")
        summaries.append(f"{escape(str(item['label']))}：终点 {eq[-1]:.4f}（{len(eq)} 笔）")
    return (
        f"<div class='card'><h3>{escape(title)}</h3>"
        f"<p class='muted'>{escape(subtitle)}</p>"
        f"<p>{''.join(legend)}</p>"
        f"<svg viewBox='0 0 {width} {height}' width='100%' height='{height}' role='img' aria-label='{escape(title)}'>{''.join(parts)}</svg>"
        f"<p class='muted'>区间 {escape(min_ts.strftime('%Y-%m-%d %H:%M UTC'))} → {escape(max_ts.strftime('%Y-%m-%d %H:%M UTC'))} ｜ {' ｜ '.join(summaries)}</p>"
        f"</div>"
    )


def build_multi_strategy_pnl_timeline_card(df: pd.DataFrame, *, time_col: str, pnl_col: str, strategy_col: str, color_map: dict[str, str], title: str, subtitle: str, width: int = 980, height: int = 320) -> str:
    if df.empty or time_col not in df.columns or pnl_col not in df.columns or strategy_col not in df.columns:
        return f"<div class='card'><h3>{escape(title)}</h3><p class='muted'>暂无可绘制的时间轴盈亏点数据。</p></div>"
    work = df[[time_col, pnl_col, strategy_col]].copy()
    work[time_col] = pd.to_datetime(work[time_col], utc=True, errors='coerce')
    work[pnl_col] = pd.to_numeric(work[pnl_col], errors='coerce')
    work[strategy_col] = work[strategy_col].astype(str)
    work = work.dropna().sort_values(time_col)
    if work.empty:
        return f"<div class='card'><h3>{escape(title)}</h3><p class='muted'>暂无可绘制的时间轴盈亏点数据。</p></div>"
    min_ts = work[time_col].min()
    max_ts = work[time_col].max()
    min_y = min(float(work[pnl_col].min()), 0.0)
    max_y = max(float(work[pnl_col].max()), 0.0)
    if min_ts == max_ts:
        max_ts = min_ts + pd.Timedelta(minutes=1)
    if abs(max_y - min_y) < 1e-12:
        max_y += 1.0
        min_y -= 1.0
    pad_x = 42
    pad_y = 18
    plot_w = width - pad_x * 2
    plot_h = height - pad_y * 2

    def x_at(ts: pd.Timestamp) -> float:
        return pad_x + (plot_w * ((ts - min_ts).total_seconds() / max((max_ts - min_ts).total_seconds(), 1)))

    def y_at(v: float) -> float:
        return pad_y + (max_y - v) / (max_y - min_y) * plot_h

    zero_y = y_at(0.0)
    parts = [f"<line x1='{pad_x}' y1='{zero_y:.2f}' x2='{width-pad_x}' y2='{zero_y:.2f}' stroke='#5b6b7b' stroke-dasharray='4 4' stroke-width='1' />"]
    legend = []
    for strategy, part in work.groupby(strategy_col):
        color = color_map.get(strategy, '#60a5fa')
        legend.append(f"<span style='display:inline-flex;align-items:center;gap:6px;margin-right:14px;'><span style='width:10px;height:10px;border-radius:999px;background:{color};display:inline-block;'></span>{escape(strategy)}</span>")
        for _, row in part.iterrows():
            parts.append(f"<circle cx='{x_at(row[time_col]):.2f}' cy='{y_at(float(row[pnl_col])):.2f}' r='4' fill='{color}' fill-opacity='0.85' />")
    return (
        f"<div class='card'><h3>{escape(title)}</h3>"
        f"<p class='muted'>{escape(subtitle)}</p>"
        f"<p>{''.join(legend)}</p>"
        f"<svg viewBox='0 0 {width} {height}' width='100%' height='{height}' role='img' aria-label='{escape(title)}'>{''.join(parts)}</svg>"
        f"<p class='muted'>每个点代表一笔已实现/已标记收益；横轴是时间，纵轴是单笔收益率。</p>"
        f"</div>"
    )


def build_interactive_strategy_compare_section(payload: dict[str, object]) -> str:
    payload_json = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    return """
<div class='card'>
  <h3>三策略对照（可切换时间窗）</h3>
  <p class='muted'>用同一时间轴同时看真钱 core3、Alt shadow、Global shadow。上面是净值曲线，下面是逐笔盈亏点；可切换 3 天 / 7 天 / 15 天 / 30 天 / 全部。</p>
  <style>
    .strategy-compare-controls { display:flex; flex-wrap:wrap; gap:10px; margin:14px 0 10px; }
    .strategy-compare-btn { background:#0f172a; color:#cbd5e1; border:1px solid #334155; border-radius:999px; padding:8px 14px; cursor:pointer; font-size:13px; }
    .strategy-compare-btn.active { background:#2563eb; border-color:#2563eb; color:white; }
    .strategy-compare-grid { display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:12px; margin:12px 0 18px; }
    .strategy-mini { background:#0f172a; border:1px solid #1f2937; border-radius:12px; padding:12px 14px; }
    .strategy-mini .label { font-size:12px; color:#94a3b8; margin-bottom:6px; }
    .strategy-mini .value { font-size:22px; font-weight:700; }
    .strategy-mini .meta { margin-top:6px; color:#9ca3af; font-size:12px; line-height:1.45; }
    .strategy-compare-chart { margin: 14px 0 20px; }
  </style>
  <div class='strategy-compare-controls' id='strategyCompareControls'></div>
  <div class='strategy-compare-grid' id='strategyCompareSummary'></div>
  <div class='strategy-compare-chart' id='strategyCompareEquity'></div>
  <div class='strategy-compare-chart' id='strategyCompareTimeline'></div>
  <script id='strategyComparePayload' type='application/json'>__PAYLOAD__</script>
  <script>
  (function () {
    const el = document.getElementById('strategyComparePayload');
    if (!el) return;
    const payload = JSON.parse(el.textContent || '{}');
    const windows = [
      { key: '3d', label: '3天', days: 3 },
      { key: '7d', label: '7天', days: 7 },
      { key: '15d', label: '15天', days: 15 },
      { key: '30d', label: '30天', days: 30 },
      { key: 'all', label: '全部', days: null },
    ];
    const controlsEl = document.getElementById('strategyCompareControls');
    const summaryEl = document.getElementById('strategyCompareSummary');
    const equityEl = document.getElementById('strategyCompareEquity');
    const timelineEl = document.getElementById('strategyCompareTimeline');
    const strategies = Array.isArray(payload.strategies) ? payload.strategies : [];
    let activeKey = '7d';

    function fmtPct(v) {
      if (v === null || v === undefined || Number.isNaN(v)) return '-';
      const pct = v * 100;
      const sign = pct > 0 ? '+' : '';
      return sign + pct.toFixed(2) + '%';
    }

    function fmtTs(ts) {
      try { return new Date(ts).toISOString().slice(0,16).replace('T', ' ') + ' UTC'; } catch { return String(ts || '-'); }
    }

    function getFilteredSeries(days) {
      const allPoints = strategies.flatMap(s => Array.isArray(s.trades) ? s.trades : []);
      const timestamps = allPoints.map(x => new Date(x.ts).getTime()).filter(Number.isFinite);
      if (!timestamps.length) return { minTs: null, maxTs: null, series: [] };
      const maxTs = Math.max.apply(null, timestamps);
      const minTs = days ? maxTs - days * 24 * 3600 * 1000 : Math.min.apply(null, timestamps);
      const series = strategies.map((s) => {
        const trades = (Array.isArray(s.trades) ? s.trades : [])
          .map(t => ({ ...t, ms: new Date(t.ts).getTime() }))
          .filter(t => Number.isFinite(t.ms) && t.ms >= minTs && t.ms <= maxTs)
          .sort((a, b) => a.ms - b.ms);
        return { ...s, trades };
      });
      return { minTs, maxTs, series };
    }

    function renderButtons() {
      controlsEl.innerHTML = windows.map(w => `<button class="strategy-compare-btn ${w.key === activeKey ? 'active' : ''}" data-key="${w.key}">${w.label}</button>`).join('');
      controlsEl.querySelectorAll('button').forEach(btn => btn.addEventListener('click', () => {
        activeKey = btn.dataset.key;
        render();
      }));
    }

    function renderSummary(state) {
      summaryEl.innerHTML = state.series.map((s) => {
        const trades = s.trades || [];
        let eq = 1.0;
        let wins = 0;
        let sum = 0.0;
        trades.forEach(t => { eq *= (1 + Number(t.ret || 0)); sum += Number(t.ret || 0); if (Number(t.ret || 0) > 0) wins += 1; });
        const total = eq - 1;
        const wr = trades.length ? wins / trades.length : null;
        const avg = trades.length ? sum / trades.length : null;
        const valueColor = total >= 0 ? '#34d399' : '#f87171';
        return `<div class="strategy-mini"><div class="label"><span style="display:inline-block;width:10px;height:10px;border-radius:999px;background:${s.color};margin-right:6px;"></span>${s.label}</div><div class="value" style="color:${valueColor}">${fmtPct(total)}</div><div class="meta">窗口内 ${trades.length} 笔｜胜率 ${wr === null ? '-' : (wr*100).toFixed(1)+'%'}<br>平均单笔 ${fmtPct(avg)}</div></div>`;
      }).join('');
    }

    function renderEquity(state) {
      if (!state.series.some(s => (s.trades || []).length)) {
        equityEl.innerHTML = '<p class="muted">这个时间窗里还没有足够的净值曲线数据。</p>';
        return;
      }
      const width = 980, height = 320, padX = 46, padY = 18, plotW = width - padX*2, plotH = height - padY*2;
      const allTs = [], allEq = [1.0];
      const built = state.series.map((s) => {
        let eq = 1.0;
        const pts = (s.trades || []).map(t => { eq *= (1 + Number(t.ret || 0)); allTs.push(t.ms); allEq.push(eq); return { ms: t.ms, eq }; });
        return { ...s, pts };
      });
      const minTs = Math.min.apply(null, allTs);
      const maxTs = Math.max.apply(null, allTs);
      let minY = Math.min.apply(null, allEq), maxY = Math.max.apply(null, allEq);
      if (Math.abs(maxY - minY) < 1e-12) { maxY += 0.01; minY -= 0.01; }
      const xAt = (ms) => padX + plotW * ((ms - minTs) / Math.max(maxTs - minTs, 1));
      const yAt = (v) => padY + (maxY - v) / (maxY - minY) * plotH;
      const baseY = yAt(1.0);
      const lines = [`<line x1="${padX}" y1="${baseY.toFixed(2)}" x2="${width-padX}" y2="${baseY.toFixed(2)}" stroke="#5b6b7b" stroke-dasharray="4 4" stroke-width="1" />`];
      built.forEach((s) => {
        if (!s.pts.length) return;
        const poly = s.pts.map(p => `${xAt(p.ms).toFixed(2)},${yAt(p.eq).toFixed(2)}`).join(' ');
        lines.push(`<polyline points="${poly}" fill="none" stroke="${s.color}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round" />`);
        s.pts.forEach(p => lines.push(`<circle cx="${xAt(p.ms).toFixed(2)}" cy="${yAt(p.eq).toFixed(2)}" r="3" fill="${s.color}" />`));
      });
      equityEl.innerHTML = `<div class="card"><h3>净值曲线（${windows.find(w => w.key === activeKey).label}）</h3><p class="muted">同一时间窗里看三条策略线谁在爬坡、谁在回撤。</p><svg viewBox="0 0 ${width} ${height}" width="100%" height="${height}">${lines.join('')}</svg><p class="muted">区间 ${fmtTs(new Date(minTs).toISOString())} → ${fmtTs(new Date(maxTs).toISOString())}</p></div>`;
    }

    function renderTimeline(state) {
      const points = state.series.flatMap(s => (s.trades || []).map(t => ({ ...t, strategy: s.label, color: s.color, ms: t.ms })));
      if (!points.length) {
        timelineEl.innerHTML = '<p class="muted">这个时间窗里还没有足够的逐笔盈亏点数据。</p>';
        return;
      }
      const width = 980, height = 340, padX = 46, padY = 18, plotW = width - padX*2, plotH = height - padY*2;
      const minTs = Math.min.apply(null, points.map(p => p.ms));
      const maxTs = Math.max.apply(null, points.map(p => p.ms));
      let minY = Math.min(0, ...points.map(p => Number(p.ret || 0)));
      let maxY = Math.max(0, ...points.map(p => Number(p.ret || 0)));
      if (Math.abs(maxY - minY) < 1e-12) { maxY += 0.01; minY -= 0.01; }
      const xAt = (ms) => padX + plotW * ((ms - minTs) / Math.max(maxTs - minTs, 1));
      const yAt = (v) => padY + (maxY - v) / (maxY - minY) * plotH;
      const zeroY = yAt(0);
      const svg = [`<line x1="${padX}" y1="${zeroY.toFixed(2)}" x2="${width-padX}" y2="${zeroY.toFixed(2)}" stroke="#5b6b7b" stroke-dasharray="4 4" stroke-width="1" />`];
      points.forEach(p => svg.push(`<circle cx="${xAt(p.ms).toFixed(2)}" cy="${yAt(Number(p.ret || 0)).toFixed(2)}" r="4" fill="${p.color}" fill-opacity="0.85"><title>${p.strategy} | ${fmtTs(p.ts)} | ${fmtPct(Number(p.ret || 0))}</title></circle>`));
      timelineEl.innerHTML = `<div class="card"><h3>逐笔盈亏点（${windows.find(w => w.key === activeKey).label}）</h3><p class="muted">每个点是一笔交易；越往上赚得越多，越往下亏得越多。鼠标悬停可看时间和单笔收益。</p><svg viewBox="0 0 ${width} ${height}" width="100%" height="${height}">${svg.join('')}</svg></div>`;
    }

    function render() {
      renderButtons();
      const selected = windows.find(w => w.key === activeKey);
      const state = getFilteredSeries(selected.days);
      renderSummary(state);
      renderEquity(state);
      renderTimeline(state);
    }

    render();
  })();
  </script>
</div>
""".replace("__PAYLOAD__", payload_json)


def excerpt(path: Path, limit: int = 28) -> str:
    if not path.exists():
        return "文档尚未创建。"
    lines = path.read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[:limit])


def trim_df(items: list[dict], cols: list[str], tail: int = 20) -> pd.DataFrame:
    df = pd.DataFrame(items)
    if df.empty:
        return df
    keep = [c for c in cols if c in df.columns]
    return df[keep].tail(tail)


def bucket_for_symbol(symbol: str, smallcap_symbols: set[str]) -> str:
    return "smallcap" if str(symbol or "").upper() in smallcap_symbols else "core"


def annotate_bucket_rows(rows: list[dict], smallcap_symbols: set[str]) -> list[dict]:
    out: list[dict] = []
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, dict):
            continue
        item = dict(row)
        if "symbol_bucket" not in item and item.get("symbol"):
            item["symbol_bucket"] = bucket_for_symbol(str(item.get("symbol")), smallcap_symbols)
        out.append(item)
    return out


def enrich_signal_rows(rows: list[dict], smallcap_symbols: set[str]) -> list[dict]:
    out: list[dict] = []
    for row in annotate_bucket_rows(rows, smallcap_symbols):
        item = dict(row)
        meta = item.get("metadata") if isinstance(item.get("metadata"), dict) else {}
        item["signal_mode"] = meta.get("signal_mode") or item.get("signal_mode")
        item["bucket_start"] = meta.get("bucket_start") or item.get("bucket_start") or item.get("timestamp")
        item["bucket_close_at"] = meta.get("bucket_close_at") or item.get("bucket_close_at")
        item["first_seen_at"] = meta.get("first_seen_at") or item.get("first_seen_at") or meta.get("signal_confirmed_at_override") or item.get("timestamp")
        item["expired_at"] = meta.get("expired_at") or item.get("expired_at")
        item["confirmed_at_close"] = meta.get("confirmed_at_close") if "confirmed_at_close" in meta else item.get("confirmed_at_close")
        item["official_confirmed_at"] = meta.get("official_confirmed_at") or item.get("official_confirmed_at")
        out.append(item)
    return out


def summarize_bucket_health(signal_rows: list[dict], closed_rows: list[dict], reject_rows: list[dict], smallcap_symbols: set[str]) -> pd.DataFrame:
    buckets = ["core", "smallcap"]
    sig_df = pd.DataFrame(annotate_bucket_rows(signal_rows, smallcap_symbols))
    closed_df = pd.DataFrame(annotate_bucket_rows(closed_rows, smallcap_symbols))
    rej_df = pd.DataFrame(annotate_bucket_rows(reject_rows, smallcap_symbols))
    rows: list[dict[str, object]] = []
    for bucket in buckets:
        sig_part = sig_df[sig_df.get("symbol_bucket") == bucket] if not sig_df.empty and "symbol_bucket" in sig_df.columns else pd.DataFrame()
        closed_part = closed_df[closed_df.get("symbol_bucket") == bucket] if not closed_df.empty and "symbol_bucket" in closed_df.columns else pd.DataFrame()
        rej_part = rej_df[rej_df.get("symbol_bucket") == bucket] if not rej_df.empty and "symbol_bucket" in rej_df.columns else pd.DataFrame()
        pnl = pd.to_numeric(closed_part.get("net_pnl"), errors="coerce") if not closed_part.empty and "net_pnl" in closed_part.columns and closed_part["net_pnl"].notna().any() else pd.to_numeric(closed_part.get("gross_pnl"), errors="coerce")
        if pnl is None:
            pnl = pd.Series(dtype=float)
        rows.append({
            "bucket": bucket,
            "signals": int(len(sig_part)),
            "closed_trades": int(len(closed_part)),
            "rejections": int(len(rej_part)),
            "pnl": float(pnl.fillna(0.0).sum()) if hasattr(pnl, "fillna") else 0.0,
            "symbols_seen": int(sig_part.get("symbol", pd.Series(dtype=str)).astype(str).str.upper().nunique()) if not sig_part.empty and "symbol" in sig_part.columns else 0,
        })
    return pd.DataFrame(rows)


def build_smallcap_activity_df(cache_obj: dict, smallcap_symbols: set[str]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    cache = cache_obj if isinstance(cache_obj, dict) else {}
    for symbol in sorted(smallcap_symbols):
        entry = cache.get(symbol, {}) if isinstance(cache.get(symbol), dict) else {}
        rows.append({
            "symbol": symbol,
            "allowed": bool(entry.get("allowed", False)),
            "percentile": entry.get("percentile"),
            "min_percentile": entry.get("min_percentile"),
            "recent_median_quote_volume": entry.get("recent_median_quote_volume"),
            "updated_at": entry.get("updated_at"),
            "cached": bool(entry.get("cached", False)),
            "stale": bool(entry.get("stale", False)),
            "error": entry.get("error") or "",
        })
    return pd.DataFrame(rows)


def prepare_closed_trade_df(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    pnl_col = "net_pnl" if "net_pnl" in df.columns and df["net_pnl"].notna().any() else "gross_pnl"
    df["pnl_used"] = pd.to_numeric(df.get(pnl_col), errors="coerce").fillna(pd.to_numeric(df.get("gross_pnl"), errors="coerce")).fillna(0.0)
    df["holding_minutes_num"] = pd.to_numeric(df.get("holding_minutes"), errors="coerce")
    df["entry_slippage_bps_num"] = pd.to_numeric(df.get("entry_slippage_bps"), errors="coerce")
    df["net_return_bps_num"] = pd.to_numeric(df.get("net_return_bps"), errors="coerce")
    df["exit_reason"] = df.get("exit_reason", "-").fillna("-").astype(str)
    df["exit_reason_label"] = df["exit_reason"].map(lambda x: EXIT_REASON_LABELS.get(x, x))
    df["side"] = df.get("side", "-").fillna("-").astype(str)
    df["signal_mode"] = df.get("signal_mode", "-").fillna("-").astype(str)
    df["signal_mode_label"] = df["signal_mode"].map(lambda x: SIGNAL_MODE_LABELS.get(x, x or "未知"))
    df["alpha_version"] = df.get("alpha_version", "-").fillna("-").astype(str)
    df["code_version"] = df.get("code_version", "-").fillna("-").astype(str)
    df["config_version"] = df.get("config_version", "-").fillna("-").astype(str)
    df["win"] = df["pnl_used"] > 0
    df["is_external"] = ~df["exit_reason"].isin(NATURAL_EXIT_REASONS)
    df["signal_timestamp_dt"] = pd.to_datetime(df.get("signal_timestamp"), utc=True, errors="coerce")
    df["entry_time_dt"] = pd.to_datetime(df.get("entry_time"), utc=True, errors="coerce")
    df["exit_time_dt"] = pd.to_datetime(df.get("exit_time"), utc=True, errors="coerce")
    return df.sort_values(["exit_time_dt", "entry_time_dt", "signal_timestamp_dt"], na_position="last").reset_index(drop=True)


def summarize_closed_trades(rows: list[dict]) -> tuple[dict[str, float | int | str], pd.DataFrame, pd.DataFrame]:
    df = prepare_closed_trade_df(rows)
    if df.empty:
        empty = pd.DataFrame()
        return {
            "closed_count": 0,
            "total_pnl": 0.0,
            "win_rate": 0.0,
            "avg_hold_minutes": 0.0,
            "tp_hits": 0,
            "sl_hits": 0,
            "timeout_hits": 0,
            "other_exit_summary": "无",
            "external_interventions": 0,
        }, empty, empty

    other_exit_counts = (
        df.loc[~df["exit_reason"].isin(NATURAL_EXIT_REASONS), "exit_reason"]
        .value_counts()
        .to_dict()
    )
    other_exit_parts = [
        f"{EXIT_REASON_LABELS.get(reason, reason)} {int(count)}"
        for reason, count in other_exit_counts.items()
        if int(count) > 0
    ]

    summary = {
        "closed_count": int(len(df)),
        "total_pnl": float(df["pnl_used"].sum()),
        "win_rate": float(df["win"].mean()) if len(df) else 0.0,
        "avg_hold_minutes": float(df["holding_minutes_num"].dropna().mean()) if df["holding_minutes_num"].notna().any() else 0.0,
        "tp_hits": int((df["exit_reason"] == "take_profit").sum()),
        "sl_hits": int((df["exit_reason"] == "stop_loss").sum()),
        "timeout_hits": int(df["exit_reason"].isin(["timeout_market", "timeout_close"]).sum()),
        "other_exit_summary": " / ".join(other_exit_parts) if other_exit_parts else "无",
        "external_interventions": int(df["is_external"].sum()),
    }

    side_df = (
        df.groupby("side", dropna=False)
        .agg(
            closed_trades=("side", "size"),
            pnl=("pnl_used", "sum"),
            win_rate=("win", "mean"),
            avg_hold_minutes=("holding_minutes_num", "mean"),
        )
        .reset_index()
    )
    if not side_df.empty:
        side_df["win_rate_pct"] = side_df["win_rate"] * 100.0
        side_df = side_df[["side", "closed_trades", "pnl", "win_rate_pct", "avg_hold_minutes"]]

    exit_df = (
        df.groupby(["exit_reason", "exit_reason_label"], dropna=False)
        .agg(
            closed_trades=("exit_reason", "size"),
            pnl=("pnl_used", "sum"),
            avg_pnl=("pnl_used", "mean"),
            win_rate=("win", "mean"),
            avg_net_return_bps=("net_return_bps_num", "mean"),
            avg_entry_slippage_bps=("entry_slippage_bps_num", "mean"),
            avg_hold_minutes=("holding_minutes_num", "mean"),
        )
        .reset_index()
        .sort_values(["closed_trades", "pnl"], ascending=[False, True])
    )
    if not exit_df.empty:
        exit_df["win_rate_pct"] = exit_df["win_rate"] * 100.0
        exit_df = exit_df[["exit_reason_label", "closed_trades", "pnl", "avg_pnl", "win_rate_pct", "avg_net_return_bps", "avg_entry_slippage_bps", "avg_hold_minutes"]]
    return summary, side_df, exit_df


def summarize_closed_by_signal_mode(rows: list[dict]) -> pd.DataFrame:
    df = prepare_closed_trade_df(rows)
    if df.empty:
        return pd.DataFrame()
    mode_df = (
        df.groupby(["signal_mode", "signal_mode_label"], dropna=False)
        .agg(
            closed_trades=("signal_mode", "size"),
            pnl=("pnl_used", "sum"),
            avg_pnl=("pnl_used", "mean"),
            win_rate=("win", "mean"),
            avg_net_return_bps=("net_return_bps_num", "mean"),
            avg_entry_slippage_bps=("entry_slippage_bps_num", "mean"),
            avg_hold_minutes=("holding_minutes_num", "mean"),
        )
        .reset_index()
    )
    if mode_df.empty:
        return mode_df
    mode_df["win_rate_pct"] = mode_df["win_rate"] * 100.0
    order = {"preview": 0, "official_close": 1, "未知": 9}
    mode_df["sort_key"] = mode_df["signal_mode_label"].map(lambda x: order.get(str(x), 5))
    mode_df = mode_df.sort_values(["sort_key", "closed_trades"], ascending=[True, False])
    return mode_df[["signal_mode_label", "closed_trades", "pnl", "avg_pnl", "win_rate_pct", "avg_net_return_bps", "avg_entry_slippage_bps", "avg_hold_minutes"]]


def summarize_recent_trade_windows(rows: list[dict], windows: tuple[int, ...] = (5, 10, 20)) -> pd.DataFrame:
    df = prepare_closed_trade_df(rows)
    if df.empty:
        return pd.DataFrame()
    stats: list[dict[str, object]] = []
    for window in windows:
        part = df.tail(min(window, len(df))).copy()
        if part.empty:
            continue
        stats.append({
            "window": f"最近{min(window, len(df))}笔",
            "closed_trades": int(len(part)),
            "pnl": float(part["pnl_used"].sum()),
            "avg_pnl": float(part["pnl_used"].mean()),
            "win_rate_pct": float(part["win"].mean() * 100.0),
            "avg_net_return_bps": float(part["net_return_bps_num"].dropna().mean()) if part["net_return_bps_num"].notna().any() else None,
            "avg_entry_slippage_bps": float(part["entry_slippage_bps_num"].dropna().mean()) if part["entry_slippage_bps_num"].notna().any() else None,
            "external_exits": int(part["is_external"].sum()),
        })
    return pd.DataFrame(stats)


def summarize_forward_observation_window(closed_rows: list[dict], event_rows: list[dict], target_trades: int = 20) -> tuple[dict[str, object], pd.DataFrame]:
    observation_cfg = load_json(PH6_OBSERVATION_WINDOW_PATH, {})
    df = prepare_closed_trade_df(closed_rows)

    if isinstance(observation_cfg, dict) and observation_cfg:
        start_dt = parse_ts(observation_cfg.get("started_at_utc"))
        target = int(observation_cfg.get("target_closed_trades", target_trades) or target_trades)
        baseline_closed = observation_cfg.get("baseline_closed_trades_total")
        try:
            baseline_closed = int(baseline_closed) if baseline_closed is not None else None
        except Exception:
            baseline_closed = None
        summary: dict[str, object] = {
            "label": observation_cfg.get("label"),
            "start_time": start_dt.strftime("%Y-%m-%dT%H:%M:%SZ") if start_dt is not None else observation_cfg.get("started_at_utc"),
            "target_trades": int(target),
            "closed_trades": 0,
            "remaining_trades": int(target),
            "progress_pct": 0.0,
            "pnl": 0.0,
            "win_rate": 0.0,
            "avg_entry_slippage_bps": None,
            "baseline_closed_trades_total": baseline_closed,
            "live_universe": observation_cfg.get("live_universe", []),
            "note": str(observation_cfg.get("note") or "当前观察窗从手动重置锚点开始计数；建议至少观察满 20 笔再下结论。"),
        }
        if df.empty:
            summary["note"] = "新观察窗已开始，但还没有新平仓样本。"
            return summary, pd.DataFrame()
        if baseline_closed is not None and baseline_closed >= 0:
            cohort = df.iloc[min(baseline_closed, len(df)):].copy()
        elif start_dt is not None:
            anchor_series = df["entry_time_dt"].where(df["entry_time_dt"].notna(), df["signal_timestamp_dt"])
            cohort = df[anchor_series >= pd.Timestamp(start_dt)].copy()
        else:
            cohort = df.copy()
        summary["closed_trades"] = int(len(cohort))
        summary["remaining_trades"] = max(0, int(target) - int(len(cohort)))
        summary["progress_pct"] = min(100.0, float(len(cohort)) / float(target) * 100.0) if target > 0 else 100.0
        if cohort.empty:
            summary["note"] = "新观察窗已开始，但还没有新平仓样本。"
            return summary, pd.DataFrame()
        summary["pnl"] = float(cohort["pnl_used"].sum())
        summary["win_rate"] = float(cohort["win"].mean())
        summary["avg_entry_slippage_bps"] = float(cohort["entry_slippage_bps_num"].dropna().mean()) if cohort["entry_slippage_bps_num"].notna().any() else None
        cohort_df = cohort[[
            "signal_timestamp",
            "entry_time",
            "symbol",
            "signal_mode_label",
            "side",
            "entry_slippage_bps_num",
            "exit_reason_label",
            "pnl_used",
            "code_version",
            "config_version",
        ]].copy().tail(target)
        cohort_df = cohort_df.rename(columns={
            "signal_timestamp": "signal_timestamp",
            "entry_time": "entry_time",
            "symbol": "symbol",
            "signal_mode_label": "signal_mode",
            "side": "side",
            "entry_slippage_bps_num": "entry_slippage_bps",
            "exit_reason_label": "exit_reason",
            "pnl_used": "pnl",
            "code_version": "code_version",
            "config_version": "config_version",
        })
        return summary, cohort_df

    event_rows = event_rows if isinstance(event_rows, list) else []
    start_candidates: list[datetime] = []
    for row in event_rows:
        if not isinstance(row, dict) or str(row.get("event_type") or "") != "SignalReceived":
            continue
        payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
        if str(payload.get("alpha_version") or "") != "canary_preview_v2":
            continue
        ts = parse_ts(row.get("timestamp")) or parse_ts(payload.get("timestamp"))
        if ts is not None:
            start_candidates.append(ts)
    start_dt = min(start_candidates) if start_candidates else None
    summary = {
        "start_time": start_dt.strftime("%Y-%m-%dT%H:%M:%SZ") if start_dt is not None else None,
        "target_trades": int(target_trades),
        "closed_trades": 0,
        "remaining_trades": int(target_trades),
        "progress_pct": 0.0,
        "pnl": 0.0,
        "win_rate": 0.0,
        "avg_entry_slippage_bps": None,
        "note": "尚未观察到 canary_preview_v2 的 live 信号。" if start_dt is None else "",
    }
    if start_dt is None:
        return summary, pd.DataFrame()
    if df.empty:
        summary["note"] = "修复后观察窗已开始，但还没有新平仓样本。"
        return summary, pd.DataFrame()
    anchor_series = df["entry_time_dt"].where(df["entry_time_dt"].notna(), df["signal_timestamp_dt"])
    cohort = df[anchor_series >= pd.Timestamp(start_dt)].copy()
    summary["closed_trades"] = int(len(cohort))
    summary["remaining_trades"] = max(0, int(target_trades) - int(len(cohort)))
    summary["progress_pct"] = min(100.0, float(len(cohort)) / float(target_trades) * 100.0) if target_trades > 0 else 100.0
    if cohort.empty:
        summary["note"] = "修复后观察窗已开始，但还没有新平仓样本。"
        return summary, pd.DataFrame()
    summary["pnl"] = float(cohort["pnl_used"].sum())
    summary["win_rate"] = float(cohort["win"].mean())
    summary["avg_entry_slippage_bps"] = float(cohort["entry_slippage_bps_num"].dropna().mean()) if cohort["entry_slippage_bps_num"].notna().any() else None
    summary["note"] = "从第一条 canary_preview_v2 live 信号开始计数；建议至少观察满 20 笔再下结论。"
    cohort_df = cohort[[
        "signal_timestamp",
        "entry_time",
        "symbol",
        "signal_mode_label",
        "side",
        "entry_slippage_bps_num",
        "exit_reason_label",
        "pnl_used",
        "code_version",
        "config_version",
    ]].copy().tail(target_trades)
    cohort_df = cohort_df.rename(columns={
        "signal_timestamp": "signal_timestamp",
        "entry_time": "entry_time",
        "symbol": "symbol",
        "signal_mode_label": "signal_mode",
        "side": "side",
        "entry_slippage_bps_num": "entry_slippage_bps",
        "exit_reason_label": "exit_reason",
        "pnl_used": "pnl",
        "code_version": "code_version",
        "config_version": "config_version",
    })
    return summary, cohort_df


def summarize_signal_health(signal_rows: list[dict], closed_rows: list[dict], reject_rows: list[dict]) -> tuple[dict[str, float | int], pd.DataFrame]:
    sig_df = pd.DataFrame(signal_rows)
    closed_df = pd.DataFrame(closed_rows)
    rej_df = pd.DataFrame(reject_rows)

    symbols = sorted({str(v).upper() for v in sig_df.get("symbol", pd.Series(dtype=str)).dropna().tolist()} | {str(v).upper() for v in closed_df.get("symbol", pd.Series(dtype=str)).dropna().tolist()})
    rows: list[dict[str, object]] = []
    for symbol in symbols:
        sig_part = sig_df[sig_df.get("symbol").astype(str).str.upper() == symbol] if not sig_df.empty and "symbol" in sig_df.columns else pd.DataFrame()
        closed_part = closed_df[closed_df.get("symbol").astype(str).str.upper() == symbol] if not closed_df.empty and "symbol" in closed_df.columns else pd.DataFrame()
        rej_part = rej_df[rej_df.get("symbol").astype(str).str.upper() == symbol] if not rej_df.empty and "symbol" in rej_df.columns else pd.DataFrame()
        pnl = pd.to_numeric(closed_part.get("net_pnl"), errors="coerce") if not closed_part.empty and "net_pnl" in closed_part.columns and closed_part["net_pnl"].notna().any() else pd.to_numeric(closed_part.get("gross_pnl"), errors="coerce")
        if pnl is None:
            pnl = pd.Series(dtype=float)
        rows.append(
            {
                "symbol": symbol,
                "signals": int(len(sig_part)),
                "long_signals": int((sig_part.get("side") == "long").sum()) if not sig_part.empty and "side" in sig_part.columns else 0,
                "short_signals": int((sig_part.get("side") == "short").sum()) if not sig_part.empty and "side" in sig_part.columns else 0,
                "closed_trades": int(len(closed_part)),
                "rejections": int(len(rej_part)),
                "pnl": float(pnl.fillna(0.0).sum()) if hasattr(pnl, "fillna") else 0.0,
            }
        )
    symbol_df = pd.DataFrame(rows)
    summary = {
        "signal_count": int(len(sig_df)),
        "long_signals": int((sig_df.get("side") == "long").sum()) if not sig_df.empty and "side" in sig_df.columns else 0,
        "short_signals": int((sig_df.get("side") == "short").sum()) if not sig_df.empty and "side" in sig_df.columns else 0,
        "rejections": int(len(rej_df)),
    }
    return summary, symbol_df


def build_signal_trigger_df(signal_rows: list[dict], state: dict, reject_rows: list[dict], tail: int = 12) -> pd.DataFrame:
    if not isinstance(signal_rows, list) or not signal_rows:
        return pd.DataFrame()
    state = state if isinstance(state, dict) else {}
    reject_rows = reject_rows if isinstance(reject_rows, list) else []

    reject_map: dict[str, str] = {}
    for row in reject_rows:
        sid = str(row.get("signal_id") or "")
        if not sid:
            continue
        reason = "-"
        risk = row.get("risk")
        if isinstance(risk, dict):
            reason = str(risk.get("reason") or "-")
        reject_map[sid] = reason

    pending_map = {str(row.get("signal_id") or ""): row for row in (state.get("pending_entries") or []) if isinstance(row, dict)}
    live_map = {str(row.get("signal_id") or ""): row for row in (state.get("live_positions") or []) if isinstance(row, dict)}
    closed_map = {str(row.get("signal_id") or ""): row for row in (state.get("closed_trades") or []) if isinstance(row, dict)}
    seen_ids = {str(x) for x in (state.get("seen_signal_ids") or [])}

    rows: list[dict[str, object]] = []
    for row in signal_rows[-tail:]:
        sid = str(row.get("signal_id") or "")
        status = "未处理"
        detail = "-"
        if sid in live_map:
            status = "已触发交易"
            detail = "已开仓，当前仍在持仓中"
        elif sid in pending_map:
            status = "已触发交易"
            detail = "已生成入场单，等待成交"
        elif sid in closed_map:
            status = "已触发交易"
            detail = f"已平仓：{closed_map[sid].get('exit_reason') or '-'}"
        elif sid in reject_map:
            status = "未触发交易"
            detail = f"风控拒绝：{reject_map[sid]}"
        elif sid in seen_ids:
            status = "已处理未下单"
            detail = "策略已消费该信号，但本轮没有形成交易"

        rows.append(
            {
                "信号时间": fmt_ts_bj(row.get("timestamp")),
                "标的": row.get("symbol"),
                "方向": row.get("side"),
                "信号价": row.get("signal_price"),
                "是否触发交易": status,
                "结果说明": detail,
            }
        )
    return pd.DataFrame(rows)


def build_preview_parity_audit(event_rows: list[dict], ttl_minutes: int, lookback_hours: int = 24, tail: int = 12) -> tuple[dict[str, object], pd.DataFrame, pd.DataFrame]:
    now_utc = datetime.now(timezone.utc)
    cutoff = now_utc - timedelta(hours=lookback_hours)
    rows = [row for row in (event_rows or []) if isinstance(row, dict)]
    rows = [row for row in rows if (parse_ts(row.get("timestamp")) or datetime.min.replace(tzinfo=timezone.utc)) >= cutoff]
    rows.sort(key=lambda r: parse_ts(r.get("timestamp")) or datetime.min.replace(tzinfo=timezone.utc))

    signal_events: list[dict[str, object]] = []
    for row in rows:
        if str(row.get("event_type") or "") != "SignalReceived":
            continue
        payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
        meta = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
        signal_mode = str(meta.get("signal_mode") or "")
        if signal_mode not in {"preview_unclosed15m", "official_close"}:
            continue
        signal_events.append({
            "event_time": row.get("timestamp"),
            "signal_id": payload.get("signal_id"),
            "symbol": payload.get("symbol"),
            "side": payload.get("side"),
            "signal_time": payload.get("timestamp"),
            "signal_confirmed_at": payload.get("signal_confirmed_at") or meta.get("signal_confirmed_at_override"),
            "signal_mode": signal_mode,
            "bucket_start": meta.get("bucket_start") or payload.get("timestamp"),
            "bucket_close_at": meta.get("bucket_close_at"),
            "first_seen_at": meta.get("first_seen_at") or payload.get("timestamp"),
            "expired_at": meta.get("expired_at"),
            "signal_price": payload.get("signal_price"),
        })

    official_by_key: dict[tuple[str, str, str], dict[str, object]] = {}
    preview_rows: list[dict[str, object]] = []
    for row in signal_events:
        key = (str(row.get("symbol") or "").upper(), str(row.get("side") or "").lower(), str(row.get("bucket_start") or ""))
        if row.get("signal_mode") == "official_close":
            official_by_key[key] = row
        elif row.get("signal_mode") == "preview_unclosed15m":
            preview_rows.append(row)

    opened_by_id: dict[str, dict] = {}
    closed_by_id: dict[str, dict] = {}
    reject_by_id: dict[str, str] = {}
    for row in rows:
        payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
        sid = str(payload.get("signal_id") or row.get("signal_id") or "")
        if not sid:
            continue
        event_type = str(row.get("event_type") or "")
        if event_type == "PositionOpened":
            opened_by_id[sid] = payload
        elif event_type == "PositionClosed":
            closed_by_id[sid] = payload
        elif event_type == "RiskRejected":
            risk = payload.get("risk") if isinstance(payload.get("risk"), dict) else {}
            reject_by_id[sid] = str(risk.get("reason") or row.get("message") or "-")

    lifecycle_rows: list[dict[str, object]] = []
    lead_minutes: list[float] = []
    preview_confirmed = 0
    preview_traded = 0
    preview_only = 0

    for row in preview_rows[-tail:]:
        key = (str(row.get("symbol") or "").upper(), str(row.get("side") or "").lower(), str(row.get("bucket_start") or ""))
        official = official_by_key.get(key)
        first_seen_dt = parse_ts(row.get("first_seen_at"))
        bucket_close_dt = parse_ts(row.get("bucket_close_at"))
        if bucket_close_dt is None:
            bs = parse_ts(row.get("bucket_start"))
            bucket_close_dt = bs + timedelta(minutes=15) if bs is not None else None
        official_dt = parse_ts(official.get("signal_confirmed_at")) if official else None
        expired_dt = parse_ts(row.get("expired_at"))
        if expired_dt is None and first_seen_dt is not None:
            expired_dt = first_seen_dt + timedelta(minutes=ttl_minutes)
        confirmed_state = "待收盘"
        if official_dt is not None:
            confirmed_state = "同向确认"
            preview_confirmed += 1
            if first_seen_dt is not None:
                lead_minutes.append((official_dt - first_seen_dt).total_seconds() / 60.0)
        elif bucket_close_dt is not None and bucket_close_dt <= now_utc:
            confirmed_state = "preview_only"
            preview_only += 1

        sid = str(row.get("signal_id") or "")
        outcome = "未消费"
        if sid in closed_by_id:
            outcome = f"已平仓：{closed_by_id[sid].get('exit_reason') or '-'}"
            preview_traded += 1
        elif sid in opened_by_id:
            outcome = "已开仓，当前持仓中"
            preview_traded += 1
        elif sid in reject_by_id:
            outcome = f"风控拒绝：{reject_by_id[sid]}"

        lifecycle_rows.append({
            "标的": row.get("symbol"),
            "方向": row.get("side"),
            "15m bucket": fmt_ts_bj(row.get("bucket_start")),
            "preview 首次出现": fmt_ts_bj(row.get("first_seen_at")),
            "有效期截止": fmt_ts_bj(expired_dt.isoformat().replace('+00:00', 'Z')) if expired_dt else "-",
            "official 收盘确认": fmt_ts_bj(official.get("signal_confirmed_at")) if official else "-",
            "收盘是否确认": confirmed_state,
            "领先分钟": round((official_dt - first_seen_dt).total_seconds() / 60.0, 2) if official_dt and first_seen_dt else None,
            "live 结果": outcome,
        })

    preview_keys = {(str(row.get("symbol") or "").upper(), str(row.get("side") or "").lower(), str(row.get("bucket_start") or "")) for row in preview_rows}
    mismatch_rows: list[dict[str, object]] = []
    official_without_preview = 0
    for key, row in sorted(official_by_key.items(), key=lambda kv: parse_ts(kv[1].get("signal_confirmed_at")) or datetime.min.replace(tzinfo=timezone.utc)):
        if key in preview_keys:
            continue
        official_without_preview += 1
        sid = str(row.get("signal_id") or "")
        outcome = "-"
        if sid in closed_by_id:
            outcome = f"已平仓：{closed_by_id[sid].get('exit_reason') or '-'}"
        elif sid in opened_by_id:
            outcome = "已开仓/已成交"
        elif sid in reject_by_id:
            outcome = f"风控拒绝：{reject_by_id[sid]}"
        mismatch_rows.append({
            "类型": "official_without_preview",
            "标的": row.get("symbol"),
            "方向": row.get("side"),
            "15m bucket": fmt_ts_bj(row.get("bucket_start")),
            "preview 首次出现": "-",
            "official 收盘确认": fmt_ts_bj(row.get("signal_confirmed_at")),
            "说明": outcome,
        })

    for row in preview_rows:
        key = (str(row.get("symbol") or "").upper(), str(row.get("side") or "").lower(), str(row.get("bucket_start") or ""))
        if key in official_by_key:
            continue
        bucket_close_dt = parse_ts(row.get("bucket_close_at"))
        if bucket_close_dt is None:
            bs = parse_ts(row.get("bucket_start"))
            bucket_close_dt = bs + timedelta(minutes=15) if bs is not None else None
        if bucket_close_dt is None or bucket_close_dt > now_utc:
            continue
        mismatch_rows.append({
            "类型": "preview_only",
            "标的": row.get("symbol"),
            "方向": row.get("side"),
            "15m bucket": fmt_ts_bj(row.get("bucket_start")),
            "preview 首次出现": fmt_ts_bj(row.get("first_seen_at")),
            "official 收盘确认": "-",
            "说明": "bucket 收盘后未见同向 official 确认",
        })

    summary = {
        "preview_signals": len(preview_rows),
        "preview_confirmed_at_close": preview_confirmed,
        "preview_only": preview_only,
        "official_without_preview": official_without_preview,
        "preview_traded": preview_traded,
        "avg_preview_lead_minutes": (sum(lead_minutes) / len(lead_minutes)) if lead_minutes else None,
    }
    lifecycle_df = pd.DataFrame(lifecycle_rows).tail(tail)
    mismatch_df = pd.DataFrame(mismatch_rows).tail(tail)
    return summary, lifecycle_df, mismatch_df


def directional_entry_slippage_bps(*, signal_price: object, entry_price: object, side: object) -> float | None:
    sig = pd.to_numeric(pd.Series([signal_price]), errors="coerce").iloc[0]
    ent = pd.to_numeric(pd.Series([entry_price]), errors="coerce").iloc[0]
    if pd.isna(sig) or pd.isna(ent) or float(sig) <= 0:
        return None
    base = (float(ent) - float(sig)) / float(sig) * 10000.0
    return base if str(side or "").lower() == "long" else -base


def enrich_trade_rows_with_signal_context(rows: list[dict], signal_rows: list[dict], event_rows: list[dict] | None = None) -> list[dict]:
    signal_rows = signal_rows if isinstance(signal_rows, list) else []
    event_rows = event_rows if isinstance(event_rows, list) else []
    signal_map: dict[str, dict] = {}
    fallback_map: dict[tuple[str, str, str], dict] = {}

    def register_signal_like(row: dict, *, timestamp_key: str = "timestamp") -> None:
        sid = str(row.get("signal_id") or "")
        if sid:
            signal_map[sid] = row
        fallback_key = (
            str(row.get("symbol") or "").upper(),
            str(row.get("side") or "").lower(),
            str(row.get(timestamp_key) or ""),
        )
        if fallback_key[0] and fallback_key[2]:
            fallback_map[fallback_key] = row

    for row in signal_rows:
        if isinstance(row, dict):
            register_signal_like(row)

    for row in event_rows:
        if not isinstance(row, dict):
            continue
        if str(row.get("event_type") or "") != "SignalReceived":
            continue
        payload = row.get("payload")
        if not isinstance(payload, dict):
            continue
        register_signal_like(payload)

    out: list[dict] = []
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, dict):
            continue
        item = dict(row)
        signal_price = item.get("signal_price")
        signal_ts = item.get("signal_timestamp")
        sid = str(item.get("signal_id") or "")
        matched = signal_map.get(sid)
        if matched is None:
            matched = fallback_map.get((str(item.get("symbol") or "").upper(), str(item.get("side") or "").lower(), str(signal_ts or "")))
        if isinstance(matched, dict):
            if signal_price is None or pd.isna(signal_price):
                signal_price = matched.get("signal_price")
                item["signal_price"] = signal_price
            if not signal_ts or signal_ts == "-" or pd.isna(signal_ts):
                item["signal_timestamp"] = matched.get("timestamp")
            item["alpha_version"] = matched.get("alpha_version") or item.get("alpha_version")
            meta = matched.get("metadata") if isinstance(matched.get("metadata"), dict) else {}
            item["signal_mode"] = meta.get("signal_mode") or item.get("signal_mode")
            item["bucket_start"] = meta.get("bucket_start") or item.get("bucket_start")
            item["first_seen_at"] = meta.get("first_seen_at") or item.get("first_seen_at")
            item["confirmed_at_close"] = meta.get("confirmed_at_close") if "confirmed_at_close" in meta else item.get("confirmed_at_close")
        item["entry_slippage_bps"] = directional_entry_slippage_bps(
            signal_price=item.get("signal_price"),
            entry_price=item.get("entry_price"),
            side=item.get("side"),
        )
        out.append(item)
    return out


def main() -> None:
    ensure_dir(SITE_DIR)

    ph1_status = load_json(PH1_STATUS_PATH, {})
    ph1_run = load_json(PH1_RUN_SUMMARY_PATH, {})
    ph1_intentions = load_json(PH1_INTENTIONS_PATH, [])
    ph1_rejections = load_json(PH1_REJECTIONS_PATH, [])
    ph1_symbol_state = load_json(PH1_SYMBOL_STATE_PATH, [])

    ph2_status = load_json(PH2_STATUS_PATH, {})
    ph2_run = load_json(PH2_RUN_SUMMARY_PATH, {})
    ph2_orders = load_json(PH2_ORDERS_PATH, [])
    ph2_rejections = load_json(PH2_REJECTIONS_PATH, [])
    ph2_chains = load_json(PH2_CHAINS_PATH, [])
    ph2_symbol_state = load_json(PH2_SYMBOL_STATE_PATH, [])
    ph2_packets = load_json(PH2_PACKET_PATH, [])

    ph3_status = load_json(PH3_STATUS_PATH, {})
    ph3_run = load_json(PH3_RUN_SUMMARY_PATH, {})
    ph3_venue_health = load_json(PH3_VENUE_HEALTH_PATH, [])
    ph3_account_snapshot = load_json(PH3_ACCOUNT_SNAPSHOT_PATH, {})
    ph3_ledger = load_json(PH3_LEDGER_PATH, [])
    ph3_packets = load_json(PH3_PACKET_PATH, {})

    ph4_run = load_json(PH4_RUN_SUMMARY_PATH, {})
    ph4_receipt = load_json(PH4_RECEIPT_PATH, {})
    ph4_packet = load_json(PH4_PACKET_PATH, {})

    ph5_status = load_json(PH5_STATUS_PATH, {})
    ph5_run = load_json(PH5_RUN_SUMMARY_PATH, {})
    ph5_receipt = load_json(PH5_RECEIPT_PATH, {})
    ph5_packet = load_json(PH5_PACKET_PATH, {})

    ph6_status = load_json(PH6_STATUS_PATH, {})
    ph6_run = load_json(PH6_RUN_SUMMARY_PATH, {})
    ph6_orders = load_json(PH6_ORDERS_PATH, [])
    ph6_positions = load_json(PH6_POSITIONS_PATH, [])
    ph6_closed = load_json(PH6_CLOSED_PATH, [])
    ph6_signals = load_json(PH6_SIGNALS_PATH, [])
    ph6_events = load_jsonl(PH6_EVENTS_PATH, [])
    ph6_rejections = load_json(PH6_REJECTIONS_PATH, [])
    ph6_state = load_json(PH6_STATE_PATH, {})
    ph6_warnings = load_json(PH6_WARNINGS_PATH, [])
    ph6_packet = load_json(PH6_PACKET_PATH, {})
    ph6_smallcap_activity_cache = load_json(PH6_SMALLCAP_ACTIVITY_CACHE_PATH, {})
    shadow_beat_run = load_json(SHADOW_BEAT_RUN_SUMMARY_PATH, {})
    shadow_beat_status = load_json(SHADOW_BEAT_STATUS_PATH, {})
    shadow_beat_paper = load_json(SHADOW_BEAT_PAPER_SUMMARY_PATH, {})
    shadow_beat_trades = load_json(SHADOW_BEAT_PAPER_TRADES_PATH, [])
    shadow_global_run = load_json(SHADOW_GLOBAL_RUN_SUMMARY_PATH, {})
    shadow_global_status = load_json(SHADOW_GLOBAL_STATUS_PATH, {})
    shadow_global_paper = load_json(SHADOW_GLOBAL_PAPER_SUMMARY_PATH, {})
    shadow_global_trades = load_json(SHADOW_GLOBAL_PAPER_TRADES_PATH, [])
    global_live_run = load_json(GLOBAL_LIVE_RUN_SUMMARY_PATH, {})
    global_live_status = load_json(GLOBAL_LIVE_STATUS_PATH, {})
    global_live_compare_df = pd.read_csv(GLOBAL_LIVE_COMPARE_PATH) if GLOBAL_LIVE_COMPARE_PATH.exists() and GLOBAL_LIVE_COMPARE_PATH.stat().st_size > 0 else pd.DataFrame()

    cfg = {}
    if CONFIG_PATH.exists():
        try:
            cfg = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}
        except Exception:
            cfg = {}

    phase6_cfg = cfg.get("phase6", {}) if isinstance(cfg, dict) else {}
    phase6_smallcap_cfg = phase6_cfg.get("smallcap", {}) if isinstance(phase6_cfg, dict) else {}
    phase6_smallcap_symbols = {str(symbol).upper() for symbol in (phase6_smallcap_cfg.get("symbols", []) if isinstance(phase6_smallcap_cfg, dict) else [])}
    phase6_core_symbols = [str(symbol).upper() for symbol in (cfg.get("universe", {}) or {}).get("symbols", []) if str(symbol).upper() not in phase6_smallcap_symbols]
    ph6_orders = annotate_bucket_rows(ph6_orders, phase6_smallcap_symbols)
    ph6_positions = annotate_bucket_rows(ph6_positions, phase6_smallcap_symbols)
    ph6_closed = annotate_bucket_rows(ph6_closed, phase6_smallcap_symbols)
    ph6_signals = enrich_signal_rows(ph6_signals, phase6_smallcap_symbols)
    ph6_rejections = annotate_bucket_rows(ph6_rejections, phase6_smallcap_symbols)
    ph6_warnings = annotate_bucket_rows(ph6_warnings, phase6_smallcap_symbols)
    ph6_positions = enrich_trade_rows_with_signal_context(ph6_positions, ph6_signals, ph6_events)
    ph6_closed = enrich_trade_rows_with_signal_context(ph6_closed, ph6_signals, ph6_events)

    ph1_intentions_df = trim_df(ph1_intentions, ["created_at", "symbol", "side", "target_price", "ttl_minutes", "intention_id"])
    ph1_reject_df = pd.DataFrame(ph1_rejections)
    if not ph1_reject_df.empty:
        cols = [c for c in ["timestamp", "symbol", "side", "signal_id"] if c in ph1_reject_df.columns]
        if "risk" in ph1_reject_df.columns:
            ph1_reject_df["reason"] = ph1_reject_df["risk"].apply(lambda x: x.get("reason") if isinstance(x, dict) else "-")
            cols.append("reason")
        ph1_reject_df = ph1_reject_df[cols].tail(20)
    ph1_state_df = pd.DataFrame(ph1_symbol_state)

    ph2_orders_df = trim_df(ph2_orders, ["submit_at", "symbol", "side", "status", "submit_mode", "broker_order_id", "venue_ref"])
    ph2_chain_df = trim_df(ph2_chains, ["symbol", "stage", "complete", "capital_deployed", "broker_order_id", "trace_id"])
    ph2_reject_df = pd.DataFrame(ph2_rejections)
    if not ph2_reject_df.empty:
        cols = [c for c in ["timestamp", "symbol", "side", "signal_id"] if c in ph2_reject_df.columns]
        if "risk" in ph2_reject_df.columns:
            ph2_reject_df["reason"] = ph2_reject_df["risk"].apply(lambda x: x.get("reason") if isinstance(x, dict) else "-")
            cols.append("reason")
        ph2_reject_df = ph2_reject_df[cols].tail(20)
    ph2_state_df = pd.DataFrame(ph2_symbol_state)
    ph2_packet_excerpt = json.dumps(ph2_packets[-1], ensure_ascii=False, indent=2) if isinstance(ph2_packets, list) and ph2_packets else "尚无 operator packet。"

    ph3_venue_df = pd.DataFrame(ph3_venue_health)
    ph3_ledger_df = trim_df(ph3_ledger, ["symbol", "side", "status", "ttl_minutes", "ttl_state", "seconds_remaining", "receipt_chain_stage", "capital_deployed", "broker_order_id"], tail=40)
    ph3_account_excerpt = json.dumps(ph3_account_snapshot, ensure_ascii=False, indent=2) if ph3_account_snapshot else "尚无 account snapshot。"
    ph3_packet_excerpt = json.dumps(ph3_packets, ensure_ascii=False, indent=2) if ph3_packets else "尚无 phase3 operator packet。"

    ph4_receipt_excerpt = json.dumps(ph4_receipt, ensure_ascii=False, indent=2) if ph4_receipt else "尚无 phase4 receipt。"
    ph4_packet_excerpt = json.dumps(ph4_packet, ensure_ascii=False, indent=2) if ph4_packet else "尚无 phase4 operator packet。"

    ph5_receipt_excerpt = json.dumps(ph5_receipt, ensure_ascii=False, indent=2) if ph5_receipt else "尚无 phase5 receipt。"
    ph5_packet_excerpt = json.dumps(ph5_packet, ensure_ascii=False, indent=2) if ph5_packet else "尚无 phase5 operator packet。"

    ph6_orders_df = trim_df(ph6_orders, ["timestamp", "symbol", "symbol_bucket", "side", "order_role", "order_type", "price", "qty", "status", "exchange_order_id"], tail=40)
    ph6_positions_df = trim_df(ph6_positions, ["signal_timestamp", "symbol", "symbol_bucket", "side", "signal_price", "entry_time", "entry_price", "entry_slippage_bps", "entry_qty", "tp_price", "sl_price", "timeout_at"], tail=20)
    ph6_closed_df = trim_df(ph6_closed, ["signal_timestamp", "symbol", "symbol_bucket", "side", "signal_price", "entry_time", "entry_price", "entry_slippage_bps", "exit_time", "exit_price", "qty", "holding_minutes", "exit_reason", "gross_pnl", "net_pnl"], tail=40)
    ph6_signal_df = trim_df(ph6_signals, ["timestamp", "bucket_start", "first_seen_at", "expired_at", "signal_mode", "symbol", "symbol_bucket", "side", "signal_price", "confirmed_at_close", "official_confirmed_at"], tail=40)
    ph6_reject_df = pd.DataFrame(ph6_rejections)
    if not ph6_reject_df.empty:
        cols = [c for c in ["timestamp", "symbol", "symbol_bucket", "side", "signal_id"] if c in ph6_reject_df.columns]
        if "risk" in ph6_reject_df.columns:
            ph6_reject_df["reason"] = ph6_reject_df["risk"].apply(lambda x: x.get("reason") if isinstance(x, dict) else "-")
            ph6_reject_df["selected_symbol"] = ph6_reject_df["risk"].apply(lambda x: x.get("selected_symbol") if isinstance(x, dict) else "-")
            ph6_reject_df["signal_strength"] = ph6_reject_df["risk"].apply(lambda x: x.get("signal_strength") if isinstance(x, dict) else None)
            ph6_reject_df["selected_strength"] = ph6_reject_df["risk"].apply(lambda x: x.get("selected_strength") if isinstance(x, dict) else None)
            ph6_reject_df["activity_percentile"] = ph6_reject_df["risk"].apply(lambda x: ((x.get("activity") or {}).get("percentile") if isinstance(x, dict) else None))
            cols.extend(["reason", "activity_percentile", "selected_symbol", "signal_strength", "selected_strength"])
        ph6_reject_df = ph6_reject_df[cols].tail(40)
    ph6_warn_df = trim_df(ph6_warnings, ["timestamp", "symbol", "level", "message"], tail=40)
    ph6_packet_excerpt = json.dumps(ph6_packet, ensure_ascii=False, indent=2) if ph6_packet else "尚无 phase6 operator packet。"
    live_snapshot_excerpt = run_text_command(f"/usr/bin/python3 {SNAPSHOT_SCRIPT}", timeout=40)
    current_commit = run_text_command("git rev-parse --short=12 HEAD", timeout=10)
    ph6_closed_summary, ph6_side_df, ph6_exit_df = summarize_closed_trades(ph6_closed)
    ph6_live_curve_df = pd.DataFrame(ph6_closed)
    if not ph6_live_curve_df.empty:
        ph6_live_curve_df["trade_ret"] = pd.to_numeric(ph6_live_curve_df.get("net_return_bps"), errors="coerce") / 10000.0
    ph6_live_curve_card = build_equity_curve_card(
        ph6_live_curve_df,
        time_col="exit_time",
        ret_col="trade_ret",
        title="实盘累计收益曲线",
        subtitle="基于近期已平仓交易的 net_return_bps 复利累计；这里只看实盘已闭环样本。",
    )
    shadow_beat_curve_df = pd.DataFrame(shadow_beat_trades if isinstance(shadow_beat_trades, list) else [])
    if not shadow_beat_curve_df.empty:
        shadow_beat_curve_df["curve_ts"] = shadow_beat_curve_df.get("exit_ts")
        if "mark_ts" in shadow_beat_curve_df.columns:
            shadow_beat_curve_df["curve_ts"] = shadow_beat_curve_df["curve_ts"].where(shadow_beat_curve_df["curve_ts"].notna(), shadow_beat_curve_df["mark_ts"])
        if "entry_ts" in shadow_beat_curve_df.columns:
            shadow_beat_curve_df["curve_ts"] = shadow_beat_curve_df["curve_ts"].where(shadow_beat_curve_df["curve_ts"].notna(), shadow_beat_curve_df["entry_ts"])
        shadow_beat_curve_df["trade_ret"] = pd.to_numeric(shadow_beat_curve_df.get("paper_effective_net_ret"), errors="coerce")
    shadow_global_curve_df = pd.DataFrame(shadow_global_trades if isinstance(shadow_global_trades, list) else [])
    if not shadow_global_curve_df.empty:
        shadow_global_curve_df["curve_ts"] = shadow_global_curve_df.get("exit_ts")
        if "mark_ts" in shadow_global_curve_df.columns:
            shadow_global_curve_df["curve_ts"] = shadow_global_curve_df["curve_ts"].where(shadow_global_curve_df["curve_ts"].notna(), shadow_global_curve_df["mark_ts"])
        if "entry_ts" in shadow_global_curve_df.columns:
            shadow_global_curve_df["curve_ts"] = shadow_global_curve_df["curve_ts"].where(shadow_global_curve_df["curve_ts"].notna(), shadow_global_curve_df["entry_ts"])
        shadow_global_curve_df["trade_ret"] = pd.to_numeric(shadow_global_curve_df.get("paper_effective_net_ret"), errors="coerce")

    def make_strategy_series(df: pd.DataFrame, *, label: str, color: str, time_col: str, ret_col: str) -> dict[str, object]:
        if df.empty or time_col not in df.columns or ret_col not in df.columns:
            return {"label": label, "color": color, "trades": []}
        work = df[[time_col, ret_col]].copy()
        work[time_col] = pd.to_datetime(work[time_col], utc=True, errors="coerce")
        work[ret_col] = pd.to_numeric(work[ret_col], errors="coerce")
        work = work.dropna().sort_values(time_col)
        trades = [
            {"ts": ts.strftime('%Y-%m-%dT%H:%M:%SZ'), "ret": float(ret)}
            for ts, ret in zip(work[time_col].tolist(), work[ret_col].tolist())
        ]
        return {"label": label, "color": color, "trades": trades}

    strategy_compare_payload = {
        "strategies": [
            make_strategy_series(ph6_live_curve_df, label="真钱 core3", color="#60a5fa", time_col="exit_time", ret_col="trade_ret"),
            make_strategy_series(shadow_beat_curve_df, label="Alt shadow", color="#f59e0b", time_col="curve_ts", ret_col="trade_ret"),
            make_strategy_series(shadow_global_curve_df, label="Global shadow", color="#34d399", time_col="curve_ts", ret_col="trade_ret"),
        ]
    }
    strategy_compare_section = build_interactive_strategy_compare_section(strategy_compare_payload)
    ph6_mode_df = summarize_closed_by_signal_mode(ph6_closed)
    ph6_recent_windows_df = summarize_recent_trade_windows(ph6_closed)
    ph6_observation_summary, ph6_observation_df = summarize_forward_observation_window(ph6_closed, ph6_events, target_trades=20)
    ph6_signal_summary, ph6_symbol_health_df = summarize_signal_health(ph6_signals, ph6_closed, ph6_rejections)
    ph6_bucket_health_df = summarize_bucket_health(ph6_signals, ph6_closed, ph6_rejections, phase6_smallcap_symbols)
    ph6_smallcap_activity_df = build_smallcap_activity_df(ph6_smallcap_activity_cache, phase6_smallcap_symbols)
    ph6_signal_trigger_df = build_signal_trigger_df(ph6_signals, ph6_state, ph6_rejections)
    signal_ttl_minutes = int(((phase6_cfg.get("safety", {}) or {}).get("max_signal_age_minutes", 3)) if isinstance(phase6_cfg, dict) else 3)
    ph6_preview_parity_summary, ph6_preview_lifecycle_df, ph6_preview_mismatch_df = build_preview_parity_audit(
        ph6_events,
        ttl_minutes=signal_ttl_minutes,
        lookback_hours=24,
        tail=12,
    )

    ph6_orders_df = localize_time_columns(ph6_orders_df, ["timestamp"]).rename(columns={"timestamp": "时间", "symbol": "标的", "symbol_bucket": "池子", "side": "方向", "order_role": "订单角色", "order_type": "订单类型", "price": "价格", "qty": "数量", "status": "状态", "exchange_order_id": "交易所订单号"})
    ph6_positions_df = localize_time_columns(ph6_positions_df, ["signal_timestamp", "entry_time", "timeout_at"]).rename(columns={"signal_timestamp": "信号时间", "symbol": "标的", "symbol_bucket": "池子", "side": "方向", "signal_price": "信号价", "entry_time": "开仓时间", "entry_price": "开仓均价", "entry_slippage_bps": "开仓滑点(bps)", "entry_qty": "数量", "tp_price": "止盈价", "sl_price": "止损价", "timeout_at": "超时平仓时间"})
    ph6_closed_df = localize_time_columns(ph6_closed_df, ["signal_timestamp", "entry_time", "exit_time"]).rename(columns={"signal_timestamp": "信号时间", "symbol": "标的", "symbol_bucket": "池子", "side": "方向", "signal_price": "信号价", "entry_time": "开仓时间", "entry_price": "开仓均价", "entry_slippage_bps": "开仓滑点(bps)", "exit_time": "平仓时间", "exit_price": "平仓价", "qty": "数量", "holding_minutes": "持有分钟", "exit_reason": "退出原因", "gross_pnl": "毛 PnL", "net_pnl": "净 PnL"})
    ph6_observation_df = localize_time_columns(ph6_observation_df, ["signal_timestamp", "entry_time"]).rename(columns={"signal_timestamp": "信号时间", "entry_time": "开仓时间", "symbol": "标的", "signal_mode": "模式", "side": "方向", "entry_slippage_bps": "开仓滑点(bps)", "exit_reason": "退出原因", "pnl": "PnL", "code_version": "代码版本", "config_version": "配置版本"})
    ph6_signal_df = localize_time_columns(ph6_signal_df, ["timestamp", "bucket_start", "first_seen_at", "expired_at", "official_confirmed_at"]).rename(columns={"timestamp": "信号时间", "bucket_start": "15m bucket", "first_seen_at": "首次出现", "expired_at": "有效期截止", "signal_mode": "模式", "symbol": "标的", "symbol_bucket": "池子", "side": "方向", "signal_price": "信号价", "confirmed_at_close": "收盘确认", "official_confirmed_at": "official 确认时间"})
    ph6_preview_lifecycle_df = localize_time_columns(ph6_preview_lifecycle_df, [])
    ph6_preview_mismatch_df = localize_time_columns(ph6_preview_mismatch_df, [])
    ph6_warn_df = localize_time_columns(ph6_warn_df, ["timestamp"]).rename(columns={"timestamp": "时间", "symbol": "标的", "symbol_bucket": "池子", "level": "级别", "message": "消息"})
    if not ph6_reject_df.empty and "timestamp" in ph6_reject_df.columns:
        ph6_reject_df = localize_time_columns(ph6_reject_df, ["timestamp"]).rename(columns={
            "timestamp": "时间",
            "symbol": "标的",
            "symbol_bucket": "池子",
            "side": "方向",
            "signal_id": "信号ID",
            "reason": "拒绝原因",
            "activity_percentile": "活跃度分位",
            "selected_symbol": "被选中标的",
            "signal_strength": "本信号强度",
            "selected_strength": "被选中强度",
        })
    if not ph6_side_df.empty:
        ph6_side_df = ph6_side_df.rename(columns={"side": "方向", "closed_trades": "已平仓笔数", "pnl": "PnL", "win_rate_pct": "胜率(%)", "avg_hold_minutes": "平均持有分钟"})
    if not ph6_exit_df.empty:
        ph6_exit_df = ph6_exit_df.rename(columns={"exit_reason_label": "退出原因", "closed_trades": "已平仓笔数", "pnl": "PnL", "avg_pnl": "平均单笔PnL", "win_rate_pct": "胜率(%)", "avg_net_return_bps": "平均收益(bps)", "avg_entry_slippage_bps": "平均开仓滑点(bps)", "avg_hold_minutes": "平均持有分钟"})
    if not ph6_mode_df.empty:
        ph6_mode_df = ph6_mode_df.rename(columns={"signal_mode_label": "模式", "closed_trades": "已平仓笔数", "pnl": "PnL", "avg_pnl": "平均单笔PnL", "win_rate_pct": "胜率(%)", "avg_net_return_bps": "平均收益(bps)", "avg_entry_slippage_bps": "平均开仓滑点(bps)", "avg_hold_minutes": "平均持有分钟"})
    if not ph6_recent_windows_df.empty:
        ph6_recent_windows_df = ph6_recent_windows_df.rename(columns={"window": "观察窗", "closed_trades": "样本数", "pnl": "PnL", "avg_pnl": "平均单笔PnL", "win_rate_pct": "胜率(%)", "avg_net_return_bps": "平均收益(bps)", "avg_entry_slippage_bps": "平均开仓滑点(bps)", "external_exits": "外部退出数"})
    if not ph6_symbol_health_df.empty:
        ph6_symbol_health_df = ph6_symbol_health_df.rename(columns={"symbol": "标的", "signals": "信号数", "long_signals": "多头信号", "short_signals": "空头信号", "closed_trades": "已平仓笔数", "rejections": "拒绝数", "pnl": "PnL"})
    if not ph6_bucket_health_df.empty:
        ph6_bucket_health_df = ph6_bucket_health_df.rename(columns={"bucket": "池子", "signals": "信号数", "closed_trades": "已平仓笔数", "rejections": "拒绝数", "pnl": "PnL", "symbols_seen": "出现过信号的标的数"})
    if not ph6_smallcap_activity_df.empty:
        ph6_smallcap_activity_df = localize_time_columns(ph6_smallcap_activity_df, ["updated_at"]).rename(columns={
            "symbol": "标的",
            "allowed": "允许交易",
            "percentile": "当前活跃度分位",
            "min_percentile": "阈值分位",
            "recent_median_quote_volume": "最近7天中位成交额",
            "updated_at": "更新时间",
            "cached": "命中缓存",
            "stale": "缓存过期",
            "error": "错误",
        })

    phase6_cfg = cfg.get("phase6", {}) if isinstance(cfg, dict) else {}
    phase6_sizing = phase6_cfg.get("sizing", {}) if isinstance(phase6_cfg, dict) else {}
    phase6_exit = phase6_cfg.get("exit", {}) if isinstance(phase6_cfg, dict) else {}
    risk_cfg = cfg.get("risk", {}) if isinstance(cfg, dict) else {}
    symbols = [str(s).upper() for s in ((cfg.get("universe", {}) or {}).get("symbols", []) or [])]
    by_symbol = phase6_sizing.get("desired_notional_usdt_by_symbol", {}) if isinstance(phase6_sizing, dict) else {}
    if not isinstance(by_symbol, dict):
        by_symbol = {}
    base_notional = float(phase6_sizing.get("desired_notional_usdt", 0.0) or 0.0)
    cfg_rows = [{
        "symbol": s,
        "symbol_bucket": bucket_for_symbol(s, phase6_smallcap_symbols),
        "target_notional_usdt": float(by_symbol.get(s, base_notional) or base_notional),
    } for s in symbols]
    ph6_notional_df = pd.DataFrame(cfg_rows)
    if not ph6_notional_df.empty:
        ph6_notional_df = ph6_notional_df.rename(columns={"symbol": "标的", "symbol_bucket": "池子", "target_notional_usdt": "目标仓位(USDT)"})

    activity_allowed_count = int((ph6_smallcap_activity_df.get("允许交易") == True).sum()) if not ph6_smallcap_activity_df.empty and "允许交易" in ph6_smallcap_activity_df.columns else 0
    activity_blocked_count = int((ph6_smallcap_activity_df.get("允许交易") == False).sum()) if not ph6_smallcap_activity_df.empty and "允许交易" in ph6_smallcap_activity_df.columns else 0
    activity_stale_count = int((ph6_smallcap_activity_df.get("缓存过期") == True).sum()) if not ph6_smallcap_activity_df.empty and "缓存过期" in ph6_smallcap_activity_df.columns else 0
    core_bucket_row = ph6_bucket_health_df[ph6_bucket_health_df.get("池子") == "core"] if not ph6_bucket_health_df.empty and "池子" in ph6_bucket_health_df.columns else pd.DataFrame()
    small_bucket_row = ph6_bucket_health_df[ph6_bucket_health_df.get("池子") == "smallcap"] if not ph6_bucket_health_df.empty and "池子" in ph6_bucket_health_df.columns else pd.DataFrame()
    core_bucket = core_bucket_row.iloc[0].to_dict() if not core_bucket_row.empty else {}
    small_bucket = small_bucket_row.iloc[0].to_dict() if not small_bucket_row.empty else {}

    ph6_timer_status = run_text_command("systemctl is-active momentum-rank32b-canary-phase6.timer || true", timeout=10)
    ph6_service_status = run_text_command("systemctl is-active momentum-rank32b-canary-phase6.service || true", timeout=10)
    last_signal_time = str(
        ph6_run.get("latest_observed_signal_time")
        or ph6_status.get("last_signal_time")
        or "-"
    )
    latest_actionable_signal_time = str(ph6_run.get("latest_actionable_signal_time") or "-")
    latest_evaluated_bar_time = str(
        ph6_run.get("latest_evaluated_bar_time")
        or ph6_status.get("latest_evaluated_bar_time")
        or "-"
    )
    last_finish = str(ph6_run.get("run_finished_at") or ph6_run.get("generated_at_utc") or ph6_status.get("last_run_utc") or "-")
    live_count = len(ph6_state.get("live_positions", [])) if isinstance(ph6_state.get("live_positions"), list) else int(ph6_run.get("live_positions", 0) or 0)

    generated_at = fmt_ts_bj(datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    shadow_beat_last_run = fmt_ts_bj(shadow_beat_run.get("last_run_utc") or shadow_beat_status.get("last_run_utc") or "-")
    shadow_global_last_run = fmt_ts_bj(shadow_global_run.get("last_run_utc") or shadow_global_status.get("last_run_utc") or "-")
    global_live_last_run = fmt_ts_bj(global_live_run.get("run_finished_at") or global_live_status.get("last_run_utc") or "-")
    shadow_beat_status_text = fmt(shadow_beat_status.get("status") or shadow_beat_run.get("status") or "-")
    shadow_global_status_text = fmt(shadow_global_status.get("status") or shadow_global_run.get("status") or "-")
    global_live_status_text = fmt(global_live_status.get("system_health") or global_live_run.get("status") or "-")
    global_live_net = pd.to_numeric(global_live_compare_df.get("live_net_pnl_usdt"), errors="coerce").fillna(0.0).sum() if not global_live_compare_df.empty else 0.0
    global_live_delta = pd.to_numeric(global_live_compare_df.get("delta_vs_shadow_usdt"), errors="coerce").fillna(0.0).sum() if not global_live_compare_df.empty else 0.0
    html = f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>32B 实盘 Canary 看板</title>
  <style>
    body {{ font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; background: #0b1220; color: #e5e7eb; }}
    .wrap {{ max-width: 1240px; margin: 0 auto; padding: 32px 20px 56px; }}
    h1,h2,h3 {{ margin: 0 0 12px; }}
    p {{ line-height: 1.6; }}
    .muted {{ color: #94a3b8; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; margin: 18px 0 28px; }}
    .card {{ background: #111827; border: 1px solid #1f2937; border-radius: 14px; padding: 16px; }}
    .k {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: .05em; }}
    .v {{ font-size: 24px; font-weight: 700; margin-top: 8px; word-break: break-word; }}
    .s {{ margin-top: 8px; color: #9ca3af; font-size: 13px; }}
    table {{ width: 100%; border-collapse: collapse; background: #111827; border: 1px solid #1f2937; border-radius: 14px; overflow: hidden; margin: 12px 0 28px; }}
    th, td {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid #1f2937; font-size: 13px; vertical-align: top; }}
    th {{ background: #0f172a; color: #cbd5e1; }}
    tr:last-child td {{ border-bottom: none; }}
    code, pre {{ background: #0f172a; color: #cbd5e1; border-radius: 8px; }}
    code {{ padding: 2px 6px; }}
    pre {{ padding: 14px; white-space: pre-wrap; word-break: break-word; border: 1px solid #1f2937; overflow-x: auto; }}
    a {{ color: #60a5fa; }}
  </style>
</head>
<body>
  <div class='wrap'>
    <p class='muted'>页面生成时间：{escape(generated_at)}</p>
    <h1>32B 实盘 Canary 看板</h1>
    <p>本页优先展示<strong>当前正在运行的实盘策略</strong>。Phase 1-5 只保留为历史研发记录，默认折叠，避免干扰你看实盘状态。</p>
    <p><a href='/momentum/factors/live_trading_center/report.html'>Live Trading Center</a> ｜ <a href='/momentum/factors/rank32b/report.html'>回到 32b 主页面</a> ｜ <a href='/momentum/factors/rank32b/transparency.html'>交易逻辑透明页</a> ｜ <a href='/momentum/canary-doc/'>打开实盘控制台</a> ｜ <a href='/momentum/factors/scout_rank32b_slope_floor_continuation_15m/report.html'>查看主研究报告</a> ｜ <a href='/momentum/factors/rank32b_shadow_beat/report.html'>Alt shadow sidecar</a> ｜ <a href='/momentum/factors/rank32b_shadow_global_winner/report.html'>Global strongest-only shadow</a> ｜ <a href='/momentum/factors/rank32b_global_live/report.html'>global32b live</a></p>

    <div class='card'>
      <h2>Shadow 对照（和 3 币种真钱并排看）</h2>
      <div class='grid'>
        <div class='card'><div class='k'>Alt shadow sidecar</div><div class='v'>{escape(shadow_beat_status_text)}</div><div class='s'>最近运行：{escape(shadow_beat_last_run)}<br>paper 已平仓：{int(shadow_beat_paper.get('closed_trades', 0) or 0)} 笔<br>paper 标记收益：{escape(num(float(shadow_beat_paper.get('marked_total_return', 0.0) or 0.0) * 100.0, 2))}%<br><a href='/momentum/factors/rank32b_shadow_beat/report.html'>打开页面</a></div></div>
        <div class='card'><div class='k'>Global strongest-only shadow</div><div class='v'>{escape(shadow_global_status_text)}</div><div class='s'>最近运行：{escape(shadow_global_last_run)}<br>paper 已平仓：{int(shadow_global_paper.get('closed_trades', 0) or 0)} 笔<br>paper 标记收益：{escape(num(float(shadow_global_paper.get('marked_total_return', 0.0) or 0.0) * 100.0, 2))}%<br><a href='/momentum/factors/rank32b_shadow_global_winner/report.html'>打开页面</a></div></div>
        <div class='card'><div class='k'>global32b live</div><div class='v'>{escape(global_live_status_text)}</div><div class='s'>最近运行：{escape(global_live_last_run)}<br>真钱 closed：{int(global_live_run.get('closed_trades_total', 0) or 0)} 笔<br>真钱净 PnL：{escape(num(global_live_net, 4))} USDT<br>vs shadow delta：{escape(num(global_live_delta, 4))} USDT<br><a href='/momentum/factors/rank32b_global_live/report.html'>打开页面</a></div></div>
      </div>
      <p class='muted'>这里把两条 shadow 和新的 global32b 实盘线放在一起看：这样你能分清 shadow 赚钱，是 selector 本身有效，还是实际上线后执行质量也能跟上。</p>
    </div>

    <div class='card'>
      <h2>实盘速览（先看这里）</h2>
      <div class='grid'>
        <div class='card'><div class='k'>最近完成时间</div><div class='v'>{escape(fmt_ts_bj(last_finish))}</div><div class='s'>最近一轮成功完成时间</div></div>
        <div class='card'><div class='k'>最近算到的 K 线时间</div><div class='v'>{escape(fmt_ts_bj(latest_evaluated_bar_time))}</div><div class='s'>最近一次参与信号计算的最新 bar；这是“持续计算”的硬证据</div></div>
        <div class='card'><div class='k'>最近观测到信号时间</div><div class='v'>{escape(fmt_ts_bj(last_signal_time))}</div><div class='s'>最近一次真实观测到 rank32b 信号的时间；不代表当前仍然有效</div></div>
        <div class='card'><div class='k'>当前 fresh 信号数 / 本轮新处理 / 被最强筛掉</div><div class='v'>{int(ph6_run.get('signals_seen_this_window', 0) or 0)} / {int(ph6_run.get('new_signals_processed', 0) or 0)} / {int(ph6_run.get('skipped_weaker_signals', 0) or 0)}</div><div class='s'>当前仍在有效期内、可执行的信号数；0 不等于没有持续计算。最近 fresh 信号时间：{escape(fmt_ts_bj(latest_actionable_signal_time))}</div></div>
        <div class='card'><div class='k'>选择模式</div><div class='v'>{escape(fmt(ph6_run.get('selection_mode')))}</div><div class='s'>强度口径：{escape(fmt(ph6_run.get('selection_strength_metric')))}</div></div>
        <div class='card'><div class='k'>当前本地持仓 / 非 canary 仓位</div><div class='v'>{live_count} / {int(ph6_run.get('unexpected_exchange_positions', 0) or 0)}</div><div class='s'>账户里有无别的策略仓位干扰</div></div>
        <div class='card'><div class='k'>近期总 PnL / 胜率</div><div class='v'>{escape(num(ph6_closed_summary.get('total_pnl'), 4))} / {escape(num(float(ph6_closed_summary.get('win_rate', 0.0) or 0.0) * 100.0, 2))}%</div><div class='s'>基于 recent closed trades</div></div>
        <div class='card'><div class='k'>止盈 / 止损 / 超时</div><div class='v'>{int(ph6_closed_summary.get('tp_hits', 0) or 0)} / {int(ph6_closed_summary.get('sl_hits', 0) or 0)} / {int(ph6_closed_summary.get('timeout_hits', 0) or 0)}</div><div class='s'>自然退出结构<br>其他退出：{escape(str(ph6_closed_summary.get('other_exit_summary') or '无'))}</div></div>
      </div>
      <p class='muted'>下方先是历史研发阶段（默认折叠），再往下是完整的 <strong>Phase 6 实盘运行面板</strong>。</p>
    </div>

    <details>
      <summary>历史研发阶段（Phase 1-5，可忽略）</summary>
      <h2>Phase 1 / Signal → Risk → Intention</h2>
      <div class='grid'>
        <div class='card'><div class='k'>Mode</div><div class='v'>{escape(fmt(ph1_status.get('mode')))}</div><div class='s'>signal / risk / intention skeleton</div></div>
        <div class='card'><div class='k'>Signals in window</div><div class='v'>{int(ph1_run.get('signals_seen_this_window', 0) or 0)}</div><div class='s'>adapter snapshot</div></div>
        <div class='card'><div class='k'>Intentions created</div><div class='v'>{int(ph1_run.get('intentions_created', 0) or 0)}</div><div class='s'>no broker actions</div></div>
        <div class='card'><div class='k'>Risk rejects</div><div class='v'>{int(ph1_run.get('risk_rejections', 0) or 0)}</div><div class='s'>standardized reasons</div></div>
        <div class='card'><div class='k'>Last run</div><div class='v'>{escape(fmt(ph1_status.get('last_run_utc')))}</div><div class='s'>health={escape(fmt(ph1_status.get('system_health')))}</div></div>
      </div>
      <h3>Phase 1 recent intentions</h3>
      {render_table(ph1_intentions_df)}
      <h3>Phase 1 recent rejects</h3>
      {render_table(ph1_reject_df)}
      <h3>Phase 1 symbol runtime state</h3>
      {render_table(ph1_state_df)}

      <h2>Phase 2 / Minimal Receipt Chain</h2>
      <div class='grid'>
        <div class='card'><div class='k'>Mode</div><div class='v'>{escape(fmt(ph2_status.get('mode')))}</div><div class='s'>default=test/no-fill</div></div>
        <div class='card'><div class='k'>Orders placed</div><div class='v'>{int(ph2_run.get('orders_placed', 0) or 0)}</div><div class='s'>isolated test receipt chain</div></div>
        <div class='card'><div class='k'>Receipt chains completed</div><div class='v'>{int(ph2_run.get('receipt_chains_completed', 0) or 0)}</div><div class='s'>intent → ack → cancel → final</div></div>
        <div class='card'><div class='k'>Capital deployed</div><div class='v'>0</div><div class='s'>phase2 hard rule</div></div>
        <div class='card'><div class='k'>Last run</div><div class='v'>{escape(fmt(ph2_status.get('last_run_utc')))}</div><div class='s'>health={escape(fmt(ph2_status.get('system_health')))}</div></div>
      </div>
      <h3>Phase 2 recent orders</h3>
      {render_table(ph2_orders_df)}
      <h3>Phase 2 receipt chains</h3>
      {render_table(ph2_chain_df)}
      <div class='card'><h3>Phase 2 latest operator packet</h3><pre>{escape(ph2_packet_excerpt)}</pre></div>

      <h2>Phase 3 / Real Query Surface + Ledger + TTL</h2>
      <div class='grid'>
        <div class='card'><div class='k'>Mode</div><div class='v'>{escape(fmt(ph3_status.get('mode')))}</div><div class='s'>query_only</div></div>
        <div class='card'><div class='k'>Venue checks</div><div class='v'>{int(ph3_run.get('venue_checks', 0) or 0)}</div><div class='s'>private query surfaces</div></div>
        <div class='card'><div class='k'>Venue ok count</div><div class='v'>{int(ph3_run.get('venue_ok_count', 0) or 0)}</div><div class='s'>binance / lighter</div></div>
        <div class='card'><div class='k'>Ledger rows</div><div class='v'>{int(ph3_run.get('ledger_rows', 0) or 0)}</div><div class='s'>derived from phase2 chain</div></div>
        <div class='card'><div class='k'>Capital deployed</div><div class='v'>0</div><div class='s'>phase3 hard rule</div></div>
        <div class='card'><div class='k'>Last run</div><div class='v'>{escape(fmt(ph3_status.get('last_run_utc')))}</div><div class='s'>health={escape(fmt(ph3_status.get('system_health')))}</div></div>
      </div>
      <h3>Phase 3 venue health</h3>
      {render_table(ph3_venue_df)}
      <h3>Phase 3 order ledger</h3>
      {render_table(ph3_ledger_df, digits_cols={'seconds_remaining':0, 'ttl_minutes':0})}
      <div class='card'><h3>Phase 3 account snapshot</h3><pre>{escape(ph3_account_excerpt)}</pre></div>
      <div class='card'><h3>Phase 3 operator packet</h3><pre>{escape(ph3_packet_excerpt)}</pre></div>

      <h2>Phase 4 / Minimal Real Order Experiment</h2>
      <div class='grid'>
        <div class='card'><div class='k'>Mode</div><div class='v'>{escape(fmt(ph4_run.get('mode')))}</div><div class='s'>real signed test order</div></div>
        <div class='card'><div class='k'>Venue</div><div class='v'>{escape(fmt(ph4_run.get('venue')))}</div><div class='s'>binance futures</div></div>
        <div class='card'><div class='k'>HTTP status</div><div class='v'>{escape(fmt(ph4_run.get('http_status')))}</div><div class='s'>/fapi/v1/order/test</div></div>
        <div class='card'><div class='k'>Symbol</div><div class='v'>{escape(fmt(ph4_run.get('symbol')))}</div><div class='s'>signed validation path</div></div>
        <div class='card'><div class='k'>Quantity</div><div class='v'>{escape(fmt(ph4_run.get('quantity')))}</div><div class='s'>no capital deployment</div></div>
        <div class='card'><div class='k'>Capital deployed</div><div class='v'>0</div><div class='s'>phase4 hard rule</div></div>
      </div>
      <div class='card'><h3>Phase 4 execution receipt</h3><pre>{escape(ph4_receipt_excerpt)}</pre></div>
      <div class='card'><h3>Phase 4 operator packet</h3><pre>{escape(ph4_packet_excerpt)}</pre></div>

      <h2>Phase 5 / Minimal Live Order Gate</h2>
      <div class='grid'>
        <div class='card'><div class='k'>Mode</div><div class='v'>{escape(fmt(ph5_run.get('mode')))}</div><div class='s'>live limit gtx then cancel</div></div>
        <div class='card'><div class='k'>Venue</div><div class='v'>{escape(fmt(ph5_run.get('venue')))}</div><div class='s'>binance futures live</div></div>
        <div class='card'><div class='k'>Final status</div><div class='v'>{escape(fmt(ph5_run.get('final_status')))}</div><div class='s'>expect canceled / expired</div></div>
        <div class='card'><div class='k'>Target notional</div><div class='v'>{escape(fmt(ph5_run.get('target_notional_usdt')))}</div><div class='s'>auto-raised to min filters</div></div>
        <div class='card'><div class='k'>Chosen notional</div><div class='v'>{escape(fmt(ph5_run.get('chosen_notional_usdt')))}</div><div class='s'>actual submitted notional</div></div>
        <div class='card'><div class='k'>Symbol / Side</div><div class='v'>{escape(fmt(ph5_run.get('symbol')))} {escape(fmt(ph5_run.get('side')))}</div><div class='s'>single isolated order</div></div>
      </div>
      <div class='card'>
        <h3>Phase 5 interpretation</h3>
        <ul>
          <li>这一步已经是真正的 live order，不再是 test order。</li>
          <li>订单类型是 <code>LIMIT + GTX</code>，价格故意挂在当前价外侧，并在 ack 后立即撤单，以降低真实成交概率。</li>
          <li>quantity 会自动抬到满足 Binance 最小下单限制，不会因为 minQty / minNotional 被拒。</li>
        </ul>
      </div>
      <div class='card'><h3>Phase 5 execution receipt</h3><pre>{escape(ph5_receipt_excerpt)}</pre></div>
      <div class='card'><h3>Phase 5 operator packet</h3><pre>{escape(ph5_packet_excerpt)}</pre></div>
    </details>

    <h2>当前实盘策略（Phase 6 自动执行）</h2>
    <h3>运行健康</h3>
    <div class='grid'>
      <div class='card'><div class='k'>定时器 / 执行服务</div><div class='v'>{escape(fmt(ph6_timer_status))} / {escape(fmt(ph6_service_status))}</div><div class='s'>timer 常驻等待；service 一次跑完回到 inactive 属于正常</div></div>
      <div class='card'><div class='k'>系统健康度</div><div class='v'>{escape(fmt(ph6_status.get('system_health')))}</div><div class='s'>phase6 运行状态分类</div></div>
      <div class='card'><div class='k'>最近完成时间</div><div class='v'>{escape(fmt_ts_bj(last_finish))}</div><div class='s'>最近一轮成功完成时间（北京时间 / UTC）</div></div>
      <div class='card'><div class='k'>最近算到的 K 线时间</div><div class='v'>{escape(fmt_ts_bj(latest_evaluated_bar_time))}</div><div class='s'>最近一次参与信号计算的最新 bar 时间</div></div>
      <div class='card'><div class='k'>交易开关 / Kill Switch</div><div class='v'>{escape(str(bool(risk_cfg.get('trade_enabled', True))))} / {escape(str(bool(risk_cfg.get('kill_switch', False))))}</div><div class='s'>网页控制面板可直接修改</div></div>
      <div class='card'><div class='k'>当前 fresh 信号数 / 本轮新处理 / 被最强筛掉</div><div class='v'>{int(ph6_run.get('signals_seen_this_window', 0) or 0)} / {int(ph6_run.get('new_signals_processed', 0) or 0)} / {int(ph6_run.get('skipped_weaker_signals', 0) or 0)}</div><div class='s'>当前仍在有效期内、可执行的信号数 / 本轮新处理数量 / 同窗竞争淘汰数</div></div>
      <div class='card'><div class='k'>选择模式 / 强度口径</div><div class='v'>{escape(fmt(ph6_run.get('selection_mode')))} / {escape(fmt(ph6_run.get('selection_strength_metric')))}</div><div class='s'>当前：同窗只做最强信号</div></div>
      <div class='card'><div class='k'>最近观测到信号时间</div><div class='v'>{escape(fmt_ts_bj(last_signal_time))}</div><div class='s'>最近一次真实观测到 rank32b 信号的时间；不代表当前仍然有效。最近 fresh 信号时间：{escape(fmt_ts_bj(latest_actionable_signal_time))}</div></div>
      <div class='card'><div class='k'>当前本地持仓数</div><div class='v'>{live_count}</div><div class='s'>phase6 本地追踪仓位</div></div>
      <div class='card'><div class='k'>账户仓位 / 非 canary 仓位</div><div class='v'>{int(ph6_run.get('exchange_open_positions', 0) or 0)} / {int(ph6_run.get('unexpected_exchange_positions', 0) or 0)}</div><div class='s'>账户总仓位 / 不归 canary 管理的仓位</div></div>
      <div class='card'><div class='k'>策略告警 / 外部仓位提醒</div><div class='v'>{int(ph6_run.get('canary_warnings', 0) or 0)} / {int(ph6_run.get('external_account_warnings', 0) or 0)}</div><div class='s'>策略自身异常 / 共享账户外部仓位提醒</div></div>
      <div class='card'><div class='k'>本轮发单数</div><div class='v'>{int(ph6_run.get('orders_emitted', 0) or 0)}</div><div class='s'>本轮发出的 entry + exit plan 数量</div></div>
      <div class='card'><div class='k'>默认目标仓位</div><div class='v'>{escape(num(base_notional, 2))} USDT</div><div class='s'>低于交易所最小量时会自动上调</div></div>
      <div class='card'><div class='k'>止盈 / 止损 / 超时</div><div class='v'>{escape(num(phase6_exit.get('tp_atr_mult'),2))} / {escape(num(phase6_exit.get('sl_atr_mult'),2))} / {escape(str(int(phase6_exit.get('timeout_minutes', 120) or 120)))}m</div><div class='s'>当前实盘 exit 参数</div></div>
      <div class='card'><div class='k'>默认杠杆</div><div class='v'>{escape(str(int(phase6_cfg.get('default_leverage', 1) or 1)))}x</div><div class='s'>下单前会强制校验</div></div>
      <div class='card'><div class='k'>当前代码版本</div><div class='v'>{escape(fmt(current_commit))}</div><div class='s'>用于和修复后观察窗对照，避免混淆旧样本</div></div>
    </div>

    <h3>本轮修复后观察窗（目标 20 笔）</h3>
    <p class='muted'>这块是专门给“改完一轮后先别急着下结论”用的。若存在手动 observation window 锚点，则以该锚点为准；否则回退到历史默认口径。</p>
    <div class='grid'>
      <div class='card'><div class='k'>观察窗起点</div><div class='v'>{escape(fmt_ts_bj(ph6_observation_summary.get('start_time')))}</div><div class='s'>从这之后的新样本才更有参考价值</div></div>
      <div class='card'><div class='k'>进度</div><div class='v'>{int(ph6_observation_summary.get('closed_trades', 0) or 0)} / {int(ph6_observation_summary.get('target_trades', 20) or 20)}</div><div class='s'>还差 {int(ph6_observation_summary.get('remaining_trades', 20) or 20)} 笔；进度 {escape(num(ph6_observation_summary.get('progress_pct'), 1))}%</div></div>
      <div class='card'><div class='k'>观察窗 PnL / 胜率</div><div class='v'>{escape(num(ph6_observation_summary.get('pnl'), 4))} / {escape(num(float(ph6_observation_summary.get('win_rate', 0.0) or 0.0) * 100.0, 2))}%</div><div class='s'>只统计观察窗起点之后的新平仓样本</div></div>
      <div class='card'><div class='k'>观察窗平均开仓滑点</div><div class='v'>{escape(num(ph6_observation_summary.get('avg_entry_slippage_bps'), 2))} bps</div><div class='s'>正数 = 比信号价更差；负数 = 更好</div></div>
    </div>
    <p class='muted'>{escape(str(ph6_observation_summary.get('note') or ''))}</p>
    <h3>修复后观察窗成交样本</h3>
    {render_table(ph6_observation_df, digits_cols={'开仓滑点(bps)':2, 'PnL':4})}

    <h3>主池 / 小币池分层运行视图</h3>
    <div class='grid'>
      <div class='card'><div class='k'>主池标的数 / 小币标的数</div><div class='v'>{len(phase6_core_symbols)} / {len(phase6_smallcap_symbols)}</div><div class='s'>主池维持原白名单；小币池是增量 bucket</div></div>
      <div class='card'><div class='k'>主池并发 / 小币并发 / 总并发</div><div class='v'>{int(risk_cfg.get('max_core_positions', 1) or 1)} / {int(phase6_smallcap_cfg.get('max_concurrent_positions', 1) or 1)} / {int(risk_cfg.get('max_concurrent_positions', 1) or 1)}</div><div class='s'>现在是 core 1 + smallcap 1</div></div>
      <div class='card'><div class='k'>主池近期信号 / 小币近期信号</div><div class='v'>{int(core_bucket.get('信号数', 0) or 0)} / {int(small_bucket.get('信号数', 0) or 0)}</div><div class='s'>recent signals 里按 bucket 统计</div></div>
      <div class='card'><div class='k'>主池近期已平仓 / 小币近期已平仓</div><div class='v'>{int(core_bucket.get('已平仓笔数', 0) or 0)} / {int(small_bucket.get('已平仓笔数', 0) or 0)}</div><div class='s'>按 bucket 看实际成交闭环</div></div>
      <div class='card'><div class='k'>小币 activity filter：允许 / 阻断</div><div class='v'>{activity_allowed_count} / {activity_blocked_count}</div><div class='s'>按当前缓存中的 8 个小币状态统计</div></div>
      <div class='card'><div class='k'>小币 activity cache 过期数</div><div class='v'>{activity_stale_count}</div><div class='s'>如果大于 0，说明过滤器缓存需要刷新</div></div>
    </div>

    <h3>最近盈亏拆解（基于近期已平仓交易）</h3>
    <div class='grid'>
      <div class='card'><div class='k'>已平仓笔数</div><div class='v'>{int(ph6_closed_summary.get('closed_count', 0) or 0)}</div><div class='s'>recent closed trades 样本数</div></div>
      <div class='card'><div class='k'>总 PnL</div><div class='v'>{escape(num(ph6_closed_summary.get('total_pnl'), 4))}</div><div class='s'>优先用 net_pnl；缺失时回退 gross_pnl</div></div>
      <div class='card'><div class='k'>胜率</div><div class='v'>{escape(num(float(ph6_closed_summary.get('win_rate', 0.0) or 0.0) * 100.0, 2))}%</div><div class='s'>按 recent closed trades 统计</div></div>
      <div class='card'><div class='k'>平均持有时长</div><div class='v'>{escape(num(ph6_closed_summary.get('avg_hold_minutes'), 1))}m</div><div class='s'>平均持有时长</div></div>
      <div class='card'><div class='k'>止盈 / 止损 / 超时</div><div class='v'>{int(ph6_closed_summary.get('tp_hits', 0) or 0)} / {int(ph6_closed_summary.get('sl_hits', 0) or 0)} / {int(ph6_closed_summary.get('timeout_hits', 0) or 0)}</div><div class='s'>自然退出结构<br>其他退出：{escape(str(ph6_closed_summary.get('other_exit_summary') or '无'))}</div></div>
      <div class='card'><div class='k'>外部干预退出</div><div class='v'>{int(ph6_closed_summary.get('external_interventions', 0) or 0)}</div><div class='s'>manual / external_flat / attach_failed / emergency flatten</div></div>
    </div>

    {ph6_live_curve_card}
    {strategy_compare_section}

    <h3>最近 5 / 10 / 20 笔滚动观察窗</h3>
    <p class='muted'>这块是拿来防止“被全样本历史拖着走”的。你后面可以主要盯最近 20 笔，而不是一直被早期 bug 样本污染情绪。</p>
    {render_table(ph6_recent_windows_df, digits_cols={'PnL':4, '平均单笔PnL':4, '胜率(%)':2, '平均收益(bps)':2, '平均开仓滑点(bps)':2})}
    <h3>按信号模式拆分：preview vs official</h3>
    <p class='muted'>如果后面 preview 又开始明显差于 official，这张表会第一时间把问题暴露出来。</p>
    {render_table(ph6_mode_df, digits_cols={'PnL':4, '平均单笔PnL':4, '胜率(%)':2, '平均收益(bps)':2, '平均开仓滑点(bps)':2, '平均持有分钟':2})}

    <h3>信号与交易结构健康度</h3>
    <div class='grid'>
      <div class='card'><div class='k'>近期信号数</div><div class='v'>{int(ph6_signal_summary.get('signal_count', 0) or 0)}</div><div class='s'>recent signals 样本数</div></div>
      <div class='card'><div class='k'>多头 / 空头信号</div><div class='v'>{int(ph6_signal_summary.get('long_signals', 0) or 0)} / {int(ph6_signal_summary.get('short_signals', 0) or 0)}</div><div class='s'>判断最近是不是单边 regime</div></div>
      <div class='card'><div class='k'>风控拒绝数</div><div class='v'>{int(ph6_signal_summary.get('rejections', 0) or 0)}</div><div class='s'>被 risk gate 拒掉的信号数</div></div>
      <div class='card'><div class='k'>总告警数</div><div class='v'>{int(ph6_run.get('warnings', 0) or 0)}</div><div class='s'>需要结合下方告警表看细项</div></div>
    </div>

    <h3>Preview / Official 一致性审计（最近 24h）</h3>
    <div class='grid'>
      <div class='card'><div class='k'>preview 信号数</div><div class='v'>{int(ph6_preview_parity_summary.get('preview_signals', 0) or 0)}</div><div class='s'>基于 live SignalReceived 事件统计</div></div>
      <div class='card'><div class='k'>收盘同向确认 / preview_only</div><div class='v'>{int(ph6_preview_parity_summary.get('preview_confirmed_at_close', 0) or 0)} / {int(ph6_preview_parity_summary.get('preview_only', 0) or 0)}</div><div class='s'>preview 最后是否被 official_close 同向确认</div></div>
      <div class='card'><div class='k'>official_without_preview</div><div class='v'>{int(ph6_preview_parity_summary.get('official_without_preview', 0) or 0)}</div><div class='s'>收盘确认了，但此前没在 live 里看到 preview 的 bucket</div></div>
      <div class='card'><div class='k'>preview 已触发交易</div><div class='v'>{int(ph6_preview_parity_summary.get('preview_traded', 0) or 0)}</div><div class='s'>preview 信号里最终实际触发开仓/已平仓的数量</div></div>
      <div class='card'><div class='k'>preview 平均领先分钟</div><div class='v'>{escape(num(ph6_preview_parity_summary.get('avg_preview_lead_minutes'), 2))}</div><div class='s'>preview 首次出现到 official 收盘确认之间的平均时间差</div></div>
      <div class='card'><div class='k'>当前 TTL</div><div class='v'>{signal_ttl_minutes}m</div><div class='s'>fresh 信号有效期；用于判断是否仍可执行</div></div>
    </div>

    <h3>最近 preview 生命周期</h3>
    <p class='muted'>这张表专门回答：<strong>属于哪根 15m bucket、第一次在 live 里几点出现、到几点过期、收盘后有没有被 official 同向确认、最后实际结果是什么。</strong></p>
    {render_table(ph6_preview_lifecycle_df, digits_cols={'领先分钟':2})}
    <h3>Preview / Official 对账差异</h3>
    <p class='muted'>这里只列真正值得盯的偏差：<strong>preview_only</strong>（live 预览出现了，但收盘没确认）和 <strong>official_without_preview</strong>（收盘确认了，但 live 没提前看到 preview）。</p>
    {render_table(ph6_preview_mismatch_df)}
    <h3>最近信号是否触发交易</h3>
    {render_table(ph6_signal_trigger_df, digits_cols={'信号价':4})}
    <h3>各标的目标仓位（USDT）</h3>
    {render_table(ph6_notional_df, digits_cols={'目标仓位(USDT)':2})}
    <h3>按池子汇总：主池 vs 小币池</h3>
    {render_table(ph6_bucket_health_df, digits_cols={'PnL':4})}
    <h3>小币 activity filter 当前缓存</h3>
    {render_table(ph6_smallcap_activity_df, digits_cols={'当前活跃度分位':3, '阈值分位':2, '最近7天中位成交额':2})}
    <h3>按标的健康度汇总</h3>
    {render_table(ph6_symbol_health_df, digits_cols={'PnL':4})}
    <h3>按多空方向的 PnL 汇总</h3>
    {render_table(ph6_side_df, digits_cols={'PnL':4, '胜率(%)':2, '平均持有分钟':2})}
    <h3>按退出原因的收益 / 滑点 / 胜率汇总</h3>
    <p class='muted'>这张表是用来看“钱到底死在哪种退出里”的。尤其适合盯 stop-loss、timeout 和任何异常退出。</p>
    {render_table(ph6_exit_df, digits_cols={'PnL':4, '平均单笔PnL':4, '胜率(%)':2, '平均收益(bps)':2, '平均开仓滑点(bps)':2, '平均持有分钟':2})}
    <h3>近期信号明细</h3>
    {render_table(ph6_signal_df, digits_cols={'信号价':4})}
    <h3>近期风控拒绝</h3>
    {render_table(ph6_reject_df)}
    <h3>近期订单明细</h3>
    {render_table(ph6_orders_df)}
    <h3>当前 / 近期开仓</h3>
    <p class='muted'>这里新增了 <strong>信号价 / 开仓均价 / 开仓滑点(bps)</strong>。滑点口径：<strong>正数 = 比信号价更差</strong>，负数 = 比信号价更好；多头按买得更高算更差，空头按卖得更低算更差。无当前持仓时，也会保留近期已开过的样本，便于审计滑点。</p>
    {render_table(ph6_positions_df, digits_cols={'信号价':6, '开仓均价':6, '开仓滑点(bps)':2, '数量':6, '止盈价':6, '止损价':6})}
    <h3>近期已平仓交易</h3>
    {render_table(ph6_closed_df, digits_cols={'信号价':6, '开仓均价':6, '开仓滑点(bps)':2, '平仓价':6, '数量':6, '持有分钟':2, '毛 PnL':4, '净 PnL':4})}
    <h3>近期告警</h3>
    {render_table(ph6_warn_df)}
    <div class='card'><h3>Phase 6 原始状态包（调试用）</h3><pre>{escape(ph6_packet_excerpt)}</pre></div>
    <div class='card'><h3>Phase 6 收益审计（含手续费口径）</h3><pre>{escape(live_snapshot_excerpt)}</pre></div>

    <div class='card'>
      <h2>当前说明与操作入口</h2>
      <p class='muted'>完整编辑页：<a href='https://jp.jerrypsy.top/momentum/canary-doc/'>/momentum/canary-doc/</a></p>
      <pre>{escape(excerpt(DOC_PATH, limit=36))}</pre>
    </div>
    <div class='card'><h2>Phase 6 说明（摘录）</h2><pre>{escape(excerpt(PHASE6_DOC_PATH, limit=28))}</pre></div>
    <details>
      <summary>历史阶段说明（Phase 1-5，可忽略）</summary>
      <div class='card'><h2>Phase 1 说明（摘录）</h2><pre>{escape(excerpt(PHASE1_DOC_PATH, limit=22))}</pre></div>
      <div class='card'><h2>Phase 2 说明（摘录）</h2><pre>{escape(excerpt(PHASE2_DOC_PATH, limit=22))}</pre></div>
      <div class='card'><h2>Phase 3 说明（摘录）</h2><pre>{escape(excerpt(PHASE3_DOC_PATH, limit=22))}</pre></div>
      <div class='card'><h2>Phase 4 说明（摘录）</h2><pre>{escape(excerpt(PHASE4_DOC_PATH, limit=22))}</pre></div>
      <div class='card'><h2>Phase 5 说明（摘录）</h2><pre>{escape(excerpt(PHASE5_DOC_PATH, limit=24))}</pre></div>
    </details>
  </div>
</body>
</html>
"""
    OUT_PATH.write_text(html, encoding="utf-8")
    print({"generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "out": str(OUT_PATH)})


if __name__ == '__main__':
    main()
