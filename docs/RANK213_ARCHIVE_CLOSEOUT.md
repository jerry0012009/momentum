# Rank213 age90 Live Canary Archive Close-out

更新时间：2026-05-13 03:16 UTC

## 最终状态

**Rank213 age90 14d skip1d voladj Top50 4x4：ARCHIVED / live canary stopped.**

这次收口针对的是当前真钱 canary：

- 策略：`rank213_age90_14d_skip1d_voladj_top50_4x4`
- 实盘 shell：`rank213_age90_live_canary_shell`
- checklist 页面：<https://jp.jerrypsy.top/momentum/factors/rank213_live_vs_backtest_checklist/report.html>

## 关闭原因

2026 年 5 月 13 日收口前，当前 live artifact 显示：

- `closed_trade_count = 34`
- `closed_basket_count = 5`
- `realized_net_pnl = -20.5406 USDT`
- `open_unrealized_pnl = -1.5836 USDT`
- `snapshot_total_pnl = -22.1241 USDT`

最近已闭合的 5 个 basket 全部为负，属于持续亏损，不再适合继续保留真钱 falsification。

## 实际执行

### 1. 平掉当前真钱持仓

2026-05-13 03:16:11 UTC 提交 reduce-only 市价平仓，6 条当前持仓全部成交：

- `SKYAIUSDT` long `36`，flatten 成交均价 `0.6037567`
- `ENJUSDT` short `398`，flatten 成交均价 `0.04871`
- `ZECUSDT` long `0.032`，flatten 成交均价 `586.53000`
- `SOLUSDT` long `0.2`，flatten 成交均价 `95.080000`
- `ZBTUSDT` short `117`，flatten 成交均价 `0.1665974`
- `ARIAUSDT` short `343`，flatten 成交均价 `0.0592000`

收口回执确认：**`remaining_position_count_after_flatten = 0`**。

### 2. 停掉调度

2026-05-13 03:16:30 UTC，以下 timer 已 `disable --now`：

- `momentum-rank213-age90-live-canary.timer`
- `momentum-rank213-age90-shadow-runner.timer`
- `momentum-rank213-age90-live-pending.timer`

状态：**`timers_disable_status = all_disabled`**。

## 特别说明

收口时本地 shell state 里还残留了 2 条 `pending_entries`：

- `SIRENUSDT`
- `STOUSDT`

它们不是当前仍持有的真钱仓位；实际收口是按交易所当前 open positions 直接 flatten，并在 flatten 后确认剩余仓位为 0。之后再停掉全部 timer，避免这两个本地 pending 状态继续触发任何新动作。

## 当前网页入口

- 实盘透明页：<https://jp.jerrypsy.top/momentum/factors/rank213_live_vs_backtest_checklist/report.html>
- 收口页：<https://jp.jerrypsy.top/momentum/paper/rank213_archive_closeout.html>
- 日频 shadow 页：<https://jp.jerrypsy.top/momentum/paper/rank213_age90_daily_shadow_runner.html>
- evidence map：<https://jp.jerrypsy.top/momentum/paper/rank213_evidence_map.html>

## 关键本地文件

- `docs/RANK213_ARCHIVE_CLOSEOUT.md`
- `scripts/build_rank213_archive_closeout_report.py`
- `scripts/close_rank213_age90_live_canary.py`
- `reports/artifacts/rank213_age90_live_canary_shell/rank213_archive_closeout_receipt.json`
- `reports/site/paper/rank213_archive_closeout.html`

## 后续规则

不要再做：

- 重启 `rank213 age90` live canary timers；
- 让旧 checklist 停留在 4 月旧产物路径；
- 把这次真钱 canary 的历史运行理解成“仍在 active live lane”；
- 在没有新研究假设和新 release gate 的情况下继续加钱或续跑。

当前默认动作：

**Rank213 age90 live canary 已停止并归档；后续如要重启，必须从新的研究假设、独立 gate 和新的透明文档重新开始。**
