# 别把横截面 alpha 继续写成单特征排序：这篇 2025 论文更值得先测的是「24h loser × 高波动 bucket」交互式 raw alpha
- 时间：2026-03-25 13:23 UTC
- 类型：2025 论文（摘要级证据）+ Binance Futures 公共 15m K 线最小快检
- 主题类型：raw alpha
- 基础 alpha：过去 24h 的横截面输家，在过去 24h 已经显著放大波动的币篮子里，更像短周期过度反应；因此应做 `high-RV bucket 内 long losers / short winners`，而不是把 `last-day return` 单独当全市场统一信号
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/mean-reversion/interaction-effects/double-sort/high-volatility/loser-basket/relative-value/binance/perpetual/15m/1h/4h/paper
- 证据类型：论文摘要级证据 + 本地公共数据快检

> 先回答 base alpha：**不是 shared filter，也不是纯解释。base alpha 就是“过去收益 × 风险状态”的交互式横截面反转——对 desk 来说，当前最值得先做的不是全市场 loser basket，而是 `高 24h realized-vol bucket` 里的 loser-vs-winner 相对值腿。**

## 1. 这次看了什么
主线材料是：
- **Aleksander Mercik, Barbara Będowska-Sójka, Sitara Karim, Adam Zaremba (2025), _Cross-sectional interactions in cryptocurrency returns_, International Review of Financial Analysis**

这篇论文最有价值的地方，不是再告诉我们“某个单一特征能预测收益”，而是明确把问题改写成：

**crypto 横截面里，alpha 很可能不是单变量，而是“特征 × 特征”的 interaction。**

摘要已经给得很明确：
- 作者对 **40 个特征** 做 **double-sorted portfolios**
- 样本覆盖 **500+ major coins and tokens（2017–2023）**
- 最强 interaction 主要来自 **liquidity / risk / past return** 的组合
- 选 top / bottom interactions 的 OOS long-short 策略，**Sharpe 超过 1**

对我们 desk，我不想把它写成“再做一个大而全的多特征工厂”。更值得先偷的一条，是最容易映射到 `15m / 1h / 4h` 的那条腿：

**先把 `past-24h return × past-24h realized-volatility` 做成双排序，测试高波动 bucket 内的 loser-basket reversal。**

## 2) 核心结论
- **一句话核心结论：** 这篇 2025 论文最该给我们的不是“更多特征”，而是“不要再做单特征排序”；对当前 desk，最值得先落地的交互式 raw alpha，是 **`24h loser × 高波动 bucket` 的横截面反转**。
- **一句话证明方式：** 论文摘要显示交互项里最强的一组正是 `risk / liquidity / past return`；我再用 Binance 永续公开 `15m` 数据做最小快检，发现 **高 24h realized-vol bucket 内做 loser-vs-winner** 的相对值腿显著强于低波动 bucket，而且在 `4h hold` 上比 `1h hold` 更像完整策略骨架。

3 个关键数据点：
1. **论文摘要级原始发现**：在 **500+** 个 major coins / tokens、**2017–2023** 样本上，基于 **40 个特征** 的双排序 interaction 里，最强组合来自 **liquidity / risk / past return**；作者报告 **OOS long-short Sharpe > 1**。
2. **本地快检（12 个高流动性 Binance USDⓈ-M 永续，近 90 天，15m bars）**：在 `高 24h realized-vol` bucket 内做 `long bottom-third past-24h losers / short top-third winners`，**1h hold、15m rebalance** 的平均毛收益约 **+2.31 bps / rebalance**，毛 Sharpe 约 **8.87**，胜率约 **53.63%**；对照组 **低波动 bucket** 同口径约 **-0.18 bps**。
3. **持有窗 sweep**：同一条 `high-RV loser reversal` 腿在 **4h hold、1h rebalance** 下平均毛收益约 **+7.99 bps / rebalance**，毛 Sharpe 约 **8.00**，胜率约 **55.30%**；说明这条线更像“需要给一点扩散时间”的交互式反转，而不是必须 bar-by-bar 追的极短线信号。

## 3) 为什么和当前 desk 直接相关
- 这是 **raw alpha**，不是解释层，也不是共享 gate。
- 它补的是我们当前更该继续扩充的方向：**cross-sectional / relative-value / mean-reversion**，而不是又回到单资产 breakout 内循环。
- 它比“全市场 loser basket”更 desk-friendly，因为 interaction 把 universe 先切成了更有信息密度的 pocket：
  - `past return` 决定谁是过度反应候选
  - `realized vol` 决定哪里更像“刚发生挤压 / 恐慌 / unwind”
- 更重要的是，这条线天然能拆成完整策略：
  - ranking
  - bucket selection
  - rebalance cadence
  - hold horizon
  - cost / veto

## 3.5) 策略拆解（必填）
- 方向属性：cross-sectional / relative-value / mean-reversion
- 基础 alpha：高波动状态下，过去 24h 横截面输家更容易出现短期反弹，过去 24h 横截面赢家更容易回吐
- entry：
  - 每个 `15m` bar 计算可交易 universe 的：
    - `past_24h_return`
    - `rv_24h`（24h realized volatility）
  - 先按 `rv_24h` 横截面分 bucket，选 **top tercile 高波动 bucket**
  - 在该 bucket 内，再按 `past_24h_return` 分 tercile：
    - `long bottom-third losers`
    - `short top-third winners`
- exit：
  - 第一版优先测 **4h 固定持有**
  - 对照测 `1h / 2h`，看 alpha 是否只是极短暂冲击回补
