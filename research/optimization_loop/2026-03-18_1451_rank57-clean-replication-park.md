# 2026-03-18 14:51 UTC — Rank 57 minimal clean replication -> park

## 本轮执行定位（按 TRADING DESK BOARD）
- 先执行 `Run 1 / EMA due-check only`。
- 当前 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍显示全 desk 没有新的 `due-now / overdue` lane：
  - `美股 1d+1wk -> 2026-03-18 20:00 UTC`
  - `Crypto 1d+1wk -> 2026-03-19 00:00 UTC`
  - `A股三条 lane -> 2026-03-19 07:00 UTC`
- 同时复核 `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`，当前仍是 `new_closed_trades_appended=0`，说明没有新的 `P3 status-changing event` 值得把 bot3 拉回 continuity。
- 因此这轮不能把 `waiting_not_due` 误读成整桌等待；合法主动作仍是 **`Run 2 / Rank 57 minimal clean replication`**。

## Repo / workspace state
- `git status --short` 显示 repo 内存在大量与本轮无关的既有脏文件与未跟踪产物；本轮只增量新增/触碰：
  - `scripts/build_rank57_ttm_squeeze_clean_replication.py`
  - `docs/TODO.md`
  - `reports/artifacts/scout_rank57_ttm_squeeze_release_regime_gate_15m/*`
  - `reports/site/factors/scout_rank57_ttm_squeeze_release_regime_gate_15m/report.html`
  - `reports/site/reading/repo_scout/rank57_ttm_squeeze_release_regime_gate_clean_replication.html`
  - 本日志文件
- 因存在大量无关脏文件，本轮不做 commit，避免混提。

## 主点
完成 `Rank 57 / TTM squeeze release regime gate` 的唯一那手 **最小 clean replication**：
- 脚本：`python3 scripts/build_rank57_ttm_squeeze_clean_replication.py`
- 固定样本：`BTC/ETH/SOL 120d 15m` cache
- base archetype：`ema_psar_long`、`fib_retest_long`、`breakout_short`
- 固定四臂：
  - `base`
  - `no_sqz_on_veto`
  - `release_recent_gate`
  - `release_recent_gate_momentum_sign`
- 执行冻结：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`

## 紧邻子点
在同一轮顺手补了 2 个轻量稳定性切片，并完成 authoritative writeback：
1. `time stability`：把 trade log 按时间三分桶，检查结果是不是只来自偶然 pocket；
2. `parameter stability`：把 `release_recent` 窗口从 `1~4 bars` 做最小邻域扫描，并对比是否叠 `momentum_sign`；
3. 把 hard verdict 与新的 `Next 3` 排班写回 `docs/TODO.md`；
4. 生成 reader-facing 页面：
   - `reports/site/factors/scout_rank57_ttm_squeeze_release_regime_gate_15m/report.html`
   - `reports/site/reading/repo_scout/rank57_ttm_squeeze_release_regime_gate_clean_replication.html`

## 关键结果（6bps/side）
### setup-level
- `ema_psar_long`：`base≈-3.68%` / `veto≈-6.66%` / `release≈-2.94%` / `release+mom≈-2.77%`
- `fib_retest_long`：`base≈+1.17%` / `veto≈+1.70%` / `release≈+0.30%` / `release+mom≈+0.09%`
- `breakout_short`：`base≈-3.55%` / `veto≈-3.61%` / `release≈-0.10%` / `release+mom≈-0.10%`

### 诚实读法
- `breakout_short` 上，`release_recent_gate` 确实把均值亏损从约 `-3.55%` 压到接近 `-0.10%`，但代价是 `trade_count_retention≈25.22%`，仍明显偏薄。
- `fib_retest_long` 的 base 本来就略正；`release` 反而没有改善，说明这条 overlay 没有跨 setup 形成统一增益。
- `ema_psar_long` 虽然 `release` / `release+mom` 比 base 少亏一点，但 `retention` 只剩约 `13.33% / 11.43%`，同样更像极端减样本，而不是稳定 shared gate。

## Light Stability Pack（本轮完成 2 项）
### 1) 时间稳定性
- 已输出：`reports/artifacts/scout_rank57_ttm_squeeze_release_regime_gate_15m/time_pocket_summary.csv`
- 读法：当前结果没有显示出足够干净、跨 setup 统一的时间稳定 pocket；更多是个别 slice 少亏，而不是连续稳定通过。

### 2) 参数稳定性（release 1~4 bars）
- 已输出：`reports/artifacts/scout_rank57_ttm_squeeze_release_regime_gate_15m/parameter_stability_summary.csv`
- 读法：
  - `breakout_short` 在 `release 1~4 bars` 下都只是接近打平/少亏；
  - `fib_retest_long` 在 `release 1~4 bars` 下都只有轻微正值，但平均 trades 仅约 `1.67`；
  - `ema_psar_long` 在整个 `1~4 bars` 邻域里都仍是负值。
- 这说明参数稳定性并没有给出“稍微改窗口仍能站住”的强证据。

## Hard verdict
- **`Rank 57 / TTM squeeze release regime gate = park / evidence pool`**
- 更直白地说：这条线不是完全没信息量，但当前改善主要来自**大幅砍样本后的少亏**，还没有跨 setup / 跨资产形成足够统一、可升格的 shared regime gate，不该继续占默认 Scout 主资源位。

## 对排班的影响
- 当前最新 `Next 3` 应重置为：
  - `Run 1 = EMA due-check only`
  - `Run 2 = 按 7.10 再认领 1 条 fresh paper/repo source（优先 5m / 15m crypto）`
  - `Run 3 = 只有 fresh pool 也 exhausted 时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing`
- `Rank 57` 后续若要重开，只能以 `park / evidence pool` 身份被重新 framing，而不是继续默认占 clean-replication queue。

## 最小验证
- 成功执行：`python3 scripts/build_rank57_ttm_squeeze_clean_replication.py`
- 已确认输出存在：
  - `reports/artifacts/scout_rank57_ttm_squeeze_release_regime_gate_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank57_ttm_squeeze_release_regime_gate_15m/setup_compare.csv`
  - `reports/artifacts/scout_rank57_ttm_squeeze_release_regime_gate_15m/parameter_stability_summary.csv`
  - `reports/site/factors/scout_rank57_ttm_squeeze_release_regime_gate_15m/report.html`
  - `reports/site/reading/repo_scout/rank57_ttm_squeeze_release_regime_gate_clean_replication.html`

## Reader-facing 落点
- `reports/site/factors/scout_rank57_ttm_squeeze_release_regime_gate_15m/report.html`
- `reports/site/reading/repo_scout/rank57_ttm_squeeze_release_regime_gate_clean_replication.html`

## 风险备注
- 当前工作区有大量与本轮无关的脏文件，本轮未提交。
- 本轮只用现有历史缓存推进 verdict，没有追最新 bar，也没有重跑不必要的重型下载。 
