# Strategy Review (bot2)

Time: 2026-03-29 23:35 UTC

## 本轮一句话判断
`Paper launch queue` 当前没有等待接线的新 queue 头，`Rank 243` 已经成为唯一合法 survivor 且值得消费那唯一一次 follow-up，当前不存在 `Active P2`；因此这轮默认排班必须先做 `Rank 243` 的 executable honesty 决断，再把 fresh intake 切到最新的 `GMADL / direction-aware loss × thresholded state machine`，最后才轮到 `Rank 64 / Rank 96` 两条 conditional reframe。

## 1) 本轮读取与边界
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short`
- 最近 `research/optimization_loop/`：
  - `2026-03-29_2332_rank243_coinmargined_boxspread_rate_keep_p1.md`
  - `2026-03-29_2302_rank242_trend_pullback_correlation_shell_keep_p1.md`
  - `2026-03-29_2249_rank86_cycle_item_blocked_rank222_duplicate.md`
  - `2026-03-29_2228_rank64_park_residual_long_hold_quality_not_frontslot.md`
  - `2026-03-29_2200_market_factor_neutralized_multipair_statarb_background_only.md`
- 最近 `research/strategy_review/`：
  - `2026-03-29_2252_strategy-review.md`
- 为本轮排班补读：
  - `research/optimization_loop/2026-03-29_1230_rank235_p2_exit_rescope_p1_honesty_gap.md`
  - `research/optimization_loop/2026-03-29_2332_rank243_coinmargined_boxspread_rate_keep_p1.md`
  - `research/quant_digests/2026-03-29_2325_gmadl-directional-threshold-btc-alpha.md`
  - `research/park_reframe/INDEX.md`

硬约束遵守：
- 只更新了 `docs/BOT2_BOT3_STATE.md`
- 未改 policy / brief / operating card / auto loop / cron prompt
- 未把 background pool 旧候选自动拉回前排
- 未把 `docs/TODO.md` 当成排班依据
- 当前前排对象都已有正式 `Rank`

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**否。**

runtime truth 是：
- `current_target = none`
- `connected_runner_live = Rank 200 / 201 / 213 / 229`

所以当前没有新的 queue 头等待 `runner + scheduler + 首跑验证` 这类 P3 接线动作。

### Q2. 本轮 `fresh intake` 是什么？
**当前 runtime 里的最新 fresh intake 是 `Rank 243 / coin-margined same-expiry box-spread implied-rate alpha`。**

原因：
- `Fresh intake slot.current_target` 已经写成 `Rank 243`
- `2026-03-29_2332_rank243_coinmargined_boxspread_rate_keep_p1.md` 已给出正式 first verdict = `keep_P1`
- 它的 desk 主语已明确收敛为 `USD-normalized executable box APR`

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得。**

这里的“上一条 fresh intake”就是 `Rank 243`。之所以值得唯一一次 follow-up，是因为：
1. blocker 很单一，而且足够 decisive：`coin-margined 单位归一 + 四腿 executable honesty cut`
2. follow-up 的问题也很硬：统一到同一 USD 口径后，`mid APR` 变成 `executable APR` 还剩不剩真实 pocket
3. 这一步会直接决定出口：
   - 若 survives → 升 `P2`
   - 若 collapses → survivor 用尽后回 `background/P0`

所以它不是“再看看”的拖延项，而是合法且高杠杆的唯一 survivor follow-up。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**当前不存在明确 `Active P2`。**

原因：
- `Active P2 slot.current_target = none`
- 最近一次明确 P2 出口仍是 `Rank 235`，并且已经在 `2026-03-29_1230_rank235_p2_exit_rescope_p1_honesty_gap.md` 中完成 `one-time P2 -> P1 re-scope`
- 此后没有新的对象进入 `Active P2 slot`

因此本轮不存在需要在 `P3 / P1 / P0` 三出口之间做 bot2 兜底裁决的 active P2。

## 3) P3 兜底判断
本轮专门核对了 policy 的兜底要求：如果某个 `Active P2` 已明显达到 paper-trade 门槛，bot2 必须直接推进到 `P3`。

结论：**本轮不触发。**

原因很简单：
- `Active P2 = none`
- `Rank 243` 目前只是 `P1 survivor`，不是 `P2`
- 最近 desk review 没有出现“已经够格 P3 但 bot3 尚未升级”的对象

## 4) rank 合规检查
- `Paper launch queue / connected_runner_live`：都有正式 rank
- `Fresh intake slot`：`Rank 243`
- `Surviving candidate slot`：`Rank 243`
- `Active P2 slot`：`none`

结论：**本轮无需补新的 `Rank`。**

## 5) 本轮 `cycle_plan` 重写逻辑
按 policy 默认顺序扫描：
1. **P3 handoff**：无 queue 头，跳过
2. **P2 admission/promote/park**：无 `Active P2`，跳过
3. **P1 survivor**：有，而且只能是 `Rank 243`，必须排第一
4. **fresh intake**：只有在 survivor 已经诚实排入前部后，才可切回新的具体 fresh intake
5. **conditional fresh intake**：预算有余时再给 `Rank 64 / Rank 96`

因此，本轮最诚实的 4 项是：
1. `Rank 243 / coin-margined same-expiry box-spread implied-rate alpha` survivor follow-up
2. `direction-aware loss × thresholded long/short state machine on BTC` fresh intake
3. `Rank 64 park residual -> long-side-only hold-quality admission score`
4. `Rank 96 park residual -> short-side second-touch + candle-quality admission-delay`

## 6) 为什么是这 4 项
### 6.1 Rank 243 survivor follow-up 必须排第一
因为：
- survivor 槽位已经被 `Rank 243` 占住
- policy 明写 survivor follow-up 在 fresh intake 之前
- 这次 follow-up 不是低杠杆重复，而是唯一剩余 blocker：`USD-normalized executable APR` 是否仍然成立

若此时跳过它直接去看新 intake，就是前排失序。

### 6.2 GMADL / direction-aware loss × thresholded state machine 作为新的首个 fresh intake
这条排第二，因为：
- 它是最新 digest 里最像独立 raw alpha 的新对象
- 主语清楚：不是泛 `Informer`，而是 `direction-aware loss × thresholded long/short/flat state machine`
- 它允许清楚做 desk 级最小对照：`MSE vs direction-aware loss`、`loss vs threshold abstain`
- 跟现有前排对象正交，不是 momentum/pairs/funding/options 的换壳复读

### 6.3 Rank 64 仍保留为第 3 项 conditional fresh intake
因为：
- 它仍是 `derived_hypothesis_drafted`
- 但最近 `2026-03-29_2228` 已明确提醒：这条残余与既有 `Rank 101 / Rank 106` long-side hold-quality family 重叠很高
- 所以只能排在前排 survivor 与新鲜新材料之后，做一次是否仍有独立对象边界的诚实检查

### 6.4 Rank 96 作为第 4 项，比继续写 Rank 86 更诚实
因为：
- `Rank 86` 最近已经再次被明确记成 `duplicate of Rank 222`
- 继续把 `Rank 86` 排入只会重复 blocked
- `Rank 96` 在 `park_reframe/INDEX.md` 里仍是未消费的 `soft_reframe_candidate`
- 它保留的 residual axis 也很清楚：`short-side second-touch + candle-quality admission-delay`

## 7) 已写回 runtime truth
本轮已更新 `docs/BOT2_BOT3_STATE.md`，仅重写 `cycle_plan`：

1. `Rank 243` survivor follow-up：
   - 统一 USD 口径
   - 对照 `repo_raw_profit / mid APR / executable APR`
   - 直接回答升 `P2` 还是 survivor 用尽回 background
2. `direction-aware loss × thresholded state machine on BTC` fresh intake
3. `Rank 64` conditional fresh intake
4. `Rank 96` conditional fresh intake

所有新生成项都满足：
- `result = none`
- `status = pending`

## 8) 一句话结论
这轮最关键的不是找更多新东西，而是先把已经锁住 survivor 槽位的 `Rank 243` 做掉：**它若在 executable 口径下还活，就升 `P2`；若不活，就诚实回 background。** 只有这一步被排到前面后，新的首个 intake 才该轮到 `GMADL / direction-aware loss × thresholded state machine`。