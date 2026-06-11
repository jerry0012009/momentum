# 2026-04-13 15:11 UTC · Rank 52 park reframe

## Selected rank
- `Rank 52`
- selection note: 本轮按 `50~79` 号段低频轮转，优先选最近 `7` 天未复盘、且仍停留在 `park` 的条目。`Rank 52` 上次 park-reframe 是 `2026-04-04 02:38 UTC`，已超过 7 天；同时 4 月上旬又新增了更明确的 microstructure / toxic-flow raw-alpha 旁证，足够再判断一次：这些新证据是在救旧 `Rank 52`，还是继续把它的主题外流到新的宿主。

## Original park reason
原始 authoritative 证据：
- `research/optimization_loop/2026-03-18_0950_rank52-trade-flow-intake.md`
- `research/optimization_loop/2026-03-18_1011_rank52-clean-replication-park.md`
- `research/park_reframe/INDEX.md` 中 `2026-04-04 02:38 | Rank 52`

原 `Rank 52 / trade-flow imbalance veto` 被 park 的原因没有变化：它把 **setup 前最后几分钟的主动成交失衡** 写成了 `15m` 三条线（尤其 `breakdown_reclaim_short` / `ema_pullback_long`）的 shared veto，但 clean replication 证明这条壳没有成立。

冻结审计里最关键的失败点：
- 主读法 `breakdown_reclaim_short + opposite_flow_veto @ 6bps`：
  - `mean_total_return ≈ -2.73%`
  - `positive_asset_ratio = 0/3`
  - `mean_trades ≈ 17.0`
  - `mean_trade_count_retention ≈ 81.90%`
  - `mean_false_break_or_hold_4bars_rate ≈ 85.65%`
- 对照 `ema_pullback_long + opposite_flow_veto @ 6bps`：
  - `mean_total_return ≈ -4.04%`
  - `mean_trade_count_retention ≈ 57.87%`
- time-pocket 也没有留下可 admission 的稳定 pocket。

翻成人话：
- 原 rank 失败的对象，一直是 **“把 trade-flow imbalance 降级成 15m shared veto 后，能稳定减少假突破 / 假回踩”** 这条写法；
- 不是 order-flow / microstructure 主题整体无效；
- 但也不是旧 Rank 52 只差一个更紧阈值就能救活。

## Hard park or soft park?
- 本轮判断：`soft park，但比 4 月 4 日那轮更接近 hard`

为什么仍保留 soft：
1. trade-flow / OFI / toxicity 主题本身显然还活着；
2. 4 月上旬新 digest 继续证明，订单流质量仍能服务短周期方向判断；
3. 失败更像是 **职责层摆错**，而不是“flow 完全没信息”。

为什么又更接近 hard：
1. 原 Rank 52 的宿主已经审计清楚：`15m` shared veto 没站住；
2. 新证据越来越像支持 **1m/3m raw alpha / event alpha**，不是支持旧的 `shared veto` 外壳；
3. 若继续在旧 rank 上做阈值、窗口、lane 微调，更像切样本而不是单轴诚实救法。

## Any salvage signal?
有，但不再属于旧 `Rank 52` 的诚实 residual。

本轮最 relevant 的新增旁证：
- `research/quant_digests/2026-04-03_0732_crossasset-ofi-vwap-shap-microstructure-alpha.md`
- `research/quant_digests/2026-04-08_1828_toxicflow-jump-continuation-alpha.md`

这些旁证共同在说：
1. flow / imbalance 的信息量更像 **短周期 directional raw alpha**，而不是 `15m` bar-close shared veto；
2. 更自然的主语是 `OFI + VWAP pressure`、`toxic-flow jump × continuation` 这种 **事件型 / 1m~3m** 宿主；
3. 它们在救的是新的 microstructure family，不是在证明旧 Rank 52 只差把 `same_direction_flow_gate` 或 `opposite_flow_veto` 再调细一点。

因此，本轮能确认的“可救信号”只有一句：
- **flow 主题仍有价值，但它该活在更快、更独立的 raw-alpha 宿主里，而不是继续停留在旧 Rank 52 的 15m shared veto 壳中。**

## Single best cut
如果只保留唯一一刀，本轮最值得改的唯一一刀其实是：

> **把 `15m trade-flow imbalance shared veto` 改写成 `1m/3m toxic-flow / OFI event-driven directional alpha host`。**

但这刀为什么仍不诚实地属于 `Rank 52b`：
1. 它同时改了 **职责层**（veto -> raw alpha）；
2. 也实质改了 **时间尺度**（15m -> 1m/3m）；
3. 还改了 **入场主语**（base setup 附件 -> event-triggered standalone host）。

这已经不是对旧 rank 的窄 reframe，而是换宿主。

## Derived hypothesis?
- 结论：`keep_park`
- 不新增 `derived hypothesis`

为什么这轮仍不值得 draft `Rank 52b`：
1. 原 `park` verdict 没被推翻；
2. 唯一显著残余价值，已经外流到更快的 microstructure / toxic-flow raw-alpha family；
3. 若现在硬写 `Rank 52b`，大概率会变成“借新 family 给旧 veto 壳续命”；
4. 这不符合 bot6 的审计边界，也不符合“唯一主修改轴”的纪律。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `soft park，但比 4 月 4 日那轮更接近 hard；4 月上旬新增的 OFI / toxic-flow 证据继续说明 flow 主题仍有信息，但它救活的是 1m/3m event-driven microstructure raw-alpha 宿主，而不是旧 Rank 52 的 15m shared veto 写法，因此当前不诚实 draft Rank 52b`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## Commit
- 本轮默认不做 commit。
- 原因：只做最小必要文档改动；且仓库存在共享脏文件风险，避免混提。
