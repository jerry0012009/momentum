from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional

import numpy as np
import pandas as pd
import requests

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
INTERVAL = "15m"
LOOKBACK_DAYS = 120
ATR_N = 14
BREAKOUT_N = 20
MAX_RETEST_BARS = 8
MAX_OUTCOME_BARS = 8
RETEST_ATR_MULT = 0.35
FAIL_ATR = 0.60
CONT_ATR = 0.90
OUT_DIR = Path("/root/clawd/jerry/momentum/reports/artifacts/quant_digests/bounce_polarity_proxy_20260322")
OUT_DIR.mkdir(parents=True, exist_ok=True)
BASE_URL = "https://api.binance.com/api/v3/klines"
MS = 1000


def fetch_klines(symbol: str, interval: str, start_ms: int, end_ms: int) -> pd.DataFrame:
    rows = []
    cur = start_ms
    session = requests.Session()
    while cur < end_ms:
        r = session.get(
            BASE_URL,
            params={
                "symbol": symbol,
                "interval": interval,
                "startTime": cur,
                "endTime": end_ms,
                "limit": 1000,
            },
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        if not data:
            break
        rows.extend(data)
        last_open = data[-1][0]
        # advance by one bar
        cur = last_open + 15 * 60 * 1000
        if len(data) < 1000:
            break
    if not rows:
        raise RuntimeError(f"no rows for {symbol}")
    cols = [
        "open_time","open","high","low","close","volume","close_time",
        "quote_asset_volume","num_trades","taker_buy_base","taker_buy_quote","ignore",
    ]
    df = pd.DataFrame(rows, columns=cols)
    for c in ["open","high","low","close","volume"]:
        df[c] = df[c].astype(float)
    df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df = df[["timestamp","open","high","low","close","volume"]].drop_duplicates("timestamp").reset_index(drop=True)
    return df


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    prev_close = df["close"].shift(1)
    tr = pd.concat([
        (df["high"] - df["low"]),
        (df["high"] - prev_close).abs(),
        (df["low"] - prev_close).abs(),
    ], axis=1).max(axis=1)
    df = df.copy()
    df["atr"] = tr.rolling(ATR_N).mean()
    df["roll_high"] = df["high"].shift(1).rolling(BREAKOUT_N).max()
    df["roll_low"] = df["low"].shift(1).rolling(BREAKOUT_N).min()
    candle_range = (df["high"] - df["low"]).replace(0, np.nan)
    df["body_pct"] = (df["close"] - df["open"]).abs() / candle_range
    df["clv"] = (df["close"] - df["low"]) / candle_range
    return df


def find_events(df: pd.DataFrame, symbol: str) -> List[Dict]:
    events: List[Dict] = []
    i = BREAKOUT_N + ATR_N + 1
    n = len(df)
    while i < n - MAX_RETEST_BARS - MAX_OUTCOME_BARS - 1:
        row = df.iloc[i]
        atr = row["atr"]
        if not np.isfinite(atr) or atr <= 0:
            i += 1
            continue
        direction = None
        level = None
        if row["close"] > row["roll_high"] and row["body_pct"] >= 0.5 and row["clv"] >= 0.7:
            direction = "long"
            level = float(row["roll_high"])
        elif row["close"] < row["roll_low"] and row["body_pct"] >= 0.5 and row["clv"] <= 0.3:
            direction = "short"
            level = float(row["roll_low"])
        if direction is None:
            i += 1
            continue

        touch_idx: Optional[int] = None
        bounce_idx: Optional[int] = None
        retest_extreme: Optional[float] = None
        for j in range(i + 1, min(n, i + 1 + MAX_RETEST_BARS)):
            rj = df.iloc[j]
            tol = atr * RETEST_ATR_MULT
            if direction == "long":
                if rj["close"] < level - FAIL_ATR * atr:
                    break
                touched = (rj["low"] <= level + tol) and (rj["high"] >= level - tol)
                if touched:
                    if touch_idx is None:
                        touch_idx = j
                        retest_extreme = float(rj["low"])
                    else:
                        retest_extreme = min(retest_extreme, float(rj["low"]))
                    if rj["close"] > level:
                        bounce_idx = j
                        break
            else:
                if rj["close"] > level + FAIL_ATR * atr:
                    break
                touched = (rj["high"] >= level - tol) and (rj["low"] <= level + tol)
                if touched:
                    if touch_idx is None:
                        touch_idx = j
                        retest_extreme = float(rj["high"])
                    else:
                        retest_extreme = max(retest_extreme, float(rj["high"]))
                    if rj["close"] < level:
                        bounce_idx = j
                        break
        if bounce_idx is None:
            i += 1
            continue

        bounce = df.iloc[bounce_idx]
        entry = float(bounce["close"])
        outcome = "timeout"
        decision_bars = None
        for k in range(bounce_idx + 1, min(n, bounce_idx + 1 + MAX_OUTCOME_BARS)):
            rk = df.iloc[k]
            if direction == "long":
                cont = rk["high"] >= entry + CONT_ATR * atr
                fail = rk["low"] <= entry - FAIL_ATR * atr
            else:
                cont = rk["low"] <= entry - CONT_ATR * atr
                fail = rk["high"] >= entry + FAIL_ATR * atr
            if cont and fail:
                # pessimistic ordering: if same bar hits both, count as fail
                outcome = "fail"
                decision_bars = k - bounce_idx
                break
            if fail:
                outcome = "fail"
                decision_bars = k - bounce_idx
                break
            if cont:
                outcome = "continue"
                decision_bars = k - bounce_idx
                break

        same_body = bool(bounce["close"] > bounce["open"]) if direction == "long" else bool(bounce["close"] < bounce["open"])
        doji = math.isclose(float(bounce["close"]), float(bounce["open"]), rel_tol=0.0, abs_tol=1e-12)
        events.append({
            "symbol": symbol,
            "direction": direction,
            "breakout_ts": df.iloc[i]["timestamp"].isoformat(),
            "bounce_ts": bounce["timestamp"].isoformat(),
            "level": level,
            "entry": entry,
            "atr": float(atr),
            "breakout_body_pct": float(row["body_pct"]),
            "breakout_clv": float(row["clv"]),
            "retest_bars": bounce_idx - i,
            "bounce_body_pct": float(abs(bounce["close"] - bounce["open"]) / max(bounce["high"] - bounce["low"], 1e-12)),
            "bounce_same_direction_body": same_body,
            "bounce_doji": doji,
            "outcome": outcome,
            "decision_bars": decision_bars,
            "retest_extreme": retest_extreme,
        })
        i = bounce_idx + 1
    return events


def summarize(df: pd.DataFrame, by: List[str]) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    g = df.groupby(by, dropna=False)
    out = g.size().rename("n").reset_index()
    for label in ["continue", "fail", "timeout"]:
        share = g["outcome"].apply(lambda s, lab=label: (s == lab).mean()).reset_index(drop=True)
        out[f"{label}_share"] = share
    out["median_retest_bars"] = g["retest_bars"].median().reset_index(drop=True)
    out["median_bounce_body_pct"] = g["bounce_body_pct"].median().reset_index(drop=True)
    out["mean_decision_bars"] = g["decision_bars"].mean().reset_index(drop=True)
    return out


def main():
    end_ms = int(pd.Timestamp.utcnow().timestamp() * 1000)
    start_ms = end_ms - LOOKBACK_DAYS * 24 * 60 * 60 * 1000
    all_events: List[Dict] = []
    for symbol in SYMBOLS:
        df = fetch_klines(symbol, INTERVAL, start_ms, end_ms)
        df = add_features(df)
        all_events.extend(find_events(df, symbol))
    ev = pd.DataFrame(all_events)
    if ev.empty:
        raise RuntimeError("no events")
    ev.to_csv(OUT_DIR / "events.csv", index=False)

    pooled = summarize(ev, ["bounce_same_direction_body"])
    side = summarize(ev, ["direction", "bounce_same_direction_body"])
    symbol_side = summarize(ev, ["symbol", "direction", "bounce_same_direction_body"])
    pooled.to_csv(OUT_DIR / "summary_by_bounce_polarity.csv", index=False)
    side.to_csv(OUT_DIR / "side_summary.csv", index=False)
    symbol_side.to_csv(OUT_DIR / "symbol_side_summary.csv", index=False)

    md = {
        "symbols": SYMBOLS,
        "interval": INTERVAL,
        "lookback_days": LOOKBACK_DAYS,
        "atr_n": ATR_N,
        "breakout_n": BREAKOUT_N,
        "max_retest_bars": MAX_RETEST_BARS,
        "max_outcome_bars": MAX_OUTCOME_BARS,
        "retest_atr_mult": RETEST_ATR_MULT,
        "fail_atr": FAIL_ATR,
        "cont_atr": CONT_ATR,
        "n_events": int(len(ev)),
        "n_same_body": int(ev["bounce_same_direction_body"].sum()),
        "n_other_body": int((~ev["bounce_same_direction_body"]).sum()),
        "doji_share": float(ev["bounce_doji"].mean()),
    }
    (OUT_DIR / "metadata.json").write_text(json.dumps(md, indent=2), encoding="utf-8")
    print(json.dumps(md, indent=2))
    print("\nPooled\n", pooled.to_string(index=False))
    print("\nSide\n", side.to_string(index=False))


if __name__ == "__main__":
    main()
