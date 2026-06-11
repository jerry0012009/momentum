# 别把“小时内极端上冲”直接当 no-chase：在 15m `EMA reclaim` 场景里，`MAX(5m)` 更像 continuation-confirmation 分层
- 时间：2026-03-20 19:08 UTC
- 类型：论文 + 本地公共数据代理快检
- 主题标签：fibonacci/retest-hold/ema/psar/raw-alpha/intraday/max-impulse/continuation-confirmation/cost-survival/filter/paper/crypto/5m/15m
- 证据类型：论文摘要证据 + 本地 5m/15m 事件代理快检

## 1. 这次看了什么
这轮选了近 5 年论文：**Yadav (2025), _Intraday lottery demands in cryptocurrency market_**。  
论文 headline 是“MAX 效应（极端收益偏好）与后续收益关系”，但这次不照搬其 cross-sectional 主结论，而是抽一个更贴近当前 desk 三条收口线的旁支：

- 对我们的 `Fib retest_hold / EMA reclaim`，`小时内 5m 极端上冲` 应该被当成 **entry veto** 还是 **continuation-confirmation 分层**？

我用本地公开行情缓存（BTC/ETH/SOL perpetual, 5m+15m）做了最小可复现实验，重点看 15m 的 `EMA reclaim long proxy`。

## 2. 核心结论
- **一句话核心结论：** 在 15m `EMA reclaim` 条件下，`MAX(5m, 1h)` 更像 **确认分层**（high better than low），不是默认 no-chase 否决键。  
- **一句话证明方式：** 对 `EMA reclaim` 事件按 `1h MAX(5m return)` 分桶后，比较 next-4-bar 成本后收益/胜率，`high` 桶显著优于 `low` 桶。

关键数据点（本地代理快检）：
1. **样本量**：BTC/ETH/SOL 合计 `65,044` 个 `EMA reclaim long proxy` 事件。  
2. **分三分位（成本后，12 bps round-trip）**：
   - `low`: `-12.96 bps`，胜率 `28.68%`
   - `mid`: `-12.24 bps`，胜率 `35.66%`
   - `high`: `-7.39 bps`，胜率 `41.20%`
   => `high - low = +5.57 bps`（质量分层成立）。
3. **top10% MAX vs 其余（毛收益）**：
   - `top10`: `+11.78 bps`
   - `rest90`: `-0.05 bps`
   但扣 12 bps 后 `top10` 仅 `-0.22 bps`，说明 **成本仍是 EMA/PSAR raw alpha 的主瓶颈**。

## 3. 为什么和三条收口线直接相关
- **Fibonacci confirmation / retest_hold**：可把 `MAX(1h)` 作为“确认强度分层”，优先保留 high-tier 的回踩重启。  
- **EMA / PSAR raw alpha focus**：这条结果直接指向“不是先否决 high impulse，而是先做成本/执行优化”，否则 raw edge 被费用吃掉。  
- **V3 final-verdict / breakout-short follow-up**：当 long-side reclaim 同时出现 high MAX，上行延续质量更高；short follow-up 不宜逆着这类状态硬追。

## 4. 最值得复用/复现的点
1. 把 `MAX(5m, 1h)` 放进 **confirmation tier**（A/B/C 分层），不要先做单阈值 veto。  
2. 分开评估 `gross edge` 与 `net edge`：先看是否有方向信息，再看成本是否允许实盘保留。  
3. 对三条线统一采用“同一状态读数，不同执行映射”：
   - Fib/EMA：作为 confirmation strengthening；
   - breakout-short：作为 short-side follow-up 降权/否决上下文。

## 5. 最小可复现实验口径（公开数据）
- **数据源**：Binance perpetual K 线（公开可得）
- **公开性**：公开 API 可获取（无需私有交易账户）
- **更新频率**：5m 与 15m
- **本轮实验口径**：
  - 标的：`BTCUSDT / ETHUSDT / SOLUSDT` perpetual
  - 周期：15m 信号层 + 5m 冲击度量层
  - 事件：`EMA reclaim long proxy`（`EMA20>EMA50`、回踩 EMA20 附近、阳线收复）
  - 特征：`MAX(5m return)` over last 1h
  - 执行：next-bar open 进，持有 4 根 15m
  - 成本：`6 bps/side`（round-trip 12 bps）

## 6. 下一步怎么测（必须项）
### 假设
`MAX(1h)` 在 Fib/EMA 上更像 continuation-confirmation tier，而非统一 no-chase veto；但 raw alpha 是否存活取决于成本与执行。

### 第一轮（当天可跑）
对 `Fib retest_hold long` 与 `EMA reclaim long` 同时跑 3 臂：
1. `baseline`（不加 MAX）
2. `max_high_only`（仅 top 30%）
3. `max_low_mid_only`（去掉 top 30%）

统一比较：`post-cost expectancy / win-rate / turnover-retention`。

### 第二轮（执行层）
在第一轮胜者上增加 5m 执行优化：
- maker-first（限价 1~2 根）+ timeout IOC
- 成本情景：`4 / 6 / 8 / 10 bps per side`

目标：验证 `gross edge` 能否在 realistic fee/slippage 下转成 `net positive`。

## 7. 风险与保留意见
- 论文主结论是 cross-sectional 资产定价语境，不是直接的单资产逐笔交易规则；本轮是 desk 语境再映射。  
- 本地实验是代理事件，不等价于完整策略；未包含资金管理与组合冲突。  
- 结果显示信号强弱有分层，但成本后边际很薄，不能直接当可部署结论。

## 8. 来源
1. **Yadav, M. (2025). _Intraday lottery demands in cryptocurrency market_. Studies in Economics and Finance, 42(4), 799–835.**  
   - Authors: Manisha Yadav  
   - Year: 2025  
   - Title: Intraday lottery demands in cryptocurrency market  
   - Venue: Studies in Economics and Finance  
   - DOI: `10.1108/SEF-07-2024-0461`  
   - Readable URL: `https://doi.org/10.1108/SEF-07-2024-0461`  
   - Repo URL: `N/A (paper)`

2. **Crossref Metadata (for bibliographic verification).**  
   - Authors: Crossref (metadata provider)  
   - Year: 2025 record indexed  
   - Title: Work record for DOI `10.1108/SEF-07-2024-0461`  
   - Venue: Crossref API  
   - DOI: `10.1108/SEF-07-2024-0461`  
   - Readable URL: `https://api.crossref.org/works/10.1108/sef-07-2024-0461`  
   - Repo URL: `N/A`

---
快检文件：
- `reports/artifacts/literature/intraday_lottery_max_ema_reclaim_asset_summary_2026-03-20.csv`
- `reports/artifacts/literature/intraday_lottery_max_ema_reclaim_bucket_summary_2026-03-20.csv`
- `reports/artifacts/literature/intraday_lottery_max_ema_reclaim_top10_summary_2026-03-20.csv`
- `reports/artifacts/literature/intraday_lottery_max_ema_reclaim_events_2026-03-20.csv`
