# Bot3 Optimization Loop — Rank 140 scorecard arm 命名修正（gate_kept / gate_veto）

- 时间：2026-03-22 19:07 UTC
- 严格顺序：Run1 → Run2 → Run3
- 范围控制：本轮仅 **1 个主点（Rank 140 scorecard arms 人话命名）** + **1 个紧邻子点（Rank 112 explicit 3-arm scorecard 轻量重跑）**。

---

## Run 1 = EMA due-check first（Paper Seat）
执行：
```bash
cd jerry/momentum
python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due
```
结果：`waiting_not_due`（exit code 2 合规）
- 当前无 `due-now / overdue` lane
- 最靠前：Crypto 1d+1wk 约 4.9h 后到点；创业板ETF 1d / 贵州茅台 1d+1wk 约 11.9h 后到点

结论：Paper Seat 本轮无合法刷新动作，**不得空转**，切下一允许动作。

---

## Run 2 = Hosted P3 continuity（低频、事件驱动）
仅做事件判定（不做近义健康巡检）：
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`
  - `run_at_utc = 2026-03-22T19:06:54Z`
  - `new_closed_trades_appended = 0`

结论：无 status-changing event（refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch），按顶板规则跳过。

---

## Run 3 = Scout Seat（只选 1 个：Rank 140 honesty gate）
### 主点：把 canonical scorecard 的 arm 命名从历史遗留改为人话
背景：当前 `build_pbo_cscv_dsr_scorecard.py` 在显式三臂输入模式下，仍输出历史 arm 名（`veto_opp_dir / confirm_same_dir_only`），语义容易误导（它们现在只是 “gate presence 分桶” 的 kept/veto，而非方向确认）。

本轮改动（只改命名，不扩功能，不引入新候选）：
- `scripts/build_pbo_cscv_dsr_scorecard.py`
  - `ARMS = [baseline, gate_kept, gate_veto]`
  - explicit 3-arm 模式的 return 映射：
    - `gross_ret_gate_kept -> gate_kept`
    - `gross_ret_gate_veto -> gate_veto`
  - event-col 旧模式也同步把输出 key 改成 `gate_kept/gate_veto`（保持一致）。

### 紧邻子点：只重跑 Rank112 explicit 3-arm scorecard（验证产物一致）
执行：
```bash
python3 scripts/build_pbo_cscv_dsr_scorecard.py \
  --trade-log reports/artifacts/pbo_cscv_honesty_gate/rank112_explicit_three_arm_returns_matrix.csv \
  --baseline-col gross_ret_baseline \
  --gate-kept-col gross_ret_gate_kept \
  --gate-veto-col gross_ret_gate_veto \
  --out-dir reports/artifacts/pbo_cscv_honesty_gate/rank112_explicit_three_arm_scorecard \
  --label "Rank140 canonical scorecard on Rank112 explicit 3-arm returns matrix" \
  --segments 8
```
产物（更新后的 CSV 中 arm 命名已变更）：
- `reports/artifacts/pbo_cscv_honesty_gate/rank112_explicit_three_arm_scorecard/rank139_pbo_cscv_dsr_scorecard.csv`
- `reports/artifacts/pbo_cscv_honesty_gate/rank112_explicit_three_arm_scorecard/rank139_pbo_cscv_dsr_meta.json`

读数（与上一轮一致，仅命名变更）：
- `PBO ≈ 0.314` → `verdict = guard_risky`
- `lambda_median = 0.75`
- trades：baseline=122 / gate_kept=120 / gate_veto=2

---

## 本轮 hard verdict
- ✅ Rank 140 honesty gate 的 scorecard 输出 arms 已从“历史别名”改为 `gate_kept / gate_veto`，降低语义误读成本。
- ✅ 仅对 Rank112 做了最小重跑校验，未扩展到新 family / 新候选，符合本轮范围控制。

## Next（留给后续 run，不在本轮展开）
- 选一个 `gate_kept : gate_veto` 分布更均衡的 family 再跑 1 次（避免 120:2 极端导致信息量不足）。
