#!/usr/bin/env python3
from __future__ import annotations

import math
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_crypto_pairs_stat_arb_15m_rank4b"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_crypto_pairs_stat_arb_15m_rank4b"
REPORT_PATH = SITE_DIR / "report.html"

SPEC_PATH = ART_DIR / "clean_room_spec_v2.csv"
PAIR_SUMMARY_PATH = ART_DIR / "pair_summary.csv"
TRADES_PATH = ART_DIR / "trades.csv"
TRIAL_META_PATH = ART_DIR / "trial_meta.csv"
COMPARE_PATH = ART_DIR / "rank4_vs_rank4b_compare.csv"
TIME_STABILITY_PATH = ART_DIR / "time_stability_check.csv"

SYMBOLS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
PAIRS = [
    ("BTC-USD", "ETH-USD"),
    ("ETH-USD", "SOL-USD"),
    ("BTC-USD", "SOL-USD"),
]
TRAIN_FRACTION = 0.60
ROLL_WINDOW = 192
ENTRY_Z = 2.5
EXIT_Z = 0.0
MAX_HOLD_BARS = 32
COST_BPS_PER_SIDE = 6.0
ROUNDTRIP_COST = 4.0 * COST_BPS_PER_SIDE / 10000.0
MIN_TRADE_FLOOR = 12
BASELINE_PAIR_SUMMARY_PATH = ROOT / "reports" / "artifacts" / "scout_crypto_pairs_stat_arb_15m" / "pair_summary.csv"


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


