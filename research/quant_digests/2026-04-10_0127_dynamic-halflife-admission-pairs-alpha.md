# 别把这篇 2021 pairs 论文只读成“crypto 也能做协整”：对 short-cycle desk，更该先测的是「dynamic pair admission × half-life-bounded spread fade」这条完整 raw alpha
- 时间：2026-04-10 01:27 UTC
- 类型：论文
- 主题类型：raw alpha
- 基础 alpha：动态筛出的 cointegrated spread 偏离后会向均值回归，且“哪一对值得做”本身就是 alpha admission 的一部分
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：pairs / stat-arb / relative-value / mean-reversion / cointegration / half-life / admission / BTC / ETH / XRP / 15m / 5m
- 证据类型：论文证据（arXiv 全文）+ Binance USDⓈ-M 公共数据 portability probe

## 1. 这次看了什么
这次看的是 **Vadim Poplavskyi, Oleksii Serhieiev, Danylo Ovsii, Vadym Zhukov (2021), _Evaluation of Dynamic Cointegration-Based Pairs Trading Strategy in the Cryptocurrency Market_, Studies in Economics and Finance**。这篇最值钱的地方，不是再证明一遍“crypto 也能做 pairs”，而是把 raw alpha 明确写成：**先动态挑 pair，再做 spread fade**，而不是长期抱死 BTC/ETH。

## 2. 核心结论
- **一句话核心结论：** 这篇 paper 真正值得 desk 拿来抄的，不是“协整存在”，而是 **dynamic admission 比固定 pair 更重要**：先用 unit-root / cointegration + 最短 half-life 挑出当前最像会回归的一对，再做 z-score fade。
- **一句话证明方式：** 作者用 BitMEX 一分钟数据做全年滚动回测，formation / trading 按周滚动，显式模拟 bid/ask、limit/market 成交与不同组合方式；结果不是一条 pair 的偶然胜利，而是 admission 机制在多个场景下都能保住高 Sharpe。
- 论文里单 pair 场景的月均收益约 **`24.7%`**、Sharpe 约 **`7.94`**、最大回撤约 **`17.3%`**，正收益月份约 **`90%`**；扩展到 Johansen 多币 spread 后，月均收益约 **`13.9%`**、Sharpe 约 **`6.96`**，但最大回撤进一步降到约 **`5.6%`**、正收益月份约 **`95%`**。
- 对我们 desk，更高价值的旁支不是“再换一个更花的 spread 指标”，而是这条拆法：`raw alpha = spread MR`，`admission = 当前哪对/哪篮子最值得做`，`risk = half-life / capital cap / execution realism`。
- 我用 Binance USDⓈ-M 公共 `15m` 数据做了一个更贴近 short-cycle 的 portability probe：在 `BTC/ETH/SOL/XRP/ADA` 上，用 **14d formation + 2d trading**、每天重选一次 pair，若只保留 `ADF p < 0.05` 且 half-life 在 `2~96` bar 的组合，再做 `z>2` 反手、回到 `|z|<0.5` 平仓，则近约 **45 天**里共 **25 笔**，gross 约 **`+341 bps`**，即便粗扣每笔 round-trip **`8 bps`** 也还有约 **`+141 bps`**；被选中的窗口主要集中在 **`ETH/XRP`（11 次）** 与 **`SOL/XRP`（8 次）**，而不是 BTC/ETH。
- 同一套 shell 若机械固定做 `BTC/ETH`，同窗口下约 **16 笔 / `-493 bps` gross**，说明这条线最该先测的不是“BTC/ETH 参数再调细”，而是 **dynamic admission 到底能不能把 pair 选对**。
- 我又做了一个更激进的 `5m` 缩短版快检：在 `ETH/SOL/XRP/ADA` 上用 **7d formation + 1d trading** 的同类 admission shell，近约 **18 天**里约 **7 笔 / `+242 bps` gross**；样本不大，但足够说明这篇思路不是只能活在慢频周尺度。

## 3. 为什么和当前项目有关
最近 desk 连续补了单资产 intraday lag / momentum，这轮更该补一篇 **relative-value / stat-arb raw alpha** 来平衡素材池。它和当前项目的直接关系是：
- base alpha 很清楚：cointegrated spread fade；
- 但真正决定能不能落地的，是 admission 层，而不是“固定 pair + 固定参数”；
- 这正好能接到我们后续的 `5m / 15m` major-alt pairs、cross-sectional RV、甚至 basket stat-arb。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / market-neutral / mean reversion
- 基础 alpha：动态筛出的 cointegrated spread 会向均值回归
- regime：只在 `cointegration / ADF` 通过且 half-life 足够短的窗口启用
- filter / veto：`p-value` 不过线、half-life 太长、z-score 未到阈值时不交易
- risk / sizing / execution overlay：formation/trading 分窗、half-life 约束、capital cap、bid/ask 成交假设、rough fee/funding 扣减

## 4. 可复刻的最小实验
**研究假设：** 对 short-cycle crypto pairs，alpha 本体不是“任何两条相关曲线都会回归”，而是 **被动态 admission 选中的短 half-life pair** 更容易在未来 `1~2d` 的 `5m/15m` 上完成 spread reversion。

**最小实验：**
1. 资产：Binance / Bybit top-liquid perps，先 `BTC/ETH/SOL/XRP/ADA/TRX`；
2. 周期：先 `15m`，再压到 `5m`；
3. formation / trading：先测 `14d / 2d` 与 `7d / 1d`；
4. admission：每天重选一次，保留 `ADF p < 0.05`、half-life 落在可交易区间的 pair；
5. 交易：`z > 2` 做空 spread，`z < -2` 做多 spread，回到 `|z| < 0.5` 平仓，窗口结束强平。

**先看 2 个指标：**
- dynamic admission 相对固定 `BTC/ETH` 的 `post-cost bps/trade` 改善；
- 被选中 pair 的集中度是否稳定（是否长期集中在少数 alt-major 组合）。

## 5. 风险与保留意见
- 论文主样本是 **BitMEX 1m**，我本地 probe 是 **Binance perp 近窗口 15m/5m**，两者不是同一市场结构；这里证明的是 portability，不是原文逐表复刻。
- 当前快检还没把 funding、borrow、真实双腿冲击和下单量约束完整接入，所以只能当 first verdict，不能当 production 回测。
- dynamic admission 也有过拟合风险：如果 pair 每天频繁漂移，交易成本可能把“选对 pair”的 edge 吃掉。
- `5m` 快检样本仍短，只说明有可继续追的苗头，不说明已经过稳健线。

## 6. 来源
- Poplavskyi, V., Serhieiev, O., Ovsii, D., & Zhukov, V. (2021). *Evaluation of Dynamic Cointegration-Based Pairs Trading Strategy in the Cryptocurrency Market*. *Studies in Economics and Finance*.
- DOI: `10.1108/SEF-12-2020-0497`
- Readable URL: `https://doi.org/10.1108/SEF-12-2020-0497`
- arXiv full text: `https://arxiv.org/abs/2109.10662`
- PDF used this round: `https://arxiv.org/pdf/2109.10662.pdf`

## 7. 一句话带走
**别再把 pairs 写成“固定 BTC/ETH + 固定 z-score”的老模板；对 short-cycle crypto，真正该先测的是“今天该做哪一对”——dynamic admission 可能比 spread 公式本身更重要。**
