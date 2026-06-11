# Rank29 Postmortem (2026-04)

## 一句话结论

`Rank29` 当前这版定义，**不能再被视为“已验证有效”的策略**。

原因不是简单的“最近市场不适合它”，而是更根本的问题：

> 旧回测口径里，趋势线状态会被后续确认的 pivot **回填到历史 bars**，从而把一部分本来在当时并不可见的信号，事后改写成“看起来当时就能交易”的信号。

因此，`Rank29` 已在 2026-04-04 被正式降为：

- **P0 archived**
- **live timer disabled**
- 旧 `P3 / narrow paper` 结论全部撤销

---

## 这次到底发现了什么

### 1. 问题不是“图画得不清楚”，而是“信号定义本身不诚实”

最开始暴露问题的是多周期图：
- breakout 点和 trendline 看起来没有真正交汇；
- A/P 两个点不总是能解释清楚；
- 有些线看起来像是“先有信号，后有第二个点”。

后来继续往下查，发现这不是纯展示问题，而是**底层状态回填**：

- 未来才确认的 `pivot`
- 会改变更早 bars 上的：
  - `line_value`
  - `line_slope`
  - `active_pivot_origin`
  - `line_is_provisional`
  - 进而影响 `trend_score / composite trend`

这就会造成一种危险错觉：

> 某根历史 bar 在“当时真实世界”里其实还只是 provisional / 不可交易，
> 但在整段历史重算后，会被改写成“已经确认、而且满足条件”。

---

## 直接证据

### 例子：同一根 signal bar，在 hindsight 和 causal 视角下不是同一回事

在一个具体示例里（SOL 某个 signal bar）：

- **hindsight 视角**：
  - `short_trend = 1`
  - `medium_trend = 1`
  - `long_trend = 1`
  - `composite = 3`
  - 看起来像真多头信号

- **causal 视角**（只允许使用当时之前能看到的信息）：
  - `short_trend = 1`
  - `medium_trend = -1`
  - `long_trend = -1`
  - `composite = -1`
  - 根本不满足原本的多头准入门槛

也就是说：

> 同一根 bar，旧口径会把它算成“真信号”，
> 但严格 causal 口径下，它其实根本不是当时能诚实得到的交易机会。

---

## 复盘结果（strict-causal 重算后）

主样本：
- `Binance spot`
- `15m`
- `BTC / ETH / SOL`
- `120d`

### 主版本 `breakout_align_ge2`

#### 旧口径：`confirmed_line_only`
- `6bps / side`
- `mean_total_return ≈ +80.59%`
- `positive_asset_ratio = 100%`

#### 新口径：`causal_replay`
- `6bps / side`
- **0 笔交易**
- `positive_asset_ratio = 0%`

### 放宽版本 `breakout_align_ge1`

即便放宽到更容易出信号的版本：
- `mean_total_return ≈ -8.16%`
- `positive_asset_ratio = 0%`
- `false_break_ratio ≈ 45.5%`

结论很直接：

- 严格版本：**没有真实可交易信号**
- 放宽版本：**有信号，但整体不健康**

---

## 污染比例

按这次主样本审计：

- 旧口径信号：`449`
- strict-causal 真信号：`0`
- hindsight-only：`449`
- **误导比例：100%**

这说明不是“少量边角信号被污染”，而是：

> 在这轮主样本里，旧口径的核心结论本身就建立在 hindsight contamination 上。

---

## 这件事为什么重要

因为它会直接扭曲 4 种判断：

1. **会不会误以为策略已经验证过**
2. **会不会误把“事后长出来的信号”当成当时可下单的机会**
3. **会不会误把“实盘不成交”理解成执行问题，而不是信号定义问题**
4. **会不会在错误的基准上继续做优化（例如 gate / overlay / bucket）**

换句话说：

> 如果 baseline 本身就不诚实，后面再加 regime gate、paper overlay、时间稳定性、成本敏感性，都会建立在歪掉的地基上。

---

## 我们这次做了哪些修正

### 1. 底层支持 strict-causal 模式

现在 `trendline_breakout_navigator` 支持两种模式：

- `backfill_history = true`
  - 适合研究/可视化/事后解释
  - 允许把已确认结构回填到更早 bars
- `backfill_history = false`
  - **strict-causal baseline**
  - 不允许未来确认信息改写历史 bars

### 2. 回测基准切到 causal

`Rank29` 相关基准已经切到：
- `build_rank29_trades_baseline(...) = causal_replay`

### 3. 页面口径区分 causal vs hindsight-only

监控页里的星号已经分开：
- `★` = causal 真信号
- `☆` = hindsight-only（事后长出来）

### 4. Rank29 已归档

- live disabled
- P0 archived
- 仅保留作 audit / archive / historical reference

---

## 对后续 Rank 系列最有价值的教训

### 教训 1：不要只看“回测很漂亮”

必须先问：

> 这个 signal bar 在当时，真的能被算出来吗？

### 教训 2：凡是涉及 pivot / segment / trendline 的信号，都要先区分两种时间

一个点至少有两个时间：
- `origin time`：这个点落在哪根 bar
- `confirmed_at`：你什么时候才知道“它真的是这个点”

如果只画 `origin time`，很容易让人误以为它当时已经可用。

### 教训 3：所有结构型信号都应该至少保留两套口径

- `hindsight / explanatory`
- `strict-causal / tradable`

前者可以帮助理解图和结构；
后者才可以作为策略能不能推进的基准。

### 教训 4：overlay / gate / bucket 检查之前，先确认 baseline 是诚实的

顺序应该是：
1. baseline honesty
2. no-overlap honesty
3. cost sensitivity
4. time stability
5. regime overlay
6. paper / live admission

而不是反过来。

---

## 后续建议

### 对 Rank29

当前建议不是继续补 patch，而是二选一：

1. **重写信号定义**
   - 重新设计 causal 下也能自然产生信号的结构逻辑
2. **彻底封存旧版本**
   - 保留作 future-leak 反例教材

### 对后续 Rank 系列

以后凡是出现下面这些元素，都要默认触发 honesty audit：
- pivot confirmation
- trendline anchor / second-point update
- backfilled regime state
- post-hoc bucket stability
- 事后才知道的 label / state machine switch

---

## 相关页面 / 产物

### 审计页
- `rank29_monitoring_hub/report.html`
- `scout_rank29_trendline_breakout_navigator_15m/report.html`
- `scout_rank29_trendline_breakout_navigator_15m/no_overlap_honesty_check.html`
- `scout_rank29_trendline_breakout_navigator_15m/time_stability_check.html`

### 关键 artifacts
- `reports/artifacts/scout_rank29_trendline_breakout_navigator_15m/overall_summary.csv`
- `reports/artifacts/scout_rank29_trendline_breakout_navigator_15m/signal_honesty_summary.csv`
- `reports/artifacts/scout_rank29_trendline_breakout_navigator_15m/no_overlap_overall_summary.csv`
- `reports/artifacts/scout_rank29_trendline_breakout_navigator_15m/time_stability_overall_summary.csv`

---

## 最后一句备忘

以后再遇到“历史强、实盘弱、图上看着有信号但真实 runner 经常接不到”的策略，
**第一反应不要先怪执行层。**

先问这句：

> 这条信号，在当时那根 bar 上，真的是当时就能知道的吗？
