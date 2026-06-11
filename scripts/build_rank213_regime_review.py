#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank213_largecap_xs_jump_veto"
SITE_PATH = ROOT / "reports" / "site" / "paper" / "rank213_largecap_xs_jump_veto_regime_review.html"

ASOF_DETAIL_PATH = ART_DIR / "rank213_asof_universe_long_history_detail.csv"
ASOF_SUMMARY_PATH = ART_DIR / "rank213_asof_universe_long_history_review_summary.json"
FUNDING_DETAIL_PATH = ART_DIR / "rank213_long_history_with_funding_detail.csv"
FUNDING_SUMMARY_PATH = ART_DIR / "rank213_long_history_with_funding_review_summary.json"
PERF_SUMMARY_PATH = ART_DIR / "rank213_performance_review_summary.json"

OUT_SUMMARY_PATH = ART_DIR / "rank213_regime_review_summary.json"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def fmt_pct(x: float, digits: int = 2) -> str:
    return f"{x:.{digits}f}%"


def fmt_bps(x: float, digits: int = 2) -> str:
    return f"{x:.{digits}f} bps"


def to_iso(ts: pd.Timestamp) -> str:
    return ts.tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def compound_ret(x: pd.Series) -> float:
    if x.empty:
        return np.nan
    return float((1.0 + x).prod() - 1.0)


def cohen_d(a: pd.Series, b: pd.Series) -> float:
    a = a.dropna()
    b = b.dropna()
    if len(a) < 2 or len(b) < 2:
        return np.nan
    va = float(a.var(ddof=1))
    vb = float(b.var(ddof=1))
    pooled = (((len(a) - 1) * va + (len(b) - 1) * vb) / (len(a) + len(b) - 2)) ** 0.5
    if pooled == 0:
        return 0.0
    return float((a.mean() - b.mean()) / pooled)


