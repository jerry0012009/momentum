# 2026-03-20 19:57 UTC — Rank 127 / signal→confirm ATR delta phase gate / minimal clean replication

## 本轮先核对的东西
- repo：`master`；`git status --short | wc -l = 1957`，存在大量与本轮无关的脏文件，**不混提**。
- 最近 optimization loop：最新已留痕是 `2026-03-20 19:40 UTC / Rank 127 source intake + 两条轻量诚实守门`。
- 最近 strategy review：最新是 `2026-03-20 19:19 UTC / strategy review`，当时 authoritative 排班已写死：
  1. `Run 1 = EMA due-check first`
  2. `Run 2 = 若 EMA 仍 waiting_not_due，则给 Rank 127 1 次最小 clean replication`
  3. `Run 3 = 若 Rank 127 clean replication hard-fail / exhausted，则切 Rank 128 source intake`
- `Paper Seat`：这轮再次实际执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`，结果仍是 **`EMA = waiting_not_due`**；当前无 `due-now / overdue` lane，最近 due 约为：美股 `~2 分钟`、Crypto `~4.0 小时`、创业板ETF `~59.0 小时`。
- hosted paper lanes：本轮未出现新的 `P3 status-changing event`，因此不回头占用 continuity 预算。

## 为什么这轮合法主动作仍是 Rank 127
因为当前 run 开始时：
- `EMA` 仍真实处于 `waiting_not_due`；
- `Rank 127` 已在上一轮进入 `guard-passed / admit_to_clean_replication_queue`；
- 顶板最新 `Next 3` 已明确写死这轮只允许给它 **1 次最小 clean replication**；
- 因此不能空转，也不能擅自切去 `Rank 125 / 112 / 111` 或 `tiny-live plumbing`。

## 本轮实际执行
### 1. 新增 clean-room 复刻脚本
- `scripts/build_rank127_signal_confirm_atr_delta_clean_replication.py`

### 2. 冻结实验口径
统一只跑这 1 次最小实验：
- 资产：`BTC/ETH/SOL`
- 周期：`120d 15m`
- 三条 base archetype：`breakout_short` / `fib_retest_long` / `ema_psar_long`
- 执行口径：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`
- 三臂对照：
  - `baseline`
  - `shared_gate`
  - `setup_specific_gate`

### 3. 训练段冻结的规则
#### shared 对照（训练段自动选择）
- 最佳 cheap shared 对照并不是 “mid only” 或 “expanding only”，而是：
  - **`shared = non_expanding`**

#### setup-specific 首轮冻结
- `breakout_short = mid_only`
- `fib_retest_long = expanding_only`
- `ema_psar_long = non_expanding`

#### 训练段 ATR delta 分位阈值
- `global q33 ≈ 0.0394`
- `global q67 ≈ 0.0929`
- per-setup 阈值也单独冻结进 artifact，避免测试段再改口径。

## 测试段硬结果（6 bps / side）
### overall
#### shared_gate（best shared = non_expanding）
- `baseline_trades = 328`
- `variant_trades = 231`
- `trade_count_retention ≈ 70.4%`
- `baseline_return ≈ -6.52 bps`
- `variant_return ≈ -3.62 bps`
- `return_delta ≈ +2.90 bps`
- `baseline_failure ≈ 51.52%`
- `variant_failure ≈ 51.08%`
- `failure_delta ≈ -0.44 pct`

#### setup_specific_gate
- `baseline_trades = 328`
- `variant_trades = 143`
- `trade_count_retention ≈ 43.6%`
- `baseline_return ≈ -6.52 bps`
- `variant_return ≈ -3.99 bps`
- `return_delta ≈ +2.52 bps`
- `baseline_failure ≈ 51.52%`
- `variant_failure ≈ 53.15%`
- `failure_delta ≈ +1.62 pct`

### 分 setup 最关键读法
- **`breakout_short`**：setup-specific `mid_only` 在测试段没有兑现，收益和 failure 都不比 shared 更诚实。
- **`fib_retest_long`**：`expanding_only` 方向上仍有局部信息，但测试样本很薄，不能单靠它抬整条 rank。
- **`ema_psar_long`**：`non_expanding` 仍是相对更像样的保留方向，但并不足以单轮把整条 rank 升格。

