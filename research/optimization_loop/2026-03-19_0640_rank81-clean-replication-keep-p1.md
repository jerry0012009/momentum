# 2026-03-19 06:40 UTC — Rank 81 RS+/RS- asymmetry clean replication → keep P1

## 本轮先核对的 desk 状态
- repo 工作区存在大量与本轮无关的脏文件；本轮未做 commit，也未混提无关改动。
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`
  - 全 desk 仍无 `due-now / overdue`
  - 最近 due 点仍是 `A股三条 lane -> 2026-03-19 07:00 UTC`
  - 结论：`Paper Seat = EMA / running paper / waiting_not_due`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`
  - 最新仍无新的 `P3 status-changing event`
  - 结论：当前不得回头挤占 `P3 continuity`

## 本轮只认领的主点
- **主点：`Scout Seat / Rank 81 / RS+/RS- realized-semivariance asymmetry gate` 的唯一那手最小 clean replication**
- 未额外打开 ETF / Fib 或其他 fresh source；严格按顶板只做 `Run 2`

## 为什么本轮仍是 Rank 81
- 顶板最新 `Next 3` 已明确：在 `EMA = waiting_not_due` 时，本轮合法动作就是把 `Rank 81` 从 `guard-passed` 推到 `promote_to_P2 / keep_P1 / park` 三选一。
- 相比直接切去 ETF lead regime gate 或 Fib trend-strength admission layer，这一步边际价值更高，因为它先回答：**把 `RS+ / RS-` 非对称做成 shared directional veto / sizing gate，到底能不能在当前 desk 级样本里便宜诚实地改善方向错配。**

## 本轮执行冻结
- 资产：`BTC/ETH/SOL`
- 周期：`15m` base setup + `5m` realized-semivariance features
- 样本：本地 `120d` cache
  - `reports/artifacts/scout_tau_band_breakout_15m/cache/*__120d__15m.csv`
  - `reports/artifacts/scout_rank66_exec_tf_switch_alignment_15m/spot_cache/*_120d_5m.csv`
- 执行：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`
- setup：`ema_psar_long / fib_retest_long / breakout_short`
- RS 特征：
  - 只使用信号当根及之前最近 `12` 根 `5m` 收益
  - `RS+ = Σ max(r,0)^2`
  - `RS- = Σ max(-r,0)^2`
  - `A = (RS+ - RS-) / (RS+ + RS-)`
  - 阈值统一走 `15m` 级 trailing quantile（`A` 的 `q20`，`RS+ / RS-` 的 `q80`）
- 比较三臂：
  - `baseline`
  - `rs_veto`
  - `rs_halfsize`

## 6bps/side 关键结果
### desk 级 overall
- `baseline`
  - `mean_total_return ≈ -2.00%`
  - `mean_expectancy ≈ -0.065%`
  - `early_fail ≈ 27.25%`
- `rs_halfsize`
  - `mean_total_return ≈ -1.69%`
  - `mean_expectancy ≈ -0.073%`
  - `retention ≈ 89.32%`
  - `avg_size ≈ 0.98x`
  - `early_fail ≈ 26.92%`
- `rs_veto`
  - `mean_total_return ≈ -1.30%`
  - `mean_expectancy ≈ -0.057%`
  - `retention ≈ 84.80%`
  - `early_fail ≈ 26.18%`

### 分 setup 读法（6bps/side）
- `ema_psar_long`
  - `rs_veto` 最干净：`mean_total_return ≈ -0.09%`，`expectancy ≈ +0.002%`
  - `rs_halfsize` 也明显优于 baseline（`-3.66% -> -1.24%`）
- `fib_retest_long`
  - baseline 仍是最好（`+1.21%`）
  - `rs_veto / rs_halfsize` 都在稀释这条 lane
- `breakout_short`
  - 当前 `RS+/RS-` gate 基本没起到过滤作用
  - `rs_veto` 与 `rs_halfsize` 几乎等同于 baseline 的同向全保留，但结果更差

## hard verdict
- **`Rank 81 / RS+/RS- realized-semivariance asymmetry gate = keep_P1 / evidence_pool`**

### 为什么不是 promote_to_P2
- 这条线并非没信息：
  - `ema_psar_long` 上确实改善明显
  - strict veto 的 desk 级 total / expectancy / early-fail 也都比 baseline 稍好
- 但它没有形成足够统一的 desk 级改善：
  - `halfsize` 并未改善 expectancy
  - `fib_retest_long` 被稀释
  - `breakout_short` 这条最需要方向 veto 的线当前没有被修好
- 更直白地说：**它现在更像“对 EMA-PSAR long pocket 有帮助的 shared veto 线索”，还不够像能升到 `paper candidate pool` 的统一 desk gate。**

### 为什么也不是 park
- `ema_psar_long` 上的改善不是幻觉，说明 `RS+ / RS-` 非对称至少抓到了一部分方向尾部信息。
- 当前更诚实的位置不是直接判死刑，而是保留在 `P1 evidence pool`，让主资源回到新的 fresh source。

## 产物
- script:
  - `scripts/build_rank81_rs_semivariance_asymmetry_clean_replication.py`
- artifacts:
  - `reports/artifacts/scout_rank81_rs_semivariance_asymmetry_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank81_rs_semivariance_asymmetry_15m/by_setup_summary.csv`
  - `reports/artifacts/scout_rank81_rs_semivariance_asymmetry_15m/per_asset_setup_summary.csv`
  - `reports/artifacts/scout_rank81_rs_semivariance_asymmetry_15m/rs_feature_snapshot.csv`
  - `reports/artifacts/scout_rank81_rs_semivariance_asymmetry_15m/trade_samples.csv`
- reader-facing:
  - `reports/site/factors/scout_rank81_rs_semivariance_asymmetry_15m/report.html`
  - `reports/site/reading/repo_scout/rank81_rs_semivariance_asymmetry_clean_replication.html`
- 顶板已更新：
  - `docs/TODO.md` 中 seat 分级与 `Next 3 bot3 runs`

## 对顶板的更新结论
- `Run 1 = EMA due-check only`
- `Run 2 = ETF lead regime gate > Fib trend-strength admission layer > 其他 fresh source`
- `Run 3 = 只有 fresh source 这一层也 exhausted 时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing`
- `P3 continuity` 继续只算低频 sidecar，不得默认抢占 Scout 主资源

## 最小验证
- 脚本成功运行：`python3 scripts/build_rank81_rs_semivariance_asymmetry_clean_replication.py`
- 读回 `overall_summary.csv / by_setup_summary.csv / docs/TODO.md`，确认 verdict 与顶板更新一致
- reader-facing 页面与 factor report 已落盘

## 备注
- 本轮没有追新 bar、没有重拉远端数据，只复用本地 `15m + 5m` cache。
- TODO 之外仍有大量与本轮无关的历史脏文件；本轮未整理、未提交。
