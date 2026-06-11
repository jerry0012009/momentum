# Strategy Review — 2026-04-05 22:10 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short --branch`
- 最近 optimization：
  - `research/optimization_loop/2026-04-05_2206_rank343_poc_cvd_absorption_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-05_2135_rank342_survivor_followup_lowgas_samechain_pocket_promote_p2.md`
  - `research/optimization_loop/2026-04-05_2024_rank342_samechain_crossdex_pricegap_close_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-05_1940_rank341_survivor_followup_majors_realistic_cost_not_admission_ready_background_p0.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-05_2101_strategy-review.md`
  - `research/strategy_review/2026-04-05_1944_strategy-review.md`

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
- 就现有证据看，它离 **`P3` 最近**，不是离 `P1/P0` 最近。
- 原因很简单：最近 survivor follow-up 已经把对象从“概念上的 onchain RV”推进到“Base 等 low-gas 链存在 after-cost pocket”的 admission-ready 状态；这更像是在补齐 `P3` 之前剩下的 admission 五轴，而不是在寻找 fatal flaw。
- 当然，当前还**不足以直接由 bot2 强制升 P3**，因为最近证据主要解决了 `executable lane / after-cost pocket`，还没把 `cross-asset / time / parameter / honesty` 系统补齐；所以本轮最诚实的做法不是越级写 `P3`，而是把 `Rank 342` 放在 cycle plan 最前，集中完成 admission 收口。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Surviving candidate slot.current_target = Rank 343 / POC + CVD absorption`
- `Active P2 slot.current_target = Rank 342 / same-chain cross-DEX price-gap close`
- 当前前排对象都有正式 rank；本轮无需补 rank。

## P2 -> P3 兜底裁判检查
- 本轮**暂不触发** bot2 的强制 `P2 -> P3` 升级。
- 解释：`Rank 342` 已明显不像 `P0/P1`，而是更接近 `P3`；但现有桌面证据还没有清楚到“已经足够值得 paper trade 且无明显 honesty / execution 问题”的程度。
- 换句话说：它现在不该被继续排成泛研究，也不该被回退；正确动作是把 admission 收口排到最前，两步内尽量逼近明确出口。如果这两步继续给出正面结果，下一轮就该更偏向 `promote_P3`，而不是第三次开放式拖延。

## 本轮排班结论
按 policy 默认顺序：`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0`。

当前运行态下：
- `P3`：无待接线对象
- `P2`：有且只有 `Rank 342`
- `P1`：有且只有 `Rank 343`
- 因此前排链条并未清空，新的 fresh intake 不能排到它们前面

已将 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan` 重写为：
1. `Rank 342 / same-chain cross-DEX price-gap close`：先补 `effectiveness / cross-asset`
2. `Rank 342 / same-chain cross-DEX price-gap close`：再补 `time / parameter / honesty`
3. `Rank 343 / POC + CVD absorption`：执行 survivor 唯一一次 decisive follow-up
4. `research/quant_digests/2026-04-05_1919_winneronly-losershort-veto-xs-alpha.md`：作为当前 fresh intake 做 first verdict

这样排的原因：
- `Rank 342` 已经是明确 `Active P2`，而且更接近 `P3`，所以优先级必须高于新的发现；
- `Rank 343` 作为 survivor，依法享有那唯一一次 follow-up 的前排锁定权；
- 只有在前两层都被诚实排进当前轮后，才轮到 fresh intake；
- `chartpattern-neckline-imbalance` 这轮不再占前四，因为它没有前排优先级，且当前预算已经被 `P2 + survivor + fresh intake` 填满。

## 本轮一句话
现在不是“继续刷新发现”的时候：`Rank 342` 已进入明确 P2、并且更像朝 `P3` 走，`Rank 343` 也锁住了唯一 survivor follow-up，所以这轮应该先把前排收口，再给 `winner-only × loser-short veto` 新鲜入口。