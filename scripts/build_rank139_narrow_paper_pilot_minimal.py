#!/usr/bin/env python3
"""Rank139 hosted narrow paper pilot — minimal ledger/monitoring/refresh artifacts.

Goal (from TRADING DESK BOARD):
- Treat Rank139 as Scout Seat mainline candidate promoted to P3.
- Provide *visible* pilot artifacts (ledger/monitor board/refresh clock) without turning this into a huge research rerun.

This script:
- assumes `scripts/build_rank139_cusum_event_bar_confirm_veto_clean_replication.py` already ran and produced:
  - reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/trade_log.csv
  - reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/summary_by_arm.csv
  - reports/site/factors/scout_rank139_cusum_event_bar_confirm_veto_15m/report.html
- derives a small monitoring board (default: arm=confirm_same_dir_only, thr_mult=0.8)
- writes a tiny HTML landing page for ops-style scanning.

NOTE: This is intentionally "paper pilot" style visibility; it is not an execution system.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank139_cusum_event_bar_confirm_veto_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank139_cusum_event_bar_confirm_veto_15m"

TRADES_PATH = ART_DIR / "trade_log.csv"
SUMMARY_PATH = ART_DIR / "summary_by_arm.csv"
OUT_MONITOR_CSV = ART_DIR / "narrow_paper_pilot_monitoring_board.csv"
OUT_REFRESH_JSON = ART_DIR / "narrow_paper_pilot_refresh_clock.json"
OUT_PAGE = SITE_DIR / "narrow_paper_monitoring_board.html"

DEFAULT_THR_MULT = 0.8
DEFAULT_ARM = "confirm_same_dir_only"
COST_BPS = 6.0

CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 24px auto; max-width: 1180px; line-height: 1.55; color: #1f2937; padding: 0 16px 40px; }
h1,h2,h3 { color: #111827; }
code { background: #f3f4f6; padding: 0.1rem 0.3rem; border-radius: 4px; }
table { border-collapse: collapse; width: 100%; margin: 16px 0; }
th, td { border: 1px solid #d1d5db; padding: 8px 10px; text-align: left; vertical-align: top; }
th { background: #f3f4f6; }
.card { background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 10px; padding: 14px 16px; margin: 16px 0; }
.muted { color: #6b7280; }
.good { color: #065f46; font-weight: 600; }
.bad { color: #991b1b; font-weight: 600; }
"""


def ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def pct(v: float | None, digits: int = 1) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def num(v: float | None, digits: int = 4) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f}"


