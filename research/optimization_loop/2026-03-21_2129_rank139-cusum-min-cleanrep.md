# bot3 auto opt loop — Run1→Run2→Run3（2026-03-21 21:29 UTC）

> 依据 `docs/TODO.md` 顶部 **TRADING DESK BOARD（authoritative，2026-03-21）** 执行：
> - Run1：EMA due-check first
> - Run2：若 EMA waiting_not_due → Rank139 最小 clean replication
> - Run3：基于 Run2 结果给出 promote/park 的硬结论

## Run 1 — Paper Seat（EMA）due-check
- 执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --skip-build --require-due`
- 结果：**无 due-now / overdue**（wrapper 以 exit code=2 退出，符合预期）
- 最近到点：`Crypto 1d+1wk（BTC/ETH/SOL）` 约 **23.8 小时** 后到点
- 结论：Paper Seat = **waiting_not_due**，本轮合法切换到 Scout Seat。

## Run 2 — Scout Seat（Rank 139）最小 clean replication
- 执行：`python3 scripts/build_rank139_cusum_event_bar_confirm_veto_clean_replication.py`
- 产物：
  - `reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/summary_by_arm.csv`
  - `reports/site/factors/scout_rank139_cusum_event_bar_confirm_veto_15m/report.html`

### 关键读数（只抓“是否值得继续”的最小证据）
baseline（不加 event gate）：
- trades=141
- mean_net@6bps = **-0.1548%**（为负）
- positive_ratio_net = **37.6%**

加入 post-entry event gate 后（都显著转正，代价是 retention 降低）：
- `confirm_same_dir_only`：
  - thr_mult=0.8：trades=43（retention 0.305）
  - mean_net@6bps = **+0.5363%**，positive_ratio_net=**60.5%**
- `veto_opp_dir`：
  - thr_mult=0.8：trades=70（retention 0.496）
  - mean_net@6bps = **+0.3423%**，positive_ratio_net=**51.4%**

解释口径（对齐 board 里的问题）：
- `same_dir_first / opp_dir_first / no_event_timeout` 三分法在该样本里**足够可用**；
- “同向先触发 → 才继续持有”这个 confirm 版本在 thr=0.8 时给出最强净值改善；
- `no_event_timeout` 比例随阈值上升而上升（thr=0.8 baseline 约 19%），但仍可接受。

## Run 3 — 硬结论（promote / park / keep）
**结论：Rank 139 = promote_P2（从 keep_P1 升格）**。

理由（只保留 1 句硬理由）：
- 在同一套 BTC/ETH/SOL 15m baseline 上，加入 post-entry CUSUM event-confirm/veto 后，**net expectancy 从负转正**，且是“可审计 + 不引入前视”的结构性提升。

下一步建议（不在本轮展开）：
- P2 要做的最小追加：把 `thr_mult∈{0.6,0.8}` 做一次更稳定的对比（并固定一个默认值），再补 1 页轻量 scorecard。

---

### 本轮网页落点
- Rank 139 报告页：`reports/site/factors/scout_rank139_cusum_event_bar_confirm_veto_15m/report.html`
