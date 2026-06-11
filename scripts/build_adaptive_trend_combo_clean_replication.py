#!/usr/bin/env python3
from __future__ import annotations

import math
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

from build_volume_supportflip_higherlow_first_verdict import (
    ASSETS,
    COST_BPS_PER_SIDE,
    ensure_dir,
    fmt_ts,
    pct,
    num,
    prepare_bars,
    build_event_frame,
    render_table,
    simulate_variant_events,
    summarize_trades,
)

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_adaptive_trend_combo_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_adaptive_trend_combo_15m"
REPORT_PATH = SITE_DIR / "report.html"
SPEC_PATH = ART_DIR / "clean_room_spec_v1.csv"

VARIANTS = ["fixed_priority", "equal_vote", "state_weighted_vote"]
COSTS = [6.0, 10.0, 15.0, 20.0]
PRIMARY_COST = 6.0
PRIMARY_VARIANT = "state_weighted_vote"
PARAM_CONFIGS = [
    {"label": "t55_v65", "trend_q": 0.55, "vol_q": 0.65},
    {"label": "t55_v70", "trend_q": 0.55, "vol_q": 0.70},
    {"label": "t60_v70", "trend_q": 0.60, "vol_q": 0.70},
    {"label": "t65_v70", "trend_q": 0.65, "vol_q": 0.70},
    {"label": "t60_v75", "trend_q": 0.60, "vol_q": 0.75},
]


def compute_regime_columns(bars: pd.DataFrame, *, trend_q: float = 0.60, vol_q: float = 0.70) -> pd.DataFrame:
    out = bars.copy()
    out["ret"] = out["close"].pct_change()
    out["ema_direction"] = np.sign(out["ema_fast"] - out["ema_slow"]).astype(int)
    out["ema_spread_pct"] = (out["ema_fast"] - out["ema_slow"]).abs() / out["close"].replace(0, np.nan)
    out["realized_vol_20"] = out["ret"].rolling(20, min_periods=20).std()
    out["trend_threshold"] = out["ema_spread_pct"].rolling(96, min_periods=40).quantile(trend_q)
    out["turbulent_threshold"] = out["realized_vol_20"].rolling(96, min_periods=40).quantile(vol_q)

    regime = []
    for _, row in out.iterrows():
        if (
            pd.notna(row["ema_spread_pct"])
            and pd.notna(row["trend_threshold"])
            and int(row["ema_direction"]) != 0
            and float(row["ema_spread_pct"]) >= float(row["trend_threshold"])
        ):
            regime.append("trend")
        elif (
            pd.notna(row["realized_vol_20"])
            and pd.notna(row["turbulent_threshold"])
            and float(row["realized_vol_20"]) >= float(row["turbulent_threshold"])
        ):
            regime.append("turbulent")
        else:
            regime.append("chop")
    out["regime_state"] = regime
    return out


def retest_guard_info(bars: pd.DataFrame, event: pd.Series) -> tuple[bool, int | None, str]:
    breakout_idx = int(event["breakout_idx"])
    side = str(event["side"])
    edge = float(event["raw_edge"])
    flip_idx = None if pd.isna(event.get("flip_idx")) else int(event.get("flip_idx"))
    future = bars.iloc[breakout_idx + 1 : breakout_idx + 4].copy()
    if future.empty or not math.isfinite(edge):
        return False, flip_idx, "no_window"

    if side == "long":
        closes_ok = future[future["close"] >= edge]
    else:
        closes_ok = future[future["close"] <= edge]

    if len(closes_ok) >= 2:
        return True, int(closes_ok.index[1]), "2of3_closes"
    if flip_idx is not None:
        return True, flip_idx, "support_flip"
    return False, None, "none"


