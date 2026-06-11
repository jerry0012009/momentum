# Rank 342 — P2 admission round 1: low-gas same-chain lane replicates across Base + Arbitrum and beyond single WETH/USDC, keep_P2 with stronger P3 tilt

- Time: 2026-04-05 22:44 UTC
- Target: `Rank 342 / same-chain cross-DEX price-gap close`
- Slot before execution: `Active P2`
- Verdict: `keep_P2`
- Layer transition: `P2 -> P2`
- Evidence axis: `effectiveness_cross_asset_cross_chain_after_cost_replication`

## Why this changed system belief

本轮 admission 首轮要回答的不是“这条线是不是完美”，而是更关键的一句：

> `Rank 342` 在 low-gas same-chain lane 上，是否已经不再只是 `Base / WETH-USDC` 单一特例，而是真有跨链、跨 pair 的 after-cost replication？

本轮结论是：**yes，已经能看到不止一个 liquid pair / chain 的可复制 pocket，因此最诚实的状态是 `keep_P2`，而且离 `P3` 更近了。**

一句话概括：

> `Rank 342` 的 after-cost pocket 不只存在于 `Base WETH/USDC`；在 `Base cbBTC/WETH`、`Base cbBTC/USDC`、`Arbitrum WETH/USDC` 甚至 `Arbitrum WBTC/WETH` 这些 same-chain 多池样本里，也能看到净价差在保守 friction floor 后仍明显为正，因此对象已通过 admission 的 `effectiveness / cross-asset` 首轮，不再像单一 pool 特例。

## What was checked

本轮继续使用 DexScreener 公共 `token-pairs v1` 接口，但不再只看单一 `Base WETH/USDC`：

- 链：`Base`、`Arbitrum`（并保留 `Ethereum` 作为高-gas 对照）
- 对象：`WETH`、`cbBTC`、`WBTC`
- 组法：同链、同 base token、同 quote token，多池比较 cheapest executable pool vs richest executable pool
- 过滤：优先看 `liquidity >= $1m`；若样本不足，再退到 `>= $250k`
- 成本 sanity floor：
  - 非 gas friction floor = `13 bps`（双边 pool fee + MEV / quote-staleness 缓冲）
  - gas 假设沿用对象 source shell：`Ethereum $15`、`Arbitrum $0.5`、`Base $0.2`
  - 名义额：`$5k / $10k / $25k`

## Key findings

### 1) Base WETH/USDC 不是孤例

在 `Base / WETH / USDC`、`liquidity >= $1m` 下：

- liquid pools：`7`
- gross spread：`29.78 bps`
- net spread after floor：
  - `$5k`: `+16.38 bps`
  - `$10k`: `+16.58 bps`
  - `$25k`: `+16.70 bps`

这继续确认了上一轮 survivor follow-up 的核心判断：low-gas 链上，同链多池的 `gross -> net retention` 确实能活下来。

### 2) Base 上不仅 ETH，cbBTC 相关 pair 也存活

`Base / cbBTC / WETH`、`liquidity >= $1m`：

- liquid pools：`7`
- gross spread：`51.00 bps`
- net spread after floor：
  - `$5k`: `+37.60 bps`
  - `$10k`: `+37.80 bps`
  - `$25k`: `+37.92 bps`

`Base / cbBTC / USDC`、`liquidity >= $1m`：

- liquid pools：`9`
- gross spread：`30.92 bps`
- net spread after floor：
  - `$5k`: `+17.52 bps`
  - `$10k`: `+17.72 bps`
  - `$25k`: `+17.84 bps`

这一步很关键，因为它把对象从“也许只在 `WETH/USDC` 上成立”推进到“至少在另一类高流动性风险资产（BTC beta）上也能留下净 pocket”。

### 3) Arbitrum 也能看到 pocket，只是 liquidity bucket 更薄

`Arbitrum / WETH / USDC`、`liquidity >= $250k`：

- liquid pools：`3`
- gross spread：`20.86 bps`
- net spread after floor：
  - `$5k`: `+6.86 bps`
  - `$10k`: `+7.36 bps`
  - `$25k`: `+7.66 bps`

`Arbitrum / WBTC / WETH`、`liquidity >= $250k`：

