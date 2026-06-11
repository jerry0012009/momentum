# PyTrendline 报告：补 baseline v1 / 结论卡 / 下一步建议

## Why this was chosen now

这轮继续沿着最近几次自动优化的同一条主线推进：把 `pytrendline_research` 收尾成一个可冻结的 explainability baseline v1。

最近几轮已经连续完成了：
- decision chain
- accepted vs rejected examples
- line lifecycle / state diagram
- time semantics
- selected line deep-dive
- candidate lines before filtering
- duplicate grouping before/after
- plans / TODO / research design 文档网页化

在这个上下文里，当前最邻近、最小步、但对 Jerry 理解最有帮助的一步，不是再补新图，而是补上三张收束性的“结论卡”：
1. 这页现在到底是什么阶段（baseline v1 status）；
2. 当前应该相信什么 / 不该过度解读什么；
3. 从这里往 event foundation 最自然的下一步是什么。

这一步直接对应 `docs/TODO.md` 中 P0 收尾项，也能避免读者在页面末尾仍然不知道：
- 这页已经完成到什么程度；
- 它是不是可交易信号；
- 后面应不应该直接跳去 parallel channel 或策略层。

## What changed

### 1) 在 `pytrendline_research` 页面新增 `Baseline v1 status` 卡片

文件：
- `scripts/build_pytrendline_report.py`
- `reports/site/factors/pytrendline_research/report.html`

新增区块：
- `Baseline v1 status：这页当前处在什么阶段`

该卡片明确说明：
- 当前阶段是 **explainability baseline v1**；
- 它最适合做：结构解释 / 外部方法映射 / foundation report 的前置教材；
- 它当前不是什么：正式交易信号、bar-by-bar 审计引擎、最终收益证明。

### 2) 新增“当前我应该相信什么 / 不该过度解读什么”结论卡

新增区块：
- `当前我应该相信什么 / 不该过度解读什么`

该卡片把页面阅读后的结论收束为三类：
- 现在已经可以稳健相信的：
  - 页面已把 pivot → candidate lines → grouping → breakout 语义讲清楚；
- 现在不该直接跳到的：
  - 不能把 `is_breakout=True` 直接读成可追信号；
  - 不能把高 `score` 直接读成高收益线；
- 当前最合理的使用方式：
  - 把它当作结构语义基线页，为后续 slope / confirmation / feature value 审计做准备。

### 3) 新增“下一步建议”区块

新增区块：
- `下一步建议：从 explainability baseline 到 event foundation`

该区块明确建议：
1. 进入 `trendline_event_foundation_report`
2. 先做事件研究（breakout vs rebound、raw vs confirmed、slope buckets），再做策略
3. `parallel channel` 暂时保持候选分支，除非 foundation report 给出更强正面证据

### 4) 回写 TODO

已将以下 P0 条目标记完成：
- `当前我应该相信什么 / 不该过度解读什么` 结论卡片
- `下一步建议` 区块
- `baseline v1 status note`

## Validation / evidence

### A. 最小重建 + 发布

执行：
- `/root/clawd/jerry/momentum/.venv/bin/python scripts/build_pytrendline_report.py --ticker BTC-USD --period 10d --interval 5m --window-bars 96`
- `python3 scripts/build_plans_site.py`
- `bash scripts/publish_report_site.sh`

结果：
- 成功重建 `reports/site/factors/pytrendline_research/report.html`
- 成功发布到站点

### B. 页面区块存在性检查

已确认 HTML 中出现新的 3 个区块：
- `Baseline v1 status：这页当前处在什么阶段`
- `当前我应该相信什么 / 不该过度解读什么`
- `下一步建议：从 explainability baseline 到 event foundation`

### C. 线上检查

已抓取线上页面并确认当前生成时间更新到：
- `2026-03-12 08:01 UTC`

## Risks / caveats

- 这轮补的是“页面收束层”，不是新的研究实验，也没有新增 event-level validation 结果。
- 页面现在已经更明确地说明了什么能信、什么不能直接读成交易信号，但这并不替代后续 `trendline_event_foundation_report` 的最小验证。
- 本轮重建了 pytrendline 报告 artifacts，因此与该报告相关的 CSV / PNG / HTML 都有时间戳更新；提交时已只挑选本轮相关文件，未把其它因发布脚本顺手生成的脏文件一起打包。

## Next recommended step

下一轮最自然的主点有两个：

1. **四段式页面结构重排**
   - 把页面更明确地重排成：定义层 / 计算层 / 结果层 / 边界层。

2. **开始定义 `trendline_event_foundation_report` 的最小 artifacts 与指标口径**
   - 直接承接 `docs/RESEARCH_TRENDLINE_EVENT.md`。

如果只选一个，我建议下一轮优先做：
- **四段式页面结构重排**

原因：这样 `pytrendline_research` 的 P0 收尾就几乎只剩最后一个页面结构项，可以更干净地冻结为 baseline v1。

## Commit hash (if committed)

- 已 selective commit：`bee56b2` (`report(pytrendline): add baseline conclusion cards`)

## Commit note

repo 里仍有与本轮无关的脏文件（例如 interval sweep / crypto rebound scan / deep dive / quant digest 自动生成项，以及更上层工作区的其它未跟踪文件），因此没有整仓提交；本轮只 selective commit 了：
- `docs/TODO.md`
- `scripts/build_pytrendline_report.py`
- `reports/site/factors/pytrendline_research/report.html`
- `reports/site/plans/momentum_todo.html`
- `reports/artifacts/pytrendline_research/*` 中本轮重建涉及的相关文件

本记录文件将单独提交并邮件发送，避免把无关脏文件混入同一提交。
