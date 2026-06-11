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
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank116_ema_respect_memory_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank116_ema_respect_memory_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank116_ema_respect_memory_clean_replication.html"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
TRAIN_FRACTION = 0.60
HOLD_BARS = 8
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0]
SCORE_WINDOW = 14
TOUCH_BAND_PCT = 0.005
SCORE_THRESHOLD = 2
MAX_DIST_ATR = 0.75
MIN_DEPTH_ATR = -0.80
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


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_bars(symbol, asset)
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema15"] = df["close"].ewm(span=15, adjust=False).mean()
    df["ema_slope"] = df["ema9"].pct_change(3)
    df["atr14"] = compute_atr(df)
    df["swing_high_30"] = df["high"].rolling(30, min_periods=30).max().shift(1)
    df["swing_low_30"] = df["low"].rolling(30, min_periods=30).min().shift(1)
    swing_range = (df["swing_high_30"] - df["swing_low_30"]).clip(lower=EPS)
    df["fib_618"] = df["swing_high_30"] - 0.618 * swing_range
    df["fib_500"] = df["swing_high_30"] - 0.500 * swing_range
    df["base_signal"] = (
        df["fib_618"].notna()
        & df["atr14"].notna()
        & (df["ema9"] > df["ema15"])
        & (df["ema_slope"] > 0)
        & (df["close"] > df["fib_618"])
        & (df["close"].shift(1) <= df["fib_618"].shift(1))
        & (df["low"] <= df["fib_618"] + 0.2 * df["atr14"])
        & (df["close"] > df["fib_500"])
    ).fillna(False)

    touch_band = TOUCH_BAND_PCT
    touch_hit = (
        df["low"].between(df["ema9"] * (1.0 - touch_band), df["ema9"] * (1.0 + touch_band), inclusive="both")
        & (df["close"] > df["ema9"])
        & (df["close"] > df["open"])
    ).fillna(False)
    df["ema_touch_hit"] = touch_hit.astype(int)
    df["ema_respect_score"] = df["ema_touch_hit"].shift(1).rolling(SCORE_WINDOW, min_periods=SCORE_WINDOW).sum()
    df["signal_dist_atr"] = ((df["close"] - df["ema9"]).abs() / df["atr14"]).replace([np.inf, -np.inf], np.nan)
    df["signal_depth_atr"] = ((df["low"] - df["ema9"]) / df["atr14"]).replace([np.inf, -np.inf], np.nan)
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
        score = float(row["ema_respect_score"]) if pd.notna(row["ema_respect_score"]) else np.nan
        score_only = bool(pd.notna(score) and score >= SCORE_THRESHOLD)
        corridor_ok = bool(
            score_only
            and pd.notna(row["signal_dist_atr"])
            and pd.notna(row["signal_depth_atr"])
            and float(row["signal_dist_atr"]) <= MAX_DIST_ATR
            and float(row["signal_depth_atr"]) >= MIN_DEPTH_ATR
        )
        rows.append(
            {
                "asset": asset,
                "signal_idx": int(idx),
                "signal_time": row["timestamp"],
                "signal_close": float(row["close"]),
                "fib_500": float(row["fib_500"]),
                "atr14": float(row["atr14"]),
                "ema_respect_score": score,
                "signal_dist_atr": float(row["signal_dist_atr"]) if pd.notna(row["signal_dist_atr"]) else np.nan,
                "signal_depth_atr": float(row["signal_depth_atr"]) if pd.notna(row["signal_depth_atr"]) else np.nan,
                "score_only_pass": score_only,
                "score_plus_corridor_pass": corridor_ok,
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
    if variant == "baseline":
        pass_col = None
    elif variant == "score_only":
        pass_col = "score_only_pass"
    else:
        pass_col = "score_plus_corridor_pass"

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
        for j in range(entry_idx, exit_idx + 1):
            if float(frame.iloc[j]["close"]) < float(sig["fib_500"]):
                actual_exit_idx = j
                exit_reason = "fib50_fail"
                break
        exit_px = float(frame.iloc[actual_exit_idx]["close"])
        gross = exit_px / entry_px - 1.0
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
                "false_follow_4bars": int((early["close"] < float(sig["signal_close"])).any()) if len(early) else 0,
                "best_move": float(window["high"].max() / entry_px - 1.0) if len(window) else np.nan,
                "mae": float((window["low"] / entry_px - 1.0).min()) if len(window) else np.nan,
                "gate_conflict": int(bool(sig["score_only_pass"]) != bool(sig["score_plus_corridor_pass"])),
                "exit_reason": exit_reason,
            }
        )
        last_exit_idx = actual_exit_idx
    return pd.DataFrame(rows)


