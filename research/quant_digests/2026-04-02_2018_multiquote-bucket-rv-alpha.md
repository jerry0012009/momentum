# 别把这篇 2024 *International Journal of Financial Studies* 论文只读成 fiat-quote 小众套利：对 short-cycle desk，更该先测的是「same-underlier 多报价 bucket × convex allocator」这条完整 relative-value raw alpha
- 时间：2026-04-02 20:18 UTC
- 类型：2024 *International Journal of Financial Studies* 论文摘要 / Crossref metadata + arXiv 摘要 + 作者开源代码仓库 source audit（`README.md` + `optimal_trading_technique.py`）+ Binance Spot `1m/3m/5m/15m` public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：**同一底层资产**在不同报价资产/币种上的相对价格短时偏离，后续存在向共同锚点回归的压力；alpha 本体是 **same-underlier cross-quote / relative-value / stat-arb mean reversion**，不是优化器本身。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/relative-value/stat-arb/same-underlier/cross-quote/multiquote/bucket/mean-reversion/convex-optimization/market-neutral/spot/1m/3m/5m/15m/paper/repo/public-data/cost
- 证据类型：论文摘要元数据（主证据）+ 开源源码（主证据）+ Binance 公开报价梯度最小快检（transfer 证据）

## 1. 这次看了什么
### 一句话核心结论
**这篇材料真正值得 intake 的，不是“Kraken 上 ETH 对多法币报价可以套利”这个表面故事，而是它把一条非常适合 short-cycle desk 的 raw alpha 讲清楚了：同一底层、多个报价腿会同时冒出相对偏离，但真正能落地的是“pair signal 负责找错价，convex allocator 负责解决多信号同时出现时到底该配哪几腿、配多大”。**

### 一句话它为什么适合当前 desk
最近 digest 已经补了不少 `pairs / coint / residual / cross-venue / funding`，但大多数仍停在 **两腿 spread 的 entry/exit**；这篇更稀缺的地方是：
**它把 same-underlier relative-value 从“两腿单独做”推进成“多腿 bucket 一起解仓位冲突”的完整策略骨架。**

## 2. base alpha 是什么
这轮的 **base alpha 很清楚**：

1. 选同一底层资产在不同报价腿上的价格序列；
2. 对每一组报价腿构造 log-price residual / spread；
3. 当某条 residual 明显偏离其稳定关系时，做多低估腿、做空高估腿；
4. 如果同一时刻多条 spread 同时触发，不是每条都各自满仓，而是统一交给一个 risk-aware allocator 共同解仓位；
5. 等 spread 回归、组合约束触发、或时间/成本条件失效时退出。

翻成人话：
**不是赌 ETH 单边涨跌，而是赌“同一个 ETH，不该因为报价资产不同而被短时标出明显不同的相对价格”；如果同一时刻多个报价腿都错了，就用统一的仓位解算器，避免互相打架。**

所以这轮主题的定位是：
- raw alpha：**same-underlier cross-quote mean reversion**
- execution / portfolio layer：**多 signal 冲突解算**
- risk layer：**在收益与风险之间做显式 trade-off，而不是一条一条 spread 盲开**

## 3. 为什么这轮值得写
### 3.1 它和最近 intake 不重复的地方，不在“又一个 pairs”
最近已经有不少：
- `cointegration spread z-score fade`
- `dynamic coint percentile threshold`
- `cross-venue basis / funding carry`
- `pairs sizing / graduation / daily throttle`

这些大多还是 **两腿交易卡**。这篇真正不同的是：
**它讨论的是“同一底层有多条相对价值机会一起冒出来时，怎么把它们作为一个 bucket 来配仓，而不是把每条 spread 当孤岛”。**

### 3.2 它补的是 desk 现在还缺的一层
`MAINLINE1_STRATEGY_FACTOR_MAP`、`FACTOR_BACKLOG` 和最近几篇 pairs digest 已经把：
- pair selection
- spread construction
- threshold / exit
- veto / cost gate

补得很多了；但 **多信号同时触发时的统一分配器** 还相对稀缺。这篇提供的正是：
**同一 alpha family 内部的 portfolio coordinator。**

### 3.3 它对 1m / 3m / 5m / 15m 的适配非常自然
原文是“法币报价腿”，但 desk 更容易落地的读法其实是：
- `ETHUSDT / ETHUSDC / ETHFDUSD`
- `BTCUSDT / BTCUSDC / BTCFDUSD`
- 同一底层跨 venue 的 spot/perp 同报价腿

