# Rank 271 / stablecoin discount → peer-parity reversion / fresh intake keep_P1

- 时间：2026-03-31 18:52 UTC
- 执行轮次：bot3 13m auto
- 对象：`research/quant_digests/2026-03-31_1617_stablecoin-discount-parity-reversion-alpha.md`
- 结论：`keep_P1`
- 正式 Rank：`271`

## 本轮只回答的问题
这条对象是否已经形成一条可审计的 stablecoin relative-value raw alpha，而不是把机制论文/监管叙事/已有 overlay 误当成前排策略。

## 最小核对
我只做了 intake 所需的最小交叉核对：
1. 该 digest 已明确把主体收口为 `secondary-market discount → peer-parity reversion`，不是“stablecoin 很重要”的泛解释；
2. 项目中已存在相邻但不相同的素材：
   - `2026-03-29_1458_usdt-depeg-jump-risk-shared-overlay.md` 是 **共享风险 overlay**，不是 raw alpha；
   - `2026-03-25_1234_fdusdusdc-zero-fee-grid-peg-reversion.md` 与 `2026-03-24_1318_stablecoin-ata-asymmetric-threshold-meanreversion.md` 更接近 **peg-near stablecoin pair MR**，但这次对象强调的是 **discount event / peer basket / cross-quote 映射**，尤其包含 `same-underlier multi-quote spread` 这一层；
3. 当前 digest 已给出可审计的策略骨架：anchor 定义、entry/exit、depeg veto、成本口径、direct pair 与 same-underlier multi-quote 两种最小实验路径都已写清。

## 为什么这轮不给 P2
虽然 raw alpha 骨架已经成立，但还没到 `P2` admission 的诚实门槛，主要差一层最小 clean-room replication：
1. 还没有把 `single-anchor` vs `peer-median anchor` 固定成一个可回放的统一定义；
2. 还没有在公开 CEX spot 数据上证明：
   - `USDC/USDT`、`FDUSD/USDT`、`TUSD/USDT` 的 discount pocket 在统一 fee/spread 后仍保留可迁移净边；或
   - `BTC/USDT vs BTC/USDC`、`ETH/USDT vs ETH/FDUSD` 这类 same-underlier multi-quote spread 能比 direct pair 更厚；
3. 还没有把“普通折价回锚”和“真实 depeg / run-risk”用同一套 veto 阈值诚实切开。

所以它还不该直接写成 `P2`；但也不该回 `P0`，因为独立 raw alpha 主体已经清楚、且与现有 overlay / 旧 stablecoin pair 素材并不重复。

## 本轮 verdict
`stablecoin discount → peer-parity reversion` 已形成独立、可审计的 stablecoin relative-value raw alpha skeleton：主体不是监管叙事，也不是 depeg overlay，而是 fiat-backed stablecoin 在二级市场相对 `$1` / peer basket 的折价回归及其向 same-underlier multi-quote spread 的映射；因此本轮给正式 `Rank 271` 并首判 `keep_P1`，后续唯一 survivor follow-up 应只回答在统一 anchor、统一成本和 depeg veto 下，这条 discount/parity MR 是否仍保留可迁移 post-cost edge，以及 direct pair 与 same-underlier quote-spread 哪个更值得升 `P2`。
