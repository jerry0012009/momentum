#!/usr/bin/env python3
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "rank251_survivor_followup_20260330"
ART_DIR.mkdir(parents=True, exist_ok=True)

SOURCE = ROOT / "reports" / "artifacts" / "scout_rank228_dc_overshoot_survivor_followup" / "btcusdt_1m.csv"
ANCHORS = [0, 8, 16]
TRAIN_DAYS = 30
TEST_DAYS = 7
MIN_TRAIN_OBS = 20
ROUNDTRIP_COST_BPS = 6.0
MAX_CANDIDATES_PER_ANCHOR = 5


@dataclass
class WindowPick:
    anchor: int
    train_start: str
    train_end: str
    test_start: str
    test_end: str
    pred_hour: int
    tgt_hour: int
    beta: float
    train_mean_net_bps: float
    test_mean_net_bps: float
    test_trades: int


def load_hour_frame() -> pd.DataFrame:
    df = pd.read_csv(SOURCE)
    df["ts"] = pd.to_datetime(df["ts"], utc=True)
    hourly = (
        df.set_index("ts")
        .resample("1h")
        .agg(open=("open", "first"), close=("close", "last"))
        .dropna()
        .reset_index()
    )
    hourly["hour_ret"] = hourly["close"] / hourly["open"] - 1.0
    return hourly


def build_daily_matrix(hourly: pd.DataFrame, anchor: int) -> pd.DataFrame:
    shifted = hourly.copy()
    shifted["pseudo_day"] = (shifted["ts"] - pd.Timedelta(hours=anchor)).dt.floor("D")
    shifted["slot"] = ((shifted["ts"].dt.hour - anchor) % 24).astype(int)
    mat = shifted.pivot_table(index="pseudo_day", columns="slot", values="hour_ret", aggfunc="first")
    mat = mat.sort_index().dropna(axis=0, how="any")
    return mat


