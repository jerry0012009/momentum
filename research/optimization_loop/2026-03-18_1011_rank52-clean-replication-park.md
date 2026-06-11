# 2026-03-18 10:11 UTC — Rank 52 / trade-flow imbalance veto 最小 clean replication 完成并压回 park

## 本轮席位判定与认领
- 先读 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 与 `Next 3 bot3 runs`。
- `Run 1 / Paper Seat`：读取 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`，当前 `美股 20:00 UTC / Crypto 03-19 00:00 UTC / A股 03-19 07:00 UTC`，均为 `waiting_not_due`，无 due-now 动作。
- 按板上顺序转 `Run 2 / Scout Seat`：执行 `Rank 52` 唯一允许的一手最小 clean replication（主点）。

## 本轮主动作（1 主点 + 1 紧邻子点）
### 主点：Rank 52 minimal clean replication
- 新增并执行：`scripts/build_rank52_trade_flow_imbalance_clean_replication.py`
- 固定口径：
  - 样本：`BTC/ETH/SOL 120d 15m` cache
  - flow：仅取 signal 前最后 `5` 分钟 `aggTrades` 摘要（主动买卖量失衡）
  - 执行：`next-bar open + no-overlap + hold 8 bars`
  - setup：`ema_pullback_long`、`breakdown_reclaim_short`
  - 变体：`base / same_direction_flow_gate / strong_flow_gate / opposite_flow_veto`
  - 成本：`6 / 10 bps per side`
- 产物：
  - `reports/artifacts/scout_rank52_trade_flow_imbalance_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank52_trade_flow_imbalance_15m/asset_summary.csv`
  - `reports/artifacts/scout_rank52_trade_flow_imbalance_15m/time_pocket_summary.csv`
  - `reports/artifacts/scout_rank52_trade_flow_imbalance_15m/trade_log.csv`
  - `reports/artifacts/scout_rank52_trade_flow_imbalance_15m/signal_windows_with_flow.csv`

### 紧邻子点：reader-facing 与 authoritative write-back
- 页面：
  - `reports/site/factors/scout_rank52_trade_flow_imbalance_15m/report.html`
  - `reports/site/reading/repo_scout/rank52_trade_flow_imbalance_clean_replication.html`
- 已在 `docs/TODO.md` 顶部作战板追加本轮结果与 `Next 3` 回写。

## 核心结果（硬结论）
- 主读法（`breakdown_reclaim_short + opposite_flow_veto @ 6bps`）：
  - `mean_total_return ≈ -2.73%`
  - `positive_asset_ratio = 0/3`
  - `mean_trades ≈ 17.0`
  - `mean_trade_count_retention ≈ 81.90%`
  - `mean_false_break_or_hold_4bars_rate ≈ 85.65%`
- 对照（`ema_pullback_long + opposite_flow_veto @ 6bps`）：
  - `mean_total_return ≈ -4.04%`
  - `mean_trade_count_retention ≈ 57.87%`
- time-pocket（主读法）仍呈中后段负 pocket，未形成可升格的稳定结构。

**Hard verdict：`Rank 52 / trade-flow imbalance veto = park / evidence pool`**。

## 过程异常与修复
- 首次执行遇到 Binance `429 Too Many Requests`。
- 已在脚本中加入 `429` 重试与指数退避（含 `Retry-After` 处理），并成功复跑完成。

## 版本与工作区
- 未提交 git（当前存在大量与本轮无关脏文件，避免混提）。

## 下一轮建议（按板）
- `Run 1 = EMA due-check only`
- 若仍 `waiting_not_due`：`Run 2 = fresh paper/repo intake（按 7.10 从 RECENT_PAPER_SEEDS / quant_digests / validated shortlist 认领 1 条）`
- 若 fresh intake 也 exhausted：`Run 3 = Rank 35b > Rank 16b > tiny-live plumbing`
