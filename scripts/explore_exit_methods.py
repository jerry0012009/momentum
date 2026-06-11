#!/usr/bin/env python3
"""Compare exit methods for Event+V4 strategy.

Tests:
1. Trailing stop (current baseline) - uses HWM
2. Fixed holding period - no HWM, backtest=live
3. ATR-based stop (entry-based, no trailing) - no HWM
4. Fixed TP/SL - no HWM
5. ATR TP/SL - no HWM

Goal: Find exit methods that (a) have positive expectation and
(b) minimize backtest-live discrepancy.
"""

import csv
import math
import statistics
from pathlib import Path

TRADES = Path("reports/artifacts/binance_event_study_v1_6a_second_squeeze_tpsl/all_trades_tpsl.csv")
KLINE_DIR = Path("reports/artifacts/binance_event_study_v1_6a_second_squeeze_tpsl/klines_1h")

FEE_BPS = 4.0
FEE_RATE = FEE_BPS / 10000.0


def load_trades():
    rows = []
    with open(TRADES) as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def load_klines(symbol):
    """Load 1h klines for a symbol. Returns list of {ts, open, high, low, close, volume}."""
    kfile = KLINE_DIR / f"{symbol}_1h.csv"
    if not kfile.exists():
        return []
    bars = []
    with open(kfile) as f:
        reader = csv.DictReader(f)
        for r in reader:
            bars.append({
                "ts": r.get("open_time_utc", r.get("ts", "")),
                "open": float(r["open"]),
                "high": float(r["high"]),
                "low": float(r["low"]),
                "close": float(r["close"]),
                "volume": float(r.get("quote_volume", r.get("volume", 0))),
            })
    return bars


def compute_atr(bars, period=14):
    """Compute ATR from bars."""
    if len(bars) < period + 1:
        return None
    trs = []
    for i in range(1, len(bars)):
        h = bars[i]["high"]
        l = bars[i]["low"]
        pc = bars[i-1]["close"]
        tr = max(h - l, abs(h - pc), abs(l - pc))
        trs.append(tr)
    if len(trs) < period:
        return None
    return sum(trs[-period:]) / period


def find_bar_index(bars, target_ts):
    """Find the index of the bar whose open_time matches target_ts."""
    for i, b in enumerate(bars):
        if b["ts"] == target_ts:
            return i
    # Try matching by prefix
    for i, b in enumerate(bars):
        if b["ts"][:16] == target_ts[:16]:
            return i
    return None


def net_ret(gross_ret):
    """Apply round-trip fees."""
    return (1.0 + gross_ret) * (1.0 - FEE_RATE) * (1.0 - FEE_RATE) - 1.0


def simulate_trailing_stop(bars, entry_idx, entry_px, trail_pct, max_hold=48):
    """Original trailing stop with HWM using bar high. Returns (exit_px, exit_idx, reason)."""
    hwm = entry_px
    for i in range(entry_idx, min(entry_idx + max_hold, len(bars))):
        bar = bars[i]
        hwm = max(hwm, bar["high"])
        trail_stop = hwm * (1 - trail_pct)
        if bar["low"] <= trail_stop:
            return trail_stop, i, "trailing_stop"
    # Timeout
    exit_idx = min(entry_idx + max_hold, len(bars) - 1)
    return bars[exit_idx]["close"], exit_idx, "timeout"


def simulate_fixed_hold(bars, entry_idx, entry_px, hold_bars):
    """Fixed holding period. Returns (exit_px, exit_idx, reason)."""
    exit_idx = min(entry_idx + hold_bars, len(bars) - 1)
    return bars[exit_idx]["close"], exit_idx, "fixed_hold"


def simulate_atr_stop(bars, entry_idx, entry_px, atr_mult, max_hold=48):
    """ATR-based stop from entry (no trailing). Returns (exit_px, exit_idx, reason)."""
    atr = compute_atr(bars[:entry_idx+1])
    if atr is None or atr <= 0:
        return None, None, "no_atr"
    stop_px = entry_px - atr_mult * atr
    for i in range(entry_idx, min(entry_idx + max_hold, len(bars))):
        bar = bars[i]
        if bar["low"] <= stop_px:
            return stop_px, i, "atr_stop"
    # Timeout
    exit_idx = min(entry_idx + max_hold, len(bars) - 1)
    return bars[exit_idx]["close"], exit_idx, "timeout"


