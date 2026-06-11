# Bot3 Optimization Loop — Rank 140 接入 1 条 fresh scout family（Rank 112 aligned returns matrix → canonical scorecard）

- 时间：2026-03-22 18:05 UTC
- 严格顺序：Run1 → Run2 → Run3
- 范围控制：本轮仅 **1 个主点（Rank 140）** + **1 个紧邻子点（选定 family=Rank 112；只接这一条）**。

## 1) Run 1 = EMA due-check first
执行：
```bash
cd jerry/momentum
python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due
```
结果：`waiting_not_due`（require-due 拒绝伪 refresh；exit code 2 合规）
- Crypto 1d+1wk（BTC/ETH/SOL）：约 6.0h 后到点
- 创业板ETF 1d：约 13.0h 后到点
- 贵州茅台 1d+1wk：约 13.0h 后到点

结论：Paper Seat 本轮无合法刷新动作，立即切下一允许动作（不得空转）。

## 2) Run 2 = Hosted P3 continuity（低频、事件驱动）
仅做事件判定（不做近义健康巡检）：
- `jerry/momentum/reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`
  - `run_at_utc = 2026-03-22T17:24:30Z`
  - `new_closed_trades_appended = 0`

结论：无 status-changing event（refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch），按顶板规则跳过。

## 3) Run 3 = Scout Seat（Rank 140 / pbo-cscv deflated sharpe honesty gate）
### 主点：把 canonical scorecard 接到 1 条 fresh scout family 的 aligned returns matrix（本轮只接 Rank 112）
本轮选定 family：`Rank 112 / basis dislocation short veto`。
- 输入：`jerry/momentum/reports/artifacts/scout_rank112_basis_dislocation_short_veto_15m/trade_log.csv`
- baseline universe：`variant=baseline`（122 笔）
- strict 子臂：`variant=basis_extreme_plus_oi_veto`（120 笔）

### 紧邻子点（仅 1 个）：构造 single-family aligned returns matrix
输出：
- `jerry/momentum/reports/artifacts/pbo_cscv_honesty_gate/rank112_aligned_returns_matrix.csv`
- `jerry/momentum/reports/artifacts/pbo_cscv_honesty_gate/rank112_aligned_returns_matrix.meta.json`

对齐口径（与上一轮 Rank125 接线一致，最小可审计接线）：
- 以 baseline 的 trade 作为 universe；
- 若同一 `(asset, signal_ts)` 下存在 strict 变体 trade，则 `event_0.8 = same_dir_first`（视为 gate-kept）；否则 `opp_dir_first`（视为 gate-veto）；
- `gross_ret` 使用 baseline 的 `gross_return`（这一点很“粗”，但目的是先证明 Rank140 canonical scorecard 能吃进 fresh family 输入并跑通产物链）。

对齐结果分布：
- gate-kept（same_dir_first）：120
- gate-veto（opp_dir_first）：2

> 备注：这个分布非常极端，意味着这条 family 上的“gate”几乎不砍样本；因此用它来测试 PBO/CSCV 的排名稳定性，会天然更容易出现“不稳定/噪声主导”的表现（因为 arms 的差异很弱）。

### 跑 canonical-ish CSCV/PBO + DSR scorecard
执行：
```bash
cd jerry/momentum
python3 scripts/build_pbo_cscv_dsr_scorecard.py \
  --trade-log reports/artifacts/pbo_cscv_honesty_gate/rank112_aligned_returns_matrix.csv \
  --event-col event_0.8 \
  --out-dir reports/artifacts/pbo_cscv_honesty_gate/rank112_single_family_scorecard \
  --label "Rank140 canonical scorecard on Rank112 single-family aligned matrix" \
  --segments 8
```
产物：
- `jerry/momentum/reports/artifacts/pbo_cscv_honesty_gate/rank112_single_family_scorecard/rank139_pbo_cscv_dsr_scorecard.csv`
- `jerry/momentum/reports/artifacts/pbo_cscv_honesty_gate/rank112_single_family_scorecard/rank139_pbo_cscv_dsr_meta.json`

## 4) 结果（只读这一条 family）
### hard read
- `PBO = 1.0` → `verdict = guard_failed`
- `lambda_median = 0.5`

### 三臂（net 已扣 12bps roundtrip）
- baseline：`mean_net_6bps ≈ -0.165%`，`sharpe ≈ -0.175`
- veto_opp_dir（≈ gate-kept 子集）：`mean_net_6bps ≈ -0.196%`，`sharpe ≈ -0.212`
- confirm_same_dir_only：与 veto_opp_dir 相同（本轮 event 映射是二分类）

### 人话解释
- 本轮交付重点仍是“接线”而不是给 Rank 112 下最终生死判决：
  - Rank 140 的 canonical scorecard（CSCV/PBO/DSR 离线近似）可以被喂入一个完全不同的 fresh family（Rank 112）并输出可审计 CSV+meta。
- 但由于本轮对齐事件的分布 **120:2** 极端不平衡，Rank 112 这条 family 对“arm 选择/比较”的信息量很弱；因此 scorecard 读到 `PBO=1.0` 更像是“在几乎等价 arms 上做 winner picking → OOS 排名随机”的结构性体现。

## 5) 本轮 hard verdict / next
- 本轮 hard verdict：**Rank 140 接线继续成功；Rank 112 单 family scorecard = guard_failed（PBO=1.0）**。
- 更有信息量的下一步（留给后续 Run 3，不在本轮扩展）：
  1) 选一个 gate 真正能产生“保留/砍掉”更平衡分布的 family 再接一次（避免 120:2）；或
  2) 把 aligned returns matrix 升级为“显式多臂 returns 列”（baseline / gate-kept / gate-veto 各自都有完整 return 序列），避免把 arm 语义塞进 event 字段导致 arms 退化。
