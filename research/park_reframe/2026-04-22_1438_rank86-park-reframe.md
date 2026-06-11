# 2026-04-22 14:38 UTC — Rank 86 park reframe review

## 0) 本轮选择
- 选定条目：`Rank 86 / SignalPro penetration×ATR admission`。
- 轮转理由：本轮默认仍在 `50+` 号段内轮转；最近 7 天内 `80~110` 段已覆盖较少，且 `Rank 86` 上次 `bot6` 复盘是 `2026-04-10 12:40 UTC`，已超过 7 天。
- 边界：本轮只判断旧 `Rank 86` 是否还能诚实派生新的窄 reframe；不改 `docs/TODO.md`，不分配 `bot2 / bot3` 新任务。

## 1) 原 rank 为什么 park？
原 `Rank 86` 被 park 的核心原因不是 `penetration / ATR` 变量完全无信息，而是它被写成 **shared penetration×ATR admission gate** 后时间稳定性不过关：
- `ema_psar_follow_short + pen_plus_atr` overall 只到约 `+0.03%`，但第三时间桶转为约 `-2.91%`；
- `fib_retest_short + pen_plus_atr` overall 约 `+2.18%`，但第二、第三桶转负；
- `breakout_short + pen_plus_atr` overall 约 `-1.55%`，只有第一桶为正。

因此原结论是：`Rank 86 / SignalPro penetration×ATR admission = park / evidence_pool`。被保留的审计意义是：不要再把它当跨 setup 的 shared gate 续命。

## 2) 它更像 hard park 还是 soft park？
本轮判断：`soft park`，但已经非常接近 `hard park with consumed residual`。

- soft 的部分：历史上确实有一个可救信号——`penetration×ATR` 更像 `breakout-short` 专用的 short-side admission / veto，而不是 shared gate。
- hard 的部分：这条唯一自然残余已经在 3 月底被正式转写并消费为 `Rank 222 / breakout-short penetration×ATR short-admission reframe`；4 月 10 日 bot6 也已判定不应再从旧 `Rank 86` 派生新的 `86c`。

## 3) 有没有“可救信号”？
有，但不是新的：唯一可救信号仍是 **把 shared gate 收窄成 breakout-short short-side only admission**。

本轮没有发现能改变 4 月 10 日结论的新证据。4 月 21~22 的最新 quant digests 更偏向新的 pairs/stat-arb、crowding fade、new-listing bubble fade、cross-sectional mean reversion 与完整 raw-alpha shell；它们没有给旧 `Rank 86` 的 `penetration×ATR shared gate` 提供新的、独立的、同主语修复证据。

## 4) 最值得改的唯一一刀是什么？
若只看旧 `Rank 86`，唯一诚实的一刀仍是：

> 把 `shared penetration×ATR admission gate` 降级成 `breakout-short short-side only admission / veto`。

但这不是本轮新提案；它已经被 `Rank 222` 吸收并正式审计过。继续改第二刀（例如再叠 liquidity、crowding、session 或新 exit）会变成多轴大改，不符合 bot6 的窄 reframe 规则。

## 5) 是否值得形成新的 derived hypothesis？
不值得。

理由：
1. **唯一主修改轴已被消费**：`Rank 222` 已经承接了 `Rank 86b` 的 breakout-short-specific short-side admission 语义。
2. **继续命名会重复审计对象**：再写 `Rank 86c / Rank 86 reframe` 只会复述同一条 `penetration×ATR -> short-side admission` 轴，而不是产生新的独立假设。
3. **最新新证据不在旧主语上**：近期材料支持的是新的 raw-alpha / shell 宿主，而不是修复旧 shared gate。

## 6) verdict
- verdict: `keep_park`
- original verdict kept: `park`
- classification: `soft park -> hard park with consumed residual`
- derived hypothesis: none

一句话结论：`Rank 86` 的原 park 仍然成立；唯一可救残余已由 `Rank 222` 消费，当前没有新证据支持诚实 draft `Rank 86c`。

## 7) 文件与流程影响
- 新增本轮日志：`research/park_reframe/2026-04-22_1438_rank86-park-reframe.md`
- 追加更新：`research/park_reframe/INDEX.md`
- 追加更新：`docs/PARK_REFRAME_QUEUE.md` 的 Recently reviewed
- 未改：`docs/TODO.md`

## 8) git / 提交说明
本轮只做最小必要文档改动。`git status --short` 显示工作区存在大量无关未跟踪 / 脏文件；按要求不混提，本轮不做 commit。