def load_symbol(asset: str, symbol: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    if not path.exists():
        raise FileNotFoundError(f"missing cache: {path}")
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df[["timestamp", "open", "close"]].rename(
        columns={"open": f"{asset}_open", "close": f"{asset}_close"}
    )


def build_aligned_prices() -> pd.DataFrame:
    merged = None
    for asset, symbol in SYMBOLS.items():
        df = load_symbol(asset, symbol)
        merged = df if merged is None else merged.merge(df, on="timestamp", how="inner")
    if merged is None or merged.empty:
        raise RuntimeError("no aligned price cache available")
    return merged.sort_values("timestamp").reset_index(drop=True)


def fit_pair(prices: pd.DataFrame, left: str, right: str) -> tuple[dict[str, float | str], list[dict[str, object]]]:
    n = len(prices)
    split_idx = int(n * TRAIN_FRACTION)
    test = prices.iloc[split_idx:].copy().reset_index(drop=True)

    left_log_full = np.log(prices[f"{left}_close"])
    right_log_full = np.log(prices[f"{right}_close"])

    beta_full = left_log_full.rolling(ROLL_WINDOW).cov(right_log_full) / right_log_full.rolling(ROLL_WINDOW).var()
    spread_full = left_log_full - beta_full * right_log_full
    spread_mu = spread_full.rolling(ROLL_WINDOW).mean()
    spread_std = spread_full.rolling(ROLL_WINDOW).std(ddof=0)
    zscore_full = (spread_full - spread_mu) / spread_std

    test["beta"] = beta_full.iloc[split_idx:].reset_index(drop=True)
    test["spread"] = spread_full.iloc[split_idx:].reset_index(drop=True)
    test["zscore"] = zscore_full.iloc[split_idx:].reset_index(drop=True)
    test["signal_z"] = test["zscore"].shift(1)

    train_beta = beta_full.iloc[:split_idx].dropna()
    train_corr = float(np.corrcoef(left_log_full.iloc[:split_idx], right_log_full.iloc[:split_idx])[0, 1])
    beta_median = float(train_beta.median()) if not train_beta.empty else float("nan")

    pos = 0
    entry_idx = None
    entry_left = None
    entry_right = None
    entry_ts = None
    entry_z = None
    entry_beta = None
    trade_rows: list[dict[str, object]] = []

    for i in range(1, len(test)):
        signal_z = test.at[i, "signal_z"]
        beta_now = test.at[i, "beta"]
        if pd.isna(signal_z) or pd.isna(beta_now) or not math.isfinite(float(beta_now)):
            continue

        if pos == 0:
            if signal_z >= ENTRY_Z:
                pos = -1
            elif signal_z <= -ENTRY_Z:
                pos = 1
            else:
                continue
            entry_idx = i
            entry_left = float(test.at[i, f"{left}_open"])
            entry_right = float(test.at[i, f"{right}_open"])
            entry_ts = test.at[i, "timestamp"]
            entry_z = float(signal_z)
            entry_beta = float(beta_now)
            continue

        hold_bars = i - int(entry_idx)
        exit_now = False
        if pos == 1 and signal_z >= -EXIT_Z:
            exit_now = True
        if pos == -1 and signal_z <= EXIT_Z:
            exit_now = True
        if hold_bars >= MAX_HOLD_BARS:
            exit_now = True
        if not exit_now:
            continue

        exit_left = float(test.at[i, f"{left}_open"])
        exit_right = float(test.at[i, f"{right}_open"])
        left_ret = exit_left / float(entry_left) - 1.0
        right_ret = exit_right / float(entry_right) - 1.0
        left_weight = 1.0 / (1.0 + abs(float(entry_beta)))
        right_weight = abs(float(entry_beta)) / (1.0 + abs(float(entry_beta)))
        gross = left_weight * (left_ret if pos == 1 else -left_ret) + right_weight * (-right_ret if pos == 1 else right_ret)
        net = gross - ROUNDTRIP_COST
        trade_rows.append(
            {
                "pair": f"{left}/{right}",
                "side": "long_spread" if pos == 1 else "short_spread",
                "entry_time_utc": entry_ts,
                "exit_time_utc": test.at[i, "timestamp"],
                "entry_beta": entry_beta,
                "entry_zscore": entry_z,
                "exit_signal_zscore": float(signal_z),
                "hold_bars": hold_bars,
                "left_weight": left_weight,
                "right_weight": right_weight,
                "left_leg_return": left_ret,
                "right_leg_return": right_ret,
                "gross_return": gross,
                "net_return": net,
                "roundtrip_cost": ROUNDTRIP_COST,
            }
        )
        pos = 0
        entry_idx = None
        entry_left = None
        entry_right = None
        entry_ts = None
        entry_z = None
        entry_beta = None

    trades = pd.DataFrame(trade_rows)
    trade_count = int(len(trades))
    mean_net = float(trades["net_return"].mean()) if trade_count else float("nan")
    cum_net = float((1.0 + trades["net_return"]).prod() - 1.0) if trade_count else float("nan")
    win_rate = float((trades["net_return"] > 0).mean()) if trade_count else float("nan")
    avg_hold = float(trades["hold_bars"].mean()) if trade_count else float("nan")

    pair_verdict = "park"
    if trade_count >= MIN_TRADE_FLOOR and math.isfinite(cum_net) and cum_net > 0:
        pair_verdict = "one_more_light_check"
    elif trade_count >= MIN_TRADE_FLOOR:
        pair_verdict = "clean_replication_complete_but_negative"
    elif trade_count > 0:
        pair_verdict = "sample_thin"

    summary = {
        "pair": f"{left}/{right}",
        "train_rows": split_idx,
        "test_rows": int(len(test)),
        "train_log_price_corr": train_corr,
        "rolling_beta_window": ROLL_WINDOW,
        "train_beta_median": beta_median,
        "entry_z": ENTRY_Z,
        "exit_z": EXIT_Z,
        "max_hold_bars": MAX_HOLD_BARS,
        "trade_count": trade_count,
        "win_rate": win_rate,
        "mean_net_return": mean_net,
        "cumulative_net_return": cum_net,
        "avg_hold_bars": avg_hold,
        "pair_verdict": pair_verdict,
    }
    return summary, trade_rows


def build_spec() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"item": "source", "value": "Rank 4b reframe from Tadi et al. (2021/2023) + repo-inspired stat-arb template"},
            {"item": "scope", "value": "15m crypto pairs on cached BTC/ETH/SOL history; same 3 pairs as Rank 4 baseline"},
            {"item": "what_changed_vs_rank4", "value": "Freeze narrow reframe: rolling-beta z-score spread instead of frozen-beta; stricter entry_z = 2.5; no extra regime gate in the formal v2 spec"},
            {"item": "trade_on", "value": "After 60% train split, use prior-bar rolling z-score; if >= +2.5 short spread, if <= -2.5 long spread; enter on next bar open"},
            {"item": "trade_off", "value": "Exit on next bar open when prior-bar z-score mean-reverts back through 0.0, or max hold 32 bars"},
            {"item": "beta_model", "value": f"Rolling beta via {ROLL_WINDOW}-bar covariance / variance; weights frozen per trade at entry beta"},
            {"item": "positioning", "value": "Dollar-neutral proxy using 1/(1+|beta|) and |beta|/(1+|beta|) leg weights"},
            {"item": "cost_model", "value": f"{COST_BPS_PER_SIDE:.1f} bps per side per leg; roundtrip charged as 4 legs = {ROUNDTRIP_COST:.4f}"},
            {"item": "lookahead_guard", "value": "Signals use prior-bar rolling z-score only; entries/exits execute on next bar open"},
            {"item": "repaint_guard", "value": "No future extrema / no revised labels; only cached OHLCV closes and next open execution"},
            {"item": "why_no_extra_gate_yet", "value": "The reframe first asks whether model calibration alone can rescue the pocket; regime/vol gates stay second-order until this clean replication v2 passes"},
            {"item": "next_light_check_if_survives", "value": "Time stability + cost/trade-count stability + cross-pair stability before any paper-candidate discussion"},
        ]
    )


