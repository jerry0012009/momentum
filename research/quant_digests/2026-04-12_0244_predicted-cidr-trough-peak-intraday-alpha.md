# 别把这篇 2021 Bitcoin 日内曲线论文只读成功能数据分析 demo：对 crypto short-cycle desk，更该先测的是「predicted CIDR trough → subsequent peak」这条 raw alpha

- 时间：2026-04-12 02:44 UTC
- 类型：2021 *International Review of Financial Analysis* 全文 accepted PDF（University of Reading CentAUR）+ Binance USDⓈ-M `BTCUSDT 5m` portability probe
- 主题类型：raw alpha
- 基础 alpha：**把过去一段时间的 `5m` 日内累积收益曲线（CIDR）压缩成少数几个主成分分数，预测下一天整条日内回报路径；若预测曲线先下后上，就在预测谷底买入、在其后预测峰值卖出。对 desk 来说，本质不是“追涨/抄底一句话”，而是“次日 intraday path shape forecast”。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/intraday/path-shape/cidr/fpca/functional-time-series/mean-reversion/timing/btc/bitstamp/binance/5m/15m/paper/fulltext/public-probe/cost/risk
- 证据类型：论文全文证据 + 公共数据 portability probe

## 1. 这次看了什么
这轮主材料不是新 repo，而是一篇能直接拿到全文的论文：

- **Authors:** Elie Bouri, Chi Keung Marco Lau, Tareq Saeed, Shixuan Wang, Yuqian Zhao
- **Year:** 2021
- **Title:** *On the intraday return curves of Bitcoin: predictability and trading opportunities*
- **Venue:** *International Review of Financial Analysis* 76
- **DOI:** `10.1016/j.irfa.2021.101784`
- **Readable URL:** <https://centaur.reading.ac.uk/97607/>
- **Open PDF:** <https://centaur.reading.ac.uk/97607/1/Bitcoin_Functional_Accepted.pdf>
- **Repo URL:** 无

它的表面故事像“functional data analysis 在 Bitcoin 上的一个统计学应用”。
但对我们 desk，真正有交易味道的不是方法学名词，而是这句：

> **把一天内整条回报曲线先预测出来，再从预测曲线里读出次日的买点和卖点。**

这不是常见的：
- 单根 bar continuation；
- 某个指标 cross；
- funding/basis/carry 慢频壳子；
- 纯解释型 filter。

它是一个可以单独成型的 **raw alpha**：

> **预测次日 path shape → 在预测 trough 入场 → 在其后预测 peak 离场。**

## 2. 先回答最重要的一句：base alpha 到底是什么
这轮 base alpha 是清楚的：

> **next-day intraday path-shape forecast alpha**。

翻成人话：

- 先把每天 `5m` 的 BTC 价格轨迹改写成一条“从当天开头累积到当天每个时点的收益曲线”；
- 再看过去很多天这些曲线里，最稳定的几个“形状因子”是什么；
- 用这些因子分数去预测下一天的曲线大概会先往哪边走、何时更像低点、何时更像高点；
- 如果预测是“先压后抬”，就可以提前规划第二天的 long-only intraday trade。

所以它不是：

- 只给趋势信号做一个模糊 filter；
- 只能解释、不能下单的结构研究；
- 低频 regime 备注。

它本身就能写成完整交易规则，因此归类 **raw alpha** 没问题。

## 3. 论文里真正值得 desk 拿走的 5 个点

### 3.1 原始样本与信号口径很贴近我们的 fast lane
论文用的是：

- **标的：** Bitcoin
- **来源：** Bitstamp
- **频率：** `5m`
- **区间：** `2014-11-01` 到 `2019-08-10`
- **样本天数：** `1367` 天
- **单日观测数：** 论文写 `290` 个 intraday grid

它先定义：

```text
CIDR_t(u) = 100 × [ log P_t(u) - log P_t(0) ]
```

也就是：
- 当天起点收益是 `0`；
- 曲线后面每个点，表示“从当天开始到此刻，累计涨了/跌了多少”。

这对 short-cycle desk 的好处很明显：
- 它保留了**整天的路径信息**，不是只看收盘到收盘；
- 很容易迁移到 `5m / 15m`；
- 可以直接产出 **time-of-day execution plan**，而不只是方向判断。

### 3.2 论文结论不是“整条曲线自相关很强”，而是“曲线本身不相关，但分数在某些时期会相关”
论文先做了一堆 functional tests，结论很关键：

