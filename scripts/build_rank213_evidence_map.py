#!/usr/bin/env python3
from __future__ import annotations

import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_DIR = ROOT / "reports" / "artifacts" / "rank213_evidence_map" / "manifests"
DOC_PATH = ROOT / "docs" / "RANK213_EVIDENCE_MAP.md"
HTML_PATH = ROOT / "reports" / "site" / "paper" / "rank213_evidence_map.html"
PAPER_ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank213_largecap_xs_jump_veto"
MONTHLY_VOLUME_SUMMARY_PATH = PAPER_ART_DIR / "rank213_monthly_volume_universe_rebuild_summary.json"
SEGMENT_STABILITY_SUMMARY_PATH = PAPER_ART_DIR / "rank213_monthly_volume_segment_stability_summary.json"


def load_manifests() -> list[dict]:
    rows: list[dict] = []
    for path in sorted(MANIFEST_DIR.glob("*.json")):
        obj = json.loads(path.read_text(encoding="utf-8"))
        obj["_path"] = path
        rows.append(obj)
    rows.sort(key=lambda x: (int(x.get("order", 9999)), str(x.get("id", ""))))
    return rows


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def rel_link(path: str) -> str:
    return f"/momentum/{path}"


def md_list(items: list[str]) -> str:
    return "<br/>".join(f"- {item}" for item in items)


def fmt_pct(value: object) -> str:
    try:
        return f"{float(value):.2f}%"
    except (TypeError, ValueError):
        return "n/a"


def fmt_bps(value: object) -> str:
    try:
        return f"{float(value):.2f} bps"
    except (TypeError, ValueError):
        return "n/a"


def fmt_num(value: object, digits: int = 2) -> str:
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return "n/a"


def no_lookahead_rows() -> list[dict]:
    seg = read_json(SEGMENT_STABILITY_SUMMARY_PATH)
    rows = seg.get("overall") or []
    if rows:
        return rows
    monthly = read_json(MONTHLY_VOLUME_SUMMARY_PATH)
    metrics = monthly.get("metrics", {}).get("monthly_volume_rebuild", {})
    return [
        {
            "label": "1) plain baseline",
            "strategy": "plain_baseline",
            **metrics.get("plain", {}),
        },
        {
            "label": "2) baseline + veto",
            "strategy": "baseline_plus_veto",
            **metrics.get("baseline_plus_veto", {}),
        },
        {
            "label": "3a) veto + fixed gate",
            "strategy": "baseline_plus_veto_plus_fixed_gate",
            **metrics.get("baseline_plus_veto_plus_gate", {}),
        },
    ]


def row_meaning(strategy: str) -> str:
    meanings = {
        "plain_baseline": "原始 15m Rank213 排名逻辑，不加 veto，不加 gate；每次都交易。",
        "baseline_plus_veto": "在 baseline 上加入 short-leg jump veto；仍然每次都交易。",
        "baseline_plus_veto_plus_fixed_gate": "沿用 frozen30 研究里的固定 gate；gate OFF 时空仓。",
        "baseline_plus_veto_plus_percentile_gate_q60": "用 monthly-volume 历史自身的 expanding percentile q60 gate；这是研究候选，不是当前 live 规则。",
    }
    return meanings.get(strategy, "")


def row_reading(strategy: str, net_cum_pct: object, max_dd_pct: object) -> str:
    try:
        net = float(net_cum_pct)
        dd = float(max_dd_pct)
    except (TypeError, ValueError):
        return "缺少可读结果。"
    if strategy == "baseline_plus_veto_plus_percentile_gate_q60":
        return "全样本略正，但回撤很深，只能当候选研究，不能当已过关。"
    if net < 0:
        return "亏损或弱化明显，不支持继续用旧故事解释 Rank213。"
    if dd < -50:
        return "收益为正但回撤过深，仍不适合直接实盘扩张。"
    return "结果较好，但仍需看分段稳定性和执行风险。"