def choose_variant_acceptance(bars: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for _, event in events.iterrows():
        breakout_idx = int(event["breakout_idx"])
        side = str(event["side"])
        combo_idx = None if pd.isna(event.get("combo_idx")) else int(event.get("combo_idx"))
        regime_row_idx = combo_idx if combo_idx is not None else breakout_idx
        row = bars.iloc[regime_row_idx]
        ema_dir = int(row.get("ema_direction", 0))
        regime = str(row.get("regime_state", "chop"))
        ema_side = "long" if ema_dir > 0 else "short" if ema_dir < 0 else "flat"
        retest_ok, retest_idx, retest_mode = retest_guard_info(bars, event)

        same_votes = {"long": 0.0, "short": 0.0}
        if ema_side in same_votes:
            same_votes[ema_side] += 1.0
        if combo_idx is not None:
            same_votes[side] += 1.0
        if retest_ok:
            same_votes[side] += 1.0

        weights = {
            "trend": {"ema": 0.5, "breakout": 0.3, "retest": 0.2, "min_score": 0.6},
            "turbulent": {"ema": 0.2, "breakout": 0.3, "retest": 0.5, "min_score": 0.6},
            "chop": {"ema": 0.2, "breakout": 0.1, "retest": 0.2, "min_score": 0.7},
        }[regime]
        weighted = {"long": 0.0, "short": 0.0}
        if ema_side in weighted:
            weighted[ema_side] += weights["ema"]
        if combo_idx is not None:
            weighted[side] += weights["breakout"]
        if retest_ok:
            weighted[side] += weights["retest"]

        fixed_ok = ema_side == side and combo_idx is not None and retest_ok
        fixed_signal_idx = max(x for x in [combo_idx, retest_idx] if x is not None) if fixed_ok else None

        equal_side = "long" if same_votes["long"] > same_votes["short"] else "short" if same_votes["short"] > same_votes["long"] else None
        equal_score = max(same_votes.values())
        equal_ok = equal_side is not None and equal_score >= 2.0
        equal_signal_idx = max(x for x in [combo_idx, retest_idx, breakout_idx] if x is not None) if equal_ok else None

        weighted_side = "long" if weighted["long"] > weighted["short"] else "short" if weighted["short"] > weighted["long"] else None
        weighted_best = max(weighted.values())
        weighted_opp = min(weighted.values())
        weighted_ok = (
            weighted_side is not None
            and weighted_best >= weights["min_score"]
            and weighted_opp < 0.4
        )
        weighted_signal_idx = max(x for x in [combo_idx, retest_idx, breakout_idx] if x is not None) if weighted_ok else None

        for variant in VARIANTS:
            accepted = False
            variant_side = side
            signal_idx = None
            if variant == "fixed_priority":
                accepted = fixed_ok
                signal_idx = fixed_signal_idx
                variant_side = side
            elif variant == "equal_vote":
                accepted = equal_ok
                signal_idx = equal_signal_idx
                variant_side = equal_side or side
            elif variant == "state_weighted_vote":
                accepted = weighted_ok
                signal_idx = weighted_signal_idx
                variant_side = weighted_side or side

            rows.append(
                {
                    **event.to_dict(),
                    "variant": variant,
                    "accepted": int(bool(accepted)),
                    "signal_idx": int(signal_idx) if signal_idx is not None else np.nan,
                    "variant_side": variant_side,
                    "ema_side": ema_side,
                    "ema_vote": 1 if ema_side == side else -1 if ema_side in {"long", "short"} and ema_side != side else 0,
                    "combo_vote": 1 if combo_idx is not None and side == variant_side else 0,
                    "retest_vote": 1 if retest_ok and side == variant_side else 0,
                    "retest_mode": retest_mode,
                    "retest_signal_idx": int(retest_idx) if retest_idx is not None else np.nan,
                    "regime_state": regime,
                    "ema_spread_pct": float(row.get("ema_spread_pct", np.nan)),
                    "realized_vol_20": float(row.get("realized_vol_20", np.nan)),
                    "long_vote_count": same_votes["long"],
                    "short_vote_count": same_votes["short"],
                    "long_weighted_score": weighted["long"],
                    "short_weighted_score": weighted["short"],
                    "trade_side": variant_side if accepted else "flat",
                }
            )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out["signal_ts"] = pd.Series(pd.NaT, index=out.index, dtype="datetime64[ns, UTC]")
    mask = out["accepted"] == 1
    out.loc[mask, "signal_ts"] = out.loc[mask, "signal_idx"].astype(int).map(lambda i: bars.iloc[i]["timestamp"])
    out["breakout_ts_str"] = pd.to_datetime(out["breakout_ts"], utc=True, errors="coerce").dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return out


def summarize_with_notrade(trades: pd.DataFrame, nav: pd.DataFrame, candidate_events: pd.DataFrame, asset: str, variant: str, cost: float) -> pd.DataFrame:
    base = summarize_trades(trades, nav, asset, variant)
    total_events = int(len(candidate_events))
    accepted_events = int(candidate_events["accepted"].sum()) if not candidate_events.empty else 0
    no_trade_ratio = 1.0 - (accepted_events / total_events) if total_events else np.nan
    base["cost_bps_per_side"] = float(cost)
    base["candidate_events"] = total_events
    base["accepted_events"] = accepted_events
    base["no_trade_ratio"] = no_trade_ratio
    base["regimes_seen"] = candidate_events.loc[candidate_events["accepted"] == 1, "regime_state"].nunique() if not candidate_events.empty else 0
    return base


def build_overall_summary(asset_summary: pd.DataFrame) -> pd.DataFrame:
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
            mean_win_rate=("win_rate", "mean"),
            mean_trades=("trades", "mean"),
            min_trades=("trades", "min"),
            mean_no_trade_ratio=("no_trade_ratio", "mean"),
            mean_signal_delay_bars=("avg_signal_delay_bars", "mean"),
        )
        .sort_values(["cost_bps_per_side", "mean_total_return"], ascending=[True, False])
        .reset_index(drop=True)
    )
    out["positive_asset_ratio"] = out["positive_assets"] / out["assets_tested"].replace(0, np.nan)
    return out


