# 别把 basis 继续只拿来做拥挤 gate：这篇 2023 JFM 论文更该先测的是「long cheap basis / short rich basis」横截面 raw alpha
- 时间：2026-03-26 03:21 UTC
- 类型：2023 Journal of Futures Markets 论文（摘要级）+ Binance Futures 公共 `15m` premiumIndex 最小快检
- 主题类型：raw alpha
- 基础 alpha：cross-sectional basis / carry spread（做多低 basis / 便宜腿，做空高 basis / 昂贵腿）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/carry/basis/cross-sectional/relative-value/market-neutral/perpetual/futures/premium-index/binance/15m/5m/8h/paper/external-data
- 证据类型：论文摘要级证据 + 本地公共数据最小实验（可复现）

## 1. 这次看了什么
先回答 base alpha：**这篇东西的基础 alpha 是横截面 basis 排名，不是把 basis 当成别的策略 veto。**

主材料是 **Yeguang Chi, Wenyan Hao, Jiangdong Hu, Zhenkai Ran (2023), _An empirical investigation on risk factors in cryptocurrency futures_, Journal of Futures Markets, DOI: 10.1002/fut.22425**。这篇论文的 headline 很朴素，但对 desk 真正有价值的点很直接：

- 它不是在讲“某个单币 breakout 怎么过滤”；
- 它是在讲 **crypto futures 横截面里，basis 本身就是 raw alpha 候选**；
- 而且论文摘要直接给出一个很关键的排序：**basis > momentum；basis-momentum 的增量在 basis 之后基本消失。**

这对我们现在的 intake 很重要，因为它提醒一件事：**如果已经有 funding / basis 数据管道，就不该只把它们降格成拥挤度说明书，还应该先把它们当成可以独立成策的横截面 carry / relative-value 本体。**

## 2. 核心结论
### 2.1 论文里最该记住的 3 个点
根据论文摘要：
1. 样本覆盖 **2017–2021 年 major cryptocurrencies futures**。
2. **basis、momentum、basis–momentum** 三类因子都能解释横截面收益，但 **basis 是最强信号**。
3. **daily factor returns 明显强于 weekly**，而 **monthly 不显著**。

把这三句翻成人话：
- 这不是“越长越稳”的低频故事；
- 它更像一个 **中短持有期的横截面 carry / rich-vs-cheap spread**；
- 而且如果你已经有 basis，本轮默认先测 **basis 本体**，不要先绕去做二次混合特征。

### 2.2 desk 化一句话结论
**对 `1m/3m/5m/15m` desk，更值得先测的不是“basis extreme 能不能 veto breakout”，而是：每 15m 刷新一次便宜/昂贵排序，做 `long cheap basis / short rich basis` 的 market-neutral spread，持有 4h~8h。**

## 3. 为什么和当前 desk 直接相关
- 这是 **独立 raw alpha 家族**，不是继续给 trend / breakout 找一个附属过滤器。
- 它天然是完整策略，不难拆成：
  - **entry**：按 basis 排名开仓；
  - **exit**：固定持有 / 反向排名 / 信号衰减退出；
  - **sizing**：等权、inverse-vol、beta-neutral 都能直接接；
  - **risk**：funding 结算窗、OI 扩张、极端拥挤可做风险约束；
  - **cost**：双边手续费 + 滑点 + 资金费率直接入账。
- 它还能和现有储备形成互补：
  - 和 **funding dispersion** 一样属于 carry 家族，但这里测的是 **basis 本体**；
  - 和 **lead-lag / reversal** 不同，它不是事件驱动，而是 **持续横截面 rich-vs-cheap**；
  - 如果后面要做多腿 relative-value book，这条线是很自然的底层砖块。

## 3.5 策略拆解（必填）
- 方向属性：cross-sectional / carry / relative-value / market-neutral
- 基础 alpha：同一时点上，basis 更低（更“便宜”）的合约，后续相对表现好于 basis 更高（更“昂贵”）的合约
- 主题类型：raw alpha
- regime：更适合在横截面 basis 分布有明显斜率、且 major 合约流动性稳定时启用
- filter / veto：极端事件窗、结算边界前后、OI 异常扩张、单腿流动性骤降时减仓或停机
- risk / sizing / execution overlay：优先 major perp；先等权 bottom-2 vs top-2，后续再测 inverse-vol / beta-neutral；成交成本需按组合 round-trip 诚实建模

## 4. 本地最小快检（Binance Futures 公共数据）
### 4.1 数据与口径
- 数据源：Binance Futures 公共 REST API
  - `premiumIndexKlines` 作为 **perp basis proxy**
  - `klines` 作为价格序列
- 公开性：公开可得，无需私钥
- 更新频率：`15m`
- 币池：`BTC / ETH / BNB / SOL / XRP / ADA / DOGE / LINK`
- 样本：最近 `1500` 根 `15m` bars（约 15.6 天）
- 横截面组合：每次做多 basis 最低的 `2` 个、做空 basis 最高的 `2` 个
- 信号定义：`premiumIndex close` 的滚动均值排名（`1 / 4 / 16 / 32 / 96` bars 均测）
- 持有定义：`4 / 16 / 32` bars；重点看更诚实的 **non-overlap** 口径