def render_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "<p class='muted'>暂无数据。</p>"
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows = []
    for _, r in df.iterrows():
        tds = "".join(f"<td>{escape(str(r[c]))}</td>" for c in df.columns)
        rows.append(f"<tr>{tds}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    if not TRADES_PATH.exists() or not SUMMARY_PATH.exists():
        raise FileNotFoundError(
            "Missing rank139 artifacts. Run scripts/build_rank139_cusum_event_bar_confirm_veto_clean_replication.py first."
        )

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    trades = pd.read_csv(TRADES_PATH)
    summary = pd.read_csv(SUMMARY_PATH)

    # Pick the desk-default gate: confirm_same_dir_only @ thr_mult=0.8
    pick = summary[(summary["thr_mult"] == DEFAULT_THR_MULT) & (summary["arm"] == DEFAULT_ARM)].copy()
    if pick.empty:
        # fallback: just take best arm for 0.8 by mean_net@6bps
        pick = (
            summary[summary["thr_mult"] == DEFAULT_THR_MULT]
            .dropna(subset=["mean_net@6bps"])
            .sort_values("mean_net@6bps", ascending=False)
            .head(1)
            .copy()
        )

    gate_line = "-"
    if not pick.empty:
        row = pick.iloc[0]
        gate_line = f"thr_mult={row['thr_mult']} | arm={row['arm']} | mean_net@6bps={num(row.get('mean_net@6bps'))} | retention={pct(row.get('retention_vs_base'), 1)} | no_event_timeout={pct(row.get('no_event_timeout'), 1)}"

    # Trades-level monitoring (trades table already contains event_{mult} columns)
    event_col = f"event_{DEFAULT_THR_MULT}"
    if event_col not in trades.columns:
        # keep the page alive even if the trade log came from an older version
        event_cols = [c for c in trades.columns if c.startswith("event_")]
        raise ValueError(f"Missing {event_col} in trade_log.csv. Found event cols: {event_cols}")

    # Compute monitoring rows by asset×setup
    group_cols = ["asset", "setup"]
    out_rows = []
    for (asset, setup), g in trades.groupby(group_cols, dropna=False):
        g = g.copy()
        gross = pd.to_numeric(g.get("gross_ret"), errors="coerce")
        net = (1.0 + gross) * (1.0 - COST_BPS / 10000.0) * (1.0 - COST_BPS / 10000.0) - 1.0

        base_n = int(len(g))
        kept = g[g[event_col] == "same_dir_first"].copy()
        kept_n = int(len(kept))
        kept_gross = pd.to_numeric(kept.get("gross_ret"), errors="coerce")
        kept_net = (1.0 + kept_gross) * (1.0 - COST_BPS / 10000.0) * (1.0 - COST_BPS / 10000.0) - 1.0

        out_rows.append(
            {
                "asset": asset,
                "setup": setup,
                "thr_mult": DEFAULT_THR_MULT,
                "arm": DEFAULT_ARM,
                "base_trades": base_n,
                "kept_trades": kept_n,
                "retention": (kept_n / base_n) if base_n else None,
                "mean_net_base@6bps": float(net.mean()) if base_n else None,
                "mean_net_kept@6bps": float(kept_net.mean()) if kept_n else None,
                "no_event_timeout_rate": float((g[event_col] == "no_event_timeout").mean()) if base_n else None,
                "same_dir_first_rate": float((g[event_col] == "same_dir_first").mean()) if base_n else None,
                "opp_dir_first_rate": float((g[event_col] == "opp_dir_first").mean()) if base_n else None,
            }
        )

    monitor = pd.DataFrame(out_rows).sort_values(["asset", "setup"]).reset_index(drop=True)

    # Friendly formatted columns for CSV (keep raw + percent)
    monitor_out = monitor.copy()
    for c in ["retention", "no_event_timeout_rate", "same_dir_first_rate", "opp_dir_first_rate"]:
        monitor_out[c] = monitor_out[c].astype(float)
        monitor_out[c + "_pct"] = monitor_out[c].map(lambda x: pct(x, 1))

    OUT_MONITOR_CSV.write_text(monitor_out.to_csv(index=False), encoding="utf-8")

    clock = {
        "generated_at_utc": generated_at,
        "policy": {
            "thr_mult": DEFAULT_THR_MULT,
            "arm": DEFAULT_ARM,
            "note": "ops visibility snapshot; not an execution engine",
        },
        "inputs": {
            "trade_log": str(TRADES_PATH.relative_to(ROOT)),
            "summary_by_arm": str(SUMMARY_PATH.relative_to(ROOT)),
        },
    }
    OUT_REFRESH_JSON.write_text(json.dumps(clock, ensure_ascii=False, indent=2), encoding="utf-8")

    # Minimal HTML landing page
    summary_cols = [
        "thr_mult",
        "arm",
        "trades",
        "retention_vs_base",
        "mean_net@6bps",
        "positive_ratio_net",
        "no_event_timeout",
    ]
    summary_small = summary[summary_cols].copy()
    for c in ["retention_vs_base", "positive_ratio_net", "no_event_timeout"]:
        summary_small[c] = summary_small[c].map(lambda x: pct(x, 1))
    summary_small["mean_net@6bps"] = summary_small["mean_net@6bps"].map(lambda x: pct(x, 2))

    monitor_show = monitor[[
        "asset",
        "setup",
        "base_trades",
        "kept_trades",
        "retention",
        "mean_net_base@6bps",
        "mean_net_kept@6bps",
        "no_event_timeout_rate",
    ]].copy()
    monitor_show["retention"] = monitor_show["retention"].map(lambda x: pct(x, 1))
    monitor_show["no_event_timeout_rate"] = monitor_show["no_event_timeout_rate"].map(lambda x: pct(x, 1))
    monitor_show["mean_net_base@6bps"] = monitor_show["mean_net_base@6bps"].map(lambda x: pct(x, 2))
    monitor_show["mean_net_kept@6bps"] = monitor_show["mean_net_kept@6bps"].map(lambda x: pct(x, 2))

    body = f"""
<h1>Rank 139 · narrow paper pilot monitoring board (minimal)</h1>
<p class='muted'>generated_at: <code>{escape(generated_at)}</code></p>

<div class='card'>
  <b>当前默认 gate（desk board）：</b>
  <p><code>{escape(gate_line)}</code></p>
  <ul>
    <li>report（research / clean replication）：<a href='report.html'>report.html</a></li>
    <li>artifact：<code>reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/narrow_paper_pilot_monitoring_board.csv</code></li>
    <li>refresh clock：<code>.../narrow_paper_pilot_refresh_clock.json</code></li>
  </ul>
  <p class='muted'>说明：本页的定位是把 Rank139 作为 P3 候选的“可见性面板”。它不替代真正的 paper ledger / broker 适配。</p>
  <p class='muted'>当前统计口径：`gross_ret / mean_net_*` 基于 <code>latency_end → exit</code> 的残余收益（T+3→T+8 style），不再把前 45m 分组窗口计入被比较收益。</p>
</div>

<h2>monitoring board（asset×setup）</h2>
{render_table(monitor_show)}

<h2>research summary（all arms / all thr_mult）</h2>
{render_table(summary_small)}
"""

    OUT_PAGE.write_text(
        f"<!doctype html><html><head><meta charset='utf-8'><title>Rank139 narrow paper pilot monitoring</title><style>{CSS}</style></head><body>{body}</body></html>",
        encoding="utf-8",
    )

    print(f"[rank139-pilot] wrote {OUT_MONITOR_CSV}")
    print(f"[rank139-pilot] wrote {OUT_PAGE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
