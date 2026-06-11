# Rank 427 / high-volume selloff -> 5m bounce launch wiring connected_runner_live

- 时间：2026-04-20 01:16 UTC
- 对象：`Rank 427 / high-volume selloff -> 5m bounce (ex-ETH core bounce sleeve)`
- 动作：`P3 handoff / launch wiring`
- 结论：`connected_runner_live`

## 本轮完成内容
1. 落库 dedicated runner：`scripts/run_rank427_highvol_selloff_bounce_paper_runner.py`
2. 落库 scheduler 单元：
   - `ops/systemd/momentum-rank427-paper-refresh.service`
   - `ops/systemd/momentum-rank427-paper-refresh.timer`
3. 已安装到 `/etc/systemd/system/`，执行 `systemctl daemon-reload`
4. 已启用 timer：`momentum-rank427-paper-refresh.timer`
5. 已单独触发首跑验证：`systemctl start momentum-rank427-paper-refresh.service`
6. 首跑产出 runtime artifact：
   - `reports/artifacts/paper_rank427_highvol_selloff_bounce/rank427_status.csv`
   - `reports/artifacts/paper_rank427_highvol_selloff_bounce/rank427_state.json`
   - `reports/artifacts/paper_rank427_highvol_selloff_bounce/rank427_current_snapshot.csv`
   - `reports/artifacts/paper_rank427_highvol_selloff_bounce/rank427_live_signal_snapshot.csv`
   - `reports/artifacts/paper_rank427_highvol_selloff_bounce/rank427_launch_checks.csv`
   - `reports/artifacts/paper_rank427_highvol_selloff_bounce/rank427_frozen_launch_spec.json`

## 冻结后的 runner 定义
- live scope：`BTCUSDT / SOLUSDT / BNBUSDT / DOGEUSDT`
- excluded：`ETHUSDT`
- 信号口径：复用 `2026-04-19_highvol_selloff_bounce_5m_panel.csv` 的 `signal=1`
- 执行壳：`5m` short-hold bounce sleeve
- 退出：固定 `hold12`（约 `1h`）
- 成本：统一 `8bps` round-trip
- 不允许回退到已证伪的 `strongest-only top1 router`，也不拉长到 `hold36`

## 首跑验证结果
- timer 状态：`enabled + active`
- 首跑后 runner 状态：`connected_runner_live`
- `rank427_status.csv` 记录：
  - `core_hold12_net8_mean_bps ≈ +22.86`
  - `top2_hold12_net8_mean_bps ≈ +21.45`
  - `avg_book_spread_bps ≈ 0.61`
  - `decisive_blocker = none`
- `rank427_last_run_summary.json` 记录：`wiring_status = connected_runner_live`

## 本轮 verdict
`Rank 427` 已不再停留在仅 queue-ready 的模糊状态：dedicated runner、scheduler 与 first verified run 已全部落地，且 runtime artifact 已写出，因此本轮正式把它记为 `connected_runner_live`。

## 尾部步骤记录
- `publish_homepage_index.sh` 作为非阻断 tail step 启动后未在轮次窗口内完成，随后异步会话被终止（SIGKILL）；不影响本轮已写出的 state / runner artifact / verdict。
- 中文邮件摘要已成功发送。
