# Rank 130 / cross-market leader impulse nonlinear gate intake

## 为什么这次选这个
- 先按 desk 规则执行了 `Run 1 / EMA due-check first`：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due` 再次如实返回 `EMA = waiting_not_due`，当前没有新的 `due-now / overdue` lane；最近 due 仍是 `Crypto 1d+1wk`，约 `2.6` 小时后到点。
- 同时核对 `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-20T21:23:16Z`，结果仍为 `new_closed_trades_appended=0`，说明 hosted `P3` continuity 这轮也没有新的 status-changing event 可以插队。
- 因而按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 的最新 `Next 3`，本轮合法主动作只能是：**`Run 2 / Rank 130 / cross-market leader impulse nonlinear gate` 的 source intake + 两条轻量诚实守门**。
- 重新比较 active Scout 的边际价值后，这条线仍高于回头继续磨 `Rank 127 / 125 / 112 / 111`：旧 `P1` 已是 `budget used / evidence_pool`，而 `Rank 130` 是一个 concrete、paper-based、5m/15m crypto 直接可测、且能同时服务 `breakout-short / Fib retest / EMA-PSAR` 三条主线的 shared follow-up 候选。

## 做了什么改动
1. 新建 queue-facing artifact：
   - `reports/artifacts/literature/scout_rank130_crossmarket_leader_impulse_source_intake_card.csv`
2. 新建 reader-facing 页面：
   - `reports/site/reading/repo_scout/rank130_crossmarket_leader_impulse_source_intake.html`
3. 最小更新 `docs/TODO.md` 顶部 desk board：
   - 追加 `2026-03-20 21:23 UTC` 的最新补充；
   - 把 `Rank 130` 从 `fresh paper source intake next` 前推到 **`P1 / guard-passed / minimal clean replication next`**；
   - 把 `Next 3` 改写为：`Run 1 = EMA due-check first` -> `Run 2 = Rank 130 1 次最小 clean replication` -> `Run 3 = 若 Rank 130 exhausted，则回 fresh intake reserve`。

## 验证 / 证据
### 1) Paper Seat 仍 waiting_not_due
实际执行：
```bash
python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due
```
关键信号：
- `EMA = waiting_not_due`
- 无 `due-now / overdue lane`
- 最近 due：`Crypto 1d+1wk -> due_soon / 约 2.6 小时后到点`

### 2) P3 continuity 这轮没有插队理由
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`
- `run_at_utc = 2026-03-20T21:23:16Z`
- `new_closed_trades_appended = 0`

### 3) Rank 130 两条轻量诚实守门
当前最诚实的 `trade on / trade off`：
- **trade on**：它只配当三条 baseline（`breakout-short / Fib retest / EMA-PSAR`）共用的 **shared follow-up gate**。当 `signal` 当根之前的跨市场 leader impulse 落在 `low-z` 区时，允许 continuation / 正常 follow-up。
- **trade off**：它不是独立 alpha，不是新主触发器，也不是“leader 越强越该追”。当 leader impulse 冲到 `high-z` 极端时，更诚实的读法是 `veto / size-down / no-chase`。
- **honesty gate**：通过。`leader z-score` 只能来自 `signal 当根及之前、已完成 bar` 的 ETH/SOL→BTC 跨市场序列；阈值只能在训练段或滚动过去窗口冻结；下一轮 clean replication 必须统一到 `next-bar open + no-overlap`，禁止 future return、全样本分位、或事后最优阈值倒灌。

## 当前硬结论
**`Rank 130 / cross-market leader impulse nonlinear gate = guard-passed / admit_to_clean_replication_queue`**。

翻成人话：
这条线值得拿 **1 次最小 clean replication** 预算，因为它回答的是“跨市场 leader 冲击到底该放行，还是该追尾回避”，而不是再发明一条新神因子。

## 风险 / 边界
- 这轮只做了 `source intake + honesty gate`，还**没有**做 clean replication，更没有完成 `Light Stability Pack`。
- 这条线当前只能当 shared follow-up gate，不得被误读成新 alpha 或新 `Live Seat` 竞争者。
- `Xu et al. (2024)` 仍是 working paper；本地 quickcheck 只能当 intake 证据，不是正式 replication。

## 下一步建议
- 若下一轮 `EMA` 仍 `waiting_not_due`，则严格只给 `Rank 130` **1 次最小 clean replication**：
  - 对照：`baseline / low_z_only / high_z_veto`
  - 数据：`BTC/ETH/SOL 120d~180d 15m` 本地缓存
  - 统一口径：`signal 当根及之前数据 + next-bar open + no-overlap`
  - 主看：`post_cost_return / false_follow_ratio / trade_count_retention`
- 若这 1 次 clean replication 不能形成 honest uplift，就直接 `park`，不要继续磨 admission wording。

## Commit hash
- 未提交。
- 原因：当前 repo 工作区存在大量与本轮无关的脏文件（顶板也已明确 `git status --short | wc -l` 很高），这轮不适合做安全 selective commit。
