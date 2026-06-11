# 2026-04-17 18:10 UTC — Rank 89 fresh intake first verdict -> background/P0

## Target
- `Rank 89 / outside-close -> back-inside-close anchored failure-followthrough setup`
- source: `research/park_reframe/2026-04-10_0611_rank89-park-reframe.md`

## Why this was the front pending item
`cycle_plan` item1 要求把旧 shared allow-gate 压成最小 event spec，只回答它改写成 `back-inside bar anchored failure-followthrough setup` 后，是否足以成为独立、值得保留的 queue-facing failure 事件；并补 1 个最小 honesty / execution realism blocker。

## Evidence used this round
1. `research/park_reframe/2026-04-10_0611_rank89-park-reframe.md`
2. `research/optimization_loop/2026-03-19_1219_rank89-outside-inside-intake.md`
3. `research/optimization_loop/2026-03-19_1252_rank89-clean-replication-park.md`
4. `research/quant_digests/2026-03-19_1059_breakout-reentry-inside-sequence-failure-verdict.md`
5. `research/quant_digests/2026-03-22_2028_dc-first-hit-followup-verdict-gate.md`

## Minimal first-verdict answer
结论：**直接 `background/P0`，不保留为新的 `keep_P1`。**

### Why not keep_P1
原始 clean replication 已经给出最关键的硬约束：
- `outside_inside_binary` 的改善主要靠把样本压到约 `trade_count_retention ≈ 4.45%`；
- 最强改善集中在极薄的 `breakout_short / fib_retest_long` 子样本；
- `seqext_size` 没有进一步提供诚实增量；
- 原 shared allow-gate 壳已经被证伪。

本轮把它收缩成 `back-inside bar anchored failure-followthrough` 后，确实得到一个更像样的事件语义：
- 先出现 `outside close`；
- 再出现 `back-inside close`；
- 然后只讨论这一下后的短窗 follow-through / fade。

但这一步**没有改写两个决定性问题**：
1. **distinctness 仍不足**
   - 该 reframe 仍然本质上属于既有 `failure verdict / first-hit follow-up` family；
   - 从当前证据看，它更像 `Rank 31b / Rank 104` 一类 failure-family 的宿主变体，而不是能独立命名的新 residual；
   - 目前没有新的 reader-facing 证据证明 `outside -> back-inside` 这一锚点能稳定拉开到值得单列的 queue-facing alpha lane。
2. **厚度问题没有被结构性修复**
   - 把 shared gate 改成单事件宿主，不会自动把原先 `~4.45%` retention 级别的稀薄事件变成可保留前排对象；
   - 现有证据仍更像“局部 verdict clue”，不是可保留的新 lane。

## Minimal honesty / execution realism check
本轮只做 cycle_plan 允许的 1 个最小 honesty 检查：

### Checked question
`back-inside` failure 事件及其后短窗 follow-through，是否在决策时点真实可见，还是依赖 bar-complete hindsight / future-window 回填？

### Answer
- **事件锚本身可以诚实定义。**
  - 只有当 `back-inside close` 这根 bar 完整收盘后，才能确认 failure event 成立；
  - 若以后真要交易，最早也只能从其后 `next-bar open` 起做，不该把当根内部 path 倒灌回 signal。
- **但这只能说明“可诚实实现”，不能说明“值得单列保留”。**
  - 也就是说，honesty 这条轴并不是当前唯一 blocker；
  - 真正阻止它进入 `keep_P1` 的仍是 `distinctness + thickness`：它虽然可以做成 honest event，但仍高度重叠于既有 failure family，且没有新增足够厚的独立 residual。

## Runtime-changing conclusion
**Rank 89：即使压成 `back-inside anchored failure-followthrough`，当前也仍只是 failure-family 内的稀薄事件锚，distinctness 与厚度都不足以保留为新的 survivor 候选，因此本轮 fresh intake 直接收口 `background/P0`。**

## State write-back required
- `Fresh intake slot` 本轮对象已诚实收口为 `background/P0`。
- `cycle_plan` item1 应记为 `done`。
- 不触发 survivor；item4 的条件前提不成立。

## Tail-step note
若首页刷新或邮件发送失败，只记为尾部失败，不回滚本轮结论。