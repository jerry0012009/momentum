# Strategy Review (bot2)

Time: 2026-03-29 05:57 UTC

## 本轮一句话判断
当前前排唯一真实待收口对象是 `Rank 231 / ETH whale balance imbalance` 的唯一 survivor follow-up；`Paper launch queue` 已无待接线 queue 头、`Active P2` 也为空，所以本轮必须先把 `Rank 231` 做出 `P2 / background` 二选一收口，再切回新的具体 fresh intake，优先是 `crossvenue synthetic forward parity`，其后才轮到 park-reframe 候选。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git status --short`
- 最近 `research/optimization_loop/`：
  - `2026-03-29_0403_rank231_eth_whale_balance_imbalance_fresh_intake_keep_p1.md`
  - `2026-03-29_0343_rank229_p3_launch_wiring_connected_runner_live.md`
  - `2026-03-29_0551_cycle_plan_no_pending_legal_action.md`
  - 以及 `2026-03-29_0536 / 0518 / 0458 / 0455 / 0442` 几条 no-op / stale-blocked 记录
- 最近 `research/strategy_review/`：
  - `2026-03-29_0348_strategy-review.md`
  - `2026-03-29_0237_strategy-review.md`
  - `2026-03-29_0010_strategy-review.md`
- 为决定 fresh intake / conditional intake，再读：
  - `research/quant_digests/2026-03-29_0428_crossvenue-synthetic-forward-parity-alpha.md`
  - `research/quant_digests/2026-03-28_1033_eth-whale-balance-imbalance-alpha.md`
  - `research/park_reframe/INDEX.md`
  - `research/park_reframe/2026-03-26_0218_rank96-park-reframe.md`
  - `research/park_reframe/2026-03-25_2209_rank76-park-reframe.md`

硬约束遵守：
- 只更新 `docs/BOT2_BOT3_STATE.md`
- 未改写 policy / brief / operating card / auto loop / cron prompt
- 未自动把 background pool 旧候选拉回前排
- `docs/TODO.md` 未参与本轮排班
- 前排对象不存在无 rank 情况，因此无需补新的整数 `Rank`

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**广义上非空，但当前 queue 头为空。**

原因：
- `connected_runner_live` 里已有 `Rank 200 / 201 / 213 / 229`；
- 但 `Rank 229` 已在 `2026-03-29_0343_rank229_p3_launch_wiring_connected_runner_live.md` 中完成 `runner + scheduler + first verified run + runtime writeback`；
- `current_target` 仍是 `none`，所以当前不存在需要优先压过前排研究动作的 `P3 launch wiring` 待办。

### Q2. 本轮 `fresh intake` 是什么？
**本轮真正的新 fresh intake 应是 `research/quant_digests/2026-03-29_0428_crossvenue-synthetic-forward-parity-alpha.md`。**

原因：
- 先前被写进 `cycle_plan` 的 `eth-whale` 已经不是 fresh intake，而是 `Rank 231` survivor；
- `liquidity-ranked EMA` 与 `Rank 86` reframe 都已被证明是已消费旧对象，继续排只会违反 no-auto-reopen；
- `2026-03-29_0428_crossvenue-synthetic-forward-parity-alpha.md` 是最近新增、且尚未进入前排槽位的新对象，符合 policy 里“最近新的 repo/paper/alpha 报告优先”的 fresh intake 来源。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得，而且这轮就该把这唯一一次 follow-up 花在 `Rank 231 / ETH whale balance imbalance` 身上。**

原因：
- `Rank 231` 的 first verdict 已经很清楚：它不是纯链上故事，而是值得保留的 ETH 事件型 raw alpha 结构；
- 当前唯一没回答的 blocker 也足够收敛：分钟化后的 `Δlarge - Δsmall` 在 `15m/30m/60m/240m` 上是否留下可交易 drift；
- 这正符合 policy 对 survivor 的定义：**只能是上一条 fresh intake，且只花 1 次 decisive follow-up**。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在。当前 `Active P2 = none`。**

原因：
- `Rank 229` 已完成 `P2 -> P3 -> connected_runner_live`，不再占 `Active P2`；
- `Rank 231` 还停留在 survivor，还没过 admission；
- 因此前排当前不是 `P2 exit` 阶段，而是 `P1 survivor 收口 -> fresh intake` 阶段。

## 3) rank 合规检查
- `Paper launch queue / connected_runner_live`：`Rank 200 / 201 / 213 / 229` 都有正式 rank
- `Surviving candidate slot`：`Rank 231` 已有正式 rank
- `Active P2 slot`：`none`
- `Fresh intake slot`：最近首判对象为 `Rank 231`，已有正式 rank
- 结论：**本轮无需补新的整数 Rank**

## 4) 为什么这轮不能继续挂着旧 blocked cycle_plan
最近几条 bot3 日志已经把问题说透：
- `2026-03-29_0551_cycle_plan_no_pending_legal_action.md`
- `2026-03-29_0536_no_pending_cycle_item_guard_block.md`
- `2026-03-29_0518_no_pending_legal_cycle_item.md`

这些 no-op 不是因为 bot3 懒，而是因为旧 `cycle_plan` 里塞的对象已经失真：
- `eth-whale` 已经从 fresh intake 变成 survivor；
- `liquidity-ranked EMA` 早已是 `Rank 219` 并完成 survivor 收口；
- `Rank 86` reframe 早已被 `Rank 222` 消费。

继续保留这些 blocked 项，只会制造更多“没有合法 pending 动作”的空转日志。按 policy，本轮必须把 `cycle_plan` 改回真正合法、具体、能推进的对象。

## 5) 本轮排班为什么是这个顺序
policy 默认顺序：
1. `P3 handoff`
2. `P2 admission/promote/park`
3. `P1 survivor 唯一 follow-up`
4. `fresh intake`
5. 诚实收口后再补 conditional fresh intake

当前 runtime truth：
- `P3`：无 queue 头
- `P2`：无 active 对象
- `P1`：有，而且只有 `Rank 231`
- `fresh intake`：有新的具体对象 `2026-03-29_0428_crossvenue-synthetic-forward-parity-alpha.md`

所以本轮合法顺序只能是：
1. 先做 `Rank 231` survivor follow-up
2. 再切到新的 fresh intake `crossvenue synthetic forward parity`
3. 若预算仍有余，再补 park-reframe 的 concrete conditional intake

## 6) 本轮对 state 的实际写回
已重写 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan` 为 4 项：

1. `Rank 231 / ETH whale balance imbalance`
   - 执行 survivor 的唯一一次分钟化 honesty follow-up
2. `research/quant_digests/2026-03-29_0428_crossvenue-synthetic-forward-parity-alpha.md`
   - 新的 fresh intake first verdict
3. `research/park_reframe/2026-03-26_0218_rank96-park-reframe.md`
   - conditional fresh intake：`short-side second-touch + candle-quality admission delay`
4. `research/park_reframe/2026-03-25_2209_rank76-park-reframe.md`
   - conditional fresh intake：`fixed UTC bucket mode switch`

所有新项都满足：
- 只包含 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`

## 7) 一句话结论
本轮最关键的不是再找借口重做旧对象，而是把前排真实状态写诚实：`Rank 231` 现在是唯一该先收口的 survivor；收口后，新 intake 应切到真正未消费的 `crossvenue synthetic forward parity`，而不是继续让 stale blocked 项把前排卡死。
