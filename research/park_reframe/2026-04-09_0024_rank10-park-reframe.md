# 2026-04-09 00:24 UTC｜bot6 park-reframe｜Rank 10

## 0) 本轮选择
- 选定：`Rank 10 / volatility-managed EMA / ATR sizing overlay`
- 轮转理由：`50+` 与 `80~110` 号段近 7 天已被高频覆盖；本轮按规则回到 `1~24`，并优先选择**超过 7 天未被 bot6 复盘**、且仍处于 `park` 的条目。
- 最近一次 bot6 正式复盘：`2026-03-23 17:40 UTC`，已超过 `7` 天。
- 本轮要回答的不是“ATR 有没有用”，而是：**最近新增的 execution / liquidity 旁证，够不够把旧 Rank 10 再派生成一个新的窄 reframe hypothesis。**

## 1) 原 Rank 为什么 park？
原始结论来自：
- `research/optimization_loop/2026-03-16_2312_vol-managed-ema-park.md`

原 Rank 10 被 park 的原因很直接：
**standalone 的 ATR / volatility-managed sizing 没有把 15m EMA 方向层救活。**

上次 bot6 复盘已经把原始 blocker 说清楚：
- 问题不是“样本太薄，看不清”；
- 也不是“clip 参数还差一点”；
- 而是当它被写成一条独立修复线时，收益、回撤、时间稳定性、参数稳定性、跨标的稳定性、成本稳定性一起失败。

翻成人话：
**ATR 在这里更像‘这单能不能做 / 要不要缩手’的信息，不像‘靠它自己就能把策略变盈利’的信息。**

## 2) 它更像 hard park 还是 soft park？
- 本轮继续读作：`soft park`

原因：
- 对 **原 Rank 10 本体**（standalone volatility-managed EMA / ATR sizing）来说，读法已经非常接近 hard park；
- 但 ATR / 波动信息本身并没有被证明“完全无信息”；
- 它仍保留一条很窄、且早已被写出来的 residual：
  - **`Rank 10b`：把 ATR 降级成 shared `size-down / veto / tradeability` overlay。**

所以更准确地说：
- **原 rank 的 standalone 读法：接近 hard park**
- **整条主题是否还有残余价值：仍是 soft park**

## 3) 现有证据里有没有“可救信号”？
- 有，但仍然只是**旧 residual 的加固**，不是新的主修改轴。

本轮主要看的新增旁证：
- `research/quant_digests/2026-04-05_2003_orderbook-variation-liquidity-timing-overlay.md`
- `research/quant_digests/2026-04-08_2249_fillaware-ofi-flowcontrol-shell.md`

这两条新证据的共同含义不是“再调一次 ATR 就能救回来”，而是：
1. 真正重要的往往是 **交易性 / 流动性 / fill realism / adverse selection**；
2. execution 风险更适合被写成 **veto / sizing / tradeability** 层；
3. 越往新证据走，越像是在说明：
   - **先判断这笔单值不值得做、做不做得出去；**
   - **再谈仓位缩放；**
   - 而不是把 ATR 本身继续包装成独立 alpha 修复器。

所以 Rank 10 的“可救信号”仍只有一句话：
**ATR 还有信息，但它更像 shared risk / tradeability layer 的一个输入，不值得再被写成新的 standalone rescue line。**

## 4) 最值得改的唯一一刀是什么？
- **没有新的一刀。最值得保留的唯一修改轴，仍然是既有 `Rank 10b`。**

也就是：
- 把 ATR 从 standalone sizing alpha，降级成 shared `size-veto / tradeability` overlay；
- 第一刀仍应是 `baseline vs size-down vs veto` 这类 strict A/B；
- 不应该再顺手叠第二轴（新 regime / 新 entry / 新 exit / 新 liquidity score）。

这次新增的 4 月证据，并没有给出比 `Rank 10b` 更窄、更独立、更诚实的新轴。
它们只是进一步强化：
**原 Rank 10 最大的问题，就是把 ATR 的职责摆错了。**

## 5) 是否值得形成新的 derived hypothesis？
- 结论：**不值得。**
- 本轮最终 verdict：`keep_park`

原因：
1. 原 `park` 结论没有被推翻；
2. 最近新证据强化的是 execution / liquidity / tradeability 层，而不是 ATR standalone 读法；
3. 这些强化依旧落在既有 `Rank 10b` 的职责边界里；
4. 如果现在硬写一个 `Rank 10c`，大概率只是把 `10b` 换种措辞重写一遍，不是新增一条真正独立的主修改轴。

## 6) 本轮固定回答（摘要）
- 原 rank 为什么 park？
  - 因为 standalone ATR volatility-managed sizing 没把 15m EMA 方向层救活；失败不是参数还没调对，而是角色本身写错了。
- 它更像 hard park 还是 soft park？
  - `soft park`；但对原 Rank 10 本体的 standalone 读法，已经接近 hard park。
- 有没有可救信号？
  - 有；但只说明 ATR 更像 shared risk / tradeability layer 的输入，不支持新的 standalone reframe。
- 最值得改的唯一一刀是什么？
  - 仍是既有 `Rank 10b`：把 ATR 降级成 shared `size-down / veto / tradeability` overlay。
- 是否值得形成新的 derived hypothesis？
  - 不值得；本轮结论为 `keep_park`。

## 7) 本轮结论
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park`
- `why_not_new_derivation`: `2026-04-05~2026-04-08 新增的 liquidity / fill-aware 证据继续把 ATR 主题往 execution / tradeability overlay 推，而不是支持再诚实派生 Rank 10c；既有 Rank 10b 已覆盖唯一主修改轴`

## 8) 文件动作
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## 9) commit
- 本轮默认不做 commit。
- 原因：`git status` 显示仓库存在与本轮无关的共享脏文件 / 未跟踪文件；为避免混提，这轮只做最小必要文档改动。