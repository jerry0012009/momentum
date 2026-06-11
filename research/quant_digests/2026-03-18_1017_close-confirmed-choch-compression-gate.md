# 别让 wick 把 15m 趋势直接翻面：HTF swing close + CHoCH 确认，更像 breakout-short / Fib / EMA 的 shared failure gate
- 时间：2026-03-18 10:17 UTC
- 类型：GitHub
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/structure/choch/liquidity-sweep/filter/repo/crypto/15m
- 证据类型：仓库规则拆解 + 公开代码可复现实验

## 1. 这次看了什么
这次看的是 Jerome Cornier 在 2026-02 发布的 GitHub 仓库 `jcornierfra/TradingView_Indicator_JCO_Swings_Trend_HTF`。它表面上是 `CHoCH + liquidity sweep + SMC` 风格指标，但对我们 desk 真正值钱的，不是术语包装，而是一个很实用的判断：**别因为一根 wick 刺穿 swing high/low，就把 15m 的方向或结构 gate 立刻翻面；先看 higher-TF pivot close 有没有真正完成 break。**

## 2. 核心结论
- **一句话核心结论**：这份 repo 最值得抄的，不是整套 SMC 词汇，而是 **`close-confirmed CHoCH + no-CHoCH-no-flip`** 这层 shared failure gate：没有收盘确认的结构破坏，宁可先当 `compression / unclear`，不要急着把趋势翻向。
- **一句话证明方式**：作者不是靠主观画图，而是把规则写死在代码里——默认用 **最近 3 组 swing highs/lows** 定义结构、用 **HTF=60m**、`Swing Period=5` 找 pivot，并明确要求 `pivot candle close` 真正突破前一 swing 水平，才接受 CHoCH reversal。
- 对 bullish / bearish 的判断也很适合 desk 读法：上涨不只看新高，而先看 **higher lows**；下跌不只看新低，而先看 **lower highs**。这和我们当前三条收口线都更接近，因为它关心的是“结构有没有被接受”，不是“线有没有被碰到”。
- 最关键的一条是 **trend reversal gating**：如果 raw trend 看起来翻了，但没有 CHoCH close-confirm，repo 不会直接认新方向，而是先维持前方向的 `Compression`，只有当更大结构也失效时才降到 `Unclear`。这正好对应我们 15m 上最常见的假动作：**先被 wick 吓翻，再被主趋势打脸。**
- repo 还把 `liquidity sweep` 和真实 reversal 分开：如果双向 CHoCH 同时出现，却最终还是回到前趋势方向，作者把它记成 **liquidity sweep / 假破流动性**，不是反转成立。这对 `breakout-short follow-up` 特别重要，因为很多失败空头不是没破位，而是 **只破了 stop，不破 acceptance**。

## 3. 为什么和当前项目有关
这题现在值得先做，不是因为我们缺一个新花样，而是因为最近几篇 digest 已经在补 `session`、`VWAP`、`flow`、`participation` 这些过滤层；下一个最自然、也最贴三条收口线的缺口，就是：**价格到底是“真翻了”，还是只是 wick 把人甩下车。**
- 对 `V3 final-verdict / breakout-short follow-up`：最直接的用法就是 **short 侧别因一根 low break 就默认 continuation**。如果 1h swing low 被刺穿，但没有 close-confirmed bearish CHoCH，甚至随后回到前结构内，更诚实的读法应是 `compression / sweep`，而不是继续加码 short。
- 对 `Fibonacci confirmation / retest_hold`：Fib 位本来就只是位置。若回踩后虽然摸破前低，但 higher-TF close 没有确认跌破，反而更像 **retest_hold 仍有效**；反过来，若真出现 bearish CHoCH close break，再好的 Fib 位也不该硬接。
- 对 `EMA / PSAR raw alpha focus`：它提供的是一个比“再叠一条均线”更健康的结构 gate。EMA / PSAR 给方向，HTF close-confirmed structure 只回答：**这次翻向是不是被更高一级结构真正接受了。**

