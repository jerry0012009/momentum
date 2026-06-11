#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "execution" / "rank213_age90_live_canary.yaml"
ART_DIR = ROOT / "reports" / "artifacts" / "rank213_age90_live_canary"
SHADOW_DIR = ROOT / "reports" / "artifacts" / "paper_rank213_age90_live"
PHASE3_DIR = ROOT / "reports" / "artifacts" / "paper_rank213_largecap_xs_jump_veto"
SITE_PATH = ROOT / "reports" / "site" / "paper" / "rank213_age90_live_launch.html"
SUMMARY_PATH = ART_DIR / "rank213_age90_live_launch_parity.json"
EXPECTED_STRATEGY_ID = "rank213_age90_14d_skip1d_voladj_top50_4x4"
EXPECTED_LONG_LEGS = 4
EXPECTED_SHORT_LEGS = 4


def iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def pct(value: Any, digits: int = 2) -> str:
    try:
        return f"{float(value):.{digits}f}%"
    except Exception:
        return ""


def bps(value: Any, digits: int = 2) -> str:
    try:
        return f"{float(value):.{digits}f} bps"
    except Exception:
        return ""


def usd(value: Any) -> str:
    try:
        v = float(value)
    except Exception:
        return ""
    if abs(v) >= 1_000_000:
        return f"${v / 1_000_000:.2f}M"
    if abs(v) >= 1_000:
        return f"${v / 1_000:.1f}K"
    return f"${v:.0f}"


