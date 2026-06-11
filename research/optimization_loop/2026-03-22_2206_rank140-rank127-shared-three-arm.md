# Bot3 Optimization Loop — Rank 140 / Rank 127（`shared_gate`）显式三臂重跑

- 时间：2026-03-22 22:01–22:06 UTC
- 严格顺序：Run1 → Run2 → Run3
- 范围控制：本轮仅 **1 个主点（Rank 140 / pbo-cscv honesty gate）** + **1 个紧邻子点（Rank 127 的 `shared_gate` strict arm）**。

## 1) Run 1 = EMA due-check first（Paper Seat）
执行：
```bash
cd /root/clawd/jerry/momentum
python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due
```
结果：`waiting_not_due`（exit code 2，合规）
- 当前无 `due-now / overdue` lane
- 最靠前：`Crypto 1d+1wk（BTC/ETH/SOL）` 已进入 `due_soon`，约 `2.0 小时` 后到点

结论：Run1 不允许伪造 refresh，立刻切到下一允许动作。

## 2) Run 2 = Hosted P3 continuity（低频、事件驱动）
检查：
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`
  - `run_at_utc = 2026-03-22T21:49:15Z`
  - `new_closed_trades_appended = 1`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_bot3_reentry_queue.csv`
  - 当前 `Rank 2 / 17 / 29 / 32b` 全部 `bot3_reentry_now = yes`，说明有 continuity 触发资格
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_closed_trades.csv`
  - 最新 append 是 `Rank 29 / BTC-USD / breakout_align_ge2`
  - `entry_ts=2026-03-22T18:45:00Z`，`exit_ts=2026-03-22T20:30:00Z`
  - `net_ret ≈ +0.0352%`（6bps/side 后仍接近平）
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_open_positions.csv`
  - 仍只有 `Rank 17 / ETH-USD` 与 `Rank 17 / SOL-USD` 两个 continuity open inferred，口径未突变

结论：这次确实出现了一个 **status-changing event（新增 closed trade append）**，所以 Run2 不是空转；但事件读下来只是 **Rank 29 常规 append**，没有 `refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch`。因此本轮对 P3 的最小诚实处理是：**记账 + 不升级成主资源位**，随后继续回到 Scout 主线。

## 3) Run 3 = Scout Seat（只选 1 个：Rank 140 / pbo-cscv honesty gate）
### 主点
继续沿顶板当前唯一主点：`Rank 140 / pbo-cscv deflated sharpe honesty gate`。

### 紧邻子点（仅 1 个）
本轮不新开别的 Scout 候选，只拿 **已 park 但仍 relevant 的 Rank 127 family** 做 1 次最小显式三臂重跑：
- family：`Rank 127 / signal→confirm ATR delta phase gate`
- strict arm：`shared_gate`

这样做的原因：
- 顶板已经明确提到 `Rank 127` 的 shared 版本在 2026-03 转负，因此它是一个很合适的 honesty-layer 对照 family；
- 本轮只回答一个问题：**在显式 `baseline / gate_kept / gate_veto` 口径下，Rank 127 shared_gate 到底是“真有 kept 优势但 guard 仍失败”，还是“其实 veto 臂更好，只是以前被聚合读法遮住了”？**

## 4) 输入与最小兼容处理
原始文件：
- `reports/artifacts/scout_rank127_signal_confirm_atr_delta_phase_15m/trade_log.csv`

注意：该 trade log 的时间列名是 `signal_time`，而矩阵脚本要求 `signal_ts`。本轮只做最小兼容处理：
- 生成规范化输入：`reports/artifacts/pbo_cscv_honesty_gate/rank127_trade_log_signal_ts_shared_gate.csv`
- 将 `signal_time` 原样映射为 `signal_ts`
- 不改原 family 原始产物，不扩到其他候选

新产物：
- `reports/artifacts/pbo_cscv_honesty_gate/rank127_trade_log_signal_ts_shared_gate.csv`
- `reports/artifacts/pbo_cscv_honesty_gate/rank127_explicit_three_arm_returns_matrix_shared_gate.csv`
- `reports/artifacts/pbo_cscv_honesty_gate/rank127_explicit_three_arm_returns_matrix_shared_gate.meta.json`
- `reports/artifacts/pbo_cscv_honesty_gate/rank127_explicit_three_arm_scorecard_shared_gate/rank139_pbo_cscv_dsr_scorecard.csv`
- `reports/artifacts/pbo_cscv_honesty_gate/rank127_explicit_three_arm_scorecard_shared_gate/rank139_pbo_cscv_dsr_meta.json`

