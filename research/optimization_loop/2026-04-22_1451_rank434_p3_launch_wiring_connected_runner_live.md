# Rank 434 / newlisting early-short bubble fade — P3 launch wiring connected_runner_live

- 时间：2026-04-22 14:51 UTC
- 执行者：bot3
- 对应 cycle_plan 小点：1
- target: `Rank 434 / newlisting early-short bubble fade`

## 本轮只执行的动作
按 `Paper launch queue` front-slot 要求，只做 `Rank 434` 的最小 launch wiring：落库 dedicated runner、安装并启用 scheduler、完成 first verified run，并把 runtime artifact 写回到 paper runner 目录。

## 本轮完成内容
### 1) dedicated runner 已落库
- `scripts/run_rank434_newlisting_earlyshort_paper_runner.py`

冻结后的 launch 口径：
- scope：Binance USDⓈ-M newly listed USDT perps；仅 early listing short bubble-fade sleeve
- entry：listing age `>= 3d` 且 close 位于 trailing `3d` high 的 `95%` 阈值附近，同时 latest funding 为正
- exit：desk paper lane 冻结 `8% TP / 5% SL / 3d hard timeout`
- 风控：每个 symbol/listing window 最多 `3` 笔；paper admission 语义为每 symbol `1-3` early trades；额外 `+100bps` early-listing execution buffer 作为最保守诚实检验
- honesty：listing-age gate、per-symbol cap、short availability / funding check、child fill realism 都写入 runner snapshot/state

### 2) scheduler 已安装并启用
已写入并安装：
- `ops/systemd/momentum-rank434-paper-refresh.service`
- `ops/systemd/momentum-rank434-paper-refresh.timer`

已执行：
- `systemctl daemon-reload`
- `systemctl enable --now momentum-rank434-paper-refresh.timer`
- `systemctl start momentum-rank434-paper-refresh.service`

`systemctl status momentum-rank434-paper-refresh.timer --no-pager` 显示：
- `Loaded: loaded (/etc/systemd/system/momentum-rank434-paper-refresh.timer; enabled)`
- `Active: active (waiting)`
- `Trigger: 2026-04-22 14:52:00 UTC`

### 3) first verified run 已成功写出 runtime artifact
首跑成功执行：
- `python3 /root/clawd/jerry/momentum/scripts/run_rank434_newlisting_earlyshort_paper_runner.py --refresh`
- `systemctl start momentum-rank434-paper-refresh.service`

service 首跑结果：
- `Result=success`
- `ExecMainStatus=0`

已写出 artifacts：
- `reports/artifacts/paper_rank434_newlisting_earlyshort_bubble_fade/rank434_status.csv`
- `reports/artifacts/paper_rank434_newlisting_earlyshort_bubble_fade/rank434_state.json`
- `reports/artifacts/paper_rank434_newlisting_earlyshort_bubble_fade/rank434_current_snapshot.csv`
- `reports/artifacts/paper_rank434_newlisting_earlyshort_bubble_fade/rank434_launch_checks.csv`
- `reports/artifacts/paper_rank434_newlisting_earlyshort_bubble_fade/rank434_live_signal_snapshot.csv`
- `reports/artifacts/paper_rank434_newlisting_earlyshort_bubble_fade/rank434_frozen_launch_spec.json`
- `reports/artifacts/paper_rank434_newlisting_earlyshort_bubble_fade/rank434_last_run_summary.json`

## verified run 核心状态
来自 `rank434_state.json` / `rank434_status.csv`：
- `wiring_status = connected_runner_live`
- `candidate_rank = 434`
- `cap3_avg_net_after_extra_100bps_pct ≈ +1.3643%/trade`
- `cap3_positive_months = 3`
- `decisive_blocker = none`
- `last_run_at_utc = 2026-04-22T14:51:24Z`

## 本轮结论
`Rank 434` 已完成 P3 launch wiring：dedicated runner `scripts/run_rank434_newlisting_earlyshort_paper_runner.py` 已落库，systemd timer `momentum-rank434-paper-refresh.timer` 已启用并 active，首跑验证成功写出 `rank434_state/status/ledger/snapshot` artifacts，runtime 正式收口为 `connected_runner_live`。

## runtime 写回
- `Paper launch queue.current_target -> none`
- `Paper launch queue.connected_runner_live` 新增：`Rank 434 / newlisting early-short bubble fade (3d listing-age + funding-positive high-window short, capped early trades)`
- `cycle_plan` item1：`status = done`
- `cycle_plan` item1.result：`Rank 434` 已完成 runner + scheduler + first verified run，P3 接线收口为 `connected_runner_live`

## 一句话结果
`Rank 434` 已完成 P3 launch wiring：dedicated runner、systemd timer、首跑验证均已落地，runtime 正式进入 `connected_runner_live`。

## 尾部步骤记录（非阻断）
- homepage publish：`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 异步会话最终 `SIGKILL`（`tide-nud`）；按 policy 记为非阻断尾部失败，不回滚本轮 verdict/state/log。
- 邮件通知：`python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot3-auto] Rank434完成P3接线" --body-file /root/clawd/jerry/momentum/research/optimization_loop/2026-04-22_1451_rank434_p3_launch_wiring_connected_runner_live.md` 已成功发送。
