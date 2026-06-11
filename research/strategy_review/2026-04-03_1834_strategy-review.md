# Strategy Review — 2026-04-03 18:34 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short --branch`；只作 evidence，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-03_1809_rank315_crossvenue_pricegap_close_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-03_1808_rank314_survivor_followup_promote_p2.md`
  - `research/optimization_loop/2026-04-03_1730_rank314_orca_pairs_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-03_1703_rank313_survivor_followup_background_p0.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-03_1733_strategy-review.md`
  - `research/strategy_review/2026-04-03_1631_strategy-review.md`
  - `research/strategy_review/2026-04-03_1544_strategy-review.md`
- 最近 fresh intake 候选材料：
  - `research/quant_digests/2026-04-03_1827_hedgevision-half-life-pairs-shell.md`
  - `research/quant_digests/2026-04-03_1647_polymarket-finalwindow-lagarb-alpha.md`
  - `research/quant_digests/2026-04-03_1425_hyperliquid-public-trigger-cluster-alpha.md`

## 只回答 4 个问题

1) `Paper launch queue` 是否非空？
- 否。
- `Paper launch queue.current_target = none`。
- 当前仍只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有新的待接线 queue 头对象。

2) 本轮 `fresh intake` 是什么？
- 运行态里刚完成首判的 fresh intake 是：
  - `research/quant_digests/2026-04-03_1728_crossvenue-pricegap-close-alpha.md`
- 它已在 `research/optimization_loop/2026-04-03_1809_rank315_crossvenue_pricegap_close_first_verdict_keep_p1.md` 完成 first verdict，并获得正式编号 `Rank 315`；因此当前它不再是待首判 intake，而是合法占据前排的 survivor 来源对象。

3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 值得。
- 上一条 fresh intake 就是 `Rank 315 / cross-venue same-underlier spread close`。
- 它的唯一 decisive blocker 已很清楚：不是再泛谈“跨所价差曾经有效”，而是要在统一 `symbol × venue-pair` admission、统一 `maker+maker / maker+taker / taker+taker` 成本口径、以及 `majors vs alt pocket` 对照下，直接回答当前 desk 是否仍存在至少一个可净后存活的 `alt / venue-specific dislocation × maker-first / inventory-aware` pocket。
- 若这一步成立，应直接升 `P2`；若诚实成本后只剩 execution 生意或不可复现偶然，就该回 `background/P0`。

4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前存在明确 `Active P2`：`Rank 314 / ORCA tradability-aware cluster pairs`。
- 它当前离 `P3` 最近，但还没到可以 bot2 直接兜底升 `P3` 的程度。
- 原因不是 effectiveness 不够，而是最新 admission 证据只证明了 `tradability-aware` book 在统一 `5m/15m`、固定成本、walk-forward 壳下，相对 `top-corr` 拿到更高净后回报与更短 holding；本轮还没有完成 `turnover / replacement friction / refresh cadence / stability penalty / honesty` 的更真实收口。
- 因此它本轮应该进入面向 `P3` 的 P2 出口决策前置检查，而不是回退 `P1`，也不是被提前打到 `P0`。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Fresh intake slot.current_target = research/quant_digests/2026-04-03_1728_crossvenue-pricegap-close-alpha.md`
- `Surviving candidate slot.current_target = Rank 315 / cross-venue same-underlier spread close`
- `Active P2 slot.current_target = Rank 314 / ORCA tradability-aware cluster pairs`
- 当前前排对象不存在无 rank 的 `P1 / P2 / P3`；本轮无需补发新的整数 `Rank`。

## P2 -> P3 兜底裁判检查
- 当前虽有 `Active P2 = Rank 314`，但最新 desk review / optimization 仍未清楚证明它已经“足够值得直接进入 paper trade / paper launch”。
- 缺的不是更多同轴 effectiveness 复读，而是 `turnover / replacement friction / refresh cadence / stability penalty / honesty` 这一轮更真实的出口检查。
- 因此本轮不直接把 `Rank 314` 写入新的 `P3 / Paper launch queue` 或 handoff 路径；但其最近出口已明确偏向 `P3`，不是 `P1/P0`。

## 本轮排班改写
按 policy 默认顺序扫描后：
- `P3`：无待接线对象
- `P2`：有且仅有 `Rank 314`，必须排队首
- `P1`：有且仅有 `Rank 315` survivor 唯一 follow-up，必须排在 `Active P2` 之后、所有新 intake 之前
- 然后才允许继续 fresh intake

因此本轮 `cycle_plan` 改写为：
1. `Rank 314 / ORCA tradability-aware cluster pairs`
2. `Rank 315 / cross-venue same-underlier spread close`
3. `research/quant_digests/2026-04-03_1827_hedgevision-half-life-pairs-shell.md`
4. `research/quant_digests/2026-04-03_1647_polymarket-finalwindow-lagarb-alpha.md`
5. `research/quant_digests/2026-04-03_1425_hyperliquid-public-trigger-cluster-alpha.md`

改写理由：
- 现在前排已经不是空的：`Rank 314` 是明确 `Active P2`，`Rank 315` 是刚进入 survivor 槽位的唯一 follow-up。
- 按 policy，已有前排对象的收口优先级永远高于新的发现，所以任何 fresh intake 都不得越过 `Rank 314` 与 `Rank 315`。
- `Rank 314` 这轮应当从 admission 成功后的 `keep_P2` 舒适区，推进到真正面向 `P3` 的出口检查；否则会落入同 axis 低杠杆重复。
- `Rank 315` 已首判 `keep_P1`，其唯一 follow-up 默认享有 survivor 锁定权，因此也不能被新的 `keep_P1` 候选覆盖。
- fresh intake 上优先选 `2026-04-03_1827_hedgevision-half-life-pairs-shell.md`，因为它是最近新 repo / alpha 报告里最新的一条，而且虽然仍属 pairs 家族，但主语是 `half-life/Hurst admission × z-score/time-stop shell`，可先检验其对当前 `Rank 314` 轴是否提供独立增量，而不是直接把旧 pairs 叙事重复一遍。
- 之后再排 `Polymarket final-window lag arb` 与 `Hyperliquid public trigger cluster` 两条更异质的 fresh intake；前者主语独立、paper shell 清楚，后者仍带 wallet discovery 工程依赖，所以放在最后作为 conditional intake。

## 本轮写回内容
- 已更新：`docs/BOT2_BOT3_STATE.md`
- 已新增：`research/strategy_review/2026-04-03_1834_strategy-review.md`
- 未改动：policy / brief / operating card / auto loop / cron prompt

## 本轮改变系统认知的一句话
当前前排不但没清空，反而已形成清楚链条：`Rank 314` 先做面向 `P3` 的 P2 出口检查，`Rank 315` 紧随其后完成唯一 survivor follow-up；只有这两件事被诚实排进前部后，新的 fresh intake 才能从 `hedgevision / Polymarket / Hyperliquid` 依次接上。