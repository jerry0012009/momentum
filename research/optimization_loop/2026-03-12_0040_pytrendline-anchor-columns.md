# PyTrendline 报告：给 Best support / resistance 表补锚点字段

## Why this was chosen now

在 `pytrendline explainability` 主线里，上一轮已经把 Step 2 / Step 3 的代表线命中点用白心圆点画回图上了。

所以下一步最自然就是把这些锚点也写进结果表：
- 不只是“图上看得到”；
- 还要“表里也查得到”；
- 这样图和表才能真正双向对照。

这正对应 TODO 里的：
- 给 support / resistance 表增加与图表对应的锚点信息列。

## What changed

### 1) 新增显示层辅助函数

文件：
- `scripts/build_pytrendline_report.py`

本轮新增：
- `_parse_timestamp_list(...)`
- `_compact_list_str(...)`
- `_prepare_display_lines(...)`

作用：
- 把 `pointset_indeces` 从原始 list / 字符串转换成更适合 HTML 表格阅读的形式；
- 把 `pointset_dates` 格式化成更紧凑的 `MM-DD HH:MM` 列表；
- 统一生成 Best support / Best resistance 表所需的展示列。

### 2) Best support / Best resistance 表增加锚点字段

当前表里新增了：
- `pointset_indeces`
- `pointset_dates`
- `breakout_index`
- `breakout_date`

这样读者现在可以同时看到：
- 这条线命中了哪些结构点
- 这些结构点分别对应什么时间
- 若它是 breakout line，事件发生在哪根 bar / 哪个时刻

### 3) 文案与字段解释同步升级

本轮还同步更新了：
- Best support / resistance 区块说明文字
- glossary 里的字段解释

特别新增了：
- `pointset_indeces / pointset_dates`
  - 用来把图上的白心圆点和表里的锚点信息直接对上

### 4) 回写 TODO

已将以下任务标记为完成：
- 给 support / resistance 表增加与图表对应的锚点信息列

## Validation / evidence

### A. 报告已成功重建并发布
执行：
- `/root/clawd/jerry/momentum/.venv/bin/python scripts/build_pytrendline_report.py`
- `./scripts/publish_report_site.sh`

结果：
- 页面已更新到：
  - `https://jp.jerrypsy.top/momentum/factors/pytrendline_research/report.html`

### B. 生成后的 HTML 已包含新字段

额外检查了生成后的 HTML，确认以下内容已存在：
- `pointset_indeces`
- `pointset_dates`
- `命中了哪些结构点`

说明表格层和文案层都已同步更新，不只是底层数据结构变了。

## Risks / caveats

- 当前表里的 `pointset_dates` 仍是紧凑串联形式，优先保证可读性；还没有做成更复杂的 tooltip / 可折叠显示。
- 若一条线命中点很多，表格会变长；当前还是偏研究页，不是极致压缩版 dashboard。
- 这轮没有新增新的图像，只是在结果表和字段解释层增强对照能力。

## Next recommended step

下一轮最值得做的小步动作：

1. **优先方案**：在 Step 1 的 pivots 图里补适度的 pivot index / 时间标签，让锚点从“图上有点”升级到“图上可定位”；
2. **次优方案**：补 `duplicate grouping before/after` 对照图，让“全部候选结果 -> best-from-group”这一步也能图形化对照。

## Commit hash (if committed)

ab7aadf04bf3f83fac0611bdebb4298df81dcd0c

## Commit note

本轮仍存在与 interval sweep / crypto rebound / reading pages 相关的其他脏文件，因此只会 selective commit 本轮的 pytrendline 报告与 TODO 文件，不打包无关改动。
