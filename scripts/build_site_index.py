#!/usr/bin/env python3
from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
from fnmatch import fnmatch
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SITE_DIR = ROOT / "reports" / "site"
OUT_PATH = SITE_DIR / "index.html"
ART_DIR = ROOT / "reports" / "artifacts"
EMA_ART_DIR = ART_DIR / "ema_psar_raw_alpha"
BREAKOUT_ART_DIR = ART_DIR / "support_breakout_v0_h24"
ALPHA_CLOSURE_ART_DIR = ART_DIR / "alpha_closure_board"
EMA_DUE_PATH = EMA_ART_DIR / "ema_paper_trading_due_guardrail_snapshot.csv"
EMA_HISTORY_PATH = EMA_ART_DIR / "ema_paper_trading_refresh_history.csv"
BREAKOUT_SCOPE_PATH = BREAKOUT_ART_DIR / "avoid_fluctuating_scope_verdict_20bps.csv"
BREAKOUT_REFRESH_RECHECK_GLOB = "avoid_fluctuating_refresh_recheck_*_20bps.csv"
BREAKOUT_REVISIT_GUARD_PATH = BREAKOUT_ART_DIR / "avoid_fluctuating_revisit_guard_20bps.csv"
RANK2_CLOSEOUT_SNAPSHOT_PATH = ALPHA_CLOSURE_ART_DIR / "small_live_rank2_closeout_snapshot_v1.csv"
RANK_REGISTRY_TABLE_PATH = ART_DIR / "rank_registry" / "full_rank_p3_p2_table.csv"
FACTOR_LIBRARY_ART_DIR = ART_DIR / "factor_research_library"

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")

HIDDEN_FROM_HOME = {
    "paper/binance_event_study_v1_6a_momentum_ignition_report.html",
    "paper/binance_event_study_v1_6_2b_short_reversal.html",
    "paper/binance_event_study_phase2c.html",
    "paper/rank450_event_alpha_research.html",
    "factors/trendline_breakout_navigator/report.html",
    "factors/trendline_event_foundation/report.html",
    "factors/trendline_segment_backtest/report.html",
    "factors/trendline_segment_backtest_interval_sweep/report.html",
    "factors/trendline_segment_backtest_cross_market/report.html",
    "factors/trendline_segment_crypto_rebound_scan/report.html",
    "factors/trendline_event_slope_audit/report.html",
    "factors/trendline_confirmation_ladder/report.html",
    "factors/pytrendline_research/report.html",
    "factors/pytrendline_event_validation_v3/report.html",
    "factors/pytrendline_event_validation_v3_crypto_180d/report.html",
    "factors/pytrendline_event_validation_v3_crypto_extension_plan_v1/report.html",
    "factors/pytrendline_event_validation_v3_breakout_side_audit/report.html",
    "factors/pytrendline_event_validation_v3_breakout_metric_reaudit/report.html",
    "factors/pytrendline_event_validation_v3_sampler_fix_spec/report.html",
    "factors/pytrendline_event_validation_v3_sampler_fix_r2_impl/report.html",
    "factors/pytrendline_event_validation_v3_sampler_fix_r3_impl/report.html",
    "factors/pytrendline_event_validation_v3_sampler_fix_rerun_a4c/report.html",
}

FEATURED_ORDER = [
    "factor_research_library/index.html",
    "factors/rank_strategy_hub/report.html",
    "factors/rank_registry_p3_p2/report.html",
    "factors/phase2_strategy_portal/report.html",
    "phases/index.html",
    "factors/paper_phase2a_event_v4_sl_only/report.html",
    "factors/rank32b/report.html",
    "factors/rank32b_canary/report.html",
    "factors/live_trading_center/report.html",
    "factors/alpha_closure_board/report.html",
]


BJ_TZ = timezone(timedelta(hours=8), name="Asia/Shanghai")

# Aggregate freshness for "board / index" style pages so their card time reflects
# relevant child pages or source docs, not only the page file itself.
AGGREGATE_FRESHNESS: dict[str, list[str]] = {
    "factors/rank_registry_p3_p2/report.html": [
        "reports/site/factors/rank_registry_p3_p2/report.html",
        "reports/artifacts/rank_registry/full_rank_p3_p2_table.csv",
        "research/strategy_review/*.md",
        "research/optimization_loop/*.md",
    ],
    "plans/report.html": [
        "reports/site/plans/*.html",
        "docs/*.md",
        "research/strategy_review/*.md",
        "research/optimization_loop/*.md",
    ],
    "factors/alpha_closure_board/report.html": [
        "reports/site/factors/alpha_closure_board/report.html",
        "reports/site/factors/structure_event_mainline/report.html",
        "reports/site/factors/support_breakout_v0_h24/report.html",
        "reports/site/factors/support_breakout_v0_fib_ab/report.html",
        "reports/site/factors/ema_psar_raw_alpha/report.html",
        "reports/site/factors/pytrendline_event_validation_v3_final_verdict/report.html",
        "reports/site/plans/*.html",
        "docs/TODO.md",
        "research/strategy_review/*.md",
        "research/optimization_loop/*.md",
    ],
    "factors/structure_event_mainline/report.html": [
        "reports/site/factors/structure_event_mainline/report.html",
        "reports/site/factors/support_breakout_v0_h24/report.html",
        "reports/site/factors/support_breakout_v0_fib_ab/report.html",
        "reports/site/factors/ema_psar_raw_alpha/report.html",
        "reports/site/factors/alpha_closure_board/report.html",
        "reports/site/factors/trendline_pyindicator_track/report.html",
        "reports/site/factors/trendline_pytrendline_track/report.html",
        "reports/site/plans/*.html",
        "docs/TODO.md",
        "research/strategy_review/*.md",
        "research/optimization_loop/*.md",
    ],
    "factors/phase2_strategy_portal/report.html": [
        "reports/site/factors/phase2_strategy_portal/report.html",
        "reports/site/factors/paper_phase2a_event_v4_sl_only/report.html",
        "reports/artifacts/paper_phase2a_event_v4_sl_only/status.csv",
        "reports/artifacts/paper_phase2a_event_v4_sl_only/open_positions.csv",
        "reports/artifacts/paper_phase2a_event_v4_sl_only/live_open_positions.csv",
        "reports/artifacts/paper_phase2a_event_v4_sl_only/run_log.csv",
        "config/execution/phase2a_event_v4_trail_paper.json",
        "reports/site/paper/rank450/index.html",
        "reports/site/paper/binance_event_study_hub.html",
    ],
}

