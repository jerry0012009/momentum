# Bot3 Optimization Loop — Rank 140 / Rank 125 显式三臂 returns matrix + canonical scorecard

- 时间：2026-03-22 19:20 UTC
- 严格顺序：Run1 → Run2 → Run3
- 范围控制：本轮仅 **1 个主点（Rank 140）** + **1 个紧邻子点（Rank 125 explicit 3-arm matrix）**。

## 1) Run 1 = EMA due-check first（Paper Seat）
执行：
```bash
cd jerry/momentum
python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due
```
结果：`waiting_not_due`（exit code 2 合规）
- Crypto 1d+1wk：约 4.6 小时后到点
- 创业板ETF 1d：约 11.6 小时后到点
- 贵州茅台 1d+1wk：约 11.6 小时后到点

结论：本轮不得空转，立刻切下一允许动作。

## 2) Run 2 = Hosted P3 continuity（低频、事件驱动）
仅做事件判定（不做近义健康巡检）：
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`
  - `run_at_utc = 2026-03-22T19:06:54Z`
  - `new_closed_trades_appended = 0`

结论：无 status-changing event（无 refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch），按顶板规则跳过。

## 3) Run 3 = Scout Seat（只选 1 个：Rank 140 / pbo-cscv honesty gate）
### 主点：把 Rank 125 从“隐式 event 映射”升级成显式三臂 returns matrix
沿用桌面板当前唯一允许主点：`Rank 140 / pbo-cscv deflated sharpe honesty gate`。

### 紧邻子点（仅 1 个）：只接 Rank 125 这一个 family
输入：
- `reports/artifacts/scout_rank125_range_location_veto_15m/trade_log.csv`

本轮新产物：
- `reports/artifacts/pbo_cscv_honesty_gate/rank125_explicit_three_arm_returns_matrix.csv`
- `reports/artifacts/pbo_cscv_honesty_gate/rank125_explicit_three_arm_returns_matrix.meta.json`
- `reports/artifacts/pbo_cscv_honesty_gate/rank125_explicit_three_arm_scorecard/rank139_pbo_cscv_dsr_scorecard.csv`
- `reports/artifacts/pbo_cscv_honesty_gate/rank125_explicit_three_arm_scorecard/rank139_pbo_cscv_dsr_meta.json`

显式三臂口径（人话）：
- `baseline`：每笔 baseline trade 都保留原始 `gross_return`
- `gate_kept`：若同一 `(asset, setup, signal_time)` 下存在 `rl_gate` trade，则写入同一笔 baseline 的 `gross_return`
- `gate_veto`：若不存在 `rl_gate` trade，则写入同一笔 baseline 的 `gross_return`
- 空白表示 `no-trade`，不应收费

本轮对齐结果：
- baseline：`824`
- gate_kept：`459`
- gate_veto：`365`

> 这比上一轮 Rank 112 的 `120:2` 极端分布更像样，终于能把“被保留”和“被 veto”拆成有信息量的两臂，而不是几乎全挤在一边。

## 4) 跑 canonical scorecard（显式三臂）
执行：
```bash
python3 scripts/build_pbo_cscv_dsr_scorecard.py \
  --trade-log reports/artifacts/pbo_cscv_honesty_gate/rank125_explicit_three_arm_returns_matrix.csv \
  --baseline-col gross_ret_baseline \
  --gate-kept-col gross_ret_gate_kept \
  --gate-veto-col gross_ret_gate_veto \
  --out-dir reports/artifacts/pbo_cscv_honesty_gate/rank125_explicit_three_arm_scorecard \
  --label "Rank140 canonical scorecard on Rank125 explicit 3-arm returns matrix" \
  --segments 8
```

## 5) 结果（只读这一条 family）
### hard read
- `PBO = 0.5714` → `verdict = guard_failed`
- `lambda_median = 0.25`

### 三臂读数（net 已扣 12bps roundtrip）
- `baseline`：`trades=824`，`mean_net_6bps ≈ -0.0626%`，`sharpe ≈ -0.0458`
- `gate_kept`：`trades=459`，`mean_net_6bps ≈ -0.0132%`，`sharpe ≈ -0.0102`
- `gate_veto`：`trades=365`，`mean_net_6bps ≈ -0.1247%`，`sharpe ≈ -0.0859`

### 人话解释
- 这轮最重要的不是把 `PBO` 变好，而是把 Rank 125 的输入从“event 字段里暗藏 arm 语义”改成了 **显式三臂 returns**。
- 结果上，`gate_kept` 明显比 `gate_veto` 少亏，说明 `rl_gate` 至少在“把更差的一臂分出去”这件事上有一点像样的区分度；
- 但 `PBO` 仍然高于 0.5，表示即便换成显式三臂后，这条 family 的 OOS 排名稳定性还是不够，按 Rank 140 honesty-layer 口径仍应判 `guard_failed`。

## 6) 本轮 hard verdict / next
- ✅ Run1 合规 `waiting_not_due`，未伪造 refresh。
- ✅ Run2 合规跳过，无 status-changing event。
- ✅ Run3 完成 1 个最小硬交付：`Rank 125 explicit 3-arm matrix + scorecard`。
- ✅ 和上一轮相比，这次终于拿到更平衡的 `459 : 365` kept/veto 分布，说明“显式三臂”这条路是对的。
- ❌ 但 `PBO=0.5714` 仍然说明 Rank 125 在当前 honesty-layer 下不够稳，暂时不该把它往 promote 方向误读。

## 7) 留给后续 run（本轮不展开）
- 若继续 Rank 140，优先再选 **1 条** kept/veto 分布更均衡、且 gate 语义更干净的 family 做同样 explicit 3-arm 重跑；
- 不要同时打开多个 Scout 候选，也不要退回近义 intake/demo。