# 别把日内时钟只当 filter：`22:00 UTC 单小时多头` 本身就是可独立复现的 raw alpha
- 时间：2026-03-24 00:15 UTC
- 类型：近 5 年论文（SSRN）+ 公开策略库二次摘要 + Binance 公共数据最小快检
- 主题类型：raw alpha
- 基础 alpha：利用 BTC 在固定时段（重点 `22:00–23:00 UTC`）存在的正向时段收益偏移，做“只在该时窗持仓、其余时间空仓”的时间窗 alpha
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/seasonality/intraday/time-of-day/btc/session/momentum/mean-reversion/crypto/1m/3m/5m/15m/cost
- 证据类型：论文线索 + 二次摘要证据 + 公开交易所数据快检

## 1. 这次看了什么
先回答 base alpha：**不是“用时钟当确认层”，而是“时钟本身就是入场信号”**。

本轮选题来自近 5 年论文线索：Padyšák & Vojtko (2022)《Seasonality, Trend-following, and Mean reversion in Bitcoin》（DOI: `10.2139/ssrn.4081000`）。
论文原页（SSRN）当前有反爬限制，本轮先用可访问的二次摘要页（Quantpedia/QuantBuffet）提炼可复现口径，再用 Binance 公共 K 线做最小快检，判断是否值得进我们 raw alpha 池。

## 2. 核心结论
- **一句话结论：** `22:00 UTC` 这一个小时可以先当“独立 raw alpha 候选”，而不是继续只当别的策略的 shared gate。
- 来自论文二次摘要（Quantpedia）的公开指标显示：该思路在原样本（2015–2021）有较高风险调整后收益（摘要给出年化约 33%、Sharpe 约 1.58、MDD 约 -34%）。
- 我们用 Binance `BTCUSDT` 公共数据做的最小快检（2024-01-01 至 2026-03-24）显示：
  - `22:00` 这个小时的 1h 平均收益约 **+4.69 bps**；
  - 把 `22:00` 这一小时拆成 15m 后，整小时复合平均约 **+4.68 bps**，胜率约 **52.6%**；
  - 但 `23:00` 小时均值偏负（约 **-3.65 bps**），说明“持 2 小时”未必优于“只做第 1 小时”。
- 这条线对我们 desk 的价值在于：它是**可独立下单、可直接做 entry/exit/sizing/risk/cost 闭环**的时间窗 alpha，不依赖 breakout/retest 结构定义。

## 3. 为什么和当前项目有关
当前我们已经有大量“确认层/过滤层”材料；这条线能直接补 raw alpha 素材池，而且实现门槛低：
- 数据公开、拉取便宜（交易所 K 线即可）；
- 规则简单、可先做干净 OOS；
- 可自然映射到 `1m/3m/5m/15m`（作为执行粒度，而非必须逐根预测）。

如果问“为什么它比继续补 filter 更值得”：因为它直接回答了“**不看形态，只看时间窗，能不能单独赚钱**”，对素材池是增量信息。

## 3.5 策略拆解（必填）
- 方向属性：日内时段性 + 轻趋势/微动量（time-of-day alpha）
- 基础 alpha：`hold BTC only in 22:00–23:00 UTC window`
- regime：默认全市场；可加“波动分位中档优先”的子状态分层
- filter / veto：
  - 超高波动 veto（例如 15m RV > P95）
  - 重大事件 blackout（CPI/FOMC 前后）
- risk / sizing / execution overlay：
  - **entry**：21:59:50–22:00:10 UTC 按 TWAP/限价分批开多
  - **exit**：22:59:50–23:00:10 UTC 全平
  - **sizing**：波动目标仓位（例如 `target_vol / recent_realized_vol`）
  - **risk**：单窗止损（如 `-0.6%`）+ 日内最大回撤闸门
  - **cost**：手续费 + spread + 冲击（按 participation cap 控制）

## 4. 外部数据与公开性（必填）
该主题依赖的外部数据完全公开，且可快速映射到短周期实验：
- **数据源**：Binance 公共 K 线（REST/WebSocket）
- **公开性**：公开可得，无需付费
- **更新频率**：分钟级/秒级（足够 1m/3m/5m/15m 执行研究）
- **最小可复现实验口径**：
  - 标的：`BTCUSDT`（可扩展到 ETH/SOL）
  - 周期：先 15m（执行可读性高），再下钻 5m/1m
  - 样本：至少 2 年，按年份滚动 OOS

## 5. 可复刻的最小实验（下一步怎么测）
**研究假设：** `22:00–23:00 UTC` 单小时多头在成本后仍有正期望，且优于“22:00–00:00 两小时持有”。

**最小实验步骤：**
1. 拉取 `BTCUSDT` 1h 与 15m 数据（2020–至今），统一 UTC。
2. 构建三条可比策略：
   - A: 仅持有 `22:00–23:00`
   - B: 持有 `22:00–00:00`
   - C: 随机同频持仓基线（matching exposure）
3. 全部纳入成本（双边 fee + 固定滑点 + 轻冲击）。
4. 做滚动 OOS（按年训练阈值、下一年验证）。
5. 先看 4 个指标：`post-cost mean bps/window`、Sharpe、MDD、稳定正收益年份占比。

**和 1m/3m/5m/15m 的关系：**
- 这条 alpha 的“信号频率”是小时级，但执行可在 `1m/3m/5m/15m` 完成；
- 因此它是“低复杂信号 + 高频执行”的组合，不是伪装成逐根预测。

## 6. 风险与保留意见
- 本轮对论文正文仍属“待全文核验”状态（SSRN 访问受限）；当前结论是 intake 级别，不是最终定稿。
- 时段 alpha 易被拥挤与交易所制度变化侵蚀，必须按季度重检。
- `22:00` 正收益不保证每年稳定，需看分年与熊市段表现。
- 若只在 Binance 有效而跨所失效，需降级为 venue-specific pocket，而非通用规律。

## 7. 来源
1. **Padyšák, M., & Vojtko, R. (2022). _Seasonality, Trend-following, and Mean reversion in Bitcoin_. SSRN Electronic Journal.**
   - DOI: `10.2139/ssrn.4081000`
   - Readable URL: `https://doi.org/10.2139/ssrn.4081000`
   - SSRN URL: `https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4081000`
2. **Quantpedia strategy summary (accessed 2026-03-24). _Overnight Seasonality in Bitcoin_.**
   - Readable URL: `https://quantpedia.com/strategies/intraday-seasonality-in-bitcoin`
3. **QuantBuffet strategy summary (2024-04-13). _Bitcoin Local Extremes Mean-Reversion and Trend Strategy_.**
   - Readable URL: `https://quantbuffet.com/en/2024/04/13/mean-reversion-and-trend-following-based-on-min-and-max-in-btc/`
4. **Binance Spot API Docs (public market data).**
   - Readable URL: `https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints`