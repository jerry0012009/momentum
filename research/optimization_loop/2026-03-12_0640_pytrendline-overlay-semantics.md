# PyTrendline 报告：收紧最终总览图的语义与 pivot 噪声

## Why this was chosen now

这轮继续沿着最近几次自动优化的同一条主线推进：`pytrendline_research` 的 explainability / auditability。

紧邻上一轮用户反馈的两个问题是：
1. 最终总览图里，breakout 线仍然是“整条虚线”，没有像 Step 2 / Step 3 那样区分 break 前与 break 后；
2. 总览图里 support / resistance pivots 太多，视觉上会和代表线、事件线抢注意力。

这两点都属于同一个主点：**把最终总览图从“信息堆叠图”收紧成“语义清楚的教学图”**。因此本轮只做一个主点，附带一个紧邻子点：
- 主点：让 overlay 的 breakout 线型与 Step 2 / Step 3 保持一致；
- 子点：overlay 不再显示全量 pivots，而只显示当前展示线实际使用到的 pivots。

这比直接改底层 pivot 检测阈值更稳妥，因为它先解决“看图太乱”的问题，而不改变当前研究基线。

## What changed

### 1) 最终总览图改成“break 前实线 + break 后虚线”

文件：
- `scripts/build_pytrendline_report.py`
- `reports/artifacts/pytrendline_research/trendlines_overlay.png`
- `reports/site/factors/pytrendline_research/report.html`

之前 final overlay 的画法比较粗：
- non-breakout：整条实线
- breakout：整条虚线

现在改成与 Step 2 / Step 3 同步的分段语义：
- breakout 前：实线
- breakout 后：虚线
- breakout bar：继续高亮圈出

这样总览图不再把 breakout 线当成“另一种完全不同的线”，而是把它表达成**同一条结构线在事件前后的两个阶段**。

### 2) 最终总览图不再铺满全量 pivots

新增逻辑：只收集当前 overlay 里被展示的代表线（support top-4 / resistance top-4）实际命中的 `pointset_indeces`，并只高亮这些 pivots。

结果是：
- Step 1 继续保留“全量 pivot universe”视角；
- final overlay 改成“代表线实际依附了哪些 pivots”的收束视角。

这能明显减少视觉噪声，也更符合这张图在页面中的职责：
- 不是再讲一次“窗口里所有 pivot 长什么样”；
- 而是总结“哪些代表线 + 哪些相关 pivots + 哪些 breakout 事件”最终值得看。

### 3) 更新报告文案与 TODO

- 更新了 final overlay 的图下注释，明确写出：
  - breakout 线按 break 前 / break 后分段显示；
  - overlay 只高亮当前展示线实际命中的 pivots；
  - 若要看全量 pivot universe，应回到 Step 1。
- 在 `docs/TODO.md` 中新增并勾选完成项：
  - `调整最终总览图的显示语义与 pivot 噪声控制`

## Validation / evidence

### A. 最小重建 + 发布

执行：
- `/root/clawd/jerry/momentum/.venv/bin/python scripts/build_pytrendline_report.py --ticker BTC-USD --period 10d --interval 5m --window-bars 96`
- `bash scripts/publish_report_site.sh`

结果：
- 成功重建 `reports/site/factors/pytrendline_research/report.html`
- 成功发布到 `/var/www/momentum-report`

### B. HTML 文案检查

已确认页面 HTML 中出现新的 overlay 注释：
- `break 前实线 + break 后虚线`
- `只高亮当前代表线实际命中的那些 support / resistance pivots`
- `如果你要看全量 pivot universe，请回到 Step 1`

### C. 产物更新

已更新与本轮最相关的产物：
- `reports/artifacts/pytrendline_research/trendlines_overlay.png`
- `reports/site/factors/pytrendline_research/report.html`

## Risks / caveats

- 这轮**没有**改变 upstream `pytrendline` 的 pivot 检测阈值；因此“pivot 本身是否过密”这个研究问题还没有被解决，只是先在展示层降低了噪声。
- 当前 overlay 只显示“当前展示线实际使用到的 pivots”，这会让总览图更清楚，但也意味着它不再等价于“完整 pivot 分布图”；完整 pivot 分布需要回到 Step 1 看。
- 如果后面要验证“更严格 swing 点是否更合理”，应该作为**独立研究实验**来做，而不是把展示优化和底层定义变更混在同一轮里。

## Next recommended step

下一轮最自然的相邻动作有两个：

1. **pivot sensitivity / stricter swing experiment**
   - 保留当前 upstream baseline，另开一个更严格 pivot 阈值实验，对比：pivot 数量、有效线数量、breakout 占比、页面可读性。

2. **candidate lines before filtering 图**
   - 让读者看到“原始候选线很多”，以及最终代表线只是筛选压缩后的结果。

如果只选一个，我更建议先做 **pivot sensitivity 对照实验**，因为当前用户已经明确开始质疑“pivot 是否太敏感”。

## Commit hash (if committed)

- 实现与报告变更已 selective commit：`99787d3` (`report(pytrendline): refine overlay semantics`)

## Commit note

repo 里仍存在与本轮无关的脏文件（例如 interval sweep / crypto rebound / quant digests / deep dives / 较早 optimization loop 记录等），因此没有整仓提交；本轮只 selective commit 了：
- `docs/TODO.md`
- `scripts/build_pytrendline_report.py`
- `reports/site/factors/pytrendline_research/report.html`
- `reports/artifacts/pytrendline_research/*` 中本轮重建涉及的相关文件

本记录文件将单独提交，避免把无关脏文件打包进同一个提交。
