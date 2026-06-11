# 2026-03-20 06:52 UTC — Rank 111 / abnormal-return event clock follow-up gate clean replication（keep_P1 / honest signal, not P2）

## Run 1 -> Run 2 执行
- Run 1：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：`EMA = waiting_not_due`
  - 当前没有 `due-now / overdue` lane
  - 最近 due：`A股三条 lane -> 2026-03-20 07:00 UTC`（约 `15m`）
  - `require-due` guard 正常触发（exit code `2`），没有伪造 refresh
- 因此按当前 `TRADING DESK BOARD` 的 authoritative `Next 3`，本轮合法主动作只能继续落在 `Scout Seat`，且只允许给 **`Rank 111 / abnormal-return event clock follow-up gate`** 做那 1 次最小 clean replication。

## 开轮检查
- branch：`master`
- repo 脏文件：`git status --short | wc -l = 1694`
- 最近 optimization logs：
  - `2026-03-20_0624_rank111-event-clock-intake.md`
  - `2026-03-20_0614_rank110-time-stability-park.md`
  - `2026-03-20_0540_rank110-clean-replication.md`
- 最近 strategy review：`2026-03-20_0617_strategy-review.md`
- 当前席位直读：
  - `Paper Seat = EMA / running paper / waiting_not_due`
  - `Live Seat = 暂空`
  - 本轮前 `Scout Seat = Rank 111 / abnormal-return event clock follow-up gate`
- `manual_narrow_paper_last_run_summary.json @ 2026-03-20T06:30:06Z` 仍是 `new_closed_trades_appended=0`，当前没有新的 `P3 status-changing event` 可以插队。

## Active Scout 候选边际比较（先比较后认领）
1. **`Rank 111 / abnormal-return event clock follow-up gate`**
   - 上轮已完成 `source intake + 两条轻量诚实守门`，这轮只差那 1 次最小 clean replication。
   - 它直接回答 desk 当前最缺的一件事：`冲击后还能追多久` 能不能被写成诚实的 `follow-up / timeout gate`。
2. **`basis dislocation short veto reserve`**
   - 仍是下一顺位，但第一手 honest test 需要先补 `basis / OI` plumbing，因此当前摩擦高于先把 `Rank 111` 的最小 replication 跑完。
3. **`alpha-beta abstain / profit-window reserve`**
   - 仍保留为第二后备，但它先天带着 `forward label -> ex-ante translation` 风险，当前不该越过 `Rank 111`。
4. **旧 `P1 evidence_pool` / `P3 continuity` / `tiny-live plumbing`**
   - 当前都不该挤掉这轮 queue-facing Scout 主链。

结论：本轮只认领 `Rank 111` 的最小 clean replication，不并开 basis / alpha-beta，也不回头磨 `P3 continuity`。

## 本轮认领
- 主点：`Rank 111 / abnormal-return event clock follow-up gate` 的 **1 次最小 clean replication**
- 紧邻子点：同步 reader-facing 落点、顶板顺序刷新