def stable_hash(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def table(rows: list[dict[str, Any]], cols: list[tuple[str, str]]) -> str:
    head = "".join(f"<th>{escape(label)}</th>" for _, label in cols)
    body = []
    for row in rows:
        body.append("<tr>" + "".join(f"<td>{escape(str(row.get(key, '')))}</td>" for key, _ in cols) + "</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def read_phase3() -> dict[str, Any]:
    summary = read_json(PHASE3_DIR / "rank213_age90_14d_phase3_validation_summary.json", {})
    exec_grid_path = PHASE3_DIR / "rank213_age90_14d_phase3_execution_cost_grid.csv"
    liq_path = PHASE3_DIR / "rank213_age90_14d_phase3_liquidity_capacity.csv"
    exec_rows: list[dict[str, Any]] = []
    liq_rows: list[dict[str, Any]] = []
    if exec_grid_path.exists():
        df = pd.read_csv(exec_grid_path)
        keep = df[df["scenario"].astype(str).isin(["signal_day_open_to_next_open", "twap_240m", "vwap_240m", "delayed_next_open_to_following_open"])]
        cost_col = "cost_bps" if "cost_bps" in keep.columns else "cost_bps_per_basket"
        if cost_col in keep.columns:
            keep = keep[pd.to_numeric(keep[cost_col], errors="coerce").eq(12)]
        for _, r in keep.iterrows():
            exec_rows.append({
                "scenario": r.get("scenario"),
                "cost": bps(r.get(cost_col), 0),
                "cum": pct(r.get("net_cum_pct")),
                "dd": pct(r.get("max_drawdown_pct")),
                "mean": bps(r.get("net_mean_bps")),
                "win": pct(r.get("win_rate_pct")),
            })
    if liq_path.exists():
        liq = pd.read_csv(liq_path)
        keep = liq[liq["scenario"].astype(str).isin(["twap_240m", "vwap_240m"])]
        for _, r in keep.iterrows():
            liq_rows.append({
                "scenario": r.get("scenario"),
                "participation": pct(r.get("participation_pct")),
                "p10_capacity": usd(r.get("p10_capacity_usdt")),
                "median_capacity": usd(r.get("median_capacity_usdt")),
            })
    return {"summary": summary, "execution_rows": exec_rows, "liquidity_rows": liq_rows}


def build_payload() -> dict[str, Any]:
    cfg = load_yaml(CONFIG_PATH)
    shadow_current = read_json(SHADOW_DIR / "rank213_age90_shadow_current_decision.json", {})
    shadow_status = read_json(SHADOW_DIR / "rank213_age90_shadow_status.json", {})
    signal_snapshot = read_json(SHADOW_DIR / "rank213_age90_signal_snapshot.json", {})
    old_status = read_json(ROOT / "reports" / "artifacts" / "rank213_live_canary_shell" / "live_status.json", {})
    new_status = read_json(ROOT / "reports" / "artifacts" / "rank213_age90_live_canary_shell" / "live_status.json", {})
    flatten_plan = read_json(ART_DIR / "prelaunch_flatten_plan.json", {})
    phase3 = read_phase3()

    config_strategy = ((cfg.get("meta") or {}).get("strategy_id"))
    shadow_strategy = shadow_current.get("strategy_id")
    legs_ok = len(shadow_current.get("longs", []) or []) == EXPECTED_LONG_LEGS and len(shadow_current.get("shorts", []) or []) == EXPECTED_SHORT_LEGS
    hash_basis = {
        "decision_ts": shadow_current.get("decision_ts"),
        "planned_exit_ts": shadow_current.get("planned_exit_ts"),
        "longs": shadow_current.get("longs", []),
        "shorts": shadow_current.get("shorts", []),
        "weights": shadow_current.get("weights", {}),
        "strategy_id": shadow_current.get("strategy_id"),
    }
    computed_shadow_hash = stable_hash(hash_basis)
    configured_hold = int(((cfg.get("phase6") or {}).get("exit") or {}).get("timeout_minutes", 0) or 0)
    cadence = int((cfg.get("execution") or {}).get("entry_cadence_minutes", 0) or 0)
    old_residuals = []
    for row in old_status.get("exchange_open_positions", []) if isinstance(old_status.get("exchange_open_positions"), list) else []:
        if str(row.get("reconciliation_classification") or "") == "residual_open_on_exchange" and bool(row.get("rank213_owned")):
            old_residuals.append(row)
    launch_blockers = []
    if old_residuals:
        launch_blockers.append("old_rank213_residual_open_on_exchange")
    if shadow_status.get("current_decision_source_mode") != "recompute_recent":
        launch_blockers.append("shadow_not_recompute_recent")
    if not legs_ok:
        launch_blockers.append("basket_not_4x4")
    if config_strategy != shadow_strategy:
        launch_blockers.append("config_shadow_strategy_id_mismatch")
    if configured_hold != 1440 or cadence != 1440:
        launch_blockers.append("daily_cadence_or_hold_not_1440_minutes")

    return {
        "generated_at_utc": iso_now(),
        "launch_status": "blocked" if launch_blockers else "ready_to_arm_after_operator_confirm",
        "launch_blockers": launch_blockers,
        "config_path": str(CONFIG_PATH.relative_to(ROOT)),
        "shadow_current": shadow_current,
        "shadow_status": shadow_status,
        "signal_snapshot_hash": signal_snapshot.get("signal_hash"),
        "computed_shadow_hash": computed_shadow_hash,
        "config": {
            "strategy_id": config_strategy,
            "entry_cadence_minutes": cadence,
            "hold_timeout_minutes": configured_hold,
            "gross_notional_usdt": ((cfg.get("capital") or {}).get("desired_gross_notional_usdt")),
            "leg_notional_usdt": ((cfg.get("capital") or {}).get("desired_leg_notional_usdt")),
            "live_order_placement_enabled": ((cfg.get("canary_controls") or {}).get("live_order_placement_enabled")),
            "trade_enabled": ((cfg.get("safety") or {}).get("trade_enabled")),
            "dry_run_only": ((cfg.get("safety") or {}).get("dry_run_only")),
        },
        "residuals": {
            "old_rank213_count": len(old_residuals),
            "old_rank213_symbols": [r.get("symbol") for r in old_residuals],
            "old_rank213_rows": old_residuals,
            "flatten_plan_status": flatten_plan.get("execution_status"),
        },
        "new_live_status": new_status,
        "phase3": phase3,
    }


def build_html(payload: dict[str, Any]) -> str:
    status = payload["launch_status"]
    blockers = payload["launch_blockers"]
    shadow = payload["shadow_current"]
    cfg = payload["config"]
    phase3 = payload["phase3"]
    base = (phase3.get("summary") or {}).get("base_stats", {})
    residual_rows = [
        {
            "symbol": r.get("symbol"),
            "side": r.get("side"),
            "qty": r.get("qty") or r.get("exchange_qty_abs"),
            "entry": r.get("entry_price"),
            "pnl": r.get("unrealized_pnl"),
            "why": r.get("reconciliation_classification"),
        }
        for r in (payload.get("residuals") or {}).get("old_rank213_rows", [])
    ]
    blocker_text = "无" if not blockers else ", ".join(blockers)
    launch_text = "可以进入人工确认启动" if status != "blocked" else "暂时不能启动实盘"
    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Rank213 age90 Top50 4x4 live launch parity</title>
<style>
body{{margin:0;background:#f6f1e7;color:#172019;font-family:ui-serif,Georgia,"Times New Roman","Noto Serif SC",serif;line-height:1.55}}
main{{max-width:1120px;margin:0 auto;padding:34px 18px 60px}}
.hero{{background:linear-gradient(135deg,#172019,#31523d);color:#fff;border-radius:24px;padding:28px;box-shadow:0 18px 48px rgba(23,32,25,.18)}}
h1{{margin:0 0 8px;font-size:34px}} h2{{margin-top:28px}} .pill{{display:inline-block;padding:5px 10px;border-radius:999px;background:#e8d29a;color:#172019;font-weight:700}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px;margin-top:18px}}
.card{{background:#fffaf0;border:1px solid #dfd2b5;border-radius:18px;padding:16px}}
.num{{font-size:26px;font-weight:800}} .bad{{color:#9d2d20}} .ok{{color:#236b3f}}
table{{width:100%;border-collapse:collapse;background:#fffaf0;border-radius:14px;overflow:hidden}} th,td{{border-bottom:1px solid #dfd2b5;padding:9px 10px;text-align:left;font-size:14px}} th{{background:#eadfca}}
code{{background:#eadfca;padding:2px 5px;border-radius:5px}} a{{color:#285f75}} .small{{font-size:13px;color:#5c6259}}
</style>
</head>
<body><main>
<section class="hero">
<span class="pill">{escape(launch_text)}</span>
<h1>Rank213 age90 Top50 4L4S 实盘启动一致性页</h1>
<p>这页只回答一个问题：现在准备启动的 Top50 4L4S live canary，是否和第四轮扩展回测口径、daily shadow、实盘执行配置一致。</p>
<p><b>当前结论：</b>{escape(launch_text)}。阻塞项：{escape(blocker_text)}。</p>
<p class="small">生成时间：{escape(payload["generated_at_utc"])}</p>
</section>

<div class="grid">
<div class="card"><div>Top50 4L4S 验证页</div><div class="num">Top50</div><div class="small"><a href="/momentum/paper/rank213_age90_top50_4x4_execution_stability.html">执行成本与稳定性验证</a></div></div>
<div class="card"><div>回测最大回撤</div><div class="num bad">{escape(pct(base.get("max_drawdown_pct")))}</div><div class="small">说明它仍是高波动 canary，不是稳健现金机</div></div>
<div class="card"><div>当前 shadow 多空</div><div class="num">{len(shadow.get("longs", []) or [])} x {len(shadow.get("shorts", []) or [])}</div><div class="small">{escape(str(shadow.get("decision_ts") or ""))}</div></div>
<div class="card"><div>旧 Rank213 残留仓位</div><div class="num {'bad' if (payload.get('residuals') or {}).get('old_rank213_count') else 'ok'}">{(payload.get('residuals') or {}).get('old_rank213_count')}</div><div class="small">{escape(', '.join((payload.get('residuals') or {}).get('old_rank213_symbols') or []) or 'none')}</div></div>
</div>

<h2>启动前硬检查</h2>
{table([
{"item":"策略 ID", "expected":EXPECTED_STRATEGY_ID, "actual":cfg.get("strategy_id"), "result":"OK" if cfg.get("strategy_id")==shadow.get("strategy_id")==EXPECTED_STRATEGY_ID else "FAIL"},
{"item":"频率", "expected":"daily / 1440 minutes", "actual":cfg.get("entry_cadence_minutes"), "result":"OK" if cfg.get("entry_cadence_minutes")==1440 else "FAIL"},
{"item":"持仓周期", "expected":"1 day / 1440 minutes", "actual":cfg.get("hold_timeout_minutes"), "result":"OK" if cfg.get("hold_timeout_minutes")==1440 else "FAIL"},
{"item":"篮子", "expected":"4 long + 4 short", "actual":f"{len(shadow.get('longs', []) or [])}+{len(shadow.get('shorts', []) or [])}", "result":"OK" if len(shadow.get("longs", []) or [])==EXPECTED_LONG_LEGS and len(shadow.get("shorts", []) or [])==EXPECTED_SHORT_LEGS else "FAIL"},
{"item":"shadow 来源", "expected":"recompute_recent", "actual":payload.get("shadow_status", {}).get("current_decision_source_mode"), "result":"OK" if payload.get("shadow_status", {}).get("current_decision_source_mode")=="recompute_recent" else "FAIL"},
{"item":"旧仓位残留", "expected":"0", "actual":(payload.get("residuals") or {}).get("old_rank213_count"), "result":"FAIL" if (payload.get("residuals") or {}).get("old_rank213_count") else "OK"},
], [("item","项目"),("expected","期望"),("actual","当前"),("result","结果")])}

<h2>当前 daily shadow 信号</h2>
{table([
{"side":"LONG", "symbols":", ".join(shadow.get("longs", []) or [])},
{"side":"SHORT", "symbols":", ".join(shadow.get("shorts", []) or [])},
{"side":"HASH", "symbols":shadow.get("signal_hash")},
], [("side","字段"),("symbols","值")])}

<h2>Phase 3 执行敏感性摘要</h2>
<p>重点不是宣传收益，而是提醒：这个策略对成交口径很敏感。启动 live canary 只是小仓验证“shadow、paper、live 是否一致”，不是证明已经能大仓赚钱。</p>
{table(phase3.get("execution_rows") or [], [("scenario","执行口径"),("cost","成本"),("cum","累计"),("dd","回撤"),("mean","均值"),("win","胜率")])}

<h2>容量粗检</h2>
{table(phase3.get("liquidity_rows") or [], [("scenario","执行口径"),("participation","参与率"),("p10_capacity","P10 容量"),("median_capacity","中位容量")])}

<h2>残留仓位</h2>
<p>如果这里非空，live shell 会因为 residual blocker 拒绝开新篮子。必须先平掉，或人工确认这个仓位不属于 Rank213。</p>
{table(residual_rows, [("symbol","symbol"),("side","side"),("qty","qty"),("entry","entry"),("pnl","unrealized pnl"),("why","classification")]) if residual_rows else "<p class='ok'>没有检测到旧 Rank213 residual_open_on_exchange。</p>"}

<h2>人工启动顺序</h2>
<p><code>shadow runner</code> 每天 00:01Z 产出信号；<code>live canary</code> 00:02:15Z 读取同一份 current decision；<code>pending manager</code> 只管理 maker pending。实际启用 timer 前，需要先处理残留仓位。</p>
<p class="small">相关页面：<a href="rank213_age90_14d_phase3_validation.html">Phase 3 验证</a> | <a href="rank213_age90_daily_shadow_runner.html">Daily shadow</a></p>
</main></body></html>"""
    return html


def main() -> int:
    payload = build_payload()
    save_json(SUMMARY_PATH, payload)
    SITE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SITE_PATH.write_text(build_html(payload), encoding="utf-8")
    print(f"wrote {SUMMARY_PATH.relative_to(ROOT)}")
    print(f"wrote {SITE_PATH.relative_to(ROOT)}")
    print(json.dumps({"launch_status": payload["launch_status"], "launch_blockers": payload["launch_blockers"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
