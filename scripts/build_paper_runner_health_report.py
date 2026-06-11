#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SITE_DIR = ROOT / "reports" / "site" / "factors" / "paper_runner_health"
OUT_PATH = SITE_DIR / "report.html"
ART_DIR = ROOT / "reports" / "artifacts"

BJ = timezone(timedelta(hours=8), name="Asia/Shanghai")
RATE_LIMIT_RE = re.compile(r"429|too many requests|rate limit|ratelimit|retry-after", re.I)
ERROR_RE = re.compile(r"http [45][0-9][0-9]|traceback|exception|failed|error", re.I)


@dataclass
class RunnerSpec:
    key: str
    label: str
    service: str
    timer: str
    cadence_minutes: int
    status_csv: Path | None = None
    state_json: Path | None = None
    run_summary_json: Path | None = None
    extra_warning_json: Path | None = None
    notes: str = ""
    expected_service_state: str = "inactive"


RUNNERS = [
    RunnerSpec(
        key="rank183",
        label="Rank 183 / cbETH-ETH fair-basis MR",
        service="momentum-rank183-paper-refresh.service",
        timer="momentum-rank183-paper-refresh.timer",
        cadence_minutes=15,
        status_csv=ART_DIR / "paper_rank183_cbeth_eth_basis" / "rank183_status.csv",
        state_json=ART_DIR / "paper_rank183_cbeth_eth_basis" / "rank183_state.json",
        run_summary_json=ART_DIR / "paper_rank183_cbeth_eth_basis" / "rank183_last_run_summary.json",
        notes="Coinbase candles + book；15m refresh",
    ),
    RunnerSpec(
        key="rank186",
        label="Rank 186 / CME expiry postfix short BTC",
        service="momentum-rank186-paper-refresh.service",
        timer="momentum-rank186-paper-refresh.timer",
        cadence_minutes=1,
        status_csv=ART_DIR / "paper_rank186_cme_expiry" / "rank186_status.csv",
        state_json=ART_DIR / "paper_rank186_cme_expiry" / "rank186_state.json",
        run_summary_json=ART_DIR / "paper_rank186_cme_expiry" / "rank186_last_run_summary.json",
        notes="Binance futures 1m event clock；1m refresh",
    ),
    RunnerSpec(
        key="rank187",
        label="Rank 187 / BTC 15m path-shape swing",
        service="momentum-rank187-paper-refresh.service",
        timer="momentum-rank187-paper-refresh.timer",
        cadence_minutes=15,
        status_csv=ART_DIR / "paper_rank187_path_shape" / "rank187_status.csv",
        state_json=ART_DIR / "paper_rank187_path_shape" / "rank187_state.json",
        run_summary_json=ART_DIR / "paper_rank187_path_shape" / "rank187_last_run_summary.json",
        notes="Binance futures 15m path-state refresh",
    ),
    RunnerSpec(
        key="rank32b",
        label="Rank 32b / live canary phase6",
        service="momentum-rank32b-canary-phase6.service",
        timer="momentum-rank32b-canary-phase6.timer",
        cadence_minutes=1,
        status_csv=ART_DIR / "rank32b_canary" / "phase6_status.json",
        run_summary_json=ART_DIR / "rank32b_canary" / "phase6_last_run_summary.json",
        state_json=ART_DIR / "rank32b_canary" / "phase6_state.json",
        extra_warning_json=ART_DIR / "rank32b_canary" / "phase6_warnings.json",
        notes="实盘 canary；高频、共享账户、最容易先暴露 API / venue 异常",
        expected_service_state="activating",
    ),
]


def run(cmd: str, timeout: int = 20) -> str:
    try:
        out = subprocess.check_output(["/bin/bash", "-lc", cmd], cwd=str(ROOT), stderr=subprocess.STDOUT, text=True, timeout=timeout)
        return out.strip()
    except subprocess.CalledProcessError as exc:
        return (exc.output or "").strip() or f"command failed: {cmd}"
    except Exception as exc:  # noqa: BLE001
        return f"command failed: {cmd} :: {exc}"


def read_json(path: Path):
    if not path or not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv_first(path: Path) -> dict[str, str] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    return rows[0] if rows else None


def fmt_ts(ts: datetime | None) -> str:
    if ts is None:
        return "-"
    return f"{ts.astimezone(BJ).strftime('%Y-%m-%d %H:%M:%S')} 北京 / {ts.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC"


