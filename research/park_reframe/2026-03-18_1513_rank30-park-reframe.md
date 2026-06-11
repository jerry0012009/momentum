# 2026-03-18 15:13 UTC · Rank 30 park reframe review

## Scope
- Source rank: `Rank 30 trendln paired-channel breach / corridor breakout gate`
- Original verdict stays: `park / evidence pool`
- This round only asks: **should Rank 30 derive one narrower reframe hypothesis, without overturning the original park?**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- recent reframe logs:
  - `research/park_reframe/2026-03-18_1314_rank26-park-reframe.md`
  - `research/park_reframe/2026-03-18_1036_rank18-park-reframe.md`
  - `research/park_reframe/2026-03-18_0836_rank31-park-reframe.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_1422_rank30-clean-replication-park.md`
  - `reports/site/factors/scout_rank30_trendln_channel_15m/report.html`
  - `research/quant_digests/2026-03-18_1500_event-anchored-vwap-hold-gate.md`

## Why this rank
- It is within `Rank 1~37` and currently parked.
- It has **not** been reviewed by `bot6` in the recent 7-day reframe queue.
- It is tempting for a narrow reframe because the original line was **bad, but not structurally incoherent**: `breach_plus_reclaim_hold` did improve on raw breach a bit, yet still died on a very specific blocker — fake breaks stayed extremely high.
- A fresh digest now offers a naturally adjacent, still narrow rescue axis: instead of asking for one more binary close outside the channel, ask whether price can hold the **breach-event anchored VWAP** on the strong side.

## 1) 原 rank 为什么 park？
Rank 30 被 park，不是因为“paired-channel breakout 完全没信息”，而是因为它的最小 clean replication 已经清楚回答：**通道突破后的确认方式太脆，假突破率高到吞掉了所有改善。**

原 clean replication 关键证据：
- `raw_corridor_breach @ 6bps/side`：`mean_total_return≈-10.73%`、`positive_asset_ratio=0/3`、`mean_trades≈93.0`、`mean_false_break_ratio≈86.11%`
- `breach_plus_reclaim_hold @ 6bps/side`：`mean_total_return≈-7.33%`、`positive_asset_ratio=0/3`、`mean_trades≈57.3`、`mean_false_break_ratio≈82.39%`
- `mean_width_cv≈0.137`，说明问题不主要是通道宽度稳定性彻底崩掉，而更像 **确认层没把真假突破分开**

更直白地说：
- 加一层 `reclaim_hold` 确实比裸 breach 少亏一点；
- 但改善远远不够，三腿仍全负；
- 核心 blocker 不是“完全没突破”，而是“突破后库存成本/接受度没被诚实确认”。

所以原 `park` verdict 必须保留。

## 2) 它更像 hard park 还是 soft park？
**更像 `soft park`。**

原因：
- 它不是那种一上来就全线爆炸、没有任何可分解结构的 rank；
- `breach_plus_reclaim_hold` 相比 `raw_corridor_breach` 至少给出了一点方向正确的信号：亏损更小、假突破率略降、交易数也还没稀到不可用；
- 这说明问题更像出在“确认定义太粗”，不是“corridor breach 这个方向完全不行”。

但它还没到可以直接重开原 rank 的程度，因为：
- 现有证据仍然是 `positive_asset_ratio=0/3`；
- 原线当前的二元 `reclaim_hold` 写法已经被事实证明不够诚实。

## 3) 有没有“可救信号”？
**有，而且比很多已 park rank 更清楚。**

当前可救信号主要有三点：
1. `reclaim_hold` 至少沿着对的方向走了一小步：相对 raw breach 少亏、假突破率略降；
2. `mean_width_cv≈0.137` 不算灾难，说明并不是通道拟合本身全坏；
3. 最新 quant digest 给出一条很贴 Rank 30 原故事的窄轴：**用 breach 事件锚定的 AVWAP hold/reclaim，替代“再多收一根在通道外”这类二元确认。**

翻成人话：
- 原 Rank 30 的问题更像“你知道要确认，但确认得太笨”；
- event-anchored VWAP 刚好是在问：**突破以后，新库存平均成本线到底有没有真的站住。**

这条轴既不像完全推翻原 rank，也不像多轴大改。

## 4) 最值得改的唯一一刀是什么？
**唯一最值得改的一刀：把 `breach_plus_reclaim_hold` 的二元“下一根继续收在通道外”确认，替换成 `breach-event anchored VWAP hold/reclaim` 确认。**

也就是：
- 保留原来的 `paired-channel corridor breach` 作为方向事件；
- 不再用“再来一根 close 还在通道外”当 continuation 确认；
- 改成把 `breach confirm bar` 冻结成 anchor，随后只在价格仍守在 `A_VWAP(anchor)` 强侧，或最近 `3` 根里至少 `2` 根守在强侧时，才允许进场；
- 可选再加一层很窄的 proximity 读法：`|close - A_VWAP| < 0.5 * ATR14`，只当 retest 够近的附加条件，而不是第二主轴。

为什么这是一刀而不是多轴：
- entry 事件没改；
- universe / timeframe / hold / execution 没改；
- 只改了 **breakout confirmation 的唯一表达方式**。

## 5) 是否值得形成新的 derived hypothesis？
**值得。结论：`derived_hypothesis_drafted`。**

理由：
- 原 `park` 仍保留完整审计意义；
- 原 rank 失败的主 blocker 很集中：`false_break_ratio` 太高；
- 最新 digest 提供了一条与该 blocker 高度同构、且足够窄的确认层改写；
- 这不是“再试一个参数”，而是把确认语义从“再多站一根”改成“库存成本线是否真的被守住”。

## 6) trade on / trade off 结论
### Proposed derived hypothesis
- `proposed_rank`: `Rank 30b`
- `source_rank`: `Rank 30`
- `single modification axis`: `replace binary breach_plus_reclaim_hold confirmation with breach-event anchored VWAP hold/reclaim`
- `trade on`: `保留 paired-channel corridor breach 为方向事件；只有当 breach confirm bar 作为固定 anchor 后，价格仍收在该 event-anchored VWAP 强侧（或最近 3 根里至少 2 根守在强侧；short 镜像），才按 next-bar open 入场`
- `trade off`: `放弃“只看再多一根是否仍在通道外”的更机械确认，换取更贴近 24/7 crypto 的库存成本/接受度读法；代价是 AVWAP anchor 若定义不严，容易重新滑向事后美化，因此必须把 anchor 类别提前冻结`
- `why now`: `原 clean replication 已显示 breach_plus_reclaim_hold 比 raw breach 少亏且假突破率略降，说明问题更像确认层太粗；最新 event-anchored VWAP digest 又正好提供了更贴 Rank 30 原故事的单轴改写`
- `suggested initial state`: `source intake / clean replication next`

## Final verdict for this round
- `verdict`: `derived_hypothesis_drafted`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park`

## Minimal audit note
This round does **not** reopen Rank 30 itself.
It keeps the original `park` intact, while drafting only one narrow follow-up idea: **`Rank 30b = keep corridor breach, but replace binary reclaim_hold with breach-event anchored VWAP hold/reclaim confirmation`.**

## Git
- 本轮只做最小必要文档改动；未做 commit。
- 原因：工作区存在大量无关脏文件与未跟踪文件，当前不适合安全地 selective commit。
