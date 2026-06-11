#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_rank32b_slope_floor_continuation_15m" / "perp_cache"
ART_DIR = ROOT / "reports" / "artifacts" / "rank289_survivor_followup"
ART_DIR.mkdir(parents=True, exist_ok=True)

ASSETS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
VARIANTS = ["shock_only", "shock_ema", "shock_ema_volume", "shock_ema_volume_displacement"]
COSTS_BPS_RT = [10.0, 20.0, 30.0]
ROC_BARS = 24
ROC_STD_BARS = 96
EMA_LEN = 48
VOL_MA_LEN = 48
RET_STD_LEN = 48
SHOCK_K = 1.5
DISP_K = 1.0
HOLD_BARS = 8


def load_bars(symbol: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m__perp.csv"
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    for col in ["open", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df[["timestamp", "open", "close", "volume"]].dropna().sort_values("timestamp").reset_index(drop=True)


def prep(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ret_1"] = out["close"].pct_change()
    out["roc"] = out["close"].pct_change(ROC_BARS)
    out["roc_std"] = out["roc"].rolling(ROC_STD_BARS).std()
    out["ema"] = out["close"].ewm(span=EMA_LEN, adjust=False).mean()
    out["vol_ma"] = out["volume"].rolling(VOL_MA_LEN).mean()
    out["ret_std"] = out["ret_1"].rolling(RET_STD_LEN).std()
    out["disp"] = (out["close"] / out["ema"] - 1.0).abs()
    out["disp_thresh"] = DISP_K * out["ret_std"] * math.sqrt(EMA_LEN)
    out["side"] = 0
    out.loc[out["roc"] > SHOCK_K * out["roc_std"], "side"] = 1
    out.loc[out["roc"] < -SHOCK_K * out["roc_std"], "side"] = -1
    out["ema_ok"] = ((out["side"] == 1) & (out["close"] > out["ema"])) | ((out["side"] == -1) & (out["close"] < out["ema"]))
    out["vol_ok"] = out["volume"] > out["vol_ma"]
    out["disp_ok"] = out["disp"] > out["disp_thresh"]
    out["entry_open"] = out["open"].shift(-1)
    out["exit_close"] = out["close"].shift(-(HOLD_BARS + 1))
    return out


def simulate_variant(df: pd.DataFrame, variant: str, cost_bps_rt: float) -> dict:
    sig = df[df["side"] != 0].copy()
    if variant in {"shock_ema", "shock_ema_volume", "shock_ema_volume_displacement"}:
        sig = sig[sig["ema_ok"]]
    if variant in {"shock_ema_volume", "shock_ema_volume_displacement"}:
        sig = sig[sig["vol_ok"]]
    if variant == "shock_ema_volume_displacement":
        sig = sig[sig["disp_ok"]]
    sig = sig.dropna(subset=["entry_open", "exit_close"]).copy()
    if sig.empty:
        return {"trades": 0, "mean_gross_bps": np.nan, "mean_net_bps": np.nan, "total_net_return": np.nan, "win_rate": np.nan, "t_stat_net": np.nan}
    sig["gross_ret"] = np.where(sig["side"] == 1, sig["exit_close"] / sig["entry_open"] - 1.0, sig["entry_open"] / sig["exit_close"] - 1.0)
    sig["net_ret"] = sig["gross_ret"] - cost_bps_rt / 10000.0
    # thin overlap by only keeping every HOLD_BARS-th signal after a trade starts
    kept = []
    last_entry_idx = -10**9
    for idx in sig.index:
        if idx <= last_entry_idx + HOLD_BARS:
            continue
        kept.append(idx)
        last_entry_idx = idx + 1
    sig = sig.loc[kept].copy()
    x = sig["net_ret"]
    t_stat = float(x.mean() / (x.std(ddof=1) / math.sqrt(len(x)))) if len(x) >= 2 and x.std(ddof=1) > 0 else np.nan
    return {
        "trades": int(len(sig)),
        "mean_gross_bps": float(sig["gross_ret"].mean() * 10000.0),
        "mean_net_bps": float(sig["net_ret"].mean() * 10000.0),
        "total_net_return": float((1.0 + sig["net_ret"]).prod() - 1.0),
        "win_rate": float((sig["net_ret"] > 0).mean()),
        "t_stat_net": t_stat,
    }


def main() -> None:
    rows = []
    for symbol in ASSETS:
        df = prep(load_bars(symbol))
        for variant in VARIANTS:
            for cost in COSTS_BPS_RT:
                rows.append({"symbol": symbol, "variant": variant, "cost_bps_rt": cost, **simulate_variant(df, variant, cost)})
    summary = pd.DataFrame(rows)
    summary.to_csv(ART_DIR / "summary_by_asset_variant_cost.csv", index=False)

    aggregate = (
        summary.groupby(["variant", "cost_bps_rt"], as_index=False)
        .agg(
            assets=("symbol", "nunique"),
            positive_assets=("total_net_return", lambda s: int((s > 0).sum())),
            mean_net_bps=("mean_net_bps", "mean"),
            min_net_bps=("mean_net_bps", "min"),
            mean_total_return=("total_net_return", "mean"),
            min_total_return=("total_net_return", "min"),
            mean_win_rate=("win_rate", "mean"),
            min_trades=("trades", "min"),
        )
        .sort_values(["cost_bps_rt", "mean_net_bps"], ascending=[True, False])
        .reset_index(drop=True)
    )
    aggregate["positive_asset_ratio"] = aggregate["positive_assets"] / aggregate["assets"]
    aggregate.to_csv(ART_DIR / "aggregate_variant_cost.csv", index=False)

    decision = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "verdict": "background_P0",
        "one_line": "去优化 15m clean-room baseline 下，这条 vol-normalized shock continuation 的 8-bar hold proxy 在 BTC/ETH/SOL 与 10/20/30bps 成本梯度上没有留下可迁移的 after-cost pocket；survivor follow-up 用尽后应回 background/P0。",
        "params": {
            "sample": "120d 15m perp cache",
            "roc_bars": ROC_BARS,
            "roc_std_bars": ROC_STD_BARS,
            "ema_len": EMA_LEN,
            "vol_ma_len": VOL_MA_LEN,
            "shock_k": SHOCK_K,
            "disp_k": DISP_K,
            "hold_bars": HOLD_BARS,
        },
    }
    primary = aggregate[(aggregate["variant"] == "shock_ema_volume_displacement") & (aggregate["cost_bps_rt"] == 20.0)]
    if not primary.empty:
        row = primary.iloc[0]
        if float(row["mean_net_bps"]) > 0 and float(row["positive_asset_ratio"]) >= 2 / 3:
            decision["verdict"] = "promote_P2"
            decision["one_line"] = "去优化 15m clean-room baseline 下，full admission variant 在 20bps 往返成本仍保留跨 BTC/ETH/SOL 的正向 after-cost pocket，survivor follow-up 回答为肯定，足以升 P2。"
    (ART_DIR / "decision.json").write_text(json.dumps(decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(summary.to_string(index=False))
    print("\n=== aggregate ===")
    print(aggregate.to_string(index=False))
    print("\n=== decision ===")
    print(json.dumps(decision, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
