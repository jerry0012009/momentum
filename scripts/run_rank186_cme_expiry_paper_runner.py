#!/usr/bin/env python3
from __future__ import annotations

import calendar
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

from paper_runner_utils import (
    ROOT,
    ensure_dir,
    fetch_binance_futures_book,
    fetch_binance_futures_klines,
    iso_z,
    normalize_for_csv,
    read_csv_or_empty,
    read_json,
    utc_now,
    write_json,
)

ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank186_cme_expiry"
CACHE_DIR = ART_DIR / "cache"
LEDGER_PATH = ART_DIR / "rank186_closed_trades.csv"
STATUS_PATH = ART_DIR / "rank186_status.csv"
STATE_PATH = ART_DIR / "rank186_state.json"
RUN_SUMMARY_PATH = ART_DIR / "rank186_last_run_summary.json"
EVENTS_PATH = ART_DIR / "rank186_events.csv"
HTML_PATH = ROOT / "reports" / "site" / "paper" / "rank186_cme_expiry.html"

CANDIDATE_ID = "rank186_cme_expiry_postfix_short_btc"
CANDIDATE_RANK = 186
SYMBOL = "BTCUSDT"
ENTRY_DELAY_MIN = 5
EXIT_DELAY_MIN = 120
COST_RT_BPS = 10.0
RUNNER_TIMER = "momentum-rank186-paper-refresh.timer"
RUNNER_SERVICE = "momentum-rank186-paper-refresh.service"
LONDON = ZoneInfo("Europe/London")
KLINE_INTERVAL = "1m"
PRE_EVENT_MONITOR_MIN = 10
POST_EXIT_MONITOR_MIN = 5
BOOK_REFRESH_MIN = 5


def last_friday_event(year: int, month: int) -> datetime:
    cal = calendar.monthcalendar(year, month)
    friday_col = calendar.FRIDAY
    fridays = [week[friday_col] for week in cal if week[friday_col] != 0]
    last_friday = fridays[-1]
    london_dt = datetime(year, month, last_friday, 16, 0, tzinfo=LONDON)
    return london_dt.astimezone(timezone.utc)


def month_iter(start_year: int, start_month: int, end_year: int, end_month: int):
    year, month = start_year, start_month
    while (year, month) <= (end_year, end_month):
        yield year, month
        month += 1
        if month == 13:
            year += 1
            month = 1


def month_key(event_utc: datetime) -> str:
    return event_utc.strftime("%Y_%m")


def minute_floor(ts: datetime) -> datetime:
    return ts.astimezone(timezone.utc).replace(second=0, microsecond=0)


def event_window_bounds(event_utc: datetime) -> tuple[datetime, datetime]:
    start = event_utc - timedelta(minutes=2)
    end = event_utc + timedelta(minutes=EXIT_DELAY_MIN + POST_EXIT_MONITOR_MIN)
    return start, end


def cache_path_for_event(event_utc: datetime) -> Path:
    return CACHE_DIR / f"rank186_event_window_{month_key(event_utc)}.csv"


def load_cached_window(event_utc: datetime) -> pd.DataFrame:
    path = cache_path_for_event(event_utc)
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame(columns=["ts", "open", "high", "low", "close", "volume", "close_ts"])
    df = pd.read_csv(path)
    if df.empty:
        return df
    for col in ["ts", "close_ts"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], utc=True)
    return df.sort_values("ts").drop_duplicates(subset=["ts"]).reset_index(drop=True)


def save_cached_window(event_utc: datetime, df: pd.DataFrame) -> None:
    ensure_dir(CACHE_DIR)
    out = df.copy()
    for col in ["ts", "close_ts"]:
        if col in out.columns:
            out[col] = pd.to_datetime(out[col], utc=True).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    out.to_csv(cache_path_for_event(event_utc), index=False)


def price_from_close(df: pd.DataFrame, ts: datetime) -> float | None:
    row = df.loc[df["ts"] == pd.Timestamp(ts)]
    if row.empty:
        return None
    return float(row.iloc[0]["close"])


def window_complete_for_closed_trade(df: pd.DataFrame, event_utc: datetime) -> bool:
    if df.empty:
        return False
    entry_utc = event_utc + timedelta(minutes=ENTRY_DELAY_MIN)
    exit_utc = event_utc + timedelta(minutes=EXIT_DELAY_MIN)
    return price_from_close(df, entry_utc) is not None and price_from_close(df, exit_utc) is not None


