#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from paper_runner_utils import (
    ROOT,
    ensure_dir,
    fetch_binance_futures_book,
    fetch_binance_futures_klines,
    iso_z,
    read_csv_or_empty,
    utc_now,
    write_json,
)

ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank201_utc_clock_low_switch"
LEDGER_PATH = ART_DIR / "rank201_closed_trades.csv"
STATUS_PATH = ART_DIR / "rank201_status.csv"
STATE_PATH = ART_DIR / "rank201_state.json"
RUN_SUMMARY_PATH = ART_DIR / "rank201_last_run_summary.json"
SLEEVE_PATH = ART_DIR / "rank201_daily_schedule.csv"
MARKOUT_PATH = ART_DIR / "rank201_recent_markouts.csv"
HTML_PATH = ROOT / "reports" / "site" / "paper" / "rank201_utc_clock_low_switch.html"

CANDIDATE_ID = "rank201_utc_clock_low_switch_schedule"
CANDIDATE_RANK = 201
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT", "LINKUSDT"]
INTERVAL = "15m"
LOOKBACK_DAYS = 120
ROUND_TRIP_COST_BPS = 8.0
ONE_WAY_COST_BPS = ROUND_TRIP_COST_BPS / 2.0
RUNNER_TIMER = "momentum-rank201-paper-refresh.timer"
RUNNER_SERVICE = "momentum-rank201-paper-refresh.service"

LONG_HOURS = {20, 21}
SHORT_HOURS = {22, 23}
ENTRY_HOURS = {20: "long", 22: "short"}
EXIT_HOURS = {22: "long", 0: "short"}


def fetch_symbol_frame(symbol: str) -> pd.DataFrame:
    end = utc_now().replace(minute=0, second=0, microsecond=0) + pd.Timedelta(days=1)
    start = end - pd.Timedelta(days=LOOKBACK_DAYS)
    df = fetch_binance_futures_klines(symbol, INTERVAL, int(start.timestamp() * 1000), int(end.timestamp() * 1000))
    if df.empty:
        raise RuntimeError(f"no 15m futures candles fetched for {symbol}")
    df = df.sort_values("ts").reset_index(drop=True)
    df["symbol"] = symbol
    df["hour"] = df["ts"].dt.hour
    df["minute"] = df["ts"].dt.minute
    df["date_utc"] = df["ts"].dt.strftime("%Y-%m-%d")
    return df


