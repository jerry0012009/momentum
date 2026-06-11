# 别把这篇 2024 *IJFS* multivariate pairs 论文只读成“多 fiat 套利”：对 short-cycle desk，更该先测的是「same-underlier multiquote bucket MR × conflict-netting allocator」这条 raw alpha

- 时间：2026-04-13 13:48 UTC
- 类型：2024 *International Journal of Financial Studies* 论文全文（arXiv/MDPI 同文版本，本地全文抽取）+ OpenAlex/Crossref 元数据 + Binance Spot `5m` public-data portability probe
- 主题标签：raw-alpha/relative-value/stat-arb/mean-reversion/multiquote/same-underlier/bucket-allocation/conflict-netting/stablecoin-quote/binance-spot/btc/eth/usdt/usdc/fdusd/5m/paper/fulltext/public-data/cost/risk
- 证据类型：论文全文 + 元数据 + 公共数据 portability probe

- 主题类型：raw alpha
- 基础 alpha：**同一标的在多个报价腿上的相对价格偏离会回归；与其把每个 pair 各做一遍，不如先把 richest quote / cheapest quote 压成一个 bucket spread，再用冲突净额分配去吃这段收敛。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否

## 1. 这次看了什么

这轮看的是：

- **Hongshen Yang, Avinash Malik (2024)**
- **Optimal Market-Neutral Multivariate Pair Trading on the Cryptocurrency Platform**
- *International Journal of Financial Studies*
- DOI：<https://doi.org/10.3390/ijfs12030077>
- arXiv：<https://arxiv.org/abs/2405.15461>

这篇东西最容易被读成：

> “又一个 crypto pairs / fiat arbitrage 论文，而且还是 Kraken 上 ETH 对多国法币，离我们 desk 很远。”

如果只按 headline 读，这个判断不算错；但对当前 short-cycle desk，更值钱的不是它那套 **ETH/USD/CAD/GBP/EUR** 的字面市场，而是它背后的 **multivariate relative-value raw alpha 结构**：

> **同一 anchor 资产在多个报价腿上出现偏离时，alpha 本体不是某一对腿，而是“整个报价 bucket 的 richest-vs-cheapest 偏离会回归”；多 pair 同时触发时，关键不是再加更多 signal，而是怎么把冲突腿净掉、减少无谓费用。**

这就把它从“又一篇多国法币论文”，翻译成了更贴合 desk 的一条可复现 branch：

- **same-underlier multiquote bucket mean reversion**
- **conflict-netting allocator**
- **适合先在 `5m` 做最小实验**

## 2. 先把一句话说清楚：这篇东西的 base alpha 是什么？

> **base alpha = same-underlier relative-value mean reversion。**

也就是：
- 不赌 `BTC` 本身涨跌；
- 而是赌 `BTC` 在不同 quote leg 上的相对定价偏离会收敛；
- `rich quote` 做空、`cheap quote` 做多；
- spread 回去就平。

所以它是：
- `raw alpha`
- 不是 `filter`
- 不是 `regime`
- 也不是单纯的 `sizing overlay`

论文里的优化器很重要，但那是**服务这条 raw alpha 的仓位/净额分配层**，不是 alpha 本体。

## 3. 来源

### 主来源（paper）
- **Authors：** Hongshen Yang, Avinash Malik
- **Year：** 2024
- **Title：** *Optimal Market-Neutral Multivariate Pair Trading on the Cryptocurrency Platform*
- **Venue：** *International Journal of Financial Studies*, 12(3), 77
- **DOI：** <https://doi.org/10.3390/ijfs12030077>
- **Readable URL：** <https://www.mdpi.com/2227-7072/12/3/77>
- **arXiv URL：** <https://arxiv.org/abs/2405.15461>
- **Repo URL：** N/A

### 元数据复核
- **OpenAlex：** <https://api.openalex.org/works?search=Optimal%20Market-Neutral%20Multivariate%20Pair%20Trading%20on%20the%20Cryptocurrency%20Platform&per-page=5>

### 本轮本地 artifacts
- Probe script：`reports/artifacts/quant_digests/2026-04-13_multiquote_bucket_probe.py`
- Probe summary：`reports/artifacts/quant_digests/multiquote_bucket_probe_summary_2026-04-13.csv`
- Probe overlap：`reports/artifacts/quant_digests/multiquote_bucket_probe_overlap_2026-04-13.csv`

## 4. 一句话核心结论 + 一句话证明方式

