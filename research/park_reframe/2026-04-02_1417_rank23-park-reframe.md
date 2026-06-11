# 2026-04-02 14:17 UTC｜bot6 park-reframe｜Rank 23

## 0) 本轮选择
- 选定：`Rank 23 / volatility regime mid-band / cost-survival gate`。
- 原因：
  - 它属于 `Rank 1~37` 里的已 `park` 条目；
  - 最近 `7` 天未被 bot6 复盘；
  - 3 月下旬的判断还停留在“soft park，但波动/流动性主题没死”，适合用最近新增的 `liquidity proxy / slot-cost` 证据再做一次低频校准。
- 本轮目标不是推翻原 `park`，而是判断：**最近新证据够不够把 Rank 23 诚实压成一条新的窄 reframe hypothesis。**

## 1) 原 Rank 为什么 park？
原始证据来自：`research/optimization_loop/2026-03-17_0503_rank23-clean-replication-park.md`。

原 rank 被 `park` 的核心原因：
- 它把 `realized-vol mid-band / no-high-vol-extreme` 写成了 **standalone vol/regime gate**；
- clean replication 虽然证明“避开最极端高波动”能少亏一点，但**没有把收益结构救活**；
- 它在跨资产、时间分桶、参数邻域、成本四个维度都没形成 desk 需要的诚实 pocket。

关键原始数值（`6bps/side`）：
- `baseline_mtf`：`mean_total_return≈-38.69%`，`positive_asset_ratio=0/3`
- `no_high_vol_extreme`：`mean_total_return≈-43.30%`，`positive_asset_ratio=0/3`
- `rv_midband_q20_80`：`mean_total_return≈-33.33%`，`positive_asset_ratio=0/3`，`mean_no_trade_ratio≈46.52%`
- `rv_midband_q30_70`：`mean_total_return≈-31.75%`，`positive_asset_ratio=0/3`，`mean_no_trade_ratio≈63.71%`
- time stability：主变体 `0/3` 正 bucket
- parameter stability：最优近邻也仍明显为负（最佳约 `-14.79%`）
- cost ladder：`10/15/20bps` 继续明显恶化

所以原 verdict 不能改写：**Rank 23 被 park，不是因为“波动状态永远没信息”，而是因为“把它写成可独立扛 15m 入场质量的 standalone gate，不成立”。**

## 2) 它更像 hard park 还是 soft park？
- **本轮判断：`soft park`，但比 3 月下旬时更偏硬。**

为什么还不是 pure hard park：
- `vol / liquidity / tradeability` 这个主题本身没死；
- 原失败更像“职责层级放错”，不是主题彻底归零。

为什么又更偏硬：
- 最近新增证据已经把残余价值进一步推向 **shared execution / liquidity overlay**；
- 这条残余信息已经越来越不像 Rank 23 原来那种 `shared vol entry gate`；
- 若硬写成 `Rank 23b`，很容易只是把一条更上游的 tradeability family 强行挂回旧 rank 名下。

## 3) 有没有“可救信号”？
- **有，但信号已经更像“tradeability / liquidity overlay”，而不是原 Rank 23 的 standalone mid-band gate。**

本轮主要参考的新证据：
- `research/quant_digests/2026-04-01_1426_lowfreq-liquidity-proxy-gate-overlay.md`
- `research/quant_digests/2026-04-02_0448_utc-slot-costmap-route-veto-overlay.md`

这两条新证据共同指向：
- 便宜、公开数据可得的 `Amihud / CS / AR / realized-vol` 一类 proxy，确实能描述 **什么时候更贵、更吵、更不适合高换手执行**；
- `UTC slot cost map` 说明时段本身就该进 `route / size / veto` 逻辑；
- 也就是说，Rank 23 真正还留下来的，不是“mid-band 里做 signal 更好”，而更像：
  - **高波动/差流动性时少做或降仓**；
  - **把波动状态转写成 shared tradeability layer，而不是独立 entry gate。**

翻成人话：
- 可救信号还在；
- 但它已经更像“别在最贵/最吵的时候交易”的执行层信息；
- 不再像一条应该以 `Rank 23` 名义独立存活的 queue-facing hypothesis。

## 4) 最近新证据有没有改变判断？
- **有改变，但改变的是“残余价值的角色判断”，不是把 Rank 23 救活。**

最新证据并没有说：
- `rv_midband` 终于能变成一条独立 alpha；

它们真正说的是：
- 流动性 / spread proxy / realized-vol / UTC slot 的信息，适合被写成 **shared execution-veto / size-down / routing overlay**；
- 这是一条更上游、更泛化的 tradeability family；
- 它能服务 breakout、pairs、carry、lead-lag 等多类 base alpha。

因此它**没有推翻** Rank 23 的原 `park`，反而进一步说明：
- Rank 23 的 residual value 已经从“shared vol gate”继续上移为“shared tradeability overlay”；
- 真值得新开的，是更泛化的 liquidity/execution 组件家族，而不是把旧 Rank 23 再硬包装成 `23b`。

## 5) 最值得改的唯一一刀是什么？
**唯一主修改轴仍只有一条：把 standalone `realized-vol mid-band gate` 降级成 shared tradeability / execution veto overlay。**

更具体地说：
- 不再让 Rank 23 自己决定 15m 是否放行新 signal；
- 只在现有 base setup 已触发时，额外判断当前是否处在 `high-cost / poor-liquidity / bad-slot` 区间；
- 第一刀若以后真重开，也只能做：
  - `baseline vs veto-only / size-down-only overlay`
  - 不允许顺手叠第二轴（新 entry / new exit / 新 regime stack / 新 universe）。

但今天的新证据仍不足以把这条 why-notion 直接升级成新的 queue-facing draft。

## 6) 是否值得形成新的 derived hypothesis？
- **本轮结论：`keep_park`。**

原因：
1. 原 `park` audit 对象是 `shared vol/regime entry gate`，这条结论仍成立；
2. 最近新证据给出的残余价值，已经更像一条**更泛化的 liquidity / execution overlay family**；
3. 若硬写 `Rank 23b`，会模糊“保留原 park verdict”与“另起新 family”之间的边界；
4. bot6 本轮最诚实的动作，不是 draft 一个名不副实的 `23b`，而是承认：**Rank 23 的残余价值更适合被别的 future intake / shared overlay family 吸收。**

## 7) trade on / trade off（仅作 why-not-draft 说明）
若未来真要重开，这条唯一轴仍应这样理解：
- `trade on`：把波动/流动性状态收敛成 shared tradeability overlay，减少在高成本 / 坏流动性 / 差时段里硬做薄 edge；
- `trade off`：它不再是 Rank 23 原本那种 queue-facing standalone gate，而且极容易退化成“砍单美化”；若没有严格冻结的 baseline A/B，这条线就不该重开。

但今天的新证据还不足以把这段 why-notion 升级成新的 derived hypothesis。

## 8) 本轮结论
- `keep_park`
- 补充口径：`soft park，但更偏硬；最近新增的 liquidity-proxy / UTC-slot-cost 证据把 Rank 23 的残余价值继续上移到 shared tradeability overlay family，不足以把旧的 volatility-regime mid-band 诚实派生成新的窄修改轴`

## 9) 文件动作
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## 10) commit
- 本轮默认不做 commit。
- 原因：按要求只做最小必要文档改动，且仓库长期存在与本轮无关的共享脏文件风险，避免混提。
