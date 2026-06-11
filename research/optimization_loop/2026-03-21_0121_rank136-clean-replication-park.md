# 2026-03-21 01:21 UTC — Rank 136 / phase-wide RSI memory retest gate / minimal clean replication = park

## 本轮一句话
先按 desk 规则执行 `EMA due-check first`；结果继续 `waiting_not_due`，因此本轮主动作落在 **`Rank 136 / phase-wide RSI memory retest gate` 的 1 次最小 clean replication**。硬结论：**`park`**。

## 先检查了什么
- branch：`master`
- repo：仍有大量与本轮无关脏文件，继续 **不混提**。
- 顶板 authoritative `Next 3`：
  1. `Run 1 = EMA due-check first`
  2. `Run 2 = 若 EMA 仍 waiting_not_due，则执行 Rank 136 最小 clean replication`
  3. `Run 3 = 若 Rank 136 不通过，则回 fresh intake`
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 返回：当前无 `due-now / overdue` lane
  - 最近 due：`Crypto 1d+1wk（BTC/ETH/SOL）` 约 `22.6h` 后到点
  - 说明：该命令在 `require-due` 下正常用 `exit code 2` 表示“还没到点，不做伪 refresh”；不是故障。

## 为什么这轮仍合法认领 Rank 136
- `EMA` 真实仍是 `waiting_not_due`
- `Rank 136` 上一轮已完成 `source intake + honesty gate`
- 顶板已写死这轮就给它 **1 次** 最小 clean replication
- 因此不能空转，也不能擅自插队去做 `P3 continuity` 或 tiny-live plumbing

## 本轮动作
### 新增脚本
- `scripts/build_rank136_phase_wide_rsi_clean_replication.py`

### 固定实验口径
- 资产：`BTC/ETH/SOL`
- 周期：`15m`
- 数据：本地 cache（优先 `120d`）
- 三条 base archetype：
  - `breakout_short`
  - `fib_retest_long`
  - `ema_psar_long`
- 执行口径：`signal 当根及之前数据 + next-bar open + 按资产 no-overlap + hold 8 bars`
- gate 定义：
  - long：最近 `7` 根 completed bars（含 signal bar）的 `min RSI >= 55`
  - short：最近 `7` 根 completed bars（含 signal bar）的 `max RSI <= 44`
- 对照：只比较
  - `baseline`
  - `phase_gate`
- 成本：`6 / 10 / 15 bps`

### 生成产物
- `reports/artifacts/scout_rank136_phase_wide_rsi_memory_15m/signal_catalog.csv`
- `reports/artifacts/scout_rank136_phase_wide_rsi_memory_15m/trade_log.csv`
- `reports/artifacts/scout_rank136_phase_wide_rsi_memory_15m/overall_summary.csv`
- `reports/artifacts/scout_rank136_phase_wide_rsi_memory_15m/setup_summary.csv`
- `reports/artifacts/scout_rank136_phase_wide_rsi_memory_15m/asset_summary.csv`
- `reports/artifacts/scout_rank136_phase_wide_rsi_memory_15m/cost_summary.csv`
- `reports/artifacts/scout_rank136_phase_wide_rsi_memory_15m/scorecard.csv`
- `reports/artifacts/scout_rank136_phase_wide_rsi_memory_15m/summary.json`
- `reports/site/factors/scout_rank136_phase_wide_rsi_memory_15m/report.html`
- `reports/site/reading/repo_scout/rank136_phase_wide_rsi_memory_clean_replication.html`

## 结果 / 硬结论
## authoritative verdict
**`Rank 136 / phase-wide RSI memory retest gate = park`**。

翻成人话：
- 这条线不是“稍弱但可留 P1”，而是这次最小 clean replication 已经足够说明：
  **phase-wide RSI memory 作为 shared gate 在当前口径下会砍掉太多交易，却没有换来更诚实的 post-cost 结果。**
- 所以它不该继续占 Scout fast lane，也不值得再拿默认预算做稳定性包。

## 关键结果
### overall（6 bps / side）
- `baseline_trades = 1015`
- `gate_trades = 243`
- `trade_count_retention ≈ 23.9%`
- `baseline_return ≈ -15.60 bps`
- `gate_return ≈ -20.30 bps`
- `return_delta ≈ -4.69 bps`
- `baseline_failure ≈ 53.79%`
- `gate_failure ≈ 57.20%`
- `failure_delta ≈ +3.41 pct`

