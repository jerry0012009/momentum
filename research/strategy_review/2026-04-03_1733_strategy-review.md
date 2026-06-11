# Strategy Review — 2026-04-03 17:33 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short --branch`；只作 evidence，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-03_1730_rank314_orca_pairs_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-03_1703_rank313_survivor_followup_background_p0.md`
  - `research/optimization_loop/2026-04-03_1624_rank313_liquid_highmomentum_first_verdict_keep_p1.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-03_1631_strategy-review.md`
  - `research/strategy_review/2026-04-03_1544_strategy-review.md`
  - `research/strategy_review/2026-04-03_1453_strategy-review.md`
- 最近 fresh intake 材料：
  - `research/quant_digests/2026-04-03_1728_crossvenue-pricegap-close-alpha.md`
  - `research/quant_digests/2026-04-03_1647_polymarket-finalwindow-lagarb-alpha.md`
  - `research/quant_digests/2026-04-03_1425_hyperliquid-public-trigger-cluster-alpha.md`
  - `research/quant_digests/2026-04-03_1355_pumpfun-fastpath-graduation-alpha.md`

## 只回答 4 个问题

1) `Paper launch queue` 是否非空？
- 否。
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有待接线的 queue 头对象。

2) 本轮 `fresh intake` 是什么？
- 当前运行态里刚完成首判的 fresh intake 是：
  - `research/quant_digests/2026-04-03_1625_orca-tradability-cluster-pairs-alpha.md`
- 它已在 `research/optimization_loop/2026-04-03_1730_rank314_orca_pairs_first_verdict_keep_p1.md` 完成 first verdict，并获得正式编号 `Rank 314`；因此当前它不再是待首判 intake，而是合法占据前排的 survivor 来源对象。

3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 值得。
- 上一条 fresh intake 就是 `Rank 314 / ORCA tradability-aware cluster pairs`。
- 它的唯一 decisive blocker 很清楚：不是继续重复“高相关不等于可交易”这句方法论，而是要在统一 `5m/15m`、固定成本、walk-forward 的 execution shell 下，直接比较 `top-corr pairs` 与 `top tradability-score pairs`，回答 `tradability-aware / OU-like pair admission` 是否真能提升净后 `pnl/turn`、holding efficiency、stop-hit ratio 与 pair replacement stability。
- 若这一步成立，应直接升 `P2`；若 desk 口径下做不出净后改进，就该诚实收口到 `background/P0`。

4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`（`current_target = none`）。
- 最近一次明确 P2 出口仍是 `Rank 285` 在 `research/optimization_loop/2026-04-02_0159_rank285_p2_exit_rescope_to_p1.md` 完成的 `one-time P2->P1 re-scope`。
- 因此本轮没有需要 bot2 兜底直升 `P3` 的漏判 `Active P2` 对象。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Fresh intake slot.current_target = research/quant_digests/2026-04-03_1625_orca-tradability-cluster-pairs-alpha.md`
- `Surviving candidate slot.current_target = Rank 314 / ORCA tradability-aware cluster pairs`
- `Active P2 slot.current_target = none`
- 当前前排对象不存在无 rank 的 `P1 / P2 / P3`；本轮无需补发新的整数 `Rank`。

## P2 -> P3 兜底裁判检查
- 当前没有 `Active P2`。
- 最近 desk review / optimization 里也没有“已经足够 paper trade、但 bot3 尚未升级”的漏升对象。
- 因此本轮不直接写入新的 `P3 / Paper launch queue` 或 handoff 路径。

## 本轮排班改写
按 policy 默认顺序扫描后：
- `P3`：无待接线对象
- `P2`：无 active P2
- `P1`：有且仅有 `Rank 314` survivor follow-up，必须占据队首
- 然后才允许继续 fresh intake

因此本轮 `cycle_plan` 改写为：
1. `Rank 314 / ORCA tradability-aware cluster pairs`
2. `research/quant_digests/2026-04-03_1728_crossvenue-pricegap-close-alpha.md`
3. `research/quant_digests/2026-04-03_1647_polymarket-finalwindow-lagarb-alpha.md`
4. `research/quant_digests/2026-04-03_1425_hyperliquid-public-trigger-cluster-alpha.md`

改写理由：
- `Rank 313` 已在 `research/optimization_loop/2026-04-03_1703_rank313_survivor_followup_background_p0.md` 诚实收口，不再占前排。
- `Rank 314` 刚在 `research/optimization_loop/2026-04-03_1730_rank314_orca_pairs_first_verdict_keep_p1.md` 进入 survivor 槽位，按 policy 其唯一 follow-up 默认享有前排锁定权。
- 因此任何新的 fresh intake 都不得排到它前面。
- 在 fresh intake 候选上，优先选最近新的 strategy repo / paper / alpha 报告中时间最新、且 raw alpha 主语最清楚的对象：
  - 先是 `2026-04-03_1728_crossvenue-pricegap-close-alpha.md`，因为它把同一 underlier 的 cross-venue spread close 明确收敛成 `maker-first / inventory-aware` raw alpha 问题；
  - 再是 `2026-04-03_1647_polymarket-finalwindow-lagarb-alpha.md`，因为它把 `leader venue move -> hard-expiry binary odds lag repair` 写成独立可 paper 的主语；
  - 最后保留 `2026-04-03_1425_hyperliquid-public-trigger-cluster-alpha.md` 作为 conditional intake，因为它仍可能受 wallet discovery 稀疏度约束，优先级低于前两条更直接的新对象。
- `2026-04-03_1355_pumpfun-fastpath-graduation-alpha.md` 不是被否决，而是本轮预算下排在上述三条之后。

## 本轮写回内容
- 已更新：`docs/BOT2_BOT3_STATE.md`
- 已新增：`research/strategy_review/2026-04-03_1733_strategy-review.md`
- 未改动：policy / brief / operating card / auto loop / cron prompt

## 本轮改变系统认知的一句话
当前前排唯一必须先收口的是 `Rank 314` 的 survivor decisive follow-up；在它诚实走向 `P2` 或 `background/P0` 之前，本轮新的 fresh intake 只能从最近、主语最清楚的 `cross-venue spread close` 与 `Polymarket final-window lag arb` 里往后排，不能越过前排 survivor。