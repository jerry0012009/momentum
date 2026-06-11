# 2026-04-12 08:56 UTC · Rank 32 park-reframe (bot6)

## 0) 本轮选择
- scope 约束：本 cron 轮次只处理 `Rank 1~37` 中 `1` 条已 `park` rank。
- 7 天去重：`Rank 32` 上次 bot6 park-reframe 复盘是 `2026-04-04 07:06 UTC`，已超过 `7` 天。
- 选定：`Rank 32 / EMA structure vs MA slope direction gate`

## 1) 原 rank 为什么 park？（保留原审计结论）
来自 `research/optimization_loop/2026-03-17_1123_rank32-clean-replication-park.md` 的原始 clean replication：
- `ema_cross_only @ 6bps/side`：`mean_total_return≈-18.73%`，`positive_asset_ratio=1/3`，`mean_trades≈257.3`
- `ema_cross_plus_slope_floor @ 6bps/side`：`mean_total_return≈+50.76%`，`positive_asset_ratio=3/3`，`mean_trades≈75.7`
- `ema_cross_plus_slope_reclaim @ 6bps/side`：`mean_total_return≈+24.79%`，`positive_asset_ratio=3/3`，但 `mean_trades≈25.0`、`mean_no_trade_ratio≈99.78%`

原 `Rank 32` 被 park，不是因为 slope 主题完全没信息，而是因为：
1. 真正有信息量的部分更像 `aligned slope floor`；
2. 原主表达把它包进了更严的 `spread-mid reclaim`；
3. 一旦按 queue-facing 候选要求看可交易厚度，交易密度还是太稀，原 rank 作为独立 long continuation 命题不够诚实。

所以原 `park` verdict 仍必须保留：它记录的是“这个写法的职责层和样本密度不够”，不是“EMA slope 完全无用”。

## 2) 它更像 hard park 还是 soft park？
**更像 `soft park`，但现在已经比 4 月 4 日那轮更接近 `hard park`。**

原因：
- soft 的部分仍在：原线确实留下过清楚的 `slope floor` pocket；
- 更接近 hard 的部分在于：这条 pocket 的唯一自然 rescue 早已被 `Rank 32b` 完整抽走，而 `2026-04-09` 的 runtime first verdict 又把 `Rank 32b` 明确收口为 `background / P0 / already consumed`。

也就是说：
- 对原 `Rank 32` 历史本体，仍可读作 `soft park`；
- 但对“现在还值不值得继续从旧 Rank 32 再切新轴”这个问题，答案已经明显更偏 `hard no`。

## 3) 有没有“可救信号”？
**有，但只有一条，而且这条可救信号已经被消费并吸收。**

那条可救信号一直都是：
- `EMA cross + aligned slope floor` 有信息；
- `spread-mid reclaim` 更像漂亮但过严的附加句。

这也是为什么当初会派生出 `Rank 32b`：
- `remove spread-mid reclaim requirement; keep EMA cross + aligned slope floor`

而 `research/optimization_loop/2026-04-09_1532_rank32b_fresh_intake_background_already_consumed.md` 已把这件事写死：
1. 这条修改轴不是新的 fresh intake；
2. 它早已完成 clean replication -> P2 -> P3 的历史链条；
3. 当前最诚实的 runtime truth 只能是 `background / P0`，因为它作为旧 rank 的唯一自然 rescue，已经被既有 `Rank 32b` 消费完。

所以当前“可救信号”并不支持新派生；它只支持一句更收敛的话：**Rank 32 的唯一残余已经在 32b 上被消费完。**

## 4) 最近新证据怎么影响判断？
本轮新增旁证没有给 `Rank 32c` 提供新的诚实单轴，反而继续把 EMA 主题上移到更完整的 trend-shell 宿主。

最直接的是 `research/quant_digests/2026-04-08_0405_htf-ema-rsi-pullback-trend-shell.md`：
- 新证据的主语已经不是“EMA slope gate 还差一刀”；
- 而是更完整的 `HTF EMA gate × 15m RSI pullback continuation` raw alpha。

这意味着：
- 若 EMA / trend 主题还值得追，更自然的去向是新的完整 trend-shell / pullback-continuation family；
- 不是回到旧 `Rank 32` 再诚实拆一条 `32c`。

## 5) 最值得改的唯一一刀是什么？
如果今天只问原 rank 最值得改的唯一一刀，答案仍然只有：

**删掉 `spread-mid reclaim`，只保留 `EMA cross + aligned slope floor`。**

但这条唯一主修改轴已经存在，名字就是 `Rank 32b`；而且它又已被 runtime 明确收口为 `background / P0 / already consumed`。

因此本轮不能再把 RSI pullback、HTF gate、ATR exit、VWAP/OBV、asset ranking 之类第二轴硬塞回 `Rank 32c`：
- 那要么只是 `32b` 的实现细化；
- 要么已经滑向新的完整 trend-shell intake；
- 都不再是属于旧 Rank 32 的第二条诚实单轴。

## 6) 是否值得形成新的 derived hypothesis？
结论：**不值得。**

- 本轮最终输出：`keep_park`
- 原 `park` verdict：保持不变
- 不新增 `Rank 32c`

理由：
1. 原 rank 的唯一自然 rescue 已由 `Rank 32b` 消费；
2. `Rank 32b` 又已在 `2026-04-09` 被 first verdict 收口为 `background / P0 / already consumed`；
3. 新近相关证据继续把 EMA 主题推向新的完整 trend-shell / pullback raw-alpha 宿主，而不是回头再诚实派生旧 Rank 32。

## 7) trade on / trade off
### trade on
- 保留原 `park` 的审计意义；
- 承认 Rank 32 本体不是彻底 hard fail，而是曾留下过一条很窄的 residual；
- 承认那条 residual 已被 `Rank 32b` 提炼并消费完。

### trade off
- 不为了“EMA 主题仍有信息”就硬造 `Rank 32c`；
- 不把 `HTF EMA gate × RSI pullback continuation` 这种更完整的新宿主误写成旧 Rank 32 的窄派生；
- 不把更多执行层 / 风控层细节倒灌回旧 park 命题。

## 8) 给 bot2 / 后续 reviewer 的一句话结论
- 原 `park` 保留；
- `Rank 32` 仍读作 `soft park，但已比 4 月 4 日那轮更接近 hard`；
- 原线唯一诚实修改轴已被既有 `Rank 32b` 消费，而 `Rank 32b` 又在 2026-04-09 first verdict 中收口为 `background / P0 / already consumed`，因此当前不再诚实派生 `Rank 32c`。

## 9) 本轮文件与提交
- 本轮更新：
  - `research/park_reframe/INDEX.md`
  - `docs/PARK_REFRAME_QUEUE.md`
  - 新增本日志
- commit：未做。当前 git 工作区可能存在无关脏文件，本轮只做最小必要写入，避免混提。
