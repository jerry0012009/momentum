# Strategy Review (bot2)

Time: 2026-03-28 07:36 UTC

## 本轮一句话判断
`Paper launch queue` 仍为空；本轮 legal front chain 明确是 `Rank 213 / large-cap XS momentum × short-leg jump veto` 的 `P2 admission` 在前，`Rank 214 / XS relative-strength full-stack baseline` 的唯一 survivor follow-up 在后，剩余预算才给新的具体 fresh intake；当前没有足够硬的新证据要求 bot2 越过 bot3 直接把 `Rank 213` 升到 `P3`。

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
  - `2026-03-28_0651_strategy-review.md`
  - `2026-03-28_0553_strategy-review.md`
- 本轮补读的新 intake 对象：
  - `research/quant_digests/2026-03-28_0608_return-relvol-xs-momentum-alpha.md`
  - `research/quant_digests/2026-03-28_0704_liquidity-ranked-ema-trend-fullstack.md`

硬约束遵守：
- 只更新了 `docs/BOT2_BOT3_STATE.md`
- 未改 policy / brief / operating card / auto loop / cron prompt
- 未自动把 background pool 旧候选拉回前排
- 未把 `docs/TODO.md` 当作调度依据
- 当前前排对象都已有正式 `Rank`，无需补号

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**否，当前为空。**
- queue 头部仍是 `none`
- `Rank 200` 与 `Rank 201` 都已是 `connected_runner_live`
- 因此本轮没有 `P3 launch wiring` 动作可排在最前

### Q2. 本轮 `fresh intake` 是什么？
**本轮首先不是 fresh intake，而是前排已有对象的收口；在它们之后，首条 fresh intake 是 `research/quant_digests/2026-03-28_0608_return-relvol-xs-momentum-alpha.md`。**
原因：
- 当前存在明确 `Active P2 = Rank 213`
- 当前存在明确 `Surviving candidate = Rank 214`
- 按 policy，已有前排对象的收口优先级永远高于新的发现
- 因此前两项必须先排 `Rank 213 admission` 与 `Rank 214` 的唯一 survivor follow-up；新的 fresh intake 只能从第三项开始，头部是 `0608 return × relative-volume XS momentum`

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得。**
上一条 fresh intake 是 `Rank 214 / XS relative-strength full-stack baseline`：
- 它已经在首判里被明确写成 `keep_P1`
- 负收益结论也已经诚实确认：它不是现成可升 `P2` 的 standalone alpha
- 但它留下了一个很干净的 `XS momentum full-stack baseline shell`，而且这个壳正好能承接 desk 当前最有信息量的增量件（`jump-veto / rel-volume / sentiment`）
- 因此它完全符合 survivor 的唯一一次 follow-up 条件：问题清楚、成本低、且这次 follow-up 的结果会直接决定 `promote_P2` 还是回 background

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**存在，当前明确 `Active P2` 是 `Rank 213 / large-cap XS momentum × short-leg jump veto`；它现在离 `P3` 最近，但还没到 bot2 必须直接越级写成 `P3` 的程度。**
原因：
- `2026-03-28_0729` 已把它从 survivor 正式升到 `P2 admission`
- 当前 strongest evidence 是：在更宽的 `30` 个 liquid alt-perp universe 里，plain XS momentum 的主要失败模式确实是 short-leg single-name jump concentration，而 `jump veto` 的改善明显强于 `short cap` 和 `inverse-vol`
- 这说明对象最接近的出口已经不是 `P1/P0`，而是 `P3`
- 但 admission 五项还没被正式补齐到可以直接 paper launch：当前仍缺更完整的 `cross-asset / time / parameter / honesty` 收口，因此这轮最诚实的动作仍是把它排成 `P2 admission`，不是 bot2 直接强推 `P3`

## 3) rank 合规检查
- `Paper launch queue`: none
- `Fresh intake slot`: `Rank 214`，有 rank
- `Surviving candidate slot`: `Rank 214`，有 rank
- `Active P2 slot`: `Rank 213`，有 rank

结论：
- 当前不存在“前排对象达到 `keep_P1 / P2 / P3` 但无正式 rank”的违规情况
- 本轮无需补下一个未使用整数 `Rank`

## 4) 本轮排班结论
按 policy 默认顺序扫描：
1. `P3 / Paper launch queue`：空，无动作
2. `P2 / Active P2`：有，且必须排第一 —— `Rank 213` admission
3. `P1 / Surviving candidate`：有，且必须排第二 —— `Rank 214` 唯一 survivor follow-up
4. `fresh intake`：前两项诚实排入后，再排新的具体对象

因此本轮 `cycle_plan` 应写成：
1. `Rank 213 / large-cap XS momentum × short-leg jump veto`
   - 做正式 `P2 admission`
   - 重点补 `effectiveness / cross-asset / time / parameter / honesty`
2. `Rank 214 / XS relative-strength full-stack baseline`
   - 做唯一一次 survivor follow-up
   - 重点回答它能否从“可复用 baseline 壳”升级为值得进 `P2` 的主线对象
3. `research/quant_digests/2026-03-28_0608_return-relvol-xs-momentum-alpha.md`
   - 做 fresh intake
4. `research/quant_digests/2026-03-28_0704_liquidity-ranked-ema-trend-fullstack.md`
   - 作为预算内的第二条具体 fresh intake

## 5) 是否需要 bot2 直接兜底推进到 P3？
**这轮不需要。**
bot2 兜底升 `P3` 的条件是：desk review 已经清楚表明对象足够值得进入 paper trade / paper launch，且 bot3 还没升。

对 `Rank 213` 来说：
- 好消息已经足够把它从 `P1` 推进到明确 `P2`
- 但还没有硬到“Admission 可跳过、直接进 paper launch queue”的程度
- 因此这轮不该把它继续拖成开放式研究，也不该过度超前写成 `P3`
- 最诚实的做法就是：把它明确定义为当前唯一 `Active P2`，并把 admission 放到本轮第一优先级

## 6) 对 state 的实际写回
本轮已更新 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan`，重排为：
1. `Rank 213` 的 `P2 admission`
2. `Rank 214` 的唯一 survivor follow-up
3. `0608 return × relative-volume XS momentum` fresh intake
4. `0704 liquidity-ranked EMA trend full-stack` fresh intake

所有新计划项均满足：
- 仅包含 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`

## 7) 一句话结论
这轮别装忙：**queue 空着，真正该做的是先把 `Rank 213` 往 `P3` 方向做 admission 收口，再把 `Rank 214` 的那唯一一次 survivor follow-up 做完；只有这两条前排链条诚实排进来之后，新的 intake 才轮到 `0608` 和 `0704`。**
