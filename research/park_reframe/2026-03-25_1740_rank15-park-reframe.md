# 2026-03-25 17:40 UTC · Rank 15 park reframe review

## Scope
- Source rank: `Rank 15 / support-resistance regime-switch confirmation gate`
- Original authoritative verdict stays: `park / evidence pool`
- This round only asks: **在不推翻原 park 的前提下，Rank 15 是否值得派生出 1 条新的窄 reframe hypothesis**

## 7-day rule note
- `Rank 15` 在 `2026-03-22 18:39 UTC` 已复盘过一次，按规则本应优先换别的。
- 但本轮轮转已基本把 `50+`、`80~110` 与低号近期更活跃条目扫过一遍；当前低号 parked 池里，`Rank 15` 仍是一个“看起来像还能再救、但未必诚实”的代表位。
- 本轮不是重跑，只是借着 **3/25 新增的 raw-alpha / microstructure / leader-continuation 证据继续变多** 这个背景，再确认一次：`Rank 15` 这种老式 S/R confirm 线，究竟还有没有必要再单独派生。

## Read set
- required:
  - `docs/TODO.md`
  - `docs/PARK_REFRAME_QUEUE.md`
  - `docs/RECENT_PAPER_SEEDS.md`
  - `research/quant_digests/INDEX.md`
  - `research/park_reframe/INDEX.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_0103_rank15-sr-regime-switch-intake.md`
  - `research/optimization_loop/2026-03-17_0126_rank15-clean-replication-park.md`
  - `research/park_reframe/2026-03-22_1839_rank15-park-reframe.md`

---

## 1) 原 rank 为什么 park？
原 Rank 15 想回答的是：**support / resistance 被触碰后，若不立刻追，而是等 `confirm1/2of3 outside` 或 `retest_hold_reclaim`，能不能把“越线”变成更诚实的状态切换 setup。**

原始 park 理由仍然成立：
- 最不差主变体还是 `retest_hold_reclaim @ 6bps/side`，但本质只是少亏：
  - `mean_total_return ≈ -1.94%`
  - `positive_asset_ratio = 1/3`
  - `mean_no_trade_ratio ≈ 81.73%`
- 四项 Light Stability Pack 继续一起 fail：
  - 时间稳定性：`1/3 positive buckets`
  - 参数稳定性：`0/5 positive neighbors`
  - 跨标的稳定性：`1/3 assets positive`
  - 成本稳定性：`0/4 cost levels positive`

一句话：**“多等一层确认”并没有把这条 S/R regime-switch 线救成可入板候选。**

## 2) 它更像 hard park 还是 soft park？
**soft park，但偏硬。**

原因不是它完全没信号，而是：
- `retest_hold_reclaim` 相对 baseline 确实更少亏，说明“确认层”方向不是纯错；
- 但这个残余信息太薄，且主要表现为 **少做 + 少亏**，不是稳定存活；
- 一旦再往前多走一步，就很容易滑成“把确认层降级成泛用 gate/overlay”的老路，而这条路现在已有很多更窄、更贴 desk 的提案在 queue 里。

所以它不是彻底死透的 hard park，但也已经很接近“自然救法基本被用完”的状态。

## 3) 现有证据里是否存在“可救信号”？
**有，但很弱，而且更像被新 family 吸收，而不是值得再派生 Rank 15b。**

本轮再看 3/25 新增 digest 后，最明显的变化不是 Rank 15 自身变得更可救，而是 desk 上已经越来越清楚：
- 真值得新开预算的，往往是 **完整 raw alpha family**（比如 raw mean reversion / microstructure / leader continuation / cross-sectional interaction）；
- 老的 `S/R confirm` 主题若还剩一点信息，也更像给现有 setup 当局部质量特征，而不是自己再单独立一个 rank。

也就是说，Rank 15 的残余价值并未完全为零，但它更像：
- “结构确认层里的一丝局部信息”；
- 而不是“还缺一个没试过的单轴写法”。

## 4) 最值得改的唯一一刀是什么？
**本轮仍然没有足够诚实的唯一一刀。**

表面上最像的两刀仍然是：
1. 把 `retest_hold_reclaim` 继续改成更宽的 zone / context 表达；
2. 把它从 standalone confirmation 改写成 shared veto / overlay。

但现在这两刀都不值得立新号：
- 第一刀已经太接近相邻的 zone / persistence / context 路线，辨识度不够；
- 第二刀会把 Rank 15 稀释成一个泛化 overlay，和 `12b / 9b / 21b / 25b` 这一堆“降级成 gate/overlay”的提案高度重叠。

所以本轮最诚实的答案依旧是：**没有一条还没被消费、又只改 1 轴的自然切口。**

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

### trade on / trade off（为何不 draft）
如果现在硬 draft，一个看似最自然的 trade on 会是：
- trade on：保留 S/R 主题，但把它降级成已有 continuation / retest setups 的质量过滤层；
- trade off：它将失去独立主题，且极大概率只是靠砍单美化，最后变成与现有 queue 提案重复。

这正是本轮不该 draft 的原因：
- **trade on 不够独特**；
- **trade off 太明显**；
- 审计增量小于重复风险。

---

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park，但偏硬`

## Minimal audit note
本轮不重开 `Rank 15`，也不推翻原 park。
只确认一件事：**截至 2026-03-25，Rank 15 仍只有“确认层少亏”这点残余信息；这点信息更像会被更新的 raw-alpha / gate family 吸收，而不是值得单独再派生一个 `Rank 15b`。**

## Git
- 本轮只做最小必要文档改动；不做 commit。
- 原因：工作区存在大量与本轮无关的脏文件，且 `docs/PARK_REFRAME_QUEUE.md` 已被其他流程改动，当前不适合安全 selective commit。
