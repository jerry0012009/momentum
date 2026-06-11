# Rank 430 survivor 唯一 follow-up：recent regime / 稀疏度收口 -> background/P0

- 对象：`Rank 430 / downside liquidity sweep rejection -> panic-bounce continuation`
- 执行动作：按 cycle_plan 仅做 1 个 decisive blocker 检查：`15m next-bar + 8bps` 下 recent regime（2026-03~2026-04，实际仅有 2026-04 事件）与单日/单窗口贡献集中度。
- 本轮结论：`background/P0`（不 promote_P2）

## 关键证据（strict long, hold8）
- strict long 事件总数：`n=48`（全部落在 `2026-04`）
- 全样本 `gross≈+75.05bps`，统一 `8bps` 后 `net≈+67.05bps`
- 但收益高度集中在少数日期与窗口：
  - 单日贡献占比：`top1 day ≈ 66.47%`，`top3 day ≈ 99.49%`
  - 去掉 top1 day 后仍为正：`gross≈+32.65bps`（`net8≈+24.65bps`, `n=37`）
  - 去掉 top2 day 后已近成本线：`gross≈+7.14bps`（`net8≈-0.86bps`, `n=32`）
  - 去掉 top3 day 后明显转负：`gross≈+0.59bps`（`net8≈-7.41bps`, `n=31`）
  - 小时窗口集中：`top1 hour ≈ 54.21%`，`top3 hour ≈ 94.12%`

## runtime decision
- `Rank 430` 的 survivor 唯一 follow-up 预算在本轮已消费完。
- 虽然表面费后均值很高，但当前 pocket 对少数日/少数时段过度依赖，未通过“不是单一 execution window 驱动”的 decisive blocker。
- 因此本轮直接收口到 `background/P0`，不升级 `P2`。

## 本轮写回
- `Surviving candidate slot` 清空为 `none`
- `cycle_plan` 第 1 项写回 `done`
- `Background pool` 追加 `Rank 430` 收口记录
