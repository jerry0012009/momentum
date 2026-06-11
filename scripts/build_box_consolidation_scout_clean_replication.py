#!/usr/bin/env python3
from __future__ import annotations

import math
import sys
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.signals.box_consolidation import BoxConsolidationConfig, compute_box_consolidation_signals  # noqa: E402
from build_volume_supportflip_higherlow_first_verdict import ASSETS, ensure_dir, pct, num, render_table  # noqa: E402

CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_box_consolidation_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_box_consolidation_15m"
REPORT_PATH = SITE_DIR / "report.html"
SPEC_PATH = ART_DIR / "clean_room_spec_v1.csv"
META_PATH = ART_DIR / "clean_replication_meta.csv"
SUMMARY_PATH = ART_DIR / "clean_replication_summary.csv"
ASSET_SUMMARY_PATH = ART_DIR / "clean_replication_asset_summary.csv"
TRADES_PATH = ART_DIR / "clean_replication_trades.csv"
TIME_STABILITY_PATH = ART_DIR / "time_stability.csv"
PARAM_STABILITY_PATH = ART_DIR / "parameter_stability.csv"
CROSS_ASSET_PATH = ART_DIR / "cross_asset_stability.csv"
COST_STABILITY_PATH = ART_DIR / "cost_trade_stability.csv"
PAPER_CANDIDATE_PATH = ART_DIR / "paper_candidate_admission_memo.csv"
SIGNAL_SNAPSHOT_PATH = ART_DIR / "signal_snapshot.csv"

ATR_PERIOD = 14
STOP_ATR = 1.0
TARGET_ATR = 2.0
TIME_STOP_BARS = 8
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0, 20.0]
TIME_BUCKETS = 3
PRIMARY_VARIANT = "accumulation_ready"
PRIMARY_LABEL = "d1.5_nb1.5_box20_buf5"
VARIANTS = ["narrow_accum_ready", "box_breakout_ready", "accumulation_ready"]

PRIMARY_CFG = {
    "label": PRIMARY_LABEL,
    "decline_lookback": 48,
    "min_decline_pct": 0.015,
    "decline_recent_window": 16,
    "bearish_floor_lookback": 64,
    "floor_hold_days": 3,
    "narrow_box_lookback": 12,
    "narrow_range_max": 0.015,
    "atr_period": 14,
    "narrow_atr_ratio_max": 0.010,
    "upwave_recent_window": 16,
    "box_lookback": 20,
    "box_range_min": 0.015,
    "box_range_max": 0.060,
    "breakout_buffer": 0.0005,
}
PARAM_GRID = [
    {**PRIMARY_CFG, "label": "d1.0_nb1.5_box20_buf5", "min_decline_pct": 0.010},
    {**PRIMARY_CFG, "label": "d1.5_nb1.2_box20_buf5", "narrow_range_max": 0.012},
    {**PRIMARY_CFG, "label": "d1.5_nb1.5_box16_buf5", "box_lookback": 16},
    {**PRIMARY_CFG, "label": "d1.5_nb1.5_box20_buf5"},
    {**PRIMARY_CFG, "label": "d2.0_nb1.5_box20_buf5", "min_decline_pct": 0.020},
    {**PRIMARY_CFG, "label": "d1.5_nb1.8_box20_buf5", "narrow_range_max": 0.018},
    {**PRIMARY_CFG, "label": "d1.5_nb1.5_box24_buf10", "box_lookback": 24, "breakout_buffer": 0.0010},
]


