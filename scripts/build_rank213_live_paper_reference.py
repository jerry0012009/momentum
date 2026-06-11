#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank213_largecap_xs_jump_veto"
SUMMARY_PATH = ROOT / "reports" / "artifacts" / "optimization_loop" / "rank213_p2_admission_20260328" / "summary.json"

OUT_CLOSED_PATH = ART_DIR / "rank213_paper_reference_closed.csv"
OUT_OPEN_PATH = ART_DIR / "rank213_paper_reference_open.csv"
OUT_STATUS_PATH = ART_DIR / "rank213_paper_reference_status.json"
OUT_CURVE_PATH = ART_DIR / "rank213_paper_reference_curve.csv"

BASKET_NOTIONAL_USDT = 120.0
DEFAULT_RECENT_DAYS = 7


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


shadow_mod = load_module(ROOT / "scripts" / "run_rank213_largecap_xs_jump_veto_shadow_runner.py", "rank213_live_paper_shadow_mod")
funding_mod = load_module(ROOT / "scripts" / "build_rank213_long_history_review_with_funding.py", "rank213_live_paper_funding_mod")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_z(ts: Any) -> str | None:
    if ts is None or pd.isna(ts):
        return None
    return pd.to_datetime(ts, utc=True).strftime("%Y-%m-%dT%H:%M:%SZ")


def normalize_for_csv(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[col]):
            out[col] = out[col].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return out


def load_symbols() -> list[str]:
    payload = read_json(SUMMARY_PATH)
    return [str(s).upper() for s in payload.get("symbols", []) if str(s)]


def build_price_panel(symbols: list[str], start_ts: pd.Timestamp, end_ts: pd.Timestamp) -> tuple[pd.DataFrame, dict[str, pd.DataFrame], dict[str, pd.DataFrame]]:
    price_frames: list[pd.DataFrame] = []
    price_map: dict[str, pd.DataFrame] = {}
    funding_map: dict[str, pd.DataFrame] = {}
    for symbol in symbols:
        kdf = funding_mod.load_or_build_symbol_klines(symbol, start_ts, end_ts)
        if kdf.empty:
            continue
        price_map[symbol] = kdf.copy()
        price_frames.append(kdf.rename(columns={"close": symbol}).set_index("timestamp")[[symbol]])
        fdf, _ = funding_mod.load_or_build_symbol_funding(symbol, start_ts, end_ts)
        funding_map[symbol] = fdf.copy()
    if not price_frames:
        return pd.DataFrame(), price_map, funding_map
    panel = price_frames[0]
    for frame in price_frames[1:]:
        panel = panel.join(frame, how="outer")
    panel = panel.sort_index().ffill()
    return panel, price_map, funding_map


def parse_symbols(text: Any) -> list[str]:
    return [x for x in str(text or "").split(",") if x]


def mean_leg_return(panel: pd.DataFrame, symbols: list[str], entry_ts: pd.Timestamp, mark_ts: pd.Timestamp, *, short: bool) -> float:
    if not symbols:
        return 0.0
    legs: list[float] = []
    for symbol in symbols:
        if symbol not in panel.columns:
            continue
        entry_px = panel.at[entry_ts, symbol] if entry_ts in panel.index else np.nan
        mark_px = panel.at[mark_ts, symbol] if mark_ts in panel.index else np.nan
        if pd.isna(entry_px) or pd.isna(mark_px) or float(entry_px) == 0.0:
            continue
        raw_ret = float(mark_px) / float(entry_px) - 1.0
        legs.append(-raw_ret if short else raw_ret)
    if not legs:
        return np.nan
    return float(np.mean(legs) * 0.5)


