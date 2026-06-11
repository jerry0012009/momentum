# SIGNALS_TRENDLINE_BREAKOUT_NAVIGATOR

一个基于 clean reimplementation 的趋势线突破研究模块。

## 当前定位
- 正式放在 `momentum` 代码仓库里
- 但当前仍应视为 **research-grade signal module**
- 作用是把“学习到的 breakout 逻辑”重写成我们自己的代码，而不是搬运原实现

---

## 来源边界

### 这份模块不是直接复制外部源码
它的逻辑路径参考了外部 breakout navigator 的思路：
- confirmed pivot highs / lows
- HH / LL 触发趋势切换
- 从 swing low / swing high 锚定 active trendline
- 跟踪 line value / line slope / wick break / composite trend

但实现是本仓库重写：
- 自己的命名
- 自己的状态机
- 自己的测试
- 自己的数据输出结构

### 为什么不直接搬外部 breakout 文件
因为之前审计到外部 breakout navigator 文件头带有：
- LuxAlgo attribution
- CC BY-NC-SA 4.0 / analytical use only 语义

所以这次采取：
- 学逻辑
- 重实现
- 自己审计

---

## 模块做了什么

### 输入
- `timestamp`
- `high`
- `low`
- `close`
- 可选 `symbol`

### 配置
- `swing_long`
- `swing_medium`
- `swing_short`
- `swing_right`
- `min_pivot_gap`
- enable flags
- `backfill_history`
  - `true`：允许在后续 pivot 确认后，把 line / slope / pivot state 回填到更早 bars；适合研究解释和图表
  - `false`：strict-causal，不允许未来确认信息改写历史 bars；适合作为可交易 baseline

### 输出
按三个 swing 长度分别输出：
- `tbn_long_trend` / `tbn_medium_trend` / `tbn_short_trend`
- `*_line_value`
- `*_line_slope`
- `*_line_side`（`+1=support`, `-1=resistance`, `0=none`）
- `*_anchor_origin` / `*_anchor_price`
- `*_active_pivot_origin` / `*_active_pivot_price`
- `*_line_is_provisional`
- `*_pivot_high_price` / `*_pivot_low_price`
- `*_pivot_high_origin` / `*_pivot_low_origin`

聚合输出：
- `tbn_wick_bull`
- `tbn_wick_bear`
- `tbn_breakout_bull`
- `tbn_breakout_bear`
- `tbn_hh`
- `tbn_ll`
- `tbn_composite_trend`
- `tbn_signal`

## Segment state（工程化收尾）
除了 bar-state 输出，当前还支持显式 segment state：
- helper: `extract_trendline_breakout_segments(...)`
- 每条线段都会记录：
  - `segment_id`
  - `timeframe`（long/medium/short）
  - `start_bar` / `end_bar` / `bars_visible`
  - `side` / `side_label`
  - `anchor_origin` / `anchor_price`
  - `pivot_origin` / `pivot_price`
  - `slope`
  - `is_provisional`
  - `end_reason`（`breakout` / `pivot_update` / `trend_switch` / `window_end`）

---

## 逻辑概述

### 1. pivot 检测
- 使用 left/right bars 规则确认 pivot high / low
- 只有在确认 bar 才写入 pivot 信息

### 2. 趋势切换
- 当新的 pivot high 高于上一个 pivot high，且满足最小间隔条件，可触发 `HH`
- 当新的 pivot low 低于上一个 pivot low，且满足最小间隔条件，可触发 `LL`

### 3. active trendline
- `HH` 后，从上一个 pivot low 启动 bullish support line
- `LL` 后，从上一个 pivot high 启动 bearish resistance line
- 当前已对齐到更接近 `PyIndicators` 原版的行为：
  - `HH / LL` 刚出现时，先生成一条 **水平的 provisional line**
  - 不是立刻拿 `HH bar low` / `LL bar high` 去算斜率
  - 需要等后续同侧 pivot（bullish 看后续 pivot low，bearish 看后续 pivot high）出现后，才把线更新成真正的斜线
- 为了让 report 能解释“这条线到底连哪两个点”，当前额外暴露：
  - `*_line_side`：当前线是 support 还是 resistance
  - `*_anchor_*`：线的起点
  - `*_active_pivot_*`：当前真正用于定斜率的第二个 pivot
  - `*_line_is_provisional`：是否还处于“只有 anchor、尚未等到第二个 pivot”的水平占位阶段

### 4. breakout / wick interaction
- 价格收盘穿过 active line 时，trendline 失效
- 当前仓库里已把这种“真突破”显式落成：
  - `tbn_breakout_bear` = close 真正跌破 active support line
  - `tbn_breakout_bull` = close 真正站上 active resistance line
- 后续 pivot 相对当前线的互动会记录为 wick bull / wick bear：
  - `tbn_wick_bull` 更接近支撑被测试后守住 / rebound
  - `tbn_wick_bear` 更接近压力被测试后压回 / rejection
- 因此这里的 `wick bull / wick bear` 更接近“线已存在后的 wick interaction / false break”，而不是任意一根 K 线的简单上下影线判定

### 4.1 重要提醒：图表解释口径 ≠ 可交易口径

`trendline_breakout_navigator` 现在明确支持两种模式：

- `backfill_history = true`
  - 用途：解释结构、画图、做 hindsight audit
  - 特点：后续确认的 pivot 可以把 line / slope / pivot state 回填到历史 bars
- `backfill_history = false`
  - 用途：strict-causal baseline
  - 特点：未来确认的信息不会改写更早 bars

后续凡是拿这个模块去做策略晋级、paper / live admission、成本/稳定性评估，**默认必须先看 `backfill_history = false` 的结果**。

不要把：
- hindsight 图形更完整
- 结构解释更顺
- 事后状态更漂亮

误读成：
- 这些信号当时也一定可交易

### 5. composite trend
- 三个 timeframe trend 相加
- 再映射到 `tbn_signal ∈ {-1,0,1}`

---

## 当前和 `pytrendline` 的关系

- `pytrendline`：更偏趋势线搜索 / scoring / breakout 研究
- `trendline_breakout_navigator.py`：更偏逐 bar 状态机 / 多 swing 组合

两者不是完全替代关系，
当前更适合并排研究，而不是二选一。
