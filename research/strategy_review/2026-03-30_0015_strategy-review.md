# Strategy Review (bot2)

Time: 2026-03-30 00:15 UTC

## 本轮一句话判断
`Paper launch queue` 当前为空，最新 `fresh intake`/唯一合法 `survivor` 是 `Rank 244 / direction-aware loss × thresholded BTC directional state machine`，它值得那唯一一次 follow-up；当前不存在 `Active P2`，因此本轮默认排班必须先把 `Rank 244` 做成 survivor 出口决断，再切到新的 conditional fresh intake（先 `Rank 96`，后 `Rank 76 / Rank 101`）。

## 1) 本轮读取与边界
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short`
- 最近 `research/optimization_loop/`：
  - `2026-03-30_0012_rank64_conditional_intake_keep_park_reframe.md`
  - `2026-03-30_0000_rank244_gmadl_directional_threshold_btc_keep_p1.md`
  - `2026-03-29_2345_rank243_survivor_followup_background.md`
  - `2026-03-29_2332_rank243_coinmargined_boxspread_rate_keep_p1.md`
  - `2026-03-29_2302_rank242_trend_pullback_correlation_shell_keep_p1.md`
  - `2026-03-29_2249_rank86_cycle_item_blocked_rank222_duplicate.md`
  - `2026-03-29_2228_rank64_park_residual_long_hold_quality_not_frontslot.md`
  - `2026-03-29_2200_market_factor_neutralized_multipair_statarb_background_only.md`
- 最近 `research/strategy_review/`：
  - `2026-03-29_2335_strategy-review.md`
  - `2026-03-29_2252_strategy-review.md`
- 为本轮排班补读：
  - `research/optimization_loop/2026-03-30_0000_rank244_gmadl_directional_threshold_btc_keep_p1.md`
  - `research/optimization_loop/2026-03-30_0012_rank64_conditional_intake_keep_park_reframe.md`
  - `research/optimization_loop/2026-03-29_2345_rank243_survivor_followup_background.md`
  - `research/optimization_loop/2026-03-29_1230_rank235_p2_exit_rescope_p1_honesty_gap.md`
  - `research/park_reframe/INDEX.md`

硬约束遵守：
- 只更新了 `docs/BOT2_BOT3_STATE.md`
- 未改 policy / brief / operating card / auto loop / cron prompt
- 未把 background pool 旧候选自动拉回前排
- 未把 `docs/TODO.md` 当成排班依据
- 当前前排对象都有正式 `Rank`

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**否。**

runtime truth 仍是：
- `current_target = none`
- `connected_runner_live = Rank 200 / 201 / 213 / 229`

因此当前没有新的 queue 头等待 `runner + scheduler + 首跑验证` 这类 P3 接线动作。

### Q2. 本轮 `fresh intake` 是什么？
**当前 runtime 里的最新 fresh intake 是 `Rank 244 / direction-aware loss × thresholded BTC directional state machine`。**

原因：
- `Fresh intake slot.current_target` 已写成 `Rank 244`
- `2026-03-30_0000_rank244_gmadl_directional_threshold_btc_keep_p1.md` 已给出正式 first verdict = `keep_P1`
- 它的 desk 主语已经锁到：
  - `next-bar return forecast`
  - `direction-aware loss`
  - `thresholded long / short / flat admission`
  - `cost-aware abstain`
  这四件事组成的 BTC 单币短窗 directional raw alpha，而不是泛 `Informer` 模型复述。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得。**

这里的“上一条 fresh intake”就是 `Rank 244`。它值得 survivor 那唯一一次 follow-up，因为：
1. blocker 单一而 decisive：`direction-aware loss` 的增量到底来自 loss 本身，还是主要来自 `threshold abstain` 的稀疏交易；
2. follow-up 的问题够硬：必须在同一 BTC 数据、同一特征、同一状态机、同一成本口径下，把 `MSE vs direction-aware loss` 与 `loss effect vs threshold abstain effect` 拆开；
3. 这一步会直接决定出口：
   - 若 survives → 升 `P2`
   - 若 collapses → survivor 用尽后回 `background/P0`

所以这不是“再补一点看看”的拖延项，而是合法且高杠杆的唯一 survivor follow-up。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**当前不存在明确 `Active P2`。**

原因：
- `Active P2 slot.current_target = none`
- 最近一次明确 P2 出口仍是 `Rank 235`，并且已经在 `2026-03-29_1230_rank235_p2_exit_rescope_p1_honesty_gap.md` 中完成 `one-time P2 -> P1 re-scope`
- 自此之后没有新的对象进入 `Active P2 slot`

因此本轮不存在需要在 `P3 / P1 / P0` 三出口之间做 bot2 兜底裁决的 active P2。

## 3) P3 兜底判断
本轮专门核对了 policy 的兜底要求：如果某个 `Active P2` 已明显达到 paper-trade 门槛，bot2 必须直接推进到 `P3`。

结论：**本轮不触发。**

原因：
- `Active P2 = none`
- `Rank 244` 当前只是 `P1 survivor`，不是 `P2`
- 最近 desk review 没有出现“已经够格 P3 但 bot3 尚未升级”的对象

## 4) rank 合规检查
- `Paper launch queue / connected_runner_live`：都有正式 rank
- `Fresh intake slot`：`Rank 244`
- `Surviving candidate slot`：`Rank 244`
- `Active P2 slot`：`none`

结论：**本轮无需补新的 `Rank`。**

## 5) 本轮 `cycle_plan` 重写逻辑
按 policy 默认顺序扫描：
1. **P3 handoff**：无 queue 头，跳过
2. **P2 admission/promote/park**：无 `Active P2`，跳过
3. **P1 survivor**：有，而且只能是 `Rank 244`，必须排第一
4. **fresh intake**：只有在 survivor 已经诚实排入前部后，才可切回新的具体对象
5. **conditional fresh intake**：预算有余时再给 `Rank 96 / Rank 76 / Rank 101`

因此，本轮最诚实的 4 项是：
1. `Rank 244 / direction-aware loss × thresholded BTC directional state machine` survivor follow-up
2. `Rank 96 park residual -> short-side second-touch + candle-quality admission-delay`
3. `Rank 76 park residual -> fixed UTC bucket mode switch`
4. `Rank 101 park residual -> long-side hold-quality residual note`

## 6) 为什么是这 4 项
### 6.1 Rank 244 survivor follow-up 必须排第一
因为：
- survivor 槽位已经被 `Rank 244` 占住
- policy 明写 survivor follow-up 在 fresh intake 之前
- 这次 follow-up 不是低杠杆重复，而是唯一剩余 blocker：`direction-aware loss` 的成本后增量是否独立存在

若此时跳过它直接去看新 intake，就是前排失序。

### 6.2 Rank 96 作为 survivor 之后的首个 conditional fresh intake
它排第二，因为：
- `research/park_reframe/INDEX.md` 里它仍是未消费的 `soft_reframe_candidate`
- 主语清楚：`short-side second-touch + candle-quality admission-delay`
- 与这轮刚被收口为不独立的 `Rank 64` 不是同一 long-side residual 轴
- 最近没有被明确判成重复或 blocked

### 6.3 Rank 76 比继续写 Rank 64 / Rank 86 更诚实
因为：
- `Rank 64` 刚在 `2026-03-30_0012` 被再次明确记成 `继续留在 park/reframe`
- `Rank 86` 最近已再次被明确记成 `duplicate of Rank 222`
- `Rank 76` 仍是未消费的 `soft_reframe_candidate`，而且它保留的残余轴足够具体：`fixed UTC bucket mode switch`
- 但它又必须接受严厉 distinctness 检查，不能偷换成泛时钟 family 或借 `Rank 200 / 201` 的成功直接蹭前排

### 6.4 Rank 101 放在第 4 项，只作剩余预算里的诚实检查
因为：
- 它也是未消费的 `soft_reframe_candidate`
- 但和 `Rank 64 / Rank 106` 的 long-side hold-quality family 重叠较高
- 所以它不能排到 `Rank 96 / Rank 76` 前面，只能放在预算尾部做一次“到底能不能脱离既有 family”的诚实检查

## 7) 已写回 runtime truth
本轮已更新 `docs/BOT2_BOT3_STATE.md`，重写 `cycle_plan` 为：
1. `Rank 244` survivor follow-up：
   - 拆开 `MSE vs direction-aware loss`
   - 拆开 `loss effect vs threshold abstain effect`
   - 直接回答升 `P2` 还是 survivor 用尽回 background
2. `Rank 96` conditional fresh intake
3. `Rank 76` conditional fresh intake
4. `Rank 101` conditional fresh intake

所有新生成项都满足：
- `result = none`
- `status = pending`

## 8) 一句话结论
这轮的关键不是继续堆新发现，而是先把已经锁住 survivor 槽位的 `Rank 244` 做成出口决断：**如果 `direction-aware loss` 在固定阈值与诚实 friction 下仍比 `MSE` 留下清楚成本后增量，就升 `P2`；如果优势主要来自 abstain 稀疏化或一上成本就塌，就诚实回 background。** 只有这一步被排到前面后，后面的 `Rank 96 / Rank 76 / Rank 101` intake 才排得住。