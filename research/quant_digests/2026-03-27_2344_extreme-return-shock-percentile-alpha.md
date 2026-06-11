# 别把这篇 2025 高频美股论文只读成“成本后归零”：对 desk 更该先测的是「极端短窗 return shock 的 continuation / fade 分位规则」raw alpha
- 时间：2026-03-27 23:44 UTC
- 类型：2025 开放获取论文全文 PDF
- 主题类型：raw alpha
- 基础 alpha：极端短窗收益冲击本身就是信号；超强上冲往往继续走一小段，超弱下砸则更容易先出现短窗回补，是否延续/回吐取决于阈值、持有长度与成本
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/time-series/short-horizon/shock/percentile-threshold/continuation/mean-reversion/vwap/ma-confirmation/1m/3m/5m/15m/paper/cost
- 证据类型：论文全文证据

## 1. 这次看了什么
这次看的是 **Floris Laly (2025), _High-frequency momentum and contrarian strategies in U.S. blue chips_**, 发表在 **Investment Management and Financial Innovations**。这篇东西对 desk 最有用的，不是“高频里最后都被成本吃掉”这句结论本身，而是它把一条 **最容易在 crypto 上做 first verdict 的 raw alpha 母式** 讲得很清楚：

> **base alpha 很简单：当最新一跳/最新一根 bar 的收益落到历史分位极端时，接下来几分钟会出现可交易的 continuation 或 fade。**

所以这不是 filter，也不是 overlay；VWAP / MA 只是可选确认层，alpha 本体就是 **extreme-return percentile shock**。

## 2. 核心结论
- **一句话核心结论：** 这篇论文真正值得搬的，不是“高频 momentum/contrarian 有没有故事”，而是 **“极端 return shock 分位规则”本身可以直接写成双分支 raw alpha baseline**：一支做 continuation，一支做 reversal。
- **一句话它怎么证明：** 作者用 **2020–2021 年、28 只纳斯达克高流动性蓝筹、约 6.26 亿笔逐笔成交**，系统测试 **288** 组规则，并做了 **risk / data-snooping / luck / transaction-cost** 四层清洗。
- **规则骨架非常轻：** 信号只看“最新 tick return 是否超过历史分布分位数”。momentum 用 `90/95/99` 分位上冲，contrarian 用 `10/5/1` 分位下砸；历史窗口用 **前 1 / 5 / 10 / 20 个交易日**。
- **确认层不是必须：** 288 组规则里，确认只是在 shock 触发后，再额外要求 **VWAP** 或 **5-13 / 5-21 MA crossing**；但 top 配置反而多是 **无确认、无临时止损**。
- **ex-cost 最强配置很朴素：** 最强 momentum 是 **M2：1-day 分布、95th percentile、无 trend confirm、无临时 stop**，Sharpe **0.23**、Sortino **0.28**；最强 contrarian 则集中在 **10th percentile** 的浅极端回补，如 **C3/C9** 在 `5d/10d` 分布上的 Sharpe 约 **0.21**。
- **但成本是硬墙：** 做完数据挖掘修正后，**37** 个 momentum、**43** 个 contrarian 规则在成本前仍优于 benchmark；做完 luck 修正后分别是 **63 / 69**。但一旦加入 **0.05%/trade** 的交易费，**全部归零**。
- **对 crypto 最值钱的含义：** 这说明我们不该先争论“shock 后一定追还是一定反手”，而该先问：**在我们的 bar 粒度、费率和执行方式下，哪一支还能活。**

## 3. 为什么和当前项目有关
这篇值得进池，因为它补的是一条 **便宜、快、可直接落地** 的 raw alpha 骨架：

- 不是固定形态，也不是又一个“breakout 需要确认”；
- 它直接给出 **continuation / mean reversion** 两条可对照主线；
- 规则足够轻，适合在 `1m/3m/5m/15m` 上马上做 first verdict；
- 它还能顺手回答一个当前 desk 很实际的问题：**极端 bar shock 在 crypto 短周期里，到底更像追涨杀跌，还是更像尾部回补。**

更重要的是，论文还给了一个很诚实的负面约束：**如果 5 bps 一笔就能把 edge 全抹平，那 taker-heavy 的 1m 高频版本默认不能先乐观。** 这对当前素材池非常有用，因为它逼我们把“alpha 方向判断”和“能不能穿过 friction ladder”一起看，而不是只看 gross。

