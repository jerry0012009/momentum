# 2026-04-11 21:00 UTC · Rank 18 park reframe review

## Scope
- Source rank: `Rank 18 / EMA neighborhood consensus / plateau-stable crossover`
- Original authoritative verdict stays: `park / evidence pool`
- This round only asks: **在不推翻原 park 的前提下，经历 2026-04-09 对既有派生 `Rank 18b` 的 runtime 收口后，旧 Rank 18 是否还值得再派生一个新的窄 reframe hypothesis。**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_0309_rank18-clean-replication-park.md`
  - `research/park_reframe/2026-03-21_1815_rank18-park-reframe.md`
  - `research/park_reframe/2026-04-02_0246_rank18-park-reframe.md`
  - `research/optimization_loop/2026-04-09_0429_rank18_stale_pending_duplicate_blocked.md`
  - `research/optimization_loop/2026-04-09_1537_rank18b_fresh_intake_background_shared_overlay.md`

## Why this rank this round
- `Rank 18` 属于 `Rank 1~24`，且距离上次 bot6 复盘（`2026-04-02 02:46 UTC`）已超过 7 天。
- 它之前已有唯一诚实窄派生：`Rank 18b = shared abstain / trend-readiness veto gate`。
- 但 2026-04-09 又出现了一条更关键的新 runtime truth：
  1. 旧 `Rank 18` 被判定为 `stale duplicate blocked`，不能再被当成新的 fresh intake 重开；
  2. 既有派生 `Rank 18b` 的 fresh intake first verdict 也已正式收口为 `background / P0`。
- 因此这轮最该回答的，不是“还能不能再讲一个新故事”，而是：**这条线是否已经从 soft park 进一步向 hard park 靠，足以停止再切 `Rank 18c`。**

---

## 1) 原 rank 为什么 park？
原 `Rank 18` 被 park 的原因没有变化，而且依然很硬。

来自 clean replication 的核心结果：
- `plateau_vote_5of9_spread_guard @ 6bps/side`：`mean_total_return ≈ -19.89%`
- `positive_asset_ratio = 0/3`
- `mean_trades ≈ 157`
- `mean_no_trade_ratio ≈ 68.48%`
- 成本梯度 `10/15/20bps` 继续恶化：约 `-29.36% / -39.63% / -48.42%`
- 参数邻域没有出现由负转正的平台稳定证据

翻成人话：
- `EMA 邻域平台共识` 当成 **standalone entry alpha** 这条路已经被审计清楚：不是“差一点”，而是全资产、跨成本都不成立。
- 所以原 `park` verdict 的审计意义必须保留，不能被后续 reframe 语言覆盖掉。

## 2) 它更像 hard park 还是 soft park？
**本轮结论：仍是 `soft park`，但已经比 4 月 2 日那轮更接近 `hard park`。**

为什么还不是纯 hard：
- 原 clean replication 里，`plateau_vote_5of9_spread_guard` 相比更粗的 `anchor_10_40` 仍然少亏不少；
- 这说明“EMA 共识不足时少做/不做”这件事不是完全没信息量。

为什么现在更接近 hard：
- 这点残余信息早已被压缩成唯一诚实窄轴：`Rank 18b`；
- 而 `2026-04-09` 的更晚 runtime truth 又明确说明：`Rank 18b` 并没有长成新的 queue-facing pocket，只是既有 `no-trade / trend-readiness / veto` shared overlay family 的一个宿主实例，first verdict 直接收口为 `background / P0`；
- 这意味着 Rank 18 留下的那点 residual，已经不只是不够新，而且连“作为独立派生对象”都站不住。

## 3) 现有证据里是否存在“可救信号”？
**有，但只够保留审计式 residual note，不足以再派生新的 `Rank 18c`。**

仅存的可救信号是：
- `Rank 18` 的高 `no_trade_ratio` 与较少亏损，说明它更像在表达“哪些时候不该做”，而不是“何时该直接开仓”；
- 这也是为什么此前能诚实收敛出 `Rank 18b`。

但 4 月 9 日之后，这个可救信号已经进一步被证明：
- **它只够当 shared overlay family 的一个实现例子；**
- **不够形成新的独立 lane、独立宿主、或独立 honesty blocker。**

所以现在的可救信号，更像“别忘了原 rank 的 residual 是 veto/readiness 语义”，而不是“值得继续 draft 新对象”。

## 4) 最值得改的唯一一刀是什么？
**唯一最值得改的一刀没有变化，仍然只是既有 `Rank 18b`：把 standalone EMA plateau-consensus entry 降级成 shared abstain / trend-readiness veto gate。**

也就是说：
- 不再让 `Rank 18` 自己触发 entry；
- 只在其他 setup 触发时，用 plateau consensus 做 `allow / veto`；
- 不偷带 bubble-state、breakout trigger、new exit、new universe 等第二轴。

而本轮最关键的新判断是：
- **这唯一一刀已经被 4 月 9 日的 runtime truth 审计过，且结果只是 `background / P0`；**
- 所以现在再去切 `Rank 18c`，本质上会变成重复包装同一 residual，或滑向多轴大改。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

更精确地说：
- 原 `Rank 18` 的 `park` 保持；
- 既有 `Rank 18b` 继续保留为历史 residual 记录；
- 但 `Rank 18b` 已在 2026-04-09 被 first verdict 收口为 `background / P0`，因此当前不诚实再 draft `Rank 18c`。

## 6) trade on / trade off 如何写？
本轮不新增派生，因此只做审计式复述：

- `trade on`：
  - 如果未来还要引用 Rank 18 的残余价值，最诚实的读法仍是：EMA plateau-consensus 只负责提示“趋势尚未 ready / 这段更该 abstain”，不负责 standalone 开仓。
- `trade off`：
  - 这类改写天然会降低 trade density；
  - 很容易退化成“砍单美化”；
  - 更重要的是，`2026-04-09` 已证明这种 residual 即使写成 `Rank 18b`，也仍会被现有 shared overlay family 吸收，缺乏独立 front-slot 价值。

---

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park，但已比 4 月初更接近 hard park`

## Minimal audit note
本轮新增的 decisive runtime truth 不是“Rank 18 有新救法”，而是相反：**原 rank 的唯一诚实 residual 已经被既有 `Rank 18b` 完整表达，而 `Rank 18b` 本身又在 2026-04-09 的 first verdict 中收口为 `background / P0`。** 因此当前不诚实再派生 `Rank 18c`；更好的记录方式是继续保留原 `park`，并把这条线读成已被 shared overlay family 吸收的 residual。

## Git
- 本轮只做最小必要文档改动：本日志、`research/park_reframe/INDEX.md`、`docs/PARK_REFRAME_QUEUE.md`
- 默认不改 `docs/TODO.md`
- 本轮未做 git commit；保持 selective write only
