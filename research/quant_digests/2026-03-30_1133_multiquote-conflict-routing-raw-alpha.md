# 别把 same-underlier 多报价继续只做成单 pair z-score：这篇 2024 IJFS 更该先测的是「multi-spread conflict routing × no-idle-capital」完整 raw alpha
- 时间：2026-03-30 11:33 UTC
- 类型：2024 *International Journal of Financial Studies* 开放获取全文 PDF（arXiv accepted manuscript 可读）+ Binance Spot 公共 `1m/5m/15m` 多报价最小快检
- 主题类型：raw alpha
- 基础 alpha：**同一标的在多个 quote 市场之间的相对错价会回归；当同一时刻出现多条 spread 偏离时，用 multivariate routing / risk-aware allocation 而不是单 pair 孤立下单，去吃 spread convergence**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/same-underlier/multiquote/multivariate/conflict-routing/capital-allocation/market-neutral/spot/binance/eth/usdt/usdc/fdusd/1m/3m/5m/15m/paper/public-data/cost
- 证据类型：开放获取全文论文 + 公共 Binance 多报价最小实验口径

## 1. 这次看了什么
这次主看：

- **Hongshen Yang, Avinash Malik (2024)**
  **_Optimal Market-Neutral Multivariate Pair Trading on the Cryptocurrency Platform_**
  *International Journal of Financial Studies*。
  - DOI：`10.3390/ijfs12030077`
  - Readable URL：<https://arxiv.org/abs/2405.15461>
  - Journal DOI URL：<https://doi.org/10.3390/ijfs12030077>
  - Data availability（文中声明）：Kraken 可下载历史 OHLCVT 数据

这篇 paper 的 headline 表面上像“又一篇 crypto pairs 论文”，但它真正对 desk 有价值的，不是再讲一次 spread 会均值回归，而是：

> **当同一标的在多个 quote 市场上同时出现多条 spread 偏离时，如何把“冲突信号 + 共享资金池”写成一个可执行的 capital router。**

这点和我们最近几篇相近题材的 digest 有明显区别：
- 之前更常聚焦 **pair-level signal**：比如固定阈值、动态阈值、按 `|z|` 分层加仓；
- 这篇真正新增的是 **bucket-level allocation**：多个 spreads 同时亮灯时，不再一条一条各做各的，而是统一解决：
  - 哪些腿其实在纸面上可以净掉；
  - 哪些 quote 资金被重复占用；
  - 哪些机会该优先给仓位。

所以这轮不是补一个老 pairs baseline，而是在补：
**same-underlier multiquote raw alpha 的“路由层 / 资金分配层”完整骨架。**

## 2. 核心结论
### 2.1 先回答一句：这篇东西的 base alpha 是什么？
**base alpha = same-underlier 多报价之间的相对错价回归。**

更交易化地说：
- 同一标的（论文里是 `ETH`）同时对多个 quote（论文里是多种 fiat；desk 可换成 `USDT / USDC / FDUSD`）报价；
- 这些 quote 线之间会出现短时不同步；
- 当某一条或多条 spread 偏离其历史相对关系后，后续更值得先测的是 **spread convergence / mispricing correction**；
- 真正的增量不是“会不会回归”，而是：**多条 spread 同时偏离时，怎么做得比一条一条 pair trade 更有效率。**

所以它是明确的 **raw alpha**，不是 filter / regime / overlay。

### 2.2 论文里真正给出的完整策略部件
论文不是只给概念，实际上已经把完整骨架拆到了可复现程度：

1. **资产筛选（screening）**
   - 先选相关性高、协整关系稳定的 quote 资产进 bucket；
   - 用 Pearson correlation + Engle–Granger cointegration 做形成期筛选；
   - 明确排除会因为自身通胀/贬值而破坏 mean reversion 假设的 quote。

2. **入场 / 出场规则**
   - 对任意两条 quote 线，先算 `log-price spread`；
   - 再做 z-score 标准化；
   - 当 spread 偏离超过 `open_threshold` 开仓；
   - 当 spread 回到 `close_threshold` 内平仓。

3. **多信号冲突处理**
   - 如果同一时刻多条 pair 都亮灯，传统 pair-by-pair 做法会出现：
     - 同一 quote 被重复占用；
     - 一边 long 一边 short 的相互抵消腿仍然各自付费；
     - 部分资金闲置。
   - 论文的核心增量就是承认这些问题真实存在，然后把它正式写进分配层。

4. **资金分配优化（最值钱的部分）**
   - 目标函数是：
     - 最大化预期利润；
     - 同时最小化组合波动；
   - 用 `λ` 作为风险厌恶参数，把收益与风险做 bi-objective convex optimization；
   - 约束里显式写了：
     - 单条 pair 的 long/short 权重边界；
     - 每个 quote 的总占用不能超过 100%；
     - 按 underlying 单位回推后的 market neutrality。

