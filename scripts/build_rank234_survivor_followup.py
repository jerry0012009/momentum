#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "rank234_survivor_followup"
ART_DIR.mkdir(parents=True, exist_ok=True)

FUTURES_EXCHANGE_INFO = "https://fapi.binance.com/fapi/v1/exchangeInfo"
FUTURES_TICKER_24H = "https://fapi.binance.com/fapi/v1/ticker/24hr"
FUTURES_KLINES = "https://fapi.binance.com/fapi/v1/klines"

LOOKBACK_DAYS = 45
INTERVAL = "1h"
TOP_24H_PROBE = 50
UNIVERSE_SIZE = 24
MIN_LISTING_DAYS = 180
LONG_SHORT_FRAC = 0.20
COST_BPS_PER_SIDE = 5.0
REQUEST_SLEEP_SEC = 0.05
FORMATION_HOURS = [1, 24, 72]
HOLD_HOURS = [1, 4, 8]
STABLE_BASES = {"USDT", "USDC", "FDUSD", "BUSD", "USDP", "TUSD", "USDE", "USDS", "DAI"}


def fetch_json(base_url: str, params: dict[str, Any] | None = None, retries: int = 5) -> Any:
    url = base_url + ("?" + urllib.parse.urlencode(params) if params else "")
    headers = {
        "User-Agent": "Mozilla/5.0 OpenClaw-Rank234-Survivor/1.0",
        "Accept": "application/json,text/plain,*/*",
    }
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            if attempt < retries - 1:
                time.sleep(1.0 + attempt)
                continue
            raise
    raise RuntimeError(f"failed to fetch {url}: {last_err}")


def is_plain_alpha_base(base: str) -> bool:
    return bool(base) and base.isalpha() and base.upper() == base and base not in STABLE_BASES


def pick_universe() -> pd.DataFrame:
    exchange_info = fetch_json(FUTURES_EXCHANGE_INFO)
    tickers = {row.get("symbol", ""): row for row in fetch_json(FUTURES_TICKER_24H)}
    now_ms = int(time.time() * 1000)
    rows: list[dict[str, Any]] = []
    for row in exchange_info.get("symbols", []):
        symbol = str(row.get("symbol", ""))
        if row.get("status") != "TRADING":
            continue
        if row.get("contractType") != "PERPETUAL":
            continue
        if row.get("quoteAsset") != "USDT":
            continue
        if not symbol.endswith("USDT"):
            continue
        base = symbol[:-4]
        if not is_plain_alpha_base(base):
            continue
        onboard_ms = float(row.get("onboardDate") or 0.0)
        listing_days = (now_ms - onboard_ms) / 1000.0 / 86400.0 if onboard_ms else 0.0
        if listing_days < MIN_LISTING_DAYS:
            continue
        ticker = tickers.get(symbol, {})
        quote_volume = float(ticker.get("quoteVolume") or 0.0)
        rows.append({
            "symbol": symbol,
            "base": base,
            "listing_days": listing_days,
            "quote_volume_24h": quote_volume,
        })
    frame = pd.DataFrame(rows).sort_values("quote_volume_24h", ascending=False).head(TOP_24H_PROBE).reset_index(drop=True)
    return frame.head(UNIVERSE_SIZE).reset_index(drop=True)


