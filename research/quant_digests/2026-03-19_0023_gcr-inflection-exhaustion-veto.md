# 别把 breakout-short 继续做在最后一脚：`extreme sentiment + volume exhaustion + BB edge + divergence`，更像 15m continuation failure veto
- 时间：2026-03-19 00:23 UTC
- 类型：GitHub
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/exhaustion/divergence/volume/bollinger/filter/repo/crypto/15m
- 证据类型：工程经验

## 1. 这次看了什么
这次看的是 **Jermaine Ragsdale (2025), _Trading Strategy Scanners / GCR Inflection Point Scanner_**。它主叙事是 contrarian reversal，但对当前 desk 更值钱的，不是把它整套当反转 alpha，而是把其中一条旁支单独拎出来：**当走势已经走到“情绪极端 + 放量耗尽 + 布林带边缘 + 动量背离”时，别再把 continuation 当默认会延续。**

## 2. 核心结论
- **一句话核心结论：** 对 5m/15m 来说，GCR 更值得先偷成一个 **`不要追最后一脚` 的 failure veto**，而不是单独反转入场系统。
- **一句话说明它怎么证明：** 证据不是论文回测，而是 repo 里把极端区、量能耗尽、BB 边缘和 divergence 明确写成可计算 Pine 条件，足够直接转成最小实验。
- 代码里最有用的三组阈值很清楚：`RSI ≥ 75 / ≤ 25`，`volume > 2.0x MA20`，`exhaustion volume > 2.5x MA20`。
- 信号不是只看超买超卖；它把 **价格极端**（触上/下轨或 pivot 极值）、**crowding**（量能异常）和 **动量分歧**（bullish/bearish divergence）绑在一起，比单独 RSI 更像“末端衰竭”。
- 对我们最贴的读法是：**顺势信号可以继续来自 breakout-short / Fib / EMA / PSAR；GCR 只负责 veto 那些已经太挤、太晚、太容易反抽的入场。**

## 3. 为什么和当前项目有关
- 对 `V3 final-verdict / breakout-short follow-up`：它直接回答“哪些下破不能追”——尤其是已经出现 **oversold + capitulation volume + lower-BB touch + bullish divergence** 的那种尾段。
- 对 `Fibonacci confirmation / retest_hold`：它能把“回踩守住但其实已过热/过冷”的情况单独剔掉，减少把 retest 当成机械触线开仓。
- 对 `EMA / PSAR raw alpha focus`：它不替代趋势骨架，而是给裸趋势一层更便宜的 **entry veto / size-down overlay**。
- 这题比再补一个 trend filter 更值钱，因为三条线这两天已经有不少“允许做”的 gate，**但还缺一个专门处理末端拥挤与反抽风险的 shared 否决层。**

## 4. 可复刻的最小实验
- 研究假设：15m 主信号若在执行前/后 1~3 根 5m 内出现强 opposite-side GCR inflection，则 continuation 胜率和 post-cost 路径会明显变差；把这类单子 veto 或半仓，比继续裸追更划算。
- 一个可计算定义：
  - `bullish_exhaustion_veto_for_shorts = (RSI<=25 or Stoch<=20) & RVOL>2.0 & (volume>2.5*MA20 or bullish_divergence) & low<=BB_lower`
  - `bearish_exhaustion_veto_for_longs = (RSI>=75 or Stoch>=80) & RVOL>2.0 & (volume>2.5*MA20 or bearish_divergence) & high>=BB_upper`
  - 若 `score >= +40`，禁止新开 downside follow-up short；若 `score <= -40`，禁止新开 upside follow-up long。
- 最小回测切口：BTC/ETH/SOL perpetual；15m 生成 breakout/Fib/EMA-PSAR 主信号，5m 作为 veto 执行层；样本先看近 180d。
- 最该先看：`next 4~8 bars continuation return`、`false_break_ratio`、`MAE before 1R`。先看 veto 后是否明显减少“入场后立刻反抽”的坏单。

## 5. 风险与保留意见
- 这是 GitHub 规则仓，不是论文；目前更像 **高价值工程线索**，不是已验证 alpha。
- 它原始用途偏 reversal scanner；若直接拿来反着做，容易和 desk 当前趋势/突破主线打架。所以我建议**只当 veto / size-down，不当主入场。**
- divergence 在实时上常有重绘/回看偏差风险，最好先做两版：`带 divergence` 与 `纯极端+量能版`，别一开始就把最花哨的条件全锁死。
- Crypto 比股票更常出现连续 squeeze 后的单边扩张，所以这个 veto 也可能错杀强趋势；因此要重点比较 **收益下降** 和 **回撤改善** 谁更大。

## 6. 来源
- Jermaine Ragsdale. (2025). *Trading Strategy Scanners* / *GCR Inflection Point Scanner*. GitHub.
- Readable URL: https://github.com/jmragsdale/trading-breakout-scanner
- Repo URL: https://github.com/jmragsdale/trading-breakout-scanner
- Raw Pine URL: https://raw.githubusercontent.com/jmragsdale/trading-breakout-scanner/master/GCR_Strategy_Scanner_TradingView.pine
- README: https://raw.githubusercontent.com/jmragsdale/trading-breakout-scanner/master/README.md
