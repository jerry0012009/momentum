# 2026-03-21 00:16 UTC — Rank 134 最小 clean replication → park，并把桌面切回 Rank 135 fresh intake

## 本轮先做的桌面检查（按 TRADING DESK BOARD）
- `git status --short`：repo 仍有大量与本轮无关脏文件，继续 **不混提**。
- 先执行 `Run 1 / EMA due-check first`：
  - `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：当前仍无 `due-now / overdue` lane；`Crypto 1d+1wk（BTC/ETH/SOL）` 已回到 `waiting_not_due`，约 `23.8h` 后到点。
  - 备注：脚本按 `require-due` 如实返回非零退出，但已完成守门输出与 report rebuild；本轮据此认定 `Paper Seat = waiting_not_due`，合法切去 `Scout Seat`。
- 再核对顶板：`Rank 134` 已在上一轮完成 `source intake + honesty gate`，因此本轮允许动作是它那 **1 次最小 clean replication**；不回头磨旧 `P1`，也不抢 `P3 continuity`。

## 本轮主点：Rank 134 / cross-market intraday TSMOM lead-lag gate 最小 clean replication

### 新增脚本
- `scripts/build_rank134_crossmarket_leadlag_clean_replication.py`

### 新增 artifact
- `reports/artifacts/scout_rank134_cross_market_intraday_tsmom_leadlag_15m/overall_summary.csv`
- `reports/artifacts/scout_rank134_cross_market_intraday_tsmom_leadlag_15m/asset_summary.csv`
- `reports/artifacts/scout_rank134_cross_market_intraday_tsmom_leadlag_15m/setup_summary.csv`
- `reports/artifacts/scout_rank134_cross_market_intraday_tsmom_leadlag_15m/cost_summary.csv`
- `reports/artifacts/scout_rank134_cross_market_intraday_tsmom_leadlag_15m/trade_log.csv`
- `reports/artifacts/scout_rank134_cross_market_intraday_tsmom_leadlag_15m/scout_promotion_scorecard.csv`
- `reports/artifacts/scout_rank134_cross_market_intraday_tsmom_leadlag_15m/summary.json`

### 新增 reader-facing 页面
- `reports/site/factors/scout_rank134_cross_market_intraday_tsmom_leadlag_15m/report.html`
- `reports/site/reading/repo_scout/rank134_cross_market_intraday_tsmom_leadlag_clean_replication.html`

## 冻结口径（只做最小诚实检查）
- `BTC` 作为 leader，`ETH/SOL` 作为 follower。
- 原有 `entry` 冻结不变：继续沿用当前 scout 常用的 `breakout_short / fib_retest_long / ema_psar_long` 信号框架。
- leader 只使用 **signal 当根及之前** 的 completed bars：
  - `BTC 4-bar return`
  - `BTC 8-bar return`
  - `BTC 4-bar impulse z-score`
- gate 规则固定为：
  - `BTC 4/8 bar` 同向；
  - 与 follower 当根方向一致；
  - `BTC` 幅度至少达到 follower 当根波动的 `0.75x`；
  - `impulse z-score` 落在 `[0.35, 2.20]`；
  - 执行口径统一 `next-bar open + no-overlap + hold 8 bars`。

## 关键结果（test / 6 bps per side）
### 总表
- baseline：`217 trades`，`mean return = +0.26 bps`
- leadlag_gate：`25 trades`，`mean return = +8.42 bps`
- `return delta = +8.16 bps`
- 但 `trade_count_retention = 11.52%`
- 同时 `failure delta = +10.23 pct`（更差，不是更好）

### 分资产
- `ETH`：
  - baseline `-3.70 bps`
  - gate `-33.16 bps`
  - `return delta = -29.46 bps`
  - `failure delta = +11.54 pct`
- `SOL`：
  - baseline `+3.91 bps`
  - gate `+53.48 bps`
  - `return delta = +49.56 bps`
  - `failure delta = +8.78 pct`

### 读法
- 这不是“shared gate 变得更诚实”，而更像：
  1. 主要靠 **大幅缩样本**（只剩 `11.5%` 交易）；
  2. `ETH` 与 `SOL` 表现 **明显分裂**；
  3. 即便总体平均收益抬起来，`failure_before_target` 却更糟。
- 换成人话：它不是稳定的 desk 级 shared gate，更像只在 `SOL` 一侧偶然挑中了更强样本。

## 轻量 scorecard
- `clean_replication_test_return`：`pass`
- `clean_replication_test_failure`：`fail`
- `cross_asset_breadth`：`fail`
- `stability_pack`：`pending`

## 本轮硬结论
**`Rank 134 / cross-market intraday TSMOM lead-lag gate = park / evidence pool`**。

原因不是“完全没任何 uplift”，而是：
- uplift 主要来自 **过度缩样本**；
- `failure` 指标恶化；
- 只有 `SOL` 站住，`ETH` 明显变差；
- 因此不够诚实，不值得升到 `P2`，甚至不该继续占 `P1` 主位。

## 紧邻子点：最小 write-back 到 desk board
已更新 `docs/TODO.md` 顶部：
- `Scout Seat 当前主点` 切回 **`Rank 135 / fresh intake slot（待认领）`**；
- `Active Scout` 里把 `Rank 134` 下放到 `P0 / park / evidence pool`；
- `Next 3 runs` 改为：`Run 2 = Rank 135 source intake + honesty gate`，`Run 3 = Rank 135 guard-pass 后最小 clean replication`；
- `最近关键 evidence` 补入 `Rank 134 clean replication → park` 与本轮最新 `EMA waiting_not_due` 守门结果。

## 验证
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- `python3 scripts/build_rank134_crossmarket_leadlag_clean_replication.py`

## commit
- 未提交。
- 原因：当前工作区存在大量与本轮无关脏文件，不适合做安全 selective commit。
