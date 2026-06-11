# Strategy Review (bot2)

Time: 2026-03-28 07:57 UTC

## 本轮一句话判断
`Paper launch queue` 仍为空；当前 front chain 仍是 `Rank 213` 的 `P2 admission` 在前、`Rank 214` 的唯一 survivor follow-up 在后；新出现的 `2026-03-28_0756_tether-mint-whalealert-btc-impulse-alpha.md` 作为最新且合法的 raw-alpha fresh intake，应当插到 fresh-intake 头部，但还不能越过前排收口。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short`
- 最近 `research/optimization_loop/`：
  - `2026-03-28_0733_rank214_xs_relative_strength_fullstack_baseline_intake_keep_p1.md`
  - `2026-03-28_0729_rank213_survivor_followup_promote_p2.md`
  - `2026-03-28_0650_1s_book_horizon_sweep_fresh_intake_blocked_already_rank202_background.md`
  - `2026-03-28_0621_rank213_largecap_xs_momentum_shortleg_veto_intake_keep_p1.md`
- 最近 `research/strategy_review/`：
  - `2026-03-28_0736_strategy-review.md`
  - `2026-03-28_0651_strategy-review.md`
- 本轮新增补读：
  - `research/quant_digests/2026-03-28_0756_tether-mint-whalealert-btc-impulse-alpha.md`

硬约束遵守：
- 只更新 `docs/BOT2_BOT3_STATE.md`
- 未改 policy / brief / operating card / auto loop / cron prompt
- 未自动把 background pool 旧候选拉回前排
- 未把 `docs/TODO.md` 当成本轮排班依据
- 当前前排对象都有正式 `Rank`，无需补号

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**否，当前为空。**
- `current_target = none`
- `Rank 200`、`Rank 201` 都已经是 `connected_runner_live`
- 因此本轮没有 queue-side `P3 launch wiring` 动作需要排在最前

### Q2. 本轮 `fresh intake` 是什么？
**在当前前排链条之后，fresh-intake 头部应改为 `research/quant_digests/2026-03-28_0756_tether-mint-whalealert-btc-impulse-alpha.md`。**
原因：
- 当前存在明确 `Active P2 = Rank 213`
- 当前存在明确 `Surviving candidate = Rank 214`
- policy 明确要求已有前排对象的收口优先级永远高于新的发现
- 但在 fresh-intake 自己的队列里，应优先最近新的 repo / paper / alpha report；`0756` 比 `0608`、`0704` 更新，因此应升为 fresh-intake 头部

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得。**
上一条 fresh intake 是 `Rank 214 / XS relative-strength full-stack baseline`：
- 首判已明确为 `keep_P1`
- standalone repo 结果为负，这一点已经诚实确认
- 但它留下了一个可复现、可插拔的 `XS momentum full-stack baseline shell`
- 这正好适合承接当前 desk 已显出信息量的 `jump-veto / rel-volume / sentiment` 增量件
- 因此它完全配得上 survivor 的那唯一一次 follow-up；并且在收口前拥有 survivor 前排锁定权

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**存在，当前明确 `Active P2` 是 `Rank 213 / large-cap XS momentum × short-leg jump veto`；它离 `P3` 最近。**
原因：
- `2026-03-28_0729` 已正式把它从 survivor 升到 `P2`
- 最新证据已经回答了关键 blocker：更宽的 `30` 币 liquid alt-perp universe 下，plain XS momentum 的主要失败源是 short-leg single-name jump concentration，而 `jump veto` 的改善明显强于 `short cap` 与 `inverse-vol`
- 这意味着它当前离 `P3` 最近，而不是 `P1/P0`
- 但 admission 五项尚未被正式补齐到可以让 bot2 直接兜底写成 `P3`；因此这轮最诚实的动作仍是第一优先级做 `P2 admission` 收口，而不是越级 paper-launch

## 3) rank 合规检查
- `Paper launch queue`: none
- `Fresh intake slot`: `Rank 214`，有 rank
- `Surviving candidate slot`: `Rank 214`，有 rank
- `Active P2 slot`: `Rank 213`，有 rank

结论：
- 当前不存在前排对象已达 `keep_P1 / P2 / P3` 但无正式 rank 的违规情况
- 本轮无需补新的整数 `Rank`

## 4) 本轮排班结论
按 policy 默认顺序扫描：
1. `P3 / Paper launch queue`：空，无动作
2. `P2 / Active P2`：有，且必须排第一 —— `Rank 213 admission`
3. `P1 / Surviving candidate`：有，且必须排第二 —— `Rank 214` 唯一 survivor follow-up
4. `fresh intake`：前两项诚实排入后，再排最新合法具体对象

因此本轮 `cycle_plan` 应写成：
1. `Rank 213 / large-cap XS momentum × short-leg jump veto`
   - 正式 `P2 admission`
2. `Rank 214 / XS relative-strength full-stack baseline`
   - 唯一 survivor follow-up
3. `research/quant_digests/2026-03-28_0756_tether-mint-whalealert-btc-impulse-alpha.md`
   - 最新 raw-alpha fresh intake
4. `research/quant_digests/2026-03-28_0608_return-relvol-xs-momentum-alpha.md`
   - 条件性下一条 fresh intake

`2026-03-28_0704_liquidity-ranked-ema-trend-fullstack.md` 本轮被挤出默认 4 项预算，不是因为它失效，而是因为 `0756` 更新、更符合“最近新 repo/paper/alpha 报告优先”的 fresh-intake 顺序。

## 5) 是否需要 bot2 直接兜底推进到 P3？
**这轮仍不需要。**
- `Rank 213` 已明显是当前最接近 `P3` 的对象
- 但 desk review 还没有硬到可以绕过 admission 收口、直接写成 `Paper launch queue`
- 因此 bot2 本轮的职责是把它牢牢排在 `P2 admission` 第一位，而不是继续开放式研究，也不是过早伪装成已够格 `P3`

## 6) 对 state 的实际写回
本轮已更新 `docs/BOT2_BOT3_STATE.md`，仅重写 `cycle_plan`：
1. `Rank 213` 的 `P2 admission`
2. `Rank 214` 的唯一 survivor follow-up
3. `0756 tether mint / Whale Alert / BTC impulse` fresh intake
4. `0608 return × relative-volume XS momentum` fresh intake

所有新计划项均满足：
- 只包含 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`

## 7) 一句话结论
这轮真正的调度变化只有一个：**前排链条不变，但 fresh-intake 头部该从旧的 `0608/0704` 组合，更新成最新的 `0756 tether mint event alpha` 在前、`0608 return×relvol` 在后。**