### 分资产最关键读法
- **BTC**：setup-specific 基本没提供净增益，failure 还更差。
- **ETH**：shared / setup-specific 都偏弱，setup-specific 也没打出更优优势。
- **SOL**：setup-specific 有局部 uplift，但不足以抵消其它资产上的不稳。

## 硬结论
**`Rank 127 / signal→confirm ATR delta phase gate = keep_P1 / weak candidate / budget used`**。

翻成人话：
- `ATR delta` 不是没信息；
- 但这轮最小 clean replication **没有证明 “setup-specific 明显优于 shared”**；
- 当前最像样的 cheap shared 对照反而是 `non_expanding`，而不是 intake 时预设的“三条线各自分 bucket”；
- 所以这条线暂时不能升到 `P2 / paper candidate`，但也不至于直接判死；更诚实的处理是：
  - 保留为 `P1 weak candidate / evidence_pool`
  - 默认**不再继续打磨** reader-facing 叙事
  - 只有当 bot2 明确点名 1 个真正会改变 verdict 的 follow-up（例如仅单独复查 `breakout_short` 的 mid-pocket 假设）时，才值得再拿预算

## 本轮产物
### artifacts
- `reports/artifacts/scout_rank127_signal_confirm_atr_delta_phase_15m/atr_delta_thresholds.csv`
- `reports/artifacts/scout_rank127_signal_confirm_atr_delta_phase_15m/shared_policy_grid.csv`
- `reports/artifacts/scout_rank127_signal_confirm_atr_delta_phase_15m/signal_catalog.csv`
- `reports/artifacts/scout_rank127_signal_confirm_atr_delta_phase_15m/trade_log.csv`
- `reports/artifacts/scout_rank127_signal_confirm_atr_delta_phase_15m/overall_summary.csv`
- `reports/artifacts/scout_rank127_signal_confirm_atr_delta_phase_15m/setup_summary.csv`
- `reports/artifacts/scout_rank127_signal_confirm_atr_delta_phase_15m/asset_summary.csv`
- `reports/artifacts/scout_rank127_signal_confirm_atr_delta_phase_15m/cost_summary.csv`
- `reports/artifacts/scout_rank127_signal_confirm_atr_delta_phase_15m/summary.json`

### reader-facing
- `reports/site/factors/scout_rank127_signal_confirm_atr_delta_phase_15m/report.html`
- `reports/site/reading/repo_scout/rank127_signal_confirm_atr_delta_phase_clean_replication.html`

### desk write-back
- `docs/TODO.md`（新增 `2026-03-20 19:57 UTC` 顶板执行补充）

## 对 desk 的含义
- `Paper Seat`：不变，仍是 `EMA / running paper / waiting_not_due`（美股 lane 即将到点）
- `Live Seat`：继续暂空
- `Scout Seat`：默认主资源位应切到
  - `Rank 128 = P1 fresh intake next`
  - `Rank 127 = P1 weak candidate / budget used / evidence_pool`
  - `Rank 125 / 112 / 111 = P1 evidence_pool or budget_used`
  - `Rank 126 / 124 / 123 / 121 / 120 / 119 / 118 / 117 / 115 / 114 / 113 = P0 park`
  - `Rank 122 / Rank 2 / Rank 17 / Rank 29 / Rank 32b = P3 hosted continuity only`

## 下一手建议
### 默认顺序
1. **先做 `EMA due-check / real refresh`**（美股 lane 即将 due）
2. 若 refresh 之后 `EMA` 再次回到 `waiting_not_due`：
   - 立刻切 **`Rank 128 / MAX(5m) impulse confirmation tier`** 的 `source intake + 两条轻量诚实守门`
3. 只有当 `Rank 128` 也 guard-pass 且 EMA 仍 waiting_not_due 时：
   - 才给 `Rank 128` 1 次最小 clean replication

### 不建议做的事
- 不继续磨 `Rank 127` 的 admission wording / operator packet / closure-copy
- 不回头继续磨 `Rank 125 / 112 / 111`
- 不拿这轮结果去强行宣称 “ATR delta 一定是 setup-specific superior”
