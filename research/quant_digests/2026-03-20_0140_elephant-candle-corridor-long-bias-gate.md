# 别把大实体确认 bar 写成多空对称：`elephant candle corridor` 在 15m 更像 Fib retest / EMA continuation 的 long-side bounce gate，不是 breakout-short 的 shared follow-up 键
- 时间：2026-03-20 01:40 UTC
- 类型：GitHub + 本地代理快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/candle-quality/atr/volatility-expansion/long-bias/confirmation/filter/repo/crypto/15m
- 证据类型：工程证据（仓库源码）+ 公开行情代理快检

## 1. 这次看了什么
这轮主看新仓库 **Timo Anttila / `trading-engulfing` (2025)**。它的核心不是“engulfing 图形”本身，而是一个更适合我们 desk 偷出来单独测的旁支规则：**确认 bar 既要够强，又不能强到过热**。源码把这件事压成一条很具体的 `elephant candle corridor`：`body_ratio>=50%`、`body > prev_range`、`body > 0.8 ATR`、同时 `full_range < 3.5 ATR`，再叠 `0.15 ATR` 的 breakout buffer 与 `20/200 SMA` 趋势背景。

## 2. 核心结论
- **一句话核心结论**：`elephant candle corridor` 目前更像 **Fib retest / EMA continuation 的 long-side bounce-quality gate**；不适合直接升成 `breakout-short` 的共享 follow-up 键。
- **一句话它怎么证明**：repo 给了可编程的“强但不过热”确认 bar 骨架；我在 Binance Futures `BTC/ETH/SOL 15m` 最近 `120d` 上，用 `next-bar open -> 持有4 bars -> round-trip 12bps` 的最小代理，比较 `base breakout`、`expansion floor`、`elephant corridor` 三档。
- 聚合结果（`n=1053`）里，`elephant corridor` 比 base 稍好，但没有把事件整体救正：
  - `all_base`: `n=1053`，`net12_mean≈-13.69 bps/笔`
  - `elephant_corridor`: `n=556`，`net12_mean≈-11.68 bps/笔`
- 真正明显的地方在 **long 侧**：
  - `long_base`: `n=580`，`net12_mean≈-14.59 bps`，`win≈33.97%`
  - `long_elephant_corridor`: `n=308`，`net12_mean≈-8.59 bps`，`win≈38.96%`
- 但对当前最敏感的 **breakout-short follow-up**，这条线反而不诚实：
  - `short_base`: `n=473`，`net12_mean≈-12.59 bps`
  - `short_elephant_corridor`: `n=248`，`net12_mean≈-15.52 bps`
- 所以 desk 读法不该是“以后只做大实体确认 bar”，而该是：**把“强但不过热”的 candle corridor 留给 long-side reclaim / continuation；short follow-up 先别偷用。**

## 3. 为什么和当前项目有关
- **`Fibonacci confirmation / retest_hold`**：这是最直接受益线。Fib 现在缺的不是再多一根线，而是 **reclaim 那根 bar 到底算不算“真反攻”**。`elephant corridor` 正好能把“够强、但不是过热追价”写成明确门槛。
- **`EMA / PSAR raw alpha focus`**：它更像 `EMA continuation long` 的 admission gate。EMA/PSAR 继续给方向，`elephant corridor` 只回答“这根继续 bar 的质量够不够”。
- **`V3 final-verdict / breakout-short follow-up`**：这轮同样有价值，因为它在阻止我们继续把一个 long-biased 质量门，误包装成 short 侧共享确认键。

## 4. 可复刻的最小实验
- **研究假设**：在 `15m`，`elephant corridor` 更适合作为 `Fib reclaim long / EMA continuation long` 的确认层，而不是 `breakout-short` 的共享 gate。
- **一个可计算定义**：
  - `body_ratio = abs(close-open)/(high-low) >= 0.50`
  - `body > prev_bar_range`
  - `body > 0.8 * ATR14`
  - `high-low < 3.5 * ATR14`
- **最小回测切口**：
  1. `fib_retest_long`：保留现有 `0.5/0.618` 触位与 reclaim 定义，只在 reclaim bar 额外加 `elephant corridor`；
  2. `ema_cont_long`：保留现有 `EMA` 方向与 trigger，只在 trigger bar 额外加 `elephant corridor`；
  3. `breakout_short`：只做对照，不默认接入。
- **首轮只比三臂**：`baseline / body-only(>=50%) / full corridor`。
- **最先看 3 个指标**：`post_cost_return`、`fail_back_inside_4bars`、`trade_count_retention`。

## 5. 风险与保留意见
- 这不是论文，是一个 **很新的 GitHub repo**（当前 social proof 很弱，`0 stars`），所以证据上限来自“规则清楚 + 可快检”，不是学术稳健性。
- 本轮代理只看 `4-bar` continuation，不是完整持仓生命周期；更像在测 **确认 bar 质量**，不是完整策略。
- 当前信号仍全部为负，说明它不是“新 alpha”。最诚实的定位仍是 **long-side confirmation candidate**，不是独立引擎。
- 由于 short 侧结果更差，后续若有人想把它偷渡成 `breakout-short` admission，应该先过一次窄口 clean replication，而不是默认共享。

## 6. 来源
1. Anttila, T. (2025). *Engulfing Breakouts (BigE)*. GitHub repository.  
   - Authors: Timo Anttila / Tuspe Design Oy  
   - Year: 2025  
   - Title: Engulfing Breakouts  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: <https://github.com/timoanttila/trading-engulfing>  
   - Raw Script URL: <https://raw.githubusercontent.com/timoanttila/trading-engulfing/master/EngulfingBreakouts.pine>  
   - Repo URL: <https://github.com/timoanttila/trading-engulfing>
2. Binance Developers. (2026). *USDⓈ-M Futures REST API — Kline/Candlestick Data*.  
   - Authors: Binance  
   - Year: 2026  
   - Title: Kline/Candlestick Data API  
   - Venue: Binance Developers  
   - DOI: N/A  
   - Readable URL: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data>
3. 本轮代理快检产物  
   - `reports/artifacts/quant_digests/elephant_corridor_breakout_proxy_20260320/events.csv`  
   - `reports/artifacts/quant_digests/elephant_corridor_breakout_proxy_20260320/summary.csv`  
   - `reports/artifacts/quant_digests/elephant_corridor_breakout_proxy_20260320/asset_side_summary.csv`  
   - `reports/artifacts/quant_digests/elephant_corridor_breakout_proxy_20260320/meta.json`