def is_active_monitor_window(event_utc: datetime, now_utc: datetime) -> bool:
    monitor_start = event_utc - timedelta(minutes=PRE_EVENT_MONITOR_MIN)
    monitor_end = event_utc + timedelta(minutes=EXIT_DELAY_MIN + POST_EXIT_MONITOR_MIN)
    return monitor_start <= now_utc <= monitor_end


def fetch_incremental_window(event_utc: datetime, now_utc: datetime, force_full: bool = False) -> tuple[pd.DataFrame, dict]:
    start_utc, end_utc = event_window_bounds(event_utc)
    cache = load_cached_window(event_utc)
    stats = {
        "cache_path": str(cache_path_for_event(event_utc).relative_to(ROOT)),
        "cache_rows_before": int(len(cache)),
        "network_calls": 0,
        "fetch_mode": "cache_hit",
        "fetch_start_utc": None,
        "fetch_end_utc": None,
        "cache_rows_after": int(len(cache)),
    }

    fetch_end = end_utc if force_full else min(end_utc, minute_floor(now_utc))
    if fetch_end < start_utc:
        stats["fetch_mode"] = "pre_window_skip"
        return cache, stats

    if force_full or cache.empty:
        fetch_start = start_utc
    else:
        last_cached_ts = pd.to_datetime(cache["ts"], utc=True).max().to_pydatetime()
        fetch_start = max(start_utc, last_cached_ts + timedelta(minutes=1))

    if fetch_start <= fetch_end:
        fetched = fetch_binance_futures_klines(
            SYMBOL,
            KLINE_INTERVAL,
            int(fetch_start.timestamp() * 1000),
            int(fetch_end.timestamp() * 1000) + 60_000,
        )
        stats["network_calls"] = 1
        stats["fetch_start_utc"] = iso_z(fetch_start)
        stats["fetch_end_utc"] = iso_z(fetch_end)
        stats["fetch_mode"] = "full_seed" if cache.empty or force_full else "incremental_append"
        if not fetched.empty:
            if cache.empty:
                combined = fetched.copy()
            else:
                combined = pd.concat([cache, fetched], ignore_index=True)
            combined = combined.sort_values("ts").drop_duplicates(subset=["ts"]).reset_index(drop=True)
            cache = combined
            save_cached_window(event_utc, cache)
    stats["cache_rows_after"] = int(len(cache))
    return cache, stats


def closed_month_trade_rows(now_utc: datetime) -> tuple[pd.DataFrame, dict]:
    rows: list[dict] = []
    total_network_calls = 0
    cache_reuse_months = 0
    seeded_months = 0
    skipped_months = 0
    for year, month in month_iter(2025, 1, now_utc.year, now_utc.month):
        event_utc = last_friday_event(year, month)
        exit_utc = event_utc + timedelta(minutes=EXIT_DELAY_MIN)
        if now_utc < exit_utc + timedelta(minutes=1):
            continue
        cache = load_cached_window(event_utc)
        if window_complete_for_closed_trade(cache, event_utc):
            cache_reuse_months += 1
            window = cache
        else:
            window, fetch_stats = fetch_incremental_window(event_utc, now_utc, force_full=True)
            total_network_calls += int(fetch_stats["network_calls"])
            seeded_months += 1 if fetch_stats["network_calls"] > 0 else 0
        entry_utc = event_utc + timedelta(minutes=ENTRY_DELAY_MIN)
        exit_price_ts = event_utc + timedelta(minutes=EXIT_DELAY_MIN)
        entry_price = price_from_close(window, entry_utc)
        exit_price = price_from_close(window, exit_price_ts)
        if entry_price is None or exit_price is None:
            skipped_months += 1
            continue
        gross_ret = (entry_price - exit_price) / entry_price
        net_ret = gross_ret - (COST_RT_BPS / 10000.0)
        rows.append(
            {
                "trade_id": f"{year:04d}-{month:02d}|{iso_z(event_utc)}",
                "candidate_id": CANDIDATE_ID,
                "candidate_rank": CANDIDATE_RANK,
                "event_month": f"{year:04d}-{month:02d}",
                "event_ts": event_utc,
                "entry_ts": entry_utc,
                "exit_ts": exit_price_ts,
                "side": "short_btc",
                "entry_price": entry_price,
                "exit_price": exit_price,
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "gross_bps": gross_ret * 10000.0,
                "net_bps": net_ret * 10000.0,
                "cost_rt_bps": COST_RT_BPS,
                "entry_delay_min": ENTRY_DELAY_MIN,
                "exit_delay_min": EXIT_DELAY_MIN,
                "timezone_ref": "Europe/London",
            }
        )
    return pd.DataFrame(rows), {
        "closed_month_network_calls": total_network_calls,
        "closed_month_cache_reuse": cache_reuse_months,
        "closed_month_seeded": seeded_months,
        "closed_month_skipped": skipped_months,
    }


