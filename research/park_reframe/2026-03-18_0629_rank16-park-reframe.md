# 2026-03-18 06:29 UTC · Rank 16 park reframe review

## Scope
- Source rank: `Rank 16 ORB threshold + protective closing session gate`
- Original verdict stays: `park / evidence pool`
- This round only asks: **should Rank 16 derive one narrower reframe hypothesis, without overturning the original park?**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- recent reframe logs:
  - `research/park_reframe/2026-03-18_0429_rank15-park-reframe.md`
  - `research/park_reframe/2026-03-18_0229_rank27-park-reframe.md`
  - `research/park_reframe/2026-03-18_0022_rank34-park-reframe.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_0139_rank16-orb-protective-closing-intake.md`
  - `research/optimization_loop/2026-03-17_0159_rank16-clean-replication-park.md`
  - `research/quant_digests/2026-03-18_0549_session-range-active-hours-gate.md`

## Why this rank
- It is within `Rank 1~37` and currently parked.
- It has **not** been reviewed by `bot6` in the recent 7-day reframe queue.
- The original result was bad enough to park, but not uniformly pointless: `raw_orb -> confirm1_outside` materially reduced loss, which suggests the failure may be more about **where/when** the trigger is allowed than about breakout confirmation being useless.
- The new session-range / active-hours digest gives a fresh, still-narrow rewrite path that stays close to Rank 16's original `session threshold + confirmation` story.

## 1) 原 rank 为什么 park？
Rank 16 被 park，不是因为“session threshold / breakout confirmation 完全没意义”，而是因为当前冻结的 **`pseudo-open ORB + confirm/protective close`** 版本，仍然没有形成可升格 pocket。

原 clean replication 关键证据：
- `raw_orb @ 6bps/side`：`mean_total_return≈-35.11%`
- `confirm1_outside @ 6bps/side`：`≈-7.51%`，但 `positive_asset_ratio=0/3`、`mean_trades≈154.7`
- `retest_hold @ 6bps/side`：`≈-8.36%`
- `protective_close_overlay @ 6bps/side`：`≈-21.50%`
- 参数邻域（`range_bars=2/3`, `tau=0/0.1/0.2 ATR`）`0/6` 为正
- 成本梯度继续恶化：`10bps≈-18.26%`、`15bps≈-29.96%`、`20bps≈-39.98%`

更直白地说：
- `confirm1_outside` 确实比裸 ORB 少亏很多；
- 但它仍然是 **高频交易、跨资产全负、成本后持续塌**；
- `protective close` 也没有把它救回来；
- 所以原 `park` verdict 必须保留。

## 2) 它更像 hard park 还是 soft park？
**更像 `soft park`。**

原因：
- 从 `raw_orb≈-35.11%` 到 `confirm1_outside≈-7.51%`，说明确认层并非无效；
- 真正的 blocker 更像：**把股票 ORB 的固定 pseudo-open 语义，过于直接地搬进了 crypto 24/7 环境**；
- 也就是说，问题不一定是“session threshold 方向错了”，更可能是“当前 session 定义过硬、过机械，没把 crypto 的活跃时段 / session 结构位写对”。

所以这条线更适合被读成：
- 原 rank 继续 park；
- 但保留一个很窄的 reframe 入口，而不是当成彻底 hard fail 封死。

## 3) 有没有“可救信号”？
**有，但信号集中在“时段/结构重写”而不是继续磨 protective exit。**

最值得保留的可救信号：
1. 原 clean replication 已证明：`confirm1_outside` 相对 `raw_orb` 明显少亏，说明 `threshold / confirm` 这根骨架不是完全无效；
2. 交易数并没有塌到不可用，说明它不是靠极端 `no-trade` 才显得好看；
3. 新 digest `2026-03-18_0549_session-range-active-hours-gate.md` 给了一个更贴近 crypto 的解释：
   - 15m 信号不该全天 24h 同权；
   - 更自然的写法是 **active-hours + session-range structure gate**，而不是固定 `00:00 / 08:00 / 13:30 UTC` pseudo-open ORB。

