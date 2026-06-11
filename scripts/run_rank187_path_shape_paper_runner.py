#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from paper_runner_utils import (
    ROOT,
    ensure_dir,
    fetch_binance_futures_klines,
    iso_z,
    normalize_for_csv,
    read_csv_or_empty,
    utc_now,
    write_json,
)

ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank187_path_shape"
LEDGER_PATH = ART_DIR / "rank187_closed_trades.csv"
STATUS_PATH = ART_DIR / "rank187_status.csv"
STATE_PATH = ART_DIR / "rank187_state.json"
RUN_SUMMARY_PATH = ART_DIR / "rank187_last_run_summary.json"
SIGNALS_PATH = ART_DIR / "rank187_signal_snapshot.csv"
HTML_PATH = ROOT / "reports" / "site" / "paper" / "rank187_path_shape.html"
SEED_TRADES_PATH = ROOT / "reports" / "artifacts" / "quant_digests" / "bitcoin_intraday_curve_shape_20260326_1633" / "selected_variant_trades.csv"

CANDIDATE_ID = "rank187_btcusdt_late_session_path_shape_swing"
CANDIDATE_RANK = 187
SYMBOL = "BTCUSDT"
INTERVAL = "15m"
LOOKBACK_FETCH_DAYS = 95
LOOKBACK_DAYS = 60
OBS_BARS = 32
NN_K = 3
COST_RT_BPS = 6.0
RUNNER_TIMER = "momentum-rank187-paper-refresh.timer"
RUNNER_SERVICE = "momentum-rank187-paper-refresh.service"


def load_bars() -> pd.DataFrame:
    end_ms = int(utc_now().replace(second=0, microsecond=0).timestamp() * 1000)
    start_ms = end_ms - LOOKBACK_FETCH_DAYS * 24 * 60 * 60 * 1000
    df = fetch_binance_futures_klines(SYMBOL, INTERVAL, start_ms, end_ms)
    if df.empty:
        raise RuntimeError("no BTCUSDT 15m bars fetched")
    df = df[["ts", "open", "high", "low", "close", "volume"]].copy()
    df["day"] = df["ts"].dt.floor("D")
    return df.sort_values("ts").reset_index(drop=True)


def build_day_frames(df: pd.DataFrame) -> tuple[dict[pd.Timestamp, pd.DataFrame], list[pd.Timestamp], pd.Timestamp | None]:
    frames: dict[pd.Timestamp, pd.DataFrame] = {}
    full_days: list[pd.Timestamp] = []
    current_partial_day = None
    latest_day = df["day"].max()
    for day, grp in df.groupby("day"):
        grp = grp.sort_values("ts").reset_index(drop=True).copy()
        grp["bar_idx"] = range(len(grp))
        grp["cum_log_ret"] = np.log(grp["close"] / float(grp["close"].iloc[0]))
        grp["day_date"] = day
        frames[day] = grp
        if len(grp) == 96:
            full_days.append(day)
        elif day == latest_day:
            current_partial_day = day
    full_days = sorted(full_days)
    return frames, full_days, current_partial_day


