#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank213_largecap_xs_jump_veto"
SITE_PATH = ROOT / "reports" / "site" / "paper" / "rank213_largecap_xs_jump_veto_fee_sensitivity_review.html"

ASOF_DETAIL_PATH = ART_DIR / "rank213_asof_universe_long_history_detail.csv"
FREEZE_PATH = ART_DIR / "rank213_formal_strategy_freeze_summary.json"

SUMMARY_PATH = ART_DIR / "rank213_fee_sensitivity_review_summary.json"
TABLE_PATH = ART_DIR / "rank213_fee_sensitivity_review_table.csv"

COST_BPS_LIST = [4, 6, 8, 10, 12, 16]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def to_iso(ts: pd.Timestamp) -> str:
    return ts.tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def fmt_pct(x: float, digits: int = 2) -> str:
    if pd.isna(x):
        return ""
    return f"{x:.{digits}f}%"


def fmt_bps(x: float, digits: int = 2) -> str:
    if pd.isna(x):
        return ""
    return f"{x:.{digits}f} bps"


def max_drawdown(ret: pd.Series) -> float:
    if ret.empty:
        return np.nan
    eq = (1.0 + ret).cumprod()
    dd = eq / eq.cummax() - 1.0
    return float(dd.min())


def calc_stats(ret: pd.Series, turnover: pd.Series, gate_on: pd.Series | None = None) -> dict:
    if ret.empty:
        return {
            "rebalances": 0,
            "net_mean_bps": np.nan,
            "net_cum_pct": np.nan,
            "max_drawdown_pct": np.nan,
            "win_rate_pct": np.nan,
            "avg_turnover_x": np.nan,
            "gate_on_rate_pct": np.nan,
        }
    if gate_on is None:
        gate_on_rate_pct = 100.0
    else:
        gate_on_rate_pct = float(pd.Series(gate_on).astype(bool).mean() * 100.0)
    return {
        "rebalances": int(len(ret)),
        "net_mean_bps": float(ret.mean() * 10000.0),
        "net_cum_pct": float(((1.0 + ret).prod() - 1.0) * 100.0),
        "max_drawdown_pct": float(max_drawdown(ret) * 100.0),
        "win_rate_pct": float((ret > 0).mean() * 100.0),
        "avg_turnover_x": float(turnover.mean()),
        "gate_on_rate_pct": gate_on_rate_pct,
    }