### 一句话核心结论
> **这篇 paper 最该给 desk 拿走的，不是“ETH 对多法币”这个字面市场，而是“same-underlier 多报价 bucket 的 richest-vs-cheapest 偏离会回归，而且 simultaneous pair signal 应先做冲突净额”这条 raw alpha 结构。**

### 一句话证明方式
> **论文用 2020–2022 的 Kraken 多法币 ETH 数据做 full-cycle / bull / bear 回测，显示 5m bucket 版在带成本口径下仍有正年化；我再用 Binance Spot 的 `BTC/ETH × USDT/USDC/FDUSD` `5m` 公共数据做 portability probe，看到 max-min quote spread 的 1~3 bar 回归仍然存在，而且把多 pair 压成 bucket 后能显著减少腿数。**

## 5. 论文里真正值得 desk 记住的点

### 5.1 它不是简单“找 pair 再做 z-score”，而是直接处理**多腿同时出现信号**
论文的核心不是又加一个 pair selection 指标，而是：

1. 先把同一 crypto anchor 的多个报价腿放进一个 bucket；
2. 每两腿都会形成 spread；
3. 当多个 spread 同时发出 open / close signal 时，不是机械每对都下；
4. 而是用一个 **bi-objective convex optimization** 在“收益 vs 风险”之间分配资金；
5. 同时利用腿间可抵消关系，尽量减少无谓换手与费用。

翻成人话：

> **pair 很多时，难点不只是“哪对会回归”，而是“同一根 bar 同时有三四个 pair 都在叫，钱怎么分、哪些腿其实可以净掉”。**

这点对 desk 是真问题，不是学院派装饰。

### 5.2 论文给了明确的 `5m` 结果，不是慢频空谈
论文里对 `1m / 5m / 60m` 都做了试验；对我们最重要的是 `5m`：

- **最优阈值（5m）**：`open = 9σ`，`close = 7σ`
- **5m full-cycle 年化（TC 0.1%）**：
  - `OTT λ=0.5`：**37.74%**
  - `OTT λ=1`：**15.49%**
  - `OTT λ=2`：**7.74%**
- **5m full-cycle Sharpe（文中 Table 8）**：
  - `λ=0.5`：**1.11**
  - `λ=1`：**0.68**
  - `λ=2`：**0.44**
- **5m bear-market 年化（TC 0.1%）**：`λ=1` 仍约 **4.99%**

这不等于“我们照抄就能赚到同样的钱”，但至少说明：
- 这不是纯概念文；
- 它给了 `5m` 层面的完整策略骨架；
- 而且重点就是 **market-neutral / relative-value**，不是单边牛市吃 β。

### 5.3 它最适合迁移的，不是“多法币”，而是“多报价腿 + 净额分配”
论文原始市场是 Kraken 的 ETH 多法币报价；
对我们 desk，更自然的迁移不是去复现 `ETHCAD / ETHGBP / ETHEUR`，而是：

- `BTCUSDT / BTCUSDC / BTCFDUSD`
- `ETHUSDT / ETHUSDC / ETHFDUSD`
- 甚至未来再扩到多 venue / spot-perp / perp-perp 同 underlier 多报价腿

因为真正可迁移的是：
- **quote-premium dispersion**
- **bucket-level richest vs cheapest**
- **signal conflict netting**

## 6. 为什么这轮值得进当前研究池

### 6.1 它仍然是 raw alpha，不是“pairs 组合管理小修小补”
最近池子里 pairs / stat-arb 已经很多，但多数还是：
- pair admission
- hedge ratio
- spread z-score
- threshold / half-life

这篇多补了一层很关键、也更 desk 化的东西：

> **当你不是只有一对腿，而是一整个 quote bucket 时，raw alpha 依然成立，但 execution / sizing 不该再按 pair-by-pair 处理。**

### 6.2 它和当前 short-cycle desk 直接相关
它不是长周期资产配置题，因为：
- 论文直接包含 `5m`；
- 当前可迁移市场（stablecoin quote legs）也能落在 `5m / 1m / 3m`；
- 最小实验不依赖付费数据。

### 6.3 它补的是当前素材池里相对少的一种 relative-value 形态
它不是：
- 单币动量
- 单币反转
- funding carry
- 跨资产 lead-lag

而是：
- **same-underlier, multi-quote, market-neutral mean reversion**
- 这和已有大量“BTC 带 alt、funding、session pocket”的题材确实不一样