def simulate_fixed_tp_sl(bars, entry_idx, entry_px, tp_pct, sl_pct, max_hold=48):
    """Fixed take-profit / stop-loss from entry. Returns (exit_px, exit_idx, reason)."""
    tp_px = entry_px * (1 + tp_pct)
    sl_px = entry_px * (1 - sl_pct)
    for i in range(entry_idx, min(entry_idx + max_hold, len(bars))):
        bar = bars[i]
        # Check SL first (conservative: assume SL hit before TP if both in same bar)
        if bar["low"] <= sl_px:
            return sl_px, i, "stop_loss"
        if bar["high"] >= tp_px:
            return tp_px, i, "take_profit"
    # Timeout
    exit_idx = min(entry_idx + max_hold, len(bars) - 1)
    return bars[exit_idx]["close"], exit_idx, "timeout"


def simulate_atr_tp_sl(bars, entry_idx, entry_px, tp_atr_mult, sl_atr_mult, max_hold=48):
    """ATR-based TP/SL from entry. Returns (exit_px, exit_idx, reason)."""
    atr = compute_atr(bars[:entry_idx+1])
    if atr is None or atr <= 0:
        return None, None, "no_atr"
    tp_px = entry_px + tp_atr_mult * atr
    sl_px = entry_px - sl_atr_mult * atr
    for i in range(entry_idx, min(entry_idx + max_hold, len(bars))):
        bar = bars[i]
        if bar["low"] <= sl_px:
            return sl_px, i, "stop_loss"
        if bar["high"] >= tp_px:
            return tp_px, i, "take_profit"
    exit_idx = min(entry_idx + max_hold, len(bars) - 1)
    return bars[exit_idx]["close"], exit_idx, "timeout"


def run_experiment(trades, name, sim_fn, **kwargs):
    """Run a simulation and return results."""
    rets = []
    reasons = {}
    for t in trades:
        sym = t["symbol"]
        entry_px = float(t["paper_entry_price"])
        entry_ts = t["entry_ts_utc"]

        bars = load_klines(sym)
        if not bars:
            continue

        idx = find_bar_index(bars, entry_ts)
        if idx is None:
            # Try to find closest bar
            for i, b in enumerate(bars):
                if entry_ts[:13] in b["ts"]:
                    idx = i
                    break
        if idx is None:
            continue

        result = sim_fn(bars, idx, entry_px, **kwargs)
        if result[0] is None:
            continue

        exit_px, exit_idx, reason = result
        gross = exit_px / entry_px - 1.0
        rets.append(gross)
        reasons[reason] = reasons.get(reason, 0) + 1

    if not rets:
        return None

    net_rets = [net_ret(r) for r in rets]
    wins = [r for r in net_rets if r > 0]
    losses = [r for r in net_rets if r <= 0]

    return {
        "name": name,
        "n": len(rets),
        "median": statistics.median(net_rets) * 100,
        "mean": statistics.mean(net_rets) * 100,
        "win_rate": len(wins) / len(net_rets) * 100 if net_rets else 0,
        "pf": sum(wins) / abs(sum(losses)) if losses else float("inf"),
        "worst": min(net_rets) * 100,
        "best": max(net_rets) * 100,
        "reasons": reasons,
    }


