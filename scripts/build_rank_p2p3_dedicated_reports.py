#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path

ROOT = Path('/root/clawd/jerry/momentum')
SITE_FACTORS = ROOT / 'reports' / 'site' / 'factors'
ARTIFACTS = ROOT / 'reports' / 'artifacts'
REGISTRY_CSV = ARTIFACTS / 'rank_registry' / 'full_rank_p3_p2_table.csv'
MANIFEST_CSV = ARTIFACTS / 'rank_registry' / 'p3_p2_generated_reports_manifest.csv'

BJ = timezone(timedelta(hours=8), name='Asia/Shanghai')


def _rank_num(rank: str) -> str | None:
    m = re.search(r'(\d+)', rank or '')
    return m.group(1) if m else None


def _same_rank_pattern(rank: str) -> re.Pattern[str] | None:
    num = _rank_num(rank)
    if not num:
        return None
    return re.compile(rf'(^|_)rank{num}(?:_|$)', re.IGNORECASE)


def same_rank_reports(rank: str) -> list[Path]:
    pat = _same_rank_pattern(rank)
    if pat is None:
        return []
    out: list[Path] = []
    for d in sorted(SITE_FACTORS.iterdir()):
        if not d.is_dir() or d.name.startswith('rank_registry_p3_p2'):
            continue
        if not pat.search(d.name):
            continue
        rp = d / 'report.html'
        if rp.exists():
            out.append(rp)
    return out


def same_rank_artifact_dirs(rank: str) -> list[Path]:
    pat = _same_rank_pattern(rank)
    if pat is None:
        return []
    out: list[Path] = []
    for d in sorted(ARTIFACTS.iterdir()):
        if d.is_dir() and pat.search(d.name):
            out.append(d)
    return out


def file_stats(d: Path) -> dict[str, int]:
    files = [p for p in d.rglob('*') if p.is_file()]
    return {
        'all': len(files),
        'md': sum(1 for p in files if p.suffix.lower() == '.md'),
        'html': sum(1 for p in files if p.suffix.lower() == '.html'),
        'csv': sum(1 for p in files if p.suffix.lower() == '.csv'),
        'json': sum(1 for p in files if p.suffix.lower() == '.json'),
        'log': sum(1 for p in files if p.suffix.lower() in {'.log', '.txt'}),
    }


def first_md_excerpt(dirs: list[Path], max_chars: int = 1600) -> tuple[str | None, str | None]:
    for d in dirs:
        for md in sorted(d.rglob('*.md')):
            text = md.read_text(encoding='utf-8', errors='ignore').strip()
            if not text:
                continue
            snippet = text[:max_chars]
            return md.relative_to(ROOT).as_posix(), snippet
    return None, None


def _read_json(path: Path) -> dict | list:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return {}


def _fmt_pct(x: float | int | None) -> str:
    if x is None:
        return '-'
    try:
        return f'{float(x) * 100.0:.2f}%'
    except Exception:
        return '-'


def family_hint(mother: str) -> str:
    mother = (mother or '').strip()
    mapping = {
        '均值回复': '核心思想：价格偏离某个“相对公平值”后，倾向于回归；常见风险是趋势单边把回归交易持续压制。',
        '趋势延续': '核心思想：价格/结构已形成方向后，继续沿原方向推进；常见风险是震荡区反复假突破。',
        '波动状态': '核心思想：不同波动或时段状态下，alpha 表现不同；先识别状态，再决定是否交易。',
        '截面选择': '核心思想：在同一时刻比较多个标的，做强弱排序或配对；关键是排序稳定与交易成本可控。',
        '风险过滤': '核心思想：不是制造 entry alpha，而是减少明显差环境下的交易暴露。',
        '其他（跨市场联动）': '核心思想：把外部市场/跨资产信息映射到 crypto 交易决策，重点在可复现链路与时序因果。',
        'deployment layer': '核心思想：作为部署执行层，不应被当作独立 alpha；作用是把上层 alpha 更稳地落地。',
        'exit': '核心思想：作为退出组件，目标是改善收益回撤结构，而非独立制造入场 alpha。',
    }
    return mapping.get(mother, '核心思想：先明确 alpha 本体与过滤/执行层边界，再按可复现证据推进。')


def role_split(role: str) -> tuple[str, str]:
    role_norm = (role or '').strip().lower()
    if '副baseline' in role:
        return '副baseline', '与主 baseline 并行的可部署分支，通常要求更强稳定性证明。'
    if '主baseline' in role:
        return '主baseline', '研究母体，负责定义主 alpha 假设与最小可复现策略骨架。'
    if 'challenger' in role_norm:
        return 'challenger', '挑战/替代 baseline 的候选路线，先追求可解释增量，再看成本后存活。'
    if 'filter' in role_norm:
        return 'filter', '过滤层，控制何时不做或降权，不应伪装成独立 alpha 本体。'
    if 'veto' in role_norm:
        return 'veto', '否决层，在特定坏环境下阻止入场，关注误杀率与漏杀率平衡。'
    if 'exit' in role_norm:
        return 'exit', '退出层，控制持仓寿命与风险释放速度。'
    if 'deployment layer' in role_norm:
        return 'deployment layer', '部署执行层，负责路由/成交/约束，不单独承担 alpha 归因。'
    return role or 'unknown', '先明确该层是 alpha 本体、过滤层还是执行层。'


