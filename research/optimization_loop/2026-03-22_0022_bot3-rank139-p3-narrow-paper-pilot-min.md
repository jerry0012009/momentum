# bot3 auto loop — Rank139 P3 narrow paper pilot (minimal)

- time: 2026-03-22 00:22 UTC
- scope: **Run1 → Run2 → Run3**（按 TRADING DESK BOARD 顺序执行；本轮主点=Rank139 hosted P3 可见性闭环，紧邻子点=EMA due-check）

## Run 1 — EMA due-check first（require-due）
执行：
```bash
cd jerry/momentum && python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due
```
结果：**没有 due-now / overdue lane**（脚本按设计返回 code=2）。
- 最新输出显示最靠前 lane 仍是 `Crypto 1d+1wk（BTC/ETH/SOL）`，`waiting_not_due`，`约 23.6 小时 后到点`。
- 同时 `ema_paper_trading_refresh_history.csv` 追加了 1 条新 completed-bar rows（累计 27）。

结论：Paper Seat 本轮合法继续视为 `running paper / waiting_not_due`，按板子切到 Scout Seat。

## Run 2 — Rank139 (P3) 接入 hosted narrow paper pilot 的最小运行闭环
目标：给 Rank139 一个**可见的**“narrow paper pilot”面板（ledger/monitoring/refresh clock 的最小替身），并把 `no_event_timeout` 纳入监控字段。

本轮实现（最小可运行）：
1) 先重跑 Rank139 minimal clean replication（确保 trade_log/summary/report 产出齐全）
```bash
cd jerry/momentum && python3 scripts/build_rank139_cusum_event_bar_confirm_veto_clean_replication.py
```
产出：
- artifact: `reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/summary_by_arm.csv`
- artifact: `reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/trade_log.csv`
- page: `reports/site/factors/scout_rank139_cusum_event_bar_confirm_veto_15m/report.html`

2) 生成 hosted P3 的 monitoring board（默认 desk gate：`confirm_same_dir_only @ thr_mult=0.8`，并显示 `no_event_timeout`）
```bash
cd jerry/momentum && python3 scripts/build_rank139_narrow_paper_pilot_minimal.py
```
新增产出：
- artifact: `reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/narrow_paper_pilot_monitoring_board.csv`
- artifact: `reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/narrow_paper_pilot_refresh_clock.json`
- page: `reports/site/factors/scout_rank139_cusum_event_bar_confirm_veto_15m/narrow_paper_monitoring_board.html`

说明：
- 这是 **ops 可见性闭环**（让 Rank139 具备“pilot 面板 + 可追溯 artifact + 网页落点”），不是把它硬塞进现有 20m `manual_narrow_paper_lanes` 托管 runner。
- 监控字段覆盖：`trades/retention/mean_net@6bps/positive_ratio/no_event_timeout`（其中 positive_ratio 目前在 research summary 表里；monitor board 里先给 base vs kept 的 mean_net & retention/no_event_timeout）。

## Run 3 — 只选 1 个
按 TRADING DESK BOARD 的判定分支：
- 由于 Run2 已把 Rank139 的 **关键接线（最小可见性闭环）**补齐，本轮 Run3 选择：**“补 1 个阻塞点” 已完成**（不扩新候选，避免打开多个 Scout 候选）。

## 下一步（留给下一轮）
- 如果要把 Rank139 真正变成“hosted narrow paper lane（可定时 refresh 的 ledger）”，下一步应把 Rank139 gate 逻辑接入 `scripts/run_manual_narrow_paper_lanes.py` 或做一个单独的低频 refresh runner（更符合 desk 的“低频健康检查”要求），并把输出写入统一的 `manual_narrow_paper_*` 状态/ledger。
- 当前先以页面+artifact 的最小闭环满足 Scout Seat 的“可见性 + 不研究化磨损”。
