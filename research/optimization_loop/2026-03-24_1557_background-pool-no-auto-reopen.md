# 2026-03-24 15:57 UTC — Background pool no-auto-reopen guard

## 执行动作
- 读取 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md`
- 检查当前前排运行槽位与 `cycle_plan`
- 验证本轮剩余 pending 小点是否会把 background pool 旧候选重新拉回前排

## 观察
- 当前 `Paper launch queue` 仍为 `Rank 154 / Crypto-Stat-Arb`，且 handoff packet 已固化。
- 当前 `Fresh intake slot` 已完成 `yeshunyi/crypto-momentum-strategy` 的 fresh intake，并已 direct park。
- 当前 `Surviving candidate slot` 为 `none`，`Active P2 slot` 也为 `none`。
- 当前唯一 pending 小点是对 `Background pool` 的 guard：确认旧候选继续只保留 evidence，不因旧 repo / artifact / 日志密集而自动 reopen。
- 经核对，当前 state 中不存在任何需要 bot3 合法执行的 auto-reopen 动作，也不存在可合法提升为前排槽位的 background 对象。

## 结论
- 旧候选继续留在 background pool，不发生自动 reopen；当前运行态前排仍保持 `Rank 154` 的 P3 handoff 队列 + open fresh intake，无新增 survivor / active P2。

## 对 runtime truth 的影响
- 仅将本轮 `cycle_plan` 第 3 项收口为 guard 完成。
- 未改写 policy / brief / operating card / cron prompt。
- 未新增运行槽位，未重排 `cycle_plan`，未把任何 background 对象拉回前排。
