#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urlencode
from urllib.request import urlopen

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank228_dc_overshoot_survivor_followup"
ART_DIR.mkdir(parents=True, exist_ok=True)

API = "https://fapi.binance.com/fapi/v1/klines"
INTERVAL = "1m"
LOOKBACK_DAYS = 90
LIMIT = 1500
SYMBOLS = ["BTCUSDT", "ETHUSDT"]
THRESHOLDS_BPS = [10, 15, 20, 30, 40]
ALPHAS = [0.4, 0.6, 0.8]
COSTS_BPS = [4.0, 6.0]
ABNORMAL_VOL_Z = 2.5
ABNORMAL_BAR_Z = 2.5
MIN_TRADES = 40


@dataclass
class Trade:
    symbol: str
    theta_bps: int
    alpha: float
    exit_mode: str
    entry_ts: pd.Timestamp
    exit_ts: pd.Timestamp
    hold_minutes: int
    gross_bps: float
    net4_bps: float
    net6_bps: float
    veto_blocked: int
    abnormal_at_entry: int


def fetch_json(url: str, retries: int = 5) -> list:
    last = None
    for attempt in range(retries):
        try:
            with urlopen(url, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(1.0 + attempt)
    raise RuntimeError(f"failed fetch: {url} :: {last}")


def fetch_klines(symbol: str, days: int = LOOKBACK_DAYS) -> pd.DataFrame:
    end_ms = int(time.time() * 1000)
    start_ms = end_ms - days * 24 * 60 * 60 * 1000
    rows: list[list] = []
    cur = start_ms
    while cur < end_ms:
        qs = urlencode({
            "symbol": symbol,
            "interval": INTERVAL,
            "startTime": cur,
            "endTime": end_ms,
            "limit": LIMIT,
        })
        batch = fetch_json(f"{API}?{qs}")
        if not batch:
            break
        rows.extend(batch)
        nxt = int(batch[-1][0]) + 60_000
        if nxt <= cur:
            break
        cur = nxt
        time.sleep(0.08)
    if not rows:
        raise RuntimeError(f"no rows for {symbol}")
    df = pd.DataFrame(rows, columns=[
        "open_time","open","high","low","close","volume","close_time",
        "quote_volume","trade_count","taker_base","taker_quote","ignore"
    ])
    for c in ["open","high","low","close","volume","quote_volume"]:
        df[c] = df[c].astype(float)
    df["ts"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df = df[["ts","open","high","low","close","volume"]].drop_duplicates("ts").sort_values("ts").reset_index(drop=True)
    return df


def add_abnormal_proxy(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ret1"] = out["close"].pct_change().fillna(0.0)
    out["abs_ret1"] = out["ret1"].abs()
    rv60 = out["ret1"].rolling(60).std() * math.sqrt(60)
    rv_base = rv60.rolling(24 * 60, min_periods=240).mean()
    rv_std = rv60.rolling(24 * 60, min_periods=240).std()
    out["rv60"] = rv60
    out["rv60_z"] = ((rv60 - rv_base) / rv_std.replace(0, np.nan)).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    bar_base = out["abs_ret1"].rolling(24 * 60, min_periods=240).mean()
    bar_std = out["abs_ret1"].rolling(24 * 60, min_periods=240).std()
    out["bar_z"] = ((out["abs_ret1"] - bar_base) / bar_std.replace(0, np.nan)).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    out["abnormal"] = ((out["rv60_z"] >= ABNORMAL_VOL_Z) | (out["bar_z"] >= ABNORMAL_BAR_Z)).astype(int)
    return out


def simulate_symbol(df: pd.DataFrame, symbol: str, theta_bps: int, alpha: float, use_veto: bool) -> tuple[list[Trade], dict[str, int]]:
    theta = theta_bps / 10_000.0
    exit_thresh = alpha * theta
    closes = df["close"].to_numpy()
    ts = df["ts"].to_numpy()
    abnormal = df["abnormal"].to_numpy()

    trough = closes[0]
    trough_idx = 0
    pending_long = False
    pending_from_idx = -1
    in_pos = False
    entry_idx = -1
    entry_px = 0.0
    trades: list[Trade] = []
    blocked = 0
    suppressed = 0
    peak = closes[0]

    for i in range(1, len(df)):
        px = closes[i]

        if not in_pos:
            if px < trough:
                trough = px
                trough_idx = i
                pending_long = False
            elif px >= trough * (1.0 + theta):
                pending_long = True
                pending_from_idx = i

            if pending_long and i + 1 < len(df):
                if use_veto and abnormal[i] == 1:
                    blocked += 1
                    pending_long = False
                    trough = min(trough, px)
                    continue
                in_pos = True
                entry_idx = i + 1
                entry_px = closes[entry_idx]
                peak = entry_px
                pending_long = False
                suppressed += int(use_veto and abnormal[i] == 1)
                continue
        else:
            peak = max(peak, px)
            reverse_hit = px <= peak * (1.0 - exit_thresh)
            abnormal_hit = use_veto and abnormal[i] == 1
            if reverse_hit or abnormal_hit or i == len(df) - 1:
                exit_px = px
                gross_bps = (exit_px / entry_px - 1.0) * 10_000.0
                cost4 = gross_bps - 8.0
                cost6 = gross_bps - 12.0
                trades.append(Trade(
                    symbol=symbol,
                    theta_bps=theta_bps,
                    alpha=alpha,
                    exit_mode="alpha_reverse_or_abnormal_veto" if use_veto else "alpha_reverse_only",
                    entry_ts=pd.Timestamp(ts[entry_idx]),
                    exit_ts=pd.Timestamp(ts[i]),
                    hold_minutes=int(i - entry_idx),
                    gross_bps=float(gross_bps),
                    net4_bps=float(cost4),
                    net6_bps=float(cost6),
                    veto_blocked=0,
                    abnormal_at_entry=int(abnormal[entry_idx]),
                ))
                in_pos = False
                trough = px
                trough_idx = i
                pending_long = False

    meta = {"blocked_entries": blocked, "suppressed": suppressed}
    return trades, meta


def summarize(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame()
    def q05(x: pd.Series) -> float:
        return float(x.quantile(0.05))
    def q50(x: pd.Series) -> float:
        return float(x.quantile(0.50))
    def hit(x: pd.Series) -> float:
        return float((x > 0).mean())
    return (
        trades.groupby(["symbol","theta_bps","alpha","exit_mode"], as_index=False)
        .agg(
            trades=("gross_bps", "size"),
            gross_mean_bps=("gross_bps", "mean"),
            gross_med_bps=("gross_bps", q50),
            gross_p05_bps=("gross_bps", q05),
            net4_mean_bps=("net4_bps", "mean"),
            net4_p05_bps=("net4_bps", q05),
            net4_hit_rate=("net4_bps", hit),
            net6_mean_bps=("net6_bps", "mean"),
            net6_p05_bps=("net6_bps", q05),
            net6_hit_rate=("net6_bps", hit),
            mean_hold_min=("hold_minutes", "mean"),
        )
        .sort_values(["symbol","net6_mean_bps","net4_mean_bps"], ascending=[True, False, False])
        .reset_index(drop=True)
    )


def pick_best(summary: pd.DataFrame, symbol: str, exit_mode: str) -> pd.Series | None:
    sub = summary[(summary["symbol"] == symbol) & (summary["exit_mode"] == exit_mode) & (summary["trades"] >= MIN_TRADES)].copy()
    if sub.empty:
        return None
    sub = sub.sort_values(["net6_mean_bps", "net4_mean_bps", "gross_mean_bps"], ascending=False)
    return sub.iloc[0]


def main() -> None:
    datasets: dict[str, pd.DataFrame] = {}
    for symbol in SYMBOLS:
        df = add_abnormal_proxy(fetch_klines(symbol))
        datasets[symbol] = df
        df.to_csv(ART_DIR / f"{symbol.lower()}_1m.csv", index=False)

    all_trades: list[Trade] = []
    meta_rows = []
    for symbol, df in datasets.items():
        for theta in THRESHOLDS_BPS:
            for alpha in ALPHAS:
                for use_veto in [False, True]:
                    trades, meta = simulate_symbol(df, symbol, theta, alpha, use_veto)
                    all_trades.extend(trades)
                    meta_rows.append({
                        "symbol": symbol,
                        "theta_bps": theta,
                        "alpha": alpha,
                        "exit_mode": "alpha_reverse_or_abnormal_veto" if use_veto else "alpha_reverse_only",
                        **meta,
                    })

    trades_df = pd.DataFrame([t.__dict__ for t in all_trades])
    if trades_df.empty:
        raise RuntimeError("no trades generated")
    trades_df.to_csv(ART_DIR / "trades.csv", index=False)
    pd.DataFrame(meta_rows).to_csv(ART_DIR / "meta.csv", index=False)

    summary = summarize(trades_df)
    summary.to_csv(ART_DIR / "summary.csv", index=False)

    comparisons = []
    for symbol in SYMBOLS:
        base = pick_best(summary, symbol, "alpha_reverse_only")
        veto = pick_best(summary, symbol, "alpha_reverse_or_abnormal_veto")
        row = {"symbol": symbol}
        if base is not None:
            for k in ["theta_bps","alpha","trades","gross_mean_bps","net4_mean_bps","net6_mean_bps","gross_p05_bps","net4_p05_bps","net6_p05_bps","mean_hold_min"]:
                row[f"base_{k}"] = float(base[k]) if isinstance(base[k], (np.floating, float, int, np.integer)) else base[k]
        if veto is not None:
            for k in ["theta_bps","alpha","trades","gross_mean_bps","net4_mean_bps","net6_mean_bps","gross_p05_bps","net4_p05_bps","net6_p05_bps","mean_hold_min"]:
                row[f"veto_{k}"] = float(veto[k]) if isinstance(veto[k], (np.floating, float, int, np.integer)) else veto[k]
        if base is not None and veto is not None:
            row["veto_tail_improve_net6_bps"] = float(veto["net6_p05_bps"] - base["net6_p05_bps"])
            row["veto_mean_improve_net6_bps"] = float(veto["net6_mean_bps"] - base["net6_mean_bps"])
            row["veto_tail_improve_net4_bps"] = float(veto["net4_p05_bps"] - base["net4_p05_bps"])
        comparisons.append(row)
    cmp_df = pd.DataFrame(comparisons)
    cmp_df.to_csv(ART_DIR / "best_variant_comparison.csv", index=False)

    pocket_rows = []
    for symbol in SYMBOLS:
        sub = summary[(summary["symbol"] == symbol) & (summary["trades"] >= MIN_TRADES)].copy()
        for _, r in sub.iterrows():
            pocket_rows.append({
                "symbol": symbol,
                "theta_bps": int(r.theta_bps),
                "alpha": float(r.alpha),
                "exit_mode": r.exit_mode,
                "trades": int(r.trades),
                "net4_positive": bool(r.net4_mean_bps > 0),
                "net6_positive": bool(r.net6_mean_bps > 0),
                "tail_better_than_minus20bps_net6": bool(r.net6_p05_bps > -20),
                "quality_pass": bool((r.net6_mean_bps > 0) and (r.net6_hit_rate >= 0.5)),
            })
    pocket_df = pd.DataFrame(pocket_rows)
    pocket_df.to_csv(ART_DIR / "pockets.csv", index=False)

    positive_net6 = summary[(summary["trades"] >= MIN_TRADES) & (summary["net6_mean_bps"] > 0)].copy()
    tail_improvers = cmp_df[(cmp_df.get("veto_tail_improve_net6_bps", pd.Series(dtype=float)) > 0)] if not cmp_df.empty else pd.DataFrame()

    decision = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "lookback_days": LOOKBACK_DAYS,
        "symbols": SYMBOLS,
        "thresholds_bps": THRESHOLDS_BPS,
        "alphas": ALPHAS,
        "costs_bps_per_side": COSTS_BPS,
        "positive_net6_variants": int(len(positive_net6)),
        "best_comparison": comparisons,
    }

    if positive_net6.empty:
        decision["verdict"] = "keep_P1_then_background"
        decision["one_line"] = "BTC/ETH 的 1m bar-proxy DC overshoot continuation 在 4~6 bps/side 后没有留下足够稳定的正 pocket；abnormal veto 虽偶尔改善左尾，但不足以把对象送进 P2。"
    else:
        # still require both assets have a positive net6 pocket and veto improves tail on at least one asset
        by_symbol = positive_net6.groupby("symbol").size().to_dict()
        veto_help = False
        if not cmp_df.empty and "veto_tail_improve_net6_bps" in cmp_df.columns:
            veto_help = bool((cmp_df["veto_tail_improve_net6_bps"] > 0).any())
        if all(by_symbol.get(sym, 0) > 0 for sym in SYMBOLS) and veto_help:
            decision["verdict"] = "promote_P2"
            decision["one_line"] = "BTC/ETH 两个资产都留下了至少一个 6 bps/side 后仍为正的 bar-proxy DC pocket，且 abnormal veto 对左尾有实质改善，可升 P2。"
        else:
            decision["verdict"] = "keep_P1_then_background"
            decision["one_line"] = "即使个别参数点在单资产上偶有薄正值，也没有形成 BTC/ETH 同时站稳、且 abnormal veto 明显压尾的可迁移 pocket；不升 P2。"

    (ART_DIR / "decision.json").write_text(json.dumps(decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(decision, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
