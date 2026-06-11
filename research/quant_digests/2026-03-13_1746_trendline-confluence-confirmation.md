# 趋势线不是画出来就算数：第三次触碰 + EMA/MACD 共识，才更像可执行的 breakout confirmation
- 时间：2026-03-13 17:46 UTC
- 类型：论文
- 主题标签：trendline / breakout / confirmation / support-resistance / trend
- 证据类型：论文全文（open-access PDF）
- 证据强度提示：**偏弱**（更像系统化案例研究 + 图表判读，不是大样本规则回测）

## 1) 这次看了什么
这次看的是：
- **Bartłomiej Wiśniewski (2024)**
- **Technical Analysis as a Tool for Determining Cryptocurrency Trends in Times of Chaos**
- Venue: **Ekonomia Międzynarodowa**
- DOI: **10.18778/2082-4440.46.01**

论文研究 2018–2023 年 **BTC / ETH 周频**，用三类最基础工具：**30-period EMA、MACD(12,26,9)、trendline**，去看在高波动与大事件（COVID、俄乌战争）下，这些工具如何识别趋势变化与进出点。

它不是严格的大样本交易规则比较，更像一篇**把“趋势线确认”说得比较明确**的案例论文：
- 趋势线是否成立，作者反复依赖 **第三个顶/底（third vertex / third peak / three lows）** 来确认；
- 单看 breakout 或单看 EMA/MACD 往往会出现**弱信号**或冲突；
- 更可靠的是 **趋势线结构 + EMA/MACD 同向** 的共识确认。

## 2) 核心结论
- **结论 1：趋势线不是“连两点就能交易”的信号，第三次触碰/第三个高低点才更像有效确认。**
  论文在 BTC/ETH 的 2019、2020、2023 段落里都把“第三峰/第三低点/three lows”当作趋势成立或切换的重要确认，而不是第一次 breakout 就直接下结论。
- **结论 2：单个指标经常互相打架；要降低假突破，更合理的做法是 trendline 结构确认后，再要求 EMA/MACD 共识。**
  论文在结论里明确写到：MACD、EMA、simple trendline 都可能有用，但**许多时候它们会给出 conflicting signals**；因此单独依赖一个指标有较大误判风险，多个指标同时使用更稳。

## 3) 论文是怎么支持这些结论的
### 样本与方法
- 资产：BTC/USD、ETH/USD
- 频率：**weekly**
- 时间：2018–2023
- 工具：
  - EMA 30
  - MACD (12,26,9)
  - 手工趋势线 / 支撑阻力线

### 文中最值得摘出来的细节
1. **趋势线确认反复依赖“第三个点”**
   - 作者多次写到某条趋势线是否成立，要看是否出现 **third peak / third vertex / three lows**。这很接近离散版的“结构确认”，而不是“边界被碰一下就算”。
2. **breakout 本身经常只是弱信号**
   - BTC 2019/2020 的案例里，论文提到 price breakout 出现后，MACD 往往只给出 **weak buy / weak sell**，说明“破线”不等于“信号已经足够强”。
3. **EMA/MACD 更像时序确认，不是结构本身**
   - 文中把 trendline 当作方向/结构框架；EMA 和 MACD 更像告诉你“这个结构变化有没有继续被价格动量确认”。
4. **结论部分明确强调 conflicting signals**
   - 论文结论写得很直白：这些工具在很多情况下提供了 valuable signals，但也**经常互相冲突**；因此最合理的不是依赖单一指标，而是使用更**multilayered analytical approach**。

## 4) 为什么这篇对当前 5m/15m 有价值
这篇最有价值的地方，不是它证明了某条趋势线系统“已被回测赚钱”，而是它把你当前在想的东西说得更具体了：

### A. 第三次确认，比“第一次突破”更像可执行规则
你最近一直在强化：
- breakout 后 1~3 根确认
- 阳线确认
- 回踩确认

