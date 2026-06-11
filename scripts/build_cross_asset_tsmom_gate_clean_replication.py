#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_cross_asset_tsmom_gate_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_cross_asset_tsmom_gate_15m"
REPORT_PATH = SITE_DIR / "report.html"
SPEC_PATH = ART_DIR / "clean_room_spec_v1.csv"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
COSTS = [6.0, 10.0, 15.0, 20.0]
PRIMARY_COST = 6.0
PRIMARY_VARIANT = "peer_dual_gate"
PRIMARY_MOM_WINDOW = 16
VARIANTS = [
    {"variant": "baseline_sign_mom", "gate_mode": "none", "peer_windows": ()},
    {"variant": "peer_1h_gate", "gate_mode": "peer_align", "peer_windows": (4,)},
    {"variant": "peer_4h_gate", "gate_mode": "peer_align", "peer_windows": (16,)},
    {"variant": "peer_dual_gate", "gate_mode": "peer_align", "peer_windows": (4, 16)},
    {"variant": "peer_dual_strict", "gate_mode": "peer_align_strict", "peer_windows": (4, 16)},
]
PARAM_CONFIGS = [
    {"label": "m12_p416", "mom_window": 12, "peer_windows": (4, 16), "strict": False},
    {"label": "m16_p416", "mom_window": 16, "peer_windows": (4, 16), "strict": False},
    {"label": "m20_p416", "mom_window": 20, "peer_windows": (4, 16), "strict": False},
    {"label": "m16_p824", "mom_window": 16, "peer_windows": (8, 24), "strict": False},
    {"label": "m16_p416_strict", "mom_window": 16, "peer_windows": (4, 16), "strict": True},
]


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def pct(value: float | int | None, digits: int = 2) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{float(value) * 100:.{digits}f}%"


def num(value: float | int | None, digits: int = 2) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{float(value):.{digits}f}"


