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
from matplotlib import font_manager
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "rank32b_symbol_regime_focus"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "rank32b_symbol_regime_focus"
IMG_DIR = SITE_DIR / "images"
LIVE_PATH = ROOT / "scripts" / "build_rank32b_live_parity_universe.py"
QMOD_PATH = ROOT / "scripts" / "build_rank32b_regime_5y_quarterly.py"
FONT_PATH = ROOT.parent / "assets" / "fonts" / "NotoSansCJKsc-Regular.otf"

DAYS = 365 * 3
REGIME_WINDOW_DAYS = 20
TARGETS = {
    "SOLUSDT": "SOL-USD",
    "BEATUSDT": "BEAT-USD",
    "PIPPINUSDT": "PIPPIN-USD",
}

REGIME_COLORS = {
    "bull|trendy": "#16a34a",
    "bull|mid": "#65a30d",
    "bull|choppy": "#84cc16",
    "bear|trendy": "#2563eb",
    "bear|mid": "#1d4ed8",
    "bear|choppy": "#dc2626",
    "flat_mixed|trendy": "#7c3aed",
    "flat_mixed|mid": "#64748b",
    "flat_mixed|choppy": "#f59e0b",
}
REGIME_CN = {
    "bull|trendy": "绿色：上涨且顺滑（更适合）",
    "bull|mid": "浅绿：上涨但一般顺",
    "bull|choppy": "黄绿：上涨但比较抖",
    "bear|trendy": "蓝色：下跌但顺滑",
    "bear|mid": "深蓝：下跌但一般顺",
    "bear|choppy": "红色：下跌且乱（更差）",
    "flat_mixed|trendy": "紫色：震荡里有段落性趋势",
    "flat_mixed|mid": "灰色：中性混合",
    "flat_mixed|choppy": "橙色：震荡且乱",
}
REGIME_SHORT = {
    "bull|trendy": "bull/trendy",
    "bull|mid": "bull/mid",
    "bull|choppy": "bull/choppy",
    "bear|trendy": "bear/trendy",
    "bear|mid": "bear/mid",
    "bear|choppy": "bear/choppy",
    "flat_mixed|trendy": "flat/trendy",
    "flat_mixed|mid": "flat/mid",
    "flat_mixed|choppy": "flat/choppy",
}


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


live_mod = load_module(LIVE_PATH, "rank32b_live_focus")
qmod = load_module(QMOD_PATH, "rank32b_qmod_focus")


def configure_matplotlib_cjk() -> None:
    if FONT_PATH.exists():
        font_manager.fontManager.addfont(str(FONT_PATH))
        prop = font_manager.FontProperties(fname=str(FONT_PATH))
        plt.rcParams["font.family"] = prop.get_name()
    plt.rcParams["axes.unicode_minus"] = False


configure_matplotlib_cjk()


@dataclass
class SymbolResult:
    symbol: str
    asset: str
    daily_regime: pd.DataFrame
    trades: pd.DataFrame
    quarter_view: pd.DataFrame
    regime_summary: pd.DataFrame
    current_state: dict[str, Any]
    images: dict[str, str]



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



def trade_sharpe(returns: pd.Series) -> float | None:
    vals = pd.to_numeric(returns, errors="coerce").dropna()
    if len(vals) < 5:
        return None
    std = float(vals.std(ddof=0))
    if std <= 0:
        return None
    return float((vals.mean() / std) * math.sqrt(len(vals)))



def mode_or_none(series: pd.Series):
    s = series.dropna()
    if s.empty:
        return None
    m = s.mode()
    return m.iloc[0] if not m.empty else s.iloc[-1]



