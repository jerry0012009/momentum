#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank32b_slope_floor_continuation_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank32b_slope_floor_continuation_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "trendline_alpha_scout" / "rank32b_slope_floor_continuation_clean_replication.html"

DAYS = 1825
MARKER_ID = "rank32b-unified-cost-round3-1825d"
ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}

PROFILE_CONFIGS = {
    "vip0_base": {
        "label": "VIP0 base realistic",
        "maker_fee_bps": 2.0,
        "taker_fee_bps": 5.0,
        "maker_slip_bps": 0.0,
        "taker_entry_slip_bps": 1.0,
        "taker_exit_slip_bps": 1.0,
        "stop_slip_bps": 2.0,
        "timeout_slip_bps": 1.0,
    },
    "vip0_stress": {
        "label": "VIP0 stressed slippage",
        "maker_fee_bps": 2.0,
        "taker_fee_bps": 5.0,
        "maker_slip_bps": 0.0,
        "taker_entry_slip_bps": 2.0,
        "taker_exit_slip_bps": 2.0,
        "stop_slip_bps": 3.0,
        "timeout_slip_bps": 2.0,
    },
}
PROFILE_ORDER = ["vip0_base", "vip0_stress"]
FOCUS_SCENARIOS = [
    "fixed_hold_4_taker",
    "baseline_taker_fixed8",
    "maker_entry_2bps_ttl15m_fixed8",
    "taker_tp1.25_sl1.00_to8",
    "taker_tp1.00_sl1.00_to16",
    "maker2bps_tp1.25_sl1.00_to8",
    "maker2bps_tp1.00_sl1.00_to16",
]

SCENARIO_LABELS = {
    "fixed_hold_4_taker": "固定持有 4x15m（taker close）",
    "baseline_taker_fixed8": "固定持有 8x15m（taker entry/exit）",
    "maker_entry_2bps_ttl15m_fixed8": "maker-first 入场 2bps / TTL15m + fixed 8x15m",
    "taker_tp1.25_sl1.00_to8": "taker 入场 + TP 1.25 ATR / SL 1.00 ATR / timeout 8x15m",
    "taker_tp1.00_sl1.00_to16": "taker 入场 + TP 1.00 ATR / SL 1.00 ATR / timeout 16x15m",
    "maker2bps_tp1.25_sl1.00_to8": "maker-first 入场 2bps + TP 1.25 ATR / SL 1.00 ATR / timeout 8x15m",
    "maker2bps_tp1.00_sl1.00_to16": "maker-first 入场 2bps + TP 1.00 ATR / SL 1.00 ATR / timeout 16x15m",
}


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
        return '<p class="muted">暂无数据。</p>'
    percent_cols = percent_cols or set()
    digits_cols = digits_cols or {}
    headers = ''.join(f'<th>{escape(str(c))}</th>' for c in df.columns)
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
            cells.append(f'<td>{escape(text)}</td>')
        rows.append(f'<tr>{"".join(cells)}</tr>')
    return f'<table><thead><tr>{headers}</tr></thead><tbody>{"".join(rows)}</tbody></table>'


def load_csv(path: Path, time_cols: list[str] | None = None) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in time_cols or []:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], utc=True, format="mixed")
    return df


def infer_exit_type(row: pd.Series) -> str:
    scenario = str(row.get("scenario", ""))
    if scenario.startswith("fixed_hold_") or scenario.endswith("fixed8"):
        return "fixed_close"
    if row.get("stop_hit", 0) == 1:
        return "stop_loss"
    if row.get("same_bar_conflict", 0) == 1:
        return "conflict_stop_first"
    if row.get("exit_type") and not pd.isna(row.get("exit_type")):
        return str(row.get("exit_type"))
    if int(row.get("exit_maker", 0)) == 1:
        return "target_limit"
    return "timeout_close"


