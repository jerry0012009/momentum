#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(SRC))

from momentum.signals.trendline_breakout_navigator import (  # noqa: E402
    TrendlineBreakoutNavigatorConfig,
    compute_trendline_breakout_navigator,
)

BASE_SCRIPT = ROOT / "scripts" / "build_rank29_trendline_breakout_clean_replication.py"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank29_trendline_breakout_navigator_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank29_trendline_breakout_navigator_15m"
CACHE_DIR = ART_DIR / "long_window_cache"
PRIMARY_VARIANT = "breakout_align_ge2"
HOLD_BARS = 8
FAILURE_LOOKAHEAD = 4
COSTS = [6.0, 10.0, 15.0, 20.0]
FOCUS_COSTS = [10.0, 15.0]
DEFAULT_3Y_SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "XRPUSDT",
    "ADAUSDT",
    "DOGEUSDT",
    "LTCUSDT",
    "BCHUSDT",
    "ETCUSDT",
    "LINKUSDT",
    "SOLUSDT",
    "AVAXUSDT",
]
DEFAULT_5Y_SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "XRPUSDT",
    "ADAUSDT",
    "DOGEUSDT",
    "LTCUSDT",
    "BCHUSDT",
]
DEFAULT_DAYS = 1095
DEFAULT_TAG = "long_window_stability_3y_expanded"


def load_base_module():
    spec = importlib.util.spec_from_file_location("rank29_base", BASE_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


base_mod = load_base_module()


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
                text = pct(value, digits_cols.get(col, 2))
            elif isinstance(value, (float, np.floating, int, np.integer)) and not isinstance(value, bool):
                text = num(value, digits_cols.get(col, 2))
            else:
                text = str(value)
            cells.append(f"<td>{escape(text)}</td>")
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def build_asset_map(symbols_csv: str) -> dict[str, str]:
    selected: dict[str, str] = {}
    for raw in symbols_csv.split(","):
        symbol = raw.strip().upper()
        if not symbol:
            continue
        if not symbol.endswith("USDT"):
            raise ValueError(f"unsupported symbol {symbol}: expected *USDT")
        selected[symbol.replace("USDT", "-USD")] = symbol
    if not selected:
        raise ValueError("no symbols provided")
    return selected


def fetch_binance_bars(symbol: str, days: int, interval: str = "15m") -> pd.DataFrame:
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
        for attempt in range(5):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "OpenClaw-Rank29-LongWindow/1.0"})
                with urllib.request.urlopen(req, timeout=20) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                break
            except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
                last_error = exc
                time.sleep(1.5 + attempt)
        if data is None:
            raise RuntimeError(f"failed to fetch {symbol} after retries: {last_error}")
        if not data:
            break
        rows.extend(data)
        current = int(data[-1][6]) + 1
        if len(data) < 1000:
            break
        time.sleep(0.05)
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


def load_or_fetch_bars(symbol: str, days: int) -> pd.DataFrame:
    ensure_dir(CACHE_DIR)
    cache_path = CACHE_DIR / f"{symbol}__{days}d__15m.csv"
    if cache_path.exists():
        df = pd.read_csv(cache_path)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        return df.sort_values("timestamp").reset_index(drop=True)
    bars = fetch_binance_bars(symbol, days=days)
    bars.to_csv(cache_path, index=False)
    return bars


def build_frame(asset: str, bars: pd.DataFrame) -> pd.DataFrame:
    bars = bars.copy().sort_values("timestamp").reset_index(drop=True)
    nav = compute_trendline_breakout_navigator(
        bars[["timestamp", "high", "low", "close"]].copy(),
        config=TrendlineBreakoutNavigatorConfig(),
    )
    out = pd.concat(
        [
            bars.reset_index(drop=True),
            nav.drop(columns=["timestamp", "high", "low", "close"], errors="ignore").reset_index(drop=True),
        ],
        axis=1,
    )
    out["asset"] = asset
    return out


