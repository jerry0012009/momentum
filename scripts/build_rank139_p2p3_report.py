#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path('/root/clawd/jerry/momentum')
ART = ROOT / 'reports' / 'artifacts' / 'scout_rank139_cusum_event_bar_confirm_veto_15m'
REG = ROOT / 'reports' / 'artifacts' / 'rank_registry' / 'full_rank_p3_p2_table.csv'
OUT = ROOT / 'reports' / 'site' / 'factors' / 'rank139' / 'report.html'
BJ = timezone(timedelta(hours=8), name='Asia/Shanghai')


def pct(x: float | int | None, digits: int = 2) -> str:
    if x is None:
        return '-'
    try:
        return f"{float(x)*100:.{digits}f}%"
    except Exception:
        return '-'


def num(x: float | int | None, digits: int = 4) -> str:
    if x is None:
        return '-'
    try:
        return f"{float(x):.{digits}f}"
    except Exception:
        return '-'


def load_registry_rank139() -> dict[str, str]:
    rows = list(csv.DictReader(REG.open('r', encoding='utf-8')))
    for r in rows:
        if (r.get('rank') or '').strip() == 'rank139':
            return r
    raise RuntimeError('rank139 not found in registry csv')


def render() -> str:
    reg = load_registry_rank139()
    meta = json.loads((ART / 'meta.json').read_text(encoding='utf-8'))
    arm = pd.read_csv(ART / 'summary_by_arm.csv')
    board = pd.read_csv(ART / 'narrow_paper_pilot_monitoring_board.csv')

    baseline = arm[arm['arm'] == 'baseline'].iloc[0].to_dict()
    non_base = arm[arm['arm'] != 'baseline'].sort_values('mean_net@6bps', ascending=False)
    best_gate = non_base.iloc[0].to_dict() if not non_base.empty else None

    board2 = board.copy()
    board2['delta_net_vs_base@6bps'] = board2['mean_net_kept@6bps'] - board2['mean_net_base@6bps']
    board_best = board2.sort_values('delta_net_vs_base@6bps', ascending=False).head(8)

    assets = sorted(str(x) for x in board['asset'].dropna().unique())
    setups = sorted(str(x) for x in board['setup'].dropna().unique())

    generated_at = datetime.now(timezone.utc)
    generated_text = generated_at.astimezone(BJ).strftime('%Y-%m-%d %H:%M:%S 北京时间')

    arm_rows = []
    for _, r in arm.sort_values(['thr_mult', 'arm']).iterrows():
        arm_rows.append(
            '<tr>'
            f"<td>{num(r['thr_mult'], 2)}</td>"
            f"<td><code>{escape(str(r['arm']))}</code></td>"
            f"<td>{int(r['trades'])}</td>"
            f"<td>{pct(r['retention_vs_base'])}</td>"
            f"<td>{num(r['mean_gross'], 5)}</td>"
            f"<td>{num(r['mean_net@6bps'], 5)}</td>"
            f"<td>{pct(r['positive_ratio_net'])}</td>"
            f"<td>{pct(r['same_dir_first'])}</td>"
            f"<td>{pct(r['opp_dir_first'])}</td>"
            '</tr>'
        )

    board_rows = []
    for _, r in board_best.iterrows():
        board_rows.append(
            '<tr>'
            f"<td>{escape(str(r['asset']))}</td>"
            f"<td><code>{escape(str(r['setup']))}</code></td>"
            f"<td><code>{escape(str(r['arm']))}</code></td>"
            f"<td>{int(r['kept_trades'])}/{int(r['base_trades'])}</td>"
            f"<td>{pct(r['retention'])}</td>"
            f"<td>{num(r['mean_net_base@6bps'],5)}</td>"
            f"<td>{num(r['mean_net_kept@6bps'],5)}</td>"
            f"<td>{num(r['delta_net_vs_base@6bps'],5)}</td>"
            '</tr>'
        )

    best_gate_text = '无' if best_gate is None else (
        f"thr_mult={num(best_gate['thr_mult'],2)} / {best_gate['arm']}，"
        f"trades={int(best_gate['trades'])}，mean_net@6bps={num(best_gate['mean_net@6bps'],5)}"
    )

    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>rank139 · P3 独立策略报告（详细版）</title>
  <style>
    :root {{ --bg:#f8fafc; --card:#fff; --line:#e2e8f0; --text:#0f172a; --muted:#64748b; }}
    body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width:1180px; margin:26px auto; padding:0 16px; background:var(--bg); color:var(--text); line-height:1.64; }}
    .card {{ background:var(--card); border:1px solid var(--line); border-radius:12px; padding:14px 16px; margin-bottom:12px; }}
    h1,h2 {{ margin:0 0 8px; }}
    .muted {{ color:var(--muted); }}
    .pill {{ display:inline-block; border-radius:999px; padding:3px 9px; font-size:12px; background:#e2e8f0; }}
    table {{ width:100%; border-collapse:collapse; font-size:14px; }}
    th,td {{ border-bottom:1px solid var(--line); padding:8px 10px; text-align:left; vertical-align:top; }}
    th {{ background:#f1f5f9; }}
    code {{ background:#eff6ff; border-radius:6px; padding:1px 5px; }}
    pre {{ white-space:pre-wrap; background:#0b1220; color:#dbeafe; border-radius:10px; padding:10px; font-size:12px; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>rank139 · P3 独立策略报告（详细版）</h1>
    <p class="muted">本页针对 P3/P2 清单中的第 1 个 rank（rank139）做详细拆分：策略类型、挑战基线、信号定义、event-bar confirm/veto 机制与当前证据。</p>
    <p>
      <a href="../rank_registry_p3_p2/report.html">← 返回 P3/P2 总表</a> ｜
      <a href="../rank_registry_p3_p2_entries/rank139/report.html">registry entry</a> ｜
      <a href="../scout_rank139_cusum_event_bar_confirm_veto_15m/report.html">clean replication 报告</a> ｜
      <a href="../scout_rank139_cusum_event_bar_confirm_veto_15m/narrow_paper_monitoring_board.html">pilot monitoring board</a>
    </p>
    <p class="muted">页面生成时间：{escape(generated_text)}</p>
  </div>

  <div class="card">
    <h2>1) 策略定位（P3 拆分）</h2>
    <p><b>stage：</b>{escape(reg['stage'])} ｜ <b>status：</b><span class="pill">{escape(reg['status'])}</span></p>
    <p><b>策略类型（mother theme）：</b>{escape(reg['mother_theme'])}</p>
    <p><b>角色（role）：</b>{escape(reg['role'])}</p>
    <p><b>挑战基线（challenge baseline）：</b>{escape(reg['challenge_baseline'])}</p>
    <p><b>唯一增量（unique increment）：</b>{escape(reg['unique_increment'])}</p>
    <p><b>下一步动作（registry）：</b>{escape(reg['next_action'])}</p>
  </div>

  <div class="card">
    <h2>2) 信号原理与定义（可审计）</h2>
    <p class="muted">来自 clean replication 脚本：<code>scripts/build_rank139_cusum_event_bar_confirm_veto_clean_replication.py</code></p>

    <h3>2.1 基础 setup 信号</h3>
    <ul>
      <li><b>ema_psar_long</b>：<code>close &gt; ema20</code> 且 <code>psar_long=True</code> 且 <code>volume &gt; vol_ma20</code></li>
      <li><b>fib_reclaim_long</b>：<code>ema9 &gt; ema15</code>、<code>ema_slope &gt; 0</code>、<code>close &gt; fib_618</code></li>
      <li><b>breakout_long</b>：<code>ema9 &gt; ema15</code>、<code>ema_slope &gt; 0.0003</code>、<code>close &gt; prior20_high + 0.20*atr14</code></li>
      <li><b>breakout_short</b>：<code>ema9 &lt; ema15</code>、<code>ema_slope &lt; -0.0003</code>、<code>close &lt; prior20_low - 0.20*atr14</code></li>
    </ul>

    <h3>2.2 Event-bar confirm/veto 机制（rank139 核心）</h3>
    <ul>
      <li>入场后先等待 <code>latency_minutes={meta.get('latency_minutes')}</code> 分钟，再观察后续 1m 轨迹。</li>
      <li>阈值：<code>thr = thr_mult * (atr14/close)</code>（以入场时 15m bar 的 ATR 百分比缩放）</li>
      <li>在观察窗口内，记录首次触发事件：
        <ul>
          <li><code>same_dir_first</code>：先向持仓方向触发 +thr</li>
          <li><code>opp_dir_first</code>：先向反方向触发 -thr</li>
          <li><code>none</code>：都未触发</li>
        </ul>
      </li>
      <li>三种 arm：
        <ul>
          <li><code>baseline</code>：全部保留</li>
          <li><code>confirm_same_dir_only</code>：只保留 <code>same_dir_first</code></li>
          <li><code>veto_opp_dir</code>：剔除 <code>opp_dir_first</code></li>
        </ul>
      </li>
    </ul>
  </div>

  <div class="card">
    <h2>3) 参数与样本口径</h2>
    <p><b>assets：</b>{', '.join(assets)}</p>
    <p><b>setups：</b>{', '.join(setups)}</p>
    <p><b>thr_mults：</b>{', '.join(str(x) for x in meta.get('thr_mults', []))}</p>
    <p><b>latency_minutes：</b>{meta.get('latency_minutes')} ｜ <b>hold_bars_15m：</b>{meta.get('hold_bars_15m')} ｜ <b>cost_bps：</b>{meta.get('cost_bps')}</p>
    <p><b>scored_window：</b>{escape(str(meta.get('scored_window')))} ｜ <b>trades：</b>{meta.get('trades')}</p>
    <p><b>generated_at (artifact)：</b>{escape(str(meta.get('generated_at')))}</p>
  </div>

  <div class="card">
    <h2>4) 结果摘要（按 arm）</h2>
    <p><b>baseline：</b>trades={int(baseline['trades'])}，mean_net@6bps={num(baseline['mean_net@6bps'],5)}，positive_ratio={pct(baseline['positive_ratio_net'])}</p>
    <p><b>best gate（按 mean_net@6bps）：</b>{escape(best_gate_text)}</p>
    <table>
      <thead>
        <tr><th>thr_mult</th><th>arm</th><th>trades</th><th>retention</th><th>mean_gross</th><th>mean_net@6bps</th><th>positive_ratio</th><th>same_dir_first</th><th>opp_dir_first</th></tr>
      </thead>
      <tbody>{''.join(arm_rows)}</tbody>
    </table>
  </div>

  <div class="card">
    <h2>5) Asset × Setup 监控（pilot board Top）</h2>
    <p class="muted">以下按 <code>delta_net_vs_base@6bps</code> 排序，展示“保留后净收益相对 baseline 的改善”较高的条目。</p>
    <table>
      <thead>
        <tr><th>asset</th><th>setup</th><th>arm</th><th>kept/base</th><th>retention</th><th>mean_net_base</th><th>mean_net_kept</th><th>delta</th></tr>
      </thead>
      <tbody>{''.join(board_rows)}</tbody>
    </table>
  </div>

  <div class="card">
    <h2>6) 研究证据与复现路径</h2>
    <ul>
      <li><code>reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/meta.json</code></li>
      <li><code>reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/summary_by_arm.csv</code></li>
      <li><code>reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/narrow_paper_pilot_monitoring_board.csv</code></li>
      <li><code>reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/trade_log.csv</code></li>
      <li><code>scripts/build_rank139_cusum_event_bar_confirm_veto_clean_replication.py</code></li>
    </ul>
    <p class="muted">这页的作用是：把“策略类型/基线/信号定义/当前证据”放在一页说清楚，便于 P3/P2 维护与后续晋级判断。</p>
  </div>
</body>
</html>'''


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding='utf-8')
    print({'out': str(OUT)})
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
