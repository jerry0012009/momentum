# 别把这篇 2020 JFE cross-asset TSMOM 只读成“债股宏观配置”：对 crypto short-cycle desk，更该先测的是「BTC-confirmed alt TSMOM」这条 raw alpha

- 时间：2026-04-12 01:52 UTC
- 类型：2020 *Journal of Financial Economics* 论文全文 PDF + Binance USDⓈ-M public `15m/5m` portability probe
- 主题类型：raw alpha
- 基础 alpha：**alt 自身的 lookback-sign time-series momentum；`BTC` 同窗趋势信号只负责做 cross-asset confirm / boost，不替代目标币自己的方向信号。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha/cross-asset/lead-lag/time-series-momentum/btc-confirmation/alt-beta/eth/sol/xrp/ada/binance-perpetual/15m/5m/paper/fulltext/public-probe/cost/risk
- 证据类型：论文证据 + Binance USDⓈ-M 公共数据 portability probe

## 1. 这次看了什么
这轮主材料是：

- **Authors:** Aleksi Pitkäjärvi, Matti Suominen, Lauri Vaittinen
- **Year:** 2020
- **Title:** *Cross-asset signals and time series momentum*
- **Venue:** *Journal of Financial Economics*
- **DOI:** <https://doi.org/10.1016/j.jfineco.2019.08.013>
- **Readable URL:** <https://www.sciencedirect.com/science/article/pii/S0304405X19302156>
- **PDF used this round:** <https://assets.super.so/e46b77e7-ee08-445e-b43f-4ffd88ae0a0e/files/8e6baac4-b9ff-4769-9bff-3ed60dca467d.pdf>
- **Related thesis page / abstract anchor:** <https://research.aalto.fi/en/publications/essays-on-time-series-momentum>

论文原始语境是 **20 个发达国家的 bond/equity index**。它不是在讲“市场 A 涨了所以市场 B 也会涨”这种空泛相关，而是给了一条可交易的 cross-asset TSMOM 结构：

- **过去债券收益**，会**正向预测未来股票收益**；
- **过去股票收益**，会**负向预测未来债券收益**；
- 用这组 cross-asset predictability 做出来的 **XTSMOM**，比只看单资产 own-sign 的普通 TSMOM 更强。

论文里最值得记住的两组数：

1. 从 `1980-01` 到 `2016-12`，作者给的**分散化 XTSMOM gross Sharpe 约 `0.89`**，而普通 **TSMOM 约 `0.61`**，前者高约 **`45%`**；
2. 在控制对应 TSMOM、全球股债基准和常见风格因子后，**XTSMOM 仍有约 `0.25%/month` 的显著 alpha**；不控制 TSMOM 时，alpha 约 **`0.54%/month`**。

一句话讲，这篇最值钱的不是“跨资产也有一点预测性”，而是：

> **同一个目标资产的 own-trend，如果能被另一条更宏观、更慢的 cross-asset trend 同方向确认，原始 TSMOM 的质量会更高。**

## 2. 先回答最重要的一句：base alpha 到底是什么
这轮的 `base alpha` 是清楚的：

> **target alt 自身的 time-series momentum。**

翻成人话：

- 先看 `ETH / SOL / XRP / ADA` 自己过去一段时间到底是在涨还是在跌；
- 这仍然是最核心、最原始的方向信号；
- `BTC` 的作用不是替代它，而是回答：
  - **这段 alt 趋势，是不是也被更“宏观”的 crypto beta 主腿确认了？**

所以这条线不是：

- 单纯的 shared gate；
- 也不是纯解释型宏观故事；
- 更不是“拿 BTC 当万能方向”。

它本质上仍然是一条 **raw alpha**：

> **alt own-trend 是主信号，BTC trend 是跨资产确认与加权层。**

