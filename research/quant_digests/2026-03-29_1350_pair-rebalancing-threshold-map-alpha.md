# 别把高频 pairs 又写成“固定阈值随手拍”：这篇 2025 *Computational Economics* 更该先测的是「pair-rebalancing MR × correlation-signed threshold map」完整 raw alpha
- 时间：2026-03-29 13:50 UTC
- 类型：2025 *Computational Economics* 开放获取全文 PDF（Springer 可读）+ 本地表格抽取 + Binance USDⓈ-M Perpetual 公共 `15m` threshold proxy
- 主题类型：raw alpha
- 基础 alpha：**两资产等权组合的 pair-rebalancing mean reversion**——当一条腿的组合权重/市值相对另一条腿偏离超过阈值，就卖高配腿、买低配腿，吃的是相对权重回摆；这篇 paper 新增的关键不是“pairs 会回归”本身，而是 **不同相关性 pair 应该用多高阈值才更像样**。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/rebalancing/threshold-governance/correlation-map/high-frequency/binance/perpetual/15m/5m/1m/3m/paper/public-data/cost
- 证据类型：全文论文证据 + 本地表格级结果抽取 + Binance perp desk proxy

## 1. 这次看了什么
先把 **base alpha** 说清楚：

> **这不是 filter，也不是纯 ML 选阈值 demo。它的 alpha 本体就是：两条腿相对涨跌失衡后，做一次向等权状态回摆的 rebalancing。**

翻成人话：
- 如果 pair 里 A 这条腿涨得明显快于 B，组合就不再是 50/50；
- 一旦偏离超过阈值，就卖掉一部分 A、补一些 B；
- 之后如果相对关系回摆，组合就把这段“高卖低买”的 rebalancing alpha 吃下来。

这篇东西最值得 intake 的，不是“Random Forest 比别的分类器好”这种表层结论，而是更直接的一句：

> **高频 pair-rebalancing 这条 raw alpha 可以单独活成完整策略，但它不是所有 pair 都该用同一个 threshold；threshold 本身就是决定能不能活下来的核心参数。**

一句话核心结论：

> **对高相关 pair，低阈值更合理；对弱相关/负相关 pair，最优阈值会更高。真正值得 desk 先搬的，是“相关性签名 → 阈值分层”这张阈值地图。**

一句话它怎么证明：

> **作者拿 Binance 上 50 个 crypto 资产的两年分钟级数据，枚举全部 pair，逐个扫 `1%~30%` 阈值求最大利润，再用 pair 的均值、方差、偏度、峰度、VaR、相关系数去分类“最优阈值落在哪个区间”，最后用 2024 年新样本做 out-of-sample 验证。**

## 2. 核心结论
### 2.1 这篇 paper 真正新增了什么
最近我们已经 intake 过不少 pairs / stat-arb 材料，但很多主题更偏：
- 怎么选 pair
- 怎么定义 spread
- 用 cointegration / OU / copula / Hurst 哪套信号

而这篇 2025 paper 补的是另一块常被写得很糊的东西：

> **同一个 pair-rebalancing alpha，到底该用多宽的 trigger threshold？**

这不是小参数。阈值太低：
- 交易次数暴涨
- 成本吃人
- 容易在噪声里来回 rebalance

阈值太高：
- 该吃的回摆根本轮不到你
- 高相关 pair 常常等不到那么大的偏离

所以这篇最值钱的地方，不是再给一个新 spread，而是：
**把 threshold governance 从拍脑袋，推进成可由 pair 统计属性驱动的策略组件。**

### 2.2 论文里最该记住的数字
作者用的是 **Binance 50 个 crypto 资产、2022~2023 两年、每分钟价格**，把所有 pair 全部扫了一遍。结果先看 pair 分布：
- **正相关 pair：18,582 个**
- **弱相关 pair：7,216 个**
- **负相关 pair：3,602 个**

然后做最优阈值区间分类：
- **二分类**：`0~15%` vs `15~30%`
- **三分类**：`0~10% / 10~20% / 20~30%`
- **四分类**：`0~7.5% / 7.5~15% / 15~22.5% / 22.5~30%`

最值得记的不是模型名，而是结构结论：
- **正相关 pair 的最优阈值明显偏低**，大量落在低阈值区间；
- **负相关 pair 的最优阈值明显偏高**，更常落在高阈值区间；
- 也就是：**相关性越低，最优 threshold 越高。**

