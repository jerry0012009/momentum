#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import math
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "rank32b_timecycle"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "rank32b_timecycle"
IMG_DIR = SITE_DIR / "images"
QMOD_PATH = ROOT / "scripts" / "build_rank32b_regime_5y_quarterly.py"

DEFAULT_DAYS = 365 * 5 + 5
PRIMARY_COST_BPS = 10.0

CORE18 = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
    "LTC-USD": "LTCUSDT",
    "NEAR-USD": "NEARUSDT",
    "UNI-USD": "UNIUSDT",
    "XRP-USD": "XRPUSDT",
    "DOGE-USD": "DOGEUSDT",
    "BNB-USD": "BNBUSDT",
    "ADA-USD": "ADAUSDT",
    "AVAX-USD": "AVAXUSDT",
    "LINK-USD": "LINKUSDT",
    "BCH-USD": "BCHUSDT",
    "DOT-USD": "DOTUSDT",
    "ZEC-USD": "ZECUSDT",
    "AAVE-USD": "AAVEUSDT",
    "SUI-USD": "SUIUSDT",
    "WLD-USD": "WLDUSDT",
}

HOT_SMALLCAP = {
    "BEAT-USD": "BEATUSDT",
    "PIPPIN-USD": "PIPPINUSDT",
    "SIREN-USD": "SIRENUSDT",
    "TRADOOR-USD": "TRADOORUSDT",
    "FARTCOIN-USD": "FARTCOINUSDT",
    "WIF-USD": "WIFUSDT",
    "PENGU-USD": "PENGUUSDT",
    "PNUT-USD": "PNUTUSDT",
    "MOODENG-USD": "MOODENGUSDT",
    "HIPPO-USD": "HIPPOUSDT",
}

BASKETS = {
    "core18": {"label": "大币 / core18", "plot_label": "core18 majors", "assets": CORE18},
    "hot_smallcap": {"label": "小币 / hot smallcap", "plot_label": "hot smallcaps", "assets": HOT_SMALLCAP},
}


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


qmod = load_module(QMOD_PATH, "rank32b_qmod_timecycle")