也就是把“不同 fiat quote”翻译成“不同 stable quote / 不同 venue quote”。这对我们当前短周期 desk 明显更贴身。

## 4. 来源信息
### 论文来源
- **Authors：** Hongshen Yang, Avinash Malik
- **Year：** 2024
- **Title：** *Optimal Market-Neutral Multivariate Pair Trading on the Cryptocurrency Platform*
- **Venue：** *International Journal of Financial Studies*
- **DOI：** <https://doi.org/10.3390/ijfs12030077>
- **Readable URL：** <https://www.mdpi.com/2227-7072/12/3/77>
- **arXiv URL：** <https://arxiv.org/abs/2405.15461>
- **arXiv DOI：** <https://doi.org/10.48550/arXiv.2405.15461>

### 工程来源
- **Repo owner：** `Hongshen-Yang`
- **Year：** 2024
- **Title：** `optimal-trading-technique`
- **Venue：** GitHub repository
- **Repo URL：** <https://github.com/Hongshen-Yang/optimal-trading-technique>

## 5. 论文 / 源码里真正有用的策略骨架
### 5.1 universe：同一底层、多报价腿，而不是任意两币硬配对
README 和代码写得很清楚，默认示例直接使用 Kraken OHLCVT：
- `ETHUSD`
- `ETHCAD`
- `ETHGBP`
- `ETHEUR`

也就是说，作者不是在做随便两条 unrelated crypto 序列的统计套利，而是在做：
**一个底层（ETH）在多种报价腿上的相对价值偏离。**

这件事非常关键，因为这种结构天然满足两点：
1. 基本面锚点相同；
2. 价差更多来自报价腿、流动性、交易时段和微观结构摩擦，而不是底层资产自身叙事差异。

### 5.2 signal：先构造多条 pair residual，再在 residual 超阈值时开仓
源码主函数 `arbitrage_trade()` 的流程大致是：

1. 读入多条同底层 OHLCVT；
2. 先要求全体价格相关性极高（代码里甚至用了 **`corr > 0.99`** 的硬门槛）；
3. 对每个报价腿组合做 log-price OLS；
4. 用回归残差构造 spread；
5. 可选再做 ADF 检验保留更稳的 spread；
6. 把 spread 标准化成 z-score；
7. 当 residual 偏离足够大时，做多低估腿、做空高估腿。

翻成人话：
**alpha 不是“哪个报价腿绝对便宜”，而是“哪条报价腿相对其余报价腿偏得不正常”。**

### 5.3 这篇最该偷走的，不是某条固定 spread，而是 bucket allocator
作者真正和普通 pairs 策略拉开差距的地方是 `build_prob_cons()`：

- 目标函数：
  - **maximize expected return - λ × expected risk**
- 风险项：
  - 用 pairwise covariance matrix 构造
- 约束项：
  - 每种报价货币的 cash 不能超限
  - long/short 两腿要满足价格比例匹配
  - 交易成本可选显式并入

这意味着同一时间如果有多条 spread 一起亮灯，系统不是“看见一条下一条”，而是：
**先把所有候选腿放进同一个优化问题，再统一吐出本根 bar 该开的多空腿和权重。**

这正是 desk 当前最值得拿走的部分。

### 5.4 entry / exit / sizing / risk / cost 五件事，源码都给了
从源码能清楚读出的策略卡如下：

- **Entry：** 某条 spread 的偏离超过开仓阈值时进入候选集；
- **Direction：** z-score 为正时 short rich leg / long cheap leg；z-score 为负时反过来；
- **Sizing：** 不是固定手数，而是优化器在现金约束和风险惩罚下给权重；
- **Exit：** spread 回到均值带附近即平仓；
- **Cost：** `TX_COST = 0.001`，即默认 **单边 10 bps**；
- **Risk aversion：** `LAMBDA = 0.5`。

对 desk 来说，这已经是完整策略，而不是一段只会“发现价差”的研究脚本。

