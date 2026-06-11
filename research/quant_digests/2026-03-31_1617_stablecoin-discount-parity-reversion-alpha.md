# 别把这篇 2025 NBER / BFI stablecoin 论文只读成监管讨论：对 desk 更该先测的是「secondary-market discount → peer-parity reversion」事件型 raw alpha

- 时间：2026-03-31 16:17 UTC
- 类型：quant_digest
- 主题标签：raw-alpha/relative-value/stat-arb/stablecoin/parity/discount-mean-reversion/peer-basket/usdt/usdc/fdusd/tusd/spot/multi-quote/cross-quote/event-driven/1m/3m/5m/15m/paper/public-data/cost
- 证据类型：2025 NBER Working Paper / BFI PDF 全文 + Crossref DOI 元数据 + NBER data appendix 线索

- 主题类型：raw alpha
- 基础 alpha：法币抵押 stablecoin 在二级市场相对 1 美元或相对同类 stablecoin 篮子的折价/溢价会均值回复
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否

## 1. 这次看了什么
这篇 paper headline 在讲 **stablecoin run risk 与 arbitrage centralization**，但对我们 desk 更值钱的旁支不是监管，而是一个很直接的 **relative-value raw alpha**：**当某个 stablecoin 在二级市场相对 $1 / 相对 peer basket 出现可观折价时，折价通常会被套利资金逐步吃回；而不同 stablecoin 的套利通道集中度不同，会决定这个 pocket 出现得多不多、回得快不快。**

## 2. 为什么这次值得进研究池
最近几天 digest 已经补了不少：
- perp funding / basis / options no-arb；
- cross-sectional momentum / reversal；
- 多种 pairs / stat-arb。

但 **stablecoin 二级市场折价回归** 这块，当前素材池明显还不厚。它值得补有三个原因：

1. **base alpha 很清楚**：不是 filter，不是纯解释变量，而是价格偏离本身的回归；
2. **和我们现有多报价 / same-underlier routing 素材天然兼容**：stablecoin 自己可以直接做 pair，也能作为多报价 spread 的底层驱动；
3. **能和已有 depeg overlay 直接拼起来**：2026-03-29 那篇 USDT depeg overlay 不是主 alpha，这篇正好补 raw alpha 本体，前者可以做风险 veto。

## 3. 先回答一句：这篇东西的 base alpha 是什么？
**base alpha = stablecoin 在二级市场相对 $1 / 相对 peer basket 的折价（或溢价）均值回复。**

更直白地说：
- 当某个 fiat-backed stablecoin 因为卖压、套利通道不够顺、或做市承接不够，短时跌到“比同类更便宜”；
- 折价只要还没进入真正信用/赎回危机区间，后续往往会被二级市场买盘、跨 stablecoin 轮动、或一级赎回套利逐步拉回；
- 所以它本质上是 **event-driven relative-value / stat-arb**，不是 overlay。

## 4. 核心来源
### 4.1 主论文
- **Authors**：Yiming Ma, Yao Zeng, Anthony Lee Zhang
- **Year**：2025
- **Title**：*Stablecoin Runs and the Centralization of Arbitrage*
- **Venue**：NBER Working Paper No. 33882 / BFI Working Paper 2025-76
- **DOI**：10.3386/w33882
- **Readable URL**：https://bfi.uchicago.edu/working-paper/stablecoin-runs-and-the-centralization-of-arbitrage/
- **PDF URL**：https://bfi.uchicago.edu/wp-content/uploads/2025/06/BFI_WP_2025-76.pdf
- **NBER URL**：https://www.nber.org/papers/w33882

### 4.2 补充元数据
- **Crossref / NBER DOI**：https://doi.org/10.3386/w33882
- **SSRN DOI（working-paper 镜像）**：https://doi.org/10.2139/ssrn.5278385
- **Data appendix**：http://www.nber.org/data-appendix/w33882

## 5. 证据里最该拿走的硬点
### 5.1 这篇 paper 给出了“机会为什么会反复出现”的市场结构解释
作者研究的是 6 个最大法币抵押 stablecoins（USDT、USDC、BUSD、USDP、TUSD、GUSD），把 **一级申赎链路** 和 **二级市场价格偏离** 放在一起看。

最关键的不是“stablecoin 会不会偏离”，而是：
- **谁能做一级赎回套利**；
- **这个通道有多集中**；
- **集中度会怎样影响二级市场折价能挂多久。**

这正好解释了为什么 stablecoin alpha 不是“看见折价就无脑抄底”，而是要先判断：
- 这是 **普通二级折价**，还是 **run-risk 区间**；
- 这是 **可交易 pocket**，还是 **信用断裂前兆**。

### 5.2 USDT 和 USDC 的套利通道集中度差异非常大
论文里最值得 desk 直接记住的数字：
- **USDT**：平均每个月只有 **6** 个可实际做赎回的 arbitrageurs；最大的那个占了 **66%** 的赎回活动；
- **USDC**：平均每个月有 **521** 个 redeeming arbitrageurs。

