#!/usr/bin/env python3
"""V0 Audit: IC/RankIC/spread direction consistency, monthly stability,
non-overlap robustness, outlier robustness, and symbol contribution.

Vectorized version — uses pivot + numpy for fast cross-sectional IC."""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
UNIVERSE = "crypto_top50_usdt_perp_1h"
CACHE = ROOT / "data" / "cache" / UNIVERSE
FEATURE = ROOT / "data" / "features" / UNIVERSE
REPORT = ROOT / "reports" / "artifacts" / "factor_eval" / UNIVERSE
OUTDIR = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "audit_v0"
FACTORS = ["mom_20h", "reversal_5h", "volatility_20h", "rsi_14h", "bb_zscore_20h"]
LABELS = ["ret_fwd_1h", "ret_fwd_4h", "ret_fwd_24h", "ret_fwd_72h"]
MIN_N = 10


def clean(x: Any) -> float | None:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return None if (math.isnan(v) or math.isinf(v)) else v


def _nanmean_safe(a: np.ndarray) -> float | None:
    v = np.nanmean(a) if len(a) > 0 else np.nan
    return clean(v)


def _nanstd_safe(a: np.ndarray) -> float | None:
    v = np.nanstd(a, ddof=1) if len(a) > 1 else np.nan
    return clean(v)


def _tstat_arr(a: np.ndarray) -> float | None:
    a = a[~np.isnan(a)]
    if len(a) < 2:
        return None
    s = np.std(a, ddof=1)
    return clean(np.mean(a) / s * math.sqrt(len(a))) if s > 0 else None


def _ratio(m: float | None, s: float | None) -> float | None:
    return clean(m / s) if m is not None and s not in (None, 0) else None


def _pearson_col(x: np.ndarray, y: np.ndarray) -> float | None:
    """Fast Pearson correlation for two 1-d arrays (no NaN)."""
    if len(x) < 2 or np.std(x) == 0 or np.std(y) == 0:
        return None
    return float(np.corrcoef(x, y)[0, 1])


def _spearman_col(x: np.ndarray, y: np.ndarray) -> float | None:
    """Fast Spearman via rank then Pearson."""
    rx = _rank_1d(x)
    ry = _rank_1d(y)
    return _pearson_col(rx, ry)


def _rank_1d(a: np.ndarray) -> np.ndarray:
    """Average rank (like scipy.stats.rankdata average)."""
    sorter = np.argsort(a)
    rank = np.empty_like(sorter, dtype=float)
    rank[sorter] = np.arange(1, len(a) + 1, dtype=float)
    return rank


def winsorize(s: pd.Series, lo: float = 0.01, hi: float = 0.99) -> pd.Series:
    ql, qh = s.quantile(lo), s.quantile(hi)
    return s.clip(lower=ql, upper=qh)


# ─────────── vectorized IC engine ───────────

