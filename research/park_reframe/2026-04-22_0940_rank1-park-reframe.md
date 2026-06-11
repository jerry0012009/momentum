# 2026-04-22 09:40 UTC · Rank 1 park reframe revisit

## Selected rank
- `Rank 1`
- selection note: 本轮严格限定在 `Rank 1~37` 的已 `park` 条目内；`Rank 2 / Rank 17` 虽在号段里，但当前属于存活 lane，不是 parked 对象。`Rank 1` 上次 bot6 复盘是 `2026-04-15 08:59 UTC`，这次刚好越过默认 `7` 天回避窗口；同时 4 月 19~22 又新增了几条 breakout / continuation 新证据，足够回答一个更具体的问题：旧 `τ-band` 宿主是否还有没被消费的新单轴 reframe 空间。

## 1) 原 rank 为什么 park？
原 `Rank 1 / static τ-band breakout confirmation` 被 park 的根因没有变化：
- 它确实证明了“breakout 后多等一层 outside-confirm，会比 raw breakout 少亏”；
- 但它没有证明 **`static τ-band` 本身** 是足以独立 rescue breakout 的有效主语。

原始冻结口径下（`BTC/ETH/SOL | 120d | 15m | 6bps/side`）：
- `confirm2of3_tau_010` 相对 `raw_breakout` 更不差、假突破率更低；
- 但 honest recheck 后仍只有 `mean_total_return ≈ -11.16%`、`positive_asset_ratio = 0/3`；
- 所以它最多是 `execution guard / scout follow-up`，不是 replace-ready winner。

换句话说：
**被证伪的不是 breakout 主题，而是“用 static τ-band 当 standalone rescue”这件事。**

## 2) 它更像 hard park 还是 soft park？
- 本轮判断：`soft park，但已更接近 hard park with consumed residual`

为什么还留一点 soft：
- breakout 后的 `outside persistence / continuation confirmation` 语义本身不是假的；
- 旧 Rank 1 至少留下过一个诚实 residual：`第一根 break 不算，后续继续站在区间外才承认 continuation`。

为什么又更接近 hard：
- 这条 residual 早已被写成 `Rank 1b`；
- 随后又被运行态里的 `Rank 94 / two-bar outside-range follow-through gate` 同题吸收；
- `Rank 94` 自己也已 clean replication 后重新压回 `park / evidence_pool`。

所以今天更诚实的表述不是“Rank 1 没残余”，而是：
**它唯一站得住的残余已经被表达、执行、再关闭。**

## 3) 有没有“可救信号”？
有，但仍然不是新的可救信号，而是旧 residual 的重复确认。

唯一还站得住的可救信号仍然只是：
- `static τ-band` → `two-stage outside-persistence continuation gate`

但 4 月 19~22 的新证据并没有把这条 residual 重新拉活，反而继续说明：
1. `2026-04-19` 的 `extreme recent return × strongest-only continuation router` 更像 **完整的 strongest-event raw alpha 宿主**；
2. `2026-04-20` 的 `20-bar breakout × dual momentum × ATR expansion` 更像 **带 acceleration / vol-expansion 的完整 breakout shell**；
3. `2026-04-22` 的 `BB squeeze breakout × EMA/MACD consensus` 也同样把价值落在 **完整 compression-breakout raw alpha**，而不是 old `τ-band` 这类 shared gate 残余。

因此现在还能说的“可救”，更像：
- breakout 后确实值得看 persistence；
- 但这层信息要么已经被 `Rank 1b -> Rank 94` 这条线消费完，
- 要么已经外流到新的、更完整的 breakout / continuation raw-alpha 宿主。

**结论：有主题级可救信号，但没有新的 Rank 1 本体级可救信号。**

## 4) 最值得改的唯一一刀是什么？
如果只谈 old `Rank 1`，唯一最值得改的一刀仍然没有变化：

**把 `static τ-band breakout confirmation` 改写成 `two-stage outside-persistence continuation gate`。**

但这刀已经不是本轮可新增内容，因为：
- 它不是新发现；
- 它不是未消费空间；
- 再写 `Rank 1c`，本质上只会重复 `Rank 1b -> Rank 94` 已审计过的对象边界。

## 5) 是否值得形成新的 derived hypothesis？
- 结论：**不值得**
- 本轮 verdict：`keep_park`

原因很简单：
1. 原 `park` 结论没有被推翻；
2. 唯一诚实 residual 已被 `Rank 1b -> Rank 94` 完整消费；
3. 最近新证据继续把 breakout / continuation 的价值往 **完整 raw-alpha shell** 上移，而不是回流到 old `τ-band` gate；
4. 若现在硬 draft `Rank 1c`，不是重复旧 residual，就是偷换成新宿主，都会削弱原 `park` 的审计边界。

## 6) 最终回答（按 bot6 模板）
- 原 rank 为什么 park？
  - 因为 `static τ-band` 只证明“多等一层 outside-confirm 比 raw breakout 少亏”，没证明自己是独立可救的 breakout alpha。
- 更像 hard park 还是 soft park？
  - `soft park`，但已更接近 `hard park with consumed residual`。
- 有没有可救信号？
  - 有，但只是旧的 `outside-persistence` residual；没有新的 Rank 1 本体级信号。
- 最值得改的唯一一刀是什么？
  - 仍是把 `static τ-band` 改成 `two-stage outside-persistence continuation gate`。
- 是否值得形成新的 derived hypothesis？
  - 不值得；当前更诚实的结论仍是 `keep_park`。

## Final verdict
- `verdict`: `keep_park`
- `original_verdict_kept`: `park`
- `one-line note`: `soft park，但比 4 月 15 日那轮更接近 hard with consumed residual；4 月 19~22 的 strongest-only continuation / dual-momentum breakout / BB squeeze breakout 新证据继续说明，breakout 主题若还有价值，也更像新的完整 raw-alpha 宿主，而不是足以把 old Rank 1 的 static τ-band 再诚实派生成 Rank 1c。`

## File actions
- 新增：`research/park_reframe/2026-04-22_0940_rank1-park-reframe.md`
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## Commit
- 本轮默认不做 commit。
- 原因：仅做最小必要文档改动，且仓库存在无关未跟踪脏文件，避免混提。
