#!/usr/bin/env python3
from __future__ import annotations

"""Honest daily paper runner for Rank 154 / Crypto-Stat-Arb.

What this does
- Recomputes a daily cross-sectional Binance USDT-M perpetual universe.
- Selects a guarded top-30 universe by rolling 30d quote volume.
- Scores carry / momentum / breakout on completed daily bars only.
- Rebalances a paper long-short portfolio once per day and records decisions,
  turnover, costs, funding, equity, and current positions.
- Emits a dedicated report page plus CSV/JSON artifacts for later audit.

What this does NOT do
- It does not place real orders.
- It does not pretend historical seed trades are forward paper results.
- It does not claim exact live fill parity; fills are a paper close-to-close proxy.
"""

import argparse
import json
import math
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from momentum.strategies import rank154_crypto_stat_arb as rank154_signal

ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank154_crypto_stat_arb_runner"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "paper_rank154_crypto_stat_arb_runner"
STATE_PATH = ART_DIR / "rank154_paper_state.json"
STATUS_PATH = ART_DIR / "rank154_paper_status.csv"
EQUITY_PATH = ART_DIR / "rank154_paper_equity_curve.csv"
DECISIONS_PATH = ART_DIR / "rank154_paper_decisions.csv"
TRADES_PATH = ART_DIR / "rank154_paper_rebalance_trades.csv"
POSITIONS_PATH = ART_DIR / "rank154_paper_open_positions.csv"
SNAPSHOT_PATH = ART_DIR / "rank154_paper_universe_snapshot.csv"
EXCLUDED_PATH = ART_DIR / "rank154_paper_universe_excluded.csv"
RUN_SUMMARY_PATH = ART_DIR / "rank154_paper_last_run_summary.json"
REPORT_PATH = SITE_DIR / "report.html"

FUTURES_EXCHANGE_INFO = "https://fapi.binance.com/fapi/v1/exchangeInfo"
FUTURES_TICKER_24H = "https://fapi.binance.com/fapi/v1/ticker/24hr"
FUTURES_KLINES = "https://fapi.binance.com/fapi/v1/klines"
FUNDING_URL = "https://fapi.binance.com/fapi/v1/fundingRate"

CANDIDATE_ID = "rank154_crypto_stat_arb"
CANDIDATE_RANK = 154
RUNNER_MODE = "daily_cross_sectional_forward_paper"
REFRESH_CADENCE = "daily_utc_close"
SOURCE_RECORD = "research/optimization_loop/2026-03-24_0922_crypto-stat-arb-fresh-intake.md"
LATEST_ADMISSION_RECORD = "research/optimization_loop/2026-03-24_1046_crypto-stat-arb-p2-honesty-execution.md"
PROMOTION_RECORD = "research/strategy_review/2026-03-24_1219_strategy-review.md"
LAUNCH_ENTRY = "reports/site/reading/quant_digests/2026-03-24_0922_crypto-stat-arb-carry-momo-breakout-intake.html"
FACTOR_PAGE_ANCHOR = "reports/site/factors/paper_rank154_crypto_stat_arb_runner/report.html"
SCRIPT_ANCHOR = "scripts/run_rank154_crypto_stat_arb_paper_runner.py"

INITIAL_EQUITY = 10_000.0
COST_BPS_PER_SIDE = 5.0
TOP_24H_PROBE = 60
UNIVERSE_SIZE = 30
MIN_LISTING_DAYS = 180
MAX_ABS_WEIGHT = 0.10
WEIGHT_BUFFER = 0.01
MIN_EFFECTIVE_WEIGHT = 0.005
KLINE_LIMIT_DAYS = 140
REQUEST_SLEEP_SEC = 0.05
MAX_REASON_ROWS = 10

STABLE_BASES = {
    "USDT",
    "USDC",
    "FDUSD",
    "BUSD",
    "USDP",
    "TUSD",
    "USDE",
    "USDS",
    "DAI",
}

STATUS_FIELDS = [
    "candidate_id",
    "candidate_rank",
    "stage",
    "runner_mode",
    "refresh_cadence",
    "scheduler_attached",
    "scheduler_unit",
    "latest_signal_date_utc",
    "last_rebalance_ts_utc",
    "equity_usd",
    "lifetime_return",
    "running_max_equity_usd",
    "current_drawdown",
    "gross_exposure",
    "net_exposure",
    "universe_size",
    "long_count",
    "short_count",
    "top_long",
    "top_short",
    "latest_price_pnl_usd",
    "latest_funding_pnl_usd",
    "latest_commission_usd",
    "latest_turnover",
    "latest_reason_summary",
    "source_record",
    "latest_admission_record",
    "promotion_record",
    "launch_entry",
    "factor_page_anchor",
    "script_anchor",
    "positions_path",
    "decisions_path",
    "equity_curve_path",
    "rebalance_trades_path",
    "note",
    "updated_at_utc",
]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_z(ts: Any) -> str:
    return pd.to_datetime(ts, utc=True).strftime("%Y-%m-%dT%H:%M:%SZ")


def human_utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def pct(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def usd(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"${float(v):,.{digits}f}"


def num(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f}"


def fetch_json(base_url: str, params: dict[str, Any] | None = None, *, retries: int = 5) -> Any:
    if params:
        url = base_url + "?" + urllib.parse.urlencode(params)
    else:
        url = base_url
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) OpenClaw-Rank154-PaperRunner/1.0",
        "Accept": "application/json,text/plain,*/*",
    }
    last_err: Exception | None = None
    for attempt in range(retries):
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            last_err = exc
            if exc.code in {403, 418, 429, 500, 502, 503, 504} and attempt < retries - 1:
                time.sleep((attempt + 1) * 1.5)
                continue
            raise
        except urllib.error.URLError as exc:
            last_err = exc
            if attempt < retries - 1:
                time.sleep((attempt + 1) * 1.5)
                continue
            raise
    if last_err is not None:
        raise last_err
    raise RuntimeError(f"failed to fetch json from {url}")


def read_csv_or_empty(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path)


def normalize_for_csv(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[col]):
            out[col] = out[col].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return out


