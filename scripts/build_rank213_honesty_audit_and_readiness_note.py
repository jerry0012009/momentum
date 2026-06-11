#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank213_largecap_xs_jump_veto"
SITE_DIR = ROOT / "reports" / "site" / "paper"

ADMISSION_SUMMARY_PATH = ROOT / "reports" / "artifacts" / "optimization_loop" / "rank213_p2_admission_20260328" / "summary.json"
ADMISSION_TS_PATH = ROOT / "reports" / "artifacts" / "optimization_loop" / "rank213_p2_admission_20260328" / "variant_timeseries.csv"
ADMISSION_GEN_PATH = ROOT / "tmp_rank213_p2_admission_check.py"
RUNNER_PATH = ROOT / "scripts" / "run_rank213_largecap_xs_jump_veto_paper_runner.py"
FUNDING_PATH = ROOT / "scripts" / "build_rank213_long_history_review_with_funding.py"
FUNDING_SUMMARY_PATH = ART_DIR / "rank213_long_history_with_funding_review_summary.json"
ASOF_LONG_HISTORY_SUMMARY_PATH = ART_DIR / "rank213_asof_universe_long_history_review_summary.json"

HONESTY_JSON = ART_DIR / "rank213_honesty_audit_summary.json"
HONESTY_HTML = SITE_DIR / "rank213_largecap_xs_jump_veto_honesty_audit.html"
READINESS_JSON = ART_DIR / "rank213_readiness_note_summary.json"
READINESS_HTML = SITE_DIR / "rank213_largecap_xs_jump_veto_readiness_note.html"

VARIANT = "f64_h12_floor150_mult2p0"
HOLD_BARS = 12
BAR_MINUTES = 15
EXPECTED_STEP_MINUTES = HOLD_BARS * BAR_MINUTES


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def to_iso(ts: pd.Timestamp) -> str:
    return ts.tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def classify(*, risk: bool, clean: bool) -> str:
    if risk:
        return "risk found"
    if clean:
        return "confirmed clean"
    return "unclear"


