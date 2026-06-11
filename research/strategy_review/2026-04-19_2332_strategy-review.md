# 2026-04-19 23:32 UTC strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git -C /root/clawd/jerry/momentum status --short --branch`
- Recent optimization evidence:
  - `research/optimization_loop/2026-04-19_2326_hl_xs_overextension_freshintake_background_p0_cost_universe_basket.md`
  - `research/optimization_loop/2026-04-19_2254_rank427_survivor_followup_promote_p2_exeth_corebounce.md`
  - `research/optimization_loop/2026-04-19_2240_cycleplan_item3_blocked_survivor_frontlock.md`
  - `research/optimization_loop/2026-04-19_2223_cycleplan_item2_blocked_survivor_lock.md`
- Recent strategy review evidence:
  - `research/strategy_review/2026-04-19_2241_strategy-review.md`
  - `research/strategy_review/2026-04-19_2200_strategy-review.md`

## Repo status snapshot
- repo 工作区仍有大量历史未跟踪临时文件；按 policy 仅视为噪声，不把“文件多”误判成当前前排对象。
- 最近真正改变 runtime front slots 的证据只有两条：
  1. `research/optimization_loop/2026-04-19_2254_rank427_survivor_followup_promote_p2_exeth_corebounce.md`：`Rank 427` 已用尽 survivor 唯一 follow-up，并直接升入 `Active P2`；
  2. `research/optimization_loop/2026-04-19_2326_hl_xs_overextension_freshintake_background_p0_cost_universe_basket.md`：`2026-04-19_1906_hl-xs-overextension-fade-alpha.md` 已完成 fresh intake first verdict 并直接收口 `background/P0`。
- `Paper launch queue` 非空，但 `current_target = none`，当前只有 `connected_runner_live` 存量，没有待接线 `P3`。
- 当前存在明确 `Active P2`：`Rank 427 / high-volume selloff -> 5m bounce (ex-ETH core bounce sleeve)`。

## 仅回答 4 个问题
1. `Paper launch queue` 是否非空？
- 是，非空。
- 但当前仅有已接线完成的 `connected_runner_live` 存量，没有未完成 runner / scheduler / first verified run 的 queue 目标。

2. 本轮 `fresh intake` 是什么？
- 当前前排 fresh intake 已前移到：`research/quant_digests/2026-04-19_1815_fibmacd-shallowpullback-continuation-alpha.md`。
- 其后顺位是：
  - `research/quant_digests/2026-04-19_2240_fundingcarry-regimeaware-childexec-alpha.md`
  - `research/quant_digests/2026-04-19_2312_scalp-confluence-timeboxed-bounce-shell.md`

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 不值得。
- 上一条 fresh intake 是 `research/quant_digests/2026-04-19_1906_hl-xs-overextension-fade-alpha.md`。
- 最新 first verdict 已诚实回答唯一 blocker：原 digest 表面 `15m top1-bottom1 hold12 gross≈+12.04bps`，在改成更真实的等权 spread 资本口径后只剩 `gross≈+6.01bps`；统一按双腿 `8bps` 成本后，`all10 / majors6 / core4` 与 `top1 / top2` basket 全部不再保留 after-cost pocket，因此应直接 `background/P0`，不应占用 survivor 唯一 follow-up。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 有：`Rank 427 / high-volume selloff -> 5m bounce (ex-ETH core bounce sleeve)`。
- 结合最新 survivor follow-up 证据，它当前**离 `P3` 最近**，不是因为 admission 已完成，而是因为已保住 recent after-cost pocket，且不是单一币硬撑；下一轮最该回答的不是“还能不能做第二次 P1 检查”，而是它在 `cross-asset / time / 最小 execution realism` 下是否已足够进入 `paper launch queue`。
- 但 desk review 目前还没有看到“已经清楚足够值得 paper trade”的 admission 终局证据，因此本轮**不直接兜底升 `P3`**，而是把第 1 个小点明确排成 `P2` 出口决策轮。

## Rank 完整性检查
- 当前前排对象均带正式 Rank：
  - `Active P2 = Rank 427`
  - `Paper launch queue.connected_runner_live` 内对象均已有 Rank
  - `Fresh intake slot` 当前目标尚未到 `keep_P1`，因此不需要先补 Rank
- 本轮无需补新的 `Rank`。

## State rewrite
已按 policy 重写 `docs/BOT2_BOT3_STATE.md`：
- 保持 `Paper launch queue` 不变（无待接线 `P3`）；
- 保持 `Surviving candidate slot = none`；
- 保持 `Active P2 = Rank 427`；
- 将 `Fresh intake slot.current_target` 前移到 `2026-04-19_1815_fibmacd-shallowpullback-continuation-alpha.md`；
- 重写当前轮 `cycle_plan` 为 4 项，顺序严格遵循：`P2 admission > fresh intake > fresh intake > fresh intake`。

## 当前轮 cycle_plan
1. `Rank 427 / high-volume selloff -> 5m bounce (ex-ETH core bounce sleeve)`
   - `action`: `P2 admission`，直接回答它离 `P3 / P1 / P0` 哪个出口最近；围绕 `cross-asset + time stability` 与 `最小 execution realism` 做出口决策
   - `success_criterion`: 必须输出 `promote_P3`、`one-time P2->P1 re-scope` 或 `drop_to_background` 三选一
2. `2026-04-19_1815_fibmacd-shallowpullback-continuation-alpha.md`
   - `action`: fresh intake first verdict
3. `2026-04-19_2240_fundingcarry-regimeaware-childexec-alpha.md`
   - `action`: fresh intake first verdict
4. `2026-04-19_2312_scalp-confluence-timeboxed-bounce-shell.md`
   - `action`: fresh intake first verdict

## Why this cycle_plan is policy-consistent
- 当前没有待接线 `P3`，但有明确 `Active P2`；因此第 1 项必须先排 `Rank 427` 的 admission / promote / park 决策。
- 当前没有 survivor，因此 fresh intake 只能排在 `P2` 后面。
- 三条 fresh intake 都是具体对象，来自最近尚未消费的新 digest，不是 background reopen。
- 当前尚未达到 bot2 必须兜底直推 `P3` 的门槛，所以第 1 项被诚实写成出口决策轮，而不是伪装成开放式“再补点证据”。

## Review verdict
- `Paper launch queue` 非空，但当前没有待接线 `P3`。
- 本轮 fresh intake 是 `2026-04-19_1815_fibmacd-shallowpullback-continuation-alpha.md`。
- 上一条 fresh intake `2026-04-19_1906_hl-xs-overextension-fade-alpha.md` 不值得 survivor follow-up，已诚实收口 `background/P0`。
- 当前存在明确 `Active P2 = Rank 427`，且它离 `P3` 最近；但证据还没到 bot2 需要直接兜底升 `P3` 的程度，因此当前正确动作是把它排成 `P2` 出口决策轮。