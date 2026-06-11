# 2026-04-25 20:40 UTC · Rank 18 park reframe revisit

## Selected rank
- `Rank 18`
- selection note:
  - 按当前低频轮转，`50+` 与 `80~110` 号段本周已连续覆盖；本轮切回 `1~24`
  - `Rank 18` 上次 bot6 复盘为 `2026-04-18 21:30 UTC`，已刚好超过 `7` 天窗口
  - 它属于典型的 `trend-readiness / abstain` 旧壳，且 4 月 21 日与 4 月 23 日又新增了更近的 trend-shell / pullback 旁证，值得做一次低频收口判断

## Read set
- `docs/BOT6_PARK_REFRAME_BRIEF.md`
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- source / prior rank evidence:
  - `research/optimization_loop/2026-03-17_0309_rank18-clean-replication-park.md`
  - `research/optimization_loop/2026-04-09_1537_rank18b_fresh_intake_background_shared_overlay.md`
  - `research/park_reframe/2026-04-18_2130_rank18-park-reframe.md`
- new side evidence:
  - `research/quant_digests/2026-04-21_1358_tripleema-rsi-atr-stack-alpha.md`
  - `research/quant_digests/2026-04-23_0548_stochrsi-macd-pullback-continuation-alpha.md`

## 1) 原 rank 为什么 park？
原 `Rank 18 / EMA plateau-consensus entry` 被 park 的 blocker 没变：
- 它把 `EMA 邻域平台共识` 写成了 standalone entry / standalone alpha；
- 但 clean replication 已经把这条路审计得很清楚：`plateau_vote_5of9_spread_guard @ 6bps/side ≈ -19.89%`，`positive_asset_ratio=0/3`；
- 成本梯度继续恶化（约 `-29.36% / -39.63% / -48.42%`）；
- 它不是“差一点成功”，而是 **作为直接开仓职责，本体失败**。

因此原 `park` 的审计意义必须保留：
> 失败的是“EMA plateau-consensus 自己负责 entry”这层职责，不是所有 trend-readiness / abstain 信息都不存在。

## 2) 它更像 hard park 还是 soft park？
**本轮仍判为 `soft park`，但已更接近 `hard park with consumed residual`。**

原因：
1. 它仍保留一点 residual value：相较更粗的版本，plateau-consensus 至少表达了“有些段更该不做”的 abstain/readiness 语义；
2. 但这条 residual 早已被唯一诚实的一刀收敛为既有 `Rank 18b`；
3. `Rank 18b` 又已在 `2026-04-09` 的 fresh intake 首判里收口为 `background / P0`；
4. 最近新增证据继续把主题往更完整的 trend shell / pullback shell 上移，而不是把 old `Rank 18` 再拉回 queue-facing 独立对象。

## 3) 有没有“可救信号”？
**有主题层面的可救信号，但没有 old `Rank 18` 壳内的新可救信号。**

最近两条旁证都在强化同一件事：

### A. `triple EMA stack × RSI veto × ATR bracket`
`2026-04-21_1358_tripleema-rsi-atr-stack-alpha.md` 更清楚地说明：
- `EMA stack` 更像完整 trend raw-alpha 的主壳；
- `RSI veto` 只是在趋势壳内避免末端追涨/追跌；
- 也就是说，readiness/filter 语义更自然地服务一个明确的 trend shell，而不是自己独立当入场主语。

### B. `StochRSI 极值回摆 × RSI 方向约束 × MACD 相位翻转`
`2026-04-23_0548_stochrsi-macd-pullback-continuation-alpha.md` 进一步说明：
- 市场里仍然存在“趋势没坏，只是局部回摆结束”的 continuation pocket；
- 但它的宿主是更完整的 `pullback-continuation raw alpha`；
- 不是 old `Rank 18` 这种 generic plateau-consensus gate。

合起来，本轮更像在说：
> trend-readiness 信息还活，但它活在 **新的完整 trend / pullback raw-alpha 宿主** 里；不是在救 old `Rank 18` 本体。

## 4) 最值得改的唯一一刀是什么？
**唯一最值得改的一刀仍然只有既有 `Rank 18b`：**

> `demote standalone EMA plateau-consensus entry into a shared abstain / trend-readiness veto gate`

也就是：
- 不再让 `Rank 18` 自己负责开仓；
- 只在别的 base setup 已触发时，用 plateau-consensus 做 `allow / veto / abstain`；
- 第一刀只测 `baseline vs abstain-only gate`，不偷带新的 trend shell、pullback shell、exit、regime 或 universe 第二轴。

但这刀已经被写过，也已被 fresh intake 首判消费。若今天继续往前写，只会落入两种情况：
1. 只是换句话重讲 `18b`；或
2. 偷带 `triple EMA / StochRSI / MACD / ATR` 等新壳信息，变成一个新的宿主，而不再是 old `Rank 18` 的窄 reframe。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。本轮继续 `keep_park`。**

理由：
1. 原 `park` verdict 没被推翻；
2. old `Rank 18` 唯一诚实 residual 仍只到既有 `Rank 18b`；
3. `Rank 18b` 已于 `2026-04-09` 收口为 `background / P0`；
4. 4 月 21~23 的新证据强化的是“新的 trend shell / pullback shell 宿主”，而不是 old `Rank 18` 的新单轴。

## 单轮审查模板回答
### 原 rank 为什么 park？
因为 `EMA plateau-consensus` 作为 standalone entry 在 clean replication 中跨资产、跨成本都明显不过线，失败不是轻微偏差，而是职责错位。

### 它更像 hard park 还是 soft park？
`soft park`，但已更接近 `hard park with consumed residual`。

### 有没有“可救信号”？
有，但主要是 trend-readiness 作为完整 trend / pullback raw-alpha 宿主内的 filter/readiness 语义；可救的是主题，不是旧 `Rank 18` 壳。

### 最值得改的唯一一刀是什么？
把 standalone plateau-consensus 降级成 shared abstain / trend-readiness veto gate，也就是既有 `Rank 18b` 那一刀。

### 是否值得形成新的 derived hypothesis？
不值得；本轮继续 `keep_park`。

## Final verdict
- `keep_park`
- original verdict kept: `park`
- short note: `soft park，但已更接近 hard park with consumed residual；4 月 21~23 的 triple-EMA / StochRSI pullback continuation 新证据继续说明，trend-readiness 主题若还有价值，更像新的完整 trend-shell / pullback raw-alpha 宿主，而不是足以把 old Rank 18 再诚实派生成 Rank 18c；旧线唯一自然 residual 仍只到既有 Rank 18b。`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`
- 未改：`docs/TODO.md`

## Commit
- 本轮不做 commit。
- 原因：git 工作区存在大量与本轮无关的共享脏文件 / 未跟踪文件；本轮只做最小必要文档改动，避免混提。

## 邮件短标题
- `Rank 18 继续 park，readiness 残余仍只到 18b`