def parse_iso(s: str | None) -> datetime | None:
    if not s:
        return None
    text = str(s).strip()
    if not text or text == "-":
        return None
    text = text.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def parse_systemctl_time(s: str | None) -> datetime | None:
    if not s:
        return None
    text = str(s).strip()
    if not text:
        return None
    for fmt in ("%a %Y-%m-%d %H:%M:%S UTC", "%a %Y-%m-%d %H:%M:%S %Z"):
        try:
            dt = datetime.strptime(text, fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def parse_show_block(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in text.splitlines():
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def load_service_props(unit: str) -> dict[str, str]:
    text = run(
        f"systemctl show {unit} -p Id -p ActiveState -p SubState -p Result -p ExecMainStatus -p ExecMainStartTimestamp -p ExecMainExitTimestamp -p NRestarts",
        timeout=20,
    )
    return parse_show_block(text)


def load_timer_props(unit: str) -> dict[str, str]:
    text = run(
        f"systemctl show {unit} -p Id -p ActiveState -p SubState -p Result -p LastTriggerUSec -p NextElapseUSecRealtime",
        timeout=20,
    )
    return parse_show_block(text)


def recent_journal(unit: str, since_hours: int = 6) -> list[str]:
    since = (datetime.now(timezone.utc) - timedelta(hours=since_hours)).strftime("%Y-%m-%d %H:%M:%S UTC")
    text = run(f"journalctl -u {unit} --since '{since}' --no-pager", timeout=30)
    lines = [line for line in text.splitlines() if line.strip()]
    return lines[-200:]


def detect_health(service: dict[str, str], timer: dict[str, str], status_updated: datetime | None, cadence_minutes: int, rate_limit_count: int, error_count: int, expected_service_state: str) -> tuple[str, str]:
    now = datetime.now(timezone.utc)
    stale_limit = timedelta(minutes=max(3, cadence_minutes * 3))
    if rate_limit_count > 0:
        return "RED", "journal 命中过 rate-limit / 429"
    if service.get("Result") not in {"success", ""}:
        return "RED", f"service Result={service.get('Result') or '-'}"
    if service.get("ExecMainStatus") not in {"0", ""}:
        return "RED", f"ExecMainStatus={service.get('ExecMainStatus') or '-'}"
    if timer.get("ActiveState") != "active":
        return "RED", f"timer ActiveState={timer.get('ActiveState') or '-'}"
    if expected_service_state == "inactive":
        if service.get("ActiveState") not in {"inactive", "activating"}:
            return "RED", f"service ActiveState={service.get('ActiveState') or '-'}"
    if status_updated is not None and now - status_updated > stale_limit:
        return "YELLOW", f"artifact 超过 {stale_limit} 未更新"
    if error_count > 0:
        return "YELLOW", f"近 6h journal 有 {error_count} 条 error-like 关键词，需盯"
    return "GREEN", "调度正常，artifact 新鲜，近 6h 未见 rate-limit"


def build_runner_snapshot(spec: RunnerSpec) -> dict:
    if spec.status_csv and spec.status_csv.suffix == ".csv":
        status_payload = read_csv_first(spec.status_csv) or {}
    else:
        status_payload = read_json(spec.status_csv) or {}
    state_payload = read_json(spec.state_json) or {}
    summary_payload = read_json(spec.run_summary_json) or {}
    warnings_payload = read_json(spec.extra_warning_json) if spec.extra_warning_json else None

    service = load_service_props(spec.service)
    timer = load_timer_props(spec.timer)
    journal_lines = recent_journal(spec.service, since_hours=6)
    rate_limit_lines = [line for line in journal_lines if RATE_LIMIT_RE.search(line)]
    error_lines = [line for line in journal_lines if ERROR_RE.search(line)]

    updated_at = None
    for key in ("updated_at_utc", "last_run_utc", "last_run_at_utc", "run_finished_at", "generated_at_utc"):
        updated_at = parse_iso(status_payload.get(key) if isinstance(status_payload, dict) else None)
        if updated_at is not None:
            break
        updated_at = parse_iso(summary_payload.get(key) if isinstance(summary_payload, dict) else None)
        if updated_at is not None:
            break
        updated_at = parse_iso(state_payload.get(key) if isinstance(state_payload, dict) else None)
        if updated_at is not None:
            break

    exec_start = parse_systemctl_time(service.get("ExecMainStartTimestamp"))
    exec_exit = parse_systemctl_time(service.get("ExecMainExitTimestamp"))
    last_trigger = parse_systemctl_time(timer.get("LastTriggerUSec"))
    next_elapse = parse_systemctl_time(timer.get("NextElapseUSecRealtime"))
    duration_sec = None
    if exec_start and exec_exit:
        duration_sec = max(0.0, (exec_exit - exec_start).total_seconds())

    health, diagnosis = detect_health(
        service,
        timer,
        updated_at,
        spec.cadence_minutes,
        len(rate_limit_lines),
        len(error_lines),
        spec.expected_service_state,
    )

    warning_count = 0
    if isinstance(warnings_payload, list):
        warning_count = len(warnings_payload)
    elif isinstance(warnings_payload, dict):
        warning_count = len(warnings_payload)

    return {
        "spec": spec,
        "status": status_payload,
        "state": state_payload,
        "summary": summary_payload,
        "warnings": warnings_payload,
        "warning_count": warning_count,
        "service": service,
        "timer": timer,
        "updated_at": updated_at,
        "exec_start": exec_start,
        "exec_exit": exec_exit,
        "last_trigger": last_trigger,
        "next_elapse": next_elapse,
        "duration_sec": duration_sec,
        "health": health,
        "diagnosis": diagnosis,
        "rate_limit_lines": rate_limit_lines,
        "error_lines": error_lines,
        "journal_tail": journal_lines[-8:],
    }


def render_table(rows: list[dict[str, str]], headers: list[str]) -> str:
    if not rows:
        return "<p class='muted'>暂无数据。</p>"
    head = "".join(f"<th>{escape(h)}</th>" for h in headers)
    body = []
    for row in rows:
        cells = "".join(f"<td>{escape(str(row.get(h, '-')))}</td>" for h in headers)
        body.append(f"<tr>{cells}</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def render() -> str:
    generated_at = datetime.now(timezone.utc)
    snaps = [build_runner_snapshot(spec) for spec in RUNNERS]
    green = sum(1 for s in snaps if s["health"] == "GREEN")
    yellow = sum(1 for s in snaps if s["health"] == "YELLOW")
    red = sum(1 for s in snaps if s["health"] == "RED")
    total_rate_limit_hits = sum(len(s["rate_limit_lines"]) for s in snaps)
    total_error_hits = sum(len(s["error_lines"]) for s in snaps)

    cards = []
    rows = []
    detail_blocks = []
    for s in snaps:
        spec: RunnerSpec = s["spec"]
        health_class = s["health"].lower()
        cards.append(
            f"""
            <div class='card {health_class}'>
              <div class='k'>{escape(spec.label)}</div>
              <div class='v'>{escape(s['health'])}</div>
              <div class='s'>{escape(s['diagnosis'])}</div>
              <div class='tiny'>last artifact: {escape(fmt_ts(s['updated_at']))}</div>
              <div class='tiny'>last trigger: {escape(fmt_ts(s['last_trigger']))}</div>
              <div class='tiny'>next run: {escape(fmt_ts(s['next_elapse']))}</div>
            </div>
            """
        )
        rows.append(
            {
                "Runner": spec.label,
                "Health": s["health"],
                "Timer": s["timer"].get("ActiveState") or "-",
                "ServiceResult": s["service"].get("Result") or "-",
                "ExitStatus": s["service"].get("ExecMainStatus") or "-",
                "LastArtifact": fmt_ts(s["updated_at"]),
                "LastTrigger": fmt_ts(s["last_trigger"]),
                "NextRun": fmt_ts(s["next_elapse"]),
                "DurationSec": "-" if s["duration_sec"] is None else f"{s['duration_sec']:.1f}",
                "RateLimitHits6h": str(len(s["rate_limit_lines"])),
                "ErrorLikeHits6h": str(len(s["error_lines"])),
            }
        )
        latest_open = s["status"].get("open_position_side") or s["status"].get("current_position_side") or "-"
        detail_blocks.append(
            f"""
            <div class='detail card'>
              <h2>{escape(spec.label)}</h2>
              <p><b>结论：</b>{escape(s['diagnosis'])}</p>
              <ul>
                <li>cadence: <code>{spec.cadence_minutes}m</code></li>
                <li>timer active: <code>{escape(s['timer'].get('ActiveState') or '-')}</code></li>
                <li>service result / exit: <code>{escape(s['service'].get('Result') or '-')}</code> / <code>{escape(s['service'].get('ExecMainStatus') or '-')}</code></li>
                <li>last artifact: <code>{escape(fmt_ts(s['updated_at']))}</code></li>
                <li>last trigger: <code>{escape(fmt_ts(s['last_trigger']))}</code></li>
                <li>next run: <code>{escape(fmt_ts(s['next_elapse']))}</code></li>
                <li>last duration: <code>{'-' if s['duration_sec'] is None else f"{s['duration_sec']:.1f}s"}</code></li>
                <li>rate-limit hits (6h): <code>{len(s['rate_limit_lines'])}</code></li>
                <li>error-like hits (6h): <code>{len(s['error_lines'])}</code></li>
                <li>current/open side: <code>{escape(str(latest_open))}</code></li>
                <li>notes: {escape(spec.notes)}</li>
              </ul>
              <p class='muted'>artifacts: <code>{escape(str(spec.status_csv.relative_to(ROOT)) if spec.status_csv else '-')}</code></p>
              <h3>journal tail</h3>
              <pre>{escape(chr(10).join(s['journal_tail']) if s['journal_tail'] else 'no recent journal lines')}</pre>
            </div>
            """
        )

    summary_note = "近 6 小时未发现 rate-limit 命中。" if total_rate_limit_hits == 0 else f"近 6 小时发现 {total_rate_limit_hits} 条 rate-limit 命中，需立即降频或缓存。"

    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Paper Runner Health Dashboard</title>
  <style>
    body {{ font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; background: #0b1220; color: #e5e7eb; }}
    .wrap {{ max-width: 1240px; margin: 0 auto; padding: 28px 20px 56px; }}
    .grid {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(240px,1fr)); gap:14px; margin:16px 0 24px; }}
    .card {{ background:#111827; border:1px solid #1f2937; border-radius:14px; padding:16px; }}
    .green {{ border-color:#166534; box-shadow: inset 0 0 0 1px rgba(34,197,94,.18); }}
    .yellow {{ border-color:#a16207; box-shadow: inset 0 0 0 1px rgba(234,179,8,.18); }}
    .red {{ border-color:#991b1b; box-shadow: inset 0 0 0 1px rgba(239,68,68,.22); }}
    .k {{ font-size:12px; color:#94a3b8; text-transform:uppercase; letter-spacing:.05em; }}
    .v {{ font-size:24px; font-weight:700; margin-top:8px; }}
    .s {{ margin-top:8px; color:#cbd5e1; line-height:1.5; }}
    .tiny {{ margin-top:6px; color:#94a3b8; font-size:12px; }}
    table {{ width:100%; border-collapse:collapse; background:#111827; border:1px solid #1f2937; border-radius:14px; overflow:hidden; margin:12px 0 28px; }}
    th, td {{ text-align:left; padding:10px 12px; border-bottom:1px solid #1f2937; font-size:13px; vertical-align:top; }}
    th {{ background:#0f172a; color:#cbd5e1; }}
    tr:last-child td {{ border-bottom:none; }}
    code, pre {{ background:#0f172a; color:#cbd5e1; border-radius:8px; }}
    code {{ padding:2px 6px; }}
    pre {{ padding:14px; white-space:pre-wrap; word-break:break-word; border:1px solid #1f2937; overflow-x:auto; }}
    .muted {{ color:#94a3b8; }}
    a {{ color:#60a5fa; }}
  </style>
</head>
<body>
  <div class='wrap'>
    <p class='muted'>生成时间：{escape(fmt_ts(generated_at))}</p>
    <h1>Paper Runner Health Dashboard</h1>
    <p>本页专门看 <b>Rank 183 / 186 / 187</b> 以及对照项 <b>Rank 32b live canary</b> 的健康度：调度有没有按时触发、artifact 有没有持续更新、近 6 小时 journal 里有没有 429 / rate-limit / error-like 迹象。</p>
    <div class='grid'>
      <div class='card'><div class='k'>GREEN / YELLOW / RED</div><div class='v'>{green} / {yellow} / {red}</div><div class='s'>这是当前四个 runner 的即时健康分布。</div></div>
      <div class='card'><div class='k'>Rate-limit hits (6h)</div><div class='v'>{total_rate_limit_hits}</div><div class='s'>{escape(summary_note)}</div></div>
      <div class='card'><div class='k'>Error-like hits (6h)</div><div class='v'>{total_error_hits}</div><div class='s'>这里只是关键词预警；如果不是 429，更多是需要人工复核的 yellow 信号。</div></div>
      <div class='card'><div class='k'>Method</div><div class='v'>systemd + artifacts + journal</div><div class='s'>不是只看 timer 在不在，而是同时看 service result、artifact freshness、journal tail。</div></div>
    </div>
    <div class='grid'>
      {''.join(cards)}
    </div>
    <h2>Compact Health Table</h2>
    {render_table(rows, ['Runner','Health','Timer','ServiceResult','ExitStatus','LastArtifact','LastTrigger','NextRun','DurationSec','RateLimitHits6h','ErrorLikeHits6h'])}
    <h2>Runner Details</h2>
    {''.join(detail_blocks)}
    <p class='muted'><a href='/momentum/'>返回首页</a> ｜ <a href='/momentum/factors/rank32b_canary/report.html'>查看 32b canary 看板</a></p>
  </div>
</body>
</html>
"""


def main() -> int:
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(render(), encoding="utf-8")
    print(json.dumps({"generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "out": str(OUT_PATH)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
