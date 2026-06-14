"""Phase 7H: Batch-2 candidate selection and operator gap analysis."""
from __future__ import annotations

import pandas as pd
from pathlib import Path

RUN = Path("research/factor_runs/crypto_top50_factor_library")

AVAILABLE_OPS = {"delay","delta","rolling_mean","rolling_std","rolling_min","rolling_max",
                 "rolling_corr","rolling_sum","ts_rank","zscore","signed_power","ema","true_range"}
AVAILABLE_DATA = {"open","high","low","close","volume","quote_volume"}


def classify_op(fid: str, source: str) -> str:
    fid_l = fid.lower()
    if source == "worldquant":
        return "rolling_mean;rolling_std;zscore;signed_power;ts_rank"
    if source == "alibaba":
        return "rolling_mean;rolling_std;ts_rank;ema"
    if "rsi" in fid_l: return "rolling_mean;delta"
    if "stoch" in fid_l: return "rolling_min;rolling_max"
    if "williams" in fid_l: return "rolling_min;rolling_max"
    if "cci" in fid_l: return "rolling_mean;rolling_std"
    if "adx" in fid_l: return "rolling_mean;ema;true_range"
    if "ema" in fid_l: return "ema;rolling_mean"
    if "skew" in fid_l or "kurt" in fid_l: return "rolling_mean;rolling_std"
    if "vol_of_vol" in fid_l: return "rolling_std;rolling_mean"
    if "downside_vol" in fid_l or "upside_vol" in fid_l: return "rolling_std;rolling_mean"
    if "consolidation" in fid_l: return "rolling_max;rolling_min;rolling_mean"
    if "breakout" in fid_l or "breakdown" in fid_l: return "rolling_max;rolling_min"
    if "trend_strength" in fid_l: return "rolling_mean;rolling_std;ema"
    if "body_ratio" in fid_l or "wick_ratio" in fid_l: return "rolling_mean"
    if "gap_up" in fid_l: return "rolling_mean"
    if "xs_rank" in fid_l: return "cross_sectional_rank"
    if "range" in fid_l: return "rolling_max;rolling_min"
    if "ratio" in fid_l: return "rolling_mean;rolling_std;zscore"
    if "gap" in fid_l: return "rolling_mean;ema"
    if "accel" in fid_l: return "delta;rolling_mean"
    return "rolling_mean;rolling_std"


def score(row, batch1_families: set[str]) -> tuple[int, dict]:
    fid = row["factor_id"]
    family = row["factor_family"]
    source = row["source"]
    direction = row["expected_direction"]
    required_cols = str(row.get("required_columns", ""))
    lb = str(row.get("lookback_window", ""))
    cols = [c.strip() for c in required_cols.replace(";", ",").split(",") if c.strip()]

    # data_ready
    data = 3 if all(c in AVAILABLE_DATA for c in cols) else 0

    # ops_supported
    ops = 2 if source in ("worldquant", "alibaba") else 3

    # novelty_vs_batch1 — strict
    if family not in batch1_families:
        novelty = 3  # genuinely new family
    else:
        # Same family as Batch-1 — lookback variants score low
        novelty = 1  # default: same family = limited novelty

    # risk_control
    if direction == "conditional":
        risk = 1
    elif direction in ("positive", "negative"):
        risk = 2
        try:
            if int(lb) >= 20:
                risk = 3
        except:
            pass
    else:
        risk = 1

    return data + ops + novelty + risk, {"data": data, "ops": ops, "novelty": novelty, "risk": risk}


def decide(row, total: int, batch1_families: set[str]):
    fid = row["factor_id"]
    family = row["factor_family"]
    direction = row["expected_direction"]
    source = row["source"]
    required_cols = str(row.get("required_columns", ""))
    cols = [c.strip() for c in required_cols.replace(";", ",").split(",") if c.strip()]

    # Hard blocker: missing data
    if any(c not in AVAILABLE_DATA for c in cols):
        return "DEFER_DATA", "requires data source not currently available"

    # Formulaic alpha penalty: require higher threshold
    if source == "worldquant" and total < 11:
        return "DEFER_REDUNDANT", f"score={total}, formulaic alpha needs stronger novelty signal"
    if source == "alibaba" and total < 11:
        return "DEFER_REDUNDANT", f"score={total}, formulaic alpha needs stronger novelty signal"

    if total >= 10:
        if direction == "conditional":
            return "DEFER_DIRECTION_UNCLEAR", f"score={total}, conditional direction"
        return "SELECT_NOW", f"score={total}, meets criteria"
    elif total >= 7:
        if direction == "conditional":
            return "DEFER_DIRECTION_UNCLEAR", f"score={total}, conditional direction"
        return "DEFER_REDUNDANT", f"score={total}, below SELECT_NOW threshold"
    else:
        return "REJECT_FOR_NOW", f"score={total}, below minimum"


