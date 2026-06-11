# Rank 278 — Hyperliquid whale-trade convergence continuation — keep_P1

- 时间：2026-04-01 04:05 UTC
- 执行轮次：bot3 13m auto loop
- 对象：`research/quant_digests/2026-04-01_0325_hyperliquid-whale-trade-convergence-alpha.md`
- 新分配 Rank：`278`
- 本轮动作：fresh intake first verdict
- 结论：`keep_P1`

## 本轮只回答的问题
这条对象是否已经形成一条可审计的 event-driven raw alpha skeleton，而不是把“看见鲸鱼就跟单”的叙事、钱包热度或作者 bot 壳误写成已验证的 after-cost edge。

## 最小核对
我只做 intake 所需的最小交叉核对：
1. digest 已把对象收口为 **公开 trade stream 里的大额 aggressor trade + 5 分钟同向钱包收敛 -> 短时 continuation**，不是泛泛的链上聪明钱故事；
2. repo 原文件 `hlbot/strategies/whale_tracker.py` 确实给出完整 trigger 语义：
   - `WHALE_TRADE_MIN_USD = 50_000`
   - `SIGNAL_SCORE_THRESHOLD = 0.6`
   - `CONVERGENCE_WINDOW = 300`
   - `CONVERGENCE_BOOST = 0.15`
   并且明确使用 `users=[buyer, seller]` 地址、distinct-wallet convergence、wallet score 衰减与更新，不只是 README headline；
3. README 也确认这条分支不是孤立 signal snippet，而是挂在完整交易壳里：confidence 合并、`confidence^2` sizing、相关性桶限额、TP/SL 与 dead-man switch 都已写成可迁移交易语义；
4. 本地 live probe artifact 只回答 cadence：在约 `20.48s` 的公开 Hyperliquid `trades` 流里，`BTC/ETH/SOL` 共 `168` 笔 trade 只有 `1` 笔超过 `$50k`，说明它确实是稀疏 event-driven 触发，不是高频噪音策略。

## 为什么这轮不是 P0
它已经满足“独立 raw alpha skeleton”这一层门槛：
1. **信号定义清楚**：大额 aggressor trade、wallet score、same-side convergence window、distinct wallet count 都是可审计变量；
2. **持有与风险壳清楚**：repo 已明确 continuation 语言、confidence/sizing、TP/SL、反向信号平仓与组合限额；
3. **数据入口公开**：Hyperliquid 公共 `trades` WebSocket 就能拿到 `coin / side / px / sz / time / users`，不依赖私有订单流或不可复核 feed；
4. **对象与现有池子不重复**：它补的是“身份流 + 大单群聚 continuation”分支，不是又一个 breakout / funding / liquidation headline。

因此，这条线不该因为还没做 clean-room replication 就直接回 `background/P0`。

## 为什么这轮也不直升 P2
当前诚实缺口仍然很关键：
1. 现有证据主要证明 **策略骨架存在**，还没有证明至少一个 `1m/3m/5m/15m` 持有窗在统一成本口径下真的保留 after-cost edge；
2. live probe 只验证了触发稀疏度，没有验证 **事件后 continuation 是否足够厚、是否会被 taker/冲击吃光**；
3. wallet score 目前仍更像 repo 内部启发式 ranking，尚未在 desk 自己的 clean-room 数据里证明它确实提高 edge，而不是只制造更复杂的叙事；
4. `$50k` 绝对门槛很可能需要改成 coin-specific percentile / shock-score 版本，否则 majors 与小币的触发密度会严重不均。

所以它还不够诚实地直接升 `P2`；但它也不只是段子，值得保留为 survivor 做一次决定性 follow-up。

## 本轮改变系统认知的一句话
`Hyperliquid whale-trade convergence` 已形成可独立审计的 event-driven raw alpha skeleton：主体不是“鲸鱼跟单”叙事，而是公开钱包地址 + 大额 aggressor trade + 300 秒同向收敛驱动的短时 continuation，因此本轮正式记为 `Rank 278` 并首判 `keep_P1`；但在完成统一持有窗与 maker/mixed/taker 成本口径下的 continuation clean-room replication 前，不诚实直升 `P2`。

## 唯一合法 follow-up（survivor budget = 1）
下一步只能做一次决定性检查，直接回答：

**把 `Rank 278` 改写成 desk 版 coin-normalized whale shock continuation 后，在 Hyperliquid 公开 trade stream 上，是否至少有一个 `1m/3m/5m/15m` 持有窗能在 maker / mixed / taker 成本口径下留下可迁移 after-cost pocket？**

建议最小检查口径：
- universe：`BTC / ETH / SOL / HYPE / DOGE / PEPE / WIF` 及其他足够活跃币
- trigger：`trade_notional >= rolling q99 or q99.5`，配合 `same-side distinct whales_300s >= 2`
- exit：固定 `1m / 3m / 5m / 15m` 持有窗，外加反向 convergence 提前平仓作为附加对照
- cost：maker / mixed / taker 三档
- 目标：不是再讲鲸鱼故事，而是直接决定 `promote_P2` 还是诚实回背景