def current_or_next_event(now_utc: datetime) -> tuple[datetime, datetime, datetime]:
    event = last_friday_event(now_utc.year, now_utc.month)
    if now_utc > event + timedelta(minutes=EXIT_DELAY_MIN + POST_EXIT_MONITOR_MIN):
        year, month = now_utc.year, now_utc.month + 1
        if month == 13:
            year += 1
            month = 1
        event = last_friday_event(year, month)
    return event, event + timedelta(minutes=ENTRY_DELAY_MIN), event + timedelta(minutes=EXIT_DELAY_MIN)


def maybe_active_position(event_utc: datetime, now_utc: datetime) -> tuple[dict | None, dict]:
    if not is_active_monitor_window(event_utc, now_utc):
        return None, {
            "live_window_mode": "idle_outside_event_window",
            "live_window_network_calls": 0,
            "live_window_fetch_mode": "skip",
            "live_window_fetch_start_utc": None,
            "live_window_fetch_end_utc": None,
            "live_window_cache_path": str(cache_path_for_event(event_utc).relative_to(ROOT)),
        }

    window, fetch_stats = fetch_incremental_window(event_utc, now_utc, force_full=False)
    entry_utc = event_utc + timedelta(minutes=ENTRY_DELAY_MIN)
    exit_utc = event_utc + timedelta(minutes=EXIT_DELAY_MIN)
    if not (entry_utc <= now_utc < exit_utc):
        return None, {
            "live_window_mode": "watch_only_pre_or_post_position",
            "live_window_network_calls": int(fetch_stats["network_calls"]),
            "live_window_fetch_mode": fetch_stats["fetch_mode"],
            "live_window_fetch_start_utc": fetch_stats["fetch_start_utc"],
            "live_window_fetch_end_utc": fetch_stats["fetch_end_utc"],
            "live_window_cache_path": fetch_stats["cache_path"],
        }

    entry_price = price_from_close(window, entry_utc)
    if entry_price is None or window.empty:
        return None, {
            "live_window_mode": "watch_only_entry_bar_missing",
            "live_window_network_calls": int(fetch_stats["network_calls"]),
            "live_window_fetch_mode": fetch_stats["fetch_mode"],
            "live_window_fetch_start_utc": fetch_stats["fetch_start_utc"],
            "live_window_fetch_end_utc": fetch_stats["fetch_end_utc"],
            "live_window_cache_path": fetch_stats["cache_path"],
        }

    current_price = float(window.iloc[-1]["close"])
    current_ts = pd.Timestamp(window.iloc[-1]["ts"])
    gross_ret = (entry_price - current_price) / entry_price
    return {
        "side": "short_btc",
        "event_ts": event_utc,
        "entry_ts": entry_utc,
        "planned_exit_ts": exit_utc,
        "entry_price": entry_price,
        "current_ts": current_ts,
        "current_price": current_price,
        "gross_mtm_bps": gross_ret * 10000.0,
        "net_mtm_bps_after_rt_cost": (gross_ret - COST_RT_BPS / 10000.0) * 10000.0,
    }, {
        "live_window_mode": "active_incremental_monitor",
        "live_window_network_calls": int(fetch_stats["network_calls"]),
        "live_window_fetch_mode": fetch_stats["fetch_mode"],
        "live_window_fetch_start_utc": fetch_stats["fetch_start_utc"],
        "live_window_fetch_end_utc": fetch_stats["fetch_end_utc"],
        "live_window_cache_path": fetch_stats["cache_path"],
    }