## 3. 为什么对 crypto desk，不该照抄论文 headline，而该先抽这条“BTC-confirmed alt TSMOM”旁支
论文的原始权重写法里，单国 bond/equity 的 regular XTSMOM 大意是：

- `bond weight = own bond sign - 0.5 * equity sign`
- `equity weight = own equity sign + 0.5 * bond sign`

也就是说：

- equity leg 会被 bond trend **正向加权**；
- bond leg 会被 equity trend **反向修正**。

把它直接生搬到 crypto 没意义，因为 crypto 没有天然对应的“债券 leg”。但它里面有个非常适合 desk 的可移植核心：

> **更宏观、更主导的 beta leg 的趋势，可以给更高 beta 的 follower leg 做确认和加权。**

放到 crypto，最自然的翻译就是：

- `BTC` 更像 market-beta / macro leg；
- `ETH / SOL / XRP / ADA` 更像 beta 更高的 follower legs；
- 因此，**alt 自己的 TSMOM 若得到 BTC 同向确认，质量可能更高；若与 BTC 冲突，expectancy 可能明显变差。**

这也是为什么我这轮不去写“债股配置启示录”，而是直接把 paper 压成一个能在 `15m/5m` 立刻快检的 desk 版本。

## 4. 本地 portability probe：`BTC` 做 confirm，alt 自身做方向，这条线在 `15m/5m` 上有没有边
本地 artifacts：

- `/root/clawd/jerry/momentum/reports/artifacts/literature/btc_confirmed_alt_tsmom_probe_summary_2026-04-12.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/btc_confirmed_alt_tsmom_probe_detail_2026-04-12.csv`

### 4.1 数据与口径
- **数据源：** Binance Vision 公共 USDⓈ-M monthly klines zip
- **标的：** `BTCUSDT` 作为 confirm leg；`ETHUSDT / SOLUSDT / XRPUSDT / ADAUSDT` 作为 target legs
- **样本：** `2025-10` 到 `2026-03`
- **频率：** `15m` 与 `5m`
- **公开性：** 完全公开可下载

### 4.2 我测了什么
我没有硬复刻论文里的 bond/equity 不对称号，而是先做一个更 desk 化的最小版本。

对每个 target alt：

```text
target_sig_t = sign(sum(ret_target, last J bars))
btc_sig_t    = sign(sum(ret_BTC,    last J bars))
```

然后做 3 个版本：

1. **baseline own-TSMOM**
   - `pnl = target_sig * future_return`
2. **BTC-align veto**
   - 只有 `target_sig == btc_sig` 时才交易，否则 `flat`
3. **BTC-confirm boost**
   - `position = target_sig + 0.5 * btc_sig`
   - 也就是：
     - 同向时加仓到 `1.5x`
     - 冲突时缩到 `0.5x`

这不是 production 版本，只是先回答一个最关键的问题：

> **BTC 的同窗趋势，对 alt own-trend 到底是在“加分”，还是只是噪声？**

## 5. 结果先说结论
结论相当干脆：

> **在这轮 public-data quick probe 里，BTC 不是替代 alt 方向的主信号，但它对 alt TSMOM 的“确认价值”很明显。**

更具体地说：

- `15m` 上最像 first lane；
- `5m` 也能压缩，但更适合作为 `15m` 结论的高频展开；
- 冲突桶通常明显更差，说明 **BTC-confirm 更像 admission / sizing layer，而不是多余特征。**

## 6. 这轮最值得记住的 6 个数
### 6.1 论文原文里，XTSMOM 相比普通 TSMOM 的提升不是小修小补
- 分散化 **XTSMOM gross Sharpe 约 `0.89`**；
- 对应 **TSMOM 约 `0.61`**；
- 相比高约 **`45%`**；
- 控制 TSMOM 后，**仍有约 `0.25%/month` alpha**。

也就是说，paper 本体已经证明：

> **cross-asset confirm 不是“讲故事的 embellishment”，而是能提高 risk-adjusted performance 的真东西。**