RECENT_REPORT_LIMIT = 8
RECENT_NOTE_LIMIT = 10
RECENT_NOTE_WINDOW_HOURS = 36


@dataclass
class SiteEntry:
    rel_path: str
    title: str
    section: str
    updated_at: datetime
    updated_text: str
    freshness_note: str = "page"


@dataclass
class ActivityEntry:
    kind: str
    title: str
    rel_path: str
    updated_at: datetime
    updated_text: str
    note: str


def format_beijing(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).astimezone(BJ_TZ).strftime("%Y-%m-%d %H:%M 北京时间")


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def read_latest_glob_csv_rows(directory: Path, pattern: str) -> list[dict[str, str]]:
    matches = [path for path in directory.glob(pattern) if path.is_file()]
    if not matches:
        return []
    latest_path = max(matches, key=lambda path: path.stat().st_mtime)
    return read_csv_rows(latest_path)


def _rank_num(rank: str) -> str | None:
    m = re.search(r"(\d+)", rank or "")
    return m.group(1) if m else None


def _same_rank_reports(entries: list[SiteEntry], rank: str) -> list[str]:
    num = _rank_num(rank)
    if not num:
        return []
    pat = re.compile(rf"(^|_)rank{num}(?:_|$)", re.IGNORECASE)
    out: list[str] = []
    for e in entries:
        if not e.rel_path.startswith("factors/") or not e.rel_path.endswith("/report.html"):
            continue
        dir_name = e.rel_path.split("/")[1]
        if dir_name.startswith("rank_registry_p3_p2"):
            continue
        if pat.search(dir_name):
            out.append(e.rel_path)
    return sorted(set(out))


def render_p2p3_fixed_links(entries: list[SiteEntry]) -> tuple[str, int, int]:
    rows = read_csv_rows(RANK_REGISTRY_TABLE_PATH)
    if not rows:
        return "<p class='muted'>暂无 P2/P3 注册表数据。</p>", 0, 0

    items: list[str] = []
    missing = 0
    for row in rows:
        rank = (row.get("rank") or "-").strip() or "-"
        stage = (row.get("stage") or "-").strip() or "-"
        status = (row.get("status") or "-").strip() or "-"
        entry = f"factors/rank_registry_p3_p2_entries/{rank}/report.html"
        reps = _same_rank_reports(entries, rank)
        if not reps:
            missing += 1
        rep_text = f"独立报告 {len(reps)}"
        items.append(
            f"<li><a href='{escape(entry)}'><code>{escape(rank)}</code></a>"
            f" <span class='muted'>({escape(stage)} / {escape(status)} · {escape(rep_text)})</span></li>"
        )

    return f"<ul>{''.join(items)}</ul>", missing, len(rows)


def parse_utc_label(label: str) -> datetime | None:
    text = (label or "").strip()
    if not text or text == "-":
        return None
    for fmt in ("%Y-%m-%d %H:%M UTC", "%Y-%m-%d %H:%M:%S UTC"):
        try:
            return datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def parse_float_label(label: str) -> float | None:
    text = (label or "").strip().rstrip("h")
    if not text or text == "-":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def format_due_gap(target: datetime, now: datetime | None = None) -> str:
    ref = now or datetime.now(timezone.utc)
    delta_seconds = int(round((target - ref).total_seconds()))
    if delta_seconds <= 0:
        overdue_seconds = abs(delta_seconds)
        if overdue_seconds < 3600:
            return f"已超时约 {max(1, round(overdue_seconds / 60))} 分钟"
        return f"已超时约 {overdue_seconds / 3600:.1f} 小时"
    if delta_seconds < 3600:
        return f"约 {max(1, round(delta_seconds / 60))} 分钟 后到点"
    return f"约 {delta_seconds / 3600:.1f} 小时 后到点"


def format_remaining_gap(target: datetime, now: datetime | None = None) -> str:
    ref = now or datetime.now(timezone.utc)
    delta_seconds = max(0, int(round((target - ref).total_seconds())))
    if delta_seconds < 3600:
        return f"约 {max(1, round(delta_seconds / 60))} 分钟"
    return f"约 {delta_seconds / 3600:.1f} 小时"


