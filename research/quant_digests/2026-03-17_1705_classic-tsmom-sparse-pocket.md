# 别把 15m 动量都写成快进快出：经典 TSMOM 更值得先看“慢一点、稀一点、少重叠”的 own-past persistence pocket
- 时间：2026-03-17 17:05 UTC
- 类型：论文
- 主题标签：trend / momentum / sparse / no-overlap / crypto / 15m
- 证据类型：论文证据 + desk source intake

## 1. 这次看了什么
这次回收的是：
- **Moskowitz, Ooi, Pedersen (2012)**
- **Time Series Momentum**
- Venue: **Journal of Financial Economics**
- DOI: **10.1016/j.jfineco.2011.11.003**

这篇对当前 desk 最有用的，不是再讲一遍“动量可能赚钱”，而是提醒一个更贴近当前 fast-lane 的切法：**如果当前 15m crypto 的 sign-momentum 家族老是被交易频率和成本拖垮，那更值得先认领的，不是再加一层花哨过滤器，而是回到经典 TSMOM 的更慢、更稀、更少重叠的 own-past persistence pocket。**

翻成当前 Scout Seat 语言：先别默认把“15m 动量”理解成每几根 bar 都要翻方向、每个 pocket 都高频重叠。更诚实的新 intake 是：**把 own-past persistence 压成 slow-window sign + fixed-hold + no-overlap 的最小 clean-room 候选，看看问题到底出在 alpha 不存在，还是出在我们之前拿得太快、太密。**

## 2. 为什么本轮选它，而不是直接回 Run 3
当前边际价值比较很直接：
- `Rank 17 / Rank 2 / Rank 29`：都属于 `P3 continuity`，而且当前没有真实 `append/review need`；继续认领只会撞到当日 hard cap。
- `Rank 30~36`：当前允许动作都已消耗并 `park`；继续重开大概率只是重复 closeout。
- `Rank 5 / Rank 6`：仍偏 external-data lane，不符合当前“先 paper / repo based 本地 fast-lane”的默认顺序。
- 剩余本地 seeds 里，**经典 TSMOM** 比 `Limited Attention Theory` 更适合当前这一轮，因为它**不需要额外 attention proxy 假设**，也比继续重挤结构/突破旁支更能回答一个真正会改变 desk judgment 的问题：
  - 当前 15m crypto 动量家族，到底是没有 own-past persistence，
  - 还是只是被过密交易与过短持有毁掉了？

所以这轮最诚实的动作不是退回 `Run 3`，而是先把这条更直接、预算更小的本地 paper-based intake 补上。

## 3. 对当前项目最重要的结论
- **结论 1：经典 TSMOM 的原始精神，更接近“自资产过去收益方向在一段时间内延续”，而不是“每隔几根 15m bar 都要重新抢方向”。**
- **结论 2：如果要把它翻成当前 15m crypto fast-lane，更值得先测的是 slow-window sign + fixed hold + no-overlap 的稀疏 pocket。**
- **结论 3：这条线和 `Rank 36 / TSM vs drift honesty gate` 不冲突。** `Rank 36` 回答的是“recent sign 有没有只是 drift 近义包装”；这轮新 intake 回答的是“即使不靠 drift 包装，慢一点、稀一点的 classic own-past persistence 还有没有最小存活空间”。
- **结论 4：因此这条线当前最合适的定位，是 fresh source intake admitted，而不是直接偷升成 `paper candidate`。**

## 4. 对 desk 的最小 clean-room 映射（source intake only）
### 候选名
`classic sparse TSMOM / own-past persistence pocket`

### trade on / trade off
- **trade on（slow-window leg）**：当前资产过去一段更慢窗口（例如 `4h~12h`）的累计收益方向为正/负，则沿该方向交易。
- **trade on（agree leg）**：若两档 slow window 都同向（例如 `4h` 与 `12h`），则只保留双窗口同向的交易。
- **trade off**：slow-window sign 不存在、方向冲突、或持有期结束。
- **执行约束**：默认 `signal bar close -> next-bar open` 入场，固定持有若干根 `15m` bar，优先 `no-overlap`，避免把经典 TSMOM 偷做成高频翻单器。

### 这条线和现有 baseline 的差别
- 不是继续在现有 `sign(momentum)` 旁边加新过滤器；
- 不是 cross-asset confirmation；
- 也不是再开一个 drift-honesty gate；
- 它要回答的是：**更慢、更稀、更少重叠的 pure own-past persistence，在当前 `BTC / ETH / SOL 15m` cache 上有没有最小 admission 味道。**

## 5. 下轮最小 clean replication 应该怎么做
### 固定样本
- 资产：`BTC / ETH / SOL`
- 周期：`15m`
- 样本：现有 `120d` 本地 cache
- 执行：`next-bar open` 入场；优先 `no-overlap`

### 只比较三档最小规则
1. `slow_4h_sign_hold_4h`
2. `slow_12h_sign_hold_8h`
3. `slow_4h_12h_agree_hold_8h`

> 这里的数值只是当前最小 clean replication 的起点，不是说论文参数原样照搬到 crypto 15m。

### 先看哪 4 个指标
- `post_cost_return`
- `positive_asset_ratio`
- `trade_count`
- `time-pocket honesty`

### 当前真正想回答的问题
- 如果更慢、更稀、no-overlap 的 classic TSMOM pocket 仍然全面转负，那就说明当前本地 15m crypto 环境下，连最朴素的 own-past persistence 都不值得继续给默认预算；
- 如果它明显比 `recent_sign_only` 一类快翻 pocket 更诚实、更抗成本，那才值得拿下一轮 clean replication 或轻量 stability 预算；
- 如果它只是靠极低 trade count 勉强转正，也应快速 `park`，不要误读成 `paper candidate`。

## 6. 当前 hard verdict（仅限 source intake）
- **`Rank 37 / classic sparse TSMOM / own-past persistence pocket`：允许进入下一轮最小 clean replication queue**

注意：
- 这还不是 `paper candidate`
- 也不是 `narrow paper pilot`
- 更不是说“经典 TSMOM 已经在 15m crypto 上被证明成立”

它当前只是满足了 fresh intake 的最低条件：
1. 来源硬；
2. `trade on / trade off` 能清楚写成 clean-room 规则；
3. 不需要额外外部数据；
4. 能直接复用当前 `BTC / ETH / SOL 15m` cache 做最小 clean replication。

## 7. 风险与保留意见
- 论文原证据是跨资产、更慢周期，不是让我们把月频参数硬搬到 15m crypto。
- 这条 intake 的价值，在于给当前 desk 一个**更诚实的 slow-pocket 对照**，而不是保证会产出新 alpha。
- 如果下轮最小 clean replication 发现它只是“少交易所以看起来没那么差”，也应尽快 `park`。

## 8. 来源
1. Moskowitz, T. J., Ooi, Y. H., & Pedersen, L. H. (2012). *Time Series Momentum*. Journal of Financial Economics, 104(2), 228-250.
   - DOI: https://doi.org/10.1016/j.jfineco.2011.11.003
   - Readable URL: https://www.sciencedirect.com/science/article/pii/S0304405X11002613
