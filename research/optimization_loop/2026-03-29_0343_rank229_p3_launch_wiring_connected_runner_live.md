# Rank 229 / ETH-led abnormal-day continuation (session-defined) — P3 launch wiring connected_runner_live

- 时间：2026-03-29 03:30–03:43 UTC
- 对象：`Rank 229 / ETH-led abnormal-day continuation (session-defined)`
- 本轮角色：bot3 只执行当前 `cycle_plan` 第 2 个 pending 小点，把 queue-side 的 `scheduler_ready_runner_seeded` 真正推进成 `scheduler + first verified run + runtime truth`

## 结论
**正式结果：`Rank 229` 已完成最小 launch wiring，运行态应从 `scheduler_ready_runner_seeded` 改写为 `connected_runner_live`。**

这轮不再回到开放式研究，而是把已经通过 P2 admission 且已 seed runner 的对象接上线：
- dedicated runner 继续沿用：`scripts/run_rank229_eth_abnormal_day_paper_runner.py`
- scheduler 已安装并启用：
  - `momentum-rank229-paper-refresh.service`
  - `momentum-rank229-paper-refresh.timer`
- 首跑验证已成功：
  - `systemctl start momentum-rank229-paper-refresh.service` 返回 `ExecMainStatus=0`
  - timer 已 `enable --now`，下一次触发时间为 `2026-03-29 03:47:20 UTC`

## 这次接线具体落了什么
### 1) scheduler
本轮新增 repo 内 unit 文件：
- `ops/systemd/momentum-rank229-paper-refresh.service`
- `ops/systemd/momentum-rank229-paper-refresh.timer`

并已安装到 `/etc/systemd/system/` 后执行：
- `systemctl daemon-reload`
- `systemctl enable --now momentum-rank229-paper-refresh.timer`
- `systemctl start momentum-rank229-paper-refresh.service`

当前 timer 状态：
- `ActiveState=active`
- `SubState=waiting`
- `NextElapseUSecRealtime=Sun 2026-03-29 03:47:20 UTC`

### 2) first verified run
首跑 service 成功执行后，`Rank 229` 的 paper artifacts 已刷新：
- 状态：`reports/artifacts/paper_rank229_eth_abnormal_day/rank229_status.csv`
- state：`reports/artifacts/paper_rank229_eth_abnormal_day/rank229_state.json`
- ledger：`reports/artifacts/paper_rank229_eth_abnormal_day/rank229_closed_trades.csv`
- current signal：`reports/artifacts/paper_rank229_eth_abnormal_day/rank229_current_signal_frame.csv`
- 页面：`reports/site/paper/rank229_eth_abnormal_day.html`
- run summary：`reports/artifacts/paper_rank229_eth_abnormal_day/rank229_last_run_summary.json`

首跑后关键快照：
- `mode`: `refresh`
- `runner_mode`: `frozen_admission_trade_seed`
- `closed_trades_total`: `90`
- `new_closed_trades_appended`: `0`
- `mean_net_bps`: `86.6889`
- `win_rate`: `66.67%`
- `lifetime_total_return`: `+105.80%`
- `last_run_at_utc`: `2026-03-29T03:42:56Z`
- `wiring_status`: `connected_runner_live`

### 3) runtime artifact 口径收口
为了避免 timer 后续刷新又把运行态写回旧的 `scheduler_ready_runner_seeded`，本轮同步把 runner 写回口径收口为：
- `stage = connected_runner_live`
- `wiring_status = connected_runner_live`

这样后续定时刷新会延续真实运行态，而不是退回接线前语义。

## 为什么这一步改变了系统认知
在这轮之前，`Rank 229` 只是已经 seed 完 runner、但还没完成 scheduler + first verified run 的 queue 头部对象；
在这轮之后，它已经是一个**有专用 runner、有启用中的 scheduler、且有首跑 runtime artifact 的 live paper lane**。

这意味着：
> `Rank 229` 不应再继续占据 `Paper launch queue.current_target` 的“等待接线”位置，而应直接并入 `connected_runner_live`。

同时也要诚实保留边界：
> 当前 live 的是 **frozen admission trade seed** 接线态，不是假装已经有 raw-bar 实时重算器；raw-bar recomputation 仍是未来可单独立项的 scope。

## 本轮改变系统认知的一句话
`Rank 229 / ETH-led abnormal-day continuation (session-defined)` 已完成最小 `launch wiring`：专用 runner、已启用的 systemd timer 与首跑验证都已落地，运行态应从 `scheduler_ready_runner_seeded` 改写为正式 `connected_runner_live`，不再只是 paper queue 里的待接线对象。
