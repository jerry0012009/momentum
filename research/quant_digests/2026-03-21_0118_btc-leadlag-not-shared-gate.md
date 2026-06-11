# 别把“BTC 先动同向”直接升成 15m 三线 shared gate：completed-bar lead-lag 只留下 **11.5%** 交易，且失败率更高
- 时间：2026-03-21 01:18 UTC
- 类型：论文 + 本地 clean replication
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/crossmarket/intraday/lead-lag/btc/eth/sol/filter/paper/crypto/15m
- 证据类型：论文机制启发 + 本地最小 clean replication

## 1) 这次为什么值得先写
这轮继续服务三条收口线，而且比再塞一个新 gate 更值钱：
**我们需要尽快知道，“BTC 先动、山寨后跟”这种很诱人的跨市场直觉，到底值不值得升成 `breakout-short / Fib / EMA-PSAR` 的 shared 放行键。**

如果它只是听起来合理、实测却靠缩样本才勉强变好，就应该尽早 park，别继续占 desk 预算。

## 2) 看的来源
### Source A（主）
- **Dezhong Xu, Bin Li, Tarlok Singh, Jinze Li (2023). _Cross-Market Intraday Time-Series Momentum_. SSRN working paper.**
- DOI: `10.2139/ssrn.4651331`
- Readable URL: `https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4651331`
- Repo URL: `N/A`

这篇 paper 最值得偷的不是“直接照抄一套 intraday alpha”，而是：
**把 leader market 的已完成短窗走势，当成 follower 市场的 cheap context / gate。**

### Source B（公开数据）
- **Binance Developers. USDⓈ-M Futures Kline/Candlestick Data.**
- Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`
- Repo URL: `N/A`

## 3) desk 版一句话结论
- **一句话核心结论：** 对当前 15m desk，`BTC 同向 completed-bar lead-lag` 不适合直接升成三条线 shared gate；它把交易数砍得太狠，而且失败率更差。  
- **一句话证明方式：** 冻结既有 entry，只给 `ETH/SOL` 信号叠一层 `BTC 过去 4/8 根 15m completed bars 同向领先 + impulse z-score` gate；结果 pooled 样本只剩 **11.5%**，虽然收益表面微升，但 failure 明显恶化、跨资产也不稳定。

## 4) 最关键的数据点
### 4.1 pooled 总表（6 bps / side）
- baseline：`217` 笔，成本后收益约 `0.00%`
- 加 gate 后：`25` 笔，成本后收益约 `+0.08%`
- **trade_count_retention = 11.52%**
- failure rate：`49.77% -> 60.00%`（**+10.23pct**）

翻成人话：
**它不是把错单筛掉了，而更像把大多数单都砍掉后，留下一个极小子样本，顺手把失败率也搞差了。**

### 4.2 分资产：广度不够
- **ETH**：`104 -> 13` 笔，return delta `-0.29%`，failure `+11.54pct`
- **SOL**：`113 -> 12` 笔，return delta `+0.50%`，failure `+8.78pct`

也就是说，改善几乎只剩 **SOL 偶然性**，ETH 并没有跟着一起变好，达不到 shared gate 该有的 breadth。

### 4.3 分 setup：Fib / EMA 几乎被砍没
- ETH `fib_retest_long`: `2 -> 0`
- ETH `ema_psar_long`: `12 -> 0`
- SOL `fib_retest_long`: `1 -> 0`
- SOL `ema_psar_long`: `11 -> 1`

这条最关键：
**如果一个 gate 还没证明自己真有 edge，就先把 Fib / EMA 侧样本几乎清空，它就不该进 shared queue。**

## 5) 为什么它对三条收口线是“负面但有价值”的结论
这不是偏题，反而是很好的收口工作：
- 对 **`V3 breakout-short follow-up`**：说明“BTC 已先跌”不能粗暴当 short 放行键；更可能需要的是更细的 `nonlinear lead-impulse band`，而不是 yes/no 同向过滤。
- 对 **`Fibonacci confirmation / retest_hold`**：当前口径下几乎直接被砍没，说明它不该偷渡成 long-side shared context。
- 对 **`EMA / PSAR raw alpha focus`**：raw alpha 本来就脆，这种会极端压缩样本的 gate 只会让角色更混乱，不像 honest overlay。

所以这轮最大的价值不是“找到了更强 gate”，而是：
**尽快排除一个很诱人、但不够稳的 shared 候选。**

## 6) 下一步怎么测（别原地重复）
不要继续测同一个 blunt gate；如果要复活这条线，只允许走更窄的下一步：

### 实验 A（优先）
只保留在 `breakout_short` 上，比较：
- `A = no cross-market gate`
- `B = same-direction blunt gate`（本轮已知大概率失败）
- `C = nonlinear band gate`：把 BTC 领先冲击分成 `low / mid / high` 三档，只 veto 极端档，不做全有全无封杀

### 实验 B
只在 `SOL breakout_short` 上做一次最小复核：
看 `+0.50%` return delta` 是否只是 12 笔子样本噪音。

### 第一优先指标
- `post_cost_expectancy`
- `failure_delta`
- `trade_count_retention`
- `cross_asset_breadth`

如果不能同时守住 **failure** 和 **breadth**，这条线就继续 park，不再抢三条主线预算。

## 7) 风险与保留意见
- 当前是 **最小 clean replication**，不是完整 walk-forward；
- leader 只用了 `BTC`，没测 `ETH -> SOL` 等其他 leader 结构；
- 当前 gate 太硬（同向 + completed-bar），本身就可能过度稀疏；
- 但也正因如此，这轮结论很明确：**至少这种最便宜、最直觉的 shared 版本，不值得继续升。**

## 8) 本轮产物
- 研究笔记：`research/quant_digests/2026-03-21_0118_btc-leadlag-not-shared-gate.md`
- clean replication artifact：`reports/artifacts/scout_rank134_cross_market_intraday_tsmom_leadlag_15m/`
- 关键文件：
  - `overall_summary.csv`
  - `asset_summary.csv`
  - `setup_summary.csv`
  - `cost_summary.csv`
  - `scout_promotion_scorecard.csv`

## 9) 来源
1. **Xu, D., Li, B., Singh, T., & Li, J. (2023). _Cross-Market Intraday Time-Series Momentum_. SSRN Working Paper.**
   - DOI: `10.2139/ssrn.4651331`
   - Readable URL: `https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4651331`
   - Repo URL: `N/A`
2. **Binance Developers. USDⓈ-M Futures Market Data API.**
   - Title: `Kline/Candlestick Data`
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`
   - Repo URL: `N/A`

---
一句话收口：

**“BTC 先动、山寨再跟”这件事可以继续当研究灵感，但在当前 15m desk 上，它还不配直接升成 breakout-short / Fib / EMA-PSAR 的 shared 放行键。**