def signal_for_day(day: pd.Timestamp, frames: dict[pd.Timestamp, pd.DataFrame], full_days: list[pd.Timestamp]) -> dict | None:
    current = frames.get(day)
    if current is None or len(current) < OBS_BARS:
        return None
    hist_days = [d for d in full_days if d < day]
    if len(hist_days) < LOOKBACK_DAYS:
        return None
    hist_days = hist_days[-LOOKBACK_DAYS:]
    current_path = current["cum_log_ret"].iloc[:OBS_BARS].to_numpy(dtype=float)
    dists: list[tuple[float, pd.Timestamp]] = []
    for hist_day in hist_days:
        hist_path = frames[hist_day]["cum_log_ret"].iloc[:OBS_BARS].to_numpy(dtype=float)
        dists.append((float(np.linalg.norm(hist_path - current_path)), hist_day))
    dists.sort(key=lambda x: x[0])
    nn_days = [d for _, d in dists[:NN_K]]
    avg_nn_dist = float(np.mean([x[0] for x in dists[:NN_K]]))
    remainders = []
    for hist_day in nn_days:
        hist_frame = frames[hist_day]
        hist_path = hist_frame["cum_log_ret"].to_numpy(dtype=float)
        remainders.append(hist_path[OBS_BARS - 1 :] - hist_path[OBS_BARS - 1])
    avg_remainder = np.mean(np.vstack(remainders), axis=0)
    future = avg_remainder[1:]
    if len(future) == 0:
        return None
    predicted_eod_ret = float(avg_remainder[-1])
    future_max = float(np.max(future))
    if future_max <= 0 or predicted_eod_ret <= 0:
        return None
    future_argmax = int(np.argmax(future)) + 1
    planned_exit_idx = (OBS_BARS - 1) + future_argmax
    if planned_exit_idx >= len(current):
        planned_exit_ts = None
        exit_price = None
    else:
        planned_exit_ts = pd.Timestamp(current.iloc[planned_exit_idx]["ts"])
        exit_price = float(current.iloc[planned_exit_idx]["close"])
    entry_row = current.iloc[OBS_BARS - 1]
    entry_ts = pd.Timestamp(entry_row["ts"])
    entry_price = float(entry_row["close"])
    nn_preview = ",".join([pd.Timestamp(d).strftime("%Y-%m-%d") for d in nn_days])
    signal = {
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "day": day,
        "entry_ts": entry_ts,
        "entry_price": entry_price,
        "planned_exit_ts": planned_exit_ts,
        "planned_exit_idx": int(planned_exit_idx),
        "predicted_future_max_pct": future_max * 100.0,
        "predicted_eod_ret_pct": predicted_eod_ret * 100.0,
        "avg_nn_dist": avg_nn_dist,
        "nn_days": nn_preview,
        "side": "long_btc",
    }
    if exit_price is not None and planned_exit_ts is not None:
        gross_ret = (exit_price / entry_price) - 1.0
        net_ret = gross_ret - (COST_RT_BPS / 10000.0)
        signal.update(
            {
                "exit_ts": planned_exit_ts,
                "exit_price": exit_price,
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "gross_bps": gross_ret * 10000.0,
                "net_bps": net_ret * 10000.0,
                "hold_bars": int(planned_exit_idx - (OBS_BARS - 1)),
            }
        )
    return signal


