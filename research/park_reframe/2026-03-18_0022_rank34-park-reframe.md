# 2026-03-18 00:22 UTC · Rank 34 park reframe review

## Scope
- Source rank: `Rank 34 chip-distribution trapped-holder reclaim / winner-ratio gate`
- Original verdict stays: `park / evidence pool`
- This round only asks: **should Rank 34 derive one narrower reframe hypothesis, without overturning the original park?**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- recent reframe logs:
  - `research/park_reframe/2026-03-17_2222_rank35-park-reframe.md`
  - `research/park_reframe/2026-03-17_2022_rank32-park-reframe.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_1740_rank34-authoritative-writeback.md`
  - `reports/site/factors/scout_rank34_chip_distribution_15m/report.html`
  - `reports/artifacts/scout_rank34_chip_distribution_15m/assumption_sensitivity_summary.csv`

## Why this rank
- It is within `Rank 1~37` and currently parked.
- It has not been reviewed by `bot6` in the recent 7-day reframe queue.
- It is not a total “everything is bad” collapse: under the `conservative` anchor, `chip_cost_reclaim` did show a real local pocket (`6bps≈+18.14%`, `positive_asset_ratio=100%`, `mean_trades≈101`).
- But that pocket is sitting directly on the line’s biggest honesty blocker — **anchor sensitivity**. That makes Rank 34 a good test of whether there is a genuinely narrow salvage axis, or whether the right answer is to keep it parked.

## 1) 原 rank 为什么 park？
Rank 34 被 park，不是因为 `chip_cost_reclaim` 在所有定义下都失败，而是因为它的结果**过度依赖 synthetic shares / turnover anchor 假设**。

关键证据：
- `conservative / chip_cost_reclaim @ 6bps`：`mean_total_return≈+18.14%`、`positive_asset_ratio=100%`、`mean_trades≈101.0`
- `neutral / chip_cost_reclaim @ 6bps`：`mean_total_return≈+13.72%`，但 `positive_asset_ratio` 已掉到 `33.33%`
- `aggressive / chip_cost_reclaim @ 6bps`：`mean_total_return≈-18.62%`、`positive_asset_ratio=33.33%`
- 同一主变体的 best-to-worst return gap 约 `36.76pp`

更直白地说：
- 一旦把 shares 假设收紧，这条线的 edge 就明显变形，甚至翻负；
- 说明当前“筹码成本带 reclaim”更像是**假设托出来的 pocket**，还不是足够稳的 deployable pocket。

所以原 `park` verdict 需要保留，不能因为看到 `conservative` 一格漂亮数字就翻案。

## 2) 它更像 hard park 还是 soft park？
**更像 `hard park`，不是 soft park。**

原因：
- 这里的 blocker 不是一个可以轻松删掉的附加过滤器；
- 真正的问题落在这条线最核心的实现前提：`chip` 成本带本身如何由 volume / synthetic shares 递推；
- 如果主 pocket 只在 `conservative` 假设下存活，而同一逻辑在 `neutral / aggressive` 下迅速塌陷，那就不是“规则包装过严”，而是**核心估计层不够稳**。

因此它更像“核心假设未过诚实门槛”的 hard park，而不是“只差删一层 gate 就能重开”的 soft park。

## 3) 有没有“可救信号”？
**有局部信号，但还不构成可救信号。**

存在的局部正 pocket：
- `conservative / chip_cost_reclaim @ 6bps` 确实跨资产为正；
- `conservative / chip_cost_reclaim_plus_winner_ratio @ 15bps` 甚至仍勉强为正（`≈+0.53%`）。

但这些信号为什么还不够“可救”：
- pocket 完全依赖最宽松的 anchor；
- `neutral` 已经掉成单腿为正，`aggressive` 直接翻负；
- 这说明救回来的不是一个更干净的交易故事，而更像是某个特定 inventory-decay 假设。

所以这里最多只能说“有局部亮点”，不能诚实地说“已有明确 salvage signal”。

## 4) 最值得改的唯一一刀是什么？
**没有足够诚实的唯一一刀。**

这正是 Rank 34 与 `Rank 32 / Rank 35` 的差别：
- `Rank 32` 可以清楚说唯一一刀是删掉 `reclaim`；
- `Rank 35` 可以清楚说唯一一刀是删掉 `VWAP reclaim`；
- 但 `Rank 34` 若想“救”，通常都会滑向多轴手术：
  - 改 shares half-life / anchor
  - 改 turnover decay
  - 改赢家比率阈值
  - 改适用品种或只留 SOL

这些都不是本轮允许的窄单轴 reframe。

若硬要写一刀，最像的一刀会是“冻结 conservative anchor 作为唯一实现口径”；但这本质上是在**选择最有利假设**，不是在回答原 rank 的核心诚实问题，因此不够格作为新 derived hypothesis。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

原因：
- 原 rank 的 blocker 仍是核心估计层本身，而不是一层可切除的附加 gate；
- 当前没有一个足够窄、足够诚实、且不依赖“挑最优 anchor”的 single modification axis；
- 若现在强行派生，很容易把 `bot6` 变成“替假设敏感策略找最顺手口径”的续命器，这正是 brief 明确不允许的事。

## 6) trade on / trade off 结论
本轮**不形成**新的 `Rank 34b`。

保留原解释更诚实：
- `trade on` 故事本身不是完全没吸引力；
- `trade off` 不是“确认层太严”，而是“筹码带估计对 anchor 假设过敏”；
- 在这个核心问题没被新的外部证据改变之前，不应把它包装成新的 reframe 候选。

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `hard park`

## Minimal audit note
This round does **not** reopen Rank 34 itself.
It records that Rank 34 currently fails the park-reframe test because its apparent edge is too dependent on the exact synthetic-shares anchor, and there is **no honest single-axis cut** worth drafting as a new derived hypothesis.