def evaluate_anchor(mat: pd.DataFrame, anchor: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    days = list(mat.index)
    window_picks: list[WindowPick] = []
    candidate_rows: list[dict] = []
    realized_rows: list[dict] = []
    if len(days) < TRAIN_DAYS + TEST_DAYS + 1:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    pair_list = [(i, j) for i in range(24) for j in range(i + 1, 24)]
    for start in range(0, len(days) - TRAIN_DAYS - TEST_DAYS + 1, TEST_DAYS):
        train_days = days[start : start + TRAIN_DAYS]
        test_days = days[start + TRAIN_DAYS : start + TRAIN_DAYS + TEST_DAYS]
        train = mat.loc[train_days]
        test = mat.loc[test_days]
        scored: list[dict] = []
        for i, j in pair_list:
            x = train[i]
            y = train[j]
            ok = x.notna() & y.notna()
            if int(ok.sum()) < MIN_TRAIN_OBS:
                continue
            x_ok = x[ok]
            y_ok = y[ok]
            denom = float((x_ok ** 2).sum())
            if denom <= 0:
                continue
            beta = float((x_ok * y_ok).sum() / denom)
            if beta == 0 or not np.isfinite(beta):
                continue
            train_edge = np.sign(beta) * np.sign(x_ok) * y_ok - ROUNDTRIP_COST_BPS / 10000.0
            test_ok = test[i].notna() & test[j].notna()
            x_test = test.loc[test_ok, i]
            y_test = test.loc[test_ok, j]
            test_edge = np.sign(beta) * np.sign(x_test) * y_test - ROUNDTRIP_COST_BPS / 10000.0
            scored.append({
                "anchor": anchor,
                "train_start": str(train_days[0].date()),
                "train_end": str(train_days[-1].date()),
                "test_start": str(test_days[0].date()),
                "test_end": str(test_days[-1].date()),
                "pred_hour": i,
                "tgt_hour": j,
                "beta": beta,
                "train_obs": int(ok.sum()),
                "train_mean_net_bps": float(train_edge.mean() * 10000.0),
                "train_win_rate": float((train_edge > 0).mean()),
                "test_mean_net_bps": float(test_edge.mean() * 10000.0) if len(test_edge) else np.nan,
                "test_win_rate": float((test_edge > 0).mean()) if len(test_edge) else np.nan,
                "test_trades": int(len(test_edge)),
            })
        if not scored:
            continue
        scored_df = pd.DataFrame(scored).sort_values(["train_mean_net_bps", "train_win_rate"], ascending=[False, False])
        candidate_rows.extend(scored_df.head(MAX_CANDIDATES_PER_ANCHOR).to_dict(orient="records"))
        best = scored_df.iloc[0]
        window_picks.append(WindowPick(
            anchor=anchor,
            train_start=str(best["train_start"]),
            train_end=str(best["train_end"]),
            test_start=str(best["test_start"]),
            test_end=str(best["test_end"]),
            pred_hour=int(best["pred_hour"]),
            tgt_hour=int(best["tgt_hour"]),
            beta=float(best["beta"]),
            train_mean_net_bps=float(best["train_mean_net_bps"]),
            test_mean_net_bps=float(best["test_mean_net_bps"]),
            test_trades=int(best["test_trades"]),
        ))
        test_ok = test[int(best["pred_hour"])].notna() & test[int(best["tgt_hour"])].notna()
        x_test = test.loc[test_ok, int(best["pred_hour"])]
        y_test = test.loc[test_ok, int(best["tgt_hour"])]
        trade_ret = np.sign(best["beta"]) * np.sign(x_test) * y_test - ROUNDTRIP_COST_BPS / 10000.0
        for day, xval, yval, rval in zip(x_test.index, x_test.values, y_test.values, trade_ret.values):
            realized_rows.append({
                "anchor": anchor,
                "test_window_start": str(best["test_start"]),
                "pseudo_day": str(day.date()),
                "pred_hour": int(best["pred_hour"]),
                "tgt_hour": int(best["tgt_hour"]),
                "beta_sign": int(np.sign(best["beta"])),
                "pred_ret_bps": float(xval * 10000.0),
                "tgt_ret_bps": float(yval * 10000.0),
                "net_trade_bps": float(rval * 10000.0),
            })
    return pd.DataFrame([w.__dict__ for w in window_picks]), pd.DataFrame(candidate_rows), pd.DataFrame(realized_rows)


def summarize(window_df: pd.DataFrame, anchor: int) -> dict:
    if window_df.empty:
        return {
            "anchor": anchor,
            "windows": 0,
            "unique_pairs": 0,
            "test_mean_net_bps": np.nan,
            "positive_windows": 0,
            "negative_windows": 0,
            "stable_pair": False,
        }
    pair_counts = window_df.groupby(["pred_hour", "tgt_hour"]).size().reset_index(name="count")
    stable_pair = bool((pair_counts["count"] >= 2).any())
    return {
        "anchor": anchor,
        "windows": int(len(window_df)),
        "unique_pairs": int(pair_counts.shape[0]),
        "test_mean_net_bps": float(window_df["test_mean_net_bps"].mean()),
        "positive_windows": int((window_df["test_mean_net_bps"] > 0).sum()),
        "negative_windows": int((window_df["test_mean_net_bps"] <= 0).sum()),
        "stable_pair": stable_pair,
    }


def main() -> None:
    hourly = load_hour_frame()
    hourly.to_csv(ART_DIR / "btc_hourly_frame.csv", index=False)

    window_frames = []
    candidate_frames = []
    realized_frames = []
    summary_rows = []
    for anchor in ANCHORS:
        mat = build_daily_matrix(hourly, anchor)
        mat.to_csv(ART_DIR / f"anchor_{anchor:02d}_daily_matrix.csv")
        window_df, candidate_df, realized_df = evaluate_anchor(mat, anchor)
        if not window_df.empty:
            window_df.to_csv(ART_DIR / f"anchor_{anchor:02d}_window_best_pairs.csv", index=False)
            candidate_df.to_csv(ART_DIR / f"anchor_{anchor:02d}_window_top_candidates.csv", index=False)
            realized_df.to_csv(ART_DIR / f"anchor_{anchor:02d}_window_realized_trades.csv", index=False)
            window_frames.append(window_df)
            candidate_frames.append(candidate_df)
            realized_frames.append(realized_df)
        summary_rows.append(summarize(window_df, anchor))

    summary = pd.DataFrame(summary_rows)
    summary.to_csv(ART_DIR / "anchor_summary.csv", index=False)

    all_windows = pd.concat(window_frames, ignore_index=True) if window_frames else pd.DataFrame()
    if not all_windows.empty:
        all_windows.to_csv(ART_DIR / "all_window_best_pairs.csv", index=False)
        pair_counts = all_windows.groupby(["anchor", "pred_hour", "tgt_hour", (all_windows["beta"] > 0).map({True: "cont", False: "reversal"})]).size().reset_index(name="count")
        pair_counts.columns = ["anchor", "pred_hour", "tgt_hour", "mode", "count"]
        pair_counts.to_csv(ART_DIR / "pair_reuse_counts.csv", index=False)
    else:
        pair_counts = pd.DataFrame(columns=["anchor", "pred_hour", "tgt_hour", "mode", "count"])

    stable_positive = summary[(summary["stable_pair"] == True) & (summary["test_mean_net_bps"] > 0)]
    any_anchor_positive = bool((summary["test_mean_net_bps"] > 0).any())
    decision = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "source": str(SOURCE.relative_to(ROOT)),
        "sample_start": str(hourly["ts"].min()),
        "sample_end": str(hourly["ts"].max()),
        "anchors": ANCHORS,
        "train_days": TRAIN_DAYS,
        "test_days": TEST_DAYS,
        "roundtrip_cost_bps": ROUNDTRIP_COST_BPS,
        "summary": summary.to_dict(orient="records"),
        "stable_reused_pairs": pair_counts[pair_counts["count"] >= 2].sort_values(["count", "anchor"], ascending=[False, True]).to_dict(orient="records") if not pair_counts.empty else [],
    }
    if stable_positive.empty:
        decision["verdict"] = "background_P0"
        decision["one_line"] = "Rank 251 的唯一 survivor follow-up 已收口：在 BTC 近 90 天、UTC 00/08/16 三种 pseudo-day 锚点下，30d train / 7d OOS 每窗挑最强 hour-pair 后，最佳 pair 会频繁换槽，三种锚点都没有留下既重复出现又成本后为正的稳定 pocket，因此更像网格挖掘，不足以升 P2。"
    else:
        decision["verdict"] = "promote_P2"
        decision["one_line"] = "至少一个 pseudo-day 锚点留下了可重复出现且成本后为正的 stable hour-pair pocket，Rank 251 可升 P2。"
    (ART_DIR / "decision.json").write_text(json.dumps(decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(decision, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
