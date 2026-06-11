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

import pandas as pd

ROOT = Path("/root/clawd/jerry/momentum")
CFG_PATH = ROOT / "config/execution/phase2a_event_v4_trail_paper.json"
LIVE_ART = ROOT / "reports/artifacts/paper_phase2a_event_v4_sl_only"
OUT = ROOT / "reports/artifacts/phase2a_may15_v4_parity_audit"

BASE_URL = "https://fapi.binance.com"
START = pd.Timestamp("2026-05-13T00:00:00Z")
END = pd.Timestamp("2026-05-16T03:00:00Z")
AUDIT_START = pd.Timestamp("2026-05-15T00:00:00Z")
AUDIT_END = pd.Timestamp("2026-05-16T02:00:00Z")


def request_json(path: str, params: dict[str, Any] | None = None, retries: int = 5) -> Any:
    url = BASE_URL + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    headers = {
        "User-Agent": "Mozilla/5.0 OpenClaw-Phase2a-May15-Audit/1.0",
        "Accept": "application/json,text/plain,*/*",
    }
    last: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            last = exc
            if attempt < retries - 1:
                time.sleep(0.4 * (attempt + 1))
                continue
            raise
    raise last or RuntimeError(url)


def ms(ts: pd.Timestamp) -> int:
    return int(ts.timestamp() * 1000)


def iso_z(ts: Any) -> str:
    if ts is None or pd.isna(ts):
        return ""
    return pd.to_datetime(ts, utc=True).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_symbols(cfg: dict[str, Any]) -> list[str]:
    stable_bases = set(cfg.get("stable_bases", []))
    raw = request_json("/fapi/v1/exchangeInfo")
    symbols: list[str] = []
    for row in raw.get("symbols", []):
        symbol = str(row.get("symbol") or "")
        base = str(row.get("baseAsset") or symbol.removesuffix("USDT"))
        if row.get("status") != "TRADING":
            continue
        if row.get("contractType") != "PERPETUAL":
            continue
        if row.get("quoteAsset") != "USDT":
            continue
        if not symbol.endswith("USDT"):
            continue
        if base in stable_bases:
            continue
        symbols.append(symbol)
    return sorted(set(symbols))


def fetch_klines(symbol: str) -> pd.DataFrame:
    raw = request_json(
        "/fapi/v1/klines",
        {
            "symbol": symbol,
            "interval": "1h",
            "startTime": ms(START),
            "endTime": ms(END),
            "limit": 1500,
        },
    )
    if not raw:
        return pd.DataFrame()
    df = pd.DataFrame(
        raw,
        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_volume",
            "number_of_trades",
            "taker_buy_base_volume",
            "taker_buy_quote_volume",
            "ignore",
        ],
    )
    out = pd.DataFrame(
        {
            "ts": pd.to_datetime(pd.to_numeric(df["open_time"], errors="coerce"), unit="ms", utc=True),
            "symbol": symbol,
            "open": pd.to_numeric(df["open"], errors="coerce"),
            "high": pd.to_numeric(df["high"], errors="coerce"),
            "low": pd.to_numeric(df["low"], errors="coerce"),
            "close": pd.to_numeric(df["close"], errors="coerce"),
            "quote_volume": pd.to_numeric(df["quote_volume"], errors="coerce"),
        }
    )
    return out.dropna(subset=["ts", "open", "close", "quote_volume"]).sort_values("ts")


def add_features(g: pd.DataFrame) -> pd.DataFrame:
    g = g.sort_values("ts").copy()
    # Historical research definition from v1.6a artifacts.
    g["hist_ret_1h"] = g["close"].pct_change()
    g["hist_vol_ma20_incl"] = g["quote_volume"].rolling(20, min_periods=10).mean()
    g["hist_vol_ratio_incl"] = g["quote_volume"] / g["hist_vol_ma20_incl"]
    g["hist_v4"] = (g["hist_vol_ratio_incl"] >= 3.0) & (g["hist_ret_1h"] >= 0.01)

    # Current forward runner definition.
    g["runner_ret_1h"] = g["close"] / g["open"] - 1.0
    g["runner_vol_ma20_prev"] = g["quote_volume"].shift(1).rolling(20, min_periods=20).mean()
    g["runner_vol_ratio_prev"] = g["quote_volume"] / g["runner_vol_ma20_prev"]
    g["runner_v4"] = (g["runner_vol_ratio_prev"] > 3.0) & (g["runner_ret_1h"] > 0.01)

    # Historical event overlay definition.
    g["event_ret24_c2c"] = g["close"].pct_change(24)
    g["event_vol24_sum"] = g["quote_volume"].rolling(24, min_periods=12).sum()
    return g


