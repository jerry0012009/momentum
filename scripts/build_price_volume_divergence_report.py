#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.signals.multi_tf_momentum import (  # noqa: E402
    MultiTfMomentumConfig,
    compute_multi_tf_momentum_signals,
)
from momentum.signals.price_volume_divergence import (  # noqa: E402
    PriceVolumeDivergenceConfig,
    compute_price_volume_divergence_signals,
)
from momentum.analytics.multi_tf_momentum_backtest import (  # noqa: E402
    MultiTfMomentumBacktestConfig,
    evaluate_multi_tf_momentum_reversal,
)


SWEEP_BREAKOUT_LOOKBACKS = [12, 24, 36]
SWEEP_DIVERGENCE_DELTAS = [0.0, 0.5, 1.0]


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def flatten_yf_columns(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    return df


def download_bars(ticker: str, period: str, interval: str) -> pd.DataFrame:
    raw = yf.download(ticker, period=period, interval=interval, auto_adjust=False, progress=False)
    if raw is None or raw.empty:
        raise ValueError(f"No data for {ticker}")
    raw = flatten_yf_columns(raw)
    bars = raw.reset_index().rename(
        columns={
            "Datetime": "timestamp",
            "Date": "timestamp",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        }
    )
    bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True)
    keep = [c for c in ["timestamp", "open", "high", "low", "close", "volume"] if c in bars.columns]
    bars = bars[keep].dropna(subset=["open", "high", "low", "close", "volume"]).sort_values("timestamp").reset_index(drop=True)
    return bars


def load_input_data(input_path: str | None, ticker: str, period: str, interval: str) -> pd.DataFrame:
    if input_path:
        path = Path(input_path)
        if not path.is_absolute():
            path = ROOT / path
        if not path.exists():
            raise ValueError(f"Input not found: {path}")
        df = pd.read_csv(path)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        return df
    return download_bars(ticker=ticker, period=period, interval=interval)


def summarize_variant(summary_df: pd.DataFrame, variant: str, **params) -> dict:
    if summary_df.empty:
        return {
            "variant": variant,
            **params,
            "trades": 0,
            "win_rate": np.nan,
            "avg_ret": np.nan,
            "median_ret": np.nan,
            "total_return": 0.0,
            "max_drawdown": 0.0,
            "long_trades": 0,
            "short_trades": 0,
        }
    row = summary_df.iloc[0].to_dict()
    return {"variant": variant, **params, **row}


