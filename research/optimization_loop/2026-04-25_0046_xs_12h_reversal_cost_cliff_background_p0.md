# bot3 optimization loop — xs 12h reversal cost cliff -> background/P0

- Time: 2026-04-25 00:46 UTC
- Target: `research/quant_digests/2026-04-24_2224_xs-12h-reversal-cost-cliff-portability.md`
- Action: fresh intake first verdict for `12h loser→winner fade × liquidity filter`
- Verdict: `background/P0`

## Why this step is decisive
本轮 success criterion 要求：只有在统一成本口径下，至少一个 `1h parent -> 15m/5m child` XS reversal pocket **明显成立**、且不是“流动性过滤后只是少亏一点”的语义时，才允许 `keep_P1`。

现有 digest 与 artifact 只提供了 repo 4H spot 结果，以及 desk 化的 Binance USDⓈ-M `1h` parent portability probe；没有拿出任何 `15m/5m child` after-cost pocket 为正的证据。相反，现有最优可见口径仍然是亏损。

## Minimal evidence checked
读取 `reports/artifacts/quant_digests/2026-04-24_xs_reversal_statarb_portability_probe.csv` 后，可见：

- 最优行已经是 `H=12, liq50, cost=8bps`
- 但其 `sharpe = -2.459368275798182`
- `final_equity = 0.952088786659101`
- 同条件下 `unfiltered` 更差：`sharpe = -8.529715668158818`, `final_equity = 0.8838455516214332`
- 升到 `12bps/20bps` 后进一步失真，`liq50 + H=12` 也仅到 `0.855 / 0.690`

这说明：
1. 流动性过滤的作用仍停留在“少亏一点”；
2. 当前最优父层口径都没有留下 after-cost 正边；
3. 还没有任何 child-execution artifact 能把 verdict 从 `repo 现货 4h 有想法` 推到 `short-cycle perp 有可独立交易 pocket`。

## System-level conclusion
`12h loser→winner fade × liquidity filter` 在当前 short-cycle crypto perp portability 口径下，唯一最小 decisive blocker 仍是：**缺少统一成本后可独立成立的 after-cost XS reversal pocket；现有证据反而显示最优可见配置仍为负 Sharpe/负净值。** 因此本轮不能给 `keep_P1`，应诚实收口为 `background/P0`。

## Runtime writeback
- Fresh intake first verdict complete for this target
- No rank assigned, because verdict did not reach `keep_P1`
- Front fresh intake should advance to the next pending object
