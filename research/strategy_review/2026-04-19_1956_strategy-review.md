# 2026-04-19 19:56 UTC strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git -C /root/clawd/jerry/momentum status --short`
- Recent optimization evidence:
  - `research/optimization_loop/2026-04-19_1951_supertrend_shortflip_freshintake_background_p0_timesymbol_concentration.md`
  - `research/optimization_loop/2026-04-19_1913_rank426_volume_switch_freshintake_keep_p1.md`
  - `research/optimization_loop/2026-04-19_1729_retailflow_downside_panic_bounce_freshintake_background_p0.md`
  - `research/optimization_loop/2026-04-19_1611_rank425_survivor_followup_background_p0_timeslice_concentration.md`
- Recent strategy review evidence:
  - `research/strategy_review/2026-04-19_1842_strategy-review.md`
  - `research/strategy_review/2026-04-19_1802_strategy-review.md`
- Fresh-intake source notes checked this round:
  - `research/quant_digests/2026-04-19_1932_hyperliquid-funding-signflip-shell.md`
  - `research/quant_digests/2026-04-19_1906_hl-xs-overextension-fade-alpha.md`
  - `research/quant_digests/2026-04-19_1815_fibmacd-shallowpullback-continuation-alpha.md`

## Repo status snapshot
- 工作区仍有大量历史未跟踪临时文件与旧草稿；按 policy 只把它们视为噪声，不把“最近文件很多”误判成新的前排对象。
- 最近真正改变前排的只有两条：
  1. `Rank 426` 在 `2026-04-19_1913_rank426_volume_switch_freshintake_keep_p1.md` 获得 first verdict，成为当前唯一 survivor；
  2. `ATR-adjusted trend flip × vol gate × strongest short flip router` 在 `2026-04-19_1951_supertrend_shortflip_freshintake_background_p0_timesymbol_concentration.md` 被诚实收口到 `background/P0`。
- `Paper launch queue` 虽然非空，但当前只有 `connected_runner_live` 存量，没有待接线 `P3`；`Active P2` 也仍为空。

## 仅回答 4 个问题
1. `Paper launch queue` 是否非空？
- 是，非空。
- `connected_runner_live` 里已有多条对象；但 `current_target = none`，说明当前没有尚未完成 wiring 的 `P3` 前排动作。

2. 本轮 `fresh intake` 是什么？
- 本轮 fresh intake 应切到：
- `research/quant_digests/2026-04-19_1932_hyperliquid-funding-signflip-shell.md`

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 不值得。
- 上一条 fresh intake 是 `research/quant_digests/2026-04-19_0446_supertrend-volgate-shortflip-router-alpha.md`。
- 最新 evidence 已明确：表面 `15m top1 short` 只有薄正且 `median net` 为负；一旦改成更诚实的 `short-only top1` 复核，整体 `net8≈-0.36bps/trade`，且正收益几乎全来自 `2026-02` 与少数 alt（AVAX/LTC/XRP），`2026-03/04` 已转负，因此不值得 survivor 唯一 follow-up，已直接收口 `background/P0`。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`。
- 当前唯一前排非 fresh 对象是 `Rank 426` survivor；它尚未进入 `P2`，因此现在离的最近出口不是 `P3/P1/P0` 中的某个 `P2` 出口，而是先要完成 survivor 唯一 follow-up，直接回答是否 `promote_P2` 还是 `background/P0`。

## Rank 完整性检查
- 当前前排对象不存在无 rank 污染：
  - `Surviving candidate = Rank 426`
  - `Active P2 = none`
  - `Paper launch queue.connected_runner_live` 中对象均已有正式 `Rank`
- 因此本轮无需补新的 rank。

## 排班结论
按 authoritative priority ladder 逐层扫描后：
1. `P3 handoff / launch wiring`：无未完成动作；queue 非空但仅为已接线 live 对象。
2. `P2 admission / promote / park`：无 `Active P2`。
3. `P1 survivor follow-up`：有，且 `Rank 426` 作为“上一条 fresh intake 的唯一 survivor”享有前排锁定权，必须先于任何新 intake 收口。
4. 在 survivor 已诚实放到第 1 位之后，剩余预算再切回最近新的具体 intake。

## State rewrite
已重写 `docs/BOT2_BOT3_STATE.md`：
- `Fresh intake slot.status` 改为 `pending`
- `Fresh intake slot.current_target` 改为 `research/quant_digests/2026-04-19_1932_hyperliquid-funding-signflip-shell.md`
- 保留最近已完成 first verdict 为 `supertrend short-flip -> background/P0`
- `cycle_plan` 重排为：
  1. `Rank 426` survivor 唯一 follow-up：在 `30m / 1h` 低换手 spec 间做一次出口决策，直接回答 `promote_P2` 或 `background/P0`
  2. `2026-04-19_1932_hyperliquid-funding-signflip-shell.md`
  3. `2026-04-19_1906_hl-xs-overextension-fade-alpha.md`
  4. `2026-04-19_1815_fibmacd-shallowpullback-continuation-alpha.md`
- 所有新生成条目均按 policy 写成 `result: none`、`status: pending`

## Why this cycle_plan is policy-consistent
- 当前没有待接线 `P3`，也没有 `Active P2`，所以唯一合法的前排旧对象就是 `Rank 426` survivor。
- policy 明确要求：已有 `Surviving candidate` 的诚实收口优先级高于新发现，因此 `Rank 426` 必须排在第 1 位，不能被新的 fresh intake 覆盖。
- 在 survivor 已诚实占据首位后，余下 3 个预算位才切到最近新 digest；本轮选的都是最新、尚未消费的具体对象，不涉及 background reopen。
- 当前 desk review 没有发现任何“已明显达到 paper trade / paper launch 门槛但 bot3 尚未升级”的 `Active P2`，因此不存在 bot2 需要兜底直推 `P3` 的对象。

## Review verdict
- `Paper launch queue` 非空，但当前没有待接线的 `P3`。
- 本轮 `fresh intake` 应切到 `hyperliquid funding sign-flip shell`。
- 上一条 fresh intake `supertrend short-flip router` 不值得 survivor follow-up，已经诚实收口到 `background/P0`。
- 当前没有 `Active P2`；唯一必须优先收口的前排对象是 `Rank 426` survivor，其最近出口是“先决定升 `P2` 还是回 `P0`”，而不是继续开放式研究。
