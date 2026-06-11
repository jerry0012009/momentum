# 2026-03-19 14:52 UTC — Rank 93 first-major-break base-age clean replication keep-P1

## 本轮先做的 desk 检查（Run 1）
- 已先核对 repo 状态 / 最近 runs / 当前脏文件：
  - `git status --short` 仍显示大量与本轮无关的脏文件（本轮未清理、未混提）
  - 最近 optimization logs 最新到：
    - `2026-03-19_1429_rank93-base-age-intake.md`
    - `2026-03-19_1403_rank91-clean-replication-keep-p1.md`
    - `2026-03-19_1350_rank91-sweep-count-intake.md`
- 已再次实际执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：**`waiting_not_due`**（命令按预期以 code 2 退出）
  - 当前仍无 `due-now / overdue` lane
  - 最近 due 约为：`美股 5.1h`、`Crypto 9.1h`、`A股 16.1h`
- 结论：`Paper Seat = EMA / running paper / waiting_not_due` 仍成立；本轮不能伪造 refresh，也不该回头挤占 `P3 continuity`。

## 本轮主点 + 紧邻子点
- **主点**：`Run 3 / Rank 93 / first-major-break base-age gate` 唯一允许的最小 clean replication
- **紧邻子点**：把 hard verdict、active Scout 顺序、`Next 3 bot3 runs` 写回 `TRADING DESK BOARD`

## 先比较 active Scout 候选边际价值（3.5）
本轮按顶板与 `14:29 UTC` 版本重排当前允许动作：
1. `Rank 93 / first-major-break base-age gate`（仅剩 1 次最小 clean replication）
2. `Rank 92 / opening-drive adaptive offset continuation gate`
3. `Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool`
4. `P3 continuity`
5. `tiny-live plumbing`

当前把第 1 条排第一，因为：
- `Rank 93` 已在上一轮 guard-pass，按 `Next 3` 本轮唯一允许动作就是把这 1 次 clean replication 跑完；
- `EMA` 仍是 `waiting_not_due`，因此不能伪造 `Run 1`；
- `Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81` 都已落到 evidence_pool，不该越级插队。

