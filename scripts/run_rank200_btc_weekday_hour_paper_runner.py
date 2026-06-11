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
    normalize_for_csv,
    read_csv_or_empty,
    utc_now,
    write_json,
)

ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank200_btc_weekday_hour_sparse_short"
LEDGER_PATH = ART_DIR / "rank200_closed_trades.csv"
STATUS_PATH = ART_DIR / "rank200_status.csv"
STATE_PATH = ART_DIR / "rank200_state.json"
RUN_SUMMARY_PATH = ART_DIR / "rank200_last_run_summary.json"
SCHEDULE_PATH = ART_DIR / "rank200_current_bottom5_schedule.csv"
HOURLY_PATH = ART_DIR / "rank200_recent_hourly_frame.csv"
HTML_PATH = ROOT / "reports" / "site" / "paper" / "rank200_btc_weekday_hour_sparse_short.html"

CANDIDATE_ID = "rank200_btc_weekday_hour_sparse_short_schedule"
CANDIDATE_RANK = 200
SYMBOL = "BTCUSDT"
INTERVAL = "1h"
LOOKBACK_DAYS = 400
REFRESH_LOOKBACK_DAYS = 365
TOP_K = 5
HOLD_HOURS = 4
ROUND_TRIP_COST_BPS = 8.0
RUNNER_TIMER = "momentum-rank200-paper-refresh.timer"
RUNNER_SERVICE = "momentum-rank200-paper-refresh.service"


def load_hourly_frame() -> pd.DataFrame:
    end = utc_now().replace(minute=0, second=0, microsecond=0)
    start = end - pd.Timedelta(days=LOOKBACK_DAYS)
    df = fetch_binance_futures_klines(
        SYMBOL,
        INTERVAL,
        int(start.timestamp() * 1000),
        int(end.timestamp() * 1000),
    )
    if df.empty:
        raise RuntimeError("no BTCUSDT hourly futures candles fetched")
    df = df.sort_values("ts").reset_index(drop=True)
    df["ret_1h"] = df["close"].pct_change()
    df["weekday"] = df["ts"].dt.weekday
    df["hour"] = df["ts"].dt.hour
    df["month_start"] = df["ts"].dt.strftime("%Y-%m-01T00:00:00Z").pipe(pd.to_datetime, utc=True)
    return df


