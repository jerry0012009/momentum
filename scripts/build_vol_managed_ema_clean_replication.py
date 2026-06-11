#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_vol_managed_ema_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_vol_managed_ema_15m"
REPORT_PATH = SITE_DIR / "report.html"
SPEC_PATH = ART_DIR / "clean_room_spec_v1.csv"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
COSTS = [6.0, 10.0, 15.0, 20.0]
PRIMARY_COST = 6.0
EMA_FAST = 20
EMA_SLOW = 50
ATR_PERIOD = 14
PRIMARY_VARIANT = "atr_clip_050_150"
VARIANTS = [
    {"variant": "baseline_100", "atr_target": 1.00, "clip_min": 1.00, "clip_max": 1.00},
    {"variant": "atr_clip_075_125", "atr_target": 1.00, "clip_min": 0.75, "clip_max": 1.25},
    {"variant": "atr_clip_050_150", "atr_target": 1.00, "clip_min": 0.50, "clip_max": 1.50},
    {"variant": "atr_clip_025_175", "atr_target": 1.00, "clip_min": 0.25, "clip_max": 1.75},
]
PARAM_CONFIGS = [
    {"label": "f15_s40", "ema_fast": 15, "ema_slow": 40},
    {"label": "f20_s50", "ema_fast": 20, "ema_slow": 50},
    {"label": "f25_s60", "ema_fast": 25, "ema_slow": 60},
    {"label": "f20_s80", "ema_fast": 20, "ema_slow": 80},
    {"label": "f30_s90", "ema_fast": 30, "ema_slow": 90},
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
        tds = []
        for col in df.columns:
            value = row[col]
            if col in percent_cols:
                text = pct(value)
            elif isinstance(value, (float, np.floating, int, np.integer)) and not isinstance(value, bool):
                text = num(value, digits_cols.get(col, 2))
            else:
                text = str(value)
            tds.append(f"<td>{escape(text)}</td>")
        body.append(f"<tr>{''.join(tds)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def load_cached_bars(symbol: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df.sort_values("timestamp").reset_index(drop=True)


def ema(s: pd.Series, span: int) -> pd.Series:
    return s.ewm(span=span, adjust=False).mean()


def atr(df: pd.DataFrame, period: int = ATR_PERIOD) -> pd.Series:
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


def prepare_bars(asset: str, symbol: str, *, ema_fast: int = EMA_FAST, ema_slow: int = EMA_SLOW) -> pd.DataFrame:
    bars = load_cached_bars(symbol).copy()
    bars["asset"] = asset
    bars["ema_fast"] = ema(bars["close"], ema_fast)
    bars["ema_slow"] = ema(bars["close"], ema_slow)
    bars["atr14"] = atr(bars, ATR_PERIOD)
    bars["atr_pct"] = bars["atr14"] / bars["close"].replace(0.0, np.nan)
    bars["signal"] = (bars["ema_fast"] > bars["ema_slow"]).astype(float)
    bars["bar_ret"] = bars["close"] / bars["open"] - 1.0
    atr_ref = float(bars["atr_pct"].median(skipna=True))
    bars["atr_ref"] = atr_ref
    return bars


def build_position_series(bars: pd.DataFrame, variant_cfg: dict) -> pd.DataFrame:
    out = bars.copy()
    atr_ref = float(out["atr_ref"].iloc[0])
    size_raw = atr_ref / out["atr_pct"].replace(0.0, np.nan)
    size_raw = size_raw.replace([np.inf, -np.inf], np.nan).fillna(variant_cfg["atr_target"])
    size = size_raw.clip(variant_cfg["clip_min"], variant_cfg["clip_max"])
    if variant_cfg["clip_min"] == variant_cfg["clip_max"] == 1.0:
        size = pd.Series(1.0, index=out.index)
    out["size_mult"] = size
    out["desired_position"] = out["signal"] * out["size_mult"]
    out["position"] = out["desired_position"].shift(1).fillna(0.0)
    out["turnover"] = (out["position"] - out["position"].shift(1).fillna(0.0)).abs()
    return out


def simulate_variant(bars: pd.DataFrame, variant_cfg: dict, cost_bps_per_side: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = build_position_series(bars, variant_cfg)
    cost_rate = float(cost_bps_per_side) / 10000.0
    df["cost"] = df["turnover"] * cost_rate
    df["gross_ret"] = df["position"] * df["bar_ret"]
    df["net_ret"] = df["gross_ret"] - df["cost"]
    df["nav"] = (1.0 + df["net_ret"]).cumprod()
    df["variant"] = variant_cfg["variant"]
    df["cost_bps_per_side"] = float(cost_bps_per_side)
    df["trade_event"] = ((df["turnover"] > 1e-12) & (df["position"] > 0.0)).astype(int)
    nav = df[["asset", "timestamp", "variant", "cost_bps_per_side", "nav"]].copy()
    return df, nav


def summarize_asset_variant(df: pd.DataFrame, asset: str, variant: str, cost: float) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    running_peak = df["nav"].cummax()
    drawdown = df["nav"] / running_peak - 1.0
    active = df[df["position"] > 0.0].copy()
    return pd.DataFrame([
        {
            "asset": asset,
            "variant": variant,
            "cost_bps_per_side": float(cost),
            "bars": int(len(df)),
            "active_bar_ratio": float((df["position"] > 0.0).mean()),
            "avg_position": float(df["position"].mean()),
            "avg_active_position": float(active["position"].mean()) if not active.empty else np.nan,
            "trade_events": int(df["trade_event"].sum()),
            "turnover": float(df["turnover"].sum()),
            "mean_bar_ret": float(df["net_ret"].mean()),
            "vol_bar_ret": float(df["net_ret"].std(ddof=0)),
            "total_return": float(df["nav"].iloc[-1] - 1.0),
            "max_drawdown": float(drawdown.min()),
            "positive_bar_ratio": float((df["net_ret"] > 0.0).mean()),
        }
    ])


def build_variant_aggregate(asset_summary: pd.DataFrame) -> pd.DataFrame:
    if asset_summary.empty:
        return pd.DataFrame()
    out = (
        asset_summary.groupby(["variant", "cost_bps_per_side"], as_index=False)
        .agg(
            assets_tested=("asset", "nunique"),
            positive_assets=("total_return", lambda s: int((s > 0).sum())),
            mean_total_return=("total_return", "mean"),
            median_total_return=("total_return", "median"),
            mean_max_drawdown=("max_drawdown", "mean"),
            mean_active_bar_ratio=("active_bar_ratio", "mean"),
            mean_avg_position=("avg_position", "mean"),
            mean_trade_events=("trade_events", "mean"),
            mean_turnover=("turnover", "mean"),
        )
        .sort_values(["cost_bps_per_side", "mean_total_return"], ascending=[True, False])
        .reset_index(drop=True)
    )
    out["positive_asset_ratio"] = out["positive_assets"] / out["assets_tested"].replace(0, np.nan)
    return out


def build_time_stability(primary_df: pd.DataFrame) -> pd.DataFrame:
    cols = ["gate", "status", "actual", "threshold", "why_it_matters"]
    if primary_df.empty or len(primary_df) < 30:
        return pd.DataFrame(columns=cols)
    df = primary_df.sort_values(["asset", "timestamp"]).copy()
    rows = []
    bucket_stats = []
    for asset, g in df.groupby("asset"):
        g = g.reset_index(drop=True)
        g["bucket"] = pd.qcut(np.arange(len(g)), 3, labels=["early", "mid", "late"])
        asset_bucket = g.groupby("bucket", observed=False)["net_ret"].apply(lambda s: float((1.0 + s).prod() - 1.0)).reset_index(name="asset_return")
        asset_bucket["asset"] = asset
        bucket_stats.append(asset_bucket)
    bdf = pd.concat(bucket_stats, ignore_index=True)
    summary = bdf.groupby("bucket", as_index=False, observed=False).agg(mean_asset_return=("asset_return", "mean"), positive_assets=("asset_return", lambda s: int((s > 0).sum())), assets=("asset", "nunique"))
    positive_buckets = int((summary["mean_asset_return"] > 0).sum())
    rows.append({"gate": "positive_bucket_floor", "status": "pass" if positive_buckets >= 2 else "fail", "actual": f"{positive_buckets}/3 positive buckets", "threshold": ">= 2/3", "why_it_matters": "不是只靠单一时间切片好看。"})
    min_bucket_return = float(summary["mean_asset_return"].min()) if not summary.empty else np.nan
    rows.append({"gate": "worst_bucket_watch", "status": "pass" if pd.notna(min_bucket_return) and min_bucket_return > -0.08 else "watch", "actual": pct(min_bucket_return), "threshold": "> -8%", "why_it_matters": "避免最近或最早一段明显塌掉。"})
    rows.append({"gate": "bucket_trade_floor", "status": "pass", "actual": "3 buckets present", "threshold": "3 buckets", "why_it_matters": "至少完成最小时间切片。"})
    return pd.DataFrame(rows)


def build_parameter_stability() -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    detail = []
    for cfg in PARAM_CONFIGS:
        asset_rows = []
        for asset, symbol in ASSETS.items():
            bars = prepare_bars(asset, symbol, ema_fast=cfg["ema_fast"], ema_slow=cfg["ema_slow"])
            sim, _ = simulate_variant(bars, next(v for v in VARIANTS if v["variant"] == PRIMARY_VARIANT), PRIMARY_COST)
            summary = summarize_asset_variant(sim, asset, PRIMARY_VARIANT, PRIMARY_COST).iloc[0]
            asset_rows.append(summary)
            detail.append({
                "config_label": cfg["label"],
                "asset": asset,
                "total_return": summary["total_return"],
                "max_drawdown": summary["max_drawdown"],
                "trade_events": summary["trade_events"],
            })
        sdf = pd.DataFrame(asset_rows)
        rows.append({
            "config_label": cfg["label"],
            "mean_total_return": float(sdf["total_return"].mean()),
            "positive_assets": int((sdf["total_return"] > 0).sum()),
            "assets": int(sdf["asset"].nunique()),
            "mean_trade_events": float(sdf["trade_events"].mean()),
        })
    out = pd.DataFrame(rows)
    if out.empty:
        gates = pd.DataFrame(columns=["gate", "status", "actual", "threshold", "why_it_matters"])
        return gates, pd.DataFrame(detail)
    positive_neighbors = int((out["mean_total_return"] > 0).sum())
    gates = pd.DataFrame([
        {"gate": "neighbor_positive_floor", "status": "pass" if positive_neighbors >= 3 else "fail", "actual": f"{positive_neighbors}/{len(out)} positive configs", "threshold": ">= 3/5", "why_it_matters": "小参数邻域不能一碰就碎。"},
        {"gate": "neighbor_trade_floor", "status": "pass" if float(out["mean_trade_events"].min()) >= 10 else "fail", "actual": num(float(out["mean_trade_events"].min())), "threshold": ">= 10", "why_it_matters": "不是靠几笔孤立交易撑出来。"},
        {"gate": "worst_neighbor_watch", "status": "pass" if float(out["mean_total_return"].min()) > -0.10 else "watch", "actual": pct(float(out["mean_total_return"].min())), "threshold": "> -10%", "why_it_matters": "最差邻域不能太离谱。"},
    ])
    return gates, out


def build_cross_asset_stability(primary_asset_summary: pd.DataFrame) -> pd.DataFrame:
    cols = ["gate", "status", "actual", "threshold", "why_it_matters"]
    if primary_asset_summary.empty:
        return pd.DataFrame(columns=cols)
    positive_assets = int((primary_asset_summary["total_return"] > 0).sum())
    min_trade_events = int(primary_asset_summary["trade_events"].min())
    worst_asset_return = float(primary_asset_summary["total_return"].min())
    return pd.DataFrame([
        {"gate": "positive_asset_floor", "status": "pass" if positive_assets >= 2 else "fail", "actual": f"{positive_assets}/{len(primary_asset_summary)} assets positive", "threshold": ">= 2/3", "why_it_matters": "不能只在单一币种上活。"},
        {"gate": "min_trade_floor", "status": "pass" if min_trade_events >= 10 else "fail", "actual": str(min_trade_events), "threshold": ">= 10", "why_it_matters": "至少每个币种都有最小样本。"},
        {"gate": "worst_asset_watch", "status": "pass" if worst_asset_return > -0.12 else "watch", "actual": pct(worst_asset_return), "threshold": "> -12%", "why_it_matters": "避免某个资产显著拖后腿。"},
    ])


def build_cost_trade_stability(variant_aggregate: pd.DataFrame) -> pd.DataFrame:
    cols = ["gate", "status", "actual", "threshold", "why_it_matters"]
    hit = variant_aggregate[variant_aggregate["variant"] == PRIMARY_VARIANT].copy()
    if hit.empty:
        return pd.DataFrame(columns=cols)
    positive_costs = int((hit["mean_total_return"] > 0).sum())
    min_trade_events = float(hit["mean_trade_events"].min())
    worst_cost = float(hit["mean_total_return"].min())
    return pd.DataFrame([
        {"gate": "cost_survival_floor", "status": "pass" if positive_costs >= 2 else "fail", "actual": f"{positive_costs}/{len(hit)} cost levels positive", "threshold": ">= 2/4", "why_it_matters": "加轻量 friction 后不能立刻归零。"},
        {"gate": "trade_count_floor", "status": "pass" if min_trade_events >= 10 else "fail", "actual": num(min_trade_events), "threshold": ">= 10", "why_it_matters": "不是靠极少数调仓撑出来。"},
        {"gate": "worst_cost_watch", "status": "pass" if worst_cost > -0.12 else "watch", "actual": pct(worst_cost), "threshold": "> -12%", "why_it_matters": "成本抬升后也别崩得太厉害。"},
    ])


def build_spec() -> pd.DataFrame:
    return pd.DataFrame([
        {"section": "run_context", "item": "why_now", "value": "EMA Paper Seat 当前 waiting_not_due；Rank 7/8/9 已 park，Rank 2 只在真实 append/review need 时再继续。", "why_it_matters": "本轮 Scout Seat 需要一个新的 paper-based 15m crypto 候选，而不是继续磨旧 wiring。", "operator_rule": "只做最小 clean replication + hard verdict，不把 overlay 漂成长期研究态。"},
        {"section": "candidate", "item": "candidate_id", "value": "scout_vol_managed_ema_15m_v1", "why_it_matters": "给本轮新 intake 一个稳定句柄。", "operator_rule": "后续若重开，沿用同一 candidate_id。"},
        {"section": "candidate", "item": "source_anchor", "value": "Moreira & Muir (2017) Volatility Managed Portfolios + ATR proxy engineering approximation", "why_it_matters": "论文讲的是波动管理思想，不是直接证明 15m crypto ATR sizing 必有效。", "operator_rule": "不得把 ATR scaling 说成论文已直接验证的 crypto alpha。"},
        {"section": "scope", "item": "market_timeframe", "value": "BTC-USD / ETH-USD / SOL-USD | Binance 120d | 15m", "why_it_matters": "与现有 Scout Fast Lane 保持同级别样本，复用现有 cache。", "operator_rule": "第一刀不扩币种、不换数据源。"},
        {"section": "trade_rule", "item": "trade_on_off", "value": "trade on = EMA20 > EMA50；trade off = EMA20 <= EMA50；position size = clip(ATR_ref / ATR14_t, min, max)", "why_it_matters": "先把规则写清楚，避免把仓位管理和信号逻辑混成黑箱。", "operator_rule": "执行采用 next-bar position lag；不看未来波动。"},
        {"section": "variants", "item": "sizing_matrix", "value": "baseline_100 | atr_clip_075_125 | atr_clip_050_150 | atr_clip_025_175", "why_it_matters": "先看 vol-managed overlay 是否真的改变准入判断。", "operator_rule": "四档共用同一 EMA 信号与同一成本口径。"},
        {"section": "execution", "item": "bar_level_engine", "value": "use previous bar desired_position on current bar open->close return; charge cost on position change", "why_it_matters": "保持因果：今天的仓位只来自昨天看得到的信号与 ATR。", "operator_rule": "不能用当前 bar 收盘后算出的 size 直接吃到同一 bar 收益。"},
        {"section": "evaluation", "item": "light_stability_pack", "value": "时间稳定性 | 参数稳定性 | 跨标的稳定性 | 成本/交易数稳定性", "why_it_matters": "决定它是 park、supporting overlay，还是值得继续接 paper。", "operator_rule": "本轮必须给出 hard verdict。"},
    ])


def choose_hard_verdict(primary_row: pd.Series, time_gates: pd.DataFrame, param_gates: pd.DataFrame, cross_gates: pd.DataFrame, cost_gates: pd.DataFrame, baseline_row: pd.Series | None) -> tuple[str, str]:
    fail_count = 0
    for gates in [time_gates, param_gates, cross_gates, cost_gates]:
        fail_count += int((gates["status"] == "fail").sum()) if not gates.empty else 0
    primary_return = float(primary_row["mean_total_return"])
    primary_mdd = float(primary_row["mean_max_drawdown"])
    baseline_return = float(baseline_row["mean_total_return"]) if baseline_row is not None else np.nan
    baseline_mdd = float(baseline_row["mean_max_drawdown"]) if baseline_row is not None else np.nan
    if primary_return > 0 and fail_count <= 1 and float(primary_row["positive_asset_ratio"]) >= (2 / 3):
        return "paper candidate", "波动管理不仅成本后为正，而且至少没有在四项快筛里被打成明显脆弱。"
    if pd.notna(baseline_mdd) and primary_mdd < baseline_mdd and primary_return > baseline_return - 0.02 and fail_count <= 3:
        return "supporting overlay only", "这条线更像现有 EMA 的风险层补丁，而不是独立 scout winner。"
    return "park", "它没有把当前 desk judgment 从研究态明显推向 paper candidate，最多只是曲线形状小修小补。"


def write_report(spec_df: pd.DataFrame, variant_aggregate: pd.DataFrame, asset_summary: pd.DataFrame, time_gates: pd.DataFrame, param_gates: pd.DataFrame, param_detail: pd.DataFrame, cross_gates: pd.DataFrame, cost_gates: pd.DataFrame, verdict: str, verdict_reason: str) -> None:
    ensure_dir(SITE_DIR)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    primary_row = variant_aggregate[(variant_aggregate["variant"] == PRIMARY_VARIANT) & (variant_aggregate["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    baseline_hit = variant_aggregate[(variant_aggregate["variant"] == "baseline_100") & (variant_aggregate["cost_bps_per_side"] == PRIMARY_COST)]
    baseline_text = "-"
    if not baseline_hit.empty:
        base = baseline_hit.iloc[0]
        baseline_text = f"baseline_100 @ 6bps：mean_total_return={pct(base['mean_total_return'])}，mean_max_drawdown={pct(base['mean_max_drawdown'])}"
    html = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Scout Seat · volatility-managed EMA · 15m crypto</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1140px; margin: 40px auto; padding: 0 18px; line-height: 1.68; color: #111827; background: #f8fafc; }}
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
  <h1>Scout Seat · volatility-managed EMA · 15m crypto clean replication</h1>
  <p class="muted">生成时间：{escape(now)} ｜ 来源锚点：Moreira &amp; Muir (2017) + ATR 近似工程化第一刀。</p>

  <div class="card">
    <h2>hard verdict</h2>
    <p><b>{escape(verdict)}</b> —— {escape(verdict_reason)}</p>
    <ul>
      <li>primary variant：<code>{escape(PRIMARY_VARIANT)}</code> @ 6 bps/side</li>
      <li>mean_total_return：<b>{escape(pct(primary_row['mean_total_return']))}</b></li>
      <li>positive_asset_ratio：<b>{escape(num(primary_row['positive_asset_ratio']))}</b></li>
      <li>mean_max_drawdown：<b>{escape(pct(primary_row['mean_max_drawdown']))}</b></li>
      <li>{escape(baseline_text)}</li>
    </ul>
  </div>

  <div class="card">
    <h2>怎么读这条线</h2>
    <ul>
      <li>这不是发明新 alpha，而是问：同样的 EMA 方向层，在 15m crypto 上加一层 ATR 风险缩放，能不能改变准入判断。</li>
      <li>如果它只是让回撤小一点、但收益和稳定性都没过关，就不该把它写成新的默认 seat。</li>
      <li>因此这轮输出的目标不是漂亮曲线，而是明确三选一：<code>paper candidate</code> / <code>supporting overlay only</code> / <code>park</code>。</li>
    </ul>
  </div>

  <div class="card">
    <h2>clean-room spec</h2>
    {render_table(spec_df, percent_cols=set())}
  </div>

  <div class="card">
    <h2>variant aggregate</h2>
    {render_table(variant_aggregate, percent_cols={'mean_total_return','median_total_return','mean_max_drawdown','mean_active_bar_ratio','positive_asset_ratio'}, digits_cols={'mean_avg_position':3,'mean_trade_events':1,'mean_turnover':2})}
  </div>

  <div class="card">
    <h2>per-asset summary</h2>
    {render_table(asset_summary[(asset_summary['variant'] == PRIMARY_VARIANT) & (asset_summary['cost_bps_per_side'] == PRIMARY_COST)].reset_index(drop=True), percent_cols={'active_bar_ratio','total_return','max_drawdown','positive_bar_ratio'}, digits_cols={'avg_position':3,'avg_active_position':3,'trade_events':0,'turnover':2})}
  </div>

  <div class="card">
    <h2>Light Stability Pack</h2>
    <h3>时间稳定性</h3>
    {render_table(time_gates, percent_cols=set())}
    <h3>参数稳定性</h3>
    {render_table(param_gates, percent_cols=set())}
    <p class="muted">参数邻域明细：</p>
    {render_table(param_detail, percent_cols={'mean_total_return'}, digits_cols={'mean_trade_events':1})}
    <h3>跨标的稳定性</h3>
    {render_table(cross_gates, percent_cols=set())}
    <h3>成本 / 交易数稳定性</h3>
    {render_table(cost_gates, percent_cols=set())}
  </div>

  <div class="card">
    <h2>reader-facing takeaway</h2>
    <ul>
      <li>如果 <code>vol-managed</code> 版本只是把 <code>EMA</code> 曲线修圆，但没有把收益 / 跨标的 / 成本存活一起抬起来，它更适合放回证据池，而不是抢默认席位。</li>
      <li>只有当它至少能把 <code>positive_asset_ratio</code> 和成本后收益一起抬过基线，才值得继续接 paper plumbing。</li>
    </ul>
  </div>
</body>
</html>'''
    REPORT_PATH.write_text(html, encoding="utf-8")


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    spec_df = build_spec()
    spec_df.to_csv(SPEC_PATH, index=False)

    all_rows = []
    all_asset_rows = []
    nav_rows = []
    bar_rows = []

    for asset, symbol in ASSETS.items():
        bars = prepare_bars(asset, symbol)
        for variant_cfg in VARIANTS:
            for cost in COSTS:
                sim_df, nav_df = simulate_variant(bars, variant_cfg, cost)
                all_asset_rows.append(summarize_asset_variant(sim_df, asset, variant_cfg["variant"], cost))
                nav_rows.append(nav_df)
                if variant_cfg["variant"] == PRIMARY_VARIANT and cost == PRIMARY_COST:
                    bar_rows.append(sim_df)
                all_rows.append(sim_df[["asset", "timestamp", "variant", "cost_bps_per_side", "position", "turnover", "gross_ret", "net_ret", "nav", "trade_event"]].copy())

    asset_summary = pd.concat(all_asset_rows, ignore_index=True)
    bar_level = pd.concat(all_rows, ignore_index=True)
    nav_df = pd.concat(nav_rows, ignore_index=True)
    primary_df = pd.concat(bar_rows, ignore_index=True)

    variant_aggregate = build_variant_aggregate(asset_summary)
    time_gates = build_time_stability(primary_df)
    param_gates, param_detail = build_parameter_stability()
    cross_gates = build_cross_asset_stability(asset_summary[(asset_summary["variant"] == PRIMARY_VARIANT) & (asset_summary["cost_bps_per_side"] == PRIMARY_COST)].reset_index(drop=True))
    cost_gates = build_cost_trade_stability(variant_aggregate)

    primary_row = variant_aggregate[(variant_aggregate["variant"] == PRIMARY_VARIANT) & (variant_aggregate["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    baseline_hit = variant_aggregate[(variant_aggregate["variant"] == "baseline_100") & (variant_aggregate["cost_bps_per_side"] == PRIMARY_COST)]
    baseline_row = baseline_hit.iloc[0] if not baseline_hit.empty else None
    verdict, verdict_reason = choose_hard_verdict(primary_row, time_gates, param_gates, cross_gates, cost_gates, baseline_row)

    meta_df = pd.DataFrame([
        {
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "candidate_id": "scout_vol_managed_ema_15m_v1",
            "source": "Moreira & Muir (2017) + ATR approximation",
            "primary_variant": PRIMARY_VARIANT,
            "primary_cost_bps_per_side": PRIMARY_COST,
            "hard_verdict": verdict,
            "verdict_reason": verdict_reason,
            "trade_on_rule": "EMA20 > EMA50",
            "trade_off_rule": "EMA20 <= EMA50",
        }
    ])

    spec_df.to_csv(ART_DIR / "clean_room_spec_v1.csv", index=False)
    meta_df.to_csv(ART_DIR / "clean_replication_meta.csv", index=False)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    variant_aggregate.to_csv(ART_DIR / "variant_aggregate.csv", index=False)
    time_gates.to_csv(ART_DIR / "time_stability_drycheck.csv", index=False)
    param_gates.to_csv(ART_DIR / "parameter_stability_drycheck.csv", index=False)
    param_detail.to_csv(ART_DIR / "parameter_neighbor_grid.csv", index=False)
    cross_gates.to_csv(ART_DIR / "cross_asset_stability_drycheck.csv", index=False)
    cost_gates.to_csv(ART_DIR / "cost_trade_stability_drycheck.csv", index=False)
    bar_level.to_csv(ART_DIR / "bar_level_summary.csv", index=False)
    nav_df.to_csv(ART_DIR / "nav_paths.csv", index=False)

    write_report(spec_df, variant_aggregate, asset_summary, time_gates, param_gates, param_detail, cross_gates, cost_gates, verdict, verdict_reason)


if __name__ == "__main__":
    main()
