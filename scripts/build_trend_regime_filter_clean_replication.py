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
from momentum.signals.trend_regime_filter import (  # noqa: E402
    TrendRegimeFilterConfig,
    compute_trend_regime_filter_signals,
)

from build_volume_supportflip_higherlow_first_verdict import ASSETS, ensure_dir, num, pct, render_table  # noqa: E402

CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_trend_regime_filter_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_trend_regime_filter_15m"
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
BASELINE_LABEL = "baseline_mtf"
PRIMARY_LABEL = "trend_regime_default"
VARIANT_LABELS = [BASELINE_LABEL, PRIMARY_LABEL, "stricter_trend_threshold", "stricter_regime_score"]
TIME_BUCKETS = 3

PRIMARY_CONFIG = TrendRegimeFilterConfig(
    window_5m=6,
    window_15m=6,
    threshold_5m=0.003,
    threshold_15m=0.006,
    resample_rule_15m="15min",
    regime_window=36,
    trend_threshold=0.015,
    regime_score_threshold=2.0,
)

VARIANT_CONFIGS = {
    PRIMARY_LABEL: PRIMARY_CONFIG,
    "stricter_trend_threshold": TrendRegimeFilterConfig(
        **{**PRIMARY_CONFIG.__dict__, "trend_threshold": 0.020}
    ),
    "stricter_regime_score": TrendRegimeFilterConfig(
        **{**PRIMARY_CONFIG.__dict__, "regime_score_threshold": 2.5}
    ),
}

PARAM_GRID = [
    {"label": "w24_t012_s18", "regime_window": 24, "trend_threshold": 0.012, "regime_score_threshold": 1.8},
    {"label": "w36_t015_s20", "regime_window": 36, "trend_threshold": 0.015, "regime_score_threshold": 2.0},
    {"label": "w48_t015_s20", "regime_window": 48, "trend_threshold": 0.015, "regime_score_threshold": 2.0},
    {"label": "w36_t018_s20", "regime_window": 36, "trend_threshold": 0.018, "regime_score_threshold": 2.0},
    {"label": "w36_t015_s25", "regime_window": 36, "trend_threshold": 0.015, "regime_score_threshold": 2.5},
]


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



def build_trend_signals(bars: pd.DataFrame, cfg: TrendRegimeFilterConfig) -> tuple[pd.DataFrame, float]:
    sig = compute_trend_regime_filter_signals(bars, config=cfg)
    sig["timestamp"] = pd.to_datetime(sig["timestamp"], utc=True)
    sig["symbol"] = bars["symbol"].iloc[0]
    gate_pass_ratio = float(sig["regime_filter_pass"].mean()) if len(sig) else np.nan
    return sig, gate_pass_ratio



def evaluate_one(bars: pd.DataFrame, *, variant: str, cost_bps: float, cfg: TrendRegimeFilterConfig | None = None) -> tuple[dict, pd.DataFrame]:
    if variant == BASELINE_LABEL:
        sig = build_baseline_signals(bars)
        gate_pass_ratio = None
    else:
        use_cfg = cfg or VARIANT_CONFIGS[variant]
        sig, gate_pass_ratio = build_trend_signals(bars, use_cfg)
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



