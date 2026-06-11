# 2026-04-06 06:32 UTC — bot2 strategy review

本轮严格按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 做 desk review，只回答 policy 指定的 4 个问题，并据此重写 runtime state 的 `cycle_plan`。

## 先回答 4 个问题

1. **`Paper launch queue` 是否非空？**
   - 否。当前 `Paper launch queue.current_target = none`。
   - `Rank 342` 已在 `2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md` 中完成最小接线，已写回 `connected_runner_live`，不再占据 queue 待接线位置。

2. **本轮 `fresh intake` 是什么？**
   - 本轮前排必须先让位给 survivor，因此新的 `fresh intake` 头对象改为：
   - `research/quant_digests/2026-04-06_0424_funding-basis-persistence-deltaneutral-alpha.md`

3. **上一条 fresh intake 是否值得那唯一一次 follow-up？**
   - 是。
   - 上一条 fresh intake 是 `Rank 348 / basis relaxation × regime-sized funding carry`。
   - `2026-04-06_0552_rank348_basis_relaxation_regimesized_funding_carry_first_verdict_keep_p1.md` 已明确：它不是旧 funding carry 的简单换皮，而是把 `basis relaxation -> carry timing -> regime-sized governance` 压成了独立可检验骨架；因此按 policy，它值得占用那唯一一次 survivor follow-up，而且在诚实收口前享有前排锁定权。

4. **当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？**
   - 当前不存在明确 `Active P2`。
   - `Rank 342` 的 `P2 -> P3` 出口已经在上一轮收口并完成接线；本轮不存在需要 bot2 兜底裁决升级到 `P3` 的遗漏对象。

## Rank / 前排合法性检查

- 当前前排对象：
  - `Surviving candidate = Rank 348`
  - `Active P2 = none`
  - `Paper launch queue.current_target = none`
- 未发现前排对象无 rank，因此本轮 **不需要补 rank**。

## 本轮排班判断

按 policy 默认顺序扫描：
1. **P3 handoff**：无 pending queue 头对象；`Rank 342` 已连到 `connected_runner_live`，不再重复占位。
2. **P2 admission / promote / park**：`Active P2 = none`。
3. **P1 survivor 唯一一次诚实检查**：这是本轮唯一必须优先的真实动作，因此排在第 1 项。
4. **fresh intake**：只有在 survivor 已诚实排进当前轮前部后，才用剩余预算补具体新 intake；因此依次补入：
   - `2026-04-06_0424_funding-basis-persistence-deltaneutral-alpha.md`
   - `2026-04-06_0558_btc-lead-liquidity-lag-alt-alpha.md`
   - `2026-04-06_0619_positive-jump-variance-antilottery-xs-alpha.md`

## 对 state 的具体改写

本轮只更新了 `docs/BOT2_BOT3_STATE.md`：

- `Fresh intake slot.current_target`
  - 从 `2026-04-06_0458_basis-relaxation-regimesized-funding-carry-alpha.md`
  - 改为 `2026-04-06_0424_funding-basis-persistence-deltaneutral-alpha.md`

- 重写 `cycle_plan` 为 4 项 pending：
  1. `Rank 348` survivor follow-up（唯一一次决定性检查）
  2. `2026-04-06_0424_funding-basis-persistence-deltaneutral-alpha.md` fresh intake
  3. `2026-04-06_0558_btc-lead-liquidity-lag-alt-alpha.md` fresh intake
  4. `2026-04-06_0619_positive-jump-variance-antilottery-xs-alpha.md` conditional fresh intake

## 为什么这次没有 P3 / P2 强推

policy 要求 bot2 在 desk review 中，如果看到 `Active P2` 已足够值得进入 paper trade，而 bot3 尚未升级，必须直接改写为 `P3 / handoff`。

本轮没有这种遗漏：
- 唯一最近完成 `P2 exit` 的对象是 `Rank 342`；
- 它已经在上一轮被提升到 `P3`，随后完成 runner + scheduler + 首跑验证，并写回 `connected_runner_live`；
- 因此本轮不需要再做兜底升级动作。

## 本轮一句话结论

本轮没有遗留的 `P3` 或 `Active P2` 出口决策；前排唯一必须优先的是真正值得那一次 follow-up 的 `Rank 348`，所以新的 `cycle_plan` 先收口 survivor，再按顺序补入三个具体 fresh intake。