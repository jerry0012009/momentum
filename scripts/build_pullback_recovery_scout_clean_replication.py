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
from momentum.signals.pullback_recovery_confirmation import (  # noqa: E402
    PullbackRecoveryConfirmationConfig,
    compute_pullback_recovery_confirmation_signals,
)

from build_volume_supportflip_higherlow_first_verdict import ASSETS, ensure_dir, pct, num, render_table  # noqa: E402

CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_pullback_recovery_confirmation_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_pullback_recovery_confirmation_15m"
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
    "label": "pullback2_vol1.0_break1",
    "pullback_lookback": 2,
    "vol_recover_th": 1.0,
    "breakout_lookback": 1,
}
PARAM_GRID = [
    {"label": "pb1_v0.5_b1", "pullback_lookback": 1, "vol_recover_th": 0.5, "breakout_lookback": 1},
    {"label": "pb2_v0.5_b1", "pullback_lookback": 2, "vol_recover_th": 0.5, "breakout_lookback": 1},
    {"label": "pb2_v1.0_b1", "pullback_lookback": 2, "vol_recover_th": 1.0, "breakout_lookback": 1},
    {"label": "pb2_v1.5_b1", "pullback_lookback": 2, "vol_recover_th": 1.5, "breakout_lookback": 1},
    {"label": "pb2_v1.0_b2", "pullback_lookback": 2, "vol_recover_th": 1.0, "breakout_lookback": 2},
    {"label": "pb3_v1.0_b1", "pullback_lookback": 3, "vol_recover_th": 1.0, "breakout_lookback": 1},
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



def backtest_cost(total_cost_bps_per_side: float) -> MultiTfMomentumBacktestConfig:
    return MultiTfMomentumBacktestConfig(
        fee_bps_per_side=float(total_cost_bps_per_side),
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
    return sig



def build_pullback_signals(bars: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    sig = compute_pullback_recovery_confirmation_signals(
        bars,
        config=PullbackRecoveryConfirmationConfig(
            window_5m=6,
            window_15m=6,
            threshold_5m=0.003,
            threshold_15m=0.006,
            resample_rule_15m="15min",
            vol_window=20,
            pullback_lookback=int(cfg["pullback_lookback"]),
            pullback_vol_z_max=0.0,
            vol_recover_th=float(cfg["vol_recover_th"]),
            breakout_lookback=int(cfg["breakout_lookback"]),
        ),
    )
    sig["timestamp"] = pd.to_datetime(sig["timestamp"], utc=True)
    return sig



def evaluate_one(bars: pd.DataFrame, *, variant: str, cfg: dict | None, cost_bps: float) -> tuple[dict, pd.DataFrame]:
    if cfg is None:
        sig = build_baseline_signals(bars)
    else:
        sig = build_pullback_signals(bars, cfg)
    bt = evaluate_multi_tf_momentum_reversal(sig, config=backtest_cost(cost_bps))
    summary = summarize_variant(bt.summary, asset=str(bars.iloc[0]["symbol"]), variant=variant, cost_bps=cost_bps)
    trades = bt.trades.copy()
    if not trades.empty:
        trades["asset"] = str(bars.iloc[0]["symbol"])
        trades["variant"] = variant
        trades["cost_bps_per_side"] = float(cost_bps)
    return summary, trades



def mean_numeric(df: pd.DataFrame, cols: list[str]) -> dict:
    out = {}
    for col in cols:
        out[col] = float(df[col].mean()) if col in df.columns and not df.empty else np.nan
    return out



def build_spec() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "section": "run_context",
                "item": "why_this_candidate_now",
                "value": "EMA 当前 waiting_not_due；Rank 7~16 已完成 clean replication + Light Stability Pack 并压回 park；Rank 2 已 narrow paper pilot approved 且当前没有真实 append/review need。",
                "why_it_matters": "当前 Scout Seat 的高边际值动作，是拿 repo 里已存在的 pullback recovery 模块做一刀 honest clean replication，而不是继续磨旧候选 wiring。",
                "operator_rule": "本轮只做一个新候选的 clean replication + Light Stability Pack；不同时打开多条线。",
            },
            {
                "section": "candidate",
                "item": "candidate_id",
                "value": "scout_pullback_recovery_confirmation_15m_v1",
                "why_it_matters": "给这条新 Scout 候选一个稳定句柄，方便后续 desk / report / log 统一追踪。",
                "operator_rule": "若 clean replication 后结论弱，直接 park，不继续拖成长文档。",
            },
            {
                "section": "source_anchor",
                "item": "paper_to_rule_mapping",
                "value": "Lo et al. (2000) / Jiang, Kelly, Xiu (2023) 的价格结构语义 -> repo 内 pullback_recovery_confirmation 模块",
                "why_it_matters": "它不是凭空扩框架，而是把 repo 里已经存在的结构确认模块压回当前 Scout Seat 的 15m crypto 快筛口径。",
                "operator_rule": "trade on=多周期动量同向 + 最近 pullback 量弱 + 当前恢复突破量强；trade off=任一条件缺失。",
            },
            {
                "section": "scope",
                "item": "market_timeframe",
                "value": "BTC-USD / ETH-USD / SOL-USD | 本地 Binance 120d cache | 15m",
                "why_it_matters": "完全复用现有历史样本，不追最新 bar，不引入新数据源。",
                "operator_rule": "第一刀只做这三币与固定 120d 样本。",
            },
            {
                "section": "variants",
                "item": "primary_variant",
                "value": "pullback_lookback=2, vol_recover_th=1.0, breakout_lookback=1",
                "why_it_matters": "直接沿用 repo 文档默认研究口径，避免后验挑最优。",
                "operator_rule": "parameter stability 只做主点邻域，不做大网格搜参。",
            },
            {
                "section": "light_stability_pack",
                "item": "checks",
                "value": "时间稳定性 / 参数稳定性 / 跨标的稳定性 / 成本-交易数稳定性",
                "why_it_matters": "满足当前 desk 对 fresh Scout 候选的最小诚实门槛。",
                "operator_rule": "若任一检查显示只是靠交易数塌缩才变好，默认不进 paper candidate。",
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
  <title>Scout Seat · pullback recovery confirmation · 15m crypto</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1120px; margin: 40px auto; padding: 0 18px; line-height: 1.68; color: #111827; background: #f8fafc; }}
    h1,h2,h3 {{ line-height: 1.25; }}
    .muted {{ color:#6b7280; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    ul {{ padding-left:20px; }}
    a {{ color:#2563eb; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
  </style>
</head>
<body>
  <p><a href="../../index.html">← 返回首页</a></p>
  <h1>Scout Seat · pullback recovery confirmation · 15m crypto</h1>
  <p class="muted">生成时间：{escape(str(meta['generated_at_utc']))} ｜ 新 fresh Scout 候选的 clean replication + Light Stability Pack。</p>

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
    {render_table(summary_df, percent_cols={'win_rate','avg_ret','median_ret','total_return','max_drawdown'}, digits_cols={'trades':0,'long_trades':0,'short_trades':0})}
  </div>

  <div class="card">
    <h2>跨标的稳定性</h2>
    {render_table(asset_df, percent_cols={'win_rate','avg_ret','median_ret','total_return','max_drawdown'}, digits_cols={'trades':0,'long_trades':0,'short_trades':0})}
  </div>

  <div class="card">
    <h2>时间稳定性</h2>
    {render_table(time_df, percent_cols={'win_rate','avg_ret','median_ret','total_return','max_drawdown'}, digits_cols={'trades':0})}
  </div>

  <div class="card">
    <h2>参数稳定性</h2>
    {render_table(param_df, percent_cols={'win_rate','avg_ret','median_ret','total_return','max_drawdown'}, digits_cols={'trades':0,'positive_asset_ratio':2})}
  </div>

  <div class="card">
    <h2>成本 / 交易数稳定性</h2>
    {render_table(cost_df, percent_cols={'win_rate','avg_ret','median_ret','total_return','max_drawdown'}, digits_cols={'trades':0,'positive_asset_ratio':2})}
    <p class="muted">artifact 目录：<code>reports/artifacts/scout_pullback_recovery_confirmation_15m/</code></p>
  </div>
</body>
</html>'''
    REPORT_PATH.write_text(html, encoding="utf-8")



def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    spec_df = build_spec()
    spec_df.to_csv(SPEC_PATH, index=False)

    bars_by_asset = {asset: load_cached_bars(symbol, asset) for asset, symbol in ASSETS.items()}

    summary_rows = []
    asset_rows = []
    trades_list = []
    for asset, bars in bars_by_asset.items():
        base_row, _ = evaluate_one(bars, variant=BASELINE_LABEL, cfg=None, cost_bps=PRIMARY_COST)
        prim_row, prim_trades = evaluate_one(bars, variant=PRIMARY_CFG["label"], cfg=PRIMARY_CFG, cost_bps=PRIMARY_COST)
        asset_rows.extend([base_row, prim_row])
        if not prim_trades.empty:
            trades_list.append(prim_trades)
        summary_rows.append({
            "asset": asset,
            "baseline_total_return": base_row["total_return"],
            "primary_total_return": prim_row["total_return"],
            "baseline_trades": base_row["trades"],
            "primary_trades": prim_row["trades"],
        })

    cross_df = pd.DataFrame(asset_rows)
    primary_assets = cross_df[cross_df["variant"] == PRIMARY_CFG["label"]].copy()
    baseline_assets = cross_df[cross_df["variant"] == BASELINE_LABEL].copy()
    aggregate = pd.DataFrame([
        {
            "variant": BASELINE_LABEL,
            **mean_numeric(baseline_assets, ["win_rate", "avg_ret", "median_ret", "total_return", "max_drawdown"]),
            "trades": float(baseline_assets["trades"].mean()),
            "long_trades": float(baseline_assets["long_trades"].mean()),
            "short_trades": float(baseline_assets["short_trades"].mean()),
            "positive_asset_ratio": float((baseline_assets["total_return"] > 0).mean()),
        },
        {
            "variant": PRIMARY_CFG["label"],
            **mean_numeric(primary_assets, ["win_rate", "avg_ret", "median_ret", "total_return", "max_drawdown"]),
            "trades": float(primary_assets["trades"].mean()),
            "long_trades": float(primary_assets["long_trades"].mean()),
            "short_trades": float(primary_assets["short_trades"].mean()),
            "positive_asset_ratio": float((primary_assets["total_return"] > 0).mean()),
        },
    ])

    time_rows = []
    for asset, bars in bars_by_asset.items():
        n = len(bars)
        chunk = n // TIME_BUCKETS
        for i in range(TIME_BUCKETS):
            start = i * chunk
            end = (i + 1) * chunk if i < TIME_BUCKETS - 1 else n
            part = bars.iloc[start:end].reset_index(drop=True)
            if len(part) < 100:
                continue
            row, _ = evaluate_one(part, variant=PRIMARY_CFG["label"], cfg=PRIMARY_CFG, cost_bps=PRIMARY_COST)
            row["time_bucket"] = f"bucket_{i+1}"
            time_rows.append(row)
    time_df = pd.DataFrame(time_rows)

    param_rows = []
    for cfg in PARAM_GRID:
        cfg_rows = []
        for asset, bars in bars_by_asset.items():
            row, _ = evaluate_one(bars, variant=cfg["label"], cfg=cfg, cost_bps=PRIMARY_COST)
            cfg_rows.append(row)
        cfg_df = pd.DataFrame(cfg_rows)
        param_rows.append(
            {
                "variant": cfg["label"],
                "pullback_lookback": cfg["pullback_lookback"],
                "vol_recover_th": cfg["vol_recover_th"],
                "breakout_lookback": cfg["breakout_lookback"],
                "total_return": float(cfg_df["total_return"].mean()),
                "max_drawdown": float(cfg_df["max_drawdown"].mean()),
                "trades": float(cfg_df["trades"].mean()),
                "positive_asset_ratio": float((cfg_df["total_return"] > 0).mean()),
                "win_rate": float(cfg_df["win_rate"].mean()),
                "avg_ret": float(cfg_df["avg_ret"].mean()),
                "median_ret": float(cfg_df["median_ret"].mean()),
            }
        )
    param_df = pd.DataFrame(param_rows).sort_values(["total_return", "positive_asset_ratio", "trades"], ascending=[False, False, False]).reset_index(drop=True)

    cost_rows = []
    for cost in COSTS:
        cost_cfg_rows = []
        for asset, bars in bars_by_asset.items():
            row, _ = evaluate_one(bars, variant=PRIMARY_CFG["label"], cfg=PRIMARY_CFG, cost_bps=cost)
            cost_cfg_rows.append(row)
        cdf = pd.DataFrame(cost_cfg_rows)
        cost_rows.append(
            {
                "cost_bps_per_side": float(cost),
                "variant": PRIMARY_CFG["label"],
                "total_return": float(cdf["total_return"].mean()),
                "max_drawdown": float(cdf["max_drawdown"].mean()),
                "trades": float(cdf["trades"].mean()),
                "positive_asset_ratio": float((cdf["total_return"] > 0).mean()),
                "win_rate": float(cdf["win_rate"].mean()),
                "avg_ret": float(cdf["avg_ret"].mean()),
                "median_ret": float(cdf["median_ret"].mean()),
            }
        )
    cost_df = pd.DataFrame(cost_rows)

    if not trades_list:
        trades_df = pd.DataFrame(columns=["asset", "variant", "cost_bps_per_side"])
    else:
        trades_df = pd.concat(trades_list, ignore_index=True)

    primary_total = float(aggregate.loc[aggregate["variant"] == PRIMARY_CFG["label"], "total_return"].iloc[0])
    primary_positive_ratio = float(aggregate.loc[aggregate["variant"] == PRIMARY_CFG["label"], "positive_asset_ratio"].iloc[0])
    primary_trades = float(aggregate.loc[aggregate["variant"] == PRIMARY_CFG["label"], "trades"].iloc[0])
    primary_cost_10 = float(cost_df.loc[cost_df["cost_bps_per_side"] == 10.0, "total_return"].iloc[0])
    primary_cost_20 = float(cost_df.loc[cost_df["cost_bps_per_side"] == 20.0, "total_return"].iloc[0])
    positive_buckets = float((time_df["total_return"] > 0).mean()) if not time_df.empty else 0.0
    positive_param_ratio = float((param_df["total_return"] > 0).mean()) if not param_df.empty else 0.0
    best_param = param_df.iloc[0]

    is_paper_candidate = (
        primary_total > 0
        and primary_positive_ratio >= (2.0 / 3.0)
        and primary_cost_10 > 0
        and primary_trades >= 40
    )
    if is_paper_candidate:
        verdict = "当前 pullback recovery confirmation 已满足最小 paper candidate 条件：进入 paper candidate pool，但暂不升 narrow paper pilot。"
    else:
        verdict = "当前 pullback recovery confirmation 在本地 120d/15m 样本上更诚实的读法仍是 park / evidence pool，不进入 paper candidate pool。"

    paper_candidate_df = pd.DataFrame([
        {
            "candidate_id": "scout_pullback_recovery_confirmation_15m_v1",
            "verdict": "paper_candidate" if is_paper_candidate else "park",
            "primary_variant": PRIMARY_CFG["label"],
            "aggregate_total_return_6bps": primary_total,
            "positive_asset_ratio_6bps": primary_positive_ratio,
            "aggregate_trades_6bps": primary_trades,
            "aggregate_total_return_10bps": primary_cost_10,
            "aggregate_total_return_20bps": primary_cost_20,
            "positive_time_bucket_ratio": positive_buckets,
            "positive_param_ratio": positive_param_ratio,
            "best_neighbor_variant": best_param["variant"],
            "best_neighbor_total_return": float(best_param["total_return"]),
            "next_gate": "若继续认领，默认只做最小 paper candidate wiring / monitoring sketch，或一个真正改变 verdict 的最小检查；不要回到泛研究态。",
        }
    ])

    meta_df = pd.DataFrame([
        {
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "candidate_id": "scout_pullback_recovery_confirmation_15m_v1",
            "desk_role": "fresh Scout intake / paper-based 15m crypto candidate",
            "hard_verdict": verdict,
            "evidence_line_1": f"primary variant 6bps/side aggregate mean_total_return={primary_total:.4f}, positive_asset_ratio={primary_positive_ratio:.2f}, mean_trades={primary_trades:.1f}。",
            "evidence_line_2": f"10bps/side mean_total_return={primary_cost_10:.4f}，20bps/side={primary_cost_20:.4f}；time_stability 正收益 bucket 占比={positive_buckets:.2f}；最优邻域参数={best_param['variant']} mean_total_return={float(best_param['total_return']):.4f}。",
        }
    ])

    aggregate.to_csv(SUMMARY_PATH, index=False)
    cross_df.to_csv(ASSET_SUMMARY_PATH, index=False)
    cross_df.to_csv(CROSS_ASSET_PATH, index=False)
    time_df.to_csv(TIME_STABILITY_PATH, index=False)
    param_df.to_csv(PARAM_STABILITY_PATH, index=False)
    cost_df.to_csv(COST_STABILITY_PATH, index=False)
    paper_candidate_df.to_csv(PAPER_CANDIDATE_PATH, index=False)
    trades_df.to_csv(TRADES_PATH, index=False)
    meta_df.to_csv(META_PATH, index=False)
    write_report(aggregate, cross_df, time_df, param_df, cost_df, meta_df)
    print(f"[ok] wrote {ART_DIR}")
    print(meta_df.iloc[0]["hard_verdict"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
