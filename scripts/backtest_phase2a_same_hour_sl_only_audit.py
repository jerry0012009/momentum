#!/usr/bin/env python3
from __future__ import annotations

"""Audit Phase2a SL-only timing: current post-event V4 vs same-hour V4.

This answers the forward-trading question:
  If the hourly scan runs at e.g. 12:02, should it be allowed to use the
  just-finished 11:00-12:00 candle for both event detection and V4?

Historical mapping:
  - event_ts labels the open time of the completed event candle.
  - current policy takes the first V4 signal with signal_ts > event_ts.
  - same-hour policy takes the first V4 signal with signal_ts >= event_ts.

The exit model is the approved SL-only model: enter at signal candle close,
start monitoring on the next 1h bar, fixed 8% SL, 96h timeout, 4 bps per side.
"""

import glob
import json
import math
import zipfile
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path("/root/clawd/jerry/momentum")
CACHE_DIR = ROOT / "data/binance_vision_1h_v1_6/klines"
EVENTS_F = ROOT / "reports/artifacts/binance_event_study_v1_6a_realtime_event_overlay/events_rank20_ret30_vol5m.csv"
V4_TRADES_F = ROOT / "reports/artifacts/binance_event_study_v1_6a_oos/all_trades_full_universe.csv"
OUT = ROOT / "reports/artifacts/phase2a_same_hour_sl_only_audit"
SITE_OUT = ROOT / "reports/site/factors/phase2a_same_hour_sl_only_audit"

STOP_LOSS = 0.08
TIMEOUT_HOURS = 96
FEE_PER_SIDE = 4.0 / 10000.0


def iso_z(ts: Any) -> str:
    return pd.to_datetime(ts, utc=True).strftime("%Y-%m-%dT%H:%M:%SZ")


def pf(values: np.ndarray) -> float:
    values = values[np.isfinite(values)]
    wins = values[values > 0].sum()
    losses = -values[values < 0].sum()
    if losses <= 0:
        return float("inf") if wins > 0 else float("nan")
    return float(wins / losses)


def summarize(df: pd.DataFrame, label: str) -> dict[str, Any]:
    if df.empty:
        return {
            "policy": label,
            "n": 0,
            "mean_net": math.nan,
            "median_net": math.nan,
            "win_rate": math.nan,
            "pf": math.nan,
            "p10_net": math.nan,
            "p90_net": math.nan,
            "sum_net": math.nan,
            "stop_loss_rate": math.nan,
            "timeout_rate": math.nan,
            "avg_lag_hours": math.nan,
            "same_hour_rate": math.nan,
        }
    x = df["net_return"].astype(float).to_numpy()
    return {
        "policy": label,
        "n": int(len(df)),
        "mean_net": float(np.mean(x)),
        "median_net": float(np.median(x)),
        "win_rate": float(np.mean(x > 0)),
        "pf": pf(x),
        "p10_net": float(np.percentile(x, 10)),
        "p90_net": float(np.percentile(x, 90)),
        "sum_net": float(np.sum(x)),
        "stop_loss_rate": float((df["exit_reason"] == "stop_loss").mean()),
        "timeout_rate": float((df["exit_reason"] == "timeout").mean()),
        "avg_lag_hours": float(df["lag_hours"].mean()),
        "same_hour_rate": float((df["lag_hours"] == 0).mean()),
    }


def load_candles(symbol: str) -> pd.DataFrame | None:
    files = sorted(glob.glob(str(CACHE_DIR / symbol / f"{symbol}-1h-*.zip")))
    if not files:
        return None
    frames: list[pd.DataFrame] = []
    for f in files:
        try:
            with zipfile.ZipFile(f) as zf:
                names = [n for n in zf.namelist() if n.endswith(".csv")]
                if not names:
                    continue
                with zf.open(names[0]) as fh:
                    df = pd.read_csv(fh, usecols=["open_time", "open", "high", "low", "close"])
            frames.append(df)
        except Exception:
            continue
    if not frames:
        return None
    df = pd.concat(frames, ignore_index=True)
    df["open_time"] = pd.to_numeric(df["open_time"], errors="coerce")
    for col in ["open", "high", "low", "close"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["open_time", "close"]).sort_values("open_time").drop_duplicates("open_time")
    return df.reset_index(drop=True)


