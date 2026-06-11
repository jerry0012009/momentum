# 别把 EMA / PSAR raw trigger 当成入场：`pullback → two-sided breakout window` 更像 breakout-short / Fib / EMA 的 honest continuation verdict
- 时间：2026-03-20 07:42 UTC
- 类型：GitHub 仓库
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/pullback/two-sided-window/continuation/failure/timeout/final-verdict/follow-up/repo/crypto/5m/15m
- 证据类型：仓库代码 + 仓库自报回测

## 1. 这次看了什么
这次主看 GitHub 仓库 **ilahuerta-IA/backtrader-pullback-window-xauusd**（2025-10 创建，2026-03 仍在更新，37★）。这份 repo 最值得偷的不是它的 `EMA(1/14/18/24)` 参数，而是一个很适合我们当前三条收口线的旁支想法：**把“raw trigger”降级成 `scan`，真正的 entry 交给 `pullback → two-sided breakout window` 来做 success / failure / timeout 判决。**

## 2. 核心结论
- **一句话核心结论**：对 5m/15m crypto desk，更值得先测的不是“换一组更神的 EMA/PSAR 参数”，而是把原始信号之后的那段小路径离散成 `armed → pullback confirmed → window open → success/failure/timeout`。
- **一句话证明方式**：repo 用 5 分钟 XAUUSD 回测一个 4-phase state machine；虽然资产不是 crypto、结果也属作者自报，但它明确给出了一个比“信号一亮就下单”更诚实的执行骨架。
- repo 自报结果（**未独立复核**）：2020-07~2025-07 的 5m XAUUSD 上，`175` 笔交易、`55.43%` 胜率、`1.64` Profit Factor、`5.81%` Max DD、总回报 `+44.75%`。
- repo 自报的细节里，最有启发的一条不是总收益，而是：`Window Breakout (Normal)` 有 `162` 笔、胜率 `56.2%`，而 `Quick Entry (Fast Market)` 只有 `13` 笔、胜率 `46.2%`。这基本就是在提醒我们：**同一个方向 bias，晚一点、等 verdict，再进，可能比 trigger 当场冲更值钱。**
- 代码层的关键骨架：
  1. `SCANNING`：只负责发现 EMA crossover + 方向 candle + 可选 angle/ATR filter；
  2. `ARMED`：不立刻进场，先等 `1~3` 根逆向 pullback candle；
  3. `WINDOW_OPEN`：用最后一根 pullback candle 的 `high/low` 构造双边窗口，并允许 `time offset`；
  4. `SUCCESS / FAILURE / TIMEOUT`：顺向破边才 entry；反向破边视为 instability；超时则 setup 作废。
- 对我们更重要的不是 “Gold 也能赚”，而是这套骨架把 continuation / retest / re-break 统一写成了一个**可离散、可统计、可否决**的 verdict 机制。

## 3. 为什么这轮值得先做
这轮不是另开新宇宙，反而是直接给当前三条收口线补一个共同缺口：**trigger 之后，到底什么才算“值得进”的 follow-up。**

- `V3 final-verdict / breakout-short follow-up`：breakdown 本身只负责把 setup 变成 `armed_short`；随后若出现 `1~2` 根反抽绿转红/红转绿`(按方向定义)`，再开一个很短的下破窗口。**向下 success 才叫 follow-up，向上 failure 就该直接否决。**
- `Fibonacci confirmation / retest_hold`：Fib zone 触位后，不要把“摸到就算 hold”。更诚实的写法是：先确认 pullback 成立，再要求价格在 `W` 根内重新突破 pullback extremum；没突破是 timeout，跌穿 opposite edge 是 failure。
- `EMA / PSAR raw alpha focus`：这套东西本质上没有改 EMA/PSAR 的本体，只是把 raw alpha 从 `entry key` 降成 `scan key`。这正适合当前阶段——先测“post-trigger verdict layer”能不能救 raw alpha，而不是继续炼更复杂指标堆叠。

## 4. 我们最该偷的，不是参数，而是 3 个 execution 结构件
### A. 双边窗口，而不是单边确认
repo 的窗口不是“只看顺向破位”，而是同时定义 `success boundary` 和 `failure boundary`。这点非常适合我们当前的 `final-verdict` 语境：
- breakout-short：下破 `pullback low - offset` 才算 success；上穿 `pullback high + offset` 就是 failure；
- Fib retest：重破 pullback high / low 才算 hold confirmed；反向失守就是 hold invalidated；
- EMA/PSAR：raw cross / flip 只是 `scan`，真正进场要等窗口给 verdict。

### B. timeout 必须是一级公民
repo 明确把 `window_expiry_bar` 写进状态机。对 15m 很关键：
- 如果 retest / follow-up 迟迟不发生，它本身就是负信息；
- 这比事后再加 `late entry veto` 更干净，因为 timeout 是 setup 自带标签，不是补丁；
- 这跟最近我们反复碰到的 `late retest / stale follow-up` 问题是同一个洞。

