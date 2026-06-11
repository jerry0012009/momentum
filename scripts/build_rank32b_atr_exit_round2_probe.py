#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank32b_slope_floor_continuation_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank32b_slope_floor_continuation_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "trendline_alpha_scout" / "rank32b_slope_floor_continuation_clean_replication.html"
EXEC_SCRIPT = ROOT / "scripts" / "build_rank32b_execution_probe.py"
EXT_SCRIPT = ROOT / "scripts" / "build_rank32b_extended_history_probe.py"
PERP_SCRIPT = ROOT / "scripts" / "build_rank32b_perp_funding_probe.py"

DEFAULT_DAYS = 1825
TP_MULTS = [0.75, 1.00, 1.25]
SL_MULTS = [0.50, 0.75, 1.00]
TIMEOUT_15M_BARS = [8, 16]
ENTRY_SCENARIOS = [
    ("taker", 0.0),
    ("maker2", 2.0),
]
MARKER_ID = "rank32b-atr-exit-round2-1825d"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


exec_mod = load_module(EXEC_SCRIPT, "rank32b_exec_mod_round2")
ext_mod = load_module(EXT_SCRIPT, "rank32b_ext_mod_round2")
perp_mod = load_module(PERP_SCRIPT, "rank32b_perp_mod_round2")


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


def scenario_name(entry_style: str, offset_bps: float, tp_mult: float, sl_mult: float, timeout_15m: int) -> str:
    entry_tag = "taker" if entry_style == "taker" else f"maker{int(offset_bps)}bps"
    return f"{entry_tag}_tp{tp_mult:.2f}_sl{sl_mult:.2f}_to{timeout_15m}"


def scenario_label(name: str) -> str:
    left, tp, sl, timeout = name.split("_")
    entry_text = "taker 入场"
    if left.startswith("maker"):
        bps = left.replace("maker", "").replace("bps", "")
        entry_text = f"maker-first 入场 {bps}bps"
    tp_text = tp.replace("tp", "")
    sl_text = sl.replace("sl", "")
    to_text = timeout.replace("to", "")
    return f"{entry_text} + TP {tp_text} ATR / SL {sl_text} ATR / timeout {to_text}x15m"


def simulate_atr_oco_exit(
    sub_df: pd.DataFrame,
    fill_idx: int,
    fill_px: float,
    direction_sign: int,
    atr_value: float,
    tp_mult: float,
    sl_mult: float,
    timeout_15m_bars: int,
) -> dict[str, object] | None:
    if not np.isfinite(atr_value) or atr_value <= 0:
        return None
    timeout_5m_bars = int(timeout_15m_bars * 3)
    end_idx = min(len(sub_df) - 1, fill_idx + timeout_5m_bars - 1)
    target_px = float(fill_px + direction_sign * tp_mult * atr_value)
    stop_px = float(fill_px - direction_sign * sl_mult * atr_value)

    for idx in range(fill_idx, end_idx + 1):
        bar = sub_df.iloc[idx]
        if direction_sign > 0:
            hit_tp = float(bar["high"]) >= target_px
            hit_sl = float(bar["low"]) <= stop_px
        else:
            hit_tp = float(bar["low"]) <= target_px
            hit_sl = float(bar["high"]) >= stop_px

        if hit_tp and hit_sl:
            # 5m OHLC path ambiguity: take the conservative assumption (stop first)
            return {
                "exit_idx": int(idx),
                "exit_ts": pd.to_datetime(bar["timestamp"], utc=True),
                "exit_px": stop_px,
                "exit_fee_bps": exec_mod.TAKER_FEE_BPS,
                "exit_maker": 0,
                "exit_type": "conflict_stop_first",
                "target_hit": 0,
                "stop_hit": 1,
                "same_bar_conflict": 1,
                "hold_minutes": int((idx - fill_idx + 1) * 5),
            }
        if hit_tp:
            return {
                "exit_idx": int(idx),
                "exit_ts": pd.to_datetime(bar["timestamp"], utc=True),
                "exit_px": target_px,
                "exit_fee_bps": exec_mod.MAKER_FEE_BPS,
                "exit_maker": 1,
                "exit_type": "target_limit",
                "target_hit": 1,
                "stop_hit": 0,
                "same_bar_conflict": 0,
                "hold_minutes": int((idx - fill_idx + 1) * 5),
            }
        if hit_sl:
            return {
                "exit_idx": int(idx),
                "exit_ts": pd.to_datetime(bar["timestamp"], utc=True),
                "exit_px": stop_px,
                "exit_fee_bps": exec_mod.TAKER_FEE_BPS,
                "exit_maker": 0,
                "exit_type": "stop_loss",
                "target_hit": 0,
                "stop_hit": 1,
                "same_bar_conflict": 0,
                "hold_minutes": int((idx - fill_idx + 1) * 5),
            }

    bar = sub_df.iloc[end_idx]
    return {
        "exit_idx": int(end_idx),
        "exit_ts": pd.to_datetime(bar["timestamp"], utc=True),
        "exit_px": float(bar["close"]),
        "exit_fee_bps": exec_mod.TAKER_FEE_BPS,
        "exit_maker": 0,
        "exit_type": "timeout_close",
        "target_hit": 0,
        "stop_hit": 0,
        "same_bar_conflict": 0,
        "hold_minutes": int((end_idx - fill_idx + 1) * 5),
    }