def compute_reference_row(row: pd.Series, panel: pd.DataFrame, funding_map: dict[str, pd.DataFrame], latest_mark_ts: pd.Timestamp) -> dict[str, Any] | None:
    decision_ts = pd.to_datetime(row.get("timestamp_ts"), utc=True, errors="coerce")
    planned_exit_ts = pd.to_datetime(row.get("exit_ts"), utc=True, errors="coerce")
    if pd.isna(decision_ts) or pd.isna(planned_exit_ts):
        return None
    gate_on = bool(row.get("gate_on"))
    longs = parse_symbols(row.get("shadow_longs"))
    shorts = parse_symbols(row.get("shadow_shorts"))
    if latest_mark_ts < decision_ts:
        return None

    actual_mark_ts = min(planned_exit_ts, latest_mark_ts)
    is_closed = actual_mark_ts >= planned_exit_ts
    turnover_x = float(pd.to_numeric(pd.Series([row.get("shadow_turnover_x")]), errors="coerce").fillna(0.0).iloc[0]) if gate_on else 0.0

    if gate_on:
        long_price = mean_leg_return(panel, longs, decision_ts, actual_mark_ts, short=False)
        short_price = mean_leg_return(panel, shorts, decision_ts, actual_mark_ts, short=True)
        if pd.isna(long_price) or pd.isna(short_price):
            return None
        paper_price_ret = float(long_price + short_price)
        long_funding_ret, long_events = funding_mod.funding_sum_for_symbols(funding_map, longs, decision_ts, actual_mark_ts, sign=+1)
        short_funding_ret, short_events = funding_mod.funding_sum_for_symbols(funding_map, shorts, decision_ts, actual_mark_ts, sign=-1)
        paper_funding_ret = float(long_funding_ret + short_funding_ret)
        paper_net_ret = float(paper_price_ret + paper_funding_ret - turnover_x * (funding_mod.COST_BPS / 10000.0))
        paper_net_bps = paper_net_ret * 10000.0
        paper_pnl_usdt = paper_net_ret * BASKET_NOTIONAL_USDT
    else:
        long_events = 0
        short_events = 0
        paper_price_ret = 0.0
        paper_funding_ret = 0.0
        paper_net_ret = 0.0
        paper_net_bps = 0.0
        paper_pnl_usdt = 0.0

    return {
        "decision_ts": decision_ts,
        "planned_exit_ts": planned_exit_ts,
        "actual_exit_ts": planned_exit_ts if is_closed else pd.NaT,
        "mark_ts": actual_mark_ts,
        "paper_mode": "asof_rawbar_funding_reference",
        "reference_status": "closed" if is_closed else "open_mark_to_market",
        "gate_on": gate_on,
        "longs": ",".join(longs),
        "shorts": ",".join(shorts),
        "veto_count": int(pd.to_numeric(pd.Series([row.get("veto_count")]), errors="coerce").fillna(0).iloc[0]),
        "paper_price_ret": paper_price_ret,
        "paper_funding_ret": paper_funding_ret,
        "paper_net_ret": paper_net_ret,
        "paper_net_bps": paper_net_bps,
        "paper_pnl_usdt": paper_pnl_usdt,
        "paper_turnover_x": turnover_x,
        "funding_events": int(long_events + short_events),
    }


