# 2026-04-11 08:11 UTC strategy review（bot2）

## 读取范围（按约束顺序）
1. `docs/BOT2_BOT3_POLICY.md`
2. `docs/BOT2_BOT3_STATE.md`
3. repo 状态与最近记录：
   - `git status --short`
   - 最近 optimization_loop：
     - `2026-04-11_0807_cycleplan_item2_blocked_survivor_locked.md`
     - `2026-04-11_0724_rank379_intraday_entropy_ratio_first_verdict_keep_p1.md`
     - `2026-04-11_0704_postcost_combined_funding_spread_first_verdict_background_p0.md`
   - 最近 strategy_review：`2026-04-11_0707_strategy-review.md`

## 本轮只答 4 个问题
1. `Paper launch queue` 是否非空？
- 是，非空；当前 `connected_runner_live` 仍包含 Rank 200/201/213/229/342/368/370/376/378。

2. 本轮 `fresh intake` 是什么？
- 本轮已完成的 fresh intake 是：`research/quant_digests/2026-04-11_0654_intraday-entropy-ratio-xs-reversal-alpha.md`（已首判 `keep_P1` 并分配 `Rank 379`）。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 值得，且已锁定为唯一 survivor：`Rank 379 / intraday entropy-ratio XS reversal`，其唯一 follow-up 应直击 `friction realism`（two-leg 成本后净边际）。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`（`Active P2 slot = none`）。

## rank 合规检查
- 当前前排对象：`Surviving candidate = Rank 379`，`Paper launch queue` 全部已带 rank；未发现无 rank 违规对象。

## 排班重写（按 policy 默认顺序）
前排存在合法动作（Surviving candidate follow-up），因此必须优先收口前排，再切回 fresh intake。已重写 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan` 为 4 项：
1) Rank 379 survivor 唯一 follow-up（friction realism 决策轮）
2) 若 #1 升 P2，则立即做 Rank 379 的 P2 admission 出口轮（直答 P3/P1/P0）
3) 前排收口后执行 fresh intake：`2026-04-11_0431_perp-oi-quadrant-router-alpha.md`
4) 若 #3 完成且仍有预算，执行 conditional fresh intake：`2026-04-11_0248_salience-crosssectional-downside-vs-upside-alpha.md`

所有新项均为：`result = none`，`status = pending`。

## P2->P3 兜底裁判检查
- 本轮未触发：当前无 `Active P2`，不存在“已达 paper trade 门槛但 bot3 未升级”的在槽对象。
- 已在 cycle_plan 第2项写明：若 Rank 379 在第1项升入 P2 且达到门槛，必须直接 `promote_P3`，不得继续开放式研究。
