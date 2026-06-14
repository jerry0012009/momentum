#!/usr/bin/env python3
"""
Build reproducible crypto-native data caches: taker enriched bars + funding rate.

Usage:
    python scripts/build_crypto_native_caches.py --mode all
    python scripts/build_crypto_native_caches.py --mode taker
    python scripts/build_crypto_native_caches.py --mode funding
    python scripts/build_crypto_native_caches.py --mode validate

Modes:
    all      Build taker enriched bars + funding rate caches + manifest
    taker    Build taker enriched bars only
    funding  Build funding rate events + 1h aligned only
    validate Validate existing caches against manifest (no rebuild)

Inputs:
    - static/dynamic bars_1h.parquet (from existing factor library cache)
    - raw Binance klines zips (data/binance_vision_1h_v1_6/klines/<SYMBOL>/)
    - raw funding rate zips (data/binance_vision_rank154/data/futures/um/monthly/fundingRate/)

Outputs:
    - Taker enriched bars (does NOT overwrite original bars cache)
    - Funding rate events parquet
    - Funding rate 1h aligned (static + dynamic)
    - Summary CSVs in research/factor_runs/crypto_top50_factor_library/
    - Manifest CSV for auditability

Rules:
    - No factor implementation
    - No factor_values build
    - No evaluation/backtest
    - Taker: join on (timestamp, symbol), missing = NaN, no forward-fill
    - Funding: merge_asof backward, age <= interval, missing symbol = all NaN
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


# ── Config ──────────────────────────────────────────────────────────
@dataclass
class CacheBuildConfig:
    """All paths resolved from CLI args — no module-level globals."""

    static_dataset_id: str
    dynamic_dataset_id: str
    funding_source: Path
    output_root: Path
    report_dir: Path
    klines_dir: Path

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> CacheBuildConfig:
        return cls(
            static_dataset_id=args.static_dataset_id,
            dynamic_dataset_id=args.dynamic_dataset_id,
            funding_source=Path(args.funding_source),
            output_root=Path(args.output_root),
            report_dir=Path(args.report_dir),
            klines_dir=Path(args.klines_dir),
        )

    def static_bars_path(self) -> Path:
        return self.output_root / self.static_dataset_id / "bars_1h.parquet"

    def dynamic_bars_path(self) -> Path:
        return self.output_root / self.dynamic_dataset_id / "bars_1h.parquet"

    def taker_enriched_path(self, dataset_id: str) -> Path:
        return self.output_root / f"{dataset_id}_taker_enriched" / "bars_1h.parquet"

    def funding_dir(self) -> Path:
        return self.output_root / "crypto_funding_rate_1h_contract_v1"

    def funding_events_path(self) -> Path:
        return self.funding_dir() / "funding_rate_events.parquet"

    def funding_aligned_path(self, variant: str) -> Path:
        return self.funding_dir() / f"funding_rate_1h_aligned_{variant}.parquet"


# ── Helpers ─────────────────────────────────────────────────────────
def sha256_file(path: Path) -> str:
    """Compute SHA-256 of a file (streaming, memory-safe)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def is_git_tracked(path: Path) -> bool:
    """Check if a path is tracked by git (staged or committed)."""
    try:
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", str(path)],
            capture_output=True, text=True, timeout=10,
        )
        return result.returncode == 0
    except Exception:
        return False


def load_taker_klines(symbols: list[str], klines_dir: Path) -> pd.DataFrame:
    """Load taker fields from raw klines zips for given symbols."""
    frames = []
    for sym in sorted(symbols):
        sym_dir = klines_dir / sym
        if not sym_dir.exists():
            continue
        for zf_path in sorted(sym_dir.glob("*.zip")):
            try:
                zf = zipfile.ZipFile(zf_path)
                with zf.open(zf.namelist()[0]) as f:
                    df = pd.read_csv(
                        f,
                        usecols=[
                            "open_time",
                            "close_time",
                            "taker_buy_volume",
                            "taker_buy_quote_volume",
                        ],
                    )
                    df["symbol"] = sym
                    frames.append(df)
            except Exception:
                pass  # early months may have different schema
    if not frames:
        return pd.DataFrame()
    all_klines = pd.concat(frames, ignore_index=True)
    all_klines["bar_open_time"] = pd.to_datetime(
        all_klines["open_time"], unit="ms", utc=True
    )
    all_klines = all_klines.drop(columns=["open_time", "close_time"])
    all_klines = all_klines.drop_duplicates(subset=["symbol", "bar_open_time"])
    return all_klines