def maybe_book_snapshot(event_utc: datetime, now_utc: datetime, previous_state: dict) -> tuple[dict, str]:
    previous_book = previous_state.get("last_book_snapshot") if isinstance(previous_state, dict) else {}
    previous_book_ts = None
    if isinstance(previous_book, dict):
        previous_book_ts = pd.to_datetime(previous_book.get("updated_at_utc"), utc=True) if previous_book.get("updated_at_utc") else None
    if not is_active_monitor_window(event_utc, now_utc):
        return previous_book if isinstance(previous_book, dict) else {}, "skip_outside_event_window"
    if previous_book_ts is not None and now_utc - previous_book_ts.to_pydatetime() < timedelta(minutes=BOOK_REFRESH_MIN):
        return previous_book if isinstance(previous_book, dict) else {}, "reuse_recent_snapshot"
    try:
        book = fetch_binance_futures_book(SYMBOL, limit=5)
        best_bid = float(book["bids"][0][0]) if book.get("bids") else None
        best_ask = float(book["asks"][0][0]) if book.get("asks") else None
        top_spread_bps = ((best_ask - best_bid) / ((best_ask + best_bid) / 2.0)) * 10000.0 if best_bid and best_ask else None
        snapshot = {
            "best_bid": best_bid,
            "best_ask": best_ask,
            "top_spread_bps": top_spread_bps,
            "updated_at_utc": iso_z(now_utc),
            "error": None,
        }
        return snapshot, "live_fetch"
    except Exception as exc:  # noqa: BLE001
        snapshot = previous_book if isinstance(previous_book, dict) else {}
        if not snapshot:
            snapshot = {"best_bid": None, "best_ask": None, "top_spread_bps": None}
        snapshot["updated_at_utc"] = iso_z(now_utc)
        snapshot["error"] = str(exc)
        return snapshot, "fetch_error_reuse"


def write_html(status: dict, open_position: dict | None) -> None:
    ensure_dir(HTML_PATH.parent)
    body = f"""<!doctype html>
<html lang=\"zh\">
<head>
  <meta charset=\"utf-8\" />
  <title>Rank 186 Paper Runner</title>
  <style>body{{font-family:Arial,sans-serif;margin:24px;line-height:1.5}}code{{background:#f3f3f3;padding:2px 4px}}</style>
</head>
<body>
  <h1>Rank 186 / CME expiry postfix short BTC</h1>
  <p><strong>接线状态：</strong>{status['wiring_status']}</p>
  <ul>
    <li>runner: <code>{status['runner_script']}</code></li>
    <li>service: <code>{status['service_unit']}</code></li>
    <li>timer: <code>{status['timer_unit']}</code></li>
    <li>事件时钟: <code>last Friday 16:00 Europe/London</code></li>
    <li>标准执行: <code>+{ENTRY_DELAY_MIN}m entry / +{EXIT_DELAY_MIN}m exit</code></li>
    <li>调度策略: <code>{status['scheduler_policy']}</code></li>
    <li>实时拉数策略: <code>{status['kline_poll_policy']}</code></li>
    <li>最近更新时间: <code>{status['updated_at_utc']}</code></li>
    <li>闭合交易数: <code>{status['closed_trades']}</code></li>
    <li>累计净收益: <code>{status['lifetime_total_return']:.4%}</code></li>
  </ul>
  <h2>当前仓位</h2>
  <pre>{json.dumps(open_position or {'side': 'flat'}, ensure_ascii=False, indent=2, default=str)}</pre>
</body>
</html>
"""
    HTML_PATH.write_text(body, encoding="utf-8")


