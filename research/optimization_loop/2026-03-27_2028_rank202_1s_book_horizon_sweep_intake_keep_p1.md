# Rank 202 / 1s book horizon sweep microstructure drift — fresh intake verdict = keep_P1

- 时间：2026-03-27 20:28 UTC
- 对象：`research/quant_digests/2026-03-27_1927_1s-book-horizon-sweep-alpha.md`
- 执行动作：fresh intake first verdict
- 正式 Rank：`202`
- 结论：`keep_P1`

## 这轮只回答一件事
这条新 digest 现在应不应该进入前排继续占资源？

我的结论是：**应该保留，但只保留到 `P1`，不能直接升 `P2`。**

## 为什么保留
这条线留下来的，不是 repo 里的 `BTC long-only LightGBM` 外壳，而是更一般化的一条 raw alpha 母线：

> **`1s` 盘口失衡 / microprice 偏移 / 净订单流共振，是否会在更慢一些的 `3m~15m` 方向漂移里留下可交易 edge。**

当前 digest 已经给出三个对前排有意义的正面信号：

1. **alpha 本体清楚，不是纯黑箱。**
   关键特征族、标签、purged walk-forward、动态分位阈值、cost-aware 执行骨架都写得比较完整。
2. **repo 至少展示了 gross edge 随 horizon 拉长而改善。**
   `3m` gross 小正但 net 明显负，`15m` net 接近打平，`30m` 在重 taker 成本假设下才勉强转正；这说明它更像“微结构压力映射到较慢漂移”的候选，而不是已经成立的 ultra-short HFT 成品。
3. **下一步 cheapest decisive follow-up 很明确。**
   直接把同一框架平移到 Binance/Bybit 公共 feed，做 long/short 对称版，并输出 horizon × hold × cost 生存表，就能快速回答它到底是可交易母策略，还是只是 repo 内部的长持有 timing 偶然体感。

## 为什么不直接升 P2
还差几个 admission 前必须先补的硬缺口：

1. **当前证据主要还是 repo/self-reported artifact，缺少我方最小复验。**
2. **repo 版本管理不干净。** `config` 与输出命名不一致，原始输入文件也未随仓库发布。
3. **执行层目前只做 long-only。** 但对象真正值钱的部分反而是 long/short 对称版；在 short 侧未测前，不够进入 `P2 admission`。
4. **当前唯一存活窗口要到 `30m` taker 假设下才勉强净正。** 这离“足够值得 paper trade / pre-paper”还差一层最小外部复验。

## 对 runtime 的影响
因此，这轮 runtime 应写成：

- 分配正式 `Rank 202`
- fresh intake verdict = `keep_P1`
- 进入 `Surviving candidate slot`
- survivor 唯一 follow-up 应围绕：
  - 公共 feed 最小复验
  - `long/short` 对称版
  - `3m/5m/15m` horizon × cost 生存表
- **不要**现在就把它写成 `P2`，也不要把它当成已经可部署的 microstructure 策略

## 一句话结果
`Rank 202 / 1s book horizon sweep microstructure drift` 首轮 intake 完成：这条线保留下来的不是 repo 里的 `BTC long-only HFT` 外壳，而是“`1s` 微结构压力能否迁移成 `3m~15m` 可交易方向漂移”的 raw alpha 母线；当前 repo 证据足够支持 `keep_P1`，但因仍缺公共 feed 最小复验、short 侧对称检验与干净 executable artifact，暂不升 `P2`。
