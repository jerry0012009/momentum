#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from paper_runner_utils import (
    ROOT,
    ensure_dir,
    fetch_coinbase_book,
    fetch_coinbase_candles,
    iso_z,
    normalize_for_csv,
    read_csv_or_empty,
    read_json,
    utc_now,
    write_json,
)

ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank183_cbeth_eth_basis"
LEDGER_PATH = ART_DIR / "rank183_closed_trades.csv"
STATUS_PATH = ART_DIR / "rank183_status.csv"
STATE_PATH = ART_DIR / "rank183_state.json"
RUN_SUMMARY_PATH = ART_DIR / "rank183_last_run_summary.json"
LATEST_SERIES_PATH = ART_DIR / "rank183_latest_pair_series.csv"
HTML_PATH = ROOT / "reports" / "site" / "paper" / "rank183_cbeth_eth_basis.html"

CANDIDATE_ID = "rank183_cbeth_eth_rolling_fair_basis_mr"
CANDIDATE_RANK = 183
PRODUCT_CBETH = "CBETH-USD"
PRODUCT_ETH = "ETH-USD"
GRANULARITY_SEC = 900
LOOKBACK_DAYS = 14
ROLLING_DAYS = 7
ROLLING_BARS = ROLLING_DAYS * 24 * 4
ENTRY_Z = 2.0
EXIT_Z = 0.5
TIMEOUT_BARS = 24 * 4
PAIR_RT_COST_BPS = 28.0
RUNNER_TIMER = "momentum-rank183-paper-refresh.timer"
RUNNER_SERVICE = "momentum-rank183-paper-refresh.service"


def load_pair_frame() -> pd.DataFrame:
    end = utc_now().replace(second=0, microsecond=0)
    start = end - pd.Timedelta(days=LOOKBACK_DAYS)
    cbeth = fetch_coinbase_candles(PRODUCT_CBETH, GRANULARITY_SEC, start, end)
    eth = fetch_coinbase_candles(PRODUCT_ETH, GRANULARITY_SEC, start, end)
    cbeth = cbeth.rename(columns={"close": "cbeth_close", "open": "cbeth_open", "volume": "cbeth_volume"})
    eth = eth.rename(columns={"close": "eth_close", "open": "eth_open", "volume": "eth_volume"})
    df = cbeth[["ts", "cbeth_open", "cbeth_close", "cbeth_volume"]].merge(
        eth[["ts", "eth_open", "eth_close", "eth_volume"]], on="ts", how="inner"
    )
    if df.empty:
        raise RuntimeError("no aligned CBETH / ETH candles fetched")
    df = df.sort_values("ts").reset_index(drop=True)
    df["spread_log"] = np.log(df["cbeth_close"]) - np.log(df["eth_close"])
    df["rolling_mean"] = df["spread_log"].rolling(ROLLING_BARS, min_periods=ROLLING_BARS).mean()
    df["rolling_std"] = df["spread_log"].rolling(ROLLING_BARS, min_periods=ROLLING_BARS).std(ddof=0)
    df["zscore"] = (df["spread_log"] - df["rolling_mean"]) / df["rolling_std"].replace(0, np.nan)
    df["premium_pct"] = (np.exp(df["spread_log"]) - 1.0) * 100.0
    df["fair_basis_pct"] = (np.exp(df["rolling_mean"]) - 1.0) * 100.0
    return df.dropna(subset=["zscore"]).reset_index(drop=True)


def side_name(position: int) -> str:
    if position > 0:
        return "long_cbeth_short_eth"
    if position < 0:
        return "short_cbeth_long_eth"
    return "flat"