并补写：
- `reports/artifacts/pbo_cscv_honesty_gate/rank140_explicit_three_arm_family_board.csv`
- `reports/artifacts/pbo_cscv_honesty_gate/rank140_explicit_three_arm_family_board.meta.json`

## 5) 显式三臂结果（Rank 127 / `shared_gate`）
对齐结果：
- `baseline = 824`
- `gate_kept = 525`
- `gate_veto = 299`
- `kept:veto = 525:299`

人话解释：
- 这不是 Rank112 那种几乎没有 veto 臂的极端失衡；
- 但也不算像 Rank111 / Rank125 那样比较平衡；
- 它更像一个 **split 可用、但 kept 明显更重** 的 shared-gate family。

## 6) canonical scorecard 结果
### hard read
- `PBO = 0.6286`
- `lambda_median = 0.25`
- `verdict = guard_failed`

### 三臂读数（net 已扣 12bps roundtrip）
- `baseline`：`trades=824`，`mean_net_6bps ≈ -0.0626%`，`sharpe ≈ -0.0458`
- `gate_kept`：`trades=525`，`mean_net_6bps ≈ -0.0737%`，`sharpe ≈ -0.0587`
- `gate_veto`：`trades=299`，`mean_net_6bps ≈ -0.0431%`，`sharpe ≈ -0.0279`
- `kept - veto mean diff ≈ -0.0307%`

### 人话解释
- 这次不是“gate_kept 稍微更好但 PBO 还是不过关”，而是更直接：
  - `gate_kept` 比 `gate_veto` **更亏**；
  - OOS 组合里也经常是 `gate_veto` 排名更靠前。
- 换句话说：**Rank 127 的 `shared_gate` 在显式三臂口径下，更像是在保留较差的那一臂，而不是诚实地把坏交易 veto 掉。**
- 这和顶板先前对 Rank 127 的 desk 结论是同方向的：shared 版本不但没升格，放到 Rank 140 honesty-layer 里看，反而能更清楚地看到“被 veto 的那部分并不更差，很多时候还更好”。

## 7) family board 更新后的读法
当前 family board 已至少含这些代表行：
- `Rank125 / rl_gate`：split 较平衡，`PBO=0.5714`，但仍 `guard_failed`
- `Rank111 / same_window_only`：`105:93` 最平衡，`PBO=0.7143`
- `Rank111 / window_plus_timeout`：`113:85`，`PBO=0.8000`
- `Rank112 / basis_extreme_plus_oi_veto`：`120:2`，低 PBO 但极端失衡
- `Rank112 / basis_extreme_veto`：split 稍改善，但 `PBO=0.9429`
- `Rank127 / shared_gate`：`525:299`，split 可用，但 **veto 臂优于 kept 臂**，`PBO=0.6286`

当前更清楚的结论：
- `Rank127` 不应再被误读成一个“shared gate 曾经差一点就能当 honesty layer”的 family；
- 它在显式三臂语义下给出的其实是一个更强的反证：**这个 gate 留下来的那部分并没有更好。**
- 因而 Rank140 目前仍缺少一条真正满足“split 可解释 + kept 优于 veto + PBO 过得去”的参考 family。

## 8) 本轮 hard verdict / next
- ✅ Run1 合规 `waiting_not_due`，未伪造 refresh。
- ✅ Run2 合规认领了 1 次真实 P3 continuity 事件，但确认只是 `Rank29` 常规 append，不升级成主资源位。
- ✅ Run3 完成 1 个最小硬交付：`Rank127 / shared_gate` 显式三臂 matrix + canonical scorecard，并回写 family board。
- ❌ 结果仍是 `guard_failed`；而且方向比 Rank111/125 更差：这次是 **`veto` 臂优于 `kept` 臂**。

## 9) 留给后续 run（本轮不展开）
- 若继续 `Rank 140`，优先只选 **1 条** 仍有机会出现“kept 优于 veto 且 split 可解释”的 family；
- 不要回头重磨 `Rank127` 的近义 shared 变体；
- 也不要因为这次 Run2 有 append，就把 Hosted P3 continuity 重新抬回 Scout 主资源位。 
