# 2026-04-18 23:49 UTC · Rank 59 park reframe revisit

- source rank: `Rank 59 / Ichimoku Kijun + cloud-side continuation gate`
- verdict: `keep_park`
- original verdict kept: `park`
- selection note: 按 `bot6` 当前轮转，仍优先处理 `Rank 50+` 的 parked rank；`Rank 59` 上次 park-reframe 是 `2026-04-11 13:25 UTC`，已超过 `7` 天窗口。本轮只复盘这一条，不改 `TODO` 顶部排班，也不替 `bot2 / bot3` 直接分配新任务。

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/park_reframe/2026-04-04_1140_rank59-park-reframe.md`
- `research/optimization_loop/2026-03-18_1537_rank59-source-intake.md`
- `research/optimization_loop/2026-03-18_1557_rank59-clean-replication.md`
- `research/optimization_loop/2026-03-18_1640_rank59-time-stability-park.md`
- `research/quant_digests/2026-04-18_0431_rsi-breakout-trend-shell.md`

## 1) 原 rank 为什么 park
原 `Rank 59` 想把 `Ichimoku` 的 `Kijun + cloud-side` 写成一条可横向服务 `ema_psar_long / fib_retest_long / breakout_short` 的 shared continuation gate。

但最小 clean replication + 便宜 time-stability 的审计结论一直很一致：
- `ema_psar_long` 上只剩“少亏一些”的薄 pocket；
- `fib_retest_long` 的改善主要靠极端砍样本，`kijun+cloud_side` retention 只剩约 `6.06%`；
- `breakout_short` 几乎没被修好；
- 时间稳定性里，最不差的 `ema_psar_long / cloud_side` 也是 `bucket_1≈-5.44% / bucket_2≈-1.55% / bucket_3≈+6.33%`，只在最后一桶转正。

所以它被 park 的根因没有变：
**不是 Ichimoku 完全没信息，而是这点信息不足以继续承担“跨 setup 共用 continuation gate”这个岗位。**

## 2) 它更像 hard park 还是 soft park
**结论：`soft park`，但比 4 月 4 日那轮更接近 `hard park with consumed residual`。**

原因：
- 仍算 soft park，是因为 `Kijun / cloud-side` 至少保留了“慢趋势 / trend-readiness context 可能有信息”的残余；
- 但更接近 hard，是因为这条残余已经越来越不像 `Rank 59` 本体还值得诚实派生，而更像会被别的完整 trend shell 宿主吸收。

## 3) 有没有“可救信号”
**有，但只剩主题级残余，不再像 old Rank 59 自己的 queue-facing salvage。**

本轮新增旁证来自 `2026-04-18_0431_rsi-breakout-trend-shell.md`：
- 新证据强调的是 `EMA200 + ADX + volume + RSI breakout + ATR trail` 这种**完整 trend shell**；
- 它保留的核心语义，恰恰就是“先确认慢趋势 / trend readiness，再谈 continuation”；
- 但这层语义已经被写进一个更完整的 raw-alpha 宿主里，而不是回流到旧 `Ichimoku shared gate` 这种跨 lane 共用过滤层。

换句话说：
- `Rank 59` 留下的并不是零信息；
- 但新证据救活的是“新的 trend shell / raw-alpha 宿主”，不是旧 `Rank 59` 本体。

## 4) 最值得改的唯一一刀是什么
如果只保留 **1 条唯一主修改轴**，仍然只有这一刀是诚实的：

**把 `Ichimoku Kijun + cloud-side` 从 shared continuation gate 继续降级成更慢的 HTF context-only trend-bias / trend-readiness overlay。**

但这刀本轮依然**不值得**再写成新的 `Rank 59b`，因为：
1. 这不是新故事，仍是在重复“慢趋势线更像 context、不像平级触发器”的角色降级；
2. 新增证据已经把这层语义上移到完整 trend shell 宿主里；
3. 如果现在硬 draft `Rank 59b`，很容易只是换一个 Ichimoku 外壳重讲已有 family 语义，削弱原 `park` verdict 的审计边界。

## 5) 是否值得形成新的 derived hypothesis
**不值得。最终结论：`keep_park`。**

原因：
- 原 blocker 没被推翻：shared continuation gate 读法仍主要靠薄 pocket / 大幅砍样本减亏；
- 唯一诚实修改轴只是继续降级成慢趋势 context-only 角色；
- 这条 residual 已被更完整的 trend-shell / raw-alpha 宿主吸收，distinctness 不足，没必要再挂一个新的 `Rank 59b`。

## 模板回答
1. **原 rank 为什么 park？**
   - 因为 `Kijun / cloud-side` 作为 shared continuation gate 只在 `ema_psar_long` 留下薄残余，在 `fib_retest_long` 上主要靠极端砍样本、在 `breakout_short` 上几乎无效，而且时间稳定性不足。
2. **更像 hard park 还是 soft park？**
   - `soft park`，但比上次更接近 `hard park with consumed residual`。
3. **有没有可救信号？**
   - 有；但只剩“慢趋势 / trend-readiness context”这层主题级残余，更像新的 trend-shell 宿主，不像 old Rank 59 本体还能再诚实派生。
4. **最值得改的唯一一刀是什么？**
   - 把 `Ichimoku Kijun + cloud-side` 从 shared continuation gate 继续降级成 HTF context-only trend-bias / trend-readiness overlay。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得。

## Minimal update note
- 本轮只更新：
  - `research/park_reframe/2026-04-18_2349_rank59-park-reframe.md`
  - `research/park_reframe/INDEX.md`
  - `docs/PARK_REFRAME_QUEUE.md`
- 默认不改 `docs/TODO.md`。
- 当前 repo 仍有无关脏文件，本轮不做混合提交。
