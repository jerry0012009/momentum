#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank213_largecap_xs_jump_veto"
MONTHLY_UNIVERSE_PATH = ART_DIR / "rank213_monthly_volume_universe_rebuild_monthly_universe.csv"
CANDIDATE_PATH = ART_DIR / "rank213_monthly_volume_universe_rebuild_candidates.csv"
REBUILD_MODULE_PATH = ROOT / "scripts" / "build_rank213_monthly_volume_universe_rebuild.py"

STRATEGY_ID = "rank213_age90_14d_skip1d_voladj_top50_4x4"
SCORE_KIND = "age90_14d_skip1d_voladj"
TOP_N = 4
BOTTOM_N = 4
AGE_DAYS = 90
TARGET_UNIVERSE_SIZE = 50
BINANCE_FAPI_KLINES = "https://fapi.binance.com/fapi/v1/klines"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load module: {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def iso_z(ts: Any) -> str:
    return pd.to_datetime(ts, utc=True).strftime("%Y-%m-%dT%H:%M:%SZ")


def month_key(ts: pd.Timestamp) -> str:
    return pd.to_datetime(ts, utc=True).strftime("%Y-%m")


def stable_hash(payload: dict[str, Any]) -> str:
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_monthly_universe() -> pd.DataFrame:
    if not MONTHLY_UNIVERSE_PATH.exists():
        return pd.DataFrame()
    return pd.read_csv(MONTHLY_UNIVERSE_PATH)


def load_candidates() -> pd.DataFrame:
    if not CANDIDATE_PATH.exists():
        raise RuntimeError(f"missing candidates file: {CANDIDATE_PATH}")
    out = pd.read_csv(CANDIDATE_PATH)
    out["onboard_utc"] = pd.to_datetime(out["onboard_utc"], utc=True, format="mixed")
    out["onboard_ms"] = pd.to_numeric(out["onboard_ms"], errors="coerce")
    return out.dropna(subset=["symbol", "onboard_utc"])


def selected_symbols_from_row(row: pd.Series) -> list[str]:
    return [x for x in str(row.get("selected_symbols") or "").split(",") if x]


def compute_prev_month_volume_universe(decision_ts: pd.Timestamp, *, allow_download: bool = True) -> tuple[list[str], dict[str, Any]]:
    mod = load_module(REBUILD_MODULE_PATH, "rank213_age90_mv_rebuild_mod")
    candidates = load_candidates()
    current_month_start = pd.Timestamp(decision_ts.year, decision_ts.month, 1, tz="UTC")
    prev_month_start = current_month_start - pd.offsets.MonthBegin(1)
    prev_month_end = current_month_start - pd.Timedelta(days=1)
    prev_ym = prev_month_start.strftime("%Y-%m")
    rows: list[tuple[str, float]] = []
    missing: list[str] = []

    def load_prev_month_qv(symbol: str, onboard: pd.Timestamp) -> tuple[str, float | None, str]:
        if onboard >= current_month_start:
            return symbol, None, "not_onboarded"
        monthly_zip = mod.CACHE_DIR / "raw_1d" / "monthly" / symbol / f"{symbol}-1d-{prev_ym}.zip"
        try:
            if monthly_zip.exists():
                daily = mod.read_kline_zip(monthly_zip)
            elif allow_download:
                ok = mod.safe_download(mod.DATA_VISION_MONTHLY_KLINES_1D.format(symbol=symbol, ym=prev_ym), monthly_zip)
                daily = mod.read_kline_zip(monthly_zip) if ok else pd.DataFrame()
            else:
                cache_path = ART_DIR / "rank213_local_cache" / "monthly_volume_universe" / "daily_1d" / f"{symbol}.csv"
                if not cache_path.exists():
                    return symbol, None, "missing_cache"
                daily = pd.read_csv(cache_path)
                daily["timestamp"] = pd.to_datetime(daily["timestamp"], utc=True, errors="coerce")
        except Exception:
            return symbol, None, "load_error"
        if daily.empty or "quote_volume" not in daily.columns:
            return symbol, None, "empty_or_no_quote_volume"
        daily["timestamp"] = pd.to_datetime(daily["timestamp"], utc=True, errors="coerce")
        sub = daily[(daily["timestamp"] >= prev_month_start) & (daily["timestamp"] < current_month_start)].copy()
        qv = pd.to_numeric(sub.get("quote_volume"), errors="coerce").fillna(0.0)
        qv_sum = float(qv.sum())
        if not np.isfinite(qv_sum) or qv_sum <= 0:
            return symbol, None, "zero_quote_volume"
        return symbol, qv_sum, "ok"

    tasks = [
        (str(cand["symbol"]).upper(), pd.to_datetime(cand["onboard_utc"], utc=True))
        for _, cand in candidates.iterrows()
    ]
    with ThreadPoolExecutor(max_workers=16) as ex:
        futs = [ex.submit(load_prev_month_qv, symbol, onboard) for symbol, onboard in tasks]
        for fut in as_completed(futs):
            symbol, qv_sum, status = fut.result()
            if status == "ok" and qv_sum is not None:
                rows.append((symbol, float(qv_sum)))
            elif status != "not_onboarded":
                missing.append(symbol)

    rows.sort(key=lambda x: x[1], reverse=True)
    selected = [sym for sym, _ in rows[:TARGET_UNIVERSE_SIZE]]
    meta = {
        "source": "computed_prev_full_month_quote_volume",
        "month": month_key(decision_ts),
        "prev_month_start_utc": iso_z(prev_month_start),
        "prev_month_end_utc": iso_z(prev_month_end),
        "candidate_count": int(len(candidates)),
        "volume_rows": int(len(rows)),
        "missing_count": int(len(missing)),
        "missing_sample": missing[:20],
        "top_quote_volume": [{"symbol": sym, "quote_volume": qv} for sym, qv in rows[:TARGET_UNIVERSE_SIZE]],
    }
    return selected, meta


def get_universe(decision_ts: pd.Timestamp, *, allow_download: bool = True) -> tuple[list[str], dict[str, Any]]:
    month = month_key(decision_ts)
    monthly = load_monthly_universe()
    if not monthly.empty and "month" in monthly.columns:
        hit = monthly[monthly["month"].astype(str) == month]
        if not hit.empty:
            selected = selected_symbols_from_row(hit.iloc[-1])
            if len(selected) >= TARGET_UNIVERSE_SIZE:
                return selected[:TARGET_UNIVERSE_SIZE], {
                    "source": "monthly_universe_csv",
                    "month": month,
                    "path": str(MONTHLY_UNIVERSE_PATH.relative_to(ROOT)),
                    "selected_count": len(selected[:TARGET_UNIVERSE_SIZE]),
                    "target_universe_size": TARGET_UNIVERSE_SIZE,
                }
            computed, meta = compute_prev_month_volume_universe(decision_ts, allow_download=allow_download)
            meta.update({
                "csv_path": str(MONTHLY_UNIVERSE_PATH.relative_to(ROOT)),
                "csv_selected_count": len(selected),
                "csv_insufficient_for_target": True,
                "target_universe_size": TARGET_UNIVERSE_SIZE,
            })
            return computed, meta
    return compute_prev_month_volume_universe(decision_ts, allow_download=allow_download)


def fetch_recent_daily_klines(symbol: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    start = pd.to_datetime(start, utc=True).floor("1D")
    end = pd.to_datetime(end, utc=True).floor("1D")
    params = {
        "symbol": symbol.upper(),
        "interval": "1d",
        "startTime": str(int(start.timestamp() * 1000)),
        "endTime": str(int((end + pd.Timedelta(hours=23, minutes=59)).timestamp() * 1000)),
        "limit": "1000",
    }
    url = f"{BINANCE_FAPI_KLINES}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "rank213-age90-live-signal/1.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        raw = json.loads(resp.read().decode("utf-8"))
    rows = []
    for k in raw if isinstance(raw, list) else []:
        if not isinstance(k, list) or len(k) < 8:
            continue
        rows.append({
            "timestamp": pd.to_datetime(int(k[0]), unit="ms", utc=True),
            "close": float(k[4]),
            "volume": float(k[5]),
            "quote_volume": float(k[7]),
        })
    if not rows:
        return pd.DataFrame(columns=["timestamp", "close", "volume", "quote_volume"])
    out = pd.DataFrame(rows)
    return out[(out["timestamp"] >= start) & (out["timestamp"] <= end)].drop_duplicates("timestamp").sort_values("timestamp")


def load_daily_panel(symbols: list[str], start: pd.Timestamp, end: pd.Timestamp, *, allow_download: bool = True) -> tuple[pd.DataFrame, dict[str, Any]]:
    mod = load_module(REBUILD_MODULE_PATH, "rank213_age90_daily_rebuild_mod")
    frames: list[pd.Series] = []
    missing: list[str] = []
    rest_filled: list[str] = []
    for symbol in symbols:
        cache_path = ART_DIR / "rank213_local_cache" / "monthly_volume_universe" / "daily_1d" / f"{symbol}.csv"
        if not allow_download and not cache_path.exists():
            missing.append(symbol)
            continue
        try:
            df = mod.load_daily_prices(symbol, start, end)
        except Exception:
            missing.append(symbol)
            continue
        if df.empty:
            missing.append(symbol)
            continue
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
        if allow_download and (df["timestamp"].dropna().empty or df["timestamp"].max() < pd.to_datetime(end, utc=True).floor("1D")):
            try:
                recent = fetch_recent_daily_klines(symbol, start, end)
                if not recent.empty:
                    df = pd.concat([df, recent], ignore_index=True)
                    df = df.dropna(subset=["timestamp", "close"]).drop_duplicates("timestamp", keep="last").sort_values("timestamp")
                    rest_filled.append(symbol)
                    cache_path.parent.mkdir(parents=True, exist_ok=True)
                    df[["timestamp", "close", "volume", "quote_volume"]].to_csv(cache_path, index=False)
            except Exception:
                pass
        ser = df.set_index("timestamp")["close"].astype(float).rename(symbol)
        frames.append(ser)
    if not frames:
        return pd.DataFrame(), {"missing_symbols": missing, "loaded_symbols": 0, "rest_filled_symbols": rest_filled}
    panel = pd.concat(frames, axis=1).sort_index()
    panel.index = pd.to_datetime(panel.index, utc=True)
    panel = panel[~panel.index.duplicated(keep="last")].sort_index()
    return panel, {"missing_symbols": missing, "loaded_symbols": len(frames), "rest_filled_symbols": rest_filled}


def score_age90_14d_skip1d_voladj(panel: pd.DataFrame, decision_ts: pd.Timestamp, eligible: list[str]) -> pd.Series:
    t1 = decision_ts - pd.Timedelta(days=1)
    t0 = decision_ts - pd.Timedelta(days=15)
    if t1 not in panel.index or t0 not in panel.index:
        return pd.Series(dtype=float)
    px1 = pd.to_numeric(panel.loc[t1, eligible], errors="coerce")
    px0 = pd.to_numeric(panel.loc[t0, eligible], errors="coerce")
    mom = px1 / px0 - 1.0
    hist = panel.loc[t0:t1, eligible].pct_change(fill_method=None).dropna(how="all")
    vol = hist.std().replace(0.0, np.nan)
    return (mom / vol).replace([np.inf, -np.inf], np.nan).dropna()


def build_signal(decision_ts: pd.Timestamp | None = None, *, allow_download: bool = True) -> dict[str, Any]:
    if decision_ts is None:
        now = pd.Timestamp.utcnow()
        decision_ts = pd.Timestamp(now.year, now.month, now.day, tz="UTC")
    else:
        decision_ts = pd.to_datetime(decision_ts, utc=True).floor("1D")
    planned_exit_ts = decision_ts + pd.Timedelta(days=1)

    universe, universe_meta = get_universe(decision_ts, allow_download=allow_download)
    candidates = load_candidates()
    onboard_map = {str(r["symbol"]).upper(): pd.to_datetime(r["onboard_utc"], utc=True) for _, r in candidates.iterrows()}
    eligible = [
        sym for sym in universe
        if sym in onboard_map and decision_ts - onboard_map[sym] >= pd.Timedelta(days=AGE_DAYS)
    ]

    panel_start = decision_ts - pd.Timedelta(days=20)
    panel_end = decision_ts - pd.Timedelta(days=1)
    panel, panel_meta = load_daily_panel(sorted(set([*eligible, *universe])), panel_start, panel_end, allow_download=allow_download)
    scores = score_age90_14d_skip1d_voladj(panel, decision_ts, eligible) if not panel.empty else pd.Series(dtype=float)
    ranked = scores.sort_values()
    active = len(ranked) >= TOP_N + BOTTOM_N
    longs = ranked.index[-TOP_N:].tolist()[::-1] if active else []
    shorts = ranked.index[:BOTTOM_N].tolist() if active else []
    weights = {sym: round(0.5 / TOP_N, 10) for sym in longs}
    weights.update({sym: round(-0.5 / BOTTOM_N, 10) for sym in shorts})

    score_payload = [
        {"symbol": str(sym), "score": float(scores.loc[sym])}
        for sym in scores.sort_values(ascending=False).index
    ]
    hash_payload = {
        "strategy_id": STRATEGY_ID,
        "score_kind": SCORE_KIND,
        "decision_ts": iso_z(decision_ts),
        "planned_exit_ts": iso_z(planned_exit_ts),
        "universe": universe,
        "eligible": eligible,
        "longs": longs,
        "shorts": shorts,
        "weights": weights,
        "scores": [(row["symbol"], round(float(row["score"]), 12)) for row in score_payload],
    }
    signal_hash = stable_hash(hash_payload)

    return {
        "strategy_id": STRATEGY_ID,
        "score_kind": SCORE_KIND,
        "decision_ts": iso_z(decision_ts),
        "planned_exit_ts": iso_z(planned_exit_ts),
        "bar_key": iso_z(decision_ts),
        "decision": SCORE_KIND if active else "flat_insufficient_eligible",
        "gate_on": bool(active),
        "longs": longs,
        "shorts": shorts,
        "weights": weights,
        "universe": universe,
        "eligible_universe": eligible,
        "scores": score_payload,
        "signal_hash": signal_hash,
        "hash_payload": hash_payload,
        "meta": {
            "top_n": TOP_N,
            "bottom_n": BOTTOM_N,
            "age_days": AGE_DAYS,
            "score_formula": "return(t-15d -> t-1d) / realized_vol(t-15d -> t-1d)",
            "selection_causality": "previous full-month quote_volume universe; score skips most recent day",
            "universe_meta": universe_meta,
            "panel_meta": panel_meta,
            "panel_start_utc": iso_z(panel_start),
            "panel_end_utc": iso_z(panel_end),
        },
    }


def current_decision_payload(signal: dict[str, Any]) -> dict[str, Any]:
    return {
        "decision_ts": signal["decision_ts"],
        "planned_exit_ts": signal["planned_exit_ts"],
        "bar_key": signal["bar_key"],
        "decision": signal["decision"],
        "gate_on": bool(signal["gate_on"]),
        "gate_votes": 1 if signal["gate_on"] else 0,
        "gate_valid_rules": 1,
        "gate_needed_votes": 1,
        "longs": signal["longs"],
        "shorts": signal["shorts"],
        "veto_count": 0,
        "veto_threshold": 0.0,
        "eligible_universe_size": len(signal["eligible_universe"]),
        "shadow_turnover_x": 1.0 if signal["gate_on"] else 0.0,
        "shadow_net_bps": None,
        "source_mode": "recompute_recent",
        "frame_source_mode": "recompute_recent",
        "current_decision_source_mode": "recompute_recent",
        "is_preview": False,
        "has_realized_hold_return": False,
        "strategy_id": signal["strategy_id"],
        "score_kind": signal["score_kind"],
        "weights": signal["weights"],
        "signal_hash": signal["signal_hash"],
    }


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Build Rank213 age90 shared signal")
    ap.add_argument("--decision-date", help="UTC decision date, e.g. 2026-05-06")
    ap.add_argument("--no-download", action="store_true", help="Do not download missing Binance daily data")
    args = ap.parse_args()

    signal = build_signal(pd.Timestamp(args.decision_date, tz="UTC") if args.decision_date else None, allow_download=not args.no_download)
    print(json.dumps(signal, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
