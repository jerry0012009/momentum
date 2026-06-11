# 2026-04-19 23:36 UTC · Rank 33 park reframe revisit

## Scope
- source rank: `Rank 33 / NW + confirmed HL reclaim`
- original verdict stays: `park / evidence pool`
- this round only asks: after the newer `path-shape downside continuation` evidence, does old `Rank 33` still leave an honest narrow reframe, or should it simply remain parked?

## Why this rank this round
- 按 `Rank 1~37` 的低频轮转继续往前走；`Rank 33` 上次 bot6 复盘是 `2026-04-12 16:24 UTC`，已超过最近 `7` 天回避窗口。
- 它已经从 earlier `soft_reframe_candidate` 收口为 `keep_park`，但仍值得用一条更新证据回答：**结构 residual 到底还留在 old reclaim family 里，还是已经继续外流到新的 path-shape / downside-continuation 宿主。**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- recent references:
  - `research/optimization_loop/2026-03-17_1150_rank33-clean-replication-park.md`
  - `research/park_reframe/2026-04-07_2055_rank33-park-reframe.md`
  - `research/park_reframe/2026-04-12_1624_rank33-park-reframe.md`
  - `research/optimization_loop/2026-04-08_1111_rank33_fresh_intake_first_verdict_background_sync.md`
  - `research/quant_digests/2026-04-17_2056_pathshape-downtrend-continuation-alpha.md`

## 1) 原 rank 为什么 park？
原 `Rank 33` 被 park 的核心原因没有变化：
- `NW` 平滑与 `confirmed HL/LH reclaim` 确实能略微压低假 reclaim；
- 但压低假 reclaim 没有同步长成可交易收益；
- 一旦再叠更强确认（如 `highbreak`），又迅速滑向极度稀疏、靠不交易美化。

原 clean replication 的硬证据仍然是：
- `raw_extrema_reclaim @ 6bps`：`mean_total_return≈-1.72%`，`positive_asset_ratio=1/3`，`mean_false_reclaim_ratio≈49.13%`
- `nw_hl_reclaim @ 6bps`：`mean_total_return≈-1.39%`，`positive_asset_ratio=1/3`，`mean_false_reclaim_ratio≈47.20%`
- `nw_hl_plus_highbreak @ 6bps`：`mean_total_return≈-8.51%`，`positive_asset_ratio=1/3`，`mean_no_trade_ratio≈98.71%`

所以原审计被否掉的不是“结构真假 reclaim 完全没信息”，而是：
> `NW + reclaim` 这层 standalone continuation entry 写法本身不够诚实。

## 2) 它更像 hard park 还是 soft park？
**本轮判断：仍可叫 `soft park`，但已比 4 月 12 日那轮更接近 `hard park with consumed residual`。**

原因：
- 还带一点 `soft`，因为 old Rank 33 确实留下过很薄的 `false reclaim / bad reclaim` 判决价值；
- 但越来越接近 `hard`，因为这点 residual 现在已经不太像 old `NW + reclaim` family 自己还能诚实切出一条 queue-facing 单轴，而更像会被别的 event-defined / path-defined 宿主吸收。

## 3) 有没有“可救信号”？
**有很薄的可救信号，但它不再像 old Rank 33 自己的可救信号。**

旧 residual 仍然只有一条：
- `false reclaim / failure path` 可能比 `reclaim continuation` 本身更有信息。

但 `2026-04-17_2056_pathshape-downtrend-continuation-alpha.md` 新增的证据，进一步把这点 residual 往别的宿主上移：
- 这条新证据真正有信息的主语，是 **短窗内更单边、更贴近区间低点的 downside path shape → 后续继续下滑**；
- 它的最像样 pocket 来自 `15m downside continuation`，尤其是 `SOL 15m short`；
- 它强调的是 **路径单边性 / close-near-low / downside continuation**，不是 old Rank 33 那种“先平滑，再等 HL reclaim”语义。

因此，新证据没有救活 `NW reclaim`，反而把结构主题更明确地推向：
- 新的 `path-shape downside continuation` raw-alpha 宿主；或
- 更事件化的 breakdown / failure / follow-through family。

## 4) 最值得改的唯一一刀是什么？
**如果今天还要回答唯一一刀，答案仍然只能是旧答案：**

> 把 `Rank 33` 从 standalone `NW + reclaim` entry，降级成 shared `false-reclaim veto / failure-verdict note`。

也就是：
- 不让 `NW + confirmed reclaim` 自己直接开仓；
- 只把它用作已有 setup 的坏 reclaim 备注或 veto 提示。

但这次比 4 月 12 日更明确的一点是：
- 这条“唯一一刀”已经越来越不像值得继续保留为 queue-facing 候选；
- 它更像旧 rank 留下的一句审计注释，而不是值得再 draft 新 rank 的主修改轴。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。本轮结论继续是：`keep_park`。**

原因：
1. 原 `park` 审计意义完全成立，不能推翻；
2. 最近新增的 path-shape 证据虽然支持“结构路径有信息”，但它救活的是新的 downside-continuation raw-alpha 宿主，不是 old `Rank 33`；
3. 若现在硬写 `Rank 33b`，大概率会把 old reclaim residual 偷换成新的 `path-shape / downside continuation / failure-followthrough` family；
4. 这会稀释 old `Rank 33 = NW + reclaim standalone 不成立` 的边界，因此不诚实。

## 单轮审查模板回答
### 原 rank 为什么 park？
因为 `NW + confirmed reclaim` 只能略微减少假 reclaim，没能救回收益、覆盖与诚实交易厚度；更强确认又会滑向稀疏美化。

### 它更像 hard park 还是 soft park？
`soft park`，但已比 4 月 12 日更接近 `hard park with consumed residual`。

### 有没有“可救信号”？
有，但只剩 `false reclaim / failure path` 这条很薄 residual；而最近 path-shape 新证据说明，这点信息更像新宿主在吸收它，而不是 old Rank 33 自己可救。

### 最值得改的唯一一刀是什么？
仍是把 standalone `NW + reclaim` 降级成 shared `false-reclaim veto / failure-verdict note`。

### 是否值得形成新的 derived hypothesis？
不值得；本轮不 draft `Rank 33b`。

## Final verdict
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park，但更接近 hard with consumed residual`
- concise note: `4 月 17 日新增的 path-shape downside-continuation 证据继续说明，结构路径主题若还有信息，更像新的 downside continuation / failure-followthrough raw-alpha 宿主，而不是足以再诚实派生 old Rank 33 的 Rank 33b。`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`
- 未改：`docs/TODO.md`

## Git
- 未做 commit。
- 原因：git 工作区存在大量无关脏文件；本轮只做最小必要文档更新，避免混提。
