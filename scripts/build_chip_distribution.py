#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import json

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.factors.chip_distribution import ChipConfig, estimate_chip_distribution_panel


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data


def resolve_files(input_glob: str, input_paths: list[str]) -> list[Path]:
    files = set()
    for p in input_paths:
        path = Path(p)
        if path.is_file() and path.suffix.lower() == ".csv":
            files.add(path.resolve())
    if input_glob:
        for p in ROOT.glob(input_glob):
            if p.is_file() and p.suffix.lower() == ".csv":
                files.add(p.resolve())
    return sorted(files)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build chip distribution tables from silver OHLCV.")
    parser.add_argument("--config", default="config/features/chip_distribution.yaml")
    parser.add_argument("--input-glob", default=None, help="CSV glob relative to repo root")
    parser.add_argument("--input-path", action="append", default=[], help="Additional CSV paths")
    parser.add_argument("--symbols", default=None, help="Comma-separated symbols filter")

    parser.add_argument("--bin-size-pct", type=float, default=None, help="Log-grid pct step, e.g. 0.005")
    parser.add_argument("--distribution", choices=["triangular", "uniform"], default=None)
    parser.add_argument("--turnover-cap", type=float, default=None)
    parser.add_argument("--min-chip-pct", type=float, default=None)

    parser.add_argument("--shares-col", default=None, help="Per-row shares column if present")
    parser.add_argument("--default-shares", type=float, default=None)

    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    cfg_all = load_yaml(ROOT / args.config)
    cfg = cfg_all.get("chip_distribution", cfg_all)

    input_glob = args.input_glob or cfg.get("input_glob", "data/silver/**/*.csv")
    output_dir = Path(args.output_dir or cfg.get("output_dir", "outputs/chip_distribution"))

    symbols = None
    if args.symbols:
        symbols = {s.strip() for s in args.symbols.split(",") if s.strip()}

    feature_cfg = ChipConfig(
        bin_size_pct=float(args.bin_size_pct if args.bin_size_pct is not None else cfg.get("bin_size_pct", 0.005)),
        distribution=str(args.distribution or cfg.get("distribution", "triangular")),
        turnover_cap=float(args.turnover_cap if args.turnover_cap is not None else cfg.get("turnover_cap", 1.0)),
        min_chip_pct=float(args.min_chip_pct if args.min_chip_pct is not None else cfg.get("min_chip_pct", 1e-6)),
    )

    shares_cfg = cfg.get("shares", {}) if isinstance(cfg.get("shares", {}), dict) else {}
    shares_map = shares_cfg.get("symbol_shares", {}) if isinstance(shares_cfg.get("symbol_shares", {}), dict) else {}
    shares_map = {str(k): float(v) for k, v in shares_map.items()}

    default_shares = args.default_shares
    if default_shares is None and shares_cfg.get("default") is not None:
        default_shares = float(shares_cfg["default"])

    shares_col = args.shares_col or cfg.get("shares_col")

    files = resolve_files(input_glob=input_glob, input_paths=args.input_path)
    if not files:
        raise SystemExit(f"No CSV files found. glob={input_glob}, input_paths={args.input_path}")

    frames = []
    for f in files:
        df = pd.read_csv(f)
        if "symbol" not in df.columns:
            # fallback from filename, e.g. 1810.HK_1d_5y_silver.csv
            sym = f.stem.split("_")[0]
            df["symbol"] = sym
        frames.append(df)

    bars = pd.concat(frames, ignore_index=True)
    if symbols is not None:
        bars = bars[bars["symbol"].astype(str).isin(symbols)].copy()

    if bars.empty:
        raise SystemExit("No bars after symbol filter.")

    asset_df, norm_df, summary_df = estimate_chip_distribution_panel(
        bars,
        config=feature_cfg,
        shares_by_symbol=shares_map,
        default_shares=default_shares,
        shares_col=shares_col,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    asset_path = output_dir / "chip_distribution_asset.csv"
    norm_path = output_dir / "chip_distribution_normalized.csv"
    summary_path = output_dir / "chip_summary_daily.csv"
    meta_path = output_dir / "run_meta.json"

    asset_df.to_csv(asset_path, index=False)
    norm_df.to_csv(norm_path, index=False)
    summary_df.to_csv(summary_path, index=False)

    meta = {
        "input_files": [str(f.relative_to(ROOT)) if str(f).startswith(str(ROOT)) else str(f) for f in files],
        "rows": {
            "asset": int(len(asset_df)),
            "normalized": int(len(norm_df)),
            "summary": int(len(summary_df)),
        },
        "symbols": sorted(summary_df["symbol"].unique().tolist()) if not summary_df.empty else [],
        "config": {
            "bin_size_pct": feature_cfg.bin_size_pct,
            "distribution": feature_cfg.distribution,
            "turnover_cap": feature_cfg.turnover_cap,
            "min_chip_pct": feature_cfg.min_chip_pct,
            "shares_col": shares_col,
            "default_shares": default_shares,
        },
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[ok] asset: {asset_path} ({len(asset_df)} rows)")
    print(f"[ok] normalized: {norm_path} ({len(norm_df)} rows)")
    print(f"[ok] summary: {summary_path} ({len(summary_df)} rows)")
    print(f"[ok] meta: {meta_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
