# 2026-04-09 03:44 UTC strategy review

## Scope
按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 执行本轮 40 分钟 desk review；本轮只核对 runtime truth、最近 evidence、前排合法性与默认排班顺序，并只更新 `BOT2_BOT3_STATE.md`。

## 先回答 4 个问题

### 1) `Paper launch queue` 是否非空？
**否。**

- `Paper launch queue.current_target = none`
- `Rank 200 / 201 / 213 / 229 / 342` 都已在 `connected_runner_live`
- 当前没有“已进 P3 但 dedicated runner / scheduler / first verified run 尚未接线完成”的对象，因此 queue 为空

### 2) 本轮 `fresh intake` 是什么？
**是 `research/park_reframe/2026-04-03_0656_rank57-park-reframe.md`。**

原因：
- 当前 `Paper launch queue = none`
- 当前 `Active P2 = none`
- 当前 `Surviving candidate = none`
- 最近两条 fresh intake：
  - `2026-04-09_0116_factor-sleeve-momentum-xs-router-alpha.md`
  - `2026-04-09_0041_hyperliquid-xs-funding-carry-persistence-alpha.md`
  已分别在 `research/optimization_loop/2026-04-09_0243_factor_sleeve_momentum_fresh_intake_background.md` 与 `research/optimization_loop/2026-04-09_0341_hyperliquid_funding_carry_fresh_intake_background.md` 中诚实收口为 `background / P0`
- 因此前三层前排（`P3 / P2 / P1`）都为空后，当前应按 policy 切到 `research/park_reframe/INDEX.md` 中仍保留为 `derived_hypothesis_drafted / soft_reframe_candidate` 的具体对象；其中最值得先判的是 `Rank 57`

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
**不值得。**

- 上一条 fresh intake 是 `research/quant_digests/2026-04-09_0041_hyperliquid-xs-funding-carry-persistence-alpha.md`
- `research/optimization_loop/2026-04-09_0341_hyperliquid_funding_carry_fresh_intake_background.md` 已明确：它仍是 generic funding/basis carry family 的延伸叙事，未证明能在现货可借、借币费率、费用/冲击与容量约束下稳定兑现独立净 carry
- blocker 不是“再补一点 evidence”就能解决，而是当前主语本身没有脱离既有 carry family，也没有形成独立 queue-facing pocket
- 因此 first verdict 已诚实收口为 `background / P0`，不值得占用 survivor 那唯一一次 follow-up

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在。**

- `Active P2 slot.current_target = none`
- 最近明确的 P2 出口仍是 `Rank 342`，但它已完成 `P2 -> P3 -> connected_runner_live`
- 当前没有需要 bot2 兜底直升 `P3` 的漏升 `Active P2`

## 最近读取与证据核对
1. `docs/BOT2_BOT3_POLICY.md`
2. `docs/BOT2_BOT3_STATE.md`
3. repo 状态
   - 工作区存在大量历史未跟踪文件；本轮只把它视作 repo hygiene 事实，不据此 reopen background pool，也不据此倒推改 policy
4. 最近 `research/optimization_loop/`
   - `2026-04-09_0341_hyperliquid_funding_carry_fresh_intake_background.md`
   - `2026-04-09_0243_factor_sleeve_momentum_fresh_intake_background.md`
   - `2026-04-09_0201_rank21b_sentiment_extremity_overlay_fresh_intake_background.md`
   - `2026-04-09_0121_rank25c_ema_context_donchian_primary_fresh_intake_background.md`
5. 最近 `research/strategy_review/`
   - `2026-04-09_0207_strategy-review.md`
   - `2026-04-09_0014_strategy-review.md`
6. 当前值得进入本轮预算的具体对象
   - `research/park_reframe/2026-04-03_0656_rank57-park-reframe.md`
   - `research/park_reframe/2026-04-06_1313_rank83-park-reframe.md`
   - `research/park_reframe/2026-04-09_0244_rank71-park-reframe.md`
   - `research/park_reframe/2026-04-08_0019_rank28-park-reframe.md`

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

进一步按 policy 的 fresh-intake 子顺序：
- 最近新 digest 已被诚实收口，因此当前应切到 `park_reframe/INDEX.md` 中仍具备 `derived_hypothesis_drafted / soft_reframe_candidate` 身份的具体对象
- `Rank 57` 是最像 still-live 的单轴：`shared squeeze gate -> breakout-family-local pre-break compression admission`
- `Rank 83` 虽更偏硬，但仍留有 `strong-only Fib binary confirm` 这条具体 residual，可作为第二个明确对象
- `Rank 71` 的 `extreme-only binary gate / veto` 仍只到 soft 候选，但比 `keep_park` 条目更值得占剩余预算
- `Rank 28` 仍在 `soft_reframe_candidate`，且同主题 residual 尚未被本轮前排消费，可作为最后一个 conditional intake

## 为什么本轮不需要 bot2 兜底升 P3
policy 只要求 bot2 在 desk review 已清楚看到某个**在场 `Active P2`** 已达到 paper trade / paper launch 门槛，而 bot3 尚未升级时，直接把对象推进到 `P3 / Paper launch queue` 或 handoff。

本轮不满足该条件：
- `Active P2 = none`
- 当前前排动作全部是 fresh intake / conditional fresh intake
- 最近升级到 `P3` 的对象已经在 `connected_runner_live`

因此，本轮不存在需要 bot2 兜底强推到 `P3` 的对象。

## Runtime writeback
本轮已重写 `docs/BOT2_BOT3_STATE.md`，但只做 runtime 层收口：
- 将 `Fresh intake slot.current_target / source_record` 顺延到 `research/park_reframe/2026-04-03_0656_rank57-park-reframe.md`
- 保留 `Fresh intake slot.latest_result` 为刚完成收口的 `Hyperliquid funding carry persistence -> background / P0`
- 保留 `latest_result_record = research/optimization_loop/2026-04-09_0341_hyperliquid_funding_carry_fresh_intake_background.md`
- 重写 `cycle_plan` 为 4 条具体 pending 动作，顺序为：`Rank 57` -> `Rank 83` -> `Rank 71` -> `Rank 28`
- 不改 policy / brief / operating card / auto loop / cron prompt
- 不 reopen background pool
- 不新增 rank

## 一句话总结
这轮依然没有待接线 `P3`、没有 `Active P2`、也没有 survivor；上一条 fresh intake `Hyperliquid funding carry persistence` 不值 follow-up，而最近两条新 digest 已全部被诚实收口，所以当前前排应切到 `park_reframe` 残余里最具体的 4 条对象：先判 `Rank 57`，再判 `Rank 83`，若仍无前排层级变化，再用剩余预算检查 `Rank 71 / Rank 28`。