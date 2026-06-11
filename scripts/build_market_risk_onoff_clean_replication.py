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
from momentum.signals.market_risk_on_off_filter import (  # noqa: E402
    MarketRiskOnOffFilterConfig,
    compute_market_risk_on_off_filter_signals,
)
from momentum.signals.multi_tf_momentum import (  # noqa: E402
    MultiTfMomentumConfig,
    compute_multi_tf_momentum_signals,
)

from build_volume_supportflip_higherlow_first_verdict import ASSETS, ensure_dir, num, pct, render_table  # noqa: E402

CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_market_risk_onoff_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_market_risk_onoff_15m"
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
PRIMARY_LABEL = "market_risk_2of3"
VARIANT_LABELS = [BASELINE_LABEL, "trend_only_gate", PRIMARY_LABEL, "market_risk_3of3"]
PARAM_GRID = [
    {"label": "trend0.3_ema24_q80_2of3", "trend_threshold_1h": 0.003, "ema_window_1h": 24, "vol_quantile_max": 0.8, "min_pass_count": 2},
    {"label": "trend0.5_ema24_q80_2of3", "trend_threshold_1h": 0.005, "ema_window_1h": 24, "vol_quantile_max": 0.8, "min_pass_count": 2},
    {"label": "trend0.8_ema24_q80_2of3", "trend_threshold_1h": 0.008, "ema_window_1h": 24, "vol_quantile_max": 0.8, "min_pass_count": 2},
    {"label": "trend0.5_ema18_q80_2of3", "trend_threshold_1h": 0.005, "ema_window_1h": 18, "vol_quantile_max": 0.8, "min_pass_count": 2},
    {"label": "trend0.5_ema30_q80_2of3", "trend_threshold_1h": 0.005, "ema_window_1h": 30, "vol_quantile_max": 0.8, "min_pass_count": 2},
    {"label": "trend0.5_ema24_q70_2of3", "trend_threshold_1h": 0.005, "ema_window_1h": 24, "vol_quantile_max": 0.7, "min_pass_count": 2},
    {"label": "trend0.5_ema24_q90_2of3", "trend_threshold_1h": 0.005, "ema_window_1h": 24, "vol_quantile_max": 0.9, "min_pass_count": 2},
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



def summarize_variant(summary_df: pd.DataFrame, *, asset: str, variant: str, cost_bps: float, gate_pass_ratio: float | None = None) -> dict:
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
            "no_trade_ratio": 1.0 if gate_pass_ratio is None else 1.0 - gate_pass_ratio,
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
    return sig



def build_risk_base_signals(bars: pd.DataFrame, *, trend_threshold_1h: float, ema_window_1h: int, vol_quantile_max: float) -> pd.DataFrame:
    sig = compute_market_risk_on_off_filter_signals(
        bars,
        config=MarketRiskOnOffFilterConfig(
            window_5m=6,
            window_15m=6,
            threshold_5m=0.003,
            threshold_15m=0.006,
            resample_rule_15m="15min",
            market_resample_rule="1h",
            trend_window_1h=12,
            trend_threshold_1h=float(trend_threshold_1h),
            ema_window_1h=int(ema_window_1h),
            vol_window_1h=12,
            vol_quantile_window_1h=72,
            vol_quantile_max=float(vol_quantile_max),
            min_pass_count=2,
        ),
    )
    sig["timestamp"] = pd.to_datetime(sig["timestamp"], utc=True)
    sig["symbol"] = bars["symbol"].iloc[0]
    return sig



def variant_from_risk_base(risk_sig: pd.DataFrame, variant: str) -> tuple[pd.DataFrame, float]:
    sig = risk_sig.copy()
    if variant == "trend_only_gate":
        gate = (sig["trend_ok_1h"] == 1)
    elif variant == "market_risk_2of3":
        gate = (sig["risk_on_score"] >= 2)
    elif variant == "market_risk_3of3":
        gate = (sig["risk_on_score"] >= 3)
    else:
        raise ValueError(f"unsupported variant: {variant}")
    sig["long_signal"] = ((sig["base_long_signal"] == 1) & gate).astype(int)
    sig["short_signal"] = ((sig["base_short_signal"] == 1) & gate).astype(int)
    sig["long_filtered_out"] = ((sig["base_long_signal"] == 1) & (sig["long_signal"] == 0)).astype(int)
    sig["short_filtered_out"] = ((sig["base_short_signal"] == 1) & (sig["short_signal"] == 0)).astype(int)
    gate_pass_ratio = float(gate.mean()) if len(gate) else np.nan
    return sig, gate_pass_ratio



def evaluate_one(bars: pd.DataFrame, *, variant: str, cost_bps: float, risk_params: dict | None = None) -> tuple[dict, pd.DataFrame]:
    if variant == BASELINE_LABEL:
        sig = build_baseline_signals(bars)
        gate_pass_ratio = None
    else:
        risk_params = risk_params or {"trend_threshold_1h": 0.005, "ema_window_1h": 24, "vol_quantile_max": 0.8}
        risk_sig = build_risk_base_signals(bars, **risk_params)
        sig, gate_pass_ratio = variant_from_risk_base(risk_sig, variant)
    bt = evaluate_multi_tf_momentum_reversal(sig, config=backtest_cfg(cost_bps))
    summary = summarize_variant(bt.summary, asset=str(bars.iloc[0]["symbol"]), variant=variant, cost_bps=cost_bps, gate_pass_ratio=gate_pass_ratio)
    trades = bt.trades.copy()
    if not trades.empty:
        trades["asset"] = str(bars.iloc[0]["symbol"])
        trades["variant"] = variant
        trades["cost_bps_per_side"] = float(cost_bps)
    return summary, trades



def aggregate(df: pd.DataFrame, key_col: str) -> pd.DataFrame:
    out = []
    for key, g in df.groupby(key_col, sort=False):
        out.append(
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
    return pd.DataFrame(out)



def build_spec() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "section": "run_context",
                "item": "why_this_candidate_now",
                "value": "EMA 当前 waiting_not_due；Rank 2 与 Rank 17 均已是 narrow paper pilot 且当前没有真实 append/review need，因此 Scout Seat 应优先把最新 Rank 21 intake 直接推进到 clean replication + Light Stability Pack verdict。",
                "why_it_matters": "当前边际价值最高的动作，是尽快回答 regime gate 到底能不能改善 15m crypto cost survival，而不是继续磨旧 P3 wiring。",
                "operator_rule": "本轮只做 Rank 21 一条线，不并行打开其他 fresh intake。",
            },
            {
                "section": "candidate",
                "item": "candidate_id",
                "value": "scout_market_risk_onoff_15m_v1",
                "why_it_matters": "延续上一轮 source intake 句柄，让 clean replication / stability / verdict 统一追踪。",
                "operator_rule": "若 clean replication + stability 仍弱，直接 park。",
            },
            {
                "section": "source_anchor",
                "item": "paper_repo_mapping",
                "value": "Svogun & Bazán-Palomino (2022) + repo `market_risk_on_off_filter.py`，把『技术规则能否活过成本取决于 market regime』压成 1h 背景 gate。",
                "why_it_matters": "它不是新 alpha 主体，而是检验环境门控有没有净增量。",
                "operator_rule": "trade on = baseline multi-tf momentum 通过且 gate 放行；trade off = gate 阻断或 baseline 消失。",
            },
            {
                "section": "scope",
                "item": "market_timeframe",
                "value": "BTC-USD / ETH-USD / SOL-USD | Binance 120d cache | 15m execution + 1h gate",
                "why_it_matters": "完全复用现有历史样本，不追新 bar，不扩币种。",
                "operator_rule": "第一刀固定三币与 120d cache。",
            },
            {
                "section": "variants",
                "item": "first_experiment_matrix",
                "value": "baseline_mtf / trend_only_gate / market_risk_2of3 / market_risk_3of3",
                "why_it_matters": "直接对应上一轮 spec，先判断 gate 的净增量与 no-trade 代价。",
                "operator_rule": "四档共享同一执行、同一成本、同一样本。",
            },
            {
                "section": "light_stability_pack",
                "item": "checks",
                "value": "时间稳定性 / 参数稳定性 / 跨标的稳定性 / 成本-交易数稳定性",
                "why_it_matters": "满足当前 Scout Seat 的最小诚实门槛。",
                "operator_rule": "若改善主要来自 no-trade_ratio 过高或参数像 hot pixel，一律不进 paper candidate pool。",
            },
        ]
    )



