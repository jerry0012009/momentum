# 2026-04-07 10:58 UTC — crash-trim + vol-managed XS momentum intake blocked by Rank 355 survivor lock

- 当前执行小点：`research/quant_digests/2026-04-07_0333_crashtrim-volmanaged-xs-momentum-alpha.md`
- action: 作为第二条具体 `fresh intake`，判断 `crash-trim + vol-managed cross-sectional momentum` 是否真形成了独立于既有 XS momentum / short-leg veto 家族的新 admission 语义，还是只是对老 momentum 壳的风险裁剪再命名
- success_criterion: 必须给出明确 first verdict：若对象把 `crash-trim / volatility management` 带来的独立 raw alpha 主语或明确可迁移 pocket 压清，则写成 `keep_P1`；若只是旧 `XS momentum × short-leg risk control` 家族的重述，则明确写成 `background / P0`

## 为什么本轮不能执行

1. 当前 runtime 明确写着：
   - `Surviving candidate slot.current_target = Rank 355 / Polymarket adjacent-horizon YES-price spread × Kalman-OU reversion`
   - `followup_budget_remaining = 1`
2. 固定 policy 明确规定：
   - `Surviving candidate` 只能是上一条 fresh intake；
   - 其唯一一次 decisive follow-up 在诚实收口前，默认享有前排锁定权；
   - bot2 不得让另一条新的 `keep_P1` 候选覆盖该 survivor 槽位。
3. 因此，在 `Rank 355` 的 survivor follow-up 尚未执行并收口前，把新的 `fresh intake`（无论是否最终会判成 `background / P0`）排到默认执行轮次里，前置条件都不成立。

## 对当前对象的最小认知

我确实快速复核了 digest 题目与库内历史，确认它讨论的核心仍落在已经被 runtime 主线吸收过的 `XS momentum × short-leg/tail-risk control` 家族附近：
- 已存在 `Rank 213 / large-cap XS momentum × short-leg jump veto`，且已是 `connected_runner_live`；
- 也已有同论文系的 `shortleg momentum crash veto` 补充记录，被明确写成 `background only`，理由就是对象主语已被 `Rank 213` 占用；
- 因而这条 `crash-trim + vol-managed XS momentum` 很可能不是当前系统该优先新开的 front-slot 对象。

但这轮**不需要**把它正式收口成 first verdict，因为更上游的合法性检查已经足够：前排 survivor 尚未收口，新的 intake 不应继续执行。

## 本轮结果

> `crash-trim + vol-managed XS momentum` 这条 fresh-intake 小点本轮前置条件不成立：`Rank 355` 仍合法占用 survivor 槽位且 follow-up 预算未用完，因此该小点必须按 policy 记为 `blocked`，等待 bot2 先把 `Rank 355` 的 survivor follow-up 排到前面并收口。
