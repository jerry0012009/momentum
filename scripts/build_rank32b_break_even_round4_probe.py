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
UC_SCRIPT = ROOT / "scripts" / "build_rank32b_unified_cost_probe.py"

DAYS = 1825
MARKER_ID = "rank32b-break-even-round4-1825d"
FAMILY_CONFIGS = [
    {"name": "taker_tp1.25_sl1.00_to8", "entry_style": "taker", "entry_offset_bps": 0.0, "tp_mult": 1.25, "sl_mult": 1.00, "timeout_15m": 8},
    {"name": "maker2_tp1.25_sl1.00_to8", "entry_style": "maker", "entry_offset_bps": 2.0, "tp_mult": 1.25, "sl_mult": 1.00, "timeout_15m": 8},
    {"name": "taker_tp1.00_sl0.75_to16", "entry_style": "taker", "entry_offset_bps": 0.0, "tp_mult": 1.00, "sl_mult": 0.75, "timeout_15m": 16},
    {"name": "maker2_tp1.00_sl0.75_to16", "entry_style": "maker", "entry_offset_bps": 2.0, "tp_mult": 1.00, "sl_mult": 0.75, "timeout_15m": 16},
]
PROFILE_ORDER = ["vip0_base", "vip0_stress"]


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


exec_mod = load_module(EXEC_SCRIPT, "rank32_exec_mod_round4")
ext_mod = load_module(EXT_SCRIPT, "rank32_ext_mod_round4")
perp_mod = load_module(PERP_SCRIPT, "rank32_perp_mod_round4")
uc_mod = load_module(UC_SCRIPT, "rank32_uc_mod_round4")


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


def scenario_label(family_name: str, trigger_kind: str) -> str:
    parts = family_name.split("_")
    entry_raw = parts[0]
    tp_raw = parts[1].replace("tp", "")
    sl_raw = parts[2].replace("sl", "")
    to_raw = parts[3].replace("to", "")
    if entry_raw == "taker":
        entry_text = "taker 入场"
    else:
        entry_text = "maker-first 入场 2bps"
    base = f"{entry_text} + TP {tp_raw} ATR / SL {sl_raw} ATR / timeout {to_raw}x15m"
    if trigger_kind == "none":
        return base + " / 无 BE"
    if trigger_kind == "be_1atr":
        return base + " / BE@1ATR+cost"
    return base + " / BE@1R+cost"


def candidate_triggers(family: dict[str, float]) -> list[str]:
    if abs(float(family["sl_mult"]) - 1.0) < 1e-12:
        return ["none", "be_1atr"]
    return ["none", "be_1atr", "be_1r"]


def load_funding_abs_means() -> dict[str, float]:
    out: dict[str, float] = {}
    fmap = uc_mod.load_funding_map()
    for asset, df in fmap.items():
        out[asset] = float(df["funding_rate"].abs().mean()) if len(df) else 0.0
    return out


def compute_cost_buffer_bps(asset: str, entry_maker: bool, timeout_15m: int, profile: dict[str, float], funding_abs_mean: dict[str, float]) -> float:
    entry_cost = (profile["maker_fee_bps"] + profile["maker_slip_bps"]) if entry_maker else (profile["taker_fee_bps"] + profile["taker_entry_slip_bps"])
    exit_stop_cost = profile["taker_fee_bps"] + profile["stop_slip_bps"]
    expected_funding_bps = funding_abs_mean.get(asset, 0.0) * (timeout_15m * 15.0 / 480.0) * 10000.0
    return float(entry_cost + exit_stop_cost + expected_funding_bps)


def gross_return(entry_px: float, exit_px: float, direction_sign: int) -> float:
    return float((exit_px / entry_px - 1.0) * direction_sign)


