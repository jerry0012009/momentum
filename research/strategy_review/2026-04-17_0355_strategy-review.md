# 2026-04-17 03:55 UTC bot2 strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git status --short --branch`（`jerry/momentum` 分支为 `main`；本 repo 本轮无新的已跟踪改动，工作树里主要是历史遗留未跟踪临时文件）
- Recent optimization loop: `2026-04-16_1954_item1_fundingdesign_residual_freshintake_background_p0.md`
- Recent strategy review: `2026-04-16_1711_strategy-review.md`

## 四个问题（本轮结论）
1. `Paper launch queue` 是否非空？
   - 结论：**否**。`current_target = none`；`connected_runner_live` 非空，但这些对象都已完成 runner + scheduler + first verified run，不属于待接线 queue。

2. 本轮 `fresh intake` 是什么？
   - 结论：上一条 fresh intake（`2026-04-16_1615_fundingdesign-residual-premiumfade-alpha.md`）已被 bot3 在 `2026-04-16_1954...` 明确收口 `background/P0`，因此本轮 fresh intake 顺位切换为：
   - `research/quant_digests/2026-04-16_1026_aprranked-fundingcarry-spreadcap-allocation-shell.md`

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
   - 结论：**不值得**。`funding-design residual premium fade alpha` 的 strongest bucket optimistic gross 仅 `+0.94~+1.85bps`，统一 `4/6/8bps` 成本后 overall 与 Asia/EU/US 全部为负；同窗 funding 离散时钟聚簇还意味着 `t+2` delayed confirmation 与换仓摩擦只会更差，first-verdict 直接 `background/P0`，无 survivor 资格。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
   - 结论：**不存在**。`Active P2 = none`；最近一次 P2 口是 `Rank 417`，但它已在 2026-04-16 执行完 `one-time P2->P1 re-scope` 并退出 active 槽位，不构成本轮待判出口。

## Rank 合规检查
- 当前前排对象（`Paper launch queue / Surviving candidate / Active P2`）均不存在“已到 `keep_P1 / P2 / P3` 但无正式 rank”的违规。
- 本轮无需补发新 Rank。

## 排班判断
- 当前没有待接线 `P3`、没有 `Active P2`、也没有 survivor 锁定权对象，因此按 policy 应直接切回 fresh intake。
- 最近连续多条 funding/carry intake 已被统一 `t+2 + 4/6/8bps + Asia/EU/US` 口径收口为 `background/P0`，说明继续在同一 axis 上重复写条件变体的杠杆偏低；因此本轮虽然仍保留 1 条最近 repo fresh intake（APR-ranked carry shell），但剩余预算改优先给 `park_reframe/INDEX.md` 中已明确标注为 `derived_hypothesis_drafted` 的对象，而不是继续排 `soft_reframe_candidate`。

## State rewrite（本轮执行）
- `Fresh intake slot.current_target/source_record` 改写为：
  - `research/quant_digests/2026-04-16_1026_aprranked-fundingcarry-spreadcap-allocation-shell.md`
- `cycle_plan` 按本轮真实可执行对象重写为 4 项：
  1. `2026-04-16_1026_aprranked-fundingcarry-spreadcap-allocation-shell.md`（fresh intake first-verdict）
  2. `2026-04-06_1034_rank60-park-reframe.md`（derived_hypothesis_drafted fresh intake）
  3. `2026-04-06_0606_rank27-park-reframe.md`（conditional derived_hypothesis_drafted fresh intake）
  4. `2026-04-03_0656_rank57-park-reframe.md`（conditional derived_hypothesis_drafted fresh intake）
- 新计划项均满足约束：仅包含 `target / action / success_criterion / result / status`，且新生成项统一 `result = none`、`status = pending`。

## P2->P3 兜底裁判检查
- 本轮无 `Active P2`，也无 desk review 已清楚表明“足够值得 paper trade 但 bot3 未升级”的对象。
- 因此本轮无需把任何对象强制写入 `P3 / Paper launch queue` 或 handoff 路径。
