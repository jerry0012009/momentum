# Rank 342 — survivor follow-up: low-gas same-chain executable pocket is more credible than Ethereum deep-pool lane, promote_P2

- Time: 2026-04-05 21:35 UTC
- Target: `Rank 342 / same-chain cross-DEX price-gap close`
- Slot before execution: `Surviving candidate`
- Verdict: `promote_P2`
- Layer transition: `Surviving candidate -> Active P2`

## Why this changed system belief

本轮 survivor 唯一一次 follow-up 的收口结论是：`same-chain executable net-gap` 并没有被证明只停留在概念层；至少在 **low-gas chain** 这条执行通道上，它已经留下了足够进入 `P2 admission` 的最小 pocket 证据，因此对象应从 `P1 survivor` 直接升级到 `Active P2`，而不是被打回背景池。

一句话概括：

> `Rank 342` 的真正可交易壳不在 Ethereum 主网蓝筹深池，而更像 **Base/低 gas 链上的 same-chain pool dislocation close**：gross spread 并未比主网大很多，但 gas 负担低一个数量级，使 `gross -> net retention` 明显更诚实，已足以支持进入 P2 admission。

## What was checked this round

### 1) Ethereum vs Base 的同链多池 gross spread 快照

用 DexScreener 公共 `token-pairs v1` 接口，对 `WETH/USDC` 做最小 same-chain 多池快照（流动性过滤 `>= $1m`）：

- **Ethereum**：`7` 个 liquid pools，最便宜池到最贵池的 gross spread 约 **28.91 bps**
- **Base**：`7` 个 liquid pools，最便宜池到最贵池的 gross spread 约 **26.62 bps**
- **Arbitrum**：在当前严格过滤口径下仅抓到 `1` 个符合条件池，样本不足，不作为本轮主判断依据

这一步的重要性不在于宣称“Base gross 一定更大”，而在于：

> **low-gas chain 不需要 gross spread 明显大于 Ethereum，只要 gross 相近、而 gas 明显更低，net pocket 就会更可能存活。**

### 2) 用对象自身 source shell 的 friction 假设做最小 net-floor sanity check

沿用对象 source/repo 在 digest 里已明确写出的链级 gas 假设：

- Ethereum：`$15`
- Base：`$0.2`

再加一个保守但不过分的非 gas friction floor：

- 双边 pool fee 合计：`10 bps`（两腿各 `5 bps`）
- MEV / quote-staleness buffer：`3 bps`
- 合计非 gas floor：`13 bps`

对本轮快照做 notional sanity check：

#### Ethereum
- `$5k`：`28.91 - 13 - 30.00 = -14.09 bps`
- `$10k`：`28.91 - 13 - 15.00 = +0.91 bps`
- `$25k`：`28.91 - 13 - 6.00 = +9.91 bps`

#### Base
- `$5k`：`26.62 - 13 - 0.40 = +13.22 bps`
- `$10k`：`26.62 - 13 - 0.20 = +13.42 bps`
- `$25k`：`26.62 - 13 - 0.08 = +13.54 bps`

## Why this is enough to promote, not enough to launch

### Enough for P2

这轮 follow-up 只需要回答一件事：

> **low-gas same-chain lane 是否已经留下 “after-cost pocket + executable lane” 的最小证据？**

答案是 **yes**，因为：

1. **gross spread 并不只存在于 Ethereum**，Base 上同样能看到同量级的多池价差；
2. **gas burden 决定性地改变了 `gross -> net retention`**：在 `$5k~$10k` 这种 short-cycle first-pass notional 上，Ethereum 主网几乎被 gas 吞光，而 Base 仍保留双位数 bps 的净空间；
3. 这使对象从“概念上的 onchain relative-value”变成了“已经有具体链/具体 execution lane 的 admission-ready 候选”。

### Not enough for P3

但这还远远不等于 paper-launch-ready，因为当前还没完成完整 admission：

- 还没做系统化的 **cross-asset / cross-pair** 验证；
- 还没做 **time stability**（不同日/不同事件窗口的 pocket 持续性）;
- 还没做 **parameter stability**（不同 notional / threshold / liquidity floor）;
- 还没做足够诚实的 **execution realism**（真实池费层、深度曲线、MEV/quote staleness、close half-life）。

因此最诚实的位置不是 `P3`，而是：

> **把 Rank 342 升到 `Active P2`，接下来围绕 low-gas same-chain lane 做 admission。**

## Why it should NOT be dropped to background

若本轮证据显示：
- 只有 headline spread，
- low-gas chain 上也留不下净 pocket，
- 或只能在 Ethereum 大额 notional 才勉强为正，

那按 policy 就该直接 `drop_to_background / P0`。

但事实不是这样。

本轮最关键的新认知是：

> **对象的 pocket 并非“所有地方都薄”，而是明显呈现链依赖：Ethereum deep-pool lane 更像被 gas 吃掉的伪机会，Base 这类 low-gas 链才是更值得 admission 的主战场。**

这已经足够改变层级判断，所以不能按“仍只是概念叙事”处理。

## Runtime sentence to write back

`Rank 342：survivor follow-up 已收口；same-chain cross-DEX net-gap 的真实 pocket 更像出现在 Base 等 low-gas 链，而非 Ethereum 主网蓝筹深池，gross spread 相近但 gas 负担显著更低，使 after-cost retention 明显改善，因此对象从 surviving candidate 升级为 Active P2。`

## Evidence used

- Existing first-verdict digest/log:
  - `research/quant_digests/2026-04-05_1740_samechain-crossdex-pricegap-close-alpha.md`
  - `research/optimization_loop/2026-04-05_2024_rank342_samechain_crossdex_pricegap_close_first_verdict_keep_p1.md`
- Existing artifact:
  - `reports/artifacts/quant_digests/cross_dex_samechain_20260405/summary.json`
- New live sanity snapshot (same DexScreener public endpoint, 2026-04-05 21:35 UTC):
  - Ethereum `WETH/USDC`: liquid pools `7`, gross spread `28.91 bps`
  - Base `WETH/USDC`: liquid pools `7`, gross spread `26.62 bps`
  - Arbitrum `WETH/USDC`: only `1` pool after strict liquidity filter; insufficient for this round

## Ops note

- 本轮属于真实推进（层级变化：`P1 -> P2`），应刷新首页并发送中文邮件摘要。
