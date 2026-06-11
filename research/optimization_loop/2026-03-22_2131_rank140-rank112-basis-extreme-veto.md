# Bot3 Optimization Loop — Rank 140 / Rank 112 (`basis_extreme_veto`) 显式三臂重跑

- 时间：2026-03-22 21:31 UTC
- 严格顺序：Run1 → Run2 → Run3
- 范围控制：本轮仅 **1 个主点（Rank 140 / pbo-cscv honesty gate）** + **1 个紧邻子点（Rank 112 的替代 strict arm：`basis_extreme_veto`）**。

## 1) Run 1 = EMA due-check first（Paper Seat）
执行：
```bash
cd /root/clawd/jerry/momentum
python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due
```
结果：`waiting_not_due`（exit code 2，合规）
- 当前无 `due-now / overdue` lane
- 最靠前：`Crypto 1d+1wk（BTC/ETH/SOL）` 已进入 `due_soon`，约 `2.5 小时` 后到点

结论：本轮不允许伪造 refresh，立刻切下一允许动作。

## 2) Run 2 = Hosted P3 continuity（低频、事件驱动）
检查：
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`
  - `run_at_utc = 2026-03-22T21:29:29Z`
  - `new_closed_trades_appended = 0`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_bot3_reentry_queue.csv`
  - `Rank 2 / 17 / 29 / 32b` 全部 `bot3_reentry_now = no`

结论：无 `refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch` 这类 status-changing event，本轮按顶板规则跳过，不做近义健康巡检。

## 3) Run 3 = Scout Seat（只选 1 个：Rank 140 / pbo-cscv honesty gate）
### 主点
继续沿顶板当前唯一主点：`Rank 140 / pbo-cscv deflated sharpe honesty gate`。

### 紧邻子点（仅 1 个）
不新开第 4 个 Scout 候选；只在 **已完成 family = Rank 112** 内，把 strict arm 从此前极端失衡的 `basis_extreme_plus_oi_veto`，改成更宽一点但仍同 family 的 `basis_extreme_veto`，重做一次显式三臂 returns matrix。

输入：
- `reports/artifacts/scout_rank112_basis_dislocation_short_veto_15m/trade_log.csv`

新产物：
- `reports/artifacts/pbo_cscv_honesty_gate/rank112_explicit_three_arm_returns_matrix_basis_extreme_veto.csv`
- `reports/artifacts/pbo_cscv_honesty_gate/rank112_explicit_three_arm_returns_matrix_basis_extreme_veto.meta.json`
- `reports/artifacts/pbo_cscv_honesty_gate/rank112_explicit_three_arm_scorecard_basis_extreme_veto/rank139_pbo_cscv_dsr_scorecard.csv`
- `reports/artifacts/pbo_cscv_honesty_gate/rank112_explicit_three_arm_scorecard_basis_extreme_veto/rank139_pbo_cscv_dsr_meta.json`
- `reports/artifacts/pbo_cscv_honesty_gate/rank112_explicit_three_arm_scorecard_basis_extreme_veto/summary.json`

并把结果补进：
- `reports/artifacts/pbo_cscv_honesty_gate/rank140_explicit_three_arm_family_board.csv`
- `reports/artifacts/pbo_cscv_honesty_gate/rank140_explicit_three_arm_family_board.meta.json`

## 4) 显式三臂结果（Rank 112 / `basis_extreme_veto`）
对齐结果：
- `baseline = 122`
- `gate_kept = 104`
- `gate_veto = 18`
- `kept:veto = 104:18`

对比上一版 `basis_extreme_plus_oi_veto = 120:2`：
- 这次 **仍不平衡**，但至少不再几乎“没有 veto 臂”；读数可解释性明显更高。
- 也因此能更诚实地回答：之前 Rank112 的低 PBO，到底是不是被极端 split 偶然美化了。

## 5) canonical scorecard 结果
### hard read
- `PBO = 0.9429`
- `lambda_median = 0.25`
- `verdict = guard_failed`

### 三臂读数（net 已扣 12bps roundtrip）
- `baseline`：`trades=122`，`mean_net_6bps ≈ -0.1652%`，`sharpe ≈ -0.1747`
- `gate_kept`：`trades=104`，`mean_net_6bps ≈ -0.1780%`，`sharpe ≈ -0.1962`
- `gate_veto`：`trades=18`，`mean_net_6bps ≈ -0.0910%`，`sharpe ≈ -0.0778`
- `kept - veto mean diff ≈ -0.0870%`

### 人话解释
- 一旦把 Rank112 的 strict arm 放宽到 `basis_extreme_veto`，三臂虽然更能拆开，但结果反而更差：
  - `gate_kept` 比 `gate_veto` 更亏；
  - `PBO` 直接恶化到 `0.9429`。
- 这说明：**Rank112 之前那个相对“好看”的分数，很大概率就是被 `120:2` 极端 split 扭曲出来的假象，不适合当 Rank140 的主参考 family。**

## 6) 本轮 hard verdict / next
- ✅ Run1 合规 `waiting_not_due`，未伪造 refresh。
- ✅ Run2 合规跳过，无 hosted P3 re-entry event。
- ✅ Run3 完成 1 个最小硬交付：`Rank112 / basis_extreme_veto` 显式三臂 matrix + scorecard，并回写 family board。
- ✅ 现在对 Rank112 的读法更清楚了：
  - `basis_extreme_plus_oi_veto` = `PBO` 低，但 arms 极端失衡；
  - `basis_extreme_veto` = split 稍好，但 `PBO` 与 kept/veto 方向同时恶化；
  - **因此 Rank112 不应再被误读成 Rank140 的优先参考 family。**
- ✅ 当前 family board 的更像样参考位仍是：`Rank125`（split 与解释性更平衡），其次可保留 `Rank111` 作为“split 最平衡但 guard 仍失败”的样本。

## 7) 留给后续 run（本轮不展开）
- 若继续 `Rank 140`，优先只选 **1 条** kept/veto 真能拆开的 family，继续沿显式三臂口径推进；
- 不要再回头把 `Rank112` 当作“低 PBO 优选样本”，除非未来能拿出新的 split 设计同时改善 `arms balance` 与 `guard verdict`。
