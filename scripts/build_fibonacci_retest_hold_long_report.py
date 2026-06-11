#!/usr/bin/env python3
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "fibonacci_retest_hold_long"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "fibonacci_retest_hold_long"
SITE_PATH = SITE_DIR / "report.html"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
SAMPLE_DAYS = [60, 120, 180]
HOLD_BARS = [24, 48, 72, 96]
ROUND_TRIP_COST = 0.001
INTERVAL = "15m"
PIVOT_LEFT = 2
PIVOT_RIGHT = 2
INVALIDATION_BARS = 12
RETEST_LOOKAHEAD = 6


@dataclass
class Pivot:
    idx: int
    kind: str
    price: float
    confirm_idx: int


@dataclass
class SwingPair:
    direction: str
    swing_low: float
    swing_high: float
    available_idx: int

    @property
    def fib38(self) -> float:
        if self.direction == "long":
            return self.swing_high - 0.382 * (self.swing_high - self.swing_low)
        return self.swing_low + 0.382 * (self.swing_high - self.swing_low)

    @property
    def fib50(self) -> float:
        return self.swing_low + 0.5 * (self.swing_high - self.swing_low)

    @property
    def zone_low(self) -> float:
        return min(self.fib38, self.fib50)

    @property
    def zone_high(self) -> float:
        return max(self.fib38, self.fib50)


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def pct(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "nan"
    return f"{float(v) * 100:.{digits}f}%"


def download_binance_bars(symbol: str, *, interval: str = INTERVAL, days: int = 180) -> pd.DataFrame:
    end_ms = int(pd.Timestamp.now("UTC").timestamp() * 1000)
    start_ms = end_ms - days * 24 * 60 * 60 * 1000
    url = "https://api.binance.com/api/v3/klines"
    rows: list[list] = []
    current = start_ms

    while current < end_ms:
        qs = urlencode(
            {
                "symbol": symbol,
                "interval": interval,
                "startTime": current,
                "endTime": end_ms,
                "limit": 1000,
            }
        )
        with urlopen(f"{url}?{qs}", timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if not data:
            break
        rows.extend(data)
        current = int(data[-1][6]) + 1
        if len(data) < 1000:
            break

    df = pd.DataFrame(rows, columns=[
        "open_time", "open", "high", "low", "close", "volume", "close_time",
        "quote_asset_volume", "number_of_trades", "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
    ])
    out = pd.DataFrame({
        "timestamp": pd.to_datetime(df["open_time"], unit="ms", utc=True),
        "open": pd.to_numeric(df["open"]),
        "high": pd.to_numeric(df["high"]),
        "low": pd.to_numeric(df["low"]),
        "close": pd.to_numeric(df["close"]),
        "volume": pd.to_numeric(df["volume"]),
    })
    return out.sort_values("timestamp").reset_index(drop=True)


def detect_confirmed_pivots(bars: pd.DataFrame) -> list[Pivot]:
    highs = bars["high"].to_numpy()
    lows = bars["low"].to_numpy()
    pivots: list[Pivot] = []
    n = len(bars)
    for i in range(PIVOT_LEFT, n - PIVOT_RIGHT):
        high_window = highs[i - PIVOT_LEFT : i + PIVOT_RIGHT + 1]
        low_window = lows[i - PIVOT_LEFT : i + PIVOT_RIGHT + 1]
        if highs[i] == np.max(high_window) and np.sum(high_window == highs[i]) == 1:
            pivots.append(Pivot(i, "high", float(highs[i]), i + PIVOT_RIGHT))
        if lows[i] == np.min(low_window) and np.sum(low_window == lows[i]) == 1:
            pivots.append(Pivot(i, "low", float(lows[i]), i + PIVOT_RIGHT))
    pivots.sort(key=lambda p: (p.confirm_idx, p.idx, p.kind))
    return pivots


def build_pair_state(n: int, pivots: list[Pivot]) -> list[dict[str, SwingPair | None]]:
    state: list[dict[str, SwingPair | None]] = []
    p = 0
    last_low: Pivot | None = None
    last_high: Pivot | None = None
    long_pair: SwingPair | None = None
    short_pair: SwingPair | None = None
    for i in range(n):
        while p < len(pivots) and pivots[p].confirm_idx <= i:
            pv = pivots[p]
            if pv.kind == "low":
                last_low = pv
                if last_high is not None and last_high.confirm_idx < pv.confirm_idx:
                    short_pair = SwingPair("short", float(pv.price), float(last_high.price), pv.confirm_idx)
            else:
                last_high = pv
                if last_low is not None and last_low.confirm_idx < pv.confirm_idx:
                    long_pair = SwingPair("long", float(last_low.price), float(pv.price), pv.confirm_idx)
            p += 1
        state.append({"long": long_pair, "short": short_pair})
    return state


def overlaps_zone(low_: float, high_: float, pair: SwingPair) -> bool:
    return low_ <= pair.zone_high and high_ >= pair.zone_low


def favorable_close(close_price: float, pair: SwingPair) -> bool:
    return close_price > pair.fib38 if pair.direction == "long" else close_price < pair.fib38


def build_retest_hold_entries(bars: pd.DataFrame, *, asset: str) -> pd.DataFrame:
    pivots = detect_confirmed_pivots(bars)
    pair_state = build_pair_state(len(bars), pivots)
    rows: list[dict] = []
    n = len(bars)

    for i in range(n):
        row = bars.iloc[i]
        for direction in ("long", "short"):
            pair = pair_state[i][direction]
            if pair is None or i < pair.available_idx:
                continue
            if not overlaps_zone(float(row["low"]), float(row["high"]), pair):
                continue

            reacquire_idx = None
            for j in range(i + 1, min(i + 1 + RETEST_LOOKAHEAD, n)):
                if favorable_close(float(bars.iloc[j]["close"]), pair):
                    reacquire_idx = j
                    break
            if reacquire_idx is None:
                continue

            retest_idx = None
            for r in range(reacquire_idx + 1, min(reacquire_idx + 1 + RETEST_LOOKAHEAD, n)):
                rrow = bars.iloc[r]
                if overlaps_zone(float(rrow["low"]), float(rrow["high"]), pair) and favorable_close(float(rrow["close"]), pair):
                    retest_idx = r
                    break
            if retest_idx is None:
                continue

            entry_idx = retest_idx + 1
            if entry_idx >= n:
                continue
            rows.append({
                "asset": asset,
                "direction": direction,
                "touch_idx": i,
                "entry_idx": entry_idx,
                "touch_timestamp": bars.iloc[i]["timestamp"],
                "entry_timestamp": bars.iloc[entry_idx]["timestamp"],
                "entry_lag_bars": int(entry_idx - i),
                "swing_low": pair.swing_low,
                "swing_high": pair.swing_high,
                "fib38": pair.fib38,
                "fib50": pair.fib50,
            })
    return pd.DataFrame(rows)


def gross_return(entry_open: float, exit_close: float, direction: str) -> float:
    return exit_close / entry_open - 1.0 if direction == "long" else entry_open / exit_close - 1.0


def invalidated(window: pd.DataFrame, *, direction: str, swing_low: float, swing_high: float) -> int:
    if window.empty:
        return 0
    if direction == "long":
        return int(float(window["low"].min()) < swing_low)
    return int(float(window["high"].max()) > swing_high)


def evaluate_holds(bars: pd.DataFrame, entries: pd.DataFrame, *, sample_days: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    summary_rows = []
    all_events = []
    for hold_bars in HOLD_BARS:
        hold_rows = []
        for _, e in entries.iterrows():
            entry_idx = int(e["entry_idx"])
            if entry_idx + hold_bars >= len(bars):
                continue
            entry_open = float(bars.iloc[entry_idx]["open"])
            exit_close = float(bars.iloc[entry_idx + hold_bars]["close"])
            gross = gross_return(entry_open, exit_close, str(e["direction"]))
            inv_end = min(entry_idx + INVALIDATION_BARS, len(bars) - 1)
            inv = invalidated(
                bars.iloc[entry_idx : inv_end + 1],
                direction=str(e["direction"]),
                swing_low=float(e["swing_low"]),
                swing_high=float(e["swing_high"]),
            )
            hold_rows.append({
                **e.to_dict(),
                "sample_days": sample_days,
                "hold_bars": hold_bars,
                "gross_return": gross,
                "net_return": gross - ROUND_TRIP_COST,
                "invalidated_12b": inv,
            })
        ev = pd.DataFrame(hold_rows)
        if ev.empty:
            summary_rows.append({
                "sample_days": sample_days,
                "hold_bars": hold_bars,
                "trade_count": 0,
                "mean_net_return": np.nan,
                "median_net_return": np.nan,
                "win_ratio": np.nan,
                "invalidation_ratio_12b": np.nan,
                "mean_entry_lag_bars": np.nan,
                "positive_asset_ratio": np.nan,
            })
            continue

        by_asset = ev.groupby("asset", as_index=False)["net_return"].mean().rename(columns={"net_return": "asset_mean_net_return"})
        summary_rows.append({
            "sample_days": sample_days,
            "hold_bars": hold_bars,
            "trade_count": int(len(ev)),
            "mean_net_return": float(ev["net_return"].mean()),
            "median_net_return": float(ev["net_return"].median()),
            "win_ratio": float((ev["net_return"] > 0).mean()),
            "invalidation_ratio_12b": float(ev["invalidated_12b"].mean()),
            "mean_entry_lag_bars": float(ev["entry_lag_bars"].mean()),
            "positive_asset_ratio": float((by_asset["asset_mean_net_return"] > 0).mean()),
        })
        all_events.append(ev)

    summary_df = pd.DataFrame(summary_rows)
    events_df = pd.concat(all_events, ignore_index=True) if all_events else pd.DataFrame()
    return summary_df, events_df


def plot_heatmap(matrix: pd.DataFrame, *, title: str, fmt: str, cmap: str, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    data = matrix.to_numpy(dtype=float)
    im = ax.imshow(data, cmap=cmap, aspect="auto")
    ax.set_xticks(range(len(matrix.columns)))
    ax.set_xticklabels([str(c) for c in matrix.columns])
    ax.set_yticks(range(len(matrix.index)))
    ax.set_yticklabels([str(i) for i in matrix.index])
    ax.set_xlabel("hold_bars")
    ax.set_ylabel("sample_days")
    ax.set_title(title)
    for r in range(data.shape[0]):
        for c in range(data.shape[1]):
            v = data[r, c]
            text = "nan" if np.isnan(v) else format(v, fmt)
            ax.text(c, r, text, ha="center", va="center", color="black", fontsize=10)
    fig.colorbar(im, ax=ax, shrink=0.9)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def render_table(df: pd.DataFrame) -> str:
    show = df.copy()
    for col in ["mean_net_return", "median_net_return", "win_ratio", "invalidation_ratio_12b", "positive_asset_ratio"]:
        if col in show.columns:
            show[col] = show[col].map(lambda v: pct(v) if pd.notna(v) else "nan")
    if "mean_entry_lag_bars" in show.columns:
        show["mean_entry_lag_bars"] = show["mean_entry_lag_bars"].map(lambda v: f"{float(v):.2f}" if pd.notna(v) else "nan")
    return show.to_html(index=False, border=0, classes="dataframe")


def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    longest = max(SAMPLE_DAYS)
    base_bars: dict[str, pd.DataFrame] = {}
    for asset, symbol in ASSETS.items():
        print(f"[download] {asset} {longest}d", flush=True)
        b = download_binance_bars(symbol, days=longest)
        b["asset"] = asset
        base_bars[asset] = b

    all_summary = []
    all_events = []
    for days in SAMPLE_DAYS:
        cutoff = pd.Timestamp.now("UTC") - pd.Timedelta(days=days)
        for asset, bars_all in base_bars.items():
            bars = bars_all[bars_all["timestamp"] >= cutoff].copy().reset_index(drop=True)
            print(f"[prepare] {asset} {days}d rows={len(bars)}", flush=True)
            entries = build_retest_hold_entries(bars, asset=asset)
            s_df, e_df = evaluate_holds(bars, entries, sample_days=days)
            if not s_df.empty:
                s_df["asset"] = asset
                all_summary.append(s_df)
            if not e_df.empty:
                all_events.append(e_df)

    per_asset_summary = pd.concat(all_summary, ignore_index=True)
    events_df = pd.concat(all_events, ignore_index=True) if all_events else pd.DataFrame()

    # aggregate over assets
    agg = per_asset_summary.groupby(["sample_days", "hold_bars"], as_index=False).agg(
        trade_count=("trade_count", "sum"),
        mean_net_return=("mean_net_return", "mean"),
        median_net_return=("median_net_return", "mean"),
        win_ratio=("win_ratio", "mean"),
        invalidation_ratio_12b=("invalidation_ratio_12b", "mean"),
        mean_entry_lag_bars=("mean_entry_lag_bars", "mean"),
        positive_asset_ratio=("positive_asset_ratio", "mean"),
    )

    agg = agg.sort_values(["sample_days", "hold_bars"]).reset_index(drop=True)

    agg.to_csv(ART_DIR / "summary.csv", index=False)
    per_asset_summary.to_csv(ART_DIR / "summary_by_asset.csv", index=False)
    events_df.to_csv(ART_DIR / "events.csv", index=False)

    heat_ret = agg.pivot(index="sample_days", columns="hold_bars", values="mean_net_return").sort_index()
    heat_win = agg.pivot(index="sample_days", columns="hold_bars", values="win_ratio").sort_index()
    heat_trades = agg.pivot(index="sample_days", columns="hold_bars", values="trade_count").sort_index()
    plot_heatmap(heat_ret, title="retest_hold mean net return", fmt=".2%", cmap="RdYlGn", out_path=SITE_DIR / "heat_ret.png")
    plot_heatmap(heat_win, title="retest_hold win ratio", fmt=".1%", cmap="Blues", out_path=SITE_DIR / "heat_win.png")
    plot_heatmap(heat_trades, title="retest_hold trade count", fmt=".0f", cmap="Purples", out_path=SITE_DIR / "heat_trades.png")

    best = agg.sort_values(["mean_net_return", "win_ratio", "trade_count"], ascending=[False, False, False]).iloc[0].to_dict()

    # pull 60d old comparison (from previous v2 run with 4 variants, hold=24)
    old_v2 = ROOT / "reports" / "artifacts" / "fibonacci_confirmation_slice_v2" / "summary_by_variant.csv"
    old_compare_html = "<p class='muted'>未找到旧版 60d 对照表。</p>"
    if old_v2.exists():
        old_df = pd.read_csv(old_v2)
        old_compare_html = render_table(old_df[[
            "variant", "trade_count", "mean_net_return", "win_ratio", "invalidation_ratio_12b", "mean_entry_lag_bars", "positive_asset_ratio"
        ]])

    result = {
        "strategy": "retest_hold",
        "best_sample_days": int(best["sample_days"]),
        "best_hold_bars": int(best["hold_bars"]),
        "best_mean_net_return": float(best["mean_net_return"]),
        "best_trade_count": int(best["trade_count"]),
        "best_win_ratio": float(best["win_ratio"]),
    }
    (ART_DIR / "summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    html = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Fibonacci Retest-Hold Extended Backtest</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1160px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111827; background: #f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .muted {{ color:#6b7280; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }}
    img {{ max-width:100%; border:1px solid #e5e7eb; border-radius:12px; background:white; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:16px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; }}
    a {{ color:#2563eb; text-decoration:none; }}
  </style>
</head>
<body>
  <p><a href=\"../../index.html\">← 返回首页</a></p>
  <h1>Fibonacci 回撤策略（retest_hold）扩展回测</h1>
  <p class=\"muted\">生成时间：{generated_at} ｜ Binance 15m（BTC/ETH/SOL）｜ 成本：10bps round-trip</p>

  <div class=\"card\">
    <h2>策略确定</h2>
    <p><span class=\"pill\">final strategy</span><span class=\"pill\">retest_hold</span></p>
    <p>根据前一轮 60d 结果，<b>retest_hold</b> 在收益、胜率、失效率之间最均衡，因此本轮把它定为主策略，并在更长样本（120d / 180d）和更长持有期（24/48/72/96 bars）上做扩展回测。</p>
  </div>

  <div class=\"card\">
    <h2>扩展回测结论</h2>
    <ul>
      <li>当前最优格子：<b>{int(best['sample_days'])}d / 持有 {int(best['hold_bars'])} bars</b></li>
      <li>聚合单笔净收益：<b>{pct(best['mean_net_return'])}</b></li>
      <li>聚合胜率：<b>{pct(best['win_ratio'])}</b></li>
      <li>交易数：<b>{int(best['trade_count'])}</b></li>
    </ul>
    <p class=\"muted\">解释：这说明 retest_hold 在更长样本下仍可继续研究，但它依然更适合作为 confirmation/filter layer，而不是独立主 alpha。</p>
  </div>

  <div class=\"card\">
    <h2>热力图</h2>
    <div class=\"grid\">
      <div><img src=\"heat_ret.png\" alt=\"mean net return\" /></div>
      <div><img src=\"heat_win.png\" alt=\"win ratio\" /></div>
      <div><img src=\"heat_trades.png\" alt=\"trades\" /></div>
    </div>
  </div>

  <div class=\"card\">
    <h2>按样本天数 × 持有期的汇总表</h2>
    {render_table(agg)}
  </div>

  <div class=\"card\">
    <h2>为什么选 retest_hold（引用上一轮 60d 对照）</h2>
    {old_compare_html}
  </div>

  <div class=\"card\">
    <h2>小白版讲解</h2>
    <ol>
      <li>retest_hold 的核心是：先确认方向回来，再等一次回踩不破位再进场。</li>
      <li>这样做通常会减少“刚进就被打脸”的概率，但代价是进场更晚、机会更少。</li>
      <li>扩展回测的重点不是证明“已经稳定赚钱”，而是确认这条规则在更长样本里是否还能保持合理的 trade-off。</li>
    </ol>
  </div>
</body>
</html>
"""
    SITE_PATH.write_text(html, encoding="utf-8")

    print(f"[ok] {SITE_PATH}")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