- CIDR curves **stationary**
- **non-normal**
- **uncorrelated**
- 但有 **conditional heteroscedasticity**

这点很重要，因为它说明：

> **不能简单把整条曲线直接喂进 functional AR，就期待稳定预测。**

作者的处理是：
- 先做 FPCA，把曲线压成少数几个 principal scores；
- 再只在这些 score 序列出现 serial correlation 的时候做预测。

这跟我们做 short-cycle 的习惯很像：

> **不要默认 alpha 永远开着；要先问当前这个“状态/分数过程”有没有可预测性。**

### 3.3 第一主成分像“均值曲线”，第二主成分更像“均值回归形状”
论文原文直接说：

- 前 **2** 个主成分已经解释了 **90.23%** 的总变异；
- 第一主成分主要解释 functional mean；
- 第二主成分更像 **mean-reversion mechanism of return curves**。

对 desk 的启发非常直接：

- 这条线不是纯 trend-only alpha；
- 它更像“**日内路径模板**”在不同 regime 下的切换；
- 第二主成分如果升高/降低，很可能就是“今天更像先冲后回 / 先压后弹”的 shape switch。

也就是说，这篇东西虽然表面挂着“functional forecasting”，但实质上更接近：

> **path-shape based intraday timing alpha**。

### 3.4 论文里的最小策略是完整的，不是半成品
论文给的 long-only 交易流程很朴素：

1. 用过去 `w` 天估计模型；
2. 预测下一天的整条 CIDR 曲线；
3. 找预测曲线的最小值时点 `u_min`，作为买点；
4. 在 `u_min` 之后再找预测曲线的最大值 `u_max`，作为卖点；
5. 次日按这个计划执行，且**不隔夜**。

这是完整交易规则，不需要你再脑补：
- entry
- exit
- long-only constraint
- intraday flattening

所以这篇 paper 不是“有想法但没办法下单”，而是已经给了我们一个能落地的 skeletal strategy。

### 3.5 论文最值钱的结果，不是“天天都能预测”，而是“serial-score pocket 里更有边”
论文的诚实点在于：

- 如果拿全部样本硬做，FPES / FPAR 的 forecasting error 并不总是优于简单均值曲线；
- 但如果只看 **first / second score 出现 serial correlation** 的子样本，预测才明显变得更值钱。

几个关键数字：

#### 预测误差层（Table 3）
当训练窗 `S=182`：
- 在“**第一或第二 score serially correlated**”的子样本上，FPAR 仍不算特别强；
- 但在“**第一和第二 score 都 serially correlated**”子样本上：
  - **FPAR RPE = +1.98%**
  - FPES 也转正，**RPE = +0.89%**

#### 交易层（Table 4）
**整段样本、每天都交易：**
- Fmean Sharpe：`1.03`
- FPES Sharpe：`1.08`
- **FPAR Sharpe：`1.11`**（`S=182`）

**只在“第一或第二 score serially correlated”时交易：**
- Fmean Sharpe：`0.55`
- FPES Sharpe：`0.63`
- **FPAR Sharpe：`0.72`**（`S=182`）
- 换 `S=365` 时，**FPAR Sharpe = `1.05`**

**考虑论文假设的 0.03% fee 后**（appendix 口径）：
- FPAR 仍是最优方案；
- 在全样本 `S=182` 下，Sharpe 还剩大约 **`0.74`**。

一句话：

> **这不是“永远开着”的傻瓜型 raw alpha，更像是“分数过程先出现可预测口袋，再启用路径定时交易”。**

## 4. 为什么这轮值得进池，而不是继续做又一条普通 momentum / pairs
因为它补的是当前素材池里比较少的一块：

1. **它是 raw alpha，不是纯 filter。**
2. **它天然带 timing 维度。**
   - 不是只告诉你多空方向；
   - 而是告诉你“今天更该在什么时候进，什么时候平”。
3. **它既能单独成策略，也能给别的 alpha 做 execution router。**
   - 例如：趋势 alpha 只在预测曲线后半段抬升时启用；
   - reversal alpha 只在预测曲线前半段下压后反抬时启用。
4. **它和我们当前 `5m / 15m` desk 直接相关。**
   - 不需要专有数据；
   - 只要公开 `5m` / `15m` K 线就能起步。

所以这条线不是学术好看而已，它确实能补一个我们还没系统收录的：

> **“day-template / path-shape” raw alpha family。**

## 5. 本地 portability probe：放到更近的 Binance `BTCUSDT 5m` 上，还剩什么
我补了一个**最小近样本迁移测试**，不是论文原版复现，但足够判断它在现今 crypto 上有没有残留价值。

