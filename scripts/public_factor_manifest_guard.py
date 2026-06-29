"""Shared guards for public factor manifest lifecycle statuses."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_FACTOR_MANIFEST = ROOT / "docs" / "factor_library" / "public_factor_candidate_manifest.csv"


def load_skipped_public_factor_ids(path: Path = PUBLIC_FACTOR_MANIFEST) -> set[str]:
    """Load public manifest factor IDs that are explicitly skipped."""
    if not path.exists():
        return set()
    with path.open(newline="") as handle:
        return {
            row["factor_id"]
            for row in csv.DictReader(handle)
            if row.get("implementation_status", "").startswith("skipped_")
        }


def find_skipped_public_factor_ids(
    factor_ids: Sequence[str],
    skipped_public_factor_ids: set[str] | None = None,
) -> list[str]:
    """Return requested IDs that are explicitly skipped in the public manifest."""
    skipped = skipped_public_factor_ids
    if skipped is None:
        skipped = load_skipped_public_factor_ids()
    return [fid for fid in factor_ids if fid in skipped]


def raise_for_skipped_public_factor_ids(
    factor_ids: Sequence[str],
    *,
    action: str,
    skipped_public_factor_ids: set[str] | None = None,
) -> None:
    """Raise ValueError if any requested IDs are skipped public manifest rows."""
    skipped = find_skipped_public_factor_ids(factor_ids, skipped_public_factor_ids)
    if skipped:
        raise ValueError(f"Public manifest skipped factor IDs cannot be {action}: {skipped}")
