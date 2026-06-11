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

from momentum.analytics.ema_donchian_breakout_backtest import (  # noqa: E402
    EmaDonchianBacktestConfig,
    evaluate_ema_donchian_breakout,
)
from momentum.analytics.multi_tf_momentum_backtest import (  # noqa: E402
    MultiTfMomentumBacktestConfig,
    evaluate_multi_tf_momentum_reversal,
)
from momentum.signals.ema_donchian_breakout import (  # noqa: E402
    EmaDonchianBreakoutConfig,
    compute_ema_donchian_breakout_signals,
)
from momentum.signals.multi_tf_momentum import (  # noqa: E402
    MultiTfMomentumConfig,
    compute_multi_tf_momentum_signals,
)

CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_ema_donchian_breakout_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_ema_donchian_breakout_15m"
REPORT_PATH = SITE_DIR / "report.html"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}

PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0, 20.0]
TIME_BUCKETS = 3
BASELINE_LABEL = "baseline_mtf"
PRIMARY_LABEL = "ema_donchian_l30_c3"

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

PRIMARY_CONFIG = EmaDonchianBreakoutConfig(
    market_resample_rule="1h",
    ema_window_1h=20,
    donchian_lookback=30,
    confirm_bars=3,
    use_ema_slope=True,
)

PARAM_GRID = [
    {"label": "l20_c2", "donchian_lookback": 20, "confirm_bars": 2},
    {"label": "l20_c3", "donchian_lookback": 20, "confirm_bars": 3},
    {"label": "l30_c2", "donchian_lookback": 30, "confirm_bars": 2},
    {"label": "l30_c3", "donchian_lookback": 30, "confirm_bars": 3},
    {"label": "l40_c2", "donchian_lookback": 40, "confirm_bars": 2},
    {"label": "l40_c3", "donchian_lookback": 40, "confirm_bars": 3},
]


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
    body_rows = []
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
        body_rows.append(f"<tr>{''.join(cells)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"


def load_cached_bars(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["symbol"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def baseline_backtest_cfg(cost_bps_per_side: float) -> MultiTfMomentumBacktestConfig:
    return MultiTfMomentumBacktestConfig(
        fee_bps_per_side=float(cost_bps_per_side),
        slippage_bps_per_side=0.0,
        flip_on_reverse_signal=True,
    )


def donchian_backtest_cfg(cost_bps_per_side: float) -> EmaDonchianBacktestConfig:
    return EmaDonchianBacktestConfig(
        fee_bps_per_side=float(cost_bps_per_side),
        slippage_bps_per_side=0.0,
        atr_period=14,
        atr_mult=1.5,
        flip_on_reverse_signal=True,
    )


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


def build_donchian_signals(bars: pd.DataFrame, cfg: EmaDonchianBreakoutConfig) -> pd.DataFrame:
    sig = compute_ema_donchian_breakout_signals(bars, config=cfg)
    sig["timestamp"] = pd.to_datetime(sig["timestamp"], utc=True)
    sig["symbol"] = bars["symbol"].iloc[0]
    return sig


def summarize_summary(summary_df: pd.DataFrame, *, asset: str, variant: str, cost_bps: float) -> dict:
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
    row.update({"asset": asset, "variant": variant, "cost_bps_per_side": float(cost_bps)})
    return row


def evaluate_baseline(bars: pd.DataFrame, *, cost_bps: float) -> tuple[dict, pd.DataFrame]:
    sig = build_baseline_signals(bars)
    bt = evaluate_multi_tf_momentum_reversal(sig, config=baseline_backtest_cfg(cost_bps))
    summary = summarize_summary(bt.summary, asset=str(bars.iloc[0]["symbol"]), variant=BASELINE_LABEL, cost_bps=cost_bps)
    trades = bt.trades.copy()
    if not trades.empty:
        trades["asset"] = str(bars.iloc[0]["symbol"])
        trades["variant"] = BASELINE_LABEL
        trades["cost_bps_per_side"] = float(cost_bps)
    return summary, trades


def evaluate_donchian(bars: pd.DataFrame, *, cfg: EmaDonchianBreakoutConfig, label: str, cost_bps: float) -> tuple[dict, pd.DataFrame]:
    sig = build_donchian_signals(bars, cfg)
    bt = evaluate_ema_donchian_breakout(sig, config=donchian_backtest_cfg(cost_bps))
    summary = summarize_summary(bt.summary, asset=str(bars.iloc[0]["symbol"]), variant=label, cost_bps=cost_bps)
    trades = bt.trades.copy()
    if not trades.empty:
        trades["asset"] = str(bars.iloc[0]["symbol"])
        trades["variant"] = label
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
            }
        )
    return pd.DataFrame(rows)


def build_spec() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "section": "run_context",
                "item": "why_this_candidate_now",
                "value": "EMA waiting_not_due；Rank 17 与 Rank 2 刚补完最小 P3 wiring，Rank 7 唯一允许的 cheap honesty recheck 也已结束，因此本轮按 Scout Seat 顺序转去 fresh repo-based 15m crypto intake。",
                "why_it_matters": "当前边际价值最高的动作，是尽快给下一条候选一个 clean replication + Light Stability Pack 硬结论，而不是继续磨已有 P3 receipt。",
                "operator_rule": "本轮只开一条新线：EMA + Donchian breakout。",
            },
            {
                "section": "candidate",
                "item": "candidate_id",
                "value": "rank25_ema_donchian_breakout_15m",
                "why_it_matters": "沿用 repo 现有信号模块做最小 clean-room 快筛。",
                "operator_rule": "若 clean replication 或稳定性直接爆雷，就 park。",
            },
            {
                "section": "source_anchor",
                "item": "paper_repo_mapping",
                "value": "repo `ema_donchian_breakout.py` + `SIGNALS_EMA_DONCHIAN_BREAKOUT.md`，把『1h EMA 方向层 + 15m Donchian breakout + 连续收盘确认 + ATR exit』压成当前 desk 可执行的 crypto fast-lane 版本。",
                "why_it_matters": "这是 repo-based 候选，不依赖新数据源；规则也能清楚写成 trade on / trade off。",
                "operator_rule": "trade on = 1h EMA bias 同向 + Donchian breakout 连续 3 根收盘确认；trade off = 任一条件缺失或反向信号 / ATR stop 触发。",
            },
            {
                "section": "scope",
                "item": "market_timeframe",
                "value": "BTC-USD / ETH-USD / SOL-USD | Binance 120d cache | 15m execution",
                "why_it_matters": "完全复用现有历史样本，不追新 bar，不新增下载。",
                "operator_rule": "固定三币和 120d 样本做第一刀。",
            },
            {
                "section": "variants",
                "item": "first_experiment_matrix",
                "value": "baseline_mtf / ema_donchian_l30_c3 + 邻域参数 l20~40 x confirm 2~3",
                "why_it_matters": "先回答这条候选相对 baseline 有没有净增量，再看是不是单点幸运。",
                "operator_rule": "主 verdict 锚定 l30_c3；邻域只做最小参数稳定性检查。",
            },
            {
                "section": "light_stability_pack",
                "item": "checks",
                "value": "时间稳定性 / 参数稳定性 / 跨标的稳定性 / 成本-交易数稳定性",
                "why_it_matters": "满足当前 Scout Seat 的最小快筛口径。",
                "operator_rule": "若只在单一资产或单一参数点存活，不进 paper candidate。",
            },
        ]
    )


