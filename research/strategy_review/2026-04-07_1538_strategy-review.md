# 2026-04-07 15:38 UTC strategy review

## Scope
按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 做本轮 40 分钟 desk review；只更新 runtime state，不改 policy / brief / operating card / auto loop / cron prompt。

## 先回答 4 个问题

### 1) `Paper launch queue` 是否非空？
**否。**

当前 `Paper launch queue.current_target = none`。`Rank 200 / 201 / 213 / 229 / 342` 都已经在 `connected_runner_live`；最近一条仍是 `Rank 342`，其 dedicated runner、scheduler 与首跑验证已在 `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md` 完成。因此本轮没有待接线的 `P3` 头对象。

### 2) 本轮 `fresh intake` 是什么？
**是 `research/quant_digests/2026-04-07_1523_xemm-makerfirst-takerhedge-alpha.md`。**

原因：当前前排里存在合法 `Surviving candidate`，所以默认顺序先处理 survivor；但 `Fresh intake slot` 作为本轮新的 intake 入口，必须切到最新、尚未处理的具体对象。按最近 digest 时间顺序，最新合格对象是 `maker-first cross-venue quote gap × taker-hedge profitability buffer`。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得，而且它已经拿到了那唯一一次 follow-up 配额。**

上一条 fresh intake 是 `research/quant_digests/2026-04-07_1412_breadth-conditioned-xs-momentum-router-alpha.md`，已在 `research/optimization_loop/2026-04-07_1449_rank356_breadth_conditioned_xs_momentum_router_intake_keep_p1.md` 被正式写成 `Rank 356 / keep_P1`。根据 policy，任何 fresh intake 一旦首判为 `keep_P1`，其唯一 survivor follow-up 在诚实收口前享有前排锁定权，因此本轮第一优先不是再开新坑，而是把 `Rank 356` 的 single decisive follow-up 做完。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在。**

`Active P2 slot.current_target = none`。最近的明确 `Active P2` 仍是 `Rank 342`，但它已经在 `research/optimization_loop/2026-04-05_2300_rank342_p2_exit_promote_p3_lowgas_samechain_paper_queue.md` 完成 `P2 -> P3`，随后又在 `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md` 完成最小接线，因此本轮不存在 bot2 需要兜底推进到 `P3 / P1 / P0` 的在场 `Active P2`。

## Rank / 前排合法性检查
- `Paper launch queue.current_target = none`，合法。
- `Surviving candidate slot.current_target = Rank 356`，且该对象已有正式 rank，合法。
- `Active P2 slot.current_target = none`，合法。
- 当前前排不存在达到 `keep_P1 / P2 / P3` 但无正式 `Rank` 的对象，因此本轮无需补 rank。

## 最近证据与本轮判断
最近链条很清楚：

1. `research/optimization_loop/2026-04-07_1449_rank356_breadth_conditioned_xs_momentum_router_intake_keep_p1.md`
   - `Rank 356` 已完成 first verdict，并不是 generic XS momentum 重述，而是一个有独立命题的 `shallow-bear sign-flip router`，因此合规进入 survivor。
2. `research/optimization_loop/2026-04-07_1530_btc_coinm_carry_rollover_shell_first_verdict_background.md`
   - `1334 btc-coinm carry rollover shell` 已完成 first verdict 并诚实收口为 `background / P0`，说明 fresh intake 槽位已经重新打开。
3. `research/quant_digests/2026-04-07_1523_xemm-makerfirst-takerhedge-alpha.md`
   - 当前最新、最具体、尚未处理的新 repo/digest，对应本轮新的 fresh intake。
4. `research/quant_digests/2026-04-07_1436_majorlead-closeslot-crossmarket-itsm-alpha.md`
   - 次新的具体对象，可以作为前排收口后补入的第二条 intake。
5. `research/quant_digests/2026-04-07_1129_polymarket-pairsum-shield-maker-alpha.md`
   - 仍是合格的具体 intake，但优先级低于当前最新两条。

因此，这轮的正确动作不是空喊“继续 fresh intake”，也不是凭空制造 `P2/P3`；而是：
- 先把已有 survivor `Rank 356` 的唯一一次 follow-up 放到 `cycle_plan` 第 1 位；
- 再把新的 fresh intake 入口切到 `1523 xemm`；
- 剩余预算依次补 `1436` 与 `1129`。

## 本轮 runtime 调整
本轮重写了 `docs/BOT2_BOT3_STATE.md`，变化只有两类：

### 1) Fresh intake slot
- `current_target` 切到新的 `research/quant_digests/2026-04-07_1523_xemm-makerfirst-takerhedge-alpha.md`
- `latest_result` 仍保留最近已落地的 first verdict：`1334 btc-coinm carry rollover shell -> background / P0`
- 这符合 policy：历史结论不改写，但新的 intake 入口要指向当前最新尚未处理对象

### 2) cycle_plan
按 authoritative 顺序改写为：
1. `Rank 356` survivor follow-up（唯一一次 decisive 检查）
2. `1523 xemm-makerfirst-takerhedge` fresh intake
3. `1436 majorlead-closeslot-crossmarket-itsm` fresh intake
4. `1129 polymarket-pairsum-shield-maker` conditional fresh intake

每项都只写了 `target / action / success_criterion / result / status`；新生成项全部为 `result: none`、`status: pending`。

## 为什么这轮不需要 bot2 兜底升 P3
本轮没有任何在场 `Active P2`：
- `Rank 342` 已经完成 `P2 -> P3 -> connected_runner_live`
- `Rank 356` 只到 `keep_P1`，目前只配得上 survivor 的那唯一一次 follow-up
- 最新 digest 们都还没进 `P2`

因此不存在“desk review 已清楚表明足够值得 paper trade、但 bot3 尚未升级”的漏升对象；本轮无需 bot2 直接写入 `P3 / Paper launch queue` 或 handoff 路径。

## 一句话总结
本轮前排并不空：`P3` 空、`P2` 空，但 `survivor = Rank 356` 仍在前排锁定位。因此我已把 `Rank 356` 的唯一一次 follow-up 提到第一优先，并把新的 fresh intake 入口切到最新的 `1523 xemm`。