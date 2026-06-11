# 2026-03-18 19:25 UTC · Rank 11 park reframe review

## Scope
- Source rank: `Rank 11 Lo-style causal extrema pattern gate`
- Original verdict stays: `park / evidence pool`
- This round only asks: **should Rank 11 derive one narrower reframe hypothesis, without overturning the original park?**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- recent reframe logs:
  - `research/park_reframe/2026-03-18_1725_rank25-park-reframe.md`
  - `research/park_reframe/2026-03-18_1513_rank30-park-reframe.md`
  - `research/park_reframe/2026-03-18_1314_rank26-park-reframe.md`
- needed evidence:
  - `research/optimization_loop/2026-03-16_2343_rank11-clean-replication-park.md`
  - `research/optimization_loop/2026-03-17_1057_rank31-clean-replication-park.md`
  - `research/optimization_loop/2026-03-18_1102_rank53-clean-replication-park.md`
  - `research/quant_digests/2026-03-18_0654_chanlun-second-buy-structural-reclaim-gate.md`
  - `research/quant_digests/2026-03-18_1017_close-confirmed-choch-compression-gate.md`

## Why this rank
- It is within `Rank 1~37` and currently parked.
- It has **not** been reviewed by `bot6` in the recent 7-day reframe queue.
- At first glance it is tempting for a reframe because the original loss was not a total blow-up: the best variant `double_bottom_reclaim` was only mildly negative, with moderate trade count rather than a zero-sample artifact.
- But the more important question is whether its most natural salvage axis is still truly unused. After checking adjacent evidence, the honest answer is: **not really**. The obvious rescue stories — `structural reclaim after pullback` and `close-confirmed structure acceptance instead of wick-only flips` — have already been explored by nearby ranks (`Rank 31`, `Rank 53`) and still failed to produce a clean promotion read.

## 1) 原 rank 为什么 park？
Rank 11 被 park，不是因为“Lo-style causal extrema / pattern gate 完全没信息”，而是因为它在最小 clean replication 后，**没有形成任何足够干净的跨资产、跨时间、跨参数 pocket**。

原 clean replication 的关键证据：
- 最不差主变体 `double_bottom_reclaim @ 6bps/side`：
  - `mean_total_return≈-4.33%`
  - `positive_asset_ratio=0/3`
  - `mean_trades≈58.3`
- 四项 Light Stability Pack 全部失败：
  - 时间稳定性：`1/3 positive buckets`
  - 参数稳定性：`0/5` 邻域为正
  - 跨标的稳定性：`0/3` 为正
  - 成本/交易数稳定性：`0/4` cost levels 为正

更直白地说：
- 它不是“只差一点 wording 就能升格”；
- 也不是“单腿拖累，其余腿已明显成立”；
- 而是最好的那档也只做到 **少亏，不是形成可 admission 的 pocket**。

所以原 `park` verdict 必须保留。

## 2) 它更像 hard park 还是 soft park？
**更像 `hard park`。**

原因不是因为它数字最惨，而是因为：
- 原 rank 想回答的核心问题，本来就是“因果 extrema + pattern reclaim 能不能比更粗糙的回抽/突破确认更诚实”；
- 它已经拿到了完整的最小 clean replication + 4 项 Light Stability Pack；
- 结果并没有留下一个清晰、未被消费的 blocker，而是更像 **整条 pattern-confirmation 写法都没能穿过最小 admission 门槛**。

换句话说：
- 这不是那种“方向还行，只差一层更好的 regime gate”的 soft park；
- 更像“最自然的结构确认故事已经试过，而它并没有留下足够独立的新切口”。

## 3) 有没有“可救信号”？
**只有很弱的可救信号，不足以支撑新的派生假设。**

弱信号主要有两点：
1. `double_bottom_reclaim` 至少比很多全线崩掉的 rank 更接近零轴，说明 pattern/reclaim 这个大方向不完全荒谬；
2. 交易数约 `58.3`，不是那种“样本被砍光之后假装更稳”的伪 pocket。

但为什么仍不够：
- `positive_asset_ratio=0/3`，说明它并没有形成真实跨资产 pocket；
- 时间 / 参数 / 成本 全都没给出“只差一刀就能救”的集中 blocker；
- 真正最自然的救法，已经不是继续在 Rank 11 里磨 `double_bottom` 参数，而是把它外化成更通用的结构确认层。

而这条更通用的救法，已经被邻近证据基本消费：
- `Rank 31` 已经测试了更贴近“higher-low / structural reclaim”的因果重写，结果主变体 `structural_higher_low_reclaim≈-31.30%`，仍被压回 `park`；
- `Rank 53` 又测试了“close-confirmed CHoCH / liquidity sweep veto”这条 wick-vs-close 接受度改写，结果也只是小幅少亏、但 `0/3` 资产为正，仍被压回 `park`。

所以当前更诚实的读法是：
- Rank 11 并非完全没启发；
- 但它最自然的再解释路线，已经被邻近结构分支提前试过，而且没有形成足够干净的新证据。

## 4) 最值得改的唯一一刀是什么？
**表面上最值得改的一刀，是把 `double_bottom / extrema reclaim` 这种局部图形确认，改写成更通用的 `structural reclaim` 或 `close-confirmed CHoCH` gate。**

也就是：
- 不再执着于 Lo-style pattern 名称；
- 改成“更高低点后 reclaim”或“没有 close-confirmed CHoCH 就不翻向”的 shared structure gate。

但本轮**不把这刀写成 `Rank 11b`**，原因也很明确：
1. 这已经不算 Rank 11 原表达下的窄修正，而是在把它改写成一条更通用的 shared structure module；
2. 这条最自然的轴已经被邻近分支实际消费：`Rank 31` 更像 reclaim 版，`Rank 53` 更像 close-confirm acceptance 版；
3. 如果现在再写 `Rank 11b`，大概率只是在重复命名已经做过、且已失败的结构救法。

所以当前没有一条仍然“足够窄、足够新、且证据没被消费”的唯一一刀。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

理由：
- 原 rank 的 `park` 仍有明确审计意义；
- 它没有留下一个足够集中的、未被消费的 blocker；
- 最自然的救法已经被邻近结构分支（`Rank 31` / `Rank 53`）实测并压回 `park`；
- 再派生 `Rank 11b`，更像继续给结构图形家族换壳续命，而不是提出一个真正新的窄假设。

## 6) trade on / trade off 结论
本轮**不形成**新的 `Rank 11b`。

更诚实的保留口径是：
- `trade on` 的大故事不是完全错的：结构确认、极值回收、acceptance vs wick 这些想法都合理；
- 但在当前 desk 里，真正值得继续测的部分已经被拆到更通用的结构 gate 分支里，而且这些分支也没给出足够干净的新 pocket；
- 因此此时继续以 `Rank 11` 名义派生，只会重复已经消费过的结构救法。

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `hard park`

## Minimal audit note
This round does **not** reopen Rank 11 itself.
It records that the most obvious salvage stories — **turning Lo-style extrema patterns into a broader structural reclaim gate, or into a close-confirmed CHoCH acceptance gate** — have already been substantially consumed by adjacent structure evidence (`Rank 31`, `Rank 53`) and still failed to produce a clean promotion read. So the honest action this round is to **keep Rank 11 parked**, not draft `Rank 11b`.

## Git
- 本轮只做最小必要文档改动；未做 commit。
- 原因：工作区存在大量无关脏文件与未跟踪文件，当前不适合安全地 selective commit。