def render_table(df: pd.DataFrame, pct_cols: set[str] | None = None, bps_cols: set[str] | None = None, x_cols: set[str] | None = None) -> str:
    pct_cols = pct_cols or set()
    bps_cols = bps_cols or set()
    x_cols = x_cols or set()
    if df.empty:
        return "<p class='muted'>暂无数据。</p>"

    headers = "".join(f"<th>{c}</th>" for c in df.columns)
    body = []
    for _, row in df.iterrows():
        tds = []
        for c in df.columns:
            v = row[c]
            if pd.isna(v):
                txt = ""
            elif c in pct_cols:
                txt = fmt_pct(float(v))
            elif c in bps_cols:
                txt = fmt_bps(float(v))
            elif c in x_cols:
                txt = f"{float(v):.3f}x"
            elif isinstance(v, (float, np.floating)):
                txt = f"{float(v):.4f}"
            else:
                txt = str(v)
            tds.append(f"<td>{txt}</td>")
        body.append("<tr>" + "".join(tds) + "</tr>")

    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def apply_frozen_gate(detail: pd.DataFrame, freeze: dict) -> pd.DataFrame:
    gate = freeze["gate"]
    rules = gate["rules"]
    vote_ratio = float(gate.get("vote_ratio", 0.67))
    lookback_days = int(gate.get("lookback_days", 30))

    out = detail.copy().sort_values("timestamp_ts").reset_index(drop=True)
    out["timestamp_ts"] = pd.to_datetime(out["timestamp_ts"], utc=True)
    out["exit_ts"] = pd.to_datetime(out["exit_ts"], utc=True, errors="coerce")

    veto_active_rate = (pd.to_numeric(out["veto_count"], errors="coerce").fillna(0) > 0).astype(float).to_numpy()
    xs_dispersion_bps = pd.to_numeric(out["universe_cumret_std"], errors="coerce").astype(float).to_numpy() * 10000.0
    ls_divergence_bps = (
        pd.to_numeric(out["long_price_contrib"], errors="coerce").astype(float).to_numpy()
        - pd.to_numeric(out["veto_short_price_contrib"], errors="coerce").astype(float).to_numpy()
    ) * 10000.0

    ts_ns = out["timestamp_ts"].astype("int64").to_numpy()
    exit_ns = out["exit_ts"].astype("int64").to_numpy()
    start_ns = ts_ns - pd.Timedelta(days=lookback_days).value
    start_ixs = np.searchsorted(ts_ns, start_ns, side="left")
    end_decision_ixs = np.arange(len(out), dtype=int)
    end_realized_ixs = np.searchsorted(exit_ns, ts_ns, side="right") - 1

    def window_mean(values: np.ndarray, end_ixs: np.ndarray) -> np.ndarray:
        valid = np.isfinite(values)
        csum = np.concatenate([[0.0], np.cumsum(np.where(valid, values, 0.0))])
        ccnt = np.concatenate([[0], np.cumsum(valid.astype(int))])
        res = np.full(len(values), np.nan, dtype=float)
        for i, (start_ix, end_ix) in enumerate(zip(start_ixs, end_ixs)):
            if end_ix < start_ix or end_ix < 0:
                continue
            total = csum[end_ix + 1] - csum[start_ix]
            count = ccnt[end_ix + 1] - ccnt[start_ix]
            if count > 0:
                res[i] = total / count
        return res

    out["gate_feature_veto_active_rate"] = window_mean(veto_active_rate, end_decision_ixs)
    out["gate_feature_xs_dispersion_bps"] = window_mean(xs_dispersion_bps, end_decision_ixs)
    out["gate_feature_ls_divergence_bps"] = window_mean(ls_divergence_bps, end_realized_ixs)

    gate_on = []
    votes_list = []
    valid_list = []
    needed_list = []

    for _, row in out.iterrows():
        votes = 0
        valid = 0
        for rule in rules:
            var = str(rule["variable"])
            col = f"gate_feature_{var}"
            val = row[col] if col in out.columns else np.nan
            if pd.isna(val):
                continue
            valid += 1
            if bool(rule["higher_is_good"]):
                ok = bool(float(val) >= float(rule["threshold"]))
            else:
                ok = bool(float(val) <= float(rule["threshold"]))
            votes += int(ok)

        needed = max(1, int(np.ceil(valid * vote_ratio))) if valid > 0 else 1
        on = bool(votes >= needed) if valid > 0 else False
        gate_on.append(on)
        votes_list.append(votes)
        valid_list.append(valid)
        needed_list.append(needed)

    out["gate_on"] = gate_on
    out["gate_votes"] = votes_list
    out["gate_valid_rules"] = valid_list
    out["gate_needed_votes"] = needed_list
    return out


def interpolate_zero(costs: list[float], values: list[float]) -> float | None:
    if not costs or not values or len(costs) != len(values):
        return None
    pairs = sorted(zip(costs, values), key=lambda x: x[0])
    costs_s = [p[0] for p in pairs]
    vals_s = [p[1] for p in pairs]

    if all(v > 0 for v in vals_s):
        return None
    if all(v <= 0 for v in vals_s):
        return costs_s[0]

    for i in range(1, len(vals_s)):
        v0, v1 = vals_s[i - 1], vals_s[i]
        c0, c1 = costs_s[i - 1], costs_s[i]
        if v0 == 0:
            return c0
        if v0 > 0 and v1 <= 0:
            if c1 == c0:
                return c0
            return c0 + (0 - v0) * (c1 - c0) / (v1 - v0)
    return None