5. **不要求外部裸卖空，也不要求把中间资产长期拿在手上**
   - 这是 paper 的一个很关键的 desk 友好点；
   - 它不是那种“逻辑上 market-neutral，执行上其实偷偷假设你能无限借券 / 无限 borrow”的纸面策略。

### 2.3 论文最关键的结果数字
论文给了几个很适合拿来当 intake 判断基准的数据点：

- **5m 样本、`λ = 1`**：年化收益 **15.49%**；
- **5m 样本、`λ = 0.5`（更激进）**：年化收益 **37.74%**，Sharpe **1.11**；
- **5m 样本、`λ = 2`（更保守）**：年化收益 **7.74%**；
- 论文还给出：OTT 平均比 baseline distance method **高约 2.72 倍**；
- `5m` 全周期样本里，OTT 共做了 **12,166** 笔交易，
  - 胜率 **54.4%**；
  - win/loss ratio **1.19**；
  - 平均持有 **5.09 小时**。

这些数字不等于我们可以直接照抄实盘；
但它们足够说明：
**这不是一篇只能产出 filter 的解释文，而是一条已经长出 entry / exit / sizing / risk 的完整策略线。**

## 3. 为什么这轮值得进当前 desk 的研究池
这轮值得，不是因为“pairs 又多了一篇”。而是因为它刚好补了我们当前素材池里一个经常缺失的东西：

> **pair-level alpha 很多，但 multivariate bucket 真到同时亮灯时，资金怎么路由，往往写得很含糊。**

对当前短周期 desk，这条线有三点现实价值：

1. **它是 raw alpha，不是二层配件。**
   base alpha 很清楚，就是 same-underlier 多报价错价回归。

2. **它直接补的是完整策略的“执行内核”。**
   最近我们已经积累了很多“怎么定义 spread / 怎么挑阈值”的材料；
   这篇更值钱的是补上：
   **多条 spread 一起动时，pair trade 该怎样统一分仓。**

3. **它天然映射到 `1m / 3m / 5m / 15m`。**
   论文主结果含 `1m / 5m / 60m`；
   而 desk 最小实验完全可以直接迁到：
   `ETHUSDT / ETHUSDC / ETHFDUSD` 或 `BTCUSDT / BTCUSDC / BTCFDUSD` 的公开多报价市场。

## 4. desk 口径的最小快检：Binance ETH 多报价
为了避免只停留在论文层，我用 Binance Spot 公共 K 线对 `ETHUSDT / ETHUSDC / ETHFDUSD` 做了一个极简快检。

### 4.1 快检口径
- 数据：Binance Spot 公共 `klines`
- 标的：`ETHUSDT / ETHUSDC / ETHFDUSD`
- 频率：`1m / 5m / 15m`
- 观察窗口：各频率最近 `1000` 根 bar
- 先做极简 pair-level proxy：
  - spread = `log(P_a / P_b)`
  - 形成期均值/标准差 = 样本内静态估计
  - `|z| > 2` 开，回到 `|z| < 0.5` 平
- **注意**：这只是最小 existence check，**没扣手续费、没扣 stablecoin 再平衡成本、也没做真正 multivariate allocator**。

### 4.2 结果：1m / 5m / 15m 都能看到可交易结构
#### `5m`
- `ETHUSDT vs ETHFDUSD`：最近 `1000` 根里，极简规则共平掉 **32** 笔，平均持有 **3.12** 根，平均 gross spread-capture **3.60 bps**；
- `ETHUSDC vs ETHFDUSD`：共 **16** 笔，平均持有 **7.50** 根，平均 gross **4.24 bps**；
- `ETHUSDT vs ETHUSDC`：共 **19** 笔，平均持有 **7.74** 根，平均 gross **2.02 bps**。

#### `1m`
- `ETHUSDT vs ETHFDUSD`：共 **28** 笔，平均持有 **3.39** 根，平均 gross **2.78 bps**；
- `ETHUSDC vs ETHFDUSD`：共 **23** 笔，平均持有 **3.65** 根，平均 gross **2.99 bps**；
- `ETHUSDT vs ETHUSDC`：共 **44** 笔，平均持有 **2.39** 根，平均 gross **1.54 bps**。

#### `15m`
- `ETHUSDT vs ETHFDUSD`：共 **18** 笔，平均持有 **8.50** 根，平均 gross **3.81 bps**；
- `ETHUSDC vs ETHFDUSD`：共 **4** 笔，平均持有 **59.0** 根，平均 gross **6.11 bps**；
- `ETHUSDT vs ETHUSDC`：共 **2** 笔，平均持有 **39.0** 根，平均 gross **3.52 bps**。