def enrich_due_rows(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    now = datetime.now(timezone.utc)
    enriched: list[dict[str, object]] = []
    for idx, row in enumerate(rows, 1):
        next_close_ts = parse_utc_label(row.get("next_expected_close_utc") or "")
        due_bucket = str(row.get("due_bucket") or "")
        dynamic_bucket = due_bucket or "waiting_not_due"
        dynamic_gap = str(row.get("relative_due_gap") or "-")
        if next_close_ts is not None:
            dynamic_gap = format_due_gap(next_close_ts, now)
            dynamic_bucket = "overdue_refresh_check" if next_close_ts <= now else "waiting_not_due"
            if next_close_ts > now and (next_close_ts - now).total_seconds() <= 6 * 3600:
                dynamic_bucket = "due_soon"
        enriched.append(
            {
                **row,
                "_sort_rank": next_close_ts or datetime.max.replace(tzinfo=timezone.utc),
                "dynamic_due_bucket": dynamic_bucket,
                "dynamic_relative_due_gap": dynamic_gap,
                "dynamic_is_due": dynamic_bucket in {"due_now_refresh_window", "overdue_refresh_check"},
                "_source_rank": idx,
            }
        )
    return sorted(enriched, key=lambda row: (row["_sort_rank"], row["_source_rank"]))


def compute_breakout_guard_state(rows: list[dict[str, str]]) -> dict[str, str]:
    if not rows:
        return {}
    lookup = {(row.get("check") or "").strip(): row for row in rows}
    now = datetime.now(timezone.utc)
    cooldown_hours = parse_float_label(lookup.get("rerun_cooldown_hours", {}).get("value") or "") or 6.0
    last_generated_at = parse_utc_label(lookup.get("last_heavy_recheck_generated_at_utc", {}).get("value") or "")
    last_checked_bar = parse_utc_label(lookup.get("last_heavy_recheck_checked_bar_utc", {}).get("value") or "")
    current_cache_bar = parse_utc_label(lookup.get("current_cache_latest_bar_utc", {}).get("value") or "")

    cache_ahead = bool(last_checked_bar and current_cache_bar and current_cache_bar > last_checked_bar)
    cooldown_active = False
    cooldown_remaining = "-"
    elapsed_since_recheck = "-"
    if last_generated_at is not None:
        cooldown_deadline = last_generated_at + timedelta(hours=cooldown_hours)
        cooldown_active = cooldown_deadline > now
        cooldown_remaining = format_remaining_gap(cooldown_deadline, now)
        elapsed_hours = max(0.0, (now - last_generated_at).total_seconds() / 3600)
        elapsed_since_recheck = f"{elapsed_hours:.1f}h"

    if cache_ahead and cooldown_active:
        verdict = "cache_advanced_but_recent_recheck_cooldown_hold"
        trigger = "current_cache_latest_bar_utc > last_heavy_recheck_checked_bar_utc AND recent_heavy_recheck_within_cooldown"
        action = f"cooldown hold；等剩余 {cooldown_remaining} 冷却走完后，若 cache 仍领先，再只重跑 1 次 heavy recheck"
    elif cache_ahead:
        verdict = "cache_advanced_rerun_worth_checking"
        trigger = "current_cache_latest_bar_utc > last_heavy_recheck_checked_bar_utc"
        action = "cache tail 仍领先；现在值得只重跑 1 次 heavy breakout refresh recheck"
    else:
        verdict = "same_sample_hold_no_rerun"
        trigger = "wait until current_cache_latest_bar_utc moves beyond last_heavy_recheck_checked_bar_utc"
        action = "继续 hold same-sample freeze；先不要重跑 heavy breakout refresh"

    return {
        "guard_verdict": verdict,
        "guard_trigger": trigger,
        "guard_action": action,
        "guard_last": lookup.get("last_heavy_recheck_checked_bar_utc", {}).get("value") or "-",
        "guard_now": lookup.get("current_cache_latest_bar_utc", {}).get("value") or "-",
        "guard_delta": lookup.get("cache_tail_delta_vs_last_recheck", {}).get("value") or "-",
        "cooldown_active": "yes" if cooldown_active else "no",
        "cooldown_remaining": cooldown_remaining,
        "elapsed_since_recheck": elapsed_since_recheck,
    }


def render_ops_watch() -> str:
    due_rows = enrich_due_rows(read_csv_rows(EMA_DUE_PATH))
    history_rows = read_csv_rows(EMA_HISTORY_PATH)
    breakout_rows = read_csv_rows(BREAKOUT_SCOPE_PATH)
    breakout_refresh_rows = read_latest_glob_csv_rows(BREAKOUT_ART_DIR, BREAKOUT_REFRESH_RECHECK_GLOB)
    breakout_guard_rows = read_csv_rows(BREAKOUT_REVISIT_GUARD_PATH)
    rank2_closeout_rows = read_csv_rows(RANK2_CLOSEOUT_SNAPSHOT_PATH)

    ops_items: list[str] = []

    if due_rows:
        due_now = [row for row in due_rows if bool(row.get("dynamic_is_due"))]
        due_soon = next((row for row in due_rows if row.get("dynamic_due_bucket") == "due_soon"), due_rows[0])
        scope = escape(str(due_soon.get("deployment_scope") or "-"))
        gap = escape(str(due_soon.get("dynamic_relative_due_gap") or "-"))
        next_close = escape(str(due_soon.get("next_expected_close_utc") or "-"))
        if due_now:
            due_labels = "；".join(
                escape(f"{row.get('deployment_scope', '-')}（{row.get('dynamic_relative_due_gap', '-')})") for row in due_now[:3]
            )
            ops_items.append(
                f"<li><b>EMA ledger：</b>首页已按 <code>next_expected_close_utc</code> 动态重算时钟；当前已有 <b>{len(due_now)}</b> 条 lane 进入 <code>due_now / overdue</code>，默认应先跑 <code>python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due</code>；最靠前的是 {due_labels}。</li>"
            )
        else:
            ops_items.append(
                f"<li><b>EMA ledger：</b>首页已按 <code>next_expected_close_utc</code> 动态重算时钟；当前还没有 <code>due_now / overdue</code> lane。最靠前的是 <b>{scope}</b>，下一次 close 约在 <code>{next_close}</code>，<b>{gap}</b>。</li>"
            )

    if history_rows:
        latest_recorded = max(
            history_rows,
            key=lambda row: parse_utc_label(row.get("history_recorded_at_utc") or "") or datetime.min.replace(tzinfo=timezone.utc),
        )
        latest_bar_row = max(
            history_rows,
            key=lambda row: parse_utc_label(row.get("latest_completed_bar_utc") or "") or datetime.min.replace(tzinfo=timezone.utc),
        )
        recorded_at = escape(latest_recorded.get("history_recorded_at_utc") or "-")
        latest_bar = escape(latest_bar_row.get("latest_completed_bar_utc") or "-")
        scopes = len({(row.get("deployment_scope") or "").strip() for row in history_rows if (row.get("deployment_scope") or "").strip()})
        ops_items.append(
            f"<li><b>EMA continuity：</b><code>ema_paper_trading_refresh_history.csv</code> 已累计 <b>{len(history_rows)}</b> 条 completed-bar rows，覆盖 <b>{scopes}</b> 条 lane；最近一次写入 <code>{recorded_at}</code>，当前 history 里最新 completed bar 截止到 <code>{latest_bar}</code>。</li>"
        )

    if breakout_rows:
        scope_row = next((row for row in breakout_rows if (row.get("question") or "") == "当前最诚实的 scope 是什么"), None)
        blocker_row = next((row for row in breakout_rows if (row.get("question") or "") == "当前最不该误读成什么"), None)
        next_row = next((row for row in breakout_rows if (row.get("question") or "") == "下一次什么才算有效推进"), None)
        if scope_row and blocker_row and next_row:
            ops_items.append(
                "<li><b>Breakout gate：</b>当前 scope 仍是 <code>{scope}</code>；当前最不该误读成 <code>{blocker}</code>（{evidence}）；所以下一刀只有在 {next_step} 时才算有效推进。</li>".format(
                    scope=escape(scope_row.get("current_answer") or "-"),
                    blocker=escape(blocker_row.get("current_answer") or "-"),
                    evidence=escape(blocker_row.get("key_evidence") or "-"),
                    next_step=escape(next_row.get("current_answer") or "-"),
                )
            )

    if breakout_refresh_rows:
        refresh_lookup = {(row.get("check") or "").strip(): row for row in breakout_refresh_rows}
        latest_action = escape(refresh_lookup.get("breakout_event_latest_action_utc", {}).get("value") or "-")
        latest_bar = escape(refresh_lookup.get("v3_cache_latest_bar_utc", {}).get("value") or "-")
        pure_down = escape(refresh_lookup.get("pair_halfsize_pure_down_coverage", {}).get("value") or "-")
        predown_bridge = escape(refresh_lookup.get("pair_halfsize_predown_bridge_12h", {}).get("value") or "-")
        refresh_verdict = escape(refresh_lookup.get("refresh_recheck_verdict", {}).get("value") or "-")
        ops_items.append(
            "<li><b>Breakout fresh recheck：</b>最新 rerun 之后，purged sample 尾部仍停在 <code>{latest_action}</code>，上游 cache 也只刷新到 <code>{latest_bar}</code>；默认 pair candidate 的硬 blocker 仍是 <code>pure down {pure_down}</code>、<code>12h pre-down bridge {predown_bridge}</code>。当前结论仍是 <code>{refresh_verdict}</code>，所以在出现新的 post-tail 事件前，不该再把同类 rerun 当成有效推进。</li>".format(
                latest_action=latest_action,
                latest_bar=latest_bar,
                pure_down=pure_down,
                predown_bridge=predown_bridge,
                refresh_verdict=refresh_verdict,
            )
        )

    if breakout_guard_rows:
        guard_state = compute_breakout_guard_state(breakout_guard_rows)
        guard_verdict = escape(guard_state.get("guard_verdict") or "-")
        guard_delta = escape(guard_state.get("guard_delta") or "-")
        guard_last = escape(guard_state.get("guard_last") or "-")
        guard_now = escape(guard_state.get("guard_now") or "-")
        guard_trigger = escape(guard_state.get("guard_trigger") or "-")
        guard_action = escape(guard_state.get("guard_action") or "-")
        cooldown_note = ""
        if guard_state.get("cooldown_active") == "yes":
            cooldown_note = "；最近一次 heavy recheck 距今约 <code>{elapsed}</code>，冷却还剩 <code>{remaining}</code>".format(
                elapsed=escape(guard_state.get("elapsed_since_recheck") or "-"),
                remaining=escape(guard_state.get("cooldown_remaining") or "-"),
            )
        ops_items.append(
            "<li><b>Breakout rerun guard：</b><code>avoid_fluctuating_revisit_guard_20bps.csv</code> 当前 verdict 为 <code>{guard_verdict}</code>；上次 heavy recheck 对应 cache bar 是 <code>{guard_last}</code>，当前 cache 最新 bar 是 <code>{guard_now}</code>（delta=<code>{guard_delta}</code>）{cooldown_note}。触发条件：<code>{guard_trigger}</code>；默认动作：<code>{guard_action}</code>。</li>".format(
                guard_verdict=guard_verdict,
                guard_last=guard_last,
                guard_now=guard_now,
                guard_delta=guard_delta,
                cooldown_note=cooldown_note,
                guard_trigger=guard_trigger,
                guard_action=guard_action,
            )
        )

    if rank2_closeout_rows:
        row = rank2_closeout_rows[0]
        next_action = escape(row.get("next_allowed_action") or "-")
        current_state = escape(row.get("current_state") or "-")
        closeout_state = escape(row.get("closeout_state") or "-")
        hard_stop = escape(row.get("hard_stop") or "-")
        blockers = escape(row.get("current_blockers") or "-")
        ops_items.append(
            "<li><b>Scout Rank 2 / tiny-live plumbing：</b><code>small_live_rank2_closeout_snapshot_v1.csv</code> 当前仍是 <code>{closeout_state}</code>；{current_state} 当前唯一允许动作仍是 <code>{next_action}</code>。只要触发 <code>{hard_stop}</code>，就继续停在 <code>paper_candidate_only / blocked</code>；当前 blocker 仍包括 <code>{blockers}</code>。</li>".format(
                closeout_state=closeout_state,
                current_state=current_state,
                next_action=next_action,
                hard_stop=hard_stop,
                blockers=blockers,
            )
        )

    if not ops_items:
        return ""

    return """
  <div class=\"section\">
    <h2>Deployment Watch / 当前守门快照</h2>
    <p class=\"muted\">这里直接从当前 artifacts 读取 EMA live ledger、breakout admission blocker 与 Rank 2 paper-candidate closeout 状态，减少只看首页时的判断摩擦。</p>
  </div>
  <div class=\"hero\">
    <ul class=\"ops-list\">{items}</ul>
  </div>
""".format(items="\n".join(ops_items))


def strip_tags(text: str) -> str:
    return WS_RE.sub(" ", TAG_RE.sub("", text)).strip()


def extract_title(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore")
    m = TITLE_RE.search(text)
    if m:
        title = strip_tags(m.group(1))
        if title:
            return title
    m = H1_RE.search(text)
    if m:
        title = strip_tags(m.group(1))
        if title:
            return title
    parts = path.parts
    if len(parts) >= 2:
        return parts[-2].replace("_", " ").replace("-", " ").title()
    return path.stem


def detect_section(rel_path: str) -> str:
    if rel_path.startswith("factors/"):
        return "Factors"
    if rel_path.startswith("reading/"):
        return "Reading"
    if rel_path.startswith("plans/"):
        return "Plans"
    return "Other"


def resolve_aggregate_mtime(rel_path: str, default_path: Path) -> tuple[float, str]:
    patterns = AGGREGATE_FRESHNESS.get(rel_path)
    if not patterns:
        return default_path.stat().st_mtime, "page"
    matched: list[Path] = []
    for pattern in patterns:
        if any(ch in pattern for ch in "*?["):
            matched.extend([p for p in ROOT.rglob("*") if p.is_file() and fnmatch(p.relative_to(ROOT).as_posix(), pattern)])
        else:
            p = ROOT / pattern
            if p.exists() and p.is_file():
                matched.append(p)
    if not matched:
        return default_path.stat().st_mtime, "page"
    freshest = max(matched, key=lambda p: p.stat().st_mtime)
    note = "aggregate" if freshest != default_path else "page"
    return freshest.stat().st_mtime, note


def discover_entries() -> list[SiteEntry]:
    entries: list[SiteEntry] = []
    report_paths = list(SITE_DIR.rglob("report.html"))
    showcase_path = SITE_DIR / "interview_showcase" / "index.html"
    if showcase_path.exists():
        report_paths.append(showcase_path)
    library_path = SITE_DIR / "factor_research_library" / "index.html"
    if library_path.exists():
        report_paths.append(library_path)
    for path in report_paths:
        if path == OUT_PATH:
            continue
        rel_path = path.relative_to(SITE_DIR).as_posix()
        if rel_path == "interview_showcase/index.html" and (SITE_DIR / "factor_research_library" / "index.html").exists():
            continue
        if rel_path in HIDDEN_FROM_HOME:
            continue
        ts, freshness_note = resolve_aggregate_mtime(rel_path, path)
        entries.append(
            SiteEntry(
                rel_path=rel_path,
                title=extract_title(path),
                section=detect_section(rel_path),
                updated_at=datetime.fromtimestamp(ts, tz=timezone.utc),
                updated_text=format_beijing(ts),
                freshness_note=freshness_note,
            )
        )
    entries.sort(key=lambda x: (x.updated_at, x.title.lower()), reverse=True)
    return entries


def render_card(entry: SiteEntry) -> str:
    safe_rel = escape(entry.rel_path)
    freshness_pill = ""
    if entry.freshness_note == "aggregate":
        freshness_pill = '<span class="pill freshness">聚合更新时间</span>'
    return f"""
    <a class=\"card\" href=\"{safe_rel}\" data-report-path=\"{safe_rel}\" data-freshness-note=\"{escape(entry.freshness_note)}\">
      <div class=\"row\">
        <div>
          <h2>{escape(entry.title)}</h2>
          <p class=\"muted\">{safe_rel}</p>
        </div>
        <div class=\"meta\">
          <span class=\"pill\">{escape(entry.section)}</span>
          {freshness_pill}
          <span class=\"pill time js-report-updated\" data-report-path=\"{safe_rel}\" data-freshness-note=\"{escape(entry.freshness_note)}\">最新更新时间：{escape(entry.updated_text)}</span>
        </div>
      </div>
    </a>
""".rstrip()


def _recent_note_entries(dir_name: str, label: str, limit: int, cutoff: datetime) -> list[ActivityEntry]:
    note_dir = ROOT / "research" / dir_name
    note_files: list[tuple[datetime, Path]] = []
    if note_dir.exists():
        for p in note_dir.glob("*.md"):
            st = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)
            if st >= cutoff:
                note_files.append((st, p))
    note_files.sort(reverse=True)
    out: list[ActivityEntry] = []
    for st, p in note_files[:limit]:
        title = p.stem
        if "_" in title:
            title = title.split("_", 2)[-1]
        out.append(
            ActivityEntry(
                kind="note",
                title=title.replace("-", " "),
                rel_path=p.relative_to(ROOT).as_posix(),
                updated_at=st,
                updated_text=st.astimezone(BJ_TZ).strftime("%Y-%m-%d %H:%M 北京时间"),
                note=label,
            )
        )
    return out


def _read_no_progress_reason(rel_path: str) -> str:
    path = ROOT / rel_path
    if not path.exists():
        return "等待下一次真实 completed bar / 新的 forward blocker evidence"
    try:
        first_line = path.read_text(encoding="utf-8", errors="ignore").splitlines()[0].strip()
    except Exception:
        return "等待下一次真实 completed bar / 新的 forward blocker evidence"
    if first_line.startswith("NO_PROGRESS:"):
        reason = first_line.split(":", 1)[-1].strip()
        if reason:
            return reason
    return "等待下一次真实 completed bar / 新的 forward blocker evidence"


def _collapse_repeated_no_progress(activity: list[ActivityEntry]) -> list[ActivityEntry]:
    no_progress = [
        item
        for item in activity
        if item.kind == "note"
        and item.note == "bot3 / optimization_loop 研究笔记"
        and item.title == "no progress"
    ]
    if len(no_progress) <= 1:
        return activity

    latest = max(no_progress, key=lambda item: item.updated_at)
    latest_reason = _read_no_progress_reason(latest.rel_path)
    collapsed = ActivityEntry(
        kind="note",
        title=f"no progress × {len(no_progress)}（已合并）",
        rel_path=latest.rel_path,
        updated_at=latest.updated_at,
        updated_text=latest.updated_text,
        note=f"bot3 / optimization_loop 研究笔记（合并显示；最新原因：{latest_reason}）",
    )
    kept = [item for item in activity if item not in no_progress]
    kept.append(collapsed)
    return kept


def discover_recent_activity(entries: list[SiteEntry]) -> list[ActivityEntry]:
    activity: list[ActivityEntry] = []
    for entry in sorted(entries, key=lambda x: x.updated_at, reverse=True)[:RECENT_REPORT_LIMIT]:
        activity.append(
            ActivityEntry(
                kind="report",
                title=entry.title,
                rel_path=entry.rel_path,
                updated_at=entry.updated_at,
                updated_text=entry.updated_text,
                note="报告页更新",
            )
        )

    cutoff = datetime.now(timezone.utc) - timedelta(hours=RECENT_NOTE_WINDOW_HOURS)
    activity.extend(_recent_note_entries("optimization_loop", "bot3 / optimization_loop 研究笔记", RECENT_NOTE_LIMIT, cutoff))
    activity.extend(_recent_note_entries("strategy_review", "bot2 / strategy_review 决策记录", RECENT_NOTE_LIMIT, cutoff))
    activity = _collapse_repeated_no_progress(activity)

    activity.sort(key=lambda x: x.updated_at, reverse=True)
    return activity[: max(RECENT_REPORT_LIMIT, RECENT_NOTE_LIMIT) + 8]


def render_activity(activity: list[ActivityEntry]) -> str:
    if not activity:
        return "<p class='muted'>最近暂无新的报告或研究笔记。</p>"
    items = []
    for item in activity:
        tag = "Report" if item.kind == "report" else "Note"
        if item.kind == "report":
            items.append(
                f"<a class='activity-item' href='{escape(item.rel_path)}'><div><div class='activity-title'>{escape(item.title)}</div><div class='muted'>{escape(item.rel_path)}</div><div class='muted'>{escape(item.note)}</div></div><div class='activity-meta'><span class='pill'>{tag}</span><span class='pill time'>{escape(item.updated_text)}</span></div></a>"
            )
        else:
            items.append(
                f"<div class='activity-item activity-note'><div><div class='activity-title'>{escape(item.title)}</div><div class='muted'>{escape(item.rel_path)}</div><div class='muted'>{escape(item.note)}</div></div><div class='activity-meta'><span class='pill'>{tag}</span><span class='pill time'>{escape(item.updated_text)}</span></div></div>"
            )
    return "\n".join(items)


def factor_library_stats() -> dict[str, int]:
    def row_count(name: str) -> int:
        path = FACTOR_LIBRARY_ART_DIR / name
        if not path.exists():
            return 0
        try:
            return int(len(pd.read_csv(path)))
        except Exception:
            return 0

    catalog_path = FACTOR_LIBRARY_ART_DIR / "rank_report_catalog.csv"
    ic_path = FACTOR_LIBRARY_ART_DIR / "factor_ic_ir_summary.csv"
    unique_ranks = 0
    reviewed_ic_rows = 0
    pending_ic_rows = 0
    if catalog_path.exists():
        try:
            catalog = pd.read_csv(catalog_path)
            unique_ranks = int(catalog.get("rank_id", pd.Series(dtype=str)).replace("unranked", pd.NA).dropna().nunique())
        except Exception:
            unique_ranks = 0
    if ic_path.exists():
        try:
            ic_df = pd.read_csv(ic_path)
            status = ic_df.get("ic_review_status", pd.Series("needs_strategy_review", index=ic_df.index)).fillna("needs_strategy_review").astype(str)
            reviewed_ic_rows = int(status.eq("reviewed").sum())
            pending_ic_rows = int((~status.eq("reviewed")).sum())
        except Exception:
            reviewed_ic_rows = 0
            pending_ic_rows = row_count("factor_ic_ir_summary.csv")
    return {
        "catalog_rows": row_count("rank_report_catalog.csv"),
        "unique_ranks": unique_ranks,
        "reviewed_ic_rows": reviewed_ic_rows,
        "pending_ic_rows": pending_ic_rows,
        "evidence_rows": row_count("paper_live_evidence_summary.csv"),
    }


def factor_library_stats_html(stats: dict[str, int]) -> str:
    items = [
        ("报告目录", stats.get("catalog_rows", 0)),
        ("唯一 rank", stats.get("unique_ranks", 0)),
        ("审计通过 IC", stats.get("reviewed_ic_rows", 0)),
        ("待审计 IC 候选", stats.get("pending_ic_rows", 0)),
        ("paper/live 证据", stats.get("evidence_rows", 0)),
    ]
    return "<div class='hero-metrics'>" + "".join(
        f"<div class='metric'><span>{escape(label)}</span><b>{int(value)}</b></div>" for label, value in items
    ) + "</div>"


def render_index(entries: list[SiteEntry]) -> str:
    generated_at = datetime.now(timezone.utc).astimezone(BJ_TZ).strftime("%Y-%m-%d %H:%M 北京时间")
    by_path = {entry.rel_path: entry for entry in entries}
    featured = [by_path[p] for p in FEATURED_ORDER if p in by_path]
    featured_set = {entry.rel_path for entry in featured}

    rank_prefixes = ("factors/rank", "factors/paper_rank", "factors/scout_rank")
    rank_entries = [e for e in entries if e.rel_path.startswith(rank_prefixes) and e.rel_path not in featured_set]

    secondary_order = [
        "plans/report.html",
        "reading/quant_digests/report.html",
        "reading/deep_dives/report.html",
        "reading/trendline_alpha_scout/report.html",
    ]
    secondary = [by_path[p] for p in secondary_order if p in by_path and p not in featured_set]

    featured_html = "\n".join(render_card(entry) for entry in featured) if featured else "<p class='muted'>暂无主线入口。</p>"
    rank_html = "\n".join(render_card(entry) for entry in rank_entries[:120]) if rank_entries else "<p class='muted'>暂无 rank 页面。</p>"
    secondary_html = "\n".join(render_card(entry) for entry in secondary) if secondary else "<p class='muted'>暂无次级入口。</p>"
    p2p3_html, p2p3_missing, p2p3_total = render_p2p3_fixed_links(entries)
    library_stats = factor_library_stats_html(factor_library_stats())

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Momentum Reports</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1120px; margin: 34px auto; padding: 0 18px; line-height: 1.6; color: #111827; background: #f8fafc; }}
    h1, h2 {{ line-height: 1.25; }}
    .muted {{ color: #6b7280; }}
    .hero {{ border: 1px solid #e5e7eb; border-radius: 16px; background: white; padding: 20px 22px; margin-bottom: 16px; }}
    .section {{ margin: 20px 0 12px; }}
    .section h2 {{ margin: 0 0 8px; font-size: 20px; }}
    .list {{ display: grid; gap: 12px; }}
    .card {{ display: block; border: 1px solid #e5e7eb; border-radius: 14px; background: white; padding: 16px 18px; color: inherit; text-decoration: none; box-shadow: 0 1px 2px rgba(0,0,0,0.03); }}
    .card:hover {{ border-color: #93c5fd; box-shadow: 0 4px 14px rgba(37,99,235,0.08); }}
    .row {{ display: flex; justify-content: space-between; gap: 16px; align-items: flex-start; }}
    .row h2 {{ margin: 0 0 6px; font-size: 22px; }}
    .row p {{ margin: 0; }}
    .meta {{ display: flex; flex-wrap: wrap; gap: 8px; justify-content: flex-end; min-width: 260px; }}
    .pill {{ display: inline-block; padding: 4px 10px; border-radius: 999px; background: #eef2ff; color: #3730a3; font-size: 12px; white-space: nowrap; }}
    .time {{ background: #ecfeff; color: #155e75; }}
    .freshness {{ background: #fef3c7; color: #92400e; }}
    .hero-metrics {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap:10px; margin:14px 0 10px; }}
    .metric {{ border:1px solid #e5e7eb; border-radius:10px; padding:10px 12px; background:#f9fafb; }}
    .metric span {{ display:block; color:#6b7280; font-size:12px; }}
    .metric b {{ display:block; font-size:24px; line-height:1.15; margin-top:2px; }}
    .quick-nav {{ display:flex; gap:10px; flex-wrap:wrap; margin-top:8px; }}
    .btn {{ display:inline-block; border:1px solid #dbe3ef; border-radius:10px; background:#fff; padding:7px 10px; color:#1d4ed8; text-decoration:none; font-weight:600; font-size:13px; }}
    .btn:hover {{ border-color:#93c5fd; text-decoration:none; }}
    a {{ color: #2563eb; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    @media (max-width: 820px) {{
      .row {{ flex-direction: column; }}
      .meta {{ justify-content: flex-start; min-width: 0; }}
      .hero-metrics {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
  </style>
</head>
<body>
  <div class="hero">
    <h1>Momentum Reports</h1>
    <p class="muted">当前主入口是 <b>Momentum 因子研究结果库</b>：先看全量 rank 分类、IC/IR 横向对比、paper/live 成果矩阵和归档审计，再进入单个 rank 报告。</p>
    {library_stats}
    <p class="muted">推荐路径：<b>因子研究结果库</b> → <b>当前候选 / 运行观察</b> → <b>Top IC/IR</b> → <b>Paper/Live 成果矩阵</b> → <b>全量 Rank 目录</b>。Rank32B、Rank154、Rank213 等已降级为归档/审计材料，不再作为当前主线正例。</p>
    <p class="muted">Phase2 与旧 live/monitor 页面继续保留为执行和归档入口；读者需要先从研究库理解哪些证据仍可作为当前候选，哪些只是审计材料。</p>
    <div class="quick-nav">
      <a class="btn" href="factor_research_library/index.html">因子研究结果库</a>
      <a class="btn" href="factors/rank_strategy_hub/report.html">Rank Strategy Hub</a>
      <a class="btn" href="factors/rank_registry_p3_p2/report.html">P3/P2 Registry</a>
      <a class="btn" href="factors/phase2_strategy_portal/report.html">Phase2 Portal</a>
      <a class="btn" href="factors/paper_phase2a_event_v4_sl_only/report.html">Phase2a SL-only</a>
      <a class="btn" href="factors/rank32b/report.html">Rank32B</a>
      <a class="btn" href="factors/rank32b_canary/report.html">Rank32B Canary</a>
      <a class="btn" href="factors/live_trading_center/report.html">Live Trading Center</a>
      <a class="btn" href="factors/rank32c_live/report.html">Rank32c Live</a>
      <a class="btn" href="paper/rank213_version_overview.html">Rank213 Versions</a>
      <a class="btn" href="paper/rank213c_architecture.html">213c Architecture</a>
    </div>
    <p class="muted">P2/P3 注册表：共 {p2p3_total} 条；当前还需补独立 factors 报告：{p2p3_missing} 条（每条都已有首页固定入口）。</p>
    <p class="muted js-page-generated">共 {len(entries)} 个入口 ｜ 本页生成时间：{escape(generated_at)}</p>
  </div>

  <div class="section">
    <h2>主线入口（Rank Mainline）</h2>
    <p class="muted">这组是首页默认入口，围绕 rank 主线排布。</p>
  </div>
  <div class="list">{featured_html}</div>

  <div class="section">
    <h2>P2/P3 固定入口（首页直达）</h2>
    <p class="muted">这里固定展示注册表的每个 rank，避免因首页列表截断而看不到。</p>
    {p2p3_html}
  </div>

  <div class="section">
    <h2>Rank 页面目录（最近更新优先）</h2>
    <p class="muted">仅展示 rank / paper_rank / scout_rank 页面；更多细节可进 Rank Strategy Hub。</p>
  </div>
  <div class="list">{rank_html}</div>

  <div class="section">
    <h2>次级入口（文档 / 研究）</h2>
  </div>
  <div class="list">{secondary_html}</div>

  <script>
    (function () {{
      const bj = new Intl.DateTimeFormat('zh-CN', {{
        timeZone: 'Asia/Shanghai',
        year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit', hour12: false,
      }});
      function fmt(date) {{
        const parts = bj.formatToParts(date);
        const map = Object.fromEntries(parts.filter(p => p.type !== 'literal').map(p => [p.type, p.value]));
        return `${{map.year}}-${{map.month}}-${{map.day}} ${{map.hour}}:${{map.minute}} 北京时间`;
      }}
      const pageEl = document.querySelector('.js-page-generated');
      if (pageEl && document.lastModified) {{
        const d = new Date(document.lastModified);
        if (!isNaN(d)) {{
          const prefix = pageEl.textContent.split('｜')[0].trim();
          pageEl.textContent = `${{prefix}} ｜ 本页生成时间：${{fmt(d)}}`;
        }}
      }}
      document.querySelectorAll('.js-report-updated').forEach(async (el) => {{
        const path = el.getAttribute('data-report-path');
        const freshnessNote = el.getAttribute('data-freshness-note');
        if (!path || freshnessNote === 'aggregate') return;
        try {{
          const res = await fetch(path, {{ method: 'HEAD', cache: 'no-store' }});
          const lastModified = res.headers.get('Last-Modified');
          if (lastModified) {{
            const d = new Date(lastModified);
            if (!isNaN(d)) el.textContent = `最新更新时间：${{fmt(d)}}`;
          }}
        }} catch (_) {{
          // keep static fallback text generated at build time
        }}
      }});
    }})();
  </script>
</body>
</html>
"""


def main() -> int:
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    entries = discover_entries()
    OUT_PATH.write_text(render_index(entries), encoding="utf-8")
    print("[ok] site index generated")
    print("[site]", OUT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