def classify_regime_daily(bars_15m: pd.DataFrame) -> pd.DataFrame:
    daily = bars_15m[["timestamp", "close"]].copy().set_index("timestamp").resample("1D").last().dropna().reset_index()
    daily["ret_1d"] = daily["close"].pct_change()
    daily["trend_return_20d"] = daily["close"] / daily["close"].shift(REGIME_WINDOW_DAYS) - 1.0
    abs_path = daily["ret_1d"].abs().rolling(REGIME_WINDOW_DAYS, min_periods=REGIME_WINDOW_DAYS).sum()
    daily["efficiency_20d"] = daily["trend_return_20d"].abs() / abs_path.replace(0.0, np.nan)
    daily["vol_20d_ann"] = daily["ret_1d"].rolling(REGIME_WINDOW_DAYS, min_periods=REGIME_WINDOW_DAYS).std(ddof=0) * math.sqrt(365)
    daily["direction_bucket"] = np.where(
        daily["trend_return_20d"] >= 0.15,
        "bull",
        np.where(daily["trend_return_20d"] <= -0.15, "bear", "flat_mixed"),
    )
    daily["efficiency_bucket"] = qmod.bucketize(daily["efficiency_20d"], ["choppy", "mid", "trendy"])
    daily["vol_bucket"] = qmod.bucketize(daily["vol_20d_ann"], ["low_vol", "mid_vol", "high_vol"])
    daily["regime_combo"] = daily["direction_bucket"].astype(str) + "|" + daily["efficiency_bucket"].astype(str)
    daily["regime_color"] = daily["regime_combo"].map(REGIME_COLORS).fillna("#94a3b8")
    daily["regime_label_cn"] = daily["regime_combo"].map(REGIME_CN).fillna("灰色：样本不足")
    return daily



def simulate_symbol(symbol: str, asset: str, days: int) -> pd.DataFrame:
    candidate_df, _ = live_mod.simulate_candidates({asset: symbol}, days=days, tp_mult=live_mod.DEFAULT_TP, sl_mult=live_mod.DEFAULT_SL, timeout_15m=live_mod.DEFAULT_TIMEOUT_15M, refresh=False)
    selected, _ = live_mod.apply_live_selection(candidate_df, strongest_only_per_bar=True, max_concurrent_positions=1)
    if selected.empty:
        return selected
    selected = selected.copy().sort_values("entry_ts").reset_index(drop=True)
    return selected



def summarize_regime_trades(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["regime_combo","regime_label_cn","trades","total_return","avg_trade_ret","win_rate","trade_sharpe","first_trade","last_trade"])
    rows: list[dict[str, Any]] = []
    for regime_combo, grp in trades.groupby("regime_combo", sort=False):
        returns = pd.to_numeric(grp["net_ret"], errors="coerce")
        rows.append({
            "regime_combo": regime_combo,
            "regime_label_cn": REGIME_CN.get(regime_combo, regime_combo),
            "trades": int(len(grp)),
            "total_return": float((1.0 + returns).prod() - 1.0),
            "avg_trade_ret": float(returns.mean()),
            "win_rate": float((returns > 0).mean()),
            "trade_sharpe": trade_sharpe(returns),
            "first_trade": pd.to_datetime(grp["entry_ts"].min(), utc=True).strftime("%Y-%m-%d"),
            "last_trade": pd.to_datetime(grp["entry_ts"].max(), utc=True).strftime("%Y-%m-%d"),
        })
    out = pd.DataFrame(rows)
    return out.sort_values(["trade_sharpe", "avg_trade_ret"], ascending=[False, False], na_position="last").reset_index(drop=True)



