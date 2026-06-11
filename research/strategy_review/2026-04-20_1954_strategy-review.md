# 2026-04-20 19:54 UTC strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git -C /root/clawd/jerry/momentum status --short`
- Recent optimization evidence:
  - `research/optimization_loop/2026-04-20_1841_rank430_liquidity_sweep_rejection_bounce_freshintake_keep_p1.md`
  - `research/optimization_loop/2026-04-20_1950_cycle_item2_blocked_survivor_already_locked.md`
- Recent strategy review evidence:
  - `research/strategy_review/2026-04-20_1834_strategy-review.md`

## 仅回答 4 个问题
1. `Paper launch queue` 是否非空？
- 是，非空（`connected_runner_live` 有多条已接线对象）；但当前 `current_target = none`，无待接线 P3。

2. 本轮 `fresh intake` 是什么？
- 本轮前排主动作不是新 intake，而是 `Rank 430` 的 survivor 唯一 follow-up。
- 在 survivor 收口后，fresh intake 依次是：
  - `research/quant_digests/2026-04-20_1216_kalman-dynhedge-pair-spreadfade-alpha.md`
  - `research/quant_digests/2026-04-20_1129_dual-momentum-breakout-expansion-alpha.md`
  - `research/quant_digests/2026-04-20_0455_betacorr-gated-betaweighted-futures-pairs-shell.md`

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 值得。上一条 fresh intake 已在 `2026-04-20_1841...` 首判为 `keep_P1` 并分配 `Rank 430`，当前按 policy 占用 survivor 槽位且 `followup_budget_remaining=1`。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 不存在。`Active P2 = none`。

## Rank 完整性检查
- 前排对象检查：
  - `Surviving candidate = Rank 430`（有正式 rank）
  - `Active P2 = none`
  - `Paper launch queue.current_target = none`
- 本轮无需补新 Rank。

## State rewrite（按默认排班顺序）
已重写 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan`，并按优先级落实为：
1. `P1 survivor`：`Rank 430` 唯一 follow-up（出口只允许 `promote_P2` 或 `background/P0`）
2. `fresh intake`：Kalman dyn-hedge pairs
3. `fresh intake`：dual-momentum breakout expansion
4. `fresh intake`：beta-corr gated beta-weighted pairs shell

所有新项均满足：`result = none`、`status = pending`。

## P2->P3 兜底判断
- 当前无 `Active P2`，不存在“已够格但 bot3 未升级”的遗漏对象。
- 本轮无需触发 bot2 强制直推 `P3 / Paper launch queue`。

## Tail step status
- homepage publish（独立命令）待执行
- email notify（独立命令）待执行
