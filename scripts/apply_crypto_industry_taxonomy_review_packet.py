#!/usr/bin/env python3
"""Apply manually reviewed taxonomy batch packet targets to a source CSV.

This helper only copies explicit reviewer target fields into the reviewed
taxonomy source workbook. It does not infer taxonomy groups, approve CoinGecko
categories, build the parquet artifact, or register factors.
"""
from __future__ import annotations

import argparse
import glob
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "data" / "sources" / "crypto_industry_taxonomy_contract_v1" / "symbol_taxonomy.csv"
DEFAULT_PACKET = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_diagnostics" / "industry_taxonomy_review_batch_001.csv"
DEFAULT_BARS = (
    ROOT
    / "data"
    / "cache"
    / "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1"
    / "bars_1h.parquet"
)
TARGET_COLUMNS = [
    "target_sector",
    "target_industry",
    "target_subindustry",
    "target_quality_flag",
    "target_known_at",
    "target_effective_from",
]
BATCH_PACKET_RE = re.compile(r"industry_taxonomy_review_batch_(\d+)\.csv$")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_crypto_industry_taxonomy_contract import REQUIRED_COLUMNS, VALID_QUALITY_FLAGS  # noqa: E402
from validate_crypto_industry_taxonomy_review_packet import (  # noqa: E402
    _latest_bar_timestamp,
    validate_review_packet,
)


def _require_columns(df: pd.DataFrame, required: set[str], name: str) -> None:
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{name} missing required columns: {sorted(missing)}")


def _batch_id_from_path(path: Path) -> int:
    match = BATCH_PACKET_RE.match(path.name)
    return int(match.group(1)) if match else 0


def _raise_if_packet_validation_fails(
    source: pd.DataFrame,
    packet: pd.DataFrame,
    *,
    latest_bar: pd.Timestamp | None = None,
) -> None:
    report = validate_review_packet(
        packet,
        source=source,
        latest_bar=latest_bar,
        allow_no_ok=True,
    )
    failed = [row for row in report["checks"] if not bool(row["passed"])]
    approved_rows = int(report.get("approved_packet_rows", 0) or 0)
    blocking_failed = [
        row
        for row in failed
        if not (approved_rows == 0 and row["check"] == "has_ok_target_rows")
    ]
    if blocking_failed:
        failed_checks = "|".join(str(row["check"]) for row in blocking_failed)
        blocker = report.get("blocker") or "packet_validation_checks_failed"
        raise ValueError(f"packet failed validation before apply: {blocker}; checks={failed_checks}")


