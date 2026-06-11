# 别把 `retest_hold` 只看成“当前回踩到哪”：`DeepestRetracement%` 更像 15m 的 honest hold-quality gate
- 时间：2026-03-20 15:57 UTC
- 类型：GitHub 仓库 + Binance 公共数据快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/retracement/deepest-retracement/hold-quality/path-memory/filter/repo/crypto/15m
- 证据类型：工程证据（高信号公开仓库）+ 公开行情代理快检

## 1) 这次看了什么
主看 **joshyattridge (2023-) 的 `smart-money-concepts`**。这次不拿它最显眼的 BOS / CHoCH 当主角，而是抽一个更适合当前 desk 的旁支：`smc.retracements()` 不只返回 **CurrentRetracement%**，还额外追踪 **DeepestRetracement%** —— 也就是这段回踩过程中“最深曾经扎到哪”。

## 2) 核心结论（先说人话）
- **一句话核心结论：** 对 15m 的 `Fib confirmation / retest_hold`，只看“现在收在哪”不够诚实；很多看起来还站得住的回踩，中途其实已经扎得很深，`DeepestRetracement%` 更像真正的 hold-quality 读数。  
- **一句话证明方式：** repo 直接把“当前回撤”和“本段最深回撤”拆开计算，而且代码里还专门做了 **1 bar shift**，避免把当根未确认信息偷看进来。
- 公开数据代理快检（BTC/ETH/SOL 永续，15m，近 120d，20-bar breakout 后 12 bar 内 retest+reclaim proxy）显示，这不是形式主义：
  - 共抓到 **684** 个 reclaim 事件；
  - `Deepest - Current` 的回撤差中位数约 **12.6 个百分点**，75 分位约 **21.1**；
  - **25.3%** 的事件会因为看 `deepest` 而落入**不同的 Fib 深度桶**；
  - 即使当前回踩看起来还 `<=61.8%`，仍有 **5.3%** 的事件中途其实已经 **扎穿 61.8%**。

## 3) 为什么这轮比继续找别的旁题更值得做
它不是游离题，反而正好补三条收口线里一个共同盲点：**路径上的最差一脚**。
- **Fib retest_hold（最直接）**：先解决“守住了没有，到底按当前 close 算，还是按中途最深下探算”。
- **V3 breakout-short follow-up**：break 后的反抽若中途已经明显越界，再回到 level 下方，不应被当成同质量 continuation。
- **EMA / PSAR raw alpha**：EMA/PSAR 本来就容易被单次回抽打脸；`deepest excursion` 很适合做外置 veto / size-down 层，而不是继续把 raw signal 写成二元开关。

## 4) 怎么映射到 15m 当前框架
对任一候选 setup，先保留你现有的 anchor（例如 confirmed extremum Fib anchor、broken level、EMA bounce anchor），然后新增：
- `current_retracement_pct`：当前 bar 的回踩深度；
- `deepest_retracement_pct`：自 setup 启动以来、到当前确认 bar 为止的最深回踩深度。

落地建议：
- **Fib retest_hold**：`current <= 50` 但 `deepest > 61.8` 的事件，直接降级为 weak hold / no-trade；
- **breakout-short follow-up**：若反抽中 `deepest` 已明显穿回 body-defined failure zone，再次转弱也只算二次机会，不算同质量 initial continuation；
- **EMA / PSAR**：把 `deepest / ATR` 做成 risk overlay，优先 veto “close 看起来还行、但中途已经失真”的 continuation。

## 5) 最小可复现实验（公开可得）
**数据源**：Binance USDⓈ-M Futures 15m K 线，公开可得，分钟级更新。  
**实验 A（先做）**：
1. 沿用现有 `fib_retest_long` 或 `breakout follow-up` baseline；
2. 对每个信号同时记录 `current_retracement_pct` 与 `deepest_retracement_pct`；
3. 做 A/B：
   - A 组：只按 `current` 判是否 hold；
   - B 组：加入 `deepest` honesty gate（如 `deepest <= 61.8` 或 `deepest <= 0.75 ATR beyond level`）。
4. 先看 4 个指标：`post_cost_expectancy`、`failure-before-target`、`trade_count_retention`、`false-hold rate`。

**实验 B（最小网格）**：
- 深度阈值先只测三档：`50 / 61.8 / 79`；
- 确认窗先只测两档：`6 bars / 12 bars`；
- 若只有单点有效，不升级为默认 shared gate。

## 6) 风险与保留
- 这是 repo 规则 + proxy 证据，不是已发表论文结论。  
- 本轮快检里的 reclaim proxy 天生会让 `current retracement` 偏浅，所以 `deepest` 的价值更像**诚实校正层**，不是单独 alpha。  
- 若 `deepest` 规则把交易数打得太低，它可能只是另一个过严 gate；所以必须同时盯 `trade_count_retention`。

## 7) 产物与留痕
- 代理事件明细：`reports/artifacts/quant_digests/deepest_retracement_proxy/events.csv`
- 代理摘要：`reports/artifacts/quant_digests/deepest_retracement_proxy/summary.json`

## 8) 来源
1. **joshyattridge. (2023-2026). _smart-money-concepts_. GitHub Repository.**  
   - Authors: Josh Yattridge  
   - Year: 2023-2026  
   - Title: smart-money-concepts  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: <https://github.com/joshyattridge/smart-money-concepts>  
   - Repo URL: <https://github.com/joshyattridge/smart-money-concepts>  
   - Notes: MIT License；截至本轮抓取约 **1403 stars**；仓库创建于 2023-09-21，最近页面更新时间 2026-03-20。
2. **joshyattridge. (2023-2026). _README.md / Retracements API_.**  
   - Readable URL: <https://github.com/joshyattridge/smart-money-concepts/blob/master/README.md>
3. **joshyattridge. (2023-2026). _smartmoneyconcepts/smc.py_ (`retracements`).**  
   - Readable URL: <https://github.com/joshyattridge/smart-money-concepts/blob/master/smartmoneyconcepts/smc.py>
   - Raw URL: <https://raw.githubusercontent.com/joshyattridge/smart-money-concepts/master/smartmoneyconcepts/smc.py>
4. **Binance. (2026). _USDⓈ-M Futures API — Kline/Candlestick Data_.**  
   - Readable URL: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data>

## 9) 下一步怎么测（一句话）
先在 `Fib retest_hold` 上做一版最小 honesty A/B：同一批信号只改一个条件——从“只看当前回踩”改成“当前回踩 + deepest 回踩不过阈值”，如果成本后收益和 false-hold rate 同时改善，再把它推广到 breakout-short / EMA-PSAR 的 shared veto 层。