def load_cached_bars(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["symbol"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)



def compute_atr(df: pd.DataFrame, period: int = ATR_PERIOD) -> pd.Series:
    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [
            (df["high"] - df["low"]).abs(),
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.rolling(period, min_periods=period).mean()



def make_config(cfg: dict) -> BoxConsolidationConfig:
    return BoxConsolidationConfig(
        ma_period=20,
        decline_lookback=int(cfg["decline_lookback"]),
        min_decline_pct=float(cfg["min_decline_pct"]),
        decline_recent_window=int(cfg["decline_recent_window"]),
        bearish_floor_lookback=int(cfg["bearish_floor_lookback"]),
        floor_hold_days=int(cfg["floor_hold_days"]),
        narrow_box_lookback=int(cfg["narrow_box_lookback"]),
        narrow_range_max=float(cfg["narrow_range_max"]),
        atr_period=int(cfg["atr_period"]),
        narrow_atr_ratio_max=float(cfg["narrow_atr_ratio_max"]),
        upwave_recent_window=int(cfg["upwave_recent_window"]),
        box_lookback=int(cfg["box_lookback"]),
        box_range_min=float(cfg["box_range_min"]),
        box_range_max=float(cfg["box_range_max"]),
        breakout_buffer=float(cfg["breakout_buffer"]),
        require_chip_filter=False,
    )



def prepare_signals(asset: str, symbol: str, cfg: dict) -> pd.DataFrame:
    bars = load_cached_bars(symbol, asset).copy()
    bars["atr"] = compute_atr(bars)
    sig = compute_box_consolidation_signals(bars, config=make_config(cfg))
    sig["timestamp"] = pd.to_datetime(sig["timestamp"], utc=True)
    sig["asset"] = asset
    if "symbol" in sig.columns:
        sig = sig.drop(columns=["symbol"])
    return sig.sort_values("timestamp").reset_index(drop=True)



def signal_snapshot(df: pd.DataFrame) -> pd.DataFrame:
    keep = [
        "timestamp",
        "asset",
        "close",
        "prior_decline_recent",
        "narrow_box_ok",
        "box_width_ok",
        "box_breakout",
        "narrow_accum_ready",
        "box_breakout_ready",
        "accumulation_ready",
    ]
    rows = []
    for asset, g in df.groupby("asset", sort=True):
        tail = g.tail(12).copy()
        rows.extend(tail[keep].to_dict("records"))
    out = pd.DataFrame(rows)
    if not out.empty:
        out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return out



def max_drawdown_from_returns(returns: list[float]) -> float:
    if not returns:
        return 0.0
    equity = np.cumprod([1.0 + r for r in returns])
    peak = np.maximum.accumulate(equity)
    dd = equity / peak - 1.0
    return float(np.nanmin(dd)) if len(dd) else 0.0



def simulate_variant(df: pd.DataFrame, variant: str, cost_bps_per_side: float) -> tuple[pd.DataFrame, dict]:
    signal = df[variant].fillna(0).astype(int).to_numpy()
    timestamps = df["timestamp"].to_numpy()
    opens = df["open"].to_numpy(dtype=float)
    highs = df["high"].to_numpy(dtype=float)
    lows = df["low"].to_numpy(dtype=float)
    closes = df["close"].to_numpy(dtype=float)
    atrs = df["atr"].to_numpy(dtype=float)
    asset = str(df.iloc[0]["asset"])
    cost_rate = float(cost_bps_per_side) / 10000.0

    in_pos = False
    entry_idx = None
    entry_price = None
    entry_atr = None
    trades = []

    for idx in range(len(df) - 1):
        if not in_pos:
            prev_sig = int(signal[idx - 1]) if idx > 0 else 0
            if prev_sig == 0 and int(signal[idx]) == 1:
                atr = float(atrs[idx])
                entry_open = float(opens[idx + 1])
                if math.isfinite(atr) and atr > 0 and math.isfinite(entry_open) and entry_open > 0:
                    in_pos = True
                    entry_idx = idx + 1
                    entry_price = entry_open
                    entry_atr = atr
            continue

        assert entry_idx is not None and entry_price is not None and entry_atr is not None
        stop_price = entry_price - STOP_ATR * entry_atr
        target_price = entry_price + TARGET_ATR * entry_atr
        exit_reason = None
        exit_price = None
        exit_idx = idx

        if lows[idx] <= stop_price:
            exit_reason = "atr_stop"
            exit_price = stop_price
        elif highs[idx] >= target_price:
            exit_reason = "atr_target"
            exit_price = target_price
        elif int(signal[idx]) == 0:
            exit_reason = "signal_off"
            exit_price = float(closes[idx])
        elif (idx - entry_idx + 1) >= TIME_STOP_BARS:
            exit_reason = "time_stop"
            exit_price = float(closes[idx])

        if exit_reason is None:
            continue

        gross_mult = exit_price / entry_price
        net_mult = gross_mult * (1.0 - cost_rate) * (1.0 - cost_rate)
        net_ret = net_mult - 1.0
        trades.append(
            {
                "asset": asset,
                "variant": variant,
                "cost_bps_per_side": float(cost_bps_per_side),
                "entry_ts": pd.Timestamp(timestamps[entry_idx]).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": pd.Timestamp(timestamps[exit_idx]).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_price": float(entry_price),
                "exit_price": float(exit_price),
                "hold_bars": int(exit_idx - entry_idx + 1),
                "gross_ret": float(gross_mult - 1.0),
                "net_ret": float(net_ret),
                "win": int(net_ret > 0),
                "exit_reason": exit_reason,
            }
        )
        in_pos = False
        entry_idx = None
        entry_price = None
        entry_atr = None

    if in_pos and entry_idx is not None and entry_price is not None:
        exit_idx = len(df) - 1
        exit_price = float(closes[exit_idx])
        gross_mult = exit_price / entry_price
        net_mult = gross_mult * (1.0 - cost_rate) * (1.0 - cost_rate)
        net_ret = net_mult - 1.0
        trades.append(
            {
                "asset": asset,
                "variant": variant,
                "cost_bps_per_side": float(cost_bps_per_side),
                "entry_ts": pd.Timestamp(timestamps[entry_idx]).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": pd.Timestamp(timestamps[exit_idx]).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_price": float(entry_price),
                "exit_price": float(exit_price),
                "hold_bars": int(exit_idx - entry_idx + 1),
                "gross_ret": float(gross_mult - 1.0),
                "net_ret": float(net_ret),
                "win": int(net_ret > 0),
                "exit_reason": "forced_close",
            }
        )

    trades_df = pd.DataFrame(trades)
    signal_on_ratio = float(np.nanmean(signal)) if len(signal) else 0.0
    no_trade_ratio = 1.0 - signal_on_ratio
    candidate_entries = int(np.sum((np.r_[0, signal[:-1]] == 0) & (signal == 1)))
    if trades_df.empty:
        return trades_df, {
            "asset": asset,
            "variant": variant,
            "cost_bps_per_side": float(cost_bps_per_side),
            "trades": 0,
            "win_rate": np.nan,
            "avg_ret": np.nan,
            "median_ret": np.nan,
            "total_return": 0.0,
            "max_drawdown": 0.0,
            "avg_hold_bars": np.nan,
            "signal_on_ratio": signal_on_ratio,
            "no_trade_ratio": no_trade_ratio,
            "candidate_entries": candidate_entries,
        }

    returns = trades_df["net_ret"].astype(float).tolist()
    return trades_df, {
        "asset": asset,
        "variant": variant,
        "cost_bps_per_side": float(cost_bps_per_side),
        "trades": int(len(trades_df)),
        "win_rate": float(trades_df["win"].mean()),
        "avg_ret": float(trades_df["net_ret"].mean()),
        "median_ret": float(trades_df["net_ret"].median()),
        "total_return": float(np.prod(1.0 + np.array(returns)) - 1.0),
        "max_drawdown": max_drawdown_from_returns(returns),
        "avg_hold_bars": float(trades_df["hold_bars"].mean()),
        "signal_on_ratio": signal_on_ratio,
        "no_trade_ratio": no_trade_ratio,
        "candidate_entries": candidate_entries,
    }



def aggregate_rows(rows: list[dict], *, group_col: str) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    out = []
    for key, g in df.groupby(group_col, sort=False):
        out.append(
            {
                group_col: key,
                "mean_total_return": float(g["total_return"].mean()),
                "positive_asset_ratio": float((g["total_return"] > 0).mean()),
                "mean_trades": float(g["trades"].mean()),
                "mean_no_trade_ratio": float(g["no_trade_ratio"].mean()),
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
                "value": "EMA 当前 waiting_not_due；Rank 17 若无 genuinely verdict-changing evidence 不该继续磨；因此本轮转 fresh Scout intake。",
                "why_it_matters": "优先给出新的 paper/repo based 15m crypto 候选快筛闭环，而不是围着旧线补近义 wiring。",
                "operator_rule": "本轮只做一个新候选：source mapping -> clean replication -> Light Stability Pack -> park/paper candidate。",
            },
            {
                "section": "candidate",
                "item": "candidate_id",
                "value": "scout_box_consolidation_15m_v1",
                "why_it_matters": "用稳定句柄追踪这条结构 breakout 候选。",
                "operator_rule": "若结果弱，直接 park，不继续扩成结构长文。",
            },
            {
                "section": "source_anchor",
                "item": "paper_repo_mapping",
                "value": "Lo et al. (2000) / Jiang, Kelly, Xiu (2023) 的可程序化结构 alpha 语义 -> repo 现有 box_consolidation 模块。",
                "why_it_matters": "不是凭空发明新框架，而是把已有 repo 结构模块翻译成当前 desk 的 15m crypto 快筛口径。",
                "operator_rule": "trade on=先出现近期下跌+箱体/窄幅结构，再触发 narrow_accum_ready / box_breakout_ready；trade off=信号撤销、ATR 止损、ATR 止盈或 time stop。",
            },
            {
                "section": "scope",
                "item": "market_timeframe",
                "value": "BTC-USD / ETH-USD / SOL-USD | Binance 120d cache | 15m",
                "why_it_matters": "完全复用现有缓存，不追新 bar、不下载新数据。",
                "operator_rule": "先在三币固定样本完成最小诚实快筛。",
            },
            {
                "section": "light_stability_pack",
                "item": "checks",
                "value": "时间稳定性 / 参数稳定性 / 跨标的稳定性 / 成本-交易数稳定性",
                "why_it_matters": "满足当前 Scout Seat 的最低诚实门槛。",
                "operator_rule": "若只是靠 no-trade_ratio 拉高结果，默认不进 paper candidate。",
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
  <title>Scout Seat · box consolidation · 15m crypto</title>
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
  <h1>Scout Seat · box consolidation / structure breakout · 15m crypto</h1>
  <p class="muted">生成时间：{escape(str(meta['generated_at_utc']))} ｜ fresh Scout intake 的 clean replication + Light Stability Pack。</p>

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
    {render_table(summary_df, percent_cols={'mean_total_return','positive_asset_ratio','mean_no_trade_ratio','mean_max_drawdown','mean_win_rate'}, digits_cols={'mean_trades':1})}
  </div>

  <div class="card">
    <h2>cross-asset stability（主变体）</h2>
    {render_table(asset_df, percent_cols={'total_return','win_rate','avg_ret','median_ret','max_drawdown','signal_on_ratio','no_trade_ratio'}, digits_cols={'trades':0,'avg_hold_bars':1,'candidate_entries':0})}
  </div>

  <div class="card">
    <h2>time stability（主变体）</h2>
    {render_table(time_df, percent_cols={'mean_total_return','positive_asset_ratio','mean_no_trade_ratio','mean_max_drawdown','mean_win_rate'}, digits_cols={'mean_trades':1})}
  </div>

  <div class="card">
    <h2>parameter stability</h2>
    {render_table(param_df, percent_cols={'mean_total_return','positive_asset_ratio','mean_no_trade_ratio','mean_max_drawdown','mean_win_rate'}, digits_cols={'mean_trades':1})}
  </div>

  <div class="card">
    <h2>cost / trade-count stability（主变体）</h2>
    {render_table(cost_df, percent_cols={'mean_total_return','positive_asset_ratio','mean_no_trade_ratio','mean_max_drawdown','mean_win_rate'}, digits_cols={'mean_trades':1})}
  </div>

  <div class="card">
    <h2>trade on / trade off（plain language）</h2>
    <ul>
      <li><b>trade on：</b>先有一段近期回撤，再出现窄幅箱体或更宽箱体；随后当前 bar 满足 <code>narrow_accum_ready</code> / <code>box_breakout_ready</code>，下一根 open 才进场。</li>
      <li><b>trade off：</b>信号撤销、1 ATR 止损、2 ATR 止盈，或持有 8 根 bar 到时退出。</li>
      <li><b>诚实边界：</b>全部条件都只用当下和过去 bar 计算；没有 future label，也没有回头改箱体。</li>
    </ul>
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

    primary_signal_snapshots = []
    variant_rows = []
    variant_trades = []
    for asset, symbol in ASSETS.items():
        sig = prepare_signals(asset, symbol, PRIMARY_CFG)
        primary_signal_snapshots.append(signal_snapshot(sig))
        for variant in VARIANTS:
            trades_df, row = simulate_variant(sig, variant, PRIMARY_COST)
            variant_rows.append(row)
            if not trades_df.empty:
                variant_trades.append(trades_df)

    summary_df = aggregate_rows(variant_rows, group_col="variant").sort_values("variant").reset_index(drop=True)
    asset_df = pd.DataFrame([r for r in variant_rows if r["variant"] == PRIMARY_VARIANT]).sort_values("asset").reset_index(drop=True)

    time_rows = []
    for asset, symbol in ASSETS.items():
        sig = prepare_signals(asset, symbol, PRIMARY_CFG)
        buckets = np.array_split(sig.reset_index(drop=True), TIME_BUCKETS)
        for idx, bucket in enumerate(buckets, start=1):
            if bucket.empty:
                continue
            _, row = simulate_variant(bucket.reset_index(drop=True), PRIMARY_VARIANT, PRIMARY_COST)
            row["time_bucket"] = f"bucket_{idx}"
            time_rows.append(row)
    time_df = aggregate_rows(time_rows, group_col="time_bucket").sort_values("time_bucket").reset_index(drop=True)

    param_rows = []
    for cfg in PARAM_GRID:
        cfg_rows = []
        for asset, symbol in ASSETS.items():
            sig = prepare_signals(asset, symbol, cfg)
            _, row = simulate_variant(sig, PRIMARY_VARIANT, PRIMARY_COST)
            cfg_rows.append(row)
        agg = aggregate_rows(cfg_rows, group_col="variant")
        row = agg.iloc[0].to_dict()
        row["param_label"] = cfg["label"]
        param_rows.append(row)
    param_df = pd.DataFrame(param_rows)[["param_label", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_no_trade_ratio", "mean_max_drawdown", "mean_win_rate"]]

    cost_rows = []
    for cost in COSTS:
        rows = []
        for asset, symbol in ASSETS.items():
            sig = prepare_signals(asset, symbol, PRIMARY_CFG)
            _, row = simulate_variant(sig, PRIMARY_VARIANT, cost)
            rows.append(row)
        agg = aggregate_rows(rows, group_col="variant")
        row = agg.iloc[0].to_dict()
        row["cost_bps_per_side"] = float(cost)
        cost_rows.append(row)
    cost_df = pd.DataFrame(cost_rows)[["cost_bps_per_side", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_no_trade_ratio", "mean_max_drawdown", "mean_win_rate"]]

    primary_6 = cost_df.loc[cost_df["cost_bps_per_side"] == PRIMARY_COST].iloc[0]
    primary_10 = cost_df.loc[cost_df["cost_bps_per_side"] == 10.0].iloc[0]
    positive_buckets = int((time_df["mean_total_return"] > 0).sum()) if not time_df.empty else 0
    best_param = param_df.sort_values("mean_total_return", ascending=False).iloc[0]

    if (primary_6["mean_total_return"] > 0.0) and (primary_10["mean_total_return"] > 0.0) and (primary_6["positive_asset_ratio"] >= 2/3):
        verdict = "paper candidate pool"
    else:
        verdict = "park / evidence pool"

    memo_df = pd.DataFrame(
        [
            {
                "candidate_id": "scout_box_consolidation_15m_v1",
                "hard_verdict": verdict,
                "primary_variant": PRIMARY_LABEL,
                "primary_variant_signal": PRIMARY_VARIANT,
                "cost_6_mean_total_return": primary_6["mean_total_return"],
                "cost_10_mean_total_return": primary_10["mean_total_return"],
                "cost_6_positive_asset_ratio": primary_6["positive_asset_ratio"],
                "time_positive_bucket_count": positive_buckets,
                "best_param_label": best_param["param_label"],
                "best_param_mean_total_return": best_param["mean_total_return"],
                "notes": "结构箱体候选已完成 clean replication + Light Stability Pack；若只是靠 no-trade_ratio 才少亏，则默认 park。",
            }
        ]
    )

    evidence_line_1 = (
        f"主变体 {PRIMARY_LABEL} 在 6bps/side 下跨资产 mean_total_return={pct(primary_6['mean_total_return'])}，"
        f"positive_asset_ratio={pct(primary_6['positive_asset_ratio'])}，mean_trades={num(primary_6['mean_trades'], 1)}。"
    )
    evidence_line_2 = (
        f"10bps/side={pct(primary_10['mean_total_return'])}；time stability 正收益 bucket={positive_buckets}/{len(time_df)}；"
        f"最佳邻域={best_param['param_label']}({pct(best_param['mean_total_return'])})。"
    )

    meta_df = pd.DataFrame(
        [
            {
                "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                "candidate_id": "scout_box_consolidation_15m_v1",
                "source_anchor": "Lo et al. (2000) / Jiang, Kelly, Xiu (2023) -> repo box_consolidation module",
                "hard_verdict": verdict,
                "evidence_line_1": evidence_line_1,
                "evidence_line_2": evidence_line_2,
            }
        ]
    )

    summary_df.to_csv(SUMMARY_PATH, index=False)
    asset_df.to_csv(ASSET_SUMMARY_PATH, index=False)
    (pd.concat(variant_trades, ignore_index=True) if variant_trades else pd.DataFrame()).to_csv(TRADES_PATH, index=False)
    time_df.to_csv(TIME_STABILITY_PATH, index=False)
    param_df.to_csv(PARAM_STABILITY_PATH, index=False)
    asset_df.to_csv(CROSS_ASSET_PATH, index=False)
    cost_df.to_csv(COST_STABILITY_PATH, index=False)
    memo_df.to_csv(PAPER_CANDIDATE_PATH, index=False)
    meta_df.to_csv(META_PATH, index=False)
    pd.concat(primary_signal_snapshots, ignore_index=True).to_csv(SIGNAL_SNAPSHOT_PATH, index=False)

    write_report(summary_df, asset_df, time_df, param_df, cost_df, meta_df)
    print(f"Wrote scout box consolidation artifacts to {ART_DIR}")
    print(f"Hard verdict: {verdict}")


if __name__ == "__main__":
    main()
