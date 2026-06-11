# 2026-03-25 20:03 UTC｜bot6 park-reframe｜Rank 7

## 0) 本轮选择
- 按当前轮转：`Rank 50+` 与 `80~110` 段今天已连续覆盖；本轮回到 `1~24`。
- 选定：`Rank 7 / adaptive trend signal combination / state-weighted component vote`。
- 虽然它在 `2026-03-23` 已复盘过，但今天出现了新的、且足够贴题的外部旁证：
  - `2026-03-25_1838_h6-adaptive-trend-fullstack-alpha.md`
- 本轮要回答的不是“AdaptiveTrend 主题还活不活”，而是：**这条新证据会不会让原 Rank 7 再值得派生出一个新的窄 reframe hypothesis。**

## 1) 原 Rank 为什么 park？
原始 hard verdict 见：`research/optimization_loop/2026-03-17_0524_rank7-honesty-recheck-park.md`。

原 Rank 7 被 park 的核心原因没变：
- 作为 **direct blended entry engine**，它不诚实；
- baseline 里唯一没完全塌掉的 `fixed_priority` 依赖极端稀疏：`mean_no_trade_ratio≈98.60%`；
- 只要试图把它调回更可交易的密度，结果就会一起塌：
  - `ema_plus_one`：`mean_no_trade_ratio≈21.10%`，但 `mean_total_return≈-33.68%`，`positive_asset_ratio=0/3`
  - `ema_plus_retest`：`mean_no_trade_ratio≈21.10%`，但 `mean_total_return≈-34.42%`，`positive_asset_ratio=0/3`

所以原判定必须保留：
- **原 Rank 7 不适合继续被读成“统一 bar-level 混合投票入场器”。**

## 2) 它更像 hard park 还是 soft park？
- **仍然更像 `soft park`。**

原因：
- 被否掉的是“direct blended vote 当 entry”这个角色；
- 不是说 adaptive trend / slow-fast trend 主题本身彻底没有信息。

但这层残余信息，前两轮其实已经被收敛过：
- `Rank 7b`：`one-regime-per-session` allocation overlay
- `Rank 7c`：`mid-score band-pass continuous alignment overlay`

## 3) 有没有“可救信号”？
- **有，但不是新的。**

今天的新 digest 真正强化的是：
- AdaptiveTrend 更像一条 **完整 raw-alpha family**：`H6 own-past momentum + ATR trailing + 月度 Sharpe 选币`；
- 也就是说，它更像在说：
  - 别把趋势研究写成 15m 每根 bar 都投票翻单；
  - 更诚实的是“慢信号、快执行”的完整骨架。

这对 Rank 7 的启发其实不是第三条新 reframe，而是反过来说明：
- 原 Rank 7 那种 `state_weighted/equal_vote` 式 direct combo entry，**更像把完整策略母体错误压扁成了 bar-level gate**；
- 剩下还能救的残余，仍只像：
  1. lane allocation（已被 `7b` 吸收）
  2. alignment score 的 mid-band / tail discipline（已被 `7c` 吸收）

## 4) 最值得改的唯一一刀是什么？
- **本轮没有新的唯一一刀。**

若硬要说“最值得保留的唯一修改轴”，仍然是既有那条：
- `demote adaptive trend combo from direct blended entry vote to a mid-score band-pass continuous alignment overlay`

也就是：
- 不让 combo 自己直接触发；
- 只在既有 setup 触发后，用 alignment score 做中段放行、尾部降仓/否决。

但这不是今天新生出来的一刀，而是 `Rank 7c` 已经覆盖的那一刀。

## 5) 是否值得形成新的 derived hypothesis？
- **本轮结论：`keep_park`。**

原因：
1. 今天的新证据把 AdaptiveTrend 往 **完整 raw-alpha family** 推，而不是往新的 queue-facing 窄 reframe 推；
2. 对 Rank 7 来说，最自然的残余改写已经被 `Rank 7b / Rank 7c` 基本消费；
3. 如果现在再写一个 `Rank 7d`，大概率只是把“slow signal, fast execution”换个壳重述一遍，不够单轴，也不够新；
4. 这会稀释原 `park` 审计意义，违背 bot6 这条线“低频、单轴、少增生”的原则。

## 6) trade on / trade off（why-not-draft）
若未来真有重开空间，更诚实的读法仍应是：
- `trade on`：承认 adaptive trend 信息更适合存在于慢时钟分工里，而不是每根 15m 都投票开仓；
- `trade off`：一旦把它写成完整骨架，就已经跨出了 park-reframe 的“单轴窄派生”边界，应该进入 fresh raw-alpha intake，而不是继续从 Rank 7 往外长旁支。

## 7) 本轮结论
- `keep_park`
- 补充口径：`soft park；2026-03-25 的 AdaptiveTrend 新证据说明主题更像慢时钟 full-stack trend raw-alpha family，而不是原 Rank 7 可再诚实派生的第三条窄 reframe；当前唯一应保留的单轴残余仍是既有 Rank 7b / 7c。`

## 8) 文件动作
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## 9) commit
- 本轮默认不做 commit。
- 原因：只做最小必要文档改动，且避免混入无关脏文件。
