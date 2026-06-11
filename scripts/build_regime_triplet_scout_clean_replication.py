#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.analytics.multi_tf_momentum_backtest import (  # noqa: E402
    MultiTfMomentumBacktestConfig,
    evaluate_multi_tf_momentum_reversal,
)
from momentum.signals.multi_tf_momentum import (  # noqa: E402
    MultiTfMomentumConfig,
    compute_multi_tf_momentum_signals,
)
from momentum.signals.regime_triplet import (  # noqa: E402
    RegimeTripletConfig,
    compute_regime_triplet_signals,
)

from build_volume_supportflip_higherlow_first_verdict import ASSETS, ensure_dir, num, pct, render_table  # noqa: E402

CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_regime_triplet_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_regime_triplet_15m"
REPORT_PATH = SITE_DIR / "report.html"

SUMMARY_PATH = ART_DIR / "clean_replication_summary.csv"
ASSET_SUMMARY_PATH = ART_DIR / "clean_replication_asset_summary.csv"
TRADES_PATH = ART_DIR / "clean_replication_trades.csv"
TIME_STABILITY_PATH = ART_DIR / "time_stability.csv"
PARAM_STABILITY_PATH = ART_DIR / "parameter_stability.csv"
CROSS_ASSET_PATH = ART_DIR / "cross_asset_stability.csv"
COST_STABILITY_PATH = ART_DIR / "cost_trade_stability.csv"
PAPER_CANDIDATE_PATH = ART_DIR / "paper_candidate_admission_memo.csv"
META_PATH = ART_DIR / "clean_replication_meta.csv"
SPEC_PATH = ART_DIR / "clean_room_spec_v1.csv"

PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0, 20.0]
TIME_BUCKETS = 3
BASELINE_LABEL = "baseline_mtf"
PRIMARY_LABEL = "strict_up_down"
VARIANT_LABELS = [BASELINE_LABEL, PRIMARY_LABEL, "regime_triplet_default", "up_only_no_side"]
PARAM_GRID = [
    {"label": "ma15_vol96_k08", "ma_period": 15, "vol_ma_period": 96, "vol_multiplier": 0.8},
    {"label": "ma20_vol120_k10", "ma_period": 20, "vol_ma_period": 120, "vol_multiplier": 1.0},
    {"label": "ma25_vol120_k10", "ma_period": 25, "vol_ma_period": 120, "vol_multiplier": 1.0},
    {"label": "ma20_vol96_k10", "ma_period": 20, "vol_ma_period": 96, "vol_multiplier": 1.0},
    {"label": "ma20_vol144_k12", "ma_period": 20, "vol_ma_period": 144, "vol_multiplier": 1.2},
]
DEFAULT_CFG = RegimeTripletConfig(ma_period=20, vol_ma_period=120, vol_multiplier=1.0)