def summarize_rows(trades: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    asset_rows: list[dict[str, object]] = []
    overall_rows: list[dict[str, object]] = []
    if trades.empty:
        return pd.DataFrame(), pd.DataFrame()

    scenario_order = list(dict.fromkeys(trades["scenario"].tolist()))
    for scenario in scenario_order:
        scoped = trades[trades["scenario"] == scenario].copy()
        per_asset = []
        for asset in exec_mod.ASSETS.keys():
            part = scoped[scoped["asset"] == asset].copy()
            if part.empty:
                row = {
                    "scenario": scenario,
                    "asset": asset,
                    "trades": 0,
                    "total_return": 0.0,
                    "win_rate": np.nan,
                    "avg_net_ret": np.nan,
                    "avg_hold_minutes": np.nan,
                    "entry_maker_fill_rate": np.nan,
                    "exit_maker_fill_rate": np.nan,
                    "target_hit_rate": np.nan,
                    "stop_hit_rate": np.nan,
                    "timeout_rate": np.nan,
                    "same_bar_conflict_rate": np.nan,
                }
            else:
                row = {
                    "scenario": scenario,
                    "asset": asset,
                    "trades": int(len(part)),
                    "total_return": float((1.0 + part["net_ret"]).prod() - 1.0),
                    "win_rate": float((part["net_ret"] > 0).mean()),
                    "avg_net_ret": float(part["net_ret"].mean()),
                    "avg_hold_minutes": float(part["hold_minutes"].mean()),
                    "entry_maker_fill_rate": float(part["entry_maker"].mean()),
                    "exit_maker_fill_rate": float(part["exit_maker"].mean()),
                    "target_hit_rate": float(part["target_hit"].mean()),
                    "stop_hit_rate": float(part["stop_hit"].mean()),
                    "timeout_rate": float((part["exit_type"] == "timeout_close").mean()),
                    "same_bar_conflict_rate": float(part["same_bar_conflict"].mean()),
                }
            per_asset.append(row)
            asset_rows.append(row)
        asset_df = pd.DataFrame(per_asset)
        totals = asset_df["total_return"].to_numpy(dtype=float)
        overall_rows.append(
            {
                "scenario": scenario,
                "mean_total_return": float(np.nanmean(totals)) if len(totals) else np.nan,
                "positive_asset_ratio": float(np.nanmean(totals > 0)) if len(totals) else np.nan,
                "mean_trades": float(asset_df["trades"].mean()) if len(asset_df) else np.nan,
                "mean_win_rate": float(asset_df["win_rate"].mean()) if len(asset_df) else np.nan,
                "mean_avg_net_ret": float(asset_df["avg_net_ret"].mean()) if len(asset_df) else np.nan,
                "mean_hold_minutes": float(asset_df["avg_hold_minutes"].mean()) if len(asset_df) else np.nan,
                "mean_entry_maker_fill_rate": float(asset_df["entry_maker_fill_rate"].mean()) if len(asset_df) else np.nan,
                "mean_exit_maker_fill_rate": float(asset_df["exit_maker_fill_rate"].mean()) if len(asset_df) else np.nan,
                "mean_target_hit_rate": float(asset_df["target_hit_rate"].mean()) if len(asset_df) else np.nan,
                "mean_stop_hit_rate": float(asset_df["stop_hit_rate"].mean()) if len(asset_df) else np.nan,
                "mean_timeout_rate": float(asset_df["timeout_rate"].mean()) if len(asset_df) else np.nan,
                "mean_same_bar_conflict_rate": float(asset_df["same_bar_conflict_rate"].mean()) if len(asset_df) else np.nan,
            }
        )
    return pd.DataFrame(overall_rows), pd.DataFrame(asset_rows)


def inject_section(report_path: Path, html_block: str, marker_id: str = MARKER_ID) -> None:
    html = report_path.read_text(encoding="utf-8")
    start_marker = f"<!-- {marker_id}:start -->"
    end_marker = f"<!-- {marker_id}:end -->"
    wrapped = f"{start_marker}\n{html_block}\n{end_marker}"
    if start_marker in html and end_marker in html:
        left = html.split(start_marker)[0]
        right = html.split(end_marker, 1)[1]
        html = left + wrapped + right
    else:
        html = html.replace("</body>", wrapped + "\n</body>")
    report_path.write_text(html, encoding="utf-8")


def build_notes(overall_df: pd.DataFrame, compare_df: pd.DataFrame | None = None) -> tuple[str, list[str], list[str]]:
    best = overall_df.sort_values("mean_total_return", ascending=False).iloc[0]
    best_name = str(best["scenario"])
    best_taker = overall_df[overall_df["scenario"].str.startswith("taker_")].sort_values("mean_total_return", ascending=False).iloc[0]
    best_maker = overall_df[overall_df["scenario"].str.startswith("maker2bps_")].sort_values("mean_total_return", ascending=False).iloc[0]

    headline = (
        f"第二轮把 ATR 离场改成更像真实 desk 会预埋的 OCO 结构后，当前最强方案是 {scenario_label(best_name)}，"
        f"mean_total_return≈{pct(best['mean_total_return'])}、平均持有≈{num(best['mean_hold_minutes'],1)} 分钟、"
        f"target hit≈{pct(best['mean_target_hit_rate'])}、stop hit≈{pct(best['mean_stop_hit_rate'])}。"
    )

    notes = [
        f"如果只看 taker 入场，当前最好的 ATR-OCO 方案是 {scenario_label(str(best_taker['scenario']))}；它比‘只有 ATR target、没有 stop’更像真实挂单结构，因为你可以在入场后同时预埋 TP 和保护性 SL。",
        f"如果允许一个温和的 maker-first 入场（2bps/15m TTL），当前最好的 ATR-OCO 方案是 {scenario_label(str(best_maker['scenario']))}；这说明 entry 端争取一点价格改善，和 ATR 预挂离场是能叠加的。",
        f"这轮还额外统计了 same-bar conflict（同一根 5m 里 TP/SL 都触发）比例；如果这个比例很低，说明用 5m OHLC 做 OCO 仿真的歧义不算大，结果更可信。",
    ]
    if compare_df is not None and not compare_df.empty:
        parts: list[str] = []
        for _, row in compare_df.iterrows():
            parts.append(
                f"{row['entry_style']}：同样是 TP 1.0 ATR + timeout 16x15m，"
                f"无 stop≈{pct(row['no_stop_mean_total_return'])}，"
                f"加 1.0 ATR stop 后≈{pct(row['with_stop_mean_total_return'])}，"
                f"增量≈{pct(row['mean_total_return_delta'])}；"
                f"平均持有从 {num(row['no_stop_mean_hold_minutes'],1)} 缩到 {num(row['with_stop_mean_hold_minutes'],1)} 分钟，"
                f"但 win rate 也从 {pct(row['no_stop_mean_win_rate'])} 降到 {pct(row['with_stop_mean_win_rate'])}。"
            )
        notes.append(
            "同口径直比（只改是否加 1.0 ATR protective stop）显示：" + "；".join(parts) + " 这说明 stop 改善的是总收益与资金周转，不是单纯把胜率抬高。"
        )

    shortlist = []
    for _, row in overall_df.sort_values("mean_total_return", ascending=False).head(3).iterrows():
        shortlist.append(
            f"{scenario_label(str(row['scenario']))} ｜ return≈{pct(row['mean_total_return'])} ｜ hold≈{num(row['mean_hold_minutes'],1)} 分钟 ｜ TP≈{pct(row['mean_target_hit_rate'])} ｜ SL≈{pct(row['mean_stop_hit_rate'])}"
        )
    return headline, notes, shortlist


def build_no_stop_compare(days: int, overall_df: pd.DataFrame) -> pd.DataFrame:
    exec_path = ART_DIR / f"execution_probe_{days}d_execution_scenarios_overall.csv"
    if not exec_path.exists():
        return pd.DataFrame()
    exec_overall = pd.read_csv(exec_path)
    if exec_overall.empty or "scenario" not in exec_overall.columns:
        return pd.DataFrame()

    compare_pairs = [
        {
            "entry_style": "taker entry",
            "no_stop_scenario": "baseline_taker_tp1atr_timeout16",
            "with_stop_scenario": "taker_tp1.00_sl1.00_to16",
        },
        {
            "entry_style": "maker-first 2bps / 15m TTL",
            "no_stop_scenario": "maker_entry_2bps_ttl15m_tp1atr_timeout16",
            "with_stop_scenario": "maker2bps_tp1.00_sl1.00_to16",
        },
    ]

    exec_view = exec_overall.set_index("scenario")
    oco_view = overall_df.set_index("scenario")
    rows: list[dict[str, object]] = []
    for pair in compare_pairs:
        if pair["no_stop_scenario"] not in exec_view.index or pair["with_stop_scenario"] not in oco_view.index:
            continue
        no_stop = exec_view.loc[pair["no_stop_scenario"]]
        with_stop = oco_view.loc[pair["with_stop_scenario"]]
        rows.append(
            {
                "entry_style": pair["entry_style"],
                "no_stop_label": str(no_stop.get("scenario_label") or no_stop.get("scenario") or pair["no_stop_scenario"]),
                "with_stop_label": scenario_label(pair["with_stop_scenario"]),
                "no_stop_mean_total_return": float(no_stop["mean_total_return"]),
                "with_stop_mean_total_return": float(with_stop["mean_total_return"]),
                "mean_total_return_delta": float(with_stop["mean_total_return"]) - float(no_stop["mean_total_return"]),
                "no_stop_mean_win_rate": float(no_stop["mean_win_rate"]),
                "with_stop_mean_win_rate": float(with_stop["mean_win_rate"]),
                "no_stop_mean_hold_minutes": float(no_stop["mean_hold_minutes"]),
                "with_stop_mean_hold_minutes": float(with_stop["mean_hold_minutes"]),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Round-2 ATR exit research for Rank 32b.")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS)
    args = parser.parse_args()
    days = int(args.days)

    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    trade_rows: list[pd.DataFrame] = []
    subbars_map: dict[str, pd.DataFrame] = {}
    ts_map: dict[str, np.ndarray] = {}
    meta_rows: list[dict[str, object]] = []

    for asset, symbol in exec_mod.ASSETS.items():
        bars_15m = perp_mod.load_or_fetch_perp_bars(symbol, days=days, refresh=False)
        bars_5m = exec_mod.load_or_fetch_perp_5m(symbol, days=days, refresh=False)
        frame = ext_mod.build_rank32b_frame_from_bars(asset, bars_15m)
        frame["atr14"] = exec_mod.compute_atr(frame)
        signals = exec_mod.build_signal_trades(frame, asset)
        trade_rows.append(signals)
        subbars = bars_5m.copy().sort_values("timestamp").reset_index(drop=True)
        subbars_map[asset] = subbars
        ts_map[asset] = subbars["timestamp"].to_numpy(dtype="datetime64[ns]")
        meta_rows.append(
            {
                "asset": asset,
                "symbol": symbol,
                "signals": int(len(signals)),
                "bars_15m": int(len(bars_15m)),
                "bars_5m": int(len(bars_5m)),
            }
        )

    trades = pd.concat([df for df in trade_rows if not df.empty], ignore_index=True) if trade_rows else pd.DataFrame()
    rows: list[dict[str, object]] = []

    for _, trade in trades.iterrows():
        asset = str(trade["asset"])
        sub_df = subbars_map[asset]
        ts_array = ts_map[asset]
        entry_ts = pd.to_datetime(trade["entry_ts"], utc=True)
        direction_sign = int(trade["direction_sign"])
        atr_value = float(trade["atr14_entry"])
        for entry_style, offset_bps in ENTRY_SCENARIOS:
            entry_res = exec_mod.simulate_entry(
                sub_df,
                ts_array,
                entry_ts,
                direction_sign,
                entry_style="taker" if entry_style == "taker" else "maker",
                entry_offset_bps=float(offset_bps),
                ttl_bars=exec_mod.ENTRY_TTL_5M_BARS,
            )
            if entry_res is None:
                continue
            for tp_mult in TP_MULTS:
                for sl_mult in SL_MULTS:
                    for timeout_15m in TIMEOUT_15M_BARS:
                        exit_res = simulate_atr_oco_exit(
                            sub_df,
                            int(entry_res["fill_idx"]),
                            float(entry_res["fill_px"]),
                            direction_sign,
                            atr_value,
                            float(tp_mult),
                            float(sl_mult),
                            int(timeout_15m),
                        )
                        if exit_res is None:
                            continue
                        gross_ret = exec_mod.gross_return(float(entry_res["fill_px"]), float(exit_res["exit_px"]), direction_sign)
                        rows.append(
                            {
                                "asset": asset,
                                "direction": str(trade["direction"]),
                                "scenario": scenario_name(entry_style, offset_bps, tp_mult, sl_mult, timeout_15m),
                                "entry_ts": pd.to_datetime(entry_res["fill_ts"], utc=True),
                                "exit_ts": pd.to_datetime(exit_res["exit_ts"], utc=True),
                                "entry_price": float(entry_res["fill_px"]),
                                "exit_price": float(exit_res["exit_px"]),
                                "gross_ret": gross_ret,
                                "net_ret": exec_mod.apply_fees(gross_ret, float(entry_res["entry_fee_bps"]), float(exit_res["exit_fee_bps"])),
                                "entry_maker": int(entry_res["entry_maker"]),
                                "exit_maker": int(exit_res["exit_maker"]),
                                "entry_offset_bps": float(entry_res["entry_offset_bps"]),
                                "target_hit": int(exit_res["target_hit"]),
                                "stop_hit": int(exit_res["stop_hit"]),
                                "same_bar_conflict": int(exit_res["same_bar_conflict"]),
                                "hold_minutes": int(exit_res["hold_minutes"]),
                                "exit_type": str(exit_res["exit_type"]),
                            }
                        )

    oco_trades = pd.DataFrame(rows)
    overall_df, asset_df = summarize_rows(oco_trades)
    overall_df["label"] = overall_df["scenario"].map(scenario_label)
    asset_df["label"] = asset_df["scenario"].map(scenario_label)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    overall_top = overall_df.sort_values("mean_total_return", ascending=False).head(12).copy()
    asset_focus_scenarios = list(overall_top["scenario"].head(4))
    asset_focus = asset_df[asset_df["scenario"].isin(asset_focus_scenarios)].copy()
    if not asset_focus.empty:
        asset_focus["scenario"] = pd.Categorical(asset_focus["scenario"], categories=asset_focus_scenarios, ordered=True)
        asset_focus = asset_focus.sort_values(["scenario", "asset"]).reset_index(drop=True)

    overall_top["label"] = overall_top["scenario"].map(scenario_label)
    if not asset_focus.empty:
        asset_focus["label"] = asset_focus["scenario"].astype(str).map(scenario_label)

    compare_df = build_no_stop_compare(days, overall_df)
    headline, notes, shortlist = build_notes(overall_df, compare_df)

    compare_html = ""
    if compare_df is not None and not compare_df.empty:
        compare_html = (
            "<h3>与‘只有 TP + timeout、无止损’同口径对照</h3>"
            + render_table(
                compare_df[
                    [
                        "entry_style",
                        "no_stop_mean_total_return",
                        "with_stop_mean_total_return",
                        "mean_total_return_delta",
                        "no_stop_mean_win_rate",
                        "with_stop_mean_win_rate",
                        "no_stop_mean_hold_minutes",
                        "with_stop_mean_hold_minutes",
                    ]
                ],
                percent_cols={
                    "no_stop_mean_total_return",
                    "with_stop_mean_total_return",
                    "mean_total_return_delta",
                    "no_stop_mean_win_rate",
                    "with_stop_mean_win_rate",
                },
                digits_cols={
                    "no_stop_mean_hold_minutes": 1,
                    "with_stop_mean_hold_minutes": 1,
                },
            )
            + "<p class='muted'>读法：这里固定同一 entry 口径、同一 TP=1.0 ATR、同一 timeout=16x15m，只比较‘是否额外加 1.0 ATR protective stop’。如果 mean_total_return 更高、平均持有更短，但 win rate 下降，说明 stop 的价值主要在切断坏单和释放资金占用，而不是单纯抬高胜率。</p>"
        )

    # persist artifacts
    trades_out = oco_trades.copy()
    for col in ["entry_ts", "exit_ts"]:
        if col in trades_out.columns:
            trades_out[col] = pd.to_datetime(trades_out[col], utc=True).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    pd.DataFrame(meta_rows).to_csv(ART_DIR / f"atr_exit_round2_{days}d_meta.csv", index=False)
    overall_df.to_csv(ART_DIR / f"atr_exit_round2_{days}d_overall.csv", index=False)
    asset_df.to_csv(ART_DIR / f"atr_exit_round2_{days}d_asset.csv", index=False)
    trades_out.to_csv(ART_DIR / f"atr_exit_round2_{days}d_trades.csv", index=False)

    html_block = f"""
  <div class='card'>
    <h2>ATR exit round 2（新增）</h2>
    <p class='muted'>新增时间：{escape(generated_at)} ｜ 样本：Binance perp 15m 信号 + 5m 执行仿真 ｜ 这轮只做一件事：把 ATR 离场改成更像实盘可预埋的 OCO（TP limit + protective stop + timeout）。</p>
    <p><b>{escape(headline)}</b></p>
    <h3>Top ATR-OCO 方案（overall）</h3>
    {render_table(overall_top[["label","mean_total_return","positive_asset_ratio","mean_trades","mean_win_rate","mean_hold_minutes","mean_entry_maker_fill_rate","mean_exit_maker_fill_rate","mean_target_hit_rate","mean_stop_hit_rate","mean_timeout_rate","mean_same_bar_conflict_rate"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_win_rate","mean_entry_maker_fill_rate","mean_exit_maker_fill_rate","mean_target_hit_rate","mean_stop_hit_rate","mean_timeout_rate","mean_same_bar_conflict_rate"}, digits_cols={"mean_trades":1, "mean_hold_minutes":1})}
    {compare_html}
    <h3>Top 方案分资产拆解</h3>
    {render_table(asset_focus[["label","asset","trades","total_return","win_rate","avg_net_ret","avg_hold_minutes","entry_maker_fill_rate","exit_maker_fill_rate","target_hit_rate","stop_hit_rate","same_bar_conflict_rate"]], percent_cols={"total_return","win_rate","avg_net_ret","entry_maker_fill_rate","exit_maker_fill_rate","target_hit_rate","stop_hit_rate","same_bar_conflict_rate"}, digits_cols={"trades":0, "avg_hold_minutes":1})}
    <h3>reader-facing 结论</h3>
    <ul>{''.join(f'<li>{escape(note)}</li>' for note in notes)}</ul>
    <p><b>当前 shortlist：</b></p>
    <ul>{''.join(f'<li>{escape(item)}</li>' for item in shortlist)}</ul>
    <p class='muted'>实盘解释：这轮 ATR exit 是“入场后立刻可预埋”的结构——目标止盈单是 maker limit，止损单和 timeout 是 taker protective exits。same-bar conflict 统一按保守口径处理：同一根 5m 同时打到 TP/SL 时，默认 stop first。</p>
    <p class='muted'>artifact：<code>atr_exit_round2_{days}d_overall.csv</code>、<code>atr_exit_round2_{days}d_asset.csv</code>、<code>atr_exit_round2_{days}d_trades.csv</code></p>
  </div>
"""

    for path in [SITE_DIR / "report.html", READING_PATH]:
        inject_section(path, html_block, marker_id=MARKER_ID)

    print(
        {
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "days": days,
            "signals": int(len(trades)),
            "oco_rows": int(len(oco_trades)),
            "overall_rows": int(len(overall_df)),
            "asset_rows": int(len(asset_df)),
        }
    )


if __name__ == "__main__":
    main()
