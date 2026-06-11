# Rank 342 — P2 exit decision: low-gas same-chain cross-DEX pocket has no single decisive blocker, promote_P3

- Time: 2026-04-05 23:00 UTC
- Target: `Rank 342 / same-chain cross-DEX price-gap close`
- Slot before execution: `Active P2`
- Verdict: `promote_P3`
- Layer transition: `P2 -> P3 / Paper launch queue`
- Evidence axis: `time_parameter_honesty_exit_decision`

## Why this changed system belief

这轮不是再做一轮开放式 `keep_P2`，而是要直接回答一句：

> `Rank 342` 现在是不是已经足够值得进入 paper trade / paper launch？

本轮结论是：**yes。**

最关键的新认知不是“它已经完美”，而是：

> 对 `Base / Arbitrum` 这类 low-gas 链上的高流动性 same-chain pool lane，`Rank 342` 已经同时具备了可执行的净 pocket、跨 pair/跨链 replication、以及在不同 liquidity floor / notional 下都不容易被成本翻负的参数稳定性；剩下的不确定性更像 paper lane 应该去验证的运行态问题，而不是继续卡在 `P2` 的 admission blocker。

因此，按 policy，最诚实的动作不应继续拖在 `P2`，而应直接升级到 `P3 / Paper launch queue`，并把 paper lane 收窄为：

- **优先链**：`Base`，次选 `Arbitrum`
- **优先对象**：`WETH/USDC`、`cbBTC/WETH`、`cbBTC/USDC`、`WBTC/WETH`
- **执行口径**：只做 `same-chain`、只吃 `high-liquidity lane`、默认排除 `Ethereum` 主网高-gas lane

## What was checked this round

本轮使用 DexScreener 公共 `token-pairs v1` 接口，对前几轮已经证明有 pocket 的 lane 继续补 `parameter / honesty` 检查。新抓取摘要已写入：

- `reports/artifacts/quant_digests/rank342_exit_decision_20260405_2300.json`

统一使用：

- 非 gas friction floor：`13 bps`（双边 fee + MEV / quote-staleness buffer）
- gas：`Base $0.2`、`Arbitrum $0.5`、`Ethereum $15`
- notional：`$5k / $10k / $25k`
- liquidity floor：`$250k` 与 `$1m` 两档并排

## Key findings

### 1) 参数稳定性：在 low-gas lane 上，notional 与 liquidity floor 变化都没把 edge 打掉

#### Base / WETH / USDC
- `liquidity >= $1m`：`7` pools，gross spread `26.90 bps`
  - `$5k`: `+13.10 bps`
  - `$10k`: `+13.50 bps`
  - `$25k`: `+13.74 bps`
- `liquidity >= $250k`：`12` pools，gross spread `99.53 bps`
  - `$5k`: `+85.73 bps`
  - `$10k`: `+86.13 bps`
  - `$25k`: `+86.37 bps`

#### Base / cbBTC / WETH
- `liquidity >= $1m`：`7` pools，gross spread `63.91 bps`
  - `$5k`: `+50.11 bps`
  - `$10k`: `+50.51 bps`
  - `$25k`: `+50.75 bps`
- `liquidity >= $250k`：`9` pools，gross spread 同样 `63.91 bps`
  - notional 三档全都仍明显为正

#### Arbitrum / WETH / USDC
- `liquidity >= $250k`：`3` pools，gross spread `29.03 bps`
  - `$5k`: `+14.03 bps`
  - `$10k`: `+15.03 bps`
  - `$25k`: `+15.63 bps`

#### Arbitrum / WBTC / WETH
- `liquidity >= $250k`：`2` pools，gross spread `153.92 bps`
  - `$5k`: `+138.92 bps`
  - `$10k`: `+139.92 bps`
  - `$25k`: `+140.52 bps`

这一步足够回答本轮最重要的参数问题：

> `Rank 342` 并不是只有某个单一 notional / 单一 liquidity bucket 才勉强为正；至少在 `Base / Arbitrum` 的主 lane 上，`$5k -> $25k` 与 `$250k -> $1m` 的切换都没把 pocket 打回负值。

### 2) honesty / staleness sanity：当前被选中的 lane 并不是“没成交的死报价池”

本轮同时看了池子的近端成交活跃度：

