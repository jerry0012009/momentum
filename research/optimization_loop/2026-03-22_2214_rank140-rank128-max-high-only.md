# Bot3 Optimization Loop — Rank 140 / Rank 128（`max_high_only`）显式三臂重跑

- 时间：2026-03-22 22:14 UTC
- 严格顺序：Run1 → Run2 → Run3
- 范围控制：本轮仅 **1 个主点（Rank 140 / pbo-cscv honesty gate）** + **1 个紧邻子点（Rank 128 的 `max_high_only` strict arm）**。

## 1) Run 1 = EMA due-check first（Paper Seat）
执行：
```bash
cd /root/clawd/jerry/momentum
python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due
```
结果：`waiting_not_due`（exit code 2，合规）
- 当前无 `due-now / overdue` lane
- 最靠前：`Crypto 1d+1wk（BTC/ETH/SOL）`，约 `1.7 小时` 后到点

结论：Run1 不允许伪造 refresh，立刻切到下一允许动作。

## 2) Run 2 = Hosted P3 continuity（低频、事件驱动）
检查：
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`
  - `run_at_utc = 2026-03-22T22:09:51Z`
  - `new_closed_trades_appended = 0`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_open_positions.csv`
  - 当前 continuity 口径未见新的 open-position 异常提示

结论：本轮没有 `refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch` 这类 status-changing event，按顶板规则跳过，不做近义健康检查。

## 3) Run 3 = Scout Seat（只选 1 个：Rank 140 / pbo-cscv honesty gate）
### 主点
继续沿顶板当前唯一主点：`Rank 140 / pbo-cscv deflated sharpe honesty gate`。

### 紧邻子点（仅 1 个）
本轮只拿 **Rank 128 / max5m impulse confirmation tier** 做 1 次最小显式三臂重跑：
- family：`Rank 128`
- strict arm：`max_high_only`

这样做的原因：
- 这条 family 的 split 不像 `Rank112` 那样极端失衡，也不像 `Rank127` 那样 kept 臂明显更重；
- 它适合回答一个很窄的问题：**高 max5m impulse 那一臂，放到显式 `baseline / gate_kept / gate_veto` 语义后，是否真的比被 veto 的那一臂更好？**

## 4) 输入与最小兼容处理
原始文件：
- `reports/artifacts/scout_rank128_max5m_impulse_confirmation_tier_15m/trade_log.csv`

注意：该 trade log 的时间列名是 `signal_time`，而矩阵脚本要求 `signal_ts`。本轮只做最小兼容处理：
- 生成规范化输入：`reports/artifacts/pbo_cscv_honesty_gate/rank128_trade_log_signal_ts_max_high_only.csv`
- 将 `signal_time` 原样映射为 `signal_ts`
- 不改原 family 原始产物，不扩到其他候选

新产物：
- `reports/artifacts/pbo_cscv_honesty_gate/rank128_trade_log_signal_ts_max_high_only.csv`
- `reports/artifacts/pbo_cscv_honesty_gate/rank128_explicit_three_arm_returns_matrix_max_high_only.csv`
- `reports/artifacts/pbo_cscv_honesty_gate/rank128_explicit_three_arm_returns_matrix_max_high_only.meta.json`
- `reports/artifacts/pbo_cscv_honesty_gate/rank128_explicit_three_arm_scorecard_max_high_only/rank139_pbo_cscv_dsr_scorecard.csv`
- `reports/artifacts/pbo_cscv_honesty_gate/rank128_explicit_three_arm_scorecard_max_high_only/rank139_pbo_cscv_dsr_meta.json`
- `reports/artifacts/pbo_cscv_honesty_gate/rank140_explicit_three_arm_family_board.csv`
- `reports/artifacts/pbo_cscv_honesty_gate/rank140_explicit_three_arm_family_board.meta.json`

## 5) 显式三臂结果（Rank 128 / `max_high_only`）
对齐结果：
- `baseline = 211`
- `gate_kept = 77`
- `gate_veto = 134`
- `kept:veto = 77:134`

人话解释：
- 这不是极端失衡；
- 但也不是像 `Rank111` 那样接近平衡；
- 更像一个 **可解释 split，但 kept 臂偏小** 的 family。

## 6) canonical scorecard 结果
### hard read
- `PBO = 0.8000`
- `lambda_median = 0.25`
- `verdict = guard_failed`

### 三臂读数（net 已扣 12bps roundtrip）
- `baseline`：`trades=211`，`mean_net_6bps ≈ -0.1475%`，`sharpe ≈ -0.1327`
- `gate_kept`：`trades=77`，`mean_net_6bps ≈ -0.1408%`，`sharpe ≈ -0.1107`
- `gate_veto`：`trades=134`，`mean_net_6bps ≈ -0.1514%`，`sharpe ≈ -0.1494`
- `kept - veto mean diff ≈ +0.0107%`

### 人话解释
- `max_high_only` 这次不是反向信号：`gate_kept` 的确比 `gate_veto` **稍微少亏一点**；
- 但幅度很小，远远不足以把 OOS 稳定性拉到能过 honesty gate 的程度；
- 换句话说：**它有一点“方向上对”，但没有强到能过 guard**。

## 7) family board 更新后的读法
新增一行：
- `Rank128 / max_high_only`：`77:134`，`PBO=0.8000`，`guard_failed`

更新后更清楚的结论：
- `Rank128` 不是 `Rank127` 那种“veto 臂反而更好”的反证型 family；
- 但它也没有像样地证明“kept 臂明显更好且可稳定复现”；
- 所以它更像一个 **弱正向但不够硬** 的 honesty-layer 参考样本，而不是可 promote 的参考 family。

## 8) 本轮 hard verdict / next
- ✅ Run1 合规 `waiting_not_due`，未伪造 refresh。
- ✅ Run2 合规跳过，无 hosted P3 status-changing event。
- ✅ Run3 完成 1 个最小硬交付：`Rank128 / max_high_only` 显式三臂 matrix + canonical scorecard，并回写 family board。
- ❌ 结果仍是 `guard_failed`；只是方向上比 `Rank127` 更正常、比 `Rank112` 更可解释。

## 9) 留给后续 run（本轮不展开）
- 若继续 `Rank 140`，优先只再选 **1 条** 仍可能出现“split 可解释 + kept 明显优于 veto”的 family；
- 不要回头重复 `Rank111/112/125/127/128` 的近义重磨；
- 也不要因为这轮无事发生，就把 Hosted P3 continuity 拉回 Scout 主资源位。