def build_no_overlap_trades(full: pd.DataFrame, *, asset: str, cost: float) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    cost_rate = float(cost) / 10000.0
    last_exit = -1
    for idx, row in full.iterrows():
        chosen = base_mod.choose_breakout_event(row, min_abs_composite=2)
        if chosen is None:
            continue
        prefix, direction = chosen
        entry_idx = idx + 1
        exit_idx = min(idx + HOLD_BARS, len(full) - 1)
        if entry_idx >= len(full):
            continue
        if idx <= last_exit:
            continue
        entry_price = float(full.iloc[entry_idx]["open"])
        exit_price = float(full.iloc[exit_idx]["close"])
        gross_ret = (exit_price / entry_price - 1.0) * direction
        net_ret = (1.0 + gross_ret) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
        rows.append(
            {
                "asset": asset,
                "mode": "no_overlap_guard",
                "variant": PRIMARY_VARIANT,
                "cost_bps_per_side": float(cost),
                "event_idx": int(idx),
                "event_ts": pd.to_datetime(full.iloc[idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_ts": pd.to_datetime(full.iloc[entry_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": pd.to_datetime(full.iloc[exit_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "direction": "long" if direction > 0 else "short",
                "trigger_tf": prefix.replace("tbn_", ""),
                "composite_trend": int(row["tbn_composite_trend"]),
                "entry_price": entry_price,
                "exit_price": exit_price,
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "hold_bars": int(exit_idx - entry_idx + 1),
                "false_break_ratio": float(base_mod.detect_line_failure(full, idx, prefix, direction, lookahead=FAILURE_LOOKAHEAD)),
            }
        )
        last_exit = exit_idx
    return pd.DataFrame(rows)


def summarize_trades(trades: pd.DataFrame, *, asset: str, mode: str, cost: float, sample_start: str, sample_end: str, bars: int) -> dict[str, object]:
    if trades.empty:
        return {
            "asset": asset,
            "mode": mode,
            "cost_bps_per_side": float(cost),
            "sample_start": sample_start,
            "sample_end": sample_end,
            "bars": int(bars),
            "trades": 0,
            "win_rate": np.nan,
            "avg_net_ret": np.nan,
            "total_return": 0.0,
            "false_break_ratio": np.nan,
            "short_tf_share": np.nan,
            "long_share": np.nan,
            "short_share": np.nan,
        }
    tf_counts = trades["trigger_tf"].value_counts(normalize=True)
    return {
        "asset": asset,
        "mode": mode,
        "cost_bps_per_side": float(cost),
        "sample_start": sample_start,
        "sample_end": sample_end,
        "bars": int(bars),
        "trades": int(len(trades)),
        "win_rate": float((trades["net_ret"] > 0).mean()),
        "avg_net_ret": float(trades["net_ret"].mean()),
        "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
        "false_break_ratio": float(trades["false_break_ratio"].mean()),
        "short_tf_share": float(tf_counts.get("short", 0.0)),
        "long_share": float((trades["direction"] == "long").mean()),
        "short_share": float((trades["direction"] == "short").mean()),
    }


def build_overall_summary(asset_summary: pd.DataFrame) -> pd.DataFrame:
    if asset_summary.empty:
        return pd.DataFrame()
    out = (
        asset_summary.groupby(["mode", "cost_bps_per_side"], as_index=False)
        .agg(
            assets_tested=("asset", "nunique"),
            positive_assets=("total_return", lambda s: int((s > 0).sum())),
            mean_total_return=("total_return", "mean"),
            median_total_return=("total_return", "median"),
            mean_win_rate=("win_rate", "mean"),
            mean_trades=("trades", "mean"),
            min_trades=("trades", "min"),
            mean_false_break_ratio=("false_break_ratio", "mean"),
        )
        .sort_values(["mode", "cost_bps_per_side"]) 
        .reset_index(drop=True)
    )
    out["positive_asset_ratio"] = out["positive_assets"] / out["assets_tested"].replace(0, np.nan)
    return out


def build_period_summary(trades: pd.DataFrame, *, days: int) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["asset", "mode", "cost_bps_per_side", "window", "total_return", "trades", "win_rate"])
    work = trades.copy()
    work["event_ts"] = pd.to_datetime(work["event_ts"], utc=True)
    rows = []
    if days >= 365 * 3:
        n_windows = max(3, min(5, int(round(days / 365))))
        latest = work["event_ts"].max()
        for asset, grp in work.groupby(["asset", "mode", "cost_bps_per_side"], sort=True):
            asset_name, mode, cost = asset
            for idx in range(n_windows):
                upper = latest - pd.Timedelta(days=365 * idx)
                lower = latest - pd.Timedelta(days=365 * (idx + 1))
                window = grp[(grp["event_ts"] >= lower) & (grp["event_ts"] < upper)]
                if window.empty:
                    continue
                rows.append(
                    {
                        "asset": asset_name,
                        "mode": mode,
                        "cost_bps_per_side": float(cost),
                        "window": f"year_{n_windows - idx}",
                        "total_return": float((1.0 + window["net_ret"]).prod() - 1.0),
                        "trades": int(len(window)),
                        "win_rate": float((window["net_ret"] > 0).mean()),
                    }
                )
    else:
        for (asset_name, mode, cost), grp in work.groupby(["asset", "mode", "cost_bps_per_side"], sort=True):
            latest = grp["event_ts"].max()
            cut_recent = latest - pd.Timedelta(days=min(240, max(60, days // 3)))
            cut_mid = latest - pd.Timedelta(days=min(480, max(120, 2 * days // 3)))
            windows = [
                ("older", grp[grp["event_ts"] < cut_mid]),
                ("middle", grp[(grp["event_ts"] >= cut_mid) & (grp["event_ts"] < cut_recent)]),
                ("recent", grp[grp["event_ts"] >= cut_recent]),
            ]
            for name, window in windows:
                if window.empty:
                    continue
                rows.append(
                    {
                        "asset": asset_name,
                        "mode": mode,
                        "cost_bps_per_side": float(cost),
                        "window": name,
                        "total_return": float((1.0 + window["net_ret"]).prod() - 1.0),
                        "trades": int(len(window)),
                        "win_rate": float((window["net_ret"] > 0).mean()),
                    }
                )
    return pd.DataFrame(rows)


def build_listing_summary(listing_rows: list[dict[str, object]]) -> pd.DataFrame:
    return pd.DataFrame(listing_rows).sort_values(["sample_start", "asset"]).reset_index(drop=True)


def build_verdict(overall_summary: pd.DataFrame, period_summary: pd.DataFrame) -> tuple[str, str]:
    focus = overall_summary[(overall_summary["mode"] == "no_overlap_guard") & (overall_summary["cost_bps_per_side"] == 10.0)]
    if focus.empty:
        return "insufficient", "缺少 no-overlap @10bps 的长窗口结果，先别下结论。"
    row = focus.iloc[0]
    stable_assets = 0
    p = period_summary[(period_summary["mode"] == "no_overlap_guard") & (period_summary["cost_bps_per_side"] == 10.0)]
    if not p.empty:
        for _, grp in p.groupby("asset"):
            pos_ratio = float((grp["total_return"] > 0).mean())
            if pos_ratio >= 0.6:
                stable_assets += 1
    if float(row["positive_asset_ratio"]) >= 0.6 and stable_assets >= max(2, int(np.ceil(row["assets_tested"] * 0.4))):
        return "promising under realistic friction", f"no-overlap @10bps 下有 {int(row['positive_assets'])}/{int(row['assets_tested'])} 个资产为正，而且至少 {stable_assets} 个资产在分段窗口里大部分时期仍为正。"
    if float(row["positive_asset_ratio"]) >= 0.5:
        return "mixed but worth further forward paper", f"no-overlap @10bps 下仍有 {int(row['positive_assets'])}/{int(row['assets_tested'])} 个资产为正，但分段稳定性不足，适合继续 forward paper 而不是直接 live。"
    return "not yet robust enough", "no-overlap @10bps 下不到多数资产为正，不建议直接往 tiny-live 推。"


def build_html(generated_at: str, days: int, symbols: list[str], overall_summary: pd.DataFrame, asset_summary: pd.DataFrame, period_summary: pd.DataFrame, listing_summary: pd.DataFrame, verdict: str, reason: str, tag: str) -> str:
    cost_focus = asset_summary[(asset_summary["mode"] == "no_overlap_guard") & (asset_summary["cost_bps_per_side"].isin(FOCUS_COSTS))].copy()
    period_focus = period_summary[(period_summary["mode"] == "no_overlap_guard") & (period_summary["cost_bps_per_side"].isin(FOCUS_COSTS))].copy()
    overall_view = overall_summary.copy()
    symbol_text = ", ".join(symbols)
    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 29 · Long-window stability · {escape(tag)}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1180px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111827; background: #f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }}
    .muted {{ color:#6b7280; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    a {{ color:#2563eb; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
  </style>
</head>
<body>
  <p><a href='./report.html'>← 返回 Rank 29 主报告</a></p>
  <h1>Rank 29 · Long-window stability</h1>
  <p class='muted'>生成时间：{escape(generated_at)} ｜ tag：<code>{escape(tag)}</code></p>

  <div class='card'>
    <h2>这轮回答什么</h2>
    <ul>
      <li>把 Rank 29 从原来的 <code>120d / BTC+ETH+SOL</code>，扩到更长时间窗与更多币种，先回答“它在更现实摩擦下，跨资产 / 跨年份还站不站得住”。</li>
      <li>资产池：<code>{escape(symbol_text)}</code></li>
      <li>时间窗：最长回看 <code>{days}</code> 天；若 Binance 可用历史不足，就如实按可用样本记录，不做回填幻想。</li>
      <li>比较两种口径：<code>clean_overlap_allowed</code> 与 <code>no_overlap_guard</code>；其中后者更接近你当前手工/实盘会接受的诚实版本。</li>
      <li>重点成本：<code>10bps/side</code>（大币现实口径）和 <code>15bps/side</code>（更保守滑点口径）。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>hard read</h2>
    <p><span class='pill'>{escape(verdict)}</span></p>
    <p class='muted'>{escape(reason)}</p>
  </div>

  <div class='card'>
    <h2>可用历史说明</h2>
    {render_table(listing_summary, digits_cols={'bars':0})}
  </div>

  <div class='card'>
    <h2>总体成本摘要（跨资产）</h2>
    {render_table(overall_view[['mode','cost_bps_per_side','assets_tested','positive_assets','positive_asset_ratio','mean_total_return','median_total_return','mean_win_rate','mean_trades','mean_false_break_ratio']], percent_cols={'positive_asset_ratio','mean_total_return','median_total_return','mean_win_rate','mean_false_break_ratio'}, digits_cols={'assets_tested':0,'positive_assets':0,'cost_bps_per_side':0,'mean_trades':1})}
  </div>

  <div class='card'>
    <h2>重点资产摘要（no-overlap @ 10/15bps）</h2>
    {render_table(cost_focus[['asset','cost_bps_per_side','sample_start','sample_end','trades','total_return','win_rate','avg_net_ret','false_break_ratio']], percent_cols={'total_return','win_rate','avg_net_ret','false_break_ratio'}, digits_cols={'cost_bps_per_side':0,'trades':0})}
  </div>

  <div class='card'>
    <h2>分段稳定性（no-overlap @ 10/15bps）</h2>
    {render_table(period_focus[['asset','cost_bps_per_side','window','total_return','trades','win_rate']], percent_cols={'total_return','win_rate'}, digits_cols={'cost_bps_per_side':0,'trades':0})}
    <p class='muted'>如果是 3y/5y 窗口，这里按年度切片；如果不足 3y，则退化为 older / middle / recent 三段。</p>
  </div>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Build long-window stability page for Rank 29")
    parser.add_argument("--symbols", type=str, default=",".join(DEFAULT_3Y_SYMBOLS), help="Comma-separated USDT symbols")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS)
    parser.add_argument("--tag", type=str, default=DEFAULT_TAG)
    args = parser.parse_args()

    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(CACHE_DIR)

    asset_map = build_asset_map(args.symbols)
    listing_rows: list[dict[str, object]] = []
    asset_rows: list[dict[str, object]] = []
    all_trades: list[pd.DataFrame] = []

    for asset, symbol in asset_map.items():
        bars = load_or_fetch_bars(symbol, days=int(args.days))
        frame = build_frame(asset, bars)
        sample_start = bars["timestamp"].min().strftime("%Y-%m-%d")
        sample_end = bars["timestamp"].max().strftime("%Y-%m-%d")
        listing_rows.append(
            {
                "asset": asset,
                "symbol": symbol,
                "sample_start": sample_start,
                "sample_end": sample_end,
                "bars": int(len(bars)),
            }
        )

        for cost in COSTS:
            clean = base_mod.build_breakout_trades(frame, asset=asset, variant=PRIMARY_VARIANT, min_abs_composite=2, cost=float(cost))
            if not clean.empty:
                clean = clean.copy()
                clean["mode"] = "clean_overlap_allowed"
                all_trades.append(clean)
            asset_rows.append(summarize_trades(clean, asset=asset, mode="clean_overlap_allowed", cost=float(cost), sample_start=sample_start, sample_end=sample_end, bars=len(bars)))

            guarded = build_no_overlap_trades(frame, asset=asset, cost=float(cost))
            if not guarded.empty:
                all_trades.append(guarded)
            asset_rows.append(summarize_trades(guarded, asset=asset, mode="no_overlap_guard", cost=float(cost), sample_start=sample_start, sample_end=sample_end, bars=len(bars)))

    asset_summary = pd.DataFrame(asset_rows)
    trades_df = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    period_summary = build_period_summary(trades_df, days=int(args.days))
    overall_summary = build_overall_summary(asset_summary)
    listing_summary = build_listing_summary(listing_rows)
    verdict, reason = build_verdict(overall_summary, period_summary)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    tag = str(args.tag).strip() or DEFAULT_TAG

    asset_path = ART_DIR / f"{tag}_asset_summary.csv"
    overall_path = ART_DIR / f"{tag}_overall_summary.csv"
    period_path = ART_DIR / f"{tag}_period_summary.csv"
    listing_path = ART_DIR / f"{tag}_listing_summary.csv"
    html_path = SITE_DIR / f"{tag}.html"

    asset_summary.to_csv(asset_path, index=False)
    overall_summary.to_csv(overall_path, index=False)
    period_summary.to_csv(period_path, index=False)
    listing_summary.to_csv(listing_path, index=False)
    html_path.write_text(build_html(generated_at, int(args.days), list(asset_map.values()), overall_summary, asset_summary, period_summary, listing_summary, verdict, reason, tag), encoding="utf-8")

    print(json.dumps({
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "days": int(args.days),
        "symbols": list(asset_map.values()),
        "html": str(html_path),
        "asset_summary_csv": str(asset_path),
        "overall_summary_csv": str(overall_path),
        "period_summary_csv": str(period_path),
        "listing_summary_csv": str(listing_path),
        "verdict": verdict,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
