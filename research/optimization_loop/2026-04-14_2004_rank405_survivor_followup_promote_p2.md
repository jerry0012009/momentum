# Bot3 执行日志（Rank 405 survivor follow-up）

- 时间：2026-04-14 20:04 UTC
- 执行动作：`cycle_plan` 小点 1（survivor 唯一一次 follow-up）
- 对象：`Rank 405 / multienvelope overshoot average-return shell (15m wall-clock scaled lane)`
- 结论：`promote_P2`（不再停留 P1）

## 本轮最小 decisive 检查

围绕唯一 blocker「同槽位拥挤执行下的容量/滑点鲁棒性」，在既有 15m 事件级明细上补做：

1. **分层成交惩罚**：额外滑点按每笔 `entries` 线性放大（`+2/+4/+6 bps` 梯度）。
2. **同步触发容量约束**：若 BTC/ETH 在同一 `open_ts` 同步触发，额外加 `0.5 × slip` 的拥挤惩罚。
3. 口径：在原 `net_bps`（已含开平费）基础上扣减上述附加惩罚，直接观察费后净边际是否仍为正。

## 结果（关键数）

来自 `reports/artifacts/optimization_loop/rank405_survivor_followup_stress_summary.csv`：

- **`+2 bps` 阶梯**：
  - BTC `+22.27 bps/trade`，ETH `+11.91 bps/trade`，合并 `+14.50 bps/trade`
- **`+4 bps` 阶梯**：
  - BTC `+19.54 bps/trade`，ETH `+9.23 bps/trade`，合并 `+11.81 bps/trade`
- **`+6 bps` 阶梯（最严）**：
  - BTC `+16.80 bps/trade`，ETH `+6.55 bps/trade`，合并 `+9.11 bps/trade`
- 同步触发占比：BTC `39.13%`、ETH `13.04%`、合并 `19.57%`；在已加入拥挤惩罚后仍未把合并均值打到负值。

## 判定

`Rank 405` 在“分层成交 + 同步触发容量约束 + 额外滑点 `+2/+4/+6 bps`”下，费后净边际仍保持正值，survivor 唯一 follow-up 已完成且满足出口条件；本轮将其从 `Surviving candidate` 直接升级为 `Active P2`。

## 产物

- `reports/artifacts/optimization_loop/rank405_survivor_followup_stress_summary.csv`
- `reports/artifacts/optimization_loop/rank405_survivor_followup_stress_slip2bps.csv`
- `reports/artifacts/optimization_loop/rank405_survivor_followup_stress_slip4bps.csv`
- `reports/artifacts/optimization_loop/rank405_survivor_followup_stress_slip6bps.csv`

## 尾部执行备注（非阻断）

- 首页刷新步骤 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 本轮未成功完成（进程后续收到 `SIGKILL`）。
- 按 policy 作为非阻断尾部失败处理，不回滚本轮 verdict / state / artifact。
- 邮件通知步骤已独立执行并成功发送。