### 4.3 最关键的一条：多信号冲突是真问题，不是纸上问题
在最近 `1000` 根 `5m` bar 里：
- 至少有 **108** 根 bar 出现了 `>=1` 条 pair 信号；
- 其中有 **37** 根 bar 同时出现了 `>=2` 条 pair 信号。

在最近 `1000` 根 `15m` bar 里：
- 有 **61** 根 bar 出现 `>=1` 条信号；
- 其中 **19** 根 bar 同时出现 `>=2` 条信号。

这就是这篇 paper 值钱的地方。
如果绝大多数时候都只有单 pair 信号，那 multivariate router 只是装饰；
但现在 public quick check 已经说明：

> **多条 spread 同时亮灯并不稀有，资金冲突 / 腿抵消 / quote 占用重复是真实存在的。**

## 5. 真正值得 desk 先抄的，不是“multivariate”这个词，而是下面这三件事
### 5.1 抄“路由层”，不是只抄 `z-score`
单条 spread 的 z-score 大家都会写；
难点在于：
- 两条或三条 spread 同时偏离时；
- 哪条优先；
- 哪些腿可以内净掉；
- 哪个 quote 先吃满预算；
- 是否该把多个 pair 合成一个 bucket trade。

paper 真正值得抄的是：
**把这些执行上最脏的部分，提前写进 objective 和 constraints，而不是回测后拍脑袋补注释。**

### 5.2 抄“每个 quote 不能被重复花”的约束
这是非常 desk 化的一点。
很多 paper 默认你每条 pair 都能独立下单，但真实情况是：
- `USDT` 资金同时被 `USDT-USDC` 和 `USDT-FDUSD` 两条 spread 想拿去做多/做空；
- 如果不做统一预算，你会得到假的容量、假的年化、假的 hit rate。

### 5.3 抄“market-neutral 要回推到 underlying 单位”
因为最终你买卖的是同一个 underlying，
所以中性不是嘴上说 `long one pair / short another pair` 就够了，
而是要把权重映射回 underlying 数量后再检查敞口是否真的接近零。

这点对同币多报价策略尤其重要，
不然你看似是在做 quote spread，实际上偷偷带了 `ETH delta`。

## 6. 对 `1m / 3m / 5m / 15m` 的最小实验怎么落
### 6.1 数据源与公开性
第一版直接用公开数据，不需要私有 feed：
- Binance Spot 公共 `kline`：先做最小 existence check；
- 若要进入 replication，再升级到：
  - `aggTrades`
  - `bookTicker` / depth snapshots
  - 真实 maker/taker fee 假设
- 标的优先：
  - `ETHUSDT / ETHUSDC / ETHFDUSD`
  - `BTCUSDT / BTCUSDC / BTCFDUSD`
  - 再考虑 `SOL` 多报价。

### 6.2 base alpha 的第一版定义
1. **形成期筛选**
   - rolling `7d / 14d` 窗口；
   - 只保留相关性高、spread 稳定的 quote 对；
   - 第一版可以先用：
     - `corr > 0.95`
     - spread rolling std 稳定
     - 或 Engle–Granger `p < 0.05`。

2. **spread 信号**
   - 对 bucket 中每条 pair 计算：
     - `spread_ij = log(P_i / P_j)`
     - `z_ij = (spread_ij - mean_ij) / std_ij`
   - 开仓：`|z_ij| >= 2.0` 或 rolling percentile `>= 97.5%`
   - 平仓：`|z_ij| <= 0.5`

3. **方向翻译**
   - 如果 `z(USDT-USDC) > 2`，说明相对历史看，`ETH` 在 `USDT` quote 上更贵，
     第一版就做：
     - 卖贵腿；
     - 买便宜腿；
     - 目标是等 spread 回归。

### 6.3 multivariate router 的第一版实现
先别一上来就求最优解；可以先做一个诚实的两步版：

**Step A：pair-level expected edge**
- `edge_ij = expected_spread_reversion_bps - fee_bps - slippage_bps - rebalance_cost_bps`
- 只有 `edge_ij > 0` 的候选才进池。

**Step B：bucket-level allocation**
在同一时刻，若有多条 pair 候选：
- 按 `edge / risk` 排序；
- 每个 quote 设置 budget cap；
- 每个 pair 设置 max weight；
- 任何新增仓位都不能让某个 quote 的总占用超过 100%；
- underlying 净敞口必须在容忍带内。

第二版再升级成论文里的形式：
- 目标：`max Σ(w * EP) - λ * portfolio_variance`
- 约束：
  - pair-level bounds
  - quote-level budget bounds
  - market-neutrality in underlying units

### 6.4 出场、风控、成本
**出场**
- base：`|z| <= 0.5` 平仓；
- timeout：
  - `1m` 最多持 `10~20` bars
  - `3m/5m` 最多持 `6~12` bars
  - `15m` 最多持 `4~8` bars
