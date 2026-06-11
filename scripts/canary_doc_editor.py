#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import secrets
import subprocess
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOC = ROOT / "docs" / "CANARY_32B_TODO.md"
VAR_DIR = ROOT / "var"
TOKEN_FILE = VAR_DIR / "canary_editor_token.txt"
CONTROL_STATE_FILE = VAR_DIR / "canary_control_state.json"
CONTROL_LOG_DIR = VAR_DIR / "control_logs"
CONFIG_PATH = ROOT / "config" / "execution" / "rank32b_canary.yaml"
DASHBOARD_PATH = ROOT / "reports" / "site" / "factors" / "rank32b_canary" / "report.html"
SNAPSHOT_SCRIPT = ROOT / "scripts" / "build_rank32b_live_email_snapshot.py"
DASHBOARD_BUILD_CMD = f"/usr/bin/python3 {ROOT / 'scripts' / 'build_rank32b_canary_dashboard.py'}"
HOST = "0.0.0.0"
PORT = 24444

ACTION_ARTIFACTS = {
    "phase5": ROOT / "reports" / "artifacts" / "rank32b_canary" / "phase5_last_run_summary.json",
    "phase6_once": ROOT / "reports" / "artifacts" / "rank32b_canary" / "phase6_last_run_summary.json",
}

TEMPLATE = """# 32B Canary TODO\n\n> 把你的长文档直接粘贴到这里，网页保存后会写回服务器。\n\n## 目标\n- 为 32b 策略规划实盘 canary\n- 明确不能阻塞 / 影响 bot2 / bot3 / bot6 / bot7 现有定时任务\n\n## 约束\n- 独立目录\n- 独立 cron / systemd / OpenClaw 任务链路\n- 先 canary，再放量\n\n## TODO\n- [ ] 在这里开始写\n"""

ACTIVE_PROCS: dict[str, subprocess.Popen] = {}
ACTIVE_LOCK = threading.Lock()


ACTIONS = {
    "phase5": {
        "title": "1) 运行 Phase 5 单次 live 下单验证",
        "desc": "发一次最小 live order gate，下单后查询并撤单，再自动重建 dashboard。",
        "button": "运行 Phase 5",
        "command": (
            f"cd {ROOT} && "
            f"/usr/bin/python3 scripts/run_rank32b_canary_phase5.py --config config/execution/rank32b_canary.yaml && "
            f"/usr/bin/python3 scripts/build_rank32b_canary_dashboard.py"
        ),
        "danger": True,
    },
    "phase6_once": {
        "title": "2) 单次运行 Phase 6 canary 策略",
        "desc": "跑一轮自动策略：signal → risk → entry → exit plan，并自动重建 dashboard。",
        "button": "运行 Phase 6 一次",
        "command": (
            f"cd {ROOT} && "
            f"/usr/bin/python3 scripts/run_rank32b_canary_phase6.py --config config/execution/rank32b_canary.yaml && "
            f"/usr/bin/python3 scripts/build_rank32b_canary_dashboard.py"
        ),
        "danger": True,
    },
    "phase6_timer": {
        "title": "3) 安装并启动 Phase 6 自动定时器",
        "desc": "把 phase6 service/timer 装进 systemd，启用后每 5 分钟自动跑一轮。",
        "button": "启动自动定时运行",
        "command": (
            f"cd {ROOT} && "
            f"install -m 0644 ops/systemd/momentum-rank32b-canary-phase6.service /etc/systemd/system/momentum-rank32b-canary-phase6.service && "
            f"install -m 0644 ops/systemd/momentum-rank32b-canary-phase6.timer /etc/systemd/system/momentum-rank32b-canary-phase6.timer && "
            f"systemctl daemon-reload && "
            f"systemctl enable --now momentum-rank32b-canary-phase6.timer && "
            f"systemctl status momentum-rank32b-canary-phase6.timer --no-pager -l"
        ),
        "danger": True,
    },
}