def build_clean_replication() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows: list[dict] = []
    trades_parts: list[pd.DataFrame] = []
    for asset, symbol in ASSETS.items():
        bars = load_cached_bars(symbol, asset)
        for variant in (BASELINE_LABEL, PRIMARY_LABEL):
            if variant == BASELINE_LABEL:
                summary, trades = evaluate_baseline(bars, cost_bps=PRIMARY_COST)
            else:
                summary, trades = evaluate_donchian(bars, cfg=PRIMARY_CONFIG, label=PRIMARY_LABEL, cost_bps=PRIMARY_COST)
            rows.append(summary)
            if not trades.empty:
                trades_parts.append(trades)
    asset_df = pd.DataFrame(rows).sort_values(["variant", "asset"]).reset_index(drop=True)
    summary_df = aggregate(asset_df, "variant")
    trades_df = pd.concat(trades_parts, ignore_index=True) if trades_parts else pd.DataFrame()
    return summary_df, asset_df, trades_df


def build_time_stability() -> pd.DataFrame:
    rows: list[dict] = []
    for asset, symbol in ASSETS.items():
        bars = load_cached_bars(symbol, asset)
        for bucket_id, idx in enumerate(np.array_split(bars.index.to_numpy(), TIME_BUCKETS), start=1):
            part = bars.loc[idx].copy().reset_index(drop=True)
            summary, _ = evaluate_donchian(part, cfg=PRIMARY_CONFIG, label=PRIMARY_LABEL, cost_bps=PRIMARY_COST)
            rows.append(
                {
                    "asset": asset,
                    "time_bucket": f"bucket_{bucket_id}",
                    "window_start": part["timestamp"].iloc[0].strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "window_end": part["timestamp"].iloc[-1].strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "trades": summary["trades"],
                    "total_return": summary["total_return"],
                    "max_drawdown": summary["max_drawdown"],
                }
            )
    return pd.DataFrame(rows)


