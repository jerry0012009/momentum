# 2026-03-21 02:08 UTC — Rank 137 / state expiry latency budget gate minimal clean replication

## 本轮一句话
先按 desk 规则执行 `EMA due-check first`；结果继续 `waiting_not_due`，于是本轮合法切去 `Scout Seat`，完成 **`Rank 137 / state expiry latency budget gate`** 的唯一那手最小 clean replication。当前更诚实的硬结论不是升格，而是：**`keep_P1`**。

## 先检查了什么
- `git status --short`
  - repo 仍有大量与本轮无关脏文件，继续 **不混提**。
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 返回：当前没有 `due-now / overdue` lane
  - 最近 due：`Crypto 1d+1wk（BTC/ETH/SOL）` 约 `21.9h` 后到点
  - 含义：`EMA` 仍是 `running paper / waiting_not_due`，所以本轮主资源位应切去 `Scout Seat`，不能空转。

## 本轮主点
### 认领对象
- `Rank 137 / state expiry latency budget gate`
- 类型：`P1 / repo-based / clean replication`

### 固定口径
- 资产：`BTC/ETH/SOL perpetual`
- 周期：`15m`
- 执行：`next-bar open`
- 持有：`8 bars`
- 约束：`no-overlap`
- 成本：`6 / 10 / 15 bps per side`
- 三臂：
  1. `baseline_no_expiry`
  2. `confirm_window_12`
  3. `confirm12_entry24`

### 这次怎么把“有时间预算”写成可测规则
不是泛泛地说“别等太久”，而是把它冻结成一套最小状态机：
- `baseline_no_expiry`：signal 后直接下一根开盘进场
- `confirm_window_12`：signal 后最多等 `12` 根 bar 出现 follow-through confirm（这里固定为约 `0.15 ATR` 的继续推进），否则作废
- `confirm12_entry24`：先在 `12` 根内 confirm，再要求之后 `24` 根内出现约 `0.35 ATR` 的 retrace entry，否则作废

这轮重点不是证明这套参数已经成熟，而是先回答：
**“把确认层从无限等待改成有限预算后，是否真能留下更诚实、成本后仍站得住的结果？”**

## 最关键结果（测试集）
### 1) 总表读法 @ 6bps
- `baseline_no_expiry`
  - `328` 笔
  - mean net return ≈ `-16.39 bps/trade`
  - failure ≈ `55.18%`
- `confirm_window_12`
  - `236` 笔，retention ≈ `71.95%`
  - mean net return ≈ `+0.42 bps/trade`
  - `return delta ≈ +16.80 bps/trade`
  - failure ≈ `27.12%`（`-28.06 pct`）
- `confirm12_entry24`
  - `217` 笔，retention ≈ `66.16%`
  - mean net return ≈ `+2.35 bps/trade`
  - `return delta ≈ +18.74 bps/trade`
  - failure ≈ `29.95%`（`-25.23 pct`）

### 2) 成本层结论
- 两个 expiry 变体在 `6bps` 下都显著优于 baseline。
- 但到了 `10 / 15bps`，两者测试集都重新转负。
- 这说明它们更像是 **改善失败率与 stale follow-up honesty 的便宜门**，还不够证明“已经能穿透更严成本”。

### 3) setup / 资产拆解
#### `confirm_window_12`
- 好处：
  - 测试集 `BTC / ETH / SOL` 三资产都转正
  - `breakout_short` 与 `ema_psar_long` 都改善明显
  - failure 压得最干净
- 坏处：
  - `fib_retest_long` 仍然偏弱
  - 到 `10 / 15bps` 仍站不住

#### `confirm12_entry24`
- 好处：
  - 测试集 `6bps` 平均回报更高
  - `breakout_short` 改善最明显
- 坏处：
  - 改善更集中，`ema_psar_long` 在测试集转回略负
  - 成本敏感度更高
  - 入场平均拖到约 `7.2 bars`，比 `confirm_window_12` 的约 `4.2 bars` 更慢

## 当前硬结论
**`Rank 137 / state expiry latency budget gate = keep_P1`**

理由不是它没信息，反而是：
1. **最小 clean replication 已经证明它不是空故事。**
   - 失败率确实大幅下降；
   - retention 仍保有 `66%~72%`，不是极端砍单；
   - baseline 的负读法在 `6bps` 下被拉回到接近零或小幅转正。
2. **但它还不够统一，不足以直接升 `P2`。**
   - 成本一加厚就重新转负；
   - `fib_retest_long` 没跟上；
   - `confirm+entryWindow` 的 uplift 更像集中在局部口袋，不够像 desk 级 shared gate。

## 下一轮最小动作建议
既然本轮已经完成唯一的 minimal clean replication，下一轮不该继续磨 intake / wording。
最值得的只剩 **1 个真正会改变 verdict 的最小检查**：
- 优先方案：对 `confirm_window_12` 做 **cheap time stability**（例如早/中/晚三桶）
- 备选方案：做 **cost / trade-count stability** 小检查

为什么优先 `confirm_window_12`：
- 虽然 `confirm12_entry24` 的平均 delta 更高，
- 但 `confirm_window_12` 在测试集三资产上更均匀，且 entry delay 更短，
- 更适合作为下一轮“升 `P2` 还是直接 `park`”的最小裁决对象。

## 本轮新增产物
- 脚本：`scripts/build_rank137_state_expiry_clean_replication.py`
- artifact：
  - `reports/artifacts/scout_rank137_state_expiry_latency_budget_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank137_state_expiry_latency_budget_15m/setup_summary.csv`
  - `reports/artifacts/scout_rank137_state_expiry_latency_budget_15m/asset_summary.csv`
  - `reports/artifacts/scout_rank137_state_expiry_latency_budget_15m/time_summary.csv`
  - `reports/artifacts/scout_rank137_state_expiry_latency_budget_15m/signal_catalog.csv`
  - `reports/artifacts/scout_rank137_state_expiry_latency_budget_15m/trade_log.csv`
  - `reports/artifacts/scout_rank137_state_expiry_latency_budget_15m/scorecard.csv`
  - `reports/artifacts/scout_rank137_state_expiry_latency_budget_15m/summary.json`
- 网页落点：
  - `reports/site/factors/scout_rank137_state_expiry_latency_budget_15m/report.html`
  - `reports/site/reading/repo_scout/rank137_state_expiry_latency_budget_clean_replication.html`

## 对 desk board 的最小 write-back
- `Scout Seat 当前主点`：改成 `minimal clean replication done / keep_P1`
- `Active Scout 排序`：`Rank 137` 更新为 `next = 1 个最小 stability-style verdict check`
- `Next 3 runs`：改为先做 `EMA due-check`，再给 `Rank 137` 一次最小 `时间稳定性 / 成本-交易数稳定性` 裁决；若仍不过，再回 `fresh intake`
- `最近关键 evidence`：补入本轮 `Rank 137 minimal clean replication = keep_P1`

## 最小验证
已实际执行：
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- `python3 scripts/build_rank137_state_expiry_clean_replication.py`

## 风险 / 边界
- 这轮只是最小 clean replication，不是最终 stability pack。
- 当前 confirm / retrace 的实现仍是项目内的 clean-room proxy，不是外部仓库的逐字照搬。
- 正因为 replication 已显示“有点东西但不够稳”，下一轮更该用一次便宜的 verdict check 快速裁决，而不是继续补近义说明页。

## Commit hash
- 未提交。
- 原因：工作区存在大量与本轮无关脏文件；本轮只做局部脚本、artifact、网页页与顶板 write-back，不适合混提。
