#!/usr/bin/env python3
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank213_largecap_xs_jump_veto"
SITE_PATH = ROOT / "reports" / "site" / "paper" / "rank213_largecap_xs_jump_veto_ffill_impact_audit.html"

ADMISSION_SUMMARY_PATH = ROOT / "reports" / "artifacts" / "optimization_loop" / "rank213_p2_admission_20260328" / "summary.json"
ADMISSION_TS_PATH = ROOT / "reports" / "artifacts" / "optimization_loop" / "rank213_p2_admission_20260328" / "variant_timeseries.csv"
ADMISSION_GEN_PATH = ROOT / "tmp_rank213_p2_admission_check.py"
KLINE_CACHE_DIR = ART_DIR / "rank213_local_cache" / "klines_15m"

OUT_SUMMARY_PATH = ART_DIR / "rank213_ffill_impact_audit_summary.json"

BASE_URL = "https://fapi.binance.com/fapi/v1/klines"
INTERVAL = "15m"
LIMIT = 1500
COST_BPS = 4.0
VARIANT = "f64_h12_floor150_mult2p0"
FORMATION = 64
HOLD = 12
FLOOR = 0.015
MULT = 2.0


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def to_iso(ts: pd.Timestamp) -> str:
    return ts.tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def load_from_cache_or_api(symbol: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    cache_file = KLINE_CACHE_DIR / f"{symbol}.csv"
    if cache_file.exists():
        df = pd.read_csv(cache_file)
        if {"timestamp", "close"}.issubset(df.columns):
            df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
            df["close"] = pd.to_numeric(df["close"], errors="coerce")
            df = df.dropna(subset=["timestamp", "close"]).drop_duplicates("timestamp").sort_values("timestamp")
            sub = df[(df["timestamp"] >= start) & (df["timestamp"] <= end)].copy()
            if not sub.empty:
                return sub[["timestamp", "close"]].reset_index(drop=True)

    start_ms = int(start.timestamp() * 1000)
    end_ms = int(end.timestamp() * 1000)
    rows = []
    cur = start_ms
    while cur < end_ms:
        qs = urllib.parse.urlencode({
            "symbol": symbol,
            "interval": INTERVAL,
            "startTime": cur,
            "endTime": end_ms,
            "limit": LIMIT,
        })
        url = f"{BASE_URL}?{qs}"
        with urllib.request.urlopen(url, timeout=30) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        if not payload:
            break
        rows.extend(payload)
        last_open = int(payload[-1][0])
        nxt = last_open + 15 * 60 * 1000
        if nxt <= cur:
            break
        cur = nxt
        time.sleep(0.05)

    if not rows:
        return pd.DataFrame(columns=["timestamp", "close"])

    out = pd.DataFrame(rows, columns=[
        "open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume",
        "trade_count", "taker_base", "taker_quote", "ignore",
    ])
    out["timestamp"] = pd.to_datetime(out["open_time"], unit="ms", utc=True)
    out["close"] = pd.to_numeric(out["close"], errors="coerce")
    out = out.dropna(subset=["timestamp", "close"])
    out = out[["timestamp", "close"]].drop_duplicates("timestamp").sort_values("timestamp")
    return out[(out["timestamp"] >= start) & (out["timestamp"] <= end)].reset_index(drop=True)


def build_panel(data_map: dict[str, pd.DataFrame]) -> pd.DataFrame:
    panel = None
    for symbol, df in data_map.items():
        s = df[["timestamp", "close"]].rename(columns={"close": symbol}).set_index("timestamp")
        panel = s if panel is None else panel.join(s, how="outer")
    return panel.sort_index()


def run_variant(close_panel: pd.DataFrame) -> pd.DataFrame:
    ret = close_panel.pct_change()
    rows = []
    i = FORMATION
    while i + HOLD < len(close_panel):
        ts = close_panel.index[i]
        hist = ret.iloc[i - FORMATION + 1:i + 1]
        cumret = close_panel.iloc[i] / close_panel.iloc[i - FORMATION] - 1.0
        universe_med = hist.abs().max().median()
        veto_threshold = max(FLOOR, MULT * float(universe_med if pd.notna(universe_med) else 0.0))

        rank = cumret.sort_values()
        longs = rank.index[-3:].tolist()[::-1]
        shorts_plain = rank.index[:3].tolist()

        short_info = []
        for sym in shorts_plain:
            sym_upbar = float(hist[sym].max()) if sym in hist else np.nan
            short_info.append((sym, sym_upbar))

        eligible = [sym for sym, mx in short_info if pd.notna(mx) and mx <= veto_threshold]
        vetoed = [sym for sym, mx in short_info if pd.notna(mx) and mx > veto_threshold]
        refill = [sym for sym in rank.index if sym not in longs and sym not in shorts_plain]
        shorts_veto = eligible.copy()
        for sym in refill:
            if len(shorts_veto) >= 3:
                break
            mx = float(hist[sym].max())
            if pd.notna(mx) and mx <= veto_threshold:
                shorts_veto.append(sym)
        if len(shorts_veto) < 3:
            for sym in rank.index:
                if sym not in longs and sym not in shorts_veto:
                    shorts_veto.append(sym)
                if len(shorts_veto) >= 3:
                    break

        future = close_panel.iloc[i + HOLD] / close_panel.iloc[i] - 1.0
        long_ret = float(future[longs].mean())
        short_plain_series = -future[shorts_plain]
        short_veto_series = -future[shorts_veto]
        plain_ret = 0.5 * long_ret + 0.5 * float(short_plain_series.mean())
        veto_ret = 0.5 * long_ret + 0.5 * float(short_veto_series.mean())

        rows.append({
            "timestamp": ts,
            "plain_gross_return": plain_ret,
            "veto_gross_return": veto_ret,
            "plain_turnover_x": 1.0,
            "veto_turnover_x": 1.0 + (len(set(shorts_veto) ^ set(shorts_plain)) / 6.0),
            "veto_count": len(vetoed),
        })
        i += HOLD
    return pd.DataFrame(rows)


def summarize_run(run: pd.DataFrame) -> dict:
    if run.empty:
        return {
            "rebalances": 0,
            "plain": {},
            "veto": {},
        }
    plain_net = run["plain_gross_return"] - run["plain_turnover_x"] * (COST_BPS / 10000.0)
    veto_net = run["veto_gross_return"] - run["veto_turnover_x"] * (COST_BPS / 10000.0)
    return {
        "rebalances": int(len(run)),
        "start_utc": to_iso(pd.to_datetime(run["timestamp"], utc=True).min()),
        "end_utc": to_iso(pd.to_datetime(run["timestamp"], utc=True).max()),
        "plain": {
            "net_mean_bps": float(plain_net.mean() * 10000.0),
            "net_cum_pct": float(((1.0 + plain_net).prod() - 1.0) * 100.0),
            "win_rate": float((plain_net > 0).mean() * 100.0),
            "avg_turnover_x": float(run["plain_turnover_x"].mean()),
        },
        "veto": {
            "net_mean_bps": float(veto_net.mean() * 10000.0),
            "net_cum_pct": float(((1.0 + veto_net).prod() - 1.0) * 100.0),
            "win_rate": float((veto_net > 0).mean() * 100.0),
            "avg_turnover_x": float(run["veto_turnover_x"].mean()),
        },
    }


def metric_delta(a: dict, b: dict, key: str) -> float:
    return float(a.get(key, np.nan) - b.get(key, np.nan))


def find_ffill_line(path: Path) -> tuple[int | None, str | None]:
    if not path.exists():
        return None, None
    lines = path.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines, start=1):
        if ".ffill()" in line:
            return i, line.strip()
    return None, None


