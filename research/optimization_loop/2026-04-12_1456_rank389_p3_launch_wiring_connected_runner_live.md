# Rank 389 — P3 launch wiring 收口（scheduler enabled + first verified run）

- 时间：2026-04-12 14:55 UTC
- 对象：`Rank 389 / cross-venue net-carry ranking alpha`
- 执行动作：按 cycle_plan 第 1 小点完成 scheduler 安装启用并执行 first verified run（仅此一项）
- 结论：`done`

## 本轮改变系统认知的一句话
`Rank 389` 已完成 `P3 launch wiring` 收口：`momentum-rank389-paper-refresh.timer` 已 `enabled + active(waiting)`，且 `momentum-rank389-paper-refresh.service` 首跑成功并写出 14:55 UTC 的 runtime artifact（含 `window_ms / edge_before_cost / edge_after_cost / venue_pair`），运行态可写为 `connected_runner_live`。

## 本轮执行
1) 新增并落库 unit：
- `ops/systemd/momentum-rank389-paper-refresh.service`
- `ops/systemd/momentum-rank389-paper-refresh.timer`

2) 安装到系统并启用：
- `/etc/systemd/system/momentum-rank389-paper-refresh.service`
- `/etc/systemd/system/momentum-rank389-paper-refresh.timer`
- `systemctl daemon-reload`
- `systemctl enable --now momentum-rank389-paper-refresh.timer`

3) first verified run：
- `systemctl start momentum-rank389-paper-refresh.service`
- service 退出状态：`0/SUCCESS`

## 关键状态快照
- Timer: `momentum-rank389-paper-refresh.timer`
  - Loaded: `enabled`
  - Active: `active (waiting)`
  - Next Trigger: `2026-04-12 15:00:00 UTC`
- Service: `momentum-rank389-paper-refresh.service`
  - 最近首跑：`2026-04-12 14:55:05 UTC`
  - 退出状态：`0/SUCCESS`

## 首跑产物（验证）
- `reports/artifacts/paper_rank389_crossvenue_netcarry/rank389_runtime_artifact.json`
- `reports/artifacts/paper_rank389_crossvenue_netcarry/rank389_status.csv`
- `reports/artifacts/paper_rank389_crossvenue_netcarry/rank389_state.json`
- `reports/artifacts/paper_rank389_crossvenue_netcarry/rank389_last_run_summary.json`
- `reports/artifacts/paper_rank389_crossvenue_netcarry/rank389_launch_checks.csv`（新增 `2026-04-12T14:55:05Z` 记录）

## 阶段状态
- `Rank 389` 已从 `runner_ready_local_dryrun_ok` 推进到 `connected_runner_live`（以 scheduler+首跑验证为准）。
- cycle_plan 第 1 小点可标记为 `done`；第 2 小点为条件失败路径，本轮因第 1 小点成功而不触发。
