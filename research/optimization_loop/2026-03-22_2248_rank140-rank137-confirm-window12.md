# Bot3 Optimization Loop — Rank 140 / Rank 137（`confirm_window_12`）显式三臂重跑

- 时间：2026-03-22 22:48 UTC
- 严格顺序：Run1 → Run2 → Run3
- 范围控制：本轮仅 **1 个主点（Rank 140 / pbo-cscv honesty gate）** + **1 个紧邻子点（Rank 137 / state expiry latency budget）**。

## 1) Run 1 = EMA due-check first（Paper Seat）
执行：
```bash
cd /root/clawd/jerry/momentum
python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due
```
结果：`waiting_not_due`（exit code 2，合规）
- 当前无 `due-now / overdue` lane
- 最靠前：`Crypto 1d+1wk（BTC/ETH/SOL）`
- 当前离下一次 close 约 `1.2 小时`

结论：Run1 不允许伪造 refresh，立刻切到下一允许动作。

## 2) Run 2 = Hosted P3 continuity（低频、事件驱动）
检查：
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`
  - `run_at_utc = 2026-03-22T22:38:48Z`
  - `new_closed_trades_appended = 0`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_open_positions.csv`
  - 仍仅见 `Rank 17 / ETH-USD short`、`Rank 17 / SOL-USD short` 的既有 open inferred 口径
  - 本轮未见新的 `refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch`

结论：Run2 合规跳过，不做近义 continuity 巡检。

## 3) Run 3 = Scout Seat（只选 1 个：Rank 140 / pbo-cscv honesty gate）
### 主点
继续沿顶板当前唯一主点：`Rank 140 / pbo-cscv deflated sharpe honesty gate`。

### 紧邻子点（仅 1 个）
本轮只拿 **Rank 137 / state expiry latency budget** 做 1 次更窄的显式三臂重跑：
- family：`Rank 137`
- strict arm：`confirm_window_12`

选择它的原因：
- 上一轮 `confirm12_entry24` 已经是 `guard_passed`；
- 本轮只追问一个更窄的问题：**真正起作用的核心，到底更像“确认窗口 12 根”本身，还是要把 entry latency 预算也一起绑上？”**
- 为了避免同轮开第二个紧邻子点，本轮只拆 `confirm_window_12`，不再额外拆 `entry24_only` 或别的 family。

## 4) 最小兼容处理
原始文件：
- `reports/artifacts/scout_rank137_state_expiry_latency_budget_15m/trade_log.csv`

兼容动作（只做最小映射，不改原 family 产物）：
- 生成规范化输入：`reports/artifacts/pbo_cscv_honesty_gate/rank137_trade_log_signal_ts_confirm_window_12.csv`
- 将 `signal_time -> signal_ts`
- 将 `baseline_no_expiry -> baseline`（仅为复用显式三臂脚本）

新产物：
- `reports/artifacts/pbo_cscv_honesty_gate/rank137_trade_log_signal_ts_confirm_window_12.csv`
- `reports/artifacts/pbo_cscv_honesty_gate/rank137_explicit_three_arm_returns_matrix_confirm_window_12.csv`
- `reports/artifacts/pbo_cscv_honesty_gate/rank137_explicit_three_arm_returns_matrix_confirm_window_12.meta.json`
- `reports/artifacts/pbo_cscv_honesty_gate/rank137_explicit_three_arm_scorecard_confirm_window_12/rank139_pbo_cscv_dsr_scorecard.csv`
- `reports/artifacts/pbo_cscv_honesty_gate/rank137_explicit_three_arm_scorecard_confirm_window_12/rank139_pbo_cscv_dsr_meta.json`
- `reports/artifacts/pbo_cscv_honesty_gate/rank140_explicit_three_arm_family_board.csv`
- `reports/artifacts/pbo_cscv_honesty_gate/rank140_explicit_three_arm_family_board.meta.json`

## 5) 显式三臂结果（Rank 137 / `confirm_window_12`）
对齐结果：
- `baseline = 818`
- `gate_kept = 545`
- `gate_veto = 273`
- `kept:veto = 545:273`

人话解释：
- split 仍然可读，没有掉成极端失衡；
- 相比上一轮的 `confirm12_entry24`，这次 `kept` 更大、`veto` 更少；
- 说明只靠“确认窗口 ≤ 12”这一个约束，就已经把明显更差的一臂切出去了一大块。

## 6) canonical scorecard 结果
### hard read
- `PBO = 0.0000`
- `lambda_median = 0.75`
- `verdict = guard_passed`

### 三臂读数（net 已扣 12bps roundtrip）
- `baseline`：`trades=818`，`mean_net_6bps ≈ -0.0949%`，`sharpe ≈ -0.0700`
- `gate_kept`：`trades=545`，`mean_net_6bps ≈ +0.2549%`，`sharpe ≈ +0.2079`
- `gate_veto`：`trades=273`，`mean_net_6bps ≈ -0.7931%`，`sharpe ≈ -0.5946`
- `kept - veto mean diff ≈ +1.0480%`

### 人话解释
- 这条比上一轮的 `confirm12_entry24` **更强**；
- 不只是 `guard_passed`，而且 `kept` 臂均值/Sharpe 都更高，被 veto 的那一臂也更差；
- 也就是说，`Rank 137` 当前最像真正有用的，不是“entry 再卡到 24 根”这层细化，而是**先把确认窗口收紧到 12 根**这件事本身；
- `entry24` 可能仍有辅助价值，但从当前单 family honesty-layer 读法看，主贡献更像来自 `confirm_window_12`。

## 7) family board 更新后的读法
新增一行：
- `Rank137 / confirm_window_12`：`545:273`，`PBO=0.0000`，`guard_passed`

更新后更清楚的结论：
- `Rank137` 现在已经有 **两条** strict 变体都能 `guard_passed`；
- 其中 `confirm_window_12` 比 `confirm12_entry24` 给出更高的 `kept` 均值和更大的 `kept-veto` 差；
- 这使得 desk 当前对 `Rank 137` 的更诚实读法，不再只是“有一个正例”，而是：**确认窗口约束本身就足以当正例核心，entry latency 更像次级细化项。**

## 8) 本轮 hard verdict / next
- ✅ Run1 合规 `waiting_not_due`，未伪造 refresh。
- ✅ Run2 合规跳过，无 hosted P3 status-changing event。
- ✅ Run3 完成 1 个最小硬交付：`Rank137 / confirm_window_12` 显式三臂 matrix + canonical scorecard，并回写 family board。
- ✅ 首页已刷新：`bash scripts/publish_homepage_index.sh`

## 9) 留给后续 run（本轮不展开）
- 下一轮若继续 `Rank 140`，优先不是再扩 family 数量，而是把 `Rank137` 这两个已过关变体压成一句更硬的 family 结论：**核心 alpha / honesty split 来自 confirm window 还是 entry latency budget**；
- 但本轮不再继续拆 `entry24_only`，避免同轮开第二个紧邻子点；
- 也不要回头重复 Hosted P3 continuity 巡检。