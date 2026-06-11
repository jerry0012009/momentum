# 2026-04-03 06:30 UTC — multivenue coint × ML filter × venue-tier risk stack fresh intake first verdict = background/P0

## 本轮执行对象
- target: `research/quant_digests/2026-04-03_0504_multivenue-coint-ml-filter-pairs-alpha.md`
- action: 作为 fresh intake，判断这条 `cointegration spread raw alpha × ML entry filter × venue-tier risk stack` 是否相对现有 pairs / stat-arb 家族拥有足够独立的新主语，而不是把旧 pairs 母板做成更复杂的工程包装。

## 读取与对照
- 当前 digest 明确主张：base alpha 是 `cointegrated spread mean reversion`，ML 只作 entry / exit timing enhancement，外加 venue-tier / Kelly / sector-correlation cap / cost shell。
- 已有家族对照：
  - `2026-03-26_1505_plain-pairs-longshort-vs-longonly.md` 已把 `plain-vanilla cointegration pairs` 固定成 pairs 家族控制组；关键结论是短周期里真正的第一性约束是换手与成本，而不是“再多一个 pairs 壳”。
  - `2026-04-01_2105_dualtest-coint-zscore-pairs-alpha.md` 已把更具体的新主语落成 `ADF + Johansen 双检验 × rolling beta spread z-score fade`，也就是“用更严 pair admission 减少假协整”的独立增量。
  - `2026-04-01_1426_lowfreq-liquidity-proxy-gate-overlay.md` 已把 venue / liquidity-aware gating 明确沉淀为可服务 pairs / spread MR 的共享 overlay。

## 这次 first verdict 真正回答的问题
要回答的不是“这 repo 是否完整”，而是：

> 它相对现有 pairs / stat-arb 家族新增的主语，是否足够独立到值得单列推进？

结论：**不够。先放回 background/P0。**

## 为什么不够独立
### 1) raw alpha 本体没有新到能单列
它的核心仍然是最经典的 `cointegration spread mean reversion`：
- pair selection
- spread z-score 入场
- 回归均衡退出
- stop / max holding / cost shell

这和现有 pairs 家族控制组相比，并没有新增一个新的、可单独验真的 alpha 主语；变化主要落在：
- ML timing filter
- venue-tier / portfolio / risk stack
- 工程与研究框架更全

这些东西当然有价值，但它们更像 **已有 pairs 母板上的 filter/overlay/production shell**，而不是一条新的 raw alpha 线。

### 2) “ML 只作 filter” 这个定位是诚实的，但正因为诚实，更说明它不是新 intake 主体
digest 自己已经把角色边界说得很清楚：
- raw alpha = spread mean reversion
- ML = timing enhancement

这意味着它对系统认知的新增，不是“发现了一条新的 pairs alpha”，而是“给已有 pairs alpha 配了一层相对合理的 ML 过滤器”。

这类增量更适合作为后续某条已入前排的 pairs/P2 admission 的增强对照，而不是今天单列 fresh intake 占一个 survivor 槽位。

### 3) venue-tier risk stack 也更像共享交易壳，不像独立主题
repo 把 venue tier、Kelly、sector cap、cross-pair correlation cap、cost/slippage 写得完整，这对以后落地很有帮助；但这些仍主要属于：
- 风控壳
- 组合壳
- venue-aware implementation壳

而不是一个新的、和 `plain pairs` 或 `dual-test admission pairs` 平级的 raw alpha identity。

### 4) 当前 pairs 家族已经有更干净的对照层次；这个对象若进前排，只会让层次变混
目前家族层次已经相对清楚：
1. `plain-vanilla pairs baseline`
2. `dual-test admission shell`（降低假 pair）
3. 共享 `liquidity / venue-aware overlay`

本对象把 1/2/3 再打包成一个更完整 repo。它适合当 **工程集成参考模板**，但不适合当新的独立研究对象。若现在给它 `keep_P1`，系统会把“完整工程包装”误读成“新 alpha 主语”。

## 诚实收口
因此本轮 first verdict 直接写成：

**这条 `cointegration spread raw alpha × ML entry filter × venue-tier risk stack` 更像是对现有 pairs 母板的工程集成与 filter/overlay 封装，而不是独立的新 raw alpha 主语；在已有 `plain baseline + dual-test admission + liquidity overlay` 的前提下，不值得再单列占用 survivor/front-slot，故 fresh intake first verdict = `background/P0`。**

## 对 runtime 的影响
- 不分配 Rank：因为没有达到 `keep_P1`。
- 不进入 `Surviving candidate slot`。
- 作为 background 参考保留：未来若某条已进入 P2 的 pairs 候选需要补 `ML timing filter` 或 `venue-tier risk shell`，可回查本 digest 作为共享组件来源，而不是 reopen 为单独主线对象。

## 一句话结果（回填 state 用）
`multivenue coint × ML filter × venue-tier risk stack` 的 fresh intake first verdict = `background/P0`：它补的是 pairs 母板的工程集成与 filter/overlay 完整度，而不是独立的新 raw alpha 主语；在已有 plain baseline、dual-test admission shell 与 liquidity overlay 的前提下，不值得单列推进。
