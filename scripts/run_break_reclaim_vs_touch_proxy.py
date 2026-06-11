#!/usr/bin/env python3
from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "reports" / "artifacts" / "quant_digests" / "2026-03-23_break_reclaim_vs_touch_retest"
BINANCE_KLINES = "https://api.binance.com/api/v3/klines"
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
INTERVAL = "15m"
LOOKBACK_DAYS = 120
BAR_LIMIT = 1000
WARMUP_BARS = 260
FORWARD_BARS = 8
TOUCH_LOOKBACK = 4
CUSHION_ATR_MULT = 0.20
FIRST_HIT_ATR_MULT = 1.0


@dataclass
class SummaryRow:
    symbol: str
    side: str
    pattern: str
    n: int
    ret4_bps: float
    ret8_bps: float
    win8: float
    continue_share: float
    fail_share: float
    timeout_share: float
    exp_score: float
    median_mfe_bps: float
    median_mae_bps: float


def fetch_klines(symbol: str, bars_needed: int) -> pd.DataFrame:
    rows: list[list] = []
    end_time: int | None = None

    while len(rows) < bars_needed:
        params = {"symbol": symbol, "interval": INTERVAL, "limit": BAR_LIMIT}
        if end_time is not None:
            params["endTime"] = end_time
        resp = requests.get(BINANCE_KLINES, params=params, timeout=30)
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        rows = batch + rows
        end_time = int(batch[0][0]) - 1
        if len(batch) < BAR_LIMIT:
            break
        time.sleep(0.12)

    cols = [
        "open_time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "quote_asset_volume",
        "trades",
        "taker_buy_base",
        "taker_buy_quote",
        "ignore",
    ]
    df = pd.DataFrame(rows, columns=cols).drop_duplicates("open_time").sort_values("open_time").reset_index(drop=True)
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)
    df["ts"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    return df


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for span in (20, 50, 200):
        out[f"ema{span}"] = out["close"].ewm(span=span, adjust=False).mean()
    prev_close = out["close"].shift(1)
    tr = pd.concat(
        [
            out["high"] - out["low"],
            (out["high"] - prev_close).abs(),
            (out["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    out["atr14"] = tr.ewm(alpha=1 / 14, adjust=False).mean()
    return out


def compute_event_masks(df: pd.DataFrame) -> dict[tuple[str, str], pd.Series]:
    trend_long = (df["ema20"] > df["ema50"]) & (df["ema50"] > df["ema200"])
    trend_short = (df["ema20"] < df["ema50"]) & (df["ema50"] < df["ema200"])
    cushion = CUSHION_ATR_MULT * df["atr14"]

    long_touch = trend_long & (df["low"] <= df["ema20"] + cushion) & (df["close"] > df["ema20"]) & (df["close"].shift(1) > df["ema20"].shift(1))
    short_touch = trend_short & (df["high"] >= df["ema20"] - cushion) & (df["close"] < df["ema20"]) & (df["close"].shift(1) < df["ema20"].shift(1))
    for k in range(1, TOUCH_LOOKBACK + 1):
        long_touch &= df["close"].shift(k) > df["ema20"].shift(k)
        short_touch &= df["close"].shift(k) < df["ema20"].shift(k)

    long_reclaim = trend_long & (df["close"].shift(1) < df["ema20"].shift(1)) & (df["close"] > df["ema20"])
    short_reclaim = trend_short & (df["close"].shift(1) > df["ema20"].shift(1)) & (df["close"] < df["ema20"])

    return {
        ("long", "touch_bounce"): long_touch.fillna(False),
        ("long", "break_reclaim"): long_reclaim.fillna(False),
        ("short", "touch_bounce"): short_touch.fillna(False),
        ("short", "break_reclaim"): short_reclaim.fillna(False),
    }


def first_hit_verdict(entry: float, atr: float, path: pd.DataFrame, side: str) -> str:
    k = FIRST_HIT_ATR_MULT
    if side == "long":
        cont_level = entry + k * atr
        fail_level = entry - k * atr
        for _, row in path.iterrows():
            hit_cont = row["high"] >= cont_level
            hit_fail = row["low"] <= fail_level
            if hit_cont and hit_fail:
                return "continue" if row["close"] >= entry else "fail"
            if hit_cont:
                return "continue"
            if hit_fail:
                return "fail"
        return "timeout"

    cont_level = entry - k * atr
    fail_level = entry + k * atr
    for _, row in path.iterrows():
        hit_cont = row["low"] <= cont_level
        hit_fail = row["high"] >= fail_level
        if hit_cont and hit_fail:
            return "continue" if row["close"] <= entry else "fail"
        if hit_cont:
            return "continue"
        if hit_fail:
            return "fail"
    return "timeout"


def evaluate_events(df: pd.DataFrame, symbol: str, side: str, pattern: str, mask: pd.Series) -> tuple[pd.DataFrame, SummaryRow] | None:
    event_rows = []
    idxs = np.flatnonzero(mask.to_numpy())
    sign = 1.0 if side == "long" else -1.0

    for i in idxs:
        if i + FORWARD_BARS >= len(df):
            continue
        entry_bar = df.iloc[i]
        path = df.iloc[i + 1 : i + 1 + FORWARD_BARS].copy()
        entry = float(entry_bar["close"])
        atr = float(entry_bar["atr14"])
        verdict = first_hit_verdict(entry, atr, path, side)
        close4 = float(df.iloc[i + 4]["close"])
        close8 = float(df.iloc[i + FORWARD_BARS]["close"])

        if side == "long":
            ret4 = close4 / entry - 1.0
            ret8 = close8 / entry - 1.0
            mfe = path["high"].max() / entry - 1.0
            mae = path["low"].min() / entry - 1.0
        else:
            ret4 = entry / close4 - 1.0
            ret8 = entry / close8 - 1.0
            mfe = entry / path["low"].min() - 1.0
            mae = entry / path["high"].max() - 1.0

        event_rows.append(
            {
                "symbol": symbol,
                "ts": entry_bar["ts"].isoformat(),
                "side": side,
                "pattern": pattern,
                "entry": entry,
                "ema20": float(entry_bar["ema20"]),
                "ema50": float(entry_bar["ema50"]),
                "ema200": float(entry_bar["ema200"]),
                "atr14": atr,
                "ret4_bps": ret4 * 10000.0,
                "ret8_bps": ret8 * 10000.0,
                "verdict": verdict,
                "mfe_bps": mfe * 10000.0,
                "mae_bps": mae * 10000.0,
            }
        )

    if not event_rows:
        return None

    events = pd.DataFrame(event_rows)
    summary = SummaryRow(
        symbol=symbol,
        side=side,
        pattern=pattern,
        n=int(len(events)),
        ret4_bps=float(events["ret4_bps"].mean()),
        ret8_bps=float(events["ret8_bps"].mean()),
        win8=float((events["ret8_bps"] > 0).mean()),
        continue_share=float((events["verdict"] == "continue").mean()),
        fail_share=float((events["verdict"] == "fail").mean()),
        timeout_share=float((events["verdict"] == "timeout").mean()),
        exp_score=float((events["verdict"] == "continue").mean() - (events["verdict"] == "fail").mean()),
        median_mfe_bps=float(events["mfe_bps"].median()),
        median_mae_bps=float(events["mae_bps"].median()),
    )
    return events, summary


def weighted_group_summary(df: pd.DataFrame, group_cols: Iterable[str]) -> pd.DataFrame:
    rows = []
    for keys, sub in df.groupby(list(group_cols), dropna=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        weights = sub["n"].astype(float)
        row = dict(zip(group_cols, keys))
        row["n"] = int(sub["n"].sum())
        for col in [
            "ret4_bps",
            "ret8_bps",
            "win8",
            "continue_share",
            "fail_share",
            "timeout_share",
            "exp_score",
            "median_mfe_bps",
            "median_mae_bps",
        ]:
            row[col] = float(np.average(sub[col], weights=weights))
        rows.append(row)
    return pd.DataFrame(rows)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    bars_needed = LOOKBACK_DAYS * 24 * 4 + WARMUP_BARS

    all_events = []
    summaries: list[SummaryRow] = []
    for symbol in SYMBOLS:
        df = add_indicators(fetch_klines(symbol, bars_needed)).iloc[WARMUP_BARS:].reset_index(drop=True)
        for (side, pattern), mask in compute_event_masks(df).items():
            evaluated = evaluate_events(df, symbol, side, pattern, mask)
            if evaluated is None:
                continue
            events, summary = evaluated
            all_events.append(events)
            summaries.append(summary)

    events_df = pd.concat(all_events, ignore_index=True)
    summary_df = pd.DataFrame([asdict(s) for s in summaries])
    pooled_by_side_pattern = weighted_group_summary(summary_df, ["side", "pattern"])
    pooled_by_pattern = weighted_group_summary(summary_df, ["pattern"])

    events_df.to_csv(OUT_DIR / "events.csv", index=False)
    summary_df.to_csv(OUT_DIR / "summary_by_symbol_side_pattern.csv", index=False)
    pooled_by_side_pattern.to_csv(OUT_DIR / "summary_by_side_pattern.csv", index=False)
    pooled_by_pattern.to_csv(OUT_DIR / "summary_by_pattern.csv", index=False)

    payload = {
        "config": {
            "symbols": SYMBOLS,
            "interval": INTERVAL,
            "lookback_days": LOOKBACK_DAYS,
            "forward_bars": FORWARD_BARS,
            "touch_lookback": TOUCH_LOOKBACK,
            "cushion_atr_mult": CUSHION_ATR_MULT,
            "first_hit_atr_mult": FIRST_HIT_ATR_MULT,
        },
        "summary_by_symbol_side_pattern": summary_df.to_dict(orient="records"),
        "summary_by_side_pattern": pooled_by_side_pattern.to_dict(orient="records"),
        "summary_by_pattern": pooled_by_pattern.to_dict(orient="records"),
    }
    (OUT_DIR / "summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("[ok] wrote", OUT_DIR)
    print(summary_df.to_string(index=False))
    print("\n[pooled side x pattern]")
    print(pooled_by_side_pattern.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