def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_PATH.parent)

    seed_summary = json.loads(ADMISSION_SUMMARY_PATH.read_text(encoding="utf-8"))
    seed_ts = pd.read_csv(ADMISSION_TS_PATH)
    seed_ts = seed_ts[seed_ts["variant"] == VARIANT].copy()
    seed_ts["timestamp"] = pd.to_datetime(seed_ts["timestamp"], utc=True)

    start = pd.to_datetime(seed_summary["sample_start"], utc=True)
    end = pd.to_datetime(seed_summary["sample_end"], utc=True)
    symbols = seed_summary["symbols"]

    data_map = {sym: load_from_cache_or_api(sym, start, end) for sym in symbols}
    raw_panel = build_panel(data_map)

    panel_ffilled = raw_panel.ffill()
    fill_mask = raw_panel.isna() & panel_ffilled.notna()
    fill_cells = int(fill_mask.sum().sum())
    raw_nan_cells = int(raw_panel.isna().sum().sum())

    with_ffill = panel_ffilled.dropna()
    without_ffill = raw_panel.dropna()

    run_with = run_variant(with_ffill)
    run_without = run_variant(without_ffill)

    with_stats = summarize_run(run_with)
    without_stats = summarize_run(run_without)

    ffill_line, ffill_code = find_ffill_line(ADMISSION_GEN_PATH)

    deltas = {
        "bars_delta": int(len(with_ffill) - len(without_ffill)),
        "rebalances_delta": int(with_stats["rebalances"] - without_stats["rebalances"]),
        "plain_net_mean_bps_delta": metric_delta(with_stats["plain"], without_stats["plain"], "net_mean_bps"),
        "plain_net_cum_pct_delta": metric_delta(with_stats["plain"], without_stats["plain"], "net_cum_pct"),
        "veto_net_mean_bps_delta": metric_delta(with_stats["veto"], without_stats["veto"], "net_mean_bps"),
        "veto_net_cum_pct_delta": metric_delta(with_stats["veto"], without_stats["veto"], "net_cum_pct"),
    }

    material = (
        fill_cells > 0
        or deltas["bars_delta"] != 0
        or deltas["rebalances_delta"] != 0
        or abs(deltas["plain_net_mean_bps_delta"]) > 1e-9
        or abs(deltas["plain_net_cum_pct_delta"]) > 1e-9
        or abs(deltas["veto_net_mean_bps_delta"]) > 1e-9
        or abs(deltas["veto_net_cum_pct_delta"]) > 1e-9
    )

    final_conclusion = "material risk" if material else "harmless engineering leftover"

    review = {
        "scope": "ffill impact audit only; no new research",
        "seed_sample": {
            "start_utc": to_iso(start),
            "end_utc": to_iso(end),
            "symbols": len(symbols),
            "variant": VARIANT,
        },
        "ffill_path": {
            "file": str(ADMISSION_GEN_PATH.relative_to(ROOT)),
            "line": ffill_line,
            "code": ffill_code,
            "step": "build_close_panel: outer-join close panel then .ffill().dropna()",
        },
        "trigger_check": {
            "raw_panel_rows": int(len(raw_panel)),
            "raw_panel_nan_cells": raw_nan_cells,
            "ffill_filled_cells": fill_cells,
            "ffill_triggered_in_seed_sample": bool(fill_cells > 0),
        },
        "with_ffill": {
            "bars_after_dropna": int(len(with_ffill)),
            "summary": with_stats,
        },
        "without_ffill": {
            "bars_after_dropna": int(len(without_ffill)),
            "summary": without_stats,
        },
        "delta": deltas,
        "final_conclusion": final_conclusion,
    }

    OUT_SUMMARY_PATH.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    html = f"""<!doctype html>
<html lang='zh-CN'>
<head>
<meta charset='utf-8' />
<meta name='viewport' content='width=device-width, initial-scale=1' />
<title>Rank213 .ffill() impact audit</title>
<style>
:root{{--bg:#f8fafc;--card:#fff;--fg:#0f172a;--muted:#64748b;--line:#e2e8f0;--warn:#9a3412;--warnbg:#ffedd5;--ok:#166534;--okbg:#dcfce7}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.65 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}}
.wrap{{max-width:1080px;margin:0 auto;padding:28px 18px 64px}} .card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin-bottom:14px}}
h1,h2{{margin:0 0 12px}} .muted{{color:var(--muted)}} code{{background:#eff6ff;border-radius:6px;padding:2px 6px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}} .metric{{border:1px solid var(--line);border-radius:12px;padding:10px 12px}}
.note{{border-left:4px solid var(--warn);background:var(--warnbg);padding:12px 14px;border-radius:10px}} .ok{{border-left-color:var(--ok);background:var(--okbg)}}
pre{{white-space:pre-wrap;background:#f8fafc;border:1px solid var(--line);border-radius:10px;padding:10px}}
a{{color:#0f766e;text-decoration:none}} a:hover{{text-decoration:underline}}
</style>
</head>
<body><div class='wrap'>
<div class='card'>
<h1>Rank213 .ffill() impact audit（seed 样本）</h1>
<p><strong>范围：</strong>只审 <code>.ffill()</code> 路径是否在 seed 样本里产生实际影响，不新增研究。</p>
<p><a href='/momentum/paper/rank213_largecap_xs_jump_veto_honesty_audit.html'>honesty audit</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_asof_universe_long_history_review.html'>asof-universe long-history</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_regime_review.html'>regime_review</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto.html'>runner 页面</a></p>
</div>

<div class='card'>
<h2>1) 哪个文件/步骤使用了 .ffill()</h2>
<p>文件：<code>{review['ffill_path']['file']}</code>，行：<code>{review['ffill_path']['line']}</code></p>
<pre>{review['ffill_path']['code']}</pre>
<p class='muted'>步骤：{review['ffill_path']['step']}</p>
</div>

<div class='card'>
<h2>2) 在 rank213 seed 样本里是否真的触发填充</h2>
<div class='grid'>
<div class='metric'><b>raw panel rows</b><br/>{review['trigger_check']['raw_panel_rows']}</div>
<div class='metric'><b>raw panel NaN cells</b><br/>{review['trigger_check']['raw_panel_nan_cells']}</div>
<div class='metric'><b>ffill filled cells</b><br/>{review['trigger_check']['ffill_filled_cells']}</div>
<div class='metric'><b>triggered?</b><br/>{review['trigger_check']['ffill_triggered_in_seed_sample']}</div>
</div>
</div>

<div class='card'>
<h2>3) 禁用 .ffill() 后，样本长度/换仓数/baseline/veto 指标变化</h2>
<div class='grid'>
<div class='metric'><b>bars (with ffill)</b><br/>{review['with_ffill']['bars_after_dropna']}</div>
<div class='metric'><b>bars (without ffill)</b><br/>{review['without_ffill']['bars_after_dropna']}</div>
<div class='metric'><b>rebalances delta</b><br/>{review['delta']['rebalances_delta']}</div>
<div class='metric'><b>plain net mean delta</b><br/>{review['delta']['plain_net_mean_bps_delta']:.10f} bps</div>
<div class='metric'><b>veto net mean delta</b><br/>{review['delta']['veto_net_mean_bps_delta']:.10f} bps</div>
<div class='metric'><b>veto net cum delta</b><br/>{review['delta']['veto_net_cum_pct_delta']:.10f}%</div>
</div>
<pre>{json.dumps(review['with_ffill']['summary'], ensure_ascii=False, indent=2)}</pre>
<pre>{json.dumps(review['without_ffill']['summary'], ensure_ascii=False, indent=2)}</pre>
</div>

<div class='card'>
<h2>4) 最终结论</h2>
<div class='note'><b>{review['final_conclusion']}</b></div>
</div>
</div></body></html>
"""

    SITE_PATH.write_text(html, encoding="utf-8")

    print(json.dumps({
        "summary_json": str(OUT_SUMMARY_PATH.relative_to(ROOT)),
        "html": str(SITE_PATH.relative_to(ROOT)),
        "final_conclusion": final_conclusion,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
