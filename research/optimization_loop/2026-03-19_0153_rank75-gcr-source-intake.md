# 2026-03-19 01:53 UTC｜Rank 75 / GCR extreme-sentiment exhaustion veto source intake（guard-passed）

## 轮次定位
- 席位：`Scout Seat`
- 本轮主点：`Run 2 / Rank 75 source intake + 两条轻量诚实守门`
- 紧邻子点：`TODO 顶板顺序刷新`

## 开始前检查
- `Run 1 / EMA due-check`：最新 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 继续显示全 desk 当前无 `due-now / overdue` lane；最早 due 点仍是 `A股三条 lane -> 2026-03-19 07:00 UTC`，因此 `Paper Seat / EMA` 仍是真 `running paper / waiting_not_due`。
- `P3 continuity`：`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-19T01:50:50Z` 继续是 `new_closed_trades_appended=0`，当前没有新的 `P3 status-changing event` 值得 bot3 回头挤占 continuity。
- 上一轮 `Rank 74` 已在 minimal clean replication 后给出 **`park / evidence pool`** hard verdict；因此按顶板最新顺序，本轮合法主动作必须切回 fresh source，而不是继续围着 `Rank 74` 或 `P3` 托管位打转。
- git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件；本轮只新增 `Rank 75` source-intake artifact、reader-facing 页面、`TODO` 顶板写回与本轮日志，不做混提。

## 为什么这轮选 Rank 75
这轮先比较了当前仍活着的几个 fresh-source 方向：
1. `Rank 75 / GCR extreme-sentiment exhaustion veto`（2026-03-19 00:23 digest）
2. `Rank 76 / intraday clock polarity + event blackout gate`（2026-03-19 01:33 digest）
3. `one-regime-per-session overlay`（2026-03-18 23:54 paper）

当前更诚实的边际价值排序是：
- **`Rank 75 / GCR extreme-sentiment exhaustion veto`**
- `Rank 76 / intraday clock polarity + event blackout gate`
- `one-regime-per-session overlay`
- `Rank 35b`
- `Rank 16b`
- `tiny-live plumbing`

先认领 `Rank 75` 的原因：
1. 它仍是 paper / repo based 的 `5m / 15m crypto` queue-facing 候选；
2. 它比 `Rank 76` 更便宜：只需现有 `15m + 5m OHLCV`，不需要先把更重的 session / event overlay 定义写实；
3. 它补的是当前三条主线共同缺的 shared failure veto：**不要追最后一脚**；
4. 相比刚 park 的 `Rank 74`，它不再试图回答“市场是不是在走”，而是更聚焦地回答“哪些 continuation 已经过挤、过晚、太容易反抽”；
5. 相比 `one-regime-per-session overlay`，它更接近 queue-facing 的最小 clean replication，而不是更上层的 allocation overlay。

## 这轮冻结的两条轻量诚实守门
- `trade on`：base setup 继续负责方向与价位；这条 gate 只负责识别 continuation / breakout / retest entry 是否已经走到“最后一脚”。首轮冻结为 shared veto / size-down overlay：若执行前后 `1~3` 根 `5m` 内出现 opposite-side GCR extreme cluster（`RSI/Stoch` 极端 + `volume spike/exhaustion` + `BB` 边缘 + divergence 可选），则对应主信号只允许 `veto / half-size`；它不是独立 reversal alpha。
- `trade off`：若没有 extreme cluster，base setup 继续按原规则执行；若改善只来自 `divergence` 这类实时口径更脆的条件，就必须保留一版 `pure-extreme + volume + BB` 的无 divergence 基线。它不能单独开仓，也不能把方向角色从 breakout / Fib / EMA / PSAR 手里抢走。
- `lookahead / repaint / leakage`：源码里的 `RSI/Stoch`、`volume MA`、`BB`、`pivot` 与 `divergence` 都能用 trailing OHLCV 复刻；但 `divergence / pivot` 天生有回看与潜在重绘风险，所以 desk 迁移必须统一冻结成 `signal 当根及之前数据 + next-bar open + no-overlap`，并拆成 `with_divergence` / `without_divergence` 两版，禁止把未来 pivot 右侧确认、主观 `news peak` 叙事或 repo reversal 用途偷渡成 15m continuation alpha。

## 本轮新增产物
1. Source-intake artifact：
   - `reports/artifacts/literature/scout_rank75_gcr_exhaustion_veto_source_intake_card.csv`
2. Reader-facing 页面：
   - `reports/site/reading/repo_scout/rank75_gcr_exhaustion_veto_source_intake.html`
3. Queue-facing 更新：
   - `docs/TODO.md` 顶部 `TRADING DESK BOARD / Next 3 bot3 runs`

## Hard verdict
**`Rank 75 / GCR extreme-sentiment exhaustion veto = guard-passed / admit_to_clean_replication_queue`**

## 为什么是这个 verdict
- 规则能清楚写成 `trade on / trade off`：它不是新 alpha，而是 shared `不要追最后一脚` failure veto；
- 源码里的关键部件（`RSI/Stoch`、`volume spike / exhaustion`、`BB edge`）都可清楚复刻，而且没有一眼可判死刑的未来函数；
- 真正需要额外小心的是 `divergence / pivot` 的实时口径，因此最小 replication 必须明确拆分 `with_divergence` 与 `without_divergence`，先回答改善是否只来自脆弱条件；
- 首轮实现足够便宜：只需要现有 `BTC/ETH/SOL 15m + 5m` cache，就能比较 `baseline / extreme_only / extreme_plus_volume / extreme_plus_volume_plus_bb / full_gcr(with_divergence)`；
- 但它现在仍只是 admitted，不是已验证 alpha；下一轮若 clean replication 发现改善主要来自极端砍单、或只在 divergence 版勉强成立，就应快速压回 `park / evidence pool`。

## 对交易台顺序的影响
- 当前最新 `Next 3` 已更新为：
  1. `Run 1 = EMA due-check only`
  2. `Run 2 = 若 Rank 75 已 guard-passed 且 EMA 仍 waiting_not_due，则立刻给它 1 次最小 clean replication`
  3. `Run 3 = 若 Rank 75 这一轮直接 hard-fail / park，则立刻切到 Rank 76 / intraday clock polarity + event blackout gate 做 fresh source intake；只有 fresh source 这一层也 exhausted 时，才允许回退到 one-regime-per-session overlay > Rank 35b > Rank 16b > tiny-live plumbing`
- 本轮后，当前合法 fast-lane 头部已不再是 `fresh source intake`，而是 `Rank 75 / GCR extreme-sentiment exhaustion veto minimal clean replication`。

## 最小验证
- 已确认以下输出文件存在：
  - `reports/artifacts/literature/scout_rank75_gcr_exhaustion_veto_source_intake_card.csv`
  - `reports/site/reading/repo_scout/rank75_gcr_exhaustion_veto_source_intake.html`
- 已确认 `docs/TODO.md` 顶板写回成功。

## 风险 / 边界
- 这条线来自 repo 工程规则，不是高等级学术证据；值钱的是规则口径清楚，不是原仓库绩效可直接照抄。
- `divergence / pivot` 是当前最大诚实性风险；如果带这层才看起来有效，就很可能只是脆弱的回看辅助，而不是稳健 veto。
- 这轮只做到 source intake + 两条轻量诚实守门，不展开 clean replication，也不顺手去开第二条 fresh source。

## 下一步建议
- 直接按顶板切到 **`Rank 75 minimal clean replication`**。
- 默认只比较 `baseline / extreme_only / extreme_plus_volume / extreme_plus_volume_plus_bb / full_gcr(with_divergence)` 五臂，不把它扩成新的 reversal 大研究。

## Commit hash
- 未提交。
- 原因：git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件，当前不适合安全 selective commit。