## 6. source audit 后最值得记住的硬数据点
1. **样本期：** 论文摘要明确写的是 **2020–2022**，覆盖 bull run 到 bear run。
2. **headline：** 论文摘要给出的 **annualized profit = 15.49%**。
3. **默认交易对象：** 开源代码直接给出 **ETH 对 USD/CAD/GBP/EUR** 的多报价腿结构。
4. **默认频率：** repo 里明确有 `do1min()`、`do5min()`、`do60min()` 三套入口。
5. **默认成本：** repo 默认 **`TX_COST = 0.001`**，即单边 10 bps。
6. **默认风险权重：** repo 默认 **`LAMBDA = 0.5`**，原始资金 `ORIG_AMOUNT = 10000`。

再补两个对实现最有用的参数：
- **`CROSSING_MEAN = 9`**
- **`CROSSING_MAX = 11`**

但这里必须立刻补一句 source-audit 结论：
**代码里阈值比较写法比较“怪”——它把 z-score 和 `spread.std × threshold` 混用，所以这两个数字不能直接当 literal 9σ/11σ 理解；移植时必须重写成我们熟悉的纯 z-score 参数。**

## 7. Binance 公开数据最小快检：这条 alpha 在我们关心的短周期上还活着吗？
我没有去硬复刻论文全套，而是做了一个更贴 desk 的 public-data probe：

- **标的：** `ETHUSDT / ETHUSDC / ETHFDUSD`
- **市场：** Binance Spot 公开 kline
- **逻辑：** 同一底层、不同 stable quote 的 residual spread
- **判定：** 统计 `2σ` 偏离后回到 `|z| < 0.5` 的完成次数与回归速度

### 7.1 1m：最短周期也能看到相对价值回归
最近 `1000` 根 `1m` 数据里：
- `ETHUSDT-ETHUSDC`：spread std 约 **0.70 bp**，完成 **31** 次 `2σ → 0.5σ` 回归，median close **3 bars**，half-life 约 **1.32 bars**；
- `ETHUSDT-ETHFDUSD`：spread std 约 **1.11 bp**，完成 **32** 次回归，median close **2 bars**，half-life 约 **1.03 bars**；
- `ETHUSDC-ETHFDUSD`：spread std 约 **1.24 bp**，完成 **19** 次回归，median close **3 bars**，half-life 约 **1.17 bars**。

翻成人话：
**1m 上这条 alpha 不是没有，但 edge 很薄，非常依赖费用、排队和是否能避免把 1bp 级别偏离全交给手续费。**

### 7.2 3m / 5m：是当前最像“可做最小实验”的区间
最近 `1000` 根 `3m` 数据里：
- `ETHUSDT-ETHFDUSD`：spread std **1.62 bp**，触发率 **5.3%**，完成 **13** 次回归，median close **7 bars**；
- `ETHUSDC-ETHFDUSD`：spread std **1.56 bp**，完成 **23** 次回归，median close **3 bars**。

最近 `1000` 根 `5m` 数据里：
- `ETHUSDT-ETHFDUSD`：spread std **1.75 bp**，`2σ` 触发率 **4.4%**，完成 **12** 次回归，median close **4.5 bars**，half-life **2.32 bars**；
- `ETHUSDC-ETHFDUSD`：spread std **1.55 bp**，完成 **18** 次回归，median close **5 bars**，half-life **1.61 bars**。

这组结果最重要的意思不是“立刻上线 ETH stablequote arb”，而是：
**same-underlier multi-quote 的 raw alpha 在 `3m/5m` 上仍然能看到可重复的均值回归形状，适合做 bucket allocator 的最小实验。**

### 7.3 15m：频次更少，但并没有死
最近 `1000` 根 `15m` 数据里：
- `ETHUSDT-ETHFDUSD`：完成 **6** 次回归，median close **4.5 bars**；
- `ETHUSDC-ETHFDUSD`：完成 **12** 次回归，median close **7.5 bars**；
- `ETHUSDT-ETHUSDC`：完成 **4** 次回归，median close **7.5 bars**。

结论很直接：
- `15m` 还能做，但更像 **低频 bucket relative-value**；
- `3m/5m` 更像当前 desk 的首轮实验区；
- `1m` 只有在成本极低时才有意义。

## 8. 对当前 1m / 3m / 5m / 15m 的可迁移结论
### 8.1 最适合 desk 的移植方式，不是法币报价，而是 stable-quote / venue-quote
原论文的“多法币报价”对我们是启发，不是照抄对象。最顺手的移植顺序应是：

