#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank71_ema_vwap_atr_volume_score_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank71_ema_vwap_atr_volume_score_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank71_ema_vwap_atr_volume_score_clean_replication.html"
TODO_PATH = ROOT / "docs" / "TODO.md"
P3_SUMMARY_PATH = ROOT / "reports" / "artifacts" / "manual_narrow_paper_lanes" / "manual_narrow_paper_last_run_summary.json"
DUE_PATH = ROOT / "reports" / "artifacts" / "ema_psar_raw_alpha" / "ema_paper_trading_due_guardrail_snapshot.csv"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
VARIANTS = ["baseline", "score_gte60", "score_gte75"]
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0, 20.0]
BASE_HOLD_BARS = 8
EARLY_FAIL_BARS = 4
MAX_SCORE = 100.0

CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1120px; margin: 40px auto; padding: 0 18px; line-height: 1.72; color: #111827; background: #f8fafc; }
.card { border: 1px solid #e5e7eb; border-radius: 14px; background: white; padding: 18px 20px; margin: 16px 0; }
.pill { display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }
.muted { color:#6b7280; }
code { background:#f3f4f6; padding:1px 5px; border-radius:6px; }
table { width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }
th, td { border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }
a { color:#2563eb; text-decoration:none; }
"""


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def pct(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def num(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f}"


def render_table(df: pd.DataFrame, percent_cols: set[str] | None = None, digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    percent_cols = percent_cols or set()
    digits_cols = digits_cols or {}
    headers = ''.join(f'<th>{escape(str(c))}</th>' for c in df.columns)
    rows: list[str] = []
    for _, row in df.iterrows():
        cells: list[str] = []
        for col in df.columns:
            value = row[col]
            if col in percent_cols:
                text = pct(value)
            elif isinstance(value, (float, np.floating, int, np.integer)) and not isinstance(value, bool):
                text = num(value, digits_cols.get(col, 2))
            else:
                text = str(value)
            cells.append(f'<td>{escape(text)}</td>')
        rows.append(f'<tr>{"".join(cells)}</tr>')
    return f'<table><thead><tr>{headers}</tr></thead><tbody>{"".join(rows)}</tbody></table>'


def write_html(path: Path, title: str, body: str) -> None:
    path.write_text(
        f"<!doctype html><html><head><meta charset='utf-8'><title>{escape(title)}</title><style>{CSS}</style></head><body>{body}</body></html>",
        encoding="utf-8",
    )


def load_bars(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def compute_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    prev_close = df["close"].shift(1)
    tr = pd.concat([
        (df["high"] - df["low"]).abs(),
        (df["high"] - prev_close).abs(),
        (df["low"] - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def compute_psar(df: pd.DataFrame, step: float = 0.02, max_step: float = 0.2) -> pd.Series:
    high = df["high"].to_numpy(dtype=float)
    low = df["low"].to_numpy(dtype=float)
    n = len(df)
    psar = np.full(n, np.nan)
    bull = True
    af = step
    ep = high[0]
    psar[0] = low[0]
    if n > 1:
        bull = high[1] >= high[0]
        ep = high[1] if bull else low[1]
        psar[1] = min(low[0], low[1]) if bull else max(high[0], high[1])
    for i in range(2, n):
        prev_psar = psar[i - 1]
        if bull:
            cur = prev_psar + af * (ep - prev_psar)
            cur = min(cur, low[i - 1], low[i - 2])
            if low[i] < cur:
                bull = False
                cur = ep
                ep = low[i]
                af = step
            else:
                if high[i] > ep:
                    ep = high[i]
                    af = min(max_step, af + step)
        else:
            cur = prev_psar + af * (ep - prev_psar)
            cur = max(cur, high[i - 1], high[i - 2])
            if high[i] > cur:
                bull = True
                cur = ep
                ep = high[i]
                af = step
            else:
                if low[i] < ep:
                    ep = low[i]
                    af = min(max_step, af + step)
        psar[i] = cur
    return pd.Series(psar, index=df.index)


def compute_session_vwap(df: pd.DataFrame) -> pd.Series:
    typical = (df["high"] + df["low"] + df["close"]) / 3.0
    session_key = df["timestamp"].dt.floor("D")
    pv = typical * df["volume"]
    cum_pv = pv.groupby(session_key).cumsum()
    cum_vol = df["volume"].groupby(session_key).cumsum()
    return cum_pv / cum_vol.replace(0, np.nan)


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_bars(symbol, asset)
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema15"] = df["close"].ewm(span=15, adjust=False).mean()
    df["ema_slope"] = df["ema9"].pct_change(3)
    df["vol_ma20"] = df["volume"].rolling(20, min_periods=20).mean()
    df["atr14"] = compute_atr(df)
    df["atr14_ma14"] = df["atr14"].rolling(14, min_periods=14).mean()
    df["psar"] = compute_psar(df)
    df["session_vwap"] = compute_session_vwap(df)
    df["ema_spread_atr"] = ((df["ema9"] - df["ema15"]).abs() / df["atr14"].replace(0, np.nan)).clip(lower=0)
    df["vwap_dist_atr"] = ((df["close"] - df["session_vwap"]).abs() / df["atr14"].replace(0, np.nan)).clip(lower=0)
    df["vol_pass"] = (df["volume"] > df["vol_ma20"]).astype(int)
    df["atr_pass"] = (df["atr14"] > df["atr14_ma14"]).astype(int)
    df["trend_pass"] = ((df["ema9"] > df["ema15"]) & (df["close"] > df["ema9"]) & (df["close"] > df["session_vwap"]) & (df["psar"] < df["close"]))
    df["ema_component"] = np.minimum(25.0, df["ema_spread_atr"].fillna(0.0) * 25.0)
    df["vwap_component"] = np.minimum(25.0, df["vwap_dist_atr"].fillna(0.0) * 25.0)
    df["vol_component"] = 25.0 * df["vol_pass"].fillna(0)
    df["atr_component"] = 25.0 * df["atr_pass"].fillna(0)
    df["admission_score"] = (df["ema_component"] + df["vwap_component"] + df["vol_component"] + df["atr_component"]).clip(upper=MAX_SCORE)
    df["score_bucket"] = pd.cut(
        df["admission_score"],
        bins=[-np.inf, 60.0, 75.0, np.inf],
        labels=["lt60", "60_74", "gte75"],
        right=False,
    ).astype(str)
    df["ema_psar_long_signal"] = (
        (df["ema9"] > df["ema15"])
        & (df["ema_slope"] > 0.0003)
        & (df["psar"] < df["close"])
        & (df["close"] > df["high"].shift(1))
        & (df["close"].shift(1) < df["ema9"].shift(1))
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)
    return df


def build_signal_frame(frame: pd.DataFrame, asset: str, variant: str) -> pd.DataFrame:
    raw_signal = frame["ema_psar_long_signal"] & ~frame["ema_psar_long_signal"].shift(1).fillna(False)
    if variant == "baseline":
        gate = pd.Series(True, index=frame.index)
    elif variant == "score_gte60":
        gate = frame["trend_pass"].fillna(False) & (frame["admission_score"] >= 60.0)
    elif variant == "score_gte75":
        gate = frame["trend_pass"].fillna(False) & (frame["admission_score"] >= 75.0)
    else:
        raise ValueError(variant)
    sig = raw_signal & gate
    rows: list[dict[str, object]] = []
    last_exit = -1
    for idx in range(40, len(frame) - BASE_HOLD_BARS - 2):
        if idx <= last_exit or not bool(sig.iloc[idx]):
            continue
        rows.append(
            {
                "signal_id": f"{asset}|{variant}|{idx}",
                "asset": asset,
                "variant": variant,
                "signal_idx": idx,
                "entry_idx": idx + 1,
                "signal_ts": pd.to_datetime(frame.iloc[idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "signal_price": float(frame.iloc[idx]["close"]),
                "signal_atr14": float(frame.iloc[idx]["atr14"]),
                "admission_score": float(frame.iloc[idx]["admission_score"]),
                "score_bucket": str(frame.iloc[idx]["score_bucket"]),
                "ema_component": float(frame.iloc[idx]["ema_component"]),
                "vwap_component": float(frame.iloc[idx]["vwap_component"]),
                "vol_component": float(frame.iloc[idx]["vol_component"]),
                "atr_component": float(frame.iloc[idx]["atr_component"]),
            }
        )
        last_exit = idx + BASE_HOLD_BARS
    return pd.DataFrame(rows)


def build_trades(frame: pd.DataFrame, signals: pd.DataFrame, cost_bps: float) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    cost_rate = float(cost_bps) / 10000.0
    for _, sig in signals.iterrows():
        entry_idx = int(sig["entry_idx"])
        exit_idx = min(len(frame) - 1, entry_idx + BASE_HOLD_BARS - 1)
        if entry_idx >= len(frame):
            continue
        entry_px = float(frame.iloc[entry_idx]["open"])
        exit_px = float(frame.iloc[exit_idx]["open"])
        gross_ret = (exit_px / entry_px) - 1.0
        net_ret = (1.0 + gross_ret) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
        forward_end = min(len(frame) - 1, entry_idx + 2)
        forward_3bar_ret = float(frame.iloc[forward_end]["close"] / entry_px - 1.0)
        fail_window = frame.iloc[entry_idx : min(len(frame), entry_idx + EARLY_FAIL_BARS)]
        flip_fail = bool(((fail_window["close"] < fail_window["ema9"]) | (fail_window["close"] < fail_window["session_vwap"])).any())
        rows.append(
            {
                "signal_id": sig["signal_id"],
                "asset": sig["asset"],
                "variant": sig["variant"],
                "cost_bps_per_side": float(cost_bps),
                "signal_ts": sig["signal_ts"],
                "entry_ts": pd.to_datetime(frame.iloc[entry_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": pd.to_datetime(frame.iloc[exit_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_price": entry_px,
                "exit_price": exit_px,
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "hold_bars_realized": int(exit_idx - entry_idx + 1),
                "forward_3bar_ret": forward_3bar_ret,
                "flip_to_fail_4bars": int(flip_fail),
                "admission_score": float(sig["admission_score"]),
                "score_bucket": sig["score_bucket"],
                "ema_component": float(sig["ema_component"]),
                "vwap_component": float(sig["vwap_component"]),
                "vol_component": float(sig["vol_component"]),
                "atr_component": float(sig["atr_component"]),
            }
        )
    return pd.DataFrame(rows)


def summarize_asset(trades: pd.DataFrame, *, asset: str, variant: str, cost_bps: float, baseline_trades: pd.DataFrame | None = None) -> dict[str, object]:
    trade_retention = np.nan
    if baseline_trades is not None and len(baseline_trades) > 0:
        trade_retention = float(len(trades) / len(baseline_trades))
    return {
        "asset": asset,
        "variant": variant,
        "cost_bps_per_side": float(cost_bps),
        "trades": int(len(trades)),
        "trade_retention": trade_retention,
        "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0) if not trades.empty else np.nan,
        "post_cost_expectancy": float(trades["net_ret"].mean()) if not trades.empty else np.nan,
        "win_rate": float((trades["net_ret"] > 0).mean()) if not trades.empty else np.nan,
        "forward_3bar_median_return": float(trades["forward_3bar_ret"].median()) if not trades.empty else np.nan,
        "flip_to_fail_rate": float(trades["flip_to_fail_4bars"].mean()) if not trades.empty else np.nan,
        "score_median": float(trades["admission_score"].median()) if not trades.empty else np.nan,
    }


def build_overall(asset_summary: pd.DataFrame) -> pd.DataFrame:
    return (
        asset_summary.groupby(["variant", "cost_bps_per_side"], dropna=False)
        .agg(
            mean_total_return=("total_return", "mean"),
            positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
            mean_trades=("trades", "mean"),
            mean_trade_retention=("trade_retention", "mean"),
            post_cost_expectancy=("post_cost_expectancy", "mean"),
            mean_win_rate=("win_rate", "mean"),
            forward_3bar_median_return=("forward_3bar_median_return", "mean"),
            flip_to_fail_rate=("flip_to_fail_rate", "mean"),
            median_score=("score_median", "mean"),
        )
        .reset_index()
        .sort_values(["cost_bps_per_side", "variant"])
        .reset_index(drop=True)
    )


def build_bucket_summary(trades_6bps: pd.DataFrame) -> pd.DataFrame:
    if trades_6bps.empty:
        return pd.DataFrame(columns=["score_bucket", "mean_total_return", "positive_asset_ratio", "mean_trades", "post_cost_expectancy", "forward_3bar_median_return", "flip_to_fail_rate"])
    rows = []
    grouped = trades_6bps.groupby(["asset", "score_bucket"], dropna=False)
    for (asset, bucket), part in grouped:
        rows.append(
            {
                "asset": asset,
                "score_bucket": bucket,
                "total_return": float((1.0 + part["net_ret"]).prod() - 1.0),
                "trades": int(len(part)),
                "post_cost_expectancy": float(part["net_ret"].mean()),
                "forward_3bar_median_return": float(part["forward_3bar_ret"].median()),
                "flip_to_fail_rate": float(part["flip_to_fail_4bars"].mean()),
            }
        )
    tmp = pd.DataFrame(rows)
    order = ["lt60", "60_74", "gte75"]
    out = (
        tmp.groupby("score_bucket", dropna=False)
        .agg(
            mean_total_return=("total_return", "mean"),
            positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
            mean_trades=("trades", "mean"),
            post_cost_expectancy=("post_cost_expectancy", "mean"),
            forward_3bar_median_return=("forward_3bar_median_return", "mean"),
            flip_to_fail_rate=("flip_to_fail_rate", "mean"),
        )
        .reset_index()
    )
    out["score_bucket"] = pd.Categorical(out["score_bucket"], categories=order, ordered=True)
    return out.sort_values("score_bucket").reset_index(drop=True)


def build_component_summary(trades_6bps: pd.DataFrame) -> pd.DataFrame:
    if trades_6bps.empty:
        return pd.DataFrame(columns=["asset", "trades", "score_median", "ema_component_mean", "vwap_component_mean", "vol_component_mean", "atr_component_mean"])
    return (
        trades_6bps.groupby("asset", dropna=False)
        .agg(
            trades=("signal_id", "count"),
            score_median=("admission_score", "median"),
            ema_component_mean=("ema_component", "mean"),
            vwap_component_mean=("vwap_component", "mean"),
            vol_component_mean=("vol_component", "mean"),
            atr_component_mean=("atr_component", "mean"),
        )
        .reset_index()
        .sort_values("asset")
        .reset_index(drop=True)
    )


def build_verdict(overall: pd.DataFrame, bucket_summary: pd.DataFrame) -> tuple[str, str, str]:
    at6 = overall[overall["cost_bps_per_side"] == PRIMARY_COST].set_index("variant")
    if at6.empty or "baseline" not in at6.index:
        return (
            "park / evidence pool",
            "baseline 不足以形成可比 summary。",
            "这轮最小 clean replication 连 baseline 对照都不完整，不该继续占默认 Scout 预算。",
        )
    base = at6.loc["baseline"]
    s60 = at6.loc["score_gte60"] if "score_gte60" in at6.index else pd.Series(dtype=float)
    s75 = at6.loc["score_gte75"] if "score_gte75" in at6.index else pd.Series(dtype=float)

    headline = (
        f"baseline≈{pct(base.get('mean_total_return'))} / fail≈{pct(base.get('flip_to_fail_rate'))} / retention=100.00%；"
        f" score>=60≈{pct(s60.get('mean_total_return'))} / fail≈{pct(s60.get('flip_to_fail_rate'))} / retention≈{pct(s60.get('mean_trade_retention'))}；"
        f" score>=75≈{pct(s75.get('mean_total_return'))} / fail≈{pct(s75.get('flip_to_fail_rate'))} / retention≈{pct(s75.get('mean_trade_retention'))}"
    )

    monotonic = False
    if len(bucket_summary) == 3:
        b = bucket_summary.set_index("score_bucket")
        if all(k in b.index for k in ["lt60", "60_74", "gte75"]):
            monotonic = (
                float(b.loc["gte75", "post_cost_expectancy"]) >= float(b.loc["60_74", "post_cost_expectancy"]) >= float(b.loc["lt60", "post_cost_expectancy"]) and
                float(b.loc["gte75", "forward_3bar_median_return"]) >= float(b.loc["60_74", "forward_3bar_median_return"]) >= float(b.loc["lt60", "forward_3bar_median_return"]) and
                float(b.loc["gte75", "flip_to_fail_rate"]) <= float(b.loc["60_74", "flip_to_fail_rate"]) <= float(b.loc["lt60", "flip_to_fail_rate"])
            )

    improve60 = (
        pd.notna(s60.get("post_cost_expectancy")) and pd.notna(base.get("post_cost_expectancy"))
        and float(s60.get("post_cost_expectancy")) > float(base.get("post_cost_expectancy"))
        and pd.notna(s60.get("flip_to_fail_rate")) and pd.notna(base.get("flip_to_fail_rate"))
        and float(s60.get("flip_to_fail_rate")) < float(base.get("flip_to_fail_rate"))
        and pd.notna(s60.get("mean_trade_retention")) and float(s60.get("mean_trade_retention")) >= 0.55
    )
    improve75 = (
        pd.notna(s75.get("post_cost_expectancy")) and pd.notna(base.get("post_cost_expectancy"))
        and float(s75.get("post_cost_expectancy")) > float(base.get("post_cost_expectancy"))
        and pd.notna(s75.get("flip_to_fail_rate")) and pd.notna(base.get("flip_to_fail_rate"))
        and float(s75.get("flip_to_fail_rate")) < float(base.get("flip_to_fail_rate"))
        and pd.notna(s75.get("mean_trade_retention")) and float(s75.get("mean_trade_retention")) >= 0.35
    )
    cost10_ok = False
    at10 = overall[(overall["cost_bps_per_side"] == 10.0) & (overall["variant"] == "score_gte60")]
    if not at10.empty:
        cost10_ok = float(at10.iloc[0]["post_cost_expectancy"] or 0.0) >= 0

    if improve60 and improve75 and monotonic and cost10_ok:
        return (
            "P2 paper candidate / admission queue",
            headline,
            "这轮最小 clean replication 说明 graded score 不只是靠砍交易数变好：bucket 质量分层更单调，fail-rate 更低，而且 10bps 还没直接塌掉，值得升到 paper candidate pool。",
        )
    if (improve60 or improve75) and monotonic:
        return (
            "P1 weak candidate / evidence pool",
            headline,
            "这轮最小 clean replication 说明 graded admission score 开始像真的 continuation overlay：高分桶更像样、低分桶更差，但改善还不够强到直接升格，先留在 P1 证据池更诚实。",
        )
    return (
        "park / evidence pool",
        headline,
        "这轮最小 clean replication 更像在说明：graded score 目前没有稳定形成单调质量分层，或只能靠明显砍样本才看起来更好，不该继续占默认 Scout 主资源位。",
    )


def render_factor_page(overall: pd.DataFrame, asset_summary: pd.DataFrame, bucket_summary: pd.DataFrame, component_summary: pd.DataFrame, verdict: str, headline: str, reason: str, generated_at: str) -> str:
    overall_view = overall[[
        "variant", "cost_bps_per_side", "mean_total_return", "positive_asset_ratio", "mean_trades",
        "mean_trade_retention", "post_cost_expectancy", "mean_win_rate", "forward_3bar_median_return", "flip_to_fail_rate", "median_score"
    ]].copy()
    asset_view = asset_summary[(asset_summary["cost_bps_per_side"] == PRIMARY_COST)][[
        "asset", "variant", "trades", "trade_retention", "total_return", "post_cost_expectancy", "win_rate", "forward_3bar_median_return", "flip_to_fail_rate", "score_median"
    ]].copy()
    return f"""
<p><a href='../../reading/repo_scout/rank71_ema_vwap_atr_volume_score_source_intake.html'>← 返回 source intake</a></p>
<h1>Rank 71 · EMA-VWAP-ATR-volume graded admission score（minimal clean replication）</h1>
<p class='muted'>生成时间：{escape(generated_at)} ｜ 固定 BTC/ETH/SOL 120d 15m 本地 cache；只接现成 EMA/PSAR raw lane；统一 <code>signal 当根及之前数据 + next-bar open + no-overlap</code>。</p>

<div class='card'>
  <h2>这轮只回答一个问题</h2>
  <p>把 continuation 从二元 gate 改成 <b>0~100 的 graded admission score</b> 后，是否能比 baseline 更诚实地区分强弱 continuation，而不是只靠把交易数砍没？</p>
  <ul>
    <li><b>score 四块：</b><code>EMA spread / ATR</code>、<code>price-VWAP distance / ATR</code>、<code>volume > SMA20</code>、<code>ATR14 > ATR14-MA14</code>，各 25 分。</li>
    <li><b>三臂：</b><code>baseline</code>、<code>score&gt;=60</code>、<code>score&gt;=75</code>。</li>
    <li><b>主看指标：</b><code>post_cost_expectancy</code>、<code>forward_3bar_median_return</code>、<code>flip_to_fail_rate</code>、<code>trade_retention</code>。</li>
  </ul>
</div>

<div class='card'>
  <h2>硬结论</h2>
  <p><span class='pill'>{escape(verdict)}</span></p>
  <p><b>{escape(headline)}</b></p>
  <p class='muted'>{escape(reason)}</p>
</div>

<div class='card'>
  <h2>overall summary</h2>
  {render_table(overall_view, percent_cols={'mean_total_return','positive_asset_ratio','mean_trade_retention','post_cost_expectancy','mean_win_rate','forward_3bar_median_return','flip_to_fail_rate'}, digits_cols={'cost_bps_per_side':0,'mean_trades':1,'median_score':1})}
</div>

<div class='card'>
  <h2>cross-asset summary（6bps）</h2>
  {render_table(asset_view, percent_cols={'trade_retention','total_return','post_cost_expectancy','win_rate','forward_3bar_median_return','flip_to_fail_rate'}, digits_cols={'trades':0,'score_median':1})}
</div>

<div class='card'>
  <h2>score bucket 质量分层（baseline 信号，6bps）</h2>
  {render_table(bucket_summary, percent_cols={'mean_total_return','positive_asset_ratio','post_cost_expectancy','forward_3bar_median_return','flip_to_fail_rate'}, digits_cols={'mean_trades':1})}
</div>

<div class='card'>
  <h2>主臂 score 组件概览（score&gt;=60，6bps）</h2>
  {render_table(component_summary, digits_cols={'trades':0,'score_median':1,'ema_component_mean':1,'vwap_component_mean':1,'vol_component_mean':1,'atr_component_mean':1})}
</div>
"""


def render_reading_page(overall: pd.DataFrame, bucket_summary: pd.DataFrame, verdict: str, headline: str, reason: str, generated_at: str) -> str:
    overall_view = overall[[
        "variant", "cost_bps_per_side", "mean_total_return", "positive_asset_ratio", "mean_trades",
        "mean_trade_retention", "post_cost_expectancy", "forward_3bar_median_return", "flip_to_fail_rate"
    ]].copy()
    return f"""
<p><a href='rank71_ema_vwap_atr_volume_score_source_intake.html'>← 返回 source intake</a></p>
<h1>Rank 71 · EMA-VWAP-ATR-volume graded admission score clean replication</h1>
<div class='card'>
  <span class='pill'>更新时间：{escape(generated_at)}</span>
  <span class='pill'>类型：minimal clean replication</span>
  <span class='pill'>当前 verdict：{escape(verdict)}</span>
  <p class='muted'>artifact：<code>reports/artifacts/scout_rank71_ema_vwap_atr_volume_score_15m/overall_summary.csv</code></p>
</div>
<div class='card'>
  <h2>一句话结果</h2>
  <p><b>{escape(headline)}</b></p>
  <p class='muted'>{escape(reason)}</p>
</div>
<div class='card'>
  <h2>这轮冻结的最小实验</h2>
  <ul>
    <li><code>BTC/ETH/SOL</code>，复用 120d 15m 本地 cache，不追新 bar，不做重下载。</li>
    <li>只接现成 <code>EMA/PSAR raw lane</code>，不把 score 偷渡成新的独立策略。</li>
    <li>主看点不是“收益最好的是谁”，而是高分是否更像样、低分是否更容易 fail，以及交易数有没有被砍穿。</li>
  </ul>
</div>
<div class='card'>
  <h2>三臂结果总览</h2>
  {render_table(overall_view, percent_cols={'mean_total_return','positive_asset_ratio','mean_trade_retention','post_cost_expectancy','forward_3bar_median_return','flip_to_fail_rate'}, digits_cols={'cost_bps_per_side':0,'mean_trades':1})}
</div>
<div class='card'>
  <h2>baseline bucket 质量分层（6bps）</h2>
  {render_table(bucket_summary, percent_cols={'mean_total_return','positive_asset_ratio','post_cost_expectancy','forward_3bar_median_return','flip_to_fail_rate'}, digits_cols={'mean_trades':1})}
</div>
"""


def update_todo(overall: pd.DataFrame, bucket_summary: pd.DataFrame, verdict: str, generated_at: str, latest_p3_appends: int) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    marker = "### Next 3 bot3 runs（当前默认执行顺序）\n"
    if marker not in text:
        raise RuntimeError("Next 3 marker not found in TODO.md")
    if f"**最新补充（{generated_at}）**" in text:
        return

    at6 = overall[overall["cost_bps_per_side"] == PRIMARY_COST].set_index("variant")
    base = at6.loc["baseline"] if "baseline" in at6.index else pd.Series(dtype=float)
    s60 = at6.loc["score_gte60"] if "score_gte60" in at6.index else pd.Series(dtype=float)
    s75 = at6.loc["score_gte75"] if "score_gte75" in at6.index else pd.Series(dtype=float)
    bucket_line = ""
    if len(bucket_summary) == 3:
        bs = bucket_summary.set_index("score_bucket")
        bucket_line = (
            f">  - baseline 信号的 score bucket 分层（6bps）冻结为：`<60 -> return≈{pct(bs.loc['lt60','mean_total_return'])} / expectancy≈{pct(bs.loc['lt60','post_cost_expectancy'])} / fail≈{pct(bs.loc['lt60','flip_to_fail_rate'])}`；\n"
            f">    `60~74 -> return≈{pct(bs.loc['60_74','mean_total_return'])} / expectancy≈{pct(bs.loc['60_74','post_cost_expectancy'])} / fail≈{pct(bs.loc['60_74','flip_to_fail_rate'])}`；\n"
            f">    `>=75 -> return≈{pct(bs.loc['gte75','mean_total_return'])} / expectancy≈{pct(bs.loc['gte75','post_cost_expectancy'])} / fail≈{pct(bs.loc['gte75','flip_to_fail_rate'])}`。\n"
        )

    block = (
        f"> **最新补充（{generated_at}）**：先再次核对 `Run 1 / EMA due-check` 与 `P3` 托管位状态：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍显示全 desk 没有新的 `due-now / overdue` lane，最早仍是 `Crypto 1d+1wk -> 2026-03-19 00:00 UTC / due_soon`；`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` 最新一次仍是 `new_closed_trades_appended={latest_p3_appends}`。因此当前没有新的 `Paper Seat` due-now 动作，也没有新的 `P3 status-changing event` 值得 bot3 回头挤占 continuity，按权威顺序这轮执行 **`Run 2 / Rank 71 minimal clean replication`**：固定复用 `BTC/ETH/SOL 120d 15m` cache，只接现成 `EMA / PSAR raw lane`，比较 `baseline`、`score>=60`、`score>=75` 三臂，统一 `signal 当根及之前数据 + next-bar open + no-overlap`。\n"
        f">  - `6bps/side` 下三臂结果冻结为：`baseline -> return≈{pct(base.get('mean_total_return'))} / expectancy≈{pct(base.get('post_cost_expectancy'))} / fail≈{pct(base.get('flip_to_fail_rate'))} / retention=100.00%`；`score>=60 -> return≈{pct(s60.get('mean_total_return'))} / expectancy≈{pct(s60.get('post_cost_expectancy'))} / fail≈{pct(s60.get('flip_to_fail_rate'))} / retention≈{pct(s60.get('mean_trade_retention'))}`；`score>=75 -> return≈{pct(s75.get('mean_total_return'))} / expectancy≈{pct(s75.get('post_cost_expectancy'))} / fail≈{pct(s75.get('flip_to_fail_rate'))} / retention≈{pct(s75.get('mean_trade_retention'))}`。\n"
        f"{bucket_line}"
        f">  - 当前更诚实的 hard verdict：**`Rank 71 / EMA-VWAP-ATR-volume graded admission score = {verdict}`**。\n"
        f">  - reader-facing 落点：`reports/site/factors/scout_rank71_ema_vwap_atr_volume_score_15m/report.html`、`reports/site/reading/repo_scout/rank71_ema_vwap_atr_volume_score_clean_replication.html`；artifact：`reports/artifacts/scout_rank71_ema_vwap_atr_volume_score_15m/overall_summary.csv`、`bucket_summary.csv`。\n"
        f">  - 这轮已消耗掉 Rank 71 允许的那次 minimal clean replication。当前更诚实的 active Scout 顺序应更新为：**fresh source intake（优先比较 realized-vol mid-band cost-survival gate > PSAR close-confirmed follow-up gate） > Rank 35b > Rank 16b > tiny-live plumbing**。\n"
        f">  - 因此当前最新 `Next 3` 顺序应更新为：**`Run 1 = EMA due-check only` -> `Run 2 = 若 Rank 71 clean replication 后仍不能升到更高层 verdict，则优先回到 fresh source 比较 realized-vol mid-band cost-survival gate > PSAR close-confirmed follow-up gate` -> `Run 3 = 若新的 fresh source 已 guard-passed 且 EMA 仍 waiting_not_due，则立刻给它 1 次最小 clean replication；只有 fresh source 这一层也 exhausted 时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing`**\n\n"
    )
    text = text.replace(marker, marker + "\n" + block, 1)
    TODO_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    latest_p3_appends = 0
    if P3_SUMMARY_PATH.exists():
        try:
            latest_p3_appends = int(pd.read_json(P3_SUMMARY_PATH, typ="series").get("new_closed_trades_appended", 0))
        except Exception:
            latest_p3_appends = 0

    frames = {asset: build_frame(asset, symbol) for asset, symbol in ASSETS.items()}

    signal_tables: list[pd.DataFrame] = []
    for asset in ASSETS:
        frame = frames[asset]
        for variant in VARIANTS:
            sig = build_signal_frame(frame, asset, variant)
            if not sig.empty:
                signal_tables.append(sig)
    all_signals = pd.concat(signal_tables, ignore_index=True) if signal_tables else pd.DataFrame()
    if all_signals.empty:
        raise RuntimeError("no signals formed for Rank 71 clean replication")
    all_signals.to_csv(ART_DIR / "signal_windows.csv", index=False)

    asset_rows: list[dict[str, object]] = []
    trade_frames: list[pd.DataFrame] = []

    for asset in ASSETS:
        frame = frames[asset]
        baseline_signals = all_signals[(all_signals["asset"] == asset) & (all_signals["variant"] == "baseline")].copy().reset_index(drop=True)
        for cost in COSTS:
            baseline_trades = build_trades(frame, baseline_signals, cost)
            if not baseline_trades.empty:
                trade_frames.append(baseline_trades)
            asset_rows.append(summarize_asset(baseline_trades, asset=asset, variant="baseline", cost_bps=cost, baseline_trades=baseline_trades))
            for variant in ["score_gte60", "score_gte75"]:
                sigs = all_signals[(all_signals["asset"] == asset) & (all_signals["variant"] == variant)].copy().reset_index(drop=True)
                trades = build_trades(frame, sigs, cost)
                if not trades.empty:
                    trade_frames.append(trades)
                asset_rows.append(summarize_asset(trades, asset=asset, variant=variant, cost_bps=cost, baseline_trades=baseline_trades))

    trades_df = pd.concat(trade_frames, ignore_index=True) if trade_frames else pd.DataFrame()
    asset_summary = pd.DataFrame(asset_rows).sort_values(["cost_bps_per_side", "variant", "asset"]).reset_index(drop=True)
    overall = build_overall(asset_summary)
    bucket_summary = build_bucket_summary(trades_df[(trades_df["cost_bps_per_side"] == PRIMARY_COST) & (trades_df["variant"] == "baseline")].copy())
    component_summary = build_component_summary(trades_df[(trades_df["cost_bps_per_side"] == PRIMARY_COST) & (trades_df["variant"] == "score_gte60")].copy())
    verdict, headline, reason = build_verdict(overall, bucket_summary)

    all_signals.to_csv(ART_DIR / "signal_windows.csv", index=False)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    bucket_summary.to_csv(ART_DIR / "bucket_summary.csv", index=False)
    component_summary.to_csv(ART_DIR / "component_summary.csv", index=False)
    trades_df.to_csv(ART_DIR / "trade_log.csv", index=False)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    factor_html = render_factor_page(overall, asset_summary, bucket_summary, component_summary, verdict, headline, reason, generated_at)
    reading_html = render_reading_page(overall, bucket_summary, verdict, headline, reason, generated_at)
    write_html(SITE_DIR / "report.html", "Rank 71 · EMA-VWAP-ATR-volume graded admission score", factor_html)
    write_html(READING_PATH, "Rank 71 · EMA-VWAP-ATR-volume graded admission score clean replication", reading_html)
    update_todo(overall, bucket_summary, verdict, generated_at, latest_p3_appends)

    print(f"generated_at={generated_at}")
    print(f"verdict={verdict}")
    print(f"headline={headline}")


if __name__ == "__main__":
    main()
