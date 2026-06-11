# Rank 284 — dual-test coint z-score pairs：first verdict = keep_P1

- 时间：2026-04-01 21:49 UTC
- 对象：`ADF + Johansen dual-test pair admission × rolling-beta spread z-score fade`
- 来源：`research/quant_digests/2026-04-01_2105_dualtest-coint-zscore-pairs-alpha.md`
- 本轮角色：bot3 当前轮第 1 个 pending 小点执行

## 本轮结论

这条 intake 已经形成**可审计的 pairs raw alpha skeleton**，因此本轮正式记为 `Rank 284`，首判 `keep_P1`。

更准确地说，值得保留的不是 repo headline 里的“daily pairs strategy”，而是这层更可迁移的 admission 壳：

> 先用 `ADF + Johansen` 双检验守住 pair admission，再把 `rolling beta / alpha` 定义下的 spread z-score fade 下放给执行层。

这足以证明对象不是空泛的课程式 pairs 叙事；但当前还不够诚实地直升 `P2`。

## 为什么能留在前排（keep_P1）

1. **raw alpha 骨架完整**：pair formation、hedge ratio、entry/exit、stop、turnover cost 都写出来了，不是只讲“均值回复会发生”。
2. **真正新增的系统认知是 admission shell，而不是又一个 pair 回测**：这轮最值钱的部分是“别只看 ADF；pair 不干净时宁可不做”，这和当前项目里已经累积的 `half-life gate / wide-band entry / parameter plateau` 是互补的。
3. **clean-room transfer path 存在**：repo 本体虽然是 daily CoinGecko，但它给了可以直接迁到本项目的最小实验骨架——`1h` 做 pair discovery、`15m` 做 spread 执行、明确比较 `ADF-only` vs `ADF+Johansen`。

## 为什么现在还不能升 P2

当前至少有 4 个诚实 blocker：

1. **频率迁移还没被证实**：repo 是 `1D` 数据、`12m IS + 6m rebalance + 90d rolling beta`，还没有证明同一 admission 壳搬到本项目的 `1h -> 15m/5m` 结构后仍保得住 after-cost edge。
2. **pair fallback 不诚实**：代码在 `require_johansen=True` 且双检验后没有 pair 时