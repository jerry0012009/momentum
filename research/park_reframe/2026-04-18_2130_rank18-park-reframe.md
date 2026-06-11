# 2026-04-18 21:30 UTC · Rank 18 park reframe revisit

## Selected rank
- `Rank 18`
- selection note: 仍限定在 `Rank 1~37` 已 `park` 条目内；`Rank 18` 上次 bot6 复盘为 `2026-04-11 21:00 UTC`，已超过 `7` 天窗口，且 4 月中旬又新增了更贴近“trend shell / state gate 迁移”的证据，适合做一次低频复核。

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- recent park-reframe context:
  - `research/park_reframe/2026-04-18_1823_rank26-park-reframe.md`
  - `research/park_reframe/2026-04-18_1606_rank72-park-reframe.md`
  - `research/park_reframe/2026-04-18_1117_rank34-park-reframe.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_0309_rank18-clean-replication-park.md`
  - `research/park_reframe/2026-04-11_2100_rank18-park-reframe.md`
  - `research/optimization_loop/2026-04-09_1537_rank18b_fresh_intake_background_shared_overlay.md`
  - `research/quant_digests/2026-04-16_0454_bubblestate-ma-cross-trend-alpha.md`
  - `research/quant_digests/2026-04-18_0431_rsi-breakout-trend-shell.md`

## 1) 原 rank 为什么 park？
原 `Rank 18` 被 park 的核心原因没有变化：它把 **EMA 邻域平台共识** 写成了 standalone entry alpha，但 clean replication 很清楚地显示这条线不只是“差一点”，而是跨资产、跨成本都不过线。

关键结果仍然成立：
- `plateau_vote_5of9_spread_guard @ 6bps/side ≈ -19.89%`
- `positive_asset_ratio = 0/3`
- `mean_trades ≈ 157`
- `mean_no_trade_ratio ≈ 68.48%`
- `10/15/20bps` 成本梯度继续恶化：约 `-29.36% / -39.63% / -48.42%`

所以原 `park` 的审计含义必须保留：
**失败的是“EMA plateau-consensus 可以直接负责开仓”这层职责，不是 trend-readiness / abstain 信息完全不存在。**

## 2) 它更像 hard park 还是 soft park？
**本轮仍判断为 `soft park`，但比 4 月 11 日那轮更接近 `hard park with consumed residual`。**

为什么还保留 soft：
- 原线相较更粗的 `anchor_10_40` 版本，确实表现出“少做一点会少亏很多”；
- 说明它仍有弱的 `abstain / readiness` 残余信息。

为什么更接近 hard：
1. 这条残余早已被唯一诚实的一刀收敛成既有 `Rank 18b`；
2. `Rank 18b` 又已在 `2026-04-09` fresh intake first verdict 中收口为 `background / P0`；
3. 4 月中旬新增证据继续说明：trend-readiness 信息若还有价值，更像挂在完整 trend shell / raw-alpha 宿主上，而不是继续从 old `Rank 18` 切出新编号。

## 3) 有没有“可救信号”？
**有残余，但没有新的可救信号；唯一 residual 仍只到既有 `Rank 18b`。**

仍可保留的残余是：
- `EMA plateau-consensus` 更像在表达“当前趋势还没 ready / 这段更该 abstain”；
- 不像“已经到了可直接 next-bar open 入场”的主触发。

但本轮重读 4 月中旬新证据后，方向反而更清楚：
- `2026-04-16 bubble-state × MA trend alpha` 说明 state 信息更适合服务明确的 MA trend 主壳；
- `2026-04-18 RSI breakout trend shell` 说明 readiness / filter / confirmation 信息更自然地挂在完整 trend shell 上，而不是自己当独立 setup。

换句话说，这些新证据不是在救 old `Rank 18`，而是在继续把它的残余上移到**更完整的新宿主**。

## 4) 最值得改的唯一一刀是什么？
**唯一最值得改的一刀仍然没有变化：既有 `Rank 18b`。**

> `demote standalone EMA plateau-consensus entry into a shared abstain / trend-readiness veto gate`

也就是：
- 不再让 `Rank 18` 自己负责触发 entry；
- 只在别的 base setup 已触发时，用 plateau-consensus 做 `allow / veto / abstain`；
- 第一刀只测 `baseline vs abstain-only gate`，不偷带 bubble-state、ADX、new exit、new universe 等第二轴。

本轮没有比这更诚实的新一刀；若再往外扩，基本都会落入：
- 同义改写 `18b`；或
- 偷带第二轴去硬讲新故事。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。最终结论：`keep_park`。**

更精确地说：
- 原 `Rank 18 = park` 的审计意义保持不变；
- 既有 `Rank 18b` 继续是旧 rank 唯一诚实 residual；
- 本轮没有形成新的 `Rank 18c`。

## 6) trade on / trade off（审计式说明）
本轮不新增派生，只保留审计说明。

### trade on
- 若将来还要保留 `Rank 18` 的残余价值，更诚实的做法仍然只是：把 `EMA plateau-consensus` 降级成 `shared abstain / trend-readiness veto`，服务更清楚的 trend shell / breakout shell / continuation setup。

### trade off
- 它不再是 standalone gate / standalone alpha；
- 它很容易退化成“砍单美化”；
- 且 `2026-04-09` 已证明这条 residual 即使被写成 `Rank 18b`，也仍只够作为 shared overlay family 的一个实例，不足以再占新的 queue-facing 槽位。

---

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park，但已比 4 月 11 日那轮更接近 hard park with consumed residual`

## Minimal audit note
本轮不推翻 `Rank 18` 的原 park，也不新增 `Rank 18c`。更诚实的记录是：**旧线唯一诚实残余仍只是既有 `Rank 18b`；而 4 月中旬新增的 bubble-state / RSI breakout trend-shell 证据继续说明，这类 readiness 信息若还有价值，更像完整 trend shell / raw-alpha 宿主的一部分，而不是足以再诚实派生旧 `Rank 18`。**

## Git
- git 工作区存在大量与本轮无关脏文件；本轮只做最小必要文档改动，不做 selective commit，避免混提。
