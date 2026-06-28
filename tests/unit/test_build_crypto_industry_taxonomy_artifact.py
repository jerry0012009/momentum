"""Tests for reviewed CSV -> validated taxonomy parquet intake."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from build_crypto_industry_taxonomy_artifact import build_taxonomy_artifact  # noqa: E402


def _valid_rows() -> pd.DataFrame:
    return pd.DataFrame({
        "symbol": ["AAAUSDT", "AAAUSDT", "BBBUSDT"],
        "known_at": ["2025-12-31 00:00Z", "2026-02-01 00:00Z", "2025-12-31 00:00Z"],
        "effective_from": ["2026-01-01 00:00Z", "2026-02-01 00:00Z", "2026-01-01 00:00Z"],
        "effective_to": ["2026-02-01 00:00Z", "", ""],
        "sector": ["L1", "L1", "L2"],
        "industry": ["L1a", "L1b", "L2a"],
        "subindustry": ["L1a1", "L1b1", "L2a1"],
        "taxonomy_version": ["v1", "v2", "v1"],
        "source": ["manual_review", "manual_review", "manual_review"],
        "quality_flag": ["OK", "OK", "OK"],
    })


def _status(checks, name: str) -> bool:
    return next(c for c in checks if c["check"] == name)["passed"]


def test_build_taxonomy_artifact_writes_parquet_and_reports(tmp_path: Path):
    input_csv = tmp_path / "symbol_taxonomy.csv"
    output = tmp_path / "cache" / "symbol_taxonomy.parquet"
    _valid_rows().to_csv(input_csv, index=False)

    checks = build_taxonomy_artifact(input_csv, output)

    assert all(c["passed"] for c in checks), checks
    assert output.exists()
    assert (output.parent / "industry_taxonomy_contract_check.json").exists()
    assert (output.parent / "industry_taxonomy_contract_check.csv").exists()

    out = pd.read_parquet(output)
    assert list(out["symbol"]) == ["AAAUSDT", "AAAUSDT", "BBBUSDT"]
    assert pd.api.types.is_datetime64_any_dtype(out["known_at"])


def test_build_taxonomy_artifact_removes_stale_output_when_contract_fails(tmp_path: Path):
    input_csv = tmp_path / "symbol_taxonomy.csv"
    output = tmp_path / "cache" / "symbol_taxonomy.parquet"
    output.parent.mkdir(parents=True)
    pd.DataFrame({"stale": [1]}).to_parquet(output, index=False)

    bad = _valid_rows()
    bad = bad.drop(columns=["known_at"])
    bad.to_csv(input_csv, index=False)

    checks = build_taxonomy_artifact(input_csv, output)

    assert not _status(checks, "required_columns")
    assert not output.exists()
    assert (output.parent / "industry_taxonomy_contract_check.json").exists()


def test_schema_only_template_does_not_build_artifact(tmp_path: Path):
    input_csv = tmp_path / "symbol_taxonomy.template.csv"
    output = tmp_path / "cache" / "symbol_taxonomy.parquet"
    input_csv.write_text(
        "symbol,known_at,effective_from,effective_to,sector,industry,subindustry,taxonomy_version,source,quality_flag\n"
    )

    checks = build_taxonomy_artifact(input_csv, output)

    assert not _status(checks, "non_empty")
    assert not output.exists()


def test_review_only_source_does_not_build_artifact(tmp_path: Path):
    input_csv = tmp_path / "symbol_taxonomy.csv"
    output = tmp_path / "cache" / "symbol_taxonomy.parquet"
    output.parent.mkdir(parents=True)
    pd.DataFrame({"stale": [1]}).to_parquet(output, index=False)

    review = _valid_rows()
    review["quality_flag"] = "REVIEW"
    review[["sector", "industry", "subindustry"]] = ""
    review.to_csv(input_csv, index=False)

    checks = build_taxonomy_artifact(input_csv, output)

    assert not _status(checks, "has_ok_rows")
    assert not output.exists()
