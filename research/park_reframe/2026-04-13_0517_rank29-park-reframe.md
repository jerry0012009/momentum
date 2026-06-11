# 2026-04-13 05:17 UTC · Rank 29 park reframe review

## 本轮对象
- `Rank 29 / trendline breakout navigator / multi-swing structural breakout state machine`
- 原始结论保留：`park / archived`
- 本轮输出：`keep_park`

## 为什么这轮看 Rank 29
- 本轮按 `Rank 1~37` 已 `park` 条目低频复盘。
- `Rank 29` 最近 7 天没有 bot6 park-reframe 复盘记录。
- 同时，4 月初出现了对它**直接改变宿主可信度**的新证据：
  - `docs/RANK29_POSTMORTEM_2026-04.md`
  - `docs/MANUAL_NARROW_PAPER_LANES.md`（已明确写成 `Rank 29 = P0 archived`）
- 另外，`2026-04-12_2304_smc-sweep-reclaim-alpha.md` 也提供了一个与“结构扫流动性后 reclaim continuation”有关的新旁支，足以回答：旧 `Rank 29` 还有没有诚实切出窄 reframe 的空间。

## Read set
- `docs/BOT6_PARK_REFRAME_BRIEF.md`
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- recent park-reframe references:
  - `research/park_reframe/2026-04-13_0221_rank37-park-reframe.md`
  - `research/park_reframe/2026-04-12_2350_rank4-park-reframe.md`
- source / prior rank evidence:
  - `research/optimization_loop/2026-03-17_0921_rank29-clean-replication.md`
  - `docs/RANK29_POSTMORTEM_2026-04.md`
  - `docs/RANK29_SHADOWS.md`
  - `docs/MANUAL_NARROW_PAPER_LANES.md`
- new side evidence:
  - `research/quant_digests/2026-04-12_2304_smc-sweep-reclaim-alpha.md`

## 1) 原 rank 为什么 park？
原 `Rank 29` 现在不是普通意义上的“效果变差后 park”，而是因为**旧 baseline 的信号诚实性被推翻**。

先前 clean replication（`2026-03-17_0921_rank29-clean-replication.md`）一度给出很强 headline：
- `breakout_align_ge2`
- `6bps/side` 下 `mean_total_return≈+75.23%`
- `positive_asset_ratio = 3/3`
- `mean_false_break_ratio≈7.56%`

但 4 月初的 postmortem 进一步确认：
- `pivot` / `trendline` 状态会被后续确认信息回填到更早 bars；
- 这会改写历史上的 `line_value / line_slope / active_pivot_origin / composite trend`；
- 结果是旧口径里很多“当时可交易”的信号，其实是 hindsight-only。

关键 strict-causal 结论：
- 主版本 `breakout_align_ge2` 在 `causal_replay` 下：**0 笔交易**；
- 放宽到 `breakout_align_ge1`：`mean_total_return≈-8.16%`，`positive_asset_ratio=0%`；
- 审计里给出的污染比例是：旧口径 `449` 笔，strict-causal 真信号 `0` 笔，**误导比例 100%**。

所以原 `park` 的审计意义非常明确：
> 被否掉的不是“结构 / breakout / reclaim 主题整体死亡”，而是旧 `Rank 29` 这套依赖多 swing trendline 回填的宿主不再诚实可交易。

## 2) 它更像 hard park 还是 soft park？
**本轮判断：更像 `hard park`。**

原因不是主题没信息，而是旧 rank 的主语已经塌了：
1. blocker 不是参数不对、过滤太粗、trade density 太低；
2. blocker 是 baseline honesty 本身失效；
3. 一旦切到 strict-causal，旧主版本直接从“强阳性”塌成“0 笔可交易信号”；
4. 这意味着旧壳不是再补一层 gate / overlay 就能救。

因此这里的 `hard`，是针对**旧 Rank 29 宿主**，不是针对所有结构事件 alpha。

## 3) 有没有“可救信号”？
**有，但只剩主题级可救信号，不再是旧 rank 级可救信号。**

最近最相关的旁支不是“再找一种更聪明的 trendline 回填办法”，而是把结构事件改写成**当根就能冻结的、严格 causal 的事件锚**。例如：
- `2026-04-12_2304_smc-sweep-reclaim-alpha.md` 指向的是：
  - 先发生 `liquidity sweep`
  - 再看 `discount/premium reclaim`
  - 配合 `OB/FVG` 锚点
  - 做 `15m` 的 reclaim continuation

它说明：
> 结构类 edge 可能仍然存在，但更诚实的宿主更像“单事件 sweep→reclaim continuation”，而不是“多 swing 回填 trendline breakout state machine”。

这与旧 `Rank 29` 的差别已经很大：
- 旧 rank 的核心是多 swing trendline / composite trend 状态机；
- 新旁支的核心是单事件、冻结锚、strict-causal reclaim continuation。

所以“可救信号”存在，但它救的是**新的 event-driven structural raw-alpha family**，不是旧 `Rank 29` 本体。

## 4) 最值得改的唯一一刀是什么？
如果今天一定要回答“唯一最值得改的一刀”，最诚实的表述只能是：

> **放弃多-swing 回填 trendline breakout 宿主，改写成 strictly causal 的单事件结构锚（例如 liquidity-sweep / reclaim）驱动。**

但关键判断也正是在这里：
- 这已经不是旧 `Rank 29` 的窄 reframe；
- 它不只是修一层确认条件，而是把宿主从 `backfilled trendline state machine` 改成 `strict-causal event anchor`；
- 因此更像一个新的 raw-alpha family intake，而不是诚实的 `Rank 29b`。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。本轮继续 `keep_park`。**

原因：
1. 原 `park / archived` verdict 没有被推翻；
2. 旧 rank 的主 blocker 是 honesty failure，不是“只差一个 gate”；
3. 若硬写 `Rank 29b`，会把“新宿主另起炉灶”误包装成“旧 rank 的小修小补”；
4. 当前最诚实的做法，是保留 `Rank 29` 作为 future-leak / hindsight contamination 的审计反例，而不是继续给它维持 queue-facing reframe 身份。

## 单轮审查模板回答
### 原 rank 为什么 park？
因为 strict-causal 审计确认旧口径存在 pivot / trendline 回填造成的 hindsight contamination；主版本在 causal replay 下直接变成 0 笔交易，放宽版也整体转负，因此旧宿主不再诚实可交易。

### 它更像 hard park 还是 soft park？
`hard park`（针对旧 Rank 29 宿主）。

### 有没有“可救信号”？
有。结构事件主题本身仍有信息，但更像 `liquidity-sweep × reclaim continuation` 一类严格 causal 的新宿主，而不是旧多-swing trendline 壳。

### 最值得改的唯一一刀是什么？
把“回填 trendline state machine”彻底换成“strict-causal 单事件结构锚”。

### 是否值得形成新的 derived hypothesis？
不值得。本轮继续 `keep_park`。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `hard park；Rank 29 的核心 blocker 已从“效果不稳”升级为“旧 baseline honesty 失效”：strict-causal 审计把原多-swing trendline breakout 宿主直接打回 archived。近期可救信号只存在于更严格 causal 的 sweep/reclaim 事件宿主里，已属于新的 structural raw-alpha family，而不是诚实的 Rank 29b。`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`
- 未改：`docs/TODO.md`

## Commit
- 本轮不做 commit。
- 原因：git 工作区存在大量与本轮无关的共享脏文件 / 未跟踪文件；只做最小必要文档改动，避免混提。