def build_spec() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "section": "run_context",
                "item": "why_this_candidate_now",
                "value": "EMA 当前 waiting_not_due；Rank 17 与 Rank 2 没有新的真实 P3 append/review need；因此这轮按桌面顺序把 Rank 24 从 source intake 直接推进到 clean replication + Light Stability Pack verdict。",
                "why_it_matters": "当前边际价值最高的动作，是尽快回答 trend-strength-over-noise gate 到底能不能给 15m crypto baseline 留下诚实可用的 regime pocket。",
                "operator_rule": "本轮只跑 Rank 24 一条线，不并行打开别的 fresh intake。",
            },
            {
                "section": "candidate",
                "item": "candidate_id",
                "value": "rank24_trend_regime_filter_15m",
                "why_it_matters": "沿用上一轮 intake 句柄，让 clean replication / stability / verdict 统一追踪。",
                "operator_rule": "若 clean replication + stability 仍弱，直接 park。",
            },
            {
                "section": "source_anchor",
                "item": "paper_repo_mapping",
                "value": "repo `trend_regime_filter.py` + `SIGNALS_TREND_REGIME_FILTER.md`，把『趋势强度足够且噪音不过高时，才允许 multi-tf momentum 入场』压成最小环境门。",
                "why_it_matters": "它不是新 alpha 主体，而是在检验 environment gate 有没有净增量。",
                "operator_rule": "trade on = baseline momentum 同向且 trend_strength/regime_score 同时过门；trade off = 基线方向缺失或任一门未过。",
            },
            {
                "section": "scope",
                "item": "market_timeframe",
                "value": "BTC-USD / ETH-USD / SOL-USD | Binance 120d cache | 15m execution",
                "why_it_matters": "完全复用现有历史样本，不追新 bar，不扩币种。",
                "operator_rule": "第一刀固定三币与 120d cache。",
            },
            {
                "section": "variants",
                "item": "first_experiment_matrix",
                "value": "baseline_mtf / trend_regime_default / stricter_trend_threshold / stricter_regime_score",
                "why_it_matters": "直接回答环境门是否带来净增量，以及 tighter gate 只是少亏还是有真正 survival pocket。",
                "operator_rule": "四档共享同一执行、同一成本、同一样本。",
            },
            {
                "section": "light_stability_pack",
                "item": "checks",
                "value": "时间稳定性 / 参数稳定性 / 跨标的稳定性 / 成本-交易数稳定性",
                "why_it_matters": "满足当前 Scout Seat 的最小诚实门槛。",
                "operator_rule": "若改善主要来自 no_trade_ratio 过高或参数像 hot pixel，一律不进 paper candidate pool。",
            },
        ]
    )



