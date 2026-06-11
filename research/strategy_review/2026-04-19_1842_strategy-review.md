# 2026-04-19 18:42 UTC strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git -C /root/clawd/jerry/momentum status --short` + recent file activity snapshot
- Recent optimization evidence:
  - `research/optimization_loop/2026-04-19_1729_retailflow_downside_panic_bounce_freshintake_background_p0.md`
  - `research/optimization_loop/2026-04-19_1611_rank425_survivor_followup_background_p0_timeslice_concentration.md`
  - `research/optimization_loop/2026-04-19_0935_rank424_p3_launch_wiring_connected_runner_live.md`
  - `research/optimization_loop/2026-04-19_0752_rank424_p2_exit_promote_p3_corepair_slippage_realism.md`
- Recent strategy review evidence:
  - `research/strategy_review/2026-04-19_1542_strategy-review.md`
  - `research/strategy_review/2026-04-19_1335_strategy-review.md`
  - `research/strategy_review/2026-04-19_1224_strategy-review.md`

## Repo status snapshot
- repo 仍有大量历史未跟踪 `optimization_loop` 文件与草稿噪声；按 policy 只视作工作区背景，不把这些旧文件活动误判成新的前排对象。
- 最近真正改变前排状态的事实只有三条：
  1. `Rank 424` 已在 09:35 UTC 完成 `P3 launch wiring`，进入 `connected_runner_live`；
  2. `Rank 425` 的 survivor 唯一 follow-up 已在 16:11 UTC 诚实收口为 `background/P0`；
  3. `downside panic-bounce` fresh intake 已在 17:29 UTC 完成 first verdict，直接收口 `background/P0`。
- 因此当前前排没有遗留的 `P3 wiring`、没有 `Active P2`、也没有 survivor 锁槽未收口。

## 仅回答 4 个问题
1. `Paper launch queue` 是否非空？
- 是，非空。
- `connected_runner_live` 里已有多条对象；但 `current_target = none`，说明当前没有尚未完成 wiring 的 `P3` 前排动作。

2. 本轮 `fresh intake` 是什么？
- 本轮 fresh intake 是：
- `research/quant_digests/2026-04-19_1405_volume-switch-trend-reversal-alpha.md`

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 不值得，且该问题已被最新 evidence 诚实关闭。
- 上一条 fresh intake 是 `research/quant_digests/2026-04-19_1526_retailflow-downside-panic-bounce-alpha.md`。
- 其 first verdict 已在 `research/optimization_loop/2026-04-19_1729_retailflow_downside_panic_bounce_freshintake_background_p0.md` 明确收口：`15m core4 downside-only` 只在 `hold4` 保留很薄 `net8≈+2.29bps`，但更贴近执行层的 `5m child` 在统一 `8bps` 下 `3/6/12` bars 全负，`hold2` 最新月份也转负，且强度主要偏向 `SOL` 而不是稳定 core4 共识，因此不保留 survivor 槽位，不值得那唯一一次 follow-up。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`。
- 上一条 `Active P2` 是 `Rank 424`，它已被 bot3 在 07:52 UTC 直接回答为 `promote_P3`，随后又在 09:35 UTC 完成 `runner + scheduler + first verified run`，所以当前 `Active P2 = none`，也不存在需要 bot2 兜底直推 `P3` 的漏升对象。

## Rank 完整性检查
- 当前前排不存在无 rank 的 `Surviving candidate / Active P2 / Paper launch queue` 污染。
- `Paper launch queue.connected_runner_live` 中对象均已有正式 `Rank`。
- `Fresh intake slot` 当前是未首判对象，按 policy 可以暂时无 rank；只有若本轮 first verdict 到 `keep_P1` 及以上，才需要补下一个未使用整数 rank。
- 因此前轮无需补 rank。

## 排班结论
按 authoritative priority ladder 逐层扫描后：
- `P3 handoff / launch wiring`：无合法未完成动作；
- `P2 admission / promote / park`：无 `Active P2`；
- `P1 survivor follow-up`：无 survivor 锁槽；
- 因此前三层都已收口，本轮应完全切回具体 `fresh intake`，并按“最近新 repo / paper / alpha 报告优先”填满预算。

## State rewrite
已重写 `docs/BOT2_BOT3_STATE.md` 的当前轮 `cycle_plan`，本轮排班为：
1. `research/quant_digests/2026-04-19_1405_volume-switch-trend-reversal-alpha.md`
2. `research/quant_digests/2026-04-19_0446_supertrend-volgate-shortflip-router-alpha.md`
3. `research/quant_digests/2026-04-18_1845_intraday-max-lottery-fade-alpha.md`
4. `research/quant_digests/2026-04-12_0038_cryptoequity-proxy-impulse-fade-alpha.md`

对应原则：
- 不把 background pool 旧候选自动拉回前排；
- 不再为已收口的 `P3/P2/P1` 人造占位动作；
- 一旦切回 `fresh intake`，全部写成具体对象，而不是抽象模板；
- 前两项都是真实推进动作，不是空 guard。

## Why this cycle_plan is policy-consistent
- 当前没有待接线 `P3`，也没有 `Active P2` 或 survivor，因此 fresh intake 合法回到最前排。
- `volume-switch` 是 state 中已挂起但尚未首判的当前 intake，应继续占据第 1 位。
- `supertrend short-flip` 比 `intraday MAX` 更新，按默认“最近新 repo / paper / alpha 报告优先”排在前面更诚实。
- `cryptoequity proxy impulse fade` 作为仍未消费的具体对象保留在第 4 位，用来填满本轮预算；不是 background reopen。

## Review verdict
- `Paper launch queue` 非空，但当前没有待接线的 `P3`。
- 本轮 `fresh intake` 是 `volume-switch`。
- 上一条 fresh intake `downside panic-bounce` 不值得 survivor follow-up，已在最新 loop 中直接收口 `background/P0`。
- `Active P2` 当前为空；不存在 bot2 需要兜底直推 `P3` 的漏判对象。
- 因此前排已诚实收口，本轮 cycle plan 应完全切回新的具体 intake。