## 本轮执行内容
### 1) 固定 clean replication 口径
- 新增并执行：`python3 scripts/build_rank93_first_major_break_base_age_clean_replication.py`
- 固定复用 `BTC/ETH/SOL 120d 15m` 本地 cache；
- 统一执行：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`；
- 对比四臂：
  - `baseline`
  - `strict_age_gate_24`
  - `strict_age_gate_36`
  - `hybrid36_size_down`
- `base-age` 口径冻结为：
  - `up_break_event = close > rolling_high_20.shift(1)`
  - `down_break_event = close < rolling_low_20.shift(1)`
  - `base_age = 距离上一次同方向 break 已过去的 bar 数`
  - 信号触发时只读取最近 `4` 根内最近一次同方向 break 的 `base_age`
- `hybrid36_size_down` 的读法冻结为：
  - long：只有 recent up-break 存在且 `base_age >= 36` 才放行；
  - short：若 recent down-break 不 fresh，则保留但只给 `0.5x`，不直接删单。

### 2) 结果（6bps/side 主判）
- `baseline`：`mean_total_return≈-28.85%`、`positive_asset_ratio=1/3`、`mean_trades≈292.3`、`trade_count_retention=100.00%`、`mean_position_size=1.00x`
- `strict_age_gate_24`：`mean_total_return≈-8.31%`、`positive_asset_ratio=1/3`、`mean_trades≈132.7`、`trade_count_retention≈45.47%`
- `strict_age_gate_36`：`mean_total_return≈-1.55%`、`positive_asset_ratio=1/3`、`mean_trades≈95.3`、`trade_count_retention≈32.70%`
- **`hybrid36_size_down`（主判）**：`mean_total_return≈-8.48%`、`positive_asset_ratio=1/3`、`mean_trades≈215.7`、`trade_count_retention≈73.83%`、`mean_position_size≈0.72x`

### 3) setup / asset / time pocket 细看
- setup（`hybrid36_size_down @ 6bps`）：
  - `ema_psar_long`：`14` 笔，`total_return≈+0.88%`，`trade_count_retention≈12.73%`，`positive_asset_ratio≈66.67%`
  - `fib_retest_long`：`30` 笔，`total_return≈+0.84%`，`trade_count_retention≈18.29%`
  - `breakout_short`：`603` 笔，`total_return≈-27.17%`，`trade_count_retention=100.00%`，但平均仓位已降到 `≈0.70x`
- asset：
  - `BTC≈-19.47%`
  - `ETH≈-11.36%`
  - `SOL≈+5.39%`
- time pockets：
  - `bucket_1≈-1.79%`
  - `bucket_2≈-4.47%`
  - `bucket_3≈-2.22%`
  - 没出现那种“只在最早窗口好看、后面全塌”的极端口袋，但也还没硬到能升 P2。

## Hard verdict
- **`Rank 93 = keep_P1 / mixed but honest`**

原因：
- 这层 `base-age` 不是没增量；无论看 `strict_age_gate_24/36` 还是 `hybrid36_size_down`，都明显比 baseline 更诚实；
- 但当前更像 **shared admission + size-down overlay**，而不是足以直接改写 desk judgement 的独立 candidate；
- `strict_age_gate_36` 虽把 desk 级亏损进一步收窄到接近打平，但 retention 只剩 `≈32.70%`，更像高阈值 admission tag；
- `hybrid36_size_down` 保留了更厚的交易数与 shared 使用价值，但 `positive_asset_ratio` 仍只有 `1/3`，且 `breakout_short` 仍是主要拖累；
- 因此它最诚实的位置是：**先留在 `P1 evidence_pool`，别继续追加 stability pack，也别偷升 `P2`。**

## 新增产物（deployable / reader-facing）
### artifact
- `reports/artifacts/scout_rank93_first_major_break_base_age_15m/overall_summary.csv`
- `reports/artifacts/scout_rank93_first_major_break_base_age_15m/setup_summary.csv`
- `reports/artifacts/scout_rank93_first_major_break_base_age_15m/asset_summary.csv`
- `reports/artifacts/scout_rank93_first_major_break_base_age_15m/time_bucket_summary.csv`
- `reports/artifacts/scout_rank93_first_major_break_base_age_15m/trades_primary_6bps.csv`
- `reports/artifacts/scout_rank93_first_major_break_base_age_15m/meta.csv`

### reader-facing 网页
- `reports/site/factors/scout_rank93_first_major_break_base_age_15m/report.html`
- `reports/site/reading/repo_scout/rank93_first_major_break_base_age_clean_replication.html`

## 对 desk board 的写回
已更新 `docs/TODO.md`：
- 新增 `14:52 UTC` 补充，冻结 `Rank 93 / first-major-break base-age clean replication -> keep_P1 / mixed but honest`；
- 当前 active Scout 顺序改写为：
  1. `Rank 92 / opening-drive adaptive offset continuation gate`
  2. `Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool`
  3. `P3 continuity`
  4. `tiny-live plumbing`
- `Next 3` 改写为：
  1. `Run 1 = EMA due-check only`
  2. `Run 2 = Rank 92 source intake + 两条轻量诚实守门`
  3. `Run 3 = 若 Rank 92 guard-pass，则给 1 次最小 clean replication；否则回退 Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool`

## 最小验证
- 已确认以下命令成功：
  - `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - `python3 scripts/build_rank93_first_major_break_base_age_clean_replication.py`
- 已确认以下文件存在并可读：
  - `reports/site/factors/scout_rank93_first_major_break_base_age_15m/report.html`
  - `reports/site/reading/repo_scout/rank93_first_major_break_base_age_clean_replication.html`
  - `reports/artifacts/scout_rank93_first_major_break_base_age_15m/overall_summary.csv`
  - `docs/TODO.md`

## 脏文件与提交
- 当前 repo 仍有大量与本轮无关的脏文件。
- 本轮未提交，避免混提。

## 下一轮建议
- 若 `EMA` 仍 `waiting_not_due`，不要空转；
- 直接切 `Rank 92 / opening-drive adaptive offset continuation gate` 的 source intake + 两条轻量诚实守门；
- `Rank 93` 现只保留在 `P1 evidence_pool`，不要继续追加 stability pack；
- `P3 continuity` 继续只保留在 fresh Scout 之后。
