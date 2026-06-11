#!/usr/bin/env python3
from __future__ import annotations

import json
from bisect import bisect_right, insort
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank213_largecap_xs_jump_veto"
SITE_PATH = ROOT / "reports" / "site" / "paper" / "rank213_largecap_xs_jump_veto_monthly_percentile_gate_review.html"

DETAIL_PATH = ART_DIR / "rank213_monthly_marketcap_universe_rebuild_detail.csv"
MONTHLY_SUMMARY_PATH = ART_DIR / "rank213_monthly_marketcap_universe_rebuild_summary.json"
FORMAL_SUMMARY_PATH = ART_DIR / "rank213_formal_threeway_backtest_summary.json"

SUMMARY_PATH = ART_DIR / "rank213_monthly_marketcap_percentile_gate_review_summary.json"
GRID_PATH = ART_DIR / "rank213_monthly_marketcap_percentile_gate_review_grid.csv"
BUCKET_PATH = ART_DIR / "rank213_monthly_marketcap_percentile_gate_review_strength_buckets.csv"
FEATURE_BUCKET_PATH = ART_DIR / "rank213_monthly_marketcap_percentile_gate_review_feature_buckets.csv"
DETAIL_OUT_PATH = ART_DIR / "rank213_monthly_marketcap_percentile_gate_review_detail.csv"
SUBPERIOD_GRID_PATH = ART_DIR / "rank213_monthly_marketcap_percentile_gate_review_subperiod_grid.csv"
DECISION_PATH = ART_DIR / "rank213_monthly_marketcap_percentile_gate_review_frozen_decision.json"

FEATURE_SPECS = {
    "gate_feature_veto_active_rate": {
        "label": "veto_active_rate",
        "human": "最近30天 short-leg jump veto 触发占比",
    },
    "gate_feature_xs_dispersion_bps": {
        "label": "xs_dispersion_bps",
        "human": "最近30天横截面离散度",
    },
    "gate_feature_ls_divergence_bps": {
        "label": "ls_divergence_bps",
        "human": "最近30天 long leg vs veto-short leg 已实现分化",
    },
}
FEATURE_COLS = list(FEATURE_SPECS.keys())
PERCENTILE_COLS = {col: FEATURE_SPECS[col]["label"] + "_pct" for col in FEATURE_COLS}
TARGET_ON_RATE_MIN = 20.0
TARGET_ON_RATE_MAX = 50.0
BUCKET_WIDTH = 5
MIN_HISTORY_ROWS = 1440  # ~180 days at 8 three-hour baskets/day
THRESHOLDS = list(range(0, 101))
FROZEN_Q = 60
FROZEN_NEIGHBORHOOD = [58, 59, 60, 61, 62]
SUBPERIODS = [
    ("2020-2021", "2020-01-01T00:00:00Z", "2022-01-01T00:00:00Z"),
    ("2022-2023", "2022-01-01T00:00:00Z", "2024-01-01T00:00:00Z"),
    ("2024-2026", "2024-01-01T00:00:00Z", None),
]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def to_iso(ts) -> str | None:
    if ts is None or pd.isna(ts):
        return None
    return pd.to_datetime(ts, utc=True).strftime("%Y-%m-%dT%H:%M:%SZ")


def fmt_pct(x: float | int | None, digits: int = 2) -> str:
    if x is None or pd.isna(x):
        return ""
    return f"{float(x):.{digits}f}%"


def fmt_bps(x: float | int | None, digits: int = 2) -> str:
    if x is None or pd.isna(x):
        return ""
    return f"{float(x):.{digits}f} bps"


def fmt_x(x: float | int | None, digits: int = 3) -> str:
    if x is None or pd.isna(x):
        return ""
    return f"{float(x):.{digits}f}x"


