#!/usr/bin/env python3
from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BREAKOUT_ART_DIR = ROOT / "reports" / "artifacts" / "support_breakout_v0_h24"
V3_ART_DIR = ROOT / "reports" / "artifacts" / "pytrendline_event_validation_v3"
CACHE_DIR = V3_ART_DIR / "cache"
EVENT_SAMPLE_PATH = V3_ART_DIR / "event_sample_purged.csv"
OUT_PATH = BREAKOUT_ART_DIR / "avoid_fluctuating_revisit_guard_20bps.csv"
REFRESH_GLOB = "avoid_fluctuating_refresh_recheck_*_20bps.csv"


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def parse_ts(raw: str) -> datetime | None:
    text = (raw or "").strip()
    if not text or text == "-":
        return None
    normalized = text.replace("Z", "+00:00")
    for fmt in ("%Y-%m-%d %H:%M UTC", "%Y-%m-%d %H:%M:%S UTC"):
        try:
            return datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    try:
        dt = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def fmt_ts(dt: datetime | None) -> str:
    if dt is None:
        return "-"
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def latest_refresh_recheck_path() -> Path | None:
    matches = [path for path in BREAKOUT_ART_DIR.glob(REFRESH_GLOB) if path.is_file()]
    if not matches:
        return None
    return max(matches, key=lambda path: path.stat().st_mtime)


def latest_cache_timestamp() -> datetime | None:
    latest: datetime | None = None
    for path in sorted(CACHE_DIR.glob("*.csv")):
        rows = read_csv_rows(path)
        if not rows:
            continue
        row = rows[-1]
        dt = parse_ts(row.get("timestamp") or "")
        if dt is None:
            continue
        if latest is None or dt > latest:
            latest = dt
    return latest


def latest_event_timestamp(column: str) -> datetime | None:
    rows = read_csv_rows(EVENT_SAMPLE_PATH)
    latest: datetime | None = None
    for row in rows:
        dt = parse_ts(row.get(column) or "")
        if dt is None:
            continue
        if latest is None or dt > latest:
            latest = dt
    return latest


def hours_delta(later: datetime | None, earlier: datetime | None) -> str:
    if later is None or earlier is None:
        return "-"
    delta_hours = (later - earlier).total_seconds() / 3600
    if abs(delta_hours) < 0.05:
        return "0.0h"
    return f"{delta_hours:.1f}h"