def load_seed_trades() -> pd.DataFrame:
    if not SEED_TRADES_PATH.exists():
        return pd.DataFrame()
    raw = pd.read_csv(SEED_TRADES_PATH)
    raw = raw.loc[raw["variant"] == "h32_k3"].copy()
    if raw.empty:
        return pd.DataFrame()
    raw["trade_day"] = raw["date"].astype(str)
    raw["entry_ts"] = pd.to_datetime(raw["entry_time"], utc=True)
    raw["exit_ts"] = pd.to_datetime(raw["exit_time"], utc=True)
    raw["gross_ret"] = pd.to_numeric(raw["gross_ret_pct"], errors="coerce") / 100.0
    raw["net_ret"] = raw["gross_ret"] - (COST_RT_BPS / 10000.0)
    raw["gross_bps"] = raw["gross_ret"] * 10000.0
    raw["net_bps"] = raw["net_ret"] * 10000.0
    raw["trade_id"] = raw["trade_day"] + "|" + raw["entry_ts"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    out = pd.DataFrame(
        {
            "trade_id": raw["trade_id"],
            "candidate_id": CANDIDATE_ID,
            "candidate_rank": CANDIDATE_RANK,
            "trade_day": raw["trade_day"],
            "entry_ts": raw["entry_ts"],
            "exit_ts": raw["exit_ts"],
            "side": "long_btc",
            "entry_price": np.nan,
            "exit_price": np.nan,
            "hold_bars": pd.to_numeric(raw["hold_bars"], errors="coerce"),
            "avg_nn_dist": pd.to_numeric(raw["avg_nn_dist"], errors="coerce"),
            "predicted_future_max_pct": pd.to_numeric(raw["pred_eod_ret_pct"], errors="coerce"),
            "nn_days": "seed_h32_k3",
            "gross_ret": raw["gross_ret"],
            "net_ret": raw["net_ret"],
            "gross_bps": raw["gross_bps"],
            "net_bps": raw["net_bps"],
            "cost_rt_bps": COST_RT_BPS,
        }
    )
    return out


def build_dynamic_closed_trades(frames: dict[pd.Timestamp, pd.DataFrame], full_days: list[pd.Timestamp], start_after: pd.Timestamp | None) -> pd.DataFrame:
    rows: list[dict] = []
    for day in full_days:
        if start_after is not None and day <= start_after:
            continue
        signal = signal_for_day(day, frames, full_days)
        if not signal or signal.get("exit_ts") is None:
            continue
        rows.append(
            {
                "trade_id": f"{pd.Timestamp(day).strftime('%Y-%m-%d')}|{iso_z(signal['entry_ts'])}",
                "candidate_id": CANDIDATE_ID,
                "candidate_rank": CANDIDATE_RANK,
                "trade_day": pd.Timestamp(day).strftime("%Y-%m-%d"),
                "entry_ts": signal["entry_ts"],
                "exit_ts": signal["exit_ts"],
                "side": signal["side"],
                "entry_price": signal["entry_price"],
                "exit_price": signal["exit_price"],
                "hold_bars": signal["hold_bars"],
                "avg_nn_dist": signal["avg_nn_dist"],
                "predicted_future_max_pct": signal["predicted_future_max_pct"],
                "nn_days": signal["nn_days"],
                "gross_ret": signal["gross_ret"],
                "net_ret": signal["net_ret"],
                "gross_bps": signal["gross_bps"],
                "net_bps": signal["net_bps"],
                "cost_rt_bps": COST_RT_BPS,
            }
        )
    return pd.DataFrame(rows)


def current_open_position(current_day: pd.Timestamp | None, frames: dict[pd.Timestamp, pd.DataFrame], full_days: list[pd.Timestamp]) -> tuple[dict | None, dict | None]:
    if current_day is None:
        return None, None
    signal = signal_for_day(current_day, frames, full_days)
    if not signal:
        return None, None
    current_frame = frames[current_day]
    latest_row = current_frame.iloc[-1]
    latest_ts = pd.Timestamp(latest_row["ts"])
    if signal["planned_exit_ts"] is not None and latest_ts >= signal["planned_exit_ts"]:
        return signal, None
    entry_price = float(signal["entry_price"])
    current_price = float(latest_row["close"])
    gross_ret = (current_price / entry_price) - 1.0
    open_position = {
        "side": signal["side"],
        "entry_ts": signal["entry_ts"],
        "planned_exit_ts": signal["planned_exit_ts"],
        "entry_price": entry_price,
        "current_ts": latest_ts,
        "current_price": current_price,
        "avg_nn_dist": signal["avg_nn_dist"],
        "predicted_future_max_pct": signal["predicted_future_max_pct"],
        "nn_days": signal["nn_days"],
        "gross_mtm_bps": gross_ret * 10000.0,
        "net_mtm_bps_after_rt_cost": (gross_ret - COST_RT_BPS / 10000.0) * 10000.0,
    }
    return signal, open_position


def write_html(status: dict, signal: dict | None, open_position: dict | None) -> None:
    ensure_dir(HTML_PATH.parent)
    body = f"""<!doctype html>
<html lang=\"zh\">
<head>
  <meta charset=\"utf-8\" />
  <title>Rank 187 Paper Runner</title>
  <style>body{{font-family:Arial,sans-serif;margin:24px;line-height:1.5}}code{{background:#f3f3f3;padding:2px 4px}}</style>
</head>
<body>
  <h1>Rank 187 / BTCUSDT 15m late-session path-shape swing</h1>
  <p><strong>接线状态：</strong>{status['wiring_status']}</p>
  <ul>
    <li>runner: <code>{status['runner_script']}</code></li>
    <li>service: <code>{status['service_unit']}</code></li>
    <li>timer: <code>{status['timer_unit']}</code></li>
    <li>模型：<code>60d lookback / k=3 / first 8h path</code></li>
    <li>最近更新时间: <code>{status['updated_at_utc']}</code></li>
    <li>闭合交易数: <code>{status['closed_trades']}</code></li>
    <li>累计净收益: <code>{status['lifetime_total_return']:.4%}</code></li>
  </ul>
  <h2>今日信号</h2>
  <pre>{json.dumps(signal or {'signal': 'none'}, ensure_ascii=False, indent=2, default=str)}</pre>
  <h2>当前仓位</h2>
  <pre>{json.dumps(open_position or {'side': 'flat'}, ensure_ascii=False, indent=2, default=str)}</pre>
</body>
</html>
"""
    HTML_PATH.write_text(body, encoding="utf-8")


def main() -> int:
    ensure_dir(ART_DIR)
    df = load_bars()
    frames, full_days, current_day = build_day_frames(df)
    seed_trades = load_seed_trades()
    seed_last_day = pd.to_datetime(seed_trades["trade_day"], utc=True).max().floor("D") if not seed_trades.empty else None
    dynamic_trades = build_dynamic_closed_trades(frames, full_days, seed_last_day)
    trades = pd.concat([seed_trades, dynamic_trades], ignore_index=True) if not seed_trades.empty else dynamic_trades
    if not trades.empty:
        trades = trades.drop_duplicates(subset=["trade_id"], keep="last").sort_values("trade_day").reset_index(drop=True)
    prior_ledger = read_csv_or_empty(LEDGER_PATH)
    prior_ids = set(prior_ledger["trade_id"].astype(str)) if not prior_ledger.empty and "trade_id" in prior_ledger.columns else set()
    new_rows = trades[~trades["trade_id"].isin(prior_ids)].copy() if not trades.empty else pd.DataFrame()
    ledger = normalize_for_csv(trades)
    if not ledger.empty:
        ledger = ledger.drop_duplicates(subset=["trade_id"], keep="last")
        ledger.to_csv(LEDGER_PATH, index=False)

    today_signal, open_position = current_open_position(current_day, frames, full_days)
    lifetime_total_return = float((1.0 + trades["net_ret"]).prod() - 1.0) if not trades.empty else 0.0
    status = {
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "stage": "paper_runner_live",
        "wiring_status": "connected_runner_live",
        "runner_script": "scripts/run_rank187_path_shape_paper_runner.py",
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "refresh_cadence": "15m",
        "market": SYMBOL,
        "interval": INTERVAL,
        "lookback_days": LOOKBACK_DAYS,
        "observation_bars": OBS_BARS,
        "nn_k": NN_K,
        "cost_rt_bps": COST_RT_BPS,
        "closed_trades": int(len(trades)),
        "new_closed_trades_appended": int(len(new_rows)),
        "mean_net_bps": float(trades["net_bps"].mean()) if not trades.empty else 0.0,
        "win_rate": float((trades["net_bps"] > 0).mean()) if not trades.empty else 0.0,
        "lifetime_total_return": lifetime_total_return,
        "today_signal": "long_btc" if today_signal else "none",
        "today_predicted_future_max_pct": float(today_signal["predicted_future_max_pct"]) if today_signal else 0.0,
        "today_avg_nn_dist": float(today_signal["avg_nn_dist"]) if today_signal else 0.0,
        "current_position_side": open_position["side"] if open_position else "flat",
        "updated_at_utc": iso_z(utc_now()),
        "note": "wired: dedicated runner + timer live; historical baseline seeded from the approved h32_k3 research ledger, with forward updates handled by the live runner.",
    }
    pd.DataFrame([status]).to_csv(STATUS_PATH, index=False)
    signal_snapshot = pd.DataFrame([
        {
            "current_day": pd.Timestamp(current_day).strftime("%Y-%m-%d") if current_day is not None else None,
            "entry_ts": iso_z(today_signal["entry_ts"]) if today_signal else None,
            "planned_exit_ts": iso_z(today_signal["planned_exit_ts"]) if today_signal and today_signal.get("planned_exit_ts") is not None else None,
            "predicted_future_max_pct": float(today_signal["predicted_future_max_pct"]) if today_signal else None,
            "avg_nn_dist": float(today_signal["avg_nn_dist"]) if today_signal else None,
            "nn_days": today_signal["nn_days"] if today_signal else None,
        }
    ])
    signal_snapshot.to_csv(SIGNALS_PATH, index=False)
    state = {
        "candidate_id": CANDIDATE_ID,
        "candidate_rank": CANDIDATE_RANK,
        "wiring_status": "connected_runner_live",
        "runner_script": str((ROOT / "scripts" / "run_rank187_path_shape_paper_runner.py").relative_to(ROOT)),
        "service_unit": RUNNER_SERVICE,
        "timer_unit": RUNNER_TIMER,
        "last_run_at_utc": iso_z(utc_now()),
        "today_signal": {
            k: (iso_z(v) if isinstance(v, pd.Timestamp) else pd.Timestamp(v).strftime("%Y-%m-%d") if k == "day" else v)
            for k, v in (today_signal or {}).items()
        },
        "open_position": {k: (iso_z(v) if isinstance(v, pd.Timestamp) else v) for k, v in (open_position or {}).items()},
        "closed_trades": int(len(trades)),
        "lifetime_total_return": lifetime_total_return,
    }
    write_json(STATE_PATH, state)
    write_html(status, today_signal, open_position)
    summary = {
        "run_at_utc": iso_z(utc_now()),
        "runner": "rank187_path_shape_paper_runner",
        "closed_trades_total": int(len(trades)),
        "new_closed_trades_appended": int(len(new_rows)),
        "today_signal": "long_btc" if today_signal else "none",
        "open_position_side": open_position["side"] if open_position else "flat",
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