def summarize_variant(trades: pd.DataFrame, variant: str, cost_bps: float) -> pd.DataFrame:
    work = trades[trades["variant"] == variant].copy()
    if work.empty:
        return pd.DataFrame()
    entered = work[work["retention_flag"] == 1].copy()
    if not entered.empty:
        entered["net_ret"] = net_ret(entered["gross_ret"], cost_bps)
    signal_counts = work.groupby("asset").size().rename("signals_total")
    rows = []
    for asset in signal_counts.index:
        asset_all = work[work["asset"] == asset]
        asset_entered = entered[entered["asset"] == asset]
        total_signals = int(signal_counts.loc[asset])
        total_return = float((1.0 + asset_entered["net_ret"].dropna()).prod() - 1.0) if not asset_entered.empty else 0.0
        rows.append(
            {
                "asset": asset,
                "variant": variant,
                "cost_bps_per_side": float(cost_bps),
                "signals_total": total_signals,
                "entries": int(asset_entered.shape[0]),
                "retention": float(asset_entered.shape[0] / total_signals) if total_signals else np.nan,
                "mean_total_return": total_return,
                "avg_trade_return": float(asset_entered["net_ret"].mean()) if not asset_entered.empty else np.nan,
                "false_follow_4bars": float(asset_entered["false_follow_4bars"].mean()) if not asset_entered.empty else np.nan,
                "avg_best_move": float(asset_entered["best_move"].mean()) if not asset_entered.empty else np.nan,
                "avg_mae": float(asset_entered["mae"].mean()) if not asset_entered.empty else np.nan,
            }
        )
    return pd.DataFrame(rows)


