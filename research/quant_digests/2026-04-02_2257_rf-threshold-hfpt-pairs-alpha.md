# RF 预测最优阈值的高频 Pairs Rebalance：别只盯 cointegration spread，这篇 2025 论文更适合先拆成「threshold-classified HF pairs shell」

- 主题类型：raw alpha
- 基础 alpha：pairs / relative-value / stat-arb 下的双资产权重偏离均值回归；当两腿市值权重偏离超过阈值时，卖强买弱，回补到 50/50
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 时间：2026-04-02 22:57 UTC
- 类型：raw alpha
- 主题标签：raw-alpha/pairs/relative-value/stat-arb/mean-reversion/high-frequency/rebalancing/threshold-selection/random-forest/binance/btc-quoted/1m/3m/5m/15m/paper/public-data/cost
- 证据类型：2025 Springer 开放获取全文（article + tables）/ Crossref metadata

## 1. 这次看了什么

在最近几篇 pairs digest 已经补过 `cointegration / OU / copula / microprice veto` 之后，这篇 2025 *Computational Economics* 值得补进素材池的点，不是再发明一个 spread，而是把 **pairs shell 的阈值选择** 单独做成可预测对象：先承认“同一个 pairs rebalancing 策略没有通用最优阈值”，再用 `RF` 把不同 pair 的最优阈值预测到 **2 桶 / 3 桶**，让策略从“固定阈值拍脑袋”变成“按 pair 特征自适应选择触发强度”。

## 2. 为什么这轮值得做它

先回答任务里最重要的那句：**这篇东西的 base alpha 是什么？**

答：**pair 内相对强弱的短周期均值回归**。不是 filter，不是 overlay，也不是“只帮你挑参数”的元分析。它本体就是一条完整的 pairs raw alpha：

1. 先持有双腿等权组合；
2. 当两腿权重偏离超过阈值 `T`，说明相对价格已经拉开；
3. 卖出当前更贵的一腿、买入当前更便宜的一腿；
4. 把两腿重新配平到平均权重；
5. 继续等待下一次偏离。

所以它是 **relative-value / stat-arb / mean reversion**，而不是纯 filter。

这轮优先它，而不是再补一个老的 breakout / retest 变体，原因有三点：

- 它是 **完整策略壳**，而不是一句“相关性高时更好”的经验判断；
- 它直接回答了 desk 真正会遇到的问题：**pairs 壳该用多大触发阈值才不被手续费吃掉**；
- 它天然可迁移到 `1m / 3m / 5m / 15m`，并且最小实验几乎全靠公开 K 线就能先跑起来。

## 3. 论文信息

- **Authors**: Mahmut Bağcı, Pınar Kaya Soylu
- **Year**: 2025
- **Title**: *The Optimal Threshold Selection for High-Frequency Pairs Trading via Supervised Machine Learning Algorithms*
- **Venue**: *Computational Economics*
- **DOI**: `10.1007/s10614-025-10958-5`
- **Readable URL**: https://link.springer.com/article/10.1007/s10614-025-10958-5
- **DOI URL**: https://doi.org/10.1007/s10614-025-10958-5
- **Repo URL**: 无论文配套 repo（本文主要依赖 open-access article + tables）

## 4. 论文到底做了什么

### 4.1 数据与样本

- 交易所：**Binance**
- 标的：**50 个 BTC 计价 crypto-assets**（例如 `AAVE/BTC`, `ADA/BTC` 这类）
- 频率：**1 分钟**
- 样本期：**2022–2023** 用于训练 / 验证，**2024 年 1–2 月** 用于独立测试
- 每个月对所有可能双资产组合做一次样本生成；50 个币两两成对，每月 `1225` 对，24 个月合计约 `29400` 个 monthly pair samples

这点很关键：它不是只挑少数“看起来像 pairs”的币对，而是先把全部 pair 都扫一遍，再由特征决定该 pair 适合什么阈值。

