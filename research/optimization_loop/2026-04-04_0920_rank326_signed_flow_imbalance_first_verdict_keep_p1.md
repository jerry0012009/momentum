# Rank 326 — signed flow imbalance × maker-only conviction gate first verdict: keep P1

- Time: 2026-04-04 09:20 UTC
- Target: `research/quant_digests/2026-04-04_0849_signed-flow-imbalance-maker-conviction-alpha.md`
- Verdict: `keep_P1`
- New rank: `Rank 326`
- Slot impact: fresh intake 完成后进入 `Surviving candidate slot`

## Why this changes runtime truth
这条材料已经把三层分账讲清：
1. **base alpha**：`1m signed trade imbalance -> 5m forward return`
2. **conviction gate**：只在预测净边际显著大于成本时入场，而不是把微弱流向直接硬交易
3. **execution economics**：repo 自带 `maker-only / 低费率` 生存前提，已明确承认这条 edge 对执行成本高度敏感

因此它不是把 README 里的“OBI”标签误当结论；真正可 intake 的，是一条可独立于现有 pairs / carry / trend 主线的 **short-cycle microstructure raw alpha shell**。

## Honest limits
- digest 里的便携性快检同时说明：repo 的 `15bps` threshold 对线性单因子读法明显过高；
- 小样本非线性 probe 虽然能打出交易，但主导特征更多落在 volatility interaction，而不是纯 `obi`；
- 所以这轮不能直接升 `P2`，但足够进入一次 survivor follow-up，去判断它到底是独立 alpha，还是更适合作为 shared microstructure gate。

## Runtime result sentence
`Rank 326`：`1m signed trade imbalance -> 5m forward return` 已形成带 `nonlinear conviction gate + maker-only execution economics` 的最小 `1m/5m` microstructure desk shell，因此 first verdict 记为 `keep_P1`，并进入 survivor follow-up。
