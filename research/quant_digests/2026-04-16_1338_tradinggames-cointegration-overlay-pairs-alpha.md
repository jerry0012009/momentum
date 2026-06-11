# 别把这篇 2025 *Journal of Futures Markets* 论文只读成“bull market 下 pairs 也能赚”：对 short-cycle desk，更该先拆的是「cointegration spread 回归 × 参数优化（vol filter + adaptive trailing stop）」这条可落地 raw alpha

- 时间：2026-04-16 13:38 UTC
- 类型：论文（Crossref/OpenAlex 元数据+摘要）+ Binance Spot `1h` portability probe（映射到 `15m/5m`）
- 主题类型：raw alpha
- 基础 alpha：co-integrated pair 的 spread 偏离后回归；交易本体是 spread mean reversion，vol filter 与 trailing stop 属于增强层
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/cointegration/parameter-optimization/volatility-filter/adaptive-trailing-stop/1m/3m/5m/15m
- 证据类型：论文摘要级证据 + public-data probe

## 1) 这次看了什么
- **Authors**：Rafael Baptista Palazzi  
- **Year**：2025  
- **Title**：*Trading Games: Beating Passive Strategies in the Bullish Crypto Market*  
- **Venue**：*Journal of Futures Markets*  
- **DOI**：<https://doi.org/10.1002/fut.70018>  
- **Readable URL**：<https://onlinelibrary.wiley.com/doi/10.1002/fut.70018>  
- **Repo URL**：N/A（未检索到官方配套仓库）

摘要里对 desk 最有价值的不是“bull market 也能 beat passive”这句结论，而是策略结构本身：
1) **cointegrated pairs** 是 base alpha；
2) 在交易框架内做了 **systematic parameter optimization**；
3) 风控增强明确点名 **adaptive trailing stop-loss + volatility filtering**。

## 2) base alpha 先说清
这篇东西的 base alpha 是：

> **对协整关系稳定的币对做 spread 回归交易（long cheap / short rich）。**

所以它属于 `raw alpha`。  
vol filter、trailing stop、参数优化是“让 raw alpha 更可交易”的二层组件，不是 alpha 本体。

## 3) 最小可复现实验（本轮已跑）
我做了一个轻量 portability probe（公开数据、可立即复跑）：

- **数据源**：Binance Spot 公共 K 线 API（`/api/v3/klines`，无需私有权限）
- **频率**：`1h`（每个币约 `1000` 根，作为快速验证口径）
- **样本币**：`BTC/ETH/BNB/SOL/XRP/DOGE/ADA/LINK`（`28` 对）
- **base 策略**：rolling hedge ratio + spread z-score（`|z|>2` 入场，回到 0 出场）
- **overlay 策略**：在 base 上叠加 `volatility middle-band filter + adaptive trailing stop + max holding`
- **成本**：按 position change 收 `6 bps`（粗略 friction 口径，仅用于横向对比）

## 4) 关键数据点（这轮最有用的 3 个）
1. **覆盖规模**：`8` 个主流币、`28` 对、每对中位 `1000` 根 `1h` bar，说明“可快速批量筛 pair”是可行的。  
2. **overlay 不是无脑增益**：`overlay_better_total_pairs = 13/28`，中位数 `delta_total = -0.0304`，即不少 pair 会被过度约束。  
3. **overlay 也有明确口袋收益**：均值 `mean_delta_total = +0.3766`，且 `BTC-BNB` / `ETH-BNB` 等 pair 上增益显著，说明“先 pair admission 再决定是否开 overlay”比全局硬套更合理。

## 5) 对当前 desk 的直接意义
- 这不是纯 filter 题，而是**可独立复现的 pairs raw alpha**。
- 真正可迁移的是“**raw alpha 与 overlay 拆层**”这套工程化框架：
  - 先用协整+半衰期做 pair admission；
  - 再按 pair / regime 决定 vol filter 与 trailing stop 是否启用；
  - 避免把 overlay 当成默认必开。

## 6) 下一步怎么测（直接可执行）
1. **迁移到主战场周期**：在 Binance USDⓈ-M 跑 `15m` 主口径，补 `5m/3m/1m` 快口径。  
2. **先 admission 再优化**：仅保留协整稳定（rolling ADF + half-life 合格）的 pair，再做参数搜索。  
3. **分层回测矩阵**：`base only` / `base+vol filter` / `base+trail stop` / `base+both`，避免把改动揉成黑箱。  
4. **成本/执行升级**：把粗 bps 扣费替换为 maker-taker、滑点、冲击、资金费率的分层成本。  
5. **输出可上线壳**：固定 entry/exit、仓位上限、max holding、kill-switch（连续亏损/流动性骤降）。

## 7) 本轮产物
- `reports/artifacts/quant_digests/trading_games_pairs_overlay_probe_2026-04-16.csv`
- `reports/artifacts/quant_digests/trading_games_pairs_overlay_probe_2026-04-16_summary.json`

## 8) 来源
1. Palazzi, R. B. (2025). *Trading Games: Beating Passive Strategies in the Bullish Crypto Market*. Journal of Futures Markets.  
   DOI: <https://doi.org/10.1002/fut.70018>  
   Readable URL: <https://onlinelibrary.wiley.com/doi/10.1002/fut.70018>
2. Crossref metadata（含摘要）: <https://api.crossref.org/works/10.1002/fut.70018>
3. OpenAlex metadata（含 OA 链接与 abstract inverted index）: <https://api.openalex.org/works/https://doi.org/10.1002/fut.70018>
4. Binance Spot Kline API（public）: <https://api.binance.com/api/v3/klines>
