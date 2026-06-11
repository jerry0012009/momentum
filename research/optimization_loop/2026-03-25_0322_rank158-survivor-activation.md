# 2026-03-25 03:22 UTC · Rank 158 / pump-fade exhaustion reversal survivor activation

- 严格遵循：`docs/BOT2_BOT3_POLICY.md`、`docs/BOT2_BOT3_STATE.md`
- 本轮执行小点：`cycle_plan #4 / Surviving candidate slot`
- 本轮只做：在第 3 项 fresh intake 已明确 `keep_P1` 的前提下，把该对象写成新的唯一合法 survivor，并把唯一一次 follow-up 收口成单一 decisive blocker

## 1. 合法性检查
- 当前 `Fresh intake slot` 已明确为：`Rank 158 / pump-fade exhaustion reversal`
- 当前 `Surviving candidate slot = none`
- 根据 policy，survivor **只能是上一条 fresh intake**；因此本轮允许且应当直接把 `Rank 158` 提升为唯一 survivor
- 当前不存在 `Active P2` 或 `Paper launch queue` 压力，本轮不需要越权做 P2/P3 决策

## 2. 本轮收口后的唯一 follow-up 问题
把 survivor 的唯一一次 follow-up 锁定为单一 decisive blocker：

**冻结已识别的 pump 事件样本后，对 `immediate fade` 与 `wait-for-lower-high + break` 做 `5m/15m`、含 `taker + slippage + spread veto` 的成本后 event-study；若 `confirm-fade` 仍不能稳定留下正的 `net bps / event`，就直接 `drop_to_background`。**

这一步之所以是唯一 blocker，是因为当前对象已经有：
- 事件统计形状；
- 确认式 fade 执行骨架；
- 本地 source probe 支撑其“先冲高、再衰竭、再回落”的结构。

还缺的不是故事，而是**确认延迟 + 成本后**是否仍有正期望。若这点过不了，就没有继续升 `P2` 的必要。

## 3. 对 runtime truth 的改变
- `Surviving candidate slot` 从 `none` 改为 `Rank 158 / pump-fade exhaustion reversal`
- survivor 的唯一 follow-up 预算设为 `1`
- 当前系统对该对象的最新认知更新为：它已不再只是 raw fresh intake，而是一个值得做**一次**成本后确认式 fade 诚实检查的 survivor

## 4. 一句话 result
`Rank 158 / pump-fade exhaustion reversal` 已从 fresh intake 正式写入唯一合法 survivor；它的唯一一次 follow-up 被收口为成本后 `confirm-fade` event-study，若 `5m/15m` 上仍无稳定正的 `net bps / event`，下一步就应直接 `drop_to_background`。
