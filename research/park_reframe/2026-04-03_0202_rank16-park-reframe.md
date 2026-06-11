# 2026-04-03 02:02 UTC · Rank 16 park reframe

## Selected rank
- `Rank 16`
- selection note: 本轮按 `Rank 1~37` 的 parked 条目低频轮转；`Rank 16` 上次 bot6 复盘是 `2026-03-22 20:41 UTC`，已超过 `7` 天。最近又新增 `2026-04-03_0042_btc-volclock-first30-impulse-alpha.md`，值得再判断一次：它是在救旧 `Rank 16`，还是把主题继续上移到新的单币 intraday raw-alpha family。

## Original park reason
原始 authoritative 证据：
- `research/optimization_loop/2026-03-17_0159_rank16-clean-replication-park.md`
- `research/park_reframe/2026-03-22_2041_rank16-park-reframe.md`

原 `Rank 16` 被 park 的原因没有变：把 **固定 pseudo-open ORB + protective closing** 直接搬到 crypto `15m`，clean replication 仍是高频、跨资产、成本后一起转负。

冻结版 first-pass 结果（`range_bars=2`, `tau=0.10 ATR`, `6bps/side`）：
- `raw_orb ≈ -35.11%`
- `confirm1_outside ≈ -7.51%`
- `retest_hold ≈ -8.36%`
- `protective_close_overlay ≈ -21.50%`
- `positive_asset_ratio = 0/3`
- 参数邻域 `0/6` 为正，成本梯度持续恶化

翻成人话：
- 裸 ORB 很差；
- 加一层确认只是少亏，不是转正；
- `protective close` 也没有把这条线救活。

所以原审计意义必须保留：**失败对象是“固定 pseudo-open ORB 在 crypto 15m 上可直接当 standalone alpha”这件事，不是 intraday threshold / impulse 主题永远无效。**

## Hard park or soft park?
- 本轮判断：`soft park，但比 3 月下旬时更偏硬`

为什么不是 pure hard park：
- 原始 clean replication 里，`confirm1_outside` 相比 `raw_orb` 确实明显少亏；
- 说明问题更像 fixed pseudo-open 定义太粗，而不是“所有 intraday threshold / confirm 都没信息”。

为什么又更偏硬：
- 最近新增价值越来越不在“固定 session-range gate”这具旧壳子里；
- 新证据更像在把主题推向 **single-asset / volume-clock / impulse-continuation raw alpha**，而不是给旧 `Rank 16` 再开一个诚实的 `16c`。

## Any salvage signal?
有，但主要是“主题没死”的信号，不是“旧 rank 还能再切一刀”的信号。

本轮最 relevant 的新增证据：
- `research/quant_digests/2026-04-03_0042_btc-volclock-first30-impulse-alpha.md`
- `research/quant_digests/2026-03-19_0956_volume-clock-cs-spread-interaction-gate.md`
- `research/quant_digests/2026-03-19_0426_bitcoin-first-30m-impulse-quality-gate.md`

这些新证据共同在说：
1. 可保留的信息不再是“固定 00/08/16 pseudo-open ORB”；
2. 更值得测的是 **volume-clock 定义开段 + 极端量/波冲击 + 30~60m 同向续行**；
3. 这更像一条新的、偏单币 BTC 的 event-style raw alpha，而不是旧 `Rank 16` 还能再诚实派生的窄 reframe。

换句话说：
- 有可救信号；
- 但它在救的是“开段冲击续行”这个新主语；
- 不是在救旧 `Rank 16` 的 fixed session-range / protective-close 写法。

## Single best cut
如果只保留唯一一刀，当前最诚实的仍然是既有 `Rank 16b`：

> 把固定 pseudo-open ORB 改写成 **active-hours session-range break/retest gate**。

本轮不建议再写新的唯一主修改轴，原因是：
- 若写成 `volume-clock first30 impulse`，主语已经从 shared gate 变成单币 raw alpha；
- 若写成 `extreme volume + impulse continuation`，也不再是旧 Rank 16 的 session-threshold 轻改，而是在重写事件定义、作用层级和 alpha 主体；
- 若把这些东西硬挂成 `Rank 16c`，会模糊原 `park` 的审计边界。

所以本轮最值得改的唯一一刀，**仍然只是旧的 `Rank 16b`，不是新的 `Rank 16c`。**

## Derived hypothesis?
- 结论：`keep_park`
- 不新增 `derived hypothesis`

原因：
1. 原 `park` verdict 仍完整成立；
2. 最近新增证据没有给 `Rank 16` 提供一个仍属于它自己的新单轴修改；
3. intraday opening-impulse 的新增价值正继续上移到新的 BTC / volume-clock raw-alpha family；
4. 对旧 rank 来说，唯一还诚实的 residual cut 仍是既有 `Rank 16b`。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `soft park，但更偏硬；最近新增的 BTC volume-clock first30 impulse / spread×impulse 证据，更像新的单币 intraday raw-alpha family，不足以在既有 Rank 16b 之外再诚实派生 Rank 16c`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## Commit
- 本轮默认不做 commit。
- 原因：按要求只做最小必要文档改动；且仓库存在共享脏文件风险，避免混提。
