# bot3 auto — multi-venue median-outlier reversion first verdict

- time: 2026-04-23 11:44 UTC
- target: `research/quant_digests/2026-04-23_1053_xvenue-median-outlier-reversion-alpha.md`
- action: fresh intake first verdict
- verdict: `background/P0`

## Minimal honesty check
- 公开 summary 只显示 BTC/ETH 的中位离群厚度分别约 `0.187bps / 0.411bps`，属于极薄 pocket。
- 虽然存在 1-step compression，但 ETH 的 `still_gt_1bp_rate_next_sample` 仍高达 `74.3%`，说明离群后常常拖久，不是稳定、干净的短窗回归 pocket。
- 这条线与既有 cross-venue spread-close 家族（Rank 315 / 321 / 342）高度重叠，更像执行壳 / router 提示，而不是新的独立 raw alpha。

## Result
`Rankless multi-venue median-outlier reversion`：已完成最小 honesty 检查，当前只应收口为 `background/P0`，不进入 survivor。