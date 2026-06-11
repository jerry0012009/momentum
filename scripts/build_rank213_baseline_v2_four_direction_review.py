#!/usr/bin/env python3
from __future__ import annotations

import json
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank213_largecap_xs_jump_veto"
FUNDING_DIR = ART_DIR / "rank213_local_cache" / "funding_8h"
SITE_PATH = ROOT / "reports" / "site" / "paper" / "rank213_baseline_v2_four_direction_review.html"
SUMMARY_PATH = ART_DIR / "rank213_baseline_v2_four_direction_review_summary.json"
OVERALL_PATH = ART_DIR / "rank213_baseline_v2_four_direction_review_overall.csv"
ANNUAL_PATH = ART_DIR / "rank213_baseline_v2_four_direction_review_annual.csv"
MONTHLY_PATH = ART_DIR / "rank213_baseline_v2_four_direction_review_monthly.csv"
MONTHLY_SUMMARY_PATH = ART_DIR / "rank213_baseline_v2_four_direction_review_monthly_summary.csv"
FUNDING_DETAIL_PATH = ART_DIR / "rank213_baseline_v2_four_direction_review_funding_overlay_detail.csv"

BASELINE_OVERALL_PATH = ART_DIR / "rank213_monthly_volume_baseline_refresh_overall.csv"
BASELINE_ANNUAL_PATH = ART_DIR / "rank213_monthly_volume_baseline_refresh_annual.csv"
BASELINE_DAILY_PATH = ART_DIR / "rank213_monthly_volume_baseline_refresh_daily.csv"
REBUILD_SUMMARY_PATH = ART_DIR / "rank213_monthly_volume_universe_rebuild_summary.json"

FUNDING_BASE_STRATEGY = "age90_14d_skip1d_voladj"
FUNDING_KEY = "perp_funding_overlay_on_age90_14d_skip1d_voladj"


DIRECTION_SPECS = [
    {
        "direction": "1) 更稳的动量",
        "strategy": "age90_14d_skip1d_voladj",
        "why": "年龄过滤 + 14d skip-1d 动量 + 波动率调整；避免刚上市币、最后一天冲顶和高波动误判。",
        "status": "full_daily_backtest",
    },
    {
        "direction": "2) 去掉 BTC 噪音",
        "strategy": "age90_resid_14d_skip1d_voladj",
        "why": "先扣 BTC/市场方向，再按残差动量排序；目标是找币自己的相对强弱。",
        "status": "full_daily_backtest",
    },
    {
        "direction": "3) 防追顶",
        "strategy": "age90_resid_14d_skip1d_voladj_blowoffpen",
        "why": "在残差动量上惩罚最近一天暴拉；目标是少追 blowoff 后的回落。",
        "status": "full_daily_backtest",
    },
    {
        "direction": "4) 加入 perp 信息",
        "strategy": FUNDING_KEY,
        "why": "在第 1 条价格信号上叠加实际 funding cashflow；本轮只有 funding-only，尚未加入 basis/OI。",
        "status": "limited_funding_only_overlay",
    },
]

QUALITY_NOTES = {
    "age90_14d_skip1d_voladj": {
        "plain_name": "更稳的动量",
        "principle": "先剔除上市不满 90 天的币，再看过去 14 天、但跳过最近 1 天的收益；最后用 14 天波动率缩放。它的核心是：只追已经证明有持续性的中短周期强势，不追刚上市和最后一天暴拉。",
        "formula": "score = return(t-15d -> t-1d) / realized_vol(t-15d -> t-1d)",
        "lookahead": "低。选池来自每月开始前的上一完整月 quote_volume；打分只用 t 日以前的数据；收益用 t -> t+1d。主要风险不是未来函数，而是 daily close 执行假设偏理想。",
        "quality": "当前三条里质量最好。全样本强，但最大回撤仍到 -60.08%，说明它只是值得二轮研究，不是可直接上线。",
        "next_check": "做 walk-forward freeze、成本敏感性、top/bottom leg 归因、月度换池后是否集中在少数年份。"
    },
    "age90_resid_14d_skip1d_voladj": {
        "plain_name": "去掉 BTC 噪音",
        "principle": "在第一条基础上，先扣掉 BTC 同期 14 天收益，再看币自己的相对强弱。它想回答：这个币是真的独立强，还是只是跟着 BTC 涨。",
        "formula": "score = (coin_return_14d_ex1d - BTC_return_14d_ex1d) / realized_vol",
        "lookahead": "低。BTC return 和币本身 return 都只用 t 日以前数据。注意当前 beta=1 是简化近似，不是滚动回归 beta。",
        "quality": "有价值但不如第一条。收益更低、回撤更深一点，说明简单扣 BTC 不一定改善 crypto 横截面；但它是重要稳健性对照。",
        "next_check": "把 beta=1 改成 rolling beta；区分 BTC 上涨/下跌 regime；检查它是否减少市场方向暴露。"
    },
    "age90_resid_14d_skip1d_voladj_blowoffpen": {
        "plain_name": "防追顶",
        "principle": "在残差动量上，对最近 1 天暴涨的币扣分。它的目标是避免买到最后一冲、或卖到最后一砸之后马上反弹。",
        "formula": "score = residual_voladj_score - 0.5 * zscore(return(t-1d -> t))",
        "lookahead": "中低。最近 1 天收益在 t 日收盘后才完全可见；如果假设 t 日收盘调仓，不能偷用同一根收盘价之后无法成交的价格。当前 daily 快筛需要后续做 next-open 或执行滑点复核。",
        "quality": "当前结果不理想。全样本仍正，但回撤反而更深到 -74.56%，说明这个 penalty 参数或方向没有解决坏尾部，不能作为优先主线。",
        "next_check": "扫 penalty 强度；改成只 veto 极端 blowoff 而不是线性扣分；看它是否只在 2024/2026 有用。"
    },
}


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def fmt_pct(x: object, digits: int = 2) -> str:
    try:
        if pd.isna(x):
            return ""
        return f"{float(x):.{digits}f}%"
    except (TypeError, ValueError):
        return ""