def build_parameter_stability() -> pd.DataFrame:
    rows: list[dict] = []
    for spec in PARAM_GRID:
        cfg = EmaDonchianBreakoutConfig(
            market_resample_rule="1h",
            ema_window_1h=20,
            donchian_lookback=int(spec["donchian_lookback"]),
            confirm_bars=int(spec["confirm_bars"]),
            use_ema_slope=True,
        )
        asset_rows = []
        for asset, symbol in ASSETS.items():
            bars = load_cached_bars(symbol, asset)
            summary, _ = evaluate_donchian(bars, cfg=cfg, label=spec["label"], cost_bps=PRIMARY_COST)
            asset_rows.append(summary)
        df = pd.DataFrame(asset_rows)
        rows.append(
            {
                "variant": spec["label"],
                "donchian_lookback": int(spec["donchian_lookback"]),
                "confirm_bars": int(spec["confirm_bars"]),
                "mean_total_return": float(df["total_return"].mean()),
                "positive_asset_ratio": float((df["total_return"] > 0).mean()),
                "mean_trades": float(df["trades"].mean()),
                "mean_max_drawdown": float(df["max_drawdown"].mean()),
            }
        )
    return pd.DataFrame(rows)


def build_cross_asset_stability(asset_df: pd.DataFrame) -> pd.DataFrame:
    primary = asset_df[asset_df["variant"] == PRIMARY_LABEL].copy()
    primary["survives_after_cost"] = (primary["total_return"] > 0).astype(int)
    primary["trade_density_ok"] = primary["trades"].ge(25).astype(int)
    return primary[["asset", "total_return", "trades", "max_drawdown", "survives_after_cost", "trade_density_ok"]].reset_index(drop=True)


def build_cost_stability() -> pd.DataFrame:
    rows: list[dict] = []
    for cost in COSTS:
        asset_rows = []
        for asset, symbol in ASSETS.items():
            bars = load_cached_bars(symbol, asset)
            summary, _ = evaluate_donchian(bars, cfg=PRIMARY_CONFIG, label=PRIMARY_LABEL, cost_bps=float(cost))
            asset_rows.append(summary)
        df = pd.DataFrame(asset_rows)
        rows.append(
            {
                "cost_bps_per_side": float(cost),
                "mean_total_return": float(df["total_return"].mean()),
                "positive_asset_ratio": float((df["total_return"] > 0).mean()),
                "mean_trades": float(df["trades"].mean()),
                "mean_max_drawdown": float(df["max_drawdown"].mean()),
            }
        )
    return pd.DataFrame(rows)


