#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank153_liquidation_consensus_cascade_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank153_liquidation_consensus_cascade_15m"
READING_PAGE = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank153_liquidation_consensus_cascade_first_verdict.html"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT"}
SAMPLE_DAYS = 45
COSTS = [6.0, 12.0, 20.0]  # round-trip bps
LOCAL_OI_CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_rank138_funding_oi_crowding_breadth_15m" / "oi_cache"
LOCAL_FUNDING_CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_rank138_funding_oi_crowding_breadth_15m" / "funding_cache"
ROLL_FUNDING = 21
ROLL_OI = 20
ROLL_CLUSTER = 96


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def pct(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def num(v: float | int | None, digits: int = 2) -> str:
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


def load_cached_bars(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    cutoff = df["timestamp"].max() - pd.Timedelta(days=SAMPLE_DAYS)
    df = df[df["timestamp"] >= cutoff].copy()
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def fetch_oi_5m(symbol: str, start_ms: int) -> pd.DataFrame:
    path = LOCAL_OI_CACHE_DIR / f"{symbol}_5m_open_interest.csv"
    if not path.exists():
        return pd.DataFrame(columns=["timestamp", "sumOpenInterest"])
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, format="mixed")
    df["sumOpenInterest"] = pd.to_numeric(df["sumOpenInterest"], errors="coerce")
    df = df[["timestamp", "sumOpenInterest"]].drop_duplicates("timestamp").sort_values("timestamp").reset_index(drop=True)
    return df[df["timestamp"] >= pd.to_datetime(start_ms, unit="ms", utc=True)].copy()


def aggregate_oi_to_15m(oi_5m: pd.DataFrame) -> pd.DataFrame:
    if oi_5m.empty:
        return pd.DataFrame(columns=["timestamp", "oi_close"])
    work = oi_5m.copy()
    work["timestamp"] = work["timestamp"].dt.floor("15min")
    out = work.groupby("timestamp", as_index=False)["sumOpenInterest"].last().rename(columns={"sumOpenInterest": "oi_close"})
    return out.sort_values("timestamp").reset_index(drop=True)


def fetch_funding(symbol: str, start_ms: int) -> pd.DataFrame:
    path = LOCAL_FUNDING_CACHE_DIR / f"{symbol}_funding.csv"
    if not path.exists():
        return pd.DataFrame(columns=["timestamp", "funding_rate"])
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, format="mixed")
    df["funding_rate"] = pd.to_numeric(df["funding_rate"], errors="coerce")
    df = df[["timestamp", "funding_rate"]].drop_duplicates("timestamp").sort_values("timestamp").reset_index(drop=True)
    return df[df["timestamp"] >= pd.to_datetime(start_ms, unit="ms", utc=True)].copy()


