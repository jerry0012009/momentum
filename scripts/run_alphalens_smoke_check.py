#!/usr/bin/env python3
"""Phase 5C: Alphalens smoke check with sample-aligned universe.

Ensures Alphalens and local evaluation use identical samples:
  - same symbols (excluded symbols removed)
  - same timestamps
  - same non-null rows

Primary comparison: Alphalens Spearman IC vs direct local Spearman IC (same data).
Secondary: local summary RankIC for reference.

Usage:
    python scripts/run_alphalens_smoke_check.py \\
        --dataset-id crypto_top50_usdt_perp_1h_long_v1 \\
        --factor-id mom_20h wq101_alpha53 \\
        --horizons 1h 4h 24h 72h
"""
from __future__ import annotations

import argparse
import json
import warnings
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EXPORT_BASE = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "alphalens_exports"
LOCAL_RESULTS = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"

# Excluded symbols from local evaluation (missing_bar_rate > 5%)
EXCLUDED_SYMBOLS = [
    "AIOUSDT", "ALLOUSDT", "BEATUSDT", "EPICUSDT", "ESPORTSUSDT",
    "HMSTRUSDT", "HOMEUSDT", "HUSDT", "HYPEUSDT", "LABUSDT",
    "PAXGUSDT", "PLAYUSDT", "SIRENUSDT", "SKYAIUSDT", "SPACEUSDT",
    "TRUMPUSDT", "VELVETUSDT", "XPLUSDT",
]

# ── Alphalens availability ────────────────────────────────────────

ALPHALENS_AVAILABLE = False
ALPHALENS_ERROR = None

try:
    import alphalens
    from alphalens import performance as al_perf
    ALPHALENS_AVAILABLE = True
    print(f"alphalens {alphalens.__version__} loaded")
except ImportError as e:
    ALPHALENS_ERROR = str(e)
    print(f"alphalens not available: {e}")


# ── Data loading ──────────────────────────────────────────────────

def load_exported_data(dataset_id: str, factor_id: str):
    """Load Phase 5A exported parquet files."""
    export_dir = EXPORT_BASE / dataset_id / factor_id
    afd = pd.read_parquet(export_dir / "alphalens_factor_data.parquet")
    prices = pd.read_parquet(export_dir / "prices_wide.parquet")
    return afd, prices


def build_factor_data(afd: pd.DataFrame, horizons: list[str]) -> pd.DataFrame:
    """Build Alphalens-compatible factor_data DataFrame with MultiIndex (date, asset).

    Sets freq='h' on the date level so Alphalens's asfreq() doesn't collapse rows.
    """
    rename = {"factor": "factor"}
    for h in horizons:
        fwd_col = f"forward_return_{h}"
        if fwd_col in afd.columns:
            rename[fwd_col] = h
    afd = afd.rename(columns=rename)

    keep = ["timestamp", "symbol", "factor", "factor_quantile"] + [h for h in horizons if h in afd.columns]
    afd = afd[keep].copy()
    afd = afd.set_index(["timestamp", "symbol"])
    afd.index = afd.index.set_names(["date", "asset"])

    # Set freq='h' on the date level to prevent Alphalens's asfreq(None) from
    # collapsing hourly rows into daily rows.
    date_idx = afd.index.names.index("date")
    old_dates = afd.index.levels[date_idx]
    new_dates = pd.DatetimeIndex(old_dates, freq="h")
    afd.index = afd.index.set_levels(new_dates, level="date")

    return afd