- liquid pools：`2`
- gross spread：`94.92 bps`
- net spread after floor：
  - `$5k`: `+80.92 bps`
  - `$10k`: `+81.42 bps`
  - `$25k`: `+81.72 bps`

这说明 replication 不只停留在 Base；Arbitrum 也存在 same-chain 多池 pocket，只是当前能抓到的 liquid bucket 比 Base 薄，样本层级略弱。

### 4) 高-gas Ethereum 更像“要么大 spread，要么高 notional”

作为对照，本轮 Ethereum 的 `WETH/USDC` 与 `WETH/USDT` 也抓到了较大 gross spread；但在我们使用的固定 floor 下：

- `Ethereum / WETH / USDC`：
  - `$5k` 仅 `+6.02 bps`
  - `$10k` `+21.02 bps`
- `Ethereum / WETH / DAI`：
  - `$5k` `-20.20 bps`
  - `$10k` `-5.20 bps`
  - `$25k` 才转正

这进一步强化了 admission 方向：

> 真正更可信的 paper lane 仍然更像 `low-gas chain first`，而不是默认把 Ethereum 主网蓝筹深池当成首发战场。

## Why this is enough for keep_P2, but not yet enough for P3

### Enough to keep P2 and strengthen the P3 lean

本轮已经把 admission 的前两块补得明显更实：

1. **effectiveness**：不止一个 pair / chain 出现正的 after-cost pocket；
2. **cross-asset / cross-chain**：不只 `Base WETH/USDC`，`Base cbBTC/*` 与 `Arbitrum` 相关样本也支持 same-chain dislocation close 不是单一特例；
3. **fee tier / liquidity bucket**：对象并非只能活在单一深池；它既能在 `>= $1m` 的 Base 深池组看到，也能在 `Arbitrum >= $250k` 的较薄 bucket 里留下 pocket。

因此，按 policy，本轮不能把它写成“只剩单一 WETH/USDC 特例”然后打回背景池；最诚实的更新应是：

> `Rank 342` 已通过 admission 首轮的 `effectiveness / cross-asset` 检查，保持 `P2`，且 `P3` 倾向增强。

### Not enough for direct P3 yet

但它还没到可以直接升 `P3` 的程度，因为本轮没有回答：

- `time stability`：这些 pocket 是持续存在、事件驱动存在，还是高度偶发？close half-life 是否稳定在可执行分钟级？
- `parameter stability`：不同 notional、threshold、gas buffer、liquidity floor 下，edge 是否仍稳？
- `honesty / execution realism`：quote staleness、MEV capture、真实深度曲线、两腿同步成交风险，会不会把纸面净 pocket 显著吃掉？

所以本轮最诚实的结果是 `keep_P2`，而不是越级直接 `promote_P3`。

## Runtime sentence to write back

`Rank 342：P2 admission 首轮已证明 low-gas same-chain pocket 不只存在于 Base/WETH-USDC；Base 的 cbBTC/WETH、cbBTC/USDC 与 Arbitrum 的 WETH/USDC、WBTC/WETH 也留下了 after-cost replication，因此对象通过 effectiveness/cross-asset 首轮检查，保持 P2 且 P3 倾向增强。`

## Evidence snapshot used this round

- DexScreener public API, queried at `2026-04-05 22:44 UTC`
- Representative groups:
  - `Base / WETH / USDC` (`7` pools, `>= $1m`, gross `29.78 bps`)
  - `Base / cbBTC / WETH` (`7` pools, `>= $1m`, gross `51.00 bps`)
  - `Base / cbBTC / USDC` (`9` pools, `>= $1m`, gross `30.92 bps`)
  - `Arbitrum / WETH / USDC` (`3` pools, `>= $250k`, gross `20.86 bps`)
  - `Arbitrum / WBTC / WETH` (`2` pools, `>= $250k`, gross `94.92 bps`)
  - `Ethereum / WETH / USDC` / `USDT` / `DAI` as high-gas contrast

## Ops note

- 本轮属于真实推进（新的 admission 结论），应刷新首页并发送中文邮件摘要。
- 下一轮若继续做 `Rank 342`，必须转到 `time / parameter / honesty`，不能再重复同一 `effectiveness / cross-asset` 维度。