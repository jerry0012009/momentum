#!/usr/bin/env python3
"""
V1.6a / Phase2a sensitivity test for the V4 1h return threshold.

The goal is to answer whether the current ret_1h >= 1% gate is stable when
the event filter and trail 2% exit are kept fixed.

Methodology intentionally matches the existing Phase2a historical artifacts:
- event overlay: rank<=20, 24h ret>=30%, 24h quote volume>=5M
- V4 ret_1h: close-to-close pct_change
- V4 volume baseline: rolling 20h quote-volume mean including current bar
- V4 signal cooldown: 4 bars within each symbol's full history
- execution: first V4 signal after each event in (event_ts, event_ts+48h]
- exit: trail 2%, max hold 48h, net of 13bps base round-trip cost
- slippage stress: subtract 2 * one-way slippage from the base net return
"""
from __future__ import annotations

import glob
import json
import time
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "data" / "binance_vision_1h_v1_6" / "klines"
EVENT_FILE = (
    ROOT
    / "reports"
    / "artifacts"
    / "binance_event_study_v1_6a_realtime_event_overlay"
    / "events_rank20_ret30_vol5m.csv"
)
OUT = ROOT / "reports" / "artifacts" / "binance_event_study_v1_6a_v4_ret_sensitivity"
OUT.mkdir(parents=True, exist_ok=True)

RET_THRESHOLDS = [0.005, 0.01, 0.015, 0.02, 0.03, 0.05]
VOL_THRESH = 3.0
VOL_WINDOW = 20
SIGNAL_COOLDOWN_BARS = 4
EVENT_WINDOW_HOURS = 48
TRAIL_PCT = 0.02
MAX_HOLD = 48
BASE_COST = 0.0013
SLIPPAGE_ONE_WAY = [0.0, 0.003]


