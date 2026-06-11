#!/usr/bin/env python3
"""Step 1.3 H1.3 daily-side stall/momentum-loss screen.

Focus: new-coin events from Step 1 (streak_label == 'new').

Goal: test whether daily-side stall proxies after new events add any edge
relative to naive T+1 continuation / T+1 reversal.

This script intentionally stays on daily data first to keep scope small.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PANEL_PATH = ROOT / "reports" / "artifacts" / "rank154_long_history" / "daily_panel.pkl"
V1_EVENTS = ROOT / "reports" / "artifacts" / "binance_daily_event_study_v1" / "events_v1.csv"
V1_2_EVENTS = ROOT / "reports" / "artifacts" / "binance_daily_event_study_v1_2" / "events_t1_state_v1_2.csv"
OUT = ROOT / "reports" / "artifacts" / "binance_daily_event_study_v1_3"
HORIZONS = (3, 5)
COST_BPS = 10


def pct(v: float) -> float:
    return round(v * 100, 3)


def safe_mean(s: pd.Series) -> float:
    return float(s.mean()) if len(s) else float("nan")


def safe_median(s: pd.Series) -> float:
    return float(s.median()) if len(s) else float("nan")


def safe_winrate(s: pd.Series) -> float:
    return float((s > 0).mean()) if len(s) else float("nan")


def load_inputs():
    panel = pd.read_pickle(PANEL_PATH)
    v1 = pd.read_csv(V1_EVENTS)
    v1_2 = pd.read_csv(V1_2_EVENTS)
    return panel, v1, v1_2


def build_panel_features(panel: pd.DataFrame) -> pd.DataFrame:
    p = panel.sort_values(["symbol", "date"]).copy()
    p["ret_1d"] = p["close"] / p.groupby("symbol", observed=True)["close"].shift(1) - 1.0
    p["high_proxy"] = p["close"]
    p["t1_close"] = p.groupby("symbol", observed=True)["close"].shift(-1)
    p["t2_close"] = p.groupby("symbol", observed=True)["close"].shift(-2)
    p["t3_close"] = p.groupby("symbol", observed=True)["close"].shift(-3)
    p["t5_close"] = p.groupby("symbol", observed=True)["close"].shift(-5)
    p["t1_ret"] = p["t1_close"] / p["close"] - 1.0
    p["t2_ret_from_t1"] = p["t2_close"] / p["t1_close"] - 1.0
    p["t1_qvol"] = p.groupby("symbol", observed=True)["quote_volume"].shift(-1)
    p["t2_qvol"] = p.groupby("symbol", observed=True)["quote_volume"].shift(-2)
    p["fwd_ret_3_from_t2"] = p.groupby("symbol", observed=True)["close"].shift(-5) / p["t2_close"] - 1.0
    p["fwd_ret_5_from_t2"] = p.groupby("symbol", observed=True)["close"].shift(-7) / p["t2_close"] - 1.0
    p["trailing_high_3d"] = p.groupby("symbol", observed=True)["close"].rolling(3, min_periods=1).max().reset_index(level=0, drop=True)
    return p


def classify_gainer_candidates(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["qvol_ratio_t2_t1"] = d["t2_qvol"] / d["t1_qvol"]

    # Candidate A: continuation stalls after T+1 up
    d["candidate_A"] = (
        (d["t1_ret"] > 0)
        & (d["t2_ret_from_t1"] < 0)
        & (d["t2_close"] < d["t1_close"])
    )

    # Candidate B: volume-expanded continuation, then volume contraction + stall
    d["candidate_B"] = (
        (d["t1_ret"] > 0)
        & (d["qvol_ratio_t2_t1"] < 0.85)
        & (d["t2_ret_from_t1"] <= 0)
    )

    # Candidate C: T+1 up but 2d cumulative from T+1 still negative (exhaustion proxy)
    d["candidate_C"] = (
        (d["t1_ret"] > 0)
        & ((d["t1_ret"] + d["t2_ret_from_t1"]) < 0)
    )

    # Baselines
    d["baseline_continue"] = d["t1_ret"] > 0
    d["baseline_stall"] = d["t1_ret"] <= 0
    return d


def classify_loser_candidates(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["qvol_ratio_t2_t1"] = d["t2_qvol"] / d["t1_qvol"]

    # Candidate D: loser continuation stalls after T+1 down
    d["candidate_D"] = (
        (d["t1_ret"] < 0)
        & (d["t2_ret_from_t1"] > 0)
        & (d["t2_close"] > d["t1_close"])
    )

    # Candidate E: volume-expanded continuation, then contraction + reversal-ish
    d["candidate_E"] = (
        (d["t1_ret"] < 0)
        & (d["qvol_ratio_t2_t1"] < 0.85)
        & (d["t2_ret_from_t1"] >= 0)
    )

    # Candidate F: T+1 down but 2d cumulative from T+1 flips positive (bounce exhaustion proxy)
    d["candidate_F"] = (
        (d["t1_ret"] < 0)
        & ((d["t1_ret"] + d["t2_ret_from_t1"]) > 0)
    )

    d["baseline_continue"] = d["t1_ret"] < 0
    d["baseline_stall"] = d["t1_ret"] >= 0
    return d


def summarize_candidate(df: pd.DataFrame, mask: pd.Series, label: str, event_type: str, ref_date_col: str = "date") -> dict:
    g = df[mask].copy()
    row = {
        "event_type": event_type,
        "candidate": label,
        "events": int(len(g)),
        "symbols": int(g["symbol"].nunique()),
    }
    for h in HORIZONS:
        col = f"fwd_ret_{h}_from_t2"
        row[f"fwd_{h}d_mean"] = safe_mean(g[col])
        row[f"fwd_{h}d_median"] = safe_median(g[col])
        row[f"fwd_{h}d_win"] = safe_winrate(g[col])
    # rough cost haircut on 5d spread proxy using simple assumption
    row["fwd_5d_mean_net10bps"] = row["fwd_5d_mean"] - (COST_BPS / 10000) if not np.isnan(row["fwd_5d_mean"]) else np.nan
    row["qvol_ratio_t2_t1_median"] = safe_median(g["qvol_ratio_t2_t1"])
    return row


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    panel, v1, v1_2 = load_inputs()
    pfeat = build_panel_features(panel)

    new_events = v1[v1["streak_label"] == "new"].copy()
    new_events["event_date"] = pd.to_datetime(new_events["event_date"], utc=True)

    pfeat["date"] = pd.to_datetime(pfeat["date"], utc=True)

    merged = new_events.merge(
        pfeat,
        left_on=["event_date", "symbol"],
        right_on=["date", "symbol"],
        how="left",
    )

    gainers = merged[merged.event_type == "top_gainer_1d"].copy()
    losers = merged[merged.event_type == "top_loser_1d"].copy()
    gainers = classify_gainer_candidates(gainers)
    losers = classify_loser_candidates(losers)

    rows = []
    rows.append(summarize_candidate(gainers, gainers["baseline_continue"], "gainer_baseline_continue", "top_gainer_1d"))
    rows.append(summarize_candidate(gainers, gainers["baseline_stall"], "gainer_baseline_stall", "top_gainer_1d"))
    rows.append(summarize_candidate(gainers, gainers["candidate_A"], "gainer_A_t2_reversal", "top_gainer_1d"))
    rows.append(summarize_candidate(gainers, gainers["candidate_B"], "gainer_B_volume_contraction_stall", "top_gainer_1d"))
    rows.append(summarize_candidate(gainers, gainers["candidate_C"], "gainer_C_two_day_exhaustion", "top_gainer_1d"))

    rows.append(summarize_candidate(losers, losers["baseline_continue"], "loser_baseline_continue", "top_loser_1d"))
    rows.append(summarize_candidate(losers, losers["baseline_stall"], "loser_baseline_stall", "top_loser_1d"))
    rows.append(summarize_candidate(losers, losers["candidate_D"], "loser_D_t2_reversal", "top_loser_1d"))
    rows.append(summarize_candidate(losers, losers["candidate_E"], "loser_E_volume_contraction_reversal", "top_loser_1d"))
    rows.append(summarize_candidate(losers, losers["candidate_F"], "loser_F_two_day_flip", "top_loser_1d"))

    summary = pd.DataFrame(rows)
    summary.to_csv(OUT / "daily_stall_summary_v1_3.csv", index=False)

    # Candidate selection logic
    selected = []
    for event_type in ["top_gainer_1d", "top_loser_1d"]:
        sub = summary[summary.event_type == event_type].copy()
        baseline_row = sub[sub.candidate.str.contains("baseline_continue")].iloc[0]
        candidates = sub[~sub.candidate.str.contains("baseline")]
        for _, r in candidates.iterrows():
            meets = (
                (r["events"] >= 1200)
                and (
                    (r["fwd_5d_mean"] - baseline_row["fwd_5d_mean"] >= 0.0025)
                    or (r["fwd_5d_win"] - baseline_row["fwd_5d_win"] >= 0.03)
                )
                and (not np.isnan(r["fwd_5d_mean"]))
            )
            selected.append({
                "event_type": event_type,
                "candidate": r["candidate"],
                "events": int(r["events"]),
                "baseline_fwd_5d_mean": baseline_row["fwd_5d_mean"],
                "candidate_fwd_5d_mean": r["fwd_5d_mean"],
                "delta_5d_mean": r["fwd_5d_mean"] - baseline_row["fwd_5d_mean"],
                "baseline_fwd_5d_win": baseline_row["fwd_5d_win"],
                "candidate_fwd_5d_win": r["fwd_5d_win"],
                "delta_5d_win": r["fwd_5d_win"] - baseline_row["fwd_5d_win"],
                "meets_intraday_threshold": bool(meets),
            })
    candidate_selection = pd.DataFrame(selected)
    candidate_selection.to_csv(OUT / "candidate_selection_v1_3.csv", index=False)

    intraday_eligible = bool(candidate_selection["meets_intraday_threshold"].any())
    top_candidates = candidate_selection.sort_values(["meets_intraday_threshold", "delta_5d_mean"], ascending=[False, False]).head(10)

    # Plain Chinese findings
    best_gainer = summary[summary.event_type == "top_gainer_1d"].sort_values("fwd_5d_mean", ascending=False).iloc[0]
    best_loser = summary[summary.event_type == "top_loser_1d"].sort_values("fwd_5d_mean", ascending=False).iloc[0]
    baseline_gainer = summary[(summary.event_type == "top_gainer_1d") & (summary.candidate == "gainer_baseline_continue")].iloc[0]
    baseline_loser = summary[(summary.event_type == "top_loser_1d") & (summary.candidate == "loser_baseline_continue")].iloc[0]

    md = []
    md.append("# Step 1.3 H1.3 日线侧初筛结论\n")
    md.append(f"生成时间: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}\n")
    md.append("## 范围\n")
    md.append("- 只研究 v1 中 streak_label == new 的事件\n")
    md.append("- 先用日线做失速形态初筛\n")
    md.append("- 只有当某个候选模式明显优于 baseline 时，再考虑抽样做 1h 局部验证\n")
    md.append("\n## 结论\n")
    md.append(f"- 涨幅榜最佳日线候选：{best_gainer['candidate']}，5d 均值={pct(best_gainer['fwd_5d_mean'])}%，胜率={pct(best_gainer['fwd_5d_win'])}%\n")
    md.append(f"- 涨幅榜 baseline_continue：5d 均值={pct(baseline_gainer['fwd_5d_mean'])}%，胜率={pct(baseline_gainer['fwd_5d_win'])}%\n")
    md.append(f"- 跌幅榜最佳日线候选：{best_loser['candidate']}，5d 均值={pct(best_loser['fwd_5d_mean'])}%，胜率={pct(best_loser['fwd_5d_win'])}%\n")
    md.append(f"- 跌幅榜 baseline_continue：5d 均值={pct(baseline_loser['fwd_5d_mean'])}%，胜率={pct(baseline_loser['fwd_5d_win'])}%\n")
    md.append(f"- 是否满足继续做 1h 局部样本的门槛：{'是' if intraday_eligible else '否'}\n")
    md.append("\n## 解释\n")
    md.append("这一步的意义不是直接拿到策略，而是看‘失速形态’在日线层面有没有初步证据。")
    md.append("如果日线证据都不够，就不应该立刻扩到全市场小时线；如果日线证据有苗头，再做小样本 1h 回放。\n")
    md.append("\n## 候选模式\n")
    md.append(top_candidates.to_string(index=False))
    (OUT / "findings_v1_3.md").write_text("\n".join(md), encoding="utf-8")

    manifest = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "step": "1.3",
        "scope": "daily-side H1.3 screen first; intraday inspection only if daily evidence is strong",
        "inputs": {
            "panel": str(PANEL_PATH),
            "v1_events": str(V1_EVENTS),
            "v1_2_events": str(V1_2_EVENTS),
        },
        "outputs": {
            "summary": str(OUT / "daily_stall_summary_v1_3.csv"),
            "candidate_selection": str(OUT / "candidate_selection_v1_3.csv"),
            "findings": str(OUT / "findings_v1_3.md"),
        },
        "metrics": {
            "intraday_eligible": intraday_eligible,
            "gainer_best_candidate": best_gainer["candidate"],
            "loser_best_candidate": best_loser["candidate"],
        },
    }
    (OUT / "manifest_v1_3.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[ok] wrote {OUT}")
    print("\n[summary]")
    print(summary[["event_type", "candidate", "events", "fwd_5d_mean", "fwd_5d_win", "fwd_5d_mean_net10bps", "qvol_ratio_t2_t1_median"]].to_string(index=False))
    print("\n[candidate selection]")
    print(candidate_selection.to_string(index=False))
    print("\n[intraday eligible]", intraday_eligible)


if __name__ == "__main__":
    main()
