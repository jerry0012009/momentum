# 别把 stop 后重试写成“同根再给一次机会”：`same-parent SL cooldown` 更像 breakout-short / Fib / EMA-PSAR 的 execution veto 层
- 时间：2026-03-19 12:13 UTC
- 类型：GitHub + 本地代理快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/stopout/cooldown/reentry/execution/risk-overlay/repo/crypto/5m/15m
- 证据类型：repo 代码规则（工程证据）+ 公开行情代理快检

## 1. 这次看了什么
这轮看的是 **DNA Fund (2026) 的 `dna-trading-bot`**。我没复刻它整套多策略框架，而是只抽一条更适合当前 desk 的旁支：
**“同一根（同一父级时间桶）刚被止损，不要立刻再进”**。

仓库里是显式实现：
- `register_sl_cooldown()` 记录止损发生 candle；
- 后续信号检测时若还是同一 candle，直接 `skip re-entry`。

## 2. 核心结论
1. **一句话核心结论**：`same-parent SL cooldown` 是一个值得保留的“诚实执行闸门”，但在 15m 主线里更像**低频保险丝**，不是会单独抬收益的大 alpha。  
2. **一句话证明方式**：repo 里有明确状态逻辑（止损后同 candle 禁止再进），我用 Binance 公开 5m K 线做了 15m 父桶代理快检，结果显示“同父桶 stop→重试”事件本身占比很低。  
3. 本地代理快检（BTC/ETH/SOL，120 天，5m 执行+15m 趋势过滤，6bps/side）里：
   - BTC：`3 / 506` 次 stopout 出现同父桶重试；
   - ETH：`4 / 464`；
   - SOL：`1 / 463`；
   合计 **8 / 1433 ≈ 0.56% stopout**。说明这条 gate 在当前口径下“方向正确但触发稀少”。
4. 成本后总收益（代理口径）对比：
   - BTC：`-86.14% -> -84.40%`（+1.74pct）
   - ETH：`-80.10% -> -80.32%`（-0.22pct）
   - SOL：`-76.62% -> -72.15%`（+4.47pct）
   改善不稳定，且主要不是靠大量拦截交易实现。

## 3. 为什么和当前三条收口线直接相关
- **V3 final-verdict / breakout-short follow-up**：这条最适合放在“破位后路径判决”的最后一层，避免刚被打脸就同根再追。
- **Fibonacci confirmation / retest_hold**：当 retest 失败触发 stop，先禁止同父桶内立即反复尝试，可减少噪声回补。
- **EMA / PSAR raw alpha focus**：EMA/PSAR 继续负责方向；这层只做 execution veto，角色是“防抖”，不是替代入场逻辑。

## 4. 下一步怎么测（5m / 15m 最小实验）
### 4.1 数据与公开性
- 数据源：Binance Futures 公共 K 线（`/fapi/v1/klines`）
- 公开性：公开可得
- 更新频率：5m / 15m
- 当前快检产物：
  - `reports/artifacts/quant_digests/2026-03-19_same_parent_sl_cooldown_proxy.csv`
  - `reports/artifacts/quant_digests/2026-03-19_same_parent_sl_cooldown_proxy.json`

### 4.2 最小可复现实验口径（建议）
在三条 archetype（breakout-short / fib_retest / ema_psar）上统一做 4 臂：
1. `baseline`（无 cooldown）
2. `same-parent cooldown`（本轮规则）
3. `next-parent cooldown`（stop 后至少等下一个 15m 父桶）
4. `conditional cooldown`（仅当 stop 前后出现 wick rejection/高噪声条件时启用）

统一执行：`next-bar open + no-overlap + 6/10/15 bps per side`。  
先看 3 项：`post_cost_expectancy`、`2~4 bar whipsaw rate`、`trade_count_retention`。

## 5. 风险与保留意见
- 本轮快检是代理实验，不是对 `dna-trading-bot` 全策略复刻；
- 在当前 5m->15m 口径下，同父桶 stop→重试事件太少，导致统计不够“有力”；
- 若下一轮 `next-parent cooldown` 也不显著改善，应把这条线降级为“可选执行保险丝”，避免继续占主资源。

## 6. 来源
1. **DNA Fund. (2026). _dna-trading-bot_.**
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: <https://github.com/dnafund/dna-trading-bot>
   - Repo URL: <https://github.com/dnafund/dna-trading-bot>
2. **关键实现：`src/trading/strategy/signal_detector.py`（SL cooldown 注册与同 candle re-entry 跳过）**
   - Readable URL: <https://github.com/dnafund/dna-trading-bot/blob/master/src/trading/strategy/signal_detector.py>
   - 参考片段：`register_sl_cooldown` 与 `SL cooldown active ... skipping re-entry`
3. **关键实现：`src/trading/bot.py`（止损后注册 cooldown）**
   - Readable URL: <https://github.com/dnafund/dna-trading-bot/blob/master/src/trading/bot.py>
   - 参考片段：`Register SL cooldown for positions that were just stopped out`
4. **公开行情数据源**
   - Binance Futures Klines API: <https://fapi.binance.com/fapi/v1/klines>