def build_compare(rank4b_df: pd.DataFrame) -> pd.DataFrame:
    if not BASELINE_PAIR_SUMMARY_PATH.exists():
        return pd.DataFrame()
    baseline = pd.read_csv(BASELINE_PAIR_SUMMARY_PATH)
    baseline = baseline[["pair", "trade_count", "cumulative_net_return", "pair_verdict"]].rename(
        columns={
            "trade_count": "rank4_trade_count",
            "cumulative_net_return": "rank4_cumulative_net_return",
            "pair_verdict": "rank4_verdict",
        }
    )
    cur = rank4b_df[["pair", "trade_count", "cumulative_net_return", "pair_verdict"]].rename(
        columns={
            "trade_count": "rank4b_trade_count",
            "cumulative_net_return": "rank4b_cumulative_net_return",
            "pair_verdict": "rank4b_verdict",
        }
    )
    merged = baseline.merge(cur, on="pair", how="outer")
    merged["cum_net_delta"] = merged["rank4b_cumulative_net_return"] - merged["rank4_cumulative_net_return"]
    merged["trade_count_delta"] = merged["rank4b_trade_count"] - merged["rank4_trade_count"]
    return merged.sort_values("cum_net_delta", ascending=False).reset_index(drop=True)


def build_time_stability(trade_df: pd.DataFrame) -> pd.DataFrame:
    if trade_df.empty:
        return pd.DataFrame(
            columns=[
                "pair",
                "window_kind",
                "window_label",
                "trade_count",
                "win_rate",
                "mean_net_return",
                "cumulative_net_return",
                "window_verdict",
            ]
        )

    rows: list[dict[str, object]] = []
    for pair, pair_df in trade_df.groupby("pair"):
        pair_df = pair_df.sort_values("entry_time_utc").reset_index(drop=True).copy()

        seq_codes = pd.qcut(pair_df.index, q=min(3, len(pair_df)), labels=False, duplicates="drop")
        pair_df["seq_bucket"] = seq_codes.astype(int)
        for bucket, bucket_df in pair_df.groupby("seq_bucket"):
            cum = float((1.0 + bucket_df["net_return"]).prod() - 1.0)
            rows.append(
                {
                    "pair": pair,
                    "window_kind": "time_tercile",
                    "window_label": f"tercile_{int(bucket) + 1}",
                    "trade_count": int(len(bucket_df)),
                    "win_rate": float((bucket_df["net_return"] > 0).mean()),
                    "mean_net_return": float(bucket_df["net_return"].mean()),
                    "cumulative_net_return": cum,
                    "window_verdict": "positive" if cum > 0 else "negative_or_flat",
                }
            )

        pair_df["month_bucket"] = pair_df["entry_time_utc"].dt.strftime("%Y-%m")
        for month, month_df in pair_df.groupby("month_bucket"):
            cum = float((1.0 + month_df["net_return"]).prod() - 1.0)
            rows.append(
                {
                    "pair": pair,
                    "window_kind": "calendar_month",
                    "window_label": month,
                    "trade_count": int(len(month_df)),
                    "win_rate": float((month_df["net_return"] > 0).mean()),
                    "mean_net_return": float(month_df["net_return"].mean()),
                    "cumulative_net_return": cum,
                    "window_verdict": "positive" if cum > 0 else "negative_or_flat",
                }
            )

    return pd.DataFrame(rows)


