# 别把 15m continuation 的失效继续写成“感觉走坏了”：EMA fast 失守 + VWAP flip + `0.75 ATR`，更像三条线共用的 fail-fast overlay
- 时间：2026-03-18 14:02 UTC
- 类型：GitHub
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/continuation/failure/exit/fail-fast/vwap/atr/repo/crypto/15m
- 证据类型：工程经验 / 待验证

## 1. 这次看了什么
这次看的是 `bptrades/0dte-momentum-continuation-pro`（2026）这个 Pine Script 仓库。它主打的是 intraday continuation 的**确认工具**，但对我们 desk 真正值钱的，不是它那套 A+/B 打分，而是它把“这笔 continuation 什么时候算走坏”写成了三个非常短、可冻结的条件：`close < EMA fast`、`VWAP flip`、以及 `entry ± 0.75 ATR` 的 premium protection。翻成人话：**别等主观感觉不对劲，先把 continuation 的 fail-fast 规则写死。**

## 2. 核心结论
- **一句话核心结论**：当前三条收口线更缺的，未必又是一个新入场过滤器，而是一个共享的“认错更快”失效层。
- **一句话证明方式**：repo 直接把 continuation 持仓状态写进代码：一旦多头 `close < emaFast`、或 `close < vwap`、或 `close < entryPrice - atr*0.75`，就退出；空头完全镜像。不是讲故事，是明确的状态机。
- 对 desk 最值得复用的点，是把这三件事拆成不同角色：`EMA fast` 像微观结构破坏，`VWAP flip` 像盘中接受度反转，`0.75 ATR` 像最后一道硬保护。
- 这比继续给 `breakout-short / Fib / EMA-PSAR` 各补一个新 gate 更值得先看，因为最近几轮我们已经很努力在解决“要不要进”，但**“进了以后什么时候该承认 continuation 没走出来”** 还没有 shared 语言。
- repo 还顺手给了一个诚实提醒：它自己就说这是 **confirmation/context tool, not signal generator**。这和我们现在最需要的角色定位其实很对路。

## 3. 为什么和当前项目有关
- 对 `V3 final-verdict / breakout-short follow-up`：跌破后最怕的是下去两根又被迅速拉回。`emaFast reclaim + VWAP flip` 很适合作为 **post-break failure close**，比“拿到固定 8 bar 再说”更诚实。
- 对 `Fibonacci confirmation / retest_hold`：Fib 负责回答“回到哪”，但 fail-fast 层负责回答“守没守住”。如果回踩做多后价格重新丢失 `EMA fast`，或重新跌回 VWAP 下方，`hold` 就不该再靠嘴硬。
- 对 `EMA / PSAR raw alpha focus`：这条线最直接。既然最近越来越像在把 PSAR 降级成结构锚，那真正该补的就是**entry 之后的微观失效定义**，而不是再把 PSAR硬塞回逐根出场。
- 如果要回答“为什么它比继续帮三条线收口更值得”，答案很简单：这不是开新坑，而是在给三条线补同一块缺口——**shared failure protocol**。

## 4. 可复刻的最小实验
- **研究假设**：给现有 `breakout_short`、`fib_retest_hold`、`ema_slope_continuation` 统一叠加一个三选一的 `fail_fast_overlay`，能降低 `4~8 bars` 内的假 follow-through 损耗，并改善成本后收益分布。
- **最小定义**：
  1. `ema_fail`: 多头 `close < EMA9`；空头 `close > EMA9`；
  2. `vwap_fail`: 多头 `close < session_VWAP`；空头镜像；
  3. `atr_fail`: 多头 `close < entry - 0.75*ATR14`；空头镜像；
  4. 先测三臂：`base exit`、`base + any(ema_fail, atr_fail)`、`base + any(ema_fail, vwap_fail, atr_fail)`。
- **最小回测切口**：`BTC / ETH / SOL` perpetual，最近 `180d`，`15m`，统一 `next-bar open`、`no-overlap`、成本 `6 / 10 / 15 bps per side`。
- **最先看的 4 个指标**：`post-cost expectancy`、`median loser size`、`false-follow-through rate`（入场后 `4/8` 根内反向穿回 setup 失效线）、`trade_count retention`。
- **下一步怎么测**：第一轮不要问哪个 stop 最赚钱，先只问一个更值钱的问题——**增量主要来自更快认错，还是只是把原本会回来的单子也提前砍掉？** 所以必须额外看 `winner truncation rate`（本来最终盈利、但被 fail-fast 提前砍掉的比例）。

## 5. 风险与保留意见
- 这是一个很新的小 repo，且应用场景更偏美股/0DTE intraday，不是 crypto 原生证据；当前最多算规则骨架，不是 validated alpha。
- `VWAP` 在 24/7 crypto 里天然依赖 session 切法；如果 session 定义乱，`VWAP flip` 可能只是把时段噪音包装成风控。
- `0.75 ATR` 很像“漂亮默认值”，但也最容易被误用成万能止损；不同币种、不同 regime 下可能需要 `0.5 / 0.75 / 1.0 ATR` 三档对照。
- fail-fast overlay 的典型代价是 **减少大亏，也减少后来又走出来的单子**；所以它更像收益分布塑形工具，而不是凭空创造 alpha。

## 6. 来源
- bptrades. (2026). *0dte-momentum-continuation-pro*.
  - Venue / DOI：无（GitHub repo）
  - Repo URL: <https://github.com/bptrades/0dte-momentum-continuation-pro>
  - Readable URL: <https://github.com/bptrades/0dte-momentum-continuation-pro/blob/main/README.md>
  - Raw strategy URL: <https://raw.githubusercontent.com/bptrades/0dte-momentum-continuation-pro/main/MomentumContinuationProAlgo.pine>
  - Raw README URL: <https://raw.githubusercontent.com/bptrades/0dte-momentum-continuation-pro/main/README.md>
  - Repo API: <https://api.github.com/repos/bptrades/0dte-momentum-continuation-pro>
  - Repo metadata snapshot: created `2026-02-06`, updated `2026-02-06`, `1` star at fetch time.
