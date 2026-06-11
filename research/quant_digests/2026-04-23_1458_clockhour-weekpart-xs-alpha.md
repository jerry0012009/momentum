# 别把这份 market-neutral crypto repo 只读成“又一个 intraday momentum notebook”：对 short-cycle crypto desk，更该先拆的是「同一 clock-hour 横截面 loser→winner fade / leader continuation」这条时段条件 raw alpha

- 时间：2026-04-23 14:58 UTC
- 类型：2023 GitHub repo source audit（`README.md` + `Project.ipynb`）+ Binance Spot public-data portability probe（10-coin universe，`1h` parent，`15m/5m` child-exec 映射）
- 主题类型：raw alpha
- 基础 alpha：**对每个固定 clock-hour 单独建横截面信号：若某币在“过去若干天的同一小时”里持续弱于同组，下一次来到这个小时，做 loser→winner fade；若某币在更长 lookback 上持续强于同组，下一次来到这个小时，做 winner continuation。它交易的是“同一时段的相对表现延续/回摆”，不是裸做单腿方向。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/relative-value/time-of-day/clock-hour/weekpart/momentum/mean-reversion/market-neutral/1h-parent/15m/5m-child-exec/repo/public-data/cost/risk
- 证据类型：repo source + public API portability probe

## 1) 这次看了什么
主线材料：
- **Mateo Pedro（GitHub）**
- **Year：** 2023（repo 最近主提交 2023-08-01）
- **Title：** *StatArb* / *Market-Neutral Crypto Strategy*
- **Venue：** GitHub repository
- **DOI：** N/A
- **Readable URL：** <https://github.com/MateoPedro/StatArb>
- **Repo URL：** <https://github.com/MateoPedro/StatArb>
- **可读 raw URL（README）：** <https://raw.githubusercontent.com/MateoPedro/StatArb/main/README.md>
- **可读 raw URL（notebook）：** <https://raw.githubusercontent.com/MateoPedro/StatArb/main/Project%20.ipynb>

repo README 自述的主张是：
- 这是一个 **market-neutral crypto strategy**；
- 核心利用 **matching-period intraday momentum** 与 **potential reversals**；
- `README.md` 报告了 3 年、10 币回测里大约 **Sharpe 2.03 / MaxDD 8.66% / alpha t-stat 2.05**。

但对我们这边真正重要的，不是把它复述成“作者说有 Sharpe 2.03”，而是先把 **base alpha** 说清楚：

> **它的 base alpha 不是“crypto 有日内动量”这么泛，而是“固定到某个具体 clock-hour 后，跨币横截面相对强弱会在下一次同一 hour 出现可交易的延续或回摆”。**

翻成人话：
- 不是看“刚过去 1 小时涨了就追”；
- 而是看“每天来到这个小时，这些币在这个 hour slot 里的强弱排序有没有稳定性”；
- 若短 lookback 下这种排序会反着来，就是 **same-hour cross-sectional reversal**；
- 若长 lookback 下这种排序会继续，就是 **same-hour cross-sectional momentum**。

这条线之所以值得留档，是因为它服务的不是单腿趋势判断，而是：
- `cross-sectional / relative-value`
- `market-neutral`
- 可直接变成 `1h parent -> 15m/5m child execution`
- 与近期已经写过的单资产 intraday momentum、winner rotation、pairs cointegration 并不相同。

---

## 2) 从 repo 里，真正该保留什么
`Project.ipynb` 的核心不是花哨模型，而是一条很朴素的横截面构造：

### 2.1 信号怎么造
repo 先把 10 个币的 `1h` 收益率排好，然后对每个 **hour bucket** 分开算：
- 取所有 `index.hour == h` 的样本；
- 对每个币，计算过去 `lookback_days` 个“同一小时”的平均收益；
- 做横截面 rank；
- 再做 demean + 归一化，形成 market-neutral 权重；
- 下一次来到这个小时，用上一个时点的 rank 权重去乘本小时收益。

也就是：
- 短 lookback：测 **同一小时的短期回摆**
- 长 lookback：测 **同一小时的中期延续**

### 2.2 repo 明确写出的三个假设
notebook 里把时段拆成两层：
- `regular hours = 14:00 ~ 21:00`
- `after hours = 00:00 ~ 13:00` 与 `22:00 ~ 23:00`

再按 weekday / weekend 分组，最后给出三条假设：
1. **H1：weekday after-hours 上，1~2 天 lookback 更像 reversal**
2. **H2：weekend regular-hours 上，1~8 天 reversal**
3. **H3：weekday regular-hours 上，9~21 天 momentum**

随后 repo 自己在 out-of-sample 段里写得很清楚：
- **H1 与 H3 被验证**
- **H2 不一致，被放弃**

这点很关键：
> 这不是“全天候都有效”的大而化之信号，而是 **时段条件很重** 的横截面 alpha。

### 2.3 为什么这条线值得 desk 先收进池子
因为它回答的是一个很实盘的问题：

