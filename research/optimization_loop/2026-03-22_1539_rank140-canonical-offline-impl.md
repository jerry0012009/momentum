# Bot3 Optimization Loop — Rank 140 canonical offline implementation（smoke-run）

- 时间：2026-03-22 15:39 UTC
- 主点：`Rank 140 / pbo-cscv deflated sharpe honesty gate`
- 本轮严格顺序：`Run1 -> Run2 -> Run3`
- 范围控制：仅 **1 个主点** + **1 个紧邻子点**，未同时打开多个 Scout 候选。

## 1) Run 1 = EMA due-check first
执行：
```bash
python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due
```
结果：`waiting_not_due`（exit code 2，符合守门预期）
- Crypto 1d+1wk：约 8.2h 后到点
- 创业板ETF 1d：约 15.2h 后到点
- 贵州茅台 1d+1wk：约 15.2h 后到点

结论：本轮不得空转，立刻切下一允许动作。

## 2) Run 2 = Hosted P3 continuity（事件驱动）
检查：`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`
- `run_at_utc = 2026-03-22T14:51:50Z`
- `new_closed_trades_appended = 0`

结论：未见新的 status-changing event（无 refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch），按顶板规则跳过近义健康检查。

## 3) Run 3 = Scout Seat（Rank 140）
### 主点（唯一主动作）
完成一次可复跑的 **canonical offline implementation smoke-run**（单 family 输入）：
```bash
python3 scripts/build_pbo_cscv_dsr_scorecard.py \
  --trade-log reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/trade_log.csv \
  --event-col event_0.8 \
  --out-dir reports/artifacts/pbo_cscv_honesty_gate \
  --label "Rank140 canonical offline impl smoke-run (input=rank139 trade_log)" \
  --segments 8
```
产物（已刷新）：
- `reports/artifacts/pbo_cscv_honesty_gate/rank139_pbo_cscv_dsr_scorecard.csv`
- `reports/artifacts/pbo_cscv_honesty_gate/rank139_pbo_cscv_dsr_meta.json`

### 紧邻子点（仅 1 个）
冻结最小接线口径：
- 先保证 `single-family aligned returns matrix`；
- 再跑 CSCV/PBO/DSR；
- 再决定该 family 是否允许继续争夺 `paper candidate / tiny-live review`。

一句话：**Rank 140 现在优先是“统一诚实守门层”，不是新 alpha 候选。**

## 4) 本轮 hard verdict
`Rank 140 = implementation_continues / smoke_run_done / keep_single-focus`

- 本轮已从“只讲 source”推进到“可复跑实现”层；
- 下一步仍应保持单点推进：把输入从示例 family 扩展到新的 fresh scout family（一次只接一个 family），不要并行开多个候选。