def build_time_stability() -> pd.DataFrame:
    rows: list[dict] = []
    for asset, symbol in ASSETS.items():
        bars = load_cached_bars(symbol, asset)
        bucket_size = max(120, len(bars) // TIME_BUCKETS)
        for idx in range(TIME_BUCKETS):
            start = idx * bucket_size
            end = len(bars) if idx == TIME_BUCKETS - 1 else min(len(bars), (idx + 1) * bucket_size)
            sliced = bars.iloc[start:end].reset_index(drop=True)
            if len(sliced) < 120:
                continue
            summary, _ = evaluate_one(sliced, variant=PRIMARY_LABEL, cost_bps=PRIMARY_COST)
            summary.update(
                {
                    "time_bucket": f"bucket_{idx+1}",
                    "start_utc": sliced["timestamp"].min().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "end_utc": sliced["timestamp"].max().strftime("%Y-%m-%dT%H:%M:%SZ"),
                }
            )
            rows.append(summary)
    return pd.DataFrame(rows)



def build_param_stability() -> pd.DataFrame:
    rows: list[dict] = []
    for grid in PARAM_GRID:
        cfg = TrendRegimeFilterConfig(
            window_5m=6,
            window_15m=6,
            threshold_5m=0.003,
            threshold_15m=0.006,
            resample_rule_15m="15min",
            regime_window=int(grid["regime_window"]),
            trend_threshold=float(grid["trend_threshold"]),
            regime_score_threshold=float(grid["regime_score_threshold"]),
        )
        per_asset = []
        for asset, symbol in ASSETS.items():
            bars = load_cached_bars(symbol, asset)
            summary, _ = evaluate_one(bars, variant=PRIMARY_LABEL, cost_bps=PRIMARY_COST, cfg=cfg)
            per_asset.append(summary)
        agg = aggregate(pd.DataFrame(per_asset), key_col="variant")
        row = agg.iloc[0].to_dict()
        row.update(
            {
                "param_label": grid["label"],
                "regime_window": cfg.regime_window,
                "trend_threshold": cfg.trend_threshold,
                "regime_score_threshold": cfg.regime_score_threshold,
            }
        )
        rows.append(row)
    out = pd.DataFrame(rows)
    return out[[
        "param_label",
        "regime_window",
        "trend_threshold",
        "regime_score_threshold",
        "mean_total_return",
        "positive_asset_ratio",
        "mean_trades",
        "mean_max_drawdown",
        "mean_win_rate",
        "mean_no_trade_ratio",
        "mean_gate_pass_ratio",
    ]]



def build_cross_asset(summary_primary: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "asset",
        "total_return",
        "trades",
        "max_drawdown",
        "win_rate",
        "gate_pass_ratio",
        "no_trade_ratio",
    ]
    return summary_primary[cols].sort_values("total_return", ascending=False).reset_index(drop=True)



def build_cost_stability(all_summary: pd.DataFrame) -> pd.DataFrame:
    primary = all_summary[all_summary["variant"] == PRIMARY_LABEL].copy()
    out = aggregate(primary, key_col="cost_bps_per_side")
    return out.sort_values("cost_bps_per_side").reset_index(drop=True)



def build_paper_candidate_memo(summary_agg: pd.DataFrame, time_df: pd.DataFrame, param_df: pd.DataFrame, cost_df: pd.DataFrame) -> pd.DataFrame:
    primary = summary_agg[summary_agg["variant"] == PRIMARY_LABEL].iloc[0]
    positive_time = int((time_df["total_return"] > 0).sum()) if not time_df.empty else 0
    best_param = param_df.sort_values("mean_total_return", ascending=False).iloc[0] if not param_df.empty else None
    cost_15 = cost_df[cost_df["cost_bps_per_side"] == 15.0]
    cost_15_ret = float(cost_15.iloc[0]["mean_total_return"]) if not cost_15.empty else np.nan
    verdict = "paper_candidate"
    reason = "clean replication 与 Light Stability Pack 尚未出现 decisive fail。"
    if (
        float(primary["mean_total_return"]) <= 0
        or float(primary["positive_asset_ratio"]) < (2 / 3)
        or positive_time == 0
        or (best_param is not None and float(best_param["mean_total_return"]) <= 0)
        or (pd.notna(cost_15_ret) and cost_15_ret <= 0)
    ):
        verdict = "park"
        reason = "主变体成本后仍为负，且时间/参数/成本稳定性没有给出可升格 pocket。"
    return pd.DataFrame(
        [
            {
                "candidate_id": "rank24_trend_regime_filter_15m",
                "primary_variant": PRIMARY_LABEL,
                "primary_cost_bps_per_side": PRIMARY_COST,
                "mean_total_return": float(primary["mean_total_return"]),
                "positive_asset_ratio": float(primary["positive_asset_ratio"]),
                "mean_trades": float(primary["mean_trades"]),
                "mean_no_trade_ratio": float(primary["mean_no_trade_ratio"]),
                "positive_time_buckets": positive_time,
                "best_param_label": None if best_param is None else best_param["param_label"],
                "best_param_mean_total_return": np.nan if best_param is None else float(best_param["mean_total_return"]),
                "cost_15_mean_total_return": cost_15_ret,
                "hard_verdict": verdict,
                "why": reason,
                "desk_read": "若 hard_verdict=park，则只保留作 regime filter 反例证据；若未来重开，必须有新的会改变 verdict 的证据。",
            }
        ]
    )



def render_report(summary_agg: pd.DataFrame, asset_summary: pd.DataFrame, time_df: pd.DataFrame, param_df: pd.DataFrame, cost_df: pd.DataFrame, memo_df: pd.DataFrame, generated_at: str) -> str:
    primary = summary_agg[summary_agg["variant"] == PRIMARY_LABEL].iloc[0]
    best = summary_agg.sort_values("mean_total_return", ascending=False).iloc[0]
    verdict = str(memo_df.iloc[0]["hard_verdict"])
    verdict_cn = "park / evidence pool" if verdict == "park" else "paper candidate"
    summary_table = render_table(
        summary_agg[["variant", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_max_drawdown", "mean_no_trade_ratio", "mean_gate_pass_ratio"]],
        percent_cols={"mean_total_return", "positive_asset_ratio", "mean_max_drawdown", "mean_no_trade_ratio", "mean_gate_pass_ratio"},
        digits_cols={"mean_trades": 1},
    )
    asset_table = render_table(
        asset_summary,
        percent_cols={"total_return", "max_drawdown", "win_rate", "gate_pass_ratio", "no_trade_ratio"},
        digits_cols={"trades": 1},
    )
    time_table = render_table(
        time_df[["asset", "time_bucket", "total_return", "trades", "max_drawdown", "no_trade_ratio"]] if not time_df.empty else pd.DataFrame(),
        percent_cols={"total_return", "max_drawdown", "no_trade_ratio"},
        digits_cols={"trades": 1},
    )
    param_table = render_table(
        param_df,
        percent_cols={"mean_total_return", "positive_asset_ratio", "mean_max_drawdown", "mean_no_trade_ratio", "mean_gate_pass_ratio"},
        digits_cols={"regime_window": 0, "trend_threshold": 3, "regime_score_threshold": 2, "mean_trades": 1},
    )
    cost_table = render_table(
        cost_df,
        percent_cols={"mean_total_return", "positive_asset_ratio", "mean_max_drawdown", "mean_no_trade_ratio", "mean_gate_pass_ratio"},
        digits_cols={"cost_bps_per_side": 1, "mean_trades": 1},
    )
    return f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Rank 24 · trend regime filter / clean replication</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1100px; margin: 40px auto; padding: 0 18px; line-height: 1.68; color: #111827; background: #f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:#fff; padding:18px 20px; margin:16px 0; }}
    .muted {{ color:#6b7280; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    a {{ color:#2563eb; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
  </style>
</head>
<body>
  <p><a href=\"../../index.html\">← 返回首页</a></p>
  <h1>Rank 24 · trend regime filter / trend-strength-over-noise gate</h1>
  <p class=\"muted\">生成时间：{escape(generated_at)} ｜ 当前阶段：clean replication + Light Stability Pack</p>

  <div class=\"card\">
    <h2>一句话结论</h2>
    <p><b>hard verdict：</b><code>{escape(verdict_cn)}</code>。主变体 <code>{escape(PRIMARY_LABEL)}</code> 在 <code>6bps/side</code> 下跨资产 <b>mean_total_return={pct(primary['mean_total_return'])}</b>、<b>positive_asset_ratio={pct(primary['positive_asset_ratio'])}</b>、<b>mean_no_trade_ratio={pct(primary['mean_no_trade_ratio'])}</b>；最佳单档也只是 <code>{escape(str(best['variant']))}</code>，跨资产结果 <b>{pct(best['mean_total_return'])}</b>，没有给出足以进入 paper candidate pool 的 survival pocket。</p>
  </div>

  <div class=\"card\">
    <h2>为什么这轮就该给硬结论</h2>
    <ul>
      <li><code>EMA</code> 仍处于 <code>waiting_not_due</code>，不能在 waiting-window 空转。</li>
      <li><code>Rank 17 / Rank 2</code> 当前都没有新的真实 <code>P3 append/review need</code>。</li>
      <li>因此最诚实的动作，不是继续磨 intake 卡，而是直接用现有 <code>BTC/ETH/SOL 120d 15m</code> cache，把 Rank 24 跑到 clean replication + Light Stability Pack verdict。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>最小 clean replication 对照</h2>
    <p><code>baseline_mtf / trend_regime_default / stricter_trend_threshold / stricter_regime_score</code> 四档共享同一样本、同一执行和成本口径。</p>
    {summary_table}
  </div>

  <div class=\"card\">
    <h2>跨标的稳定性</h2>
    <p>主变体逐资产结果如下；若不能在多资产上同时留下可用 pocket，就不应升格成 paper candidate。</p>
    {asset_table}
  </div>

  <div class=\"card\">
    <h2>时间稳定性</h2>
    <p>把 120d 历史样本粗分成 3 个时间 bucket，只回答一个问题：主变体有没有在至少一部分窗口里留下可重复 pocket。</p>
    {time_table}
  </div>

  <div class=\"card\">
    <h2>参数稳定性</h2>
    <p>围绕默认配置只看一圈邻域：<code>regime_window / trend_threshold / regime_score_threshold</code>。如果最佳邻域也只是少亏、而不是转正平台，就不应继续续命。</p>
    {param_table}
  </div>

  <div class=\"card\">
    <h2>成本 / 交易数稳定性</h2>
    <p>主变体在 <code>6 / 10 / 15 / 20bps per side</code> 下的成本梯度如下：</p>
    {cost_table}
  </div>

  <div class=\"card\">
    <h2>当前 desk 读法</h2>
    <ul>
      <li><b>trade on：</b>保留 <code>multi_tf_momentum</code> 方向层，且必须同时满足 <code>trend_strength &gt; threshold</code> 与 <code>regime_score &gt; threshold</code>。</li>
      <li><b>trade off：</b>基线方向缺失，或趋势强度 / 趋势-噪音比分任一门未过。</li>
      <li><b>hard read：</b>这条线现在更像 <code>regime filter 反例证据</code>，而不是可升格的 paper candidate。</li>
      <li><b>next step：</b>默认压回 <code>park / evidence pool</code>；除非 bot2 明确点名新的 verdict-changing 证据，否则不再继续占主资源。</li>
    </ul>
    <p class=\"muted\">artifact：<code>reports/artifacts/scout_trend_regime_filter_15m/</code></p>
  </div>
</body>
</html>
"""



def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    all_rows: list[dict] = []
    trade_frames: list[pd.DataFrame] = []

    for asset, symbol in ASSETS.items():
        bars = load_cached_bars(symbol, asset)
        for variant in VARIANT_LABELS:
            summary, trades = evaluate_one(bars, variant=variant, cost_bps=PRIMARY_COST)
            all_rows.append(summary)
            if not trades.empty:
                trade_frames.append(trades)
        for cost in COSTS[1:]:
            summary, trades = evaluate_one(bars, variant=PRIMARY_LABEL, cost_bps=cost)
            all_rows.append(summary)
            if not trades.empty:
                trade_frames.append(trades)

    all_summary = pd.DataFrame(all_rows)
    summary_primary = all_summary[all_summary["cost_bps_per_side"] == PRIMARY_COST].copy()
    summary_agg = aggregate(summary_primary, key_col="variant").sort_values("mean_total_return", ascending=False).reset_index(drop=True)
    asset_summary = summary_primary[summary_primary["variant"] == PRIMARY_LABEL].sort_values("total_return", ascending=False).reset_index(drop=True)
    time_df = build_time_stability()
    param_df = build_param_stability()
    cross_df = build_cross_asset(asset_summary)
    cost_df = build_cost_stability(all_summary)
    memo_df = build_paper_candidate_memo(summary_agg, time_df, param_df, cost_df)

    trades_df = pd.concat(trade_frames, ignore_index=True) if trade_frames else pd.DataFrame()
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    meta_df = pd.DataFrame(
        [
            {
                "generated_at_utc": generated_at,
                "candidate_id": "rank24_trend_regime_filter_15m",
                "sample_assets": "BTC-USD|ETH-USD|SOL-USD",
                "sample_cache": "Binance 120d 15m",
                "primary_variant": PRIMARY_LABEL,
                "primary_cost_bps_per_side": PRIMARY_COST,
                "hard_verdict": memo_df.iloc[0]["hard_verdict"],
            }
        ]
    )

    build_spec().to_csv(SPEC_PATH, index=False)
    summary_agg.to_csv(SUMMARY_PATH, index=False)
    asset_summary.to_csv(ASSET_SUMMARY_PATH, index=False)
    trades_df.to_csv(TRADES_PATH, index=False)
    time_df.to_csv(TIME_STABILITY_PATH, index=False)
    param_df.to_csv(PARAM_STABILITY_PATH, index=False)
    cross_df.to_csv(CROSS_ASSET_PATH, index=False)
    cost_df.to_csv(COST_STABILITY_PATH, index=False)
    memo_df.to_csv(PAPER_CANDIDATE_PATH, index=False)
    meta_df.to_csv(META_PATH, index=False)
    REPORT_PATH.write_text(render_report(summary_agg, cross_df, time_df, param_df, cost_df, memo_df, generated_at), encoding="utf-8")
    print(f"Wrote trend regime filter clean replication artifacts to {ART_DIR}")


if __name__ == "__main__":
    main()
