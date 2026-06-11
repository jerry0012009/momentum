# 2026-04-09 11:25 UTC · Rank 8b fresh intake first verdict

## Target
- `research/park_reframe/2026-03-19_0214_rank8-park-reframe.md`
- Object: `Rank 8b / adaptive ATR-scaled no-trade band`

## Why this step
按当前 `BOT2_BOT3_STATE.md` 的 `cycle_plan`，这是当前排在最前的 `pending` 小点，且属于 fresh intake first verdict。

## Minimal evidence used
1. `research/park_reframe/2026-03-19_0214_rank8-park-reframe.md`
2. `research/park_reframe/2026-04-07_1459_rank8-park-reframe.md`
3. `research/quant_digests/2026-03-19_0210_adjustable-band-ema-cost-survival.md`
4. `research/optimization_loop/2026-03-19_0350_rank78-band-intake.md`
5. `research/optimization_loop/2026-03-19_0410_rank78-band-clean-replication.md`
6. `research/optimization_loop/2026-03-19_0431_rank78-time-stability-scope-promotion.md`

## What changed system knowledge
这轮不需要重做第二次 replication；当前 decisive point 不是“adaptive band 有没有信息”，而是：**它现在是否足够独立，值得作为新的 queue-facing fresh intake 重新回到前排。**

现有证据给出的答案是否定的：

1. `Rank 8b` 从定义开始就是 **shielding / no-trade / admission suppression overlay**，不是独立 raw alpha body。
2. 2026-03-19 那轮最小 clean replication 虽然显示它在 `ema_psar_long` 上能明显少亏，但同一轮就已表明：
   - `breakout_short` 只有很弱的 supporting evidence；
   - `fib_retest_long` 明确转弱；
   - 因而更诚实的读法不是“共享 pocket 成立”，而是 **只在 EMA 主线上保留一个更窄的 suppression 角色**。
3. 紧接着的时间稳定性检查已经把 scope 明确收紧为 **`EMA-only suppression overlay`**；也就是说，这条线在最强时也只是 trend-shell / tradeability 层里的局部 gate，而不是一个可独立排队的新宿主。
4. 4 月初到现在的新证据继续把 EMA 主题往 **trend shell / exit shell / non-firing guardrail** 宿主里外流，而不是支持旧 `Rank 8` 血缘再长成新的 standalone pocket。`2026-04-07_1459_rank8-park-reframe.md` 也已明确：唯一值得保留的一刀仍止于 `8b`，没有新的 `8c`；今天若把 `8b` 本身再当 fresh intake 重开，本质上是在把既有 `tradeability / abstain` overlay 重新命名后再次认领。

## Verdict
- first verdict: `background / P0`
- reason: `Rank 8b` 的 `adaptive ATR-scaled no-trade band` 虽然对 EMA 主线有局部抑制价值，但其最诚实位置仍是既有 `volatility / tradeability overlay / trend-shell` family 内的 EMA-only suppression gate，没有长成不被现有宿主吸收的独立 queue-facing pocket。

## Result sentence
`Rank 8b` 的 `adaptive ATR-scaled no-trade band` 仍只是既有 `volatility / tradeability overlay / trend-shell` family 已吸收的 EMA-only suppression gate，没有新增证据证明它已长成独立 queue-facing pocket，因此本轮 first verdict 收口为 `background / P0`.
