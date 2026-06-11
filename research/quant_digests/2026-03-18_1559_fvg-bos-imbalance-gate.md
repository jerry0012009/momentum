# 别把 FVG 当 15m 万能回踩框：BOS 对齐后的 imbalance retest，才像 breakout-short / Fib / EMA 的 shared continuation gate
- 时间：2026-03-18 15:59 UTC
- 类型：GitHub
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/fvg/imbalance/bos/bias/filter/repo/crypto/15m
- 证据类型：工程经验 / 待验证

## 1. 这次看了什么
这次看的是 `m-marqx/Trade-Sense`（2025，最近在 2026-03-18 仍有更新）的 PineScript 结构工具库。它最有价值的地方，不是再给我们一个“万能 smart money 指标”，而是把几件经常被口水化的结构概念拆成了很短、能冻结的条件：`BOS`、`CHoCH`、`FVG`、`VI`、liquidity sweep、trendline breakout。对我们 desk 当前三条收口线最值得偷的，不是整套结构学叙事，而是其中这条非常朴素的读法：**只有先有顺势 `BOS`，再等 price 回到 displacement 留下的 imbalance zone（FVG / VI）并继续守住，才更像 continuation；不是图上有个 gap 矩形就默认能接。** 翻成人话：FVG 不是“神秘回踩框”，更像是一次已经跑出去的趋势，回头有没有在低效率成交区继续被同方向接住。

## 2. 核心结论
- **一句话核心结论**：对 15m 来说，`FVG` 最值得先测的角色不是独立 alpha，而是 **`BOS-aligned continuation / retest gate`**。
- **一句话证明方式**：这个 repo 直接把关键对象写成了极短代码：`bullish_bos = trend_bullish and close > last_swing_high`；`bullish_fvg = c3.low > c1.high and gap >= min_gap`；`bullish_vi = cur.low > prev.high`。也就是说，它不是“看起来像 imbalance”，而是可回放、可枚举、可做事件研究的布尔事件。
- 对 desk 最值钱的不是再学一个新名词，而是角色分工终于更清楚了：`BOS` 负责回答“有没有继续往顺势方向扩展”，`FVG/VI retest` 负责回答“扩展之后的回头，还是不是在同方向低效率区被接住”。
- 这正好补三条收口线的共同缺口：`breakout-short follow-up` 缺 post-break path 的结构回踩定义；`Fibonacci retest_hold` 缺“回踩到位以后凭什么算 hold”；`EMA / PSAR raw alpha` 缺外部结构确认，不该继续只靠均线给自己投票。
- 如果要回答“为什么这题比继续沿三条线原地小修更值得”，答案是：**因为它不是再开一条新线，而是在三条线都共用的位置上，补一层 shared continuation syntax。**

## 3. 为什么和当前项目有关
- 对 `V3 final-verdict / breakout-short follow-up`：最自然的 short 镜像是——先出现 `bearish BOS`，再看反抽是否只回补到 bearish `FVG/VI` 区间上沿附近，随后重新压回弱侧。这样比“跌破后任意反抽都算 continuation”更诚实，尤其适合回答 `post-break path` 和 `avoid-chop`。
- 对 `Fibonacci confirmation / retest_hold`：Fib 继续回答“回到哪里”，但 `FVG/VI` 能补一句更关键的话：**这次回踩是不是回到了顺势 displacement 的低效率区，而不是已经回到旧平衡中心。** 也就是 `Fib 给位置，imbalance 给成交语义`。
- 对 `EMA / PSAR raw alpha focus`：EMA / PSAR 可以继续做方向或轻触发，但若没有 `BOS + imbalance retest` 这层结构闸门，它们仍容易在拥挤区里来回翻。换句话说，EMA/PSAR 更像 `bias / trigger`，FVG/VI 更像 `continuation acceptance zone`。
- 这也贴合 backlog 当前重点：pullback confirmation、breakout follow-up、EMA 方向层都已经有雏形，但还缺一层“为什么这次回踩比上次更像顺势中继”的共享定义。

