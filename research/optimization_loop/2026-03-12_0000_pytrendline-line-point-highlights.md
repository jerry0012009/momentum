# PyTrendline 报告：在 Step 2 / Step 3 中高亮代表线命中的结构点

## Why this was chosen now

在 `pytrendline explainability` 主线里，上一轮刚修完 Step 2 / Step 3 的“non-breakout 代表线”显示逻辑。

所以下一步最自然、最有价值的动作就是把这些代表线背后的结构点直接画出来：
- 不只是告诉用户“这是一条代表线”；
- 而是让用户一眼看到“这条线到底被哪些 pivots 支撑出来”。

这正对应 TODO 里的：
- `best line 命中的 pivot 点高亮图`

## What changed

### 1) 在 Step 2 / Step 3 中高亮 line pointset

文件：
- `scripts/build_pytrendline_report.py`

本轮新增：
- `_parse_index_list(...)`
- `_highlight_line_points(...)`

作用：
- 从每条展示线的 `pointset_indeces` 中提取结构点索引；
- 在 Step 2 / Step 3 的图里，直接把这些命中点标成白心圆点；
- support 用蓝线 + 白心圆点；
- resistance 用紫线 + 白心圆点。

### 2) Step 2 / Step 3 图注同步升级

本轮还同步改了图注，明确写出：
- 线上的白心圆点
- 就是这条线命中的结构点
- 读者应把它们和 Step 1 的 pivots 对照着看

### 3) 图例字典同步补充

报告里的图上元素字典现在新增了：
- `白心蓝/紫圆点`
  - 表示当前展示线命中的结构点（pointset pivots）
  - 用来说明这条线到底是由哪些点支撑出来的

### 4) 回写 TODO

已将以下任务标记为完成：
- 增加一张 `best line 命中的 pivot 点高亮图`

## Validation / evidence

### A. 报告已成功重建并发布
执行：
- `/root/clawd/jerry/momentum/.venv/bin/python scripts/build_pytrendline_report.py`
- `./scripts/publish_report_site.sh`

结果：
- 页面已更新到：
  - `https://jp.jerrypsy.top/momentum/factors/pytrendline_research/report.html`

### B. HTML 文案已同步到位

额外检查生成后的 HTML，确认以下新说明已存在：
- `白心圆点就是这条线命中的结构点`
- `白心蓝/紫圆点`

这说明页面不只是图上变了，文字解释也同步跟上了。

## Risks / caveats

- 当前高亮的是 `pointset_indeces`，但还没有把这些点的 index / timestamp 进一步回写到 support / resistance 表里。
- 若一张图里展示多条线，白心圆点有可能部分重叠；当前是优先保证“看得到”，还没有做更复杂的去重或分层标注。
- 这轮仍然是解释层改进，没有新增新的计算逻辑。

## Next recommended step

下一轮最值得做的小步动作：

1. **优先方案**：给 support / resistance 表增加锚点字段（`pointset_indeces / pointset_dates / breakout_index / breakout_date`），让图和表双向可对照；
2. **次优方案**：在 Step 1 的 pivots 图里补适度的 pivot index / 时间标签，让读者不用凭肉眼猜哪个圈对应哪组点。

## Commit hash (if committed)

58231a905956ec57c6f7ddebfb7c81a2c15af99f

## Commit note

本轮仍存在与 interval sweep / crypto rebound / reading pages 相关的其他脏文件，因此只会 selective commit 本轮的 pytrendline 报告与 TODO 文件，不打包无关改动。
