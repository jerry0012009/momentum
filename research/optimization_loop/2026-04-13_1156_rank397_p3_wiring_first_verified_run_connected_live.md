# Rank 397 — P3 launch wiring step（scheduler 路径首跑验证并收口到 connected_runner_live）

- 时间：2026-04-13 11:56 UTC
- 对象：`Rank 397 / ETH downside outlier fade × Europe-hours veto`
- 执行动作：按 `cycle_plan` 第 2 小点完成 scheduler 路径 first verified run 核验，并把运行证据写回 runtime
- 结论：`done`

## 本轮改变系统认知的一句话
`Rank 397` 已在 scheduler 路径完成首跑（service `status=0/SUCCESS`，最近 `2026-04-13T11:52:01Z`），且 `paper_rank397_eth_downside_outlier_fade` artifact（status/state/ledger/snapshot/spec）齐备，故 `P3 launch wiring` 收口并迁入 `connected_runner_live`。

## 核验记录
1) systemd timer / service 状态
- `momentum-rank397-paper-refresh.timer`: `enabled`, `active (waiting)`
- `momentum-rank397-paper-refresh.service`: 最近一次执行成功退出
- 关键日志：
  - `ExecStart=/usr/bin/python3 /root/clawd/jerry/momentum/scripts/run_rank397_eth_downside_outlier_paper_runner.py --refresh`
  - `code=exited, status=0/SUCCESS`
  - 最近成功时间：`2026-04-13 11:52:01 UTC`

2) 首跑产物（可追溯 artifact）
- `reports/artifacts/paper_rank397_eth_downside_outlier_fade/rank397_status.csv`
- `reports/artifacts/paper_rank397_eth_downside_outlier_fade/rank397_state.json`
- `reports/artifacts/paper_rank397_eth_downside_outlier_fade/rank397_launch_checks.csv`
- `reports/artifacts/paper_rank397_eth_downside_outlier_fade/rank397_current_snapshot.csv`
- `reports/artifacts/paper_rank397_eth_downside_outlier_fade/rank397_frozen_launch_spec.json`
- `reports/artifacts/paper_rank397_eth_downside_outlier_fade/rank397_last_run_summary.json`

3) 运行态关键字段
- `wiring_status`: `runner_ready_local_dryrun_ok`
- `decisive_blocker`: `none`
- `run_at_utc`: `2026-04-13T11:52:01Z`

## runtime 回写
- `BOT2_BOT3_STATE.md` 已更新：
  - `Paper launch queue.current_target` → `none`
  - `Rank 397` 加入 `connected_runner_live`
  - `cycle_plan` 第 2 小点 `status: done` 并写入 result
