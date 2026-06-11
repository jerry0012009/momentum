# 2026-04-13 14:51 UTC · Rank 40 park reframe

## Selected rank
- `Rank 40`
- selection note: 按 `50~79 -> 80~110 -> 1~24 -> 25~49` 的低频轮转，这轮回到 `25~49` 段；`Rank 40` 上次 bot6 单独复盘是 `2026-04-03 13:31 UTC`，已超过 7 天。最近又新增了 `2026-04-08` 与 `2026-04-13` 两条更完整的 EMA / pullback 趋势壳旁证，足够再判断一次：这些新证据是在救旧 `Rank 40`，还是继续把它的主题残余外流到新的 raw-alpha 宿主。

## Original park reason
原始 authoritative 证据：
- `research/optimization_loop/2026-03-18_0314_rank40-clean-replication-park.md`
- `research/park_reframe/2026-04-03_1331_rank40-park-reframe.md`

原 `Rank 40` 被 park 的核心原因没有变化：它把 **three-EMA trend continuation + pullback swing stop + 2.06R target** 写成了 queue-facing 的 standalone continuation alpha，但最小 clean replication 并没有把这条 direct-entry 线救活。

冻结 clean-room 结果（`BTC/ETH/SOL 120d 15m`, `next-bar open`, `no-overlap`, `6bps/side`）：
- 主变体 `33/165/365`：`mean_total_return ≈ -13.32%`
- `positive_asset_ratio = 0/3`
- `mean_trades ≈ 59.0`
- `mean_no_trade_ratio ≈ 83.79%`
- 时间桶：`bucket_1 ≈ -11.47%`, `bucket_2 ≈ +6.64%`, `bucket_3 ≈ -8.00%`
- 邻近参数也没有形成可继续推的诚实主体：
  - `20/100/200 @ 6bps ≈ -0.19%`, `positive_asset_ratio = 1/3`
  - `40/200/440 @ 6bps ≈ -8.51%`, `positive_asset_ratio = 1/3`

翻成人话：
- 失败对象一直都是 **“让三 EMA 回踩自己承担 standalone 触发器角色”**；
- 不是 simple parameter miss；
- 也不是 pullback / trend-continuation 主题整体死亡。

## Hard park or soft park?
- 本轮判断：`soft park，但比 2026-04-03 那轮更接近 hard`

为什么仍不是 pure hard park：
1. 邻近参数至少说明 “顺势回踩” 大主题本身并非完全无信息；
2. 最近新增证据继续证明 **HTF trend gate + LTF pullback continuation** 在更完整的策略壳里依然可能成立；
3. 因此原 rank 的失败更像角色错位，而不是主题彻底作废。

为什么这次又更接近 hard：
1. 最近新增的强证据已经越来越明确地把主语写成 **完整 trend shell / raw alpha**，而不是旧 `three-EMA pullback direct entry`；
2. 旧 rank 剩下的 residual value 更像共享 `trend context / pullback quality / momentum confirm` 语义；
3. 若继续挂在 `Rank 40` 名下派生，很容易模糊原 park 的审计边界。

## Any salvage signal?
有，但仍然更像“主题外流”，不是“旧 rank 还能诚实窄救”。

本轮最 relevant 的新旁证：
- `research/quant_digests/2026-04-08_0405_htf-ema-rsi-pullback-trend-shell.md`
- `research/quant_digests/2026-04-13_0558_wilder-rsi-adx-atr-shell-transfer-check.md`

这些旁证共同在说：
1. **EMA / pullback / continuation 没死**；
2. 但更诚实的写法是 **HTF gate + LTF pullback filter + execution/risk shell** 的完整 raw alpha；
3. EMA 在里面扮演的是 `regime gate / context / confirm / exit shell`，不是旧 Rank 40 那种“直接让三 EMA 回踩自己下单”的主触发器。

可救信号的具体样子：
- `1h/4h EMA200` 充当趋势许可层；
- `15m RSI pullback / EMA9>EMA21 / ADX / volume` 充当 continuation 恢复质量过滤；
- `ATR trail / exhaustion exit` 负责风控与持仓管理。

但这救活的是 **新的 HTF-gated pullback trend shell**，不是旧 `Rank 40` 本体。

## Single best cut
如果只保留唯一一刀，本轮最值得改写的一刀依然是：

> **demote direct three-EMA pullback entry into a shared trend-context / pullback-quality layer**

也就是：
- 不再让 `three-EMA reclaim` 自己直接触发开仓；
- 把 EMA 降级为 `HTF context / local trend integrity / exit shell`；
- 真正的 entry 交给更完整的 pullback continuation raw-alpha 宿主。

但这刀这次比 4 月 3 日那轮更不诚实地属于 `Rank 40`，因为：
1. 它已经不再是 “three-EMA pullback alpha” 的窄修补，而是角色重写；
2. 新证据的最小可交易对象是完整 trend shell，不是 shared confirmation skeleton 再挂旧 rank 名号；
3. 若硬写 `Rank 40b`，更像在借新壳给旧 rank 续命。

## Derived hypothesis?
- 结论：`keep_park`
- 不新增 `derived hypothesis`

为什么这轮仍不值得 draft `Rank 40b`：
1. 原 `park` verdict 没被推翻；
2. 最近新增旁证虽然更强，但它们支持的是 **新的 HTF-gated pullback continuation raw-alpha 宿主**；
3. 旧 `Rank 40` 的唯一自然残余已经薄到只剩 shared context 语义，不足以再单独立号；
4. 若 bot2 以后要认领，更诚实的做法应是把这些旁证当 fresh intake / shell intake，而不是把它们追回 `Rank 40` 名下。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `soft park，但比 4 月 3 日那轮更接近 hard；4 月 8 日与 4 月 13 日新增的 HTF EMA gate × LTF pullback / Wilder-RSI trend-shell 证据继续说明 EMA-pullback 主题仍有信息，但它救活的是新的完整 trend-continuation raw-alpha 宿主，而不是旧 Rank 40 的 three-EMA direct-entry 写法，因此当前不诚实 draft Rank 40b`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## Commit
- 本轮默认不做 commit。
- 原因：只做最小必要文档改动；且仓库长期存在共享脏文件风险，避免混提。
