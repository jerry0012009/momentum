# Strategy Review (bot2)

Time: 2026-03-29 21:31 UTC

## 本轮一句话判断
`Paper launch queue` 为空；本轮 `fresh intake` 已是 `Rank 241 / same-asset executable-spread veto`，且它值得也只值得那唯一一次 survivor follow-up；当前不存在明确 `Active P2`，因此本轮默认排班必须先把 `Rank 241` 的 survivor 收口排在最前，再切回新的具体 fresh intake，其中最新最像独立 raw alpha 的对象是 `market-factor neutralized multi-pair stat-arb`。

## 1) 本轮读取与边界
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short`
- 最近 `research/optimization_loop/`：
  - `2026-03-29_2129_rank86_reframe_cycle_item_blocked_duplicate_of_rank222.md`
  - `2026-03-29_2103_rank241_amm_exec_veto_sameasset_leadlag_keep_p1.md`
  - `2026-03-29_2059_shortleg_momentum_crash_veto_intake_background_only.md`
  - `2026-03-29_2032_rank240_survivor_followup_background.md`
  - `2026-03-29_1230_rank235_p2_exit_rescope_p1_honesty_gap.md`
- 最近 `research/strategy_review/`：
  - `2026-03-29_2037_strategy-review.md`
- 为重排本轮 `cycle_plan`，补读：
  - `research/quant_digests/2026-03-29_2121_market-factor-neutralized-multipair-statarb.md`
  - `research/quant_digests/2026-03-29_1619_amm-book-slippage-veto-sameasset-leadlag.md`

硬约束遵守：
- 本轮只更新 `docs/BOT2_BOT3_STATE.md`
- 未改 policy / brief / operating card / auto loop / cron prompt
- 未把 background pool 旧候选自动拉回前排
- 未把 `docs/TODO.md` 当排班依据
- 当前前排对象无缺失正式 `Rank`；无需补新的整数 `Rank`

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**否。**

当前 state 仍是：
- `Paper launch queue.current_target = none`
- `connected_runner_live = Rank 200 / 201 / 213 / 229`
- 最近没有新的 queue 头对象等待 wiring

所以本轮没有合法的 `P3 launch wiring` 默认优先项。

### Q2. 本轮 `fresh intake` 是什么？
**本轮 fresh intake 是 `Rank 241 / same-asset executable-spread veto`。**

原因：
- `2026-03-29_2103_rank241_amm_exec_veto_sameasset_leadlag_keep_p1.md` 已明确把 `AMM executable-price reconstruction × slippage/gas veto` 正式 intake 为 `Rank 241`
- 它不是泛泛的 `CEX 领先 DEX` 摘要，而是 `same-asset relative-value / lead-lag` 家族的 shared execution veto
- 该对象已得到 first verdict：`keep_P1`

因此，运行态里最新且有效的 fresh intake 已经从先前的 `Rank 240` 切换为 `Rank 241`。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得，而且现在正该占用那唯一一次。**

这里的“上一条 fresh intake”就是 `Rank 241`。

理由：
- 它的主语足够清楚、独立且单轮可证伪：`naive mid-gap` vs `executable spread after fee/gas/slippage`
- 它服务的是 same-asset / cross-venue relative-value 家族明显缺失的一层 shared execution honesty
- 当前最关键、也最便宜的一次 decisive follow-up 很明确：在至少一条已落库策略线上回答 `with veto vs without veto` 是否留下策略级净增量

所以答案不是“继续无限 follow-up”，而是：**值得那唯一一次，而且 survivor 槽位必须先锁给它；若这次还拿不出策略级 A/B 净增量，就应按预算用尽回 `background/P0`。**

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**当前不存在明确 `Active P2`。**

原因：
- `Active P2 slot.current_target = none`
- 最近一次明确的 P2 出口判定是 `Rank 235` 在 `2026-03-29_1230_rank235_p2_exit_rescope_p1_honesty_gap.md` 中执行了 `one-time P2 -> P1 re-scope`
- 之后没有新的对象进入 `Active P2 slot`

因此本轮不存在需要在 `P3 / P1 / P0` 三出口中做即时裁决的 active P2。

## 3) P3 兜底判断
本轮专门核对了 policy 的兜底要求：若某个 `Active P2` 已明显够格 `P3`，bot2 必须直接推进。

结论：**本轮不触发。**

原因：
- `Active P2 = none`
- 最近最接近 P2 出口的 `Rank 235` 已被诚实审计收口为 `P2 -> P1 re-scope`
- `Rank 241` 只是刚完成 first verdict 的 `keep_P1` fresh intake，不是 P2
- 没有任何对象满足“desk review 已清楚表明足够进入 paper trade，但 bot3 尚未升级”的条件

## 4) rank 合规检查
- `Paper launch queue / connected_runner_live`：现有对象均带 rank
- `Fresh intake slot`：`Rank 241`
- `Surviving candidate slot`：本轮应切换为 `Rank 241`
- `Active P2 slot`：`none`

结论：**本轮无需补新的 `Rank`，但必须把 survivor 槽从旧的 `none / Rank 240 已收口` 改写为当前合法 survivor `Rank 241`。**

## 5) 本轮 `cycle_plan` 重写逻辑
按 policy 默认顺序扫描：
1. **P3 handoff**：无 queue 头，跳过
2. **P2 admission/promote/park**：无 `Active P2`，跳过
3. **P1 survivor**：有，且唯一合法对象是 `Rank 241`，必须排第一
4. **fresh intake**：只有在 `Rank 241` 的 survivor 已诚实排进前部后，才可切回新的具体 intake

因此本轮 `cycle_plan` 最诚实的 4 项应是：
1. `Rank 241 / same-asset executable-spread veto` 的唯一 survivor follow-up
2. `market-factor neutralized multi-pair stat-arb`
3. `Rank 64 park residual -> long-side-only hold-quality admission score`
4. `Rank 86 park residual -> breakout-short-specific short-side admission score / veto`

## 6) 为什么是这 4 项
### 6.1 Rank 241 survivor follow-up
这项必须排第一，不是偏好问题，而是 policy：
- `Rank 241` 是最新 fresh intake
- 它已首判 `keep_P1`
- 所以其唯一一次 survivor follow-up 默认享有前排锁定权
- 不能让新的 intake 覆盖掉这个 survivor 槽位

而且这次 follow-up 的问题非常硬：
- 它不是重复讲论文
- 而是必须回答 `with executable veto vs naive mid-gap` 是否在至少一条已落库 same-asset / cross-venue 策略线上留下策略级净增量

### 6.2 market-factor neutralized multi-pair stat-arb
这条应作为本轮第一个新 fresh intake，因为：
- 它是最近新 paper 中最像完整 raw alpha 骨架的一条
- 主语不是泛 pairs，而是 **先剥离共同市场因子，再对 stationary factor 做 basket relative-value 排序**
- 它和既有 pair / stat-arb 家族有关联，但本体明显更接近 `market-mode neutralized basket stat-arb`，具有新的独立主语
- intake 的最小实验边界也清楚：`raw return ranking` vs `beta-neutralized ranking` vs `beta-neutralized + stationarity gate`

### 6.3 Rank 64 park residual
保留为第 3 项 conditional fresh intake，理由：
- 当前前排链条在 survivor + 最新新 paper 之后才轮到 park residual
- 它仍是合法 `derived_hypothesis_drafted`
- 但与 long-side hold-quality 家族有明显重叠风险，所以只适合放在 survivor 与最新新材料之后

### 6.4 Rank 86 park residual
放第 4 项而不是更靠前，理由也一样：
- 它只能作为条件性新 intake 候选
- 且最近已有 `2026-03-29_2129_rank86_reframe_cycle_item_blocked_duplicate_of_rank222.md`，说明重复风险高
- 因此最多占最后一个预算位，不应压过 `Rank 241` survivor 或最新的新 paper

## 7) 已写回 runtime truth
本轮已更新 `docs/BOT2_BOT3_STATE.md`：
- 将 `Surviving candidate slot` 改写为 `Rank 241 / same-asset executable-spread veto`
- 将 `followup_budget_remaining` 改为 `1`
- 把旧的 `Rank 240` survivor 收口内容移出当前 survivor 槽位
- 重写 `cycle_plan` 为当前合法顺序：
  1. `Rank 241` survivor follow-up
  2. `market-factor neutralized multi-pair stat-arb`
  3. `Rank 64` conditional fresh intake
  4. `Rank 86` conditional fresh intake
- 所有新生成项都满足：`result = none`、`status = pending`

## 8) 一句话结论
这轮真正该做的不是继续空转，也不是直接跳去新对象，而是先把 `Rank 241` 的唯一 survivor follow-up 用掉；只有它被诚实排进前部之后，才轮到把 `market-factor neutralized multi-pair stat-arb` 作为新的 fresh intake 拿进来。