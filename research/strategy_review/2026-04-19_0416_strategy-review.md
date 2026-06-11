# 2026-04-19 04:16 UTC bot2 strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State before rewrite: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git -C /root/clawd/jerry/momentum status --short`
- Recent optimization loop:
  - `2026-04-19_0300_rank423_p2_exit_promote_p3_delay1_core_scope.md`
  - `2026-04-19_0402_rank424_survivor_followup_promote_p2_pair_admission.md`
- Recent strategy review:
  - `2026-04-19_0234_strategy-review.md`
- Recent fresh-intake evidence:
  - `research/quant_digests/2026-04-19_0016_intraday-extreme-return-router-alpha.md`
  - `research/quant_digests/2026-04-19_0224_crossmarket-intraday-tsmom-breadth-basket-alpha.md`

## Repo status snapshot
- 工作区仍有大量历史未跟踪 `tmp/` / artifact / scratch 文件；本轮没有把这些旧文件当成排班依据。
- 最近 runtime evidence 已明确两件事：
  1. `Rank 423` 已完成 P2 出口决策并升入 `P3 / Paper launch queue`，但还没有 dedicated runner / scheduler / first verified run，因此仍是未完成的 launch wiring。
  2. `Rank 424` 已完成 survivor 唯一 follow-up 并升入 `Active P2`，scope 已收窄为 `SOL/LTC core + LINK/AVAX secondary, LINK/LTC watch/exclude`。

## 四个问题
1. `Paper launch queue` 是否非空？
   - **是，非空。**
   - 当前 `Paper launch queue` 有 `current_target = Rank 423 / liquidation shock × OI unwind -> 30m exhaustion fade`，并且 connected runner 列表已有多个历史 live 对象。
   - 关键点：`Rank 423` 虽已进入 P3，但尚未完成 runner / scheduler / first verified run，因此按 policy 仍必须排在 P3 launch wiring 前部。

2. 本轮 `fresh intake` 是什么？
   - **本轮 fresh intake 切换为 `research/quant_digests/2026-04-19_0016_intraday-extreme-return-router-alpha.md`。**
   - 上一条 fresh intake `Rank 424` 已完成 survivor follow-up 并升入 `Active P2`，不应继续占 fresh intake 槽位。
   - 新对象是 `extreme recent return × strongest-only continuation router`，当前证据为 `15m` strongest-only、`|z|>=1.5 + volume_z>0`，约 `+8.43bps gross/trade`，但统一单腿 taker `8bps` 后边际很薄，first verdict 必须围绕 `jump/event veto + 15m->5m child execution` 这个最小 blocker。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
   - **已经值得，并且已经完成。**
   - `Rank 424` 的唯一 survivor follow-up 已由 `research/optimization_loop/2026-04-19_0402_rank424_survivor_followup_promote_p2_pair_admission.md` 消费：`SOL/LTC` 在月度与前后半样本下保住 `12-bar` after-cost 净边，`LINK/AVAX` 保留为 secondary，`LINK/LTC` 降为 watch/exclude。
   - 因此它不再是 survivor；它已正式进入 `Active P2`。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
   - **存在：`Rank 424 / cointegration-first pair admission × strongest residual z-score spread fade`。**
   - 它当前离 **`P3`** 最近，但还没有到 bot2 必须直接兜底升 P3 的程度。
   - 理由：正式 pair admission 已让 `SOL/LTC core` 与 `LINK/AVAX secondary` 成立，不像 P0；也没有明确 re-scope 方向让它回 P1。剩余问题应被压缩成一个 decisive honesty / execution blocker（pair stale-break 或 slippage-realism），下一轮应排成 P2 出口决策，而不是开放式 keep_P2。

## Rank 合规检查
- `Paper launch queue` 当前前排对象 `Rank 423` 已有正式 rank。
- `Active P2` 当前对象 `Rank 424` 已有正式 rank。
- `Surviving candidate slot = none`，无缺 rank 对象。
- 新 fresh intake 还未得到 `keep_P1` 或更高 verdict，因此暂不强制分配 rank。

## P2 -> P3 兜底裁判检查
- `Rank 423` 已经由最近 optimization loop 明确 `promote_P3`；bot2 本轮不再把它排成开放式研究，而是按 policy 直接排成 `P3 handoff / launch wiring`。
- `Rank 424` 虽更接近 P3，但当前还需要一次 P2 出口决策来回答：`SOL/LTC core + LINK/AVAX secondary` 是否在最小 execution realism 下仍成立，以及是否存在单一 decisive blocker。因此本轮不由 bot2 直接升 P3，但 `cycle_plan` 明确要求下一步只能输出 `promote_P3 / drop / one-time re-scope`，不得继续泛化补证据。

## State rewrite
本轮只更新 `docs/BOT2_BOT3_STATE.md`：
1. 将 `Fresh intake slot` 从已升 P2 的 `Rank 424` 切换为 `2026-04-19_0016_intraday-extreme-return-router-alpha.md`。
2. 更新 `Active P2` 描述，强调 `Rank 424` 下一轮应做 P2 出口决策。
3. 重写 `cycle_plan` 为：
   1. `Rank 423` P3 launch wiring：runner + scheduler + first verified run
   2. `Rank 424` P2 admission / exit decision
   3. `2026-04-19_0016_intraday-extreme-return-router-alpha.md` fresh intake first verdict
   4. `2026-04-19_0224_crossmarket-intraday-tsmom-breadth-basket-alpha.md` conditional fresh intake first verdict

## Why this ordering is policy-compliant
- P3 launch wiring 高于 P2 / P1 / fresh intake，因此 `Rank 423` 排第 1。
- 已有 Active P2 的出口决策高于新发现，因此 `Rank 424` 排第 2。
- 当前没有 survivor 槽位对象，才用剩余预算补 fresh intake。
- 没有把 background pool 旧候选拉回前排；也没有把 `Background pool guard` 当成默认 pending 小点。

## Files changed
- `docs/BOT2_BOT3_STATE.md`
- `research/strategy_review/2026-04-19_0416_strategy-review.md`

## Tail steps
1. homepage 刷新（best effort / non-blocking）：
   - `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
2. 中文邮件摘要（独立执行，不与 publish 链式拼接）：
   - `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot2-review] Rank423接线优先 Rank424转出口轮" --body-file /root/clawd/jerry/momentum/research/strategy_review/2026-04-19_0416_strategy-review.md`
