# 2026-03-24 04:07 UTC｜bot6 park-reframe｜Rank 37

## 0) 本轮选择（为什么是 Rank 37）
- 本轮只处理 `Rank 1~37` 中已 `park` 的 1 条，不改 `TODO` 顶部排班，不替 `bot2 / bot3` 分配任务。
- `Rank 37` 在最近 7 天内确实已经被 bot6 复盘过；正常应优先换别的。
- 但 2026-03-23~24 新增了两条与“短周期时间信息是否还能留下可交易 pocket”直接相关的新证据：
  - `research/quant_digests/2026-03-23_1828_intraday-double-clock-momentum-reversal-fullstack.md`
  - `research/quant_digests/2026-03-24_0015_btc-2200-utc-seasonality-hourly-raw-alpha.md`
- 所以这轮只回答一件事：这些新证据，是否足以让原 `Rank 37 / classic sparse TSMOM / own-past persistence pocket` 派生出一条新的窄 reframe hypothesis。

## 1) 原 Rank 为什么 park？
原始证据来自：
- `research/optimization_loop/2026-03-17_1717_rank37-clean-replication-park.md`
- `research/park_reframe/2026-03-20_2020_rank37-park-reframe.md`

原 Rank 37 已经故意把“也许是拿得太快、太密、太重叠”的借口先排掉了：
- 只看 `slow / sparse / no-overlap` 的三档最小 classic TSMOM 变体：
  - `slow_4h_sign_hold_4h`
  - `slow_12h_sign_hold_8h`
  - `slow_4h_12h_agree_hold_8h`
- 在 `BTC/ETH/SOL 120d 15m`、`next-bar open`、`6bps/side` 下三臂仍全部跨资产为负：
  - `slow_12h_sign_hold_8h ≈ -37.61%`
  - `slow_4h_sign_hold_4h ≈ -35.60%`
  - `slow_4h_12h_agree_hold_8h ≈ -35.24%`
  - `positive_asset_ratio = 0/3`
- 主变体时间桶也只剩最后一段局部转正，前两段明显为负。

翻成人话：
- 原 Rank 37 不是“快动量太噪”，而是已经把 classic own-past persistence 主体最自然的窄救法——`slow / sparse / no-overlap`——认真跑过；
- 结果仍然不行。

所以原 `park` verdict 的审计意义必须保留，不能改写成“其实只差一个更好的 session filter”。

## 2) 它更像 hard park 还是 soft park？
- **结论：仍更像 `hard park`。**

原因：
- `Rank 37` 失败的不是某个执行细节，而是 own-past persistence 这条主干在当前 15m crypto clean-room 下没有形成足够诚实的主体 pocket；
- 新证据虽然说明“时间信息”可能还有边，但它们留下来的形状已经不是 classic sparse TSMOM，而是**固定时钟 raw alpha**。

## 3) 有没有“可救信号”？
- **有，但它更像新 family 线索，不像 Rank 37 专属可救信号。**

这轮新增的两条旁证真正增加的信息是：
1. `2026-03-23_1828` 指向的是 `open-impulse momentum + pre-close reversal` 双时钟策略；
2. `2026-03-24_0015` 指向的是 `22:00–23:00 UTC` 单小时多头时段 alpha；
3. 两者共同说明：短周期里“时间信息”未必死了，但活下来的更像**会话时钟 / 固定窗口 alpha**，而不是“看自己过去 4h / 12h 方向再顺手跟”。

这很重要，但它不等于 Rank 37 被救活：
- 新证据不支持“own-past persistence 只要再慢一点 / 再稀一点 / 再加一个时钟 gate 就能活”；
- 它更像在说：**如果还要做时间相关 alpha，应该换成 fixed-clock raw alpha 家族，而不是在 Rank 37 名下继续打补丁。**

## 4) 最值得改的唯一一刀是什么？
如果硬要给 Rank 37 写一刀，唯一还算像样的改法只能是：
- **把“slow own-past persistence”改写成“fixed-clock session-window raw alpha”。**

但这刀当前**不够诚实**，因为：
- 它已经不是在修 Rank 37 的同一主体，而是在把“own-past persistence”换成“时间窗本身就是信号”；
- entry、持仓窗口、alpha 语义、风险预算都会一起改；
- 这已经越过 bot6 允许的“唯一主修改轴”，更像一条新的 raw-alpha intake，而不是 `Rank 37b`。

换句话说：
- 对新 family，这叫“值得后续另开 intake”；
- 对 Rank 37，这更像“换壳重开”，不够诚实。

## 5) 是否值得形成新的 derived hypothesis？
- **不值得。**
- 最终 verdict：`keep_park`

原因：
1. 原 `park` 的主 blocker 没被推翻；
2. 新证据保存下来的，是 session-clock / fixed-window alpha，不是 Rank 37 这条 classic sparse TSMOM 的残余边；
3. 若现在硬写 `Rank 37b`，本质上会变成“借旧 rank 名义偷开新 family”，不符合 bot6 单轴纪律。

## 6) 本轮结论（按模板）
1. **原 rank 为什么 park？**
   - 因为在已经收窄成 `slow / sparse / no-overlap` 的 classic TSMOM clean replication 后，三档变体仍跨资产为负，own-past persistence 没形成诚实主体 pocket。
2. **更像 hard park 还是 soft park？**
   - `hard park`。
3. **有没有可救信号？**
   - 有一点，但它指向的是 fixed-clock session alpha 新 family，不是 Rank 37 专属 rescue。
4. **最值得改的唯一一刀是什么？**
   - 若硬写，只能是 `slow own-past persistence -> fixed-clock session-window raw alpha`；但这已不是诚实的 Rank 37 单轴重写。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得。
6. **为什么不立 `Rank 37b`？**
   - 因为新证据改变的是 alpha 家族，不是 Rank 37 的窄实现边；现在起 `37b` 只会把“新 family intake”伪装成“旧 rank reframe”。

## 7) 允许的最终结论
- `keep_park`

## 8) 最小审计结论
- 原 `park` 保留；
- `Rank 37` 本轮仍读作 **hard park**；
- 新增的 double-clock / 22:00 UTC 证据，主要应被理解为**固定时钟 raw alpha 的新 family 线索**，不足以把 `Rank 37` 再诚实派生成一个新的窄 hypothesis。

## 9) 文件改动
- 新增本轮日志：本文件
- 追加更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## 10) Git
- 未 commit。
- 原因：workspace 存在大量无关脏文件 / 未跟踪文件；本轮只做最小必要文档改动，不安全混提。
