#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from dataclasses import dataclass
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank213_largecap_xs_jump_veto"
SITE_PATH = ROOT / "reports" / "site" / "paper" / "rank213_largecap_xs_jump_veto_monthly_volume_baseline_refresh.html"

MONTHLY_UNIVERSE_PATH = ART_DIR / "rank213_monthly_volume_universe_rebuild_monthly_universe.csv"
CANDIDATE_PATH = ART_DIR / "rank213_monthly_volume_universe_rebuild_candidates.csv"
INCUMBENT_SUMMARY_PATH = ART_DIR / "rank213_monthly_volume_universe_rebuild_summary.json"
INCUMBENT_DETAIL_PATH = ART_DIR / "rank213_monthly_volume_universe_rebuild_detail.csv"

SUMMARY_PATH = ART_DIR / "rank213_monthly_volume_baseline_refresh_summary.json"
SPEC_PATH = ART_DIR / "rank213_monthly_volume_baseline_refresh_spec.json"
OVERALL_PATH = ART_DIR / "rank213_monthly_volume_baseline_refresh_overall.csv"
ANNUAL_PATH = ART_DIR / "rank213_monthly_volume_baseline_refresh_annual.csv"
DAILY_PATH = ART_DIR / "rank213_monthly_volume_baseline_refresh_daily.csv"

TOP_N = 3
BOTTOM_N = 3
ONE_WAY_COST_BPS = 4.0
ROUND_COST = ONE_WAY_COST_BPS / 10000.0

MODULE_PATH = ROOT / "scripts" / "build_rank213_monthly_volume_universe_rebuild.py"


@dataclass(frozen=True)
class StrategySpec:
    key: str
    label: str
    age_days: int
    top_liq_n: int | None
    score_kind: str
    description: str