这篇论文虽然是周频，但它给了一个很明确的结构启发：**两点先定义，第三点才确认。**
翻成 15m 语言就是：
- 先识别 candidate trendline / channel edge
- 不因第一次刺破就追
- 至少等到：
  - 第三次有效接触形成结构；或
  - breakout 后 1~3 根 bar 继续站在线外；或
  - 回踩线位/通道边界不失守

### B. EMA/MACD 不该负责“发现边界”，更适合做共识过滤
在很多策略里，容易把 EMA/MACD 当主信号。但这篇更像在提醒：
- **trendline / support-resistance** 负责定义结构边界
- **EMA slope / MACD cross** 负责做方向共识

这很适合你现在的工程拆分：
1. 结构层：trendline / channel / Donchian / opening range
2. 事件层：breakout / retest / pullback touch
3. 确认层：EMA 同向、MACD 不背离、1~3 bar persistence

### C. “弱突破”需要 persistence，不要只看瞬时穿越
论文里多次把一些 breakout 称作 slight breakout / weak signal。对 15m 很关键，因为短周期最容易被 wick 和噪声骗。最直接的映射就是：
- 不用 `high > line` 触发
- 改成 `close > line + τ`
- 再加 `2-of-3 closes outside`
- 或 `breakout -> retest -> hold`

## 5) 下一步怎么测（最小可执行实验）
### 目标
验证：在 crypto 15m 上，**trendline / channel breakout** 若加入“第三次结构确认 + EMA/MACD 共识过滤”，能否明显降低假突破。

### 最小实验设计
- 标的：BTC / ETH / SOL perpetual
- 周期：15m
- 样本：最近 180d ~ 365d

### 步骤 1：结构层
先做一个**近似趋势线**版本，避免纯手工主观性：
- 用 rolling pivots（例如 fractal high/low 或 zigzag）抽 swing points
- 至少 2 个 swing high / low 才画 candidate trendline
- **第三次有效接触**才把该 trendline 标记为 confirmed

### 步骤 2：事件层
做两类事件：
1. **trendline breakout**：`close > upper_line + τ` 或 `close < lower_line - τ`
2. **retest hold**：breakout 后回踩 trendline / channel edge 但重新收回有利方向

其中 `τ ∈ {0, 0.05 ATR, 0.1 ATR}`

### 步骤 3：确认层（对照组）
- A: 裸 breakout
- B: breakout + `confirm_1bar`（下一根仍在线外）
- C: breakout + `confirm_2of3`
- D: breakout + `EMA slope 同向`
- E: breakout + `EMA slope 同向 + MACD histogram 不反向`
- F: breakout + `retest_hold + EMA/MACD 共识`

### 最先看的指标
- `post_cost_return`
- `false_break_ratio`
- `outside_bar_persistence`
- `max_drawdown`
- `time_to_failure`（几根内又跌回线内）

### 我最建议先跑的最小子实验
如果只能先跑一个：
- **confirmed trendline + breakout + 2-of-3 closes outside + EMA slope 同向**
对照
- **unconfirmed line + first-cross breakout**

这个实验最直接回答：**“第三次确认 + 共识过滤”到底值不值。**

## 6) 风险与保留意见
- 这是 **周频 BTC/ETH 案例研究**，不是严格的 out-of-sample 规则回测；证据强度明显弱于大样本技术规则论文。
- 趋势线带有主观性，文中也主要通过图表解释，**可复现性一般**。
- 它最适合提供**结构设计启发**，不适合被表述成“论文已证明某趋势线策略可稳定赚钱”。
- 真正适合当前项目的做法是：**把它翻译成客观规则**（pivot、third-touch、close outside、retest hold、EMA/MACD filter），然后做 clean-room backtest。

## 7) 来源
1. Wiśniewski, B. (2024). *Technical Analysis as a Tool for Determining Cryptocurrency Trends in Times of Chaos*. Ekonomia Międzynarodowa, 46.
   - DOI: https://doi.org/10.18778/2082-4440.46.01
   - Readable URL: https://czasopisma.uni.lodz.pl/em/article/view/23156
   - PDF: https://czasopisma.uni.lodz.pl/em/article/download/23156/24343