def filter_to_evaluation_universe(factor_data: pd.DataFrame, excluded: list[str]) -> tuple[pd.DataFrame, dict]:
    """Filter factor_data to match local evaluation universe."""
    all_assets = factor_data.index.get_level_values("asset").unique()
    eval_assets = [a for a in all_assets if a not in excluded]

    pre_rows = len(factor_data)
    pre_symbols = len(all_assets)

    mask = factor_data.index.get_level_values("asset").isin(eval_assets)
    filtered = factor_data[mask].copy()
    filtered = filtered.dropna(subset=["factor"])

    post_rows = len(filtered)
    post_symbols = len(filtered.index.get_level_values("asset").unique())

    info = {
        "pre_filter_rows": pre_rows,
        "post_filter_rows": post_rows,
        "pre_filter_symbols": pre_symbols,
        "post_filter_symbols": post_symbols,
        "excluded_symbols": excluded,
        "excluded_count": len(excluded),
        "evaluation_symbols": sorted(eval_assets),
        "evaluation_symbols_count": len(eval_assets),
    }
    return filtered, info


# ── Direct Spearman computation (fast, vectorized) ────────────────

def compute_direct_spearman_ic(factor_data: pd.DataFrame, horizon: str) -> dict:
    """Compute Spearman IC using pivot + rank + corrwith (vectorized, fast).

    Groups by timestamp (hourly) — same granularity as Alphalens with freq='h' set.
    """
    if horizon not in factor_data.columns:
        return {"status": "error", "error": f"Column '{horizon}' not found"}

    df = factor_data[["factor", horizon]].dropna()
    if len(df) < 3:
        return {"status": "error", "error": "Too few rows"}

    # Pivot to matrix: rows=timestamps, cols=symbols
    pivot_f = df["factor"].unstack("asset")
    pivot_r = df[horizon].unstack("asset")

    # Rank per row (cross-sectional rank)
    rank_f = pivot_f.rank(axis=1)
    rank_r = pivot_r.rank(axis=1)

    # Pearson of ranks = Spearman, per timestamp
    ic = rank_f.corrwith(rank_r, axis=1).dropna()

    return {
        "status": "ok",
        "mean": float(ic.mean()),
        "std": float(ic.std()),
        "count": int(len(ic)),
    }


# ── Alphalens analysis ────────────────────────────────────────────

def run_alphalens_analysis(factor_data: pd.DataFrame, horizons: list[str]):
    """Run Alphalens IC on all horizons at once."""
    result = {"ic": {}, "mean_return_by_quantile": {}, "quantile_turnover": {}}

    fwd_cols = [h for h in horizons if h in factor_data.columns]
    if not fwd_cols:
        result["status"] = "error"
        result["error"] = "No forward return columns found"
        return result

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            ic = al_perf.factor_information_coefficient(factor_data)

        for col in fwd_cols:
            if col in ic.columns:
                result["ic"][col] = {
                    "mean": float(ic[col].mean()),
                    "std": float(ic[col].std()),
                    "count": int(ic[col].count()),
                }

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            mean_ret = al_perf.mean_return_by_quantile(factor_data)

        if isinstance(mean_ret, tuple):
            mean_ret_df = mean_ret[0]
        else:
            mean_ret_df = mean_ret

        for col in fwd_cols:
            if col in mean_ret_df.columns:
                result["mean_return_by_quantile"][col] = {
                    str(k): float(v) for k, v in mean_ret_df[col].items()
                }

        for col in fwd_cols:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    turnover = al_perf.quantile_turnover(factor_data, quantile=1, period=col)
                result["quantile_turnover"][col] = {
                    "mean": float(turnover.mean()),
                    "std": float(turnover.std()),
                }
            except Exception as e:
                result["quantile_turnover"][col] = {"error": str(e)}

        result["status"] = "ok"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    return result


# ── Local results comparison ──────────────────────────────────────

def load_local_results(dataset_id: str):
    """Load local evaluation summary for comparison."""
    summary_path = LOCAL_RESULTS / f"result_summary_{dataset_id}.md"
    if not summary_path.exists():
        return None

    text = summary_path.read_text()
    rows = []
    in_table = False
    for line in text.split("\n"):
        if line.startswith("| factor"):
            in_table = True
            continue
        if in_table and line.startswith("|---"):
            continue
        if in_table and line.startswith("|"):
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 4:
                rows.append({
                    "factor_id": parts[0],
                    "label": parts[1],
                    "direction": parts[2],
                    "IC_mean": float(parts[3]) if parts[3] else 0.0,
                    "RankIC_mean": float(parts[5]) if len(parts) > 5 and parts[5] else 0.0,
                })
        elif in_table and not line.startswith("|"):
            break
    return pd.DataFrame(rows) if rows else None


