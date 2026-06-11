# 2026-03-18 10:36 UTC · Rank 18 park reframe review

## Scope
- Source rank: `Rank 18 EMA neighborhood consensus / plateau-stable crossover`
- Original verdict stays: `park / evidence pool`
- This round only asks: **should Rank 18 derive one narrower reframe hypothesis, without overturning the original park?**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- recent reframe logs:
  - `research/park_reframe/2026-03-18_0836_rank31-park-reframe.md`
  - `research/park_reframe/2026-03-18_0629_rank16-park-reframe.md`
  - `research/park_reframe/2026-03-18_0429_rank15-park-reframe.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_0249_rank18-ema-plateau-intake.md`
  - `research/optimization_loop/2026-03-17_0309_rank18-clean-replication-park.md`
  - `research/quant_digests/2026-03-18_0122_rank32b-slope-floor-continuation-gate.md`

## Why this rank
- It is within `Rank 1~37` and currently parked.
- It has **not** been reviewed by `bot6` in the recent 7-day reframe queue.
- At first glance it looks salvageable because the original loss shape was not a total blow-up; the best variant merely looked like “too sparse but maybe cleaner.”
- But the most natural rescue story for this rank — **stop chasing a wider EMA-neighborhood vote, keep the simpler directional core, and remove overly aesthetic reclaim/consensus layers** — has already been substantially consumed by adjacent EMA-family evidence, especially `Rank 32 -> Rank 32b`.

## 1) 原 rank 为什么 park？
Rank 18 被 park，不是因为“EMA 家族完全没用”，而是因为 **“邻域投票 / 平台共识” 这条具体写法没有形成可升格 pocket**。

原 clean replication 关键证据：
- `anchor_10_40 @ 6bps/side`：约 `-30.21%`
- `row_consensus_2of3 @ 6bps/side`：仍为负
- `plateau_vote_5of9 @ 6bps/side`：仍为负
- `plateau_vote_5of9_spread_guard @ 6bps/side`：`mean_total_return≈-19.89%`、`positive_asset_ratio=0/3`、`mean_trades≈157.0`、`mean_no_trade_ratio≈68.48%`
- 成本梯度继续恶化：`10/15/20bps` 全线更差
- 参数邻域没有出现从负到正的稳定平台证据

更直白地说：
- 它不是单点参数比邻域差；
- 而是连“把单点扩成小邻域共识”之后，也只是 **少亏，不是转正**；
- 所以原 `park` verdict 必须保留。

## 2) 它更像 hard park 还是 soft park？
**更像 `hard park`。**

原因不是因为它数字最惨，而是因为：
- 原 rank 最想回答的问题就是“别找神奇单一 EMA 参数，先看有没有参数平台”；
- 这件事本身已经被 Rank 18 正面测试过；
- 结果显示平台票决并没有把策略从负 pocket 拉回 admission 线。

更重要的是，EMA 家族里最自然的窄救法已经被旁支证据继续往前推过：
- `Rank 32` 表明真正更有信息量的，不是“更宽的 EMA 邻域投票”，而是 **更简单的 slope-aligned continuation 方向层**；
- `Rank 32b` 进一步说明：**删掉额外 reclaim 美学、只保留 slope floor**，才是当前更诚实的单轴重写。

也就是说：
- Rank 18 的失败不像“还没找到对的表达”；
- 更像“原本最自然的邻域平台故事已经试过，而真正可能存活的那条窄轴，已经被隔壁 EMA 分支先消费掉了”。

## 3) 有没有“可救信号”？
**只有弱信号，没有足够诚实的可救信号。**

弱信号在于：
- `plateau_vote_5of9_spread_guard` 相比 `anchor_10_40` 的确少亏；
- 说明“只看单点 EMA 交叉”并不是最好的表达。

但为什么仍不够：
1. 这个改进只是 **少亏**，不是跨资产存活；
2. `positive_asset_ratio=0/3` 说明它没有形成干净 pocket；
3. 真正看起来更像可救的那条轴，已经不是“再调投票阈值 / 再调 spread guard”，而是 **回到更简单的 continuation core**；
4. 而这条更简单的救法，已经被 `Rank 32 / 32b` 以更直接、更贴 desk 主线的方式实现并消费。

所以当前更像是在说：
- Rank 18 给出了一个有价值的否定结论：**EMA 平台共识并没有自动比简单 directional gate 更好**；
- 但这不等于它自己还值得再派生 `Rank 18b`。

## 4) 最值得改的唯一一刀是什么？
**当前没有值得再切的唯一一刀。**

表面上最像的一刀是：
- 删掉较宽的 neighborhood vote / spread guard，回到更简单的 EMA directional continuation gate。

但这刀事实上已经被旁支证据消费：
- `Rank 32` 已经把 EMA 家族改写成 `EMA cross + slope direction gate`；
- `Rank 32b` 更进一步把“删 reclaim、保留 slope floor”写成了真正的窄派生假设，并且已经成功进入更高层级。

因此如果这轮还硬写 `Rank 18b`，大概率只会变成：
- 再换 vote threshold
- 再缩 neighborhood
- 再调 spread guard
- 或者最后偷偷重写成一个和 `Rank 32b` 很像的东西

前两种只是继续磨已失败的原轴；最后一种则是在**重复命名已被邻近 rank 消费的救法**。这都不符合“每轮最多 1 条唯一主修改轴”的规则。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

理由：
- 原 rank 的 `park` 仍有明确审计意义；
- 它最自然的单轴救法不是没想到，而是已经被 `Rank 32 / 32b` 这条更贴近 desk 的 EMA continuation 分支消费；
- 再派生 `Rank 18b`，更像在 EMA 家族内部重复包装相近故事，不像真正新的窄 hypothesis。

## 6) trade on / trade off 结论
本轮**不形成**新的 `Rank 18b`。

更诚实的保留口径是：
- `trade on` 故事并非荒谬；
- 但当前真正有信息量的结论已经变成：**“EMA 邻域平台共识” 不足以救活这条线，而更简单的 continuation 重写应归到 `Rank 32b` 那类分支，而不是继续在 Rank 18 名下续命。**
- 因此在出现新的外部证据之前，不应继续把 Rank 18 包装成新的入板候选。

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `hard park`

## Minimal audit note
This round does **not** reopen Rank 18 itself.
It records that the most obvious salvage story — replacing wider EMA-neighborhood consensus with a simpler continuation core — has already been substantially consumed by adjacent EMA-family evidence (`Rank 32 -> Rank 32b`). So the honest action this round is to **keep Rank 18 parked**, not draft `Rank 18b`.

## Git
- 本轮只做最小必要文档改动；未做 commit。
- 原因：工作区存在大量无关脏文件与未跟踪文件，当前不适合安全地 selective commit。
