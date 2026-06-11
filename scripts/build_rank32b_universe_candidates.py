#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import statistics
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank32b_slope_floor_continuation_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank32b_slope_floor_continuation_15m"
OUTPUT_CSV = ART_DIR / "universe_candidate_pool.csv"
OUTPUT_JSON = ART_DIR / "universe_candidate_summary.json"
OUTPUT_HTML = SITE_DIR / "universe_candidates.html"
TOP_24H_FETCH = 60
TOP_POOL = 20
MIN_LISTING_DAYS = 730
FUTURES_EXCHANGE_INFO = "https://fapi.binance.com/fapi/v1/exchangeInfo"
FUTURES_TICKER_24H = "https://fapi.binance.com/fapi/v1/ticker/24hr"
FUTURES_KLINES = "https://fapi.binance.com/fapi/v1/klines"

CURRENT_CANARY_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "LTCUSDT", "NEARUSDT", "XRPUSDT"]


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def fetch_json(url: str) -> object:
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def load_symbol_set(path: Path, field: str = "asset") -> set[str]:
    if not path.exists():
        return set()
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        out = set()
        for row in reader:
            value = (row.get(field) or "").strip()
            if not value:
                continue
            if value.endswith("-USD"):
                out.add(value.replace("-USD", "USDT"))
            else:
                out.add(value)
        return out


def load_metric_map(path: Path) -> dict[str, dict[str, float]]:
    if not path.exists():
        return {}
    out: dict[str, dict[str, float]] = {}
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            asset = (row.get("asset") or "").strip()
            if not asset:
                continue
            symbol = asset.replace("-USD", "USDT") if asset.endswith("-USD") else asset
            try:
                out[symbol] = {
                    "total_return": float(row.get("total_return") or 0.0),
                    "trades": float(row.get("trades") or 0.0),
                    "win_rate": float(row.get("win_rate") or 0.0),
                }
            except ValueError:
                continue
    return out


def history_tier(days: float) -> str:
    if days >= 1825:
        return "5y_ready"
    if days >= 1095:
        return "3y_ready"
    if days >= 365:
        return "1y_ready"
    return "short_history"


def pct(value: float | None, digits: int = 1) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{float(value) * 100:.{digits}f}%"


