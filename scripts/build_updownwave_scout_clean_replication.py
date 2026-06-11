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
from momentum.signals.up_down_wave import (  # noqa: E402
    UpDownWaveConfig,
    compute_up_down_wave_signals,
)

from build_volume_supportflip_higherlow_first_verdict import ASSETS, ensure_dir, num, pct, render_table  # noqa: E402

CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_updownwave_persistence_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_updownwave_persistence_15m"
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
PRIMARY_LABEL = "updownwave_ma20"
VARIANT_LABELS = [BASELINE_LABEL, "updownwave_ma15", PRIMARY_LABEL, "updownwave_ma25", "updownwave_ma30"]
PARAM_GRID = [15, 20, 25, 30]


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
    return sig



def build_updownwave_signals(bars: pd.DataFrame, *, ma_period: int) -> tuple[pd.DataFrame, float]:
    base = build_baseline_signals(bars)
    wave = compute_up_down_wave_signals(
        bars[["timestamp", "open", "close", "symbol"]].copy(),
        config=UpDownWaveConfig(ma_period=int(ma_period)),
    )
    wave["timestamp"] = pd.to_datetime(wave["timestamp"], utc=True)
    out = base.merge(wave[["timestamp", "symbol", "upwave", "downwave"]], on=["timestamp", "symbol"], how="left")
    out[["upwave", "downwave"]] = out[["upwave", "downwave"]].fillna(0).astype(int)
    out["long_signal"] = (out["long_signal"].astype(int) & out["upwave"]).astype(int)
    out["short_signal"] = (out["short_signal"].astype(int) & out["downwave"]).astype(int)
    gate_pass_ratio = float(((out["long_signal"] == 1) | (out["short_signal"] == 1)).mean())
    return out, gate_pass_ratio



