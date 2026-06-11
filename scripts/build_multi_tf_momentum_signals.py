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

from momentum.signals.multi_tf_momentum import (  # noqa: E402
    MultiTfMomentumConfig,
    compute_multi_tf_momentum_signals,
)


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build multi-timeframe momentum signals from 5m OHLCV CSV."
    )
    parser.add_argument("--config", default="config/signals/multi_tf_momentum.yaml")
    parser.add_argument("--input", default=None, help="Input CSV path (5m bars)")
    parser.add_argument("--output", default=None, help="Output CSV path")
    parser.add_argument("--symbol", default=None, help="Optional symbol filter")
    parser.add_argument("--window-5m", type=int, default=None)
    parser.add_argument("--window-15m", type=int, default=None)
    parser.add_argument("--threshold-5m", type=float, default=None)
    parser.add_argument("--threshold-15m", type=float, default=None)
    parser.add_argument("--resample-rule-15m", default=None)
    args = parser.parse_args()

    cfg_all = load_yaml(ROOT / args.config)
    cfg = cfg_all.get("multi_tf_momentum", cfg_all)

    in_path_raw = args.input or cfg.get("input_csv", "")
    if not in_path_raw:
        raise SystemExit("Input CSV is required. Pass --input or set multi_tf_momentum.input_csv in YAML.")

    in_path = Path(in_path_raw)
    if not in_path.is_absolute():
        in_path = ROOT / in_path
    if not in_path.exists():
        raise SystemExit(f"Input not found: {in_path}")

    out_path_raw = args.output or cfg.get("output_csv") or "outputs/signals/multi_tf_momentum.csv"
    out_path = Path(out_path_raw)
    if not out_path.is_absolute():
        out_path = ROOT / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)

    symbol = args.symbol if args.symbol is not None else cfg.get("symbol")

    config = MultiTfMomentumConfig(
        window_5m=int(args.window_5m if args.window_5m is not None else cfg.get("window_5m", 6)),
        window_15m=int(args.window_15m if args.window_15m is not None else cfg.get("window_15m", 6)),
        threshold_5m=float(
            args.threshold_5m if args.threshold_5m is not None else cfg.get("threshold_5m", 0.0)
        ),
        threshold_15m=float(
            args.threshold_15m if args.threshold_15m is not None else cfg.get("threshold_15m", 0.0)
        ),
        resample_rule_15m=args.resample_rule_15m or cfg.get("resample_rule_15m", "15min"),
    )

    df = pd.read_csv(in_path)
    if symbol and "symbol" in df.columns:
        df = df[df["symbol"].astype(str) == str(symbol)].copy()

    result = compute_multi_tf_momentum_signals(df, config=config)

    keep_cols = [
        c
        for c in [
            "timestamp",
            "symbol",
            "close",
            "mom_5m",
            "mom_15m",
            "long_signal",
            "short_signal",
        ]
        if c in result.columns
    ]
    result[keep_cols].to_csv(out_path, index=False)

    print(f"[ok] input: {in_path}")
    print(f"[ok] output: {out_path} ({len(result)} rows)")
    print(
        "[ok] config: "
        f"window_5m={config.window_5m}, window_15m={config.window_15m}, "
        f"threshold_5m={config.threshold_5m}, threshold_15m={config.threshold_15m}, "
        f"resample_rule_15m={config.resample_rule_15m}, symbol={symbol}"
    )
    print(
        f"[ok] long_count={int(result['long_signal'].sum())}, "
        f"short_count={int(result['short_signal'].sum())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