### 4.2 策略壳（HFPT）

论文的 high-frequency pairs trading（HFPT）不是经典价差 z-score，而是一个**权重偏离触发的双资产再平衡壳**：

- 初始时，两腿各配 `1 BTC`，即总资本 `2 BTC`
- 若两腿市值权重差超过阈值 `T`
  - 卖出当前权重更高 / 更贵的一腿
  - 买入当前权重更低 / 更便宜的一腿
  - 把两腿重新拉回到相同市值
- 交易成本：**0.1% taker fee**
- 论文把 `T` 从 **1% 到 30%** 以 **1% 步长**全扫一遍，取利润最高的阈值作为该 pair 的 `OT`（optimal threshold）

换句话说，paper 先不争论“spread 该怎么建”，而是先承认：**同样的 rebalance alpha，对不同 pair 来说最优触发阈值完全不同**。

## 5. 最重要的 desk 启发：别固定阈值，先预测“阈值桶”

论文不是直接做回归预测精确阈值，而是把阈值预测降成 **分类问题**。这很实用，因为短周期 desk 真正在意的通常也不是“17% 和 18% 谁更神”，而是：

- 这是个应该用 **低阈值、频繁回补** 的 pair？
- 还是该用 **高阈值、少交易、等极端偏离** 的 pair？

论文把 pair 按相关性先分 3 组：

- **正相关**：`corr > 0.3`
- **弱相关**：`-0.3 <= corr <= 0.3`
- **负相关**：`corr < -0.3`

然后把最优阈值 `OT` 划分成 2/3/4 类：

- **2 类**：`0–15%` / `15–30%`
- **3 类**：`0–10%` / `10–20%` / `20–30%`
- **4 类**：`0–7.5%` / `7.5–15%` / `15–22.5%` / `22.5–30%`

输入特征只用了 6 个、非常朴素但很容易复现：

- portfolio mean
- variance
- skewness
- kurtosis
- VaR
- correlation coefficient

也就是说，这篇 paper 最有价值的地方不是花哨 ML，而是告诉你：

> **pair 的最优触发强度，本身就是可以用低维统计特征来预测的。**

## 6. 关键证据

### 6.1 RF 明显胜出，而且 2-class / 3-class 最实用

论文比较了 `LR / SVM / KNN / DT / RF / NB` 六种分类器。核心结果：**RF 在正相关、弱相关、负相关三组里全部拿第一**。

训练/验证期的 **RF average accuracy**：

- **正相关 pairs**：
  - 2-class `0.8751`
  - 3-class `0.7285`
  - 4-class `0.6406`
- **弱相关 pairs**：
  - 2-class `0.8399`
  - 3-class `0.6998`
  - 4-class `0.6091`
- **负相关 pairs**：
  - 2-class `0.8479`
  - 3-class `0.7690`
  - 4-class `0.6819`

独立测试集（2024 年 1–2 月）的 **RF average accuracy** 更值得看：

- **正相关**：2-class `0.9217`，3-class `0.7097`，4-class `0.6083`
- **弱相关**：2-class `0.7715`，3-class `0.6294`，4-class `0.5462`
- **负相关**：2-class `0.8168`，3-class `0.7693`，4-class `0.6065`

这组数字对 desk 的意义很直接：

- 若你只是要决定“**低阈值 / 高阈值**”两档，论文结果是够强的；
- 若你要更细一点，**3 档也还可用**；
- **4 档开始明显变脆**，不太像第一版 production 应该上的复杂度。

### 6.2 相关性越低，最优阈值越大

论文的分布图和文字结论都在指向同一件事：

- **正相关 pairs** 的最优阈值更常落在低区间（很多 `<15%`）
- **弱相关 pairs** 更常落在中间区间（很多在 `10–20%`）
- **负相关 pairs** 更常落在高区间（很多在 `22.5–30%`）

这非常像一个可以直接带回 desk 的规则：

