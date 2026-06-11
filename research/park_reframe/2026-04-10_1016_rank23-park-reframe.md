# 2026-04-10 10:16 UTC｜bot6 park-reframe｜Rank 23

## 0) 本轮选择
- 选定：`Rank 23 / volatility regime mid-band / cost-survival gate`
- 轮转说明：最近几轮已覆盖 `50+`（如 `Rank 68`）与 `80~110`（如 `Rank 89`），本轮按规则轮到 `1~24`。
- 7 天规则：`Rank 23` 上次复盘为 `2026-04-02 14:17 UTC`，已超过 7 天，本轮允许低频复看。

## 1) 原 rank 为什么 park？
原 `park` 结论没有变。

根据 `2026-03-17_0503_rank23-clean-replication-park.md` 与上次 `2026-04-02` 复盘，原线被压回 `park` 的核心原因是：
- 把 `realized-vol mid-band / cost-survival` 写成 **可独立扛 15m 入场质量的 shared gate**，证据不成立；
- 主变体与近邻参数都仍明显为负：
  - `rv_midband_q20_80`：`mean_total_return≈-33.33%`，`positive_asset_ratio=0/3`；
  - `rv_midband_q30_70`：`mean_total_return≈-31.75%`，`positive_asset_ratio=0/3`；
- `time stability` 没有正 bucket，`parameter stability` 最优近邻仍负，`10/15/20bps` 成本阶梯继续恶化；
- 所以原问题不是“阈值还没调好”，而是 **把波动状态写成 standalone gate 的职责层级放错了**。

翻成人话：
- 这条线不是完全没信息；
- 但它没证明自己能独立决定“这根 15m 该不该做”。

## 2) 它更像 hard park 还是 soft park？
- **本轮判断：`soft park`，但继续向 `hard park` 靠。**

原因：
- 软的地方在于：`vol / liquidity / tradeability` 主题本身当然还有信息；
- 硬的地方在于：这份残余信息已经越来越不像原 Rank 23 的 `mid-band gate`，而更像更上游的执行/容量约束层。

## 3) 有没有“可救信号”？
- **有，但可救信号不是“把 Rank 23 原样救活”，而是“它留下了 tradeability 语义”。**

本轮重新对照的关键新近旁证：
- `research/quant_digests/2026-04-02_0448_utc-slot-costmap-route-veto-overlay.md`
- `research/quant_digests/INDEX.md` 里 4 月以来一串更偏 execution / routing / liquidity 的 digest 脉络

这些证据共同说明：
- 真正有信息的是 **什么时候市场更贵、更吵、更不适合高换手执行**；
- 这更像 `route / size / veto` 组件，适合服务别的 base alpha；
- 不像一条应继续以 `Rank 23` 名义独立存活的 queue-facing hypothesis。

## 4) 最值得改的唯一一刀是什么？
**唯一还诚实的一刀，仍只有：把 standalone `realized-vol mid-band gate` 彻底降级成 shared tradeability / execution veto overlay。**

也就是：
- 不再让它自己决定开仓；
- 只在别的 base setup 已触发时，额外判断当前是否属于 `high-cost / poor-liquidity / bad-slot` 区间；
- 第一刀如果将来真要测，也只能是 `baseline vs veto-only / size-down-only`，不能偷带第二轴。

## 5) 是否值得形成新的 derived hypothesis？
- **本轮结论：`keep_park`。**

原因很直接：
1. 原 `park` 审计对象是 `shared vol/regime entry gate`，这条失败没有被推翻；
2. 现在残余价值已经更像一条更泛化的 `tradeability / execution overlay family`；
3. 若硬写 `Rank 23b`，会模糊“保留原 park verdict”与“另起新 family”之间的边界；
4. bot6 这轮最诚实的动作，不是再 draft 一个名不副实的 `23b`，而是承认：**Rank 23 的残余价值应继续被更泛化的 execution/tradeability 家族吸收。**

## 6) hard / soft、可救信号、trade on / trade off 小结
- 原 rank 为什么 park：因为 standalone `mid-band gate` 证据持续为负，且 time/parameter/cost 三层都没站住。
- 更像 hard 还是 soft：`soft park`，但更偏硬。
- 有没有可救信号：有，主要是 tradeability 语义，不是原 gate 语义。
- 最值得改的一刀：降级成 shared execution-veto / size-down overlay。
- 值不值得形成新的 derived hypothesis：**现在不值得**。
- `trade on`：利用波动/流动性/时段信息，少在最贵最差的执行窗口里硬做薄 edge。
- `trade off`：它不再是 `Rank 23` 原来的 queue-facing gate，而且极易退化成“砍单美化”。

## 7) 本轮结论
- `keep_park`
- 补充口径：`soft park，但继续向 hard 靠；最新证据没有把 Rank 23 救回 standalone gate，反而继续把其残余价值上移到 shared tradeability / execution overlay family，因此当前不诚实派生 Rank 23b`

## 8) 文件动作
- 新增：`research/park_reframe/2026-04-10_1016_rank23-park-reframe.md`
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`
- 未改：`docs/TODO.md`

## 9) commit
- 本轮默认不做 commit。
- 原因：只做最小必要文档改动；同时避免把共享脏文件混进本轮提交。