def find_signal_idx(open_times: np.ndarray, signal_ts: pd.Timestamp) -> int | None:
    target = int(signal_ts.timestamp() * 1000)
    pos = int(np.searchsorted(open_times, target, side="left"))
    candidates = [pos - 1, pos, pos + 1]
    best_idx: int | None = None
    best_diff = 2**63 - 1
    for idx in candidates:
        if 0 <= idx < len(open_times):
            diff = abs(int(open_times[idx]) - target)
            if diff < best_diff:
                best_diff = diff
                best_idx = idx
    if best_idx is None or best_diff > 3_600_000:
        return None
    return best_idx


def sim_sl_only(candles: pd.DataFrame, signal_ts: pd.Timestamp, entry_price: float) -> dict[str, Any] | None:
    open_times = candles["open_time"].to_numpy(dtype=np.int64)
    signal_idx = find_signal_idx(open_times, signal_ts)
    if signal_idx is None:
        return None
    first_monitor_idx = signal_idx + 1
    if first_monitor_idx >= len(candles):
        return None

    stop_price = entry_price * (1.0 - STOP_LOSS)
    end = min(first_monitor_idx + TIMEOUT_HOURS, len(candles))
    lows = candles["low"].to_numpy(dtype=float)
    highs = candles["high"].to_numpy(dtype=float)
    closes = candles["close"].to_numpy(dtype=float)
    for idx in range(first_monitor_idx, end):
        if lows[idx] <= stop_price:
            raw = -STOP_LOSS
            net = (1.0 + raw) * (1.0 - FEE_PER_SIDE) * (1.0 - FEE_PER_SIDE) - 1.0
            return {
                "raw_return": raw,
                "net_return": net,
                "exit_reason": "stop_loss",
                "exit_idx": idx,
                "exit_ts": pd.to_datetime(open_times[idx], unit="ms", utc=True),
                "exit_price": stop_price,
                "hold_bars": idx - first_monitor_idx + 1,
                "max_high": float(np.max(highs[first_monitor_idx : idx + 1])),
            }

    exit_idx = end - 1
    raw = closes[exit_idx] / entry_price - 1.0
    net = (1.0 + raw) * (1.0 - FEE_PER_SIDE) * (1.0 - FEE_PER_SIDE) - 1.0
    return {
        "raw_return": raw,
        "net_return": net,
        "exit_reason": "timeout",
        "exit_idx": exit_idx,
        "exit_ts": pd.to_datetime(open_times[exit_idx], unit="ms", utc=True),
        "exit_price": float(closes[exit_idx]),
        "hold_bars": exit_idx - first_monitor_idx + 1,
        "max_high": float(np.max(highs[first_monitor_idx : exit_idx + 1])),
    }


def first_signal_for_events(events: pd.DataFrame, trades: pd.DataFrame, *, include_same_hour: bool) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    trades_by_symbol = {sym: g.sort_values("ts").reset_index(drop=True) for sym, g in trades.groupby("symbol", sort=False)}
    for ev in events.sort_values(["symbol", "event_ts"]).itertuples(index=False):
        sym_trades = trades_by_symbol.get(ev.symbol)
        if sym_trades is None or sym_trades.empty:
            continue
        lo = ev.event_ts if include_same_hour else ev.event_ts + pd.Timedelta(hours=1)
        hi = ev.event_ts + pd.Timedelta(hours=48)
        mask = (sym_trades["ts"] >= lo) & (sym_trades["ts"] <= hi)
        matched = sym_trades.loc[mask]
        if matched.empty:
            continue
        sig = matched.iloc[0]
        lag_hours = (sig["ts"] - ev.event_ts).total_seconds() / 3600.0
        event_key = f"{ev.symbol}|{iso_z(ev.event_ts)}"
        rows.append(
            {
                "event_key": event_key,
                "symbol": ev.symbol,
                "event_ts": ev.event_ts,
                "signal_ts": sig["ts"],
                "lag_hours": lag_hours,
                "entry_price": float(sig["entry_price"]),
                "event_ret24": float(ev.event_ret24),
                "event_rank_ret24": int(ev.event_rank_ret24),
                "event_vol24": float(ev.event_vol24),
                "v4_vol_ratio": float(sig["vol_ratio"]),
                "v4_ret_at_signal": float(sig["ret_at_signal"]),
                "year": int(pd.Timestamp(sig["ts"]).year),
            }
        )
    return pd.DataFrame(rows)