def build_regime_summary(trades_df: pd.DataFrame) -> pd.DataFrame:
    if trades_df.empty:
        return pd.DataFrame()
    out = (
        trades_df.groupby(["variant", "regime_state"], as_index=False)
        .agg(
            trades=("net_ret", "size"),
            mean_net_ret=("net_ret", "mean"),
            total_return=("net_ret", lambda s: float((1.0 + s).prod() - 1.0)),
            win_rate=("win", "mean"),
            assets=("asset", "nunique"),
        )
        .sort_values(["variant", "regime_state"])
        .reset_index(drop=True)
    )
    return out


def build_time_stability(trades_df: pd.DataFrame, variant: str) -> pd.DataFrame:
    cols = ["gate", "status", "actual", "threshold", "why_it_matters"]
    hit = trades_df[trades_df["variant"] == variant].copy()
    if hit.empty or len(hit) < 9:
        return pd.DataFrame(columns=cols)
    hit["entry_dt"] = pd.to_datetime(hit["entry_ts"], utc=True)
    hit = hit.sort_values("entry_dt").reset_index(drop=True)
    hit["bucket"] = pd.qcut(np.arange(len(hit)), 3, labels=["early", "mid", "late"])
    bucket_stats = []
    for bucket, g in hit.groupby("bucket", observed=False):
        if g.empty:
            continue
        asset_totals = g.groupby("asset")["net_ret"].apply(lambda s: float((1.0 + s).prod() - 1.0))
        bucket_stats.append(
            {
                "bucket": str(bucket),
                "trades": int(len(g)),
                "positive_assets": int((asset_totals > 0).sum()),
                "assets": int(asset_totals.size),
                "mean_asset_return": float(asset_totals.mean()),
            }
        )
    bdf = pd.DataFrame(bucket_stats)
    if bdf.empty:
        return pd.DataFrame(columns=cols)
    return pd.DataFrame(
        [
            {
                "gate": "positive_bucket_floor",
                "status": "pass" if int((bdf["mean_asset_return"] > 0).sum()) >= 2 else "fail",
                "actual": f"{int((bdf['mean_asset_return'] > 0).sum())}/3 positive buckets",
                "threshold": ">= 2 positive buckets",
                "why_it_matters": "先排除只靠单一时间 pocket 才成立。",
            },
            {
                "gate": "bucket_trade_floor",
                "status": "pass" if int(bdf["trades"].min()) >= 5 else "fail",
                "actual": f"min bucket trades = {int(bdf['trades'].min())}",
                "threshold": ">= 5 trades per bucket",
                "why_it_matters": "时间稳定性不能建立在极少数交易上。",
            },
            {
                "gate": "worst_bucket_watch",
                "status": "watch" if float(bdf["mean_asset_return"].min()) <= -0.01 else "pass",
                "actual": f"worst mean_asset_return = {pct(bdf['mean_asset_return'].min())}",
                "threshold": "ideally > -1.00%",
                "why_it_matters": "最差时间 pocket 若明显翻负，就不该写成稳定。",
            },
        ],
        columns=cols,
    )


def build_cross_asset_stability(asset_summary: pd.DataFrame, variant: str) -> pd.DataFrame:
    cols = ["gate", "status", "actual", "threshold", "why_it_matters"]
    hit = asset_summary[(asset_summary["variant"] == variant) & (asset_summary["cost_bps_per_side"] == PRIMARY_COST)].copy()
    if hit.empty:
        return pd.DataFrame(columns=cols)
    worst = hit.sort_values("total_return").iloc[0]
    positive_assets = int((hit["total_return"] > 0).sum())
    return pd.DataFrame(
        [
            {
                "gate": "positive_asset_floor",
                "status": "pass" if positive_assets >= 2 else "fail",
                "actual": f"{positive_assets}/{len(hit)} assets positive",
                "threshold": ">= 2 positive assets",
                "why_it_matters": "不能只靠单一币种 lucky pocket。",
            },
            {
                "gate": "min_trade_floor",
                "status": "pass" if int(hit["trades"].min()) >= 5 else "fail",
                "actual": f"min trades = {int(hit['trades'].min())}",
                "threshold": ">= 5 per asset",
                "why_it_matters": "跨标的判断也要有最小样本。",
            },
            {
                "gate": "worst_asset_watch",
                "status": "watch" if float(worst["total_return"]) <= -0.01 else "pass",
                "actual": f"{worst['asset']} total_return={pct(worst['total_return'])}",
                "threshold": "ideally > -1.00%",
                "why_it_matters": "把最弱腿直接写清，避免均值掩盖。",
            },
        ],
        columns=cols,
    )