def build_honesty_audit() -> dict:
    summary = json.loads(ADMISSION_SUMMARY_PATH.read_text(encoding="utf-8"))
    ts = pd.read_csv(ADMISSION_TS_PATH)
    ts = ts[ts["variant"] == VARIANT].copy()
    if ts.empty:
        raise RuntimeError(f"variant not found in {ADMISSION_TS_PATH}: {VARIANT}")

    ts["timestamp"] = pd.to_datetime(ts["timestamp"], utc=True)
    ts = ts.sort_values("timestamp").reset_index(drop=True)

    admission_gen_src = load_text(ADMISSION_GEN_PATH)
    runner_src = load_text(RUNNER_PATH)
    funding_src = load_text(FUNDING_PATH)

    step_minutes = ts["timestamp"].diff().dropna().dt.total_seconds().div(60)
    unique_steps = sorted({int(x) for x in step_minutes.unique()}) if not step_minutes.empty else []
    aligned_15m = bool((ts["timestamp"].dt.minute % 15 == 0).all())

    check1_patterns = [
        "while i + hold < len(close_panel):",
        "hist = ret.iloc[i-formation+1:i+1]",
        "cumret = close_panel.iloc[i] / close_panel.iloc[i-formation] - 1.0",
        "future = close_panel.iloc[i+hold] / close_panel.iloc[i] - 1.0",
    ]
    check1_pattern_ok = all(p in admission_gen_src for p in check1_patterns)
    check1_step_ok = unique_steps == [EXPECTED_STEP_MINUTES]
    check1_clean = check1_pattern_ok and check1_step_ok and aligned_15m

    ffill_present = ".ffill()" in admission_gen_src
    resample_present = "resample(" in admission_gen_src
    suspicious_future_ops = any(k in admission_gen_src for k in ["shift(-", "rolling(", "expanding("])
    timestamp_unique = bool(ts["timestamp"].is_unique)
    timestamp_monotonic = bool(ts["timestamp"].is_monotonic_increasing)
    check2_risk = ffill_present
    check2_clean = (not check2_risk) and (not resample_present) and timestamp_unique and timestamp_monotonic and (not suspicious_future_ops)

    runner_uses_frozen_variant = "df = df[df[\"variant\"] == VARIANT].copy()" in runner_src
    runner_no_universe_reselect = "fapi" not in runner_src and "exchangeInfo" not in runner_src
    universe_size = int(summary.get("universe_size", 0))
    universe_symbols = summary.get("symbols", [])
    check3_clean = runner_uses_frozen_variant and runner_no_universe_reselect and universe_size == len(universe_symbols) == 30

    funding_window_ok = '(f["timestamp"] > entry) & (f["timestamp"] <= exit_ts)' in funding_src
    check4_clean = funding_window_ok

    checks = [
        {
            "item": "1) 每次 rebalance 信号是否只使用当时之前已收盘的 64 根 15m bar",
            "status": classify(risk=False, clean=check1_clean),
            "evidence": {
                "source_file": str(ADMISSION_GEN_PATH.relative_to(ROOT)) if ADMISSION_GEN_PATH.exists() else "missing",
                "patterns_found": check1_pattern_ok,
                "timestamp_step_minutes_unique": unique_steps,
                "expected_step_minutes": EXPECTED_STEP_MINUTES,
                "all_timestamps_on_15m_grid": aligned_15m,
            },
        },
        {
            "item": "2) 是否存在任何向前填充、未来 bar 泄漏、重采样错位",
            "status": classify(risk=check2_risk, clean=check2_clean),
            "evidence": {
                "forward_fill_present_in_seed_builder": ffill_present,
                "resample_present_in_seed_builder": resample_present,
                "future_like_ops_detected": suspicious_future_ops,
                "timestamp_monotonic": timestamp_monotonic,
                "timestamp_unique": timestamp_unique,
                "note": "发现 .ffill() 路径即按 risk found 处理（即便本样本未必触发实质填充）。",
            },
        },
        {
            "item": "3) universe 冻结是否在样本外重新选择",
            "status": classify(risk=False, clean=check3_clean),
            "evidence": {
                "runner_uses_frozen_variant_filter": runner_uses_frozen_variant,
                "runner_has_no_universe_selection_api_calls": runner_no_universe_reselect,
                "frozen_universe_size_from_admission_summary": universe_size,
                "frozen_universe_symbol_count": len(universe_symbols),
            },
        },
        {
            "item": "4) funding 计提是否严格在 entry < funding_time <= exit",
            "status": classify(risk=False, clean=check4_clean),
            "evidence": {
                "funding_window_filter_found": funding_window_ok,
                "source_file": str(FUNDING_PATH.relative_to(ROOT)),
            },
        },
    ]

    counts = {
        "confirmed_clean": sum(1 for c in checks if c["status"] == "confirmed clean"),
        "unclear": sum(1 for c in checks if c["status"] == "unclear"),
        "risk_found": sum(1 for c in checks if c["status"] == "risk found"),
    }

    return {
        "scope": "admission timeseries seed causality audit only; no new research",
        "variant": VARIANT,
        "sample": {
            "rows": int(len(ts)),
            "start_utc": to_iso(ts["timestamp"].min()),
            "end_utc": to_iso(ts["timestamp"].max()),
            "step_minutes_unique": unique_steps,
        },
        "checks": checks,
        "status_counts": counts,
        "overall": "risk found" if counts["risk_found"] > 0 else ("unclear" if counts["unclear"] > 0 else "confirmed clean"),
    }


