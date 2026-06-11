# 别把 `better-than-lastEntry EMA rebound` 写成 shared re-arm：它在 15m 只像 Fib / EMA long 的轻度 loss-control 过滤，不足以救活 EMA/PSAR raw alpha，也不该镜像给 breakout-short
- 时间：2026-03-23 01:30 UTC
- 类型：GitHub 仓库 + Binance 公共数据最小快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/supertrend/ema-rebound/price-improvement/rearm/asymmetry/filter/repo/crypto/15m
- 证据类型：工程证据（仓库源码）+ 本地最小代理快检

## 1. 这次看了什么
这轮主看 **Alorse. (2026). _pinescript-strategies_** 里的 **`Supertrend + EMA rebound [Alorse]`**。这份脚本真正值得 desk 偷看的，不是 headline 里的 `Supertrend + EMA` 四个字，而是一个更细的旁支写法：
> **只有当价格先跌回 EMA 下方、再重新站回 EMA，且这次重站回的价格比“上一次入场价更便宜”时，才允许 re-entry。**

我把它翻成当前 desk 的问题：
> **`better-than-lastEntry` 这种“更便宜再上车”约束，值不值得被升成 15m breakout-short / Fib / EMA-PSAR 的 shared re-arm gate？**

## 2. 核心结论
- **一句话结论**：不值得升成 shared gate。它最多只像 **Fib / EMA long 的轻度 loss-control re-arm 过滤**；对 `EMA / PSAR raw alpha` 不够强，对 `breakout-short` 镜像后反而更差。  
- **一句话证明方式**：先读 repo 里的 Pine 规则，再用 Binance USDⓈ-M Futures `BTC/ETH/SOL` 最近 `120d` 的 `15m` K 线做最小代理：统一 `signal on close -> next bar open`、`hold 8 bars`、`6 bps/side`，比较 `raw supertrend flip`、`EMA reclaim(any)`、`EMA reclaim + better-than-lastEntry` 三臂。

关键数据点（BTC/ETH/SOL 等权）：
1. **long 侧只看到“少亏一点”，没看到翻正**  
   - `EMA reclaim(any)`: `mean_net_return=-0.1227%`，`mean_trades=241.7`  
   - `EMA reclaim + better-entry`: `mean_net_return=-0.1075%`，只改善约 **1.5 bps**，但交易降到 `122.0`，保留率仅 **50.5%**
2. **它连 raw long flip 都没明显赢过**  
   - `raw supertrend flip long`: `mean_net_return=-0.0963%`  
   - 说明“更便宜再上车”只能削弱坏交易密度，**还不足以把 EMA/PSAR 家族从负边际救出来**
3. **short 镜像更不诚实**  
   - `EMA reclaim(any) short`: `mean_net_return=-0.1020%`  
   - `better-entry short`: `-0.1220%`，且只剩 **49.4%** 交易  
   - 反而是 `raw supertrend flip short` 还有 `+0.0266%` 的微弱正边际

## 3. 为什么和当前项目有关
- **对 `EMA / PSAR raw alpha focus`**：这是最直接的一刀。它告诉我们，`price-improvement re-arm` 更像减亏条款，不是能单独救活 raw alpha 的主按钮。  
- **对 `Fibonacci confirmation / retest_hold`**：这条思路仍有价值，但位置应该更低——更像回踩确认后的 **二次筛选**，不是独立确认真相。  
- **对 `V3 final-verdict / breakout-short follow-up`**：当前证据明确不支持镜像复用；short 侧做成 `better-than-lastEntry` 反而更坏，说明这不是 shared follow-up 语言。

## 3.5 策略拆解（必填）
- 方向属性：顺势 continuation / re-arm，但当前只在 long pullback 侧有弱信息
- 基础 alpha：趋势仍在时的 EMA reclaim 二次上车
- regime：先要求趋势状态仍在（repo 里由 `Supertrend` 维持）
- filter / veto：`reclaim EMA` 且 `current reclaim price better than last entry`
- risk / sizing / execution overlay：当前最诚实的角色更像 **loss-control / trade-thinning overlay**，不是 raw trigger

## 4. 可复刻的最小实验
下一步别把它直接升成 desk 公共规则，而是只做 **Fib / EMA long 专项 3 臂测试**：
1. `baseline_retest_hold`
2. `baseline + EMA reclaim(any)`
3. `baseline + EMA reclaim(better-than-lastEntry)`

统一口径：
- 资产：BTC/ETH/SOL perp
- 周期：`15m signal`，必要时补 `5m execution`
- 执行：`next-bar open + no-overlap`
- 判决：先看 `8/12 bars` 两档，再补 `continue vs early-fail`
- 优先看：`post-cost mean return`、`trade retention`、`early-fail ratio`

如果结果继续呈现“long 侧仅减亏、short 侧更差”，就该把它正式降级为 **Fib / EMA long 的可选 re-arm thinning filter**，不要再拿它去救 `EMA / PSAR raw alpha`，更不要往 breakout-short shared gate 上推。

## 5. 风险与保留意见
- 这轮是 **proxy hold-8**，不是完整策略回测；
- repo 原始脚本还带 `take-profit` 与 `Supertrend` 出场，这里故意先冻结成最小口径；
- `lastEntry` 在 TradingView 策略对象里的精确语义，比这里的 clean-room 代理更状态化；
- 当前结果在 ETH long 上相对更像样、在 SOL long 上反而更差，说明它更像资产敏感的 trade-thinning 规则，不像稳定 shared alpha。

## 6. 来源
1. **Alorse. (2026). _pinescript-strategies_.**  
   - Authors: Alorse  
   - Year: 2026  
   - Title: pinescript-strategies  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: `https://github.com/Alorse/pinescript-strategies`  
   - Repo URL: `https://github.com/Alorse/pinescript-strategies`

2. **Alorse. (2026). _Supertrend + EMA rebound [Alorse]_.**  
   - Authors: Alorse  
   - Year: 2026  
   - Title: Supertrend + EMA rebound [Alorse]  
   - Venue: GitHub raw source  
   - DOI: N/A  
   - Readable URL: `https://github.com/Alorse/pinescript-strategies/blob/master/strategies/trend/Supertrend%20%2B%20EMA%20rebound%20%5BAlorse%5D.pine`  
   - Repo URL: `https://raw.githubusercontent.com/Alorse/pinescript-strategies/master/strategies/trend/Supertrend%20%2B%20EMA%20rebound%20%5BAlorse%5D.pine`

3. **Binance. (2026). _USDⓈ-M Futures REST API – Kline/Candlestick Data_.**  
   - Authors: Binance  
   - Year: 2026  
   - Title: Kline/Candlestick Data  
   - Venue: Binance Developers Docs  
   - DOI: N/A  
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`  
   - Repo URL: N/A

## 7. 本轮落地产物
- `scripts/run_quant_digest_alorse_better_entry_rearm_proxy.py`
- `reports/artifacts/quant_digests/2026-03-23_alorse_better_entry_rearm/events.csv`
- `reports/artifacts/quant_digests/2026-03-23_alorse_better_entry_rearm/summary_by_symbol_arm.csv`
- `reports/artifacts/quant_digests/2026-03-23_alorse_better_entry_rearm/summary_equal_weight.csv`
- `reports/artifacts/quant_digests/2026-03-23_alorse_better_entry_rearm/summary_pooled.csv`
- `reports/artifacts/quant_digests/2026-03-23_alorse_better_entry_rearm/meta.json`