def append_csv(path: Path, df: pd.DataFrame) -> None:
    if df.empty:
        return
    out = normalize_for_csv(df)
    if path.exists() and path.stat().st_size > 0:
        prior = pd.read_csv(path)
        merged = pd.concat([prior, out], ignore_index=True)
        merged.to_csv(path, index=False)
    else:
        out.to_csv(path, index=False)


def save_state(state: dict[str, Any]) -> None:
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return {}
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def is_plain_alpha_base(base: str) -> bool:
    return rank154_signal.is_plain_alpha_base(base)


def fetch_exchange_and_tickers() -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    exchange_info = fetch_json(FUTURES_EXCHANGE_INFO)
    tickers = {row.get("symbol", ""): row for row in fetch_json(FUTURES_TICKER_24H)}
    symbol_info: dict[str, dict[str, Any]] = {}
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
        symbol_info[symbol] = {
            "symbol": symbol,
            "base_asset": base,
            "onboard_ms": float(row.get("onboardDate") or 0.0),
            "quote_asset": "USDT",
            "plain_alpha_base": is_plain_alpha_base(base),
        }
    return symbol_info, tickers


def fetch_daily_klines(symbol: str, *, limit_days: int = KLINE_LIMIT_DAYS) -> pd.DataFrame:
    data = fetch_json(
        FUTURES_KLINES,
        {
            "symbol": symbol,
            "interval": "1d",
            "limit": limit_days,
        },
    )
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(
        data,
        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "number_of_trades",
            "taker_buy_base_asset_volume",
            "taker_buy_quote_asset_volume",
            "ignore",
        ],
    )
    now_ms = pd.Timestamp.now("UTC").timestamp() * 1000.0
    df = df[pd.to_numeric(df["close_time"], errors="coerce") < now_ms].copy()
    if df.empty:
        return df
    out = pd.DataFrame(
        {
            "date": pd.to_datetime(df["open_time"], unit="ms", utc=True).dt.floor("D"),
            "open": pd.to_numeric(df["open"], errors="coerce"),
            "high": pd.to_numeric(df["high"], errors="coerce"),
            "low": pd.to_numeric(df["low"], errors="coerce"),
            "close": pd.to_numeric(df["close"], errors="coerce"),
            "base_volume": pd.to_numeric(df["volume"], errors="coerce"),
            "quote_volume": pd.to_numeric(df["quote_asset_volume"], errors="coerce"),
            "close_time": pd.to_datetime(df["close_time"], unit="ms", utc=True),
        }
    )
    return out.dropna().sort_values("date").reset_index(drop=True)


