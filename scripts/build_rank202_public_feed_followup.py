#!/usr/bin/env python3
import io
import json
import math
import zipfile
from pathlib import Path
from urllib.request import urlopen

import numpy as np
import pandas as pd

BASE = "https://data.binance.vision/data/futures/um/daily"
SYMBOL = "BTCUSDT"
DATE = "2024-01-15"
OUTDIR = Path("/root/clawd/jerry/momentum/reports/artifacts/rank202_public_feed_followup_20260327")
OUTDIR.mkdir(parents=True, exist_ok=True)


def read_zip_csv(url: str) -> pd.DataFrame:
    with urlopen(url, timeout=60) as resp:
        raw = resp.read()
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        name = zf.namelist()[0]
        with zf.open(name) as fh:
            return pd.read_csv(fh)


def load_bookticker() -> pd.DataFrame:
    url = f"{BASE}/bookTicker/{SYMBOL}/{SYMBOL}-bookTicker-{DATE}.zip"
    df = read_zip_csv(url)
    df.columns = [c.strip() for c in df.columns]
    if "transaction_time" in df.columns:
        ts_col = "transaction_time"
    elif "T" in df.columns:
        ts_col = "T"
    else:
        ts_col = df.columns[0]
    rename = {}
    for c in df.columns:
        cl = c.lower()
        if cl in {"bid_price", "best_bid_price", "b"}:
            rename[c] = "bid_price"
        elif cl in {"ask_price", "best_ask_price", "a"}:
            rename[c] = "ask_price"
        elif cl in {"bid_qty", "best_bid_qty", "b_qty", "bq", "bidsize"}:
            rename[c] = "bid_qty"
        elif cl in {"ask_qty", "best_ask_qty", "a_qty", "aq", "asksize"}:
            rename[c] = "ask_qty"
    df = df.rename(columns=rename)
    need = [ts_col, "bid_price", "ask_price", "bid_qty", "ask_qty"]
    df = df[need].copy()
    df[ts_col] = pd.to_numeric(df[ts_col], errors="coerce")
    for c in ["bid_price", "ask_price", "bid_qty", "ask_qty"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna().sort_values(ts_col)
    df["ts"] = pd.to_datetime(df[ts_col], unit="ms", utc=True)
    df["mid"] = (df["bid_price"] + df["ask_price"]) / 2.0
    df["spread_bps"] = (df["ask_price"] - df["bid_price"]) / df["mid"] * 1e4
    df["microprice"] = (
        df["ask_price"] * df["bid_qty"] + df["bid_price"] * df["ask_qty"]
    ) / (df["bid_qty"] + df["ask_qty"]).replace(0, np.nan)
    df["depth_imbalance"] = (
        (df["bid_qty"] - df["ask_qty"]) / (df["bid_qty"] + df["ask_qty"]).replace(0, np.nan)
    )
    sec = (
        df.set_index("ts")
        .resample("1s")
        .last()[["bid_price", "ask_price", "mid", "spread_bps", "microprice", "depth_imbalance"]]
        .ffill()
        .dropna()
        .reset_index()
    )
    sec["microprice_dev_bps"] = (sec["microprice"] - sec["mid"]) / sec["mid"] * 1e4
    return sec


def load_aggtrades() -> pd.DataFrame:
    url = f"{BASE}/aggTrades/{SYMBOL}/{SYMBOL}-aggTrades-{DATE}.zip"
    df = read_zip_csv(url)
    df.columns = [c.strip() for c in df.columns]
    rename = {}
    for c in df.columns:
        cl = c.lower()
        if cl in {"price", "p"}:
            rename[c] = "price"
        elif cl in {"quantity", "q"}:
            rename[c] = "qty"
        elif cl in {"transact_time", "t", "timestamp"}:
            rename[c] = "ts_ms"
        elif cl in {"is_buyer_maker", "m"}:
            rename[c] = "is_buyer_maker"
    df = df.rename(columns=rename)
    if "ts_ms" not in df.columns:
        # Data Vision aggTrades usually: agg_trade_id, price, quantity, first_trade_id, last_trade_id, transact_time, is_buyer_maker
        for c in df.columns:
            if "time" in c.lower():
                df = df.rename(columns={c: "ts_ms"})
                break
    need = ["price", "qty", "ts_ms", "is_buyer_maker"]
    df = df[need].copy()
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["qty"] = pd.to_numeric(df["qty"], errors="coerce")
    df["ts_ms"] = pd.to_numeric(df["ts_ms"], errors="coerce")
    df["is_buyer_maker"] = df["is_buyer_maker"].astype(str).str.lower().map({"true": True, "false": False})
    df = df.dropna().sort_values("ts_ms")
    df["ts"] = pd.to_datetime(df["ts_ms"], unit="ms", utc=True)
    df["signed_notional"] = np.where(df["is_buyer_maker"], -1.0, 1.0) * df["price"] * df["qty"]
    df["notional"] = df["price"] * df["qty"]
    sec = (
        df.set_index("ts")
        .resample("1s")
        .agg(
            signed_notional=("signed_notional", "sum"),
            total_notional=("notional", "sum"),
            trade_count=("price", "size"),
        )
        .fillna(0.0)
        .reset_index()
    )
    sec["flow_imbalance"] = sec["signed_notional"] / sec["total_notional"].replace(0, np.nan)
    sec["trade_count_z"] = (
        (sec["trade_count"] - sec["trade_count"].rolling(300, min_periods=30).mean())
        / sec["trade_count"].rolling(300, min_periods=30).std().replace(0, np.nan)
    )
    return sec


def build_frame() -> pd.DataFrame:
    bt = load_bookticker()
    tr = load_aggtrades()
    df = bt.merge(tr, on="ts", how="inner")
    df["ret_1s_bps"] = df["mid"].pct_change().fillna(0.0) * 1e4
    for col in ["microprice_dev_bps", "depth_imbalance", "flow_imbalance", "trade_count_z", "ret_1s_bps", "spread_bps"]:
        df[f"{col}_z60"] = (
            (df[col] - df[col].rolling(60, min_periods=20).mean())
            / df[col].rolling(60, min_periods=20).std().replace(0, np.nan)
        )
    df["signal_raw"] = (
        0.30 * df["microprice_dev_bps_z60"].fillna(0)
        + 0.30 * df["depth_imbalance_z60"].fillna(0)
        + 0.25 * df["flow_imbalance_z60"].fillna(0)
        + 0.10 * df["trade_count_z_z60"].fillna(0)
        - 0.05 * df["spread_bps_z60"].fillna(0)
    )
    return df.dropna().reset_index(drop=True)


def fit_and_eval(df: pd.DataFrame) -> pd.DataFrame:
    split = len(df) // 2
    train = df.iloc[:split].copy()
    test = df.iloc[split:].copy()
    features = [
        "microprice_dev_bps_z60",
        "depth_imbalance_z60",
        "flow_imbalance_z60",
        "trade_count_z_z60",
        "ret_1s_bps_z60",
        "spread_bps_z60",
    ]
    results = []
    preds_out = []
    for horizon in [180, 300, 900]:
        df[f"fwd_{horizon}_bps"] = (df["mid"].shift(-horizon) / df["mid"] - 1.0) * 1e4
        train_y = df.loc[train.index, f"fwd_{horizon}_bps"].dropna()
        train_x = train.loc[train_y.index, features].fillna(0.0)
        X = train_x.to_numpy()
        y = train_y.to_numpy()
        beta = np.linalg.lstsq(np.c_[np.ones(len(X)), X], y, rcond=None)[0]
        test_valid = test.index[test.index + horizon < len(df)]
        Xtest = df.loc[test_valid, features].fillna(0.0).to_numpy()
        pred = np.c_[np.ones(len(Xtest)), Xtest] @ beta
        actual = df.loc[test_valid, f"fwd_{horizon}_bps"].to_numpy()
        base = pd.DataFrame({
            "ts": df.loc[test_valid, "ts"].to_numpy(),
            "horizon_s": horizon,
            "pred_bps": pred,
            "actual_bps": actual,
        })
        preds_out.append(base)
        q_hi = np.quantile(pred, 0.90)
        q_lo = np.quantile(pred, 0.10)
        for side_name, mask, signed_actual in [
            ("long", pred >= q_hi, actual),
            ("short", pred <= q_lo, -actual),
            ("combined", (pred >= q_hi) | (pred <= q_lo), np.where(pred >= q_hi, actual, -actual)),
        ]:
            chosen = signed_actual[mask]
            pred_chosen = pred[mask]
            if len(chosen) == 0:
                continue
            gross = float(np.mean(chosen))
            corr = float(np.corrcoef(pred_chosen, chosen)[0, 1]) if len(chosen) > 2 else math.nan
            row = {
                "symbol": SYMBOL,
                "date": DATE,
                "horizon_s": horizon,
                "side": side_name,
                "events": int(mask.sum()),
                "gross_avg_bps_event": gross,
                "score_corr_signed_ret": corr,
                "q_long": float(q_hi),
                "q_short": float(q_lo),
            }
            for cost in [2, 4, 8, 12, 20]:
                row[f"net_{cost}bps_rt"] = gross - cost
            results.append(row)
    preds = pd.concat(preds_out, ignore_index=True)
    preds.to_csv(OUTDIR / "predictions.csv", index=False)
    return pd.DataFrame(results)


def main() -> None:
    frame = build_frame()
    frame.to_csv(OUTDIR / "feature_frame_1s.csv", index=False)
    summary = fit_and_eval(frame)
    summary.to_csv(OUTDIR / "summary.csv", index=False)
    best = []
    for side in ["long", "short", "combined"]:
        ss = summary[summary["side"] == side].copy()
        if len(ss):
            best.append(ss.sort_values("net_4bps_rt", ascending=False).head(1))
    if best:
        pd.concat(best, ignore_index=True).to_csv(OUTDIR / "best_by_side.csv", index=False)
    meta = {
        "symbol": SYMBOL,
        "date": DATE,
        "bookticker_url": f"{BASE}/bookTicker/{SYMBOL}/{SYMBOL}-bookTicker-{DATE}.zip",
        "aggtrades_url": f"{BASE}/aggTrades/{SYMBOL}/{SYMBOL}-aggTrades-{DATE}.zip",
        "rows_1s": int(len(frame)),
    }
    (OUTDIR / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
