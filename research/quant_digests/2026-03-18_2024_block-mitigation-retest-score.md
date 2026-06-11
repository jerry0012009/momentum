# 别把 consolidation breakout 后的回踩都当同质量：`block length + mitigation zone`，更像 breakout-short / Fib 的 shared retest quality score
- 时间：2026-03-18 20:24 UTC
- 类型：GitHub
- 主题标签：breakout-short/fibonacci/retest-hold/consolidation/block/mitigation-zone/structure/filter/repo/crypto/15m
- 证据类型：工程经验 + 社区经验/待验证

## 1. 这次看了什么
看了 **saintmexas (2025/2026)** 的 GitHub 仓库 **trading-scripts**，重点是其中两个 Pine 脚本：`Block of Candle` 与 `Range Breakout Candles with Pullback Detection`。它不是再加一个更花的指标，而是把“盘整块 → 突破 → 回踩”的对象链条，写成了可直接拆解的程序规则。

## 2. 核心结论
- 一句话核心结论：**对 15m 来说，先分出“这是从多扎实的盘整块里突破出来的”，往往比继续调 Fib/EMA 的单点阈值更值钱。**
- 这个 repo 最值得偷的不是画盒子，而是把 retest 质量写成了几个便宜、可计算的结构特征：`blockCandleCount`、`blockRange`、`avgBlockVol`、`mitigation zone`。
- `Block of Candle` 代码里，bullish block 只有在 `current_body_min > ref_high` 才算真正向上脱离；bearish 是 `current_body_max < ref_low`。这比 wick 穿线更诚实，更贴合我们当前的 breakout-short / retest_hold 收口口径。
- block 关闭后，脚本会把整段盘整的 `indicator_high ~ indicator_low` 存成 mitigation zone，并给 zone 打上 candles 数量标签；作者还提供了 `minCandlesInBlock=3`、`minBlockRangePercent=0.1`、`volumeSpikeMultiplier=1.5` 这类很便宜的质量过滤器。
- 对 desk 最有价值的旁支想法不是“盘整突破本身”，而是：**别把所有 retest 都当一样；先问“这次是从短小噪音块突破，还是从长时间吸收后的结构块突破”。**
- 一句话证明方式：**不是论文统计，而是可读 Pine 代码把 block close、zone 回踩、volume 过滤和 MTF 对齐都写成了明确规则。**

## 3. 为什么和当前项目有关
这轮值得做，因为它直接服务于两条收口线：
- `V3 breakout-short follow-up`：先筛掉那种只脱离了两三根小噪音块的假 continuation，优先保留“长 block 后破位再回抽失败”的 short。
- `Fibonacci confirmation / retest_hold`：Fib 不是单线，回踩也不是单线；BoC mitigation zone 可以给 Fib 回踩一个“结构厚度”背景。

它也能给 `EMA / PSAR raw alpha focus` 提供一个便宜的结构 veto：EMA/PSAR 方向对，但如果只是薄盘整后的小突破，先别急着把它当 continuation。

## 4. 可复刻的最小实验
**研究假设**：15m crypto 里，来自“更长、更有质量”的 consolidation block 的 breakout/retest，后续 6~12 bars continuation 更稳；而噪音短 block 更容易变成假突破或回踩失守。

**一个可计算定义（最小版）**：
1. 用 BoC 逻辑在 15m 构造 block；记录 `L = blockCandleCount`、`R = blockRangePct`、`V = avgBlockVol / SMA20(volume)`。
2. block 向上关闭后，保存 zone=`[indicator_low, indicator_high]`；向下镜像处理。
3. Long 版：突破后 8 根内第一次回踩 zone 上半区，且收盘重新站回 `zoneHigh`，记为 `retest_hold_pass`。
4. Short 版：跌破后 8 根内第一次回抽 zone 下半区，且收盘重新跌回 `zoneLow` 下方，记为 `breakout_short_follow_pass`。
5. 先只做 3 档分层：`L < 4`、`4 <= L < 8`、`L >= 8`；再看是否需要叠 `V > 1.2` 或 `R > 0.15%`。

**最小回测切口**：
- 标的：BTCUSDT、ETHUSDT、SOLUSDT perpetual
- 周期：15m
- 样本：近 180d
- 执行：next-bar open，持有 6 / 12 bars，成本 6 / 10 / 15 bps per side

**先看 3 个指标**：
1. `target-hit within 12 bars`
2. `failure-before-target`（先失守 zone 另一侧）
3. `trade-count retention`（防止只靠极端砍单“变好看”）

**首轮 A/B**：
- A：现有裸 breakout / Fib retest 规则
- B：A + `L` 分层
- C：B + `V` / `R` 质量过滤

## 5. 风险与保留意见
- 这是小仓库工程规则，不是经过大样本论文验证的 alpha。
- 作者 README 默认更偏 1H–1D；迁到 15m 可能会把 block 切得过碎，所以 first pass 必须先看 trade count 是否崩掉。
- mitigation zone 本质还是结构区，不是自动等于支撑/阻力；若回踩太深，可能已经不是 hold，而是失败。
- repo 星数低、没有正式回测报告；它的价值更像“规则骨架”，不是 ready-made 结论。

## 6. 来源
1. **saintmexas (2025/2026)**, *trading-scripts*, GitHub repository, DOI: N/A  
   - Readable URL: https://github.com/saintmexas/trading-scripts  
   - Repo URL: https://github.com/saintmexas/trading-scripts  
   - Repo metadata: created 2025-11-28, updated 2026-02-26, description = TradingView Pine Script v5 indicators for breakout & consolidation trading (crypto/forex)
2. **saintmexas (2025/2026)**, *Block of Candle*, Pine Script source  
   - Code URL: https://raw.githubusercontent.com/saintmexas/trading-scripts/main/Block-of-Candle
3. **saintmexas (2025/2026)**, *Range Breakout Candles with Pullback Detection*, Pine Script source  
   - Code URL: https://raw.githubusercontent.com/saintmexas/trading-scripts/main/Range%20Breakout%20Candles%20with%20Pullback%20Detection

## 7. 下一步怎么测
先别把整个 repo 搬进来。第一步只加一个最小结构层：**给现有 breakout-short / Fib retest 事件打上 `block length` 和 `zone retest depth` 两个字段**。如果 `L >= 8` 组在保留足够 trade count 的前提下，明显压低 `failure-before-target`，这条线就值得升成 shared retest quality score；否则就留在研究池，不再占用主线预算。
