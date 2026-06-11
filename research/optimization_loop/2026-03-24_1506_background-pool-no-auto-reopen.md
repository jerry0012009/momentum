# Background pool guard（2026-03-24 15:06 UTC）

## Target
- 仅执行当前 `cycle_plan` 的第 3 个 pending 小点：`Background pool`
- 目标：确认旧候选继续只作为 evidence 存档，不因最近 repo 日志或旧 artifact 较多而被自动拉回前排

## What I checked
- `BOT2_BOT3_POLICY.md` 仍明确要求：`Background pool` 不得自动回前排；若 state 与 policy 冲突，bot3 应回退到合法动作。
- `BOT2_BOT3_STATE.md` 当前前排槽位为：
  - `Paper launch queue`：`Rank 154 / Crypto-Stat-Arb`
  - `Fresh intake slot`：open / none
  - `Surviving candidate slot`：none
  - `Active P2 slot`：none
- 当前没有任何旧 `P0/P1` / old rank / compare-anchor / reserve / interrupt 对象被写回 `Surviving candidate`、`Active P2` 或 `Paper launch queue`。
- 因此本轮无需做 reopen、无需补新 Rank、也无需触发新的 admission / compare。

## Verdict
本轮 `Background pool` 维持 evidence-only 约束，未发现需要回退修正的非法前排对象。

## One-sentence result
旧候选继续留在 Background pool；本轮未出现任何带 reopen 授权的新事实，前排仍只保留 `Rank 154` 的 P3 queue implementation，不新增 surviving candidate 或 Active P2。
