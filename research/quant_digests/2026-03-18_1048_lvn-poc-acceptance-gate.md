# 别把 retest_hold 写成“回到线就算守住”：LVN rejection + POC acceptance，更像 15m 的 shared acceptance gate
- 时间：2026-03-18 10:48 UTC
- 类型：GitHub
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/volume-profile/lvn/poc/acceptance/repo/crypto/15m
- 证据类型：工程经验 / 待验证

## 1. 这次看了什么
看的是 GitHub 仓库 `Aksee123/nq1_Scalping_Strategy`（2025）。它本来是给 NQ1 futures 做的短线脚本，但真正值得我们 desk 借的不是它的 NQ scalp 语境，而是代码里那条更适合 `15m` 的旁支：**先用 rolling volume profile 找 `POC + low-volume nodes (LVN)`，再只在“触碰后被拒绝、并重新回到 POC 强侧”时确认进场**。这对当前 `Fibonacci confirmation / retest_hold`、`breakout-short follow-up`、`EMA / PSAR raw alpha` 都比再堆一层均线更像共享确认层。

## 2. 核心结论
- **一句话核心结论**：对 `5m / 15m` 来说，很多假回踩不是“价位没到”，而是**到了以后没有被市场重新接受**；所以比“碰到 Fib / EMA / breakout retest 位就开”更值得先测的，是 `LVN rejection + POC acceptance` 这套 acceptance gate。
- **一句话证明方式**：这个 repo 把逻辑直接写进 Pine 代码里：默认用 `150 bars / 24 bins / 70% value area` 做 volume profile，先找 `POC`，再挑 `POC` 上下方的低成交量节点当支撑/阻力，只有在价格触碰这些 level 后 **收回 level 本身**，并且同时通过 `candle / ATR / EMA` 过滤时才给信号。
- 最值钱的不是它的 NQ 交易结果，而是它把“回踩确认”拆成了三层：`位置到达`、`局部拒绝`、`重回主成交重心`。`Fib / breakout retest` 往往只解决了第一层，最多半解决第二层，但对第三层——**市场是否重新接受这个方向**——经常没写清楚。
- 代码里最可借的部分有两个：一是用 `lowest-volume rows` 去近似找容易被快速穿越、也容易被拒绝的薄成交区；二是让 `POC` 充当“强侧 / 弱侧”的判别线。翻成人话就是：**回踩到薄区不够，还得看价格能不能重新回到主要成交密集区的同侧。**
- 这轮优先做它，是因为它不是偏题新玩具，而是能同时补三条收口线：`Fib retest_hold` 需要更诚实的 hold 定义，`breakout-short follow-up` 需要 post-break acceptance/failed reclaim，`EMA / PSAR` 需要一个不那么自我循环的角色判断层。

## 3. 为什么和当前项目有关
- 对 `Fibonacci confirmation / retest_hold`：Fib 更像“允许在哪个价带观察反应”，`LVN rejection + POC acceptance` 才更像“这次回踩是不是被真接住了”。也就是说，Fib 继续负责位置，volume profile 负责 acceptance。
- 对 `V3 final-verdict / breakout-short follow-up`：break 后最怕两种错——一是刚跌破就追，二是反抽回来却没看出已经重新被市场接回去。POC/ LVN 给了更清楚的镜像写法：**跌破后先看反抽是否卡在 LVN / value migration 薄区被拒，再看 close 是否继续留在 POC 下方。**
- 对 `EMA / PSAR raw alpha focus`：EMA/PSAR 继续做方向或结构锚，但 `close relative to POC` 能补一个更像“成交重心有没有跟上”的角色判断。这样比继续加更多 trend filter 更容易做 ablation。
- 如果要回答“为什么它比继续帮三条线收口更值得”，答案其实很直接：**因为它不是第四条新线，而是一个能横向服务三条线的 shared acceptance gate。**

## 4. 可复刻的最小实验
- **研究假设**：在 `BTC / ETH / SOL` perpetual 的 `15m` 上，给现有 `Fib retest_hold`、`breakout retest` 或 `EMA/PSAR continuation` setup 叠加 `LVN rejection + POC acceptance`，能降低假 hold / 假 continuation，同时不把 trade count 砍得太狠。
- **最小定义**：
  1. 用最近 `96` 或 `144` 根 `15m` bar 做 rolling volume profile，分成 `24` 或 `32` 个 price bins；
  2. 定义 `poc_t` 为最大成交量 bin 中位价；
  3. 定义 `lvn_support_t` / `lvn_resistance_t` 为 `POC` 下方 / 上方最近的低成交量 bin 中位价；
  4. long 侧：`lvn_reject_long = low <= lvn_support_t + 0.15*ATR and close > lvn_support_t`；`poc_accept_long = close > poc_t or 最近3根至少2根收在 poc_t 上方`；
  5. short 侧镜像：`high >= lvn_resistance_t - 0.15*ATR and close < lvn_resistance_t`，且 `close < poc_t` 或最近 3 根至少 2 根收在 `poc_t` 下方。
- **最小回测切口**：最近 `180~365` 天，`15m`，`next-bar open`，`no-overlap`，成本先看 `6 / 10 / 15 bps per side`；先做三臂：`base`、`base + LVN reject`、`base + LVN reject + POC accept`。
- **最先看的 4 个指标**：`post-cost return`、`false-retest / false-follow-through rate`（入场后 4 根内重新回到 POC 反侧）、`trade_count`、`positive_asset_ratio`。
- **下一步怎么测**：第一轮不要把 value area、funding、OI、flow 全一起堆上去；先只回答一个最值钱的问题——**增量主要来自“LVN 被拒绝”还是“重新站回 / 压回 POC 同侧”？** 如果只有其中一个有效，就保留更简单的那个，别把 acceptance gate 写成复杂美化器。

## 5. 风险与保留意见
- 这是 **新 GitHub 仓库**，不是论文；而且源市场是 `NQ1 futures`，不是 crypto，不能把参数和收益口径照搬。
- repo 的 README 明显偏工程展示风格，证据强度主要来自代码结构，不来自严谨 OOS 报告；所以当前最多继承它的 **规则骨架**，不能继承它的绩效自信。
- rolling volume profile 在 crypto `24/7` 里最容易过拟合的是窗口长度和分箱数；`96 vs 144 bars`、`24 vs 32 bins` 都应做 sensitivity check。
- `POC acceptance` 可能和现有的 `EMA / VWAP / close-confirmed structure` 有部分重复信息，必须做 ablation，确认它是不是独立增量，而不是换个名字重复确认。
- 对 `breakout-short`，short mirror 尤其要小心：薄成交区有时意味着容易直接穿透，不一定意味着适合反抽做 continuation，所以一定要和 `close relative to POC` 绑定测，而不是只测“触碰 LVN 就空”。

## 6. 来源
- Rao Aksee Nasir. (2025). *Enhanced NQ1 Scalping Strategy / nq1_Scalping_Strategy*.
  - Venue / DOI：无
  - Repo URL: <https://github.com/Aksee123/nq1_Scalping_Strategy>
  - Readable URL: <https://github.com/Aksee123/nq1_Scalping_Strategy/blob/main/README.md>
  - Raw strategy URL: <https://raw.githubusercontent.com/Aksee123/nq1_Scalping_Strategy/main/nq1_scalp.pine>
  - Repo API: <https://api.github.com/repos/Aksee123/nq1_Scalping_Strategy>
  - Repo contents API: <https://api.github.com/repos/Aksee123/nq1_Scalping_Strategy/contents>
  - Repo metadata snapshot: created `2025-07-20`, updated `2026-01-28`, `2` stars, `0` forks.
