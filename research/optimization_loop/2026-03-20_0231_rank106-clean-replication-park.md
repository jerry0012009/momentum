# 2026-03-20 02:31 UTC — Rank 106 elephant candle corridor clean replication → park

## Run 1 -> Run 2 执行
- Run 1：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：`EMA = waiting_not_due`
  - 当前没有 `due-now / overdue` lane
  - 最近 due：`A股三条 lane -> 2026-03-20 07:00 UTC`（约 `4.5h`）
  - `require-due` guard 正常触发（exit code `2`），没有伪造 refresh
- 因此按当前 `TRADING DESK BOARD`，本轮合法主动作仍是 `Scout Seat`，且只该拿 **`Rank 106 / elephant candle corridor long-bias gate`** 的那唯一一手最小 clean replication。

## 开轮检查
- branch：`master`
- repo 脏文件：`git status --short | wc -l = 1637`
- 最近 optimization logs：
  - `2026-03-20_0228_rank106-elephant-intake.md`
  - `2026-03-20_0220_rank105-clean-replication-park.md`
  - `2026-03-20_0202_rank105-body-zone-intake.md`
- 当前席位直读：
  - `Paper Seat = EMA / running paper / waiting_not_due`
  - `Live Seat = 暂空`
  - 本轮前的 `Scout Seat` 顺序为：`Rank 106 / elephant candle corridor long-bias gate > MTF CHOP charged-up count > prebreak higher-low pressure ladder context gate > 旧 evidence_pool / P3 continuity / tiny-live plumbing`

## Active Scout 候选边际比较（先比较后认领）
1. **`Rank 106 / elephant candle corridor long-bias gate`**
   - 上轮已完成 `source intake + 两条轻量诚实守门`，当前是唯一合法的 queue-facing 下一手。
   - 它最直接回答当前 desk 还缺的那件事：`Fib reclaim / EMA continuation` 的确认 bar，到底能不能靠“强但不过热”这层质量门减少 early fail。
2. **`MTF CHOP charged-up count`**
   - 仍是后备 fresh intake，但在 `Rank 106` 的 clean replication verdict 没收口前，不该抢本轮主资源。
3. **`prebreak higher-low pressure ladder context gate`**
   - 仍是 context backlog，不是当前 queue-facing 主资源位。
4. **旧 `P1 evidence_pool` / `P3 continuity` / `tiny-live plumbing`**
   - 当前都不该抢主资源位。

结论：本轮只认领 `Rank 106` 的最小 clean replication，不并开任何第二条候选。

## 本轮认领
- 主点：`Rank 106 / elephant candle corridor long-bias gate`
- 紧邻子点：把 clean replication artifact、reader-facing 页面、`TODO` 顶板与下一轮顺序一次写齐

## Clean replication 口径（strict queue-facing）
- 数据：`BTC/ETH/SOL Binance Futures 120d 15m`
- 执行：`signal 当根及之前数据 + next-bar open + no-overlap + hold 4 bars + 6bps/side`
- 三臂只比较：
  1. `baseline`
     - 趋势背景下的最小 breakout 代理：`SMA20>SMA200` 且 `close > prev_high + 0.15*ATR14`；short 侧做对照镜像
  2. `body_only`
     - 只在 baseline 上额外加 `body_ratio>=0.5`
  3. `full_corridor`
     - 再加 `body > prev_range`、`body > 0.8*ATR14`、`full_range < 3.5*ATR14`
- 关键 honesty 约束：
  - ATR / prev_range / SMA 都只用 signal bar 及之前数据
  - 不允许用 future bar 决定是否满足 corridor
  - 这轮只测“确认 bar 质量门”，不是把它包装成完整独立 alpha

## 结果摘要
### overall（4 bars / 6 bps per side）
- `baseline`
  - `events = 3737`
  - `mean_net_ret ≈ -11.91bps`
  - `win_rate ≈ 35.22%`
  - `fail_back_inside_4bars ≈ 59.33%`
- `body_only`
  - `events = 3123`
  - `trade_count_retention ≈ 83.57%`
  - `mean_net_ret ≈ -10.71bps`
  - `fail_back_inside_4bars ≈ 56.39%`
- `full_corridor`
  - `events = 1557`
  - `trade_count_retention ≈ 41.66%`
  - `mean_net_ret ≈ -12.40bps`
  - `fail_back_inside_4bars ≈ 45.99%`

### side split（重点）
- `long baseline`
  - `events = 1767`
  - `mean_net_ret ≈ -14.16bps`
  - `fail_back_inside_4bars ≈ 59.03%`
