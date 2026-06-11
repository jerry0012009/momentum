# 别把这份 2026 crypto stat-arb repo 只读成 2.10 Sharpe README：对 short-cycle desk，更该先拆的是「低成交 state 下的 XS reversal + 高成交 state 下的 slow TSMOM」这条组合 raw alpha，但 15m perp 版本先被换手吃掉

- 时间：2026-04-12 07:49 UTC
- 类型：quant_digest
- 主题标签：raw-alpha/cross-sectional/relative-value/time-series-momentum/mean-reversion/volume-state/router/turnover/cost/market-neutral/binance-perpetual/15m/5m/3m/1m/repo/public-data/risk
- 证据类型：2026 GitHub repo source audit（`README.md` + `crypto-stat-arb.py`）+ Binance USDⓈ-M `15m` public portability probe

- 主题类型：raw alpha
- 基础 alpha：在高流动性 crypto 横截面里，**低成交状态优先做短周期横截面反转（long loser / short winner），高成交状态优先做较慢的时序动量（follow relative strength）**，再把两条书合成一个 beta-light 组合
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 这次看了什么
这次不是继续补一个单币形态，而是补一条**横截面 / relative-value 家族**的新 repo 线索。原因很简单：当前 desk 的 raw alpha 池里，单币趋势、单币均值回归、盘口流这类材料已经很多；但**“一条能完整写出 entry / exit / sizing / cost 的横截面组合策略”**依然值得持续补货。

这份 2026 GitHub repo 最值得拿走的，不是 README 里的 `2.10 Sharpe` 结论本身，而是它提供了一条很清楚的组合骨架：
- 一条**慢一些的 time-series momentum** 书；
- 一条**快一些的 cross-sectional reversal** 书；
- 中间用**volume state** 去路由或放大；
- 最后再做策略层组合。

翻成人话：**不是“押单币方向”，而是在币篮子里决定“现在更该追强，还是更该抄弱”**。

## 2. 先回答一句：这篇东西的 base alpha 是什么？
先把话说死：
- 它的 **base alpha 不是** volume filter 本身；
- 它的 **base alpha 不是** Sharpe-weighting 本身；
- 它的 **base alpha 也不是**“低 beta”这种结果描述。

真正的 alpha 本体是两条可独立存在的书：

1. **XS reversal 书**
   - 在一篮子币里，找最近相对弱的币做多、相对强的币做空；
   - 本质是 **cross-sectional mean reversion / liquidity provision**。

2. **TSMOM 书**
   - 看每个币最近表现相对自己长期基线是更强还是更弱；
   - 本质是 **time-series momentum**。

volume state 的作用，是决定**哪条书该更大、哪条书该更小**。所以这轮主题属于 **raw alpha**，不是纯 filter / overlay。

## 3. 为什么这轮值得写
### 3.1 它补的是“组合级 raw alpha”，不是又一个局部触发器
当前 desk 已经有很多：
- 单币 directional
- 事件驱动
- microstructure
- options RV

但**横截面 long-short 组合**的补货价值依然很高，因为这类策略天然更接近：
- beta-light
- 可做 market-neutral
- 可把风险拆到组合层，而不是每次都赌单币方向

### 3.2 它是完整策略，不是只有一句 intuition
repo 虽然小，但并不空：
- 数据抓取
- 信号公式
- 仓位合成
- 成本扣减
- alpha/beta 统计

都写在 `crypto-stat-arb.py` 里，足够拆成可执行研究笔记。

### 3.3 它非常适合拿来做“desk 化二次拆解”
repo 原版是：
- Binance US
- `4h`
- 15 个币

这不适合原样搬到我们这里；但它背后的**结构**很适合 desk 化迁移：
- 把 fast reversal 和 slow momentum 分开测；
- 把 volume state 从“解释变量”变成“路由器”；
- 把组合层 turnover 问题提前暴露出来。

## 4. 来源信息
### 4.1 主来源：GitHub repo
- **Author**：Parnell Thrower
- **Year**：2026
- **Title**：*Cryptocurrency Statistical Arbitrage*
- **Venue**：GitHub repository
- **DOI**：N/A
- **Readable URL**：<https://github.com/PThrower/crypto-start-arb>
- **Repo URL**：<https://github.com/PThrower/crypto-start-arb>
- **关键文件**：`README.md`、`crypto-stat-arb.py`