模型层面，Random Forest 全面最好：
- **正相关 pair，二分类平均准确率 `87.5%`，最好 `89.1%`**
- **弱相关 pair，二分类平均准确率 `84.0%`，最好 `85.8%`**
- **负相关 pair，三分类平均准确率 `76.9%`，最好 `81.0%`**

更重要的是 out-of-sample：作者拿 **2024 年 1~2 月** 的新样本再测，RF 仍然没崩：
- **正相关 pair，二分类测试平均准确率 `92.2%`，最好 `93.9%`**
- **弱相关 pair，三分类测试平均准确率 `62.9%`，最好 `65.1%`**
- **负相关 pair，三分类测试平均准确率 `76.9%`，最好 `79.4%`**

论文给的最直观交易例子也值得记：
- **STX-THETA（2024-02）**，实际最优阈值 **`24%`**，pair-rebalancing 利润 **`41.2%`**
- **MANA-THETA（2024-02）**，实际最优阈值 **`30%`**，利润 **`25.9%`**
- **DOGE-STX（2024-02）**，实际最优阈值 **`29%`**，利润 **`25.1%`**

这些数字不代表 desk 可以直接照搬月度大阈值，但它们说明一件事：

> **threshold 选对和选错，真不是小改小修，而是会直接决定这条 pair alpha 最后像不像一条策略。**

## 3. 为什么和当前项目直接相关
先回答这轮最关键的问题：

> **它为什么比继续补一个新的 raw alpha headline 更值得？**

答案是：
**因为 pairs / stat-arb 素材池目前并不缺“spread 怎么定义”，更缺“策略上线时到底该怎么定 threshold”。**

也就是：
- 当前库里已经有不少 `cointegration / z-score / OU / copula / Hurst / multi-leg basket`；
- 但真正会卡 live 的，往往不是 pair 选不出来，而是 **trigger 设太窄或太宽**；
- 这篇 paper 虽然不是新 pair family，却给了一个能直接落成 `trade on / trade off` 规则的治理层：**相关性不同，threshold 默认就不该一样。**

所以它和当前项目的关系非常直接：
1. **仍然是 raw alpha，不是纯 filter。**
2. **而且是完整策略**：entry / sizing / cost / threshold sweep 都给了。
3. **对后续复现很友好**：公开可得 Binance 数据就够做最小实验。
4. **它补的是 pairs live-deployment 里最容易写糊的一层。**

## 3.5 策略拆解（必填）
- 方向属性：**pairs / stat-arb / relative-value / mean reversion**
- 基础 alpha：**两资产相对权重偏离过大后，向等权状态回摆带来的 rebalancing alpha**
- 论文主口径：
  - 数据：Binance 50 个币的 **BTC quote 市场**分钟级价格
  - 组合：任意两资产组成 **等权 pair**
  - 触发：当某条腿相对另一条腿的总市值比值超过 `1 + T`
  - 动作：卖出相对高配腿、买入相对低配腿，直到回到更均衡状态
  - 成本：显式计入 **`0.1%` taker fee**
  - 阈值：扫 **`1%~30%`**，再把最优阈值落点做分类
- 对 desk 的短周期翻译：
  - `raw alpha layer`：高相关 pair 的相对偏离 → 低阈值 rebalancing
  - `governance layer`：用 rolling corr / variance / skew / kurtosis / VaR 给 pair 分配 threshold bucket
  - `execution layer`：`15m` 生成信号，`5m/1m` 做切片/盘口 veto
  - `risk layer`：流动性门槛、单 pair notional cap、并发上限、max hold

## 4. 论文里的完整策略机制
### 4.1 原始 HFPT 算法到底在做什么
作者把它叫作 **HFPT (High Frequency Pairs Trading)**，但它和经典 `spread z-score` pairs 不完全一样。

它不是先估一个公平 spread 再赌 spread 均值回归，而是更接近：
- 初始建一个 **50/50 等权双资产组合**；
- 之后只盯着这两条腿的组合价值是否失衡；
- 超过阈值就 rebalance 回去。

所以这条 alpha 更像：

> **relative-weight mean reversion / threshold rebalancing alpha**

而不是传统教科书式的 `cointegration residual`。

### 4.2 这条策略为什么对 crypto 尤其有意思
因为 crypto 尤其容易出现：
- 同向大 beta 背景下的相对强弱漂移
- 高噪声下的短期超配 / 低配
- 但又不是每个 pair 都会乖乖按同一阈值回摆