def build_asset_frame(asset: str, symbol: str, start_ms: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    bars = load_cached_bars(symbol, asset)
    oi_5m = fetch_oi_5m(symbol, start_ms)
    oi_15m = aggregate_oi_to_15m(oi_5m)
    funding = fetch_funding(symbol, start_ms)

    frame = bars.merge(oi_15m, on="timestamp", how="left")
    frame = pd.merge_asof(frame.sort_values("timestamp"), funding.sort_values("timestamp"), on="timestamp", direction="backward")
    frame["ret_1"] = frame["close"].pct_change()
    frame["ret_4h"] = frame["close"].pct_change(16)
    frame["ret_45m"] = frame["close"].pct_change(3)
    frame["abs_ret_45m"] = frame["ret_45m"].abs()
    frame["oi_4h_pct"] = frame["oi_close"].pct_change(16)
    frame["funding_abs"] = frame["funding_rate"].abs()
    frame["funding_abs_q80"] = frame["funding_abs"].rolling(ROLL_FUNDING, min_periods=8).quantile(0.8).shift(1)
    frame["oi_q80"] = frame["oi_4h_pct"].rolling(ROLL_OI, min_periods=8).quantile(0.8).shift(1)
    frame["cluster_proxy_q80"] = frame["abs_ret_45m"].rolling(ROLL_CLUSTER, min_periods=32).quantile(0.8).shift(1)
    frame["crowd_side"] = np.sign(frame["funding_rate"]).replace(0, np.nan)
    frame["base_signal"] = (
        frame["funding_rate"].notna()
        & frame["oi_4h_pct"].notna()
        & frame["funding_abs_q80"].notna()
        & frame["oi_q80"].notna()
        & (frame["funding_abs"] >= frame["funding_abs_q80"])
        & (frame["oi_4h_pct"] >= frame["oi_q80"])
        & frame["crowd_side"].notna()
    ).fillna(False)
    frame["direction"] = -np.sign(frame["funding_rate"]).replace(0, np.nan)
    frame["signal_side"] = frame["direction"].map({1.0: "long", -1.0: "short"})
    return frame.reset_index(drop=True), oi_5m, funding


def build_cluster_panel(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    panel = []
    for asset, frame in frames.items():
        part = frame[["timestamp", "ret_45m", "abs_ret_45m", "direction", "base_signal"]].copy()
        part["asset"] = asset
        part["cluster_direction_match"] = ((np.sign(part["ret_45m"]) == part["direction"]) & part["direction"].notna()).astype(int)
        part["shock_flag"] = (part["abs_ret_45m"] >= frame["cluster_proxy_q80"]).astype(int)
        panel.append(part)
    merged = pd.concat(panel, ignore_index=True)
    out = (
        merged.groupby("timestamp", as_index=False)
        .agg(
            cluster_assets=("shock_flag", "sum"),
            matched_assets=("cluster_direction_match", "sum"),
        )
        .sort_values("timestamp")
        .reset_index(drop=True)
    )
    out["consensus_cluster"] = (out["cluster_assets"] >= 2) & (out["matched_assets"] >= 2)
    return out


def make_events(frame: pd.DataFrame, variant: str) -> pd.DataFrame:
    sig = frame["base_signal"].copy()
    if variant == "funding_oi_cluster":
        sig &= frame["consensus_cluster"].fillna(False)
    sig &= ~sig.shift(1).fillna(False)
    rows: list[dict[str, object]] = []
    last_exit = -1
    for idx in range(20, len(frame) - 3):
        if idx <= last_exit or not bool(sig.iloc[idx]):
            continue
        direction = frame.iloc[idx]["direction"]
        if pd.isna(direction):
            continue
        rows.append(
            {
                "asset": frame.iloc[idx]["asset"],
                "variant": variant,
                "signal_idx": idx,
                "entry_idx": idx + 1,
                "signal_ts": pd.to_datetime(frame.iloc[idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "direction": int(direction),
                "signal_side": "long" if int(direction) > 0 else "short",
                "funding_rate": float(frame.iloc[idx]["funding_rate"]),
                "oi_4h_pct": float(frame.iloc[idx]["oi_4h_pct"]),
                "ret_45m": float(frame.iloc[idx]["ret_45m"]),
                "consensus_cluster": int(bool(frame.iloc[idx]["consensus_cluster"])),
            }
        )
        last_exit = idx + 2
    return pd.DataFrame(rows)


def trade_return(frame: pd.DataFrame, entry_idx: int, hold_bars: int, direction: int, mode: str, cost_bps_rt: float) -> tuple[float, float, float, float]:
    exit_idx = min(len(frame) - 1, entry_idx + hold_bars - 1)
    entry_px = float(frame.iloc[entry_idx]["open"])
    exit_px = float(frame.iloc[exit_idx]["close"])
    cont_ret = direction * ((exit_px / entry_px) - 1.0)
    gross = cont_ret if mode == "continuation" else -cont_ret
    net = gross - float(cost_bps_rt) / 10000.0

    path = frame.iloc[entry_idx : exit_idx + 1]
    if direction > 0:
        mfe = float((path["high"].max() / entry_px) - 1.0)
        mae = float((path["low"].min() / entry_px) - 1.0)
    else:
        mfe = float(1.0 - (path["low"].min() / entry_px))
        mae = float(1.0 - (path["high"].max() / entry_px))
    if mode == "reversal":
        mfe, mae = -mae, -mfe
    return gross, net, mfe, mae


def evaluate_events(frame: pd.DataFrame, events: pd.DataFrame, hold_bars: int, exit_mode: str, cost_bps_rt: float) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for _, ev in events.iterrows():
        entry_idx = int(ev["entry_idx"])
        if entry_idx >= len(frame):
            continue
        gross, net, mfe, mae = trade_return(frame, entry_idx, hold_bars, int(ev["direction"]), exit_mode, cost_bps_rt)
        exit_idx = min(len(frame) - 1, entry_idx + hold_bars - 1)
        rows.append(
            {
                **ev.to_dict(),
                "hold": "15m" if hold_bars == 1 else "30m",
                "exit_mode": exit_mode,
                "cost_bps_rt": float(cost_bps_rt),
                "entry_ts": pd.to_datetime(frame.iloc[entry_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": pd.to_datetime(frame.iloc[exit_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "gross_ret": gross,
                "net_ret": net,
                "mfe": mfe,
                "mae": mae,
            }
        )
    return pd.DataFrame(rows)


def summarize_asset(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["asset", "variant", "exit_mode", "hold", "cost_bps_rt", "event_count", "mean_net_bps", "win_rate", "mean_mfe_bps", "mean_mae_bps"])
    out = (
        trades.groupby(["asset", "variant", "exit_mode", "hold", "cost_bps_rt"], dropna=False)
        .agg(
            event_count=("net_ret", "size"),
            mean_net_bps=("net_ret", lambda s: float(s.mean() * 10000.0)),
            win_rate=("net_ret", lambda s: float((s > 0).mean())),
            mean_mfe_bps=("mfe", lambda s: float(s.mean() * 10000.0)),
            mean_mae_bps=("mae", lambda s: float(s.mean() * 10000.0)),
        )
        .reset_index()
        .sort_values(["variant", "exit_mode", "hold", "cost_bps_rt", "asset"])
        .reset_index(drop=True)
    )
    return out


def summarize_combo(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["variant", "exit_mode", "hold", "cost_bps_rt", "event_count", "mean_net_bps", "win_rate", "mean_mfe_bps", "mean_mae_bps"])
    out = (
        trades.groupby(["variant", "exit_mode", "hold", "cost_bps_rt"], dropna=False)
        .agg(
            event_count=("net_ret", "size"),
            mean_net_bps=("net_ret", lambda s: float(s.mean() * 10000.0)),
            win_rate=("net_ret", lambda s: float((s > 0).mean())),
            mean_mfe_bps=("mfe", lambda s: float(s.mean() * 10000.0)),
            mean_mae_bps=("mae", lambda s: float(s.mean() * 10000.0)),
        )
        .reset_index()
        .sort_values(["variant", "exit_mode", "hold", "cost_bps_rt"])
        .reset_index(drop=True)
    )
    return out


def build_scorecard(combo: pd.DataFrame) -> pd.DataFrame:
    if combo.empty:
        return pd.DataFrame([{
            "rank": 153,
            "candidate": "liquidation consensus cascade continuation alpha",
            "recommended_action": "park",
            "usefulness": 0,
            "time_stability": 0,
            "cross_asset_stability": 0,
            "cost_trade_stability": 0,
            "deployability": 0,
            "main_weakness": "artifact missing",
        }])
    focus = combo[(combo["exit_mode"] == "continuation") & (combo["hold"] == "15m") & (combo["cost_bps_rt"] == 12.0)].copy()
    if focus.empty:
        focus = combo[(combo["exit_mode"] == "continuation") & (combo["hold"] == "30m") & (combo["cost_bps_rt"] == 12.0)].copy()
    best = focus.sort_values(["mean_net_bps", "event_count"], ascending=[False, False]).iloc[0]
    reversal_focus = combo[(combo["variant"] == best["variant"]) & (combo["exit_mode"] == "reversal") & (combo["hold"] == best["hold"]) & (combo["cost_bps_rt"] == best["cost_bps_rt"])]
    reversal_bps = float(reversal_focus.iloc[0]["mean_net_bps"]) if not reversal_focus.empty else np.nan

    recommended_action = "promote_P2" if float(best["mean_net_bps"]) > 8 and int(best["event_count"]) >= 24 else "keep_P1" if float(best["mean_net_bps"]) > 0 and int(best["event_count"]) >= 10 else "park"
    usefulness = 3 if float(best["mean_net_bps"]) > 8 else 2 if float(best["mean_net_bps"]) > 0 else 1 if float(best["mean_net_bps"]) > -5 else 0
    time_stability = 1
    cross_asset_stability = 2
    cost_trade_stability = 2 if int(best["event_count"]) >= 10 else 1
    deployability = 2 if best["variant"] == "funding_oi" else 1
    main_weakness = "cluster 目前只是本地 public-proxy 共振替身，不是真实 liquidation heatmap；因此 first verdict 只够决定 keep_P1 / park。"

    return pd.DataFrame([{
        "rank": 153,
        "candidate": "liquidation consensus cascade continuation alpha",
        "best_variant": best["variant"],
        "best_exit": best["exit_mode"],
        "best_hold": best["hold"],
        "best_cost_bps_rt": best["cost_bps_rt"],
        "best_mean_net_bps": best["mean_net_bps"],
        "reversal_same_cell_bps": reversal_bps,
        "recommended_action": recommended_action,
        "usefulness": usefulness,
        "time_stability": time_stability,
        "cross_asset_stability": cross_asset_stability,
        "cost_trade_stability": cost_trade_stability,
        "deployability": deployability,
        "main_weakness": main_weakness,
    }])


def build_verdict(combo: pd.DataFrame) -> tuple[str, str]:
    if combo.empty:
        return "park", "没有足够事件形成最小 first verdict。"
    focus = combo[(combo["exit_mode"] == "continuation") & (combo["hold"] == "15m") & (combo["cost_bps_rt"] == 12.0)].copy()
    if focus.empty:
        focus = combo[(combo["exit_mode"] == "continuation") & (combo["hold"] == "30m") & (combo["cost_bps_rt"] == 12.0)].copy()
    best = focus.sort_values(["mean_net_bps", "event_count"], ascending=[False, False]).iloc[0]
    rev = combo[(combo["variant"] == best["variant"]) & (combo["exit_mode"] == "reversal") & (combo["hold"] == best["hold"]) & (combo["cost_bps_rt"] == best["cost_bps_rt"])]
    rev_bps = float(rev.iloc[0]["mean_net_bps"]) if not rev.empty else np.nan
    if float(best["mean_net_bps"]) > 8 and int(best["event_count"]) >= 24:
        return "promote_P2", f"{best['variant']} 在 continuation/{best['hold']}/12bps 下均值 {best['mean_net_bps']:.2f}bps，且明显强于 reversal({rev_bps:.2f}bps)。"
    if float(best["mean_net_bps"]) > 0 and int(best["event_count"]) >= 10:
        return "keep_P1", f"最小 first verdict 偏向 continuation：{best['variant']} 在 {best['hold']}/12bps 下均值 {best['mean_net_bps']:.2f}bps，reversal 同格 {rev_bps:.2f}bps；但样本仍小，cluster 只是 proxy。"
    return "park", f"当前最优格仍不够诚实：{best['variant']} 在 continuation/{best['hold']}/12bps 仅 {best['mean_net_bps']:.2f}bps，reversal 同格 {rev_bps:.2f}bps。"


def build_html(meta: pd.DataFrame, combo: pd.DataFrame, asset_summary: pd.DataFrame, scorecard: pd.DataFrame, verdict: str, detail: str) -> str:
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 153 · liquidation consensus cascade first verdict</title>
  <style>
    body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width:1120px; margin:40px auto; padding:0 18px; line-height:1.7; color:#111827; background:#f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:16px 18px; margin:14px 0; }}
    .muted {{ color:#6b7280; }}
    table {{ border-collapse:collapse; width:100%; font-size:14px; }}
    th, td {{ border:1px solid #e5e7eb; padding:6px 8px; text-align:left; vertical-align:top; }}
    th {{ background:#f3f4f6; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
  </style>
</head>
<body>
  <h1>Rank 153 · liquidation consensus cascade continuation alpha（first verdict / minimal）</h1>
  <p class='muted'>生成时间：{escape(generated)}｜冻结口径：BTC / ETH、15m 本地 bar cache + Binance funding / 5m OI 聚合到 15m；A/B = <code>funding+OI</code> vs <code>funding+OI+cluster-proxy</code>；出场 = continuation vs reversal；成本 = 6 / 12 / 20 bps round-trip。</p>

  <div class='card'>
    <h2>hard verdict</h2>
    <p><b>{escape(verdict)}</b></p>
    <p>{escape(detail)}</p>
    <p class='muted'>诚实说明：这里的 <code>cluster</code> 还不是 source repo 里的真实 liquidation heatmap / whale cluster，而是更便宜的 public-proxy——BTC/ETH 同向 45m shock 的两资产共振。它足够做最小 first verdict，但还不够拿来宣称 source 完整复现。</p>
  </div>

  <div class='card'>
    <h2>sample meta</h2>
    {render_table(meta)}
  </div>

  <div class='card'>
    <h2>scorecard</h2>
    {render_table(scorecard, percent_cols=set(), digits_cols={"rank":0, "best_cost_bps_rt":0, "best_mean_net_bps":2, "reversal_same_cell_bps":2})}
  </div>

  <div class='card'>
    <h2>combo summary</h2>
    {render_table(combo, percent_cols={"win_rate"}, digits_cols={"cost_bps_rt":0, "event_count":0, "mean_net_bps":2, "mean_mfe_bps":2, "mean_mae_bps":2})}
  </div>

  <div class='card'>
    <h2>asset summary</h2>
    {render_table(asset_summary, percent_cols={"win_rate"}, digits_cols={"cost_bps_rt":0, "event_count":0, "mean_net_bps":2, "mean_mfe_bps":2, "mean_mae_bps":2})}
  </div>
</body>
</html>
"""


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PAGE.parent)

    start_dt = datetime.now(timezone.utc) - timedelta(days=SAMPLE_DAYS + 2)
    start_ms = int(start_dt.timestamp() * 1000)

    frames: dict[str, pd.DataFrame] = {}
    meta_rows: list[dict[str, object]] = []
    for asset, symbol in ASSETS.items():
        frame, oi_5m, funding = build_asset_frame(asset, symbol, start_ms)
        frames[asset] = frame
        oi_5m.to_csv(ART_DIR / f"{symbol.lower()}_oi_5m.csv", index=False)
        funding.to_csv(ART_DIR / f"{symbol.lower()}_funding.csv", index=False)
        meta_rows.append({
            "asset": asset,
            "symbol": symbol,
            "bars_15m": int(len(frame)),
            "oi_rows_5m": int(len(oi_5m)),
            "funding_rows": int(len(funding)),
            "sample_start_utc": frame["timestamp"].min().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "sample_end_utc": frame["timestamp"].max().strftime("%Y-%m-%dT%H:%M:%SZ"),
        })

    cluster_panel = build_cluster_panel(frames)
    cluster_panel.to_csv(ART_DIR / "cluster_panel.csv", index=False)

    enriched: dict[str, pd.DataFrame] = {}
    event_frames: list[pd.DataFrame] = []
    trade_frames: list[pd.DataFrame] = []
    for asset, frame in frames.items():
        merged = frame.merge(cluster_panel[["timestamp", "consensus_cluster"]], on="timestamp", how="left")
        merged["consensus_cluster"] = merged["consensus_cluster"].fillna(False)
        enriched[asset] = merged
        merged.to_csv(ART_DIR / f"{ASSETS[asset].lower()}_feature_frame.csv", index=False)
        for variant in ["funding_oi", "funding_oi_cluster"]:
            events = make_events(merged, variant)
            if not events.empty:
                event_frames.append(events)
            for hold_bars, hold_label in [(1, "15m"), (2, "30m")]:
                for exit_mode in ["continuation", "reversal"]:
                    for cost_bps in COSTS:
                        trades = evaluate_events(merged, events, hold_bars, exit_mode, cost_bps)
                        if not trades.empty:
                            trade_frames.append(trades)

    events_df = pd.concat(event_frames, ignore_index=True) if event_frames else pd.DataFrame()
    trades_df = pd.concat(trade_frames, ignore_index=True) if trade_frames else pd.DataFrame()
    events_df.to_csv(ART_DIR / "events.csv", index=False)
    trades_df.to_csv(ART_DIR / "trades.csv", index=False)

    asset_summary = summarize_asset(trades_df)
    combo = summarize_combo(trades_df)
    scorecard = build_scorecard(combo)
    verdict, detail = build_verdict(combo)
    meta = pd.DataFrame(meta_rows)

    meta.to_csv(ART_DIR / "sample_meta.csv", index=False)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    combo.to_csv(ART_DIR / "combo_summary.csv", index=False)
    scorecard.to_csv(ART_DIR / "scorecard.csv", index=False)
    pd.DataFrame([{
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sample_days": SAMPLE_DAYS,
        "verdict": verdict,
        "detail": detail,
    }]).to_csv(ART_DIR / "summary.csv", index=False)

    html = build_html(meta, combo, asset_summary, scorecard, verdict, detail)
    (SITE_DIR / "report.html").write_text(html, encoding="utf-8")
    READING_PAGE.write_text(html, encoding="utf-8")
    print(f"ok: built rank153 minimal first verdict ({verdict})")


if __name__ == "__main__":
    main()
