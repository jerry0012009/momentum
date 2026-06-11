# Strategy Review — 2026-04-03 19:38 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short`；只作 evidence，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-03_1913_hedgevision_pairs_shell_first_verdict_background_p0.md`
  - `research/optimization_loop/2026-04-03_1858_rank315_survivor_followup_background_p0.md`
  - `research/optimization_loop/2026-04-03_1838_rank314_p2_turnover_replacement_friction_keep_p2.md`
  - `research/optimization_loop/2026-04-03_1808_rank314_survivor_followup_promote_p2.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-03_1834_strategy-review.md`
- 最近 fresh intake 候选材料：
  - `research/quant_digests/2026-04-03_1936_wintermute-hl-tiered-maker-ladder-alpha.md`
  - `research/quant_digests/2026-04-03_1845_pacifica-hl-maker-taker-xemm-alpha.md`
  - `research/quant_digests/2026-04-03_1647_polymarket-finalwindow-lagarb-alpha.md`
  - `research/quant_digests/2026-04-03_1425_hyperliquid-public-trigger-cluster-alpha.md`

## 只回答 4 个问题

1) `Paper launch queue` 是否非空？
- 否。
- `Paper launch queue.current_target = none`。
- 当前仍只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有新的待接线 queue 头对象。

2) 本轮 `fresh intake` 是什么？
- 本轮重新排班后，fresh intake 头切到：
  - `research/quant_digests/2026-04-03_1936_wintermute-hl-tiered-maker-ladder-alpha.md`
- 理由：前排 `P3/P2/P1` 里目前只剩 `Rank 314` 这个明确 `Active P2`；`Rank 315` survivor 已在 18:58 UTC 用尽唯一一次 follow-up 并收口到 `background/P0`，`hedgevision` 也已在 19:13 UTC 完成 first verdict 并收口到 `background/P0`。因此 fresh intake 可以切到最近、且主语最独立的新 repo 材料。

3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 不适用；答案等价于“否，因为这一步已经结束了”。
- 上一条 fresh intake 是 `research/quant_digests/2026-04-03_1827_hedgevision-half-life-pairs-shell.md`。
- 它已在 `research/optimization_loop/2026-04-03_1913_hedgevision_pairs_shell_first_verdict_background_p0.md` 完成 first verdict，并被明确记入 `background/P0`：原因是它与 `Rank 314` 的 `pairs admission-layer` 证据轴高度重合，只是把 `half-life/Hurst admission × z-score/time-stop` 壳整理得更清楚，没有提供足以单独抢占 survivor 槽位的独立 raw alpha 增量。
- 既然上一条 fresh intake 已首判直接收口到 `P0`，就不存在值得给它 survivor 唯一 follow-up 的空间。

4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 有：`Rank 314 / ORCA tradability-aware cluster pairs`。
- 它离 `P3` 最近，但 bot2 这轮还不能直接兜底升 `P3`。
- 原因：最新证据（`2026-04-03_1838_rank314_p2_turnover_replacement_friction_keep_p2.md`）已经说明它相对 classic `top-corr` 的净后优势存在，但这层优势目前主要来自更高 turnover / 更高 pair remap，而不是更高单笔效率；上一轮的明确 blocker 是 `replacement_friction_refresh_cadence_stability_penalty`。
- 因此这轮合法动作不是退回 `P1`，也不是继续开放式 `keep_P2`，而是直接做最后一轮 `honesty / execution realism` 出口决策：若在更懒 refresh 与更真实 maker/taker / remap friction 下仍能保留优势，就直接 `promote_P3`；否则应收口到 `P0`。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Fresh intake slot.current_target = research/quant_digests/2026-04-03_1936_wintermute-hl-tiered-maker-ladder-alpha.md`
- `Surviving candidate slot.current_target = none`
- `Active P2 slot.current_target = Rank 314 / ORCA tradability-aware cluster pairs`
- 当前前排对象不存在无 rank 的 `P1 / P2 / P3`；本轮无需补发新的整数 `Rank`。

## P2 -> P3 兜底裁判检查
- 当前虽有 `Active P2 = Rank 314`，但现有 desk review 还没清楚到能让 bot2 直接改写为 `P3 / Paper launch queue`。
- 关键不是它没 edge，而是最新 evidence 还没有在更懒 refresh cadence 与更真实 maker/taker / pair remap friction 下完成最终 honesty 出口决策。
- 因此 bot2 本轮不越权直接升 `P3`；但也不允许继续写成开放式研究，而是把它明确排成 **出口决策轮**。

## 本轮排班改写
按 policy 默认顺序扫描后：
- `P3`：无待接线对象
- `P2`：有且仅有 `Rank 314`，必须排队首
- `P1`：当前无 survivor；`Rank 315` 已收口，不能再假装前排仍占用 survivor 槽位
- 然后才允许切 fresh intake

因此本轮 `cycle_plan` 改写为 4 项：
1. `Rank 314 / ORCA tradability-aware cluster pairs`
2. `research/quant_digests/2026-04-03_1936_wintermute-hl-tiered-maker-ladder-alpha.md`
3. `research/quant_digests/2026-04-03_1845_pacifica-hl-maker-taker-xemm-alpha.md`
4. `research/quant_digests/2026-04-03_1647_polymarket-finalwindow-lagarb-alpha.md`

改写理由：
- 现存唯一前排合法动作就是 `Rank 314` 的 P2 出口决策，因此它必须放在第一位。
- `Surviving candidate slot = none`，说明本轮可以诚实切回 fresh intake；但切回 fresh intake 后必须直接指定具体对象。
- 新 intake 里优先选 `wintermute`，因为它是最新材料，而且主语与当前 pairs / binary / trigger-cluster 线条最不重合：`symmetric tiered maker ladder × inventory-skew / external hedge` 是独立 maker raw alpha，而不是再补一条相似的 pairs / lag-arb 壳。
- 第二条 fresh intake 选 `pacifica × hyperliquid maker-taker xemm`，因为它和 `wintermute` 同属 maker / execution family，但 alpha 主语更偏 `cross-venue maker-taker relative-value`，可与单 venue maker ladder 形成明显区分。
- 第三条 conditional fresh intake 保留 `polymarket final-window lag arb`，因为它主语清楚、`5m/15m` paper shell 也完整；但在优先级上仍低于更近的新 repo 材料。
- `hyperliquid public trigger cluster` 本轮被诚实挤出前四，不是因为它无价值，而是当前最靠前的 4 个合法动作已被填满；它仍保留在候选池里，但不该越过更近、更独立的新 repo intake。

## 本轮写回内容
- 已更新：`docs/BOT2_BOT3_STATE.md`
- 已新增：`research/strategy_review/2026-04-03_1938_strategy-review.md`
- 未改动：policy / brief / operating card / auto loop / cron prompt

## 本轮改变系统认知的一句话
当前前排已从“`Rank 314` + `Rank 315` 双前排”收口为“只剩 `Rank 314` 一个明确 `Active P2`”；因此本轮应该先逼它做 `P3 vs P0` 的 honesty 出口决策，再把 fresh intake 头切到最新、主语最独立的 `wintermute tiered maker ladder`。