def normalize_trade_frame(df: pd.DataFrame, source: str) -> pd.DataFrame:
    out = df.copy()
    out["source"] = source
    for col in ["entry_ts", "exit_ts"]:
        out[col] = pd.to_datetime(out[col], utc=True)
    if "stop_hit" not in out.columns:
        out["stop_hit"] = 0
    if "same_bar_conflict" not in out.columns:
        out["same_bar_conflict"] = 0
    if "entry_offset_bps" not in out.columns:
        out["entry_offset_bps"] = 0.0
    if "hold_minutes" not in out.columns:
        out["hold_minutes"] = (out["exit_ts"] - out["entry_ts"]).dt.total_seconds().div(60).round().astype(int)
    out["exit_type"] = out.apply(infer_exit_type, axis=1)
    return out


def load_trade_universe() -> pd.DataFrame:
    fixed_path = ART_DIR / f"execution_probe_{DAYS}d_exit_family_trades.csv"
    exec_path = ART_DIR / f"execution_probe_{DAYS}d_execution_scenarios_trades.csv"
    atr_path = ART_DIR / f"atr_exit_round2_{DAYS}d_trades.csv"

    fixed_df = normalize_trade_frame(load_csv(fixed_path, ["entry_ts", "exit_ts"]), "fixed_exit_family")
    exec_df = normalize_trade_frame(load_csv(exec_path, ["entry_ts", "exit_ts"]), "execution_scenarios")
    atr_df = normalize_trade_frame(load_csv(atr_path, ["entry_ts", "exit_ts"]), "atr_oco_round2")

    fixed_keep = fixed_df[fixed_df["scenario"].isin(["fixed_hold_4_taker"])]
    exec_keep = exec_df[exec_df["scenario"].isin(["baseline_taker_fixed8", "maker_entry_2bps_ttl15m_fixed8"])]
    atr_keep = atr_df[atr_df["scenario"].isin([s for s in FOCUS_SCENARIOS if s.startswith("taker_") or s.startswith("maker2bps_")])]
    all_trades = pd.concat([fixed_keep, exec_keep, atr_keep], ignore_index=True)
    return all_trades


def load_funding_map() -> dict[str, pd.DataFrame]:
    fmap: dict[str, pd.DataFrame] = {}
    for asset, symbol in ASSETS.items():
        path = ART_DIR / "perp_cache" / f"{symbol}__{DAYS}d__funding.csv"
        df = load_csv(path, ["timestamp"]).sort_values("timestamp").reset_index(drop=True)
        fmap[asset] = df
    return fmap


def funding_factor_and_stats(entry_ts: pd.Timestamp, exit_ts: pd.Timestamp, direction: str, funding_df: pd.DataFrame) -> tuple[float, int, float]:
    if funding_df.empty or exit_ts <= entry_ts:
        return 1.0, 0, 0.0
    ts = funding_df["timestamp"].to_numpy(dtype="datetime64[ns]")
    rates = funding_df["funding_rate"].to_numpy(dtype=float)
    left = int(np.searchsorted(ts, entry_ts.to_datetime64(), side="right"))
    right = int(np.searchsorted(ts, exit_ts.to_datetime64(), side="right"))
    hits = rates[left:right]
    if len(hits) == 0:
        return 1.0, 0, 0.0
    direction_sign = 1.0 if direction == "long" else -1.0
    factor = float(np.prod(1.0 - direction_sign * hits))
    return factor, int(len(hits)), float(hits.sum())


def slip_bps_for_side(row: pd.Series, profile: dict[str, float], side: str) -> float:
    if side == "entry":
        return float(profile["maker_slip_bps"] if int(row["entry_maker"]) == 1 else profile["taker_entry_slip_bps"])
    if int(row["exit_maker"]) == 1:
        return float(profile["maker_slip_bps"])
    exit_type = str(row["exit_type"])
    if exit_type in {"stop_loss", "conflict_stop_first"}:
        return float(profile["stop_slip_bps"])
    if exit_type == "timeout_close":
        return float(profile["timeout_slip_bps"])
    return float(profile["taker_exit_slip_bps"])


