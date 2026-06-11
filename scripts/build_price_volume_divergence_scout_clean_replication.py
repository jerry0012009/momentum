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
from momentum.signals.price_volume_divergence import (  # noqa: E402
    PriceVolumeDivergenceConfig,
    compute_price_volume_divergence_signals,
)

from build_volume_supportflip_higherlow_first_verdict import ASSETS, ensure_dir, num, pct, render_table  # noqa: E402

CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_price_volume_divergence_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_price_volume_divergence_15m"
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
PRIMARY_CFG = {
    "label": "pvd_break24_delta0.5_warn3",
    "breakout_lookback": 24,
    "divergence_delta_z": 0.5,
    "z_confirm": 0.5,
    "warning_active_bars": 3,
}
PARAM_GRID = [
    {"label": "pvd_break20_delta0.3_warn2", "breakout_lookback": 20, "divergence_delta_z": 0.3, "z_confirm": 0.3, "warning_active_bars": 2},
    {"label": "pvd_break20_delta0.5_warn3", "breakout_lookback": 20, "divergence_delta_z": 0.5, "z_confirm": 0.5, "warning_active_bars": 3},
    {"label": "pvd_break24_delta0.5_warn3", "breakout_lookback": 24, "divergence_delta_z": 0.5, "z_confirm": 0.5, "warning_active_bars": 3},
    {"label": "pvd_break24_delta0.8_warn3", "breakout_lookback": 24, "divergence_delta_z": 0.8, "z_confirm": 0.5, "warning_active_bars": 3},
    {"label": "pvd_break28_delta0.5_warn4", "breakout_lookback": 28, "divergence_delta_z": 0.5, "z_confirm": 0.5, "warning_active_bars": 4},
    {"label": "pvd_break24_delta0.5_warn5", "breakout_lookback": 24, "divergence_delta_z": 0.5, "z_confirm": 0.5, "warning_active_bars": 5},
]
TIME_BUCKETS = 3
BASELINE_LABEL = "baseline_mtf_momentum"


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



def summarize_variant(summary_df: pd.DataFrame, *, asset: str, variant: str, cost_bps: float) -> dict:
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
        }
    row = summary_df.iloc[0].to_dict()
    return {"asset": asset, "variant": variant, "cost_bps_per_side": float(cost_bps), **row}



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



def build_pvd_signals(bars: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    sig = compute_price_volume_divergence_signals(
        bars,
        config=PriceVolumeDivergenceConfig(
            window_5m=6,
            window_15m=6,
            threshold_5m=0.003,
            threshold_15m=0.006,
            resample_rule_15m="15min",
            vol_window=20,
            breakout_lookback=int(cfg["breakout_lookback"]),
            divergence_delta_z=float(cfg["divergence_delta_z"]),
            z_confirm=float(cfg["z_confirm"]),
            warning_active_bars=int(cfg["warning_active_bars"]),
        ),
    )
    sig["timestamp"] = pd.to_datetime(sig["timestamp"], utc=True)
    sig["symbol"] = bars["symbol"].iloc[0]
    return sig



def evaluate_one(bars: pd.DataFrame, *, variant: str, cfg: dict | None, cost_bps: float) -> tuple[dict, pd.DataFrame]:
    if cfg is None:
        sig = build_baseline_signals(bars)
    else:
        sig = build_pvd_signals(bars, cfg)
    bt = evaluate_multi_tf_momentum_reversal(sig, config=backtest_cfg(cost_bps))
    summary = summarize_variant(bt.summary, asset=str(bars.iloc[0]["symbol"]), variant=variant, cost_bps=cost_bps)
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
            }
        )
    return pd.DataFrame(out)