### 4.2 repo README 里给出的 headline 数字
README 报告的是一套 `4h`、15 币、Binance US 的组合结果：
- **Combined Sharpe**：`2.10`
- **Total Return**：`1.78x`
- **Max Drawdown**：`-5.07%`
- **Beta vs BTC**：`0.011`
- **Annual Trading Cost**：`0.16%`

这些数字能不能原样信，不是本轮重点；重点是：**这个 repo 提供了一条值得拆的 alpha 结构。**

## 5. repo 代码到底在做什么
### 5.1 横截面反转：找最近相对输家的反打
`xs_strategy(ret, N)` 的核心很直接：
1. 先算过去 `N` 根的滚动均值收益；
2. 在横截面里做 rank；
3. 去均值；
4. 再按绝对值和归一化。

也就是说，这不是“找 cointegration pair”，也不是“找一个 winner-long-only 列表”，而是：
**在整个 universe 里同时 long losers、short winners。**

repo 里用的是：
- `N = 6` 个 `4h` bar
- 也就是大约 **24 小时** 的横截面 reversal 书

### 5.2 时序动量：看“最近强弱”相对自己长期基线
`ts_momentum(ret, short_window, long_window)` 的写法也很标准：
- 短窗均值减长窗均值
- 再除以长窗波动
- 最后用 `tanh` 压成有限仓位

repo 参数是：
- `short_window = 42` 个 `4h` bar（约 1 周）
- `long_window = 1080` 个 `4h` bar（约 6 个月）

翻成人话：
**不是单纯看“涨了就追”，而是看“最近这段强弱，相对于它自己长历史算不算异常”。**

### 5.3 volume state：README 说的是 router，代码写的是连续 signed multiplier
repo README 的叙事是：
- momentum 在高成交时更有用
- reversal 在低成交时更有用

但代码层的实现其实更细一点：
- 先算 `volume_signal`
- 再对它做 `tanh`
- 然后直接乘到 momentum / reversal 权重上

也就是说，代码不是一个硬切换的“高量=momentum、低量=reversal”二元路由器，而更像：
**一个连续的、带正负号的 volume multiplier。**

这个细节很重要，因为它决定了：
- 原版更像“连续缩放 / 连续翻转”
- desk 化时更值得先测的是“离散 router 版本”

## 6. 这条策略最值得拿走的几个硬点
### 6.1 这是一个“组合级双书结构”
repo 不是只给一条信号，而是给了两个层次明显不同的 alpha：
- **slow TSMOM**：更慢、方向性更强
- **fast XS reversal**：更快、更偏 market-neutral

这对 desk 很有用，因为我们不一定非要一起做；完全可以把它拆成两条研究分支。

### 6.2 反转书天然更贴近 short-cycle，但也更容易死在换手上
从结构上看：
- XS reversal 的持仓更新会更频繁；
- 组合层 turnover 会比单币策略高很多；
- 如果没有 no-trade band、top-bottom 截断、分批 rebalance，很容易**gross 有 edge，net 被手续费和冲击吃掉**。

这轮 public probe 也基本验证了这一点。

### 6.3 原 repo 的 Sharpe-weighting 本身带有“研究期内知道谁更强”的味道
代码里先用全样本算每个币、每条书的 Sharpe，再拿这个结果去做组合权重；
这更像研究期内的静态组合说明，不是 production-ready 的在线分配器。

对 desk 来说，这意味着：
- **先别迷信最终组合 Sharpe**；
- 更该看的是每条书本身的可迁移性，以及它们在短周期上的 turnover / cost 轮廓。

## 7. Binance USDⓈ-M `15m` portability probe：先看结构能不能迁到短周期 perp
### 7.1 我怎么测的
为了看这套结构能不能服务 short-cycle desk，我做了一个**最小 desk 化 probe**：

