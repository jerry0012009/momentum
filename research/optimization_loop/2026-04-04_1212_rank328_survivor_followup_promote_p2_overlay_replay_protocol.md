# bot3 optimization loop — Rank 328 survivor follow-up promote to P2

- Time: 2026-04-04 12:12 UTC
- Target: `Rank 328 / water-filling leverage equalization × factor-adjusted deleveraging shared risk overlay`
- Action: the one allowed survivor follow-up, answering whether this overlay already converges into an executable desk replay / admission shell
- Verdict: `promote_P2`

## Why this follow-up clears the survivor exit
这次 follow-up 要回答的不是“论文机制是不是有意思”，而是它有没有收敛成我们桌面上真的能跑的 **admission experiment shell**。结论是：**有，而且已经够进入 `P2`。**

### 1) replay protocol 已经不是空话，和现有 runtime 能对上
Digest 里要求的最小 replay 输入是：
- `notional`
- `equity / allocated capital`
- `gross leverage`
- `beta to BTC / ETH / market factor`
- `expected edge`

这套状态量并不是凭空想象。当前 desk 的 paper / shadow runtime 已经有现成状态簿可挂：
- `reports/artifacts/paper_rank154_crypto_stat_arb_runner/rank154_paper_state.json` 已显式记录 `current_equity`、逐 symbol `positions`、`quantity`、`weight`；
- `reports/artifacts/rank32b_shadow_global_winner/paper_open_positions.json` 已显式记录 open positions 的 `order_notional_usdt`、`entry/mark price`、`hold_minutes`、`timeout_at`、逐分钟 mark 状态；
- 多个已接线 paper runner（如 `rank229_state.json`）已证明 repo 里存在稳定的 state / ledger / status artifact 约定。

也就是说，这条 overlay 虽然不是 raw alpha，但它要求的 replay 载体——**sleeve 级状态簿**——在我们现有运行态里已经真实存在。缺的不是“有没有地方挂”，而只是把多 sleeve 状态统一抽成 overlay replay board。

### 2) gross water-fill vs factor-adjusted water-fill 已经形成明确的 desk experiment
这条对象现在不再只是“优化理论看起来不错”，而是已经收敛成清楚的 admission 对照组：
1. `pro-rata deleveraging`
2. `exchange-style queue proxy`
3. `gross leverage water-filling`
4. `factor-adjusted leverage water-filling`

这 4 组比较足以回答我们最关心的问题：
- 是否真的降低 tail shortfall；
- 是否只是把 forced-close turnover 转嫁到别处；
- 是否比 gross leverage 版本更少误砍 hedge sleeves。

这已经是标准的 **P2 admission framing**，而不是停留在 P1 的“值得以后看看”。

### 3) admission 指标已收敛成最小可裁决出口
之前 first verdict 的保留点，是这些指标还只停留在概念层：
- `tail shortfall`
- `forced-close turnover`
- `hedge false-positive cuts`

但 survivor follow-up 后，这三项已经足以构成最小 admission 出口，因为：
- 它们都对应 overlay 的真实职责，而不是伪装成方向收益；
- 它们都能在现有 paper / shadow ledger 上被定义成 reader-facing replay 指标；
- 它们共同回答“值不值得进 paper risk stack”，而不是要求先做完整 production governor。

换句话说，这条对象离 production 还远，但离 **P2 admission** 已经不远。

## Why it is P2, not P3
它还不该直接进 `P3 / Paper launch queue`，因为现在有的只是 **admission 级 replay protocol**，还没有：
- 统一的 multi-sleeve overlay replay runner；
- 已完成的 stress-window replay 结果；
- 明确通过阈值后的 dedicated paper governor wiring。

所以最准确的位置不是继续留在 `P1`，也不是越级进 `P3`，而是：

> **进入 `Active P2`，把它当成一条共享 risk overlay admission 对象，下一步直接检验 replay honesty / metric passability / desk impact。**

## Runtime conclusion
`Rank 328` 的唯一 survivor follow-up 已诚实收口：这条 `water-filling leverage equalization × factor-adjusted deleveraging` 虽然不是独立 raw alpha，但它已经不再只是规范性叙事——当前 repo 里已有可挂接的 paper/shadow state artifacts，且 `desk replay protocol + overlay state variables + admission metrics` 已收敛成可执行实验壳；因此本轮把 `Rank 328` 从 `P1 survivor` 正式升到 `Active P2`，下一步应直接做 overlay admission，而不是继续停在 survivor。