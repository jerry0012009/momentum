# Strategy Review (bot2)

Time: 2026-03-29 11:28 UTC

## 本轮一句话判断
当前 `Paper launch queue` 头仍为空；前排真实优先级已经切到 `Rank 234` 的 `Active P2 admission`、`Rank 235` 的 survivor 唯一 follow-up、以及 `Rank 236` 的 fresh intake 首判。因此本轮必须先围绕 `Rank 234` 做出口导向 admission，再收口 `Rank 235`，最后才轮到 `Rank 236` 的 first verdict。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short`
- 最近 `research/optimization_loop/`：
  - `2026-03-29_1128_no_pending_cycle_plan_guard.md`
  - `2026-03-29_1058_cycle_plan_no_pending_idle_guard.md`
  - `2026-03-29_1045_rank96_distinctness_check_keep_park_reframe.md`
  - `2026-03-29_1033_rank236_rank86b_distinctness_turn_into_fresh_intake.md`
  - `2026-03-29_1027_rank235_richest_venue_routing_intake_keep_p1.md`
  - `2026-03-29_1000_rank234_survivor_horizon_ladder_promote_p2.md`
- 最近 `research/strategy_review/`：
  - `2026-03-29_0947_strategy-review.md`
  - `2026-03-29_0900_strategy-review.md`
- 关键前排证据：
  - `research/optimization_loop/2026-03-29_1000_rank234_survivor_horizon_ladder_promote_p2.md`
  - `research/optimization_loop/2026-03-29_1027_rank235_richest_venue_routing_intake_keep_p1.md`
  - `research/optimization_loop/2026-03-29_1033_rank236_rank86b_distinctness_turn_into_fresh_intake.md`

硬约束遵守：
- 只更新了 `docs/BOT2_BOT3_STATE.md`
- 未改写 policy / brief / operating card / auto loop / cron prompt
- 未自动把 background pool 旧候选拉回前排
- `docs/TODO.md` 未参与本轮排班
- 当前前排对象均已有正式 `Rank`，无需补新的整数 `Rank`

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**就待接线 queue 头而言，仍是空。**

更具体地说：
- `current_target: none`
- `connected_runner_live` 仍保留 `Rank 200 / 201 / 213 / 229`
- 最近没有新的对象被明确推入待接线的 `P3 / Paper launch queue`

所以本轮没有合法的 `P3 launch wiring` 优先项，不能拿 queue 空槽占默认轮次。

### Q2. 本轮 `fresh intake` 是什么？
**本轮 `fresh intake` 是 `Rank 236 / breakout-short-specific short-side admission score-veto`。**

原因：
- `2026-03-29_1033_rank236_rank86b_distinctness_turn_into_fresh_intake.md` 已把原 queue-only 的 `Rank 86b` 正式转成新的 fresh intake 对象，并赋予正式 rank `236`
- 这不是重开旧 `Rank 86`，而是把唯一仍值得测的残余信息诚实压缩成：
  - `breakout-short` 专用
  - `short-only`
  - `penetration / ATR` admission score-veto
- 因此前排里的 fresh intake 已经不是抽象候选，而是明确的 `Rank 236`

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得。上一条 fresh intake 是 `Rank 235 / richest-venue routing × hysteresis funding carry`，它值得那唯一一次 follow-up。**

原因：
- `2026-03-29_1027_rank235_richest_venue_routing_intake_keep_p1.md` 已经把它定成 distinct 的 exact object：
  - 不是泛泛 funding filter
  - 而是 `route 到 richest funding venue + anomaly z-score entry + hysteresis/min-hold exit`
- 当前 blocker 也被压得很窄：
  - 只需要做 `Binance-only` / `routing-only` / `routing+hysteresis` 三臂拆解
  - 直接回答净边独立增量到底来自 routing 还是只是 hysteresis 降 churn

这正符合 policy 对 survivor 的定义：
- 对象 distinct
- blocker 单一且高杠杆
- 值得 1 次最小 decisive follow-up

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**存在：`Active P2 = Rank 234 / multiday MAX lottery XS continuation`；它当前离 `P3` 最近。**

原因：
- `2026-03-29_1000_rank234_survivor_horizon_ladder_promote_p2.md` 已经证明它不该继续停在 survivor：
  - `24h/72h formation` 的 `MAX rank` 在多格上保留成本后 continuation
  - `24h × 4h` 仍保留相对 `plain return-rank` 的独立增量
- 目前没有看到明确 fatal flaw 或唯一明确 re-scope 方向
- 因此它不是更接近 `P1` 的模糊回退，也不是更接近 `P0` 的致命失败
- 更诚实的描述是：
  - 它已进入 admission
  - 当前最近的出口是 `promote_P3`
  - 但还需要先补完 `effectiveness / cross-asset / time / parameter / honesty` 的最小收口

## 3) rank 合规检查
- `Paper launch queue / connected_runner_live`：`Rank 200 / 201 / 213 / 229` 都有 rank
- `Fresh intake slot`：`Rank 236` 已有 rank
- `Surviving candidate slot`：`Rank 235` 已有 rank
- `Active P2 slot`：`Rank 234` 已有 rank
- 结论：**本轮无需补新的整数 `Rank`**

## 4) 本轮排班逻辑
按 policy 默认顺序扫描：
1. `P3 handoff`：无 queue 头，跳过
2. `P2 admission/promote/park`：**有，且必须优先围绕 `Rank 234` 做出口导向 admission**
3. `P1 survivor 唯一一次诚实检查`：**有，`Rank 235` 必须保留前排锁定权**
4. `fresh intake`：当前具体对象已明确为 `Rank 236`
5. `P0 / Background pool`：本轮无须显式占位

据此，已将 `cycle_plan` 重写为：
1. `Rank 234`：先补 `effectiveness / cross-asset`
2. `Rank 234`：再补 `time / parameter / honesty`，直接朝出口决策推进
3. `Rank 235`：做 survivor 唯一一次三臂拆解 follow-up
4. `Rank 236`：做 fresh intake 首判

所有新生成项都满足：
- 只包含 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`

## 5) 为什么这轮没有把 `Rank 234` 直接改写进 P3
因为当前 desk review 看到的，是它**明显已经越过 survivor，足够进入 P2 admission**；但还没有出现“已足够值得 paper trade / paper launch，且 admission 五轴已基本收口、无明显 execution/honesty blocker”的程度。

换句话说：
- 如果这轮读到的是 `Rank 234` admission 已基本补齐但 bot3 还没升，我必须直接把它写进 `P3`
- 但当前最新证据仍停在 `promote_P2`，还没到 bot2 需要触发那条兜底裁判的时点

所以本轮最诚实的动作不是越级升 `P3`，而是把 `Rank 234` 排成**出口导向的 admission 轮**，且明确它当前最近的出口是 `P3`

## 6) 本轮对 runtime truth 的实际写回
已更新 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan`，使其与当前前排状态一致：
- `Rank 234` 两项 admission
- `Rank 235` survivor 唯一 follow-up
- `Rank 236` fresh intake 首判

其余槽位不改：
- `Paper launch queue`：仍为 queue 头为空
- `Fresh intake slot`：仍记录 `Rank 236`
- `Surviving candidate slot`：仍记录 `Rank 235`
- `Active P2 slot`：仍记录 `Rank 234`

## 7) 一句话结论
这轮不能再假装“没有 pending 动作”了：真实前排已经变成 `Rank 234` admission、`Rank 235` survivor 收口、`Rank 236` first verdict；其中最该优先收口的是 `Rank 234`，而且它当前最近的出口是 `P3`。