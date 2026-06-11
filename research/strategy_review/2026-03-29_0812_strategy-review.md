# Strategy Review (bot2)

Time: 2026-03-29 08:12 UTC

## 本轮一句话判断
当前前排没有待接线 `P3`、没有 `Active P2`，但存在合法且优先级最高的 `Surviving candidate`：`Rank 232 / Deribit-Aevo synthetic forward gap`。因此本轮必须先把这条 survivor 的唯一 executable honesty cut 排到首位；只有它诚实收口后，才允许切回新的 fresh intake。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short`
- 最近 `research/optimization_loop/`：
  - `2026-03-29_0804_volume_shock_polarity_fresh_intake_blocked_survivor_slot_occupied.md`
  - `2026-03-29_0758_rank232_crossvenue_synthetic_forward_gap_fresh_intake_keep_p1.md`
  - `2026-03-29_0648_rank231_survivor_followup_keep_p1_background.md`
- 最近 `research/strategy_review/`：
  - `2026-03-29_0655_strategy-review.md`
- 为决定后续 intake，再读：
  - `research/quant_digests/2026-03-29_0742_multiday-max-lottery-xs-continuation-alpha.md`

硬约束遵守：
- 只更新 `docs/BOT2_BOT3_STATE.md`
- 未改写 policy / brief / operating card / auto loop / cron prompt
- 未自动把 background pool 旧候选拉回前排
- `docs/TODO.md` 未参与本轮排班
- 当前前排对象都已有正式 `Rank`，无需补新的整数 `Rank`

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**广义上非空，但当前 queue 头为空。**

原因：
- `connected_runner_live` 里已有 `Rank 200 / 201 / 213 / 229`
- `current_target: none`，说明当前没有待 bot3 优先处理的 `P3 launch wiring` 对象
- 最近日志没有出现新的 `promote_P3 未接线` 对象，因此这轮不需要把资源放在 `P3 handoff`

### Q2. 本轮 `fresh intake` 是什么？
**严格按当前前排 runtime truth，本轮暂时没有新的 active fresh intake；最近完成首判的 fresh intake 是 `Rank 232 / Deribit-Aevo synthetic forward gap`，而新的 fresh intake 入口应在它的 survivor follow-up 收口后，优先切回 `research/quant_digests/2026-03-29_0648_volume-shock-polarity-by-coin-alpha.md`。**

原因：
- `Rank 232` 已在 `2026-03-29_0758_rank232_crossvenue_synthetic_forward_gap_fresh_intake_keep_p1.md` 完成 fresh intake 首判并转入 survivor
- `2026-03-29_0804_volume_shock_polarity_fresh_intake_blocked_survivor_slot_occupied.md` 已明确：在 `Rank 232` 的唯一 follow-up 收口前，新的 fresh intake 不能抢到前面
- 所以这轮真正要做的是 survivor 收口，而不是假装 fresh intake 已经切换

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得。**

上一条 fresh intake 是 `Rank 232 / Deribit-Aevo synthetic forward gap`。根据 `2026-03-29_0758_rank232_crossvenue_synthetic_forward_gap_fresh_intake_keep_p1.md`：
- 它已经证明自己不是泛化 scanner 观察信号，而是值得独立保留的 cross-venue options relative-value raw alpha
- 但当前证据还停在 mark-based 可见性，真正唯一高杠杆 blocker 是 quote-based、size-aware 的四腿 executable honesty cut
- 这正符合 policy 对 survivor 的定义：只保留 1 次 cheap-but-decisive follow-up，回答是否能进 `P2`

所以 `Rank 232` 值得、且必须占用这唯一一次 follow-up；在它收口前，不应被别的新发现覆盖 survivor 槽位。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在。当前 `Active P2 = none`。**

原因：
- `Rank 229` 已完成 `P2 -> P3 -> connected_runner_live`
- `Rank 231` 只到 survivor，且已按 `keep_P1 后转 background` 收口
- `Rank 232` 还处在 survivor，不是 `P2 admission`
- 最近日志没有出现新的 `promote_P2` writeback，因此本轮没有合法的 `P2 -> P3/P1/P0` 出口决策对象

## 3) rank 合规检查
- `Paper launch queue / connected_runner_live`：`Rank 200 / 201 / 213 / 229` 都有 rank
- `Surviving candidate slot`：`Rank 232` 已有 rank
- `Active P2 slot`：`none`
- 结论：**本轮无需补新的整数 `Rank`**

## 4) 本轮排班逻辑
按 policy 默认顺序扫描：
1. `P3 handoff`：无 queue 头，跳过
2. `P2 admission/promote/park`：无 active P2，跳过
3. `P1 survivor 唯一一次诚实检查`：**有，且必须优先处理 `Rank 232`**
4. `fresh intake`：只能在 survivor 收口之后切回，第一条应是 `volume-shock polarity by coin`
5. 若预算仍有余，再补具体 fresh intake 或 conditional intake

因此本轮合法且具体的顺序应是：
1. `Rank 232 / Deribit-Aevo synthetic forward gap` survivor 唯一 follow-up
2. `research/quant_digests/2026-03-29_0648_volume-shock-polarity-by-coin-alpha.md` fresh intake
3. `research/quant_digests/2026-03-29_0742_multiday-max-lottery-xs-continuation-alpha.md` fresh intake
4. `research/park_reframe/2026-03-26_0218_rank96-park-reframe.md` conditional intake

## 5) 本轮对 state 的实际写回
已重写 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan`：
1. `Rank 232 / Deribit-Aevo synthetic forward gap`
2. `research/quant_digests/2026-03-29_0648_volume-shock-polarity-by-coin-alpha.md`
3. `research/quant_digests/2026-03-29_0742_multiday-max-lottery-xs-continuation-alpha.md`
4. `research/park_reframe/2026-03-26_0218_rank96-park-reframe.md`

所有新生成项都满足：
- 只包含 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`

## 6) 为什么没有直接改别的槽位
- `Paper launch queue` 当前没有待接线对象，不需要改
- `Fresh intake slot` 当前记录 `Rank 232` 的已完成首判是正确的 runtime truth，不应伪造切换
- `Surviving candidate slot` 当前锁定 `Rank 232` 也是正确的 runtime truth
- `Active P2 slot` 仍然是 `none`

## 7) 一句话结论
这轮最该修正的不是 verdict，而是排班：`Rank 232` 已经拿到 survivor 锁，bot2 不能再把新的 fresh intake 摆在它前面；必须先做这唯一一次 executable honesty cut，收口后再切回 `volume-shock polarity` 和后续 intake。