def build_reference_frames(*, recent_days: int) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    shadow_frame, source_meta = shadow_mod.build_shadow_frame(recent_days=recent_days)
    shadow_frame = shadow_frame.sort_values("timestamp_ts").reset_index(drop=True)
    if shadow_frame.empty:
        return pd.DataFrame(), pd.DataFrame(), {"source_mode": source_meta.get("mode"), "recent_days": recent_days}

    now_ts = pd.Timestamp.utcnow()
    now_ts = now_ts.tz_convert("UTC") if now_ts.tzinfo else now_ts.tz_localize("UTC")
    preview_rows = shadow_mod.build_recent_preview_rows(recent_days=recent_days, existing_frame=shadow_frame, now_ts=now_ts)
    if not preview_rows.empty:
        realized = shadow_frame[shadow_frame["shadow_has_realized_hold_return"].fillna(False)].copy()
        shadow_frame = pd.concat([realized, preview_rows], ignore_index=True).sort_values("timestamp_ts").drop_duplicates(subset=["timestamp_ts"], keep="last").reset_index(drop=True)

    since_ts = now_ts - pd.Timedelta(days=recent_days)
    relevant = shadow_frame[shadow_frame["timestamp_ts"] >= since_ts].copy()
    if relevant.empty:
        relevant = shadow_frame.tail(128).copy()

    symbols = load_symbols()
    panel_start = pd.to_datetime(relevant["timestamp_ts"].min(), utc=True) - pd.Timedelta(days=3)
    panel_end = now_ts.floor("15min")
    panel, _, funding_map = build_price_panel(symbols, panel_start, panel_end)
    if panel.empty:
        return pd.DataFrame(), pd.DataFrame(), {
            "source_mode": source_meta.get("mode"),
            "recent_days": recent_days,
            "panel_start_utc": iso_z(panel_start),
            "panel_end_utc": iso_z(panel_end),
            "error": "empty_price_panel",
        }

    latest_mark_ts = pd.to_datetime(panel.index.max(), utc=True)
    rows: list[dict[str, Any]] = []
    for _, row in relevant.iterrows():
        built = compute_reference_row(row, panel, funding_map, latest_mark_ts)
        if built is not None:
            rows.append(built)

    reference = pd.DataFrame(rows)
    if reference.empty:
        return pd.DataFrame(), pd.DataFrame(), {
            "source_mode": source_meta.get("mode"),
            "recent_days": recent_days,
            "panel_start_utc": iso_z(panel_start),
            "panel_end_utc": iso_z(panel_end),
            "latest_mark_ts": iso_z(latest_mark_ts),
            "reference_rows": 0,
        }

    reference["decision_ts"] = pd.to_datetime(reference["decision_ts"], utc=True)
    reference["planned_exit_ts"] = pd.to_datetime(reference["planned_exit_ts"], utc=True)
    reference["actual_exit_ts"] = pd.to_datetime(reference["actual_exit_ts"], utc=True, errors="coerce")
    reference["mark_ts"] = pd.to_datetime(reference["mark_ts"], utc=True)
    reference = reference.sort_values("decision_ts").drop_duplicates(subset=["decision_ts"], keep="last").reset_index(drop=True)

    closed = reference[reference["reference_status"] == "closed"].copy().reset_index(drop=True)
    open_df = reference[reference["reference_status"] == "open_mark_to_market"].copy().reset_index(drop=True)

    status = {
        "generated_at_utc": iso_z(now_ts),
        "builder": "scripts/build_rank213_live_paper_reference.py",
        "paper_mode": "backtest_only_historical_klines_and_funding",
        "source_mode": source_meta.get("mode"),
        "recent_days": int(recent_days),
        "panel_start_utc": iso_z(panel_start),
        "panel_end_utc": iso_z(panel_end),
        "latest_mark_ts": iso_z(latest_mark_ts),
        "reference_rows": int(len(reference)),
        "closed_rows": int(len(closed)),
        "open_rows": int(len(open_df)),
        "latest_decision_ts": iso_z(reference["decision_ts"].max()),
        "note": "Independent rank213 paper reference rebuilt from historical 15m K-lines + funding + as-of/formal-gate semantics. It does not read live trades, live signals, live orders, or live execution artifacts.",
    }
    return closed, open_df, status


def build_curve(closed: pd.DataFrame, open_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    if not closed.empty:
        running = 0.0
        for row in closed.sort_values("actual_exit_ts").itertuples(index=False):
            running += float(row.paper_pnl_usdt)
            rows.append({
                "ts": row.actual_exit_ts,
                "paper_pnl_usdt": running,
                "point_type": "closed_cumulative",
            })
    closed_total = float(pd.to_numeric(closed.get("paper_pnl_usdt"), errors="coerce").fillna(0.0).sum()) if not closed.empty else 0.0
    if not open_df.empty:
        open_sorted = open_df.sort_values("mark_ts")
        open_total = float(pd.to_numeric(open_sorted.get("paper_pnl_usdt"), errors="coerce").fillna(0.0).sum())
        latest_mark_ts = pd.to_datetime(open_sorted.iloc[-1]["mark_ts"], utc=True)
        rows.append({
            "ts": latest_mark_ts,
            "paper_pnl_usdt": closed_total + open_total,
            "point_type": "open_snapshot_total",
        })
    return pd.DataFrame(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build independent rank213 paper reference artifacts for the live compare window")
    parser.add_argument("--recent-days", type=int, default=DEFAULT_RECENT_DAYS)
    args = parser.parse_args()

    ensure_dir(ART_DIR)
    closed, open_df, status = build_reference_frames(recent_days=max(1, int(args.recent_days)))
    curve = build_curve(closed, open_df)

    normalize_for_csv(closed).to_csv(OUT_CLOSED_PATH, index=False)
    normalize_for_csv(open_df).to_csv(OUT_OPEN_PATH, index=False)
    normalize_for_csv(curve).to_csv(OUT_CURVE_PATH, index=False)
    OUT_STATUS_PATH.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(OUT_CLOSED_PATH)
    print(OUT_OPEN_PATH)
    print(OUT_STATUS_PATH)
    print(OUT_CURVE_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
