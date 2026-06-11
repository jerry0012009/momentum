#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank36_tsm_drift_honesty_gate_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank36_tsm_drift_honesty_gate_15m"
REPORT_PATH = SITE_DIR / "report.html"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
VARIANTS = ["recent_sign_only", "history_drift_only", "recent_and_drift_agree"]
COSTS = [6.0, 10.0, 15.0, 20.0]
PRIMARY_COST = 6.0
PRIMARY_VARIANT = "recent_and_drift_agree"
RECENT_WINDOW = 16
DRIFT_WINDOW = 96
HOLD_BARS = 8


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


def fmt_ts(ts) -> str:
    if ts is None or pd.isna(ts):
        return "-"
    return pd.to_datetime(ts, utc=True).strftime("%Y-%m-%d %H:%M UTC")


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
    df["recent_ret"] = df["close"] / df["close"].shift(RECENT_WINDOW) - 1.0
    df["drift_ret"] = df["close"] / df["close"].shift(DRIFT_WINDOW) - 1.0
    return df


def variant_signal(df: pd.DataFrame, variant: str) -> pd.Series:
    recent_sign = np.sign(df["recent_ret"])
    drift_sign = np.sign(df["drift_ret"])
    if variant == "recent_sign_only":
        sig = recent_sign
    elif variant == "history_drift_only":
        sig = drift_sign
    elif variant == "recent_and_drift_agree":
        sig = np.where((recent_sign == drift_sign) & (recent_sign != 0), recent_sign, 0.0)
    else:
        raise ValueError(variant)
    sig = pd.Series(sig, index=df.index, dtype=float).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return sig


def build_trades(df: pd.DataFrame, variant: str, cost_bps_per_side: float) -> pd.DataFrame:
    sig = variant_signal(df, variant)
    prev_sig = sig.shift(1).fillna(0.0)
    trades: list[dict] = []
    i = max(RECENT_WINDOW, DRIFT_WINDOW)
    cost_rate = float(cost_bps_per_side) / 10000.0
    while i < len(df) - HOLD_BARS - 1:
        current_sig = float(sig.iloc[i])
        if current_sig != 0.0 and current_sig != float(prev_sig.iloc[i]):
            entry_idx = i + 1
            exit_idx = min(i + HOLD_BARS, len(df) - 1)
            entry_px = float(df["open"].iloc[entry_idx])
            exit_px = float(df["close"].iloc[exit_idx])
            gross_ret = current_sig * (exit_px / entry_px - 1.0)
            net_ret = gross_ret - 2.0 * cost_rate
            recent_ret = float(df["recent_ret"].iloc[i]) if pd.notna(df["recent_ret"].iloc[i]) else np.nan
            drift_ret = float(df["drift_ret"].iloc[i]) if pd.notna(df["drift_ret"].iloc[i]) else np.nan
            trades.append(
                {
                    "asset": df["asset"].iloc[i],
                    "variant": variant,
                    "cost_bps_per_side": float(cost_bps_per_side),
                    "signal_bar_utc": df["timestamp"].iloc[i],
                    "entry_bar_utc": df["timestamp"].iloc[entry_idx],
                    "exit_bar_utc": df["timestamp"].iloc[exit_idx],
                    "side": "long" if current_sig > 0 else "short",
                    "hold_bars": HOLD_BARS,
                    "recent_ret": recent_ret,
                    "drift_ret": drift_ret,
                    "entry_price": entry_px,
                    "exit_price": exit_px,
                    "gross_ret": gross_ret,
                    "net_ret": net_ret,
                    "win": int(net_ret > 0),
                }
            )
            i = exit_idx + 1
        else:
            i += 1
    out = pd.DataFrame(trades)
    if not out.empty:
        out["signal_bar_utc"] = pd.to_datetime(out["signal_bar_utc"], utc=True)
        out["entry_bar_utc"] = pd.to_datetime(out["entry_bar_utc"], utc=True)
        out["exit_bar_utc"] = pd.to_datetime(out["exit_bar_utc"], utc=True)
    return out