def build_comparison_row(
    factor_id: str,
    horizon: str,
    alphalens_ic: float,
    direct_ic: float,
    local_df,
) -> dict:
    """Build IC comparison row.

    Primary: Alphalens Spearman vs direct hourly Spearman (same data, same grouping).
    Secondary: local summary RankIC for reference.
    """
    label = f"ret_fwd_{horizon}"
    local_row = local_df[
        (local_df["factor_id"] == factor_id) & (local_df["label"] == label)
    ] if local_df is not None else pd.DataFrame()

    local_pearson = float(local_row.iloc[0]["IC_mean"]) if not local_row.empty else None
    local_rankic = float(local_row.iloc[0]["RankIC_mean"]) if not local_row.empty else None

    # Primary: Alphalens vs direct hourly Spearman (same data, same freq)
    primary_diff = abs(alphalens_ic - direct_ic)

    if primary_diff <= 1e-6:
        status = "match"
    elif primary_diff <= 1e-4:
        status = "near_match"
    else:
        status = "mismatch"

    note = ""
    if status == "mismatch":
        note = (
            f"primary_diff={primary_diff:.6f}: "
            "Alphalens and direct Spearman use same aligned data with hourly freq. "
            "Difference likely due to NaN handling within cross-sections."
        )

    return {
        "factor_id": factor_id,
        "horizon": horizon,
        "local_summary_RankIC": round(local_rankic, 6) if local_rankic is not None else None,
        "direct_SpearmanIC": round(direct_ic, 6),
        "alphalens_SpearmanIC": round(alphalens_ic, 6),
        "primary_abs_diff": round(primary_diff, 6),
        "status": status,
        "note": note,
    }