- sizing：
  - 先做等权 long-short
  - 第二版改成 `inverse-vol within bucket` + 单币 notional cap
- risk / veto：
  - 只保留高流动性、老币、可做空的 perp
  - 排除新上币 / 极端 funding / 异常 OI spikes
  - 单币仓位上限 + 单 sector 集中度上限
- cost：
  - 必须显式计入 `fee + spread + slippage`
  - 这条腿在 `1h hold` 仅有 **~2.3 bps** 毛边，bar-by-bar taker 版大概率不够
  - `4h hold` 的 break-even 更接近 **~8 bps round-trip**，才有继续优化执行的意义

## 4) 这条线最该怎么读：不是“论文说 interaction 很重要”，而是“先偷一条最短路径可复现的 interaction alpha”
如果机械照抄论文 headline，很容易把任务写成：
- “把 40 个特征两两组合都跑一遍”

这对 desk 现在没必要，也太慢。

更值得做的是：
1. **承认论文真正的新意在 interaction，而不在单一特征本身**
2. **先挑一个最短路径 interaction**：`past return × realized vol`
3. **再把它 desk 化成最小双排序策略**

换句话说：
**这轮最值钱的不是“interaction exists”，而是“哪条 interaction 最快能在 15m/1h/4h 变成可执行策略骨架”。**

我当前给出的答案是：
**先测 `high-RV loser reversal`，而不是再做一轮全市场统一 loser basket。**

## 5) 可复刻的最小实验（15m 起步）
**数据源与公开性**：
- 数据源：Binance USDⓈ-M Futures Klines
- 公开性：公开可得，无需 API key
- 更新频率：`1m / 3m / 5m / 15m` 均可

**本地最小快检口径**：
- universe：`BTC/ETH/SOL/XRP/BNB/DOGE/ADA/LINK/AVAX/LTC/BCH/TRX`
- bar：`15m`
- feature window：`24h = 96 bars`
- bucket-1：按 `rv_24h` 做横截面 tercile
- bucket-2：在选中 bucket 内按 `past_24h_return` 再做 tercile
- signal：`long losers / short winners`
- hold：`1h / 2h / 4h`
- rebalance：`15m` 与 `1h` 都测

**当前最该先看的 5 个指标**：
1. `avg gross/net bps per rebalance`
2. `break-even round-trip cost`
3. `hit rate`
4. `turnover`
5. `bucket stability`（换 universe / 删去低流动性币后还在不在）

## 6) 下一步怎么测（直接可执行）
1. **把 RV bucket 做得更诚实**：从简单 `24h realized vol` 升级成 `realized vol + spread + listing-age` 联合筛选，避免把“高波动但不可交易”的垃圾波动也混进来。
2. **把持有窗做完整 cost curve**：重点比较 `1h / 2h / 4h / 8h`，确认这条 edge 的最佳区间到底是在“反射性回补”还是“半天内 unwinding”。
3. **把 rebalance 从 15m 降到 1h**：这轮快检已经提示，alpha 不是非得 bar-by-bar 追；下一步该正面测试“更慢调仓 + 更长持有”能否显著改善净值后的成本生存线。
4. **把 interaction 扩成 2×2 矩阵**：在 `高/低 RV` 之外，再叠一层 `高/低 ADV`，确认最佳 pocket 是：
   - 高 RV + 高 ADV
   - 高 RV + 低 ADV
   - 还是只在“高 RV 且仍可交易”这一块成立。
5. **做执行版实验**：信号仍在 `15m` 生成，但实际执行切到 `5m / 3m / 1m`，比较 `bar-close taker`、`TWAP slice`、`maker-lean` 三种方式，看 `4h hold` 这条腿能不能从毛边变成净边。

## 7) 风险与保留意见
- 论文这轮拿到的是 **摘要级证据**，不是全文复现；因此我只把它当高信号 intake，而不是已确认参数模板。
- 论文说的是“大 interaction pool 的 OOS 结果”，我这里选的是 **一个 desk-friendly side branch**，不能假装等于作者主实验。
- 本地快检只用了 **12 个高流动性 perp**，不是论文级 `500+` universe。
- 当前结果仍是**毛收益**视角；若执行上被 taker 手续费和 spread 吞掉，这条腿就需要转成更慢 rebalance 或 maker 优先的执行版本。
- `high-RV` 口袋也更容易混入新闻驱动币；没有 event veto 时，回撤可能会比均值看起来大得多。

## 8) 来源
1. **Mercik, A., Będowska-Sójka, B., Karim, S., & Zaremba, A. (2025). _Cross-sectional interactions in cryptocurrency returns_. International Review of Financial Analysis, 97, 103809.**
   - DOI: `10.1016/j.irfa.2024.103809`
   - Readable URL: `https://doi.org/10.1016/j.irfa.2024.103809`
   - Abstract / metadata URL: `https://ideas.repec.org/a/eee/finana/v97y2025ics1057521924007415.html`
   - Repo URL: `未见作者官方开源代码`
2. **Binance Developers. USDⓈ-M Futures Kline/Candlestick Data.**
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

## 9) 本地产物
- `reports/artifacts/quant_digests/cross_sectional_interactions_20260325/interaction_quickcheck_summary.csv`
- `reports/artifacts/quant_digests/cross_sectional_interactions_20260325/interaction_quickcheck_timeseries.csv`
- `reports/artifacts/quant_digests/cross_sectional_interactions_20260325/high_rv_hold_sweep.csv`
- `reports/artifacts/quant_digests/cross_sectional_interactions_20260325/interaction_quickcheck_meta.json`