### 5.1 数据与近似实现
数据源：
- **Binance USDⓈ-M Futures** `BTCUSDT`
- **频率：** `5m`
- **样本：** 最近约 `184` 个完整 UTC 日
- **公开性：** 公开 REST 接口
- **最小实验口径：** 每天 `288` 个 `5m` bar，构造 daily CIDR

近似实现：
- rolling window 分别试 `30 / 45 / 60 / 90` 天；
- 用 PCA 近似论文里的 FPCA；
- 取解释 `90%` 方差以内的前 `K<=4` 个主成分；
- 对 score 过程做简化版 Ljung-Box serial check；
- 只有 serial 成立时，才对 score 用 AR(1) 预测；否则预测 score = 0；
- 仍按论文 long-only 规则：**预测 trough 买，之后预测 peak 卖**。

相关 artifacts：
- `/root/clawd/jerry/momentum/reports/artifacts/literature/bitcoin_cidr_binance_portability_probe_2026-04-12.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/bitcoin_cidr_binance_portability_windows_summary_2026-04-12.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/bitcoin_cidr_binance_portability_window30_2026-04-12.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/bitcoin_cidr_binance_portability_window45_2026-04-12.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/bitcoin_cidr_binance_portability_window60_2026-04-12.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/bitcoin_cidr_binance_portability_window90_2026-04-12.csv`

### 5.2 结果：它不是稳定常开 alpha，但 serial-score pocket 里有一点味道
先看**全天都做**：

- **window=30d**：平均 **`-13.86 bps/trade`**，胜率 `44.8%`
- **window=45d**：平均 **`-7.05 bps/trade`**，胜率 `39.6%`
- **window=60d**：平均 **`+5.42 bps/trade`**，胜率 `44.4%`
- **window=90d**：平均 **`+1.59 bps/trade`**，胜率 `51.1%`

这说明一件很诚实的事：

> **近样本里，这条路径预测骨架不是“随便开、都能赚”的常开策略。**

但再看 **serial1_or_2** 子样本：

- **window=30d**：只有 `5` 次事件，但平均 **`+38.10 bps/trade`**，胜率 **`80%`**
- **window=60d**：只有 `4` 次事件，但平均 **`+71.42 bps/trade`**，胜率 **`75%`**

同时也要说清楚坏消息：
- `window=45d` 的 serial pocket 反而是负的；
- `serial1_and_2` 在这份近样本里几乎没出现；
- 事件数极少，还远远谈不上 production evidence。

所以近样本更像在告诉我们：

1. **论文的直觉方向没有完全死；**
2. **但它高度依赖“可预测 pocket 出现”这件事；**
3. **若不先做 admission/gating，最近样本表现会非常不稳。**

## 6. 对当前 desk，最合理的策略化读法是什么
### 6.1 主读法：它是一条 raw alpha，但不是 always-on raw alpha
我会把它定义成：

> **event-sparse / pocket-dependent raw alpha**。

也就是：
- base alpha 本体是成立的；
- 但 deployment 方式不该是“每天机械开一笔”；
- 更像先等 score serial-correlation 或 predicted amplitude 足够大时，再允许开火。

### 6.2 对 `15m` desk 的第一落点，不是照搬整日 one-trade，而是压成“预测日内模板”
论文是完整按一天交易；
但我们 desk 更适合先把它压缩成三个可测试部件：

1. **path slope sign**：预测曲线前半段 vs 后半段谁更强；
2. **predicted trough timing**：预测低点落在日内哪个 bucket；
3. **predicted amplitude**：预测 peak-trough 振幅够不够大。

然后写成 `15m` 版本：

- 若预测 trough 落在 UTC 日前 `35%~55%`，且 trough→peak 振幅 > 阈值；
- 则允许在 trough 附近 1~2 根 `15m` bar 内找 long setup；
- 若预测曲线全天单边下行，就不给 long alpha 开门；
- 若预测曲线前高后低，则反而可作为 momentum long 的 veto。

### 6.3 它最像给哪类 raw alpha 服务
这条线最适合服务两类：

#### A. BTC 单腿 intraday timing raw alpha
最直接：
- 只做 `BTCUSDT`
- `5m` 构造曲线
- `15m` 执行
- 以 predicted trough/peak 做当日交易计划

#### B. 给现有 momentum / mean-reversion 信号做日内 router
例如：
- 如果预测模板是“先压后抬”，那日内 reversal/long 信号更值得放行；
- 如果预测模板是“早高后弱”，那 continuation long 要降权，甚至转成 fade 思路。

