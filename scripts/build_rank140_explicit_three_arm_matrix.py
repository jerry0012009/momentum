from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser(
        description=(
            "Build Rank140 explicit 3-arm returns matrix (baseline / gate_kept / gate_veto) from a baseline trade log "
            "and a strict-variant presence test.\n\n"
            "Arms semantics (per row = one baseline trade):\n"
            "- baseline: always present (baseline gross_return)\n"
            "- gate_kept: baseline gross_return if strict variant trade exists for same (asset, signal_ts); else blank (no-trade)\n"
            "- gate_veto: baseline gross_return if strict variant trade does NOT exist; else blank (no-trade)"
        )
    )
    p.add_argument("--trade-log", required=True, help="Input trade_log.csv with columns asset, variant, signal_ts, gross_return")
    p.add_argument("--strict-variant", required=True, help="Variant name that defines gate-kept set")
    p.add_argument("--out-csv", required=True)
    p.add_argument("--out-meta", required=True)
    return p.parse_args()


def main():
    args = parse_args()
    rows = list(csv.DictReader(open(args.trade_log, newline="")))

    baseline = [r for r in rows if r.get("variant") == "baseline"]
    strict = [r for r in rows if r.get("variant") == args.strict_variant]

    strict_keys = {(r["asset"], r["signal_ts"]) for r in strict}

    baseline.sort(key=lambda r: (r["asset"], r["signal_ts"]))

    out_path = Path(args.out_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "asset",
        "signal_ts",
        "gross_ret_baseline",
        "gross_ret_gate_kept",
        "gross_ret_gate_veto",
    ]

    kept = 0
    veto = 0

    with out_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in baseline:
            key = (r["asset"], r["signal_ts"])
            gross = float(r["gross_return"])
            is_kept = key in strict_keys
            if is_kept:
                kept += 1
            else:
                veto += 1
            w.writerow(
                {
                    "asset": r["asset"],
                    "signal_ts": r["signal_ts"],
                    "gross_ret_baseline": gross,
                    "gross_ret_gate_kept": (gross if is_kept else ""),
                    "gross_ret_gate_veto": (gross if (not is_kept) else ""),
                }
            )

    meta = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "source_trade_log": args.trade_log,
        "strict_variant": args.strict_variant,
        "baseline_rows": len(baseline),
        "strict_rows": len(strict),
        "kept_rows": kept,
        "veto_rows": veto,
        "mapping": (
            "Explicit 3-arm matrix: baseline always = baseline gross_return; "
            "gate_kept non-empty iff strict variant trade exists for same (asset,signal_ts); "
            "gate_veto non-empty iff strict variant trade does NOT exist."
        ),
        "notes": "Blank cell means no-trade (cost should not be charged).",
    }

    meta_path = Path(args.out_meta)
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2))

    print(str(out_path))
    print(str(meta_path))


if __name__ == "__main__":
    main()