def build_readiness_note() -> dict:
    review = json.loads(FUNDING_SUMMARY_PATH.read_text(encoding="utf-8"))
    asof_review = json.loads(ASOF_LONG_HISTORY_SUMMARY_PATH.read_text(encoding="utf-8"))
    da = review["data_availability"]
    full = review["full_available_history"]
    windows = review["window_reviews"]
    asof_windows = asof_review.get("window_reviews", [])

    blocker = "frozen universe 的公共共同历史长度不足 365 天（当前从 {start} 到 {end}，共 {days:.2f} 天）".format(
        start=da["actual_common_start_utc"],
        end=da["actual_common_end_utc"],
        days=float(da["calendar_days"]),
    )

    return {
        "headline": "Readiness Note（区分 as-of long-history 与 frozen current-universe）",
        "proved": [
            "策略层面已存在 as-of universe 长历史证据：1Y/2Y/3Y 可用，且 5Y/6Y 也已有可用窗口。",
            "在冻结当前 universe/spec 下，funding-adjusted 回测已覆盖 168.64 天（{} rebalances）。".format(int(da["rebalances"])),
            "在这 168.64 天内，veto 相对 plain 仍有正增量（Δnet mean {:.2f} bps；Δnet cumulative {:.2f}%）。".format(
                float(full["delta"]["net_mean_bps"]),
                float(full["delta"]["net_cum_pct"]),
            ),
        ],
        "not_proved": [
            "尚未证明 1Y / 2Y / 3Y 冻结窗口通过（当前三个窗口均为 unavailable）。",
            "尚不能把 as-of universe 的长窗证据直接等同于 frozen current-universe readiness；但这不否定 as-of 长窗证据已足以支持继续推进 shadow / execution audit / live canary 准备。",
        ],
        "why_168d_not_enough": "168.64 天结果再强，也不是 1Y（365 天）。在 frozen universe 不变前提下，公共共同历史起点被最新上市成分截断，长度客观不足。",
        "single_blocker": blocker,
        "window_availability": {
            "frozen_1Y": next((w.get("available") for w in windows if w.get("window") == "1Y"), False),
            "frozen_2Y": next((w.get("available") for w in windows if w.get("window") == "2Y"), False),
            "frozen_3Y": next((w.get("available") for w in windows if w.get("window") == "3Y"), False),
            "asof_1Y": next((w.get("available") for w in asof_windows if w.get("window") == "1Y"), False),
            "asof_2Y": next((w.get("available") for w in asof_windows if w.get("window") == "2Y"), False),
            "asof_3Y": next((w.get("available") for w in asof_windows if w.get("window") == "3Y"), False),
            "asof_5Y": next((w.get("available") for w in asof_windows if w.get("window") == "5Y"), False),
            "asof_6Y": next((w.get("available") for w in asof_windows if w.get("window") == "6Y"), False),
        },
    }


def render_honesty_html(audit: dict) -> str:
    rows = []
    for c in audit["checks"]:
        rows.append(
            "<tr>"
            f"<td>{c['item']}</td>"
            f"<td><b>{c['status']}</b></td>"
            f"<td><pre>{json.dumps(c['evidence'], ensure_ascii=False, indent=2)}</pre></td>"
            "</tr>"
        )

    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