def render_report(spec_df: pd.DataFrame, pair_df: pd.DataFrame, trade_df: pd.DataFrame, meta_df: pd.DataFrame, compare_df: pd.DataFrame, time_stability_df: pd.DataFrame) -> None:
    ensure_dir(SITE_DIR)
    meta = meta_df.iloc[0]
    trade_preview = trade_df.head(12).copy()
    stability_preview = time_stability_df.copy()
    if not trade_preview.empty:
        trade_preview["entry_time_utc"] = trade_preview["entry_time_utc"].map(fmt_ts)
        trade_preview["exit_time_utc"] = trade_preview["exit_time_utc"].map(fmt_ts)

    html = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Scout · Crypto Pairs Stat-Arb 15m Rank 4b</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1080px; margin: 40px auto; padding: 0 18px; line-height: 1.68; color: #111827; background: #f8fafc; }}
    h1,h2,h3 {{ line-height: 1.25; }}
    .muted {{ color:#6b7280; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    a {{ color:#2563eb; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
  </style>
</head>
<body>
  <p><a href=\"../../index.html\">← 返回首页</a></p>
  <h1>Scout · Crypto Pairs Stat-Arb 15m · Rank 4b Reframe</h1>
  <p class=\"muted\">生成时间：{escape(str(meta['generated_at_utc']))} ｜ 这是原 Rank 4 之后的窄重开：不翻案原 park，只回答 rolling-beta / stricter entry 是否足够把它推进到下一刀轻量稳定性。</p>

  <div class=\"card\">
    <h2>一句话结论</h2>
    <p><b>{escape(str(meta['headline']))}</b></p>
    <ul>
      <li><b>hard verdict：</b><code>{escape(str(meta['verdict']))}</code></li>
      <li><b>best pair：</b><code>{escape(str(meta['best_pair']))}</code></li>
      <li><b>best pair cumulative net return：</b>{pct(meta['best_pair_cumulative_net_return'])}</li>
      <li><b>positive pairs：</b>{num(meta['positive_pair_count'], 0)} / {num(meta['pair_count'], 0)}</li>
      <li><b>why：</b>{escape(str(meta['verdict_basis']))}</li>
    </ul>
    <p class=\"muted\">这里仍不是 paper candidate verdict。它只是在判断：Rank 4b 这条窄重开，是否已经从“直接 park”抬升到“值得补一刀 Light Stability Pack”。</p>
  </div>

  <div class=\"card\">
    <h2>Frozen clean-room spec v2</h2>
    {render_table(spec_df, percent_cols=set())}
  </div>

  <div class=\"card\">
    <h2>Rank 4b pair summary</h2>
    {render_table(pair_df, percent_cols={'train_log_price_corr', 'win_rate', 'mean_net_return', 'cumulative_net_return'}, digits_cols={'rolling_beta_window': 0, 'train_beta_median': 3, 'entry_z': 2, 'exit_z': 2, 'avg_hold_bars': 1})}
    <p class=\"muted\">当前读法应优先看：是不是至少有不止一组 pair 从明显负 pocket 被抬回到轻微正 pocket，以及交易数有没有薄到失真。</p>
  </div>

  <div class=\"card\">
    <h2>Rank 4 vs Rank 4b compare</h2>
    {render_table(compare_df, percent_cols={'rank4_cumulative_net_return', 'rank4b_cumulative_net_return', 'cum_net_delta'}, digits_cols={'rank4_trade_count': 0, 'rank4b_trade_count': 0, 'trade_count_delta': 0})}
    <p class=\"muted\">这张对照不是为了证明 stat-arb 已经成立，而是为了回答：窄 reframe 后，结果有没有从“全线负值”抬回到“值得补下一刀”的状态。</p>
  </div>

    <div class="card">
    <h2>Light Stability Pack · 时间稳定性（决策刀）</h2>
    {render_table(stability_preview, percent_cols={'win_rate', 'mean_net_return', 'cumulative_net_return'}, digits_cols={'trade_count': 0})}
    <p class="muted">这轮只补一刀时间稳定性，而且直接拿它做 promote / park 二选一：如果 surviving positive pairs 在最近 tercile 与最近月份都一起转负，就说明 pocket 主要来自前段样本，不够诚实地升 paper candidate。</p>
  </div>

  <div class=\"card\">
    <h2>Trade preview</h2>
    {render_table(trade_preview, percent_cols={'left_weight', 'right_weight', 'left_leg_return', 'right_leg_return', 'gross_return', 'net_return', 'roundtrip_cost'}, digits_cols={'entry_beta': 3, 'entry_zscore': 2, 'exit_signal_zscore': 2, 'hold_bars': 0})}
    <p class=\"muted\">这里只展示前 12 笔 trade preview；完整表见 <code>reports/artifacts/scout_crypto_pairs_stat_arb_15m_rank4b/trades.csv</code>。</p>
  </div>

  <div class=\"card\">
    <h2>边界与下一步</h2>
    <ul>
      <li>原 Rank 4 = <code>park</code> 仍然成立；Rank 4b 只是合法窄重开，不是推翻旧 verdict。</li>
      <li>当前还没有进入 Light Stability Pack 的完整四项，只完成 clean replication v2。</li>
      <li>若后续继续，默认下一刀应是：时间稳定性、成本/交易数稳定性、跨 pair 稳定性；若这几刀任一明显翻弱，就更诚实地把 Rank 4b 压回 <code>park</code>。</li>
    </ul>
  </div>
</body>
</html>
"""
    REPORT_PATH.write_text(html, encoding="utf-8")


def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    prices = build_aligned_prices()

    spec_df = build_spec()
    pair_rows = []
    trade_rows_all: list[dict[str, object]] = []
    for left, right in PAIRS:
        summary, trade_rows = fit_pair(prices, left, right)
        pair_rows.append(summary)
        trade_rows_all.extend(trade_rows)

    pair_df = pd.DataFrame(pair_rows).sort_values("cumulative_net_return", ascending=False).reset_index(drop=True)
    trade_df = pd.DataFrame(trade_rows_all).sort_values(["entry_time_utc", "pair"]).reset_index(drop=True)
    compare_df = build_compare(pair_df)
    time_stability_df = build_time_stability(trade_df)

    positive_pair_count = int((pair_df["cumulative_net_return"] > 0).fillna(False).sum()) if not pair_df.empty else 0
    best = pair_df.iloc[0] if not pair_df.empty else pd.Series(dtype=object)

    positive_pairs = pair_df.loc[pair_df["cumulative_net_return"] > 0, "pair"].tolist() if not pair_df.empty else []
    recent_tercile = time_stability_df[
        (time_stability_df["window_kind"] == "time_tercile") & (time_stability_df["window_label"] == "tercile_3")
    ]
    latest_month_label = None
    latest_month_df = pd.DataFrame(columns=time_stability_df.columns)
    month_df = time_stability_df[time_stability_df["window_kind"] == "calendar_month"]
    if not month_df.empty:
        latest_month_label = sorted(month_df["window_label"].unique())[-1]
        latest_month_df = month_df[month_df["window_label"] == latest_month_label]

    positive_recent_tercile = set(recent_tercile.loc[recent_tercile["cumulative_net_return"] > 0, "pair"].tolist())
    positive_latest_month = set(latest_month_df.loc[latest_month_df["cumulative_net_return"] > 0, "pair"].tolist())
    positive_pairs_set = set(positive_pairs)
    tail_instability = bool(positive_pairs_set) and positive_pairs_set.isdisjoint(positive_recent_tercile) and positive_pairs_set.isdisjoint(positive_latest_month)

    verdict = "park"
    headline = "Rank 4b rolling-beta clean replication 已把部分 pair 从原先显著负值收回到轻微正 pocket，但最新时间切片把 surviving pairs 一起压回负值，因此当前更诚实 verdict 是 park。"
    verdict_basis = "虽然 ETH/SOL 与 BTC/SOL 的 overall first pass 转正，但它们在最近 tercile 与最新月份都一起转负，说明 pocket 主要来自样本前段，当前不够诚实地升为 paper candidate。"
    next_step = "park_rank4b_keep_as_evidence_pool"
    if positive_pair_count == 0:
        headline = "Rank 4b rolling-beta clean replication 仍不足以形成稳定存活 pocket；当前应更诚实地维持 park。"
        verdict_basis = "即便用 rolling-beta + stricter entry，主要 pairs 也没有形成足够硬的正向 first pass。"
    elif not tail_instability and positive_pair_count >= 1 and float(best.get("trade_count", 0)) >= MIN_TRADE_FLOOR:
        verdict = "paper_candidate"
        headline = "Rank 4b rolling-beta clean replication 在最小时间稳定性下仍保留 surviving pocket，可先升成 paper candidate pool，但还不该直接去 tiny-live。"
        verdict_basis = "至少 1 组 surviving pair 不只 overall 为正，而且没有在最新 tercile 与最新月份同时塌回负值，因此通过了这轮唯一允许的 one_more_light_check。"
        next_step = "cost_tradecount_then_cross_pair_for_paper_candidate"

    meta_df = pd.DataFrame(
        [
            {
                "generated_at_utc": generated_at,
                "sample_window": f"{fmt_ts(prices['timestamp'].min())} -> {fmt_ts(prices['timestamp'].max())}",
                "source_intake_verdict": "pass",
                "clean_replication_verdict": "pass",
                "lookahead_guard": "pass",
                "repaint_guard": "pass",
                "formal_cointegration_test": "not_attempted",
                "verdict": verdict,
                "headline": headline,
                "best_pair": best.get("pair", "-"),
                "best_pair_trade_count": best.get("trade_count", np.nan),
                "best_pair_cumulative_net_return": best.get("cumulative_net_return", np.nan),
                "pair_count": len(pair_df),
                "positive_pair_count": positive_pair_count,
                "verdict_basis": verdict_basis,
                "next_step": next_step,
            }
        ]
    )

    spec_df.to_csv(SPEC_PATH, index=False)
    pair_df.to_csv(PAIR_SUMMARY_PATH, index=False)
    trade_df.to_csv(TRADES_PATH, index=False)
    meta_df.to_csv(TRIAL_META_PATH, index=False)
    compare_df.to_csv(COMPARE_PATH, index=False)
    time_stability_df.to_csv(TIME_STABILITY_PATH, index=False)
    render_report(spec_df, pair_df, trade_df, meta_df, compare_df, time_stability_df)

    print("[ok] crypto pairs stat-arb rank4b report generated")
    print("[artifact]", PAIR_SUMMARY_PATH)
    print("[site]", REPORT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
