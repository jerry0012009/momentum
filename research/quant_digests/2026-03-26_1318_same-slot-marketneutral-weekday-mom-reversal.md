# 别把这份 2023/2025 repo 只读成“按时段切换动量/反转”：更该先测的是「same-slot cross-sectional market-neutral」完整 raw alpha
- 时间：2026-03-26 13:18 UTC
- 类型：2023 GitHub 仓库（2025 仍在更新）+ notebook 代码级审阅 + Binance Futures 公共 `15m` 最小 transfer check
- 主题类型：raw alpha
- 基础 alpha：**对每个固定日内时钟槽（same slot），按过去若干天“同一时钟槽”的平均收益做横截面排序；在 weekday after-hours 做 loser-longer reversal，在 weekday regular-hours 做 winner-longer momentum，再组一个 market-neutral 篮子。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/market-neutral/same-slot/time-of-day/momentum/reversal/weekday/off-hours/regular-hours/15m/1h/5m/3m/repo/binance/perpetual/cost-turnover
- 证据类型：repo notebook 规则审阅 + 当前公开数据最小 transfer

## 1. 这次看了什么
先回答一句：**这篇东西的 base alpha 是什么？**

不是“时段过滤器”，也不是“regular hours 比较重要”这种空话。**它的 alpha 本体，是 same-slot 横截面排序本身。**

主材料是 GitHub 仓库：
- **MateoPedro (2023, updated 2025), _StatArb_**
- Readable URL：`https://github.com/MateoPedro/StatArb`
- Repo URL：`https://github.com/MateoPedro/StatArb`
- Raw notebook：`https://raw.githubusercontent.com/MateoPedro/StatArb/main/Project%20.ipynb`

这份 repo 的真正价值，不是“又一个 notebook 回测”，而是它把一条**可以独立交易的 cross-sectional raw alpha** 写得很具体：

1. 先按 `1h` bar，把 10 个主流币放进横截面；
2. 对每个固定小时 separately 计算过去 `N` 天**同一小时**的平均收益；
3. 在横截面内做 `rank → demean → normalize`，得到市场中性权重；
4. 在 weekday after-hours 交易短 lookback reversal（`1~2d`）；
5. 在 weekday regular-hours 交易长 lookback momentum（`9~21d`）；
6. 再对两个子策略做 Sharpe-based weighting。

repo notebook 里直接给出的组合结果是：
- **annualized return ≈ 16.7%**
- **annualized vol ≈ 8.2%**
- **Sharpe ≈ 2.03**
- **max drawdown ≈ 8.67%**
- **alpha t-stat ≈ 2.05**

翻成人话：**这不是“某个时段只做多/只做空”的时间过滤，而是“同一 clock slot 的跨币种相对强弱，会在不同会话口袋里表现成不同方向的 market-neutral alpha”。**

## 2. 核心结论
### 2.1 repo 里最值得 intake 的，不是时间过滤，而是 same-slot 横截面框架
这份 repo 真的可拿来做 desk intake 的地方有 3 个：

1. **它是 raw alpha，不是 filter 假装成 alpha。**
   `time-of-day` 在这里不是 veto，而是决定你在某些 slot 里该做 reversal 还是 momentum 的 primary regime。

2. **它天然是 market-neutral。**
   不是单币追涨杀跌，而是 `rank-demean-normalize` 后的 long-short 篮子，先天更适合 desk 做成本和 beta 归因。

3. **它自带 entry/exit/sizing/risk/cost 骨架。**
   - entry：每个时钟槽 bar close 生成横截面权重，下一 bar 执行
   - exit：下一次权重刷新时 rebalance
   - sizing：normalized dollar-neutral
   - risk：两个子策略再做上层权重整合
   - cost：repo 在 notebook 中直接加了 `20 bps` t-cost 讨论

### 2.2 这条线和昨天那篇 `clock-conditioned own-past return` 不一样
昨天 intake 过的 `clock-conditioned intraday momentum/reversal` 更像：
- **单资产**
- **own-past return**
- **方向型**

而这份 repo 更像：
- **多资产横截面**
- **same-slot relative strength / weakness**
- **market-neutral long-short**