## 7. 我这次怎么做最小 portability probe

### 7.1 probe 口径
为了把 paper 翻译到更像我们 desk 的环境，我没有去重建 Kraken 多法币，而是改成：

- **市场：** Binance Spot
- **频率：** `5m`
- **样本：** 近约 `60d`（`2026-02-12 13:10 UTC` 到 `2026-04-13 13:05 UTC`）
- **资产：**
  - `BTCUSDT / BTCUSDC / BTCFDUSD`
  - `ETHUSDT / ETHUSDC / ETHFDUSD`
- **bucket 定义：** 同一时刻对三个 quote 的 log price 取横截面均值，计算各 quote premium
- **主信号：** `bucket_spread = max(premium) - min(premium)`
- **z-score：** `24h rolling`（`288` 根 `5m` bar）
- **entry：** `bucket_z > 2`
- **方向：** `short richest quote / long cheapest quote`
- **持有：** `1 bar` 与 `3 bars` 两档对照

### 7.2 为什么这样做
这样做的目的不是证明“paper 原文原封不动搬到 Binance Spot 也成立”，而是先回答两个更实用的问题：

1. **same-underlier 多报价腿的偏离回归，在今天还在不在？**
2. **如果三组 pair 同时亮灯，把它们压成一个 bucket signal，会不会比 pairwise 平铺更有效率？**

## 8. 关键结果：bucket alpha 还在，而且比“把所有 pair 都做一遍”更干净

### 8.1 BTC：bucket max-min spread 在 `5m` 上仍有明显 1~3 bar 回归
`BTC × {USDT, USDC, FDUSD}`

- `z > 2` 事件数：**880**
- `+1 bar`：**+1.20 bps / 次**，命中率 **80.9%**
- `+3 bars`：**+1.31 bps / 次**，命中率 **80.6%**

这说明：

> **当 BTC 三个报价腿里 richest-vs-cheapest 撑得够开时，未来 5~15 分钟里 spread 回来的概率很高。**

### 8.2 ETH：同样结构在 ETH 上更强
`ETH × {USDT, USDC, FDUSD}`

- `z > 2` 事件数：**751**
- `+1 bar`：**+1.78 bps / 次**，命中率 **83.6%**
- `+3 bars`：**+1.85 bps / 次**，命中率 **85.9%**

所以这不是只在 BTC 上的单点现象；
至少在 major spot multiquote 上，**same-underlier quote-premium MR** 还是能看到的。

### 8.3 把多 pair 直接压成 bucket，比 pairwise 平铺更像 desk 要的东西
我同时做了一个 pairwise 对照：
- 三个 quote 之间所有 pair 都单独算 spread z-score；
- 每根 bar 对当下所有 active pair 的收益做 equal-bar 平均；
- 看它和 bucket max-min 哪个更干净。

结果：

#### BTC
- `pairwise_equalbar +1 bar`：**+0.92 bps**，命中率 **78.9%**
- `bucket_maxmin +1 bar`：**+1.20 bps**，命中率 **80.9%**
- `pairwise_equalbar +3 bars`：**+0.98 bps**
- `bucket_maxmin +3 bars`：**+1.31 bps**

#### ETH
- `pairwise_equalbar +1 bar`：**+1.12 bps**，命中率 **80.5%**
- `bucket_maxmin +1 bar`：**+1.78 bps**，命中率 **83.6%**
- `pairwise_equalbar +3 bars`：**+1.18 bps**
- `bucket_maxmin +3 bars`：**+1.85 bps**

翻成人话：

> **不是 pair 越多越好；把最极端的 richest-vs-cheapest 抽出来，反而比“所有 pair 平铺做一遍”更强。**

## 9. 关键结果二：conflict netting 确实值得做，不是形式主义

如果你把三条 quote 腿全拆成 pair，会有三组 spread：
- USDT-USDC
- USDT-FDUSD
- USDC-FDUSD

问题是：这些信号经常会在同一根 bar 同时亮，而且方向上高度相关。

### BTC
- 有任一 pair 亮灯的 bars：**3208**
- 其中 `>=2` 条 pair 同时亮灯的比例：**43.3%**
- 如果只做“净额折叠”，把所有 pair 信号先压成 quote-level two-leg exposure：
  - 总腿数可从 **9402** 降到 **6416**
  - **腿数减少约 31.8%**

