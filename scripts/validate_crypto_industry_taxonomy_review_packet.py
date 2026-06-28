#!/usr/bin/env python3
"""Validate a manually reviewed crypto industry taxonomy batch packet.

This is the pre-apply gate for Alpha101 IndNeutralize taxonomy review packets.
It checks only reviewer-provided target fields; it does not infer taxonomy
groups, modify the source workbook, build the parquet artifact, or register
factors.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKET = (
    ROOT
    / "research"
    / "factor_runs"
    / "crypto_top50_factor_library"
    / "factor_diagnostics"
    / "industry_taxonomy_review_batch_001.csv"
)
DEFAULT_SOURCE = ROOT / "data" / "sources" / "crypto_industry_taxonomy_contract_v1" / "symbol_taxonomy.csv"
DEFAULT_BARS = (
    ROOT
    / "data"
    / "cache"
    / "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1"
    / "bars_1h.parquet"
)
DEFAULT_OUT_DIR = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_diagnostics"

TARGET_COLUMNS = [
    "target_sector",
    "target_industry",
    "target_subindustry",
    "target_quality_flag",
    "target_known_at",
    "target_effective_from",
]

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_crypto_industry_taxonomy_contract import REQUIRED_COLUMNS, VALID_QUALITY_FLAGS  # noqa: E402


def _check(checks: list[dict[str, object]], name: str, passed: bool, detail: str) -> None:
    checks.append({"check": name, "passed": bool(passed), "detail": detail})


def _pipe_join(values: list[str] | set[str]) -> str:
    return "|".join(sorted(str(v) for v in values if str(v)))


def _load_csv(path: Path, label: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"{label} not found: {path}")
    return pd.read_csv(path).fillna("")


def _latest_bar_timestamp(bars_path: Path, checks: list[dict[str, object]]) -> pd.Timestamp | None:
    if not bars_path.exists():
        _check(checks, "bars_path_exists", False, f"File not found: {bars_path}")
        return None
    bars = pd.read_parquet(bars_path, columns=["timestamp"])
    ts = pd.to_datetime(bars["timestamp"], utc=True, errors="coerce").dropna()
    if ts.empty:
        _check(checks, "bars_have_timestamps", False, "No valid timestamps")
        return None
    latest = ts.max()
    _check(checks, "bars_have_timestamps", True, latest.strftime("%Y-%m-%dT%H:%M:%SZ"))
    return latest


def validate_review_packet(
    packet: pd.DataFrame,
    *,
    source: pd.DataFrame | None = None,
    latest_bar: pd.Timestamp | None = None,
    allow_no_ok: bool = False,
) -> dict[str, object]:
    """Return validation report for a reviewed taxonomy batch packet."""
    checks: list[dict[str, object]] = []
    work = packet.copy().fillna("")

    required_packet_columns = {"symbol", *TARGET_COLUMNS}
    missing_packet_cols = required_packet_columns - set(work.columns)
    _check(
        checks,
        "packet_required_columns",
        not missing_packet_cols,
        f"Missing: {sorted(missing_packet_cols)}" if missing_packet_cols else "All present",
    )
    if missing_packet_cols:
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "packet_rows": int(len(work)),
            "approved_packet_rows": 0,
            "approved_symbols": "",
            "approved_bar_count_share": None,
            "approved_quote_volume_share": None,
            "allow_no_ok": allow_no_ok,
            "latest_bar_timestamp": "",
            "overall_pass": False,
            "blocker": "packet_missing_required_columns",
            "checks": checks,
        }

    for col in ["symbol", *TARGET_COLUMNS]:
        work[col] = work[col].astype(str).str.strip()

    non_empty_symbols = work["symbol"].ne("")
    _check(
        checks,
        "packet_symbols_non_empty",
        bool(non_empty_symbols.all()),
        f"{int(non_empty_symbols.sum())}/{len(work)} non-empty",
    )

    duplicate_symbols = sorted(work.loc[work["symbol"].duplicated(), "symbol"].unique().tolist())
    _check(
        checks,
        "packet_symbols_unique",
        not duplicate_symbols,
        f"Duplicates: {duplicate_symbols}" if duplicate_symbols else "No duplicates",
    )

    bad_flags = sorted(set(work["target_quality_flag"]) - (VALID_QUALITY_FLAGS | {""}))
    _check(
        checks,
        "target_quality_flag_domain",
        not bad_flags,
        f"Bad flags: {bad_flags}" if bad_flags else "OK/REVIEW/BLOCKED/blank only",
    )

    approved = work[work["target_quality_flag"].eq("OK")].copy()
    _check(
        checks,
        "has_ok_target_rows",
        bool(allow_no_ok or len(approved) > 0),
        f"{len(approved)} OK target rows",
    )

    for col in ["target_sector", "target_industry", "target_subindustry", "target_known_at", "target_effective_from"]:
        missing = approved[col].eq("")
        _check(
            checks,
            f"ok_rows_have_{col}",
            not bool(missing.any()),
            f"{int(missing.sum())} OK rows missing {col}",
        )

    known_at = pd.to_datetime(approved["target_known_at"], utc=True, errors="coerce") if not approved.empty else pd.Series(dtype="datetime64[ns, UTC]")
    effective_from = pd.to_datetime(approved["target_effective_from"], utc=True, errors="coerce") if not approved.empty else pd.Series(dtype="datetime64[ns, UTC]")

    bad_known_at = approved.index[known_at.isna()].tolist() if not approved.empty else []
    bad_effective_from = approved.index[effective_from.isna()].tolist() if not approved.empty else []
    _check(
        checks,
        "ok_rows_valid_target_known_at",
        not bad_known_at,
        f"{len(bad_known_at)} OK rows have invalid target_known_at",
    )
    _check(
        checks,
        "ok_rows_valid_target_effective_from",
        not bad_effective_from,
        f"{len(bad_effective_from)} OK rows have invalid target_effective_from",
    )

    if not approved.empty:
        effective_after_known = effective_from.notna() & known_at.notna() & (effective_from > known_at)
        symbols = approved.loc[effective_after_known, "symbol"].tolist()
        _check(
            checks,
            "ok_effective_from_not_after_known_at",
            not bool(effective_after_known.any()),
            f"Symbols: {symbols}" if symbols else "All effective_from <= known_at",
        )
    else:
        _check(checks, "ok_effective_from_not_after_known_at", True, "No OK rows")

    latest_bar_str = ""
    if latest_bar is not None:
        latest_bar_str = latest_bar.strftime("%Y-%m-%dT%H:%M:%SZ")
        known_after_bar = known_at.notna() & (known_at > latest_bar)
        effective_after_bar = effective_from.notna() & (effective_from > latest_bar)
        _check(
            checks,
            "ok_known_at_not_after_latest_bar",
            not bool(known_after_bar.any()),
            (
                f"{int(known_after_bar.sum())}/{len(approved)} OK rows known after latest bar {latest_bar_str}"
                if len(approved)
                else "No OK rows"
            ),
        )
        _check(
            checks,
            "ok_effective_from_not_after_latest_bar",
            not bool(effective_after_bar.any()),
            (
                f"{int(effective_after_bar.sum())}/{len(approved)} OK rows effective after latest bar {latest_bar_str}"
                if len(approved)
                else "No OK rows"
            ),
        )

    if source is not None:
        src = source.copy().fillna("")
        missing_source_cols = REQUIRED_COLUMNS - set(src.columns)
        _check(
            checks,
            "source_required_columns",
            not missing_source_cols,
            f"Missing: {sorted(missing_source_cols)}" if missing_source_cols else "All present",
        )
        if "symbol" in src.columns:
            src["symbol"] = src["symbol"].astype(str).str.strip()
            source_duplicates = sorted(src.loc[src["symbol"].duplicated(), "symbol"].unique().tolist())
            _check(
                checks,
                "source_symbols_unique",
                not source_duplicates,
                f"Duplicates: {source_duplicates}" if source_duplicates else "No duplicates",
            )
            missing_from_source = sorted(set(work["symbol"]) - set(src["symbol"]))
            _check(
                checks,
                "packet_symbols_exist_in_source",
                not missing_from_source,
                f"Missing: {missing_from_source}" if missing_from_source else "All packet symbols found",
            )

    approved_bar_share = None
    if "bar_count_share" in work.columns:
        approved_bar_share = float(pd.to_numeric(approved.get("bar_count_share"), errors="coerce").fillna(0).sum())
    approved_quote_share = None
    if "quote_volume_share" in work.columns:
        approved_quote_share = float(pd.to_numeric(approved.get("quote_volume_share"), errors="coerce").fillna(0).sum())

    failed = [c["check"] for c in checks if not bool(c["passed"])]
    if not failed:
        blocker = ""
    elif "has_ok_target_rows" in failed:
        blocker = "packet_has_no_ok_target_rows"
    elif "ok_known_at_not_after_latest_bar" in failed:
        blocker = "packet_ok_known_at_after_latest_bar"
    elif "packet_symbols_exist_in_source" in failed:
        blocker = "packet_symbols_missing_from_source"
    else:
        blocker = "packet_validation_checks_failed"

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "packet_rows": int(len(work)),
        "approved_packet_rows": int(len(approved)),
        "approved_symbols": _pipe_join(approved["symbol"].tolist()),
        "approved_bar_count_share": approved_bar_share,
        "approved_quote_volume_share": approved_quote_share,
        "allow_no_ok": allow_no_ok,
        "latest_bar_timestamp": latest_bar_str,
        "overall_pass": not failed,
        "blocker": blocker,
        "checks": checks,
    }


def validate_review_packet_from_paths(
    packet_csv: Path,
    *,
    source_csv: Path | None = None,
    bars_path: Path | None = None,
    allow_no_ok: bool = False,
) -> dict[str, object]:
    checks: list[dict[str, object]] = []
    packet = _load_csv(packet_csv, "packet CSV")
    source = _load_csv(source_csv, "source CSV") if source_csv is not None else None
    latest_bar = _latest_bar_timestamp(bars_path, checks) if bars_path is not None else None
    report = validate_review_packet(packet, source=source, latest_bar=latest_bar, allow_no_ok=allow_no_ok)
    report["packet_csv"] = str(packet_csv)
    report["source_csv"] = str(source_csv) if source_csv is not None else ""
    report["bars_path"] = str(bars_path) if bars_path is not None else ""
    if checks:
        report["checks"] = checks + list(report["checks"])
        report["overall_pass"] = all(bool(c["passed"]) for c in report["checks"])
        if not report["overall_pass"] and not report["blocker"]:
            report["blocker"] = "packet_validation_checks_failed"
    return report


def write_packet_validation_reports(
    report: dict[str, object],
    out_dir: Path = DEFAULT_OUT_DIR,
    report_stem: str = "industry_taxonomy_review_packet_validation",
) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = str(report_stem).strip()
    if not stem:
        raise ValueError("report_stem must be non-empty")
    if "/" in stem or "\\" in stem:
        raise ValueError("report_stem must be a file stem, not a path")
    out_json = out_dir / f"{stem}.json"
    out_csv = out_dir / f"{stem}_checks.csv"
    out_json.write_text(json.dumps(report, indent=2, default=str) + "\n")
    pd.DataFrame(report["checks"]).to_csv(out_csv, index=False)
    return out_json, out_csv


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet-csv", default=str(DEFAULT_PACKET), help="Reviewed batch packet CSV")
    parser.add_argument("--source-csv", default=str(DEFAULT_SOURCE), help="Current taxonomy source CSV")
    parser.add_argument("--bars-path", default=str(DEFAULT_BARS), help="Factor bars parquet for point-in-time checks")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Output diagnostics directory")
    parser.add_argument("--report-stem", default="industry_taxonomy_review_packet_validation", help="Output report file stem under --out-dir")
    parser.add_argument("--allow-no-ok", action="store_true", help="Allow structural validation before any rows are approved")
    args = parser.parse_args()

    try:
        report = validate_review_packet_from_paths(
            Path(args.packet_csv),
            source_csv=Path(args.source_csv) if args.source_csv else None,
            bars_path=Path(args.bars_path) if args.bars_path else None,
            allow_no_ok=bool(args.allow_no_ok),
        )
    except Exception as exc:
        print(f"ERROR: {exc}", flush=True)
        return 1

    print("Crypto industry taxonomy review packet validation")
    print(f"  packet: {report['packet_csv']}")
    print(f"  rows: {report['packet_rows']}")
    print(f"  approved_rows: {report['approved_packet_rows']}")
    print(f"  approved_bar_count_share: {report['approved_bar_count_share']}")
    print(f"  approved_quote_volume_share: {report['approved_quote_volume_share']}")
    if report["latest_bar_timestamp"]:
        print(f"  latest_bar_timestamp: {report['latest_bar_timestamp']}")
    print(f"  overall_pass: {report['overall_pass']}")
    print(f"  blocker: {report['blocker']}")
    out_json, out_csv = write_packet_validation_reports(report, Path(args.out_dir), report_stem=args.report_stem)
    print(f"Saved: {out_json}")
    print(f"Saved: {out_csv}")
    return 0 if report["overall_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