def apply_costs(row: dict[str, object], profile: dict[str, float], funding_map: dict[str, pd.DataFrame]) -> dict[str, object]:
    entry_maker = int(row["entry_maker"])
    exit_maker = int(row["exit_maker"])
    entry_fee_bps = profile["maker_fee_bps"] if entry_maker else profile["taker_fee_bps"]
    if exit_maker:
        exit_fee_bps = profile["maker_fee_bps"]
        exit_slip_bps = profile["maker_slip_bps"]
    else:
        exit_fee_bps = profile["taker_fee_bps"]
        if row["exit_type"] in {"stop_loss", "break_even_stop", "conflict_stop_first"}:
            exit_slip_bps = profile["stop_slip_bps"]
        elif row["exit_type"] == "timeout_close":
            exit_slip_bps = profile["timeout_slip_bps"]
        else:
            exit_slip_bps = profile["taker_exit_slip_bps"]
    entry_slip_bps = profile["maker_slip_bps"] if entry_maker else profile["taker_entry_slip_bps"]
    funding_factor, funding_events, funding_rate_sum = uc_mod.funding_factor_and_stats(pd.to_datetime(row["entry_ts"], utc=True), pd.to_datetime(row["exit_ts"], utc=True), str(row["direction"]), funding_map[str(row["asset"])])
    gross_factor = 1.0 + float(row["gross_ret"])
    net_factor = gross_factor * (1.0 - entry_fee_bps / 10000.0) * (1.0 - exit_fee_bps / 10000.0) * (1.0 - entry_slip_bps / 10000.0) * (1.0 - exit_slip_bps / 10000.0) * funding_factor
    row.update(
        {
            "entry_fee_bps_real": float(entry_fee_bps),
            "exit_fee_bps_real": float(exit_fee_bps),
            "entry_slip_bps_real": float(entry_slip_bps),
            "exit_slip_bps_real": float(exit_slip_bps),
            "funding_events": int(funding_events),
            "funding_rate_sum": float(funding_rate_sum),
            "funding_net_ret": float(funding_factor - 1.0),
            "net_ret_unified": float(net_factor - 1.0),
        }
    )
    return row


def simulate_break_even_oco(
    sub_df: pd.DataFrame,
    fill_idx: int,
    fill_px: float,
    direction_sign: int,
    atr_value: float,
    tp_mult: float,
    sl_mult: float,
    timeout_15m: int,
    trigger_kind: str,
    break_even_px: float,
) -> dict[str, object] | None:
    if not np.isfinite(atr_value) or atr_value <= 0:
        return None
    timeout_5m = int(timeout_15m * 3)
    end_idx = min(len(sub_df) - 1, fill_idx + timeout_5m - 1)
    target_px = float(fill_px + direction_sign * tp_mult * atr_value)
    initial_stop_px = float(fill_px - direction_sign * sl_mult * atr_value)
    current_stop_px = initial_stop_px
    be_active = False
    be_triggered = False
    be_activation_idx = None

    trigger_px = None
    if trigger_kind == "be_1atr":
        trigger_px = float(fill_px + direction_sign * atr_value)
    elif trigger_kind == "be_1r":
        trigger_px = float(fill_px + direction_sign * sl_mult * atr_value)

    for idx in range(fill_idx, end_idx + 1):
        bar = sub_df.iloc[idx]
        if be_triggered and be_activation_idx is not None and idx >= be_activation_idx and not be_active:
            be_active = True
            current_stop_px = break_even_px

        if direction_sign > 0:
            hit_tp = float(bar["high"]) >= target_px
            hit_sl = float(bar["low"]) <= current_stop_px
        else:
            hit_tp = float(bar["low"]) <= target_px
            hit_sl = float(bar["high"]) >= current_stop_px

        if hit_tp and hit_sl:
            exit_type = "conflict_stop_first" if be_active else "conflict_stop_first"
            return {
                "exit_idx": int(idx),
                "exit_ts": pd.to_datetime(bar["timestamp"], utc=True),
                "exit_px": current_stop_px,
                "exit_maker": 0,
                "exit_type": exit_type if not be_active else "break_even_stop",
                "target_hit": 0,
                "stop_hit": 1,
                "be_triggered": int(be_triggered),
                "be_stop_hit": 1 if be_active else 0,
                "same_bar_conflict": 1,
                "hold_minutes": int((idx - fill_idx + 1) * 5),
            }
        if hit_tp:
            return {
                "exit_idx": int(idx),
                "exit_ts": pd.to_datetime(bar["timestamp"], utc=True),
                "exit_px": target_px,
                "exit_maker": 1,
                "exit_type": "target_limit",
                "target_hit": 1,
                "stop_hit": 0,
                "be_triggered": int(be_triggered),
                "be_stop_hit": 0,
                "same_bar_conflict": 0,
                "hold_minutes": int((idx - fill_idx + 1) * 5),
            }
        if hit_sl:
            return {
                "exit_idx": int(idx),
                "exit_ts": pd.to_datetime(bar["timestamp"], utc=True),
                "exit_px": current_stop_px,
                "exit_maker": 0,
                "exit_type": "break_even_stop" if be_active else "stop_loss",
                "target_hit": 0,
                "stop_hit": 1,
                "be_triggered": int(be_triggered),
                "be_stop_hit": 1 if be_active else 0,
                "same_bar_conflict": 0,
                "hold_minutes": int((idx - fill_idx + 1) * 5),
            }

        if trigger_px is not None and not be_triggered:
            if direction_sign > 0:
                hit_trigger = float(bar["high"]) >= trigger_px
            else:
                hit_trigger = float(bar["low"]) <= trigger_px
            if hit_trigger:
                be_triggered = True
                be_activation_idx = idx + 1

    bar = sub_df.iloc[end_idx]
    return {
        "exit_idx": int(end_idx),
        "exit_ts": pd.to_datetime(bar["timestamp"], utc=True),
        "exit_px": float(bar["close"]),
        "exit_maker": 0,
        "exit_type": "timeout_close",
        "target_hit": 0,
        "stop_hit": 0,
        "be_triggered": int(be_triggered),
        "be_stop_hit": 0,
        "same_bar_conflict": 0,
        "hold_minutes": int((end_idx - fill_idx + 1) * 5),
    }