def load_candles(symbol: str) -> pd.DataFrame | None:
    files = sorted(glob.glob(str(CACHE_DIR / symbol / f"{symbol}-1h-*.zip")))
    if not files:
        return None

    frames = []
    for fp in files:
        try:
            with zipfile.ZipFile(fp) as zf:
                names = [n for n in zf.namelist() if n.endswith(".csv")]
                if not names:
                    continue
                with zf.open(names[0]) as fh:
                    raw = pd.read_csv(
                        fh,
                        usecols=lambda c: c
                        in {"open_time", "open", "high", "low", "close", "quote_volume"},
                    )
        except Exception:
            continue

        if raw.empty:
            continue
        df = pd.DataFrame(
            {
                "ts": pd.to_datetime(
                    pd.to_numeric(raw["open_time"], errors="coerce"), unit="ms", utc=True
                ),
                "open": pd.to_numeric(raw["open"], errors="coerce"),
                "high": pd.to_numeric(raw["high"], errors="coerce"),
                "low": pd.to_numeric(raw["low"], errors="coerce"),
                "close": pd.to_numeric(raw["close"], errors="coerce"),
                "quote_volume": pd.to_numeric(raw["quote_volume"], errors="coerce"),
            }
        ).dropna(subset=["ts", "close", "quote_volume"])
        frames.append(df)

    if not frames:
        return None

    out = pd.concat(frames, ignore_index=True)
    out = out.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    if len(out) < VOL_WINDOW + MAX_HOLD + 5:
        return None
    out["ret_1h"] = out["close"].pct_change()
    out["vol_ma20"] = out["quote_volume"].rolling(VOL_WINDOW, min_periods=VOL_WINDOW // 2).mean()
    out["vol_ratio"] = out["quote_volume"] / out["vol_ma20"]
    out["ts_ns"] = out["ts"].dt.as_unit("ns").astype("int64")
    return out


def cooldown_positions(pos: np.ndarray, min_gap: int) -> list[int]:
    kept = []
    prev = -10**9
    for i in pos:
        ii = int(i)
        if ii - prev >= min_gap:
            kept.append(ii)
            prev = ii
    return kept


def detect_v4_by_threshold(candles: pd.DataFrame) -> dict[float, pd.DataFrame]:
    out: dict[float, pd.DataFrame] = {}
    valid_base = (
        np.isfinite(candles["vol_ratio"].to_numpy("float64"))
        & np.isfinite(candles["ret_1h"].to_numpy("float64"))
        & (candles["vol_ratio"].to_numpy("float64") >= VOL_THRESH)
    )
    for thr in RET_THRESHOLDS:
        valid = valid_base & (candles["ret_1h"].to_numpy("float64") >= thr)
        pos = np.where(valid)[0]
        kept = cooldown_positions(pos, SIGNAL_COOLDOWN_BARS)
        sig = candles.iloc[kept][["ts", "ts_ns", "close", "ret_1h", "vol_ratio", "quote_volume"]].copy()
        sig = sig.rename(columns={"close": "entry_price"})
        out[thr] = sig.reset_index(drop=True)
    return out


def simulate_trail(candles: pd.DataFrame, entry_idx: int, entry_price: float) -> tuple[float, int, str]:
    future_end = min(entry_idx + MAX_HOLD, len(candles) - 1)
    if entry_idx < 0 or future_end <= entry_idx or entry_price <= 0:
        return np.nan, 0, "no_data"

    highs = candles["high"].to_numpy("float64")
    lows = candles["low"].to_numpy("float64")
    closes = candles["close"].to_numpy("float64")
    peak = entry_price

    for j in range(entry_idx + 1, future_end + 1):
        if highs[j] > peak:
            peak = highs[j]
        stop = peak * (1.0 - TRAIL_PCT)
        if lows[j] <= stop:
            return (stop / entry_price - 1.0) - BASE_COST, j - entry_idx, "trail"

    return (closes[future_end] / entry_price - 1.0) - BASE_COST, future_end - entry_idx, "timeout"


def pf(x: np.ndarray) -> float:
    gains = x[x > 0].sum()
    losses = -x[x < 0].sum()
    if losses <= 0:
        return float("inf") if gains > 0 else float("nan")
    return float(gains / losses)


def stats(rets: np.ndarray) -> dict:
    rets = np.asarray(rets, dtype="float64")
    rets = rets[np.isfinite(rets)]
    if len(rets) == 0:
        return {
            "n": 0,
            "mean": np.nan,
            "median": np.nan,
            "winrate": np.nan,
            "pf": np.nan,
            "p5": np.nan,
            "p25": np.nan,
            "p75": np.nan,
            "p95": np.nan,
        }
    return {
        "n": int(len(rets)),
        "mean": float(np.mean(rets)),
        "median": float(np.median(rets)),
        "winrate": float(np.mean(rets > 0)),
        "pf": pf(rets),
        "p5": float(np.percentile(rets, 5)),
        "p25": float(np.percentile(rets, 25)),
        "p75": float(np.percentile(rets, 75)),
        "p95": float(np.percentile(rets, 95)),
    }


def main() -> None:
    t0 = time.time()
    events = pd.read_csv(EVENT_FILE)
    events["event_ts"] = pd.to_datetime(events["event_ts"], utc=True)
    events = events.sort_values(["symbol", "event_ts"]).reset_index(drop=True)
    print(f"[events] {len(events):,} events, {events.symbol.nunique()} symbols")
    print(f"[thresholds] {', '.join(f'{x*100:.1f}%' for x in RET_THRESHOLDS)}")

    all_trades = []
    yearly_rows = []
    processed = 0

    for symbol, evs in events.groupby("symbol", sort=True):
        candles = load_candles(symbol)
        if candles is None or candles.empty:
            continue
        processed += 1
        if processed % 50 == 0:
            print(f"  processed {processed:>3d} symbols, trades so far={len(all_trades):,}, elapsed={time.time()-t0:.0f}s")

        candle_ts_ns = candles["ts_ns"].to_numpy("int64")
        signals_by_thr = detect_v4_by_threshold(candles)

        for thr, sigs in signals_by_thr.items():
            if sigs.empty:
                continue
            sig_ts_ns = sigs["ts_ns"].to_numpy("int64")
            for _, ev in evs.iterrows():
                ev_ts = pd.Timestamp(ev["event_ts"])
                lo = np.int64(ev_ts.value)
                hi = np.int64((ev_ts + pd.Timedelta(hours=EVENT_WINDOW_HOURS)).value)

                left = int(np.searchsorted(sig_ts_ns, lo, side="right"))
                if left >= len(sig_ts_ns) or sig_ts_ns[left] > hi:
                    continue

                sig = sigs.iloc[left]
                entry_ns = np.int64(sig["ts_ns"])
                entry_idx = int(np.searchsorted(candle_ts_ns, entry_ns, side="left"))
                if entry_idx >= len(candle_ts_ns) or candle_ts_ns[entry_idx] != entry_ns:
                    continue

                ret, hold_h, exit_type = simulate_trail(candles, entry_idx, float(sig["entry_price"]))
                if not np.isfinite(ret):
                    continue

                all_trades.append(
                    {
                        "threshold": thr,
                        "threshold_label": f"{thr*100:.1f}%",
                        "symbol": symbol,
                        "event_ts": ev_ts,
                        "signal_ts": sig["ts"],
                        "lag_hours": (pd.Timestamp(sig["ts"]) - ev_ts).total_seconds() / 3600.0,
                        "year": int(pd.Timestamp(sig["ts"]).year),
                        "event_ret24": float(ev.get("event_ret24", np.nan)),
                        "event_rank_ret24": float(ev.get("event_rank_ret24", np.nan)),
                        "event_vol24": float(ev.get("event_vol24", np.nan)),
                        "entry_price": float(sig["entry_price"]),
                        "ret_1h": float(sig["ret_1h"]),
                        "vol_ratio": float(sig["vol_ratio"]),
                        "trail_2pct_net": float(ret),
                        "trail_hold_hours": int(hold_h),
                        "exit_type": exit_type,
                    }
                )

    trades = pd.DataFrame(all_trades)
    trades.to_csv(OUT / "v4_ret_threshold_trades.csv", index=False)
    print(f"[trades] {len(trades):,} threshold/event trades")

    summary_rows = []
    for thr in RET_THRESHOLDS:
        g = trades[trades["threshold"].eq(thr)].copy()
        for slip in SLIPPAGE_ONE_WAY:
            adj = g["trail_2pct_net"].to_numpy("float64") - 2.0 * slip
            s = stats(adj)
            s.update(
                {
                    "threshold": thr,
                    "threshold_label": f"{thr*100:.1f}%",
                    "slippage_bps": int(round(slip * 10000)),
                    "events_with_trade": int(g[["symbol", "event_ts"]].drop_duplicates().shape[0]),
                    "symbols": int(g["symbol"].nunique()) if len(g) else 0,
                    "avg_lag_hours": float(g["lag_hours"].mean()) if len(g) else np.nan,
                    "avg_ret_1h": float(g["ret_1h"].mean()) if len(g) else np.nan,
                    "avg_vol_ratio": float(g["vol_ratio"].mean()) if len(g) else np.nan,
                    "trail_pct": TRAIL_PCT,
                }
            )
            summary_rows.append(s)

        for year, yg in g.groupby("year"):
            y = stats(yg["trail_2pct_net"].to_numpy("float64"))
            y.update({"threshold": thr, "threshold_label": f"{thr*100:.1f}%", "year": int(year)})
            yearly_rows.append(y)

    summary = pd.DataFrame(summary_rows)
    yearly = pd.DataFrame(yearly_rows)
    summary.to_csv(OUT / "v4_ret_threshold_summary.csv", index=False)
    yearly.to_csv(OUT / "v4_ret_threshold_yearly.csv", index=False)

    base = summary[(summary["threshold"].eq(0.01)) & (summary["slippage_bps"].eq(0))]
    stress = summary[(summary["threshold"].eq(0.01)) & (summary["slippage_bps"].eq(30))]
    meta = {
        "created_at_utc": pd.Timestamp.utcnow().isoformat(),
        "event_file": str(EVENT_FILE.relative_to(ROOT)),
        "method": {
            "event_rule": "rank<=20, ret24>=30%, quote volume 24h>=5M, 24h event cooldown from overlay",
            "signal_rule": "vol_ratio>=3 and ret_1h>=threshold",
            "ret_1h": "close-to-close pct_change",
            "vol_ratio": "current quote volume / rolling20 mean including current bar",
            "signal_cooldown_bars": SIGNAL_COOLDOWN_BARS,
            "execution": "first V4 signal per event within (event_ts, event_ts+48h]",
            "exit": "trail 2%, max hold 48h",
            "base_cost": BASE_COST,
            "slippage": "additional 2 * one-way slippage",
        },
        "thresholds": RET_THRESHOLDS,
        "symbols_processed": processed,
        "trades": int(len(trades)),
        "current_1pct": base.iloc[0].to_dict() if len(base) else {},
        "current_1pct_30bps": stress.iloc[0].to_dict() if len(stress) else {},
    }
    with open(OUT / "summary.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2, default=str)

    print("\nSummary: trail 2%, net of base 13bps")
    print(
        summary[summary["slippage_bps"].eq(0)][
            ["threshold_label", "n", "mean", "median", "winrate", "pf", "events_with_trade", "avg_ret_1h"]
        ].to_string(index=False)
    )
    print("\n30bps one-way slippage stress:")
    print(
        summary[summary["slippage_bps"].eq(30)][
            ["threshold_label", "n", "mean", "median", "winrate", "pf", "events_with_trade"]
        ].to_string(index=False)
    )
    print(f"\n[DONE] wrote {OUT.relative_to(ROOT)} in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