def render_signal_definition(row: dict[str, str]) -> str:
    mother = (row.get('mother_theme') or '').strip()
    role = (row.get('role') or '').strip()
    baseline = (row.get('challenge_baseline') or '').strip()
    unique_inc = (row.get('unique_increment') or '').strip()

    return f'''
    <ul>
      <li><b>Universe：</b>围绕该 rank 对应的可交易标的集合；优先采用当前在 artifacts/runner 中可复现的标的与时间框架。</li>
      <li><b>Baseline 主信号：</b><code>{escape(baseline or '-')}</code>（若该 rank 不是 baseline，本项为“被挑战或被增强的母体”）。</li>
      <li><b>Rank 独立增量：</b><code>{escape(unique_inc or '-')}</code>，要求在报告中单独说明它改变了 entry / filter / sizing / exit 的哪一段。</li>
      <li><b>策略类型：</b><code>{escape(mother or '-')}</code>，建议按“信号本体 vs 过滤层 vs 执行层”三段写清。</li>
      <li><b>角色归属：</b><code>{escape(role or '-')}</code>，需要明确它是否应独立承担 alpha 归因。</li>
      <li><b>执行信号定义：</b>区分“候选触发点”与“最终执行信号”。候选触发点通过后，仍需经过 veto/filter/执行约束才允许下单。</li>
      <li><b>退出与风险：</b>最少写明超时退出、反向信号退出、极端风险保护三类规则。</li>
      <li><b>成本口径：</b>明确默认费率 + 滑点假设，并写出“成本提高后是否仍存活”的结论。</li>
    </ul>
    '''


def render_decomposition_table(row: dict[str, str]) -> str:
    role_label, role_note = role_split(row.get('role', ''))
    baseline = (row.get('challenge_baseline') or '-').strip() or '-'
    unique_inc = (row.get('unique_increment') or '-').strip() or '-'
    next_action = (row.get('next_action') or '-').strip() or '-'

    rows = [
        ('baseline', baseline, '研究母体（被挑战或被增强对象）'),
        ('rank increment', unique_inc, '该 rank 相比 baseline 的独立增量'),
        (f'role: {role_label}', role_note, '该 rank 在 P2/P3 体系中的职责边界'),
        ('current next_action', next_action, '当前运营决策建议（用于 P2→P3 或回退）'),
    ]

    return ''.join(
        '<tr>'
        f'<td><code>{escape(k)}</code></td>'
        f'<td>{escape(v)}</td>'
        f'<td>{escape(explain)}</td>'
        '</tr>'
        for k, v, explain in rows
    )


def _is_rank201(rank: str) -> bool:
    return (rank or '').strip().lower() == 'rank201'


