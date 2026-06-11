# 2026-04-05 23:32 UTC｜bot6 park-reframe｜Rank 37

- 选定：`Rank 37 / classic sparse TSMOM / own-past persistence pocket`
- 本轮结论：`keep_park`
- 原 `park` verdict：**保留**

## 为什么本轮看 Rank 37
- 本任务当前仍按低频单条复盘执行；`Rank 37` 属于 `Rank 25~49` 已 park 条目，且上次 bot6 复盘是 `2026-03-24 04:07 UTC`，已超过最近 `7` 天回避窗口。
- 它也适合现在再看一次，因为最近新增的 TSMOM 证据已经不再只是“慢一点会不会更好”，而是在回答另一个更关键的问题：**若 momentum 主题还值得追，它到底还像不像原 Rank 37 这种 sparse own-past pocket，还是已经上移成更完整的 market-state / action-router raw-alpha family。**

## 先读到的原始依据
- `research/optimization_loop/2026-03-17_1717_rank37-clean-replication-park.md`
- `research/park_reframe/2026-03-20_2020_rank37-park-reframe.md`
- `research/quant_digests/2026-04-04_2223_tsmom-bull-third-noshort-alpha.md`
- `research/quant_digests/2026-04-04_1158_tail-moment-managed-tsmom-alpha.md`

## 原 Rank 37 为什么会 park
原 clean replication 已经把最自然的救法先认真跑过一遍：
- 不再做快节奏 sign-momentum；
- 直接收窄成 `slow / sparse / no-overlap`：
  - `slow_4h_sign_hold_4h`
  - `slow_12h_sign_hold_8h`
  - `slow_4h_12h_agree_hold_8h`
- 但在 `BTC/ETH/SOL 120d 15m`、`next-bar open`、`6bps/side` 下三臂仍然全部跨资产转负，`positive_asset_ratio=0/3`。

原始失败点很集中：
1. **它不是输在“太快太密太重叠”**，因为这些借口已经被 clean replication 主动拿掉；
2. **它也不是只差某个 lookback 微调**，因为最自然的 slow/sparse 版本已经试过；
3. 剩下的正信号只是一点零散时间 pocket，不足以支撑 queue-facing 的独立假设。

所以原 `park` 的审计意义很明确：
> `Rank 37` 被 park，不是因为 classic TSMOM 主题完全没意义，而是因为把它写成 **15m 上可直接交易的 sparse own-past persistence pocket** 这件事并没有站住。

## 现在看，它更像 hard park 还是 soft park
**更像 hard park。**

原因不是主题彻底死掉，而是：
- 原 Rank 37 已经把自己最自然的一刀——`slow / sparse / no-overlap`——消费掉了；
- 这和一般 soft park 不同。一般 soft park 还会留下“角色没放对 / 阈值太硬 / 可改成 overlay”的明显残余；
- 但 Rank 37 连最像样的 `slow classic TSMOM` 版本都已经跑过，仍然没有留下足够诚实的独立 pocket。

因此它不是“主题完全错”，而是**原 rank 这层写法已经相当接近 hard no**。

## 有没有可救信号
**有主题级可救信号，但几乎没有 Rank 37 级可救信号。**

最近两条新证据都很说明问题：

### 1) `2026-04-04_2223_tsmom-bull-third-noshort-alpha.md`
这条新 digest 指向的是：
- momentum 如果要活，更像 **`bull-state-only × no-short-veto` 的 market TSMOM 壳**；
- 核心不是继续做对称的 own-past long/short sparse pocket；
- 而是承认 crypto trend 的真实残余更偏向 **bull-state 才做多、bad-state 默认空仓**。

这说明：
- **可救的是 momentum 主题**；
- 但它救活的主语已经从 `Rank 37 sparse own-past persistence pocket`，变成了 **market-state-conditioned raw alpha shell**。

### 2) `2026-04-04_1158_tail-moment-managed-tsmom-alpha.md`
这条新 digest 更进一步：
- 若趋势要继续交易，真正值钱的不是“慢一点继续追”；
- 而是 **trend-state × UPM/LPM tail quadrant router** 这种完整 action map：继续顺势 / flat / reversal。

这再次说明：
- 残余价值已经不在 `Rank 37` 原本那种单层 sparse persistence pocket 里；
- 而在一个**包含状态路由、flat、甚至 reversal 管理**的完整 raw-alpha 宿主里。

所以这轮最诚实的判断是：
> **有可救信号，但是“TSMOM family 可救”，不是“Rank 37 可救”。**

## 最值得改的唯一一刀是什么
如果硬要说只改一刀，唯一还说得过去的方向只能是：

**把 `Rank 37` 从“对称 sparse own-past long/short persistence pocket”改成“bull-state-only / no-short 的 market-state trend participation shell”。**

也就是：
- 不再把 own-past persistence 当成对称 long/short 直接交易对象；
- 只在市场进入强状态时参与 long；
- 弱状态默认 flat，而不是继续硬写 short 侧 continuation。

但这刀虽然单一，**已经不是窄 reframe，而是换主语**：
- 从单层 sparse pocket 变成 market-level raw alpha shell；
- 从 simple persistence 变成 state-conditioned participation；
- 这超出了 `Rank 37b` 该有的审计边界。

## 是否值得形成新的 derived hypothesis
**不值得。最终结论：`keep_park`。**

原因有四个：
1. 原 `park` 的 blocker 没被推翻：`slow / sparse / no-overlap` 版依然不成立；
2. 最近新证据确实说明 momentum 主题还活着，但活下来的宿主已经是 **market-state shell / tail-moment router**，不是旧 `Rank 37` 的自然窄派生；
3. 若现在硬写 `Rank 37b`，大概率会把一个新的 full-stack raw alpha 错包装成旧 rank 的小修小补；
4. 这会模糊原 `park` 的审计意义：原 Rank 37 被否掉的是“15m sparse own-past persistence pocket”，不是“所有 momentum 主题都不准再研究”。

## 本轮按模板回答
1. **原 rank 为什么 park？**
   - 因为在已经主动收窄成 `slow / sparse / no-overlap` 的 clean replication 后，三档最小变体仍全部跨资产转负，说明 own-past persistence pocket 本身不够诚实。
2. **更像 hard park 还是 soft park？**
   - 更像 `hard park`。
3. **有没有可救信号？**
   - 有，但主要是 momentum 主题级信号；最近更像 `bull-state-only / no-short` market shell 或 `tail-moment router`，不是 Rank 37 级残余。
4. **最值得改的唯一一刀是什么？**
   - 若硬改，只能把对称 sparse own-past long/short pocket 改成 `bull-state-only / no-short` 的 market-state participation shell。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得；因为这已经不是 `Rank 37` 的窄派生，而是新的 raw-alpha family 主语。

## 本轮最小写回
- 新增本轮日志：`research/park_reframe/2026-04-05_2332_rank37-park-reframe.md`
- `research/park_reframe/INDEX.md` 追加 1 条索引
- `docs/PARK_REFRAME_QUEUE.md` 仅追加 1 条最近复盘记录
- 不改 `docs/TODO.md`

## 一句话结论
> `Rank 37` 继续 `keep_park`：最近新证据说明 momentum 主题若要活，更像新的 `bull-state-only / no-short` market shell 或 `tail-moment router` raw alpha，而不是旧 sparse own-past persistence pocket 的诚实窄派生。