这意味着：
- 并不是所有 fiat-backed stablecoin 的“1 美元锚”都一样硬；
- **USDT 这种申赎更集中的币，二级市场折价更容易变成可见的交易 pocket**；
- **USDC 这种申赎更分散的币，价格通常更贴锚，机会少得多，但信用层面相对更像“紧锚定基准”。**

### 5.3 折价幅度差异也不是小数点游戏，而是可交易量级
论文直接给了二级市场折价统计：
- **USDT median discount = 11 bps**；
- **USDC median discount < 1 bp**；
- **USDT average discount = 54 bps**；
- **USDC average discount = 1 bp**。

对 desk 的翻译：
- 这不是“有没有偏离”的问题，而是 **偏离幅度是否大到足以覆盖手续费、滑点和库存风险**；
- **USDT 这一侧的 pocket 显著更厚**；
- 真正值得测的不是“所有 stablecoin 一起做”，而是 **先围绕折价更容易拉开的 quote leg 建 pocket**。

### 5.4 论文还告诉你：不要把所有折价都当无风险回归
作者强调：
- 二级市场价格跌破 $1` 不等于` stablecoin 已经“break the buck”；
- 但如果一级赎回要靠抛售不够液态的准备金，**更高效的套利虽然能让价格更快回锚，也可能放大 run risk**。

这对策略设计很关键：
- **小中型折价** 可能是 alpha；
- **极端折价** 可能是 regime break；
- 不能把“更深的折价”机械当成“更大的 edge”。

所以这类策略的正确结构不是纯 z-score fade，而是：
- **普通折价区间做均值回复**；
- **超阈值折价触发 size-down / veto**；
- 正好可接上我们已经记过的 stablecoin depeg shared overlay。

## 6. 对 1m / 3m / 5m / 15m 的正确读法
### 6.1 不要照抄论文的一级赎回层
论文大量证据来自：
- issuer ↔ arbitrageur 的链上 mint / burn / redemption 事件；
- 以及多个交易所二级市场价格。

但我们做最小实验时，**不需要一开始就把一级赎回数据吃全**。对短周期复现，第一步只需要：
- 稳定币二级市场成交 / mid / depth；
- 同类 stablecoin 之间的相对价格；
- 成本与极端 regime 剔除。

也就是说：
- **研究地基来自 paper**；
- **最小可复现实验可以纯用公开 CEX spot 数据启动。**

### 6.2 对 desk 最自然的两个转译版本
#### 版本 A：stablecoin-stablecoin 直接做
例如：
- `USDC/USDT`
- `FDUSD/USDT`
- `TUSD/USDT`

信号是：
- 某个 stablecoin 相对 anchor（如 USDT 或 peer basket）突然便宜；
- 但还没进入“系统性 depeg / 信用怀疑”区间。

#### 版本 B：same-underlier 多报价 spread
例如：
- `BTC/USDT` vs `BTC/USDC`
- `ETH/USDT` vs `ETH/FDUSD`

这时你不是直接赌 stablecoin 自身回锚，
而是赌：
- **同一标的在不同 stablecoin quote 下的相对错价** 会随着 quote-side 折价修复而收敛。

版本 B 和我们已有的 multi-quote routing 素材是天然互补的；
版本 A 则更接近这篇 paper 的原始经济机制。

## 7. 这篇东西怎么拆成可执行策略
### 7.1 Entry
先定义一个 anchor：
- **单 anchor**：以 USDC 或 USDT 为基准；
- **peer basket**：`ref_t = median(USDC, FDUSD, TUSD, USDP …)` 的同步价格。

然后定义：
- `discount_t = ref_t - px_t`
- 或百分比版 `disc_pct_t = ref_t / px_t - 1`

开仓条件 first pass：
1. `disc_pct_t` 超过 rolling percentile / z-score 阈值；
2. order-book depth 足够；
3. 近 5m realized vol 没进入异常区；
4. 没触发 depeg/run-risk overlay。

### 7.2 Exit
建议先用最朴素三层：
1. **回锚退出**：折价收回 50%~80%；
2. **时间退出**：超过 `N` bars 还没回，就平；
3. **极端风险退出**：折价继续扩大到 crash bucket，直接切断。

### 7.3 Sizing
先别复杂化：
- 基础仓位按 `disc_pct_t / intraday_vol` 线性缩放；
- 再乘一个 depth cap；
- 再乘一个 regime multiplier：
  - 正常 regime = 1.0
  - depeg-risk regime = 0 或很小。

### 7.4 Risk
至少要加四道：
1. **系统性 depeg veto**：如果多个 stablecoin 同时失锚，不做；
2. **depth collapse veto**：盘口深度急缩时不做；
3. **jump veto**：1m/3m 出现异常跳价时只减仓不抄底；
4. **venue fragmentation veto**：单一 venue 异常价、其他 venue 不确认时，先视为坏数据/流动性洞。

