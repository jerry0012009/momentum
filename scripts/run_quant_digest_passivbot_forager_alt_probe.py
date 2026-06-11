#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "literature"
CACHE_DIR = ART_DIR / "passivbot_trailing_grid_probe_cache"
ASSETS = ["ETHUSDT", "BNBUSDT", "XRPUSDT", "SOLUSDT"]
INTERVAL = "15m"
MAKER_RT_BPS = 8.0


@dataclass
class Variant:
    label: str
    hold_bars: int
    min_stretch: float
    vol_mult: float
    retrace_fraction: float
    take_profit: float
    top_vol_n: int | None = None


VARIANTS = [
    Variant("alt4_balanced", 2, 0.012, 2.5, 0.85, 0.004, None),
    Variant("alt4_top2vol", 2, 0.012, 2.5, 0.85, 0.004, 2),
    Variant("alt4_extreme", 2, 0.015, 3.0, 0.85, 0.004, None),
    Variant("alt4_extreme_top2vol", 2, 0.015, 3.0, 0.85, 0.004, 2),
]


def load_symbol(symbol: str) -> pd.DataFrame:
    df = pd.read_csv(CACHE_DIR / f"{symbol}_{INTERVAL}_20251001_20260412.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def prepare_panel(symbol: str, df: pd.DataFrame) -> pd.DataFrame:
    span0, span1, span_mid, volspan = 14, 51, 27, 15
    out = df.copy()
    out["ema0"] = out["close"].ewm(span=span0, adjust=False).mean()
    out["ema1"] = out["close"].ewm(span=span1, adjust=False).mean()
    out["ema_mid"] = out["close"].ewm(span=span_mid, adjust=False).mean()
    out["ema_lower"] = out[["ema0", "ema1", "ema_mid"]].min(axis=1)
    out["norm_range"] = ((out["high"] - out["low"]) / out["close"]).ewm(span=volspan, adjust=False).mean()
    out["stretch"] = (out["ema_lower"] - out["low"]) / out["ema_lower"]
    out["close_in_range"] = (out["close"] - out["low"]) / (out["high"] - out["low"]).replace(0, np.nan)
    out["symbol"] = symbol
    return out


def apply_cost(ret: pd.Series, rt_bps: float = MAKER_RT_BPS) -> pd.Series:
    c = rt_bps / 10000.0
    return (1.0 + ret.astype(float)) * (1.0 - c) - 1.0


def simulate_variant(panel_map: dict[str, pd.DataFrame], variant: Variant) -> pd.DataFrame:
    full = pd.concat([df[["timestamp", "symbol", "norm_range"]] for df in panel_map.values()], ignore_index=True)
    full["vol_rank"] = full.groupby("timestamp")["norm_range"].rank(method="first", ascending=False)
    if variant.top_vol_n is None:
        vol_ok = {(r.timestamp, r.symbol): True for r in full.itertuples(index=False)}
    else:
        vol_ok = {(r.timestamp, r.symbol): r.vol_rank <= variant.top_vol_n for r in full.itertuples(index=False)}

    rows = []
    for symbol, df in panel_map.items():
        d = df.copy()
        d["threshold"] = np.maximum(variant.min_stretch, variant.vol_mult * d["norm_range"])
        d["signal"] = (
            (d["stretch"] >= d["threshold"])
            & (d["close_in_range"] >= variant.retrace_fraction)
            & (d["close"] < d["ema_lower"])
        )
        last_entry_idx = -99
        for i in range(len(d) - variant.hold_bars - 1):
            if not bool(d.loc[i, "signal"]):
                continue
            if variant.top_vol_n is not None and not vol_ok[(d.loc[i, "timestamp"], symbol)]:
                continue
            if i - last_entry_idx <= 2:
                continue
            entry_idx = i + 1
            entry_px = float(d.loc[entry_idx, "open"])
            tp_px = entry_px * (1.0 + variant.take_profit)
            exit_idx = entry_idx + variant.hold_bars
            exit_px = float(d.loc[exit_idx, "close"])
            tp_hit = False
            for j in range(entry_idx, entry_idx + variant.hold_bars + 1):
                if float(d.loc[j, "high"]) >= tp_px:
                    exit_idx = j
                    exit_px = tp_px
                    tp_hit = True
                    break
            rows.append(
                {
                    "variant": variant.label,
                    "symbol": symbol,
                    "signal_time": d.loc[i, "timestamp"],
                    "entry_time": d.loc[entry_idx, "timestamp"],
                    "exit_time": d.loc[exit_idx, "timestamp"],
                    "gross_ret": exit_px / entry_px - 1.0,
                    "tp_hit": tp_hit,
                    "stretch_pct": float(d.loc[i, "stretch"]),
                    "threshold_pct": float(d.loc[i, "threshold"]),
                    "close_in_range": float(d.loc[i, "close_in_range"]),
                    "top_vol_n": variant.top_vol_n or 0,
                }
            )
            last_entry_idx = entry_idx
    return pd.DataFrame(rows)


def summarize(detail: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for label, g in detail.groupby("variant"):
        rets = g["gross_ret"].astype(float)
        maker = apply_cost(rets)
        rows.append(
            {
                "variant": label,
                "trades": int(len(g)),
                "gross_mean_bps": float(rets.mean() * 10000.0),
                "gross_win_rate": float((rets > 0).mean()),
                "tp_hit_rate": float(g["tp_hit"].mean()),
                "maker_net_mean_bps": float(maker.mean() * 10000.0),
                "avg_stretch_pct": float(g["stretch_pct"].mean() * 100.0),
                "avg_threshold_pct": float(g["threshold_pct"].mean() * 100.0),
                "avg_close_in_range": float(g["close_in_range"].mean()),
            }
        )
    return pd.DataFrame(rows).sort_values("gross_mean_bps", ascending=False)


def summarize_by_symbol(detail: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (label, symbol), g in detail.groupby(["variant", "symbol"]):
        rets = g["gross_ret"].astype(float)
        rows.append(
            {
                "variant": label,
                "symbol": symbol,
                "trades": int(len(g)),
                "gross_mean_bps": float(rets.mean() * 10000.0),
                "gross_win_rate": float((rets > 0).mean()),
                "tp_hit_rate": float(g["tp_hit"].mean()),
            }
        )
    return pd.DataFrame(rows).sort_values(["variant", "gross_mean_bps"], ascending=[True, False])


def main() -> None:
    panel_map = {symbol: prepare_panel(symbol, load_symbol(symbol)) for symbol in ASSETS}
    detail = pd.concat([simulate_variant(panel_map, variant) for variant in VARIANTS], ignore_index=True)
    summary = summarize(detail)
    by_symbol = summarize_by_symbol(detail)

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    summary_path = ART_DIR / f"passivbot_forager_alt_probe_{stamp}_summary.csv"
    detail_path = ART_DIR / f"passivbot_forager_alt_probe_{stamp}_detail.csv"
    by_symbol_path = ART_DIR / f"passivbot_forager_alt_probe_{stamp}_symbol.csv"
    summary.to_csv(summary_path, index=False)
    detail.to_csv(detail_path, index=False)
    by_symbol.to_csv(by_symbol_path, index=False)

    print(summary.to_string(index=False))
    print("\nby symbol:\n")
    print(by_symbol.to_string(index=False))
    print(f"\nWrote: {summary_path}\nWrote: {by_symbol_path}\nWrote: {detail_path}")


if __name__ == "__main__":
    main()
