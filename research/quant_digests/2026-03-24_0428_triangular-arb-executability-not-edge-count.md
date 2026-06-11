# 别把三角套利机会数当 alpha：这篇 2025 论文更值得先复现的是「可执行性阈值（成本+深度+延迟）」这条 raw alpha 生存线
- 时间：2026-03-24 04:28 UTC
- 类型：近 5 年论文（全文）+ 高信号开源仓库 + Binance 公共数据最小快检
- 主题类型：raw alpha
- 基础 alpha：同一交易所内 `USDT→BTC→LTC→USDT`（或更一般多边循环）短时定价不一致带来的无方向相对价值回归
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/stat-arb/relative-value/triangular-arbitrage/cycle-arbitrage/execution-latency/orderbook-depth/transaction-cost/binance/crypto/1m/3m/5m/15m/paper/repo
- 证据类型：论文全文 + 开源检测仓库 + 公开 API 快检（本地）

## 1. 这次看了什么
先回答 base alpha：**这是 raw alpha，不是 filter。**

alpha 本体是：
- 当循环汇率乘积 `Y(t)` 暂时偏离 1（例如 `Y(t)>1`）时，做一圈无方向换汇并回到起始资产，赚取偏离收敛前的价差；
- 对应论文里的三角路径是 `USD→BTC→LTC→USD`。

本轮主材料：
1. **Muck, Schmidl, Wolf (2025, Finance Research Letters)**：把三角套利从“有机会”拆到“能否执行并净赚”。
2. **Drakkar-Software/Triangular-Arbitrage（2023 创建，2026 仍在更新，118★）**：给出可直接跑的多资产循环机会检测框架（Binance/Hyperliquid 等），但 README 明确提示未计入手续费。
3. **Binance 公共 1m K 线快检（本轮本地）**：用 `BTCUSDT / LTCBTC / LTCUSDT` 做 7 天代理验证，检查 1m/3m/5m/15m 上“毛机会 vs 费用后机会”的存活率。

## 2. 核心结论（先给交易结论）
- **一句话**：三角套利不是“有没有机会”的问题，而是“机会是否大于成本、能否在延迟窗口内成交、且有足够深度”的问题。对 desk 来说，它是可复现 raw alpha，但执行门槛极高。  
- **更直接地说**：这条线值得进素材池，但应默认归类为**执行敏感型 raw alpha**，而不是常规 5m/15m 主策略。

关键数据点（论文 + 本轮最小快检）：
1. 论文在 Binance 一周高频数据里识别 **4,879** 个潜在三角机会，但大多收益落在 **0%~0.025%**。
2. 计入交易费后，普通费率交易者仅剩 **18** 个可盈利机会；整周净利约 **$12.43 ~ $17.73**（按不同执行假设）。
3. 论文给出可执行阈值：平均需在 **146ms** 内完成执行，否则期望值转负；其采集延迟从欧洲约 **80ms** 优化到东京约 **4ms**。
4. 本轮 7 天 Binance 1m 代理快检（10080 bars）：`edge>0` 占 **56.22%**，但 `edge>0.225%`（论文 regular 费率阈值）仅 **13 bars (0.13%)**，且连续段中位数仅 **1 bar**、最大 **2 bar**。
5. 同一代理下，`edge>0.30%` 在 1m/3m/5m/15m 全部为 **0**，说明“看起来很多机会”在成本后基本被抹平。

## 3. 为什么和当前 desk 直接相关
这轮不是补 overlay，而是补一个**可独立复现的 stat-arb raw alpha 家族**（triangular/cycle arb）。

它对当前素材池的价值：
- 补齐了“**无方向相对价值**”路线，不依赖趋势判断；
- 论文+仓库都能直接转成可执行实验，不是纯综述；
- 能反向服务其他 alpha：把“可执行性阈值（成本/延迟/深度）”作为统一 realism gate。

