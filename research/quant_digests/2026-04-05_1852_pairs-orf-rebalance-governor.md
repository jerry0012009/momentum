# 别把 pairs / stat-arb 继续只卷 entry：对 short-cycle desk，更该先补「optimal rebalancing frequency（ORF）governor」这层 cadence overlay
- 时间：2026-04-05 18:52 UTC
- 类型：2024 *Borsa Istanbul Review* 论文（DOAJ / Avesis 摘要元数据）+ GitHub repo source audit + Binance Spot 公共 `3m/5m/15m` 本地 portability probe
- 主题类型：overlay
- 基础 alpha：cointegration / spread z-score 驱动的 pairs mean reversion / stat-arb
- 是否可独立复现：否
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：overlay/pairs/stat-arb/relative-value/mean-reversion/rebalance-frequency/orf/half-life/cadence-governor/cointegration/zscore/binance-spot/3m/5m/15m/paper/repo/public-data/cost/risk
- 证据类型：论文证据（主论文摘要级）+ repo 工程骨架 + 本地便携性快检

> 先回答一句：**这篇东西的 base alpha 是什么？**
>
> **base alpha = `cointegrated / residual spread mean reversion`。**
> 这篇 paper 本身不是新 raw alpha，而是给现有 pairs / spread alpha 补一个经常被忽略、但会直接决定净值形状的 **rebalancing cadence governor**。

## 1. 这次看了什么，为什么这轮值得写它
这轮主看：

1. **Bağcı, M., & Kaya Soylu, P. (2024). _Classification of the optimal rebalancing frequency for pairs trading using machine learning techniques_. Borsa Istanbul Review, 24, 83–90.**
   - DOI: `10.1016/j.bir.2024.12.004`
   - DOI URL: `https://doi.org/10.1016/j.bir.2024.12.004`
   - DOAJ: `https://doaj.org/article/ea8fd49abc0e419bb95b28b581605866`
   - Avesis metadata page: `https://avesis.marmara.edu.tr/yayin/6148063e-e17d-406d-8108-6497f5d81e61/classification-of-the-optimal-rebalancing-frequency-for-pairs-trading-using-machine-learning-techniques`
2. **MattiDeBeer / ml-statistical-arbitrage（GitHub）** —— 作为现成的 cointegration + z-score 工程骨架，对照看它缺的正是 frequency governance 这一层。
   - Repo URL: `https://github.com/MattiDeBeer/ml-statistical-arbitrage`

这轮不是再补一条新的 pairs raw alpha，而是补 **pairs 组件层**。原因很直接：

- 最近几篇 digest 已经连续 intake 了多条 pairs / cluster / cointegration / stat-arb raw alpha；
- 但这些 skeleton 里最容易被偷懒写成常数的，正是 **多久 rebalance / 多久 refit / 多久允许 spread 回归一次**；
- 如果 cadence 选错，研究里看起来有 edge，实盘里就可能只是 **过度换仓 + 噪声交易 + 手续费放大器**。

所以这轮值得写，不是因为它比 raw alpha 更性感，而是因为它直接决定我们已有那批 raw alpha 能不能从“回测有图”走到“成本后还活”。

## 2. 一句话核心结论 + 它是怎么证明的
### 一句话核心结论
**对 short-cycle pairs / stat-arb，先别急着再卷 entry；更该先做的是把 spread 当前半衰期 / 相关性桶映射成一个 ORF bucket（多久 rebalance / 多久 time-stop / 多久重估 beta），否则 `1m/3m/5m/15m` 只是拍脑袋。**

### 一句话它怎么证明
- **论文侧**：主论文把 pair trading 的 **optimal rebalancing frequency（ORF）** 当成一个可分类问题，按 **正相关 / 弱相关 / 负相关** 三个 subgroup 分桶，再比较 `random forest / logistic regression / SVC` 对 ORF range 的分类效果；摘要里给出的方向是：**负相关 pairs 最好分，正相关 pairs 最难分**。
- **本地 probe 侧**：我直接对 Binance Spot 近窗 `3m/5m/15m` 的几个 major-coin pair 做了静态 beta spread + ADF + OU half-life 快检，结果显示：**同一类 pair 在不同 bar size 下的“像不像可做 spread”差很多，15m 在最近窗口里甚至大面积退化。**

## 3. 这篇东西最值钱的 4 个点
### 3.1 这篇 paper 真正值钱的，不是“ML classifier”四个字
摘要里最有用的信息其实很朴素：
- **ORF 是 pair trading 的关键参数**，不是实现细节；
- 作者不是直接做一个全市场统一频率，而是先按 **3 类相关性 subgroup** 分桶；
- `RF / Logistic / SVC` 在 short-term 与 long-term ORF range classification 上都能给出可用结果；
- **负相关 pairs 最容易分类，正相关 pairs 最难。**

