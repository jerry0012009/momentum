# 2026-04-12 21:15 UTC · Rank 27 park reframe review

## 本轮对象
- `Rank 27 / Mt.Gox neckline confirmation / pattern-complete breakout gate`
- 原始结论保留：`park / evidence pool`
- 本轮输出：`keep_park`

## 为什么这轮看 Rank 27
- 这轮仍只处理 1 条已 `park` rank。
- `Rank 27` 虽然在 `2026-04-06` 刚被 bot6 派生出 `Rank 27c`，按 7 天窗口本不该优先重看；但这里有两条**足够新的后续证据**，会改变 queue 解释：
  1. `2026-04-07_2150_rank27_breakoutbar_takerimbalance_first_verdict_background.md`
  2. `2026-04-11_0436_rank27_freshintake_first_verdict_background_family_overlap.md`
- 同时，`2026-04-07~04-08` 又补进了 `candlestick shortlist × next-hour drift` 与 `turning-point-confirmed continuation` 两条更上位的结构/形态旁证。
- 所以本轮只回答一个问题：**既有 `Rank 27c` 已经被 first-verdict 收口到 background / family overlap 后，旧 `Rank 27` 还应不应该继续保留 queue-facing reframe 身份？**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/optimization_loop/2026-03-17_0815_rank27-mtgox-neckline-clean-replication.md`
- `research/park_reframe/2026-03-30_1334_rank27-park-reframe.md`
- `research/park_reframe/2026-04-06_0606_rank27-park-reframe.md`
- `research/optimization_loop/2026-04-11_0436_rank27_freshintake_first_verdict_background_family_overlap.md`
- `research/quant_digests/2026-04-07_2117_candlestick-shorthorizon-pattern-alpha.md`
- `research/quant_digests/2026-04-08_2041_dynamic-turningpoint-tsmom-alpha.md`

## 1) 原 rank 为什么 park
原始 clean replication（`2026-03-17_0815_rank27-mtgox-neckline-clean-replication.md`）已经把主 blocker 审计清楚：
- `raw_breakout @ 6bps/side`：`mean_total_return≈-13.79%`，`positive_asset_ratio=0/3`，`mean_false_break_ratio≈71.56%`
- `neckline_confirm @ 6bps/side`：`mean_total_return≈-17.42%`，`positive_asset_ratio=0/3`，`mean_false_break_ratio≈62.50%`
- `neckline_confirm_plus_retest_hold @ 6bps/side`：`mean_total_return≈-3.03%`，`positive_asset_ratio=0/3`，`mean_false_break_ratio≈68.67%`

也就是：
- 直接 breakout 太容易假突破；
- 原版 neckline confirm 虽然稍微压了一些假突破，但收益更差；
- retest_hold 虽然能少亏，却没有把它救成跨资产、成本后可保留的独立对象。

所以原 `Rank 27` 被 park，不是因为 pattern / neckline breakout 主题完全没信息，而是因为：
**旧 rank 这套 confirmation 写法不成立。**

## 2) 它更像 hard park 还是 soft park
**本轮判断：`soft park`，但已经比 4 月 6 日那轮更接近 `hard park with consumed residual`。**

原因：
1. soft 的部分仍在：原始 blocker 始终集中在 confirmation layer，而不是 pattern-breakout 主题被彻底否掉；
2. 但更接近 hard 的地方也更清楚了：4 月 6 日新派生出的 `Rank 27c` 已经在 `2026-04-11` fresh-intake 首判中被收口为 `background / P0 / family overlap`；
3. 这说明旧 rank 最后那一点 queue-facing residual，已经被实际 first-verdict 证明**不够独立、不够 distinct**。

## 3) 有没有“可救信号”？
**有，但现在更明确地属于“主题外流”，而不是旧 Rank 27 还能继续派生。**

### 已经出现过的可救信号
- `Rank 27b`：把静态 `retest_hold` 改成 `ATR-scaled retest zone + bounce reclaim`
- `Rank 27c`：把 post-break 回踩确认改成 `breakout-bar taker-imbalance confirmation`

这两条都对准了同一个 blocker：**confirmation 写法太粗。**

### 为什么现在仍不值得继续救
因为最新 runtime truth 已经把这两层 residual 的命运说清楚了：
- `27b` 没把对象救活；
- `27c` 虽然是一条诚实单轴，但 `2026-04-11` 首判明确写明：它的上位 alpha 语义已经被现有 breakout / flow-confirm 家族吸收，当前对象缺少可审计的独立执行主语。

再加上 `2026-04-07~04-08` 两条新 digest：
- `candlestick shortlist × next-hour drift`
- `turning-point-confirmed trend leg × short-horizon continuation`

共同说明：
> 如果结构/形态主题还值得追，更自然的宿主已经是更完整的 pattern-drift / turning-point continuation raw-alpha family，而不是继续在旧 `Rank 27` 里细切新的 confirmation 变体。

## 4) 最值得改的唯一一刀是什么
如果今天还要回答“最值得改的一刀”，答案仍然只能是：

> **把旧的 post-break 价格确认，改成 breakout 当下的更即时 confirmation（如 `27c` 的 taker-imbalance confirmation）。**

但本轮关键不在于这刀不存在，而在于：
- 这刀已经被诚实地写过；
- 且已经被 fresh-intake 首判证明缺乏独立 distinctness；
- 所以它现在只能作为**已消费 residual**，不能再继续占一个 queue-facing active candidate 槽位。

## 5) 是否值得形成新的 derived hypothesis
**不值得。结论是：继续 `keep_park`。**

原因：
1. 原 `park` verdict 完全没有被推翻；
2. 原线唯一自然 blocker（confirmation 写法）已经先后被 `27b` 与 `27c` 两条单轴尝试覆盖；
3. `27c` 又已经在 2026-04-11 first verdict 中收口为 `background / family overlap`，说明旧 rank 的 queue-facing residual 已被消费；
4. 4 月 7~8 日的新证据没有把旧 `Rank 27` 救回独立身份，反而继续把结构主题上移到更完整的新 raw-alpha 宿主。

因此现在若继续保留 `Rank 27c` 在 active reframe candidates，反而会削弱原 park 审计结论的清晰度。

## 单轮审查模板回答
### 原 rank 为什么 park？
因为 raw breakout 假突破太高，旧的 neckline confirm 虽少一点假突破但收益更差，而 retest_hold 也只做到少亏、没做到救活。

### 它更像 hard park 还是 soft park？
`soft park`，但现在已接近 `hard park with consumed residual`。

### 有没有“可救信号”？
有。可救信号一直集中在 confirmation 重写；但这部分 residual 已被 `27b / 27c` 消费，其中 `27c` 又已被 first-verdict 收口为 family overlap。

### 最值得改的唯一一刀是什么？
仍然是把 post-break 慢确认改成 breakout 当下的更即时 confirmation；代表版本就是既有 `Rank 27c` 的 `breakout-bar taker-imbalance confirmation`。

### 是否值得形成新的 derived hypothesis？
不值得。本轮继续 `keep_park`。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `soft park，但已接近 hard with consumed residual；原线最后一条诚实确认轴已在既有 Rank 27c 中表达，并于 2026-04-11 fresh-intake 首判收口为 background / family overlap；4 月 7~8 日新增的 candlestick / turning-point 证据继续把结构主题上移到更完整的 pattern-drift / continuation raw-alpha 宿主，因此当前不诚实继续保留 Rank 27c 为 queue-facing active candidate`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`
- 未改：`docs/TODO.md`

## Commit
- 本轮不做 commit。
- 原因：git 工作区存在大量与本轮无关的未跟踪/脏文件；本轮只做最小必要文档改动，避免混提。