def build_quarter_view(trades: pd.DataFrame, daily: pd.DataFrame) -> pd.DataFrame:
    q_daily = daily.copy()
    q_daily["quarter"] = q_daily["timestamp"].dt.tz_convert(None).dt.to_period("Q").astype(str)
    state_rows: list[dict[str, Any]] = []
    for quarter, grp in q_daily.groupby("quarter", sort=True):
        state_rows.append({
            "quarter": quarter,
            "quarter_start": pd.to_datetime(grp["timestamp"].min(), utc=True).strftime("%Y-%m-%d"),
            "quarter_end": pd.to_datetime(grp["timestamp"].max(), utc=True).strftime("%Y-%m-%d"),
            "regime_combo": mode_or_none(grp["regime_combo"]),
            "regime_label_cn": REGIME_CN.get(mode_or_none(grp["regime_combo"]), mode_or_none(grp["regime_combo"])),
            "direction_bucket": mode_or_none(grp["direction_bucket"]),
            "efficiency_bucket": mode_or_none(grp["efficiency_bucket"]),
            "avg_trend_return_20d": float(pd.to_numeric(grp["trend_return_20d"], errors="coerce").mean()),
            "avg_efficiency_20d": float(pd.to_numeric(grp["efficiency_20d"], errors="coerce").mean()),
        })
    q_state = pd.DataFrame(state_rows)
    if trades.empty:
        q_state["trades"] = 0
        q_state["quarter_return"] = np.nan
        q_state["trade_sharpe"] = np.nan
        return q_state
    work = trades.copy()
    work["quarter"] = pd.to_datetime(work["entry_ts"], utc=True).dt.tz_convert(None).dt.to_period("Q").astype(str)
    q_trades = work.groupby("quarter", sort=True).apply(
        lambda grp: pd.Series({
            "trades": int(len(grp)),
            "quarter_return": float((1.0 + pd.to_numeric(grp["net_ret"], errors="coerce")).prod() - 1.0),
            "trade_sharpe": trade_sharpe(pd.to_numeric(grp["net_ret"], errors="coerce")),
            "win_rate": float((pd.to_numeric(grp["net_ret"], errors="coerce") > 0).mean()),
        })
    ).reset_index()
    out = q_state.merge(q_trades, on="quarter", how="left")
    out["trades"] = out["trades"].fillna(0).astype(int)
    return out.sort_values("quarter_start").reset_index(drop=True)



def current_state_info(symbol: str, daily: pd.DataFrame, regime_summary: pd.DataFrame) -> dict[str, Any]:
    latest = daily.dropna(subset=["regime_combo"]).iloc[-1].to_dict()
    combo = latest.get("regime_combo")
    matched = regime_summary.loc[regime_summary["regime_combo"] == combo].copy()
    suitability = "样本不足"
    sample_trades = 0
    empirical_sharpe = None
    empirical_avg = None
    if not matched.empty:
        row = matched.iloc[0]
        sample_trades = int(row["trades"])
        empirical_sharpe = row.get("trade_sharpe")
        empirical_avg = row.get("avg_trade_ret")
        valid = regime_summary.dropna(subset=["trade_sharpe"]).copy()
        if sample_trades >= 5 and not valid.empty and pd.notna(empirical_sharpe):
            top_cut = valid["trade_sharpe"].quantile(0.67)
            low_cut = valid["trade_sharpe"].quantile(0.33)
            if float(empirical_sharpe) >= float(top_cut) and float(empirical_avg) > 0:
                suitability = "更适合 32b"
            elif float(empirical_sharpe) <= float(low_cut):
                suitability = "不太适合 32b"
            else:
                suitability = "一般 / 需要挑仓"
    return {
        "symbol": symbol,
        "as_of": pd.to_datetime(latest["timestamp"], utc=True).strftime("%Y-%m-%d"),
        "regime_combo": combo,
        "regime_label_cn": latest.get("regime_label_cn"),
        "regime_color": latest.get("regime_color"),
        "trend_return_20d": latest.get("trend_return_20d"),
        "efficiency_20d": latest.get("efficiency_20d"),
        "vol_20d_ann": latest.get("vol_20d_ann"),
        "direction_bucket": latest.get("direction_bucket"),
        "efficiency_bucket": latest.get("efficiency_bucket"),
        "vol_bucket": latest.get("vol_bucket"),
        "sample_trades": sample_trades,
        "empirical_trade_sharpe": empirical_sharpe,
        "empirical_avg_trade_ret": empirical_avg,
        "suitability": suitability,
    }



