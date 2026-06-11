# 2026-03-19 13:26 UTC — Rank 90 close-range compression clean replication -> keep_P1

## 本轮先做的 desk 检查（Run 1）
- 已先核对 repo 状态 / 最近 runs / 当前脏文件：
  - `git status --short | wc -l` 仍在高位（本轮未清理，避免混提）
  - 最近 optimization logs 最新到：
    - `2026-03-19_1300_rank90-close-range-compression-intake.md`
    - `2026-03-19_1252_rank89-clean-replication-park.md`
    - `2026-03-19_1219_rank89-outside-inside-intake.md`
- 已再次实际执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：**`waiting_not_due`**
  - 当前仍无 `due-now / overdue` lane
  - 最近 due 约为：`美股 6.6h`、`Crypto 10.6h`、`A股 17.6h`
- 结论：`Paper Seat = EMA / running paper / waiting_not_due` 仍成立；本轮合法主动作必须落在 `Scout Seat / Rank 90 minimal clean replication`。

## 本轮主点 + 紧邻子点
- **主点**：`Run 3 / Rank 90 / close-range compression asymmetry minimal clean replication`
- **紧邻子点**：根据 replication 结果，直接回答 `promote_to_P2 / keep_P1 / park`，并把 `Next 3` 切回 `fresh source intake`，避免继续围着旧 P1/P3 续命

## 先比较 active Scout 候选边际价值（3.5）
本轮按顶板顺序执行，当前允许动作只有：
1. `Rank 90 / close-range compression asymmetry`
2. `Rank 82 / Rank 80 / Rank 81 evidence_pool`
3. `P3 continuity`
4. `tiny-live plumbing`

由于 `Rank 90` 已在上轮完成 intake + 两条轻量诚实守门，本轮必须先把它唯一允许的那次最小 clean replication 跑完，不能跳过直接回到 `Rank 82 / 80 / 81`，也不能挤占 `P3 continuity`。

## 本轮执行内容
### 1) 最小 clean replication 口径
- 新增脚本：`scripts/build_rank90_close_range_compression_clean_replication.py`
- 固定样本与执行冻结：
  - `BTC/ETH/SOL 120d 15m` 本地 cache
  - `signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`
- base setups 固定为：
  - `ema_psar_long`
  - `fib_retest_long`
  - `breakout_short`
- 只比较三臂：
  - `baseline`
  - `long_admission_only`
  - `short_veto_or_halfsize`

### 2) compression gate 的最小实现
- 压缩定义：前 `13` 根 close 压在 `1.0%` 窄区间内，全部 `shift(1)`；
- `up-break`：当前 close 高于前窗最高价；`down-break`：当前 close 低于前窗最低价；
- `long_admission_only`：long setup 只有在最近 `4` 根内出现过 `compression up-break` 才放行；short 侧保持 baseline；
- `short_veto_or_halfsize`：在 long admission 基础上，若 short setup 最近 `4` 根内出现过 `compression down-break`，则只给 `0.5x`，否则维持 `1.0x`。

## Hard verdict
- **`Rank 90 = keep_P1 / mixed but honest`**

### 为什么不是 promote_to_P2
#### overall（6 bps / side）
- `baseline`
  - `mean_total_return ≈ -28.85%`
  - `positive_asset_ratio = 1/3`
  - `mean_trades ≈ 292.3`
  - `trade_count_retention ≈ 86.96%`
  - `4bar early-fail ≈ 77.57%`
- `long_admission_only`
  - `mean_total_return ≈ -17.27%`
  - `positive_asset_ratio = 1/3`
  - `mean_trades ≈ 212.3`
  - `trade_count_retention ≈ 32.09%`
  - `4bar early-fail ≈ 77.57%`
- `short_veto_or_halfsize`
  - `mean_total_return ≈ -10.94%`
  - `positive_asset_ratio = 1/3`
  - `mean_trades ≈ 212.3`
  - `trade_count_retention ≈ 32.09%`
  - `mean_position_size_mult ≈ 91.29%`
  - `4bar early-fail ≈ 77.57%`