## 4. 可复刻的最小实验
- **研究假设**：给现有 `breakout-short / Fib retest_hold / EMA-PSAR` 加一层 `1h close-confirmed CHoCH / compression gate` 后，`2~4 bar` 的假突破、假回踩和过早翻向会下降，成本后表现更稳。
- **公开数据源**：只需要现有交易所公开 `15m OHLCV`；把同一份数据重采样成 `1h` 即可，不依赖额外付费数据。
- **最小可计算定义**：
  1. 用 `1h` 重采样 bars 计算 swing pivots（先按 repo 的 `Swing Period=5` 试）；
  2. trend 只用 pivot candle `close` 序列判断 `higher lows / lower highs`；
  3. `bullish CHoCH` = 新高突破前高，且 pivot close 真站上去；`bearish CHoCH` 反之；
  4. 若 raw trend 翻向但无 CHoCH close confirm，则标为 `compression`，不立刻翻方向；
  5. 若先破 swing、后又回到前方向结构内，则记为 `liquidity sweep veto`。
- **第一轮 bucket**：
  1. `base`：现有原始 setup；
  2. `+ htf_close_trend_gate`：只允许更高一级 close-based trend 同向；
  3. `+ no-choch-no-flip`：无 close-confirm CHoCH 时不接受趋势翻转；
  4. `+ liquidity_sweep_veto`：若出现 sweep recovery / sweep rejection，禁做逆 sweep 方向的 entry。
- **最先看的 4 个指标**：`2/4 bar fail rate`、`false-break / false-hold rate`、`post-cost expectancy @ 6/10/15 bps per side`、`trade count retention`。
- **下一步怎么测**：先别一次铺满全策略。就拿 `BTC / ETH / SOL` 最近 `120~365` 天 `15m`，把 `1h CHoCH/compression gate` 压到三条现有 base archetype 上，只问一个问题——**close-confirmed HTF structure 能不能比 wick-only 结构，稳定减少 15m 的过早翻向？** 如果能，它就值得升格成 shared failure gate；如果只是砍样本、不改善 pocket，就把它留在 evidence pool。

## 5. 风险与保留意见
- repo 很新，当前只有 **1 star / 0 forks**，社会证明很弱；我们继承的是它的规则骨架，不是它的权威性。
- 这类 pivot / swing 逻辑天然有确认滞后；如果实现时把未确认 pivot 偷渡进信号，会立刻产生 lookahead。第一轮必须统一成 **pivot 确认后 next-bar open**。
- `Compression` 很容易被滥用成“什么都能解释”；因此回测里必须把 `compression` 单独当 bucket，别和 trend continuation 混在一起。
- 这条线和 `chanlun structural reclaim` 有邻近关系，但焦点不同：前者更偏回抽后的形态确认，这次更偏 **wick vs close acceptance / reversal gating**。如果实验结果高度重合，就别重复保留两层近义 gate。

## 6. 来源
- Jerome Cornier. (2026). *JCO Swings Trend HTF*. GitHub repository.
  - Venue / DOI：GitHub / N/A
  - Repo URL: <https://github.com/jcornierfra/TradingView_Indicator_JCO_Swings_Trend_HTF>
  - Readable URL: <https://github.com/jcornierfra/TradingView_Indicator_JCO_Swings_Trend_HTF>
  - Raw README: <https://raw.githubusercontent.com/jcornierfra/TradingView_Indicator_JCO_Swings_Trend_HTF/main/README.md>
  - Raw script: <https://raw.githubusercontent.com/jcornierfra/TradingView_Indicator_JCO_Swings_Trend_HTF/main/Indicator_JCO_Swings_Trend_HTF.pine>
  - Repo API: <https://api.github.com/repos/jcornierfra/TradingView_Indicator_JCO_Swings_Trend_HTF>
  - Repo metadata snapshot: created `2026-02-05`, updated `2026-02-26`, `1` star, `0` forks.
