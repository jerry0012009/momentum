# 别把这份 2026 OOS repo 只读成“20d 动量失效”：对 short-cycle desk，更值得 intake 的是「24h losers-vs-winners XS reversal × dispersion / turnover 约束」这条 raw alpha 候选

- 时间：2026-04-01 23:22 UTC
- 类型：quant_digest
- 主题标签：raw-alpha/cross-sectional/mean-reversion/24h-reversal/dispersion/turnover/liquidity-gate/market-neutral/binance/top25/topliquid-perps/1h/15m/5m/3m/1m/repo/public-data/cost
- 证据类型：2026 GitHub repo source audit（`README.md` + `03_backtest.ipynb` raw notebook 输出）

- 主题类型：raw alpha
- 基础 alpha：在 crypto 横截面里，**前 24h 跑得最差的一组，后续更容易反弹；前 24h 跑得最好的一组，后续更容易回落**，因此可做 `long recent losers / short recent winners` 的 cross-sectional reversal；但是否能活下来，取决于 **turnover 压缩** 与 **dispersion / liquidity 约束**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 先回答一句：这篇东西的 base alpha 是什么？
不是“regime break 讨论”，也不是“研究方法论提醒”。

它的 **base alpha** 很直接：
- 每个再平衡时点，看一篮子币在最近 `24h` 的横截面收益排名；
- 做多最近最弱的一组，做空最近最强的一组；
- 赚的是 **短期横截面 overshoot 之后的回归**。

所以它首先是一条 **raw alpha（cross-sectional mean reversion）**，不是纯 filter。

## 2. 为什么这一轮值得写它
最近 digest 池里，pairs / funding / basis / microstructure 已经很密；继续补当然也行，但边际增量没那么大。这个 2026 repo 的价值在于，它给了一条 **很清楚的 XS mean reversion 候选**，而且不是只给 in-sample 漂亮图：

1. **它把 2025-2026 OOS 单独拎出来了。**
2. **它把 alpha 和 implementability 分开讲清楚了。**
3. **它顺手给出一个 desk 很需要的结论：不是所有“gross 很强”的 reversal 都该直接 live，上线前必须先过 turnover / cost 这一关。**

换句话说，这份材料最值钱的地方不是“它证明了某条 daily 因子永恒有效”，而是：
**它把一条可复现的 raw alpha 和一套必须配套的实现约束，放在了同一张桌子上。**

## 3. 这次看了什么
### 3.1 主来源
- **Author**：Pramesh Singhavi
- **Year**：2026（README 标注 February 2026）
- **Title / Repo**：*crypto-momentum-backtest* / *Cryptocurrency Cross-Sectional Momentum: A Rigorous Out-of-Sample Analysis*
- **Repo URL**：https://github.com/prams2104/crypto-momentum-backtest
- **Readable URL**：https://github.com/prams2104/crypto-momentum-backtest
- **关键文件**：
  - `README.md`
  - `03_backtest.ipynb`
  - `utils.py`

### 3.2 它到底测了什么
- **Universe**：25 个 liquid cryptocurrencies
- **Data**：Binance historical OHLCV
- **Period**：2020-01-01 ~ 2026-02-05（约 2,229 天）
- **Frequency**：日频再平衡
- **策略**：
  1. `20-day` cross-sectional momentum
  2. `1-day` cross-sectional reversal
  3. `filtered reversal`（只保留低波动币）
- **交易成本假设**：单边 `20 bps`
- **Alpha 检验**：相对 BTC benchmark 的 alpha / t-stat

## 4. repo 里最值得 desk 拿走的硬数据点
## 4.1 真正有 OOS alpha 的，不是 20d momentum，而是 1d reversal
repo 把训练 / 验证 / 真 OOS 分开后，结论很清楚。

### 20d momentum
- **Training (2020-2022)**：
  - 年化 alpha：`36.2%`
  - alpha t-stat：`2.02`
  - net Sharpe @20bps：`0.42`
- **Validation (2023-2024)**：
  - 年化 alpha：`13.5%`
  - alpha t-stat：`1.08`
  - net Sharpe：`-0.48`
- **OOS (2025-2026)**：
  - 年化 alpha：`-12.5%`
  - alpha t-stat：`-0.81`
  - net Sharpe：`-2.18`

翻成人话：**20d XS momentum 在这份样本里不是“被成本打死”，而是先失去统计显著性，最后连方向都翻了。**

### 1d reversal
- **Training (2020-2022)**：
  - 年化 alpha：`-5.5%`
  - alpha t-stat：`-0.31`
  - net Sharpe：`-3.21`
- **Validation (2023-2024)**：
  - 年化 alpha：`17.1%`
  - alpha t-stat：`1.37`
  - net Sharpe：`-4.51`
