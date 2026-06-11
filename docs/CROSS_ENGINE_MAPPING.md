# Cross-Engine Mapping

> 目的：把 `PyIndicators` 与 `PyTrendline` 这两套不同的结构定义方式，映射到同一个 **Structure-Event Mainline** 里，避免把“定义引擎”误读成“研究主线”。

## 先给一句结论

- `PyIndicators` 和 `PyTrendline` 不是两个并列主 thesis。
- 它们是两个 **event source / definition engine**。
- 真正主线是：**这些结构事件本身，是否有 alpha / feature / confirmation 价值。**

因此：
- 主目录应该按 **Mainline → Engine Labs** 组织；
- 不是按“先选 PyIndicators 项目”或“先选 PyTrendline 项目”组织。

---

## 1. 两个引擎各自负责什么

### PyIndicators

更像：
- `active support / resistance` 的逐 bar 状态机
- 更容易生成：
  - active line
  - breakout
  - failed-breakout
  - rebound
  - confirmation-like state transition

它的强项：
- 更接近 **event generator**
- 更适合先做第一轮 event study / subset audit / confirmation ladder

它的弱项：
- 之前大量回测已经说明：**raw breakout 整体偏弱**
- 所以它不能再被默认当作最终 alpha thesis，只能先作为 baseline source

### PyTrendline

更像：
- pivot → candidate lines → filters → duplicate grouping → representative line 的静态/半静态结构解释器
- 更容易生成：
  - candidate line
  - representative line
  - breakout tag / breakout line
  - line quality / grouping / score

它的强项：
- 更适合做 **explainability baseline**
- 更适合解释“线是怎么来的、为什么保留这条线、不保留那条线”

它的弱项：
- 当前还没有像 PyIndicators 那样直接沉淀成系统性的 event-study source
- 它给出的 breakout 语义，与 active-line state machine 的 breakout 语义 **不能直接视为同一个对象**

---

## 2. 哪些概念可以对齐，哪些不能硬对齐

### 2.1 可以对齐的上位概念

这几个上位概念可以先放进 unified event schema：

- `source_engine`
- `symbol`
- `timeframe`
- `line_side`（support / resistance）
- `event_timestamp`
- `event_type`
- `confirmation_level`
- `line_quality_bucket`
- `slope_bucket`
- `sample_scope`

这些是 **mainline 可复用字段**。

### 2.2 不能直接硬对齐的对象

以下对象不能直接假装相同：

- `PyIndicators active line`
  vs
  `PyTrendline representative line`

- `PyIndicators breakout`
  vs
  `PyTrendline breakout tag`

- `PyIndicators rebound`
  vs
  `PyTrendline line-touch rejection`

原因不是名字不同，而是：
- 它们的检测时点不同
- 它们依赖的历史上下文不同
- 它们对 line lifecycle 的定义不同
- 它们是否允许事后 grouping / best-line selection 也不同

所以统一时，应该先统一到 **event family**，而不是直接统一到底层 engine object。

---

## 3. 推荐的 unified event schema（草案 v0）

下面这组字段，适合先作为跨引擎最小公约数。

### 3.1 必备通用字段

- `source_engine`
  - `pyindicators`
  - `pytrendline`
  - future: `parallel_channel` / others

- `event_family`
  - `breakout`
  - `rebound`
  - `touch`
  - `switch`

- `event_subtype`
  - 例如：
    - `raw_breach`
    - `close_confirm_same_bar`
    - `confirm1`
    - `confirm3`
    - `retest_hold`
    - `wick_rejection`
    - `touch_close_back_inside`

- `line_side`
  - `support`
  - `resistance`

- `event_timestamp`
- `symbol`
- `timeframe`
- `sample_key`

### 3.2 建议的 line context 字段

- `engine_line_id`
- `line_origin_type`
  - `active_line`
  - `representative_line`
  - `group_best_line`
  - future others

- `line_quality_bucket`
- `slope_bucket`
- `is_representative`
- `num_points_bucket`
- `score_bucket`

### 3.3 建议的 confirmation / state 字段

- `confirmation_level`
- `is_provisional`
- `is_confirmed`
- `bars_since_first_cross`
- `bars_since_touch`

### 3.4 当前不建议强行统一的字段

这些字段先允许 engine-specific：

