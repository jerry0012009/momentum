# bot3 optimization loop — hawkes LOB excitation fresh intake收口

- 时间：2026-04-21 04:42 UTC
- 对象：`research/quant_digests/2026-04-20_1945_hawkes-lob-excitation-baseimbalance-alpha.md`
- 执行动作：fresh intake first verdict
- 目标小点：对 `order-flow excitation state × base-imbalance signed drift` 只补 1 个最小 decisive blocker：确认在当前可获得的 Binance book/depth 或公开高频 proxy 下，`excitation + BI` 是否能在 `1m/3m` 聚合后超过 maker/taker、queue latency 与 cancel-delay realism 成本，而不是只停留在“下一次 mid-price change”的论文准确率。

## 本轮最小证据
1. digest 自带的论文与 repo 证据都把主结果锁在 `next mid-price change` / 秒级 event-time 预测，而不是 `1m/3m` after-cost 可成交收益：
   - 论文 headline 是 `HawkesTime` 相比 sign-only/naive baseline 提升方向准确率与时间预测误差。
   - repo 公开说明也只是 `collect_lob_data -> convert -> train multivariate hawkes -> predict_mid_price_events`，输出定位仍是 LOB 事件与 mid-price event 仿真，不是带 fee / queue / cancel-delay 的可交易策略壳。
2. 这条线的 alpha 兑现窗口天然过短：digest 写明 mid-price change 事件间隔中位数约 `0.215s`，说明优势主要存在于亚秒级微结构层；若 desk 只能诚实压成 `1m/3m` 聚合 proxy，edge 很大概率被 spread、手续费、排队失败和 cancel-delay 吞没。
3. 当前公开可见材料没有给出能跨过最小执行摩擦的 bps 级证据：
   - 没有 `1m/3m` markout / net-bps vs 静态 BI baseline 的公开表；
   - 没有 Binance 级别的 `book/depth` 复算样本去证明 `excitation gate` 的 uplift 仍高于 maker/taker + queue latency；
   - 现有 repo 还依赖 Bitfinex LOB 采集与 Hawkes 仿真环境，迁移成本高，但没有留出独立 after-cost pocket 证据来支撑继续保留前排。

## 结论
`order-flow excitation state × base-imbalance signed drift` 当前仍只是“event-time admission / urgency score”级的 microstructure 研究线索：公开证据停留在 Bitfinex 秒级 `next-event` 准确率与仿真层，未证明在 desk 可获得的 Binance/public proxy 上压成 `1m/3m` 后还能跨过 maker/taker、queue latency 与 cancel-delay realism；因此本轮不保留 survivor，直接收口 `background/P0`。

## 对 runtime 的影响
- `Fresh intake slot`：记为完成，最新结论写成 `background/P0`
- `Background pool`：追加该对象的收口记录
- `cycle_plan`：当前小点写成 `done`
