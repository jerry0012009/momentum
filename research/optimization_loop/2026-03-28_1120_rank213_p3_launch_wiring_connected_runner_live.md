# Rank 213 / large-cap XS momentum × short-leg jump veto — P3 launch wiring connected_runner_live

- 时间：2026-03-28 11:20–11:24 UTC
- 对象：`Rank 213 / large-cap XS momentum × short-leg jump veto`
- 本轮角色：bot3 对当前 `P3 / Paper launch queue` 头部对象执行最小 `launch wiring`；目标是把 queue-side 的 `queued_handoff_ready` 真正落成 `runner + scheduler + first verified run`

## 结论
**正式结果：`Rank 213` 已完成最小 launch wiring，运行态应从 queue-side 的 `queued_handoff_ready` 改写为 `connected_runner_live`。**

这次不是继续研究，而是把已经足够值得进入 paper 的对象接上线：
- dedicated runner 已写出：`scripts/run_rank213_largecap_xs_jump_veto_paper_runner.py`
- scheduler 已安装并启用：
  - `momentum-rank213-paper-refresh.service`
  - `momentum-rank213-paper-refresh.timer`
- 首跑验证已成功：
  - `systemctl start momentum-rank213-paper-refresh.service` 返回 `ExecMainStatus=0`
  - timer 已 `enable --now`，下一次触发时间为 `2026-03-28 11:32:20 UTC`

## 这次接线具体落了什么
### 1) dedicated runner
新建 runner：`scripts/run_rank213_largecap_xs_jump_veto_paper_runner.py`

最小 live 逻辑：
- source of truth：`reports/artifacts/optimization_loop/rank213_p2_admission_20260328/variant_timeseries.csv`
- frozen spec：`f64_h12_floor150_mult2p0`
- 组合口径：`top-3 long / bottom-3 short`，short 侧应用 jump veto
- 成本口径：`4 bps × turnover_x`
- runner mode：`frozen_admission_timeseries_seed`
- 每次刷新会：
  - 读取 admission 已冻结的 variant timeseries seed
  - 重写闭合 trade ledger / current signal frame / state / status / html
  - 保持 paper lane 的接线状态、审计锚点和首页可见性一致

### 2) scheduler
已把 systemd unit 安装到 `/etc/systemd/system/` 并完成：
- `systemctl daemon-reload`
- `systemctl enable --now momentum-rank213-paper-refresh.timer`
- `systemctl start momentum-rank213-paper-refresh.service`

当前 timer 状态：
- `ActiveState=active`
- `SubState=waiting`
- `NextElapseUSecRealtime=Sat 2026-03-28 11:32:20 UTC`

### 3) first verified run artifacts
首跑成功后已写出：
- 状态：`reports/artifacts/paper_rank213_largecap_xs_jump_veto/rank213_status.csv`
- state：`reports/artifacts/paper_rank213_largecap_xs_jump_veto/rank213_state.json`
- ledger：`reports/artifacts/paper_rank213_largecap_xs_jump_veto/rank213_closed_trades.csv`
- current signal：`reports/artifacts/paper_rank213_largecap_xs_jump_veto/rank213_current_signal_frame.csv`
- 页面：`reports/site/paper/rank213_largecap_xs_jump_veto.html`
- run summary：`reports/artifacts/paper_rank213_largecap_xs_jump_veto/rank213_last_run_summary.json`

首跑关键快照：
- `runner_mode`: `frozen_admission_timeseries_seed`
- `variant`: `f64_h12_floor150_mult2p0`
- `closed_trades`: `369`
- `new_closed_trades_appended`: `0`（service 验证跑是 refresh）
- `mean_net_bps`: `22.03`
- `win_rate`: `53.93%`
- `lifetime_total_return`: `+113.47%`
- `latest_signal_ts`: `2026-03-28T02:15:00Z`
- `latest_planned_exit_ts`: `2026-03-28T05:15:00Z`

## 为什么这一步改变了系统认知
在这轮之前，`Rank 213` 只是“下一步应该去接 dedicated runner”的 queue-side 结论；
在这轮之后，它已经是一个**有专用 runner、有启用中的 scheduler、且有首跑 runtime artifact 的 live paper lane**。

这意味着它不该继续挂在模糊的 handoff/queue 口径里，而应直接记为：
> `connected_runner_live`

同时，这次接线也把边界写清楚了：
> 当前 live 的是 **launch plumbing seed**，不是假装已经有 raw-bar 实时重算器。

## 风险 / 边界
- 本轮没有伪造“实时 raw-bar live runner 已存在”；当前 runner 明确读取的是 admission 已冻结的 timeseries seed。
- 若未来要把 Rank 213 从 `frozen_admission_timeseries_seed` 升到 raw-bar live recomputation，那是单独 scope，不能伪装成 routine refresh。
- 当前已不存在新的 launch-facing blocker；下一跳不再是 queue-side handoff，而是后续 continuity 观察与更高层 paper / live governance。

## 本轮改变系统认知的一句话
`Rank 213 / large-cap XS momentum × short-leg jump veto` 已完成最小 `launch wiring`：专用 runner、已启用的 systemd timer 与首跑验证都已落地，运行态应从 queue-side 的 `queued_handoff_ready` 改写为正式 `connected_runner_live`，且当前 runner 边界已明确为 `frozen_admission_timeseries_seed` 的诚实 launch seed。
