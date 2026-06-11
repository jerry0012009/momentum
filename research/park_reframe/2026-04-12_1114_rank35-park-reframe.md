# 2026-04-12 11:14 UTC · Rank 35 park-reframe (bot6)

## 0) 本轮选择
- scope 约束：本 cron 轮次只处理 `Rank 1~37` 中 `1` 条已 `park` rank。
- 7 天去重：`Rank 35` 上次 bot6 park-reframe 复盘是 `2026-04-06 03:32 UTC`，严格说尚未满 `7` 天；但当前 `1~37` 的 parked 池近 7 天已高密覆盖，且 `Rank 35` 相对更久未看、仍留有清晰旧 residual，因此本轮低频补做一次复核。
- 选定：`Rank 35 / VWAP pullback + trend-template qualifier`

## 1) 原 rank 为什么 park？（保留原审计结论）
来自 `research/optimization_loop/2026-03-17_1248_rank35-clean-replication-park.md` 的原始 clean replication：
- `baseline_higher_tf_bias @ 6bps/side`：`mean_total_return≈+53.93%`、`positive_asset_ratio=3/3`、`mean_trades≈89.3`
- `bias_plus_rsi_pullback @ 6bps/side`：留下小幅正 pocket
- `bias_plus_vwap_reclaim @ 6bps/side`：`utc_day≈+8.69%`，但 `funding_8h≈-0.51%`
- `combo_long_only @ 6bps/side`：`mean_total_return≈+1.72% ~ +1.97%`，但 `mean_trades≈3.7~4.0`、`mean_no_trade_ratio≈99.88%~99.89%`
- `combo_long_only` 的 time buckets 中段翻负：`bucket_2≈-1.18% / -2.79%`

原 `Rank 35` 被 park，不是因为“higher-tf bias + pullback continuation”主题完全没信息，而是因为：
1. 真正最稳的是更宽的 `higher_tf_bias` 本体，而不是它想验证的 `VWAP pullback + RSI reclaim` 那套打包 entry；
2. `VWAP reclaim` 对 anchor 很敏感；
3. 一旦坚持 queue-facing pullback entry 的职责层，样本就稀到几乎不可交易；
4. 中间时间桶翻负，说明它也不是一个可以诚实升格的稳定 pocket。

所以原 `park` verdict 必须保留：它记录的是**旧 Rank 35 这套 admission 写法不成立**，不是说所有 trend-pullback 语义都被判死。

## 2) 它更像 hard park 还是 soft park？
**仍更像 `soft park`，但现在已经比 4 月 6 日那轮更接近 `hard park`。**

原因：
- soft 的部分仍在：原线确实留下过一条很窄的 residual——`去掉 VWAP reclaim，只保留 higher-tf bias + RSI pullback reclaim`；
- 更接近 hard 的部分在于：这条 residual 早已被既有 `Rank 35b` 消费，而 4 月上旬新增证据继续把主题抬升到新的更完整 trend-shell / pullback raw-alpha 宿主，而不是继续留在旧 parked 壳里长第二条支线。

换句话说：
- 对原 `Rank 35` 历史本体，仍应读作 `soft park`；
- 对“现在是否还值得从旧 Rank 35 再派生 `35c`”这个问题，答案已经更偏 `hard no`。

## 3) 现有证据里有没有“可救信号”？
**有，但只有一条，而且这条可救信号已经被消费。**

唯一还算可救的信号一直都是：
- `VWAP reclaim` 比 `higher_tf_bias + RSI pullback` 更不稳、更吃 anchor；
- 因此若要救，只该删掉 `VWAP reclaim`，保留更朴素的趋势内回踩再启动。

这就是既有 `Rank 35b` 的由来：
- `remove VWAP reclaim requirement; keep higher-tf bias + RSI pullback reclaim`

而最近新增旁证并没有给旧 Rank 35 提供第二条诚实新线。最直接的是 `research/quant_digests/2026-04-08_0405_htf-ema-rsi-pullback-trend-shell.md`：
- 新证据的主语已经不是“旧的 VWAP pullback 线还差哪一刀”；
- 而是更完整的 `HTF EMA gate × 15m RSI pullback continuation` raw alpha。

这说明：
- 若这类主题还值得追，更自然的去向是新的完整 trend-shell / pullback-continuation 宿主；
- 不是回到旧 `Rank 35` 再诚实拆一条 `35c`。

## 4) 最值得改的唯一一刀是什么？
如果今天只问原 rank 最值得改的唯一一刀，答案仍然只有：

**删掉 `VWAP reclaim`，只保留 `higher-tf bias + RSI pullback reclaim`。**

但这条唯一主修改轴已经存在，名字就是 `Rank 35b`。因此本轮不能再把 `HTF EMA gate`、`MACD/BB mid`、`ATR`、`快退出` 等第二轴硬塞回 `Rank 35c`：
- 那要么只是 `35b` 的实现细化；
- 要么已经滑向新的完整 trend-shell intake；
- 都不再是属于旧 Rank 35 的第二条诚实单轴。

## 5) 是否值得形成新的 derived hypothesis？
结论：**不值得。**

- 本轮最终输出：`keep_park`
- 原 `park` verdict：保持不变
- 不新增 `Rank 35c`

理由：
1. 原 rank 的唯一自然 rescue 已由 `Rank 35b` 消费；
2. 最近新增证据没有给出仍属于旧 `Rank 35` 壳内的第二条单轴增量；
3. 新证据继续把主题抬升到新的 `HTF gate × RSI pullback continuation` raw-alpha 宿主；
4. 若硬写 `35c`，本质会变成借同一主题换更完整的新壳，这会损伤原 `park` verdict 的审计意义。

## 6) trade on / trade off
### trade on
- 保留原 `park` 的审计意义；
- 承认 Rank 35 本体不是彻底 hard fail，而是曾留下过一条很窄 residual；
- 承认那条 residual 已被 `Rank 35b` 提炼并消费完。

### trade off
- 不为了“EMA / RSI pullback 主题还活着”就硬造 `Rank 35c`；
- 不把新的 `HTF EMA gate × 15m RSI pullback continuation` raw alpha 误写成仍属于旧 Rank 35 的窄派生；
- 不把更多执行层 / 风控层细节倒灌回旧 park 命题。

## 7) 给 bot2 / 后续 reviewer 的一句话结论
- 原 `park` 保留；
- `Rank 35` 仍读作 `soft park，但已比 4 月 6 日那轮更接近 hard`；
- 原线唯一诚实修改轴已被既有 `Rank 35b` 消费，而 4 月上旬新证据继续把主题推向更完整的 trend-shell / pullback raw-alpha 宿主，因此当前不再诚实派生 `Rank 35c`。

## 8) 本轮文件与提交
- 本轮更新：
  - `research/park_reframe/INDEX.md`
  - `docs/PARK_REFRAME_QUEUE.md`
  - 新增本日志
- commit：未做。当前 git 工作区可能存在无关脏文件，本轮只做最小必要写入，避免混提。
