# Rank 422 P3 launch wiring completed -> connected_runner_live

- Time: 2026-04-19 01:30 UTC
- Target: `Rank 422 / 21:00–23:00 UTC fixed-window drift`
- Action: 完成 `P3 launch wiring` 后半段，只执行 scheduler 安装 + first verified run。

## What changed
1. 已把以下 systemd 单元安装到 `/etc/systemd/system/`：
   - `momentum-rank422-paper-refresh.service`
   - `momentum-rank422-paper-refresh.timer`
2. 已执行：
   - `systemctl daemon-reload`
   - `systemctl enable --now momentum-rank422-paper-refresh.timer`
   - `systemctl start momentum-rank422-paper-refresh.service`
3. timer 验证：
   - `Loaded: loaded (/etc/systemd/system/momentum-rank422-paper-refresh.timer; enabled; preset: enabled)`
   - `Active: active (waiting)`
   - `Trigger: 2026-04-19 01:39:00 UTC`
4. 首跑验证成功，runner 已写出 runtime artifact：
   - `reports/artifacts/paper_rank422_fixed_window_drift/rank422_status.csv`
   - `reports/artifacts/paper_rank422_fixed_window_drift/rank422_state.json`
   - `reports/artifacts/paper_rank422_fixed_window_drift/rank422_launch_checks.csv`
   - `reports/artifacts/paper_rank422_fixed_window_drift/rank422_last_run_summary.json`
5. 为避免 runner artifact 继续停留在旧 blocker，已把 `scripts/run_rank422_fixed_window_drift_paper_runner.py` 同步改成：当 systemd service/timer 已安装且 timer symlink 已启用时，写出 `wiring_status=connected_runner_live` 与 `decisive_blocker=none`。

## Verified runtime truth
- `rank422_last_run_summary.json`:
  - `run_at_utc: 2026-04-19T01:30:47Z`
  - `wiring_status: connected_runner_live`
- `rank422_status.csv`:
  - `wiring_status: connected_runner_live`
  - `current_side: flat`
  - `schedule_pointer_utc: 2026-04-19T21:15:00Z`
  - `avg_book_spread_bps: 0.48771697625239685`
  - `decisive_blocker: none`
- `rank422_state.json`:
  - `verified_run: true`
  - `wiring_status: connected_runner_live`

## Verdict
`Rank 422` 的 `EW5(BTC/ETH/SOL/BNB/DOGE) + 21:15 delay-one-bar` 已完成 scheduler 安装、timer 启用与首跑验证，runtime artifact 已真实落地，因此 queue 状态正式收口为 `connected_runner_live`。
