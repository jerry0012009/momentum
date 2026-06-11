# 别把 funding / OI 写成“单币单点阈值”：cross-symbol crowding breadth 更像 15m 三条收口线共用的 size/veto overlay
- 时间：2026-03-21 03:02 UTC
- 类型：官方 API 文档 + 官方 SDK 仓库 + 公共数据快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/funding/open-interest/crowding/breadth/regime/filter/position-sizing/repo/docs/binance/crypto/5m/15m
- 证据类型：工程可复核 + 公开数据快检（待最小回测）

## 1) 这次看了什么
本轮不再把 funding 或 OI 当“单币方向键”，而是用 Binance 公共接口做一个**横截面 crowding breadth**：
- 用 `fundingRate` 提供多空拥挤方向（符号）
- 用 `openInterestHist` 提供是否继续加仓（增量）
- 在 top-liquid 合约上做 breadth，而不是盯 BTC 一根线

## 2) 核心结论
- **一句话核心结论**：对 15m desk，`funding × OI` 更适合做 **cross-symbol crowding breadth overlay**（仓位/否决层），不适合当逐根主信号。
- **一句话证明方式**：同一时点快检显示，拥挤并非“全市场同向”，而是局部扩散；因此单币阈值容易误判，breadth 更适合作为三条收口线共享风控层。

### 本轮 3 个关键数据点（公开接口快检）
快检文件：`reports/artifacts/quant_digest_live/binance_funding_oi_breadth_20260321_030133.json`
1. top30 交易额合约里可用样本 `24` 个；
2. `long crowding breadth = 20.83%`，`short crowding breadth = 16.67%`；
3. `OI 上升广度 = 41.67%`，且 `median OIΔ(5m) = -0.0231%`（说明全体并非一致加杠杆）。

## 3) 为什么和三条收口线直接相关
这条线值得做，因为它是三条线的**共享风险层**，能直接帮助收口：
- `V3 breakout-short follow-up`：当 short crowding breadth 高时，避免“拥挤方向末端追击”；
- `Fib confirmation / retest_hold`：当 long crowding breadth 高时，提高 long-side 回踩确认门槛；
- `EMA / PSAR raw alpha`：先保留 raw trigger，不加新花哨触发，优先做仓位折扣与 veto。

## 4) 可复刻的最小实验（5m/15m）
### 数据源（公开性 / 更新频率）
- Binance USDⓈ-M 24h ticker：公开，无需 key，近实时；
- Funding rate history：公开，无需 key，funding 结算节奏（通常 8h）更新；
- Open interest statistics：公开，无需 key，可取 `5m` 频率。

### v0 指标定义
在每个 15m bar close：
1. 选 `quoteVolume` 前 30 的 USDT perpetual；
2. 对每个 symbol 取：
   - `f_i = latest fundingRate`
   - `d_i = OIΔ_15m`（由 5m OI 聚合）
3. 定义：
   - `LongCrowdBreadth_t = mean( f_i > 0 and d_i > 0 )`
   - `ShortCrowdBreadth_t = mean( f_i < 0 and d_i > 0 )`
4. 对 breadth 做 rolling percentile（如 30d）并映射 risk bucket。

### 接入三条线（先测最小口径）
- baseline：现有 breakout-short / fib_retest_hold / ema_psar；
- overlay：
  - 若 `ShortCrowdBreadth >= p80`：short 侧仓位 ×0.6，且 breakout-short 需额外 1 根 confirm；
  - 若 `LongCrowdBreadth >= p80`：long 侧仓位 ×0.6，Fib/EMA long 需额外 reclaim 确认；
  - 其余不变。

### 首轮只看 4 个指标
1. `post_cost_expectancy`
2. `failure_rate`
3. `trade_count_retention`
4. `max_drawdown`

## 5) 风险与保留意见
- Funding 更新慢于 15m，天然更像 regime/filter/sizing，不是逐根触发器；
- OI 受交易所口径与合约轮动影响，需先做活跃度过滤；
- 小币种的极端 funding/OI 波动可能污染 breadth，需设最小流动性门槛。

## 6) 来源
1. Binance. (2025-2026). **Binance Python Connectors**. GitHub Repository.  
   - Venue: GitHub  
   - DOI: `N/A`  
   - Readable URL: `https://github.com/binance/binance-connector-python`  
   - Repo URL: `https://github.com/binance/binance-connector-python`
2. Binance Developers. (2025-2026). **USDⓈ-M Futures Market Data REST API**. Official Documentation.  
   - Venue: Binance Open Platform  
   - DOI: `N/A`  
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/24hr-Ticker-Price-Change-Statistics`  
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-History`  
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Open-Interest-Statistics`

---
一句话收口：

**先把 funding/OI 从“单币方向键”升级为“横截面 crowding breadth overlay”，比继续给 15m 主信号堆阈值更能直接帮三条收口线降噪与控回撤。**
