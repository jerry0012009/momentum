# 别把这篇 2021 IRFA 论文只读成“TSMOM 风险备注”：对 crypto short-cycle desk，更该先测的是「tail-state partial-moment router × intraday TSMOM」这条 raw alpha
- 时间：2026-04-10 00:10 UTC
- 类型：论文
- 主题类型：raw alpha
- 基础 alpha：`lookback sign TSMOM`（过去一段收益的方向会延续）；`UPM/LPM` 只负责把 continuation 和 reversal 拆开
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：trend / momentum / time-series-momentum / tail-risk / partial-moment / regime-router / 15m / 5m
- 证据类型：论文证据 + Binance USDⓈ-M 公共数据 portability probe

## 1. 这次看了什么
我读的是 **Zhenya Liu, Shanglin Lu, Shixuan Wang (2021), _Asymmetry, tail risk and time series momentum_, International Review of Financial Analysis**。不是把它读成“TSMOM 也有尾部风险”这种泛结论，而是把它读成：**同样是顺势信号，近期上涨尾巴和下跌尾巴的形状，能提示这笔趋势单更像该继续跟，还是该先别跟、甚至反手。**

## 2. 核心结论
- 这篇东西的 base alpha 很清楚：**时间序列动量**。先用过去 `J` 天累计收益的正负给方向，再用 `UPM/LPM`（上行/下行 partial moment）判断当前 trend 更像 continuation 还是即将 reversal。
- 论文不是纯机制文，而是给了**可复现的 rule-based router**：以 `30d` TSMOM 为母信号，再看 `5d UPM/LPM` 落在历史联合分布 `(80%, 80%)` 量化阈值划出的 4 个区域，做 `go momentum / close out / flip`。
- 文中原始 TSM 在全样本（2008-2019，中国 `31` 个商品期货）里，`20d` lookback 约有 **`25.16%` annual return / `1.29` Sharpe / `-8.90%` max drawdown**；说明 base alpha 先成立，再谈 tail router。
- 更值钱的是后半段：在 `2013-2019` 子样本，作者说 **MTSM-S2 相比原始 TSM 平均把 Sharpe 提高约 `20%`**；以 `30d` lookback 为例，约从 **`1.04 -> 1.25`**，最大回撤约从 **`-18.73% -> -11.13%`**。
- COVID crash 段也不是只会防守：`30d` lookback 下，文中 `MTSM-S2` 约 **`28.61%` annual return / `1.79` Sharpe / `-4.81%` max drawdown**，而原始 TSM 约 **`24.49%` / `1.39` / `-8.51%`**。
- 我做的 crypto portability probe 不是全文 faithful replication，只是快检这条思想能不能压到 `15m/5m`：在 Binance USDⓈ-M `BTC/ETH/SOL/XRP/ADA/DOGE/LINK/AVAX`、`2026-02-01 ~ 2026-04-10` 上，若先用 **`24h` 收益方向**做 baseline TSM，再看近 **`6h` UPM/LPM** 是否与趋势同向，则：
  - `15m` baseline next-bar signed return 约 **`-0.12 bps/bar`**；
  - 若只保留 **tail 与趋势同向** 桶，约 **`+0.07 bps/bar`**；
  - **tail 与趋势冲突** 桶约 **`-0.43 bps/bar`**；
  - 若做一个最粗糙的 `flip-on-conflict` router，`15m` 约可到 **`+0.20 bps/bar`**。
- `5m` 上同样方向也成立，但更弱：baseline 约 **`+0.03 bps`**，粗糙 `flip` router 约 **`+0.10 bps`**。高置信结论是：**这条线更像 15m 先验证、5m 再压缩。**

## 3. 为什么和当前项目有关
这篇对 desk 的价值，不是又补一篇“趋势有效”的论文，而是把一个很实用的问题写清楚了：
**为什么同样是顺势信号，有时该跟，有时却会马上挨一刀？**