### 7.5 Cost
这类 alpha 最怕被忽略的不是方向，而是成本口径：
- spot fee
- bid/ask spread
- depth 造成的冲击
- 借贷/保证金融资成本（若要做空 quote leg）
- 多腿 routing 的资金占用

所以回测至少要有：
- maker-only 上限版；
- taker-only 保守版；
- mixed realistic 版。

## 8. 外部数据与公开性
这类主题虽然 headline 来自 paper，但**最小实验所需数据是公开可得的**。

### 8.1 核心最小数据源
- **CEX spot trades / order book / best bid-ask**
- 交易所公开 API（Binance / OKX / Bybit 等）
- 更新频率：秒级到毫秒级；落到 `1m / 3m / 5m / 15m` 完全够用

### 8.2 可选增强数据
- stablecoin mint / burn 链上事件
- issuer reserve / disclosure 更新
- depeg 事件新闻流或链上告警

这些增强项适合作为：
- **regime gate**
- **risk overlay**
- **size-down trigger**

而不该伪装成逐根主信号。

## 9. 最小可复现实验
### 实验 A：3m / 5m stablecoin direct parity reversion
- **标的**：`USDC/USDT`, `FDUSD/USDT`, `TUSD/USDT`
- **频率**：3m、5m
- **anchor**：peer median
- **entry**：`disc_pct` > rolling 95% percentile 或 `z > 2`
- **exit**：回收 60% 折价，或 `12~36` bars 超时退出
- **risk veto**：若所有 pair 同时大幅失锚，停做
- **看什么**：after-cost Sharpe、命中率、平均回锚时间、极端扩散尾损

### 实验 B：15m same-underlier multi-quote spread
- **对象**：`BTC/USDT vs BTC/USDC`、`ETH/USDT vs ETH/FDUSD`
- **频率**：15m
- **信号**：quote-implied discount 映射成同标的双边 spread
- **entry**：spread 超 rolling percentile，且 stablecoin side 折价得到 peer confirmation
- **exit**：spread 回归中位或半衰期到点
- **目的**：验证 stablecoin 折价是否真能转成我们更熟悉的 same-underlier relative-value alpha

### 实验 C：1m fast veto map
- **对象**：只选最液体 stablecoin pair
- **频率**：1m
- **目标**：不先追求收益，先估计哪些 microstructure 条件下“折价回归”会失效
- **输出**：可交易 vs 不可交易 regime 标签，为 3m/5m 主策略服务

## 10. 它和我们当前素材池怎么拼
我认为它最好的位置不是单打独斗，而是两段式：

1. **raw alpha 本体**：
   - stablecoin discount / peer-parity reversion
2. **shared overlay**：
   - 接我们 2026-03-29 已经记过的 `USDT depeg → jump-risk / cojump-risk size-down + veto`

这样分工很清楚：
- 这篇负责回答“什么情况下偏离本身能赚”；
- overlay 那篇负责回答“什么时候别去接”。

## 11. 局限与风险
1. **paper 不是现成回测策略**：它给的是机制证据，不是完整短周期交易系统。
2. **stablecoin 折价有两种状态**：普通 microstructure 折价 vs 信用/赎回怀疑；后者不能当普通 MR。
3. **短周期容量有限**：很多 pocket 很薄，吃一脚 taker 可能把 alpha 全打没。
4. **不同 venue 的 quote 规范不一**：symbol、精度、撮合深度、maker/taker 费率都要单独对。
5. **极端事件下相关性会坍塌**：peer basket 本身也可能失效。

## 12. 我建议的“下一步怎么测”
1. **先做 stablecoin direct pair，不先上复杂三角路由**：先验证 alpha 本体是否存在。
2. **先做 3m / 5m，再压到 1m**：这类 pocket 受微观噪音影响很大，先在稍慢级别看是否还有净边。
3. **把 overlay 提前接上**：depeg / cojump veto 不要等回测爆炸后再补。
4. **同一时间只测一个 anchor 定义**：先比 `single anchor` vs `peer median`，不要一次混太多 ref。
5. **必须和多报价策略联测**：如果 direct pair 本身不够厚，但 same-underlier quote spread 能留下净边，那它仍然值得留在素材池。

## 13. 一句话结论
这篇 paper 最适合 desk 拿去落地的，不是“stablecoin 监管启示”，而是：**把 fiat-backed stablecoin 的二级市场折价当成一个可做的 relative-value raw alpha，再用 depeg overlay 把普通回锚和真正 run-risk 区间切开。**

## 14. 来源链接
- BFI 页面：https://bfi.uchicago.edu/working-paper/stablecoin-runs-and-the-centralization-of-arbitrage/
- BFI PDF：https://bfi.uchicago.edu/wp-content/uploads/2025/06/BFI_WP_2025-76.pdf
- NBER 页面：https://www.nber.org/papers/w33882
- DOI：https://doi.org/10.3386/w33882
- SSRN 镜像 DOI：https://doi.org/10.2139/ssrn.5278385
- Data appendix：http://www.nber.org/data-appendix/w33882