- **数据源**：Binance USDⓈ-M perpetual public klines
- **频率**：`15m`
- **区间**：`2026-01-12 ~ 2026-04-12`（近 90 天）
- **币种**：`BTC, ETH, BNB, XRP, SOL, ADA, DOGE, LINK`
- **成本假设**：单边 `4 bps`
- **desk 化窗口**：
  - momentum：`224 / 1344` bars（约 `2.3d / 14d`）
  - reversal：`32` bars（约 `8h`）
  - volume state：`32 / 224` bars（约 `8h / 2.3d`）

这里我没有硬抄 repo 的 `4h` 原参数，而是做了一个**适合 `15m` desk 最小实验**的缩短版。

### 7.2 probe 结果：gross 里有东西，但 15m net 基本被换手吃掉
#### A. repo 风格 momentum 分支
- **gross cumulative return**：`+3.1%`
- **net cumulative return**：`-34.0%`
- **gross Sharpe**：`0.50`
- **net Sharpe**：`-2.74`
- **平均每 bar turnover**：`0.129`

结论：慢动量分支在 `15m` 上不是完全没信号，但**边太薄**，一上 perp 成本就不够看。

#### B. repo 风格 reversal 分支
- **gross cumulative return**：`-19.3%`
- **net cumulative return**：`-74.5%`
- **gross Sharpe**：`-3.76`
- **net Sharpe**：`-24.50`
- **平均每 bar turnover**：`0.334`

结论：照 repo 的 signed volume multiplier 直接搬到 `15m` perp，**reversal 这条线不成立**。

#### C. repo 风格 combo（两条书直接合成）
- **gross cumulative return**：`-11.1%`
- **net cumulative return**：`-71.3%`
- **gross Sharpe**：`-0.80`
- **net Sharpe**：`-10.73`
- **平均每 bar turnover**：`0.327`

结论：**整套 README 叙事原样 desk 化，不行。**

#### D. 只拿“plain XS reversal”出来看
- **gross cumulative return**：`+22.0%`
- **net cumulative return**：`-55.0%`
- **gross Sharpe**：`5.60`
- **net Sharpe**：`-22.06`
- **平均每 bar turnover**：`0.289`

#### E. 只拿“low-volume XS reversal”出来看
- **gross cumulative return**：`+38.6%`
- **net cumulative return**：`-49.3%`
- **gross Sharpe**：`5.43`
- **net Sharpe**：`-10.88`
- **平均每 bar turnover**：`0.291`

这两条最有启发：
- **反转书本体不是没东西**；
- 但在 `15m` perp、按 bar 级重排、单边 `4 bps` 成本下，**alpha 先被 turnover 杀死了**。

## 8. 这轮 probe 真正说明了什么
### 8.1 值得 intake 的不是 README 里的组合，而是“反转书 gross edge + 成本问题”
如果只看 repo headline，很容易得到一个错觉：
> 把 TSMOM + reversal + volume filter 搬过来就行。

但这轮最诚实的结论其实是：
- `15m` 上，**最有信息量的是 low-volume XS reversal 这条书的 gross edge**；
- repo 那种直接组合方式，对 perp 短周期不够稳；
- 真正的工作重点应该转向**turnover compression / execution transfer**，而不是继续往 signal 里塞新指标。

### 8.2 这更像 `15m signal, slower rebalance / narrower basket / cheaper execution` 题，而不是 bar-close taker 题
如果你每根 `15m` 都按全横截面重排，组合 turnover 太高。

所以这条线更合理的读法是：
- 信号可以在 `15m` 生成；
- 但**组合再平衡频率**不一定也要是 `15m`；
- 甚至更应该：
  - 只做 top/bottom 少数名次；
  - 用 no-trade band / hysteresis；
  - 用 `30m / 60m` hold 或 staggered rebalance；
  - 由 `1m / 5m` 去找更好的执行点。

### 8.3 对 short-cycle desk，最该优先拆的是“低量反转书”，不是整个 README combo
因为：
- slow TSMOM 这条线，在 `15m` 上边很薄；
- low-volume XS reversal 至少 gross 上像真东西；
- 而且它天然适合做：
  - market-neutral
  - relative-value
  - beta-light
  - basket-style execution routing

## 9. 我对这份材料的 desk 结论
### 9.1 这轮主题仍然是 raw alpha，不降级成 filter
原因很简单：
- 把 volume state 拿掉，plain XS reversal 仍然是一条完整策略；
- 把 TSMOM 拿掉，reversal 仍然能单独做；
- 所以它不是纯 filter / regime 主题。