def apply_review_packet(
    source: pd.DataFrame,
    packet: pd.DataFrame,
    *,
    latest_bar: pd.Timestamp | None = None,
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Return updated source and a summary after applying explicit OK targets."""
    _require_columns(source, REQUIRED_COLUMNS, "source")
    _require_columns(packet, {"symbol", *TARGET_COLUMNS}, "packet")
    _raise_if_packet_validation_fails(source, packet, latest_bar=latest_bar)

    updated = source.copy().fillna("")
    updated["symbol"] = updated["symbol"].astype(str)
    packet_work = packet.copy().fillna("")
    packet_work["symbol"] = packet_work["symbol"].astype(str)
    packet_work["target_quality_flag"] = packet_work["target_quality_flag"].astype(str)

    bad_flags = sorted(set(packet_work["target_quality_flag"]) - (VALID_QUALITY_FLAGS | {""}))
    if bad_flags:
        raise ValueError(f"packet has invalid target_quality_flag values: {bad_flags}")

    duplicate_symbols = sorted(packet_work.loc[packet_work["symbol"].duplicated(), "symbol"].unique().tolist())
    if duplicate_symbols:
        raise ValueError(f"packet has duplicate symbols: {duplicate_symbols}")

    approved = packet_work[packet_work["target_quality_flag"].eq("OK")].copy()
    if approved.empty:
        return updated, {
            "packet_rows": int(len(packet_work)),
            "approved_packet_rows": 0,
            "updated_rows": 0,
            "updated_symbols": "",
            "skipped_packet_rows": int(len(packet_work)),
            "note": "No target_quality_flag == OK rows to apply.",
        }

    missing_source = sorted(set(approved["symbol"]) - set(updated["symbol"]))
    if missing_source:
        raise ValueError(f"approved packet symbols missing from source: {missing_source}")

    for target_col in TARGET_COLUMNS:
        missing = approved[target_col].astype(str).str.strip().eq("")
        if missing.any():
            symbols = approved.loc[missing, "symbol"].astype(str).tolist()
            raise ValueError(f"approved packet rows missing {target_col}: {symbols}")

    timestamp_cols = ["target_known_at", "target_effective_from"]
    for col in timestamp_cols:
        parsed = pd.to_datetime(approved[col], utc=True, errors="coerce")
        if parsed.isna().any():
            symbols = approved.loc[parsed.isna(), "symbol"].astype(str).tolist()
            raise ValueError(f"approved packet rows have invalid {col}: {symbols}")

    source_idx_by_symbol = {symbol: idx for idx, symbol in updated["symbol"].items()}
    updated_symbols: list[str] = []
    for row in approved.itertuples(index=False):
        symbol = str(row.symbol)
        idx = source_idx_by_symbol[symbol]
        updated.loc[idx, "sector"] = str(row.target_sector).strip()
        updated.loc[idx, "industry"] = str(row.target_industry).strip()
        updated.loc[idx, "subindustry"] = str(row.target_subindustry).strip()
        updated.loc[idx, "quality_flag"] = str(row.target_quality_flag).strip()
        updated.loc[idx, "known_at"] = str(row.target_known_at).strip()
        updated.loc[idx, "effective_from"] = str(row.target_effective_from).strip()
        updated_symbols.append(symbol)

    return updated, {
        "packet_rows": int(len(packet_work)),
        "approved_packet_rows": int(len(approved)),
        "updated_rows": int(len(updated_symbols)),
        "updated_symbols": "|".join(updated_symbols),
        "skipped_packet_rows": int(len(packet_work) - len(approved)),
        "note": "Applied explicit OK target rows only; run source, artifact, contract, and coverage gates next.",
    }


def apply_review_packets(
    source: pd.DataFrame,
    packets: list[pd.DataFrame],
    *,
    latest_bar: pd.Timestamp | None = None,
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Return updated source and summary after sequentially applying packets."""
    if not packets:
        raise ValueError("at least one packet is required")

    updated = source.copy()
    packet_summaries: list[dict[str, object]] = []
    updated_symbols: list[str] = []
    approved_symbol_sources: dict[str, int] = {}
    for index, packet in enumerate(packets, start=1):
        updated, summary = apply_review_packet(updated, packet, latest_bar=latest_bar)
        packet_summaries.append({"packet_index": index, **summary})
        symbols = str(summary.get("updated_symbols", ""))
        if symbols:
            packet_symbols = [symbol for symbol in symbols.split("|") if symbol]
            duplicate_symbols = [
                symbol for symbol in packet_symbols
                if symbol in approved_symbol_sources
            ]
            if duplicate_symbols:
                detail = "|".join(
                    f"{symbol}:packet_{approved_symbol_sources[symbol]}->packet_{index}"
                    for symbol in sorted(duplicate_symbols)
                )
                raise ValueError(f"approved symbols duplicated across packets: {detail}")
            for symbol in packet_symbols:
                approved_symbol_sources[symbol] = index
            updated_symbols.extend(packet_symbols)

    return updated, {
        "packet_count": int(len(packets)),
        "packet_rows": int(sum(int(row["packet_rows"]) for row in packet_summaries)),
        "approved_packet_rows": int(sum(int(row["approved_packet_rows"]) for row in packet_summaries)),
        "updated_rows": int(sum(int(row["updated_rows"]) for row in packet_summaries)),
        "updated_symbols": "|".join(updated_symbols),
        "skipped_packet_rows": int(sum(int(row["skipped_packet_rows"]) for row in packet_summaries)),
        "packet_summaries": packet_summaries,
        "note": "Applied explicit OK target rows from reviewed packets only; run source, artifact, contract, and coverage gates next.",
    }


def apply_review_packet_from_paths(
    source_csv: Path,
    packet_csv: Path,
    output_csv: Path,
    *,
    bars_path: Path | None = None,
) -> dict[str, object]:
    return apply_review_packets_from_paths(source_csv, [packet_csv], output_csv, bars_path=bars_path)


def packet_paths_from_glob(packet_glob: str) -> list[Path]:
    paths = [Path(path) for path in glob.glob(packet_glob)]
    packet_paths = [path for path in paths if BATCH_PACKET_RE.match(path.name)]
    return sorted(packet_paths, key=lambda path: (_batch_id_from_path(path), str(path)))


def apply_review_packets_from_paths(
    source_csv: Path,
    packet_csvs: list[Path],
    output_csv: Path,
    *,
    bars_path: Path | None = None,
) -> dict[str, object]:
    if not source_csv.exists():
        raise FileNotFoundError(f"Source CSV not found: {source_csv}")
    if not packet_csvs:
        raise ValueError("At least one packet CSV is required")
    missing_packets = [str(packet_csv) for packet_csv in packet_csvs if not packet_csv.exists()]
    if missing_packets:
        raise FileNotFoundError(f"Packet CSV not found: {missing_packets}")
    source = pd.read_csv(source_csv).fillna("")
    packets = [pd.read_csv(packet_csv).fillna("") for packet_csv in packet_csvs]
    latest_bar = None
    if bars_path is not None:
        checks: list[dict[str, object]] = []
        latest_bar = _latest_bar_timestamp(bars_path, checks)
        failed = [row for row in checks if not bool(row["passed"])]
        if failed:
            failed_checks = "|".join(str(row["check"]) for row in failed)
            raise ValueError(f"bars failed validation before apply: checks={failed_checks}")
    updated, summary = apply_review_packets(source, packets, latest_bar=latest_bar)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    updated.to_csv(output_csv, index=False)
    return {
        **summary,
        "source_csv": str(source_csv),
        "packet_csv": "|".join(str(packet_csv) for packet_csv in packet_csvs),
        "output_csv": str(output_csv),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-csv", default=str(DEFAULT_SOURCE), help="Current taxonomy source CSV")
    parser.add_argument(
        "--packet-csv",
        action="append",
        default=None,
        help="Reviewed batch packet CSV; pass multiple times to apply several packets in order",
    )
    parser.add_argument("--packet-glob", default="", help="Glob for reviewed batch packet CSVs")
    parser.add_argument(
        "--bars-path",
        default=str(DEFAULT_BARS),
        help="Bars parquet used to reject reviewed rows known/effective after the latest evaluated bar",
    )
    parser.add_argument("--output-csv", required=True, help="Output taxonomy source CSV path")
    args = parser.parse_args()

    try:
        if args.packet_glob:
            packet_csvs = packet_paths_from_glob(args.packet_glob)
            if not packet_csvs:
                raise FileNotFoundError(f"No batch packet CSVs matched: {args.packet_glob}")
        else:
            packet_csvs = [Path(path) for path in (args.packet_csv or [str(DEFAULT_PACKET)])]
        summary = apply_review_packets_from_paths(
            Path(args.source_csv),
            packet_csvs,
            Path(args.output_csv),
            bars_path=Path(args.bars_path),
        )
    except Exception as exc:
        print(f"ERROR: {exc}", flush=True)
        return 1

    print("Applied crypto industry taxonomy review packet")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