把它翻成人话就是：

> **pairs 不是只有“做不做”两个状态，还有“该多久动一次”这个经常被忽视的第三状态。**

### 3.2 本地 portability probe：`3m/5m` 还能看到 pocket，`15m` 最近窗口明显变钝
我用 Binance Spot 公共数据，对 `BTC/ETH/SOL/BNB` 四个大币，分别在 `3m / 5m / 15m` 上拉了 **各 2400 根** close，做了一个最粗但够诚实的快检：
- 静态 log-price beta 回归
- spread ADF p-value
- OU-style half-life 估计

几个最有信息量的结果：

1. **`BNBUSDT/BTCUSDT @ 3m`**
   - `ADF p = 0.01`
   - `half-life ≈ 68 bars ≈ 204 min`
2. **`SOLUSDT/BNBUSDT @ 5m`**
   - `ADF p = 0.01`
   - `half-life ≈ 65 bars ≈ 327 min`
3. **`ETHUSDT/BTCUSDT @ 5m`**
   - `ADF p = 0.10`
   - `half-life ≈ 111 bars ≈ 553 min`
4. **`15m` 档最近窗口明显更差**
   - 这次测的 5 组 pair 里，**没有一组在 `15m` 上达到 `ADF p <= 0.10`**；
   - 最好的也只是 `p ≈ 0.18`，且 half-life 已经飘到 **`176~191` 根 `15m` bar（约 `44~48` 小时）**。

这组结果对 desk 的含义非常直接：

> **同一条 spread alpha，不是天然适合 `15m`；很多 current-window 的 mean reversion pocket 只在 `3m/5m` 还看得到。**

### 3.3 ORF 不是只管 rebalance，它还应该顺手管 3 个东西
如果把 ORF 只理解成“多久调仓一次”，还是太窄。更 desk 化的读法是它至少应该同时控制：

1. **多久允许 refit beta / hedge ratio**
2. **多久允许 spread 目标价差重新定义**
3. **time-stop 该放在几根 bar 以后**

也就是说，ORF 更像一个 **cadence governor**，不是一个孤立参数。

### 3.4 为什么它现在比继续补一条普通 pairs alpha 更值得
因为我们现在缺的不是“世界上第 N 条 z-score pair entry”，而是：

- 哪些 pair 更适合 `3m`，哪些更适合 `5m`；
- 哪些 pair 在当前 regime 下应该降低重平衡频率，避免把本来慢半拍的回归做成高换手噪声；
- 哪些 `15m` skeleton 其实应该先降级为观察名单，而不是继续推进 admission。

换句话说：

> **这层做好，是给现有 raw alpha 池补 admission / execution 之前的流量调度器。**

## 4. 为什么和当前项目直接相关
它服务的不是某一条孤立策略，而是至少 3 类我们已经在池子里的 raw alpha：

1. **cointegration z-score pairs**
2. **cluster / MST residual mean reversion**
3. **same-underlier / relative-value spread MR**

而且它和当前 desk 的 bar 体系天然对齐：
- `1m / 3m`：更像 fast bucket
- `5m`：当前看起来是很多 major-pair spread 更现实的主桶
- `15m`：不能默认稳健，应该先过 stationarity / half-life 检查再上

## 4.5 策略拆解（必填）
- 方向属性：pairs / stat-arb 的 cadence overlay
- 基础 alpha：cointegration / residual spread mean reversion
- overlay 本体：`pair-state -> ORF bucket`
- ORF bucket 建议第一版先离散成：`{4, 8, 16, 32, 64}` bars
- trade-on：当前 pair 的 `ADF / half-life / corr bucket / spread vol` 落在可交易区间，且预测 ORF 不超过 desk 可接受持有期
- veto：预测 ORF 太长、当前 half-life 飘到 `15m` 多日尺度、beta 漂移异常、净边际覆盖不了成本
- sizing / risk：ORF 越长，默认 size-down；time-stop 先设成 `1.25~1.5 x predicted ORF`；beta refit 只在 ORF 边界上做，别每根都重估

## 5. 给 desk 的最小可落地版本
第一版不用上复杂 ML，先做一个 **rule-based ORF governor** 就够：

1. 先按相关性分 3 桶：`positive / weak / negative`
2. 再按最近窗口 half-life 分 4 桶：
   - `< 8 bars`
   - `8~24 bars`
   - `24~64 bars`
   - `> 64 bars`
