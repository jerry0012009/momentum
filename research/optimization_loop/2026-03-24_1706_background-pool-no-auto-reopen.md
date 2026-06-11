# Background pool 继续归档，无自动 reopen

- 时间：2026-03-24 17:06 UTC
- 轮次：bot3 13 分钟自动执行
- 执行小点：`cycle_plan` 第一个 `pending` 项 —— `Background pool`

## 依据
- policy 明确要求 `Background pool` 里的旧 `P0/P1`、旧 rank、旧 compare/anchor/reserve/interrupt 对象不得自动回到前排。
- state 当前前排仅包含：
  - `Fresh intake slot` = `Rank 156 / Distance-first crypto pairs with trade-buffer governance`
  - `Surviving candidate slot` = 同一对象，且 `followup_budget_remaining: 1`
  - `Active P2 slot` = `none`
  - `Paper launch queue` = `none`（`Rank 154` 已完成 sidecar offload，不再占前排轮次）
  - `Background pool` 最新归档对象 = `Rank 155 / Jamestilfords/statarb-crypto`

## 本轮判断
本轮没有任何旧候选因“最近 repo 日志很多”或“旧 artifact 积累很多”而被自动拉回运行槽位；系统前排仍只保留 `Rank 156` 这一条合规的 fresh/survivor 路径。

## 写回结果
`旧候选继续留在 background；当前前排仅保留 Rank 156 的合法 P1 follow-up，未因旧 repo 日志或旧 artifact 积累触发任何自动 reopen。`