## 4. 可复刻的最小实验
- **研究假设**：把 `BOS + FVG/VI retest gate` 接到现有 `breakout_short`、`fib_retest_hold`、`ema_slope_or_psar_trigger` 上，能在不完全砍掉样本的前提下，降低 `4~8 bars` 内假延续 / 假 hold。
- **公开数据源**：Binance perpetual `15m` OHLCV（BTC / ETH / SOL），公开可得；第一轮不需要额外链上或低频宏观数据。
- **最小定义**：
  1. `bullish_bos`: `trend_bullish and close > last_confirmed_swing_high`；short 镜像；
  2. `bullish_fvg`: `low[t] > high[t-2]` 且 gap 宽度 `>= k * ATR14`，先测 `k = 0` 与 `0.1` 两档；
  3. `bullish_vi`: `low[t] > high[t-1]`；把它当更窄、更快的 micro retest zone，对照 FVG；
  4. gate 版本：在原始 setup 出现后，只接受“最近 `N=8` 根内先出现同向 BOS，随后 price 回踩到 `FVG/VI` 区间且收盘仍站在正确一侧”的入场；
  5. 做三臂对照：`base`、`base + BOS only`、`base + BOS + FVG/VI retest`。
- **最小回测切口**：近 `180d`，`15m`，`BTC/ETH/SOL`，统一 `next-bar open`、`no-overlap`、成本先看 `6 / 10 / 15 bps per side`。
- **最先看的 4 个指标**：`post-cost expectancy`、`trade_count retention`、`4~8 bar failure rate`、`positive_asset_ratio`。
- **下一步怎么测**：第一轮不要优化 swing 算法或 gap 阈值，先只回答两个问题——**增量主要来自 BOS，还是来自 retest 到 imbalance zone？VI 这种更窄的 zone 会不会比 FVG 更适合 15m？** 如果 `BOS only` 已经拿走大部分增量，说明 zone 只是包装；如果 `BOS + FVG/VI retest` 还能继续明显压低 failure rate，它才值得进入三条线共用 closure 候选。

## 5. 风险与保留意见
- 这是一个结构工具库，不是带完整 OOS 绩效的学术或生产级策略；我们能继承的是事件骨架，不是收益结论。
- `FVG` / `VI` 这套语言在社区里很热，但过热本身就是风险：如果不加 `BOS`、bias 或最小 gap 过滤，它在 15m 上很容易退化成“把随机跳空盒子画出来”。
- repo 文档里提到 `premium / discount`、HTF bias 等 contextual bias，但当前最适合 desk 的顺序不是一口气全搬，而是先做最小 ablation：`BOS`、`FVG`、`VI` 分开测。
- crypto 24/7 市场里，很多 `VI` 只是局部流动性稀薄，不一定代表可交易的 directional imbalance；所以必须看成本后结果和 retention，而不是只看胜率。

## 6. 来源
- m-marqx. (2025). *Trade-Sense: Universal Market Structure in PineScript.*
  - Venue / DOI：无（GitHub repo）
  - Repo URL: <https://github.com/m-marqx/Trade-Sense>
  - Readable URL: <https://github.com/m-marqx/Trade-Sense/blob/main/README.md>
  - Repo API: <https://api.github.com/repos/m-marqx/Trade-Sense>
  - Repo metadata snapshot: created `2025-09-03`, updated `2026-03-18`, pushed `2025-09-06`, `10` stars at fetch time.
- m-marqx. (2025). *Trade-Sense docs: Event Layer / Bias Layer.*
  - Event docs URL: <https://raw.githubusercontent.com/m-marqx/Trade-Sense/main/docs/events.md>
  - Bias docs URL: <https://raw.githubusercontent.com/m-marqx/Trade-Sense/main/docs/bias_layer.md>
- Key code URLs:
  - BOS: <https://raw.githubusercontent.com/m-marqx/Trade-Sense/main/src/events/bos.pine>
  - FVG: <https://raw.githubusercontent.com/m-marqx/Trade-Sense/main/src/events/fvg.pine>
  - Volume Imbalance: <https://raw.githubusercontent.com/m-marqx/Trade-Sense/main/src/events/volume_imbalance.pine>
