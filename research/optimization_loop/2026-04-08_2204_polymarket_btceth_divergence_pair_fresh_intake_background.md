# 2026-04-08 22:04 UTC — Polymarket BTC/ETH divergence pair fresh intake 首判

## 本轮执行小点
- target: `research/quant_digests/2026-04-08_1225_polymarket-btceth-divergence-pairs-alpha.md`
- action: 判断 `BTC/ETH 5m divergence-pair discount × hard-expiry reprice` 是否足够构成独立 prediction-market relative-value raw alpha，而不是被既有 prediction-market static mispricing / complementary-outcome / binary arb family 吸收

## 读取与对照
- 已读当前 digest：`research/quant_digests/2026-04-08_1225_polymarket-btceth-divergence-pairs-alpha.md`
- 已对照项目内现有 prediction-market / relative-value 材料（含既有 Polymarket complementary-outcome / lock-in arb 家族记录）

## 结论
`BTC/ETH divergence pair discount × hard-expiry reprice` 目前仍更像把既有 prediction-market pair-sum / hard-expiry mispricing 家族改写成 `BTC-vs-ETH current leader` 的方向选择壳：repo 给出的主要新增信息是 entry 价带、pair 组合价带和到期结算持有规则，但独立 alpha 主语仍建立在同平台同到期二元合约的静态折价回补，而不是一个已被证明独立于既有 binary/complementary mispricing family 的新机制，因此 fresh intake 首判收口为 `background / P0`。

## 为什么不是 keep_P1
1. **独立性不够**
   - 当前 repo 的核心可执行骨架，还是“同一到期窗里买入折价的二元 pair，等硬结算重定价”。
   - 与项目里已经 intake 过的 prediction-market mispricing 家族相比，真正新增的主要是：
     - 交易对象从 `互补 outcome pair` 换成 `BTC/ETH divergence pair`
     - 用 `BTC vs ETH 当前强弱` 决定买哪一侧
   - 这更像 existing family 的对象替换 + selector，而不是独立 raw alpha 新家族。

2. **证据仍主要来自 repo 规则描述，不是新机制证明**
   - digest 提供的是源码规则、价带、风控和结算方式；
   - 但还没有把这条线和既有 `same-platform binary mispricing / complementary-outcome capture / hard-expiry lock-in` 做出干净边界。
   - 也就是说，目前最强证据是“这个 bot 会这样做”，不是“这背后是一个独立且可迁移的新 alpha 机制”。

3. **honesty / execution realism 不是唯一 blocker，但也没强到足以救独立性**
   - 盘口容量、ask sweep、partial fill、resolution delay 的确是现实约束；
   - 但这轮不把它判死，主要原因不是 execution fatal，而是**独立性主语本身没立住**。
   - 换句话说，即使 execution 过关，它现在也更像 prediction-market mispricing 家族的分支实现，而不是应当前排保留的独立 survivor。

## 对 runtime 的影响
- 该对象不进入 survivor slot
- 不分配 Rank
- Fresh intake 直接收口为 `background / P0`

## 一句话 result
Polymarket `BTC/ETH 5m divergence pair discount` 目前仍是既有 prediction-market hard-expiry / pair-mispricing 家族的方向选择变体，而非足以单列前排的独立 raw alpha，因此 fresh intake 首判直接收口为 `background / P0`。