def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_PATH.parent)

    freeze = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
    detail = pd.read_csv(ASOF_DETAIL_PATH)
    detail = apply_frozen_gate(detail, freeze)

    detail["plain_gross"] = pd.to_numeric(detail["plain_gross"], errors="coerce")
    detail["veto_gross"] = pd.to_numeric(detail["veto_gross"], errors="coerce")
    detail["plain_turnover_x"] = pd.to_numeric(detail["plain_turnover_x"], errors="coerce")
    detail["veto_turnover_x"] = pd.to_numeric(detail["veto_turnover_x"], errors="coerce")

    rows = []
    for cost_bps in COST_BPS_LIST:
        unit = float(cost_bps) / 10000.0

        plain_ret = detail["plain_gross"] - detail["plain_turnover_x"] * unit
        veto_ret = detail["veto_gross"] - detail["veto_turnover_x"] * unit
        gate_ret = np.where(detail["gate_on"], veto_ret, 0.0)

        plain_stats = calc_stats(plain_ret, detail["plain_turnover_x"])
        veto_stats = calc_stats(veto_ret, detail["veto_turnover_x"])
        gate_stats = calc_stats(pd.Series(gate_ret), pd.Series(np.where(detail["gate_on"], detail["veto_turnover_x"], 0.0)), gate_on=detail["gate_on"])

        rows.extend([
            {"cost_bps": float(cost_bps), "strategy": "plain baseline", **plain_stats},
            {"cost_bps": float(cost_bps), "strategy": "baseline+veto", **veto_stats},
            {"cost_bps": float(cost_bps), "strategy": "baseline+veto+gate", **gate_stats},
        ])

    table = pd.DataFrame(rows)
    TABLE_PATH.write_text(table.to_csv(index=False), encoding="utf-8")

    gate_only = table[table["strategy"] == "baseline+veto+gate"].sort_values("cost_bps")
    gate_costs = gate_only["cost_bps"].tolist()
    gate_mean = gate_only["net_mean_bps"].tolist()
    gate_cum = gate_only["net_cum_pct"].tolist()

    breakeven_mean = interpolate_zero(gate_costs, gate_mean)
    breakeven_cum = interpolate_zero(gate_costs, gate_cum)

    plain_best = float(table[table["strategy"] == "plain baseline"]["net_cum_pct"].max())
    veto_best = float(table[table["strategy"] == "baseline+veto"]["net_cum_pct"].max())

    if breakeven_mean is None:
        gate_verdict = "在测试区间内（到16bps）gate 线仍保持 net_mean 为正。"
    elif breakeven_mean <= min(COST_BPS_LIST):
        gate_verdict = "gate 线在最低测试成本附近已接近或低于 break-even。"
    else:
        gate_verdict = f"gate 线 net_mean 的临界成本约在 {breakeven_mean:.2f} bps×turnover。"

    verdict_lines = [
        f"plain baseline 在测试成本下累计收益最高为 {plain_best:.2f}%（未转正）。",
        f"baseline+veto 在测试成本下累计收益最高为 {veto_best:.2f}%（未转正）。",
        gate_verdict,
    ]
    if breakeven_cum is not None and breakeven_cum > min(COST_BPS_LIST):
        verdict_lines.append(f"按累计收益口径，gate 线临界成本约在 {breakeven_cum:.2f} bps×turnover。")

    summary = {
        "scope": "fee sensitivity under frozen baseline/veto/gate definitions; only transaction cost changes",
        "source_paths": {
            "asof_detail": str(ASOF_DETAIL_PATH.relative_to(ROOT)),
            "frozen_rules": str(FREEZE_PATH.relative_to(ROOT)),
        },
        "cost_bps_tested": COST_BPS_LIST,
        "sample": {
            "start_utc": to_iso(pd.to_datetime(detail["timestamp_ts"], utc=True).min()),
            "end_utc": to_iso(pd.to_datetime(detail["timestamp_ts"], utc=True).max()),
            "rebalances": int(len(detail)),
            "gate_on_rate_pct": float(pd.Series(detail["gate_on"]).mean() * 100.0),
        },
        "table_csv": str(TABLE_PATH.relative_to(ROOT)),
        "breakeven_estimate": {
            "baseline_plus_veto_plus_gate_net_mean_bps": breakeven_mean,
            "baseline_plus_veto_plus_gate_net_cum_pct": breakeven_cum,
        },
        "final_answer": {
            "plain_has_profit_room_under_tested_fees": bool(plain_best > 0),
            "veto_has_profit_room_under_tested_fees": bool(veto_best > 0),
            "gate_has_profit_room_under_tested_fees": bool(gate_only["net_cum_pct"].max() > 0),
            "verdict_lines": verdict_lines,
        },
    }
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # html rendering
    view = table[[
        "cost_bps", "strategy", "net_mean_bps", "net_cum_pct", "max_drawdown_pct", "win_rate_pct", "avg_turnover_x", "gate_on_rate_pct"
    ]].copy()

    table_html = render_table(
        view,
        pct_cols={"net_cum_pct", "max_drawdown_pct", "win_rate_pct", "gate_on_rate_pct"},
        bps_cols={"net_mean_bps"},
        x_cols={"avg_turnover_x"},
    )

    verdict_html = "<br/>".join(verdict_lines)

    html = f"""<!doctype html>
<html lang='zh-CN'>
<head>
<meta charset='utf-8' />
<meta name='viewport' content='width=device-width, initial-scale=1' />
<title>Rank213 fee sensitivity review</title>
<style>
:root{{--bg:#f8fafc;--card:#fff;--fg:#0f172a;--muted:#64748b;--line:#e2e8f0;--ok:#166534;--okbg:#dcfce7;--warn:#9a3412;--warnbg:#ffedd5}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.65 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}}
.wrap{{max-width:1200px;margin:0 auto;padding:28px 18px 64px}} .card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin-bottom:14px}}
h1,h2{{margin:0 0 12px}} .muted{{color:var(--muted)}}
.note{{border-left:4px solid #1d4ed8;background:#dbeafe;padding:12px 14px;border-radius:10px;white-space:pre-wrap}}
.warn{{border-left:4px solid var(--warn);background:var(--warnbg);padding:12px 14px;border-radius:10px;white-space:pre-wrap}}
table{{width:100%;border-collapse:collapse}} th,td{{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}} th{{background:#f8fafc}}
code{{background:#eff6ff;border-radius:6px;padding:2px 6px}} a{{color:#0f766e;text-decoration:none}} a:hover{{text-decoration:underline}}
</style>
</head>
<body><div class='wrap'>
<div class='card'>
  <h1>Rank213 fee_sensitivity_review</h1>
  <p>冻结 baseline / veto / gate 定义不变，仅改变成本口径（bps × turnover）。</p>
  <p><a href='/momentum/paper/rank213_largecap_xs_jump_veto_formal_strategy_review.html'>formal_strategy_review</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_family_operating_board.html'>family_operating_board</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto.html'>runner</a></p>
</div>

<div class='card'>
  <h2>测试结果</h2>
  {table_html}
  <p class='muted'>table csv: <code>{TABLE_PATH.relative_to(ROOT)}</code></p>
</div>

<div class='card'>
  <h2>结论（你关心的问题）</h2>
  <div class='warn'>{verdict_html}</div>
  <div class='note'>
    gate_on_rate 说明：
    - plain / baseline+veto 无 gate 过滤，按 100% 记。
    - baseline+veto+gate 按冻结 gate 实际 ON 比例统计。
  </div>
</div>
</div></body></html>
"""
    SITE_PATH.write_text(html, encoding="utf-8")

    print(json.dumps({
        "summary_json": str(SUMMARY_PATH.relative_to(ROOT)),
        "table_csv": str(TABLE_PATH.relative_to(ROOT)),
        "html": str(SITE_PATH.relative_to(ROOT)),
        "breakeven_mean_bps": breakeven_mean,
        "breakeven_cum_bps": breakeven_cum,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