- **OOS (2025-2026)**：
  - 年化 alpha：`73.0%`
  - alpha t-stat：`4.64`
  - **gross Sharpe：`4.41`**
  - **net Sharpe @20bps：`-1.73`**

这就是这份 repo 最该 intake 的点：
**2025-2026 这段样本里，真正“有 alpha 本体”的反而是 1-day cross-sectional reversal。**

## 4.2 它死在实现层，不是死在 alpha 本体
repo 对 reversal 给出的 OOS 结果非常诚实：
- **gross return**：`72.8%`
- **net return @20bps**：`-28.5%`
- **daily turnover**：`138.83%`
- **annual cost drag**：约 `101%`

这很重要，因为它告诉我们：
- 这不是“没有信号”；
- 而是 **signal > 0，但 execution shell 太差**；
- 所以下一步不是把 alpha 本体判死刑，而是先问：
  **能不能把 turnover / impact 打下来？**

## 4.3 “低波动过滤版 reversal”并没有救活它
repo 还测了一个直觉上很合理的派生：
- 只在 `20d realized vol` 较低的那一半币里做 reversal。

结果作者直接写了结论：
- **Filtered Reversal consistently underperformed both base strategies across all periods**
- 也就是：**简单的 low-vol filter 没把问题修好**。

这对我们也有用，因为它避免我们在第一轮实验里把时间浪费在一个已经显著失败的简单派生上。

## 4.4 momentum 失效的关键背景：横截面 dispersion 塌了
repo 给出的 regime break 线索：
- **Pre-2023**：cross-sectional dispersion 平均约 `3.20%`
- **Post-2023**：降到约 `1.98%`
- **降幅**：约 `-38%`
- 同期 momentum gross Sharpe 从 `1.12` 掉到 `-0.68`

这不等于“dispersion 一低，reversal 就一定更好”，但至少给了一个很实用的提醒：
**横截面 alpha 的生存环境，和 dispersion 强弱高度相关。**

## 5. 对当前 short-cycle desk 的正确读法
## 5.1 不要把它照抄成“25 币 spot 日频轮动”
如果把它原样拿去跑：
- 25 个 spot 币
- 每天大幅换仓
- 单边 20bps

那 repo 已经告诉你，大概率不行。

所以对 desk 来说，真正值得 intake 的不是“照抄 daily strategy”，而是这个更窄、更实战的命题：

> **24h 横截面 losers-vs-winners reversal 这条 raw alpha 可能是真的；但必须放进更液体、更低 turnover 的 execution shell。**

## 5.2 它和 `1m / 3m / 5m / 15m` 的关系是什么？
这条 alpha 本体不是逐根 `1m` micro alpha，它更像：
- **慢一点的 cross-sectional raw alpha**；
- 用 `1h / 15m` 做信号更新；
- 用 `5m / 1m` 做执行和成本控制。

也就是说：
- **signal horizon** 可以是 `24h` return 排名；
- **rebalance cadence** 可以压缩到 `4h` 或 `1h`；
- **execution layer** 再落到 `15m/5m/1m`。

这非常适合做成一个 **低持仓占用、但和现有 intraday trend/pairs 不完全同向** 的 sleeve。

## 6. desk 化后的完整策略骨架
下面这个版本，才是我觉得值得先测的 desk 版最小骨架。

### 6.1 Universe
优先只用高流动 perpetual：
- BTC, ETH, SOL, BNB, XRP, DOGE, ADA, LINK, AVAX, LTC, BCH, DOT
- 后续再看是否扩到 15~20 个

不要第一轮就把流动性黑洞请回来。

### 6.2 Signal
每个再平衡时点：
1. 计算每个币最近 `24h` 收益；
2. 做横截面排名；
3. long bottom tail，short top tail；
4. 权重做 dollar-neutral / beta-light neutral。

### 6.3 Entry / Exit
我建议第一轮先测两种节奏：

**版本 A：4h rebalance**
- 每 `4h` 更新一次 `24h` 排名
- 持有 `4h`
- 更容易压 turnover

**版本 B：1h rebalance + buffer**
- 每 `1h` 更新一次 `24h` 排名
- 只在 rank / score 变化超过阈值时换仓
- 持有 `1h~4h`

### 6.4 Sizing
- 每侧 equal-risk 或 equal-notional
- 单币 gross cap
- 组合 gross cap
- participation cap
- 若有条件，给 BTC / ETH 更高容量权重，其余小一点

### 6.5 Risk / veto
至少要有三层：
1. **Liquidity veto**：top-of-book / ADV / spread 不达标不换仓
2. **Turnover veto**：预估换手超预算时，只保留最强几条信号
3. **Dispersion gate**：横截面 dispersion 太低时，size-down 或停机