def _compute_ic_vectorized(
    merged: pd.DataFrame, factor_col: str, label_col: str, min_n: int = MIN_N,
) -> dict[str, Any]:
    """Compute per-timestamp IC using pivot → numpy for speed."""
    sub = merged[["timestamp", "symbol", factor_col, label_col]].dropna()
    if sub.empty:
        return {"IC_mean": None, "IC_std": None, "ICIR": None,
                "RankIC_mean": None, "RankIC_std": None, "RankICIR": None,
                "spread_mean": None, "spread_t": None, "n_timestamps": 0}

    # Pivot: rows=timestamp, cols=symbol
    fv_pivot = sub.pivot_table(index="timestamp", columns="symbol",
                               values=factor_col, aggfunc="first")
    lb_pivot = sub.pivot_table(index="timestamp", columns="symbol",
                               values=label_col, aggfunc="first")
    # align
    common_syms = fv_pivot.columns.intersection(lb_pivot.columns)
    common_ts = fv_pivot.index.intersection(lb_pivot.index)
    fv_mat = fv_pivot.loc[common_ts, common_syms].values  # (T, S)
    lb_mat = lb_pivot.loc[common_ts, common_syms].values   # (T, S)

    T, S = fv_mat.shape
    if S < min_n:
        return {"IC_mean": None, "IC_std": None, "ICIR": None,
                "RankIC_mean": None, "RankIC_std": None, "RankICIR": None,
                "spread_mean": None, "spread_t": None, "n_timestamps": 0}

    ics = np.full(T, np.nan)
    rics = np.full(T, np.nan)
    spreads = np.full(T, np.nan)

    for t in range(T):
        fv_row = fv_mat[t]
        lb_row = lb_mat[t]
        mask = ~(np.isnan(fv_row) | np.isnan(lb_row))
        n = mask.sum()
        if n < min_n:
            continue
        fv_v = fv_row[mask]
        lb_v = lb_row[mask]
        ic = _pearson_col(fv_v, lb_v)
        ric = _spearman_col(fv_v, lb_v)
        if ic is not None:
            ics[t] = ic
        if ric is not None:
            rics[t] = ric
        # quintile spread
        ranks = _rank_1d(fv_v)
        q_labels = np.ceil(ranks / n * 5).astype(int)
        q_labels = np.clip(q_labels, 1, 5)
        q1_mask = q_labels == 1
        q5_mask = q_labels == 5
        if q1_mask.any() and q5_mask.any():
            spreads[t] = np.mean(lb_v[q5_mask]) - np.mean(lb_v[q1_mask])

    ics = ics[~np.isnan(ics)]
    rics = rics[~np.isnan(rics)]
    spreads = spreads[~np.isnan(spreads)]

    icm = _nanmean_safe(ics)
    icsd = _nanstd_safe(ics)
    ricm = _nanmean_safe(rics)
    ricsd = _nanstd_safe(rics)
    return {
        "IC_mean": icm, "IC_std": icsd, "ICIR": _ratio(icm, icsd),
        "RankIC_mean": ricm, "RankIC_std": ricsd, "RankICIR": _ratio(ricm, ricsd),
        "spread_mean": _nanmean_safe(spreads),
        "spread_t": _tstat_arr(spreads),
        "n_timestamps": len(ics),
    }


# ─────────── A: IC sign consistency ───────────

