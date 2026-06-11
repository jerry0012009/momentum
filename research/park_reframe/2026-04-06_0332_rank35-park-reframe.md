# 2026-04-06 03:32 UTC · Rank 35 park reframe review

## Scope
- Source rank: `Rank 35 VWAP pullback + trend-template qualifier`
- Original verdict stays: `park / evidence pool`
- This round only asks: **whether Rank 35 still deserves a new narrow reframe beyond existing `Rank 35b`, not whether the original park should be overturned.**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- Needed evidence:
  - `research/optimization_loop/2026-03-17_1248_rank35-clean-replication-park.md`
  - `research/park_reframe/2026-03-17_2222_rank35-park-reframe.md`
  - `research/quant_digests/2026-04-03_2141_wilder-rsi-fast-exit-trend-shell-alpha.md`
  - `research/quant_digests/2026-04-03_2251_dc-vwap-ema-asymmetric-trend-shell.md`

## Why this rank this round
- `Rank 35` 属于 `Rank 1~37` 的 parked 池。
- 它上次 `bot6` 复盘已超过 7 天（`2026-03-23 15:37 UTC`），满足低频重看条件。
- 它原本就不是全线硬塌，而是留下过一条很窄的 residual pocket（`bias_plus_rsi_pullback`），因此值得确认：最近新证据有没有把它推进到新的 `35c`。

## 1) 原 rank 为什么 park？
原 Rank 35 被 park，不是因为“顺势 pullback”这个大方向彻底死了，而是因为它当时要验证的**那种写法**不够诚实：
- 主变体 `combo_long_only` 在 `6bps/side` 下只剩 `mean_trades≈3.7~4.0`，太稀；
- 中间 time bucket 明确翻负；
- `bias_plus_vwap_reclaim` 对 VWAP anchor 明显敏感（`utc_day≈+8.69%`，`funding_8h≈-0.51%`）；
- 所以真正被 park 的，是“higher-tf bias + RSI pullback + VWAP reclaim 这套打包 entry”——不是 higher-tf bias 本身，也不是所有 pullback continuation 语义。

翻成人话：它更像是**确认层写得太满、VWAP 这刀最不稳、结果还稀到没法升格**，所以被放回 evidence pool。

## 2) 它更像 hard park 还是 soft park？
**仍然更像 soft park，但比 3 月下旬更偏硬。**

为什么不是 hard park：
- 原 clean replication 至少说明 `bias_plus_rsi_pullback` 留过一点点 residual value；
- `Rank 35b` 这条“删掉 VWAP reclaim，只保留 higher-tf bias + RSI pullback reclaim”的单轴改写，依然是对原 rank 最诚实的窄收缩。

为什么现在又更偏硬：
- 最近新增的两条旁证（Wilder RSI breakout、VWAP-EMA directional-change）都在说：**如果这类主题还值得追，主语已经更像新的完整 trend-shell raw alpha**；
- 也就是说，残余价值正在往“新的 raw alpha 宿主”外流，而不是继续留在旧 Rank 35 这条 parked 线里长出第二条窄派生。

## 3) 现有证据里有没有“可救信号”？
**有，但只有旧的、已经被 `Rank 35b` 消费过的那一条。**

唯一还算可救的信号仍然是：
- 去掉 VWAP reclaim 后，`bias_plus_rsi_pullback` 比完整 combo 更诚实；
- 这说明 residual value 更像“顺势回调后再接回去”的简单 pullback timing，而不是 anchor-sensitive 的 VWAP reclaim。

但最近新证据并没有给出属于 Rank 35 的第二条诚实新线：
- `2026-04-03_2141` 更像新的 **Wilder RSI breakout × fast exit trend shell**；
- `2026-04-03_2251` 更像新的 **VWAP-EMA directional-change continuation shell**；
- 两者都不是在替旧 Rank 35 的 parked 包装补一刀，而是在把主题上移到新的 raw-alpha family。

## 4) 最值得改的唯一一刀是什么？
**仍然只有一刀：删掉 VWAP reclaim，保留 higher-tf bias + RSI pullback reclaim。**

也就是既有 `Rank 35b`：
- 不再让 VWAP anchor 继续当 admission 的关键门；
- 保留“顺势回调 -> RSI reclaim -> next-bar open 进场”的最小故事。

这条唯一主修改轴没有被推翻，但也没有被最近新证据升级出第二条更好的 `35c`。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

原因：
1. 原 `park` verdict 仍应保留，不该被重写；
2. 原 rank 唯一诚实的窄 reframe 已经被 `Rank 35b` 占住；
3. 最近新增证据虽然支持“趋势延续 + 更快退出 / 更慢趋势脊柱”这类主题还活着，但它们更像新的 raw-alpha shell，而不是旧 Rank 35 可继续诚实派生的 `Rank 35c`；
4. 继续从旧 rank 往下切，只会开始混入第二轴（换 trigger、换 exit、换 shell 主语），这违反 bot6 本轮只保留一刀的边界。

## 6) trade on / trade off 怎么理解？
本轮不新增 derived hypothesis，因此不新写一套 `trade on / trade off`。

仍然有效的旧理解只有：
- `Rank 35b` 的 trade on = 继续赌顺势 pullback 的再启动；
- trade off = 放弃最不稳的 VWAP reclaim 确认，接受更高噪声。

但这套语义已经足够，当前没有诚实理由再多生一条 `35c`。

## Final verdict
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_style_now`: `soft park，但已比上次更偏硬`
- `why_not_new_derivative`: `既有 Rank 35b 已覆盖唯一诚实修改轴；最近新增的 Wilder RSI / VWAP-EMA 证据更像新的 trend-shell raw-alpha family，而不是旧 Rank 35 的可诚实窄派生`

## Minimal audit note
这轮不是推翻 `Rank 35b`，也不是否认顺势 pullback 主题本身还有研究价值。
这轮只是把边界钉清楚：**旧 Rank 35 的 residual value 到 `35b` 为止；再往下切就会把主题偷换成新的 raw-alpha 宿主，因此本轮维持 `keep_park`。**