def build_signal_trades() -> tuple[pd.DataFrame, dict[str, pd.DataFrame], dict[str, pd.DataFrame], dict[str, np.ndarray]]:
    trade_rows: list[pd.DataFrame] = []
    frame_map: dict[str, pd.DataFrame] = {}
    subbars_map: dict[str, pd.DataFrame] = {}
    ts_map: dict[str, np.ndarray] = {}
    for asset, symbol in exec_mod.ASSETS.items():
        bars_15m = perp_mod.load_or_fetch_perp_bars(symbol, days=DAYS, refresh=False)
        bars_5m = exec_mod.load_or_fetch_perp_5m(symbol, days=DAYS, refresh=False)
        frame = ext_mod.build_rank32b_frame_from_bars(asset, bars_15m)
        frame["atr14"] = exec_mod.compute_atr(frame)
        frame_map[asset] = frame
        subbars_map[asset] = bars_5m.copy().sort_values("timestamp").reset_index(drop=True)
        ts_map[asset] = subbars_map[asset]["timestamp"].to_numpy(dtype="datetime64[ns]")
        trade_rows.append(exec_mod.build_signal_trades(frame, asset))
    trades = pd.concat([df for df in trade_rows if not df.empty], ignore_index=True) if trade_rows else pd.DataFrame()
    return trades, frame_map, subbars_map, ts_map


