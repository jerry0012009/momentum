# 2026-03-20 22:58 UTC — Rank 132 / adaptive exhaustion countertrend-leg gate clean replication（park）

## 本轮先检查了什么
- branch：`master`
- repo 脏文件：`git status --short | wc -l = 2179`，仍有大量与本轮无关的脏文件，**不混提**。
- 最近 optimization loop：上一轮已留痕 `2026-03-20 22:37 UTC / Rank 132 source intake + honesty gate passed`。
- desk 顶板 `TRADING DESK BOARD`：authoritative `Next 3` 仍是
  1. `Run 1 = EMA due-check first`
  2. `Run 2 = 若 EMA 仍 waiting_not_due，则给 Rank 132 1 次最小 clean replication`
  3. `Run 3 = 按 Rank 132 clean replication 结果决定 uplift / park / fresh intake fallback`

## Run 1：EMA due-check first
实际执行：
```bash
python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due
```
结果：**`EMA = waiting_not_due`**。
- 当前没有 `due-now / overdue lane`
- 最近到点的是 `Crypto 1d+1wk（BTC/ETH/SOL）`，约 `1.1 小时` 后到点
- `require-due` guard 正常触发（exit code `2`），本轮不能伪造 paper refresh

因此本轮合法主动作必须切到 `Scout Seat`，而不是空转，也不是回头磨 hosted `P3 continuity`。

## 为什么这轮仍然认领 Rank 132
本轮先比较 active Scout 的边际价值：
- `Rank 127 / 125 / 112 / 111` 都已经是 `P1 / budget used / evidence_pool`，继续磨更像 admission wording，不像减少真实 gate；
- hosted `P3`（`Rank 122 / 2 / 17 / 29 / 32b`）当前没有新的 `status-changing event`，且 `EMA = waiting_not_due` 时不该继续吃 continuity 预算；
- `Rank 132` 刚完成 `source intake + honesty gate`，按顶板顺序，本轮正好只配拿 **1 次最小 clean replication**。

所以这轮最诚实的选择，仍然是：**给 `Rank 132` 1 次最小 clean replication，然后立刻做硬 verdict，而不是继续拖在“看起来还行”的 intake 状态。**

## 本轮认领
- 主点：`Rank 132 / adaptive exhaustion countertrend-leg gate` 的 **1 次最小 clean replication**
- 紧邻子点：同步 `Scout Promotion Scorecard`、reader-facing 页面、desk 顶板顺序刷新

## 本轮执行
### 1) 新增 clean-room 脚本
- `scripts/build_rank132_adaptive_exhaustion_clean_replication.py`

