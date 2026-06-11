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

from momentum.signals.up_down_wave import UpDownWaveConfig, compute_up_down_wave_signals


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build UpWave/DownWave signals from silver OHLCV CSV.")
    parser.add_argument("--config", default="config/signals/up_down_wave.yaml")
    parser.add_argument("--input", default=None, help="Input CSV path")
    parser.add_argument("--output", default=None, help="Output CSV path")
    parser.add_argument("--ma-period", type=int, default=None)
    parser.add_argument("--symbol", default=None, help="Optional symbol filter")
    args = parser.parse_args()

    cfg_all = load_yaml(ROOT / args.config)
    cfg = cfg_all.get("up_down_wave", cfg_all)

    in_path = Path(args.input or cfg.get("input_csv", ""))
    if not in_path.exists():
        raise SystemExit(f"Input not found: {in_path}")

    ma_period = int(args.ma_period if args.ma_period is not None else cfg.get("ma_period", 20))

    out_path = Path(
        args.output
        or cfg.get("output_csv")
        or (ROOT / "outputs" / "signals" / f"up_down_wave_ma{ma_period}.csv")
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)

    symbol = args.symbol if args.symbol is not None else cfg.get("symbol")

    df = pd.read_csv(in_path)
    if symbol and "symbol" in df.columns:
        df = df[df["symbol"].astype(str) == str(symbol)].copy()

    result = compute_up_down_wave_signals(df, config=UpDownWaveConfig(ma_period=ma_period))

    keep_cols = [
        c
        for c in ["timestamp", "symbol", "open", "close", f"ma_{ma_period}", "upwave", "downwave"]
        if c in result.columns
    ]
    result[keep_cols].to_csv(out_path, index=False)

    print(f"[ok] input: {in_path}")
    print(f"[ok] output: {out_path} ({len(result)} rows)")
    print(f"[ok] ma_period={ma_period}, symbol={symbol}")
    print(f"[ok] upwave_count={int(result['upwave'].sum())}, downwave_count={int(result['downwave'].sum())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
