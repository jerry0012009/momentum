# 2026-04-16 06:28 UTC · Rank 71 park reframe

## Selected rank
- `Rank 71`
- selection note: 按 `bot6` 当前默认优先级，本轮继续看 `50+` 号段；`Rank 71` 上次 park-reframe 复盘是 `2026-04-09 02:44 UTC`，已超过 `7` 天。其后又新增了 `2026-04-13` 的 `Wilder-RSI breakout × ADX/EMA regime × ATR trail` 与 `2026-04-14` 的 `daily-trend veto × technical-vote continuation` 两条趋势壳证据，足够重新回答：旧 `Rank 71` 的 residual 是不是值得再诚实派生，还是应继续维持 park。

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/park_reframe/2026-04-16_0418_rank4-park-reframe.md`
- `research/park_reframe/2026-04-16_0142_rank10-park-reframe.md`
- `research/park_reframe/2026-04-15_2310_rank73-park-reframe.md`
- `research/optimization_loop/2026-03-18_2326_rank71-source-intake.md`
- `research/optimization_loop/2026-03-18_2345_rank71-clean-replication-park.md`
- `research/optimization_loop/2026-04-11_0023_rank71_soft_reframe_first_verdict_background.md`
- `research/park_reframe/2026-04-09_0244_rank71-park-reframe.md`
- `research/quant_digests/2026-04-13_0558_wilder-rsi-adx-atr-shell-transfer-check.md`
- `research/quant_digests/2026-04-14_0140_dailyveto-technicalvote-shell.md`

## 1) 原 rank 为什么 park？
原 `Rank 71 / EMA-VWAP-ATR-volume graded admission score` 被 park，不是因为“高分完全没信息”，而是因为它只做到 **relative-better**，没有做到 **decisive post-cost edge**。

原 clean replication 的审计结论很清楚：
- `baseline` 明显为负；
- `score>=60` 只是少亏；
- `score>=75` 在 `6bps` 下接近打平，但主要伴随明显 retention 收缩；
- 到更诚实的 `10/15/20bps` 口径后整体又重新转负；
- bucket 也不干净：`60~74` 这一档反而比 `<60` 更差，说明“四档等权 graded score”本身不稳定。

因此，原 rank 被 park 的真实 blocker 不是“阈值还没调对”，而是：
> **把 EMA / VWAP / ATR / volume 叠成一个可扩展的 graded admission framework，这个写法本身没有被证明足够诚实。**

## 2) 它更像 hard park 还是 soft park？
**本轮判断：仍是 `soft park`，但比 2026-04-09 那轮更接近 hard。**

为什么还保留 soft：
- 原 clean replication 至少说明极高共振桶比 baseline 更像 continuation，说明这组信息并非全噪音；
- 主题层面，趋势 readiness / context 仍有价值。

为什么又更接近 hard：
- `2026-04-11` 对它的 `extreme-only binary gate / re-veto` fresh intake 首判已经收口为 `background / P0`；
- 说明它唯一自然 residual 不但已被表达，还已经被 runtime truth 消费；
- 4 月 13~14 的新增证据也没有把它重新拉回“旧 Rank 71 可继续窄救”的轨道，而是继续把这类信息上移到更完整的 `trend shell / daily veto shell` 宿主。

## 3) 有没有“可救信号”？
**有，但现在更像主题级可救信号，不再是旧 `Rank 71` 级可救信号。**

### 可救信号 A：趋势 readiness 主题仍活
`2026-04-13_0558_wilder-rsi-adx-atr-shell-transfer-check.md` 说明，`RSI / ADX / EMA / ATR / volume` 这组变量仍可能在完整趋势壳里形成正的 continuation 语义。

### 可救信号 B：真正有用的是更上位的 veto / shell
`2026-04-14_0140_dailyveto-technicalvote-shell.md` 更直接：Binance 迁移版的 survival 几乎全靠 `daily-trend veto` 保住。也就是说，真正有价值的不是“继续把 15m 上下文打成四档分数”，而是把这些组件放回一个更完整的 `daily-veto + technical-vote continuation shell`。

### 但这不是旧 Rank 71 的可救方式
这些新证据共同支持的是：
- `EMA / VWAP / ATR / volume` 更像 **trend-shell 里的 context / readiness / veto 组件**；
- 不像旧 `Rank 71` 那种可独立占一个 queue-facing 位置的 graded score 框架。

## 4) 最值得改的唯一一刀是什么？
**如果硬要保留唯一一刀，它仍然只可能是：把 graded score 收窄成 `extreme-only binary gate / veto`。**

但关键是：
- 这条唯一修改轴已经在 `2026-04-09_0244_rank71-park-reframe.md` 被提出；
- 又在 `2026-04-11_0023_rank71_soft_reframe_first_verdict_background.md` 被 fresh intake 首判收口为 `background / P0`；
- 所以它不再是“等待 bot6 再次 draft 的新单轴”，而是 **已经被消费、并被证明只够 cheap residual 的旧单轴**。

换句话说：
> 旧 `Rank 71` 当前最值得保留的唯一一刀，没有新增；它仍只是已被消费的 `extreme-only binary gate / veto`。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

理由：
1. 原 `park` blocker 没被推翻；
2. 唯一自然 residual 已经被明确写成 `extreme-only` 改写，并在 `2026-04-11` runtime 首判中收口为 `background / P0`；
3. 4 月 13~14 新证据继续说明，若这组变量还有信息，更应该迁移到新的 `trend-shell / daily-veto shell` 宿主，而不是继续扩写旧 `Rank 71`；
4. 现在再写 `Rank 71b` 或 `Rank 71c`，本质上只会是把已失败的 readiness gate 换个阈值、再包装一次，不够诚实。

## 6) trade on / trade off 怎么读？
本轮不新增派生，只保留审计式复述：

- `trade on`：
  - 承认 `EMA / VWAP / ATR / volume` 这组变量仍有趋势 readiness 信息；
  - 但它们更适合作为完整趋势壳内的 context / veto / admission 组件。
- `trade off`：
  - 放弃继续把旧 `Rank 71` 写成 queue-facing 的 graded score / binary gate 对象；
  - 接受它的 residual 已被消费，后续若再追，应该是新的 shell，不是旧 rank 续命。

## Final verdict
- `verdict`: `keep_park`
- `original_verdict_kept`: `park`
- `park_type_read`: `soft park，但已接近 hard with consumed residual`
- short note: `原 EMA-VWAP-ATR-volume graded admission score 的 blocker 没被推翻；唯一诚实 residual（extreme-only binary gate / veto）已在 2026-04-11 fresh intake 首判收口为 background / P0。4 月 13~14 新证据继续说明这组变量若还有信息，更像新的 trend-shell / daily-veto shell 宿主，而不是足以再诚实派生旧 Rank 71。`

## Minimal audit note
本轮没有推翻原 `park`，也没有改 `TODO`。只是把边界进一步说硬：
- 主题还活；
- 旧 `Rank 71` 这具 graded/readiness gate 壳子已经基本消费完毕；
- 后续若再追，应在新的趋势壳名下追，不应继续以 `Rank 71b/c` 的形式续命。

## Git
- 未做 commit。
- 原因：工作区存在共享脏文件；本轮只做最小必要文档更新与邮件交付，避免混提。
