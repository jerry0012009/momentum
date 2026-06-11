# 2026-04-12 18:45 UTC — Rank 3 park reframe review

## 本轮对象
- `Rank 3 / third-touch + EMA/MACD confluence`
- 原始结论保留：`park / evidence pool`
- 本轮输出：`keep_park`

## 为什么这轮仍看 Rank 3
- 在 `Rank 1~37` 已 `park` 的条目里，当前未处于 active paper / P3 continuity 的可选项已经很少；`Rank 2 / 17 / 29` 仍在前排，不属于本轮对象。
- `Rank 3` 上次 bot6 复盘是 `2026-04-05 21:05 UTC`，虽未满理想的换条间隔，但这几天确实出现了**新证据**：
  - `2026-04-07_2117_candlestick-shorthorizon-pattern-alpha.md`
  - `2026-04-08_2041_dynamic-turningpoint-tsmom-alpha.md`
- 因此本轮只回答一件事：这些新证据有没有把旧 `Rank 3` 从 `keep_park` 推到值得再派生一条窄 reframe hypothesis。

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/park_reframe/2026-04-05_2105_rank3-park-reframe.md`
- `research/optimization_loop/2026-03-16_0838_scout-rank3-first-verdict.md`
- `research/optimization_loop/2026-03-16_1434_scout-rank3-parameter-stability-park.md`
- `research/quant_digests/2026-04-07_2117_candlestick-shorthorizon-pattern-alpha.md`
- `research/quant_digests/2026-04-08_2041_dynamic-turningpoint-tsmom-alpha.md`

## 1) 原 rank 为什么 park
原 `Rank 3` 被 park 的核心不是“third-touch 结构主题完全没信息”，而是：
- first verdict 虽然把 `raw_breakout` 的噪声切掉很多；
- 但最好版本 `third_touch_plus_ema_macd` 只留下极少样本：`mean_trades≈0.33` 笔/资产；
- 后续参数稳定性又明确钉死：
  - `positive_neighbor_floor = pass (7/7 positive)`
  - `cross_asset_neighbor_floor = fail (0/7 >=2/3 正资产)`
  - `trade_count_neighbor_floor = fail (0/7 >=1 mean trades/asset)`

翻成人话：
- 它像一个“能把噪声切干净的局部 shape guard”；
- 但不像一个能跨资产、能保住样本厚度的独立 setup。

## 2) 它更像 hard park 还是 soft park
**结论：更像 `hard park`。**

原因没有变：
1. 原线最强 pocket 仍然建立在极低 trade density 上；
2. blocker 不是某个阈值还没调对，而是“third-touch direct trigger”这个职责层本身太窄；
3. 这几天的新证据也没有把主语拉回 `third-touch + EMA/MACD`，而是继续把结构主题推向更完整的 pattern / turning-point raw-alpha 宿主。

## 3) 有没有“可救信号”
**有，但仍然是主题外流，不是旧 Rank 3 本体被救活。**

### 新证据带来的可救信号
- `2026-04-07_2117_candlestick-shorthorizon-pattern-alpha.md` 说明：
  - 少数 pattern shortlist 在 crypto 短周期上，确实更像“下一小时 drift 标签器”；
  - 可用主语是更完整的 multi-bar pattern，而不是 `third touch` 这种局部几何条件本身。
- `2026-04-08_2041_dynamic-turningpoint-tsmom-alpha.md` 说明：
  - 结构主题若还活着，更像“turning-point-confirmed trend leg × short-horizon continuation”；
  - 主语是局部转折被确认后的新 leg 续行，而不是 `third-touch + EMA/MACD` 自己承担完整 entry。

### 为什么这些信号仍救不了旧 Rank 3
因为它们共同指向：
- **可交易的信息落在更上位的 pattern / turning-point 事件上；**
- `third-touch + EMA/MACD` 最多只像其中一个局部结构注释；
- 若现在硬写 `Rank 3b`，本质是在借旧 rank 名义，给一个新 raw-alpha family 续壳。

## 4) 最值得改的唯一一刀是什么
若只保留一刀，最诚实的唯一修改轴仍是：

> **把 `third-touch + EMA/MACD` 从独立 direct trigger，进一步降级成 pattern / turning-point continuation family 的局部 structure-quality note。**

也就是：
- 不让它自己负责 entry 主语；
- 只在更完整的 pattern-breakout / turning-point-confirmation 已经成立时，用来补充“局部结构是否干净”。

## 5) 是否值得形成新的 derived hypothesis
**结论：不值得，继续 `keep_park`。**

原因：
1. 这条唯一修改轴没有救回原 `Rank 3`，只是继续把它降级成别的 family 的旁注；
2. 新证据确实说明“结构确认主题未死”，但它们支撑的是新的 pattern / turning-point raw alpha，不是 `Rank 3` 的诚实窄派生；
3. 继续 draft `Rank 3b` 会削弱原 `park` verdict 的审计意义——原结论失败的是 `third-touch + EMA/MACD` 这条独立写法，而不是整个结构主题。

## 单轮审查模板回答
### 原 rank 为什么 park？
因为它虽能把 `raw_breakout` 切得更干净，但只留下极少数局部事件；跨资产覆盖与 trade density 都不过线，不能当独立 setup。

### 它更像 hard park 还是 soft park？
`hard park`。

### 有没有“可救信号”？
有。近期 candlestick shortlist 与 turning-point continuation 证据都说明结构主题仍有信息；但这些信息已经外流到更完整的 pattern / turning-point raw-alpha 宿主，而不是留在旧 Rank 3 身上。

### 最值得改的唯一一刀是什么？
把 `third-touch + EMA/MACD` 从独立 direct trigger，降级成 pattern / turning-point continuation family 的局部 structure-quality note。

### 是否值得形成新的 derived hypothesis？
不值得。本轮继续 `keep_park`。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `hard park；4 月 7~8 日新增的 candlestick / turning-point 证据继续证明结构主题能活在更完整的 pattern / continuation raw-alpha 宿主里，但没有把 old Rank 3 的 third-touch direct-trigger 写法救回 queue-facing 窄派生，因此当前不诚实 draft Rank 3b`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`
- 未改：`docs/TODO.md`

## Commit
- 本轮默认不做 commit。
- 原因：仓库存在无关脏文件；本轮只做最小必要文档改动，避免混提。