### 6.2 `15m` 上，`3h lookback + next 45m hold` 的 BTC-confirm 版本最有值钱感
对 `ETH+SOL+XRP+ADA` pooled：

- **baseline own-TSMOM：** 约 **`+0.315 bps/bar`**
- **BTC-align veto：** 约 **`+0.661 bps/bar`**
- **BTC-confirm boost：** 约 **`+0.818 bps/bar`**
- **align 占比：** 约 **`80.2%`**

这不是微小改善，而是一个很清楚的排序：

> **own-trend < own-trend + BTC veto < own-trend + BTC boost**

### 6.3 如果先只看最可交易的 `ETH+SOL`，改善更明显
同样在 `15m`、`12-bar lookback`、持有后续 `3` 根 bar：

- **ETH+SOL baseline：** 约 **`+0.705 bps/bar`**
- **ETH+SOL BTC-align veto：** 约 **`+0.955 bps/bar`**
- **ETH+SOL BTC-confirm boost：** 约 **`+1.307 bps/bar`**

拆腿看：

- **ETH：** `+0.346 -> +0.735 -> +0.908 bps/bar`
- **SOL：** `+1.064 -> +1.175 -> +1.707 bps/bar`

这说明它不只是“某个小币随机抖出来的结果”，而更像 **beta 更高的 alt 趋势，在 BTC 同向时更干净。**

### 6.4 真正的坏桶是 `conflict bucket`
`15m` 四币 pooled 下：

- **align bucket 条件均值：** 约 **`+0.824 bps/bar`**
- **conflict bucket 条件均值：** 约 **`-1.744 bps/bar`**

`ETH+SOL` pooled 下：

- **align：** 约 **`+1.164 bps/bar`**
- **conflict：** 约 **`-1.387 bps/bar`**

翻成人话：

> **最值钱的不只是“BTC 同向时更好”，而是“跟 BTC 打架的 alt 趋势，质量显著更差”。**

这对 desk 来说非常重要，因为它先告诉我们哪类交易该少做。

### 6.5 `5m` 也不是没法压，只是更像 `15m` 逻辑的高频展开
对 `5m`，我测的是：

- **`36-bar lookback`（约 `3h`）**
- **持有未来 `6` 根 bar（约 `30m`）**

四币 pooled：

- **baseline：** 约 **`+0.197 bps/bar`**
- **BTC-align veto：** 约 **`+0.495 bps/bar`**
- **BTC-confirm boost：** 约 **`+0.593 bps/bar`**

`ETH+SOL` pooled：

- **baseline：** 约 **`+0.379 bps/bar`**
- **BTC-align veto：** 约 **`+0.714 bps/bar`**
- **BTC-confirm boost：** 约 **`+0.904 bps/bar`**

所以这条线不是只能活在 `15m`，但当前看：

> **`15m` 更像主战场，`5m` 更像压缩版或 execution layer。**

### 6.6 当前先别把它硬吹成“已 cost-cleared 完整策略”
虽然方向上很有值钱感，但这轮 probe 还只是 **gross signed-return quick check**。

也就是说：

- 它已经足够证明 `BTC-confirm` 这层东西值得进研究池；
- 但还**不够**证明你可以不管手续费、滑点、funding、拥挤和持仓约束，直接实盘开干。

所以这一轮最准确的定位是：

> **一条强 raw alpha 候选 + 明显可服务完整策略壳的 cross-asset confirm / sizing 层。**

## 7. 对当前 desk，最合理的最小策略化落点是什么
### 7.1 最小可执行版本
先别做全市场，先做最有希望的 `ETH/SOL`：

- **主频率：** `15m`
- **lookback：** 过去 `12` 根 `15m` bar（约 `3h`）
- **方向：** `sign(sum(ret_target, last 12 bars))`
- **BTC confirm：** `sign(sum(ret_BTC, last 12 bars))`
- **entry：** bar close 生成信号，下一根执行
- **position：**
  - 同向：`1.5x target_sig`
  - 冲突：先用 `flat` 或 `0.5x target_sig` 两版并行测
