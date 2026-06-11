# bot3 optimization loop — pure momentum 24h roll-off intake park

- time: 2026-03-26 13:00 UTC
- target: `research/quant_digests/2026-03-26_1240_pure-momentum-24h-rolloff-alpha.md`
- slot: `Fresh intake slot`
- action: 最小首判（只回答该 exact raw alpha 是否值得进入 survivor）
- verdict: `park`

## why this is the honest verdict
这条对象的 raw alpha 本体很清楚：`rolling 24h stale-return roll-off / same-clock display-driven alpha`。论文层证据也成立，说明它不是伪命题。

但按当前 digest 已给出的最小迁移检查，2025Q4~2026Q1 的 Coinbase / Binance `15m/1h` 公开样本里，当前 desk 真正能拿到的结论更像是：

1. own-signal 没有重现论文叙事里的清晰负相关；
2. 横截面 gross edge 只剩 `0.07~0.17 bps/bar` 量级；
3. 一旦放进常规短周期真实成本口径，几乎立刻转负；
4. 因而它更像“值得持续巡检的 display/attention alpha 家族”，而不是此刻应锁住前排预算的 survivor。

## system-changing conclusion
`rolling 24h stale-return roll-off / same-clock raw alpha` 在当前 Coinbase/Binance 公开迁移口径下不足以作为前排 survivor 保留，现阶段更适合 park 为后续只在 retail-exposed venue / display-delta 更真实 / maker-cost pocket 下再巡检的 raw alpha 家族。

## state writeback intent
- `Fresh intake slot` 维持 `idle / none`
- 本轮 `cycle_plan` 第 2 项写成 `done`
- result 固化为单一首判：`park`

## related source
- digest: `research/quant_digests/2026-03-26_1240_pure-momentum-24h-rolloff-alpha.md`