注意：这不是把它降级成纯 filter；
而是说它**既可单独成 raw alpha，也可上接 execution router**。

## 7. 这轮最值得记住的 7 个数
1. 论文样本：**`1367` 天**，`5m` Bitcoin（Bitstamp）
2. 前两主成分解释：**`90.23%`** 总变异
3. 全样本日内交易（`S=182`）：**FPAR Sharpe `1.11`**
4. 全样本日内交易（`S=182`）：Fmean 也不差，Sharpe **`1.03`**
5. serial pocket 交易（`S=365`）：**FPAR Sharpe `1.05`**
6. 近样本 Binance probe：`window=30d` serial pocket 仅 `5` 次，但 **`+38.10 bps/trade`**
7. 近样本 Binance probe：`window=60d` serial pocket 仅 `4` 次，但 **`+71.42 bps/trade`**

这 7 个数合起来说明：

> **这条线值得进研究池，但前提是把它当“稀疏口袋 alpha”，而不是 daily always-on 印钞机。**

## 8. 最小实验应该怎么测
### 实验 1：先做 paper-style clean replication（BTC 单腿）
**目标：** 先确认这条骨架在我们自己的下载链路里能不能稳定复现。

- 标的：`BTCUSDT` perp
- 数据：公开 `5m`
- 曲线：daily CIDR
- 训练窗：`30 / 45 / 60 / 90` 天都测
- 预测：PCA/FPCA top-K + AR(1) score forecast
- gate：
  - `serial1_or_2`
  - predicted amplitude > X bps
- 执行：
  - 预测 trough 对应 `15m` bucket 开多
  - 之后最近预测 peak bucket 平仓
- 输出：
  - avg bps/trade
  - win rate
  - annualized Sharpe
  - max drawdown
  - 对比 simple mean-curve baseline

### 实验 2：把“预测 trough/peak”改写成 `15m` execution router
**目标：** 看它是不是更适合作为 execution timing 层，而不是直接 one-trade/day。

- 用 `5m` 曲线预测，但执行压到 `15m`
- 若 trough 在接下来 `2` 根 `15m` 内出现，且 predicted amplitude > 阈值：
  - 允许现有 long-alpha 进场
- 否则：
  - long-alpha 降权或 veto

### 实验 3：测它给哪一类 alpha 增益最大
**目标：** 决定它该放进 raw alpha 主池，还是作为 router 接在别的信号前面。

优先做三组：
- BTC 单腿 intraday reversal
- BTC/ETH 短窗 momentum continuation
- alt-beta 跟随 BTC 的 lead-lag long sleeve

看哪一组在接了 path-shape router 后：
- hit rate 提升最多
- drawdown 压得最多
- cost 后最能活

## 9. 风险与诚实门
这条线有 4 个不能跳过的坑：

1. **均值曲线 baseline 其实不弱。**
   - 论文里 Fmean 本身就不差；
   - 近样本里很多窗口下，复杂模型也未必稳赢 baseline。
2. **serial pocket 很稀疏。**
   - 近样本只抓到 4~5 次；
   - 现在远不能说“可直接上生产”。
3. **成本和延迟不能假装不存在。**
   - 论文 even 在 0.03% fee 下还有边，但那是历史 Bitstamp；
   - 我们要用当前 fee tier 和实际 slippage 再验一遍。
4. **它可能更适合 BTC，不一定天然外推到 alt。**
   - 真要迁移到 ETH / alt，需要单独测，不要默认复制成立。

## 10. 结论
这轮我会把它放进研究池，而且归类成 **raw alpha**，不是 filter。

但我给它的 desk 结论不是“明天就全天机械开一笔”，而是：

> **这是一条“预测次日日内路径形状”的 raw alpha。论文正文证明它能长成完整策略；近样本 probe 则提醒我们：它更像稀疏 pocket 里的 timing alpha，必须先过 serial-correlation / predicted-amplitude 这类 admission 门，再谈稳定 deployment。**

如果要排优先级，我会给它这样的落点：

1. **先做 BTC 单腿 clean replication**；
2. **再把 trough/peak timing 压成 `15m` router**；
3. **最后再看能不能服务 ETH / alt-beta 交易。**

一句话收口：

> **别把这篇 paper 只当“functional stats 在 Bitcoin 上的炫技”；对 short-cycle desk，它更像一条还没被充分开采的 `day-template / path-shape` raw alpha。**
