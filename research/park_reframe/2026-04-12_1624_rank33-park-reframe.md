# 2026-04-12 16:24 UTC · Rank 33 park reframe review

## Scope
- source rank: `Rank 33 / NW + confirmed HL reclaim`
- original verdict stays: `park / evidence pool`
- this round asks only: after the newer `turning-point-confirmed continuation` and `candlestick shortlist × next-hour drift` evidence, does `Rank 33` still deserve to remain a soft reframe candidate, or is the more honest call now simply `keep_park`?

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- recent park-reframe references:
  - `research/park_reframe/2026-04-12_1401_rank9-park-reframe.md`
  - `research/park_reframe/2026-04-12_1114_rank35-park-reframe.md`
  - `research/park_reframe/2026-04-07_2055_rank33-park-reframe.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_1150_rank33-clean-replication-park.md`
  - `research/park_reframe/2026-03-23_1337_rank33-park-reframe.md`
  - `research/quant_digests/2026-04-08_2041_dynamic-turningpoint-tsmom-alpha.md`
  - `research/quant_digests/2026-04-07_2117_candlestick-shorthorizon-pattern-alpha.md`

## Why this rank this round
- 最近几轮 `50+ / 80~110` 已连续覆盖，本轮回到 `25~49` 段。
- `Rank 33` 上次 bot6 复盘是 `2026-04-07 20:55 UTC`，尚未满 7 天；但这次不是纯重复，因为 `2026-04-07~04-08` 新增了两条更偏 event-driven / pattern-drift 的旁证，足够回答一个新的问题：**这些新证据有没有把 Rank 33 留下来的 residual 更进一步外流到新宿主，以至于连 soft reframe candidate 都不再值得保留？**

## 1) 原 rank 为什么 park？
原 `Rank 33` 被 park 的原因并不复杂：
- `NW` 平滑和 `confirmed HL/LH reclaim` 确实能把部分假 reclaim 压掉；
- 但它没有把收益结构一起救活，反而留下了典型的 `中段亮、前后两端不站住` pocket；
- 一旦再叠 `highbreak`，又迅速退化成极度稀疏、靠不交易美化的写法。

原 clean replication 的关键数字：
- `raw_extrema_reclaim @ 6bps`: `mean_total_return≈-1.72%`，`positive_asset_ratio=1/3`，`mean_false_reclaim_ratio≈49.13%`
- `nw_hl_reclaim @ 6bps`: `mean_total_return≈-1.39%`，`positive_asset_ratio=1/3`，`mean_false_reclaim_ratio≈47.20%`
- `nw_hl_plus_highbreak @ 6bps`: `mean_total_return≈-8.51%`，`positive_asset_ratio=1/3`，`mean_no_trade_ratio≈98.71%`

原审计结论一直很清楚：
> 被否掉的不是“结构失败/真假 reclaim 主题完全没信息”，而是“`NW + reclaim` 本身可以诚实地作为 standalone continuation entry”。

## 2) 它更像 hard park 还是 soft park？
**本轮结论：仍保留 soft 的尾巴，但已经比 4 月 7 日那轮更接近 `hard park`。**

更准确地说：
- 对原始 standalone reclaim 读法，已经越来越接近 `hard park`；
- 仅剩的一点 soft 成分，也不再像可 queue-facing 的窄 reframe，而更像一句研究备注：`false reclaim / bad reclaim 可能有 verdict 价值`。

## 3) 有没有“可救信号”？
**有，但这次更清楚地说明：可救信号不再属于旧 Rank 33 宿主。**

### 还剩什么信号
旧证据留下来的唯一 residual，一直都是：
- `Rank 33` 对 `false reclaim / failure path` 的识别能力，可能比它对 continuation entry 的识别更有价值。

### 为什么这次反而更不值得救
新旁证并没有把 reclaim 本体救活，反而把它继续外推到别的宿主： 
1. `2026-04-08_2041_dynamic-turningpoint-tsmom-alpha.md`
   - 更像在说：真正值得交易的是 `turning-point-confirmed trend leg × short-horizon continuation`；
   - 主语已经变成 `turning point / new leg`，不是 `NW reclaim`。
2. `2026-04-07_2117_candlestick-shorthorizon-pattern-alpha.md`
   - 更像在说：少数 short-horizon pattern 本身就能给出 next-hour drift；
   - 主语已经变成 `pattern-shortlist × drift`，不是事后再做一层平滑 reclaim。

这两条新证据共同带来的不是“Rank 33 终于能 draft 了”，而是：
> 结构主题如果还值得追，更自然的宿主正在转向 `turning-point / pattern-drift / event-confirm` 这类新的 raw-alpha family；旧 Rank 33 只剩一层很薄的 failure-verdict 注释价值。

## 4) 最值得改的唯一一刀是什么？
如果今天还硬要保留唯一一刀，它仍然只能是：

> **把 `Rank 33` 从 standalone `NW + reclaim` entry，降级成 shared `false-reclaim veto / failure-routing note`。**

但和 4 月 7 日相比，本轮更明确的一点是：
- 这已经越来越不像一条值得单独占队列位置的 reframe hypothesis；
- 更像给别的、更完整的结构 raw alpha 做审计注脚。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。本轮结论是：`keep_park`。**

原因：
1. 原 `park` 审计意义必须保留，且没有被新证据推翻；
2. 4 月 7 日那轮还能勉强说它留有 `soft_reframe_candidate` 的尾巴，但 4 月 7~8 的新增证据继续把结构主题上移到 `turning-point / candlestick pattern / event-confirm` 新宿主；
3. 现在若再保留 `Rank 33` 的 soft 候选身份，容易制造一种错觉：好像只差一刀就能重开；
4. 更诚实的说法是：**旧 Rank 33 的唯一 residual 已经薄到只配做 verdict note，不足以继续占一个 queue-facing soft candidate 槽位。**

## 单轮审查模板回答
### 原 rank 为什么 park？
因为 `NW + confirmed reclaim` 虽稍微降低假 reclaim，但收益、跨资产覆盖和交易厚度都没一起成立；叠更严格确认后又滑向极端稀疏。

### 它更像 hard park 还是 soft park？
更接近 `hard park`；最多只剩一层很薄的 failure-verdict 注释价值。

### 有没有“可救信号”？
有，但那点信号更像外流到 `turning-point-confirmed continuation` 或 `pattern-shortlist drift` 这类新 raw-alpha 宿主，而不是旧 Rank 33 本体可救。

### 最值得改的唯一一刀是什么？
把 standalone `NW + reclaim` 彻底降级成 shared `false-reclaim veto / failure-routing note`。

### 是否值得形成新的 derived hypothesis？
不值得；本轮不 draft `Rank 33b`。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `soft park 的残余已进一步变薄并继续外流；4 月 7~8 的 turning-point / candlestick 新证据没有救活旧的 NW reclaim 读法，反而更明确地把结构主题推向新的 event-driven / pattern raw-alpha 宿主，因此当前不诚实继续保留 Rank 33 的 queue-facing soft reframe 身份`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`
- 未改：`docs/TODO.md`

## Commit
- 本轮默认不做 commit。
- 原因：git 工作区存在无关脏文件；本轮只做最小必要文档更新，避免混提。
