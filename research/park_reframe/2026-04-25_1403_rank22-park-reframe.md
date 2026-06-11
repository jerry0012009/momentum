# 2026-04-25 14:03 UTC · Rank 22 park reframe review

## 本轮对象
- `Rank 22 / up/down wave + MA20 persistence gate`
- 原始结论保留：`park / evidence pool`
- 本轮输出：`keep_park`

## 为什么这轮看 Rank 22
- `Rank 1~37` 里近一周多数 parked rank 已被 bot6 低频扫过；本轮不重复碰 `Rank 2 / Rank 17` 这类非 parked 条目。
- `Rank 22` 上一次 park-reframe 是 `2026-04-19 21:15 UTC`，虽未满 7 天，但 4 月 24 日又新增了两条更直接的 downside/回吐旁证：
  - `research/quant_digests/2026-04-24_2355_liquidation-cascade-bounce-honest-portability.md`
  - `research/quant_digests/2026-04-24_2250_lowvolume-upmove-fade-alpha.md`
- 因此本轮要回答的窄问题是：这些新证据有没有把旧 `Rank 22` 的 `wave + MA persistence` gate 救回来，还是继续把“跌后修复 / 弱冲回吐”主题外流到新的 event-driven raw-alpha 宿主。

## Read set
- `docs/BOT6_PARK_REFRAME_BRIEF.md`
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- source / prior rank evidence:
  - `research/optimization_loop/2026-03-17_0437_rank22-clean-replication-park.md`
  - `research/park_reframe/2026-04-19_2115_rank22-park-reframe.md`
- new side evidence:
  - `research/quant_digests/2026-04-24_2355_liquidation-cascade-bounce-honest-portability.md`
  - `research/quant_digests/2026-04-24_2250_lowvolume-upmove-fade-alpha.md`

## 1) 原 rank 为什么 park？
原 `Rank 22` 被 park 的 blocker 没变：把“跌后修复”写成 **shared `up/down wave + MA20 persistence gate`**，最多只是让 baseline 少亏，但没有形成可 admission 的独立 edge。

`2026-03-17_0437_rank22-clean-replication-park.md` 的关键结果：
- 主变体 `updownwave_ma20`：`6bps/side` 下 `mean_total_return≈-7.94%`，`positive_asset_ratio=1/3`
- 邻域最不差的 `MA15`：也只有 `≈-3.26%`，仍未转正
- 时间稳定性：`bucket_2≈-12.70%` 明显失守
- 跨标的：`BTC≈-14.05%`、`ETH≈-18.92%`、`SOL≈+9.15%`
- 成本抬升到 `10/15/20 bps` 后继续快速恶化

所以原 `park` 的审计意义仍然清楚：
> 被否掉的是“slow wave + MA persistence gate”这层旧表达，而不是所有 downside-recovery / panic-bounce 主题都没信息。

## 2) 它更像 hard park 还是 soft park？
**本轮判断：仍是 `soft park`，但比 4 月 19 日那轮更接近 hard。**

原因：
1. 原 rank 至少留过 `SOL` 单腿 pocket，所以还不能说主题彻底归零；
2. 4 月 24 日新增证据没有修复旧 gate，反而更一致地把残余信息指向 **更快、更窄的 event-driven / single-name bounce 或 exhaustion fade**；
3. 因此今天还能保留的 soft 成分，越来越像主题级 residual，而不像旧 `Rank 22` 本体级 residual。

## 3) 有没有“可救信号”？
**有，但仍更像主题级可救信号，不属于旧 rank 级可救信号。**

两条新增旁证分别把主题往两个更诚实的新宿主上推：

### A. `joint liquidation crash -> short-window bounce`
来自 `2026-04-24_2355_liquidation-cascade-bounce-honest-portability.md`：
- 真正值得保留的是 **跨资产联动爆仓下杀 × 恐慌后反弹** 这条 raw alpha；
- 诚实 probe 后，`1h next-open long everything` 并不稳，说明不能把它简单回填成 shared gate；
- 但 `AAVE/LINK/SUI` 等 liquid alt pocket 仍留有弹性，说明“挤仓后修复”主题本身没死，只是更像 **event-defined bounce host**。

### B. `low-volume up-move -> short-window fade`
来自 `2026-04-24_2250_lowvolume-upmove-fade-alpha.md`：
- 这里保留下来的不是旧 Rank 22 的 `wave persistence`，而是 **弱参与上冲 -> 次段回吐** 这类更快、更局部的 exhaustion / fake-move 逻辑；
- `15m` 毛边还没死，但 `5m` 基本被成本打穿，说明同样不适合回写成一个慢 shared persistence gate。

合起来，这些新 evidence 更像在说：
> downside-recovery / fake-move 主题还活，但宿主更该是新的 `event-driven bounce` 或 `exhaustion fade` raw alpha。

而不是：
> `up/down wave + MA persistence` 这层 shared allow/deny gate 仍值得窄重开。

## 4) 最值得改的唯一一刀是什么？
如果今天还要回答“唯一最值得改的一刀”，最诚实的版本只能是：

> **放弃 slow `wave + MA persistence` shared gate，改写成 strongest-shock / event-defined 的短窗 bounce host。**

但这也是本轮不该 draft 的关键原因：
- 这已经不是旧 `Rank 22` 的窄 reframe；
- 它把主语从 shared gate 改成了 event-driven raw alpha；
- 若硬写成 `Rank 22b`，会把“新宿主”的证据误包装成“旧壳的小修”。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。本轮继续 `keep_park`。**

原因：
1. 原 `park` verdict 没被推翻；
2. 新 evidence 没有把 `wave + MA persistence gate` 修回可交易状态；
3. 新 evidence 只是在更明确地说明：可救信号属于新的 downside-shock bounce / exhaustion-fade raw-alpha 宿主；
4. 这类宿主若要进板，应走新的 fresh intake，而不是削弱 old `Rank 22` 审计意义的 `Rank 22b`。

## 单轮审查模板回答
### 原 rank 为什么 park？
因为 `wave + MA persistence gate` 在 clean replication 中只是减亏，不够形成 post-cost、跨资产、跨参数都能站住的 admission 级 edge。

### 它更像 hard park 还是 soft park？
`soft park`，但比 4 月 19 日那轮更接近 hard。

### 有没有“可救信号”？
有，但主要是 `joint liquidation crash -> bounce` 与 `low-volume upmove -> fade` 这类新的事件驱动 raw alpha；可救的是主题，不是旧 `Rank 22` 壳。

### 最值得改的唯一一刀是什么？
把 slow shared gate 改写成 strongest-shock / event-defined 的短窗 bounce host。

### 是否值得形成新的 derived hypothesis？
不值得。本轮继续 `keep_park`。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `soft park，但比 4 月 19 日那轮更接近 hard；4 月 24 日新增的 liquidation-cascade bounce 与 low-volume upmove fade 证据继续说明“跌后修复 / 弱冲回吐”主题仍有信息，但它更像新的 event-driven bounce / exhaustion-fade raw-alpha 宿主，而不是旧 Rank 22 的 wave + MA persistence gate，因此当前不诚实 draft Rank 22b。`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`
- 未改：`docs/TODO.md`

## Commit
- 本轮不做 commit。
- 原因：git 工作区存在大量与本轮无关的共享脏文件 / 未跟踪文件；本轮只做最小必要文档改动，避免混提。
