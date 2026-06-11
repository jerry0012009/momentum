# 2026-04-06 06:06 UTC · Rank 27 park-reframe (bot6)

## 本轮对象
- 选定：`Rank 27 / Mt.Gox neckline confirmation / pattern-complete breakout gate`
- 本轮结论：`derived_hypothesis_drafted`
- 原 verdict 保留：`park`
- 7 天去重：上次复盘 `Rank 27` 是 `2026-03-23 11:15 UTC`，已超过 7 天；且这轮有新的外部证据可看，不属于无新意重刷。

## 为什么这轮看它
- 按本 loop 约束，这轮只处理 1 条已 park rank。
- `Rank 27` 属于 `Rank 25~37` 区间里较久未复盘、且最近刚出现**同主题新证据**的一条。
- 关键新增证据是：
  - `research/quant_digests/2026-04-05_1701_chartpattern-neckline-imbalance-alpha.md`
- 这条新 digest 没有推翻原审计结论，但它确实给出了一条此前没被明确写成 queue 提案的**单轴重写**：
  - 不再把 post-break `retest_hold` 当主确认；
  - 改为在 **neckline 有效突破当下**，用**方向一致的 taker-imbalance**做 confirmation。

## 原 Rank 为什么 park
原始 clean replication（`2026-03-17_0815_rank27-mtgox-neckline-clean-replication.md`）已经把 blocker 说得很清楚：
- `raw_breakout`：`mean_total_return≈-13.79%`，`positive_asset_ratio=0/3`，`mean_false_break_ratio≈71.56%`
- `neckline_confirm`：`mean_total_return≈-17.42%`，`positive_asset_ratio=0/3`，`mean_false_break_ratio≈62.50%`
- `neckline_confirm_plus_retest_hold`：`mean_total_return≈-3.03%`，`positive_asset_ratio=0/3`，`mean_false_break_ratio≈68.67%`

因此原 Rank 27 被 park，不是因为“neckline breakout 主题完全没信息”，而是因为：
1. 直接 breakout 太容易假突破；
2. 原版 `neckline_confirm` 虽略减假突破，但收益更差；
3. `retest_hold` 虽明显缩窄亏损，却没有把对象救到跨资产、成本后可保留的程度。

换句话说，原 rank 的真正问题更像是：**confirmation 写法不对，且 `retest_hold` 这条确认思路本身也不够强。**

## 它更像 hard park 还是 soft park
- 本轮判断：**soft park**。

理由：
- 原对象并非完全无 residual value；
- `Rank 27b` 已证明“确认层重写”确实能改善一些假突破读法，只是还不够救活；
- 最新 2026-04-05 证据又进一步说明，**neckline breakout 本体仍可成立，但 confirmation 可能应该从价格回踩，改成 order-flow 同向确认**。

所以它不是 hard park；但也绝不是“原 rank 快活了”，而是：
- 原审计结论继续保留；
- 只是还有一条未被正式 queue 化的、相对诚实的窄派生可写。

## 有没有“可救信号”
有，而且这次的可救信号与上次不同。

### 已被消费过的可救信号
- 既有 `Rank 27b` 已经消费了第一条自然 rescue：
  - `binary retest_hold -> ATR-scaled retest zone + bounce reclaim`
- 这条轴改善了 false-break 读法，但没有形成足够厚的 after-cost pocket。

### 这轮新增的可救信号
- `2026-04-05_1701_chartpattern-neckline-imbalance-alpha.md` 给出的新增价值是：
  - 对 double-bottom / double-top 这类程序化形态，**最值得优先测的不是 post-break 回踩美学，而是 breakout 当下的 taker-imbalance confirmation**；
  - 论文与 digest 的主语仍是 `chart pattern -> neckline breakout`，因此没有完全漂移到不相干的新 family；
  - confirmation 角色从“等回踩成立”改成“突破时就看主动成交是否同向”，这在语义上仍然是对原 Rank 27 的**确认层单轴改写**。

## 最值得改的唯一一刀是什么
本轮唯一值得写的一刀是：

