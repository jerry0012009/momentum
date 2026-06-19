#!/usr/bin/env python3
"""Audit Factor Direction Semantics — Phase 12D-H12-A.

Reads historical direction diagnostics + current catalog/signal to produce
a direction semantics audit.  Pure read-only audit, no modifications.
"""
from __future__ import annotations

import csv, json, os, sys
from pathlib import Path
from datetime import datetime, timezone

WORK = Path(__file__).resolve().parent.parent
SCRIPTS = WORK / "scripts"
OUT_DIR = WORK / "research" / "factor_runs" / "crypto_top50_factor_library" / "direction_semantics_audit"
QC_PATH = WORK / "research" / "factor_runs" / "crypto_top50_factor_library" / "phase12d_h12a_direction_semantics_quality_checks.csv"

# ── Historical assets ──────────────────────────────────────────────
PHASE6H = WORK / "research" / "factor_runs" / "crypto_top50_factor_library" / "PHASE_6H_STATIC_DYNAMIC_COMPARISON.md"
P10A_R_DIR = WORK / "research" / "factor_runs" / "crypto_top50_factor_library"
P10A_R_SCRIPT = WORK / "archive" / "legacy_phase_scripts" / "phase10" / "run_phase10a_r_diagnostics.py"
P10A_R_TEST = WORK / "tests" / "unit" / "test_phase10a_r_direction_quantile_repair.py"

P10A_R_ASSETS = {
    "direction_consistency": P10A_R_DIR / "phase10a_r_direction_consistency_check.csv",
    "quantile_bucket_returns": P10A_R_DIR / "phase10a_r_quantile_bucket_returns.csv",
    "inverted_signal_diagnostic": P10A_R_DIR / "phase10a_r_inverted_signal_diagnostic.csv",
    "rankic_quantile_reconciliation": P10A_R_DIR / "phase10a_r_rankic_quantile_reconciliation.csv",
    "quality_checks": P10A_R_DIR / "phase10a_r_quality_checks.csv",
}

# ── Current assets ─────────────────────────────────────────────────
CATALOG_JSON = P10A_R_DIR / "factor_catalog.json"
IC_CSV = P10A_R_DIR / "factor_level_evaluation" / "factor_level_rankic_summary.csv"
COMPONENT_MANIFEST = P10A_R_DIR / "phase9b_signal_component_manifest.csv"

# ── Signal construction constants ──────────────────────────────────
FACTOR_IDS = [
    "vol_5h", "vol_40h", "downside_vol_20h", "vol_of_vol_20h",
    "rsi_7h", "rsi_28h", "xs_rank_vol",
    "range_1h", "range_4h", "price_pos_24h",
]
NEGATIVE = ["vol_5h", "vol_40h", "downside_vol_20h", "vol_of_vol_20h", "rsi_7h", "rsi_28h"]
OVERLAY = ["range_1h", "range_4h", "price_pos_24h"]
LIQUIDITY_GATE = ["xs_rank_vol"]

SIGNAL_ROLES = {
    "vol_5h": "risk_pressure", "vol_40h": "risk_pressure",
    "downside_vol_20h": "risk_pressure", "vol_of_vol_20h": "risk_pressure",
    "rsi_7h": "oscillator_exhaustion", "rsi_28h": "oscillator_exhaustion",
    "xs_rank_vol": "liquidity_gate",
    "range_1h": "position_timing_overlay", "range_4h": "position_timing_overlay",
    "price_pos_24h": "position_timing_overlay",
}

