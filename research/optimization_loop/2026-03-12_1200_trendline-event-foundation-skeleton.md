# Add trendline_event foundation skeleton

## Why this was chosen now

这轮继续沿当前最近主线推进：把 `trendline_event_foundation_report` 从文档 blueprint 再往前推一步，变成真正存在的脚本 contract + 页面 skeleton。

上一轮已经完成了 `P1-E`：
- 最小 artifacts 清单
- 页面 blueprint
- 最小读法

在这个上下文里，最自然、最小步、最有复用价值的下一步，不是马上开始算真实统计，而是先把：
- `scripts/build_trendline_event_foundation_report.py`
- `reports/site/factors/trendline_event_foundation/report.html`
- `reports/site/factors/trendline_event_foundation/contract.json`

这些“实现骨架”固定下来。这样后续 Agent 不需要再从空白开始猜：
- 这个 report 该输出到哪里；
- 它至少应该长什么样；
- artifact blueprint 和默认读法如何映射到真正页面。

因此本轮选择：
- **主点：把 trendline event foundation 从文档 blueprint 推到脚本 / 页面 skeleton**
- 紧邻子点：在 TODO 中回写一条“脚本输入 / 输出草图已存在”说明

## What changed

### 1) 新增 `scripts/build_trendline_event_foundation_report.py`

已创建第一版脚本 contract / skeleton，当前职责是：
- 生成 `reports/site/factors/trendline_event_foundation/report.html`
- 生成 `reports/site/factors/trendline_event_foundation/contract.json`

当前 **不计算真实事件统计**，而是先固定：
- 页面角色说明
- input / output contract
- 最小 artifact blueprint
- 默认阅读顺序
- 下一位 Agent 应该遵守的实现边界

### 2) 新增 skeleton 页面

新增页面：
- `reports/site/factors/trendline_event_foundation/report.html`

它当前明确说明：
- 这是 `pytrendline_research` 之后的下一页；
- 目前仍是 contract / skeleton only；
- 它的工作不是先给最终净值，而是先固定 event-study 页面结构；
- 页面中已经列出了最小 artifacts 清单和默认阅读顺序。

### 3) 新增 machine-readable contract

新增文件：
- `reports/site/factors/trendline_event_foundation/contract.json`

该文件当前保存：
- `status = contract_only`
- design source / task source
- planned artifacts
- default scope（BTC / ETH / SOL / DOGE / XRP；30m / 60m；representative_only）

这能帮助后续脚本实现不只依赖 HTML，也能从一个更稳定的 contract 文件出发。

### 4) 回写 TODO

在 `docs/TODO.md` 的 `P1-E` 之后新增并勾选：
- `起草 scripts/build_trendline_event_foundation_report.py 的输入 / 输出草图`

说明已写明：
- skeleton 当前生成 `report.html + contract.json`
- 还不计算真实统计
- 目的就是先把页面职责、I/O contract 和默认读法固定下来

## Validation / evidence

### A. 最小运行验证

执行：
- `python3 scripts/build_trendline_event_foundation_report.py`
- `python3 scripts/build_plans_site.py`
- `bash scripts/publish_report_site.sh`

结果：
- 成功写出：
  - `reports/site/factors/trendline_event_foundation/report.html`
  - `reports/site/factors/trendline_event_foundation/contract.json`
- 成功发布站点

### B. 线上检查

已确认线上可打开：
- `/momentum/factors/trendline_event_foundation/report.html`

页面中已经能读到：
- minimum artifact blueprint
- default reading order
- input / output contract

### C. TODO 镜像同步

已确认 `momentum_todo.html` 中新加入的 skeleton 任务说明已同步上线。

## Risks / caveats

- 这轮创建的是 **skeleton / contract**，不是 event-study 实现；
- 页面目前仍没有真实统计表，因此不能把它误读成已经完成 foundation report；
- 发布脚本会顺手刷新 `reading/deep_dives/*` 与 `reading/quant_digests/*` 的站点时间戳，这些文件仍保持 dirty，本轮未将它们一并提交。

## Next recommended step

现在 foundation report 已经从文档 blueprint 进入脚本 / 页面 skeleton。下一轮最自然的主点有两个：

1. **把 `contract.json` 和 `RESEARCH_TRENDLINE_EVENT.md` 对齐成更明确的数据接口说明**
   - 例如明确 future data source keys / expected CSV schemas / event bucket enum。

2. **开始往 skeleton 里填第一批真实统计**
   - 最推荐先填：
     - `sample_coverage_table`
     - `event_density_summary`
     - `breakout_confirmation_comparison`

如果只选一个，我建议下一轮优先做：
- **开始填第一批真实统计（尤其 sample coverage + event density）**

原因：到这一步为止，设计、判断逻辑、artifact blueprint 和 skeleton 页都已经有了，下一步最该开始从 contract-only 走向真正的 event-study 内容。

## Commit hash (if committed)

- 已 selective commit：`3c5623a` (`feat(momentum): add trendline event foundation skeleton`)

## Commit note

repo 中仍有与本轮无关的 dirty files（例如 `reports/site/reading/deep_dives/*`、`reports/site/reading/quant_digests/*` 的自动刷新项，以及工作区外层的未跟踪文件），因此没有整仓提交；本轮只 selective commit 了：
- `scripts/build_trendline_event_foundation_report.py`
- `docs/TODO.md`
- `reports/site/plans/*`
- `reports/site/factors/trendline_event_foundation/*`

本记录文件将单独提交并邮件发送，避免把无关脏文件混入同一提交。