def run_parameter_grid() -> pd.DataFrame:
    rows = []
    for cfg in PARAM_CONFIGS:
        asset_rows = []
        for asset, symbol in ASSETS.items():
            bars = compute_regime_columns(prepare_bars(asset, symbol), trend_q=float(cfg["trend_q"]), vol_q=float(cfg["vol_q"]))
            events = build_event_frame(asset, symbol, bars)
            candidate = choose_variant_acceptance(bars, events)
            state_events = candidate[(candidate["variant"] == PRIMARY_VARIANT) & (candidate["accepted"] == 1)].copy()
            if not state_events.empty:
                state_events["side"] = state_events["trade_side"]
            trades, nav = simulate_variant_events(bars, state_events, PRIMARY_VARIANT, cost_bps_per_side=PRIMARY_COST)
            summary = summarize_with_notrade(
                trades,
                nav,
                candidate[candidate["variant"] == PRIMARY_VARIANT],
                asset,
                PRIMARY_VARIANT,
                PRIMARY_COST,
            )
            asset_rows.append(summary)
        asset_df = pd.concat(asset_rows, ignore_index=True) if asset_rows else pd.DataFrame()
        agg = build_overall_summary(asset_df)
        hit = agg[(agg["variant"] == PRIMARY_VARIANT) & (agg["cost_bps_per_side"] == PRIMARY_COST)]
        if hit.empty:
            continue
        row = hit.iloc[0].to_dict()
        row.update(cfg)
        rows.append(row)
    return pd.DataFrame(rows)


def build_parameter_stability(parameter_grid: pd.DataFrame) -> pd.DataFrame:
    cols = ["gate", "status", "actual", "threshold", "why_it_matters"]
    if parameter_grid.empty:
        return pd.DataFrame(columns=cols)
    positive = int((parameter_grid["mean_total_return"] > 0).sum())
    stable_assets = int((parameter_grid["positive_asset_ratio"] >= (2 / 3)).sum())
    min_trades = float(parameter_grid["min_trades"].min())
    worst = parameter_grid.sort_values(["mean_total_return", "positive_asset_ratio"]).iloc[0]
    return pd.DataFrame(
        [
            {
                "gate": "positive_neighbor_floor",
                "status": "pass" if positive >= 3 else "fail",
                "actual": f"{positive}/{len(parameter_grid)} configs positive",
                "threshold": ">= 3 positive local neighbors",
                "why_it_matters": "小参数邻域别一碰就碎。",
            },
            {
                "gate": "cross_asset_neighbor_floor",
                "status": "pass" if stable_assets >= 3 else "fail",
                "actual": f"{stable_assets}/{len(parameter_grid)} keep >=2/3 positive assets",
                "threshold": ">= 3 configs keep cross-asset floor",
                "why_it_matters": "参数稳定性不能只靠单点 lucky pocket。",
            },
            {
                "gate": "trade_count_neighbor_floor",
                "status": "pass" if min_trades >= 5 else "fail",
                "actual": f"min trades across neighbors = {int(min_trades)}",
                "threshold": ">= 5 per asset",
                "why_it_matters": "参数稳定性也需要最小交易数支撑。",
            },
            {
                "gate": "worst_neighbor_watch",
                "status": "watch" if float(worst['mean_total_return']) <= -0.01 else "pass",
                "actual": f"{worst['label']} mean_total_return={pct(worst['mean_total_return'])}",
                "threshold": "ideally > -1.00%",
                "why_it_matters": "最差近邻若明显翻负，说明候选仍偏 sample-bound。",
            },
        ],
        columns=cols,
    )


