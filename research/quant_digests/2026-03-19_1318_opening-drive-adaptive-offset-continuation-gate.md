# 别把 opening-drive 突破写成“碰到箱体边就追”：`drive-edge + adaptive offset` 更像 breakout-short / Fib / EMA-PSAR 的 continuation-confirmation gate
- 时间：2026-03-19 13:18 UTC
- 类型：GitHub + 本地代理快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/opening-drive/vwap/continuation/confirmation/failure/filter/repo/crypto/15m
- 证据类型：repo 代码规则（工程证据）+ 公开行情代理快检

## 1. 这次看了什么
这轮看的是 **damianpitt / Capital41 (2026) 的 `capital41-indicators`**，重点抽取 `Capital41_Opening_Drive_Playbook.pine` 里一个适合当前 desk 的旁支：
**突破触发不要只看 `drive high/low`，而是加一个自适应偏移：`offset = max(|drive_mid - sessionVWAP|, 0.15 * drive_range)`，只有突破 `drive_edge + offset` 才当 continuation。**

## 2. 核心结论
1. **一句话核心结论**：`adaptive offset` 更像“减少假延续”的确认层，不是直接抬收益的主 alpha。  
2. **一句话证明方式**：repo 给了可直接复现的公式；我用 Binance Futures 公开 15m K 线（BTC/ETH/SOL，约 120 天）做 baseline vs adaptive-offset 代理对照，统一看 breakout 后 4~8 bar 路径。  
3. short 侧（更贴近 `breakout-short follow-up`）从 baseline 到 adaptive-offset：
   - `hold4`：**10.4% -> 16.0%**（+5.6ppt）
   - `fail_back_inside4`：**77.5% -> 69.8%**（-7.7ppt）
   - `win8`：**39.9% -> 42.0%**（+2.1ppt）
4. long 侧（给 Fib/EMA 的回踩确认参考）是“质量提升、速度下降”：
   - `hold4`：**11.4% -> 17.5%**（+6.1ppt）
   - `fail_back_inside4`：**71.0% -> 64.5%**（-6.6ppt）
   - `win8`：**50.6% -> 47.6%**（-3.0ppt）
5. 交易数保留率约 **93.6%~94.3%**：说明它是“轻过滤”，但主要价值在路径质量，不在均值收益立刻变大。

## 3. 为什么和当前三条收口线直接相关
- **V3 final-verdict / breakout-short follow-up**：这条对 short 更友好，能减少“刚破就回箱体”的假延续，适合做 follow-up 前的 admission。  
- **Fibonacci confirmation / retest_hold**：Fib 回踩后若不能穿过 `edge+offset`，更像“还没走出确认段”，可当否决条件。  
- **EMA / PSAR raw alpha focus**：EMA/PSAR 继续负责方向；`adaptive offset` 只负责“是否值得追这一脚 continuation”。

## 4. 下一步怎么测（5m / 15m 最小实验）
### 4.1 数据与公开性
- 数据源：Binance Futures 公共 K 线（`/fapi/v1/klines`）
- 公开性：公开可得
- 更新频率：5m / 15m
- 本轮代理产物：
  - `reports/artifacts/quant_digests/2026-03-19_opening_drive_adaptive_offset_proxy_events.csv`
  - `reports/artifacts/quant_digests/2026-03-19_opening_drive_adaptive_offset_proxy_summary.csv`
  - `reports/artifacts/quant_digests/2026-03-19_opening_drive_adaptive_offset_proxy_summary.json`

### 4.2 最小可复现实验口径（建议）
把三条 archetype 都接一层 `adaptive continuation offset`：
1. 定义基础触发（breakout_short / fib_retest / ema_psar）。
2. 对每次候选 continuation，计算：
   - `edge`（当前结构边界）
   - `offset = max(|mid - sessionVWAP|, 0.15 * range)`
3. 对照三臂：
   - A：baseline（edge 即触发）
   - B：fixed offset（如 `0.15 * range`）
   - C：adaptive offset（本轮主张）
4. 统一执行：`next-bar open + no-overlap + hold 8 bars + 6/10/15 bps per side`。

先看 4 项：`post_cost_expectancy`、`hold4 / fail_back_inside4`、`trade_count_retention`、`time-pocket stability`。

## 5. 风险与保留意见
- 这是事件级代理，不是完整策略回测；
- crypto 24/7 下，“opening-drive”本身需要先冻结 session 定义（UTC/London/NY）才能进主线；
- 当前结果更像“路径质量改善”而非“收益立刻改善”，尤其 long 侧 win8 下滑；
- 若后续成本后收益仍不改善，应把它降级为 short/Fib 专属确认层，不要硬升成全局 gate。

## 6. 来源
1. **damianpitt / Capital41. (2026). _capital41-indicators_.**
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: <https://github.com/damianpitt/capital41-indicators>
   - Repo URL: <https://github.com/damianpitt/capital41-indicators>
2. **关键实现：`Capital41_ Opening Drive Playbook/Capital41_Opening_Drive_Playbook.pine`**
   - Readable URL: <https://github.com/damianpitt/capital41-indicators/blob/main/Capital41_%20Opening%20Drive%20Playbook/Capital41_Opening_Drive_Playbook.pine>
   - Raw URL: <https://raw.githubusercontent.com/damianpitt/capital41-indicators/main/Capital41_%20Opening%20Drive%20Playbook/Capital41_Opening_Drive_Playbook.pine>
   - 关键规则：`contOffset = max(vwapDev, driveRange*0.15)` 与 continuation/fade 双触发线
3. **公开行情数据源**
   - Binance Futures Klines API: <https://fapi.binance.com/fapi/v1/klines>