def main() -> int:
    refresh_path = latest_refresh_recheck_path()
    refresh_rows = read_csv_rows(refresh_path) if refresh_path else []
    refresh_lookup = {(row.get("check") or "").strip(): row for row in refresh_rows}

    last_checked_bar = parse_ts(refresh_lookup.get("v3_cache_latest_bar_utc", {}).get("value") or "")
    current_cache_bar = latest_cache_timestamp()
    latest_action = latest_event_timestamp("action_timestamp")
    latest_confirm = latest_event_timestamp("confirm_timestamp")
    pure_down = (refresh_lookup.get("pair_halfsize_pure_down_coverage", {}).get("value") or "-").strip()
    predown_bridge = (refresh_lookup.get("pair_halfsize_predown_bridge_12h", {}).get("value") or "-").strip()

    cache_ahead = False
    if current_cache_bar is not None and last_checked_bar is not None:
        cache_ahead = current_cache_bar > last_checked_bar

    now_utc = datetime.now(timezone.utc)
    cooldown_hours = 6.0
    last_heavy_recheck_generated_at: datetime | None = None
    if refresh_path is not None:
        try:
            last_heavy_recheck_generated_at = datetime.fromtimestamp(refresh_path.stat().st_mtime, tz=timezone.utc)
        except OSError:
            last_heavy_recheck_generated_at = None

    cooldown_active = False
    if last_heavy_recheck_generated_at is not None:
        cooldown_active = (now_utc - last_heavy_recheck_generated_at).total_seconds() / 3600 < cooldown_hours

    if cache_ahead and cooldown_active:
        trigger = "current_cache_latest_bar_utc > last_heavy_recheck_checked_bar_utc AND recent_heavy_recheck_within_cooldown"
        action = (
            "cooldown hold: recent heavy recheck just finished; wait for cooldown expiry, "
            "then rerun once if cache is still ahead"
        )
        verdict = "cache_advanced_but_recent_recheck_cooldown_hold"
        delta_reading = (
            f"local cache 比上次 heavy recheck 新 {hours_delta(current_cache_bar, last_checked_bar)}，"
            f"但最近一次 heavy recheck 距现在仅 {hours_delta(now_utc, last_heavy_recheck_generated_at)}；"
            "先进入短冷却，避免高频重复重跑。"
        )
    elif cache_ahead:
        trigger = "current_cache_latest_bar_utc > last_heavy_recheck_checked_bar_utc"
        action = (
            "cache tail moved forward; rerun heavy breakout refresh recheck "
            "(build_pytrendline_event_validation_v3_report.py --refresh-data + build_support_breakout_v0_reports.py)"
        )
        verdict = "cache_advanced_rerun_worth_checking"
        delta_reading = f"local cache 比上次 heavy recheck 新 {hours_delta(current_cache_bar, last_checked_bar)}；现在值得再跑一次完整 recheck。"
    else:
        trigger = "wait until current_cache_latest_bar_utc moves beyond last_heavy_recheck_checked_bar_utc"
        action = "hold same-sample freeze; do not rerun heavy breakout refresh yet"
        verdict = "same_sample_hold_no_rerun"
        delta_reading = (
            "local cache 还没有比上次 heavy recheck 更往后；继续重跑只会重复同一段样本，"
            "不太可能改写 one_more_gate verdict。"
        )

    rows = [
        {
            "check": "guard_generated_at_utc",
            "value": fmt_ts(now_utc),
            "reading": "本次 rerun guard 生成时间。",
        },
        {
            "check": "last_heavy_recheck_artifact_file",
            "value": refresh_path.name if refresh_path is not None else "-",
            "reading": "最近一次 heavy refresh recheck 对应的 artifact 文件名。",
        },
        {
            "check": "last_heavy_recheck_generated_at_utc",
            "value": fmt_ts(last_heavy_recheck_generated_at),
            "reading": "最近一次 heavy refresh recheck artifact 的生成时点（用于冷却守门）。",
        },
        {
            "check": "hours_since_last_heavy_recheck",
            "value": hours_delta(now_utc, last_heavy_recheck_generated_at),
            "reading": "距离最近一次 heavy refresh recheck 过去了多久。",
        },
        {
            "check": "rerun_cooldown_hours",
            "value": f"{cooldown_hours:.0f}",
            "reading": "当 cache 前推但刚做过 heavy recheck 时，默认短冷却小时数。",
        },
        {
            "check": "rerun_cooldown_active",
            "value": "yes" if cooldown_active else "no",
            "reading": "是否处在短冷却窗口；yes 时默认先不重复重跑。",
        },
        {
            "check": "last_heavy_recheck_checked_bar_utc",
            "value": fmt_ts(last_checked_bar),
            "reading": "上一次 fresh refresh recheck 已经明确检查到的 cache 尾部。",
        },
        {
            "check": "current_cache_latest_bar_utc",
            "value": fmt_ts(current_cache_bar),
            "reading": "当前本地 v3 cache 真正可见的最新 bar；只有它继续往后，breakout 才值得再做 heavy rerun。",
        },
        {
            "check": "cache_tail_delta_vs_last_recheck",
            "value": hours_delta(current_cache_bar, last_checked_bar),
            "reading": delta_reading,
        },
        {
            "check": "current_breakout_event_latest_action_utc",
            "value": fmt_ts(latest_action),
            "reading": "当前 event_sample_purged 里的 breakout 行为尾部；若它没往后，说明样本仍停在旧尾巴。",
        },
        {
            "check": "current_breakout_event_latest_confirm_utc",
            "value": fmt_ts(latest_confirm),
            "reading": "当前 event_sample_purged 里的最后 confirm 时点。",
        },
        {
            "check": "last_known_pair_halfsize_pure_down_coverage",
            "value": pure_down,
            "reading": "沿用最近一次 heavy recheck 的 hard blocker；在它变成非零前，default pair 仍不能写成 near-down protective policy。",
        },
        {
            "check": "last_known_pair_halfsize_predown_bridge_12h",
            "value": predown_bridge,
            "reading": "沿用最近一次 heavy recheck 的 anticipatory bridge blocker；当前仍是默认候选最关键的 admission 缺口之一。",
        },
        {
            "check": "revisit_trigger",
            "value": trigger,
            "reading": "只有满足这个条件，下一次 breakout rerun 才更像新的有效推进，而不是同样本重复劳动。",
        },
        {
            "check": "operator_action",
            "value": action,
            "reading": "给下一轮自动循环的默认动作。",
        },
        {
            "check": "revisit_guard_verdict",
            "value": verdict,
            "reading": "把 breakout 当前状态压成轻量 rerun gate：先看 cache 是否真的往后，再决定要不要重跑整条 pipeline。",
        },
    ]

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["check", "value", "reading"])
        writer.writeheader()
        writer.writerows(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
