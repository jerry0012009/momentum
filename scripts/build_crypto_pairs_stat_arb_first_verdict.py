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
ART_DIR = ROOT / "reports" / "artifacts" / "scout_crypto_pairs_stat_arb_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_crypto_pairs_stat_arb_15m"
REPORT_PATH = SITE_DIR / "report.html"

SPEC_PATH = ART_DIR / "clean_room_spec_v1.csv"
PAIR_SUMMARY_PATH = ART_DIR / "pair_summary.csv"
TRADES_PATH = ART_DIR / "trades.csv"
TRIAL_META_PATH = ART_DIR / "trial_meta.csv"

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
ENTRY_Z = 2.0
EXIT_Z = 0.25
MAX_HOLD_BARS = 32
COST_BPS_PER_SIDE = 6.0
ROUNDTRIP_COST = 4.0 * COST_BPS_PER_SIDE / 10000.0
MIN_TRADE_FLOOR = 12


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


def fit_pair(prices: pd.DataFrame, left: str, right: str) -> tuple[pd.DataFrame, dict[str, float | str], list[dict[str, object]]]:
    n = len(prices)
    split_idx = int(n * TRAIN_FRACTION)
    train = prices.iloc[:split_idx].copy()
    test = prices.iloc[split_idx:].copy().reset_index(drop=True)

    left_log_train = np.log(train[f"{left}_close"])
    right_log_train = np.log(train[f"{right}_close"])
    beta = float(np.cov(left_log_train, right_log_train, ddof=0)[0, 1] / np.var(right_log_train))
    train_corr = float(np.corrcoef(left_log_train, right_log_train)[0, 1])

    left_log_full = np.log(prices[f"{left}_close"])
    right_log_full = np.log(prices[f"{right}_close"])
    spread_full = left_log_full - beta * right_log_full
    spread_mu = float(spread_full.iloc[:split_idx].mean())
    spread_std = float(spread_full.iloc[:split_idx].std(ddof=0))
    if not math.isfinite(spread_std) or spread_std <= 0:
        raise RuntimeError(f"invalid spread std for {left}/{right}")

    test = test.copy()
    test["spread"] = left_log_full.iloc[split_idx:].reset_index(drop=True) - beta * right_log_full.iloc[split_idx:].reset_index(drop=True)
    test["zscore"] = (test["spread"] - spread_mu) / spread_std
    test["signal_z"] = test["zscore"].shift(1)

    left_weight = 1.0 / (1.0 + abs(beta))
    right_weight = abs(beta) / (1.0 + abs(beta))

    pos = 0
    entry_idx = None
    entry_left = None
    entry_right = None
    entry_ts = None
    entry_z = None
    trade_rows: list[dict[str, object]] = []

    for i in range(1, len(test)):
        signal_z = test.at[i, "signal_z"]
        if pd.isna(signal_z):
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
        gross = left_weight * (left_ret if pos == 1 else -left_ret) + right_weight * (-right_ret if pos == 1 else right_ret)
        net = gross - ROUNDTRIP_COST
        trade_rows.append(
            {
                "pair": f"{left}/{right}",
                "side": "long_spread" if pos == 1 else "short_spread",
                "entry_time_utc": entry_ts,
                "exit_time_utc": test.at[i, "timestamp"],
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
        pair_verdict = "sample_thin_negative"

    summary = {
        "pair": f"{left}/{right}",
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "train_log_price_corr": train_corr,
        "frozen_beta": beta,
        "train_spread_mean": spread_mu,
        "train_spread_std": spread_std,
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
    return test, summary, trade_rows


def build_spec() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"item": "source", "value": "Tadi et al. (2021, 2023) + repo-inspired cointegration / z-score spread template"},
            {"item": "scope", "value": "15m crypto pairs on cached BTC/ETH/SOL history; first pass pairs = BTC/ETH, ETH/SOL, BTC/SOL"},
            {"item": "trade_on", "value": "Freeze hedge ratio on first 60% train window; on later bars, if prior-bar z-score >= +2 short spread, if <= -2 long spread; enter on next bar open"},
            {"item": "trade_off", "value": "Exit on next bar open when prior-bar z-score mean-reverts inside ±0.25, or max hold 32 bars"},
            {"item": "positioning", "value": "Dollar-neutral proxy using 1/(1+|beta|) and |beta|/(1+|beta|) leg weights"},
            {"item": "cost_model", "value": f"{COST_BPS_PER_SIDE:.1f} bps per side per leg; roundtrip charged as 4 legs = {ROUNDTRIP_COST:.4f}"},
            {"item": "lookahead_guard", "value": "Signals use prior-bar z-score only; entries/exits execute on next bar open"},
            {"item": "repaint_guard", "value": "No future extrema / no revised labels; only cached OHLCV closes and next open execution"},
            {"item": "what_this_is", "value": "Clean replication / honesty gate only; not yet formal cointegration test, not yet stability pack"},
            {"item": "next_light_check", "value": "If replication survives, next check should be time stability + cross-pair stability; if replication is broadly negative, park"},
        ]
    )


