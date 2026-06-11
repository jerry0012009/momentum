#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

# 统一按完整 round-trip 6 bps 估算手续费，对齐 desk 当前主口径
ROUND_TRIP_FEE_BPS = 6.0
WINDOWS = [
    ("6h", timedelta(hours=6)),
    ("12h", timedelta(hours=12)),
    ("24h", timedelta(hours=24)),
    ("3d", timedelta(days=3)),
    ("7d", timedelta(days=7)),
    ("14d", timedelta(days=14)),
]

LANES: list[dict[str, Any]] = [
    {
        "key": "core3",
        "label": "32b core3",
        "state": ROOT / "reports" / "artifacts" / "rank32b_canary" / "phase6_state.json",
        "summary": ROOT / "reports" / "artifacts" / "rank32b_canary" / "phase6_last_run_summary.json",
        "status": ROOT / "reports" / "artifacts" / "rank32b_canary" / "phase6_status.json",
        "warnings": ROOT / "reports" / "artifacts" / "rank32b_canary" / "phase6_warnings.json",
        "signals": ROOT / "reports" / "artifacts" / "rank32b_canary" / "phase6_recent_signals.json",
        "orders": ROOT / "reports" / "artifacts" / "rank32b_canary" / "phase6_recent_orders.json",
        "rejections": ROOT / "reports" / "artifacts" / "rank32b_canary" / "phase6_recent_rejections.json",
    },
    {
        "key": "global32b",
        "label": "32b global",
        "state": ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_state.json",
        "summary": ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_last_run_summary.json",
        "status": ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_status.json",
        "warnings": ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_warnings.json",
        "signals": ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_recent_signals.json",
        "orders": ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_recent_orders.json",
        "rejections": ROOT / "reports" / "artifacts" / "rank32b_global_live" / "live_recent_rejections.json",
    },
    {
        "key": "rank29_gate",
        "label": "Rank29 gate",
        "state": ROOT / "reports" / "artifacts" / "rank29_gate_live" / "rank29_gate_live_state.json",
        "summary": ROOT / "reports" / "artifacts" / "rank29_gate_live" / "rank29_gate_live_last_run_summary.json",
        "status": ROOT / "reports" / "artifacts" / "rank29_gate_live" / "rank29_gate_live_status.json",
        "warnings": ROOT / "reports" / "artifacts" / "rank29_gate_live" / "rank29_gate_live_warnings.json",
        "signals": ROOT / "reports" / "artifacts" / "rank29_gate_live" / "rank29_gate_live_recent_signals.json",
        "orders": ROOT / "reports" / "artifacts" / "rank29_gate_live" / "rank29_gate_live_recent_orders.json",
        "rejections": ROOT / "reports" / "artifacts" / "rank29_gate_live" / "rank29_gate_live_recent_rejections.json",
    },
]


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default