def write_report(summary_df: pd.DataFrame, asset_df: pd.DataFrame, time_df: pd.DataFrame, param_df: pd.DataFrame, cost_df: pd.DataFrame, meta_df: pd.DataFrame) -> None:
    ensure_dir(SITE_DIR)
    meta = meta_df.iloc[0]
    html = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Scout Seat · market risk-on/off regime gate · 15m crypto</title>
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
  <h1>Scout Seat · market risk-on/off regime gate · 15m crypto</h1>
  <p class="muted">生成时间：{escape(str(meta['generated_at_utc']))} ｜ Rank 21 clean replication + Light Stability Pack。</p>

  <div class="card">
    <h2>hard verdict</h2>
    <p><b>{escape(str(meta['hard_verdict']))}</b></p>
    <ul>
      <li>{escape(str(meta['evidence_line_1']))}</li>
      <li>{escape(str(meta['evidence_line_2']))}</li>
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
    <h2>parameter stability（主变体邻域）</h2>
    {render_table(param_df, percent_cols={'mean_total_return','positive_asset_ratio','mean_max_drawdown','mean_win_rate','mean_no_trade_ratio','mean_gate_pass_ratio'}, digits_cols={'mean_trades':1})}
  </div>

  <div class="card">
    <h2>cost / trade-count stability（主变体）</h2>
    {render_table(cost_df, percent_cols={'mean_total_return','positive_asset_ratio','mean_max_drawdown','mean_win_rate','mean_no_trade_ratio','mean_gate_pass_ratio'}, digits_cols={'mean_trades':1})}
    <p class="muted">artifact：<code>reports/artifacts/scout_market_risk_onoff_15m/</code></p>
  </div>
