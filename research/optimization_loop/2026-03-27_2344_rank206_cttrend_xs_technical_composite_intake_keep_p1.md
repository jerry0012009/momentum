# Rank 206 / CTTrend 横截面技术复合信号：fresh intake 首轮结论 = keep_P1

- 时间：2026-03-27 23:44 UTC
- 对象：`research/quant_digests/2026-03-27_1352_cttrend-xs-technical-composite-alpha.md`
- 本轮身份：bot3 执行器；按 `cycle_plan` 执行当前最前 pending 小点
- 结论：`keep_P1`，分配正式身份 `Rank 206`

## 为什么这条线值得留下
这条线留下来的，不是“把 28 个技术指标全搬到分钟级”的论文包装，而是一个更通用、可 desk 化的母策略骨架：

> **把多窗口价格/成交量/波动率技术特征压缩成一个横截面趋势分数，然后做 long top bucket / short bottom bucket。**

它和当前前排对象明显不同：
- 不同于 `Rank 203` 的配对均值回复；
- 不同于 `Rank 205` 的单币 local-drift crossover；
- 也不同于单一 breakout / reversal / 时钟 pocket 这类单轴 raw alpha。

所以它满足“足够独立、可作为单独研究对象保留”的门槛，值得正式记为 `keep_P1`。

## 为什么现在还不升 P2
当前 digest 给出的主要是论文级长期/周频证据，真正需要回答的仍是：

1. 把它压缩到 `15m/5m` 后，是否仍保留稳定的横截面排序力；
2. 这种多特征压缩是否真的优于更便宜的 `plain return-rank / simple XS momentum` baseline；
3. intraday turnover 扣掉现实成本后，是否还能留下净 alpha。

在这些问题里，**最便宜且最会改变层级判断** 的只有一个：

> 在同一 liquid perp universe、同一 holding window、同一成本框架下，做一次 `CTREND-lite vs plain return-rank` 的直接对照。

在这个对照之前，把它直接升到 `P2` 还太早；但把它判成“只是旧 momentum 换壳”也还太早。因此当前最诚实的状态是 `keep_P1`。

## runtime 应写回的变化
- 为该对象分配正式身份：`Rank 206`
- 更新 `Fresh intake slot` 的最新结果为本对象的首轮 intake verdict
- 将本轮 `cycle_plan` 第 3 小点标记为 `done`

## 一句话 verdict（供 state/result 复用）
`Rank 206：CTTrend 这条线值得保留下来的不是论文里的周频包装，而是“多窗口技术特征压缩成横截面趋势分数”的可独立 desk 化母策略；它与当前前排对象不同，正式记 keep_P1，但在完成 intraday CTREND-lite vs plain return-rank 的同窗长同成本对照前还不够升 P2。`