def build_closed_trades(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for trade_date in sorted(df["date_utc"].dropna().unique()):
        day_df = df[df["date_utc"] == trade_date].copy()
        if day_df.empty:
            continue
        long_entry = day_df[(day_df["hour"] == 20) & (day_df["minute"] == 0)]
        long_exit = day_df[(day_df["hour"] == 22) & (day_df["minute"] == 0)]
        short_entry = long_exit
        next_day_short_exit = df[(df["ts"] == (pd.Timestamp(trade_date, tz="UTC") + pd.Timedelta(days=1)))]
        if not long_entry.empty and not long_exit.empty:
            e = long_entry.iloc[0]
            x = long_exit.iloc[0]
            gross_ret = float(x["open"] / e["open"] - 1.0)
            net_ret = gross_ret - ONE_WAY_COST_BPS / 10000.0 - ONE_WAY_COST_BPS / 10000.0
            rows.append({
                "trade_id": f"{symbol_slug(df)}|{trade_date}|long20_22",
                "candidate_id": CANDIDATE_ID,
                "candidate_rank": CANDIDATE_RANK,
                "symbol": str(e["symbol"]),
                "signal_family": "utc_clock_low_switch",
                "venue_mode": "binance_usdt_perp_paper",
                "entry_ts": e["ts"],
                "exit_ts": x["ts"],
                "side": "long",
                "entry_price": float(e["open"]),
                "exit_price": float(x["open"]),
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "gross_bps": gross_ret * 10000.0,
                "net_bps": net_ret * 10000.0,
                "round_trip_cost_bps": ROUND_TRIP_COST_BPS,
                "sleeve": "20_22_long",
            })
        short_exit_ts = pd.Timestamp(trade_date, tz="UTC") + pd.Timedelta(days=1)
        short_exit = df[df["ts"] == short_exit_ts]
        if not short_entry.empty and not short_exit.empty:
            e = short_entry.iloc[0]
            x = short_exit.iloc[0]
            gross_ret = float(e["open"] / x["open"] - 1.0)
            net_ret = gross_ret - ONE_WAY_COST_BPS / 10000.0 - ONE_WAY_COST_BPS / 10000.0
            rows.append({
                "trade_id": f"{symbol_slug(df)}|{trade_date}|short22_00",
                "candidate_id": CANDIDATE_ID,
                "candidate_rank": CANDIDATE_RANK,
                "symbol": str(e["symbol"]),
                "signal_family": "utc_clock_low_switch",
                "venue_mode": "binance_usdt_perp_paper",
                "entry_ts": e["ts"],
                "exit_ts": x["ts"],
                "side": "short",
                "entry_price": float(e["open"]),
                "exit_price": float(x["open"]),
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "gross_bps": gross_ret * 10000.0,
                "net_bps": net_ret * 10000.0,
                "round_trip_cost_bps": ROUND_TRIP_COST_BPS,
                "sleeve": "22_00_short",
            })
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out = out.sort_values(["entry_ts", "symbol", "side"]).reset_index(drop=True)
    return out


def symbol_slug(df: pd.DataFrame) -> str:
    return str(df["symbol"].iloc[0]).lower()


def build_markout(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows: list[dict] = []
    for symbol, df in frames.items():
        tail = df.tail(32).copy()
        for _, row in tail.iterrows():
            hour = int(row["hour"])
            sleeve = "flat"
            target_side = "flat"
            if hour in LONG_HOURS:
                sleeve = "20_22_long"
                target_side = "long"
            elif hour in SHORT_HOURS:
                sleeve = "22_00_short"
                target_side = "short"
            rows.append({
                "ts": row["ts"],
                "symbol": symbol,
                "open": float(row["open"]),
                "close": float(row["close"]),
                "hour": hour,
                "sleeve": sleeve,
                "target_side": target_side,
            })
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values(["ts", "symbol"]).reset_index(drop=True)


def current_position(frames: dict[str, pd.DataFrame]) -> tuple[dict, list[dict]]:
    latest_ts = min(df["ts"].iloc[-1] for df in frames.values())
    hour = int(pd.Timestamp(latest_ts).hour)
    minute = int(pd.Timestamp(latest_ts).minute)
    side = "flat"
    exit_ts = None
    reason = "outside configured UTC sleeves"
    if hour in LONG_HOURS:
        side = "long"
        exit_ts = pd.Timestamp(latest_ts).normalize() + pd.Timedelta(hours=22)
        reason = "within fixed UTC long sleeve 20:00-21:59"
    elif hour in SHORT_HOURS:
        side = "short"
        exit_ts = pd.Timestamp(latest_ts).normalize() + pd.Timedelta(days=1 if hour == 23 else 0, hours=24 if hour == 23 else 0)
        if hour == 22:
            exit_ts = pd.Timestamp(latest_ts).normalize() + pd.Timedelta(days=1)
        reason = "within fixed UTC short sleeve 22:00-23:59"
    legs = []
    for symbol, df in frames.items():
        row = df[df["ts"] == latest_ts]
        if row.empty:
            row = df.tail(1)
        r = row.iloc[0]
        book = fetch_binance_futures_book(symbol, limit=5)
        bid = float(book["bids"][0][0]) if book.get("bids") else None
        ask = float(book["asks"][0][0]) if book.get("asks") else None
        spread_bps = None
        if bid and ask:
            mid = (bid + ask) / 2.0
            spread_bps = ((ask - bid) / mid) * 10000.0
        legs.append({
            "symbol": symbol,
            "bar_ts": iso_z(r["ts"]),
            "mark_close": float(r["close"]),
            "book_bid": bid,
            "book_ask": ask,
            "book_spread_bps": spread_bps,
            "side": side,
            "weight": 1.0 / len(frames) if side != "flat" else 0.0,
        })
    snap = {
        "latest_ts": latest_ts,
        "latest_hour_utc": hour,
        "latest_minute_utc": minute,
        "open_position_side": side,
        "planned_exit_ts": exit_ts,
        "reason": reason,
    }
    return snap, legs


def write_html(status: dict, state: dict, legs: list[dict], recent_trades: pd.DataFrame) -> None:
    ensure_dir(HTML_PATH.parent)
    legs_df = pd.DataFrame(legs)
    recent = recent_trades.tail(16).copy() if not recent_trades.empty else pd.DataFrame()
    body = f"""<!doctype html>
<html lang=\"zh\">
<head>
  <meta charset=\"utf-8\" />
  <title>Rank 201 Paper Runner</title>
  <style>body{{font-family:Arial,sans-serif;margin:24px;line-height:1.5}}code{{background:#f3f3f3;padding:2px 4px}}table{{border-collapse:collapse}}td,th{{border:1px solid #ddd;padding:6px 8px}}</style>
</head>
<body>
  <h1>Rank 201 / UTC clock seasonality low-switch schedule</h1>
  <p><strong>接线状态：</strong>{status['wiring_status']}</p>
  <ul>
    <li>runner: <code>{status['runner_script']}</code></li>
    <li>service: <code>{status['service_unit']}</code></li>
    <li>timer: <code>{status['timer_unit']}</code></li>
    <li>最近更新时间: <code>{status['updated_at_utc']}</code></li>
    <li>宇宙: <code>{', '.join(status['symbols'])}</code></li>
    <li>固定 sleeve: <code>20~21 UTC long / 22~23 UTC short</code></li>
    <li>闭合交易数: <code>{status['closed_trades']}</code></li>
    <li>累计净收益: <code>{status['lifetime_total_return']:.4%}</code></li>
    <li>近 30 天净收益: <code>{status['recent_30d_total_return']:.4%}</code></li>
    <li>当前仓位: <code>{state['open_position']['side']}</code></li>
    <li>计划平仓时间: <code>{state['open_position'].get('planned_exit_ts', 'n/a')}</code></li>
  </ul>
  <h2>当前腿快照</h2>
  {legs_df.to_html(index=False) if not legs_df.empty else '<p>暂无腿信息</p>'}
  <h2>最近闭合交易</h2>
  {recent.to_html(index=False) if not recent.empty else '<p>暂无闭合交易</p>'}
</body>
</html>
"""
    HTML_PATH.write_text(body, encoding="utf-8")


def main() -> int:
    ensure_dir(ART_DIR)
    frames = {symbol: fetch_symbol_frame(symbol) for symbol in SYMBOLS}
    trades = pd.concat([build_closed_trades(df) for df in frames.values()], ignore_index=True)
    if not trades.empty:
        trades = trades.drop_duplicates(subset=["trade_id"], keep="last").sort_values(["entry_ts", "symbol", "side"]).reset_index(drop=True)
        trades_for_csv = trades.copy()
        for col in ["entry_ts", "exit_ts"]:
            trades_for_csv[col] = pd.to_datetime(trades_for_csv[col], utc=True).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        trades_for_csv.to_csv(LEDGER_PATH, index=False)
    else:
        read_csv_or_empty(LEDGER_PATH)

    markout = build_markout(frames)
    if not markout.empty:
        markout_for_csv = markout.copy()
        markout_for_csv["ts"] = pd.to_datetime(markout_for_csv["ts"], utc=True).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        markout_for_csv.to_csv(MARKOUT_PATH, index=False)

    schedule_rows = []
    for symbol in SYMBOLS:
        schedule_rows.extend([
            {"symbol": symbol, "sleeve": "20_22_long", "start_utc": "20:00", "end_utc": "22:00", "side": "long", "weight": 1.0 / len(SYMBOLS)},
            {"symbol": symbol, "sleeve": "22_00_short", "start_utc": "22:00", "end_utc": "00:00", "side": "short", "weight": 1.0 / len(SYMBOLS)},
        ])
    pd.DataFrame(schedule_rows).to_csv(SLEEVE_PATH, index=False)

    snapshot, legs = current_position(frames)

    if trades.empty:
        lifetime_total_return = 0.0
        recent_30d_total_return = 0.0
        mean_net_bps = 0.0
        win_rate = 0.0
    else:
        lifetime_total_return = float((1.0 + trades["net_ret"]).prod() - 1.0)
        recent_cut = pd.Timestamp(utc_now()) - pd.Timedelta(days=30)
        recent = trades[pd.to_datetime(trades["exit_ts"], utc=True) >= recent_cut].copy()
        recent_30d_total_return = float((1.0 + recent["net_ret"]).prod() - 1.0) if not recent.empty else 0.0
        mean_net_bps = float(trades["net_bps"].mean())
        win_rate = float((trades["net_bps"] > 0).mean())

    status = {
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "stage": "paper_runner_live",
        "wiring_status": "connected_runner_live",
        "runner_script": "scripts/run_rank201_utc_clock_paper_runner.py",
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "refresh_cadence": "15m",
        "signal_timeframe": "15m",
        "venue_signal": "Binance USDⓈ-M perp 15m",
        "venue_execution": "8-asset equal-weight perp paper sleeve",
        "symbols": SYMBOLS,
        "selection_rule": "fixed UTC sleeves: long 20:00-21:59, short 22:00-23:59",
        "round_trip_cost_bps": ROUND_TRIP_COST_BPS,
        "latest_ts": iso_z(snapshot["latest_ts"]),
        "open_position_side": snapshot["open_position_side"],
        "planned_exit_ts": iso_z(snapshot["planned_exit_ts"]) if snapshot.get("planned_exit_ts") is not None else None,
        "closed_trades": int(len(trades)),
        "mean_net_bps": mean_net_bps,
        "win_rate": win_rate,
        "lifetime_total_return": lifetime_total_return,
        "recent_30d_total_return": recent_30d_total_return,
        "updated_at_utc": iso_z(utc_now()),
        "note": "wired: dedicated runner + systemd timer live; Rank 201 now runs as an 8-asset 15m UTC clock sleeve (20~21 UTC long / 22~23 UTC short).",
    }
    pd.DataFrame([status]).to_csv(STATUS_PATH, index=False)

    state = {
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "wiring_status": "connected_runner_live",
        "runner_script": str((ROOT / "scripts" / "run_rank201_utc_clock_paper_runner.py").relative_to(ROOT)),
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "last_run_at_utc": iso_z(utc_now()),
        "latest_signal_ts": iso_z(snapshot["latest_ts"]),
        "schedule": {
            "long_hours_utc": [20, 21],
            "short_hours_utc": [22, 23],
            "symbols": SYMBOLS,
            "timeframe": INTERVAL,
        },
        "open_position": {
            "side": snapshot["open_position_side"],
            "planned_exit_ts": iso_z(snapshot["planned_exit_ts"]) if snapshot.get("planned_exit_ts") is not None else None,
            "reason": snapshot["reason"],
            "legs": legs,
        },
        "closed_trades": int(len(trades)),
        "lifetime_total_return": lifetime_total_return,
        "recent_30d_total_return": recent_30d_total_return,
    }
    write_json(STATE_PATH, state)
    write_html(status, state, legs, trades)

    summary = {
        "run_at_utc": iso_z(utc_now()),
        "runner": "rank201_utc_clock_paper_runner",
        "closed_trades_total": int(len(trades)),
        "open_position_side": snapshot["open_position_side"],
        "planned_exit_ts": iso_z(snapshot["planned_exit_ts"]) if snapshot.get("planned_exit_ts") is not None else None,
        "status_path": str(STATUS_PATH.relative_to(ROOT)),
        "ledger_path": str(LEDGER_PATH.relative_to(ROOT)),
        "state_path": str(STATE_PATH.relative_to(ROOT)),
        "html_path": str(HTML_PATH.relative_to(ROOT)),
        "schedule_path": str(SLEEVE_PATH.relative_to(ROOT)),
        "recent_markout_path": str(MARKOUT_PATH.relative_to(ROOT)),
    }
    write_json(RUN_SUMMARY_PATH, summary)
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
