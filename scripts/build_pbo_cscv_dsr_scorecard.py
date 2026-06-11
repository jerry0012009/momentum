from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

COST_PER_SIDE_BPS = 6.0
ROUNDTRIP_COST = COST_PER_SIDE_BPS * 2 / 10000.0
ARMS = ["baseline", "gate_kept", "gate_veto"]


def parse_args():
    p = argparse.ArgumentParser(description="Canonical-ish CSCV/PBO/DSR offline scorecard from rank139-style trade log.")
    p.add_argument("--trade-log", required=True)
    p.add_argument("--event-col", default="event_0.8")
    p.add_argument("--baseline-col", default="gross_ret")
    p.add_argument("--gate-kept-col")
    p.add_argument("--gate-veto-col")
    p.add_argument("--out-dir", required=True)
    p.add_argument("--label", default="Rank 139 @ thr=0.8")
    p.add_argument("--segments", type=int, default=8)
    return p.parse_args()


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def sample_stdev(xs):
    if len(xs) < 2:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def sample_skew(xs):
    n = len(xs)
    if n < 3:
        return 0.0
    m = mean(xs)
    s = sample_stdev(xs)
    if s == 0:
        return 0.0
    acc = sum(((x - m) / s) ** 3 for x in xs)
    return (n / ((n - 1) * (n - 2))) * acc


def sample_kurtosis(xs):
    n = len(xs)
    if n < 4:
        return 3.0
    m = mean(xs)
    s = sample_stdev(xs)
    if s == 0:
        return 3.0
    acc4 = sum(((x - m) / s) ** 4 for x in xs)
    term1 = (n * (n + 1) / ((n - 1) * (n - 2) * (n - 3))) * acc4
    term2 = (3 * (n - 1) ** 2) / ((n - 2) * (n - 3))
    return term1 - term2 + 3.0


def normal_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def sharpe(xs):
    s = sample_stdev(xs)
    return mean(xs) / s if s > 0 else 0.0


def psr(sr_hat, sr_benchmark, n, skew, kurt):
    if n < 2:
        return 0.5
    denom_term = 1.0 - skew * sr_hat + ((kurt - 1.0) / 4.0) * (sr_hat ** 2)
    denom_term = max(1e-12, denom_term)
    z = (sr_hat - sr_benchmark) * math.sqrt(max(1, n - 1)) / math.sqrt(denom_term)
    return normal_cdf(z)


def dsr(xs, trials):
    n = len(xs)
    sr_hat = sharpe(xs)
    skew = sample_skew(xs)
    kurt = sample_kurtosis(xs)
    # pragmatic benchmark: multiple-testing uplift under approx normal iid trials
    sr_star = math.sqrt(max(0.0, 2.0 * math.log(max(1, trials)))) / math.sqrt(max(1, n))
    return psr(sr_hat, sr_star, n, skew, kurt)


def _parse_optional_ret(value):
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        if value == "":
            return None
    return float(value)


def arm_returns(row, args):
    explicit_mode = bool(args.gate_kept_col or args.gate_veto_col)
    if explicit_mode:
        baseline_gross = _parse_optional_ret(row.get(args.baseline_col))
        gate_kept_gross = _parse_optional_ret(row.get(args.gate_kept_col)) if args.gate_kept_col else None
        gate_veto_gross = _parse_optional_ret(row.get(args.gate_veto_col)) if args.gate_veto_col else None
        out = {}
        if baseline_gross is not None:
            out["baseline"] = baseline_gross - ROUNDTRIP_COST
        if gate_kept_gross is not None:
            out["gate_kept"] = gate_kept_gross - ROUNDTRIP_COST
        if gate_veto_gross is not None:
            out["gate_veto"] = gate_veto_gross - ROUNDTRIP_COST
        return out

    gross = float(row[args.baseline_col])
    net = gross - ROUNDTRIP_COST
    event = row[args.event_col].strip()
    out = {"baseline": net}
    if event != "opp_dir_first":
        out["gate_kept"] = net
    if event == "same_dir_first":
        out["gate_veto"] = net
    return out


