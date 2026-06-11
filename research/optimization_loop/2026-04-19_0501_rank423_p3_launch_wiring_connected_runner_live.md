# Rank 423 P3 launch wiring：runner + scheduler + first verified run 已接通，connected_runner_live

- 时间：2026-04-19 05:01 UTC
- 对象：`Rank 423 / liquidation shock × OI unwind -> 30m exhaustion fade`
- 执行动作：`P3 handoff / launch wiring`
- 结论：`connected_runner_live`

## 本轮完成项
1. 新增 dedicated runner：`scripts/run_rank423_liqshock_oiunwind_paper_runner.py`
   - frozen scope：`BTC/SOL/XRP` core
   - `ETH/ADA` 只保留为 watch，不进入默认 live runner
   - 固定口径：`5m signal -> 1 bar delay -> 30m fixed hold`
2. 新增 scheduler unit：
   - `ops/systemd/momentum-rank423-paper-refresh.service`
   - `ops/systemd/momentum-rank423-paper-refresh.timer`
3. 已安装并启用 systemd timer：`momentum-rank423-paper-refresh.timer`
4. 已完成首跑验证：`2026-04-19 05:01:12 UTC`

## 首跑产物
- `reports/artifacts/paper_rank423_liqshock_oiunwind_exhaustionfade/rank423_frozen_launch_spec.json`
- `reports/artifacts/paper_rank423_liqshock_oiunwind_exhaustionfade/rank423_current_snapshot.csv`
- `reports/artifacts/paper_rank423_liqshock_oiunwind_exhaustionfade/rank423_status.csv`
- `reports/artifacts/paper_rank423_liqshock_oiunwind_exhaustionfade/rank423_state.json`
- `reports/artifacts/paper_rank423_liqshock_oiunwind_exhaustionfade/rank423_launch_checks.csv`
- `reports/artifacts/paper_rank423_liqshock_oiunwind_exhaustionfade/rank423_last_run_summary.json`

## 验证结果
- `systemctl enable --now momentum-rank423-paper-refresh.timer` 成功
- `systemctl start momentum-rank423-paper-refresh.service` 成功
- 首跑 summary：
  - `wiring_status = connected_runner_live`
  - `decisive_blocker = none`
  - `min_core_delay1_net8_bps_admission = 11.1084`
  - `avg_book_spread_bps ≈ 0.6271`

## 系统认知变化
`Rank 423` 不再只是 queue 中等待 handoff 的 P3 对象；它已经具备 dedicated runner、已启用 scheduler，并在 `2026-04-19 05:01 UTC` 产出首个 verified runtime artifact，因此本轮应把 `Paper launch queue` truth 收口为 `connected_runner_live`。

## runtime writeback
- `Paper launch queue.current_target -> none`
- `connected_runner_live` 新增 `Rank 423`
- `cycle_plan[1].status -> done`
- `cycle_plan[1].result -> Rank 423 已完成 P3 接线并进入 connected_runner_live`