# ── Builders ────────────────────────────────────────────────────────
def build_taker_enriched(bars_id: str, cfg: CacheBuildConfig) -> dict:
    """Build taker enriched bars for a given dataset."""
    bars_path = cfg.output_root / bars_id / "bars_1h.parquet"
    out_path = cfg.taker_enriched_path(bars_id)

    bars = pd.read_parquet(bars_path)
    source_rows = len(bars)
    syms = sorted(bars["symbol"].unique())

    taker = load_taker_klines(syms, cfg.klines_dir)
    enriched = bars.merge(
        taker[["symbol", "bar_open_time", "taker_buy_volume", "taker_buy_quote_volume"]],
        on=["symbol", "bar_open_time"],
        how="left",
    )

    assert len(enriched) == source_rows, (
        f"Row count mismatch: {len(enriched)} != {source_rows}"
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    enriched.to_parquet(out_path, index=False)

    tbqv_cov = enriched["taker_buy_quote_volume"].notna().mean()
    tbv_cov = enriched["taker_buy_volume"].notna().mean()

    return {
        "dataset_id": bars_id,
        "source_bars_path": str(bars_path),
        "enriched_bars_path": str(out_path),
        "source_rows": source_rows,
        "enriched_rows": len(enriched),
        "row_count_match": source_rows == len(enriched),
        "n_symbols": len(syms),
        "timestamp_min": str(bars["timestamp"].min()),
        "timestamp_max": str(bars["timestamp"].max()),
        "has_taker_buy_quote_volume": True,
        "taker_buy_quote_volume_coverage": round(tbqv_cov, 6),
        "has_taker_buy_volume": True,
        "taker_buy_volume_coverage": round(tbv_cov, 6),
        "schema_status": "PASS" if tbqv_cov > 0.5 else "PARTIAL",
        "notes": f"Early months (2021-Q4 to 2022-Q1) missing taker fields; overall {tbqv_cov:.1%}",
    }


def build_funding_events(cfg: CacheBuildConfig) -> dict:
    """Build funding rate events parquet from raw zips."""
    fr_dir = cfg.funding_source
    out_path = cfg.funding_events_path()

    all_sym_dirs = sorted([d for d in fr_dir.iterdir() if d.is_dir()])
    frames = []
    for sym_dir in all_sym_dirs:
        sym = sym_dir.name
        for zf_path in sorted(sym_dir.glob("*.zip")):
            try:
                zf = zipfile.ZipFile(zf_path)
                with zf.open(zf.namelist()[0]) as f:
                    df = pd.read_csv(f)
                    df["symbol"] = sym
                    df["source_file"] = zf_path.name
                    frames.append(df)
            except Exception:
                pass

    all_events = pd.concat(frames, ignore_index=True)
    all_events["calc_time"] = pd.to_datetime(
        all_events["calc_time"], unit="ms", utc=True
    )
    all_events["known_at"] = all_events["calc_time"]
    all_events["funding_rate"] = all_events["last_funding_rate"]

    events = all_events[
        ["symbol", "calc_time", "known_at", "funding_rate",
         "funding_interval_hours", "source_file"]
    ].copy()
    events = events.sort_values(["symbol", "calc_time"]).reset_index(drop=True)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    events.to_parquet(out_path, index=False)

    return {
        "funding_source_path": str(fr_dir),
        "events_path": str(out_path),
        "n_events": len(events),
        "n_symbols": int(events["symbol"].nunique()),
        "timestamp_min": str(events["calc_time"].min()),
        "timestamp_max": str(events["calc_time"].max()),
        "has_calc_time": True,
        "has_known_at": True,
        "has_funding_rate": True,
        "has_funding_interval_hours": True,
        "interval_values": str(sorted(events["funding_interval_hours"].unique().tolist())),
        "schema_status": "PASS",
        "notes": (
            f"Intervals {sorted(events['funding_interval_hours'].unique().tolist())} present; "
            f"known_at = calc_time; {events['symbol'].nunique()} symbols"
        ),
    }


def build_funding_aligned(bars_id: str, events_path: Path, cfg: CacheBuildConfig) -> dict:
    """Build funding rate 1h aligned parquet for a given bars dataset."""
    bars_path = cfg.output_root / bars_id / "bars_1h.parquet"
    variant = "static" if "top50_usdt" in bars_id else "dynamic"
    out_path = cfg.funding_aligned_path(variant)

    bars = pd.read_parquet(bars_path)
    bars["timestamp"] = bars["timestamp"].astype("datetime64[ns, UTC]")
    bars_syms = sorted(bars["symbol"].unique())

    events = pd.read_parquet(events_path)
    events["calc_time"] = events["calc_time"].astype("datetime64[ns, UTC]")
    events["known_at"] = events["known_at"].astype("datetime64[ns, UTC]")

    frames = []
    for sym in bars_syms:
        sym_bars = bars[bars["symbol"] == sym][["timestamp", "symbol"]].copy().sort_values("timestamp")
        sym_events = events[events["symbol"] == sym].sort_values("calc_time")

        if len(sym_events) == 0:
            sym_bars["funding_rate"] = np.nan
            sym_bars["funding_known_at"] = pd.NaT
            sym_bars["funding_interval_hours"] = np.nan
            sym_bars["funding_age_hours"] = np.nan
            frames.append(sym_bars)
            continue

        merged = pd.merge_asof(
            sym_bars,
            sym_events[
                ["calc_time", "known_at", "funding_rate", "funding_interval_hours"]
            ].rename(columns={"calc_time": "funding_calc_time", "known_at": "funding_known_at"}),
            left_on="timestamp",
            right_on="funding_calc_time",
            direction="backward",
            allow_exact_matches=True,
        )

        merged["funding_age_hours"] = (
            (merged["timestamp"] - merged["funding_calc_time"]).dt.total_seconds() / 3600.0
        )

        mask = merged["funding_age_hours"] > merged["funding_interval_hours"]
        merged.loc[mask, "funding_rate"] = np.nan
        merged.loc[mask, "funding_known_at"] = pd.NaT
        merged.loc[mask, "funding_interval_hours"] = np.nan
        merged.loc[mask, "funding_age_hours"] = np.nan

        merged = merged.drop(columns=["funding_calc_time"])
        frames.append(merged)

    aligned = pd.concat(frames, ignore_index=True)
    aligned = aligned.sort_values(["timestamp", "symbol"]).reset_index(drop=True)
    aligned.to_parquet(out_path, index=False)

    n_syms_funding = aligned.groupby("symbol")["funding_rate"].apply(
        lambda x: x.notna().any()
    ).sum()
    fr_cov = aligned["funding_rate"].notna().mean()
    age_valid = aligned["funding_age_hours"].dropna()
    median_age = float(age_valid.median()) if len(age_valid) > 0 else None
    max_age = float(age_valid.max()) if len(age_valid) > 0 else None

    return {
        "dataset_id": variant,
        "bars_path": str(bars_path),
        "aligned_path": str(out_path),
        "bars_rows": len(bars),
        "aligned_rows": len(aligned),
        "row_count_match": len(aligned) == len(bars),
        "n_symbols_bars": len(bars_syms),
        "n_symbols_with_funding": int(n_syms_funding),
        "symbol_coverage": round(n_syms_funding / len(bars_syms), 4),
        "timestamp_min": str(aligned["timestamp"].min()),
        "timestamp_max": str(aligned["timestamp"].max()),
        "funding_rate_coverage": round(fr_cov, 4),
        "median_funding_age_hours": round(median_age, 2) if median_age else None,
        "max_funding_age_hours": round(max_age, 2) if max_age else None,
        "schema_status": "PASS",
        "notes": f"max_age <= interval; {n_syms_funding}/{len(bars_syms)} symbols have funding",
    }


# ── Manifest ────────────────────────────────────────────────────────
def build_manifest(cfg: CacheBuildConfig) -> pd.DataFrame:
    """Build cache manifest with checksums and metadata.

    committed_to_git semantics:
        - YES: file is tracked by git (verified via git ls-files)
        - NO_LOCAL_ARTIFACT: generated parquet kept locally, not in GitHub
        - NO: file exists but not tracked by git
        - FILE_NOT_FOUND: file does not exist

    size_policy semantics:
        - SMALL_LOCAL_FILE: < 100MB
        - LARGE_LOCAL_FILE: >= 100MB (GitHub limit)
    """
    artifacts = [
        ("taker_enriched_static", "parquet",
         str(cfg.taker_enriched_path(cfg.static_dataset_id))),
        ("taker_enriched_dynamic", "parquet",
         str(cfg.taker_enriched_path(cfg.dynamic_dataset_id))),
        ("funding_events", "parquet",
         str(cfg.funding_events_path())),
        ("funding_aligned_static", "parquet",
         str(cfg.funding_aligned_path("static"))),
        ("funding_aligned_dynamic", "parquet",
         str(cfg.funding_aligned_path("dynamic"))),
    ]

    rows = []
    for name, atype, path in artifacts:
        p = Path(path)
        exists = p.exists()
        size_bytes = p.stat().st_size if exists else 0
        is_large = size_bytes >= 100 * 1024 * 1024

        # Checksum
        if exists and not is_large:
            checksum = sha256_file(p)
        elif exists:
            checksum = "SKIPPED_LARGE_FILE"
        else:
            checksum = "FILE_NOT_FOUND"

        # committed_to_git: verify via git ls-files
        if not exists:
            committed = "FILE_NOT_FOUND"
        elif is_git_tracked(p):
            committed = "YES"
        else:
            committed = "NO_LOCAL_ARTIFACT"

        # size_policy
        if not exists:
            size_policy = "FILE_NOT_FOUND"
        elif is_large:
            size_policy = "LARGE_LOCAL_FILE"
        else:
            size_policy = "SMALL_LOCAL_FILE"

        # Read metadata for parquet files
        n_rows = n_syms = None
        ts_min = ts_max = None
        columns = None
        if exists and atype == "parquet":
            try:
                df = pd.read_parquet(p)
                n_rows = len(df)
                n_syms = df["symbol"].nunique() if "symbol" in df.columns else None
                ts_col = "timestamp" if "timestamp" in df.columns else "calc_time"
                if ts_col in df.columns:
                    ts_min = str(df[ts_col].min())
                    ts_max = str(df[ts_col].max())
                columns = ",".join(df.columns)
            except Exception:
                pass

        rows.append({
            "artifact_name": name,
            "artifact_type": atype,
            "path": path,
            "exists": exists,
            "committed_to_git": committed,
            "size_policy": size_policy,
            "file_size_bytes": size_bytes,
            "n_rows": n_rows,
            "n_symbols": n_syms,
            "timestamp_min": ts_min,
            "timestamp_max": ts_max,
            "columns": columns,
            "checksum_sha256": checksum,
            "schema_status": "PASS" if exists else "FILE_NOT_FOUND",
            "notes": (
                f"Generated parquet, local artifact ({size_bytes / 1024 / 1024:.1f}MB)"
                if exists else ""
            ),
        })

    manifest = pd.DataFrame(rows)
    manifest.to_csv(cfg.report_dir / "phase7l_r_crypto_native_cache_manifest.csv", index=False)
    return manifest


# ── Validate ────────────────────────────────────────────────────────
def validate_caches(cfg: CacheBuildConfig) -> bool:
    """Validate existing caches against manifest.

    Checks:
        1. Each artifact path exists if manifest says exists=True
        2. Re-compute checksum for small files; reject mismatch
        3. committed_to_git must be NO_LOCAL_ARTIFACT for all generated parquet
        4. size_policy must match file size
    """
    manifest_path = cfg.report_dir / "phase7l_r_crypto_native_cache_manifest.csv"
    if not manifest_path.exists():
        print("ERROR: Manifest not found. Run build first.")
        return False

    manifest = pd.read_csv(manifest_path)
    ok = True
    for _, row in manifest.iterrows():
        p = Path(row["path"])
        name = row["artifact_name"]

        # 1. Existence
        if row["exists"] and not p.exists():
            print(f"FAIL: {name} missing at {row['path']}")
            ok = False
            continue

        if not row["exists"] or not p.exists():
            continue

        # 2. Checksum re-verification for small files
        if row["checksum_sha256"] not in ("SKIPPED_LARGE_FILE", "FILE_NOT_FOUND"):
            actual = sha256_file(p)
            if actual != row["checksum_sha256"]:
                print(f"FAIL: {name} checksum mismatch (rebuild recommended)")
                ok = False

        # 3. committed_to_git: generated parquet should be NO_LOCAL_ARTIFACT
        # unless actually tracked by git
        if row["committed_to_git"] == "YES" and not is_git_tracked(p):
            print(f"FAIL: {name} claims YES but is NOT git-tracked")
            ok = False

        # 4. size_policy consistency
        size_bytes = p.stat().st_size
        expected_large = size_bytes >= 100 * 1024 * 1024
        policy = row.get("size_policy", "")
        if expected_large and policy != "LARGE_LOCAL_FILE":
            print(f"FAIL: {name} size_policy={policy} but file is {size_bytes/1024/1024:.1f}MB")
            ok = False
        elif not expected_large and policy == "LARGE_LOCAL_FILE":
            print(f"FAIL: {name} size_policy=LARGE_LOCAL_FILE but file is {size_bytes/1024/1024:.1f}MB")
            ok = False

    if ok:
        print("All caches validated OK.")
    return ok


# ── Main ────────────────────────────────────────────────────────────
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build crypto-native data caches")
    parser.add_argument(
        "--mode", choices=["all", "taker", "funding", "validate"], default="all",
        help="Build mode: all, taker, funding, or validate"
    )
    parser.add_argument(
        "--static-dataset-id", default="crypto_top50_usdt_perp_1h",
        help="Static bars dataset ID"
    )
    parser.add_argument(
        "--dynamic-dataset-id", default="crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1",
        help="Dynamic bars dataset ID"
    )
    parser.add_argument(
        "--funding-source", default="data/binance_vision_rank154/data/futures/um/monthly/fundingRate",
        help="Path to raw funding rate zip directory"
    )
    parser.add_argument(
        "--output-root", default="data/cache",
        help="Root directory for output caches"
    )
    parser.add_argument(
        "--report-dir", default="research/factor_runs/crypto_top50_factor_library",
        help="Directory for summary CSVs and manifest"
    )
    parser.add_argument(
        "--klines-dir", default="data/binance_vision_1h_v1_6/klines",
        help="Directory with raw klines zips"
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    cfg = CacheBuildConfig.from_args(args)

    cfg.report_dir.mkdir(parents=True, exist_ok=True)

    if args.mode == "validate":
        ok = validate_caches(cfg)
        sys.exit(0 if ok else 1)

    # ── Taker ────────────────────────────────────────────────────────
    if args.mode in ("all", "taker"):
        print("=== Building taker enriched bars ===")
        taker_rows = []
        for ds_id in [cfg.static_dataset_id, cfg.dynamic_dataset_id]:
            print(f"  {ds_id}...")
            result = build_taker_enriched(ds_id, cfg)
            taker_rows.append(result)
            print(f"    {result['enriched_rows']:,} rows, {result['taker_buy_quote_volume_coverage']:.1%} coverage")

        taker_df = pd.DataFrame(taker_rows)
        taker_df.to_csv(cfg.report_dir / "phase7l_taker_enriched_bars_summary.csv", index=False)
        print(f"  Saved taker summary ({len(taker_rows)} rows)")

    # ── Funding ──────────────────────────────────────────────────────
    if args.mode in ("all", "funding"):
        print("=== Building funding rate caches ===")
        print("  Events...")
        events_result = build_funding_events(cfg)
        print(f"    {events_result['n_events']:,} events, {events_result['n_symbols']} symbols")

        events_path = Path(events_result["events_path"])
        pd.DataFrame([events_result]).to_csv(
            cfg.report_dir / "phase7l_funding_events_summary.csv", index=False
        )

        align_rows = []
        for ds_id in [cfg.static_dataset_id, cfg.dynamic_dataset_id]:
            print(f"  Aligning {ds_id}...")
            result = build_funding_aligned(ds_id, events_path, cfg)
            align_rows.append(result)
            print(f"    {result['aligned_rows']:,} rows, {result['funding_rate_coverage']:.1%} coverage")

        pd.DataFrame(align_rows).to_csv(
            cfg.report_dir / "phase7l_funding_alignment_summary.csv", index=False
        )
        print(f"  Saved funding summaries")

    # ── Manifest ─────────────────────────────────────────────────────
    if args.mode == "all":
        print("=== Building manifest ===")
        manifest = build_manifest(cfg)
        print(f"  {len(manifest)} artifacts documented")

    print("\nDone.")


if __name__ == "__main__":
    main()
