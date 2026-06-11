# 2026-04-19 21:14 UTC strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git -C /root/clawd/jerry/momentum status --short`
- Recent optimization evidence:
  - `research/optimization_loop/2026-04-19_2032_rank426_survivor_followup_background_p0_30m_1h_honesty.md`
  - `research/optimization_loop/2026-04-19_1951_supertrend_shortflip_freshintake_background_p0_timesymbol_concentration.md`
  - `research/optimization_loop/2026-04-19_1913_rank426_volume_switch_freshintake_keep_p1.md`
  - `research/optimization_loop/2026-04-19_1729_retailflow_downside_panic_bounce_freshintake_background_p0.md`
- Recent strategy review evidence:
  - `research/strategy_review/2026-04-19_1956_strategy-review.md`
  - `research/strategy_review/2026-04-19_1842_strategy-review.md`
- Fresh-intake source notes checked this round:
  - `research/quant_digests/2026-04-19_1932_hyperliquid-funding-signflip-shell.md`
  - `research/quant_digests/2026-04-19_2019_highvol-selloff-bounce-5m-alpha.md`
  - `research/quant_digests/2026-04-19_1906_hl-xs-overextension-fade-alpha.md`
  - `research/quant_digests/2026-04-19_1815_fibmacd-shallowpullback-continuation-alpha.md`

## Repo status snapshot
- 工作区仍有大量历史未跟踪临时文件与旧草稿；按 policy 只把它们视为噪声，不把“最近文件很多”误判成新的前排对象。
- 最近真正改变前排的动作只有两条：
  1. `Rank 426` 的 survivor 唯一 follow-up 已在 `2026-04-19_2032_rank426_survivor_followup_background_p0_30m_1h_honesty.md` 诚实收口到 `background/P0`；
  2. `ATR-adjusted trend flip × vol gate × strongest short flip router` 已在 `2026-04-19_1951_supertrend_shortflip_freshintake_background_p0_timesymbol_concentration.md` 直接收口到 `background/P0`。
- `Paper launch queue` 仍非空，但仅有 `connected_runner_live` 存量；当前没有待接线 `P3`。`Active P2` 仍为空。

## 仅回答 4 个问题
1. `Paper launch queue` 是否非空？
- 是，非空。
- 但 `current_target = none`，说明当前没有尚未完成 wiring 的 `P3` 前排动作。

2. 本轮 `fresh intake` 是什么？
- 本轮 `fresh intake` 仍应从：
- `research/quant_digests/2026-04-19_1932_hyperliquid-funding-signflip-shell.md`

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 不值得。
- 上一条 fresh intake 是 `research/quant_digests/2026-04-19_0446_supertrend-volgate-shortflip-router-alpha.md`。
- 最新 evidence 已明确：表面 `15m top1 short` 只有薄正且 `median net` 为负；改成更诚实的 `short-only top1` 复核后，整体 `net8≈-0.36bps/trade`，而且正收益主要集中在 `2026-02` 与少数 alt（AVAX/LTC/XRP），`2026-03/04` 已转负，因此不值得 survivor 唯一 follow-up，已经诚实收口到 `background/P0`。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`。
- 最近的前排旧对象 `Rank 426` 也已在 survivor follow-up 后收口到 `P0`，所以现在前排不存在需要 bot2 兜底直推 `P3` 的 `P2` 对象。

## Rank 完整性检查
- 当前前排对象不存在无 rank 污染：
  - `Surviving candidate = none`
  - `Active P2 = none`
  - `Paper launch queue.connected_runner_live` 中对象均已有正式 `Rank`
- 因此本轮无需补新的 rank。

## 排班结论
按 authoritative priority ladder 逐层扫描后：
1. `P3 handoff / launch wiring`：无未完成动作；queue 非空但仅为已接线 live 对象。
2. `P2 admission / promote / park`：无 `Active P2`。
3. `P1 survivor follow-up`：无；`Rank 426` 已在本轮前刚完成唯一 follow-up 并收口。
4. 因此前排真实可执行动作只剩新的 `fresh intake`，本轮预算应全部填入具体新对象。

## State rewrite
已重写 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan`，只保留当前真实可执行的 4 条 fresh intake：
1. `2026-04-19_1932_hyperliquid-funding-signflip-shell.md`
2. `2026-04-19_2019_highvol-selloff-bounce-5m-alpha.md`
3. `2026-04-19_1906_hl-xs-overextension-fade-alpha.md`
4. `2026-04-19_1815_fibmacd-shallowpullback-continuation-alpha.md`

所有新生成项均按 policy 写成：
- `result: none`
- `status: pending`

## Why this cycle_plan is policy-consistent
- 当前没有待接线 `P3`、没有 `Active P2`、也没有 survivor 锁定权对象，所以默认顺序自然切到 fresh intake。
- 4 个条目全部是具体对象，不含空模板、不含背景池 guard、不含抽象泛任务。
- 没有把 background pool 里的旧候选拉回前排；选的都是最近新的、尚未消费完的具体 digest。
- 当前 desk review 没有发现任何“已清楚足够进入 paper trade 但 bot3 尚未升级”的 `Active P2`，因此不存在 bot2 必须直接改写到 `P3` 的兜底场景。

## Review verdict
- `Paper launch queue` 非空，但当前没有待接线的 `P3`。
- 本轮 fresh intake 是 `hyperliquid funding sign-flip shell`。
- 上一条 fresh intake `supertrend short-flip router` 不值得 survivor follow-up，已经诚实收口到 `background/P0`。
- 当前没有 `Active P2`；前排已清空到只剩新 intake，因此本轮 `cycle_plan` 应全部切给具体 fresh intake。