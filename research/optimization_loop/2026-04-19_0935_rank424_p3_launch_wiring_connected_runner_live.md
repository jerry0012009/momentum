# Rank 424 / cointegration-first pair admission × strongest residual z-score spread fade — P3 launch wiring connected_runner_live

## 本轮执行小点
- target: `Rank 424 / cointegration-first pair admission × strongest residual z-score spread fade`
- action: `P3 handoff / launch wiring`
- verdict: `connected_runner_live`

## 结论
`Rank 424` 已完成 `P3 launch wiring` 并进入 `connected_runner_live`：dedicated runner `scripts/run_rank424_cointegration_spreadfade_paper_runner.py` 已落库，systemd scheduler `momentum-rank424-paper-refresh.timer` 已安装并启用，首个 verified run 已成功写出 runtime artifact，故本对象不再停留在待接线队列。

## 本轮落地产物
### 1) runner script
- `scripts/run_rank424_cointegration_spreadfade_paper_runner.py`

冻结执行口径：
- core：`SOLUSDT/LTCUSDT`
- secondary/watch：`LINKUSDT/AVAXUSDT`
- exclude：`LINKUSDT/LTCUSDT`
- signal：`15m bar-close strongest residual z-score`
- execution：`next-bar conservative paper fill`
- exit：`12 bars (~3h) fixed time-stop`
- friction：`16bps` 双腿 round-trip
- 明确不启用 `5m child execution` 作为 launch 改善项，因为既有 summary 显示 `ret5_12 mean = -0.8337bps`

### 2) scheduler
已写入并启用：
- `ops/systemd/momentum-rank424-paper-refresh.service`
- `ops/systemd/momentum-rank424-paper-refresh.timer`

`systemctl status momentum-rank424-paper-refresh.timer` 显示：
- `Loaded: loaded (/etc/systemd/system/momentum-rank424-paper-refresh.timer; enabled)`
- `Active: active (waiting)`
- `Trigger: 2026-04-19 09:52:00 UTC`

### 3) first verified run
已执行：
- `python3 /root/clawd/jerry/momentum/scripts/run_rank424_cointegration_spreadfade_paper_runner.py --refresh`
- `systemctl start momentum-rank424-paper-refresh.service`

service 成功退出：`status=0/SUCCESS`。

已写出 artifact：
- `reports/artifacts/paper_rank424_cointegration_spreadfade/rank424_status.csv`
- `reports/artifacts/paper_rank424_cointegration_spreadfade/rank424_state.json`
- `reports/artifacts/paper_rank424_cointegration_spreadfade/rank424_current_snapshot.csv`
- `reports/artifacts/paper_rank424_cointegration_spreadfade/rank424_launch_checks.csv`
- `reports/artifacts/paper_rank424_cointegration_spreadfade/rank424_live_signal_snapshot.csv`
- `reports/artifacts/paper_rank424_cointegration_spreadfade/rank424_frozen_launch_spec.json`
- `reports/artifacts/paper_rank424_cointegration_spreadfade/rank424_last_run_summary.json`

## verified run 核心状态
来自 `rank424_state.json` / `rank424_status.csv`：
- `wiring_status = connected_runner_live`
- `core_pair = SOLUSDT/LTCUSDT`
- `core_signals_n = 458`
- `core_net_mean_bps_12bar_at_16 = +21.3813`
- `watch_pair = LINKUSDT/AVAXUSDT`
- `watch_net_mean_bps_12bar_at_16 = +2.3794`
- `excluded_pair = LINKUSDT/LTCUSDT`
- `excluded_net_mean_bps_12bar_at_16 = +1.2470`
- `router_5m_child_mean_bps_12 = -0.8337`
- `decisive_blocker = none`
- `last_run_at_utc = 2026-04-19T09:46:11Z`

## 对 runtime 的影响
- `Paper launch queue.current_target` 清为空，因为 `Rank 424` 已不再处于待接线状态
- `Paper launch queue.connected_runner_live` 新增 `Rank 424 / cointegration-first pair admission × strongest residual z-score spread fade (SOL/LTC core + LINK/AVAX watch)`
- `cycle_plan` 第 1 项写为 `done`

## 一句话 result
`Rank 424` 已完成 runner + scheduler + first verified run，P3 接线收口为 `connected_runner_live`，后续应由其 dedicated runner 按 13 分钟调度承担 routine refresh。