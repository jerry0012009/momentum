# 2026-03-19 06:44 UTC · Rank 3 park reframe review

## Scope
- Source rank: `Rank 3 third-touch + EMA/MACD confluence`
- Original verdict stays: `park / evidence pool`
- This round only asks: **should Rank 3 derive one narrower reframe hypothesis, without overturning the original park?**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- recent reframe logs:
  - `research/park_reframe/2026-03-19_0433_rank28-park-reframe.md`
  - `research/park_reframe/2026-03-19_0214_rank8-park-reframe.md`
  - `research/park_reframe/2026-03-18_1925_rank11-park-reframe.md`
- needed evidence:
  - `research/optimization_loop/2026-03-16_0838_scout-rank3-first-verdict.md`
  - `research/optimization_loop/2026-03-16_1434_scout-rank3-parameter-stability-park.md`
  - `research/quant_digests/2026-03-19_0632_breakout-wick-rejection-asymmetric-veto.md`

## Why this rank
- It is within `Rank 1~37` and currently parked.
- It has **not** been reviewed by `bot6` in the recent 7-day reframe queue.
- It is tempting because the original best slice was not a huge blow-up; `third_touch_plus_ema_macd` did reduce noise versus raw breakout.
- But the key question is whether that remaining signal supports a **single narrow salvage axis**, or whether the line is already too thin and too consumed by adjacent structure-confirmation evidence. After re-reading the original verdict, the honest answer is: **too thin, and too consumed.**

## 1) 原 rank 为什么 park？
Rank 3 被 park，不是因为“third-touch + EMA/MACD confluence 完全没信息”，而是因为它在 first verdict 里留下的最好结果，本质上只是 **极少样本下的少亏 / 微正 pocket**，后续补齐参数稳定性后依然没有形成可 admission 的厚度。

原始关键证据：
- first verdict 最佳变体 `third_touch_plus_ema_macd @ 6bps/side`
  - `mean_total_return≈+0.78%`
  - `positive_asset_ratio=1/3`
  - `mean_trades≈0.33` 笔/资产
  - `mean_false_break_ratio=0.00%`
- 补齐 `parameter stability dry-check` 后：
  - `positive_neighbor_floor`：pass（`7/7 positive`）
  - `cross_asset_neighbor_floor`：**fail**（`0/7` 达到 `>=2/3` 正资产）
  - `trade_count_neighbor_floor`：**fail**（`0/7` 达到 `>=1 mean trades/asset`）

翻成人话：
- 它确实把 `raw_breakout` 的噪声切掉了；
- 但切得太狠，最后只剩“看起来干净、其实几乎没交易”的超薄 pocket；
- 因此原 `park` verdict 必须保留，它不是还差一张漂亮图或一刀小补就能升格的状态。

## 2) 它更像 hard park 还是 soft park？
**更像 `hard park`。**

原因不在于它亏得最惨，而在于它的 blocker 太集中、太基础：
- 问题不是单一成本档位、单一资产腿、或单一时间 pocket 拖累；
- 问题是它整个 edge 读法都建立在**极端稀疏样本**上；
- 一旦要求最基本的跨资产厚度和参数邻域可用性，它就站不住。

所以它更像：
- `third-touch` 这种极窄结构过滤在当前 15m crypto 上可以当“解释性证据”；
- 但不再像一个还值得单独派生 `Rank 3b` 的 active hypothesis 母体。

## 3) 有没有“可救信号”？
**只有很弱的可救信号，不足以支撑新的派生假设。**

弱信号主要有两点：
1. 相对 `raw_breakout`，它确实大幅压掉了噪声和假突破；
2. 参数邻域的单点收益没有立刻翻负，说明“更严格的结构确认”这个大方向不完全荒谬。

但为什么仍不够：
- `mean_trades≈0.33` 笔/资产，说明 pocket 薄到几乎无法当策略层证据；
- `positive_asset_ratio=1/3`，不是一个 honest cross-asset pocket；
- 真正最自然的救法，其实不是继续磨 `third-touch` 本身，而是把它改写成更通用的结构确认 / failure-filter 模块。

而这条最自然的救法，邻近证据已经基本消费掉了：
- `Rank 31 / structural reclaim`、`Rank 33 / NW-confirmed HL reclaim`、`Rank 53 / close-confirmed CHoCH` 这类更通用的结构确认写法，都已经试过且没有产出干净 promotion read；
- 最新 `wick-rejection asymmetric veto` digest 也提示：如果还有残余价值，更像是 **post-trigger failure filter**，而不是继续让 `third-touch + EMA/MACD` 充当独立 entry hypothesis。

所以当前更诚实的结论是：
- Rank 3 留下的是“结构确认有时能少亏”的证据；
- 不是“Rank 3 自己还值得再派生一条窄重开”。

## 4) 最值得改的唯一一刀是什么？
**表面上最值得改的一刀，是把 `third-touch + EMA/MACD confluence` 从直接 entry gate，降级成更通用的 post-trigger structure/failure filter。**

例如更抽象地说：
- 不再要求第三触点本身生成交易；
- 改成在已有 breakout / retest / EMA continuation 触发后，只把“结构未破坏 / 没有明显反向 rejection”当 veto 层。

但本轮**不把这刀写成 `Rank 3b`**，因为它已经不算 Rank 3 原表达下的诚实窄修正：
1. 这会把 `third-touch + EMA/MACD` 改写成一个更通用、甚至更弱角色的 shared filter；
2. 这条路的邻近版本已经被 `Rank 31 / 33 / 53` 与最新 `wick-veto` 证据大幅覆盖；
3. 若现在硬写 `Rank 3b`，更像是把结构确认家族换个名字继续续命，而不是提出真正新的单轴假设。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

理由：
- 原 `park` 的审计意义仍然很强：Rank 3 已经明确告诉我们，“把噪声切得很干净”不等于“形成可交易厚度”；
- 它没有留下一个未被消费、且足够集中的 blocker；
- 最自然的救法已经外溢到更通用的结构 gate / failure filter 分支，而这些旁支也没有给出足够干净的新证据；
- 再派生 `Rank 3b`，大概率只是重复结构确认家族已经做过的故事。

## 6) trade on / trade off 结论
本轮**不形成**新的 `Rank 3b`。

更诚实的保留口径是：
- `trade on` 的大故事不算完全错：更严格的结构确认，确实有时能减少假突破；
- 但 `trade off` 太大：它把样本和跨资产厚度压得过薄，导致策略层证据站不住；
- 因此当前更适合把 Rank 3 留作“结构确认会过度切样本”的反例证据，而不是继续写成待派生候选。

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `hard park`

## Minimal audit note
This round does **not** reopen Rank 3 itself.
It records that the most tempting rescue story — **demoting strict third-touch confirmation into a broader structure/failure filter** — is no longer a clean, unused salvage axis. Adjacent structure-confirmation evidence has already consumed most of that idea, while Rank 3's own blocker remains extreme sample thinness. So the honest action this round is to **keep Rank 3 parked**, not draft `Rank 3b`.

## Git
- 本轮只做最小必要文档改动；未做 commit。
- 原因：工作区存在大量无关脏文件与未跟踪文件，当前不适合安全地 selective commit。
