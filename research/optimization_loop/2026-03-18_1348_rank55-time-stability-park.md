# 2026-03-18 13:48 UTC — Rank 55 time stability check -> park

## Context
- 先按 `TRADING DESK BOARD` 检查 `Run 1`：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍显示全 desk 没有新的 `due-now / overdue` lane。
- 当前 `Paper Seat / EMA = running paper / waiting_not_due`，因此本轮合法主动作是 `Run 2 = Rank 55 / order-imbalance crash-risk overlay` 的那 1 次便宜时间稳定性检查。
- 本轮没有回头认领 `P3 continuity`；`Live Seat` 继续空席。

## Repo / workspace state
- `git status --short` 显示工作区里有大量与本轮无关的既有脏文件与未跟踪产物；本轮只增量触碰：
  - `docs/TODO.md`
  - `scripts/build_rank55_time_stability_check.py`
  - `reports/artifacts/scout_rank55_order_imbalance_crash_risk_15m/time_stability_window_summary.csv`
  - `reports/artifacts/scout_rank55_order_imbalance_crash_risk_15m/time_stability_verdict_summary.csv`
  - `reports/site/factors/scout_rank55_order_imbalance_crash_risk_15m/time_stability_check.html`
  - 本日志文件
- 因存在大量无关脏文件，本轮不做 commit。

## What I did
1. 再次核对 `EMA` due guardrail，确认仍是 `waiting_not_due`。
2. 复用 `Rank 55` 现有 `trade_log.csv / overall_summary.csv`，写了轻量脚本 `scripts/build_rank55_time_stability_check.py`。
3. 将每个 `asset × setup × variant` 按时间顺序切成 `3` 个等样本窗口，输出：
   - `reports/artifacts/scout_rank55_order_imbalance_crash_risk_15m/time_stability_window_summary.csv`
   - `reports/artifacts/scout_rank55_order_imbalance_crash_risk_15m/time_stability_verdict_summary.csv`
4. 生成 reader-facing 页面：
   - `reports/site/factors/scout_rank55_order_imbalance_crash_risk_15m/time_stability_check.html`
5. 把新 hard verdict 写回 `docs/TODO.md`。

## Key findings
- `breakout_short` 三个变体在三个时间窗口里全部非正，说明 overlay 没有稳定救回 short archetype。
- `fib_retest_long` 只剩零碎、贴近噪音的小幅正窗口，不足以诚实升格。
- 唯一三段窗口都为正的是 `ema_psar_long + binary_crash_gate`，但它仍只在单一 archetype 上成立，且每桶平均 trades 只有约 `1.7~2.7`。

## Hard verdict
- `Rank 55 / order-imbalance crash-risk overlay = park / evidence pool`
- 理由：作为 **shared crash-risk overlay**，它没有在跨 setup 层面给出足够稳定、可迁移的改善；剩下的仅是 `EMA/PSAR long` 上一个偏薄的 pocket，不配升到 `P2 / paper candidate`。

## Desk consequence
- `Rank 55` 的那 1 次 `P1` 便宜诚实检查预算已经用完。
- 下一轮若 `EMA` 仍是 `waiting_not_due`，默认顺序应重置为：
  - `Run 1 = EMA due-check only`
  - `Run 2 = fresh paper/repo intake（按 7.10 先查 RECENT_PAPER_SEEDS / quant_digests / validated shortlist）`
  - `Run 3 = 若 fresh intake 仍 exhausted，再比较 Rank 35b > Rank 16b > tiny-live plumbing`

## Validation
- `python3 scripts/build_rank55_time_stability_check.py`
- 快读校验输出 CSV 与 HTML 已生成。

## Reader-facing artifacts
- `reports/site/factors/scout_rank55_order_imbalance_crash_risk_15m/time_stability_check.html`
- `reports/artifacts/scout_rank55_order_imbalance_crash_risk_15m/time_stability_window_summary.csv`
- `reports/artifacts/scout_rank55_order_imbalance_crash_risk_15m/time_stability_verdict_summary.csv`