### 更诚实的读法
- 它**不是完全没增量**：short 侧半仓确实让总亏损明显收窄，long admission 也把两条 long setup 拉回接近打平；
- 但它也**还不够硬**：
  - `positive_asset_ratio` 仍只有 `1/3`；
  - `trade_count_retention` 已压到约 `32.09%`；
  - `4bar early-fail` 几乎没改善，说明它没真正显著减少“入场后立刻走坏”的问题；
  - 当前改善更像 `admission 更苛刻 + short 侧少做/少亏`，不足以诚实升到 `P2 / paper candidate pool`。

### setup 级读法
- `breakout_short`
  - `baseline @6bps ≈ -15.99%`
  - `short_veto_or_halfsize @6bps ≈ -9.67%`
  - retention 仍约 `74.63%`，改善主要来自 `down-break` 情景半仓，而不是把假延续真正过滤干净
- `ema_psar_long`
  - `baseline @6bps ≈ -5.26%`
  - `long_admission_only @6bps ≈ -0.65%`
  - 但 retention 只剩约 `7.83%`
- `fib_retest_long`
  - `baseline @6bps ≈ -7.60%`
  - `long_admission_only @6bps ≈ -0.63%`
  - retention 只剩约 `13.81%`

结论：这条线有“保留为 P1 证据池”的价值，但还不够共享、也不够稳，当前默认不该继续占 `Scout Seat` 主资源位。

## 新增产物（deployable / reader-facing）
### artifact
- `reports/artifacts/scout_rank90_close_range_compression_15m/overall_summary.csv`
- `reports/artifacts/scout_rank90_close_range_compression_15m/setup_summary.csv`
- `reports/artifacts/scout_rank90_close_range_compression_15m/asset_summary.csv`
- `reports/artifacts/scout_rank90_close_range_compression_15m/trade_samples.csv`
- `reports/artifacts/scout_rank90_close_range_compression_15m/meta.csv`

### reader-facing 网页
- `reports/site/factors/scout_rank90_close_range_compression_15m/report.html`
- `reports/site/reading/repo_scout/rank90_close_range_compression_clean_replication.html`

## 对 desk board 的写回
已更新 `docs/TODO.md`：
- 新增 `13:24 UTC` 补充，冻结 `Rank 90 = keep_P1 / mixed but honest`；
- 当前 active Scout 顺序改写为：
  1. `Rank 91 / same-level consecutive sweep count level-memory gate`
  2. `Rank 92 / opening-drive adaptive offset continuation gate`
  3. `Rank 90 / Rank 82 / Rank 80 / Rank 81 evidence_pool`
  4. `P3 continuity`
  5. `tiny-live plumbing`
- `Next 3` 改写为：
  1. `Run 1 = EMA due-check only`
  2. `Run 2 = Rank 91 / same-level consecutive sweep count level-memory gate source intake + 两条轻量诚实守门`
  3. `Run 3 = 若 Rank 91 guard-pass 且 EMA 仍 waiting_not_due，则立刻给它 1 次最小 clean replication；若 Rank 91 在 intake / guard 阶段直接 hard-fail，则切 Rank 92 / opening-drive adaptive offset continuation gate source intake；只有 fresh source 这一层也 exhausted，才允许回退到 Rank 90 / Rank 82 / Rank 80 / Rank 81 evidence_pool > P3 continuity > tiny-live plumbing`

## 最小验证
- 已确认以下文件存在并可读：
  - `reports/artifacts/scout_rank90_close_range_compression_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank90_close_range_compression_15m/setup_summary.csv`
  - `reports/artifacts/scout_rank90_close_range_compression_15m/meta.csv`
  - `reports/site/reading/repo_scout/rank90_close_range_compression_clean_replication.html`
- 已确认 `docs/TODO.md` 顶板写回成功。

## 脏文件与提交
- 当前 repo 仍有大量与本轮无关的脏文件。
- 本轮未提交，避免混提。

## 下一轮建议
- 若 `EMA` 仍 `waiting_not_due`，不要继续磨 `Rank 90` 的近义说明；
- 直接切 `Rank 91 / same-level consecutive sweep count level-memory gate` 的 source intake + 两条轻量诚实守门；
- 若 `Rank 91` 直接 hard-fail，再切 `Rank 92 / opening-drive adaptive offset continuation gate`；
- 仍不要让 `P3 continuity` 或 `tiny-live plumbing` 插队。