> **如果某种横截面强弱只在固定 hour / fixed weekpart 才出现，那我们不该整天交易，而该在对的时间片才开仓。**

这会直接影响：
- 交易频率
- 成本密度
- child execution 设计
- 是否适合和别的 alpha 共用同一个 admission gate

---

## 3) 本轮最小 public-data portability probe（Binance Spot，近 180 天，`1h`）
### 3.1 数据口径
为了不依赖私有数据，这轮只做最小可复现实验：

- 数据源：Binance Spot public API `api/v3/klines`
- 周期：`1h`
- 样本：最近约 `180d`
- universe：
  - `BTCUSDT`
  - `ETHUSDT`
  - `ADAUSDT`
  - `BNBUSDT`
  - `XRPUSDT`
  - `DOTUSDT`
  - `POLUSDT`
  - `SOLUSDT`
  - `LTCUSDT`
  - `AVAXUSDT`
- 说明：repo 原 notebook 用 `MATICUSDT`，当前 Binance spot 口径已更接近 `POLUSDT`，本轮最小实验做了该替换。
- 产物：
  - `reports/artifacts/quant_digests/2026-04-23_1458_clockhour_weekpart_xs_probe_summary.csv`

我按 repo notebook 的同款逻辑复刻了两条最值得关心的假设：
- **H1：weekday after-hours，1~2 天 lookback reversal**
- **H3：weekday regular-hours，9~21 天 lookback momentum**

### 3.2 关键结果
先给 4 个最有用的数据点：

1. **当前样本里，H3（weekday regular-hours momentum）比 H1 明显更稳**
   - `lookback=18d`：**Sharpe ≈ 1.17**，`mean ≈ +0.477 bps/hour`
   - `lookback=15d`：**Sharpe ≈ 0.88**，`mean ≈ +0.367 bps/hour`
2. **H3 在 12~21 天区间整体都还是正的**
   - `12d`：Sharpe `0.76`
   - `21d`：Sharpe `0.70`
3. **H1（after-hours weekday reversal）在最近 180 天并不强**
   - `1d` lookback：Sharpe `-0.07`
   - `2d` lookback：Sharpe `0.15`
4. **也就是说，repo 里的“短 lookback same-hour reversal”更像条件很脆的旁支；真正更可迁移的，是 weekday regular-hours 的 same-hour cross-sectional continuation。**

翻成人话：
- 这份 repo 最值得我们 desk 先拿走的，**不是“reversal+momentum 都很强”这个大标题**；
- 而是更具体的：
  - **固定时段 + 横截面 + market-neutral + 中等 lookback 的 same-hour momentum**
  - 在新样本里还活着；
  - 而短窗 reversal 这边目前没那么硬。

---

## 4) 这条线为什么不等于“又一篇 intraday momentum”
### 4.1 它不是单资产 time-series momentum
近期已经有：
- BTC session momentum
- 全球 intraday tsmom portability
- hourly winner rotation

这条线与它们不同的地方在于：
- **横截面**：同一时段内做币与币之间的相对强弱，而不是做单腿方向；
- **market-neutral**：rank-demean 后天然更接近 dollar-neutral；
- **时段条件**：不是全天都跑，而是只在指定 hour / weekpart 激活；
- **raw alpha 本体就是 relative-value**，不是拿一个大盘 trend 再做 filter。

### 4.2 它和 pairs/stat-arb 也不一样
虽然都属于 relative value，
但它不是：
- cointegration residual
- spread z-score
- basis/funding convergence

它更像：
> **同一小时的“横截面微风格”在跨天重现。**

所以它对素材池的补充价值在于：
- 给我们一个 **非 pair-specific、非 spread-specific** 的 relative-value 壳；
- 后续既能单独跑，也能和 funding / dispersion / market-quality gate 叠加。

---

## 5) 可直接落地的完整策略壳
### 5.1 Entry（入场）
先做最保守的一版：

1. 以 `1h` 为 parent signal 周期；
2. 只保留 **weekday regular-hours**（先复刻当前 probe 更强的 H3）；
3. 对每个 hour bucket，计算过去 `L=12~18` 天同一小时的平均收益；
4. 横截面 rank 后做 demean / 归一化；
5. 下一次来到同一小时开仓：
   - long 当下 rank 靠前币
   - short 当下 rank 靠后币
   - 组合保持净敞口接近 0

最小实现可先用：
- `top 2 long / bottom 2 short`
- 或直接用连续 rank 权重

### 5.2 Exit（出场）
先从最朴素的 3 套出场做 A/B test：
- **time stop**：持有 `1h`
- **child-exec exit**：虽然父信号按 `1h` 决定，但在下一小时内部拆成 `4 x 15m` 或 `12 x 5m` 均匀减仓
- **intra-hour veto**：若开仓后前 `15m` 就出现横截面 rank 快速反转，则提前减半

