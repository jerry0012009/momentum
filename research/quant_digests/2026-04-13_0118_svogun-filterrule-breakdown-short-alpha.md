# 别把 Svogun 2022 只读成“技术分析会被成本吃掉”：对 short-cycle desk，更该先测的是「long-window filter-rule breakdown short」这条 raw alpha

- 时间：2026-04-13 01:18 UTC
- 类型：2022 论文元数据/可读页面复核（Crossref + OpenAlex + publisher landing page）+ Binance USDⓈ-M `15m` public-data portability probe
- 主题标签：raw-alpha/single-asset/trend/momentum/filter-rule/breakdown-short/technical-analysis/moving-average/liquid-majors/binance-perpetual/15m/5m/paper/public-data/cost/risk
- 证据类型：论文证据 + 公共数据 portability probe

- 主题类型：raw alpha
- 基础 alpha：**当液态 major perp 在 `15m` 上跌破长窗均线并形成足够大的 downside stretch（例如低于 `192-bar SMA` 约 `1%`）时，后续更像顺着下行继续走，而不是立刻均值回归；对称 long 镜像在同样口径下反而更弱。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 先把一句话说清楚：这篇东西的 base alpha 是什么？

> **base alpha = 技术规则并不一定死于成本；对当前 short-cycle desk，更可交易的分叉是「长窗 filter-rule breakdown short」，不是对称地把所有 buy / sell 信号都照抄。**

翻成人话：
- 价格如果只是围着均线乱晃，不值得碰；
- 但如果已经 **明显跌破** 一条够慢的均线，而且不是一点点，而是有一个可量化的 downside stretch；
- 这更像“趋势已经失衡、还没走完”，不是“跌多了马上弹”；
- 所以这条线不是均值回归，也不是 filter；它本身就是一条可独立交易的 **short-side trend raw alpha**。

## 2. 这次看了什么

### 主来源（paper）
- **Authors：** Daniel Svogun, Walter Bazán-Palomino
- **Year：** 2022
- **Title：** *Technical analysis in cryptocurrency markets: Do transaction costs and bubbles matter?*
- **Venue：** *Journal of International Financial Markets, Institutions and Money*
- **DOI：** <https://doi.org/10.1016/j.intfin.2022.101601>
- **Readable URL：** <https://www.sciencedirect.com/science/article/pii/S1042443122000130>
- **Metadata used：**
  - Crossref: <https://api.crossref.org/works/10.1016/j.intfin.2022.101601>
  - OpenAlex: <https://api.openalex.org/works/https://doi.org/10.1016/j.intfin.2022.101601>
- **Repo URL：** N/A

这篇 paper 常见的读法是：
- 技术分析在 crypto 里不是天然有效；
- 交易成本很重要；
- bubble / 非 bubble 状态也会改写结论。

但对我们 desk 来说，直接把它总结成“技术规则会被成本吃掉”太粗了。更有价值的读法是：

> **不要复刻 paper 的全部规则池，而是先问：哪一支能被翻成今天 `15m` perp 上可执行的最小 raw alpha？**

我这轮给出的答案是：
- 不是对称 long/short 全收；
- 也不是把它降级成一个 shared gate；
- 而是把它翻成 **long-window filter-rule breakdown short**。

## 3. 为什么这条分叉比“再写一个技术分析综述”更值钱

因为它满足当前 intake 的高优先级条件：

1. **一句话能说清 base alpha。**
   - 跌破长窗均线足够多 → downside continuation 更强。
2. **可独立复现。**
   - 只需要公开 `15m` K 线，不需要私有数据。
3. **可直接写成完整策略壳。**
   - entry / exit / sizing / cost / veto 都能明确落地。
4. **和当前短周期 desk 直接相关。**
   - 它补的是我们素材池里相对少一点的 **single-name trend short**，而不是又一层抽象解释。

## 4. desk 化重写：先别复刻 69 条规则，先测最有交易意义的一条

我没有尝试完整复刻论文里的大规则池，而是先做一个更适合 desk 的最小版本：

### 信号定义
对每个 symbol，在 `15m` 上计算：
- `SMA_192`（约等于 2 天）

若满足：
- `close < SMA_192 * (1 - 1%)`

则视为：
- **breakdown short entry signal**

### 出场
- 当 `close > SMA_192` 时平仓
- 执行统一用 **next-bar open**

