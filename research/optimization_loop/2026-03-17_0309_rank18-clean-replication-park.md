# 2026-03-17 03:09 UTC — Rank 18 EMA 邻域平台 clean replication + park verdict

## 本轮定位（按 TRADING DESK BOARD）
- 先执行 `Run 1` 检查：`Paper Seat = EMA` 仍是 `waiting_not_due`（`--require-due` 返回无 due-now / overdue，约 3.8h 后到点）。
- 按板上优先级自动切到 `Run 2 Scout Seat`。
- 先比较 active Scout 候选边际价值：
  - `Rank 17` 已在 `paper candidate pool`，且刚补完 wiring，当前若无 genuinely verdict-changing 检查不该继续磨；
  - `Rank 2` 属 narrow-paper append/review only；
  - `Rank 18` 当时处于 `source intake / clean replication next`，边际价值最高。

## 本轮主点（1 主点 + 1 紧邻子点）
1. **主点：完成 Rank 18 最小 clean replication + Light Stability Pack**
   - 新增脚本：`scripts/build_ema_plateau_consensus_clean_replication.py`
   - 固定四档比较：
     - `anchor_10_40`
     - `row_consensus_2of3`
     - `plateau_vote_5of9`
     - `plateau_vote_5of9_spread_guard`
   - 固定执行口径：`next-bar open | 1 ATR stop | 2 ATR target | 8-bar time stop | signal_off close`
   - 固定样本：`Binance 120d 15m, BTC/ETH/SOL`（只复用本地缓存，不追新 bar）
   - 诚实守门：
     - trade on/off 规则已冻结在 spec 和实现；
     - 回测仅用当下 bar 的 EMA vote / median spread / ATR，未使用 future label（无显式 lookahead/repaint）。

2. **紧邻子点：同步 desk board 到新 verdict**
   - 更新 `docs/TODO.md`：
     - `Rank 18` 从 `source intake / clean replication next` 改为 `park / evidence pool`；
     - 更新 `当前窗口排班` 与 `Next 3 runs`（新增 `2m`：下一轮默认转 fresh intake，而非继续占用 Rank 18）。

## 最小验证与关键结果
- `python3 scripts/build_ema_plateau_consensus_clean_replication.py` ✅
- 关键产物：
  - `reports/artifacts/scout_ema_plateau_consensus_15m/clean_replication_summary.csv`
  - `reports/artifacts/scout_ema_plateau_consensus_15m/cross_asset_stability.csv`
  - `reports/artifacts/scout_ema_plateau_consensus_15m/parameter_stability.csv`
  - `reports/artifacts/scout_ema_plateau_consensus_15m/cost_trade_stability.csv`
  - `reports/artifacts/scout_ema_plateau_consensus_15m/clean_replication_meta.csv`
  - `reports/site/factors/scout_ema_plateau_consensus_15m/report.html`

### Hard verdict
- **`Rank 18 EMA neighborhood consensus` 当前应读作：`park / evidence pool`，不进入 `paper candidate pool`。**
- 核心证据（6bps/side）：
  - `plateau_vote_5of9_spread_guard`：`mean_total_return ≈ -19.89%`，`positive_asset_ratio = 0/3`，`mean_trades ≈ 157.0`，`mean_no_trade_ratio ≈ 68.48%`
  - 虽相对 `anchor_10_40`（约 `-30.21%`）少亏，但仍全资产为负；
  - 成本梯度 `10/15/20bps` 全线继续恶化（约 `-29.36% / -39.63% / -48.42%`）；
  - 参数邻域（vote/spread 小邻域）没有出现“由负转正”的平台稳定证据。

## 过程异常与修复
- 首次运行 clean replication 脚本时，进程被时间窗 SIGTERM（非逻辑报错）。
- 已将回测核心循环改为更轻的 numpy 访问版本后重跑成功（约 6.3s）。

## 席位影响（本轮后）
- `Paper Seat`: 不变，仍 `EMA waiting_not_due`。
- `Live Seat`: 不变，默认暂空。
- `Scout Seat`: `Rank 18` 已完成快筛并压回 `park`；下一轮默认转 **fresh paper/repo 5m/15m crypto intake**，除非 `Rank 17` 出现 genuinely verdict-changing 检查。

## Git/工作区
- 工作区存在大量与本轮无关脏文件；本轮未做混提提交。