def fetch_klines(symbol: str, days: int = LOOKBACK_DAYS) -> pd.DataFrame:
    end_ms = int(time.time() * 1000)
    start_ms = end_ms - days * 24 * 60 * 60 * 1000
    cur = start_ms
    rows: list[list[Any]] = []
    step_ms = 60 * 60 * 1000
    while cur < end_ms:
        batch = fetch_json(FUTURES_KLINES, {
            "symbol": symbol,
            "interval": INTERVAL,
            "startTime": cur,
            "endTime": end_ms,
            "limit": 1500,
        })
        if not batch:
            break
        rows.extend(batch)
        nxt = int(batch[-1][0]) + step_ms
        if nxt <= cur:
            break
        cur = nxt
        time.sleep(REQUEST_SLEEP_SEC)
    if not rows:
        raise RuntimeError(f"no klines for {symbol}")
    df = pd.DataFrame(rows, columns=[
        "open_time", "open", "high", "low", "close", "volume", "close_time",
        "quote_volume", "trade_count", "taker_base", "taker_quote", "ignore",
    ])
    for col in ["open", "high", "low", "close", "quote_volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["ts"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    return df[["ts", "open", "close", "quote_volume"]].drop_duplicates("ts").sort_values("ts").reset_index(drop=True)


def build_panel(universe: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    frames = []
    meta_rows = []
    for row in universe.to_dict(orient="records"):
        symbol = str(row["symbol"])
        bars = fetch_klines(symbol)
        bars["symbol"] = symbol
        frames.append(bars)
        meta_rows.append({**row, "bars": int(len(bars)), "start_ts": str(bars["ts"].min()), "end_ts": str(bars["ts"].max())})
    panel = pd.concat(frames, ignore_index=True)
    meta = pd.DataFrame(meta_rows)
    return panel, meta


def evaluate_strategy(panel: pd.DataFrame, score_kind: str, formation_h: int, hold_h: int) -> dict[str, Any]:
    work = panel.copy().sort_values(["symbol", "ts"]).reset_index(drop=True)
    work["ret_1h"] = work.groupby("symbol")["close"].pct_change()
    work["fwd_ret"] = work.groupby("symbol")["open"].shift(-(hold_h + 1)) / work.groupby("symbol")["open"].shift(-1) - 1.0
    if score_kind == "max_rank":
        work["score"] = work.groupby("symbol")["ret_1h"].rolling(formation_h, min_periods=formation_h).max().reset_index(level=0, drop=True)
    elif score_kind == "return_rank":
        work["score"] = work.groupby("symbol")["close"].pct_change(formation_h)
    else:
        raise ValueError(score_kind)

    rows = []
    timestamps = sorted(work["ts"].drop_duplicates())
    step = hold_h
    for idx in range(0, len(timestamps), step):
        ts = timestamps[idx]
        snap = work[work["ts"] == ts][["symbol", "score", "fwd_ret"]].dropna().copy()
        if len(snap) < 10:
            continue
        bucket = max(2, int(math.floor(len(snap) * LONG_SHORT_FRAC)))
        snap = snap.sort_values("score", ascending=False).reset_index(drop=True)
        longs = snap.head(bucket)
        shorts = snap.tail(bucket)
        gross = longs["fwd_ret"].mean() - shorts["fwd_ret"].mean()
        net = gross - 2.0 * (COST_BPS_PER_SIDE / 10000.0)
        rows.append({
            "ts": ts,
            "n_assets": int(len(snap)),
            "bucket": bucket,
            "long_mean": float(longs["fwd_ret"].mean()),
            "short_mean": float(shorts["fwd_ret"].mean()),
            "gross_spread": float(gross),
            "net_spread": float(net),
        })
    detail = pd.DataFrame(rows)
    if detail.empty:
        return {
            "strategy": score_kind,
            "formation_h": formation_h,
            "hold_h": hold_h,
            "rebalances": 0,
            "mean_gross_bps": np.nan,
            "mean_net_bps": np.nan,
            "total_net_bps": np.nan,
            "win_rate": np.nan,
            "t_stat_net": np.nan,
            "positive_after_cost": False,
        }
    x = detail["net_spread"].dropna()
    t_stat = float(x.mean() / (x.std(ddof=1) / math.sqrt(len(x)))) if len(x) >= 2 and x.std(ddof=1) > 0 else np.nan
    detail.to_csv(ART_DIR / f"detail_{score_kind}_{formation_h}h_{hold_h}h.csv", index=False)
    return {
        "strategy": score_kind,
        "formation_h": formation_h,
        "hold_h": hold_h,
        "rebalances": int(len(detail)),
        "mean_gross_bps": float(detail["gross_spread"].mean() * 10000.0),
        "mean_net_bps": float(detail["net_spread"].mean() * 10000.0),
        "total_net_bps": float(detail["net_spread"].sum() * 10000.0),
        "win_rate": float((detail["net_spread"] > 0).mean()),
        "t_stat_net": t_stat,
        "positive_after_cost": bool(detail["net_spread"].mean() > 0),
    }


def main() -> None:
    universe = pick_universe()
    panel, meta = build_panel(universe)
    universe.to_csv(ART_DIR / "selected_universe.csv", index=False)
    meta.to_csv(ART_DIR / "universe_fetch_meta.csv", index=False)
    panel.to_csv(ART_DIR / "panel_1h.csv", index=False)

    results = []
    for formation_h in FORMATION_HOURS:
        for hold_h in HOLD_HOURS:
            for score_kind in ["max_rank", "return_rank"]:
                results.append(evaluate_strategy(panel, score_kind, formation_h, hold_h))
    summary = pd.DataFrame(results).sort_values(["formation_h", "hold_h", "strategy"]).reset_index(drop=True)
    summary.to_csv(ART_DIR / "summary.csv", index=False)

    pivot = summary.pivot(index=["formation_h", "hold_h"], columns="strategy", values="mean_net_bps").reset_index()
    pivot["max_minus_return_rank_bps"] = pivot["max_rank"] - pivot["return_rank"]
    pivot["continuation_sign_positive"] = pivot["max_rank"] > 0
    pivot.to_csv(ART_DIR / "max_vs_return_rank.csv", index=False)

    long_form = summary[summary["formation_h"].isin([24, 72]) & (summary["strategy"] == "max_rank")].copy()
    short_form = summary[(summary["formation_h"] == 1) & (summary["strategy"] == "max_rank")].copy()
    long_positive = bool((long_form["mean_net_bps"] > 0).any())
    long_beats_return = bool((pivot[pivot["formation_h"].isin([24, 72])]["max_minus_return_rank_bps"] > 0).any())
    short_fade_like = bool((short_form["mean_net_bps"] < 0).any())

    best_long = long_form.sort_values(["mean_net_bps", "t_stat_net"], ascending=[False, False]).head(1)
    best_overall = summary.sort_values(["mean_net_bps", "t_stat_net"], ascending=[False, False]).head(1)

    decision: dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "lookback_days": LOOKBACK_DAYS,
        "interval": INTERVAL,
        "universe_size": int(len(universe)),
        "universe_symbols": universe["symbol"].tolist(),
        "cost_bps_per_side": COST_BPS_PER_SIDE,
        "formation_hours": FORMATION_HOURS,
        "hold_hours": HOLD_HOURS,
        "long_positive_any_24h_or_72h": long_positive,
        "long_beats_return_rank_any_24h_or_72h": long_beats_return,
        "short_1h_max_has_negative_any_hold": short_fade_like,
        "best_long_max_rank": [] if best_long.empty else best_long.to_dict(orient="records"),
        "best_overall": best_overall.to_dict(orient="records"),
    }
    if long_positive and long_beats_return:
        decision["verdict"] = "promote_P2"
        decision["one_line"] = "liquid perp 1h ladder 快检已出现至少一格 24h/72h MAX continuation 在成本后为正且胜过 plain return-rank，survivor 问题回答为肯定，足以升 P2。"
    else:
        decision["verdict"] = "keep_P1_then_background"
        decision["one_line"] = "liquid perp 1h ladder 快检没有证明 24h/72h MAX continuation 在成本后稳定成立，更没有显示它优于 plain return-rank；因此这条 longer-formation MAX 分支当前更像论文层假设，不够诚实地升 P2。"
    (ART_DIR / "decision.json").write_text(json.dumps(decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(decision, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