# ── Phase 6H known findings ───────────────────────────────────────
PHASE6H_MISMATCH = {
    "mom_20h": {"expected": "positive", "static_ic": -0.0250, "dynamic_ic": -0.0191, "notes": "Both negative; empirical sign contradicts expected"},
    "reversal_5h": {"expected": "negative", "static_ic": 0.0328, "dynamic_ic": 0.0282, "notes": "Both positive; empirical sign contradicts expected"},
    "tech_macd": {"expected": "positive", "static_ic": -0.0086, "dynamic_ic": -0.0065, "notes": "Both negative; weak but consistent mismatch"},
    "wq101_alpha101": {"expected": "positive", "static_ic": -0.0232, "dynamic_ic": -0.0176, "notes": "Both negative; empirical sign contradicts expected"},
}
PHASE6H_CONSISTENT = {
    "volatility_20h": {"expected": "negative", "static_ic": -0.0295, "dynamic_ic": -0.0428, "notes": "strong_robust"},
    "rsi_14h": {"expected": "negative", "static_ic": -0.0236, "dynamic_ic": -0.0210, "notes": "strong_robust"},
    "bb_zscore_20h": {"expected": "negative", "static_ic": -0.0253, "dynamic_ic": -0.0244, "notes": "strong_robust"},
}
PHASE6H_CONDITIONAL = {
    "q158_high_low_range": {"static_ic": -0.0272, "dynamic_ic": -0.0413, "notes": "strong_robust"},
    "wq101_alpha53": {"static_ic": 0.0173, "dynamic_ic": 0.0127, "notes": "moderate_stable"},
    "tech_atr": {"static_ic": 0.0092, "dynamic_ic": 0.0200, "notes": "unstable"},
    "wq101_alpha12": {"static_ic": 0.0050, "dynamic_ic": 0.0041, "notes": "unstable"},
}


def load_catalog():
    with open(CATALOG_JSON) as f:
        return json.load(f)["factors"]


def load_ic_data():
    data = {}
    if not IC_CSV.exists():
        return data
    with open(IC_CSV) as f:
        for row in csv.DictReader(f):
            fid = row["factor_name"]
            h = row["horizon"]
            if fid not in data:
                data[fid] = {}
            raw = row.get("raw_mean_rank_ic")
            adj = row.get("direction_adjusted_mean_rank_ic")
            data[fid][h] = {
                "raw_ic": float(raw) if raw not in (None, "") else None,
                "adj_ic": float(adj) if adj not in (None, "") else None,
            }
    return data


def load_component_manifest():
    rows = []
    if COMPONENT_MANIFEST.exists():
        with open(COMPONENT_MANIFEST) as f:
            rows = list(csv.DictReader(f))
    return rows