# ── Main ──────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dataset-id", default="crypto_top50_usdt_perp_1h_long_v1")
    p.add_argument("--factor-id", nargs="+", default=["mom_20h", "wq101_alpha53"])
    p.add_argument("--horizons", nargs="+", default=["1h", "4h", "24h", "72h"])
    p.add_argument("--output", default=None, help="Output report path")
    args = p.parse_args()

    dataset_id = args.dataset_id
    factor_ids = args.factor_id
    horizons = args.horizons

    local_df = load_local_results(dataset_id)

    results = {
        "dataset_id": dataset_id,
        "alphalens_available": ALPHALENS_AVAILABLE,
        "alphalens_version": alphalens.__version__ if ALPHALENS_AVAILABLE else None,
        "alphalens_error": ALPHALENS_ERROR,
        "horizons": horizons,
        "factors": {},
        "comparison": [],
        "alignment": {},
        "limitations": [],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    if not ALPHALENS_AVAILABLE:
        results["limitations"].append(
            "Alphalens package unavailable; export-layer complete but actual smoke check blocked by dependency."
        )
        print("Alphalens unavailable — skipping smoke check")
    else:
        for fid in factor_ids:
            print(f"\n{'='*60}")
            print(f"Factor: {fid}")
            print(f"{'='*60}")

            afd, prices = load_exported_data(dataset_id, fid)
            factor_data = build_factor_data(afd, horizons)

            # ── Sample alignment ────────────────────────────────
            aligned_data, align_info = filter_to_evaluation_universe(factor_data, EXCLUDED_SYMBOLS)
            results["alignment"][fid] = align_info

            print(f"  Pre-filter:  {align_info['pre_filter_rows']:,} rows, {align_info['pre_filter_symbols']} symbols")
            print(f"  Post-filter: {align_info['post_filter_rows']:,} rows, {align_info['post_filter_symbols']} symbols")
            print(f"  Excluded:    {align_info['excluded_count']} symbols")

            # ── Direct Spearman (fast) ──────────────────────────
            direct = {}
            for h in horizons:
                direct[h] = compute_direct_spearman_ic(aligned_data, h)
                d_ic = direct[h]
                if d_ic["status"] == "ok":
                    print(f"  {h}: direct_Spearman={d_ic['mean']:.6f}")

            # ── Alphalens analysis on aligned data ──────────────
            print(f"  Running Alphalens (all {len(horizons)} horizons)...")
            analysis = run_alphalens_analysis(aligned_data, horizons)
            results["factors"][fid] = analysis

            if analysis["status"] == "ok":
                print(f"  Alphalens IC computed successfully")

                # ── Build comparison rows ───────────────────────
                for h in horizons:
                    alphalens_ic = analysis["ic"].get(h, {}).get("mean")
                    d_ic = direct.get(h, {}).get("mean")

                    if alphalens_ic is not None and d_ic is not None:
                        comp = build_comparison_row(fid, h, alphalens_ic, d_ic, local_df)
                        results["comparison"].append(comp)
                        print(f"  {h}: alphalens={alphalens_ic:.6f}  direct={d_ic:.6f}  diff={comp['primary_abs_diff']:.6f}  {comp['status']}")
                    else:
                        print(f"  {h}: SKIP — alphalens={'ok' if alphalens_ic else 'N/A'}, direct={'ok' if d_ic else 'N/A'}")
            else:
                print(f"  ERROR: {analysis.get('error')}")
                results["limitations"].append(f"{fid}: {analysis.get('error')}")

    # ── Limitations ─────────────────────────────────────────────
    results["limitations"].extend([
        "Alphalens IC = Spearman rank correlation; direct Spearman computed from same aligned data.",
        "freq='h' set on MultiIndex to prevent Alphalens asfreq(None) from collapsing hourly → daily.",
        "Local summary RankIC shown for reference only (different NaN handling, different sample period).",
        "get_clean_factor_and_forward_returns() skipped — hourly frequency not supported.",
        "No factor status upgrade can be based solely on Alphalens output.",
    ])

    # ── Overall status ──────────────────────────────────────────
    all_statuses = [c["status"] for c in results["comparison"]]
    if not all_statuses:
        overall = "BLOCKED"
    elif all(s in ("match", "near_match") for s in all_statuses):
        overall = "PASS"
    else:
        overall = "FAIL"

    results["overall_status"] = overall

    # ── Write reports ───────────────────────────────────────────
    output_path = Path(args.output) if args.output else (
        LOCAL_RESULTS / "PHASE_5B_ALPHALENS_SMOKE_CHECK.json"
    )
    output_path.write_text(json.dumps(results, indent=2, ensure_ascii=False, default=str) + "\n")
    print(f"\nJSON report: {output_path}")

    md_path = output_path.with_suffix(".md")
    write_markdown_report(results, md_path)
    print(f"MD report: {md_path}")

    # ── Final verdict ───────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"OVERALL: {overall}")
    match_count = sum(1 for s in all_statuses if s == "match")
    near_count = sum(1 for s in all_statuses if s == "near_match")
    mismatch_count = sum(1 for s in all_statuses if s == "mismatch")
    print(f"  match={match_count}  near_match={near_count}  mismatch={mismatch_count}")
    if overall == "PASS":
        print("  Phase 5 COMPLETE — Phase 6 READY for human approval")
    else:
        print("  Phase 5 BLOCKED — Phase 6 NOT ALLOWED")


# ── Markdown report ───────────────────────────────────────────────

def write_markdown_report(results: dict, path: Path):
    """Write human-readable markdown report."""
    overall = results.get("overall_status", "UNKNOWN")

    lines = [
        "# Phase 5C — Alphalens Smoke Check Report (Sample-Aligned)",
        "",
        f"> Generated: {results['generated_at']}",
        f"> Dataset: {results['dataset_id']}",
        f"> Alphalens: {'v' + results['alphalens_version'] if results['alphalens_available'] else 'UNAVAILABLE'}",
        "",
        "---",
        "",
        "## 1. Dependency Status",
        "",
        f"- alphalens-reloaded: **{results['alphalens_available']}** (v{results.get('alphalens_version', 'N/A')})",
        "",
        "## 2. Sample Alignment",
        "",
    ]

    for fid, align in results.get("alignment", {}).items():
        lines.append(f"### {fid}")
        lines.append("")
        lines.append(f"| Metric | Value |")
        lines.append(f"|--------|-------|")
        lines.append(f"| Pre-filter rows | {align['pre_filter_rows']:,} |")
        lines.append(f"| Post-filter rows | {align['post_filter_rows']:,} |")
        lines.append(f"| Pre-filter symbols | {align['pre_filter_symbols']} |")
        lines.append(f"| Post-filter symbols (evaluation universe) | {align['post_filter_symbols']} |")
        lines.append(f"| Excluded symbols | {align['excluded_count']} |")
        lines.append(f"| Excluded list | {', '.join(align['excluded_symbols'])} |")
        lines.append("")

    lines.extend([
        "## 3. IC Comparison (Sample-Aligned, Hourly Freq)",
        "",
        "**Primary:** Alphalens Spearman IC vs Direct Hourly Spearman IC (same data, same hourly freq).",
        "",
        "| Factor | Horizon | Local Summary RankIC | Direct Spearman IC | Alphalens Spearman IC | Primary Abs Diff | Status |",
        "|--------|---------|---------------------|-------------------|----------------------|-----------------|--------|",
    ])

    for row in results["comparison"]:
        summary_rankic = f"{row['local_summary_RankIC']:.6f}" if row['local_summary_RankIC'] is not None else "N/A"
        direct = f"{row['direct_SpearmanIC']:.6f}"
        alphalens = f"{row['alphalens_SpearmanIC']:.6f}"
        diff = f"{row['primary_abs_diff']:.6f}"
        lines.append(
            f"| {row['factor_id']} | {row['horizon']} | {summary_rankic} | {direct} | {alphalens} | {diff} | {row['status']} |"
        )

    all_statuses = [c["status"] for c in results["comparison"]]
    match_count = sum(1 for s in all_statuses if s == "match")
    near_count = sum(1 for s in all_statuses if s == "near_match")
    mismatch_count = sum(1 for s in all_statuses if s == "mismatch")

    lines.extend([
        "",
        f"**Summary:** match={match_count}, near_match={near_count}, mismatch={mismatch_count}",
    ])

    lines.extend([
        "## 4. Comparison Methodology",
        "",
        "- **Primary comparison:** Alphalens Spearman IC vs Direct Hourly Spearman IC.",
        "  Both use the same sample-aligned factor_data with hourly freq (freq='h' set on MultiIndex).",
        "  Without freq='h', Alphalens's asfreq(None) collapses hourly rows into daily, causing false mismatches.",
        "- **Local Summary RankIC:** From `result_summary_*.md` (different NaN handling, different sample period).",
        "- Sample alignment: excluded 18 symbols with missing_bar_rate > 5%, matching local evaluation universe.",
        "",
        "## 5. Limitations",
        "",
    ])
    for lim in results["limitations"]:
        lines.append(f"- {lim}")

    lines.extend([
        "",
        "## 6. Conclusion",
        "",
        f"- **Overall status: {overall}**",
        f"- Factors tested: {len(results['factors'])}",
        f"- Comparison rows: {len(results['comparison'])}",
        "",
    ])

    if overall == "PASS":
        lines.extend([
            "All primary comparisons are match or near_match.",
            "- Phase 5 (Alphalens export + smoke check): **COMPLETE**",
            "- Phase 6 (Dynamic Universe): **READY — requires human approval**",
        ])
    else:
        lines.extend([
            "Some primary comparisons are mismatch.",
            "- Phase 5 (Alphalens export + smoke check): **BLOCKED**",
            "- Phase 6 (Dynamic Universe): **NOT ALLOWED**",
            "- Investigate mismatch causes before proceeding.",
        ])

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
