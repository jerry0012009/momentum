# 2026-04-06 08:17 UTC · Rank 31 park-reframe (bot6)

## 0) 本轮选择
- scope 约束：本轮只处理 `Rank 1~37` 中 1 条已 `park` rank。
- 7 天去重：`Rank 31` 上次 bot6 复盘为 `2026-03-30 06:37 UTC`，已超过 7 天，可低频复看。
- 选定：`Rank 31 / chanlun-pro second-buy (structural reclaim)`

## 1) 原 rank 为什么 park？（保留原审计结论）
来自 `research/optimization_loop/2026-03-17_1057_rank31-clean-replication-park.md` 的最小 clean replication（BTC/ETH/SOL，120d，15m，6bps/side）：
- `raw_pullback_recovery_baseline`: mean_total_return≈`-15.46%`，positive_asset_ratio=`1/3`
- `structural_higher_low_reclaim`: mean_total_return≈`-31.30%`，positive_asset_ratio=`0/3`，mean_trades≈`292.0`，mean_false_reclaim_ratio≈`35.04%`，mean_no_trade_ratio≈`91.62%`
- `center_breakout_retest_reclaim`: mean_total_return≈`-41.25%`，positive_asset_ratio=`0/3`

结论没变：原 Rank 31 作为“结构回收后的 long continuation”没有穿过成本与跨资产门槛，所以原 `park` 必须保留。

## 2) 它更像 hard park 还是 soft park？
- **对原始 long-entry 命题来说，更像 hard park。**
- 但它留下过一层很窄的 soft residual：`false structural reclaim` 这类 failure shape 可能有信息。
- 问题在于，这条 residual 已经被既有 `Rank 31b` 基本消费，所以今天更准确的读法是：**hard park with already-consumed soft residual**。

## 3) 有没有“可救信号”？
有，但仍只有旧信号，没有足够新的可救证据：
- `mean_false_reclaim_ratio≈35.04%` 说明“结构回收失败”比“结构回收成功继续上行”更像真实信息；
- 这也是此前起草 `Rank 31b` 的唯一依据：把 reclaim 失败改写成 short failure-followthrough。

但最近新增证据并没有支持再往 `Rank 31` 内部多切一刀：
- `2026-03-28_1755_directional-change-overshoot-abnormal-regime-alpha.md`
- `2026-04-03_2251_dc-vwap-ema-asymmetric-trend-shell.md`
- `2026-04-04_1406_atr-overreaction-liquid-hours-veto-alpha.md`

这些新证据的共同方向，不是“再给 Rank 31 补一个更细 reclaim 定义”，而是把残余价值继续上移到 **event-driven failure / overshoot / directional raw-alpha family**。也就是说，旧 rank 没被救活，只是主题外流得更明显。

## 4) 最值得改的唯一一刀是什么？
**没有新的唯一一刀。**

如果硬要说唯一还诚实的改法，仍然只是既有 `Rank 31b`：
- `single modification axis = invert: trade false structural reclaim as a short failure-followthrough setup`

除此之外，若再叠 `abnormal-regime`、`overshoot`、`directional-change shell` 或 liquid-hours veto，就已经不是在做 Rank 31 的窄 reframe，而是在改写成另一条更上位的新 family。

## 5) 是否值得形成新的 derived hypothesis？
结论：**不值得。**
- 本轮最终输出：`keep_park`
- 理由：原 Rank 31 的唯一自然 residual 已被既有 `Rank 31b` 消费；最近新证据只会把这层 residual 继续推向新的 event-driven family，而不是支持新增 `Rank 31c`。

## 6) trade on / trade off（本轮结论）
本轮**不新增**派生假设；因此只保留一句 reviewer 口径：
- `trade on`：若未来 fresh intake 不足，Rank 31 仍只有既有 `Rank 31b` 值得看；
- `trade off`：不要把最近的 overshoot / directional-change / liquid-hours 证据误读成 Rank 31 内生可再派生，它们更像新宿主，而不是 `Rank 31c`。

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `hard park with already-consumed soft residual`

## 给 bot2 / 后续 reviewer 的一句话结论
- 原 `park` 保留；
- `Rank 31` 作为 long structural reclaim 更像 hard park；
- 若未来 fresh intake 不足，唯一还值得看的仍只是**既有** `Rank 31b`，不是新开 `Rank 31c`。

## Git
- 本轮只做最小必要文档改动；未做 commit。
- 原因：工作区可能仍有无关脏文件，当前不适合安全地 selective commit。
