#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.signals import BoxConsolidationConfig, compute_box_consolidation_signals


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build box-consolidation accumulation signals from silver OHLCV CSV.")
    parser.add_argument("--config", default="config/signals/box_consolidation.yaml")
    parser.add_argument("--input", default=None, help="Input CSV path")
    parser.add_argument("--output", default=None, help="Output CSV path")
    parser.add_argument("--symbol", default=None, help="Optional symbol filter")

    parser.add_argument("--ma-period", type=int, default=None)
    parser.add_argument("--decline-lookback", type=int, default=None)
    parser.add_argument("--min-decline-pct", type=float, default=None)
    parser.add_argument("--decline-recent-window", type=int, default=None)
    parser.add_argument("--bearish-floor-lookback", type=int, default=None)
    parser.add_argument("--floor-hold-days", type=int, default=None)
    parser.add_argument("--narrow-box-lookback", type=int, default=None)
    parser.add_argument("--narrow-range-max", type=float, default=None)
    parser.add_argument("--atr-period", type=int, default=None)
    parser.add_argument("--narrow-atr-ratio-max", type=float, default=None)
    parser.add_argument("--upwave-recent-window", type=int, default=None)
    parser.add_argument("--box-lookback", type=int, default=None)
    parser.add_argument("--box-range-min", type=float, default=None)
    parser.add_argument("--box-range-max", type=float, default=None)
    parser.add_argument("--breakout-buffer", type=float, default=None)
    parser.add_argument("--require-chip-filter", action="store_true")
    parser.add_argument("--chip-winner-min", type=float, default=None)
    parser.add_argument("--chip-winner-max", type=float, default=None)

    args = parser.parse_args()

    cfg_all = load_yaml(ROOT / args.config)
    cfg = cfg_all.get("box_consolidation", cfg_all)

    in_path = Path(args.input or cfg.get("input_csv", ""))
    if not in_path.exists():
        raise SystemExit(f"Input not found: {in_path}")

    out_path = Path(
        args.output
        or cfg.get("output_csv")
        or (ROOT / "outputs" / "signals" / "box_consolidation.csv")
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)

    symbol = args.symbol if args.symbol is not None else cfg.get("symbol")

    def pick(name: str, cli_v, default):
        return cli_v if cli_v is not None else cfg.get(name, default)

    signal_cfg = BoxConsolidationConfig(
        ma_period=int(pick("ma_period", args.ma_period, 20)),
        decline_lookback=int(pick("decline_lookback", args.decline_lookback, 60)),
        min_decline_pct=float(pick("min_decline_pct", args.min_decline_pct, 0.12)),
        decline_recent_window=int(pick("decline_recent_window", args.decline_recent_window, 20)),
        bearish_floor_lookback=int(pick("bearish_floor_lookback", args.bearish_floor_lookback, 120)),
        floor_hold_days=int(pick("floor_hold_days", args.floor_hold_days, 5)),
        narrow_box_lookback=int(pick("narrow_box_lookback", args.narrow_box_lookback, 20)),
        narrow_range_max=float(pick("narrow_range_max", args.narrow_range_max, 0.08)),
        atr_period=int(pick("atr_period", args.atr_period, 14)),
        narrow_atr_ratio_max=float(pick("narrow_atr_ratio_max", args.narrow_atr_ratio_max, 0.025)),
        upwave_recent_window=int(pick("upwave_recent_window", args.upwave_recent_window, 20)),
        box_lookback=int(pick("box_lookback", args.box_lookback, 30)),
        box_range_min=float(pick("box_range_min", args.box_range_min, 0.08)),
        box_range_max=float(pick("box_range_max", args.box_range_max, 0.30)),
        breakout_buffer=float(pick("breakout_buffer", args.breakout_buffer, 0.0)),
        require_chip_filter=bool(args.require_chip_filter or cfg.get("require_chip_filter", False)),
        chip_winner_min=float(pick("chip_winner_min", args.chip_winner_min, 0.30)),
        chip_winner_max=float(pick("chip_winner_max", args.chip_winner_max, 0.80)),
    )

    df = pd.read_csv(in_path)
    if symbol and "symbol" in df.columns:
        df = df[df["symbol"].astype(str) == str(symbol)].copy()

    result = compute_box_consolidation_signals(df, config=signal_cfg)

    keep_cols = [
        c
        for c in [
            "timestamp",
            "symbol",
            "open",
            "high",
            "low",
            "close",
            "upwave",
            "downwave",
            "drawdown_from_peak",
            "bearish_floor",
            "narrow_box_width",
            "atr_ratio",
            "box_width",
            "narrow_accum_ready",
            "box_breakout_ready",
            "accumulation_ready",
        ]
        if c in result.columns
    ]
    result[keep_cols].to_csv(out_path, index=False)

    print(f"[ok] input: {in_path}")
    print(f"[ok] output: {out_path} ({len(result)} rows)")
    print(f"[ok] symbol={symbol}")
    print(f"[ok] narrow_accum_ready={int(result['narrow_accum_ready'].sum())}")
    print(f"[ok] box_breakout_ready={int(result['box_breakout_ready'].sum())}")
    print(f"[ok] accumulation_ready={int(result['accumulation_ready'].sum())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
