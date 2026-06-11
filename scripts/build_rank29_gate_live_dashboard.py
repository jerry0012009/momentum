#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "rank29_gate_live"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "rank29_gate_live"
OUT_PATH = SITE_DIR / "report.html"

STATUS_PATH = ART_DIR / "rank29_gate_live_status.json"
ORDERS_PATH = ART_DIR / "rank29_gate_live_recent_orders.json"
REJECTIONS_PATH = ART_DIR / "rank29_gate_live_recent_rejections.json"
WARNINGS_PATH = ART_DIR / "rank29_gate_live_warnings.json"
COMPARE_PATH = ART_DIR / "rank29_gate_live_vs_shadow.csv"


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
    return pd.read_csv(path)


def pct(v: Any, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def num(v: Any, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f}"


def money(v: Any, digits: int = 3) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f} USDT"


def fmt_ts(v: Any) -> str:
    if v is None or v == "" or pd.isna(v):
        return "-"
    try:
        return pd.to_datetime(v, utc=True).strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return str(v)


def fmt_bool(v: Any) -> str:
    return "yes" if bool(v) else "no"


def render_table(df: pd.DataFrame, *, percent_cols: set[str] | None = None, money_cols: set[str] | None = None, digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    percent_cols = percent_cols or set()
    money_cols = money_cols or set()
    digits_cols = digits_cols or {}
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows: list[str] = []
    for _, row in df.iterrows():
        cells: list[str] = []
        for col in df.columns:
            v = row[col]
            if col in percent_cols:
                text = pct(v, digits_cols.get(col, 2))
            elif col in money_cols:
                text = money(v, digits_cols.get(col, 3))
            elif isinstance(v, (int, float)) and not isinstance(v, bool):
                text = num(v, digits_cols.get(col, 2))
            else:
                text = str(v)
            cells.append(f"<td>{escape(text)}</td>")
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def card_html(title: str, value: str, sub: str) -> str:
    return f"<div class='card stat'><div class='k'>{escape(title)}</div><div class='v'>{escape(value)}</div><div class='s'>{sub}</div></div>"


def recent_df(rows: list[dict[str, Any]], columns: list[str], *, limit: int = 12) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=columns)
    df = pd.DataFrame(rows).copy()
    for col in ["timestamp", "entry_ts", "planned_exit_ts"]:
        if col in df.columns:
            df[col] = df[col].map(fmt_ts)
    keep = [c for c in columns if c in df.columns]
    return df[keep].tail(limit).iloc[::-1].reset_index(drop=True)


def compare_views() -> tuple[pd.DataFrame, dict[str, str]]:
    df = read_csv(COMPARE_PATH)
    if df.empty:
        return pd.DataFrame(), {
            "closed_trades": "0",
            "live_net": "0.000 USDT",
            "shadow_net": "0.000 USDT",
            "delta": "0.000 USDT",
        }
    for col in ["live_entry_time", "live_exit_time", "entry_ts", "exit_ts"]:
        if col in df.columns:
            df[col] = df[col].map(fmt_ts)
    summary = {
        "closed_trades": str(len(df)),
        "live_net": money(pd.to_numeric(df.get("live_net_pnl_usdt"), errors="coerce").fillna(0.0).sum()),
        "shadow_net": money(pd.to_numeric(df.get("shadow_proxy_net_pnl_usdt"), errors="coerce").fillna(0.0).sum()),
        "delta": money(pd.to_numeric(df.get("delta_vs_shadow_usdt"), errors="coerce").fillna(0.0).sum()),
    }
    keep = [
        c
        for c in [
            "signal_id",
            "symbol",
            "side",
            "live_entry_time",
            "live_exit_time",
            "live_net_pnl_usdt",
            "shadow_proxy_net_pnl_usdt",
            "delta_vs_shadow_usdt",
            "gate_low_trend_high_noise",
            "exposure_weight",
        ]
        if c in df.columns
    ]
    view = df.sort_values(keep[4] if "live_exit_time" in keep else keep[0], ascending=False)[keep].head(24).reset_index(drop=True)
    return view, summary