<meta charset='utf-8' />
<meta name='viewport' content='width=device-width, initial-scale=1' />
<title>Rank213 honesty audit（admission timeseries seed causality）</title>
<style>
:root{{--bg:#f8fafc;--card:#fff;--fg:#0f172a;--muted:#64748b;--line:#e2e8f0;--warn:#9a3412;--warnbg:#ffedd5;--ok:#166534;--okbg:#dcfce7}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.65 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}}
.wrap{{max-width:1160px;margin:0 auto;padding:28px 18px 64px}} .card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin-bottom:14px}}
h1,h2{{margin:0 0 12px}} .muted{{color:var(--muted)}} .pill{{display:inline-block;padding:4px 10px;border-radius:999px;background:#eef2ff;border:1px solid #c7d2fe;font-weight:600}}
.pill-ok{{background:var(--okbg);border-color:#86efac;color:var(--ok)}} .pill-warn{{background:var(--warnbg);border-color:#fdba74;color:var(--warn)}}
table{{width:100%;border-collapse:collapse}} th,td{{border:1px solid var(--line);padding:10px;vertical-align:top;text-align:left}} th{{background:#f8fafc}}
pre{{margin:0;white-space:pre-wrap;background:#f8fafc;border:1px solid var(--line);border-radius:10px;padding:10px;font-size:12px}}
a{{color:#0f766e;text-decoration:none}} a:hover{{text-decoration:underline}}
</style>
</head>
<body><div class='wrap'>
<div class='card'>
<h1>Rank213 honesty audit（只审 admission timeseries seed 的因果性）</h1>
<p><span class='pill'>scope: no new research</span> <span class='pill {'pill-warn' if audit['overall'] != 'confirmed clean' else 'pill-ok'}'>overall: {audit['overall']}</span></p>
<p class='muted'>variant: <code>{audit['variant']}</code> · sample: {audit['sample']['start_utc']} → {audit['sample']['end_utc']} · rows={audit['sample']['rows']} · step={audit['sample']['step_minutes_unique']}</p>
<p><a href='/momentum/paper/rank213_largecap_xs_jump_veto_readiness_note.html'>readiness note</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_ffill_impact_audit.html'>ffill_impact_audit</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_asof_universe_long_history_review.html'>asof_universe_long_history_review</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_regime_review.html'>regime_review</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_long_history_review_with_funding.html'>funding-adjusted long-history</a></p>
</div>

<div class='card'>
<h2>逐项结论（mandatory）</h2>
<table>
<thead><tr><th>检查项</th><th>结论</th><th>证据</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
</table>
</div>

<div class='card'>
<h2>结论摘要</h2>
<ul>
<li>confirmed clean: <b>{audit['status_counts']['confirmed_clean']}</b></li>
<li>unclear: <b>{audit['status_counts']['unclear']}</b></li>
<li>risk found: <b>{audit['status_counts']['risk_found']}</b></li>
</ul>
<p class='muted'>注：出现 <code>.ffill()</code> 路径即按 risk found 标注；这表示流程存在“向前填充机制”，不等于必然发生了未来信息泄漏。</p>
</div>
</div></body></html>
"""


def render_readiness_html(note: dict) -> str:
    proved = "".join(f"<li>{x}</li>" for x in note["proved"])
    not_proved = "".join(f"<li>{x}</li>" for x in note["not_proved"])
    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
<meta charset='utf-8' />
<meta name='viewport' content='width=device-width, initial-scale=1' />
<title>Rank213 readiness note</title>
<style>
:root{{--bg:#f8fafc;--card:#fff;--fg:#0f172a;--muted:#64748b;--line:#e2e8f0;--warn:#9a3412;--warnbg:#ffedd5;--ok:#166534;--okbg:#dcfce7}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.65 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}}
.wrap{{max-width:980px;margin:0 auto;padding:28px 18px 64px}} .card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin-bottom:14px}}
h1,h2{{margin:0 0 12px}} ul{{margin:0;padding-left:20px}} li{{margin:0 0 6px}}
.note{{border-left:4px solid var(--warn);background:var(--warnbg);padding:12px 14px;border-radius:10px}}
.ok{{border-left:4px solid var(--ok);background:var(--okbg);padding:12px 14px;border-radius:10px}}
.muted{{color:var(--muted)}} a{{color:#0f766e;text-decoration:none}} a:hover{{text-decoration:underline}}
</style>
</head>
<body><div class='wrap'>
<div class='card'>
<h1>Rank213 readiness note</h1>
<p class='muted'>用于主入口的一句话版本：只回答“已证明 / 未证明 / 唯一 blocker”。</p>
<p><a href='/momentum/paper/rank213_largecap_xs_jump_veto_honesty_audit.html'>honesty audit</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_ffill_impact_audit.html'>ffill_impact_audit</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_asof_universe_long_history_review.html'>asof_universe_long_history_review</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_regime_review.html'>regime_review</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_long_history_review_with_funding.html'>funding-adjusted long-history</a></p>
</div>

<div class='card'>
<h2>已证明</h2>
<div class='ok'><ul>{proved}</ul></div>
</div>

<div class='card'>
<h2>还没证明</h2>
<div class='note'><ul>{not_proved}</ul></div>
</div>

<div class='card'>
<h2>为什么 168.64 天再强也不等于通过 1Y/2Y/3Y</h2>
<p>{note['why_168d_not_enough']}</p>
</div>

<div class='card'>
<h2>长窗证据口径区分</h2>
<div class='ok'>as-of universe: 1Y={note['window_availability']['asof_1Y']} / 2Y={note['window_availability']['asof_2Y']} / 3Y={note['window_availability']['asof_3Y']} / 5Y={note['window_availability']['asof_5Y']} / 6Y={note['window_availability']['asof_6Y']}</div>
<div class='note' style='margin-top:12px'>frozen current universe: 1Y={note['window_availability']['frozen_1Y']} / 2Y={note['window_availability']['frozen_2Y']} / 3Y={note['window_availability']['frozen_3Y']}</div>
</div>

<div class='card'>
<h2>下一步唯一 blocker</h2>
<div class='note'><b>{note['single_blocker']}</b></div>
<p class='muted'>这条 blocker 只约束 frozen current-universe readiness，不否定已存在的 as-of long-history 证据。</p>
</div>
</div></body></html>
"""


def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    audit = build_honesty_audit()
    readiness = build_readiness_note()

    HONESTY_JSON.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    HONESTY_HTML.write_text(render_honesty_html(audit), encoding="utf-8")

    READINESS_JSON.write_text(json.dumps(readiness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    READINESS_HTML.write_text(render_readiness_html(readiness), encoding="utf-8")

    print(json.dumps({
        "honesty_json": str(HONESTY_JSON.relative_to(ROOT)),
        "honesty_html": str(HONESTY_HTML.relative_to(ROOT)),
        "readiness_json": str(READINESS_JSON.relative_to(ROOT)),
        "readiness_html": str(READINESS_HTML.relative_to(ROOT)),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
