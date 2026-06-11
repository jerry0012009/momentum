# Rank 65 / perp-stress resetComplete-rearm 最小 clean replication：coverage 不成立，先 park

## 为什么这次选这个
- 当前轮次先按 `TRADING DESK BOARD` 的 `Run 1 -> Run 2 -> Run 3` 执行。
- `Run 1 / EMA` 在上一轮 `20:02 UTC` 已真实消化 `美股 1d+1wk` 的 due window；当前 `ema_paper_trading_due_guardrail_snapshot.csv` 已回到**无 `due-now / overdue` lane**，最早变成 `Crypto 1d+1wk -> 2026-03-19 00:00 UTC`。
- `manual_narrow_paper_last_run_summary.json` 最新仍是 `new_closed_trades_appended=0`，没有新的 `P3` 状态变化值得抢主资源。
- 因此这轮应严格落到 `Run 2`：只给 `Rank 65 / perp-stress resetComplete / re-arm gate` 那 **1 次最小 clean replication**，而不是继续做 `P3 continuity` 或重新发散新题。

## 这轮做了什么
1. 新增脚本：
   - `scripts/build_rank65_perp_stress_reset_rearm_clean_replication.py`
2. 实际执行：
   - `python3 scripts/build_rank65_perp_stress_reset_rearm_clean_replication.py`
3. 产物落点：
   - `reports/artifacts/scout_rank65_perp_stress_reset_rearm_15m/overall_summary.csv`
   - `reports/artifacts/scout_rank65_perp_stress_reset_rearm_15m/setup_summary.csv`
   - `reports/artifacts/scout_rank65_perp_stress_reset_rearm_15m/stress_event_board.csv`
   - `reports/site/factors/scout_rank65_perp_stress_reset_rearm_15m/report.html`
   - `reports/site/reading/repo_scout/rank65_perp_stress_reset_rearm_clean_replication.html`
4. 最小回写：
   - `docs/TODO.md` 顶部最新补充已同步到 `2026-03-18 20:18 UTC` 的 desk 状态与 `Next 3`。

## replication 口径（尽量便宜但诚实）
- 标的：`BTCUSDT / ETHUSDT / SOLUSDT`
- 周期：`120d 15m`
- 数据：现有 spot cache + Binance futures `15m` perp klines + `openInterestHist`
- base archetype：
  - `ema_psar_long`
  - `fib_retest_long`
  - `breakout_short`
- 三臂比较：
  - `no_gate`
  - `stress_pause_only`
  - `stress_pause_reset_rearm`
- 执行统一：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`
- 成本：`6 / 10 / 15 / 20 bps per side`

## 验证 / 证据
### 1) 6bps/side 下三臂结果完全一样
`overall_summary.csv`：
- `no_gate`：`mean_total_return≈-5.95%`、`positive_asset_ratio≈66.67%`、`mean_trades≈66.3`、`mean_trade_count_retention≈96.72%`、`mean_target_hit_rate_12bars≈62.35%`
- `stress_pause_only`：**完全相同**
- `stress_pause_reset_rearm`：**完全相同**

这不是“gate 很稳”，而是更糟：说明 gate 在当前最小口径下根本没有实际筛选到样本。

### 2) 根因是 strict proxy 定义下没有任何事件 coverage
`stress_event_board.csv`：
- `BTC-USD`：`stress_events=0`、`reset_complete_bars=0`
- `ETH-USD`：`stress_events=0`、`reset_complete_bars=0`
- `SOL-USD`：`stress_events=0`、`reset_complete_bars=0`

也就是说，当前这套最小诚实定义：
- `stress_event = |basis| 偏离 + OI impulse + wick/volume 异常`
- `resetComplete = basis 回中性 + OI flush + ATR 压缩`

在 `BTC/ETH/SOL 120d 15m` 的公开单交易所代理样本上，**连首轮 coverage 都站不住**。

### 3) 这轮 hard verdict
**`Rank 65 / perp-stress resetComplete / re-arm gate = park / evidence pool`**。

更直白地说：
- 它现在更像一个“概念上很合理，但最小公开代理口径打不到样本”的高摩擦模板；
- 在 coverage 都不成立的前提下，继续给它时间稳定性 / 参数稳定性预算没有意义；
- 这不该继续占 `Scout Seat` 主资源位。

## 风险 / 边界
- 这轮的 negative verdict 主要来自 **coverage fail**，不是来自“明明有很多事件，但效果不好”。
- 我另外做了一个极短 sanity check，发现如果把阈值明显放松，ETH/SOL 会出现少量事件；但那已经不是 source-intake 冻结的 strict 读法了。这轮没有偷改阈值去“救活”它。
- 因为当前 git 工作区仍有大量与本轮无关的脏文件 / 未跟踪文件，所以本轮不做 commit，避免混提。

## 对当前 desk 的硬结论
- `Paper Seat / EMA`：当前回到 `running paper / no due-now`，下一次最早真实窗口是 `Crypto 1d+1wk -> 2026-03-19 00:00 UTC`。
- `Scout Seat`：`Rank 65` 已完成允许预算内的最小 clean replication，并因 **coverage 不成立** 压回 `park / evidence pool`。
- 当前更诚实的 active Scout 顺序应更新为：
  - `exec-TF switch alignment gate`
  - `regime-matrix shared-state gate`
  - `Rank 35b`
  - `Rank 16b`
  - `tiny-live plumbing`

## 下一步建议
1. 下一轮仍先做 `Run 1 / EMA due-check only`。
2. 若仍无新的 `due-now / overdue`，则回到 fresh source 比较：
   - `exec-TF switch alignment gate > regime-matrix shared-state gate`
3. 只要新的 fresh source guard-passed，再给它 **1 次最小 clean replication**；不要回头继续磨 `Rank 65` 的 admission wording。

## 提交
- 未提交。
- 原因：当前 git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件，安全 selective commit 成本过高，容易混提。
