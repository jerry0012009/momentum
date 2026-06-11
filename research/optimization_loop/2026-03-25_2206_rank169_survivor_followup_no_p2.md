# Rank 169 survivor follow-up：不升 P2，回到 background pool

- 时间：2026-03-25 22:06 UTC
- 对象：`Rank 169 / crosscrypto-commonshock-lag-ranking alpha`
- 阶段：`Surviving candidate` 唯一一次 decisive follow-up
- 结论：**不升 `P2`，回到 `Background pool`**

## 本轮只回答的问题
`common shock` 之后的 `BTC-led slow-follower lag ranking`，在**最小成本**与**最小持有约束**下，是否还保留值得进入 `P2` 的可复制净边？

## 直接证据
来自 intake 产物 `reports/artifacts/quant_digests/cross_crypto_predictability_20260325_1945/`：

1. `15m btc_only always-on`：平均毛收益仅 **+0.88 bps / rebalance**。
2. 即使只保留 `|BTC 15m lag return|` 的 **top 30% common-shock bars**，`15m btc_only` 也只有 **+2.17 bps / rebalance**。
3. 同口径 `15m lasso` 在 shock gate 后反而约 **-0.01 bps**，说明更复杂的 cross-coin ranking 在近期 perp transfer 上没有提供更强、可复制的净边。
4. `5m` 版本无论 `btc_only` 还是 `lasso`，shock gate 后大多仍只在 **~0.7 bps** 附近，离诚实成本后可交易边际更远。
5. 原始 digest 已明确写出：当前最像样的东西只剩 **`15m common shock pocket`**，不是全天候、可扩展的 `common-shock follower family`。

## 为什么这一步不能升 P2
`P2` 需要的不是“有一点 pocket 毛边”，而是至少值得继续做 admission 的 deployable skeleton。当前证据不满足：

- **effectiveness 不够**：最强 proxy 也只有 `+2.17 bps gross / 15m rebalance`，还停留在明显吃不下现实 round-trip 成本的量级。
- **可扩展性不够**：edge 只出现在少数 `common-shock pocket`，不像稳定可复制的 family，更像事件后偶发 lag。
- **模型增量不成立**：论文里更完整的 cross-coin 预测框架转到近期 perp proxy 后没有带来更强结果，反而弱于最简单 `BTC-only` baseline。
- **当前唯一诚实保留点太窄**：它更像一个背景研究线索——“大 shock 后可能存在慢反应 follower pocket”——还不是值得占用 `Active P2` 槽位的候选。

## 本轮 verdict
`Rank 169` 的 survivor follow-up 已完成：**当前证据只支持把它保留为“15m common-shock slow-follower pocket”这条 background hypothesis，不支持它已形成值得进入 `P2` 的可复制净边。**

因此本轮把它从 `Surviving candidate slot` 诚实结束并移回 `Background pool`。
