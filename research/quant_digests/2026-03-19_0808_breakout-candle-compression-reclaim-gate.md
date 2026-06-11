# 别把 retest / follow-up 继续绑在逐根 15m 原始 K 线上：`breakout-candle 压缩流 + pullback→reclaim` 更像 breakout-short / Fib 的 shared confirmation skeleton
- 时间：2026-03-19 08:08 UTC
- 类型：GitHub + 本地快速复核
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/breakout-candle/compression/pullback/reclaim/confirmation/filter/repo/crypto/5m/15m
- 证据类型：repo 代码规则 + 公开行情快检（中等证据）

## 1. 这次看了什么
这轮主看 **saintmexas (2026) 的 `trading-scripts` 仓库**，重点不是 BoC，而是另一个脚本：
`Range Breakout Candles with Pullback Detection`。

它的可迁移点很明确：先把原始 K 线压缩成“只有突破参考高低点才记一根”的 **breakout-candle 结构流**，再在结构流上定义 pullback / reclaim，而不是在每根原始 15m 上直接判定回踩与确认。

## 2. 核心结论
- **一句话核心结论：** 这个思路不太像“新 alpha”，更像给三条收口线共用的结构化确认层；当前更适合先做 **short follow-up**，不建议 long/short 同权硬套。
- **一句话说明它怎么证明：** repo 给了可编程的压缩与 pullback 判定规则；本地用 Binance 15m（BTC/ETH/SOL，各 1500 bars）做快检后，short 侧在 pullback→reclaim 子集里出现“均值改善但分布不稳”，long 侧反而劣化。

快检（3-bar 事件口径）摘要：
1. **Short baseline**：`n=1399`，win3 `47.32%`，avg_ret3 `-0.051%`
2. **Short（pullback→reclaim gate）**：`n=38`，win3 `47.37%`，avg_ret3 `+0.0385%`（相对 baseline +`0.0895%`）
3. **Long（同 gate）**：`n=55`，win3 `41.82%`（低于 baseline `48.33%`），说明当前不适合双向照搬
4. 子样本里改善主要来自 BTC（short reclaim `n=14`，win3 `64.29%`，avg_ret3 `+0.164%`），ETH/SOL 不稳定

## 3. 为什么和当前三条收口线有关
- **V3 breakout-short follow-up**：把“继续追空”改成“结构流里先 pullback，再 reclaim 破回去才允许 follow-up”，能减少末端追击噪音。
- **Fibonacci confirmation / retest_hold**：Fib 回踩可先映射到结构流的 pullback，再用 reclaim 判定“守住”是否成立，比原始逐根 K 线更不抖。
- **EMA / PSAR raw alpha focus**：不改 EMA/PSAR 主触发，只加一层结构确认 gate，角色更像 entry veto / confirmation，而非替代主信号。

## 4. 下一步怎么测（5m/15m 最小实验）
### 4.1 数据与公开性
- 数据源：Binance Futures 公共 K 线（`/fapi/v1/klines`）
- 公开性：公开可得
- 更新频率：5m / 15m
- 首轮样本：BTC/ETH/SOL，滚动 180d（IS）+ 60d（OOS）

### 4.2 最小可复现实验口径
先冻结一个共享结构层（short-only 起步）：
1. 生成 breakout-candle 流：仅当 `high>ref_high` 或 `low<ref_low` 才产出结构 bar；
2. `trend_down`：最近结构 bar 满足 `lower-high + lower-low`；
3. `pullback_short`：下一结构 bar `close > ref_high`；
4. `reclaim_short`：随后结构 bar `close < pullback_bar.low`；
5. 仅当 `trend_down & pullback_short & reclaim_short` 才允许 breakout-short / EMA-PSAR short follow-up。

对照组：
- A：现有 baseline
- B：A + compression reclaim gate（short-only）
- C：B + `size_mult`（按结构 block 长度分档）

先看 3 个指标：
- `post_cost_expectancy`
- `false_follow_ratio`（4 bars 内反向收回）
- `trade_count_retention`

过线建议（相对 A）：
- `false_follow_ratio` 下降 ≥8%
- `trade_count_retention` ≥45%
- `post_cost_expectancy` 不恶化（或提升）

## 5. 风险与保留意见
- 源仓库是指标脚本，不是完整成本后策略；
- 当前快检事件数偏小（尤其 reclaim 子集），跨币分布不稳，存在样本偶然性；
- 结论应定位为“结构确认候选层”，不是已验证可独立上线 alpha；
- 若 OOS 显示仅 BTC 有效，应降级成 BTC 专用 overlay，而非全币统一规则。

## 6. 来源
1. **saintmexas. (2026). _trading-scripts_. GitHub Repository.**
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: <https://github.com/saintmexas/trading-scripts>
   - Repo URL: <https://github.com/saintmexas/trading-scripts>
2. **核心脚本：Range Breakout Candles with Pullback Detection**
   - Readable URL: <https://github.com/saintmexas/trading-scripts/blob/main/Range%20Breakout%20Candles%20with%20Pullback%20Detection>
   - Raw URL: <https://raw.githubusercontent.com/saintmexas/trading-scripts/main/Range%20Breakout%20Candles%20with%20Pullback%20Detection>
3. **本地快速复核（公开行情）**
   - 数据源：Binance Futures Klines API
   - API URL: <https://fapi.binance.com/fapi/v1/klines>
   - 结果文件：
     - `reports/artifacts/literature/tmp_breakout_candle_pullback_quickcheck_15m_1500bars_20260319.csv`
     - `reports/artifacts/literature/tmp_breakout_candle_pullback_reclaim_quickcheck_15m_1500bars_20260319.csv`