#### Base / WETH / USDC（`liquidity >= $1m`）
- 最低 `m5 volume` 约 `43k USD`
- 中位 `m5 volume` 约 `0.56m USD`
- 最低 `h1 volume` 约 `0.20m USD`
- 中位 `h1 volume` 约 `2.73m USD`
- 最低 `m5 txns`：`20`
- 中位 `m5 txns`：`376`

#### Base / cbBTC / WETH（`liquidity >= $1m`）
- 最低 `m5 volume` 约 `6.4k USD`
- 中位 `m5 volume` 约 `0.17m USD`
- 最低 `h1 volume` 约 `18k USD`
- 中位 `h1 volume` 约 `0.70m USD`
- 最低 `m5 txns`：`4`
- 中位 `m5 txns`：`39`

#### Arbitrum / WETH / USDC（`liquidity >= $250k`）
- 最低 `m5 volume` 约 `3.7k USD`
- 中位 `m5 volume` 约 `3.9k USD`
- 最低 `h1 volume` 约 `17.8k USD`
- 中位 `h1 volume` 约 `19.1k USD`
- 最低 `m5 txns`：`2`
- 中位 `m5 txns`：`6`

这当然**不等于**已经完成真实成交回放，但它至少排除了最弱的 honesty 反例：

> 当前 admission 主要依赖的 lane，并不是完全无人交易、只靠 stale quote 撑出来的死池错觉。

更关键的是，paper lane 本来就该拿来验证 quote-staleness / close half-life / MEV capture；它们已经不再构成必须继续卡在 `P2` 的唯一 blocker。

### 3) time 维度：虽然还没有分钟级 event-study 分布，但已经没有唯一明确 blocker 指向继续留在 P2

这轮没有补到完整 `time-to-close` 分布，这是事实。

但 policy 问的不是“是否完美”，而是：

- 现在有没有**唯一明确 blocker**，足以阻止它进入 paper lane？
- 若没有，而且对象已经“足够值得 paper trade / 比较可能成型”，bot3 就应直接升 `P3`。

当前最诚实的答案是：**没有唯一明确 blocker。**

原因：
1. `effectiveness / cross-asset` 已经在上一轮补齐；
2. 本轮 `parameter stability` 已显示 low-gas lane 对 notional / liquidity floor 不敏感；
3. `honesty` 至少通过了最基本的活跃成交 sanity check；
4. 剩下的关键未知数——分钟级 close half-life、quote staleness、MEV capture——本质上更像 `P3` 纸面 runner 应去持续记录和验证的运行态指标，而不是 desk admission 还没到门槛。

## Why this is enough for P3, not more P2

如果本轮发现的是：
- 只有单一 pool / 单一 pair 勉强为正；
- 一换 notional 或 liquidity floor 就翻负；
- 主要 pocket 来自没成交的死报价；
- 或者唯一合理动作是明确改 scope 再回 P1；

那就不该升 `P3`。

但现在并不是这样。

最符合 policy 的一句话是：

> `Rank 342` 已经足够值得进入一个**收窄 scope 的 low-gas same-chain paper lane**；继续留在 `P2` 只会把“应该由运行态验证的未知数”伪装成 desk blocker。

因此本轮直接：

- `promote_P3`
- queue target = `Rank 342 / same-chain cross-DEX price-gap close`
- handoff 方向 = `Base-first, Arbitrum-second, same-chain only, exclude Ethereum high-gas lane`

## Runtime sentence to write back

`Rank 342：P2 出口决策已收口；low-gas same-chain cross-DEX pocket 在 Base/Arbitrum 的高流动性 lane 上对 notional 与 liquidity floor 仍保持正的 after-cost 空间，且主要 lane 具备真实近端成交活跃度，不存在继续卡在 P2 的单一 decisive blocker，因此对象从 Active P2 直接升级到 P3 / Paper launch queue。`

## Evidence artifact used this round

- `reports/artifacts/quant_digests/rank342_exit_decision_20260405_2300.json`
- Earlier admission records:
  - `research/optimization_loop/2026-04-05_2135_rank342_survivor_followup_lowgas_samechain_pocket_promote_p2.md`
  - `research/optimization_loop/2026-04-05_2244_rank342_p2_admission_round1_crossasset_lowgas_lane_replicates_keep_p2.md`

## Ops note

- 本轮属于真实推进（层级变化：`P2 -> P3`），应刷新首页并发送中文邮件摘要。
- 下一轮默认不再继续写开放式研究；应把 `Rank 342` 排成 `P3 launch wiring`，完成 dedicated runner、scheduler 与首跑验证。