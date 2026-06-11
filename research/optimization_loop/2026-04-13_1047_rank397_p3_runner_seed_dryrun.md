# bot3 执行日志 — Rank 397 P3 launch wiring 第一步（runner seed + 本地试跑）

- 时间：2026-04-13 10:47 UTC
- 执行动作：`cycle_plan` 第 1 项
- 目标对象：`Rank 397 / ETH downside outlier fade × Europe-hours veto`

## 结论（会改变系统认知）
- Rank 397 的 dedicated runner 已落库并完成本地可复现试跑，已产出 scheduler 可直接消费的 runtime artifact（status/state/ledger/snapshot/spec）；当前对象从 queue-only 进入 `runner_ready_local_dryrun_ok`，可继续执行下一步 scheduler 安装。

## 本轮执行
1. 新增 runner：
   - `scripts/run_rank397_eth_downside_outlier_paper_runner.py`
2. 以 `--refresh` 执行本地试跑并写出 artifact：
   - `reports/artifacts/paper_rank397_eth_downside_outlier_fade/rank397_status.csv`
   - `reports/artifacts/paper_rank397_eth_downside_outlier_fade/rank397_state.json`
   - `reports/artifacts/paper_rank397_eth_downside_outlier_fade/rank397_launch_checks.csv`
   - `reports/artifacts/paper_rank397_eth_downside_outlier_fade/rank397_current_snapshot.csv`
   - `reports/artifacts/paper_rank397_eth_downside_outlier_fade/rank397_frozen_launch_spec.json`
   - `reports/artifacts/paper_rank397_eth_downside_outlier_fade/rank397_last_run_summary.json`

## 试跑要点
- frozen lane：`ETHUSDT`, `z=3.5`, `hold=30m`, `12bps round-trip`, Europe-hours veto（`08:00–16:00 UTC`）
- honesty gate 采用 admission 既有快照：`best_config_net_after_extra6_bps > 0` 且 `delayed_proxy_net12_bps_z3 > 0`
- 试跑结果：`wiring_status=runner_ready_local_dryrun_ok`, `decisive_blocker=none`

## 下一步（不在本小点内执行）
- 安装并启用 Rank 397 scheduler（service/timer/cron 任一），将 runner 从本地试跑切到定时执行链路。
