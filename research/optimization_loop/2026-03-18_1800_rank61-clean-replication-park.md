# 2026-03-18 18:00 UTC — Rank 61 minimal clean replication：lower-TF volume-delta polarity mismatch 压回 park

## 为什么这轮轮到它
- 先按 `TRADING DESK BOARD` 执行 `Run 1`：重新核对 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`，当前仍无新的 `due-now / overdue` lane：
  - 美股 `1d+1wk -> 2026-03-18 20:00 UTC`
  - Crypto `1d+1wk -> 2026-03-19 00:00 UTC`
  - A 股三条 lane `-> 2026-03-19 07:00 UTC`
- 同时检查 `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`：最新一次仍是 `new_closed_trades_appended=0`，当前不构成比 fresh Scout 主线更高优先级的 `P3` 抢占理由。
- `docs/TODO.md` 顶板在上一轮已把 `Rank 61 / lower-TF volume-delta polarity mismatch veto` 冻结为 `guard-passed / admit_to_clean_replication_queue`，因此这轮合法主动作就是它那唯一一手最小 clean replication。

## 开轮检查（repo / 最近 runs / 脏文件 / 当前席位）
- repo 状态：工作区仍有大量与本轮无关的既有脏文件和未跟踪产物，本轮不做混提 commit。
- 最近 optimization runs：
  - `2026-03-18_1740_rank61-source-intake.md`
  - `2026-03-18_1722_rank60-clean-replication-park.md`
  - `2026-03-18_1656_rank60-source-intake.md`
- 当前席位：
  - `Paper Seat = EMA`：`running paper / waiting_not_due`
  - `Live Seat`：暂空
  - `Scout Seat`：本轮主资源位 = `Rank 61` minimal clean replication

## 本轮主点
完成 **`Rank 61 / lower-TF volume-delta polarity mismatch veto`** 的唯一那手最小 clean replication，并直接给出 hard verdict。

## 本轮冻结口径
- 主图固定：`BTC/ETH/SOL 120d 15m` 本地 cache。
- 三条最小 archetype：`ema_psar_long`、`fib_retest_long`、`breakout_short`。
- 子周期 proxy：Binance Futures public `1m` klines，只抓 **setup 前最后 `5` 分钟**。
- delta 定义固定成：`sub close > open` 记正量、`sub close < open` 记负量；不引入入场后 volume，也不引入 repo 里其它 kitchen-sink 组件。
- 四臂固定为：
  - `base`
  - `same_direction_gate`
  - `opposite_delta_veto`
  - `strong_same_direction_only`
- 执行统一冻结到：`next-bar open + no-overlap + hold 8 bars`。

## 结果摘要（6bps/side）
### 主读法：`ema_psar_long + opposite_delta_veto`
- `mean_total_return ≈ -3.60%`
- `positive_asset_ratio ≈ 33.33%`
- `mean_trades ≈ 13.3`
- `trade_count_retention ≈ 38.10%`
- `false_break_or_hold_4bars_rate ≈ 85.66%`

### 对照读法
- `fib_retest_long + opposite_delta_veto`
  - `mean_total_return ≈ +0.71%`
  - `positive_asset_ratio ≈ 66.67%`
  - `mean_trades ≈ 4.0`
  - `trade_count_retention ≈ 36.36%`
  - `false_break_or_hold_4bars_rate ≈ 76.67%`
- `breakout_short + opposite_delta_veto`
  - `mean_total_return ≈ -3.28%`
  - `positive_asset_ratio ≈ 0.00%`
  - `mean_trades ≈ 16.7`
  - `trade_count_retention ≈ 82.50%`
  - `false_break_or_hold_4bars_rate ≈ 85.96%`

## 硬结论
- **`Rank 61 / lower-TF volume-delta polarity mismatch veto = park / evidence pool`**。
- 更直白地说：这层 lower-TF delta polarity 作为 shared veto 有一点直觉味道，但当前改善没有形成足够诚实的跨 setup / 跨资产增量：
  - `EMA` 主读法没有被救活，反而在明显砍样本后仍维持负收益；
  - `Fib` 只留下一个很薄的正 pocket，更像轻微样本筛选而不是可部署 confirmation；
  - `breakout_short` 也没有被修好。
- 因此它不配继续占 `Scout Seat` 默认主资源位，更不配向 `paper candidate` 升格。

## 本轮产物
### artifact
- `reports/artifacts/scout_rank61_volume_delta_polarity_veto_15m/signal_windows_with_subtf_delta.csv`
- `reports/artifacts/scout_rank61_volume_delta_polarity_veto_15m/trade_log.csv`
- `reports/artifacts/scout_rank61_volume_delta_polarity_veto_15m/asset_summary.csv`
- `reports/artifacts/scout_rank61_volume_delta_polarity_veto_15m/overall_summary.csv`
- `reports/artifacts/scout_rank61_volume_delta_polarity_veto_15m/time_pockets.csv`
- `reports/artifacts/scout_rank61_volume_delta_polarity_veto_15m/meta.csv`

### reader-facing 落点
- `reports/site/factors/scout_rank61_volume_delta_polarity_veto_15m/report.html`
- `reports/site/reading/repo_scout/rank61_volume_delta_polarity_veto_clean_replication.html`

### authoritative writeback
- 已更新 `docs/TODO.md` 顶部 `Next 3 bot3 runs`，把 `Rank 61` 的 clean replication 结果冻结为 `park / evidence pool`。

## 下一轮含义
- `Rank 61` 已退出 active Scout fast-lane。
- 若下一轮 `EMA` 仍是 `waiting_not_due`，默认应转去比较 **`continuation fail-fast overlay > pullback-quality / CQI`**；只有这一层也 exhausted 时，才回退到 `Rank 35b > Rank 16b > tiny-live plumbing`。
- 当前不应再继续围着 `Rank 61` 做 intake wording、补同义说明，或把它误写成可升格候选。

## 最小验证
- 已确认脚本通过：`python3 -m py_compile scripts/build_rank61_volume_delta_clean_replication.py`
- 已实际执行：`python3 scripts/build_rank61_volume_delta_clean_replication.py`
- 已确认产物存在：
  - `reports/artifacts/scout_rank61_volume_delta_polarity_veto_15m/overall_summary.csv`
  - `reports/site/factors/scout_rank61_volume_delta_polarity_veto_15m/report.html`
- 已确认 `docs/TODO.md` 顶板写回包含 `2026-03-18 17:59 UTC` 的 `Rank 61 minimal clean replication` 补充。

## Commit hash
- 未提交。
- 原因：工作区仍有大量与本轮无关的既有脏文件和未跟踪产物，当前不适合做安全 selective commit。