3. 每个 pair 只允许在对应桶里运行一组 cadence：
   - fast bucket：`3m` 为主，time-stop 偏短
   - medium bucket：`5m` 为主
   - slow bucket：只保留观察，或降频到 `15m` 研究，不急着 live-like
4. 如果 ORF bucket 连续两次漂移出当前 timeframe 可承受范围，直接把该 pair 移出 active universe

这版已经能比“固定每根 rebalance”诚实很多。

## 6. 下一步怎么测（这轮最重要）
### 6.1 先测什么
在现有 3 条 pair/raw-alpha skeleton 上都加一层 ORF governor，再做 A/B：
- baseline：固定 cadence（例如每根 `5m` 都允许开/平/重平衡）
- treatment：ORF bucket governance

优先测试对象：
1. `2026-04-03_1625_orca-tradability-cluster-pairs-alpha.md`
2. `2026-04-04_0316_kraken-pairs-zscore-stoploss-shell.md`
3. `2026-04-04_2028_ga-triplebarrier-pair-label-veto-alpha.md`

### 6.2 最小实验口径
- **数据**：Binance / Bybit / Kraken 公开 `3m / 5m / 15m`
- **pair universe**：先只做 `BTC/ETH/SOL/BNB` 里的 4~6 组高流动对
- **label**：每个 walk-forward 训练窗里，对 `ORF ∈ {4,8,16,32,64}` 做净收益 / Sharpe / turnover-adjusted pnl 排名，取最优桶为 label
- **features**：
  - rolling correlation (`20/60/120`)
  - ADF p-value
  - half-life
  - spread vol
  - z-score hit rate
  - beta drift
- **对比**：
  - gross pnl
  - net pnl（至少 `4/6/8 bps` round-trip 三档）
  - turnover
  - avg holding time
  - stop-out ratio

### 6.3 预期先看什么结果
这轮最先看 3 件事：
1. ORF governor 能不能显著降低 turnover；
2. 降 turnover 后，净 pnl / Sharpe / RoMaD 有没有改善；
3. 哪些 pair 明明 entry 看着不错，但一旦 ORF 估出来太长，就该直接 veto。

## 7. 先别自嗨的风险
1. **主论文当前在本环境里仍然是摘要级证据。** 我们拿到了 DOAJ / Avesis / Crossref / OpenAlex 元数据，但没有拿到全文逐表复核，所以这轮更像高质量组件 intake，而不是 clean replication。
2. **本地 probe 很粗。** 这里只做了静态 beta + ADF + OU half-life，没做滚动 cointegration、也没做完整成本后组合回测。
3. **major-coin spot pair 不代表全部 universe。** 它更多是告诉我们 cadence 不能拍脑袋，不是告诉我们“BNB/BTC 就一定是最好那组”。
4. **ORF 可能是 regime-dependent。** 同一 pair 在高波动 / 低波动、亚洲盘 / 美盘下，最优 bucket 可能会漂。

## 8. 这轮最值得记住的 desk 化结论
如果只记一句：

> **pairs alpha 现在更该先补“多久动一次”这层 governor，而不是继续盲加 entry 条件。最近窗口里，`3m/5m` 还能看到 pocket，`15m` 不应默认稳健。**

## 9. 来源
1. **Bağcı, M., & Kaya Soylu, P. (2024). _Classification of the optimal rebalancing frequency for pairs trading using machine learning techniques_. Borsa Istanbul Review, 24, 83–90.**
   - DOI: `10.1016/j.bir.2024.12.004`
   - Readable URL: `https://doi.org/10.1016/j.bir.2024.12.004`
   - DOAJ: `https://doaj.org/article/ea8fd49abc0e419bb95b28b581605866`
   - Avesis metadata page: `https://avesis.marmara.edu.tr/yayin/6148063e-e17d-406d-8108-6497f5d81e61/classification-of-the-optimal-rebalancing-frequency-for-pairs-trading-using-machine-learning-techniques`
2. **MattiDeBeer. _ml-statistical-arbitrage_. GitHub repository.**
   - Repo URL: `https://github.com/MattiDeBeer/ml-statistical-arbitrage`
   - 本地读过：`README.md`、`models/statarb_policy.py`、`envs/binance_trading_enviroment.py`、`scripts/algo_dataset_generator.py`
3. **本地 Binance Spot portability probe（2026-04-05）**
   - 标的：`BTCUSDT / ETHUSDT / SOLUSDT / BNBUSDT`
   - 频率：`3m / 5m / 15m`
   - 样本：各频率每个标的最近 `2400` 根 close
   - 方法：静态 beta spread、ADF p-value、OU half-life
   - 结果摘要：`3m/5m` 仍见可疑 pocket；`15m` 最近窗口在所测 5 组 pair 上整体明显变钝
