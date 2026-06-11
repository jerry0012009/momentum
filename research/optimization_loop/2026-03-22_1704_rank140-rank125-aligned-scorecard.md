# Bot3 Optimization Loop — Rank 140 接入 1 条 fresh scout family（Rank 125 aligned returns matrix → canonical scorecard）

- 时间：2026-03-22 17:04 UTC
- 严格顺序：Run1 → Run2 → Run3
- 范围控制：本轮仅 **1 个主点（Rank 140）** + **1 个紧邻子点（选定 family=Rank 125，且只接这一条）**。

## 1) Run 1 = EMA due-check first
执行：
```bash
python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due
```
结果：`waiting_not_due`（exit code 2，符合守门预期）
- Crypto 1d+1wk：约 6.9h 后到点
- 创业板ETF 1d：约 13.9h 后到点
- 贵州茅台 1d+1wk：约 13.9h 后到点

结论：本轮不得空转，立刻切下一允许动作。

## 2) Run 2 = Hosted P3 continuity（低频、事件驱动）
检查：
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`
  - `run_at_utc = 2026-03-22T16:57:37Z`
  - `new_closed_trades_appended = 0`

结论：未见 status-changing event（无 refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch），按顶板规则跳过近义健康检查。

## 3) Run 3 = Scout Seat（Rank 140）
### 主点：把 canonical scorecard 接到 1 条 fresh scout family 的 aligned returns matrix（本轮只接 Rank 125）
本轮选定 family：`Rank 125 / range location veto gate`（已有 `trade_log.csv` 且包含 baseline vs gate 两臂）。

### 紧邻子点（仅 1 个）：构造 single-family aligned returns matrix
目的：把 Rank 125 的 baseline / rl_gate 两臂对齐到同一套 `signal_ts` 上，生成可供 Rank 140 canonical scorecard 复用的输入表。

执行（一次性脚本在本轮命令里生成）：
- 输入：`reports/artifacts/scout_rank125_range_location_veto_15m/trade_log.csv`
- 输出：`reports/artifacts/pbo_cscv_honesty_gate/rank125_aligned_returns_matrix.csv`

对齐口径（人话）：
- 以 `baseline` 的 trade 作为 universe（共 824 笔）；
- 如果同一 `(asset, setup, signal_ts)` 下存在 `rl_gate` trade，则视为 `gate-kept`；否则视为 `gate-veto`；
- 将 `event_0.8` 复用为二分类事件：
  - `same_dir_first` = gate-kept（对应 script 的 `confirm_same_dir_only` 可用样本）
  - `opp_dir_first` = gate-veto

> 注：这是为了把“是否通过 gate”映射到 Rank 140 当前离线实现里三臂（baseline / veto / confirm）的最小接线方式；它不是在声称 Rank 125 的语义就是 CUSUM 事件方向。

### 跑 canonical-ish CSCV/PBO + DSR scorecard
执行：
```bash
python3 scripts/build_pbo_cscv_dsr_scorecard.py \
  --trade-log reports/artifacts/pbo_cscv_honesty_gate/rank125_aligned_returns_matrix.csv \
  --event-col event_0.8 \
  --out-dir reports/artifacts/pbo_cscv_honesty_gate/rank125_single_family_scorecard \
  --label "Rank140 canonical scorecard on Rank125 single-family aligned matrix" \
  --segments 8
```
产物：
- `reports/artifacts/pbo_cscv_honesty_gate/rank125_single_family_scorecard/rank139_pbo_cscv_dsr_scorecard.csv`
- `reports/artifacts/pbo_cscv_honesty_gate/rank125_single_family_scorecard/rank139_pbo_cscv_dsr_meta.json`

## 4) 结果（只读这一条 family）
### hard read
- `PBO = 0.5714` → `verdict = guard_failed`
- `lambda_median = 0.5`

### 三臂（net 已扣 12bps roundtrip）
- baseline：`mean_net_6bps ≈ -0.0626%`，`sharpe ≈ -0.0458`
- veto_opp_dir（≈ gate-kept 子集）：`mean_net_6bps ≈ -0.0132%`，`sharpe ≈ -0.0102`
- confirm_same_dir_only：与 veto_opp_dir 相同（因为本轮 event 映射是二分类，属于最小接线）

### 人话解释
- 这轮交付的重点是 **“接线”**：证明 Rank 140 的 canonical scorecard 可以被喂入一条全新的 family（本轮=Rank 125）并产出可审计的 CSCV/PBO/DSR 表。
- 结果显示：在这个 family 上，用目前这套最小 event 映射跑出来的 **PBO 很高（>0.5）**，意味着“IS 选赢家后，OOS 排名经常掉到下半区”，按 Rank 140 的守门口径应视为 **honesty guard failed**。
- 这不等价于“Rank 125 本身完全没价值”，更像是在提醒：
  1) 这个 family 的 gate-kept 子集在不同时间段的稳定性可能不够；或
  2) 当前把 gate-kept/veto 映射到 event 三臂的方式太粗，需要后续更严格的 aligned returns matrix 定义（例如把每个 arm 都显式写出完整 return 序列，而不是用 event 让脚本隐式生成）。

## 5) 本轮 hard verdict / next
- 本轮 hard verdict：`Rank 140 接线成功，但 Rank 125 单 family scorecard = guard_failed（PBO=0.571）`。
- 下一轮若继续 Rank 140（仍一次只接 1 条 family）：
  - 更推荐做的紧邻子点是：把 aligned returns matrix 升级成 **显式三臂 returns**（baseline / gate-kept / gate-veto 三列），再跑 PBO/CSCV/DSR（避免把 arm 语义塞进 event 字段）。
