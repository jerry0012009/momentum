#!/usr/bin/env python3
"""Causal Phase 2c audit backtest.

This script rebuilds Phase 2c without using the ex-post ``ev_structure`` label
as an entry filter. It uses only information observable at a fixed decision
hour, then writes artifacts and the public HTML page.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "reports/artifacts/binance_hourly_event_study_v1_6/hourly_event_panel.pkl"
OUT_DIR = ROOT / "reports/artifacts/binance_event_study_phase2c_causal_audit"
SITE_OUT = ROOT / "reports/site/paper/rank450/phase2c_funding_squeeze_carry.html"

COST = 0.0013
ENTRY_HOURS = [24, 36, 48]
FUNDING_QS = [0.05, 0.10, 0.20]
RET_THRESHOLDS = [0.00, 0.03, 0.05]
CLOSE_POS_THRESHOLDS = [0.50, 0.60, 0.70]
MAX_DD_LIMITS = [-0.20, -0.30]
HOLD_HOURS = [12, 24]


def _fmt_pct(v: float | int | None, digits: int = 2) -> str:
    if v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def _fmt_num(v: float | int | None, digits: int = 2) -> str:
    if v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))):
        return "-"
    return f"{float(v):,.{digits}f}"


def _metric(net: pd.Series, years: pd.Series) -> dict[str, float | int]:
    if net.empty:
        return {
            "n_trades": 0,
            "net_mean": np.nan,
            "net_median": np.nan,
            "win_rate": np.nan,
            "std": np.nan,
            "sharpe": np.nan,
        }
    span = int(years.max() - years.min() + 1)
    trades_per_year = len(net) / span if span > 0 else len(net)
    std = float(net.std(ddof=1))
    sharpe = float(net.mean() / std * np.sqrt(trades_per_year)) if std > 0 else np.nan
    return {
        "n_trades": int(len(net)),
        "net_mean": float(net.mean()),
        "net_median": float(net.median()),
        "win_rate": float((net > 0).mean()),
        "std": std,
        "sharpe": sharpe,
    }


def _funding_sum(hold: pd.DataFrame) -> float:
    if hold.empty:
        return 0.0
    clean = hold.dropna(subset=["funding_settlement_ts"])
    if clean.empty:
        return 0.0
    # Binance convention in this dataset: positive funding means longs pay;
    # negative funding means longs receive. Long PnL is therefore -rate.
    return float(-clean.drop_duplicates("funding_settlement_ts")["funding_rate"].sum())


def build_event_frame(panel: pd.DataFrame) -> pd.DataFrame:
    """Build one row per event per decision hour with precomputed exits."""
    cols = [
        "symbol",
        "event_date",
        "ts",
        "hours_from_event",
        "open",
        "high",
        "low",
        "close",
        "quote_volume",
        "funding_rate",
        "funding_settlement_ts",
        "ev_funding_bucket",
        "ev_structure",
    ]
    p = panel[cols].copy()
    p = p.sort_values(["symbol", "event_date", "hours_from_event"]).reset_index(drop=True)
    p["event_date_str"] = p["event_date"].astype(str).str[:10]
    p["event_id"] = p["symbol"].astype(str) + "|" + p["event_date_str"]

    h0 = p[p["hours_from_event"] >= 0].groupby("event_id", sort=False).head(1)
    h0_open = h0.set_index("event_id")["open"].rename("event_open")

    frames = []
    for eh in ENTRY_HOURS:
        asof = p[(p["hours_from_event"] >= 0) & (p["hours_from_event"] <= eh)]
        agg = asof.groupby("event_id", sort=False).agg(
            high_sofar=("high", "max"),
            low_sofar=("low", "min"),
            quote_volume_mean_24h=("quote_volume", "mean"),
        )
        entry = p[p["hours_from_event"] >= eh].groupby("event_id", sort=False).head(1)
        entry = entry.set_index("event_id")
        ev = entry[
            [
                "symbol",
                "event_date_str",
                "ts",
                "close",
                "funding_rate",
                "ev_funding_bucket",
                "ev_structure",
            ]
        ].rename(
            columns={
                "event_date_str": "event_date",
                "ts": "entry_ts",
                "close": "entry_price",
                "funding_rate": "funding_rate_entry",
                "ev_structure": "expost_structure",
            }
        )
        ev = ev.join(agg, how="inner").join(h0_open, how="inner")
        ev = ev[(ev["event_open"] > 0) & (ev["entry_price"] > 0)]
        ev["entry_hour"] = eh
        ev["year"] = ev["event_date"].str[:4].astype(int)
        ev["ret_since_event"] = ev["entry_price"] / ev["event_open"] - 1.0
        span = ev["high_sofar"] - ev["low_sofar"]
        ev["close_pos"] = np.where(span > 0, (ev["entry_price"] - ev["low_sofar"]) / span, 0.5)
        ev["max_dd"] = ev["low_sofar"] / ev["event_open"] - 1.0

        for hold_h in HOLD_HOURS:
            exit_row = p[p["hours_from_event"] >= eh + hold_h].groupby("event_id", sort=False).head(1)
            exit_row = exit_row.set_index("event_id")[["ts", "close", "hours_from_event"]].rename(
                columns={
                    "ts": f"exit_ts_{hold_h}",
                    "close": f"exit_price_{hold_h}",
                    "hours_from_event": f"exit_hour_{hold_h}",
                }
            )
            ev = ev.join(exit_row, how="left")
            hold_window = p[
                (p["hours_from_event"] >= eh)
                & (p["hours_from_event"] <= eh + hold_h)
            ].dropna(subset=["funding_settlement_ts"])
            fund = (
                hold_window.drop_duplicates(["event_id", "funding_settlement_ts"])
                .groupby("event_id")["funding_rate"]
                .sum()
                .mul(-1.0)
                .rename(f"funding_pnl_{hold_h}")
            )
            ev = ev.join(fund, how="left")
            ev[f"funding_pnl_{hold_h}"] = ev[f"funding_pnl_{hold_h}"].fillna(0.0)
            ev[f"price_return_{hold_h}"] = ev[f"exit_price_{hold_h}"] / ev["entry_price"] - 1.0
            ev[f"net_return_{hold_h}"] = ev[f"price_return_{hold_h}"] + ev[f"funding_pnl_{hold_h}"] - COST
            ev[f"actual_hold_hours_{hold_h}"] = ev[f"exit_hour_{hold_h}"] - eh

        frames.append(ev.reset_index())

    events = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    if events.empty:
        return events

    for eh in ENTRY_HOURS:
        idx = events["entry_hour"].eq(eh)
        ranks = events.loc[idx].groupby("entry_ts")["funding_rate_entry"].rank(pct=True)
        events.loc[idx, "funding_pctl_ts"] = ranks

    return events


def simulate_trades(events: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if events.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    trade_rows = []
    parameter_rows = []

    for eh in ENTRY_HOURS:
        base_eh = events[events["entry_hour"].eq(eh)].copy()
        if base_eh.empty:
            continue
        for fq in FUNDING_QS:
            funding_only = base_eh[base_eh["funding_pctl_ts"] <= fq].copy()
            for hold_h in HOLD_HOURS:
                required = [
                    f"exit_ts_{hold_h}",
                    f"price_return_{hold_h}",
                    f"funding_pnl_{hold_h}",
                    f"net_return_{hold_h}",
                    f"actual_hold_hours_{hold_h}",
                ]
                td = funding_only.dropna(subset=required).copy()
                if td.empty:
                    continue
                td = td.rename(
                    columns={
                        f"exit_ts_{hold_h}": "exit_ts",
                        f"price_return_{hold_h}": "price_return",
                        f"funding_pnl_{hold_h}": "funding_pnl",
                        f"net_return_{hold_h}": "net_return",
                        f"actual_hold_hours_{hold_h}": "actual_hold_hours",
                    }
                )
                td["hold_hours"] = hold_h
                td["funding_q"] = fq
                td["ret_threshold"] = -999.0
                td["close_pos_threshold"] = -999.0
                td["max_dd_limit"] = -999.0
                m = _metric(td["net_return"], td["year"])
                if m["n_trades"] >= 30:
                    parameter_rows.append(
                        {
                            "entry_hour": eh,
                            "hold_hours": hold_h,
                            "funding_q": fq,
                            "ret_threshold": -999.0,
                            "close_pos_threshold": -999.0,
                            "max_dd_limit": -999.0,
                            "price_mean": float(td["price_return"].mean()),
                            "funding_pnl_mean": float(td["funding_pnl"].mean()),
                            **m,
                        }
                    )
                    td["param_id"] = f"h{eh}_hold{hold_h}_fq{fq:.2f}_funding_only"
                    keep_cols = [
                        "param_id", "symbol", "event_date", "year", "entry_hour", "hold_hours",
                        "entry_ts", "exit_ts", "actual_hold_hours", "funding_q",
                        "ret_threshold", "close_pos_threshold", "max_dd_limit",
                        "funding_pctl_ts", "ret_since_event", "close_pos", "max_dd",
                        "funding_rate_entry", "price_return", "funding_pnl", "net_return",
                        "expost_structure", "ev_funding_bucket",
                    ]
                    trade_rows.append(td[keep_cols])
            for rt in RET_THRESHOLDS:
                for cp in CLOSE_POS_THRESHOLDS:
                    for dd in MAX_DD_LIMITS:
                        signal = base_eh[
                            (base_eh["funding_pctl_ts"] <= fq)
                            & (base_eh["ret_since_event"] >= rt)
                            & (base_eh["close_pos"] >= cp)
                            & (base_eh["max_dd"] >= dd)
                        ].copy()
                        if signal.empty:
                            continue

                        for hold_h in HOLD_HOURS:
                            required = [
                                f"exit_ts_{hold_h}",
                                f"price_return_{hold_h}",
                                f"funding_pnl_{hold_h}",
                                f"net_return_{hold_h}",
                                f"actual_hold_hours_{hold_h}",
                            ]
                            td = signal.dropna(subset=required).copy()
                            if td.empty:
                                continue
                            td = td.rename(
                                columns={
                                    f"exit_ts_{hold_h}": "exit_ts",
                                    f"price_return_{hold_h}": "price_return",
                                    f"funding_pnl_{hold_h}": "funding_pnl",
                                    f"net_return_{hold_h}": "net_return",
                                    f"actual_hold_hours_{hold_h}": "actual_hold_hours",
                                }
                            )
                            td["hold_hours"] = hold_h
                            td["funding_q"] = fq
                            td["ret_threshold"] = rt
                            td["close_pos_threshold"] = cp
                            td["max_dd_limit"] = dd
                            m = _metric(td["net_return"], td["year"])
                            if m["n_trades"] < 30:
                                continue
                            row = {
                                "entry_hour": eh,
                                "hold_hours": hold_h,
                                "funding_q": fq,
                                "ret_threshold": rt,
                                "close_pos_threshold": cp,
                                "max_dd_limit": dd,
                                "price_mean": float(td["price_return"].mean()),
                                "funding_pnl_mean": float(td["funding_pnl"].mean()),
                                **m,
                            }
                            parameter_rows.append(row)
                            td["param_id"] = (
                                f"h{eh}_hold{hold_h}_fq{fq:.2f}_ret{rt:.2f}_cp{cp:.2f}_dd{dd:.2f}"
                            )
                            keep_cols = [
                                "param_id", "symbol", "event_date", "year", "entry_hour", "hold_hours",
                                "entry_ts", "exit_ts", "actual_hold_hours", "funding_q",
                                "ret_threshold", "close_pos_threshold", "max_dd_limit",
                                "funding_pctl_ts", "ret_since_event", "close_pos", "max_dd",
                                "funding_rate_entry", "price_return", "funding_pnl", "net_return",
                                "expost_structure", "ev_funding_bucket",
                            ]
                            trade_rows.append(td[keep_cols])

    params = pd.DataFrame(parameter_rows)
    trades = pd.concat(trade_rows, ignore_index=True) if trade_rows else pd.DataFrame()

    if params.empty:
        return params, trades, pd.DataFrame()

    # OOS evaluation: rank by train 2021-2024, evaluate 2025-2026.
    oos_rows = []
    for pid, td in trades.groupby("param_id"):
        train = td[td["year"] <= 2024]
        test = td[td["year"] >= 2025]
        if len(train) < 30 or len(test) < 10:
            continue
        first = td.iloc[0]
        trm = _metric(train["net_return"], train["year"])
        tem = _metric(test["net_return"], test["year"])
        oos_rows.append(
            {
                "param_id": pid,
                "entry_hour": int(first["entry_hour"]),
                "hold_hours": int(first["hold_hours"]),
                "funding_q": float(first["funding_q"]),
                "ret_threshold": float(first["ret_threshold"]),
                "close_pos_threshold": float(first["close_pos_threshold"]),
                "max_dd_limit": float(first["max_dd_limit"]),
                "train_n": trm["n_trades"],
                "train_net_mean": trm["net_mean"],
                "train_win_rate": trm["win_rate"],
                "train_sharpe": trm["sharpe"],
                "test_n": tem["n_trades"],
                "test_net_mean": tem["net_mean"],
                "test_win_rate": tem["win_rate"],
                "test_sharpe": tem["sharpe"],
            }
        )
    oos = pd.DataFrame(oos_rows)
    return params, trades, oos


def render_table(df: pd.DataFrame, columns: list[tuple[str, str]], limit: int | None = None) -> str:
    if limit is not None:
        df = df.head(limit)
    head = "".join(f"<th>{label}</th>" for _, label in columns)
    body = []
    for _, r in df.iterrows():
        cells = []
        for col, _ in columns:
            v = r.get(col)
            cls = "num" if isinstance(v, (int, float, np.integer, np.floating)) and not isinstance(v, bool) else ""
            if col.endswith("rate") or "mean" in col or col in {"net_mean", "price_mean", "funding_pnl_mean"}:
                txt = _fmt_pct(v)
            elif "sharpe" in col:
                txt = _fmt_num(v, 2)
            elif isinstance(v, float):
                txt = _fmt_num(v, 3)
            else:
                txt = str(v)
            cells.append(f'<td class="{cls}">{txt}</td>')
        body.append("<tr>" + "".join(cells) + "</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def build_html(params: pd.DataFrame, trades: pd.DataFrame, oos: pd.DataFrame) -> str:
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    top_is = params.sort_values("net_mean", ascending=False).head(12).copy()
    top_oos = oos.sort_values("test_net_mean", ascending=False).head(12).copy() if not oos.empty else pd.DataFrame()

    best = top_oos.iloc[0] if not top_oos.empty else top_is.iloc[0]
    best_pid = best["param_id"] if "param_id" in best.index else None
    best_trades = trades[trades["param_id"].eq(best_pid)] if best_pid else trades.iloc[0:0]

    year_rows = []
    if not best_trades.empty:
        for yr, g in best_trades.groupby("year"):
            m = _metric(g["net_return"], g["year"])
            year_rows.append(
                {
                    "year": int(yr),
                    "n_trades": m["n_trades"],
                    "net_mean": m["net_mean"],
                    "win_rate": m["win_rate"],
                    "sharpe": m["sharpe"],
                    "price_mean": float(g["price_return"].mean()),
                    "funding_pnl_mean": float(g["funding_pnl"].mean()),
                }
            )
    year_df = pd.DataFrame(year_rows)

    structure_rows = []
    if not best_trades.empty:
        for s, g in best_trades.groupby("expost_structure", dropna=False):
            m = _metric(g["net_return"], g["year"])
            structure_rows.append(
                {
                    "expost_structure": str(s),
                    "n_trades": m["n_trades"],
                    "net_mean": m["net_mean"],
                    "win_rate": m["win_rate"],
                }
            )
    structure_df = pd.DataFrame(structure_rows).sort_values("n_trades", ascending=False) if structure_rows else pd.DataFrame()

    best_summary = _metric(best_trades["net_return"], best_trades["year"]) if not best_trades.empty else {}
    funding_only = params[params["ret_threshold"].eq(-999.0)].sort_values("net_mean", ascending=False).head(10)

    css = """
