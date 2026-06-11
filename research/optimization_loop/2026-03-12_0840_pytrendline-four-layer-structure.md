# PyTrendline 报告：改成四段式结构

## Why this was chosen now

这轮继续沿 `pytrendline_research` explainability baseline v1 的最近主线推进，不新开题。

在前几轮已经补完：
- candidate lines before filtering
- duplicate grouping before/after
- baseline v1 status / 信什么 / 不该过度解读什么 / 下一步建议

之后，`docs/TODO.md` 中 P0 剩下最自然、也最关键的未完成项，就是：
- 把当前页面改成更明确的 **四段式结构**（定义层 / 计算层 / 结果层 / 边界层）

这一步的价值不是新增信息，而是把已经堆得很多的 explainability 内容重新编排，减少“定义、计算、结果、限制”交叉打断阅读的问题。对 Jerry 理解页面尤其重要，因为当前页面内容已经足够多，如果不收结构，就容易变成知识点齐全但阅读路径发散的长页。

## What changed

### 1) 新增“四段式结构导航”卡片

在页面导读之后新增：
- `四段式结构导航`

明确告诉读者这页现在按四层来读：
1. 定义层：对象、参数、来源、读法
2. 计算层：pivot → candidate → filter → grouping
3. 结果层：图、代表线、事件线、总览
4. 边界层：time semantics / research-only / next step

### 2) 新增 4 个 section 卡片并重排区块顺序

文件：
- `scripts/build_pytrendline_report.py`
- `reports/site/factors/pytrendline_research/report.html`

已新增 section cards：
- `第一层：定义层`
- `第二层：计算层`
- `第三层：结果层`
- `第四层：边界层`

并做了顺序收束：

#### 定义层
集中放：
- Reading guide
- 步骤总览
- 参数
- 窗口 / 运行边界
- 来源与边界
- 参数为什么这样设
- 图上元素字典

#### 计算层
集中放：
- 逐步骤操作性定义
- Pivot points 是怎么来的
- 候选趋势线是怎么从 pivots 组合出来的
- Candidate lines before filtering
- 为什么不能把所有 pivot 两两相连
- 决策链总览
- 趋势线成立条件 / 过滤条件
- Filter waterfall
- accepted vs rejected examples
- line lifecycle / state diagram
- `num_points` / `is_breakout`
- duplicate grouping 相关区块

#### 结果层
集中放：
- 窗口内数量概览
- Step 1~4 图
- 最终 overlay 图
- selected line deep-dive
- Best support / resistance lines

#### 边界层
集中放：
- 时间语义 / hindsight 边界
- 字段解释
- research-only 边界
- Baseline v1 status
- 当前该相信什么 / 不该过度解读什么
- 下一步建议
- 与 parallel channel 的映射
- Artifacts 列表

### 3) 回写 TODO

已将 P0-B 中：
- `把当前页面改成更明确的四段式结构`

标记完成，并补充说明：
- 已新增四段式结构导航与四个 section 卡片；
- 也同步重排了区块顺序。

## Validation / evidence

### A. 最小重建 + 发布

执行：
- `/root/clawd/jerry/momentum/.venv/bin/python scripts/build_pytrendline_report.py --ticker BTC-USD --period 10d --interval 5m --window-bars 96`
- `python3 scripts/build_plans_site.py`
- `bash scripts/publish_report_site.sh`

结果：
- 成功重建 `reports/site/factors/pytrendline_research/report.html`
- 成功发布站点

### B. 关键结构存在性检查

已确认生成后的 HTML 包含：
- `四段式结构导航`
- `第一层：定义层`
- `第二层：计算层`
- `第三层：结果层`
- `第四层：边界层`

### C. 线上检查

已确认线上页面可读到新的四段式结构导航，生成时间更新到：
- `2026-03-12 08:42 UTC`

## Risks / caveats

- 这轮主要是页面编排层重构，不是新增事件研究结果；因此不会直接提升 signal 质量，只是提升理解成本和后续引用便利性。
- 由于当前报告每次重建都会使用最新下载窗口，所以与该页面绑定的 CSV / PNG / summary 也会随这次重建一起更新；提交时已经只选择本轮相关的 pytrendline 页面文件，没有把无关 report 脏文件带进去。
- 页面虽然更结构化了，但如果后续继续无节制加块，仍然可能再次失去层次，因此今后新增区块时应优先判断它属于哪一层。

## Next recommended step

现在 `pytrendline_research` 的 P0 收尾已经基本完成。下一轮最自然的主点不再是继续磨页面，而是开始承接 P1：

1. **为 `trendline_event_foundation_report` 明确 slope buckets**
2. **明确 quality buckets**
3. **明确第一轮 crypto + 少量周期的 scope 口径**

如果只选一个，我建议下一轮优先做：
- **P1-B：把 slope buckets / quality buckets / first-round scope 写成更明确的表或设计卡片**

原因：这一步能把新主线从“设计文档存在”推进到“可以开始写 foundation report 脚本”。

## Commit hash (if committed)

- 已 selective commit：`35f258f` (`report(pytrendline): reorganize report into four layers`)

## Commit note

repo 里仍有与本轮无关的脏文件（例如 interval sweep / crypto rebound scan / quant digests / deep dives 自动生成项，以及工作区外层若干未跟踪文件），因此没有整仓提交；本轮只 selective commit 了：
- `docs/TODO.md`
- `scripts/build_pytrendline_report.py`
- `reports/site/factors/pytrendline_research/report.html`
- `reports/site/plans/momentum_todo.html`
- `reports/artifacts/pytrendline_research/*` 中本轮重建涉及的相关文件

本记录文件将单独提交并邮件发送，避免把无关脏文件混入同一提交。