def money_b(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{float(value) / 1e9:.3f}B"


def rank_note(row: dict[str, object]) -> str:
    notes: list[str] = []
    if row.get("in_candidate_5y"):
        notes.append("已有 5y 候选稳定性")
    elif row.get("in_cross_asset_1y"):
        notes.append("已有 1y 跨资产首筛")
    else:
        notes.append("尚未进入 rank32b 跨资产首筛")

    if row.get("symbol") in CURRENT_CANARY_SYMBOLS:
        notes.append("已在当前/近期实盘白名单")

    tier = row.get("history_tier")
    if tier == "5y_ready":
        notes.append("可做 5y 深挖")
    elif tier == "3y_ready":
        notes.append("可先做 3y/1y 双窗")
    elif tier == "1y_ready":
        notes.append("先做 1y 首筛")
    else:
        notes.append("历史太短，先观察")
    return "；".join(notes)


def fetch_top_liquidity_candidates(limit_24h: int = TOP_24H_FETCH) -> list[dict[str, object]]:
    exchange_info = fetch_json(FUTURES_EXCHANGE_INFO)
    ticker_24h = {row["symbol"]: row for row in fetch_json(FUTURES_TICKER_24H)}

    eligible = []
    now_ms = time.time() * 1000.0
    for row in exchange_info["symbols"]:
        symbol = row.get("symbol", "")
        if row.get("status") != "TRADING":
            continue
        if row.get("contractType") != "PERPETUAL":
            continue
        if row.get("quoteAsset") != "USDT":
            continue
        if not symbol.endswith("USDT"):
            continue
        base = symbol[:-4]
        if not re.fullmatch(r"[A-Z]+", base):
            continue
        ticker = ticker_24h.get(symbol)
        if not ticker:
            continue
        onboard_ms = float(row.get("onboardDate") or 0.0)
        eligible.append(
            {
                "symbol": symbol,
                "base_asset": base,
                "quote_volume_24h": float(ticker.get("quoteVolume") or 0.0),
                "last_price": float(ticker.get("lastPrice") or 0.0),
                "listing_days": (now_ms - onboard_ms) / 1000.0 / 86400.0 if onboard_ms else 0.0,
            }
        )

    eligible.sort(key=lambda x: float(x["quote_volume_24h"]), reverse=True)
    probe = eligible[:limit_24h]
    out = []
    for idx, row in enumerate(probe, start=1):
        symbol = str(row["symbol"])
        params = urllib.parse.urlencode({"symbol": symbol, "interval": "1d", "limit": 30})
        klines = fetch_json(f"{FUTURES_KLINES}?{params}")
        quote_vols = [float(x[7]) for x in klines] if klines else []
        row = dict(row)
        row["rank_24h"] = idx
        row["quote_volume_mean_30d"] = float(sum(quote_vols) / len(quote_vols)) if quote_vols else None
        row["quote_volume_median_30d"] = float(statistics.median(quote_vols)) if quote_vols else None
        row["history_tier"] = history_tier(float(row["listing_days"]))
        out.append(row)
    return out


def build_rows() -> tuple[list[dict[str, object]], dict[str, object]]:
    cross_asset_symbols = load_symbol_set(ART_DIR / "cross_asset_expansion_asset_summary.csv")
    candidate_5y_symbols = load_symbol_set(ART_DIR / "candidate_5y_stability_asset_summary.csv")
    core_symbols = load_symbol_set(ART_DIR / "extended_history_1825d_asset_summary.csv")

    cross_asset_metrics = load_metric_map(ART_DIR / "cross_asset_expansion_asset_summary.csv")
    candidate_5y_metrics = load_metric_map(ART_DIR / "candidate_5y_stability_asset_summary.csv")
    extended_5y_metrics = load_metric_map(ART_DIR / "extended_history_1825d_asset_summary.csv")

    liquidity_rows = fetch_top_liquidity_candidates()
    liquidity_rows.sort(key=lambda x: (float(x.get("quote_volume_median_30d") or 0.0), float(x.get("quote_volume_mean_30d") or 0.0)), reverse=True)

    final_rows: list[dict[str, object]] = []
    for rank_med30, row in enumerate(liquidity_rows, start=1):
        symbol = str(row["symbol"])
        cross_metric = cross_asset_metrics.get(symbol, {})
        cand_metric = candidate_5y_metrics.get(symbol, {})
        ext_metric = extended_5y_metrics.get(symbol, {})
        final_row: dict[str, object] = {
            **row,
            "rank_median_30d": rank_med30,
            "in_current_canary": symbol in CURRENT_CANARY_SYMBOLS,
            "in_core_3_5y": symbol in core_symbols,
            "in_candidate_5y": symbol in candidate_5y_symbols,
            "in_cross_asset_1y": symbol in cross_asset_symbols,
            "cross_asset_1y_total_return": cross_metric.get("total_return"),
            "cross_asset_1y_trades": cross_metric.get("trades"),
            "cross_asset_1y_win_rate": cross_metric.get("win_rate"),
            "candidate_5y_total_return": cand_metric.get("total_return") if cand_metric else ext_metric.get("total_return"),
            "candidate_5y_trades": cand_metric.get("trades") if cand_metric else ext_metric.get("trades"),
            "candidate_5y_win_rate": cand_metric.get("win_rate") if cand_metric else ext_metric.get("win_rate"),
        }
        final_row["eligible_for_top20"] = float(final_row["listing_days"]) >= MIN_LISTING_DAYS
        final_row["research_note"] = rank_note(final_row)
        final_rows.append(final_row)

    top20 = [row for row in final_rows if bool(row["eligible_for_top20"])][:TOP_POOL]
    batch_a_new = [row["symbol"] for row in top20 if not bool(row["in_cross_asset_1y"])]
    batch_b_deepen = [row["symbol"] for row in top20 if bool(row["in_cross_asset_1y"]) and not bool(row["in_candidate_5y"]) and not bool(row["in_core_3_5y"])]
    batch_c_ready = [row["symbol"] for row in top20 if bool(row["in_candidate_5y"]) or bool(row["in_core_3_5y"])]

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "coverage": {
            "core_3_5y_symbols": sorted(core_symbols),
            "candidate_5y_symbols": sorted(candidate_5y_symbols),
            "cross_asset_1y_symbols": sorted(cross_asset_symbols),
            "current_canary_symbols": CURRENT_CANARY_SYMBOLS,
        },
        "selection": {
            "top24h_probe_size": TOP_24H_FETCH,
            "min_listing_days": MIN_LISTING_DAYS,
            "top_pool_size": TOP_POOL,
        },
        "top20_symbols": [row["symbol"] for row in top20],
        "batch_a_new_1y_first_pass": batch_a_new,
        "batch_b_existing_1y_need_deeper_stability": batch_b_deepen,
        "batch_c_already_deep_or_candidate_ready": batch_c_ready,
    }
    return final_rows, summary


def render_table(rows: list[dict[str, object]]) -> str:
    if not rows:
        return "<p class='muted'>暂无数据。</p>"
    headers = [
        "rank30d",
        "symbol",
        "med30d",
        "mean30d",
        "24h",
        "listed_days",
        "history_tier",
        "1y_cross",
        "5y_deep",
        "1y_ret",
        "5y_ret",
        "note",
    ]
    html_rows = []
    for row in rows:
        html_rows.append(
            "<tr>"
            + f"<td>{int(row['rank_median_30d'])}</td>"
            + f"<td>{escape(str(row['symbol']))}</td>"
            + f"<td>{escape(money_b(row.get('quote_volume_median_30d')))}</td>"
            + f"<td>{escape(money_b(row.get('quote_volume_mean_30d')))}</td>"
            + f"<td>{escape(money_b(row.get('quote_volume_24h')))}</td>"
            + f"<td>{int(float(row['listing_days']))}</td>"
            + f"<td>{escape(str(row['history_tier']))}</td>"
            + f"<td>{'yes' if row.get('in_cross_asset_1y') else '-'}</td>"
            + f"<td>{'yes' if (row.get('in_candidate_5y') or row.get('in_core_3_5y')) else '-'}</td>"
            + f"<td>{escape(pct(row.get('cross_asset_1y_total_return')))}</td>"
            + f"<td>{escape(pct(row.get('candidate_5y_total_return')))}</td>"
            + f"<td>{escape(str(row.get('research_note') or ''))}</td>"
            + "</tr>"
        )
    head = "".join(f"<th>{escape(h)}</th>" for h in headers)
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(html_rows)}</tbody></table>"


