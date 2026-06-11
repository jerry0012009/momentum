# Rank 422 P3 launch wiring（前半段）：dedicated runner / handoff artifact 落库

- Time: 2026-04-19 00:54 UTC
- Target: `Rank 422 / 21:00–23:00 UTC fixed-window drift`
- Action: 只执行 `P3 launch wiring` 前半段；把已确认的 `EW5(BTC/ETH/SOL/BNB/DOGE) + 21:15 delay-one-bar` 直接固化成 dedicated runner / handoff artifact，不在本轮提前宣称 scheduler 或首跑已完成。

## 本轮实际落库产物

1. dedicated runner script
   - `scripts/run_rank422_fixed_window_drift_paper_runner.py`
   - 冻结执行语义为：
     - 仅使用 `21:00–21:15` 已闭合 bar 信息
     - `21:15 UTC` 固定入场
     - `23:00 UTC` 固定退出
     - `BTC/ETH/SOL/BNB/DOGE` 等权 EW5 basket
     - `8bps` round-trip paper cost 作为冻结口径

2. scheduler unit 模板（仅落库，尚未安装启用）
   - `ops/systemd/momentum-rank422-paper-refresh.service`
   - `ops/systemd/momentum-rank422-paper-refresh.timer`

3. runner 将在后续首跑时输出的标准 runtime artifact 路径也已冻结：
   - `reports/artifacts/paper_rank422_fixed_window_drift/rank422_status.csv`
   - `reports/artifacts/paper_rank422_fixed_window_drift/rank422_state.json`
   - `reports/artifacts/paper_rank422_fixed_window_drift/rank422_frozen_launch_spec.json`
   - `reports/artifacts/paper_rank422_fixed_window_drift/rank422_current_snapshot.csv`
   - `reports/artifacts/paper_rank422_fixed_window_drift/rank422_launch_checks.csv`

## 为什么这一步足够回答当前小点

本小点的 success criterion 是：必须产出可执行 runner script 或同等 dedicated wiring 产物，并把 `Rank 422` 从“queue 里的研究结论”推进到“已具备可接线 runner 语义”。

本轮已满足：
- 策略规则已被冻结到具体代码，而不再只是研究结论；
- runner 的输入输出、ledger/status/state/spec 路径已经固定；
- 下一小点可以直接围绕 `scheduler + first verified run` 接线，而不需要再补“怎么执行”的口头定义。

## 仍明确保留的唯一 blocker

当前还**没有**完成：
- systemd 安装/启用
- 至少一次 `--refresh` 首跑验证
- runtime artifact 的真实落地验证

因此 `Rank 422` 当前最诚实的 queue 语义应是：**runner_ready_pending_scheduler**，而不是 `connected_runner_live`。

## 小结 / result

`Rank 422` 的 `EW5(BTC/ETH/SOL/BNB/DOGE) + 21:15 delay-one-bar` 已落成 dedicated runner、service/timer 模板与冻结 artifact 路径，queue 状态已从“只有研究结论”推进到“runner_ready_pending_scheduler”；唯一剩余 blocker 收敛为 `scheduler + first verified run`。
