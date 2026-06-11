# bot3 auto loop @ 2026-03-21 19:43 UTC

## TRADING DESK BOARD 读取结论（只摘本轮相关）
- Run1：EMA due-check first（若 waiting_not_due → 立刻切 Scout Seat）
- Run2：Rank 139 / CUSUM event-bar confirm-veto gate：做 1 次最小 clean replication
- Run3：若 Run2 过关，给 promote_P2/P3/keep_P1 的硬结论

---

## Run 1 — EMA due-check（结果：waiting_not_due）
执行：
- `python3 jerry/momentum/scripts/run_ema_paper_trading_guarded_refresh.py --skip-build --require-due`

结果要点：
- 当前 **无 due-now / overdue lane**（脚本 exit code=2 符合预期）
- 最靠前 lane：`Crypto 1d+1wk（BTC/ETH/SOL）` 仍 `waiting_not_due`（约 23.8h 后到点）

=> 按 desk board 规则：**不空转，切 Scout Seat**。

---

## Run 2 — Rank 139 最小 clean replication（完成）
执行：
- `python3 jerry/momentum/scripts/build_rank139_cusum_event_bar_confirm_veto_clean_replication.py`

产物：
- artifacts：`reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/summary_by_arm.csv`
- site：`reports/site/factors/scout_rank139_cusum_event_bar_confirm_veto_15m/report.html`

### 核心读数（summary_by_arm.csv）
对比 baseline（固定 hold、成本 6bps）：baseline 在该样本下 **mean_net@6bps ≈ -0.155%**。

新增 post-entry 的 event-confirm/veto 后（保留率下降到 ~30%~50%），但每笔期望显著抬升：
- `thr_mult=0.8`
  - `veto_opp_dir`：trades=70（retention≈0.50），mean_net@6bps≈ +0.342%，positive_ratio≈51%
  - `confirm_same_dir_only`：trades=43（retention≈0.305），mean_net@6bps≈ +0.536%，positive_ratio≈60%
- `thr_mult=0.6`
  - `veto_opp_dir`：mean_net@6bps≈ +0.196%，positive_ratio≈48%
  - `confirm_same_dir_only`：mean_net@6bps≈ +0.191%，positive_ratio≈50%
- `thr_mult=0.4`
  - 两个 arm mean_net@6bps≈ +0.205%（positive_ratio≈50%）

结构一致性：
- `confirm_same_dir_only` 天然只保留 `same_dir_first=1.0`
- `veto_opp_dir` 在多数阈值下 `opp_dir_first=0`，说明 veto 规则被触发有效过滤。

---

## Run 3 — 硬结论（promote）
本轮最小 clean replication **过关**（在多阈值下都把 post-cost mean 从负抬到显著为正，且逻辑符合“post-entry、时间顺序、无泄漏”的约束）。

**Hard verdict：promote_P2（作为 shared 的 post-entry event-confirm / veto layer 候选）**
- 推荐优先落点：`thr_mult=0.8`，两种 arm 都明显改善；其中 `confirm_same_dir_only` 更像“更少交易、更高质量”的 confirm 层。
- 备注：这是“gate layer / confirm-veto 层”的结论，不等同于新 alpha；下一步应在更长窗口/更多样本做轻量 time-stability（但不在本轮展开）。

---

## 本轮可见落点（网页）
- `reports/site/factors/scout_rank139_cusum_event_bar_confirm_veto_15m/report.html`

