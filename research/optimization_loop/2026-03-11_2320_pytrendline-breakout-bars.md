# PyTrendline 报告：在 breakout-only 图中高亮触发事件的 K 线

## Why this was chosen now

上一轮已经把 `is_breakout` 的计算语义、`breakout_index` 和 `breakout_date` 讲清楚了。

所以这轮最自然、最有杠杆的一步就是把这个“事件字段”真正映射回图上：
- 不只是表格里写 `breakout_index`
- 而是让用户在 breakout-only 图里一眼看到：
  - 哪根线是 breakout line
  - 哪根 K 线触发了这个 breakout

这一步能直接打通：
- 文字解释
- 表格字段
- 图像位置

## What changed

### 1) 在 breakout-only 图中高亮 breakout 触发 bar

文件：
- `scripts/build_pytrendline_report.py`

本轮新增了图形辅助逻辑：
- `_highlight_breakout_bars(...)`

作用：
- 从 breakout lines 里读取 `breakout_index`
- 在 breakout-only 图上，把对应 K 线位置圈出来
- support breakout 用 `S`
- resistance breakout 用 `R`

这样读者不再需要靠肉眼猜“是哪根 bar 真的触发了 breakout”。

### 2) breakout-only 图注同步升级

报告里的 Step 4 图注现在已经明确写出：
- 带描边的事件圈 + `S/R` 标记
- 就是实际触发 breakout 的那根 K 线

这让图的读法变得更明确，不再只是“看见一些虚线”。

### 3) 回写 TODO

已将以下任务标记为完成：
- 在 breakout-only 图里把“触发 breakout 的那根 K 线”单独高亮或打标

## Validation / evidence

### A. 报告已成功重建并发布
执行：
- `/root/clawd/jerry/momentum/.venv/bin/python scripts/build_pytrendline_report.py`
- `./scripts/publish_report_site.sh`

结果：
- 页面已更新到：
  - `https://jp.jerrypsy.top/momentum/factors/pytrendline_research/report.html`

### B. 图注已明确说明事件圈含义

本轮额外检查了生成后的 HTML，确认 breakout-only 图注已经更新，明确说明：
- 带描边的事件圈和 `S/R` 标记
- 对应实际触发 breakout 的那根 K 线

## Risks / caveats

- 当前是“按 breakout line 的 `breakout_index` 回标 bar”，还没有把同一根 bar 属于哪一条具体线做更强的图上关联。
- 若同一根 bar 触发多条 breakout line，当前图上会合并成同一位置的圈标，而不是展开多重标签。
- 这轮主要提升图表可解释性，没有新增新的数值计算逻辑。

## Next recommended step

下一轮最值得做的小步动作：

1. **优先方案**：给 support / resistance 表增加锚点对照列（如 `pointset_indeces / pointset_dates / breakout_index / breakout_date`），把图与表进一步打通；
2. **次优方案**：在 `close + pivots` 图里补适度的 pivot index / 时间标签，让锚点本身也更容易和表格对照。

## Commit hash (if committed)

8d792461cd41a95f10c2e1a2767f70ff99e88cb6

## Commit note

本轮仍存在与 interval sweep / crypto rebound / reading pages 相关的其他脏文件，因此只会 selective commit 本轮的 pytrendline 报告与 TODO 文件，不打包无关改动。
