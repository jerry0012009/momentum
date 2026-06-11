# 2026-03-18 17:22 UTC — Rank 60 clean replication 后压回 park

## 为什么这轮轮到它
- 先按 `TRADING DESK BOARD` 执行 `Run 1`：重新核对 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`，当前仍无新的 `due-now / overdue` lane。
- `Paper Seat / EMA` 继续是 **`running paper / waiting_not_due`**，不能把整桌误判成等待态。
- 顶板最新 `Next 3` 已明确这轮应执行 **`Run 2 / Rank 60 minimal clean replication`**；`Rank 60` 是当前唯一还在 `guard-passed / admit_to_clean_replication_queue` 的 active Scout 候选。

## 开轮检查（repo / 最近 runs / 脏文件 / 当前席位）
- repo 状态：工作区存在大量与本轮无关的既有脏文件与未跟踪产物，本轮不做混提 commit。
- 最近 optimization runs：
  - `2026-03-18_1656_rank60-source-intake.md`
  - `2026-03-18_1640_rank59-time-stability-park.md`
  - `2026-03-18_1557_rank59-clean-replication.md`
- 当前席位：
  - `Paper Seat = EMA`：`running paper / waiting_not_due`
  - `Live Seat`：暂空
  - `Scout Seat`：本轮主资源位 = `Rank 60` minimal clean replication
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` 最新仍为 `new_closed_trades_appended=0`，没有新的 `P3 status-changing event` 值得抢占主资源。

## 本轮主点
完成 **`Rank 60 / FVG-BOS imbalance retest gate`** 的唯一那手最小 clean replication，并直接给出 hard verdict。

## 做了什么改动
### 运行脚本
- 新增并执行：`python3 scripts/build_rank60_fvg_bos_imbalance_clean_replication.py`

### 新增 / 刷新 artifact
- `reports/artifacts/scout_rank60_fvg_bos_imbalance_retest_15m/signal_windows.csv`
- `reports/artifacts/scout_rank60_fvg_bos_imbalance_retest_15m/trade_log.csv`
- `reports/artifacts/scout_rank60_fvg_bos_imbalance_retest_15m/asset_summary.csv`
- `reports/artifacts/scout_rank60_fvg_bos_imbalance_retest_15m/overall_summary.csv`
- `reports/artifacts/scout_rank60_fvg_bos_imbalance_retest_15m/time_pockets.csv`
- `reports/artifacts/scout_rank60_fvg_bos_imbalance_retest_15m/setup_compare.csv`

### reader-facing 落点
- `reports/site/factors/scout_rank60_fvg_bos_imbalance_retest_15m/report.html`
- `reports/site/reading/repo_scout/rank60_fvg_bos_imbalance_retest_clean_replication.html`

### authoritative writeback
- 更新了 `docs/TODO.md` 顶部 `Next 3 bot3 runs`，把 `Rank 60` 的 clean replication 结果冻结为 `park / evidence pool`，并把下一手默认主资源位切到 fresh Scout intake：`Rank 61 > continuation fail-fast overlay > pullback-quality / CQI`。

## 这次 replication 的冻结口径
- 只复用 `BTC/ETH/SOL 120d 15m` 本地 cache，不追新 bar。
- 只比较三条最小 archetype：`ema_psar_long`、`fib_retest_long`、`breakout_short`。
- 四臂固定为：`base`、`bos_only`、`bos_fvg_retest`、`bos_vi_retest`。
- 所有执行统一冻结到 `signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`。
- `recent BOS` 只看最近 `8` 根内 confirmed swing 穿越；`FVG` 用三根 K gap；`VI` 用一根错位 gap；不偷渡 liquidity sweep / HTF bias / premium-discount 叙事。

## 结果与证据
### 1) setup-level 结果
- `ema_psar_long`：`base≈-3.68%` → `BOS≈-5.46%`、`BOS+FVG≈-0.11%`、`BOS+VI≈0.00%`
- `fib_retest_long`：`base≈+1.17%` → `BOS≈-0.10%`、`BOS+FVG≈+0.28%`、`BOS+VI≈0.00%`
- `breakout_short`：`base≈-3.55%` → `BOS≈-3.55%`、`BOS+FVG≈-3.25%`、`BOS+VI≈0.00%`

### 2) 当前更诚实的读法
- `bos_only` 并没有给出跨 setup 的稳定增量：`ema_psar_long` 反而更差，`fib_retest_long` 也被明显伤到，`breakout_short` 几乎没变化。
- `bos_fvg_retest` 在 `ema_psar_long / fib_retest_long` 上看起来有一点少亏味道，但样本保留太薄：
  - `ema_psar_long mean_trade_count_retention≈6.67%`
  - `fib_retest_long mean_trade_count_retention≈9.09%`
  - 同时 `winner_truncation` 很高（分别约 `91.3%` / `83.8%`），说明它更像极端砍样本，而不是稳定提升。
- `bos_vi_retest` 在三条 archetype 上几乎没有形成可用样本，当前只能算零信息，不是增量证据。
- `breakout_short` 上 FVG 只带来很轻微的少亏（`-3.55% -> -3.25%`），但正资产占比仍是 `0`，不足以改变整条线的 hard verdict。

### 3) 当前硬结论
- **`Rank 60 / FVG-BOS imbalance retest gate = park / evidence pool`**。
- 更直白地说：本轮更像在证明 **真正起作用的不是 FVG / VI retest 本身，而是它们偶尔把样本切得很薄**；没有足够证据说明这层 zone 语义能在 recent BOS 之上提供稳定、可迁移的 shared continuation gate 增量。

## 最小验证
- 脚本 stdout：
  - `verdict=park / evidence pool`
  - `ema_psar_long: base≈-3.68% / BOS≈-5.46% / BOS+FVG≈-0.11% / BOS+VI≈0.00%`
  - `fib_retest_long: base≈1.17% / BOS≈-0.10% / BOS+FVG≈0.28% / BOS+VI≈0.00%`
  - `breakout_short: base≈-3.55% / BOS≈-3.55% / BOS+FVG≈-3.25% / BOS+VI≈0.00%`
- 已确认 `docs/TODO.md` 顶板完成最小写回。
- 已确认 reader-facing 页面存在：
  - `reports/site/factors/scout_rank60_fvg_bos_imbalance_retest_15m/report.html`
  - `reports/site/reading/repo_scout/rank60_fvg_bos_imbalance_retest_clean_replication.html`

## 下一步建议
- 按当前 `Next 3`，下一手默认应切到 **fresh Scout intake**：`Rank 61 > continuation fail-fast overlay > pullback-quality / CQI`。
- 不该继续围着 `Rank 60` 打转；若后续再认领它，必须是一个真正会改变 verdict 的最小检查，而不是继续补 intake / wording。

## Commit hash
- 未提交。
- 原因：工作区有大量与本轮无关的既有脏文件和未跟踪产物，当前不适合做安全 selective commit。