1. **same-underlier stable-quote bucket**
   - 例：`BTCUSDT / BTCUSDC / BTCFDUSD`
   - 例：`ETHUSDT / ETHUSDC / ETHFDUSD`
2. **same-underlier cross-venue bucket**
   - 例：Binance / OKX / Bybit 同标的同报价腿
3. **同底层 spot-perp quote bucket**
   - 例：spot / perp / perp-on-another-venue 的统一 relative-value 解算

### 8.2 它服务于哪类 raw alpha
这篇不是孤立主题，而是能服务至少三类现有 raw alpha：
1. **same-underlier cross-quote mean reversion**
2. **cross-venue relative-value mean reversion**
3. **spot-perp / perp-perp 同底层价差回归**

因此这轮最好把它看成：
**raw alpha 本体 = multi-quote mean reversion；优化器 = 这类 alpha 的 portfolio operating system。**

### 8.3 它比继续补“普通两腿 pairs”更值得的原因
如果继续只补两腿 pairs，我们得到的是更多 spread 卡片；
这篇能补的是：
**当 3 条 spread 同时亮灯时，系统应该只开一条、全开、还是配成一篮子？**

这个问题更接近 live trading，而不是 paper trading。

## 9. 最小可复现实验
### 实验 A：stable-quote bucket（最优先）
- **标的：** `BTC` 与 `ETH` 两个底层各自一组 stable quotes
- **腿：** `USDT / USDC / FDUSD`
- **bar：** 先 `5m`，再 `3m` 与 `15m`
- **spread：** rolling OLS residual
- **entry：** `|z| >= 2.0`
- **exit：** `|z| <= 0.5` 或 max-hold `10 bars`
- **allocator baseline：** 每条 trigger 的 spread 各自固定 `1x`
- **bucket allocator：**
  - 目标：`maximize E[r] - λ·risk`
  - 风险：pairwise covariance of quote legs
  - 约束：每个 quote leg 的净敞口 / 名义资金上限
- **cost：** 单边 `1 / 2 / 3 / 5 bps` 敏感性

要先回答的问题只有一个：
**当多个 stable-quote dislocation 同时出现时，统一 allocator 相比“各 pair 各干各的”，after-cost 的净收益 / 回撤 / 冲突仓位会不会更好？**

### 实验 B：cross-venue same-underlier bucket
- **标的：** `BTCUSDT` 或 `ETHUSDT`
- **venue：** Binance / OKX / Bybit
- **bar：** `1m / 3m / 5m`
- **目的：** 看 bucket allocator 能否替代“手写 venue priority rule”

### 实验 C：保留 raw alpha，本地重写 sizing / threshold 语义
由于 repo 原始 `CROSSING_MEAN / CROSSING_MAX` 语义不干净，移植时建议：
- 直接改成纯 z-score 阈值；
- `open_z = 2.0 / 2.5`
- `close_z = 0.25 / 0.5`
- `allocator_lambda = 0.0 / 0.25 / 0.5 / 1.0`

先把参数语义统一，再比较 bucket 与 independent-pair baseline。

## 10. 风险与局限
1. **原始交易对象很“干净”。** 同底层多法币报价天然比一般跨币种 pairs 更稳，所以 headline 不该直接外推到任意 alt pair。
2. **repo 依赖 Gurobi。** 复现门槛不算高，但确实不是零依赖脚本。
3. **阈值写法需要重构。** 这是这份开源代码最重要的 source-audit caveat。
4. **1m edge 极薄。** 快检已经说明很多 spread 波动只有 `1bp` 级别；若没有极低成本与高质量成交，1m 容易变成“统计上能回归，实盘上赚不到”。
5. **更像 relative-value 组件，不是全 market 通杀因子。** 它最适合的地方是同底层多报价、多 venue 的细颗粒错价管理。

## 11. 下一步怎么测
**下一步最该做的，不是先复刻论文 2020–2022 全样本，也不是先接 Gurobi，而是用我们最容易拿到的 stable-quote 公开数据做一个干净 ablation：同一套 residual entry/exit、同一套成本，只比较 `independent pairs` vs `bucket allocator`。**

如果这一步成立，这篇就不只是“又一篇 crypto pairs 论文”，而是能直接进入我们 `3m/5m/15m` 策略池的一条完整 raw alpha：
**同底层多报价错价负责给信号，bucket allocator 负责把这些信号变成不互相打架的 live 组合。**