def add_regime_bands(ax, df: pd.DataFrame):
    if df.empty:
        return
    work = df[["timestamp", "regime_combo", "regime_color"]].dropna().copy().reset_index(drop=True)
    if work.empty:
        return
    start_idx = 0
    for i in range(1, len(work) + 1):
        if i == len(work) or work.iloc[i]["regime_combo"] != work.iloc[start_idx]["regime_combo"]:
            start_ts = pd.to_datetime(work.iloc[start_idx]["timestamp"], utc=True)
            end_ts = pd.to_datetime(work.iloc[i - 1]["timestamp"], utc=True) + pd.Timedelta(days=1)
            ax.axvspan(start_ts, end_ts, color=work.iloc[start_idx]["regime_color"], alpha=0.12, lw=0)
            start_idx = i



def plot_price_with_regime(symbol: str, asset: str, daily: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(11, 4.6))
    add_regime_bands(ax, daily)
    ax.plot(daily["timestamp"], daily["close"], color="#0f172a", linewidth=1.8)
    ax.set_title(f"{asset} ({symbol}) price with regime colors")
    ax.set_ylabel("Daily close")
    ax.grid(True, alpha=0.25)
    fig.autofmt_xdate()
    fig.tight_layout()
    name = f"{symbol.lower()}_price_regime.png"
    fig.savefig(IMG_DIR / name, dpi=150)
    plt.close(fig)
    return name



def plot_quarter_returns(symbol: str, asset: str, quarter_view: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(11, 4.6))
    colors = [REGIME_COLORS.get(v, "#94a3b8") for v in quarter_view["regime_combo"]]
    vals = pd.to_numeric(quarter_view["quarter_return"], errors="coerce") * 100.0
    ax.bar(quarter_view["quarter"], vals, color=colors, alpha=0.85)
    ax.axhline(0.0, color="#64748b", linestyle="--", linewidth=1)
    ax.set_title(f"{asset} ({symbol}) quarterly strategy return by regime")
    ax.set_ylabel("Quarter return %")
    ax.tick_params(axis="x", rotation=60)
    ax.grid(True, axis="y", alpha=0.25)
    fig.tight_layout()
    name = f"{symbol.lower()}_quarter_return.png"
    fig.savefig(IMG_DIR / name, dpi=150)
    plt.close(fig)
    return name



def plot_regime_sharpe(symbol: str, asset: str, regime_summary: pd.DataFrame) -> str:
    view = regime_summary.dropna(subset=["trade_sharpe"]).copy().sort_values("trade_sharpe", ascending=True)
    fig, ax = plt.subplots(figsize=(10, 4.8))
    colors = [REGIME_COLORS.get(v, "#94a3b8") for v in view["regime_combo"]]
    labels = [REGIME_SHORT.get(v, v) for v in view["regime_combo"]]
    ax.barh(labels, view["trade_sharpe"], color=colors, alpha=0.9)
    ax.axvline(0.0, color="#64748b", linestyle="--", linewidth=1)
    ax.set_title(f"{asset} ({symbol}) trade Sharpe by regime")
    ax.set_xlabel("Trade Sharpe")
    ax.grid(True, axis="x", alpha=0.25)
    fig.tight_layout()
    name = f"{symbol.lower()}_regime_sharpe.png"
    fig.savefig(IMG_DIR / name, dpi=150)
    plt.close(fig)
    return name