def build_monthly_schedule(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    months = sorted(df["month_start"].dropna().unique())
    sched_rows: list[dict] = []
    trade_rows: list[dict] = []
    for month_start in months:
        month_start = pd.Timestamp(month_start)
        train_start = month_start - pd.Timedelta(days=REFRESH_LOOKBACK_DAYS)
        train = df[(df["ts"] >= train_start) & (df["ts"] < month_start)].copy()
        month_df = df[(df["ts"] >= month_start) & (df["ts"] < month_start + pd.offsets.MonthBegin(1))].copy()
        if train.empty or month_df.empty:
            continue
        bucket_stats = (
            train.dropna(subset=["ret_1h"])
            .groupby(["weekday", "hour"], as_index=False)
            .agg(train_obs=("ret_1h", "size"), mean_ret_1h=("ret_1h", "mean"))
            .sort_values(["mean_ret_1h", "train_obs", "weekday", "hour"], ascending=[True, False, True, True])
            .head(TOP_K)
            .reset_index(drop=True)
        )
        bucket_stats["month_start"] = month_start
        sched_rows.extend(bucket_stats.to_dict("records"))
        eligible = month_df.merge(bucket_stats[["weekday", "hour"]], on=["weekday", "hour"], how="inner")
        for _, row in eligible.iterrows():
            entry_px = float(row["close"])
            exit_cutoff = row["ts"] + pd.Timedelta(hours=HOLD_HOURS)
            future = df[df["ts"] >= exit_cutoff]
            if future.empty:
                continue
            exit_row = future.iloc[0]
            exit_px = float(exit_row["close"])
            gross_ret = (entry_px - exit_px) / entry_px
            net_ret = gross_ret - ROUND_TRIP_COST_BPS / 10000.0
            trade_rows.append(
                {
                    "trade_id": f"{row['ts'].strftime('%Y%m%dT%H%M%SZ')}|{int(row['weekday'])}|{int(row['hour'])}",
                    "candidate_id": CANDIDATE_ID,
                    "candidate_rank": CANDIDATE_RANK,
                    "signal_family": "weekday_hour_event_clock",
                    "venue_mode": "binance_usdt_perp_paper",
                    "entry_ts": row["ts"],
                    "exit_ts": exit_row["ts"],
                    "side": "short",
                    "weekday": int(row["weekday"]),
                    "hour": int(row["hour"]),
                    "entry_price": entry_px,
                    "exit_price": exit_px,
                    "hold_hours": HOLD_HOURS,
                    "gross_ret": gross_ret,
                    "net_ret": net_ret,
                    "gross_bps": gross_ret * 10000.0,
                    "net_bps": net_ret * 10000.0,
                    "round_trip_cost_bps": ROUND_TRIP_COST_BPS,
                    "bucket_month_start": month_start,
                }
            )
    return pd.DataFrame(sched_rows), pd.DataFrame(trade_rows)


def live_snapshot(df: pd.DataFrame, schedule_df: pd.DataFrame) -> tuple[dict, dict | None]:
    latest = df.iloc[-1]
    current_month = latest["month_start"]
    current_sched = schedule_df[schedule_df["month_start"] == current_month].copy()
    current_sched = current_sched.sort_values(["mean_ret_1h", "train_obs", "weekday", "hour"], ascending=[True, False, True, True]).reset_index(drop=True)
    book = fetch_binance_futures_book(SYMBOL, limit=5)
    bid = float(book["bids"][0][0]) if book.get("bids") else None
    ask = float(book["asks"][0][0]) if book.get("asks") else None
    spread_bps = None
    if bid and ask:
        mid = (bid + ask) / 2.0
        spread_bps = ((ask - bid) / mid) * 10000.0

    is_active_bucket = False
    active_position = None
    for _, sched in current_sched.iterrows():
        if int(sched["weekday"]) == int(latest["weekday"]) and int(sched["hour"]) == int(latest["hour"]):
            is_active_bucket = True
            exit_eta = latest["ts"] + pd.Timedelta(hours=HOLD_HOURS)
            active_position = {
                "side": "short",
                "bucket_weekday": int(sched["weekday"]),
                "bucket_hour_utc": int(sched["hour"]),
                "entry_ts": latest["ts"],
                "entry_price": float(latest["close"]),
                "planned_exit_ts": exit_eta,
                "reason": "current closed hourly bar is one of this month bottom-5 weekday-hour weak buckets",
            }
            break

    snapshot = {
        "latest_ts": latest["ts"],
        "latest_close": float(latest["close"]),
        "latest_weekday": int(latest["weekday"]),
        "latest_hour_utc": int(latest["hour"]),
        "current_month_start": current_month,
        "current_bottom5_count": int(len(current_sched)),
        "current_bottom5_buckets": [f"{int(r['weekday'])}-{int(r['hour']):02d}" for _, r in current_sched.iterrows()],
        "book_bid": bid,
        "book_ask": ask,
        "book_spread_bps": spread_bps,
        "is_active_bucket_now": is_active_bucket,
    }
    return snapshot, active_position


def write_html(status: dict, active_position: dict | None, current_sched: pd.DataFrame) -> None:
    ensure_dir(HTML_PATH.parent)
    sched_preview = current_sched[["weekday", "hour", "train_obs", "mean_ret_1h"]].copy() if not current_sched.empty else pd.DataFrame()
    body = f"""<!doctype html>
<html lang=\"zh\">
<head>
  <meta charset=\"utf-8\" />
  <title>Rank 200 Paper Runner</title>
  <style>body{{font-family:Arial,sans-serif;margin:24px;line-height:1.5}}code{{background:#f3f3f3;padding:2px 4px}}table{{border-collapse:collapse}}td,th{{border:1px solid #ddd;padding:6px 8px}}</style>
</head>
<body>
  <h1>Rank 200 / BTC weekday-hour sparse short schedule</h1>
  <p><strong>接线状态：</strong>{status['wiring_status']}</p>
  <ul>
    <li>runner: <code>{status['runner_script']}</code></li>
    <li>service: <code>{status['service_unit']}</code></li>
    <li>timer: <code>{status['timer_unit']}</code></li>
    <li>最近更新时间: <code>{status['updated_at_utc']}</code></li>
    <li>当前月弱桶: <code>{', '.join(status['current_bottom5_buckets'])}</code></li>
    <li>闭合交易数: <code>{status['closed_trades']}</code></li>
    <li>累计净收益: <code>{status['lifetime_total_return']:.4%}</code></li>
    <li>均值净收益: <code>{status['mean_net_bps']:.2f} bps</code></li>
    <li>盘口 spread: <code>{status['book_spread_bps'] if status['book_spread_bps'] is not None else 'n/a'}</code></li>
  </ul>
  <h2>当前仓位 / 触发状态</h2>
  <pre>{json.dumps(active_position or {'side': 'flat', 'reason': 'current hour is not in this month bottom-5 weak buckets'}, ensure_ascii=False, indent=2, default=str)}</pre>
  <h2>本月 bottom-5 weekday-hour schedule</h2>
  {sched_preview.to_html(index=False) if not sched_preview.empty else '<p>暂无 schedule</p>'}
</body>
</html>
"""
    HTML_PATH.write_text(body, encoding="utf-8")


def main() -> int:
    ensure_dir(ART_DIR)
    df = load_hourly_frame()
    schedule_df, trades = build_monthly_schedule(df)
    if schedule_df.empty:
        raise RuntimeError("rank200 schedule build returned empty")

    snapshot, active_position = live_snapshot(df, schedule_df)
    current_sched = schedule_df[schedule_df["month_start"] == snapshot["current_month_start"]].copy()
    current_sched = current_sched.sort_values(["mean_ret_1h", "train_obs", "weekday", "hour"], ascending=[True, False, True, True]).reset_index(drop=True)

    prior_ledger = read_csv_or_empty(LEDGER_PATH)
    prior_ids = set(prior_ledger["trade_id"].astype(str)) if not prior_ledger.empty and "trade_id" in prior_ledger.columns else set()
    new_rows = trades[~trades["trade_id"].isin(prior_ids)].copy() if not trades.empty else pd.DataFrame()
    ledger = normalize_for_csv(trades)
    if not ledger.empty:
        ledger = ledger.drop_duplicates(subset=["trade_id"], keep="last")
        ledger.to_csv(LEDGER_PATH, index=False)

    normalize_for_csv(current_sched).to_csv(SCHEDULE_PATH, index=False)
    normalize_for_csv(df[["ts", "open", "high", "low", "close", "volume", "weekday", "hour", "ret_1h"]].tail(240)).to_csv(HOURLY_PATH, index=False)

    lifetime_total_return = float((1.0 + trades["net_ret"]).prod() - 1.0) if not trades.empty else 0.0
    status = {
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "stage": "paper_runner_live",
        "wiring_status": "connected_runner_live",
        "runner_script": "scripts/run_rank200_btc_weekday_hour_paper_runner.py",
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "refresh_cadence": "1h",
        "signal_timeframe": "1h",
        "venue_signal": "Binance BTCUSDT perp 1h",
        "venue_execution": "BTCUSDT perp paper short",
        "selection_rule": "monthly refresh trailing 365d bottom-5 weekday-hour weak buckets",
        "hold_hours": HOLD_HOURS,
        "round_trip_cost_bps": ROUND_TRIP_COST_BPS,
        "latest_ts": iso_z(snapshot["latest_ts"]),
        "latest_close": snapshot["latest_close"],
        "current_month_start": iso_z(snapshot["current_month_start"]),
        "current_bottom5_count": snapshot["current_bottom5_count"],
        "current_bottom5_buckets": snapshot["current_bottom5_buckets"],
        "book_spread_bps": snapshot["book_spread_bps"],
        "is_active_bucket_now": snapshot["is_active_bucket_now"],
        "closed_trades": int(len(trades)),
        "new_closed_trades_appended": int(len(new_rows)),
        "mean_net_bps": float(trades["net_bps"].mean()) if not trades.empty else 0.0,
        "win_rate": float((trades["net_bps"] > 0).mean()) if not trades.empty else 0.0,
        "lifetime_total_return": lifetime_total_return,
        "open_position_side": active_position["side"] if active_position else "flat",
        "updated_at_utc": iso_z(utc_now()),
        "note": "wired: dedicated runner + systemd timer live; Rank 200 now runs as a BTC-only monthly-refresh bottom-5 weekday-hour -> 4h short paper scheduler.",
    }
    pd.DataFrame([status]).to_csv(STATUS_PATH, index=False)
    state = {
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "wiring_status": "connected_runner_live",
        "runner_script": str((ROOT / "scripts" / "run_rank200_btc_weekday_hour_paper_runner.py").relative_to(ROOT)),
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "last_run_at_utc": iso_z(utc_now()),
        "latest_signal_ts": iso_z(snapshot["latest_ts"]),
        "current_month_start": iso_z(snapshot["current_month_start"]),
        "current_bottom5_buckets": snapshot["current_bottom5_buckets"],
        "open_position": {k: (iso_z(v) if isinstance(v, pd.Timestamp) else v) for k, v in (active_position or {}).items()},
        "closed_trades": int(len(trades)),
        "lifetime_total_return": lifetime_total_return,
    }
    write_json(STATE_PATH, state)
    write_html(status, active_position, current_sched)
    summary = {
        "run_at_utc": iso_z(utc_now()),
        "runner": "rank200_btc_weekday_hour_paper_runner",
        "closed_trades_total": int(len(trades)),
        "new_closed_trades_appended": int(len(new_rows)),
        "open_position_side": active_position["side"] if active_position else "flat",
        "current_bottom5_buckets": snapshot["current_bottom5_buckets"],
        "status_path": str(STATUS_PATH.relative_to(ROOT)),
        "ledger_path": str(LEDGER_PATH.relative_to(ROOT)),
        "state_path": str(STATE_PATH.relative_to(ROOT)),
        "html_path": str(HTML_PATH.relative_to(ROOT)),
        "schedule_path": str(SCHEDULE_PATH.relative_to(ROOT)),
    }
    write_json(RUN_SUMMARY_PATH, summary)
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