def plot_price_warnings(df: pd.DataFrame, path: Path, ticker: str) -> None:
    fig, ax = plt.subplots(figsize=(12, 5))
    ts = pd.to_datetime(df["timestamp"], utc=True)
    ax.plot(ts, df["close"], label="close", linewidth=1.0)
    bear_idx = df["bearish_divergence_event"] == 1
    bull_idx = df["bullish_divergence_event"] == 1
    if bear_idx.any():
        ax.scatter(ts[bear_idx], df.loc[bear_idx, "close"], marker="x", s=28, label="bearish divergence", color="tab:red")
    if bull_idx.any():
        ax.scatter(ts[bull_idx], df.loc[bull_idx, "close"], marker="x", s=28, label="bullish divergence", color="tab:green")
    ax.set_title(f"{ticker} price with divergence warnings")
    ax.grid(alpha=0.2)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_nav_compare(nav_base: pd.DataFrame, nav_filtered: pd.DataFrame, path: Path, ticker: str) -> None:
    fig, ax = plt.subplots(figsize=(12, 4))
    if not nav_base.empty:
        ts = pd.to_datetime(nav_base["timestamp"], utc=True)
        ax.plot(ts, nav_base["nav"], label="baseline", linewidth=1.5)
    if not nav_filtered.empty:
        ts2 = pd.to_datetime(nav_filtered["timestamp"], utc=True)
        ax.plot(ts2, nav_filtered["nav"], label="divergence-filtered", linewidth=1.5)
    ax.set_title(f"{ticker} NAV compare: baseline vs divergence filter")
    ax.grid(alpha=0.2)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_sweep_heatmap(df: pd.DataFrame, path: Path) -> None:
    pivot = df.pivot(index="breakout_lookback", columns="divergence_delta_z", values="total_return").sort_index(ascending=False)
    fig, ax = plt.subplots(figsize=(6, 4.5))
    im = ax.imshow(pivot.values, aspect="auto")
    ax.set_xticks(range(len(pivot.columns)), labels=[str(x) for x in pivot.columns])
    ax.set_yticks(range(len(pivot.index)), labels=[str(x) for x in pivot.index])
    ax.set_xlabel("divergence_delta_z")
    ax.set_ylabel("breakout_lookback")
    ax.set_title("Divergence filter sweep: total return heatmap")
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            ax.text(j, i, f"{pivot.values[i, j] * 100:.1f}%", ha="center", va="center", color="white", fontsize=8)
    fig.colorbar(im, ax=ax, shrink=0.85)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_top_variants(df: pd.DataFrame, path: Path) -> None:
    top = df.sort_values(["total_return", "max_drawdown", "trades"], ascending=[False, False, False]).head(9).copy()
    top["label"] = top.apply(lambda r: f"N{int(r['breakout_lookback'])}|d{r['divergence_delta_z']:.1f}", axis=1)
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.bar(top["label"], top["total_return"])
    ax.set_title("Top divergence filter parameter combos by total return")
    ax.set_ylabel("total_return")
    ax.grid(axis="y", alpha=0.2)
    plt.xticks(rotation=30, ha="right")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def render_html(
    *,
    ticker: str,
    period: str,
    interval: str,
    base_row: dict,
    best_row: dict,
    compare_df: pd.DataFrame,
    sweep_df: pd.DataFrame,
    assets_rel: dict,
    base_cfg: MultiTfMomentumConfig,
    best_cfg: PriceVolumeDivergenceConfig,
    backtest_cfg: MultiTfMomentumBacktestConfig,
) -> str:
    top5 = sweep_df.sort_values(["total_return", "max_drawdown", "trades"], ascending=[False, False, False]).head(5).copy()
    improved = float(best_row.get("total_return", 0.0)) > float(base_row.get("total_return", 0.0))
    q1 = "量价背离更适合做过滤器，而不是直接做反转主信号。" \
        "这版实现专门回答‘要不要追这个弱量突破’。"
    q2 = (
        f"当前样本里，最优过滤组合是 breakout_lookback={int(best_row['breakout_lookback'])}, divergence_delta_z={best_row['divergence_delta_z']:.1f}，"
        f"warning_active_bars={int(best_row['warning_active_bars'])}。"
    )
    q3 = "当前样本里，过滤器相对裸动量有增益。" if improved else "当前样本里，过滤器没有稳定打赢裸动量。"
    q4 = "如果热图里一整片参数都差不多，说明它更像稳定过滤器；如果只有一个点好看，说明还要警惕过拟合。"
    q5 = "研究上先把它当作趋势过滤器保留；后续再考虑更复杂的摆点背离（baseline B）。"

    return f"""
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>Price-Volume Divergence Report</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 32px auto; max-width: 1100px; line-height: 1.6; color: #111; }}
    h1,h2,h3 {{ line-height: 1.25; }}
    .muted {{ color: #666; }}
    .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }}
    .card {{ border: 1px solid #e5e5e5; border-radius: 10px; padding: 14px; background: #fafafa; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 20px; }}
    th, td {{ border: 1px solid #ddd; padding: 8px 10px; text-align: left; font-size: 14px; }}
    th {{ background: #f3f3f3; }}
    img {{ max-width: 100%; border: 1px solid #e5e5e5; border-radius: 8px; margin: 8px 0 20px; }}
    .qa {{ border-left: 4px solid #4f46e5; padding-left: 14px; margin: 18px 0; }}
    code {{ background: #f6f6f6; padding: 2px 6px; border-radius: 6px; }}
  </style>
</head>
<body>
  <h1>量价背离（baseline A）过滤器报告</h1>
  <p class="muted">Ticker: {ticker} · period={period} · interval={interval} · generated_at={datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</p>

  <h2>0. 研究问题</h2>
  <p>这份报告回答的问题不是“量价背离能不能单独抓顶/抓底”，而是：<b>把它作为 multi_tf_momentum 的过滤器，能不能减少弱量突破带来的低质量追单？</b></p>

  <h2>1. baseline 结构</h2>
  <div class="grid">
    <div class="card"><b>base momentum</b><br>{base_cfg.window_5m} / {base_cfg.window_15m} windows<br>th={base_cfg.threshold_5m:.3f}/{base_cfg.threshold_15m:.3f}</div>
    <div class="card"><b>default divergence</b><br>N={best_cfg.breakout_lookback}<br>delta={best_cfg.divergence_delta_z:.1f}<br>z_confirm={best_cfg.z_confirm:.1f}</div>
    <div class="card"><b>warning_active_bars</b><br>{best_cfg.warning_active_bars}<br>fee/slippage={backtest_cfg.fee_bps_per_side:.1f}/{backtest_cfg.slippage_bps_per_side:.1f}bps</div>
  </div>

  <h2>2. 规则定义（baseline A）</h2>
  <ul>
    <li>价格创新高：<code>close[t] &gt; rolling_high(close, N)[t-1]</code></li>
    <li>当前突破的 <code>vol_z</code> 低于上一次向上突破的 <code>vol_z - delta</code></li>
    <li>且当前 <code>vol_z &lt; z_confirm</code></li>
    <li>则记为 <code>bearish_divergence_warning</code>，并在接下来若干根 bar 内屏蔽追多</li>
    <li>空头方向做对称定义</li>
  </ul>

  <h2>3. 裸动量 baseline vs 最优背离过滤器</h2>
  {compare_df.to_html(index=False, float_format=lambda x: f'{x:.4f}')}
  <img src="{assets_rel['nav_compare']}" alt="nav compare" />

  <h2>4. 价格与背离警告示意</h2>
  <img src="{assets_rel['warnings']}" alt="price warnings" />

  <h2>5. 参数扫描（N × delta）</h2>
  {sweep_df.to_html(index=False, float_format=lambda x: f'{x:.4f}')}
  <img src="{assets_rel['heatmap']}" alt="heatmap" />
  <img src="{assets_rel['top']}" alt="top variants" />

  <h2>6. Top 5 参数组合</h2>
  {top5.to_html(index=False, float_format=lambda x: f'{x:.4f}')}

  <h2>7. 文字版研究结论（问题 → 结论 → 动作）</h2>
  <div class="qa">
    <h3>Q1. 量价背离在这里扮演什么角色？</h3>
    <p><b>结论：</b>{q1}</p>
    <p><b>动作：</b>先把它当过滤器研究，不要一上来把它当独立反转系统。</p>
  </div>
  <div class="qa">
    <h3>Q2. 当前样本里最值得保留的参数结构是什么？</h3>
    <p><b>结论：</b>{q2}</p>
    <p><b>动作：</b>后续先围绕这个参数结构做小步扩展，不要一下子引入摆点背离、OBV、MFI 全家桶。</p>
  </div>
  <div class="qa">
    <h3>Q3. 过滤器有没有改善 multi_tf_momentum？</h3>
    <p><b>结论：</b>{q3}</p>
    <p><b>动作：</b>如果改善主要来自减少低质量追单，而不是极端偶然行情，就可以继续保留。</p>
  </div>
  <div class="qa">
    <h3>Q4. 多参数下应该怎么判断它是不是过拟合？</h3>
    <p><b>结论：</b>{q4}</p>
    <p><b>动作：</b>看热图是不是“有一片能打”，而不是只看单点冠军。</p>
  </div>
  <div class="qa">
    <h3>Q5. 这节课之后的研究决策是什么？</h3>
    <p><b>结论：</b>{q5}</p>
    <p><b>动作：</b>当前先把 baseline A 固化进工程结构；baseline B（摆点背离）进入后续学习地图，不急着现在展开。</p>
  </div>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Build price-volume divergence filter report.")
    parser.add_argument("--ticker", default="BTC-USD")
    parser.add_argument("--period", default="60d")
    parser.add_argument("--interval", default="5m")
    parser.add_argument("--input", default=None)
    parser.add_argument("--window-5m", type=int, default=6)
    parser.add_argument("--window-15m", type=int, default=6)
    parser.add_argument("--threshold-5m", type=float, default=0.003)
    parser.add_argument("--threshold-15m", type=float, default=0.006)
    parser.add_argument("--fee-bps-per-side", type=float, default=4.0)
    parser.add_argument("--slippage-bps-per-side", type=float, default=2.0)
    parser.add_argument("--vol-window", type=int, default=20)
    parser.add_argument("--breakout-lookback", type=int, default=24)
    parser.add_argument("--divergence-delta-z", type=float, default=0.5)
    parser.add_argument("--z-confirm", type=float, default=0.5)
    parser.add_argument("--warning-active-bars", type=int, default=3)
    args = parser.parse_args()

    factor = "price_volume_divergence"
    artifacts_dir = ensure_dir(ROOT / "reports" / "artifacts" / factor)
    site_dir = ensure_dir(ROOT / "reports" / "site" / "factors" / factor)
    assets_dir = ensure_dir(site_dir / "assets")

    bars = load_input_data(args.input, args.ticker, args.period, args.interval)
    bars["symbol"] = args.ticker

    base_cfg = MultiTfMomentumConfig(
        window_5m=args.window_5m,
        window_15m=args.window_15m,
        threshold_5m=args.threshold_5m,
        threshold_15m=args.threshold_15m,
    )
    bt_cfg = MultiTfMomentumBacktestConfig(
        fee_bps_per_side=args.fee_bps_per_side,
        slippage_bps_per_side=args.slippage_bps_per_side,
        flip_on_reverse_signal=True,
    )

    base_sig = compute_multi_tf_momentum_signals(bars, config=base_cfg)
    base_bt = evaluate_multi_tf_momentum_reversal(base_sig, config=bt_cfg)
    base_row = summarize_variant(base_bt.summary, "baseline")

    sweep_rows = []
    sweep_details = []
    for n in SWEEP_BREAKOUT_LOOKBACKS:
        for delta in SWEEP_DIVERGENCE_DELTAS:
            cfg = PriceVolumeDivergenceConfig(
                window_5m=args.window_5m,
                window_15m=args.window_15m,
                threshold_5m=args.threshold_5m,
                threshold_15m=args.threshold_15m,
                vol_window=args.vol_window,
                breakout_lookback=n,
                divergence_delta_z=delta,
                z_confirm=args.z_confirm,
                warning_active_bars=args.warning_active_bars,
            )
            sig = compute_price_volume_divergence_signals(bars, config=cfg)
            bt = evaluate_multi_tf_momentum_reversal(sig, config=bt_cfg)
            row = summarize_variant(
                bt.summary,
                "divergence_filter",
                breakout_lookback=n,
                divergence_delta_z=delta,
                z_confirm=args.z_confirm,
                warning_active_bars=args.warning_active_bars,
                bearish_divergence_events=int(sig["bearish_divergence_event"].sum()),
                bullish_divergence_events=int(sig["bullish_divergence_event"].sum()),
                filtered_signal_count=int(sig["long_filtered_out"].sum() + sig["short_filtered_out"].sum()),
                long_filtered_count=int(sig["long_filtered_out"].sum()),
                short_filtered_count=int(sig["short_filtered_out"].sum()),
            )
            sweep_rows.append(row)
            sweep_details.append((cfg, sig, bt, row))

    sweep_df = pd.DataFrame(sweep_rows).sort_values(["total_return", "max_drawdown", "trades"], ascending=[False, False, False]).reset_index(drop=True)
    best_cfg, best_sig, best_bt, best_row = max(
        sweep_details,
        key=lambda x: (float(x[3].get("total_return", 0.0)), float(x[3].get("max_drawdown", -1e9)), int(x[3].get("trades", 0))),
    )

    compare_df = pd.DataFrame([base_row, {"variant": "best_divergence_filter", **best_row}])[
        [
            "variant",
            "breakout_lookback",
            "divergence_delta_z",
            "z_confirm",
            "warning_active_bars",
            "bearish_divergence_events",
            "bullish_divergence_events",
            "filtered_signal_count",
            "trades",
            "win_rate",
            "avg_ret",
            "median_ret",
            "total_return",
            "max_drawdown",
            "long_trades",
            "short_trades",
        ]
    ]
    compare_df.loc[
        compare_df["variant"] == "baseline",
        ["breakout_lookback", "divergence_delta_z", "z_confirm", "warning_active_bars", "bearish_divergence_events", "bullish_divergence_events", "filtered_signal_count"],
    ] = np.nan

    base_nav = base_bt.nav[base_bt.nav["symbol"] == args.ticker] if (not base_bt.nav.empty and "symbol" in base_bt.nav.columns) else base_bt.nav
    best_nav = best_bt.nav[best_bt.nav["symbol"] == args.ticker] if (not best_bt.nav.empty and "symbol" in best_bt.nav.columns) else best_bt.nav

    pd.DataFrame([base_row]).to_csv(artifacts_dir / "baseline_summary.csv", index=False)
    sweep_df.to_csv(artifacts_dir / "param_sweep_summary.csv", index=False)
    compare_df.to_csv(artifacts_dir / "strategy_compare.csv", index=False)
    best_sig.to_csv(artifacts_dir / "best_signal_snapshot.csv", index=False)
    best_bt.trades.to_csv(artifacts_dir / "best_trade_log.csv", index=False)
    best_bt.nav.to_csv(artifacts_dir / "best_nav_curve.csv", index=False)

    warnings_png = assets_dir / "01_price_warnings.png"
    nav_compare_png = assets_dir / "02_nav_compare.png"
    heatmap_png = assets_dir / "03_param_heatmap.png"
    top_png = assets_dir / "04_top_variants.png"

    plot_price_warnings(best_sig, warnings_png, args.ticker)
    plot_nav_compare(base_nav, best_nav, nav_compare_png, args.ticker)
    plot_sweep_heatmap(sweep_df, heatmap_png)
    plot_top_variants(sweep_df, top_png)

    manifest = {
        "ticker": args.ticker,
        "period": args.period,
        "interval": args.interval,
        "base_config": base_cfg.__dict__,
        "best_divergence_config": best_cfg.__dict__,
        "backtest_config": bt_cfg.__dict__,
        "sweep_breakout_lookbacks": SWEEP_BREAKOUT_LOOKBACKS,
        "sweep_divergence_deltas": SWEEP_DIVERGENCE_DELTAS,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    (artifacts_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    html = render_html(
        ticker=args.ticker,
        period=args.period,
        interval=args.interval,
        base_row=base_row,
        best_row=best_row,
        compare_df=compare_df,
        sweep_df=sweep_df,
        assets_rel={
            "warnings": "assets/01_price_warnings.png",
            "nav_compare": "assets/02_nav_compare.png",
            "heatmap": "assets/03_param_heatmap.png",
            "top": "assets/04_top_variants.png",
        },
        base_cfg=base_cfg,
        best_cfg=best_cfg,
        backtest_cfg=bt_cfg,
    )
    (site_dir / "report.html").write_text(html, encoding="utf-8")

    print(f"[ok] report: {site_dir / 'report.html'}")
    print(f"[ok] artifacts: {artifacts_dir}")
    print(f"[ok] baseline total_return={float(base_row.get('total_return', 0.0)):.4f}")
    print(f"[ok] best filter total_return={float(best_row.get('total_return', 0.0)):.4f}")
    print(sweep_df.head(5)[["breakout_lookback", "divergence_delta_z", "filtered_signal_count", "trades", "total_return", "max_drawdown"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
