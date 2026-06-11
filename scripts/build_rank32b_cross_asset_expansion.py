#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timezone
from html import escape
from pathlib import Path
import importlib.util

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BASE_SCRIPT = ROOT / "scripts" / "build_rank32_ema_slope_clean_replication.py"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank32b_slope_floor_continuation_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank32b_slope_floor_continuation_15m"
CACHE_DIR = ART_DIR / "cross_asset_cache"
OUTPUT_HTML = SITE_DIR / "cross_asset_expansion.html"
PRIMARY_VARIANT = "ema_cross_plus_slope_floor"
PRIMARY_COST = 6.0
DEFAULT_DAYS = 365
DEFAULT_INTERVAL = "15m"
MARKER_ID = "rank32b-cross-asset-expansion"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
    "BNB-USD": "BNBUSDT",
    "XRP-USD": "XRPUSDT",
    "ADA-USD": "ADAUSDT",
    "DOGE-USD": "DOGEUSDT",
    "LINK-USD": "LINKUSDT",
    "AVAX-USD": "AVAXUSDT",
    "LTC-USD": "LTCUSDT",
    "TRX-USD": "TRXUSDT",
    "BCH-USD": "BCHUSDT",
    "ATOM-USD": "ATOMUSDT",
    "NEAR-USD": "NEARUSDT",
    "UNI-USD": "UNIUSDT",
    "ETC-USD": "ETCUSDT",
    "DOT-USD": "DOTUSDT",
}


def load_base_module():
    spec = importlib.util.spec_from_file_location("rank32_base", BASE_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


mod = load_base_module()


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


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
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = []
        for col in df.columns:
            value = row[col]
            if col in percent_cols:
                text = pct(value)
            elif isinstance(value, (float, np.floating, int, np.integer)) and not isinstance(value, bool):
                text = num(value, digits_cols.get(col, 2))
            else:
                text = str(value)
            cells.append(f"<td>{escape(text)}</td>")
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def fetch_binance_bars(symbol: str, days: int, interval: str = DEFAULT_INTERVAL) -> pd.DataFrame:
    end_ms = int(time.time() * 1000)
    start_ms = end_ms - days * 24 * 60 * 60 * 1000
    rows: list[list] = []
    current = start_ms
    while current < end_ms:
        params = urllib.parse.urlencode(
            {
                "symbol": symbol,
                "interval": interval,
                "startTime": current,
                "endTime": end_ms,
                "limit": 1000,
            }
        )
        url = f"https://api.binance.com/api/v3/klines?{params}"
        data = None
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                with urllib.request.urlopen(url, timeout=20) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                break
            except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
                last_error = exc
                time.sleep(1 + attempt)
        if data is None:
            raise RuntimeError(f"failed to fetch {symbol} klines after retries: {last_error}")
        if not data:
            break
        rows.extend(data)
        current = int(data[-1][6]) + 1
        if len(data) < 1000:
            break
    df = pd.DataFrame(
        rows,
        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "number_of_trades",
            "taker_buy_base_asset_volume",
            "taker_buy_quote_asset_volume",
            "ignore",
        ],
    )
    out = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(df["open_time"], unit="ms", utc=True),
            "open": pd.to_numeric(df["open"], errors="coerce"),
            "high": pd.to_numeric(df["high"], errors="coerce"),
            "low": pd.to_numeric(df["low"], errors="coerce"),
            "close": pd.to_numeric(df["close"], errors="coerce"),
            "volume": pd.to_numeric(df["volume"], errors="coerce"),
        }
    )
    return out.dropna().sort_values("timestamp").reset_index(drop=True)


def load_or_fetch_bars(asset: str, symbol: str, days: int, refresh: bool) -> pd.DataFrame:
    ensure_dir(CACHE_DIR)
    cache_path = CACHE_DIR / f"{symbol}__{days}d__{DEFAULT_INTERVAL}.csv"
    if cache_path.exists() and not refresh:
        df = pd.read_csv(cache_path)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        return df.sort_values("timestamp").reset_index(drop=True)
    print(f"[fetch] {asset} {symbol} {days}d")
    df = fetch_binance_bars(symbol, days=days, interval=DEFAULT_INTERVAL)
    df.to_csv(cache_path, index=False)
    return df