> **pair 越“天然对冲”，可以越早动手；pair 越“彼此掰手腕”，越要等更大的偏离再回补。**

### 6.3 最佳样例利润很高，但不要直接当 production 预期

Table 8 给出的几组最佳样例：

- `CHZ-ETC`（正相关，2024-01）：实际 OT `21%`，月利润 `18.1%`
- `STX-THETA`（正相关，2024-02）：实际 OT `24%`，月利润 **`41.2%`**
- `MKR-STX`（弱相关，2024-01）：实际 OT `12%`，月利润 `9.3%`
- `MANA-THETA`（弱相关，2024-02）：实际 OT `30%`，月利润 `25.9%`
- `CHZ-STX`（负相关，2024-01）：实际 OT `21%`，月利润 `12.3%`
- `DOGE-STX`（负相关，2024-02）：实际 OT `29%`，月利润 `25.1%`

这些收益数字**可以当“阈值选择很重要”的证据**，但不该直接当可实现业绩，因为：

- 标的是 **BTC 计价 spot**，不等同于我们常用的 USDT perp；
- 执行假设是固定 `0.1% taker`，没把真实盘口冲击拆得很细；
- 策略是“持续回补型”，不是标准 flat-to-flat z-score round-trip。

## 7. 这篇 paper 对我们 desk 最值得拿走的，不是“照抄 spot-BTC”，而是 3 个组件

### 7.1 组件 A：用最简单的 pair shell 先找 raw alpha

别一上来就先上 Johansen / OU / copula。先用最朴素的双腿回补壳：

- 两腿初始等权
- 偏离超阈值就卖强买弱
- 回到等权后继续观察

如果这个壳本身在 `1m / 3m / 5m / 15m` 就已经能赚钱，说明 alpha 是真实存在的；后面再叠加更复杂 spread 模型，胜率更高。

### 7.2 组件 B：把“阈值选取”从手调，改成可学习对象

很多 pairs 策略死在这一步：

- 阈值太小，手续费和噪音把策略磨死；
- 阈值太大，信号又太稀疏。

这篇 paper 给的不是最终答案，而是一个非常好的最小范式：

- 先在历史上 sweep 阈值；
- 生成每个 pair / 月份的“最佳阈值桶”标签；
- 用低维统计特征去预测该 pair 下个月应该用哪个桶。

这比“全市场统一用 10%”靠谱得多。

### 7.3 组件 C：先避开 weak-correlation bucket

从测试集看，**弱相关组最差**。所以 desk 第一版不该把全部 pair 混在一起做。

更合理的顺序是：

1. 先只做 **正相关** 和 **负相关** 两组；
2. 先只做 **2-class** 或 **3-class**；
3. 弱相关 pair 当作 backlog，不要抢第一版算力和注意力。

## 8. 映射到 `1m / 3m / 5m / 15m` 的最小可复现实验

### 8.1 可直接复现的 base alpha 版本

**Universe**
- Binance / Bybit / OKX 上流动性靠前的 20–40 个 perp
- 先用 `BTC / ETH / SOL / BNB / DOGE / XRP / ADA / LINK / LTC / AVAX / STX / ETC / THETA` 这类活跃币做起步

**构造**
- 每个周期（`1m / 3m / 5m / 15m`）维护所有 pair 的两腿等权市值组合
- 可以先用简单等美元 notional；若担心 beta 不齐，再切换成 rolling beta-neutral

**信号 / 触发**
- 定义 pair 偏离：`abs(w1 - w2)`，其中 `w1,w2` 为两腿当前市值占组合净值的比例
- 若偏离超过阈值 `T`：
  - short 当前占比高的一腿
  - long 当前占比低的一腿
  - 目标调回 `50/50`

**退出 / 继续持有**
- paper 的原始壳是 continuous rebalance，不是 flat exit
- desk 最小版可以先照 paper：只做再平衡，不强制平仓
- 如果更想要标准 flat-to-flat 统计套利回测，可加一版对照：
  - 开仓：偏离超 `T`
  - 平仓：偏离回落到 `T/3` 或回到 `50/50 ± ε`

