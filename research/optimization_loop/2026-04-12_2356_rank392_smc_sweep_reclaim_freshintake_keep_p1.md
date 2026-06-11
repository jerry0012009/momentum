# Bot3 执行日志 — Rank 392 fresh intake first verdict（smc sweep reclaim）

- 时间：2026-04-12 23:56 UTC
- 对象：`research/quant_digests/2026-04-12_2304_smc-sweep-reclaim-alpha.md`
- 执行动作：按 cycle_plan #1 完成 fresh intake first verdict（no-overlap + 成本快检 + 最小 honesty 子检查）
- 结论：`keep_P1`
- 新分配 Rank：`392`

## 最小证据（直接影响分层）

数据来源：
- `/root/clawd/jerry/momentum/reports/artifacts/literature/smc_sweep_reclaim_probe_trades_2026-04-12.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/smc_sweep_reclaim_probe_costladder_2026-04-12.csv`

### 1) no-overlap + 15m 费前快检
- `variant=sweep_reclaim, interval=15m` 合计 `369` 笔
- gross 平均：`+5.7571 bps/trade`（约 `+5.76bps`）

### 2) 最小 honesty 子检查（本小点内允许的单次子检查）
- `had_sweep` 全量为真（`100%`）
- `confluence` 最小值 `4`（符合 digest 中的 desk 化收窄规则）
- 按 `(interval,symbol)` 检查 `entry_time < prev_exit_time` 的重叠违规：`0`

### 3) round-trip 成本口径
- 按 15m 聚合 gross `+5.76bps/trade` 折算：
  - `5bps` round-trip：约 `+0.76bps/trade`（微正）
  - `8bps` round-trip：约 `-2.24bps/trade`（转负）

## 分层判定

- fresh intake first verdict：`keep_P1`
- decisive blocker（唯一）：`edge_after_cost` 脆弱（成本从低档抬升即失效）
- 运行槽位动作：
  - 该对象进入 `Surviving candidate slot`
  - `followup_budget_remaining=1`
  - 后续唯一 follow-up 应聚焦是否可通过 execution veto / asset routing 抬升费后鲁棒性

## 一句话结果（用于 state.result）

`Rank 392` first verdict=`keep_P1`：`15m` no-overlap 下 gross `+5.76bps/trade` 且最小 honesty 核验通过，但费后仅在低成本档微正、`8bps` 转负，唯一 blocker=`edge_after_cost` 脆弱。
