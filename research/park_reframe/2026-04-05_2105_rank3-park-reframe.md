# 2026-04-05 21:05 UTC — Rank 3 park reframe review

## 本轮对象
- `Rank 3 / third-touch + EMA/MACD confluence`
- 原始结论保留：`park / evidence pool`
- 本轮输出：`keep_park`

## 为什么这轮看 Rank 3
- 按 `bot6` 轮转规则，在最近几轮已连续覆盖 `50+` 与 `80~110` 后，本轮回到 `1~24` 号段。
- `Rank 3` 虽在早期 queue 里被复盘过一次，但最近 `7` 天内没有新的 `bot6` 单轮复盘记录。
- 更重要的是，今天新增了 `2026-04-05_1701_chartpattern-neckline-imbalance-alpha.md`：它把“结构完成后再等 neckline breakout + order-flow confirmation”重新做成了一条更诚实的 **raw alpha**。这正好适合拿来审计：原 `Rank 3` 到底只是死掉了，还是有一部分 residual value 值得收敛成新的窄 reframe。

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/park_reframe/2026-04-05_1823_rank65-park-reframe.md`
- `research/park_reframe/2026-04-05_1612_rank61-park-reframe.md`
- `research/optimization_loop/2026-03-16_0838_scout-rank3-first-verdict.md`
- `research/optimization_loop/2026-03-16_1434_scout-rank3-parameter-stability-park.md`
- `research/quant_digests/2026-04-05_1701_chartpattern-neckline-imbalance-alpha.md`
- `research/park_reframe/2026-03-22_0439_rank31-park-reframe.md`

## 1) 原 rank 为什么 park
根据 `2026-03-16_0838_scout-rank3-first-verdict.md` 与 `2026-03-16_1434_scout-rank3-parameter-stability-park.md`：
- 原始想法是把 **third touch + EMA/MACD confluence** 写成一条更窄的结构确认线，去过滤深负的 `raw_breakout`。
- 第一轮 first verdict 的确显示：
  - `third_touch_plus_ema_macd` 比 `raw_breakout` 诚实很多；
  - `mean_total_return≈+0.78%`、`mean_false_break_ratio=0.00%`；
  - 但 `positive_asset_ratio=1/3`，`mean_trades≈0.33` 笔/资产。
- 随后补齐参数稳定性后，真正的 blocker 被钉死：
  - `positive_neighbor_floor = pass (7/7 positive)`，说明单点方向不完全是错的；
  - 但 `cross_asset_neighbor_floor = fail (0/7 达到 >=2/3 正资产)`；
  - `trade_count_neighbor_floor = fail (0/7 达到 >=1 mean trades/asset)`。

翻成人话：
- 原 rank 被 park，不是因为“third-touch 结构确认完全没信息”；
- 而是因为：**它只在极少数事件里留下了局部干净 pocket，却没形成跨资产、可交易厚度足够的稳定 setup。**

## 2) 它更像 hard park 还是 soft park
**结论：`hard park`。**

为什么不是 soft park：
1. 原始 clean replication 的唯一亮点，本质上是“极窄门过滤后保留了很少几笔干净交易”，而不是形成了可以迁移的 setup；
2. 参数邻域虽然多数仍为正，但 trade density 与 cross-asset coverage 同时失败，这说明它不是“差最后一刀阈值”就能救；
3. 今天的新证据也没有把这条线拉回“third-touch direct trigger”这层，反而把主题重新指向了更完整的 pattern-breakout 主语。

## 3) 有没有“可救信号”
**有，但它们更像主题外流，不支持直接救原 Rank 3。**

### 可救信号
- `2026-04-05_1701_chartpattern-neckline-imbalance-alpha.md` 明确说明：
  - 结构化 price pattern 并没有死；
  - 真正更自然的主语是 **double-bottom / double-top neckline breakout**；
  - order-flow / taker-imbalance 更适合作为 breakout 后的局部 confirmation，而不是把 `third touch + EMA/MACD` 本身当成完整 setup。
- `2026-03-22_0439_rank31-park-reframe.md` 也已经把相邻 family 的 residual value 收敛到“false reclaim / failure-followthrough”那一支，说明结构主题的存活位置，更多在 **break / reclaim / fail** 这种更明确的事件形态里。

### 但这些信号为什么救不了旧 Rank 3
因为它们共同支持的是：
1. **结构完成后的 breakout / reclaim / failure 事件** 仍有信息；
2. 但 `third touch + EMA/MACD confluence` 作为一个独立 direct trigger，仍然过稀、过窄、过依赖局部 shape；
3. 也就是说，主题没死，但旧 rank 的职责层仍然写错了。

## 4) 最值得改的唯一一刀是什么
如果只允许保留一条“唯一主修改轴”，那最诚实的一刀会是：

> **把 `third-touch + EMA/MACD` 从独立 direct trigger，降级成 chart-pattern breakout family 的局部 structure-confirmation note。**

也就是：
- 不再要求它自己单独承担 entry 主语；
- 而是只把它理解成“更完整形态 breakout / reclaim 之前，局部结构是否足够像一个已成型的 touch-based setup”。

## 5) 是否值得形成新的 derived hypothesis
**结论：不值得，本轮维持 `keep_park`。**

原因：
1. 上面那一刀虽然是唯一诚实的救法，但它已经把主语换成了 **chart-pattern breakout family**；
2. 这会稀释原 `park` verdict 的审计意义——原 verdict 失败的是 `third-touch + EMA/MACD` 这条独立 setup，不是整个结构确认主题失败；
3. 若硬写 `Rank 3b`，更像是借原 rank 的名义，给一个新的 pattern-breakout raw-alpha family 续壳；
4. bot6 在这里更诚实的动作，应该是明确记录：
   - `Rank 3` 原审计结论保留；
   - 它只留下“局部结构确认有信息”的 residual note；
   - 真正值得追的东西，已经外流成新的 neckline-breakout raw-alpha family，而不是旧 rank 的窄派生。

## 单轮审查模板回答
### 原 rank 为什么 park？
因为它虽然能把 `raw_breakout` 切得更干净，但只留下极少数局部事件；跨资产覆盖与可交易厚度都不成立，不足以当独立 setup。

### 它更像 hard park 还是 soft park？
`hard park`。

### 有没有“可救信号”？
有。结构化 pattern breakout 主题仍有生命力，今天新的 neckline-breakout × taker-imbalance 证据就是旁证；但那更像新的 raw-alpha family，不是旧 Rank 3 本身可救。

### 最值得改的唯一一刀是什么？
把 `third-touch + EMA/MACD` 从独立 direct trigger，降级成 chart-pattern breakout family 的局部 structure-confirmation note。

### 是否值得形成新的 derived hypothesis？
不值得。因为这已经不是原 rank 的诚实窄派生，而更像新的 pattern-breakout family fresh intake。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `hard park；原 Rank 3 的 blocker 仍是 trade density 与跨资产覆盖不足，而今天新增的 chart-pattern neckline breakout 证据只说明结构确认主题更适合外流到新的 raw-alpha family，不足以再诚实派生 Rank 3b`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`
- 未改：`docs/TODO.md`

## Commit
- 本轮默认不做 commit。
- 原因：仓库存在无关脏文件；本轮只做最小必要文档改动，避免混提。