def summarize(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    overall_rows: list[dict[str, object]] = []
    asset_rows: list[dict[str, object]] = []
    for profile_name in PROFILE_ORDER:
        prof = df[df["profile"] == profile_name].copy()
        scenario_order = list(dict.fromkeys(prof["scenario"].tolist()))
        for scenario in scenario_order:
            scoped = prof[prof["scenario"] == scenario].copy()
            per_asset = []
            for asset in exec_mod.ASSETS.keys():
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
                        "target_hit_rate": np.nan,
                        "stop_hit_rate": np.nan,
                        "break_even_trigger_rate": np.nan,
                        "break_even_stop_rate": np.nan,
                        "same_bar_conflict_rate": np.nan,
                        "avg_cost_buffer_bps": np.nan,
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
                        "target_hit_rate": float(part["target_hit"].mean()),
                        "stop_hit_rate": float(part["stop_hit"].mean()),
                        "break_even_trigger_rate": float(part["be_triggered"].mean()),
                        "break_even_stop_rate": float(part["be_stop_hit"].mean()),
                        "same_bar_conflict_rate": float(part["same_bar_conflict"].mean()),
                        "avg_cost_buffer_bps": float(part["cost_buffer_bps"].mean()),
                    }
                per_asset.append(row)
                asset_rows.append(row)
            asset_df = pd.DataFrame(per_asset)
            totals = asset_df["total_return"].to_numpy(dtype=float)
            overall_rows.append(
                {
                    "profile": profile_name,
                    "scenario": scenario,
                    "mean_total_return": float(np.nanmean(totals)),
                    "positive_asset_ratio": float(np.nanmean(totals > 0)),
                    "mean_win_rate": float(asset_df["win_rate"].mean()),
                    "mean_hold_minutes": float(asset_df["avg_hold_minutes"].mean()),
                    "mean_entry_maker_fill_rate": float(asset_df["entry_maker_fill_rate"].mean()),
                    "mean_exit_maker_fill_rate": float(asset_df["exit_maker_fill_rate"].mean()),
                    "mean_target_hit_rate": float(asset_df["target_hit_rate"].mean()),
                    "mean_stop_hit_rate": float(asset_df["stop_hit_rate"].mean()),
                    "mean_break_even_trigger_rate": float(asset_df["break_even_trigger_rate"].mean()),
                    "mean_break_even_stop_rate": float(asset_df["break_even_stop_rate"].mean()),
                    "mean_same_bar_conflict_rate": float(asset_df["same_bar_conflict_rate"].mean()),
                    "mean_cost_buffer_bps": float(asset_df["avg_cost_buffer_bps"].mean()),
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
    base = overall_df[overall_df["profile"] == "vip0_base"].copy().sort_values("mean_total_return", ascending=False)
    no_be = base[base["scenario"].str.endswith("__none")].sort_values("mean_total_return", ascending=False).iloc[0]
    be_best = base[~base["scenario"].str.endswith("__none")].sort_values("mean_total_return", ascending=False).iloc[0]
    maker_family_no = base[base["scenario"] == "maker2_tp1.25_sl1.00_to8__none"].iloc[0]
    maker_family_be = base[base["scenario"] == "maker2_tp1.25_sl1.00_to8__be_1atr"].iloc[0]
    taker_family_no = base[base["scenario"] == "taker_tp1.25_sl1.00_to8__none"].iloc[0]
    taker_family_be = base[base["scenario"] == "taker_tp1.25_sl1.00_to8__be_1atr"].iloc[0]
    onerto_none = base[base["scenario"] == "maker2_tp1.00_sl0.75_to16__none"].iloc[0]
    onerto_beatr = base[base["scenario"] == "maker2_tp1.00_sl0.75_to16__be_1atr"].iloc[0]
    onerto_ber = base[base["scenario"] == "maker2_tp1.00_sl0.75_to16__be_1r"].iloc[0]
    headline = (
        f"在统一成本层上加入 break-even with cost buffer 后，base 口径下当前最强的 BE 方案是 {scenario_label(*str(be_best['scenario']).split('__'))}，"
        f"mean_total_return≈{pct(be_best['mean_total_return'])}、BE trigger≈{pct(be_best['mean_break_even_trigger_rate'])}、BE stop≈{pct(be_best['mean_break_even_stop_rate'])}。"
    )
    notes = [
        f"和本轮纳入的无 BE 候选相比，当前最好无 BE 方案是 {scenario_label(*str(no_be['scenario']).split('__'))}（≈{pct(no_be['mean_total_return'])}）；最好 BE 方案≈{pct(be_best['mean_total_return'])}，说明 break-even 不是天然有害，但只在一部分 OCO 结构上真正加分。",
        f"对当前最值得做的 OCO 家族（TP 1.25 / SL 1.00 / timeout 8）来说，maker-first 版本从无 BE≈{pct(maker_family_no['mean_total_return'])} 提升到 BE@1ATR+cost≈{pct(maker_family_be['mean_total_return'])}；但 taker 版本从≈{pct(taker_family_no['mean_total_return'])} 小幅回落到≈{pct(taker_family_be['mean_total_return'])}。这说明 break-even 的价值和 entry 口径是耦合的。",
        f"对 TP 1.00 / SL 0.75 / timeout 16 这组，BE@1ATR+cost 和无 BE 几乎完全一样（≈{pct(onerto_beatr['mean_total_return'])} vs ≈{pct(onerto_none['mean_total_return'])}），因为 1ATR 触发点已经和 TP 太接近；而更早的 BE@1R+cost 反而把收益打到≈{pct(onerto_ber['mean_total_return'])}，说明 stop 抬得太早会把 continuation 的肉提前切掉。",
        f"这轮的 BE 不是抬到名义 entry，而是抬到 entry + cost buffer；平均 buffer 规模大约在 {num(be_best['mean_cost_buffer_bps'],2)} bps，已经把开平手续费、预估滑点和 funding buffer 算进去了。为避免路径偷看，BE 触发后从下一根 5m 才生效。",
    ]
    return headline, notes


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank 32b break-even round-4 probe.")
    parser.parse_args()

    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    trades, _, subbars_map, ts_map = build_signal_trades()
    funding_map = uc_mod.load_funding_map()
    funding_abs_mean = load_funding_abs_means()

    rows: list[dict[str, object]] = []
    for _, trade in trades.iterrows():
        asset = str(trade["asset"])
        sub_df = subbars_map[asset]
        ts_array = ts_map[asset]
        entry_ts = pd.to_datetime(trade["entry_ts"], utc=True)
        direction = str(trade["direction"])
        direction_sign = int(trade["direction_sign"])
        atr_value = float(trade["atr14_entry"])
        for family in FAMILY_CONFIGS:
            entry_res = exec_mod.simulate_entry(
                sub_df,
                ts_array,
                entry_ts,
                direction_sign,
                entry_style="taker" if family["entry_style"] == "taker" else "maker",
                entry_offset_bps=float(family["entry_offset_bps"]),
                ttl_bars=exec_mod.ENTRY_TTL_5M_BARS,
            )
            if entry_res is None:
                continue
            for profile_name in PROFILE_ORDER:
                profile = uc_mod.PROFILE_CONFIGS[profile_name]
                cost_buffer_bps = compute_cost_buffer_bps(asset, bool(entry_res["entry_maker"]), int(family["timeout_15m"]), profile, funding_abs_mean)
                be_px = float(entry_res["fill_px"]) * (1.0 + direction_sign * cost_buffer_bps / 10000.0)
                for trigger_kind in candidate_triggers(family):
                    exit_res = simulate_break_even_oco(
                        sub_df,
                        int(entry_res["fill_idx"]),
                        float(entry_res["fill_px"]),
                        direction_sign,
                        atr_value,
                        float(family["tp_mult"]),
                        float(family["sl_mult"]),
                        int(family["timeout_15m"]),
                        trigger_kind,
                        be_px,
                    )
                    if exit_res is None:
                        continue
                    row = {
                        "asset": asset,
                        "direction": direction,
                        "profile": profile_name,
                        "scenario": f"{family['name']}__{trigger_kind}",
                        "entry_ts": pd.to_datetime(entry_res["fill_ts"], utc=True),
                        "exit_ts": pd.to_datetime(exit_res["exit_ts"], utc=True),
                        "entry_price": float(entry_res["fill_px"]),
                        "exit_price": float(exit_res["exit_px"]),
                        "entry_maker": int(entry_res["entry_maker"]),
                        "exit_maker": int(exit_res["exit_maker"]),
                        "entry_offset_bps": float(entry_res["entry_offset_bps"]),
                        "target_hit": int(exit_res["target_hit"]),
                        "stop_hit": int(exit_res["stop_hit"]),
                        "be_triggered": int(exit_res["be_triggered"]),
                        "be_stop_hit": int(exit_res["be_stop_hit"]),
                        "same_bar_conflict": int(exit_res["same_bar_conflict"]),
                        "hold_minutes": int(exit_res["hold_minutes"]),
                        "exit_type": str(exit_res["exit_type"]),
                        "cost_buffer_bps": float(cost_buffer_bps),
                    }
                    row["gross_ret"] = gross_return(float(row["entry_price"]), float(row["exit_price"]), direction_sign)
                    row = apply_costs(row, profile, funding_map)
                    rows.append(row)

    out_df = pd.DataFrame(rows)
    overall_df, asset_df = summarize(out_df)
    overall_df["profile_label"] = overall_df["profile"].map(lambda x: uc_mod.PROFILE_CONFIGS[x]["label"])
    overall_df["scenario_label"] = overall_df["scenario"].map(lambda s: scenario_label(*str(s).split("__")))
    asset_df["profile_label"] = asset_df["profile"].map(lambda x: uc_mod.PROFILE_CONFIGS[x]["label"])
    asset_df["scenario_label"] = asset_df["scenario"].map(lambda s: scenario_label(*str(s).split("__")))

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    headline, notes = build_notes(overall_df)

    base_top = overall_df[overall_df["profile"] == "vip0_base"].sort_values("mean_total_return", ascending=False).head(12).copy()
    stress_compare = overall_df[overall_df["profile"] == "vip0_stress"].copy()
    compare_rows = []
    for scenario in base_top["scenario"].tolist()[:6]:
        compare_rows.append(overall_df[(overall_df["profile"] == "vip0_base") & (overall_df["scenario"] == scenario)])
        compare_rows.append(overall_df[(overall_df["profile"] == "vip0_stress") & (overall_df["scenario"] == scenario)])
    compare_df = pd.concat(compare_rows, ignore_index=True) if compare_rows else pd.DataFrame()
    compare_df["profile_label"] = compare_df["profile"].map(lambda x: uc_mod.PROFILE_CONFIGS[x]["label"])
    compare_df["scenario_label"] = compare_df["scenario"].map(lambda s: scenario_label(*str(s).split("__")))

    asset_focus_scenarios = base_top["scenario"].head(3).tolist()
    asset_focus = asset_df[(asset_df["profile"] == "vip0_base") & (asset_df["scenario"].isin(asset_focus_scenarios))].copy()
    if not asset_focus.empty:
        asset_focus["scenario"] = pd.Categorical(asset_focus["scenario"], categories=asset_focus_scenarios, ordered=True)
        asset_focus = asset_focus.sort_values(["scenario", "asset"]).reset_index(drop=True)
        asset_focus["scenario_label"] = asset_focus["scenario"].astype(str).map(lambda s: scenario_label(*str(s).split("__")))

    out_df_write = out_df.copy()
    for col in ["entry_ts", "exit_ts"]:
        out_df_write[col] = pd.to_datetime(out_df_write[col], utc=True).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    overall_df.to_csv(ART_DIR / f"break_even_round4_{DAYS}d_overall.csv", index=False)
    asset_df.to_csv(ART_DIR / f"break_even_round4_{DAYS}d_asset.csv", index=False)
    out_df_write.to_csv(ART_DIR / f"break_even_round4_{DAYS}d_trades.csv", index=False)

    html_block = f"""
  <div class='card'>
    <h2>break-even with cost buffer（新增）</h2>
    <p class='muted'>新增时间：{escape(generated_at)} ｜ 这轮只做 break-even，不上 trailing。所有结果都建立在统一成本层（VIP0 fee + maker/taker + slippage + funding + OCO 口径）上。</p>
    <p><b>{escape(headline)}</b></p>
    <p class='muted'>注：当初始 SL = 1.00 ATR 时，1R 与 1ATR 是同一个触发阈值，所以只展示一档 BE@1ATR+cost，避免重复行。</p>
    <h3>VIP0 base：break-even 头部方案</h3>
    {render_table(base_top[["scenario_label","mean_total_return","positive_asset_ratio","mean_win_rate","mean_hold_minutes","mean_break_even_trigger_rate","mean_break_even_stop_rate","mean_target_hit_rate","mean_stop_hit_rate","mean_cost_buffer_bps"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_win_rate","mean_break_even_trigger_rate","mean_break_even_stop_rate","mean_target_hit_rate","mean_stop_hit_rate"}, digits_cols={"mean_hold_minutes":1, "mean_cost_buffer_bps":2})}
    <h3>base vs stress：同尺对照</h3>
    {render_table(compare_df[["scenario_label","profile_label","mean_total_return","mean_win_rate","mean_hold_minutes","mean_break_even_trigger_rate","mean_break_even_stop_rate","mean_cost_buffer_bps"]], percent_cols={"mean_total_return","mean_win_rate","mean_break_even_trigger_rate","mean_break_even_stop_rate"}, digits_cols={"mean_hold_minutes":1, "mean_cost_buffer_bps":2})}
    <h3>VIP0 base：top 方案分资产</h3>
    {render_table(asset_focus[["scenario_label","asset","total_return","win_rate","avg_net_ret","avg_hold_minutes","break_even_trigger_rate","break_even_stop_rate","avg_cost_buffer_bps"]], percent_cols={"total_return","win_rate","avg_net_ret","break_even_trigger_rate","break_even_stop_rate"}, digits_cols={"avg_hold_minutes":1, "avg_cost_buffer_bps":2})}
    <h3>reader-facing 结论</h3>
    <ul>{''.join(f'<li>{escape(note)}</li>' for note in notes)}</ul>
    <p class='muted'>关键口径：break-even 触发后从下一根 5m 才生效；抬 stop 的目标不是名义 entry，而是 entry + cost buffer。cost buffer = 开仓成本 + 预估 stop 平仓成本 + timeout 对应 funding buffer。</p>
    <p class='muted'>artifact：<code>break_even_round4_{DAYS}d_overall.csv</code>、<code>break_even_round4_{DAYS}d_asset.csv</code>、<code>break_even_round4_{DAYS}d_trades.csv</code></p>
  </div>
"""

    for path in [SITE_DIR / "report.html", READING_PATH]:
        inject_section(path, html_block)

    print(
        {
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "rows": int(len(out_df)),
            "overall_rows": int(len(overall_df)),
            "asset_rows": int(len(asset_df)),
        }
    )


if __name__ == "__main__":
    main()
