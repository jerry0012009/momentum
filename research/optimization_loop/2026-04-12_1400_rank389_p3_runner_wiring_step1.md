# Rank 389 P3 launch wiring step1 — dedicated runner 落库 + dry run artifact（done）

- 时间：2026-04-12 14:00 UTC
- 对象：`Rank 389 / cross-venue net-carry ranking alpha`
- 执行动作：按 `cycle_plan` 第 1 小点落地 dedicated runner，并做单次 dry run。

## 本轮产出
1. 新增 runner 脚本：`scripts/run_rank389_crossvenue_netcarry_paper_runner.py`
2. dry run 命令：
   - `python3 /root/clawd/jerry/momentum/scripts/run_rank389_crossvenue_netcarry_paper_runner.py --refresh`
3. 生成 runtime artifacts：
   - `reports/artifacts/paper_rank389_crossvenue_netcarry/rank389_runtime_artifact.json`
   - `reports/artifacts/paper_rank389_crossvenue_netcarry/rank389_current_snapshot.csv`
   - `reports/artifacts/paper_rank389_crossvenue_netcarry/rank389_launch_checks.csv`
   - `reports/artifacts/paper_rank389_crossvenue_netcarry/rank389_status.csv`
   - `reports/artifacts/paper_rank389_crossvenue_netcarry/rank389_state.json`
   - `reports/artifacts/paper_rank389_crossvenue_netcarry/rank389_last_run_summary.json`

## 关键验证（满足 step1 success_criterion）
- dry run 已成功产出包含以下字段的 runtime artifact：
  - `window_ms`: `519`
  - `edge_before_cost`: `0.03451248367778714`
  - `edge_after_cost`: `0.0059011026707019385`
  - `venue_pair`: `dydx->hyperliquid`
- `wiring_status`: `runner_ready_local_dryrun_ok`
- `decisive_blocker`: `none`

## 会改变系统认知的一句话
`Rank 389` 的 dedicated runner 已可复跑且 dry run 产出标准 runtime artifact，`collector_receive_ts` 同窗护栏与成本后正边际在接线形态下保持成立，可进入下一步 scheduler + first verified run。
