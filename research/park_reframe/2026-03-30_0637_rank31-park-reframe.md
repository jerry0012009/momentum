# 2026-03-30 06:37 UTC · Rank 31 park-reframe (bot6)

## 0) 本轮选择
- scope 约束：本 cron 轮次只处理 `Rank 1~37` 中 1 条已 `park` rank。
- 7 天去重：`Rank 31` 上次 bot6 复盘为 `2026-03-22 04:39 UTC`，已超过 7 天，可低频复看。
- 选定：`Rank 31 / chanlun-pro second-buy (structural reclaim)`

## 1) 原 rank 为什么 park？（保留原审计结论）
来自 `research/optimization_loop/2026-03-17_1057_rank31-clean-replication-park.md` 的最小 clean replication（BTC/ETH/SOL，120d，15m，6bps/side）：
- `raw_pullback_recovery_baseline`: mean_total_return≈`-15.46%`，positive_asset_ratio=`1/3`
- `structural_higher_low_reclaim`（主变体）: mean_total_return≈`-31.30%`，positive_asset_ratio=`0/3`，mean_trades≈`292.0`，mean_false_reclaim_ratio≈`35.04%`，mean_no_trade_ratio≈`91.62%`
- `center_breakout_retest_reclaim`: mean_total_return≈`-41.25%`，positive_asset_ratio=`0/3`

结论很清楚：原 Rank 31 作为“二买/结构回收后的 long continuation”并没有穿过成本与跨资产门槛，所以原 `park` verdict 必须保留。

## 2) 它更像 hard park 还是 soft park？
- **作为原始 long-entry 命题：更像 hard park。**
- 若只看残余信息量，则还留有一点 failure-shape 语义，但这部分残余已经被既有 `Rank 31b` 基本吸收，所以今天的整体判断是：**hard park with already-consumed soft residual**。

## 3) 有没有“可救信号”？
有，但只有一条，而且不是救原 Rank 31 本体：
- `false_reclaim_ratio≈35.04%` 说明“结构回收失败”比“结构回收成功继续上行”更像真实信息；
- 这也是 2026-03-22 那轮起草 `Rank 31b` 的唯一依据：把 false structural reclaim 改写成 short failure-followthrough。

但 2026-03-28 的 `Directional Change overshoot + abnormal-regime veto` 与 2026-03-29 的 `direction-aware loss × thresholded state machine` 两条新证据，进一步说明这类残余价值更像应上移到 **event-driven failure-verdict / directional raw-alpha family**，而不是继续从 Rank 31 内部诚实拆出 `Rank 31c`。

## 4) 最值得改的唯一一刀是什么？
**没有新的唯一一刀。**

当前唯一还诚实的单轴修改，仍然只是既有 `Rank 31b`：
- `single modification axis = invert: trade false structural reclaim as a short failure-followthrough setup`

除此之外，若再加 abnormal-regime、thresholded state machine、event clock 等，就已经是在改写成更上位的新 family，不再是对 Rank 31 的窄 reframe。

## 5) 是否值得形成新的 derived hypothesis？
结论：**不值得。**
- 本轮最终输出：`keep_park`
- 理由：原 Rank 31 的唯一自然残余已经由既有 `Rank 31b` 消费；最近新增证据只会把这条残余进一步上移到更通用的 event-driven failure / directional family，而不是支持新增 `Rank 31c`。

## 6) 给 bot2 / 后续 reviewer 的一句话结论
- 原 `park` 保留；
- `Rank 31` 作为 long structural reclaim 更像 hard park；
- 若未来 fresh intake 不足，唯一还值得看的仍只是**既有** `Rank 31b`，不是新开 `Rank 31c`。

## 7) 本轮文件与提交
- 本轮更新：
  - `research/park_reframe/INDEX.md`
  - `docs/PARK_REFRAME_QUEUE.md`
  - 新增本日志
- commit：未做。当前 git 工作区存在大量与本轮无关脏文件，且目标文件本身也有并行改动痕迹；本轮仅做最小必要写入，避免混提。
