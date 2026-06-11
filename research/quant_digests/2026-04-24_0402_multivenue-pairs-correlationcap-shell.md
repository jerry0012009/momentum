# 别把这个 32-venue stat-arb 大仓只读成“又一个 pairs 大杂烩”：对 short-cycle crypto desk，更该先拆的是「cointegration spread fade × sector/correlation-cap allocator」这条完整 raw alpha 壳
- 时间：2026-04-24 04:02 UTC
- 类型：GitHub
- 主题类型：raw alpha
- 基础 alpha：先筛出联动稳定、可 cointegrate 的 altcoin pair，构造 `spread = y - βx`；当 spread 的 z-score 偏离过大时做均值回归，回到中枢附近平仓。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / pairs / stat-arb / relative-value / cointegration / zscore / sector-neutral / concentration-cap / walk-forward / crypto / 15m / 5m
- 证据类型：repo source + repo 回测结论

## 1. 这次看了什么
看了 2026 GitHub 仓 `abailey81/Crypto-Statistical-Arbitrage`。它表面上像“32 个 venue 的大而全系统”，但对我们最有价值的，不是它把 CEX/DEX/API 全接满，而是它把 **altcoin pairs raw alpha + 风险分配器** 写成了一条比较完整的可部署骨架。

## 2. base alpha 先说清楚
这篇东西的 **base alpha 是清楚的**：

**找 cointegrated pair，做 spread z-score fade。**

也就是：不是赌单边涨跌，而是赌两条本该一起动的相对价格关系会回归。这个本体属于典型的 `relative value / stat-arb / mean reversion` raw alpha，不是纯 filter。

## 3. 核心结论
- 这份仓最值得 desk 拿走的，不是“32 venues” 这层包装，而是 **pairs raw alpha 的完整闭环**：universe、cointegration admission、entry/exit/stop、成本、walk-forward、风险限额都给了。
- README 里给出的 phase-2 关键结果是：**Altcoin StatArb Sharpe 1.61、总收益 6.84%、最大回撤 4.64%、共 127 笔交易**；至少说明作者不是只给概念图，而是把它写成了完整回测壳。
- 对 short-cycle desk 更有价值的旁支，不是再往信号里硬塞 ML，而是它明确加了 **40% sector concentration cap + 70% max cross-pair correlation cap + Kelly 0.25~0.5x sizing**。这说明作者也承认：pairs 最大风险常常不是单 pair 没有 edge，而是多个 pair 同时其实押了同一件事。
- 所以这份材料最适合我们的读法是：**保留最朴素的 cointegration spread fade 作为 raw alpha，本轮优先吸收的是“别把多个 pair 当独立 alpha”的 allocator 思路。**

## 4. 为什么和当前 desk 直接相关
bot7 当前最该补的是 **可独立复现、可落地的 raw alpha 素材池**。这份材料符合，因为它能清楚拆成：
- alpha 本体：cointegration spread fade
- regime / admission：先做 pair 筛选，再交易
- filter / veto：DEX/CEX 分层、不同 z-score 阈值、相关性上限
- risk / sizing：Kelly 缩放、sector cap、max positions
- cost：CEX round-trip 约 0.20%，DEX all-in 约 0.50%~1.50%

这比“只会说配对交易可能有效”的材料高一个层级，因为它已经给了完整策略骨架。

## 5. 策略拆解（必填）
- 方向属性：相对价值 / stat-arb / 均值回归
- 基础 alpha：cointegration spread z-score fade
- regime：walk-forward pair admission；只交易通过 cointegration 检验的 pair
- filter / veto：sector concentration cap、cross-pair correlation cap、venue tier 分层、不同市场使用不同 entry/stop z-score
- risk / sizing / execution overlay：Kelly 0.25~0.5x、max positions 5~8（CEX）/ 2~3（DEX）、transaction-cost-aware entry

## 6. 可复刻的最小实验
- 研究假设：**在 Binance liquid alt universe 上，单个 pair 的 spread fade 也许不稀缺；真正更值钱的是“只拿少数低相关 pair 同时上场”，组合层能不能比 pair 平铺更稳。**
- 最小定义：
  1. 选 `SOL/ADA/XRP/LINK/DOGE/AVAX/BNB/ETH` 之类 liquid majors / liquid alts；
  2. 每周做一次 Engle-Granger admission；
  3. 对通过的 pair 计算 rolling spread z-score；
  4. `|z| > 2` 入场，`|z| < 0.5` 出场，`|z| > 3` 止损；
  5. 同时只保留 **相关性最低的前 2~3 个 active pair**，与“见信号就全上”做对照。
- 最小回测切口：Binance USDⓈ-M 或 spot，`15m` 主信号，`5m` child exit，近 `90~180d`。
- 最该先看：
  - 成本后组合 Sharpe / maxDD
  - `active pairs` 之间的 realized correlation 有没有明显下降

## 7. 下一步怎么测
1. **先禁用 repo 里的 ML enhancement**，只留最朴素的 cointegration + zscore 壳。
2. 做两版对照：
   - A：所有通过 admission 的 pair 都上
   - B：只上低相关前 `N=2~3` 个 pair，并加 40% sector cap
3. 统一按 `2 / 4 / 6 bps` friction ladder 重跑，先看是不是组合层比信号层更值得救。
4. 若 `15m` 组合层改善明显，再用 `5m` 只做 child execution / early exit，不要把 pair admission 也推到太高频。

## 8. 风险与保留意见
- 这份 repo 很强的地方是“结构完整”，不是“每个指标都已被我们独立验证”。README 里的 Sharpe/收益要当作 **作者口径**，不能直接当 desk 已验证事实。
- 仓里把 ML、32 venues、32 万数据源都堆进来了，容易让人误以为 edge 来自复杂度；但更可能真正值钱的，是 simpler shell + better allocator。
- 对我们当前 desk，DEX 部分和超多 venue 接入都不是第一优先；优先级更高的是：**同一套 pair alpha 在 short-cycle 上，组合相关性约束到底能不能把回撤和假分散压下来。**

## 9. 一句话总结
**这份仓最该学的不是“把 pairs 做得更花”，而是承认 pairs 组合里最危险的问题往往是隐藏的同向拥挤；所以更适合 desk 的 intake 是：保留 cointegration spread fade 这条 raw alpha，同时先验证 correlation-cap allocator 值不值。**

## 10. 来源
- Author / Year / Title / Venue
  - Andrew Bailey. (2026). *Crypto Statistical Arbitrage*. GitHub repository.
  - DOI：N/A
  - Readable URL：https://github.com/abailey81/Crypto-Statistical-Arbitrage
  - Repo URL：https://github.com/abailey81/Crypto-Statistical-Arbitrage
- Key source used
  - README（phase-2 altcoin statistical arbitrage, risk controls, walk-forward summary）
  - Raw README URL：https://raw.githubusercontent.com/abailey81/Crypto-Statistical-Arbitrage/main/README.md
