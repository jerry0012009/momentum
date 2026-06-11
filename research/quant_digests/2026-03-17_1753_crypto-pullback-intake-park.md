# 这条 crypto pullback 模板先别急着塞进 15m scout fast lane：规则像样，但 timeframe / exit / pyramiding 口径还不够诚实
- 时间：2026-03-17 17:53 UTC
- 类型：GitHub / repo source intake
- 主题标签：crypto/pullback/ema/stochrsi/repo/source-intake/scout
- 证据类型：repo source intake + 两条轻量诚实守门

## 1. 这次看了什么
这轮不是继续磨已有 P3，也不是回去做近义 writeback，而是按 `Run 2 / Scout Fast Lane` 补 1 条新的、更贴执行层的 `paper / repo based` source intake。

我对比了 3 条 fresh source：
1. `Crypto Pullback Trading Strategy Based on Stochastic RSI and EMA Crossover`（fmzquant repo）
2. `Efficient Price Channel Trading Strategy Based on 15-Minute Breakout`（fmzquant repo）
3. `Fixed Range Volume Profile + Anchored VWAP Trend Identification`（fmzquant repo）

当前 desk 语境下，边际价值排序是：
- **第一：crypto pullback / StochRSI + EMA** —— 最接近 `crypto + pullback + 可直接写规则`
- 第二：15m breakout —— 虽然是 15m，但核心锚点是 `9:15 first candle`，更像有明确开盘时段的市场，不适合 24/7 crypto
- 第三：FRVP + AVWAP —— 指标堆得太厚，source intake 阶段就已经带出明显的复杂度 / 参数层数 / 过拟合风险

所以本轮只正式认领第一条，并把它过到 intake-stage hard verdict。

## 2. 为什么这轮轮到它
- `EMA` 仍是 `waiting_not_due`，当前不能在 `Run 1` 空转；
- `Rank 17 / Rank 2 / Rank 29` 都是 `P3 continuity`，当前没有新的真实 `append/review need`；
- 本地 shortlist 基本被打穿，上一轮 `Rank 38` 也已被如实压回 `park / mechanism note only`；
- 因此这轮最该做的是：**从新的 repo source 里找 1 条更贴执行层、且能快速回答“值不值得进 replication queue”的候选。**

`crypto pullback / StochRSI + EMA` 在这几条里最像可以直接落成 `trade on / trade off` 的模板，所以它拿到本轮唯一主资源位。

## 3. 先把规则翻成人话
这条 source 的核心想法并不复杂：
- **long**：价格在 `EMA20` 上方，说明大方向偏多；但当前价格又回落到 `EMA9 / EMA14` 下方附近，同时 `StochRSI` 打到超卖，于是赌一次“顺大势的小回调结束”
- **short**：反过来，价格在 `EMA20` 下方，当前又反抽到 `EMA9 / EMA14` 上方附近，同时 `StochRSI` 打到超买，于是赌一次“顺大势的小反弹结束”

翻成人话就是：
**不是追涨杀跌，而是等顺势回调 / 反抽，再用快慢 EMA + StochRSI 过滤一次。**

## 4. 两条轻量诚实守门
### 4.1 `trade on / trade off` 能不能写清？
能，大体可以冻结成：
- **trade on（long）**：`close > EMA20`，且 `close < EMA9`、`close < EMA14`，并且 `StochRSI_K < oversold`
- **trade off（long）**：`close <= EMA20`，或价格并未处于 pullback 区，或 `StochRSI` 没有进 oversold
- short 端镜像处理

所以第一道门 **通过**：它不是纯机制故事，确实能写成具体触发条件。

### 4.2 有没有明显 `lookahead / repaint / data leakage`？
从 source 代码本身看：
- 只用了当下和过去 bar 的 `EMA / RSI / StochRSI`
- 没看到未来 bar、未来 extremum、或重绘型结构线
- 因此**没有一眼就能判死刑的 lookahead / repaint 问题**

所以第二道门也**基本通过**。

## 5. 真正卡住它的不是 repaint，而是 desk 口径不够冻结
虽然两条轻量诚实门没直接爆雷，但它还过不了当前 desk 的 fast-lane admission，核心有 3 个：

### 5.1 timeframe 口径不贴当前主线
source 自带 backtest 头里写的是：
- `period: 1d`
- `basePeriod: 1h`
- 标的是 `Futures_Binance / BTC_USDT`