def overall_summary(asset_summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (variant, cost_bps), grp in asset_summary.groupby(["variant", "cost_bps_per_side"], sort=False):
        rows.append(
            {
                "variant": variant,
                "cost_bps_per_side": float(cost_bps),
                "mean_total_return": float(grp["mean_total_return"].mean()),
                "mean_avg_trade_return": float(grp["avg_trade_return"].mean()),
                "mean_retention": float(grp["retention"].mean()),
                "mean_false_follow_4bars": float(grp["false_follow_4bars"].mean()),
                "mean_entries": float(grp["entries"].mean()),
                "positive_asset_ratio": float((grp["mean_total_return"] > 0).mean()),
            }
        )
    return pd.DataFrame(rows)


def train_test_gate_summary(train_signals: pd.DataFrame, test_signals: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for split_name, df in [("train", train_signals), ("test", test_signals)]:
        for asset, grp in df.groupby("asset", sort=True):
            total = len(grp)
            rows.append(
                {
                    "split": split_name,
                    "asset": asset,
                    "signals": total,
                    "score_only_rate": float(grp["score_only_pass"].mean()) if total else np.nan,
                    "score_plus_corridor_rate": float(grp["score_plus_corridor_pass"].mean()) if total else np.nan,
                    "avg_score": float(grp["ema_respect_score"].mean()) if total else np.nan,
                    "avg_signal_dist_atr": float(grp["signal_dist_atr"].mean()) if total else np.nan,
                }
            )
    return pd.DataFrame(rows)


def render_verdict(primary_overall: pd.DataFrame) -> tuple[str, str]:
    base = primary_overall[primary_overall["variant"] == "baseline"].iloc[0]
    score = primary_overall[primary_overall["variant"] == "score_only"].iloc[0]
    corridor = primary_overall[primary_overall["variant"] == "score_plus_corridor"].iloc[0]
    uplift = float(score["mean_total_return"] - base["mean_total_return"])
    ff_delta = float(base["mean_false_follow_4bars"] - score["mean_false_follow_4bars"])
    retention = float(score["mean_retention"])
    corridor_delta = float(corridor["mean_total_return"] - score["mean_total_return"])

    if uplift > 0 and ff_delta > 0.03 and retention >= 0.60:
        verdict = "keep_P1 / weak shared admission context"
        summary = (
            "`EMA respect memory score` 在这次 fib-retest clean-room 里有一点 honest uplift："
            "它能在不把 retention 压塌的前提下，略微改善成本后 desk 结果与 false-follow。"
            "但 uplift 仍偏弱，只配保留为轻量 context，不够升到 P2。"
        )
    else:
        verdict = "park / evidence pool"
        summary = (
            "这次最小 clean replication 没把 `EMA respect memory score` 变成更硬的共享 admission upgrade："
            "若有改善，也主要偏向轻微减亏或样本重排；而 `ATR corridor` 对照组继续证明自己更像过筛过度。"
        )
    if corridor_delta < 0:
        summary += " `score + corridor` 相比 `score-only` 继续退步，支持“保留 memory score、不要默认升级 corridor 硬门”的 intake 结论。"
    return verdict, summary


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    frames = {asset: build_frame(asset, symbol) for asset, symbol in ASSETS.items()}
    signals = pd.concat([collect_signals(frame, asset) for asset, frame in frames.items()], ignore_index=True)
    signals = signals.sort_values(["asset", "signal_time"]).reset_index(drop=True)
    train_signals, test_signals = split_train_test(signals)

    trade_logs = []
    for asset, frame in frames.items():
        asset_test = test_signals[test_signals["asset"] == asset].copy()
        for variant in ["baseline", "score_only", "score_plus_corridor"]:
            trade_logs.append(simulate_variant(frame, asset_test, variant))
    trade_log = pd.concat(trade_logs, ignore_index=True)

    asset_summaries = []
    for cost in COSTS:
        for variant in ["baseline", "score_only", "score_plus_corridor"]:
            asset_summaries.append(summarize_variant(trade_log, variant, cost))
    asset_summary = pd.concat(asset_summaries, ignore_index=True)
    overall = overall_summary(asset_summary)
    gate_summary = train_test_gate_summary(train_signals, test_signals)

    primary_overall = overall[overall["cost_bps_per_side"] == PRIMARY_COST].copy()
    verdict, verdict_summary = render_verdict(primary_overall)

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "rank": 116,
        "candidate": "EMA respect memory score",
        "base_archetype": "fib_retest_long",
        "sample": "BTC/ETH/SOL 120d 15m local cache",
        "execution": "next-bar open + no-overlap + hold 8 bars",
        "frozen_params": {
            "score_window": SCORE_WINDOW,
            "touch_band_pct": TOUCH_BAND_PCT,
            "score_threshold": SCORE_THRESHOLD,
            "max_dist_atr": MAX_DIST_ATR,
            "min_depth_atr": MIN_DEPTH_ATR,
        },
        "verdict": verdict,
    }

    signals.to_csv(ART_DIR / "signal_catalog.csv", index=False)
    trade_log.to_csv(ART_DIR / "trade_log.csv", index=False)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    gate_summary.to_csv(ART_DIR / "train_test_gate_summary.csv", index=False)
    (ART_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    primary_rows = primary_overall[["variant", "mean_total_return", "mean_retention", "mean_false_follow_4bars", "mean_entries", "positive_asset_ratio"]].copy()
    primary_rows["variant"] = primary_rows["variant"].map({
        "baseline": "baseline_direct_entry",
        "score_only": "ema_respect_score_only",
        "score_plus_corridor": "score_plus_corridor_control",
    })

    body = f"""
    <h1>Rank 116 / EMA respect memory score · 最小 clean replication</h1>
    <p class='muted'>生成时间：{escape(summary['generated_at_utc'])}</p>

    <div class='card'>
      <h2>本轮 hard verdict</h2>
      <p><strong>{escape(verdict)}</strong></p>
      <p>{escape(verdict_summary)}</p>
      <ul>
        <li>base archetype：<code>fib_retest_long</code></li>
        <li>样本：<code>BTC/ETH/SOL 120d 15m</code></li>
        <li>执行：<code>signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars</code></li>
        <li>冻结参数：<code>score_window=14</code> / <code>touch_band=0.5%</code> / <code>score>=2</code></li>
        <li>对照组：<code>score + dist&lt;=0.75 ATR + depth&gt;=-0.8 ATR</code></li>
      </ul>
    </div>

    <div class='card'>
      <h2>desk 级测试段摘要（6 bps/side）</h2>
      {render_table(primary_rows, percent_cols={'mean_total_return','mean_retention','mean_false_follow_4bars','positive_asset_ratio'}, digits_cols={'mean_entries':2})}
    </div>

    <div class='card'>
      <h2>分资产摘要</h2>
      {render_table(asset_summary[asset_summary['cost_bps_per_side'] == PRIMARY_COST][['asset','variant','entries','retention','mean_total_return','avg_trade_return','false_follow_4bars']], percent_cols={'retention','mean_total_return','avg_trade_return','false_follow_4bars'})}
    </div>

    <div class='card'>
      <h2>gate coverage（train/test）</h2>
      {render_table(gate_summary, percent_cols={'score_only_rate','score_plus_corridor_rate'})}
    </div>
    """
    write_html(SITE_DIR / "report.html", "Rank 116 EMA respect memory clean replication", body)

    reading_body = f"""
    <h1>Rank 116 / EMA respect memory score · clean replication note</h1>
    <div class='card'>
      <p><strong>一句话：</strong>{escape(verdict_summary)}</p>
      <p>这轮不再停留在 source intake，而是把 `recent EMA respect score` 直接挂到一条最小 fib-retest clean-room 上，比较：</p>
      <ul>
        <li><code>baseline_direct_entry</code></li>
        <li><code>ema_respect_score_only</code></li>
        <li><code>score_plus_corridor_control</code></li>
      </ul>
      <p>如果 `score-only` 只是靠砍样本减亏、而不能更诚实地降低 false-follow，那么它仍只配停在 weak context；如果再叠 `ATR corridor` 继续退步，就说明 intake 的“不要默认升硬门”判断是对的。</p>
    </div>
    <div class='card'>
      <h2>6 bps/side 总结</h2>
      {render_table(primary_rows, percent_cols={'mean_total_return','mean_retention','mean_false_follow_4bars','positive_asset_ratio'})}
    </div>
    <div class='card'>
      <h2>产物</h2>
      <ul>
        <li><a href='../../factors/scout_rank116_ema_respect_memory_15m/report.html'>reader-facing factor report</a></li>
        <li><code>reports/artifacts/scout_rank116_ema_respect_memory_15m/overall_summary.csv</code></li>
        <li><code>reports/artifacts/scout_rank116_ema_respect_memory_15m/asset_summary.csv</code></li>
        <li><code>reports/artifacts/scout_rank116_ema_respect_memory_15m/trade_log.csv</code></li>
      </ul>
    </div>
    """
    write_html(READING_PATH, "Rank 116 EMA respect memory clean replication", reading_body)


if __name__ == "__main__":
    main()
