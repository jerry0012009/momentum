#!/usr/bin/env python3
"""Lightweight factor warning flag system.
Reads audit_v0 CSVs and metrics.json, outputs warning_flags.csv + summary.md.

This is NOT a pass/fail gate. It's a risk-awareness mechanism for diagnostic probes.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
UNIVERSE = "crypto_top50_usdt_perp_1h"
AUDIT = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "audit_v0"
METRICS = ROOT / "reports" / "artifacts" / "factor_eval" / UNIVERSE
OUTDIR = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "warning_flags"
FACTORS = ["mom_20h", "reversal_5h", "volatility_20h", "rsi_14h", "bb_zscore_20h"]
LABELS = ["ret_fwd_1h", "ret_fwd_4h", "ret_fwd_24h", "ret_fwd_72h"]

# ── thresholds (tuned for awareness, not elimination) ──
MONTHLY_CONSISTENCY_THRESHOLD = 0.70   # below = instability
OVERLAP_DROP_THRESHOLD = 0.70          # non-overlap t-stat drop > 70%
CONCENTRATION_THRESHOLD = 0.35         # symbol in Q5/Q1 > 35%
COVERAGE_THRESHOLD = 0.95              # below = low coverage
WINSORIZE_DROP_THRESHOLD = 0.30        # IC drop > 30% after winsorize


def clean(x: Any) -> float | None:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return None if (math.isnan(v) or math.isinf(v)) else v


def load_audit_csv(name: str) -> pd.DataFrame:
    path = AUDIT / name
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def load_metrics(factor: str, label: str) -> dict:
    path = METRICS / factor / "metrics.json"
    if not path.exists():
        return {}
    with open(path) as f:
        m = json.load(f)
    return m.get("label_metrics", {}).get(label, {})


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)

    # load audit outputs
    sign_df = load_audit_csv("ic_sign_consistency.csv")
    month_df = load_audit_csv("monthly_stability.csv")
    nonov_df = load_audit_csv("nonoverlap_metrics.csv")
    wins_df = load_audit_csv("winsorized_metrics.csv")
    sym_df = load_audit_csv("symbol_contribution.csv")

    rows = []

    for factor in FACTORS:
        for label in LABELS:
            flags = []
            m = load_metrics(factor, label)

            ic_mean = clean(m.get("IC_mean"))
            rankic_mean = clean(m.get("RankIC_mean"))
            spread_mean = clean(m.get("quantile_spread_mean"))
            coverage = clean(m.get("coverage"))

            # ── DIRECTION_CONFLICT ──
            if not sign_df.empty:
                row = sign_df[(sign_df["factor"] == factor) & (sign_df["label"] == label)]
                if not row.empty and not row.iloc[0].get("direction_consistent", True):
                    flags.append("DIRECTION_CONFLICT")

            # ── MONTHLY_INSTABILITY ──
            if not month_df.empty:
                msub = month_df[(month_df["factor"] == factor) & (month_df["label"] == label)]
                if not msub.empty:
                    ics = msub["IC_mean"].dropna()
                    if len(ics) > 0:
                        dom = 1 if (ics > 0).sum() >= (ics < 0).sum() else -1
                        ratio = ((ics > 0) == (dom > 0)).sum() / len(ics)
                        if ratio < MONTHLY_CONSISTENCY_THRESHOLD:
                            flags.append("MONTHLY_INSTABILITY")

            # ── OVERLAP_INFLATION ──
            if not nonov_df.empty and label in ("ret_fwd_24h", "ret_fwd_72h"):
                full_row = nonov_df[(nonov_df["factor"] == factor) & (nonov_df["label"] == label) & (nonov_df["mode"] == "full")]
                no_row = nonov_df[(nonov_df["factor"] == factor) & (nonov_df["label"] == label) & (nonov_df["mode"] == "nonoverlap")]
                if not full_row.empty and not no_row.empty:
                    tf = clean(full_row.iloc[0]["spread_t"])
                    tn = clean(no_row.iloc[0]["spread_t"])
                    if tf and tn and abs(tf) > 0:
                        drop = 1 - abs(tn) / abs(tf)
                        if drop > OVERLAP_DROP_THRESHOLD:
                            flags.append("OVERLAP_INFLATION")

            # ── OUTLIER_SENSITIVE ──
            if not wins_df.empty:
                raw = wins_df[(wins_df["factor"] == factor) & (wins_df["label"] == label) & (wins_df["version"] == "raw")]
                w595 = wins_df[(wins_df["factor"] == factor) & (wins_df["label"] == label) & (wins_df["version"] == "factor_w595")]
                if not raw.empty and not w595.empty:
                    ic_raw = clean(raw.iloc[0]["IC_mean"])
                    ic_w = clean(w595.iloc[0]["IC_mean"])
                    if ic_raw and ic_w and abs(ic_raw) > 0.001:
                        drop = abs(ic_raw - ic_w) / abs(ic_raw)
                        if drop > WINSORIZE_DROP_THRESHOLD:
                            flags.append("OUTLIER_SENSITIVE")

            # ── SYMBOL_CONCENTRATION ──
            if not sym_df.empty:
                ssym = sym_df[(sym_df["factor"] == factor) & (sym_df["label"] == label)]
                if not ssym.empty:
                    n_ts = m.get("n_timestamps", 1)
                    for _, r in ssym.iterrows():
                        n_q5 = clean(r.get("n_q5"))
                        n_q1 = clean(r.get("n_q1"))
                        if n_q5 and n_q5 / max(n_ts, 1) > CONCENTRATION_THRESHOLD:
                            flags.append("SYMBOL_CONCENTRATION")
                            break
                        if n_q1 and n_q1 / max(n_ts, 1) > CONCENTRATION_THRESHOLD:
                            flags.append("SYMBOL_CONCENTRATION")
                            break

            # ── LOW_COVERAGE ──
            if coverage is not None and coverage < COVERAGE_THRESHOLD:
                flags.append("LOW_COVERAGE")

            # ── severity ──
            n_flags = len(flags)
            if n_flags >= 4:
                severity = "HIGH"
            elif n_flags >= 2:
                severity = "MEDIUM"
            else:
                severity = "LOW"

            # ── recommendation ──
            if n_flags >= 4:
                rec = "PARK"
            elif n_flags >= 2:
                rec = "REVIEW_LATER"
            else:
                rec = "KEEP_AS_PROBE"

            rows.append({
                "factor_name": factor,
                "label": label,
                "ic_mean": ic_mean,
                "rankic_mean": rankic_mean,
                "spread_mean": spread_mean,
                "coverage": coverage,
                "warning_flags": "; ".join(flags) if flags else "NONE",
                "warning_count": n_flags,
                "severity": severity,
                "recommendation": rec,
            })

    result_df = pd.DataFrame(rows)
    result_df.to_csv(OUTDIR / "factor_warning_flags.csv", index=False)

    # ── summary markdown ──
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "# Factor Warning Flags Summary", "",
        f"- generated_at: {now}",
        f"- universe: {UNIVERSE}",
        "- purpose: lightweight risk-awareness mechanism for diagnostic probes",
        "- this is NOT a pass/fail gate", "",
    ]

    # overview table
    lines += ["## Overview", "",
              "| factor | label | flags | severity | recommendation |",
              "|---|---|---|---|---|"]
    for _, r in result_df.iterrows():
        ic_s = f"{r['ic_mean']:.4f}" if clean(r["ic_mean"]) is not None else ""
        lines.append(f"| {r['factor_name']} | {r['label']} | {r['warning_count']} | {r['severity']} | {r['recommendation']} |")

    # flag frequency
    lines += ["", "## Flag Frequency", ""]
    all_flags = []
    for _, r in result_df.iterrows():
        if r["warning_flags"] != "NONE":
            for f in r["warning_flags"].split("; "):
                all_flags.append(f)
    from collections import Counter
    freq = Counter(all_flags)
    lines.append("| flag | count |")
    lines.append("|---|---:|")
    for flag, cnt in freq.most_common():
        lines.append(f"| {flag} | {cnt} / {len(result_df)} |")

    # per-factor summary
    lines += ["", "## Per-Factor Summary", ""]
    for factor in FACTORS:
        sub = result_df[result_df["factor_name"] == factor]
        max_sev = "LOW"
        for s in sub["severity"]:
            if s == "HIGH":
                max_sev = "HIGH"
            elif s == "MEDIUM" and max_sev != "HIGH":
                max_sev = "MEDIUM"
        all_flags_set = set()
        for f in sub["warning_flags"]:
            if f != "NONE":
                all_flags_set.update(f.split("; "))
        lines.append(f"### {factor}")
        lines.append(f"- max severity: **{max_sev}**")
        lines.append(f"- active flags: {', '.join(sorted(all_flags_set)) if all_flags_set else 'NONE'}")
        lines.append(f"- recommendation across labels: {', '.join(sub['recommendation'].unique())}")
        lines.append("")

    # philosophy
    lines += ["## Philosophy", "",
              "This system flags risks. It does not eliminate factors.",
              "Diagnostic probes are expected to have warnings — that's why they're probes.",
              "The goal is awareness, not optimization.", "",
              "## Next Steps", "",
              "1. Use these flags as context when reviewing factor results",
              "2. Do NOT tune thresholds to make current factors pass",
              "3. Build new factors from the skeleton (FACTOR_LIBRARY_SKELETON.md)",
              "4. Let the warning system evolve as the library grows", ""]

    (OUTDIR / "factor_warning_summary.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"✓ Warning flags → {OUTDIR}/")
    for f in sorted(OUTDIR.iterdir()):
        print(f"  {f.name}")


if __name__ == "__main__":
    main()