def load_cached_bars(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["symbol"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def backtest_cfg(cost_bps_per_side: float) -> MultiTfMomentumBacktestConfig:
    return MultiTfMomentumBacktestConfig(
        fee_bps_per_side=float(cost_bps_per_side),
        slippage_bps_per_side=0.0,
        flip_on_reverse_signal=True,
    )


def summarize_variant(summary_df: pd.DataFrame, *, asset: str, variant: str, cost_bps: float, gate_pass_ratio: float | None) -> dict:
    if summary_df.empty:
        return {
            "asset": asset,
            "variant": variant,
            "cost_bps_per_side": float(cost_bps),
            "trades": 0,
            "win_rate": np.nan,
            "avg_ret": np.nan,
            "median_ret": np.nan,
            "total_return": 0.0,
            "max_drawdown": 0.0,
            "long_trades": 0,
            "short_trades": 0,
            "gate_pass_ratio": gate_pass_ratio,
            "no_trade_ratio": np.nan if gate_pass_ratio is None else 1.0 - float(gate_pass_ratio),
        }
    row = summary_df.iloc[0].to_dict()
    row.update(
        {
            "asset": asset,
            "variant": variant,
            "cost_bps_per_side": float(cost_bps),
            "gate_pass_ratio": gate_pass_ratio,
            "no_trade_ratio": np.nan if gate_pass_ratio is None else 1.0 - float(gate_pass_ratio),
        }
    )
    return row


def aggregate(df: pd.DataFrame, key_col: str) -> pd.DataFrame:
    rows = []
    for key, g in df.groupby(key_col, sort=False):
        rows.append(
            {
                key_col: key,
                "mean_total_return": float(g["total_return"].mean()),
                "positive_asset_ratio": float((g["total_return"] > 0).mean()),
                "mean_trades": float(g["trades"].mean()),
                "mean_max_drawdown": float(g["max_drawdown"].mean()),
                "mean_win_rate": float(g["win_rate"].mean()) if g["win_rate"].notna().any() else np.nan,
                "mean_no_trade_ratio": float(g["no_trade_ratio"].mean()) if g["no_trade_ratio"].notna().any() else np.nan,
                "mean_gate_pass_ratio": float(g["gate_pass_ratio"].mean()) if g["gate_pass_ratio"].notna().any() else np.nan,
            }
        )
    return pd.DataFrame(rows)


def build_baseline_signals(bars: pd.DataFrame) -> pd.DataFrame:
    sig = compute_multi_tf_momentum_signals(
        bars,
        config=MultiTfMomentumConfig(
            window_5m=6,
            window_15m=6,
            threshold_5m=0.003,
            threshold_15m=0.006,
            resample_rule_15m="15min",
        ),
    )
    sig["timestamp"] = pd.to_datetime(sig["timestamp"], utc=True)
    sig["symbol"] = bars["symbol"].iloc[0]
    sig["base_long_signal"] = sig["long_signal"].astype(int)
    sig["base_short_signal"] = sig["short_signal"].astype(int)
    return sig


def build_regime_signals(bars: pd.DataFrame, *, cfg: RegimeTripletConfig, variant: str) -> tuple[pd.DataFrame, float]:
    base = build_baseline_signals(bars)
    regime = compute_regime_triplet_signals(
        bars[["timestamp", "open", "close", "volume", "symbol"]].copy(),
        config=cfg,
    )
    regime["timestamp"] = pd.to_datetime(regime["timestamp"], utc=True)
    merged = base.merge(
        regime[["timestamp", "symbol", "up_regime", "side_regime", "down_regime"]],
        on=["timestamp", "symbol"],
        how="left",
    )
    merged[["up_regime", "side_regime", "down_regime"]] = merged[["up_regime", "side_regime", "down_regime"]].fillna(0).astype(int)

    if variant == PRIMARY_LABEL:
        long_gate = merged["up_regime"] == 1
        short_gate = merged["down_regime"] == 1
    elif variant == "regime_triplet_default":
        long_gate = (merged["up_regime"] == 1) | (merged["side_regime"] == 1)
        short_gate = merged["down_regime"] == 1
    elif variant == "up_only_no_side":
        long_gate = merged["up_regime"] == 1
        short_gate = pd.Series(False, index=merged.index)
    else:
        raise ValueError(f"unsupported variant: {variant}")

    merged["long_signal"] = ((merged["base_long_signal"] == 1) & long_gate).astype(int)
    merged["short_signal"] = ((merged["base_short_signal"] == 1) & short_gate).astype(int)
    gate_pass_ratio = float(((merged["long_signal"] == 1) | (merged["short_signal"] == 1)).mean())
    return merged, gate_pass_ratio


def evaluate_one(bars: pd.DataFrame, *, variant: str, cost_bps: float, cfg: RegimeTripletConfig | None = None) -> tuple[dict, pd.DataFrame]:
    if variant == BASELINE_LABEL:
        sig = build_baseline_signals(bars)
        gate_pass_ratio = None
    else:
        sig, gate_pass_ratio = build_regime_signals(bars, cfg=cfg or DEFAULT_CFG, variant=variant)
    bt = evaluate_multi_tf_momentum_reversal(sig, config=backtest_cfg(cost_bps))
    summary = summarize_variant(
        bt.summary,
        asset=str(bars.iloc[0]["symbol"]),
        variant=variant,
        cost_bps=cost_bps,
        gate_pass_ratio=gate_pass_ratio,
    )
    trades = bt.trades.copy()
    if not trades.empty:
        trades["asset"] = str(bars.iloc[0]["symbol"])
        trades["variant"] = variant
        trades["cost_bps_per_side"] = float(cost_bps)
    return summary, trades


def build_spec() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "section": "run_context",
                "item": "why_this_candidate_now",
                "value": "EMA 当前 waiting_not_due；Rank 17 / Rank 2 当前都没有新的真实 P3 append/review need，因此这轮 Scout Seat 应切 fresh intake，而不是继续给旧 P3 补近义 wiring。",
                "why_it_matters": "当前边际价值最高的动作，是用现有 repo 信号把新候选直接推进到 clean replication + Light Stability Pack verdict。",
                "operator_rule": "本轮只做 Rank 26 一条 fresh line，不并行打开第二个候选。",
            },
            {
                "section": "candidate",
                "item": "candidate_id",
                "value": "rank26_regime_triplet_state_gate_15m",
                "why_it_matters": "给 fresh intake 一个可追踪句柄。",
                "operator_rule": "若 clean replication + stability 不过门，直接 park / evidence pool。",
            },
            {
                "section": "source_anchor",
                "item": "paper_repo_mapping",
                "value": "repo `regime_triplet.py` + 既有 regime_triplet 因子页；把『4-bar price-above/below-MA + volume persistence』压成 15m crypto 的状态门，用来过滤 baseline multi-tf momentum。",
                "why_it_matters": "它不是新大框架，而是检验 local repo 里的状态门在 15m crypto 上能否留下最小 survival pocket。",
                "operator_rule": "trade on = baseline 方向同向，且 long 端满足 up_regime 或 side_regime、short 端满足 down_regime；trade off = 基线方向缺失或状态门未过。",
            },
            {
                "section": "scope",
                "item": "market_timeframe",
                "value": "BTC-USD / ETH-USD / SOL-USD | Binance 120d cache | 15m execution",
                "why_it_matters": "完全复用现有历史样本，不追新 bar，不扩币种。",
                "operator_rule": "固定三币、固定 120d cache、固定 baseline 执行口径。",
            },
            {
                "section": "light_stability_pack",
                "item": "checks",
                "value": "时间稳定性 / 参数稳定性 / 跨标的稳定性 / 成本-交易数稳定性",
                "why_it_matters": "满足当前 Scout Seat 的最小诚实门槛。",
                "operator_rule": "若改善主要来自 no_trade_ratio 过高或邻域没有正 pocket，一律不进 paper candidate。",
            },
            {
                "section": "honesty_gate",
                "item": "causality_boundary",
                "value": "状态门只使用 t-3..t 的 open/close/volume 与 rolling MA/volume MA，下一根 bar 执行；没有明显 lookahead / repaint / data leakage。",
                "why_it_matters": "先过轻量诚实守门，再看 replication 结果。",
                "operator_rule": "禁止用未来确认信息或追新 bar 补样本。",
            },
        ]
    )


