# bot3 momentum auto-opt（13m）— 2026-03-22 01:46 UTC

> 本轮遵循 docs/TODO.md 顶部 TRADING DESK BOARD（authoritative）。

## Run 1 — EMA due-check first（Paper Seat）
结论：**无 due-now / overdue lane**，Paper Seat 处于 `waiting_not_due`。
- 执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --skip-build --require-due`
- guard 输出要点：
  - Crypto 1d+1wk（BTC/ETH/SOL）：约 23.6h 后到点（waiting_next_close）
  - 创业板ETF 1d：约 1.3d 后到点（waiting_next_close）
  - 贵州茅台 1d+1wk：约 1.3d 后到点（waiting_next_close）
- 动作：不做伪 refresh；按规则切到 Scout Seat。

## Run 2 — Rank139(P3) hosted narrow paper pilot 最小接线（状态复核）
TRADING DESK BOARD 写明该项已完成；本轮只做**健康检查**（不继续研究化磨损）。
- 产物存在且最近更新：
  - `reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/narrow_paper_pilot_monitoring_board.csv`（mtime: 01:07 UTC）
  - `.../narrow_paper_pilot_refresh_clock.json`（mtime: 01:07 UTC）
- 结论：lane 页面持续可更新，**未见“爆雷”迹象**（至少从 refresh clock 看是活的）。

## Run 3 — fresh intake（只认领 1 个候选）
### 认领候选（新）
- **候选名（暂定）**：`pbo-cscv deflated sharpe honesty gate`
- **类型**：作为 `backtest honesty / data-mining control` 的横向“守门层”，用于：
  1) 在 scout 阶段给 top candidates 的 Sharpe/回撤指标做“过拟合风险折扣”；
  2) 给后续 `promote_P3 -> hosted narrow paper pilot` 增加“可信度标签”，避免把纯运气样本抬上台。

### 本轮最小交付（只做 intake 卡，不开多个候选）
- 在日志中把候选定义清楚（是什么、解决什么问题、怎么落地到 momentum 的 scout 流水线）。

### 下一步（留给后续 1-2 轮）
1. **source intake**：锁定 1 篇权威参考（PBO / CSCV / deflated Sharpe 系列，优先 Bailey 等），整理 1 页“人话版”要点：
   - 什么时候需要它（多参数搜索/多策略筛选/多市场比较）；
   - 输入输出是什么（需要哪些序列/候选集）；
   - 它改变决策的方式（把哪些漂亮结果打回去）。
2. **minimal implementation**：做一个离线小工具（不改主 pipeline），对现有 Scout scorecard 输出加一列 `deflated_sharpe` 或 `pbo_risk_flag`。
3. **接线点**：优先挂到 `Scout Seat` 的“promote_P3 gate”上，而不是 paper/live 执行层。

---

## 本轮一句话
Paper Seat 无 due-now → 不空转，切 Scout Seat：Rank139 pilot 活跃；Run3 只认领 1 个新候选（PBO/CSCV/deflated Sharpe 守门层）并写清落地路径。