def backtest(df: pd.DataFrame) -> tuple[pd.DataFrame, dict | None]:
    trades: list[dict] = []
    position = 0
    entry_idx = None
    entry_spread = None
    entry_ts = None
    entry_z = None

    for i, row in df.iterrows():
        z = float(row["zscore"])
        if position == 0:
            if z <= -ENTRY_Z:
                position = 1
            elif z >= ENTRY_Z:
                position = -1
            if position != 0:
                entry_idx = i
                entry_spread = float(row["spread_log"])
                entry_ts = row["ts"]
                entry_z = z
            continue

        hold_bars = i - int(entry_idx)
        should_exit = abs(z) <= EXIT_Z or hold_bars >= TIMEOUT_BARS
        if should_exit:
            exit_spread = float(row["spread_log"])
            gross_ret = position * (exit_spread - float(entry_spread))
            net_ret = gross_ret - (PAIR_RT_COST_BPS / 10000.0)
            trades.append(
                {
                    "trade_id": f"{side_name(position)}|{iso_z(entry_ts)}|{iso_z(row['ts'])}",
                    "candidate_id": CANDIDATE_ID,
                    "candidate_rank": CANDIDATE_RANK,
                    "signal_family": "rolling_fair_basis_mean_reversion",
                    "venue_mode": "coinbase_spot_vs_eth_perp_paper",
                    "entry_ts": entry_ts,
                    "exit_ts": row["ts"],
                    "side": side_name(position),
                    "entry_z": entry_z,
                    "exit_z": z,
                    "entry_spread_log": entry_spread,
                    "exit_spread_log": exit_spread,
                    "hold_bars": hold_bars,
                    "gross_ret": gross_ret,
                    "net_ret": net_ret,
                    "gross_bps": gross_ret * 10000.0,
                    "net_bps": net_ret * 10000.0,
                    "pair_rt_cost_bps": PAIR_RT_COST_BPS,
                    "exit_reason": "mean_revert" if abs(z) <= EXIT_Z else "timeout",
                }
            )
            position = 0
            entry_idx = entry_spread = entry_ts = entry_z = None

    open_position = None
    if position != 0 and entry_ts is not None:
        last = df.iloc[-1]
        current_spread = float(last["spread_log"])
        gross_ret = position * (current_spread - float(entry_spread))
        open_position = {
            "position": position,
            "side": side_name(position),
            "entry_ts": entry_ts,
            "entry_z": entry_z,
            "entry_spread_log": entry_spread,
            "current_ts": last["ts"],
            "current_z": float(last["zscore"]),
            "current_spread_log": current_spread,
            "hold_bars": len(df) - 1 - int(entry_idx),
            "gross_mtm_bps": gross_ret * 10000.0,
            "net_mtm_bps_after_rt_cost": (gross_ret - PAIR_RT_COST_BPS / 10000.0) * 10000.0,
            "planned_timeout_bars": TIMEOUT_BARS,
        }
    return pd.DataFrame(trades), open_position


def latest_book_snapshot() -> dict:
    snap = {"cbeth_bid": None, "cbeth_ask": None, "cbeth_spread_bps": None}
    try:
        book = fetch_coinbase_book(PRODUCT_CBETH, level=1)
        bid = float(book["bids"][0][0]) if book.get("bids") else None
        ask = float(book["asks"][0][0]) if book.get("asks") else None
        snap["cbeth_bid"] = bid
        snap["cbeth_ask"] = ask
        if bid and ask:
            mid = (bid + ask) / 2.0
            snap["cbeth_spread_bps"] = ((ask - bid) / mid) * 10000.0
    except Exception as exc:  # noqa: BLE001
        snap["book_error"] = str(exc)
    return snap


