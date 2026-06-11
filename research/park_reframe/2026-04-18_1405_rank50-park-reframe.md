# 2026-04-18 14:05 UTC · Rank 50 park reframe revisit

- source rank: `Rank 50 / chanlun-pro structural reclaim gate`
- current authoritative verdict: `park / evidence pool`
- this round verdict: `keep_park`
- original park verdict kept: `yes`

## Why this rank this round
- 本轮继续遵循 `bot6 park-reframe` 的低频轮转：默认先看 `50+`，并优先避开最近 `7` 天内刚复盘过的对象。
- `Rank 50` 上次 park-reframe 复盘是 `2026-04-03 20:14 UTC`，已明显超过 `7` 天窗口；同时 4 月中旬新增的 path-shape / structure-aware continuation 旁证，刚好适合回答一个问题：这些新证据是在救旧 `Rank 50`，还是在进一步证明“结构接受/失败”信息已经迁到别的宿主。

## Files read this round
### Required
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`

### Recent park-reframe context
- `research/park_reframe/2026-04-18_1117_rank34-park-reframe.md`
- `research/park_reframe/2026-04-18_0830_rank12-park-reframe.md`
- `research/park_reframe/2026-04-18_0602_rank11-park-reframe.md`
- `research/park_reframe/2026-04-03_2014_rank50-park-reframe.md`
- `research/park_reframe/2026-03-25_0657_rank50-park-reframe.md`

### Rank-specific source notes
- `research/optimization_loop/2026-03-18_0738_rank50-source-intake-guard-passed.md`
- `research/optimization_loop/2026-03-18_0829_rank50-clean-replication-park.md`

### Nearby evidence consulted
- `research/quant_digests/2026-04-17_2056_pathshape-downtrend-continuation-alpha.md`
- `research/quant_digests/2026-04-18_1140_mexc-pump-crosssection-continuation-alpha.md`

## 1) 原 rank 为什么 park？
原 `Rank 50` 想做的是：
- 把 `chanlun-pro structural reclaim` 压缩成一条可复用的结构确认层；
- 希望它能作为 `breakout / retest` 之后的共享 admission，帮助判断“这次站回结构是否值得继续做 continuation”。

原 clean replication 给出的审计结论到今天没变：
- `raw_breakout_retest @ 6bps/side`：`mean_total_return ≈ -9.34%`，`mean_trades ≈ 82.3`
- `structural_reclaim @ 6bps/side`：`mean_total_return ≈ -4.85%`，`mean_trades ≈ 12.7`
- `structural_reclaim_plus_htf @ 6bps/side`：`mean_total_return ≈ -4.63%`，`positive_asset_ratio = 0/3`，`mean_trades ≈ 12.0`，`mean_false_reclaim_ratio ≈ 72.78%`，`mean_no_trade_ratio ≈ 87.14%`

所以它被 park 的根本原因不是“结构确认主题完全没信息”，而是：
**把 structural reclaim 写成 queue-facing、跨宿主可复用的共享确认 gate，这个职责没有站住。**

更直白地说：
- 它确实比 raw breakout 少亏；
- 但改善主要来自极端砍交易；
- post-cost 仍然明显为负；
- `false reclaim` 比例又很高，说明看似结构站回的事件大多不够可靠。

## 2) 它更像 hard park 还是 soft park？
本轮判断：**仍是 soft park，但比 4 月 3 日那轮更接近 hard park with consumed residual。**

为什么还保留一点 soft：
1. 相比 raw baseline，等待结构回收确实减少了无脑追 breakout 的亏损；
2. 说明“结构接受 / 失败判决”这层语义不是零信息。

为什么又更接近 hard：
1. 最终 pocket 仍没有跨资产转正；
2. `mean_no_trade_ratio ≈ 87.14%`，shared gate 主要靠极端降频成立；
3. 真正留下的信息越来越像 `false reclaim` / `acceptance failure` 这种 verdict 形状，而不是一条还能独立排队的 admission hypothesis；
4. 4 月中旬新增证据继续把结构主题推向新的 event-defined / path-defined raw-alpha 宿主，而不是把旧 `Rank 50` 拉回 queue-facing。

## 3) 有没有“可救信号”？
**有，但更像主题级残余，不再属于旧 `Rank 50` 本体。**

本轮两条更 relevant 的旁证都指向同一件事：
- `2026-04-17_2056_pathshape-downtrend-continuation-alpha.md` 说明，若结构/路径信息还有 edge，更诚实的主语更像“事件后路径形状是否继续单边”，而不是抽象的 shared reclaim gate；
- `2026-04-18_1140_mexc-pump-crosssection-continuation-alpha.md` 进一步说明，若要做 continuation，信息更像落在更窄的 burst / exhaustion / follow-through 事件宿主上。

这意味着：
- `Rank 50` 留下的确实不是零信息；
- 但信息的落点更像“结构接受失败后的 followthrough”或“更窄事件后的 continuation verdict”；
- 它们救活的是新的 event/path-shape family，而不是旧 `Rank 50` 的 shared structural-reclaim 写法。

## 4) 最值得改的唯一一刀是什么？
如果只允许保留 **1 条唯一主修改轴**，本轮最诚实的一刀仍只能写成：

**把 shared structural-reclaim admission，进一步降级成 structure-acceptance / false-reclaim verdict note。**

也就是：
- 不再让 `Rank 50` 自己承担三条 base setup 的可执行确认键；
- 只承认它在“这次站回到底是真接受，还是短暂 reclaim 后重新掉回去”这一层还有 residual 信息量。

但这条一刀依然不值得再写成新的 `Rank 50b`，因为：
1. 一旦降到 note / verdict 层，它已经不再是 bot2 可直接判断是否入板的 queue-facing 提案；
2. 它与既有 `Rank 31b` 一类 failure-followthrough 语义仍高度邻近；
3. 4 月中旬新证据给出的更自然做法，是把主题迁移到新的 event-defined / path-shape raw-alpha 宿主，而不是继续借 `Rank 50` 的壳排队。

## 5) 是否值得形成新的 derived hypothesis？
结论：**不值得；本轮维持 `keep_park`。**

原因：
1. 原 `park` verdict 的审计意义仍然很强，没被推翻；
2. 旧 rank 唯一还能保留的 residual，已经缩到 `structure-acceptance / false-reclaim verdict` 这类诊断层；
3. 这层 residual 既不够独立，也已被邻近 failure family 和更新的 event/path-shape family 基本吸收；
4. 若现在硬 draft `Rank 50b`，大概率只是在用旧 rank 名字重复已有失败语义，或偷偷借壳新 raw-alpha family。

## 6) 审计式回答（按本轮固定模板）
### 原 rank 为什么 park？
- 因为 `structural_reclaim` 作为共享确认 gate 的改善主要来自极端砍交易；post-cost 仍负，`false_reclaim_ratio` 很高，跨资产也没有形成可部署 pocket。

### 更像 hard park 还是 soft park？
- `soft park`，但已更接近 `hard park with consumed residual`。

### 有没有“可救信号”？
- 有；但只剩主题级残余，更像新的 event-defined / path-shape raw-alpha 宿主，而不是旧 `Rank 50` 本体。

### 最值得改的唯一一刀是什么？
- 把 shared structural-reclaim admission 降级成 structure-acceptance / false-reclaim verdict note。

### 是否值得形成新的 derived hypothesis？
- 不值得；继续 `keep_park` 更诚实。

## Final verdict
**`keep_park`**

- 原 `park` verdict 保留；
- `Rank 50` 更像 soft park 向 hard park with consumed residual 收紧；
- 当前“可救信号”属于更窄的 event/path-shape continuation family，而不是足以再诚实派生旧 `Rank 50` 的 `Rank 50b`。

## Queue impact
- `docs/PARK_REFRAME_QUEUE.md`：仅在 `Recently reviewed` 追加一条 `Rank 50 / keep_park` 简记；
- `research/park_reframe/INDEX.md`：追加本轮索引；
- 默认不改 `docs/TODO.md` 顶部排班；
- 不新增 active reframe candidate。

## Commit note
- 本轮只做最小必要文档改动。
- 共享工作区存在与本轮无关的脏文件，因此不做 selective commit，避免混提。
