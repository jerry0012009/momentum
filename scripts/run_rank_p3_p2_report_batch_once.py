#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path('/root/clawd/jerry/momentum')
CSV_PATH = ROOT / 'reports' / 'artifacts' / 'rank_registry' / 'full_rank_p3_p2_table.csv'
STATE_PATH = ROOT / 'reports' / 'artifacts' / 'rank_registry' / 'p3_p2_report_batch_state.json'
DEDICATED_BUILDER = ROOT / 'scripts' / 'build_rank_p2p3_dedicated_reports.py'
REGISTRY_BUILDER = ROOT / 'scripts' / 'build_rank_p3_p2_full_registry_page.py'

EVERY_MS = 15 * 60 * 1000


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_rows() -> list[dict[str, str]]:
    if not CSV_PATH.exists():
        raise FileNotFoundError(CSV_PATH)
    rows = list(csv.DictReader(CSV_PATH.open('r', encoding='utf-8')))
    return [r for r in rows if (r.get('rank') or '').strip()]


def seed_state(rows: list[dict[str, str]]) -> dict[str, Any]:
    tasks = []
    for i, row in enumerate(rows, start=1):
        rank = (row.get('rank') or '').strip()
        stage = (row.get('stage') or '').strip()
        status = 'pending'
        note = ''
        # 用户已确认“第1个任务完成”，seed 时直接记 done。
        if i == 1:
            status = 'done'
            note = 'seeded-as-done: user-confirmed first task already completed before batch landing'
        tasks.append({
            'order': i,
            'rank': rank,
            'stage': stage,
            'status': status,
            'goal': '按双页结构生成 report + decomposition，并清晰说明策略原理与信号定义。',
            'report_path': f'reports/site/factors/{rank}/report.html',
            'decomposition_path': f'reports/site/factors/{rank}/decomposition.html',
            'started_at': None,
            'finished_at': None,
            'last_error': '',
            'notes': note,
        })
    return {
        'version': 1,
        'cadence_every_ms': EVERY_MS,
        'source_csv': str(CSV_PATH.relative_to(ROOT)),
        'updated_at': now_iso(),
        'tasks': tasks,
    }


def load_or_init_state(rows: list[dict[str, str]]) -> dict[str, Any]:
    if STATE_PATH.exists():
        obj = json.loads(STATE_PATH.read_text(encoding='utf-8'))
        if isinstance(obj, dict) and isinstance(obj.get('tasks'), list):
            return obj
    state = seed_state(rows)
    save_state(state)
    return state


def save_state(state: dict[str, Any]) -> None:
    state['updated_at'] = now_iso()
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')


def summarize(state: dict[str, Any]) -> dict[str, int]:
    c = {'pending': 0, 'running': 0, 'done': 0, 'blocked': 0}
    for t in state.get('tasks', []):
        s = (t.get('status') or '').strip()
        if s in c:
            c[s] += 1
    return c


def first_pending_task(state: dict[str, Any]) -> dict[str, Any] | None:
    tasks = state.get('tasks', [])
    tasks = sorted(tasks, key=lambda x: int(x.get('order') or 10**9))
    for task in tasks:
        if (task.get('status') or '').strip() == 'pending':
            return task
    return None


def run_cmd(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(ROOT), text=True, capture_output=True, check=False)


def run_one_rank(rank: str) -> tuple[bool, str]:
    step1 = run_cmd(['python3', str(DEDICATED_BUILDER), '--rank', rank])
    if step1.returncode != 0:
        return False, f'build_rank_p2p3_dedicated_reports failed: {step1.stderr.strip()[:800]}'
    return True, step1.stdout.strip()


def main() -> int:
    rows = read_rows()
    state = load_or_init_state(rows)

    # 若已有 running，防重入。
    for t in state.get('tasks', []):
        if (t.get('status') or '').strip() == 'running':
            print(json.dumps({
                'ok': True,
                'action': 'skip_already_running',
                'running_rank': t.get('rank'),
                'summary': summarize(state),
                'state_path': str(STATE_PATH),
            }, ensure_ascii=False))
            return 0

    task = first_pending_task(state)
    if task is None:
        print(json.dumps({
            'ok': True,
            'action': 'all_done',
            'summary': summarize(state),
            'state_path': str(STATE_PATH),
        }, ensure_ascii=False))
        return 0

    rank = (task.get('rank') or '').strip()
    task['status'] = 'running'
    task['started_at'] = now_iso()
    task['last_error'] = ''
    save_state(state)

    ok, detail = run_one_rank(rank)
    if ok:
        task['status'] = 'done'
        task['finished_at'] = now_iso()
        task['notes'] = (task.get('notes') or '') + f'\ncompleted by batch runner at {task["finished_at"]}'
    else:
        task['status'] = 'blocked'
        task['finished_at'] = now_iso()
        task['last_error'] = detail

    save_state(state)

    # 状态落盘后再刷新总表，避免页面显示为 stale running。
    step_registry = run_cmd(['python3', str(REGISTRY_BUILDER)])
    if step_registry.returncode != 0:
        ok = False
        detail = (detail + '\n' + f'build_rank_p3_p2_full_registry_page failed: {step_registry.stderr.strip()[:800]}').strip()

    print(json.dumps({
        'ok': ok,
        'rank': rank,
        'detail': detail,
        'summary': summarize(state),
        'state_path': str(STATE_PATH),
    }, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