所以别把它误读成重复主题。**前者是“这个币在这个时段偏 continuation 还是 reversal”，后者是“这一组币在这个时段，谁该多、谁该空”。**

## 3. 为什么和当前 desk 直接相关
这轮我认为它值得优先 intake，原因很直接：

1. **它补的是 raw alpha 素材池，不是又多一个 overlay。**
2. **它服务的是 current desk 明显还需要继续补的 trend/momentum 家族，但形式不是单币 breakout，而是更像 alpha desk 的横截面 market-neutral。**
3. **它可以很自然地下沉到 `15m/5m`。**
   把 `same hour` 改成 `same 15m slot`，就能做对我们更贴脸的最小实验。

如果用当前任务要求那句话来审题：
- **这篇东西的 base alpha 是什么？**
- 答案是：**same-slot 横截面动量/反转排序。**

所以它不是“只可当 filter”的材料，而是**可直接落地的完整策略候选**。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / market-neutral / 可 momentum 也可 reversal
- 基础 alpha：
  - 对每个时钟槽 `s`，计算资产 `i` 的过去 `L` 天 same-slot 平均收益 `avg_ret(i, s, L)`
  - 在该时刻横截面排序后做 `demean + normalize`
  - reversal 分支：long same-slot losers / short same-slot winners
  - momentum 分支：long same-slot winners / short same-slot losers
- regime：
  - primary：`weekday after-hours` vs `weekday regular-hours`
  - secondary：不同 lookback 家族（短 lookback 偏 reversal，长 lookback 偏 momentum）
- entry：bar close 生成权重，`next bar` 执行
- exit：下一个 rebalance 时点按新权重调仓
- sizing：横截面绝对权重归一，净敞口为 0；上层对子策略再做组合权重
- risk：单币权重上限、单时段 turnover cap、单日损失上限、BTC beta 监控
- cost：核心风险不是信号定义，而是 **rebalance frequency × turnover**

## 4. 当前 `15m` transfer check：对我们 desk 还有没有边？
为了不只复述 repo，我做了一个更贴 desk 的最小迁移：

### 4.1 数据与口径
- 数据源：Binance USDⓈ-M Futures 公共 `15m` K 线
- 标的：`BTC/ETH/BNB/XRP/ADA/SOL/DOGE/AVAX`
- 窗口：最近 **120 天**
- 迁移方式：
  - 把 repo 的 `same hour` 改成 `same 15m slot`
  - `weekday after-hours` 做 **`1~2d` same-slot reversal**
  - `weekday regular-hours` 做 **`9~21d` same-slot momentum**
  - 执行仍是 `next bar`
- 成本口径：先放一个较乐观但不离谱的 baseline：**单边 2 bps**（约 round-trip 4 bps）

产物目录：
- `reports/artifacts/quant_digests/same_slot_marketneutral_transfer_20260326_1315/summary.json`

### 4.2 结果一：after-hours same-slot reversal 还有 gross edge，但 turnover 高得吓人
`weekday after-hours + 1~2d reversal`：
- **gross ≈ +0.172 bps/bar**
- **annualized gross return ≈ +60.2%**
- **gross Sharpe ≈ 6.88**
- 但 **turnover ≈ 55.2x/day**
- 扣到单边 2 bps 后：**net ≈ -0.978 bps/bar**

这很像 repo 自己给出的那层诚实结论：**alpha 可能是真的，但执行频率和换手足以把它吃穿。**

### 4.3 结果二：regular-hours same-slot momentum 在当前 15m perp 上没接住 repo 的叙事
`weekday regular-hours + 9~21d momentum`：
- **gross ≈ -0.101 bps/bar**
- **gross Sharpe ≈ -4.97**
- **turnover ≈ 24.0x/day**

也就是说，至少在当前这版 `15m` Binance perp proxy 上，**同样的 same-slot 长 lookback momentum 没有成功迁移。**

