# 2026-03-18 08:36 UTC · Rank 31 park reframe review

## Scope
- Source rank: `Rank 31 chanlun-pro second-buy / breakout-retest continuation gate`
- Original verdict stays: `park / evidence pool`
- This round only asks: **should Rank 31 derive one narrower reframe hypothesis, without overturning the original park?**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- recent reframe logs:
  - `research/park_reframe/2026-03-18_0629_rank16-park-reframe.md`
  - `research/park_reframe/2026-03-18_0429_rank15-park-reframe.md`
  - `research/park_reframe/2026-03-18_0229_rank27-park-reframe.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_1057_rank31-clean-replication-park.md`
  - `research/quant_digests/2026-03-18_0654_chanlun-second-buy-structural-reclaim-gate.md`
  - `docs/TODO.md` latest Rank 50 / chanlun structural reclaim writeback

## Why this rank
- It is within `Rank 1~37` and currently parked.
- It has **not** been reviewed by `bot6` in the recent 7-day reframe queue.
- It had an obvious reframe temptation: reinterpret `二买/二卖` as a causal `higher-low / lower-high + reclaim` confirmation layer.
- But unlike a purely speculative salvage, this axis now already has nearby fresh evidence: the new digest framed it cleanly, and the adjacent implementation attempt (`Rank 50`) has already spent that exact rescue story once.

## 1) 原 rank 为什么 park？
Rank 31 被 park，不是因为“结构确认”这个方向毫无意义，而是因为当前最自然的两种结构写法都没有形成可升格 pocket。

原 clean replication 关键证据：
- `raw_pullback_recovery_baseline @ 6bps/side`：`mean_total_return≈-15.46%`，`positive_asset_ratio=1/3`
- `structural_higher_low_reclaim @ 6bps/side`：`≈-31.30%`，`positive_asset_ratio=0/3`，`mean_trades≈292.0`，`mean_false_reclaim_ratio≈35.04%`
- `center_breakout_retest_reclaim @ 6bps/side`：`≈-41.25%`，`positive_asset_ratio=0/3`

更直白地说：
- 原始 `pullback recovery` 已经不够好；
- 往“更结构化的 higher-low reclaim”走，结果反而更差；
- 再往“中枢 breakout-retest-reclaim”走，则更差；
- 所以原 rank 的 `park` 结论必须保留。

## 2) 它更像 hard park 还是 soft park？
**更像 `hard park`。**

原因不是它完全没故事，而是它最自然、最贴近源码语义的单轴近邻已经基本试过：
- 原 Rank 31 已经试了 `structural_higher_low_reclaim`；
- 最新 digest 又把同一个核心故事重新翻成更人话的 `higher-low / lower-high + reclaim` 确认层；
- 而板上最新 `Rank 50 / chanlun-pro structural reclaim gate` 的最小 clean replication 也已经把这条邻近救法再测了一次，结果仍是 `park / evidence pool`（主变体 `6bps≈-4.63%`、`positive_asset_ratio=0/3`、`mean_false_reclaim_ratio≈72.78%`、`mean_no_trade_ratio≈87.14%`）。

也就是说：
- 这条线不是“还没找到合理表达”；
- 更像是“最合理的单轴重写已经被新证据再次消费，仍没救活”。

## 3) 有没有“可救信号”？
**只有弱信号，没有足够诚实的可救信号。**

弱信号在于：
- `二买/二卖` 被翻译成 causal structural reclaim 后，研究叙事确实更清楚；
- 它也确实像一个可复用于 `Fib retest_hold / breakout follow-up / EMA-PSAR continuation` 的确认层。

但为什么仍不够：
- 这更像“故事更清楚了”，不是“结果已出现新 pocket”；
- Rank 31 原始结构版已经失败；
- 最新邻近重写 `Rank 50` 也已经失败；
- 所以当前没有新增证据支持“再派生一个 Rank 31b 会比已有失败近邻更诚实”。

## 4) 最值得改的唯一一刀是什么？
**当前没有值得再切的唯一一刀。**

表面上最像的一刀，就是：
- 把 `二买` 从缠论对象语言进一步压成更朴素的 `higher-low / reclaim` 结构确认。

但这刀事实上已经被消费：
- 原 Rank 31 试过 `structural_higher_low_reclaim`；
- 最新 digest + `Rank 50` 又把这条轴用更窄、更因果的方式重做了一遍；
- 新结果仍没形成足够诚实的 pocket。

所以如果这轮还要硬派生 `Rank 31b`，大概率只会变成：
- 再换一点 HTF gate
- 再换一点 timeout
- 再换一点 reclaim 定义

这已经开始滑向多轴小修补，不符合本轮只允许 **1 条唯一主修改轴** 的规则。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

理由：
- 原 rank 的 `park` 仍有明确审计意义；
- 当前最自然的 salvage axis 已被原 rank 自身与 `Rank 50` 这条邻近新证据基本消费；
- 再写新的 `Rank 31b`，更像重复包装已经失败过的 structural reclaim 近邻，不像真正新的窄 hypothesis。

## 6) trade on / trade off 结论
本轮**不形成**新的 `Rank 31b`。

更诚实的保留口径是：
- `trade on` 故事本身没有荒谬；
- 但真正的问题也不是“表达还不够漂亮”，而是最自然的 causal structural reclaim 写法已经两次没形成干净 pocket；
- 因此在出现新的外部证据前，不应继续把它包装成新的入板候选。

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `hard park`

## Minimal audit note
This round does **not** reopen Rank 31 itself.
It records that the most obvious salvage axis — reinterpreting `二买` as a narrow causal `structural reclaim` confirmation layer — has already been substantially consumed by adjacent evidence and still failed to produce an honest pocket. So the right action this round is to **keep Rank 31 parked**, not draft `Rank 31b`.

## Git
- 本轮只做最小必要文档改动；未做 commit。
- 原因：工作区可能仍有无关脏文件，当前不适合安全地 selective commit。
