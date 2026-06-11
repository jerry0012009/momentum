# 2026-04-19 02:03 UTC · Rank 21 park reframe revisit

## Selected rank
- `Rank 21`
- selection note: 本轮按 `bot6` 轮转回到 `Rank 1~24` 的已 parked 条目；`Rank 21` 上次 bot6 复盘为 `2026-04-11 05:35 UTC`，已超过 `7` 天窗口，且原线仍处于 `park`，适合做一次低频复核。

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- recent park-reframe context:
  - `research/park_reframe/2026-04-18_2349_rank59-park-reframe.md`
  - `research/park_reframe/2026-04-18_2130_rank18-park-reframe.md`
  - `research/park_reframe/2026-04-18_1823_rank26-park-reframe.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_0412_rank21-clean-replication-park.md`
  - `research/park_reframe/2026-04-11_0535_rank21-park-reframe.md`
  - `research/quant_digests/2026-04-16_0454_bubblestate-ma-cross-trend-alpha.md`
  - `research/quant_digests/2026-04-18_0431_rsi-breakout-trend-shell.md`
  - `research/quant_digests/2026-04-18_2150_sar-slippage-risk-overlay.md`

## 1) 原 rank 为什么 park？
原 `Rank 21` 被 park 的根因没有变化：它把 `market risk-on/off` 写成 **15m 同频 shared allow/deny gate**，但 clean replication 已经把这条读法审计得很清楚——它至多是“比 baseline 少亏一点”，远没到可诚实 queue-facing 的程度。

关键结果仍然成立：
- `market_risk_2of3 @ 6bps/side ≈ -25.01%`
- `positive_asset_ratio = 0/3`
- `mean_trades ≈ 265.0`
- `mean_no_trade_ratio ≈ 51.29%`
- `10bps/side ≈ -39.22%`
- `15bps/side ≈ -53.14%`
- 时间稳定性：`0/3 positive buckets`
- 参数邻域最佳也仍约 `-17.06%`

所以原 park 的审计意义必须继续保留：
**失败的是“逐根 15m market risk-on/off allow/deny gate”这个岗位，而不是 risk / sentiment / bad-state 信息完全不存在。**

## 2) 它更像 hard park 还是 soft park？
**本轮仍判断为 `soft park`，但比 4 月 11 日那轮更接近 `hard park with consumed residual`。**

为什么还保留 soft：
- `risk sentiment / bad-state` 主题并没有归零；
- 它仍可能对 `size-down / veto / stricter confirm / stop trading` 这类更低频职责有信息量。

为什么更接近 hard：
1. 原线唯一诚实 residual 早已被既有 `Rank 21b` 收窄表达；
2. 4 月中下旬新证据没有提供第二条独立、同层的新修改轴；
3. 新证据反而继续把这组变量往 **完整 trend shell / execution overlay / event-driven 宿主** 上移，而不是回流到 old `Rank 21` 本体。

## 3) 有没有“可救信号”？
**有残余，但没有新的可救信号；唯一 residual 仍只到既有 `Rank 21b`。**

这轮重读后，残余信息的落点反而更收紧了：

### A. `bubble-state × MA trend` 继续说明：state 信息更适合挂在明确主壳上
`2026-04-16_0454_bubblestate-ma-cross-trend-alpha.md` 的主语是 `MA trend-following × bubble-state gate`。
它保留的是：
- market-state / bubble-state 可以帮助区分“哪些趋势更值得参与”；
- 但前提是已经有一个更清楚的 trend shell / trigger 宿主。

这不是在救 old `Rank 21` 的 15m 同频 shared gate；
而是在继续说明：**state 信息若还有价值，更像主壳上的 admission layer。**

### B. `RSI breakout trend shell` 继续说明：readiness/filter 更像完整 trend shell 的一部分
`2026-04-18_0431_rsi-breakout-trend-shell.md` 的有效语义同样不是“让 risk sentiment 自己决定逐根 allow/deny”，而是：
- 在完整 trend shell 里，慢趋势 / readiness / confirmation 可以有价值；
- 但这些 filter 要挂在更完整的 entry/exit/ATR trail 宿主上。

这进一步削弱了继续从 old `Rank 21` 派生 `21c` 的必要性。

### C. `Slippage-at-Risk` 新证据说明：风险层若还值得保留，更像 execution overlay
`2026-04-18_2150_sar-slippage-risk-overlay.md` 更明确地把“风险层”往 `entry veto / leverage-down / size-down` 这类 execution 语义上推。
这条证据并不是 sentiment 主题本身，但它给 bot6 一个更清楚的边界：
- 若现在硬把 `Rank 21` 往“风险 overlay”再拆一层，很容易只是把 generic risk overlay 换个 sentiment 外壳重讲；
- distinctness 不足，且会稀释 old `Rank 21 = market risk-on/off gate` 的审计边界。

所以本轮的结论不是“完全没有 residual”，而是：
**residual 还在，但越来越不像 old Rank 21 自己还能诚实切出新的 queue-facing reframe。**

## 4) 最值得改的唯一一刀是什么？
**唯一最值得改的一刀仍然没有变化：既有 `Rank 21b`。**

> `demote standalone market risk-on/off regime gate into a daily sentiment-extremity shared risk overlay`

也就是：
- 不再根据 `market_risk_2of3 / 3of3` 逐根决定 15m 是否 allow；
- 保留 breakout / fib / EMA-PSAR 等 base setup 自己负责触发；
- 只在 `Fear & Greed <= 25` 或 `>= 75` 的极端日做 `size-down / veto / stricter confirm`。

本轮没有出现比这更诚实的新一刀。
如果再往外扩，基本只会落入两类问题：
1. 只是同义改写 `21b`；
2. 偷带第二轴，把 `sentiment + macro-event + execution-risk` 混成一条多轴新故事。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。最终结论：`keep_park`。**

更精确地说：
- 原 `Rank 21 = park` 的审计意义保持不变；
- 既有 `Rank 21b` 继续是 old rank 唯一诚实 residual；
- 本轮没有形成新的 `Rank 21c`。

## 6) trade on / trade off（审计式说明）
本轮不新增派生，只保留审计说明。

### trade on
- 若将来还要保留 `Rank 21` 的残余价值，更诚实的做法仍然只是：
  - 让 daily sentiment extremity 只负责 `risk overlay / size-down / veto / stricter confirm`；
  - 不再假装它能逐根给出方向性 allow/deny。

### trade off
- 它不再是 standalone alpha，也不再是 standalone gate；
- 改善大概率更多体现为 left-tail / tradeability / bad-state avoidance，而不是 headline return；
- 若继续往 `macro-event + sentiment` 或 `execution overlay` 方向扩写，就已经更像新的宿主 family，而不是 old `Rank 21` 的诚实 reframe。

---

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park，但比 4 月 11 日那轮更接近 hard park with consumed residual`

## Minimal audit note
本轮不推翻 `Rank 21` 的原 park，也不新增 `Rank 21c`。更诚实的记录是：**old Rank 21 的唯一诚实 residual 仍只到既有 `Rank 21b`；而 4 月中下旬新增的 bubble-state / RSI breakout trend-shell / Slippage-at-Risk 证据继续说明，这类 risk/state 信息若还有价值，更像完整 trend shell、execution overlay 或 event-driven 宿主的一部分，而不是足以再诚实派生旧 `Rank 21`。**

## Git
- git 工作区存在大量与本轮无关脏文件；本轮只做最小必要文档改动，不做 selective commit，避免混提。