</body>
</html>
'''
    REPORT_PATH.write_text(html, encoding="utf-8")



def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    spec_df = build_spec()
    spec_df.to_csv(SPEC_PATH, index=False)

    rows = []
    trades = []
    for asset, symbol in ASSETS.items():
        bars = load_cached_bars(symbol, asset)
        for variant in VARIANT_LABELS:
            summary, t = evaluate_one(bars, variant=variant, cost_bps=PRIMARY_COST)
            rows.append(summary)
            if not t.empty:
                trades.append(t)

    all_rows_df = pd.DataFrame(rows)
    summary_df = aggregate(all_rows_df, "variant").sort_values("variant").reset_index(drop=True)
    asset_df = all_rows_df[all_rows_df["variant"] == PRIMARY_LABEL].sort_values("asset").reset_index(drop=True)

    time_rows = []
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

    param_rows = []
    for cfg in PARAM_GRID:
        cfg_rows = []
        risk_params = {
            "trend_threshold_1h": cfg["trend_threshold_1h"],
            "ema_window_1h": cfg["ema_window_1h"],
            "vol_quantile_max": cfg["vol_quantile_max"],
        }
        for asset, symbol in ASSETS.items():
            bars = load_cached_bars(symbol, asset)
            s, _ = evaluate_one(bars, variant=PRIMARY_LABEL, cost_bps=PRIMARY_COST, risk_params=risk_params)
            cfg_rows.append(s)
        agg = aggregate(pd.DataFrame(cfg_rows), "variant")
        row = agg.iloc[0].to_dict()
        row["param_label"] = cfg["label"]
        param_rows.append(row)
    param_df = pd.DataFrame(param_rows)[["param_label", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_max_drawdown", "mean_win_rate", "mean_no_trade_ratio", "mean_gate_pass_ratio"]]

    cost_rows = []
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
    cost_df = pd.DataFrame(cost_rows)[["cost_bps_per_side", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_max_drawdown", "mean_win_rate", "mean_no_trade_ratio", "mean_gate_pass_ratio"]]

    p6 = summary_df.loc[summary_df["variant"] == PRIMARY_LABEL].iloc[0]
    baseline6 = summary_df.loc[summary_df["variant"] == BASELINE_LABEL].iloc[0]
    p10 = cost_df.loc[cost_df["cost_bps_per_side"] == 10.0].iloc[0]
    p15 = cost_df.loc[cost_df["cost_bps_per_side"] == 15.0].iloc[0]
    positive_buckets = int((time_df["mean_total_return"] > 0).sum()) if not time_df.empty else 0
    best_param = param_df.sort_values("mean_total_return", ascending=False).iloc[0]

    verdict = "paper candidate"
    verdict_reason = []
    if p6["mean_total_return"] <= 0:
        verdict = "park / evidence pool"
        verdict_reason.append("6bps aggregate 仍为负")
    if p6["positive_asset_ratio"] < (2.0 / 3.0):
        verdict = "park / evidence pool"
        verdict_reason.append("跨标的 positive_asset_ratio < 2/3")
    if p10["mean_total_return"] <= 0:
        verdict = "park / evidence pool"
        verdict_reason.append("10bps cost survival 未过")
    if p6["mean_no_trade_ratio"] > 0.80:
        verdict = "park / evidence pool"
        verdict_reason.append("no_trade_ratio 过高")
    if best_param["mean_total_return"] <= 0:
        verdict = "park / evidence pool"
        verdict_reason.append("参数邻域没有正 pocket")

    evidence1 = (
        f"主变体 {PRIMARY_LABEL} 在 6bps/side 下跨资产 mean_total_return={pct(p6['mean_total_return'])}，"
        f"positive_asset_ratio={pct(p6['positive_asset_ratio'])}，mean_trades={num(p6['mean_trades'],1)}，mean_no_trade_ratio={pct(p6['mean_no_trade_ratio'])}。"
    )
    evidence2 = (
        f"baseline_mtf 6bps={pct(baseline6['mean_total_return'])}；10bps={pct(p10['mean_total_return'])}，15bps={pct(p15['mean_total_return'])}；"
        f"time 正收益 bucket={positive_buckets}/{len(time_df)}；最佳邻域={best_param['param_label']}({pct(best_param['mean_total_return'])})。"
    )
    verdict_text = (
        "当前 Rank 21 market risk-on/off regime gate 的更诚实读法仍是 park / evidence pool，不进入 paper candidate pool。"
        if verdict != "paper candidate"
        else "当前 Rank 21 market risk-on/off regime gate 已满足最小 paper candidate 条件，可进入 paper candidate pool。"
    )

    memo_df = pd.DataFrame(
        [
            {
                "candidate_id": "scout_market_risk_onoff_15m_v1",
                "hard_verdict": verdict,
                "verdict_reason": "；".join(verdict_reason) if verdict_reason else "通过最小门槛",
                "primary_variant": PRIMARY_LABEL,
                "baseline_6bps_mean_total_return": baseline6["mean_total_return"],
                "cost_6_mean_total_return": p6["mean_total_return"],
                "cost_10_mean_total_return": p10["mean_total_return"],
                "cost_15_mean_total_return": p15["mean_total_return"],
                "cost_6_positive_asset_ratio": p6["positive_asset_ratio"],
                "cost_6_mean_no_trade_ratio": p6["mean_no_trade_ratio"],
                "time_positive_bucket_count": positive_buckets,
                "best_param_label": best_param["param_label"],
                "best_param_mean_total_return": best_param["mean_total_return"],
            }
        ]
    )

    meta_df = pd.DataFrame(
        [
            {
                "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                "candidate_id": "scout_market_risk_onoff_15m_v1",
                "source_anchor": "Svogun & Bazán-Palomino (2022) + repo market_risk_on_off_filter.py",
                "hard_verdict": verdict_text,
                "evidence_line_1": evidence1,
                "evidence_line_2": evidence2,
            }
        ]
    )

    summary_df.to_csv(SUMMARY_PATH, index=False)
    asset_df.to_csv(ASSET_SUMMARY_PATH, index=False)
    (pd.concat(trades, ignore_index=True) if trades else pd.DataFrame()).to_csv(TRADES_PATH, index=False)
    time_df.to_csv(TIME_STABILITY_PATH, index=False)
    param_df.to_csv(PARAM_STABILITY_PATH, index=False)
    asset_df.to_csv(CROSS_ASSET_PATH, index=False)
    cost_df.to_csv(COST_STABILITY_PATH, index=False)
    memo_df.to_csv(PAPER_CANDIDATE_PATH, index=False)
    meta_df.to_csv(META_PATH, index=False)

    write_report(summary_df, asset_df, time_df, param_df, cost_df, meta_df)
    print(f"Wrote scout market risk-on/off artifacts to {ART_DIR}")
    print(f"Hard verdict: {verdict_text}")


if __name__ == "__main__":
    main()
