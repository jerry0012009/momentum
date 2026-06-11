# 2026-04-14 13:41 UTC · Rank 19 park reframe

## Selected rank
- `Rank 19`
- selection note: 本轮严格限定在 `Rank 1~37` 的已 `park` 条目内。`Rank 2 / Rank 17` 虽未出现在近几天的 park-reframe 记录里，但它们属于存活的 `P3 continuity`，不属于本轮对象；因此改选近 `7` 天外、且仍处于 parked 语境的 `Rank 19`。

## Read set
- `docs/BOT6_PARK_REFRAME_BRIEF.md`
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- recent park-reframe references:
  - `research/park_reframe/2026-04-13_1006_rank22-park-reframe.md`
  - `research/park_reframe/2026-04-13_1451_rank5-park-reframe.md`
  - `research/park_reframe/2026-04-06_1713_rank19-park-reframe.md`
- source / prior rank evidence:
  - `research/optimization_loop/2026-03-17_0320_rank19-box-consolidation-park.md`
  - `research/optimization_loop/2026-04-09_1116_rank19b_fresh_intake_background_absorbed.md`
- related side evidence:
  - `research/quant_digests/2026-03-30_1212_bb-compression-bottomquartile-breakout-alpha.md`
  - `research/quant_digests/2026-04-06_0940_quality-weighted-squeeze-release-alpha.md`

## 1) 原 rank 为什么 park？
原 `Rank 19 / box consolidation / structure breakout` 被 park 的 blocker 没变：
- 宽版 `accumulation_ready / narrow_accum_ready` 在 `BTC/ETH/SOL 120d 15m` 上是高交易数持续亏损；
- 更窄的 `box_breakout_ready` 虽然少亏，但 `mean_trades≈9.3`、`mean_no_trade_ratio≈99.91%`，稀到不足以诚实 admission；
- 时间、参数、跨资产、成本四项都没有把它拉回可部署区间。

翻成人话：
> 被否掉的是“把 compression 直接写成 standalone box-breakout 策略”这件事，不是 compression 主题本身永远没信息。

## 2) 它更像 hard park 还是 soft park？
**本轮判断：仍是 `soft park`，但已经接近 `hard park with consumed residual`。**

原因：
1. 对原 standalone `box breakout` 读法，证据已基本是硬失败；
2. compression 主题仍可能在别的宿主里有信息，所以还不能把整个主题直接判成硬死；
3. 但旧 rank 唯一自然 residual——`Rank 19b`——已在 `2026-04-09` 的 fresh-intake first verdict 中收口为 `background / P0`，说明旧 rank 语境下的可救余量已经基本被消费完。

## 3) 有没有“可救信号”？
**有主题级可救信号，但没有旧 rank 级的新可救信号。**

这轮真正改变判断的，不是又多了一篇 squeeze 论文，而是两层证据已经一起闭环：
1. `2026-03-30` 与 `2026-04-06` 的 compression / squeeze digests 继续说明，若这主题还有活路，更像新的 standalone breakout / continuation raw-alpha 壳；
2. 旧 rank 语境下唯一诚实的降级表达 `Rank 19b`，又在 `2026-04-09` 被 first verdict 明确收口为 `background / P0 / absorbed`。

所以现在还能保留的“可救信号”只能写成：
> compression 主题没死，但它救活的是新的 raw-alpha 宿主，不是旧 `Rank 19` 再派生一条 `Rank 19c`。

## 4) 最值得改的唯一一刀是什么？
如果今天仍要回答“唯一最值得改的一刀”，答案**仍然只有既有 `Rank 19b` 那一刀**：

> **把 standalone box-consolidation breakout 降级成 close-range compression shared long-admission + short-veto gate。**

但关键点也正在这里：
- 这刀已经起草过；
- 且它已经在 `2026-04-09` 的 first verdict 里被判定为 `background / P0 / absorbed`；
- 因此本轮不存在第二条仍诚实、且不同于 `Rank 19b` 的唯一主修改轴。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。本轮继续 `keep_park`。**

原因：
1. 原 `park` verdict 没被推翻；
2. 新证据没有把 old `box breakout` 修回 queue-facing 候选；
3. 旧 rank 唯一诚实 residual `Rank 19b` 已被 first verdict 收口为 `background / P0`；
4. 若现在硬写 `Rank 19c`，本质是在拿新的 compression raw-alpha 家族给旧 rank 续命，会削弱原审计边界。

## 单轮审查模板回答
### 原 rank 为什么 park？
因为 standalone `box consolidation breakout` 在 clean replication 中表现为：宽版持续亏、窄版极端稀疏，不足以 admission。

### 它更像 hard park 还是 soft park？
`soft park`，但已接近 `hard park with consumed residual`。

### 有没有“可救信号”？
有主题级可救信号，但属于新的 compression / squeeze raw-alpha 宿主；旧 rank 级 residual 已被 `Rank 19b` 消费并在 `2026-04-09` 收口为 `background / P0`。

### 最值得改的唯一一刀是什么？
仍然只是既有 `Rank 19b`：把 standalone box breakout 降级成 `close-range compression` shared long-admission + short-veto gate。

### 是否值得形成新的 derived hypothesis？
不值得。本轮继续 `keep_park`。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `soft park，但已接近 hard with consumed residual；原 standalone box-breakout 的 blocker 未变，而既有唯一 residual Rank 19b 已于 2026-04-09 fresh-intake first verdict 收口为 background / P0；近期 compression / squeeze 证据继续说明主题若还有信息，更像新的 standalone raw-alpha / breakout-local family，因此当前不诚实 draft Rank 19c。`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`
- 未改：`docs/TODO.md`

## Commit
- 本轮不做 commit。
- 原因：git 工作区存在大量与本轮无关的共享脏文件 / 未跟踪文件；本轮只做最小必要文档改动，避免混提。
