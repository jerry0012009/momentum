#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank213_largecap_xs_jump_veto"
SITE_DIR = ROOT / "reports" / "site" / "paper"

ASOF_DETAIL_PATH = ART_DIR / "rank213_asof_universe_long_history_detail.csv"
ASOF_SUMMARY_PATH = ART_DIR / "rank213_asof_universe_long_history_review_summary.json"
REGIME_SUMMARY_PATH = ART_DIR / "rank213_regime_review_summary.json"
ADMISSION_SUMMARY_PATH = ROOT / "reports" / "artifacts" / "optimization_loop" / "rank213_p2_admission_20260328" / "summary.json"
SYMBOL_AVAIL_PATH = ART_DIR / "rank213_asof_universe_symbol_availability.csv"
LONG_HISTORY_UNIVERSE_AVAIL_PATH = ART_DIR / "rank213_long_history_universe_availability.csv"

P2_NOTE_PATH = ROOT / "research" / "optimization_loop" / "2026-03-28_0811_rank213_p2_admission_parameter_time_honesty_keep_p2.md"
SURVIVOR_NOTE_PATH = ROOT / "research" / "optimization_loop" / "2026-03-28_0729_rank213_survivor_followup_promote_p2.md"

FREEZE_SUMMARY_PATH = ART_DIR / "rank213_formal_strategy_freeze_summary.json"
THREEWAY_SUMMARY_PATH = ART_DIR / "rank213_formal_threeway_backtest_summary.json"
THREEWAY_YEARLY_PATH = ART_DIR / "rank213_formal_threeway_backtest_yearly.csv"
THREEWAY_DETAIL_PATH = ART_DIR / "rank213_formal_threeway_backtest_detail.csv"
UNIVERSE_AUDIT_SUMMARY_PATH = ART_DIR / "rank213_universe_selection_audit_summary.json"
BOARD_SUMMARY_PATH = ART_DIR / "rank213_family_operating_board_summary.json"

FORMAL_REVIEW_HTML_PATH = SITE_DIR / "rank213_largecap_xs_jump_veto_formal_strategy_review.html"
UNIVERSE_AUDIT_HTML_PATH = SITE_DIR / "rank213_largecap_xs_jump_veto_universe_selection_audit.html"
BOARD_HTML_PATH = SITE_DIR / "rank213_largecap_xs_jump_veto_family_operating_board.html"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def to_iso(ts: pd.Timestamp) -> str:
    return ts.tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def fmt_pct(x: float, digits: int = 2) -> str:
    if pd.isna(x):
        return ""
    return f"{x:.{digits}f}%"


def fmt_bps(x: float, digits: int = 2) -> str:
    if pd.isna(x):
        return ""
    return f"{x:.{digits}f} bps"


def max_drawdown(ret: pd.Series) -> float:
    if ret.empty:
        return np.nan
    eq = (1.0 + ret).cumprod()
    dd = eq / eq.cummax() - 1.0
    return float(dd.min())


def calc_stats(ret: pd.Series, turnover: pd.Series) -> dict:
    if ret.empty:
        return {
            "rebalances": 0,
            "net_mean_bps": np.nan,
            "net_cum_pct": np.nan,
            "max_drawdown_pct": np.nan,
            "win_rate_pct": np.nan,
            "avg_turnover_x": np.nan,
        }
    return {
        "rebalances": int(len(ret)),
        "net_mean_bps": float(ret.mean() * 10000.0),
        "net_cum_pct": float(((1.0 + ret).prod() - 1.0) * 100.0),
        "max_drawdown_pct": float(max_drawdown(ret) * 100.0),
        "win_rate_pct": float((ret > 0).mean() * 100.0),
        "avg_turnover_x": float(turnover.mean()),
    }


