# 2026-03-30 04:19 UTC · Rank 20 park reframe review

## Scope
- Source rank: `Rank 20 / price-volume divergence breakout filter`
- Allowed output set: `keep_park | soft_reframe_candidate | derived_hypothesis_drafted`
- This round keeps the original `park` verdict auditable; it only asks whether Rank 20 still deserves a **new** narrow reframe hypothesis.

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_0326_rank20-price-volume-divergence-park.md`
  - `research/park_reframe/2026-03-19_1539_rank20-park-reframe.md`
  - `research/quant_digests/2026-03-19_0706_volume-price-interaction-admission-layer.md`
  - `research/optimization_loop/2026-03-19_0937_rank84-clean-replication-park.md`

## Why this rank this round
- It is a parked rank within `Rank 1~37`.
- Its last bot6 review in queue was `2026-03-23 00:45 UTC`, so it is no longer inside the recent 7-day skip window.
- Rank 20 is a good audit check because its previously drafted residual (`Rank 20b`: demote divergence filter into a shared volume-price interaction admission layer) has already been indirectly consumed by the later `Rank 84` clean replication and hard-failed.

## 1) 原 Rank 为什么 park？
原 Rank 20 被 park，不是因为“量价主题完全没信息”，而是因为它当时被写成了一条 **standalone breakout filter**，而且 clean replication 给出的答案很直接：

- baseline `baseline_mtf_momentum @ 6bps/side`
  - `mean_total_return ≈ -38.69%`
  - `positive_asset_ratio = 0/3`
- main variant `pvd_break24_delta0.5_warn3 @ 6bps/side`
  - `mean_total_return ≈ -39.22%`
  - `positive_asset_ratio = 0/3`

Light Stability Pack 也没有留下可交易残余：
- 时间稳定性：`0/3` 正 bucket
- 参数邻域：最不差也仍明显为负
- 跨资产：`BTC / ETH / SOL = 0/3` 为正
- 成本：从 `6 -> 10 -> 15 -> 20 bps` 持续恶化

翻成人话：
- 原 Rank 20 不是“还差一点”；
- 而是把 `divergence warning` 直接写成 breakout 家族主过滤器后，**整条写法一起不成立**；
- 所以原 `park` verdict 必须保留。

## 2) 它更像 hard park 还是 soft park？
**仍是 `soft park`，但比 2026-03-23 更偏硬。**

原因：
- 原始失败点一直比较集中，确实像“角色放错层级”而不只是主题彻底归零；
- 但那条最自然的窄救法——把 standalone divergence filter 降级成 `volume-price interaction` shared admission layer——已经不再只是纸面提案，而是后来被 `Rank 84` 这条 clean replication 基本消费过了；
- 既然最自然的一刀已经被试过，而且没有把结果推过 admission 线，那么这条线的 soft residual 还在，但已经明显更硬。

## 3) 有没有“可救信号”？
**有，但只剩旧的、且已被消费过的可救信号。**

可救信号仍然是：
- 量价关系更像 `admission / sizing / quality layer`，而不是 standalone breakout filter；
- `2026-03-19` 的 digest 也确实给过这个方向的理论支持。

但关键变化在于：
- 这条信号已经由 `Rank 84 / volume-price interaction admission layer` 做过最小 clean replication；
- 而 `Rank 84` 的 hard verdict 仍然是 `park / evidence_pool`；
- 它只留下了很轻微的 relative improvement（例如 `-1.97% -> -1.40% / -1.35%` 级别），同时伴随 trade shrink；没有形成足够诚实、足够独立的新 queue-facing 假设。

所以现在不能再把这个“可救信号”当成新证据，它更像 **已经验证过但未过线的旧残余**。

## 4) 最值得改的唯一一刀是什么？
如果只讨论“历史上最值得改的一刀”，答案仍然是：

> **把 Rank 20 从 standalone `price-volume divergence breakout filter`，降级成 `volume-price interaction` shared admission layer。**

但这不是本轮要新增的动作，因为：
- 这刀已经在 2026-03-19 被 draft 成 `Rank 20b`；
- 后续又被 `Rank 84` 的 clean replication 实际消费；
- 当前没有更新、更窄、且未被审计过的唯一新轴可以诚实提出。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。最终结论：`keep_park`。**

理由很简单：
1. 原 Rank 20 的 `park` 结论必须保留；
2. 它最自然的 residual axis 早已被写成 `Rank 20b`；
3. 该 residual 又被后续 `Rank 84` clean replication 基本消费并再次 `park`；
4. 因此当前再写 `Rank 20c`，大概率只是在旧残余上换措辞，而不是诚实新增一个尚未被审计过的 queue-facing 对象。

## 6) 当前最诚实的 desk 读法
- 原 Rank 20：保留 `park`
- Park 类型：`soft park`，但已经明显向硬边靠拢
- 唯一自然残余：仍只是既有 `Rank 20b` 那条“volume-price interaction shared admission layer”读法
- 但那条残余已经被 `Rank 84` clean replication 基本消费
- 所以当前更诚实的说法不是“再派生一条 20c”，而是：
  - **量价交互主题未死，但它更像应上移到更一般化的 volume-quality / event-quality family；**
  - **不再适合作为 Rank 20 这条旧 parked line 的新派生提案继续命名。**

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park, but harder than before`

## Minimal audit note
This round does **not** reopen Rank 20.
It also does **not** draft `Rank 20c`.
The reason is not “no residual existed”, but rather: **the only honest residual had already been drafted as `Rank 20b` and then substantially consumed by `Rank 84` without surviving clean replication.**

## Git
- No commit.
- Reason: this round only makes minimal documentation updates, and the workspace contains unrelated dirty state.