### 分 setup 读法
1. `breakout_short`
   - `retention ≈ 25.8%`
   - `return delta ≈ -4.38 bps`
   - `failure delta ≈ +2.93 pct`
   - 读法：本来最该受益的一腿反而明显变差，shared gate 站不住。

2. `ema_psar_long`
   - `retention ≈ 14.7%`
   - `return delta ≈ -8.45 bps`
   - `failure delta ≈ +11.87 pct`
   - 读法：不仅更稀，还更差，直接说明这层 gate 不适合作为三线共享过滤器。

3. `fib_retest_long`
   - `baseline_trades = 25`
   - `gate_trades = 0`
   - 读法：直接把这条 setup 全砍没，说明 shared 性不足，不该继续包装成 desk 级通用层。

### 分资产读法
- `BTC`：`return delta ≈ -6.39 bps`、`failure delta ≈ +6.83 pct`
- `ETH`：`return delta ≈ +2.48 bps`、`failure delta ≈ -4.83 pct`
- `SOL`：`return delta ≈ -9.20 bps`、`failure delta ≈ +6.97 pct`

最诚实的读法：
- 只有 `ETH` 这一口袋有一点点改善；
- `BTC/SOL` 两边都明显恶化；
- 当前结论更像 **single-pocket dependency**，不配继续留在 shared Scout 主位。

### 成本读法
- `6bps`: `return delta ≈ -4.69 bps`
- `10bps`: `return delta ≈ -4.69 bps`
- `15bps`: `return delta ≈ -4.68 bps`

这说明问题不是“成本再高一点才穿帮”，而是 **在最小 clean replication 这一步就已经没证明出基本诚实性**。

## Scout Promotion Scorecard
- `usefulness = 0`
- `cross_asset_stability = 1`
- `cost_trade_stability = 0`
- `deployability = 0`
- `hard_fail_flags = too_sparse, single_pocket_dependency, post_cost_collapse`
- `recommended_action = park`

## 对 desk 的直接影响
- `Paper Seat`：不变，仍是 `EMA / running paper / waiting_not_due`
- `Live Seat`：继续暂空
- `Scout Seat`：`Rank 136` 不再占主位，默认回到 **fresh intake next**
- 当前更诚实的排序应是：
  1. `fresh intake next`
  2. `Rank 127 / 125 / 112 / 111` 作为 `budget used / evidence_pool`
  3. `P3 continuity` 继续 sidecar only
  4. `Rank 136` 归入 `P0 / park`

## 本轮最小 write-back
- 更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：
  - `Scout Seat 当前主点` 改成 `fresh intake next`
  - `Rank 136` 从 active P1 移到 `P0 / park`
  - `Next 3` 改成：
    - `Run 1 = EMA due-check first`
    - `Run 2 = 若 EMA 仍 waiting_not_due，则回 fresh intake next`
    - `Run 3 = 若新 intake guard-pass，则只给 1 次最小 clean replication；否则才允许 tiny-live fallback`

## 最小验证
已实际执行：
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- `python3 scripts/build_rank136_phase_wide_rsi_clean_replication.py`
- 回读：
  - `reports/artifacts/scout_rank136_phase_wide_rsi_memory_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank136_phase_wide_rsi_memory_15m/setup_summary.csv`
  - `reports/artifacts/scout_rank136_phase_wide_rsi_memory_15m/asset_summary.csv`
  - `reports/artifacts/scout_rank136_phase_wide_rsi_memory_15m/scorecard.csv`
  - `docs/TODO.md`

## 风险 / 边界
- 这轮只是最小 clean replication，不是完整策略复盘；
- 但对于 `shared gate 是否值得继续` 这个问题，当前证据已经够硬；
- 因此按 desk 预算，更诚实的动作不是再补 stability，而是 **直接 park，回 fresh intake**。

## Commit hash
- 未提交。
- 原因：工作区存在大量与本轮无关脏文件；本轮只做局部脚本、产物、reader-facing 页面与 board write-back，不适合混提。
