# 2026-03-19 14:03 UTC — Rank 91 clean replication keep-P1

## 本轮先做的 desk 检查（Run 1）
- 已先核对 repo 状态 / 最近 runs / 当前脏文件：
  - `git status --short | wc -l = 1437`
  - 最近 optimization logs 最新到：
    - `2026-03-19_1350_rank91-sweep-count-intake.md`
    - `2026-03-19_1326_rank90-clean-replication-keep-p1.md`
    - `2026-03-19_1300_rank90-close-range-compression-intake.md`
- 已再次实际执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：**`waiting_not_due`**（命令按预期以 code 2 退出）
  - 当前仍无 `due-now / overdue` lane
  - 最近 due 约为：`美股 5.9h`、`Crypto 9.9h`、`A股 16.9h`
- 结论：`Paper Seat = EMA / running paper / waiting_not_due` 仍成立；本轮不能伪造 refresh，也不该回头挤占 `P3 continuity`。

## 本轮主点 + 紧邻子点
- **主点**：`Run 3 / Rank 91 / same-level consecutive sweep count level-memory gate` 唯一允许的最小 clean replication
- **紧邻子点**：把 hard verdict、active Scout 顺序、`Next 3 bot3 runs` 写回 `TRADING DESK BOARD`

## 先比较 active Scout 候选边际价值（3.5）
本轮按顶板与 `13:50 UTC` 版本重排当前允许动作：
1. `Rank 91 / same-level consecutive sweep count level-memory gate`（仅剩 1 次最小 clean replication）
2. `Rank 92 / opening-drive adaptive offset continuation gate`
3. `Rank 90 / Rank 82 / Rank 80 / Rank 81 evidence_pool`
4. `P3 continuity`
5. `tiny-live plumbing`

当前把第 1 条排第一，因为：
- `Rank 91` 已在上一轮 guard-pass，按 `Next 3` 本轮唯一允许动作就是把这 1 次 clean replication 跑完；
- `EMA` 仍是 `waiting_not_due`，因此不能伪造 `Run 1`；
- `Rank 90 / 82 / 80 / 81` 都已落到 evidence_pool，不该越级插队。

## 本轮执行内容
### 1) 固定 clean replication 口径
- 固定复用 `BTC/ETH/SOL 120d 15m` 本地 cache；
- 统一执行：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`；
- 比较四臂：
  - `baseline`
  - `single_sweep_gate`
  - `consec2plus_gate`
  - `consec2plus_plus_body_or_small_retest`
- sweep 定义冻结为：
  - `prior 20-bar high/low + volume >= 1.2x vol_ma20`
  - bull：`low < priorLow && close >= priorLow`
  - bear：`high > priorHigh && close <= priorHigh`
  - 若同侧事件在 `10` 根内且 level 距离不超过 `0.5% * close`，才累计为 `same-level consecutive sweep`

### 2) 结果（6bps/side 主判）
- `baseline`：`mean_total_return≈-28.85%`、`positive_asset_ratio=1/3`、`mean_trades≈292.3`、`trade_count_retention=100.00%`、`hold4≈45.61%`、`early_fail_4bars≈98.52%`
- `single_sweep_gate`：`mean_total_return≈-0.81%`、`positive_asset_ratio=1/3`、`mean_trades≈37.0`、`trade_count_retention≈12.68%`
- **`consec2plus_gate`（主判）**：`mean_total_return≈+0.56%`、`positive_asset_ratio≈66.67%`、`mean_trades≈6.7`、`trade_count_retention≈2.27%`、`hold4=50.00%`、`early_fail_4bars=100.00%`
- `consec2plus_plus_body_or_small_retest`：`mean_total_return≈-2.98%`、`positive_asset_ratio=0/3`、`mean_trades≈2.0`

### 3) setup / asset 细看
- setup：
  - `breakout_short`：`15` 笔，`total_return≈+3.82%`
  - `ema_psar_long`：`2` 笔，`total_return≈-0.32%`
  - `fib_retest_long`：`3` 笔，`total_return≈-1.83%`
- asset：
  - `SOL≈+3.33%`
  - `BTC≈+0.12%`
  - `ETH≈-1.78%`
- time pockets：`bucket_2≈-1.32% / positive_asset_ratio=0.00%`，说明这层 gate 也还没稳定到可以直接升格。

## Hard verdict
- **`Rank 91 = keep_P1 / mixed but honest`**

原因：
- 改善不是假的，`consec2plus_gate` 相对 baseline 确实把结果从明显负数拉回到接近平；
- 但改善几乎完全建立在 **极端缩样本** 上：`trade_count_retention≈2.27%`，还伴随 `early_fail_4bars=100.00%`；
- 效果主要集中在 `breakout_short`，没有形成对 `Fib / EMA-PSAR` 足够统一的 shared gate；
- 因此它现在更像 **很窄的 admission tag / evidence_pool 线索**，还不够 honest 到直接升 `P2`。

## 新增产物（deployable / reader-facing）
### artifact
- `reports/artifacts/scout_rank91_same_level_sweep_count_15m/overall_summary.csv`
- `reports/artifacts/scout_rank91_same_level_sweep_count_15m/asset_summary.csv`
- `reports/artifacts/scout_rank91_same_level_sweep_count_15m/setup_summary.csv`
- `reports/artifacts/scout_rank91_same_level_sweep_count_15m/time_bucket_summary.csv`
- `reports/artifacts/scout_rank91_same_level_sweep_count_15m/trades_primary_6bps.csv`
- `reports/artifacts/scout_rank91_same_level_sweep_count_15m/meta.csv`

### reader-facing 网页
- `reports/site/factors/scout_rank91_same_level_sweep_count_15m/report.html`
- `reports/site/reading/repo_scout/rank91_same_level_sweep_count_clean_replication.html`

## 对 desk board 的写回
已更新 `docs/TODO.md`：
- 新增 `14:03 UTC` 补充，冻结 `Rank 91 / same-level consecutive sweep count clean replication -> keep_P1 / mixed but honest`；
- 当前 active Scout 顺序改写为：
  1. `Rank 92 / opening-drive adaptive offset continuation gate`
  2. `Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool`
  3. `P3 continuity`
  4. `tiny-live plumbing`
- `Next 3` 改写为：
  1. `Run 1 = EMA due-check only`
  2. `Run 2 = Rank 92 source intake + 两条轻量诚实守门`
  3. `Run 3 = 若 Rank 92 guard-pass，则给 1 次最小 clean replication；否则回退 evidence_pool`

## 最小验证
- 已确认以下命令成功：
  - `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - `python3 scripts/build_rank91_same_level_sweep_clean_replication.py`
- 已确认以下文件存在并可读：
  - `reports/site/factors/scout_rank91_same_level_sweep_count_15m/report.html`
  - `reports/site/reading/repo_scout/rank91_same_level_sweep_count_clean_replication.html`
  - `reports/artifacts/scout_rank91_same_level_sweep_count_15m/overall_summary.csv`
  - `docs/TODO.md`

## 脏文件与提交
- 当前 repo 仍有大量与本轮无关的脏文件（`1437`）。
- 本轮未提交，避免混提。

## 下一轮建议
- 若 `EMA` 仍 `waiting_not_due`，不要空转；
- 直接切 `Rank 92 / opening-drive adaptive offset continuation gate` 的 source intake + 两条轻量诚实守门；
- `Rank 91` 现只保留在 `P1 evidence_pool`，不要继续追加 stability pack；
- `P3 continuity` 继续只保留在 fresh Scout 之后。