def build_symbol_result(symbol: str, asset: str) -> SymbolResult:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(IMG_DIR)
    bars_15m = qmod.load_or_fetch_15m(symbol, days=DAYS, refresh=False)
    daily = classify_regime_daily(bars_15m)
    trades = simulate_symbol(symbol, asset, days=DAYS)
    if not trades.empty:
        trades = pd.merge_asof(
            trades.sort_values("entry_ts"),
            daily[["timestamp", "regime_combo", "regime_label_cn", "regime_color", "direction_bucket", "efficiency_bucket", "vol_bucket", "trend_return_20d", "efficiency_20d", "vol_20d_ann"]].sort_values("timestamp"),
            left_on="entry_ts",
            right_on="timestamp",
            direction="backward",
        )
    regime_summary = summarize_regime_trades(trades)
    quarter_view = build_quarter_view(trades, daily)
    current = current_state_info(symbol, daily, regime_summary)
    images = {
        "price_regime": plot_price_with_regime(symbol, asset, daily),
        "quarter_return": plot_quarter_returns(symbol, asset, quarter_view),
        "regime_sharpe": plot_regime_sharpe(symbol, asset, regime_summary),
    }

    sym_dir = ensure_dir(ART_DIR / symbol.lower())
    daily.to_csv(sym_dir / "daily_regime.csv", index=False)
    trades.to_csv(sym_dir / "selected_trades_with_regime.csv", index=False)
    quarter_view.to_csv(sym_dir / "quarter_view.csv", index=False)
    regime_summary.to_csv(sym_dir / "regime_summary.csv", index=False)
    (sym_dir / "current_state.json").write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding="utf-8")

    return SymbolResult(symbol=symbol, asset=asset, daily_regime=daily, trades=trades, quarter_view=quarter_view, regime_summary=regime_summary, current_state=current, images=images)



def current_state_card(state: dict[str, Any]) -> str:
    color = state.get("regime_color") or "#94a3b8"
    return f"""
    <div class='state-card'>
      <div class='swatch' style='background:{escape(color)}'></div>
      <div>
        <div><b>当前颜色：</b>{escape(str(state.get('regime_label_cn') or '-'))}</div>
        <div><b>截至：</b>{escape(str(state.get('as_of') or '-'))}</div>
        <div><b>近 20 日涨跌：</b>{pct(state.get('trend_return_20d'))}</div>
        <div><b>路径效率：</b>{num(state.get('efficiency_20d'), 3)}</div>
        <div><b>20 日年化波动：</b>{pct(state.get('vol_20d_ann'))}</div>
        <div><b>经验判断：</b>{escape(str(state.get('suitability') or '-'))}</div>
        <div><b>该状态下历史样本：</b>{int(state.get('sample_trades') or 0)} 笔 ｜ <b>Sharpe：</b>{num(state.get('empirical_trade_sharpe'), 3)} ｜ <b>单笔均值：</b>{pct(state.get('empirical_avg_trade_ret'))}</div>
      </div>
    </div>
    """