### 4.4 结果三：把两个分支硬拼在一起，gross 只剩很薄的正值，净值照样不活
`0.5 × reversal + 0.5 × momentum`：
- **gross ≈ +0.035 bps/bar**
- **annualized gross return ≈ +12.4%**
- **gross Sharpe ≈ 2.20**
- **turnover ≈ 39.2x/day**
- 扣单边 2 bps 后：**net ≈ -0.781 bps/bar**

所以对 desk 更诚实的判断是：
- **repo 的框架值得收进素材池；**
- **但当前最可能活着的是“off-hours same-slot reversal”这一支，而不是完整照搬 two-branch combo；**
- **并且它首先是 turnover / execution 问题，不是 alpha 方向问题。**

## 5. 这条线现在该怎么 desk 化
### 5.1 先别做“全天同配方”
这份材料最不该学的，就是把所有时段揉成一条统一信号。真正该学的是：
- **时钟槽分桶**
- **分支拆开看**
- **先问哪一支还活、哪一支已经死**

### 5.2 当前最值得保留的分支：same-slot reversal，而不是 whole package
如果只看这轮 `15m` transfer：
- momentum 分支当前更像已经失效或需要更窄 pocket；
- reversal 分支仍有 gross signal，但需要先解决 turnover cliff。

因此本轮最合理的 desk intake 不是“照抄 repo 组合”，而是：
- **把 `weekday after-hours same-slot reversal` 收为 raw alpha 候选；**
- 同时把 **trade throttle / top-k / no-trade bucket / maker-first** 当成生死层，而不是可有可无的优化项。

## 6. 下一步怎么测
这里不能停在“repo 很有意思”。下一步要直接拆 execution 生存线：

1. **先做 slot-level 稀疏化。**
   不要每个 `15m` slot 都打。先筛：
   - 只做 gross expectancy 前 `10~20` 个时钟槽；
   - 或只做过去 rolling `30~45d` 仍为正的 slot。

2. **加 top-k / band trigger，别全横截面都换。**
   当前 rank-demean-normalize 每 bar 都会动，turnover 太高。下一轮优先测：
   - 只交易 `|score|` 最大的 top `2~3` 个币；
   - 或设置 entry band，只有 score 过阈值才换仓。

3. **把 15m bar-bar rebalance 改成“持有 2~4 bar，减半频率”。**
   这条线当前最像“alpha 有、但换手太密”。如果持有期稍拉长后 gross 不明显塌，才有资格继续。

4. **做 maker-first / passive fill 假设的 break-even 曲线。**
   当前用的是单边 `2 bps`。下一轮至少要画：`0.5 / 1 / 2 / 3 bps` 单边成本曲线，看这条线到底活在哪个 fee pocket。

5. **把 regular-hours momentum 单独做死亡确认。**
   它也许不是完全没 edge，而是：
   - 需要更长历史；
   - 只活在特定 symbol bucket；
   - 或只能活在 `1h`、活不到 `15m`。
   在没确认前，不要把它继续当这条线的主卖点。

## 7. 风险与保留意见
- repo 是单 notebook 研究，不是 production system；
- repo 的原始回测窗口偏短，且时间段比较特殊；
- 我做的 current transfer 是 **Binance perp `15m` proxy**，不等于 clean replication；
- annualized 数字在高频场景容易显得很夸张，所以这轮更该盯的是：
  - **bps/bar**
  - **turnover/day**
  - **成本后的生存线**
- 这条线当前最关键的风险，不是“alpha 方向可能错”，而是**换手把 edge 全磨没**。

## 8. 来源
1. **MateoPedro. (2023, updated 2025). _StatArb_. GitHub repository.**
   - Readable URL: `https://github.com/MateoPedro/StatArb`
   - Repo URL: `https://github.com/MateoPedro/StatArb`
   - Raw notebook: `https://raw.githubusercontent.com/MateoPedro/StatArb/main/Project%20.ipynb`
2. **Binance Developers. _USDⓈ-M Futures API – Kline/Candlestick Data_.**
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

## 9. 本地相关产物
- Digest：`research/quant_digests/2026-03-26_1318_same-slot-marketneutral-weekday-mom-reversal.md`
- Artifact：`reports/artifacts/quant_digests/same_slot_marketneutral_transfer_20260326_1315/summary.json`
