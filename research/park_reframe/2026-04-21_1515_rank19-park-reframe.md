# 2026-04-21 15:15 UTC · Rank 19 park reframe

## Selected rank
- `Rank 19`
- selection note: 本轮严格限定在 `Rank 1~37` 的已 `park` 条目内；`Rank 2 / Rank 17 / Rank 29 / Rank 32b` 当前都不属于应被 bot6 低频复盘的 parked 对象。`Rank 19` 上次 bot6 复盘是 `2026-04-14 13:41 UTC`，已超出最近 `7` 天窗口，且仍处于 parked 语境，因此本轮认领它。

## Read set
- `docs/BOT6_PARK_REFRAME_BRIEF.md`
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- source / prior rank evidence:
  - `research/optimization_loop/2026-03-17_0320_rank19-box-consolidation-park.md`
  - `research/optimization_loop/2026-04-09_1116_rank19b_fresh_intake_background_absorbed.md`
  - `research/park_reframe/2026-04-14_1341_rank19-park-reframe.md`
- related side evidence:
  - `research/quant_digests/2026-03-30_1212_bb-compression-bottomquartile-breakout-alpha.md`
  - `research/quant_digests/2026-04-06_0940_quality-weighted-squeeze-release-alpha.md`
  - `research/quant_digests/2026-04-19_1746_bbsqueeze-release-shortbasket-alpha.md`

## 1) 原 rank 为什么 park？
原 `Rank 19 / box consolidation / structure breakout` 被 park 的原因没有变：
- 宽版 `accumulation_ready / narrow_accum_ready` 在 `BTC/ETH/SOL 120d 15m` 上是高交易数持续亏损；
- 更窄的 `box_breakout_ready` 虽然少亏，但 `mean_trades≈9.3`、`mean_no_trade_ratio≈99.91%`，稀到不足以诚实 admission；
- 时间、参数、跨资产、成本四项都没有把它拉回可部署区间。

换句话说，被否掉的是“把 compression 直接写成 standalone box-breakout 策略”这件事，而不是 compression 主题本身永远没信息。

## 2) 它更像 hard park 还是 soft park？
**本轮判断：仍是 `soft park`，但已经更接近 `hard park with consumed residual`。**

原因：
1. 对旧 standalone `box breakout` 读法，主 blocker 早已是硬失败；
2. 旧 rank 唯一自然 residual 仍只到既有 `Rank 19b`；
3. 而 `Rank 19b` 又已在 `2026-04-09` 的 first verdict 中收口为 `background / P0 / absorbed`，说明旧 rank 语境下的可救余量已经基本消费完。

## 3) 有没有“可救信号”？
**只有主题级可救信号，没有旧 rank 级的新可救信号。**

这轮新增旁证主要是：
- `2026-04-19` 的 `BB squeeze release breakdown × alt short basket` 继续说明，compression / squeeze 若还能留下净边，更像一条带有完整方向、出场与组合壳的 raw-alpha；
- 它没有把旧 `Rank 19` 的 standalone box-breakout spine 救回来；
- 也没有提供一条区别于既有 `Rank 19b` 的新单轴 residual。

因此当前还能保留的“可救信号”只能写成：
> compression 主题没死，但它救活的是新的 breakout / squeeze-release raw-alpha 宿主，不是旧 `Rank 19` 再派生一条 `Rank 19c`。

## 4) 最值得改的唯一一刀是什么？
如果今天仍要回答“唯一最值得改的一刀”，答案**仍然只有既有 `Rank 19b` 那一刀**：

> **把 standalone box-consolidation breakout 降级成 close-range compression shared long-admission + short-veto gate。**

但关键也在这里：
- 这刀已经起草过；
- 且已在 `2026-04-09` 的 first verdict 里被判定为 `background / P0 / absorbed`；
- 所以本轮不存在第二条仍诚实、且不同于 `Rank 19b` 的唯一主修改轴。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。本轮继续 `keep_park`。**

原因：
1. 原 `park` verdict 没被推翻；
2. 新证据继续把 compression 主题上移到新的完整 raw-alpha / shell 宿主，而不是修复旧 `Rank 19`；
3. 旧 rank 唯一诚实 residual `Rank 19b` 已经收口为 `background / P0 / absorbed`；
4. 若现在硬写 `Rank 19c`，本质是在拿新的 squeeze/breakout family 给旧 rank 续命，会削弱原审计边界。

## 单轮审查模板回答
### 原 rank 为什么 park？
因为 standalone `box consolidation breakout` 在 clean replication 中表现为：宽版持续亏、窄版极端稀疏，不足以 admission。

### 它更像 hard park 还是 soft park？
`soft park`，但已更接近 `hard park with consumed residual`。

### 有没有“可救信号”？
有主题级可救信号，但属于新的 breakout / squeeze-release raw-alpha 宿主；旧 rank 级 residual 仍只到 `Rank 19b`，且 `Rank 19b` 已在 `2026-04-09` 收口为 `background / P0 / absorbed`。

### 最值得改的唯一一刀是什么？
仍然只是既有 `Rank 19b`：把 standalone box breakout 降级成 `close-range compression` shared long-admission + short-veto gate。

### 是否值得形成新的 derived hypothesis？
不值得。本轮继续 `keep_park`。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `soft park，但已更接近 hard park with consumed residual；原 standalone box-breakout 的 blocker 未变，旧 rank 唯一诚实 residual 仍只到既有 Rank 19b，而 2026-04-19 新增的 squeeze-release short-basket 证据继续说明 compression 主题若还有信息，更像新的完整 breakout / squeeze raw-alpha 宿主，因此当前不诚实 draft Rank 19c。`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`
- 未改：`docs/TODO.md`

## Commit
- 本轮不做 commit。
- 原因：git 工作区存在大量与本轮无关的共享脏文件 / 未跟踪文件；本轮只做最小必要文档改动，避免混提。
