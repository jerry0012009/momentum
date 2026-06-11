# 2026-04-01 21:32 UTC · Rank 22 park reframe review (revisit)

## Scope
- Source rank: `Rank 22 / up-down wave + MA20 persistence gate`
- Original authoritative verdict stays: `park / evidence pool`
- This round only asks: **在不推翻原 park 的前提下，Rank 22 是否值得再派生出 1 条新的窄 reframe hypothesis**

## Why revisit Rank 22 now
- `Rank 22` 上次 park-reframe 复盘是 `2026-03-24 08:20 UTC`，已超过 `7` 天，符合低频复查规则。
- 它属于 `Rank 1~24` 号段的 parked 条目，本轮继续在小号段里挑 1 条做低频复核。
- 最近新增的相关旁证主要是：
  - `research/quant_digests/2026-04-01_1747_1h-oversold-volume-bounce-alpha.md`
  - `research/quant_digests/2026-04-01_0528_three-candle-contrarian-tponly-alpha.md`
- 这两条新证据都在问同一个问题：**“急跌后反弹 / 过冲后回补”主题是不是该让 Rank 22 重新派生一刀？**

## Read set
- required:
  - `docs/TODO.md`
  - `docs/PARK_REFRAME_QUEUE.md`
  - `docs/RECENT_PAPER_SEEDS.md`
  - `research/quant_digests/INDEX.md`
  - `research/park_reframe/INDEX.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_0437_rank22-clean-replication-park.md`
  - `research/park_reframe/2026-03-20_1410_rank22-park-reframe.md`
  - `research/park_reframe/2026-03-24_0820_rank22-park-reframe.md`
  - `research/quant_digests/2026-04-01_1747_1h-oversold-volume-bounce-alpha.md`
  - `research/quant_digests/2026-04-01_0528_three-candle-contrarian-tponly-alpha.md`

---

## 1) 原 rank 为什么 park？
原始硬结论仍来自 `2026-03-17_0437_rank22-clean-replication-park.md`。

Rank 22 原定义是：
- 先保留 `baseline multi-tf momentum` 方向层；
- 只有当最近 4 根收盘连续站在 `MA20` 同侧，并满足 `upwave / downwave` 形态时才允许入场。

原 park 证据仍然没有变：
- 主变体 `updownwave_ma20 @ 6bps/side` 约 `-7.94%`；
- `positive_asset_ratio = 1/3`；
- 邻域最不差的 `MA15` 也只有约 `-3.26%`，本质仍是少亏；
- 时间稳定性里 `bucket_2 ≈ -12.70%`，没有稳定覆盖；
- 跨资产只剩 `SOL` 单腿为正，`BTC / ETH` 都明显为负；
- 成本升到 `10 / 15 / 20bps` 后继续恶化到约 `-27.51% / -46.17% / -59.98%`。

翻成人话：**Rank 22 证明的是“这套 persistence / wave gate 能减亏”，不是“它已经形成了可独立推进的 queue-facing alpha”。** 原 park 审计意义必须保留。

## 2) 它更像 hard park 还是 soft park？
**仍更像 `soft park`，但比上次更偏硬一点。**

原因：
- `急跌后恢复 / 反弹 / reclaim` 这个主题本身没有死；
- 但 `Rank 22` 这版写法——`multi-tf momentum + MA20 persistence + up/down wave`——已经被审计清楚：它更像一层“把最差时段过滤掉”的减亏门，而不是独立 setup；
- 连续两轮复盘后，残余信息仍只落在 **long-side recovery / bounce-quality**，且角色越来越像旁支注释，而不像值得再挂新号的独立派生。

所以：不是 hard park，因为主题未死；但也不再是那种“再补一刀很可能就能起草新号”的软状态。

## 3) 现有证据里是否存在“可救信号”？
**有，但不够形成新的派生。**

这轮新增两条旁证其实都把信息往“新 raw-alpha family”方向推，而不是往 `Rank 22b` 推。

### a) `1h oversold × volume-confirmed bounce`
`2026-04-01_1747_1h-oversold-volume-bounce-alpha.md` 留下的最强信息是：
- 真正可说清楚的 alpha 本体是 **“小时级大跌 + 放量 -> 后续 8~24h bounce capture”**；
- 它是一条完整的单币 shock-reversal / oversold-bounce skeleton；
- 它的角色不是 shared gate，而是独立 raw alpha。

这对 Rank 22 的含义不是“原 wave+MA persistence 终于能救”，而是：
- `急跌后反弹` 主题当然还活着；
- 但更诚实的写法已经偏向 **新的 event-driven MR family**，不是继续给 `Rank 22` 这条旧 gate 换壳。

### b) `three-candle contrarian fade × TP-only`
`2026-04-01_0528_three-candle-contrarian-tponly-alpha.md` 的结论也类似：
- 三连同色后的反手 fade 在 `1m` 上留下的是 **microstructure-ish / overextension fade** pocket；
- 适合写成 `1m-native raw alpha`，不适合硬抬成 `15m` 主信号；
- 它再次说明“过冲后回补”主题没死，但生存位置更靠近 **更短频率、更窄执行形状**。

这也没有把 Rank 22 原始写法救回来，反而进一步说明：
- 若继续投资这一主题，更诚实的是去开 **新的 fast MR family intake**；
- 而不是在 `MA20 persistence + up/down wave` 这个旧壳子上继续派生。

## 4) 最值得改的唯一一刀是什么？
如果只允许给一刀，本轮唯一还算诚实的表述仍然是：

**把 `standalone up/down wave + MA persistence gate` 降级成 long-side recovery-quality note，而不是继续把它当 queue-facing hypothesis。**

也就是：
- 它最多只配当“已有 long setup 触发后，再看是否出现恢复质量”的一层旁证；
- 不再值得单独起一个 `Rank 22b`；
- 更不值得顺手扩成多轴大改（换 timeframe + 换 trigger + 换 exit）。

这刀和上次相比没有本质变化，而这恰恰说明：**没有新的唯一主修改轴浮现出来。**

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

原因：
1. 原 `park` 结论没有被推翻；
2. 新增证据虽然支持“oversold bounce / shock-reversal 主题仍有信息”，但这些证据更像新的独立 raw-alpha family；
3. 若硬把它们挂到 `Rank 22b` 名下，会把“新 family intake”伪装成“旧 rank 窄救”，审计上不诚实；
4. Rank 22 剩下的残余价值仍只像 long-side recovery / bounce-quality 注释，且这一残余已经被近邻 long-side admission / recovery 主题大幅消费。

---

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park，但已更偏硬`

## Minimal audit note
本轮不重开 `Rank 22`，也不推翻原 park。

本轮只确认一件事：**最近新增的 oversold-bounce / three-candle-fade 新证据，说明“急跌后回补”主题仍活着，但它们更像新的 raw-alpha family，不是原 `Rank 22` 这条 `wave + MA persistence gate` 可再诚实派生的 `Rank 22b`。**

## Git
- 本轮只做最小必要文档改动；不做 commit。
- 原因：共享工作区长期存在大量与本轮无关的脏文件，当前不安全混提。