def no_lookahead_markdown_table() -> list[str]:
    lines = [
        "| 版本 | 含义 | 开仓率 | 单次均值 | 累计净收益 | 最大回撤 | 当前读法 |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in no_lookahead_rows():
        strategy = str(row.get("strategy", ""))
        lines.append(
            "| {label} | {meaning} | {open_rate} | {mean} | {cum} | {dd} | {reading} |".format(
                label=row.get("label", strategy),
                meaning=row_meaning(strategy),
                open_rate=fmt_pct(row.get("open_rate_pct", row.get("gate_on_rate_pct"))),
                mean=fmt_bps(row.get("net_mean_bps")),
                cum=fmt_pct(row.get("net_cum_pct")),
                dd=fmt_pct(row.get("max_drawdown_pct")),
                reading=row_reading(strategy, row.get("net_cum_pct"), row.get("max_drawdown_pct")),
            )
        )
    return lines


def no_lookahead_html_table() -> str:
    body = []
    for row in no_lookahead_rows():
        strategy = str(row.get("strategy", ""))
        body.append(
            "<tr>"
            f"<td><b>{escape(str(row.get('label', strategy)))}</b><br/><span class='muted'>{escape(strategy)}</span></td>"
            f"<td>{escape(row_meaning(strategy))}</td>"
            f"<td>{escape(fmt_pct(row.get('open_rate_pct', row.get('gate_on_rate_pct'))))}</td>"
            f"<td>{escape(fmt_bps(row.get('net_mean_bps')))}</td>"
            f"<td><b>{escape(fmt_pct(row.get('net_cum_pct')))}</b></td>"
            f"<td>{escape(fmt_pct(row.get('max_drawdown_pct')))}</td>"
            f"<td>{escape(row_reading(strategy, row.get('net_cum_pct'), row.get('max_drawdown_pct')))}</td>"
            "</tr>"
        )
    return (
        "<table class='wide'><thead><tr>"
        "<th>版本</th><th>它在测什么</th><th>开仓率</th><th>单次均值</th><th>累计净收益</th><th>最大回撤</th><th>人话结论</th>"
        "</tr></thead><tbody>"
        + "".join(body)
        + "</tbody></table>"
    )


def frozen_vs_causal_html() -> str:
    monthly = read_json(MONTHLY_VOLUME_SUMMARY_PATH)
    metrics = monthly.get("metrics", {})
    frozen = metrics.get("frozen30", {}).get("baseline_plus_veto_plus_gate", {})
    causal = metrics.get("monthly_volume_rebuild", {}).get("baseline_plus_veto_plus_gate", {})
    return f"""
      <table class="wide">
        <thead><tr><th>对比项</th><th>frozen30 固定名单</th><th>上月 K 线选池 / monthly-volume causal</th></tr></thead>
        <tbody>
          <tr><td>选池方式</td><td>固定 admission 30 币；历史回看时容易把后面才知道的标的带回过去。</td><td>每个月只用上一完整自然月 Binance UM perpetual 1d K 线的 <code>quote_volume</code> 总和选 Top30，再交易当月。</td></tr>
          <tr><td>累计净收益</td><td><b>{escape(fmt_pct(frozen.get('net_cum_pct')))}</b></td><td><b>{escape(fmt_pct(causal.get('net_cum_pct')))}</b></td></tr>
          <tr><td>单次均值</td><td>{escape(fmt_bps(frozen.get('net_mean_bps')))}</td><td>{escape(fmt_bps(causal.get('net_mean_bps')))}</td></tr>
          <tr><td>最大回撤</td><td>{escape(fmt_pct(frozen.get('max_drawdown_pct')))}</td><td>{escape(fmt_pct(causal.get('max_drawdown_pct')))}</td></tr>
          <tr><td>读法</td><td>这解释了为什么旧页面看起来强。</td><td>这才是当前更该优先看的历史 sanity check；结果明显弱化。</td></tr>
        </tbody>
      </table>
    """


def build_markdown(rows: list[dict]) -> str:
    monthly = read_json(MONTHLY_VOLUME_SUMMARY_PATH)
    seg = read_json(SEGMENT_STABILITY_SUMMARY_PATH)
    sample = monthly.get("sample", seg.get("sample", {}))
    lines = [
        "# Rank213 evidence map",
        "",
        "更新时间：2026-05-06",
        "",
        "## 目的",
        "",
        "把 Rank213 相关结果按“能回答什么问题”分层，避免后续开发把 frozen30、as-of、monthly-volume causal universe、shadow/live execution audit 混成同一条证据。",
        "",
        "## 当前一句话结论",
        "",
        "Rank213 当前应该被读成：`frozen30` 是运行/执行口径，`monthly_volume_causal` 才是当前更重要的历史 sanity check。去掉选池未来函数风险后，旧 baseline 明显变弱，所以不能再写成“历史滚动 Top30 已长周期验证通过”。",
        "",
        "## 先读这段",
        "",
        "- `frozen30`：回答“当前 runner / paper lane 怎么跑”。它不是历史滚动选池证明。",
        "- `monthly_volume_causal`：回答“如果每个月只用上个月已经发生的 K 线数据选池，Rank213 还站不站得住”。当前答案是：明显站不稳。",
        "- `asof_frozen_seed`：只修正“币没上市不能交易”，不等于每月滚动 Top30。",
        "- `live_audit_shadow`：只回答最新 gate、残仓、执行漂移，不回答长期 alpha。",
        "",
        "## 无未来函数版本：上月 K 线选池回测",
        "",
        "这里的“上月 K 线选池”具体指：在每个月开始时，只使用上一完整自然月 Binance UM perpetual `1d` K 线里的 `quote_volume` 总和，选出当月 Top30 universe；然后在这个当月 universe 上运行原 Rank213 的 15m / veto / gate / 4bps 成本规则。它不会用当月或未来月份的表现来决定当月池子。",
        "",
        f"样本：`{sample.get('start_utc', 'n/a')}` 到 `{sample.get('end_utc', 'n/a')}`，rebalance `{sample.get('rebalances', 'n/a')}` 次。",
        "",
        *no_lookahead_markdown_table(),
        "",
        "核心读法：旧 frozen30 的 `baseline+veto+gate` 在同一长样本里看起来是正的，但换成上月 K 线 causal 选池后变成约 `-37.13%`。这说明旧结果很可能被静态名单 / 幸存者偏差放大。",
        "",
        "## 证据分层",
        "",
        "| 层级 | 证据面 | 默认入口 | universe / causality | 当前读法 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {category} | `{id}`<br/>{title}<br/>status=`{status}` | `{page}` | {universe}<br/>{causality}<br/>cadence={cadence} | {verdict} |".format(
                category=row.get("category", ""),
                id=row.get("id", ""),
                title=row.get("title", ""),
                status=row.get("status", ""),
                page=row.get("primary_page", ""),
                universe=row.get("universe_mode", ""),
                causality=row.get("selection_causality", ""),
                cadence=row.get("cadence", ""),
                verdict=row.get("verdict", ""),
            )
        )

    lines.extend(
        [
            "",
            "## 当前关键数值",
            "",
            "- `monthly_volume_universe_rebuild`：样本 `2020-02-01T00:00:00Z` 到 `2026-04-10T18:00:00Z`。",
            "- 该口径下旧 Rank213 plain baseline：`-98.09%`。",
            "- 该口径下 baseline + veto：`-99.60%`。",
            "- 该口径下 baseline + veto + fixed gate：`-37.13%`。",
            "- 该口径下 percentile q60 gate：全样本轻微正，但最大回撤仍深，不能视为过关。",
            "- frozen30 固定名单同规则下看起来更强，但它不是滚动历史选池证明。",
            "",
            "## 后续开发规则",
            "",
            "1. 新功能如果依赖“策略长期有效”，默认必须先引用 `monthly_volume_universe_rebuild` 或更新后的 causal universe 证据，不能只引用 frozen30 或 as-of 页面。",
            "2. 新功能如果只是执行审计、残仓对账、basket parity、systemd 编排，可以引用 live/shadow artifacts，但文案必须写成 execution audit。",
            "3. 页面或报告标题里必须显式包含 universe 口径：`frozen30`、`asof-frozen-seed`、`monthly-volume-causal`、`live-audit` 之一。",
            "4. 任何回测表格必须同时展示 `universe_mode`、`selection_causality`、`cadence`、`sample_start/end`。",
            "5. 下一步再把报告页逐步改为从这些 manifest 读取口径字段。",
            "",
            "## Manifest 来源",
            "",
            f"- `{MANIFEST_DIR.relative_to(ROOT)}`",
        ]
    )
    return "\n".join(lines) + "\n"


def render_items(items: list[str]) -> str:
    if not items:
        return "<li>无</li>"
    return "".join(f"<li>{escape(str(item))}</li>" for item in items)


def build_html(rows: list[dict]) -> str:
    cards: list[str] = []
    for row in rows:
        metrics = "".join(f"<span class='pill'>{escape(str(x))}</span>" for x in row.get("key_metrics", []))
        artifacts = render_items(row.get("source_artifacts", []))
        cards.append(
            f"""
  <section class="card">
    <div class="topline"><span>{escape(row.get('category', ''))}</span><span class="status">{escape(row.get('status', ''))}</span></div>
    <h2>{escape(row.get('title', ''))}</h2>
    <p class="muted"><code>{escape(row.get('id', ''))}</code> · <a href="{escape(rel_link(row.get('primary_page', '')))}">{escape(row.get('primary_page', ''))}</a></p>
    <table>
      <tbody>
        <tr><th>Universe</th><td><code>{escape(row.get('universe_mode', ''))}</code></td></tr>
        <tr><th>Causality</th><td>{escape(row.get('selection_causality', ''))}</td></tr>
        <tr><th>Cadence</th><td>{escape(row.get('cadence', ''))}</td></tr>
        <tr><th>Sample</th><td><code>{escape(row.get('sample_start_utc', ''))}</code> -> <code>{escape(row.get('sample_end_utc', ''))}</code></td></tr>
        <tr><th>Verdict</th><td><b>{escape(row.get('verdict', ''))}</b></td></tr>
      </tbody>
    </table>
    <p>{metrics}</p>
    <details><summary>Use / do-not-use / artifacts</summary>
      <h3>Use for</h3><ul>{render_items(row.get('use_for', []))}</ul>
      <h3>Do not use for</h3><ul>{render_items(row.get('do_not_use_for', []))}</ul>
      <h3>Source artifacts</h3><ul>{artifacts}</ul>
    </details>
  </section>
"""
        )
    monthly = read_json(MONTHLY_VOLUME_SUMMARY_PATH)
    seg = read_json(SEGMENT_STABILITY_SUMMARY_PATH)
    sample = monthly.get("sample", seg.get("sample", {}))
    coverage = monthly.get("coverage", {})
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Rank213 Evidence Map</title>
  <style>
    body {{ font-family: "Noto Sans SC", "Source Han Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif; margin: 0; background: #f6f3ee; color: #172033; line-height: 1.65; }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 28px 16px 52px; }}
    .card {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 18px 20px; margin: 14px 0; box-shadow: 0 1px 2px rgba(15,23,42,.04); }}
    .hero {{ background: linear-gradient(135deg, #fff7ed, #ffffff 52%, #e0f2fe); border-color: #fed7aa; }}
    .warning {{ background: #fff7ed; border-color: #fdba74; }}
    .plain {{ background: #f8fafc; }}
    .muted {{ color: #64748b; }}
    .topline {{ display: flex; justify-content: space-between; gap: 12px; color: #475569; font-size: 13px; text-transform: uppercase; letter-spacing: .04em; }}
    .status {{ background: #e2e8f0; color: #0f172a; border-radius: 999px; padding: 2px 8px; }}
    .pill {{ display: inline-block; background: #eef2ff; border: 1px solid #c7d2fe; border-radius: 999px; padding: 4px 9px; margin: 3px 4px 3px 0; font-size: 13px; }}
    .grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }}
    .metric {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; padding: 12px 14px; }}
    .metric b {{ display: block; font-size: 22px; line-height: 1.25; }}
    .callout {{ border-left: 5px solid #f97316; padding: 10px 14px; background: #fff7ed; border-radius: 10px; }}
    .reading-path li {{ margin: 6px 0; }}
    code {{ background: #f1f5f9; border-radius: 6px; padding: 2px 6px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #e2e8f0; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ width: 130px; color: #475569; background: #f8fafc; }}
    .wide th {{ width: auto; }}
    a {{ color: #2563eb; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    summary {{ cursor: pointer; color: #2563eb; }}
    @media (max-width: 760px) {{
      .grid {{ grid-template-columns: 1fr; }}
      table {{ display: block; overflow-x: auto; white-space: nowrap; }}
    }}
  </style>
</head>
<body>
<main>
  <section class="card hero">
    <h1>Rank213 Evidence Map：先看这页，避免误读</h1>
    <p>这页从 manifest 和回测 summary 生成，用来区分：运行口径、无未来函数历史证据、候选研究、as-of 修正、退役证据和 live audit。默认先看这里，再进入具体页面。</p>
    <p class="muted">更新时间：2026-05-06 · manifest: <code>{escape(str(MANIFEST_DIR.relative_to(ROOT)))}</code></p>
    <p><a href="/momentum/paper/rank213_largecap_xs_jump_veto.html">返回 Rank213 主页面</a> · <a href="/momentum/index.html">站点首页</a></p>
  </section>

  <section class="card warning">
    <h2>一句话结论</h2>
    <p><b>Rank213 不能再被简写成”历史滚动 Top30 已长周期验证通过”。</b> 当前更严谨的读法是：<code>frozen30</code> 只说明当前 runner / paper lane 怎么跑；真正用来检查”去掉选池未来函数以后还行不行”的，是 <code>monthly_volume_causal</code>。这条证据明显削弱旧结论。</p>
    <div class=”callout”>如果你只想判断是否应该继续实盘扩张：先看下面”无未来函数版本”的表。它显示旧母策略在上月 K 线选池下很弱，固定 gate 后仍是负收益。</div>
    <p><b>当前活跃策略：</b><code>rank213_age90_14d_skip1d_voladj</code> 已于 2026-05-06 接入真钱 canary。Phase 3 验证未通过正式 promotion，但用户选择先跑 tiny-live 进行实盘 falsification。详见下方 Live Canary 卡片。</p>
  </section>

  <section class="card">
    <h2>三分钟读懂</h2>
    <ul class="reading-path">
      <li><b>问题在哪里：</b>如果拿 4 月才确定的 frozen30 名单去跑 3 月或更早历史，等于把未来才知道的标的带回过去，历史收益容易虚高。</li>
      <li><b>修正怎么做：</b>每个月只用上一完整自然月 Binance UM perpetual <code>1d</code> K 线里的 <code>quote_volume</code> 总和选 Top30，当月只交易这批标的。</li>
      <li><b>这不是完美 market cap 真值：</b>它是成交额 / 热门度 proxy，但它至少满足“当月选池不看当月未来表现”。</li>
      <li><b>读法优先级：</b>讨论历史有效性先看 <code>monthly_volume_causal</code>；讨论当前执行/残仓才看 <code>live_audit_shadow</code>；不要用 <code>asof</code> 或 <code>frozen30</code> 冒充滚动选池证明。</li>
    </ul>
  </section>

  <section class="card">
    <h2>无未来函数版本：上月 K 线选池回测</h2>
    <p>样本 <code>{escape(str(sample.get('start_utc', 'n/a')))}</code> → <code>{escape(str(sample.get('end_utc', 'n/a')))}</code>，rebalance <code>{escape(str(sample.get('rebalances', 'n/a')))}</code> 次。选池覆盖：候选币 <code>{escape(str(coverage.get('candidate_count', 'n/a')))}</code>，任一月份入选过 <code>{escape(str(coverage.get('union_symbols_selected_any_month', 'n/a')))}</code> 个，月均和 frozen30 重叠约 <code>{escape(fmt_num(coverage.get('avg_overlap_with_frozen30'), 2))}</code> 个。</p>
    {no_lookahead_html_table()}
    <p class="muted">重点不是某个单月，而是同一套 Rank213 规则一旦换成 causal rolling universe，baseline 和 veto 都接近归零式亏损；fixed gate 只把亏损缩小到 <b>-37.13%</b>，不能证明策略已过关。</p>
  </section>

  <section class="card">
    <h2>为什么旧结果看起来更好</h2>
    <p>下面是同一长样本、同一套 Rank213 规则、同一成本口径下的关键差异：只换 universe 选池方式，结果就从正收益变成负收益。</p>
    {frozen_vs_causal_html()}
    <p class="muted">这不是说 frozen30 页面没有用；它有运行和执行定义价值。但它不能回答“历史上每个月重新选 Top30 是否有效”。</p>
  </section>

  <section class="card plain">
    <h2>证据分层：每个页面该怎么用</h2>
    <p class="muted">下面的卡片按证据面分组。进入具体页面前，先看它的 universe、causality 和 do-not-use，避免把执行审计误读成历史 alpha。</p>
  </section>

  {''.join(cards)}
</main>
</body>
</html>
"""


def main() -> int:
    rows = load_manifests()
    DOC_PATH.write_text(build_markdown(rows), encoding="utf-8")
    HTML_PATH.write_text(build_html(rows), encoding="utf-8")
    print(f"wrote {DOC_PATH.relative_to(ROOT)}")
    print(f"wrote {HTML_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
