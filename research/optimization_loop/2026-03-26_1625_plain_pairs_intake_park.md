# Rankless intake 首判：plain-vanilla spread convergence long-short baseline → park

- Time: 2026-03-26 16:25 UTC
- Target: `research/quant_digests/2026-03-26_1505_plain-pairs-longshort-vs-longonly.md`
- Slot acted on: `Fresh intake slot`
- Action: 最小首判（只回答这条 exact raw alpha 是否值得进入 survivor）
- Verdict: `park`
- Rank assigned: none

## Why this intake does **not** earn survivor
这条对象的优点很明确：它是 pairs / stat-arb 家族里一个非常干净、可复刻、适合当 control group 的 plain-vanilla baseline。

但按当前 policy，fresh intake 是否进入 survivor，看的不是“是否适合作为研究对照组”，而是“这条 raw alpha 本体今天是否仍值得占用前排跟进预算”。这次 digest 自带的最小 transfer check 已经足够回答这个问题，而且答案偏负面：

1. **当前 edge 只停留在 gross，不在 net。**
   - Portfolio `z_enter=1.0`：`gross_bps_per_bar ≈ +0.208`，但 `net_bps_per_bar ≈ -3.502`。
   - `cum_gross_pct ≈ +12.67%`，但 `cum_net_pct ≈ -86.70%`。
2. **把阈值抬高也没有形成一个明确可保留的 exact pocket。**
   - `z_enter=2.5` 时，`active_share_avg ≈ 9.7%`，但 `gross_bps_per_bar ≈ +0.071`、`net_bps_per_bar ≈ -0.512`，仍然成本后为负。
3. **当前 digest 没有给出一个单一、已经被证据支持的 re-scope。**
   - 文中提出的 `spread-exit / maker pocket / stability funnel` 都还是“下一步该怎么测”，不是这次 intake 已经成立的 exact alpha pocket。
   - 因此不能把 survivor 保留成模糊的“pairs baseline 也许换个 exit / maker / selection 就能活”。
4. **它更像方法学控制组，不像当前前排候选。**
   - 这条对象对 desk 有价值，但价值主要是“以后评估 fancy pairs 时的 baseline 对照”，不是“现在继续往前排推进一轮就很可能升 P2”。

## Decisive evidence pulled from artifact
来源：`reports/artifacts/quant_digests/pairs_longshort_story_20260326_1505/summary.json` 与 `threshold_sweep.json`

- 组合层（top-3 pairs, 15m, next-open -> same-bar-close, 6bps RT）
  - `gross_bps_per_bar = 0.2082`
  - `net_bps_per_bar = -3.5018`
  - `gross_sharpe_ann = 8.72`
  - `cum_net_pct = -86.70%`
- 阈值扫描
  - `z=1.5`: `net_bps_per_bar = -2.0743`
  - `z=2.0`: `net_bps_per_bar = -1.0877`
  - `z=2.5`: `net_bps_per_bar = -0.5117`

结论很干脆：**目前并不存在一个已被这轮证据直接支撑、能诚实写成 survivor 的 exact pocket。**

## Runtime result sentence
`plain-vanilla spread convergence long-short baseline` 首判收口为 `park`：当前 Binance Spot `15m` 只显示 gross convergence、成本后在 `z_enter=1.0~2.5` 全部为负，且 digest 尚未给出一个已被当前证据坐实的单一 maker / exit / selection pocket，因此它更适合作为 pairs 家族 control baseline 留在背景池，而不进入 survivor。
