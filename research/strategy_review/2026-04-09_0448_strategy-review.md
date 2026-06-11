# 2026-04-09 04:48 UTC strategy review

## Scope
按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 执行本轮 40 分钟 desk review；本轮只核对 runtime truth、最近 evidence、前排合法性与默认排班顺序，并只更新 `BOT2_BOT3_STATE.md`。

## 先回答 4 个问题

### 1) `Paper launch queue` 是否非空？
**否。**

- `Paper launch queue.current_target = none`
- `Rank 200 / 201 / 213 / 229 / 342` 都已在 `connected_runner_live`
- 当前没有“已进 P3 但 dedicated runner / scheduler / first verified run 尚未接线完成”的对象，因此 queue 为空

### 2) 本轮 `fresh intake` 是什么？
**是 `research/park_reframe/2026-03-25_0457_rank101-park-reframe.md`。**

原因：
- 当前 `Paper launch queue = none`
- 当前 `Active P2 = none`
- 当前 `Surviving candidate = none`
- 刚刚前排里的 `Rank 14 / 31 / 18 / 13` 都已经被更晚 evidence 明确收口为 stale duplicate pending，不能再继续当 fresh intake 做 first verdict
- 最近新 digest（`factor sleeve momentum`、`Hyperliquid funding carry`）也已在更早 optimization loop 中诚实收口为 `background / P0`
- 因此前三层前排都为空后，本轮需要切到 **尚未被正式做成 fresh-intake first verdict** 的具体 `park_reframe` 候选；当前最靠前、且仍保留为 `soft_reframe_candidate` 的对象是 `Rank 101`

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
**不值得。**

- 上一条真正完成 first verdict 的 fresh intake 是 `research/park_reframe/2026-04-09_0244_rank71-park-reframe.md`
- `research/optimization_loop/2026-04-09_0400_rank71_fresh_intake_first_verdict_background.md` 已明确：它仍只是把旧 `EMA/VWAP/ATR/volume` graded admission score 收窄成更硬阈值的 retention 叙事
- blocker 不是“再补一点 evidence”，而是主语本身没有脱离既有 trend-shell / tradeability overlay family
- 因此 first verdict 已诚实收口为 `background / P0`，不值得占用 survivor 的唯一一次 follow-up

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在。**

- `Active P2 slot.current_target = none`
- 最近明确的 P2 出口仍是 `Rank 342`，但它已完成 `P2 -> P3 -> connected_runner_live`
- 当前没有需要 bot2 兜底直升 `P3` 的漏升 `Active P2`

## 最近读取与证据核对
1. `docs/BOT2_BOT3_POLICY.md`
2. `docs/BOT2_BOT3_STATE.md`
3. repo 状态
   - 工作区存在大量已修改文件；本轮只把它当作 repo hygiene 事实，不据此 reopen background pool，也不据此倒推改 policy
4. 最近 `research/optimization_loop/`
   - `2026-04-09_0444_cycle_plan_missing_pending_blocked.md`
   - `2026-04-09_0439_bot3_blocked_no_pending_cycle_plan.md`
   - `2026-04-09_0437_rank13_stale_pending_duplicate_blocked.md`
   - `2026-04-09_0429_rank18_stale_pending_duplicate_blocked.md`
   - `2026-04-09_0424_rank31_stale_pending_duplicate_blocked.md`
   - `2026-04-09_0419_rank14_stale_pending_duplicate_blocked.md`
5. 最近 `research/strategy_review/`
   - `2026-04-09_0413_strategy-review.md`
   - `2026-04-09_0344_strategy-review.md`
   - `2026-04-09_0207_strategy-review.md`
6. 当前值得进入本轮预算的具体对象
   - `research/park_reframe/2026-03-25_0457_rank101-park-reframe.md`
   - `research/park_reframe/2026-03-24_1430_rank4-park-reframe.md`
   - `research/park_reframe/2026-03-23_1941_rank5-park-reframe.md`
   - `research/park_reframe/2026-03-23_0914_rank7-park-reframe.md`

