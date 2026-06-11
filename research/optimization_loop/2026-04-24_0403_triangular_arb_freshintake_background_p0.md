# bot3 optimization loop — triangular arb fresh intake first verdict -> background/P0

- Time: 2026-04-24 04:03 UTC
- Executor: bot3
- Policy basis: `docs/BOT2_BOT3_POLICY.md`
- Runtime basis: `docs/BOT2_BOT3_STATE.md`
- Cycle item executed: `research/quant_digests/2026-04-23_1910_triangular-arb-fee-capacity-reality-check.md`

## What was checked
只执行 fresh intake first verdict，沿 bot2 给出的唯一 decisive blocker 收口：
- 它是否留下任何**非单 snapshot lucky-run** 的、**after-fee executable** 的 tri-arb pocket；
- 还是只剩 `thin-leg veto / multi-leg execution realism` 这一类 shared execution 提示。

## Evidence used
来自 digest 自带的最小 live probe 与论文结论：
- Binance Spot `BTCUSDT / LTCBTC / LTCUSDT`
- 约 `60s × 2Hz = 120` snapshots
- `gross_a_pos_count = 0 / 120`
- `gross_b_pos_count = 0 / 120`
- `max gross_a = -4.55 bps`
- `max gross_b = -4.53 bps`
- 还未扣三腿手续费前，闭环最优盘口拼接已为负
- 最薄桥接腿 `LTCBTC` 平均 spread `14.04 bps`，明显主导摩擦
- 论文主结论同样指向：表面机会存在，但交易成本、滑点与容量会把可赚 pocket 基本吃光

## Decision
结论收口为 `background/P0`。

原因：
1. 最小 live probe 连**无费 gross edge 转正**都没有出现，更谈不上可执行的 after-fee pocket；
2. 当前材料没有拿出跨多三角、跨多时点、可在统一 friction 口径下仍为正的 executable alpha；
3. 对当前 desk 的新增价值主要退化为：
   - `gross edge != net executable edge` 的研究护栏；
   - `thin-leg spread / capacity` veto；
   - multi-leg relative-value 策略的 execution realism 教材；
4. 这些价值属于 shared execution sanity check，而不是值得进入前排的独立 raw alpha。

## Runtime impact
- 不分配 Rank；
- 不进入 `Surviving candidate slot`；
- fresh intake first verdict 直接收口 `background/P0`；
- `cycle_plan` 第 2 项标记 `done`。

## Result sentence
`triangular arb fee / capacity reality check` 的 fresh intake first verdict 已诚实收口 `background/P0`：最小 live probe 在 `BTCUSDT/LTCBTC/LTCUSDT` 上连无费 gross edge 转正都未出现，说明当前新增价值主要是 `thin-leg veto / multi-leg execution realism` 的 shared guardrail，而不是可独立排队的 after-fee tri-arb alpha。
