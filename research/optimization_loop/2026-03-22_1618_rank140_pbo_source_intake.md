# bot3 优化循环日志（2026-03-22 16:18 UTC）

## 本轮执行范围（严格按 Next 3 runs）
- Run 1：EMA due-check first
- Run 2：Hosted P3 continuity（事件驱动）
- Run 3：Scout Seat（仅 1 个主点：Rank 140）

## Run 1 — EMA due-check（已执行）
已执行：
```bash
python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due
```
结果：
- 当前无 `due-now / overdue` lane（脚本 fast-precheck 直接拒绝伪 refresh）
- 最靠前 lane：`Crypto 1d+1wk（BTC/ETH/SOL）`，约 `7.5h` 后到点
- `创业板ETF 1d`、`贵州茅台 1d+1wk` 约 `14.5h` 后到点

结论：
- Paper Seat 当前真实为 `waiting_not_due`
- 按 desk 规则，立即切到 Scout Seat，不空转

## Run 2 — Hosted P3 continuity（事件驱动）
本轮仅做事件触发检查，不做近义健康巡检。

抽查文件（仅用于判断是否出现状态变化事件）：
- `reports/artifacts/scout_rank29_trendline_breakout_navigator_15m/narrow_paper_pilot_monitoring_board.csv`
- `reports/artifacts/scout_rank32b_slope_floor_continuation_15m/narrow_paper_monitoring_board.csv`
- `reports/artifacts/scout_rank122_atr_roc_short_rearm_15m/narrow_paper_monitoring_board.csv`
- `reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/narrow_paper_pilot_monitoring_board.csv`

判断：
- 未发现需要本轮立即接管的**新** `status-changing event`（refresh 失步/ledger 爆雷/open-position 异常）
- 维持“无事件则跳过”口径

## Run 3 — Scout Seat（主点：Rank 140 / pbo-cscv deflated sharpe honesty gate）

### 主点交付：锁定 1 篇权威 source（不扩多候选）
锁定来源：
- Bailey, D. H., Borwein, J., López de Prado, M., & Zhu, Q. J. (2014).
  **The Probability of Backtest Overfitting.**
  Journal of Computational Finance, 20(4), 39–69.
  （CSCV + PBO 的经典来源，用于“回测看起来好但真实可交易性很差”的过拟合识别）

### 紧邻子点（仅 1 个）：人话摘要 + 离线实现锚点
人话版（给 desk 用）：
1. 策略在历史上“挑最优参数”很容易挑到噪声；
2. CSCV 用“多组训练/测试切分”去看：同一策略是否在不同切分里稳定；
3. PBO 给出一个概率：你拿到的“最佳策略”未来更可能翻车还是继续有效；
4. 这层 honesty gate 目标不是找更高回测收益，而是**先拦掉最像过拟合的候选**。

对 Rank 140 的直接落地定义（离线实现锚点）：
- 输入：同一候选在多折/多窗口上的 OOS 指标序列（如 net return / Sharpe）
- 输出：
  - `pbo_estimate`（越高越危险）
  - `cscv_rank_stability`（越低越不稳）
  - `desk_verdict`：`pass / watch / fail`
- 本轮只完成 source intake 与规则冻结；下一轮再做 canonical offline 代码实现。

## 本轮结论
- 已严格执行 Run1→Run2→Run3
- 资源位只打开 1 个 Scout 主点（Rank 140），并只加 1 个紧邻子点
- 未扩新候选、未做近义重复巡检