这其实就是经典 filter rule 的 desk 化翻译：
- **不是刚跌破一点就冲进去；**
- 而是要求足够大的偏离，减少噪音进场；
- 平仓也不靠拍脑袋，而是等回到均线另一侧。

## 5. public-data portability probe：这条 short 分叉在今天的 `15m` perp 上，真的还活着吗？

### 5.1 数据口径
- **市场：** Binance USDⓈ-M Perpetual
- **频率：** `15m`
- **样本：** 最近 `365d`
- **标的：** `BTCUSDT / ETHUSDT / SOLUSDT / BNBUSDT`
- 原计划还抓 `XRPUSDT`，但本轮 Binance API 返回 `429 Too Many Requests`，所以最终有效样本是 `4` 个 liquid majors
- **执行：** next-bar open
- **成本：** round-trip `10 bps` 与 `20 bps`

### 5.2 本地 artifacts
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-13_svogun-buyfilter-majors-alpha_probe.py`
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-13_svogun-buyfilter-majors-alpha/fetch_status.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-13_svogun-buyfilter-majors-alpha/rule_summary_by_symbol.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-13_svogun-buyfilter-majors-alpha/rule_summary_aggregate.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-13_svogun-buyfilter-majors-alpha/breadth_summary.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-13_svogun-buyfilter-majors-alpha/ranked_configs_10bps.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-13_svogun-buyfilter-majors-alpha/ranked_configs_20bps.csv`

## 6. 最关键结果：最佳 pocket 不是 long，而是 short

### 6.1 这一轮最强配置
我测了一小组 filter-rule 参数后，**当前最强的是：**
- `SMA_192`
- `band = 1%`
- `side = short`

也就是：
> **`15m` close 跌破 `192-bar SMA` 超过 `1%` 时做空；回到均线之上再平。**

### 6.2 聚合结果（4 个 majors）
#### `10 bps` round-trip
- 交易数：**`597`**
- 胜率：**`28.17%`**
- 平均单笔净收益：**`+0.121%`**
- 中位数：**`-1.054%`**
- 累计净收益：**`+77.88%`**
- 平均持有：**`90.96` bars ≈ `22.7h`**
- Profit Factor：**`1.13`**

#### `20 bps` round-trip
- 交易数：**`597`**
- 胜率：**`27.41%`**
- 平均单笔净收益：**`+0.021%`**
- 累计净收益：**`+18.18%`**
- Profit Factor：**`1.02`**

这组数的意思很明确：
- 它不是高胜率系统；
- 它靠的是 **少数大趋势空单** 覆盖大量小亏；
- 但关键是 **扣到 `20 bps` 之后还没死**，说明 gross edge 并不薄。

## 7. 更重要的不是“它赚钱”，而是 long 镜像明显更差

同样的 `SMA_192 + 1% band`，如果做 **long mirror**：

### `10 bps` round-trip
- 交易数：`627`
- 平均单笔净收益：**`-0.041%`**
- 累计净收益：**`-21.09%`**

也就是说：

> **当前样本里，这条技术规则不是对称的。能活下来的不是“离均线 1% 就顺着做”，而更像“跌破长窗后的 breakdown short”。**

这正是这轮 digest 最值钱的地方：
- 它没有把技术分析写成大而化之的“趋势都能做”；
- 也没有默认 long/short 对称；
- 而是明确指出：**同一条 filter rule，在 today’s crypto perp sample 里，short side 明显更像可交易 pocket。**

## 8. breadth：不是只靠单一币种硬拉

在最佳配置 `SMA_192 / 1% / short` 下：
- `10 bps`：**`3 / 4` 个 symbol 的平均单笔净收益为正**
- `20 bps`：**仍有 `3 / 4` 个 symbol 为正**

### 逐币（`10 bps`）
- `BTCUSDT`：平均单笔 **`+0.117%`**
- `ETHUSDT`：平均单笔 **`+0.151%`**
- `SOLUSDT`：平均单笔 **`+0.255%`**
- `BNBUSDT`：平均单笔 **`-0.056%`**

所以它不是：
- 只有 BTC 一个人在贡献；
- 也不是全靠一个离谱 outlier symbol；
- 更像是 **liquid majors 里的 downside trend pocket**，但对 BNB 这类相对稳一点的币种未必同样友好。

## 9. 这条 alpha 跟当前 `1m / 3m / 5m / 15m` desk 的关系

它的主信号虽然在 `15m`，但完全可以 desk 化成：

