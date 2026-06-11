# 2026-03-18 04:02 UTC — Rank 27b ATR 回踩区 + bounce reclaim 最小诚实检查

## 本轮上下文
- 先读 `TRADING DESK BOARD` 后，`Run 1 / EMA` 仍是 `waiting_not_due`。
- 依据上一轮 authoritative 顺序：`Rank 27b > Rank 35b > Run 3`。
- 本轮只认领 1 个主点：`Rank 27b` 的唯一一次便宜诚实检查（P1 预算）。

## 主点（Scout Seat）
- 候选：`Rank 27b`（来自 `Rank 27` 的单轴派生）
- 单轴改写：
  - 原：`neckline_confirm_plus_retest_hold`（静态 retest_hold）
  - 新：`ATR 弹性回踩区 + bounce reclaim`
- 固定执行口径：
  - `BTC/ETH/SOL 120d 15m` cache
  - `next-bar open`
  - `1 ATR stop + 2 ATR target + 8-bar time stop`
  - `no-overlap`
  - 成本 `6/10/15/20 bps per side`

## 产物
- 新脚本：
  - `scripts/build_rank27b_atr_zone_bounce_check.py`
- 新 artifact：
  - `reports/artifacts/scout_rank27b_atr_zone_bounce_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank27b_atr_zone_bounce_15m/asset_summary.csv`
  - `reports/artifacts/scout_rank27b_atr_zone_bounce_15m/time_stability.csv`
  - `reports/artifacts/scout_rank27b_atr_zone_bounce_15m/meta.csv`
- reader-facing：
  - `reports/site/factors/scout_rank27b_atr_zone_bounce_15m/report.html`
- board writeback：
  - `docs/TODO.md`（新增 04:02 补充，并把窗口段落更新到 04:10 authoritative）

## 结果（6bps/side）
- `raw_breakout`：`mean_total_return≈-13.79%`，`positive_asset_ratio=0/3`，`mean_false_break_ratio≈71.56%`，`mean_trades≈109.0`
- `neckline_confirm_plus_retest_hold`：`mean_total_return≈-3.03%`，`positive_asset_ratio=0/3`，`mean_false_break_ratio≈68.67%`，`mean_trades≈36.0`
- `atr_zone_bounce_reclaim`（本轮主臂）：
  - `mean_total_return≈-3.14%`
  - `positive_asset_ratio≈33.33%`
  - `mean_false_break_ratio≈58.42%`
  - `mean_trades≈66.3`

## Light Stability Pack（本轮最小只做 1 项）
- 时间稳定性（主臂）：
  - `bucket_1≈-2.72% / positive_asset_ratio=0/3`
  - `bucket_2≈-2.00% / positive_asset_ratio=0/3`
  - `bucket_3≈+1.59% / positive_asset_ratio=1/3`

## Hard verdict
- **`park / evidence pool`**
- 原因（直白）：
  - ATR 回踩区改写确实把 `false_break_ratio` 压低了（相对 raw、相对 retest_hold）。
  - 但成本后仍未形成可保留的跨资产正收益结构（仅 `1/3` 资产为正，且前两个时间桶仍为负）。
  - 所以它不配继续占默认 Scout 预算。

## 对下一轮排班的影响
- `Rank 27b` 本轮预算用尽并压回 evidence pool。
- 若 `EMA` 仍 `waiting_not_due`，默认顺序转为：
  - `Rank 35b > Run 3 / tiny-live plumbing`

## 验证
- 脚本执行成功，退出码 `0`。
- 已确认站点页面存在：`scout_rank27b_atr_zone_bounce_15m/report.html`。
- 已确认 TODO 写回存在：`最新补充（2026-03-18 04:02 UTC）` 与 `当前窗口排班（2026-03-18 04:10 UTC）`。
