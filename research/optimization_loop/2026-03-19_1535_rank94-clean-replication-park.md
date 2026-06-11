# 2026-03-19 15:35 UTC — Rank 94 two-bar outside-range follow-through clean replication park

## 本轮先做的 desk 检查（Run 1）
- 已先核对 repo 状态 / 最近 runs / 当前脏文件：
  - `git status --short | wc -l = 1469`
  - 最近 optimization logs 最新到：
    - `2026-03-19_1512_rank94-two-bar-outside-range-intake.md`
    - `2026-03-19_1452_rank93-clean-replication-keep-p1.md`
    - `2026-03-19_1429_rank93-base-age-intake.md`
- 已再次实际执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：**`waiting_not_due`**（命令按预期不做 full rebuild）
  - 当前仍无 `due-now / overdue` lane
  - 最近 due 约为：`美股 4.4h`、`Crypto 8.4h`、`A股 15.4h`
- `manual_narrow_paper_last_run_summary.json` 仍未出现新的 `P3 status-changing event`
- 结论：`Paper Seat = EMA / running paper / waiting_not_due` 仍成立；本轮不能伪造 refresh，也不该回头挤占 `P3 continuity`。

## 本轮主点 + 紧邻子点
- **主点**：`Run 3 / Rank 94 / two-bar outside-range follow-through gate` 唯一允许的最小 clean replication
- **紧邻子点**：把 hard verdict、active Scout 顺序、`Next 3 bot3 runs` 写回 `TRADING DESK BOARD`

## 先比较 active Scout 候选边际价值（3.5）
本轮按顶板 `15:12 UTC` 版本继续执行当前允许动作：
1. `Rank 94 / two-bar outside-range follow-through gate`（仅剩 1 次最小 clean replication）
2. `Rank 92 / opening-drive adaptive offset continuation gate`
3. `Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool`
4. `P3 continuity`
5. `tiny-live plumbing`

当前把第 1 条排第一，因为：
- `Rank 94` 已在上一轮 guard-pass，按 `Next 3` 本轮唯一允许动作就是把这 1 次 clean replication 跑完；
- `EMA` 仍是 `waiting_not_due`，不能伪造 `Run 1`；
- `Rank 93 / 90 / 91 / 82 / 80 / 81` 都已落到 evidence_pool，不该越级插队。

## 本轮执行内容
### 1) 固定 clean replication 口径
- 新增并执行：`python3 scripts/build_rank94_two_bar_outside_followthrough_clean_replication.py`
- 固定复用 `BTC/ETH/SOL 120d 15m` 本地 cache；
- 统一执行：`signal 当根及之前数据 + follow-through 等待 2 根 bar + next eligible bar open + no-overlap + hold 8 bars`；
- 对比四臂：
  - `baseline`
  - `ft_gate`
  - `sft_lite_gate`
  - `baseline_half_ft_full`
- `parent_range` 固定为 signal 前两根 bar 的 `high/low`；
- `FT` 定义冻结为：信号后连续两根 close 都仍站在 parent range 外；
- `SFT-lite` 定义冻结为：在 `FT` 基础上，再要求两根同向实体推进，且至少一根 `range >= 1.5 * avg_range_10`；
- `baseline_half_ft_full` 的读法冻结为：若 `FT` 通过则 `1.0x`，否则只保留 `0.5x`，用于测试“path persistence size-up”是否比一刀 veto 更诚实。

### 2) 结果（6bps/side 主判）
- `baseline`：`mean_total_return≈-13.00%`、`positive_asset_ratio≈33.33%`、`mean_trades≈284.3`、`trade_count_retention≈100.00%`
- `ft_gate`：`mean_total_return≈-14.03%`、`positive_asset_ratio≈33.33%`、`mean_trades≈198.0`、`trade_count_retention≈69.65%`
- `sft_lite_gate`：`mean_total_return≈3.40%`、`positive_asset_ratio≈100.00%`、`mean_trades≈33.7`、`trade_count_retention≈11.87%`
- **`baseline_half_ft_full`（主判）**：`mean_total_return≈-13.55%`、`positive_asset_ratio≈33.33%`、`mean_trades≈284.3`、`trade_count_retention≈100.00%`、`mean_position_size≈82.82%`