- `long full_corridor`
  - `events = 705`
  - `mean_net_ret ≈ -9.94bps`
  - `fail_back_inside_4bars ≈ 42.70%`
  - 说明：long 侧确实更像 quality gate，少亏、也更少回吐进原区间
- `short baseline`
  - `events = 1970`
  - `mean_net_ret ≈ -9.88bps`
- `short full_corridor`
  - `events = 852`
  - `mean_net_ret ≈ -14.43bps`
  - 说明：short 侧反而恶化，不支持把它包装成 breakout-short shared gate

### 怎么读
- `body_only` 这层最像“温和改善”：保留了大部分样本，同时 slightly less bad。
- 但 desk 当前真正关心的不是“有一点改善味道”，而是这条线能不能作为 queue-facing gate 留在默认主资源位。
- `full_corridor` 在 long 侧确实更诚实：失败回吐率明显下降，post-cost 也少亏。
- 问题是：
  1. `overall` 仍然没翻正；
  2. 样本被砍到只剩约 `41.66%`；
  3. short 侧明显变差。
- 所以这条线最诚实的定位仍是：**long-side quality filter evidence**，而不是可共享的 admission gate，更不是 `P2 / paper candidate`。

## 当前硬结论
**`Rank 106 = park / evidence pool`**。

翻成人话：记住“强但不过热”的 candle corridor 对 long reclaim / continuation 有一点帮助，但别把这点帮助误包装成更大的结论。它没把整体 expectancy 拉正，也不该被偷渡成 breakout-short shared follow-up 键。

## 本轮交付（deployable artifact）
- artifact：
  - `reports/artifacts/scout_rank106_elephant_candle_corridor_15m/event_log.csv`
  - `reports/artifacts/scout_rank106_elephant_candle_corridor_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank106_elephant_candle_corridor_15m/side_summary.csv`
  - `reports/artifacts/scout_rank106_elephant_candle_corridor_15m/symbol_summary.csv`
  - `reports/artifacts/scout_rank106_elephant_candle_corridor_15m/verdict_summary.csv`
  - `reports/artifacts/scout_rank106_elephant_candle_corridor_15m/summary_snapshot.json`
- reader-facing 页面：
  - `reports/site/factors/scout_rank106_elephant_candle_corridor_15m/report.html`
  - `reports/site/reading/repo_scout/rank106_elephant_candle_corridor_clean_replication.html`
- 可复现脚本：
  - `scripts/build_rank106_elephant_candle_corridor_clean_replication.py`

## 对顶板的直接影响
- `Paper Seat = EMA / running paper / waiting_not_due`
- `Live Seat = 暂空`
- `Scout Seat` 默认从 `Rank 106` 切到 **`MTF CHOP charged-up count`**
- 当前 active Scout 顺序应改写为：
  1. `MTF CHOP charged-up count`
  2. `prebreak higher-low pressure ladder context gate`
  3. `旧 P1 evidence_pool`
  4. `P3 continuity sidecar`
  5. `tiny-live plumbing`
- 当前最新 `Next 3`：
  1. `Run 1 = EMA due-check only（优先盯 A股三条 lane -> 2026-03-20 07:00 UTC）`
  2. `Run 2 = 若 EMA 仍 waiting_not_due，则切 MTF CHOP charged-up count 的 source intake + 两条轻量诚实守门`
  3. `Run 3 = 若 MTF CHOP charged-up count guard-pass，则只给它 1 次最小 clean replication；若它 hard-fail / exhausted，则切 prebreak higher-low pressure ladder context gate；只有 fresh source 也 exhausted，才轮到旧 P1 evidence_pool > P3 continuity sidecar > tiny-live plumbing`

## 最小验证
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 如实确认当前仍是 `waiting_not_due`
- `python3 scripts/build_rank106_elephant_candle_corridor_clean_replication.py`
  - 成功生成 rank106 clean replication artifact 与 reader-facing 页面
- 回读以下文件，确认已写入成功：
  - `reports/artifacts/scout_rank106_elephant_candle_corridor_15m/verdict_summary.csv`
  - `reports/site/reading/repo_scout/rank106_elephant_candle_corridor_clean_replication.html`
  - `docs/TODO.md`

## 备注
- 本轮没有并开 `MTF CHOP`、`prebreak ladder` 或任何 `P3 continuity`
- 本轮没有整理或覆盖无关脏文件
- 工作区仍有大量历史脏文件；本轮只做 selective write-back