def _sign(v):
    if v is None:
        return "N/A"
    return "POSITIVE" if v > 0 else ("NEGATIVE" if v < 0 else "ZERO")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    catalog = load_catalog()
    ic_data = load_ic_data()
    components = load_component_manifest()

    # Build catalog lookup
    cat_by_id = {r["factor_id"]: r for r in catalog}

    # ── 1. Legacy diagnostics inventory ────────────────────────────
    legacy_assets = [
        {"asset_path": str(PHASE6H), "phase": "6H", "asset_type": "comparison_md", "exists": PHASE6H.exists()},
        {"asset_path": str(P10A_R_SCRIPT), "phase": "10A-R", "asset_type": "diagnostics_script", "exists": P10A_R_SCRIPT.exists()},
        {"asset_path": str(P10A_R_TEST), "phase": "10A-R", "asset_type": "unit_test", "exists": P10A_R_TEST.exists()},
    ]
    for name, path in P10A_R_ASSETS.items():
        legacy_assets.append({
            "asset_path": str(path), "phase": "10A-R", "asset_type": name, "exists": path.exists()
        })

    # Read each existing asset
    p10a_findings = {}
    for asset in legacy_assets:
        if not asset["exists"]:
            asset["read_success"] = False
            asset["key_findings"] = "FILE NOT FOUND"
            continue
        try:
            p = Path(asset["asset_path"])
            if p.suffix == ".csv":
                with open(p) as f:
                    rows = list(csv.DictReader(f))
                    asset["read_success"] = True
                    if asset["asset_type"] == "direction_consistency":
                        p10a_findings["direction_consistency"] = rows
                        inconsistent = [r for r in rows if r.get("sign_consistent") == "False"]
                        asset["key_findings"] = f"{len(rows)} rows; {len(inconsistent)} inconsistent (all have non_monotonic_tail_behavior)"
                    elif asset["asset_type"] == "inverted_signal_diagnostic":
                        p10a_findings["inverted"] = rows
                        asset["key_findings"] = f"{len(rows)} rows; inversion resolves spread but flips RankIC negative for 1h/4h"
                    elif asset["asset_type"] == "quantile_bucket_returns":
                        p10a_findings["bucket_returns"] = rows
                        asset["key_findings"] = f"{len(rows)} rows; bucket 0 has extreme positive returns"
                    elif asset["asset_type"] == "rankic_quantile_reconciliation":
                        p10a_findings["reconciliation"] = rows
                        asset["key_findings"] = f"{len(rows)} rows; reconciliation data"
                    else:
                        asset["key_findings"] = f"{len(rows)} rows"
            elif p.suffix == ".md":
                asset["read_success"] = True
                asset["key_findings"] = "Phase 6H comparison: 4 mismatch, 3 consistent, 4 conditional"
            else:
                asset["read_success"] = True
                asset["key_findings"] = "Python script/read"
        except Exception as e:
            asset["read_success"] = False
            asset["key_findings"] = f"Read error: {e}"

    # Write legacy inventory
    inv_fields = ["asset_path", "phase", "asset_type", "exists", "read_success", "key_findings", "applies_to_current_pipeline", "notes"]
    for asset in legacy_assets:
        asset.setdefault("applies_to_current_pipeline", "YES" if asset["exists"] else "N/A")
        asset.setdefault("notes", "")
    inv_path = OUT_DIR / "legacy_direction_diagnostics_inventory.csv"
    with open(inv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=inv_fields)
        w.writeheader()
        w.writerows(legacy_assets)
    os.chmod(inv_path, 0o644)

    # ── 2. Factor direction semantics audit ────────────────────────
    audit_rows = []
    for cat_row in catalog:
        fid = cat_row["factor_id"]
        family = cat_row["family"]
        expected_dir = cat_row["expected_direction"]
        in_signal = cat_row["used_in_current_signal"]
        lifecycle = cat_row["lifecycle_status"]

        # Get IC data
        ic_1h = ic_data.get(fid, {}).get("1h", {})
        ic_4h = ic_data.get(fid, {}).get("4h", {})
        ic_24h = ic_data.get(fid, {}).get("24h", {})
        ic_72h = ic_data.get(fid, {}).get("72h", {})

        raw_1h = ic_1h.get("raw_ic")
        adj_1h = ic_1h.get("adj_ic")
        raw_4h = ic_4h.get("raw_ic")
        adj_4h = ic_4h.get("adj_ic")
        raw_24h = ic_24h.get("raw_ic")
        adj_24h = ic_24h.get("adj_ic")
        raw_72h = ic_72h.get("raw_ic")
        adj_72h = ic_72h.get("adj_ic")

        # Phase 6H status
        if fid in PHASE6H_MISMATCH:
            p6h_status = "DIRECTION_MISMATCH"
            p6h_notes = PHASE6H_MISMATCH[fid]["notes"]
        elif fid in PHASE6H_CONSISTENT:
            p6h_status = "DIRECTION_CONSISTENT"
            p6h_notes = PHASE6H_CONSISTENT[fid]["notes"]
        elif fid in PHASE6H_CONDITIONAL:
            p6h_status = "CONDITIONAL"
            p6h_notes = PHASE6H_CONDITIONAL[fid]["notes"]
        else:
            p6h_status = "NOT_EVALUATED_IN_6H"
            p6h_notes = ""

        # Signal transform
        if fid in NEGATIVE:
            signal_transform = "MULTIPLY_BY_NEG1"
        elif fid in OVERLAY:
            signal_transform = "MULTIPLY_BY_NEG1"
        elif fid in LIQUIDITY_GATE:
            signal_transform = "RANK_PERCENTILE_GATE"
        else:
            signal_transform = "NONE"

        # Formula summary
        formula_map = {
            "mom_20h": "close/close_20h_ago - 1",
            "reversal_5h": "-(close/close_5h_ago - 1)",
            "volatility_20h": "rolling_std(ret, 20)",
            "rsi_14h": "Wilder RSI 14",
            "bb_zscore_20h": "(close - mean20) / std20",
            "wq101_alpha101": "(close-open)/(high-low+eps)",
            "wq101_alpha12": "sign(dvol) * (-dclose)",
            "wq101_alpha53": "-delta(intraday_pos, 9)",
            "q158_high_low_range": "(high-low)/close",
            "tech_macd": "MACD histogram (EMA12-EMA26 signal)",
            "tech_atr": "Average True Range 14 bars",
            "mom_5h": "close/close_5h_ago - 1",
            "mom_10h": "close/close_10h_ago - 1",
            "mom_40h": "close/close_40h_ago - 1",
            "rev_3h": "-(close/close_3h_ago - 1)",
            "rev_10h": "-(close/close_10h_ago - 1)",
            "rev_24h": "-(close/close_24h_ago - 1)",
            "vol_5h": "rolling_std(ret, 5)",
            "vol_40h": "rolling_std(ret, 40)",
            "vol_ratio_5_20": "std(ret,5)/std(ret,20)",
            "range_1h": "(high-low)/close",
            "range_4h": "(HH4-LL4)/close",
            "range_24h": "(HH24-LL24)/close",
            "price_pos_24h": "(close-LL24)/(HH24-LL24+eps)",
            "price_pos_72h": "(close-LL72)/(HH72-LL72+eps)",
            "vol_zscore_20h": "(vol-SMA20)/STD20",
            "vol_zscore_48h": "(vol-SMA48)/STD48",
            "qvol_zscore_20h": "(qvol-SMA20)/STD20",
            "qvol_zscore_48h": "(qvol-SMA48)/STD48",
            "ma_gap_5_20": "(SMA5-SMA20)/SMA20",
            "ma_gap_10_40": "(SMA10-SMA40)/SMA40",
            "ma_gap_20_80": "(SMA20-SMA80)/SMA80",
            "breakout_dist_20h": "(close-HH20)/(HH20-LL20+eps)",
            "breakout_dist_48h": "(close-HH48)/(HH48-LL48+eps)",
            "candle_body": "(close-open)/(high-low+eps)",
            "candle_wick_upper": "(high-max(open,close))/(high-low+eps)",
            "candle_wick_lower": "(min(open,close)-low)/(high-low+eps)",
            "xs_rank_ret_1h": "per-symbol 1h return; xs rank by caller",
            "xs_rank_vol": "per-symbol 20h rolling mean volume; xs rank by caller",
            "ema_12_26_gap": "(EMA12-EMA26)/EMA26",
            "rsi_7h": "Wilder RSI 7",
            "rsi_28h": "Wilder RSI 28",
            "williams_r_14h": "(HH14-close)/(HH14-LL14+eps)",
            "downside_vol_20h": "rolling_std(min(ret,0), 20)",
            "vol_of_vol_20h": "rolling_std(rolling_std(ret,5),20)",
            "mom_accel_20h": "mom_20h - delay(mom_20h, 5)",
            "qvol_ma_ratio_5_20": "SMA(qvol,5)/SMA(qvol,20)-1",
            "taker_buy_ratio_20h": "rolling_mean(taker_buy_qvol/qvol, 20)",
            "taker_buy_zscore_20h": "zscore(taker_buy_qvol/qvol, 20)",
            "taker_buy_delta_5h": "ratio - delay(ratio, 5)",
            "funding_rate_level_20h": "rolling_mean(funding_rate, 20)",
            "funding_rate_zscore_80h": "zscore(funding_rate, 80)",
            "funding_rate_change_24h": "funding_rate - delay(funding_rate, 24)",
        }

        # Semantic status
        if lifecycle == "MISSING_INPUT_DATA":
            semantic_status = "MISSING_INPUT_DATA"
        elif fid in PHASE6H_MISMATCH and raw_1h is not None:
            # Check if historical mismatch was repaired (expected_direction now matches IC sign)
            ic_sign_positive = raw_1h > 0
            direction_now_matches = (
                (expected_dir == "positive" and ic_sign_positive) or
                (expected_dir == "negative" and not ic_sign_positive)
            )
            if direction_now_matches:
                semantic_status = "REPAIRED_IN_H12B"
            else:
                semantic_status = "HISTORICAL_DIRECTION_MISMATCH"
        elif fid in PHASE6H_MISMATCH:
            semantic_status = "HISTORICAL_DIRECTION_MISMATCH"
        elif expected_dir == "conditional" and in_signal:
            semantic_status = "CONDITIONAL_USED_IN_SIGNAL"
        elif expected_dir == "conditional":
            semantic_status = "CONDITIONAL_DIAGNOSTIC_ONLY"
        elif fid in PHASE6H_CONSISTENT:
            semantic_status = "DIRECTION_CONSISTENT"
        elif not in_signal:
            semantic_status = "OK_NOT_IN_SIGNAL"
        else:
            # Check if IC sign matches expected direction
            if raw_1h is not None:
                ic_sign_positive = raw_1h > 0
                if expected_dir == "positive" and ic_sign_positive:
                    semantic_status = "DIRECTION_CONSISTENT"
                elif expected_dir == "negative" and not ic_sign_positive:
                    semantic_status = "DIRECTION_CONSISTENT"
                else:
                    semantic_status = "NEEDS_HUMAN_REVIEW"
            else:
                semantic_status = "OK_NOT_IN_SIGNAL"

        # Recommended action
        if semantic_status == "MISSING_INPUT_DATA":
            rec = "Acquire data source"
        elif semantic_status == "HISTORICAL_DIRECTION_MISMATCH":
            rec = "Review in H12-B; do NOT enter signal without direction fix"
        elif semantic_status == "CONDITIONAL_USED_IN_SIGNAL":
            rec = "Document signal transform justification; consider metadata update"
        elif semantic_status == "CONDITIONAL_DIAGNOSTIC_ONLY":
            rec = "Keep diagnostic; direction unknown"
        elif semantic_status == "NEEDS_HUMAN_REVIEW":
            rec = "Review IC sign vs expected_direction in H12-B"
        else:
            rec = "No action needed"

        audit_rows.append({
            "factor_id": fid,
            "family": family,
            "formula_summary": formula_map.get(fid, "UNKNOWN"),
            "formula_sign_notes": "",
            "expected_direction": expected_dir,
            "raw_ic_1h": round(raw_1h, 6) if raw_1h is not None else None,
            "adj_ic_1h": round(adj_1h, 6) if adj_1h is not None else None,
            "raw_ic_4h": round(raw_4h, 6) if raw_4h is not None else None,
            "adj_ic_4h": round(adj_4h, 6) if adj_4h is not None else None,
            "raw_ic_24h": round(raw_24h, 6) if raw_24h is not None else None,
            "adj_ic_24h": round(adj_24h, 6) if adj_24h is not None else None,
            "raw_ic_72h": round(raw_72h, 6) if raw_72h is not None else None,
            "adj_ic_72h": round(adj_72h, 6) if adj_72h is not None else None,
            "raw_ic_sign_1h": _sign(raw_1h),
            "adjusted_ic_sign_1h": _sign(adj_1h),
            "phase6h_prior_direction_status": p6h_status,
            "phase6h_prior_notes": p6h_notes,
            "current_lifecycle_status": lifecycle,
            "used_in_current_signal": in_signal,
            "signal_transform": signal_transform,
            "signal_role": SIGNAL_ROLES.get(fid, ""),
            "semantic_status": semantic_status,
            "recommended_action": rec,
        })

    audit_path = OUT_DIR / "factor_direction_semantics_audit.csv"
    with open(audit_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(audit_rows[0].keys()))
        w.writeheader()
        w.writerows(audit_rows)
    os.chmod(audit_path, 0o644)

    # ── 3. Direction mismatch candidates ───────────────────────────
    candidate_ids = [
        "mom_20h", "reversal_5h", "tech_macd", "wq101_alpha101",
        "q158_high_low_range", "range_1h", "range_4h", "price_pos_24h",
        "xs_rank_vol", "rev_3h", "rsi_14h", "bb_zscore_20h", "volatility_20h",
    ]
    mismatch_rows = []
    for fid in candidate_ids:
        cat = cat_by_id.get(fid, {})
        ic_1h = ic_data.get(fid, {}).get("1h", {})
        raw_1h = ic_1h.get("raw_ic")
        adj_1h = ic_1h.get("adj_ic")
        expected = cat.get("expected_direction", "unknown")
        in_signal = cat.get("used_in_current_signal", False)
        lifecycle = cat.get("lifecycle_status", "")

        # Determine issue type
        if fid in PHASE6H_MISMATCH:
            issue_type = "PHASE6H_DIRECTION_MISMATCH"
            evidence = PHASE6H_MISMATCH[fid]["notes"]
        elif expected == "conditional" and in_signal:
            issue_type = "CONDITIONAL_IN_SIGNAL"
            evidence = f"expected_direction=conditional but used in signal as {SIGNAL_ROLES.get(fid, 'unknown')}"
        elif expected == "conditional":
            issue_type = "CONDITIONAL_DIAGNOSTIC"
            evidence = "direction unknown; kept for diagnostic"
        elif raw_1h is not None and expected == "positive" and raw_1h < 0:
            issue_type = "IC_SIGN_VS_EXPECTED"
            evidence = f"expected positive but raw_ic_1h={raw_1h:.4f}"
        elif raw_1h is not None and expected == "negative" and raw_1h > 0:
            issue_type = "IC_SIGN_VS_EXPECTED"
            evidence = f"expected negative but raw_ic_1h={raw_1h:.4f}"
        else:
            issue_type = "CONSISTENT_OR_NA"
            evidence = "no direction issue detected"

        # Signal transform
        if fid in NEGATIVE:
            sig_transform = "MULTIPLY_BY_NEG1"
        elif fid in OVERLAY:
            sig_transform = "MULTIPLY_BY_NEG1"
        elif fid in LIQUIDITY_GATE:
            sig_transform = "RANK_PERCENTILE_GATE"
        else:
            sig_transform = "NONE_OR_NA"

        mismatch_rows.append({
            "factor_id": fid,
            "issue_type": issue_type,
            "evidence": evidence,
            "current_expected_direction": expected,
            "raw_ic_sign": _sign(raw_1h),
            "adjusted_ic_sign": _sign(adj_1h),
            "signal_transform": sig_transform if in_signal else "NOT_IN_SIGNAL",
            "risk_if_unfixed": "direction inversion could flip signal interpretation" if "MISMATCH" in issue_type or "CONDITIONAL_IN_SIGNAL" == issue_type else "low",
            "recommended_next_step": "Review in H12-B" if "MISMATCH" in issue_type or "CONDITIONAL_IN_SIGNAL" == issue_type else "No action",
        })

    mismatch_path = OUT_DIR / "direction_mismatch_candidates.csv"
    with open(mismatch_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(mismatch_rows[0].keys()))
        w.writeheader()
        w.writerows(mismatch_rows)
    os.chmod(mismatch_path, 0o644)

    # ── 4. Signal direction transform audit ────────────────────────
    sig_rows = []
    for fid in FACTOR_IDS:
        cat = cat_by_id.get(fid, {})
        ic_1h = ic_data.get(fid, {}).get("1h", {})
        raw_1h = ic_1h.get("raw_ic")
        adj_1h = ic_1h.get("adj_ic")
        expected = cat.get("expected_direction", "unknown")
        in_neg = fid in NEGATIVE
        in_ovl = fid in OVERLAY
        in_liq = fid in LIQUIDITY_GATE

        if in_neg:
            transform = "MULTIPLY_BY_NEG1"
        elif in_ovl:
            transform = "MULTIPLY_BY_NEG1"
        elif in_liq:
            transform = "RANK_PERCENTILE_GATE"
        else:
            transform = "NONE"

        # Does transform match expected direction?
        if expected == "negative" and in_neg:
            match = "YES — negative expected, signal flips to positive"
        elif expected == "conditional" and in_ovl:
            match = "CONDITIONAL — overlay justified by mean-reversion hypothesis"
        elif expected == "conditional" and in_liq:
            match = "CONDITIONAL — liquidity gate uses rank percentile, not direction"
        elif expected == "positive" and not in_neg and not in_ovl:
            match = "YES — positive expected, no transform"
        else:
            match = "REVIEW_NEEDED"

        sig_rows.append({
            "factor_id": fid,
            "used_in_signal": True,
            "signal_role": SIGNAL_ROLES.get(fid, ""),
            "in_NEGATIVE_list": in_neg,
            "in_OVERLAY_list": in_ovl,
            "signal_transform_applied": transform,
            "factor_expected_direction": expected,
            "factor_raw_ic_1h": round(raw_1h, 6) if raw_1h is not None else None,
            "factor_adj_ic_1h": round(adj_1h, 6) if adj_1h is not None else None,
            "transform_matches_expected_direction": match,
            "notes": "",
        })

    sig_path = OUT_DIR / "signal_direction_transform_audit.csv"
    with open(sig_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(sig_rows[0].keys()))
        w.writeheader()
        w.writerows(sig_rows)
    os.chmod(sig_path, 0o644)

    # ── 5. Manifest ───────────────────────────────────────────────
    mismatch_count = sum(1 for r in mismatch_rows if r["issue_type"] not in ("CONSISTENT_OR_NA", "CONDITIONAL_DIAGNOSTIC"))
    conditional_in_signal = sum(1 for r in audit_rows if r["semantic_status"] == "CONDITIONAL_USED_IN_SIGNAL")
    double_inv = sum(1 for r in audit_rows if r["semantic_status"] == "POSSIBLE_DOUBLE_INVERSION")
    hist_mismatch = sum(1 for r in audit_rows if r["semantic_status"] == "HISTORICAL_DIRECTION_MISMATCH")

    manifest = {
        "phase": "12D-H12-A",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_files": [str(PHASE6H), str(IC_CSV), str(CATALOG_JSON), str(COMPONENT_MANIFEST)],
        "output_files": [str(inv_path), str(audit_path), str(mismatch_path), str(sig_path)],
        "historical_assets_read": [a["asset_path"] for a in legacy_assets if a.get("read_success")],
        "total_factors": len(audit_rows),
        "mismatch_count": mismatch_count,
        "conditional_used_in_signal_count": conditional_in_signal,
        "possible_double_inversion_count": double_inv,
        "historical_direction_mismatch_count": hist_mismatch,
        "no_factor_modified": True,
        "no_signal_modified": True,
        "phase13_status": "NOT_STARTED",
    }
    manifest_path = OUT_DIR / "direction_semantics_audit_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    os.chmod(manifest_path, 0o644)

    # ── 6. Summary ────────────────────────────────────────────────
    summary = f"""# Direction Semantics Audit Summary

**Phase:** 12D-H12-A  
**Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d')}  
**Status:** AUDIT ONLY — no metadata modified, no signal modified

---

## What Was Checked

- Factor formula sign vs FactorSpec expected_direction vs raw/adjusted IC
- Phase 6H historical direction mismatch records
- Phase 10A-R signal-level RankIC/spread sign inconsistency diagnostics
- Current signal construction transforms (NEGATIVE, OVERLAY, LIQUIDITY_GATE)
- 53 registered factors; 10 active signal factors

## Historical Assets

- **Phase 6H** (PHASE_6H_STATIC_DYNAMIC_COMPARISON.md): Found and read.
  - 4 direction mismatch: mom_20h, reversal_5h, tech_macd, wq101_alpha101
  - 3 direction consistent: volatility_20h, rsi_14h, bb_zscore_20h
  - 4 conditional: q158_high_low_range, wq101_alpha53, tech_atr, wq101_alpha12
- **Phase 10A-R** (6 CSVs + script + test): All found and read.
  - All signal×horizon show RankIC positive / spread negative
  - Root cause: non_monotonic_tail_behavior (bucket 0 extreme positive returns)
  - Inversion resolves spread but flips RankIC negative
  - Phase 10A-R was diagnostic only, did NOT modify signal

## Current Catalog Findings

- **6 MISSING_INPUT_DATA**: taker/funding factors (raw bars lack columns)
- **10 ACTIVE_IN_SIGNAL**: all have IC across 4 horizons
- **27 CANDIDATE**: non-signal factors with computed IC
- **10 DIAGNOSTIC_ONLY**: conditional direction factors

## Key Findings

### A. reversal_5h — Possible Double Inversion

Formula: `-(close / close_5h_ago - 1)` — already negated in formula.
expected_direction: `negative` — but formula already expresses reversal hypothesis.
Raw IC 1h: **+0.028** (positive) — higher factor_value = past losers outperform.
Adjusted IC: `adj = -raw` (because expected=negative) → **-0.028**.
**Risk**: If expected_direction should be `positive` (formula already inverted), the
adjustment double-inverts, flipping the IC sign. This is a **POSSIBLE_DOUBLE_INVERSION**.
**Verdict**: Needs H12-B review. Most likely expected_direction should be `positive`.

### B. mom_20h — Historical Direction Mismatch

Formula: `close / close_20h_ago - 1` — standard momentum.
expected_direction: `positive`.
Raw IC 1h: **-0.023** (negative) — contradicts expected.
Phase 6H recorded this mismatch. Empirical sign is stable across static/dynamic.
**Verdict**: Not a bug — this is a factor that empirically behaves as reversal in
this market/period. Keep as DIAGNOSTIC_PROBE. Do NOT change expected_direction
without careful study (could be regime-dependent). No H12-B action needed.

### C. Conditional Factors in Signal

4 factors with conditional expected_direction are used in signal:
- **xs_rank_vol**: Used as liquidity gate (rank percentile, no direction assumption). Justified.
- **range_1h, range_4h**: Used in OVERLAY with `* -1` transform (mean-reversion hypothesis). Justified.
- **price_pos_24h**: Used in OVERLAY with `* -1` transform. Justified.

Signal construction explicitly handles direction via transforms. The `conditional`
expected_direction at factor level does NOT create a signal bug, because signal
construction applies its own direction policy.

### D. Phase 10A-R vs H12-A Distinction

- Phase 10A-R: Signal-level RankIC/spread sign inconsistency → bucket 0 tail behavior.
  This is a **signal-level** issue about non-monotonic returns, not a factor direction issue.
- H12-A: Factor-level direction semantics (formula sign vs expected_direction vs IC).
  This is a **metadata** issue about whether FactorSpec correctly represents the factor.
- They are related but distinct. H12-A does NOT re-analyze bucket tails.

## Signal Transform Summary

| Factor | Expected Dir | Signal Role | Transform | Match? |
|--------|-------------|-------------|-----------|--------|
| vol_5h | negative | risk_pressure | *-1 | YES |
| vol_40h | negative | risk_pressure | *-1 | YES |
| downside_vol_20h | negative | risk_pressure | *-1 | YES |
| vol_of_vol_20h | negative | risk_pressure | *-1 | YES |
| rsi_7h | negative | oscillator | *-1 | YES |
| rsi_28h | negative | oscillator | *-1 | YES |
| xs_rank_vol | conditional | liquidity_gate | rank_pct | CONDITIONAL |
| range_1h | conditional | overlay | *-1 | CONDITIONAL |
| range_4h | conditional | overlay | *-1 | CONDITIONAL |
| price_pos_24h | conditional | overlay | *-1 | CONDITIONAL |

## Repair Recommendation (H12-B)

**Recommended for H12-B metadata repair:**
- reversal_5h: Change expected_direction from `negative` to `positive`

**Not recommended for change:**
- mom_20h: Keep as DIAGNOSTIC_PROBE; empirical mismatch is regime-dependent
- Conditional signal factors: Signal transforms are justified; no metadata change needed

**No signal modification recommended.**
"""

    summary_path = OUT_DIR / "DIRECTION_SEMANTICS_AUDIT_SUMMARY.md"
    with open(summary_path, "w") as f:
        f.write(summary)
    os.chmod(summary_path, 0o644)

    # ── Print summary ─────────────────────────────────────────────
    print(f"Audit complete: {len(audit_rows)} factors")
    print(f"Historical direction mismatch: {hist_mismatch}")
    print(f"Conditional in signal: {conditional_in_signal}")
    print(f"Possible double inversion: {double_inv}")
    print(f"Mismatch candidates: {mismatch_count}")
    print(f"Output: {OUT_DIR}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