### 9.2 但当前 short-cycle desk 最值得保留的，只是其中一个“可压缩换手”的分支
我会这样排序：
1. **优先保留**：`low-volume XS reversal` 这条 raw alpha 候选
2. **次级保留**：`plain XS reversal` 作为对照书
3. **延后处理**：slow TSMOM 分支
4. **不建议直接照搬**：repo 原版 continuous volume multiplier + static Sharpe-weighted combo

### 9.3 它和当前 desk 的关系很直接
这轮不是离题的“泛化综述”，而是直接补：
- raw alpha 素材池里的 **cross-sectional / relative-value / stat-arb** 家族
- 且非常适合和现有的：
  - funding / basis
  - positioning
  - liquidity / cost
  - execution veto
  这些 shared component 拼起来

## 10. 对 `1m / 3m / 5m / 15m` 的最小落地建议
### 10.1 别先做全市场全排序，先做 top-bottom 截断
第一版建议：
- 只在 `8~12` 个高流动性 perp 里做
- 每次只做 **top 2 / bottom 2** 或 **top 3 / bottom 3**
- 其余币不动

这样做的目的很直接：
**把 turnover 从“全横截面重排”压成“极端名次轮换”。**

### 10.2 别每根 bar 全量 rebalance，先试 fixed hold + hysteresis
建议先测：
- signal bar：`15m`
- hold：`30m / 60m / 90m`
- 只有当 rank gap 或 score gap 超过阈值，才允许换仓

翻成人话：
**不要因为第 4 名和第 5 名交换了一次就整本书重排。**

### 10.3 成本测试必须前置，不要等到最后再扣
至少要同时跑：
- 单边 `1 bps`
- 单边 `2 bps`
- 单边 `4 bps`

如果只在 `<=1 bps` 下活着，那它更像：
- maker / queue-aware execution 题
- 或内部撮合 / 低冲击执行题

而不是普通 bar-close taker 题。

### 10.4 TSMOM 分支先降级成 slow companion，不要和 fast reversal 同频同权
更合理的 desk 版本是：
- **fast book**：`15m` low-volume XS reversal
- **slow book**：`1h` 或 `30m` 的 TSMOM companion
- 两条书的 rehedge / rebalance 频率分开

否则组合层 turnover 只会继续恶化。

## 11. 下一步怎么测
按优先级，我建议直接做下面 4 组实验：

### 实验 1：只测 `low-volume XS reversal`
- universe：8~12 个高流动性 USDT perp
- signal：过去 `8h / 12h / 24h` 横截面 loser-winner 排名
- filter：仅在 volume z-score < 0 时开仓
- holding：`30m / 60m / 90m`
- rebalance：非每 bar，改成 fixed hold

目标：确认**gross edge 在降低换手后能否留到 net**。

### 实验 2：top-bottom 截断 + no-trade band
- 只做 top2-bottom2 / top3-bottom3
- 设 score gap 门槛
- 小于门槛不调仓

目标：确认 repo 的失败是不是主要来自**横截面尾部噪声 + 过度重排**。

### 实验 3：执行层 transfer
- signal 仍然 `15m`
- execution 改到 `1m / 5m`
- 用 VWAP 偏离、盘口滑点、短时反弹/回踩做分批挂单

目标：确认这条线到底是**signal 不行**，还是**execution 太贵**。

### 实验 4：把 slow TSMOM 单独升到 `30m / 1h`
- 不和 fast reversal 同频混合
- 单独测它的 cost survival

目标：确认它是否值得作为第二条 companion book 留在素材池里。

## 12. 一句话结论
这份 2026 repo 真正值得 desk intake 的，不是 README 里的“2.10 Sharpe 组合神话”，而是：

**“低成交状态下的横截面反转书，本体可能有 edge；但 `15m` perp 上若按 bar-close 全量重排，换手会先把它吃死。”**

所以本轮结论不是“照搬”，而是：
- **保留 raw alpha 本体**：`low-volume XS reversal`
- **降级原版 combo**：不直接照抄
- **下一步重点**：turnover compression + execution transfer，而不是继续往信号里加花样
