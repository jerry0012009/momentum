#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.analytics.wave_hold_backtest import WaveBacktestConfig, evaluate_wave_hold


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def main() -> int:
    parser = argparse.ArgumentParser(description="Event backtest for UpWave/DownWave with fixed hold days.")
    parser.add_argument("--config", default="config/signals/up_down_wave.yaml")
    parser.add_argument("--input", default=None, help="Signal CSV produced by build_up_down_wave_signals.py")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--hold-days", type=int, default=None)
    parser.add_argument("--fee-bps-roundtrip", type=float, default=None)
    args = parser.parse_args()

    cfg_all = load_yaml(ROOT / args.config)
    cfg = cfg_all.get("up_down_wave", cfg_all)
    bt_cfg = cfg.get("backtest", {}) if isinstance(cfg.get("backtest", {}), dict) else {}

    default_input = cfg.get("output_csv")
    in_path = Path(args.input or default_input or "")
    if not in_path.exists():
        raise SystemExit(f"Input not found: {in_path}")

    hold_days = int(args.hold_days if args.hold_days is not None else bt_cfg.get("hold_days", 5))
    fee_bps_roundtrip = float(
        args.fee_bps_roundtrip if args.fee_bps_roundtrip is not None else bt_cfg.get("fee_bps_roundtrip", 0.0)
    )

    out_dir = Path(args.output_dir or bt_cfg.get("output_dir", "outputs/backtests/wave_hold"))
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(in_path)

    trades, summary = evaluate_wave_hold(
        df,
        config=WaveBacktestConfig(
            hold_days=hold_days,
            fee_bps_roundtrip=fee_bps_roundtrip,
        ),
    )

    trades_path = out_dir / "wave_hold_trades.csv"
    summary_path = out_dir / "wave_hold_summary.csv"
    meta_path = out_dir / "wave_hold_meta.json"

    trades.to_csv(trades_path, index=False)
    summary.to_csv(summary_path, index=False)

    overall = {
        "trades": int(len(trades)),
        "win_rate": float(trades["win"].mean()) if len(trades) else None,
        "avg_ret": float(trades["net_ret"].mean()) if len(trades) else None,
        "median_ret": float(trades["net_ret"].median()) if len(trades) else None,
        "cum_ret_mult": float((1.0 + trades["net_ret"]).prod() - 1.0) if len(trades) else None,
    }

    meta = {
        "input": str(in_path),
        "config": {
            "hold_days": hold_days,
            "fee_bps_roundtrip": fee_bps_roundtrip,
        },
        "overall": overall,
        "by_signal": summary.to_dict(orient="records"),
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[ok] trades: {trades_path} ({len(trades)} rows)")
    print(f"[ok] summary: {summary_path} ({len(summary)} rows)")
    print(f"[ok] meta: {meta_path}")

    if len(summary):
        print("\n== by signal ==")
        for _, r in summary.iterrows():
            print(
                f"{r['symbol']} {r['signal']}: trades={int(r['trades'])}, "
                f"win_rate={r['win_rate']:.2%}, avg_ret={r['avg_ret']:.4%}, median_ret={r['median_ret']:.4%}"
            )

    if overall["trades"]:
        print("\n== overall ==")
        print(
            f"trades={overall['trades']}, win_rate={overall['win_rate']:.2%}, "
            f"avg_ret={overall['avg_ret']:.4%}, median_ret={overall['median_ret']:.4%}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