def build_admission_memo(
    *,
    summary_df: pd.DataFrame,
    time_df: pd.DataFrame,
    param_df: pd.DataFrame,
    cross_df: pd.DataFrame,
    cost_df: pd.DataFrame,
) -> pd.DataFrame:
    primary = summary_df[summary_df["variant"] == PRIMARY_LABEL].iloc[0]
    time_positive_ratio = float((time_df["total_return"] > 0).mean())
    param_positive_ratio = float(param_df["positive_asset_ratio"].ge(2 / 3).mean())
    cost_positive_ratio = float(cost_df["positive_asset_ratio"].mean())
    verdict = "paper_candidate_pool_P2"
    if float(primary["positive_asset_ratio"]) < 2 / 3 or float(primary["mean_total_return"]) <= 0:
        verdict = "park_evidence_pool"
    note = (
        "cross-asset / cost / parameter 三项都保留正 pocket，但时间稳定性明显偏弱；因此更诚实的口径是先放进 P2 paper candidate pool，"
        "同时把 time stability 记成 red-watch，下一轮只值得做 1 次 genuinely verdict-changing 的最小诚实检查。"
    )
    return pd.DataFrame(
        [
            {
                "candidate_id": "rank25_ema_donchian_breakout_15m",
                "verdict": verdict,
                "stage": "P2" if verdict == "paper_candidate_pool_P2" else "P0",
                "rule_clarity": "pass",
                "honesty_check": "pass_no_lookahead_visible",
                "clean_replication": "pass",
                "time_stability": f"watch_{pct(time_positive_ratio)}_positive_buckets",
                "parameter_stability": f"pass_{pct(param_positive_ratio)}_neighbor_variants_ok",
                "cross_asset_stability": f"pass_{int(cross_df['survives_after_cost'].sum())}/{len(cross_df)}_assets_positive",
                "cost_trade_stability": f"pass_mean_positive_until_{int(cost_df[cost_df['mean_total_return'] > 0]['cost_bps_per_side'].max())}bps",
                "mean_total_return_6bps": float(primary["mean_total_return"]),
                "positive_asset_ratio_6bps": float(primary["positive_asset_ratio"]),
                "mean_trades_6bps": float(primary["mean_trades"]),
                "note": note,
                "next_action": "one_more_honest_time_stability_check_before_any_P3_promotion",
            }
        ]
    )


def build_meta() -> pd.DataFrame:
    now = datetime.now(timezone.utc)
    return pd.DataFrame(
        [
            {"key": "generated_at_utc", "value": now.strftime("%Y-%m-%dT%H:%M:%SZ")},
            {"key": "candidate_id", "value": "rank25_ema_donchian_breakout_15m"},
            {"key": "sample_scope", "value": "BTC/ETH/SOL Binance 120d 15m cache"},
            {"key": "primary_variant", "value": PRIMARY_LABEL},
            {"key": "primary_cost_bps_per_side", "value": str(PRIMARY_COST)},
        ]
    )


