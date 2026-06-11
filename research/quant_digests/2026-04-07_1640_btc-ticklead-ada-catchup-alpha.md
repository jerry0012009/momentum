# 别把这篇 2023 tick lead-lag 论文只读成测量文：对 short-cycle desk，更该先测的是「BTC tick impulse × ADA 60s delayed catch-up」
- 时间：2026-04-07 16:40 UTC
- 类型：2023 开放获取论文全文 PDF（Business Perspectives PDF）+ Crossref/OpenAlex metadata
- 主题类型：raw alpha
- 基础 alpha：BTC 的超短周期方向冲击先到，ADA 会在随后约 `16~118` 秒内补这一步；赚的是 **BTC 先动、ADA 后跟** 的极短 lead-lag catch-up。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / cross-asset / lead-lag / relative-value / btc-leads-ada / tick-data / 1m / 3m / 5m / paper / public-proxy / cost / risk
- 证据类型：论文证据

## 1. 这次看了什么
这次主看 **Bing Anderson (2023)** 的论文 **《A tick-by-tick level measurement of the lead-lag duration between cryptocurrencies: The case of Bitcoin versus Cardano》**。它不是泛泛讲“BTC 会带动 alt”，而是直接用 **tick-by-tick midpoint quotes** 去估计：BTC 对 ADA 到底领先多久。对我们 desk 来说，这最有价值的不是“测出来一个秒数”，而是把它翻译成一条可下单的 **cross-asset lead-lag raw alpha**。

## 2. 核心结论
- 这篇东西的 **base alpha 很清楚**：当 BTC 在超短窗口里先出现显著方向冲击，而 ADA 还没跟上时，ADA 后面那几十秒存在同向 catch-up 空间。
- 论文用 HitBTC 的 **BTC/USD 与 ADA/USD tick 数据**，逐月估计 `2019-01 ~ 2021-05` 的 lead time；结果显示 **BTC 对 ADA 的领先时间介于 `16` 到 `118` 秒之间，平均约 `56.5~57` 秒**。
- 这条领先时间不是常数，而是在样本期里 **显著下降**。翻成人话：alpha 没完全消失，但更像一条会被市场学习、会被压缩的短时 edge，所以今天复现时要先假设“窗口比论文里更短、更脆”。
- 季节性检验基本 **不显著**。也就是说，值钱的不是“每月某几天”这种 calendar effect，而是 **BTC 冲击发生后，ADA 有没有在很短时间里落后**。
- 对 short-cycle desk 最直接的策略翻译不是做复杂 VAR，而是：**先盯 BTC impulse，再做 ADA delayed catch-up**；若将来证据成立，再扩到 `BTC -> ETH/SOL/ADA` 的 leader-follower 篮子。

## 3. 为什么和当前项目有关
我们最近虽然也在补 lead-lag，但更多是 `5m / 15m` 或 basket 层的 follower catch-up；这篇 2023 论文补的是更底层的一层：**raw alpha 的时间尺度到底有多短**。它直接告诉我们，这类 alpha 可以先在 `tick / 1s / 10s` 上验证，再压缩成 `1m / 3m` 的入场特征，而不是一上来就粗暴用 bar-close 追涨。

一句话核心结论：**BTC 的超短冲击并不会被 ADA 同步瞬间吃完，仍可能留下一小段几十秒级的 delayed catch-up。**  
一句话证明方式：**作者不是看日线相关性，而是用 tick 级异步数据整合，逐月估计 BTC 领先 ADA 的具体秒数，并检验它的趋势与季节性。**

## 3.5 策略拆解（必填）
- 方向属性：跨资产 / 相对价值 / lead-lag continuation
- 基础 alpha：BTC 最新 `30~60s` 冲击对 ADA 随后 `30~120s` 收益有预测力
- regime：BTC 主导、联动增强、但 follower 尚未完全同步的高流动性时段
- filter / veto：仅在 `|r_BTC|` 超过滚动分位阈值、ADA 同期残差仍显著落后、盘口成本低于预期 edge 时开仓
- risk / sizing / execution overlay：仓位按 `BTC impulse z-score × ADA depth / spread` 缩放；默认单笔持有 `30~120s`，`max-hold` 到时强平；若 ADA 已补齐 `70~90%` 或出现反向 `x` bps 立即退出

## 4. 可复刻的最小实验
- 研究假设：当 BTC 在最近 `30s` 出现 top-decile 方向冲击、而 ADA 同期只跟了不到 `30%~40%` 时，ADA 在下一段 `30~120s` 仍会同向补动作。
- 一个可计算定义：
  1. 用 Binance `aggTrades` 或逐笔成交，把 `BTCUSDT / ADAUSDT` 聚成 `1s` 收益；
  2. 定义 `impulse_gap_t = r_BTC,30s - beta * r_ADA,30s`；`beta` 可先取滚动回归或简单波动比；
  3. 若 `r_BTC,30s > q90` 且 `impulse_gap_t > q80`，做多 ADA；若 `r_BTC,30s < q10` 且 `impulse_gap_t < q20`，做空 ADA；
  4. 退出先测两版：`T+60s` 固定离场，或 `gap` 收敛到入场时的 `20%` 以下即离场。
- 最小回测切口：
  - 资产：`BTCUSDT / ADAUSDT`，先用 Binance spot，再看 perp 是否更强但更贵
  - 周期：底层 `1s`，研究汇总到 `1m / 3m`
  - 样本：近 `30~90` 天连续交易日，按 UTC 分时段拆开
- 最该先看哪 1~2 个指标：**费用后单笔期望值是否仍为正**、**edge 衰减曲线是在 `10s / 30s / 60s / 120s` 哪个点被吃完**。

## 5. 风险与保留意见
- 论文测的是 **lead-lag duration**，不是现成回测；也就是说，alpha 本体很清楚，但 **交易成本、延迟、滑点、成交优先级** 需要我们自己补。
- 论文样本是 `2019~2021` 的 HitBTC，今天主流所的市场效率可能更高，真实 lead time 可能已经比 `56.5s` 更短，所以一定要先测 **decay curve**，不要默认论文秒数还能照搬。
- 单一 `BTC-ADA` 关系也可能受 market beta 驱动；复现时最好同时做一个 **市场共振对照**：如果 ADA 同步跟 ETH/SOL 也一起动，那就不是纯 lead-lag。
- 这条线很可能是“**低延迟 raw alpha + 高成本脆弱**”型；若成本后被吃掉，仍然可退而求其次，把它降级成 `1m / 3m` 的 **entry confirmation / execution timing gate**。

## 6. 来源
1. **Anderson, B. (2023).** *A tick-by-tick level measurement of the lead-lag duration between cryptocurrencies: The case of Bitcoin versus Cardano*. *Investment Management and Financial Innovations*, 20(1), 173-183.
   - DOI: `10.21511/imfi.20(1).2023.15`
   - Readable URL: `https://doi.org/10.21511/imfi.20(1).2023.15`
   - PDF URL: `https://www.businessperspectives.org/images/pdf/applications/publishing/templates/article/assets/17735/IMFI_2023_01_Anderson.pdf`
2. **Crossref metadata**
   - URL: `https://api.crossref.org/works/10.21511/imfi.20(1).2023.15`
3. **OpenAlex metadata**
   - URL: `https://api.openalex.org/works/https://doi.org/10.21511/imfi.20(1).2023.15`
