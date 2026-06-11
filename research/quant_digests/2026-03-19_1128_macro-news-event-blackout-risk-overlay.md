# 别把宏观日程当日线背景音：`FOMC/CPI event-blackout + size-down` 更像 15m 三条主线共用的风险覆盖层
- 时间：2026-03-19 11:28 UTC
- 类型：论文 + 外部公开数据 + 本地快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/macro-news/event-blackout/risk-overlay/position-sizing/filter/paper/crypto/5m/15m
- 证据类型：近 5 年论文 + 官方公开日程 + 15m 历史快检

## 1) 这次看了什么（只抓对 desk 有用的旁支）
本轮不把宏观新闻硬装成逐根 15m 主信号，而是把它定位成更诚实的 **event-risk overlay**：
- **Ben Omrane et al. (2025)**：`Exploring volatility reactions in cryptocurrency markets using intraday macroeconomic news analysis`（近 5 年新论文）
- **Ben Omrane, Houidi, Savaşer (2023)**：`Macroeconomic news and intraday seasonal volatility in the cryptocurrency markets`

这条线比继续在 entry 细节里打补丁更值得：
> 因为它能同时服务三条收口线（breakout-short / Fib retest_hold / EMA-PSAR），且实现成本很低（只需公开日程 + 时间窗映射），优先解决的是 **fake break / whipsaw / 成本后存活**。

## 2) 对当前三条收口线的可执行结论
一句话：
**宏观高风险时间窗更适合当 `blackout / size-down gate`，而不是 15m 主触发。**

映射到三条线：
1. **V3 final-verdict / breakout-short follow-up**
   - 在事件窗内，突破后的 follow-up 更容易变成“方向先对、路径后坏”；
   - 先做 `size-down` 或 `延迟确认`，比继续加复杂形态条件更便宜。
2. **Fibonacci confirmation / retest_hold**
   - 事件窗里回踩容易被突发波动穿透后再拉回；
   - `retest_hold` 应增加事件窗 veto（或更高确认阈值）。
3. **EMA / PSAR raw alpha focus**
   - EMA/PSAR 更适合保留为方向层；
   - 事件窗交给 risk overlay（仓位/触发门槛）而非改坏原始方向逻辑。

## 3) 本地最小快检（公开日程 + 现有 15m cache）
### 3.1 数据与口径
- 价格数据：`BTC/ETH/SOL 15m perp`（本地已有 cache）
- 事件数据（公开、官方）：
  - Fed FOMC 日程：<https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm>
  - BLS CPI 发布日程：<https://www.bls.gov/schedule/news_release/cpi.htm>
- 时间映射（首版冻结）：
  - FOMC statement 按 `14:00 ET` 映射到 UTC
  - CPI 按 `08:30 ET` 映射到 UTC
- 指标：
  - 事件 bar `abs_return_bp`
  - 事件 bar `bar_range_bp`
  - 事件后 1h `fwd1h_range_bp`
- 对照：同样本期全体 15m bar 的中位数

### 3.2 快检结果（2025-01-01 ~ 2026-03-19）
关键数值（中位数倍数）：
1. **BTC：FOMC/CPI 事件后 1h range ≈ 基线的 2.91x**（149.7bp vs 51.5bp）
2. **ETH：事件后 1h range ≈ 基线的 2.51x**（218.6bp vs 86.9bp）
3. **SOL：事件后 1h range ≈ 基线的 2.22x**（228.5bp vs 103.1bp）

补充：FOMC 事件 bar 当根 range 在 BTC/ETH/SOL 分别约为基线 **3.34x / 3.41x / 2.84x**。

快检文件：
- `reports/artifacts/literature/macro_event_overlay_quickcheck_events_2026-03-19.csv`
- `reports/artifacts/literature/macro_event_overlay_quickcheck_summary_2026-03-19.csv`

## 4) 下一步怎么测（5m/15m 最小实验）
### 4.1 实验目标
验证：在不改三条主线方向逻辑的前提下，`macro-event overlay` 能否降低 continuation failure 并改善成本后表现。

### 4.2 A/B 设计（最小可复现）
- Universe：BTC/ETH/SOL perp
- 执行：15m 产信号，`next-bar open`，`no-overlap`
- 成本：`6/10/15 bps per side`

组别：
- **A（baseline）**：原 breakout-short / fib_retest_long / ema_psar_long
- **B（blackout）**：事件前后 `[-1h,+1h]` 不开新仓
- **C（size-down）**：事件窗内仓位乘数 `0.5x`
- **D（hybrid）**：事件前后 `[-30m,+30m]` blackout，`[+30m,+120m]` size-down

### 4.3 先看判据
- `post_cost_return`
- `false_break_ratio`
- `4~8 bar continuation failure rate`
- `trade_count_retention`

首轮通过门槛（相对 A）：
- `failure rate` 下降 ≥ 8%
- `post_cost_return` 不恶化超过 5%
- `trade_count_retention` ≥ 60%

## 5) 风险与保留意见
- 这条线是 **overlay/filter**，不是独立 alpha；
- 当前快检样本仍偏短，且事件时间采用“官方发布时间近似映射”，后续应接入更细粒度实际发布时间戳；
- 事件窗可能与本来活跃时段重叠，需在回测中做“时段效应剥离”（避免把时段 alpha 误记为宏观 alpha）。

## 6) 来源（Authors / Year / Title / Venue / DOI / URL / Repo）
1. **Ben Omrane, W., Dabbou, H., Saadi, S., Savaşer, T., & Sebai, S. (2025).**
   *Exploring volatility reactions in cryptocurrency markets using intraday macroeconomic news analysis*.
   **International Review of Economics & Finance**.
   - DOI: <https://doi.org/10.1016/j.iref.2025.104509>
   - Readable URL: <https://doi.org/10.1016/j.iref.2025.104509>
   - Repo URL: N/A

2. **Ben Omrane, W., Houidi, F., & Savaşer, T. (2023).**
   *Macroeconomic news and intraday seasonal volatility in the cryptocurrency markets*.
   **Applied Economics**.
   - DOI: <https://doi.org/10.1080/00036846.2023.2212970>
   - Readable URL: <https://doi.org/10.1080/00036846.2023.2212970>
   - Repo URL: N/A

3. **外部公开数据（用于最小可复现实验）**
   - Fed FOMC meeting calendar（公开网页，按会议更新）
     - <https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm>
   - BLS CPI release schedule（公开网页，按月更新）
     - <https://www.bls.gov/schedule/news_release/cpi.htm>
