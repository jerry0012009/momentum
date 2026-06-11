# 2026-04-11 13:25 UTC — Rank 59 park reframe

## 本轮选择
- 当前 `bot6` 仍按 `50+` 号段低频轮转；`Rank 59` 上次复盘是 `2026-04-04 11:40 UTC`，已超过 `7` 天。
- 近期又出现一批更完整的短周期趋势壳旁证，尤其是：
  - `research/quant_digests/2026-04-08_0405_htf-ema-rsi-pullback-trend-shell.md`
  - `research/quant_digests/2026-04-04_1050_dual-supertrend-nonfiring-alpha.md`
- 因此本轮只回答一件事：原 `Rank 59 / Ichimoku Kijun + cloud-side continuation gate` 是否还值得再诚实切出一个新的窄 reframe hypothesis。

## 读集
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/optimization_loop/2026-03-18_1557_rank59-clean-replication.md`
- `research/optimization_loop/2026-03-18_1640_rank59-time-stability-park.md`
- `research/park_reframe/2026-04-04_1140_rank59-park-reframe.md`
- `research/quant_digests/2026-04-08_0405_htf-ema-rsi-pullback-trend-shell.md`
- `research/quant_digests/2026-04-04_1050_dual-supertrend-nonfiring-alpha.md`

## 原 rank 为什么 park
原 `Rank 59` 想把 `Ichimoku` 的 `Kijun + cloud-side` 写成一个 **15m shared continuation gate**，横向服务 `ema_psar_long / fib_retest_long / breakout_short`。

但原始 clean replication 与 cheap time-stability 已把 blocker 审计得很清楚：
- `ema_psar_long` 只留下“少亏一些”的薄 residual；
- `fib_retest_long` 的改善主要靠极端砍样本，`kijun+cloud_side` retention 约仅 `6.06%`；
- `breakout_short` 基本没有被修好；
- 时间稳定性上，最不差的 `ema_psar_long / cloud_side` 仍是前两桶负、最后一桶正，不像稳定主轴。

翻成人话：
**原 Rank 59 失败的不是 Ichimoku 语义完全没信息，而是它撑不起“跨 setup 的 shared continuation gate”这个岗位。**

## 它更像 hard park 还是 soft park
**结论：`soft park`，但现在比 4 月 4 日那轮更接近 `hard park`。**

原因：
- 仍算 soft，是因为 `Kijun / cloud-side` 至少保留了“慢趋势 / trend-readiness context 可能有信息”的残余；
- 更接近 hard，是因为这点残余越来越不像 `Rank 59` 自己还能诚实派生出的 queue-facing 新对象，而更像应被别的 trend-shell 宿主吸收。

## 有没有“可救信号”
**有，但可救信号不再属于旧 Rank 59 本体。**

唯一还能保留的信号是：
- `Ichimoku` 留下的不是“再加一道 shared continuation gate”，而是 **慢趋势 context / trend-readiness** 这一层语义可能仍有信息。

但 4 月上旬的新证据继续把这层语义上移到更完整的 raw-alpha 宿主：
1. `2026-04-08_0405_htf-ema-rsi-pullback-trend-shell.md`
   - 更像 `HTF EMA gate × 15m RSI pullback continuation` 的完整趋势壳；
   - 其中 `HTF EMA gate` 已经覆盖了 Rank 59 想表达的“先确认慢趋势，再谈 continuation”。
2. `2026-04-04_1050_dual-supertrend-nonfiring-alpha.md`
   - 虽然当前实现几乎不触发，但它同样把“慢趋势确认”放在完整 trend shell 里，而不是写成一个横向共享 gate。

因此，最近的新证据没有把旧 `Rank 59` 救回来，反而继续说明：
**若慢趋势确认还值得追，更像新的 trend-shell family 组件，而不是 `Rank 59b`。**

## 最值得改的唯一一刀是什么
如果只保留 **1 条唯一主修改轴**，最值得改的一刀仍然只有：

**把 `Ichimoku Kijun + cloud-side` 从 shared continuation gate 继续降级成 HTF context-only trend-bias / trend-readiness overlay。**

但本轮不值得把这刀再写成新的 `Rank 59b`，因为：
- 这不是新故事，只是在重复“慢趋势线更像 context，不像平级触发器”的旧角色改写；
- 近期新证据已把这层语义抬升到更完整的 trend-shell 宿主；
- 现在硬写 `Rank 59b`，大概率只是把原 `park` 结论换个 Ichimoku 壳重讲一遍。

## 是否值得形成新的 derived hypothesis
**不值得。最终结论：`keep_park`。**

### 模板回答
1. **原 rank 为什么 park？**
   - 因为 `Kijun / cloud-side` 作为 shared continuation gate 只在 `ema_psar_long` 留下薄 residual，在 `fib_retest_long` 上主要靠极端砍样本，在 `breakout_short` 上几乎无效，而且时间稳定性不足。
2. **更像 hard park 还是 soft park？**
   - `soft park`，但比上次复盘更接近 `hard park`。
3. **有没有“可救信号”？**
   - 有；但更像慢趋势 / trend-readiness context 仍有信息，不像旧 `Rank 59` 本体还能再诚实派生。
4. **最值得改的唯一一刀是什么？**
   - 把 `Ichimoku Kijun + cloud-side` 从 shared continuation gate 继续降级成 HTF context-only trend-bias / trend-readiness overlay。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得，维持 `keep_park`。

## 最小审计结论
- 保留原 `park` verdict；
- `Rank 59` 本轮状态仍记为 **`keep_park`**；
- 原线唯一诚实残余仍只是“慢趋势 context”这层被新 trend-shell 宿主吸收的语义，不足以再诚实派生 `Rank 59b`。

## Git
- 当前 repo 仍有无关脏文件；本轮只做 park-reframe 最小文本更新。
- 不改 `docs/TODO.md`，也不做混合 commit。
