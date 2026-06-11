# Rank 67 / regime-matrix shared-state gate minimal clean replication

## 轮次定位
- 时间：2026-03-18 21:30 UTC
- 席位：`Scout Seat`
- 本轮主点：`Run 3 / Rank 67 minimal clean replication`
- 紧邻子点：`queue-facing 更新（TODO 顶板）`

## 开始前检查
- `Run 1 / EMA due-check`：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍无 `due-now / overdue`；最早仍是 `Crypto 1d+1wk -> 2026-03-19 00:00 UTC / due_soon`。
- `P3 continuity`：`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` 最新一次仍是 `new_closed_trades_appended=0`，没有新的 status-changing event。
- 当前 active Scout 顺序：`Rank 67 / regime-matrix shared-state gate > Rank 68 / block-mitigation retest score > Rank 35b > Rank 16b > tiny-live plumbing`。
- git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件；本轮只新增 `Rank 67` 对应脚本、artifact、reader-facing 页面、TODO 顶板与本轮日志，不做混提。

## 本轮最小实验口径
- 数据：固定复用 `BTC/ETH/SOL 120d 15m` 本地 cache，不追新 bar、不做重型下载；`30m` regime label 直接从同一条 `15m` 数据 resample。
- base archetype：`ema_psar_long`、`fib_retest_long`、`breakout_short`。
- 四臂固定为：
  1. `base`
  2. `no_MR_gate`
  3. `trend_expansion_only`
  4. `compression_to_expansion_breakout`
- `30m` regime 只用最小 trailing 代理：`hurst_100`、`ADX14`、`ADX slope(5)`、`rv20`、`rv slope(5)`。
- 四态定义：
  - `Trend` = `hurst>=0.58 & ADX>=22 & adx_slope>0`
  - `Expansion` = `rv_slope>0.08 & adx_slope>0 & 非 Trend`
  - `Compression` = `rv_slope<-0.08 & ADX<=16`
  - 其余 = `Mean Reversion`
- 执行统一冻结到：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`。

## 本轮新增产物
1. 脚本：
   - `scripts/build_rank67_regime_matrix_clean_replication.py`
2. Artifact：
   - `reports/artifacts/scout_rank67_regime_matrix_shared_state_15m/signal_windows.csv`
   - `reports/artifacts/scout_rank67_regime_matrix_shared_state_15m/trade_log.csv`
   - `reports/artifacts/scout_rank67_regime_matrix_shared_state_15m/asset_summary.csv`
   - `reports/artifacts/scout_rank67_regime_matrix_shared_state_15m/overall_summary.csv`
   - `reports/artifacts/scout_rank67_regime_matrix_shared_state_15m/time_pockets.csv`
   - `reports/artifacts/scout_rank67_regime_matrix_shared_state_15m/setup_compare.csv`
   - `reports/artifacts/scout_rank67_regime_matrix_shared_state_15m/regime_summary_30m.csv`
3. Reader-facing 页面：
   - `reports/site/factors/scout_rank67_regime_matrix_shared_state_15m/report.html`
   - `reports/site/reading/repo_scout/rank67_regime_matrix_clean_replication.html`
4. Queue-facing 更新：
   - `docs/TODO.md` 顶部 `Next 3 bot3 runs` 已补 `2026-03-18 21:30 UTC` 最新块。

## 关键结果（6bps / side）
- `ema_psar_long`：
  - `base≈-3.79%`
  - `no_MR≈-1.47%`
  - `trend+exp≈-1.26%`
  - `comp→exp≈-`（本轮没有形成可比样本）
- `fib_retest_long`：
  - `base≈1.20%`
  - `no_MR≈2.04%`
  - `trend+exp≈2.04%`
  - `comp→exp≈-`
- `breakout_short`：
  - `base≈-3.54%`
  - `no_MR≈-1.04%`
  - `trend+exp≈-0.49%`
  - `comp→exp≈-`

## Hard verdict
**`Rank 67 / regime-matrix shared-state gate = park / evidence pool`**

## 为什么是这个 verdict
- `no_MR` / `trend+exp` 的确让 `ema_psar_long` 与 `breakout_short` 少亏，也让 `fib_retest_long` 更赚钱，但改善主要来自**大幅砍样本**：
  - `ema_psar_long` retention 只剩约 `16.2%~21.0%`
  - `fib_retest_long` retention 只剩约 `15.2%`
  - `breakout_short` retention 只剩约 `17.0%~26.1%`
- `fib_retest_long` 是唯一干净改善的 setup，但这还不足以把它包装成三条主线共用的 shared state language。
- `breakout_short` 在 `trend+exp` 下虽然少亏，但 `false-break / false-hold 4bars rate` 反而从 `61.70%` 升到 `72.22%`，说明它没有稳定改善 continuation 质量。
- `compression_to_expansion_breakout` 本轮没有形成可比样本，至少在这套最小公开代理口径里，没证明自己是可用的 breakout 专属 arm。
- 因此更诚实的读法是：**保留为 evidence pool，但不升格；主资源切到 Rank 68。**

## 对交易台顺序的影响
- `Rank 67` 已消耗完当前允许的 `1 次 minimal clean replication` 预算，不应继续在 fast-lane 队首反复打磨。
- 当前更诚实的 active Scout 顺序更新为：
  - `Rank 68 / block-mitigation retest score`
  - `Rank 35b`
  - `Rank 16b`
  - `tiny-live plumbing`
- 更新后的 `Next 3`：
  - `Run 1 = EMA due-check only`
  - `Run 2 = 若 Rank 67 未能升到下一层，则立刻切到 Rank 68 / block-mitigation retest score 做 source intake + 两条轻量诚实守门`
  - `Run 3 = 若 Rank 68 已 guard-passed 且 EMA 仍 waiting_not_due，则立刻给它 1 次最小 clean replication；若 Rank 68 直接 hard-fail / 未 admitted，则继续按 7.10 先认领新的 5m / 15m crypto source；只有 fresh source 这一层也 exhausted 时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing`

## 最小验证
- 成功执行：`python3 scripts/build_rank67_regime_matrix_clean_replication.py`
- 结果：脚本完成并输出 `verdict=park / evidence pool`
- 备注：运行中仅出现 pandas `FutureWarning(observed=False)`，不影响本轮 artifact 与 verdict。

## 提交
- 未提交（工作区有大量与本轮无关的脏文件，避免混提）。
