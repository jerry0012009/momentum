# bot3 momentum auto（13m）— 2026-03-22 13:06 UTC — pbo-cscv-honesty-gate-mini-report

> 约束：严格按 `docs/TODO.md` 顶部 TRADING DESK BOARD 的 **Next 3 bot3 runs**（Run1→Run2→Run3）。本轮最多：1 个主点 + 1 个紧邻子点；不同时打开多个 Scout 候选。

## Run 1 — EMA due-check first（Paper Seat）

- 执行：`python3 jerry/momentum/scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：**waiting_not_due**（无 `due-now / overdue` lane）
  - Crypto 1d+1wk（BTC/ETH/SOL）：约 **10.9h** 后到点
  - 创业板ETF 1d：约 **17.9h** 后到点
  - 贵州茅台 1d+1wk：约 **17.9h** 后到点

结论：不做伪 refresh；按规则立即切到下一允许动作。

## Run 2 — Hosted P3 continuity（低频、事件驱动）

按 desk 口径：仅做“是否有 status-changing event”判定。

- 观察：`reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/narrow_paper_pilot_refresh_clock.json`
- 最新 `generated_at_utc = 2026-03-22 11:16 UTC`（距当前约 1h50m）

结论：未见 `refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch` 等状态变化信号；**本轮跳过 Run2**（不做近义健康检查重复劳动）。

## Run 3 — Scout Seat（本轮主交付）

主点：`pbo-cscv / deflated sharpe honesty gate` 的“可外显落点”。

### 动作：补 1 个最小可见落点（site 页面）

新增一个极简说明页，把离线 scorecard + canonical 来源汇总到站点树下，方便随时从网页侧查看。

- 新增页面：
  - `reports/site/factors/pbo_cscv_honesty_gate/report.html`
- 该页链接到现有 artifacts：
  - `reports/artifacts/pbo_cscv_honesty_gate/rank139_pbo_cscv_dsr_scorecard.csv`
  - `reports/artifacts/pbo_cscv_honesty_gate/rank139_pbo_cscv_dsr_meta.json`
  - `reports/artifacts/pbo_cscv_honesty_gate/source_intake_card.csv`

### 页面里的关键读数（取自 scorecard）
- PBO（CSCV）：`0.1714` → **guard_passed**
- baseline：mean_net@6bps ≈ `-0.1549%`，dsr_probability ≈ `0.0036`
- confirm_same_dir_only：mean_net@6bps ≈ `+0.5370%`，sharpe ≈ `0.365`，dsr_probability ≈ `0.881`
- veto_opp_dir：mean_net@6bps ≈ `+0.3428%`，sharpe ≈ `0.268`，dsr_probability ≈ `0.839`

结论：在不扩 scope 的前提下，本轮把 `pbo-cscv` 从“日志/脚本/CSV”补到了一个更容易被 Jerry 直接看到的网页落点；后续若要继续推进，优先考虑把该页纳入站点索引/入口导航（但不在本轮扩展）。