def fmt_bps(x: object, digits: int = 2) -> str:
    try:
        if pd.isna(x):
            return ""
        return f"{float(x):.{digits}f} bps"
    except (TypeError, ValueError):
        return ""


def max_drawdown(ret: pd.Series) -> float:
    if ret.empty:
        return np.nan
    eq = (1.0 + pd.to_numeric(ret, errors="coerce").fillna(0.0)).cumprod()
    dd = eq / eq.cummax() - 1.0
    return float(dd.min())


def calc_stats(df: pd.DataFrame, ret_col: str = "net_ret") -> dict:
    ret = pd.to_numeric(df[ret_col], errors="coerce").fillna(0.0)
    active = pd.to_numeric(df.get("active", 1), errors="coerce").fillna(0).astype(bool)
    return {
        "days": int(len(df)),
        "active_days": int(active.sum()),
        "active_rate_pct": float(active.mean() * 100.0) if len(df) else np.nan,
        "net_mean_bps": float(ret.mean() * 10000.0) if len(df) else np.nan,
        "net_cum_pct": float(((1.0 + ret).prod() - 1.0) * 100.0) if len(df) else np.nan,
        "max_drawdown_pct": float(max_drawdown(ret) * 100.0) if len(df) else np.nan,
        "win_rate_pct": float((ret > 0).mean() * 100.0) if len(df) else np.nan,
    }


def compound_return(ret: pd.Series) -> float:
    ret = pd.to_numeric(ret, errors="coerce").fillna(0.0)
    return float((1.0 + ret).prod() - 1.0) if len(ret) else np.nan


def selected_price_daily() -> pd.DataFrame:
    daily = pd.read_csv(BASELINE_DAILY_PATH)
    keep = [x["strategy"] for x in DIRECTION_SPECS[:3]]
    daily = daily[daily["strategy"].isin(keep)].copy()
    daily["timestamp_ts"] = pd.to_datetime(daily["timestamp_ts"], utc=True, errors="coerce", format="mixed")
    daily["exit_ts"] = pd.to_datetime(daily["exit_ts"], utc=True, errors="coerce", format="mixed")
    daily["net_ret"] = pd.to_numeric(daily["net_ret"], errors="coerce").fillna(0.0)
    daily["active"] = daily["active"].astype(str).str.lower().isin(["true", "1", "yes"])
    return daily.dropna(subset=["timestamp_ts"]).sort_values(["strategy", "timestamp_ts"])


def build_monthly_stats(daily: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict] = []
    for (strategy, month), sub in daily.groupby(["strategy", "month"]):
        spec = next((x for x in DIRECTION_SPECS if x["strategy"] == strategy), {})
        stats = calc_stats(sub)
        rows.append({
            "month": str(month),
            "direction": spec.get("direction", ""),
            "strategy": strategy,
            "trading_baskets": stats["active_days"],
            "calendar_days": stats["days"],
            "net_mean_bps": stats["net_mean_bps"],
            "net_cum_pct": stats["net_cum_pct"],
            "max_drawdown_pct": stats["max_drawdown_pct"],
            "win_rate_pct": stats["win_rate_pct"],
        })
    monthly = pd.DataFrame(rows).sort_values(["month", "strategy"]).reset_index(drop=True)

    summary_rows: list[dict] = []
    for strategy, sub in monthly.groupby("strategy"):
        spec = next((x for x in DIRECTION_SPECS if x["strategy"] == strategy), {})
        ret = pd.to_numeric(sub["net_cum_pct"], errors="coerce")
        summary_rows.append({
            "direction": spec.get("direction", ""),
            "strategy": strategy,
            "months": int(len(sub)),
            "positive_months": int((ret > 0).sum()),
            "positive_month_rate_pct": float((ret > 0).mean() * 100.0) if len(sub) else np.nan,
            "avg_monthly_net_pct": float(ret.mean()) if len(sub) else np.nan,
            "median_monthly_net_pct": float(ret.median()) if len(sub) else np.nan,
            "best_month": str(sub.loc[ret.idxmax(), "month"]) if len(sub) and ret.notna().any() else "",
            "best_month_net_pct": float(ret.max()) if len(sub) else np.nan,
            "worst_month": str(sub.loc[ret.idxmin(), "month"]) if len(sub) and ret.notna().any() else "",
            "worst_month_net_pct": float(ret.min()) if len(sub) else np.nan,
        })
    monthly_summary = pd.DataFrame(summary_rows).sort_values("avg_monthly_net_pct", ascending=False).reset_index(drop=True)
    return monthly, monthly_summary


