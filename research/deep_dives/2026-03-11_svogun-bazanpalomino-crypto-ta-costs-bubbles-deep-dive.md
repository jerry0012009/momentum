# Deep Dive — Svogun, Bazán-Palomino (2022): Technical analysis in cryptocurrency markets: Do transaction costs and bubbles matter?

- 时间：2026-03-11
- 类型：论文精读
- 主题标签：crypto / technical-analysis / breakout / transaction-cost / bubble / regime
- 当前相关性：高

## 1. 为什么这篇值得你现在认真看

如果你现在研究的是：
- 平行通道
- 支撑阻力
- 趋势线突破
- breakout 后 1~3 根确认

那么你迟早会遇到一个非常现实的问题：

> 这些规则在图上看起来不错，但扣掉手续费、滑点和市场状态变化之后，还剩多少？

这篇论文最值钱的地方就在这里：

**它不是问“技术分析有没有用”，而是问“在 crypto 里，扣掉成本、再考虑泡沫阶段之后，还剩多少用”。**

这比很多泛泛的技术分析论文更贴近落地。

## 2. 论文到底研究了什么

基于当前可获取的元信息和项目内已产出 digest，这篇论文的核心框架可以概括为：

- 研究对象：加密货币市场
- 规则集合：参数化技术规则（包括 moving average / breakout 家族）
- 频率覆盖：至少包含超短频和更低频对照（项目内 digest 里已记录 1-min 与 1-day）
- 关键比较：
  1. 不计成本 vs 计入成本
  2. 非泡沫 vs 泡沫阶段

它要回答的不是“有没有某个神奇指标”，而是：
- 成本对技术规则的侵蚀有多大
- 市场状态（尤其泡沫期）会不会改变技术规则的有效性

## 3. 这篇论文最重要的三层启发

### A. 纸面 alpha 和可交易 alpha 不是一回事
这点对你尤其重要。

很多 breakout / channel / support-resistance 策略会有一个典型问题：
- 频率越高，看起来有效机会越多
- 但频率越高，交易成本越容易把 edge 吃干净

也就是说，
**如果你后面做 15m 甚至更短周期结构突破，必须从第一天就把成本后指标当主指标。**

### B. 并不是所有技术规则都会被成本完全杀死
这篇论文的价值不只是“泼冷水”。

更细的结论是：
- 成本会让很多规则显著缩水；
- 但并不是所有规则都因此失效。

这给你的现实启发是：

> 不要因为“很多规则扣成本后变差”就直接放弃 breakout 类研究；
> 你该做的是筛出在成本后仍能站住的结构规则。

### C. 市场状态会改写规则表现
bubble periods matter 这点非常关键。

对你当前研究“通道突破 / 阻力位突破”尤其重要，因为：
- 有些突破在趋势狂热阶段更容易延续；
- 有些突破在高泡沫、高拥挤阶段更容易变成 chase top；
- 有些 confirmation 在高噪音阶段只是拖慢入场。

所以：
**breakout 不应该被当作静态规则，而应该与 regime / bubble proxy 联合研究。**

## 4. 这篇论文怎么映射到你当前的研究问题

### 4.1 对“平行通道突破”有什么启发？
这篇论文不会直接教你怎么画平行通道，但它会给你一条硬约束：

- 不要只问通道识别对不对
- 要问“通道突破信号在扣成本后是否还值得交易”

### 4.2 对“阻力位突破后的几根阳线确认”有什么启发？
confirmation 的本质是：
- 降低假突破
- 但也会降低进场速度
- 从而改变交易次数、平均收益、成本暴露

这篇论文支持你这样看 confirmation：

> 它不是纯粹为了让图更好看，而是一个“成本后存活率过滤器”。

### 4.3 对“什么时候该怀疑自己的 breakout 逻辑”有什么启发？
如果你的 breakout 规则满足下面任一特征，就要特别警惕：
- 超高换手
- 小利润依赖极多交易
- 过于依赖 intrabar 突破
- 大量收益来自少数极端行情窗口

这些都容易在成本或 regime 切换后失效。

## 5. 你现在最该怎么复用这篇论文

### 方法 1：所有 breakout 策略默认做 gross/net 双报告
至少同时输出：
- `gross_return`
- `post_cost_return`
- `turnover`
- `trade_count`

### 方法 2：对 breakout 策略做 regime slice
哪怕你现在不完整实现 PSY 泡沫识别，也至少要做轻量代理切片，例如：
- 价格相对中长均线偏离程度
- realized volatility expansion
- trend persistence score

### 方法 3：把 confirmation 也当作成本控制工具来研究
例如比较：
- 裸 breakout
- 1 根收盘确认
- 2 根收盘确认
- 回踩确认

然后看哪一种虽然机会少一点，但 net performance 更稳。

## 6. 对当前项目的具体实现建议

如果我把这篇论文直接翻译成 `momentum` 项目待办，我会这样排：

### A. breakout baseline
- 用现有 `ema_donchian_breakout` 做基础模板

### B. confirmation variants
增加 3 组开关：
- `confirm_close_bars = {0,1,2}`
- `confirm_retest = {False, True}`
- `confirm_volume = {False, True}`

### C. cost ladder
每次报告默认跑：
- `low_cost`
- `mid_cost`
- `high_cost`

### D. regime split
至少先按以下代理切片：
- `trend_strength`
- `volatility_state`
- `distance_from_slow_ma`

## 7. 一个非常具体的最小实验

### 实验题目
**15m 阻力位突破：confirmation 是降低假突破，还是只是延迟入场？**

### 设计
#### 资产
- BTC, ETH, SOL

#### 周期
- 15m

#### 触发
- `close > upper_channel` 或 `close > rolling_high(20)`

#### 对照组
1. 裸 breakout
2. breakout + 1 根收盘确认
3. breakout + 2 根收盘确认
4. breakout + 回踩确认

#### 成本
每组都跑：
- gross
- net_low
- net_high

#### 先看
- `post_cost_return`
- `positive_window_ratio`
- `trade_count`
- `max_drawdown`

### 你真正想回答的问题
不是“谁收益最高”，而是：

> 哪种 breakout confirmation 在 15m crypto 上，扣成本后仍能减少假突破，而不是把 edge 全拖没。

## 8. 这篇论文的局限

- 它不是专门研究“平行通道突破后两根阳线确认”的。
- 它给你的不是细参数答案，而是一个很强的现实约束：
  - **成本与 regime 是 breakout 研究不能绕开的。**
- 你不能拿它直接当“某个 confirmation 必然有效”的证据。

## 9. 我对这篇论文的最终使用建议

如果只让我从这篇论文拿走一句最值钱的话，我会写成：

> 所有结构型 breakout alpha，从第一天开始就必须在成本后与市场状态条件下评估，否则研究结果大概率偏乐观。

## 10. 来源
- Svogun, D., & Bazán-Palomino, W. (2022). *Technical analysis in cryptocurrency markets: Do transaction costs and bubbles matter?* Journal of International Financial Markets, Institutions and Money.
- DOI: <https://doi.org/10.1016/j.intfin.2022.101601>
- Readable URL: <https://doi.org/10.1016/j.intfin.2022.101601>
- 项目内短卡：`research/quant_digests/2026-03-10_1838-crypto-technical-analysis-costs-bubbles.md`