def build_html(results: list[SymbolResult]) -> str:
    sections: list[str] = []
    legend = "".join(
        f"<div class='legend-item'><span class='dot' style='background:{c}'></span>{escape(REGIME_CN[k])}</div>"
        for k, c in REGIME_COLORS.items()
    )
    for res in results:
        regime_view = res.regime_summary[["regime_label_cn", "trades", "total_return", "avg_trade_ret", "win_rate", "trade_sharpe", "first_trade", "last_trade"]].copy() if not res.regime_summary.empty else pd.DataFrame()
        quarter_recent = res.quarter_view.sort_values("quarter_start", ascending=False).head(12).copy()
        sections.append(
            f"""
            <section class='card'>
              <h2>{escape(res.asset)} / {escape(res.symbol)}</h2>
              <p>这页在看三件事：<b>历史上它大多数时间是什么颜色、这些颜色下 32b 的收益/Sharpe 怎么变、现在它是什么颜色，适不适合做。</b></p>
              {current_state_card(res.current_state)}
              <div class='grid2'>
                <img src='images/{res.images['price_regime']}' alt='{escape(res.symbol)} price regime'>
                <img src='images/{res.images['quarter_return']}' alt='{escape(res.symbol)} quarter returns'>
              </div>
              <div class='grid2'>
                <img src='images/{res.images['regime_sharpe']}' alt='{escape(res.symbol)} regime sharpe'>
                <div>
                  <h3>不同状态下，32b 表现怎么变</h3>
                  {render_table(regime_view, percent_cols={'total_return','avg_trade_ret','win_rate'}, digits_cols={'trades':0,'trade_sharpe':3})}
                </div>
              </div>
              <h3>最近季度处在什么状态</h3>
              {render_table(quarter_recent[["quarter","quarter_start","quarter_end","regime_label_cn","quarter_return","trade_sharpe","avg_trend_return_20d","avg_efficiency_20d","trades"]], percent_cols={'quarter_return','avg_trend_return_20d'}, digits_cols={'trade_sharpe':3,'avg_efficiency_20d':3,'trades':0})}
            </section>
            """
        )
    generated_at = pd.Timestamp.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>Rank32b · BEAT / PIPPIN / SOL regime focus</title>
  <style>
    body {{ font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; margin:0; background:#f8fafc; color:#0f172a; }}
    .wrap {{ max-width: 1260px; margin: 0 auto; padding: 24px; }}
    .card {{ background:#fff; border-radius:16px; padding:18px; box-shadow:0 1px 3px rgba(0,0,0,.08); margin-bottom:18px; }}
    .grid2 {{ display:grid; grid-template-columns:1fr; gap:16px; margin-top:14px; }}
    .grid2 img {{ width:100%; border-radius:12px; border:1px solid #e2e8f0; background:white; }}
    table {{ width:100%; border-collapse:collapse; font-size:14px; margin-top:10px; }}
    th,td {{ border-bottom:1px solid #e2e8f0; padding:8px 10px; text-align:left; vertical-align:top; }}
    th {{ background:#f8fafc; }}
    .muted {{ color:#64748b; }}
    .legend {{ display:flex; flex-wrap:wrap; gap:10px 18px; margin-top:12px; }}
    .legend-item {{ display:flex; align-items:center; gap:8px; font-size:14px; }}
    .dot {{ width:14px; height:14px; border-radius:999px; display:inline-block; }}
    .state-card {{ display:flex; gap:14px; align-items:flex-start; border:1px solid #e2e8f0; border-radius:14px; padding:14px; background:#fcfcfd; margin-top:10px; }}
    .swatch {{ width:52px; height:52px; border-radius:12px; border:1px solid rgba(0,0,0,.08); flex:none; }}
    @media (min-width: 980px) {{ .grid2 {{ grid-template-columns: 1fr 1fr; }} }}
  </style>
</head>
<body>
  <div class='wrap'>
    <h1>Rank32b · BEAT / PIPPIN / SOL 的市场状态焦点页</h1>
    <p class='muted'>生成时间：{generated_at} ｜ 研究口径：单币 32b live-parity 骨架（TP/SL/timeout）+ 近 20 日市场状态颜色分类。</p>
    <section class='card'>
      <h2>怎么读这页</h2>
      <ul>
        <li>背景颜色不是“情绪随便染色”，而是按每个币最近 20 天的 <b>方向 + 路径效率 + 波动</b> 算出来的 regime。</li>
        <li>你可以直接看：<b>某段时间是什么颜色</b>，以及那种颜色下 32b 的 <b>收益 / 胜率 / trade Sharpe</b> 有没有明显变好或变坏。</li>
        <li>“当前颜色”卡片会告诉你：<b>现在这个币处在哪种市场环境里、历史上这种环境对 32b 友不友好。</b></li>
      </ul>
      <div class='legend'>{legend}</div>
    </section>
    {''.join(sections)}
  </div>
</body>
</html>
"""



def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(IMG_DIR)
    results: list[SymbolResult] = []
    meta: dict[str, Any] = {
        "generated_at_utc": pd.Timestamp.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "days": DAYS,
        "symbols": list(TARGETS.keys()),
    }
    for symbol, asset in TARGETS.items():
        print(f"building {symbol}", flush=True)
        res = build_symbol_result(symbol, asset)
        results.append(res)
        meta[symbol] = {
            "current_state": res.current_state,
            "trade_count": int(len(res.trades)),
            "regimes": int(len(res.regime_summary)),
        }
    (SITE_DIR / "report.html").write_text(build_html(results), encoding="utf-8")
    (ART_DIR / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