def build_equity_frame(daily: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for strategy, sub in daily.groupby("strategy"):
        spec = next((x for x in DIRECTION_SPECS if x["strategy"] == strategy), {})
        work = sub.sort_values("timestamp_ts").copy()
        work["equity"] = (1.0 + pd.to_numeric(work["net_ret"], errors="coerce").fillna(0.0)).cumprod()
        for _, row in work.iterrows():
            rows.append({
                "timestamp_ts": row["timestamp_ts"],
                "strategy": strategy,
                "direction": spec.get("direction", ""),
                "equity": float(row["equity"]),
                "net_ret": float(row["net_ret"]),
            })
    return pd.DataFrame(rows).sort_values(["timestamp_ts", "strategy"]).reset_index(drop=True)


def load_funding(symbol: str) -> pd.Series | None:
    path = FUNDING_DIR / f"{symbol}.csv"
    if not path.exists():
        return None
    df = pd.read_csv(path)
    if df.empty or "timestamp" not in df.columns or "funding_rate" not in df.columns:
        return None
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce", format="mixed")
    df["funding_rate"] = pd.to_numeric(df["funding_rate"], errors="coerce")
    df = df.dropna(subset=["timestamp", "funding_rate"]).drop_duplicates("timestamp").sort_values("timestamp")
    if df.empty:
        return None
    return df.set_index("timestamp")["funding_rate"]


def funding_sum(cache: dict[str, pd.Series], symbol: str, start: pd.Timestamp, end: pd.Timestamp) -> float | None:
    ser = cache.get(symbol)
    if ser is None:
        ser = load_funding(symbol)
        if ser is None:
            cache[symbol] = pd.Series(dtype=float)
            return None
        cache[symbol] = ser
    if ser.empty:
        return None
    window = ser[(ser.index > start) & (ser.index <= end)]
    if window.empty:
        return None
    return float(window.sum())


def build_funding_overlay() -> tuple[pd.DataFrame, dict]:
    daily = pd.read_csv(BASELINE_DAILY_PATH)
    daily = daily[daily["strategy"] == FUNDING_BASE_STRATEGY].copy()
    daily["timestamp_ts"] = pd.to_datetime(daily["timestamp_ts"], utc=True)
    daily["exit_ts"] = pd.to_datetime(daily["exit_ts"], utc=True)
    cache: dict[str, pd.Series] = {}
    rows: list[dict] = []
    missing_rows = 0

    for _, row in daily.iterrows():
        longs = [x for x in str(row.get("longs", "")).split(",") if x]
        shorts = [x for x in str(row.get("shorts", "")).split(",") if x]
        if not longs or not shorts:
            continue
        start = row["timestamp_ts"]
        end = row["exit_ts"]
        long_fr_raw = [funding_sum(cache, sym, start, end) for sym in longs]
        short_fr_raw = [funding_sum(cache, sym, start, end) for sym in shorts]
        long_fr = [x for x in long_fr_raw if x is not None]
        short_fr = [x for x in short_fr_raw if x is not None]
        if not long_fr or not short_fr:
            missing_rows += 1
            continue
        funding_ret = 0.5 * float(np.mean([-x for x in long_fr])) + 0.5 * float(np.mean(short_fr))
        base_net = float(row["net_ret"])
        rows.append({
            "timestamp_ts": start,
            "exit_ts": end,
            "month": row["month"],
            "strategy": FUNDING_KEY,
            "label": "4) perp funding overlay on best price baseline",
            "longs": ",".join(longs),
            "shorts": ",".join(shorts),
            "base_net_ret": base_net,
            "funding_ret": funding_ret,
            "net_ret": base_net + funding_ret,
            "long_funding_covered_legs": len(long_fr),
            "short_funding_covered_legs": len(short_fr),
            "funding_covered_legs": len(long_fr) + len(short_fr),
            "funding_leg_coverage_pct": (len(long_fr) + len(short_fr)) / (len(longs) + len(shorts)) * 100.0,
            "active": True,
        })

    detail = pd.DataFrame(rows)
    meta = {
        "base_strategy": FUNDING_BASE_STRATEGY,
        "funding_cache_dir": str(FUNDING_DIR.relative_to(ROOT)),
        "available_symbols": sorted(p.stem for p in FUNDING_DIR.glob("*.csv")),
        "input_days": int(len(daily)),
        "covered_days": int(len(detail)),
        "missing_days": int(missing_rows),
        "coverage_pct": float(len(detail) / len(daily) * 100.0) if len(daily) else np.nan,
        "avg_funding_leg_coverage_pct": float(detail["funding_leg_coverage_pct"].mean()) if not detail.empty else np.nan,
        "limitation": "funding-only partial-leg overlay using local cached Binance funding files; rows require at least one funded long leg and one funded short leg, but not all six legs. No basis/OI history is included, and coverage is mostly frozen30-era symbols after 2025-10.",
    }
    return detail, meta


def table_html(df: pd.DataFrame, cols: list[str]) -> str:
    headers = "".join(f"<th>{escape(c)}</th>" for c in cols)
    body = []
    for _, row in df.iterrows():
        cells = []
        for c in cols:
            val = row.get(c, "")
            if c.endswith("_pct"):
                txt = fmt_pct(val)
            elif c.endswith("_bps"):
                txt = fmt_bps(val)
            elif isinstance(val, float):
                txt = f"{val:.4f}"
            else:
                txt = escape(str(val))
            cells.append(f"<td>{txt}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def equity_svg(equity: pd.DataFrame) -> str:
    if equity.empty:
        return "<p class='muted'>暂无权益曲线数据。</p>"
    colors = {
        "age90_14d_skip1d_voladj": "#2563eb",
        "age90_resid_14d_skip1d_voladj": "#16a34a",
        "age90_resid_14d_skip1d_voladj_blowoffpen": "#dc2626",
    }
    width, height = 1120, 420
    left, right, top, bottom = 70, 25, 30, 60
    plot_w = width - left - right
    plot_h = height - top - bottom
    ts_min = equity["timestamp_ts"].min()
    ts_max = equity["timestamp_ts"].max()
    x_span = max((ts_max - ts_min).total_seconds(), 1.0)
    y_vals = np.log(pd.to_numeric(equity["equity"], errors="coerce").clip(lower=1e-6))
    y_min = float(y_vals.min())
    y_max = float(y_vals.max())
    if y_max <= y_min:
        y_max = y_min + 1.0

    def xy(ts: pd.Timestamp, eq: float) -> tuple[float, float]:
        x = left + ((ts - ts_min).total_seconds() / x_span) * plot_w
        y = top + (1.0 - ((np.log(max(eq, 1e-6)) - y_min) / (y_max - y_min))) * plot_h
        return x, y

    paths: list[str] = []
    legends: list[str] = []
    for idx, (strategy, sub) in enumerate(equity.groupby("strategy")):
        pts = [xy(row["timestamp_ts"], float(row["equity"])) for _, row in sub.sort_values("timestamp_ts").iterrows()]
        if not pts:
            continue
        d = " ".join(("M" if i == 0 else "L") + f"{x:.2f},{y:.2f}" for i, (x, y) in enumerate(pts))
        color = colors.get(strategy, "#334155")
        paths.append(f"<path d='{d}' fill='none' stroke='{color}' stroke-width='2.4'/>")
        legends.append(f"<g transform='translate({left + idx * 330}, {height - 24})'><rect width='14' height='14' rx='3' fill='{color}'/><text x='22' y='12'>{escape(strategy)}</text></g>")

    y_labels = []
    for eq_level in [0.25, 0.5, 1.0, 2.0, 5.0]:
        ly = top + (1.0 - ((np.log(eq_level) - y_min) / (y_max - y_min))) * plot_h
        if top <= ly <= top + plot_h:
            y_labels.append(
                f"<line x1='{left}' y1='{ly:.1f}' x2='{width-right}' y2='{ly:.1f}' stroke='#e2e8f0'/>"
                f"<text x='{left-10}' y='{ly+4:.1f}' text-anchor='end'>{eq_level:.2f}x</text>"
            )
    year_labels = []
    for year in range(ts_min.year, ts_max.year + 1):
        ts = pd.Timestamp(f"{year}-01-01T00:00:00Z")
        if ts_min <= ts <= ts_max:
            x = left + ((ts - ts_min).total_seconds() / x_span) * plot_w
            year_labels.append(f"<line x1='{x:.1f}' y1='{top}' x2='{x:.1f}' y2='{top+plot_h}' stroke='#f1f5f9'/><text x='{x:.1f}' y='{height-42}' text-anchor='middle'>{year}</text>")

    return f"""
<svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="Baseline V2 equity curves">
  <rect x="0" y="0" width="{width}" height="{height}" rx="18" fill="#ffffff"/>
  <g font-family="Noto Sans SC, Microsoft YaHei, sans-serif" font-size="13" fill="#475569">
    {''.join(y_labels)}
    {''.join(year_labels)}
    <line x1="{left}" y1="{top+plot_h}" x2="{width-right}" y2="{top+plot_h}" stroke="#cbd5e1"/>
    <line x1="{left}" y1="{top}" x2="{left}" y2="{top+plot_h}" stroke="#cbd5e1"/>
    {''.join(paths)}
    {''.join(legends)}
    <text x="{left}" y="20" font-size="15" font-weight="700" fill="#172033">权益曲线（log scale，初始=1.0）</text>
  </g>
</svg>
"""


def monthly_summary_cards(monthly_summary: pd.DataFrame) -> str:
    cards: list[str] = []
    for _, row in monthly_summary.iterrows():
        cards.append(f"""
      <div class="metric">
        <b>{fmt_pct(row.get('positive_month_rate_pct'))}</b>
        <span>{escape(str(row.get('direction', '')))} 正收益月占比</span>
        <small>均值 {fmt_pct(row.get('avg_monthly_net_pct'))} · 最差 {escape(str(row.get('worst_month', '')))} {fmt_pct(row.get('worst_month_net_pct'))}</small>
      </div>
""")
    return "".join(cards)


def monthly_table_html(monthly: pd.DataFrame) -> str:
    if monthly.empty:
        return "<p class='muted'>暂无月度数据。</p>"
    strategies = [x["strategy"] for x in DIRECTION_SPECS[:3]]
    labels = {x["strategy"]: x["direction"] for x in DIRECTION_SPECS[:3]}
    by_month = {m: g.set_index("strategy") for m, g in monthly.groupby("month")}
    headers = "<th>month</th>" + "".join(
        f"<th>{escape(labels[s])}<br/>收益 / 交易天数 / 胜率</th>" for s in strategies
    )
    rows: list[str] = []
    for month in sorted(by_month.keys()):
        cells = [f"<td>{escape(str(month))}</td>"]
        g = by_month[month]
        for strategy in strategies:
            if strategy not in g.index:
                cells.append("<td></td>")
                continue
            r = g.loc[strategy]
            ret = float(r["net_cum_pct"])
            cls = "pos" if ret > 0 else "neg" if ret < 0 else "flat"
            cells.append(
                f"<td class='{cls}'><b>{fmt_pct(ret)}</b><br/>"
                f"{int(r['trading_baskets'])} baskets · win {fmt_pct(r['win_rate_pct'])}<br/>"
                f"DD {fmt_pct(r['max_drawdown_pct'])}</td>"
            )
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return f"<table class='monthly'><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def strategy_explain_cards(overall: pd.DataFrame) -> str:
    cards: list[str] = []
    for spec in DIRECTION_SPECS[:3]:
        row = overall[overall["strategy"] == spec["strategy"]]
        note = QUALITY_NOTES[spec["strategy"]]
        metric = row.iloc[0].to_dict() if not row.empty else {}
        cards.append(f"""
  <section class="strategy-card">
    <div class="badge">{escape(note['plain_name'])}</div>
    <h3>{escape(spec['strategy'])}</h3>
    <p>{escape(note['principle'])}</p>
    <div class="formula"><code>{escape(note['formula'])}</code></div>
    <div class="mini-flow">
      <div>月初用上月成交额选池</div><span>→</span>
      <div>上市满 90 天过滤</div><span>→</span>
      <div>只用历史窗口打分</div><span>→</span>
      <div>次日收益记账</div>
    </div>
    <div class="metric-row">
      <span>累计 <b>{fmt_pct(metric.get('net_cum_pct'))}</b></span>
      <span>回撤 <b>{fmt_pct(metric.get('max_drawdown_pct'))}</b></span>
      <span>均值 <b>{fmt_bps(metric.get('net_mean_bps'))}</b></span>
    </div>
    <p><b>未来函数评价：</b>{escape(note['lookahead'])}</p>
    <p><b>回测质量评价：</b>{escape(note['quality'])}</p>
    <p class="muted"><b>下一步验证：</b>{escape(note['next_check'])}</p>
  </section>
""")
    return "".join(cards)


def svg_explainer() -> str:
    return """
<svg class="diagram" viewBox="0 0 1120 300" role="img" aria-label="baseline v2 causal backtest flow">
  <defs>
    <linearGradient id="g1" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0%" stop-color="#fff7ed"/>
      <stop offset="100%" stop-color="#e0f2fe"/>
    </linearGradient>
  </defs>
  <rect x="10" y="10" width="1100" height="280" rx="24" fill="url(#g1)" stroke="#fed7aa"/>
  <g font-family="Noto Sans SC, Microsoft YaHei, sans-serif" font-size="18" fill="#172033">
    <rect x="60" y="70" width="210" height="88" rx="18" fill="#ffffff" stroke="#cbd5e1"/>
    <text x="85" y="105" font-weight="700">1. Causal universe</text>
    <text x="85" y="135" font-size="14">每月只用上月 quote_volume</text>
    <text x="85" y="155" font-size="14">选当月 Top30</text>
    <text x="300" y="122" font-size="30">→</text>
    <rect x="340" y="70" width="210" height="88" rx="18" fill="#ffffff" stroke="#cbd5e1"/>
    <text x="365" y="105" font-weight="700">2. Historical score</text>
    <text x="365" y="135" font-size="14">只看 t 日以前窗口</text>
    <text x="365" y="155" font-size="14">14d / skip1d / voladj</text>
    <text x="580" y="122" font-size="30">→</text>
    <rect x="620" y="70" width="210" height="88" rx="18" fill="#ffffff" stroke="#cbd5e1"/>
    <text x="645" y="105" font-weight="700">3. Cross-section rank</text>
    <text x="645" y="135" font-size="14">多 strongest 3</text>
    <text x="645" y="155" font-size="14">空 weakest 3</text>
    <text x="860" y="122" font-size="30">→</text>
    <rect x="900" y="70" width="170" height="88" rx="18" fill="#ffffff" stroke="#cbd5e1"/>
    <text x="925" y="105" font-weight="700">4. Next day PnL</text>
    <text x="925" y="135" font-size="14">t → t+1d</text>
    <text x="925" y="155" font-size="14">扣 4bps/side</text>
    <path d="M170 205 C300 245, 820 245, 970 205" fill="none" stroke="#f97316" stroke-width="4"/>
    <text x="330" y="255" font-size="16" fill="#9a3412">关键防线：选池、打分、调仓都不能用 t 之后的数据</text>
  </g>
</svg>
"""


def quality_matrix_html() -> str:
    rows = [
        ("选池未来函数", "低", "每月用上一完整自然月 quote_volume 选当月池子，不用当月/未来表现。"),
        ("打分未来函数", "低", "前两条只用 t 日以前窗口；第三条用最近 1 天，后续要确认执行价不能偷用收盘后价格。"),
        ("幸存者偏差", "中", "monthly-volume universe 比 frozen30 好很多，但仍依赖 Binance UM 历史可交易合约集合，不是官方历史市值快照。"),
        ("交易成本", "中", "已扣 one-way 4bps，但 daily close-to-close 没有真实盘口、滑点、冲击成本。"),
        ("执行一致性", "中高风险", "这是 daily 快筛，不是原 15m Rank213 execution；不能直接迁移到 live。"),
        ("过拟合风险", "中", "候选数量不多，但参数仍需 walk-forward freeze 和样本外验证。"),
    ]
    body = "".join(f"<tr><td>{escape(a)}</td><td><b>{escape(b)}</b></td><td>{escape(c)}</td></tr>" for a, b, c in rows)
    return f"<table><thead><tr><th>检查项</th><th>风险</th><th>说明</th></tr></thead><tbody>{body}</tbody></table>"


def verdict(row: pd.Series) -> str:
    if row.get("strategy") == FUNDING_KEY and int(row.get("days", 0) or 0) == 0:
        return "本地 funding/basis 数据与 2020-2026 daily 样本无有效重叠；本轮不能给出收益结论，必须补全历史 funding/basis/OI 后再测。"
    net = float(row.get("net_cum_pct", np.nan))
    dd = float(row.get("max_drawdown_pct", np.nan))
    if row.get("strategy") == FUNDING_KEY:
        return "样本太窄，只能说明 funding cashflow 对第 1 条不是决定性修复；不能替代完整 basis/funding/OI 回测。"
    if net > 100 and dd > -65:
        return "值得进入第二轮，但回撤仍大，不能直接上线。"
    if net > 0:
        return "有正收益迹象，但稳定性/回撤需要继续筛。"
    return "当前不支持继续推进。"


def build_report(
    overall: pd.DataFrame,
    annual: pd.DataFrame,
    monthly: pd.DataFrame,
    monthly_summary: pd.DataFrame,
    equity: pd.DataFrame,
    funding_meta: dict,
    incumbent: dict,
) -> str:
    overall_view = overall.copy()
    overall_view["human_verdict"] = overall_view.apply(verdict, axis=1)
    cols = [
        "direction", "strategy", "status", "days", "active_rate_pct", "net_mean_bps",
        "net_cum_pct", "max_drawdown_pct", "win_rate_pct", "human_verdict",
    ]
    annual_cols = ["segment", "strategy", "days", "active_days", "net_mean_bps", "net_cum_pct", "max_drawdown_pct", "win_rate_pct"]
    spec_list = "".join(
        f"<li><b>{escape(x['direction'])}</b>：{escape(x['why'])}<br><span class='muted'><code>{escape(x['strategy'])}</code> · {escape(x['status'])}</span></li>"
        for x in DIRECTION_SPECS
    )
    best = overall_view.iloc[0] if not overall_view.empty else {}
    generated = pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%d %H:%M UTC")
    funding_days = int(funding_meta.get("covered_days", 0) or 0)
    if funding_days:
        funding_sentence = "第 4 条有窄样本 funding-only 结果，但仍不能代表完整 perp basis/funding/OI 研究。"
    else:
        funding_sentence = "第 4 条本轮没有有效回测收益：本地 funding 缓存主要在样本截止日之后，和 2020-2026 daily baseline 样本无重叠；需要补历史 funding/basis/OI。"
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Rank213 Baseline V2 四方向初筛</title>
  <style>
    body {{ margin:0; background:#f5f1e8; color:#172033; font-family:"Noto Sans SC","Source Han Sans SC","PingFang SC","Microsoft YaHei",sans-serif; line-height:1.65; }}
    main {{ max-width:1180px; margin:0 auto; padding:28px 16px 52px; }}
    .card {{ background:#fff; border:1px solid #e6dccb; border-radius:16px; padding:18px 20px; margin:14px 0; box-shadow:0 1px 2px rgba(20,24,31,.04); }}
    .hero {{ background:linear-gradient(135deg,#fff7ed,#fff 58%,#e0f2fe); border-color:#fdba74; }}
    .warn {{ background:#fff7ed; border-color:#fdba74; }}
    .muted {{ color:#64748b; }}
    .grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; }}
    .metric {{ background:#f8fafc; border:1px solid #e2e8f0; border-radius:14px; padding:12px; }}
    .metric b {{ display:block; font-size:22px; line-height:1.2; }}
    .metric small {{ display:block; margin-top:6px; color:#64748b; font-size:12px; }}
    .strategy-grid {{ display:grid; grid-template-columns:1fr; gap:14px; }}
    .strategy-card {{ border:1px solid #e2e8f0; border-radius:16px; padding:16px 18px; background:#ffffff; }}
    .badge {{ display:inline-block; background:#0f172a; color:#fff; border-radius:999px; padding:3px 10px; font-size:12px; }}
    .formula {{ background:#f8fafc; border:1px dashed #cbd5e1; border-radius:12px; padding:10px 12px; margin:10px 0; }}
    .mini-flow {{ display:grid; grid-template-columns:1fr auto 1fr auto 1fr auto 1fr; gap:8px; align-items:center; margin:12px 0; }}
    .mini-flow div {{ background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:8px 10px; text-align:center; font-size:13px; }}
    .mini-flow span {{ color:#f97316; font-weight:700; }}
    .metric-row {{ display:flex; flex-wrap:wrap; gap:10px; margin:10px 0; }}
    .metric-row span {{ background:#eef2ff; border:1px solid #c7d2fe; border-radius:999px; padding:4px 10px; }}
    .diagram {{ width:100%; height:auto; margin:8px 0; }}
    .chart {{ width:100%; height:auto; border:1px solid #e2e8f0; border-radius:18px; background:#fff; }}
    .table-wrap {{ overflow-x:auto; }}
    table {{ border-collapse:collapse; min-width:980px; width:100%; }}
    th,td {{ border-bottom:1px solid #e2e8f0; padding:8px 10px; text-align:right; vertical-align:top; font-size:14px; }}
    th {{ background:#f8fafc; color:#475569; }}
    td:first-child,th:first-child,td:nth-child(2),th:nth-child(2),td:last-child,th:last-child {{ text-align:left; }}
    code {{ background:#f1f5f9; border-radius:6px; padding:2px 6px; }}
    .monthly td {{ min-width:190px; }}
    .monthly td:first-child {{ min-width:80px; font-weight:700; }}
    .pos {{ background:#f0fdf4; color:#14532d; }}
    .neg {{ background:#fff7ed; color:#7c2d12; }}
    .flat {{ background:#f8fafc; color:#475569; }}
    a {{ color:#2563eb; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
    @media (max-width:760px) {{ .grid {{ grid-template-columns:1fr; }} .mini-flow {{ grid-template-columns:1fr; }} .mini-flow span {{ display:none; }} }}
  </style>
</head>
<body>
<main>
  <section class="card hero">
    <h1>Rank213 Baseline V2：四方向初筛</h1>
    <p>这页回答一个问题：既然原 Rank213 baseline 在无未来函数选池下太弱，换 baseline 的四个方向初步表现如何？</p>
    <p class="muted">生成时间：{escape(generated)} · 样本主口径：monthly-volume causal universe · 价格候选为 daily rebalance / next-day hold / top3-bottom3 / one-way cost 4bps。</p>
    <p><a href="/momentum/paper/rank213_evidence_map.html">Evidence Map</a> · <a href="/momentum/paper/rank213_age90_14d_phase3_validation.html">age90 Phase 3</a> · <a href="/momentum/paper/rank213_age90_14d_second_round_validation.html">age90_14d 二轮验证</a> · <a href="/momentum/paper/rank213_largecap_xs_jump_veto_monthly_volume_baseline_refresh.html">原 baseline refresh 页</a></p>
  </section>

  <section class="card warn">
    <h2>先说结论</h2>
    <p><b>第 1 条目前最强：</b><code>{escape(str(best.get('strategy', 'n/a')))}</code>，累计 {fmt_pct(best.get('net_cum_pct'))}，最大回撤 {fmt_pct(best.get('max_drawdown_pct'))}。但这仍是研究快筛，不是上线策略。</p>
    <p><b>第 4 条限制最大：</b>{escape(funding_sentence)}</p>
  </section>

  <section class="card">
    <h2>为什么测这四条</h2>
    <ul>{spec_list}</ul>
  </section>

  <section class="card">
    <h2>三条策略的共同回测流程</h2>
    <p>前三条都不是用 4 月 frozen30 回看过去，而是在 <b>monthly-volume causal universe</b> 上做 daily baseline 快筛。核心防线是：当日决策只能看当日以前已经发生的数据。</p>
    {svg_explainer()}
  </section>

  <section class="card">
    <h2>三条策略原理、未来函数评价、回测质量</h2>
    <div class="strategy-grid">{strategy_explain_cards(overall)}</div>
  </section>

  <section class="card warn">
    <h2>回测质量总评</h2>
    <p><b>结论：</b>这组回测比旧 frozen30 更可信，因为选池是 causal 的；但它仍是 daily baseline 研究快筛，不是 execution-grade 策略。最大问题不是未来函数，而是回撤、执行假设、样本外稳定性。</p>
    <div class="table-wrap">{quality_matrix_html()}</div>
  </section>

  <section class="card">
    <h2>旧 baseline 参照</h2>
    <p>无未来函数 monthly-volume 口径下，原 15m plain baseline：mean {fmt_bps(incumbent.get('net_mean_bps'))}，cum {fmt_pct(incumbent.get('net_cum_pct'))}，DD {fmt_pct(incumbent.get('max_drawdown_pct'))}。这就是换 baseline 的原因。</p>
  </section>

  <section class="card">
    <h2>全样本/可用样本结果</h2>
    <div class="table-wrap">{table_html(overall_view, cols)}</div>
  </section>

  <section class="card">
    <h2>收益曲线</h2>
    <p class="muted">这张图展示前三条价格 baseline 的日度复利权益曲线。纵轴用 log scale，避免后期收益较大的线把早期波动压扁。</p>
    {equity_svg(equity)}
  </section>

  <section class="card">
    <h2>逐月稳定性总览</h2>
    <p class="muted">每个月都是独立复利统计；交易次数这里指 daily basket 数，即当天一组 top3/bottom3 组合。</p>
    <div class="grid">{monthly_summary_cards(monthly_summary)}</div>
  </section>

  <section class="card">
    <h2>逐月收益、交易次数、胜率</h2>
    <p class="muted">绿色为当月正收益，橙色为当月负收益。单元格依次展示：当月净收益 / 交易天数 baskets / 胜率 / 当月内最大回撤。</p>
    <div class="table-wrap">{monthly_table_html(monthly)}</div>
  </section>

  <section class="card">
    <h2>Funding Overlay 覆盖说明</h2>
    <div class="grid">
      <div class="metric"><b>{funding_meta.get('covered_days', 0)}</b><span>covered days</span></div>
      <div class="metric"><b>{fmt_pct(funding_meta.get('coverage_pct'))}</b><span>coverage</span></div>
      <div class="metric"><b>{len(funding_meta.get('available_symbols', []))}</b><span>cached funding symbols</span></div>
      <div class="metric"><b>{fmt_pct(funding_meta.get('avg_funding_leg_coverage_pct'))}</b><span>avg leg coverage</span></div>
    </div>
    <p class="muted">basis / OI included: <b>no</b></p>
    <p class="muted">{escape(str(funding_meta.get('limitation', '')))}</p>
    <p class="muted">当前结论：第 4 条不是失败策略，而是数据不足；不能用空样本判断 funding/basis overlay 的好坏。</p>
  </section>

  <section class="card">
    <h2>按年切片</h2>
    <p class="muted">年度表保留用于快速定位年份稳定性。更细的逐月波动请以上面的月度表为准。</p>
    <div class="table-wrap">{table_html(annual, annual_cols)}</div>
  </section>
</main>
</body>
</html>
"""


def main() -> int:
    overall_src = pd.read_csv(BASELINE_OVERALL_PATH)
    annual_src = pd.read_csv(BASELINE_ANNUAL_PATH)
    rebuild_summary = read_json(REBUILD_SUMMARY_PATH)
    incumbent = rebuild_summary.get("metrics", {}).get("monthly_volume_rebuild", {}).get("plain", {})
    price_daily = selected_price_daily()
    monthly, monthly_summary = build_monthly_stats(price_daily)
    equity = build_equity_frame(price_daily)

    funding_detail, funding_meta = build_funding_overlay()
    funding_detail.to_csv(FUNDING_DETAIL_PATH, index=False)

    selected_rows: list[dict] = []
    for spec in DIRECTION_SPECS[:3]:
        row = overall_src[overall_src["strategy"] == spec["strategy"]].iloc[0].to_dict()
        selected_rows.append({**spec, **row})

    if not funding_detail.empty:
        fstats = calc_stats(funding_detail)
        base = {
            "label": "4) perp funding overlay on best price baseline",
            "avg_eligible_universe_size": np.nan,
            **fstats,
        }
        selected_rows.append({**DIRECTION_SPECS[3], **base})
    else:
        selected_rows.append({
            **DIRECTION_SPECS[3],
            "label": "4) perp funding/basis overlay needs historical data",
            "days": 0,
            "active_days": 0,
            "active_rate_pct": 0.0,
            "net_mean_bps": np.nan,
            "net_cum_pct": np.nan,
            "max_drawdown_pct": np.nan,
            "win_rate_pct": np.nan,
            "avg_eligible_universe_size": np.nan,
        })

    overall = pd.DataFrame(selected_rows)
    overall = overall.sort_values("net_mean_bps", ascending=False, na_position="last").reset_index(drop=True)

    annual_rows: list[dict] = []
    for spec in DIRECTION_SPECS[:3]:
        sub = annual_src[annual_src["strategy"] == spec["strategy"]].copy()
        for _, row in sub.iterrows():
            annual_rows.append({**spec, **row.to_dict()})
    if not funding_detail.empty:
        for year, sub in funding_detail.groupby(funding_detail["timestamp_ts"].dt.year):
            annual_rows.append({
                **DIRECTION_SPECS[3],
                "segment": str(int(year)),
                "label": "4) perp funding overlay on best price baseline",
                **calc_stats(sub),
            })
    annual = pd.DataFrame(annual_rows).sort_values(["segment", "net_mean_bps"], ascending=[True, False], na_position="last").reset_index(drop=True)

    overall.to_csv(OVERALL_PATH, index=False)
    annual.to_csv(ANNUAL_PATH, index=False)
    monthly.to_csv(MONTHLY_PATH, index=False)
    monthly_summary.to_csv(MONTHLY_SUMMARY_PATH, index=False)

    summary = {
        "generated_at_utc": pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ"),
        "objective": "initial four-direction review for replacing weak Rank213 baseline",
        "important_limitations": [
            "The first three directions reuse the existing daily baseline refresh under monthly-volume causal universe.",
            "The fourth direction is funding-only and limited to locally cached funding coverage; it does not include historical basis or open interest.",
            "Daily baseline refresh is not apples-to-apples with the original 15m Rank213 execution cadence.",
        ],
        "directions": DIRECTION_SPECS,
        "incumbent_plain_baseline": incumbent,
        "funding_overlay_meta": funding_meta,
        "overall": overall.to_dict(orient="records"),
        "artifacts": {
            "overall": str(OVERALL_PATH.relative_to(ROOT)),
            "annual": str(ANNUAL_PATH.relative_to(ROOT)),
            "monthly": str(MONTHLY_PATH.relative_to(ROOT)),
            "monthly_summary": str(MONTHLY_SUMMARY_PATH.relative_to(ROOT)),
            "funding_detail": str(FUNDING_DETAIL_PATH.relative_to(ROOT)),
            "site": str(SITE_PATH.relative_to(ROOT)),
        },
    }
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    SITE_PATH.write_text(build_report(overall, annual, monthly, monthly_summary, equity, funding_meta, incumbent), encoding="utf-8")
    print(f"wrote {SUMMARY_PATH.relative_to(ROOT)}")
    print(f"wrote {OVERALL_PATH.relative_to(ROOT)}")
    print(f"wrote {ANNUAL_PATH.relative_to(ROOT)}")
    print(f"wrote {MONTHLY_PATH.relative_to(ROOT)}")
    print(f"wrote {MONTHLY_SUMMARY_PATH.relative_to(ROOT)}")
    print(f"wrote {FUNDING_DETAIL_PATH.relative_to(ROOT)}")
    print(f"wrote {SITE_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
