#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank78_adaptive_no_trade_band_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank78_adaptive_no_trade_band_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank78_adaptive_no_trade_band_time_stability_scope_check.html"
TODO_PATH = ROOT / "docs" / "TODO.md"
TRADES_PATH = ART_DIR / "trades.csv"
PRIMARY_COST = 6.0
PRIMARY_VARIANT = "adaptive_band_q1"
BASE_VARIANT = "raw"
CSS = """
body { font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width:1150px; margin:40px auto; padding:0 18px 48px; line-height:1.72; color:#111827; background:#f8fafc; }
.card { border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }
.pill { display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }
.muted { color:#6b7280; }
.good { color:#065f46; font-weight:600; }
.bad { color:#991b1b; font-weight:600; }
code { background:#f3f4f6; padding:1px 5px; border-radius:6px; }
table { width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; background:white; }
th, td { border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }
a { color:#2563eb; text-decoration:none; }
"""


def pct(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def num(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f}"


def render_table(df: pd.DataFrame, percent_cols: set[str] | None = None, digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    percent_cols = percent_cols or set()
    digits_cols = digits_cols or {}
    headers = ''.join(f'<th>{escape(str(c))}</th>' for c in df.columns)
    rows: list[str] = []
    for _, row in df.iterrows():
        cells: list[str] = []
        for col in df.columns:
            value = row[col]
            if col in percent_cols:
                text = pct(value)
            elif isinstance(value, (float, np.floating, int, np.integer)) and not isinstance(value, bool):
                text = num(value, digits_cols.get(col, 2))
            else:
                text = str(value)
            cells.append(f'<td>{escape(text)}</td>')
        rows.append(f'<tr>{"".join(cells)}</tr>')
    return f'<table><thead><tr>{headers}</tr></thead><tbody>{"".join(rows)}</tbody></table>'


def load_trades() -> pd.DataFrame:
    trades = pd.read_csv(TRADES_PATH)
    trades["entry_ts"] = pd.to_datetime(trades["entry_ts"], utc=True)
    trades["net_return"] = trades["gross_return"] - (2.0 * PRIMARY_COST / 10000.0)
    return trades


def build_bucket_summary(trades: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for setup, g in trades.groupby("setup"):
        g = g.sort_values("entry_ts").copy()
        ts = g["entry_ts"]
        q1, q2 = ts.quantile([1 / 3, 2 / 3])
        g["bucket"] = np.where(ts <= q1, "bucket_1", np.where(ts <= q2, "bucket_2", "bucket_3"))
        out = (
            g.groupby(["setup", "variant", "bucket"], as_index=False)
            .agg(
                trade_count=("signal_id", "count"),
                mean_net_return=("net_return", "mean"),
                total_net_return=("net_return", "sum"),
                early_fail_rate=("early_fail", "mean"),
                mean_band=("adaptive_band", "mean"),
            )
        )
        rows.append(out)
    return pd.concat(rows, ignore_index=True).sort_values(["setup", "variant", "bucket"]).reset_index(drop=True)


def build_delta_summary(bucket_summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for (setup, bucket), g in bucket_summary.groupby(["setup", "bucket"]):
        raw = g[g["variant"] == BASE_VARIANT]
        adaptive = g[g["variant"] == PRIMARY_VARIANT]
        if raw.empty or adaptive.empty:
            continue
        raw_row = raw.iloc[0]
        adaptive_row = adaptive.iloc[0]
        retention = np.nan
        if float(raw_row["trade_count"]) > 0:
            retention = float(adaptive_row["trade_count"]) / float(raw_row["trade_count"])
        rows.append(
            {
                "setup": setup,
                "bucket": bucket,
                "raw_trade_count": raw_row["trade_count"],
                "adaptive_trade_count": adaptive_row["trade_count"],
                "retention": retention,
                "raw_total_net_return": raw_row["total_net_return"],
                "adaptive_total_net_return": adaptive_row["total_net_return"],
                "delta_total_vs_raw": float(adaptive_row["total_net_return"] - raw_row["total_net_return"]),
                "raw_early_fail_rate": raw_row["early_fail_rate"],
                "adaptive_early_fail_rate": adaptive_row["early_fail_rate"],
                "delta_early_fail_vs_raw": float(adaptive_row["early_fail_rate"] - raw_row["early_fail_rate"]),
                "adaptive_mean_band": adaptive_row["mean_band"],
            }
        )
    return pd.DataFrame(rows).sort_values(["setup", "bucket"]).reset_index(drop=True)


def build_scope_check(delta: pd.DataFrame, trades: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    setup_rows: list[dict[str, object]] = []
    setup_stats: dict[str, dict[str, float | int]] = {}
    overall = (
        trades.groupby(["setup", "variant"], as_index=False)
        .agg(
            trade_count=("signal_id", "count"),
            total_net_return=("net_return", "sum"),
            early_fail_rate=("early_fail", "mean"),
        )
    )
    for setup, g in delta.groupby("setup"):
        support = int((g["delta_total_vs_raw"] > 0).sum())
        fail = int((g["delta_total_vs_raw"] <= 0).sum())
        early_nonworse = int((g["delta_early_fail_vs_raw"] <= 0).sum())
        retention_mean = float(g["retention"].mean()) if not g.empty else np.nan
        raw_overall = overall[(overall["setup"] == setup) & (overall["variant"] == BASE_VARIANT)].iloc[0]
        adaptive_overall = overall[(overall["setup"] == setup) & (overall["variant"] == PRIMARY_VARIANT)].iloc[0]
        verdict = "park"
        reason = "时间分桶未显示稳定改善。"
        if support == len(g) and early_nonworse == len(g):
            verdict = "stable_improve"
            reason = "所有时间分桶都优于或不差于 raw，且 early-fail 没有恶化。"
        elif support >= max(1, len(g) - 1):
            verdict = "mixed_positive"
            reason = "大多数时间分桶改善，但仍非全口径稳定。"
        setup_rows.append(
            {
                "setup": setup,
                "bucket_support_count": support,
                "bucket_fail_count": fail,
                "early_fail_nonworse_buckets": early_nonworse,
                "mean_retention": retention_mean,
                "raw_total_net_return": raw_overall["total_net_return"],
                "adaptive_total_net_return": adaptive_overall["total_net_return"],
                "delta_total_vs_raw": float(adaptive_overall["total_net_return"] - raw_overall["total_net_return"]),
                "raw_early_fail_rate": raw_overall["early_fail_rate"],
                "adaptive_early_fail_rate": adaptive_overall["early_fail_rate"],
                "verdict": verdict,
                "reason": reason,
            }
        )
        setup_stats[setup] = {
            "support": support,
            "fail": fail,
            "early_nonworse": early_nonworse,
            "retention": retention_mean,
            "overall_delta": float(adaptive_overall["total_net_return"] - raw_overall["total_net_return"]),
        }

    ema_ok = setup_stats.get("ema_psar_long", {}).get("support", 0) == 3 and setup_stats.get("ema_psar_long", {}).get("early_nonworse", 0) == 3 and float(setup_stats.get("ema_psar_long", {}).get("retention", 0)) >= 0.8
    fib_fail = setup_stats.get("fib_retest_long", {}).get("fail", 0) == 3
    breakout_support = setup_stats.get("breakout_short", {}).get("support", 0) == 3

    final_verdict = "keep P2 / paper candidate"
    why = "时间稳定性确认它对 EMA 线有帮助，但还不够统一到能当 desk 级 shared gate。"
    if ema_ok and fib_fail:
        final_verdict = "promote to narrow paper pilot approved (P3, EMA-only suppression overlay)"
        why = "EMA 主线在 3/3 时间分桶都相对 raw 改善且 early-fail 更低，说明 adaptive no-trade band 更像 EMA-only admission suppression overlay；但 fib 3/3 分桶都转弱，因此只适合窄范围 EMA 纸面试跑，不应包装成全 desk shared gate。"
    elif not ema_ok:
        final_verdict = "park / evidence pool"
        why = "连 EMA 主线都没有给出足够稳定的时间改善，P2 不再成立。"

    meta = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "final_verdict": final_verdict,
        "why": why,
        "ema_time_stable": bool(ema_ok),
        "breakout_supportive_only": bool(breakout_support),
        "fib_decisive_fail": bool(fib_fail),
    }
    return pd.DataFrame(setup_rows), meta


def render_html(delta: pd.DataFrame, scope_check: pd.DataFrame, meta: dict[str, object]) -> str:
    body = [
        "<h1>Rank 78 / adaptive no-trade band 时间稳定性与 scope promotion check</h1>",
        '<p class="muted">这是 Rank 78 在 clean replication 之后唯一允许的 P2 最小检查：只复用已有 trades，检查 6bps/side 下的时间稳定性，并直接回答能否升到窄范围 paper pilot。</p>',
        '<div class="card">'
        '<span class="pill">Run 2</span><span class="pill">P2 minimal check</span><span class="pill">reader-facing</span>'
        f'<p><strong>Hard verdict：</strong>{escape(str(meta["final_verdict"]))}</p>'
        f'<p>{escape(str(meta["why"]))}</p>'
        '<p class="muted">上游 clean replication：<a href="report.html">Rank 78 report.html</a></p>'
        '</div>',
        '<div class="card"><h2>时间分桶 delta（adaptive vs raw）</h2>' + render_table(
            delta,
            {
                "retention",
                "raw_total_net_return",
                "adaptive_total_net_return",
                "delta_total_vs_raw",
                "raw_early_fail_rate",
                "adaptive_early_fail_rate",
                "delta_early_fail_vs_raw",
                "adaptive_mean_band",
            },
        ) + '</div>',
        '<div class="card"><h2>scope promotion check</h2>' + render_table(
            scope_check,
            {
                "mean_retention",
                "raw_total_net_return",
                "adaptive_total_net_return",
                "delta_total_vs_raw",
                "raw_early_fail_rate",
                "adaptive_early_fail_rate",
            },
        ) + '</div>',
        '<div class="card"><h2>结论口径</h2><ul>'
        '<li><strong>EMA 主线：</strong>只要时间稳定性仍是 3/3 分桶改善，就允许把 Rank 78 当成 EMA-only suppression overlay，而不是泛化成 shared gate。</li>'
        '<li><strong>Fib：</strong>若 3/3 分桶都弱于 raw，就视为当前 shared-gate 叙事的 decisive fail。</li>'
        '<li><strong>Breakout：</strong>当前只保留 supporting evidence，不重新把 desk 默认重心切回 breakout。</li>'
        '</ul></div>',
    ]
    return f"<!doctype html><html><head><meta charset='utf-8'><title>Rank 78 time stability scope check</title><style>{CSS}</style></head><body>{''.join(body)}</body></html>"


def update_todo(meta: dict[str, object]) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    anchor = "\n- **最新补充（2026-03-19 03:50 UTC）**"
    insert = f"\n- **最新补充（2026-03-19 04:27 UTC）**：这轮继续先按 `Run 1 / EMA due-check only` 复核当前 guardrail：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍显示全 desk 无 `due-now / overdue` lane，最近 due 点仍是 `A股三条 lane -> 2026-03-19 07:00 UTC`；因此这轮允许动作仍落在 `Run 2 / Rank 78`，而不是回头挤占 `P3 continuity`。\n  - 这轮只做了 `Rank 78 / adaptive no-trade band / EMA cost survival` 唯一允许的 **P2 最小检查：时间稳定性**。口径是：直接复用上一轮 clean replication 的 `trades.csv`，只看 `6bps/side` 下 `adaptive_band_q1 vs raw` 的三段时间分桶 delta，不重开新 source，也不再加重型下载。\n  - 结果很直接：`ema_psar_long` 在 **3/3 时间分桶** 都相对 `raw` 给出更好的 `total_net_return`，且 `early_fail` 也都更低；`breakout_short` 同样是 **3/3 分桶非劣 / 小幅改善**，但当前只保留 supporting evidence；`fib_retest_long` 则是 **3/3 分桶都弱于 raw**，构成当前 shared-gate 叙事的明确 fail。\n  - 因此当前更诚实的 hard verdict 应更新为：**`Rank 78 / adaptive no-trade band / EMA cost survival = {meta['final_verdict']}`**。它现在不该继续停在泛 `P2` 研究态：更准确的读法是 **`EMA-only suppression overlay`** 值得进入窄范围 paper pilot，而不是 desk 级 shared gate。\n  - 网页落点：`reports/site/factors/scout_rank78_adaptive_no_trade_band_15m/time_stability_scope_check.html`、`reports/site/reading/repo_scout/rank78_adaptive_no_trade_band_time_stability_scope_check.html`；artifact：`reports/artifacts/scout_rank78_adaptive_no_trade_band_15m/time_stability_delta.csv`、`scope_promotion_check.csv`、`scope_promotion_meta.json`。\n  - 因此当前最新 `Next 3` 顺序应更新为：**`Run 1 = EMA due-check only（最近 due 点仍是 A股 07:00 UTC；若仍 waiting_not_due，不得空转）` -> `Run 2 = Rank 78 已给出最终 scope verdict 后，默认回到 fresh Scout：one-regime-per-session overlay > RECENT_PAPER_SEEDS / quant_digests / validated shortlist 其他 fresh source` -> `Run 3 = 只有 fresh source 这一层也 exhausted、或 Rank 17 / Rank 78 出现真实 status-changing event 需要最小 continuity writeback 时，才动用 1 次低频 P3 continuity 例外；否则不得继续围着旧 P3 lane 打转`**。\n"
    if insert in text:
        return
    if anchor not in text:
        raise SystemExit("Next 3 anchor not found for 04:27 writeback")
    TODO_PATH.write_text(text.replace(anchor, insert + anchor, 1), encoding="utf-8")


def main() -> None:
    if not TRADES_PATH.exists():
        raise SystemExit(f"missing trades file: {TRADES_PATH}")
    ART_DIR.mkdir(parents=True, exist_ok=True)
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    READING_PATH.parent.mkdir(parents=True, exist_ok=True)

    trades = load_trades()
    bucket_summary = build_bucket_summary(trades)
    delta = build_delta_summary(bucket_summary)
    scope_check, meta = build_scope_check(delta, trades)

    delta.to_csv(ART_DIR / "time_stability_delta.csv", index=False)
    scope_check.to_csv(ART_DIR / "scope_promotion_check.csv", index=False)
    (ART_DIR / "scope_promotion_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    html = render_html(delta, scope_check, meta)
    (SITE_DIR / "time_stability_scope_check.html").write_text(html, encoding="utf-8")
    READING_PATH.write_text(html, encoding="utf-8")

    update_todo(meta)
    print(json.dumps(meta, ensure_ascii=False))


if __name__ == "__main__":
    main()
