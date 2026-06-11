# Rank 238 / UTC schedule × macro timestamp shared gate — first verdict keep_P1

- Time: 2026-03-29 13:58 UTC
- Target: `UTC 时钟 × 宏观时间戳 shared gate`
- Source: `research/quant_digests/2026-03-29_1022_utc-schedule-macro-timestamp-gate.md`
- Verdict: `keep_P1`
- Rank assigned: `238`

## What was decided
这条对象足够边界清楚，可以正式收窄为：

`Rank 238 / UTC schedule_score shared gate × continuation admission / reversal veto`

它不是独立 raw alpha，不直接提供 entry/exit/sizing；但它满足进入前排的最小条件，因为：

1. **主语清楚**：对象不是泛泛“crypto 有时钟效应”，而是一个可写进 bar-level backtest 的 `schedule_score` shared gate。
2. **服务至少两类 alpha**：
   - continuation / breakout / post-shock continuation 的 admission
   - reversal / fade 的 veto
3. **最小实验清楚**：digest 已给出 desk-usable 的最小 `schedule_score` 框架：minute-of-hour、hour-of-day、weekday、macro event window；也给出了 baseline / gated / inverse 的 AB test 口径。
4. **诚实边界清楚**：它不能伪装成完整策略，也不能把 macro gate 与无条件时钟 gate 混写成单一规则；但这正说明它应作为 shared filter 被验证，而不是留在宽泛摘要层。

## Why not background only
尽管这条线没有独立 alpha，但它比“普通论文摘要”更具体，因为它已经回答了一个当前 desk 反复会遇到的共享问题：

- continuation 什么时候更像真的、该放行？
- reversal 什么时候更可能被最强 activity 碾掉、该 veto？

现有 digest 里已经有不少 raw alpha；这条线补的是共享 timing map，而不是重复再造一个 headline alpha。它因此符合 `shared gate / filter` 类型 fresh intake 的准入标准。

## Why not P2 yet
当前证据仍主要是论文 + quick check，尚未完成最关键的 desk 验证：

- 同一套 `schedule_score` 是否真的能在至少一条 continuation alpha 和一条 reversal alpha 上同时产生 post-cost 分层；
- `macro gate` 与 `无条件 UTC 时钟 gate` 是否需要分层处理，且不会因条件混写造成伪效果。

所以本轮诚实停在 `keep_P1`，不直接升 `P2`。

## Result sentence
`UTC 时钟 × 宏观时间戳` 不该只留在“crypto 也有日历效应”的摘要层；它已足够收窄成 `Rank 238 / UTC schedule_score shared gate × continuation admission / reversal veto`，因此 first verdict 记为 `keep_P1`。