def build_page() -> str:
    status = read_json(STATUS_PATH, {}) or {}
    orders = read_json(ORDERS_PATH, []) or []
    rejections = read_json(REJECTIONS_PATH, []) or []
    warnings = read_json(WARNINGS_PATH, []) or []
    compare_df, compare_summary = compare_views()
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    recent_orders = recent_df(
        orders,
        ["timestamp", "order_role", "symbol", "side", "exchange_side", "price", "qty", "desired_notional_usdt", "status", "exit_reason"],
    )
    recent_rejections = recent_df(
        rejections,
        ["timestamp", "reason", "symbol", "side", "entry_ts", "planned_exit_ts", "exposure_weight"],
    )
    recent_warnings = recent_df(
        warnings,
        ["timestamp", "message"],
    )

    core3_busy = status.get("core3_busy_symbols") or []
    live_symbols = status.get("live_symbols") or []
    busy_text = ", ".join(core3_busy[:8]) if core3_busy else "none"
    live_symbol_text = ", ".join(live_symbols[:8]) if live_symbols else "none"
    lifecycle = str(status.get("lifecycle_status", "") or "").strip().lower()
    retired = lifecycle.startswith("retired") or (status.get("allow_live_orders") is False and bool(status.get("retired_at_utc")))
    hero_title = "Rank29 · retired live debug" if retired else "Rank29 · gate live 100u"
    hero_intro = (
        "这页现在是 <b>retired / raw detail</b> 细页：Rank29 已停实盘并降为 P0，保留这里仅为留档 orders / rejections / raw compare。"
        if retired
        else "这页现在降级为 <b>debug / raw detail</b> 细页：专门盯 <b>rank29_gate_live_100u</b> 这条真实 live lane 的 orders / rejections / raw compare。"
    )
    retired_note = ""
    if retired:
        retired_note = f"<p class=\"warn\"><b>P0 archived：</b>{escape(str(status.get('retirement_reason', 'strict-causal audit found future-leak contamination; do not restart this live lane.')))}</p>"

    cards = [
        card_html(
            "weekly closed pnl",
            money(status.get("weekly_closed_pnl_usdt"), 3),
            f"weekly stop = -{abs(float(status.get('weekly_loss_limit_usdt', 10.0))):.1f} USDT · active={fmt_bool(status.get('weekly_stop_active'))}",
        ),
        card_html(
            "open live positions",
            str(int(status.get("live_positions", 0) or 0)),
            f"symbols={escape(live_symbol_text)}",
        ),
        card_html(
            "closed trades vs shadow",
            compare_summary["closed_trades"],
            f"live={compare_summary['live_net']} · shadow={compare_summary['shadow_net']} · delta={compare_summary['delta']}",
        ),
        card_html(
            "core3 conflict watch",
            str(len(core3_busy)),
            f"busy symbols={escape(busy_text)}",
        ),
    ]

    html = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Rank29 retired live debug</title>
  <style>
    body {{ font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; background: #020617; color: #e5e7eb; }}
    .wrap {{ max-width: 1260px; margin: 0 auto; padding: 32px 20px 64px; }}
    h1,h2,h3 {{ margin: 0 0 12px; }}
    p, li {{ line-height: 1.65; }}
    a {{ color: #60a5fa; }}
    .muted {{ color: #94a3b8; }}
    .warn {{ color: #fbbf24; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px; margin: 18px 0 28px; }}
    .card {{ background: #0f172a; border: 1px solid #1f2937; border-radius: 16px; padding: 16px 18px; }}
    .hero {{ border-color: #334155; background: linear-gradient(180deg, #0f172a 0%, #0b1220 100%); }}
    .stat .k {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: .05em; }}
    .stat .v {{ font-size: 30px; font-weight: 800; margin-top: 8px; }}
    .stat .s {{ margin-top: 8px; color: #9ca3af; font-size: 13px; }}
    table {{ width: 100%; border-collapse: collapse; background: #0f172a; border: 1px solid #1f2937; border-radius: 16px; overflow: hidden; margin: 12px 0 28px; }}
    th, td {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid #1f2937; font-size: 13px; vertical-align: top; }}
    th {{ background: #111827; color: #cbd5e1; }}
    tr:last-child td {{ border-bottom: none; }}
    code {{ background: #111827; color: #cbd5e1; padding: 2px 6px; border-radius: 6px; }}
    .section {{ margin-top: 28px; }}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <p class=\"muted\">Generated: {generated}</p>
    <p><a href=\"../rank29_monitoring_hub/report.html\">← 返回 Rank29 archive / audit</a></p>
    <h1>{hero_title}</h1>
    <p>{hero_intro} 日常结论请优先看 <a href=\"../rank29_monitoring_hub/report.html\">Rank29 archive / audit</a>。坏环境降仓 / weekly stop 这些旧 live 机制仍保留在此页，只为解释历史 runner 行为。</p>
    {retired_note}

    <div class=\"card hero\">
      <h2>当前读法</h2>
      <ul>
        <li><b>closed trades vs shadow</b>：看真钱执行后，和 shadow proxy 的同窗差异有没有跑偏。</li>
        <li><b>core3 conflict watch</b>：看 live lane 是否经常因为 core3 忙而主动 skip。</li>
        <li><b>recent orders / rejections</b>：看最近到底是正常发单、被 core3 挡掉，还是因为信号过期没做。</li>
      </ul>
      <p class=\"muted\">runner update = {escape(fmt_ts(status.get('generated_at_utc')))} · allow_live_orders = {escape(fmt_bool(status.get('allow_live_orders')))} · scanned signals = {escape(str(status.get('candidate_signals_scanned', 0)))} · seen ids = {escape(str(status.get('seen_signal_ids', 0)))} · priority = {escape(str(status.get('priority', 'P0')))} </p>
    </div>

    <div class=\"grid\">{''.join(cards)}</div>

    <div class=\"section\">
      <h2>1) live vs shadow 同窗对比</h2>
      <p class=\"muted\">这里按 signal_id 对齐 live closed trades 和 gate shadow proxy，主要看真钱执行是否明显弱于 shadow。</p>
      {render_table(compare_df, money_cols={'live_net_pnl_usdt','shadow_proxy_net_pnl_usdt','delta_vs_shadow_usdt'}, digits_cols={'exposure_weight':2})}
    </div>

    <div class=\"section\">
      <h2>2) 最近 orders</h2>
      <p class=\"muted\">entry / exit / preview 都会记在这里，所以如果暂时还没真钱成交，也能看 runner 最近有没有正常扫到信号。</p>
      {render_table(recent_orders, money_cols={'price','desired_notional_usdt'}, digits_cols={'qty':6})}
    </div>

    <div class=\"section\">
      <h2>3) 最近 rejections</h2>
      <p class=\"muted\">最关键的是看 <code>core3_symbol_conflict_skip</code> 占比高不高；如果大多数 reject 都是这个，说明两条 live lane 撞车比较频繁。</p>
      {render_table(recent_rejections, digits_cols={'exposure_weight':2})}
    </div>

    <div class=\"section\">
      <h2>4) 最近 warnings</h2>
      {render_table(recent_warnings)}
    </div>

    <div class=\"section\">
      <h2>Artifacts</h2>
      <ul>
        <li><a href=\"../../artifacts/rank29_gate_live/rank29_gate_live_status.json\">rank29_gate_live_status.json</a></li>
        <li><a href=\"../../artifacts/rank29_gate_live/rank29_gate_live_vs_shadow.csv\">rank29_gate_live_vs_shadow.csv</a></li>
        <li><a href=\"../../artifacts/rank29_gate_live/rank29_gate_live_recent_orders.json\">rank29_gate_live_recent_orders.json</a></li>
        <li><a href=\"../../artifacts/rank29_gate_live/rank29_gate_live_recent_rejections.json\">rank29_gate_live_recent_rejections.json</a></li>
        <li><a href=\"../../artifacts/rank29_gate_live/rank29_gate_live_warnings.json\">rank29_gate_live_warnings.json</a></li>
      </ul>
    </div>
  </div>
</body>
</html>
"""
    return html


def main() -> int:
    ensure_dir(SITE_DIR)
    OUT_PATH.write_text(build_page(), encoding="utf-8")
    print(OUT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