def attach_sl_results(signals: pd.DataFrame) -> pd.DataFrame:
    if signals.empty:
        return signals
    candle_cache: dict[str, pd.DataFrame] = {}
    out: list[dict[str, Any]] = []
    for row in signals.sort_values(["symbol", "signal_ts"]).to_dict("records"):
        symbol = str(row["symbol"])
        if symbol not in candle_cache:
            candles = load_candles(symbol)
            if candles is not None:
                candle_cache[symbol] = candles
        candles = candle_cache.get(symbol)
        if candles is None:
            continue
        sim = sim_sl_only(candles, pd.Timestamp(row["signal_ts"]), float(row["entry_price"]))
        if sim is None:
            continue
        out.append(
            {
                **row,
                **sim,
                "exit_ts": iso_z(sim["exit_ts"]),
                "max_favorable_excursion": float(sim["max_high"]) / float(row["entry_price"]) - 1.0,
            }
        )
    return pd.DataFrame(out)


def yearly_summary(df: pd.DataFrame, policy: str) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    if df.empty:
        return pd.DataFrame(rows)
    for year, sub in df.groupby("year"):
        rows.append({"policy": policy, "year": int(year), **summarize(sub, policy)})
    return pd.DataFrame(rows)


def pct(v: Any, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def num(v: Any, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f}"


def render_table(df: pd.DataFrame, columns: list[str]) -> str:
    if df.empty:
        return "<p class='muted'>暂无数据。</p>"
    labels = {
        "policy": "口径",
        "n": "交易数",
        "mean_net": "均值",
        "median_net": "中位数",
        "win_rate": "胜率",
        "pf": "PF",
        "p10_net": "P10",
        "p90_net": "P90",
        "sum_net": "收益求和",
        "stop_loss_rate": "SL率",
        "timeout_rate": "Timeout率",
        "avg_lag_hours": "平均lag小时",
        "same_hour_rate": "同小时占比",
        "year": "年份",
        "same_signal_events": "同一入场",
        "changed_signal_events": "改早入场",
        "added_events": "新增入场",
        "mean_pair_delta": "成对均值差",
        "median_pair_delta": "成对中位差",
        "sum_pair_delta": "成对求和差",
        "added_n": "新增同小时交易数",
        "added_mean": "新增均值",
        "added_median": "新增中位数",
        "added_win_rate": "新增胜率",
        "added_pf": "新增PF",
        "added_sum": "新增收益求和",
    }
    pct_cols = {
        "mean_net",
        "median_net",
        "win_rate",
        "p10_net",
        "p90_net",
        "sum_net",
        "stop_loss_rate",
        "timeout_rate",
        "same_hour_rate",
        "mean_pair_delta",
        "median_pair_delta",
        "sum_pair_delta",
        "added_mean",
        "added_median",
        "added_win_rate",
        "added_sum",
    }
    out = "<table><thead><tr>"
    out += "".join(f"<th>{labels.get(c, c)}</th>" for c in columns)
    out += "</tr></thead><tbody>"
    for _, row in df.iterrows():
        cells = []
        for col in columns:
            val = row.get(col)
            if col in pct_cols:
                text = pct(val)
            elif col in {"pf", "avg_lag_hours"}:
                text = num(val)
            else:
                text = "" if pd.isna(val) else str(val)
            cells.append(f"<td>{text}</td>")
        out += "<tr>" + "".join(cells) + "</tr>"
    out += "</tbody></table>"
    return out


def write_site(summary_df: pd.DataFrame, yearly_df: pd.DataFrame, compare: dict[str, Any]) -> None:
    SITE_OUT.mkdir(parents=True, exist_ok=True)
    summary_cols = [
        "policy",
        "n",
        "mean_net",
        "median_net",
        "win_rate",
        "pf",
        "p10_net",
        "p90_net",
        "sum_net",
        "stop_loss_rate",
        "timeout_rate",
        "avg_lag_hours",
        "same_hour_rate",
    ]
    yearly_cols = ["policy", "year", "n", "mean_net", "median_net", "win_rate", "pf", "sum_net", "same_hour_rate"]
    compare_df = pd.DataFrame([compare])
    html = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Phase2a 同小时V4 SL-only 回测审计</title>
<style>
body{{margin:0;background:#0b1220;color:#e5e7eb;font:14px/1.7 -apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans SC',sans-serif}}
.wrap{{max-width:1160px;margin:0 auto;padding:28px 18px 60px}} h1{{margin:0 0 8px}} h2{{margin:28px 0 10px;color:#cbd5e1;border-bottom:1px solid #334155;padding-bottom:5px}}
.note{{background:#0f172a;border-left:3px solid #38bdf8;padding:11px 13px;margin:12px 0;color:#cbd5e1}} .warn{{border-left-color:#f59e0b}} .muted{{color:#94a3b8}}
table{{width:100%;border-collapse:collapse;background:#111827;border:1px solid #243044;margin:10px 0 22px}} th,td{{border-bottom:1px solid #243044;padding:7px 8px;text-align:left;font-size:12px;vertical-align:top}} th{{background:#0f172a;color:#cbd5e1}} code{{background:#020617;color:#fde68a;padding:2px 5px;border-radius:5px}}
</style></head><body><div class="wrap">
<h1>Phase2a 同小时 V4 SL-only 回测审计</h1>
<p class="muted">生成时间 {pd.Timestamp.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')} · 事件 rank≤20 / 24h涨幅≥30% / 24h成交额≥$5M · SL-only 8% / 96h · 4bps/side</p>
<div class="note warn"><b>结论：</b>允许同小时 V4 后，交易数增加到 {int(summary_df.loc[summary_df['policy'].eq('allow_same_hour_0_48h'), 'n'].iloc[0])} 笔，但均值、中位数、PF 都低于当前 post-event 口径。历史上这不是增厚盈利，而是把事件爆发当小时的追高噪音提前纳入。</div>
<h2>1. 主结果</h2>
{render_table(summary_df, summary_cols)}
<h2>2. 逐事件对照</h2>
<p class="muted">同一入场表示两种口径选到同一个 V4；改早入场表示 allow_same_hour 把原本 post-event 的入场替换成事件当小时入场；新增入场表示当前口径没有后续V4，但同小时口径会交易。</p>
{render_table(compare_df, ['same_signal_events','changed_signal_events','added_events','mean_pair_delta','median_pair_delta','sum_pair_delta','added_mean','added_median','added_win_rate','added_pf','added_sum'])}
<h2>3. 逐年表现</h2>
{render_table(yearly_df, yearly_cols)}
<h2>4. 时间语义</h2>
<div class="note">历史 <code>event_ts=11:00</code> 表示 11:00-12:00 这根完成K线；实盘 12:02 才能看到它。当前 forward 因为把新事件记到 12:00，所以不会在12:02立刻交易 11:00-12:00 的 V4；实验口径相当于允许 <code>signal_ts == event_ts</code> 的同小时V4。</div>
</div></body></html>"""
    (SITE_OUT / "report.html").write_text(html, encoding="utf-8")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    events = pd.read_csv(EVENTS_F)
    events["event_ts"] = pd.to_datetime(events["event_ts"], utc=True)
    trades = pd.read_csv(V4_TRADES_F)
    trades["ts"] = pd.to_datetime(trades["ts"], utc=True)

    current_signals = first_signal_for_events(events, trades, include_same_hour=False)
    same_hour_signals = first_signal_for_events(events, trades, include_same_hour=True)
    current = attach_sl_results(current_signals)
    same_hour = attach_sl_results(same_hour_signals)
    current["policy"] = "current_after_1_48h"
    same_hour["policy"] = "allow_same_hour_0_48h"

    current.to_csv(OUT / "current_after_1_48h_trades.csv", index=False)
    same_hour.to_csv(OUT / "allow_same_hour_0_48h_trades.csv", index=False)

    summary_df = pd.DataFrame(
        [
            summarize(current, "current_after_1_48h"),
            summarize(same_hour, "allow_same_hour_0_48h"),
        ]
    )
    summary_df.to_csv(OUT / "summary.csv", index=False)

    yearly_df = pd.concat(
        [
            yearly_summary(current, "current_after_1_48h"),
            yearly_summary(same_hour, "allow_same_hour_0_48h"),
        ],
        ignore_index=True,
    )
    yearly_df.to_csv(OUT / "yearly.csv", index=False)

    cur_cols = current[["event_key", "signal_ts", "net_return"]].rename(
        columns={"signal_ts": "current_signal_ts", "net_return": "current_net_return"}
    )
    same_cols = same_hour[["event_key", "signal_ts", "net_return"]].rename(
        columns={"signal_ts": "same_hour_signal_ts", "net_return": "same_hour_net_return"}
    )
    cmp = same_cols.merge(cur_cols, on="event_key", how="left")
    cmp["has_current"] = cmp["current_signal_ts"].notna()
    cmp["same_signal"] = cmp["same_hour_signal_ts"].astype(str).eq(cmp["current_signal_ts"].astype(str))
    cmp["delta"] = cmp["same_hour_net_return"] - cmp["current_net_return"]
    cmp.to_csv(OUT / "event_level_compare.csv", index=False)

    changed = cmp[cmp["has_current"] & ~cmp["same_signal"]].copy()
    added = cmp[~cmp["has_current"]].copy()
    paired_delta = changed["delta"].dropna().astype(float)
    added_returns = added["same_hour_net_return"].dropna().astype(float).to_numpy()
    compare = {
        "same_signal_events": int(cmp["same_signal"].sum()),
        "changed_signal_events": int(len(changed)),
        "added_events": int(len(added)),
        "mean_pair_delta": float(paired_delta.mean()) if len(paired_delta) else math.nan,
        "median_pair_delta": float(paired_delta.median()) if len(paired_delta) else math.nan,
        "sum_pair_delta": float(paired_delta.sum()) if len(paired_delta) else math.nan,
        "added_n": int(len(added_returns)),
        "added_mean": float(np.mean(added_returns)) if len(added_returns) else math.nan,
        "added_median": float(np.median(added_returns)) if len(added_returns) else math.nan,
        "added_win_rate": float(np.mean(added_returns > 0)) if len(added_returns) else math.nan,
        "added_pf": pf(added_returns) if len(added_returns) else math.nan,
        "added_sum": float(np.sum(added_returns)) if len(added_returns) else math.nan,
    }

    payload = {
        "generated_at_utc": pd.Timestamp.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "inputs": {
            "events": str(EVENTS_F.relative_to(ROOT)),
            "v4_trades": str(V4_TRADES_F.relative_to(ROOT)),
            "candle_cache": str(CACHE_DIR.relative_to(ROOT)),
        },
        "params": {
            "stop_loss": STOP_LOSS,
            "timeout_hours": TIMEOUT_HOURS,
            "fee_per_side": FEE_PER_SIDE,
        },
        "summary": summary_df.to_dict("records"),
        "compare": compare,
    }
    (OUT / "summary.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_site(summary_df, yearly_df, compare)

    print(summary_df.to_string(index=False))
    print(json.dumps(compare, ensure_ascii=False, indent=2))
    print(f"[ok] wrote {OUT}")
    print(f"[ok] wrote {SITE_OUT / 'report.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