**成本**
- 第一版统一：单边 `4–6 bps` maker / `8–10 bps` taker 两套
- paper 参考值：**10 bps taker**

**仓位**
- 每对 pair 固定风险预算
- 论文给了一个很实用的粗 cap：
  - 单腿资金不超过低流动性腿日成交额的 `(1/T)%`
- desk 里可改写成：
  - `pair_notional_cap = min(adv_leg1, adv_leg2) * k / T`
  - `k` 先取 `0.5% ~ 1%`

### 8.2 阈值预测版本（真正值得测的版本）

对每个 pair、每个月滚动生成 6 个特征：

- mean
- variance
- skewness
- kurtosis
- VaR
- corr

然后：

1. 在过去 `N` 天 / `N` 周历史中 sweep `T = 1%..30%`
2. 找到该 pair 的最佳阈值 `OT`
3. 将其离散成：
   - 2-class：`<=15%` vs `>15%`
   - 或 3-class：`<=10%` / `10~20%` / `20~30%`
4. 训练 RF
5. 在下一滚动窗预测 pair 应该使用的阈值桶
6. live 交易时只在该桶内取一个代表阈值，例如：
   - 2-class：`10%` / `22%`
   - 3-class：`7.5%` / `15%` / `25%`

这一步的重点不是把 RF 神化，而是先验证：

> **pair-specific threshold bucket 是否显著优于全市场统一 threshold。**

## 9. 我对 desk 的具体改写建议

### 9.1 不要继续用 BTC-quoted spot，改成 USDⓈ-M perp 或统一美元计价

论文用 BTC 计价现货，适合学术上统一 numeraire，但对实盘 desk 有两个问题：

- BTC 本身会把很多 pair 的共同波动“藏”进 quote currency；
- 现货 borrow / inventory / 尾部成交习惯和 perp 很不一样。

所以 desk 版更建议：

- 先上 **USDT perp**；
- 先用 **equal-dollar** 或 **beta-neutral**；
- 再去看这套 threshold bucket 逻辑能否保留下来。

### 9.2 第一版只做 2-class RF，不做 4-class

原因很简单：paper 自己的结果已经说明 4-class 会明显掉精度。对实盘而言，**“低阈值 / 高阈值”** 先分出来就已经很有用。

### 9.3 第一版只保留正相关 / 负相关 pair

- 正相关组测试集 2-class average accuracy：`92.17%`
- 负相关组测试集 3-class average accuracy：`76.93%`
- 弱相关组整体最差

这说明第一版没必要追求“所有 pair 都做”，而该先挑 **结构最清楚** 的 pair。

### 9.4 给它加一个交易频次 veto

这篇 paper 的大漏洞是：只看最后利润，没有把 **每个 threshold 带来的 turnover** 摊开得很细。

所以 desk 里一定要补：

- 每日最大 rebalance 次数上限
- pair 的 rolling turnover cap
- fee-to-edge 比率 veto

否则 RF 可能只是帮你挑出了“看起来利润高、但交易过密”的 threshold bucket。

## 10. 下一步怎么测

### 实验 1：先验证“固定阈值 rebalancing 壳”有没有 alpha

**目标**：验证这不是纯 ML 幻觉，而是 pair shell 本身有边。

- 数据：Binance USDⓈ-M 前 20–30 个高流动 perp
- 周期：`1m / 3m / 5m / 15m`
- pair 选法：先只取 rolling corr `> 0.3` 或 `< -0.3`
- 阈值：固定扫 `5%, 10%, 15%, 20%, 25%`
- 执行：偏离超阈值即回补到 50/50
- 输出：
  - net pnl
  - Sharpe
  - max drawdown
  - rebalance count
  - fee / gross ratio
  - 每个阈值下的 top / bottom pairs

