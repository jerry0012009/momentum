# 别把 `higher-low pressure ladder` 当 breakout 前硬门：它更像 15m `retest_hold` 的上下文特征，不是独立入场键
- 时间：2026-03-19 23:29 UTC
- 类型：GitHub + 本地代理快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/higher-low/pressure-ladder/retest/candle-quality/confirmation/filter/repo/crypto/15m
- 证据类型：工程证据（仓库源码）+ 代理快检（公开行情）

## 1. 这次看了什么
主来源是 GitHub 仓库 **wwakeford/breakout-retest-backtest (2025)**。它把“横向阻力突破 → 回踩 → 再入场”拆成了可复刻模块，尤其强调三件事：`HigherLowsPattern`（突破前抬低点结构）、`ResistanceLevel`（多次触碰后的水平位）、`is_valid_retracement`（回踩时小实体 + 低量）。

## 2. 核心结论
- **一句话核心结论**：`higher-low pressure ladder` 不适合直接当 15m breakout 的硬放行键；更像一个“上下文特征”，要和回踩 K 线质量（small-body hold）组合后才有价值。
- **一句话证明方式**：仓库代码把 `higher-lows` 与 `volume/retracement` 明确分层；本地 15m 代理快检（BTC/ETH/SOL、近 120 天）显示“仅靠 ladder”信号不稳定，但在 `small-body retest` 子集里表现明显改善。
- 代理快检关键读数（15m，Binance 永续，forward=4 bars）：
  1) **Raw breakout long**：`ladder=1` 的中位数约 **-5.96 bps**，优于 `ladder=0` 的 **-9.27 bps**，但 fail rate 并未改善（54.06% vs 52.30%）。
  2) **Retest 子集**：`ladder=1` vs `ladder=0` 的中位数几乎打平（**-3.14 bps** vs **-3.46 bps**），但 fail rate 更高（52.36% vs 48.99%）。
  3) **交互项（关键）**：在 retest 样本中，`ladder=1 + small-body` 中位数约 **+1.09 bps**；`ladder=1 + 非small-body` 约 **-6.71 bps**。这说明 ladder 需要“回踩质量”配合才更像可用信息。

## 3. 为什么和当前项目有关
这轮不是开新坑，而是继续给三条收口线做“确认层收敛”：
- `V3 final-verdict / breakout-short follow-up`：当上破前已出现 `higher-low ladder`，不应机械追空回落；更适合作为 **short-veto / size-down** 的先验特征。
- `Fibonacci confirmation / retest_hold`：`ladder` 可作为回踩背景分层（prior），但最终是否放行仍应由 `retest body quality + hold` 决定。
- `EMA / PSAR raw alpha focus`：把 `ladder` 放到过滤/打分层，而不是直接和 EMA/PSAR 并列触发，可减少“多规则同层抢权”。

## 4. 可复刻的最小实验
### 研究假设
在 15m 上，`pre-break higher-low ladder` 作为上下文特征（而非硬门）+ `retest candle quality` 组合，优于“只用 ladder 放行”的二元规则。

### 一个可计算定义
- `ladder_score`：突破前 16 bars 内 swing low 连续抬高步数（`>=2` 记为 1，否则 0）。
- `retest_quality`：回踩 K 线满足 `close >= level` 且 `body_ratio <= 0.30`。
- 放行建议（最小版）：
  - 不再使用 `ladder==1` 直接入场；
  - 改为 `entry_score = 0.6 * retest_quality + 0.4 * ladder_score`；
  - `entry_score >= 0.8` 才放行（即必须有 quality，ladder 只加分）。

### 最小回测切口
- 资产：BTC/ETH/SOL perp
- 周期：15m
- 样本：近 120 天滚动
- 成本：`6/10 bps per side`
- 对照组：
  1) baseline（现有 retest_hold）
  2) baseline + `ladder` 硬门
  3) baseline + `ladder` 打分特征（本轮建议）

### 最先看 3 个指标
1. `post_cost_return`
2. `false_follow_through_4bars`
3. `left_tail_pnl_p5`（或 `max_drawdown`）

## 5. 风险与保留意见
- 该仓库是教学/工程实现风格，非审稿论文；证据强度来自“可读代码 + 本地复核”，不是学术显著性检验。
- 本轮快检是代理实验，不能替代完整策略回测与 OOS。
- 结论偏“结构角色判断”：`ladder` 当前更像 context feature，不是 standalone alpha。后续应继续做参数邻域与多市场稳健性检查。

## 6. 来源
1. wwakeford. (2025). *breakout-retest-backtest*. GitHub Repository.  
   - Authors: wwakeford  
   - Year: 2025  
   - Title: breakout-retest-backtest  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: https://raw.githubusercontent.com/wwakeford/breakout-retest-backtest/main/README.md  
   - Repo URL: https://github.com/wwakeford/breakout-retest-backtest
2. wwakeford. (2025). *strategy.py / indicators.py* (HigherLowsPattern, ResistanceLevel, retracement validation).  
   - Authors: wwakeford  
   - Year: 2025  
   - Title: Strategy implementation files  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: https://raw.githubusercontent.com/wwakeford/breakout-retest-backtest/main/strategy.py  
   - Repo URL: https://github.com/wwakeford/breakout-retest-backtest
3. Binance Developers. (2026). *USDⓈ-M Futures REST API — Kline/Candlestick Data*.  
   - Authors: Binance  
   - Year: 2026  
   - Title: Kline/Candlestick Data API  
   - Venue: Binance Developers  
   - DOI: N/A  
   - Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data  
   - Repo URL: N/A

---
### 附：本轮代理快检产物
- `reports/artifacts/quant_digests/prebreak_higher_low_pressure_ladder_proxy_20260319/raw_summary.csv`
- `reports/artifacts/quant_digests/prebreak_higher_low_pressure_ladder_proxy_20260319/retest_summary.csv`
- `reports/artifacts/quant_digests/prebreak_higher_low_pressure_ladder_proxy_20260319/retest_smallbody_interaction.csv`
- `reports/artifacts/quant_digests/prebreak_higher_low_pressure_ladder_proxy_20260319/meta.json`