def cooldown_first_signals(sig: pd.DataFrame, col: str) -> pd.DataFrame:
    rows = []
    for sym, g in sig[sig[col]].sort_values(["symbol", "ts"]).groupby("symbol", sort=False):
        last_i = -10**9
        local = g.reset_index(drop=False)
        for i, r in local.iterrows():
            if i - last_i >= 4:
                rows.append(r["index"])
                last_i = i
    if not rows:
        return sig.iloc[[]].copy()
    return sig.loc[rows].sort_values(["symbol", "ts"]).copy()


def dedup_events(raw: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for sym, g in raw.sort_values(["symbol", "ts"]).groupby("symbol", sort=False):
        last = pd.Timestamp("1970-01-01", tz="UTC")
        for r in g.itertuples(index=False):
            if (r.ts - last).total_seconds() / 3600.0 < 24:
                continue
            rows.append(
                {
                    "symbol": sym,
                    "event_ts": r.ts,
                    "event_ret24": float(r.event_ret24_c2c),
                    "event_rank": int(r.event_rank),
                    "event_vol24": float(r.event_vol24_sum),
                    "xsec_symbols": int(r.xsec_symbols),
                }
            )
            last = r.ts
    return pd.DataFrame(rows)


def first_signal_after_event(events: pd.DataFrame, signals: pd.DataFrame, *, include_event_ts: bool) -> pd.DataFrame:
    if events.empty or signals.empty:
        return pd.DataFrame()
    rows = []
    sig_by_symbol = {sym: g.sort_values("ts") for sym, g in signals.groupby("symbol", sort=False)}
    for ev in events.sort_values(["event_ts", "symbol"]).itertuples(index=False):
        sg = sig_by_symbol.get(ev.symbol)
        if sg is None or sg.empty:
            continue
        lo_ok = sg["ts"] >= ev.event_ts if include_event_ts else sg["ts"] > ev.event_ts
        hi_ok = sg["ts"] <= ev.event_ts + pd.Timedelta(hours=48)
        m = sg[lo_ok & hi_ok]
        if m.empty:
            continue
        s = m.iloc[0]
        rows.append(
            {
                "symbol": ev.symbol,
                "event_ts": iso_z(ev.event_ts),
                "signal_ts": iso_z(s["ts"]),
                "lag_hours": (s["ts"] - ev.event_ts).total_seconds() / 3600.0,
                "event_rank": ev.event_rank,
                "event_ret24": ev.event_ret24,
                "event_vol24": ev.event_vol24,
                "hist_ret_1h": s.get("hist_ret_1h"),
                "hist_vol_ratio_incl": s.get("hist_vol_ratio_incl"),
                "runner_ret_1h": s.get("runner_ret_1h"),
                "runner_vol_ratio_prev": s.get("runner_vol_ratio_prev"),
            }
        )
    return pd.DataFrame(rows)


def live_event_v4_compare(features: pd.DataFrame) -> pd.DataFrame:
    event_log = pd.read_csv(LIVE_ART / "event_log.csv")
    event_log = event_log[event_log["accepted"].astype(bool)].copy()
    if event_log.empty:
        return pd.DataFrame()
    event_log["event_ts"] = pd.to_datetime(event_log["event_ts_utc"], utc=True)
    rows = []
    for ev in event_log.itertuples(index=False):
        g = features[(features["symbol"] == ev.symbol) & (features["ts"] >= ev.event_ts) & (features["ts"] <= ev.event_ts + pd.Timedelta(hours=48))]
        if g.empty:
            rows.append({"symbol": ev.symbol, "event_ts": iso_z(ev.event_ts), "hist_first_v4_ts": "", "runner_first_v4_ts": ""})
            continue
        hist = g[g["hist_v4"]]
        runner = g[g["runner_v4"]]
        best_hist = hist.iloc[0] if not hist.empty else None
        best_runner = runner.iloc[0] if not runner.empty else None
        max_hist = g.sort_values("hist_vol_ratio_incl", ascending=False).iloc[0]
        max_runner = g.sort_values("runner_vol_ratio_prev", ascending=False).iloc[0]
        rows.append(
            {
                "symbol": ev.symbol,
                "event_ts": iso_z(ev.event_ts),
                "live_event_rank": getattr(ev, "event_rank"),
                "live_event_ret24": getattr(ev, "event_ret24"),
                "hist_first_v4_ts": iso_z(best_hist["ts"]) if best_hist is not None else "",
                "hist_first_v4_ret_1h": best_hist["hist_ret_1h"] if best_hist is not None else math.nan,
                "hist_first_v4_vol_ratio": best_hist["hist_vol_ratio_incl"] if best_hist is not None else math.nan,
                "runner_first_v4_ts": iso_z(best_runner["ts"]) if best_runner is not None else "",
                "runner_first_v4_ret_1h": best_runner["runner_ret_1h"] if best_runner is not None else math.nan,
                "runner_first_v4_vol_ratio": best_runner["runner_vol_ratio_prev"] if best_runner is not None else math.nan,
                "hist_max_vol_ratio": max_hist["hist_vol_ratio_incl"],
                "hist_max_vol_ts": iso_z(max_hist["ts"]),
                "runner_max_vol_ratio": max_runner["runner_vol_ratio_prev"],
                "runner_max_vol_ts": iso_z(max_runner["ts"]),
                "hist_max_ret_1h": g["hist_ret_1h"].max(),
                "runner_max_ret_1h": g["runner_ret_1h"].max(),
            }
        )
    return pd.DataFrame(rows)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    cfg = json.loads(CFG_PATH.read_text(encoding="utf-8"))
    symbols = load_symbols(cfg)
    frames = []
    failures = []
    for i, symbol in enumerate(symbols, 1):
        try:
            df = fetch_klines(symbol)
            if not df.empty:
                frames.append(df)
        except Exception as exc:
            failures.append({"symbol": symbol, "error": repr(exc)})
        if i % 50 == 0:
            print(f"fetched {i}/{len(symbols)} symbols, frames={len(frames)}, failures={len(failures)}", flush=True)
            time.sleep(0.2)
    panel = pd.concat(frames, ignore_index=True)
    features = pd.concat([add_features(g) for _, g in panel.groupby("symbol", sort=False)], ignore_index=True)
    features.to_csv(OUT / "may15_1h_features.csv", index=False)

    audit_features = features[(features["ts"] >= AUDIT_START) & (features["ts"] <= AUDIT_END)].copy()
    xsec = audit_features.groupby("ts")["symbol"].transform("count")
    audit_features["xsec_symbols"] = xsec.astype(int)
    audit_features["event_rank"] = audit_features.groupby("ts")["event_ret24_c2c"].rank(method="first", ascending=False)
    event_raw = audit_features[
        (audit_features["xsec_symbols"] >= 100)
        & (audit_features["event_rank"] <= 20)
        & (audit_features["event_ret24_c2c"] >= 0.30)
        & (audit_features["event_vol24_sum"] >= 5_000_000.0)
    ].copy()
    events = dedup_events(event_raw)

    hist_signals_all = cooldown_first_signals(features, "hist_v4")
    runner_signals_all = features[features["runner_v4"]].copy()
    hist_signals = first_signal_after_event(events, hist_signals_all, include_event_ts=False)
    runner_signals = first_signal_after_event(events, runner_signals_all, include_event_ts=False)
    live_cmp = live_event_v4_compare(features)

    event_raw.to_csv(OUT / "kline_event_raw_hours.csv", index=False)
    events.to_csv(OUT / "kline_events_rank20_ret30_vol5m.csv", index=False)
    hist_signals.to_csv(OUT / "kline_events_hist_v4_first_signals.csv", index=False)
    runner_signals.to_csv(OUT / "kline_events_runner_v4_first_signals.csv", index=False)
    live_cmp.to_csv(OUT / "live_accepted_events_v4_compare.csv", index=False)
    pd.DataFrame(failures).to_csv(OUT / "fetch_failures.csv", index=False)

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "symbols_requested": len(symbols),
        "symbols_fetched": int(panel["symbol"].nunique()),
        "fetch_failures": len(failures),
        "feature_time_min": iso_z(features["ts"].min()),
        "feature_time_max": iso_z(features["ts"].max()),
        "audit_start": iso_z(AUDIT_START),
        "audit_end": iso_z(AUDIT_END),
        "kline_event_raw_hours": int(len(event_raw)),
        "kline_events_after_24h_cooldown": int(len(events)),
        "kline_events_hist_v4_first_signals": int(len(hist_signals)),
        "kline_events_runner_v4_first_signals": int(len(runner_signals)),
        "live_accepted_events": int(len(live_cmp)),
        "live_accepted_events_hist_v4_signals": int(live_cmp["hist_first_v4_ts"].astype(str).ne("").sum()) if not live_cmp.empty else 0,
        "live_accepted_events_runner_v4_signals": int(live_cmp["runner_first_v4_ts"].astype(str).ne("").sum()) if not live_cmp.empty else 0,
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