### 4.2 快检结果
**A. overlap 读法（偏乐观，只拿来找方向）**
- 最强组合是 **`16-bar` signal + `32-bar` hold**：平均 **+11.63 bps** / 次，t-stat **7.53**。
- 结论很清楚：**方向是 `long cheap basis / short rich basis`，而不是反过来。**

**B. non-overlap 读法（更适合 first verdict）**
- **`16-bar` signal + `32-bar` hold**：
  - 平均 **gross = +14.36 bps / trade**
  - **win rate = 60.9%**
  - `46` 笔 non-overlap 组合交易
- **`16-bar` signal + `16-bar` hold**：
  - 平均 **gross = +6.83 bps / trade**
  - `92` 笔交易

把它翻成人话：
- 在当前最小口径下，**basis 这条线更像“慢一点的横截面 spread”**，不是 1~2 根 K 的超短线信号；
- **4h 信号平滑 + 8h 持有** 比“更快进更快出”更像样；
- 这和论文里“daily 强于 weekly、monthly 不显著”的读法是一致的：**它是中短节奏，不是超高频，也不是拖很久。**

### 4.3 成本生存线（按组合 round-trip 粗估）
以最优的 **`16-bar signal + 32-bar hold`** 为例：
- 若 round-trip 成本约 **8 bps**，则 net 约 **+6.36 bps / trade**
- 若 round-trip 成本约 **12 bps**，则 net 约 **+2.36 bps / trade**
- 若 round-trip 成本约 **16 bps**，则 net 约 **-1.64 bps / trade**

这说明它不是“成本随便加都能活”的粗暴 alpha，但也不是一碰成本就死：**major perp、低冲击执行下，至少值得继续往下压。**

## 5. 这条线现在最诚实的读法
**它已经够资格进 raw alpha 素材池，而且优先级不低。**

原因不是“论文讲了 basis 很重要”这么简单，而是：
1. **paper side** 给了明确方向：basis 是 strongest signal；
2. **desk side** 的最小快检也给了同向支持：cheap-vs-rich 在 15m proxy 上是正的；
3. 它还能直接落成完整策略，而不是停在“以后也许能做 filter”。

但也要保留两条诚实约束：
- 论文研究的是 **cryptocurrency futures** 横截面，我们这边先用的是 **Binance perp premium proxy**，不是原论文逐字复刻；
- 当前 quick check 样本还短，所以它更像 **通过 first verdict**，还不是 final deployment verdict。

## 6. 下一步怎么测（可直接执行）
1. **先把 perp proxy 与 dated futures basis 分开测。**
   - 若能拿到 Binance 季度合约或其他公开 futures basis，就做真 basis replication；
   - 若拿不到，就明确把当前版本命名为 `perp premium carry proxy`，避免偷换概念。
2. **做 `15m signal / 5m execution` 二层结构。**
   - 排名仍在 `15m` 上做，执行下钻到 `5m`；
   - 看能否把冲击成本从 `12~16 bps` 压回 `8~12 bps` 生存区间。
3. **加入 funding / OI 作为 risk overlay，不要先混进 alpha 本体。**
   - 先跑纯 basis；
   - 再问：`高 funding + basis rich` 是否只是帮你减回撤，而不改变方向本体。
4. **做 sector-neutral / beta-neutral 对照。**
   - 当前先是 bottom-2 vs top-2 等权；
   - 下一步要看按 `beta-neutral` 或 `inverse-vol` 配权后，是提升 Sharpe 还是只是降波动。
5. **做 sign stability。**
   - 同一套框架同时跑 `long cheap / short rich` 和反向；
   - 如果 sign 经常翻，说明它只是样本噪声；如果 sign 稳定，才配进入更深一层复现。

## 7. 风险与保留意见
- 当前论文正文被 Wiley Cloudflare 挡住，本轮对论文的直接证据主要来自 **OpenAlex 抽取的摘要元数据**；因此不对正文中未直接可见的公式细节做过度延伸。
- 本地快检使用的是 **perpetual premium index proxy**，不是论文原始 futures 口径；它更适合回答“这条线在我们 desk 是否值得继续”，不等于已经完成 paper replication。
- `premiumIndex` 的横截面可能混入 funding、杠杆需求、交易所微结构与币种风险偏好，因此后续必须做 **真正 basis / funding / OI 拆分归因**。

## 8. 来源
1. **Chi, Yeguang; Hao, Wenyan; Hu, Jiangdong; Ran, Zhenkai. (2023). _An empirical investigation on risk factors in cryptocurrency futures_. Journal of Futures Markets.**
   - DOI: `10.1002/fut.22425`
   - Readable URL: https://doi.org/10.1002/fut.22425
2. **OpenAlex metadata for the paper**
   - Readable URL: https://api.openalex.org/works?filter=doi:https://doi.org/10.1002/fut.22425
3. **Binance USDⓈ-M Futures API: Premium Index Kline Data**
   - Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Premium-Index-Kline-Data
4. **Binance USDⓈ-M Futures API: Kline/Candlestick Data**
   - Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data

## 9. 本地复现产物
- `reports/artifacts/quant_digests/basis_xs_cheap_vs_rich_20260326/summary.csv`
- `reports/artifacts/quant_digests/basis_xs_cheap_vs_rich_20260326/meta.json`