### 5.3 Sizing（仓位）
建议先用：
- 横截面 rank 归一化权重
- 再乘 `1 / rolling_vol_24h` 做简单 vol target
- 单币上限 `cap_i`
- 单 hour-bucket 总风险上限 `cap_hour`

### 5.4 Risk（风控）
这条线最该防的不是趋势反向，而是：
- 横截面 leader 过度集中在一个 beta 因子上；
- 周末/美盘外时段的流动性塌缩；
- 大行情新闻下的“统一方向冲击”把 market-neutral 排名逻辑冲烂。

所以至少要加：
- `BTC beta neutralization` 或简单 benchmark hedge 检查
- `dispersion too low / too high` veto
- 低成交额币过滤
- 单币 / 单 sector concentration cap

### 5.5 Cost（成本）
repo 里只是把收益统一乘 `(1 - 0.002)`，相当粗糙；
对我们更现实的 friction ladder 建议是：
- `4 bps round-trip`
- `8 bps round-trip`
- `12 bps round-trip`

因为这条线是 **横截面换仓策略**，真正的问题不是“有没有信号”，而是：
- 是否每次都要全篮子重配；
- 是否能做 partial rebalance；
- child execution 能否把每小时换仓压到 maker-first。

---

## 6) 它和 `15m / 5m` 的关系怎么落地
虽然 repo 信号本身是 `1h`，但它并不脱离我们现在的短周期体系。

### 更合理的 desk 读法
- **`1h` 负责定义 alpha 本体**：当前这个固定 hour 的横截面 continuation 是否成立
- **`15m / 5m` 负责 child execution**：
  - 分批进场
  - 回撤时补仓/取消
  - 做 microstructure veto

### 两条最快可测的 child 版本
1. **15m child TWAP 版**
   - 每到目标 `1h` 的起点开仓；
   - 接下来 `4` 根 `15m` 分批建仓/平仓；
   - 看净滑点能否明显小于整点一次性冲击。

2. **5m confirmation 版**
   - `1h` parent 决定 long/short basket；
   - 只在对应币的首个 `5m` 没出现极端逆向 spike 时执行；
   - 把“hourly rank edge”与“micro pullback entry”拼起来。

所以它不是“只能做 1h 的慢信号”，而是一个很适合给 `15m/5m` 执行层喂单的 parent alpha。

---

## 7) 这轮结论怎么用
### 结论 1：能进 raw alpha 素材池
因为它满足：
- base alpha 清楚；
- market-neutral relative-value 结构清楚；
- 可以独立写出 entry / exit / sizing / risk / cost；
- 不是单纯 filter / regime / overlay。

### 结论 2：当前应优先保留 H3，不要把 H1 也一股脑打包继承
本轮 portability probe 给出的结论非常直接：
- **weekday regular-hours same-hour momentum** 还有可迁移性；
- **after-hours weekday reversal** 当前样本没那么硬。

所以别把 repo 的 reversal/momentum 双主线原样照搬。
先保留：
- `same-hour cross-sectional continuation`
再把 reversal 当成候补旁支。

### 结论 3：这条线最适合和哪些组件拼接
优先考虑：
- market-quality gate
- dispersion gate
- top-liquidity universe gate
- `1h parent -> 15m/5m child exec`

不建议第一版就叠太多复杂 ML 特征，先确认最朴素的 hour-bucket edge 有没有穿过成本。

---

## 8) 下一步怎么测
按优先级给一个最小实验序列：

### A. 先做 parent alpha 真伪确认
在 Binance USDⓈ-M liquid majors 上复刻：
- universe：`BTC/ETH/SOL/XRP/BNB/DOGE/ADA/LTC/AVAX/DOT`
- bar：`1h`
- signal bucket：
  - `weekday regular-hours`
  - `L = 12, 15, 18, 21 days`
- 组合：`top2-bottom2` 与 `continuous-rank` 两版并行
- 成本：`4/8/12 bps round-trip`

### B. 再测 15m child execution
同一套 `1h` parent signal，比较：
- 整点一次性成交
- `4 x 15m` 均匀拆单
- `5m` 首段 veto + 剩余分批成交

核心看：
- edge 保留率
- realized turnover
- net alpha after cost

### C. 最后才把 bucket 从 24 个小时压到 96 个 `15m` 时段
如果 `1h` parent 过线，再测：
- 是否存在更细的 `quarter-hour-of-day` 横截面效应；
- 以及这些更细 bucket 是否稳定，还是只是噪声放大器。

我的建议很明确：
> **先别急着把这条线直接压成纯 `5m` alpha；先把它当成“有时段条件的横截面 parent signal”，再让 `15m/5m` 去负责执行优化。**

---

## 9) 一句话结论
如果只保留一件事：

> **这份 repo 真正值得 desk 继续测的，不是泛泛的 intraday momentum，而是“weekday regular-hours 的 same-hour cross-sectional continuation”这条 market-neutral raw alpha；它和 pairs/basis/funding 都不是一回事，而且天然适合接到 `15m/5m` child execution 层。**