def render_rank201_report(row: dict[str, str], artifact_dirs: list[Path], sibling_reports: list[Path], generated_at: str) -> str:
    rank = (row.get('rank') or 'rank201').strip() or 'rank201'
    stage = (row.get('stage') or '-').strip() or '-'
    status = (row.get('status') or '-').strip() or '-'
    baseline = (row.get('challenge_baseline') or '-').strip() or '-'
    unique_inc = (row.get('unique_increment') or '-').strip() or '-'
    next_action = (row.get('next_action') or '-').strip() or '-'

    sibling_html = ''.join(
        f"<li><a href='../../{escape(p.relative_to(ROOT / 'reports' / 'site').as_posix())}'>{escape(p.relative_to(ROOT / 'reports' / 'site').as_posix())}</a></li>"
        for p in sibling_reports if p.relative_to(ROOT / 'reports' / 'site').as_posix() != f'factors/{rank}/report.html'
    ) or '<li>暂无</li>'

    artifact_list = ''.join(
        f"<li><code>{escape(d.relative_to(ROOT).as_posix())}</code></li>" for d in artifact_dirs
    ) or '<li>暂无同 rank artifacts 目录</li>'

    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(rank)} · 说明页（审计版）</title>
  <style>
    body {{ font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width: 1100px; margin: 28px auto; padding: 0 16px; line-height: 1.66; color:#0f172a; background:#f8fafc; }}
    .card {{ background:#fff; border:1px solid #e2e8f0; border-radius:12px; padding:14px 16px; margin-bottom:12px; }}
    .muted {{ color:#64748b; }}
    table {{ width:100%; border-collapse:collapse; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e2e8f0; padding:8px 10px; text-align:left; vertical-align:top; }}
    code {{ background:#eff6ff; border-radius:6px; padding:1px 5px; }}
    .pill {{ display:inline-block; border-radius:999px; padding:3px 9px; font-size:12px; background:#e2e8f0; }}
    .alert {{ border:2px solid #dc2626; background:#fef2f2; }}
    .alert h2 {{ margin-top:0; color:#991b1b; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>{escape(rank)} · 说明页（审计版）</h1>
    <p class="muted">生成时间：{escape(generated_at)}。目标：只保留可审计、可复述、可执行口径。</p>
    <p>
      <a href="../rank_registry_p3_p2/report.html">← 返回 P2/P3 总表</a> ｜
      <a href="decomposition.html">本 rank 拆解页</a> ｜
      <a href="review_history.html">研究复盘页（时间线）</a> ｜
      <a href="../rank_registry_p3_p2_entries/{escape(rank)}/report.html">该 rank 的 registry entry</a> ｜
      <a href="../../index.html">站点首页</a>
    </p>
  </div>

  <div class="card alert">
    <h2>⚠ 当前状态：观察线 / 非主研发线</h2>
    <ul>
      <li>保留 runner live（持续产出运行台账）。</li>
      <li>仍归类在 P3，仅因为 runner 处于 live；不是主研发优先级。</li>
      <li>不再作为主赚钱候选，不分配主研究时间。</li>
      <li>不再扩展参数与变体；只做稳定性监控与异常告警。</li>
    </ul>
    <p><b>主入口说明：</b>本 rank 的默认阅读入口是本页 + <a href="review_history.html">研究复盘页</a>；口径以“观察线”执行，不按主研发线推进。</p>
  </div>

  <div class="card">
    <h2>1) 冻结版策略 Spec（先看这一段）</h2>
    <table>
      <thead><tr><th>项</th><th>冻结口径</th><th>证据路径</th></tr></thead>
      <tbody>
        <tr><td>Universe</td><td><code>BTCUSDT, ETHUSDT, SOLUSDT, BNBUSDT, XRPUSDT, DOGEUSDT, ADAUSDT, LINKUSDT</code></td><td><code>reports/artifacts/rank201_5y_validation/README.md</code></td></tr>
        <tr><td>Bar</td><td><code>15m</code></td><td><code>reports/artifacts/rank201_5y_validation/README.md</code></td></tr>
        <tr><td>Long UTC 时段</td><td><code>20:00~21:59 UTC</code></td><td><code>README.md / Strategy frozen for validation</code></td></tr>
        <tr><td>Short UTC 时段</td><td><code>22:00~23:59 UTC</code></td><td><code>README.md / Strategy frozen for validation</code></td></tr>
        <tr><td>Entry / Exit</td><td><code>20:00 开多；22:00 平多并翻空；00:00 平空</code></td><td><code>README.md / Entry/exit rule</code></td></tr>
        <tr><td>Round-trip cost</td><td><code>8 bps</code></td><td><code>README.md / round-trip cost</code></td></tr>
      </tbody>
    </table>
  </div>

  <div class="card">
    <h2>2) Baseline / Increment / Verdict（单页决策账本）</h2>
    <table>
      <thead><tr><th>问题</th><th>答案</th><th>审计备注</th></tr></thead>
      <tbody>
        <tr><td>Baseline 是什么？</td><td><code>{escape(baseline)}</code></td><td>这是被对照的母体，不是本页新增定义。</td></tr>
        <tr><td>Increment 是什么？</td><td><code>{escape(unique_inc)}</code></td><td>唯一增量点，不能再掺其它改动。</td></tr>
        <tr><td>当前 verdict 是什么？</td><td><code>{escape(stage)} / {escape(status)}</code>（解释：observe_only=仅观察运行，不属于主研发推进）</td><td>状态沿用 registry 当前口径。</td></tr>
        <tr><td>为什么 5Y 全负仍保留 runner？</td><td><ul><li>5Y 冻结验证显示该 exact schedule 长期不稳，不能当“普适长期 alpha”。</li><li>保留 runner 只是为了低成本连续观测与异常告警，不是扩投入/加仓/升级结论。</li><li>因此它被降级为观察线：不做主赚钱候选、不分配主研究时间、不扩参数/变体。</li></ul></td><td>见 <code>rank201_5y_validation/README.md</code> 与当前 next action 口径。</td></tr>
      </tbody>
    </table>
  </div>

  <div class="card">
    <h2>3) 5Y 冻结验证快照（不加新研究）</h2>
    <table>
      <thead><tr><th>指标</th><th>值</th><th>来源</th></tr></thead>
      <tbody>
        <tr><td>Lifetime total return</td><td><code>-91.61%</code></td><td><code>rank201_5y_validation/README.md</code></td></tr>
        <tr><td>Max drawdown</td><td><code>-93.67%</code></td><td><code>rank201_5y_validation/README.md</code></td></tr>
        <tr><td>Positive months</td><td><code>17 / 60 (28.33%)</code></td><td><code>rank201_5y_validation/README.md</code></td></tr>
        <tr><td>Yearly returns</td><td><code>2021:-3.92%, 2022:-25.14%, 2023:-67.23%, 2024:-28.85%, 2025:-49.37%, 2026YTD:-1.20%</code></td><td><code>rank201_5y_validation/README.md</code></td></tr>
      </tbody>
    </table>
  </div>

  <div class="card">
    <h2>4) 当前唯一下一步动作（执行口径）</h2>
    <p><b>唯一动作：</b><code>{escape(next_action)}</code></p>
    <ul>
      <li>保持 <code>momentum-rank201-paper-refresh.timer</code> 与 runner 在线。</li>
      <li>只做稳定性监控和异常告警；不改参数、不加新规则、不重写结论。</li>
      <li>不再分配主研究时间，不再扩展参数与变体，不作为主赚钱候选。</li>
      <li>若后续决定下线 runner，则同步迁出 P3 运行态（转入非 live 队列）。</li>
      <li>任何“升级为长期可部署 alpha”的主张，必须先有新的验证证据页，不在本页内外推。</li>
    </ul>
    <p class="muted">1 句话复述模板：Rank201 的 frozen schedule 在 5Y 不成立，当前是 observe_only（观察线），仅保留 runner 监控，不作为主研发线。</p>
  </div>

  <div class="card">
    <h2>5) 关联页面 / 证据目录</h2>
    <p><b>主入口说明：</b>默认从本页开始，先读“观察线状态”，再看 <code>review_history.html</code>；不要把 rank201 当主研发线。</p>
    <p><b>快速入口</b></p>
    <ul>
      <li><a href="review_history.html">Rank201 研究复盘页（本次“发生了什么”时间线）</a></li>
      <li><a href="decomposition.html">拆解页（baseline / increment / verdict）</a></li>
    </ul>
    <p><b>同 rank 其它 factors 报告入口</b></p>
    <ul>{sibling_html}</ul>
    <p><b>Artifacts 目录</b></p>
    <ul>{artifact_list}</ul>
  </div>
</body>
</html>
'''


def render_rank201_decomposition(row: dict[str, str], artifact_dirs: list[Path], generated_at: str) -> str:
    rank = (row.get('rank') or 'rank201').strip() or 'rank201'
    stage = (row.get('stage') or '-').strip() or '-'
    status = (row.get('status') or '-').strip() or '-'
    baseline = (row.get('challenge_baseline') or '-').strip() or '-'
    unique_inc = (row.get('unique_increment') or '-').strip() or '-'
    next_action = (row.get('next_action') or '-').strip() or '-'

    md_path, md_excerpt = first_md_excerpt(artifact_dirs, max_chars=2200)
    evidence = (
        f"<p><b>证据摘录：</b><code>{escape(md_path or '-')}</code></p><pre>{escape(md_excerpt or '')}</pre>"
        if md_path and md_excerpt else
        "<p class='muted'>暂无同 rank 证据摘录。</p>"
    )

    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(rank)} · decomposition（审计版）</title>
  <style>
    body {{ font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width: 1040px; margin: 28px auto; padding: 0 16px; line-height: 1.68; color:#0f172a; background:#f8fafc; }}
    .card {{ background:#fff; border:1px solid #e2e8f0; border-radius:12px; padding:14px 16px; margin-bottom:12px; }}
    .muted {{ color:#64748b; }}
    table {{ width:100%; border-collapse:collapse; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e2e8f0; padding:8px 10px; text-align:left; vertical-align:top; }}
    code {{ background:#eff6ff; border-radius:6px; padding:1px 5px; }}
    pre {{ white-space:pre-wrap; background:#0b1220; color:#dbeafe; border-radius:10px; padding:10px; font-size:12px; }}
    .alert {{ border:2px solid #dc2626; background:#fef2f2; }}
    .alert h2 {{ margin-top:0; color:#991b1b; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>{escape(rank)} · decomposition（审计版）</h1>
    <p class="muted">生成时间：{escape(generated_at)}。目标：把 baseline / increment / 决策口径拆到可复述和可执行。</p>
    <p><a href="report.html">← 返回该 rank 说明页</a> ｜ <a href="review_history.html">研究复盘页（时间线）</a> ｜ <a href="../rank_registry_p3_p2/report.html">P3/P2 总表</a></p>
  </div>

  <div class="card alert">
    <h2>⚠ 当前状态：观察线 / 非主研发线</h2>
    <ul>
      <li>runner 保持在线，只做监控。</li>
      <li>仍归类在 P3，仅因为 runner 处于 live；不是主研发优先级。</li>
      <li>不再作为主赚钱候选，不分配主研究时间。</li>
      <li>不再扩参数和变体，不再开主研发分支。</li>
    </ul>
  </div>

  <div class="card">
    <h2>1) 冻结版策略 Spec（固定，不外推）</h2>
    <table>
      <thead><tr><th>项</th><th>冻结定义</th></tr></thead>
      <tbody>
        <tr><td>Universe</td><td><code>BTCUSDT, ETHUSDT, SOLUSDT, BNBUSDT, XRPUSDT, DOGEUSDT, ADAUSDT, LINKUSDT</code></td></tr>
        <tr><td>Bar</td><td><code>15m</code></td></tr>
        <tr><td>Long UTC 时段</td><td><code>20:00~21:59 UTC</code></td></tr>
        <tr><td>Short UTC 时段</td><td><code>22:00~23:59 UTC</code></td></tr>
        <tr><td>Entry/Exit</td><td><code>20:00 开多；22:00 平多并翻空；00:00 平空</code></td></tr>
        <tr><td>Cost</td><td><code>8 bps round-trip</code></td></tr>
      </tbody>
    </table>
  </div>

  <div class="card">
    <h2>2) baseline / increment / ablation 拆解</h2>
    <table>
      <thead><tr><th>模块</th><th>定义</th><th>执行约束</th></tr></thead>
      <tbody>
        <tr><td><code>baseline</code></td><td>{escape(baseline)}</td><td>作为对照母体，不与其它改动混测。</td></tr>
        <tr><td><code>increment</code></td><td>{escape(unique_inc)}</td><td>只允许“UTC 时段切换”这一处增量。</td></tr>
        <tr><td><code>ablation A</code></td><td><code>baseline only</code></td><td>不加 increment，不加额外过滤。</td></tr>
        <tr><td><code>ablation B</code></td><td><code>baseline + increment</code></td><td>仅新增 increment，验证增量贡献方向。</td></tr>
        <tr><td><code>ablation C</code></td><td><code>baseline + increment + cost stress</code></td><td>固定 8 bps，并记录费率上调后的存活性。</td></tr>
      </tbody>
    </table>
  </div>

  <div class="card">
    <h2>3) 当前 verdict 与观察线解释</h2>
    <table>
      <thead><tr><th>项</th><th>当前口径</th></tr></thead>
      <tbody>
        <tr><td>Verdict</td><td><code>{escape(stage)} / {escape(status)}</code></td></tr>
        <tr><td>5Y 结论</td><td>冻结 schedule 在 5Y 重叠窗口整体为负，不满足“长期稳定规律”。</td></tr>
        <tr><td>为何仍保留 runner</td><td>observe_only 仅用于维持在线观测与监控链路；不表示通过长期有效性验证，也不代表扩投入结论。</td></tr>
        <tr><td>决策边界</td><td>在无新增验证前，不把该 schedule 描述为“可长期部署 alpha”。</td></tr>
      </tbody>
    </table>
  </div>

  <div class="card">
    <h2>4) 当前唯一下一步动作（SOP）</h2>
    <p><b>唯一动作：</b><code>{escape(next_action)}</code></p>
    <ol>
      <li>确认 runner 与 timer 持续在线。</li>
      <li>只监控：是否断更、是否异常跳变、是否告警触发。</li>
      <li>如无异常，不改参数、不新增研究分支、不改 verdict。</li>
      <li>默认不分配主研究时间，不再扩展参数与变体。</li>
      <li>若决定下线 runner，则同步迁出 P3 运行态（转入非 live 队列）。</li>
    </ol>
  </div>

  <div class="card">
    <h2>5) 现有证据摘录</h2>
    {evidence}
  </div>
</body>
</html>
'''


def render_rank201_review_history(row: dict[str, str], generated_at: str) -> str:
    rank = (row.get('rank') or 'rank201').strip() or 'rank201'
    stage = (row.get('stage') or '-').strip() or '-'
    status = (row.get('status') or '-').strip() or '-'
    next_action = (row.get('next_action') or '-').strip() or '-'

    summary_5y = _read_json(ARTIFACTS / 'rank201_5y_validation' / 'rank201_5y_summary.json')
    live_state = _read_json(ARTIFACTS / 'paper_rank201_utc_clock_low_switch' / 'rank201_state.json')
    cross_summary = _read_json(ARTIFACTS / 'cross_market_clock_scan' / 'cross_market_clock_summary.json')

    def _list_item(symbol: str) -> dict:
        if isinstance(cross_summary, list):
            for item in cross_summary:
                if str(item.get('symbol', '')).upper() == symbol.upper():
                    return item
        return {}

    def _combined(symbol: str) -> str:
        item = _list_item(symbol)
        return _fmt_pct(item.get('combined_test_total_return'))

    fivey_return = _fmt_pct(summary_5y.get('lifetime_total_return') if isinstance(summary_5y, dict) else None)
    fivey_mdd = _fmt_pct(summary_5y.get('max_drawdown') if isinstance(summary_5y, dict) else None)
    fivey_pos_months = '-'
    if isinstance(summary_5y, dict):
        pm = summary_5y.get('positive_months')
        tm = summary_5y.get('total_months')
        if pm is not None and tm is not None:
            fivey_pos_months = f'{pm}/{tm}'

    live_lifetime = _fmt_pct(live_state.get('lifetime_total_return') if isinstance(live_state, dict) else None)
    live_30d = _fmt_pct(live_state.get('recent_30d_total_return') if isinstance(live_state, dict) else None)
    live_closed = str(live_state.get('closed_trades', '-')) if isinstance(live_state, dict) else '-'
    live_last_run = str(live_state.get('last_run_at_utc', '-')) if isinstance(live_state, dict) else '-'

    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(rank)} · 研究复盘（发生了什么）</title>
  <style>
    body {{ font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width: 1100px; margin: 28px auto; padding: 0 16px; line-height: 1.66; color:#0f172a; background:#f8fafc; }}
    .card {{ background:#fff; border:1px solid #e2e8f0; border-radius:12px; padding:14px 16px; margin-bottom:12px; }}
    .muted {{ color:#64748b; }}
    table {{ width:100%; border-collapse:collapse; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e2e8f0; padding:8px 10px; text-align:left; vertical-align:top; }}
    code {{ background:#eff6ff; border-radius:6px; padding:1px 5px; }}
    .ok {{ color:#166534; font-weight:600; }}
    .bad {{ color:#991b1b; font-weight:600; }}
    .alert {{ border:2px solid #dc2626; background:#fef2f2; }}
    .alert h2 {{ margin-top:0; color:#991b1b; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>{escape(rank)} · 研究复盘（发生了什么）</h1>
    <p class="muted">生成时间：{escape(generated_at)}。用途：给“我们之前到底做了什么、为什么结论变了”一个可审计时间线。</p>
    <p>
      <a href="report.html">← 返回说明页</a> ｜
      <a href="decomposition.html">拆解页</a> ｜
      <a href="../rank_registry_p3_p2/report.html">P3/P2 总表</a>
    </p>
  </div>

  <div class="card alert">
    <h2>⚠ 当前状态：观察线 / 非主研发线</h2>
    <ul>
      <li>runner 继续在线（用于监控，不用于主研发推进）。</li>
      <li>仍归类在 P3，仅因为 runner 处于 live；不是主研发优先级。</li>
      <li>不作为主赚钱候选，不分配主研究时间。</li>
      <li>不再扩展参数与变体，除非先有新的审计证据触发重开。</li>
    </ul>
  </div>

  <div class="card">
    <h2>一句话结论（人话）</h2>
    <p>Rank201 一开始在<strong>最近几个月</strong>看起来不错，所以被推进到 P3 并接了 paper runner；但后面做了<strong>更长历史 + 固定口径</strong>审计后，发现 5 年整体很差、稳定性不够，所以现在的口径变成：<span class="bad">观察线（observe_only），非主研发线</span>。</p>
  </div>

  <div class="card">
    <h2>我们到底做了什么（时间线）</h2>
    <table>
      <thead><tr><th>时间（UTC）</th><th>做了什么</th><th>当时结论</th><th>证据</th></tr></thead>
      <tbody>
        <tr>
          <td>2026-03-27 19:48</td>
          <td>首次 intake，确认是可执行的时钟策略候选（20~21 多 / 22~23 空）。</td>
          <td><code>keep_P1</code></td>
          <td><code>research/optimization_loop/2026-03-27_1948_rank201_utc_clock_seasonality_intake_keep_p1.md</code></td>
        </tr>
        <tr>
          <td>2026-03-27 20:15</td>
          <td>做 15m 可执行迁移检查（8 币组合，近期样本）。</td>
          <td><code>promote_P2</code></td>
          <td><code>research/optimization_loop/2026-03-27_2015_rank201_survivor_followup_promote_p2.md</code></td>
        </tr>
        <tr>
          <td>2026-03-27 21:58</td>
          <td>补 admission 检查（成本梯度、邻近 pocket、跨资产）。</td>
          <td><code>promote_P3</code></td>
          <td><code>research/optimization_loop/2026-03-27_2158_rank201_p2_admission_promote_p3.md</code></td>
        </tr>
        <tr>
          <td>2026-03-27 22:16</td>
          <td>真正接线：runner + systemd timer + 首跑验证。</td>
          <td><code>connected_runner_live</code></td>
          <td><code>research/optimization_loop/2026-03-27_2216_rank201_p3_launch_wiring_connected_runner_live.md</code></td>
        </tr>
        <tr>
          <td>2026-04-01 04:23</td>
          <td>做冻结版 5Y 审计回测（公共重叠窗口 + 8 币统一规则）。</td>
          <td><span class="bad">5Y 不稳定（全局偏负）</span></td>
          <td><code>reports/artifacts/rank201_5y_validation/README.md</code></td>
        </tr>
        <tr>
          <td>2026-04-01 05:16</td>
          <td>策略评审收口：不再当高优先 deploy 候选。</td>
          <td><span class="bad">deprioritized（保留 clock-family 研究意义）</span></td>
          <td><code>research/strategy_review/2026-04-01_0516_rank201_deprioritized_note.md</code></td>
        </tr>
        <tr>
          <td>2026-04-11</td>
          <td>正式降级为观察线/非主研发线；保留 runner live，但停止主线研发投入。</td>
          <td><span class="bad">observe_only（非主研发）</span></td>
          <td><code>reports/artifacts/rank_registry/full_rank_p3_p2_table.csv</code></td>
        </tr>
      </tbody>
    </table>
  </div>

  <div class="card">
    <h2>关键数字：为什么会“先好看，后打脸”</h2>
    <table>
      <thead><tr><th>视角</th><th>结果</th><th>解释</th></tr></thead>
      <tbody>
        <tr>
          <td>近期样本（当时推进用）</td>
          <td class="ok">2026-01~03 的 15m 可执行检查在 4bps 单边下为正（历史记录约 +18.8%）</td>
          <td>说明它在某个最近 pocket 里确实能跑，不是纯噪音。</td>
        </tr>
        <tr>
          <td>5Y 冻结审计（后续补做）</td>
          <td class="bad">总收益 {escape(fivey_return)}，最大回撤 {escape(fivey_mdd)}，正月占比 {escape(fivey_pos_months)}</td>
          <td>说明同一套固定 schedule 拉长后不稳，不能当“长期通用规律”。</td>
        </tr>
        <tr>
          <td>分币种结果（5Y）</td>
          <td class="bad">8 个币总收益都为负（见 5Y README）</td>
          <td>不是“个别币拖后腿”，而是整体结构失效。</td>
        </tr>
        <tr>
          <td>当前 runner 运行态</td>
          <td>lifetime {escape(live_lifetime)} ｜ recent 30d {escape(live_30d)} ｜ closed trades {escape(live_closed)}</td>
          <td>最近仍可能有正段落，但这不等于通过了长期稳定性审计。</td>
        </tr>
      </tbody>
    </table>
    <p class="muted">当前状态快照时间：{escape(live_last_run)}</p>
  </div>

  <div class="card">
    <h2>我们还做了“换市场/换标的”的旁证吗？</h2>
    <p>做过一轮跨市场时钟扫描（US/HK/Gold，Yahoo 60m 约 730d）。结论是：<b>时钟效应在别的市场也存在</b>，但并不支持“把 Rank201 的固定 UTC 时段原样抄过去就通吃”。</p>
    <table>
      <thead><tr><th>市场样本</th><th>组合 test 回报（scan）</th><th>备注</th></tr></thead>
      <tbody>
        <tr><td>QQQ</td><td>{escape(_combined('QQQ'))}</td><td>弱</td></tr>
        <tr><td>SPY</td><td>{escape(_combined('SPY'))}</td><td>弱</td></tr>
        <tr><td>GLD</td><td>{escape(_combined('GLD'))}</td><td>一般</td></tr>
        <tr><td>GC=F</td><td>{escape(_combined('GC=F'))}</td><td>偏弱</td></tr>
        <tr><td>2800.HK</td><td>{escape(_combined('2800.HK'))}</td><td>相对更好</td></tr>
        <tr><td>3033.HK</td><td>{escape(_combined('3033.HK'))}</td><td>相对更好</td></tr>
        <tr><td>0700.HK</td><td>{escape(_combined('0700.HK'))}</td><td>相对更好</td></tr>
      </tbody>
    </table>
    <p class="muted">证据：<code>reports/artifacts/cross_market_clock_scan/README.md</code> + <code>cross_market_clock_summary.json</code></p>
  </div>

  <div class="card">
    <h2>现在到底是什么状态？</h2>
    <p><b>策略状态：</b><code>{escape(stage)} / {escape(status)}</code></p>
    <p><b>唯一动作：</b><code>{escape(next_action)}</code></p>
    <ul>
      <li>保留 runner，持续观察近期表现和异常。</li>
      <li>不把它当作“已证明长期稳定”的策略去扩投入。</li>
      <li>不分配主研究时间，不扩参数与变体，不作为主赚钱候选。</li>
      <li>后续如果要翻案，必须先拿出新的可审计验证页（不是口头感觉）。</li>
    </ul>
  </div>
</body>
</html>
'''


def render_report(row: dict[str, str], artifact_dirs: list[Path], sibling_reports: list[Path], generated_at: str) -> str:
    rank = (row.get('rank') or '-').strip() or '-'
    if _is_rank201(rank):
        return render_rank201_report(row, artifact_dirs, sibling_reports, generated_at)
    stage = (row.get('stage') or '-').strip() or '-'
    status = (row.get('status') or '-').strip() or '-'
    mother = (row.get('mother_theme') or '-').strip() or '-'
    role = (row.get('role') or '-').strip() or '-'
    baseline = (row.get('challenge_baseline') or '-').strip() or '-'
    unique_inc = (row.get('unique_increment') or '-').strip() or '-'
    next_action = (row.get('next_action') or '-').strip() or '-'

    stats_rows: list[str] = []
    for d in artifact_dirs:
        s = file_stats(d)
        stats_rows.append(
            '<tr>'
            f'<td><code>{escape(d.name)}</code></td>'
            f'<td>{s["all"]}</td><td>{s["md"]}</td><td>{s["csv"]}</td><td>{s["json"]}</td><td>{s["html"]}</td><td>{s["log"]}</td>'
            '</tr>'
        )
    stats_html = ''.join(stats_rows) if stats_rows else '<tr><td colspan="7">暂无同 rank artifacts 目录</td></tr>'

    md_path, md_excerpt = first_md_excerpt(artifact_dirs)
    md_block = (
        f"<p><b>已发现可复用 MD：</b><code>{escape(md_path or '-')}</code></p>"
        f"<pre>{escape(md_excerpt or '')}</pre>"
    ) if md_path and md_excerpt else "<p class='muted'>当前未发现同 rank 的现成 MD 说明，优先采用数据摘要模板并在后续补完信号定义细节。</p>"

    artifact_list = ''.join(
        f"<li><code>{escape(d.relative_to(ROOT).as_posix())}</code></li>" for d in artifact_dirs
    ) or '<li>暂无同 rank artifacts 目录</li>'

    sibling_html = ''.join(
        f"<li><a href='../../{escape(p.relative_to(ROOT / 'reports' / 'site').as_posix())}'>{escape(p.relative_to(ROOT / 'reports' / 'site').as_posix())}</a></li>"
        for p in sibling_reports if p.relative_to(ROOT / 'reports' / 'site').as_posix() != f'factors/{rank}/report.html'
    ) or '<li>暂无</li>'

    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(rank)} · 独立策略报告（P2/P3）</title>
  <style>
    body {{ font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width: 1100px; margin: 28px auto; padding: 0 16px; line-height: 1.66; color:#0f172a; background:#f8fafc; }}
    .card {{ background:#fff; border:1px solid #e2e8f0; border-radius:12px; padding:14px 16px; margin-bottom:12px; }}
    .muted {{ color:#64748b; }}
    table {{ width:100%; border-collapse:collapse; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e2e8f0; padding:8px 10px; text-align:left; vertical-align:top; }}
    pre {{ white-space:pre-wrap; background:#0b1220; color:#dbeafe; border-radius:10px; padding:10px; font-size:12px; }}
    code {{ background:#eff6ff; border-radius:6px; padding:1px 5px; }}
    .pill {{ display:inline-block; border-radius:999px; padding:3px 9px; font-size:12px; background:#e2e8f0; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:12px; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>{escape(rank)} · 独立策略报告（P2/P3）</h1>
    <p class="muted">本页由任务链自动生成（15m cadence / 双页结构），用于保证 P2/P3 rank 在 factors 目录有独立报告入口。生成时间：{escape(generated_at)}</p>
    <p>
      <a href="../rank_registry_p3_p2/report.html">← 返回 P2/P3 总表</a> ｜
      <a href="decomposition.html">本 rank 拆解页</a> ｜
      <a href="../rank_registry_p3_p2_entries/{escape(rank)}/report.html">该 rank 的 registry entry</a> ｜
      <a href="../../index.html">站点首页</a>
    </p>
  </div>

  <div class="card">
    <h2>策略定位</h2>
    <p><b>stage：</b>{escape(stage)} ｜ <b>status：</b><span class="pill">{escape(status)}</span></p>
    <p><b>策略类型（mother theme）：</b>{escape(mother)}</p>
    <p><b>角色（role）：</b>{escape(role)}</p>
    <p><b>挑战基线（challenge baseline）：</b>{escape(baseline)}</p>
    <p><b>唯一增量（unique increment）：</b>{escape(unique_inc)}</p>
    <p><b>下一步唯一动作（next action）：</b>{escape(next_action)}</p>
  </div>

  <div class="card">
    <h2>研究结果与原理（人话版）</h2>
    <p>{escape(family_hint(mother))}</p>
    <p class="muted">当前 rank 要回答的核心问题：这条“独立增量”到底是在补 baseline 的哪个短板（入场、过滤、仓位、退出、执行）？</p>
    <div class="grid">
      <div>
        <h3>拆分视角</h3>
        <table>
          <thead><tr><th>层</th><th>内容</th><th>说明</th></tr></thead>
          <tbody>{render_decomposition_table(row)}</tbody>
        </table>
      </div>
      <div>
        <h3>信号定义（落地模板）</h3>
        {render_signal_definition(row)}
      </div>
    </div>
  </div>

  <div class="card">
    <h2>同 rank 其它 factors 报告入口</h2>
    <ul>{sibling_html}</ul>
  </div>

  <div class="card">
    <h2>Artifacts 证据目录（同 rank）</h2>
    <ul>{artifact_list}</ul>
    <table>
      <thead><tr><th>artifacts 目录</th><th>总文件</th><th>md</th><th>csv</th><th>json</th><th>html</th><th>log/txt</th></tr></thead>
      <tbody>{stats_html}</tbody>
    </table>
  </div>

  <div class="card">
    <h2>可复用说明文档（如有）</h2>
    {md_block}
  </div>
</body>
</html>
'''


def render_decomposition(row: dict[str, str], artifact_dirs: list[Path], generated_at: str) -> str:
    rank = (row.get('rank') or '-').strip() or '-'
    if _is_rank201(rank):
        return render_rank201_decomposition(row, artifact_dirs, generated_at)
    stage = (row.get('stage') or '-').strip() or '-'
    status = (row.get('status') or '-').strip() or '-'
    mother = (row.get('mother_theme') or '-').strip() or '-'
    role = (row.get('role') or '-').strip() or '-'
    baseline = (row.get('challenge_baseline') or '-').strip() or '-'
    unique_inc = (row.get('unique_increment') or '-').strip() or '-'
    next_action = (row.get('next_action') or '-').strip() or '-'

    md_path, md_excerpt = first_md_excerpt(artifact_dirs, max_chars=2200)
    evidence = (
        f"<p><b>证据摘要来源：</b><code>{escape(md_path or '-')}</code></p><pre>{escape(md_excerpt or '')}</pre>"
        if md_path and md_excerpt else
        "<p class='muted'>当前暂无可直接复用的同 rank 说明文档；建议下一轮补一份最小可复现 spec（含 entry/exit/cost）。</p>"
    )

    role_label, role_note = role_split(role)

    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(rank)} · decomposition（baseline / components / ablation）</title>
  <style>
    body {{ font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width: 1040px; margin: 28px auto; padding: 0 16px; line-height: 1.68; color:#0f172a; background:#f8fafc; }}
    .card {{ background:#fff; border:1px solid #e2e8f0; border-radius:12px; padding:14px 16px; margin-bottom:12px; }}
    .muted {{ color:#64748b; }}
    table {{ width:100%; border-collapse:collapse; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e2e8f0; padding:8px 10px; text-align:left; vertical-align:top; }}
    code {{ background:#eff6ff; border-radius:6px; padding:1px 5px; }}
    pre {{ white-space:pre-wrap; background:#0b1220; color:#dbeafe; border-radius:10px; padding:10px; font-size:12px; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>{escape(rank)} · decomposition（baseline / components / ablation）</h1>
    <p class="muted">生成时间：{escape(generated_at)}。本页服务于“把 P2/P3 策略拆到可执行组件”的需求。</p>
    <p><a href="report.html">← 返回该 rank 主报告</a> ｜ <a href="../rank_registry_p3_p2/report.html">P3/P2 总表</a></p>
  </div>

  <div class="card">
    <h2>一、baseline / components / ablation 拆分</h2>
    <table>
      <thead><tr><th>模块</th><th>定义</th><th>为什么需要</th></tr></thead>
      <tbody>
        <tr><td><code>baseline</code></td><td>{escape(baseline)}</td><td>提供主 alpha 假设与对照面。</td></tr>
        <tr><td><code>increment</code></td><td>{escape(unique_inc)}</td><td>该 rank 相比 baseline 的独立改动点。</td></tr>
        <tr><td><code>role</code></td><td>{escape(role_label)}</td><td>{escape(role_note)}</td></tr>
        <tr><td><code>stage/status</code></td><td>{escape(stage)} / {escape(status)}</td><td>决定当前是继续推进、观测，还是归档/降级。</td></tr>
      </tbody>
    </table>
  </div>

  <div class="card">
    <h2>二、信号定义（具体口径）</h2>
    <p><b>策略类型：</b>{escape(mother)}</p>
    <ol>
      <li><b>输入层（Input）</b>：价格/成交/跨资产数据，要求明确频率与对齐时点。</li>
      <li><b>候选触发层（Candidate Trigger）</b>：先给出“触发候选”的条件，不直接等同于下单。</li>
      <li><b>过滤/否决层（Filter/Veto）</b>：说明哪些条件会阻止候选触发变成真实交易。</li>
      <li><b>执行层（Execution Signal）</b>：给出最终下单定义（方向、仓位、并发约束、冷却时间）。</li>
      <li><b>退出层（Exit）</b>：至少覆盖止损、止盈、超时退出与异常风控保护。</li>
      <li><b>成本层（Cost）</b>：固定费率/滑点假设 + 敏感性结论（费率上升后是否仍成立）。</li>
    </ol>
    <p class="muted">简化记忆法：候选信号 ≠ 真实执行信号；只有通过过滤与执行约束后，才是可归因交易。</p>
  </div>

  <div class="card">
    <h2>三、ablation 建议</h2>
    <ul>
      <li>先测 <code>baseline only</code>（无增量、无额外过滤）。</li>
      <li>再测 <code>baseline + increment</code>（只加该 rank 独立增量）。</li>
      <li>再测 <code>baseline + increment + filter/veto</code>（看收益与回撤是否同步改善）。</li>
      <li>最后做 <code>cost stress</code>（费率/滑点提高后的存活性）。</li>
    </ul>
    <p><b>当前下一步：</b>{escape(next_action)}</p>
  </div>

  <div class="card">
    <h2>四、现有证据摘录</h2>
    {evidence}
  </div>
</body>
</html>
'''


def read_registry_rows() -> list[dict[str, str]]:
    if not REGISTRY_CSV.exists():
        raise FileNotFoundError(REGISTRY_CSV)
    rows = list(csv.DictReader(REGISTRY_CSV.open('r', encoding='utf-8')))
    return rows


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description='Build dedicated P2/P3 rank reports (+ decomposition pages).')
    p.add_argument('--rank', default='', help='Only build one rank (e.g., rank201). Empty means build all rows.')
    return p.parse_args()


def main() -> int:
    args = parse_args()
    rows = read_registry_rows()
    generated_at = datetime.now(timezone.utc).astimezone(BJ).strftime('%Y-%m-%d %H:%M:%S 北京时间')

    target = args.rank.strip().lower()
    if target:
        filtered = [r for r in rows if (r.get('rank') or '').strip().lower() == target]
        if not filtered:
            raise SystemExit(f'[error] rank not found in registry csv: {args.rank}')
        rows = filtered

    existing_manifest: dict[str, dict[str, str]] = {}
    if MANIFEST_CSV.exists():
        for r in csv.DictReader(MANIFEST_CSV.open('r', encoding='utf-8')):
            rank = (r.get('rank') or '').strip()
            if rank:
                existing_manifest[rank] = r

    processed = 0
    for row in rows:
        rank = (row.get('rank') or '').strip()
        if not rank:
            continue

        out_dir = SITE_FACTORS / rank
        out_dir.mkdir(parents=True, exist_ok=True)
        out_report = out_dir / 'report.html'
        out_decomposition = out_dir / 'decomposition.html'

        artifact_dirs = same_rank_artifact_dirs(rank)
        sibling_reports = same_rank_reports(rank)

        out_report.write_text(render_report(row, artifact_dirs, sibling_reports, generated_at), encoding='utf-8')
        out_decomposition.write_text(render_decomposition(row, artifact_dirs, generated_at), encoding='utf-8')
        if _is_rank201(rank):
            out_review = out_dir / 'review_history.html'
            out_review.write_text(render_rank201_review_history(row, generated_at), encoding='utf-8')

        existing_manifest[rank] = {
            'rank': rank,
            'stage': row.get('stage', ''),
            'status': row.get('status', ''),
            'output_report': out_report.relative_to(ROOT / 'reports' / 'site').as_posix(),
            'output_decomposition': out_decomposition.relative_to(ROOT / 'reports' / 'site').as_posix(),
            'mode': 'generated_from_registry_dual_page',
            'generated_at': generated_at,
        }
        processed += 1

    all_rows = read_registry_rows()
    sorted_ranks: list[str] = []
    for r in all_rows:
        rank = (r.get('rank') or '').strip()
        if rank and rank not in sorted_ranks:
            sorted_ranks.append(rank)
    for rank in sorted(existing_manifest.keys()):
        if rank not in sorted_ranks:
            sorted_ranks.append(rank)

    MANIFEST_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ['rank', 'stage', 'status', 'output_report', 'output_decomposition', 'mode', 'generated_at']
    with MANIFEST_CSV.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for rank in sorted_ranks:
            rec = existing_manifest.get(rank)
            if not rec:
                continue
            w.writerow({k: rec.get(k, '') for k in fieldnames})

    print({
        'processed': processed,
        'rank_filter': target or 'ALL',
        'manifest': str(MANIFEST_CSV),
    })
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
