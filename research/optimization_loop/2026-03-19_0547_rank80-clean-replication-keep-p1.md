# 2026-03-19 05:47 UTC — Rank 80 first-30m impulse quality clean replication → keep P1

## 本轮先核对的 desk 状态
- repo 工作区存在大量与本轮无关的脏文件；本轮未做 commit，也未混提无关改动。
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`
  - 全 desk 仍无 `due-now / overdue`
  - 最近 due 点仍是 `A股三条 lane -> 2026-03-19 07:00 UTC`
  - 结论：`Paper Seat = EMA / running paper / waiting_not_due`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-19T05:36:12Z`
  - `new_closed_trades_appended=0`
  - 结论：当前没有新的 `P3 continuity` status-changing event 需要抢占主资源

## 本轮只认领的主点
- **主点：`Scout Seat / Rank 80 / first-30m impulse quality shared gate` 的唯一那手最小 clean replication**
- 未额外打开其他候选；严格按顶板只做 `Run 2`

## 为什么这轮仍是 Rank 80
- 顶板最新 `Next 3` 已明确：当 `EMA = waiting_not_due` 时，本轮合法动作就是把 `Rank 80` 从 `guard-passed` 推到 `keep_P1 / promote_to_P2 / park` 三选一。
- 相比直接切去 `RS+/RS- asymmetry gate` 或 `ETF lead regime gate`，这一步边际价值更高，因为它先回答：**开段冲击质量这道 shared continuation gate，到底能不能在 desk 级样本里便宜诚实地改善 continuation failure。**

## 本轮执行冻结
- 资产：`BTC/ETH/SOL`
- 周期：`15m` base setup + `5m` open30 features
- 样本：本地 `120d` cache
  - `reports/artifacts/scout_tau_band_breakout_15m/cache/*__120d__15m.csv`
  - `reports/artifacts/scout_rank66_exec_tf_switch_alignment_15m/spot_cache/*_120d_5m.csv`
- 执行：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`
- setup：`ema_psar_long / fib_retest_long / breakout_short`
- session anchor：`00/08/16 UTC`
- open30 特征：session 起始后前 `6` 根 `5m`
  - `r_open30`
  - `vol_z_open30`（相对过去 `30` 个 session）
  - `rv_open30 > trailing q60`
- 比较三臂：
  - `baseline`
  - `impulse_veto`
  - `impulse_halfsize`

## 6bps/side 关键结果
### desk 级 overall
- `baseline`
  - `mean_total_return ≈ -2.00%`
  - `mean_expectancy ≈ -0.065%`
  - `early_fail ≈ 27.25%`
- `impulse_halfsize`
  - `mean_total_return ≈ -1.09%`
  - `mean_expectancy ≈ -0.039%`
  - `mean_avg_size ≈ 0.55x`
  - `early_fail ≈ 27.25%`
- `impulse_veto`
  - `mean_total_return ≈ -0.24%`
  - `mean_expectancy ≈ +0.012%`
  - 但 `mean_trade_count_retention ≈ 14.01%`
  - 且 `early_fail ≈ 31.55%`

### 分 setup 读法（6bps/side）
- `breakout_short`
  - `impulse_veto` 最干净：`mean_total_return ≈ +0.54%`，`positive_asset_ratio = 2/3`
  - 但 retention 只有 `≈15.14%`
- `ema_psar_long`
  - `impulse_halfsize` 只是把亏损收窄（`-3.66% -> -2.29%`），没把它救正
  - `impulse_veto` 反而更差
- `fib_retest_long`
  - baseline 本来就最好（`+1.21%`）
  - `impulse_veto / halfsize` 都在稀释这条 lane

## hard verdict
- **`Rank 80 / first-30m impulse quality shared gate = keep_P1 / evidence_pool`**

### 为什么不是 promote_to_P2
- `halfsize` 版确实比 baseline 更诚实：
  - 总亏损收窄
  - expectancy 改善
  - 严格 `veto` 的极端砍单问题也被避免
- 但它没有形成足够统一的 desk 级改善：
  - `early_fail` 并没有真正下降
  - 主要价值集中在 `breakout_short`
  - `fib_retest_long` 被明显稀释
- 更直白地说：**它现在更像“某些 continuation pocket 可用的 shared sizing hint”，还不够像能升到 `paper candidate pool` 的通用 desk gate。**

### 为什么也不是 park
- `strict veto` 虽然太狠，但至少说明开段冲击质量不是完全没信息
- `halfsize` 版相对 baseline 仍有边际改善，因此这条线更诚实的位置不是直接判死刑，而是保留在 `P1 evidence pool`

## 产物
- script:
  - `scripts/build_rank80_first30m_impulse_clean_replication.py`
- artifacts:
  - `reports/artifacts/scout_rank80_first30m_impulse_quality_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank80_first30m_impulse_quality_15m/by_setup_summary.csv`
  - `reports/artifacts/scout_rank80_first30m_impulse_quality_15m/per_asset_setup_summary.csv`
  - `reports/artifacts/scout_rank80_first30m_impulse_quality_15m/session_open30_features.csv`
  - `reports/artifacts/scout_rank80_first30m_impulse_quality_15m/trade_samples.csv`
- reader-facing:
  - `reports/site/factors/scout_rank80_first30m_impulse_quality_15m/report.html`
  - `reports/site/reading/repo_scout/rank80_first30m_impulse_quality_clean_replication.html`
- 顶板已更新：
  - `docs/TODO.md` 中 `Next 3 bot3 runs`

## 对顶板的更新结论
- `Run 1 = EMA due-check only`
- `Run 2 = RS+/RS- asymmetry gate source intake（若 EMA 仍 waiting_not_due）`
- `Run 3 = ETF lead regime gate > Fib trend-strength admission layer > 其他 fresh source`
- `P3 continuity` 继续只算低频 sidecar，不得默认抢占 Scout 主资源

## 最小验证
- 脚本成功运行：`python3 scripts/build_rank80_first30m_impulse_clean_replication.py`
- 读回 `overall_summary.csv / by_setup_summary.csv / docs/TODO.md`，确认 verdict 与顶板更新一致

## 备注
- 本轮没有追新 bar、没有重拉远端数据，只复用本地 `15m + 5m` cache。
- TODO 之外仍有大量与本轮无关的历史脏文件；本轮未整理、未提交。