def ensure_token(path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        token = path.read_text(encoding="utf-8").strip()
        if token:
            return token
    token = secrets.token_urlsafe(24)
    path.write_text(token + "\n", encoding="utf-8")
    return token


def ensure_doc(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(TEMPLATE, encoding="utf-8")


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_control_state() -> dict:
    if not CONTROL_STATE_FILE.exists():
        return {"actions": {}}
    try:
        return json.loads(CONTROL_STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"actions": {}}


def save_control_state(state: dict) -> None:
    CONTROL_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONTROL_STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def is_proc_running(action_id: str) -> bool:
    with ACTIVE_LOCK:
        proc = ACTIVE_PROCS.get(action_id)
        if proc is None:
            return False
        code = proc.poll()
        if code is None:
            return True
        ACTIVE_PROCS.pop(action_id, None)
        return False


def tail_text(path: Path, max_lines: int = 40) -> str:
    if not path.exists():
        return "暂无日志。"
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(lines[-max_lines:]) or "暂无日志。"


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def _to_float(value: str | None, default: float) -> float:
    try:
        if value is None:
            return float(default)
        return float(str(value).strip())
    except Exception:
        return float(default)


def _to_int(value: str | None, default: int) -> int:
    try:
        if value is None:
            return int(default)
        return int(float(str(value).strip()))
    except Exception:
        return int(default)


def _to_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return bool(default)
    return str(value).strip().lower() in {"1", "true", "on", "yes"}


def save_canary_config_from_form(form: dict[str, list[str]]) -> str:
    cfg = load_yaml(CONFIG_PATH)
    if not cfg:
        raise RuntimeError(f"无法读取配置：{CONFIG_PATH}")

    phase6 = cfg.setdefault("phase6", {})
    sizing = phase6.setdefault("sizing", {})
    exit_cfg = phase6.setdefault("exit", {})
    risk_cfg = cfg.setdefault("risk", {})

    symbols = [str(s).upper() for s in (cfg.get("universe", {}).get("symbols", []) or [])]

    desired_notional_usdt = max(1.0, _to_float((form.get("desired_notional_usdt") or [None])[0], float(sizing.get("desired_notional_usdt", 50.0))))
    sizing["desired_notional_usdt"] = float(desired_notional_usdt)

    by_symbol: dict[str, float] = {}
    existing_by_symbol = sizing.get("desired_notional_usdt_by_symbol", {})
    if not isinstance(existing_by_symbol, dict):
        existing_by_symbol = {}
    for symbol in symbols:
        key = f"notional_{symbol}"
        current = float(existing_by_symbol.get(symbol, desired_notional_usdt))
        value = max(1.0, _to_float((form.get(key) or [None])[0], current))
        by_symbol[symbol] = float(value)
    if by_symbol:
        sizing["desired_notional_usdt_by_symbol"] = by_symbol

    phase6["default_leverage"] = max(1, _to_int((form.get("default_leverage") or [None])[0], int(phase6.get("default_leverage", 1))))
    phase6["max_new_signals_per_run"] = max(1, _to_int((form.get("max_new_signals_per_run") or [None])[0], int(phase6.get("max_new_signals_per_run", 3))))

    exit_cfg["tp_atr_mult"] = max(0.1, _to_float((form.get("tp_atr_mult") or [None])[0], float(exit_cfg.get("tp_atr_mult", 1.25))))
    exit_cfg["sl_atr_mult"] = max(0.1, _to_float((form.get("sl_atr_mult") or [None])[0], float(exit_cfg.get("sl_atr_mult", 1.0))))
    exit_cfg["timeout_minutes"] = max(5, _to_int((form.get("timeout_minutes") or [None])[0], int(exit_cfg.get("timeout_minutes", 120))))

    risk_cfg["trade_enabled"] = "trade_enabled" in form
    risk_cfg["kill_switch"] = "kill_switch" in form
    risk_cfg["max_concurrent_positions"] = max(1, _to_int((form.get("max_concurrent_positions") or [None])[0], int(risk_cfg.get("max_concurrent_positions", 1))))

    rendered = yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False)
    atomic_write_text(CONFIG_PATH, rendered)
    return f"配置已保存：global={desired_notional_usdt:.2f} USDT，symbols={','.join(symbols) or '-'}"


def update_action_state(action_id: str, **patch) -> dict:
    state = load_control_state()
    actions = state.setdefault("actions", {})
    row = actions.setdefault(action_id, {})
    row.update(patch)
    save_control_state(state)
    return row


def monitor_process(action_id: str, proc: subprocess.Popen, log_path: Path) -> None:
    returncode = proc.wait()
    with ACTIVE_LOCK:
        ACTIVE_PROCS.pop(action_id, None)
    update_action_state(
        action_id,
        status="ok" if returncode == 0 else "failed",
        returncode=returncode,
        last_finished_at=now_utc_iso(),
        log_path=str(log_path),
    )


def start_action(action_id: str) -> tuple[bool, str]:
    if action_id not in ACTIONS:
        return False, "未知动作。"
    if is_proc_running(action_id):
        return False, "这个动作还在运行，别重复点。"

    action = ACTIONS[action_id]
    CONTROL_LOG_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    log_path = CONTROL_LOG_DIR / f"{action_id}_{stamp}.log"
    cmd = action["command"]

    with log_path.open("w", encoding="utf-8") as f:
        f.write(f"[started_at] {now_utc_iso()}\n")
        f.write(f"[action] {action_id}\n")
        f.write(f"[command] {cmd}\n\n")
        f.flush()
        proc = subprocess.Popen(
            ["/bin/bash", "-lc", cmd],
            cwd=str(ROOT),
            stdout=f,
            stderr=subprocess.STDOUT,
            text=True,
        )

    with ACTIVE_LOCK:
        ACTIVE_PROCS[action_id] = proc

    update_action_state(
        action_id,
        status="running",
        pid=proc.pid,
        returncode=None,
        last_started_at=now_utc_iso(),
        last_finished_at=None,
        log_path=str(log_path),
        command=cmd,
    )
    threading.Thread(target=monitor_process, args=(action_id, proc, log_path), daemon=True).start()
    return True, f"已启动：{action['title']}"


def render_status_badge(status: str) -> str:
    klass = {
        "running": "warn",
        "ok": "ok",
        "failed": "bad",
    }.get(status or "", "idle")
    label = {
        "running": "运行中",
        "ok": "成功",
        "failed": "失败",
    }.get(status or "", "未运行")
    return f"<span class='pill {klass}'>{html.escape(label)}</span>"


def run_text_command(command: str, *, timeout: int = 20) -> str:
    try:
        out = subprocess.check_output(["/bin/bash", "-lc", command], cwd=str(ROOT), stderr=subprocess.STDOUT, text=True, timeout=timeout)
        return out.strip()
    except Exception as exc:  # noqa: BLE001
        return f"命令执行失败：{exc}"


def render_simple_table(columns: list[str], rows: list[dict[str, object]]) -> str:
    if not rows:
        return "<div class='muted'>暂无数据。</div>"
    thead = "".join(f"<th>{html.escape(str(col))}</th>" for col in columns)
    trs = []
    for row in rows:
        tds = []
        for col in columns:
            val = row.get(col, "-")
            if isinstance(val, float):
                text = f"{val:.4f}"
            else:
                text = str(val)
            tds.append(f"<td>{html.escape(text)}</td>")
        trs.append(f"<tr>{''.join(tds)}</tr>")
    return f"<table class='mini-table'><thead><tr>{thead}</tr></thead><tbody>{''.join(trs)}</tbody></table>"


def render_live_overview() -> str:
    summary = load_json(ROOT / "reports" / "artifacts" / "rank32b_canary" / "phase6_last_run_summary.json")
    state = load_json(ROOT / "reports" / "artifacts" / "rank32b_canary" / "phase6_state.json")
    warnings = load_json(ROOT / "reports" / "artifacts" / "rank32b_canary" / "phase6_warnings.json")
    closed = load_json(ROOT / "reports" / "artifacts" / "rank32b_canary" / "phase6_recent_closed_trades.json")
    signals = load_json(ROOT / "reports" / "artifacts" / "rank32b_canary" / "phase6_recent_signals.json")
    rejections = load_json(ROOT / "reports" / "artifacts" / "rank32b_canary" / "phase6_recent_rejections.json")
    snapshot = run_text_command(f"/usr/bin/python3 {SNAPSHOT_SCRIPT}", timeout=30)
    timer_status = run_text_command("systemctl is-active momentum-rank32b-canary-phase6.timer || true", timeout=10)
    service_status = run_text_command("systemctl is-active momentum-rank32b-canary-phase6.service || true", timeout=10)
    whitelist = ", ".join(state.get("enabled_symbols", [])) if isinstance(state, dict) else ""
    whitelist = whitelist or "-"
    live_positions = len(state.get("live_positions", [])) if isinstance(state, dict) and isinstance(state.get("live_positions"), list) else 0
    warning_count = len(warnings) if isinstance(warnings, list) else 0
    closed_rows = closed if isinstance(closed, list) else []
    signal_rows = signals if isinstance(signals, list) else []
    rejection_rows = rejections if isinstance(rejections, list) else []

    total_pnl = 0.0
    wins = 0
    tp_hits = sl_hits = timeout_hits = external_hits = 0
    side_stats: dict[str, dict[str, float]] = {}
    exit_stats: dict[str, dict[str, float]] = {}
    for row in closed_rows:
        pnl = row.get("net_pnl")
        if pnl is None:
            pnl = row.get("gross_pnl")
        try:
            pnl_val = float(pnl or 0.0)
        except Exception:
            pnl_val = 0.0
        total_pnl += pnl_val
        if pnl_val > 0:
            wins += 1
        side = str(row.get("side") or "-")
        exit_reason = str(row.get("exit_reason") or "-")
        side_bucket = side_stats.setdefault(side, {"closed_trades": 0, "pnl": 0.0, "tp": 0, "sl": 0, "timeout": 0, "external": 0})
        side_bucket["closed_trades"] += 1
        side_bucket["pnl"] += pnl_val
        if exit_reason == "take_profit":
            side_bucket["tp"] += 1
            tp_hits += 1
        elif exit_reason == "stop_loss":
            side_bucket["sl"] += 1
            sl_hits += 1
        elif exit_reason == "timeout_market":
            side_bucket["timeout"] += 1
            timeout_hits += 1
        elif exit_reason in {"manual_market_close", "external_flat_reconciled", "exit_attach_failed_market_close", "tp_attach_failed_market_close"}:
            side_bucket["external"] += 1
            external_hits += 1
        exit_bucket = exit_stats.setdefault(exit_reason, {"closed_trades": 0, "pnl": 0.0})
        exit_bucket["closed_trades"] += 1
        exit_bucket["pnl"] += pnl_val

    signal_side = {"long": 0, "short": 0}
    symbol_mix: dict[str, dict[str, float]] = {}
    for row in signal_rows:
        side = str(row.get("side") or "-")
        symbol = str(row.get("symbol") or "-")
        if side in signal_side:
            signal_side[side] += 1
        bucket = symbol_mix.setdefault(symbol, {"signals": 0, "long_signals": 0, "short_signals": 0, "closed_trades": 0, "pnl": 0.0, "rejections": 0})
        bucket["signals"] += 1
        if side == "long":
            bucket["long_signals"] += 1
        elif side == "short":
            bucket["short_signals"] += 1
    for row in closed_rows:
        symbol = str(row.get("symbol") or "-")
        bucket = symbol_mix.setdefault(symbol, {"signals": 0, "long_signals": 0, "short_signals": 0, "closed_trades": 0, "pnl": 0.0, "rejections": 0})
        bucket["closed_trades"] += 1
        pnl = row.get("net_pnl") if row.get("net_pnl") is not None else row.get("gross_pnl")
        try:
            bucket["pnl"] += float(pnl or 0.0)
        except Exception:
            pass
    for row in rejection_rows:
        symbol = str(row.get("symbol") or "-")
        bucket = symbol_mix.setdefault(symbol, {"signals": 0, "long_signals": 0, "short_signals": 0, "closed_trades": 0, "pnl": 0.0, "rejections": 0})
        bucket["rejections"] += 1

    side_rows = [{"side": k, **v} for k, v in sorted(side_stats.items())]
    exit_rows = [{"exit_reason": k, **v} for k, v in sorted(exit_stats.items(), key=lambda kv: (-int(kv[1]["closed_trades"]), kv[0]))]
    symbol_rows = [{"symbol": k, **v} for k, v in sorted(symbol_mix.items())]
    win_rate = (wins / len(closed_rows) * 100.0) if closed_rows else 0.0
    last_signal = signal_rows[-1].get("timestamp") if signal_rows else "-"
    status_badge = render_status_badge('ok' if str(timer_status).strip() == 'active' else 'failed')

    return f"""
    <div class='card'>
      <div class='card-top'>
        <div>
          <h2 style='margin:0 0 8px;'>32B Live 策略总览</h2>
          <div class='muted'>重点只看三件事：有没有正常跑、最近赚没赚、结构是不是健康。</div>
          <div class='muted'>统一入口：<a href='/momentum/factors/rank32b/report.html'>32b 主页面</a> ｜ <a href='/momentum/factors/rank32b_canary/report.html'>实盘 Dashboard</a> ｜ <a href='/momentum/factors/scout_rank32b_slope_floor_continuation_15m/report.html'>主研究报告</a></div>
        </div>
        <div>{status_badge}</div>
      </div>

      <h3 style='margin:12px 0 10px;'>1) 运行健康</h3>
      <div class='meta-grid small'>
        <div class='box'><b>白名单交易币种</b><br />{html.escape(whitelist)}</div>
        <div class='box'><b>自动 timer / service</b><br />{html.escape(timer_status or '-')} / {html.escape(service_status or '-')}</div>
        <div class='box'><b>最近完成时间</b><br />{html.escape(str(summary.get('run_finished_at') or summary.get('generated_at_utc') or '-'))}</div>
        <div class='box'><b>最近信号时间</b><br />{html.escape(str(last_signal or '-'))}</div>
        <div class='box'><b>当前本地持仓数</b><br />{live_positions}</div>
        <div class='box'><b>账户外部仓位提醒</b><br />{html.escape(str(summary.get('external_account_warnings', 0) or 0))}</div>
        <div class='box'><b>最近一轮订单数</b><br />{html.escape(str(summary.get('orders_emitted', '-')))}</div>
        <div class='box'><b>最近 warnings 数</b><br />{warning_count}</div>
      </div>

      <h3 style='margin:12px 0 10px;'>2) 最近盈亏拆解</h3>
      <div class='meta-grid small'>
        <div class='box'><b>recent closed trades</b><br />{len(closed_rows)}</div>
        <div class='box'><b>总 PnL</b><br />{total_pnl:.4f}</div>
        <div class='box'><b>胜率</b><br />{win_rate:.2f}%</div>
        <div class='box'><b>TP / SL / timeout</b><br />{tp_hits} / {sl_hits} / {timeout_hits}</div>
        <div class='box'><b>外部干预退出</b><br />{external_hits}</div>
      </div>
      {render_simple_table(["side", "closed_trades", "pnl", "tp", "sl", "timeout", "external"], side_rows)}
      {render_simple_table(["exit_reason", "closed_trades", "pnl"], exit_rows)}

      <h3 style='margin:12px 0 10px;'>3) 信号 / 交易结构健康度</h3>
      <div class='meta-grid small'>
        <div class='box'><b>recent signals</b><br />{len(signal_rows)}</div>
        <div class='box'><b>long / short signals</b><br />{signal_side['long']} / {signal_side['short']}</div>
        <div class='box'><b>risk rejections</b><br />{len(rejection_rows)}</div>
        <div class='box'><b>unexpected exchange positions</b><br />{html.escape(str(summary.get('unexpected_exchange_positions', 0) or 0))}</div>
      </div>
      {render_simple_table(["symbol", "signals", "long_signals", "short_signals", "closed_trades", "rejections", "pnl"], symbol_rows)}

      <details open>
        <summary>中文运行快照</summary>
        <pre>{html.escape(snapshot or '暂无快照。')}</pre>
      </details>
    </div>
    """


def render_strategy_config_card() -> str:
    cfg = load_yaml(CONFIG_PATH)
    phase6 = cfg.get("phase6", {}) if isinstance(cfg, dict) else {}
    sizing = phase6.get("sizing", {}) if isinstance(phase6, dict) else {}
    exit_cfg = phase6.get("exit", {}) if isinstance(phase6, dict) else {}
    risk_cfg = cfg.get("risk", {}) if isinstance(cfg, dict) else {}
    symbols = [str(s).upper() for s in ((cfg.get("universe", {}) or {}).get("symbols", []) or [])]
    by_symbol = sizing.get("desired_notional_usdt_by_symbol", {})
    if not isinstance(by_symbol, dict):
        by_symbol = {}

    default_notional = float(sizing.get("desired_notional_usdt", 50.0) or 50.0)
    symbol_inputs = []
    for symbol in symbols:
        value = float(by_symbol.get(symbol, default_notional) or default_notional)
        symbol_inputs.append(
            f"""
            <label class='box' style='display:block;'>
              <b>{html.escape(symbol)} 目标仓位 (USDT)</b><br />
              <input type='number' step='0.1' min='1' name='notional_{html.escape(symbol)}' value='{value:.2f}' style='width:100%;margin-top:8px;background:#0a0f1f;color:#e5e7eb;border:1px solid #27314f;border-radius:8px;padding:8px;' />
            </label>
            """
        )

    trade_enabled_checked = "checked" if bool(risk_cfg.get("trade_enabled", True)) else ""
    kill_switch_checked = "checked" if bool(risk_cfg.get("kill_switch", False)) else ""
    selection_cfg = phase6.get("selection", {}) if isinstance(phase6, dict) else {}

    return f"""
    <div class='card'>
      <div class='card-top'>
        <div>
          <h2 style='margin:0 0 8px;'>策略关键配置（网页可改）</h2>
          <div class='muted'>保存后会写回 <code>{html.escape(str(CONFIG_PATH))}</code>，并自动重建 dashboard；phase6 下一轮会按新配置执行。</div>
          <div class='muted'>当前选择模式：<b>{html.escape(str(selection_cfg.get('mode', 'all_signals')))}</b>（按 <b>{html.escape(str(selection_cfg.get('strength_metric', 'slope_strength')))}</b> 只做最强信号）。</div>
        </div>
      </div>
      <form method='post' action='./save-config'>
        <div class='meta-grid small'>
          <label class='box' style='display:block;'>
            <b>默认目标仓位 (USDT)</b><br />
            <input type='number' step='0.1' min='1' name='desired_notional_usdt' value='{default_notional:.2f}' style='width:100%;margin-top:8px;background:#0a0f1f;color:#e5e7eb;border:1px solid #27314f;border-radius:8px;padding:8px;' />
          </label>
          {''.join(symbol_inputs)}
        </div>
        <div class='meta-grid small'>
          <label class='box' style='display:block;'><b>TP ATR 倍数</b><br /><input type='number' step='0.05' min='0.1' name='tp_atr_mult' value='{float(exit_cfg.get('tp_atr_mult', 1.25)):.2f}' style='width:100%;margin-top:8px;background:#0a0f1f;color:#e5e7eb;border:1px solid #27314f;border-radius:8px;padding:8px;' /></label>
          <label class='box' style='display:block;'><b>SL ATR 倍数</b><br /><input type='number' step='0.05' min='0.1' name='sl_atr_mult' value='{float(exit_cfg.get('sl_atr_mult', 1.0)):.2f}' style='width:100%;margin-top:8px;background:#0a0f1f;color:#e5e7eb;border:1px solid #27314f;border-radius:8px;padding:8px;' /></label>
          <label class='box' style='display:block;'><b>Timeout (分钟)</b><br /><input type='number' step='1' min='5' name='timeout_minutes' value='{int(exit_cfg.get('timeout_minutes', 120) or 120)}' style='width:100%;margin-top:8px;background:#0a0f1f;color:#e5e7eb;border:1px solid #27314f;border-radius:8px;padding:8px;' /></label>
          <label class='box' style='display:block;'><b>默认杠杆</b><br /><input type='number' step='1' min='1' name='default_leverage' value='{int(phase6.get('default_leverage', 1) or 1)}' style='width:100%;margin-top:8px;background:#0a0f1f;color:#e5e7eb;border:1px solid #27314f;border-radius:8px;padding:8px;' /></label>
          <label class='box' style='display:block;'><b>每轮最多新信号</b><br /><input type='number' step='1' min='1' name='max_new_signals_per_run' value='{int(phase6.get('max_new_signals_per_run', 1) or 1)}' style='width:100%;margin-top:8px;background:#0a0f1f;color:#e5e7eb;border:1px solid #27314f;border-radius:8px;padding:8px;' /></label>
          <label class='box' style='display:block;'><b>最大并发持仓数</b><br /><input type='number' step='1' min='1' name='max_concurrent_positions' value='{int(risk_cfg.get('max_concurrent_positions', 1) or 1)}' style='width:100%;margin-top:8px;background:#0a0f1f;color:#e5e7eb;border:1px solid #27314f;border-radius:8px;padding:8px;' /></label>
          <label class='box' style='display:flex;align-items:center;gap:8px;'><input type='checkbox' name='trade_enabled' value='on' {trade_enabled_checked} /> <b>trade_enabled</b></label>
          <label class='box' style='display:flex;align-items:center;gap:8px;'><input type='checkbox' name='kill_switch' value='on' {kill_switch_checked} /> <b>kill_switch</b></label>
        </div>
        <div class='actions'>
          <button type='submit'>保存策略配置</button>
          <span class='muted'>说明：默认每笔 150U；若不满足交易所最小下单量，会自动抬到最小可下单数量。</span>
        </div>
      </form>
    </div>
    """


def render_controls(token: str) -> str:
    state = load_control_state().get("actions", {})
    cards: list[str] = [render_strategy_config_card()]
    for action_id, action in ACTIONS.items():
        row = state.get(action_id, {})
        status = str(row.get("status") or "")
        artifact = load_json(ACTION_ARTIFACTS[action_id]) if action_id in ACTION_ARTIFACTS else {}
        artifact_ts = str(artifact.get("generated_at_utc") or "")
        state_ts = str(row.get("last_finished_at") or "")
        if artifact_ts and (not state_ts or artifact_ts > state_ts):
            status = "ok"
        log_path = Path(str(row.get("log_path") or "")) if row.get("log_path") else None
        tail = tail_text(log_path) if log_path else "暂无日志。"
        artifact_summary = ""
        if artifact:
            artifact_summary = html.escape(json.dumps(artifact, ensure_ascii=False, indent=2))
        cards.append(
            f"""
            <div class='card control-card'>
              <div class='card-top'>
                <div>
                  <h3>{html.escape(action['title'])}</h3>
                  <div class='muted'>{html.escape(action['desc'])}</div>
                </div>
                <div>{render_status_badge(status)}</div>
              </div>
              <div class='meta-grid small'>
                <div class='box'><b>最近启动</b><br />{html.escape(str(row.get('last_started_at') or '-'))}</div>
                <div class='box'><b>最近结束</b><br />{html.escape(str(row.get('last_finished_at') or '-'))}</div>
                <div class='box'><b>Return code</b><br />{html.escape(str(row.get('returncode') if row.get('returncode') is not None else '-'))}</div>
                <div class='box'><b>最近策略产物</b><br />{html.escape(artifact_ts or '-')}</div>
              </div>
              <div class='codebox'><code>{html.escape(action['command'])}</code></div>
              <form method='post' action='./run' class='actions'>
                <input type='hidden' name='action_id' value='{html.escape(action_id)}' />
                <button type='submit' class='{'danger' if action.get('danger') else ''}'>{html.escape(action['button'])}</button>
                <a class='btn secondary' href='./log?action_id={quote(action_id)}' target='_blank'>查看最新日志</a>
              </form>
              <details>
                <summary>日志尾部</summary>
                <pre>{html.escape(tail)}</pre>
              </details>
              <details>
                <summary>最近策略产物摘要</summary>
                <pre>{artifact_summary or '暂无策略产物。'}</pre>
              </details>
            </div>
            """
        )

    dashboard_link = "./dashboard"
    return f"""
    <div class='hero'>
      <h1>32B Canary 控制台</h1>
      <div class='muted'>这里放的是你要点的三个按钮：单次 live 验证、单次启动 canary、启动自动定时运行。所有动作都会写日志，并可直接跳看 dashboard。</div>
      <div class='actions' style='margin-top:14px;'>
        <a class='btn secondary' href='{dashboard_link}' target='_blank'>打开当前 Canary Dashboard</a>
      </div>
    </div>
    <div class='grid controls-grid'>
      {''.join(cards)}
    </div>
    """


def render_page(doc_path: Path, content: str, saved: bool, token: str, flash: str = "") -> bytes:
    saved_html = '<div class="flash ok">已保存到服务器。</div>' if saved else ""
    flash_html = f'<div class="flash ok">{html.escape(flash)}</div>' if flash else ""
    title = "32B Canary TODO + Control"
    overview_html = render_live_overview()
    controls_html = render_controls(token)
    html_doc = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{html.escape(title)}</title>
  <style>
    :root {{
      --bg: #0b1020;
      --panel: #121933;
      --panel-2: #0f152b;
      --text: #e5e7eb;
      --muted: #9ca3af;
      --line: #27314f;
      --accent: #60a5fa;
      --ok: #10b981;
      --warn: #f59e0b;
      --bad: #ef4444;
    }}
    body {{ margin: 0; font-family: Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif; background: var(--bg); color: var(--text); }}
    .wrap {{ max-width: 1280px; margin: 0 auto; padding: 24px; }}
    .hero {{ background: linear-gradient(180deg, #151d39 0%, #0f152b 100%); border: 1px solid var(--line); border-radius: 16px; padding: 20px 22px; margin-bottom: 18px; }}
    .hero h1 {{ margin: 0 0 8px; font-size: 30px; }}
    .muted {{ color: var(--muted); }}
    .card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 16px; padding: 18px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 16px; margin-bottom: 18px; }}
    .meta-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-bottom: 16px; }}
    .meta-grid.small {{ margin-top: 14px; margin-bottom: 12px; }}
    .box {{ background: var(--panel-2); border: 1px solid var(--line); border-radius: 12px; padding: 12px; }}
    textarea {{ width: 100%; min-height: 72vh; box-sizing: border-box; resize: vertical; border-radius: 12px; border: 1px solid var(--line); background: #0a0f1f; color: var(--text); padding: 16px; font: 14px/1.6 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
    .actions {{ display: flex; gap: 12px; align-items: center; margin-top: 14px; flex-wrap: wrap; }}
    button, a.btn {{ appearance: none; border: 0; border-radius: 10px; padding: 10px 16px; background: var(--accent); color: #08111f; font-weight: 700; text-decoration: none; cursor: pointer; }}
    button.danger {{ background: #fca5a5; color: #3f0a0a; }}
    a.btn.secondary {{ background: #1f2937; color: var(--text); border: 1px solid var(--line); }}
    .flash.ok {{ margin-bottom: 12px; padding: 10px 12px; border-radius: 10px; background: rgba(16,185,129,0.12); color: #a7f3d0; border: 1px solid rgba(16,185,129,0.35); }}
    .codebox {{ margin-top: 12px; }}
    code, pre {{ background: #0a0f1f; border: 1px solid var(--line); border-radius: 8px; }}
    code {{ padding: 2px 6px; display: block; white-space: pre-wrap; word-break: break-word; }}
    pre {{ padding: 14px; white-space: pre-wrap; word-break: break-word; overflow-x: auto; }}
    .pill {{ display: inline-block; border-radius: 999px; padding: 6px 10px; font-size: 12px; font-weight: 700; }}
    .pill.ok {{ background: rgba(16,185,129,.15); color: #a7f3d0; border: 1px solid rgba(16,185,129,.35); }}
    .pill.warn {{ background: rgba(245,158,11,.15); color: #fde68a; border: 1px solid rgba(245,158,11,.35); }}
    .pill.bad {{ background: rgba(239,68,68,.15); color: #fecaca; border: 1px solid rgba(239,68,68,.35); }}
    .pill.idle {{ background: rgba(148,163,184,.12); color: #cbd5e1; border: 1px solid rgba(148,163,184,.25); }}
    .card-top {{ display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; }}
    summary {{ cursor: pointer; color: #cbd5e1; margin-top: 8px; }}
    .mini-table {{ width: 100%; border-collapse: collapse; margin: 12px 0 16px; background: var(--panel-2); border: 1px solid var(--line); border-radius: 12px; overflow: hidden; }}
    .mini-table th, .mini-table td {{ text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--line); font-size: 13px; vertical-align: top; }}
    .mini-table th {{ color: #cbd5e1; background: #0b1220; }}
    .mini-table tr:last-child td {{ border-bottom: none; }}
  </style>
</head>
<body>
  <div class=\"wrap\">
    {overview_html}
    {controls_html}
    <div class=\"hero\">
      <h1>32B Canary TODO Editor</h1>
      <div class=\"muted\">这是独立编辑页，专门给 32b canary 长文档用；不走 bot2 / bot3 / bot6 / bot7 的现有定时链路。</div>
    </div>
    <div class=\"meta-grid\">
      <div class=\"box\"><b>文档路径</b><br /><code>{html.escape(str(doc_path))}</code></div>
      <div class=\"box\"><b>最近页面生成</b><br />{html.escape(now_utc())}</div>
      <div class=\"box\"><b>访问 token</b><br /><code>{html.escape(token[:10])}…</code></div>
    </div>
    <div class=\"card\">
      {saved_html}
      {flash_html}
      <form method=\"post\" action=\"./save\">
        <textarea name=\"content\" spellcheck=\"false\">{html.escape(content)}</textarea>
        <div class=\"actions\">
          <button type=\"submit\">保存到服务器</button>
          <a class=\"btn secondary\" href=\"./raw\" target=\"_blank\">查看原始 Markdown</a>
        </div>
      </form>
    </div>
  </div>
</body>
</html>
"""
    return html_doc.encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    doc_path: Path = DEFAULT_DOC
    token: str = ""

    def _send(self, code: int, body: bytes, content_type: str = "text/html; charset=utf-8") -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _authorized(self) -> bool:
        path = urlparse(self.path).path.rstrip("/")
        return path.startswith(f"/{self.token}")

    def _subpath(self) -> str:
        path = urlparse(self.path).path
        prefix = f"/{self.token}"
        if path.startswith(prefix):
            rest = path[len(prefix):]
            return rest or "/"
        return path

    def do_GET(self) -> None:
        if not self._authorized():
            self._send(404, b"not found", "text/plain; charset=utf-8")
            return
        sub = self._subpath()
        ensure_doc(self.doc_path)
        if sub in {"", "/"}:
            qs = parse_qs(urlparse(self.path).query)
            saved = qs.get("saved", ["0"])[0] == "1"
            flash = qs.get("flash", [""])[0]
            body = render_page(self.doc_path, self.doc_path.read_text(encoding="utf-8"), saved=saved, token=self.token, flash=flash)
            self._send(200, body)
            return
        if sub == "/raw":
            self._send(200, self.doc_path.read_bytes(), "text/plain; charset=utf-8")
            return
        if sub == "/healthz":
            self._send(200, b"ok\n", "text/plain; charset=utf-8")
            return
        if sub == "/dashboard":
            if DASHBOARD_PATH.exists():
                self._send(200, DASHBOARD_PATH.read_bytes(), "text/html; charset=utf-8")
            else:
                self._send(404, b"dashboard not generated yet\n", "text/plain; charset=utf-8")
            return
        if sub == "/log":
            qs = parse_qs(urlparse(self.path).query)
            action_id = qs.get("action_id", [""])[0]
            state = load_control_state().get("actions", {})
            row = state.get(action_id, {})
            log_path = Path(str(row.get("log_path") or "")) if row.get("log_path") else None
            body = tail_text(log_path, max_lines=200).encode("utf-8")
            self._send(200, body, "text/plain; charset=utf-8")
            return
        self._send(404, b"not found", "text/plain; charset=utf-8")

    def do_POST(self) -> None:
        if not self._authorized():
            self._send(404, b"not found", "text/plain; charset=utf-8")
            return
        sub = self._subpath()
        if sub == "/save":
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8", errors="replace")
            form = parse_qs(raw, keep_blank_values=True)
            content = form.get("content", [""])[0]
            content = content.replace("\r\n", "\n")
            ensure_doc(self.doc_path)
            self.doc_path.write_text(content, encoding="utf-8")
            self.send_response(303)
            self.send_header("Location", "./?saved=1")
            self.end_headers()
            return
        if sub == "/save-config":
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8", errors="replace")
            form = parse_qs(raw, keep_blank_values=True)
            try:
                msg = save_canary_config_from_form(form)
                _ = run_text_command(DASHBOARD_BUILD_CMD, timeout=40)
                flash = quote(msg + "；dashboard 已刷新")
            except Exception as exc:  # noqa: BLE001
                flash = quote(f"配置保存失败：{exc}")
            self.send_response(303)
            self.send_header("Location", f"./?flash={flash}")
            self.end_headers()
            return
        if sub == "/run":
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8", errors="replace")
            form = parse_qs(raw, keep_blank_values=True)
            action_id = form.get("action_id", [""])[0]
            ok, msg = start_action(action_id)
            flash = quote(msg)
            self.send_response(303)
            self.send_header("Location", f"./?flash={flash}")
            self.end_headers()
            return
        self._send(404, b"not found", "text/plain; charset=utf-8")

    def log_message(self, fmt: str, *args) -> None:
        print(f"[canary-doc-editor] {self.address_string()} - {fmt % args}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve a tiny editor for the 32b canary todo doc.")
    parser.add_argument("--host", default=HOST)
    parser.add_argument("--port", type=int, default=PORT)
    parser.add_argument("--doc", default=str(DEFAULT_DOC))
    parser.add_argument("--token-file", default=str(TOKEN_FILE))
    args = parser.parse_args()

    doc_path = Path(args.doc).resolve()
    token = ensure_token(Path(args.token_file).resolve())
    ensure_doc(doc_path)
    CONTROL_LOG_DIR.mkdir(parents=True, exist_ok=True)
    save_control_state(load_control_state())

    Handler.doc_path = doc_path
    Handler.token = token

    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"[canary-doc-editor] serving {doc_path} on http://{args.host}:{args.port}/{token}/")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