这正是 paper 想解决的：
- **pair-rebalancing 的 alpha 本体可以统一**；
- **threshold 则必须个性化。**

### 4.3 threshold map 的最实用读法
如果只偷 paper 里一件东西，我不会先偷 RF 模型，而会先偷这句：

> **正相关 pair 默认先试低 threshold；弱相关 / 负相关 pair 才考虑更高 threshold。**

这对 desk 的意义非常大，因为它让第一轮 grid 不用瞎扫整个空间：
- 对高相关 pair：先看 `2%~8%`
- 对中等相关 pair：先看 `6%~15%`
- 对低相关 / 反向结构：才看 `15%+`

也就是说，它给的是 **parameter search 的先验地图**。

## 5. Binance USDⓈ-M Perpetual 公共 `15m` threshold proxy
我补了一个很轻的 desk proxy。先说明：

> **这不是原论文的硬复刻。**

它只是测试 paper 里最值得搬的那句：
**在 liquid-major perp 口径里，高相关 pair 的最优 trigger 是否也更偏低阈值。**

### 5.1 proxy 口径
- 数据：Binance USDⓈ-M Perpetual 公共 `15m` klines
- 样本：**2026-03-13 23:00 UTC ~ 2026-03-29 13:45 UTC**
- bar 数：**1,500 根**
- universe：`BTC ETH SOL XRP BNB DOGE ADA LINK LTC AVAX`
- pair 数：全部两两组合，共 **45 个 pair**
- 交易逻辑：做一个**等权 rebalance proxy**——当两腿市值偏离超过 threshold，就把组合拉回更均衡状态
- 成本：先按 **单边 `4 bps`** 做简化 proxy
- 扫描阈值：`2% / 4% / 6% / ... / 20%`

### 5.2 proxy 结果
这个 pocket 里，45 个 pair **全部都是高正相关**：
- **median corr = `0.835`**

最重要的不是收益，而是 threshold 分布：
- **median best threshold = `4%`**
- 最优 threshold 计数：
  - `2%`：**21 个 pair**
  - `4%`：**8 个 pair**
  - `6%`：**11 个 pair**
  - `8%`：**4 个 pair**
  - `10%`：**1 个 pair**
  - `12%+`：**0 个 pair**

也就是说：

> **在这段 liquid-major `15m` 样本里，高相关 pair 基本都只在低单数字 threshold 区间里才有交易发生；`10%+` 基本已经大到像不存在。**

这点和论文对正相关 pair 的结论是同向的。

### 5.3 但别误读成“已经能交易”
收益层面，proxy 很诚实地给了一个负面提醒：
- 45 个 pair 的 **median best return 约 `-6.19%`**
- 即便取每个 pair 自己最好的 threshold，结果也普遍没活下来
- 最好的几对也只是：
  - `ETH-LTC`：约 **`-3.64%`**
  - `XRP-LTC`：约 **`-3.71%`**
  - `DOGE-LTC`：约 **`-4.16%`**

翻成人话：

> **threshold map 这件事大概率是对的，但在我们这段 liquid-major `15m` 样本里，pair-rebalancing 这条 alpha 本体并没有因此自动变成能收租的现成 pocket。**

这也是这次 intake 很值钱的地方：
- **参数治理的方向对**；
- **但 alpha 本体在 major-perp 上仍然不够强。**

## 6. 这组结果该怎么解读
### 6.1 论文和 desk proxy 一致的地方
一致的是：
- **高相关 pair 确实更适合低 threshold**；
- 在 major-perp `15m` 上，`10%+` 这种大阈值几乎失去现实意义；
- 所以 desk 不该再把 high-corr pairs 的 threshold 起步点写得太宽。

### 6.2 论文和 desk proxy 不一致、但也很重要的地方
不一致的是：
- 论文里这条策略可以在更广泛 pair 池和更长历史里找到高利润 pocket；
- 但我这次 liquid-major `15m` proxy 没看到它在成本后直接成立。

这并不一定说明 paper 错，而更像说明：
1. 原论文数据是 **BTC quote 现货结构**，不是我们现在的 major perp；
2. 论文允许更广泛、更异质的 pair 池；
3. major-perp universe 太“干净”，高相关但相对波动未必够大；
4. 我这里样本只有最近约两周，且是更强的可交易性约束口径。

所以更稳妥的结论是：

> **这篇 2025 paper 值得进入 raw-alpha 素材池，但更适合被 intake 为“pairs threshold governance 模块”，而不是直接被宣传成 liquid-major `15m` ready-made alpha。**

