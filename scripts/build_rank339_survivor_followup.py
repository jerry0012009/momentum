#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PERP_CACHE = ROOT / "reports" / "artifacts" / "scout_rank32b_slope_floor_continuation_15m" / "perp_cache"
ART_DIR = ROOT / "reports" / "artifacts" / "rank339_survivor_followup"
ART_DIR.mkdir(parents=True, exist_ok=True)

SURVIVOR_ASSETS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "LTCUSDT", "BCHUSDT", "SOLUSDT"]
ROTATING_ASSETS = ["AAVEUSDT", "AVAXUSDT", "DOTUSDT", "LINKUSDT", "NEARUSDT", "SUIUSDT", "UNIUSDT", "WLDUSDT", "ZECUSDT"]
ALL_ASSETS = SURVIVOR_ASSETS + ROTATING_ASSETS
LOOKBACK = "30d"
FAST_BARS = 32   # 8h on 15m bars
SLOW_BARS = 96   # 24h on 15m bars
REBARS = 4       # 1h rebalance
LONG_SHORT_Q = 0.20
COST_BPS_RT = 10.0


def load_close_matrix(assets: list[str]) -> pd.DataFrame:
    series = []
    for asset in assets:
        path = PERP_CACHE / f"{asset}__{LOOKBACK}__15m__perp.csv"
        if not path.exists():
            raise FileNotFoundError(path)
        df = pd.read_csv(path, usecols=["timestamp", "close"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        df[asset] = pd.to_numeric(df["close"], errors="coerce")
        series.append(df[["timestamp", asset]].dropna())
    out = series[0]
    for df in series[1:]:
        out = out.merge(df, on="timestamp", how="inner")
    return out.sort_values("timestamp").reset_index(drop=True)


def zscore_cross_section(df: pd.DataFrame) -> pd.DataFrame:
    mean = df.mean(axis=1)
    std = df.std(axis=1, ddof=0).replace(0.0, np.nan)
    return df.sub(mean, axis=0).div(std, axis=0)


def simulate_sleeve(close_df: pd.DataFrame, sleeve_name: str) -> tuple[dict, pd.DataFrame]:
    closes = close_df.set_index("timestamp")
    ret_bar = closes.pct_change().fillna(0.0)
    score_fast = zscore_cross_section(closes.pct_change(FAST_BARS))
    score_slow = zscore_cross_section(closes.pct_change(SLOW_BARS))
    score = 0.5 * score_fast + 0.5 * score_slow

    rebalance_index = np.arange(SLOW_BARS, len(closes) - REBARS, REBARS)
    detail_rows = []
    net_rets = []
    gross_rets = []
    for i in rebalance_index:
        snap = score.iloc[i].dropna().sort_values(ascending=False)
        if len(snap) < 6:
            continue
        bucket = max(1, int(np.floor(len(snap) * LONG_SHORT_Q)))
        long_assets = list(snap.head(bucket).index)
        short_assets = list(snap.tail(bucket).index)
        weights = pd.Series(0.0, index=closes.columns)
        weights[long_assets] = 1.0 / bucket
        weights[short_assets] = -1.0 / bucket
        fwd = ret_bar.iloc[i + 1:i + 1 + REBARS]
        gross = float((fwd * weights).sum(axis=1).sum())
        net = gross - COST_BPS_RT / 10000.0
        gross_rets.append(gross)
        net_rets.append(net)
        detail_rows.append({
            "rebalance_ts": str(closes.index[i]),
            "sleeve": sleeve_name,
            "n_assets": int(len(snap)),
            "bucket": int(bucket),
            "longs": ",".join(long_assets),
            "shorts": ",".join(short_assets),
            "gross_bps": gross * 10000.0,
            "net_bps": net * 10000.0,
        })
    detail = pd.DataFrame(detail_rows)
    arr = np.array(net_rets, dtype=float)
    gross_arr = np.array(gross_rets, dtype=float)
    t_stat = float(arr.mean() / (arr.std(ddof=1) / np.sqrt(len(arr)))) if len(arr) >= 2 and float(arr.std(ddof=1) or 0.0) > 0 else np.nan
    summary = {
        "sleeve": sleeve_name,
        "assets": int(closes.shape[1]),
        "rebalances": int(len(arr)),
        "mean_gross_bps": float(gross_arr.mean() * 10000.0),
        "mean_net_bps": float(arr.mean() * 10000.0),
        "total_net_bps": float(arr.sum() * 10000.0),
        "win_rate": float((arr > 0).mean()),
        "t_stat_net": t_stat,
        "positive_after_cost": bool(arr.mean() > 0),
    }
    return summary, detail


def main() -> None:
    membership = pd.DataFrame(
        [{"sleeve": "survivor", "asset": x} for x in SURVIVOR_ASSETS] +
        [{"sleeve": "rotating", "asset": x} for x in ROTATING_ASSETS]
    )
    membership.to_csv(ART_DIR / "sleeve_membership.csv", index=False)

    summary_rows = []
    detail_frames = []
    for sleeve_name, assets in [("survivor", SURVIVOR_ASSETS), ("rotating", ROTATING_ASSETS), ("combined", ALL_ASSETS)]:
        summary, detail = simulate_sleeve(load_close_matrix(assets), sleeve_name)
        summary_rows.append(summary)
        detail_frames.append(detail)
    summary_df = pd.DataFrame(summary_rows)
    detail_df = pd.concat(detail_frames, ignore_index=True)
    summary_df.to_csv(ART_DIR / "summary.csv", index=False)
    detail_df.to_csv(ART_DIR / "rebalance_detail.csv", index=False)

    by_sleeve = {row["sleeve"]: row for row in summary_rows}
    rotating = by_sleeve["rotating"]
    survivor = by_sleeve["survivor"]
    combined = by_sleeve["combined"]
    if rotating["mean_net_bps"] > 0 and rotating["t_stat_net"] > 1.0 and survivor["mean_net_bps"] <= 0 and combined["mean_net_bps"] <= rotating["mean_net_bps"]:
        verdict = "promote_P2"
        one_line = "同一套 8h/24h blended XS momentum + 1h rebalance + 10bps 往返成本下，净收益壳主要留在 rotating sleeve，而 survivor sleeve 不成立；这说明 universe-engineering 不是措辞差异，足以升 P2。"
    else:
        verdict = "background_P0"
        one_line = "同一套 8h/24h blended XS momentum + 1h rebalance + 10bps 往返成本下，rotating sleeve 没有留下明显强于 survivor/combined 的独立 after-cost 净收益壳；这更像 universe 叙事而不是可迁移 alpha，应在 survivor follow-up 用尽后回 background/P0。"
    decision = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "sample": f"{LOOKBACK} 15m perp cache",
        "signal": "8h/24h blended cross-sectional momentum",
        "rebalance": "1h",
        "cost_bps_roundtrip": COST_BPS_RT,
        "summary": by_sleeve,
        "verdict": verdict,
        "one_line": one_line,
    }
    (ART_DIR / "decision.json").write_text(json.dumps(decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(summary_df.to_string(index=False))
    print("\n=== decision ===")
    print(json.dumps(decision, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