def render_table(df: pd.DataFrame, *, pct_cols: set[str] | None = None, bps_cols: set[str] | None = None, x_cols: set[str] | None = None, int_cols: set[str] | None = None) -> str:
    pct_cols = pct_cols or set()
    bps_cols = bps_cols or set()
    x_cols = x_cols or set()
    int_cols = int_cols or set()
    if df.empty:
        return "<p class='muted'>暂无数据。</p>"
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows: list[str] = []
    for _, row in df.iterrows():
        cols: list[str] = []
        for c in df.columns:
            v = row[c]
            if pd.isna(v):
                txt = ""
            elif c in pct_cols:
                txt = fmt_pct(v)
            elif c in bps_cols:
                txt = fmt_bps(v)
            elif c in x_cols:
                txt = fmt_x(v)
            elif c in int_cols:
                txt = str(int(v))
            elif isinstance(v, (float, np.floating)):
                txt = f"{float(v):.4f}"
            else:
                txt = escape(str(v))
            cols.append(f"<td>{txt}</td>")
        rows.append("<tr>" + "".join(cols) + "</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def max_drawdown(ret: pd.Series) -> float:
    if ret.empty:
        return np.nan
    eq = (1.0 + ret.fillna(0.0)).cumprod()
    dd = eq / eq.cummax() - 1.0
    return float(dd.min())


def calc_stats(df: pd.DataFrame, gate_on: pd.Series) -> dict:
    work = df.copy()
    gate_on = pd.Series(gate_on, index=work.index).fillna(False).astype(bool)
    gated_ret = np.where(gate_on, pd.to_numeric(work["veto_net"], errors="coerce"), 0.0)
    gated_turn = np.where(gate_on, pd.to_numeric(work["veto_turnover_x"], errors="coerce"), 0.0)
    veto_ret = pd.to_numeric(work["veto_net"], errors="coerce").fillna(0.0)
    veto_turn = pd.to_numeric(work["veto_turnover_x"], errors="coerce").fillna(0.0)
    gated_ret_s = pd.Series(gated_ret)
    months = work["month"].astype(str)
    active_months = months[gate_on].nunique()
    total_months = months.nunique()
    gated_dd = float(max_drawdown(gated_ret_s) * 100.0) if len(work) else np.nan
    veto_dd = float(max_drawdown(veto_ret) * 100.0) if len(work) else np.nan
    out = {
        "analysis_rows": int(len(work)),
        "gate_on_baskets": int(gate_on.sum()),
        "gate_on_rate_pct": float(gate_on.mean() * 100.0) if len(work) else np.nan,
        "gate_on_months": int(active_months),
        "gate_on_month_share_pct": float((active_months / total_months) * 100.0) if total_months else np.nan,
        "net_mean_bps": float(np.nanmean(gated_ret) * 10000.0) if len(work) else np.nan,
        "net_cum_pct": float(((1.0 + gated_ret_s).prod() - 1.0) * 100.0) if len(work) else np.nan,
        "max_drawdown_pct": gated_dd,
        "win_rate_pct": float((gated_ret_s > 0).mean() * 100.0) if len(work) else np.nan,
        "avg_turnover_x": float(np.nanmean(gated_turn)) if len(work) else np.nan,
        "veto_net_mean_bps": float(np.nanmean(veto_ret) * 10000.0) if len(work) else np.nan,
        "veto_net_cum_pct": float(((1.0 + veto_ret).prod() - 1.0) * 100.0) if len(work) else np.nan,
        "veto_max_drawdown_pct": veto_dd,
        "delta_net_mean_bps_vs_veto": float((np.nanmean(gated_ret) - np.nanmean(veto_ret)) * 10000.0) if len(work) else np.nan,
        "delta_net_cum_pct_vs_veto": float((((1.0 + gated_ret_s).prod() - 1.0) - ((1.0 + veto_ret).prod() - 1.0)) * 100.0) if len(work) else np.nan,
        "drawdown_improvement_pct_points_vs_veto": float(gated_dd - veto_dd) if len(work) else np.nan,
    }
    return out


def downsample_indices(n: int, max_points: int = 1200) -> np.ndarray:
    if n <= 0:
        return np.array([], dtype=int)
    if n <= max_points:
        return np.arange(n, dtype=int)
    return np.unique(np.linspace(0, n - 1, max_points, dtype=int))


def _scale_x(i: float, n: int, left: float, width: float) -> float:
    if n <= 1:
        return left
    return left + (float(i) / float(n - 1)) * width


def _scale_y(v: float, lo: float, hi: float, top: float, height: float) -> float:
    if hi <= lo:
        return top + height / 2.0
    return top + height - ((float(v) - lo) / (hi - lo)) * height


def _line_path(xs: np.ndarray, ys: np.ndarray, *, n_total: int, left: float, top: float, width: float, height: float, y_lo: float, y_hi: float) -> str:
    if len(xs) == 0:
        return ""
    pts: list[str] = []
    for i, v in zip(xs, ys):
        px = _scale_x(int(i), n_total, left, width)
        py = _scale_y(float(v), y_lo, y_hi, top, height)
        pts.append(f"{px:.2f},{py:.2f}")
    return "M " + " L ".join(pts)


def render_frozen_q60_chart(analysis: pd.DataFrame) -> str:
    if analysis.empty:
        return "<p class='muted'>暂无可绘制的 q=60 历史曲线。</p>"
    work = analysis[["timestamp_ts", "veto_net", "strength_min_pct"]].copy()
    work["gate_on_q60"] = pd.to_numeric(work["strength_min_pct"], errors="coerce") >= float(FROZEN_Q)
    work["veto_net"] = pd.to_numeric(work["veto_net"], errors="coerce").fillna(0.0)
    work["gated_ret_q60"] = np.where(work["gate_on_q60"], work["veto_net"], 0.0)
    work["gated_eq_pct"] = ((1.0 + work["gated_ret_q60"]).cumprod() - 1.0) * 100.0
    work["veto_eq_pct"] = ((1.0 + work["veto_net"]).cumprod() - 1.0) * 100.0

    n = len(work)
    idx = downsample_indices(n, max_points=1400)
    sample = work.iloc[idx].copy().reset_index().rename(columns={"index": "orig_i"})

    left = 72.0
    right = 22.0
    top = 24.0
    plot_h = 260.0
    strip_top = top + plot_h + 28.0
    strip_h = 22.0
    bottom = 42.0
    width = 1040.0
    total_h = strip_top + strip_h + bottom
    total_w = left + width + right

    y_vals = np.r_[work["gated_eq_pct"].to_numpy(), work["veto_eq_pct"].to_numpy(), np.array([0.0])]
    y_lo = float(np.nanmin(y_vals))
    y_hi = float(np.nanmax(y_vals))
    pad = max((y_hi - y_lo) * 0.08, 4.0)
    y_lo -= pad
    y_hi += pad

    gated_path = _line_path(sample["orig_i"].to_numpy(), sample["gated_eq_pct"].to_numpy(), n_total=n, left=left, top=top, width=width, height=plot_h, y_lo=y_lo, y_hi=y_hi)
    veto_path = _line_path(sample["orig_i"].to_numpy(), sample["veto_eq_pct"].to_numpy(), n_total=n, left=left, top=top, width=width, height=plot_h, y_lo=y_lo, y_hi=y_hi)

    shade_rects: list[str] = []
    strip_rects: list[str] = [f"<rect x='{left:.2f}' y='{strip_top:.2f}' width='{width:.2f}' height='{strip_h:.2f}' fill='#e2e8f0' rx='4'/>" ]
    gate_flags = work["gate_on_q60"].to_numpy(dtype=bool)
    n_bins = min(320, n)
    edges = np.linspace(0, n, n_bins + 1, dtype=int)
    for b in range(n_bins):
        s = int(edges[b])
        e = int(max(edges[b + 1] - 1, s))
        if s >= n:
            continue
        on_share = float(gate_flags[s:e + 1].mean()) if e >= s else 0.0
        if on_share <= 0:
            continue
        x0 = _scale_x(s, n, left, width)
        x1 = _scale_x(e, n, left, width)
        w = max(x1 - x0, width / max(n_bins, 1))
        opacity = 0.10 + 0.22 * on_share
        shade_rects.append(f"<rect x='{x0:.2f}' y='{top:.2f}' width='{w:.2f}' height='{plot_h:.2f}' fill='#86efac' opacity='{opacity:.3f}' />")
        strip_rects.append(f"<rect x='{x0:.2f}' y='{strip_top:.2f}' width='{w:.2f}' height='{strip_h:.2f}' fill='#16a34a' opacity='{min(0.35 + 0.65 * on_share, 1.0):.3f}' rx='2' />")

    grid_lines: list[str] = []
    y_ticks: list[str] = []
    for frac in np.linspace(0.0, 1.0, 5):
        y = top + frac * plot_h
        val = y_hi - frac * (y_hi - y_lo)
        grid_lines.append(f"<line x1='{left:.2f}' y1='{y:.2f}' x2='{left + width:.2f}' y2='{y:.2f}' stroke='#e2e8f0' stroke-width='1' />")
        y_ticks.append(f"<text x='{left - 10:.2f}' y='{y + 4:.2f}' text-anchor='end' font-size='12' fill='#64748b'>{val:.0f}%</text>")

    x_labels = [
        (0, work.iloc[0]["timestamp_ts"].strftime("%Y-%m")),
        (n // 2, work.iloc[n // 2]["timestamp_ts"].strftime("%Y-%m")),
        (n - 1, work.iloc[-1]["timestamp_ts"].strftime("%Y-%m")),
    ]
    x_ticks = []
    for pos, label in x_labels:
        x = _scale_x(pos, n, left, width)
        x_ticks.append(f"<line x1='{x:.2f}' y1='{top + plot_h:.2f}' x2='{x:.2f}' y2='{top + plot_h + 6:.2f}' stroke='#94a3b8' stroke-width='1' />")
        x_ticks.append(f"<text x='{x:.2f}' y='{strip_top + strip_h + 22:.2f}' text-anchor='middle' font-size='12' fill='#64748b'>{label}</text>")

    zero_y = _scale_y(0.0, y_lo, y_hi, top, plot_h)
    gate_on_rate = float(work["gate_on_q60"].mean() * 100.0)
    cond_mean = float(work.loc[work["gate_on_q60"], "veto_net"].mean() * 10000.0) if work["gate_on_q60"].any() else np.nan
    final_gated = float(work["gated_eq_pct"].iloc[-1])
    final_veto = float(work["veto_eq_pct"].iloc[-1])

    legend_y = 12.0
    legend = f"""
      <circle cx='{left:.2f}' cy='{legend_y:.2f}' r='4' fill='#2563eb'/><text x='{left + 10:.2f}' y='{legend_y + 4:.2f}' font-size='12' fill='#0f172a'>q=60 gated cumulative return</text>
      <circle cx='{left + 235:.2f}' cy='{legend_y:.2f}' r='4' fill='#475569'/><text x='{left + 245:.2f}' y='{legend_y + 4:.2f}' font-size='12' fill='#0f172a'>always-on veto baseline</text>
      <rect x='{left + 425:.2f}' y='{legend_y - 5:.2f}' width='16' height='10' fill='#86efac' opacity='0.35' /><text x='{left + 447:.2f}' y='{legend_y + 4:.2f}' font-size='12' fill='#0f172a'>gate ON window</text>
    """

    svg = f"""
    <svg viewBox='0 0 {total_w:.0f} {total_h:.0f}' width='100%' role='img' aria-label='q60 cumulative return with gate on/off windows'>
      <rect x='0' y='0' width='{total_w:.0f}' height='{total_h:.0f}' fill='#ffffff' rx='12'/>
      {''.join(grid_lines)}
      <line x1='{left:.2f}' y1='{zero_y:.2f}' x2='{left + width:.2f}' y2='{zero_y:.2f}' stroke='#94a3b8' stroke-width='1.2' stroke-dasharray='4 4' />
      {''.join(shade_rects)}
      <path d='{veto_path}' fill='none' stroke='#475569' stroke-width='2.0' />
      <path d='{gated_path}' fill='none' stroke='#2563eb' stroke-width='2.4' />
      <line x1='{left:.2f}' y1='{top + plot_h:.2f}' x2='{left + width:.2f}' y2='{top + plot_h:.2f}' stroke='#0f172a' stroke-width='1.2' />
      <line x1='{left:.2f}' y1='{top:.2f}' x2='{left:.2f}' y2='{top + plot_h:.2f}' stroke='#0f172a' stroke-width='1.2' />
      {''.join(y_ticks)}
      {''.join(x_ticks)}
      {''.join(strip_rects)}
      <text x='{left - 12:.2f}' y='{strip_top + strip_h/2 + 4:.2f}' text-anchor='end' font-size='12' fill='#64748b'>gate</text>
      {legend}
      <text x='{left:.2f}' y='{total_h - 8:.2f}' font-size='12' fill='#475569'>q=60 full-sample cum={final_gated:.2f}% · always-on veto cum={final_veto:.2f}% · gate-on rate={gate_on_rate:.2f}% · conditional mean when ON={cond_mean:.2f} bps</text>
    </svg>
    """
    return svg


def expanding_percentile(series: pd.Series, *, min_history_rows: int) -> pd.Series:
    hist: list[float] = []
    out = np.full(len(series), np.nan, dtype=float)
    valid_hist = 0
    for i, raw in enumerate(series.to_numpy()):
        val = pd.to_numeric(raw, errors="coerce")
        if not pd.isna(val) and valid_hist >= min_history_rows:
            out[i] = 100.0 * bisect_right(hist, float(val)) / float(valid_hist)
        if not pd.isna(val):
            insort(hist, float(val))
            valid_hist += 1
    return pd.Series(out, index=series.index)


def assign_bucket_labels(values: pd.Series, *, width: int = BUCKET_WIDTH) -> pd.Series:
    def one(x):
        if pd.isna(x):
            return None
        v = min(max(float(x), 0.0), 100.0)
        if v == 100.0:
            lo = 100 - width
        else:
            lo = int(np.floor(v / width) * width)
        hi = lo + width
        if hi >= 100:
            return f"[{lo},{100}]"
        return f"[{lo},{hi})"
    return values.apply(one)


def build_bucket_stats(df: pd.DataFrame, value_col: str, *, bucket_name: str) -> pd.DataFrame:
    work = df.copy()
    work[bucket_name] = assign_bucket_labels(work[value_col])
    work = work[work[bucket_name].notna()].copy()
    if work.empty:
        return pd.DataFrame()
    rows = []
    total = len(work)
    for bucket, grp in work.groupby(bucket_name, sort=False):
        lo = int(str(bucket).split(",")[0].replace("[", ""))
        rows.append({
            "bucket": bucket,
            "bucket_lo": lo,
            "rows": int(len(grp)),
            "share_pct": float(len(grp) / total * 100.0),
            "mean_strength_pct": float(pd.to_numeric(grp[value_col], errors="coerce").mean()),
            "mean_veto_net_bps": float(pd.to_numeric(grp["veto_net"], errors="coerce").mean() * 10000.0),
            "cum_veto_pct": float(((1.0 + pd.to_numeric(grp["veto_net"], errors="coerce").fillna(0.0)).prod() - 1.0) * 100.0),
            "max_drawdown_veto_pct": float(max_drawdown(pd.to_numeric(grp["veto_net"], errors="coerce").fillna(0.0)) * 100.0),
            "win_rate_pct": float((pd.to_numeric(grp["veto_net"], errors="coerce") > 0).mean() * 100.0),
            "avg_turnover_x": float(pd.to_numeric(grp["veto_turnover_x"], errors="coerce").mean()),
            "months": int(grp["month"].astype(str).nunique()),
        })
    return pd.DataFrame(rows).sort_values("bucket_lo").drop(columns=["bucket_lo"]).reset_index(drop=True)


def build_feature_bucket_stats(df: pd.DataFrame) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for feature_col, pct_col in PERCENTILE_COLS.items():
        part = build_bucket_stats(df, pct_col, bucket_name="bucket")
        if part.empty:
            continue
        part.insert(0, "feature", FEATURE_SPECS[feature_col]["label"])
        frames.append(part)
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    out["feature_order"] = out["feature"].map({FEATURE_SPECS[c]["label"]: i for i, c in enumerate(FEATURE_COLS)})
    out["bucket_lo"] = out["bucket"].astype(str).str.extract(r"\[(\d+),").astype(int)
    out = out.sort_values(["feature_order", "bucket_lo"]).drop(columns=["feature_order", "bucket_lo"]).reset_index(drop=True)
    return out


def compute_threshold_grid(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    grid_rows: list[dict] = []
    sub_rows: list[dict] = []
    current = df.iloc[-1] if not df.empty else None
    current_strength = float(current["strength_min_pct"]) if current is not None and pd.notna(current["strength_min_pct"]) else np.nan
    for q in THRESHOLDS:
        gate_on = pd.to_numeric(df["strength_min_pct"], errors="coerce") >= float(q)
        stats = calc_stats(df, gate_on)
        row = {
            "threshold_pct": int(q),
            **stats,
            "current_strength_min_pct": current_strength,
            "current_window_gate_on": bool(pd.notna(current_strength) and current_strength >= float(q)),
        }
        pos_count = 0
        for label, start, end in SUBPERIODS:
            start_ts = pd.Timestamp(start)
            end_ts = pd.Timestamp(end) if end else None
            sub = df[df["timestamp_ts"] >= start_ts].copy()
            if end_ts is not None:
                sub = sub[sub["timestamp_ts"] < end_ts]
            if sub.empty:
                sub_stats = {k: np.nan for k in ["analysis_rows", "gate_on_baskets", "gate_on_rate_pct", "net_mean_bps", "net_cum_pct", "max_drawdown_pct", "delta_net_mean_bps_vs_veto", "delta_net_cum_pct_vs_veto"]}
            else:
                sub_gate = pd.to_numeric(sub["strength_min_pct"], errors="coerce") >= float(q)
                sub_stats = calc_stats(sub, sub_gate)
                if pd.notna(sub_stats["delta_net_mean_bps_vs_veto"]) and sub_stats["delta_net_mean_bps_vs_veto"] > 0:
                    pos_count += 1
            sub_rows.append({
                "threshold_pct": int(q),
                "subperiod": label,
                **sub_stats,
            })
        row["subperiod_positive_count"] = int(pos_count)
        grid_rows.append(row)
    return pd.DataFrame(grid_rows), pd.DataFrame(sub_rows)


def pick_recommendation(grid: pd.DataFrame) -> tuple[dict | None, pd.DataFrame]:
    if grid.empty:
        return None, pd.DataFrame()
    candidates = grid[
        grid["gate_on_rate_pct"].between(TARGET_ON_RATE_MIN, TARGET_ON_RATE_MAX)
        & (grid["delta_net_mean_bps_vs_veto"] > 0)
        & (grid["subperiod_positive_count"] >= 2)
    ].copy()
    if candidates.empty:
        fallback = grid[(grid["delta_net_mean_bps_vs_veto"] > 0)].copy()
        if fallback.empty:
            return None, candidates
        fallback["target_band_distance"] = np.where(
            fallback["gate_on_rate_pct"] < TARGET_ON_RATE_MIN,
            TARGET_ON_RATE_MIN - fallback["gate_on_rate_pct"],
            np.where(fallback["gate_on_rate_pct"] > TARGET_ON_RATE_MAX, fallback["gate_on_rate_pct"] - TARGET_ON_RATE_MAX, 0.0),
        )
        fallback = fallback.sort_values(["target_band_distance", "subperiod_positive_count", "threshold_pct", "delta_net_mean_bps_vs_veto"], ascending=[True, False, False, False])
        return fallback.iloc[0].to_dict(), candidates
    candidates = candidates.sort_values(["threshold_pct", "delta_net_mean_bps_vs_veto", "net_cum_pct"], ascending=[False, False, False])
    return candidates.iloc[0].to_dict(), candidates


def compute_current_raw_thresholds(detail: pd.DataFrame, *, q: int) -> dict:
    current = detail.iloc[-1] if not detail.empty else None
    prior = detail.iloc[:-1].copy() if len(detail) >= 2 else pd.DataFrame()
    out: dict[str, dict] = {}
    for col in FEATURE_COLS:
        s = pd.to_numeric(prior[col], errors="coerce").dropna()
        threshold = float(np.quantile(s.to_numpy(), q / 100.0)) if len(s) else np.nan
        current_value = float(current[col]) if current is not None and pd.notna(current[col]) else np.nan
        out[FEATURE_SPECS[col]["label"]] = {
            "feature_col": col,
            "threshold": threshold,
            "current_value": current_value,
            "pass": bool(pd.notna(current_value) and pd.notna(threshold) and current_value >= threshold),
        }
    return out


def load_inputs() -> tuple[pd.DataFrame, dict, dict]:
    detail = pd.read_csv(DETAIL_PATH)
    detail["timestamp_ts"] = pd.to_datetime(detail["timestamp_ts"], utc=True)
    detail["exit_ts"] = pd.to_datetime(detail["exit_ts"], utc=True)
    for col in ["veto_net", "veto_turnover_x", *FEATURE_COLS, "gate_on", "gate_net"]:
        if col in detail.columns:
            detail[col] = pd.to_numeric(detail[col], errors="coerce")
    detail = detail.sort_values("timestamp_ts").reset_index(drop=True)
    monthly_summary = read_json(MONTHLY_SUMMARY_PATH)
    formal_summary = read_json(FORMAL_SUMMARY_PATH)
    return detail, monthly_summary, formal_summary


def build_review() -> dict:
    detail, monthly_summary, formal_summary = load_inputs()
    for feature_col, pct_col in PERCENTILE_COLS.items():
        detail[pct_col] = expanding_percentile(detail[feature_col], min_history_rows=MIN_HISTORY_ROWS)
    detail["strength_min_pct"] = detail[list(PERCENTILE_COLS.values())].min(axis=1, skipna=False)
    detail["strength_mean_pct"] = detail[list(PERCENTILE_COLS.values())].mean(axis=1, skipna=False)

    analysis = detail[detail["strength_min_pct"].notna()].copy().reset_index(drop=True)
    analysis_start = to_iso(analysis["timestamp_ts"].min()) if not analysis.empty else None
    analysis_end = to_iso(analysis["timestamp_ts"].max()) if not analysis.empty else None

    strength_buckets = build_bucket_stats(analysis, "strength_min_pct", bucket_name="bucket")
    feature_buckets = build_feature_bucket_stats(analysis)
    grid, sub_grid = compute_threshold_grid(analysis)
    recommendation, candidate_table = pick_recommendation(grid)

    detail_out = detail.copy()
    for col in detail_out.columns:
        if pd.api.types.is_datetime64_any_dtype(detail_out[col]):
            detail_out[col] = detail_out[col].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    detail_out.to_csv(DETAIL_OUT_PATH, index=False)
    strength_buckets.to_csv(BUCKET_PATH, index=False)
    feature_buckets.to_csv(FEATURE_BUCKET_PATH, index=False)
    grid.to_csv(GRID_PATH, index=False)
    sub_grid.to_csv(SUBPERIOD_GRID_PATH, index=False)

    current = analysis.iloc[-1].copy() if not analysis.empty else None
    current_snapshot = None
    if current is not None:
        current_snapshot = {
            "timestamp_ts": to_iso(current["timestamp_ts"]),
            "month": str(current["month"]),
            "strength_min_pct": float(current["strength_min_pct"]),
            "strength_mean_pct": float(current["strength_mean_pct"]),
            "pct_veto_active_rate": float(current[PERCENTILE_COLS["gate_feature_veto_active_rate"]]),
            "pct_xs_dispersion_bps": float(current[PERCENTILE_COLS["gate_feature_xs_dispersion_bps"]]),
            "pct_ls_divergence_bps": float(current[PERCENTILE_COLS["gate_feature_ls_divergence_bps"]]),
            "raw_veto_active_rate": float(current["gate_feature_veto_active_rate"]),
            "raw_xs_dispersion_bps": float(current["gate_feature_xs_dispersion_bps"]),
            "raw_ls_divergence_bps": float(current["gate_feature_ls_divergence_bps"]) if pd.notna(current["gate_feature_ls_divergence_bps"]) else None,
        }

    frozen_row = grid[grid["threshold_pct"] == FROZEN_Q].iloc[0].to_dict() if not grid.empty and (grid["threshold_pct"] == FROZEN_Q).any() else None
    frozen_neighborhood = grid[grid["threshold_pct"].isin(FROZEN_NEIGHBORHOOD)].copy().sort_values("threshold_pct")
    frozen_subperiods = sub_grid[sub_grid["threshold_pct"] == FROZEN_Q].copy().sort_values("subperiod")
    frozen_current_raw_thresholds = compute_current_raw_thresholds(detail, q=FROZEN_Q)
    frozen_decision = {
        "decision_type": "freeze",
        "frozen_q": int(FROZEN_Q),
        "why": "Use the center of the 58-62 robust plateau instead of the q≈50 sign-flip edge. q=60 stays comfortably above the 2024-2026 zero-crossing, keeps all three subperiods positive, and is easier to explain than 61/62 while avoiding the extra sparsity of 65+.",
        "live_policy": "Do not switch the current live/formal raw gate to percentile q=60 immediately. Freeze q=60 as the approved research/adaptive target for monthly-rebuild evidence, but keep the current causal_live_aligned raw gate unchanged for live execution for now, because the latest monthly snapshot would be OFF under q=60.",
        "activation_rule": "Percentile gate ON iff strength_min_pct >= 60, equivalently all three expanding feature percentiles are at or above 60.",
        "current_snapshot_under_frozen_q": {
            "strength_min_pct": float(current_snapshot["strength_min_pct"]) if current_snapshot else np.nan,
            "gate_on": bool(current_snapshot and float(current_snapshot["strength_min_pct"]) >= float(FROZEN_Q)),
            "raw_thresholds": frozen_current_raw_thresholds,
        },
        "frozen_row": frozen_row,
        "neighborhood_rows": frozen_neighborhood.to_dict(orient="records"),
        "subperiod_rows": frozen_subperiods.to_dict(orient="records"),
    }

    summary = {
        "scope": "monthly marketcap rebuild percentile gate review using causal monthly-rebuild feature history only",
        "methodology": {
            "universe_definition": "For each historical rebalance t, first use the month containing t to define the as-of monthly marketcap-proxy universe; then use that row's own monthly-rebuild features.",
            "percentile_definition": "For each row t, each feature percentile is computed only from prior monthly-rebuild rows (timestamp < t) under the same monthly-rebuild process; future rows are never used.",
            "strength_definition": "strength_min_pct = min(pct_veto_active_rate, pct_xs_dispersion_bps, pct_ls_divergence_bps).",
            "gate_definition": "percentile gate turns ON when strength_min_pct >= q, where q is scanned from 0 to 100.",
            "min_history_rows": int(MIN_HISTORY_ROWS),
            "bucket_width_pct_points": int(BUCKET_WIDTH),
            "threshold_scan": [int(THRESHOLDS[0]), int(THRESHOLDS[-1])],
            "target_on_rate_band_pct": [TARGET_ON_RATE_MIN, TARGET_ON_RATE_MAX],
        },
        "input_paths": {
            "monthly_detail": str(DETAIL_PATH.relative_to(ROOT)),
            "monthly_summary": str(MONTHLY_SUMMARY_PATH.relative_to(ROOT)),
            "formal_summary": str(FORMAL_SUMMARY_PATH.relative_to(ROOT)),
        },
        "sample": {
            "full_rows": int(len(detail)),
            "analysis_rows": int(len(analysis)),
            "analysis_start_utc": analysis_start,
            "analysis_end_utc": analysis_end,
            "analysis_months": int(analysis["month"].astype(str).nunique()) if not analysis.empty else 0,
        },
        "anchors": {
            "formal_gate_on_rate_pct": float(formal_summary.get("gate", {}).get("on_rate_pct", np.nan)),
            "monthly_raw_gate_on_rate_pct": float(monthly_summary.get("metrics", {}).get("monthly_marketcap_rebuild", {}).get("baseline_plus_veto_plus_gate", {}).get("gate_on_rate_pct", np.nan)),
            "monthly_raw_gate_net_cum_pct": float(monthly_summary.get("metrics", {}).get("monthly_marketcap_rebuild", {}).get("baseline_plus_veto_plus_gate", {}).get("net_cum_pct", np.nan)),
        },
        "current_snapshot": current_snapshot,
        "recommendation": recommendation,
        "frozen_decision": frozen_decision,
        "candidate_count_in_target_band": int(len(candidate_table)),
        "output_paths": {
            "summary_json": str(SUMMARY_PATH.relative_to(ROOT)),
            "grid_csv": str(GRID_PATH.relative_to(ROOT)),
            "strength_bucket_csv": str(BUCKET_PATH.relative_to(ROOT)),
            "feature_bucket_csv": str(FEATURE_BUCKET_PATH.relative_to(ROOT)),
            "detail_csv": str(DETAIL_OUT_PATH.relative_to(ROOT)),
            "subperiod_grid_csv": str(SUBPERIOD_GRID_PATH.relative_to(ROOT)),
            "decision_json": str(DECISION_PATH.relative_to(ROOT)),
            "html": str(SITE_PATH.relative_to(ROOT)),
        },
    }
    ensure_dir(SUMMARY_PATH.parent)
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    DECISION_PATH.write_text(json.dumps(frozen_decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "detail": detail,
        "analysis": analysis,
        "strength_buckets": strength_buckets,
        "feature_buckets": feature_buckets,
        "grid": grid,
        "sub_grid": sub_grid,
        "summary": summary,
        "recommendation": recommendation,
        "candidate_table": candidate_table,
    }


def write_html(payload: dict) -> None:
    summary = payload["summary"]
    analysis = payload["analysis"]
    strength_buckets = payload["strength_buckets"]
    feature_buckets = payload["feature_buckets"]
    grid = payload["grid"]
    candidate_table = payload["candidate_table"]
    recommendation = payload["recommendation"]
    frozen_decision = summary.get("frozen_decision") or {}

    top_strength = strength_buckets.copy()
    top_strength = top_strength[["bucket", "rows", "share_pct", "mean_strength_pct", "mean_veto_net_bps", "cum_veto_pct", "max_drawdown_veto_pct", "months"]]

    feature_display = feature_buckets[["feature", "bucket", "rows", "share_pct", "mean_veto_net_bps", "cum_veto_pct", "months"]].copy() if not feature_buckets.empty else pd.DataFrame()

    grid_display = grid.copy()
    grid_display = grid_display[(grid_display["threshold_pct"] % 5) == 0].copy()
    grid_display = grid_display[[
        "threshold_pct", "gate_on_rate_pct", "gate_on_baskets", "gate_on_months", "net_mean_bps", "net_cum_pct", "max_drawdown_pct", "delta_net_mean_bps_vs_veto", "subperiod_positive_count", "current_window_gate_on"
    ]]

    candidate_display = candidate_table[[
        "threshold_pct", "gate_on_rate_pct", "gate_on_baskets", "gate_on_months", "net_mean_bps", "net_cum_pct", "max_drawdown_pct", "delta_net_mean_bps_vs_veto", "subperiod_positive_count"
    ]].head(12).copy() if not candidate_table.empty else pd.DataFrame()

    current = summary.get("current_snapshot") or {}
    rec_block = "<div class='warn'><b>当前没有找到同时满足 target on-rate + 正 delta + 子区间稳定性的推荐阈值。</b></div>"
    if recommendation:
        rec_block = f"""
    <div class='good'>
      <b>扫描器按原规则给出的默认推荐阈值：</b><code>q = {int(recommendation['threshold_pct'])}</code><br/>
      理由：它落在目标 on-rate 带 <code>{TARGET_ON_RATE_MIN:.0f}%~{TARGET_ON_RATE_MAX:.0f}%</code> 内（当前 <code>{float(recommendation['gate_on_rate_pct']):.2f}%</code>），同时 full-period 相对 <code>veto</code> 仍保持正增量（<code>{float(recommendation['delta_net_mean_bps_vs_veto']):.2f} bps</code>），且三个子区间里有 <code>{int(recommendation['subperiod_positive_count'])}</code> 段为正。<br/>
      这只是按预设筛选规则得出的 <b>scan recommendation</b>，不是最终人工冻结值。
    </div>
"""

    frozen_block = ""
    if frozen_decision:
        frozen_q = int(frozen_decision.get("frozen_q", FROZEN_Q))
        frozen_row = frozen_decision.get("frozen_row") or {}
        snap = frozen_decision.get("current_snapshot_under_frozen_q") or {}
        frozen_block = f"""
    <div class='warn'>
      <b>本次最终冻结决策：</b><code>q = {frozen_q}</code><br/>
      不是选 <code>q=50</code> 这个“刚从负收益翻正”的边缘点，而是取 <code>58~62</code> 稳定平台的中位点 <code>q=60</code>。对应 full-period：<code>on-rate={float(frozen_row.get('gate_on_rate_pct', float('nan'))):.2f}%</code>、<code>net_mean={float(frozen_row.get('net_mean_bps', float('nan'))):.2f} bps</code>、<code>delta_vs_veto={float(frozen_row.get('delta_net_mean_bps_vs_veto', float('nan'))):.2f} bps</code>，且三个子区间仍是 <code>{int(frozen_row.get('subperiod_positive_count', 0))}/3</code> 为正。<br/>
      <b>固定 gate 定义：</b><code>strength_min_pct &gt;= {frozen_q}</code> 才算 ON。<br/>
      <b>但实盘策略暂不立即切换到这个 percentile gate。</b>原因很简单：当前最新 snapshot 的 <code>strength_min_pct={float(snap.get('strength_min_pct', float('nan'))):.2f}</code>，若现在就切到 <code>q={frozen_q}</code> 会是 <code>{'ON' if snap.get('gate_on') else 'OFF'}</code>；因此本次先把 <b>研究结论 / 冻结参数</b> 定下来，live execution 继续沿用当前 causal-live-aligned raw gate，避免此刻直接影响实盘。
    </div>
"""

    q60_chart = render_frozen_q60_chart(analysis)

    method_list = f"""
    <ul>
      <li><b>Universe 口径固定：</b>对每个历史时点 <code>t</code>，先用 <code>t</code> 所在月份的 monthly marketcap-proxy rebuild 定义当时 universe，再读取该行对应的 monthly-rebuild feature；不是拿“当前这组币”回头跑历史 percentile。</li>
      <li><b>Percentile 口径固定：</b>对每个历史时点 <code>t</code>，每个 feature 的 percentile 只用 <code>t</code> 之前的 monthly-rebuild 历史行计算；不允许偷看未来。</li>
      <li><b>强度定义固定：</b><code>strength_min_pct = min(pct_veto_active_rate, pct_xs_dispersion_bps, pct_ls_divergence_bps)</code>。</li>
      <li><b>本轮分桶：</b>覆盖 <code>0~100</code> 全范围，按 <code>{BUCKET_WIDTH}</code> percentile points 分桶，而不是只看 <code>{TARGET_ON_RATE_MIN:.0f}%~{TARGET_ON_RATE_MAX:.0f}%</code> 区间。</li>
      <li><b>阈值扫描：</b>离线扫描 <code>q = 0..100</code>，最后再根据研究结果决定阈值放哪，不先拍脑袋定 <code>p50</code>。</li>
      <li><b>Warmup：</b>percentile 至少要求 <code>{MIN_HISTORY_ROWS}</code> 条 prior monthly-rebuild 历史行后才生效；因此本研究的 analysis sample 从 <code>{escape(str(summary['sample']['analysis_start_utc']))}</code> 开始。</li>
    </ul>
"""

    body = f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank213 monthly marketcap percentile gate review (retired)</title>
  <style>
    :root{{--bg:#f8fafc;--card:#fff;--fg:#0f172a;--muted:#64748b;--line:#e2e8f0;--ok:#166534;--okbg:#dcfce7;--warn:#9a3412;--warnbg:#ffedd5;--note:#1d4ed8;--notebg:#dbeafe;}}
    *{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.65 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}}
    .wrap{{max-width:1180px;margin:0 auto;padding:28px 18px 64px}} .card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin-bottom:14px}}
    h1,h2,h3{{margin:0 0 12px}} .muted{{color:var(--muted)}} code{{background:#eff6ff;border-radius:6px;padding:2px 6px}} pre{{margin:0;white-space:pre-wrap;background:#f8fafc;border:1px solid var(--line);border-radius:10px;padding:10px;font-size:12px}}
    .good{{border-left:4px solid var(--ok);background:var(--okbg);padding:12px 14px;border-radius:10px}} .warn{{border-left:4px solid var(--warn);background:var(--warnbg);padding:12px 14px;border-radius:10px}} .note{{border-left:4px solid var(--note);background:var(--notebg);padding:12px 14px;border-radius:10px}}
    table{{width:100%;border-collapse:collapse}} th,td{{border-bottom:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}} th{{background:#f8fafc}} a{{color:#0f5bd8;text-decoration:none}} a:hover{{text-decoration:underline}}
  </style>
</head>
<body><div class='wrap'>
  <div class='card'>
    <h1>Rank213：monthly marketcap rebuild × percentile gate review 已退役</h1>
    <p class='muted'>这页建立在已退役的 monthly marketcap rebuild 口径上，只保留为历史审计记录。当前主线请看 <a href='/momentum/paper/rank213_evidence_map.html'>evidence_map</a> 与 <a href='/momentum/paper/rank213_largecap_xs_jump_veto_monthly_volume_percentile_gate_review.html'>monthly volume percentile gate review</a>。</p>
    <p><a href='/momentum/paper/rank213_evidence_map.html'>evidence_map</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_monthly_volume_universe_rebuild.html'>monthly volume rebuild</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto.html'>返回主页面</a></p>
  </div>

  <div class='card warn'>
    <b>退役原因：</b>marketcap proxy 口径已被 monthly volume causal universe 取代；不要再用本页作为当前结论、实盘依据或历史有效性证明。
  </div>

  <div class='card'>
    <h2>先给结论</h2>
    <div class='warn'><b>先说原问题：</b>当前 raw-threshold monthly rebuild gate 的确太稀。formal frozen gate 的长期 on-rate 约 <code>{summary['anchors']['formal_gate_on_rate_pct']:.2f}%</code>，但 monthly raw gate 只有 <code>{summary['anchors']['monthly_raw_gate_on_rate_pct']:.3f}%</code>，所以它在 5 年多历史里几乎只抓到极少数月份，统计效力偏弱。</div>
    {rec_block}
    {frozen_block}
    <div class='note'><b>当前窗口快照：</b>最新 monthly rebuild 行 <code>{escape(str(current.get('timestamp_ts')))}</code> 的 <code>strength_min_pct</code> 是 <code>{'' if pd.isna(current.get('strength_min_pct')) else f'{float(current.get('strength_min_pct')):.2f}'}</code>。三个单项 percentile 分别是：<code>veto={'' if pd.isna(current.get('pct_veto_active_rate')) else f'{float(current.get('pct_veto_active_rate')):.2f}'}</code>、<code>xs={'' if pd.isna(current.get('pct_xs_dispersion_bps')) else f'{float(current.get('pct_xs_dispersion_bps')):.2f}'}</code>、<code>ls={'' if pd.isna(current.get('pct_ls_divergence_bps')) else f'{float(current.get('pct_ls_divergence_bps')):.2f}'}</code>。</div>
  </div>

  <div class='card'>
    <h2>这次固定下来的计算口径</h2>
    {method_list}
  </div>

  <div class='card'>
    <h2>q=60 历史累计收益曲线（结合 gate on/off）</h2>
    <div class='note'><b>怎么读这张图：</b>蓝线是 <code>q=60</code> gate 真正接到时间轴后的累计收益曲线；灰线是 <code>always-on veto baseline</code>；浅绿色背景和下方状态条表示 <code>gate ON</code> 的时段。也就是说，蓝线在多数时间会变平，不是因为没收益，而是因为那些时段 gate 关着、回报被记为 <code>0</code>。</div>
    {q60_chart}
  </div>

  <div class='card'>
    <h2>Strength 分桶（覆盖 0~100 全范围）</h2>
    <div class='good'><b>怎么读这张表：</b>这里看的是 <code>strength_min_pct</code> 不同 bucket 下，原始 <code>veto</code> 条件收益的表现。如果 bucket 越高、收益/回撤越有改善，说明 percentile 强度确实在分层，而不是纯噪声。</div>
    {render_table(top_strength, pct_cols={'share_pct', 'cum_veto_pct', 'max_drawdown_veto_pct', 'win_rate_pct'}, bps_cols={'mean_veto_net_bps'}, x_cols={'avg_turnover_x'}, int_cols={'rows', 'months'})}
  </div>

  <div class='card'>
    <h2>单 feature 分桶（辅助看哪一维更有解释力）</h2>
    {render_table(feature_display, pct_cols={'share_pct', 'cum_veto_pct', 'win_rate_pct'}, bps_cols={'mean_veto_net_bps'}, int_cols={'rows', 'months'})}
  </div>

  <div class='card'>
    <h2>Threshold grid（每 5 个点展示一次；完整结果见 CSV）</h2>
    <div class='note'><b>注意：</b>分桶是 <code>0~100</code> 全覆盖；阈值表这里每 <code>5</code> 个点展示一次只是为了网页可读性，完整扫描仍然是 <code>q = 0..100</code>。</div>
    {render_table(grid_display, pct_cols={'gate_on_rate_pct', 'net_cum_pct', 'max_drawdown_pct', 'gate_on_month_share_pct'}, bps_cols={'net_mean_bps', 'delta_net_mean_bps_vs_veto'}, int_cols={'threshold_pct', 'gate_on_baskets', 'gate_on_months', 'subperiod_positive_count'})}
  </div>

  <div class='card'>
    <h2>落在目标 on-rate 带（20%~50%）的候选阈值</h2>
    {render_table(candidate_display, pct_cols={'gate_on_rate_pct', 'net_cum_pct', 'max_drawdown_pct'}, bps_cols={'net_mean_bps', 'delta_net_mean_bps_vs_veto'}, int_cols={'threshold_pct', 'gate_on_baskets', 'gate_on_months', 'subperiod_positive_count'})}
  </div>

  <div class='card'>
    <h2>文件输出</h2>
    <ul>
      <li><code>{escape(summary['output_paths']['summary_json'])}</code></li>
      <li><code>{escape(summary['output_paths']['grid_csv'])}</code></li>
      <li><code>{escape(summary['output_paths']['strength_bucket_csv'])}</code></li>
      <li><code>{escape(summary['output_paths']['feature_bucket_csv'])}</code></li>
      <li><code>{escape(summary['output_paths']['detail_csv'])}</code></li>
      <li><code>{escape(summary['output_paths']['subperiod_grid_csv'])}</code></li>
      <li><code>{escape(summary['output_paths']['decision_json'])}</code></li>
    </ul>
  </div>
</div></body>
</html>
"""
    ensure_dir(SITE_PATH.parent)
    SITE_PATH.write_text(body, encoding="utf-8")


def main() -> int:
    payload = build_review()
    write_html(payload)
    print(json.dumps(payload["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