def write_html(status: dict, open_position: dict | None) -> None:
    ensure_dir(HTML_PATH.parent)
    body = f"""<!doctype html>
<html lang=\"zh\">
<head>
  <meta charset=\"utf-8\" />
  <title>Rank 183 Paper Runner</title>
  <style>body{{font-family:Arial,sans-serif;margin:24px;line-height:1.5}}code{{background:#f3f3f3;padding:2px 4px}}</style>
</head>
<body>
  <h1>Rank 183 / cbETH-ETH rolling fair-basis MR</h1>
  <p><strong>接线状态：</strong>{status['wiring_status']}</p>
  <ul>
    <li>runner: <code>{status['runner_script']}</code></li>
    <li>service: <code>{status['service_unit']}</code></li>
    <li>timer: <code>{status['timer_unit']}</code></li>
    <li>最近更新时间: <code>{status['updated_at_utc']}</code></li>
    <li>最新 z-score: <code>{status['latest_zscore']:.3f}</code></li>
    <li>最新 premium: <code>{status['latest_premium_pct']:.3f}%</code></li>
    <li>rolling fair basis: <code>{status['rolling_fair_basis_pct']:.3f}%</code></li>
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
    df = load_pair_frame()
    trades, open_position = backtest(df)
    latest = df.iloc[-1]
    prior_ledger = read_csv_or_empty(LEDGER_PATH)
    prior_ids = set(prior_ledger["trade_id"].astype(str)) if not prior_ledger.empty and "trade_id" in prior_ledger.columns else set()
    new_rows = trades[~trades["trade_id"].isin(prior_ids)].copy() if not trades.empty else pd.DataFrame()
    ledger = normalize_for_csv(trades)
    if not ledger.empty:
        ledger = ledger.drop_duplicates(subset=["trade_id"], keep="last")
        ledger.to_csv(LEDGER_PATH, index=False)

    book = latest_book_snapshot()
    lifetime_total_return = float((1.0 + trades["net_ret"]).prod() - 1.0) if not trades.empty else 0.0
    status = {
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "stage": "paper_runner_live",
        "wiring_status": "connected_runner_live",
        "runner_script": "scripts/run_rank183_cbeth_eth_paper_runner.py",
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "refresh_cadence": "15m",
        "signal_timeframe": "15m",
        "venue_signal": "Coinbase CBETH-USD / ETH-USD",
        "venue_execution": "CBETH Coinbase spot + ETHUSDT perp hedge",
        "rolling_days": ROLLING_DAYS,
        "entry_z": ENTRY_Z,
        "exit_z": EXIT_Z,
        "timeout_bars": TIMEOUT_BARS,
        "pair_rt_cost_bps": PAIR_RT_COST_BPS,
        "latest_ts": iso_z(latest["ts"]),
        "latest_zscore": float(latest["zscore"]),
        "latest_premium_pct": float(latest["premium_pct"]),
        "rolling_fair_basis_pct": float(latest["fair_basis_pct"]),
        "closed_trades": int(len(trades)),
        "new_closed_trades_appended": int(len(new_rows)),
        "mean_net_bps": float(trades["net_bps"].mean()) if not trades.empty else 0.0,
        "win_rate": float((trades["net_bps"] > 0).mean()) if not trades.empty else 0.0,
        "lifetime_total_return": lifetime_total_return,
        "open_position_side": open_position["side"] if open_position else "flat",
        "open_position_age_bars": int(open_position["hold_bars"]) if open_position else 0,
        "cbeth_top_book_spread_bps": book.get("cbeth_spread_bps"),
        "updated_at_utc": iso_z(utc_now()),
        "note": "wired: dedicated runner + systemd timer live; runner creation and first execution are now explicit parts of P3 launch wiring.",
    }
    normalize_for_csv(df[["ts", "cbeth_close", "eth_close", "spread_log", "rolling_mean", "zscore", "premium_pct", "fair_basis_pct"]].tail(400)).to_csv(LATEST_SERIES_PATH, index=False)
    pd.DataFrame([status]).to_csv(STATUS_PATH, index=False)
    state = {
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "wiring_status": "connected_runner_live",
        "runner_script": str((ROOT / "scripts" / "run_rank183_cbeth_eth_paper_runner.py").relative_to(ROOT)),
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "last_run_at_utc": iso_z(utc_now()),
        "latest_signal_ts": iso_z(latest["ts"]),
        "latest_zscore": float(latest["zscore"]),
        "open_position": {k: (iso_z(v) if isinstance(v, pd.Timestamp) else v) for k, v in (open_position or {}).items()},
        "closed_trades": int(len(trades)),
        "lifetime_total_return": lifetime_total_return,
    }
    write_json(STATE_PATH, state)
    write_html(status, open_position)
    summary = {
        "run_at_utc": iso_z(utc_now()),
        "runner": "rank183_cbeth_eth_paper_runner",
        "closed_trades_total": int(len(trades)),
        "new_closed_trades_appended": int(len(new_rows)),
        "open_position_side": open_position["side"] if open_position else "flat",
        "latest_zscore": float(latest["zscore"]),
        "status_path": str(STATUS_PATH.relative_to(ROOT)),
        "ledger_path": str(LEDGER_PATH.relative_to(ROOT)),
        "state_path": str(STATE_PATH.relative_to(ROOT)),
        "html_path": str(HTML_PATH.relative_to(ROOT)),
    }
    write_json(RUN_SUMMARY_PATH, summary)
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