## 7. 风险与保留意见
1. **这条 alpha 和传统 cointegration pairs 不一样。**
   它更像 threshold rebalancing，而不是 residual z-score mean reversion；不要混成一类。
2. **论文的赢家样本包含弱相关和负相关 pair。**
   但我这次 liquid-major perp proxy 几乎只有高相关 pair，无法验证 paper 的高阈值 bucket 是否在低/负相关组里更有料。
3. **desk proxy 不是原算法逐字复刻。**
   它是为了先测“threshold map 是否方向正确”，而不是论文收益复现。
4. **major-perp 的现实约束更强。**
   如果 pair 本体 edge 不够，单靠调 threshold 不会凭空把它救活。

## 8. 下一步怎么测
### 8.1 先把 universe 扩到“可交易但不只剩 top majors”
第一步不要继续只测 `BTC/ETH/SOL/...` 这种最干净的大币。
建议分三层：
1. `top majors`
2. `mid-cap liquid perps`
3. `可交易尾部但有足够成交的 alts`

要验证的就是：

> **pair-rebalancing alpha 会不会只在“相关但不太同质”的中段 universe 才开始有空间。**

### 8.2 先把 threshold grid 按 corr bucket 缩窄
下一轮别再全局扫一遍 `1%~30%`。
直接按先验做：
- `corr >= 0.7`：先测 `2%~8%`
- `0.4 <= corr < 0.7`：先测 `6%~15%`
- `corr < 0.4`：先测 `12%~25%`

这样更符合这篇 paper 真正提供的新增价值。

### 8.3 补真正 desk 需要的 veto
raw alpha 层之外，至少要补：
- 单 pair 流动性下限
- 单腿 funding 异常 veto
- max hold
- event / macro 时钟禁做窗口
- 盘口滑点约束

因为这条 alpha 很容易在“理论可 rebalance、实盘太贵”之间断掉。

### 8.4 做一个最关键的对照
同一批 pair，必须并排测：
1. **固定 threshold baseline**
2. **corr-bucket threshold map**
3. **rolling moment + RF threshold classifier**

如果 2 比 1 好，而 3 又能进一步改善，才说明 paper 这套 threshold governance 真能从论文进入 desk。

## 9. 研究结论（给自己留一句话）
**这篇 2025 *Computational Economics* 真正值得 intake 的，不是“又一个 high-frequency pairs paper”，而是：pair-rebalancing 这条 raw alpha 的成败，很大程度取决于 threshold governance；而 threshold 又明显受 pair 相关性结构影响。**

但 current desk proxy 也提醒得很清楚：

> **在 liquid-major `15m` perp 口径里，这条策略的最佳 threshold 确实落在低单数字区间，但 alpha 本体暂时还没活。**

所以它当前最合理的位置是：
- **进入 raw-alpha 素材池**；
- 同时作为 **pairs threshold governance** 的强候选模块；
- 而不是被过度写成“已经完成短周期迁移”。

## 10. 来源与链接
1. **Bağcı, M., & Kaya Soylu, P. (2025). _The Optimal Threshold Selection for High-Frequency Pairs Trading via Supervised Machine Learning Algorithms_. Computational Economics.**
   - Authors: Mahmut Bağcı; Pınar Kaya Soylu
   - Year: 2025
   - Title: *The Optimal Threshold Selection for High-Frequency Pairs Trading via Supervised Machine Learning Algorithms*
   - Venue: *Computational Economics*
   - DOI: `10.1007/s10614-025-10958-5`
   - DOI URL: `https://doi.org/10.1007/s10614-025-10958-5`
   - Readable URL: `https://link.springer.com/article/10.1007/s10614-025-10958-5`
   - PDF URL: `https://link.springer.com/content/pdf/10.1007/s10614-025-10958-5.pdf`
   - Repo URL: `N/A（文中未提供公开代码仓库）`

2. **Binance Developers. USDⓈ-M Futures API – Kline/Candlestick Data.**
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

## 11. 本地相关产物
- Digest：`research/quant_digests/2026-03-29_1350_pair-rebalancing-threshold-map-alpha.md`
- Proxy artifact：`reports/artifacts/quant_digest_threshold_pairs_proxy_2026-03-29.json`
- 页面 URL（发布后）：`https://jp.jerrypsy.top/momentum/reading/quant_digests/2026-03-29_1350_pair-rebalancing-threshold-map-alpha.html`
