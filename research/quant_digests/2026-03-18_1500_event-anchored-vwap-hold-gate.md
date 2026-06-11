# 别把 VWAP 只锚在 session：对 15m 来说，event-anchored VWAP 更像 breakout-short / Fib / EMA 的 shared hold-reclaim spine
- 时间：2026-03-18 15:00 UTC
- 类型：GitHub
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/anchored-vwap/event-anchor/hold-reclaim/repo/crypto/15m
- 证据类型：工程经验 / 待验证

## 1. 这次看了什么
这次看的是两个 Anchored VWAP 开源实现：`s-kust/anchored_vwaps`（2024）和 `ShabbirHasan1/Anchored_Volume_Weighted_Average_Price`（2025）。前者把 **anchor date 列表 + 从锚点开始累积的 VWAP 曲线** 写成了清楚的 Python 骨架，后者进一步把 `年初 / 最近低点 / 最近高点` 三条 anchored VWAP，外加 `0.5 ATR` 距离条件，直接写成了 Bullish / Bearish / Long / Short 规则。对我们 desk 真正值钱的，不是照搬它们的股票语境，而是把 VWAP 从“按天切 session 的公平价”改成“围绕某个事件重新计算的持仓成本线”。翻成人话：**对 24/7 的 15m crypto，更该问的是“突破/回踩/摆点之后，谁的平均成本线被守住了”，而不是死守 session 边界。**

## 2. 核心结论
- **一句话核心结论**：如果当前三条收口线都在反复纠结“回踩到底算不算守住”，那比继续把 session VWAP 当唯一公平价更值得先测的，是 **event-anchored VWAP hold / reclaim**。
- **一句话证明方式**：两个 repo 都把规则写成了可复用代码——核心是从指定 anchor 时刻开始，计算 `A_VWAP = cumsum(Typical*Volume) / cumsum(Volume)`；第二个 repo 甚至直接用 `last_close` 相对 `年初 / 最近低点 / 最近高点` 三条 anchored VWAP 的位置，再加 `0.5 ATR` 距离，生成趋势与 Long/Short 条件。
- 最值得复用的不是它们的股票 ticker 列表，而是 **“锚点是事件，不是时钟”** 这句话。session VWAP 更像全天平均成本；event-anchored VWAP 更像某一段新仓位从哪里开始堆出来。
- 这正好补三条线的共同缺口：`breakout-short follow-up` 要知道跌破后反抽有没有重新站回那段抛压成本线；`Fib retest_hold` 要知道回踩后是不是还守在“这段趋势资金的均价”上；`EMA / PSAR` 则需要一个不完全自指的成交量加权支撑线。
- 如果要回答“为什么它比继续帮三条线收口更值得”，答案很简单：**因为 24/7 crypto 里 session 切法天然任意，而 event anchor 更贴我们真正关心的交易对象——那一段 breakout / retest / continuation 仓位。**

## 3. 为什么和当前项目有关
- 对 `V3 final-verdict / breakout-short follow-up`：short 侧最怕的是跌破后一拉就收回。比只看 session VWAP 更细的写法，是把 AVWAP 锚在 **breakdown 确认 bar** 或最近确认 swing high；若后续反抽重新站回该 AVWAP 上方，short continuation 就更像失效，而不是“还可以再等等”。
- 对 `Fibonacci confirmation / retest_hold`：Fib 负责回答“回到哪一段价位”，event-anchored VWAP 负责回答“回到这里以后，趋势资金的平均成本线还在不在脚下”。也就是：**Fib 给位置，AVWAP 给持仓成本结构。**
- 对 `EMA / PSAR raw alpha focus`：EMA / PSAR 继续做方向或结构锚，但 AVWAP 能补一个 volume-weighted 的 hold/reclaim spine，避免整套 continuation 只围着均线自转。
- 和今天早些时候的 session VWAP digest 不同，这里不是按日内时钟切，而是按 **事件** 切。对 crypto 来说，这个差异不小：session VWAP 解决“今天的平均成本”，event AVWAP 更像解决“这次 breakout / retest 以来的新库存成本”。