> **把 Rank 27 的确认层，从 post-break `retest_hold / bounce reclaim` 改成 breakout-bar taker-imbalance confirmation。**

更直白地说：
- 保留 `double bottom / double top + neckline breakout` 这个主语；
- 不再把“回踩不破”当 primary confirmation；
- 改为只在 `neckline break` 发生时，要求同方向 taker flow 也同步显著偏向该方向。

这是一条单轴修改，因为它只改**confirmation modality**，不顺手改：
- pattern 定义
- holding window
- exit
- 多层 regime
- second-layer score

## 是否值得形成新的 derived hypothesis
- 结论：**值得。**
- 本轮状态：`derived_hypothesis_drafted`

理由：
1. 这次新增证据与 `Rank 27` 主语高度同源，仍然是 `chart-pattern neckline breakout`；
2. 它不是在 `27b` 上继续加第二层过滤，而是提出另一条**彼此独立的确认层替换轴**；
3. 相比再往 `27b` 上叠 `phase / score / polarity / VWAP`，这条 order-flow confirmation 更干净、更像一个 bot2 可直接判断是否入板的窄提案；
4. 它也不推翻历史：原 Rank 27 仍然是被 park 的，新的只是 `Rank 27c` 这条 queue-only 派生。

## Drafted derived hypothesis
- proposed_rank: `Rank 27c`
- source_rank: `Rank 27`
- status: `derived_hypothesis_drafted`
- single modification axis: `replace post-break retest confirmation with breakout-bar taker-imbalance confirmation on neckline break`
- trade on:
  - 保留 `double bottom / double top` 的程序化 pattern-complete 与 `neckline breakout` 作为主语；
  - 当 breakout bar 收盘有效穿越 neckline 时，不再等待 `retest_hold`；
  - 只在 breakout 方向与同 bar 的 taker-imbalance 同向且超过最小阈值时放行入场；
  - 第一轮优先 strict A/B：`raw breakout` vs `neckline confirm` vs `neckline breakout + taker-imbalance confirm`；不偷带 retest、ATR zone、VWAP、second-layer regime。
- trade off:
  - 放弃“post-break retest 才更诚实”的旧确认思路，换取更贴近论文新证据的 order-flow confirmation；
  - 代价是它会把对象从更慢、更价形态美学的确认，改成更即时的 flow-confirmed breakout；若阈值过严，也可能只是靠砍单美化，因此第一轮必须报告 trade retention 与 false-break 变化。
- why now:
  - 原 Rank 27 与既有 `Rank 27b` 都说明“确认层写法”才是主要 blocker，而不是 neckline breakout 主题彻底无效；
  - `2026-04-05` 新 digest 又给出同主题但不同于 retest 的新 confirmation 线索：`double-bottom/top neckline breakout × taker-imbalance confirmation`；
  - 因此现在值得把它收敛成一条新的、单轴的 queue-only 窄派生，而不是继续只围着 `27b` 做实现细化。
- suggested initial state: `source intake / clean replication next`

## 本轮最终判断
- 原 rank 为什么 park：因为 raw breakout 太假、原 neckline confirm 更差、retest_hold 只减亏但没救活。
- 它更像 hard 还是 soft park：`soft park`。
- 有没有可救信号：有，新的可救信号是 **neckline breakout × taker-imbalance confirmation**。
- 最值得改的唯一一刀：**把确认层改成 breakout-bar order-flow confirmation，而不是 post-break retest。**
- 是否值得形成新的 derived hypothesis：**值得，draft `Rank 27c`。**

## 对 bot2 / bot3 的含义
- 不改 `docs/TODO.md` 顶部排班。
- 不直接分配新任务。
- 仅把 `Rank 27c` 写入 `docs/PARK_REFRAME_QUEUE.md`，作为 bot2 在 fresh intake 不足时可择优判断是否入板的短提案。

## 本轮产出
- 新日志：`research/park_reframe/2026-04-06_0606_rank27-park-reframe.md`
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`
