# bot3 optimization loop — 2026-03-21 19:57 UTC — Rank 139 CUSUM confirm/veto 最小 clean replication

## TL;DR（本轮 1 主点 + 1 紧邻子点）
- **主点（Run 2）：** 已完成 `Rank 139 / CUSUM event-bar confirm-veto gate` 的 **1 次最小 clean replication**（BTC/ETH/SOL · 15m baseline + entry 后 1m 事件）。
- **紧邻子点（Run 3）：** 依据结果给出 **hard verdict：建议 `promote_P2 (paper candidate)`**，采取更稳的 `veto_opp_dir` 作为 shared confirm/veto layer；`confirm_same_dir_only` 作为激进备选但可能偏“后验筛选”。

---

## Run 1 — EMA due-check first（Paper Seat）
执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`

结果：脚本按 guard 正常退出（exit code = `2`），确认当前 **无 `due-now / overdue` lane**，因此 `EMA = waiting_not_due`，不得伪造 refresh。
- 最近 due：`Crypto 1d+1wk（BTC/ETH/SOL）` 约 **4.0h** 后到点

结论：符合 desk board；本轮合法主动作立即切到 `Scout Seat`。

---

## Run 2 — Rank 139 minimal clean replication（Scout Seat 主点）
执行：`python3 scripts/build_rank139_cusum_event_bar_confirm_veto_clean_replication.py`

产物：
- CSV：`reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/summary_by_arm.csv`
- 页面：`reports/site/factors/scout_rank139_cusum_event_bar_confirm_veto_15m/report.html`

关键结果（跨 BTC/ETH/SOL × setups 汇总，成本=6bps/side）：
- **baseline**（不加 gate）：`mean_net@6bps ≈ -0.00155`，明显为负。
- **veto_opp_dir**（先出现 opp_dir_first 则 veto）：
  - `thr=0.8×ATR15m%`：`trades=70`（retention≈49.6%）
  - `mean_net@6bps ≈ +0.00342`，`positive_ratio≈51.4%`
- **confirm_same_dir_only**（只保留 same_dir_first）：
  - `thr=0.8×ATR15m%`：`trades=43`（retention≈30.5%）
  - `mean_net@6bps ≈ +0.00536`，`positive_ratio≈60.5%`

解读：
- **方向确认/否决层**在这份最小样本里是“有增量”的：baseline 成本后为负，而两种 gate 都把成本后期望拉正。
- 但 `confirm_same_dir_only` 的 retention 明显塌缩，更像强筛选；更稳的实现路径应先用 `veto_opp_dir`。

---

## Run 3 — 条件分支 hard verdict（紧邻子点）
本轮不打开新候选（严格不同时并行多个 Scout）。只给 Rank 139 结论。

**Hard verdict：`Rank 139 = promote_P2 (paper candidate)`**，推荐落地为 **shared confirm/veto layer**：
- 默认采用：`veto_opp_dir @ thr_mult=0.8×ATR15m%`
- 解释口径：entry 后观察 1m 价格路径，若先出现与信号相反方向的 first-event（越阈），则 **直接 veto**；否则保留交易。

原因（按 desk 规则）：
- `veto_opp_dir` 在 retention 仍可接受（~50%）的前提下，把 baseline 的成本后负期望翻转为正。
- `confirm_same_dir_only` 虽更高，但 retention 更低，风险是更接近“后验挑选”，不作为第一落地方案。

建议（不在本轮执行，留给后续排期）：
- 若要进一步稳固：补 1 个更贴近执行的 cheap check（例如：固定 `veto_opp_dir`，仅扩样本/延长窗口或做 out-of-week sanity），再考虑从 `P2 -> Paper Seat sidecar` 的接线。

---

## 本轮运行时间与可见落点
- generated_at（报告页标注）：`2026-03-21 19:57 UTC`
- 页面落点：`reports/site/factors/scout_rank139_cusum_event_bar_confirm_veto_15m/report.html`
