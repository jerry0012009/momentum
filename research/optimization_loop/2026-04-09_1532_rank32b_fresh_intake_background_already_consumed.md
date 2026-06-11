# 2026-04-09 15:32 UTC — Rank 32b fresh intake first verdict：background / P0（唯一自然 rescue 早已被既有 Rank 32b 消费）

## Context
- 当前 `Paper launch queue / Active P2 / Surviving candidate` 都为空；按当前 `cycle_plan`，本轮只执行第 3 个 pending 小点：
  - target: `research/park_reframe/2026-03-17_2022_rank32-park-reframe.md`
  - object: `Rank 32b / EMA cross + aligned slope floor only`
- 目标不是重跑旧 admission，而是回答：把 `EMA cross + spread-mid reclaim` 改成 `EMA cross + aligned slope floor only`，今天是否还应被读成一个新的、queue-facing fresh intake pocket。

## What I checked
1. 直接重读原始 park reframe：`research/park_reframe/2026-03-17_2022_rank32-park-reframe.md`
2. 检索该对象在 runtime / park reframe / strategy review / narrow-paper 托管文档中的后续命运，确认这条修改轴是否还是“未消费的新 intake”。

## Key evidence
- 原始 reframe 本身就把唯一主修改轴写得很明确：
  - `remove spread-mid reclaim requirement; keep EMA cross + aligned slope floor only`
  - 并把它命名为：`Rank 32b / Rank 32 slope-floor continuation gate`
- 这条轴后来不只停留在草案：
  - `research/optimization_loop/2026-03-18_0135_rank32b-clean-replication.md`：`Rank 32b` 完成 clean replication，升到 `P1`
  - `research/optimization_loop/2026-03-18_0218_rank32b-paper-candidate.md`：通过 cheap honesty check，升到 `P2`
  - `research/optimization_loop/2026-03-18_0236_rank32b-scope-promotion.md`：通过 promotion honesty，升到 `P3`
- 后续多份 strategy review / park reframe 还反复把这件事写死：
  - `research/park_reframe/2026-03-21_0030_rank32-park-reframe.md`
  - `research/park_reframe/2026-03-29_1035_rank32-park-reframe.md`
  - `research/park_reframe/2026-04-04_0706_rank32-park-reframe.md`
  它们的共同结论都是：**原 `Rank 32` 的唯一自然 rescue 已被既有 `Rank 32b` 消费，不应再诚实派生新的 `Rank 32c`。**
- 也就是说，今天 `cycle_plan` 里把 `Rank 32b` 再当 fresh intake 来问“它是不是独立 pocket”，答案已经不是开放问题；runtime 里已有既成事实：
  - 这条修改轴早已脱离“新 intake 候选”阶段，甚至曾进入 `P3 hosted narrow paper continuity`；
  - 因而它不可能再被诚实地记作一个新的 queue-facing fresh intake。

## Verdict
`Rank 32b` 并不是一个仍待判定的新鲜 `slope-aligned continuation pocket`，而是原 `Rank 32` 唯一自然、最窄的 rescue 轴，且这条轴早已被既有 `Rank 32b` clean replication -> P2 -> P3 的历史链条完全消费；因此本轮 fresh-intake 读法必须直接收口为 **`background / P0`**，而不是重复给它 `keep_P1`。

## Why this changes system truth
- 改变点不在于“发现它不好”，而在于**确认它不再是合法 fresh intake 对象**；
- 这能阻止系统把已经被历史 runtime 消费过的旧派生线，误当成当前 front-slot 的新候选再判一次。

## Runtime writeback required
- `Fresh intake slot.latest_result` 应更新为本轮 `Rank 32b` 的 first verdict
- `Fresh intake slot.latest_result_record` 应指向本文
- `cycle_plan` 第 3 项应标记为 `done`

## Final one-line result
`Rank 32b` 不是新的 fresh intake pocket，而是原 `Rank 32` 唯一自然 rescue 轴且早已被既有 `Rank 32b` 的 clean-replication→P2→P3 链条消费，因此本轮 first verdict 直接收口为 `background / P0`。