def render_report(summary_df: pd.DataFrame, asset_df: pd.DataFrame, time_df: pd.DataFrame, param_df: pd.DataFrame, cost_df: pd.DataFrame, meta_df: pd.DataFrame) -> str:
    meta = meta_df.iloc[0]
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Scout Seat · regime triplet state gate · 15m crypto</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1120px; margin: 40px auto; padding: 0 18px; line-height: 1.68; color: #111827; background: #f8fafc; }}
    h1,h2,h3 {{ line-height: 1.25; }}
    .muted {{ color:#6b7280; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
  </style>
</head>
<body>
  <p><a href="../../index.html">← 返回首页</a></p>
  <h1>Scout Seat · regime triplet state gate · 15m crypto</h1>
  <p class="muted">生成时间：{escape(str(meta['generated_at_utc']))} ｜ Rank 26 clean replication + Light Stability Pack。</p>

  <div class="card">
    <h2>hard verdict</h2>
    <p><b>{escape(str(meta['hard_verdict']))}</b></p>
    <ul>
      <li>{escape(str(meta['evidence_line_1']))}</li>
      <li>{escape(str(meta['evidence_line_2']))}</li>
    </ul>
  </div>

  <div class="card">
    <h2>trade on / trade off</h2>
    <ul>
      <li><b>trade on：</b>baseline multi-tf momentum 同向，且 long 端满足 <code>up_regime 或 side_regime</code>、short 端满足 <code>down_regime</code>。</li>
      <li><b>trade off：</b>基线方向缺失，或状态门未过。</li>
      <li><b>因果边界：</b>状态门仅使用 t-3..t 的 open/close/volume 和 rolling MA/volume MA；默认下一根 bar 执行。</li>
    </ul>
  </div>

  <div class="card">
    <h2>aggregate clean replication（6bps/side）</h2>
    {render_table(summary_df, percent_cols={'mean_total_return','positive_asset_ratio','mean_max_drawdown','mean_win_rate','mean_no_trade_ratio','mean_gate_pass_ratio'}, digits_cols={'mean_trades':1})}
  </div>

  <div class="card">
    <h2>cross-asset stability（主变体）</h2>
    {render_table(asset_df, percent_cols={'total_return','win_rate','avg_ret','median_ret','max_drawdown','no_trade_ratio','gate_pass_ratio'}, digits_cols={'trades':0,'long_trades':0,'short_trades':0})}
  </div>

  <div class="card">
    <h2>time stability（主变体）</h2>
    {render_table(time_df, percent_cols={'mean_total_return','positive_asset_ratio','mean_max_drawdown','mean_win_rate','mean_no_trade_ratio','mean_gate_pass_ratio'}, digits_cols={'mean_trades':1})}
  </div>

  <div class="card">
    <h2>parameter stability</h2>
    {render_table(param_df, percent_cols={'mean_total_return','positive_asset_ratio','mean_max_drawdown','mean_win_rate','mean_no_trade_ratio','mean_gate_pass_ratio'}, digits_cols={'ma_period':0,'vol_ma_period':0,'vol_multiplier':2,'mean_trades':1})}
  </div>

  <div class="card">
    <h2>cost / trade-count stability（主变体）</h2>
    {render_table(cost_df, percent_cols={'mean_total_return','positive_asset_ratio','mean_max_drawdown','mean_win_rate','mean_no_trade_ratio','mean_gate_pass_ratio'}, digits_cols={'cost_bps_per_side':1,'mean_trades':1})}
    <p class="muted">artifact：<code>reports/artifacts/scout_regime_triplet_15m/</code></p>
  </div>
</body>
</html>
'''


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    build_spec().to_csv(SPEC_PATH, index=False)

    rows: list[dict] = []
    trades: list[pd.DataFrame] = []
    for asset, symbol in ASSETS.items():
        bars = load_cached_bars(symbol, asset)
        for variant in VARIANT_LABELS:
            summary, t = evaluate_one(bars, variant=variant, cost_bps=PRIMARY_COST)
            rows.append(summary)
            if not t.empty:
                trades.append(t)

    all_rows_df = pd.DataFrame(rows)
    summary_df = aggregate(all_rows_df, "variant").sort_values("mean_total_return", ascending=False).reset_index(drop=True)
    asset_df = all_rows_df[all_rows_df["variant"] == PRIMARY_LABEL].sort_values("asset").reset_index(drop=True)

    time_rows: list[dict] = []
    for asset, symbol in ASSETS.items():
        bars = load_cached_bars(symbol, asset)
        idx_splits = np.array_split(np.arange(len(bars)), TIME_BUCKETS)
        for i, idx in enumerate(idx_splits, start=1):
            if len(idx) < 30:
                continue
            bucket_bars = bars.iloc[idx].reset_index(drop=True)
            s, _ = evaluate_one(bucket_bars, variant=PRIMARY_LABEL, cost_bps=PRIMARY_COST)
            s["time_bucket"] = f"bucket_{i}"
            time_rows.append(s)
    time_df = aggregate(pd.DataFrame(time_rows), "time_bucket").sort_values("time_bucket").reset_index(drop=True)

    param_rows: list[dict] = []
    for grid in PARAM_GRID:
        cfg = RegimeTripletConfig(
            ma_period=int(grid["ma_period"]),
            vol_ma_period=int(grid["vol_ma_period"]),
            vol_multiplier=float(grid["vol_multiplier"]),
        )
        cfg_rows = []
        for asset, symbol in ASSETS.items():
            bars = load_cached_bars(symbol, asset)
            s, _ = evaluate_one(bars, variant=PRIMARY_LABEL, cost_bps=PRIMARY_COST, cfg=cfg)
            cfg_rows.append(s)
        agg = aggregate(pd.DataFrame(cfg_rows), "variant")
        row = agg.iloc[0].to_dict()
        row.update(grid)
        param_rows.append(row)
    param_df = pd.DataFrame(param_rows)[[
        "label", "ma_period", "vol_ma_period", "vol_multiplier", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_max_drawdown", "mean_win_rate", "mean_no_trade_ratio", "mean_gate_pass_ratio"
    ]].rename(columns={"label": "param_label"})

    cost_rows: list[dict] = []
    for cost in COSTS:
        c_rows = []
        for asset, symbol in ASSETS.items():
            bars = load_cached_bars(symbol, asset)
            s, _ = evaluate_one(bars, variant=PRIMARY_LABEL, cost_bps=cost)
            c_rows.append(s)
        agg = aggregate(pd.DataFrame(c_rows), "variant")
        row = agg.iloc[0].to_dict()
        row["cost_bps_per_side"] = float(cost)
        cost_rows.append(row)
    cost_df = pd.DataFrame(cost_rows)[[
        "cost_bps_per_side", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_max_drawdown", "mean_win_rate", "mean_no_trade_ratio", "mean_gate_pass_ratio"
    ]]

    primary = summary_df.loc[summary_df["variant"] == PRIMARY_LABEL].iloc[0]
    best_neighbor = param_df.sort_values("mean_total_return", ascending=False).iloc[0]
    positive_buckets = int((time_df["mean_total_return"] > 0).sum()) if not time_df.empty else 0
    verdict = "paper candidate"
    reasons = []
    if primary["mean_total_return"] <= 0:
        verdict = "park / evidence pool"
        reasons.append("6bps aggregate 仍为负")
    if primary["positive_asset_ratio"] < (2.0 / 3.0):
        verdict = "park / evidence pool"
        reasons.append("positive_asset_ratio < 2/3")
    if positive_buckets <= 1:
        verdict = "park / evidence pool"
        reasons.append("时间正收益 bucket 不足")
    if best_neighbor["mean_total_return"] <= 0:
        verdict = "park / evidence pool"
        reasons.append("参数邻域没有正 pocket")
    if cost_df.loc[cost_df["cost_bps_per_side"] == 10.0, "mean_total_return"].iloc[0] <= 0:
        verdict = "park / evidence pool"
        reasons.append("10bps cost survival 未过")

    evidence1 = (
        f"主变体 {PRIMARY_LABEL} 在 6bps/side 下跨资产 mean_total_return={pct(primary['mean_total_return'])}，"
        f"positive_asset_ratio={pct(primary['positive_asset_ratio'])}，mean_trades={num(primary['mean_trades'],1)}，mean_no_trade_ratio={pct(primary['mean_no_trade_ratio'])}。"
    )
    evidence2 = (
        f"time 正收益 bucket={positive_buckets}/{len(time_df)}；最佳邻域={best_neighbor['param_label']}({pct(best_neighbor['mean_total_return'])})；"
        f"10/15/20bps={pct(cost_df.iloc[1]['mean_total_return'])} / {pct(cost_df.iloc[2]['mean_total_return'])} / {pct(cost_df.iloc[3]['mean_total_return'])}。"
    )

    memo_df = pd.DataFrame([
        {
            "candidate_id": "rank26_regime_triplet_state_gate_15m",
            "hard_verdict": verdict,
            "verdict_reason": "；".join(reasons) if reasons else "通过最小门槛",
            "primary_variant": PRIMARY_LABEL,
            "cost_6_mean_total_return": primary["mean_total_return"],
            "cost_6_positive_asset_ratio": primary["positive_asset_ratio"],
            "cost_6_mean_no_trade_ratio": primary["mean_no_trade_ratio"],
            "time_positive_bucket_count": positive_buckets,
            "best_param_label": best_neighbor["param_label"],
            "best_param_mean_total_return": best_neighbor["mean_total_return"],
        }
    ])

    meta_df = pd.DataFrame([
        {
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "candidate_id": "rank26_regime_triplet_state_gate_15m",
            "source_anchor": "repo regime_triplet.py + existing regime_triplet factor",
            "hard_verdict": verdict,
            "evidence_line_1": evidence1,
            "evidence_line_2": evidence2,
        }
    ])

    summary_df.to_csv(SUMMARY_PATH, index=False)
    asset_df.to_csv(ASSET_SUMMARY_PATH, index=False)
    (pd.concat(trades, ignore_index=True) if trades else pd.DataFrame()).to_csv(TRADES_PATH, index=False)
    time_df.to_csv(TIME_STABILITY_PATH, index=False)
    param_df.to_csv(PARAM_STABILITY_PATH, index=False)
    asset_df.to_csv(CROSS_ASSET_PATH, index=False)
    cost_df.to_csv(COST_STABILITY_PATH, index=False)
    memo_df.to_csv(PAPER_CANDIDATE_PATH, index=False)
    meta_df.to_csv(META_PATH, index=False)
    REPORT_PATH.write_text(render_report(summary_df, asset_df, time_df, param_df, cost_df, meta_df), encoding="utf-8")
    print(f"Wrote scout regime triplet artifacts to {ART_DIR}")
    print(f"Hard verdict: {verdict}")


if __name__ == "__main__":
    main()