def parse_utc(ts: Any) -> datetime | None:
    if ts in (None, "", "-"):
        return None
    if isinstance(ts, (int, float)):
        try:
            return datetime.fromtimestamp(float(ts), tz=timezone.utc)
        except Exception:
            return None
    raw = str(ts).strip()
    if not raw:
        return None
    try:
        return datetime.strptime(raw, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except Exception:
        pass
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None



def sf(v: Any, d: float = 0.0) -> float:
    try:
        return float(v)
    except Exception:
        return float(d)



def fmt(v: float | int | None, digits: int = 4) -> str:
    if v is None:
        return "-"
    return f"{float(v):,.{digits}f}"



def get_first(mapping: dict[str, Any], keys: list[str]) -> Any:
    for key in keys:
        if key in mapping and mapping.get(key) not in (None, ""):
            return mapping.get(key)
    return None



def find_latest_ts(rows: Any, keys: list[str]) -> datetime | None:
    if not isinstance(rows, list):
        return None
    latest: datetime | None = None
    for row in rows:
        if not isinstance(row, dict):
            continue
        for key in keys:
            dt = parse_utc(row.get(key))
            if dt is not None and (latest is None or dt > latest):
                latest = dt
    return latest



def estimate_trade_fee_and_net(row: dict[str, Any]) -> tuple[float, float, float]:
    gross = sf(row.get("gross_pnl"))
    fee = row.get("fee")
    if fee is None:
        qty = sf(row.get("qty"))
        entry_price = sf(row.get("entry_price"))
        exit_price = sf(row.get("exit_price"))
        entry_notional = qty * entry_price
        exit_notional = qty * exit_price
        avg_notional = (entry_notional + exit_notional) / 2.0 if (entry_notional + exit_notional) > 0 else 0.0
        fee = avg_notional * (ROUND_TRIP_FEE_BPS / 10000.0)
    fee = sf(fee)

    net = row.get("net_pnl")
    if net is None:
        net = gross - fee
    net = sf(net)

    net_bps = row.get("net_return_bps")
    if net_bps is None:
        qty = sf(row.get("qty"))
        entry_price = sf(row.get("entry_price"))
        exit_price = sf(row.get("exit_price"))
        entry_notional = qty * entry_price
        exit_notional = qty * exit_price
        avg_notional = (entry_notional + exit_notional) / 2.0 if (entry_notional + exit_notional) > 0 else 0.0
        net_bps = (net / avg_notional * 10000.0) if avg_notional > 0 else 0.0
    net_bps = sf(net_bps)

    return fee, net, net_bps



def verdict_from_net(count: int, net_sum: float) -> str:
    if count <= 0:
        return "无交易"
    if net_sum > 0:
        return "赚钱"
    if net_sum < 0:
        return "亏钱"
    return "持平"



def build_window_lines(closed_trades: list[dict[str, Any]], now_dt: datetime) -> list[str]:
    lines: list[str] = []
    for label, delta in WINDOWS:
        cutoff = now_dt - delta
        bucket = []
        for row in closed_trades:
            exit_dt = parse_utc(row.get("exit_time"))
            if exit_dt is not None and exit_dt >= cutoff:
                bucket.append(row)

        count = len(bucket)
        net_sum = 0.0
        wins = 0
        net_bps_list: list[float] = []
        for row in bucket:
            _, net, net_bps = estimate_trade_fee_and_net(row)
            net_sum += net
            net_bps_list.append(net_bps)
            if net > 0:
                wins += 1

        win_rate = (wins / count * 100.0) if count else 0.0
        avg_net = (net_sum / count) if count else 0.0
        avg_net_bps = (sum(net_bps_list) / len(net_bps_list)) if net_bps_list else 0.0
        verdict = verdict_from_net(count, net_sum)
        lines.append(
            f"- {label}: 交易 {count} 笔 | 已实现净收益 {fmt(net_sum)} USDT | 状态 {verdict} | 胜率 {fmt(win_rate, 2)}% | 单笔平均净收益 {fmt(avg_net)} USDT | 单笔平均净收益 {fmt(avg_net_bps, 2)} bps"
        )
    return lines



def summarize_live_positions(rows: Any) -> list[str]:
    if not isinstance(rows, list) or not rows:
        return ["- 当前无 live positions"]
    lines: list[str] = []
    for row in rows[:8]:
        if not isinstance(row, dict):
            continue
        lines.append(
            "- "
            + f"{row.get('symbol', '-')} {row.get('side', row.get('positionSide', '-'))} | "
            + f"entry={row.get('entry_time', '-')} @{row.get('entry_price', row.get('entryPrice', '-'))} | "
            + f"qty={row.get('qty', row.get('positionAmt', '-'))}"
        )
    return lines or ["- 当前无 live positions"]



def build_recent_trade_lines(closed_trades: list[dict[str, Any]], limit: int = 5) -> list[str]:
    rows = sorted(
        [row for row in closed_trades if isinstance(row, dict)],
        key=lambda row: parse_utc(row.get("exit_time")) or datetime(1970, 1, 1, tzinfo=timezone.utc),
        reverse=True,
    )[:limit]
    if not rows:
        return ["- 最近无已完成交易"]
    lines: list[str] = []
    for row in rows:
        _, net, net_bps = estimate_trade_fee_and_net(row)
        lines.append(
            "- "
            + f"{row.get('symbol', '-')} {row.get('side', '-')} | "
            + f"entry={row.get('entry_time', '-')} @{row.get('entry_price', '-')} | "
            + f"exit={row.get('exit_time', '-')} @{row.get('exit_price', '-')} | "
            + f"reason={row.get('exit_reason', '-')} | net={fmt(net)} USDT | net_bps={fmt(net_bps, 2)}"
        )
    return lines



def lane_snapshot(spec: dict[str, Any], now_dt: datetime) -> list[str]:
    state = load_json(spec["state"], {})
    summary = load_json(spec["summary"], {})
    status = load_json(spec["status"], {})
    warnings = load_json(spec["warnings"], [])
    signals = load_json(spec["signals"], [])
    orders = load_json(spec["orders"], [])
    rejections = load_json(spec["rejections"], [])

    closed_trades = state.get("closed_trades", []) if isinstance(state, dict) else []
    live_positions = state.get("live_positions", []) if isinstance(state, dict) else []
    recent_warnings = state.get("recent_warnings", []) if isinstance(state, dict) else []

    last_run = None
    for source in [summary, status, state]:
        if isinstance(source, dict):
            last_run = get_first(
                source,
                [
                    "run_finished_at",
                    "generated_at_utc",
                    "last_run_utc",
                    "updated_at_utc",
                ],
            )
            if last_run is not None:
                break

    latest_signal_ts = find_latest_ts(signals, ["timestamp", "signal_confirmed_at", "first_seen_at", "signal_timestamp"])
    latest_order_ts = find_latest_ts(orders, ["timestamp", "submit_at", "last_update_at", "created_at", "updated_at"])
    latest_reject_ts = find_latest_ts(rejections, ["timestamp", "rejected_at", "created_at", "updated_at"])
    latest_close_ts = find_latest_ts(closed_trades, ["exit_time", "timestamp"])

    warnings_count = 0
    if isinstance(warnings, list):
        warnings_count += len(warnings)
    if isinstance(recent_warnings, list):
        warnings_count += len(recent_warnings)

    lines: list[str] = []
    lines.append(f"== {spec['label']} ==")
    lines.append(f"- 最近运行完成时间：{last_run or '-'}")
    if isinstance(status, dict):
        trade_enabled = get_first(status, ["trade_enabled", "allow_live_orders"])
        if trade_enabled is not None:
            lines.append(f"- 交易开关：{trade_enabled}")
        system_health = get_first(status, ["system_health", "health_status"])
        if system_health is not None:
            lines.append(f"- 系统健康：{system_health}")
        latest_bar = get_first(status, ["latest_evaluated_bar_time", "latest_sample_end_utc", "latest_bar_time"])
        if latest_bar is not None:
            lines.append(f"- 最新评估 bar：{latest_bar}")
    lines.append(f"- 当前 live positions：{len(live_positions) if isinstance(live_positions, list) else 0}")
    lines.append(f"- 最新信号时间：{latest_signal_ts.strftime('%Y-%m-%d %H:%M:%S UTC') if latest_signal_ts else '-'}")
    lines.append(f"- 最新订单时间：{latest_order_ts.strftime('%Y-%m-%d %H:%M:%S UTC') if latest_order_ts else '-'}")
    lines.append(f"- 最新拒单/跳过时间：{latest_reject_ts.strftime('%Y-%m-%d %H:%M:%S UTC') if latest_reject_ts else '-'}")
    lines.append(f"- 最新平仓时间：{latest_close_ts.strftime('%Y-%m-%d %H:%M:%S UTC') if latest_close_ts else '-'}")
    lines.append(f"- 已完成交易总数：{len(closed_trades) if isinstance(closed_trades, list) else 0}")
    lines.append(f"- warnings 记录数：{warnings_count}")
    lines.append("- 固定窗口统计（只看已完成 closed trades）：")
    lines.extend(build_window_lines(closed_trades if isinstance(closed_trades, list) else [], now_dt))
    lines.append("- 当前持仓摘要：")
    lines.extend(summarize_live_positions(live_positions))
    lines.append("- 最近已完成交易（最近 5 笔）：")
    lines.extend(build_recent_trade_lines(closed_trades if isinstance(closed_trades, list) else [], limit=5))
    lines.append("")
    return lines



def main() -> None:
    now_dt = datetime.now(timezone.utc)
    lines: list[str] = []
    lines.append(f"三线实盘状态快照（生成时间：{now_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}）")
    lines.append("")
    lines.append(f"统计窗口：{', '.join(label for label, _ in WINDOWS)}")
    lines.append(f"手续费口径：round-trip {ROUND_TRIP_FEE_BPS:.2f} bps；优先使用 trade row 自带 fee/net_pnl，缺失时再按该口径估算。")
    lines.append("")
    for spec in LANES:
        lines.extend(lane_snapshot(spec, now_dt))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