def build_cost_trade_stability(overall_summary: pd.DataFrame, variant: str) -> pd.DataFrame:
    cols = ["gate", "status", "actual", "threshold", "why_it_matters"]
    hit = overall_summary[overall_summary["variant"] == variant].copy()
    if hit.empty:
        return pd.DataFrame(columns=cols)
    cost_positive = int((hit["mean_total_return"] > 0).sum())
    at20 = hit[hit["cost_bps_per_side"] == 20.0]
    at20_val = float(at20.iloc[0]["mean_total_return"]) if not at20.empty else np.nan
    return pd.DataFrame(
        [
            {
                "gate": "cost_survival_floor",
                "status": "pass" if cost_positive >= 2 else "fail",
                "actual": f"{cost_positive}/{len(hit)} cost levels positive",
                "threshold": ">= 2 positive cost levels",
                "why_it_matters": "轻量 friction 后不能立刻归零。",
            },
            {
                "gate": "trade_count_floor",
                "status": "pass" if int(hit["min_trades"].min()) >= 5 else "fail",
                "actual": f"min trades across cost ladder = {int(hit['min_trades'].min())}",
                "threshold": ">= 5 per asset",
                "why_it_matters": "trade count 过薄就不配继续推广。",
            },
            {
                "gate": "20bps_watch",
                "status": "watch" if pd.notna(at20_val) and at20_val <= 0 else "pass",
                "actual": pct(at20_val) if pd.notna(at20_val) else "-",
                "threshold": "ideally > 0% @ 20bps",
                "why_it_matters": "20bps 不是硬门槛，但能看出是否只在轻摩擦下存活。",
            },
        ],
        columns=cols,
    )


def choose_candidate_variant(overall_summary: pd.DataFrame) -> str:
    hit = overall_summary[overall_summary["cost_bps_per_side"] == PRIMARY_COST].copy()
    if hit.empty:
        return PRIMARY_VARIANT
    ranked = hit.sort_values(["mean_total_return", "positive_asset_ratio", "mean_no_trade_ratio"], ascending=[False, False, True])
    return str(ranked.iloc[0]["variant"])


def derive_verdict(overall_summary: pd.DataFrame, asset_summary: pd.DataFrame, time_stability: pd.DataFrame, parameter_stability: pd.DataFrame, cross_asset_stability: pd.DataFrame, cost_trade_stability: pd.DataFrame) -> tuple[str, list[str], str]:
    primary6 = overall_summary[overall_summary["cost_bps_per_side"] == PRIMARY_COST].copy()
    if primary6.empty:
        return "hard verdict：当前没有生成可读 clean replication 结果。", ["缺少 6bps/side 总表。"], PRIMARY_VARIANT

    winner = choose_candidate_variant(overall_summary)
    fixed = primary6[primary6["variant"] == "fixed_priority"].iloc[0]
    equal = primary6[primary6["variant"] == "equal_vote"].iloc[0]
    state = primary6[primary6["variant"] == "state_weighted_vote"].iloc[0]
    winner_row = primary6[primary6["variant"] == winner].iloc[0]

    fail_sets = []
    for name, df in [
        ("time", time_stability),
        ("parameter", parameter_stability),
        ("cross_asset", cross_asset_stability),
        ("cost_trade", cost_trade_stability),
    ]:
        if not df.empty and (df["status"] == "fail").any():
            fail_sets.append(name)

    state_beats_fixed = float(state["mean_total_return"]) > float(fixed["mean_total_return"]) and float(state["mean_no_trade_ratio"]) <= 0.70
    equal_beats_fixed = float(equal["mean_total_return"]) > float(fixed["mean_total_return"]) and float(equal["mean_no_trade_ratio"]) <= 0.70

    verdict_tag = "park"
    headline = (
        "hard verdict：adaptive trend combo 这轮 clean replication 更像 `park / evidence pool`，"
        "暂不进入 paper candidate pool。"
    )
    if (state_beats_fixed or equal_beats_fixed) and float(winner_row["mean_total_return"]) > 0 and float(winner_row["positive_asset_ratio"]) >= 2 / 3 and not fail_sets:
        verdict_tag = "narrow paper pilot" if float(winner_row["mean_total_return"]) > 0.03 and float(winner_row["mean_trades"]) >= 8 else "paper candidate"
        headline = (
            f"hard verdict：adaptive trend combo 的 {winner} 在当前 15m crypto clean replication 上已拿到最小正向 first verdict，"
            f"可进入 `{verdict_tag}`。"
        )
    elif (state_beats_fixed or equal_beats_fixed) and float(winner_row["mean_total_return"]) > 0:
        verdict_tag = "paper candidate"
        headline = (
            f"hard verdict：adaptive trend combo 的 {winner} 相对 fixed_priority 更不差，"
            "且 post-cost return 已转正；当前可进入窄范围 `paper candidate pool`，但仍保留 one-more-light-check 读法。"
        )

    bullets = [
        f"fixed_priority：mean_total_return {pct(fixed['mean_total_return'])}，positive_asset_ratio {pct(fixed['positive_asset_ratio'])}，mean_no_trade_ratio {pct(fixed['mean_no_trade_ratio'])}。",
        f"equal_vote：mean_total_return {pct(equal['mean_total_return'])}，positive_asset_ratio {pct(equal['positive_asset_ratio'])}，mean_no_trade_ratio {pct(equal['mean_no_trade_ratio'])}。",
        f"state_weighted_vote：mean_total_return {pct(state['mean_total_return'])}，positive_asset_ratio {pct(state['positive_asset_ratio'])}，mean_no_trade_ratio {pct(state['mean_no_trade_ratio'])}。",
        "两条轻量诚实守门已通过：规则能明确写成 trade on / trade off；当前实现只用当下 bar 信息做 regime / breakout / retest，不用 future label。",
        f"当前 Light Stability Pack 硬 fail 位：{', '.join(fail_sets) if fail_sets else '无硬 fail'}。",
    ]
    if float(state["mean_no_trade_ratio"]) > 0.70:
        bullets.append("state_weighted_vote 的 no_trade_ratio 已超过 70%，因此即便 headline 不差，也要防止把‘少做交易’误写成组合优势。")
    if winner == "equal_vote" and float(equal["mean_total_return"]) >= float(state["mean_total_return"]):
        bullets.append("当前更优版本是更简单的 equal_vote，因此默认不把状态切换写得比证据更大。")
    if verdict_tag == "park":
        bullets.append("因此这条线当前更像 clean-replication evidence，而不是应立即进入 paper wiring 的新席位候选。")
    else:
        bullets.append(f"因此当前最诚实的 desk call 是：先把 {winner} 作为窄范围 `{verdict_tag}` 保留，而不是继续停在 source-intake wording。")
    return headline, bullets, verdict_tag


