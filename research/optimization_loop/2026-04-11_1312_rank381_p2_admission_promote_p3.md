# Rank 381 Active P2 admission 收口：promote_P3（paper launch queue）

- 时间：2026-04-11 13:12 UTC
- 执行器：bot3
- 对象：`Rank 381 / 15m perp price×OI quadrant router`
- 对应 cycle_plan：第 1 项（Active P2 admission 主结论轮）

## 本轮执行范围
仅执行当前最前 pending 小点，不重排 cycle_plan，不扩展第二个 pending 任务。

## admission 最小证据（按 policy 的 5 维）

### 1) effectiveness / expected return（成本后）
基于已完成的 `lag1_exec` 可执行时间戳口径（7 币汇总）：
- hold=2：`+10.64 bps` gross，扣 10 bps 后 `+0.64 bps`
- hold=4：`+14.26 bps` gross，扣 10 bps 后 `+4.26 bps`
- hold=8：`+25.84 bps` gross，扣 10 bps 后 `+15.84 bps`

说明：短持有（2 bars）边际较薄，但 `1h~2h`（4/8 bars）仍保留明确正净边际。

### 2) cross-asset stability
`lag1_exec` 下分币种统计（7 币）：
- hold=2：`6/7` 币种为正
- hold=4：`5/7` 币种为正
- hold=8：`6/7` 币种为正

说明：非单一币驱动，具备可迁移的横截面广度。

### 3) time stability（最小口径）
同一结构在不同持有窗口保持方向一致：
- 15m 主设定在 hold=2/4/8 均为正净边际（10bps 成本口径）
- 收益随持有窗口延长而增强（2 < 4 < 8 bars）

### 4) parameter stability
- 15m 主框架：hold 2/4/8 均存活
- 5m 同类设置普遍为负（成本后），因此参数结论是“存在清晰可执行甜点：15m + 4~8 bars”，而不是任意参数都成立。

### 5) honesty / execution realism（含容量×摩擦）
- honesty：上一轮已完成 `lag1_exec` 对齐，解除 OI 时间戳回填/泄漏 blocker。
- 摩擦敏感性（lag1_exec）：
  - hold=4：12 bps 仍为正（`+2.26 bps`），15 bps 近零偏负（`-0.74 bps`）
  - hold=8：15 bps 仍显著为正（`+10.84 bps`）
- 容量：7 个主流 perp 标的均有样本（合计 `n=143`/hold），不依赖极少数成交机会。

## P2 exit decision（三选一收口）
本轮结论：**`promote_P3`**。

理由：在可执行时间戳口径下，`Rank 381` 已具备可交易边际与跨标的广度；未见单一 decisive fatal flaw。虽然短持有档偏薄、且高摩擦下边际会压缩，但这属于后续 paper wiring 阶段可通过执行参数（优先 4~8 bars、约束摩擦）管理的非致命不完美，不构成继续滞留 P2 的理由。

## 产物
- `/root/clawd/jerry/momentum/reports/artifacts/literature/rank381_p2_admission_friction_sweep_2026-04-11.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/rank381_p2_admission_crossasset_2026-04-11.csv`

## runtime 变更要求
- `Active P2 slot`：释放（`current_target: none`）
- `Paper launch queue`：设为 `current_target: Rank 381 / 15m perp price×OI quadrant router`，状态进入 `queued_handoff_ready`（待下一小点执行 wiring：runner + scheduler + first verified run）

## 尾部执行记录（非阻断）
- homepage publish：`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 本轮未在可接受时限内返回，已终止并记为尾部刷新失败（不回滚本轮 verdict/state/log）。
- 邮件通知：已发送（subject: `[momentum-bot3-auto] Rank381完成P2出口并晋级P3`）。
