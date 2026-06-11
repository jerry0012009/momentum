# bot3 momentum auto-opt (13m)

- Time (UTC): 2026-03-22 00:35
- Desk board: `TRADING DESK BOARD（authoritative，2026-03-21）`

## Run 1 — EMA due-check first
- 读取 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`
- 结论：全 desk 仍为 `waiting_not_due`（最早到点：Crypto 1d+1wk 约 23.6h；A 股 1d 约 1.3d；美股约 1.8d）
- 因此：**不做伪 refresh**，按规则切到 Scout Seat。

## Run 2 — Rank 139 (P3) 接入 hosted narrow paper lane 的最小运行闭环
本轮只做 1 个动作：补齐 **monitoring board + refresh clock** 的“可运行可外显”最小闭环（并确保包含 `no_event_timeout` 字段）。

### 产出（artifacts）
- CSV：`reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/narrow_paper_pilot_monitoring_board.csv`
  - 已包含：`retention`、`mean_net@6bps`、`no_event_timeout_rate`、`same_dir_first_rate`、`opp_dir_first_rate`
- JSON（refresh clock snapshot）：`reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/narrow_paper_pilot_refresh_clock.json`

### 产出（site 落点）
- HTML：`reports/site/factors/scout_rank139_cusum_event_bar_confirm_veto_15m/narrow_paper_monitoring_board.html`

### 备注（策略口径冻结）
- 固定 baseline setups：BTC/ETH/SOL（15m）
- post-entry gate：`confirm_same_dir_only @ thr_mult=0.8`
- `no_event_timeout`：先按“未确认=不放行”的保守语义做可见性统计（本轮只做监控快照，不改执行引擎）。

## Run 3
- 按本轮资源约束（最多 1 个主点），**Run 3 留到下一次 cron**。

## Next
- 下一轮优先：把 Rank 139 的 hosted lane 接到现有 20m refresh lane 的“最小可跑”刷新路径（或补 1 个关键接线），避免扩新候选。
