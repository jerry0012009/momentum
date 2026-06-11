# 别把这份 2026 新 repo 只读成相关性看板：对 short-cycle desk，更该先测的是「correlation-first pair admission × ratio z-score spread fade」这条 raw alpha
- 时间：2026-04-16 07:18 UTC
- 类型：GitHub / repo source audit + public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：相关性足够高的两腿，其价格比（A/B）出现统计极端偏离后，会向均值回归（做空贵腿、做多便宜腿）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（可先落 baseline）
- 主题标签：pairs / stat-arb / relative-value / mean-reversion / correlation-admission / zscore / binance-perpetual / 5m / 15m
- 证据类型：工程经验 + public-data fast probe

**先回答 base alpha：**这篇东西的 base alpha 不是“相关性本身”，而是**通过相关性先筛 pair，再交易 ratio 的极端偏离回归**。

## 1) 这次看了什么
看了 2026 新仓库 `ApexQuant-Dev/binance-correlation-stat-arb`（`README.md`、`correlation_bot.py`、`phase1_data_fetch_correlation.py`）。仓库给的是一个很轻量但清晰的骨架：
- `5m` 相关性矩阵做 admission（默认阈值 `corr>=0.7`）
- ratio z-score 触发（`|z|>2`）
- 方向是典型 spread mean reversion（short rich leg / long cheap leg）

## 2) 核心结论
- 这是**可独立复现的 raw alpha 候选**，而且可以直接写成完整 baseline（entry/exit/sizing/risk/cost 都能定义）。
- 我用 Binance USDⓈ-M 公共 `5m` 数据（`2026-03-15~2026-04-16`，`BTC/ETH`、`SOL/AVAX`、`ARB/OP`）做了 portability probe：共 `371` 笔。组合层面平均 gross 仅 `+0.77 bps/笔`，成本后明显不过线。
- 成本梯度结果：
  - `2 bps` roundtrip（双腿合计）下，平均 net `-1.23 bps/笔`，累计约 `-4.47%`
  - `8 bps` 下，平均 net `-7.23 bps/笔`，累计约 `-23.53%`
- 但有 pocket：`SOL/AVAX` 在 `8bps` 下接近打平（gross `+7.33 bps/笔`，net `-0.67 bps/笔`，累计 `-0.81%`），说明这条线更像“**pair-admission + execution 依赖型**”而不是天然失效。

## 3) 为什么和当前项目有关
这条线直接扩充了 desk 的 **pairs / stat-arb raw alpha 素材池**，且结构简单、可快测：
- 先做相关性 admission（减少瞎配对）
- 再做 spread/zscore 反转（alpha 本体）
- 最后在执行层决定它能不能活（maker/taker、滑点、时段）

对 `1m/3m/5m/15m` 的关系：
- alpha 本体更像 `5m/15m`；
- `1m/3m` 更适合做执行细化（入场挂单、短超时止损、腿间滑点控制）。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / 均值回复（market-neutral）
- 基础 alpha：ratio z-score extreme → spread mean reversion
- regime：rolling corr 必须达标（如 `corr>=0.7`）
- filter / veto：波动过高、盘口过薄、腿间滑点超阈值时 veto
- risk / sizing / execution overlay：双腿名义对冲、单笔风险上限、max-hold 超时离场、成本门槛（至少要覆盖双腿 roundtrip）

## 4) 可复刻的最小实验（下一步怎么测）
**假设：**相关性 admission 能提升 zscore spread fade 的费后生存率。  
**定义：**
1. `pair` 仅在 rolling `corr>=0.7` 可交易；
2. `z = (ratio-mean)/std`，`z>2` 做 `short A/long B`，`z<-2` 反向；
3. `z` 回到 `0` 或 `24 bars` 超时离场；
4. 成本先测 `2/4/8 bps` 梯度。

**最小回测切口：**Binance USDⓈ-M，`5m` 主测 + `15m` 稳健性，先用 `BTC/ETH`、`SOL/AVAX`、`ARB/OP`。  
**先看 2 个指标：**`net bps/笔` + `cost ladder break-even`。若都不过线，优先优化 execution 而不是继续堆信号。

## 5) 风险与保留意见
- 当前 repo 交易层还偏“信号演示”，并未给完整成交/滑点/资金容量建模。
- 相关性不是协整，可能出现“高相关但不可回复”的结构性漂移。
- 本轮 probe 已显示：在 taker 口径下，edge 大概率被成本吃掉；要活下来几乎必需更严 pair admission + 更低摩擦执行。

## 6) 产物与来源
### 本轮产物
- Probe 脚本：`reports/artifacts/quant_digests/2026-04-16_correlation_zscore_pairs_probe.py`
- 明细交易：`reports/artifacts/quant_digests/2026-04-16_correlation_zscore_pairs_probe_trades.csv`
- 汇总：`reports/artifacts/quant_digests/2026-04-16_correlation_zscore_pairs_probe_summary.json`

### 来源
1. **ApexQuant-Dev. (2026). Binance Correlation & Stat-Arb Suite. (GitHub Repository).**  
   - Repo URL: `https://github.com/ApexQuant-Dev/binance-correlation-stat-arb`  
   - Readable URL: `https://github.com/ApexQuant-Dev/binance-correlation-stat-arb`
2. **Gatev, E., Goetzmann, W. N., & Rouwenhorst, K. G. (2006). Pairs Trading: Performance of a Relative-Value Arbitrage Rule. Review of Financial Studies.**  
   - DOI: `10.1093/rfs/hhj020`  
   - Readable URL: `https://doi.org/10.1093/rfs/hhj020`
3. **Avellaneda, M., & Lee, J.-H. (2010). Statistical arbitrage in the US equities market. Quantitative Finance.**  
   - DOI: `10.1080/14697680903124632`  
   - Readable URL: `https://doi.org/10.1080/14697680903124632`