## 3.5 策略拆解（entry / exit / sizing / risk / cost）
- **Entry（触发）**：当循环报价乘积 `Y(t)` 超过阈值 `1 + fee_buffer + slippage_buffer`。
- **Exit（完成）**：三腿（或多腿）循环全部成交并回到起始资产；若超时未成交则放弃（timeout kill）。
- **Sizing（仓位）**：由最薄腿深度决定：`size = min(leg1_qty, leg2_qty换算, leg3_qty换算, ... )`。
- **Risk（风险）**：
  - 任何一腿挂单超时 / 部分成交 → 立刻对冲或强平残留；
  - 设最大允许执行时延（论文给了 146ms 量级的参考）。
- **Cost（成本）**：至少计入三腿手续费 + 滑点 + 取消重挂损耗；仅看“毛 edge”无意义。

## 4. 与 `1m/3m/5m/15m` 的关系（诚实版）
- **1m/3m**：可作为“机会雷达 + 生存线估计”频率；但真正执行通常要更低延迟数据（盘口/逐笔）。
- **5m/15m**：不适合当逐根主信号；更适合做“执行可行性监控”或低频化的跨资产循环扫描。
- 结论：该题材**属于 raw alpha**，但不是典型 K 线频率主策略，核心在 execution stack。

## 5. 最小可复现实验口径（本轮已跑）
### 5.1 数据源、公开性、更新频率
- 数据源：Binance Spot REST `/api/v3/klines`（`BTCUSDT`,`LTCBTC`,`LTCUSDT`）
- 公开性：公开可得，无需私有数据
- 更新频率：1m（可聚合为 3m/5m/15m）

### 5.2 实验口径
- 时间窗：最近 7 天
- 代理 edge：`edge_pct = LTCUSDT / (BTCUSDT * LTCBTC) - 1`
- 成本阈值：
  - 论文 regular 费率参照：`0.225%`
  - 保守三腿 taker 参照：`0.30%`
- 输出：
  - `reports/artifacts/literature/triangular_arb_binance_1m_7d_proxy_2026-03-24.csv`

## 6. 下一步怎么测（必须）
1. **从 K 线代理升级到盘口级**：改用 top-of-book bid/ask 与可成交量，重算真实 `Y(t)` 与可成交 notional。  
2. **显式建模延迟预算**：按 `20/50/100/150/200ms` 五档回放，直接画 `EV(latency)` 曲线，验证本地基础设施是否能过线。  
3. **做费用/角色分层**：maker-only、maker+taker、VIP/regular 三套费用场景，确认策略是否仅在特定费率层可活。  
4. **扩展到多循环与多交易所**：从三角扩到 4~7 边循环（对应开源仓库能力），但每条循环都要过“深度+延迟+成本”三重门。  
5. **把它接入组合治理**：若无法稳定跨过执行门槛，则把该信号降级为“市场效率压力指标”，不进入主交易配额。

## 7. 风险与保留意见
- 这类 alpha 对撮合与网络位置极端敏感，研究可复现 ≠ 实盘可赚钱。  
- 本轮本地快检是 K 线代理，不含盘口微结构与撮合队列位置，只能做“是否值得继续”的 first-pass。  
- 开源仓库默认不含费用，直接照跑容易高估收益。

## 8. 来源
1. **Muck, M., Schmidl, T., & Wolf, J. (2025). _Wish or reality? On the exploitability of triangular arbitrage in cryptocurrency markets_. Finance Research Letters, 73, 106508.**  
   - Venue: Finance Research Letters (Elsevier)  
   - DOI: https://doi.org/10.1016/j.frl.2024.106508  
   - Readable URL: https://www.sciencedirect.com/science/article/pii/S154461232401537X  
   - Fulltext mirror URL: https://fis.uni-bamberg.de/server/api/core/bitstreams/8b9ae900-017a-4bed-94b9-609c16e89945/content  
   - Repo URL: N/A
2. **Drakkar-Software. (2023–2026). _Triangular-Arbitrage_. GitHub repository.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: https://github.com/Drakkar-Software/Triangular-Arbitrage  
   - Repo URL: https://github.com/Drakkar-Software/Triangular-Arbitrage
3. **Binance Developers. _Spot API – Kline/Candlestick data_.**  
   - Venue: Official Docs  
   - DOI: N/A  
   - Readable URL: https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#klinecandlestick-data  
   - Repo URL: N/A

## 9. 本地复现产物
- `reports/artifacts/literature/triangular_arb_binance_1m_7d_proxy_2026-03-24.csv`