def render_table(df: pd.DataFrame, pct_cols: set[str] | None = None, bps_cols: set[str] | None = None, x_cols: set[str] | None = None) -> str:
    pct_cols = pct_cols or set()
    bps_cols = bps_cols or set()
    x_cols = x_cols or set()
    if df.empty:
        return "<p class='muted'>暂无数据。</p>"

    headers = "".join(f"<th>{c}</th>" for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        tds = []
        for c in df.columns:
            v = row[c]
            if pd.isna(v):
                txt = ""
            elif c in pct_cols:
                txt = fmt_pct(float(v))
            elif c in bps_cols:
                txt = fmt_bps(float(v))
            elif c in x_cols:
                txt = f"{float(v):.3f}x"
            elif isinstance(v, (float, np.floating)):
                txt = f"{float(v):.4f}"
            else:
                txt = str(v)
            tds.append(f"<td>{txt}</td>")
        rows.append("<tr>" + "".join(tds) + "</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def build_freeze_summary(*, refreeze: bool) -> dict:
    if FREEZE_SUMMARY_PATH.exists() and not refreeze:
        return read_json(FREEZE_SUMMARY_PATH)

    asof_summary = read_json(ASOF_SUMMARY_PATH)
    regime_summary = read_json(REGIME_SUMMARY_PATH)

    checks = regime_summary.get("q5_simple_gate", {}).get("current_gate", {}).get("checks", [])
    if not checks:
        raise RuntimeError("missing q5_simple_gate.current_gate.checks in regime summary; rerun regime review first")

    rules = []
    for c in checks:
        rules.append(
            {
                "variable": str(c["variable"]),
                "threshold": float(c["threshold"]),
                "higher_is_good": bool(c["higher_is_good"]),
            }
        )

    frozen_spec = asof_summary.get("frozen_spec", {})
    baseline = {
        "name": "rank213_baseline_v1",
        "definition": "15m 频率，formation=64、hold=12，按 as-of 可见 universe 做截面排名，top3 long / bottom3 short，等权 market-neutral。",
        "formation_bars": int(frozen_spec.get("formation_bars", 64)),
        "hold_bars": int(frozen_spec.get("hold_bars", 12)),
        "top_n": int(frozen_spec.get("top_n", 3)),
        "bottom_n": int(frozen_spec.get("bottom_n", 3)),
    }
    veto = {
        "name": "rank213_veto_v1",
        "definition": "在 baseline 的 short 候选上执行 jump veto：若过去 formation 窗内最大15m上冲 >= max(1.5%, 2.0×全市场中位max-up-bar)，则跳过并向下顺延补齐 short。",
        "veto_floor_pct": float(frozen_spec.get("veto_floor_pct", 1.5)),
        "veto_mult_x_median": float(frozen_spec.get("veto_mult_x_median", 2.0)),
    }
    gate = {
        "name": "rank213_regime_gate_v1",
        "definition": "使用最近30天滚动窗口特征投票；每条规则按阈值判断 pass，满足票数>=ceil(valid_rules*0.67) 即 ON，否则 OFF。OFF 时 baseline+veto 结果记为 flat(0收益、0换手)。",
        "lookback_days": 30,
        "vote_ratio": 0.67,
        "rules": rules,
        "off_action": "flat",
        "on_action": "run_baseline_plus_veto",
    }

    out = {
        "scope": "formal strategy freeze; no parameter optimization",
        "frozen_at_utc": to_iso(pd.Timestamp.now(tz="UTC")),
        "source_paths": {
            "asof_summary": str(ASOF_SUMMARY_PATH.relative_to(ROOT)),
            "regime_summary": str(REGIME_SUMMARY_PATH.relative_to(ROOT)),
            "admission_summary": str(ADMISSION_SUMMARY_PATH.relative_to(ROOT)),
        },
        "baseline": baseline,
        "veto": veto,
        "gate": gate,
        "cost_bps_per_turnover_x": float(frozen_spec.get("cost_bps_per_turnover_x", 4.0)),
    }

    FREEZE_SUMMARY_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out


def apply_frozen_gate(detail: pd.DataFrame, freeze: dict) -> tuple[pd.DataFrame, dict]:
    gate = freeze["gate"]
    rules = gate["rules"]
    vote_ratio = float(gate.get("vote_ratio", 0.67))
    lookback_days = int(gate.get("lookback_days", 30))

    detail = detail.copy().sort_values("timestamp_ts").reset_index(drop=True)
    detail["timestamp_ts"] = pd.to_datetime(detail["timestamp_ts"], utc=True)
    detail["exit_ts"] = pd.to_datetime(detail["exit_ts"], utc=True, errors="coerce")

    veto_active_rate = (pd.to_numeric(detail["veto_count"], errors="coerce").fillna(0) > 0).astype(float).to_numpy()
    xs_dispersion_bps = pd.to_numeric(detail["universe_cumret_std"], errors="coerce").astype(float).to_numpy() * 10000.0
    ls_divergence_bps = (
        pd.to_numeric(detail["long_price_contrib"], errors="coerce").astype(float).to_numpy()
        - pd.to_numeric(detail["veto_short_price_contrib"], errors="coerce").astype(float).to_numpy()
    ) * 10000.0

    ts_ns = detail["timestamp_ts"].astype("int64").to_numpy()
    exit_ns = detail["exit_ts"].astype("int64").to_numpy()
    start_ns = ts_ns - pd.Timedelta(days=lookback_days).value
    start_ixs = np.searchsorted(ts_ns, start_ns, side="left")
    end_decision_ixs = np.arange(len(detail), dtype=int)
    end_realized_ixs = np.searchsorted(exit_ns, ts_ns, side="right") - 1

    def window_mean(values: np.ndarray, end_ixs: np.ndarray) -> np.ndarray:
        valid = np.isfinite(values)
        csum = np.concatenate([[0.0], np.cumsum(np.where(valid, values, 0.0))])
        ccnt = np.concatenate([[0], np.cumsum(valid.astype(int))])
        out = np.full(len(values), np.nan, dtype=float)
        for i, (start_ix, end_ix) in enumerate(zip(start_ixs, end_ixs)):
            if end_ix < start_ix or end_ix < 0:
                continue
            total = csum[end_ix + 1] - csum[start_ix]
            count = ccnt[end_ix + 1] - ccnt[start_ix]
            if count > 0:
                out[i] = total / count
        return out

    detail["gate_feature_veto_active_rate"] = window_mean(veto_active_rate, end_decision_ixs)
    detail["gate_feature_xs_dispersion_bps"] = window_mean(xs_dispersion_bps, end_decision_ixs)
    detail["gate_feature_ls_divergence_bps"] = window_mean(ls_divergence_bps, end_realized_ixs)

    gate_on = []
    votes_list = []
    valid_list = []
    needed_list = []
    checks_latest = []

    for i, row in detail.iterrows():
        votes = 0
        valid = 0
        checks_this = []
        for rule in rules:
            var = str(rule["variable"])
            col = f"gate_feature_{var}"
            val = row[col] if col in detail.columns else np.nan
            if pd.isna(val):
                checks_this.append(
                    {
                        "variable": var,
                        "value": np.nan,
                        "threshold": float(rule["threshold"]),
                        "higher_is_good": bool(rule["higher_is_good"]),
                        "pass": False,
                        "valid": False,
                    }
                )
                continue
            valid += 1
            if rule["higher_is_good"]:
                ok = bool(float(val) >= float(rule["threshold"]))
            else:
                ok = bool(float(val) <= float(rule["threshold"]))
            votes += int(ok)
            checks_this.append(
                {
                    "variable": var,
                    "value": float(val),
                    "threshold": float(rule["threshold"]),
                    "higher_is_good": bool(rule["higher_is_good"]),
                    "pass": ok,
                    "valid": True,
                }
            )

        needed = max(1, int(math.ceil(valid * vote_ratio))) if valid > 0 else 1
        on = bool(votes >= needed) if valid > 0 else False

        gate_on.append(on)
        votes_list.append(votes)
        valid_list.append(valid)
        needed_list.append(needed)
        if i == len(detail) - 1:
            checks_latest = checks_this

    detail["gate_on"] = gate_on
    detail["gate_votes"] = votes_list
    detail["gate_valid_rules"] = valid_list
    detail["gate_needed_votes"] = needed_list

    latest = detail.iloc[-1]
    gate_snapshot = {
        "window_start_utc": to_iso(latest["timestamp_ts"] - pd.Timedelta(days=lookback_days)),
        "window_end_utc": to_iso(latest["timestamp_ts"]),
        "calculation_mode": "causal_live_aligned",
        "calculation_note": "veto/xs features use data observable at decision time; ls_divergence only uses rows whose exit_ts was already realized by that decision time.",
        "gate_on": bool(latest["gate_on"]),
        "votes": int(latest["gate_votes"]),
        "valid_rules": int(latest["gate_valid_rules"]),
        "needed_votes": int(latest["gate_needed_votes"]),
        "checks": checks_latest,
    }
    return detail, gate_snapshot


def build_threeway_backtest(freeze: dict) -> dict:
    detail = pd.read_csv(ASOF_DETAIL_PATH)
    detail["timestamp_ts"] = pd.to_datetime(detail["timestamp_ts"], utc=True)
    detail = detail.sort_values("timestamp_ts").reset_index(drop=True)

    detail, gate_snapshot = apply_frozen_gate(detail, freeze)

    detail["plain_ret"] = pd.to_numeric(detail["plain_net"], errors="coerce")
    detail["veto_ret"] = pd.to_numeric(detail["veto_net"], errors="coerce")
    detail["gate_ret"] = np.where(detail["gate_on"], detail["veto_ret"], 0.0)

    detail["plain_turnover_x"] = pd.to_numeric(detail["plain_turnover_x"], errors="coerce")
    detail["veto_turnover_x"] = pd.to_numeric(detail["veto_turnover_x"], errors="coerce")
    detail["gate_turnover_x"] = np.where(detail["gate_on"], detail["veto_turnover_x"], 0.0)

    full_plain = calc_stats(detail["plain_ret"], detail["plain_turnover_x"])
    full_veto = calc_stats(detail["veto_ret"], detail["veto_turnover_x"])
    full_gate = calc_stats(detail["gate_ret"], detail["gate_turnover_x"])

    delta = {
        "veto_minus_plain": {
            "net_mean_bps": full_veto["net_mean_bps"] - full_plain["net_mean_bps"],
            "net_cum_pct": full_veto["net_cum_pct"] - full_plain["net_cum_pct"],
            "max_drawdown_reduction_pct_points": abs(full_plain["max_drawdown_pct"]) - abs(full_veto["max_drawdown_pct"]),
            "win_rate_pct_points": full_veto["win_rate_pct"] - full_plain["win_rate_pct"],
            "avg_turnover_x": full_veto["avg_turnover_x"] - full_plain["avg_turnover_x"],
        },
        "gate_minus_veto": {
            "net_mean_bps": full_gate["net_mean_bps"] - full_veto["net_mean_bps"],
            "net_cum_pct": full_gate["net_cum_pct"] - full_veto["net_cum_pct"],
            "max_drawdown_reduction_pct_points": abs(full_veto["max_drawdown_pct"]) - abs(full_gate["max_drawdown_pct"]),
            "win_rate_pct_points": full_gate["win_rate_pct"] - full_veto["win_rate_pct"],
            "avg_turnover_x": full_gate["avg_turnover_x"] - full_veto["avg_turnover_x"],
        },
        "gate_minus_plain": {
            "net_mean_bps": full_gate["net_mean_bps"] - full_plain["net_mean_bps"],
            "net_cum_pct": full_gate["net_cum_pct"] - full_plain["net_cum_pct"],
            "max_drawdown_reduction_pct_points": abs(full_plain["max_drawdown_pct"]) - abs(full_gate["max_drawdown_pct"]),
            "win_rate_pct_points": full_gate["win_rate_pct"] - full_plain["win_rate_pct"],
            "avg_turnover_x": full_gate["avg_turnover_x"] - full_plain["avg_turnover_x"],
        },
    }

    detail["year"] = detail["timestamp_ts"].dt.year.astype(int)
    rows = []
    for year, sub in detail.groupby("year", as_index=False):
        plain = calc_stats(sub["plain_ret"], sub["plain_turnover_x"])
        veto = calc_stats(sub["veto_ret"], sub["veto_turnover_x"])
        gate = calc_stats(sub["gate_ret"], sub["gate_turnover_x"])
        rows.append(
            {
                "year": int(year),
                "rebalances": int(len(sub)),
                "plain_net_mean_bps": plain["net_mean_bps"],
                "plain_net_cum_pct": plain["net_cum_pct"],
                "plain_max_drawdown_pct": plain["max_drawdown_pct"],
                "plain_win_rate_pct": plain["win_rate_pct"],
                "plain_avg_turnover_x": plain["avg_turnover_x"],
                "veto_net_mean_bps": veto["net_mean_bps"],
                "veto_net_cum_pct": veto["net_cum_pct"],
                "veto_max_drawdown_pct": veto["max_drawdown_pct"],
                "veto_win_rate_pct": veto["win_rate_pct"],
                "veto_avg_turnover_x": veto["avg_turnover_x"],
                "gate_net_mean_bps": gate["net_mean_bps"],
                "gate_net_cum_pct": gate["net_cum_pct"],
                "gate_max_drawdown_pct": gate["max_drawdown_pct"],
                "gate_win_rate_pct": gate["win_rate_pct"],
                "gate_avg_turnover_x": gate["avg_turnover_x"],
                "delta_veto_minus_plain_net_mean_bps": veto["net_mean_bps"] - plain["net_mean_bps"],
                "delta_veto_minus_plain_net_cum_pct": veto["net_cum_pct"] - plain["net_cum_pct"],
                "delta_gate_minus_veto_net_mean_bps": gate["net_mean_bps"] - veto["net_mean_bps"],
                "delta_gate_minus_veto_net_cum_pct": gate["net_cum_pct"] - veto["net_cum_pct"],
                "delta_gate_minus_plain_net_mean_bps": gate["net_mean_bps"] - plain["net_mean_bps"],
                "delta_gate_minus_plain_net_cum_pct": gate["net_cum_pct"] - plain["net_cum_pct"],
                "gate_on_rate_pct": float(sub["gate_on"].mean() * 100.0),
            }
        )
    yearly = pd.DataFrame(rows).sort_values("year")

    THREEWAY_YEARLY_PATH.write_text(yearly.to_csv(index=False), encoding="utf-8")

    detail_out = detail[[
        "timestamp_ts",
        "plain_ret",
        "veto_ret",
        "gate_ret",
        "plain_turnover_x",
        "veto_turnover_x",
        "gate_turnover_x",
        "gate_on",
        "gate_votes",
        "gate_valid_rules",
        "gate_needed_votes",
    ]].copy()
    detail_out["timestamp_ts"] = detail_out["timestamp_ts"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    detail_out.to_csv(THREEWAY_DETAIL_PATH, index=False)

    summary = {
        "scope": "plain vs veto vs veto+gate same-spec backtest; no parameter retune",
        "source_paths": {
            "asof_detail": str(ASOF_DETAIL_PATH.relative_to(ROOT)),
            "frozen_gate": str(FREEZE_SUMMARY_PATH.relative_to(ROOT)),
        },
        "sample": {
            "start_utc": to_iso(detail["timestamp_ts"].min()),
            "end_utc": to_iso(detail["timestamp_ts"].max()),
            "rebalances": int(len(detail)),
        },
        "full_period": {
            "plain": full_plain,
            "baseline_plus_veto": full_veto,
            "baseline_plus_veto_plus_gate": full_gate,
            "delta": delta,
        },
        "gate": {
            "calculation_mode": "causal_live_aligned",
            "calculation_note": "veto/xs features use decision-time-observable data; ls_divergence only uses rows whose exit_ts was already realized by that decision time.",
            "on_rebalances": int(detail["gate_on"].sum()),
            "off_rebalances": int((~detail["gate_on"]).sum()),
            "on_rate_pct": float(detail["gate_on"].mean() * 100.0),
            "current_snapshot": gate_snapshot,
        },
        "yearly_csv": str(THREEWAY_YEARLY_PATH.relative_to(ROOT)),
        "detail_csv": str(THREEWAY_DETAIL_PATH.relative_to(ROOT)),
    }
    THREEWAY_SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {
        "summary": summary,
        "yearly": yearly,
    }


def build_universe_selection_audit() -> dict:
    admission = read_json(ADMISSION_SUMMARY_PATH)
    sample_start = pd.to_datetime(admission["sample_start"], utc=True)
    sample_end = pd.to_datetime(admission["sample_end"], utc=True)
    symbols = admission.get("symbols", [])

    symbol_avail = pd.read_csv(SYMBOL_AVAIL_PATH)
    symbol_avail["onboard_utc"] = pd.to_datetime(symbol_avail["onboard_utc"], utc=True, errors="coerce")
    symbol_avail["first_bar_utc"] = pd.to_datetime(symbol_avail["first_bar_utc"], utc=True, errors="coerce")

    long_hist = pd.read_csv(LONG_HISTORY_UNIVERSE_AVAIL_PATH) if LONG_HISTORY_UNIVERSE_AVAIL_PATH.exists() else pd.DataFrame()

    p2_note = P2_NOTE_PATH.read_text(encoding="utf-8") if P2_NOTE_PATH.exists() else ""
    survivor_note = SURVIVOR_NOTE_PATH.read_text(encoding="utf-8") if SURVIVOR_NOTE_PATH.exists() else ""

    phrase = "样本起点前已上线、当前仍交易"
    phrase_found = phrase in p2_note or phrase in survivor_note

    onboard_ok = symbol_avail["onboard_utc"].notna().all() and bool((symbol_avail["onboard_utc"] <= sample_start).all())

    selection_snapshot_exists = False
    for p in [
        ART_DIR / "rank213_universe_selection_snapshot.json",
        ART_DIR / "rank213_universe_selection_ranking.csv",
        ART_DIR / "rank213_universe_selection_inputs.json",
    ]:
        if p.exists():
            selection_snapshot_exists = True
            break

    source_set = sorted(set(long_hist["source"].dropna().astype(str))) if not long_hist.empty and "source" in long_hist.columns else []

    audit = {
        "scope": "audit how the frozen 30-symbol universe was selected and whether it is reproducible/honest",
        "frozen_universe": {
            "size": int(len(symbols)),
            "symbols": symbols,
            "sample_start_utc": to_iso(sample_start),
            "sample_end_utc": to_iso(sample_end),
        },
        "selection_definition_evidence": {
            "phrase": phrase,
            "found_in_notes": bool(phrase_found),
            "sources": [str(P2_NOTE_PATH.relative_to(ROOT)), str(SURVIVOR_NOTE_PATH.relative_to(ROOT))],
        },
        "checks": {
            "frozen_list_replayable_today": {
                "status": "yes",
                "reason": "admission summary 已保存完整 symbols 列表，可 1:1 重放。",
            },
            "original_selection_uses_only_then_visible_info": {
                "status": "partial_no",
                "reason": "缺少当时的 liquidity 排名快照/输入文件；且定义含“当前仍交易”，天然带有样本后视角。",
            },
            "survivorship_bias_risk": {
                "status": "yes",
                "reason": "静态 30 币筛选包含“当前仍交易”条件，原始选池阶段存在幸存者偏差风险；后续 as-of 回测仅缓解执行期 lookahead。",
            },
            "execution_stage_uses_asof_information_only": {
                "status": "yes",
                "reason": "asof 回测按 onboard 时间做时间可见性约束（symbol availability / onboard gating）。",
            },
            "can_deploy_directly_today": {
                "status": "yes_with_scope",
                "reason": "可直接复现 frozen 30-symbol 版本；若要“无幸存者偏差地重建原始选池”，当前证据不足。",
            },
        },
        "evidence": {
            "admission_summary": str(ADMISSION_SUMMARY_PATH.relative_to(ROOT)),
            "symbol_availability_csv": str(SYMBOL_AVAIL_PATH.relative_to(ROOT)),
            "long_history_universe_availability_csv": str(LONG_HISTORY_UNIVERSE_AVAIL_PATH.relative_to(ROOT)),
            "cached_source_tags": source_set,
            "all_symbols_onboard_before_sample_start": bool(onboard_ok),
            "selection_snapshot_artifact_exists": bool(selection_snapshot_exists),
        },
        "final_verdict": "当前 30 币 frozen universe 可直接复现并用于正式运行；但原始“为何是这30个”的当时排名快照未留档，selection 维度仍有幸存者偏差风险，需在文档中显式披露。",
    }

    UNIVERSE_AUDIT_SUMMARY_PATH.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return audit


def build_family_board(*, freeze: dict, threeway_summary: dict) -> dict:
    gate_snapshot = threeway_summary["gate"]["current_snapshot"]
    gate_on = bool(gate_snapshot["gate_on"])

    next_action = (
        "gate=ON：继续按冻结的 baseline+veto+gate 正式运行（保持参数不变）。"
        if gate_on
        else "gate=OFF：进入 flat（不新开仓），仅等待 gate 回到 ON。"
    )

    board = {
        "scope": "family operating board (formal only)",
        "updated_at_utc": to_iso(pd.Timestamp.now(tz="UTC")),
        "formal_baseline": freeze["baseline"],
        "formal_veto": freeze["veto"],
        "formal_gate": freeze["gate"],
        "current_gate_status": gate_snapshot,
        "single_next_action": next_action,
    }
    BOARD_SUMMARY_PATH.write_text(json.dumps(board, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return board


def write_formal_review_html(freeze: dict, threeway: dict) -> None:
    summary = threeway["summary"]
    yearly = threeway["yearly"].copy()

    full = pd.DataFrame(
        [
            {"strategy": "plain baseline", **summary["full_period"]["plain"]},
            {"strategy": "baseline+veto", **summary["full_period"]["baseline_plus_veto"]},
            {"strategy": "baseline+veto+gate", **summary["full_period"]["baseline_plus_veto_plus_gate"]},
        ]
    )[["strategy", "rebalances", "net_mean_bps", "net_cum_pct", "max_drawdown_pct", "win_rate_pct", "avg_turnover_x"]]

    delta = pd.DataFrame(
        [
            {"delta": "veto - plain", **summary["full_period"]["delta"]["veto_minus_plain"]},
            {"delta": "gate - veto", **summary["full_period"]["delta"]["gate_minus_veto"]},
            {"delta": "gate - plain", **summary["full_period"]["delta"]["gate_minus_plain"]},
        ]
    )[["delta", "net_mean_bps", "net_cum_pct", "max_drawdown_reduction_pct_points", "win_rate_pct_points", "avg_turnover_x"]]

    full_table = render_table(full, pct_cols={"net_cum_pct", "max_drawdown_pct", "win_rate_pct"}, bps_cols={"net_mean_bps"}, x_cols={"avg_turnover_x"})
    delta_table = render_table(delta, pct_cols={"net_cum_pct", "max_drawdown_reduction_pct_points", "win_rate_pct_points"}, bps_cols={"net_mean_bps"}, x_cols={"avg_turnover_x"})

    yearly_view = yearly[[
        "year",
        "rebalances",
        "plain_net_mean_bps",
        "plain_net_cum_pct",
        "veto_net_mean_bps",
        "veto_net_cum_pct",
        "gate_net_mean_bps",
        "gate_net_cum_pct",
        "delta_veto_minus_plain_net_mean_bps",
        "delta_gate_minus_veto_net_mean_bps",
        "delta_gate_minus_plain_net_mean_bps",
        "gate_on_rate_pct",
    ]]
    yearly_table = render_table(
        yearly_view,
        pct_cols={"plain_net_cum_pct", "veto_net_cum_pct", "gate_net_cum_pct", "gate_on_rate_pct"},
        bps_cols={
            "plain_net_mean_bps",
            "veto_net_mean_bps",
            "gate_net_mean_bps",
            "delta_veto_minus_plain_net_mean_bps",
            "delta_gate_minus_veto_net_mean_bps",
            "delta_gate_minus_plain_net_mean_bps",
        },
    )

    gate_def = []
    for r in freeze["gate"]["rules"]:
        op = ">=" if r["higher_is_good"] else "<="
        gate_def.append(f"{r['variable']} {op} {r['threshold']:.4f}")
    gate_def_txt = " and ".join(gate_def) + "；满足票数>=ceil(valid*0.67) 为 ON"

    html = f"""<!doctype html>
<html lang='zh-CN'>
<head>
<meta charset='utf-8' />
<meta name='viewport' content='width=device-width, initial-scale=1' />
<title>Rank213 formal strategy review</title>
<style>
:root{{--bg:#f8fafc;--card:#fff;--fg:#0f172a;--muted:#64748b;--line:#e2e8f0;--ok:#166534;--okbg:#dcfce7;--warn:#9a3412;--warnbg:#ffedd5}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.65 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}}
.wrap{{max-width:1180px;margin:0 auto;padding:28px 18px 64px}} .card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin-bottom:14px}}
h1,h2{{margin:0 0 12px}} .muted{{color:var(--muted)}}
.note{{border-left:4px solid #1d4ed8;background:#dbeafe;padding:12px 14px;border-radius:10px;white-space:pre-wrap}}
.ok{{border-left-color:var(--ok);background:var(--okbg)}} .warn{{border-left-color:var(--warn);background:var(--warnbg)}}
table{{width:100%;border-collapse:collapse}} th,td{{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}} th{{background:#f8fafc}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}} .metric{{border:1px solid var(--line);border-radius:12px;padding:10px 12px}}
code{{background:#eff6ff;border-radius:6px;padding:2px 6px}} a{{color:#0f766e;text-decoration:none}} a:hover{{text-decoration:underline}}
</style>
</head>
<body><div class='wrap'>
<div class='card'>
<h1>Rank213 正式策略收束（冻结参数版）</h1>
<p><strong>边界：</strong>不新增参数优化，不新增策略想法；只做 baseline / veto / gate 正式定义与同口径回测收束。</p>
<div class='note warn'><b>证据等级提醒：</b>本页保留为 formal rule / frozen gate 定义参考；历史有效性讨论默认先看 <a href='/momentum/paper/rank213_evidence_map.html'>evidence_map</a> 和 <a href='/momentum/paper/rank213_largecap_xs_jump_veto_monthly_volume_universe_rebuild.html'>monthly_volume_universe_rebuild</a>。本页不能单独用来证明“历史滚动 Top30 已通过”。</div>
<p><a href='/momentum/paper/rank213_largecap_xs_jump_veto_universe_selection_audit.html'>universe_selection_audit</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_family_operating_board.html'>family_operating_board</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_fee_sensitivity_review.html'>fee_sensitivity_review</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_monthly_volume_universe_rebuild.html'>monthly_volume_universe_rebuild</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_regime_review.html'>regime_review</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto.html'>runner</a></p>
</div>

<div class='card'>
<h2>1) 正式定义（冻结）</h2>
<div class='grid'>
  <div class='metric'><b>baseline</b><br/>{freeze['baseline']['definition']}</div>
  <div class='metric'><b>veto</b><br/>{freeze['veto']['definition']}</div>
  <div class='metric'><b>gate</b><br/>{freeze['gate']['definition']}<br/><code>{gate_def_txt}</code></div>
</div>
<div class='note'>source: <code>{summary['source_paths']['asof_detail']}</code> + <code>{summary['source_paths']['frozen_gate']}</code></div>
</div>

<div class='card'>
<h2>2) 三件套同口径全样本结果</h2>
{full_table}
<h3>差值（Δ）</h3>
{delta_table}
</div>

<div class='card'>
<h2>3) 按年表现 + 差值</h2>
{yearly_table}
<p class='muted'>yearly csv: <code>{THREEWAY_YEARLY_PATH.relative_to(ROOT)}</code></p>
</div>
</div></body></html>
"""
    FORMAL_REVIEW_HTML_PATH.write_text(html, encoding="utf-8")


def write_universe_audit_html(audit: dict) -> None:
    checks = audit["checks"]
    html = f"""<!doctype html>
<html lang='zh-CN'>
<head>
<meta charset='utf-8' />
<meta name='viewport' content='width=device-width, initial-scale=1' />
<title>Rank213 universe selection audit</title>
<style>
:root{{--bg:#f8fafc;--card:#fff;--fg:#0f172a;--muted:#64748b;--line:#e2e8f0;--ok:#166534;--okbg:#dcfce7;--warn:#9a3412;--warnbg:#ffedd5}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.65 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}}
.wrap{{max-width:1080px;margin:0 auto;padding:28px 18px 64px}} .card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin-bottom:14px}}
h1,h2{{margin:0 0 12px}} .muted{{color:var(--muted)}}
.ok{{border-left:4px solid var(--ok);background:var(--okbg);padding:12px 14px;border-radius:10px}}
.warn{{border-left:4px solid var(--warn);background:var(--warnbg);padding:12px 14px;border-radius:10px}}
code{{background:#eff6ff;border-radius:6px;padding:2px 6px}} a{{color:#0f766e;text-decoration:none}} a:hover{{text-decoration:underline}}
ul{{margin:0;padding-left:20px}} li{{margin:0 0 6px}}
</style>
</head>
<body><div class='wrap'>
<div class='card'>
<h1>Rank213 universe_selection_audit</h1>
<p><a href='/momentum/paper/rank213_largecap_xs_jump_veto_formal_strategy_review.html'>formal_strategy_review</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_family_operating_board.html'>family_operating_board</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_monthly_volume_universe_rebuild.html'>monthly_volume_universe_rebuild</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto.html'>runner</a></p>
</div>

<div class='card'>
<h2>冻结 universe</h2>
<ul>
<li>size: <b>{audit['frozen_universe']['size']}</b></li>
<li>sample: <code>{audit['frozen_universe']['sample_start_utc']}</code> → <code>{audit['frozen_universe']['sample_end_utc']}</code></li>
<li>symbols: <code>{', '.join(audit['frozen_universe']['symbols'])}</code></li>
</ul>
</div>

<div class='card'>
<h2>审计结论（按你要求的四问）</h2>
<ul>
<li><b>这30个币怎么选入：</b>{checks['frozen_list_replayable_today']['reason']}</li>
<li><b>是否只用当时可见信息：</b>{checks['original_selection_uses_only_then_visible_info']['reason']}</li>
<li><b>是否存在幸存者偏差：</b>{checks['survivorship_bias_risk']['reason']}</li>
<li><b>今天能否直接落地复现：</b>{checks['can_deploy_directly_today']['reason']}</li>
</ul>
<div class='warn'><b>final verdict:</b> {audit['final_verdict']}</div>
</div>

<div class='card'>
<h2>证据路径</h2>
<ul>
<li><code>{audit['evidence']['admission_summary']}</code></li>
<li><code>{audit['evidence']['symbol_availability_csv']}</code></li>
<li><code>{audit['evidence']['long_history_universe_availability_csv']}</code></li>
<li>cached source tags: <code>{', '.join(audit['evidence']['cached_source_tags'])}</code></li>
</ul>
<p class='muted'>selection phrase check = {audit['selection_definition_evidence']['found_in_notes']}; snapshot artifact exists = {audit['evidence']['selection_snapshot_artifact_exists']}</p>
</div>
</div></body></html>
"""
    UNIVERSE_AUDIT_HTML_PATH.write_text(html, encoding="utf-8")


def write_board_html(board: dict) -> None:
    gate = board["current_gate_status"]
    gate_label = "ON" if gate["gate_on"] else "OFF"
    html = f"""<!doctype html>
<html lang='zh-CN'>
<head>
<meta charset='utf-8' />
<meta name='viewport' content='width=device-width, initial-scale=1' />
<title>Rank213 family operating board</title>
<style>
:root{{--bg:#f8fafc;--card:#fff;--fg:#0f172a;--line:#e2e8f0;--ok:#166534;--okbg:#dcfce7;--warn:#9a3412;--warnbg:#ffedd5}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.65 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}}
.wrap{{max-width:980px;margin:0 auto;padding:28px 18px 64px}} .card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin-bottom:14px}}
h1,h2{{margin:0 0 12px}} .note{{border-left:4px solid #1d4ed8;background:#dbeafe;padding:12px 14px;border-radius:10px}}
.status{{border-left:4px solid {'var(--ok)' if gate['gate_on'] else 'var(--warn)'};background:{'var(--okbg)' if gate['gate_on'] else 'var(--warnbg)'};padding:12px 14px;border-radius:10px}}
code{{background:#eff6ff;border-radius:6px;padding:2px 6px}} a{{color:#0f766e;text-decoration:none}} a:hover{{text-decoration:underline}}
</style>
</head>
<body><div class='wrap'>
<div class='card'>
<h1>Rank213 family_operating_board</h1>
<p><a href='/momentum/paper/rank213_largecap_xs_jump_veto_formal_strategy_review.html'>formal_strategy_review</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_universe_selection_audit.html'>universe_selection_audit</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_fee_sensitivity_review.html'>fee_sensitivity_review</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_monthly_volume_universe_rebuild.html'>monthly_volume_universe_rebuild</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto.html'>runner</a></p>
</div>

<div class='card'>
<h2>正式 baseline</h2>
<div class='note'>{board['formal_baseline']['definition']}</div>
</div>

<div class='card'>
<h2>正式 veto</h2>
<div class='note'>{board['formal_veto']['definition']}</div>
</div>

<div class='card'>
<h2>正式 gate</h2>
<div class='note'>{board['formal_gate']['definition']}</div>
</div>

<div class='card'>
<h2>当前 ON/OFF 状态</h2>
<div class='status'><b>{gate_label}</b>（{gate['votes']}/{gate['valid_rules']}，阈值 {gate['needed_votes']}）<br/><code>{gate['window_start_utc']}</code> → <code>{gate['window_end_utc']}</code></div>
</div>

<div class='card'>
<h2>唯一 next action</h2>
<div class='note'><b>{board['single_next_action']}</b></div>
</div>
</div></body></html>
"""
    BOARD_HTML_PATH.write_text(html, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Rank213 formal strategy pack (freeze + threeway + universe audit + operating board)")
    parser.add_argument("--refreeze", action="store_true", help="Re-freeze gate rules from current regime summary")
    args = parser.parse_args()

    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    freeze = build_freeze_summary(refreeze=args.refreeze)
    threeway = build_threeway_backtest(freeze)
    universe_audit = build_universe_selection_audit()
    board = build_family_board(freeze=freeze, threeway_summary=threeway["summary"])

    write_formal_review_html(freeze, threeway)
    write_universe_audit_html(universe_audit)
    write_board_html(board)

    out = {
        "freeze_summary_json": str(FREEZE_SUMMARY_PATH.relative_to(ROOT)),
        "threeway_summary_json": str(THREEWAY_SUMMARY_PATH.relative_to(ROOT)),
        "threeway_yearly_csv": str(THREEWAY_YEARLY_PATH.relative_to(ROOT)),
        "universe_audit_summary_json": str(UNIVERSE_AUDIT_SUMMARY_PATH.relative_to(ROOT)),
        "family_board_summary_json": str(BOARD_SUMMARY_PATH.relative_to(ROOT)),
        "formal_review_html": str(FORMAL_REVIEW_HTML_PATH.relative_to(ROOT)),
        "universe_audit_html": str(UNIVERSE_AUDIT_HTML_PATH.relative_to(ROOT)),
        "family_board_html": str(BOARD_HTML_PATH.relative_to(ROOT)),
        "current_gate": board["current_gate_status"],
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
