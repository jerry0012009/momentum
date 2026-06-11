# 2026-03-19 09:37 UTC — Rank 84 clean replication（park）

## 本轮先核对的 desk 状态
- repo 工作区有大量与本轮无关的既有脏文件（tracked + untracked）；本轮不做混提提交。
- 已按 `Run 1` 实际执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 返回：`waiting_not_due`（无 `due-now / overdue`）
  - 最近 due：`美股 1d+1wk -> 2026-03-19 20:00 UTC`（其次 `Crypto 1d+1wk -> 2026-03-20 00:00 UTC`）
  - 结论：`Paper Seat = EMA / running paper / waiting_not_due`

## 本轮认领（仅 1 主点 + 1 紧邻子点）
- **主点：`Scout Seat / Run 2 / Rank 84` 最小 clean replication**
- 紧邻子点：把 `SignalPro penetration×ATR admission` 保持为 `Run 2` 下一候选（仅在 Rank 84 hard-fail 后接手）

## 先比较 active Scout 边际价值（3.5）
- 本轮比较：`Rank 84 > SignalPro penetration×ATR > breakout-candle compression reclaim`
- 决策原因：在“默认不再强调 breakout”的约束下，Rank 84 作为共享 admission layer（可跨 EMA/PSAR、Fib、breakout_short）优先级更高。

## 执行与冻结口径（clean replication）
- 脚本：`scripts/build_rank84_volume_price_interaction_clean_replication.py`
- 数据：固定复用 `BTC/ETH/SOL 120d 15m` 本地 cache
- 执行冻结：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`
- 对比四臂：
  - `baseline`
  - `single_volume_gate`
  - `interaction_admission`
  - `interaction_sizing`
- VPIS 冻结：
  - `VPIS = thrust(close-open vs ATR) + close_efficiency(price location × rvol_z) - absorption_penalty(wick × rvol_z)`
  - `single_volume_gate` 仅保留 `rvol_z > 0`
  - `interaction_admission` 用 trailing q60
  - `interaction_sizing` 用 q60~q80 分档 `half/full`

## 本轮 hard verdict
- **`Rank 84 / volume-price interaction admission layer = park / evidence_pool`**
- 原因（简述）：最小 clean replication 未证明 interaction 方案能稳定优于 baseline / single-volume；改善不足且带交易数收缩，当前应 park。

## 关键结果（6 bps/side 摘要）
- `baseline`: `mean_total_return≈-1.97%`，`mean_avg_net_ret≈-0.0647%`，`mean_flip_to_fail_3bars_rate≈43.53%`
- `interaction_admission`: `mean_total_return≈-1.40%`，`mean_avg_net_ret≈-0.0517%`，`retention≈93.55%`
- `interaction_sizing`: `mean_total_return≈-1.35%`，`mean_avg_net_ret≈-0.0453%`，`retention≈93.55%`，`mean_size≈0.966`

## 产物（deployable + reader-facing）
- artifact：
  - `reports/artifacts/scout_rank84_volume_price_interaction_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank84_volume_price_interaction_15m/by_setup_summary.csv`
  - `reports/artifacts/scout_rank84_volume_price_interaction_15m/asset_summary.csv`
  - `reports/artifacts/scout_rank84_volume_price_interaction_15m/meta.csv`
- reader-facing：
  - `reports/site/factors/scout_rank84_volume_price_interaction_15m/report.html`
  - `reports/site/reading/repo_scout/rank84_volume_price_interaction_clean_replication.html`
- 顶板：`docs/TODO.md` 已更新到 `2026-03-19 09:34 UTC`，`Next 3` 切换为：
  - `Run 1 = EMA due-check only`
  - `Run 2 = SignalPro penetration×ATR admission source intake`
  - `Run 3 = breakout-candle compression reclaim（后备）`

## 最小验证
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`（已执行，确认 waiting_not_due）
- `python3 scripts/build_rank84_volume_price_interaction_clean_replication.py`（已执行并落盘）
- 读回 `overall_summary.csv` / `by_setup_summary.csv` / `meta.csv`（已确认）

## 备注
- 本轮未追新 bar、未跑重型下载。
- `Scout Seat` 本轮已完成 clean replication + hard verdict；按预算纪律下一轮应切 fresh intake 候选，不继续磨 Rank 84。