def main():
    cand = pd.read_csv(RUN / "factor_mining_candidates_v0_1.csv")
    curated = pd.read_csv(RUN / "phase7g_curated_factor_library_v0_2.csv")
    batch1_ids = set(curated["factor_id"])
    batch1_families = set(curated["factor_family"])

    results = []
    for _, row in cand.iterrows():
        if row["status"] == "selected_for_7B":
            continue
        total, details = score(row, batch1_families)
        fid = row["factor_id"]
        family = row["factor_family"]
        direction = row["expected_direction"]
        source = row["source"]
        formula = str(row.get("formula_description", ""))
        required_cols = str(row.get("required_columns", ""))
        cols = [c.strip() for c in required_cols.replace(";", ",").split(",") if c.strip()]

        decision, reason = decide(row, total, batch1_families)

        req_ops = classify_op(fid, source)
        ops_list = [o.strip() for o in req_ops.split(";")]
        supported = all(o in AVAILABLE_OPS for o in ops_list)
        current_ops = "YES" if supported else ("PARTIAL" if any(o in AVAILABLE_OPS for o in ops_list) else "NO")

        prop_status = {"SELECT_NOW": "SELECTED_FOR_7I_IMPLEMENTATION", "REJECT_FOR_NOW": "REJECTED_FOR_NOW"}.get(decision, "DEFERRED")
        red_risk = "LOW" if family not in batch1_families else ("MODERATE" if details["novelty"] >= 2 else "HIGH")
        turn_risk = "HIGH" if "candle" in family else ("MODERATE" if direction == "conditional" else "LOW")
        leakage = "LOW" if direction in ("positive", "negative") else "MODERATE"
        dir_clarity = "CLEAR" if direction in ("positive", "negative") else "UNCLEAR"

        results.append({
            "factor_id": fid,
            "factor_family": family,
            "candidate_formula_or_description": formula[:80],
            "source": source,
            "data_requirements": required_cols,
            "required_ops": req_ops,
            "current_ops_supported": current_ops,
            "implementation_complexity": row["implementation_complexity"],
            "leakage_risk": leakage,
            "redundancy_risk_vs_batch1": red_risk,
            "turnover_risk": turn_risk,
            "direction_clarity": dir_clarity,
            "expected_direction": direction,
            "batch2_decision": decision,
            "selection_score": total,
            "decision_reason": reason,
            "proposed_next_status": prop_status,
            "notes": f"data={details['data']} ops={details['ops']} novelty={details['novelty']} risk={details['risk']}",
        })

    sel_df = pd.DataFrame(results)
    sel_df.to_csv(RUN / "phase7h_batch2_candidate_selection.csv", index=False)

    # Summary
    print("=== SELECTION SUMMARY ===")
    counts = {}
    for d in ["SELECT_NOW", "DEFER_REDUNDANT", "DEFER_DATA", "DEFER_OPS", "DEFER_LEAKAGE_RISK", "DEFER_DIRECTION_UNCLEAR", "REJECT_FOR_NOW"]:
        cnt = (sel_df["batch2_decision"] == d).sum()
        counts[d] = cnt
        if cnt: print(f"  {d}: {cnt}")
    print(f"  TOTAL: {len(sel_df)}")

    sn = sel_df[sel_df["batch2_decision"] == "SELECT_NOW"]
    print(f"\n=== SELECT_NOW ({len(sn)}) ===")
    for _, r in sn.iterrows():
        print(f"  {r['factor_id']:25s} | {r['factor_family']:25s} | score={r['selection_score']} | {r['direction_clarity']}")

    print(f"\n=== DEFERRED ({(sel_df['batch2_decision'].str.startswith('DEFER')).sum()}) ===")
    for d in ["DEFER_REDUNDANT", "DEFER_DATA", "DEFER_DIRECTION_UNCLEAR"]:
        sub = sel_df[sel_df["batch2_decision"] == d]
        if len(sub) > 0:
            print(f"\n  {d}: {len(sub)}")
            for _, r in sub.iterrows():
                print(f"    {r['factor_id']:25s} | {r['factor_family']:25s} | score={r['selection_score']}")

    # Operator gap analysis
    needed_ops = set()
    for _, r in sel_df.iterrows():
        for op in r["required_ops"].split(";"):
            needed_ops.add(op.strip())

    ops_rows = []
    for op in sorted(needed_ops):
        factors = sel_df[sel_df["required_ops"].str.contains(op, na=False)]["factor_id"].tolist()
        if op in AVAILABLE_OPS:
            gap_type, supporting, priority = "NO_GAP", "scripts/factor_ops.py", "N/A"
        elif op == "cross_sectional_rank":
            gap_type, supporting, priority = "SMALL_EXTENSION", "needs new cross_sectional_rank function", "HIGH"
        else:
            gap_type, supporting, priority = "MEDIUM_EXTENSION", "not in factor_ops.py", "MEDIUM"
        ops_rows.append({
            "required_op": op,
            "needed_by_factors": "; ".join(factors[:5]),
            "currently_supported": "YES" if gap_type == "NO_GAP" else "NO",
            "supporting_file": supporting,
            "gap_type": gap_type,
            "implementation_priority": priority,
            "notes": "",
        })

    pd.DataFrame(ops_rows).to_csv(RUN / "phase7h_operator_gap_analysis.csv", index=False)
    print(f"\n=== OPERATOR GAPS ({len(ops_rows)}) ===")
    for r in ops_rows:
        print(f"  {r['required_op']:20s} | {r['gap_type']} | factors needing: {r['needed_by_factors'][:60]}")


if __name__ == "__main__":
    main()
