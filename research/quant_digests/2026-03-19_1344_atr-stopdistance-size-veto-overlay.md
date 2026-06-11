# 别把 ATR 只当止损距离：`stopDistancePct` 更像 breakout-short / Fib / EMA-PSAR 的 shared size-veto 层
- 时间：2026-03-19 13:44 UTC
- 类型：GitHub + 本地代理快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/atr/position-sizing/risk-overlay/filter/repo/crypto/15m
- 证据类型：repo 代码规则（工程证据）+ 公开行情代理快检

## 1. 这次看了什么
这轮看的是 **Fesenko2v (2026) 的 `TradingView-strategy-EMA200-Donchian-breakout-ATR-risk`**。我没有把它当“新 alpha”，而是抽出更适合当前 desk 的旁支：
**把 `stopDistance = ATR*K` 变成 `stopDistancePct = (ATR*K)/close`，用于仓位缩放或高波动 veto。**

## 2. 核心结论
1. **一句话核心结论**：对 15m 来说，`ATR stopDistancePct` 更像风险层（size-down / veto），不是进场层；它能减少“高波动同仓位硬做 continuation”的磨损。  
2. **一句话证明方式**：repo 给了可复现的风险计算骨架（`riskCapital/stopDistance`）；我用 Binance Futures 公开 15m（BTC/ETH/SOL，120 天）做 Donchian breakout 事件代理，比较固定名义 vs `size_mult=clip(median(stopPct)/stopPct,0.5,1.5)`。  
3. 代理结果（2211 个事件，round-trip 成本 8bps）：
   - 固定名义 `net8_mean`：**-0.49 bps/笔**
   - size-down 后 `sized_net8_mean`：**+1.22 bps/笔**
4. 分桶后更直观：
   - **high ATR 桶**：`net8_mean = -6.14 bps`（最差）
   - **mid ATR 桶**：`+2.61 bps`
   - **low ATR 桶**：`+2.05 bps`
5. 这说明高 ATR 事件不是“仓位该放大”的区间，先做 size-down 或 veto 更诚实。

## 3. 为什么和当前三条收口线直接相关
- **V3 final-verdict / breakout-short follow-up**：当下破后 `stopDistancePct` 落在高分位，优先降仓或禁做 follow-up，避免假延续阶段放大亏损。  
- **Fibonacci confirmation / retest_hold**：Fib 位置确认可继续用，但若回踩确认发生在高 ATR 桶，不应同仓位执行；更像 `admission + sizing` 联动。  
- **EMA / PSAR raw alpha focus**：EMA/PSAR 负责方向，`stopDistancePct` 负责“做多少/是否做”，正好补齐当前风险层缺口（`FACTOR_BACKLOG` 的 ATR sizing 待补项）。

## 4. 下一步怎么测（5m / 15m 最小实验）
### 4.1 数据与公开性
- 数据源：Binance Futures 公共 K 线（`/fapi/v1/klines`）
- 公开性：公开可得
- 更新频率：5m / 15m
- 本轮产物：
  - `reports/artifacts/quant_digests/2026-03-19_atr_stopdistance_size_gate_proxy_events.csv`
  - `reports/artifacts/quant_digests/2026-03-19_atr_stopdistance_size_gate_proxy_summary.csv`
  - `reports/artifacts/quant_digests/2026-03-19_atr_stopdistance_size_gate_proxy_summary.json`

### 4.2 最小可复现实验口径（建议）
把三条 archetype（breakout-short / fib-retest / ema-psar）统一接一层：
1. 每个候选事件算 `stopDistancePct_t=(ATR14*K)/close`（先 `K=2`）；
2. 做三臂对照：
   - A：固定名义仓位
   - B：`size_mult=clip(median/stopPct,0.5,1.5)`
   - C：B + `high ATR` 桶直接 veto
3. 执行统一：`next-bar open`，`hold 8 bars`，成本 `6/10/15 bps per side`。

首轮只看 4 项：`post_cost_expectancy`、`max_drawdown`、`trade_count_retention`、`high-ATR bucket contribution`。

## 5. 风险与保留意见
- 这是事件级代理，不是完整策略回测；
- 当前快检基于 Donchian breakout 骨架，迁移到 Fib/EMA-PSAR 需单独复核；
- `size-down` 可能在强趋势高波动段“少赚”，不能只看回撤改善；
- 若 OOS 下只改善曲线、不改善成本后期望，应降级为“风险保守模式”而非默认层。

## 6. 来源
1. **Fesenko2v. (2026). _TradingView-strategy-EMA200-Donchian-breakout-ATR-risk_.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: <https://github.com/Fesenko2v/TradingView-strategy-EMA200-Donchian-breakout-ATR-risk>  
   - Repo URL: <https://github.com/Fesenko2v/TradingView-strategy-EMA200-Donchian-breakout-ATR-risk>
2. **关键实现：`src/strategy.pine`（`riskCapital/stopDistance` 与固定风险仓位）**  
   - Readable URL: <https://github.com/Fesenko2v/TradingView-strategy-EMA200-Donchian-breakout-ATR-risk/blob/main/src/strategy.pine>  
   - Raw URL: <https://raw.githubusercontent.com/Fesenko2v/TradingView-strategy-EMA200-Donchian-breakout-ATR-risk/main/src/strategy.pine>
3. **公开行情数据源**  
   - Binance Futures Klines API: <https://fapi.binance.com/fapi/v1/klines>