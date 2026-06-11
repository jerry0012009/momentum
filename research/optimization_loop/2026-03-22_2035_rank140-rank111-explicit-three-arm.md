# Bot3 Optimization Loop — Rank 140 / Rank 111 显式三臂 returns matrix + canonical scorecard

- 时间：2026-03-22 20:35 UTC
- 严格顺序：Run1 → Run2 → Run3
- 范围控制：本轮仅 **1 个主点（Rank 140）** + **1 个紧邻子点（Rank 111 explicit 3-arm）**。

## 1) Run 1 = EMA due-check first（Paper Seat）
执行：
```bash
cd /root/clawd/jerry/momentum
python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due
```
结果：`waiting_not_due`（exit code 2 合规）
- Crypto 1d+1wk（BTC/ETH/SOL）：约 3.4 小时后到点
- 创业板ETF 1d：约 10.4 小时后到点
- 贵州茅台 1d+1wk：约 10.4 小时后到点

结论：Run1 不得伪造 refresh，立刻切下一允许动作。

## 2) Run 2 = Hosted P3 continuity（低频、事件驱动）
检查：
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`
  - `run_at_utc = 2026-03-22T20:10:01Z`
  - `new_closed_trades_appended = 0`

结论：无 status-changing event（无 refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch），按顶板规则跳过，不做近义健康巡检。

## 3) Run 3 = Scout Seat（只选 1 个：Rank 140 / pbo-cscv honesty gate）
### 主点
继续沿顶板当前唯一主点：`Rank 140 / pbo-cscv deflated sharpe honesty gate`。

### 紧邻子点（仅 1 个）
选定 family：`Rank 111 / abnormal-return event clock`。
本轮只做 **显式三臂 returns matrix + canonical scorecard**，不再开第二个 Scout 候选。

输入：
- `reports/artifacts/scout_rank111_event_clock_15m/trade_log.csv`
- strict arm：`same_window_only`

新产物：
- `reports/artifacts/pbo_cscv_honesty_gate/rank111_explicit_three_arm_returns_matrix.csv`
- `reports/artifacts/pbo_cscv_honesty_gate/rank111_explicit_three_arm_returns_matrix.meta.json`
- `reports/artifacts/pbo_cscv_honesty_gate/rank111_explicit_three_arm_scorecard/rank139_pbo_cscv_dsr_scorecard.csv`
- `reports/artifacts/pbo_cscv_honesty_gate/rank111_explicit_three_arm_scorecard/rank139_pbo_cscv_dsr_meta.json`

显式三臂口径（人话）：
- `baseline`：每笔 baseline trade 保留原始 `gross_return`
- `gate_kept`：若同一 `(asset, signal_time)` 存在 `same_window_only` trade，则写入同一笔 baseline 的 `gross_return`
- `gate_veto`：若不存在对应 strict trade，则写入同一笔 baseline 的 `gross_return`
- 空白表示 `no-trade`，不应收费

对齐结果：
- baseline：`198`
- gate_kept：`105`
- gate_veto：`93`

> 这次 kept/veto 分布明显比 Rank 112 的 `120:2` 更健康，也比 Rank 125 更接近平衡，适合继续验证 Rank 140 的显式三臂口径。

## 4) 跑 canonical scorecard（显式三臂）
执行：
```bash
python3 scripts/build_pbo_cscv_dsr_scorecard.py \
  --trade-log reports/artifacts/pbo_cscv_honesty_gate/rank111_explicit_three_arm_returns_matrix.csv \
  --baseline-col gross_ret_baseline \
  --gate-kept-col gross_ret_gate_kept \
  --gate-veto-col gross_ret_gate_veto \
  --out-dir reports/artifacts/pbo_cscv_honesty_gate/rank111_explicit_three_arm_scorecard \
  --label "Rank140 canonical scorecard on Rank111 explicit 3-arm returns matrix" \
  --segments 8
```

## 5) 结果（只读这一条 family）
### hard read
- `PBO = 0.7143` → `verdict = guard_failed`
- `lambda_median = 0.25`

### 三臂读数（net 已扣 12bps roundtrip）
- `baseline`：`trades=198`，`mean_net_6bps ≈ -0.0980%`，`sharpe ≈ -0.0705`
- `gate_kept`：`trades=105`，`mean_net_6bps ≈ -0.0699%`，`sharpe ≈ -0.0431`
- `gate_veto`：`trades=93`，`mean_net_6bps ≈ -0.1298%`，`sharpe ≈ -0.1201`

### 人话解释
- `same_window_only` 至少把更差的一臂分出去了一点：`gate_kept` 比 `gate_veto` 少亏，说明 gate 不是完全没信息量。
- 但 `PBO` 仍高于 `0.5`，说明即便 kept/veto 分布已经更平衡，OOS 排名稳定性还是不够，按 Rank 140 honesty-layer 口径仍应判 `guard_failed`。
- 换句话说：**Rank 111 在当前显式三臂口径下，区分度有一点，但还远不够稳。**

## 6) 本轮 hard verdict / next
- ✅ Run1 合规 `waiting_not_due`，未伪造 refresh。
- ✅ Run2 合规跳过，无 status-changing event。
- ✅ Run3 完成 1 个最小硬交付：`Rank 111 explicit 3-arm matrix + scorecard`。
- ✅ 本轮拿到较健康的 `105 : 93` kept/veto 分布，说明显式三臂方法继续值得沿用。
- ❌ 但 `PBO=0.7143` 仍属 `guard_failed`，不能把这条 family 误读成可 promote。

## 7) 留给后续 run（本轮不展开）
- 若继续 Rank 140，仍应只选 **1 条** family 做同样 explicit 3-arm 重跑；优先选 kept/veto 分布接近平衡、且 strict 语义比 `same_window_only` 更强的 family。
- 不要退回近义 intake/demo，也不要同时打开多个 Scout 候选。