- **exit：** 持有 `3` 根 `15m` bar（约 `45m`）
- **sizing：** 先做 inverse-vol 或等风险权重
- **risk：** 单币权重上限 + book gross cap + funding 极端时减半

### 7.2 它服务的是哪类 raw alpha
它最直接服务的是：

1. **trend / momentum raw alpha**
   - 尤其是 alt 自身 trend-following
2. **cross-asset / lead-lag raw alpha**
   - BTC 作为 confirm leg，而不是单独拿来替代目标币方向
3. **组合层 sizing / veto**
   - 当 own-trend 和 BTC trend 冲突时，先减仓或停机，而不是机械继续做

## 8. 风险与保留意见
- 论文原样本是**月频国际 bond/equity index**，不是 crypto perp；我这里只拿它的**结构思想**做 portability，不是声称 paper 结果能直接平移到币圈。
- 当前 probe 还没把 **maker/taker fee、spread、slippage、funding、持仓上限** 明确纳进去，所以不能直接宣称已可实盘。
- `BTC -> alt` 这个映射在 crypto 里很自然，但仍然是**类比迁移**，不是 paper 原设定里的资产经济学原义。
- `ADA` 的结果明显弱于 `ETH/SOL`，说明这条线更像 **majors / high-beta liquid alts** 的东西，不一定适合无脑铺到全 universe。

## 9. 下一步怎么测
这轮最值得继续追的，不是再补故事，而是直接把它推进到成本与组合层：

1. **先做 `ETH/SOL` 专项成本回测**
   - `15m 12x3` 与 `5m 36x6`
   - maker / taker 分开测
   - 看 `post-cost expectancy` 还能剩多少
2. **把冲突桶从“flat”扩成“减仓 / 反向 / 不交易”三选一**
   - 当前 quick probe 已说明 conflict 桶明显差；
   - 下一步要回答的是：最优处理到底是 `flat` 还是 `fade`。
3. **把单腿信号推进到 basket / cross-sectional 版本**
   - 例如：只在 BTC-confirm 的币里做多 strongest sleeve，冲突币降权或剔除；
   - 这可能比单腿更接近实盘可用的组合壳。
4. **加 market-state 切片**
   - 按 BTC realized vol、funding、basis、美国时段重叠窗口切层；
   - 看 BTC-confirm 是否本质上是一个“risk-on beta clean-up”层。

## 10. 来源与本地文件
### 论文来源
- Pitkäjärvi, Aleksi; Suominen, Matti; Vaittinen, Lauri (2020). *Cross-asset signals and time series momentum*. *Journal of Financial Economics*.
- DOI: <https://doi.org/10.1016/j.jfineco.2019.08.013>
- Readable URL: <https://www.sciencedirect.com/science/article/pii/S0304405X19302156>
- PDF used this round: <https://assets.super.so/e46b77e7-ee08-445e-b43f-4ffd88ae0a0e/files/8e6baac4-b9ff-4769-9bff-3ed60dca467d.pdf>
- Thesis abstract anchor: <https://research.aalto.fi/en/publications/essays-on-time-series-momentum>

### 本地 artifacts
- `/root/clawd/jerry/momentum/reports/artifacts/literature/btc_confirmed_alt_tsmom_probe_summary_2026-04-12.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/btc_confirmed_alt_tsmom_probe_detail_2026-04-12.csv`
- `/root/clawd/jerry/momentum/research/quant_digests/2026-04-12_0152_btc-confirmed-alt-tsmom-alpha.md`

## 11. 一句话带走
**这篇 paper 对 crypto desk 最值钱的翻译，不是“去做债股宏观配置”，而是：alt 自身的趋势先别单独信，先问一句——BTC 同不同意。**