### 3) setup / asset / time pocket 细看
- setup（`baseline_half_ft_full @ 6bps`）：
  - `breakout_short`：`581` 笔，`total_return≈-23.06%`，`trade_count_retention≈100.00%`，`positive_asset_ratio≈33.33%`
  - `ema_psar_long`：`110` 笔，`total_return≈-11.46%`，`trade_count_retention≈100.00%`，`positive_asset_ratio≈33.33%`
  - `fib_retest_long`：`162` 笔，`total_return≈-6.14%`，`trade_count_retention≈100.00%`，`positive_asset_ratio≈66.67%`
- asset：
  - `BTC≈-12.33%`
  - `ETH≈-29.97%`
  - `SOL≈1.65%`
- time pockets：
  - `bucket_1≈-5.60%`
  - `bucket_2≈-6.99%`
  - `bucket_3≈-0.96%`

- 读法：`sft_lite_gate` 确实有一个很窄的小样本正口袋，但 retention 只有 `≈11.87%`；`ft_gate` 与 `baseline_half_ft_full` 都没把 desk 级读法推到更诚实的位置。

## Hard verdict
- **`Rank 94 = park / evidence_pool`**

原因：
- 两根区间外延续确认这条线并没有在 desk 级别诚实减 gate；`ft_gate` 在 6bps 下比 delayed baseline 还差；
- `baseline_half_ft_full` 只是把仓位均值压到 `≈82.82%`，但跨资产仍只有 `1/3` 为正；
- `sft_lite_gate` 虽然转正，但 retention 仅 `≈11.87%`，明显更像局部 pocket，而不是共享 continuation gate；
- setup 与 asset 侧也没有出现足够硬的 admission 改写，因此最诚实的位置就是直接压回 evidence_pool，而不是继续追加 stability pack。

## 新增产物（deployable / reader-facing）
### artifact
- `reports/artifacts/scout_rank94_two_bar_outside_followthrough_15m/overall_summary.csv`
- `reports/artifacts/scout_rank94_two_bar_outside_followthrough_15m/setup_summary.csv`
- `reports/artifacts/scout_rank94_two_bar_outside_followthrough_15m/asset_summary.csv`
- `reports/artifacts/scout_rank94_two_bar_outside_followthrough_15m/time_bucket_summary.csv`
- `reports/artifacts/scout_rank94_two_bar_outside_followthrough_15m/trades_primary_6bps.csv`
- `reports/artifacts/scout_rank94_two_bar_outside_followthrough_15m/meta.csv`

### reader-facing 网页
- `reports/site/factors/scout_rank94_two_bar_outside_followthrough_15m/report.html`
- `reports/site/reading/repo_scout/rank94_two_bar_outside_followthrough_clean_replication.html`

## 对 desk board 的写回
已更新 `docs/TODO.md`：
- 新增 `15:33 UTC` 补充，冻结 `Rank 94 / two-bar outside-range follow-through clean replication -> park / evidence_pool`；
- 当前 active Scout 顺序改写为：
  1. `Rank 92 / opening-drive adaptive offset continuation gate`
  2. `Rank 93 / Rank 94 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool`
  3. `P3 continuity`
  4. `tiny-live plumbing`
- `Next 3` 改写为：
  1. `Run 1 = EMA due-check only`
  2. `Run 2 = Rank 92 source intake + 两条轻量诚实守门`
  3. `Run 3 = 若 Rank 92 guard-pass，则给 1 次最小 clean replication；否则回退 Rank 93 / Rank 94 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool`

## 最小验证
- 已确认以下命令成功：
  - `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - `python3 scripts/build_rank94_two_bar_outside_followthrough_clean_replication.py`
- 已确认以下文件存在并可读：
  - `reports/site/factors/scout_rank94_two_bar_outside_followthrough_15m/report.html`
  - `reports/site/reading/repo_scout/rank94_two_bar_outside_followthrough_clean_replication.html`
  - `reports/artifacts/scout_rank94_two_bar_outside_followthrough_15m/overall_summary.csv`
  - `docs/TODO.md`

## 脏文件与提交
- 当前 repo 仍有大量与本轮无关的脏文件。
- 本轮未提交，避免混提。

## 下一轮建议
- 若 `EMA` 仍 `waiting_not_due`，不要空转；
- 直接切 `Rank 92 / opening-drive adaptive offset continuation gate` 的 source intake + 两条轻量诚实守门；
- `Rank 94` 现已压回 `park / evidence_pool`，不要继续追加 stability pack；
- `P3 continuity` 继续只保留在 fresh Scout 之后。
