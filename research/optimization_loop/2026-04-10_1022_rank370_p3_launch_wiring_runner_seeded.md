# Rank 370 — P3 launch wiring 第1步：dedicated runner 落地并可单命令执行

- Time: 2026-04-10 10:22 UTC
- Cycle step: `cycle_plan` #1（本轮唯一执行小点）
- Target: `Rank 370 / same-event strike surface mispricing × fair-value recross / time-stop`

## 本轮执行
按 policy 仅执行 `P3 launch wiring` 第1步：落地 dedicated runner，并验证可单命令执行。

### 新增 runner artifact
- `scripts/run_rank370_surface_mispricing_paper_runner.py`
- 绑定对象：`Rank 370`
- 单命令入口：
  - `python3 /root/clawd/jerry/momentum/scripts/run_rank370_surface_mispricing_paper_runner.py --refresh --seed-only`

### runner 内置的执行语义（与 Rank 370 一致）
1. **fair-value 计算**：
   - 对同事件 strike ladder 的 `mid` 做单调曲面拟合（PAVA），得到 `fair_mid`。
2. **触发规则**：
   - `edge_cents = (fair_mid - market_mid) * 100`；
   - `edge >= +2c` 触发 `buy_yes`，`edge <= -2c` 触发 `sell_yes`。
3. **撤单/退出边界**：
   - stale quote 超过 `max_quote_age_seconds=90` 的信号 veto；
   - 支持 `fair-mid recross` / `max_hold=360min` / 临近结算 flatten 的退出约束（写入 frozen spec）。
4. **下单前风控**：
   - `min_volume_usd>=2000`、`max_positions=1`、最低梯子深度 `>=3`。
5. **runtime artifact 落盘**：
   - `reports/artifacts/paper_rank370_surface_mispricing/rank370_frozen_launch_spec.json`
   - `reports/artifacts/paper_rank370_surface_mispricing/rank370_status.csv`
   - `reports/artifacts/paper_rank370_surface_mispricing/rank370_state.json`
   - `reports/artifacts/paper_rank370_surface_mispricing/rank370_current_signal_frame.csv`
   - `reports/artifacts/paper_rank370_surface_mispricing/rank370_queue_ledger.csv`
   - `reports/artifacts/paper_rank370_surface_mispricing/rank370_last_run_summary.json`
   - `reports/site/paper/rank370_surface_mispricing.html`

## 验证
已执行：

```bash
python3 /root/clawd/jerry/momentum/scripts/run_rank370_surface_mispricing_paper_runner.py --refresh --seed-only
```

返回 `wiring_status = scheduler_ready_runner_seeded`，说明 dedicated runner 已可执行并已写出 Rank370 的 queue-side frozen spec 与运行态骨架 artifact。

## 结论（会改变系统认知）
`Rank 370` 的 dedicated runner 已落地并通过单命令可执行验证；对象从 `queued_for_launch_wiring` 前进到 `scheduler_ready_runner_seeded`，下一步应直接执行 `scheduler + first verified run`。
