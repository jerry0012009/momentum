# 别把这篇 2025 JFM + 开源 repo 只读成“又一个 pairs 教程”：对 short-cycle desk，更该先测的是「cointegration spread z-score × optimized lookback × volatility veto × adaptive trailing stop」这条完整 pairs raw alpha
- 时间：2026-04-02 04:05 UTC
- 类型：2025 *Journal of Futures Markets* 论文摘要 metadata + 2025 GitHub repo source audit（`README.md` + `pairs_trading_strategy.R` + GitHub API metadata）
- 主题类型：raw alpha
- 基础 alpha：当两条高度相关、可协整的 crypto 价格序列暂时偏离各自的长期均衡关系时，偏离过大的 spread 往往有回归压力；alpha 本体是 **cointegration spread mean reversion**，不是 trailing stop，也不是 volatility filter。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/cointegration/zscore/lookback-optimization/volatility-filter/trailing-stop/min-holding/market-neutral/crypto/15m/5m/3m/1m/paper/repo/public-data/cost
- 证据类型：2025 GitHub repo source audit（主证据）+ Crossref/Wiley 论文 metadata 与 abstract（辅助证据，非全文）

## 1. 这次看了什么
### 一句话核心结论
**这轮更值得 intake 的，不是“再看一个 BTC/ETH pairs notebook”，而是一条已经把 `entry / hedge ratio / risk / exit / cost` 都写进开源代码的完整 raw alpha：用协整 spread 的 z-score 做均值回归入场，再叠 lookback 优化、波动 veto、最短持有期与动态 trailing stop。**

### 一句话它是怎么证明的
**主证据不是论文 headline，而是 repo 把策略骨架完整写在 `pairs_trading_strategy.R` 里；论文 abstract 只负责提供样本背景与作者正式发表的研究定位。**

## 2. base alpha 是什么
这次的 **base alpha 很清楚**：

1. 先在两条价格序列之间估一个长期关系：`y1 = μ + γ*y2 + ε`；
2. 用 `spread = y1 - γ*y2` 表示“这对资产当前偏离长期关系有多远”；
3. 再把 spread 做成 rolling z-score；
4. 当 `z <= -threshold` 时做多 spread（多低估腿、空高估腿），当 `z >= +threshold` 时做空 spread；
5. 等偏离回归、结构失效，或风险层触发时退出。

翻成人话：**它不是赌某个币自己会涨或会跌，而是赌“一对本来应该走得比较像的资产，短时间被拉开太远后，会向中间收敛”。**

所以这篇东西的定位非常明确：
- 方向属性：**相对价值 / 市场中性**
- 基础 alpha：**协整 spread 的均值回归**
- regime / filter：**spread 自身波动是否过高**
- risk / execution overlay：**最短持有期 + 动态 trailing stop + 交易成本**

## 3. 为什么这轮值得写
- 当前项目自己的学习地图和 backlog 还偏向 **trend / breakout / pullback / ATR / volume** 这条主线；但 bot7 当前明确要求持续补齐 **mean reversion / relative value / stat-arb / pairs** 的 raw alpha 素材池，这篇正好补的是这块空白。
- 最近 intake 里虽然也有 pairs 主题，但很多更像“某个 threshold / 某个 gate / 某个外部 filter”的拼装；这篇不同的地方在于：**它已经是一张完整策略卡，而不是只给一个 entry 想法。**
- 公开材料足够复现：
  - 有正式论文 DOI；
  - 有开源 repo；
  - 有公开数据 DOI（Mendeley Data）；
  - 代码里把 hedge ratio、lookback、risk、成本都写明了。

如果按当前 desk 的优先级来排，这篇的价值在于：**它不是在给已有 alpha 加一个附属过滤器，而是在给 raw alpha 池补一条可直接落地的 market-neutral 均值回归骨架。**

