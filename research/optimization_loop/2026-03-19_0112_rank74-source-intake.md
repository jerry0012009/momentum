# 2026-03-19 01:12 UTC｜Rank 74 / ADX+ER price-only trend-readiness gate source intake（guard-passed）

## 轮次定位
- 席位：`Scout Seat`
- 本轮主点：`Run 2 / fresh paper-repo source re-rank -> Rank 74 source intake + 两条轻量诚实守门`
- 紧邻子点：`TODO 顶板顺序刷新`

## 开始前检查
- `Run 1 / EMA due-check`：最新 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 继续显示全 desk 当前无 `due-now / overdue` lane；最早 due 点仍是 `A股三条 lane -> 2026-03-19 07:00 UTC`，因此 `Paper Seat / EMA` 仍是真 `running paper / waiting_not_due`。
- `P3 continuity`：`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-19T01:06:23Z` 继续是 `new_closed_trades_appended=0`，当前没有新的 `P3 status-changing event` 值得 bot3 回头挤占 continuity。
- 上一轮 `Rank 73` 已在 minimal clean replication 后给出 **`park / evidence pool`** hard verdict；因此按顶板最新顺序，本轮合法主动作必须切回 fresh source，而不是继续围着 `Rank 73` 或 `P3` 托管位打转。
- git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件；本轮只新增 `Rank 74` source-intake artifact、reader-facing 页面、`TODO` 顶板写回与本轮日志，不做混提。

## 为什么这轮选 Rank 74
这轮先比较了当前仍活着的几个 fresh-source 方向：
1. `ADX+ER price-only trend-readiness gate`（2026-03-19 00:55 digest）
2. `GCR extreme-sentiment exhaustion veto`（2026-03-19 00:23 digest）
3. `one-regime-per-session overlay`（2026-03-18 23:54 paper）

当前更诚实的边际价值排序是：
- **`Rank 74 / ADX+ER price-only trend-readiness gate`**
- `GCR extreme-sentiment exhaustion veto`
- `one-regime-per-session overlay`
- `Rank 35b`
- `Rank 16b`
- `tiny-live plumbing`

先认领 `Rank 74` 的原因：
1. 它只吃现有 `15m OHLCV`，不需要新的外部 flow / OI / liquidation 数据接入；
2. 覆盖面最广：能同时服务 `breakout-short / Fibonacci retest_hold / EMA-PSAR` 三条主线；
3. 它补的是当前 desk 最缺的 shared spine：**先问市场是不是“真的在走”，而不是继续堆第 N 个各自不同的小 veto**；
4. 相比 `GCR exhaustion veto`，它不是只盯“最后一脚别追”，而是更前置的 `anti-chop / trend-readiness` allow/deny 层；
5. 相比 `one-regime-per-session overlay`，它更便宜、更接近当前 queue-facing 的最小 clean replication，而不是更上层的 allocation overlay。

## 这轮冻结的两条轻量诚实守门
- `trade on`：base setup 继续负责方向与价位；`ADX + ER` 只负责回答当前 15m 价格路径是否已经进入 `trend-ready` pocket。首轮冻结为：
  - `trend_ready_long = (adx14 >= 20) & (er20 >= 0.20) & (plus_di > minus_di)`
  - `trend_ready_short = (adx14 >= 20) & (er20 >= 0.20) & (minus_di > plus_di)`
  - `er20 >= 0.40` 只允许先做 high-conviction bucket，不直接偷渡成独立 alpha
- `trade off`：若 `adx14 < 20`、`er20 < 0.20`、或 `DI` 方向与主 trigger 不一致，则直接 veto / 延后；它不能单独开仓，也不能把方向角色从 breakout / Fib / EMA 手里抢走。
- `lookahead / repaint / leakage`：`ER20`、`ADX14`、`DI` 都可只用 trailing OHLCV 计算，源码层未见一眼可判死刑的未来函数；但 desk 迁移必须统一冻结成 `signal 当根及之前数据 + next-bar open + no-overlap`，不得把 signal 后 bar 回填为 trend-ready 判定，也不得把 repo 默认 `4h` 口径包装成 `15m` 既成事实。

## 本轮新增产物
1. Source-intake artifact：
   - `reports/artifacts/literature/scout_rank74_adx_er_trend_readiness_source_intake_card.csv`
2. Reader-facing 页面：
   - `reports/site/reading/repo_scout/rank74_adx_er_trend_readiness_source_intake.html`
3. Queue-facing 更新：
   - `docs/TODO.md` 顶部 `Next 3 bot3 runs`

## Hard verdict
**`Rank 74 / ADX+ER price-only trend-readiness gate = guard-passed / admit_to_clean_replication_queue`**

## 为什么是这个 verdict
- 规则能清楚写成 `trade on / trade off`：它不是新 alpha，而是 shared `anti-chop / trend-readiness` gate；
- 源码里的关键指标都可清楚复刻，而且没有一眼可判死刑的 `lookahead / repaint / leakage`；
- 首轮实现足够便宜：只需要现有 `BTC/ETH/SOL 15m` cache，就能比较 `baseline / adx_only / er_only / adx_plus_er / adx_plus_er_plus_di`；
- 但它现在仍只是 admitted，不是已验证 alpha；下一轮若 clean replication 发现改善主要来自极端砍单、或只在单一 archetype 勉强成立，就应快速压回 `park / evidence pool`。

## 对交易台顺序的影响
- 当前最新 `Next 3` 已更新为：
  1. `Run 1 = EMA due-check only`
  2. `Run 2 = 若 Rank 74 已 guard-passed 且 EMA 仍 waiting_not_due，则立刻给它 1 次最小 clean replication`
  3. `Run 3 = 若 Rank 74 这一轮给出 hard verdict，则先回到 fresh source re-rank（默认比较 GCR exhaustion veto > one-regime-per-session overlay > fresh pool 其他 source）；只有 fresh source 这一层也 exhausted 时，才允许回退到 Rank 35b > Rank 16b > tiny-live plumbing`
- 本轮后，当前合法 fast-lane 头部已不再是 `Rank 73`，而是 `Rank 74 / ADX+ER price-only trend-readiness gate`。

## 最小验证
- 已确认以下输出文件存在：
  - `reports/artifacts/literature/scout_rank74_adx_er_trend_readiness_source_intake_card.csv`
  - `reports/site/reading/repo_scout/rank74_adx_er_trend_readiness_source_intake.html`
- 已确认 `docs/TODO.md` 顶板写回成功。

## 风险 / 边界
- 这条线来自 repo 工程规则，不是高等级学术证据；值钱的是规则口径清楚，不是原仓库绩效可直接照抄。
- `ADX` 和 `ER` 都偏慢；若阈值卡太死，很可能把 breakout-short 的早期 expansion 错杀掉。
- 这轮只做到 source intake + 两条轻量诚实守门，不展开 clean replication，也不顺手去开第二条 fresh source。

## 下一步建议
- 直接按顶板切到 **`Rank 74 minimal clean replication`**。
- 默认只比较 `baseline / adx_only / er_only / adx_plus_er / adx_plus_er_plus_di` 五臂，不把它扩成新的 ADX/ER 大研究。

## Commit hash
- 未提交。
- 原因：git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件，当前不适合安全 selective commit。
