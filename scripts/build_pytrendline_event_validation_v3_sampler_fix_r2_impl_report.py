#!/usr/bin/env python3
from __future__ import annotations

import json
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "scripts" / "build_pytrendline_event_validation_v3_report.py"
ART = ROOT / "reports" / "artifacts" / "pytrendline_event_validation_v3_sampler_fix_r2_impl"
SITE = ROOT / "reports" / "site" / "factors" / "pytrendline_event_validation_v3_sampler_fix_r2_impl"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def render_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "<p><em>empty</em></p>"
    return df.to_html(index=False, classes="tbl", border=0)


def find_line(lines: list[str], needle: str) -> int | None:
    for i, line in enumerate(lines, start=1):
        if needle in line:
            return i
    return None


def snippet(lines: list[str], center: int | None, radius: int = 3) -> str:
    if center is None:
        return "not found"
    start = max(1, center - radius)
    end = min(len(lines), center + radius)
    body = []
    for i in range(start, end + 1):
        body.append(f"{i:04d}: {lines[i-1]}")
    return "\n".join(body)


def main() -> None:
    ensure_dir(ART)
    ensure_dir(SITE)

    lines = SRC.read_text(encoding="utf-8").splitlines()
    support_gate = "if breakout_raw and (lv_t > h):"
    resistance_gate = "if breakout_raw and (lv_t < l):"

    support_line = find_line(lines, support_gate)
    resistance_line = find_line(lines, resistance_gate)

    def branch_flags(gate_line: int | None) -> dict[str, int | None]:
        if gate_line is None:
            return {"raw": None, "confirm_1": None, "confirm_2": None}
        branch = lines[gate_line - 1 : min(len(lines), gate_line + 5)]
        raw_line = find_line(branch, "breakout_raw = False")
        c1_line = find_line(branch, "breakout_confirm_1 = False")
        c2_line = find_line(branch, "breakout_confirm_2 = False")
        return {
            "raw": gate_line + raw_line - 1 if raw_line else None,
            "confirm_1": gate_line + c1_line - 1 if c1_line else None,
            "confirm_2": gate_line + c2_line - 1 if c2_line else None,
        }

    support_flags = branch_flags(support_line)
    resistance_flags = branch_flags(resistance_line)

    checks = pd.DataFrame(
        [
            {
                "check_id": "R2-support-gate",
                "status": "present" if support_line else "missing",
                "line": support_line,
                "what_it_checks": "support breakout rows are dropped when line_value_event > event_high",
                "reliability": "high for source-code presence",
            },
            {
                "check_id": "R2-resistance-gate",
                "status": "present" if resistance_line else "missing",
                "line": resistance_line,
                "what_it_checks": "resistance breakout rows are dropped when line_value_event < event_low",
                "reliability": "high for source-code presence",
            },
            {
                "check_id": "R2-support-resets",
                "status": "present" if all(support_flags.values()) else "missing",
                "line": support_flags["raw"],
                "what_it_checks": "support wrong-side gate zeroes raw / confirm_1 / confirm_2 breakout flags",
                "reliability": "high for source-code presence",
            },
            {
                "check_id": "R2-resistance-resets",
                "status": "present" if all(resistance_flags.values()) else "missing",
                "line": resistance_flags["raw"],
                "what_it_checks": "resistance wrong-side gate zeroes raw / confirm_1 / confirm_2 breakout flags",
                "reliability": "high for source-code presence",
            },
        ]
    )
    checks.to_csv(ART / "implementation_checks.csv", index=False)

    support_snippet = snippet(lines, support_line)
    resistance_snippet = snippet(lines, resistance_line)
    (ART / "support_gate_snippet.txt").write_text(support_snippet + "\n", encoding="utf-8")
    (ART / "resistance_gate_snippet.txt").write_text(resistance_snippet + "\n", encoding="utf-8")

    implemented = bool(support_line and resistance_line and all(support_flags.values()) and all(resistance_flags.values()))
    summary = {
        "title": "PyTrendline V3 sampler fix R2 implementation note",
        "todo_item": "V3X-A / A4-b2",
        "implemented": implemented,
        "finding": "The v3 sampler source now contains explicit event-time strict wrong-side breakout gates for both support and resistance branches.",
        "found": [
            "support branch now drops breakout rows when line_value_event is above the event candle high",
            "resistance branch now drops breakout rows when line_value_event is below the event candle low",
            "both branches also zero the confirm_1 / confirm_2 breakout variants, so the same bad event bar cannot leak back through confirmation rows",
        ],
        "not_found": [
            "No BTC/ETH minimal rerun in this step, so this is not fix closure.",
            "No claim yet that mirrored breakout pairs are solved; that is A4-b3 / A4-c work.",
            "No claim yet about how much breakout-family alpha survives after the sampler repair.",
        ],
        "reliability": {
            "code_presence": "high",
            "post_rerun_impact": "not_measured_yet",
        },
        "source_checks": checks.to_dict("records"),
    }
    (ART / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    support_ok = "是" if support_line else "否"
    resistance_ok = "是" if resistance_line else "否"
    html = f"""<!doctype html>
<html lang=\"zh\">
<head>
  <meta charset=\"utf-8\" />
  <title>PyTrendline V3 · Sampler Fix R2 Implementation Note</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 32px auto; max-width: 1100px; line-height: 1.6; color: #1f2937; padding: 0 16px; }}
    h1, h2, h3 {{ color: #111827; }}
    .card {{ border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px 18px; margin: 16px 0; background: #fff; }}
    .ok {{ background: #ecfdf5; border-left: 4px solid #10b981; padding: 12px 14px; }}
    .warn {{ background: #fffbeb; border-left: 4px solid #f59e0b; padding: 12px 14px; }}
    .muted {{ color: #6b7280; }}
    code {{ background: #f3f4f6; padding: 1px 4px; border-radius: 4px; }}
    pre {{ background: #0f172a; color: #e2e8f0; padding: 14px; border-radius: 10px; overflow-x: auto; font-size: 13px; }}
    .tbl {{ border-collapse: collapse; width: 100%; font-size: 14px; }}
    .tbl th, .tbl td {{ border: 1px solid #e5e7eb; padding: 6px 8px; text-align: left; vertical-align: top; }}
    .tbl th {{ background: #f9fafb; }}
    ul {{ margin-top: 0.3em; }}
  </style>
</head>
<body>
  <h1>PyTrendline V3 · Sampler Fix R2 Implementation Note</h1>
  <p><a href="../pytrendline_event_validation_v3/report.html">← 返回 v3 主报告</a> ｜ <a href="../pytrendline_event_validation_v3_sampler_fix_spec/report.html">上一页：sampler fix spec</a></p>

  <div class="card warn">
    <b>这页完成了什么？</b>
    只完成 TODO 里的 <code>A4-b2</code>：把 <b>event-time strict wrong-side breakout 过滤</b> 实现在 v3 sampler 里。
    这页不是重跑结果页，所以不会假装回答“修完后 alpha 还剩多少”。
  </div>

  <div class="card ok">
    <b>一句话结论：</b>
    v3 采样器源码里现在已经有了显式的 R2 几何门：<b>support breakout 若 line 已高于 event high，则该 breakout raw / confirm_1 / confirm_2 一起丢弃；resistance 则做镜像处理</b>。
  </div>

  <h2>1. 这轮发现了什么？</h2>
  <div class="card">
    <ul>
      <li><b>Found:</b> support 分支已出现 R2 条件：<code>{escape(support_gate)}</code>（检测结果：<b>{support_ok}</b>）。</li>
      <li><b>Found:</b> resistance 分支已出现 R2 条件：<code>{escape(resistance_gate)}</code>（检测结果：<b>{resistance_ok}</b>）。</li>
      <li><b>Found:</b> 两边都不只是屏蔽 raw breakout，还会同步把 <code>breakout_confirm_1</code> / <code>breakout_confirm_2</code> 设为 <code>False</code>，避免坏样本换个确认标签重新溜回来。</li>
    </ul>
  </div>

  <h2>2. 这轮没有发现什么？</h2>
  <div class="card">
    <ul>
      <li><b>Not found:</b> 这轮没有做 BTC+ETH / 20~45d 的最小重跑，所以这页不是 A4-c。</li>
      <li><b>Not found:</b> 这轮没有处理 exact mirrored breakout pair；那还是 <code>A4-b3</code> 的剩余工作。</li>
      <li><b>Not found:</b> 这轮没有声称 breakout family 的 side-level 结论已经可信；需要等重跑审计回来再说。</li>
    </ul>
  </div>

  <h2>3. 实现检查表</h2>
  <div class="card">{render_table(checks)}</div>

  <h2>4. 代码证据（support 分支）</h2>
  <div class="card">
    <pre>{escape(support_snippet)}</pre>
  </div>

  <h2>5. 代码证据（resistance 分支）</h2>
  <div class="card">
    <pre>{escape(resistance_snippet)}</pre>
  </div>

  <h2>6. 结果该怎么读？</h2>
  <div class="card">
    <ul>
      <li><b>Plain language：</b>以前 sampler 可能把“这根线在事件发生那根 K 线时，几何位置已经明显错边”的 breakout 也记进样本。现在至少先把这批最明显的坏 breakout 行挡住了。</li>
      <li><b>What this supports：</b>后续 A4-c 的最小重跑，应该能诚实回答 strict wrong-side share 是否下降。</li>
      <li><b>What this does NOT support：</b>还不支持直接说 support / resistance breakout 是两条独立 alpha，也不支持说 breakout short 主线已经审计干净。</li>
    </ul>
  </div>

  <h2>7. 可靠性</h2>
  <div class="card">
    <ul>
      <li><b>高：</b>“代码里有没有这道门”——这是直接扫源码得出的。</li>
      <li><b>低 / 未测：</b>“这道门会让样本减少多少、alpha 还剩多少”——必须等最小重跑。</li>
    </ul>
  </div>

  <h2>8. 下一步</h2>
  <div class="card">
    <ol>
      <li>继续做 <code>A4-b3</code>：显式处理 exact mirrored breakout pairs。</li>
      <li>然后做 <code>A4-c</code>：BTC+ETH / 20~45d 最小重跑，对比 strict wrong-side rows 与 mirrored pair rows 是否下降。</li>
    </ol>
  </div>

  <h2>Artifacts</h2>
  <div class="card">
    <ul>
      <li><a href="../../artifacts/pytrendline_event_validation_v3_sampler_fix_r2_impl/implementation_checks.csv">implementation_checks.csv</a></li>
      <li><a href="../../artifacts/pytrendline_event_validation_v3_sampler_fix_r2_impl/support_gate_snippet.txt">support_gate_snippet.txt</a></li>
      <li><a href="../../artifacts/pytrendline_event_validation_v3_sampler_fix_r2_impl/resistance_gate_snippet.txt">resistance_gate_snippet.txt</a></li>
      <li><a href="../../artifacts/pytrendline_event_validation_v3_sampler_fix_r2_impl/summary.json">summary.json</a></li>
    </ul>
  </div>
</body>
</html>
"""
    (SITE / "report.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