def build_html(rows: list[dict[str, object]], summary: dict[str, object]) -> str:
    top20 = [row for row in rows if bool(row["eligible_for_top20"])][:TOP_POOL]
    new_batch = [row for row in top20 if not bool(row["in_cross_asset_1y"])]
    deepen_batch = [row for row in top20 if bool(row["in_cross_asset_1y"]) and not bool(row["in_candidate_5y"]) and not bool(row["in_core_3_5y"])]
    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 32b · universe candidates</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1180px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111827; background: #f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .muted {{ color:#6b7280; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; margin-bottom:6px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
  </style>
</head>
<body>
  <p><a href='./report.html'>← 返回 Rank 32b 主报告</a></p>
  <h1>Rank 32b · universe candidates</h1>
  <p class='muted'>生成时间：{escape(str(summary['generated_at_utc']))} ｜ 目的：把当前 32b 已覆盖研究范围、按流动性排序的 20 币候选池、以及下一步批次拆解成一个可直接接首筛的清单。</p>

  <div class='card'>
    <h2>当前研究覆盖</h2>
    <p><span class='pill'>core 3 / 5y</span>{escape(', '.join(summary['coverage']['core_3_5y_symbols']))}</p>
    <p><span class='pill'>candidate 5y</span>{escape(', '.join(summary['coverage']['candidate_5y_symbols']))}</p>
    <p><span class='pill'>cross asset 1y</span>{escape(', '.join(summary['coverage']['cross_asset_1y_symbols']))}</p>
    <p><span class='pill'>current canary/live list</span>{escape(', '.join(summary['coverage']['current_canary_symbols']))}</p>
  </div>

  <div class='card'>
    <h2>20 币候选池（按 30d 中位成交额排序）</h2>
    <p class='muted'>先从 Binance U 本位永续 <code>24h quote volume</code> 前 {TOP_24H_FETCH} 名里取样，再用 <code>30d 日线 quote volume 中位数</code> 重新排序；只保留上市满 {MIN_LISTING_DAYS} 天的币进入首批 20 币池。这样能减少“单日爆量热币”把研究池搞歪。</p>
    {render_table(top20)}
  </div>

  <div class='card'>
    <h2>下一步执行批次</h2>
    <p><span class='pill'>Batch A · 新币首筛</span>{escape(', '.join(summary['batch_a_new_1y_first_pass']) or '无')}</p>
    <p class='muted'>这些币已经进了高流动性前 20，但还没进入过 rank32b 的 1 年跨资产首筛，优先补这批最划算。</p>
    <p><span class='pill'>Batch B · 已有 1y，补深挖稳定性</span>{escape(', '.join(summary['batch_b_existing_1y_need_deeper_stability']) or '无')}</p>
    <p class='muted'>这些币已经证明“不是一眼就坏”，但还没做到 5y / yearly bucket / 参数扰动这一级，适合第二批补深。</p>
    <p><span class='pill'>Batch C · 已较深覆盖</span>{escape(', '.join(summary['batch_c_already_deep_or_candidate_ready']) or '无')}</p>
    <p class='muted'>这些币已经有 core-3 级 5 年结果或 candidate-5y 结果，可以先作为组合层验证的基础盘。</p>
  </div>

  <div class='card'>
    <h2>首批新币（Batch A）明细</h2>
    {render_table(new_batch[:10])}
  </div>

  <div class='card'>
    <h2>已过 1y 首筛、但值得补深挖的币（Batch B）</h2>
    {render_table(deepen_batch[:10])}
  </div>
</body>
</html>
"""


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    rows, summary = build_rows()

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_CSV, index=False)
    OUTPUT_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUTPUT_HTML.write_text(build_html(rows, summary), encoding="utf-8")

    print(f"[ok] csv -> {OUTPUT_CSV}")
    print(f"[ok] json -> {OUTPUT_JSON}")
    print(f"[ok] html -> {OUTPUT_HTML}")
    print(f"[top20] {', '.join(summary['top20_symbols'])}")
    print(f"[batch_a] {', '.join(summary['batch_a_new_1y_first_pass']) or 'none'}")
    print(f"[batch_b] {', '.join(summary['batch_b_existing_1y_need_deeper_stability']) or 'none'}")


if __name__ == "__main__":
    main()
