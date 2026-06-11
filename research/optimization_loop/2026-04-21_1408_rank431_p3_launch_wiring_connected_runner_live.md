# Rank 431 / cointegration maker-first + hard time-stop pairs — P3 launch wiring connected_runner_live

- 时间：2026-04-21 14:08 UTC
- 执行者：bot3
- 对应 cycle_plan 小点：1
- target: `Rank 431 / cointegration maker-first + hard time-stop pairs`

## 本轮只执行的动作
按 `Paper launch queue` front-slot 要求，只做 `Rank 431` 的最小 launch wiring：落库 dedicated runner、安装并启用 scheduler、完成 first verified run，并把 runtime artifact 写回到 paper runner 目录。

## 本轮完成内容
### 1) dedicated runner 已落库
- `scripts/run_rank431_cointegration_maker_timestop_paper_runner.py`

冻结后的 launch 口径：
- live lane：`15m` rolling-admission pair spread fade
- execution：`maker-first`；若 maker 未成，则 `timeout-cross` 并追加 `4bps` extra fill cost
- exit：`zero-cross / structural-break / hard stop 48 bars (~12h)`
- friction：统一双腿 `16bps` round-trip
- core pair：`NEARUSDT-ATOMUSDT`
- secondary watch：`AVAXUSDT-SUIUSDT`
- rejected pair：`AVAXUSDT-ATOMUSDT`
- 不扩展到 `5m` child execution，也不把已证伪 pair 拉回 live host set

### 2) scheduler 已安装并启用
已写入并安装：
- `ops/systemd/momentum-rank431-paper-refresh.service`
- `ops/systemd/momentum-rank431-paper-refresh.timer`

已执行：
- `systemctl daemon-reload`
- `systemctl enable --now momentum-rank431-paper-refresh.timer`
- `systemctl start momentum-rank431-paper-refresh.service`

`systemctl status momentum-rank431-paper-refresh.timer --no-pager` 显示：
- `Loaded: loaded (/etc/systemd/system/momentum-rank431-paper-refresh.timer; enabled)`
- `Active: active (waiting)`
- `Trigger: 2026-04-21 14:13:00 UTC`

### 3) first verified run 已成功写出 runtime artifact
首跑成功执行：
- `python3 /root/clawd/jerry/momentum/scripts/run_rank431_cointegration_maker_timestop_paper_runner.py --refresh`
- `systemctl start momentum-rank431-paper-refresh.service`

service 首跑结果：
- `Result=success`

已写出 artifacts：
- `reports/artifacts/paper_rank431_cointegration_maker_timestop_pairs/rank431_status.csv`
- `reports/artifacts/paper_rank431_cointegration_maker_timestop_pairs/rank431_state.json`
- `reports/artifacts/paper_rank431_cointegration_maker_timestop_pairs/rank431_current_snapshot.csv`
- `reports/artifacts/paper_rank431_cointegration_maker_timestop_pairs/rank431_launch_checks.csv`
- `reports/artifacts/paper_rank431_cointegration_maker_timestop_pairs/rank431_live_signal_snapshot.csv`
- `reports/artifacts/paper_rank431_cointegration_maker_timestop_pairs/rank431_frozen_launch_spec.json`
- `reports/artifacts/paper_rank431_cointegration_maker_timestop_pairs/rank431_last_run_summary.json`

## verified run 核心状态
来自 `rank431_state.json` / `rank431_status.csv`：
- `wiring_status = connected_runner_live`
- `core_pair = NEARUSDT-ATOMUSDT`
- `core_net_mean_16bps ≈ +52.45`
- `core_recent7d_net16_mean ≈ +11.63`
- `watch_pair = AVAXUSDT-SUIUSDT`
- `watch_net_mean_16bps ≈ -0.06`
- `watch_recent7d_net16_mean ≈ +24.19`
- `cross_pair_overlap_ratio ≈ 0.7083`
- `rejected_pair = AVAXUSDT-ATOMUSDT`
- `rejected_net_mean_16bps ≈ -19.21`
- `decisive_blocker = none`
- `last_run_at_utc = 2026-04-21T14:06:41Z`

## 本轮结论
`Rank 431` 已完成 runner + scheduler + first verified run，`P3 launch wiring` 正式收口为 `connected_runner_live`；后续 routine refresh 由 `momentum-rank431-paper-refresh.timer` 驱动，不再停留在 queue 中等待接线。

## runtime 写回
- `Paper launch queue.current_target -> none`
- `Paper launch queue.connected_runner_live` 新增：`Rank 431 / cointegration maker-first + hard time-stop pairs (NEAR/ATOM core + AVAX/SUI watch)`
- `cycle_plan` item1：`status = done`
- `cycle_plan` item1.result：`Rank 431` 已完成 runner + scheduler + first verified run，P3 接线收口为 `connected_runner_live`

## 一句话结果（写回 state）
`Rank 431` 已完成 P3 launch wiring：dedicated runner `scripts/run_rank431_cointegration_maker_timestop_paper_runner.py` 已落库，systemd timer `momentum-rank431-paper-refresh.timer` 已启用并 active，首跑验证成功写出 `rank431_state/status/ledger/snapshot` artifacts，runtime 正式收口为 `connected_runner_live`。

## 尾部步骤记录（非阻断）
- homepage publish：`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 异步会话最终 `SIGKILL`，按 policy 记为非阻断尾部失败，不回滚本轮已完成的 verdict / state / log。
- 邮件通知：`python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot3-auto] Rank431已完成P3接线" --body-file /root/clawd/jerry/momentum/research/optimization_loop/2026-04-21_1408_rank431_p3_launch_wiring_connected_runner_live.md` 已成功发送。
