#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "fibonacci_retest_hold_long"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "fibonacci_retest_hold_long"
SITE_PATH = SITE_DIR / "report.html"
EVENTS_PATH = ART_DIR / "events.csv"
OLD_V2_PATH = ROOT / "reports" / "artifacts" / "fibonacci_confirmation_slice_v2" / "summary_by_variant.csv"


def pct(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "nan"
    return f"{float(v) * 100:.{digits}f}%"


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
    for col in ["mean_net_return", "median_net_return", "win_ratio", "invalidation_ratio_12b", "positive_asset_ratio", "mean_total_return", "median_total_return", "total_return"]:
        if col in show.columns:
            show[col] = show[col].map(lambda v: pct(v) if pd.notna(v) else "nan")
    if "mean_entry_lag_bars" in show.columns:
        show["mean_entry_lag_bars"] = show["mean_entry_lag_bars"].map(lambda v: f"{float(v):.2f}" if pd.notna(v) else "nan")
    return show.to_html(index=False, border=0, classes="dataframe")


def main() -> int:
    df = pd.read_csv(EVENTS_PATH, parse_dates=["touch_timestamp", "entry_timestamp"])
    asset_rows = []
    kept_rows = []
    for (days, hold, asset), sub in df.groupby(["sample_days", "hold_bars", "asset"]):
        sub = sub.sort_values(["entry_idx", "touch_idx"]).reset_index(drop=True)
        keep = []
        current_end = -1
        for _, r in sub.iterrows():
            if int(r.entry_idx) > current_end:
                keep.append(r)
                current_end = int(r.entry_idx) + int(r.hold_bars)
        kept = pd.DataFrame(keep)
        if kept.empty:
            continue
        kept_rows.append(kept)
        total_return = float((1 + kept["net_return"]).prod() - 1)
        asset_rows.append(
            {
                "sample_days": int(days),
                "hold_bars": int(hold),
                "asset": asset,
                "trade_count": int(len(kept)),
                "mean_net_return": float(kept["net_return"].mean()),
                "median_net_return": float(kept["net_return"].median()),
                "win_ratio": float((kept["net_return"] > 0).mean()),
                "total_return": total_return,
                "invalidation_ratio_12b": float(kept["invalidated_12b"].mean()),
                "mean_entry_lag_bars": float(kept["entry_lag_bars"].mean()),
            }
        )

    kept_df = pd.concat(kept_rows, ignore_index=True)
    asset_df = pd.DataFrame(asset_rows)
    agg = asset_df.groupby(["sample_days", "hold_bars"], as_index=False).agg(
        trade_count=("trade_count", "sum"),
        mean_net_return=("mean_net_return", "mean"),
        median_net_return=("median_net_return", "mean"),
        win_ratio=("win_ratio", "mean"),
        mean_total_return=("total_return", "mean"),
        median_total_return=("total_return", "median"),
        positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
        invalidation_ratio_12b=("invalidation_ratio_12b", "mean"),
        mean_entry_lag_bars=("mean_entry_lag_bars", "mean"),
    ).sort_values(["sample_days", "hold_bars"]).reset_index(drop=True)

    agg.to_csv(ART_DIR / "portfolio_summary.csv", index=False)
    asset_df.to_csv(ART_DIR / "portfolio_summary_by_asset.csv", index=False)
    kept_df.to_csv(ART_DIR / "portfolio_events.csv", index=False)

    heat_ret = agg.pivot(index="sample_days", columns="hold_bars", values="mean_net_return").sort_index()
    heat_total = agg.pivot(index="sample_days", columns="hold_bars", values="mean_total_return").sort_index()
    heat_trades = agg.pivot(index="sample_days", columns="hold_bars", values="trade_count").sort_index()
    plot_heatmap(heat_ret, title="portfolio mean net return", fmt=".2%", cmap="RdYlGn", out_path=SITE_DIR / "portfolio_heat_ret.png")
    plot_heatmap(heat_total, title="portfolio mean total return", fmt=".1%", cmap="RdYlGn", out_path=SITE_DIR / "portfolio_heat_total.png")
    plot_heatmap(heat_trades, title="portfolio trade count", fmt=".0f", cmap="Purples", out_path=SITE_DIR / "portfolio_heat_trades.png")

    best = agg.sort_values(["mean_total_return", "mean_net_return", "win_ratio"], ascending=[False, False, False]).iloc[0].to_dict()
    best_asset_df = asset_df[(asset_df.sample_days == int(best["sample_days"])) & (asset_df.hold_bars == int(best["hold_bars"]))].copy()

    old_compare_html = "<p class='muted'>未找到旧版 60d 变体对照。</p>"
    if OLD_V2_PATH.exists():
        old_df = pd.read_csv(OLD_V2_PATH)
        old_compare_html = render_table(old_df[["variant", "trade_count", "mean_net_return", "win_ratio", "invalidation_ratio_12b", "mean_entry_lag_bars", "positive_asset_ratio"]])

    best_days = int(best["sample_days"])
    best_hold = int(best["hold_bars"])
    best_hold_hours = best_hold * 15 / 60
    best_eth = best_asset_df[best_asset_df["asset"] == "ETH-USD"].iloc[0].to_dict() if not best_asset_df[best_asset_df["asset"] == "ETH-USD"].empty else None
    best_btc = best_asset_df[best_asset_df["asset"] == "BTC-USD"].iloc[0].to_dict() if not best_asset_df[best_asset_df["asset"] == "BTC-USD"].empty else None
    best_sol = best_asset_df[best_asset_df["asset"] == "SOL-USD"].iloc[0].to_dict() if not best_asset_df[best_asset_df["asset"] == "SOL-USD"].empty else None

    summary_json = {
        "strategy": "retest_hold",
        "portfolio_rule": "one-position-per-asset-no-overlap",
        "best_sample_days": best_days,
        "best_hold_bars": best_hold,
        "best_mean_net_return": float(best["mean_net_return"]),
        "best_mean_total_return": float(best["mean_total_return"]),
        "best_trade_count": int(best["trade_count"]),
    }
    (ART_DIR / "portfolio_summary.json").write_text(json.dumps(summary_json, ensure_ascii=False, indent=2))

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    html = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Fibonacci Retest-Hold Portfolio Backtest</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1180px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111827; background: #f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .muted {{ color:#6b7280; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }}
    img {{ max-width:100%; border:1px solid #e5e7eb; border-radius:12px; background:white; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:16px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    a {{ color:#2563eb; text-decoration:none; }}
  </style>
</head>
<body>
  <p><a href=\"../../index.html\">← 返回首页</a></p>
  <h1>Fibonacci 回撤策略（retest_hold）扩展策略回测</h1>
  <p class=\"muted\">生成时间：{generated_at} ｜ Binance 15m（BTC/ETH/SOL）｜ 成本：10bps round-trip ｜ 规则：同一资产同一时间只保留一笔仓位，不允许重叠开仓。</p>

  <div class=\"card\">
    <h2>先说结论</h2>
    <p><span class=\"pill\">strategy chosen</span><span class=\"pill\">retest_hold</span><span class=\"pill\">portfolio-gated</span></p>
    <p><b>策略确定：</b>根据前一轮 Fibonacci 变体比较，主策略定为 <code>retest_hold</code>：先恢复到有利方向，再等一次回踩确认后进场。</p>
    <p><b>扩展回测最优格子：</b><b>{best_days}d / 持有 {best_hold} bars</b>（约 {best_hold_hours:.1f} 小时）。在“每个资产同一时间只持有一笔”的更像真实交易的口径下，这个格子的聚合表现约为：<b>单笔净收益 {pct(best['mean_net_return'])}</b>、<b>平均总收益 {pct(best['mean_total_return'])}</b>、<b>交易数 {int(best['trade_count'])}</b>。</p>
  </div>

  <div class=\"card\">
    <h2>一句话摘要（最容易理解的版本）</h2>
    <p><b>你可以把这条策略理解成：</b>不是价格一碰 Fibonacci 回撤位就买，而是要先看到它 <b>回到有利方向</b>，再等一次 <b>回踩但没破坏结构</b>，下一根再进场。</p>
    <ul>
      <li><b>什么时候信号出现？</b> 当价格先摸到回撤区（38.2%~50%），随后重新站回有利方向，并在 6 根 K 线内再次回踩该区但收盘没走坏。</li>
      <li><b>信号出现后我该做什么？</b> 下一根 K 线开盘进场；如果是多头结构就做多，如果是空头结构就做空。</li>
      <li><b>拿多久？</b> 这次最优组合是拿 <b>{best_hold} bars</b>，也就是大约 <b>{best_hold_hours:.1f} 小时</b>。</li>
      <li><b>收益大概怎么样？</b> 在最优组合里，平均每笔约 <b>{pct(best['mean_net_return'])}</b>，三资产平均总收益约 <b>{pct(best['mean_total_return'])}</b>，共做了 <b>{int(best['trade_count'])}</b> 笔。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>Q &amp; A（人话版）</h2>
    <h3>Q1：到底什么叫“信号出现”？</h3>
    <p>A：不是“碰到 Fibonacci 就算”。真正的信号是 3 步：</p>
    <ol>
      <li>先有一段已经确认过的 swing high / swing low；</li>
      <li>价格回到 38.2%~50% 回撤区；</li>
      <li>价格先恢复到有利方向，再回踩一次但没破位，这时才算 <code>retest_hold</code> 信号成立。</li>
    </ol>

    <h3>Q2：信号出现的时候，我应该做什么？</h3>
    <p>A：<b>下一根 K 线开盘进场</b>。如果当前结构是上升回踩，就做多；如果当前结构是下降反抽，就做空。然后按这次最佳组合，持有 <b>{best_hold} bars ≈ {best_hold_hours:.1f} 小时</b> 后退出。</p>

    <h3>Q3：具体收益是多少？</h3>
    <p>A：按这次最优组合（<b>{best_days}d / {best_hold} bars</b>）看：</p>
    <ul>
      <li>平均单笔净收益：<b>{pct(best['mean_net_return'])}</b></li>
      <li>平均总收益：<b>{pct(best['mean_total_return'])}</b></li>
      <li>总交易数：<b>{int(best['trade_count'])}</b></li>
      <li>正收益资产占比：<b>{pct(best['positive_asset_ratio'])}</b></li>
    </ul>
    <p class=\"muted\">注意：这里的“平均总收益”是把 BTC / ETH / SOL 三个资产各自跑完后再求平均，不是说每一笔都能赚这么多。</p>

    <h3>Q4：哪几个币表现最好？</h3>
    <p>A：在这次最优组合里，<b>ETH 最强</b>，BTC 一般，SOL 接近打平：</p>
    <ul>
      <li>BTC：总收益约 <b>{pct(best_btc['total_return']) if best_btc else 'nan'}</b>，交易数 {int(best_btc['trade_count']) if best_btc else 'nan'} 笔</li>
      <li>ETH：总收益约 <b>{pct(best_eth['total_return']) if best_eth else 'nan'}</b>，交易数 {int(best_eth['trade_count']) if best_eth else 'nan'} 笔</li>
      <li>SOL：总收益约 <b>{pct(best_sol['total_return']) if best_sol else 'nan'}</b>，交易数 {int(best_sol['trade_count']) if best_sol else 'nan'} 笔</li>
    </ul>

    <h3>Q5：这是不是已经可以直接实盘？</h3>
    <p>A：<b>还不建议直接当独立主策略实盘。</b> 原因很简单：它在某些样本段有效，但不是所有更长样本都稳定。更诚实的定位是：它现在更像一个 <b>confirmation / filter layer</b>，适合叠加到 breakout / pullback 主线上，而不是自己单独扛起整个策略。</p>
  </div>

  <div class=\"card\">
    <h2>为什么我又多做了一层 portfolio gate？</h2>
    <ol>
      <li>如果把所有触发都算进去，会出现大量重叠信号，次数会被夸大。</li>
      <li>真正更像实盘的做法是：同一资产已经有仓位时，不再重复开新仓。</li>
      <li>所以这页的数据，比单纯 signal-level 统计更接近“策略回测”。</li>
    </ol>
  </div>

  <div class=\"card\">
    <h2>热力图</h2>
    <div class=\"grid\">
      <div><img src=\"portfolio_heat_ret.png\" alt=\"portfolio mean net return\" /></div>
      <div><img src=\"portfolio_heat_total.png\" alt=\"portfolio mean total return\" /></div>
      <div><img src=\"portfolio_heat_trades.png\" alt=\"portfolio trade count\" /></div>
    </div>
  </div>

  <div class=\"card\">
    <h2>样本天数 × 持有期的策略汇总</h2>
    {render_table(agg)}
    <p class=\"muted\">重点看 <code>mean_total_return</code>：它比单笔均值更接近你真正关心的“整段跑下来有没有赚”。</p>
  </div>

  <div class=\"card\">
    <h2>最优格子的分资产结果</h2>
    {render_table(best_asset_df[["asset", "trade_count", "mean_net_return", "win_ratio", "total_return", "invalidation_ratio_12b", "mean_entry_lag_bars"]])}
  </div>

  <div class=\"card\">
    <h2>为什么选 retest_hold（引用上一轮 60d 变体比较）</h2>
    {old_compare_html}
  </div>

  <div class=\"card\">
    <h2>小白版讲解</h2>
    <ol>
      <li><b>retest_hold</b> 不是“摸到回撤位就冲”，而是“先确认方向回来，再等一次更像样的回踩”。</li>
      <li>这样通常能减少一部分假信号，但代价是机会更少、进场更晚。</li>
      <li>扩展回测说明：这条规则在更长样本里有一定继续研究价值，但它更像 <b>过滤层</b>，不是已经成熟的独立主策略。</li>
    </ol>
  </div>
</body>
</html>
"""
    SITE_PATH.write_text(html, encoding="utf-8")
    print(f"[ok] wrote {SITE_PATH}")
    print(json.dumps(summary_json, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