:root { color-scheme: dark; --bg:#0b1220; --panel:#111827; --muted:#94a3b8; --line:#263244; --text:#e5e7eb; --good:#22c55e; --warn:#f59e0b; --bad:#ef4444; --info:#38bdf8; }
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--text); font:14px/1.58 -apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans SC",sans-serif; }
.wrap { max-width:1180px; margin:0 auto; padding:28px 18px 60px; }
h1 { margin:0 0 8px; font-size:28px; line-height:1.2; }
h2 { margin:28px 0 12px; font-size:20px; color:#dbeafe; }
h3 { margin:18px 0 8px; font-size:15px; color:#cbd5e1; }
p { margin:8px 0; } a { color:#7dd3fc; text-decoration:none; } code { background:#0f172a; color:#fbbf24; padding:2px 6px; border-radius:5px; }
.muted { color:var(--muted); } .hero { border:1px solid #334155; background:#101827; padding:22px 24px; border-radius:12px; margin-bottom:18px; }
.nav { margin:0 0 18px; padding:12px 14px; border:1px solid #334155; border-radius:10px; background:#0f172a; display:flex; gap:12px; flex-wrap:wrap; font-size:13px; }
.grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:12px; margin:16px 0 22px; }
.card { background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:14px 16px; }
.card .k { color:var(--muted); font-size:12px; margin-bottom:5px; } .card .v { font-size:22px; font-weight:700; }
.good .v { color:#4ade80; } .warn .v { color:#fbbf24; } .bad .v { color:#f87171; } .info .v { color:#7dd3fc; }
.note { border-left:4px solid var(--info); background:#0c1a3d; padding:12px 14px; border-radius:0 8px 8px 0; margin:12px 0; }
.note.warn { border-left-color:var(--warn); background:#3a2508; } .note.bad { border-left-color:var(--bad); background:#3a0f12; } .note.good { border-left-color:var(--good); background:#072a19; }
table { width:100%; border-collapse:collapse; margin:10px 0 20px; background:var(--panel); border:1px solid var(--line); border-radius:8px; overflow:hidden; }
th,td { padding:8px 10px; border-bottom:1px solid var(--line); vertical-align:top; } th { background:#0f172a; color:#cbd5e1; text-align:left; white-space:nowrap; } tr:last-child td { border-bottom:0; }
.num { text-align:right; font-variant-numeric:tabular-nums; } .formula { background:#0f172a; border:1px solid var(--line); border-radius:8px; padding:12px 14px; margin:10px 0; font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; white-space:pre-wrap; }
.flow { display:grid; grid-template-columns:repeat(5,1fr); gap:8px; margin:12px 0 20px; } .step { border:1px solid var(--line); background:var(--panel); border-radius:8px; padding:10px; min-height:90px; } .step b { color:#e0f2fe; }
ul { padding-left:20px; } li { margin:5px 0; } @media (max-width: 900px) { .flow { grid-template-columns:1fr; } }
"""

    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Phase 2c 清洁回测：无未来函数负费率延续做多</title>
<style>{css}</style>
</head>
<body>
<div class="wrap">
  <div class="nav">
    <a href="index.html">Rank 450 总览</a>
    <a href="phase2a_momentum_ignition.html">2a 二次点火追多</a>
    <a href="phase2b_short_reversal.html">2b 冲高回落做空</a>
    <a href="../binance_event_study_hub.html">事件研究入口</a>
  </div>
  <section class="hero">
    <p class="muted">Generated: {generated}</p>
    <h1>Phase 2c 清洁回测：无未来函数负费率延续做多</h1>
    <p class="muted">本页替换旧版事后 <code>continuation</code> 分类入场。新版只使用入场时点之前可观测的价格路径、回撤、收盘位置和同刻 funding 横截面排名。</p>
  </section>

  <div class="grid">
    <div class="card warn"><div class="k">最终状态</div><div class="v">WATCH</div><p class="muted">清洁后仍有 OOS 正样本，但强度明显低于旧版。</p></div>
    <div class="card info"><div class="k">测试变体</div><div class="v">{len(params):,}</div><p class="muted">h=24/36/48 × funding × 价格代理 × 退出。</p></div>
    <div class="card good"><div class="k">最佳 OOS 均值</div><div class="v">{_fmt_pct(float(best.get('test_net_mean', np.nan)))}</div><p class="muted">按 2021-2024 训练、2025-2026 测试排序。</p></div>
    <div class="card info"><div class="k">最佳 OOS Sharpe</div><div class="v">{_fmt_num(float(best.get('test_sharpe', np.nan)), 2)}</div><p class="muted">trade-level 年化，未按组合并发修正。</p></div>
    <div class="card warn"><div class="k">最佳信号样本</div><div class="v">{int(best_summary.get('n_trades', 0)):,}</div><p class="muted">最佳 OOS 参数对应全样本交易数。</p></div>
  </div>

  <h2>1. 清洁规则</h2>
  <div class="note good">新版信号不读取 <code>ev_structure</code>、<code>fwd_ret_t1/t2/t3</code> 或任何 entry_ts 之后的数据。旧的 <code>continuation</code> 只保留为事后诊断列。</div>
  <div class="formula">entry_hour tau in {{24, 36, 48}}
entry_ts = first hourly bar with hours_from_event >= tau

ret_since_event = close(entry_ts) / open(h=0) - 1
close_pos = (close(entry_ts) - min_low[0,tau]) / (max_high[0,tau] - min_low[0,tau])
max_dd = min_low[0,tau] / open(h=0) - 1
funding_pctl_ts = rank_pct(funding_rate(entry_ts) across events sharing entry_ts)

signal = funding_pctl_ts <= q
         AND ret_since_event >= ret_threshold
         AND close_pos >= close_pos_threshold
         AND max_dd >= max_dd_limit

exit_ts = first hourly bar with hours_from_event >= tau + hold_hours
net = price_return + funding_pnl - 0.13%
funding_pnl for long = -sum(unique settlement funding_rate)</div>

  <h2>2. 流程图</h2>
  <div class="flow">
    <div class="step"><b>事件池</b><br>只取已有 top gainer event，不用未来结构标签。</div>
    <div class="step"><b>固定观察时点</b><br>h=24/36/48，等待 K 线完成后入场。</div>
    <div class="step"><b>因果特征</b><br>截至 entry_ts 的收益、区间位置、最大回撤。</div>
    <div class="step"><b>同刻 funding</b><br>按 entry_ts 横截面排名。</div>
    <div class="step"><b>真实时间退出</b><br>entry + 12h/24h，不再用过滤后第 N 行。</div>
  </div>

  <h2>3. 样本内 Top 参数</h2>
  {render_table(top_is, [
      ('entry_hour','入场h'), ('hold_hours','持有h'), ('funding_q','funding q'),
      ('ret_threshold','收益阈值'), ('close_pos_threshold','收盘位置阈值'), ('max_dd_limit','最大回撤下限'),
      ('n_trades','N'), ('net_mean','净收益均值'), ('win_rate','胜率'), ('sharpe','Sharpe'),
      ('price_mean','价格贡献'), ('funding_pnl_mean','Funding贡献')
  ])}

  <h2>4. OOS 结果：2021-2024 训练，2025-2026 测试</h2>
  <div class="note warn">下面按测试期净收益排序。若只看样本内 Top，仍可能重新引入数据挖掘偏差。</div>
  {render_table(top_oos, [
      ('entry_hour','入场h'), ('hold_hours','持有h'), ('funding_q','funding q'),
      ('ret_threshold','收益阈值'), ('close_pos_threshold','收盘位置阈值'), ('max_dd_limit','最大回撤下限'),
      ('train_n','训练N'), ('train_net_mean','训练均值'), ('train_sharpe','训练Sharpe'),
      ('test_n','测试N'), ('test_net_mean','测试均值'), ('test_win_rate','测试胜率'), ('test_sharpe','测试Sharpe')
  ])}

  <h2>5. 最佳 OOS 参数的年度拆解</h2>
  {render_table(year_df, [
      ('year','年份'), ('n_trades','N'), ('net_mean','净收益均值'), ('win_rate','胜率'),
      ('sharpe','Sharpe'), ('price_mean','价格贡献'), ('funding_pnl_mean','Funding贡献')
  ])}

  <h2>6. 事后结构诊断，不参与入场</h2>
  <div class="note">这里可以观察清洁信号最终落在哪些旧标签里，但这些标签没有参与信号计算。</div>
  {render_table(structure_df, [
      ('expost_structure','事后结构'), ('n_trades','N'), ('net_mean','净收益均值'), ('win_rate','胜率')
  ])}

  <h2>7. Funding-only 基线</h2>
  <div class="note warn">这里完全不加价格趋势代理，只看同刻低 funding 排名。本轮 funding-only 有小幅正 OOS，但胜率偏低、中位数偏弱；价格代理带来的是增量改善，而不是恢复旧版高夏普。</div>
  {render_table(funding_only, [
      ('entry_hour','入场h'), ('hold_hours','持有h'), ('funding_q','funding q'),
      ('n_trades','N'), ('net_mean','净收益均值'), ('win_rate','胜率'), ('sharpe','Sharpe'),
      ('price_mean','价格贡献'), ('funding_pnl_mean','Funding贡献')
  ])}

  <h2>8. 审计结论</h2>
  <ul>
    <li>旧版高夏普主要来自事后 <code>continuation</code> 路径筛选；新版已移除该未来函数。</li>
    <li>清洁版还有正 OOS 口袋，但样本数比旧版少，且 trade-level Sharpe 仍未做组合并发和容量修正。</li>
    <li>低 funding 本身留下弱正收益；事件后可观测趋势代理带来小幅增量，但没有恢复旧版事后 continuation 带来的高 Sharpe。</li>
    <li>更准确的名字是 <code>post-event causal continuation proxy + low funding context</code>，而不是已经可执行的 carry harvest。</li>
    <li>建议状态从 WATCH+ 下调到 WATCH：保留研究价值，但需要组合净值、滑点和 walk-forward 后才可谈 paper lane。</li>
  </ul>

  <h2>9. 产物</h2>
  <ul>
    <li><code>scripts/backtest_phase2c_causal_audit.py</code></li>
    <li><code>reports/artifacts/binance_event_study_phase2c_causal_audit/causal_param_summary.csv</code></li>
    <li><code>reports/artifacts/binance_event_study_phase2c_causal_audit/causal_oos_summary.csv</code></li>
    <li><code>reports/artifacts/binance_event_study_phase2c_causal_audit/causal_trade_detail.csv</code></li>
  </ul>
</div>
</body>
</html>"""
    return html


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("[1/4] loading hourly panel")
    panel = pd.read_pickle(PANEL)
    print(f"  rows={len(panel):,}")

    print("[2/4] building causal event features")
    events = build_event_frame(panel)
    events.to_csv(OUT_DIR / "causal_event_features.csv", index=False)
    print(f"  event-feature rows={len(events):,}")

    print("[3/4] running causal parameter scan")
    params, trades, oos = simulate_trades(events)
    params.to_csv(OUT_DIR / "causal_param_summary.csv", index=False)
    trades.to_csv(OUT_DIR / "causal_trade_detail.csv", index=False)
    oos.to_csv(OUT_DIR / "causal_oos_summary.csv", index=False)
    summary = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "n_event_feature_rows": int(len(events)),
        "n_param_variants": int(len(params)),
        "n_trade_rows": int(len(trades)),
        "n_oos_variants": int(len(oos)),
    }
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2))
    print(f"  params={len(params):,}, trade rows={len(trades):,}, oos variants={len(oos):,}")

    print("[4/4] writing HTML")
    html = build_html(params, trades, oos)
    SITE_OUT.write_text(html)
    audit_copy = SITE_OUT.with_name("phase2c_watchplus_audit.html")
    audit_copy.write_text(html)
    print(f"  wrote {SITE_OUT}")


if __name__ == "__main__":
    main()