**判定标准**：若某些 pair 在 `5m / 15m` 下固定阈值 already 有稳定正 edge，这篇主题成立。

### 实验 2：验证“pair-specific threshold”是否优于“统一 threshold”

**目标**：证明 threshold selection 真能成为 alpha 组件。

- 用滚动月窗给每个 pair 打 label：最佳阈值桶
- 特征：`mean / var / skew / kurt / VaR / corr`
- 模型：先只用 RF
- 对照组：
  - 全市场统一 `T=10%`
  - 全市场统一 `T=15%`
  - pair-specific RF 2-class bucket

**判定标准**：pair-specific bucket 至少应在以下一项明显胜出：
- 净收益
- fee-adjusted Sharpe
- turnover-adjusted pnl

### 实验 3：把 continuous rebalance 改写成 desk 更熟悉的 flat-to-flat 版本

**目标**：把论文壳变成更标准的可审计交易单元。

- 开仓：权重偏离超预测阈值 `T*`
- 平仓：偏离回落到 `T*/3` 或 `0`
- 止损：偏离继续扩大到 `1.5 * T*`
- 超时：`N` 根 bar 后仍未回补则平仓

**判定标准**：看 flat-to-flat 版本是否能保留 paper 的主要 edge，同时显著改善回测解释性和实盘可监控性。

## 11. 我会怎么给这篇东西下判断

**结论不是**“RF 很强，直接上线”。

**更准确的结论是**：

1. 这篇 paper 提供了一条 **可独立复现的 high-frequency pairs raw alpha shell**；
2. 它最值得 desk 吸收的，不是 spot-BTC 这个实现细节，而是 **threshold bucket 也是可学习对象** 这个观念；
3. 对 `1m / 3m / 5m / 15m` desk，最佳落地方向不是照抄全部 50 币 spot，而是：
   - 先做 liquid perp universe
   - 先做正/负相关 pair
   - 先做 2-class RF threshold bucket
   - 再和统一阈值 baseline 正面对打。

如果这一步打赢了，我们就得到了一块很实用的可复用组件：

> **pair shell 不再用全市场统一触发阈值，而是按 pair 特征动态分桶。**

这东西既能服务传统 coint / z-score pairs，也能服务后续的 microprice-pairs、funding-pairs、cross-venue relative-value 壳。

## 12. 主要风险与不该误读的地方

- **它不是 spread 建模论文**：别强行把它读成“替代 cointegration”。它更像 pairs 壳的触发层。
- **它不是 execution 论文**：没有细拆盘口冲击、maker fill、queue position。
- **spot BTC quote 可能放大了公共因子**：搬到 USDT perp 后，阈值分布未必原样保留。
- **continuous rebalance 可能掩盖了真实 round-trip 统计**：所以一定要做 flat-to-flat 对照版。
- **弱相关组结果偏弱**：第一版别把 weak bucket 当主力。

## 13. 来源摘录

1. Bağcı, M., Kaya Soylu, P. (2025). *The Optimal Threshold Selection for High-Frequency Pairs Trading via Supervised Machine Learning Algorithms*. *Computational Economics*. DOI: `10.1007/s10614-025-10958-5`  
   Readable URL: https://link.springer.com/article/10.1007/s10614-025-10958-5
2. Table 3–8 from Springer article page: RF 在正/弱/负相关三组中均为最佳分类器；测试集 2-class 正相关准确率均值 `0.9217`；最佳 pair `STX-THETA` 2024-02 在 `24%` 阈值下利润 `41.2%`。

## 14. 一句话版本

这篇 2025 paper 最值得 intake 的不是“又一个 pairs”，而是把 **pairs 的触发阈值** 从固定超参数，变成了一个可以用低维统计特征去预测的 **strategy component**；对我们当前 short-cycle desk，最该先测的是 **USDT perp 上的 2-class RF threshold bucket vs 全市场统一阈值**。