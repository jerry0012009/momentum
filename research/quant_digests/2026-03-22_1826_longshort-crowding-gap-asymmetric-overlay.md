# 别把 Long/Short Ratio 当 15m 方向键：`global-vs-top position crowding gap` 更像 breakout-short / Fib / EMA-PSAR 的 asymmetric risk overlay
- 时间：2026-03-22 18:26 UTC
- 类型：官方 API 文档 + Binance 公共数据最小快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/long-short-ratio/crowding-gap/asymmetry/regime/filter/position-sizing/risk-overlay/crypto/15m
- 证据类型：工程快检（公开数据）

## 1. 这次看了什么
这轮不再把 `Long/Short Ratio` 当“做多/做空按钮”，而是抽一个更贴 desk 的旁支变量：

> **`crowding_gap = global longAccount - topTraderPosition longAccount`**

直觉：
- `global` 代表全体账户拥挤度；
- `topTraderPosition` 更接近头部仓位真金白银的净暴露；
- 两者差值更像“散户拥挤与头部仓位是否同向”的温度计，可做 15m 的过滤/仓位层。

## 2. 核心结论
- **一句话核心结论：** `Long/Short Ratio` 单点方向信息不稳定，但 `global-vs-top position crowding gap` 在 15m breakout proxy 上呈明显**方向不对称**，更适合作为 `veto / size overlay`，不是主入场信号。  
- **一句话证明方式：** 用 Binance USDⓈ-M 公开 15m 数据（BTC/ETH/SOL，近 30 天）做 Donchian20 breakout 代理事件，比较不同 crowding gap 分桶的 4-bar 成本后表现。

### 本轮关键数据点（pooled）
样本：`BTCUSDT/ETHUSDT/SOLUSDT`，15m，近 30 天；事件数：`long=341`，`short=347`；成本代理：`12 bps roundtrip`。

1. **long breakout 在 low-gap 桶最差**（`gap_longAccount <= p10`）  
   - `mean_net = -27.67 bps`，`fail_ratio = 65.71%`  
   - 对比 mid 桶：`mean_net = -3.62 bps`

2. **short breakout 在 high-gap 桶反而最好**（`gap_longAccount >= p90`）  
   - `mean_net = +6.34 bps`，而 mid 桶为 `-5.12 bps`

3. `gap` 分位阈值（事件内）大致在：  
   - long：`p10≈0.0128`，`p90≈0.1777`  
   - short：`p10≈-0.0058`，`p90≈0.1525`

> 解读（人话）：同样叫“拥挤”，它对多空不是镜像关系。拿它做“统一方向开关”很危险；拿它做分线 veto/仓位叠加更实用。

## 3. 为什么和当前三条收口线直接相关
- **V3 final-verdict / breakout-short follow-up**：当 `crowding_gap` 高（全体更拥挤多头、头部仓位没那么多），short follow-up 质量在本轮 proxy 里更好，适合做 short 侧加分或放行层。  
- **Fibonacci confirmation / retest_hold**：long retest 若落在 `low-gap` 区间，本轮更像“弱承接回弹”，可先做 veto 或降仓。  
- **EMA / PSAR raw alpha focus**：可直接作为 shared risk overlay（先过滤拥挤错配状态，再让 EMA/PSAR 承担触发）。

如果问“为何这题比继续泛找更值得”：它是**公开可得、15m 对齐、实现成本低**的外部行为变量，且能立刻接到三条收口线，不用等复杂数据工程。

## 4. 可复刻的最小实验
- **研究假设**：`global-vs-top position` 拥挤错配对 15m continuation/failure 有方向不对称信息，适合做 veto/sizing overlay。  
- **数据源（公开）**：Binance USDⓈ-M Futures REST（无需私钥，公网可拉）。  
- **更新频率**：`5m/15m/30m/...`（本轮用 15m）。  
- **最小口径**：
  1) 用 `fapi/v1/klines` 构造 Donchian20 breakout 事件；
  2) 同时拉 `globalLongShortAccountRatio` 与 `topLongShortPositionRatio`；
  3) 计算 `gap_longAccount = longAccount_global - longAccount_toppos`；
  4) 比较 `p10 / mid / p90` 三桶的 `4-bar post-cost net` 与 `fail_ratio`。

## 5. 下一步怎么测（必须动作）
在三条收口线直接做 A/B：

1. **A（baseline）**：不加 crowding overlay；
2. **B（veto）**：long 侧若 `gap <= p10` 则 veto；
3. **C（asymmetric sizing）**：short 侧若 `gap >= p90` 半仓→满仓递增，其他维持 baseline。

统一比较四个指标：
- `post_cost_expectancy`
- `false_follow_ratio`（入场后 2~4 bar 反向）
- `trade_retention`
- `timeout_share`

通过条件建议：若 B/C 在 OOS 下能同时改善 `expectancy` 与 `false_follow_ratio`，且 `trade_retention` 不低于 70%，再升级为 shared overlay。

## 6. 风险与保留意见
- 本轮是 breakout proxy 快检，不是三条正式策略的 clean replication；不能直接当生产阈值。  
- 两端分桶样本较小（每侧约 35 笔），需 rolling/OOS 继续验证。  
- `top trader` 统计口径是交易所定义口径，可能随平台结构变化漂移。  
- 因子呈现明显多空不对称，**禁止一套阈值镜像套给多空**。

## 7. 来源
1. **Binance Open Platform. (2026). _Long Short Ratio_ (USDⓈ-M Futures REST API).**  
   - Authors / Org: Binance  
   - Year: 2026  
   - Title: Long Short Ratio  
   - Venue: Binance Open Platform Docs  
   - DOI: N/A  
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Long-Short-Ratio`  
   - Repo URL: N/A

2. **Binance Open Platform. (2026). _Top Trader Long Short Account Ratio_ (USDⓈ-M Futures REST API).**  
   - Authors / Org: Binance  
   - Year: 2026  
   - Title: Top Trader Long Short Account Ratio  
   - Venue: Binance Open Platform Docs  
   - DOI: N/A  
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Top-Long-Short-Account-Ratio`  
   - Repo URL: N/A

3. **Binance Open Platform. (2026). _Top Trader Long Short Position Ratio_ (USDⓈ-M Futures REST API).**  
   - Authors / Org: Binance  
   - Year: 2026  
   - Title: Top Trader Long Short Position Ratio  
   - Venue: Binance Open Platform Docs  
   - DOI: N/A  
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Top-Trader-Long-Short-Ratio`  
   - Repo URL: N/A

## 8. 本轮产物
- `reports/artifacts/quant_digests/ls_ratio_gap_proxy_20260322/panel_15m.csv`
- `reports/artifacts/quant_digests/ls_ratio_gap_proxy_20260322/breakout_proxy_conditional_summary.csv`
- `reports/artifacts/quant_digests/ls_ratio_gap_proxy_20260322/breakout_proxy_conditional_summary_by_symbol.csv`
- `reports/artifacts/quant_digests/ls_ratio_gap_proxy_20260322/metadata.json`
