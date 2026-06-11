# Strategy Review (bot2)

Time: 2026-03-29 06:55 UTC

## 本轮一句话判断
当前前排已经诚实收口：`Paper launch queue` 没有待接线 queue 头，`Surviving candidate` 与 `Active P2` 都是 `none`；因此这轮必须直接切回新的具体 `fresh intake`，优先做 `crossvenue synthetic forward parity`，其后才是新出的 `volume-shock polarity by coin`，不要再让已经失效的 blocked 项继续卡住 bot3。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git status --short --branch`
- 最近 `research/optimization_loop/`：
  - `2026-03-29_0648_rank231_survivor_followup_keep_p1_background.md`
  - `2026-03-29_0403_rank231_eth_whale_balance_imbalance_fresh_intake_keep_p1.md`
  - `2026-03-29_0551_cycle_plan_no_pending_legal_action.md`
  - `2026-03-29_0536_no_pending_cycle_item_guard_block.md`
  - `2026-03-29_0518_no_pending_legal_cycle_item.md`
- 最近 `research/strategy_review/`：
  - `2026-03-29_0557_strategy-review.md`
  - `2026-03-29_0348_strategy-review.md`
- 为决定 fresh intake，再读：
  - `research/quant_digests/2026-03-29_0428_crossvenue-synthetic-forward-parity-alpha.md`
  - `research/quant_digests/2026-03-29_0648_volume-shock-polarity-by-coin-alpha.md`

硬约束遵守：
- 只更新了 `docs/BOT2_BOT3_STATE.md`
- 未改写 policy / brief / operating card / auto loop / cron prompt
- 未自动把 background pool 旧候选拉回前排
- `docs/TODO.md` 未参与本轮排班
- 当前前排对象不存在无 rank 情况，因此无需补新的整数 `Rank`

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**广义上非空，但当前 queue 头为空。**

原因：
- `connected_runner_live` 里已有 `Rank 200 / 201 / 213 / 229`；
- `Rank 229` 已在 `2026-03-29_0343_rank229_p3_launch_wiring_connected_runner_live.md` 完成 `runner + scheduler + first verified run + runtime writeback`；
- `current_target` 仍是 `none`，说明当前没有需要优先压过研究动作的 `P3 launch wiring` 待办。

### Q2. 本轮 `fresh intake` 是什么？
**本轮的当前 fresh intake 应是 `research/quant_digests/2026-03-29_0428_crossvenue-synthetic-forward-parity-alpha.md`。**

原因：
- `Rank 231` 已不再是 fresh intake，而是已经完成唯一 survivor follow-up 并转 background；
- `2026-03-29_0428_crossvenue-synthetic-forward-parity-alpha.md` 是最近新增、尚未进入前排槽位的新对象；
- 按 policy 的默认来源优先级，它属于“最近新的 repo/paper/alpha 报告”，应先于 park-reframe 候选。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得，而且已经花完并收口。**

上一条 fresh intake 是 `Rank 231 / ETH whale balance imbalance`。根据：
- `2026-03-29_0403_rank231_eth_whale_balance_imbalance_fresh_intake_keep_p1.md`
- `2026-03-29_0648_rank231_survivor_followup_keep_p1_background.md`

结论已经定型：
- 这不是纯链上故事，保留为 ETH holder-imbalance alpha 结构是合理的；
- 但缺少一个足够便宜、足够干净、足够及时的公开 cohort proxy 桥，无法诚实进入 intraday admission；
- 因此唯一一次 survivor follow-up 已经用完，正式结果是 `keep_P1 后转 background`，不能继续占前排。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在。当前 `Active P2 = none`。**

原因：
- `Rank 229` 已完成 `P2 -> P3 -> connected_runner_live`；
- `Rank 231` 只到 survivor，未进入 admission；
- 当前没有任何对象处于需要继续做 `effectiveness / cross-asset / time / parameter / honesty` 五项 admission 的阶段。

## 3) rank 合规检查
- `Paper launch queue / connected_runner_live`：`Rank 200 / 201 / 213 / 229` 都有正式 rank
- `Fresh intake slot`：本轮目标是新 digest，不涉及已升层对象，因此不存在无 rank 前排候选
- `Surviving candidate slot`：`none`
- `Active P2 slot`：`none`
- 结论：**本轮无需补新的整数 Rank**

## 4) 为什么这轮不能继续沿用旧 blocked cycle_plan
最近三条优化日志已经把问题说清：
- `2026-03-29_0551_cycle_plan_no_pending_legal_action.md`
- `2026-03-29_0536_no_pending_cycle_item_guard_block.md`
- `2026-03-29_0518_no_pending_legal_cycle_item.md`

这些 no-op 说明旧 `cycle_plan` 已经失真：
- `Rank 231` 的 survivor 动作已经完成；
- 旧 blocked 项不再对应真实前排状态；
- 如果 bot2 不重写 state，bot3 只会继续在“没有合法 pending 动作”的状态里空转。

## 5) 本轮排班为什么是这个顺序
policy 默认顺序：
1. `P3 handoff`
2. `P2 admission/promote/park`
3. `P1 survivor 唯一 follow-up`
4. `fresh intake`
5. 诚实收口后再补更多 fresh intake / conditional intake

当前 runtime truth：
- `P3`：无 queue 头
- `P2`：无 active 对象
- `P1`：无 survivor 对象
- 因此只能切回 fresh intake

所以本轮合法顺序应是：
1. `crossvenue synthetic forward parity`（当前 fresh intake）
2. `volume-shock polarity by coin`（下一条具体 fresh intake）
3. `rank96 park reframe`（conditional fresh intake）
4. `rank76 park reframe`（conditional fresh intake）

## 6) 本轮对 state 的实际写回
已更新 `docs/BOT2_BOT3_STATE.md`：

### Fresh intake slot
- `status` 改为 `pending`
- `current_target` 改为 `research/quant_digests/2026-03-29_0428_crossvenue-synthetic-forward-parity-alpha.md`
- `source_record` 同步改为该 digest
- `latest_result` 仍保留上一条已完成 fresh intake（`Rank 231`）的正式首判结果

### cycle_plan
已重写为 4 项，且前两项都是真实推进动作：
1. `research/quant_digests/2026-03-29_0428_crossvenue-synthetic-forward-parity-alpha.md`
2. `research/quant_digests/2026-03-29_0648_volume-shock-polarity-by-coin-alpha.md`
3. `research/park_reframe/2026-03-26_0218_rank96-park-reframe.md`
4. `research/park_reframe/2026-03-25_2209_rank76-park-reframe.md`

所有新项都满足：
- 只包含 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`

## 7) 一句话结论
这轮真正该做的不是继续围着已收口的 `Rank 231` 打转，而是把 state 改回当前真实前排：前排已清空，立即切回新的具体 fresh intake，先做 `crossvenue synthetic forward parity`，再做 `volume-shock polarity by coin`。