# 2026-04-19 14:48 UTC — Rank 16 park reframe review

## 为什么本轮选 Rank 16
- 本轮继续只处理 `1` 条已 `park` rank。
- `Rank 16` 上次 bot6 park-reframe 复盘是 `2026-04-12 06:04 UTC`，相对当前轮次已超过 `7` 天。
- 期间出现了新的直接旁证：`research/quant_digests/2026-04-18_0558_session-orb-widthgate-shell.md`。它值得用来判断：旧 `Rank 16` 是否还存在一条属于原命题的窄 reframe，还是应继续保留原 `park`。

## 本轮补读
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/optimization_loop/2026-03-17_0159_rank16-clean-replication-park.md`
- `research/park_reframe/2026-04-12_0604_rank16-park-reframe.md`
- `research/quant_digests/2026-04-18_0558_session-orb-widthgate-shell.md`

---

## 1) 原 Rank 为什么 park？
原 `Rank 16` 的主语是：把固定 `pseudo-open` 的 `ORB threshold + protective closing session gate` 写成可独立承压的 `15m` session breakout 策略。

它被 park 的核心原因没有变：
- `raw_orb @ 6bps/side` 约 `-35.11%`，原始写法明显失真；
- `confirm1_outside` 虽把亏损收窄到约 `-7.51%`，但仍是 `positive_asset_ratio=0/3`、交易频繁且成本后持续为负；
- `protective_close_overlay` 没有把它救回来，反而更差；
- 参数邻域（`range_bars=2/3`、`tau=0/0.1/0.2 ATR`）`0/6` 为正，说明不是单点参数埋了 pocket；
- 成本从 `6bps` 升到 `10/15/20bps` 后继续明显恶化。

所以原 `park` 记录的是一件很具体的事：**固定 pseudo-open ORB 这套 standalone 15m 写法不成立**。原审计结论不应被推翻。

## 2) 它更像 hard park 还是 soft park？
本轮判断：**soft park，但比 4 月 12 日那轮更接近 hard with consumed residual。**

- `soft` 的部分：session opening-range / breakout 主题本身并没有被证明完全没信息；
- `更接近 hard` 的部分：新证据并没有把旧 `Rank 16` 的残余救回原壳，反而更明确地说明，若主题还有价值，它更像新的完整 raw-alpha shell，而不是旧 rank 的下一条窄派生。

## 3) 有没有“可救信号”？
**有，但更像“主题外流”的可救信号，不是旧 Rank 16 本体的可救信号。**

4 月 18 日新增 digest 给出的关键结论是：
- plain session ORB 在 crypto 上直接照抄仍偏负；
- 但 **US session × box-width gate** 留下了可审计 pocket；
- 也就是说，真正站住的是“特定 session + 特定 box 宽度条件下的 opening-range breakout shell”。

这条信号的重要含义不是“旧 Rank 16 只差再补一个小 gate 就能回来”，而是：
- session ORB 若有残余价值，更像一条 **完整的 session-conditional raw-alpha shell**；
- 它有自己独立的 session 选择、box-width gate、R-multiple exit、per-session trade budget；
- 这已经超出旧 `Rank 16` 的“fixed pseudo-open ORB + protective close”单轴纠偏语义。

因此，可救信号存在，但它救活的是 **新的 ORB/session shell 宿主**，不是旧 `Rank 16` 的 `Rank 16c`。

## 4) 最值得改的唯一一刀是什么？
如果仍站在旧 `Rank 16` 语义里，唯一还诚实的一刀仍然是：

**把固定 pseudo-open ORB 改写成 active-hours / selected-session session-range breakout gate。**

但关键在于：
- 这条唯一主修改轴早已被既有 `Rank 16b` 覆盖；
- 而 `Rank 16b` 又已经在 2026-04-09 的 fresh-intake first verdict 中收口为 `background / P0 / absorbed`；
- 4 月 18 日的新 digest 不是在 `16b` 这条轴上给出更好的旧线实现，而是进一步把主题上移成新的完整 ORB shell。

所以，本轮最值得改的一刀并没有产生“新的旧-rank residual”；它只是在逻辑上再次确认：**旧 Rank 16 的唯一诚实 residual 已被 16b 消费完。**

## 5) 是否值得形成新的 derived hypothesis？
**不值得；本轮结论是 `keep_park`。**

原因：
1. 原 `park` 审计意义仍然成立，不能推翻；
2. 旧 rank 唯一诚实 residual 仍只到既有 `Rank 16b`；
3. `Rank 16b` 已被 runtime truth 收口为 `background / P0 / absorbed`；
4. 4 月 18 日的新证据虽然强化了 session ORB 主题，但它强化的是 **新的 session+box-width raw-alpha shell**，不是旧 `fixed pseudo-open ORB` 命题下还能再切出的单轴窄 reframe。

---

## 本轮模板回答（简版）
- 原 rank 为什么 park：固定 pseudo-open ORB 在 `15m` crypto 上对成本、跨资产与参数邻域都不够诚实。
- 更像 hard 还是 soft：`soft park`，但已比 4 月 12 日那轮更接近 `hard with consumed residual`。
- 有没有可救信号：有，但它指向新的 `session ORB × box-width gate` raw-alpha shell，而不是旧 rank 本体。
- 最值得改的唯一一刀：旧 rank 内唯一还诚实的一刀仍只是把 fixed pseudo-open 改写成 active-hours / selected-session gate，而这已被 `Rank 16b` 覆盖并消费。
- 是否值得形成新的 derived hypothesis：不值得，继续 `keep_park`。

## 最终结论
- verdict: **`keep_park`**
- note: 原 `park` 保留；4 月 18 日新增的 ORB width-gate 证据没有救活旧 `Rank 16` 的 fixed pseudo-open ORB 读法，反而更明确地把 session breakout 主题推向新的完整 raw-alpha shell，因此当前不诚实 draft `Rank 16c`。

## Git / 执行备注
- 本轮只做最小必要文档改动。
- 工作区存在大量无关脏文件；为避免混提，本轮不做 selective commit。
