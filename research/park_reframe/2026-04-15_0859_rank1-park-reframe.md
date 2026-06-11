# 2026-04-15 08:59 UTC · Rank 1 park reframe

## Selected rank
- `Rank 1`
- selection note: 本轮严格按用户给定范围只看 `Rank 1~37` 的已 `park` 条目；而 `25~37` 号段大多在最近 7 天已复盘，因此回到 `1~24`。`Rank 1` 上次 bot6 复盘是 `2026-04-08 11:24 UTC`，已超过 7 天，且适合再次确认：原 `τ-band` 宿主是否还有新的、仍属于它自己的窄 reframe 空间。

## Original park reason
原 `Rank 1 / τ-band / no-trade breakout filter` 被 park 的原因没有变化：
- 它最多证明“breakout 后需要额外确认，比 raw breakout 少亏”；
- 但没证明 `static τ-band` 本身是一个足以独立继续前推的 alpha。

原始关键证据：
- `2026-03-16_0355_tau-band-first-verdict.md`
- `2026-03-16_0912_scout-rank1-honest-recheck.md`

冻结口径下（`BTC/ETH/SOL | 120d | 15m | 6bps/side`）：
- `confirm2of3_tau_010` 相对 `raw_breakout` 的确少亏、假突破率更低；
- 但 honest recheck 后仍是 `mean_total_return ≈ -11.16%`、`positive_asset_ratio = 0/3`；
- 因此它只够算 `execution guard / scout follow-up`，不够算 replace-ready winner。

翻成人话：
**原 Rank 1 失败的不是 breakout 主题整体，而是“拿 static τ-band 去充当 breakout 的 standalone rescue”这件事。**

## Hard park or soft park?
- 本轮判断：`soft park，但对原 Rank 1 本体已接近 hard with consumed residual`

为什么仍保留 soft：
- breakout 后 persistence / outside-confirm 这层语义本身曾经留下过诚实 residual。

为什么又更接近 hard：
- 这条 residual 早已被写成 `Rank 1b`；
- 随后又被运行态里的 `Rank 94 / two-bar outside-range follow-through gate` 同题吸收；
- `Rank 94` 自己也已 clean replication 后重新压回 `park`。

也就是说：
**原 Rank 1 不是完全没留信息，而是唯一留得住的信息已经被完整消费过。**

## Any salvage signal?
有，但仍是旧信号，不是新的可救轴。

唯一站得住的可救信号仍然只是：
- `static tau-band` → `two-stage outside-persistence continuation gate`

但这条线已经经历：
1. `2026-03-20` park-reframe draft 成 `Rank 1b`
2. `2026-03-30` runtime 明确记账：被 `Rank 94` 同题吸收
3. `2026-04-09` 再次被 runtime truth 写死：`Rank 1b` 已是 stale duplicate，不能重新当前排 intake

所以本轮的结论不是“没有 residual”，而是：
**唯一 residual 已被完整表达、执行并再度关闭。**

## Single best cut
若只谈原 `Rank 1` 最值得改的唯一一刀，它仍然是：

**把 `static τ-band breakout confirmation` 改写成 `two-stage outside-persistence continuation gate`。**

但这刀已经不再是本轮可新增的东西：
- 它不是新发现；
- 也不是尚未消费的空间；
- 继续写 `Rank 1c` 只会重复 `Rank 1b -> Rank 94` 已经审计过的对象边界。

## Is a new derived hypothesis warranted?
- 结论：`keep_park`
- 不形成新的 `derived hypothesis`

原因：
1. 原 `park` 结论没有被推翻；
2. 唯一诚实 residual 已被 `Rank 1b -> Rank 94` 这条链完整消费；
3. 后续 breakout 主题若还有价值，更像新的 `fresh-high / recency-state` raw-alpha 宿主，而不是旧 `τ-band` rank 的再救援；
4. 现在再 draft `Rank 1c`，要么只是重复旧 residual，要么就是偷换到新的宿主，不诚实。

## Final verdict
- `verdict`: `keep_park`
- `original_verdict_kept`: `park`
- `one-line note`: `soft park，但对原 static τ-band 读法已接近 hard with consumed residual；唯一诚实 residual 仍只到既有 Rank 1b，并已被 Rank 94 同题吸收后再次压回 park，因此当前不诚实再派生 Rank 1c。`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## Commit
- 本轮默认不做 commit。
- 原因：只做最小必要文档改动；且仓库长期存在无关脏文件，避免混提。
