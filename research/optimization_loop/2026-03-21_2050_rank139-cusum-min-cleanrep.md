# bot3 optimization loop — Rank139 最小 clean replication（CUSUM event-bar confirm/veto）

时间：2026-03-21 20:50 UTC

## Run1（Paper Seat due-check）
- 执行：`python3 jerry/momentum/scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：**无 due-now / overdue**，`Paper Seat=EMA` 处于 `waiting_not_due`
  - 最靠前：`Crypto 1d+1wk（BTC/ETH/SOL）` 距离到点约 **3.1 小时**
- 结论：符合 desk board 规则 → **立刻切 Scout Seat**，不空转、不做伪 refresh。

## Run2（Scout Seat / Rank139：1 次最小 clean replication）
- 执行：`python3 jerry/momentum/scripts/build_rank139_cusum_event_bar_confirm_veto_clean_replication.py`
- 产出：
  - artifact：`reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/summary_by_arm.csv`
  - 页面：`reports/site/factors/scout_rank139_cusum_event_bar_confirm_veto_15m/report.html`

### 核心读数（post-cost, 6bps；固定 hold=8×15m bars；1m 窗口=45min）
基线（baseline）在本次抽样下 **mean_net@6bps 为负**：
- baseline：`mean_net@6bps ≈ -0.1548%`（trades=141，positive_ratio≈0.376）

加入 CUSUM 事件的 post-entry gate 后（retention 下降，但期望显著转正）：
- `thr_mult=0.4`
  - veto_opp_dir：trades=52（retention≈0.369），mean_net≈**+0.2045%**，positive_ratio≈0.50
  - confirm_same_dir_only：trades=51（retention≈0.362），mean_net≈**+0.2090%**，positive_ratio≈0.510
- `thr_mult=0.6`
  - veto_opp_dir：trades=66（retention≈0.468），mean_net≈**+0.1957%**
  - confirm_same_dir_only：trades=52（retention≈0.369），mean_net≈**+0.1909%**
- `thr_mult=0.8`
  - veto_opp_dir：trades=70（retention≈0.496），mean_net≈**+0.3423%**
  - confirm_same_dir_only：trades=43（retention≈0.305），mean_net≈**+0.5363%**，positive_ratio≈0.605

补充：在 `confirm_same_dir_only` 下，样本里基本都是 `same_dir_first=1.0`（按定义筛选）。

## Run3（硬结论 / 下一步）
### 硬结论（本轮可审计）
- 这次“最小 clean replication”给出的信号非常一致：
  - baseline（不加 gate）在 post-cost 维度为负；
  - **只要用 CUSUM 事件做 post-entry gate（veto 或 confirm）就能把 mean_net 拉到显著为正**，且跨 `thr_mult=0.4/0.6/0.8` 都成立。
- 代价是 trade retention 明显下降（约 0.30~0.50），但这是可以接受的：它本来就是 *event-confirm / veto layer* 的职责。

### Desk decision（对 TRADING DESK BOARD 的动作建议）
- **建议：`Rank 139` 从 `keep_P1` → `promote_P2`（可作为 shared 的 post-entry event-confirm/veto layer 进入更正式的对照队列）。**
- 仍需 1 个“更严格但仍轻量”的跟进（不在本轮展开）：
  - 固定一个默认阈值候选（我倾向先用 `thr_mult=0.6` 的 `veto_opp_dir` 作为稳健起点；`thr_mult=0.8 confirm_only` 虽更强但更稀疏），
  - 做一次更大样本 / 更长时间窗的对照（保持同一基线 entry，不动 entry 逻辑）。
