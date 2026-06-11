# Strategy Review — 2026-04-05 22:50 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short --branch`
- 最近 optimization：
  - `research/optimization_loop/2026-04-05_2244_rank342_p2_admission_round1_crossasset_lowgas_lane_replicates_keep_p2.md`
  - `research/optimization_loop/2026-04-05_2206_rank343_poc_cvd_absorption_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-05_2135_rank342_survivor_followup_lowgas_samechain_pocket_promote_p2.md`
  - `research/optimization_loop/2026-04-05_2024_rank342_samechain_crossdex_pricegap_close_first_verdict_keep_p1.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-05_2210_strategy-review.md`
  - `research/strategy_review/2026-04-05_2101_strategy-review.md`

## 只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- **否。**
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有新的待接线 queue 头对象。

### 2) 本轮 `fresh intake` 是什么？
- **`research/quant_digests/2026-04-05_1919_winneronly-losershort-veto-xs-alpha.md`。**
- 原因：`Rank 343 / POC + CVD absorption` 已在 `2026-04-05_2206_rank343_poc_cvd_absorption_first_verdict_keep_p1.md` 完成 fresh intake first verdict 并占据 `Surviving candidate slot`，所以 fresh intake 前位顺延到 `winner-only × loser-short veto`。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得，而且必须先做。**
- 上一条 fresh intake 是 `Rank 343 / POC + CVD absorption`。
- 它当前已经不是术语拼接，而是把 `rolling POC 锚点 + price-vs-CVD absorption trigger + POC-distance 约束 + 1H->15m transfer boundary` 压成了独立 single-asset raw alpha 壳，所以 first verdict 合法进入 `keep_P1`。
- 但它还没回答最关键的 survivor 问题：`1H` 母信号是否真能迁移成 `15m child execution` 的 short-cycle edge，而不是只停留在 HTF 独立策略。
- 因此它值得、且按 policy 必须获得那唯一一次 decisive follow-up；在这次 follow-up 收口前，不能让新的 `keep_P1` 候选覆盖 survivor 槽位。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **存在。**
- 当前 `Active P2 = Rank 342 / same-chain cross-DEX price-gap close`。
- 就现有证据看，它离 **`P3` 最近**。
- 理由：`Rank 342` 已先通过 survivor 收口，确认真正可交易壳更像 `Base/低 gas 链上的 same-chain pool dislocation close`；随后又在 `Base cbBTC/WETH`、`Base cbBTC/USDC`、`Arbitrum WETH/USDC`、`Arbitrum WBTC/WETH` 上补出了 `effectiveness / cross-asset` 首轮 replication，因此它已经不再像单一 `Base WETH/USDC` 特例。
- 但本轮**暂不触发** bot2 兜底强升 `P3`：因为最近 desk review 仍未把 `time / parameter / honesty` 三轴补齐到“足够值得直接 paper trade 且无明显致命 execution 问题”的程度，所以最诚实的动作是把它排成 **出口决策轮**，而不是继续开放式研究，也不是提前越级升级。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Surviving candidate slot.current_target = Rank 343 / POC + CVD absorption`
- `Active P2 slot.current_target = Rank 342 / same-chain cross-DEX price-gap close`
- 当前前排对象都有正式 rank；本轮无需补 rank。

## P2 -> P3 兜底裁判检查
- 本轮结论：**不强行把 `Rank 342` 改写进 `P3 / Paper launch queue`。**
- 原因不是它不够强，而是 desk review 还没有清楚到可以直接宣告“paper-launch-ready”：
  - `effectiveness / cross-asset` 已有正面结果；
  - 但 `time stability / parameter stability / honesty / execution realism` 仍是最后一组真正可能改变出口的 blocker。
- 所以按 policy，正确动作是把 `Rank 342` 的下一步写成 **直接出口决策轮**：`promote_P3 / one-time P2->P1 re-scope / drop_to_background` 三选一，不得再写第三次开放式 `keep_P2` admission。

## cycle_plan 重写结果
按 policy 默认顺序：`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0`。

当前运行态下：
- `P3`：无待接线对象
- `P2`：有且只有 `Rank 342`
- `P1`：有且只有 `Rank 343`
- 因此前排链条未收口前，新的 fresh intake 不能排到它们前面

已将 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan` 重写为：
1. `Rank 342 / same-chain cross-DEX price-gap close`：直接做出口决策轮，补 `time / parameter / honesty`
2. `Rank 343 / POC + CVD absorption`：执行 survivor 唯一一次 decisive follow-up
3. `research/quant_digests/2026-04-05_1919_winneronly-losershort-veto-xs-alpha.md`：作为当前 fresh intake 做 first verdict
4. `research/quant_digests/2026-04-05_2151_rolling-max-spike-persistence-xs-alpha.md`：作为 conditional fresh intake 占位，仅在前排链条已诚实排入后再轮到它

### 为什么这么排
- `Rank 342` 已经是唯一 `Active P2`，而且离 `P3` 最近，所以必须放在第 1 位，且这次必须是出口决策轮；
- `Rank 343` 依法享有 survivor 唯一一次 follow-up 的前排锁定权；
- `winner-only × loser-short veto` 仍是当前 fresh intake，但只能在前排链条已被诚实排入后执行；
- 因为 `Rank 342` 目前只有 **1 次** `keep_P2`，还没到“连续 2 次 keep_P2 后必须保留 conditional fresh intake”的硬触发；但当前轮预算允许，且前 3 项都已具体排入，所以第 4 项可以诚实写成明确对象，不必回到抽象模板句。
- 选择 `rolling-max spike persistence` 作为 conditional intake，是因为它属于最近新 digest，且需要先过 distinctness 检查，确认不是对 `fresh-high / breakout continuation` 家族的重复换壳。

## 本轮一句话
现在不是继续撒网的时候：`Rank 342` 已经到了该做出口决策的节点，`Rank 343` 也锁住了唯一 follow-up，所以这轮先把前排收口，再给 `winner-only × loser-short veto` 和下一条条件 intake 留位。