def rank_desc(values_by_arm):
    ordered = sorted(values_by_arm.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
    return {arm: i + 1 for i, (arm, _) in enumerate(ordered)}


def split_segments(rows, segments):
    n = len(rows)
    base = n // segments
    rem = n % segments
    out = []
    i = 0
    for s in range(segments):
        size = base + (1 if s < rem else 0)
        out.append(rows[i:i + size])
        i += size
    return [seg for seg in out if seg]


def flatten(chunks):
    out = []
    for c in chunks:
        out.extend(c)
    return out


def summarize_arm(xs, trials):
    return {
        "trades": len(xs),
        "mean_net_6bps": mean(xs),
        "sharpe_6bps": sharpe(xs),
        "dsr_probability": dsr(xs, trials),
        "skewness": sample_skew(xs),
        "kurtosis": sample_kurtosis(xs),
    }


def main():
    args = parse_args()
    rows = list(csv.DictReader(open(args.trade_log, newline="")))
    rows.sort(key=lambda r: r["signal_ts"])

    segments = max(4, args.segments)
    if segments % 2 != 0:
        raise SystemExit("--segments must be even for CSCV")
    if len(rows) < segments:
        raise SystemExit(f"not enough rows ({len(rows)}) for segments={segments}")

    segment_rows = split_segments(rows, segments)
    half = len(segment_rows) // 2
    fold_ids = list(range(len(segment_rows)))
    cs_pairs = list(itertools.combinations(fold_ids, half))

    all_by_arm = defaultdict(list)
    for row in rows:
        for arm, ret in arm_returns(row, args).items():
            all_by_arm[arm].append(ret)

    total_trials = len(ARMS)
    summary = {arm: summarize_arm(all_by_arm.get(arm, []), total_trials) for arm in ARMS}

    lambdas = []
    chosen_counts = defaultdict(int)
    oos_rank_sum = defaultdict(int)
    cs_records = []

    for is_idx in cs_pairs:
        is_set = set(is_idx)
        oos_idx = tuple(i for i in fold_ids if i not in is_set)
        if min(oos_idx, default=-1) < 0:
            continue

        is_rows = flatten(segment_rows[i] for i in is_idx)
        oos_rows = flatten(segment_rows[i] for i in oos_idx)

        is_by_arm = defaultdict(list)
        oos_by_arm = defaultdict(list)
        for row in is_rows:
            for arm, ret in arm_returns(row, args).items():
                is_by_arm[arm].append(ret)
        for row in oos_rows:
            for arm, ret in arm_returns(row, args).items():
                oos_by_arm[arm].append(ret)

        is_metric = {arm: sharpe(is_by_arm.get(arm, [])) for arm in ARMS}
        oos_metric = {arm: sharpe(oos_by_arm.get(arm, [])) for arm in ARMS}
        is_rank = rank_desc(is_metric)
        oos_rank = rank_desc(oos_metric)
        chosen = min(is_rank, key=is_rank.get)
        chosen_counts[chosen] += 1
        chosen_oos_rank = oos_rank[chosen]
        oos_rank_sum[chosen] += chosen_oos_rank
        # PBO lambda should be high when OOS rank is good and low when it falls into the bottom half.
        lam = 1.0 - (chosen_oos_rank / (len(ARMS) + 1.0))
        lambdas.append(lam)
        cs_records.append({
            "is_folds": list(is_idx),
            "oos_folds": list(oos_idx),
            "chosen_arm": chosen,
            "chosen_is_sharpe_6bps": is_metric[chosen],
            "chosen_oos_sharpe_6bps": oos_metric[chosen],
            "chosen_oos_rank": chosen_oos_rank,
            "lambda": lam,
            "logit_lambda": math.log(lam / (1.0 - lam)),
        })

    pbo = mean([1.0 if lam <= 0.5 else 0.0 for lam in lambdas]) if lambdas else 1.0
    median_lambda = sorted(lambdas)[len(lambdas) // 2] if lambdas else 0.0

    for arm in ARMS:
        summary[arm]["cscv_selected_count"] = chosen_counts.get(arm, 0)
        if chosen_counts.get(arm, 0):
            summary[arm]["avg_oos_rank_when_selected"] = oos_rank_sum[arm] / chosen_counts[arm]
        else:
            summary[arm]["avg_oos_rank_when_selected"] = ""
        summary[arm]["pbo"] = pbo
        summary[arm]["lambda_median"] = median_lambda
        summary[arm]["verdict"] = (
            "guard_failed" if pbo > 0.5 else
            "guard_risky" if pbo > 0.2 else
            "guard_passed"
        )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "rank139_pbo_cscv_dsr_scorecard.csv"
    json_path = out_dir / "rank139_pbo_cscv_dsr_meta.json"

    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "label", "arm", "trades", "mean_net_6bps", "sharpe_6bps", "dsr_probability",
            "skewness", "kurtosis", "cscv_selected_count", "avg_oos_rank_when_selected",
            "pbo", "lambda_median", "verdict", "note"
        ])
        writer.writeheader()
        for arm in ARMS:
            row = summary[arm].copy()
            row.update({
                "label": args.label,
                "arm": arm,
                "note": "offline canonical-ish CSCV/PBO + DSR approximation; final production gate may still need pooled multi-family input",
            })
            writer.writerow(row)

    meta = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "label": args.label,
        "source_trade_log": args.trade_log,
        "event_col": args.event_col,
        "baseline_col": args.baseline_col,
        "gate_kept_col": args.gate_kept_col,
        "gate_veto_col": args.gate_veto_col,
        "roundtrip_cost_assumption_bps": COST_PER_SIDE_BPS * 2,
        "segments": len(segment_rows),
        "cs_combinations": len(cs_records),
        "pbo": pbo,
        "lambda_median": median_lambda,
        "verdict": (
            "guard_failed" if pbo > 0.5 else
            "guard_risky" if pbo > 0.2 else
            "guard_passed"
        ),
        "cs_records": cs_records,
        "warning": "This is an offline CSCV/PBO + DSR approximation for scout honesty gating, not a full library-grade statistical package."
    }
    json_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    print(csv_path)
    print(json_path)


if __name__ == "__main__":
    main()