def audit_ic_sign(merged_all: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for fname, df in merged_all.items():
        for label in LABELS:
            m = _compute_ic_vectorized(df, "factor_value", label)
            ic, ric, sp = m["IC_mean"], m["RankIC_mean"], m["spread_mean"]
            ic_ric = (clean(ic) is not None and clean(ric) is not None
                      and (ic > 0) != (ric > 0))
            ic_sp = (clean(ic) is not None and clean(sp) is not None
                     and (ic > 0) != (sp > 0))
            notes = []
            if ic_ric:
                notes.append("IC↔RankIC conflict")
            if ic_sp:
                notes.append("IC↔spread conflict")
            rows.append({
                "factor": fname, "label": label,
                "IC_mean": ic, "RankIC_mean": ric, "spread_mean": sp,
                "IC_sign": "+" if (clean(ic) or 0) > 0 else ("-" if (clean(ic) or 0) < 0 else "0"),
                "RankIC_sign": "+" if (clean(ric) or 0) > 0 else ("-" if (clean(ric) or 0) < 0 else "0"),
                "spread_sign": "+" if (clean(sp) or 0) > 0 else ("-" if (clean(sp) or 0) < 0 else "0"),
                "direction_consistent": not ic_ric and not ic_sp,
                "notes": "; ".join(notes) if notes else "OK",
            })
    return pd.DataFrame(rows)


# ─────────── B: Monthly stability ───────────

def audit_monthly(merged_all: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for fname, df in merged_all.items():
        df = df.copy()
        df["month"] = df["timestamp"].dt.to_period("M")
        for label in LABELS:
            for month, mdf in df.groupby("month", sort=True):
                m = _compute_ic_vectorized(mdf, "factor_value", label)
                rows.append({
                    "factor": fname, "label": label, "month": str(month),
                    "IC_mean": m["IC_mean"], "RankIC_mean": m["RankIC_mean"],
                    "spread_mean": m["spread_mean"], "spread_t": m["spread_t"],
                    "n_timestamps": m["n_timestamps"],
                })
    return pd.DataFrame(rows)


# ─────────── C: Non-overlap labels ───────────

def audit_nonoverlap(merged_all: dict[str, pd.DataFrame],
                     labels_df: pd.DataFrame) -> pd.DataFrame:
    lo = labels_df.copy()
    lo["hour"] = lo["timestamp"].dt.hour
    lo["day"] = lo["timestamp"].dt.day
    mask24 = lo["hour"] == 0
    mask72 = (lo["hour"] == 0) & (lo["day"] % 3 == 0)
    no_map = {
        "ret_fwd_24h": lo.loc[mask24, ["timestamp", "symbol", "ret_fwd_24h"]],
        "ret_fwd_72h": lo.loc[mask72, ["timestamp", "symbol", "ret_fwd_72h"]],
    }
    rows = []
    for fname, df in merged_all.items():
        for label_name, sub_lb in no_map.items():
            m_full = _compute_ic_vectorized(df, "factor_value", label_name)
            # filter to non-overlap timestamps using merge
            ts_keys = sub_lb[["timestamp", "symbol"]].drop_duplicates()
            merged_inner = df.merge(ts_keys, on=["timestamp", "symbol"], how="inner")
            m_no = _compute_ic_vectorized(merged_inner, "factor_value", label_name) if not merged_inner.empty else {
                "IC_mean": None, "RankIC_mean": None, "spread_t": None, "n_timestamps": 0}
            for mode, m in [("full", m_full), ("nonoverlap", m_no)]:
                rows.append({
                    "factor": fname, "label": label_name, "mode": mode,
                    "IC_mean": m["IC_mean"], "RankIC_mean": m["RankIC_mean"],
                    "spread_t": m["spread_t"], "n_timestamps": m["n_timestamps"],
                })
    return pd.DataFrame(rows)


# ─────────── D: Outlier robustness ───────────

def audit_winsorize(merged_all: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for fname, base_df in merged_all.items():
        for label in LABELS:
            m_raw = _compute_ic_vectorized(base_df, "factor_value", label)
            rows.append({"factor": fname, "label": label, "version": "raw", "wlevel": "",
                         "IC_mean": m_raw["IC_mean"], "RankIC_mean": m_raw["RankIC_mean"],
                         "spread_t": m_raw["spread_t"]})
            for w_lo, w_hi, w_name in [(0.01, 0.99, "w199"), (0.05, 0.95, "w595")]:
                df = base_df.copy()
                df["fv_w"] = winsorize(df["factor_value"], w_lo, w_hi)
                df["lbl_w"] = winsorize(df[label], w_lo, w_hi)
                # factor only
                m_f = _compute_ic_vectorized(df, "fv_w", label)
                rows.append({"factor": fname, "label": label, "version": f"factor_{w_name}",
                             "wlevel": w_name,
                             "IC_mean": m_f["IC_mean"], "RankIC_mean": m_f["RankIC_mean"],
                             "spread_t": m_f["spread_t"]})
                # both
                tmp = df.copy()
                tmp[label] = tmp["lbl_w"]
                m_both = _compute_ic_vectorized(tmp, "fv_w", label)
                rows.append({"factor": fname, "label": label, "version": f"both_{w_name}",
                             "wlevel": w_name,
                             "IC_mean": m_both["IC_mean"], "RankIC_mean": m_both["RankIC_mean"],
                             "spread_t": m_both["spread_t"]})
    return pd.DataFrame(rows)


# ─────────── E: Symbol contribution ───────────

def audit_symbol_contribution(merged_all: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Per-symbol Q5/Q1 membership and spread contribution."""
    rows = []
    for fname, df in merged_all.items():
        for label in LABELS:
            valid = df[["timestamp", "symbol", "factor_value", label]].dropna()
            if valid.empty:
                continue
            # assign quintiles per timestamp
            q_parts = []
            for _, g in valid.groupby("timestamp", sort=True):
                if len(g) < MIN_N:
                    continue
                g = g.copy()
                fv = g["factor_value"].values
                n = len(fv)
                ranks = _rank_1d(fv)
                q_labels = np.clip(np.ceil(ranks / n * 5).astype(int), 1, 5)
                g["q"] = q_labels
                q_parts.append(g)
            if not q_parts:
                continue
            qdf = pd.concat(q_parts, ignore_index=True)
            for sym, sdf in qdf.groupby("symbol"):
                n_q5 = int((sdf["q"] == 5).sum())
                n_q1 = int((sdf["q"] == 1).sum())
                mean_ret = clean(sdf[label].mean())
                mean_fv = clean(sdf["factor_value"].mean())
                r5 = sdf.loc[sdf["q"] == 5, label].mean() if n_q5 > 0 else np.nan
                r1 = sdf.loc[sdf["q"] == 1, label].mean() if n_q1 > 0 else np.nan
                contrib = clean(r5 - r1) if not (np.isnan(r5) or np.isnan(r1)) else None
                rows.append({
                    "factor": fname, "label": label, "symbol": sym,
                    "mean_forward_return": mean_ret, "mean_factor_exposure": mean_fv,
                    "n_q5": n_q5, "n_q1": n_q1, "spread_contribution": contrib,
                })
    return pd.DataFrame(rows)


# ─────────── write summary ───────────

def write_summary(sign_df: pd.DataFrame, month_df: pd.DataFrame,
                  nonov_df: pd.DataFrame, wins_df: pd.DataFrame,
                  sym_df: pd.DataFrame) -> None:
    lines = [
        "# V0 Factor Audit Summary", "",
        f"- generated_at: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "- universe: crypto_top50_usdt_perp_1h",
        "- evaluation_period: 2025-12-14 ~ 2026-06-12", "",
    ]

    # ── A ──
    lines += ["## A. IC Sign Consistency", "",
              "| factor | label | IC_sign | RankIC_sign | spread_sign | consistent | notes |",
              "|---|---|---:|---:|---:|---:|---|"]
    for _, r in sign_df.iterrows():
        lines.append(f"| {r['factor']} | {r['label']} | {r['IC_sign']} | {r['RankIC_sign']} | {r['spread_sign']} | {'✓' if r['direction_consistent'] else '✗'} | {r['notes']} |")
    conflicts = sign_df[~sign_df["direction_consistent"]]
    lines += ["", f"**Conflicts:** {len(conflicts)} / {len(sign_df)} pairs", ""]
    if not conflicts.empty:
        for _, r in conflicts.iterrows():
            lines.append(f"- {r['factor']} × {r['label']}: {r['notes']}")

    # ── B ──
    lines += ["", "## B. Monthly Stability", ""]
    for fname in FACTORS:
        sub = month_df[month_df["factor"] == fname]
        if sub.empty:
            continue
        lines += [f"### {fname}", "",
                  "| label | month | IC | RankIC | spread_t | n_ts |",
                  "|---|---|---:|---:|---:|---:|"]
        for _, r in sub.iterrows():
            ic_s = f"{r['IC_mean']:.4f}" if clean(r['IC_mean']) is not None else ""
            ric_s = f"{r['RankIC_mean']:.4f}" if clean(r['RankIC_mean']) is not None else ""
            st_s = f"{r['spread_t']:.2f}" if clean(r['spread_t']) is not None else ""
            lines.append(f"| {r['label']} | {r['month']} | {ic_s} | {ric_s} | {st_s} | {int(r['n_timestamps'])} |")
        lines.append("")

    # monthly direction consistency
    lines += ["### Monthly direction consistency", "",
              "| factor | label | months | consistent | ratio |",
              "|---|---|---:|---:|---:|"]
    for fname in FACTORS:
        for label in LABELS:
            sub = month_df[(month_df["factor"] == fname) & (month_df["label"] == label)]
            ics = sub["IC_mean"].dropna()
            if len(ics) == 0:
                continue
            dom = 1 if (ics > 0).sum() >= (ics < 0).sum() else -1
            cons = int(((ics > 0) == (dom > 0)).sum())
            lines.append(f"| {fname} | {label} | {len(ics)} | {cons} | {cons/len(ics):.2f} |")
    lines.append("")

    # ── C ──
    lines += ["## C. Non-Overlap Labels Audit", "",
              "| factor | label | mode | IC_mean | RankIC_mean | spread_t | n_ts |",
              "|---|---|---|---:|---:|---:|---:|"]
    if not nonov_df.empty:
        for _, r in nonov_df.iterrows():
            ic_s = f"{r['IC_mean']:.4f}" if clean(r['IC_mean']) is not None else ""
            ric_s = f"{r['RankIC_mean']:.4f}" if clean(r['RankIC_mean']) is not None else ""
            st_s = f"{r['spread_t']:.2f}" if clean(r['spread_t']) is not None else ""
            lines.append(f"| {r['factor']} | {r['label']} | {r['mode']} | {ic_s} | {ric_s} | {st_s} | {int(r['n_timestamps'])} |")
    lines += ["",
              "**Interpretation:** If spread_t drops significantly in nonoverlap mode, the",
              "original t-stat was inflated by overlapping samples.", ""]

    # ── D ──
    lines += ["## D. Outlier Robustness (Winsorize)", "",
              "| factor | label | version | IC_mean | RankIC_mean | spread_t |",
              "|---|---|---|---:|---:|---:|"]
    if not wins_df.empty:
        for _, r in wins_df.iterrows():
            ic_s = f"{r['IC_mean']:.4f}" if clean(r['IC_mean']) is not None else ""
            ric_s = f"{r['RankIC_mean']:.4f}" if clean(r['RankIC_mean']) is not None else ""
            st_s = f"{r['spread_t']:.2f}" if clean(r['spread_t']) is not None else ""
            lines.append(f"| {r['factor']} | {r['label']} | {r['version']} | {ic_s} | {ric_s} | {st_s} |")
    lines += ["",
              "**Focus:** If volatility_20h Pearson IC drops sharply after winsorize,",
              "its signal depends on extreme returns.", ""]

    # ── E ──
    lines += ["## E. Symbol Contribution", ""]
    if not sym_df.empty:
        for fname in FACTORS:
            for label in ["ret_fwd_1h", "ret_fwd_24h"]:
                sub = sym_df[(sym_df["factor"] == fname) & (sym_df["label"] == label)]
                if sub.empty:
                    continue
                top5 = sub.nlargest(5, "n_q5")
                bot5 = sub.nlargest(5, "n_q1")
                lines += [f"### {fname} × {label}", "",
                          "Top Q5 symbols:",
                          "| symbol | mean_fwd_ret | mean_factor | n_q5 | n_q1 | spread_contrib |",
                          "|---|---:|---:|---:|---:|---:|"]
                for _, r in top5.iterrows():
                    mfr = f"{r['mean_forward_return']:.6f}" if clean(r['mean_forward_return']) is not None else ""
                    mf = f"{r['mean_factor_exposure']:.4f}" if clean(r['mean_factor_exposure']) is not None else ""
                    sc = f"{r['spread_contribution']:.6f}" if clean(r['spread_contribution']) is not None else ""
                    lines.append(f"| {r['symbol']} | {mfr} | {mf} | {int(r['n_q5'])} | {int(r['n_q1'])} | {sc} |")
                lines += ["", "Top Q1 symbols:",
                          "| symbol | mean_fwd_ret | mean_factor | n_q5 | n_q1 | spread_contrib |",
                          "|---|---:|---:|---:|---:|---:|"]
                for _, r in bot5.iterrows():
                    mfr = f"{r['mean_forward_return']:.6f}" if clean(r['mean_forward_return']) is not None else ""
                    mf = f"{r['mean_factor_exposure']:.4f}" if clean(r['mean_factor_exposure']) is not None else ""
                    sc = f"{r['spread_contribution']:.6f}" if clean(r['spread_contribution']) is not None else ""
                    lines.append(f"| {r['symbol']} | {mfr} | {mf} | {int(r['n_q5'])} | {int(r['n_q1'])} | {sc} |")
                lines.append("")

        # concentration check
        lines += ["### Concentration Risk", "",
                  "If any single symbol appears in Q5 > 30% of timestamps, it dominates the factor.", ""]
        for fname in FACTORS:
            for label in LABELS:
                sub = sym_df[(sym_df["factor"] == fname) & (sym_df["label"] == label)]
                if sub.empty:
                    continue
                try:
                    with open(REPORT / fname / "metrics.json") as f:
                        m = json.load(f)
                    n_ts = m["label_metrics"][label].get("n_timestamps", 1)
                except (FileNotFoundError, KeyError):
                    n_ts = 1
                max_row = sub.loc[sub["n_q5"].idxmax()]
                pct = max_row["n_q5"] / max(n_ts, 1)
                if pct > 0.30:
                    lines.append(f"- ⚠ **{fname} × {label}**: {max_row['symbol']} in Q5 {pct:.0%} of timestamps")

    # ── Verdict ──
    lines += ["", "## Verdict", ""]
    n_conflicts = len(conflicts)

    t_drops = []
    if not nonov_df.empty:
        for fname in FACTORS:
            for label in ["ret_fwd_24h", "ret_fwd_72h"]:
                full_row = nonov_df[(nonov_df["factor"] == fname) & (nonov_df["label"] == label) & (nonov_df["mode"] == "full")]
                no_row = nonov_df[(nonov_df["factor"] == fname) & (nonov_df["label"] == label) & (nonov_df["mode"] == "nonoverlap")]
                if full_row.empty or no_row.empty:
                    continue
                tf = clean(full_row.iloc[0]["spread_t"])
                tn = clean(no_row.iloc[0]["spread_t"])
                if tf and tn and abs(tf) > 0:
                    drop = 1 - abs(tn) / abs(tf)
                    if drop > 0.3:
                        t_drops.append(f"{fname} × {label}: spread_t {tf:.2f} → {tn:.2f} (drop {drop:.0%})")

    lines.append(f"- IC sign conflicts: **{n_conflicts}** / {len(sign_df)}")
    lines.append(f"- Overlap-inflated t-stats (>30% drop): **{len(t_drops)}**")
    for d in t_drops:
        lines.append(f"  - {d}")

    # V1 recommendation
    strong = []
    for fname in ["volatility_20h", "rsi_14h", "bb_zscore_20h"]:
        sub = sign_df[(sign_df["factor"] == fname)]
        for _, r in sub.iterrows():
            if r["label"] in ("ret_fwd_24h", "ret_fwd_72h"):
                ic = clean(r["IC_mean"])
                if ic and abs(ic) > 0.01:
                    strong.append(fname)
                    break
    lines.append("")
    if strong:
        lines.append(f"**Factors worth deeper investigation in V1:** {', '.join(set(strong))}")
    else:
        lines.append("**No factor shows sufficiently stable signal for V1 promotion.**")

    lines += ["",
              "## Next Steps", "",
              "1. If volatility_20h survives winsorize + non-overlap: try combining with rsi_14h as composite",
              "2. Run regime analysis (bull/bear/sideways) to check conditional IC",
              "3. Add cost-adjusted labels (ret_fwd_Xh - estimated_cost) before any strategy consideration",
              "4. Consider 4h or 1d frequency to reduce noise", ""]

    (OUTDIR / "audit_summary.md").write_text("\n".join(lines), encoding="utf-8")


# ─────────── main ───────────

def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)

    print("Loading data...", flush=True)
    labels_df = pd.read_parquet(FEATURE / "labels.parquet")
    labels_df["timestamp"] = pd.to_datetime(labels_df["timestamp"], utc=True)

    merged_all: dict[str, pd.DataFrame] = {}
    for fname in FACTORS:
        fv = pd.read_parquet(FEATURE / fname / "factor_values.parquet")
        fv["timestamp"] = pd.to_datetime(fv["timestamp"], utc=True)
        merged = fv[["timestamp", "symbol", "factor_value"]].merge(
            labels_df, on=["timestamp", "symbol"], how="left")
        merged_all[fname] = merged
        print(f"  {fname}: {len(merged)} rows", flush=True)

    print("\n[A] IC sign consistency...", flush=True)
    sign_df = audit_ic_sign(merged_all)
    sign_df.to_csv(OUTDIR / "ic_sign_consistency.csv", index=False)
    print(f"  → {len(sign_df)} pairs, {len(sign_df[~sign_df['direction_consistent']])} conflicts", flush=True)

    print("[B] Monthly stability...", flush=True)
    month_df = audit_monthly(merged_all)
    month_df.to_csv(OUTDIR / "monthly_stability.csv", index=False)
    print(f"  → {len(month_df)} rows", flush=True)

    print("[C] Non-overlap labels audit...", flush=True)
    nonov_df = audit_nonoverlap(merged_all, labels_df)
    nonov_df.to_csv(OUTDIR / "nonoverlap_metrics.csv", index=False)
    print(f"  → {len(nonov_df)} rows", flush=True)

    print("[D] Winsorize robustness...", flush=True)
    wins_df = audit_winsorize(merged_all)
    wins_df.to_csv(OUTDIR / "winsorized_metrics.csv", index=False)
    print(f"  → {len(wins_df)} rows", flush=True)

    print("[E] Symbol contribution...", flush=True)
    sym_df = audit_symbol_contribution(merged_all)
    sym_df.to_csv(OUTDIR / "symbol_contribution.csv", index=False)
    print(f"  → {len(sym_df)} rows", flush=True)

    print("\nWriting audit_summary.md...", flush=True)
    write_summary(sign_df, month_df, nonov_df, wins_df, sym_df)

    print(f"\n✓ Audit complete → {OUTDIR}/", flush=True)
    for f in sorted(OUTDIR.iterdir()):
        print(f"  {f.name}", flush=True)


if __name__ == "__main__":
    main()
