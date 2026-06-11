# 2026-03-28 07:21 UTC | Rank 37 park reframe review

## 本轮对象
- source rank: `Rank 37`
- source label: `classic sparse TSMOM / own-past persistence pocket`
- original status: `park / evidence pool`
- 本轮结论: `keep_park`

## 为什么这轮看 Rank 37
- 按 `bot6` 轮转，最近 `Rank 50+` 与 `80~110` 已连续覆盖；`1~24` 内最近 7 天也几乎都被复盘过。
- `Rank 37` 虽在 `2026-03-24 04:07 UTC` 刚被复盘过，但之后出现了**真正新的外部证据**：
  - `research/quant_digests/2026-03-27_1555_weekday-hour-bitcoin-eventclock-alpha.md`
  - `research/quant_digests/2026-03-27_1822_utc-clock-seasonality-alpha.md`
  - 以及后续 survivor follow-up：`Rank 200` / `Rank 201` 已把 fixed clock / sparse schedule 家族推进到 `P2 admission`
- 所以这轮要回答的不是“Rank 37 原结论对不对”，而是：**这些新时钟证据，是否足以把 Rank 37 诚实地改写成一个新的窄 reframe hypothesis。**

## 原 Rank 37 为什么会 park
回看 `research/optimization_loop/2026-03-17_1717_rank37-clean-replication-park.md`，原审计结论很硬：
- 它测试的是 **own-past persistence**：把 classic TSMOM 放慢、放稀、去重叠之后，看“过去自己的方向”能不能在 `BTC/ETH/SOL 120d 15m` 上留下可交易 pocket。
- 结果三档最小 clean-room 变体在 `6bps/side` 下全部跨资产转负，`positive_asset_ratio=0/3`。
- 更关键的是，trade count 并不稀薄，说明不是“太少单导致样本不诚实”；而是 **主题本身在当前 15m crypto fast-lane 上不成立**。
- time-pocket 也只有最后一段为正，无法支撑 admission。

翻成人话：
> 原 Rank 37 被 park，不是因为执行小毛病，也不是因为参数还没调到位；而是因为“慢一点、稀一点、少重叠”并没有把 own-past persistence 救活。

## 这条线现在更像 hard park 还是 soft park
**结论：仍更像 `hard park`。**

原因：
1. 原 blocker 还在：
   - 负收益是跨三腿、跨三档最小变体同时出现，不是单 pocket 偶然失败。
2. 新证据没有救回“own-past persistence”这件事本身：
   - `Rank 200` 证明的是 **weekday-hour sparse short schedule** 可以活；
   - `Rank 201` 证明的是 **fixed UTC low-switch schedule** 可以活；
   - 这两条活下来的关键都不是“过去几小时自己的方向还会延续”，而是 **固定时钟 / 稀疏事件时段本身带方向偏置**。
3. 也就是说，新证据支持的是**另一条母线**，不是原 Rank 37 的主命题。

所以，相比 3/24 那次“时间信息更像新 family”的判断，这轮不是变软，反而是**更确认 Rank 37 的 park 应保留为 hard-ish audit record**。

## 有没有可救信号
**有，但它不属于 Rank 37 自己。**

可救信号是：
- “稀疏时段 + 低切换 + 固定 clock pocket” 在最近证据里确实活了；
- 这说明市场里不是完全没有时间结构，也不是所有 sparse schedule 都死掉。

但不可混淆的地方在于：
- Rank 37 的原句是 **classic sparse TSMOM / own-past persistence pocket**；
- 新活下来的 Rank 200 / 201 更像 **event-clock / fixed UTC schedule raw alpha**。

所以可救信号只能写成：
> 时间结构主题未死；但活下来的不是 Rank 37 这条“own-past persistence”，而是更纯的 fixed-clock raw alpha family。

## 最值得改的唯一一刀是什么
如果硬要写唯一主修改轴，最自然的一刀其实是：

> **把“own-past persistence 决定何时出手”替换成“fixed UTC / weekday-hour schedule 决定何时出手”。**

但这正是本轮不应诚实派生 `Rank 37b` 的原因：
- 这一刀不是原命题内部的窄改写；
- 它已经把 alpha 驱动力从“过去收益方向”换成“时钟本身”；
- 本质上是在换母线，而不是 reframe 原 rank。

换句话说：
- 这是**好的一刀**；
- 但它更该属于新 family（现在已有 `Rank 200 / Rank 201` 这类承接），**不该伪装成 Rank 37b**。

## 是否值得形成新的 derived hypothesis
**不值得。结论维持 `keep_park`。**

理由：
1. 原 `park` verdict 的审计意义需要保留：
   - Rank 37 已经回答了“own-past persistence 在当前 desk 映射里不成立”。
2. 新证据虽然强，但主要把价值转移到别的家族：
   - fixed-clock / sparse schedule raw alpha 已有更诚实的独立承接对象；
   - 再写一个 `Rank 37b` 只会模糊边界，造成“旧 rank 被新 family 借壳复活”的错觉。
3. 单轴约束下，若把驱动力都换掉，就不再是 reframe，而是另起题目。

## 本轮最终判断
- 原 rank 为什么 park：因为 `slow / sparse / no-overlap` 也没能救回 own-past persistence，三档最小变体在 `6bps/side` 下跨资产全负。
- 它更像 hard 还是 soft park：**hard park（比 3/24 更确认）**。
- 有没有可救信号：**有，时间结构主题本身未死；但救活的是 fixed-clock schedule family，不是 Rank 37 自身。**
- 最值得改的唯一一刀：**把驱动力从 own-past persistence 改成 fixed UTC / weekday-hour schedule**。
- 是否值得形成新的 derived hypothesis：**不值得；这已经越过“窄 reframe”边界，更诚实的承接对象是新 family，而不是 `Rank 37b`。**

## 对 queue 的写法
本轮只追加一条简短 note：
- `Rank 37 | keep_park`
- note: `3/27 的 Rank 200 / 201 与 clock digests 进一步证明“时间结构未死”，但活下来的是真正的 fixed-clock raw alpha，而不是 Rank 37 的 own-past persistence；因此原 park 保留，且比 3/24 更偏硬。`

## 关联证据
- `research/optimization_loop/2026-03-17_1717_rank37-clean-replication-park.md`
- `research/park_reframe/2026-03-24_0407_rank37-park-reframe.md`
- `research/quant_digests/2026-03-27_1555_weekday-hour-bitcoin-eventclock-alpha.md`
- `research/quant_digests/2026-03-27_1822_utc-clock-seasonality-alpha.md`
- `research/optimization_loop/2026-03-27_1927_rank200_survivor_followup_promote_p2.md`
- `research/optimization_loop/2026-03-27_2015_rank201_survivor_followup_promote_p2.md`
