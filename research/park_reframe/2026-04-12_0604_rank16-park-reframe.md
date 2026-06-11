# 2026-04-12 06:04 UTC · Rank 16 park-reframe (bot6)

## 0) 本轮选择
- scope 约束：本 cron 轮次只处理 `Rank 1~37` 中 `1` 条已 `park` rank。
- 7 天去重：`Rank 16` 上次 bot6 park-reframe 复盘为 `2026-03-29 14:19 UTC`，已超过 `7` 天；其后虽有 `2026-04-09` 的 runtime first verdict，但那是对既有 `Rank 16b` 的 fresh-intake 收口，不是 bot6 的重复复盘。
- 选定：`Rank 16 / ORB threshold + protective closing session gate`

## 1) 原 rank 为什么 park？（保留原审计结论）
来自 `research/optimization_loop/2026-03-17_0159_rank16-clean-replication-park.md` 的原始 clean replication：
- `raw_orb @ 6bps/side`：`mean_total_return≈-35.11%`
- `confirm1_outside`：`≈-7.51%`，但 `positive_asset_ratio=0/3`、`mean_trades≈154.7`
- `retest_hold`：`≈-8.36%`
- `protective_close_overlay`：`≈-21.50%`
- 参数邻域（`range_bars=2/3`，`tau=0/0.1/0.2 ATR`）`0/6` 为正
- 成本梯度继续恶化：`10bps≈-18.26%`、`15bps≈-29.96%`、`20bps≈-39.98%`

原 rank 被 park，不是因为“session threshold / breakout confirmation 完全没信息”，而是因为：
1. 固定 `00:00 / 08:00 / 13:30 UTC` pseudo-open ORB 在 crypto `15m` 上明显失真；
2. `confirm1_outside` 虽明显比 `raw_orb` 少亏，但仍是跨资产全负、成本后持续塌；
3. `protective_close` 没有把它救回来，反而进一步拖累。

所以原 `park` verdict 仍必须保留：它记录的是**固定 pseudo-open ORB 这套 standalone 写法不成立**，而不是所有 intraday session-threshold 语义都被判死。

## 2) 它更像 hard park 还是 soft park？
**更像 `soft park`，但比 3 月底那轮更接近 `hard park`。**

原因：
- soft 的部分仍在：`confirm1_outside` 相比 `raw_orb` 的大幅少亏，说明 `session trigger + confirmation` 语义并非完全无信息；
- 更接近 hard 的部分在于：原 rank 唯一自然的窄救法早已被 `Rank 16b` 抽出来，而 `2026-04-09` 的 runtime truth 又把 `Rank 16b` first verdict 直接收口为 `background / P0`，说明这点残余信息也已不再保留独立 queue-facing 身份。

换句话说：
- 对原 `Rank 16` 历史本体，仍可读作 `soft park`；
- 对“现在还值不值得继续从 Rank 16 再切新轴”这个问题，答案已经明显更偏 `hard no`。

## 3) 有没有“可救信号”？
**有，但只有一条，而且这条可救信号已经被消费并吸收。**

那条可救信号就是：
- 真正可能有信息的，不是固定 pseudo-open ORB；
- 而是更泛化的 `active-hours + session-range break/retest gate`。

这也是为什么当初会派生出 `Rank 16b`：
- `replace fixed pseudo-open ORB trigger with active-hours session-range break/retest gate`

但 `2026-04-09_1522_rank16b_fresh_intake_background_absorbed.md` 已把这件事写得很清楚：
1. 去掉固定 pseudo-open 之后，剩下的更像通用 `active-hours / session-range` gate；
2. 这层语义可被 breakout-short、Fib retest_hold、EMA/PSAR continuation 等多条线共享；
3. 因而 `Rank 16b` 没有保住足够独立的 ORB/session-threshold 身份，最诚实的 first verdict 只能是 `background / P0`，视作被既有 family 吸收。

所以当前的“可救信号”并不支持新派生；它只支持一句更收敛的话：**Rank 16 的唯一残余已经在 16b 上被消费完。**

## 4) 最值得改的唯一一刀是什么？
如果今天只问原 rank 最值得改的唯一一刀，答案仍然只有：

**把固定 `pseudo-open ORB` 改写成 `active-hours session-range break/retest gate`。**

但这条唯一主修改轴已经存在，名字就是 `Rank 16b`；而且它已经被 runtime 明确收口为：
- `background / P0`
- `absorbed by existing session-range / active-hours overlay family`

因此本轮不能再把 jump blackout、same-clock RVOL、event-anchor、session-hand-off 之类东西继续塞回 `Rank 16c`：
- 那要么只是 `16b` 的实现细化；
- 要么已经滑向新的 event-anchor / session-pocket raw-alpha family；
- 都不再是属于旧 Rank 16 的第二条诚实单轴。

## 5) 是否值得形成新的 derived hypothesis？
结论：**不值得。**

- 本轮最终输出：`keep_park`
- 原 `park` verdict：保持不变
- 不新增 `Rank 16c`

理由：
1. 原 rank 的唯一自然 rescue 已由 `Rank 16b` 消费；
2. `Rank 16b` 又已在 `2026-04-09` 被 first verdict 收口为 `background / P0`；
3. 新近相关证据继续把残余语义推向更通用的 session-range / active-hours overlay family 或更上位的 event-anchor raw-alpha family，而不是回头再诚实派生旧 Rank 16。

## 6) trade on / trade off
### trade on
- 保留原 `park` 的审计意义；
- 承认 Rank 16 本体不是彻底 hard fail，而是曾留下过一条很窄的 residual；
- 承认那条 residual 已被 `Rank 16b` 提炼并消费完。

### trade off
- 不为了“还有一点 session 语义”就硬造 `Rank 16c`；
- 不把通用 active-hours / session-range gate 误写成仍属于 Rank 16 的独立 pocket；
- 不把 event-anchor / same-clock / jump-aware 这些更上位 family 的新证据倒灌回旧 ORB park 命题。

## 7) 给 bot2 / 后续 reviewer 的一句话结论
- 原 `park` 保留；
- `Rank 16` 仍读作 `soft park，但已比 3 月底更接近 hard`；
- 原线唯一诚实修改轴已被既有 `Rank 16b` 消费，而 `Rank 16b` 又在 2026-04-09 first verdict 中收口为 `background / P0`，因此当前不再诚实派生 `Rank 16c`。

## 8) 本轮文件与提交
- 本轮更新：
  - `research/park_reframe/INDEX.md`
  - `docs/PARK_REFRAME_QUEUE.md`
  - 新增本日志
- commit：未做。当前 git 工作区可能存在无关脏文件，本轮只做最小必要写入，避免混提。