### 2) 冻结实验口径
- 资产：`BTC/ETH/SOL perpetual`
- 周期：`15m signal + 5m execution readout`
- base setups：`breakout_short` / `fib_retest_long` / `ema_psar_long`
- 执行口径：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`
- 三臂对照：
  - `baseline`
  - `minor_exhaustion_gate`
  - `strict_exhaustion_tier`
- 成本：`6 / 10 / 15 bps per side`
- 主要指标：
  - `post_cost_expectancy`
  - `sl_first_rate`
  - `mae@4bars`
  - `trade_count_retention`
  - `entry_delay_bars`

### 3) 这次如何把 5m exhaustion 写成可复刻规则
不是去发明反转神谕，而是只在 **signal 当根已完成的最后 3 根 5m bar** 上读一层 countertrend leg 是否已经衰竭：
- 先把 5m return 按交易方向重定向（long 为正、short 为负）
- 读出最近 `3` 根里的：
  - `counter_mag`
  - `counter_count`
  - `response_strength`
  - `response_ratio`
- 用训练段按 setup 冻结三组阈值：
  - `minor_ratio_min`
  - `strict_ratio_min`
  - `min_counter_mag`
- 然后统一测试：
  - `minor_exhaustion_gate`：最近至少有 `1` 次 countertrend，且最后一根 5m 已回到交易方向，并达到 `minor_ratio_min`
  - `strict_exhaustion_tier`：最近至少有 `2` 次 countertrend，再用更高 `strict_ratio_min` 做更严格放行

冻结阈值：
- `breakout_short`：`minor_ratio_min≈1.997`，`strict_ratio_min≈4.957`，`min_counter_mag≈0.000513`
- `fib_retest_long`：`minor_ratio_min≈1.168`，`strict_ratio_min≈2.527`，`min_counter_mag≈0.000696`
- `ema_psar_long`：`minor_ratio_min≈1.106`，`strict_ratio_min≈2.929`，`min_counter_mag≈0.000737`

## 测试段硬结果（6 bps / side）
### overall
#### minor_exhaustion_gate
- `baseline_trades = 326`
- `variant_trades = 83`
- `trade_count_retention ≈ 25.46%`
- `baseline_return ≈ -5.92 bps`
- `variant_return ≈ -37.64 bps`
- `return_delta ≈ -31.72 bps`
- `baseline_sl_first_rate ≈ 50.92%`
- `variant_sl_first_rate ≈ 54.22%`
- `sl_first_delta ≈ +3.30 pct`
- `baseline_mae4 ≈ -0.776%`
- `variant_mae4 ≈ -1.011%`
- `mae4_delta ≈ -0.235 pct`

#### strict_exhaustion_tier
- `baseline_trades = 326`
- `variant_trades = 8`
- `trade_count_retention ≈ 2.45%`
- `baseline_return ≈ -5.92 bps`
- `variant_return ≈ -21.83 bps`
- `return_delta ≈ -15.91 bps`
- `variant_sl_first_rate = 75.00%`
- `sl_first_delta ≈ +24.08 pct`
- `variant_mae4 ≈ -1.151%`
- `mae4_delta ≈ -0.375 pct`

翻成人话：
- `minor gate` 不是“过滤掉坏单后更稳”，而是 **砍掉了大约四分之三的交易，结果还更差**；
- `strict tier` 更糟：几乎把样本砍空，只剩极薄交易，还没有把成本后表现救回来。

## 分 setup 读法（test @ 6bps）
### minor_exhaustion_gate
- `breakout_short`
  - `280 -> 71` 笔，`retention≈25.36%`
  - `return delta ≈ -27.98 bps`
  - `sl_first_delta ≈ -0.37 pct`
- `fib_retest_long`
  - `7 -> 1` 笔，`retention≈14.29%`
  - `return delta ≈ -46.14 bps`
- `ema_psar_long`
  - `39 -> 11` 笔，`retention≈28.21%`
  - `return delta ≈ -55.91 bps`
  - `sl_first_delta ≈ +27.97 pct`

### strict_exhaustion_tier
- `breakout_short`
  - `280 -> 5` 笔，`retention≈1.79%`
  - `return delta ≈ -63.94 bps`
- `fib_retest_long`
  - `7 -> 0` 笔，直接砍空
- `ema_psar_long`
  - `39 -> 3` 笔，表面上单 setup 有 `+43.53 bps`，但样本极薄，且 desk 级完全不够抵消其它 setup 的退化

## 分资产读法（test @ 6bps）
### minor_exhaustion_gate
- `BTC`：`return delta ≈ -3.79 bps`
- `ETH`：`return delta ≈ -90.98 bps`
- `SOL`：`return delta ≈ -9.95 bps`

### strict_exhaustion_tier
- `BTC`：`return delta ≈ -27.06 bps`
- `ETH`：`return delta ≈ -77.31 bps`
- `SOL`：`return delta ≈ +15.30 bps`

读法：
- `SOL` 在 strict tier 上有一点局部亮点；
- 但 `BTC / ETH` 明显拖累，尤其 `ETH` 很差；
- 这不足以把整条线留在默认预算上，更别说 shared gate。

## Scout Promotion Scorecard
- `minor_exhaustion_gate`：`usefulness=0 / time_stability=0 / cost_trade_stability=0 / deployability=0`
  - `hard_fail_flags = too_sparse, post_cost_collapse`
- `strict_exhaustion_tier`：`usefulness=0 / time_stability=0 / cost_trade_stability=0 / deployability=0`
  - `hard_fail_flags = too_sparse, post_cost_collapse`

## 当前硬结论
**`Rank 132 / adaptive exhaustion countertrend-leg gate = P0 / park / evidence pool`**。

翻成人话：
- “回踩腿先走完再放行” 这个想法不算荒谬；
- 但按这轮最小 clean replication，它并没有在 desk 当前三条主线里形成一个诚实、便宜、可共享的 5m follow-up gate；
- 它现在更像 **会把样本砍薄、却没把坏单真正砍掉** 的 gating 方向；
- 所以默认动作不是继续补稳定性包，而是 **直接 park，回到 fresh intake reserve。**

## 本轮产物
### scripts
- `scripts/build_rank132_adaptive_exhaustion_clean_replication.py`

### artifacts
- `reports/artifacts/scout_rank132_adaptive_exhaustion_countertrend_leg_15m/threshold_config.csv`
- `reports/artifacts/scout_rank132_adaptive_exhaustion_countertrend_leg_15m/signal_catalog.csv`
- `reports/artifacts/scout_rank132_adaptive_exhaustion_countertrend_leg_15m/trade_log.csv`
- `reports/artifacts/scout_rank132_adaptive_exhaustion_countertrend_leg_15m/overall_summary.csv`
- `reports/artifacts/scout_rank132_adaptive_exhaustion_countertrend_leg_15m/setup_summary.csv`
- `reports/artifacts/scout_rank132_adaptive_exhaustion_countertrend_leg_15m/asset_summary.csv`
- `reports/artifacts/scout_rank132_adaptive_exhaustion_countertrend_leg_15m/cost_summary.csv`
- `reports/artifacts/scout_rank132_adaptive_exhaustion_countertrend_leg_15m/scorecard.csv`
- `reports/artifacts/scout_rank132_adaptive_exhaustion_countertrend_leg_15m/summary.json`

### reader-facing
- `reports/site/factors/scout_rank132_adaptive_exhaustion_countertrend_leg_15m/report.html`
- `reports/site/reading/repo_scout/rank132_adaptive_exhaustion_countertrend_leg_clean_replication.html`

### desk write-back
- `docs/TODO.md`
  - 把 `Rank 132` 从 `clean replication queue` 改为 `P0 / park / evidence pool`
  - 把 `Scout Seat` 当前主点切回 `fresh intake reserve`
  - 把 `Next 3` 刷成：`EMA due-check -> fresh intake reserve -> guard-pass 后 1 次最小 clean replication`

## 最小验证
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- `python3 scripts/build_rank132_adaptive_exhaustion_clean_replication.py`
- 回读：
  - `reports/artifacts/scout_rank132_adaptive_exhaustion_countertrend_leg_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank132_adaptive_exhaustion_countertrend_leg_15m/setup_summary.csv`
  - `reports/artifacts/scout_rank132_adaptive_exhaustion_countertrend_leg_15m/asset_summary.csv`
  - `reports/artifacts/scout_rank132_adaptive_exhaustion_countertrend_leg_15m/scorecard.csv`
  - `reports/site/factors/scout_rank132_adaptive_exhaustion_countertrend_leg_15m/report.html`
  - `docs/TODO.md`

## 风险 / 边界
- 这轮只做了最小 clean replication，没有继续做 Light Stability Pack——因为 clean replication 已经足够给出 `park` verdict。
- `Rank 132` 不是“逻辑错误”，而是 **以当前 frozen 口径没形成 shared default gate**；如果未来只想单独复查 `ema_psar_long + SOL` 这种更窄 pocket，必须另开更诚实的窄问题，而不是拿现在这条 rank 继续续命。
- 当前 `EMA = waiting_not_due`，且 hosted `P3 continuity` 没有真实 `status-changing event`，所以下一轮默认优先动作应是 `fresh intake`，不是继续磨 `P3 continuity`。

## Commit hash
- 未提交。
- 原因：repo 工作区仍有大量与本轮无关的既有脏文件，这轮不适合做安全 selective commit。
