# Rank 337 — bull-third no-short trend sleeve first verdict: keep P1

- Time: 2026-04-05 05:46 UTC
- Target: `research/quant_digests/2026-04-04_2223_tsmom-bull-third-noshort-alpha.md`
- Action: fresh intake first verdict
- Verdict: `keep_P1`
- Assigned Rank: `337`

## Why this changes system state
`bull-third no-short trend sleeve` 不只是已有 breakout / regime gate / market-trend 题材换壳；它给出了一个可独立执行的 `market TSMOM` 原始壳：用市场组合回看收益的时间序列分位定义 `bull state`，仅在上三分之一时做多，落入下三分之一时默认空仓而非机械开空。这个 `no-short asymmetry` 不是措辞差异，而是该对象最核心的可迁移 edge 主张。

## First-verdict judgment
结论先落在 `keep_P1`，不直接升 `P2`。

原因：
1. **state trigger 清楚**：`bull-state definition` 不是模糊“涨了就做多”，而是 market basket rolling return 的历史 percentile rank 触发。
2. **asymmetry rationale 清楚**：论文与 digest 都明确指出 crypto TSMOM 的利润主要集中在 bullish state 的 long leg，bad-state short 默认不值钱，`flat > auto-short` 是对象的结构性主张。
3. **execution shell 清楚**：已有最小 short-cycle transfer 壳——liquid-major market basket、`15m` 主时钟、`L/H/N` 网格、`>=0.67` 开多、`<=0.33` 只 flat、不做空、成本三档回放。
4. **cost-aware transfer path 清楚**：已明确要求在 `5/10/15 bps` 全包成本下验证，并把 `always-on long` 与 `symmetric long-short` 作为对照书，而不是只保留叙事。

## Why not higher than P1 yet
还不能直接升 `P2`，因为当前仍停留在 paper-to-desk transfer 设计层，尚未完成最小 clean-room 验证，特别是：
- `market basket shell` 具体定义（等权 / beta-adjusted / top-N liquid majors）还未压成唯一 admission 对象；
- `bull-third` percentile trigger 在短周期下是否仍保留 edge 还未做最小实测；
- `flat-vs-short veto` 虽然叙事很强，但还缺一轮最小 liquid-major 读数来证明这不是日频论文参数迁移后的幻觉。

## Survivor follow-up that remains legal
作为唯一一次 survivor follow-up，下一步只值得做一件便宜且决定性的检查：
- 把对象压成单一 `liquid-major market basket` clean-room 规范，验证 `bull-third long-only` 相对 `always-on long` 与 `symmetric long-short` 是否仍保留 `flat-not-short` 的 admission 级优势。

## One-line result
`Rank 337`：`bull-third no-short` 市场 TSMOM 壳已形成 distinct 的 long-only market-trend raw alpha，fresh intake first verdict 通过，进入 `P1 / Surviving candidate`。