def main():
    trades = load_trades()
    print(f"Loaded {len(trades)} trades")

    # Check available kline files
    kline_files = list(KLINE_DIR.glob("*_1h.csv"))
    print(f"Available kline files: {len(kline_files)}")

    # Filter trades to those with available klines
    available_syms = {f.stem.replace("_1h", "") for f in kline_files}
    trades_with_klines = [t for t in trades if t["symbol"] in available_syms]
    print(f"Trades with klines: {len(trades_with_klines)}")

    experiments = [
        # Baseline: trailing stop
        ("trail_2pct", simulate_trailing_stop, {"trail_pct": 0.02}),
        ("trail_1pct", simulate_trailing_stop, {"trail_pct": 0.01}),
        ("trail_3pct", simulate_trailing_stop, {"trail_pct": 0.03}),
        ("trail_5pct", simulate_trailing_stop, {"trail_pct": 0.05}),

        # Fixed holding period
        ("hold_1h", simulate_fixed_hold, {"hold_bars": 1}),
        ("hold_2h", simulate_fixed_hold, {"hold_bars": 2}),
        ("hold_4h", simulate_fixed_hold, {"hold_bars": 4}),
        ("hold_8h", simulate_fixed_hold, {"hold_bars": 8}),
        ("hold_24h", simulate_fixed_hold, {"hold_bars": 24}),
        ("hold_48h", simulate_fixed_hold, {"hold_bars": 48}),

        # ATR-based stop (entry-based, no trailing)
        ("atr_1x_stop", simulate_atr_stop, {"atr_mult": 1.0}),
        ("atr_2x_stop", simulate_atr_stop, {"atr_mult": 2.0}),
        ("atr_3x_stop", simulate_atr_stop, {"atr_mult": 3.0}),

        # Fixed TP/SL
        ("tp1_sl1", simulate_fixed_tp_sl, {"tp_pct": 0.01, "sl_pct": 0.01}),
        ("tp2_sl1", simulate_fixed_tp_sl, {"tp_pct": 0.02, "sl_pct": 0.01}),
        ("tp3_sl1", simulate_fixed_tp_sl, {"tp_pct": 0.03, "sl_pct": 0.01}),
        ("tp2_sl2", simulate_fixed_tp_sl, {"tp_pct": 0.02, "sl_pct": 0.02}),
        ("tp3_sl2", simulate_fixed_tp_sl, {"tp_pct": 0.03, "sl_pct": 0.02}),
        ("tp5_sl2", simulate_fixed_tp_sl, {"tp_pct": 0.05, "sl_pct": 0.02}),

        # ATR TP/SL
        ("atr_tp2_sl1", simulate_atr_tp_sl, {"tp_atr_mult": 2.0, "sl_atr_mult": 1.0}),
        ("atr_tp3_sl1", simulate_atr_tp_sl, {"tp_atr_mult": 3.0, "sl_atr_mult": 1.0}),
        ("atr_tp3_sl2", simulate_atr_tp_sl, {"tp_atr_mult": 3.0, "sl_atr_mult": 2.0}),
        ("atr_tp2_sl2", simulate_atr_tp_sl, {"tp_atr_mult": 2.0, "sl_atr_mult": 2.0}),
    ]

    results = []
    for name, fn, kwargs in experiments:
        r = run_experiment(trades_with_klines, name, fn, **kwargs)
        if r:
            results.append(r)
            print(f"  {name}: n={r['n']}, median={r['median']:.2f}%, winrate={r['win_rate']:.1f}%, PF={r['pf']:.2f}")

    # Sort by median return
    results.sort(key=lambda x: x["median"], reverse=True)

    # Print summary table
    print("\n" + "=" * 100)
    print(f"{'Config':<20} {'N':>5} {'Median%':>8} {'Mean%':>8} {'WinRate%':>9} {'PF':>6} {'Worst%':>8} {'Best%':>8}")
    print("-" * 100)
    for r in results:
        pf_str = f"{r['pf']:.2f}" if r['pf'] != float('inf') else "inf"
        print(f"{r['name']:<20} {r['n']:>5} {r['median']:>8.2f} {r['mean']:>8.2f} {r['win_rate']:>9.1f} {pf_str:>6} {r['worst']:>8.2f} {r['best']:>8.2f}")

    # Print exit reason breakdown for top configs
    print("\n\nExit reason breakdown (top 10):")
    for r in results[:10]:
        print(f"  {r['name']}: {r['reasons']}")

    # Focus on configs that are "HWM-free" (no look-ahead bias)
    hwm_free = [r for r in results if r["name"].startswith(("hold_", "atr_", "tp", "atr_tp"))]
    if hwm_free:
        print("\n\n=== HWM-Free configs only (backtest ≈ live) ===")
        print(f"{'Config':<20} {'N':>5} {'Median%':>8} {'Mean%':>8} {'WinRate%':>9} {'PF':>6}")
        print("-" * 70)
        for r in hwm_free:
            pf_str = f"{r['pf']:.2f}" if r['pf'] != float('inf') else "inf"
            print(f"{r['name']:<20} {r['n']:>5} {r['median']:>8.2f} {r['mean']:>8.2f} {r['win_rate']:>9.1f} {pf_str:>6}")


if __name__ == "__main__":
    main()