## 4. 可复刻的最小实验
- **研究假设**：把 `event_anchored_vwap` 接到现有 `breakout_short`、`fib_retest_hold`、`ema_slope_continuation` 上，比 `session VWAP` 更能识别真假 hold / reclaim，并减少 `4~8 bars` 内的假延续磨损。
- **公开数据源**：Binance perpetual `15m` OHLCV（公开 REST / dump 即可），不需要额外低频外部数据。
- **最小定义**：
  1. anchor 候选先只测 3 类：`breakout/breakdown confirm bar`、`最近确认 swing low/high`、`Fib leg 起点 bar`；
  2. `A_VWAP_t(anchor) = cumsum(((O+H+L+C)/4)*V) / cumsum(V)`，只从 anchor bar 起累计；
  3. long 侧 gate：`close > A_VWAP_anchor`，或最近 `3` 根里至少 `2` 根收在其上；short 镜像；
  4. 可加一层 repo 启发的距离条件：`abs(close - A_VWAP_anchor) < 0.5 * ATR14`，把它当“回踩够近”的 retest 条件，而不是主 alpha。
- **最小回测切口**：`BTC / ETH / SOL` perpetual，最近 `180d`，`15m`，统一 `next-bar open`、`no-overlap`、成本先看 `6 / 10 / 15 bps per side`；对照 `base`、`base + session_vwap_gate`、`base + event_avwap_gate`、`base + event_avwap_gate + 0.5ATR proximity`。
- **最先看的 4 个指标**：`post-cost expectancy`、`false-hold / false-follow-through rate`、`trade_count retention`、`winner truncation rate`。
- **下一步怎么测**：第一轮不要扫太多 anchor 组合，先只回答一个更值钱的问题——**真正有增量的，是“event anchor 比 session anchor 更贴交易对象”，还是只是又多加了一条会砍样本的线？** 只要 `event_avwap` 在 trade retention 还过得去的前提下，能稳定降低假守住率，它就值得进入 shared confirmation 候选池。

## 5. 风险与保留意见
- 这轮主证据是 repo 代码，不是论文 OOS；它证明的是“规则很好冻结”，不是“edge 已被严格验证”。
- anchor 选得太自由，最容易把 event AVWAP 变成事后美化器；所以第一轮必须把 anchor 类别冻结，不能一根图上随意挑“看起来对的起点”。
- `0.5 ATR` 很适合做 proximity 条件，但也很容易过拟合成漂亮阈值；应该只当一档基线，与 `0.25 / 0.75 ATR` 做小范围敏感性比较。
- event AVWAP 和 EMA / VWAP / LVN-POC 可能有信息重叠；后续必须做 ablation，确认它是不是独立增量，而不是换了个更高级的名字重复确认。

## 6. 来源
- s-kust. (2024). *anchored_vwaps: Python code to add anchored VWAPs to OHLC data and draw charts*.
  - Venue / DOI：无（GitHub repo）
  - Repo URL: <https://github.com/s-kust/anchored_vwaps>
  - Readable URL: <https://github.com/s-kust/anchored_vwaps/blob/main/README.md>
  - Raw README URL: <https://raw.githubusercontent.com/s-kust/anchored_vwaps/main/README.md>
  - Key code URL: <https://raw.githubusercontent.com/s-kust/anchored_vwaps/main/vwaps_plot_build_save.py>
  - Repo metadata snapshot: created `2024-09-10`, pushed `2024-12-15`, `10` stars at fetch time.
- Shabbir Hasan. (2025). *Anchored_Volume_Weighted_Average_Price*.
  - Venue / DOI：无（GitHub repo）
  - Repo URL: <https://github.com/ShabbirHasan1/Anchored_Volume_Weighted_Average_Price>
  - Readable URL: <https://github.com/ShabbirHasan1/Anchored_Volume_Weighted_Average_Price/blob/main/README.md>
  - Key script URL: <https://raw.githubusercontent.com/ShabbirHasan1/Anchored_Volume_Weighted_Average_Price/main/6.Anchored_Volume_Weighted_Average_Price.py>
  - Repo metadata snapshot: created `2025-10-20`, pushed `2025-10-04`, `0` stars at fetch time.
- 概念背景（仅作母体，不作为本轮主证据）：Brian Shannon. *Maximum Trading Gains with Anchored VWAP*.