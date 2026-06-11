# bot3 optimization loop — dynamic cointegration admission × half-life-aware spread fade first verdict

- Time: 2026-04-21 23:22 UTC
- Cycle item: 2
- Target: `research/quant_digests/2026-04-21_2232_dynamic-cointegration-halflife-admission-alpha.md`
- Verdict: `background/P0`

## What I checked
只执行当前最前的 pending 小点：对 `dynamic cointegration admission × half-life-aware spread fade` 做 fresh intake first verdict，最小检查它是否相对固定 formation/timeout 真正留下了**非单 pair、非单窗支撑**的独立 after-cost pair-MR pocket，而不是只当已 live pairs family 的 admission / timeout 组件说明书。

读取 digest 与本地 artifacts：
- `jerry/momentum/research/quant_digests/2026-04-21_2232_dynamic-cointegration-halflife-admission-alpha.md`
- `jerry/momentum/reports/artifacts/quant_digests/dynamic_cointegration_halflife_summary_2026-04-21.csv`
- `jerry/momentum/reports/artifacts/quant_digests/dynamic_cointegration_halflife_pairs_2026-04-21.csv`

## Key evidence
### Summary layer
- `15m fixed96`: `262` trades, `gross_bps_per_trade ≈ -0.75`
- `15m dynamic`: `354` trades, `gross_bps_per_trade ≈ +0.19`
- `5m fixed96`: `255` trades, `gross_bps_per_trade ≈ +3.66`
- `5m dynamic`: `346` trades, `gross_bps_per_trade ≈ +3.64`

结论：dynamic admission + half-life timeout **确实改善了 fixed baseline**，尤其把 `15m` 从小幅负 gross 拉回到近零上方；但 strongest summary 也只有 `~3.6bps/笔` gross，仍明显不够覆盖短周期 perp pairs 至少双腿、且更接近四腿切换现实下的成本门槛。

### Pair concentration layer
动态模式下较厚 pocket 主要集中在：
- `15m ADAUSDT/LINKUSDT`: `45` trades, `+9.45bps/笔`
- `15m DOGEUSDT/ADAUSDT`: `44` trades, `+8.70bps/笔`
- `15m BTCUSDT/LINKUSDT`: `57` trades, `+4.76bps/笔`
- `15m SOLUSDT/LINKUSDT`: `41` trades, `+3.15bps/笔`
- `5m DOGEUSDT/ADAUSDT`: `35` trades, `+7.34bps/笔`
- `5m ADAUSDT/LINKUSDT`: `46` trades, `+4.89bps/笔`

但同一批结果里，多个主流/更广谱 pair 仍明显为负：
- `15m BTCUSDT/ETHUSDT`: `-3.09bps/笔`
- `15m BTCUSDT/SOLUSDT`: `-3.90bps/笔`
- `15m ETHUSDT/LINKUSDT`: `-9.36bps/笔`
- `15m ETHUSDT/SOLUSDT`: `-12.07bps/笔`

这说明它目前留下的是**少数 alt-alt / alt-heavy pair 的 gross pocket**，不是跨 pair 更广谱、可直接承接的 after-cost family。

### Distinctness layer vs live pairs family
当前 runtime 已有：
- `Rank 431 / cointegration maker-first + hard time-stop pairs`
- `Rank 424 / cointegration-first pair admission × strongest residual z-score spread fade`

本对象新增价值主要体现在：
1. 用 `half-life` 约束 formation / timeout；
2. 动态重估 pair admission，少做不该做的 pair。

但现有 artifacts 还没有证明这些改动形成了**独立于已 live pair family 的新增 after-cost alpha**；更像是现有 pair-MR 家族可吸收的 admission / timeout tuning 模块，而不是新的 queue-facing raw alpha 主语。

## Result
`dynamic cointegration admission × half-life-aware spread fade` 的 fresh intake first verdict 已诚实收口 `background/P0`：dynamic admission + half-life timeout 虽把固定窗 baseline 从 `15m gross≈-0.75bps/笔` 拉到 `≈+0.19bps/笔`、并在 `DOGE/ADA` 与 `ADA/LINK` 等少数 alt-heavy pairs 留下 `gross≈+4.9~+9.5bps/笔` pocket，但 strongest summary 仍不足以覆盖短周期 pairs 的现实双腿/四腿成本，而且正边际没有扩展成至少两个非单一 pair/单窗之外、相对已 live `Rank 431 / 424` 仍具独立新增价值的 after-cost alpha；因此本对象更适合作为 pairs family 的 admission/timeout 设计提示，而不是新的前排 fresh intake。