## 4. 来源信息
### 论文来源
- **Author：** Rafael Baptista Palazzi
- **Year：** 2025
- **Title：** *Trading Games: Beating Passive Strategies in the Bullish Crypto Market*
- **Venue：** *Journal of Futures Markets*
- **DOI：** <https://doi.org/10.1002/fut.70018>
- **Readable URL：** <https://onlinelibrary.wiley.com/doi/10.1002/fut.70018>
- **目前拿到的证据层级：** Crossref metadata + abstract；Wiley 正文页被 Cloudflare challenge 挡住，**本轮不是全文阅读**。

### 工程来源
- **Repo owner：** `rafaelpalazzi`
- **Year：** 2025（repo created `2025-12-20T01:59:21Z`）
- **Title：** `trading-games-crypto`
- **Venue：** GitHub repository
- **Repo URL：** <https://github.com/rafaelpalazzi/trading-games-crypto>
- **Core file：** <https://raw.githubusercontent.com/rafaelpalazzi/trading-games-crypto/main/pairs_trading_strategy.R>
- **GitHub metadata：** stars `3`，default branch `main`，latest update `2026-02-14T11:07:46Z`

### 数据来源
- **Dataset：** *Trading Games: Beating Passive Strategies in the Bullish Crypto Market* [Dataset]
- **Venue：** Mendeley Data
- **DOI：** <https://doi.org/10.17632/2kky7c6xkn.1>

## 5. repo 具体是怎么把这条 alpha 写出来的
### 5.1 Hedge ratio 与 market-neutral sizing 都是显式的
代码先在训练集上用 OLS 估：
`Y1 ~ Y2`

然后得到：
- `μ`：截距
- `γ`：hedge ratio

接着把组合权重写成：
`w_ref = (1, -γ) / (1 + |γ|)`

这一步很重要，因为它不是“等权多一个、空一个”，而是先把两腿缩成一个**归一化 spread 组合**。对 desk 来说，这直接回答了一个关键问题：**这篇不是只会喊 entry，它连配对仓位怎么摆都给了。**

### 5.2 Entry 不是拍脑袋，而是 z-score 均值回归
repo 的信号层非常朴素：
- `Z_score <= -threshold_long` → `signal = 1`
- `Z_score >= +threshold_short` → `signal = -1`
- 否则 `signal = 0`

默认 `threshold_value = 0.7`。

也就是说，这个系统的核心不是“预测谁更强”，而是：
**spread 偏得太离谱了，就押它往回收。**

### 5.3 它不是固定 lookback，而是先在训练集上找最合适的 spread 记忆长度
代码会在训练集里扫描：
- `lookback_periods = 5, 10, 15, ... , 360`

然后对每个 lookback：
- 计算 spread rolling mean / rolling std；
- 生成 z-score；
- 生成交易收益；
- 用 `SharpeRatio.annualized` 选出最优 lookback。

这点对我们很有价值，因为它不是把“20 日 / 60 日”当教条，而是在明确问：
**这对 spread 的均值回归速度，到底更像短记忆还是长记忆？**

## 6. risk / filter / exit 层里最值得 desk 偷走的东西
### 6.1 波动 veto：不是所有 spread 偏离都值得接
repo 先算：
- `spread_return = diff(spread)`
- `spread_vol = rolling_sd(spread_return, vol_lookback)`

默认参数：
- `vol_lookback = 30`
- `vol_threshold = 1.5`

然后只在：
`spread_vol <= 1.5 × average_spread_vol`
时允许信号生效。

翻成人话：**如果这对 spread 已经进入异常躁动区，就先别硬接飞刀。**

这不是 alpha 本体，但它是一个很适合短周期 desk 的 regime/filter：
**均值回归最怕你接到“相关性结构正在断裂”的那种偏离。**

### 6.2 最短持有期：避免刚进就来回反手
默认：
- `min_holding_period = 5`

对日频研究它代表 5 天；
对我们更重要的翻法是：**这是一个“冷静期 / 最短持仓 bars”约束。**

在 `15m` 上不该机械照抄成 5 天，而更应该翻成：
- `2 / 4 / 8 / 12 bars` 的最短持仓约束，
看看它到底是在降噪、减少来回磨损，还是只是在拖慢出场。