## Rank / 前排合法性检查
- `Paper launch queue.current_target = none`，合法
- `Surviving candidate slot.current_target = none`，合法
- `Active P2 slot.current_target = none`，合法
- 当前前排不存在达到 `keep_P1 / P2 / P3` 但无正式 rank 的对象，因此本轮无需补 rank
- 当前也不存在 desk review 已清楚表明“应直升 P3”但尚未升级的 `Active P2`

## 排班判断
按 policy 默认顺序：
`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0`

本轮扫描结果：
- `P3`：无待接线对象
- `P2`：无在场 `Active P2`
- `P1`：无在场 survivor
- 因此前三层都没有真实可执行动作，本轮应继续停留在具体 `fresh intake`

进一步按当前合法对象顺序：
- 原 `Rank 14 / 31 / 18 / 13` 这组 cycle item 已全部被更晚 runtime truth 逐条否掉，继续排它们只会重复 stale duplicate
- 最近新 digest 已在更早轮次全部判完，不能再拿来冒充新前排
- 因此本轮应切到 **尚未被正式做成 first verdict** 的 `park_reframe` 候选
- 当前最合适的一组是：`Rank 101` -> `Rank 4` -> `Rank 5` -> `Rank 7`
  - `Rank 101`：先回答“缩量回踩残余是否真是独立 hold-quality pocket，还是只是 retention 美化”
  - `Rank 4`：再回答“pairs spread z-score 降级成 shared risk overlay 后，是否能脱离 generic pairs sizing family”
  - `Rank 5`：若前两项都收口，再看 session-tail 主题是否只剩一个可独立的 first-30m impulse-quality gate
  - `Rank 7`：最后再看 adaptive trend combo 是否只剩 band-pass continuous alignment overlay 这条仍可能单列的轴

## 为什么本轮不需要 bot2 兜底升 P3
policy 只要求 bot2 在 desk review 已清楚看到某个**在场 `Active P2`** 已达到 paper trade / paper launch 门槛，而 bot3 尚未升级时，直接把对象推进到 `P3 / Paper launch queue` 或 handoff。

本轮不满足该条件：
- `Active P2 = none`
- 当前前排动作全部是 fresh intake / conditional fresh intake
- 最近升级到 `P3` 的对象已经在 `connected_runner_live`

因此，本轮不存在需要 bot2 兜底强推到 `P3` 的对象。

## Runtime writeback
本轮已重写 `docs/BOT2_BOT3_STATE.md`，且只做 runtime 层收口：
- 将 `Fresh intake slot` 从 `blocked / Rank 14 stale` 改回 `pending`
- 将 `Fresh intake slot.current_target / source_record` 顺延到 `research/park_reframe/2026-03-25_0457_rank101-park-reframe.md`
- 将 `latest_result` 改写为：上一组 `Rank 14 / 31 / 18 / 13` pending 已全部被更晚 runtime truth 收口为 stale duplicate，本轮正式切到新的合法 fresh intake
- 重写 `cycle_plan` 为 4 条具体 pending 动作，顺序为：`Rank 101` -> `Rank 4` -> `Rank 5` -> `Rank 7`
- 所有新项均按要求写成 `target / action / success_criterion / result / status`，且 `result = none`、`status = pending`
- 不改 policy / brief / operating card / auto loop / cron prompt
- 不 reopen background pool
- 不新增 rank

## 一句话总结
这轮依然没有待接线 `P3`、没有 `Active P2`、也没有 survivor；旧前排 `Rank 14 / 31 / 18 / 13` 已被逐条打成 stale duplicate，不再是合法 pending，所以当前前排应切到新的、尚未正式做过 first verdict 的 `park_reframe` 候选：先判 `Rank 101`，再判 `Rank 4`，若仍无层级变化，再用剩余预算检查 `Rank 5 / Rank 7`。