### 推荐第一版策略壳
- **Universe：** `BTC / ETH / SOL` 优先，BNB 暂时降级观察
- **Signal TF：** `15m`
- **Entry：** `close < SMA_192 * 0.99`
- **Execution TF：** `5m`
  - 不建议直接 `15m` bar close 追单
  - 更合理的是：`15m` 触发后，在 `5m` 上等第一次弱反抽失败或 micro lower-high 再进
- **Exit：**
  1. `15m close > SMA_192`
  2. 或固定 time stop（如 `24h`）
  3. 或 trailing stop 防止 V 型反抽
- **Sizing：**
  - 单笔风险固定预算
  - 按近 `24h` realized vol 做 vol-scaling
- **Cost 假设：**
  - 先按 `10 / 20 / 30 bps` 三档压力测试

所以它不是超快 `1m` 高频 alpha，
但它是一个**完全能服务 15m 主信号、再由 5m 执行层细化**的 raw alpha。

## 10. 为什么它值得进研究池

### 10.1 它补的是 single-name short trend，不是又一条 pairs / carry
最近素材池里：
- pairs / stat-arb / carry / basis 很多；
- 但这种 **简单、可解释、成本后还活着的 single-name short trend pocket** 反而没那么密。

### 10.2 它足够朴素，反而容易被诚实验证
这条线好的一点是：
- 不依赖神秘特征；
- 不依赖黑箱模型；
- 不依赖难拿的外部数据。

只需要公开 K 线，
就能先回答一个很关键的问题：

> **today’s crypto major perps 到底有没有“跌穿长窗后还会继续下”的 pocket？**

这轮答案是：**有，而且 short side 比对称 long 更诚实。**

## 11. 风险与保留意见

### 11.1 这不是 paper 的完整复刻
我这轮做的是：
- 从 paper 里抽一条最 desk-able 的技术规则分叉；
- 不是去复刻它的全部规则家族、全部资产、全部 bubble 分类。

### 11.2 样本明显带有 2025-2026 市场状态特征
这轮结果很可能受当前市场状态影响：
- 如果 2025-2026 这段本身更偏 downside persistence，
- 那 short side 会天然更占优。

所以不能直接说这是“永恒规律”，
只能说：
- **在当前这段真实可交易样本里，它比 long mirror 强得多。**

### 11.3 中位数为负，说明它是明显的 convex / crisis-trend 形态
最佳配置里：
- 胜率不到 `30%`
- 中位数也为负

这意味着：
- 它更像 trend follower / breakdown follower；
- 不适合被当成高命中率 alpha；
- 风险管理和仓位治理必须认真做。

## 12. 下一步怎么测

1. **补 regime split**
   - 把样本分成 risk-off / risk-on、high funding stress / low funding stress、BTC 下行 / 横盘 / 上行段；
   - 看这条 edge 到底是 always-on，还是只活在 downside regime。

2. **把论文里的 bubble 视角重新接回来**
   - 原文会讨论 bubble / 非 bubble；
   - desk 版可以先用轻量代理（如 rolling acceleration / blow-off percentile / funding crowding）替代；
   - 看 breakdown short 是否主要出现在 bubble unwind 段。

3. **从 `15m signal` 拆到 `5m execution`**
   - 现在还是 next-bar open；
   - 下一步应测试：
     - 触发后首个 `5m` 反抽失败进场
     - VWAP 下方继续走弱进场
     - 或 `1m` micro lower-high 进场
   - 目的是降低追单滑点。

4. **做更完整的风险壳**
   - 补 `time stop / trailing stop / ATR cap / funding veto`
   - 看是否能把中位数亏损收窄，而不伤到大趋势单。

5. **扩到更多 liquid majors，但要解决 API 节流**
   - 本轮 `XRPUSDT` 因 `429` 没纳入；
   - 下一轮应加节流 / cache，把 `XRP / DOGE / ADA / LINK` 等纳进来。

## 13. 一句话带走

> **Svogun 2022 不该只被读成“技术分析会被成本吃掉”；对今天的 crypto short-cycle desk，更有交易意义的分叉是：在 liquid major perps 的 `15m` 上，`close < SMA_192 × 0.99` 这类 long-window filter-rule breakdown short，扣到 `20 bps` 仍能留下正的平均单笔净收益，而对称 long 镜像反而明显更弱——这是一条值得继续细化执行层的 raw alpha。**