这并不等于它不能迁到 15m，但它说明：
- **source 原始证据并不是按当前 desk 默认要的 `5m / 15m crypto` 口径给的**；
- 若下一步硬搬到 `BTC/ETH/SOL 120d 15m cache`，就已经不是“直接复刻”，而是**带着额外时间框架重解释**。

### 5.2 exit / hold 规则没有冻结
代码里只有 `strategy.entry`，没有把当前 desk 最关心的执行单元写死：
- 下一根开盘进？还是本 bar 收盘进？
- 持有几根 15m bar？
- 反向信号平仓还是允许无限叠加？
- 有无止损 / time stop / overlap 约束？

换句话说：
**它只把“什么时候想进场”讲了个大概，但没把“这到底是一笔什么交易”钉死。**

### 5.3 `pyramiding = 10` 让 clean replication 更容易走形
source 直接允许 `pyramiding = 10`。
这会带来一个很现实的问题：
- 同样的信号逻辑，在“单次离散交易”口径下可能是一回事；
- 在“允许连续加仓 10 次”的口径下，又是另一回事。

当前 desk 的 Scout Fast Lane 默认更偏向：
- 先做**可审计、可比对、单次交易单元清晰**的 clean replication
- 而不是一上来就把多次加仓、资金路径、叠单节奏混进来

所以它当前的 blocker，不是“信号看起来太笨”，而是：
**source 把 execution unit 写得太松，进入当前 fast lane 之前还要再补一层冻结。**

## 6. 为什么它仍然高于另外两条 fresh source
虽然这条最终还是 park，但它依然是这轮最该先看的新 source，因为：
- 相比 `15m breakout / 9:15 first candle`，它至少是 **crypto 语境**，不自带明显 session-mismatch；
- 相比 `FRVP + AVWAP + EMA + RSI + MACD + volume + ATR` 那种多层指标堆叠，它至少**规则更短、能先说清楚在干嘛**；
- 它暴露的主要问题不是复杂度失控，而是 **timeframe / exit / pyramiding freeze 还没补齐**。

也就是说：
它是这轮 fresh source 里**边际价值最高**的一条，
但这不等于它已经达到 **当前 fast-lane replication queue** 的 admission 标准。

## 7. 当前 hard verdict
### `Rank 39 / crypto pullback (StochRSI + EMA)`
- **当前 verdict：`park / source-template only`**
- **不进入**当前 `clean replication queue`
- **不进入**`paper candidate pool`

更直白地说：
- 它不是坏 source；
- 但当前更像一个“可以参考的入场模板”，
- 还不是一个已经足够冻结、可以直接丢进当前 `BTC/ETH/SOL 15m` fast-lane 里做诚实 clean replication 的候选。

## 8. 如果未来要重开，只允许补什么
若以后真要重开，默认只允许补 1 次最小冻结，不允许扩成大研究：
1. 固定到 `BTC/ETH/SOL 120d 15m` cache
2. 明确 `next-bar open` 还是 `close-to-close`
3. 明确 `hold N bars / reverse on opposite / no-overlap`
4. 先禁掉 pyramiding，做单次交易单元 clean replication

如果连这 4 步都没被明确冻结，就不该把它重新塞回 default Scout 预算。

## 9. 来源
1. fmzquant/strategies
   - `基于随机RSI和EMA交叉的加密货币回调交易策略Crypto-Pullback-Trading-Strategy-Based-on-Stochastic-RSI-and-EMA-Crossover`
   - raw: https://raw.githubusercontent.com/fmzquant/strategies/master/%E5%9F%BA%E4%BA%8E%E9%9A%8F%E6%9C%BARSI%E5%92%8CEMA%E4%BA%A4%E5%8F%89%E7%9A%84%E5%8A%A0%E5%AF%86%E8%B4%A7%E5%B8%81%E5%9B%9E%E8%B0%83%E4%BA%A4%E6%98%93%E7%AD%96%E7%95%A5Crypto-Pullback-Trading-Strategy-Based-on-Stochastic-RSI-and-EMA-Crossover.md
2. 对照 source
   - `Efficient Price Channel Trading Strategy Based on 15-Minute Breakout`
   - `Fixed Range Volume Profile And Anchored VWAP Trend Identification Strategy With Dynamic Stop-Loss`
