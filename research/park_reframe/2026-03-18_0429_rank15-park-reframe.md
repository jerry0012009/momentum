# 2026-03-18 04:29 UTC · Rank 15 park reframe review

## Scope
- Source rank: `Rank 15 support/resistance regime-switch confirmation gate`
- Original verdict stays: `park / evidence pool`
- This round only asks: **should Rank 15 derive one narrower reframe hypothesis, without overturning the original park?**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- recent reframe logs:
  - `research/park_reframe/2026-03-18_0229_rank27-park-reframe.md`
  - `research/park_reframe/2026-03-18_0022_rank34-park-reframe.md`
  - `research/park_reframe/2026-03-17_2222_rank35-park-reframe.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_0103_rank15-sr-regime-switch-intake.md`
  - `research/optimization_loop/2026-03-17_0126_rank15-clean-replication-park.md`
  - `research/quant_digests/2026-03-15_0942_support-resistance-zones-averaged-levels.md`

## Why this rank
- It is within `Rank 1~37` and currently parked.
- It has **not** been reviewed by `bot6` in the recent 7-day reframe queue.
- At first glance it looks temptingly salvageable because `retest_hold_reclaim` was only mildly negative (`6bps≈-1.94%`) rather than a total collapse.
- But after re-reading the original evidence together with adjacent support/resistance work, the more honest read is: the idea has already spent its obvious single-axis rescue budget.

## 1) 原 rank 为什么 park？
Rank 15 被 park，不是因为“support/resistance 确认层完全没意义”，而是因为当前这套 `touch_or_cross -> confirm -> retest_hold_reclaim` 的 regime-switch 版本并**没有把确认层做成可升格的交易故事**。

原 clean replication 关键证据：
- `retest_hold_reclaim @ 6bps/side`：`mean_total_return≈-1.94%`
- `positive_asset_ratio=1/3`
- `mean_no_trade_ratio≈81.73%`
- Light Stability Pack 四项都硬 fail：
  - 时间稳定性：`1/3` positive buckets
  - 参数稳定性：`0/5` 邻域为正
  - 跨标的稳定性：`1/3` 资产为正
  - 成本 / 交易数稳定性：`0/4` 成本档位为正（`20bps≈-5.45%`）

更直白地说：
- `confirm / retest` 比裸 `touch_or_cross` 更讲得通，但没把它救成可推广 pocket；
- 它的“少亏”主要伴随 **高 no-trade / 低可用性**，不是足够诚实的稳定存活；
- 所以原 `park` 结论必须保留。

## 2) 它更像 hard park 还是 soft park？
**更像 `hard park`。**

原因不是数字最差，而是它的失败形状已经说明：
- 一旦放宽一点，容易把噪音带回来；
- 一旦收紧一点，又迅速变成高 `no_trade_ratio` 的稀薄 pocket；
- 而且这种张力并不只是 `Rank 15` 自己的问题，旁边的相邻支持/阻力近义重写也已经试过。

尤其是：
- `Rank 12 averaged support/resistance zone + context gate` 已经回答过“把单线改成平均 zone / context”这一刀，结果仍是 hard fail；
- `2026-03-15_0942_support-resistance-zones-averaged-levels.md` 虽给了外部论文启发，但本地 `Rank 12` 已经把这条最自然的单轴旁支诚实试过了。

所以 Rank 15 当前不像“只差删一层 gate 的 soft park”，更像“核心确认故事已经试过几种自然近邻表达，仍没有形成干净 pocket”的 hard park。

## 3) 有没有“可救信号”？
**只有弱信号，没有足够诚实的可救信号。**

能算弱信号的部分：
- `retest_hold_reclaim` 确实比很多直接爆炸的 parked rank 更接近零；
- 说明“确认层”不是完全没边际价值。

但为什么还不够：
- 这个 pocket 只体现为“少亏”，不是跨资产 / 时间 / 参数同时干净；
- `1/3` positive asset + `0/5` parameter neighborhood positive，说明并不存在明显稳定平台；
- 最自然的外部启发——把精确线改成 `zone`——已经在相邻 `Rank 12` 的本地实现里试过，仍然失败。

因此这里更像“方向有点道理，但已经不剩一个没被试过的诚实单轴可切”，而不是“已经看到明确 salvage signal”。

## 4) 最值得改的唯一一刀是什么？
**当前没有足够诚实的唯一一刀。**

表面上最像的一刀有两种：
1. 把单线 `retest_hold` 改成 `averaged zone retest`
2. 进一步放宽 `confirm bars` / `outside stay` 条件

但这两刀都不够诚实：
- 第 1 刀已经被相邻 `Rank 12` 基本覆盖过；
- 第 2 刀更像“为了增加 trade count 而继续放松”，没有新的旁支证据证明这是对 blocker 的真正修复。

换句话说，Rank 15 当前若硬要派生，几乎一定会滑向多轴混改：`zone + context + asymmetric threshold + wider timeout` 之类。这不符合本轮只允许 **1 条唯一主修改轴** 的规则。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

原因：
- 原 rank 的 `park` 仍有明确审计意义；
- 当前没有一个既窄、又没被旁支证据提前消费掉的 single modification axis；
- 继续派生更像在 support/resistance 近义变体之间换壳续命，而不是提出真正新的窄 hypothesis。

## 6) trade on / trade off 结论
本轮**不形成**新的 `Rank 15b`。

更诚实的保留口径是：
- `trade on` 故事并非彻底荒谬；
- `trade off` 的真实问题也不是“确认层不够复杂”，而是它已经在几种最自然的确认重写里都没证明自己能形成稳定 pocket；
- 在出现新的外部证据之前，不应继续把它包装成新的入板候选。

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `hard park`

## Minimal audit note
This round does **not** reopen Rank 15 itself.
It records that Rank 15 currently fails the park-reframe test because its obvious nearby rescue axis (`single-line -> averaged zone/context`) has effectively already been spent by adjacent evidence, while the original rank still lacks any clean cross-asset / parameter-stable pocket.

## Git
- 本轮只做最小必要文档改动；未做 commit。
- 原因：工作区存在大量无关脏文件与未跟踪文件，当前不适合安全地 selective commit。