### 6.6 Cost
第一轮必须固定跑三档：
- maker-ish
- mixed
- taker-heavy

否则你永远分不清：
- 是 alpha 本体不行；
- 还是你的执行假设过于理想。

## 7. 我对这条线的核心判断
## 7.1 它是 raw alpha，不是纯 overlay
这一点要讲清楚。

它的本体是：
- `24h` 横截面 losers-vs-winners reversal。

`dispersion` 与 `turnover budget` 只是它的生存条件，不是 alpha 本体。

## 7.2 但它不是“可直接原样实盘”的 raw alpha
repo 自己已经证明：
- 原始 daily spot 壳子里，它过不了成本。

所以更准确的说法是：
- **raw alpha 存在；**
- **原始 implementation shell 不合格；**
- **我们要复现的是 alpha 本体 + 更强执行壳子，而不是原样照搬。**

## 7.3 这比继续补一个相似的 pairs 门槛更值钱
因为它给了我们两件最近很需要的东西：
1. **一个新的 raw alpha 家族补位**：cross-sectional reversal
2. **一个可共享的风控先验**：dispersion / turnover 约束

也就是说，它既能扩 raw alpha 池，也能顺手反哺已有 XS 方向。

## 8. 最小可复现实验（直接面向当前 desk）
### 实验 A：top-liquid perp 版 `24h` XS reversal
- **Universe**：top 8~12 liquid perps
- **Signal**：最近 `24h` return 排名
- **Rebalance**：每 `4h`
- **持有**：`4h`
- **组合**：long bottom `20%` / short top `20%`
- **成本**：maker / mixed / taker 三档
- **核心问题**：把 universe 收窄、把换手降下来后，after-cost 是否能转正？

### 实验 B：1h 版 + trade buffer
- **Signal**：同样是 `24h` 排名
- **刷新**：每 `1h`
- **约束**：只有当 rank change / score gap 超阈值时才换仓
- **目的**：验证“trade buffer 能否把 turnover 从不可交易区间拉回可交易区间”

### 实验 C：dispersion gate
- 用 rolling `24h` cross-sectional dispersion
- 只在 dispersion 高于过去 `60d` 中位数 / 或分位阈值时开仓
- 对照无 gate 版本
- **目的**：验证 dispersion 作为 reversal 生存条件是否有效，而不是只对 momentum 有解释力

### 实验 D：execution shell 拆解
- 先不改 signal
- 只改 execution：maker 比例、分批入场、最大 participation、单币 cap
- **目的**：确定问题到底主要在 signal，还是主要在执行层

## 9. 下一步怎么测
如果只做一轮最小实验，我建议按这个顺序：

1. **先做 top-liquid perp + 4h rebalance**
   - 这是最便宜、也最像真实 desk 壳子的第一步。
2. **固定 24h lookback，不先扫太多 lookback**
   - 先验证 repo 的 alpha family 能不能迁移，不要一上来就参数挖矿。
3. **直接记录 turnover / spread / slippage attribution**
   - 不要只看 Sharpe。
4. **再加 trade buffer**
   - 如果 gross 还行但 net 不行，优先砍 turnover。
5. **最后再测 dispersion gate**
   - 先确定 alpha 本体能不能迁移，再决定 gate 要不要上。

一句话版：
**先验证“高流动 perp + 低换手壳子”能不能救活这条 24h XS reversal，再决定是否值得继续深挖。**

## 10. 风险与局限
1. 主证据来自 **日频 Binance 横截面**，不是分钟级；
2. repo 的核心亮点是 **OOS alpha 与实现失败并存**，不是直接可 live 的净 alpha；
3. dispersion 对 momentum 的解释较强，但对 reversal 是否同样构成充分 gate，仍需要我们自己验证；
4. 如果 universe 太小，横截面排序会退化；如果 universe 太大，又会重新把成本黑洞带回来。

## 11. 一句话结论
这份 2026 repo 最值得 intake 的，不是“20d 动量失效”这个结论本身，而是：
**`24h` crypto cross-sectional reversal 这条 raw alpha 在 2025-2026 OOS 里很强，但只有在 turnover / liquidity / dispersion 约束下，才有机会从 `gross alpha` 变成 `after-cost alpha`。**

## 12. 来源链接
1. **Pramesh Singhavi. (2026). _crypto-momentum-backtest_. GitHub repository.**  
   Repo: https://github.com/prams2104/crypto-momentum-backtest
2. **README**：https://raw.githubusercontent.com/prams2104/crypto-momentum-backtest/main/README.md
3. **Backtest notebook**：https://raw.githubusercontent.com/prams2104/crypto-momentum-backtest/main/03_backtest.ipynb