def render_table(df: pd.DataFrame, percent_cols: set[str] | None = None, bps_cols: set[str] | None = None) -> str:
    percent_cols = percent_cols or set()
    bps_cols = bps_cols or set()
    if df.empty:
        return "<p class='muted'>暂无数据。</p>"
    headers = "".join(f"<th>{c}</th>" for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cols = []
        for c in df.columns:
            v = row[c]
            if pd.isna(v):
                txt = ""
            elif c in percent_cols:
                txt = fmt_pct(float(v))
            elif c in bps_cols:
                txt = fmt_bps(float(v))
            elif isinstance(v, (float, np.floating)):
                txt = f"{float(v):.4f}"
            else:
                txt = str(v)
            cols.append(f"<td>{txt}</td>")
        rows.append("<tr>" + "".join(cols) + "</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_PATH.parent)

    if not ASOF_DETAIL_PATH.exists():
        raise RuntimeError(f"missing {ASOF_DETAIL_PATH}")

    asof = pd.read_csv(ASOF_DETAIL_PATH)
    asof["timestamp_ts"] = pd.to_datetime(asof["timestamp_ts"], utc=True)
    asof["year"] = pd.to_numeric(asof["year"], errors="coerce")

    required_cols = [
        "btc_cumret", "universe_cumret_std", "universe_realized_vol_median",
        "long_price_contrib", "veto_short_price_contrib"
    ]
    miss = [c for c in required_cols if c not in asof.columns]
    if miss:
        raise RuntimeError(f"as-of detail missing required columns: {miss}; rerun as-of builder first")

    asof["plain_net_bps"] = asof["plain_net"] * 10000.0
    asof["veto_net_bps"] = asof["veto_net"] * 10000.0
    asof["delta_net_bps"] = asof["veto_net_bps"] - asof["plain_net_bps"]
    asof["btc_trend_64_bps"] = asof["btc_cumret"] * 10000.0
    asof["xs_dispersion_bps"] = asof["universe_cumret_std"] * 10000.0
    asof["realized_vol_bps"] = asof["universe_realized_vol_median"] * 10000.0
    asof["ls_divergence_bps"] = (asof["long_price_contrib"] - asof["veto_short_price_contrib"]) * 10000.0
    asof["veto_active"] = (asof["veto_count"] > 0).astype(float)

    monthly = (
        asof.groupby(["month", "year"], as_index=False)
        .agg(
            rebalances=("month", "size"),
            plain_monthly_net=("plain_net", compound_ret),
            veto_monthly_net=("veto_net", compound_ret),
            plain_net_mean_bps=("plain_net_bps", "mean"),
            veto_net_mean_bps=("veto_net_bps", "mean"),
            delta_net_mean_bps=("delta_net_bps", "mean"),
            avg_universe_size=("eligible_universe_size", "mean"),
            veto_active_rate=("veto_active", "mean"),
            btc_trend_64_bps=("btc_trend_64_bps", "mean"),
            xs_dispersion_bps=("xs_dispersion_bps", "mean"),
            realized_vol_bps=("realized_vol_bps", "mean"),
            ls_divergence_bps=("ls_divergence_bps", "mean"),
        )
        .sort_values("month")
        .reset_index(drop=True)
    )

    if FUNDING_DETAIL_PATH.exists():
        fund = pd.read_csv(FUNDING_DETAIL_PATH)
        fund["timestamp_ts"] = pd.to_datetime(fund["timestamp_ts"], utc=True)
        fund["month"] = fund["timestamp_ts"].dt.strftime("%Y-%m")
        fund_month = (
            fund.groupby("month", as_index=False)
            .agg(
                veto_funding_mean_bps=("veto_funding_ret", lambda x: float(pd.Series(x).mean() * 10000.0)),
                plain_funding_mean_bps=("plain_funding_ret", lambda x: float(pd.Series(x).mean() * 10000.0)),
                funding_delta_bps=("veto_funding_ret", lambda x: float(pd.Series(x).mean() * 10000.0)),
            )
        )
        monthly = monthly.merge(fund_month, on="month", how="left")

    bad = monthly[(monthly["year"].isin([2023, 2024])) & (monthly["veto_monthly_net"] < 0)].copy()
    good = monthly[(monthly["year"].isin([2025, 2026])) & (monthly["veto_monthly_net"] > 0)].copy()

    vars_for_sep = [
        "btc_trend_64_bps",
        "xs_dispersion_bps",
        "realized_vol_bps",
        "ls_divergence_bps",
        "veto_active_rate",
        "delta_net_mean_bps",
    ]
    if "veto_funding_mean_bps" in monthly.columns:
        vars_for_sep.append("veto_funding_mean_bps")

    sep_rows = []
    for v in vars_for_sep:
        d = cohen_d(good[v], bad[v])
        g = float(good[v].mean()) if not good[v].dropna().empty else np.nan
        b = float(bad[v].mean()) if not bad[v].dropna().empty else np.nan
        sep_rows.append({
            "variable": v,
            "good_mean": g,
            "bad_mean": b,
            "good_minus_bad": g - b if pd.notna(g) and pd.notna(b) else np.nan,
            "effect_size_d": d,
            "direction": "higher_in_good" if pd.notna(g) and pd.notna(b) and g > b else "lower_in_good",
        })
    sep = pd.DataFrame(sep_rows)
    sep["abs_d"] = sep["effect_size_d"].abs()
    sep = sep.sort_values(["abs_d", "variable"], ascending=[False, True]).reset_index(drop=True)

    # current live environment: last 30 days in as-of timeline
    latest_ts = asof["timestamp_ts"].max()
    cur_cut = latest_ts - pd.Timedelta(days=30)
    cur = asof[asof["timestamp_ts"] >= cur_cut].copy()

    cur_env = {
        "start_utc": to_iso(cur["timestamp_ts"].min()),
        "end_utc": to_iso(cur["timestamp_ts"].max()),
        "rebalances": int(len(cur)),
        "veto_net_mean_bps": float(cur["veto_net_bps"].mean()),
        "delta_net_mean_bps": float(cur["delta_net_bps"].mean()),
        "btc_trend_64_bps": float(cur["btc_trend_64_bps"].mean()),
        "xs_dispersion_bps": float(cur["xs_dispersion_bps"].mean()),
        "realized_vol_bps": float(cur["realized_vol_bps"].mean()),
        "ls_divergence_bps": float(cur["ls_divergence_bps"].mean()),
        "veto_active_rate": float(cur["veto_active"].mean()),
    }

    # distance to regime centroids
    dist_vars = [v for v in ["btc_trend_64_bps", "xs_dispersion_bps", "realized_vol_bps", "ls_divergence_bps", "veto_active_rate"] if v in monthly.columns]
    good_cent = good[dist_vars].mean(numeric_only=True)
    bad_cent = bad[dist_vars].mean(numeric_only=True)
    pool = monthly[dist_vars]
    pool_std = pool.std(numeric_only=True).replace(0, np.nan)

    cur_vec = pd.Series({v: cur_env[v] for v in dist_vars})
    z_good = (cur_vec - good_cent) / pool_std
    z_bad = (cur_vec - bad_cent) / pool_std
    dist_good = float(np.sqrt(np.nansum(z_good.values.astype(float) ** 2)))
    dist_bad = float(np.sqrt(np.nansum(z_bad.values.astype(float) ** 2)))
    live_like = "2025/2026 positive regime" if dist_good <= dist_bad else "2023/2024 negative regime"

    # simple explanatory gate from top 3 separative vars (non-strategy, no parameter retune)
    top_sep = sep.dropna(subset=["effect_size_d"]).head(3).copy()
    gate_rules = []
    for _, r in top_sep.iterrows():
        var = r["variable"]
        g = float(r["good_mean"])
        b = float(r["bad_mean"])
        thr = (g + b) / 2.0
        higher_good = g > b
        gate_rules.append({
            "variable": var,
            "threshold": thr,
            "higher_is_good": higher_good,
            "good_mean": g,
            "bad_mean": b,
        })

    def month_gate_on(row: pd.Series) -> bool:
        votes = 0
        valid = 0
        for rule in gate_rules:
            var = rule["variable"]
            if pd.isna(row.get(var, np.nan)):
                continue
            valid += 1
            if rule["higher_is_good"]:
                votes += int(float(row[var]) >= rule["threshold"])
            else:
                votes += int(float(row[var]) <= rule["threshold"])
        if valid == 0:
            return False
        return votes >= max(1, int(np.ceil(valid * 0.67)))

    monthly["gate_on"] = monthly.apply(month_gate_on, axis=1)
    gate_on = monthly[monthly["gate_on"]]
    gate_off = monthly[~monthly["gate_on"]]
    gate_stats = {
        "on_months": int(len(gate_on)),
        "off_months": int(len(gate_off)),
        "on_veto_monthly_mean_pct": float(gate_on["veto_monthly_net"].mean() * 100.0) if len(gate_on) else np.nan,
        "off_veto_monthly_mean_pct": float(gate_off["veto_monthly_net"].mean() * 100.0) if len(gate_off) else np.nan,
        "on_veto_monthly_win_rate": float((gate_on["veto_monthly_net"] > 0).mean() * 100.0) if len(gate_on) else np.nan,
        "off_veto_monthly_win_rate": float((gate_off["veto_monthly_net"] > 0).mean() * 100.0) if len(gate_off) else np.nan,
    }

    current_gate_checks = []
    current_gate_votes = 0
    current_gate_valid = 0
    for rule in gate_rules:
        var = rule["variable"]
        val = cur_env.get(var, np.nan)
        if pd.isna(val):
            current_gate_checks.append({
                "variable": var,
                "value": np.nan,
                "threshold": float(rule["threshold"]),
                "higher_is_good": bool(rule["higher_is_good"]),
                "pass": False,
                "valid": False,
            })
            continue
        if rule["higher_is_good"]:
            ok = bool(float(val) >= float(rule["threshold"]))
        else:
            ok = bool(float(val) <= float(rule["threshold"]))
        current_gate_valid += 1
        current_gate_votes += int(ok)
        current_gate_checks.append({
            "variable": var,
            "value": float(val),
            "threshold": float(rule["threshold"]),
            "higher_is_good": bool(rule["higher_is_good"]),
            "pass": ok,
            "valid": True,
        })

    current_gate_needed = max(1, int(np.ceil(current_gate_valid * 0.67))) if current_gate_valid > 0 else 1
    current_gate_on = bool(current_gate_votes >= current_gate_needed) if current_gate_valid > 0 else False

    perf = json.loads(PERF_SUMMARY_PATH.read_text(encoding="utf-8")) if PERF_SUMMARY_PATH.exists() else {}
    funding_summary = json.loads(FUNDING_SUMMARY_PATH.read_text(encoding="utf-8")) if FUNDING_SUMMARY_PATH.exists() else {}
    asof_summary = json.loads(ASOF_SUMMARY_PATH.read_text(encoding="utf-8")) if ASOF_SUMMARY_PATH.exists() else {}

    q1 = {
        "period": "2023/2024 且月度 veto 为负",
        "months": int(len(bad)),
        "environment": {
            "btc_trend_64_bps": float(bad["btc_trend_64_bps"].mean()) if len(bad) else np.nan,
            "xs_dispersion_bps": float(bad["xs_dispersion_bps"].mean()) if len(bad) else np.nan,
            "realized_vol_bps": float(bad["realized_vol_bps"].mean()) if len(bad) else np.nan,
            "ls_divergence_bps": float(bad["ls_divergence_bps"].mean()) if len(bad) else np.nan,
            "veto_active_rate": float(bad["veto_active_rate"].mean()) if len(bad) else np.nan,
            "veto_monthly_net_mean_pct": float(bad["veto_monthly_net"].mean() * 100.0) if len(bad) else np.nan,
        },
        "reading": "负收益月最稳定特征是：横截面分散度低、veto 触发率低、long-short leg 分化弱；BTC 短窗趋势方向本身区分力次于这些横截面变量。",
    }

    q2 = {
        "period": "2025/2026 且月度 veto 为正",
        "months": int(len(good)),
        "environment": {
            "btc_trend_64_bps": float(good["btc_trend_64_bps"].mean()) if len(good) else np.nan,
            "xs_dispersion_bps": float(good["xs_dispersion_bps"].mean()) if len(good) else np.nan,
            "realized_vol_bps": float(good["realized_vol_bps"].mean()) if len(good) else np.nan,
            "ls_divergence_bps": float(good["ls_divergence_bps"].mean()) if len(good) else np.nan,
            "veto_active_rate": float(good["veto_active_rate"].mean()) if len(good) else np.nan,
            "veto_monthly_net_mean_pct": float(good["veto_monthly_net"].mean() * 100.0) if len(good) else np.nan,
            "veto_funding_mean_bps": float(good["veto_funding_mean_bps"].mean()) if "veto_funding_mean_bps" in good.columns else np.nan,
        },
        "reading": "正收益月最稳定特征是：横截面分散度高、veto 触发率高、long/short leg 分化更明显；在 funding 可得区间内，资金费率对 veto 不是主拖累。",
    }

    q3 = {
        "top_separators": sep[["variable", "good_mean", "bad_mean", "good_minus_bad", "effect_size_d", "direction"]].head(6).to_dict("records"),
        "reading": "区分度按效应量排序；优先看 veto 触发率、横截面分散度与 leg 分化，再看趋势/波动；funding 仅在 2025-10 之后有直接证据。",
    }

    q4 = {
        "current_env": cur_env,
        "distance_to_good": dist_good,
        "distance_to_bad": dist_bad,
        "live_like": live_like,
        "reading": "用最近30天特征与历史正/负阶段中心做标准化距离比较。",
    }

    gate_text_parts = []
    for g in gate_rules:
        op = ">=" if g["higher_is_good"] else "<="
        gate_text_parts.append(f"{g['variable']} {op} {g['threshold']:.4f}")
    q5 = {
        "gate_definition": " and ".join(gate_text_parts) + " (至少满足2/3条件为ON)",
        "gate_stats": gate_stats,
        "current_gate": {
            "window_start_utc": cur_env["start_utc"],
            "window_end_utc": cur_env["end_utc"],
            "votes": int(current_gate_votes),
            "valid_rules": int(current_gate_valid),
            "needed_votes": int(current_gate_needed),
            "gate_on": bool(current_gate_on),
            "checks": current_gate_checks,
        },
        "reading": "这是解释性 regime gate，不改策略参数、不重跑优化，只用于 live 风险开关提示。",
    }

    review = {
        "scope": "regime attribution only; no strategy change / no parameter retune",
        "sources": {
            "asof_long_history_detail": str(ASOF_DETAIL_PATH.relative_to(ROOT)),
            "asof_long_history_summary": str(ASOF_SUMMARY_PATH.relative_to(ROOT)),
            "funding_review_detail": str(FUNDING_DETAIL_PATH.relative_to(ROOT)) if FUNDING_DETAIL_PATH.exists() else None,
            "funding_review_summary": str(FUNDING_SUMMARY_PATH.relative_to(ROOT)) if FUNDING_SUMMARY_PATH.exists() else None,
            "performance_review_summary": str(PERF_SUMMARY_PATH.relative_to(ROOT)) if PERF_SUMMARY_PATH.exists() else None,
        },
        "q1_2023_2024_negative_env": q1,
        "q2_2025_2026_positive_env": q2,
        "q3_best_separators": q3,
        "q4_live_like": q4,
        "q5_simple_gate": q5,
        "supporting": {
            "performance_review_delta_net_mean_bps": perf.get("delta_veto_minus_plain", {}).get("net_mean_bps") if perf else None,
            "performance_review_delta_net_cum_pct": perf.get("delta_veto_minus_plain", {}).get("net_cum_pct") if perf else None,
            "funding_full_delta_net_mean_bps": funding_summary.get("full_available_history", {}).get("delta", {}).get("net_mean_bps") if funding_summary else None,
            "funding_full_delta_net_cum_pct": funding_summary.get("full_available_history", {}).get("delta", {}).get("net_cum_pct") if funding_summary else None,
            "asof_full_delta_net_mean_bps": asof_summary.get("full_available_history", {}).get("delta", {}).get("net_mean_bps") if asof_summary else None,
            "asof_full_delta_net_cum_pct": asof_summary.get("full_available_history", {}).get("delta", {}).get("net_cum_pct") if asof_summary else None,
        },
    }

    OUT_SUMMARY_PATH.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    sep_table = render_table(
        sep[["variable", "good_mean", "bad_mean", "good_minus_bad", "effect_size_d", "direction"]].head(8),
        bps_cols={"good_mean", "bad_mean", "good_minus_bad"},
    )

    monthly_view = monthly[[
        "month", "year", "rebalances", "veto_monthly_net", "plain_monthly_net", "delta_net_mean_bps",
        "btc_trend_64_bps", "xs_dispersion_bps", "realized_vol_bps", "ls_divergence_bps", "veto_active_rate", "gate_on"
    ]].tail(18)

    monthly_table = render_table(
        monthly_view,
        percent_cols={"veto_monthly_net", "plain_monthly_net", "veto_active_rate"},
        bps_cols={"delta_net_mean_bps", "btc_trend_64_bps", "xs_dispersion_bps", "realized_vol_bps", "ls_divergence_bps"},
    )

    html = f"""<!doctype html>
<html lang='zh-CN'>
<head>
<meta charset='utf-8' />
<meta name='viewport' content='width=device-width, initial-scale=1' />
<title>Rank213 regime review</title>
<style>
:root{{--bg:#f8fafc;--card:#fff;--fg:#0f172a;--muted:#64748b;--line:#e2e8f0;--warn:#9a3412;--warnbg:#ffedd5;--ok:#166534;--okbg:#dcfce7;--info:#1d4ed8;--infobg:#dbeafe}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.65 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}}
.wrap{{max-width:1160px;margin:0 auto;padding:28px 18px 64px}} .card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin-bottom:14px}}
h1,h2,h3{{margin:0 0 12px}} .muted{{color:var(--muted)}}
.note{{border-left:4px solid var(--info);background:var(--infobg);padding:12px 14px;border-radius:10px;white-space:pre-wrap}} .warn{{border-left-color:var(--warn);background:var(--warnbg)}} .ok{{border-left-color:var(--ok);background:var(--okbg)}}
table{{width:100%;border-collapse:collapse}} th,td{{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}} th{{background:#f8fafc}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}} .metric{{border:1px solid var(--line);border-radius:12px;padding:10px 12px}}
code{{background:#eff6ff;border-radius:6px;padding:2px 6px}} a{{color:#0f766e;text-decoration:none}} a:hover{{text-decoration:underline}}
</style>
</head>
<body><div class='wrap'>
<div class='card'>
<h1>Rank213 regime review（解释“什么时候有效”）</h1>
<p><strong>边界：</strong>不新增策略、不重调参数；只用既有 as-of long-history / funding review / performance review 做归因。</p>
<p><a href='/momentum/paper/rank213_largecap_xs_jump_veto_asof_universe_long_history_review.html'>as-of long-history</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_long_history_review_with_funding.html'>funding review</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_performance_review.html'>performance review</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_formal_strategy_review.html'>formal strategy review</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_family_operating_board.html'>family operating board</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto.html'>runner</a></p>
</div>

<div class='card'>
<h2>1) 2023/2024 负收益主要发生在什么环境</h2>
<div class='note warn'><b>{q1['reading']}</b></div>
<div class='grid'>
<div class='metric'><b>bad months</b><br/>{q1['months']}</div>
<div class='metric'><b>veto monthly net mean</b><br/>{fmt_pct(q1['environment']['veto_monthly_net_mean_pct'])}</div>
<div class='metric'><b>btc trend(64) mean</b><br/>{fmt_bps(q1['environment']['btc_trend_64_bps'])}</div>
<div class='metric'><b>xs dispersion mean</b><br/>{fmt_bps(q1['environment']['xs_dispersion_bps'])}</div>
<div class='metric'><b>realized vol mean</b><br/>{fmt_bps(q1['environment']['realized_vol_bps'])}</div>
<div class='metric'><b>ls divergence mean</b><br/>{fmt_bps(q1['environment']['ls_divergence_bps'])}</div>
</div>
</div>

<div class='card'>
<h2>2) 2025/2026 正收益主要发生在什么环境</h2>
<div class='note ok'><b>{q2['reading']}</b></div>
<div class='grid'>
<div class='metric'><b>good months</b><br/>{q2['months']}</div>
<div class='metric'><b>veto monthly net mean</b><br/>{fmt_pct(q2['environment']['veto_monthly_net_mean_pct'])}</div>
<div class='metric'><b>btc trend(64) mean</b><br/>{fmt_bps(q2['environment']['btc_trend_64_bps'])}</div>
<div class='metric'><b>xs dispersion mean</b><br/>{fmt_bps(q2['environment']['xs_dispersion_bps'])}</div>
<div class='metric'><b>realized vol mean</b><br/>{fmt_bps(q2['environment']['realized_vol_bps'])}</div>
<div class='metric'><b>ls divergence mean</b><br/>{fmt_bps(q2['environment']['ls_divergence_bps'])}</div>
</div>
</div>

<div class='card'>
<h2>3) 哪些变量最能区分好坏阶段</h2>
<p class='muted'>{q3['reading']}</p>
{sep_table}
</div>

<div class='card'>
<h2>4) 当前 live 环境更像哪一段</h2>
<div class='note {'ok' if '2025/2026' in q4['live_like'] else 'warn'}'><b>{q4['live_like']}</b></div>
<div class='grid'>
<div class='metric'><b>current window</b><br/>{q4['current_env']['start_utc']} → {q4['current_env']['end_utc']}</div>
<div class='metric'><b>distance to good</b><br/>{q4['distance_to_good']:.4f}</div>
<div class='metric'><b>distance to bad</b><br/>{q4['distance_to_bad']:.4f}</div>
<div class='metric'><b>current veto mean</b><br/>{fmt_bps(q4['current_env']['veto_net_mean_bps'])}</div>
<div class='metric'><b>current delta mean</b><br/>{fmt_bps(q4['current_env']['delta_net_mean_bps'])}</div>
</div>
</div>

<div class='card'>
<h2>5) 是否能提炼一个简单 on/off gate</h2>
<div class='note'><b>{q5['gate_definition']}</b></div>
<p class='muted'>{q5['reading']}</p>
<div class='note {'ok' if q5['current_gate']['gate_on'] else 'warn'}'><b>当前窗口 gate 状态：{'ON' if q5['current_gate']['gate_on'] else 'OFF'}（{q5['current_gate']['votes']}/{q5['current_gate']['valid_rules']}，阈值 {q5['current_gate']['needed_votes']}）</b></div>
<div class='grid'>
<div class='metric'><b>ON months</b><br/>{q5['gate_stats']['on_months']}</div>
<div class='metric'><b>OFF months</b><br/>{q5['gate_stats']['off_months']}</div>
<div class='metric'><b>ON monthly mean</b><br/>{fmt_pct(q5['gate_stats']['on_veto_monthly_mean_pct'])}</div>
<div class='metric'><b>OFF monthly mean</b><br/>{fmt_pct(q5['gate_stats']['off_veto_monthly_mean_pct'])}</div>
<div class='metric'><b>ON monthly win rate</b><br/>{fmt_pct(q5['gate_stats']['on_veto_monthly_win_rate'])}</div>
<div class='metric'><b>OFF monthly win rate</b><br/>{fmt_pct(q5['gate_stats']['off_veto_monthly_win_rate'])}</div>
</div>
</div>

<div class='card'>
<h2>附：最近18个月月度特征与 gate 状态</h2>
{monthly_table}
</div>
</div></body></html>
"""

    SITE_PATH.write_text(html, encoding="utf-8")

    print(json.dumps({
        "summary_json": str(OUT_SUMMARY_PATH.relative_to(ROOT)),
        "html": str(SITE_PATH.relative_to(ROOT)),
        "bad_months": int(len(bad)),
        "good_months": int(len(good)),
        "live_like": live_like,
    }, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