对当前 `momentum` 主线，它更像：
- 一个可独立复现的 **trend raw alpha**（TSMOM）
- 再加一个能服务 trend sleeve 的 **tail-state router / veto / flip layer**

它特别适合接到我们已有的 `turning-point`、`anchor-open displacement`、`breakout`、`shock router` 这些 raw alpha 外面，做一个 shared gate：
**最近几小时的上/下行尾部风险，究竟是在给趋势加油，还是在提示“这段趋势已经变脏了”。**

## 3.5 策略拆解（必填）
- 方向属性：顺势为主；冲突 tail state 下允许 flat / 反手
- 基础 alpha：过去一段收益方向会在下一小段时间继续（TSMOM）
- regime：`UPM/LPM` 联合状态；可用滚动 `(80%,80%)` 历史分位划四象限
- filter / veto：正趋势但 `LPM` 尾部主导时，不要机械继续做多；负趋势但 `UPM` 尾部主导时，不要机械继续做空
- risk / sizing / execution overlay：先用 `bar-close -> next-bar` 测 direction router；过第一关后再补成本、holding horizon、vol-target、maker/taker 分层

## 4. 可复刻的最小实验
**研究假设**：`15m` 上的原始 TSM baseline 很容易把“快要反转的坏趋势”也一并吃进去；若用近 `6h` 的 `UPM/LPM` 把 tail-state 分桶，可提升短持有窗的 post-cost expectancy。

**一个可计算定义**：
- `trend_t = sign(log(close_t / close_{t-96}))`  （`15m` 的 `24h` trend sign）
- `UPM_t = sum(max(ret, 0)^2, last 24 bars)`
- `LPM_t = sum(max(-ret, 0)^2, last 24 bars)`
- 快速版 router：
  - 若 `trend_t > 0` 且 `UPM_t > LPM_t`，保留 long；若 `LPM_t > UPM_t`，先 flat 或 flip
  - 若 `trend_t < 0` 且 `LPM_t > UPM_t`，保留 short；若 `UPM_t > LPM_t`，先 flat 或 flip

**最小回测切口**：
- 资产：Binance / OKX top-liquid perps，先 `BTC/ETH/SOL/XRP/ADA/DOGE/LINK/AVAX`
- 周期：先 `15m`，持有 `1` 根与 `4` 根；再压到 `5m`
- 样本：近 `90~180d`
- 对照：`base TSM` vs `align-only veto` vs `flip-on-conflict`

**最该先看哪 1~2 个指标**：
1. `post-cost expectancy / trade or / bar`
2. `conflict bucket` 是否稳定显著更差（这是 router 值不值钱的关键）

## 5. 风险与保留意见
- 论文样本是**中国商品期货日频**，不是 crypto perp；我这里只做了思想 portability，不是声称 paper 结果可直接平移。
- 论文里明确说**没有处理交易成本**；对 `5m/15m` crypto 来说，这恰好是生死线，所以不能只看方向正确率。
- 我本地 probe 只做了简化版 `UPM/LPM alignment`，**没有完整复刻论文的四象限 + S1/S2 规则**；下一步若要正式 admission，应该把 `(80%,80%)` joint-quantile quadrant faithfully 搬到 perp 数据上。
- 当前 `15m` 结果优于 `5m`，说明这条线更像 **short-horizon router**，不是越快越好。

## 6. 来源
- Zhenya Liu, Shanglin Lu, Shixuan Wang. (2021). *Asymmetry, tail risk and time series momentum*. *International Review of Financial Analysis*.
- DOI: `10.1016/j.irfa.2021.101938`
- Readable URL: `https://doi.org/10.1016/j.irfa.2021.101938`
- Accepted PDF: `https://centaur.reading.ac.uk/100824/1/FINANA-D-21-00329-R1.pdf`

## 7. 一句话带走
**这篇最值钱的不是“TSMOM 也有尾部风险”，而是：近期上/下行 tail shape 本身就能把“该继续跟的趋势”和“更像快反转的假趋势”拆开。**