- stop：若 `|z|` 扩到 `3~3.5` 仍未回归，强制减仓或止损。

**仓位 / risk**
- `λ` 先测 `0.5 / 1 / 2` 三档；
- bucket gross cap：例如单 bucket 不超过总资金 `20%~30%`；
- 单 quote 占用 cap：例如不超过 bucket 预算的 `50%`；
- 同时亮灯太多时，宁可截断，也不要假设无限资金。

**成本**
- 必须显式计入：
  - maker/taker fee
  - spread crossing cost
  - quote 再平衡成本（尤其 `USDC/FDUSD` 不一定零摩擦）
  - 零费时代结束后的 fee regime 变化
- 如果后续换到 perp 版本，还要加：
  - funding
  - borrow / carry
  - inventory financing。

## 7. 这张卡最容易自欺的地方
### 7.1 把 stablecoin quote 差异误当“无风险送钱”
`USDT / USDC / FDUSD` 的差异有时确实会回归，
但有时它不是噪音，而是：
- quote 自身信用层级差异；
- 零费活动残留；
- 单一 quote 流动性/费率/用户结构变化。

所以不要默认所有 spread 都会强回归。
第一层就该先筛掉长期漂移、或 regime 明显变了的 quote 对。

### 7.2 只做 pair-level backtest，会夸大真实容量
如果三条 pair 同时亮灯，却让回测把同一份 `USDT` 重复拿去三次，
你得到的是假收益、假资金效率。

### 7.3 用 bar close 价替代可执行价，会高估净 edge
尤其在 `1m / 3m`：
- 实际上你看到的是 close，不是 fill；
- 真正能不能吃到 spread，需要 book 层验证。

所以这条线第一轮只负责证明“有结构”；
第二轮必须补 book / fee / queue realism。

## 8. 这篇 digest 最后的判断
**结论：值得进研究池，而且是偏高优先级的 raw alpha / 完整策略主题。**

但它值得进，不是因为论文证明了“pairs 还能赚钱”，而是因为它补上了一个更稀缺的部件：

> **当 same-underlier 多报价同时给出多条可交易 spread 时，如何把 signal selection、capital allocation、market-neutrality、quote budget 一次写完整。**

对 desk 而言，这比继续补一个新的 pairs 阈值论文更值钱，
因为它直接服务后续复现与实盘组件拆解：
- signal layer：spread deviation
- routing layer：多信号冲突解算
- sizing layer：风险厌恶 / 预算约束
- execution layer：quote 再平衡与成本治理

## 9. 下一步怎么测
按下面顺序做，别一上来堆复杂优化：

1. **先做 pair-level baseline**
   - `ETHUSDT / ETHUSDC / ETHFDUSD`
   - `1m / 5m / 15m`
   - 固定 `z-open / z-close` + 显式费用
   - 先确认每条 spread 单独是否还有 gross edge。

2. **再做 bucket-level conflict audit**
   - 统计每个 bar 同时亮灯的 pair 数；
   - 统计 quote 预算冲突发生率；
   - 统计如果不做路由，会夸大多少名义占用。

3. **再比三种 allocator**
   - equal-weight pair-by-pair
   - greedy `edge/risk` 路由
   - 论文式 `收益 - λ*风险` 优化

4. **最后才接入更真实执行**
   - bookTicker / depth
   - maker vs taker
   - stablecoin 再平衡成本
   - timeout / stop / queue realism

如果第三步已经能证明：
- multivariate router 相比 pair-by-pair 明显减少重复占用；
- 成本后仍保留可观净边；
那这条线就该升格到正式 replication queue。

## 10. 来源与链接
### 论文
- **Authors**: Hongshen Yang, Avinash Malik
- **Year**: 2024
- **Title**: *Optimal Market-Neutral Multivariate Pair Trading on the Cryptocurrency Platform*
- **Venue**: *International Journal of Financial Studies*
- **DOI**: `10.3390/ijfs12030077`
- **Readable URL**: <https://arxiv.org/abs/2405.15461>
- **Journal URL**: <https://doi.org/10.3390/ijfs12030077>
- **Repo URL**: 未见作者公开官方 repo

### 数据与最小实验口径
- **Paper data source**: Kraken historical OHLCVT（文内 data availability）
- **Kraken URL**: <https://support.kraken.com/hc/en-us/articles/360047124832-Downloadable-historical-OHLCVT-Open-High-Low-Close-Volume-Trades-data>
- **Desk quick-check data source**: Binance Spot public klines
- **Binance docs**: <https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#klinecandlestick-data>

### 这轮最该记住的一句话
**别把同币多报价只做成“某一条 pair 的 z-score 触发器”；真正更值得 desk 先复现的，是 multi-spread 同时亮灯时的 conflict routing + no-idle-capital allocator。**
