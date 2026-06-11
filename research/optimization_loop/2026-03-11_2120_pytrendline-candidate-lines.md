# PyTrendline 报告：补 candidate lines 生成口径与过滤逻辑说明

## Why this was chosen now

在 `pytrendline explainability` 主线里，pivot 讲清楚之后，下一步最自然就是 candidate lines。

因为对用户来说，光知道“有 pivots”还不够；更关键的问题是：
- 这些线到底是不是从所有 pivot 对里枚举出来的？
- 为什么最终页面里只剩几条代表线？
- `num_points` 到底在衡量什么？

所以这轮继续做 `A0-Calculation`：把 candidate lines 的生成与过滤逻辑写清楚。

## What changed

### 1) 在报告中新增候选线逻辑区块

文件：
- `scripts/build_pytrendline_report.py`

新增区块：
- `候选趋势线是怎么从 pivots 组合出来的`
- ``num_points` 应该怎么读`

### 2) 页面中明确写出的候选线生成口径

当前已补充这些关键点：

- **起点/终点从哪来**
  - 在当前配置下，start/end 都必须来自 pivots
  - 这是因为 `all_pts_must_be_pivots=True`

- **是不是所有 pivot 组合都会尝试**
  - 在当前配置下，源码会对满足条件的 pivot-pairs 逐个拟合一条线
  - 也就是说，候选线不是人工挑几条画出来，而是从 pivot pairs 系统枚举出来的

- **第一层过滤**
  - 先过滤 slope 与 last-price 明显不合理的线

- **第二层过滤**
  - 再扫描从起点到窗口末尾的 bars
  - 用 `max_allowable_error` 判断有多少点足够贴近这条线

- **最小命中数**
  - 当前要求 `num_points >= 3`
  - 所以 2 点就能画出的线不会进入最终结果

- **breakout 检测**
  - 如果价格越过线并超过 breakout tolerance，就会标成 breakout line

### 3) 把当前窗口下的“理论候选对数量”写出来

为了避免读者误以为页面里本来就只生成了几条线，本轮把当前窗口下的理论 pivot-pair 数量也写进了报告：
- support pivot pairs（理论上限）
- resistance pivot pairs（理论上限）

同时页面也写明：
- 这些 pair 只是候选起点；
- 后面还要经过 slope / last price / 命中点数 / breakout 等规则过滤；
- 所以最后保留下来的线数会远小于理论 pair 数量。

### 4) 补充 `num_points` 的阅读方式

本轮还单独解释了：
- `num_points` 不是交易次数
- 它更像“有多少个价格点足够贴近这条线”的结构支撑强度指标
- 为什么只用 2 点不够
- 为什么还需要 `score` 来区分同样命中数但误差不同的线

### 5) 回写 TODO

已将以下任务标记为完成：
- 单独解释 candidate lines 的生成口径
- 在报告里单独解释候选趋势线是怎么从 pivots 组合出来的

## Validation / evidence

### A. 报告已成功重建并发布
执行：
- `/root/clawd/jerry/momentum/.venv/bin/python scripts/build_pytrendline_report.py`
- `./scripts/publish_report_site.sh`

结果：
- 页面已更新到：
  - `https://jp.jerrypsy.top/momentum/factors/pytrendline_research/report.html`

### B. 页面现在已经能回答的核心问题

新增区块已经能直接回答：
- 候选线是不是从系统枚举的 pivot pairs 来的
- `all_pts_must_be_pivots=True` 在候选线阶段到底限制了什么
- `min_points_required=3` 在过滤阶段意味着什么
- 为什么页面最终只展示少量线
- `num_points` 应该如何解读

## Risks / caveats

- 这轮仍然没有补“candidate lines before filtering”的图示；现在是文字与数量解释先到位。
- duplicate grouping 的后半段压缩逻辑还没完全展开，因此读者虽然知道候选线如何进入“全部结果”，但还没完全看到“为什么最后只展示 best-from-group”。
- 当前理论 pair 数量是建立在当前窗口与当前 pivot 数上的，不应被误读成跨样本固定复杂度。

## Next recommended step

下一轮最值得做的小步动作：

1. **优先方案**：补 duplicate grouping 的计算与阅读方式，并说明 best-from-group 如何从“全部候选结果”压缩成“页面代表线”；
2. **次优方案**：补一张 `candidate lines before filtering` 的示意图，让文字规则与视觉结果直接对上。

## Commit hash (if committed)

1aef28a10c7eb49763c2e3056a283469d47330e1

## Commit note

本轮仍存在与 interval sweep / crypto rebound / reading pages 相关的其他脏文件，因此只会 selective commit 本轮的 pytrendline 报告与 TODO 文件，不打包无关改动。