SPECS = [
    StrategySpec(
        key="daily_raw_7d_control",
        label="1) daily raw 7d control",
        age_days=0,
        top_liq_n=None,
        score_kind="raw_7d",
        description="控制组：不做年龄过滤，直接按过去 7d 原始收益做横截面排序，等于故意保留追妖币/追短期强者的倾向。",
    ),
    StrategySpec(
        key="age90_14d_skip1d_voladj",
        label="2) age90 14d ex1d vol-adjusted",
        age_days=90,
        top_liq_n=None,
        score_kind="voladj_14d_ex1d",
        description="先上年龄过滤，再用 14d skip-1d 动量 / 14d 波动做排名，测试“中短周期动量 + recent skip + 风险缩放”。",
    ),
    StrategySpec(
        key="age90_resid_14d_skip1d_voladj",
        label="3) age90 residual 14d ex1d vol-adjusted",
        age_days=90,
        top_liq_n=None,
        score_kind="resid_voladj_14d_ex1d",
        description="在 14d skip-1d vol-adjusted 基础上，再扣掉同期 BTC 方向暴露（beta=1 近似），先做一版轻量 residual 近似，尽量把共同 beta 和 idiosyncratic continuation 拆开。",
    ),
    StrategySpec(
        key="age90_resid_14d_skip1d_voladj_blowoffpen",
        label="4) age90 residual 14d ex1d + blowoff penalty",
        age_days=90,
        top_liq_n=None,
        score_kind="resid_voladj_14d_ex1d_blowoffpen",
        description="推荐主候选：residual + skip + vol-adjust + 末日 blowoff 惩罚，目标就是少追‘最后一天冲顶的小票’。",
    ),
    StrategySpec(
        key="age90_top12liq_resid_14d_skip1d_voladj_blowoffpen",
        label="5) age90 top12-liq residual + blowoff penalty",
        age_days=90,
        top_liq_n=12,
        score_kind="resid_voladj_14d_ex1d_blowoffpen",
        description="保守锚点：每个月只在最液态的 top12 里做 residual momentum，检验‘大币/高流动性 anchor’是否更诚实。",
    ),
]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_rebuild_module():
    spec = importlib.util.spec_from_file_location("rank213_mv_rebuild", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load module: {MODULE_PATH}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def fmt_pct(x: float | int | None, digits: int = 2) -> str:
    if x is None or pd.isna(x):
        return ""
    return f"{float(x):.{digits}f}%"


def fmt_bps(x: float | int | None, digits: int = 2) -> str:
    if x is None or pd.isna(x):
        return ""
    return f"{float(x):.{digits}f} bps"


def render_table(df: pd.DataFrame, *, pct_cols: set[str] | None = None, bps_cols: set[str] | None = None, int_cols: set[str] | None = None) -> str:
    pct_cols = pct_cols or set()
    bps_cols = bps_cols or set()
    int_cols = int_cols or set()
    if df.empty:
        return "<p class='muted'>暂无数据。</p>"
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows: list[str] = []
    for _, row in df.iterrows():
        cells: list[str] = []
        for c in df.columns:
            v = row[c]
            if pd.isna(v):
                txt = ""
            elif c in pct_cols:
                txt = fmt_pct(v)
            elif c in bps_cols:
                txt = fmt_bps(v)
            elif c in int_cols:
                txt = str(int(v))
            elif isinstance(v, (float, np.floating)):
                txt = f"{float(v):.4f}"
            else:
                txt = escape(str(v))
            cells.append(f"<td>{txt}</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def max_drawdown(ret: pd.Series) -> float:
    if ret.empty:
        return np.nan
    eq = (1.0 + ret.fillna(0.0)).cumprod()
    dd = eq / eq.cummax() - 1.0
    return float(dd.min())


def calc_stats(df: pd.DataFrame) -> dict:
    ret = pd.to_numeric(df["net_ret"], errors="coerce").fillna(0.0)
    active = pd.to_numeric(df["active"], errors="coerce").fillna(0).astype(bool)
    return {
        "days": int(len(df)),
        "active_days": int(active.sum()),
        "active_rate_pct": float(active.mean() * 100.0) if len(df) else np.nan,
        "net_mean_bps": float(ret.mean() * 10000.0) if len(df) else np.nan,
        "net_cum_pct": float(((1.0 + ret).prod() - 1.0) * 100.0) if len(df) else np.nan,
        "max_drawdown_pct": float(max_drawdown(ret) * 100.0) if len(df) else np.nan,
        "win_rate_pct": float((ret > 0).mean() * 100.0) if len(df) else np.nan,
        "avg_eligible_universe_size": float(pd.to_numeric(df["eligible_universe_size"], errors="coerce").mean()) if len(df) else np.nan,
    }


def zscore(s: pd.Series) -> pd.Series:
    s = pd.to_numeric(s, errors="coerce")
    std = float(s.std()) if len(s.dropna()) else np.nan
    if pd.isna(std) or std <= 0:
        return pd.Series(0.0, index=s.index)
    return (s - float(s.mean())) / std


def build_daily_panel(mod, symbols: list[str], start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    ordered = []
    seen = set()
    for sym in [*symbols, "BTCUSDT"]:
        if sym in seen:
            continue
        ordered.append(sym)
        seen.add(sym)

    series: list[pd.Series] = []
    for n, symbol in enumerate(ordered, start=1):
        df = mod.load_daily_prices(symbol, start, end)
        if df.empty:
            continue
        ser = df.set_index("timestamp")["close"].astype(float).rename(symbol)
        series.append(ser)
        if n % 25 == 0:
            print(f"[load] daily {n}/{len(ordered)} symbols")
    if not series:
        raise RuntimeError("daily panel is empty")
    panel = pd.concat(series, axis=1).sort_index()
    panel = panel[~panel.index.duplicated(keep="last")].sort_index()
    return panel


def get_series_ratio(panel: pd.DataFrame, syms: list[str], t1: pd.Timestamp, t0: pd.Timestamp) -> pd.Series | None:
    if t1 not in panel.index or t0 not in panel.index:
        return None
    a = panel.loc[t1, syms]
    b = panel.loc[t0, syms]
    return pd.to_numeric(a, errors="coerce") / pd.to_numeric(b, errors="coerce") - 1.0


def score_cross_section(panel: pd.DataFrame, ts: pd.Timestamp, syms: list[str], kind: str) -> pd.Series | None:
    if kind == "raw_7d":
        return get_series_ratio(panel, syms, ts, ts - pd.Timedelta(days=7))

    # common ingredients
    mom_14d = get_series_ratio(panel, syms, ts - pd.Timedelta(days=1), ts - pd.Timedelta(days=15))
    if mom_14d is None:
        return None
    hist = panel.loc[ts - pd.Timedelta(days=15):ts - pd.Timedelta(days=1), syms].pct_change(fill_method=None).dropna(how="all")
    vol_14d = hist.std().replace(0.0, np.nan)
    base = mom_14d / vol_14d

    if kind == "voladj_14d_ex1d":
        return base

    btc_mom_14d = get_series_ratio(panel, ["BTCUSDT"], ts - pd.Timedelta(days=1), ts - pd.Timedelta(days=15))
    if btc_mom_14d is None or btc_mom_14d.empty or pd.isna(btc_mom_14d.iloc[0]):
        return None
    btc_mom = float(btc_mom_14d.iloc[0])

    residual = mom_14d - btc_mom
    score = residual / vol_14d

    if kind == "resid_voladj_14d_ex1d":
        return score

    if kind == "resid_voladj_14d_ex1d_blowoffpen":
        one_day = get_series_ratio(panel, syms, ts, ts - pd.Timedelta(days=1))
        if one_day is None:
            return None
        penalty = zscore(one_day)
        return score - 0.50 * penalty

    raise ValueError(f"unsupported score kind: {kind}")


def backtest_daily_baseline(panel: pd.DataFrame, monthly_universe: dict[str, list[str]], onboard_map: dict[str, pd.Timestamp], spec: StrategySpec) -> pd.DataFrame:
    rows: list[dict] = []
    all_index = panel.index.sort_values()
    start = pd.Timestamp("2020-02-01T00:00:00Z")
    end = all_index.max() - pd.Timedelta(days=1)
    dates = [ts for ts in all_index if start <= ts <= end]

    for j, ts in enumerate(dates, start=1):
        if j % 250 == 0:
            print(f"[backtest] {spec.key} {j}/{len(dates)} days")
        next_ts = ts + pd.Timedelta(days=1)
        if next_ts not in panel.index:
            continue

        month = ts.strftime("%Y-%m")
        month_symbols = monthly_universe.get(month, [])
        if spec.top_liq_n is not None:
            month_symbols = month_symbols[: spec.top_liq_n]

        eligible: list[str] = []
        for sym in month_symbols:
            onboard = onboard_map.get(sym)
            if onboard is None:
                continue
            if spec.age_days > 0 and ts - onboard < pd.Timedelta(days=spec.age_days):
                continue
            if sym not in panel.columns:
                continue
            if pd.isna(panel.at[ts, sym]) or pd.isna(panel.at[next_ts, sym]):
                continue
            eligible.append(sym)

        row = {
            "timestamp_ts": ts,
            "exit_ts": next_ts,
            "month": month,
            "strategy": spec.key,
            "label": spec.label,
            "eligible_universe_size": int(len(eligible)),
        }

        if len(eligible) < TOP_N + BOTTOM_N:
            row.update({
                "longs": "",
                "shorts": "",
                "net_ret": 0.0,
                "gross_ret": 0.0,
                "active": False,
            })
            rows.append(row)
            continue

        score = score_cross_section(panel, ts, eligible, spec.score_kind)
        if score is None:
            row.update({
                "longs": "",
                "shorts": "",
                "net_ret": 0.0,
                "gross_ret": 0.0,
                "active": False,
            })
            rows.append(row)
            continue

        score = pd.to_numeric(score, errors="coerce").dropna()
        future = pd.to_numeric(panel.loc[next_ts, score.index], errors="coerce") / pd.to_numeric(panel.loc[ts, score.index], errors="coerce") - 1.0
        valid = future.dropna().index.intersection(score.dropna().index)
        score = score.reindex(valid).dropna()
        future = future.reindex(score.index).dropna()
        score = score.reindex(future.index)
        if len(score) < TOP_N + BOTTOM_N:
            row.update({
                "longs": "",
                "shorts": "",
                "net_ret": 0.0,
                "gross_ret": 0.0,
                "active": False,
            })
            rows.append(row)
            continue

        rank = score.sort_values()
        longs = rank.index[-TOP_N:].tolist()[::-1]
        shorts = rank.index[:BOTTOM_N].tolist()
        gross = 0.5 * float(future[longs].mean()) + 0.5 * float((-future[shorts]).mean())
        net = gross - ROUND_COST
        row.update({
            "longs": ",".join(longs),
            "shorts": ",".join(shorts),
            "gross_ret": float(gross),
            "net_ret": float(net),
            "active": True,
        })
        rows.append(row)

    return pd.DataFrame(rows)


def build_report(overall: pd.DataFrame, annual: pd.DataFrame, incumbent_ref: dict, sample: dict, spec_payload: dict) -> str:
    spec_items = []
    for item in spec_payload["candidate_baselines"]:
        spec_items.append(
            f"<li><b>{escape(item['label'])}</b>：{escape(item['description'])}"
            f"<br><span class='muted'>age_days={item['age_days']}, top_liq_n={item['top_liq_n']}, score_kind={escape(item['score_kind'])}</span></li>"
        )

    incumbent_line = (
        f"plain baseline（原 rank213 15m 参考线）：mean {fmt_bps(incumbent_ref['net_mean_bps'])}, "
        f"cum {fmt_pct(incumbent_ref['net_cum_pct'])}, DD {fmt_pct(incumbent_ref['max_drawdown_pct'])}, "
        f"active {fmt_pct(incumbent_ref['open_rate_pct'])}"
    )

    html = f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank213 monthly-volume baseline refresh</title>
  <style>
    body {{ font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width: 1240px; margin: 32px auto; padding: 0 18px; line-height: 1.62; color:#111827; background:#f8fafc; }}
    .card {{ background:white; border:1px solid #e5e7eb; border-radius:16px; padding:18px 20px; margin:16px 0; box-shadow:0 1px 2px rgba(15,23,42,0.03); }}
    .muted {{ color:#64748b; }}
    .warn {{ color:#92400e; background:#fffbeb; border:1px solid #fde68a; border-radius:12px; padding:12px 14px; }}
    .good {{ color:#166534; background:#f0fdf4; border:1px solid #bbf7d0; border-radius:12px; padding:12px 14px; }}
    .pill {{ display:inline-block; padding:4px 10px; margin:2px 4px 2px 0; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; }}
    .table-wrap {{ overflow-x:auto; margin:12px 0; }}
    table {{ border-collapse: collapse; min-width: 980px; width: 100%; background:white; }}
    th,td {{ border:1px solid #e5e7eb; padding:7px 9px; text-align:right; white-space:nowrap; font-size:13px; }}
    th {{ background:#f1f5f9; color:#334155; position:sticky; top:0; z-index:1; }}
    td:first-child, th:first-child, td:nth-child(2), th:nth-child(2) {{ text-align:left; }}
    code {{ background:#f1f5f9; border-radius:6px; padding:2px 5px; }}
  </style>
</head>
<body>
  <div class='card'>
    <h1>Rank213 monthly-volume baseline refresh</h1>
    <p class='muted'>目的不是继续给旧 veto/gate 打补丁，而是先测试：在相同 <b>monthly volume causal universe</b> 框架下，换一个更适合 crypto 的 baseline 母体，是否比当前 plain baseline 更诚实。</p>
    <p>
      <span class='pill'>sample {escape(sample['start_utc'])} → {escape(sample['end_utc'])}</span>
      <span class='pill'>daily rebalance / next-day hold</span>
      <span class='pill'>top3 / bottom3</span>
      <span class='pill'>one-way cost {ONE_WAY_COST_BPS:.1f} bps</span>
    </p>
    <div class='warn'><b>口径提醒：</b>本页是 <b>baseline refresh 第一轮快筛</b>，执行层改成了 daily rebalance / next-day hold，目的是更贴近“几天内拉升/回落”的 crypto 横截面现实；它不是对原 15m rank213 的 apples-to-apples 替代，而是“新母体候选”的 first falsification。</div>
  </div>

  <div class='card'>
    <h2>原 15m 参考线（只作上下文）</h2>
    <p>{escape(incumbent_line)}</p>
    <p class='muted'>这条线来自现有 <code>rank213_monthly_volume_universe_rebuild_summary.json</code>，只是提醒为什么要先换 baseline：旧母体自己已经跨窗失稳。</p>
  </div>

  <div class='card'>
    <h2>本轮 baseline spec</h2>
    <ul>{''.join(spec_items)}</ul>
  </div>

  <div class='card'>
    <h2>全样本总表</h2>
    <div class='table-wrap'>{render_table(overall, pct_cols={'active_rate_pct','net_cum_pct','max_drawdown_pct','win_rate_pct'}, bps_cols={'net_mean_bps'}, int_cols={'days','active_days'})}</div>
  </div>

  <div class='card'>
    <h2>按年切</h2>
    <div class='table-wrap'>{render_table(annual, pct_cols={'active_rate_pct','net_cum_pct','max_drawdown_pct','win_rate_pct'}, bps_cols={'net_mean_bps'}, int_cols={'days','active_days'})}</div>
  </div>
</body>
</html>
"""
    return html


def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_PATH.parent)

    mod = load_rebuild_module()
    if CANDIDATE_PATH.exists():
        candidates = pd.read_csv(CANDIDATE_PATH)
    else:
        candidates = mod.build_candidates()
    monthly_df = pd.read_csv(MONTHLY_UNIVERSE_PATH)
    incumbent_summary = json.loads(INCUMBENT_SUMMARY_PATH.read_text(encoding="utf-8"))

    sample_start = pd.Timestamp("2020-02-01T00:00:00Z")
    sample_end = pd.to_datetime(incumbent_summary["sample"]["end_utc"], utc=True).normalize()
    monthly_universe = {
        row["month"]: [s for s in str(row["selected_symbols"]).split(",") if s]
        for _, row in monthly_df.iterrows()
    }
    union_symbols = sorted({s for syms in monthly_universe.values() for s in syms})
    onboard_map = {
        str(row["symbol"]): pd.to_datetime(int(row["onboard_ms"]), unit="ms", utc=True)
        for _, row in candidates.iterrows()
    }

    print(f"[info] union symbols={len(union_symbols)}")
    panel = build_daily_panel(mod, union_symbols, sample_start - pd.Timedelta(days=45), sample_end + pd.Timedelta(days=3))
    print(f"[info] panel rows={len(panel)} cols={len(panel.columns)}")

    details: list[pd.DataFrame] = []
    overall_rows: list[dict] = []
    annual_rows: list[dict] = []

    for spec in SPECS:
        print(f"[run] {spec.key}")
        detail = backtest_daily_baseline(panel, monthly_universe, onboard_map, spec)
        if detail.empty:
            continue
        details.append(detail)
        stats = calc_stats(detail)
        overall_rows.append({
            "strategy": spec.key,
            "label": spec.label,
            **stats,
        })
        for year, sub in detail.groupby(detail["timestamp_ts"].dt.year):
            annual_rows.append({
                "segment": str(int(year)),
                "strategy": spec.key,
                "label": spec.label,
                **calc_stats(sub),
            })

    if not details:
        raise RuntimeError("baseline refresh returned empty detail")

    detail_all = pd.concat(details, ignore_index=True)
    overall = pd.DataFrame(overall_rows).sort_values("net_mean_bps", ascending=False).reset_index(drop=True)
    annual = pd.DataFrame(annual_rows).sort_values(["segment", "net_mean_bps"], ascending=[True, False]).reset_index(drop=True)

    incumbent_ref = incumbent_summary["metrics"]["monthly_volume_rebuild"]["plain"]
    incumbent_ref["open_rate_pct"] = 100.0
    spec_payload = {
        "objective": "refresh rank213 baseline candidates under monthly volume causal universe",
        "sample": {
            "start_utc": sample_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end_utc": sample_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "execution": {
            "rebalance": "daily",
            "holding": "next_day_close_to_close",
            "top_n": TOP_N,
            "bottom_n": BOTTOM_N,
            "one_way_cost_bps": ONE_WAY_COST_BPS,
        },
        "candidate_baselines": [
            {
                "key": s.key,
                "label": s.label,
                "age_days": s.age_days,
                "top_liq_n": s.top_liq_n,
                "score_kind": s.score_kind,
                "description": s.description,
            }
            for s in SPECS
        ],
        "incumbent_reference": incumbent_ref,
    }

    detail_all.to_csv(DAILY_PATH, index=False)
    overall.to_csv(OVERALL_PATH, index=False)
    annual.to_csv(ANNUAL_PATH, index=False)
    SPEC_PATH.write_text(json.dumps(spec_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = {
        "generated_at_utc": pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ"),
        **spec_payload,
        "overall_best_by_mean": overall.iloc[0].to_dict() if not overall.empty else {},
        "overall_table_rows": int(len(overall)),
        "annual_table_rows": int(len(annual)),
        "artifacts": {
            "daily": str(DAILY_PATH.relative_to(ROOT)),
            "overall": str(OVERALL_PATH.relative_to(ROOT)),
            "annual": str(ANNUAL_PATH.relative_to(ROOT)),
            "spec": str(SPEC_PATH.relative_to(ROOT)),
            "site": str(SITE_PATH.relative_to(ROOT)),
        },
    }
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    page = build_report(overall, annual, incumbent_ref, spec_payload["sample"], spec_payload)
    SITE_PATH.write_text(page, encoding="utf-8")

    print(f"[ok] wrote {SUMMARY_PATH}")
    print(f"[ok] wrote {SPEC_PATH}")
    print(f"[ok] wrote {OVERALL_PATH}")
    print(f"[ok] wrote {ANNUAL_PATH}")
    print(f"[ok] wrote {DAILY_PATH}")
    print(f"[ok] wrote {SITE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
