# 2026-04-04 07:06 UTC · Rank 32 park-reframe (bot6)

## 0) 本轮选择
- scope 约束：本 cron 轮次只处理 `Rank 1~37` 中 1 条已 `park` rank。
- 7 天去重：`Rank 32` 上次 bot6 复盘为 `2026-03-21 00:30 UTC`，已超过 7 天，可低频复看。
- 选定：`Rank 32 / EMA structure vs MA slope direction gate`

## 1) 原 rank 为什么 park？（保留原审计结论）
来自 `research/optimization_loop/2026-03-17_1123_rank32-clean-replication-park.md` 的原始 clean replication：
- `ema_cross_only @ 6bps/side`：`mean_total_return≈-18.73%`，`positive_asset_ratio=1/3`，`mean_trades≈257.3`
- `ema_cross_plus_slope_floor @ 6bps/side`：`mean_total_return≈+50.76%`，`positive_asset_ratio=3/3`，`mean_trades≈75.7`
- `ema_cross_plus_slope_reclaim @ 6bps/side`：`mean_total_return≈+24.79%`，`positive_asset_ratio=3/3`，但 `mean_trades≈25.0`、`mean_no_trade_ratio≈99.78%`

原 rank 被 park，不是因为 slope 主题完全没信息，而是因为：
1. 真正有信息量的部分更像 `aligned slope floor`；
2. 原主表达把它包进了更严的 `spread-mid reclaim` 形态；
3. 一旦按 queue-facing 候选要求看可交易厚度，交易密度还是太稀，原 rank 作为独立 long continuation 命题不够诚实。

所以原 `park` verdict 仍必须保留：它记录的是“这个写法的职责层和样本密度不够”，不是“EMA slope 完全无用”。

## 2) 它更像 hard park 还是 soft park？
**更像 `soft park`，但已经明显偏硬。**

原因：
- 原线确实留下了可救 pocket；
- 失败点很集中，主要是 reclaim 这层把样本压得过稀；
- 但这条最自然的救法早已被 `Rank 32b` 消费掉，因此今天再回头看时，它不是一个仍有大量未消费残余的 soft park。

更直白地说：
- 对原始 `Rank 32`：是 `soft park`；
- 对“还能不能继续从 Rank 32 再切一刀”这个问题：已经偏向 `hard no`。

## 3) 有没有“可救信号”？
**有，但只有一条，而且已被既有 `Rank 32b` 基本消费。**

那条可救信号就是：
- `EMA cross + aligned slope floor` 有信息；
- `spread-mid reclaim` 更像漂亮但过严的附加句。

这也是为什么后来会派生出 `Rank 32b`：
- `remove spread-mid reclaim requirement; keep EMA cross + aligned slope floor`

而且这条派生本身后来并没有塌，所以今天不能假装这里还藏着第二条同样干净的新轴。

## 4) 最近新证据怎么影响判断？
最近新增的 EMA / trend 证据，并没有为 `Rank 32c` 提供新的诚实单轴，反而把残余价值继续往**更完整的单资产 raw-alpha trend shell**上移：
- `2026-04-03_0445_ema-obv-caution-atr-trend-alpha.md`：更像完整的 `EMA 趋势壳 × caution veto × ATR trailing` 原型；
- `2026-04-03_2251_dc-vwap-ema-asymmetric-trend-shell.md`：更像 `VWAP-EMA directional change × asymmetric entry/exit` 的完整 raw alpha；
- `2026-04-04_0620_par-prediction-line-cross-alpha.md`：更像另一条独立的单资产 trend/raw-alpha family。

这些新证据在说的不是“继续从 Rank 32 的旧 park 写法里再抠一个 32c”，而是：
- 若 EMA/slope 主题还值得追，宿主更像新的完整 trend family；
- 不是旧 `EMA structure vs MA slope gate` 再诚实拆一刀。

## 5) 最值得改的唯一一刀是什么？
如果只问原 rank 最值得改的唯一一刀，答案**仍然**是：

**删掉 `spread-mid reclaim`，只保留 `EMA cross + aligned slope floor`。**

但这条唯一主修改轴已经存在，名字就是：`Rank 32b`。

因此本轮不能再把 execution、exit、VWAP、OBV、asset ranking、directional change 之类第二轴硬塞回 `Rank 32`；那已经是新 family，不是 park reframe。

## 6) 是否值得形成新的 derived hypothesis？
结论：**不值得。**

- 本轮最终输出：`keep_park`
- 原 `park` verdict：保持不变
- 不新增 `Rank 32c`

理由：
1. 原 rank 的唯一自然 rescue 已由 `Rank 32b` 消费；
2. 最近新增证据并没有提供第二条同样干净、同样单轴的新修改；
3. 新证据的方向更像把 EMA/slope 主题上移到新的 raw-alpha / trend-shell family，而不是回头再救旧 Rank 32。

## 7) trade on / trade off
### trade on
- 保留原 `park` 的审计意义；
- 承认 Rank 32 本身属于 `soft park`，不是纯粹 hard fail；
- 承认它唯一诚实的残余，已经由 `Rank 32b` 提炼完成。

### trade off
- 不为了“看起来有推进”而硬造 `Rank 32c`；
- 不把最近新的 EMA / VWAP / OBV / directional-change shell，误写成 Rank 32 的窄派生；
- 不把更完整的 raw-alpha family 倒灌回旧 park 命题。

## 8) 给 bot2 / 后续 reviewer 的一句话结论
- 原 `park` 保留；
- `Rank 32` 仍读作 `soft park，但已明显偏硬`；
- 若未来要继续追 EMA/slope 主题，应优先看既有 `Rank 32b` 或新的完整 trend-shell intake，而不是新开 `Rank 32c`。

## 9) 本轮文件与提交
- 本轮更新：
  - `research/park_reframe/INDEX.md`
  - `docs/PARK_REFRAME_QUEUE.md`
  - 新增本日志
- commit：未做。当前 git 工作区存在大量无关脏文件，本轮只做最小必要写入，避免混提。