- `duplicate_group_id`
- `pytrendline_score`
- `is_best_from_duplicate_group`
- `navigator_state`
- `active_line_start_bar`
- `active_line_reset_reason`

做法应该是：
- 保留在 source artifacts 里
- 但不要一上来就要求所有 engine 都必须产出

---

## 4. 一个实用的映射方式：先做“两层翻译”

推荐不要直接：
- engine raw object → final strategy label

而应该分两层：

### Layer 1. Engine-native object

由各自引擎负责：
- PyIndicators: active line / state transition / breakout / rebound
- PyTrendline: candidate line / representative line / breakout tag / group info

### Layer 2. Mainline event object

统一翻译成：
- `event_family`
- `event_subtype`
- `confirmation_level`
- `line context`
- `quality / slope buckets`

这样好处是：
- engine 差异不会被粗暴抹平
- mainline 仍然可以做统一比较
- 后续加入 `parallel channel` 也更容易

---

## 5. 当前最合理的项目组织落点

### Mainline 放什么

- `Momentum TODO / Roadmap`
- `Trendline Event Research Plan`
- `Trendline Event Foundation Report`
- `Trendline Event Slope Audit`
- `Trendline Confirmation Ladder Report`
- 本文：`Cross-Engine Mapping`

### Engine Lab · PyIndicators 放什么

- `Trendline Breakout Navigator`
- `Trendline Segment Backtest`
- `Interval Sweep`
- `Cross-Market`
- `Rebound Scan`

### Engine Lab · PyTrendline 放什么

- `PyTrendline Research Report`
- 后续如有：PyTrendline event-source bridge / schema export / source audit

---

## 6. 这页最重要的阅读结论

### 结论 1

以后不要再问：
- “这是 PyIndicators 项目还是 PyTrendline 项目？”

更应该问：
- “这是 Mainline 的问题，还是某个 Engine Lab 的问题？”

### 结论 2

- `PyIndicators` 当前更像 **first event-study source**
- `PyTrendline` 当前更像 **explainability baseline**
- 二者都不是默认终局

### 结论 3

下一步真正该做的不是继续混淆目录，而是：
- 让 `PyTrendline` 也能输出一版最小 event-source sample
- 然后把它接进 mainline 的 unified event schema

---

## 7. PyIndicators mapping v1（当前哪些字段已经能接 unified schema）

这轮先补 `B2-C` 里一个很具体、但一直缺少明确落点的问题：

> `PyIndicators` 现有产物里，哪些字段其实已经足够接到 unified event schema，哪些还没有？

当前最可审计的 3 份输入分别是：

- `reports/artifacts/trendline_segment_backtest/segment_strategy_events.csv`
- `reports/artifacts/trendline_segment_backtest/navigator_segments.csv`
- `reports/artifacts/trendline_confirmation_ladder/trade_detail.csv`

这 3 份文件合在一起，已经足够明确：`PyIndicators` **不是完全没有 schema bridge**，而是**已经有一批核心字段，只是仍混着 execution 语义**。

### 7.1 已经有明确落点的 unified 字段

如果当前先以 `trade_detail.csv` 作为 confirmation-aware 主样本、再用 `segment_strategy_events.csv` / `navigator_segments.csv` 补 detection 语义，那么下面这些字段已经有明确映射：

- `source_engine`
  - 当前可直接写成常量：`pyindicators`

- `sample_key`
  - 直接来自：`trade_detail.sample_key`
  - 当前样本里已含 `60m_365d` / `60m_730d`

- `symbol`
  - 直接来自：`symbol`

- `timeframe`
  - 当前可先保留 engine horizon label：`short / medium / long`
  - 若需要外部实验窗口，则同时读 `sample_key` / `interval`

- `event_family`
  - 直接来自：`strategy` 或 `strategy_event`
  - 当前已稳定分成：`breakout` / `rebound`

- `line_side`
  - 直接来自：`side_label`
  - 当前已稳定分成：`support` / `resistance`

- `event_timestamp`
  - confirmation-aware 视角：优先用 `signal_ts`
  - detection-aware 视角：回退到 `candidate_ts`
  - 这说明 `PyIndicators` 已经不是“完全没有事件时间戳”，而是**同时存在 detection 与 confirmation 两种时点**

- `engine_line_id`
  - 当前可直接用：`segment_id`
  - 它更像 active-line segment handle，而不是 PyTrendline 式的静态 line id

