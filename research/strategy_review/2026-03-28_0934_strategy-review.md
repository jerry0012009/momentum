# Strategy Review (bot2)

Time: 2026-03-28 09:34 UTC

## 本轮一句话判断
`Paper launch queue` 现已非空，且头部 `Rank 213` 已经明确够格进入 `P3 / Paper launch queue`，因此本轮默认排班必须先做它的 `P3 launch wiring`；`Rank 216` 作为新的唯一 survivor 继续锁住前排第二位；只有这两项诚实排入后，才轮到最新的 fresh intake。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short --branch`
- 最近 `research/optimization_loop/`：
  - `2026-03-28_0934_rank217_intake_blocked_by_rank216_survivor_lock.md`
  - `2026-03-28_0925_rank216_hyperliquid_fundingaware_tsmom_intake_keep_p1.md`
  - `2026-03-28_0919_rank215_survivor_followup_close_to_background.md`
  - `2026-03-28_0852_rank213_p2_exit_promote_p3_deploy_ready_spec.md`
- 最近 `research/strategy_review/`：
  - `2026-03-28_0849_strategy-review.md`
- 本轮补读：
  - `research/quant_digests/2026-03-28_0903_drift-hyperliquid-basis-pocket.md`

硬约束遵守：
- 只更新 `docs/BOT2_BOT3_STATE.md`
- 未改 policy / brief / operating card / auto loop / cron prompt
- 未自动把 background pool 旧候选拉回前排
- 未把 `docs/TODO.md` 当成本轮排班依据
- 当前前排对象都有正式 `Rank`，无需补号

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**是，当前非空。**
- `current_target = Rank 213 / large-cap XS momentum × short-leg jump veto`
- `latest_result_record = research/optimization_loop/2026-03-28_0852_rank213_p2_exit_promote_p3_deploy_ready_spec.md`
- `Rank 200`、`Rank 201` 继续留在 `connected_runner_live`
- 因此本轮第一优先级不再是 `P2 admission`，而是 **`Rank 213` 的最小 `P3 launch wiring`**

### Q2. 本轮 `fresh intake` 是什么？
**本轮新的 fresh-intake 头部应是 `research/quant_digests/2026-03-28_0903_drift-hyperliquid-basis-pocket.md`。**
原因：
- 当前不存在 `Active P2`
- 当前存在明确 `Paper launch queue` 头部 `Rank 213`
- 当前存在明确 `Surviving candidate = Rank 216`
- policy 明确要求已有前排对象收口优先级高于新的发现
- 在剩余 intake 队列里，`0903` 比 `0704` 更新，因此它是最靠前、也最具体的 fresh intake 对象

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得。**
上一条 fresh intake 是 `Rank 216 / Hyperliquid funding-aware multi-window TSMOM × edge gate`：
- 首判已经明确为 `keep_P1`
- 它留下来的不是空泛“趋势还行吗”，而是一个可独立判分的 perp 组合：`多窗口 TSMOM + directional funding penalty + edge gate`
- 当前 blocker 也已经被压缩得很集中：`OI_USD universe` 口径与 `funding realism`
- 这正好符合 policy 允许的那唯一一次便宜且诚实的 decisive follow-up

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在，当前 `Active P2 = none`。**
- `Rank 213` 已在 `2026-03-28_0852` 从 `P2` 正式收口并升级到 `P3 / Paper launch queue`
- 当前前排里已经没有待 admission 的 `Active P2` 对象
- 因此本轮不存在“某个 Active P2 离哪个出口最近”的比较问题；最接近出口的前排动作已变成 `Rank 213` 的 `P3 handoff / launch wiring`

## 3) rank 合规检查
- `Paper launch queue`: `Rank 213`，有 rank
- `Fresh intake slot`: `Rank 216`，有 rank
- `Surviving candidate slot`: `Rank 216`，有 rank
- `Active P2 slot`: none

结论：
- 当前不存在前排对象已达 `keep_P1 / P2 / P3` 但无正式 rank 的违规情况
- 本轮无需补新的整数 `Rank`

## 4) 本轮排班结论
按 policy 默认顺序扫描：
1. `P3 / Paper launch queue`：有，且必须排第一 —— `Rank 213` 的最小 `launch wiring`
2. `P2 / Active P2`：无，不占位
3. `P1 / Surviving candidate`：有，且必须排第二 —— `Rank 216` 的唯一 survivor follow-up
4. `fresh intake`：前两项诚实排入后，再排最新合法具体对象

因此本轮 `cycle_plan` 应写成：
1. `Rank 213 / large-cap XS momentum × short-leg jump veto`
   - 做最小 `P3 launch wiring` 收口，目标是 runner / scheduler / 首跑验证的明确接线路径，不再继续研究 alpha 本体
2. `Rank 216 / Hyperliquid funding-aware multi-window TSMOM × edge gate`
   - 做唯一 survivor follow-up，直接回答修正 `OI_USD` universe 与 funding-realism 后，它是 `promote_P2` 还是 `keep_P1 后转 background`
3. `research/quant_digests/2026-03-28_0903_drift-hyperliquid-basis-pocket.md`
   - 最新 fresh intake
4. `research/quant_digests/2026-03-28_0704_liquidity-ranked-ema-trend-fullstack.md`
   - 条件性下一条 fresh intake

所有新计划项均满足：
- 只包含 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`

## 5) 是否需要 bot2 直接兜底推进到 P3？
**这轮已经需要，而且已在 state 中兑现。**
- `Rank 213` 的 `2026-03-28_0852` desk evidence 已经足够清楚：它不只是还值得研究，而是已经出现可冻结的 deploy-ready sweet spot（`f64_h12_floor150_mult2p0` 前后半样本均为正，成本后 net mean 为 `+22.03 bps/rebalance`）
- 按 policy，若 bot3 没升、但 desk review 已清楚表明对象足够值得进入 `paper trade / paper launch`，bot2 必须直接推进到 `P3`
- 当前 state 也已反映这一点：`Rank 213` 不再留在 `Active P2`，而是直接进入 `Paper launch queue`

## 6) 对 state 的实际写回
本轮已更新 `docs/BOT2_BOT3_STATE.md`，重写 `cycle_plan` 为：
1. `Rank 213` 的 `P3 launch wiring`
2. `Rank 216` 的唯一 survivor follow-up
3. `0903 drift-hyperliquid basis pocket` fresh intake
4. `0704 liquidity-ranked EMA trend full-stack` fresh intake

## 7) 一句话结论
这轮真正的变化是：**`Rank 213` 已不允许再以 `P2` 名义被拖延，必须先做 `P3` 接线；`Rank 216` 的唯一 survivor 继续锁住第二位；新的 fresh intake 头部切到 `0903 Drift↔Hyperliquid basis pocket`。**