### 6.3 Dynamic trailing stop：不是只等回归到均值
repo 的 stop 不是固定值，而是：
`dynamic_stop = trailing_stop_factor × max(current_vol / avg_vol, 1)`

默认：
- `trailing_stop_factor = 0.025`

也就是说，**波动越大，stop 会相应放宽。**

这点很像“波动自适应止损”而不是死板百分比止损。对 short-cycle desk 来说，可迁移之处不是 `2.5%` 这个数字本身，而是这条思路：
**mean reversion 也可以做 vol-aware 的风险带，而不是只靠 zero-cross 机械平仓。**

## 7. 6 个最值得记住的硬数据点
1. **论文样本背景（abstract）：** 10 个主要 crypto，时间覆盖 `2019-01` 到 `2024-05`。
2. **train / test 切法（repo）：** `split_ratio = 0.75`，即 `75%` 训练、`25%` OOS。
3. **entry 阈值（repo 默认）：** `z-score ±0.7`。
4. **波动过滤（repo 默认）：** `30` 期 rolling spread vol，阈值 `1.5 × average vol`。
5. **最短持有期（repo 默认）：** `5`。
6. **交易成本（repo 默认）：** `transaction_cost = 0.002`；从代码实现看，更接近**每次进/出各扣一次**的简化成本口径。

补一句非常重要的保留：
**README 里写了年化 Sharpe ≈ 2.0、年化收益 ≈ 71%，但在本轮没读到全文前，这些只能当“作者自述 + repo 摘要”，不能当作我们已经独立确认的结论。**

## 8. 和当前 1m / 3m / 5m / 15m 的关系
### 8.1 这条 alpha 最适合先落在 `15m`
原因很简单：
- pairs / spread 均值回归比单币追涨更怕噪音；
- `1m / 3m` 上 hedge ratio 漂移、盘口跳点、手续费吞噬会更严重；
- `15m` 更适合先回答“after-cost 到底有没有 edge”。

所以第一步最合理的是：
- **`15m` 做 alpha existence test**
- **`5m` 做 execution refinement**
- **`1m / 3m` 只在 15m 已经成立后，再拿来做更细的入场/减仓/回补**

### 8.2 适合 desk 的对象不是“固定一对币”，而是 rolling shortlist
repo 用的是两资产框架，但 desk 版不该一上来就锁死 `BTC/ETH`。
更合理的翻法是：
1. 先在 top-liquidity majors 里滚动挑候选对；
2. 用协整 / 残差稳定性筛 shortlist；
3. 再把这套 `z-score + vol veto + stop` 壳子套上去。

### 8.3 这篇最值钱的地方，是它把 pairs 从“研究想法”推进到“完整策略卡”
很多配对策略材料只讲：
- 怎么选 pair；
- 怎么算 spread；
- 怎么画个 z-score。

但这篇 repo 已经把下面四层都补上了：
- `entry`：spread 偏离
- `sizing`：hedge ratio 归一化两腿
- `risk/filter`：波动 veto + 最短持有期
- `exit`：动态 trailing stop + 成本

这正符合当前 desk 对“可直接落地完整策略”的偏好。

## 9. 最小可复现实验
### 实验 A：15m pairs existence test（最优先）
- **资产池：** Binance USDⓈ-M 或最液态 spot/perp 的 top `8~12` majors
- **bar：** `15m`
- **pair shortlist：** 每周滚动一次；只保留过去 `20 / 40 / 60` 天里残差最稳定的 `3~5` 对
- **spread 定义：** rolling OLS hedge ratio + log-price spread
- **entry：** `z >= {1.5, 2.0, 2.5}` 做空 spread，`z <= {-1.5, -2.0, -2.5}` 做多 spread
- **exit：**
  - `z` 回到 `0 / ±0.25`
  - 或 spread trailing stop hit
