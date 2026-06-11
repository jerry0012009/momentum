# bot2 strategy review — 2026-04-15 21:43 UTC

## 读取与证据
- policy: `docs/BOT2_BOT3_POLICY.md`
- runtime state: `docs/BOT2_BOT3_STATE.md`
- repo status: `git status --short`
- recent optimization loop（最新抽样）:
  - `2026-04-15_2103_rank416_copula_spreadpair_freshintake_keep_p1.md`
  - `2026-04-15_2018_item2_extremefunding_freshintake_background_p0.md`
  - `2026-04-15_1941_rank415_survivor_followup_drop_background.md`
- recent strategy review:
  - `2026-04-15_2023_strategy-review.md`
  - `2026-04-15_1910_strategy-review.md`

## 本轮只回答 4 个问题
1. **`Paper launch queue` 是否非空？**
   - **是，非空**。`connected_runner_live` 中已有多条已接线运行对象（含 Rank 200/201/213/.../405）。

2. **本轮 `fresh intake` 是什么？**
   - `research/quant_digests/2026-04-15_2010_copula-spreadpair-mispricing-alpha.md`（已完成首判并给出 `Rank 416`，结论 `keep_P1`）。

3. **上一条 fresh intake 是否值得那唯一一次 follow-up？**
   - **值得，且已锁定。**
   - `Rank 416` 作为“上一条 fresh intake 且首判为 keep_P1”的对象，按 policy 获得 survivor 唯一一次 follow-up；本轮应优先执行该最小 decisive 检查，不得被新 intake 覆盖。

4. **当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？**
   - **当前不存在明确 `Active P2`**（`current_target=none`）。
   - 最近一次 P2 出口为 `Rank 414`，已在前轮收口为一次性 `P2->P1 re-scope` 并回收至 background；当前无待裁决 P2 出口。

## Rank 合规检查
- `Paper launch queue` / `Surviving candidate` / `Active P2` 前排对象均满足 rank 约束；未发现“前排对象无 rank”。
- 本轮无需补发新整数 rank。

## cycle_plan 重排（按 policy 默认顺序）
已重写 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan`，顺序为：
1. `Rank 416` survivor 唯一 follow-up（前排锁定优先）
2. `2026-04-15_1930_liquidation-stinkbid-hardexpiry-alpha.md` fresh intake
3. `2026-04-15_1436_xsmomentum-topquintile-weeklyrotation-alpha.md` conditional fresh intake
4. `park_reframe Rank 74 soft_reframe_candidate` conditional fresh intake

新生成项均为：`result=none`、`status=pending`。

## P2->P3 兜底裁判结论
- 本轮无 `Active P2`，不触发“bot2 直接把 P2 推进 P3 / handoff”的兜底动作。
- 当前最优先可执行动作是完成 `Rank 416` 的 survivor 唯一 follow-up 并给出 `promote_P2` 或 `background/P0` 的出口结论。

## 结论
- 前排链条存在真实动作（`P1 survivor`），已按高优先级排到本轮首位。
- 在该收口动作完成前，不应让新的 `keep_P1` 候选覆盖 survivor 槽位。