def write_report(overall_summary: pd.DataFrame, asset_summary: pd.DataFrame, regime_summary: pd.DataFrame, time_stability: pd.DataFrame, parameter_stability: pd.DataFrame, cross_asset_stability: pd.DataFrame, cost_trade_stability: pd.DataFrame, parameter_grid: pd.DataFrame, meta_df: pd.DataFrame) -> None:
    ensure_dir(SITE_DIR)
    headline, bullets, verdict_tag = derive_verdict(overall_summary, asset_summary, time_stability, parameter_stability, cross_asset_stability, cost_trade_stability)
    meta = meta_df.iloc[0].to_dict() if not meta_df.empty else {}
    bullets_html = "".join(f"<li>{escape(x)}</li>" for x in bullets)
    summary_table = render_table(
        overall_summary[overall_summary["cost_bps_per_side"] == PRIMARY_COST][[
            "variant", "assets_tested", "positive_assets", "positive_asset_ratio", "mean_total_return", "mean_trades", "mean_no_trade_ratio", "mean_signal_delay_bars"
        ]],
        percent_cols={"positive_asset_ratio", "mean_total_return", "mean_no_trade_ratio"},
        digits_cols={"mean_trades": 1, "mean_signal_delay_bars": 2},
    )
    asset_table = render_table(
        asset_summary[asset_summary["cost_bps_per_side"] == PRIMARY_COST][[
            "asset", "variant", "trades", "total_return", "win_rate", "no_trade_ratio"
        ]],
        percent_cols={"total_return", "win_rate", "no_trade_ratio"},
        digits_cols={"trades": 0},
    )
    regime_table = render_table(
        regime_summary[["variant", "regime_state", "trades", "mean_net_ret", "total_return", "win_rate", "assets"]] if not regime_summary.empty else regime_summary,
        percent_cols={"mean_net_ret", "total_return", "win_rate"},
        digits_cols={"trades": 0, "assets": 0},
    )
    cost_table = render_table(
        overall_summary[["variant", "cost_bps_per_side", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_no_trade_ratio"]],
        percent_cols={"mean_total_return", "positive_asset_ratio", "mean_no_trade_ratio"},
        digits_cols={"cost_bps_per_side": 0, "mean_trades": 1},
    )
    time_table = render_table(time_stability, percent_cols=set())
    param_table = render_table(parameter_stability, percent_cols=set())
    cross_table = render_table(cross_asset_stability, percent_cols=set())
    cost_stability_table = render_table(cost_trade_stability, percent_cols=set())
    grid_table = render_table(
        parameter_grid[["label", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_no_trade_ratio"]] if not parameter_grid.empty else parameter_grid,
        percent_cols={"mean_total_return", "positive_asset_ratio", "mean_no_trade_ratio"},
        digits_cols={"mean_trades": 1},
    )

    html = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Scout Seat · adaptive trend combo · clean replication</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1120px; margin: 40px auto; padding: 0 18px; line-height: 1.68; color: #111827; background: #f8fafc; }}
    h1,h2,h3 {{ line-height: 1.25; }}
    .muted {{ color:#6b7280; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    ul {{ padding-left:20px; }}
    a {{ color:#2563eb; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
  </style>
</head>
<body>
  <p><a href="../../index.html">← 返回首页</a></p>
  <h1>Scout Seat · adaptive trend combo · 15m crypto clean replication</h1>
  <p class="muted">生成时间：{escape(str(meta.get('generated_at_utc', '-')))} ｜ 这页把上一轮 clean-room spec 推进到最小 clean replication + Light Stability Pack，不再停留在 source-intake wording。</p>

  <div class="card">
    <h2>hard verdict</h2>
    <p><b>{escape(headline)}</b></p>
    <ul>{bullets_html}</ul>
  </div>

  <div class="card">
    <h2>本轮 clean replication 口径</h2>
    <ul>
      <li>样本：<code>Binance 120d / 15m / BTC-USD + ETH-USD + SOL-USD</code></li>
      <li>组件：<code>EMA20-EMA50 direction</code> + <code>Rank 2 combo_all breakout confirmation vote</code> + <code>2-of-3 closes / support-flip retest guard</code></li>
      <li>三档聚合：<code>fixed_priority</code>、<code>equal_vote</code>、<code>state_weighted_vote</code></li>
      <li>regime：<code>trend / turbulent / chop</code> 只用 trailing EMA spread 与 realized vol 定义，不用 future label</li>
      <li>执行：<code>next-bar open | 1 ATR stop | 2 ATR target | 8-bar time stop | 6bps/side</code></li>
      <li>spec：<code>{escape(str(SPEC_PATH.relative_to(ROOT)) if SPEC_PATH.exists() else '-')}</code></li>
    </ul>
  </div>

  <div class="card">
    <h2>variant aggregate（6bps/side）</h2>
    {summary_table}
    <p class="muted">artifact：<code>reports/artifacts/scout_adaptive_trend_combo_15m/overall_summary.csv</code></p>
  </div>

  <div class="card">
    <h2>per-asset summary（6bps/side）</h2>
    {asset_table}
    <p class="muted">这里把 <code>no_trade_ratio</code> 单独外显，避免把“少做交易”误写成策略增量。</p>
  </div>

  <div class="card">
    <h2>regime bucket summary</h2>
    {regime_table}
    <p class="muted">artifact：<code>reports/artifacts/scout_adaptive_trend_combo_15m/regime_bucket_summary.csv</code></p>
  </div>

  <div class="card">
    <h2>cost ladder</h2>
    {cost_table}
    {cost_stability_table}
  </div>

  <div class="card">
    <h2>Light Stability Pack</h2>
    <h3>1) 时间稳定性</h3>
    {time_table}
    <h3>2) 参数稳定性</h3>
    {param_table}
    <h3>3) 跨标的稳定性</h3>
    {cross_table}
    <h3>4) 成本 / 交易数稳定性</h3>
    {cost_stability_table}
  </div>

  <div class="card">
    <h2>parameter neighbor grid（state_weighted_vote）</h2>
    {grid_table}
    <p class="muted">这张表只看 regime 阈值的小邻域，防止把单点阈值 lucky pocket 写成组合优势。</p>
  </div>

  <div class="card">
    <h2>怎么读这页</h2>
    <ul>
      <li>如果 <code>state_weighted_vote</code> 并没有同时改善收益与成本存活，或者只是靠 <code>no_trade_ratio</code> 飙升才站住，就应该直接 <code>park</code>。</li>
      <li>如果 <code>equal_vote</code> 已经不差于 <code>state_weighted_vote</code>，默认更诚实的结论是保留简单版本，而不是把“状态切换”写得比证据更大。</li>
      <li>这页服务的是 Scout 快筛 verdict：<code>park / paper candidate / narrow paper pilot</code>，不是直接去争 Live Seat。</li>
    </ul>
  </div>
</body>
</html>
'''
    REPORT_PATH.write_text(html, encoding="utf-8")


def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    accepted_rows = []
    all_trades = []
    all_nav = []
    all_summaries = []

    for asset, symbol in ASSETS.items():
        bars = compute_regime_columns(prepare_bars(asset, symbol))
        events = build_event_frame(asset, symbol, bars)
        candidate = choose_variant_acceptance(bars, events)
        accepted_rows.append(candidate)
        for variant in VARIANTS:
            variant_candidate = candidate[candidate["variant"] == variant].copy()
            variant_events = variant_candidate[variant_candidate["accepted"] == 1].copy()
            if not variant_events.empty:
                variant_events["side"] = variant_events["trade_side"]
            for cost in COSTS:
                trades, nav = simulate_variant_events(bars, variant_events, variant, cost_bps_per_side=cost)
                if not trades.empty:
                    trades = trades.merge(
                        variant_events[["breakout_ts_str", "regime_state", "trade_side", "long_weighted_score", "short_weighted_score", "retest_mode"]],
                        left_on="breakout_ts",
                        right_on="breakout_ts_str",
                        how="left",
                    ).drop(columns=["breakout_ts_str"])
                    trades["cost_bps_per_side"] = float(cost)
                if not nav.empty:
                    nav["cost_bps_per_side"] = float(cost)
                summary = summarize_with_notrade(trades, nav, variant_candidate, asset, variant, cost)
                all_trades.append(trades)
                all_nav.append(nav)
                all_summaries.append(summary)

    candidate_df = pd.concat(accepted_rows, ignore_index=True) if accepted_rows else pd.DataFrame()
    trades_df = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    nav_df = pd.concat(all_nav, ignore_index=True) if all_nav else pd.DataFrame()
    asset_summary = pd.concat(all_summaries, ignore_index=True) if all_summaries else pd.DataFrame()
    overall_summary = build_overall_summary(asset_summary)
    regime_summary = build_regime_summary(trades_df[trades_df["cost_bps_per_side"] == PRIMARY_COST].copy() if not trades_df.empty else trades_df)
    winner_variant = choose_candidate_variant(overall_summary)
    time_stability = build_time_stability(trades_df[trades_df["cost_bps_per_side"] == PRIMARY_COST].copy() if not trades_df.empty else trades_df, winner_variant)
    cross_asset_stability = build_cross_asset_stability(asset_summary, winner_variant)
    parameter_grid = run_parameter_grid()
    parameter_stability = build_parameter_stability(parameter_grid)
    cost_trade_stability = build_cost_trade_stability(overall_summary, winner_variant)
    verdict_headline, _, verdict_tag = derive_verdict(overall_summary, asset_summary, time_stability, parameter_stability, cross_asset_stability, cost_trade_stability)

    meta_df = pd.DataFrame([
        {
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "candidate_id": "scout_adaptive_trend_combo_15m_v1",
            "winner_variant": winner_variant,
            "verdict_tag": verdict_tag,
            "verdict": verdict_headline,
            "sample_window": "Binance 120d / 15m / BTC+ETH+SOL",
            "next_step": "若为 park，则默认切去更高边际价值 Scout intake；若为 paper candidate，则只补最小 monitoring / ledger，不再磨 wording。",
        }
    ])

    if not candidate_df.empty:
        candidate_df.to_csv(ART_DIR / "candidate_events_with_votes.csv", index=False)
    if not trades_df.empty:
        trades_df.to_csv(ART_DIR / "trades.csv", index=False)
    if not nav_df.empty:
        nav_df.to_csv(ART_DIR / "nav.csv", index=False)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    overall_summary.to_csv(ART_DIR / "overall_summary.csv", index=False)
    if not regime_summary.empty:
        regime_summary.to_csv(ART_DIR / "regime_bucket_summary.csv", index=False)
    if not time_stability.empty:
        time_stability.to_csv(ART_DIR / "time_stability_drycheck.csv", index=False)
    if not cross_asset_stability.empty:
        cross_asset_stability.to_csv(ART_DIR / "cross_asset_stability_drycheck.csv", index=False)
    if not parameter_grid.empty:
        parameter_grid.to_csv(ART_DIR / "parameter_neighbor_grid.csv", index=False)
    if not parameter_stability.empty:
        parameter_stability.to_csv(ART_DIR / "parameter_stability_drycheck.csv", index=False)
    if not cost_trade_stability.empty:
        cost_trade_stability.to_csv(ART_DIR / "cost_trade_stability_drycheck.csv", index=False)
    meta_df.to_csv(ART_DIR / "clean_replication_meta.csv", index=False)

    write_report(
        overall_summary,
        asset_summary.sort_values(["cost_bps_per_side", "variant", "asset"]).reset_index(drop=True),
        regime_summary,
        time_stability,
        parameter_stability,
        cross_asset_stability,
        cost_trade_stability,
        parameter_grid,
        meta_df,
    )
    print("[ok] adaptive trend combo clean replication generated")
    print("[artifact]", ART_DIR / "overall_summary.csv")
    print("[site]", REPORT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
