# 2026-04-07 14:18 UTC strategy review

## Scope
按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 做本轮 40 分钟 desk review；只更新 runtime state，不改 policy / brief / operating card / auto loop / cron prompt。

## 先回答 4 个问题

### 1) `Paper launch queue` 是否非空？
**否。**

当前 `Paper launch queue.current_target = none`。`Rank 200 / 201 / 213 / 229 / 342` 都已经在 `connected_runner_live`；最近一条仍是 `Rank 342`，其 dedicated runner、scheduler 与首跑验证已在 `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md` 完成。因此本轮没有待接线的 `P3` 头对象。

### 2) 本轮 `fresh intake` 是什么？
**是 `research/quant_digests/2026-04-07_1412_breadth-conditioned-xs-momentum-router-alpha.md`。**

原因很直接：上一条 fresh intake `2026-04-07_1206_ratio-band-corrvol-pairs-alpha.md` 已在 `research/optimization_loop/2026-04-07_1342_ratio_band_corrvol_pairs_first_verdict_background.md` 完成 first verdict 并收口为 `background / P0`；当前又没有 `P3 / Active P2 / Surviving candidate` 的真实前排动作，所以必须按 policy 切回最近新的 strategy repo / paper / alpha 报告。最新具体对象就是这条 `breadth-conditioned XS momentum × shallow-bear sign-flip router`。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
**不值得。**

上一条 fresh intake 不是 `Rank 355`，而是已经刚刚做完 first verdict 的 `dzenanh/crypto-derivative-trading-engine`。它的结论已经很清楚：只证明了旧 `ratio-band pairs / stat-arb` 家族可以被工程化成 `corr/vol gate + 双腿执行` 的完整壳，没有形成独立的新 raw alpha 主语。因此它首判就应直接 `background / P0`，根本不该占用 survivor 的那唯一一次 follow-up。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在。**

`Active P2 slot.current_target = none`。最近的明确 `Active P2` 仍是 `Rank 342`，但它已经在 `research/optimization_loop/2026-04-05_2300_rank342_p2_exit_promote_p3_lowgas_samechain_paper_queue.md` 完成 `P2 -> P3`，随后又在 `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md` 完成最小接线，因此本轮不存在 bot2 需要兜底推进到 `P3 / P1 / P0` 的在场 `Active P2`。

## Rank / 前排合法性检查
- `Paper launch queue.current_target = none`，合法。
- `Surviving candidate slot.current_target = none`，且 `followup_budget_remaining = 0`，说明 `Rank 355` 已正常退出前排。
- `Active P2 slot.current_target = none`，合法。
- 当前前排不存在达到 `keep_P1 / P2 / P3` 但无正式 `Rank` 的对象，因此本轮无需补 rank。

## 最近证据与本轮判断
最近证据的顺序很清楚：

1. `research/optimization_loop/2026-04-07_1342_ratio_band_corrvol_pairs_first_verdict_background.md`
   - 已经把上一条 fresh intake 诚实收口为 `background / P0`，说明 fresh intake 槽位重新开放。
2. `research/optimization_loop/2026-04-07_1300_rank355_survivor_followup_exhausted_background.md`
   - 说明上一条 survivor 已经用完唯一 follow-up，并正常退出前排，不再占 survivor 锁。
3. `research/quant_digests/2026-04-07_1412_breadth-conditioned-xs-momentum-router-alpha.md`
   - 当前最新、最具体的 fresh intake 候选，且它补的是 `cross-sectional raw alpha` 这条当前仍值得继续 intake 的素材线。
4. `research/quant_digests/2026-04-07_1334_btc-coinm-carry-rollover-shell.md`
   - 次新的 repo 线索，属于 `carry / basis` 家族，但带着完整的 `15m execution + rollover/rehedge` 工程壳，值得做 first verdict。
5. `research/quant_digests/2026-04-07_1129_polymarket-pairsum-shield-maker-alpha.md`
   - 仍是合格的具体 fresh intake，但优先级低于上面两个更新的对象。

所以，这一轮的正确动作不是回头拖 `Rank 355`，也不是凭空制造新的 `P2/P3` 研究，而是**按 policy 干净地把当前轮切回新的 fresh intake，并按最新具体对象重排 `cycle_plan`。**

## 本轮 runtime 调整
本轮重写了 `docs/BOT2_BOT3_STATE.md`，变化只有两类：

### 1) Fresh intake slot
- `current_target` 从已完成 first verdict 的
  `research/quant_digests/2026-04-07_1206_ratio-band-corrvol-pairs-alpha.md`
  切到新的
  `research/quant_digests/2026-04-07_1412_breadth-conditioned-xs-momentum-router-alpha.md`
- `latest_result` 仍保留上一条 fresh intake 的已落地结论，不改写历史 verdict。

### 2) cycle_plan
当前没有 `P3 / P2 / P1` 前排动作，所以本轮按默认顺序直接切回具体 fresh intake，新的 4 项为：
1. `2026-04-07_1412_breadth-conditioned-xs-momentum-router-alpha.md`
2. `2026-04-07_1334_btc-coinm-carry-rollover-shell.md`
3. `2026-04-07_1129_polymarket-pairsum-shield-maker-alpha.md`
4. `2026-04-07_0333_crashtrim-volmanaged-xs-momentum-alpha.md`

每一项都符合 policy：
- 只写 `target / action / success_criterion / result / status`
- 新生成项的 `result = none`
- 新生成项的 `status = pending`
- 没有抽象模板句子、没有空占位、没有无具体对象的泛任务

## 为什么这轮不需要 bot2 兜底升 P3
这轮没有任何在场 `Active P2`：
- `Rank 342` 已经完成 `P2 -> P3 -> connected_runner_live`
- `Rank 355` 只到 `keep_P1`，且唯一 follow-up 已经用完并退出前排
- 当前剩下的都是 fresh intake，还没到 `P2` 门槛

因此不存在“desk review 已清楚表明足够值得 paper trade、但 bot3 尚未升级”的漏升对象；本轮无需 bot2 直接写入 `P3 / Paper launch queue`。

## 一句话总结
本轮前排已经收干净：`P3` 空、`P2` 空、`survivor` 空；因此我已把 runtime state 切回新的最新 fresh intake，并把 `breadth-conditioned XS momentum router` 放到本轮第一优先对象。