def render_report(spec_df: pd.DataFrame, pair_df: pd.DataFrame, trade_df: pd.DataFrame, meta_df: pd.DataFrame) -> None:
    ensure_dir(SITE_DIR)
    meta = meta_df.iloc[0]
    best_pair = pair_df.sort_values("cumulative_net_return", ascending=False).iloc[0] if not pair_df.empty else pd.Series(dtype=object)
    trade_preview = trade_df.head(12).copy()
    if not trade_preview.empty:
        trade_preview["entry_time_utc"] = trade_preview["entry_time_utc"].map(fmt_ts)
        trade_preview["exit_time_utc"] = trade_preview["exit_time_utc"].map(fmt_ts)

    html = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Scout · Crypto Pairs Stat-Arb 15m</title>
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
  <p><a href="../../index.html">← 返回首页</a></p>
  <h1>Scout · Crypto Pairs Stat-Arb 15m</h1>
  <p class=\"muted\">生成时间：{escape(str(meta['generated_at_utc']))} ｜ 这是 Rank 4 的最小 clean replication 页：只回答 source intake / replication 是否跑通，以及当前应该继续还是 park。</p>

  <div class=\"card\">
    <h2>一句话结论</h2>
    <p><b>{escape(str(meta['headline']))}</b></p>
    <ul>
      <li><b>hard verdict：</b><code>{escape(str(meta['verdict']))}</code></li>
      <li><b>best pair：</b><code>{escape(str(meta['best_pair']))}</code></li>
      <li><b>best pair cumulative net return：</b>{pct(meta['best_pair_cumulative_net_return'])}</li>
      <li><b>best pair trade count：</b>{num(meta['best_pair_trade_count'], 0)}</li>
      <li><b>why：</b>{escape(str(meta['verdict_basis']))}</li>
    </ul>
    <p class=\"muted\">这轮是 clean replication，不是 formal cointegration paper-faithful 复现，也不是 Light Stability Pack。当前先判断：最小规则能否诚实跑通，结果是否值得进入下一刀轻量稳定性。</p>
  </div>

  <div class=\"card\">
    <h2>Frozen clean-room spec</h2>
    {render_table(spec_df, percent_cols=set())}
  </div>

  <div class=\"card\">
    <h2>Pair summary</h2>
    {render_table(pair_df, percent_cols={'train_log_price_corr', 'win_rate', 'mean_net_return', 'cumulative_net_return'}, digits_cols={'frozen_beta': 3, 'train_spread_mean': 4, 'train_spread_std': 4, 'entry_z': 2, 'exit_z': 2, 'avg_hold_bars': 1})}
    <p class=\"muted\">若 clean replication 后三组 pairs 都是负净路径，desk 读法应更偏向 <code>park</code>，而不是为继续保留 Rank 4 强行补更多漂亮说明。</p>
  </div>

  <div class=\"card\">
    <h2>Trade preview</h2>
    {render_table(trade_preview, percent_cols={'left_weight', 'right_weight', 'left_leg_return', 'right_leg_return', 'gross_return', 'net_return', 'roundtrip_cost'}, digits_cols={'entry_zscore': 2, 'exit_signal_zscore': 2, 'hold_bars': 0})}
    <p class=\"muted\">这里只展示前 12 笔 trade preview；完整表见 <code>reports/artifacts/scout_crypto_pairs_stat_arb_15m/trades.csv</code>。</p>
  </div>

  <div class=\"card\">
    <h2>边界与下一步</h2>
    <ul>
      <li>当前没有跑 formal cointegration test / Johansen / rolling beta，只做 repo-inspired frozen-beta z-score clean replication。</li>
      <li>当前也没有做时间稳定性 / 参数稳定性 / 跨 pair 稳定性 / 成本敏感度，这些属于后续 Light Stability Pack。</li>
      <li>但如果 clean replication 本身已经在主要 pairs 上一起偏负，就应优先给 <code>park</code>，而不是默认继续扩研究。</li>
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
        _, summary, trade_rows = fit_pair(prices, left, right)
        pair_rows.append(summary)
        trade_rows_all.extend(trade_rows)

    pair_df = pd.DataFrame(pair_rows).sort_values("cumulative_net_return", ascending=False).reset_index(drop=True)
    trade_df = pd.DataFrame(trade_rows_all).sort_values(["entry_time_utc", "pair"]).reset_index(drop=True)

    best = pair_df.iloc[0] if not pair_df.empty else pd.Series(dtype=object)
    any_positive = bool((pair_df["cumulative_net_return"] > 0).fillna(False).any()) if not pair_df.empty else False
    all_negative = bool((pair_df["cumulative_net_return"] <= 0).fillna(True).all()) if not pair_df.empty else True

    verdict = "park"
    headline = "Rank 4 已完成最小 clean replication；当前三组高相关 crypto pairs 在 frozen-beta z-score spread first pass 下整体偏负，应先 park。"
    verdict_basis = "BTC/ETH、ETH/SOL、BTC/SOL 三组 pair 的 cumulative net return 全为负；clean replication 已跑通，但当前不值得直接进入 paper candidate pool。"
    next_step = "park_rank4_and_revisit_only_if_new_pair_scope_or_better_repo_spec"
    if any_positive and float(best.get("trade_count", 0)) >= MIN_TRADE_FLOOR:
        verdict = "one_more_light_check"
        headline = "Rank 4 clean replication 已跑通，且至少一组 pair 保留正向 first-pass 迹象；可以补一刀轻量稳定性再决定。"
        verdict_basis = "至少一组 pair 在 frozen-beta z-score spread first pass 下保持正 cumulative net return，且交易数未低于最小 floor。"
        next_step = "time_stability_then_cross_pair_stability"
    elif not all_negative:
        headline = "Rank 4 clean replication 已跑通，但结果混合且不够硬；当前仍更像 one-more-light-check / narrow hold，而不是 paper candidate。"
        verdict_basis = "存在 mixed pair outcomes，但没有足够强的跨 pair 正向迹象；先不升格。"
        next_step = "time_stability_then_cost_tradecount_check"

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
                "verdict_basis": verdict_basis,
                "next_step": next_step,
            }
        ]
    )

    spec_df.to_csv(SPEC_PATH, index=False)
    pair_df.to_csv(PAIR_SUMMARY_PATH, index=False)
    trade_df.to_csv(TRADES_PATH, index=False)
    meta_df.to_csv(TRIAL_META_PATH, index=False)
    render_report(spec_df, pair_df, trade_df, meta_df)

    print("[ok] crypto pairs stat-arb first verdict generated")
    print("[artifact]", PAIR_SUMMARY_PATH)
    print("[site]", REPORT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