### ETH
- 有任一 pair 亮灯的 bars：**3095**
- 其中 `>=2` 条 pair 同时亮灯的比例：**43.4%**
- 净额折叠后：
  - 总腿数从 **9102** 降到 **6190**
  - **腿数减少约 32.0%**

也就是说：

> **即便不做复杂优化器，只先做最朴素的 signal netting，腿数也能少掉约三分之一。**

这就是这篇 paper 对 desk 最现实的价值之一。

## 10. 但为什么我仍然把“可直接落地完整策略”写成“否”

因为当前 probe 还有几个硬限制：

1. **gross edge 太薄**
   - 1~2 bps 的 spread 回归很好看；
   - 但若按普通双腿 taker、甚至普通 spot 成交成本算，很容易被吃掉。

2. **现货同 underlier 多报价腿，不等于天然可 frictionless 做空 rich leg**
   - 如果没有 margin / inventory / internal conversion / maker queue，执行并不免费。

3. **这轮只验证了 alpha 本体和 netting 价值**
   - 还没把真正的 fee ladder、borrow、maker queue、fill uncertainty 放进去。

所以最诚实的定位是：

> **这是一条可独立复现、而且结构很清楚的 raw alpha；但今天更像“same-venue quote dispersion sleeve / execution router / internal inventory book”候选，而不是 plain taker 现成策略。**

## 11. 对当前 desk 的落点

我会把它定位成三种用途之一：

### 11.1 raw alpha 素材池里的一个独立 relative-value 分支
不是单币，不是跨资产，也不是 funding；
它补的是 **same-underlier quote dispersion MR**。

### 11.2 pairs / basket 书的 allocator 设计参考
这篇 paper 其实在提醒我们：
- 多 pair 同时亮灯时，
- 不要本能地“每个 pair 各开一遍”；
- 先看能不能压到 quote-level / leg-level 做净额。

### 11.3 执行/路由层的 veto / selector
如果之后我们还有：
- spot-perp basis
- perp-perp same-underlier spread
- cross-venue quote dislocation

那这个 bucket 思路也可以反过来当：
- **selector**：只挑 richest-vs-cheapest 的最极端腿
- **throttle**：同一 underlier 不重复开太多互相关腿

## 12. 策略拆解（当前版本）

- 方向属性：market-neutral / same-underlier / relative-value / short-horizon mean reversion
- 基础 alpha：`richest quote premium - cheapest quote premium` 回归
- 最小信号：`bucket_z > z_entry`
- 最小执行：`short rich quote / long cheap quote`
- 最小 exit：`1~3 bars` 或 `spread 回到 close band`
- sizing / allocator：先做 quote-level netting，再谈 risk-weighted allocation
- 主要风险：fee、滑点、稳定币本身的 peg 偏移、margin/borrow 可得性、队列成交不确定性

## 13. 下一步怎么测（必须项）

1. **把 gross 直接压进 fee ladder**
   - 至少测试 `0.5 / 1 / 2 / 4 bps per leg`；
   - 这样才能知道它是 maker-only、inventory-only，还是根本不该做。

2. **从 fixed-hold 改成真正的 `open/close band`**
   - 参考 paper 的 `open/close threshold` 思路；
   - 看 `z>2 open, z<0.5 close` 与 `1/3 bar fixed hold` 哪个更适合当前 quote leg。

3. **把 bucket 从单 venue spot 扩到更可执行的腿**
   - `spot quote vs spot quote`
   - `spot vs perp` 同 underlier
   - `perp vs perp` 多 venue 同 underlier

4. **把 allocator 做成真正 quote-level netting，而不是 pair-by-pair 下单**
   - 输出最终 quote exposure，而不是输出三条 pair order；
   - 这是这篇 paper 最值得工程化的部分。

5. **往更快频率下压 `1m / 3m`**
   - 这类 quote dispersion 通常寿命更短；
   - `5m` 已经能看见结构，下一步应直接检查 `1m / 3m` 是否更像真实 pocket。

## 14. 当前结论

如果只问一句“这篇东西现在为什么值得进池子？”——我的答案是：

> **因为它不是又一篇普通 pairs；它补的是“same-underlier 多报价腿 raw alpha + signal conflict netting”这层结构，而这层正好能服务于我们后续的 relative-value / stat-arb / execution router 组件拆解。**

更具体一点：
- 作为 **raw alpha**，它成立；
- 作为 **直接 taker 策略**，当前不够；
- 作为 **desk 的 relative-value / allocator 素材**，很值钱。
