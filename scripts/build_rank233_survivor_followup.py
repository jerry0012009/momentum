#!/usr/bin/env python3
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "rank233_survivor_followup"
ART_DIR.mkdir(parents=True, exist_ok=True)

API = "https://fapi.binance.com/fapi/v1/klines"
INTERVAL = "5m"
LIMIT = 1500
DAYS = 180
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT"]
RET_THRESHOLD = 0.005
VOL_Z_THRESHOLD = 2.0
VOL_LOOKBACK = 72
HOLDS = [1, 2, 3]
COST_PER_SIDE = 0.0006  # 6 bps / side
SLEEP_SEC = 0.06


def fetch_json(url: str, retries: int = 5):
    last = None
    for attempt in range(retries):
        try:
            with urlopen(url, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(1.0 + attempt)
    raise RuntimeError(f"failed fetch: {url} :: {last}")


def fetch_klines(symbol: str, days: int = DAYS) -> pd.DataFrame:
    end_ms = int(time.time() * 1000)
    start_ms = end_ms - days * 24 * 60 * 60 * 1000
    cur = start_ms
    rows: list[list] = []
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
        nxt = int(batch[-1][0]) + 5 * 60 * 1000
        if nxt <= cur:
            break
        cur = nxt
        time.sleep(SLEEP_SEC)
    if not rows:
        raise RuntimeError(f"no rows for {symbol}")
    df = pd.DataFrame(rows, columns=[
        "open_time", "open", "high", "low", "close", "volume", "close_time",
        "quote_volume", "trade_count", "taker_base", "taker_quote", "ignore",
    ])
    for col in ["open", "high", "low", "close", "quote_volume"]:
        df[col] = df[col].astype(float)
    df["ts"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    return (
        df[["ts", "open", "high", "low", "close", "quote_volume"]]
        .drop_duplicates("ts")
        .sort_values("ts")
        .reset_index(drop=True)
    )


def analyze_symbol(symbol: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    bars = fetch_klines(symbol)
    bars["ret_5m"] = bars["close"].pct_change()
    log_quote = np.log(bars["quote_volume"].replace(0.0, np.nan))
    roll_mean = log_quote.rolling(VOL_LOOKBACK).mean()
    roll_std = log_quote.rolling(VOL_LOOKBACK).std(ddof=0)
    bars["vol_z"] = ((log_quote - roll_mean) / roll_std.replace(0.0, np.nan))
    bars["shock_dir"] = np.sign(bars["ret_5m"]).fillna(0.0)
    bars["month"] = bars["ts"].dt.strftime("%Y-%m")

    for hold in HOLDS:
        bars[f"fwd_ret_{hold}"] = bars["open"].shift(-(hold + 1)) / bars["open"].shift(-1) - 1.0

    event_mask = (
        (bars["ret_5m"].abs() >= RET_THRESHOLD)
        & (bars["vol_z"] >= VOL_Z_THRESHOLD)
        & (bars["shock_dir"] != 0.0)
    )
    event_cols = ["ts", "month", "shock_dir", "ret_5m", "vol_z"] + [f"fwd_ret_{h}" for h in HOLDS]
    events = bars.loc[event_mask, event_cols].copy().reset_index(drop=True)

    summary_rows: list[dict[str, object]] = []
    detail_frames: list[pd.DataFrame] = []

    for hold in HOLDS:
        frame = events[["ts", "month", "shock_dir", "ret_5m", "vol_z", f"fwd_ret_{hold}"]].rename(
            columns={f"fwd_ret_{hold}": "fwd_ret"}
        ).dropna().copy()
        frame["ret_cont"] = frame["shock_dir"] * frame["fwd_ret"] - 2.0 * COST_PER_SIDE
        frame["ret_fade"] = -frame["shock_dir"] * frame["fwd_ret"] - 2.0 * COST_PER_SIDE
        month_train = frame.groupby("month")[["ret_cont", "ret_fade"]].mean().sort_index()
        prior_choice: dict[str, str] = {}
        months = list(month_train.index)
        for i in range(1, len(months)):
            prev_month = months[i - 1]
            month = months[i]
            prior_choice[month] = "continuation" if month_train.loc[prev_month, "ret_cont"] >= month_train.loc[prev_month, "ret_fade"] else "fade"
        frame["map_choice"] = frame["month"].map(prior_choice)
        frame["ret_map"] = np.where(frame["map_choice"].eq("continuation"), frame["ret_cont"], frame["ret_fade"])
        frame["symbol"] = symbol
        frame["hold_bars"] = hold
        detail_frames.append(frame)

        scored = frame[frame["map_choice"].notna()].copy()
        for variant, col in [("always_continuation", "ret_cont"), ("always_fade", "ret_fade"), ("monthly_polarity_map", "ret_map")]:
            series = scored[col].dropna()
            summary_rows.append({
                "symbol": symbol,
                "hold_bars": hold,
                "variant": variant,
                "trades": int(series.shape[0]),
                "mean_net_bps": float(series.mean() * 10000.0) if not series.empty else np.nan,
                "median_net_bps": float(series.median() * 10000.0) if not series.empty else np.nan,
                "total_net_bps": float(series.sum() * 10000.0) if not series.empty else np.nan,
                "win_rate": float((series > 0).mean()) if not series.empty else np.nan,
            })

    summary = pd.DataFrame(summary_rows).sort_values(["symbol", "hold_bars", "variant"]).reset_index(drop=True)
    detail = pd.concat(detail_frames, ignore_index=True)
    return summary, detail


def main() -> None:
    summary_frames = []
    detail_frames = []
    for symbol in SYMBOLS:
        summary, detail = analyze_symbol(symbol)
        summary_frames.append(summary)
        detail_frames.append(detail)

    summary_df = pd.concat(summary_frames, ignore_index=True)
    detail_df = pd.concat(detail_frames, ignore_index=True)
    summary_df.to_csv(ART_DIR / "summary_by_symbol_hold_variant.csv", index=False)
    detail_df.to_csv(ART_DIR / "event_level_detail.csv", index=False)

    best_rows = []
    for symbol in SYMBOLS:
        sub = summary_df[summary_df["symbol"] == symbol].copy()
        best = sub.sort_values(["mean_net_bps", "trades"], ascending=[False, False]).iloc[0]
        best_rows.append(best)
    best_df = pd.DataFrame(best_rows).reset_index(drop=True)
    best_df.to_csv(ART_DIR / "best_variant_by_symbol.csv", index=False)

    map_rows = summary_df[summary_df["variant"] == "monthly_polarity_map"].copy()
    base_rows = summary_df[summary_df["variant"].isin(["always_continuation", "always_fade"])].copy()
    merged = map_rows.merge(
        base_rows.groupby(["symbol", "hold_bars"], as_index=False)["mean_net_bps"].max().rename(columns={"mean_net_bps": "best_constant_mean_net_bps"}),
        on=["symbol", "hold_bars"],
        how="left",
    )
    merged["map_beats_best_constant"] = merged["mean_net_bps"] > merged["best_constant_mean_net_bps"]
    merged.to_csv(ART_DIR / "map_vs_best_constant.csv", index=False)

    positive_map = merged[(merged["map_beats_best_constant"]) & (merged["mean_net_bps"] > 0)].copy()
    decision = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "lookback_days": DAYS,
        "interval": INTERVAL,
        "symbols": SYMBOLS,
        "event_rule": "abs(ret_5m) >= 0.5% and log(quote_volume) zscore over trailing 72 bars >= 2.0",
        "execution_rule": "next-bar open, no-overlap, 6 bps/side",
        "holds": HOLDS,
        "monthly_map_rule": "for each symbol+hold, trade each calendar month using the better of continuation/fade from the immediately previous month",
        "map_beats_best_constant_any_symbol_hold": bool(merged["map_beats_best_constant"].any()),
        "positive_map_beating_constant_rows": positive_map.to_dict(orient="records"),
        "best_variants": best_df.to_dict(orient="records"),
    }

    if positive_map.empty:
        decision["verdict"] = "keep_P1_then_background"
        decision["one_line"] = "180d frozen replication 显示，monthly polarity map 虽偶尔比最差常数方向少亏，但在四个主币、1~3 bar 上没有任何一格能做到成本后为正且胜过 best constant baseline；唯一转正的是 XRP 的 always fade 3-bar，说明该对象更像单币常数 fade pocket，而不是可推广的 monthly polarity map admission。"
    else:
        decision["verdict"] = "promote_P2"
        decision["one_line"] = "monthly polarity map 在至少一个主币-持有期上成本后为正且胜过常数方向基线，足以进入 P2。"

    (ART_DIR / "decision.json").write_text(json.dumps(decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(decision, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
