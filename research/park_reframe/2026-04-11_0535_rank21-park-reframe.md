# 2026-04-11 05:35 UTC · Rank 21 park reframe review

## Scope
- Source rank: `Rank 21 / market risk-on/off regime gate`
- Original authoritative verdict stays: `park / evidence pool`
- This round only asks: **在不推翻原 park 的前提下，4 月上旬新增的 sentiment / macro-event 证据，是否足以在既有 `Rank 21b` 之外，再诚实派生一条新的窄 reframe hypothesis。**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_0412_rank21-clean-replication-park.md`
  - `research/park_reframe/2026-04-01_1313_rank21-park-reframe.md`
  - `research/quant_digests/2026-04-03_2354_fng-extremity-adverse-selection-overlay.md`
  - `research/quant_digests/2026-04-05_2318_tuning-news-sentiment-macro-impulse-alpha.md`

## Why this rank this round
- `Rank 21` 属于 `Rank 1~37` 的已 parked 条目。
- 距离上次 bot6 复盘（`2026-04-01 13:13 UTC`）已超过 7 天，满足低频复看条件。
- 它已经有一条既有窄派生：`Rank 21b = daily sentiment-extremity shared risk overlay`。
- 4 月上旬又新增了两类容易让人误判为“还能继续救”的证据：
  - `F&G extremity × adverse-selection veto`（更强地支持 overlay 语言）
  - `scheduled macro impulse × pre-event sentiment`（把 sentiment 拉向 event-driven raw-alpha 宿主）
- 本轮要回答的是：**这些新证据是否真的构成新的 `Rank 21c` 单轴，还是只会进一步钉死“原 rank 已 park，残余只到既有 21b 或更上位新 family”。**

---

## 1) 原 rank 为什么 park？
原 `Rank 21` 被 park 的原因没有变化，而且仍然很硬：

原 clean replication 关键结果：
- `market_risk_2of3 @ 6bps/side`：`mean_total_return ≈ -25.01%`
- `positive_asset_ratio = 0/3`
- `mean_trades ≈ 265.0`
- `mean_no_trade_ratio ≈ 51.29%`
- `10bps/side ≈ -39.22%`
- `15bps/side ≈ -53.14%`
- 时间稳定性：`0/3 positive buckets`
- 参数邻域最佳也只有约 `-17.06%`

翻成人话：
- `market risk-on/off` 这条线并不是“再调一下就能转正”；
- 它证明的只是：**15m 同频 shared gate 比 baseline 少亏一点**；
- 但完全没证明：**逐根 15m risk-on/off allow/deny 本身是足够诚实、足够稳的 queue-facing alpha / gate。**

所以原 verdict 仍然必须保持：
- 原 rank 应继续读作 `park / evidence pool`；
- 不应因为后续 sentiment 主题继续活跃，就回头推翻这个审计结论。

## 2) 它更像 hard park 还是 soft park？
**本轮仍读作 `soft park`，但对原 Rank 21 本体的 15m 同频 gate 读法已经更偏 hard。**

为什么还不是 hard park：
- `risk sentiment / risk state` 本身没有完全死掉；
- 它依然可能对仓位、阈值、maker/taker 选择、是否停手有信息量。

为什么又明显比一般 soft park 更硬：
- 原始失败点已经被 clean replication 审计清楚，不像参数还没扫到；
- 原线唯一诚实残余，早已被收窄成既有 `Rank 21b`；
- 4 月新增证据没有提供第二条独立、同层的新修改轴，反而继续强化“这条线只适合做更低频 overlay，或迁到新的 event-driven 宿主”。

## 3) 有没有“可救信号”？
**有，但仍然只有一条可救信号，而且它继续指向既有 `Rank 21b`，而不是新的 `Rank 21c`。**

### 可救信号 A：extremity 更像 adverse-selection / spread-widening 警报
`2026-04-03_2354_fng-extremity-adverse-selection-overlay.md` 给出的最强信息是：
- 极端 fear / greed 更像 `spread 更坏 / 噪声更大 / 流动性更差` 的 regime；
- 它不适合读成方向预测器；
- 更适合读成 `size-down / veto / stricter confirmation` 的共享 overlay。

这其实不是新轴，而是把既有 `Rank 21b` 说得更硬：
- `Rank 21` 的残余价值不是“逐根 allow/deny”；
- 而是“极端日少做 / 缩尺 / 提确认”。

### 可救信号 B：sentiment 还能服务事件窗，但那已经更像新宿主
`2026-04-05_2318_tuning-news-sentiment-macro-impulse-alpha.md` 的关键信息是：
- 真正可交易的 base alpha 是 `scheduled macro announcement -> immediate impulse`；
- pre-event sentiment 更像 admission / amplitude gate，而不是方向本体。

这条证据说明 sentiment 主题确实没死；
但它的落点已经变成：
- `event-driven raw alpha shell + sentiment gate`。

也就是说：
- 如果继续追这条线，更诚实的对象是新的 macro/event family；
- 而不是从旧 `Rank 21 / market risk-on/off 15m shared gate` 再硬切一条 `Rank 21c`。

## 4) 最值得改的唯一一刀是什么？
**唯一最值得改的一刀没有变化，仍然只是既有 `Rank 21b`：**

- **single modification axis:** `demote standalone market risk-on/off regime gate into a daily sentiment-extremity shared risk overlay`

具体读法仍是：
- 不再根据 `market_risk_2of3 / 3of3` 逐根决定 15m setup 是否 allow；
- 保留 breakout / fib / EMA-PSAR 一类 base setup 原始触发；
- 只在 `Fear & Greed <= 25` 或 `>= 75` 的极端日做 `size-down / stricter-confirm / veto`。

本轮最关键的判断恰恰是：
- 4 月新增两条证据，并没有产生新的唯一主修改轴；
- 它们只是在两个方向上把旧结论钉得更牢：
  1. `F&G extremity` 更支持 overlay；
  2. `macro impulse × sentiment` 则更支持迁到新 event-driven 宿主。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

更精确地说：
- 原 `Rank 21` 的 `park` 保持不变；
- 既有 `Rank 21b` 继续保留，而且仍然是唯一诚实窄派生；
- 本轮新证据不足以再派生 `Rank 21c`。

原因有三层：
1. 新增的 `F&G extremity` 证据没有提出第二个单轴，只是更强地支持 21b；
2. 新增的 `macro impulse × sentiment` 证据虽然有价值，但主语已经变成 event-time raw alpha，不再属于旧 Rank 21 的同层修补；
3. 如果把 extremity overlay 和 macro-event shell 一起塞回 Rank 21，就会变成多轴大改，不符合 bot6 每轮只允许一刀的纪律。

## 6) trade on / trade off 怎么读？
本轮不新增派生，因此这里只做审计式复述：

### trade on
- 如果将来还要保留 Rank 21 的残余价值，最诚实的做法仍然是：
  - 让 sentiment extremity 只负责 `risk overlay / sizing / veto / stricter confirmation`；
  - 不再假装它能逐根给出方向性 allow/deny。

### trade off
- 它不再是独立 alpha，也不再是 standalone gate；
- headline return 可能不会显著改善，更多体现在 left-tail / tradeability；
- 若改善主要来自砍单，仍然应快速压回 park；
- 如果继续往 `macro-event + sentiment` 延伸，那就已经不是旧 Rank 21 的 reframe，而是新的 event-driven family intake。

---

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park，但对原 15m 同频 market risk-on/off gate 读法已更偏 hard`

## Minimal audit note
本轮不推翻 `Rank 21` 的原 park，也不新增 `Rank 21c`。
更诚实的记录是：**4 月上旬新增的 extremity / macro-sentiment 证据，一部分继续把 Rank 21 的唯一残余钉死在既有 `Rank 21b`（daily sentiment-extremity shared risk overlay），另一部分则把 sentiment 主题抬升到新的 event-driven raw-alpha 宿主；两者都不足以再为旧 Rank 21 诚实派生新的单轴 reframe。**

## Git
- 本轮只做最小必要文档改动；未做 commit。
- 原因：工作区可能存在无关脏文件，当前任务不需要安全 selective commit。