# 2026-04-16 01:42 UTC · Rank 10 park reframe

## 本轮范围与选择
- 本轮只复盘 `1` 条 parked rank。
- 按你刚更新的口径，只在 `Rank 1~37` 中低频挑选。
- `Rank 10` 上次 park-reframe 记录是 `2026-04-09 00:24 UTC`，已超过 `7` 天边界；且它属于典型的“原 rank 已 park、唯一 residual 已有 10b、适合检查 residual 是否已被消费”的条目。
- 本轮不改 `docs/TODO.md` 顶部排班，不替 `bot2 / bot3` 分配新任务。

## 读到的最小必要材料
1. `docs/TODO.md`
2. `docs/PARK_REFRAME_QUEUE.md`
3. `docs/RECENT_PAPER_SEEDS.md`
4. `research/quant_digests/INDEX.md`
5. `research/park_reframe/INDEX.md`
6. `research/optimization_loop/2026-03-16_2312_vol-managed-ema-park.md`
7. `research/optimization_loop/2026-04-09_0805_rank10b_fresh_intake_background.md`

## 原 rank 为什么 park
`Rank 10 / volatility-managed EMA / ATR sizing overlay` 被 park 的原因并不含糊：

1. 原始 `EMA20 > EMA50` 方向层本身就没被 ATR clipping 救活；
2. `ATR_ref / ATR14` 的几档 clipping 变体在 `BTC/ETH/SOL, 120d, 15m` clean replication 下，收益不但没改善，回撤还更差；
3. 它不是“样本太稀所以暂缓判断”，而是 **交易很多、成本后仍系统性偏负**；
4. Light Stability Pack 四项一起失败：时间、参数、跨标的、成本生存线都没站住。

原始 log 的最关键一句其实已经给出审计结论：**这条线最多只算风险层反例证据，不是能前排占位的新 alpha。**

## hard park 还是 soft park
结论：**soft park，但现在已经非常接近 hard park with consumed residual。**

为什么不是直接写 hard：
- 原题里仍残留一点真实语义——`ATR / stop distance` 确实更像风险预算与 tradeability 信息，而不是纯噪音。

为什么又说已接近 hard：
- 这点残余早就不再支持 `Rank 10` 作为独立对象；
- 它唯一诚实的改写 `Rank 10b` 也已经在 `2026-04-09` 的 fresh intake first verdict 中被判成 `background / P0`；
- 所以现在剩下的不是“还有第二条可切修改轴”，而只是“这层信息还能不能附着到别的宿主里”。

## 有没有可救信号
有，但很弱，而且已经不属于 `Rank 10` 这个对象本身。

### 可救信号
- `ATR stopDistancePct` 仍然像一层 **size-down / veto / tradeability** 风险语义；
- 近期 digest 也继续支持这一点：ATR / liquidity / execution 主题若有价值，更常以 **更完整的 raw-alpha 壳** 或 **更具体的 setup-local overlay** 形式出现，而不是独立的 shared front-slot 对象。

### 不可救的部分
- `ATR-managed EMA sizing` 这条原命题已被审计完；
- `Rank 10b` 这条唯一自然 residual 也已被首判收口为 `background / P0`；
- 再往下切，几乎一定会滑成更具体宿主里的局部风险层，而不是诚实的 `Rank 10c`。

## 最值得改的唯一一刀
如果硬要保留原 rank 的残余价值，唯一诚实的一刀仍然只能是：

**把 standalone volatility-managed EMA sizing 彻底降级成 setup-local 的 ATR stopDistancePct size-down / veto 风险层。**

也就是：
- trade on：保留 `ATR / stop-distance` 对高波动、低 tradeability 事件的风险提示；
- trade off：放弃“ATR 仓位管理本身可以构成独立 rank / 独立 queue-facing 对象”的旧读法。

但这条刀法并不是新的发现；它正是既有 `Rank 10b` 已经表达、并且已经被 runtime truth 收口掉的那一刀。

## 是否值得形成新的 derived hypothesis
结论：**不值得；本轮维持 `keep_park`。**

原因很直接：
1. 原 rank 的唯一自然 residual 已经被 `Rank 10b` 消费；
2. `Rank 10b` 自身又已在 `2026-04-09` fresh intake first verdict 中被收口为 `background / P0`；
3. 4 月 11~13 的新增证据也没有把这层 ATR 信息重新拉回独立 front-slot，反而继续把它推向：
   - 更完整的 `ATR trail / ATR stop / ATR-defined shell` raw-alpha 宿主；或
   - 更 setup-specific 的 tradeability / execution / size-veto overlay。
4. 因此现在再 draft `Rank 10c`，本质上只会是把已被消费的 shared risk-layer 换个名字重写一次，不够诚实。

## 本轮结论（authoritative）
- `verdict`: `keep_park`
- `original verdict kept`: `park`
- `park flavor`: `soft park，但已接近 hard with consumed residual`
- `salvage signal`: `ATR stopDistancePct 只剩 setup-local size-down / veto / tradeability risk-layer 语义`
- `single modification axis if forced`: `demote standalone volatility-managed EMA sizing into setup-local ATR stopDistancePct size-veto overlay`
- `final judgment`: `该唯一修改轴已被既有 Rank 10b 表达，并已于 2026-04-09 收口为 background / P0；当前不诚实再派生 Rank 10c`

## 对 queue 的最小写回
仅做两处最小更新：
1. 追加本轮日志到 `research/park_reframe/INDEX.md`
2. 在 `docs/PARK_REFRAME_QUEUE.md` 的 `Recently reviewed` 区追加 `Rank 10` 本轮结论

## 备注
- 本轮未改 `docs/TODO.md`
- 本轮未新增 `derived_hypothesis_drafted`
- 本轮目标是保留原 `park` verdict 的审计意义，而不是翻案