## 本轮动作
- 新增脚本：`scripts/build_rank111_event_clock_clean_replication.py`
- 执行：`python3 scripts/build_rank111_event_clock_clean_replication.py`
- 统一冻结：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars + 6bps/side`
- 固定 cache：`BTCUSDT / ETHUSDT / SOLUSDT 120d 15m`
- 事件定义：`abs(ret_15m) > rolling_mean(abs(ret), 96) + 2.0 * rolling_std(abs(ret), 96)`
- 三臂对照：
  - `baseline`
  - `same_window_only`：仅 `event_age<=12` 时放行
  - `window_plus_timeout`：`event_age<=12` 放行；`12~24` 之间必须额外二次确认，否则 timeout no-trade
- 二次确认冻结为最小因果口径：
  - long：`close > ema9 且 close > open`
  - short：`close < ema9 且 close < open`
- 中途故障 / fallback：
  - 首次运行脚本失败，原因是 `variant_decision()` 错把字段名写成 `last_event_dir`，导致非 baseline 变体全被误判成 `no_recent_event`
  - 按要求没有整轮失败，立即回退做 `read + 调试`，确认事件样本存在后，把字段修正为 `event_dir` 再重跑，成功完成 clean replication

## 当前硬结论
**`Rank 111 = keep_P1 / event-clock gate has honest signal`**。

翻成人话：
- 它不是已经够硬的 `paper candidate`，但确实证明了一个方向：**把“冲击后还能追多久”写成 same-window 放行 + 超窗 timeout/reconfirm，比裸 baseline 更诚实**；
- `baseline` 的 desk 级结果是 `mean_total_return≈-6.47%`、`false_follow≈53.03%`、`positive_asset_ratio=1/3`；
- `same_window_only` 收紧后变成 `≈-2.44% / 45.28% / 2/3`；`window_plus_timeout` 也改善到 `≈-3.41% / 45.61% / 2/3`；
- baseline 里有 **`42.42%`** 交易属于跨窗追单，而这些交易的 `false_follow` 高到 **`64.29%`**，说明“超窗默认不追”这件事本身是有料的；
- 但 retention 仍只有 **`53.54%` / `57.58%`**，而且 `ema_psar_long` 这一腿还在拖后腿（`window_plus_timeout total_return≈-14.97%`），所以当前只够留在 **`P1 weak candidate / evidence_pool`**，不足以升到 `P2 / paper candidate`。

## 关键结果
### desk 级（6bps/side）
- `baseline`
  - `mean_total_return≈-6.47%`
  - `positive_asset_ratio=1/3`
  - `false_follow_through_4bars≈53.03%`
  - `trade_count_retention=100.00%`
  - `cross_window_trade_share≈42.42%`
- `same_window_only`
  - `mean_total_return≈-2.44%`
  - `positive_asset_ratio=2/3`
  - `false_follow_through_4bars≈45.28%`
  - `trade_count_retention≈53.54%`
  - `cross_window_trade_share=0.00%`
- `window_plus_timeout`
  - `mean_total_return≈-3.41%`
  - `positive_asset_ratio=2/3`
  - `false_follow_through_4bars≈45.61%`
  - `trade_count_retention≈57.58%`
  - `cross_window_trade_share≈7.02%`

### setup 级（6bps/side）
- `breakout_short`
  - `baseline≈-9.41%`
  - `same_window_only≈+1.15%`
  - `window_plus_timeout≈-1.70%`
- `fib_retest_long`
  - `baseline≈+3.08%`
  - `same_window_only≈+5.23%`
  - `window_plus_timeout≈+6.43%`
- `ema_psar_long`
  - `baseline≈-13.07%`
  - `same_window_only≈-13.71%`
  - `window_plus_timeout≈-14.97%`
  - 说明这条 overlay 目前更像对 `breakout_short / fib_retest` 有帮助，对 `ema_psar_long` 还不够诚实。

### asset 级（6bps/side）
- `baseline`：`BTC≈-1.30%`、`ETH≈-19.81%`、`SOL≈+1.71%`
- `same_window_only`：`BTC≈+3.98%`、`ETH≈-21.61%`、`SOL≈+10.29%`
- `window_plus_timeout`：`BTC≈+2.69%`、`ETH≈-21.61%`、`SOL≈+8.68%`
- 说明它对 `BTC/SOL` 的帮助比较清楚，但 `ETH` 仍是当前最大拖累；跨资产稳定性还不够支撑升格。

### event-age 读法（6bps/side）
- `baseline / same-window trades`：`114` 笔，`total_return≈-7.76%`，`false_follow≈44.74%`
- `baseline / cross-window trades`：`84` 笔，`total_return≈-11.65%`，`false_follow≈64.29%`
- `window_plus_timeout / cross-window trades`：只保留 `8` 笔，`total_return≈-2.91%`，`false_follow≈50.00%`
- 这说明本轮最有价值的不是“同窗内多赚钱”，而是 **诚实地削掉一批跨窗坏追单**。

## 对顶板的直接影响
- `Paper Seat = EMA / running paper / waiting_not_due`
- `Live Seat = 暂空`
- `Rank 111` 应从 `P0 / source intake next` 更新为：**`P1 weak candidate / evidence_pool / budget used`**
- 当前更诚实的 active Scout 顺序：
  1. `basis dislocation short veto reserve`（`P0 / source intake next`）
  2. `alpha-beta abstain / profit-window reserve`（`P0 / ex-ante honesty gate first`）
  3. `Rank 111 / abnormal-return event clock`（`P1 weak candidate / evidence_pool / budget used`）
  4. `Rank 93 / 90 / 91 / 82 / 80 / 81`（`P1 evidence_pool / budget used`）
  5. `Rank 110 / 109 / 108 / 107 / 106 / 105 / 104 / 103 / 102 / 101 / 100 / 99 / 98 / 97 / 96 / 95 / 94 / 92 / regression-channel-width`（`P0 park / evidence pool`）
  6. `Rank 2 / Rank 17 / Rank 29 / Rank 32b`（`P3 continuity / hosted lanes / sidecar only`）
- 当前 `P2` 仍空、`P4` 仍空。
- 最新 `Next 3`（本轮后）：
  1. `Run 1 = EMA due-check first（若 due-now / overdue，先做 guarded refresh）`
  2. `Run 2 = 若 EMA 仍 waiting_not_due，则只给 basis dislocation short veto 1 次 source intake + 两条轻量诚实守门`
  3. `Run 3 = 若 basis guard-pass，则只给它 1 次最小 clean replication；若 basis hard-fail / exhausted，则切 alpha-beta abstain / profit-window 的 ex-ante honesty gate source intake；只有这层也 exhausted 后，才轮到 Rank 17 的低频 health-check fallback > tiny-live plumbing`

## 本轮交付（deployable artifact）
- script：`scripts/build_rank111_event_clock_clean_replication.py`
- artifacts：
  - `reports/artifacts/scout_rank111_event_clock_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank111_event_clock_15m/setup_summary.csv`
  - `reports/artifacts/scout_rank111_event_clock_15m/asset_summary.csv`
  - `reports/artifacts/scout_rank111_event_clock_15m/event_age_summary.csv`
  - `reports/artifacts/scout_rank111_event_clock_15m/time_bucket_summary.csv`
  - `reports/artifacts/scout_rank111_event_clock_15m/trade_log.csv`
  - `reports/artifacts/scout_rank111_event_clock_15m/summary.json`
- reader-facing 页面：
  - `reports/site/factors/scout_rank111_event_clock_15m/report.html`
  - `reports/site/reading/repo_scout/rank111_event_clock_clean_replication.html`
- 顶板刷新：`docs/TODO.md`

## 最小验证
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- `python3 scripts/build_rank111_event_clock_clean_replication.py`
- 回读确认：
  - `reports/artifacts/scout_rank111_event_clock_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank111_event_clock_15m/setup_summary.csv`
  - `reports/artifacts/scout_rank111_event_clock_15m/event_age_summary.csv`
  - `reports/site/factors/scout_rank111_event_clock_15m/report.html`
  - `docs/TODO.md`

## 风险 / 边界
- 这轮只完成了最小 clean replication，**没有**进入 `Light Stability Pack`，更没有升格到 `paper candidate pool`。
- 当前最诚实的读法仍是：它更像 `shared follow-up / timeout overlay` 的 honest evidence，而不是已经能直接托管的共享 gate。
- 当前工作区有大量与本轮无关的脏文件，因此不安全混提。

## Commit hash
- 未提交。
- 原因：工作区存在大量无关脏文件（`1694` 项），本轮只做局部脚本 / 产物 / 顶板回写，不适合混提。
