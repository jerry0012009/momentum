# Bot3 Optimization Loop — Rank 140 / Rank 111（`window_plus_timeout`）显式三臂重跑

- 时间：2026-03-22 21:42–21:46 UTC
- 严格顺序：Run1 → Run2 → Run3
- 范围控制：本轮仅 **1 个主点（Rank 140 / pbo-cscv honesty gate）** + **1 个紧邻子点（Rank 111 的替代 strict arm：`window_plus_timeout`）**。

## 1) Run 1 = EMA due-check first（Paper Seat）
执行：
```bash
cd /root/clawd/jerry/momentum
python3 scripts/run_ema_paper_trading_guarded_refresh.py --skip-build --require-due
```
结果：`waiting_not_due`（exit code 2，合规）
- 当前无 `due-now / overdue` lane
- 最靠前：`Crypto 1d+1wk（BTC/ETH/SOL）` 已进入 `due_soon`，约 `3.2 小时` 后到点

结论：Run1 不允许伪造 refresh，立刻切到下一允许动作。

## 2) Run 2 = Hosted P3 continuity（低频、事件驱动）
检查：
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`
  - `run_at_utc = 2026-03-22T21:29:29Z`
  - `new_closed_trades_appended = 0`
- `reports/artifacts/rank32b_canary/phase3_status.json`
  - `system_health = ok`
  - `kill_switch = false`
- `reports/artifacts/rank32b_canary/phase3_last_run_summary.json`
  - `venue_ok_count = 2`
  - `query_only = true`

结论：无 `refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch` 这类 status-changing event，本轮按顶板规则跳过，不做近义健康巡检。

## 3) Run 3 = Scout Seat（只选 1 个：Rank 140 / pbo-cscv honesty gate）
### 主点
继续沿顶板当前唯一主点：`Rank 140 / pbo-cscv deflated sharpe honesty gate`。

### 紧邻子点（仅 1 个）
不新开第 4 个 Scout 候选；只在 **已完成 family = Rank 111** 内，把 strict arm 从此前已跑过的 `same_window_only`，换成更宽一点但仍属同 family 的 `window_plus_timeout`，重做一次显式三臂 returns matrix。

### 输入与处理
原始文件：
- `reports/artifacts/scout_rank111_event_clock_15m/trade_log.csv`

注意：该 trade log 的时间列名是 `signal_time`，而矩阵脚本要求 `signal_ts`。本轮只做最小兼容处理：
- 生成规范化输入：`reports/artifacts/pbo_cscv_honesty_gate/rank111_trade_log_signal_ts_window_plus_timeout.csv`
- 将 `signal_time` 原样映射为 `signal_ts`
- 不改原始 family 产物，不扩到别的候选

新产物：
- `reports/artifacts/pbo_cscv_honesty_gate/rank111_trade_log_signal_ts_window_plus_timeout.csv`
- `reports/artifacts/pbo_cscv_honesty_gate/rank111_explicit_three_arm_returns_matrix_window_plus_timeout.csv`
- `reports/artifacts/pbo_cscv_honesty_gate/rank111_explicit_three_arm_returns_matrix_window_plus_timeout.meta.json`
- `reports/artifacts/pbo_cscv_honesty_gate/rank111_explicit_three_arm_scorecard_window_plus_timeout/rank139_pbo_cscv_dsr_scorecard.csv`
- `reports/artifacts/pbo_cscv_honesty_gate/rank111_explicit_three_arm_scorecard_window_plus_timeout/rank139_pbo_cscv_dsr_meta.json`

并补写：
- `reports/artifacts/pbo_cscv_honesty_gate/rank140_explicit_three_arm_family_board.csv`
- `reports/artifacts/pbo_cscv_honesty_gate/rank140_explicit_three_arm_family_board.meta.json`

## 4) 显式三臂结果（Rank 111 / `window_plus_timeout`）
对齐结果：
- `baseline = 198`
- `gate_kept = 113`
- `gate_veto = 85`
- `kept:veto = 113:85`

对比上一版 `same_window_only = 105:93`：
- 这次分布仍然算健康，没有掉到 Rank112 那种极端失衡；
- 但比 `same_window_only` 略偏向 `kept`，说明 `window_plus_timeout` 确实放宽了 strict arm；
- 因而这一版更像是对同 family 内“strict 语义放宽后，PBO 会不会更稳”的最小复核。

## 5) canonical scorecard 结果
### hard read
- `PBO = 0.8000`
- `lambda_median = 0.25`
- `verdict = guard_failed`

### 三臂读数（net 已扣 12bps roundtrip）
- `baseline`：`trades=198`，`mean_net_6bps ≈ -0.0980%`，`sharpe ≈ -0.0705`
- `gate_kept`：`trades=113`，`mean_net_6bps ≈ -0.0907%`，`sharpe ≈ -0.0567`
- `gate_veto`：`trades=85`，`mean_net_6bps ≈ -0.1078%`，`sharpe ≈ -0.1017`
- `kept - veto mean diff ≈ +0.0171%`

### 人话解释
- `window_plus_timeout` 仍然保留了一点区分度：`gate_kept` 比 `gate_veto` 少亏。
- 但这点区分度仍不够稳，`PBO` 反而比 `same_window_only` 的 `0.7143` 更差，升到 `0.8000`。
- 也就是说：**把 Rank111 的 strict arm 放宽到 `window_plus_timeout`，并没有把 Rank140 的 honesty-layer 读数变得更可信；只是让 kept/veto 看起来还算能拆，但 OOS 稳定性依旧不行。**

## 6) family board 更新后的读法
当前 family board 已含以下代表行：
- `Rank125 / rl_gate`：split 较平衡，但 `PBO=0.5714`，仍 `guard_failed`
- `Rank111 / same_window_only`：`105:93` 最平衡，`PBO=0.7143`
- `Rank111 / window_plus_timeout`：`113:85`，`PBO=0.8000`
- `Rank112 / basis_extreme_plus_oi_veto`：`120:2` 极端失衡，虽 `PBO=0.3143` 但不可误读
- `Rank112 / basis_extreme_veto`：split 稍改善到 `104:18`，但 `PBO=0.9429`

当前更清楚的结论：
- `Rank111` 这条 family 在 **更严格 (`same_window_only`)** 与 **稍放宽 (`window_plus_timeout`)** 两个 strict 版本下，都没能把 `PBO` 压到可接受区间；
- `Rank112` 的较低 `PBO` 主要仍像 split 偶然产物；
- 因此 `Rank140` 目前还没有拿到一条“split 可解释 + PBO 过关”的像样参考 family。

## 7) 本轮 hard verdict / next
- ✅ Run1 合规 `waiting_not_due`，未伪造 refresh。
- ✅ Run2 合规跳过，无 hosted P3 re-entry event。
- ✅ Run3 完成 1 个最小硬交付：`Rank111 / window_plus_timeout` 显式三臂 matrix + canonical scorecard，并回写 family board。
- ✅ 这轮补足了 Rank111 的**同 family 宽严对照**：
  - `same_window_only` = 更平衡、但 `PBO=0.7143`
  - `window_plus_timeout` = 略放宽、但 `PBO=0.8000`
- ❌ 结论依旧是 `guard_failed`；Rank111 不能被误写成 Rank140 的可 promote reference family。

## 8) 留给后续 run（本轮不展开）
- 若继续 `Rank 140`，优先只选 **1 条** 仍未做“split 可解释 + 严格语义明确”对照的 family，继续沿显式三臂口径推进；
- 不要退回近义 intake/demo；
- 也不要再把 `Rank111` 当成还有明显增量空间的优先 family，除非后续改的是 split 定义而不是再换近义 strict 词。