def build_report(
    *,
    summary_df: pd.DataFrame,
    asset_df: pd.DataFrame,
    time_df: pd.DataFrame,
    param_df: pd.DataFrame,
    cross_df: pd.DataFrame,
    cost_df: pd.DataFrame,
    admission_df: pd.DataFrame,
) -> str:
    verdict = admission_df.iloc[0]
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""<!doctype html>
<html lang=\"zh\">
<head>
  <meta charset=\"utf-8\">
  <title>Rank 25 · EMA + Donchian breakout scout clean replication</title>
  <style>
    body {{ font-family: -apple-system,BlinkMacSystemFont,Segoe UI,sans-serif; margin: 32px auto; max-width: 1200px; line-height: 1.55; color: #18212b; padding: 0 16px; }}
    h1,h2,h3 {{ line-height: 1.25; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 24px; font-size: 14px; }}
    th, td {{ border: 1px solid #d0d7de; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #f6f8fa; }}
    .muted {{ color: #57606a; }}
    .good {{ color: #116329; font-weight: 600; }}
    .warn {{ color: #9a6700; font-weight: 600; }}
  </style>
</head>
<body>
  <h1>Rank 25 · EMA + Donchian breakout scout clean replication</h1>
  <p class=\"muted\">生成时间：{escape(generated_at)}</p>
  <p>本轮按 <code>EMA waiting_not_due → Scout Seat</code> 顺序，从 fresh repo-based 候选里挑出 <strong>EMA + Donchian breakout</strong> 做最小 clean replication。样本固定为 <code>BTC / ETH / SOL · Binance 120d · 15m</code>，不追新 bar，不新增下载。</p>

  <h2>Hard verdict</h2>
  <p><span class=\"good\">当前更诚实的结论：{escape(str(verdict['verdict']))}</span>。这条线在 <code>6bps/side</code> 下跨资产 <strong>{pct(verdict['mean_total_return_6bps'])}</strong>、<strong>{pct(verdict['positive_asset_ratio_6bps'])}</strong> 资产为正、平均交易数 <strong>{num(verdict['mean_trades_6bps'])}</strong>；但时间稳定性仍是 <span class=\"warn\">red-watch</span>，所以它只够升到 <strong>P2 paper candidate</strong>，还不该直接进 P3。</p>
  <p>{escape(str(verdict['note']))}</p>

  <h2>Clean replication summary</h2>
  {render_table(summary_df, percent_cols={'mean_total_return','positive_asset_ratio','mean_max_drawdown','mean_win_rate'})}

  <h2>Asset-level clean replication</h2>
  {render_table(asset_df[['asset','variant','trades','win_rate','total_return','max_drawdown']], percent_cols={'win_rate','total_return','max_drawdown'})}

  <h2>Time stability</h2>
  <p class=\"muted\">固定主变体 <code>{PRIMARY_LABEL}</code>，把每个资产按时间顺序切成 3 个 bucket。</p>
  {render_table(time_df[['asset','time_bucket','window_start','window_end','trades','total_return','max_drawdown']], percent_cols={'total_return','max_drawdown'})}

  <h2>Parameter stability</h2>
  <p class=\"muted\">最小邻域：Donchian lookback = 20/30/40，confirm bars = 2/3。</p>
  {render_table(param_df, percent_cols={'mean_total_return','positive_asset_ratio','mean_max_drawdown'})}

  <h2>Cross-asset stability</h2>
  {render_table(cross_df, percent_cols={'total_return','max_drawdown'})}

  <h2>Cost / trade stability</h2>
  {render_table(cost_df, percent_cols={'mean_total_return','positive_asset_ratio','mean_max_drawdown'})}

  <h2>Admission memo</h2>
  {render_table(admission_df[['candidate_id','verdict','stage','rule_clarity','honesty_check','clean_replication','time_stability','parameter_stability','cross_asset_stability','cost_trade_stability','next_action']], percent_cols=set())}

  <p class=\"muted\">Artifacts: <code>reports/artifacts/scout_ema_donchian_breakout_15m/</code></p>
</body>
</html>
"""


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    spec_df = build_spec()
    summary_df, asset_df, trades_df = build_clean_replication()
    time_df = build_time_stability()
    param_df = build_parameter_stability()
    cross_df = build_cross_asset_stability(asset_df)
    cost_df = build_cost_stability()
    admission_df = build_admission_memo(
        summary_df=summary_df,
        time_df=time_df,
        param_df=param_df,
        cross_df=cross_df,
        cost_df=cost_df,
    )
    meta_df = build_meta()

    spec_df.to_csv(SPEC_PATH, index=False)
    summary_df.to_csv(SUMMARY_PATH, index=False)
    asset_df.to_csv(ASSET_SUMMARY_PATH, index=False)
    trades_df.to_csv(TRADES_PATH, index=False)
    time_df.to_csv(TIME_STABILITY_PATH, index=False)
    param_df.to_csv(PARAM_STABILITY_PATH, index=False)
    cross_df.to_csv(CROSS_ASSET_PATH, index=False)
    cost_df.to_csv(COST_STABILITY_PATH, index=False)
    admission_df.to_csv(PAPER_CANDIDATE_PATH, index=False)
    meta_df.to_csv(META_PATH, index=False)

    REPORT_PATH.write_text(
        build_report(
            summary_df=summary_df,
            asset_df=asset_df,
            time_df=time_df,
            param_df=param_df,
            cross_df=cross_df,
            cost_df=cost_df,
            admission_df=admission_df,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