def fee_bps_for_side(is_maker: int, profile: dict[str, float]) -> float:
    return float(profile["maker_fee_bps"] if int(is_maker) == 1 else profile["taker_fee_bps"])


def apply_profile(trades: pd.DataFrame, funding_map: dict[str, pd.DataFrame], profile_name: str, profile: dict[str, float]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for _, row in trades.iterrows():
        asset = str(row["asset"])
        funding_factor, funding_events, funding_rate_sum = funding_factor_and_stats(pd.to_datetime(row["entry_ts"], utc=True), pd.to_datetime(row["exit_ts"], utc=True), str(row["direction"]), funding_map[asset])
        gross_ret = float(row["gross_ret"])
        gross_factor = 1.0 + gross_ret
        entry_slip = slip_bps_for_side(row, profile, "entry") / 10000.0
        exit_slip = slip_bps_for_side(row, profile, "exit") / 10000.0
        entry_fee = fee_bps_for_side(int(row["entry_maker"]), profile) / 10000.0
        exit_fee = fee_bps_for_side(int(row["exit_maker"]), profile) / 10000.0
        net_factor = gross_factor * (1.0 - entry_slip) * (1.0 - exit_slip) * (1.0 - entry_fee) * (1.0 - exit_fee) * funding_factor
        rows.append(
            {
                **row.to_dict(),
                "profile": profile_name,
                "entry_fee_bps_real": entry_fee * 10000.0,
                "exit_fee_bps_real": exit_fee * 10000.0,
                "entry_slip_bps_real": entry_slip * 10000.0,
                "exit_slip_bps_real": exit_slip * 10000.0,
                "funding_events": funding_events,
                "funding_rate_sum": funding_rate_sum,
                "funding_net_ret": funding_factor - 1.0,
                "net_ret_unified": float(net_factor - 1.0),
            }
        )
    return pd.DataFrame(rows)


def summarize_profile(trades: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    overall_rows: list[dict[str, object]] = []
    asset_rows: list[dict[str, object]] = []
    for profile_name in PROFILE_ORDER:
        prof_df = trades[trades["profile"] == profile_name].copy()
        for scenario in FOCUS_SCENARIOS:
            scoped = prof_df[prof_df["scenario"] == scenario].copy()
            if scoped.empty:
                continue
            per_asset_rows = []
            for asset in ASSETS.keys():
                part = scoped[scoped["asset"] == asset].copy()
                if part.empty:
                    row = {
                        "profile": profile_name,
                        "scenario": scenario,
                        "asset": asset,
                        "trades": 0,
                        "total_return": 0.0,
                        "win_rate": np.nan,
                        "avg_net_ret": np.nan,
                        "avg_hold_minutes": np.nan,
                        "entry_maker_fill_rate": np.nan,
                        "exit_maker_fill_rate": np.nan,
                        "avg_funding_events": np.nan,
                        "avg_funding_net_ret": np.nan,
                        "avg_total_fees_bps": np.nan,
                        "avg_total_slippage_bps": np.nan,
                    }
                else:
                    row = {
                        "profile": profile_name,
                        "scenario": scenario,
                        "asset": asset,
                        "trades": int(len(part)),
                        "total_return": float((1.0 + part["net_ret_unified"]).prod() - 1.0),
                        "win_rate": float((part["net_ret_unified"] > 0).mean()),
                        "avg_net_ret": float(part["net_ret_unified"].mean()),
                        "avg_hold_minutes": float(part["hold_minutes"].mean()),
                        "entry_maker_fill_rate": float(part["entry_maker"].mean()),
                        "exit_maker_fill_rate": float(part["exit_maker"].mean()),
                        "avg_funding_events": float(part["funding_events"].mean()),
                        "avg_funding_net_ret": float(part["funding_net_ret"].mean()),
                        "avg_total_fees_bps": float((part["entry_fee_bps_real"] + part["exit_fee_bps_real"]).mean()),
                        "avg_total_slippage_bps": float((part["entry_slip_bps_real"] + part["exit_slip_bps_real"]).mean()),
                    }
                per_asset_rows.append(row)
                asset_rows.append(row)
            asset_df = pd.DataFrame(per_asset_rows)
            totals = asset_df["total_return"].to_numpy(dtype=float)
            overall_rows.append(
                {
                    "profile": profile_name,
                    "scenario": scenario,
                    "mean_total_return": float(np.nanmean(totals)),
                    "positive_asset_ratio": float(np.nanmean(totals > 0)),
                    "mean_trades": float(asset_df["trades"].mean()),
                    "mean_win_rate": float(asset_df["win_rate"].mean()),
                    "mean_avg_net_ret": float(asset_df["avg_net_ret"].mean()),
                    "mean_hold_minutes": float(asset_df["avg_hold_minutes"].mean()),
                    "mean_entry_maker_fill_rate": float(asset_df["entry_maker_fill_rate"].mean()),
                    "mean_exit_maker_fill_rate": float(asset_df["exit_maker_fill_rate"].mean()),
                    "mean_funding_events": float(asset_df["avg_funding_events"].mean()),
                    "mean_funding_net_ret": float(asset_df["avg_funding_net_ret"].mean()),
                    "mean_total_fees_bps": float(asset_df["avg_total_fees_bps"].mean()),
                    "mean_total_slippage_bps": float(asset_df["avg_total_slippage_bps"].mean()),
                }
            )
    return pd.DataFrame(overall_rows), pd.DataFrame(asset_rows)


def inject_section(report_path: Path, html_block: str) -> None:
    html = report_path.read_text(encoding="utf-8")
    start_marker = f"<!-- {MARKER_ID}:start -->"
    end_marker = f"<!-- {MARKER_ID}:end -->"
    wrapped = f"{start_marker}\n{html_block}\n{end_marker}"
    if start_marker in html and end_marker in html:
        left = html.split(start_marker)[0]
        right = html.split(end_marker, 1)[1]
        html = left + wrapped + right
    else:
        html = html.replace("</body>", wrapped + "\n</body>")
    report_path.write_text(html, encoding="utf-8")


def build_notes(overall_df: pd.DataFrame) -> tuple[str, list[str]]:
    base_df = overall_df[overall_df["profile"] == "vip0_base"].copy().sort_values("mean_total_return", ascending=False)
    stress_df = overall_df[overall_df["profile"] == "vip0_stress"].copy().sort_values("mean_total_return", ascending=False)
    best_base = base_df.iloc[0]
    best_stress = stress_df.iloc[0]
    best_oco = base_df[base_df["scenario"].str.contains("tp")].iloc[0]
    fixed4 = base_df[base_df["scenario"] == "fixed_hold_4_taker"].iloc[0]
    fixed8 = base_df[base_df["scenario"] == "baseline_taker_fixed8"].iloc[0]
    headline = (
        f"统一到 Binance perp VIP0 + maker/taker + slippage + 实际持仓 funding 后，base 口径下 raw 收益最高的仍是 {SCENARIO_LABELS[str(best_base['scenario'])]}（mean_total_return≈{pct(best_base['mean_total_return'])}）；"
        f"如果只看可预埋 OCO 结构，当前最强的是 {SCENARIO_LABELS[str(best_oco['scenario'])]}（≈{pct(best_oco['mean_total_return'])}）。"
    )
    notes = [
        f"把成本层统一后，fixed-hold 仍然强，但 OCO 版本没有被成本直接打死：fixed 4x15m≈{pct(fixed4['mean_total_return'])}，fixed 8x15m≈{pct(fixed8['mean_total_return'])}，最佳 OCO≈{pct(best_oco['mean_total_return'])}。这说明 32b 的核心 edge 不是纯靠理想化成交撑出来的。",
        f"在这组真实持仓时长下，funding 的实际影响比前面 48h 假设小得多：base 口径下各候选的 mean_funding_events 通常接近 0，说明 ATR/OCO 这类短持仓结构主要该盯 fee + slippage，而不是先被 funding 吃死。",
        f"压力档（更高 taker/stop slippage）下，当前最强方案变成 {SCENARIO_LABELS[str(best_stress['scenario'])]}（≈{pct(best_stress['mean_total_return'])}）。如果 base 和 stress 的头部名单高度重合，说明这条线对成本假设不是一碰就碎。",
    ]
    return headline, notes


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank 32b unified cost simulation.")
    parser.parse_args()

    trades = load_trade_universe()
    funding_map = load_funding_map()

    profiled = pd.concat([apply_profile(trades, funding_map, name, PROFILE_CONFIGS[name]) for name in PROFILE_ORDER], ignore_index=True)
    overall_df, asset_df = summarize_profile(profiled)

    overall_df["profile_label"] = overall_df["profile"].map(lambda x: PROFILE_CONFIGS[x]["label"])
    overall_df["scenario_label"] = overall_df["scenario"].map(SCENARIO_LABELS)
    asset_df["profile_label"] = asset_df["profile"].map(lambda x: PROFILE_CONFIGS[x]["label"])
    asset_df["scenario_label"] = asset_df["scenario"].map(SCENARIO_LABELS)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    headline, notes = build_notes(overall_df)

    base_top = overall_df[overall_df["profile"] == "vip0_base"].sort_values("mean_total_return", ascending=False).reset_index(drop=True)
    stress_top = overall_df[overall_df["profile"] == "vip0_stress"].sort_values("mean_total_return", ascending=False).reset_index(drop=True)
    focus_compare = overall_df[overall_df["scenario"].isin(FOCUS_SCENARIOS)].copy()
    focus_compare["profile"] = pd.Categorical(focus_compare["profile"], categories=PROFILE_ORDER, ordered=True)
    focus_compare["scenario"] = pd.Categorical(focus_compare["scenario"], categories=FOCUS_SCENARIOS, ordered=True)
    focus_compare = focus_compare.sort_values(["scenario", "profile"]).reset_index(drop=True)
    focus_compare["profile_label"] = focus_compare["profile"].map(lambda x: PROFILE_CONFIGS[x]["label"])
    focus_compare["scenario_label"] = focus_compare["scenario"].map(SCENARIO_LABELS)

    asset_focus = asset_df[(asset_df["profile"] == "vip0_base") & (asset_df["scenario"].isin(["fixed_hold_4_taker", "maker2bps_tp1.25_sl1.00_to8", "maker2bps_tp1.00_sl1.00_to16"]))].copy()
    asset_focus["scenario"] = pd.Categorical(asset_focus["scenario"], categories=["fixed_hold_4_taker", "maker2bps_tp1.25_sl1.00_to8", "maker2bps_tp1.00_sl1.00_to16"], ordered=True)
    asset_focus = asset_focus.sort_values(["scenario", "asset"]).reset_index(drop=True)
    asset_focus["scenario_label"] = asset_focus["scenario"].astype(str).map(SCENARIO_LABELS)

    assumptions_df = pd.DataFrame([
        {"profile": PROFILE_CONFIGS[name]["label"], **{k: v for k, v in PROFILE_CONFIGS[name].items() if k != "label"}} for name in PROFILE_ORDER
    ])

    profiled_out = profiled.copy()
    for col in ["entry_ts", "exit_ts"]:
        profiled_out[col] = pd.to_datetime(profiled_out[col], utc=True).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    overall_df.to_csv(ART_DIR / f"unified_cost_round3_{DAYS}d_overall.csv", index=False)
    asset_df.to_csv(ART_DIR / f"unified_cost_round3_{DAYS}d_asset.csv", index=False)
    profiled_out.to_csv(ART_DIR / f"unified_cost_round3_{DAYS}d_trades.csv", index=False)

    html_block = f"""
  <div class='card'>
    <h2>unified cost simulation（新增）</h2>
    <p class='muted'>新增时间：{escape(generated_at)} ｜ 这轮把成本层统一到同一把尺子：Binance perp VIP0 fee、maker/taker 区分、实际持仓 funding、进出场 slippage、post-only fallback、OCO 成交口径。</p>
    <p><b>{escape(headline)}</b></p>
    <h3>统一成本假设</h3>
    {render_table(assumptions_df[["profile","maker_fee_bps","taker_fee_bps","maker_slip_bps","taker_entry_slip_bps","taker_exit_slip_bps","stop_slip_bps","timeout_slip_bps"]], digits_cols={"maker_fee_bps":1,"taker_fee_bps":1,"maker_slip_bps":1,"taker_entry_slip_bps":1,"taker_exit_slip_bps":1,"stop_slip_bps":1,"timeout_slip_bps":1})}
    <p class='muted'>说明：maker 口径按 post-only resting order；maker-first entry 若在 TTL 内未成交，则 fallback 为 taker。OCO 冲突（同一根 5m 同时触发 TP/SL）统一按保守口径：stop first。</p>
    <h3>VIP0 base：统一成本后头部方案</h3>
    {render_table(base_top[["scenario_label","mean_total_return","positive_asset_ratio","mean_win_rate","mean_hold_minutes","mean_entry_maker_fill_rate","mean_exit_maker_fill_rate","mean_funding_events","mean_funding_net_ret","mean_total_fees_bps","mean_total_slippage_bps"]].head(10), percent_cols={"mean_total_return","positive_asset_ratio","mean_win_rate","mean_entry_maker_fill_rate","mean_exit_maker_fill_rate","mean_funding_net_ret"}, digits_cols={"mean_hold_minutes":1, "mean_funding_events":2, "mean_total_fees_bps":2, "mean_total_slippage_bps":2})}
    <h3>base vs stress：关键候选同尺对照</h3>
    {render_table(focus_compare[["scenario_label","profile_label","mean_total_return","mean_win_rate","mean_hold_minutes","mean_funding_events","mean_total_fees_bps","mean_total_slippage_bps"]], percent_cols={"mean_total_return","mean_win_rate"}, digits_cols={"mean_hold_minutes":1, "mean_funding_events":2, "mean_total_fees_bps":2, "mean_total_slippage_bps":2})}
    <h3>VIP0 base：fixed-hold vs OCO 分资产</h3>
    {render_table(asset_focus[["scenario_label","asset","total_return","win_rate","avg_net_ret","avg_hold_minutes","avg_funding_events","avg_total_fees_bps","avg_total_slippage_bps"]], percent_cols={"total_return","win_rate","avg_net_ret"}, digits_cols={"avg_hold_minutes":1, "avg_funding_events":2, "avg_total_fees_bps":2, "avg_total_slippage_bps":2})}
    <h3>reader-facing 结论</h3>
    <ul>{''.join(f'<li>{escape(note)}</li>' for note in notes)}</ul>
    <p class='muted'>artifact：<code>unified_cost_round3_{DAYS}d_overall.csv</code>、<code>unified_cost_round3_{DAYS}d_asset.csv</code>、<code>unified_cost_round3_{DAYS}d_trades.csv</code></p>
  </div>
"""

    for path in [SITE_DIR / "report.html", READING_PATH]:
        inject_section(path, html_block)

    print(
        {
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "rows_in": int(len(trades)),
            "rows_out": int(len(profiled)),
            "overall_rows": int(len(overall_df)),
            "asset_rows": int(len(asset_df)),
        }
    )


if __name__ == "__main__":
    main()
