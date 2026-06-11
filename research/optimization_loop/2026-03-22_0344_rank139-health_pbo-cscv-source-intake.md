# bot3 auto optimization loop — 2026-03-22 03:44 UTC

## 主点：Run2 / Scout Seat — Rank 139(P3) narrow paper pilot 低频健康检查

### Run1 / EMA due-check（守门结果）
- 执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：**无 `due-now / overdue` lane**（exit code=2 属于预期）。
- 最近 3 条 lane（按 guard 输出）：
  - `Crypto 1d+1wk（BTC/ETH/SOL）`：`waiting_not_due`，约 **20.2 小时**后到点
  - `创业板ETF 1d`：`waiting_not_due`，约 **27.2 小时**后到点
  - `贵州茅台 1d+1wk`：`waiting_not_due`，约 **27.2 小时**后到点
- 结论：Paper Seat 本轮**真实 waiting_not_due**，按顶板规则切到 Scout Seat，不做伪 refresh。

### Run2 / Rank 139 pilot ops 可见性
- 监控文件（mtime）：
  - `reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/narrow_paper_pilot_monitoring_board.csv`（**2026-03-22 02:32 UTC**）
  - `.../narrow_paper_pilot_refresh_clock.json`（`generated_at_utc=2026-03-22 02:32 UTC`）
- 当前 policy（来自 refresh_clock）：
  - `thr_mult=0.8`
  - `arm=confirm_same_dir_only`

### 关键健康指标（monitoring_board 摘要）
> 目前 board 只有 9 行（BTC/ETH/SOL × 3 setups），字段齐全。

- **no_event_timeout_rate**：
  - 区间约 **5.6% ~ 27.8%**（最低：ETH ema_psar_long 5.6%）
  - 备注：没有出现“异常高到影响可交易性”的单点爆雷，但仍需后续用时间序列观察是否持续抬升。

- **retention（kept/base）**：
  - 区间约 **11.8% ~ 50.0%**
  - 典型值（几条对比）：
    - SOL breakout_short：50.0%
    - ETH ema_psar_long：44.4%
    - BTC ema_psar_long：11.8%（偏低，但 kept 后 mean_net 转正）

- **mean_net_kept@6bps（仅 kept trades）**：
  - 正向较明显：
    - SOL ema_psar_long：**+0.032965**
    - ETH ema_psar_long：**+0.009122**
    - ETH fib_retest_long：**+0.010340**
  - 仍为负的 setup（需要继续盯住，不做额外研究发散）：
    - BTC breakout_short：-0.006127
    - ETH breakout_short：-0.003240

### Run2 hard verdict
- **ops 维持正常**：refresh clock 在跑、CSV 在更新、字段包含 `no_event_timeout_rate`，符合“可运行监控”的目标。
- 本轮不追加近义研究/对比，只记录现状；下一次低频检查可优先关注：
  1) `no_event_timeout_rate` 是否持续上升；
  2) breakout_short（BTC/ETH）是否持续拖累 kept 的 mean_net。

---

## 紧邻子点：Run3 / pbo-cscv honesty gate — source intake（锁 1 篇权威参考 + 人话摘要）

### 目标（为什么现在做它）
- 当前 Scout Seat 已把 Rank139 推到“可跑监控”，这类 P3 线不再允许继续研究化磨损；因此 Run3 只做 **1 个小交付**：给 `pbo-cscv / deflated sharpe honesty gate` 补齐最小 source intake（作为后续 minimal implementation 的依据）。

### 权威参考（先锁 1 篇）
- **Bailey, Borwein, López de Prado, Zhu (2016)**
  - *The Probability of Backtest Overfitting*（PBO）
  - 核心：当你在很多候选/参数里“挑最好的”，回测表现会系统性被高估；PBO 给出“你挑到的最优策略其实是过拟合”的概率估计。

### 人话摘要（给后续工程化落地用）
- **PBO 想解决的问题**：
  - 你做了很多参数/策略试验，然后选了 Sharpe/CAGR 最好的那个。这个“最好”很可能只是样本噪音加成。
- **CSCV 的直觉**：
  - 把历史切成多段（多个组合的 train/test 切法），在 train 上选“赢家”，再看这些赢家在 test 上排名是否还能靠前；
  - 如果 test 上经常掉到后排，说明你挑出来的“最优”很可能是过拟合。
- **落地到 momentum scout 的用法（下一步候选）**：
  - 在现有 scout scorecard（按 arm/variant）旁边加 1 个字段：`pbo_risk_flag` 或 `pbo_estimate`（先做粗分层也行），用于把“靠筛出来的高 Sharpe”打折处理。

### next step（留给下一轮，只做 1 件事）
- 二选一：
  1) **minimal implementation**：在某个固定的 scorecard 输出里加一列 `deflated_sharpe` / `pbo_risk_flag`（先做最小可见落点）；
  2) 或再补 1 篇 deflated Sharpe/DSR 的参考，但必须确保不占用主资源、且不同时打开多个候选。
