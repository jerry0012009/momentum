# Strategy Review — 2026-04-03 16:31 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short --branch`；只作 evidence，不反向改 policy）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-03_1624_rank313_liquid_highmomentum_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-03_1555_rank312_survivor_followup_background_p0.md`
  - `research/optimization_loop/2026-04-03_1542_rank312_adaptive_regime_first_verdict_keep_p1.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-03_1544_strategy-review.md`
  - `research/strategy_review/2026-04-03_1453_strategy-review.md`
  - `research/strategy_review/2026-04-03_1332_strategy-review.md`
- 最近 fresh intake 材料：
  - `research/quant_digests/2026-04-03_1625_orca-tradability-cluster-pairs-alpha.md`
  - `research/quant_digests/2026-04-03_1510_liquid-highmomentum-rolling-high-crosssectional-alpha.md`
  - `research/quant_digests/2026-04-03_1425_hyperliquid-public-trigger-cluster-alpha.md`
  - `research/quant_digests/2026-04-03_1355_pumpfun-fastpath-graduation-alpha.md`

## 只回答 4 个问题

1) `Paper launch queue` 是否非空？
- 否。
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有待接线的 queue 头对象。

2) 本轮 `fresh intake` 是什么？
- 运行态里刚完成首判的 fresh intake 是：
  - `research/quant_digests/2026-04-03_1510_liquid-highmomentum-rolling-high-crosssectional-alpha.md`
- 它已在 `research/optimization_loop/2026-04-03_1624_rank313_liquid_highmomentum_first_verdict_keep_p1.md` 完成 first verdict，并获得正式编号 `Rank 313`；因此当前它不再是待首判 intake，而是合法占据前排的 survivor 来源对象。

3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 值得。
- 上一条 fresh intake 就是 `Rank 313 / liquid-major distance-to-high cross-sectional continuation`。
- 它的唯一 decisive blocker 很清楚：不是再解释周频论文叙事，而是要在统一 `liquid majors 5m/15m`、统一 `4/6/8bps` 成本口径下，直接回答 `hmom / distance-to-high` 在 top-liquidity bucket 是否还能净后优于 generic `ret_n` baseline，以及 tail bucket 是否如预期更差或翻面。
- 若这一步成立，应直接升 `P2`；若 clean replication 做不出来，就该诚实收口到 `background/P0`。

4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`（`current_target = none`）。
- 最近一次明确 P2 出口仍是 `Rank 285` 在 `research/optimization_loop/2026-04-02_0159_rank285_p2_exit_rescope_to_p1.md` 完成的 `one-time P2->P1 re-scope`。
- 因此本轮没有需要 bot2 兜底直升 `P3` 的漏判 `Active P2` 对象。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Fresh intake slot.current_target = research/quant_digests/2026-04-03_1510_liquid-highmomentum-rolling-high-crosssectional-alpha.md`
- `Surviving candidate slot.current_target = Rank 313 / liquid-major distance-to-high cross-sectional continuation`
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
- `P1`：有且仅有 `Rank 313` survivor follow-up，必须占据队首
- 然后才允许继续 fresh intake

因此本轮 `cycle_plan` 改写为：
1. `Rank 313 / liquid-major distance-to-high cross-sectional continuation`
2. `research/quant_digests/2026-04-03_1625_orca-tradability-cluster-pairs-alpha.md`
3. `research/quant_digests/2026-04-03_1425_hyperliquid-public-trigger-cluster-alpha.md`
4. `research/quant_digests/2026-04-03_1355_pumpfun-fastpath-graduation-alpha.md`

改写理由：
- `Rank 312` 已在 `research/optimization_loop/2026-04-03_1555_rank312_survivor_followup_background_p0.md` 诚实收口，不再占前排。
- `Rank 313` 刚在 `research/optimization_loop/2026-04-03_1624_rank313_liquid_highmomentum_first_verdict_keep_p1.md` 进入 survivor 槽位，按 policy 其唯一 follow-up 默认享有前排锁定权。
- 因此任何新的 fresh intake 都不得排到它前面。
- 在 fresh intake 候选上，优先选最近新 repo/paper/alpha 报告中最新、且主语最清楚的新对象：
  - 先是 `ORCA` 这条 `tradability-aware clustering × OU spread mean reversion`，因为它提供了与普通 top-corr / coint pairs 不同的 pair-admission raw alpha 主语；
  - 再是 `Hyperliquid public trigger / liquidation cluster continuation` 这条 event-driven 主语；
  - 最后是 `same-vSOL fast-path launch continuation` 这条 launch-phase event 主语。

## 本轮写回内容
- 已更新：`docs/BOT2_BOT3_STATE.md`
- 已新增：`research/strategy_review/2026-04-03_1631_strategy-review.md`
- 未改动：policy / brief / operating card / auto loop / cron prompt

## 本轮改变系统认知的一句话
当前前排真正需要先收口的是 `Rank 313` 的 survivor clean replication，而不是继续跳过它去开新的 intake；在它诚实走向 `P2` 或 `background/P0` 之前，所有新的 fresh intake 都只能排在后面。