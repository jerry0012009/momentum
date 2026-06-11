# 2026-04-19 22:41 UTC strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git -C /root/clawd/jerry/momentum status --short --branch`
- Recent optimization evidence:
  - `research/optimization_loop/2026-04-19_2240_cycleplan_item3_blocked_survivor_frontlock.md`
  - `research/optimization_loop/2026-04-19_2223_cycleplan_item2_blocked_survivor_lock.md`
  - `research/optimization_loop/2026-04-19_2209_rank427_highvol_selloff_bounce_freshintake_keep_p1.md`
  - `research/optimization_loop/2026-04-19_2032_rank426_survivor_followup_background_p0_30m_1h_honesty.md`
  - `research/optimization_loop/2026-04-19_1951_supertrend_shortflip_freshintake_background_p0_timesymbol_concentration.md`
- Recent strategy review evidence:
  - `research/strategy_review/2026-04-19_2200_strategy-review.md`
  - `research/strategy_review/2026-04-19_2114_strategy-review.md`
- Fresh-intake source notes checked this round:
  - `research/quant_digests/2026-04-19_1906_hl-xs-overextension-fade-alpha.md`
  - `research/quant_digests/2026-04-19_1815_fibmacd-shallowpullback-continuation-alpha.md`
  - `research/quant_digests/2026-04-19_2240_fundingcarry-regimeaware-childexec-alpha.md`

## Repo status snapshot
- repo 工作区仍有大量历史未跟踪临时文件；按 policy 仅视为噪声，不把“文件多”误判成当前前排对象。
- 最近真正改变 runtime 的 front 证据仍是：
  1. `research/optimization_loop/2026-04-19_2209_rank427_highvol_selloff_bounce_freshintake_keep_p1.md`：`Rank 427` 已成为合法 survivor，且唯一 follow-up 预算尚未消耗；
  2. `research/optimization_loop/2026-04-19_2223_cycleplan_item2_blocked_survivor_lock.md` 与 `...2240_cycleplan_item3_blocked_survivor_frontlock.md`：说明前一版 cycle_plan 把新的 fresh intake 误排到 survivor 前，已被 bot3 按 policy 拦下；
  3. `research/optimization_loop/2026-04-19_2032_rank426_survivor_followup_background_p0_30m_1h_honesty.md`：上一条 survivor 已诚实收口到 `background/P0`；
  4. `research/optimization_loop/2026-04-19_1951_supertrend_shortflip_freshintake_background_p0_timesymbol_concentration.md`：上一条前序 fresh intake 已直接收口到 `background/P0`。
- `Paper launch queue` 非空，但 `current_target = none`，且已有对象都在 `connected_runner_live`；当前没有待接线 `P3`。
- `Active P2 = none`；本轮不存在需要 bot2 兜底直推 `P3` 的对象。

## 仅回答 4 个问题
1. `Paper launch queue` 是否非空？
- 是，非空。
- 但当前只有 `connected_runner_live` 存量，没有未完成 runner/scheduler/first-run 的 queue 目标。

2. 本轮 `fresh intake` 是什么？
- 严格按 policy，本轮真正占前排的是 survivor，而不是新的 intake。
- 若问“survivor 收口后的下一条新 intake 候选”，则应按最近未消费的新 digest 顺序切到：
  - 第一候选：`research/quant_digests/2026-04-19_1906_hl-xs-overextension-fade-alpha.md`
  - 第二候选：`research/quant_digests/2026-04-19_1815_fibmacd-shallowpullback-continuation-alpha.md`
  - 第三候选：`research/quant_digests/2026-04-19_2240_fundingcarry-regimeaware-childexec-alpha.md`

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 值得。
- 上一条 fresh intake 就是当前 survivor：`Rank 427 / high-volume selloff -> 5m bounce`。
- 已有 first verdict 说明它不是 top1 router，但在统一 `8bps` 后，`5m hold12` 于全 8 币与 core4/core5 缩池仍保留正的 after-cost pocket；这已经足够支撑那唯一一次 follow-up，用来直接回答它是否能被诚实收敛成 `core bounce / ex-ETH / minimal child-exec` 版本并升入 `P2`。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`。
- 因此本轮没有 bot2 必须直接执行 `P2 -> P3` 兜底升级的对象。

## Rank 完整性检查
- 当前前排对象都已有正式 Rank：
  - `Surviving candidate = Rank 427`
  - `Active P2 = none`
  - `Paper launch queue.connected_runner_live` 内对象均已有 Rank
- 因此本轮无需补新 Rank。

## State rewrite
已重写 `docs/BOT2_BOT3_STATE.md` 的当前轮 `cycle_plan`，修正上一版把 fresh intake 排在 survivor 前的 policy 冲突。

新的排班顺序为：
1. `Rank 427 / high-volume selloff -> 5m bounce` survivor 唯一 follow-up
2. `2026-04-19_1906_hl-xs-overextension-fade-alpha.md` fresh intake
3. `2026-04-19_1815_fibmacd-shallowpullback-continuation-alpha.md` fresh intake
4. `2026-04-19_2240_fundingcarry-regimeaware-childexec-alpha.md` fresh intake

## Why this cycle_plan is policy-consistent
- 当前没有待接线 `P3`，没有 `Active P2`，但**有合法 survivor**；因此第 1 项必须先给 `Rank 427` 的唯一 follow-up。
- 只有 survivor 已被诚实排在前部后，新的 fresh intake 才能顺位进入本轮计划。
- 3 条 fresh intake 都是具体对象，不是空模板，也不是 background reopen。
- 当前 desk review 没看到任何“已足够 paper trade 但 bot3 尚未升级”的 `Active P2`，因此没有 bot2 直接改写 `P3` 的兜底场景。

## Review verdict
- `Paper launch queue` 非空，但当前没有待接线 `P3`。
- 本轮前排主动作不是新 intake，而是 `Rank 427` 的 survivor 唯一 follow-up。
- `Rank 427` 值得那唯一一次 follow-up；其收口结果应直接回答 `P2` 或 `background/P0`，不能继续拖成开放式 P1。
- 当前没有 `Active P2`，因此也没有需要 bot2 直接兜底推进到 `P3 / Paper launch queue` 的对象。
