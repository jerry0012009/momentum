# 2026-03-21 04:42 UTC · Rank 34 park reframe review

## Scope
- Source rank: `Rank 34 / chip-distribution trapped-holder reclaim / winner-ratio gate`
- Original verdict stays: `park / evidence pool`
- This round only asks: **after the new 2026-03-20 digest, does Rank 34 now deserve one narrower derived reframe hypothesis?**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- prior reframe log:
  - `research/park_reframe/2026-03-18_0022_rank34-park-reframe.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_1222_rank34-clean-replication-park.md`
  - `research/optimization_loop/2026-03-17_1740_rank34-authoritative-writeback.md`
  - `research/quant_digests/2026-03-20_2038_chip-band-winner-ratio-not-shared-gate.md`

## Why this rank this round
- `Rank 34` 确实在最近 7 天内被 bot6 看过；正常应优先换别的。
- 但这条线在 `2026-03-20 20:38 UTC` 新增了一条**直接相关的新 digest**：`chip-band / winner-ratio` 被重新压回“assumptions-sensitive evidence，而不是 shared gate”。
- 所以这轮不是无意义重复，而是借新证据确认：**原来的 hard-park 读法有没有被推翻，或者至少能不能收敛出一条新的单轴 reframe。**

## 1) 原 rank 为什么 park？
原 `park` 的根因没有变：
**Rank 34 的亮点主要依赖 `synthetic shares / turnover anchor` 假设，核心问题落在估计层本身，而不是确认层太粗。**

关键旧证据（`chip_cost_reclaim`, `6bps/side`）：
- `conservative`：`mean_total_return ≈ +18.14%`，`positive_asset_ratio = 3/3`
- `neutral`：`mean_total_return ≈ +13.72%`，但 `positive_asset_ratio = 1/3`
- `aggressive`：`mean_total_return ≈ -18.62%`，`positive_asset_ratio = 1/3`

翻成人话：
- 这条线不是完全没有 pocket；
- 但 pocket 主要长在**最宽松 anchor** 上；
- 一旦把 shares / turnover 假设收紧，跨资产存活度和收益就一起塌。

因此原 `park` verdict 仍然有审计意义，不能被回收。

## 2) 它更像 hard park 还是 soft park？
**这轮仍然更像 `hard park`。**

原因：
- 新 digest 没有提供“同一信号换个更诚实确认层就能救”的证据；
- 相反，它进一步把问题压实为：`winner_ratio / cost band reclaim` 现在依旧只是 **assumption-sensitive evidence**；
- 也就是说，问题不是 gate 写得太薄，而是这套 holder-structure 叙事在当前公开数据近似下，仍然太依赖你怎么编 shares proxy。

这比 soft park 更硬：
soft park 通常意味着“主题还对，只是职责层错了”；
而 Rank 34 当前更像“主题有吸引力，但最核心可观测层还不够诚实”。

## 3) 有没有“可救信号”？
**有局部亮点，但还不够升级成可救信号。**

新 digest 带来的新增信息不是“它突然更稳了”，而是：
- `cost band reclaim` 这个想法仍可留在证据池里；
- 但它**不配直接升成 15m shared gate**；
- `winner_ratio` 也没有把这条线从 assumptions-driven pocket 变成稳健过滤层。

所以现在最诚实的表述是：
- 有“概念值得保留”的信号；
- 没有“足以派生新 queue-facing hypothesis”的信号。

## 4) 最值得改的唯一一刀是什么？
**仍然没有足够诚实的唯一一刀。**

最像“一刀”的候选其实是：
- 把 `fixed synthetic shares` 改成更真实的 `OI-based / turnover proxy`；或
- 只允许 `cost_p50 reclaim`，先去掉 `winner_ratio`。

但这两种写法都不够过关：
1. **改 shares proxy**：这其实是在动核心估计层，不是窄 reframe，而是“重做可观测基础设施”；
2. **删掉 winner_ratio**：新 digest 已经说明，哪怕退回更窄的 `cost band reclaim`，问题仍在 assumptions sensitivity，本质没变。

所以这轮依旧没有像 `Rank 32b / 35b` 那样清楚、诚实、单轴的切法。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

为什么：
- 原 hard blocker 没被新证据推翻；
- 新 digest 更像在**收紧这条线的上限**，而不是打开新的 rescue path；
- 若现在硬写一个 `Rank 34b`，最容易变成“先选一个更有利的 shares proxy，再把它包装成新假设”，这违反了 brief 想防止的事情。

## 6) trade on / trade off 结论
本轮**不形成**新的 `Rank 34b`。

更诚实的保留口径：
- `trade on`：holder-structure / cost-band reclaim 这个研究主题本身仍有解释力，值得继续作为证据池里的旁证；
- `trade off`：在当前 15m 公开数据近似下，它还没过“可稳定观测”的诚实门，因此不该被包装成新的 queue-facing 假设；
- 新 digest 的真正价值，是把它更明确地压回“evidence only”，而不是帮它重开。

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `hard park`

## Minimal audit note
This round revisits `Rank 34` only because there is **new evidence** after the prior bot6 review.
That new evidence does **not** overturn the old conclusion; it actually reinforces that `chip-band / winner-ratio reclaim` is still too assumption-sensitive to deserve a fresh derived hypothesis.

## Git / write scope
- 本轮只做最小必要写入：本日志、`research/park_reframe/INDEX.md`、`docs/PARK_REFRAME_QUEUE.md`
- 默认不改 `docs/TODO.md`
- 未做 git commit：仓库当前存在大量与本轮无关的共享脏文件，避免混提