def build_frame(asset: str, bars: pd.DataFrame) -> pd.DataFrame:
    frame = bars.copy().sort_values("timestamp").reset_index(drop=True)
    frame["asset"] = asset
    market = frame[["timestamp", "close"]].copy().rename(columns={"close": "close_1h_src"}).set_index("timestamp")
    market_1h = market.resample("1h").last().dropna().reset_index()
    market_1h["ema_fast_1h"] = market_1h["close_1h_src"].ewm(span=mod.EMA_FAST_1H, adjust=False).mean()
    market_1h["ema_slow_1h"] = market_1h["close_1h_src"].ewm(span=mod.EMA_SLOW_1H, adjust=False).mean()
    market_1h["fast_slope"] = market_1h["ema_fast_1h"].pct_change()
    market_1h["slow_slope"] = market_1h["ema_slow_1h"].pct_change()
    frame = pd.merge_asof(frame, market_1h.sort_values("timestamp"), on="timestamp", direction="backward")
    frame["spread_mid"] = (frame["ema_fast_1h"] + frame["ema_slow_1h"]) / 2.0
    frame["long_structure"] = (frame["ema_fast_1h"] > frame["ema_slow_1h"]).fillna(False).astype(int)
    frame["short_structure"] = (frame["ema_fast_1h"] < frame["ema_slow_1h"]).fillna(False).astype(int)
    frame["slope_floor_long"] = ((frame["fast_slope"] > mod.SLOPE_FLOOR) & (frame["slow_slope"] > 0)).fillna(False).astype(int)
    frame["slope_floor_short"] = ((frame["fast_slope"] < -mod.SLOPE_FLOOR) & (frame["slow_slope"] < 0)).fillna(False).astype(int)
    frame["slope_strength"] = frame["fast_slope"].abs().fillna(0.0) + frame["slow_slope"].abs().fillna(0.0)
    prev_close = frame["close"].shift(1)
    prev_fast = frame["ema_fast_1h"].shift(1)
    frame["cross_only_long"] = ((frame["long_structure"] == 1) & (prev_close <= prev_fast) & (frame["close"] > frame["ema_fast_1h"])).fillna(False).astype(int)
    frame["cross_only_short"] = ((frame["short_structure"] == 1) & (prev_close >= prev_fast) & (frame["close"] < frame["ema_fast_1h"])).fillna(False).astype(int)
    frame["slope_floor_long_signal"] = ((frame["cross_only_long"] == 1) & (frame["slope_floor_long"] == 1)).astype(int)
    frame["slope_floor_short_signal"] = ((frame["cross_only_short"] == 1) & (frame["slope_floor_short"] == 1)).astype(int)
    return frame


