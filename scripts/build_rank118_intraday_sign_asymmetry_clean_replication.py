#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank118_intraday_sign_asymmetry_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank118_intraday_sign_asymmetry_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank118_intraday_sign_asymmetry_clean_replication.html"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
TRAIN_FRACTION = 0.60
HOLD_BARS = 8
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0]
PAIR_LOOKBACK = 32
PAIR_THRESHOLD = 0.0
JUMP_LOOKBACK = 96
JUMP_SIGMA = 2.0
FOMC_EVENTS_UTC = [
    "2025-12-17T19:00:00Z",
    "2026-01-28T19:00:00Z",
    "2026-03-18T18:00:00Z",
]
BLACKOUT_HOURS = 2
EPS = 1e-12

CSS = """
body { font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width:1180px; margin:32px auto; padding:0 18px 48px; line-height:1.68; color:#111827; background:#f8fafc; }
h1,h2,h3 { color:#111827; }
.card { border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }
.muted { color:#6b7280; }
.good { color:#065f46; font-weight:600; }
.bad { color:#991b1b; font-weight:600; }
.warn { color:#92400e; font-weight:600; }
code { background:#f3f4f6; padding:1px 5px; border-radius:6px; }
table { width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; background:white; }
th, td { border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }
a { color:#2563eb; text-decoration:none; }
"""


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def pct(v, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def num(v, digits: int = 2) -> str:
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


def net_ret(gross: pd.Series | float, cost_bps: float) -> pd.Series | float:
    rate = float(cost_bps) / 10000.0
    return (1.0 + gross) * (1.0 - rate) * (1.0 - rate) - 1.0


def load_bars(symbol: str, asset: str) -> pd.DataFrame:
    df = pd.read_csv(CACHE_DIR / f"{symbol}__120d__15m.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def compute_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [
            (df["high"] - df["low"]).abs(),
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def build_blackout_mask(ts: pd.Series) -> pd.Series:
    events = pd.to_datetime(FOMC_EVENTS_UTC, utc=True)
    mask = pd.Series(False, index=ts.index)
    for event in events:
        mask |= (ts >= event - pd.Timedelta(hours=BLACKOUT_HOURS)) & (ts <= event + pd.Timedelta(hours=BLACKOUT_HOURS))
    return mask


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_bars(symbol, asset)
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema15"] = df["close"].ewm(span=15, adjust=False).mean()
    df["ema_slope"] = df["ema9"].pct_change(3)
    df["atr14"] = compute_atr(df)
    df["vol_ma20"] = df["volume"].rolling(20, min_periods=20).mean()
    df["rolling_low20"] = df["low"].rolling(20, min_periods=20).min().shift(1)
    low = df["rolling_low20"]
    atr = df["atr14"]

    df["base_signal"] = (
        low.notna()
        & atr.notna()
        & (df["ema9"] < df["ema15"])
        & (df["ema_slope"] < -0.0003)
        & (df["close"].shift(1) > low.shift(1))
        & (df["close"].shift(2) > low.shift(2))
        & (df["close"] < low - 0.1 * atr)
        & (df["high"] <= low + 0.3 * atr)
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)

    df["recent_ret_4"] = df["close"] / df["close"].shift(4) - 1.0
    df["forward_ret_4"] = df["close"].shift(-4) / df["close"] - 1.0
    df["slot"] = df["timestamp"].dt.strftime("%H:%M")
    df["pair_value"] = df["recent_ret_4"] * df["forward_ret_4"]
    df["pair_value_lag"] = df.groupby("slot")["pair_value"].shift(1)
    df["pair_mean"] = df.groupby("slot")["pair_value_lag"].transform(
        lambda s: s.rolling(PAIR_LOOKBACK, min_periods=PAIR_LOOKBACK).mean()
    )
    df["pair_count"] = df.groupby("slot")["pair_value_lag"].transform(
        lambda s: s.rolling(PAIR_LOOKBACK, min_periods=PAIR_LOOKBACK).count()
    )
    df["predictor_sign"] = 0
    df.loc[df["pair_mean"] > PAIR_THRESHOLD, "predictor_sign"] = 1
    df.loc[df["pair_mean"] < -PAIR_THRESHOLD, "predictor_sign"] = -1

    df["recent_dir"] = np.sign(df["recent_ret_4"]).fillna(0).astype(int)
    df["expected_next_dir"] = 0
    cont_mask = df["predictor_sign"] == 1
    rev_mask = df["predictor_sign"] == -1
    df.loc[cont_mask, "expected_next_dir"] = df.loc[cont_mask, "recent_dir"]
    df.loc[rev_mask, "expected_next_dir"] = -df.loc[rev_mask, "recent_dir"]

    df["ret4_std"] = df["recent_ret_4"].shift(1).rolling(JUMP_LOOKBACK, min_periods=JUMP_LOOKBACK).std()
    df["jump_z"] = (df["recent_ret_4"].abs() / df["ret4_std"].clip(lower=EPS)).replace([np.inf, -np.inf], np.nan)
    df["no_jump"] = (df["jump_z"] <= JUMP_SIGMA).fillna(False)
    df["fomc_blackout"] = build_blackout_mask(df["timestamp"])
    return df


def collect_signals(frame: pd.DataFrame, asset: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    signal_idx = np.flatnonzero(frame["base_signal"].to_numpy())
    for idx in signal_idx:
        if idx + 2 >= len(frame):
            continue
        row = frame.iloc[idx]
        if not np.isfinite(row["atr14"]) or float(row["atr14"]) <= 0:
            continue
        sign_gate = bool(int(row["expected_next_dir"]) == -1 and int(row["predictor_sign"]) != 0)
        rows.append(
            {
                "asset": asset,
                "signal_idx": int(idx),
                "signal_time": row["timestamp"],
                "signal_close": float(row["close"]),
                "breakout_anchor": float(row["rolling_low20"]),
                "atr14": float(row["atr14"]),
                "recent_ret_4": float(row["recent_ret_4"]) if pd.notna(row["recent_ret_4"]) else np.nan,
                "pair_mean": float(row["pair_mean"]) if pd.notna(row["pair_mean"]) else np.nan,
                "pair_count": float(row["pair_count"]) if pd.notna(row["pair_count"]) else np.nan,
                "predictor_sign": int(row["predictor_sign"]),
                "recent_dir": int(row["recent_dir"]),
                "expected_next_dir": int(row["expected_next_dir"]),
                "jump_z": float(row["jump_z"]) if pd.notna(row["jump_z"]) else np.nan,
                "no_jump": bool(row["no_jump"]),
                "fomc_blackout": bool(row["fomc_blackout"]),
                "sign_gate_only_pass": sign_gate,
                "sign_gate_plus_blackout_pass": bool(sign_gate and row["no_jump"] and not row["fomc_blackout"]),
            }
        )
    return pd.DataFrame(rows).sort_values(["asset", "signal_time"]).reset_index(drop=True)


def split_train_test(signals: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_parts = []
    test_parts = []
    for _, grp in signals.groupby("asset", sort=True):
        cut = max(1, int(len(grp) * TRAIN_FRACTION))
        train_parts.append(grp.iloc[:cut])
        test_parts.append(grp.iloc[cut:])
    train = pd.concat(train_parts, ignore_index=True) if train_parts else pd.DataFrame(columns=signals.columns)
    test = pd.concat(test_parts, ignore_index=True) if test_parts else pd.DataFrame(columns=signals.columns)
    return train, test


def simulate_variant(frame: pd.DataFrame, signals: pd.DataFrame, variant: str, hold_bars: int = HOLD_BARS) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    last_exit_idx = -1
    pass_col = {
        "baseline": None,
        "sign_gate_only": "sign_gate_only_pass",
        "sign_gate_plus_blackout": "sign_gate_plus_blackout_pass",
    }[variant]

    for _, sig in signals.iterrows():
        idx = int(sig["signal_idx"])
        if idx <= last_exit_idx:
            continue
        if pass_col and not bool(sig[pass_col]):
            rows.append({**sig.to_dict(), "variant": variant, "retention_flag": 0, "verdict": "veto"})
            continue
        entry_idx = idx + 1
        if entry_idx >= len(frame):
            continue
        entry_px = float(frame.iloc[entry_idx]["open"])
        if not np.isfinite(entry_px) or entry_px <= 0:
            continue
        exit_idx = min(len(frame) - 1, entry_idx + hold_bars)
        window = frame.iloc[entry_idx : exit_idx + 1]
        early = frame.iloc[entry_idx : min(len(frame), entry_idx + 4)]
        actual_exit_idx = exit_idx
        exit_reason = "time_stop"
        fail_level = float(sig["breakout_anchor"] + 0.30 * sig["atr14"])
        for j in range(entry_idx, exit_idx + 1):
            if float(frame.iloc[j]["close"]) > fail_level:
                actual_exit_idx = j
                exit_reason = "anchor_reclaim"
                break
        exit_px = float(frame.iloc[actual_exit_idx]["close"])
        gross = entry_px / exit_px - 1.0
        rows.append(
            {
                **sig.to_dict(),
                "variant": variant,
                "retention_flag": 1,
                "verdict": "entry",
                "entry_idx": entry_idx,
                "entry_time": frame.iloc[entry_idx]["timestamp"],
                "entry_price": entry_px,
                "exit_idx": actual_exit_idx,
                "exit_time": frame.iloc[actual_exit_idx]["timestamp"],
                "exit_price": exit_px,
                "gross_ret": gross,
                "false_follow_4bars": int((early["close"] > float(sig["signal_close"])).any()) if len(early) else 0,
                "best_move": float(entry_px / window["low"].min() - 1.0) if len(window) else np.nan,
                "mae": float(entry_px / window["high"].max() - 1.0) if len(window) else np.nan,
                "exit_reason": exit_reason,
            }
        )
        last_exit_idx = actual_exit_idx
    return pd.DataFrame(rows)


def summarize_variant(trades: pd.DataFrame, variant: str, cost_bps: float) -> pd.DataFrame:
    work = trades[trades["variant"] == variant].copy()
    if work.empty:
        return pd.DataFrame()
    rows: list[dict[str, object]] = []
    for asset, grp in work.groupby("asset", sort=True):
        entries = grp[grp["verdict"] == "entry"].copy()
        net_total = float(net_ret(entries["gross_ret"], cost_bps).sum()) if not entries.empty else 0.0
        rows.append(
            {
                "asset": asset,
                "variant": variant,
                "cost_bps_per_side": cost_bps,
                "signal_count": int(len(grp)),
                "trade_count": int(len(entries)),
                "trade_retention": float(len(entries) / len(grp)) if len(grp) else np.nan,
                "mean_total_return": net_total,
                "mean_avg_net_ret": float(net_ret(entries["gross_ret"], cost_bps).mean()) if not entries.empty else np.nan,
                "win_rate": float((net_ret(entries["gross_ret"], cost_bps) > 0).mean()) if not entries.empty else np.nan,
                "false_follow_4bars": float(entries["false_follow_4bars"].mean()) if not entries.empty else np.nan,
                "jump_blackout_share": float((entries["no_jump"] == False).mean()) if not entries.empty else np.nan,
                "fomc_blackout_share": float(entries["fomc_blackout"].mean()) if not entries.empty else np.nan,
                "neutral_sign_share": float((entries["predictor_sign"] == 0).mean()) if not entries.empty else np.nan,
            }
        )
    return pd.DataFrame(rows)


def overall_summary(asset_summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    if asset_summary.empty:
        return pd.DataFrame()
    for (variant, cost), grp in asset_summary.groupby(["variant", "cost_bps_per_side"], sort=False):
        rows.append(
            {
                "variant": variant,
                "cost_bps_per_side": cost,
                "mean_total_return": float(grp["mean_total_return"].mean()),
                "positive_asset_ratio": float((grp["mean_total_return"] > 0).mean()),
                "mean_trades": float(grp["trade_count"].mean()),
                "mean_retention": float(grp["trade_retention"].mean()),
                "mean_avg_net_ret": float(grp["mean_avg_net_ret"].mean()),
                "mean_win_rate": float(grp["win_rate"].mean()),
                "mean_false_follow_4bars": float(grp["false_follow_4bars"].mean()),
                "mean_jump_blackout_share": float(grp["jump_blackout_share"].mean()),
                "mean_fomc_blackout_share": float(grp["fomc_blackout_share"].mean()),
            }
        )
    return pd.DataFrame(rows)


def decide_verdict(overall: pd.DataFrame) -> tuple[str, str]:
    base = overall[(overall["variant"] == "baseline") & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    sign = overall[(overall["variant"] == "sign_gate_only") & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    both = overall[(overall["variant"] == "sign_gate_plus_blackout") & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    if base.empty or sign.empty or both.empty:
        return "inconclusive", "样本不足，无法给出诚实 verdict。"
    base_r = float(base.iloc[0]["mean_total_return"])
    base_ret = float(base.iloc[0]["mean_retention"])
    sign_r = float(sign.iloc[0]["mean_total_return"])
    sign_ret = float(sign.iloc[0]["mean_retention"])
    both_r = float(both.iloc[0]["mean_total_return"])
    both_ret = float(both.iloc[0]["mean_retention"])
    if both_r > base_r and both_ret >= max(0.55, base_ret * 0.75):
        return "keep_p1", "`sign_gate_plus_blackout` 在不把样本砍塌的前提下优于 baseline，保留 P1。"
    if sign_r > base_r and sign_ret >= max(0.55, base_ret * 0.75):
        return "keep_p1", "`sign_gate_only` 有 honest uplift，但 blackout 叠加没带来额外帮助，保留 P1。"
    return "park", "改善主要来自砍样本或 blackout 过度过滤，没有形成足够诚实的 desk uplift。"


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    signal_catalog_parts: list[pd.DataFrame] = []
    train_state_parts: list[pd.DataFrame] = []
    test_trade_parts: list[pd.DataFrame] = []

    for asset, symbol in ASSETS.items():
        frame = build_frame(asset, symbol)
        signals = collect_signals(frame, asset)
        signal_catalog_parts.append(signals)
        train, test = split_train_test(signals)
        train_state_parts.append(
            pd.DataFrame(
                [{
                    "asset": asset,
                    "train_signals": len(train),
                    "test_signals": len(test),
                    "train_non_neutral_share": float((train["predictor_sign"] != 0).mean()) if len(train) else np.nan,
                    "test_non_neutral_share": float((test["predictor_sign"] != 0).mean()) if len(test) else np.nan,
                    "train_no_jump_share": float(train["no_jump"].mean()) if len(train) else np.nan,
                    "test_no_jump_share": float(test["no_jump"].mean()) if len(test) else np.nan,
                }]
            )
        )
        for variant in ["baseline", "sign_gate_only", "sign_gate_plus_blackout"]:
            trades = simulate_variant(frame, test, variant)
            test_trade_parts.append(trades)

    signal_catalog = pd.concat(signal_catalog_parts, ignore_index=True) if signal_catalog_parts else pd.DataFrame()
    train_test_state = pd.concat(train_state_parts, ignore_index=True) if train_state_parts else pd.DataFrame()
    trade_log = pd.concat(test_trade_parts, ignore_index=True) if test_trade_parts else pd.DataFrame()

    asset_summaries = []
    for cost in COSTS:
        for variant in ["baseline", "sign_gate_only", "sign_gate_plus_blackout"]:
            asset_summaries.append(summarize_variant(trade_log, variant, cost))
    asset_summary = pd.concat([df for df in asset_summaries if not df.empty], ignore_index=True) if asset_summaries else pd.DataFrame()
    overall = overall_summary(asset_summary)

    verdict, verdict_reason = decide_verdict(overall)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    summary = {
        "generated_at_utc": ts,
        "archetype": "breakout_short",
        "execution": "signal当根及之前数据 + next-bar open + no-overlap + hold 8 bars",
        "pair_lookback": PAIR_LOOKBACK,
        "jump_sigma": JUMP_SIGMA,
        "fomc_blackout_hours": BLACKOUT_HOURS,
        "verdict": verdict,
        "verdict_reason": verdict_reason,
    }

    signal_catalog.to_csv(ART_DIR / "signal_catalog.csv", index=False)
    train_test_state.to_csv(ART_DIR / "train_test_gate_summary.csv", index=False)
    trade_log.to_csv(ART_DIR / "trade_log.csv", index=False)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    (ART_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    base6 = overall[(overall["variant"] == "baseline") & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    sign6 = overall[(overall["variant"] == "sign_gate_only") & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    both6 = overall[(overall["variant"] == "sign_gate_plus_blackout") & (overall["cost_bps_per_side"] == PRIMARY_COST)]

    verdict_class = "good" if verdict == "keep_p1" else "bad"
    title = "Rank 118 / intraday sign-asymmetry + no-jump / no-FOMC gate · clean replication"
    body = f"""
    <h1>{escape(title)}</h1>
    <p class="muted">生成时间：{escape(ts)} · 只测 1 条 archetype：<code>breakout_short</code></p>
    <div class="card">
      <p><strong>本轮 hard verdict：</strong><span class=\"{verdict_class}\">{escape(verdict)}</span></p>
      <p>{escape(verdict_reason)}</p>
      <p class="muted">固定口径：<code>signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars</code>。比较三臂：<code>baseline</code> / <code>sign_gate_only</code> / <code>sign_gate_plus_blackout</code>。</p>
    </div>
    <div class="card">
      <h2>一句人话</h2>
      <p>这轮不是在找新 alpha，而是在问：<strong>breakout-short follow-up 能不能靠 intraday sign-asymmetry + no-jump / no-FOMC 变得更诚实</strong>。</p>
      <p>{escape(verdict_reason)}</p>
    </div>
    <div class="card">
      <h2>6 bps/side 总览</h2>
      {render_table(overall[overall['cost_bps_per_side'] == PRIMARY_COST].copy(), percent_cols={'mean_total_return','positive_asset_ratio','mean_retention','mean_avg_net_ret','mean_win_rate','mean_false_follow_4bars','mean_jump_blackout_share','mean_fomc_blackout_share'})}
    </div>
    <div class="card">
      <h2>按资产明细</h2>
      {render_table(asset_summary[asset_summary['cost_bps_per_side'] == PRIMARY_COST].copy(), percent_cols={'trade_retention','mean_total_return','mean_avg_net_ret','win_rate','false_follow_4bars','jump_blackout_share','fomc_blackout_share','neutral_sign_share'})}
    </div>
    <div class="card">
      <h2>训练/测试 gate 状态</h2>
      {render_table(train_test_state.copy(), percent_cols={'train_non_neutral_share','test_non_neutral_share','train_no_jump_share','test_no_jump_share'})}
    </div>
    <div class="card">
      <h2>产物</h2>
      <ul>
        <li><a href="../../artifacts/scout_rank118_intraday_sign_asymmetry_15m/overall_summary.csv">overall_summary.csv</a></li>
        <li><a href="../../artifacts/scout_rank118_intraday_sign_asymmetry_15m/asset_summary.csv">asset_summary.csv</a></li>
        <li><a href="../../artifacts/scout_rank118_intraday_sign_asymmetry_15m/trade_log.csv">trade_log.csv</a></li>
        <li><a href="../../artifacts/scout_rank118_intraday_sign_asymmetry_15m/signal_catalog.csv">signal_catalog.csv</a></li>
      </ul>
    </div>
    """
    write_html(SITE_DIR / "report.html", title, body)

    reading_body = f"""
    <h1>{escape(title)}</h1>
    <p class="muted">Rank 118 的最小 clean replication。主问题：这条 gate 是否比 baseline 更诚实，而不是单纯靠少做单改善外观。</p>
    <div class="card">
      <p><strong>结论：</strong><span class=\"{verdict_class}\">{escape(verdict)}</span></p>
      <p>{escape(verdict_reason)}</p>
      <p>实现口径：把每个 15m slot 的历史 <code>recent_ret_4 × forward_ret_4</code> 作为 sign-asymmetry proxy；对当前 short 候选，只在 <code>expected_next_dir = short</code> 时放行，再叠 <code>no_jump</code> 与 <code>no-FOMC</code> blackout。</p>
      <p><a href="../../factors/scout_rank118_intraday_sign_asymmetry_15m/report.html">查看完整 factor 报告</a></p>
    </div>
    <div class="card">
      {render_table(overall[overall['cost_bps_per_side'] == PRIMARY_COST].copy(), percent_cols={'mean_total_return','positive_asset_ratio','mean_retention','mean_avg_net_ret','mean_win_rate','mean_false_follow_4bars','mean_jump_blackout_share','mean_fomc_blackout_share'})}
    </div>
    """
    write_html(READING_PATH, title, reading_body)

    print(json.dumps(summary, ensure_ascii=False))
    if not base6.empty:
        print("baseline_6bps", base6.to_dict(orient="records")[0])
    if not sign6.empty:
        print("sign_gate_only_6bps", sign6.to_dict(orient="records")[0])
    if not both6.empty:
        print("sign_gate_plus_blackout_6bps", both6.to_dict(orient="records")[0])


if __name__ == "__main__":
    main()
