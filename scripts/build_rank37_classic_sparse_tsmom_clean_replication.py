#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank37_classic_sparse_tsmom_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank37_classic_sparse_tsmom_15m"
REPORT_PATH = SITE_DIR / "report.html"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
VARIANT_SPECS = {
    "slow_4h_sign_hold_4h": {"lookback_bars": 16, "hold_bars": 16, "agree_windows": None},
    "slow_12h_sign_hold_8h": {"lookback_bars": 48, "hold_bars": 32, "agree_windows": None},
    "slow_4h_12h_agree_hold_8h": {"lookback_bars": None, "hold_bars": 32, "agree_windows": (16, 48)},
}
COSTS = [6.0, 10.0, 15.0, 20.0]
PRIMARY_VARIANT = "slow_12h_sign_hold_8h"
PRIMARY_COST = 6.0


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def pct(value: float | int | None, digits: int = 2) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{float(value) * 100:.{digits}f}%"


def num(value: float | int | None, digits: int = 2) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{float(value):.{digits}f}"


def render_table(df: pd.DataFrame, *, percent_cols: set[str], digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    digits_cols = digits_cols or {}
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    body = []
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
        body.append(f"<tr>{''.join(cells)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def load_cached_bars(symbol: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df.sort_values("timestamp").reset_index(drop=True)


def prepare_bars(asset: str, symbol: str) -> pd.DataFrame:
    df = load_cached_bars(symbol).copy()
    df["asset"] = asset
    df["ret_16"] = df["close"] / df["close"].shift(16) - 1.0
    df["ret_48"] = df["close"] / df["close"].shift(48) - 1.0
    return df


def variant_signal(df: pd.DataFrame, variant: str) -> pd.Series:
    spec = VARIANT_SPECS[variant]
    if spec["agree_windows"] is None:
        window = int(spec["lookback_bars"])
        sig = np.sign(df[f"ret_{window}"])
    else:
        w1, w2 = spec["agree_windows"]
        sig1 = np.sign(df[f"ret_{w1}"])
        sig2 = np.sign(df[f"ret_{w2}"])
        sig = np.where((sig1 == sig2) & (sig1 != 0), sig1, 0.0)
    return pd.Series(sig, index=df.index, dtype=float).replace([np.inf, -np.inf], np.nan).fillna(0.0)


def build_trades(df: pd.DataFrame, variant: str, cost_bps_per_side: float) -> pd.DataFrame:
    spec = VARIANT_SPECS[variant]
    sig = variant_signal(df, variant)
    warmup = max([v for v in [spec.get("lookback_bars"), *(spec.get("agree_windows") or [])] if v is not None])
    hold_bars = int(spec["hold_bars"])
    cost_rate = float(cost_bps_per_side) / 10000.0
    trades: list[dict] = []

    i = warmup
    while i < len(df) - hold_bars - 1:
        current_sig = float(sig.iloc[i])
        if current_sig == 0.0:
            i += 1
            continue
        entry_idx = i + 1
        exit_idx = min(i + hold_bars, len(df) - 1)
        entry_px = float(df["open"].iloc[entry_idx])
        exit_px = float(df["close"].iloc[exit_idx])
        gross_ret = current_sig * (exit_px / entry_px - 1.0)
        net_ret = gross_ret - 2.0 * cost_rate
        ret_16 = float(df["ret_16"].iloc[i]) if pd.notna(df["ret_16"].iloc[i]) else np.nan
        ret_48 = float(df["ret_48"].iloc[i]) if pd.notna(df["ret_48"].iloc[i]) else np.nan
        trades.append(
            {
                "asset": df["asset"].iloc[i],
                "variant": variant,
                "cost_bps_per_side": float(cost_bps_per_side),
                "signal_bar_utc": df["timestamp"].iloc[i],
                "entry_bar_utc": df["timestamp"].iloc[entry_idx],
                "exit_bar_utc": df["timestamp"].iloc[exit_idx],
                "side": "long" if current_sig > 0 else "short",
                "lookback_4h_ret": ret_16,
                "lookback_12h_ret": ret_48,
                "hold_bars": hold_bars,
                "entry_price": entry_px,
                "exit_price": exit_px,
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "win": int(net_ret > 0),
            }
        )
        i = exit_idx + 1

    out = pd.DataFrame(trades)
    if not out.empty:
        for col in ["signal_bar_utc", "entry_bar_utc", "exit_bar_utc"]:
            out[col] = pd.to_datetime(out[col], utc=True)
    return out


def summarize_trades(trades: pd.DataFrame, total_bars: int) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame([
            {
                "trades": 0,
                "total_return": 0.0,
                "avg_trade_ret": np.nan,
                "median_trade_ret": np.nan,
                "win_rate": np.nan,
                "trade_bar_share": 0.0,
                "no_trade_ratio": 1.0,
            }
        ])
    trade_bar_share = min(1.0, float((trades["hold_bars"].sum()) / max(total_bars, 1)))
    return pd.DataFrame([
        {
            "trades": int(len(trades)),
            "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
            "avg_trade_ret": float(trades["net_ret"].mean()),
            "median_trade_ret": float(trades["net_ret"].median()),
            "win_rate": float((trades["net_ret"] > 0).mean()),
            "trade_bar_share": float(trade_bar_share),
            "no_trade_ratio": float(1.0 - trade_bar_share),
        }
    ])


def build_time_bucket_summary(primary_trades: pd.DataFrame) -> pd.DataFrame:
    cols = ["variant", "time_bucket", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_win_rate"]
    if primary_trades.empty:
        return pd.DataFrame(columns=cols)
    frames = []
    for asset, g in primary_trades.groupby("asset"):
        g = g.sort_values("entry_bar_utc").reset_index(drop=True)
        if len(g) < 3:
            continue
        g["time_bucket"] = pd.qcut(np.arange(len(g)), 3, labels=["bucket_1", "bucket_2", "bucket_3"])
        bucketed = (
            g.groupby("time_bucket", as_index=False, observed=False)
            .agg(
                total_return=("net_ret", lambda s: float((1.0 + s).prod() - 1.0)),
                trades=("net_ret", "size"),
                win_rate=("win", "mean"),
            )
        )
        bucketed["asset"] = asset
        frames.append(bucketed)
    if not frames:
        return pd.DataFrame(columns=cols)
    detail = pd.concat(frames, ignore_index=True)
    out = (
        detail.groupby("time_bucket", as_index=False, observed=False)
        .agg(
            mean_total_return=("total_return", "mean"),
            positive_assets=("total_return", lambda s: int((s > 0).sum())),
            assets=("asset", "nunique"),
            mean_trades=("trades", "mean"),
            mean_win_rate=("win_rate", "mean"),
        )
    )
    out["positive_asset_ratio"] = out["positive_assets"] / out["assets"].replace(0, np.nan)
    out.insert(0, "variant", PRIMARY_VARIANT)
    return out[cols]


def derive_verdict(overall_summary: pd.DataFrame) -> tuple[str, list[str], str]:
    hit = overall_summary[(overall_summary["variant"] == PRIMARY_VARIANT) & (overall_summary["cost_bps_per_side"] == PRIMARY_COST)]
    if hit.empty:
        return (
            "当前 Rank 37 没形成可读 primary variant，先压回 park / evidence pool。",
            ["缺少 primary variant 汇总，说明这条最小 clean replication 本身就没有站住脚。"],
            "park / evidence pool",
        )
    row = hit.iloc[0]
    headline = "当前 Rank 37 的最小 clean replication 没有给出足够诚实的 admission edge，应压回 park / evidence pool。"
    verdict = "park / evidence pool"
    if float(row["mean_total_return"]) > 0 and float(row["positive_asset_ratio"]) >= 2 / 3 and float(row["mean_trades"]) >= 8:
        headline = "当前 Rank 37 至少拿到了一个可继续 cheap check 的 first verdict，可暂列 P1 weak candidate。"
        verdict = "P1 weak candidate / one cheap check at most"
    bullets = [
        f"primary variant={PRIMARY_VARIANT} @ 6bps/side：mean_total_return {pct(row['mean_total_return'])}，positive_asset_ratio {pct(row['positive_asset_ratio'])}，mean_trades {num(row['mean_trades'], 1)}，mean_no_trade_ratio {pct(row['mean_no_trade_ratio'])}。",
        "trade on / trade off 仍是因果的：只用当前已完成 bar 的 slow-window sign，在 next-bar open 入场，并用 fixed-hold + no-overlap 避免偷做成高频翻单器。",
    ]
    if verdict.startswith("park"):
        bullets.append("更直白地说：把 pocket 放慢、放稀、去重叠之后，当前样本里也没有出现足够干净的 own-past persistence 存活证据，不值得继续给默认 Scout 预算。")
    else:
        bullets.append("如果下一轮继续认领，也只允许做 1 次便宜诚实检查；不要直接偷升为 paper candidate。")
    return headline, bullets, verdict


def render_report(overall_summary: pd.DataFrame, asset_summary: pd.DataFrame, time_buckets: pd.DataFrame, primary_trades: pd.DataFrame, headline: str, bullets: list[str], verdict: str) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    bullets_html = "".join(f"<li>{escape(x)}</li>" for x in bullets)
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Rank 37 · classic sparse TSMOM / own-past persistence pocket</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1120px; margin: 40px auto; padding: 0 18px; line-height: 1.68; color: #111827; background: #f8fafc; }}
    h1,h2 {{ line-height: 1.25; }}
    .muted {{ color:#6b7280; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    ul {{ padding-left:20px; }}
    a {{ color:#2563eb; text-decoration:none; }}
  </style>
</head>
<body>
  <p><a href="../../index.html">← 返回首页</a></p>
  <h1>Rank 37 · classic sparse TSMOM / own-past persistence pocket</h1>
  <p class="muted">生成时间：{generated_at} ｜ 当前只做 1 个最小 clean replication：固定复用 BTC/ETH/SOL 120d 15m cache，对比 slow 4h / slow 12h / agree-only 三档稀疏 own-past persistence pocket。</p>

  <div class="card">
    <h2>hard verdict</h2>
    <p><span class="pill">{escape(verdict)}</span></p>
    <p><b>{escape(headline)}</b></p>
    <ul>{bullets_html}</ul>
  </div>

  <div class="card">
    <h2>clean-room 口径</h2>
    <ul>
      <li>样本：<code>BTC / ETH / SOL | Binance 120d | 15m</code></li>
      <li>执行：<code>signal bar close -> next-bar open</code> 入场，固定持有，且默认 <code>no-overlap</code></li>
      <li><code>slow_4h_sign_hold_4h</code>：过去 <code>16</code> 根 15m bar 的累计收益方向，持有 <code>16</code> 根</li>
      <li><code>slow_12h_sign_hold_8h</code>：过去 <code>48</code> 根 15m bar 的累计收益方向，持有 <code>32</code> 根</li>
      <li><code>slow_4h_12h_agree_hold_8h</code>：只有 <code>4h</code> 与 <code>12h</code> 两档 slow sign 同向时才交易，持有 <code>32</code> 根</li>
      <li>trade off：slow-window sign 缺失、方向冲突（agree 变体）、或固定持有结束</li>
    </ul>
  </div>

  <div class="card">
    <h2>跨变体总表</h2>
    {render_table(overall_summary[["variant", "cost_bps_per_side", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_win_rate", "mean_no_trade_ratio"]], percent_cols={"mean_total_return", "positive_asset_ratio", "mean_win_rate", "mean_no_trade_ratio"}, digits_cols={"cost_bps_per_side": 0, "mean_trades": 1})}
  </div>

  <div class="card">
    <h2>主变体分资产摘要（{escape(PRIMARY_VARIANT)}）</h2>
    {render_table(asset_summary[["asset", "trades", "total_return", "avg_trade_ret", "median_trade_ret", "win_rate", "no_trade_ratio"]], percent_cols={"total_return", "avg_trade_ret", "median_trade_ret", "win_rate", "no_trade_ratio"}, digits_cols={"trades": 0})}
  </div>

  <div class="card">
    <h2>time-pocket honesty（主变体 6bps）</h2>
    {render_table(time_buckets, percent_cols={"mean_total_return", "positive_asset_ratio", "mean_win_rate"}, digits_cols={"mean_trades": 1})}
  </div>

  <div class="card">
    <h2>主变体样本片段（前 20 笔）</h2>
    {render_table(primary_trades.head(20)[["asset", "entry_bar_utc", "exit_bar_utc", "side", "lookback_4h_ret", "lookback_12h_ret", "gross_ret", "net_ret"]], percent_cols={"lookback_4h_ret", "lookback_12h_ret", "gross_ret", "net_ret"})}
  </div>

  <div class="card">
    <h2>artifact</h2>
    <ul>
      <li><a href="../../../artifacts/scout_rank37_classic_sparse_tsmom_15m/overall_summary.csv">overall_summary.csv</a></li>
      <li><a href="../../../artifacts/scout_rank37_classic_sparse_tsmom_15m/asset_summary.csv">asset_summary.csv</a></li>
      <li><a href="../../../artifacts/scout_rank37_classic_sparse_tsmom_15m/time_bucket_summary.csv">time_bucket_summary.csv</a></li>
      <li><a href="../../../artifacts/scout_rank37_classic_sparse_tsmom_15m/primary_trades_6bps.csv">primary_trades_6bps.csv</a></li>
      <li><a href="../../reading/quant_digests/2026-03-17_1705_classic-tsmom-sparse-pocket.html">source intake</a></li>
    </ul>
  </div>
</body>
</html>'''


def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    overall_rows = []
    primary_asset_rows = []
    primary_trade_frames = []
    for asset, symbol in ASSETS.items():
        bars = prepare_bars(asset, symbol)
        total_bars = len(bars)
        for variant in VARIANT_SPECS:
            for cost in COSTS:
                trades = build_trades(bars, variant, cost)
                summary = summarize_trades(trades, total_bars).iloc[0].to_dict()
                overall_rows.append({
                    "variant": variant,
                    "asset": asset,
                    "cost_bps_per_side": float(cost),
                    **summary,
                })
                if variant == PRIMARY_VARIANT and cost == PRIMARY_COST:
                    primary_asset_rows.append({"asset": asset, **summary})
                    primary_trade_frames.append(trades)

    overall_detail = pd.DataFrame(overall_rows)
    overall_summary = (
        overall_detail.groupby(["variant", "cost_bps_per_side"], as_index=False)
        .agg(
            assets_tested=("asset", "nunique"),
            positive_assets=("total_return", lambda s: int((s > 0).sum())),
            mean_total_return=("total_return", "mean"),
            mean_trades=("trades", "mean"),
            mean_win_rate=("win_rate", "mean"),
            mean_no_trade_ratio=("no_trade_ratio", "mean"),
        )
        .sort_values(["cost_bps_per_side", "mean_total_return"], ascending=[True, False])
        .reset_index(drop=True)
    )
    overall_summary["positive_asset_ratio"] = overall_summary["positive_assets"] / overall_summary["assets_tested"].replace(0, np.nan)
    overall_summary = overall_summary[["variant", "cost_bps_per_side", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_win_rate", "mean_no_trade_ratio"]]

    primary_asset_summary = pd.DataFrame(primary_asset_rows).sort_values("asset").reset_index(drop=True)
    primary_trades = pd.concat(primary_trade_frames, ignore_index=True) if primary_trade_frames else pd.DataFrame()
    if not primary_trades.empty:
        primary_trades = primary_trades.sort_values(["asset", "entry_bar_utc"]).reset_index(drop=True)
    time_buckets = build_time_bucket_summary(primary_trades)
    headline, bullets, verdict = derive_verdict(overall_summary)

    overall_summary.to_csv(ART_DIR / "overall_summary.csv", index=False)
    primary_asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    time_buckets.to_csv(ART_DIR / "time_bucket_summary.csv", index=False)
    primary_trades.to_csv(ART_DIR / "primary_trades_6bps.csv", index=False)
    pd.DataFrame([
        {
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "candidate_id": "rank37_classic_sparse_tsmom",
            "sample_window": "BTC/ETH/SOL Binance 120d 15m cache",
            "primary_variant": PRIMARY_VARIANT,
            "primary_cost_bps_per_side": PRIMARY_COST,
            "hard_verdict": verdict,
            "headline": headline,
            "evidence_1": bullets[0] if bullets else "",
            "evidence_2": bullets[1] if len(bullets) > 1 else "",
        }
    ]).to_csv(ART_DIR / "trial_meta.csv", index=False)

    REPORT_PATH.write_text(render_report(overall_summary, primary_asset_summary, time_buckets, primary_trades, headline, bullets, verdict), encoding="utf-8")
    print("[ok] rank37 clean replication generated")
    print("[artifact]", ART_DIR / "overall_summary.csv")
    print("[site]", REPORT_PATH)
    print("[verdict]", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