def fetch_funding_history(symbol: str, *, start_ms: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Fetch funding rate history. Returns (daily_agg, per_event).

    daily_agg: columns [date, funding_rate_last, funding_rate_sum, funding_count]
    per_event: columns [timestamp, date, funding_rate, mark_price]
    """
    rows: list[dict[str, Any]] = []
    current = int(start_ms)
    while True:
        data = fetch_json(FUNDING_URL, {"symbol": symbol, "startTime": current, "limit": 1000})
        if not data:
            break
        rows.extend(data)
        last_ts = int(data[-1].get("fundingTime") or 0)
        if len(data) < 1000 or last_ts <= current:
            break
        current = last_ts + 1
        time.sleep(REQUEST_SLEEP_SEC)
    empty_daily = pd.DataFrame(columns=["date", "funding_rate_last", "funding_rate_sum", "funding_count"])
    empty_events = pd.DataFrame(columns=["timestamp", "date", "funding_rate", "mark_price"])
    if not rows:
        return empty_daily, empty_events
    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(pd.to_numeric(df["fundingTime"], errors="coerce"), unit="ms", utc=True)
    df["funding_rate"] = pd.to_numeric(df["fundingRate"], errors="coerce")
    df["mark_price"] = pd.to_numeric(df.get("markPrice", pd.Series(dtype=float)), errors="coerce")
    df = df.dropna(subset=["timestamp", "funding_rate"]).copy()
    df["date"] = df["timestamp"].dt.floor("D")
    # Per-event record (for PnL)
    per_event = df[["timestamp", "date", "funding_rate", "mark_price"]].copy()
    # Daily aggregation: last settled rate (for signal), sum (for backward compat), count
    daily = df.groupby("date", as_index=False).agg(
        funding_rate_last=("funding_rate", "last"),
        funding_rate_sum=("funding_rate", "sum"),
        funding_count=("funding_rate", "count"),
    ).sort_values("date").reset_index(drop=True)
    return daily, per_event


def days_since_high_rolling(close: pd.Series, window: int = 20) -> pd.Series:
    return rank154_signal.days_since_high_rolling(close, window)


def build_symbol_frame(symbol: str, info: dict[str, Any], ticker_row: dict[str, Any]) -> pd.DataFrame:
    bars = fetch_daily_klines(symbol)
    if bars.empty:
        return pd.DataFrame()
    start_ms = int(bars["date"].min().timestamp() * 1000)
    funding_daily, funding_events = fetch_funding_history(symbol, start_ms=start_ms)
    frame = bars.merge(funding_daily, on="date", how="left")
    frame["funding_rate_last"] = frame["funding_rate_last"].fillna(0.0)
    frame["funding_rate_sum"] = frame["funding_rate_sum"].fillna(0.0)
    frame["funding_count"] = frame["funding_count"].fillna(0).astype(int)
    frame["symbol"] = symbol
    frame["base_asset"] = info["base_asset"]
    frame["quote_volume_24h"] = float(ticker_row.get("quoteVolume") or 0.0)
    frame["last_price"] = float(ticker_row.get("lastPrice") or frame["close"].iloc[-1])
    frame["listing_days"] = (frame["date"] - pd.to_datetime(info["onboard_ms"], unit="ms", utc=True)).dt.total_seconds() / 86400.0
    frame["plain_alpha_base"] = bool(info.get("plain_alpha_base"))
    frame["trail_quote_volume_30d"] = frame["quote_volume"].rolling(30, min_periods=30).mean()
    frame["momo_10d"] = frame["close"].pct_change(10)
    frame["days_since_20d_high"] = days_since_high_rolling(frame["close"], 20)
    frame["breakout_raw"] = 19.0 - frame["days_since_20d_high"]
    # Use LAST settled rate (not sum) to avoid 4h/8h interval bias
    frame["carry_raw"] = frame["funding_rate_last"]
    frame["decision_ready"] = (
        frame["trail_quote_volume_30d"].notna()
        & frame["momo_10d"].notna()
        & frame["breakout_raw"].notna()
    )
    frame["guard_pass"] = (
        frame["decision_ready"]
        & frame["plain_alpha_base"]
        & (frame["listing_days"] >= MIN_LISTING_DAYS)
    )
    frame["guard_reason"] = np.where(
        ~frame["plain_alpha_base"],
        "filtered_non_alpha_or_stable_base",
        np.where(frame["listing_days"] < MIN_LISTING_DAYS, "listing_too_short", np.where(~frame["decision_ready"], "insufficient_history", "eligible")),
    )
    return frame.sort_values("date").reset_index(drop=True)


def centered_deciles(series: pd.Series) -> tuple[pd.Series, pd.Series]:
    return rank154_signal.centered_deciles(series)


def build_panel_for_date(frames: dict[str, pd.DataFrame], decision_date: pd.Timestamp) -> tuple[pd.DataFrame, pd.DataFrame]:
    return rank154_signal.build_panel_for_date(
        frames,
        decision_date,
        universe_size=UNIVERSE_SIZE,
        max_abs_weight=MAX_ABS_WEIGHT,
        min_effective_weight=MIN_EFFECTIVE_WEIGHT,
    )


def build_reason_text(row: pd.Series) -> str:
    return rank154_signal.build_reason_text(row)


def state_positions_frame(state: dict[str, Any]) -> pd.DataFrame:
    positions = state.get("positions", {}) or {}
    rows = []
    for symbol, pos in positions.items():
        rows.append({
            "symbol": symbol,
            "quantity": float(pos.get("quantity") or 0.0),
            "weight": float(pos.get("weight") or 0.0),
            "entry_price": float(pos.get("entry_price") or 0.0),
            "entry_signal_date_utc": pos.get("entry_signal_date_utc"),
            "decision_reason": pos.get("decision_reason") or "",
        })
    return pd.DataFrame(rows)


def build_price_maps(frames: dict[str, pd.DataFrame], decision_date: pd.Timestamp) -> tuple[dict[str, float], dict[str, float]]:
    price_map: dict[str, float] = {}
    funding_map: dict[str, float] = {}
    for symbol, frame in frames.items():
        row = frame[frame["date"] == decision_date]
        if row.empty:
            continue
        price_map[symbol] = float(row.iloc[0]["close"])
        # Use funding_rate_sum for PnL (total funding paid/received for the day)
        funding_map[symbol] = float(row.iloc[0].get("funding_rate_sum", 0.0))
    return price_map, funding_map


def compute_period_pnl(state: dict[str, Any], decision_date: pd.Timestamp, price_map: dict[str, float], funding_map: dict[str, float]) -> tuple[float, float, float]:
    gross_price_pnl = 0.0
    funding_pnl = 0.0
    for symbol, pos in (state.get("positions", {}) or {}).items():
        qty = float(pos.get("quantity") or 0.0)
        entry_price = float(pos.get("entry_price") or 0.0)
        if symbol not in price_map or entry_price <= 0 or qty == 0:
            continue
        close_price = float(price_map[symbol])
        gross_price_pnl += qty * (close_price - entry_price)
        funding_rate_sum = float(funding_map.get(symbol) or 0.0)
        funding_pnl += -qty * entry_price * funding_rate_sum
    equity_before = float(state.get("current_equity") or INITIAL_EQUITY) + gross_price_pnl + funding_pnl
    return gross_price_pnl, funding_pnl, equity_before


def apply_rebalance(
    state: dict[str, Any],
    decision_date: pd.Timestamp,
    universe: pd.DataFrame,
    panel: pd.DataFrame,
    price_map: dict[str, float],
    equity_before: float,
) -> tuple[dict[str, Any], pd.DataFrame, pd.DataFrame, float]:
    current_positions = state_positions_frame(state)
    current_weight_map: dict[str, float] = {}
    if not current_positions.empty and equity_before > 0:
        for _, row in current_positions.iterrows():
            symbol = str(row["symbol"])
            qty = float(row["quantity"])
            px = float(price_map.get(symbol) or 0.0)
            if px <= 0:
                continue
            current_weight_map[symbol] = qty * px / equity_before

    target_weight_map = {str(row["symbol"]): float(row["target_weight"]) for _, row in universe.iterrows()}
    reason_map = {str(row["symbol"]): str(row["decision_reason"]) for _, row in universe.iterrows()}
    feature_map = universe.set_index("symbol").to_dict(orient="index") if not universe.empty else {}

    symbol_set = sorted(set(current_weight_map) | set(target_weight_map) | set(price_map))
    rebalance_rows: list[dict[str, Any]] = []
    final_weight_map: dict[str, float] = {}

    for symbol in symbol_set:
        current_weight = float(current_weight_map.get(symbol, 0.0))
        target_weight = float(target_weight_map.get(symbol, 0.0))
        final_weight = current_weight if abs(target_weight - current_weight) <= WEIGHT_BUFFER else target_weight
        if abs(final_weight) < MIN_EFFECTIVE_WEIGHT:
            final_weight = 0.0
        final_weight_map[symbol] = final_weight
        delta_weight = final_weight - current_weight
        trade_notional = abs(delta_weight) * equity_before
        side = "buy" if delta_weight > 0 else ("sell" if delta_weight < 0 else "hold")
        feat = feature_map.get(symbol, {})
        rebalance_rows.append(
            {
                "signal_date_utc": iso_z(decision_date),
                "symbol": symbol,
                "action": side,
                "current_weight": current_weight,
                "target_weight": target_weight,
                "final_weight": final_weight,
                "delta_weight": delta_weight,
                "trade_notional_usd": trade_notional,
                "close_price": float(price_map.get(symbol) or np.nan),
                "commission_usd": trade_notional * COST_BPS_PER_SIDE / 10000.0,
                "in_universe": int(symbol in target_weight_map),
                "decision_reason": reason_map.get(symbol, "close_out_not_in_top30_or_guard_failed"),
                "dominant_driver": feat.get("dominant_driver"),
                "carry_decile": feat.get("carry_decile"),
                "momo_decile": feat.get("momo_decile"),
                "breakout_decile": feat.get("breakout_decile"),
                "volume_rank_30d": feat.get("volume_rank_30d"),
            }
        )

    rebalance_df = pd.DataFrame(rebalance_rows)
    commission = float(rebalance_df["commission_usd"].sum()) if not rebalance_df.empty else 0.0
    equity_after = max(0.0, equity_before - commission)

    new_positions: dict[str, Any] = {}
    position_rows: list[dict[str, Any]] = []
    for symbol, weight in final_weight_map.items():
        px = float(price_map.get(symbol) or 0.0)
        if px <= 0 or abs(weight) < MIN_EFFECTIVE_WEIGHT:
            continue
        qty = equity_after * weight / px
        reason = reason_map.get(symbol, "carry_forward")
        new_positions[symbol] = {
            "quantity": qty,
            "weight": weight,
            "entry_price": px,
            "entry_signal_date_utc": iso_z(decision_date),
            "decision_reason": reason,
        }
        position_rows.append(
            {
                "signal_date_utc": iso_z(decision_date),
                "symbol": symbol,
                "side": "long" if weight > 0 else "short",
                "weight": weight,
                "quantity": qty,
                "entry_price": px,
                "mark_price": px,
                "decision_reason": reason,
            }
        )

    state["positions"] = new_positions
    state["current_equity"] = equity_after
    state["last_signal_date_utc"] = iso_z(decision_date)
    state["last_rebalance_ts_utc"] = iso_z(utc_now())
    state["latest_reason_summary"] = summarize_reasons(universe)
    return state, rebalance_df, pd.DataFrame(position_rows), commission


def summarize_reasons(universe: pd.DataFrame) -> str:
    if universe.empty:
        return "no_eligible_universe"
    longs = universe[universe["target_weight"] > 0].sort_values("target_weight", ascending=False).head(3)
    shorts = universe[universe["target_weight"] < 0].sort_values("target_weight").head(3)
    long_txt = ", ".join(longs["symbol"].tolist()) if not longs.empty else "none"
    short_txt = ", ".join(shorts["symbol"].tolist()) if not shorts.empty else "none"
    return f"多头主力={long_txt}；空头主力={short_txt}"


def build_decision_rows(universe: pd.DataFrame, panel: pd.DataFrame, decision_date: pd.Timestamp) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if panel.empty:
        empty = pd.DataFrame()
        return empty, empty, empty
    in_universe = set(universe["symbol"].tolist()) if not universe.empty else set()
    volume_rank_map = {}
    if not panel.empty:
        elig = panel[panel["guard_pass"]].sort_values(["trail_quote_volume_30d", "quote_volume_24h"], ascending=False).reset_index(drop=True)
        volume_rank_map = {str(sym): int(i + 1) for i, sym in enumerate(elig["symbol"].tolist())}

    decision_rows = []
    excluded_rows = []
    for _, row in panel.iterrows():
        symbol = str(row["symbol"])
        in_uni = symbol in in_universe
        reason = "selected_top30_volume_guarded" if in_uni else str(row.get("guard_reason") or "outside_top30_by_30d_volume")
        target = 0.0
        driver = ""
        carry_dec = np.nan
        momo_dec = np.nan
        breakout_dec = np.nan
        combined = np.nan
        target_row = universe[universe["symbol"] == symbol]
        if not target_row.empty:
            rr = target_row.iloc[0]
            target = float(rr["target_weight"])
            driver = str(rr["dominant_driver"])
            carry_dec = rr["carry_decile"]
            momo_dec = rr["momo_decile"]
            breakout_dec = rr["breakout_decile"]
            combined = rr["combined_score"]
            reason = str(rr["decision_reason"])
        decision_rows.append(
            {
                "signal_date_utc": iso_z(decision_date),
                "symbol": symbol,
                "base_asset": row["base_asset"],
                "selected": int(in_uni),
                "target_weight": target,
                "side": "long" if target > 0 else ("short" if target < 0 else "flat"),
                "trail_quote_volume_30d": float(row["trail_quote_volume_30d"]) if pd.notna(row["trail_quote_volume_30d"]) else np.nan,
                "volume_rank_30d": volume_rank_map.get(symbol),
                "listing_days": float(row["listing_days"]) if pd.notna(row["listing_days"]) else np.nan,
                "carry_raw": float(row["carry_raw"]) if pd.notna(row["carry_raw"]) else np.nan,
                "momo_10d": float(row["momo_10d"]) if pd.notna(row["momo_10d"]) else np.nan,
                "breakout_raw": float(row["breakout_raw"]) if pd.notna(row["breakout_raw"]) else np.nan,
                "carry_decile": carry_dec,
                "momo_decile": momo_dec,
                "breakout_decile": breakout_dec,
                "combined_score": combined,
                "dominant_driver": driver,
                "guard_reason": row.get("guard_reason"),
                "decision_reason": reason,
            }
        )
        if not in_uni:
            excluded_rows.append(
                {
                    "signal_date_utc": iso_z(decision_date),
                    "symbol": symbol,
                    "base_asset": row["base_asset"],
                    "guard_reason": row.get("guard_reason"),
                    "trail_quote_volume_30d": float(row["trail_quote_volume_30d"]) if pd.notna(row["trail_quote_volume_30d"]) else np.nan,
                    "volume_rank_30d": volume_rank_map.get(symbol),
                    "listing_days": float(row["listing_days"]) if pd.notna(row["listing_days"]) else np.nan,
                }
            )
    return pd.DataFrame(decision_rows), universe.copy(), pd.DataFrame(excluded_rows)


def load_frames_for_candidate_symbols(state: dict[str, Any]) -> tuple[dict[str, pd.DataFrame], dict[str, dict[str, Any]], pd.Timestamp]:
    symbol_info, tickers = fetch_exchange_and_tickers()
    eligible_symbols = []
    for symbol, row in tickers.items():
        if symbol not in symbol_info:
            continue
        try:
            qv = float(row.get("quoteVolume") or 0.0)
        except Exception:
            qv = 0.0
        eligible_symbols.append((symbol, qv))
    eligible_symbols.sort(key=lambda x: x[1], reverse=True)
    top_symbols = [symbol for symbol, _ in eligible_symbols[:TOP_24H_PROBE]]
    held_symbols = sorted((state.get("positions", {}) or {}).keys())
    candidate_symbols = list(dict.fromkeys(top_symbols + held_symbols))

    frames: dict[str, pd.DataFrame] = {}
    meta: dict[str, dict[str, Any]] = {}
    latest_dates: list[pd.Timestamp] = []
    for symbol in candidate_symbols:
        info = symbol_info.get(symbol)
        ticker_row = tickers.get(symbol)
        if not info or not ticker_row:
            continue
        try:
            frame = build_symbol_frame(symbol, info, ticker_row)
        except Exception as exc:  # noqa: BLE001
            print(f"[warn] rank154 skip {symbol}: {exc}")
            time.sleep(REQUEST_SLEEP_SEC)
            continue
        time.sleep(REQUEST_SLEEP_SEC)
        if frame.empty:
            continue
        frames[symbol] = frame
        meta[symbol] = {
            "symbol": symbol,
            "base_asset": info["base_asset"],
            "onboard_ms": info["onboard_ms"],
            "plain_alpha_base": info["plain_alpha_base"],
            "quote_volume_24h": float(ticker_row.get("quoteVolume") or 0.0),
        }
        latest_dates.append(pd.to_datetime(frame["date"].max(), utc=True))
    if not latest_dates:
        raise RuntimeError("No symbol data fetched for Rank 154 paper runner")
    latest_decision_date = min(latest_dates)
    return frames, meta, latest_decision_date


def build_missing_dates(state: dict[str, Any], latest_decision_date: pd.Timestamp) -> list[pd.Timestamp]:
    last_signal = state.get("last_signal_date_utc")
    if not last_signal:
        return [latest_decision_date]
    start = pd.to_datetime(last_signal, utc=True) + pd.Timedelta(days=1)
    if start > latest_decision_date:
        return []
    return list(pd.date_range(start=start, end=latest_decision_date, freq="1D", tz="UTC"))


def build_equity_row(
    decision_date: pd.Timestamp,
    state_before: dict[str, Any],
    state_after: dict[str, Any],
    universe: pd.DataFrame,
    price_pnl: float,
    funding_pnl: float,
    commission: float,
    equity_before: float,
) -> dict[str, Any]:
    equity_after = float(state_after.get("current_equity") or 0.0)
    running_max = max(float(state_before.get("running_max_equity") or INITIAL_EQUITY), equity_after)
    state_after["running_max_equity"] = running_max
    drawdown = (equity_after / running_max - 1.0) if running_max > 0 else 0.0
    turnover = 0.0
    if commission > 0 and equity_before > 0:
        turnover = commission / (COST_BPS_PER_SIDE / 10000.0) / equity_before
    gross = float(universe["target_weight"].abs().sum()) if not universe.empty else 0.0
    net = float(universe["target_weight"].sum()) if not universe.empty else 0.0
    long_count = int((universe["target_weight"] > 0).sum()) if not universe.empty else 0
    short_count = int((universe["target_weight"] < 0).sum()) if not universe.empty else 0
    top_long = str(universe.sort_values("target_weight", ascending=False).iloc[0]["symbol"]) if long_count else "none"
    top_short = str(universe.sort_values("target_weight").iloc[0]["symbol"]) if short_count else "none"
    return {
        "signal_date_utc": iso_z(decision_date),
        "rebalance_ts_utc": state_after.get("last_rebalance_ts_utc"),
        "equity_before_rebalance_usd": equity_before,
        "price_pnl_usd": price_pnl,
        "funding_pnl_usd": funding_pnl,
        "commission_usd": commission,
        "equity_after_rebalance_usd": equity_after,
        "lifetime_return": equity_after / INITIAL_EQUITY - 1.0,
        "running_max_equity_usd": running_max,
        "drawdown": drawdown,
        "gross_exposure": gross,
        "net_exposure": net,
        "turnover": turnover,
        "universe_size": int(len(universe)),
        "long_count": long_count,
        "short_count": short_count,
        "top_long": top_long,
        "top_short": top_short,
        "reason_summary": state_after.get("latest_reason_summary") or "",
    }


def write_status(state: dict[str, Any], latest_equity_row: dict[str, Any] | None) -> dict[str, Any]:
    positions = state_positions_frame(state)
    long_positions = positions[positions["weight"] > 0].sort_values("weight", ascending=False) if not positions.empty else pd.DataFrame()
    short_positions = positions[positions["weight"] < 0].sort_values("weight") if not positions.empty else pd.DataFrame()
    latest_price_pnl = latest_equity_row.get("price_pnl_usd", 0.0) if latest_equity_row else 0.0
    latest_funding_pnl = latest_equity_row.get("funding_pnl_usd", 0.0) if latest_equity_row else 0.0
    latest_commission = latest_equity_row.get("commission_usd", 0.0) if latest_equity_row else 0.0
    latest_turnover = latest_equity_row.get("turnover", 0.0) if latest_equity_row else 0.0
    status = {
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "stage": "running_autonomous_daily_paper",
        "runner_mode": RUNNER_MODE,
        "refresh_cadence": REFRESH_CADENCE,
        "scheduler_attached": str(bool(state.get("scheduler_attached"))).lower(),
        "scheduler_unit": state.get("scheduler_unit") or "",
        "latest_signal_date_utc": state.get("last_signal_date_utc"),
        "last_rebalance_ts_utc": state.get("last_rebalance_ts_utc"),
        "equity_usd": float(state.get("current_equity") or 0.0),
        "lifetime_return": float(state.get("current_equity") or 0.0) / INITIAL_EQUITY - 1.0,
        "running_max_equity_usd": float(state.get("running_max_equity") or INITIAL_EQUITY),
        "current_drawdown": (float(state.get("current_equity") or 0.0) / float(state.get("running_max_equity") or INITIAL_EQUITY) - 1.0) if float(state.get("running_max_equity") or 0.0) > 0 else 0.0,
        "gross_exposure": float(positions["weight"].abs().sum()) if not positions.empty else 0.0,
        "net_exposure": float(positions["weight"].sum()) if not positions.empty else 0.0,
        "universe_size": int(len(positions)),
        "long_count": int((positions["weight"] > 0).sum()) if not positions.empty else 0,
        "short_count": int((positions["weight"] < 0).sum()) if not positions.empty else 0,
        "top_long": str(long_positions.iloc[0]["symbol"]) if not long_positions.empty else "none",
        "top_short": str(short_positions.iloc[0]["symbol"]) if not short_positions.empty else "none",
        "latest_price_pnl_usd": latest_price_pnl,
        "latest_funding_pnl_usd": latest_funding_pnl,
        "latest_commission_usd": latest_commission,
        "latest_turnover": latest_turnover,
        "latest_reason_summary": state.get("latest_reason_summary") or "",
        "source_record": SOURCE_RECORD,
        "latest_admission_record": LATEST_ADMISSION_RECORD,
        "promotion_record": PROMOTION_RECORD,
        "launch_entry": LAUNCH_ENTRY,
        "factor_page_anchor": FACTOR_PAGE_ANCHOR,
        "script_anchor": SCRIPT_ANCHOR,
        "positions_path": str(POSITIONS_PATH.relative_to(ROOT)),
        "decisions_path": str(DECISIONS_PATH.relative_to(ROOT)),
        "equity_curve_path": str(EQUITY_PATH.relative_to(ROOT)),
        "rebalance_trades_path": str(TRADES_PATH.relative_to(ROOT)),
        "note": "Daily forward paper runner. Uses completed daily bars + daily funding aggregation; no live orders are placed.",
        "updated_at_utc": iso_z(utc_now()),
    }
    pd.DataFrame([status], columns=STATUS_FIELDS).to_csv(STATUS_PATH, index=False)
    return status


def render_table(df: pd.DataFrame, *, percent_cols: set[str] | None = None, money_cols: set[str] | None = None, digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return "<p class='muted'>暂无数据。</p>"
    percent_cols = percent_cols or set()
    money_cols = money_cols or set()
    digits_cols = digits_cols or {}
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = []
        for col in df.columns:
            value = row[col]
            if col in percent_cols:
                text = pct(value, digits_cols.get(col, 2))
            elif col in money_cols:
                text = usd(value, digits_cols.get(col, 2))
            elif isinstance(value, (float, np.floating, int, np.integer)) and not isinstance(value, bool):
                text = num(value, digits_cols.get(col, 2))
            else:
                text = str(value)
            cells.append(f"<td>{escape(text)}</td>")
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def write_report(status: dict[str, Any]) -> None:
    equity_df = read_csv_or_empty(EQUITY_PATH)
    decisions_df = read_csv_or_empty(DECISIONS_PATH)
    trades_df = read_csv_or_empty(TRADES_PATH)
    positions_df = read_csv_or_empty(POSITIONS_PATH)
    excluded_df = read_csv_or_empty(EXCLUDED_PATH)

    recent_equity = equity_df.tail(15).copy() if not equity_df.empty else pd.DataFrame()
    recent_trades = trades_df.tail(20).copy() if not trades_df.empty else pd.DataFrame()
    latest_signal = status.get("latest_signal_date_utc")
    latest_decisions = decisions_df[decisions_df["signal_date_utc"] == latest_signal].copy() if (latest_signal and not decisions_df.empty) else pd.DataFrame()
    latest_decisions = latest_decisions.sort_values("target_weight", ascending=False)
    latest_longs = latest_decisions[latest_decisions["target_weight"] > 0].head(MAX_REASON_ROWS)
    latest_shorts = latest_decisions[latest_decisions["target_weight"] < 0].sort_values("target_weight").head(MAX_REASON_ROWS)
    latest_excluded = excluded_df[excluded_df["signal_date_utc"] == latest_signal].head(15) if (latest_signal and not excluded_df.empty) else pd.DataFrame()

    html = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Rank 154 · Crypto-Stat-Arb Daily Paper Runner</title>
  <style>
    body {{ font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; background: #0b1220; color: #e5e7eb; }}
    .wrap {{ max-width: 1180px; margin: 0 auto; padding: 32px 18px 56px; }}
    h1,h2,h3 {{ margin: 0 0 12px; }}
    p, li {{ line-height: 1.65; }}
    .muted {{ color: #94a3b8; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin: 18px 0 28px; }}
    .card {{ background: #111827; border: 1px solid #1f2937; border-radius: 14px; padding: 16px; }}
    .k {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: .05em; }}
    .v {{ font-size: 22px; font-weight: 700; margin-top: 8px; word-break: break-word; }}
    .s {{ margin-top: 8px; color: #9ca3af; font-size: 13px; }}
    table {{ width: 100%; border-collapse: collapse; background: #111827; border: 1px solid #1f2937; border-radius: 14px; overflow: hidden; margin: 12px 0 28px; }}
    th, td {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid #1f2937; font-size: 13px; vertical-align: top; }}
    th {{ background: #0f172a; color: #cbd5e1; }}
    tr:last-child td {{ border-bottom: none; }}
    code {{ background: #0f172a; color: #cbd5e1; padding: 2px 6px; border-radius: 6px; }}
  </style>
</head>
<body>
  <div class="wrap">
    <p class="muted">Generated: {escape(human_utc(utc_now()))}</p>
    <h1>Rank 154 · Crypto-Stat-Arb · Daily forward paper runner</h1>
    <p class="muted">这条 lane 现在记录的是 <b>daily forward paper</b>：每天用已完成的 Binance USDT-M perpetual 日线与 funding 重算 top-30 横截面组合，并写入决策、仓位、换手、费用、PnL 与证据。它不是 live trading。</p>

    <div class="grid">
      <div class="card"><div class="k">Latest signal date</div><div class="v">{escape(str(status.get('latest_signal_date_utc') or 'none'))}</div><div class="s">completed daily bar only</div></div>
      <div class="card"><div class="k">Equity</div><div class="v">{escape(usd(status.get('equity_usd')))}</div><div class="s">lifetime={escape(pct(status.get('lifetime_return')))}</div></div>
      <div class="card"><div class="k">Current drawdown</div><div class="v">{escape(pct(status.get('current_drawdown')))}</div><div class="s">running max={escape(usd(status.get('running_max_equity_usd')))}</div></div>
      <div class="card"><div class="k">Exposure</div><div class="v">gross {escape(pct(status.get('gross_exposure')))}</div><div class="s">net {escape(pct(status.get('net_exposure')))}</div></div>
      <div class="card"><div class="k">Top long / short</div><div class="v">{escape(str(status.get('top_long') or 'none'))}</div><div class="s">vs {escape(str(status.get('top_short') or 'none'))}</div></div>
      <div class="card"><div class="k">Latest day costs</div><div class="v">{escape(usd(status.get('latest_commission_usd')))}</div><div class="s">turnover {escape(pct(status.get('latest_turnover')))}</div></div>
    </div>

    <div class="card">
      <p><b>一句话状态</b></p>
      <ul class="muted">
        <li><b>当前 runner 已经不再是 refresh-only frozen seed。</b> 它会每天重算 guarded top-30 perp universe、生成组合权重，并留下 forward paper 证据链。</li>
        <li>执行口径：<code>completed daily bars only</code>、<code>daily funding aggregation</code>、<code>{COST_BPS_PER_SIDE:.1f} bps per side</code>、<code>{WEIGHT_BUFFER:.2%} weight buffer</code>、<code>{MAX_ABS_WEIGHT:.0%}</code> 单币权重上限。</li>
        <li>guard：过滤非纯字母 base / 稳定币类 base，且要求至少 <code>{MIN_LISTING_DAYS}</code> 天上市历史，尽量避免把 1000 系列/刚上市妖币直接混进 top-30 组合。</li>
      </ul>
    </div>

    <h2>Current open positions</h2>
    {render_table(positions_df[['signal_date_utc','symbol','side','weight','quantity','entry_price','decision_reason']].tail(20) if not positions_df.empty else positions_df, percent_cols={'weight'}, digits_cols={'weight': 2, 'quantity': 6, 'entry_price': 4})}

    <h2>Latest long basket</h2>
    {render_table(latest_longs[['symbol','target_weight','dominant_driver','carry_decile','momo_decile','breakout_decile','decision_reason']] if not latest_longs.empty else latest_longs, percent_cols={'target_weight'}, digits_cols={'target_weight': 2})}

    <h2>Latest short basket</h2>
    {render_table(latest_shorts[['symbol','target_weight','dominant_driver','carry_decile','momo_decile','breakout_decile','decision_reason']] if not latest_shorts.empty else latest_shorts, percent_cols={'target_weight'}, digits_cols={'target_weight': 2})}

    <h2>Recent equity curve</h2>
    {render_table(recent_equity[['signal_date_utc','equity_after_rebalance_usd','price_pnl_usd','funding_pnl_usd','commission_usd','turnover','drawdown','top_long','top_short']] if not recent_equity.empty else recent_equity, percent_cols={'turnover','drawdown'}, money_cols={'equity_after_rebalance_usd','price_pnl_usd','funding_pnl_usd','commission_usd'})}

    <h2>Recent rebalance trades</h2>
    {render_table(recent_trades[['signal_date_utc','symbol','action','current_weight','target_weight','delta_weight','trade_notional_usd','commission_usd','decision_reason']] if not recent_trades.empty else recent_trades, percent_cols={'current_weight','target_weight','delta_weight'}, money_cols={'trade_notional_usd','commission_usd'})}

    <h2>Latest excluded / not-selected names</h2>
    {render_table(latest_excluded[['symbol','guard_reason','trail_quote_volume_30d','volume_rank_30d','listing_days']] if not latest_excluded.empty else latest_excluded, money_cols={'trail_quote_volume_30d'}, digits_cols={'listing_days': 0})}

    <div class="card">
      <p><b>Artifact paths</b></p>
      <ul class="muted">
        <li><code>{escape(str(EQUITY_PATH.relative_to(ROOT)))}</code></li>
        <li><code>{escape(str(DECISIONS_PATH.relative_to(ROOT)))}</code></li>
        <li><code>{escape(str(TRADES_PATH.relative_to(ROOT)))}</code></li>
        <li><code>{escape(str(POSITIONS_PATH.relative_to(ROOT)))}</code></li>
        <li><code>{escape(str(STATUS_PATH.relative_to(ROOT)))}</code></li>
      </ul>
    </div>
  </div>
</body>
</html>
'''
    REPORT_PATH.write_text(html, encoding="utf-8")


def init_or_refresh(args: argparse.Namespace) -> dict[str, Any]:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    state = load_state()
    if args.init_from_now and state and not args.force_reinit:
        raise SystemExit(f"state already exists at {STATE_PATH}; use --force-reinit to reset")
    if args.refresh and not state:
        raise SystemExit(f"missing state at {STATE_PATH}; run --init-from-now first")

    if state and args.scheduler_attached:
        state["scheduler_attached"] = True
        if args.scheduler_unit:
            state["scheduler_unit"] = args.scheduler_unit

    frames, meta, latest_decision_date = load_frames_for_candidate_symbols(state if state else {})
    missing_dates = build_missing_dates(state, latest_decision_date)

    if not missing_dates and not args.init_from_now:
        save_state(state)
        latest_equity = read_csv_or_empty(EQUITY_PATH)
        latest_equity_row = latest_equity.iloc[-1].to_dict() if not latest_equity.empty else None
        status = write_status(state, latest_equity_row)
        write_report(status)
        summary = {
            "run_at_utc": iso_z(utc_now()),
            "mode": "refresh_noop",
            "latest_signal_date_utc": state.get("last_signal_date_utc"),
            "new_signal_dates_processed": 0,
            "status_path": str(STATUS_PATH.relative_to(ROOT)),
            "report_path": str(REPORT_PATH.relative_to(ROOT)),
        }
        RUN_SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return summary

    if args.init_from_now:
        state = {
            "initialized_at_utc": iso_z(utc_now()),
            "mode": RUNNER_MODE,
            "scheduler_attached": bool(args.scheduler_attached),
            "scheduler_unit": args.scheduler_unit or "",
            "current_equity": INITIAL_EQUITY,
            "running_max_equity": INITIAL_EQUITY,
            "positions": {},
            "last_signal_date_utc": None,
            "last_rebalance_ts_utc": None,
            "latest_reason_summary": "",
            "config": {
                "cost_bps_per_side": COST_BPS_PER_SIDE,
                "top_24h_probe": TOP_24H_PROBE,
                "universe_size": UNIVERSE_SIZE,
                "min_listing_days": MIN_LISTING_DAYS,
                "max_abs_weight": MAX_ABS_WEIGHT,
                "weight_buffer": WEIGHT_BUFFER,
                "min_effective_weight": MIN_EFFECTIVE_WEIGHT,
            },
        }
        for path in [EQUITY_PATH, DECISIONS_PATH, TRADES_PATH, POSITIONS_PATH, SNAPSHOT_PATH, EXCLUDED_PATH, STATUS_PATH, REPORT_PATH]:
            if path.exists():
                path.unlink()
        missing_dates = [latest_decision_date]
    elif args.scheduler_attached:
        state["scheduler_attached"] = True
        if args.scheduler_unit:
            state["scheduler_unit"] = args.scheduler_unit

    processed = 0
    latest_equity_row: dict[str, Any] | None = None
    all_new_decisions = []
    all_new_trades = []
    latest_positions_df = pd.DataFrame()
    latest_snapshot_df = pd.DataFrame()
    latest_excluded_df = pd.DataFrame()

    for decision_date in missing_dates:
        universe, panel = build_panel_for_date(frames, decision_date)
        if universe.empty:
            raise RuntimeError(f"No eligible universe for {decision_date.date()} under current guards")
        price_map, funding_map = build_price_maps(frames, decision_date)
        price_pnl, funding_pnl, equity_before = compute_period_pnl(state, decision_date, price_map, funding_map)
        state_before = dict(state)
        state, rebalance_df, positions_df, commission = apply_rebalance(state, decision_date, universe, panel, price_map, equity_before)
        decisions_df, snapshot_df, excluded_df = build_decision_rows(universe, panel, decision_date)
        latest_equity_row = build_equity_row(decision_date, state_before, state, universe, price_pnl, funding_pnl, commission, equity_before)
        processed += 1
        all_new_decisions.append(decisions_df)
        all_new_trades.append(rebalance_df)
        latest_positions_df = positions_df
        latest_snapshot_df = snapshot_df
        latest_excluded_df = excluded_df
        append_csv(EQUITY_PATH, pd.DataFrame([latest_equity_row]))

    if all_new_decisions:
        append_csv(DECISIONS_PATH, pd.concat(all_new_decisions, ignore_index=True))
    if all_new_trades:
        append_csv(TRADES_PATH, pd.concat(all_new_trades, ignore_index=True))
    if not latest_positions_df.empty:
        normalize_for_csv(latest_positions_df).to_csv(POSITIONS_PATH, index=False)
    else:
        pd.DataFrame(columns=["signal_date_utc", "symbol", "side", "weight", "quantity", "entry_price", "mark_price", "decision_reason"]).to_csv(POSITIONS_PATH, index=False)
    if not latest_snapshot_df.empty:
        normalize_for_csv(latest_snapshot_df).to_csv(SNAPSHOT_PATH, index=False)
    else:
        pd.DataFrame().to_csv(SNAPSHOT_PATH, index=False)
    if not latest_excluded_df.empty:
        normalize_for_csv(latest_excluded_df).to_csv(EXCLUDED_PATH, index=False)
    else:
        pd.DataFrame().to_csv(EXCLUDED_PATH, index=False)

    save_state(state)
    status = write_status(state, latest_equity_row)
    write_report(status)

    summary = {
        "run_at_utc": iso_z(utc_now()),
        "mode": "init_from_now" if args.init_from_now else "refresh",
        "latest_signal_date_utc": state.get("last_signal_date_utc"),
        "new_signal_dates_processed": processed,
        "current_equity_usd": state.get("current_equity"),
        "scheduler_attached": state.get("scheduler_attached", False),
        "scheduler_unit": state.get("scheduler_unit", ""),
        "status_path": str(STATUS_PATH.relative_to(ROOT)),
        "state_path": str(STATE_PATH.relative_to(ROOT)),
        "equity_curve_path": str(EQUITY_PATH.relative_to(ROOT)),
        "decisions_path": str(DECISIONS_PATH.relative_to(ROOT)),
        "rebalance_trades_path": str(TRADES_PATH.relative_to(ROOT)),
        "positions_path": str(POSITIONS_PATH.relative_to(ROOT)),
        "report_path": str(REPORT_PATH.relative_to(ROOT)),
    }
    RUN_SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank 154 honest daily paper runner")
    parser.add_argument("--init-from-now", action="store_true", help="Initialize the runner from the latest completed daily bar and create the first paper portfolio.")
    parser.add_argument("--refresh", action="store_true", help="Process any newly completed daily bar since the stored watermark.")
    parser.add_argument("--force-reinit", action="store_true", help="Allow reinitialization even if state already exists.")
    parser.add_argument("--scheduler-attached", action="store_true", help="Mark the runner as scheduler-owned.")
    parser.add_argument("--scheduler-unit", default="", help="Owning timer/service unit name.")
    args = parser.parse_args()

    if args.init_from_now == args.refresh:
        parser.error("choose exactly one of --init-from-now or --refresh")

    summary = init_or_refresh(args)
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