- `line_origin_type`
  - 当前可先固定为：`active_line`

- `confirmation_level`
  - 直接来自：`ladder_label`
  - breakout 侧当前已有：`breakout_hold_1/2/3/4`
  - rebound 侧当前已有：`rebound_inside_0/1/2/3`

- `is_provisional`
  - 直接来自：`segment_is_provisional` / `is_provisional`

- `slope_bucket`
  - 直接来自：`slope_bucket`
  - 同时已有 `slope_sign` 与 `slope_magnitude_bucket` 可追溯

### 7.2 已经接近可用、但当前仍需派生的字段

这些字段并不是完全没有，只是还没有以最终 mainline 口径单独导出：

- `event_subtype`
  - 当前可由 `event_type` + `ladder_type` + `ladder_label` 派生
  - 例如把 `breakout_long / breakout_hold_2` 归到 `breakout / confirm2-like`

- `is_confirmed`
  - 当前可由 `ladder_label`、`confirm_bars`、`breakout_confirm_bars_cfg` / `rebound_confirm_bars_cfg` 派生

- `bars_since_first_cross`
  - breakout 侧已有近似信息：`confirm_bars` / `breakout_confirm_bars_cfg`

- `bars_since_touch`
  - rebound 侧已有近似信息：`rebound_confirm_bars_cfg`

- `sample_scope`
  - 当前可由 `sample_key + interval + period` 组合得到
  - 只是还没被单独沉淀成统一字段

### 7.3 当前仍然缺失、或不应硬补的字段

下面这些字段要么当前没有，要么不应为了“强行对齐”而假造：

- `line_quality_bucket`
- `num_points_bucket`
- `score_bucket`
- `is_representative`
- `duplicate_group_id`
- 与 execution 解耦后的 **full event-universe rows**

这也解释了为什么：

- `PyIndicators` 现在已经足够做 **confirmation protocol source #1**；
- 但它还不能被误读成“已经有一份干净的 unified event-source export”。

## 8. PyTrendline mapping v1（当前已落地的最小 bridge）

本轮已经把 `pytrendline_research` 现有产物翻译成一版最小 event-source bridge：

- 样本文件：`outputs/research/pytrendline_event_sample.csv`
- 网页入口：`reports/site/factors/pytrendline_event_source/report.html`

### 8.1 v1 具体怎么映射

当前 v1 的做法是：

- 输入来源：
  - `reports/artifacts/pytrendline_research/support_trendlines.csv`
  - `reports/artifacts/pytrendline_research/resistance_trendlines.csv`
- 只取：
  - `is_best_from_duplicate_group == True` 的 representative lines 作为默认样本
- 最小映射规则：
  - `engine_line_id` ← `id`
  - `line_side` ← `SUPPORT / RESISTANCE`
  - `line_origin_type` ← `group_best_line`
  - `event_family` ← `is_breakout ? breakout : touch`
  - `event_subtype` ← `breakout_tagged_line / line_touch_candidate`
  - `event_timestamp` ← breakout 用 `breakout_date`，否则退回 `ends_at_date`
  - `line_quality_bucket` / `score_bucket` ← 当前样本内 `score` 分位数分桶
  - `slope_bucket` ← 当前样本内 `slope` 方向 + 强度分桶

### 8.2 v1 明确没覆盖什么

这版 bridge 还没有覆盖：

- 完整的 `rebound` 语义
- `retest_hold` / `confirmed switch` 一类更强事件状态
- 多 symbol / 多 sample 的统一输出
- 与 `PyIndicators` 一样细的逐 bar state transition

所以它当前的定位应是：

- **足够进入 unified schema 比较**
- **还不足够直接进入完整 event validation 终局**

## 9. 下一步建议

1. 先把 `PyIndicators` 这批已存在字段单独导出成一份更干净的 baseline event-source sample
   - 只保留 detection / confirmation / line context
   - 不再把 trade execution 字段混在同一层

2. 把 `PyTrendline v1` 再推进一格：
   - 明确 representative only vs all valid 两种输出口径
   - 单独标记 breakout-only 与 non-breakout candidate

3. 再做第二轮更严格的 source 对照：
   - 同一资产 / 周期下
   - 尽量同样窗口、同样 bucket
   - 比较 `PyIndicators source vs PyTrendline source` 谁更像可继续的事件来源