### C. failure 后别直接归零，可回到 re-arm
repo 在 failure / timeout 后不是一律回 `SCANNING`，而是很多情形回到 `ARMED_*`，允许同方向 setup 重新找新的 pullback。这个细节很适合 `breakout-short follow-up`：**失败不等于 bias 死亡，更可能只是这一次 re-break 质量不够。**

## 5. 先别急着照搬的地方
- 资产是 `XAUUSD 5m`，不是 crypto perp；它的时段性、跳动值、交易时段、spread 结构都不同。
- repo 的绩效数字是作者自报，且没有独立 clean replication；我们现在只能把它当“高信息执行模板”，不能当已验证 alpha。
- 该 repo 还带了 angle / ATR / time filter / 头寸管理等一整包条件；**这轮最该偷的是 state machine verdict，不是整包照抄。**

## 6. 可复刻的最小实验（先做这个）
### 实验目标
验证：**把 raw trigger 改成 `scan-only`，再加一个短窗口 success/failure/timeout verdict，是否能优于当场入场。**

### 6.1 统一母骨架
1. 周期：先 `15m`，执行补充看 `5m`；标的先 `BTC/ETH/SOL perp`。
2. 原始 trigger：
   - breakout-short：现有 `V3 final-verdict` 触发条件；
   - Fib：现有 `zone touch / reclaim` 候选；
   - EMA/PSAR：现有 raw cross / raw flip。
3. 一旦 trigger 出现，只标 `armed_dir=±1`，**不立刻下单**。
4. pullback 定义：trigger 后出现 `1~3` 根逆向 candle，或 `pullback_depth <= d`（可并行测 `candle-count` 与 `depth` 两种口径）。
5. 窗口定义：用最后一根 pullback bar 的 `high/low` 建双边窗口；先测：
   - `offset = 0, 0.25, 0.5 × pullback_range`
   - `window = 2, 4, 6 bars`
6. verdict：
   - `success`：顺向破 success edge；
   - `failure`：反向破 failure edge；
   - `timeout`：到 `window_expiry_bar` 仍未 success。

### 6.2 三条线各自怎么压
- **breakout-short**：
  - `scan` = 原始 breakdown candidate
  - `pullback` = 1~2 根反抽
  - `success` = low 跌破 pullback low - offset
  - `failure` = high 上穿 pullback high + offset
- **Fib retest_hold**：
  - `scan` = 触到目标 Fib 区且仍保有方向 bias
  - `pullback` = 进入区间后的停顿 / 逆向小回撤
  - `success` = close/ high 重破 pullback extremum
  - `failure` = 反向穿越 zone invalidation line
- **EMA / PSAR raw alpha**：
  - `scan` = raw EMA cross / raw PSAR flip
  - `pullback` = trigger 后 1~3 根 counter bars
  - `success` = 重新突破 pullback edge
  - `failure` = 反向失守 opposite edge

### 6.3 先看哪几个指标
- `成本后 expectancy`
- `success rate / failure rate / timeout rate`
- `trigger→entry 平均延迟`
- `false-follow rate`（入场后 `N` 根内即回到 opposite edge）
- `missed-fast-move cost`（因为等 verdict 而错过的趋势）

## 7. 我对这轮的判断
如果这层东西成立，它最可能带来的不是“信号数暴增”，而是三件更现实的好处：
1. **把 breakout-short 的 final-verdict 写得更诚实**：不是破了就追，而是先看 pullback 后能不能再给一次真实下破；
2. **把 Fib retest_hold 从“碰位叙事”改成“窗口 verdict”**：摸到位不再自动算 hold；
3. **给 EMA/PSAR raw alpha 一个低侵入修复方向**：先修 entry path，而不是继续堆 filter。

我的倾向是：这条值得进研究池，而且优先级不低，因为它不是又一个零散过滤层，而是一个能同时作用于三条收口线的**post-trigger execution skeleton**。

## 8. 来源
1. ilahuerta-IA. (2025-2026). *Backtrader Gold (XAU/USD) Pullback Strategy*.
   - Repo URL: https://github.com/ilahuerta-IA/backtrader-pullback-window-xauusd
   - Readable URL: https://github.com/ilahuerta-IA/backtrader-pullback-window-xauusd/blob/main/README.md
   - Performance doc: https://github.com/ilahuerta-IA/backtrader-pullback-window-xauusd/blob/main/PERFORMANCE_METRICS.md
   - Raw strategy file: https://raw.githubusercontent.com/ilahuerta-IA/backtrader-pullback-window-xauusd/main/src/strategy/sunrise_ogle_xauusd.py
   - DOI: N/A
   - Authors: GitHub user `ilahuerta-IA`（未见论文式作者署名）