def summarize_trades(trades: pd.DataFrame, total_bars: int) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(
            [{
                "trades": 0,
                "total_return": 0.0,
                "avg_trade_ret": 0.0,
                "win_rate": np.nan,
                "avg_recent_ret": np.nan,
                "avg_drift_ret": np.nan,
                "trade_bar_share": 0.0,
                "no_trade_ratio": 1.0,
            }]
        )
    trade_bar_share = min(1.0, len(trades) * HOLD_BARS / max(total_bars, 1))
    return pd.DataFrame(
        [{
            "trades": int(len(trades)),
            "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
            "avg_trade_ret": float(trades["net_ret"].mean()),
            "win_rate": float((trades["net_ret"] > 0).mean()),
            "avg_recent_ret": float(trades["recent_ret"].mean()),
            "avg_drift_ret": float(trades["drift_ret"].mean()),
            "trade_bar_share": float(trade_bar_share),
            "no_trade_ratio": float(1.0 - trade_bar_share),
        }]
    )


def build_time_bucket_summary(primary_trades: pd.DataFrame) -> pd.DataFrame:
    if primary_trades.empty:
        return pd.DataFrame(columns=["variant", "time_bucket", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_win_rate"])
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
        return pd.DataFrame(columns=["variant", "time_bucket", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_win_rate"])
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
    return out[["variant", "time_bucket", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_win_rate"]]


def render_report(overall: pd.DataFrame, asset_summary: pd.DataFrame, time_buckets: pd.DataFrame, primary_trades: pd.DataFrame) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    primary = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    drift = overall[(overall["variant"] == "history_drift_only") & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    recent = overall[(overall["variant"] == "recent_sign_only") & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    primary_row = primary.iloc[0] if not primary.empty else None
    drift_row = drift.iloc[0] if not drift.empty else None
    recent_row = recent.iloc[0] if not recent.empty else None
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Rank 36 · TSM vs drift honesty gate</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1120px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111827; background: #f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }}
    .muted {{ color:#6b7280; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    ul {{ padding-left: 20px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    a {{ color:#2563eb; text-decoration:none; }}
  </style>
</head>
<body>
  <p><a href="../../reading/quant_digests/report.html">← 返回 Quant Digests</a></p>
  <h1>Rank 36 · recent-return sign vs history-drift honesty gate</h1>
  <p class="muted">生成时间：{generated_at} ｜ 类型：最小 clean replication ｜ 角色：Scout Seat 的 TSM honesty-gate fast verdict</p>

  <div class="card">
    <h2>这轮只回答什么</h2>
    <ul>
      <li>固定复用 <code>BTC/ETH/SOL 120d 15m</code> cache，不追新 bar。</li>
      <li>只比较 <code>recent_sign_only / history_drift_only / recent_and_drift_agree</code> 三档最小 clean-room 对照。</li>
      <li>recent sign 冻结为 <code>16</code> 根 15m bar 回报符号；history drift 冻结为 <code>96</code> 根 15m bar 回报符号。</li>
      <li>执行口径保持最小：signal 用当前已完成 bar，实际交易用 <code>next-bar open</code> 进场，固定持有 <code>8</code> 根 15m bar，且默认 <code>no-overlap</code>。</li>
    </ul>
  </div>

  <div class="card">
    <h2>clean-room 规则</h2>
    <ul>
      <li><b>recent_sign_only：</b>最近 16 根 15m bar 的累计收益为正就做多，为负就做空。</li>
      <li><b>history_drift_only：</b>更慢的 96 根 15m bar 累计收益为正就做多，为负就做空。</li>
      <li><b>recent_and_drift_agree：</b>只有当 recent sign 与 history-drift sign 同向时，才允许 recent-momentum 交易保留。</li>
      <li><b>trade off：</b>任一方向缺失，或两者冲突。</li>
    </ul>
  </div>

  <div class="card">
    <h2>hard verdict</h2>
    <p><span class="pill">park / evidence pool</span></p>
    <p><b>agree-only gate 没把这条线救回来。</b> 在 6bps/side 下，<code>recent_and_drift_agree</code> 仍只有 mean_total_return≈{pct(primary_row['mean_total_return']) if primary_row is not None else '-'}、positive_asset_ratio≈{pct(primary_row['positive_asset_ratio']) if primary_row is not None else '-'}、mean_trades≈{num(primary_row['mean_trades'], 1) if primary_row is not None else '-'}。</p>
    <p class="muted">更直白地说：这条线当前不是 “recent sign 很强，只是被 drift 污染”；而更像是 <code>recent_sign_only</code> 与 <code>recent_and_drift_agree</code> 都明显亏损，<code>history_drift_only</code> 虽然更不差，但在 6bps/side 下也仍约 {pct(drift_row['mean_total_return']) if drift_row is not None else '-'}，同样不足以进入 paper candidate pool。</p>
    <p class="muted">对比：<code>recent_sign_only</code> 在 6bps/side 下约 {pct(recent_row['mean_total_return']) if recent_row is not None else '-'}；<code>history_drift_only</code> 约 {pct(drift_row['mean_total_return']) if drift_row is not None else '-'}；<code>recent_and_drift_agree</code> 约 {pct(primary_row['mean_total_return']) if primary_row is not None else '-'}。</p>
  </div>

  <div class="card">
    <h2>跨变体总表</h2>
    {render_table(overall[["variant", "cost_bps_per_side", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_win_rate", "mean_no_trade_ratio"]], percent_cols={"mean_total_return", "positive_asset_ratio", "mean_win_rate", "mean_no_trade_ratio"}, digits_cols={"cost_bps_per_side": 0, "mean_trades": 1})}
  </div>

  <div class="card">
    <h2>主变体分资产摘要（recent_and_drift_agree）</h2>
    {render_table(asset_summary[["asset", "trades", "total_return", "avg_trade_ret", "win_rate", "avg_recent_ret", "avg_drift_ret", "no_trade_ratio"]], percent_cols={"total_return", "avg_trade_ret", "win_rate", "avg_recent_ret", "avg_drift_ret", "no_trade_ratio"}, digits_cols={"trades": 0})}
  </div>

  <div class="card">
    <h2>time-pocket honesty（主变体 6bps）</h2>
    {render_table(time_buckets, percent_cols={"mean_total_return", "positive_asset_ratio", "mean_win_rate"}, digits_cols={"mean_trades": 1})}
  </div>

  <div class="card">
    <h2>主变体样本片段（前 20 笔）</h2>
    {render_table(primary_trades.head(20)[["asset", "entry_bar_utc", "exit_bar_utc", "side", "recent_ret", "drift_ret", "gross_ret", "net_ret"]], percent_cols={"recent_ret", "drift_ret", "gross_ret", "net_ret"})}
  </div>

  <div class="card">
    <h2>artifact</h2>
    <ul>
      <li><a href="../../../artifacts/scout_rank36_tsm_drift_honesty_gate_15m/overall_summary.csv">overall_summary.csv</a></li>
      <li><a href="../../../artifacts/scout_rank36_tsm_drift_honesty_gate_15m/asset_summary.csv">asset_summary.csv</a></li>
      <li><a href="../../../artifacts/scout_rank36_tsm_drift_honesty_gate_15m/time_bucket_summary.csv">time_bucket_summary.csv</a></li>
      <li><a href="../../../artifacts/scout_rank36_tsm_drift_honesty_gate_15m/primary_trades_6bps.csv">primary_trades_6bps.csv</a></li>
      <li><a href="../../../reading/quant_digests/2026-03-17_1635_tsm-vs-drift-honesty-gate.html">source intake</a></li>
    </ul>
  </div>
</body>
</html>'''


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    overall_rows = []
    primary_asset_rows = []
    primary_trades_frames = []
    for asset, symbol in ASSETS.items():
        bars = prepare_bars(asset, symbol)
        total_bars = len(bars)
        for variant in VARIANTS:
            for cost in COSTS:
                trades = build_trades(bars, variant, cost)
                summary = summarize_trades(trades, total_bars).iloc[0].to_dict()
                overall_rows.append(
                    {
                        "variant": variant,
                        "asset": asset,
                        "cost_bps_per_side": float(cost),
                        **summary,
                    }
                )
                if variant == PRIMARY_VARIANT and cost == PRIMARY_COST:
                    primary_asset_rows.append({"asset": asset, **summary})
                    primary_trades_frames.append(trades)

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
    primary_trades = pd.concat(primary_trades_frames, ignore_index=True) if primary_trades_frames else pd.DataFrame()
    if not primary_trades.empty:
        primary_trades = primary_trades.sort_values(["asset", "entry_bar_utc"]).reset_index(drop=True)
    time_bucket_summary = build_time_bucket_summary(primary_trades)

    overall_summary.to_csv(ART_DIR / "overall_summary.csv", index=False)
    primary_asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    time_bucket_summary.to_csv(ART_DIR / "time_bucket_summary.csv", index=False)
    primary_trades.to_csv(ART_DIR / "primary_trades_6bps.csv", index=False)

    REPORT_PATH.write_text(render_report(overall_summary, primary_asset_summary, time_bucket_summary, primary_trades), encoding="utf-8")
    print(f"wrote {ART_DIR}")
    print(f"wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
