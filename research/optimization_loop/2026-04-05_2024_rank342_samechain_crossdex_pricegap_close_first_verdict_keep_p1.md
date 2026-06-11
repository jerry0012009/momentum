# Rank 342 — same-chain cross-DEX price-gap close first verdict: keep_P1

- Time: 2026-04-05 20:24 UTC
- Target: `research/quant_digests/2026-04-05_1740_samechain-crossdex-pricegap-close-alpha.md`
- Slot before execution: `Fresh intake`
- Assigned Rank: `342`
- Verdict: `keep_P1`
- Layer transition: `fresh intake -> Surviving candidate`

## Why this changed system belief

本轮 first verdict 结论是：`same-chain cross-DEX price-gap close` 不是旧式 `CEX -> DEX` lead-lag / transfer-arb 的换壳命名，而是一条独立的 **same-chain / same-asset / executable net-gap close** raw alpha，已经具备进入 `P1` 的最小诚实研究壳。

一句话概括：

> 当同链同币对在多个 DEX 池之间出现短时可执行净价差，而且该价差在扣除双边池费、滑点、gas 与 MEV buffer 后仍为正，赌的是这条净价差向零闭合，而不是赌方向。

## Why it passes first-verdict threshold

### 1) Mispricing state 是清楚的，不是泛泛“有价差”
对象明确把 alpha state 压成：

- 同一条链
- 同一资产对
- 多个 DEX / 多个 pool
- 取 cheapest executable buy pool 与 richest executable sell pool
- 研究的是 **gross gap 扣摩擦后的 net executable gap**

这已经把 `mispricing state` 与常见的跨链价差、CEX/DEX lead-lag、单边趋势判断明确分开。

### 2) Execution lane 是清楚的，且比跨链版本更诚实
文档明确强调：

- 先做 `same-chain only`
- 不把跨链 bridge latency / inventory / async settlement 混进首轮壳
- 以双腿同链路由、分钟级 gap-close 为最小实验对象

这使它成为一条可以被 short-cycle desk 诚实验证的 onchain relative-value 壳，而不是靠复杂桥接/库存管理掩盖 alpha 本体。

### 3) Fee / gas / slippage realism 已写进 alpha 定义本身
对象不是停在 headline spread，而是显式要求净价差：

- buy pool fee
- sell pool fee
- buy/sell slippage
- gas bps
- MEV buffer

而且 repo/source 中已给出链级 gas 假设、最低 spread threshold、liquidity floor、trade size cap。也就是说，它不是“之后再考虑成本”，而是把成本现实直接嵌进 first-pass shell。

### 4) Gap-close clock 是短周期且可验证的
当前定义明确面向：

- `1m / 3m / 5m / 15m`
- 事件持续分钟数
- 闭合速度
- 以 same-chain event study 作为首轮实验

这满足 policy 要求的最小 clean-room / 可证伪路径：可先做 event study，再决定是否值得上完整策略回测。

## Why it is NOT just an old shell renamed

它**不是**旧式 `CEX -> DEX` 价差 carry / lead-lag 的简单改名，原因在于：

1. **venue family 不同**：这里研究的是 DEX vs DEX 同链多池，而不是 CEX 与链上的异步传导。
2. **clock 不同**：这里假设的是同链微观错位后的分钟级闭合，而不是跨 venue 的信息传导/库存修复。
3. **execution friction 结构不同**：核心摩擦来自池费、gas、滑点、MEV，而不是充值提币/transfer/结算等待。
4. **state definition 更原教旨**：对象定义的是 same-asset executable net gap，而不是 broader cross-venue dislocation narrative。

因此它可以被视为独立的 onchain relative-value raw alpha family member，而非旧对象 alias。

## Remaining uncertainty (why only keep_P1, not higher)

虽然 first verdict 通过，但当前还没有 admission-ready 证据，至少还缺：

- 哪些链/池费层/交易对的 `gross -> net` 保留率最高；
- `net_gap_bps > 0` 事件的持续性是否足以支持真实可成交；
- 蓝筹深池 vs 次级池 vs 事件窗口，哪里才是有效 pocket；
- MEV / block timing / quote staleness 是否会显著侵蚀纸面净价差。

所以本轮最诚实的位置是 `keep_P1`，而不是直接升 `P2`。

## Suggested single survivor follow-up

若下一轮要用 survivor 唯一一次 follow-up，最合适的唯一问题是：

> `same-chain executable net-gap` 在 low-gas chains（如 Base / Arbitrum）上，是否比 Ethereum 主网蓝筹池更可能留下 after-cost、minutes-scale 的真实 pocket？

也就是优先验证：

- low-gas chain
- same-chain only
- event-study first
- `gross -> net` 保留率与 close half-life

## Runtime sentence to write back

`Rank 342：same-chain cross-DEX price-gap close 已完成 first verdict；对象把 same-chain routing path、fee/gas/slippage realism 与 minutes-scale gap-close clock 压成了独立 onchain relative-value raw alpha 壳，因此进入 keep_P1，并占据 surviving candidate slot。`

## Ops note

- 中文邮件摘要已发送。
- 首页刷新已尝试执行 `scripts/publish_homepage_index.sh`，但当前 direct runtime 无可用 elevated/sudo 能力，脚本在发布到 `/var/www/momentum-report/index.html` 阶段超时；本地 `build_site_index.py` 可由该脚本触发，但本轮未完成最终站点落盘。