def build_time_bucket_summary(trades: pd.DataFrame, bucket_count: int = 4) -> pd.DataFrame:
    if trades.empty or len(trades) < max(24, bucket_count * 3):
        return pd.DataFrame(columns=["time_bucket", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_win_rate"])
    work = trades.copy()
    work["event_ts"] = pd.to_datetime(work["event_ts"], utc=True)
    work["time_bucket"] = pd.qcut(
        work["event_ts"].view("int64"),
        q=bucket_count,
        labels=[f"bucket_{i}" for i in range(1, bucket_count + 1)],
        duplicates="drop",
    )
    rows = []
    for bucket, grp in work.groupby("time_bucket", sort=False, observed=False):
        asset_total = grp.groupby("asset")["net_ret"].apply(lambda s: float((1.0 + s).prod() - 1.0))
        rows.append(
            {
                "time_bucket": str(bucket),
                "mean_total_return": float(asset_total.mean()) if len(asset_total) else np.nan,
                "positive_asset_ratio": float((asset_total > 0).mean()) if len(asset_total) else np.nan,
                "mean_trades": float(grp.groupby("asset").size().mean()) if len(grp) else np.nan,
                "mean_win_rate": float(grp.groupby("asset")["net_ret"].apply(lambda s: (s > 0).mean()).mean()) if len(grp) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def build_cost_stability_summary(asset_summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for cost, grp in asset_summary.groupby("cost_bps_per_side", sort=True):
        returns = grp["total_return"].to_numpy(dtype=float)
        rows.append(
            {
                "cost_bps_per_side": int(cost),
                "asset_count": int(len(grp)),
                "positive_asset_ratio": float(np.nanmean(returns > 0)) if len(returns) else np.nan,
                "mean_total_return": float(np.nanmean(returns)) if len(returns) else np.nan,
                "median_total_return": float(np.nanmedian(returns)) if len(returns) else np.nan,
                "worst_asset_return": float(np.nanmin(returns)) if len(returns) else np.nan,
                "best_asset_return": float(np.nanmax(returns)) if len(returns) else np.nan,
                "mean_trades": float(grp["trades"].mean()) if len(grp) else np.nan,
                "mean_no_trade_ratio": float(grp["no_trade_ratio"].mean()) if len(grp) else np.nan,
                "mean_win_rate": float(grp["win_rate"].mean()) if len(grp) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def build_cross_asset_verdict(cost_summary: pd.DataFrame, primary_asset_summary: pd.DataFrame) -> tuple[str, str]:
    if cost_summary.empty or primary_asset_summary.empty:
        return "insufficient", "扩展币种样本不足，当前还不能形成稳定性判断。"
    primary = cost_summary[cost_summary["cost_bps_per_side"] == int(PRIMARY_COST)]
    if primary.empty:
        return "insufficient", "缺少 6bps 主成本档结果，无法评价跨币种稳定性。"
    row = primary.iloc[0]
    pos_ratio = float(row["positive_asset_ratio"])
    mean_ret = float(row["mean_total_return"])
    worst_ret = float(row["worst_asset_return"])
    mean_trades = float(row["mean_trades"])
    positive_assets = int((primary_asset_summary["total_return"] > 0).sum())
    total_assets = int(len(primary_asset_summary))
    if pos_ratio >= 0.66 and mean_ret > 0 and worst_ret > -0.20 and mean_trades >= 40:
        return "cross-asset pocket exists", f"扩展到 {total_assets} 个币种后，6bps 下仍有 {positive_assets}/{total_assets} 个币种为正，且均值、最差腿与交易密度都还在可讨论范围。"
    if pos_ratio >= 0.50 and mean_ret > 0:
        return "mixed stability", f"扩展后仍有 {positive_assets}/{total_assets} 个币种为正，但稳定性明显弱于原来的 BTC/ETH/SOL 三腿，应该把它理解成 selective universe，而不是 broad market alpha。"
    return "fragile outside core legs", f"扩展后只有 {positive_assets}/{total_assets} 个币种为正，说明这条线更像少数核心币种 pocket，不适合把原 verdict 外推到宽 universe。"


def build_html(
    generated_at: str,
    days: int,
    cost_summary: pd.DataFrame,
    primary_asset_summary: pd.DataFrame,
    time_summary: pd.DataFrame,
    verdict: str,
    reason: str,
) -> str:
    primary_row = cost_summary[cost_summary["cost_bps_per_side"] == int(PRIMARY_COST)].iloc[0]
    headline = (
        f"扩到 {int(primary_row['asset_count'])} 个币种后，6bps/side 下 mean_total_return≈{pct(primary_row['mean_total_return'])}、"
        f"positive_asset_ratio≈{pct(primary_row['positive_asset_ratio'])}、mean_trades≈{num(primary_row['mean_trades'],1)}、"
        f"worst_asset_return≈{pct(primary_row['worst_asset_return'])}。"
    )
    asset_view = primary_asset_summary.copy().sort_values("total_return", ascending=False).reset_index(drop=True)
    asset_view["cost_bps_per_side"] = asset_view["cost_bps_per_side"].astype(int)
    cost_view = cost_summary.copy()
    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 32b · Cross-Asset Expansion</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1180px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111827; background: #f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }}
    .muted {{ color:#6b7280; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    a {{ color:#2563eb; text-decoration:none; }}
  </style>
</head>
<body>
  <p><a href='./report.html'>← 返回 Rank 32b 主报告</a></p>
  <h1>Rank 32b · Cross-Asset Expansion</h1>
  <p class='muted'>生成时间：{escape(generated_at)} ｜ 样本：Binance spot 15m ｜ 窗口：最近 {days} 天 ｜ 用途：检查原三腿结论能否外推到更多主流币</p>

  <div class='card'>
    <h2>这轮做了什么</h2>
    <ul>
      <li>保留原始骨架不变：<code>EMA cross + aligned slope floor</code>。</li>
      <li>把资产 universe 从 <code>BTC/ETH/SOL</code> 扩到 <code>BTC/ETH/SOL/BNB/XRP/ADA/DOGE/LINK/AVAX/LTC/TRX/BCH/ATOM/NEAR/UNI/ETC/DOT</code>。</li>
      <li>执行口径仍是 <code>next-bar open / hold 8 bars / non-overlap</code>，不混入新的规则优化。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>hard read</h2>
    <p><span class='pill'>{escape(verdict)}</span></p>
    <p><b>{escape(headline)}</b></p>
    <p class='muted'>{escape(reason)}</p>
  </div>

  <div class='card'>
    <h2>成本稳定性总表</h2>
    {render_table(cost_view[["cost_bps_per_side","asset_count","mean_total_return","median_total_return","positive_asset_ratio","worst_asset_return","best_asset_return","mean_trades","mean_no_trade_ratio","mean_win_rate"]], percent_cols={"mean_total_return","median_total_return","positive_asset_ratio","worst_asset_return","best_asset_return","mean_no_trade_ratio","mean_win_rate"}, digits_cols={"mean_trades":1})}
  </div>

  <div class='card'>
    <h2>6bps 分资产摘要</h2>
    {render_table(asset_view[["asset","cost_bps_per_side","trades","total_return","win_rate","no_trade_ratio","false_reclaim_ratio","long_share","short_share"]], percent_cols={"total_return","win_rate","no_trade_ratio","false_reclaim_ratio","long_share","short_share"}, digits_cols={"trades":0})}
  </div>

  <div class='card'>
    <h2>6bps 时间分桶稳定性</h2>
    {render_table(time_summary[["time_bucket","mean_total_return","positive_asset_ratio","mean_trades","mean_win_rate"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_win_rate"}, digits_cols={"mean_trades":1})}
  </div>

  <div class='card'>
    <h2>怎么解读</h2>
    <ul>
      <li>如果扩到更多币种后，<code>positive_asset_ratio</code> 还维持得住，说明这条线不只是三腿特例。</li>
      <li>如果均值为正但最差币种明显拖后腿，就更适合理解成“需要 asset filter 的 selective alpha”。</li>
      <li>如果一扩 universe 就塌，那原结论仍然只应限于核心大币，不该直接外推到更宽的轮动池。</li>
    </ul>
  </div>
</body>
</html>
"""


def inject_report_summary(report_path: Path, generated_at: str, days: int, cost_summary: pd.DataFrame, verdict: str, reason: str) -> None:
    if not report_path.exists():
        return
    primary = cost_summary[cost_summary["cost_bps_per_side"] == int(PRIMARY_COST)].iloc[0]
    block = f"""
  <div class='card'>
    <h2>cross-asset expansion</h2>
    <p class='muted'>新增时间：{escape(generated_at)} ｜ 窗口：最近 {days} 天 ｜ 目的：检查原三腿结论能否外推到更多主流币。</p>
    <p><span class='pill'>{escape(verdict)}</span></p>
    <p><b>扩到 {int(primary['asset_count'])} 个币种后，6bps/side 下 mean_total_return≈{pct(primary['mean_total_return'])}、positive_asset_ratio≈{pct(primary['positive_asset_ratio'])}、worst_asset_return≈{pct(primary['worst_asset_return'])}。</b></p>
    <p class='muted'>{escape(reason)}</p>
    <p><a href='./cross_asset_expansion.html'>查看完整跨币种稳定性页面</a></p>
  </div>"""
    html = report_path.read_text(encoding="utf-8")
    start_marker = f"<!-- {MARKER_ID}:start -->"
    end_marker = f"<!-- {MARKER_ID}:end -->"
    wrapped = f"{start_marker}\n{block}\n{end_marker}"
    if start_marker in html and end_marker in html:
        left = html.split(start_marker)[0]
        right = html.split(end_marker, 1)[1]
        html = left + wrapped + right
    else:
        html = html.replace("</body>", wrapped + "\n</body>")
    report_path.write_text(html, encoding="utf-8")


def build_asset_map(symbols_csv: str | None) -> dict[str, str]:
    if not symbols_csv:
        return dict(ASSETS)
    selected: dict[str, str] = {}
    for raw in symbols_csv.split(','):
        symbol = raw.strip().upper()
        if not symbol:
            continue
        if not symbol.endswith('USDT'):
            raise ValueError(f"unsupported symbol {symbol}: expected *USDT perpetual symbol")
        asset = symbol.replace('USDT', '-USD')
        selected[asset] = symbol
    if not selected:
        raise ValueError('no symbols provided')
    return selected


def output_path(kind: str, tag: str) -> Path:
    if kind == 'html':
        return SITE_DIR / f"{tag}.html"
    return ART_DIR / f"{tag}_{kind}.csv"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build cross-asset expansion page for Rank 32b.")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--symbols", type=str, default=None, help="Comma-separated USDT perpetual symbols, e.g. XRPUSDT,DOGEUSDT")
    parser.add_argument("--output-tag", type=str, default="cross_asset_expansion", help="Output stem/tag for csv/html artifacts")
    parser.add_argument("--inject-report", action="store_true", help="Inject summary block into main report even for custom symbol runs")
    args = parser.parse_args()

    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(CACHE_DIR)

    asset_map = build_asset_map(args.symbols)
    tag = str(args.output_tag).strip() or 'cross_asset_expansion'

    asset_rows = []
    primary_trades = []
    skipped_assets: list[dict[str, str]] = []
    for asset, symbol in asset_map.items():
        try:
            bars = load_or_fetch_bars(asset, symbol, days=int(args.days), refresh=bool(args.refresh))
        except Exception as exc:
            skipped_assets.append({"asset": asset, "symbol": symbol, "error": str(exc)})
            print(f"[skip] {asset} {symbol}: {exc}")
            continue
        frame = build_frame(asset, bars)
        for cost in mod.COSTS:
            trades, no_trade_ratio, eligible_bars = mod.build_trades(frame, asset, PRIMARY_VARIANT, cost)
            row = mod.summarize_asset(
                trades,
                asset=asset,
                variant=PRIMARY_VARIANT,
                cost_bps=cost,
                no_trade_ratio=no_trade_ratio,
                eligible_bars=eligible_bars,
            )
            asset_rows.append(row)
            if cost == PRIMARY_COST and not trades.empty:
                primary_trades.append(trades)

    asset_summary = pd.DataFrame(asset_rows)
    cost_summary = build_cost_stability_summary(asset_summary)
    primary_asset_summary = asset_summary[asset_summary["cost_bps_per_side"] == PRIMARY_COST].reset_index(drop=True)
    primary_trades_df = pd.concat(primary_trades, ignore_index=True) if primary_trades else pd.DataFrame()
    time_summary = build_time_bucket_summary(primary_trades_df, bucket_count=4)
    verdict, reason = build_cross_asset_verdict(cost_summary, primary_asset_summary)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    cost_path = output_path('cost_summary', tag)
    asset_path = output_path('asset_summary', tag)
    trades_path = output_path('primary_trades', tag)
    time_path = output_path('time_buckets', tag)
    skipped_path = output_path('skipped_assets', tag)
    html_path = output_path('html', tag)

    cost_summary.to_csv(cost_path, index=False)
    asset_summary.to_csv(asset_path, index=False)
    primary_trades_df.to_csv(trades_path, index=False)
    time_summary.to_csv(time_path, index=False)
    pd.DataFrame(skipped_assets).to_csv(skipped_path, index=False)

    html_path.write_text(
        build_html(
            generated_at=generated_at,
            days=int(args.days),
            cost_summary=cost_summary,
            primary_asset_summary=primary_asset_summary,
            time_summary=time_summary,
            verdict=verdict,
            reason=reason,
        ),
        encoding="utf-8",
    )

    should_inject = bool(args.inject_report) or (args.symbols is None and tag == 'cross_asset_expansion')
    if should_inject:
        inject_report_summary(SITE_DIR / "report.html", generated_at, int(args.days), cost_summary, verdict, reason)
        reading_report = ROOT / "reports" / "site" / "reading" / "trendline_alpha_scout" / "rank32b_slope_floor_continuation_clean_replication.html"
        inject_report_summary(reading_report, generated_at, int(args.days), cost_summary, verdict, reason)

    print(
        json.dumps(
            {
                "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "days": int(args.days),
                "asset_count": int(len(asset_map)),
                "assets_completed": int(primary_asset_summary["asset"].nunique()) if not primary_asset_summary.empty else 0,
                "assets_skipped": int(len(skipped_assets)),
                "html": str(html_path),
                "asset_summary_csv": str(asset_path),
                "cost_summary_csv": str(cost_path),
                "verdict": verdict,
                "symbols": [symbol for symbol in asset_map.values()],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