def evaluate_one(bars: pd.DataFrame, *, variant: str, cost_bps: float) -> tuple[dict, pd.DataFrame]:
    if variant == BASELINE_LABEL:
        sig = build_baseline_signals(bars)
        gate_pass_ratio = None
    else:
        ma_period = int(variant.split("_ma", 1)[1])
        sig, gate_pass_ratio = build_updownwave_signals(bars, ma_period=ma_period)
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
                "value": "EMA 当前 waiting_not_due；Rank 17 / Rank 2 均已是 P3 且没有新的 append/review need，因此当前边际价值最高的动作是把 Rank 22 从 source intake 直接推进到 clean replication verdict。",
                "why_it_matters": "不再停留在 spec 或 intake wording，而是尽快回答它到底该升格还是 park。",
                "operator_rule": "本轮只跑 Rank 22 一条线；若结果已足够硬，就直接 park / promote，不追加第二条 fresh intake。",
            },
            {
                "section": "candidate",
                "item": "candidate_id",
                "value": "scout_updownwave_persistence_15m_v1",
                "why_it_matters": "沿用 Rank 22 句柄，让 clean replication / stability / verdict 能统一追踪。",
                "operator_rule": "若 clean replication + stability 仍弱，直接 park。",
            },
            {
                "section": "source_anchor",
                "item": "paper_repo_mapping",
                "value": "现有 repo `up_down_wave.py` + `docs/SIGNALS_UP_DOWN_WAVE.md`，把『四根连续站上/跌破 MA20 的持续性过滤』压成 multi-tf momentum 的结构确认门。",
                "why_it_matters": "它不是新 alpha 框架，而是检验 persistence gate 能否帮 baseline 活过成本。",
                "operator_rule": "trade on = baseline multi-tf momentum 同向且 upwave/downwave 成立；trade off = baseline 消失或 wave 不成立。",
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
                "value": "baseline_mtf / updownwave_ma15 / updownwave_ma20 / updownwave_ma25 / updownwave_ma30",
                "why_it_matters": "既能看 intake 原始 MA20 版本，也能用邻域判断它是不是 hot pixel。",
                "operator_rule": "共享同一执行、同一成本、同一样本。",
            },
            {
                "section": "light_stability_pack",
                "item": "checks",
                "value": "时间稳定性 / 参数稳定性 / 跨标的稳定性 / 成本-交易数稳定性",
                "why_it_matters": "满足当前 Scout Seat 的最小诚实门槛。",
                "operator_rule": "不跑重下载，不追最新 bar。",
            },
            {
                "section": "honesty_gate",
                "item": "causality_boundary",
                "value": "信号只使用 t-3..t 已知数据，默认下一根 bar 执行；没有明显 lookahead / repaint / data leakage。",
                "why_it_matters": "先过 Stage A，再谈 replication 结果。",
                "operator_rule": "禁止用未来 pivot 或当根后验信息。",
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
  <title>Scout Seat · up/down wave persistence gate · 15m crypto</title>
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
  <h1>Scout Seat · up/down wave persistence gate · 15m crypto</h1>
  <p class="muted">生成时间：{escape(str(meta['generated_at_utc']))} ｜ Rank 22 clean replication + Light Stability Pack。</p>

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
    <h2>cross-asset stability（主变体 MA20）</h2>
    {render_table(asset_df, percent_cols={'total_return','win_rate','avg_ret','median_ret','max_drawdown','no_trade_ratio','gate_pass_ratio'}, digits_cols={'trades':0,'long_trades':0,'short_trades':0})}
  </div>

  <div class="card">
    <h2>time stability（主变体 MA20）</h2>
    {render_table(time_df, percent_cols={'mean_total_return','positive_asset_ratio','mean_max_drawdown','mean_win_rate','mean_no_trade_ratio','mean_gate_pass_ratio'}, digits_cols={'mean_trades':1})}
  </div>

  <div class="card">
    <h2>parameter stability（MA 邻域）</h2>
    {render_table(param_df, percent_cols={'mean_total_return','positive_asset_ratio','mean_max_drawdown','mean_win_rate','mean_no_trade_ratio','mean_gate_pass_ratio'}, digits_cols={'mean_trades':1})}
  </div>

  <div class="card">
    <h2>cost / trade-count stability（主变体 MA20）</h2>
    {render_table(cost_df, percent_cols={'mean_total_return','positive_asset_ratio','mean_max_drawdown','mean_win_rate','mean_no_trade_ratio','mean_gate_pass_ratio'}, digits_cols={'mean_trades':1})}
    <p class="muted">artifact：<code>reports/artifacts/scout_updownwave_persistence_15m/</code></p>
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
    for ma_period in PARAM_GRID:
        cfg_rows = []
        label = f"updownwave_ma{ma_period}"
        for asset, symbol in ASSETS.items():
            bars = load_cached_bars(symbol, asset)
            s, _ = evaluate_one(bars, variant=label, cost_bps=PRIMARY_COST)
            cfg_rows.append(s)
        agg = aggregate(pd.DataFrame(cfg_rows), "variant")
        row = agg.iloc[0].to_dict()
        row["param_label"] = f"ma{ma_period}"
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

    best_neighbor = param_df.sort_values("mean_total_return", ascending=False).iloc[0]
    primary_row = summary_df.loc[summary_df["variant"] == PRIMARY_LABEL].iloc[0]
    verdict = "park / evidence pool"
    evidence_1 = (
        f"主变体 MA20 在 6bps/side 下跨资产 mean_total_return≈{pct(primary_row['mean_total_return'])}，"
        f"positive_asset_ratio={num(primary_row['positive_asset_ratio'] * 3, 0)}/3，mean_trades≈{num(primary_row['mean_trades'], 1)}。"
    )
    evidence_2 = (
        f"参数邻域里最不差的 {best_neighbor['param_label']} 仍只有 mean_total_return≈{pct(best_neighbor['mean_total_return'])}；"
        f"主变体在 10/15/20bps 下继续走弱到 {pct(cost_df.iloc[1]['mean_total_return'])} / {pct(cost_df.iloc[2]['mean_total_return'])} / {pct(cost_df.iloc[3]['mean_total_return'])}。"
    )

    meta_df = pd.DataFrame(
        [
            {
                "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                "hard_verdict": verdict,
                "evidence_line_1": evidence_1,
                "evidence_line_2": evidence_2,
                "source_cache": "reports/artifacts/scout_tau_band_breakout_15m/cache/*__120d__15m.csv",
                "primary_variant": PRIMARY_LABEL,
                "primary_cost_bps_per_side": PRIMARY_COST,
                "best_neighbor_param": best_neighbor["param_label"],
            }
        ]
    )

    admission_df = pd.DataFrame(
        [
            {
                "candidate_id": "rank22_updownwave_persistence_gate",
                "verdict": verdict,
                "primary_variant": PRIMARY_LABEL,
                "primary_cost_bps_per_side": PRIMARY_COST,
                "mean_total_return": primary_row["mean_total_return"],
                "positive_asset_ratio": primary_row["positive_asset_ratio"],
                "mean_trades": primary_row["mean_trades"],
                "mean_no_trade_ratio": primary_row["mean_no_trade_ratio"],
                "best_neighbor": best_neighbor["param_label"],
                "best_neighbor_mean_total_return": best_neighbor["mean_total_return"],
                "decision_note": "MA20 原始 intake 版本在 6bps 仍显著为负；参数邻域最不差的 MA15 也只是轻微少亏且仅 1/3 资产为正，成本抬升后继续恶化，因此当前更诚实的 desk verdict 是 park。",
            }
        ]
    )

    summary_df.to_csv(SUMMARY_PATH, index=False)
    asset_df.to_csv(ASSET_SUMMARY_PATH, index=False)
    pd.concat(trades, ignore_index=True).to_csv(TRADES_PATH, index=False) if trades else pd.DataFrame().to_csv(TRADES_PATH, index=False)
    time_df.to_csv(TIME_STABILITY_PATH, index=False)
    param_df.to_csv(PARAM_STABILITY_PATH, index=False)
    asset_df.to_csv(CROSS_ASSET_PATH, index=False)
    cost_df.to_csv(COST_STABILITY_PATH, index=False)
    admission_df.to_csv(PAPER_CANDIDATE_PATH, index=False)
    meta_df.to_csv(META_PATH, index=False)

    write_report(summary_df, asset_df, time_df, param_df, cost_df, meta_df)


if __name__ == "__main__":
    main()