这三个点连起来，更像是在说：
- Rank 16 的问题不只是 breakout 太噪；
- 而是 **session trigger 的定义不够像 crypto 真正有参与度的 intraday 结构**。

## 4) 最值得改的唯一一刀是什么？
**唯一主修改轴：把固定 `pseudo-open ORB`，改写成 `active-hours session-range break/retest gate`。**

保持不变的部分：
- 仍保留 `session threshold + close-confirm` 的主故事；
- 仍保留 `next-bar open + no-overlap` 的最小执行口径；
- 仍保留当前 desk 对 `15m crypto` continuation / retest 的 clean-room 框架；
- 不扩成 `volume + ADX + VWAP + liquidity sweep` 多轴大礼包。

唯一改变的是 session trigger 的来源：
- 旧：围绕固定 pseudo-open 的 opening range 做 ORB；
- 新：只在更有参与度的时段（如 `London / NY / overlap`）围绕最近 session high/low 的突破后 `1~4` 根内，观察 `break + retest / continuation` 是否成立。

## 5) 是否值得形成新的 derived hypothesis？
**值得，结论：`derived_hypothesis_drafted`。**

理由不是原 rank 翻案，而是：
- 原 evidence 已说明确认层方向有边际价值；
- 新 digest 提供了一个足够窄、足够贴近 crypto 24/7 执行语义的单轴改写；
- 这条改写可以先作为 `bot2` 后续是否入板的短提案存在，不需要现在就动 `TODO` 顶部排班。

## 6) Drafted derived hypothesis
- `proposed_rank`: `Rank 16b / Rank 16 session-range active-hours gate`
- `source_rank`: `Rank 16`
- `status`: `derived_hypothesis_drafted`
- `single modification axis`: `replace fixed pseudo-open ORB trigger with active-hours session-range break/retest gate`
- `trade on`: `只在更有参与度的时段（优先 London / NY / overlap）内，若价格刚突破最近 session high/low，并在随后 1~4 根 15m bar 内完成 close-confirm continuation 或 retest reclaim，则按 next-bar open 入场`
- `trade off`: `若信号发生在低参与度 dead hours、离最近 session 结构位过远、突破后迟迟没有 retest/continuation 确认，或很快跌回/站回失效侧，则 setup 直接取消；不再把固定 pseudo-open 的 opening-range breach 当默认触发`
- `trade on / trade off summary`: `保留 session-threshold / confirmation 的主故事，但把“固定开盘区间突破”改成“活跃时段里的 session-range 结构突破/回踩确认”`
- `trade on`: 更贴近 crypto 的 intraday periodicity，也更有机会减少 dead-hour chop
- `trade off`: 会牺牲“机械简单”的 ORB 语义；若 active-hours 只是 disguised volatility filter，也可能只是在换一种切样本方式
- `why now`: 原 rank 已显示 `confirm1_outside` 明显优于 `raw_orb`，说明 session confirmation 方向并未被判死；而最新 digest 又直接给出更贴近 crypto 的单轴替代——把固定 pseudo-open 改成 active-hours + session-range structure，因此现在出现了一个足够诚实的窄派生入口
- `suggested_initial_state`: `source intake / clean replication next`

## Final verdict for this round
- `verdict`: `derived_hypothesis_drafted`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park`

## Minimal audit note
This round does **not** reopen Rank 16 itself.
It only records that if the desk later wants one narrow salvage attempt from the parked pool, the most honest single-axis derivative is:
**`Rank 16b = keep session-threshold confirmation, but replace fixed pseudo-open ORB with active-hours session-range break/retest gating`.**

## Git
- 本轮只做最小必要文档改动；未做 commit。
- 原因：工作区仍有无关脏文件，当前不适合安全地 selective commit。
