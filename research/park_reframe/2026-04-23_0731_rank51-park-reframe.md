# 2026-04-23 07:31 UTC · Rank 51 park reframe

## Selected rank
- `Rank 51`
- selection note: 继续按 `50+` 优先的低频轮转处理 1 条 parked rank。`Rank 51` 上次 park-reframe 是 `2026-04-13 17:30 UTC`，已超过 `7` 天窗口；同时 4 月 19~23 又新增了更贴近 VWAP / anchor 的 raw-alpha 旁证，足够再判断一次：这些新证据是在救旧 `session VWAP reclaim + breadth gate`，还是继续把主题外流到新的 mean-reversion / anchor 宿主。

## Read set
必读：
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`

补充：
- `research/park_reframe/2026-04-13_1730_rank51-park-reframe.md`
- `research/optimization_loop/2026-03-18_0922_rank51-clean-replication-park.md`
- `research/quant_digests/2026-04-19_0715_vwap-lowerband-persistent-placement-alpha.md`
- `research/quant_digests/2026-04-23_0419_anchored-vwap-regimeextreme-reversion-alpha.md`

## 1) 原 rank 为什么 park？
原 `Rank 51 / session VWAP reclaim + breadth gate` 的 `park` 理由没有变化：

- 它想把 `session VWAP reclaim + breadth` 写成 continuation / retest 家族可共享的防守确认层；
- 但最小 clean replication 证明，这条线虽然能明显减少 false retest，却仍主要是在“少做错单”，不是 desk 口径下可部署的赚钱 gate。

冻结审计结果仍然清楚（`BTC/ETH/SOL 120d 15m`, `6bps/side`, `next-bar open`, `no-overlap`）：
- `touch_only`: `mean_total_return≈-79.13%`，`false_retest_4bars_rate≈75.57%`
- `touch_plus_reclaim`: `mean_total_return≈-49.69%`，`false_retest_4bars_rate≈47.70%`
- `touch_reclaim_plus_breadth`: `mean_total_return≈-43.79%`，`positive_asset_ratio=0/3`，`trade_count_retention≈39.10%`，`false_retest_4bars_rate≈39.20%`
- time pocket 三段仍全负。

所以 old `Rank 51` 被 park 的核心不是“breadth 再调一下就够了”，而是：

> **把 session VWAP reclaim + breadth 写成跨宿主 shared gate，这层主语已经被审计否掉。**

## 2) 它更像 hard park 还是 soft park？
**本轮判断：仍是 `soft park`，但比 2026-04-13 那轮更接近 `hard park with consumed residual`。**

为什么仍保留 `soft`：
- `VWAP reclaim / acceptance` 的方向感并非纯噪声；
- clean replication 的确证明它能压低假回踩率。

为什么更接近 `hard`：
- 改善仍主要来自砍交易数，而不是把 shared gate 变成正期望；
- 新证据越来越一致地把 VWAP / anchor 主题推向新的 raw-alpha 宿主，而不是旧 `Rank 51` 本体还能再诚实切出一刀。

一句话：
> 主题还活着，但旧 `Rank 51` 这具 shared-gate 宿主越来越不像值得继续派生 `Rank 51b` 的地方。

## 3) 有没有“可救信号”？
**有，但仍然只是主题级可救信号，不是旧 rank 级可救信号。**

### A. 4 月 19 日 lower-VWAP persistent placement 旁证
`2026-04-19_0715_vwap-lowerband-persistent-placement-alpha.md` 说明：
- `VWAP 下沿持续压住 -> reclaim` 这类 underpricing / acceptance 语义仍然有信息；
- 但它更像单资产 long-side mean-reversion 原型；
- broad `15m` 迁移仍偏负，说明真正值得继续追的是 **更强事件过滤 / 更好 execution / 更准确宿主**，不是把 old `Rank 51` 的 shared defense gate 再细修一层。

这条证据强化的是：
- VWAP 可以当 raw alpha 的公平价锚；
- 不是继续当 old `Rank 51` 的 shared confirmation 小补丁。

### B. 4 月 23 日 anchored VWAP regime-extreme 旁证
`2026-04-23_0419_anchored-vwap-regimeextreme-reversion-alpha.md` 把方向说得更清楚：
- 真正更有活性的写法是 `recent swing anchor -> AVWAP -> deviation extreme -> reclaim/timeout exit`；
- 这已经是 **anchor-led raw alpha host**，不是 session VWAP reclaim + breadth gate；
- 它把主语从“给既有 setup 做防守确认”改成了“AVWAP 偏离本身就是交易起点”。

这等于进一步确认：
- VWAP / anchor 主题若还有 residual value，更像新的 anchored-VWAP mean-reversion / event-anchor 宿主；
- 而不是足以把 old `Rank 51` 再诚实派生成 `Rank 51b`。

## 4) 最值得改的唯一一刀是什么？
**如果只回答唯一主修改轴，本轮最值得改的一刀仍然是：把 fixed session VWAP reclaim + breadth gate 改写成 anchor-led VWAP host。**

但这刀为什么仍然不诚实地属于 `Rank 51b`：
1. 它把主语从 `shared gate` 改成了 `raw alpha host`；
2. 它把锚点从固定 session reset 外推到 swing / event / AVWAP 一类更通用的因果 anchor；
3. 它已经不是 old `Rank 51` 内部的窄 reframe，而是在换宿主、换角色、换研究问题。

所以对旧 `Rank 51` 来说，本轮**没有出现新的唯一主修改轴**；唯一“最值得改的一刀”其实已经越界到新的 family 里了。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

原因：
1. 原 `park` verdict 没有被推翻；
2. 新证据没有把 old `Rank 51` 拉回 queue-facing shared gate；
3. 4 月 19~23 的证据都在继续把 VWAP / anchor 主题外流到新的 mean-reversion / anchored-VWAP raw-alpha 宿主；
4. 若现在硬写 `Rank 51b`，本质会是借新 AVWAP / raw-alpha family 给旧 session-gate 续命，模糊原审计边界。

## 6) 单轮模板回答
### 原 rank 为什么 park？
因为 `session VWAP reclaim + breadth` 作为跨宿主 shared confirmation gate，只证明了“能少犯一些错”，没有证明能形成成本后正期望；time pocket 也没有留下干净 pocket。

### 它更像 hard park 还是 soft park？
`soft park`，但比 2026-04-13 那轮更接近 `hard park with consumed residual`。

### 有没有“可救信号”？
有，但只是主题级：近期新证据继续证明 VWAP / anchor 仍有信息，不过它们更像新的 lower-VWAP / anchored-VWAP raw-alpha 宿主，而不是 old `Rank 51` 本体可救。

### 最值得改的唯一一刀是什么？
概念上仍是“把 fixed session VWAP reclaim + breadth gate 改写成 anchor-led VWAP host”，但这已经不属于 old `Rank 51` 的诚实窄 reframe。

### 是否值得形成新的 derived hypothesis？
不值得；本轮继续 `keep_park`。

## Final verdict
- `verdict`: `keep_park`
- `original_verdict_kept`: `park`
- `park_type_read`: `soft park，但比 2026-04-13 那轮更接近 hard park with consumed residual`
- short note: `4 月 19~23 的 lower-VWAP reclaim 与 anchored-VWAP regime-extreme 新证据继续说明：VWAP / anchor 主题还活，但真正可救的是新的 underpricing / anchored-VWAP raw-alpha 宿主，而不是旧 Rank 51 的 session VWAP reclaim + breadth shared gate；当前不诚实 draft Rank 51b。`

## Minimal audit note
本轮没有推翻原 `park`，也没有改写 `TODO`。只是进一步确认：
- VWAP / anchor 主题值得继续研究；
- 但应作为新的 raw-alpha / anchor-host family 去追，而不是继续在 old `Rank 51` 名下硬切 `Rank 51b`。

## Git
- 未做 commit。
- 原因：`git status --short` 显示工作区存在大量与本轮无关的既有脏文件 / 未跟踪文件；本轮只做最小必要文档更新与邮件交付，避免混提。