- **filter：** spread realized vol 不高于其过去 `N` bar 均值的 `1.25 / 1.5` 倍
- **cost：** round-trip `10 / 20 / 30 / 40 bps`

先回答一个最朴素的问题：
**在 15m、after-cost、market-neutral 框架下，协整 spread 均值回归到底能不能活。**

### 实验 B：5m execution refinement
若实验 A 活着，再做：
- `15m` 信号触发后，比较：
  1. 下一根 `5m` 立刻下；
  2. 等半个 spread 回补再下；
  3. 用 `5m` microprice / mid reversion 做更温和入场。

### 实验 C：ablation（必须做）
按下面顺序拆：
1. `z-score only`
2. `z-score + rolling pair selection`
3. `z-score + pair selection + vol veto`
4. `z-score + pair selection + vol veto + trailing stop`

这样才能知道 edge 到底来自：
- spread 回归本身，
还是
- filter / exit 在替它擦屁股。

## 10. 下一步怎么测
1. **不要直接照抄 repo 的 `0.7` 阈值。** 这个阈值在更高频短周期里很可能太窄，先从 `1.5~2.5` 做第一轮更合理。
2. **把“日频参数”翻译成“bar 参数”，而不是字面照搬。** `min_holding_period=5`、`vol_lookback=30` 到 intraday 里都需要重映射。
3. **先做 rolling hedge ratio，不要只做一次 train/test 固定估计。** crypto 的配对关系更容易漂移，静态 `γ` 太乐观。
4. **成本一定打厚。** pairs 看着 market-neutral，但换手、资金费率、滑点都会咬收益；first pass 就该看 `10~40bps`。
5. **把 pair selection 与 trading shell 分开评估。** 否则你最后不知道，赚的是“选对 pair”，还是“这套 z-score shell 本身就有 edge”。
6. **移植前先做一次代码审计。** repo 的持仓状态机是简化版，真实 intraday port 前应重新检查信号清零、状态切换、翻仓成本和 stop 触发逻辑。

## 11. 风险与保留意见
- **论文非全文。** 本轮主证据来自 repo 源码；论文只拿到 metadata + abstract，所以学术结论不能说太满。
- **pairs 在 crypto 上最怕结构断裂。** 一旦协整关系失效，均值回归会迅速变成接飞刀。
- **高频下成本比方向策略更容易被低估。** 双腿交易、funding、跳点、借币/换仓摩擦都会放大侵蚀。
- **lookback 优化容易过拟合。** 训练集里最优，不代表滚动 OOS 里仍然稳。
- **这条线适合做 raw alpha 候选，但不适合现在就当“已验证可实盘策略”。** 它应该先进入 clean replication / admission check。

## 12. 对当前项目的直接意义
如果只用一句话概括这轮 intake 的价值，那就是：
**它让我们把“pairs/relative-value”从零散想法，推进成一张可直接写成 `entry / exit / sizing / risk / cost` 的完整 raw alpha 策略卡。**

而且它和当前学习主线并不冲突：
- 主线项目自己在补 trend / breakout / ATR / volume；
- 这篇则补的是另一条 raw alpha 家族：**market-neutral mean reversion**；
- 两条线未来完全可以共存，甚至作为 desk 层面互补：
  - 趋势腿负责吃 directional move；
  - pairs 腿负责吃相对价值回归。

## 13. 来源链接
### 主来源
- Paper DOI：<https://doi.org/10.1002/fut.70018>
- Wiley article page：<https://onlinelibrary.wiley.com/doi/10.1002/fut.70018>
- Crossref metadata：<https://api.crossref.org/works/10.1002/fut.70018>
- Repo：<https://github.com/rafaelpalazzi/trading-games-crypto>
- Core code：<https://raw.githubusercontent.com/rafaelpalazzi/trading-games-crypto/main/pairs_trading_strategy.R>
- GitHub API metadata：<https://api.github.com/repos/rafaelpalazzi/trading-games-crypto>

### 数据来源
- Mendeley Data DOI：<https://doi.org/10.17632/2kky7c6xkn.1>
