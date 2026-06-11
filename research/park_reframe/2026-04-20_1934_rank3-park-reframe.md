# 2026-04-20 19:34 UTC — Rank 3 park reframe review

## 本轮对象
- `Rank 3 / third-touch + EMA/MACD confluence`
- 原始结论保留：`park / evidence pool`
- 本轮输出：`keep_park`

## 为什么这轮看 Rank 3
- 本轮只处理 1 条已 `park` rank，且不改 `docs/TODO.md` 顶部排班。
- `Rank 3` 上一次 bot6 复盘是 `2026-04-12 18:45 UTC`，距今已超过 7 天内“无新证据不重复”的默认避让线；本轮有新增证据可看：
  - `research/quant_digests/2026-04-19_2049_retest-rebreak-short-continuation-alpha.md`
  - `research/quant_digests/2026-04-20_1310_liquidity-sweep-rejection-bounce-alpha.md`
- 本轮只回答一件事：这些新增证据，是否把旧 `Rank 3` 从 `keep_park` 推到值得派生一条诚实的窄 reframe hypothesis。

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/park_reframe/2026-04-12_1845_rank3-park-reframe.md`
- `research/optimization_loop/2026-03-16_0838_scout-rank3-first-verdict.md`
- `research/optimization_loop/2026-03-16_1434_scout-rank3-parameter-stability-park.md`
- `research/quant_digests/2026-04-19_2049_retest-rebreak-short-continuation-alpha.md`
- `research/quant_digests/2026-04-20_1310_liquidity-sweep-rejection-bounce-alpha.md`

## 1) 原 rank 为什么 park
原 `Rank 3` 被 park 的原因没有变：
- `third_touch_plus_ema_macd` 比 `raw_breakout` 干净很多，能切掉大量噪声；
- 但代价是样本极薄，`mean_trades ≈ 0.33` 笔/资产；
- 参数稳定性进一步把问题钉死：
  - `positive_neighbor_floor = pass (7/7 positive)`
  - `cross_asset_neighbor_floor = fail (0/7 >=2/3 正资产)`
  - `trade_count_neighbor_floor = fail (0/7 >=1 mean trades/asset)`

翻成人话：
- 它不是完全没信息；
- 但它的信息量只够当一个很窄的局部结构提示；
- 不够厚、不够广，撑不起独立 queue-facing setup。

## 2) 它更像 hard park 还是 soft park
**结论：更像 `hard park`。**

原因：
1. blocker 不是某个阈值差一点，而是 `third-touch direct trigger` 这个职责层本身太窄；
2. 原本最强 pocket 就建立在极低 trade density 上；
3. 这轮新增证据也没有把主语拉回 `third-touch + EMA/MACD`，反而进一步证明“结构性事件”若还有 edge，也应该写成更完整的 event-defined raw alpha。

## 3) 有没有“可救信号”
**有，但仍然不是旧 Rank 3 本体被救活。**

### 新证据怎么读
- `2026-04-19 retest-rebreak short continuation` 说明：
  - 真正可交易的结构信息，更像“break -> retest -> fail to repair -> re-break low”这种**事件定义完整**的 continuation raw alpha；
  - 值钱的是 re-break 事件本身，不是 `third-touch` 这个局部几何条件。
- `2026-04-20 liquidity sweep rejection bounce` 说明：
  - 另一侧也一样：真正能直接下单的，是“sweep -> reclaim -> bounce continuation”这种**完整 rejection 事件**；
  - 值钱的是 panic / rejection 被确认后的反应，而不是某个孤立触点条件。

### 为什么这仍救不了旧 Rank 3
因为两条新证据共同说明：
- 结构主题还有信息，但信息落在**更完整的事件壳**上；
- `third-touch + EMA/MACD` 最多只像这些事件里的一个局部结构注释；
- 若现在硬写 `Rank 3b`，本质是在借旧 rank 名义给一条新 family 续壳，不够诚实。

## 4) 最值得改的唯一一刀是什么
若只保留一刀，最诚实的唯一修改轴仍是：

> **把 `third-touch + EMA/MACD` 从独立 direct trigger，进一步降级成 event-defined structure family 的局部 structure-quality note。**

也就是：
- 不让它自己负责 entry 主语；
- 只在更完整的 `retest -> re-break` 或 `sweep rejection -> bounce` 一类事件已经成立时，把它当“局部结构是否干净”的附属说明。

## 5) 是否值得形成新的 derived hypothesis
**结论：不值得，继续 `keep_park`。**

原因：
1. 这条唯一修改轴没有救回旧 `Rank 3`，只是继续把它降级成别的 family 的旁注；
2. 新证据确实支持“结构型事件”还能活，但支撑的是新的 raw-alpha 宿主，不是 `Rank 3` 的诚实窄派生；
3. 若为了重开而强写 `Rank 3b`，会削弱原 `park` verdict 的审计意义。

## 单轮审查模板回答
### 原 rank 为什么 park？
因为它虽能把 `raw_breakout` 切得更干净，但只留下极少数局部事件；跨资产覆盖与 trade density 都不过线，不能当独立 setup。

### 它更像 hard park 还是 soft park？
`hard park`。

### 有没有“可救信号”？
有。近期 `retest -> re-break` 与 `sweep rejection -> bounce` 证据都说明结构主题仍有信息；但这些信息落在更完整的 event-defined raw-alpha 宿主上，不留在旧 Rank 3 身上。

### 最值得改的唯一一刀是什么？
把 `third-touch + EMA/MACD` 从独立 direct trigger，降级成 event-defined structure family 的局部 structure-quality note。

### 是否值得形成新的 derived hypothesis？
不值得。本轮继续 `keep_park`。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `hard park；4 月 19~20 日新增的 retest-rebreak 与 liquidity-sweep-rejection 证据继续说明结构主题能活在更完整的 event-defined raw-alpha 宿主里，但没有把 old Rank 3 的 third-touch direct-trigger 写法救回 queue-facing 窄派生，因此当前不诚实 draft Rank 3b`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`
- 未改：`docs/TODO.md`

## Commit
- 本轮默认不做 commit。
- 原因：工作区存在大量与本轮无关的已修改/未跟踪文件；本轮只做最小必要文档改动，避免混提。