def render_table(df: pd.DataFrame, *, percent_cols: set[str], digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    digits_cols = digits_cols or {}
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    body = []
    for _, row in df.iterrows():
        cells = []
        for col in df.columns:
            value = row[col]
            if col in percent_cols:
                text = pct(value)
            elif isinstance(value, (float, np.floating, int, np.integer)) and not isinstance(value, bool):
                text = num(value, digits_cols.get(col, 2))
            else:
                text = str(value)
            cells.append(f"<td>{escape(text)}</td>")
        body.append(f"<tr>{''.join(cells)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def load_cached_bars(symbol: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df.sort_values("timestamp").reset_index(drop=True)


def build_base_panel(*, mom_window: int, peer_windows: tuple[int, ...]) -> pd.DataFrame:
    frames = []
    for asset, symbol in ASSETS.items():
        df = load_cached_bars(symbol).copy()
        df["asset"] = asset
        df["bar_ret"] = df["close"].pct_change().fillna(0.0)
        df["mom"] = df["close"] / df["close"].shift(mom_window) - 1.0
        frames.append(df[["timestamp", "asset", "close", "bar_ret", "mom"]])
    panel = pd.concat(frames, ignore_index=True).sort_values(["timestamp", "asset"]).reset_index(drop=True)
    peer_mean = panel.pivot(index="timestamp", columns="asset", values="bar_ret").sort_index()
    for asset in ASSETS:
        peer_cols = [c for c in peer_mean.columns if c != asset]
        peer_series = peer_mean[peer_cols].mean(axis=1)
        for window in peer_windows:
            panel.loc[panel["asset"] == asset, f"peer_ret_{window}"] = peer_series.rolling(window, min_periods=window).sum().reindex(panel.loc[panel["asset"] == asset, "timestamp"]).to_numpy()
    return panel.reset_index(drop=True)


def build_variant_positions(panel: pd.DataFrame, variant_cfg: dict) -> pd.DataFrame:
    df = panel.copy()
    desired = np.sign(df["mom"]).astype(float)
    desired = np.where(pd.isna(df["mom"]), 0.0, desired)
    gate_mode = variant_cfg["gate_mode"]
    peer_windows = variant_cfg["peer_windows"]
    if gate_mode != "none":
        aligned = np.ones(len(df), dtype=bool)
        nonzero = desired != 0.0
        for window in peer_windows:
            peer_col = f"peer_ret_{window}"
            peer_sign = np.sign(df[peer_col].fillna(0.0)).to_numpy()
            aligned &= peer_sign == np.sign(desired)
            if gate_mode == "peer_align_strict":
                aligned &= np.abs(df[peer_col].fillna(0.0).to_numpy()) > 0.0
        desired = np.where(nonzero & aligned, desired, 0.0)
    out = df.copy()
    out["variant"] = variant_cfg["variant"]
    out["desired_position"] = desired.astype(float)
    out["position"] = out.groupby("asset")["desired_position"].shift(1).fillna(0.0)
    out["turnover"] = (out["position"] - out.groupby("asset")["position"].shift(1).fillna(0.0)).abs()
    out["trade_event"] = (out["turnover"] > 1e-12).astype(int)
    out["active_bar"] = (out["position"] != 0.0).astype(int)
    return out


def simulate_variant(panel: pd.DataFrame, variant_cfg: dict, cost_bps_per_side: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = build_variant_positions(panel, variant_cfg)
    cost_rate = float(cost_bps_per_side) / 10000.0
    df["gross_ret"] = df["position"] * df["bar_ret"]
    df["cost"] = df["turnover"] * cost_rate
    df["net_ret"] = df["gross_ret"] - df["cost"]
    df["nav"] = df.groupby("asset")["net_ret"].transform(lambda s: (1.0 + s).cumprod())
    df["cost_bps_per_side"] = float(cost_bps_per_side)
    nav = df[["asset", "timestamp", "variant", "cost_bps_per_side", "nav"]].copy()
    return df, nav


def summarize_asset_variant(df: pd.DataFrame, asset: str, variant: str, cost: float) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    running_peak = df["nav"].cummax()
    drawdown = df["nav"] / running_peak - 1.0
    return pd.DataFrame([
        {
            "asset": asset,
            "variant": variant,
            "cost_bps_per_side": float(cost),
            "bars": int(len(df)),
            "active_bar_ratio": float((df["position"] != 0.0).mean()),
            "long_share": float((df["position"] > 0.0).mean()),
            "short_share": float((df["position"] < 0.0).mean()),
            "trade_events": int(df["trade_event"].sum()),
            "mean_turnover": float(df["turnover"].mean()),
            "mean_net_ret": float(df["net_ret"].mean()),
            "vol_net_ret": float(df["net_ret"].std(ddof=0)),
            "total_return": float(df["nav"].iloc[-1] - 1.0),
            "max_drawdown": float(drawdown.min()),
            "positive_bar_ratio": float((df["net_ret"] > 0).mean()),
        }
    ])


def build_variant_aggregate(asset_summary: pd.DataFrame) -> pd.DataFrame:
    if asset_summary.empty:
        return pd.DataFrame()
    out = (
        asset_summary.groupby(["variant", "cost_bps_per_side"], as_index=False)
        .agg(
            assets_tested=("asset", "nunique"),
            positive_assets=("total_return", lambda s: int((s > 0).sum())),
            mean_total_return=("total_return", "mean"),
            median_total_return=("total_return", "median"),
            mean_max_drawdown=("max_drawdown", "mean"),
            mean_active_bar_ratio=("active_bar_ratio", "mean"),
            mean_trade_events=("trade_events", "mean"),
            mean_turnover=("mean_turnover", "mean"),
        )
        .sort_values(["cost_bps_per_side", "mean_total_return"], ascending=[True, False])
        .reset_index(drop=True)
    )
    out["positive_asset_ratio"] = out["positive_assets"] / out["assets_tested"].replace(0, np.nan)
    return out


def build_time_stability(primary_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    cols = ["gate", "status", "actual", "threshold", "why_it_matters"]
    if primary_df.empty or len(primary_df) < 30:
        return pd.DataFrame(columns=cols), pd.DataFrame()
    rows = []
    bucket_stats = []
    for asset, g in primary_df.groupby("asset"):
        g = g.sort_values("timestamp").reset_index(drop=True)
        g["bucket"] = pd.qcut(np.arange(len(g)), 3, labels=["early", "mid", "late"])
        tmp = g.groupby("bucket", observed=False).agg(
            asset_return=("net_ret", lambda s: float((1.0 + s).prod() - 1.0)),
            bars=("net_ret", "size"),
            trade_events=("trade_event", "sum"),
        ).reset_index()
        tmp["asset"] = asset
        bucket_stats.append(tmp)
    detail = pd.concat(bucket_stats, ignore_index=True)
    summary = detail.groupby("bucket", as_index=False, observed=False).agg(
        mean_asset_return=("asset_return", "mean"),
        positive_assets=("asset_return", lambda s: int((s > 0).sum())),
        assets=("asset", "nunique"),
        mean_trade_events=("trade_events", "mean"),
    )
    positive_buckets = int((summary["mean_asset_return"] > 0).sum())
    worst_bucket = float(summary["mean_asset_return"].min()) if not summary.empty else np.nan
    rows.append({"gate": "positive_bucket_floor", "status": "pass" if positive_buckets >= 2 else "fail", "actual": f"{positive_buckets}/3 positive buckets", "threshold": ">= 2/3", "why_it_matters": "不能只靠单一时间切片好看。"})
    rows.append({"gate": "worst_bucket_watch", "status": "pass" if pd.notna(worst_bucket) and worst_bucket > -0.08 else "watch", "actual": pct(worst_bucket), "threshold": "> -8%", "why_it_matters": "避免某一段明显塌掉。"})
    rows.append({"gate": "bucket_trade_floor", "status": "pass" if float(summary["mean_trade_events"].min()) >= 30 else "watch", "actual": num(float(summary["mean_trade_events"].min()), 1), "threshold": ">= 30 平均切换", "why_it_matters": "时间切片里仍要有最小交易密度。"})
    return pd.DataFrame(rows), detail


def run_param_config(cfg: dict) -> pd.DataFrame:
    rows = []
    variant_cfg = {
        "variant": "param_probe",
        "gate_mode": "peer_align_strict" if cfg["strict"] else "peer_align",
        "peer_windows": cfg["peer_windows"],
    }
    panel = build_base_panel(mom_window=cfg["mom_window"], peer_windows=cfg["peer_windows"])
    for asset in ASSETS:
        sim, _ = simulate_variant(panel[panel["asset"] == asset].copy() if False else panel, variant_cfg, PRIMARY_COST)
        hit = sim[(sim["asset"] == asset) & (sim["variant"] == "param_probe")].copy()
        rows.append(summarize_asset_variant(hit, asset, "param_probe", PRIMARY_COST).iloc[0])
    return pd.DataFrame(rows)


def build_parameter_stability() -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    detail = []
    for cfg in PARAM_CONFIGS:
        sdf = run_param_config(cfg)
        rows.append({
            "config_label": cfg["label"],
            "mean_total_return": float(sdf["total_return"].mean()),
            "positive_assets": int((sdf["total_return"] > 0).sum()),
            "assets": int(sdf["asset"].nunique()),
            "mean_trade_events": float(sdf["trade_events"].mean()),
        })
        for _, row in sdf.iterrows():
            detail.append({
                "config_label": cfg["label"],
                "asset": row["asset"],
                "total_return": row["total_return"],
                "max_drawdown": row["max_drawdown"],
                "trade_events": row["trade_events"],
            })
    out = pd.DataFrame(rows)
    if out.empty:
        return pd.DataFrame(), pd.DataFrame(detail)
    positive_neighbors = int((out["mean_total_return"] > 0).sum())
    min_trade_events = float(out["mean_trade_events"].min()) if not out.empty else np.nan
    gates = pd.DataFrame([
        {"gate": "neighbor_positive_floor", "status": "pass" if positive_neighbors >= 3 else "fail", "actual": f"{positive_neighbors}/{len(out)} positive configs", "threshold": ">= 3/5", "why_it_matters": "小参数邻域不能一碰就碎。"},
        {"gate": "trade_density_floor", "status": "pass" if pd.notna(min_trade_events) and min_trade_events >= 60 else "watch", "actual": num(min_trade_events, 1), "threshold": ">= 60 平均切换", "why_it_matters": "参数变化后不能只剩极薄样本。"},
    ])
    return gates, pd.DataFrame(detail)


def build_cross_asset_stability(primary_summary: pd.DataFrame) -> pd.DataFrame:
    if primary_summary.empty:
        return pd.DataFrame(columns=["gate", "status", "actual", "threshold", "why_it_matters"])
    positive_assets = int((primary_summary["total_return"] > 0).sum())
    assets = int(primary_summary["asset"].nunique())
    worst_asset = float(primary_summary["total_return"].min()) if not primary_summary.empty else np.nan
    return pd.DataFrame([
        {"gate": "positive_asset_floor", "status": "pass" if positive_assets >= 2 else "fail", "actual": f"{positive_assets}/{assets} positive assets", "threshold": ">= 2/3", "why_it_matters": "不能只在单一币种偶然存活。"},
        {"gate": "worst_asset_watch", "status": "pass" if pd.notna(worst_asset) and worst_asset > -0.12 else "watch", "actual": pct(worst_asset), "threshold": "> -12%", "why_it_matters": "避免最差币种直接把组合拖穿。"},
    ])


def build_cost_trade_stability(overall_summary: pd.DataFrame) -> pd.DataFrame:
    hit = overall_summary[overall_summary["variant"] == PRIMARY_VARIANT].copy().sort_values("cost_bps_per_side")
    if hit.empty:
        return pd.DataFrame(columns=["gate", "status", "actual", "threshold", "why_it_matters"])
    positive_costs = int((hit["mean_total_return"] > 0).sum())
    worst_cost = float(hit["mean_total_return"].min()) if not hit.empty else np.nan
    min_trades = float(hit["mean_trade_events"].min()) if not hit.empty else np.nan
    return pd.DataFrame([
        {"gate": "positive_cost_levels", "status": "pass" if positive_costs >= 2 else "fail", "actual": f"{positive_costs}/{len(hit)} positive cost levels", "threshold": ">= 2/4", "why_it_matters": "成本上去后不能立刻归零。"},
        {"gate": "worst_cost_watch", "status": "pass" if pd.notna(worst_cost) and worst_cost > -0.12 else "watch", "actual": pct(worst_cost), "threshold": "> -12%", "why_it_matters": "高摩擦场景仍要可解释。"},
        {"gate": "trade_floor", "status": "pass" if pd.notna(min_trades) and min_trades >= 80 else "watch", "actual": num(min_trades, 1), "threshold": ">= 80 平均切换", "why_it_matters": "过滤后不能只剩极少交易。"},
    ])


def build_meta(overall_summary: pd.DataFrame, time_gates: pd.DataFrame, param_gates: pd.DataFrame, cross_gates: pd.DataFrame, cost_gates: pd.DataFrame) -> pd.DataFrame:
    primary = overall_summary[(overall_summary["variant"] == PRIMARY_VARIANT) & (overall_summary["cost_bps_per_side"] == PRIMARY_COST)]
    if primary.empty:
        raise RuntimeError("missing primary summary")
    p = primary.iloc[0]
    all_gates = pd.concat([time_gates, param_gates, cross_gates, cost_gates], ignore_index=True)
    fail_count = int((all_gates["status"] == "fail").sum())
    watch_count = int((all_gates["status"] == "watch").sum())
    verdict = "paper_candidate" if fail_count == 0 and float(p["mean_total_return"]) > 0 else "park"
    return pd.DataFrame([
        {
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "candidate": "cross-asset TSMOM confirmation gate",
            "source": "Pitkäjärvi, Suominen, Vaittinen (2020)",
            "winner_variant": PRIMARY_VARIANT,
            "primary_cost_bps_per_side": PRIMARY_COST,
            "mean_total_return": float(p["mean_total_return"]),
            "positive_asset_ratio": float(p["positive_asset_ratio"]),
            "mean_trade_events": float(p["mean_trade_events"]),
            "mean_max_drawdown": float(p["mean_max_drawdown"]),
            "fail_count": fail_count,
            "watch_count": watch_count,
            "verdict_tag": verdict,
        }
    ])


def write_report(overall_summary: pd.DataFrame, primary_summary: pd.DataFrame, time_gates: pd.DataFrame, time_detail: pd.DataFrame, param_gates: pd.DataFrame, param_detail: pd.DataFrame, cross_gates: pd.DataFrame, cost_gates: pd.DataFrame, meta: pd.DataFrame) -> None:
    ensure_dir(SITE_DIR)
    meta_row = meta.iloc[0]
    primary_row = overall_summary[(overall_summary["variant"] == PRIMARY_VARIANT) & (overall_summary["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    generated_at = meta_row["generated_at_utc"]
    verdict = str(meta_row["verdict_tag"])
    html = f"""
<!doctype html>
<html lang=\"zh\">
<head>
  <meta charset=\"utf-8\" />
  <title>Scout｜Cross-asset TSMOM gate 15m</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 24px auto; max-width: 1180px; line-height: 1.5; color: #1f2937; padding: 0 16px 64px; }}
    h1, h2, h3 {{ color: #111827; }}
    .muted {{ color: #6b7280; }}
    .pill {{ display: inline-block; padding: 4px 10px; border-radius: 999px; background: #eef2ff; margin-right: 8px; margin-bottom: 8px; }}
    .good {{ background: #dcfce7; }}
    .bad {{ background: #fee2e2; }}
    table {{ border-collapse: collapse; width: 100%; margin: 14px 0 24px; font-size: 14px; }}
    th, td {{ border: 1px solid #e5e7eb; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #f9fafb; }}
    code {{ background: #f3f4f6; padding: 1px 4px; border-radius: 4px; }}
  </style>
</head>
<body>
  <h1>Scout Seat｜Cross-asset TSMOM confirmation gate（15m crypto）</h1>
  <p class=\"muted\">生成时间：{escape(str(generated_at))}</p>
  <p>
    <span class=\"pill {'bad' if verdict == 'park' else 'good'}\">hard verdict：{escape(verdict)}</span>
    <span class=\"pill\">primary variant：{escape(PRIMARY_VARIANT)}</span>
    <span class=\"pill\">primary cost：{escape(num(PRIMARY_COST, 0))} bps/side</span>
  </p>
  <h2>一句话结论</h2>
  <p>这次把 <code>cross-asset signals and time-series momentum</code> 翻成 15m crypto 的最小 clean-room：先看本币 <code>sign(momentum)</code>，再要求其余主流币的 <code>1h + 4h</code> peer basket 同向。结果是 <b>{escape(PRIMARY_VARIANT)}</b> 在 120d / 15m / BTC-ETH-SOL cache 上只有 <b>{pct(primary_row['mean_total_return'])}</b>、<b>{num(primary_row['positive_assets'], 0)}/{num(primary_row['assets_tested'], 0)}</b> 资产为正、平均切换 <b>{num(primary_row['mean_trade_events'], 1)}</b>，仍不足以进入 paper candidate，当前更诚实的结论仍是 <b>park</b>。</p>

  <h2>Clean-room 规则</h2>
  <ul>
    <li><code>mom_16 = close / close.shift(16) - 1</code></li>
    <li>baseline：<code>mom &gt; 0</code> 做多，<code>mom &lt; 0</code> 做空</li>
    <li><code>peer_1h_gate</code>：其余两币近 <code>4</code> 根 15m 收益均值与本币方向同向</li>
    <li><code>peer_4h_gate</code>：其余两币近 <code>16</code> 根 15m 收益均值与本币方向同向</li>
    <li><code>peer_dual_gate</code>：1h 与 4h peer basket 都要同向；<code>peer_dual_strict</code> 额外要求两档 peer return 非零</li>
    <li>成本：按持仓切换收单边 <code>6/10/15/20 bps</code></li>
  </ul>

  <h2>Primary 资产读法</h2>
  {render_table(primary_summary[["asset", "total_return", "max_drawdown", "active_bar_ratio", "trade_events", "long_share", "short_share"]], percent_cols={"total_return", "max_drawdown", "active_bar_ratio", "long_share", "short_share"}, digits_cols={"trade_events": 0})}

  <h2>Variant 总览</h2>
  {render_table(overall_summary[["variant", "cost_bps_per_side", "mean_total_return", "positive_asset_ratio", "mean_max_drawdown", "mean_active_bar_ratio", "mean_trade_events"]], percent_cols={"mean_total_return", "positive_asset_ratio", "mean_max_drawdown", "mean_active_bar_ratio"}, digits_cols={"cost_bps_per_side": 0, "mean_trade_events": 1})}

  <h2>Light Stability Pack</h2>
  <h3>时间稳定性</h3>
  {render_table(time_gates, percent_cols=set())}
  {render_table(time_detail[["asset", "bucket", "asset_return", "trade_events"]], percent_cols={"asset_return"}, digits_cols={"trade_events": 0})}

  <h3>参数稳定性</h3>
  {render_table(param_gates, percent_cols=set())}
  {render_table(param_detail[["config_label", "asset", "total_return", "max_drawdown", "trade_events"]], percent_cols={"total_return", "max_drawdown"}, digits_cols={"trade_events": 0})}

  <h3>跨标的稳定性</h3>
  {render_table(cross_gates, percent_cols=set())}

  <h3>成本 / 交易数稳定性</h3>
  {render_table(cost_gates, percent_cols=set())}

  <h2>为什么当前先 park</h2>
  <ul>
    <li>如果跨资产 gate 真有明显增量，至少应让 3 个币里 2 个存活，或在多个成本档下不至于整体继续为负；当前没有做到。</li>
    <li>它更像是给单币动量加一层“市场共振确认”，而不是能单独撑起 15m crypto alpha 的候选。</li>
    <li>因此当前更适合把它留在 evidence pool，作为未来 EMA / TSMOM 的 confirmation 参考，而不是继续升格到 paper candidate。</li>
  </ul>
</body>
</html>
"""
    REPORT_PATH.write_text(html, encoding="utf-8")


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    SPEC_PATH.write_text(
        "candidate,source,mom_window,primary_variant,rule\n"
        "cross-asset TSMOM confirmation gate,Pitkajarvi et al. 2020,16,peer_dual_gate,sign(momentum) gated by peer-basket 1h+4h alignment\n",
        encoding="utf-8",
    )

    sim_frames = []
    nav_frames = []
    asset_summary_frames = []
    panel = build_base_panel(mom_window=PRIMARY_MOM_WINDOW, peer_windows=(4, 16))
    for variant_cfg in VARIANTS:
        for cost in COSTS:
            sim, nav = simulate_variant(panel, variant_cfg, cost)
            sim_frames.append(sim)
            nav_frames.append(nav)
            for asset in ASSETS:
                asset_summary_frames.append(summarize_asset_variant(sim[sim["asset"] == asset].copy(), asset, variant_cfg["variant"], cost))

    sim_df = pd.concat(sim_frames, ignore_index=True)
    nav_df = pd.concat(nav_frames, ignore_index=True)
    asset_summary = pd.concat(asset_summary_frames, ignore_index=True)
    overall_summary = build_variant_aggregate(asset_summary)
    primary_summary = asset_summary[(asset_summary["variant"] == PRIMARY_VARIANT) & (asset_summary["cost_bps_per_side"] == PRIMARY_COST)].copy().reset_index(drop=True)
    primary_df = sim_df[(sim_df["variant"] == PRIMARY_VARIANT) & (sim_df["cost_bps_per_side"] == PRIMARY_COST)].copy()

    time_gates, time_detail = build_time_stability(primary_df)
    param_gates, param_detail = build_parameter_stability()
    cross_gates = build_cross_asset_stability(primary_summary)
    cost_gates = build_cost_trade_stability(overall_summary)
    meta = build_meta(overall_summary, time_gates, param_gates, cross_gates, cost_gates)

    sim_df.to_csv(ART_DIR / "bar_level_simulation.csv", index=False)
    nav_df.to_csv(ART_DIR / "nav_series.csv", index=False)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    overall_summary.to_csv(ART_DIR / "overall_summary.csv", index=False)
    primary_summary.to_csv(ART_DIR / "primary_asset_summary.csv", index=False)
    time_gates.to_csv(ART_DIR / "time_stability_drycheck.csv", index=False)
    time_detail.to_csv(ART_DIR / "time_stability_detail.csv", index=False)
    param_gates.to_csv(ART_DIR / "parameter_stability_drycheck.csv", index=False)
    param_detail.to_csv(ART_DIR / "parameter_stability_detail.csv", index=False)
    cross_gates.to_csv(ART_DIR / "cross_asset_stability_drycheck.csv", index=False)
    cost_gates.to_csv(ART_DIR / "cost_trade_stability_drycheck.csv", index=False)
    meta.to_csv(ART_DIR / "clean_replication_meta.csv", index=False)
    write_report(overall_summary, primary_summary, time_gates, time_detail, param_gates, param_detail, cross_gates, cost_gates, meta)
    print("[ok] cross-asset tsmom gate clean replication generated")


if __name__ == "__main__":
    main()