## 3.5 策略拆解（必填）
- 方向属性：顺势 + 逆势双分支
- 基础 alpha：极端短窗 return shock 的后续几根 bar 仍存在可预测漂移或回补
- entry：当当前 bar return 超过滚动分位上阈值时开 continuation；跌破滚动分位下阈值时开 fade / rebound
- exit：固定持有 `1~6` 根 bar，或在分位回到中性区间时平仓
- sizing：先固定 notional；第二层再做 inverse-vol 或 signal-strength sizing
- risk：先只保留日内最大持有时间、单笔 ATR/振幅止损、单日最大亏损熔断
- cost：优先跑 maker / taker 分层；若 taker `>=4~8 bps` 已显著压缩净 edge，就不要默认往更细频压
- 更适合的 regime：短时冲击后有后续跟随、或订单流失衡后出现 quick snapback 的时段
- 主要 veto：重大数据/清算瀑布/盘口断层时的假极端 bar、极低流动币、手续费高于 edge 的超高换手版本

## 4. 可复刻的最小实验
**研究假设：** 把论文里的逐笔 shock 分位规则，降采样成 crypto 的 `1m/3m/5m` bar 后，至少其中一支（continuation 或 fade）会在 majors 上留下可穿过低成本的 pocket。

**最小实验建议：**
1. **Universe：** 先做 Binance / OKX / Bybit 的 BTC、ETH、SOL 三个高流动 perp；第二轮再扩到 `10~20` 个 majors。
2. **Bar：** 从 `3m` 和 `5m` 开始，`1m` 只做附加；`15m` 用来检查 edge 是否只是更粗时间聚合后的假象。
3. **信号：** 计算当前 bar return 相对过去 `1d / 5d / 10d / 20d` 同粒度 bar-return 分布的分位数。
4. **两条主线分开测：**
   - continuation：`ret_t >= q95 / q99` 后，顺着方向持有 `1/2/4` 根 bar；
   - fade：`ret_t <= q10 / q5` 后，反向持有 `1/2/4` 根 bar。
5. **先测最朴素版：** 默认先复现论文的“赢家配置”思路——**无 VWAP/MA confirm、无临时 stop**；确认层留到第二轮再比较是否减少假信号还是只是拖慢反应。
6. **成本口径：** 至少跑 `2 / 4 / 8 / 12 bps round-trip` 四档，并单独记 trade count、holding time、gross edge、net edge。
7. **成功标准：** 不是只看命中率，而是看：
   - 哪条分支在成本后仍 > 0；
   - `3m` 是否明显优于 `1m`；
   - 加确认层后，净值是否改善而不是只让 trade count 变少；
   - edge 是否只集中在 BTC 单资产，还是可扩到 ETH/SOL majors。

## 5. 我对这条线的当前判断
我的判断是：**值得立刻进研究池，而且优先级不低。**

原因很简单：这不是又一篇讲大框架的解释文，而是一套 **最便宜、最适合先做 first verdict 的 raw alpha baseline**。它能同时服务两类当前还值得继续补的方向：
- `shock continuation`
- `shock mean reversion`

但也要老实：论文已经明确告诉我们，**如果换手太快、执行太差，成本会把这类 edge 直接磨平。** 所以它更像“先判定哪条分支在 crypto 还活着”的 intake，不是默认可直接上线的成品。

## 6. 下一步最该怎么测
如果只给一个最优先动作，我会做这个：

> **先在 BTC/ETH `3m` perp 上做“q95 continuation vs q10 fade”对照实验，并把 `无确认` 与 `VWAP确认` 并排放到同一 friction ladder 里。**

这一步最便宜，也最能快速回答：
- 我们的短周期 desk 里，极端 shock 之后到底是“顺着做”还是“反着做”更活；
- 确认层到底是在帮忙，还是只是在事后安慰。

## 7. 来源与可复用材料
1. **Laly, F. (2025). _High-frequency momentum and contrarian strategies in U.S. blue chips_. Investment Management and Financial Innovations, 22(3), 395–413.**  
   DOI：<https://doi.org/10.21511/imfi.22(3).2025.30>  
   Readable URL：<https://www.businessperspectives.org/journals/investment-management-and-financial-innovations/issue-479/high-frequency-momentum-and-contrarian-strategies-in-u-s-blue-chips>  
   PDF URL：<https://www.businessperspectives.org/images/pdf/applications/publishing/templates/article/assets/22862/IMFI_2025_03_Laly.pdf>
2. **可直接复用的规则元件：** rolling percentile shock trigger、VWAP / MA confirm 开关、固定持有根数、成本前后 SSPA / luck correction 的诚实评估框架。
3. **Repo URL：** 暂未见作者官方复现仓库；这条线更适合直接按论文规则轻量重写。