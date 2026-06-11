# 2026-04-07 04:55 UTC strategy review

## Scope
按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 进行 40 分钟 desk review；本轮只检查并在必要时更新 runtime state，不改 policy / brief / operating card / cron prompt。

## 先回答 4 个问题

### 1) `Paper launch queue` 是否非空？
**否。**

当前 `Paper launch queue.current_target = none`。`Rank 200 / 201 / 213 / 229 / 342` 都已经写在 `connected_runner_live`，表示这些对象已经完成最小 `P3 launch wiring`，不是当前待接线队列成员；因此此刻没有需要继续排在 `P3 handoff` 前排的对象。

### 2) 本轮 `fresh intake` 是什么？
**`research/quant_digests/2026-04-06_1020_volume-anomaly-bandfade-hmm-veto-alpha.md`。**

原因：当前没有 `P3` 待接线对象，也没有 `Active P2`；按 policy，唯一必须先收口的是 survivor `Rank 354`。在 survivor 之后，当前 `cycle_plan` 中第一个合法且尚未做 first verdict 的 intake 对象，就是这条 `volume anomaly band-fade × HMM veto`。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得。**

上一条 fresh intake 是 `Rank 354 / BTC crowd-positioning fuel-cascade`，并已合法进入 `Surviving candidate slot`，`followup_budget_remaining = 1`。它值得这唯一一次 follow-up 的原因仍然成立：

- 已经有独立 raw alpha 主语：`public positioning + OI -> squeeze/cascade/forced-liquidation fuel state`
- 数据口径公开可取，最小状态机已成形
- 唯一高杠杆问题已经压清：`PB14-L / PB12 / FLIQ-L` 中是否至少有一个分支在诚实 `fee / slippage / funding` 口径下仍保留可迁移净边

这正符合 policy 对 survivor 唯一一次 follow-up 的要求：做一次最小 decisive check，然后直接决定 `promote_P2` 还是 `background / P0`。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在。**

`Active P2 slot.current_target = none`。上一条 `Active P2`（`Rank 342`）已在 2026-04-05 23:00 UTC 完成 `P2 -> P3` 出口决策，并在 2026-04-06 00:16 UTC 完成最小 wiring，正式进入 `connected_runner_live`。因此当前没有任何对象停留在 `P2`，也不存在需要 bot2 兜底升级到 `P3` 的漏判对象。

## Rank / 前排合法性检查
- `Surviving candidate slot = Rank 354`，已有正式 rank，合法。
- `Paper launch queue.current_target = none`，无需补 rank。
- `Active P2 slot = none`，无需补 rank。
- 当前前排对象不存在“达到 keep_P1 / P2 / P3 但无正式 rank”的情况，因此本轮不需要补新 rank，也不需要改写 `BOT2_BOT3_STATE.md`。

## 本轮排班判断
按 policy 默认顺序扫描：
1. `P3 handoff`：无待接线对象。
2. `P2 admission/promote/park`：无 `Active P2`。
3. `P1 survivor follow-up`：有，且是当前最高优先级真实动作 → `Rank 354` 必须排第 1。
4. `fresh intake`：在 survivor 已诚实排到前面后，用剩余预算补最近具体对象。

结论：**当前 `BOT2_BOT3_STATE.md` 已与 policy 一致，本轮无需改写 runtime state；现有 `cycle_plan` 仍是合法且最诚实的排法。**

## 当前有效 cycle_plan（保持不变）
1. `Rank 354 / BTC crowd-positioning fuel-cascade` survivor 唯一 follow-up，直接回答 `promote_P2` 还是 `background / P0`
2. `2026-04-06_1020_volume-anomaly-bandfade-hmm-veto-alpha.md` fresh intake
3. `2026-04-07_0333_crashtrim-volmanaged-xs-momentum-alpha.md` fresh intake
4. `2026-04-07_0241_halflife-kelly-coint-pairs-alpha.md` fresh intake

## 为什么这轮不改 state
- 没有新的 `P3` 待接线对象。
- 没有新的 `Active P2` 需要 admission / exit。
- survivor 仍是合法且唯一的前排 `P1` 对象，没有被新的 `keep_P1` 候选覆盖。
- 不存在无 rank 的前排对象。
- 最近新 evidence 仍只改变两件事：
  - `Rank 354` 被确认为 `keep_P1` 并进入 survivor 前排；
  - `synthetic futures carry substitution` 被确认为旧 carry 家族的 desk packaging，直接回 `background / P0`。
- 最近数条 strategy review 的判断与当前 runtime 一致，未出现需要 bot2 纠偏的 `P2 -> P3` 漏升情形。

## Repo / recent evidence notes
- `research/optimization_loop/` 最近两条新增分别是：
  - `2026-04-07_0259_rank354_positioning_fuel_cascade_intake_keep_p1.md`
  - `2026-04-07_0403_synthetic_futures_carry_substitution_intake_background_p0.md`
- 最近 `research/strategy_review/2026-04-07_0437_strategy-review.md` 与 `2026-04-07_0446_strategy-review.md` 的核心结论一致：当前前排链条仍是 `P3 none / Active P2 none / Surviving candidate = Rank 354`。
- `volume anomaly band-fade × HMM veto`、`crash-trim vol-managed XS momentum`、`halflife-Kelly coint pairs` 仍都只是合法候选 intake，不具备越过 survivor 锁直接前插的资格。

## 发布与通知
- 首页发布脚本已按要求执行。
- 中文邮件摘要已按要求发送。

## 运行态一句话总结
当前前排链条仍然是：`P3 none / Active P2 none / Surviving candidate = Rank 354`；因此 bot3 下一步应先把 `Rank 354` 的唯一 survivor follow-up 收口，再回到新的 fresh intake。