def build_spec() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "section": "run_context",
                "item": "why_this_candidate_now",
                "value": "EMA 当前 waiting_not_due；Rank 17 若无 verdict-changing 新证据不应继续磨；Rank 2 仅 append/review need 时再做。",
                "why_it_matters": "当前边际价值最高的是继续 fresh Scout intake，给出新的 clean replication + Light Stability Pack 三选一结论。",
                "operator_rule": "本轮只开一条新候选，不并行多条线。",
            },
            {
                "section": "candidate",
                "item": "candidate_id",
                "value": "scout_price_volume_divergence_15m_v1",
                "why_it_matters": "用稳定 ID 追踪这条 repo-based 过滤层候选。",
                "operator_rule": "若快筛后仍弱，直接 park。",
            },
            {
                "section": "source_anchor",
                "item": "paper_repo_mapping",
                "value": "Lo et al. (2000) 可程序化结构思想 + repo `price_volume_divergence.py`（breakout 时量价背离过滤）",
                "why_it_matters": "不是凭空扩框架，而是把已存在 repo 模块翻译成 15m crypto 快筛闭环。",
                "operator_rule": "trade on=多周期动量同向且未触发对应方向背离 warning；trade off=反向信号触发平翻仓。",
            },
            {
                "section": "scope",
                "item": "market_timeframe",
                "value": "BTC-USD / ETH-USD / SOL-USD | Binance 120d cache | 15m",
                "why_it_matters": "完全复用现有历史样本，不追最新 bar。",
                "operator_rule": "第一刀固定三币和 120d 样本。",
            },
            {
                "section": "light_stability_pack",
                "item": "checks",
                "value": "时间稳定性 / 参数稳定性 / 跨标的稳定性 / 成本-交易数稳定性",
                "why_it_matters": "满足当前 Scout Seat 的最小诚实门槛。",
                "operator_rule": "若改善只来自 trade_count 塌缩，默认不进 paper candidate。",
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
  <title>Scout Seat · price-volume divergence filter · 15m crypto</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1120px; margin: 40px auto; padding: 0 18px; line-height: 1.68; color: #111827; background: #f8fafc; }}
    h1,h2,h3 {{ line-height: 1.25; }}
    .muted {{ color:#6b7280; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
  </style>
</head>
<body>
  <p><a href="../../index.html">← 返回首页</a></p>
  <h1>Scout Seat · price-volume divergence filter · 15m crypto</h1>
  <p class="muted">生成时间：{escape(str(meta['generated_at_utc']))} ｜ fresh scout intake clean replication + Light Stability Pack。</p>

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
    {render_table(summary_df, percent_cols={'mean_total_return','positive_asset_ratio','mean_max_drawdown','mean_win_rate'}, digits_cols={'mean_trades':1})}
  </div>

  <div class="card">
    <h2>cross-asset stability（主变体）</h2>
    {render_table(asset_df, percent_cols={'total_return','win_rate','avg_ret','median_ret','max_drawdown'}, digits_cols={'trades':0,'long_trades':0,'short_trades':0})}
  </div>

  <div class="card">
    <h2>time stability（主变体）</h2>
    {render_table(time_df, percent_cols={'mean_total_return','positive_asset_ratio','mean_max_drawdown','mean_win_rate'}, digits_cols={'mean_trades':1})}
  </div>

  <div class="card">
    <h2>parameter stability</h2>
    {render_table(param_df, percent_cols={'mean_total_return','positive_asset_ratio','mean_max_drawdown','mean_win_rate'}, digits_cols={'mean_trades':1})}
  </div>

  <div class="card">
    <h2>cost / trade-count stability（主变体）</h2>
    {render_table(cost_df, percent_cols={'mean_total_return','positive_asset_ratio','mean_max_drawdown','mean_win_rate'}, digits_cols={'mean_trades':1})}
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
        summary, t = evaluate_one(bars, variant=BASELINE_LABEL, cfg=None, cost_bps=PRIMARY_COST)
        rows.append(summary)
        if not t.empty:
            trades.append(t)
        summary, t = evaluate_one(bars, variant=PRIMARY_CFG["label"], cfg=PRIMARY_CFG, cost_bps=PRIMARY_COST)
        rows.append(summary)
        if not t.empty:
            trades.append(t)

    summary_df = aggregate(pd.DataFrame(rows), "variant").sort_values("variant").reset_index(drop=True)
    asset_df = pd.DataFrame([r for r in rows if r["variant"] == PRIMARY_CFG["label"]]).sort_values("asset").reset_index(drop=True)

    time_rows = []
    for asset, symbol in ASSETS.items():
        bars = load_cached_bars(symbol, asset)
        idx_splits = np.array_split(np.arange(len(bars)), TIME_BUCKETS)
        for i, idx in enumerate(idx_splits, start=1):
            if len(idx) < 30:
                continue
            b = bars.iloc[idx].reset_index(drop=True)
            s, _ = evaluate_one(b, variant=PRIMARY_CFG["label"], cfg=PRIMARY_CFG, cost_bps=PRIMARY_COST)
            s["time_bucket"] = f"bucket_{i}"
            time_rows.append(s)
    time_df = aggregate(pd.DataFrame(time_rows), "time_bucket").sort_values("time_bucket").reset_index(drop=True)

    param_rows = []
    for cfg in PARAM_GRID:
        cfg_rows = []
        for asset, symbol in ASSETS.items():
            bars = load_cached_bars(symbol, asset)
            s, _ = evaluate_one(bars, variant=cfg["label"], cfg=cfg, cost_bps=PRIMARY_COST)
            cfg_rows.append(s)
        agg = aggregate(pd.DataFrame(cfg_rows), "variant")
        row = agg.iloc[0].to_dict()
        row["param_label"] = cfg["label"]
        param_rows.append(row)
    param_df = pd.DataFrame(param_rows)[["param_label", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_max_drawdown", "mean_win_rate"]]

    cost_rows = []
    for cost in COSTS:
        c_rows = []
        for asset, symbol in ASSETS.items():
            bars = load_cached_bars(symbol, asset)
            s, _ = evaluate_one(bars, variant=PRIMARY_CFG["label"], cfg=PRIMARY_CFG, cost_bps=cost)
            c_rows.append(s)
        agg = aggregate(pd.DataFrame(c_rows), "variant")
        row = agg.iloc[0].to_dict()
        row["cost_bps_per_side"] = float(cost)
        cost_rows.append(row)
    cost_df = pd.DataFrame(cost_rows)[["cost_bps_per_side", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_max_drawdown", "mean_win_rate"]]

    p6 = cost_df.loc[cost_df["cost_bps_per_side"] == 6.0].iloc[0]
    p10 = cost_df.loc[cost_df["cost_bps_per_side"] == 10.0].iloc[0]
    positive_buckets = int((time_df["mean_total_return"] > 0).sum()) if not time_df.empty else 0
    best_param = param_df.sort_values("mean_total_return", ascending=False).iloc[0]

    verdict = "paper candidate pool" if (p6["mean_total_return"] > 0) and (p10["mean_total_return"] > 0) and (p6["positive_asset_ratio"] >= 2/3) else "park / evidence pool"

    evidence1 = (
        f"主变体 {PRIMARY_CFG['label']} 在 6bps/side 下跨资产 mean_total_return={pct(p6['mean_total_return'])}，"
        f"positive_asset_ratio={pct(p6['positive_asset_ratio'])}，mean_trades={num(p6['mean_trades'],1)}。"
    )
    evidence2 = (
        f"10bps/side={pct(p10['mean_total_return'])}；time 正收益 bucket={positive_buckets}/{len(time_df)}；"
        f"最佳邻域={best_param['param_label']}({pct(best_param['mean_total_return'])})。"
    )

    memo_df = pd.DataFrame(
        [
            {
                "candidate_id": "scout_price_volume_divergence_15m_v1",
                "hard_verdict": verdict,
                "primary_variant": PRIMARY_CFG["label"],
                "cost_6_mean_total_return": p6["mean_total_return"],
                "cost_10_mean_total_return": p10["mean_total_return"],
                "cost_6_positive_asset_ratio": p6["positive_asset_ratio"],
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
                "candidate_id": "scout_price_volume_divergence_15m_v1",
                "source_anchor": "Lo et al. (2000) + repo price_volume_divergence.py",
                "hard_verdict": verdict,
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
    print(f"Wrote scout price-volume divergence artifacts to {ART_DIR}")
    print(f"Hard verdict: {verdict}")


if __name__ == "__main__":
    main()