@dataclass
class BasketResult:
    key: str
    label: str
    quarter_df: pd.DataFrame
    rolling_4q: pd.DataFrame
    rolling_12q: pd.DataFrame
    selected_trades: pd.DataFrame
    asset_meta: pd.DataFrame
    direction_summary: pd.DataFrame
    combo_summary: pd.DataFrame


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def pct(v: float | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def num(v: float | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f}"


def render_table(df: pd.DataFrame, percent_cols: set[str] | None = None, digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return "<p class='muted'>暂无数据。</p>"
    percent_cols = percent_cols or set()
    digits_cols = digits_cols or {}
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows: list[str] = []
    for _, row in df.iterrows():
        cells: list[str] = []
        for col in df.columns:
            value = row[col]
            if col in percent_cols:
                text = pct(value)
            elif isinstance(value, (float, np.floating, int, np.integer)) and not isinstance(value, bool):
                text = num(value, digits_cols.get(col, 2))
            else:
                text = str(value)
            cells.append(f"<td>{escape(text)}</td>")
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def apply_strongest_only(trades: pd.DataFrame, max_concurrent_positions: int = 1) -> pd.DataFrame:
    if trades.empty:
        return trades.copy()
    work = trades.sort_values(["event_ts", "slope_strength", "asset"], ascending=[True, False, True]).reset_index(drop=True)
    best_idx = work.groupby("event_ts", sort=False)["slope_strength"].idxmax().tolist()
    bar_selected = work.loc[sorted(best_idx)].copy().sort_values(["event_ts", "slope_strength"], ascending=[True, False]).reset_index(drop=True)

    active_until: list[pd.Timestamp] = []
    picked_rows: list[dict[str, Any]] = []
    for _, row in bar_selected.iterrows():
        entry_ts = pd.to_datetime(row["entry_ts"], utc=True)
        active_until = [ts for ts in active_until if ts > entry_ts]
        if len(active_until) >= max_concurrent_positions:
            continue
        picked_rows.append(row.to_dict())
        active_until.append(pd.to_datetime(row["exit_ts"], utc=True))
        active_until.sort()
    return pd.DataFrame(picked_rows)


def trade_sharpe(returns: pd.Series) -> float | None:
    vals = pd.to_numeric(returns, errors="coerce").dropna()
    if len(vals) < 5:
        return None
    std = float(vals.std(ddof=0))
    if std <= 0:
        return None
    return float((vals.mean() / std) * math.sqrt(len(vals)))


def classify_breadth_bucket(v: float | None) -> str | None:
    if v is None or pd.isna(v):
        return None
    if float(v) >= 0.67:
        return "broad"
    if float(v) <= 0.33:
        return "narrow"
    return "mixed"


def enrich_quarter_regimes(qdf: pd.DataFrame) -> pd.DataFrame:
    if qdf.empty:
        return qdf.copy()
    out = qdf.copy()
    out["direction_bucket"] = out.apply(lambda r: qmod.classify_direction(r.get("eq_ret_3m"), r.get("breadth_pos")), axis=1)
    out["efficiency_bucket"] = qmod.bucketize(out["ew_efficiency"], ["choppy", "mid", "trendy"])
    out["vol_bucket"] = qmod.bucketize(out["ew_vol_ann"], ["low_vol", "mid_vol", "high_vol"])
    out["breadth_bucket"] = out["breadth_pos"].apply(classify_breadth_bucket)
    out["regime_combo"] = out["direction_bucket"].astype(str) + " | " + out["efficiency_bucket"].astype(str)
    return out


def aggregate_quarter_regimes(qdf: pd.DataFrame, by: list[str]) -> pd.DataFrame:
    if qdf.empty:
        return pd.DataFrame()
    work = qdf.dropna(subset=["quarter_return"]).copy()
    if work.empty:
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    for key, grp in work.groupby(by, dropna=False, sort=False):
        if not isinstance(key, tuple):
            key = (key,)
        row = {col: val for col, val in zip(by, key)}
        row.update({
            "windows": int(len(grp)),
            "mean_quarter_return": float(pd.to_numeric(grp["quarter_return"], errors="coerce").mean()),
            "median_quarter_return": float(pd.to_numeric(grp["quarter_return"], errors="coerce").median()),
            "positive_quarter_ratio": float((pd.to_numeric(grp["quarter_return"], errors="coerce") > 0).mean()),
            "mean_trade_sharpe": float(pd.to_numeric(grp["trade_sharpe"], errors="coerce").dropna().mean()) if pd.to_numeric(grp["trade_sharpe"], errors="coerce").notna().any() else np.nan,
            "mean_eq_ret_3m": float(pd.to_numeric(grp["eq_ret_3m"], errors="coerce").mean()),
            "mean_breadth_pos": float(pd.to_numeric(grp["breadth_pos"], errors="coerce").mean()),
            "mean_ew_efficiency": float(pd.to_numeric(grp["ew_efficiency"], errors="coerce").mean()),
            "mean_ew_vol_ann": float(pd.to_numeric(grp["ew_vol_ann"], errors="coerce").mean()),
            "mean_trades": float(pd.to_numeric(grp["trades"], errors="coerce").mean()),
        })
        rows.append(row)
    return pd.DataFrame(rows)


def build_benchmark_quarter_frame(bar_map: dict[str, pd.DataFrame]) -> pd.DataFrame:
    benchmark = qmod.build_benchmark_features(bar_map)
    benchmark["quarter"] = benchmark["timestamp"].dt.tz_convert(None).dt.to_period("Q").astype(str)
    rows: list[dict[str, Any]] = []
    for quarter, grp in benchmark.groupby("quarter", sort=True):
        start_ts = pd.to_datetime(grp["timestamp"].min(), utc=True)
        end_ts = pd.to_datetime(grp["timestamp"].max(), utc=True)
        eq_close = grp["eq_close"].dropna()
        btc_close = grp["btc_close"].dropna()
        eq_ret = float(eq_close.iloc[-1] / eq_close.iloc[0] - 1.0) if len(eq_close) >= 2 else np.nan
        btc_ret = float(btc_close.iloc[-1] / btc_close.iloc[0] - 1.0) if len(btc_close) >= 2 else np.nan
        eq_bar_ret = pd.to_numeric(grp["eq_ret"], errors="coerce").dropna()
        ew_vol_ann = float(eq_bar_ret.std(ddof=0) * math.sqrt(365 * 24 * 4)) if len(eq_bar_ret) >= 2 else np.nan
        ew_efficiency = float(abs(eq_ret) / eq_bar_ret.abs().sum()) if len(eq_bar_ret) >= 2 and eq_bar_ret.abs().sum() > 0 else np.nan
        asset_rets = []
        listed_assets = 0
        for _, bars in bar_map.items():
            sub = bars[(bars["timestamp"] >= start_ts) & (bars["timestamp"] <= end_ts)]
            if len(sub) >= 2:
                listed_assets += 1
                asset_rets.append(float(sub.iloc[-1]["close"] / sub.iloc[0]["close"] - 1.0))
        breadth = float(np.mean(np.array(asset_rets) > 0)) if asset_rets else np.nan
        rows.append({
            "quarter": quarter,
            "quarter_start": start_ts,
            "quarter_end": end_ts,
            "eq_ret_3m": eq_ret,
            "btc_ret_3m": btc_ret,
            "breadth_pos": breadth,
            "listed_asset_count": listed_assets,
            "ew_vol_ann": ew_vol_ann,
            "ew_efficiency": ew_efficiency,
        })
    return pd.DataFrame(rows).sort_values("quarter_start").reset_index(drop=True)


def build_quarter_summary(selected: pd.DataFrame, bar_map: dict[str, pd.DataFrame]) -> pd.DataFrame:
    bench = build_benchmark_quarter_frame(bar_map)
    if selected.empty:
        bench["trades"] = 0
        bench["quarter_return"] = np.nan
        bench["avg_trade_ret"] = np.nan
        bench["win_rate"] = np.nan
        bench["trade_sharpe"] = np.nan
        return bench
    work = selected.copy()
    work["entry_ts"] = pd.to_datetime(work["entry_ts"], utc=True)
    work["quarter"] = work["entry_ts"].dt.tz_convert(None).dt.to_period("Q").astype(str)
    rows: list[dict[str, Any]] = []
    for quarter, grp in work.groupby("quarter", sort=True):
        rows.append({
            "quarter": quarter,
            "trades": int(len(grp)),
            "quarter_return": float((1.0 + grp["net_ret"]).prod() - 1.0),
            "avg_trade_ret": float(grp["net_ret"].mean()),
            "win_rate": float((grp["net_ret"] > 0).mean()),
            "trade_sharpe": trade_sharpe(grp["net_ret"]),
        })
    qdf = bench.merge(pd.DataFrame(rows), on="quarter", how="left")
    qdf["trades"] = qdf["trades"].fillna(0).astype(int)
    qdf = qdf.sort_values("quarter_start").reset_index(drop=True)
    return enrich_quarter_regimes(qdf)


def build_rolling_windows(qdf: pd.DataFrame, window_quarters: int) -> pd.DataFrame:
    if qdf.empty:
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    work = qdf.sort_values("quarter_start").reset_index(drop=True)
    for end_idx in range(window_quarters - 1, len(work)):
        part = work.iloc[end_idx - window_quarters + 1 : end_idx + 1].copy()
        if part["quarter_return"].notna().sum() < window_quarters:
            continue
        qrets = pd.to_numeric(part["quarter_return"], errors="coerce")
        total_return = float((1.0 + qrets).prod() - 1.0)
        std = float(qrets.std(ddof=0))
        sharpe = float((qrets.mean() / std) * math.sqrt(4)) if std > 0 else np.nan
        rows.append({
            "window_quarters": window_quarters,
            "window_start": part.iloc[0]["quarter"],
            "window_end": part.iloc[-1]["quarter"],
            "window_return": total_return,
            "window_sharpe_q": sharpe,
            "positive_quarter_ratio": float((qrets > 0).mean()),
            "avg_eq_ret_3m": float(pd.to_numeric(part["eq_ret_3m"], errors="coerce").mean()),
            "avg_breadth_pos": float(pd.to_numeric(part["breadth_pos"], errors="coerce").mean()),
            "avg_ew_efficiency": float(pd.to_numeric(part["ew_efficiency"], errors="coerce").mean()),
            "avg_ew_vol_ann": float(pd.to_numeric(part["ew_vol_ann"], errors="coerce").mean()),
            "avg_trades_per_quarter": float(pd.to_numeric(part["trades"], errors="coerce").mean()),
        })
    return pd.DataFrame(rows)


def plot_basket(key: str, label: str, plot_label: str, qdf: pd.DataFrame, r4: pd.DataFrame, r12: pd.DataFrame) -> dict[str, str]:
    ensure_dir(IMG_DIR)
    out: dict[str, str] = {}

    fig, ax1 = plt.subplots(figsize=(11, 4.8))
    colors = ["#16a34a" if (pd.notna(v) and v >= 0) else "#dc2626" for v in qdf["quarter_return"]]
    ax1.bar(qdf["quarter"], qdf["quarter_return"] * 100.0, color=colors, alpha=0.75)
    ax1.axhline(0.0, color="#64748b", linestyle="--", linewidth=1)
    ax1.set_title(f"{plot_label}: quarterly strategy return")
    ax1.set_ylabel("Quarter return %")
    ax1.tick_params(axis="x", rotation=60)
    ax1.grid(True, axis="y", alpha=0.25)
    fig.tight_layout()
    name1 = f"{key}_quarter_returns.png"
    fig.savefig(IMG_DIR / name1, dpi=150)
    plt.close(fig)
    out["quarter_returns"] = name1

    if not r4.empty or not r12.empty:
        fig, ax = plt.subplots(figsize=(11, 4.8))
        if not r4.empty:
            ax.plot(r4["window_end"], r4["window_return"] * 100.0, marker="o", label="Rolling 1Y return (4Q)", color="#2563eb")
        if not r12.empty:
            ax.plot(r12["window_end"], r12["window_return"] * 100.0, marker="o", label="Rolling 3Y return (12Q)", color="#7c3aed")
        ax.axhline(0.0, color="#64748b", linestyle="--", linewidth=1)
        ax.set_title(f"{plot_label}: rolling 1Y / 3Y strategy return")
        ax.set_ylabel("Rolling return %")
        ax.tick_params(axis="x", rotation=60)
        ax.grid(True, alpha=0.25)
        ax.legend()
        fig.tight_layout()
        name2 = f"{key}_rolling_returns.png"
        fig.savefig(IMG_DIR / name2, dpi=150)
        plt.close(fig)
        out["rolling_returns"] = name2

        fig, ax = plt.subplots(figsize=(11, 4.8))
        if not r4.empty:
            ax.plot(r4["window_end"], r4["window_sharpe_q"], marker="o", label="Rolling 1Y Sharpe", color="#0f766e")
        if not r12.empty:
            ax.plot(r12["window_end"], r12["window_sharpe_q"], marker="o", label="Rolling 3Y Sharpe", color="#b45309")
        ax.axhline(0.0, color="#64748b", linestyle="--", linewidth=1)
        ax.set_title(f"{plot_label}: rolling 1Y / 3Y Sharpe (quarterly returns)")
        ax.set_ylabel("Sharpe")
        ax.tick_params(axis="x", rotation=60)
        ax.grid(True, alpha=0.25)
        ax.legend()
        fig.tight_layout()
        name3 = f"{key}_rolling_sharpe.png"
        fig.savefig(IMG_DIR / name3, dpi=150)
        plt.close(fig)
        out["rolling_sharpe"] = name3
    return out


def top_bottom(df: pd.DataFrame, sort_col: str, top_n: int = 3) -> tuple[pd.DataFrame, pd.DataFrame]:
    if df.empty or sort_col not in df.columns:
        return pd.DataFrame(), pd.DataFrame()
    work = df.dropna(subset=[sort_col]).copy()
    if work.empty:
        return pd.DataFrame(), pd.DataFrame()
    top = work.sort_values(sort_col, ascending=False).head(top_n).reset_index(drop=True)
    bottom = work.sort_values(sort_col, ascending=True).head(top_n).reset_index(drop=True)
    return top, bottom


def analyze_basket(key: str, label: str, assets: dict[str, str], days: int, refresh: bool = False) -> BasketResult:
    basket_dir = ensure_dir(ART_DIR / key)
    bar_map: dict[str, pd.DataFrame] = {}
    trade_frames: list[pd.DataFrame] = []
    meta_rows: list[dict[str, Any]] = []

    for i, (asset, symbol) in enumerate(assets.items(), start=1):
        print(f"[{key}] {i}/{len(assets)} {asset} {symbol}", flush=True)
        bars = qmod.load_or_fetch_15m(symbol, days=days, refresh=refresh)
        if bars.empty or len(bars) < 500:
            meta_rows.append({"asset": asset, "symbol": symbol, "status": "empty", "bars": int(len(bars))})
            continue
        frame = qmod.build_frame_from_bars(asset, bars)
        trades = qmod.build_trades(frame, asset=asset, cost_bps=PRIMARY_COST_BPS)
        bar_map[asset] = bars
        meta_rows.append({
            "asset": asset,
            "symbol": symbol,
            "status": "ok",
            "bars": int(len(bars)),
            "start": pd.to_datetime(bars["timestamp"].min(), utc=True).strftime("%Y-%m-%d"),
            "end": pd.to_datetime(bars["timestamp"].max(), utc=True).strftime("%Y-%m-%d"),
            "trades": int(len(trades)),
        })
        if not trades.empty:
            trade_frames.append(trades)

    all_trades = pd.concat(trade_frames, ignore_index=True) if trade_frames else pd.DataFrame(columns=["asset","event_ts","entry_ts","exit_ts","net_ret","slope_strength"])
    selected = apply_strongest_only(all_trades, max_concurrent_positions=1)
    qdf = build_quarter_summary(selected, bar_map)
    r4 = build_rolling_windows(qdf, 4)
    r12 = build_rolling_windows(qdf, 12)
    direction_summary = aggregate_quarter_regimes(qdf, ["direction_bucket"])
    combo_summary = aggregate_quarter_regimes(qdf, ["direction_bucket", "efficiency_bucket"])

    pd.DataFrame(meta_rows).to_csv(basket_dir / "asset_meta.csv", index=False)
    selected.to_csv(basket_dir / "selected_trades.csv", index=False)
    qdf.to_csv(basket_dir / "quarter_summary.csv", index=False)
    r4.to_csv(basket_dir / "rolling_1y.csv", index=False)
    r12.to_csv(basket_dir / "rolling_3y.csv", index=False)
    direction_summary.to_csv(basket_dir / "direction_summary.csv", index=False)
    combo_summary.to_csv(basket_dir / "regime_combo_summary.csv", index=False)

    return BasketResult(
        key=key,
        label=label,
        quarter_df=qdf,
        rolling_4q=r4,
        rolling_12q=r12,
        selected_trades=selected,
        asset_meta=pd.DataFrame(meta_rows),
        direction_summary=direction_summary,
        combo_summary=combo_summary,
    )


def build_html(results: list[BasketResult], generated_at: str, days: int) -> str:
    sections: list[str] = []
    lead_bits: list[str] = []
    for res in results:
        q_top, q_bottom = top_bottom(res.quarter_df, "quarter_return", 3)
        r4_top, r4_bottom = top_bottom(res.rolling_4q, "window_sharpe_q", 3)
        r12_top, r12_bottom = top_bottom(res.rolling_12q, "window_sharpe_q", 3)
        regime_top, regime_bottom = top_bottom(res.combo_summary, "mean_trade_sharpe", 2)
        plot_label = BASKETS.get(res.key, {}).get("plot_label", res.key)
        images = plot_basket(res.key, res.label, plot_label, res.quarter_df, res.rolling_4q, res.rolling_12q)
        qdf_view = res.quarter_df.copy()
        if not qdf_view.empty:
            qdf_view["quarter_start"] = pd.to_datetime(qdf_view["quarter_start"], utc=True).dt.strftime("%Y-%m-%d")
            qdf_view["quarter_end"] = pd.to_datetime(qdf_view["quarter_end"], utc=True).dt.strftime("%Y-%m-%d")
        asset_meta_view = res.asset_meta.copy()

        quarter_best = q_top.iloc[0] if not q_top.empty else None
        quarter_worst = q_bottom.iloc[0] if not q_bottom.empty else None
        regime_best = regime_top.iloc[0] if not regime_top.empty else None
        regime_worst = regime_bottom.iloc[0] if not regime_bottom.empty else None
        lead_bits.append(
            f"<li><b>{escape(res.label)}</b>：最好季度 {escape(str(quarter_best['quarter'])) if quarter_best is not None else '-'}（{pct(quarter_best['quarter_return']) if quarter_best is not None else '-'}），最差季度 {escape(str(quarter_worst['quarter'])) if quarter_worst is not None else '-'}（{pct(quarter_worst['quarter_return']) if quarter_worst is not None else '-'}）；按 regime 看，较优状态更像 <code>{escape(str(regime_best['direction_bucket'])) if regime_best is not None else '-'}</code> + <code>{escape(str(regime_best['efficiency_bucket'])) if regime_best is not None else '-'}</code>，较差状态更像 <code>{escape(str(regime_worst['direction_bucket'])) if regime_worst is not None else '-'}</code> + <code>{escape(str(regime_worst['efficiency_bucket'])) if regime_worst is not None else '-'}</code>。</li>"
        )

        one_year_note = ""
        if res.rolling_4q.empty:
            one_year_note = "<p class='muted'>这个篮子目前连完整的 4 个季度都不够，所以还给不出稳定的 rolling 1Y 结论。</p>"
        three_year_note = ""
        if res.rolling_12q.empty:
            three_year_note = "<p class='muted'>这个篮子目前没有足够长的连续上市历史，因此 rolling 3Y 只能对更老的篮子（如 core18）认真看；小币这边要接受“上市太晚，3 年结论天然缺样本”的现实。</p>"

        sections.append(
            f"""
            <section class='card'>
              <h2>{escape(res.label)}</h2>
              <p>这部分回答两个问题：<b>什么时候做它更舒服？什么时候明显更难做？</b> 口径是 <code>official-close → next-bar open → hold 8×15m → strongest-only per bar → max_concurrent=1</code>，先看 alpha 骨架的长期周期性，不掺 recent live 的微观执行噪音。</p>
              <div class='grid2'>
                <div><img src='images/{images.get('quarter_returns','')}' alt='{escape(res.label)} quarterly returns'></div>
                <div>
                  <img src='images/{images.get('rolling_returns','')}' alt='{escape(res.label)} rolling returns'>
                  {'' if 'rolling_sharpe' not in images else f"<img src='images/{images.get('rolling_sharpe','')}' alt='{escape(res.label)} rolling sharpe'>"}
                </div>
              </div>
              <h3>最好 / 最差窗口</h3>
              <div class='grid2'>
                <div>
                  <h4>按季度收益</h4>
                  {render_table(q_top[['quarter','quarter_return','trade_sharpe','eq_ret_3m','breadth_pos','trades']], percent_cols={'quarter_return','eq_ret_3m','breadth_pos'}, digits_cols={'trades':0,'trade_sharpe':3})}
                  {render_table(q_bottom[['quarter','quarter_return','trade_sharpe','eq_ret_3m','breadth_pos','trades']], percent_cols={'quarter_return','eq_ret_3m','breadth_pos'}, digits_cols={'trades':0,'trade_sharpe':3})}
                </div>
                <div>
                  <h4>按 rolling 1Y / 3Y Sharpe</h4>
                  {one_year_note if one_year_note else render_table(r4_top[['window_start','window_end','window_return','window_sharpe_q','positive_quarter_ratio','avg_eq_ret_3m','avg_breadth_pos','avg_ew_efficiency']], percent_cols={'window_return','positive_quarter_ratio','avg_eq_ret_3m','avg_breadth_pos'}, digits_cols={'window_sharpe_q':3,'avg_ew_efficiency':3}) + render_table(r4_bottom[['window_start','window_end','window_return','window_sharpe_q','positive_quarter_ratio','avg_eq_ret_3m','avg_breadth_pos','avg_ew_efficiency']], percent_cols={'window_return','positive_quarter_ratio','avg_eq_ret_3m','avg_breadth_pos'}, digits_cols={'window_sharpe_q':3,'avg_ew_efficiency':3})}
                  {three_year_note if three_year_note else render_table(r12_top[['window_start','window_end','window_return','window_sharpe_q','positive_quarter_ratio','avg_eq_ret_3m','avg_breadth_pos','avg_ew_efficiency']], percent_cols={'window_return','positive_quarter_ratio','avg_eq_ret_3m','avg_breadth_pos'}, digits_cols={'window_sharpe_q':3,'avg_ew_efficiency':3}) + render_table(r12_bottom[['window_start','window_end','window_return','window_sharpe_q','positive_quarter_ratio','avg_eq_ret_3m','avg_breadth_pos','avg_ew_efficiency']], percent_cols={'window_return','positive_quarter_ratio','avg_eq_ret_3m','avg_breadth_pos'}, digits_cols={'window_sharpe_q':3,'avg_ew_efficiency':3})}
                </div>
              </div>
              <h3>按 regime 汇总：什么时候更适合开</h3>
              {render_table(res.direction_summary[['direction_bucket','windows','mean_quarter_return','mean_trade_sharpe','mean_eq_ret_3m','mean_breadth_pos','mean_ew_efficiency','mean_trades']], percent_cols={'mean_quarter_return','mean_eq_ret_3m','mean_breadth_pos'}, digits_cols={'windows':0,'mean_trade_sharpe':3,'mean_ew_efficiency':3,'mean_trades':1})}
              {render_table(res.combo_summary[['direction_bucket','efficiency_bucket','windows','mean_quarter_return','mean_trade_sharpe','mean_eq_ret_3m','mean_breadth_pos','mean_ew_efficiency','mean_trades']], percent_cols={'mean_quarter_return','mean_eq_ret_3m','mean_breadth_pos'}, digits_cols={'windows':0,'mean_trade_sharpe':3,'mean_ew_efficiency':3,'mean_trades':1})}
              <h3>季度明细</h3>
              {render_table(qdf_view[['quarter','quarter_start','quarter_end','listed_asset_count','trades','quarter_return','trade_sharpe','eq_ret_3m','breadth_pos','ew_efficiency','direction_bucket','efficiency_bucket','vol_bucket']], percent_cols={'quarter_return','eq_ret_3m','breadth_pos'}, digits_cols={'listed_asset_count':0,'trades':0,'trade_sharpe':3,'ew_efficiency':3})}
              <h3>成分币历史覆盖</h3>
              {render_table(asset_meta_view[['asset','symbol','status','bars','start','end','trades']], digits_cols={'bars':0,'trades':0})}
            </section>
            """
        )

    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>Rank32b 时间周期研究</title>
  <style>
    body {{ font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; margin:0; background:#f8fafc; color:#0f172a; }}
    .wrap {{ max-width: 1240px; margin: 0 auto; padding: 24px; }}
    .card {{ background:#fff; border-radius:16px; padding:18px; box-shadow:0 1px 3px rgba(0,0,0,.08); margin-bottom:18px; }}
    .muted {{ color:#64748b; }}
    table {{ width:100%; border-collapse:collapse; font-size:14px; margin-top:10px; }}
    th,td {{ border-bottom:1px solid #e2e8f0; padding:8px 10px; text-align:left; vertical-align:top; }}
    th {{ background:#f8fafc; }}
    code {{ background:#e2e8f0; padding:2px 6px; border-radius:6px; }}
    .grid2 {{ display:grid; grid-template-columns:1fr; gap:16px; }}
    .grid2 img {{ width:100%; border:1px solid #e2e8f0; border-radius:12px; background:white; }}
    @media (min-width: 980px) {{ .grid2 {{ grid-template-columns: 1.1fr 1fr; }} }}
  </style>
</head>
<body>
  <div class='wrap'>
    <h1>Rank32b · 时间周期研究（大币 vs 小币）</h1>
    <p class='muted'>生成时间：{escape(generated_at)} ｜ 历史抓取上限：{days} 天 ｜ 目标：回答“这个策略在什么市场时间段更有盈利空间 / 更高 Sharpe，什么时间段明显更差”。</p>

    <section class='card'>
      <h2>这次口径为什么比 recent live/shadow 更有意义</h2>
      <ul>
        <li>你说得对：最近实盘 / shadow 样本太短，拿它直接做“策略本体”判断，信息密度不够。</li>
        <li>所以这里故意退一步，先看 <b>长历史、统一执行骨架</b>：<code>official close → next bar open → fixed hold 8 bars</code>，然后在篮子内做 <b>strongest-only</b> 选择。</li>
        <li>这页的重点不是解释最近一两天，而是回答：<b>32b 更像在哪些季度 / 哪些滚动 1 年 / 哪些滚动 3 年里有 edge。</b></li>
        <li><b>别拿这里的绝对收益倍数当实盘宣传词。</b> 这页更适合看相对高低、Sharpe 排名、以及什么市场窗口更友好/更恶劣。</li>
      </ul>
    </section>

    <section class='card'>
      <h2>先讲一句人话</h2>
      <ul>
        {''.join(lead_bits)}
      </ul>
      <p>看法上我会这样切：<b>大币篮子更适合看 rolling 3Y</b>，因为上市历史长；<b>小币篮子更适合看最近 1Y / since-listing 的季度面板</b>，因为很多币根本没资格给你 3 年样本。</p>
    </section>

    {''.join(sections)}
  </div>
</body>
</html>
"""


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Build rank32b timecycle report")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()

    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(IMG_DIR)

    results: list[BasketResult] = []
    meta: dict[str, Any] = {
        "generated_at_utc": pd.Timestamp.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "days": args.days,
        "primary_cost_bps": PRIMARY_COST_BPS,
        "baskets": {},
    }

    for key, cfg in BASKETS.items():
        res = analyze_basket(key, cfg["label"], cfg["assets"], days=args.days, refresh=args.refresh)
        results.append(res)
        meta["baskets"][key] = {
            "label": cfg["label"],
            "selected_trades": int(len(res.selected_trades)),
            "quarters": int(len(res.quarter_df)),
            "rolling_1y_windows": int(len(res.rolling_4q)),
            "rolling_3y_windows": int(len(res.rolling_12q)),
        }

    html = build_html(results, pd.Timestamp.utcnow().strftime("%Y-%m-%d %H:%M UTC"), args.days)
    (SITE_DIR / "report.html").write_text(html, encoding="utf-8")
    (ART_DIR / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
