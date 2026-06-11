# 2026-03-19 03:15 UTC｜Rank 77 / alt-vs-BTC RS breadth shared gate source intake（guard-passed）

## 轮次定位
- 席位：`Scout Seat`
- 本轮主点：`Run 2 / fresh paper-repo source re-rank`
- 紧邻子点：把真正更 queue-facing 的下一条 fresh source 冻结成 `Rank 77` source intake，并刷新 `TODO` 顶板 `Next 3`

## 开始前检查
- `Run 1 / EMA due-check`：最新 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍显示全 desk 当前无 `due-now / overdue` lane；最近 due 点仍是 `A股三条 lane -> 2026-03-19 07:00 UTC`，因此 `Paper Seat / EMA` 继续是 `running paper / waiting_not_due`。
- `P3 continuity`：`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-19T02:46:36Z` 继续是 `new_closed_trades_appended=0`，本轮没有新的 `P3 status-changing event` 值得回头挤占 continuity。
- 最近 run：`Rank 76` 已在 `02:58 UTC` 的最小 clean replication 后给出 `park / evidence pool` 硬结论，因此当前合法主动作必须回到 `fresh source re-rank`。
- git 工作区仍有大量与本轮无关的脏文件 / 未跟踪文件；本轮只新增 `Rank 77` source-intake artifact、reader-facing 页面、`TODO` 顶板写回与本轮日志，不做混提。

## 为什么这轮选这个
这轮没有继续默认拿 `one-regime-per-session overlay`，而是先按规则显式比较当前最相关的 3 条允许动作：
1. `one-regime-per-session overlay`
2. `adaptive no-trade band / EMA cost survival`
3. `alt-vs-BTC RS breadth shared gate`

比较后的诚实顺序：
- **`Rank 77 / alt-vs-BTC RS breadth shared gate`**
- `adaptive no-trade band / EMA cost survival`
- `one-regime-per-session overlay`

原因：
1. `Rank 77` 是公开 repo，规则可清楚冻结成 `trade on / trade off`，而且直接服务 `breakout-short / Fib retest_hold / EMA-PSAR` 三条主线；
2. `adaptive band` 虽然也有价值，但当前更像 `EMA / PSAR raw alpha` 单线的成本存活层，而且本轮证据主要还是论文摘要级；
3. `one-regime-per-session` 更像 desk-level allocation overlay，不够 queue-facing，不该在仍有更便宜的 fresh shared gate 时继续抢默认 fast lane。

## 这轮具体做了什么
### 1. 正式冻结新的 queue-facing Rank
- 把 `2026-03-19 02:37 UTC` digest 里的 `alt-vs-BTC RS breadth shared gate` 正式冻结为：
  - **`Rank 77 / alt-vs-BTC RS breadth shared gate`**
- 生成 queue-facing artifact：
  - `reports/artifacts/literature/scout_rank77_alt_btc_rs_breadth_source_intake_card.csv`
- 生成 reader-facing 页面：
  - `reports/site/reading/repo_scout/rank77_alt_btc_rs_breadth_source_intake.html`

### 2. 过两条轻量诚实守门
- `trade on`：先冻结 `Top20~50` 可交易 alt universe，滚动计算 `rs_i = ret_24h(asset_i) - ret_24h(BTC)`；当 `breadth_pos` 明显走高时放宽 `Fib retest_long / EMA continuation`，当 `breadth_neg` 明显走高时放宽 `breakout_short`，中性区只 half-size / no-trade。
- `trade off`：breadth 只能当 shared allow/deny 或 sizing gate，不能单独开仓，也不能把“山寨强/弱”叙事偷渡成某个单币的 15m 入场神谕。
- `lookahead / repaint / leakage`：desk 迁移必须把 universe、ranking 与 breadth 统一冻结到 `signal 当根及之前可得数据 + next-bar open + no-overlap`，不能用日后才知道的成交量排名、成分变动或未来 breadth 回填结果。

## Hard verdict
**`Rank 77 / alt-vs-BTC RS breadth shared gate = guard-passed / admit_to_clean_replication_queue`**

## 为什么这轮给这个 verdict
- 它满足两条最轻诚实门槛：规则能清楚写成 `trade on / trade off`，源码结构也没有一眼可判死刑的 lookahead / repaint / leakage；
- 它是当前比 `one-regime` 更 queue-facing、比 `adaptive band` 更共享的 shared gate；
- 但当前还只是 source-intake / honesty-gate 通过，不是已验证 alpha；下一轮必须只给它 **1 次最小 clean replication**，不能直接升格。

## 对交易台顺序的影响
- 当前 active Scout 顺序应更新为：
  1. `Rank 77 / alt-vs-BTC RS breadth shared gate`
  2. `adaptive no-trade band / EMA cost survival`
  3. `one-regime-per-session overlay`
  4. `Rank 35b`
  5. `Rank 16b`
  6. `tiny-live plumbing`
- 当前 seat 分级应收紧为：
  - `Rank 77 = P1 weak candidate（guard-passed / minimal clean replication next）`
  - `adaptive no-trade band / EMA cost survival = P0 fresh-paper queue / not admitted`
  - `one-regime-per-session overlay = P0 evidence / backlog`
  - `Rank 76 / 75 / 74 / 73 / 72 = P0 park / evidence pool`
  - `Rank 2 / 17 / 29 / 32b = P3 narrow paper continuity`
- 更新后的 `Next 3`：
  1. `Run 1 = EMA due-check only`
  2. `Run 2 = 若 Rank 77 已 guard-passed 且 EMA 仍 waiting_not_due，则立刻给它 1 次最小 clean replication（优先比较 24h vs 8h breadth 变体）`
  3. `Run 3 = 若 Rank 77 这一轮给出 hard verdict，则再回到 adaptive no-trade band > one-regime-per-session overlay > fresh pool 其他 source；只有 fresh source 这一层也 exhausted 时，才允许回退到 Rank 35b > Rank 16b > tiny-live plumbing`

## 最小验证
- 已确认以下文件存在：
  - `reports/artifacts/literature/scout_rank77_alt_btc_rs_breadth_source_intake_card.csv`
  - `reports/site/reading/repo_scout/rank77_alt_btc_rs_breadth_source_intake.html`
- 已确认 `docs/TODO.md` 顶板写回成功。

## 风险 / 边界
- 当前只是 source-intake / honesty-gate 通过，不代表 breadth 在 15m 上一定有效；
- `24h RS breadth` 可能太慢，所以下一轮默认要和 `8h breadth` 一起做最小 clean replication，而不是先写更多解释页；
- universe 漂移是这条线最大的诚实风险，必须先冻结可交易 perp 池，避免用事后排名修饰结果。

## Commit hash
- 未提交。
- 原因：git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件，当前不适合安全 selective commit。