def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(CACHE_DIR)
    now_utc = minute_floor(utc_now())
    previous_state = read_json(STATE_PATH, default={})

    trades, history_stats = closed_month_trade_rows(now_utc)
    prior_ledger = read_csv_or_empty(LEDGER_PATH)
    prior_ids = set(prior_ledger["trade_id"].astype(str)) if not prior_ledger.empty and "trade_id" in prior_ledger.columns else set()
    new_rows = trades[~trades["trade_id"].isin(prior_ids)].copy() if not trades.empty else pd.DataFrame()
    ledger = normalize_for_csv(trades)
    if not ledger.empty:
        ledger = ledger.drop_duplicates(subset=["trade_id"], keep="last")
        ledger.to_csv(LEDGER_PATH, index=False)

    next_event, next_entry, next_exit = current_or_next_event(now_utc)
    open_position, live_stats = maybe_active_position(next_event, now_utc)
    book_snapshot, book_mode = maybe_book_snapshot(next_event, now_utc, previous_state)
    lifetime_total_return = float((1.0 + trades["net_ret"]).prod() - 1.0) if not trades.empty else 0.0
    total_network_calls = int(history_stats["closed_month_network_calls"]) + int(live_stats["live_window_network_calls"]) + (1 if book_mode == "live_fetch" else 0)

    status = {
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "stage": "paper_runner_live",
        "wiring_status": "connected_runner_live",
        "runner_script": "scripts/run_rank186_cme_expiry_paper_runner.py",
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "refresh_cadence": "1m scheduler / adaptive incremental polling",
        "scheduler_policy": "keep 1m timer for exact-time event freshness, but no minute-by-minute kline pull outside the live event window",
        "kline_poll_policy": f"historical months cache-once; live month incremental 1m only inside [{PRE_EVENT_MONITOR_MIN}m pre-event, +{EXIT_DELAY_MIN + POST_EXIT_MONITOR_MIN}m post-event] window",
        "event_clock": "last Friday 16:00 Europe/London",
        "entry_delay_min": ENTRY_DELAY_MIN,
        "exit_delay_min": EXIT_DELAY_MIN,
        "cost_rt_bps": COST_RT_BPS,
        "closed_trades": int(len(trades)),
        "new_closed_trades_appended": int(len(new_rows)),
        "mean_net_bps": float(trades["net_bps"].mean()) if not trades.empty else 0.0,
        "win_rate": float((trades["net_bps"] > 0).mean()) if not trades.empty else 0.0,
        "lifetime_total_return": lifetime_total_return,
        "next_event_utc": iso_z(next_event),
        "next_entry_utc": iso_z(next_entry),
        "next_exit_utc": iso_z(next_exit),
        "current_position_side": open_position["side"] if open_position else "flat",
        "top_book_spread_bps": book_snapshot.get("top_spread_bps"),
        "book_error": book_snapshot.get("error"),
        "book_mode": book_mode,
        "live_window_mode": live_stats["live_window_mode"],
        "history_cache_reuse_months": history_stats["closed_month_cache_reuse"],
        "history_seeded_months": history_stats["closed_month_seeded"],
        "history_skipped_months": history_stats["closed_month_skipped"],
        "closed_month_network_calls": history_stats["closed_month_network_calls"],
        "live_window_network_calls": live_stats["live_window_network_calls"],
        "total_network_calls_this_run": total_network_calls,
        "updated_at_utc": iso_z(now_utc),
        "note": "incrementalized: no longer refetches all months every minute; historical windows are cached, and live month only appends 1m bars inside the actual event-monitor window.",
    }
    events_df = pd.DataFrame(
        [
            {
                "reference": "current_or_next",
                "event_ts": iso_z(next_event),
                "entry_ts": iso_z(next_entry),
                "exit_ts": iso_z(next_exit),
                "live_window_mode": live_stats["live_window_mode"],
            }
        ]
    )
    events_df.to_csv(EVENTS_PATH, index=False)
    pd.DataFrame([status]).to_csv(STATUS_PATH, index=False)
    state = {
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "wiring_status": "connected_runner_live",
        "runner_script": str((ROOT / "scripts" / "run_rank186_cme_expiry_paper_runner.py").relative_to(ROOT)),
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "last_run_at_utc": iso_z(now_utc),
        "next_event_utc": iso_z(next_event),
        "open_position": {k: (iso_z(v) if isinstance(v, pd.Timestamp) else iso_z(v) if isinstance(v, datetime) else v) for k, v in (open_position or {}).items()},
        "closed_trades": int(len(trades)),
        "lifetime_total_return": lifetime_total_return,
        "live_window_mode": live_stats["live_window_mode"],
        "history_cache_reuse_months": history_stats["closed_month_cache_reuse"],
        "closed_month_network_calls": history_stats["closed_month_network_calls"],
        "live_window_network_calls": live_stats["live_window_network_calls"],
        "total_network_calls_this_run": total_network_calls,
        "last_book_snapshot": book_snapshot,
        "live_window_fetch_mode": live_stats["live_window_fetch_mode"],
        "live_window_fetch_start_utc": live_stats["live_window_fetch_start_utc"],
        "live_window_fetch_end_utc": live_stats["live_window_fetch_end_utc"],
        "live_window_cache_path": live_stats["live_window_cache_path"],
    }
    write_json(STATE_PATH, state)
    write_html(status, open_position)
    summary = {
        "run_at_utc": iso_z(now_utc),
        "runner": "rank186_cme_expiry_paper_runner",
        "closed_trades_total": int(len(trades)),
        "new_closed_trades_appended": int(len(new_rows)),
        "open_position_side": open_position["side"] if open_position else "flat",
        "next_event_utc": iso_z(next_event),
        "status_path": str(STATUS_PATH.relative_to(ROOT)),
        "ledger_path": str(LEDGER_PATH.relative_to(ROOT)),
        "state_path": str(STATE_PATH.relative_to(ROOT)),
        "html_path": str(HTML_PATH.relative_to(ROOT)),
        "closed_month_network_calls": history_stats["closed_month_network_calls"],
        "live_window_network_calls": live_stats["live_window_network_calls"],
        "total_network_calls_this_run": total_network_calls,
        "live_window_mode": live_stats["live_window_mode"],
        "live_window_fetch_mode": live_stats["live_window_fetch_mode"],
        "book_mode": book_mode,
    }
    write_json(RUN_SUMMARY_PATH, summary)
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
